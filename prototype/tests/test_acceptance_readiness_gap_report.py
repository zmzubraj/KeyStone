from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export_acceptance_readiness_gap_report.py"


FIELDNAMES = [
    "path",
    "phase",
    "required",
    "owner",
    "status",
    "revision",
    "sha256",
]
REMEDIATION_FIELDS = [
    "remediation_id",
    "priority",
    "status",
    "question_ids",
    "claim_ids",
    "owner",
    "action",
    "required_evidence",
    "acceptance_test",
    "dependencies",
    "new_data_required",
    "notes",
]


def _write_case(root: Path) -> Path:
    state = {
        "system_name": "KEYSTONE-MPP-F1",
        "status": "ACTIVE",
        "current_phase": "INTAKE",
        "resume_from": "INTAKE",
        "novelty_status": "UNRESOLVED",
        "feasibility_decision": "UNASSESSED",
        "solution_viability_status": "ASSERTED_ONLY",
        "postdoctoral_ai_audit": "UNASSESSED",
        "acceptance_readiness": "NOT_ASSESSABLE",
        "maturity_stage": "CONCEPT",
        "next_action": "Verify intake before novelty work.",
    }
    state_path = root / "research-case/program-state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    registry_path = root / "research-case/artifact-registry.csv"
    rows = [
        {
            "path": "00-governance/study-profile.json",
            "phase": "INTAKE",
            "required": "true",
            "owner": "root-integration-owner",
            "status": "DRAFT",
            "revision": "3",
            "sha256": "a" * 64,
        },
        {
            "path": "01-novelty/novelty-matrix.csv",
            "phase": "NOVELTY_AUDIT",
            "required": "true",
            "owner": "novelty_synthesis",
            "status": "MISSING",
            "revision": "0",
            "sha256": "",
        },
        {
            "path": "07-manuscript/manuscript.md",
            "phase": "MANUSCRIPT",
            "required": "true",
            "owner": "manuscript_integration",
            "status": "DRAFT",
            "revision": "13",
            "sha256": "b" * 64,
        },
        {
            "path": "09-submission/acceptance-readiness.md",
            "phase": "SUBMISSION_QA",
            "required": "true",
            "owner": "UNASSIGNED",
            "status": "MISSING",
            "revision": "0",
            "sha256": "",
        },
        {
            "path": "09-submission/build-manifest.json",
            "phase": "SUBMISSION_QA",
            "required": "false",
            "owner": "UNASSIGNED",
            "status": "MISSING",
            "revision": "0",
            "sha256": "",
        },
    ]
    with registry_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    remediation_path = root / "research-case/08-validation/remediation-log.csv"
    remediation_path.parent.mkdir(parents=True, exist_ok=True)
    remediation_rows = [
        {
            "remediation_id": "REM-001",
            "priority": "P0",
            "status": "OPEN",
            "question_ids": "KQ-017",
            "claim_ids": "C001|C002|C003",
            "owner": "human_approval",
            "action": "Obtain canonical independent INTAKE verification.",
            "required_evidence": "Signed hash-bound verifier return from a registered independent identity.",
            "acceptance_test": "Return contract validates and canonical gate transition is independently authorized.",
            "dependencies": "",
            "new_data_required": "false",
            "notes": "No AI or same-owner mechanical check can satisfy this gate.",
        },
        {
            "remediation_id": "REM-002",
            "priority": "P1",
            "status": "OPEN",
            "question_ids": "KQ-002|KQ-003",
            "claim_ids": "C001",
            "owner": "novelty_synthesis",
            "action": "Close and independently challenge the narrow novelty claim.",
            "required_evidence": "Search and signed challenge.",
            "acceptance_test": "NOVELTY_SURVIVES or REFRAME is recorded.",
            "dependencies": "REM-001",
            "new_data_required": "false",
            "notes": "Broad novelty remains rejected.",
        },
        {
            "remediation_id": "REM-010",
            "priority": "P2",
            "status": "DEFERRED",
            "question_ids": "KQ-016",
            "claim_ids": "C001|C002|C003",
            "owner": "human_approval",
            "action": "Freeze complete authorship and disclosure metadata.",
            "required_evidence": "Human-approved metadata.",
            "acceptance_test": "All metadata approved.",
            "dependencies": "REM-008",
            "new_data_required": "false",
            "notes": "Deferred by explicit user instruction; do not infer now.",
        },
    ]
    with remediation_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REMEDIATION_FIELDS)
        writer.writeheader()
        writer.writerows(remediation_rows)

    build_manifest = {
        "status": "DRAFT_PREAUTHORIZATION_NOT_SUBMISSION_READY",
        "canonical_phase": "INTAKE",
        "canonical_acceptance_readiness": "NOT_ASSESSABLE",
        "build_classification": "INTERNAL_PREAUTHORIZATION_ONLY",
        "submission_authorized": False,
        "external_transfer_authorized": False,
        "blocking_serial_gate": "INTAKE",
        "external_review_blocker": "REM-001",
        "page_count": 21,
        "outputs": [{"path": "paper/preauthorization-build/main.pdf", "sha256": "c" * 64}],
    }
    build_manifest_path = root / "paper/preauthorization-build/build-manifest.json"
    build_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    build_manifest_path.write_text(json.dumps(build_manifest, indent=2) + "\n", encoding="utf-8")

    for rel in (
        "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md",
        "docs/23_INDEPENDENT_INTAKE_HUMAN_VERIFICATION_SOP_BN.md",
        "docs/24_INVALID_AI_INTAKE_VERIFICATION_QUARANTINE.md",
        "review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip",
        "review-packets/KEYSTONE-MPP-F1-intake-verifier-return-template.json",
        "docs/21_PC02_NOVELTY_VERIFIER_HANDOFF.md",
        "review-packets/KEYSTONE-MPP-F1-pc02-novelty-review-packet.zip",
        "review-packets/KEYSTONE-MPP-F1-pc02-novelty-verifier-return-template.json",
    ):
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("placeholder\n", encoding="utf-8")
    return root


