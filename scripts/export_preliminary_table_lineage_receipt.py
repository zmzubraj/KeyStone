#!/usr/bin/env python3
"""Emit or verify a non-scientific lineage receipt for preliminary paper tables."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TABLE_EXPORTER = Path("scripts/export_paper_tables.py")
MARKDOWN_OUTPUT = Path("paper/tables/preliminary_results.md")
LATEX_OUTPUT = Path("paper/tables/preliminary_results.tex")
RECEIPT = Path("paper/tables/lineage/preliminary-table-lineage-receipt.json")
SIDECAR = Path("paper/tables/lineage/preliminary-table-lineage-receipt.json.sha256")

CLASSIFICATION = {
    "evidence_stage": "PRELIMINARY",
    "authorization_boundary": "PREAUTHORIZATION_ONLY",
    "scientific_evidence_status": "NOT_SCIENTIFIC_EVIDENCE",
    "independence_status": "SAME_WORKSPACE_NOT_INDEPENDENT",
    "canonical_table_status": "NOT_CANONICAL_T_SERIES",
}


@dataclass(frozen=True)
class InputSpec:
    input_id: str
    path: Path
    format: str
    expected_rows: int
    selected_fields: tuple[str, ...]
    identity_fields: tuple[str, ...]
    markdown_section: str
    latex_label: str


INPUT_SPECS = (
    InputSpec(
        "MONTE_CARLO_BASELINE",
        Path("prototype/results/baseline.json"),
        "JSON_ARRAY",
        4,
        (
            "name",
            "trials",
            "reconstruction_success_rate",
            "reconstruction_success_ci_low",
            "reconstruction_success_ci_high",
            "audit_pass_rate",
            "audit_pass_ci_low",
            "audit_pass_ci_high",
            "catastrophic_trials",
            "catastrophic_detection_rate",
            "catastrophic_detection_ci_low",
            "catastrophic_detection_ci_high",
        ),
        ("name",),
        "Monte Carlo outcomes",
        "tab:preliminary-monte-carlo",
    ),
    InputSpec(
        "EXACT_STRATIFIED_VALIDATION",
        Path("prototype/results/exact_stratified_validation.csv"),
        "CSV",
        1,
        (
            "design",
            "required_successes",
            "exact_tail_probability",
            "monte_carlo_tail_probability",
            "absolute_error",
            "trials",
            "seed",
        ),
        ("design",),
        "Exact fixed-quota stratified validation",
        "tab:exact-stratified-validation",
    ),
    InputSpec(
        "SOLIDITY_GAS",
        Path("contracts/gas_report.csv"),
        "CSV",
        8,
        ("operation", "gas", "measurement_scope"),
        ("operation",),
        "Solidity operation gas",
        "tab:preliminary-gas",
    ),
    InputSpec(
        "TEMPORAL_DEPENDENCE",
        Path("prototype/results/markov_temporal_dependence.csv"),
        "CSV",
        4,
        (
            "audits",
            "final_catastrophic_trials",
            "all_audits_pass_and_final_catastrophic_count",
            "conditional_sequence_false_accept_rate",
            "conditional_sequence_false_accept_ci_low",
            "conditional_sequence_false_accept_ci_high",
            "static_set_repeated_bound",
        ),
        ("audits",),
        "Exploratory temporal-dependence boundary",
        "tab:temporal-boundary",
    ),
    InputSpec(
        "CRYPTO_MICROBENCHMARK",
        Path("prototype/results/crypto_benchmark.csv"),
        "CSV",
        3,
        (
            "n",
            "threshold",
            "keygen_median_ms",
            "seal_median_ms",
            "partial_proof_median_ms",
            "partial_verify_median_ms",
            "open_median_ms",
            "signature_sign_median_ms",
            "signature_verify_median_ms",
            "signature_size_bytes",
        ),
        ("n", "threshold"),
        "Local cryptographic and signature microbenchmark",
        "tab:preliminary-crypto-benchmark",
    ),
)

ARTIFACT_PATHS = tuple(spec.path for spec in INPUT_SPECS) + (
    TABLE_EXPORTER,
    MARKDOWN_OUTPUT,
    LATEX_OUTPUT,
)
TABLE_CHECK_SEMANTIC_ARGV = (
    "<PYTHON_EXECUTABLE>",
    TABLE_EXPORTER.as_posix(),
    "--check",
)


class LineageError(RuntimeError):
    """Raised when preliminary table lineage is incomplete or has drifted."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise LineageError(message)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_relative_paths(root: Path, paths: tuple[Path, ...]) -> list[dict[str, str]]:
    _require(len(paths) == len(set(paths)), "duplicate artifact path")
    rows: list[dict[str, str]] = []
    for relative in paths:
        path = root / relative
        _require(path.is_file(), f"missing lineage artifact: {relative.as_posix()}")
        rows.append({"path": relative.as_posix(), "sha256": _sha256(path)})
    return rows


