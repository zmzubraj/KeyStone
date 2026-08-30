#!/usr/bin/env python3
"""Export and structurally validate the fail-closed PC02 novelty verifier return contract."""

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


TEMPLATE = Path("review-packets/KEYSTONE-MPP-F1-pc02-novelty-verifier-return-template.json")
BUNDLE = Path("review-packets/KEYSTONE-MPP-F1-pc02-novelty-review-packet.zip")
ARTIFACTS = (
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
QUESTIONS = (
    (
        "PC02-Q01",
        "Is the ciphertext-availability versus dispute-key-serviceability distinction materially explicit in a stronger predecessor?",
    ),
    (
        "PC02-Q02",
        "Does a predecessor already combine a pre-authorization non-production partial-decryption readiness drill with a present-serviceability estimand?",
    ),
    (
        "PC02-Q03",
        "Does prior work already provide equivalent catastrophic false-accept analysis tied to that drill?",
    ),
    (
        "PC02-Q04",
        "Does prior work already tie correlation-aware or failure-domain sampling to the same readiness decision?",
    ),
    (
        "PC02-Q05",
        "Is the surviving contribution best disposed as NOVELTY_SURVIVES, REFRAME, or STOP?",
    ),
)
EXPECTED_STATE = {
    "status": "ACTIVE",
    "current_phase": "INTAKE",
    "novelty_status": "UNRESOLVED",
    "feasibility_decision": "UNASSESSED",
    "solution_viability_status": "ASSERTED_ONLY",
    "acceptance_readiness": "NOT_ASSESSABLE",
}
QUESTION_DISPOSITIONS = {"VERIFIED", "REFUTED", "QUALIFIED", "UNKNOWN"}
ARTIFACT_DISPOSITIONS = {"VERIFIED", "QUALIFIED", "REFUTED", "UNKNOWN"}
OVERALL_DISPOSITIONS = {"NOVELTY_SURVIVES", "REFRAME", "STOP"}
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
            "PC02 return contract requires fail-closed canonical state: "
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
    for artifact_path in ARTIFACTS:
        registry_path = artifact_path.removeprefix("research-case/")
        row = by_path.get(registry_path)
        if row is None:
            raise ContractError(f"canonical PC02 artifact is missing from registry: {registry_path}")
        missing = [field for field in ("revision", "sha256", "updated_at") if not row.get(field)]
        if missing:
            raise ContractError(f"registry row {registry_path} is missing: {', '.join(missing)}")
        actual_path = root / artifact_path
        if not actual_path.is_file():
            raise ContractError(f"canonical PC02 artifact is missing: {artifact_path}")
        actual_sha = sha256_bytes(actual_path.read_bytes())
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
    return output


def build_template(root: Path) -> dict[str, Any]:
    state = load_json(root / "research-case/program-state.json")
    validate_state(state)
    bundle = root / BUNDLE
    if not bundle.is_file():
        raise ContractError(f"PC02 review packet is missing: {bundle}")
    artifacts = registry_artifacts(root)
    return {
        "schema_id": "KEYSTONE_PC02_NOVELTY_VERIFIER_RETURN",
        "schema_version": 1,
        "status": "UNCOMPLETED_TEMPLATE",
        "review_scope": "PC02_NOVELTY_ONLY",
        "review_packet_path": BUNDLE.as_posix(),
        "review_packet_sha256": sha256_bytes(bundle.read_bytes()),
        "contract_timestamp": max(item["updated_at"] for item in artifacts),
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
                "strongest_predecessor": "",
                "decisive_overlap_or_differentiator": "",
                "access_limitations": "",
                "rationale": "",
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
            "scientific correctness, independence, provenance, or novelty disposition eligibility."
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
        raise ContractError("completed return must answer all five PC02 novelty questions")
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
        require_text(item.get("strongest_predecessor"), f"question {item.get('question_id')} strongest_predecessor")
        require_text(
            item.get("decisive_overlap_or_differentiator"),
            f"question {item.get('question_id')} decisive_overlap_or_differentiator",
        )
        require_text(item.get("access_limitations"), f"question {item.get('question_id')} access_limitations")
        require_text(item.get("rationale"), f"question {item.get('question_id')} rationale")

    artifacts = response.get("artifact_dispositions")
    expected_artifacts = template["artifact_dispositions"]
    if not isinstance(artifacts, list) or len(artifacts) != len(expected_artifacts):
        raise ContractError("completed return must include exactly ten artifact dispositions")
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
        raise ContractError("overall disposition must be NOVELTY_SURVIVES, REFRAME, or STOP")
    if overall == "NOVELTY_SURVIVES" and any(item.get("disposition") != "VERIFIED" for item in artifacts):
        raise ContractError("NOVELTY_SURVIVES requires all ten artifacts marked VERIFIED in the return")
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
                "VALID STRUCTURE ONLY: return matches the current PC02 novelty packet contract; "
                "this does not verify signature, identity, independence, scientific correctness, provenance, or novelty disposition eligibility."
            )
            return 0
        expected = canonical_bytes(build_template(root))
        path = root / TEMPLATE
        if args.check:
            if not path.is_file() or path.read_bytes() != expected:
                raise ContractError(f"PC02 verifier return template is stale: {path}")
            print(f"OK: PC02 verifier return template is current: {path}")
            return 0
        if not path.is_file() or path.read_bytes() != expected:
            atomic_write(path, expected)
        print(f"WROTE: PC02 verifier return template: {path}")
        return 0
    except (ContractError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
