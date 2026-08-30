from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "export_intake_review_bundle.py"

BUNDLE_PATH = Path("review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip")
SIDECAR_PATH = Path("review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip.sha256")

ALLOWED_ARCHIVE_PATHS = (
    "README.md",
    "bundle-manifest.json",
    "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md",
    "research-case/program-state.json",
    "research-case/00-governance/verifier-registry.json",
    "research-case/00-governance/verification-ledger.jsonl",
    "research-case/00-governance/intake-original.md",
    "research-case/00-governance/intake.json",
    "research-case/00-governance/program-charter.md",
    "research-case/00-governance/study-profile.json",
)

GENERATED_ARCHIVE_PATHS = {
    "README.md",
    "bundle-manifest.json",
}

CANONICAL_REQUIRED_PATHS = (
    "research-case/00-governance/intake-original.md",
    "research-case/00-governance/intake.json",
    "research-case/00-governance/program-charter.md",
    "research-case/00-governance/study-profile.json",
)

COPY_INPUTS = (
    "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md",
    "research-case/program-state.json",
    "research-case/artifact-registry.csv",
    "research-case/00-governance/verifier-registry.json",
    "research-case/00-governance/verification-ledger.jsonl",
    "research-case/00-governance/intake-original.md",
    "research-case/00-governance/intake.json",
    "research-case/00-governance/program-charter.md",
    "research-case/00-governance/study-profile.json",
    "research-case/00-governance/accountable-authority-confirmation.md",
)


def run_cli(project_root: Path, *argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(project_root), *argv],
        text=True,
        capture_output=True,
        check=False,
    )


def copy_inputs(project_root: Path) -> None:
    for rel in COPY_INPUTS:
        src = ROOT / rel
        dst = project_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def bundle_paths(project_root: Path) -> tuple[Path, Path]:
    return project_root / BUNDLE_PATH, project_root / SIDECAR_PATH


