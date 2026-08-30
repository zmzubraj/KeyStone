from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "export_pc02_novelty_verifier_packet.py"

DOCUMENT = Path("docs/21_PC02_NOVELTY_VERIFIER_HANDOFF.md")
BUNDLE = Path("review-packets/KEYSTONE-MPP-F1-pc02-novelty-review-packet.zip")
SIDECAR = Path(f"{BUNDLE}.sha256")

NOVELTY_PATHS = (
    "research-case/01-novelty/novelty-claim-specification.md",
    "research-case/01-novelty/search-protocol.md",
    "research-case/01-novelty/prior-art-query-log.json",
    "research-case/01-novelty/prior-art-raw-snapshots.json",
    "research-case/01-novelty/prior-art-dedup-report.json",
    "research-case/01-novelty/search-coverage.csv",
    "research-case/01-novelty/evidence-ledger.csv",
    "research-case/01-novelty/independent-search-challenge.md",
    "research-case/01-novelty/novelty-matrix.csv",
    "research-case/01-novelty/citation-audit.md",
)

INPUT_PATHS = (
    "research-case/artifact-registry.csv",
    "research-case/program-state.json",
    "research-case/00-governance/verifier-registry.json",
    "research-case/00-governance/verification-ledger.jsonl",
    *NOVELTY_PATHS,
)


def copy_inputs(project_root: Path) -> None:
    for rel in INPUT_PATHS:
        source = ROOT / rel
        target = project_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def run_cli(project_root: Path, *argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(project_root), *argv],
        text=True,
        capture_output=True,
        check=False,
    )


def test_packet_is_deterministic_hash_bound_and_fail_closed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)

    first = run_cli(project_root)
    assert first.returncode == 0, first.stderr or first.stdout
    document = project_root / DOCUMENT
    bundle = project_root / BUNDLE
    sidecar = project_root / SIDECAR
    assert document.is_file() and bundle.is_file() and sidecar.is_file()

    document_text = document.read_text(encoding="utf-8")
    assert "Developmental reviewer handoff only" in document_text
    assert "does not certify novelty" in document_text
    assert "signed qualified verification event" in document_text
    assert "author metadata is deferred" in document_text.lower()
    assert "must not be transferred until `REM-001` is actually recorded" in document_text
    assert "bounded `REFRAME` lane" in document_text
    for rel in NOVELTY_PATHS:
        assert rel in document_text

    expected_sidecar = f"{hashlib.sha256(bundle.read_bytes()).hexdigest()}  ./{BUNDLE.as_posix()}\n"
    assert sidecar.read_text(encoding="utf-8") == expected_sidecar

    with zipfile.ZipFile(bundle) as archive:
        names = tuple(archive.namelist())
        assert names == ("README.md", "bundle-manifest.json", DOCUMENT.as_posix(), *NOVELTY_PATHS)
        manifest = json.loads(archive.read("bundle-manifest.json"))
        assert manifest["schema_id"] == "KEYSTONE_PC02_NOVELTY_REVIEW_BUNDLE"
        assert manifest["status"] == "PREPARED_FOR_QUALIFIED_EXTERNAL_REVIEW"
        assert manifest["canonical_phase"] == "INTAKE"
        assert manifest["novelty_status"] == "UNRESOLVED"
        assert manifest["may_assert_novelty"] is False
        assert manifest["broad_primitive_novelty_rejected"] is True
        assert manifest["surviving_disposition_ceiling"] == "REFRAME_ONLY"
        assert manifest["transfer_prerequisite_remediation"] == "REM-001"
        assert manifest["external_transfer_authorized"] is False
        assert tuple(item["archive_path"] for item in manifest["source_files"]) == names

    before = (document.read_bytes(), bundle.read_bytes(), sidecar.read_bytes())
    second = run_cli(project_root)
    assert second.returncode == 0, second.stderr or second.stdout
    assert (document.read_bytes(), bundle.read_bytes(), sidecar.read_bytes()) == before
    assert run_cli(project_root, "--check").returncode == 0

    target = project_root / NOVELTY_PATHS[0]
    target.write_text(target.read_text(encoding="utf-8") + "\nDRIFT\n", encoding="utf-8")
    stale = run_cli(project_root, "--check")
    assert stale.returncode != 0
    assert "mismatch" in (stale.stdout + stale.stderr).lower()


def test_packet_rejects_phase_or_registry_drift(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)

    state_path = project_root / "research-case/program-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["current_phase"] = "NOVELTY_AUDIT"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    result = run_cli(project_root)
    assert result.returncode != 0
    assert "intake" in (result.stdout + result.stderr).lower()

    copy_inputs(project_root)
    registry_path = project_root / "research-case/artifact-registry.csv"
    with registry_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        assert fieldnames is not None
        rows = list(reader)
    wanted = NOVELTY_PATHS[0].removeprefix("research-case/")
    for row in rows:
        if row.get("path") == wanted:
            row["sha256"] = "0" * 64
            break
    with registry_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    result = run_cli(project_root)
    assert result.returncode != 0
    assert "mismatch" in (result.stdout + result.stderr).lower()


def test_packet_excludes_contact_and_private_key_material(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    result = run_cli(project_root)
    assert result.returncode == 0, result.stderr or result.stdout

    with zipfile.ZipFile(project_root / BUNDLE) as archive:
        payload = b"\n".join(archive.read(name) for name in archive.namelist())
    assert b"@gmail.com" not in payload
    assert b"@omu.ac.jp" not in payload
    assert b"BEGIN OPENSSH PRIVATE KEY" not in payload
