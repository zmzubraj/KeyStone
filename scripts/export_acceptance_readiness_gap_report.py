#!/usr/bin/env python3
"""Export a deterministic, fail-closed acceptance-readiness gap inventory."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import sys


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
STATE_RELATIVE = Path("research-case/program-state.json")
REGISTRY_RELATIVE = Path("research-case/artifact-registry.csv")
REMEDIATION_RELATIVE = Path("research-case/08-validation/remediation-log.csv")
PREAUTH_BUILD_RELATIVE = Path("paper/preauthorization-build/build-manifest.json")
OUTPUT_RELATIVE = Path("research-case/09-submission/acceptance-readiness.md")
SELF_PATH = "09-submission/acceptance-readiness.md"

PHASE_ORDER = (
    "INTAKE",
    "NOVELTY_AUDIT",
    "FEASIBILITY_GATE",
    "STUDY_DESIGN",
    "AUTHORIZED_EXECUTION",
    "ANALYSIS",
    "MANUSCRIPT",
    "ADVERSARIAL_QA",
    "SUBMISSION_QA",
    "HUMAN_APPROVAL",
)
STATUS_ORDER = ("VERIFIED", "N/A", "DRAFT", "BLOCKED", "STALE", "MISSING")
FINAL_STATUSES = {"VERIFIED", "N/A"}
REQUIRED_STATE = {
    "status": "ACTIVE",
    "acceptance_readiness": "NOT_ASSESSABLE",
}
REQUIRED_REGISTRY_FIELDS = {
    "path",
    "phase",
    "required",
    "owner",
    "status",
    "revision",
    "sha256",
}
REQUIRED_REMEDIATION_FIELDS = {
    "remediation_id",
    "priority",
    "status",
    "claim_ids",
    "owner",
    "action",
    "required_evidence",
    "acceptance_test",
    "dependencies",
    "new_data_required",
    "notes",
}
REQUIRED_PREAUTH_BUILD_FIELDS = {
    "status",
    "canonical_phase",
    "canonical_acceptance_readiness",
    "build_classification",
    "submission_authorized",
    "external_transfer_authorized",
    "blocking_serial_gate",
    "external_review_blocker",
    "page_count",
    "outputs",
}
REMEDIATION_PACKET_MAP = {
    "REM-001": (
        "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md",
        "docs/23_INDEPENDENT_INTAKE_HUMAN_VERIFICATION_SOP_BN.md",
        "docs/24_INVALID_AI_INTAKE_VERIFICATION_QUARANTINE.md",
        "review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip",
        "review-packets/KEYSTONE-MPP-F1-intake-verifier-return-template.json",
    ),
    "REM-002": (
        "docs/21_PC02_NOVELTY_VERIFIER_HANDOFF.md",
        "review-packets/KEYSTONE-MPP-F1-pc02-novelty-review-packet.zip",
        "review-packets/KEYSTONE-MPP-F1-pc02-novelty-verifier-return-template.json",
    ),
    "REM-003": (
        "docs/22_PC03_METHODS_VERIFIER_HANDOFF.md",
        "review-packets/KEYSTONE-MPP-F1-pc03-methods-review-packet.zip",
        "review-packets/KEYSTONE-MPP-F1-pc03-methods-verifier-return-template.json",
    ),
    "REM-005": (
        "research-case/03-design/independent-reproduction-handoff.md",
    ),
}


class GapReportError(RuntimeError):
    """Raised when canonical inputs cannot support a deterministic gap report."""


def _read_state(root: Path) -> dict[str, object]:
    path = root / STATE_RELATIVE
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GapReportError(f"cannot read canonical program state: {exc}") from exc
    if not isinstance(payload, dict):
        raise GapReportError("canonical program state must be a JSON object")
    for field, expected in REQUIRED_STATE.items():
        actual = payload.get(field)
        if actual != expected:
            if field == "acceptance_readiness":
                raise GapReportError(
                    "gap exporter only supports canonical NOT_ASSESSABLE state; "
                    f"got {actual}"
                )
            raise GapReportError(f"canonical state mismatch: {field} expected {expected}, got {actual}")
    phase = payload.get("current_phase")
    if phase not in PHASE_ORDER:
        raise GapReportError(f"unsupported canonical current_phase: {phase}")
    return payload


def _read_registry(root: Path) -> list[dict[str, str]]:
    path = root / REGISTRY_RELATIVE
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = set(reader.fieldnames or ())
            missing_fields = sorted(REQUIRED_REGISTRY_FIELDS - fields)
            if missing_fields:
                raise GapReportError(
                    "artifact registry missing fields: " + ", ".join(missing_fields)
                )
            rows = list(reader)
    except OSError as exc:
        raise GapReportError(f"cannot read artifact registry: {exc}") from exc

    seen: set[str] = set()
    allowed_statuses = set(STATUS_ORDER)
    for row in rows:
        artifact_path = row["path"].strip()
        if not artifact_path:
            raise GapReportError("artifact registry contains blank path")
        if artifact_path in seen:
            raise GapReportError(f"duplicate artifact registry path: {artifact_path}")
        seen.add(artifact_path)
        if row["required"] not in {"true", "false"}:
            raise GapReportError(
                f"invalid required flag for {artifact_path}: {row['required']}"
            )
        if row["status"] not in allowed_statuses:
            raise GapReportError(f"invalid status for {artifact_path}: {row['status']}")
        if row["phase"] not in PHASE_ORDER:
            raise GapReportError(f"invalid phase for {artifact_path}: {row['phase']}")
    if SELF_PATH not in seen:
        raise GapReportError(f"artifact registry lacks canonical readiness path: {SELF_PATH}")
    return rows


def _read_remediation(root: Path) -> list[dict[str, str]]:
    path = root / REMEDIATION_RELATIVE
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = set(reader.fieldnames or ())
            missing_fields = sorted(REQUIRED_REMEDIATION_FIELDS - fields)
            if missing_fields:
                raise GapReportError(
                    "remediation log missing fields: " + ", ".join(missing_fields)
                )
            rows = list(reader)
    except OSError as exc:
        raise GapReportError(f"cannot read remediation log: {exc}") from exc

    seen: set[str] = set()
    for row in rows:
        remediation_id = row["remediation_id"].strip()
        if not remediation_id:
            raise GapReportError("remediation log contains blank remediation_id")
        if remediation_id in seen:
            raise GapReportError(f"duplicate remediation id: {remediation_id}")
        seen.add(remediation_id)
    return rows


def _read_preauthorization_build(root: Path, state: dict[str, object]) -> dict[str, object] | None:
    path = root / PREAUTH_BUILD_RELATIVE
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GapReportError(f"cannot read preauthorization build manifest: {exc}") from exc
    if not isinstance(payload, dict):
        raise GapReportError("preauthorization build manifest must be a JSON object")
    missing_fields = sorted(field for field in REQUIRED_PREAUTH_BUILD_FIELDS if field not in payload)
    if missing_fields:
        raise GapReportError(
            "preauthorization build manifest missing fields: " + ", ".join(missing_fields)
        )
    if payload["canonical_phase"] != state["current_phase"]:
        raise GapReportError(
            "preauthorization build manifest phase mismatch: "
            f"{payload['canonical_phase']} vs {state['current_phase']}"
        )
    if payload["canonical_acceptance_readiness"] != state["acceptance_readiness"]:
        raise GapReportError(
            "preauthorization build manifest acceptance readiness mismatch: "
            f"{payload['canonical_acceptance_readiness']} vs {state['acceptance_readiness']}"
        )
    if payload["build_classification"] != "INTERNAL_PREAUTHORIZATION_ONLY":
        raise GapReportError(
            "preauthorization build manifest must remain INTERNAL_PREAUTHORIZATION_ONLY"
        )
    if payload["submission_authorized"] is not False:
        raise GapReportError("preauthorization build manifest must keep submission_authorized=false")
    if payload["external_transfer_authorized"] is not False:
        raise GapReportError(
            "preauthorization build manifest must keep external_transfer_authorized=false"
        )
    if payload["blocking_serial_gate"] != state["current_phase"]:
        raise GapReportError(
            "preauthorization build manifest blocking serial gate mismatch: "
            f"{payload['blocking_serial_gate']} vs {state['current_phase']}"
        )
    outputs = payload["outputs"]
    if not isinstance(outputs, list) or not outputs:
        raise GapReportError("preauthorization build manifest outputs must be a non-empty list")
    return payload


def _render_status_counts(rows: list[dict[str, str]]) -> list[str]:
    counts = Counter(row["status"] for row in rows)
    lines = ["| Lifecycle status | Required artifact count |", "| --- | ---: |"]
    for status in STATUS_ORDER:
        count = counts.get(status, 0)
        if count:
            lines.append(f"| `{status}` | {count} |")
    return lines


def _render_gap_rows(rows: list[dict[str, str]]) -> list[str]:
    phase_rank = {phase: index for index, phase in enumerate(PHASE_ORDER)}
    gaps = sorted(
        (row for row in rows if row["status"] not in FINAL_STATUSES),
        key=lambda row: (phase_rank[row["phase"]], row["path"]),
    )
    lines = [
        "| Phase | Canonical artifact | Status | Revision | Owner | Smallest adequate action |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for row in gaps:
        action = (
            "independent semantic verification with authenticated provenance"
            if row["status"] == "DRAFT"
            else "produce the canonical artifact, then independently verify it"
        )
        if row["status"] in {"BLOCKED", "STALE"}:
            action = "resolve the recorded blocker or invalidation, regenerate, and reverify"
        lines.append(
            f"| `{row['phase']}` | `{row['path']}` | `{row['status']}` | "
            f"{row['revision'] or '0'} | `{row['owner'] or 'UNASSIGNED'}` | {action} |"
        )
    return lines


def _format_dependencies(raw: str) -> str:
    items = [item.strip() for item in raw.split("|") if item.strip()]
    return ", ".join(f"`{item}`" for item in items) if items else "none"


def _format_packet_paths(root: Path, remediation_id: str) -> str:
    paths = REMEDIATION_PACKET_MAP.get(remediation_id)
    if not paths:
        return "none prepared yet"
    prepared = [f"`{path}`" for path in paths if (root / path).exists()]
    missing = [path for path in paths if not (root / path).exists()]
    if prepared and not missing:
        return ", ".join(prepared)
    if prepared and missing:
        return ", ".join(prepared) + " (partial packet set)"
    return "declared packet path missing"


def _next_step(remediation_id: str, row: dict[str, str]) -> str:
    status = row["status"].strip()
    if status == "DEFERRED":
        return "keep deferred until every accountable author explicitly approves metadata freeze"
    if remediation_id == "REM-001":
        return "obtain accountable-human authorization for a named independent reviewer, follow the human-verification SOP, and only then transfer the prepared intake packet while preserving the invalid-AI quarantine boundary"
    if remediation_id in {"REM-002", "REM-003"}:
        return "preserve the prepared packet, but do not transfer it until REM-001 is recorded and accountable-human authorization names the reviewer"
    if remediation_id == "REM-005":
        return "use the clean-machine handoff only after the result-blind design and authorized execution prerequisites are satisfied"
    if remediation_id == "REM-008":
        return "select the venue only after the evidence package is defensible enough to survive novelty and reproduction review"
    if remediation_id == "REM-009":
        return "build the hermetic submission package only after visual QA and venue rules are current"
    if remediation_id == "REM-011":
        return "commission independent manuscript review only after the evidence package, reproduction, and submission package exist"
    if remediation_id == "REM-012":
        return "either independently authorize and rerun the C003 negative-finding lane or explicitly narrow the claim-to-figure contract"
    return row["action"].strip()


def _render_remediation_rows(root: Path, rows: list[dict[str, str]]) -> list[str]:
    priority_rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    ordered = sorted(
        rows,
        key=lambda row: (
            priority_rank.get(row["priority"].strip(), 99),
            row["remediation_id"].strip(),
        ),
    )
    lines = [
        "| Remediation | Priority | Status | Owner | Dependencies | Prepared handoff artifacts | Next admissible step |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in ordered:
        remediation_id = row["remediation_id"].strip()
        lines.append(
            f"| `{remediation_id}` | `{row['priority'].strip()}` | `{row['status'].strip()}` | "
            f"`{row['owner'].strip() or 'UNASSIGNED'}` | {_format_dependencies(row['dependencies'])} | "
            f"{_format_packet_paths(root, remediation_id)} | {_next_step(remediation_id, row)} |"
        )
    return lines


def _render_preauthorization_snapshot(build_manifest: dict[str, object] | None) -> list[str]:
    if build_manifest is None:
        return [
            "## Draft preauthorization build snapshot",
            "",
            "No current internal preauthorization build manifest is registered.",
            "",
        ]
    pdf_path = "paper/preauthorization-build/main.pdf"
    manifest_path = str(PREAUTH_BUILD_RELATIVE)
    return [
        "## Draft preauthorization build snapshot",
        "",
        "This snapshot is **internal preauthorization only**. It helps the workspace stay assembly-ready, "
        "but it does **not** satisfy `REM-009`, does not authorize external transfer, and does not prove "
        "submission-package or venue readiness.",
        "",
        "| Snapshot field | Current value |",
        "| --- | --- |",
        f"| Build status | `{build_manifest['status']}` |",
        f"| Build classification | `{build_manifest['build_classification']}` |",
        f"| Canonical phase | `{build_manifest['canonical_phase']}` |",
        f"| Canonical acceptance readiness | `{build_manifest['canonical_acceptance_readiness']}` |",
        f"| Blocking serial gate | `{build_manifest['blocking_serial_gate']}` |",
        f"| External review blocker | `{build_manifest['external_review_blocker']}` |",
        f"| Submission authorized | `{build_manifest['submission_authorized']}` |",
        f"| External transfer authorized | `{build_manifest['external_transfer_authorized']}` |",
        f"| Draft PDF page count | `{build_manifest['page_count']}` |",
        f"| Build manifest | `{manifest_path}` |",
        f"| Draft PDF | `{pdf_path}` |",
        "",
    ]


def render_report(
    root: Path,
    state: dict[str, object],
    registry: list[dict[str, str]],
    remediation: list[dict[str, str]],
    build_manifest: dict[str, object] | None,
) -> str:
    required_rows = [
        row for row in registry if row["required"] == "true" and row["path"] != SELF_PATH
    ]
    phase = str(state["current_phase"])
    next_action = str(state.get("next_action") or "Resolve the current serial gate.")
    status_counts = _render_status_counts(required_rows)
    gap_rows = _render_gap_rows(required_rows)
    remediation_rows = _render_remediation_rows(root, remediation)
    final_count = sum(row["status"] in FINAL_STATUSES for row in required_rows)
    open_count = len(required_rows) - final_count

    lines = [
        "# Acceptance-Readiness Gap Report",
        "",
        "System: `KEYSTONE-MPP-F1`  ",
        "Artifact status: `DRAFT / PRE-SUBMISSION / MECHANICAL GAP INVENTORY`  ",
        "Acceptance readiness: `NOT_ASSESSABLE`  ",
        f"Current serial gate: `{phase}`",
        "",
        "## Executive disposition",
        "",
        "The manuscript package is **not publication-ready and not submission-ready**. "
        "The canonical program has not cleared the current serial scientific gate, and "
        "required downstream scientific, adversarial-review, venue, build, and human-approval "
        "artifacts are not independently final.",
        "",
        "This report is a mechanical gap inventory, not independent scientific review, "
        "editorial judgment, author approval, or evidence that any missing gate has passed.",
        "",
        "Final author order, corresponding-author designation, and exact affiliation wording remain deferred. "
        "This report does not freeze or infer them.",
        "",
        "## Current blocking boundary",
        "",
        "| Boundary | Disposition | Required resolution evidence |",
        "| --- | --- | --- |",
        f"| External independent INTAKE verification | `{'BLOCKING' if phase == 'INTAKE' else 'RESOLVED_OR_SUPERSEDED'}` | Authenticated, independently signed canonical INTAKE verification events with matching artifact hashes and provenance |",
        f"| Driver next action | `WAIT` | {next_action} |",
        "| External transfer | `NOT_AUTHORIZED_IN_THIS_RUN` | Explicit accountable-human transfer authorization plus recipient and confidentiality boundary |",
        "| Acceptance forecast | `N/A — NOT ESTIMABLE` | Target-matched, transparently calibrated historical evidence; absent at this stage |",
        "",
        *_render_preauthorization_snapshot(build_manifest),
        "## Priority remediation and external-review queue",
        "",
        "Prepared packets are producer-side artifacts only. They do not authorize external transfer, do not prove independent review, and do not clear any gate until a named reviewer returns an authenticated, hash-bound decision through the canonical verifier workflow.",
        "",
        *remediation_rows,
        "",
        "## Required-artifact summary",
        "",
        f"Required canonical artifacts assessed (excluding this self-report): **{len(required_rows)}**.  ",
        f"Final (`VERIFIED` or justified `N/A`): **{final_count}**.  ",
        f"Open (`DRAFT`, `MISSING`, `BLOCKED`, or `STALE`): **{open_count}**.",
        "",
        *status_counts,
        "",
        "## Open canonical requirements",
        "",
        *gap_rows,
        "",
        "## Promotion rule",
        "",
        "No aggregate score, local test pass, file existence, AI review, or prose quality may "
        "promote acceptance readiness. Advancement requires the serial research phases, "
        "artifact-specific semantic validation, matching hashes, authenticated independent "
        "verification where required, rule-derived adversarial/submission ledgers, current venue "
        "rules, hermetic build evidence, rendered-page review, and accountable human approval.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    output = root / OUTPUT_RELATIVE
    try:
        state = _read_state(root)
        expected = render_report(
            root,
            state,
            _read_registry(root),
            _read_remediation(root),
            _read_preauthorization_build(root, state),
        )
    except GapReportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.check:
        try:
            actual = output.read_text(encoding="utf-8")
        except OSError:
            actual = ""
        if actual != expected:
            print(f"error: acceptance-readiness gap report is stale: {output}", file=sys.stderr)
            return 1
        print(f"OK: acceptance-readiness gap report is current: {output}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(expected, encoding="utf-8")
    print(f"Wrote acceptance-readiness gap report: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
