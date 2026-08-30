from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "intake_verifier_return_contract.py"
TEMPLATE = Path("review-packets/KEYSTONE-MPP-F1-intake-verifier-return-template.json")
BUNDLE = Path("review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip")

INPUTS = (
    "research-case/program-state.json",
    "research-case/artifact-registry.csv",
    "research-case/00-governance/intake-original.md",
    "research-case/00-governance/intake.json",
    "research-case/00-governance/program-charter.md",
    "research-case/00-governance/study-profile.json",
    BUNDLE.as_posix(),
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
    payload["reviewer"] = {
        "identity": "qualified-reviewer-001",
        "registry_id": "intake-reviewer-001",
        "signing_key_id": "intake-reviewer-key-001",
        "independence_basis": "No production ownership or authorship of reviewed artifacts.",
        "conflicts_disclosure": "None declared.",
        "competence_basis": "Computational security research governance and methods review.",
    }
    for question in payload["question_responses"]:
        question["disposition"] = "PASS"
        question["evidence_locations"] = ["research-case/00-governance/program-charter.md"]
        question["rationale"] = "Directly checked against the frozen intake boundary."
    for index, artifact in enumerate(payload["artifact_dispositions"], start=1):
        artifact["disposition"] = "VERIFIED"
        artifact["verification_event_id"] = f"INTAKE-RETURN-{index:03d}"
        artifact["corrections_required"] = []
        artifact["residual_uncertainty"] = "No material intake-only uncertainty identified."
    payload["overall_disposition"] = "PROCEED_RECOMMENDED"
    payload["reviewer_attestation"] = (
        "INTAKE_ONLY review; no novelty, feasibility, methods, results, manuscript, venue, "
        "submission, or authorship decision is asserted."
    )
    payload["signed_return"] = {
        "signature_path": "outside-case/intake-return.sig",
        "signature_sha256": "a" * 64,
    }
    return payload


def test_template_is_deterministic_hash_bound_and_non_promoting(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)

    first = run_cli(project_root)
    assert first.returncode == 0, first.stderr or first.stdout
    template_path = project_root / TEMPLATE
    first_bytes = template_path.read_bytes()
    payload = json.loads(first_bytes)

    assert payload["schema_id"] == "KEYSTONE_INTAKE_VERIFIER_RETURN"
    assert payload["status"] == "UNCOMPLETED_TEMPLATE"
    assert payload["review_scope"] == "INTAKE_ONLY"
    assert payload["may_promote_phase"] is False
    assert payload["may_assert_novelty"] is False
    assert payload["author_metadata_included"] is False
    assert payload["review_packet_sha256"] == hashlib.sha256(
        (project_root / BUNDLE).read_bytes()
    ).hexdigest()
    assert len(payload["question_responses"]) == 9
    assert len(payload["artifact_dispositions"]) == 4
    assert all(item["disposition"] == "UNANSWERED" for item in payload["question_responses"])

    second = run_cli(project_root)
    assert second.returncode == 0
    assert template_path.read_bytes() == first_bytes
    assert run_cli(project_root, "--check").returncode == 0

    bundle = project_root / BUNDLE
    bundle.write_bytes(bundle.read_bytes() + b"DRIFT")
    stale = run_cli(project_root, "--check")
    assert stale.returncode != 0
    assert "stale" in (stale.stdout + stale.stderr).lower()


def test_completed_return_passes_structural_validation_without_state_write(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    assert run_cli(project_root).returncode == 0
    response = complete_template(project_root / TEMPLATE)
    response_path = project_root / "completed-return.json"
    response_path.write_text(json.dumps(response, indent=2), encoding="utf-8")
    state_before = (project_root / "research-case/program-state.json").read_bytes()

    result = run_cli(project_root, "--validate", str(response_path))

    assert result.returncode == 0, result.stderr or result.stdout
    assert "structure only" in result.stdout.lower()
    assert "does not verify signature" in result.stdout.lower()
    assert (project_root / "research-case/program-state.json").read_bytes() == state_before


def test_validation_rejects_hash_scope_and_incomplete_answers(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    assert run_cli(project_root).returncode == 0
    response = complete_template(project_root / TEMPLATE)
    response["review_packet_sha256"] = "0" * 64
    response["may_promote_phase"] = True
    response["question_responses"][0]["disposition"] = "UNANSWERED"
    response_path = project_root / "invalid-return.json"
    response_path.write_text(json.dumps(response), encoding="utf-8")

    result = run_cli(project_root, "--validate", str(response_path))

    assert result.returncode != 0
    message = (result.stdout + result.stderr).lower()
    assert "packet" in message or "promote" in message or "unanswered" in message


def test_validation_rejects_artifact_drift_and_unbound_verified_event(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    assert run_cli(project_root).returncode == 0
    response = complete_template(project_root / TEMPLATE)
    response["artifact_dispositions"][0]["sha256"] = "f" * 64
    response["artifact_dispositions"][1]["verification_event_id"] = ""
    response_path = project_root / "invalid-artifact-return.json"
    response_path.write_text(json.dumps(response), encoding="utf-8")

    result = run_cli(project_root, "--validate", str(response_path))

    assert result.returncode != 0
    message = (result.stdout + result.stderr).lower()
    assert "artifact" in message or "verification event" in message
