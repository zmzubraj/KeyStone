#!/usr/bin/env python3
"""Export and structurally validate the fail-closed PC03 methods verifier return contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


TEMPLATE = Path("review-packets/KEYSTONE-MPP-F1-pc03-methods-verifier-return-template.json")
BUNDLE = Path("review-packets/KEYSTONE-MPP-F1-pc03-methods-review-packet.zip")
ARTIFACTS = (
    {"path": "research-case/03-design/protocol.md", "registry_required": True},
    {"path": "research-case/03-design/analysis-plan.md", "registry_required": True},
    {"path": "research-case/03-design/power-or-precision.md", "registry_required": True},
    {"path": "research-case/03-design/preregistration-and-deviations.md", "registry_required": True},
    {"path": "research-case/03-design/pc03-prospective-amendment.md", "registry_required": False},
    {"path": "research-case/03-design/pc03-prospective-counts.csv", "registry_required": False},
    {"path": "research-case/03-design/pc03-seed-schedule.csv", "registry_required": False},
    {"path": "research-case/03-design/pc03-independent-methods-challenge/design-assessment.md", "registry_required": False},
    {"path": "research-case/03-design/pc03-independent-methods-challenge/prospective-counts.csv", "registry_required": False},
    {"path": "research-case/03-design/pc03-independent-methods-challenge/calculation-notes.md", "registry_required": False},
    {"path": "research-case/02-feasibility/pilot-plan.md", "registry_required": True},
    {"path": "research-case/02-feasibility/pilot-run-contract.csv", "registry_required": False},
    {"path": "prototype/src/keystone/simulation.py", "registry_required": False},
    {"path": "prototype/scripts/run_experiments.py", "registry_required": False},
    {"path": "prototype/configs/baseline.json", "registry_required": False},
)
QUESTIONS = (
    ("PC03-Q01", "Does the sampling-unit definition match the actual simulator semantics, without treating a seed-run aggregate as a Bernoulli observation?"),
    ("PC03-Q02", "Are scenario draws independent under the frozen generator, and are blockwise estimates sufficient to expose implementation-level dependence or drift?"),
    ("PC03-Q03", "For RID-C003-STRAT-001, does the implementation create true common-random-number matched policy pairs with identical latent scenarios and no unpaired substitution?"),
    ("PC03-Q04", "For RID-C003-SW-001, are audit-pass and dispute-success outcomes evaluated within the same synthetic draw, with the signed gap direction fixed before execution?"),
    ("PC03-Q05", "Recompute both Hoeffding requirements of 73,778 and confirm that 32 x 4,096 = 131,072 valid primary draws exceeds them under the stated bounded outcomes."),
    ("PC03-Q06", "Are all 108 seed-schedule rows unique and deterministic, with exactly 32 primary and four reserve streams for each included result ID?"),
    ("PC03-Q07", "Does the reserve rule replace only documented infrastructure failures and prohibit replacement of valid unfavorable blocks?"),
    ("PC03-Q08", "Is one primary cell per included family sufficient for the frozen minimum claim, with optional secondary tests correctly confined to Holm control?"),
    ("PC03-Q09", "Are CORR and DEADLINE correctly excluded, and is every existing correlated/deadline display prevented from becoming confirmatory evidence?"),
    ("PC03-Q10", "Are missingness, invalid-run, deviation, stopping, negative-result retention, and exploratory-quarantine rules complete and operationally testable?"),
    ("PC03-Q11", "Could any existing exploratory value, figure, or code default have contaminated the chosen cells, precision targets, or decision rules?"),
    ("PC03-Q12", "Does the pilot run contract reproduce the same included/excluded boundaries without introducing a stronger claim or execution authorization?"),
)
EXPECTED_STATE = {
    "status": "ACTIVE",
    "current_phase": "INTAKE",
    "novelty_status": "UNRESOLVED",
    "feasibility_decision": "UNASSESSED",
    "solution_viability_status": "ASSERTED_ONLY",
    "acceptance_readiness": "NOT_ASSESSABLE",
}
QUESTION_DISPOSITIONS = {"PASS", "PARTIAL", "FAIL", "UNKNOWN"}
ARTIFACT_DISPOSITIONS = {"VERIFIED", "QUALIFIED", "REFUTED", "UNKNOWN"}
OVERALL_DISPOSITIONS = {"ACCEPT_AS_DRAFT", "REVISE", "STOP"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ContractError(ValueError):
    """Raised when the return contract is stale, incomplete, or structurally invalid."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON contract input: {path}") from exc
    if not isinstance(payload, dict):
        raise ContractError(f"JSON contract input must be an object: {path}")
    return payload


