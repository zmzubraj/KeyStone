#!/usr/bin/env python3
"""Export a deterministic, fail-closed PC02 novelty-review handoff."""

from __future__ import annotations

import argparse
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


DOCUMENT = Path("docs/21_PC02_NOVELTY_VERIFIER_HANDOFF.md")
BUNDLE = Path("review-packets/KEYSTONE-MPP-F1-pc02-novelty-review-packet.zip")
SIDECAR = Path(f"{BUNDLE}.sha256")

NOVELTY_PATHS = (
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

ARCHIVE_PATHS = ("README.md", "bundle-manifest.json", DOCUMENT.as_posix(), *NOVELTY_PATHS)

EXPECTED_STATE = {
    "status": "ACTIVE",
    "current_phase": "INTAKE",
    "novelty_status": "UNRESOLVED",
    "feasibility_decision": "UNASSESSED",
    "solution_viability_status": "ASSERTED_ONLY",
    "acceptance_readiness": "NOT_ASSESSABLE",
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
            "PC02 packet is defined only for the fail-closed INTAKE state: "
            + "; ".join(mismatches)
        )


def validate_rows(root: Path) -> list[dict[str, str]]:
    registry = load_registry(root / "research-case/artifact-registry.csv")
    rows: list[dict[str, str]] = []
    for archive_path in NOVELTY_PATHS:
        relative = archive_path.removeprefix("research-case/")
        row = registry.get(relative)
        if row is None:
            raise PacketError(f"required novelty registry row is missing: {relative}")
        if row.get("required", "").lower() != "true":
            raise PacketError(f"novelty artifact is not required: {relative}")
        missing = [field for field in ("status", "revision", "sha256", "updated_at") if not row.get(field)]
        if missing:
            raise PacketError(f"novelty registry row {relative} is missing: {', '.join(missing)}")
        path = root / archive_path
        if not path.is_file():
            raise PacketError(f"required novelty artifact is missing: {archive_path}")
        actual = sha256_bytes(path.read_bytes())
        if actual != row["sha256"]:
            raise PacketError(
                f"SHA-256 mismatch for {archive_path}: registry={row['sha256']} actual={actual}"
            )
        rows.append(row)
    return rows


def independent_novelty_event_count(root: Path) -> int:
    verifier_registry = load_json(root / "research-case/00-governance/verifier-registry.json")
    entries = verifier_registry.get("entries", [])
    reviewer_ids = {
        entry.get("registry_id")
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("active") is not False
        and entry.get("verifier_type") == "INDEPENDENT_REVIEWER"
        and entry.get("registry_id")
    }
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
        artifact = str(event.get("artifact_path") or event.get("path") or "")
        artifact = artifact.removeprefix("research-case/")
        if (
            event.get("independence_mode") == "INDEPENDENT"
            and event.get("verifier_registry_id") in reviewer_ids
            and artifact in {path.removeprefix("research-case/") for path in NOVELTY_PATHS}
        ):
            count += 1
    return count


def render_document(
    rows: list[dict[str, str]], state: dict[str, Any], event_count: int
) -> str:
    lines = [
        "# KEYSTONE-MPP-F1 PC02 Novelty Verifier Handoff",
        "",
        "Status: `PREPARED_FOR_QUALIFIED_EXTERNAL_REVIEW`",
        "",
        "> Developmental reviewer handoff only. This packet does not certify novelty, authorize execution, promote the research phase, or substitute for a signed qualified verification event.",
        "",
        "## Frozen decision boundary",
        "",
        "The broad primitive-level novelty claim is rejected. Review only the bounded `REFRAME` candidate: KEYSTONE separates ciphertext availability from present dispute-key serviceability in an encrypted-rollup dispute workflow, and studies a pre-authorization, non-production canary partial-decryption readiness audit with explicit catastrophic false-accept and correlated-failure qualification.",
        "",
        "The reviewer must not upgrade this to a claim of a new threshold-encryption primitive, new DLEQ proof, proof of future cooperation, unconditional liveness accountability, field validation, or production readiness.",
        "",
        "Author metadata is deferred and intentionally excluded from this packet.",
        "",
        "## Canonical state",
        "",
        f"- status: `{state['status']}`",
        f"- phase: `{state['current_phase']}`",
        f"- novelty: `{state['novelty_status']}`",
        f"- feasibility: `{state['feasibility_decision']}`",
        f"- solution viability: `{state['solution_viability_status']}`",
        f"- acceptance readiness: `{state['acceptance_readiness']}`",
        f"- accepted independent novelty verification events: `{event_count}`",
        "",
        "## Required reviewer determinations",
        "",
        "For each claim axis, return `VERIFIED`, `REFUTED`, `QUALIFIED`, or `UNKNOWN`, with the exact artifact path, source identifier or URL, decisive overlap or differentiator, access limitation, and rationale:",
        "",
        "1. Is the ciphertext-availability versus dispute-key-serviceability distinction materially explicit in a stronger predecessor?",
        "2. Does a predecessor already combine a pre-authorization non-production partial-decryption readiness drill with a present-serviceability estimand?",
        "3. Does prior work already provide equivalent catastrophic false-accept analysis tied to that drill?",
        "4. Does prior work already tie correlation-aware or failure-domain sampling to the same readiness decision?",
        "5. Is the surviving contribution best disposed as `NOVELTY_SURVIVES`, `REFRAME`, or `STOP`?",
        "",
        "A zero-hit search is not novelty evidence. Proprietary or inaccessible sources must remain explicit residual uncertainty.",
        "",
        "## Transfer and disposition gate",
        "",
        "This packet must not be transferred until `REM-001` is actually recorded through the canonical independent-INTAKE workflow and the accountable human names the reviewer and disclosure boundary for this exact packet.",
        "",
        "Any acceptable outcome from this packet is capped at the bounded `REFRAME` lane unless the reviewer returns stronger, hash-bound defeating evidence against the current rejection of the broad primitive-level novelty claim.",
        "",
        "## Hash-bound evidence inventory",
        "",
        "| Artifact | Status | Revision | SHA-256 |",
        "| --- | --- | ---: | --- |",
    ]
    for archive_path, row in zip(NOVELTY_PATHS, rows, strict=True):
        lines.append(
            f"| `{archive_path}` | `{row['status']}` | `{row['revision']}` | `{row['sha256']}` |"
        )
    lines.extend(
        [
            "",
            "## Verification and return contract",
            "",
            "A decision-bearing return must identify the verifier registry ID and signing key ID, demonstrate independence from the producer roles, bind every determination to the exact artifact SHA-256 above, and be recorded through the canonical verification-event workflow. An unsigned email, AI review, aggregate score, or prose endorsement is developmental feedback only.",
            "",
            "Local packet generation does not authorize external transfer. The accountable human must approve any transfer to a named reviewer and confirm the disclosure boundary.",
            "",
        ]
    )
    return "\n".join(lines)


def render_readme(state: dict[str, Any], event_count: int, bundle_timestamp: str) -> str:
    return "\n".join(
        [
            "# KEYSTONE-MPP-F1 PC02 Novelty Review Bundle",
            "",
            "Developmental reviewer handoff only.",
            "This bundle does not certify novelty, authorize execution, promote the research phase, or authorize external transfer.",
            "Author metadata is deferred and excluded.",
            "Transfer prerequisite: `REM-001` recorded plus accountable-human authorization for the named reviewer and disclosure boundary.",
            "Disposition ceiling: bounded `REFRAME` candidate only; broad primitive-level novelty remains rejected unless independently overturned with hash-bound evidence.",
            f"Canonical phase: `{state['current_phase']}`",
            f"Canonical novelty status: `{state['novelty_status']}`",
            f"Accepted independent novelty verification events: `{event_count}`",
            f"Deterministic timestamp: `{bundle_timestamp}`",
            "",
        ]
    )


def validate_disclosure(payloads: dict[str, bytes]) -> None:
    for name, payload in payloads.items():
        if EMAIL_PATTERN.search(payload):
            raise PacketError(f"contact metadata is forbidden in PC02 bundle: {name}")
        if any(marker in payload for marker in PRIVATE_KEY_MARKERS):
            raise PacketError(f"private signing material is forbidden in PC02 bundle: {name}")


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
    rows = validate_rows(root)
    event_count = independent_novelty_event_count(root)
    timestamp = max(row["updated_at"] for row in rows)
    document = render_document(rows, state, event_count).encode("utf-8")
    readme = render_readme(state, event_count, timestamp).encode("utf-8")

    payloads: dict[str, bytes] = {
        "README.md": readme,
        "bundle-manifest.json": b"",
        DOCUMENT.as_posix(): document,
    }
    for name in NOVELTY_PATHS:
        payloads[name] = (root / name).read_bytes()

    source_files = []
    for name in ARCHIVE_PATHS:
        payload = payloads[name]
        source_files.append(
            {
                "archive_path": name,
                "source_path": name if name not in {"README.md", "bundle-manifest.json"} else None,
                "source_sha256": sha256_bytes(payload) if name != "bundle-manifest.json" else None,
                "archive_sha256": sha256_bytes(payload) if name != "bundle-manifest.json" else None,
            }
        )
    manifest = {
        "schema_id": "KEYSTONE_PC02_NOVELTY_REVIEW_BUNDLE",
        "schema_version": 1,
        "status": "PREPARED_FOR_QUALIFIED_EXTERNAL_REVIEW",
        "bundle_timestamp": timestamp,
        "canonical_phase": state["current_phase"],
        "novelty_status": state["novelty_status"],
        "may_assert_novelty": False,
        "broad_primitive_novelty_rejected": True,
        "surviving_disposition_ceiling": "REFRAME_ONLY",
        "transfer_prerequisite_remediation": "REM-001",
        "external_transfer_authorized": False,
        "author_metadata_included": False,
        "independent_novelty_verification_events": event_count,
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
                    raise PacketError(f"PC02 novelty packet mismatch or stale output: {path}")
            print(f"OK: PC02 novelty verifier packet is current: {root / BUNDLE}")
            return 0
        for path, payload in outputs.items():
            if not path.is_file() or path.read_bytes() != payload:
                atomic_write(path, payload)
        print(f"WROTE: PC02 novelty verifier packet: {root / BUNDLE}")
        return 0
    except (OSError, PacketError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
