#!/usr/bin/env python3
"""Fail closed when the KEYSTONE manuscript drifts from its evidence contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import sys


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT_RELATIVE = Path("research-case/07-manuscript/manuscript.md")
MATRIX_RELATIVE = Path("research-case/07-manuscript/claim-evidence-matrix.csv")
GRAPH_RELATIVE = Path("research-case/07-manuscript/claim-graph.json")
SOURCE_MANIFEST_RELATIVE = Path("research-case/07-manuscript/source-manifest.json")
STATE_RELATIVE = Path("research-case/program-state.json")
BIBLIOGRAPHY_RELATIVE = Path("paper/references.bib")

EXPECTED_STATE = {
    "status": "ACTIVE",
    "current_phase": "INTAKE",
    "resume_from": "INTAKE",
    "novelty_status": "UNRESOLVED",
    "feasibility_decision": "UNASSESSED",
    "solution_viability_status": "ASSERTED_ONLY",
    "acceptance_readiness": "NOT_ASSESSABLE",
    "maturity_stage": "CONCEPT",
}
EXPECTED_CLAIMS = {"C001", "C002", "C003"}
REQUIRED_TABLES = {f"T{index}" for index in range(1, 9)}
ALLOWED_TABLES = REQUIRED_TABLES
REQUIRED_DIAGRAMS = {f"D{index}" for index in range(1, 9)}
ALLOWED_DIAGRAMS = REQUIRED_DIAGRAMS
REQUIRED_FIGURES = {f"F{index}" for index in range(1, 6)}
ALLOWED_FIGURES = {f"F{index}" for index in range(1, 9)}
REQUIRED_SOURCE_BINDINGS = {
    "SRC-MANUSCRIPT-ALIGNMENT-CHECKER": Path("scripts/check_manuscript_alignment.py"),
    "SRC-MANUSCRIPT-ALIGNMENT-TESTS": Path("prototype/tests/test_manuscript_alignment.py"),
}
REQUIRED_MANUSCRIPT_MARKERS = (
    "DRAFT / PRE-MANUSCRIPT / PRE-AUTHORIZATION",
    "UNRESOLVED",
    "UNASSESSED",
    "not authorized",
    "final author order",
    "corresponding-author designation",
    "exact affiliation wording",
    "deferred",
)


class AlignmentError(RuntimeError):
    """Raised when an alignment contract is absent or inconsistent."""


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise AlignmentError(f"cannot read required file {path}: {exc}") from exc


def _read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(_read_text(path))
    except json.JSONDecodeError as exc:
        raise AlignmentError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AlignmentError(f"expected JSON object in {path}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise AlignmentError(f"cannot hash required file {path}: {exc}") from exc
    return digest.hexdigest()


def _sorted_ids(values: set[str]) -> list[str]:
    return sorted(values, key=lambda value: (value[0], int(value[1:])))


def _check_state(root: Path) -> None:
    state = _read_json(root / STATE_RELATIVE)
    for field, expected in EXPECTED_STATE.items():
        actual = state.get(field)
        if actual != expected:
            raise AlignmentError(
                f"canonical state mismatch: {field} expected {expected}, got {actual}"
            )


def _check_markers(manuscript: str) -> None:
    normalized = " ".join(manuscript.lower().split())
    missing = [
        marker
        for marker in REQUIRED_MANUSCRIPT_MARKERS
        if " ".join(marker.lower().split()) not in normalized
    ]
    if missing:
        raise AlignmentError("missing fail-closed manuscript markers: " + ", ".join(missing))


def _extract_citations(manuscript: str) -> set[str]:
    citations = set(re.findall(r"(?<![\w.])@([A-Za-z0-9_:.+-]+)", manuscript))
    for group in re.findall(r"\\cite[a-zA-Z*]*\{([^}]+)\}", manuscript):
        citations.update(key.strip() for key in group.split(",") if key.strip())
    return citations


def _check_citations(root: Path, manuscript: str) -> set[str]:
    bibliography = _read_text(root / BIBLIOGRAPHY_RELATIVE)
    known = set(re.findall(r"@[A-Za-z]+\s*\{\s*([^,\s]+)\s*,", bibliography))
    citations = _extract_citations(manuscript)
    unknown = sorted(citations - known)
    if unknown:
        raise AlignmentError("unknown citation key: " + ", ".join(unknown))
    return citations


def _check_images(root: Path, manuscript_path: Path, manuscript: str) -> list[Path]:
    root_resolved = root.resolve()
    image_targets = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", manuscript)
    resolved_images: list[Path] = []
    for raw_target in image_targets:
        target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("/"):
            raise AlignmentError(f"image reference must be workspace-local: {target}")
        resolved = (manuscript_path.parent / target).resolve()
        try:
            resolved.relative_to(root_resolved)
        except ValueError as exc:
            raise AlignmentError(f"image reference escapes workspace root: {target}") from exc
        if not resolved.is_file():
            raise AlignmentError(f"missing manuscript image reference: {target}")
        resolved_images.append(resolved)
    return resolved_images


def _read_matrix_claims(path: Path) -> set[str]:
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or "claim_id" not in reader.fieldnames:
                raise AlignmentError(f"claim matrix lacks claim_id column: {path}")
            return {row["claim_id"].strip() for row in reader if row.get("claim_id", "").strip()}
    except OSError as exc:
        raise AlignmentError(f"cannot read claim matrix {path}: {exc}") from exc


def _check_claims(root: Path, manuscript: str) -> set[str]:
    manuscript_claims = set(re.findall(r"\bC\d{3}\b", manuscript))
    matrix_claims = _read_matrix_claims(root / MATRIX_RELATIVE)
    graph = _read_json(root / GRAPH_RELATIVE)
    claims_node = graph.get("claims")
    if not isinstance(claims_node, dict):
        raise AlignmentError("claim graph lacks claims object")
    graph_claims = set(claims_node)
    if not (manuscript_claims == matrix_claims == graph_claims == EXPECTED_CLAIMS):
        raise AlignmentError(
            "claim set mismatch: "
            f"manuscript={sorted(manuscript_claims)}; matrix={sorted(matrix_claims)}; "
            f"graph={sorted(graph_claims)}; expected={sorted(EXPECTED_CLAIMS)}"
        )
    return manuscript_claims


def _check_family(
    manuscript: str,
    label: str,
    prefix: str,
    required: set[str],
    allowed: set[str],
) -> set[str]:
    found = set(re.findall(rf"\b{prefix}\d+\b", manuscript))
    unexpected = found - allowed
    if unexpected:
        raise AlignmentError(
            f"unexpected manuscript {label} identifiers: " + ", ".join(_sorted_ids(unexpected))
        )
    missing = required - found
    if missing:
        raise AlignmentError(
            f"missing manuscript {label} identifiers: " + ", ".join(_sorted_ids(missing))
        )
    return found


def _check_source_manifest(root: Path) -> int:
    payload = _read_json(root / SOURCE_MANIFEST_RELATIVE)
    sources = payload.get("sources")
    if not isinstance(sources, list):
        raise AlignmentError("source manifest lacks sources array")
    seen: set[str] = set()
    resolved_rows: dict[str, tuple[str, str]] = {}
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise AlignmentError(f"invalid source manifest row at index {index}")
        source_id = source.get("source_id")
        relative = source.get("path")
        base = source.get("path_base")
        expected_hash = source.get("sha256")
        if not all(isinstance(value, str) and value for value in (source_id, relative, base, expected_hash)):
            raise AlignmentError(f"incomplete source manifest row at index {index}")
        if source_id in seen:
            raise AlignmentError(f"duplicate source manifest source_id: {source_id}")
        seen.add(source_id)
        if base == "workspace_root":
            base_path = root
        elif base == "research_case_root":
            base_path = root / "research-case"
        else:
            raise AlignmentError(f"unsupported path_base for {source_id}: {base}")
        path = (base_path / relative).resolve()
        try:
            path.relative_to(base_path.resolve())
        except ValueError as exc:
            raise AlignmentError(f"source manifest path escapes {base}: {source_id}") from exc
        if not path.is_file():
            raise AlignmentError(f"source manifest file missing for {source_id}: {relative}")
        actual_hash = _sha256(path)
        if actual_hash != expected_hash:
            raise AlignmentError(f"source manifest hash mismatch for {source_id}: {relative}")
        resolved_rows[source_id] = (relative, base)
    missing_bindings = sorted(set(REQUIRED_SOURCE_BINDINGS) - set(resolved_rows))
    if missing_bindings:
        raise AlignmentError(
            "missing required source manifest bindings: " + ", ".join(missing_bindings)
        )
    for source_id, expected_path in REQUIRED_SOURCE_BINDINGS.items():
        relative, base = resolved_rows[source_id]
        if base != "workspace_root" or Path(relative) != expected_path:
            raise AlignmentError(
                f"source manifest binding mismatch for {source_id}: "
                f"expected workspace_root::{expected_path}, got {base}::{relative}"
            )
    return len(sources)


def check_alignment(root: Path) -> dict[str, object]:
    root = root.resolve()
    manuscript_path = root / MANUSCRIPT_RELATIVE
    manuscript = _read_text(manuscript_path)
    _check_state(root)
    _check_markers(manuscript)
    citations = _check_citations(root, manuscript)
    images = _check_images(root, manuscript_path, manuscript)
    claims = _check_claims(root, manuscript)
    tables = _check_family(manuscript, "table", "T", REQUIRED_TABLES, ALLOWED_TABLES)
    diagrams = _check_family(manuscript, "diagram", "D", REQUIRED_DIAGRAMS, ALLOWED_DIAGRAMS)
    figures = _check_family(manuscript, "figure", "F", REQUIRED_FIGURES, ALLOWED_FIGURES)
    source_count = _check_source_manifest(root)
    return {
        "citation_count": len(citations),
        "claim_ids": _sorted_ids(claims),
        "diagram_ids": _sorted_ids(diagrams),
        "figure_ids": _sorted_ids(figures),
        "image_reference_count": len(images),
        "source_count": source_count,
        "status": "PASS",
        "table_ids": _sorted_ids(tables),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args(argv)
    try:
        summary = check_alignment(args.root)
    except AlignmentError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