def read_archive(project_root: Path) -> dict[str, bytes]:
    archive_path, _ = bundle_paths(project_root)
    with zipfile.ZipFile(archive_path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def latest_required_updated_at(project_root: Path) -> str:
    with (project_root / "research-case/artifact-registry.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    row_by_path = {row["path"]: row for row in rows if row.get("path")}
    return max(
        row_by_path[path.removeprefix("research-case/")]["updated_at"]
        for path in CANONICAL_REQUIRED_PATHS
    )


def canonical_trust_mode(project_root: Path) -> str:
    payload = json.loads(
        (project_root / "research-case/00-governance/verifier-registry.json").read_text(
            encoding="utf-8"
        )
    )
    value = payload.get("trust_mode")
    if not isinstance(value, str) or not value:
        raise RuntimeError("verifier-registry.json lacks trust_mode")
    return value


def mutate_registry_sha(project_root: Path, path: str, sha256: str) -> None:
    csv_path = project_root / "research-case/artifact-registry.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise RuntimeError("artifact-registry.csv has no header")
        rows = [row.copy() for row in reader]
    for row in rows:
        if row.get("path") == path.removeprefix("research-case/"):
            row["sha256"] = sha256
            break
    else:
        raise RuntimeError(f"missing artifact row for {path}")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_generation_writes_exact_allowlist_manifest_and_sidecar(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)

    result = run_cli(project_root)
    assert result.returncode == 0, result.stderr or result.stdout

    archive_path, sidecar_path = bundle_paths(project_root)
    assert archive_path.is_file()
    assert sidecar_path.is_file()

    archive_bytes = archive_path.read_bytes()
    assert sidecar_path.read_text(encoding="utf-8") == (
        f"{hashlib.sha256(archive_bytes).hexdigest()}  ./{BUNDLE_PATH.as_posix()}\n"
    )

    payloads = read_archive(project_root)
    assert tuple(payloads) == ALLOWED_ARCHIVE_PATHS

    manifest = json.loads(payloads["bundle-manifest.json"].decode("utf-8"))
    assert manifest["schema_id"] == "KEYSTONE_INTAKE_REVIEW_BUNDLE"
    assert manifest["schema_version"] == 1
    assert manifest["status"] == "PREPARED_FOR_EXTERNAL_VERIFICATION"
    assert manifest["canonical_phase"] == "INTAKE"
    assert manifest["novelty_status"] == "UNRESOLVED"
    assert manifest["feasibility_decision"] == "UNASSESSED"
    assert manifest["solution_viability_status"] == "ASSERTED_ONLY"
    assert manifest["acceptance_readiness"] == "NOT_ASSESSABLE"
    assert manifest["trust_mode"] == canonical_trust_mode(project_root)
    assert manifest["bundle_timestamp"] == latest_required_updated_at(project_root)

    source_files = manifest["source_files"]
    assert tuple(entry["archive_path"] for entry in source_files) == ALLOWED_ARCHIVE_PATHS
    row_by_path = {
        entry["archive_path"]: entry
        for entry in source_files
    }
    for rel in ALLOWED_ARCHIVE_PATHS:
        entry = row_by_path[rel]
        archive_hash = hashlib.sha256(payloads[rel]).hexdigest()
        if rel in GENERATED_ARCHIVE_PATHS:
            assert entry["source_path"] is None
            if rel == "bundle-manifest.json":
                assert entry["source_sha256"] is None
                assert entry["archive_sha256"] is None
            else:
                assert entry["source_sha256"] == archive_hash
                assert entry["archive_sha256"] == archive_hash
        else:
            assert entry["archive_sha256"] == archive_hash
            expected_hash = sha256_hex(project_root / rel)
            assert entry["source_path"] == rel
            assert entry["source_sha256"] == expected_hash

    readme = payloads["README.md"].decode("utf-8")
    assert "local generation does not authorize external transfer" in readme
    assert "does not create independent scientific verification" in readme
    assert "does not promote the research phase" in readme
    assert "author metadata deferred" in readme.lower()


def test_rerun_is_deterministic_and_check_detects_source_drift(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)

    first = run_cli(project_root)
    assert first.returncode == 0, first.stderr or first.stdout
    archive_path, sidecar_path = bundle_paths(project_root)
    first_archive = archive_path.read_bytes()
    first_sidecar = sidecar_path.read_text(encoding="utf-8")

    second = run_cli(project_root)
    assert second.returncode == 0, second.stderr or second.stdout
    assert archive_path.read_bytes() == first_archive
    assert sidecar_path.read_text(encoding="utf-8") == first_sidecar
    assert run_cli(project_root, "--check").returncode == 0

    handoff = project_root / "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md"
    handoff.write_text(handoff.read_text(encoding="utf-8") + "\nDrift.\n", encoding="utf-8")

    check = run_cli(project_root, "--check")
    assert check.returncode != 0
    output = (check.stdout + check.stderr).lower()
    assert "stale" in output or "rerun" in output or "mismatch" in output
    assert archive_path.read_bytes() == first_archive
    assert sidecar_path.read_text(encoding="utf-8") == first_sidecar


def test_registry_hash_mismatch_fails_closed_without_rewriting_prior_outputs(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)

    first = run_cli(project_root)
    assert first.returncode == 0, first.stderr or first.stdout
    archive_path, sidecar_path = bundle_paths(project_root)
    before_archive = archive_path.read_bytes()
    before_sidecar = sidecar_path.read_text(encoding="utf-8")

    mutate_registry_sha(
        project_root,
        "research-case/00-governance/program-charter.md",
        "0" * 64,
    )
    result = run_cli(project_root)

    assert result.returncode != 0
    output = (result.stdout + result.stderr).lower()
    assert "sha-256 mismatch" in output or "error" in output
    assert archive_path.read_bytes() == before_archive
    assert sidecar_path.read_text(encoding="utf-8") == before_sidecar


def test_missing_snapshot_markers_fail_closed_before_bundle_write(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)

    handoff = project_root / "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md"
    original = handoff.read_text(encoding="utf-8")
    handoff.write_text(original.replace("<!-- BEGIN GENERATED INTAKE SNAPSHOT -->", ""), encoding="utf-8")

    result = run_cli(project_root)
    archive_path, sidecar_path = bundle_paths(project_root)
    assert result.returncode != 0
    assert not archive_path.exists()
    assert not sidecar_path.exists()
    output = (result.stdout + result.stderr).lower()
    assert "marker" in output or "snapshot" in output or "error" in output


def test_bundle_excludes_deferred_authority_and_contact_artifacts(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)

    result = run_cli(project_root)
    assert result.returncode == 0, result.stderr or result.stdout

    payloads = read_archive(project_root)
    assert (
        "research-case/00-governance/accountable-authority-confirmation.md"
        not in payloads
    )
    combined_text = "\n".join(
        data.decode("utf-8", errors="ignore") for data in payloads.values()
    )
    assert "zmzubraj@gmail.com" not in combined_text
    assert "istiaque@omu.ac.jp" not in combined_text


@pytest.mark.parametrize(
    ("injected_text", "expected_message"),
    [
        ('{"reviewer_contact":"reviewer@example.org"}\n', "contact metadata"),
        ('{"key":"-----BEGIN OPENSSH PRIVATE KEY-----"}\n', "private signing material"),
    ],
)
def test_sensitive_material_in_selected_input_fails_closed(
    tmp_path: Path, injected_text: str, expected_message: str
) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    ledger = project_root / "research-case/00-governance/verification-ledger.jsonl"
    ledger.write_text(
        ledger.read_text(encoding="utf-8") + injected_text,
        encoding="utf-8",
    )

    result = run_cli(project_root)

    archive_path, sidecar_path = bundle_paths(project_root)
    assert result.returncode != 0
    assert expected_message in (result.stdout + result.stderr).lower()
    assert not archive_path.exists()
    assert not sidecar_path.exists()
