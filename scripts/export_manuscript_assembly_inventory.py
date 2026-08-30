#!/usr/bin/env python3
"""Export a deterministic draft manuscript-assembly inventory."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re
import sys

from check_manuscript_alignment import AlignmentError, check_alignment


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
STATE_RELATIVE = Path("research-case/program-state.json")
MANUSCRIPT_RELATIVE = Path("research-case/07-manuscript/manuscript.md")
MATRIX_RELATIVE = Path("research-case/07-manuscript/claim-evidence-matrix.csv")
FIGURE_MANIFEST_RELATIVE = Path("research-case/06-visuals/figures/figure-manifest.csv")
TABLE_MANIFEST_RELATIVE = Path("paper/tables/t1_t8_manifest.json")
OUTPUT_RELATIVE = Path("research-case/07-manuscript/assembly-inventory.md")

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
EXPECTED_CLAIM_FIELDS = {
    "claim_id",
    "claim_text",
    "table_targets",
    "figure_targets",
    "diagram_targets",
    "current_status",
    "blocked_by",
    "allowed_wording",
}
EXPECTED_FIGURE_FIELDS = {
    "figure_id",
    "canonical_output_path",
    "derivative_png_path",
    "status",
    "source_data",
}
FUTURE_FIGURE_IDS = ("F6", "F7", "F8")


class InventoryError(RuntimeError):
    """Raised when canonical inputs cannot support the inventory."""


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise InventoryError(f"cannot read required file {path}: {exc}") from exc


def _read_json(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(_read_text(path))
    except json.JSONDecodeError as exc:
        raise InventoryError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise InventoryError(f"expected JSON object in {path}")
    return payload


def _read_state(root: Path) -> dict[str, str]:
    payload = _read_json(root / STATE_RELATIVE)
    for field, expected in EXPECTED_STATE.items():
        actual = payload.get(field)
        if actual != expected:
            raise InventoryError(
                f"canonical state mismatch: {field} expected {expected}, got {actual}"
            )
    return {field: str(payload[field]) for field in EXPECTED_STATE}


def _split_targets(raw: str) -> list[str]:
    return [item.strip() for item in raw.split("|") if item.strip()]


def _format_targets(values: list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(f"`{value}`" for value in values)


def _read_claim_rows(root: Path) -> list[dict[str, str]]:
    path = root / MATRIX_RELATIVE
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = set(reader.fieldnames or ())
            missing = sorted(EXPECTED_CLAIM_FIELDS - fields)
            if missing:
                raise InventoryError(
                    "claim matrix missing fields: " + ", ".join(missing)
                )
            rows = []
            seen: set[str] = set()
            for row in reader:
                claim_id = row["claim_id"].strip()
                if not claim_id:
                    raise InventoryError("claim matrix contains blank claim_id")
                if claim_id in seen:
                    raise InventoryError(f"duplicate claim_id in claim matrix: {claim_id}")
                seen.add(claim_id)
                rows.append(
                    {
                        "claim_id": claim_id,
                        "current_status": row["current_status"].strip() or "UNKNOWN",
                        "table_targets": _format_targets(_split_targets(row["table_targets"])),
                        "figure_targets": _format_targets(_split_targets(row["figure_targets"])),
                        "diagram_targets": _format_targets(_split_targets(row["diagram_targets"])),
                        "blocked_by": row["blocked_by"].strip() or "none",
                        "allowed_wording": row["allowed_wording"].strip() or "none",
                    }
                )
    except OSError as exc:
        raise InventoryError(f"cannot read claim matrix {path}: {exc}") from exc
    return sorted(rows, key=lambda row: row["claim_id"])


def _parse_image_assets(root: Path) -> list[dict[str, str]]:
    manuscript_path = root / MANUSCRIPT_RELATIVE
    manuscript = _read_text(manuscript_path)
    assets: list[dict[str, str]] = []
    seen: set[str] = set()
    for alt, target in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", manuscript):
        match = re.search(r"\b([DF]\d+)\b", alt)
        if match is None:
            continue
        asset_id = match.group(1)
        if asset_id in seen:
            raise InventoryError(f"duplicate rendered manuscript asset: {asset_id}")
        seen.add(asset_id)
        resolved = (manuscript_path.parent / target.strip()).resolve()
        if not resolved.is_file():
            raise InventoryError(f"missing rendered manuscript asset: {target.strip()}")
        assets.append(
            {
                "asset_id": asset_id,
                "kind": "diagram" if asset_id.startswith("D") else "figure",
                "target": target.strip(),
            }
        )
    return sorted(assets, key=lambda row: (row["kind"], row["asset_id"]))


def _read_figure_manifest(root: Path) -> list[dict[str, str]]:
    path = root / FIGURE_MANIFEST_RELATIVE
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = set(reader.fieldnames or ())
            missing = sorted(EXPECTED_FIGURE_FIELDS - fields)
            if missing:
                raise InventoryError(
                    "figure manifest missing fields: " + ", ".join(missing)
                )
            rows = []
            seen: set[str] = set()
            for row in reader:
                figure_id = row["figure_id"].strip()
                if not figure_id:
                    raise InventoryError("figure manifest contains blank figure_id")
                if figure_id in seen:
                    raise InventoryError(f"duplicate figure manifest id: {figure_id}")
                seen.add(figure_id)
                rows.append(
                    {
                        "figure_id": figure_id,
                        "status": row["status"].strip() or "UNKNOWN",
                        "canonical_output_path": row["canonical_output_path"].strip(),
                        "derivative_png_path": row["derivative_png_path"].strip(),
                        "source_data": row["source_data"].strip(),
                    }
                )
    except OSError as exc:
        raise InventoryError(f"cannot read figure manifest {path}: {exc}") from exc
    return sorted(rows, key=lambda row: row["figure_id"])


def _read_table_manifest(root: Path) -> dict[str, object]:
    payload = _read_json(root / TABLE_MANIFEST_RELATIVE)
    table_ids = payload.get("table_ids")
    table_dispositions = payload.get("table_dispositions")
    outputs = payload.get("outputs")
    missing_required = payload.get("missing_required_evidence")
    if not isinstance(table_ids, list) or not all(isinstance(item, str) for item in table_ids):
        raise InventoryError("table manifest lacks string table_ids")
    if not isinstance(table_dispositions, dict):
        raise InventoryError("table manifest lacks table_dispositions object")
    if not isinstance(outputs, list):
        raise InventoryError("table manifest lacks outputs array")
    if not isinstance(missing_required, list) or not all(
        isinstance(item, str) for item in missing_required
    ):
        raise InventoryError("table manifest lacks string missing_required_evidence")
    output_paths: dict[str, str] = {}
    for row in outputs:
        if not isinstance(row, dict):
            raise InventoryError("table manifest outputs must contain objects")
        path_value = row.get("path")
        if not isinstance(path_value, str) or not path_value:
            raise InventoryError("table manifest output row lacks path")
        match = re.match(r"t(\d+)_", path_value)
        if match is not None:
            output_paths[f"T{int(match.group(1))}"] = path_value
    return {
        "table_ids": sorted(table_ids, key=lambda value: int(value[1:])),
        "table_dispositions": {
            key: str(value) for key, value in table_dispositions.items() if isinstance(value, str)
        },
        "output_paths": output_paths,
        "missing_required_evidence": [item for item in missing_required if item],
    }


def render_inventory(root: Path) -> str:
    state = _read_state(root)
    try:
        alignment = check_alignment(root)
    except AlignmentError as exc:
        raise InventoryError(str(exc)) from exc
    manuscript = _read_text(root / MANUSCRIPT_RELATIVE)
    claim_rows = _read_claim_rows(root)
    image_assets = _parse_image_assets(root)
    figure_rows = _read_figure_manifest(root)
    table_manifest = _read_table_manifest(root)

    figure_asset_paths = {
        row["asset_id"]: row["target"] for row in image_assets if row["kind"] == "figure"
    }
    diagram_asset_paths = {
        row["asset_id"]: row["target"] for row in image_assets if row["kind"] == "diagram"
    }

    figure_manifest_ids = {row["figure_id"] for row in figure_rows}
    referenced_figure_ids = list(alignment["figure_ids"])
    missing_figure_assets = [
        figure_id for figure_id in referenced_figure_ids if figure_id not in figure_manifest_ids
    ]
    unexpected_future_manifest = sorted(
        figure_id for figure_id in figure_manifest_ids if figure_id in FUTURE_FIGURE_IDS
    )
    if unexpected_future_manifest:
        raise InventoryError(
            "future figure ids may not enter the rendered manifest during INTAKE: "
            + ", ".join(unexpected_future_manifest)
        )
    unexpected_future_assets = sorted(
        figure_id for figure_id in figure_asset_paths if figure_id in FUTURE_FIGURE_IDS
    )
    if unexpected_future_assets:
        raise InventoryError(
            "future figure ids may not appear as rendered manuscript assets during INTAKE: "
            + ", ".join(unexpected_future_assets)
        )
    if missing_figure_assets != list(FUTURE_FIGURE_IDS):
        raise InventoryError(
            "future figure boundary drift: expected missing rendered figures "
            f"{list(FUTURE_FIGURE_IDS)}, got {missing_figure_assets}"
        )
    if set(figure_asset_paths) != figure_manifest_ids:
        raise InventoryError(
            "rendered figure references and figure manifest ids differ: "
            f"images={sorted(figure_asset_paths)}; manifest={sorted(figure_manifest_ids)}"
        )

    lines = [
        "# Manuscript Assembly Inventory",
        "",
        "System: `KEYSTONE-MPP-F1`  ",
        "Artifact status: `DRAFT / PRE-MANUSCRIPT / PRE-AUTHORIZATION`  ",
        f"Current serial gate: `{state['current_phase']}`  ",
        f"Novelty: `{state['novelty_status']}`  ",
        f"Feasibility: `{state['feasibility_decision']}`  ",
        f"Solution viability: `{state['solution_viability_status']}`  ",
        f"Acceptance readiness: `{state['acceptance_readiness']}`",
        "",
        "This inventory binds the current manuscript shell to its draft claim, table, figure, and "
        "diagram assets. It is a deterministic assembly aid only. It does not authorize confirmatory "
        "execution, external transfer, novelty clearance, feasibility promotion, or submission.",
        "",
        "Final author order, corresponding-author designation, and exact affiliation wording remain deferred.",
        "",
        "## Coverage summary",
        "",
        f"- Claim anchors in manuscript/matrix/graph: **{len(alignment['claim_ids'])}**",
        f"- Table identifiers referenced in manuscript: **{len(alignment['table_ids'])}**",
        f"- Diagram identifiers with rendered assets: **{len(diagram_asset_paths)}**",
        f"- Quantitative figures with rendered assets: **{len(figure_rows)}**",
        f"- Manuscript-local image references: **{alignment['image_reference_count']}**",
        f"- Source-manifest entries verified by the alignment checker: **{alignment['source_count']}**",
        "",
    ]
    if missing_figure_assets:
        lines.extend(
            [
                "Referenced figure identifiers without rendered manuscript assets: "
                + ", ".join(f"`{item}`" for item in missing_figure_assets)
                + ".",
                "",
            ]
        )

    lines.extend(
        [
            "## Future-figure boundary",
            "",
            "The current canonical INTAKE manuscript may reference `F6`, `F7`, and `F8` only as future confirmatory outputs. "
            "They must remain absent from the rendered manuscript asset set and the figure manifest until `REM-003` and `REM-004` are closed and canonical lineage exists.",
            "",
            "## Claim map",
            "",
            "| Claim | Draft status | Table targets | Figure targets | Diagram targets | Blocked by | Allowed wording |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in claim_rows:
        lines.append(
            f"| `{row['claim_id']}` | `{row['current_status']}` | {row['table_targets']} | "
            f"{row['figure_targets']} | {row['diagram_targets']} | `{row['blocked_by']}` | "
            f"`{row['allowed_wording']}` |"
        )

    lines.extend(
        [
            "",
            "## Table inventory",
            "",
            "| Table | Draft role | Output binding |",
            "| --- | --- | --- |",
        ]
    )
    for table_id in table_manifest["table_ids"]:
        disposition = table_manifest["table_dispositions"].get(table_id, "MISSING_DISPOSITION")
        output_path = table_manifest["output_paths"].get(table_id, "MISSING_OUTPUT_BINDING")
        lines.append(f"| `{table_id}` | {disposition} | `{output_path}` |")

    lines.extend(
        [
            "",
            "## Figure inventory",
            "",
            "| Figure | Status | Rendered SVG | Derivative PNG | Source data |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in figure_rows:
        lines.append(
            f"| `{row['figure_id']}` | `{row['status']}` | `{figure_asset_paths[row['figure_id']]}` | "
            f"`{row['derivative_png_path']}` | `{row['source_data']}` |"
        )

    lines.extend(
        [
            "",
            "## Diagram inventory",
            "",
            "| Diagram | Rendered SVG | Editable source | Alternate source |",
            "| --- | --- | --- | --- |",
        ]
    )
    for diagram_id in alignment["diagram_ids"]:
        target = diagram_asset_paths.get(diagram_id)
        if target is None:
            raise InventoryError(f"missing rendered diagram reference for {diagram_id}")
        base = target.removesuffix(".svg")
        lines.append(f"| `{diagram_id}` | `{target}` | `{base}.mmd` | `{base}.dot` |")

    lines.extend(
        [
            "",
            "## Blocking evidence",
            "",
            "| Blocking item | Source |",
            "| --- | --- |",
        ]
    )
    for blocked_item in table_manifest["missing_required_evidence"]:
        lines.append(f"| `{blocked_item}` | `paper/tables/t1_t8_manifest.json` |")
    seen_claim_blockers: set[str] = set()
    for row in claim_rows:
        blocker = row["blocked_by"]
        if blocker == "none" or blocker in seen_claim_blockers:
            continue
        seen_claim_blockers.add(blocker)
        lines.append(f"| `{blocker}` | `research-case/07-manuscript/claim-evidence-matrix.csv` |")

    if "deferred" not in manuscript.lower():
        raise InventoryError("manuscript no longer declares deferred author metadata")

    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    output = root / OUTPUT_RELATIVE
    try:
        expected = render_inventory(root)
    except InventoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.check:
        try:
            actual = output.read_text(encoding="utf-8")
        except OSError:
            actual = ""
        if actual != expected:
            print(f"error: manuscript assembly inventory is stale: {output}", file=sys.stderr)
            return 1
        print(f"OK: manuscript assembly inventory is current: {output}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(expected, encoding="utf-8")
    print(f"Wrote manuscript assembly inventory: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
