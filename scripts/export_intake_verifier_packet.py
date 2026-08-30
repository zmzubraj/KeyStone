#!/usr/bin/env python3
"""Render and validate the generated snapshot in the INTAKE verifier handoff."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


BEGIN_MARKER = "<!-- BEGIN GENERATED INTAKE SNAPSHOT -->"
END_MARKER = "<!-- END GENERATED INTAKE SNAPSHOT -->"

REQUIRED_ARTIFACTS = (
    "00-governance/intake-original.md",
    "00-governance/intake.json",
    "00-governance/program-charter.md",
    "00-governance/study-profile.json",
)

EXPECTED_STATE = {
    "status": "ACTIVE",
    "current_phase": "INTAKE",
    "novelty_status": "UNRESOLVED",
    "feasibility_decision": "UNASSESSED",
    "solution_viability_status": "ASSERTED_ONLY",
    "acceptance_readiness": "NOT_ASSESSABLE",
}


class PacketError(ValueError):
    """Raised when packet inputs fail the fail-closed contract."""


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PacketError(f"cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PacketError(f"JSON root must be an object: {path}")
    return payload


def load_registry(path: Path) -> dict[str, dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or "path" not in reader.fieldnames:
                raise PacketError("artifact registry is missing its path column")
            rows: dict[str, dict[str, str]] = {}
            for line_number, row in enumerate(reader, start=2):
                if None in row:
                    raise PacketError(
                        f"malformed artifact registry: extra column at line {line_number}"
                    )
                artifact_path = row.get("path", "")
                if not artifact_path:
                    raise PacketError(
                        f"malformed artifact registry: empty path at line {line_number}"
                    )
                if artifact_path in rows:
                    raise PacketError(
                        f"malformed artifact registry: duplicate path {artifact_path}"
                    )
                rows[artifact_path] = {key: value or "" for key, value in row.items()}
    except OSError as exc:
        raise PacketError(f"cannot read artifact registry {path}: {exc}") from exc
    return rows


def validate_required_rows(
    root: Path, registry: dict[str, dict[str, str]]
) -> list[dict[str, str]]:
    required_rows: list[dict[str, str]] = []
    for artifact_path in REQUIRED_ARTIFACTS:
        row = registry.get(artifact_path)
        if row is None:
            raise PacketError(f"required artifact registry row is missing: {artifact_path}")
        missing = [
            field
            for field in ("required", "status", "revision", "sha256", "updated_at")
            if not row.get(field)
        ]
        if missing:
            raise PacketError(
                f"required artifact row {artifact_path} is missing: {', '.join(missing)}"
            )
        if row["required"].lower() != "true":
            raise PacketError(f"INTAKE artifact is not marked required: {artifact_path}")
        file_path = root / "research-case" / artifact_path
        if not file_path.is_file():
            raise PacketError(f"required artifact file is missing: {file_path}")
        actual_hash = sha256_hex(file_path)
        if actual_hash != row["sha256"]:
            raise PacketError(
                f"SHA-256 mismatch for {artifact_path}: registry={row['sha256']} actual={actual_hash}"
            )
        required_rows.append(row)
    return required_rows


def validate_state(state: dict[str, Any]) -> None:
    mismatches = [
        f"{field}={state.get(field)!r} (expected {expected!r})"
        for field, expected in EXPECTED_STATE.items()
        if state.get(field) != expected
    ]
    if mismatches:
        raise PacketError(
            "unsupported scientific state for an INTAKE verifier packet: "
            + "; ".join(mismatches)
        )


def independent_reviewer_ids(verifier_registry: dict[str, Any]) -> set[str]:
    entries = verifier_registry.get("entries")
    if not isinstance(entries, list):
        raise PacketError("verifier registry entries must be a list")
    result: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise PacketError("verifier registry entry must be an object")
        if entry.get("active") is not False and entry.get("verifier_type") == "INDEPENDENT_REVIEWER":
            registry_id = entry.get("registry_id")
            if isinstance(registry_id, str) and registry_id:
                result.add(registry_id)
    return result


def independent_event_count(ledger_path: Path, reviewer_ids: set[str]) -> int:
    count = 0
    try:
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise PacketError(f"cannot read verification ledger {ledger_path}: {exc}") from exc
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise PacketError(
                f"verification ledger contains malformed JSON at line {line_number}"
            ) from exc
        if not isinstance(payload, dict):
            raise PacketError(
                f"verification ledger event at line {line_number} must be an object"
            )
        event = payload.get("verification_event", payload)
        if not isinstance(event, dict):
            raise PacketError(
                f"verification_event at line {line_number} must be an object"
            )
        artifact = event.get("artifact_path") or event.get("path")
        artifact = str(artifact).removeprefix("research-case/") if artifact else ""
        verifier_registry_id = event.get("verifier_registry_id")
        is_independent = (
            event.get("independence_mode") == "INDEPENDENT"
            and isinstance(verifier_registry_id, str)
            and verifier_registry_id in reviewer_ids
        )
        if artifact in REQUIRED_ARTIFACTS and is_independent:
            count += 1
    return count


def render_snapshot(
    rows: list[dict[str, str]],
    state: dict[str, Any],
    verifier_registry: dict[str, Any],
    reviewer_count: int,
    event_count: int,
) -> str:
    snapshot_at = max(row["updated_at"] for row in rows)
    lines = [
        "",
        "## Current artifact snapshot",
        "",
        "This generated snapshot is derived from canonical registry and governance inputs.",
        f"Snapshot source timestamp: `{snapshot_at}` (latest required artifact `updated_at`; no wall-clock value).",
        "",
        f"- Current status: `{state['status']}`",
        f"- Current phase: `{state['current_phase']}`",
        f"- Novelty status: `{state['novelty_status']}`",
        f"- Feasibility decision: `{state['feasibility_decision']}`",
        f"- Solution viability: `{state['solution_viability_status']}`",
        f"- Acceptance readiness: `{state['acceptance_readiness']}`",
        f"- Verifier trust mode: `{verifier_registry.get('trust_mode', '')}`",
        f"- Active independent reviewers: `{reviewer_count}`",
        f"- Independent verification events for these four artifacts: `{event_count}`",
        "",
        "| Path | Required | Status | Revision | SHA-256 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| `research-case/{path}` | `{required}` | `{status}` | `{revision}` | `{sha256}` |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "Any content or registry change invalidates this snapshot until the exporter is rerun.",
            "This snapshot is operational metadata, not independent scientific verification.",
            "",
        ]
    )
    return "\n".join(lines)


def split_document(text: str) -> tuple[str, str, str]:
    if text.count(BEGIN_MARKER) != 1 or text.count(END_MARKER) != 1:
        raise PacketError("document must contain exactly one generated snapshot marker pair")
    begin = text.index(BEGIN_MARKER)
    end = text.index(END_MARKER)
    if end <= begin:
        raise PacketError("generated snapshot markers are out of order")
    prefix = text[: begin + len(BEGIN_MARKER)]
    existing = text[begin + len(BEGIN_MARKER) : end]
    suffix = text[end:]
    return prefix, existing, suffix


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def build_expected_document(root: Path) -> tuple[Path, str, str]:
    registry = load_registry(root / "research-case/artifact-registry.csv")
    rows = validate_required_rows(root, registry)
    state = load_json(root / "research-case/program-state.json")
    validate_state(state)
    verifier_registry = load_json(
        root / "research-case/00-governance/verifier-registry.json"
    )
    reviewers = independent_reviewer_ids(verifier_registry)
    events = independent_event_count(
        root / "research-case/00-governance/verification-ledger.jsonl", reviewers
    )
    document_path = root / "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md"
    try:
        current = document_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PacketError(f"cannot read handoff document {document_path}: {exc}") from exc
    prefix, _, suffix = split_document(current)
    section = render_snapshot(rows, state, verifier_registry, len(reviewers), events)
    return document_path, current, prefix + section + suffix


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        document_path, current, expected = build_expected_document(args.root.resolve())
        if args.check:
            if current != expected:
                raise PacketError(
                    "generated INTAKE snapshot is stale; rerun export_intake_verifier_packet.py"
                )
            print(f"OK: INTAKE verifier packet is current: {document_path}")
            return 0
        if current != expected:
            atomic_write(document_path, expected)
        print(f"WROTE: INTAKE verifier packet snapshot: {document_path}")
        return 0
    except PacketError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
