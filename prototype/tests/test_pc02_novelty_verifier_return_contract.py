from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "pc02_novelty_verifier_return_contract.py"
TEMPLATE = Path("review-packets/KEYSTONE-MPP-F1-pc02-novelty-verifier-return-template.json")
BUNDLE = Path("review-packets/KEYSTONE-MPP-F1-pc02-novelty-review-packet.zip")

INPUTS = (
    "research-case/program-state.json",
    "research-case/artifact-registry.csv",
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
        "identity": "qualified-novelty-reviewer-001",
        "registry_id": "pc02-reviewer-001",
        "signing_key_id": "pc02-reviewer-key-001",
        "independence_basis": "No producer ownership of reviewed novelty artifacts.",
        "conflicts_disclosure": "None declared.",
        "competence_basis": "Prior-art and novelty review for computational systems research.",
    }
    for question in payload["question_responses"]:
        question["disposition"] = "QUALIFIED"
        question["evidence_locations"] = ["research-case/01-novelty/novelty-matrix.csv"]
        question["strongest_predecessor"] = "bounded-predecessor-001"
        question["decisive_overlap_or_differentiator"] = "Narrow DKA versus ciphertext-availability distinction remains bounded."
        question["access_limitations"] = "Public search only; no proprietary corpus access."
        question["rationale"] = "Reviewed against the bounded REFRAME novelty packet."
    for index, artifact in enumerate(payload["artifact_dispositions"], start=1):
        artifact["disposition"] = "VERIFIED"
        artifact["verification_event_id"] = f"PC02-RETURN-{index:03d}"
        artifact["corrections_required"] = []
        artifact["residual_uncertainty"] = "Residual uncertainty remains bounded to inaccessible sources."
    payload["overall_disposition"] = "REFRAME"
    payload["reviewer_attestation"] = (
        "PC02 novelty-only review; no feasibility, methods, execution, manuscript, venue, "
        "submission, or authorship decision is asserted."
    )
    payload["signed_return"] = {
        "signature_path": "outside-case/pc02-return.sig",
        "signature_sha256": "b" * 64,
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

    assert payload["schema_id"] == "KEYSTONE_PC02_NOVELTY_VERIFIER_RETURN"
    assert payload["status"] == "UNCOMPLETED_TEMPLATE"
    assert payload["review_scope"] == "PC02_NOVELTY_ONLY"
    assert payload["may_promote_phase"] is False
    assert payload["may_assert_novelty"] is False
    assert payload["author_metadata_included"] is False
    assert payload["review_packet_sha256"] == hashlib.sha256(
        (project_root / BUNDLE).read_bytes()
    ).hexdigest()
    assert len(payload["question_responses"]) == 5
    assert len(payload["artifact_dispositions"]) == 10
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
    response["may_assert_novelty"] = True
    response["question_responses"][0]["disposition"] = "UNANSWERED"
    response_path = project_root / "invalid-return.json"
    response_path.write_text(json.dumps(response), encoding="utf-8")

    result = run_cli(project_root, "--validate", str(response_path))

    assert result.returncode != 0
    message = (result.stdout + result.stderr).lower()
    assert "packet" in message or "novelty" in message or "unanswered" in message


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
