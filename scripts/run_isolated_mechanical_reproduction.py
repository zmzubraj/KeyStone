#!/usr/bin/env python3
"""Run a bounded KEYSTONE isolated mechanical reproduction."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_OUTPUT_DIR_RELATIVE = "prototype/results/engineering_qa/isolated_reproduction"
SHA256SUMS_PATH = "SHA256SUMS"
PACKAGE_MANIFEST_PATH = "PACKAGE_MANIFEST.md"
PROGRAM_STATE_PATH = "research-case/program-state.json"
SOURCE_MANIFEST_PATH = "research-case/07-manuscript/source-manifest.json"

RECEIPT_CONSTANTS = {
    "schema_id": "KEYSTONE_ISOLATED_MECHANICAL_REPRODUCTION_RECEIPT",
    "schema_version": 1,
    "system": "KEYSTONE-MPP-F1",
    "canonical_phase": "INTAKE",
    "novelty_status": "UNRESOLVED",
    "feasibility_decision": "UNASSESSED",
    "solution_viability": "ASSERTED_ONLY",
    "acceptance_readiness": "NOT_ASSESSABLE",
    "executor_class": "SECOND_AGENT_SAME_HOST_ISOLATED_COPY",
    "scientific_evidence_status": "NOT_INDEPENDENT_SCIENTIFIC_VERIFICATION",
    "external_sharing": "NOT_PERFORMED",
    "network_isolation": "TOOL_FLAGS_ONLY_NOT_KERNEL_ENFORCED",
}

COMMAND_ENV_OVERRIDES = {
    "UV_OFFLINE": "1",
    "CARGO_NET_OFFLINE": "true",
    "FOUNDRY_OFFLINE": "true",
    "NO_COLOR": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTEST_ADDOPTS": "-p no:cacheprovider",
}

ALLOWED_PARENT_ENV_KEYS = frozenset(
    {
        "PATH",
        "HOME",
        "TMPDIR",
        "TEMP",
        "TMP",
        "LANG",
        "LC_ALL",
        "TERM",
        "USER",
        "LOGNAME",
        "SYSTEMROOT",
        "COMSPEC",
        "PATHEXT",
    }
)

FORBIDDEN_PATH_PARTS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".cache",
        "cache",
        "out",
        "broadcast",
    }
)
FORBIDDEN_FILENAMES = frozenset({".DS_Store", "Thumbs.db", "runtime.lock"})
ALLOWED_PATH_BASES = {
    "workspace_root": "",
    "research_case_root": "research-case",
}
RESIDUAL_LIMITATIONS = (
    "same host and potentially shared host-level caches",
    "no external operator identity binding",
    "tool offline flags are not kernel-enforced network isolation",
    "no scientific independence or independent scientific verification",
    "no distributed deadline execution",
    "no venue or institutional approval",
)


class OperationalError(RuntimeError):
    """Raised when receipt execution or validation cannot proceed safely."""


@dataclass(frozen=True, slots=True)
class InventoryEntry:
    relative_path: str
    sha256: str


@dataclass(frozen=True, slots=True)
class CommandSpec:
    command_id: str
    cwd: str
    argv: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CommandObservation:
    command_id: str
    cwd: str
    argv: tuple[str, ...]
    returncode: int
    stdout_path: str
    stderr_path: str
    stdout_sha256: str
    stderr_sha256: str
    argv_sha256: str
    cwd_sha256: str


@dataclass(frozen=True, slots=True)
class InventoryState:
    digest: str | None
    error: str | None
    rows: tuple[dict[str, str], ...] | None


COMMAND_SPECS = (
    CommandSpec(
        command_id="deadline_package_check",
        cwd=".",
        argv=("python3", "scripts/export_deadline_pilot_start_package.py", "--check"),
    ),
    CommandSpec(
        command_id="t1_t8_check",
        cwd=".",
        argv=("python3", "scripts/export_t1_t8_tables.py", "--check"),
    ),
    CommandSpec(
        command_id="paper_tables_check",
        cwd=".",
        argv=("python3", "scripts/export_paper_tables.py", "--check"),
    ),
    CommandSpec(
        command_id="python_suite",
        cwd="prototype",
        argv=(
            "uv",
            "run",
            "--offline",
            "--locked",
            "--extra",
            "dev",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
        ),
    ),
    CommandSpec(
        command_id="foundry_test",
        cwd=".",
        argv=("forge", "test", "--root", "contracts", "--offline"),
    ),
    CommandSpec(
        command_id="gas_snapshot_check",
        cwd=".",
        argv=(
            "forge",
            "snapshot",
            "--root",
            "contracts",
            "--offline",
            "--match-test",
            "^testGas_",
            "--check",
            ".gas-snapshot",
        ),
    ),
    CommandSpec(
        command_id="gas_report_check",
        cwd=".",
        argv=(
            "python3",
            "contracts/scripts/export_gas_snapshot.py",
            "--check",
            ".gas-snapshot",
            "contracts/gas_report.csv",
        ),
    ),
    CommandSpec(
        command_id="test_vectors_check",
        cwd="prototype",
        argv=(
            "uv",
            "run",
            "--offline",
            "--locked",
            "--extra",
            "dev",
            "python",
            "scripts/export_test_vectors.py",
            "--check",
        ),
    ),
    CommandSpec(
        command_id="signature_vectors_check",
        cwd="prototype",
        argv=(
            "uv",
            "run",
            "--offline",
            "--locked",
            "--extra",
            "dev",
            "python",
            "scripts/export_signature_vectors.py",
            "--check",
        ),
    ),
    CommandSpec(
        command_id="strict_research_case",
        cwd=".",
        argv=(
            "python3",
            "/Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/check_research_case.py",
            "research-case",
            "--strict",
        ),
    ),
)


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def stable_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def sha256_text(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_within_root(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise OperationalError(
            f"path traversal outside project root: {relative_path}"
        ) from exc
    return candidate


def is_forbidden_copy_path(relative_path: str) -> bool:
    path = Path(relative_path)
    if any(part in FORBIDDEN_PATH_PARTS for part in path.parts):
        return True
    if path.name in FORBIDDEN_FILENAMES:
        return True
    return path.parts[:2] == ("research-case", ".runtime")


def parse_sha256_inventory(project_root: Path) -> tuple[InventoryEntry, ...]:
    sha_path = project_root / SHA256SUMS_PATH
    if not sha_path.is_file():
        raise OperationalError(f"missing SHA256SUMS: {sha_path}")

    entries: list[InventoryEntry] = []
    seen_paths: set[str] = set()
    for line_number, raw_line in enumerate(
        sha_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not raw_line:
            raise OperationalError(f"invalid SHA256SUMS line {line_number}: empty line")
        if len(raw_line) < 68 or raw_line[64:68] != "  ./":
            raise OperationalError(f"invalid SHA256SUMS line {line_number}: {raw_line}")
        digest = raw_line[:64]
        relative_path = raw_line[68:]
        if any(character not in "0123456789abcdef" for character in digest):
            raise OperationalError(f"invalid SHA256SUMS line {line_number}: {raw_line}")
        if not relative_path or relative_path.startswith("/"):
            raise OperationalError(
                f"invalid inventory path on line {line_number}: {relative_path}"
            )
        if relative_path in seen_paths:
            raise OperationalError(f"duplicate inventory path: {relative_path}")
        if is_forbidden_copy_path(relative_path):
            raise OperationalError(f"forbidden inventory path: {relative_path}")
        candidate = resolve_within_root(project_root, relative_path)
        if not candidate.is_file():
            raise OperationalError(f"missing inventoried file: {relative_path}")
        seen_paths.add(relative_path)
        entries.append(InventoryEntry(relative_path=relative_path, sha256=digest))

    return tuple(entries)


def read_sha256_inventory(project_root: Path) -> tuple[InventoryEntry, ...]:
    entries = parse_sha256_inventory(project_root)
    for entry in entries:
        candidate = resolve_within_root(project_root, entry.relative_path)
        if sha256_file(candidate) != entry.sha256:
            raise OperationalError(f"inventory hash mismatch: {entry.relative_path}")
    return entries


def compute_inventory_state(
    project_root: Path,
    inventory: tuple[InventoryEntry, ...],
    digest_overrides: dict[str, str] | None = None,
) -> tuple[list[dict[str, str]], str]:
    rows: list[dict[str, str]] = []
    overrides = {} if digest_overrides is None else digest_overrides
    for entry in inventory:
        digest = overrides.get(entry.relative_path)
        if digest is None:
            candidate = resolve_within_root(project_root, entry.relative_path)
            if not candidate.is_file():
                raise OperationalError(
                    f"missing inventoried file during verification: {entry.relative_path}"
                )
            digest = sha256_file(candidate)
        rows.append({"path": entry.relative_path, "sha256": digest})
    rendered = stable_json(rows)
    return rows, sha256_text(rendered)


def observe_inventory_state(
    project_root: Path,
    inventory: tuple[InventoryEntry, ...],
) -> InventoryState:
    try:
        rows, digest = compute_inventory_state(project_root, inventory)
    except OperationalError as exc:
        return InventoryState(digest=None, error=str(exc), rows=None)
    return InventoryState(digest=digest, error=None, rows=tuple(rows))


def require_matching_inventory(
    observed: list[dict[str, str]],
    expected: tuple[InventoryEntry, ...],
    label: str,
) -> None:
    expected_rows = [
        {"path": entry.relative_path, "sha256": entry.sha256}
        for entry in expected
    ]
    if observed != expected_rows:
        raise OperationalError(f"{label} inventory mismatch")


def verify_source_manifest(project_root: Path) -> int:
    manifest_path = project_root / SOURCE_MANIFEST_PATH
    if not manifest_path.is_file():
        raise OperationalError(f"missing source manifest: {manifest_path}")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    sources = payload.get("sources")
    if not isinstance(sources, list):
        raise OperationalError("source manifest missing sources list")

    seen_ids: set[str] = set()
    verified = 0
    for row in sources:
        if not isinstance(row, dict):
            raise OperationalError("source manifest contains non-object entry")
        source_id = row.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise OperationalError("source manifest source_id missing")
        if source_id in seen_ids:
            raise OperationalError(f"duplicate source_id: {source_id}")
        seen_ids.add(source_id)

        path = row.get("path")
        path_base = row.get("path_base")
        digest = row.get("sha256")
        if not isinstance(path, str) or not path:
            raise OperationalError(f"source manifest path missing for {source_id}")
        if not isinstance(path_base, str) or path_base not in ALLOWED_PATH_BASES:
            raise OperationalError(
                f"unsupported path_base for {source_id}: {path_base}"
            )
        if not isinstance(digest, str) or len(digest) != 64:
            raise OperationalError(f"invalid source hash for {source_id}")
        if any(character not in "0123456789abcdef" for character in digest):
            raise OperationalError(f"invalid source hash for {source_id}")

        base = project_root / ALLOWED_PATH_BASES[path_base]
        candidate = resolve_within_root(base, path)
        if not candidate.is_file():
            raise OperationalError(
                f"missing source manifest file for {source_id}: {path}"
            )
        if sha256_file(candidate) != digest:
            raise OperationalError(
                f"source manifest hash mismatch for {source_id}: {path}"
            )
        verified += 1

    return verified


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def publish_receipt(
    receipt_path: Path,
    sidecar_path: Path,
    receipt: dict[str, object],
) -> None:
    rendered = stable_json(receipt)
    _atomic_write_text(receipt_path, rendered)
    digest = sha256_file(receipt_path)
    _atomic_write_text(sidecar_path, f"{digest}  {receipt_path.name}\n")


def build_tools_platform() -> dict[str, object]:
    versions: dict[str, str | None] = {
        "python": platform.python_version(),
        "uv": None,
        "forge": None,
    }
    for tool_name in ("uv", "forge"):
        resolved = shutil.which(tool_name)
        if resolved is None:
            continue
        try:
            completed = subprocess.run(
                [resolved, "--version"],
                check=False,
                capture_output=True,
                text=True,
                shell=False,
            )
        except OSError:
            continue
        versions[tool_name] = (
            completed.stdout.strip()
            or completed.stderr.strip()
            or Path(resolved).name
        )

    return {
        "python_executable": Path(sys.executable).name,
        "platform": platform.platform(),
        "versions": versions,
        "command_environment_overrides": COMMAND_ENV_OVERRIDES,
    }


def copy_inventory_to_isolated_root(
    project_root: Path,
    isolated_root: Path,
    inventory: tuple[InventoryEntry, ...],
) -> None:
    for entry in inventory:
        source = resolve_within_root(project_root, entry.relative_path)
        destination = isolated_root / entry.relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    shutil.copy2(project_root / SHA256SUMS_PATH, isolated_root / SHA256SUMS_PATH)


def build_execution_env() -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if key in ALLOWED_PARENT_ENV_KEYS
    }
    env.update(COMMAND_ENV_OVERRIDES)
    return env


def run_command(
    command_spec: CommandSpec,
    isolated_root: Path,
    logs_root: Path,
) -> CommandObservation:
    working_directory = (
        isolated_root
        if command_spec.cwd == "."
        else resolve_within_root(isolated_root, command_spec.cwd)
    )
    if not working_directory.is_dir():
        raise OperationalError(f"missing command cwd: {command_spec.cwd}")
    stdout_path = logs_root / f"{command_spec.command_id}.stdout.txt"
    stderr_path = logs_root / f"{command_spec.command_id}.stderr.txt"
    completed = subprocess.run(
        list(command_spec.argv),
        cwd=working_directory,
        env=build_execution_env(),
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )
    _atomic_write_text(stdout_path, completed.stdout)
    _atomic_write_text(stderr_path, completed.stderr)
    return CommandObservation(
        command_id=command_spec.command_id,
        cwd=command_spec.cwd,
        argv=command_spec.argv,
        returncode=completed.returncode,
        stdout_path=f"commands/{stdout_path.name}",
        stderr_path=f"commands/{stderr_path.name}",
        stdout_sha256=sha256_file(stdout_path),
        stderr_sha256=sha256_file(stderr_path),
        argv_sha256=sha256_text(stable_json(list(command_spec.argv))),
        cwd_sha256=sha256_text(command_spec.cwd),
    )


def validate_output_dir(project_root: Path, output_dir: Path) -> Path:
    if output_dir.exists() and output_dir.is_symlink():
        raise OperationalError(f"output directory may not be a symlink: {output_dir}")
    expected_output = (project_root / CANONICAL_OUTPUT_DIR_RELATIVE).resolve(strict=False)
    resolved_output = output_dir.resolve(strict=False)
    try:
        resolved_output.relative_to(project_root.resolve())
    except ValueError as exc:
        raise OperationalError(f"output directory escapes project root: {output_dir}") from exc
    if resolved_output != expected_output:
        raise OperationalError(
            f"output directory must match canonical path: {project_root / CANONICAL_OUTPUT_DIR_RELATIVE}"
        )
    if output_dir.exists() and not output_dir.is_dir():
        raise OperationalError(f"output path is not a directory: {output_dir}")
    return output_dir


def validate_execute_output_dir(project_root: Path, output_dir: Path) -> Path:
    validate_output_dir(project_root, output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise OperationalError(f"output directory must be empty: {output_dir}")
    return output_dir


def build_failure_reason(
    commands: list[CommandObservation],
    source_post_state: InventoryState,
    isolated_post_state: InventoryState,
    source_tree_unchanged: bool,
    isolated_copy_unchanged: bool,
) -> str | None:
    for observation in commands:
        if observation.returncode != 0:
            return f"command {observation.command_id} returned {observation.returncode}"
    if isolated_post_state.error is not None:
        return (
            "isolated copy inventory verification failed: "
            f"{isolated_post_state.error}"
        )
    if source_post_state.error is not None:
        return f"source inventory verification failed: {source_post_state.error}"
    if not isolated_copy_unchanged:
        return "isolated copy inventory changed during execution"
    if not source_tree_unchanged:
        return "source inventory changed during execution"
    return None


def build_receipt(
    project_root: Path,
    inventory: tuple[InventoryEntry, ...],
    source_manifest_count: int,
    pre_rows: list[dict[str, str]],
    pre_digest: str,
    source_post_state: InventoryState,
    isolated_pre_digest: str,
    isolated_post_state: InventoryState,
    commands: list[CommandObservation],
) -> dict[str, object]:
    tools_platform = build_tools_platform()
    source_tree_unchanged = (
        source_post_state.digest is not None
        and source_post_state.rows is not None
        and pre_rows == list(source_post_state.rows)
    )
    isolated_copy_unchanged = (
        isolated_post_state.digest is not None
        and isolated_pre_digest == isolated_post_state.digest
    )
    all_commands_passed = len(commands) == len(COMMAND_SPECS) and all(
        observation.returncode == 0 for observation in commands
    )
    status = (
        "MECHANICAL_PASS"
        if all_commands_passed and source_tree_unchanged and isolated_copy_unchanged
        else "MECHANICAL_FAIL"
    )
    failure_reason = build_failure_reason(
        commands=commands,
        source_post_state=source_post_state,
        isolated_post_state=isolated_post_state,
        source_tree_unchanged=source_tree_unchanged,
        isolated_copy_unchanged=isolated_copy_unchanged,
    )

    return {
        **RECEIPT_CONSTANTS,
        "status": status,
        "generated_at": utc_now(),
        "inventoried_file_count": len(inventory),
        "sha256sums_sha256": sha256_file(project_root / SHA256SUMS_PATH),
        "package_manifest_sha256": sha256_file(project_root / PACKAGE_MANIFEST_PATH),
        "program_state_sha256": sha256_file(project_root / PROGRAM_STATE_PATH),
        "source_manifest_sha256": sha256_file(project_root / SOURCE_MANIFEST_PATH),
        "pre_execution_source_inventory_sha256": pre_digest,
        "post_execution_source_inventory_sha256": source_post_state.digest,
        "source_inventory_verification_error": source_post_state.error,
        "pre_execution_isolated_copy_inventory_sha256": isolated_pre_digest,
        "post_execution_isolated_copy_inventory_sha256": isolated_post_state.digest,
        "isolated_copy_inventory_verification_error": isolated_post_state.error,
        "source_tree_unchanged": source_tree_unchanged,
        "isolated_copy_unchanged": isolated_copy_unchanged,
        "source_manifest_sources_verified": source_manifest_count,
        "tools_platform": tools_platform,
        "tools_platform_sha256": sha256_text(stable_json(tools_platform)),
        "commands": [asdict(observation) for observation in commands],
        "failure_reason": failure_reason,
        "residual_limitations": list(RESIDUAL_LIMITATIONS),
    }


def execute(project_root: Path, output_dir: Path) -> int:
    inventory = read_sha256_inventory(project_root)
    pre_rows, pre_digest = compute_inventory_state(project_root, inventory)
    require_matching_inventory(pre_rows, inventory, "source")
    source_manifest_count = verify_source_manifest(project_root)

    with tempfile.TemporaryDirectory(prefix="keystone-isolated-copy-") as isolated_dir_name:
        isolated_root = Path(isolated_dir_name)
        copy_inventory_to_isolated_root(project_root, isolated_root, inventory)
        isolated_inventory = read_sha256_inventory(isolated_root)
        isolated_pre_rows, isolated_pre_digest = compute_inventory_state(
            isolated_root,
            isolated_inventory,
        )
        require_matching_inventory(isolated_pre_rows, inventory, "isolated copy")

        with tempfile.TemporaryDirectory(prefix="keystone-isolated-logs-") as logs_dir_name:
            logs_root = Path(logs_dir_name) / "commands"
            logs_root.mkdir(parents=True, exist_ok=True)
            commands: list[CommandObservation] = []
            for command_spec in COMMAND_SPECS:
                observation = run_command(command_spec, isolated_root, logs_root)
                commands.append(observation)
                if observation.returncode != 0:
                    break

            isolated_post_state = observe_inventory_state(isolated_root, isolated_inventory)
            source_post_state = observe_inventory_state(project_root, inventory)
            receipt = build_receipt(
                project_root=project_root,
                inventory=inventory,
                source_manifest_count=source_manifest_count,
                pre_rows=pre_rows,
                pre_digest=pre_digest,
                source_post_state=source_post_state,
                isolated_pre_digest=isolated_pre_digest,
                isolated_post_state=isolated_post_state,
                commands=commands,
            )

            output_dir.mkdir(parents=True, exist_ok=True)
            commands_dir = output_dir / "commands"
            commands_dir.mkdir(parents=True, exist_ok=True)
            for observation in commands:
                for relative in (observation.stdout_path, observation.stderr_path):
                    name = Path(relative).name
                    shutil.copy2(logs_root / name, commands_dir / name)
            publish_receipt(
                output_dir / "receipt.json",
                output_dir / "receipt.json.sha256",
                receipt,
            )
            return 0 if receipt["status"] == "MECHANICAL_PASS" else 1


def read_sidecar_hash(sidecar_path: Path, receipt_name: str) -> str:
    if not sidecar_path.is_file():
        raise OperationalError(f"missing receipt sidecar: {sidecar_path}")
    line = sidecar_path.read_text(encoding="utf-8").strip()
    expected_suffix = f"  {receipt_name}"
    if len(line) != 64 + len(expected_suffix) or not line.endswith(expected_suffix):
        raise OperationalError(f"invalid receipt sidecar format: {sidecar_path}")
    digest = line[:64]
    if any(character not in "0123456789abcdef" for character in digest):
        raise OperationalError(f"invalid receipt sidecar hash: {sidecar_path}")
    return digest


def require_hex_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise OperationalError(f"invalid {label}")
    if any(character not in "0123456789abcdef" for character in value):
        raise OperationalError(f"invalid {label}")
    return value


def require_optional_hex_digest(value: object, label: str) -> str | None:
    if value is None:
        return None
    return require_hex_digest(value, label)


def resolve_receipt_log_path(
    output_dir: Path,
    value: object,
    command_id: str,
    suffix: str,
) -> Path:
    if not isinstance(value, str) or not value:
        raise OperationalError(f"missing {suffix} path for {command_id}")
    if Path(value).is_absolute():
        raise OperationalError(f"{suffix} path must be relative for {command_id}")
    expected = f"commands/{command_id}.{suffix}.txt"
    if value != expected:
        raise OperationalError(f"{suffix} path mismatch for {command_id}")
    candidate = (output_dir / value).resolve(strict=False)
    try:
        candidate.relative_to(output_dir.resolve())
    except ValueError as exc:
        raise OperationalError(
            f"{suffix} path escapes output directory for {command_id}"
        ) from exc
    return candidate


def validate_receipt_constants(receipt: dict[str, object]) -> None:
    for key, expected in RECEIPT_CONSTANTS.items():
        if receipt.get(key) != expected:
            raise OperationalError(f"receipt constant mismatch for {key}")


def require_matching_receipt_digest(
    receipt: dict[str, object],
    field_name: str,
    expected_digest: str,
) -> None:
    if require_hex_digest(receipt.get(field_name), field_name) != expected_digest:
        raise OperationalError(f"{field_name} does not match current project state")


def validate_exact_list(value: object, expected: list[str], label: str) -> None:
    if value != expected:
        raise OperationalError(f"{label} mismatch")


def validate_tools_platform(receipt: dict[str, object]) -> None:
    tools_platform = receipt.get("tools_platform")
    if not isinstance(tools_platform, dict):
        raise OperationalError("tools_platform must be an object")
    if tools_platform.get("command_environment_overrides") != COMMAND_ENV_OVERRIDES:
        raise OperationalError("tools_platform command_environment_overrides mismatch")
    expected_sha = sha256_text(stable_json(tools_platform))
    if (
        require_hex_digest(receipt.get("tools_platform_sha256"), "tools_platform_sha256")
        != expected_sha
    ):
        raise OperationalError("tools_platform_sha256 mismatch")
    validate_exact_list(
        receipt.get("residual_limitations"),
        list(RESIDUAL_LIMITATIONS),
        "residual_limitations",
    )


def derive_inventory_unchanged(
    receipt: dict[str, object],
    pre_field: str,
    post_field: str,
    error_field: str,
    boolean_field: str,
) -> tuple[bool, str | None]:
    pre_digest = require_hex_digest(receipt.get(pre_field), pre_field)
    post_digest = require_optional_hex_digest(receipt.get(post_field), post_field)
    error_value = receipt.get(error_field)
    if error_value is None:
        error_text = None
    elif isinstance(error_value, str) and error_value:
        error_text = error_value
    else:
        raise OperationalError(f"invalid {error_field}")

    if post_digest is None:
        if error_text is None:
            raise OperationalError(f"{post_field} missing without {error_field}")
        unchanged = False
    else:
        if error_text is not None:
            raise OperationalError(f"{error_field} present despite {post_field}")
        unchanged = pre_digest == post_digest

    if receipt.get(boolean_field) != unchanged:
        raise OperationalError(f"{boolean_field} does not match digest evidence")
    return unchanged, error_text


def require_positive_integer(value: object, label: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise OperationalError(f"invalid {label}")
    return value


def check_receipt(project_root: Path, output_dir: Path) -> int:
    receipt_path = output_dir / "receipt.json"
    sidecar_path = output_dir / "receipt.json.sha256"
    if not receipt_path.is_file():
        raise OperationalError(f"missing receipt: {receipt_path}")
    if sha256_file(receipt_path) != read_sidecar_hash(sidecar_path, receipt_path.name):
        raise OperationalError("receipt sidecar hash mismatch")

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if not isinstance(receipt, dict):
        raise OperationalError("receipt root must be a JSON object")
    validate_receipt_constants(receipt)
    validate_tools_platform(receipt)

    require_hex_digest(
        receipt.get("sha256sums_sha256"),
        "sha256sums_sha256",
    )
    require_hex_digest(
        receipt.get("package_manifest_sha256"),
        "package_manifest_sha256",
    )
    require_hex_digest(
        receipt.get("program_state_sha256"),
        "program_state_sha256",
    )
    require_hex_digest(
        receipt.get("source_manifest_sha256"),
        "source_manifest_sha256",
    )
    require_positive_integer(
        receipt.get("inventoried_file_count"),
        "inventoried_file_count",
    )
    require_positive_integer(
        receipt.get("source_manifest_sources_verified"),
        "source_manifest_sources_verified",
    )

    commands = receipt.get("commands")
    if not isinstance(commands, list):
        raise OperationalError("receipt commands must be a list")
    if len(commands) > len(COMMAND_SPECS):
        raise OperationalError("receipt command inventory exceeds allowlist")

    seen_ids: set[str] = set()
    first_nonzero_index: int | None = None
    for index, row in enumerate(commands):
        if not isinstance(row, dict):
            raise OperationalError("receipt command entry must be an object")
        command_id = row.get("command_id")
        if not isinstance(command_id, str) or not command_id:
            raise OperationalError("receipt command_id missing")
        if command_id in seen_ids:
            raise OperationalError(f"duplicate command_id in receipt: {command_id}")
        expected_spec = COMMAND_SPECS[index]
        if command_id != expected_spec.command_id:
            raise OperationalError(f"receipt command order mismatch: {command_id}")
        if row.get("argv") != list(expected_spec.argv):
            raise OperationalError(f"argv mismatch for {command_id}")
        if row.get("cwd") != expected_spec.cwd:
            raise OperationalError(f"cwd mismatch for {command_id}")
        seen_ids.add(command_id)

        stdout_path = resolve_receipt_log_path(
            output_dir,
            row.get("stdout_path"),
            command_id,
            "stdout",
        )
        stderr_path = resolve_receipt_log_path(
            output_dir,
            row.get("stderr_path"),
            command_id,
            "stderr",
        )
        if not stdout_path.is_file() or not stderr_path.is_file():
            raise OperationalError(f"missing command logs for {command_id}")
        if sha256_file(stdout_path) != require_hex_digest(
            row.get("stdout_sha256"),
            f"stdout hash for {command_id}",
        ):
            raise OperationalError(f"stdout hash mismatch for {command_id}")
        if sha256_file(stderr_path) != require_hex_digest(
            row.get("stderr_sha256"),
            f"stderr hash for {command_id}",
        ):
            raise OperationalError(f"stderr hash mismatch for {command_id}")
        if sha256_text(stable_json(list(expected_spec.argv))) != require_hex_digest(
            row.get("argv_sha256"),
            f"argv hash for {command_id}",
        ):
            raise OperationalError(f"argv hash mismatch for {command_id}")
        if sha256_text(expected_spec.cwd) != require_hex_digest(
            row.get("cwd_sha256"),
            f"cwd hash for {command_id}",
        ):
            raise OperationalError(f"cwd hash mismatch for {command_id}")
        returncode = row.get("returncode")
        if not isinstance(returncode, int):
            raise OperationalError(f"invalid returncode for {command_id}")
        if returncode != 0 and first_nonzero_index is None:
            first_nonzero_index = index

    derived_source_tree_unchanged, source_inventory_error = derive_inventory_unchanged(
        receipt,
        "pre_execution_source_inventory_sha256",
        "post_execution_source_inventory_sha256",
        "source_inventory_verification_error",
        "source_tree_unchanged",
    )
    derived_isolated_copy_unchanged, isolated_inventory_error = derive_inventory_unchanged(
        receipt,
        "pre_execution_isolated_copy_inventory_sha256",
        "post_execution_isolated_copy_inventory_sha256",
        "isolated_copy_inventory_verification_error",
        "isolated_copy_unchanged",
    )

    post_source_digest = require_optional_hex_digest(
        receipt.get("post_execution_source_inventory_sha256"),
        "post_execution_source_inventory_sha256",
    )

    status = receipt.get("status")
    failure_reason = receipt.get("failure_reason")
    if failure_reason is not None and not isinstance(failure_reason, str):
        raise OperationalError("failure_reason must be a string or null")

    if status == "MECHANICAL_PASS":
        if len(commands) != len(COMMAND_SPECS):
            raise OperationalError("MECHANICAL_PASS requires the complete command plan")
        if first_nonzero_index is not None:
            raise OperationalError("MECHANICAL_PASS cannot contain a nonzero command")
        if not derived_source_tree_unchanged or not derived_isolated_copy_unchanged:
            raise OperationalError(
                "MECHANICAL_PASS requires unchanged source and isolated inventories"
            )
        if source_inventory_error is not None or isolated_inventory_error is not None:
            raise OperationalError(
                "MECHANICAL_PASS cannot contain inventory verification errors"
            )
        if failure_reason is not None:
            raise OperationalError("MECHANICAL_PASS cannot contain failure_reason")
    elif status == "MECHANICAL_FAIL":
        if first_nonzero_index is not None:
            if len(commands) != first_nonzero_index + 1:
                raise OperationalError(
                    "command-failure receipt must stop at first nonzero command"
                )
            for row in commands[:first_nonzero_index]:
                if row["returncode"] != 0:
                    raise OperationalError(
                        "command-failure receipt has nonzero command before failure"
                    )
            expected_failure_reason = (
                f"command {commands[first_nonzero_index]['command_id']} returned "
                f"{commands[first_nonzero_index]['returncode']}"
            )
        else:
            if len(commands) != len(COMMAND_SPECS):
                raise OperationalError(
                    "inventory-failure receipt must contain the complete command plan"
                )
            expected_failure_reason = build_failure_reason(
                commands=[],
                source_post_state=InventoryState(
                    digest=receipt.get("post_execution_source_inventory_sha256"),
                    error=source_inventory_error,
                    rows=None,
                ),
                isolated_post_state=InventoryState(
                    digest=receipt.get("post_execution_isolated_copy_inventory_sha256"),
                    error=isolated_inventory_error,
                    rows=None,
                ),
                source_tree_unchanged=derived_source_tree_unchanged,
                isolated_copy_unchanged=derived_isolated_copy_unchanged,
            )
            if expected_failure_reason is None:
                raise OperationalError(
                    "MECHANICAL_FAIL lacks command or inventory failure evidence"
                )
        if failure_reason != expected_failure_reason:
            raise OperationalError("failure_reason mismatch for MECHANICAL_FAIL")
    else:
        raise OperationalError("receipt status must be MECHANICAL_PASS or MECHANICAL_FAIL")
    return 0


def dry_run(project_root: Path) -> int:
    inventory = read_sha256_inventory(project_root)
    rows, _ = compute_inventory_state(project_root, inventory)
    require_matching_inventory(rows, inventory, "source")
    verify_source_manifest(project_root)
    for command in COMMAND_SPECS:
        print(command.command_id)
    return 0


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--check-receipt", action="store_true")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--output-dir", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        project_root = args.project_root.resolve()
        if not project_root.is_dir():
            raise OperationalError(f"project root is not a directory: {project_root}")

        if args.check_receipt:
            if args.output_dir is None:
                raise OperationalError(
                    "--output-dir is required for execute and check-receipt"
                )
            return check_receipt(
                project_root,
                validate_output_dir(project_root, args.output_dir),
            )
        if args.execute:
            if args.output_dir is None:
                raise OperationalError(
                    "--output-dir is required for execute and check-receipt"
                )
            return execute(
                project_root,
                validate_execute_output_dir(project_root, args.output_dir),
            )
        return dry_run(project_root)
    except (OperationalError, OSError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
