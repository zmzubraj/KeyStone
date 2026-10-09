#!/usr/bin/env python3
"""Export and structurally validate the accountable-human INTAKE transfer authorization contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


TEMPLATE = Path("review-packets/KEYSTONE-MPP-F1-intake-transfer-authorization-template.json")
DRAFT = Path("review-packets/KEYSTONE-MPP-F1-intake-transfer-authorization-draft.json")
EXPECTED_STATE = {
    "status": "ACTIVE",
    "current_phase": "INTAKE",
    "novelty_status": "UNRESOLVED",
    "feasibility_decision": "UNASSESSED",
    "solution_viability_status": "ASSERTED_ONLY",
    "acceptance_readiness": "NOT_ASSESSABLE",
}
TRANSFER_ARTIFACTS = (
    Path("docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md"),
    Path("docs/23_INDEPENDENT_INTAKE_HUMAN_VERIFICATION_SOP_BN.md"),
    Path("docs/24_INVALID_AI_INTAKE_VERIFICATION_QUARANTINE.md"),
    Path("review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip"),
    Path("review-packets/KEYSTONE-MPP-F1-intake-verifier-return-template.json"),
)
DECISIONS = {"APPROVED_FOR_TRANSFER", "REVISE", "DENIED"}
POLICY_BASIS_VALUES = {"YES_MATCHES_CURRENT_CONFIRMATION", "CONTRADICTION_REPORTED"}


class ContractError(ValueError):
    """Raised when the contract is stale, incomplete, or structurally invalid."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ContractError(f"JSON root must be an object: {path}")
    return payload


def validate_state(state: dict[str, Any]) -> None:
    mismatches = [
        f"{key}={state.get(key)!r} expected={expected!r}"
        for key, expected in EXPECTED_STATE.items()
        if state.get(key) != expected
    ]
    if mismatches:
        raise ContractError(
            "INTAKE transfer authorization requires fail-closed canonical state: "
            + "; ".join(mismatches)
        )


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"completed authorization requires nonblank {label}")
    return value.strip()


def extract_accountable_human(root: Path) -> dict[str, str]:
    path = root / "research-case/00-governance/accountable-authority-confirmation.md"
    text = path.read_text(encoding="utf-8")
    identity = ""
    contact = ""
    for line in text.splitlines():
        if not identity and line.startswith("- Accountable author full name:"):
            identity = line.split(":", 1)[1].strip().strip("`")
        elif not contact and line.startswith("- Contact identity to use in paper metadata:"):
            contact = line.split(":", 1)[1].strip().strip("`")
    if not identity or not contact:
        raise ContractError("accountable authority confirmation lacks identity/contact lines required for draft generation")
    return {"identity": identity, "contact": contact}


