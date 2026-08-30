#!/usr/bin/env python3
"""Export the deterministic KEYSTONE INTAKE review bundle."""

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

from export_intake_verifier_packet import (
    PacketError,
    build_expected_document,
    independent_event_count,
    independent_reviewer_ids,
    load_json,
    load_registry,
    validate_required_rows,
)


BUNDLE_PATH = Path("review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip")
SIDECAR_PATH = Path("review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip.sha256")

READ_ONLY_ARCHIVE_PATHS = (
    "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md",
    "research-case/program-state.json",
    "research-case/00-governance/verifier-registry.json",
    "research-case/00-governance/verification-ledger.jsonl",
    "research-case/00-governance/intake-original.md",
    "research-case/00-governance/intake.json",
    "research-case/00-governance/program-charter.md",
    "research-case/00-governance/study-profile.json",
)

ARCHIVE_PATHS = (
    "README.md",
    "bundle-manifest.json",
    *READ_ONLY_ARCHIVE_PATHS,
)

MANIFEST_SCHEMA_ID = "KEYSTONE_INTAKE_REVIEW_BUNDLE"
MANIFEST_STATUS = "PREPARED_FOR_EXTERNAL_VERIFICATION"

EMAIL_PATTERN = re.compile(
    rb"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9.-])"
)
PRIVATE_KEY_MARKERS = (
    b"-----BEGIN OPENSSH PRIVATE KEY-----",
    b"-----BEGIN PRIVATE KEY-----",
    b"-----BEGIN RSA PRIVATE KEY-----",
    b"-----BEGIN EC PRIVATE KEY-----",
    b"-----BEGIN DSA PRIVATE KEY-----",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def atomic_write_bytes(path: Path, payload: bytes) -> None:
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


def latest_required_timestamp(rows: list[dict[str, str]]) -> str:
    return max(row["updated_at"] for row in rows)


def validate_bundle_timestamp(updated_at: str) -> None:
    try:
        datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise PacketError(f"invalid updated_at timestamp for deterministic ZIP: {updated_at}") from exc


def validate_disclosure_boundary(archive_payloads: dict[str, bytes]) -> None:
    for archive_path, payload in archive_payloads.items():
        if EMAIL_PATTERN.search(payload):
            raise PacketError(
                f"contact metadata is forbidden in the external review bundle: {archive_path}"
            )
        if any(marker in payload for marker in PRIVATE_KEY_MARKERS):
            raise PacketError(
                f"private signing material is forbidden in the external review bundle: {archive_path}"
            )


def current_snapshot_document(root: Path) -> tuple[str, list[dict[str, str]], dict[str, Any], dict[str, Any]]:
    registry = load_registry(root / "research-case/artifact-registry.csv")
    rows = validate_required_rows(root, registry)
    state = load_json(root / "research-case/program-state.json")
    verifier_registry = load_json(root / "research-case/00-governance/verifier-registry.json")
    _, current, expected = build_expected_document(root)
    if current != expected:
        raise PacketError(
            "INTAKE handoff snapshot is stale; rerun export_intake_verifier_packet.py before bundling"
        )
    return current, rows, state, verifier_registry


def readme_text(
    *,
    bundle_timestamp: str,
    state: dict[str, Any],
    verifier_registry: dict[str, Any],
    reviewer_count: int,
    event_count: int,
) -> str:
    return "\n".join(
        [
            "# KEYSTONE-MPP-F1 Intake Review Bundle",
            "",
            "This bundle is a local reviewer handoff for the `INTAKE` phase only.",
            "local generation does not authorize external transfer.",
            "this bundle does not create independent scientific verification.",
            "this bundle does not promote the research phase.",
            "",
            "Current fail-closed state:",
            f"- status: `{state['status']}`",
            f"- phase: `{state['current_phase']}`",
            f"- novelty: `{state['novelty_status']}`",
            f"- feasibility: `{state['feasibility_decision']}`",
            f"- solution viability: `{state['solution_viability_status']}`",
            f"- acceptance readiness: `{state['acceptance_readiness']}`",
            f"- verifier trust mode: `{verifier_registry.get('trust_mode', '')}`",
            f"- active independent reviewers: `{reviewer_count}`",
            f"- independent verification events on canonical INTAKE artifacts: `{event_count}`",
            f"- deterministic bundle timestamp: `{bundle_timestamp}`",
            "",
            "Review boundary:",
            "- the four canonical INTAKE artifacts only",
            "- no novelty certification",
            "- no feasibility approval",
            "- no manuscript or venue approval",
            "- author metadata deferred",
            "",
            "Excluded by design:",
            "- accountable-authority confirmation with contact metadata",
            "- private keys or signing material",
            "- unrelated unpublished artifacts outside the bounded INTAKE review packet",
            "",
        ]
    )


def build_source_entries(
    *,
    root: Path,
    archive_payloads: dict[str, bytes],
    rows: list[dict[str, str]],
    state: dict[str, Any],
    verifier_registry: dict[str, Any],
    reviewer_count: int,
    event_count: int,
    bundle_timestamp: str,
) -> list[dict[str, Any]]:
    manifest_entry: dict[str, Any] = {
        "archive_path": "bundle-manifest.json",
        "source_path": None,
        "source_sha256": None,
        "archive_sha256": None,
    }
    entries: list[dict[str, Any]] = [
        {
            "archive_path": "README.md",
            "source_path": None,
            "source_sha256": sha256_bytes(archive_payloads["README.md"]),
            "archive_sha256": sha256_bytes(archive_payloads["README.md"]),
        },
        manifest_entry,
    ]

    for rel in READ_ONLY_ARCHIVE_PATHS:
        file_path = root / rel
        payload = archive_payloads[rel]
        entries.append(
            {
                "archive_path": rel,
                "source_path": rel,
                "source_sha256": sha256_path(file_path),
                "archive_sha256": sha256_bytes(payload),
            }
        )

    if tuple(entry["archive_path"] for entry in entries) != ARCHIVE_PATHS:
        raise PacketError("internal archive order drift detected while building source entries")

    registry_rows = [
        {
            "path": f"research-case/{row['path']}",
            "required": row["required"],
            "status": row["status"],
            "revision": row["revision"],
            "sha256": row["sha256"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]

    manifest = {
        "schema_id": MANIFEST_SCHEMA_ID,
        "schema_version": 1,
        "status": MANIFEST_STATUS,
        "current_status": state["status"],
        "canonical_phase": state["current_phase"],
        "novelty_status": state["novelty_status"],
        "feasibility_decision": state["feasibility_decision"],
        "solution_viability_status": state["solution_viability_status"],
        "acceptance_readiness": state["acceptance_readiness"],
        "trust_mode": verifier_registry.get("trust_mode", ""),
        "active_independent_reviewers": reviewer_count,
        "independent_verification_events": event_count,
        "bundle_timestamp": bundle_timestamp,
        "author_metadata_status": "DEFERRED",
        "source_files": entries,
        "registry_rows": registry_rows,
    }
    archive_payloads["bundle-manifest.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return entries


def build_bundle(root: Path) -> tuple[bytes, bytes]:
    handoff, rows, state, verifier_registry = current_snapshot_document(root)
    bundle_timestamp = latest_required_timestamp(rows)
    validate_bundle_timestamp(bundle_timestamp)
    reviewers = independent_reviewer_ids(verifier_registry)
    event_count = independent_event_count(
        root / "research-case/00-governance/verification-ledger.jsonl",
        reviewers,
    )
    reviewer_count = len(reviewers)

    archive_payloads: dict[str, bytes] = {
        "README.md": readme_text(
            bundle_timestamp=bundle_timestamp,
            state=state,
            verifier_registry=verifier_registry,
            reviewer_count=reviewer_count,
            event_count=event_count,
        ).encode("utf-8"),
        "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md": handoff.encode("utf-8"),
    }

    for rel in READ_ONLY_ARCHIVE_PATHS[1:]:
        archive_payloads[rel] = (root / rel).read_bytes()

    build_source_entries(
        root=root,
        archive_payloads=archive_payloads,
        rows=rows,
        state=state,
        verifier_registry=verifier_registry,
        reviewer_count=reviewer_count,
        event_count=event_count,
        bundle_timestamp=bundle_timestamp,
    )
    validate_disclosure_boundary(archive_payloads)

    bundle_stream = io.BytesIO()
    timestamp = (1980, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(
        bundle_stream,
        mode="w",
        compression=zipfile.ZIP_STORED,
    ) as archive:
        for rel in ARCHIVE_PATHS:
            info = zipfile.ZipInfo(rel)
            info.date_time = timestamp
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, archive_payloads[rel])

    bundle_bytes = bundle_stream.getvalue()
    sidecar_bytes = (
        f"{sha256_bytes(bundle_bytes)}  ./{BUNDLE_PATH.as_posix()}\n".encode("utf-8")
    )
    return bundle_bytes, sidecar_bytes


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    bundle_path = root / BUNDLE_PATH
    sidecar_path = root / SIDECAR_PATH
    try:
        expected_bundle, expected_sidecar = build_bundle(root)
        current_bundle = bundle_path.read_bytes() if bundle_path.is_file() else None
        current_sidecar = sidecar_path.read_bytes() if sidecar_path.is_file() else None

        if args.check:
            if current_bundle != expected_bundle or current_sidecar != expected_sidecar:
                raise PacketError(
                    "INTAKE review bundle is stale; rerun export_intake_review_bundle.py"
                )
            print(f"OK: INTAKE review bundle is current: {bundle_path}")
            return 0

        if current_bundle != expected_bundle:
            atomic_write_bytes(bundle_path, expected_bundle)
        if current_sidecar != expected_sidecar:
            atomic_write_bytes(sidecar_path, expected_sidecar)
        print(f"WROTE: INTAKE review bundle: {bundle_path}")
        return 0
    except PacketError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
