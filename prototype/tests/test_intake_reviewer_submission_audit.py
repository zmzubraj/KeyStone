from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/intake_reviewer_submission_audit.py"
REPORT = ROOT / (
    "review-packets/reviewer-submissions/"
    "KEYSTONE-MPP-F1-intake-reviewer-submission-audit.json"
)


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(ROOT), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def test_workspace_audit_is_current_and_fail_closed() -> None:
    result = _run("--check")
    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(REPORT.read_text(encoding="utf-8"))

    assert payload["schema_id"] == "KEYSTONE_INTAKE_REVIEWER_SUBMISSION_AUDIT"
    assert payload["overall_status"] == "INCOMPLETE"
    assert payload["may_promote_phase"] is False
    assert payload["canonical_phase"] == "INTAKE"
    assert payload["checks"]["signed_verifier_registry"] == "PASS"
    assert payload["checks"]["completed_return_structure"] in {"PASS", "FAIL"}
    assert payload["details"]["required_signature_namespace"] == "keystone-mpp-f1-intake"
    assert payload["checks"]["canonical_verification_events"] in {"PASS", "FAIL"}
    assert payload["blocking_reasons"]


def test_require_complete_fails_for_current_incomplete_submission() -> None:
    result = _run("--require-complete")
    assert result.returncode == 1
    assert "INCOMPLETE" in (result.stdout + result.stderr)


def test_attestation_binding_requires_every_contract_token() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from intake_reviewer_submission_audit import attestation_binding_errors

    response = {
        "review_packet_sha256": "a" * 64,
        "reviewer": {
            "identity": "reviewer-1",
            "registry_id": "registry-1",
            "signing_key_id": "key-1",
        },
        "question_responses": [
            {"question_id": "INTAKE-Q01", "disposition": "PASS"}
        ],
        "artifact_dispositions": [
            {
                "path": "research-case/00-governance/intake.json",
                "revision": "2",
                "sha256": "b" * 64,
                "disposition": "VERIFIED",
                "verification_event_id": "INTAKE-NORMALIZED-001",
            }
        ],
        "overall_disposition": "PROCEED_RECOMMENDED",
        "may_promote_phase": False,
        "may_assert_novelty": False,
        "may_authorize_execution": False,
        "author_metadata_included": False,
        "reviewer_attestation": "INTAKE-only independent review.",
    }
    complete_text = "\n".join(
        [
            "reviewer-1 registry-1 key-1",
            "a" * 64,
            "INTAKE-Q01 PASS",
            "research-case/00-governance/intake.json revision 2 VERIFIED ",
            "b" * 64,
            "INTAKE-NORMALIZED-001",
            "PROCEED_RECOMMENDED",
            "may_promote_phase=false may_assert_novelty=false",
            "may_authorize_execution=false author_metadata_included=false",
            "INTAKE-only independent review.",
        ]
    )

    assert attestation_binding_errors(complete_text, response) == []
    errors = attestation_binding_errors(complete_text.replace("INTAKE-Q01", "Q-X"), response)
    assert any("INTAKE-Q01" in error for error in errors)
