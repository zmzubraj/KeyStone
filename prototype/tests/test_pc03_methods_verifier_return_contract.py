from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "pc03_methods_verifier_return_contract.py"
TEMPLATE = Path("review-packets/KEYSTONE-MPP-F1-pc03-methods-verifier-return-template.json")
BUNDLE = Path("review-packets/KEYSTONE-MPP-F1-pc03-methods-review-packet.zip")

INPUTS = (
    "research-case/program-state.json",
    "research-case/artifact-registry.csv",
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
        "identity": "qualified-methods-reviewer-001",
        "registry_id": "pc03-reviewer-001",
        "signing_key_id": "pc03-reviewer-key-001",
        "independence_basis": "No producer ownership of reviewed methods artifacts.",
        "conflicts_disclosure": "None declared.",
        "competence_basis": "Statistical simulation and experimental-methods review.",
    }
    for question in payload["question_responses"]:
        question["disposition"] = "PASS"
        question["evidence_locations"] = ["research-case/03-design/analysis-plan.md"]
        question["calculation_or_code_evidence"] = "Recomputed against the frozen methods packet."
        question["consequence"] = "No phase promotion or execution authorization is implied."
        question["smallest_adequate_correction"] = "None required for structural validation."
    for index, artifact in enumerate(payload["artifact_dispositions"], start=1):
        artifact["disposition"] = "VERIFIED"
        artifact["verification_event_id"] = f"PC03-RETURN-{index:03d}"
        artifact["corrections_required"] = []
        artifact["residual_uncertainty"] = "Independent execution authorization remains outside this contract."
    payload["overall_disposition"] = "ACCEPT_AS_DRAFT"
    payload["reviewer_attestation"] = (
        "PC03 methods-only review; no novelty, feasibility, execution, manuscript, venue, "
        "submission, or authorship decision is asserted."
    )
    payload["signed_return"] = {
        "signature_path": "outside-case/pc03-return.sig",
        "signature_sha256": "c" * 64,
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

    assert payload["schema_id"] == "KEYSTONE_PC03_METHODS_VERIFIER_RETURN"
    assert payload["status"] == "UNCOMPLETED_TEMPLATE"
    assert payload["review_scope"] == "PC03_METHODS_ONLY"
    assert payload["may_promote_phase"] is False
    assert payload["may_authorize_execution"] is False
    assert payload["author_metadata_included"] is False
    assert payload["review_packet_sha256"] == hashlib.sha256(
        (project_root / BUNDLE).read_bytes()
    ).hexdigest()
    assert len(payload["question_responses"]) == 12
    assert len(payload["artifact_dispositions"]) == 15
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
    response["may_authorize_execution"] = True
    response["question_responses"][0]["disposition"] = "UNANSWERED"
    response_path = project_root / "invalid-return.json"
    response_path.write_text(json.dumps(response), encoding="utf-8")

    result = run_cli(project_root, "--validate", str(response_path))

    assert result.returncode != 0
    message = (result.stdout + result.stderr).lower()
    assert "packet" in message or "authorize" in message or "unanswered" in message


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
