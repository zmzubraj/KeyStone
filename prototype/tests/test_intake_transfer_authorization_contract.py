from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "intake_transfer_authorization_contract.py"
TEMPLATE = Path("review-packets/KEYSTONE-MPP-F1-intake-transfer-authorization-template.json")
DRAFT = Path("review-packets/KEYSTONE-MPP-F1-intake-transfer-authorization-draft.json")
INPUTS = (
    "research-case/program-state.json",
    "research-case/00-governance/accountable-authority-confirmation.md",
    "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md",
    "docs/23_INDEPENDENT_INTAKE_HUMAN_VERIFICATION_SOP_BN.md",
    "docs/24_INVALID_AI_INTAKE_VERIFICATION_QUARANTINE.md",
    "review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip",
    "review-packets/KEYSTONE-MPP-F1-intake-verifier-return-template.json",
)


def copy_inputs(project_root: Path) -> None:
    for rel in INPUTS:
        source = ROOT / rel
        target = project_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def run_cli(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(project_root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def complete_template(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["status"] = "COMPLETED_FOR_STRUCTURAL_VALIDATION"
    payload["accountable_human"] = {
        "identity": "Zubaer Mahmood Zubraj",
        "contact": "zmzubraj@gmail.com",
        "policy_basis_confirmation": "YES_MATCHES_CURRENT_CONFIRMATION",
    }
    payload["named_reviewer"] = {
        "identity": "independent-reviewer-001",
        "affiliation_or_role": "Independent computational security reviewer",
        "contact": "reviewer@example.org",
        "independence_basis": "No authorship or production ownership of the reviewed intake artifacts.",
        "conflicts_disclosure": "No material conflict declared.",
    }
    payload["transfer_channel"] = {
        "channel_type": "encrypted_email",
        "destination": "reviewer@example.org",
        "confidentiality_boundary": "Only the listed INTAKE handoff artifacts may be sent.",
        "institutional_policy_notes": "No contradictory rule reported for this transfer.",
    }
    payload["authorization_id"] = "REM001-TRANSFER-APPROVAL-001"
    payload["authorization_decision"] = "APPROVED_FOR_TRANSFER"
    payload["decision_rationale"] = "Named reviewer, transfer channel, and confidentiality boundary were explicitly approved."
    payload["authorization_attestation"] = (
        "I approve transfer of only the listed INTAKE handoff artifacts to the named reviewer. "
        "This approval does not promote any scientific gate, authorize execution, or freeze author metadata."
    )
    return payload


def test_template_is_deterministic_hash_bound_and_non_promoting(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)

    first = run_cli(project_root)
    assert first.returncode == 0, first.stderr or first.stdout
    template_path = project_root / TEMPLATE
    first_bytes = template_path.read_bytes()
    payload = json.loads(first_bytes)

    assert payload["schema_id"] == "KEYSTONE_INTAKE_TRANSFER_AUTHORIZATION"
    assert payload["status"] == "UNCOMPLETED_TEMPLATE"
    assert payload["authorization_scope"] == "INTAKE_EXTERNAL_TRANSFER_ONLY"
    assert payload["constraints"]["may_promote_phase"] is False
    assert payload["constraints"]["may_assert_independent_verification"] is False
    assert len(payload["allowed_transfer_artifacts"]) == 5

    second = run_cli(project_root)
    assert second.returncode == 0
    assert template_path.read_bytes() == first_bytes
    assert run_cli(project_root, "--check").returncode == 0


def test_draft_is_deterministic_prefilled_and_non_authorizing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)

    first = run_cli(project_root, "--draft")
    assert first.returncode == 0, first.stderr or first.stdout
    draft_path = project_root / DRAFT
    first_bytes = draft_path.read_bytes()
    payload = json.loads(first_bytes)

    assert payload["schema_id"] == "KEYSTONE_INTAKE_TRANSFER_AUTHORIZATION"
    assert payload["status"] == "DRAFT_PENDING_ACCOUNTABLE_HUMAN"
    assert payload["authorization_decision"] == "UNANSWERED"
    assert payload["accountable_human"]["identity"] == "Zubaer Mahmood Zubraj"
    assert payload["accountable_human"]["contact"] == "zmzubraj@gmail.com"
    assert payload["constraints"]["may_promote_phase"] is False
    assert payload["named_reviewer"]["identity"] == ""
    assert len(payload["draft_instructions"]) == 5

    second = run_cli(project_root, "--draft")
    assert second.returncode == 0
    assert draft_path.read_bytes() == first_bytes
    assert run_cli(project_root, "--check-draft").returncode == 0


def test_completed_authorization_passes_structural_validation(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    assert run_cli(project_root).returncode == 0
    response = complete_template(project_root / TEMPLATE)
    response_path = project_root / "completed-authorization.json"
    response_path.write_text(json.dumps(response, indent=2), encoding="utf-8")

    result = run_cli(project_root, "--validate", str(response_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "structure only" in result.stdout.lower()
    assert "does not verify human identity" in result.stdout.lower()


def test_validation_rejects_drifted_packet_scope_and_promotion_flags(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    assert run_cli(project_root).returncode == 0
    response = complete_template(project_root / TEMPLATE)
    response["review_packet_sha256"] = "0" * 64
    response["constraints"]["may_promote_phase"] = True
    response_path = project_root / "invalid-authorization.json"
    response_path.write_text(json.dumps(response), encoding="utf-8")

    result = run_cli(project_root, "--validate", str(response_path))

    assert result.returncode != 0
    message = (result.stdout + result.stderr).lower()
    assert "drift" in message or "scope" in message or "promote" in message


def test_validation_rejects_self_approval_and_missing_boundary(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    assert run_cli(project_root).returncode == 0
    response = complete_template(project_root / TEMPLATE)
    response["named_reviewer"]["identity"] = "Zubaer Mahmood Zubraj"
    response["transfer_channel"]["confidentiality_boundary"] = ""
    response_path = project_root / "invalid-self-approval.json"
    response_path.write_text(json.dumps(response), encoding="utf-8")

    result = run_cli(project_root, "--validate", str(response_path))

    assert result.returncode != 0
    message = (result.stdout + result.stderr).lower()
    assert "reviewer" in message or "boundary" in message


def test_draft_check_rejects_stale_scope(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    assert run_cli(project_root, "--draft").returncode == 0
    draft_path = project_root / DRAFT
    payload = json.loads(draft_path.read_text(encoding="utf-8"))
    payload["review_packet_sha256"] = "0" * 64
    draft_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    result = run_cli(project_root, "--check-draft")

    assert result.returncode != 0
    assert "draft is stale" in (result.stdout + result.stderr).lower()