def validate_state(state: dict[str, Any]) -> None:
    mismatches = [
        f"{key}={state.get(key)!r} expected={expected!r}"
        for key, expected in EXPECTED_STATE.items()
        if state.get(key) != expected
    ]
    if mismatches:
        raise ContractError(
            "PC03 return contract requires fail-closed canonical state: "
            + "; ".join(mismatches)
        )


def registry_artifacts(root: Path) -> list[dict[str, str]]:
    path = root / "research-case/artifact-registry.csv"
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, UnicodeError) as exc:
        raise ContractError(f"cannot read artifact registry: {path}") from exc
    by_path = {row.get("path", ""): row for row in rows}
    output: list[dict[str, str]] = []
    for artifact in ARTIFACTS:
        artifact_path = artifact["path"]
        actual_path = root / artifact_path
        if not actual_path.is_file():
            raise ContractError(f"canonical PC03 artifact is missing: {artifact_path}")
        actual_sha = sha256_bytes(actual_path.read_bytes())
        if artifact["registry_required"]:
            registry_path = artifact_path.removeprefix("research-case/")
            row = by_path.get(registry_path)
            if row is None:
                raise ContractError(f"canonical PC03 artifact is missing from registry: {registry_path}")
            missing = [field for field in ("revision", "sha256", "updated_at") if not row.get(field)]
            if missing:
                raise ContractError(f"registry row {registry_path} is missing: {', '.join(missing)}")
            if actual_sha != row["sha256"]:
                raise ContractError(f"canonical artifact SHA-256 mismatch: {artifact_path}")
            output.append(
                {
                    "path": artifact_path,
                    "revision": row["revision"],
                    "sha256": row["sha256"],
                    "updated_at": row["updated_at"],
                }
            )
            continue
        output.append(
            {
                "path": artifact_path,
                "revision": "N/A",
                "sha256": actual_sha,
                "updated_at": "",
            }
        )
    return output


def build_template(root: Path) -> dict[str, Any]:
    state = load_json(root / "research-case/program-state.json")
    validate_state(state)
    bundle = root / BUNDLE
    if not bundle.is_file():
        raise ContractError(f"PC03 review packet is missing: {bundle}")
    artifacts = registry_artifacts(root)
    return {
        "schema_id": "KEYSTONE_PC03_METHODS_VERIFIER_RETURN",
        "schema_version": 1,
        "status": "UNCOMPLETED_TEMPLATE",
        "review_scope": "PC03_METHODS_ONLY",
        "review_packet_path": BUNDLE.as_posix(),
        "review_packet_sha256": sha256_bytes(bundle.read_bytes()),
        "contract_timestamp": max(item["updated_at"] for item in artifacts if item["updated_at"]),
        "canonical_phase": "INTAKE",
        "may_promote_phase": False,
        "may_assert_novelty": False,
        "may_authorize_execution": False,
        "author_metadata_included": False,
        "reviewer": {
            "identity": "",
            "registry_id": "",
            "signing_key_id": "",
            "independence_basis": "",
            "conflicts_disclosure": "",
            "competence_basis": "",
        },
        "question_responses": [
            {
                "question_id": question_id,
                "question": question,
                "disposition": "UNANSWERED",
                "evidence_locations": [],
                "calculation_or_code_evidence": "",
                "consequence": "",
                "smallest_adequate_correction": "",
            }
            for question_id, question in QUESTIONS
        ],
        "artifact_dispositions": [
            {
                "path": item["path"],
                "revision": item["revision"],
                "sha256": item["sha256"],
                "disposition": "UNANSWERED",
                "verification_event_id": "",
                "corrections_required": [],
                "residual_uncertainty": "",
            }
            for item in artifacts
        ],
        "overall_disposition": "UNANSWERED",
        "reviewer_attestation": "",
        "signed_return": {"signature_path": "", "signature_sha256": ""},
        "validation_boundary": (
            "Structural validation does not verify signature authenticity, reviewer identity, "
            "scientific correctness, independence, provenance, or execution eligibility."
        ),
    }


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"completed return requires nonblank {label}")
    return value.strip()


