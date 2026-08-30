from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "export_pc03_methods_verifier_packet.py"

DOCUMENT = Path("docs/22_PC03_METHODS_VERIFIER_HANDOFF.md")
BUNDLE = Path("review-packets/KEYSTONE-MPP-F1-pc03-methods-review-packet.zip")
SIDECAR = Path(f"{BUNDLE}.sha256")

METHODS_PATHS = (
    "research-case/03-design/protocol.md",
    "research-case/03-design/analysis-plan.md",
    "research-case/03-design/power-or-precision.md",
    "research-case/03-design/preregistration-and-deviations.md",
    "research-case/03-design/pc03-prospective-amendment.md",
    "research-case/03-design/pc03-prospective-counts.csv",
    "research-case/03-design/pc03-seed-schedule.csv",
    "research-case/03-design/pc03-independent-methods-challenge/design-assessment.md",
    "research-case/03-design/pc03-independent-methods-challenge/prospective-counts.csv",
    "research-case/03-design/pc03-independent-methods-challenge/calculation-notes.md",
    "research-case/02-feasibility/pilot-plan.md",
    "research-case/02-feasibility/pilot-run-contract.csv",
    "prototype/src/keystone/simulation.py",
    "prototype/scripts/run_experiments.py",
    "prototype/configs/baseline.json",
)

INPUT_PATHS = (
    "research-case/artifact-registry.csv",
    "research-case/program-state.json",
    "research-case/00-governance/verifier-registry.json",
    "research-case/00-governance/verification-ledger.jsonl",
    *METHODS_PATHS,
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
    assert "PREPARED_FOR_QUALIFIED_EXTERNAL_METHODS_REVIEW" in document_text
    assert "Developmental methods-review handoff only" in document_text
    assert "CORR" in document_text and "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE" in document_text
    assert "DEADLINE" in document_text and "EXCLUDED_PENDING_ENVIRONMENT_PROFILE" in document_text
    assert "PASS" in document_text and "PARTIAL" in document_text
    assert "FAIL" in document_text and "UNKNOWN" in document_text
    assert "author metadata is deferred" in document_text.lower()
    assert "131,072" in document_text
    assert "73,778" in document_text
    assert "must not be transferred until `REM-001` is recorded" in document_text
    assert "`REM-002` remains confined to the bounded novelty `REFRAME` lane" in document_text
    assert "does not authorize confirmatory execution" in document_text
    for rel in METHODS_PATHS:
        assert rel in document_text

    expected_sidecar = f"{hashlib.sha256(bundle.read_bytes()).hexdigest()}  ./{BUNDLE.as_posix()}\n"
    assert sidecar.read_text(encoding="utf-8") == expected_sidecar

    with zipfile.ZipFile(bundle) as archive:
        names = tuple(archive.namelist())
        assert names == ("README.md", "bundle-manifest.json", DOCUMENT.as_posix(), *METHODS_PATHS)
        manifest = json.loads(archive.read("bundle-manifest.json"))
        assert manifest["schema_id"] == "KEYSTONE_PC03_METHODS_REVIEW_BUNDLE"
        assert manifest["status"] == "PREPARED_FOR_QUALIFIED_EXTERNAL_METHODS_REVIEW"
        assert manifest["canonical_phase"] == "INTAKE"
        assert manifest["novelty_status"] == "UNRESOLVED"
        assert manifest["feasibility_decision"] == "UNASSESSED"
        assert manifest["solution_viability_status"] == "ASSERTED_ONLY"
        assert manifest["acceptance_readiness"] == "NOT_ASSESSABLE"
        assert manifest["may_authorize_execution"] is False
        assert manifest["may_assert_methods_verified"] is False
        assert manifest["may_promote_phase"] is False
        assert manifest["transfer_prerequisite_remediations"] == ["REM-001", "REM-002"]
        assert manifest["external_transfer_authorized"] is False
        assert manifest["execution_prerequisite_remediation"] == "REM-003"
        assert manifest["separate_accountable_start_required"] is True
        assert manifest["author_metadata_included"] is False
        assert manifest["included_result_ids"] == [
            "RID-C003-IID-001",
            "RID-C003-STRAT-001",
            "RID-C003-SW-001",
        ]
        assert tuple(item["archive_path"] for item in manifest["source_files"]) == names

    before = (document.read_bytes(), bundle.read_bytes(), sidecar.read_bytes())
    second = run_cli(project_root)
    assert second.returncode == 0, second.stderr or second.stdout
    assert (document.read_bytes(), bundle.read_bytes(), sidecar.read_bytes()) == before
    assert run_cli(project_root, "--check").returncode == 0

    target = project_root / METHODS_PATHS[0]
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
    rows = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(rows.replace("03-design/protocol.md", "03-design/protocol-missing.md", 1), encoding="utf-8")
    result = run_cli(project_root)
    assert result.returncode != 0
    assert "missing" in (result.stdout + result.stderr).lower()


def test_packet_rejects_count_seed_or_exclusion_drift(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    counts = project_root / "research-case/03-design/pc03-prospective-counts.csv"
    counts.write_text(counts.read_text(encoding="utf-8").replace("73778", "73777", 1), encoding="utf-8")
    result = run_cli(project_root)
    assert result.returncode != 0
    assert "mismatch" in (result.stdout + result.stderr).lower()

    copy_inputs(project_root)
    seeds = project_root / "research-case/03-design/pc03-seed-schedule.csv"
    lines = seeds.read_text(encoding="utf-8").splitlines()
    seeds.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    result = run_cli(project_root)
    assert result.returncode != 0
    assert "108" in (result.stdout + result.stderr)

    copy_inputs(project_root)
    amendment = project_root / "research-case/03-design/pc03-prospective-amendment.md"
    amendment.write_text(
        amendment.read_text(encoding="utf-8").replace(
            "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE", "BLOCKED_PENDING_GATE"
        ),
        encoding="utf-8",
    )
    result = run_cli(project_root)
    assert result.returncode != 0


def test_packet_rejects_contact_metadata_in_review_inputs(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    amendment = project_root / "research-case/03-design/pc03-prospective-amendment.md"
    amendment.write_text(
        amendment.read_text(encoding="utf-8").replace(
            "Author metadata remains deferred.", "Corresponding author is person@example.org."
        ),
        encoding="utf-8",
    )
    result = run_cli(project_root)
    assert result.returncode != 0
    message = (result.stdout + result.stderr).lower()
    assert "contact metadata" in message or "author metadata remains deferred" in message


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