def require_no_artifact_drift(
    before: list[dict[str, str]], after: list[dict[str, str]]
) -> None:
    before_map = {row["path"]: row["sha256"] for row in before}
    after_map = {row["path"]: row["sha256"] for row in after}
    _require(len(before_map) == len(before), "duplicate artifact in pre-check snapshot")
    _require(len(after_map) == len(after), "duplicate artifact in post-check snapshot")
    if before_map != after_map:
        changed = sorted(
            path
            for path in before_map.keys() | after_map.keys()
            if before_map.get(path) != after_map.get(path)
        )
        raise LineageError(f"artifact drift detected during table check: {changed}")


def _load_input_rows(root: Path, spec: InputSpec) -> list[dict[str, Any]]:
    path = root / spec.path
    _require(path.is_file(), f"missing lineage source: {spec.path.as_posix()}")
    try:
        if spec.format == "JSON_ARRAY":
            loaded = json.loads(path.read_text(encoding="utf-8"))
            _require(isinstance(loaded, list), f"{spec.input_id}: expected JSON array")
            rows = loaded
        elif spec.format == "CSV":
            with path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
        else:
            raise LineageError(f"{spec.input_id}: unsupported input format")
    except (UnicodeDecodeError, json.JSONDecodeError, csv.Error) as exc:
        raise LineageError(f"{spec.input_id}: invalid input: {exc}") from exc
    _require(len(rows) == spec.expected_rows, f"{spec.input_id}: input row count mismatch")
    for index, row in enumerate(rows):
        _require(isinstance(row, dict), f"{spec.input_id}[{index}]: row is not an object")
        missing = [field for field in spec.selected_fields if field not in row]
        _require(not missing, f"{spec.input_id}[{index}]: selected fields missing: {missing}")
    return rows


def _validate_output_classification(markdown: str, latex: str) -> None:
    _require(
        "> Evidence label: internal preliminary simulation/contract evidence." in markdown
        and "not confirmatory or independently verified" in markdown,
        "Markdown preliminary/non-independent classification mismatch",
    )
    _require(
        "% Evidence label: internal preliminary; rerun after study-design freeze." in latex,
        "LaTeX preliminary classification mismatch",
    )