def validate_completed_return(root: Path, response: dict[str, Any]) -> None:
    template = build_template(root)
    if response.get("schema_id") != template["schema_id"] or response.get("schema_version") != 1:
        raise ContractError("unsupported verifier return schema")
    if response.get("status") != "COMPLETED_FOR_STRUCTURAL_VALIDATION":
        raise ContractError("return status must be COMPLETED_FOR_STRUCTURAL_VALIDATION")
    for field in ("review_scope", "review_packet_path", "review_packet_sha256", "canonical_phase"):
        if response.get(field) != template[field]:
            raise ContractError(f"verifier return {field} does not match the current review packet")
    for field in ("may_promote_phase", "may_assert_novelty", "may_authorize_execution", "author_metadata_included"):
        if response.get(field) is not False:
            raise ContractError(f"verifier return must keep {field}=false")

    reviewer = response.get("reviewer")
    if not isinstance(reviewer, dict):
        raise ContractError("completed return requires reviewer identity fields")
    for field in ("identity", "registry_id", "signing_key_id", "independence_basis", "conflicts_disclosure", "competence_basis"):
        require_text(reviewer.get(field), f"reviewer.{field}")

    questions = response.get("question_responses")
    if not isinstance(questions, list) or len(questions) != len(QUESTIONS):
        raise ContractError("completed return must answer all twelve PC03 methods questions")
    expected_question_ids = [item[0] for item in QUESTIONS]
    actual_question_ids = [item.get("question_id") for item in questions if isinstance(item, dict)]
    if actual_question_ids != expected_question_ids:
        raise ContractError("question IDs or order do not match the current contract")
    for item in questions:
        if item.get("disposition") not in QUESTION_DISPOSITIONS:
            raise ContractError(f"question {item.get('question_id')} has an unanswered or invalid disposition")
        locations = item.get("evidence_locations")
        if not isinstance(locations, list) or not locations or not all(isinstance(value, str) and value.strip() for value in locations):
            raise ContractError(f"question {item.get('question_id')} requires direct evidence locations")
        require_text(
            item.get("calculation_or_code_evidence"),
            f"question {item.get('question_id')} calculation_or_code_evidence",
        )
        require_text(item.get("consequence"), f"question {item.get('question_id')} consequence")
        require_text(
            item.get("smallest_adequate_correction"),
            f"question {item.get('question_id')} smallest_adequate_correction",
        )

    artifacts = response.get("artifact_dispositions")
    expected_artifacts = template["artifact_dispositions"]
    if not isinstance(artifacts, list) or len(artifacts) != len(expected_artifacts):
        raise ContractError("completed return must include exactly fifteen artifact dispositions")
    for actual, expected in zip(artifacts, expected_artifacts, strict=True):
        if not isinstance(actual, dict):
            raise ContractError("artifact disposition must be an object")
        for field in ("path", "revision", "sha256"):
            if actual.get(field) != expected[field]:
                raise ContractError(f"artifact {field} drift for {expected['path']}")
        disposition = actual.get("disposition")
        if disposition not in ARTIFACT_DISPOSITIONS:
            raise ContractError(f"artifact disposition is invalid for {expected['path']}")
        if disposition == "VERIFIED":
            require_text(actual.get("verification_event_id"), f"verification event ID for {expected['path']}")
        corrections = actual.get("corrections_required")
        if not isinstance(corrections, list) or not all(isinstance(value, str) for value in corrections):
            raise ContractError(f"corrections_required must be a string list for {expected['path']}")
        require_text(actual.get("residual_uncertainty"), f"residual uncertainty for {expected['path']}")

    event_ids = [item.get("verification_event_id") for item in artifacts if item.get("disposition") == "VERIFIED"]
    if len(event_ids) != len(set(event_ids)):
        raise ContractError("verification event IDs must be unique")
    overall = response.get("overall_disposition")
    if overall not in OVERALL_DISPOSITIONS:
        raise ContractError("overall disposition must be ACCEPT_AS_DRAFT, REVISE, or STOP")
    if overall == "ACCEPT_AS_DRAFT" and any(item.get("disposition") != "VERIFIED" for item in artifacts):
        raise ContractError("ACCEPT_AS_DRAFT requires all fifteen artifacts marked VERIFIED in the return")
    require_text(response.get("reviewer_attestation"), "reviewer_attestation")
    signed = response.get("signed_return")
    if not isinstance(signed, dict):
        raise ContractError("completed return requires signed_return metadata")
    require_text(signed.get("signature_path"), "signed_return.signature_path")
    signature_sha = require_text(signed.get("signature_sha256"), "signed_return.signature_sha256")
    if not SHA256_RE.fullmatch(signature_sha):
        raise ContractError("signed_return.signature_sha256 must be a lowercase SHA-256 value")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--validate", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    try:
        if args.validate is not None:
            response = load_json(args.validate.resolve())
            validate_completed_return(root, response)
            print(
                "VALID STRUCTURE ONLY: return matches the current PC03 methods packet contract; "
                "this does not verify signature, identity, independence, scientific correctness, provenance, or execution eligibility."
            )
            return 0
        expected = canonical_bytes(build_template(root))
        path = root / TEMPLATE
        if args.check:
            if not path.is_file() or path.read_bytes() != expected:
                raise ContractError(f"PC03 verifier return template is stale: {path}")
            print(f"OK: PC03 verifier return template is current: {path}")
            return 0
        if not path.is_file() or path.read_bytes() != expected:
            atomic_write(path, expected)
        print(f"WROTE: PC03 verifier return template: {path}")
        return 0
    except (ContractError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
