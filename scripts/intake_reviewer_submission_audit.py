#!/usr/bin/env python3
"""Audit an INTAKE reviewer submission without promoting any research gate."""

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

from intake_verifier_return_contract import ContractError, load_json, validate_completed_return


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
CASE_RELATIVE = Path("research-case")
RETURN_RELATIVE = Path(
    "review-packets/reviewer-submissions/"
    "KEYSTONE-MPP-F1-intake-verifier-return-completed.json"
)
ATTESTATION_RELATIVE = Path(
    "review-packets/reviewer-submissions/"
    "KEYSTONE-MPP-F1-intake-reviewer-attestation.txt"
)
SIGNATURE_RELATIVE = Path(f"{ATTESTATION_RELATIVE.as_posix()}.sig")
REPORT_RELATIVE = Path(
    "review-packets/reviewer-submissions/"
    "KEYSTONE-MPP-F1-intake-reviewer-submission-audit.json"
)
SIGN_NAMESPACE = "keystone-mpp-f1-intake"
CHECK_NAMES = (
    "signed_verifier_registry",
    "completed_return_structure",
    "registered_reviewer_binding",
    "attestation_present",
    "attestation_contract_binding",
    "detached_signature_present",
    "detached_signature_hash",
    "detached_signature_valid",
    "canonical_verification_events",
)


class AuditError(RuntimeError):
    """Raised for an audit-input or deterministic-output failure."""


def _skill_scripts_path() -> Path:
    return Path.home() / ".codex/skills/orchestrate-top-journal-research/scripts"