def load_transfer_artifacts(root: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for path in TRANSFER_ARTIFACTS:
        full = root / path
        if not full.is_file():
            raise ContractError(f"required transfer artifact is missing: {path}")
        entries.append({"path": path.as_posix(), "sha256": sha256_bytes(full.read_bytes())})
    return entries


def build_template(root: Path) -> dict[str, Any]:
    state = load_json(root / "research-case/program-state.json")
    validate_state(state)
    authority_path = Path("research-case/00-governance/accountable-authority-confirmation.md")
    if not (root / authority_path).is_file():
        raise ContractError(f"authority confirmation is missing: {authority_path}")
    transfer_artifacts = load_transfer_artifacts(root)
    review_packet = next(item for item in transfer_artifacts if item["path"].endswith(".zip"))
    return {
        "schema_id": "KEYSTONE_INTAKE_TRANSFER_AUTHORIZATION",
        "schema_version": 1,
        "status": "UNCOMPLETED_TEMPLATE",
        "authorization_scope": "INTAKE_EXTERNAL_TRANSFER_ONLY",
        "canonical_phase": state["current_phase"],
        "canonical_acceptance_readiness": state["acceptance_readiness"],
        "authority_reference_path": authority_path.as_posix(),
        "review_packet_path": review_packet["path"],
        "review_packet_sha256": review_packet["sha256"],
        "allowed_transfer_artifacts": transfer_artifacts,
        "constraints": {
            "may_promote_phase": False,
            "may_assert_independent_verification": False,
            "may_authorize_execution": False,
            "may_freeze_author_metadata": False,
        },
        "accountable_human": {
            "identity": "",
            "contact": "",
            "policy_basis_confirmation": "UNANSWERED",
        },
        "named_reviewer": {
            "identity": "",
            "affiliation_or_role": "",
            "contact": "",
            "independence_basis": "",
            "conflicts_disclosure": "",
        },
        "transfer_channel": {
            "channel_type": "",
            "destination": "",
            "confidentiality_boundary": "",
            "institutional_policy_notes": "",
        },
        "authorization_id": "",
        "authorization_decision": "UNANSWERED",
        "decision_rationale": "",
        "authorization_attestation": "",
        "validation_boundary": (
            "Structural validation does not verify the accountable human identity, institutional "
            "authority, reviewer independence, transmission security, recipient identity, or "
            "scientific correctness. It only checks that the approval stays bound to the current "
            "INTAKE packet scope and non-promotion limits."
        ),
    }


def build_draft(root: Path) -> dict[str, Any]:
    template = build_template(root)
    accountable = extract_accountable_human(root)
    return {
        **template,
        "status": "DRAFT_PENDING_ACCOUNTABLE_HUMAN",
        "accountable_human": {
            "identity": accountable["identity"],
            "contact": accountable["contact"],
            "policy_basis_confirmation": "YES_MATCHES_CURRENT_CONFIRMATION",
        },
        "named_reviewer": {
            "identity": "",
            "affiliation_or_role": "",
            "contact": "",
            "independence_basis": "",
            "conflicts_disclosure": "",
        },
        "transfer_channel": {
            "channel_type": "",
            "destination": "",
            "confidentiality_boundary": "",
            "institutional_policy_notes": "",
        },
        "authorization_id": "REM001-TRANSFER-APPROVAL-DRAFT",
        "authorization_decision": "UNANSWERED",
        "decision_rationale": "",
        "authorization_attestation": (
            "Draft only. This file is not approval until the accountable human completes the "
            "named reviewer, transfer channel, confidentiality boundary, and final decision."
        ),
        "draft_instructions": [
            "Confirm the current packet, return-template, and transfer-template hashes before approval.",
            "Fill the named reviewer identity, role, contact, independence basis, and conflicts disclosure.",
            "Fill the exact transfer channel, destination, and confidentiality boundary for this packet.",
            "Set authorization_decision to APPROVED_FOR_TRANSFER, REVISE, or DENIED.",
            "Save the completed file outside this draft path before structural validation.",
        ],
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


def validate_completed_authorization(root: Path, response: dict[str, Any]) -> None:
    template = build_template(root)
    if response.get("schema_id") != template["schema_id"] or response.get("schema_version") != 1:
        raise ContractError("unsupported transfer authorization schema")
    if response.get("status") != "COMPLETED_FOR_STRUCTURAL_VALIDATION":
        raise ContractError("authorization status must be COMPLETED_FOR_STRUCTURAL_VALIDATION")
    for field in (
        "authorization_scope",
        "canonical_phase",
        "canonical_acceptance_readiness",
        "authority_reference_path",
        "review_packet_path",
        "review_packet_sha256",
    ):
        if response.get(field) != template[field]:
            raise ContractError(f"authorization field drift: {field}")
    if response.get("allowed_transfer_artifacts") != template["allowed_transfer_artifacts"]:
        raise ContractError("allowed transfer artifacts do not match the current packet scope")

    constraints = response.get("constraints")
    if not isinstance(constraints, dict):
        raise ContractError("completed authorization requires constraints")
    for field in template["constraints"]:
        if constraints.get(field) is not False:
            raise ContractError(f"authorization must keep constraints.{field}=false")

    accountable = response.get("accountable_human")
    if not isinstance(accountable, dict):
        raise ContractError("completed authorization requires accountable_human fields")
    accountable_identity = require_text(accountable.get("identity"), "accountable_human.identity")
    require_text(accountable.get("contact"), "accountable_human.contact")
    policy_basis = require_text(
        accountable.get("policy_basis_confirmation"),
        "accountable_human.policy_basis_confirmation",
    )
    if policy_basis not in POLICY_BASIS_VALUES:
        raise ContractError("policy basis confirmation is invalid")

    decision = response.get("authorization_decision")
    if decision not in DECISIONS:
        raise ContractError("authorization_decision must be APPROVED_FOR_TRANSFER, REVISE, or DENIED")
    authorization_id = require_text(response.get("authorization_id"), "authorization_id")
    if " " in authorization_id:
        raise ContractError("authorization_id must not contain spaces")
    require_text(response.get("decision_rationale"), "decision_rationale")
    require_text(response.get("authorization_attestation"), "authorization_attestation")

    reviewer = response.get("named_reviewer")
    if not isinstance(reviewer, dict):
        raise ContractError("completed authorization requires named_reviewer fields")
    channel = response.get("transfer_channel")
    if not isinstance(channel, dict):
        raise ContractError("completed authorization requires transfer_channel fields")

    if decision == "APPROVED_FOR_TRANSFER":
        reviewer_identity = require_text(reviewer.get("identity"), "named_reviewer.identity")
        require_text(reviewer.get("affiliation_or_role"), "named_reviewer.affiliation_or_role")
        require_text(reviewer.get("contact"), "named_reviewer.contact")
        require_text(reviewer.get("independence_basis"), "named_reviewer.independence_basis")
        require_text(reviewer.get("conflicts_disclosure"), "named_reviewer.conflicts_disclosure")
        require_text(channel.get("channel_type"), "transfer_channel.channel_type")
        require_text(channel.get("destination"), "transfer_channel.destination")
        require_text(channel.get("confidentiality_boundary"), "transfer_channel.confidentiality_boundary")
        if reviewer_identity == accountable_identity:
            raise ContractError("named reviewer must not be the same as the accountable human approver")
        if policy_basis != "YES_MATCHES_CURRENT_CONFIRMATION":
            raise ContractError("approved transfer requires the current policy basis confirmation")


def validate_draft(root: Path, response: dict[str, Any]) -> None:
    expected = build_draft(root)
    if response != expected:
        raise ContractError(f"INTAKE transfer authorization draft is stale: {root / DRAFT}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("--check-draft", action="store_true")
    parser.add_argument("--validate", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    try:
        if args.validate is not None:
            response = load_json(args.validate.resolve())
            validate_completed_authorization(root, response)
            print(
                "VALID STRUCTURE ONLY: transfer authorization matches the current INTAKE packet scope; "
                "this does not verify human identity, institutional authority, transmission security, "
                "recipient identity, reviewer independence, or scientific correctness."
            )
            return 0
        if args.check_draft:
            expected = canonical_bytes(build_draft(root))
            path = root / DRAFT
            if not path.is_file() or path.read_bytes() != expected:
                raise ContractError(f"INTAKE transfer authorization draft is stale: {path}")
            print(f"OK: INTAKE transfer authorization draft is current: {root / DRAFT}")
            return 0
        if args.draft:
            expected = canonical_bytes(build_draft(root))
            path = root / DRAFT
            if not path.is_file() or path.read_bytes() != expected:
                atomic_write(path, expected)
            print(f"WROTE: INTAKE transfer authorization draft: {path}")
            return 0
        expected = canonical_bytes(build_template(root))
        path = root / TEMPLATE
        if args.check:
            if not path.is_file() or path.read_bytes() != expected:
                raise ContractError(f"INTAKE transfer authorization template is stale: {path}")
            print(f"OK: INTAKE transfer authorization template is current: {path}")
            return 0
        if not path.is_file() or path.read_bytes() != expected:
            atomic_write(path, expected)
        print(f"WROTE: INTAKE transfer authorization template: {path}")
        return 0
    except (ContractError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
