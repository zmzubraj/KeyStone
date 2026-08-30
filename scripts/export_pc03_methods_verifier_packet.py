#!/usr/bin/env python3
"""Export a deterministic, fail-closed PC03 external methods-review handoff."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from export_intake_verifier_packet import PacketError, load_json, load_registry


DOCUMENT = Path("docs/22_PC03_METHODS_VERIFIER_HANDOFF.md")
BUNDLE = Path("review-packets/KEYSTONE-MPP-F1-pc03-methods-review-packet.zip")
SIDECAR = Path(f"{BUNDLE}.sha256")

DESIGN_PATHS = (
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
)
REGISTERED_PATHS = {
    "research-case/03-design/protocol.md": "03-design/protocol.md",
    "research-case/03-design/analysis-plan.md": "03-design/analysis-plan.md",
    "research-case/03-design/power-or-precision.md": "03-design/power-or-precision.md",
    "research-case/03-design/preregistration-and-deviations.md": "03-design/preregistration-and-deviations.md",
    "research-case/02-feasibility/pilot-plan.md": "02-feasibility/pilot-plan.md",
}
ARCHIVE_PATHS = ("README.md", "bundle-manifest.json", DOCUMENT.as_posix(), *DESIGN_PATHS)

EXPECTED_STATE = {
    "status": "ACTIVE",
    "current_phase": "INTAKE",
    "novelty_status": "UNRESOLVED",
    "feasibility_decision": "UNASSESSED",
    "solution_viability_status": "ASSERTED_ONLY",
    "acceptance_readiness": "NOT_ASSESSABLE",
}
INCLUDED = (
    "RID-C003-IID-001",
    "RID-C003-STRAT-001",
    "RID-C003-SW-001",
)
EXCLUDED = {
    "RID-C003-CORR-001": "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE",
    "RID-C003-DEADLINE-001": "EXCLUDED_PENDING_ENVIRONMENT_PROFILE",
}
EMAIL_PATTERN = re.compile(
    rb"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9.-])"
)
PRIVATE_KEY_MARKERS = (
    b"-----BEGIN OPENSSH PRIVATE KEY-----",
    b"-----BEGIN PRIVATE KEY-----",
    b"-----BEGIN RSA PRIVATE KEY-----",
    b"-----BEGIN EC PRIVATE KEY-----",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def validate_state(state: dict[str, Any]) -> None:
    mismatches = [
        f"{field}={state.get(field)!r} expected={expected!r}"
        for field, expected in EXPECTED_STATE.items()
        if state.get(field) != expected
    ]
    if mismatches:
        raise PacketError(
            "PC03 methods packet is defined only for the fail-closed INTAKE state: "
            + "; ".join(mismatches)
        )


def validate_inputs(root: Path) -> tuple[dict[str, dict[str, str]], dict[str, bytes]]:
    registry = load_registry(root / "research-case/artifact-registry.csv")
    rows: dict[str, dict[str, str]] = {}
    payloads: dict[str, bytes] = {}
    for archive_path in DESIGN_PATHS:
        path = root / archive_path
        if not path.is_file():
            raise PacketError(f"required PC03 review input is missing: {archive_path}")
        payload = path.read_bytes()
        payloads[archive_path] = payload
        registry_path = REGISTERED_PATHS.get(archive_path)
        if registry_path is None:
            continue
        row = registry.get(registry_path)
        if row is None:
            raise PacketError(f"required registry row is missing: {registry_path}")
        missing = [field for field in ("status", "revision", "sha256", "updated_at") if not row.get(field)]
        if missing:
            raise PacketError(f"registry row {registry_path} is missing: {', '.join(missing)}")
        actual = sha256_bytes(payload)
        if actual != row["sha256"]:
            raise PacketError(
                f"SHA-256 mismatch for {archive_path}: registry={row['sha256']} actual={actual}"
            )
        rows[archive_path] = row
    validate_disclosure(payloads)
    validate_frozen_design(payloads)
    return rows, payloads


def validate_frozen_design(payloads: dict[str, bytes]) -> None:
    amendment_path = "research-case/03-design/pc03-prospective-amendment.md"
    amendment = payloads[amendment_path].decode("utf-8")
    required_text = (
        "Author metadata remains deferred.",
        "independent synthetic scenario draws",
        "32 primary seed blocks",
        "73,778",
        "131,072",
        *EXCLUDED.values(),
    )
    for needle in required_text:
        if needle not in amendment:
            raise PacketError(f"PC03 amendment is missing frozen boundary text: {needle}")

    counts_path = "research-case/03-design/pc03-prospective-counts.csv"
    rows = list(csv.DictReader(io.StringIO(payloads[counts_path].decode("utf-8"))))
    by_result = {row.get("result_id", ""): row for row in rows}
    if len(by_result) != 5:
        raise PacketError("PC03 count contract must contain exactly five result-family rows")
    for result_id in INCLUDED:
        row = by_result.get(result_id)
        if row is None:
            raise PacketError(f"PC03 count contract is missing included result: {result_id}")
        expected = {
            "primary_seed_blocks_per_cell": "32",
            "reserve_seed_blocks_per_cell": "4",
            "draws_per_seed_block": "4096",
            "primary_draws_per_cell": "131072",
            "required_draws_per_cell": "73778",
            "execution_status": "BLOCKED_PENDING_GATE",
        }
        for field, wanted in expected.items():
            if row.get(field) != wanted:
                raise PacketError(f"PC03 count mismatch for {result_id} {field}: {row.get(field)!r}")
    for result_id, status in EXCLUDED.items():
        row = by_result.get(result_id)
        if row is None or row.get("execution_status") != status:
            raise PacketError(f"PC03 excluded-family boundary mismatch for {result_id}")

    seeds_path = "research-case/03-design/pc03-seed-schedule.csv"
    seeds = list(csv.DictReader(io.StringIO(payloads[seeds_path].decode("utf-8"))))
    if len(seeds) != 108:
        raise PacketError(f"PC03 seed schedule must contain 108 rows, got {len(seeds)}")
    seed_values = [row.get("seed", "") for row in seeds]
    if len(set(seed_values)) != len(seed_values) or any(not value for value in seed_values):
        raise PacketError("PC03 seed schedule contains blank or duplicate streams")
    for result_id in INCLUDED:
        result_rows = [row for row in seeds if row.get("result_id") == result_id]
        roles = [row.get("role") for row in result_rows]
        if len(result_rows) != 36 or roles.count("PRIMARY") != 32 or roles.count("RESERVE") != 4:
            raise PacketError(f"PC03 seed schedule role mismatch for {result_id}")


def independent_methods_event_count(root: Path) -> int:
    verifier_registry = load_json(root / "research-case/00-governance/verifier-registry.json")
    reviewer_ids = {
        entry.get("registry_id")
        for entry in verifier_registry.get("entries", [])
        if isinstance(entry, dict)
        and entry.get("active") is not False
        and entry.get("verifier_type") == "INDEPENDENT_REVIEWER"
        and entry.get("registry_id")
    }
    canonical_paths = set(REGISTERED_PATHS.values())
    count = 0
    ledger = root / "research-case/00-governance/verification-ledger.jsonl"
    for line_number, line in enumerate(ledger.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise PacketError(f"malformed verification event at line {line_number}") from exc
        event = payload.get("verification_event", payload)
        if not isinstance(event, dict):
            raise PacketError(f"verification event at line {line_number} is not an object")
        artifact = str(event.get("artifact_path") or event.get("path") or "").removeprefix(
            "research-case/"
        )
        if (
            event.get("independence_mode") == "INDEPENDENT"
            and event.get("verifier_registry_id") in reviewer_ids
            and artifact in canonical_paths
        ):
            count += 1
    return count


def render_document(
    rows: dict[str, dict[str, str]],
    payloads: dict[str, bytes],
    state: dict[str, Any],
    event_count: int,
) -> str:
    lines = [
        "# KEYSTONE-MPP-F1 PC03 Methods Verifier Handoff",
        "",
        "Status: `PREPARED_FOR_QUALIFIED_EXTERNAL_METHODS_REVIEW`",
        "",
        "> Developmental methods-review handoff only. This packet does not certify the design, authorize execution, promote the research phase, establish novelty, or substitute for an authenticated independently signed verification event.",
        "",
        "Author metadata is deferred and intentionally excluded from this packet.",
        "",
        "## Frozen review boundary",
        "",
        "Review the result-blind minimum synthetic design only. Independent synthetic scenario draws are the Monte Carlo sampling units for the frozen model-probability estimands; 32 primary seed blocks and four ordered reserve blocks are execution, dispersion, and reproducibility units. Each included cell schedules 131,072 primary draws against a distribution-free requirement of 73,778 draws.",
        "",
        "Included result IDs: `RID-C003-IID-001`, `RID-C003-STRAT-001`, and `RID-C003-SW-001`.",
        "",
        "Excluded boundaries:",
        "",
        "- `RID-C003-CORR-001`: `EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE`",
        "- `RID-C003-DEADLINE-001`: `EXCLUDED_PENDING_ENVIRONMENT_PROFILE`",
        "",
        "Existing exploratory outcomes may be inspected only for contamination and denominator-risk detection. They may not set, repair, or justify the prospective thresholds.",
        "",
        "## Canonical state",
        "",
        f"- status: `{state['status']}`",
        f"- phase: `{state['current_phase']}`",
        f"- novelty: `{state['novelty_status']}`",
        f"- feasibility: `{state['feasibility_decision']}`",
        f"- solution viability: `{state['solution_viability_status']}`",
        f"- acceptance readiness: `{state['acceptance_readiness']}`",
        f"- accepted independent methods verification events on canonical review paths: `{event_count}`",
        "",
        "## Required reviewer determinations",
        "",
        "Return `PASS`, `PARTIAL`, `FAIL`, or `UNKNOWN` for every item, with direct artifact locations, recomputation or code evidence, consequence, and the smallest adequate correction:",
        "",
        "1. Does the sampling-unit definition match the actual simulator semantics, without treating a seed-run aggregate as a Bernoulli observation?",
        "2. Are scenario draws independent under the frozen generator, and are blockwise estimates sufficient to expose implementation-level dependence or drift?",
        "3. For `RID-C003-STRAT-001`, does the implementation create true common-random-number matched policy pairs with identical latent scenarios and no unpaired substitution?",
        "4. For `RID-C003-SW-001`, are audit-pass and dispute-success outcomes evaluated within the same synthetic draw, with the signed gap direction fixed before execution?",
        "5. Recompute both Hoeffding requirements of 73,778 and confirm that 32 x 4,096 = 131,072 valid primary draws exceeds them under the stated bounded outcomes.",
        "6. Are all 108 seed-schedule rows unique and deterministic, with exactly 32 primary and four reserve streams for each included result ID?",
        "7. Does the reserve rule replace only documented infrastructure failures and prohibit replacement of valid unfavorable blocks?",
        "8. Is one primary cell per included family sufficient for the frozen minimum claim, with optional secondary tests correctly confined to Holm control?",
        "9. Are CORR and DEADLINE correctly excluded, and is every existing correlated/deadline display prevented from becoming confirmatory evidence?",
        "10. Are missingness, invalid-run, deviation, stopping, negative-result retention, and exploratory-quarantine rules complete and operationally testable?",
        "11. Could any existing exploratory value, figure, or code default have contaminated the chosen cells, precision targets, or decision rules?",
        "12. Does the pilot run contract reproduce the same included/excluded boundaries without introducing a stronger claim or execution authorization?",
        "",
        "Any critical `FAIL` or `UNKNOWN` leaves PC03 unverified and execution blocked. `PARTIAL` must identify the exact claim ceiling and remediation. No aggregate score or majority vote can compensate for a critical defect.",
        "",
        "## Transfer and execution gate",
        "",
        "This packet must not be transferred until `REM-001` is recorded through the canonical independent-INTAKE workflow, `REM-002` remains confined to the bounded novelty `REFRAME` lane, and the accountable human names the reviewer and disclosure boundary for this exact packet.",
        "",
        "A methods-review `ACCEPT_AS_DRAFT` disposition does not authorize confirmatory execution. `REM-003` closes only after the signed return is recorded and a separate accountable start decision preserves the same included and excluded result-family boundary.",
        "",
        "## Hash-bound review inventory",
        "",
        "| Artifact | Registry status | Revision | SHA-256 |",
        "| --- | --- | ---: | --- |",
    ]
    for archive_path in DESIGN_PATHS:
        row = rows.get(archive_path)
        status = row["status"] if row else "AUXILIARY_HASH_BOUND_INPUT"
        revision = row["revision"] if row else "N/A"
        lines.append(
            f"| `{archive_path}` | `{status}` | `{revision}` | `{sha256_bytes(payloads[archive_path])}` |"
        )
    lines.extend(
        [
            "",
            "## Required signed return",
            "",
            "A decision-bearing return must include reviewer identity, verifier registry ID, signing key ID, conflict disclosure, independence basis, competence basis in statistical simulation or experimental methods, every question disposition, reviewed path/revision/SHA-256, calculations or code evidence, residual risks, and one overall disposition: `ACCEPT_AS_DRAFT`, `REVISE`, or `STOP`.",
            "",
            "The reviewer must sign current canonical artifact revisions through the schema-v4 verifier workflow. A same-host AI review, unsigned email, prose endorsement, or possession of a public key is developmental evidence only. If upstream novelty or claim semantics later change, affected methods verification becomes stale and must be repeated.",
            "",
            "Local packet generation does not authorize external transfer. The accountable human must approve transfer to a named reviewer and confirm the disclosure boundary. Review acceptance does not authorize confirmatory execution; a separate accountable start decision remains mandatory.",
            "",
        ]
    )
    return "\n".join(lines)


def render_readme(state: dict[str, Any], event_count: int, timestamp: str) -> str:
    return "\n".join(
        [
            "# KEYSTONE-MPP-F1 PC03 Methods Review Bundle",
            "",
            "Developmental methods-review handoff only.",
            "This bundle does not certify methods, authorize execution or transfer, promote the phase, or establish novelty.",
            "Author metadata is deferred and excluded.",
            "Transfer prerequisites: `REM-001` recorded, bounded `REM-002` novelty lane preserved, and accountable-human authorization for the named reviewer and disclosure boundary.",
            "Execution prerequisite: a signed PC03 return plus a separate accountable start decision; methods review alone cannot authorize confirmatory execution.",
            f"Canonical phase: `{state['current_phase']}`",
            f"Accepted independent methods verification events: `{event_count}`",
            f"Deterministic timestamp: `{timestamp}`",
            "",
        ]
    )


def validate_disclosure(payloads: dict[str, bytes]) -> None:
    for name, payload in payloads.items():
        if EMAIL_PATTERN.search(payload):
            raise PacketError(f"contact metadata is forbidden in PC03 bundle: {name}")
        if any(marker in payload for marker in PRIVATE_KEY_MARKERS):
            raise PacketError(f"private signing material is forbidden in PC03 bundle: {name}")


def zip_datetime(timestamp: str) -> tuple[int, int, int, int, int, int]:
    try:
        parsed = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise PacketError(f"invalid registry timestamp: {timestamp}") from exc
    return (parsed.year, parsed.month, parsed.day, parsed.hour, parsed.minute, parsed.second)


def build_archive(payloads: dict[str, bytes], timestamp: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in ARCHIVE_PATHS:
            info = zipfile.ZipInfo(name, zip_datetime(timestamp))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, payloads[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return buffer.getvalue()


def build_outputs(root: Path) -> tuple[bytes, bytes, bytes]:
    state = load_json(root / "research-case/program-state.json")
    validate_state(state)
    rows, design_payloads = validate_inputs(root)
    event_count = independent_methods_event_count(root)
    timestamp = max(row["updated_at"] for row in rows.values())
    document = render_document(rows, design_payloads, state, event_count).encode("utf-8")
    readme = render_readme(state, event_count, timestamp).encode("utf-8")

    payloads: dict[str, bytes] = {
        "README.md": readme,
        "bundle-manifest.json": b"",
        DOCUMENT.as_posix(): document,
        **design_payloads,
    }
    source_files = []
    for name in ARCHIVE_PATHS:
        payload = payloads[name]
        digest = None if name == "bundle-manifest.json" else sha256_bytes(payload)
        source_files.append(
            {
                "archive_path": name,
                "source_path": name if name not in {"README.md", "bundle-manifest.json"} else None,
                "source_sha256": digest,
                "archive_sha256": digest,
            }
        )
    manifest = {
        "schema_id": "KEYSTONE_PC03_METHODS_REVIEW_BUNDLE",
        "schema_version": 1,
        "status": "PREPARED_FOR_QUALIFIED_EXTERNAL_METHODS_REVIEW",
        "bundle_timestamp": timestamp,
        "canonical_phase": state["current_phase"],
        "novelty_status": state["novelty_status"],
        "feasibility_decision": state["feasibility_decision"],
        "solution_viability_status": state["solution_viability_status"],
        "acceptance_readiness": state["acceptance_readiness"],
        "may_authorize_execution": False,
        "may_assert_methods_verified": False,
        "may_promote_phase": False,
        "transfer_prerequisite_remediations": ["REM-001", "REM-002"],
        "external_transfer_authorized": False,
        "execution_prerequisite_remediation": "REM-003",
        "separate_accountable_start_required": True,
        "author_metadata_included": False,
        "included_result_ids": list(INCLUDED),
        "excluded_result_ids": EXCLUDED,
        "independent_methods_verification_events": event_count,
        "source_files": source_files,
    }
    payloads["bundle-manifest.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    )
    validate_disclosure(payloads)
    archive = build_archive(payloads, timestamp)
    sidecar = f"{sha256_bytes(archive)}  ./{BUNDLE.as_posix()}\n".encode("utf-8")
    return document, archive, sidecar


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    try:
        document, archive, sidecar = build_outputs(root)
        outputs = {
            root / DOCUMENT: document,
            root / BUNDLE: archive,
            root / SIDECAR: sidecar,
        }
        if args.check:
            for path, expected in outputs.items():
                if not path.is_file() or path.read_bytes() != expected:
                    raise PacketError(f"PC03 methods packet mismatch or stale output: {path}")
            print(f"OK: PC03 methods verifier packet is current: {root / BUNDLE}")
            return 0
        for path, payload in outputs.items():
            if not path.is_file() or path.read_bytes() != payload:
                atomic_write(path, payload)
        print(f"WROTE: PC03 methods verifier packet: {root / BUNDLE}")
        return 0
    except (OSError, UnicodeError, PacketError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