def _run(root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *extra],
        text=True,
        capture_output=True,
        check=False,
    )


def test_export_writes_fail_closed_gap_report_from_canonical_state(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")

    result = _run(root)

    assert result.returncode == 0, result.stderr
    report = (root / "research-case/09-submission/acceptance-readiness.md").read_text()
    assert "Acceptance readiness: `NOT_ASSESSABLE`" in report
    assert "Current serial gate: `INTAKE`" in report
    assert "External independent INTAKE verification | `BLOCKING`" in report
    assert "## Draft preauthorization build snapshot" in report
    assert "internal preauthorization only" in report
    assert "does **not** satisfy `REM-009`" in report
    assert "| Build classification | `INTERNAL_PREAUTHORIZATION_ONLY` |" in report
    assert "| Draft PDF page count | `21` |" in report
    assert "`paper/preauthorization-build/build-manifest.json`" in report
    assert "`paper/preauthorization-build/main.pdf`" in report
    assert "## Priority remediation and external-review queue" in report
    assert "`REM-001`" in report
    assert "`REM-002`" in report
    assert "`REM-010`" in report
    assert "`docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md`" in report
    assert "`docs/23_INDEPENDENT_INTAKE_HUMAN_VERIFICATION_SOP_BN.md`" in report
    assert "`docs/24_INVALID_AI_INTAKE_VERIFICATION_QUARANTINE.md`" in report
    assert "`review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip`" in report
    assert "do not authorize external transfer" in report
    assert "follow the human-verification SOP" in report
    assert "invalid-AI quarantine boundary" in report
    assert "keep deferred until every accountable author explicitly approves metadata freeze" in report
    assert "Final author order, corresponding-author designation, and exact affiliation wording remain deferred." in report
    assert "| `DRAFT` | 2 |" in report
    assert "| `MISSING` | 1 |" in report
    assert "`01-novelty/novelty-matrix.csv`" in report
    assert "`09-submission/build-manifest.json`" not in report
    assert "This report is a mechanical gap inventory, not independent scientific review" in report


def test_rejects_submission_authorized_preauthorization_manifest(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")
    manifest_path = root / "paper/preauthorization-build/build-manifest.json"
    payload = json.loads(manifest_path.read_text())
    payload["submission_authorized"] = True
    manifest_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    result = _run(root)

    assert result.returncode == 1
    assert "preauthorization build manifest must keep submission_authorized=false" in result.stderr


def test_check_detects_stale_report_after_registry_change(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")
    assert _run(root).returncode == 0
    registry = root / "research-case/artifact-registry.csv"
    registry.write_text(registry.read_text().replace("MISSING,0", "DRAFT,1", 1), encoding="utf-8")

    result = _run(root, "--check")

    assert result.returncode == 1
    assert "acceptance-readiness gap report is stale" in result.stderr


def test_check_passes_for_current_report(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")
    assert _run(root).returncode == 0

    result = _run(root, "--check")

    assert result.returncode == 0, result.stderr
    assert "acceptance-readiness gap report is current" in result.stdout


def test_refuses_to_generate_after_readiness_becomes_assessable(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")
    state_path = root / "research-case/program-state.json"
    state = json.loads(state_path.read_text())
    state["acceptance_readiness"] = "NOT_READY"
    state_path.write_text(json.dumps(state) + "\n", encoding="utf-8")

    result = _run(root)

    assert result.returncode == 1
    assert "gap exporter only supports canonical NOT_ASSESSABLE state" in result.stderr


def test_duplicate_registry_path_fails_closed(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")
    registry = root / "research-case/artifact-registry.csv"
    lines = registry.read_text().splitlines()
    registry.write_text("\n".join(lines + [lines[1]]) + "\n", encoding="utf-8")

    result = _run(root)

    assert result.returncode == 1
    assert "duplicate artifact registry path: 00-governance/study-profile.json" in result.stderr


def test_duplicate_remediation_id_fails_closed(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")
    remediation = root / "research-case/08-validation/remediation-log.csv"
    lines = remediation.read_text().splitlines()
    remediation.write_text("\n".join(lines + [lines[1]]) + "\n", encoding="utf-8")

    result = _run(root)

    assert result.returncode == 1
    assert "duplicate remediation id: REM-001" in result.stderr