def _load_signing_helpers() -> tuple[Any, Any, Any, Any]:
    skill_scripts = _skill_scripts_path()
    if not skill_scripts.is_dir():
        raise AuditError(f"research orchestration signing helpers are missing: {skill_scripts}")
    sys.path.insert(0, str(skill_scripts))
    try:
        from research_case_ledger_chain import read_chained_jsonl
        from research_case_signing import (
            load_verifier_registry,
            resolve_verifier_identity,
            verify_signature_with_registered_key,
        )
        from research_case_verification import verification_signature_valid
    except (ImportError, OSError) as exc:  # pragma: no cover - environment failure
        raise AuditError(f"cannot load research signing helpers: {exc}") from exc
    return (
        load_verifier_registry,
        resolve_verifier_identity,
        verify_signature_with_registered_key,
        (read_chained_jsonl, verification_signature_valid),
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _contains_false_binding(text: str, field: str) -> bool:
    return bool(
        re.search(
            rf"(?i)(?:\"?{re.escape(field)}\"?)\s*[:=]\s*(?:\"?false\"?)",
            text,
        )
    )


def attestation_binding_errors(text: str, response: dict[str, Any]) -> list[str]:
    """Return missing binding facts required in the signed companion attestation."""

    errors: list[str] = []
    reviewer = response.get("reviewer", {})
    for field in ("identity", "registry_id", "signing_key_id"):
        value = reviewer.get(field) if isinstance(reviewer, dict) else ""
        if not isinstance(value, str) or not value or value not in text:
            errors.append(f"attestation does not bind reviewer.{field}")
    packet_hash = response.get("review_packet_sha256")
    if not isinstance(packet_hash, str) or packet_hash not in text:
        errors.append("attestation does not bind review_packet_sha256")

    questions = response.get("question_responses", [])
    if isinstance(questions, list):
        for item in questions:
            if not isinstance(item, dict):
                continue
            question_id = str(item.get("question_id", ""))
            disposition = str(item.get("disposition", ""))
            if not question_id or not re.search(
                rf"(?m)^.*\b{re.escape(question_id)}\b.*\b{re.escape(disposition)}\b.*$",
                text,
            ):
                errors.append(f"attestation does not bind {question_id}={disposition}")

    artifacts = response.get("artifact_dispositions", [])
    if isinstance(artifacts, list):
        for item in artifacts:
            if not isinstance(item, dict):
                continue
            path = str(item.get("path", ""))
            required = (
                path,
                str(item.get("revision", "")),
                str(item.get("sha256", "")),
                str(item.get("disposition", "")),
                str(item.get("verification_event_id", "")),
            )
            for value in required:
                if not value or value not in text:
                    errors.append(f"attestation does not bind {path or 'artifact'} token {value or '<blank>'}")

    overall = response.get("overall_disposition")
    if not isinstance(overall, str) or overall not in text:
        errors.append("attestation does not bind overall_disposition")
    for field in (
        "may_promote_phase",
        "may_assert_novelty",
        "may_authorize_execution",
        "author_metadata_included",
    ):
        if response.get(field) is not False or not _contains_false_binding(text, field):
            errors.append(f"attestation does not bind {field}=false")
    attestation = response.get("reviewer_attestation")
    normalized_text = " ".join(text.split())
    normalized_attestation = " ".join(attestation.split()) if isinstance(attestation, str) else ""
    if not normalized_attestation or normalized_attestation not in normalized_text:
        errors.append("attestation does not reproduce reviewer_attestation")
    return errors


def _registry_binding(
    case: Path,
    response: dict[str, Any],
    registry: dict[str, Any],
    resolve_verifier_identity: Any,
) -> tuple[dict[str, Any] | None, str]:
    reviewer = response.get("reviewer")
    if not isinstance(reviewer, dict):
        return None, "completed return lacks reviewer object"
    identity = str(reviewer.get("identity", ""))
    registry_id = str(reviewer.get("registry_id", ""))
    key_id = str(reviewer.get("signing_key_id", ""))
    if not identity or not registry_id or not key_id:
        return None, "completed return lacks reviewer identity, registry ID, or key ID"
    entries = [
        entry
        for entry in registry.get("entries", [])
        if isinstance(entry, dict)
        and entry.get("active") is True
        and entry.get("verifier_type") == "INDEPENDENT_REVIEWER"
        and entry.get("registry_id") == registry_id
    ]
    if len(entries) != 1:
        return None, "reviewer registry_id does not identify one active independent reviewer"
    entry = entries[0]
    if entry.get("signing_key_id") != key_id:
        return None, "reviewer signing_key_id does not match the signed registry"
    try:
        # reviewer.identity may contain the human name; canonical verification
        # events use the run-scoped registry alias as their signing identity.
        resolved = resolve_verifier_identity(case, registry_id, "INDEPENDENT_REVIEWER")
    except (OSError, ValueError) as exc:
        return None, str(exc)
    if resolved != entry:
        return None, "registered reviewer public-key binding is inconsistent"
    if registry_id not in identity:
        return None, "reviewer.identity does not carry the registered run-scoped alias"
    return entry, "registered independent reviewer identity and key are bound"


def _canonical_events_check(
    root: Path,
    response: dict[str, Any],
    reviewer_entry: dict[str, Any],
    read_chained_jsonl: Any,
    verification_signature_valid: Any,
) -> tuple[bool, int, list[str]]:
    case = root / CASE_RELATIVE
    try:
        with (case / "artifact-registry.csv").open(encoding="utf-8", newline="") as handle:
            registry_rows = {row["path"]: row for row in csv.DictReader(handle)}
        events = read_chained_jsonl(case / "00-governance/verification-ledger.jsonl")
    except (OSError, ValueError, KeyError) as exc:
        return False, 0, [f"cannot read canonical verification state: {exc}"]
    reviewer = response.get("reviewer", {})
    matched = 0
    errors: list[str] = []
    for item in response.get("artifact_dispositions", []):
        if not isinstance(item, dict):
            continue
        relative = str(item.get("path", "")).removeprefix("research-case/")
        verification_id = str(item.get("verification_event_id", ""))
        row = registry_rows.get(relative)
        candidates = [
            event
            for event in events
            if event.get("artifact_path") == relative
            and event.get("artifact_sha256") == item.get("sha256")
            and event.get("verification_id") == verification_id
            and event.get("verifier_registry_id") == reviewer_entry.get("registry_id")
            and event.get("signing_key_id") == reviewer_entry.get("signing_key_id")
            and event.get("verifier_identity") == reviewer_entry.get("registry_id")
        ]
        valid_events = [event for event in candidates if verification_signature_valid(case, event)]
        row_ok = bool(
            row
            and row.get("status") == "VERIFIED"
            and row.get("sha256") == item.get("sha256")
            and row.get("verification_id") == verification_id
            and row.get("verifier_registry_id") == reviewer_entry.get("registry_id")
            and row.get("signing_key_id") == reviewer_entry.get("signing_key_id")
            and valid_events
        )
        if row_ok:
            matched += 1
        else:
            errors.append(f"canonical signed verification event is absent or invalid for {relative}")
    return matched == 4, matched, errors


def build_audit(root: Path) -> dict[str, Any]:
    root = root.resolve()
    case = root / CASE_RELATIVE
    return_path = root / RETURN_RELATIVE
    attestation_path = root / ATTESTATION_RELATIVE
    signature_path = root / SIGNATURE_RELATIVE
    checks = {name: "NOT_RUN" for name in CHECK_NAMES}
    details: dict[str, Any] = {
        "active_independent_reviewer_ids": [],
        "completed_return_error": "",
        "reviewer_binding_error": "",
        "attestation_binding_errors": [],
        "canonical_events_matched": 0,
        "required_signature_namespace": SIGN_NAMESPACE,
    }
    blockers: list[str] = []
    response: dict[str, Any] | None = None
    parsed_response: dict[str, Any] | None = None
    registry: dict[str, Any] | None = None
    reviewer_entry: dict[str, Any] | None = None

    try:
        (
            load_verifier_registry,
            resolve_verifier_identity,
            verify_signature_with_registered_key,
            ledger_helpers,
        ) = _load_signing_helpers()
        registry = load_verifier_registry(case)
        checks["signed_verifier_registry"] = "PASS"
        details["active_independent_reviewer_ids"] = sorted(
            str(entry.get("registry_id"))
            for entry in registry.get("entries", [])
            if isinstance(entry, dict)
            and entry.get("active") is True
            and entry.get("verifier_type") == "INDEPENDENT_REVIEWER"
        )
    except (AuditError, OSError, ValueError, json.JSONDecodeError) as exc:
        checks["signed_verifier_registry"] = "FAIL"
        blockers.append(f"signed verifier registry is invalid: {exc}")
        resolve_verifier_identity = verify_signature_with_registered_key = None
        ledger_helpers = (None, None)

    if return_path.is_file():
        try:
            parsed_response = load_json(return_path)
            validate_completed_return(root, parsed_response, allow_recorded_revision_drift=True)
            response = parsed_response
            checks["completed_return_structure"] = "PASS"
        except (ContractError, OSError, UnicodeError, json.JSONDecodeError) as exc:
            checks["completed_return_structure"] = "FAIL"
            details["completed_return_error"] = str(exc)
            blockers.append(f"completed return is not structurally valid: {exc}")
    else:
        checks["completed_return_structure"] = "FAIL"
        details["completed_return_error"] = f"missing {RETURN_RELATIVE.as_posix()}"
        blockers.append(details["completed_return_error"])

    if parsed_response is not None and registry is not None and resolve_verifier_identity is not None:
        reviewer_entry, message = _registry_binding(
            case, parsed_response, registry, resolve_verifier_identity
        )
        details["reviewer_binding_error"] = "" if reviewer_entry else message
        checks["registered_reviewer_binding"] = "PASS" if reviewer_entry else "FAIL"
        if reviewer_entry is None:
            blockers.append(f"reviewer is not bound to the signed registry: {message}")
    else:
        checks["registered_reviewer_binding"] = "FAIL"
        blockers.append("reviewer binding cannot be checked until the return and registry are valid")

    attestation_text = ""
    if attestation_path.is_file():
        try:
            attestation_text = attestation_path.read_text(encoding="utf-8")
            if not attestation_text.strip():
                raise AuditError("attestation is blank")
            checks["attestation_present"] = "PASS"
        except (OSError, UnicodeError, AuditError) as exc:
            checks["attestation_present"] = "FAIL"
            blockers.append(f"reviewer attestation is invalid: {exc}")
    else:
        checks["attestation_present"] = "FAIL"
        blockers.append(f"reviewer attestation is missing: {ATTESTATION_RELATIVE.as_posix()}")

    if parsed_response is not None and attestation_text:
        binding_errors = attestation_binding_errors(attestation_text, parsed_response)
        details["attestation_binding_errors"] = binding_errors
        checks["attestation_contract_binding"] = "PASS" if not binding_errors else "FAIL"
        blockers.extend(binding_errors)
    else:
        checks["attestation_contract_binding"] = "FAIL"
        blockers.append("attestation contract binding cannot pass without a valid return and attestation")

    if signature_path.is_file():
        checks["detached_signature_present"] = "PASS"
    else:
        checks["detached_signature_present"] = "FAIL"
        blockers.append(f"detached signature is missing: {SIGNATURE_RELATIVE.as_posix()}")

    declared_signature_hash = ""
    if parsed_response is not None and isinstance(parsed_response.get("signed_return"), dict):
        declared_signature_hash = str(parsed_response["signed_return"].get("signature_sha256", ""))
    if checks["detached_signature_present"] == "PASS" and declared_signature_hash:
        actual_signature_hash = sha256_file(signature_path)
        details["detached_signature_sha256"] = actual_signature_hash
        checks["detached_signature_hash"] = (
            "PASS" if actual_signature_hash == declared_signature_hash else "FAIL"
        )
        if checks["detached_signature_hash"] == "FAIL":
            blockers.append("detached signature SHA-256 does not match the completed return")
    else:
        checks["detached_signature_hash"] = "FAIL"
        blockers.append("detached signature hash cannot pass without both signature and declared hash")

    signature_valid = False
    if (
        reviewer_entry is not None
        and attestation_text
        and signature_path.is_file()
        and verify_signature_with_registered_key is not None
    ):
        try:
            signature = signature_path.read_text(encoding="utf-8")
            key_id = str(reviewer_entry.get("signing_key_id", ""))
            identity = str(parsed_response.get("reviewer", {}).get("identity", "")) if parsed_response else ""
            principals = [value for value in (key_id, identity) if value]
            signature_valid = any(
                verify_signature_with_registered_key(
                    case,
                    principal=principal,
                    namespace=SIGN_NAMESPACE,
                    text=attestation_text,
                    signature=signature,
                    key_id=key_id,
                )
                for principal in principals
            )
        except (OSError, UnicodeError, ValueError):
            signature_valid = False
    checks["detached_signature_valid"] = "PASS" if signature_valid else "FAIL"
    if not signature_valid:
        blockers.append("detached signature is not valid under the registered reviewer key and namespace")

    if (
        response is not None
        and checks["completed_return_structure"] == "PASS"
        and reviewer_entry is not None
        and ledger_helpers[0] is not None
    ):
        events_ok, matched, event_errors = _canonical_events_check(
            root,
            response,
            reviewer_entry,
            ledger_helpers[0],
            ledger_helpers[1],
        )
        details["canonical_events_matched"] = matched
        checks["canonical_verification_events"] = "PASS" if events_ok else "FAIL"
        blockers.extend(event_errors)
    else:
        checks["canonical_verification_events"] = "FAIL"
        blockers.append("four canonical signed verification events cannot be checked yet")

    complete = all(checks[name] == "PASS" for name in CHECK_NAMES)
    return {
        "schema_id": "KEYSTONE_INTAKE_REVIEWER_SUBMISSION_AUDIT",
        "schema_version": 1,
        "system_id": "KEYSTONE-MPP-F1",
        "canonical_phase": "INTAKE",
        "review_scope": "INTAKE_ONLY",
        "overall_status": (
            "AUTHENTICATED_RETURN_AND_CANONICAL_EVENTS_PRESENT" if complete else "INCOMPLETE"
        ),
        "may_promote_phase": False,
        "may_assert_novelty": False,
        "may_authorize_execution": False,
        "source_paths": {
            "completed_return": RETURN_RELATIVE.as_posix(),
            "attestation": ATTESTATION_RELATIVE.as_posix(),
            "detached_signature": SIGNATURE_RELATIVE.as_posix(),
        },
        "checks": checks,
        "details": details,
        "blocking_reasons": sorted(set(blockers)),
        "validation_boundary": (
            "A complete audit proves only packet-bound structure, registered-key signature, "
            "attestation binding, and presence of four canonical signed INTAKE events. It does "
            "not independently establish the reviewer's real-world identity, competence, "
            "scientific correctness, novelty, feasibility, execution authority, or phase eligibility."
        ),
    }


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    try:
        payload = build_audit(root)
        expected = canonical_bytes(payload)
        report = root / REPORT_RELATIVE
        if args.check:
            if not report.is_file() or report.read_bytes() != expected:
                raise AuditError(f"INTAKE reviewer submission audit is stale: {report}")
            print(f"OK: INTAKE reviewer submission audit is current: {report}")
        else:
            atomic_write(report, expected)
            print(f"WROTE: INTAKE reviewer submission audit: {report}")
        if args.require_complete and payload["overall_status"] != "AUTHENTICATED_RETURN_AND_CANONICAL_EVENTS_PRESENT":
            print("INCOMPLETE: authenticated reviewer return and canonical events are not complete", file=sys.stderr)
            return 1
        return 0
    except (AuditError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