def collect_workspace_snapshot(root: Path = ROOT) -> dict[str, Any]:
    markdown_path = root / MARKDOWN_OUTPUT
    latex_path = root / LATEX_OUTPUT
    _require(markdown_path.is_file(), "missing preliminary Markdown output")
    _require(latex_path.is_file(), "missing preliminary LaTeX output")
    markdown = markdown_path.read_text(encoding="utf-8")
    latex = latex_path.read_text(encoding="utf-8")
    _validate_output_classification(markdown, latex)

    inputs: list[dict[str, Any]] = []
    for spec in INPUT_SPECS:
        rows = _load_input_rows(root, spec)
        _require(
            f"## {spec.markdown_section}" in markdown,
            f"{spec.input_id}: mapped Markdown section missing",
        )
        _require(
            f"\\label{{{spec.latex_label}}}" in latex,
            f"{spec.input_id}: mapped LaTeX section missing",
        )
        identities = [
            {field: row[field] for field in spec.identity_fields}
            for row in rows
        ]
        _require(
            len({json.dumps(item, sort_keys=True) for item in identities}) == len(identities),
            f"{spec.input_id}: duplicate row identity",
        )
        inputs.append(
            {
                "input_id": spec.input_id,
                "path": spec.path.as_posix(),
                "sha256": _sha256(root / spec.path),
                "format": spec.format,
                "row_count": len(rows),
                "selected_fields": list(spec.selected_fields),
                "row_identities": identities,
                "section_mapping": {
                    "markdown_heading": spec.markdown_section,
                    "latex_label": spec.latex_label,
                },
            }
        )

    return {
        "classification": dict(CLASSIFICATION),
        "source_exporter": {
            "path": TABLE_EXPORTER.as_posix(),
            "sha256": _sha256(root / TABLE_EXPORTER),
        },
        "inputs": inputs,
        "outputs": [
            {
                "format": "MARKDOWN",
                "path": MARKDOWN_OUTPUT.as_posix(),
                "sha256": _sha256(markdown_path),
            },
            {
                "format": "LATEX",
                "path": LATEX_OUTPUT.as_posix(),
                "sha256": _sha256(latex_path),
            },
        ],
    }


def table_check_argv(python_executable: str) -> tuple[list[str], list[str]]:
    _require(bool(python_executable), "blank Python executable for table check")
    return list(TABLE_CHECK_SEMANTIC_ARGV), [
        python_executable,
        TABLE_EXPORTER.as_posix(),
        "--check",
    ]


def validate_table_check_argv_record(record: Any) -> None:
    _require(isinstance(record, dict), "stored table-check record missing")
    _require(
        record.get("command_argv") == list(TABLE_CHECK_SEMANTIC_ARGV),
        "stored table-check semantic argv mismatch",
    )
    executed = record.get("executed_argv")
    _require(
        isinstance(executed, list)
        and len(executed) == 3
        and isinstance(executed[0], str)
        and bool(executed[0])
        and executed[1:] == [TABLE_EXPORTER.as_posix(), "--check"],
        "stored table-check executed argv malformed",
    )


def _run_table_check(
    root: Path,
) -> tuple[list[str], list[str], subprocess.CompletedProcess[str]]:
    semantic_argv, executed_argv = table_check_argv(sys.executable)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        executed_argv,
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    _require(result.returncode == 0, f"paper table exporter --check failed: {result.returncode}")
    _require(
        "PASS: paper tables match canonical result sources" in result.stdout,
        "paper table exporter --check success marker missing",
    )
    return semantic_argv, executed_argv, result


def _checked_snapshot(
    root: Path,
) -> tuple[
    dict[str, Any],
    list[dict[str, str]],
    list[str],
    list[str],
    subprocess.CompletedProcess[str],
]:
    before = hash_relative_paths(root, ARTIFACT_PATHS)
    semantic_argv, executed_argv, result = _run_table_check(root)
    after = hash_relative_paths(root, ARTIFACT_PATHS)
    require_no_artifact_drift(before, after)
    return collect_workspace_snapshot(root), before, semantic_argv, executed_argv, result


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _publish_receipt(root: Path, receipt: dict[str, Any]) -> str:
    receipt_path = root / RECEIPT
    sidecar_path = root / SIDECAR
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    try:
        _atomic_write(receipt_path, rendered)
        receipt_hash = _sha256(receipt_path)
        _atomic_write(sidecar_path, f"{receipt_hash}  {receipt_path.name}\n")
    except OSError:
        receipt_path.unlink(missing_ok=True)
        sidecar_path.unlink(missing_ok=True)
        raise
    return receipt_hash


def _verified_existing_receipt(root: Path) -> tuple[dict[str, Any], str]:
    receipt_path = root / RECEIPT
    sidecar_path = root / SIDECAR
    _require(receipt_path.is_file(), "lineage receipt missing")
    _require(sidecar_path.is_file(), "lineage receipt sidecar missing")
    lines = [line.strip() for line in sidecar_path.read_text().splitlines() if line.strip()]
    _require(len(lines) == 1, "lineage sidecar must contain exactly one entry")
    match = re.fullmatch(r"([0-9a-f]{64})\s{2}([^/]+)", lines[0])
    _require(match is not None, "malformed lineage sidecar")
    expected_hash, expected_name = match.groups()
    _require(expected_name == receipt_path.name, "lineage sidecar filename mismatch")
    actual_hash = _sha256(receipt_path)
    _require(actual_hash == expected_hash, "lineage receipt SHA-256 mismatch")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LineageError(f"invalid lineage receipt JSON: {exc}") from exc
    _require(isinstance(receipt, dict), "lineage receipt root must be an object")
    return receipt, actual_hash


def _runtime() -> dict[str, str]:
    return {
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "platform_machine": platform.machine(),
        "working_directory": ROOT.as_posix(),
    }


def _remove_stale_outputs(root: Path) -> None:
    for relative in (RECEIPT, SIDECAR):
        (root / relative).unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the existing receipt and lineage")
    args = parser.parse_args(argv)
    started_at = _utc_now()
    try:
        if args.check:
            existing, receipt_hash = _verified_existing_receipt(ROOT)
            snapshot, artifact_hashes, semantic_argv, executed_argv, check_result = _checked_snapshot(ROOT)
            _require(existing.get("receipt_type") == "PRELIMINARY_TABLE_LINEAGE_RECEIPT", "receipt type mismatch")
            _require(existing.get("overall_status") == "PASS", "receipt overall status is not PASS")
            for key, value in CLASSIFICATION.items():
                _require(existing.get(key) == value, f"receipt classification mismatch: {key}")
            _require(existing.get("lineage") == snapshot, "stored lineage snapshot is stale")
            _require(
                existing.get("artifact_hashes_before_check") == artifact_hashes
                and existing.get("artifact_hashes_after_check") == artifact_hashes,
                "stored pre/post artifact hashes are stale",
            )
            table_check = existing.get("table_check")
            validate_table_check_argv_record(table_check)
            _require(
                table_check.get("command_argv") == semantic_argv,
                "stored table-check semantic argv mismatch",
            )
            _require(
                existing.get("runtime", {}).get("python_executable")
                == table_check.get("executed_argv", [None])[0],
                "stored generation runtime/executed argv mismatch",
            )
            print(f"PASS: verified {RECEIPT.as_posix()}")
            print(f"SHA256: {receipt_hash}")
            return 0

        _remove_stale_outputs(ROOT)
        snapshot, artifact_hashes, semantic_argv, executed_argv, check_result = _checked_snapshot(ROOT)
        completed_at = _utc_now()
        receipt: dict[str, Any] = {
            "schema_version": 1,
            "receipt_type": "PRELIMINARY_TABLE_LINEAGE_RECEIPT",
            **CLASSIFICATION,
            "overall_status": "PASS",
            "started_at_utc": started_at,
            "completed_at_utc": completed_at,
            "runtime": _runtime(),
            "invocation_argv": [sys.executable, Path(__file__).resolve().relative_to(ROOT).as_posix()],
            "table_check": {
                "command_argv": semantic_argv,
                "executed_argv": executed_argv,
                "returncode": check_result.returncode,
                "stdout": check_result.stdout.strip(),
                "stderr": check_result.stderr.strip(),
            },
            "artifact_hashes_before_check": artifact_hashes,
            "artifact_hashes_after_check": artifact_hashes,
            "lineage": snapshot,
            "receipt_hash_location": SIDECAR.as_posix(),
            "limitations": [
                "This receipt records same-workspace lineage for preliminary outputs only.",
                "It is not scientific evidence, independent reproduction, confirmatory analysis, or canonical T-series evidence.",
                "A passing exporter check establishes deterministic source-to-table consistency, not scientific validity.",
            ],
        }
        receipt_hash = _publish_receipt(ROOT, receipt)
        print(f"PASS: wrote {RECEIPT.as_posix()}")
        print(f"SHA256: {receipt_hash}")
        return 0
    except (LineageError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
