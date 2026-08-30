#!/usr/bin/env python3
"""Export a deterministic, quarantined preauthorization exploratory ledger."""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
from pathlib import Path
import sys


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = Path("research-case/program-state.json")
CHARTER_PATH = Path("research-case/00-governance/program-charter.md")
SOURCE_PATH = Path("prototype/results/markov_temporal_dependence.csv")
EXPERIMENT_MANIFEST_PATH = Path("prototype/results/experiment_manifest.json")
PROVENANCE_PATH = Path("research-case/04-data/provenance-manifest.csv")
EVIDENCE_PATH = Path("research-case/04-data/evidence-status.csv")
OUTPUT_PATH = Path("research-case/05-analysis/results/exploratory-findings.csv")

ASSET_ID = "ASSET-MARKOV-TEMPORAL-DEPENDENCE"
EVIDENCE_ID = "RID-C003-CORR-001"
REQUIRED_STATE = {
    "status": "ACTIVE",
    "current_phase": "INTAKE",
    "resume_from": "INTAKE",
    "novelty_status": "UNRESOLVED",
    "solution_viability_status": "ASSERTED_ONLY",
    "acceptance_readiness": "NOT_ASSESSABLE",
}
REQUIRED_BOUNDARY = {
    "authorization_boundary": "PREAUTHORIZATION_ONLY",
    "scientific_evidence_status": "NOT_SCIENTIFIC_EVIDENCE",
    "independence_status": "SAME_WORKSPACE_NOT_INDEPENDENT",
}
SOURCE_FIELDS = (
    "audits",
    "trials",
    "seed",
    "online_to_offline",
    "offline_to_online",
    "final_catastrophic_trials",
    "all_audits_pass_and_final_catastrophic_count",
    "conditional_sequence_false_accept_rate",
    "conditional_sequence_false_accept_ci_low",
    "conditional_sequence_false_accept_ci_high",
    "static_set_repeated_bound",
)
OUTPUT_FIELDS = (
    "finding_id",
    "claim_id",
    "evidence_ids",
    "source_asset_id",
    "source_path",
    "analysis_class",
    "estimand",
    "condition",
    "effect_estimate",
    "uncertainty_interval",
    "sample_size",
    "seed",
    "comparison",
    "analysis_status",
    "authorized",
    "independent",
    "evidence_origin",
    "evidence_maturity",
    "claim_ceiling",
    "interpretation_boundary",
    "excluded_generality",
    "notes",
)


class ExploratoryExportError(RuntimeError):
    """Raised when an exploratory export would violate its evidence boundary."""


def _read_json(path: Path, label: str) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExploratoryExportError(f"cannot read {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ExploratoryExportError(f"{label} must be a JSON object")
    return payload


def _read_csv(path: Path, label: str) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = list(reader.fieldnames or [])
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ExploratoryExportError(f"cannot read {label}: {exc}") from exc
    return headers, rows


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ExploratoryExportError(f"cannot hash source {path}: {exc}") from exc


def _validate_control_boundary(root: Path) -> None:
    state = _read_json(root / STATE_PATH, "canonical program state")
    for field, expected in REQUIRED_STATE.items():
        actual = state.get(field)
        if actual != expected:
            raise ExploratoryExportError(f"canonical {field} expected {expected}, got {actual}")
    try:
        charter = (root / CHARTER_PATH).read_text(encoding="utf-8").lower()
    except OSError as exc:
        raise ExploratoryExportError(f"cannot read program charter: {exc}") from exc
    required_phrases = ("final author order", "corresponding-author", "affiliation wording", "remain deferred")
    if not all(phrase in charter for phrase in required_phrases):
        raise ExploratoryExportError("program charter does not preserve the required author metadata deferral")


def _manifest_entry(root: Path) -> dict[str, object]:
    manifest = _read_json(root / EXPERIMENT_MANIFEST_PATH, "experiment manifest")
    for field, expected in REQUIRED_BOUNDARY.items():
        actual = manifest.get(field)
        if actual != expected:
            raise ExploratoryExportError(f"experiment manifest {field} expected {expected}, got {actual}")
    outputs = manifest.get("outputs")
    datasets = outputs.get("datasets") if isinstance(outputs, dict) else None
    if not isinstance(datasets, list):
        raise ExploratoryExportError("experiment manifest lacks outputs.datasets")
    matches = [item for item in datasets if isinstance(item, dict) and item.get("path") == SOURCE_PATH.as_posix()]
    if len(matches) != 1:
        raise ExploratoryExportError("experiment manifest must contain exactly one Markov source entry")
    return matches[0]


def _validate_lineage(root: Path, expected_hash: str) -> None:
    _, provenance = _read_csv(root / PROVENANCE_PATH, "provenance manifest")
    assets = [row for row in provenance if row.get("asset_id") == ASSET_ID]
    if len(assets) != 1:
        raise ExploratoryExportError(f"provenance manifest must contain exactly one {ASSET_ID} row")
    asset = assets[0]
    if asset.get("source") != SOURCE_PATH.as_posix():
        raise ExploratoryExportError("provenance source path does not match the Markov dataset")
    if asset.get("sha256") != expected_hash:
        raise ExploratoryExportError("provenance source hash does not match the Markov dataset")
    if asset.get("authorization") != "PREAUTHORIZATION_ONLY / NOT_SCIENTIFIC_EVIDENCE":
        raise ExploratoryExportError("provenance authorization boundary is not fail-closed")

    _, evidence_rows = _read_csv(root / EVIDENCE_PATH, "evidence status ledger")
    matches = [row for row in evidence_rows if row.get("evidence_id") == EVIDENCE_ID]
    if len(matches) != 1:
        raise ExploratoryExportError(f"evidence ledger must contain exactly one {EVIDENCE_ID} row")
    evidence = matches[0]
    required = {
        "claim_ids": "C003",
        "origin": "SIMULATED",
        "maturity": "V2 SIMULATED",
        "status": "PARTIAL",
        "authorized": "false",
        "independent": "false",
        "source_artifact": "04-data/provenance-manifest.csv",
        "authorization": "PREAUTHORIZATION_ONLY",
    }
    for field, expected in required.items():
        actual = evidence.get(field)
        if actual != expected:
            raise ExploratoryExportError(f"evidence {field} expected {expected}, got {actual}")
    asset_ids = set((evidence.get("source_asset_ids") or "").split("|"))
    if ASSET_ID not in asset_ids:
        raise ExploratoryExportError(f"evidence {EVIDENCE_ID} does not reference {ASSET_ID}")


def _decimal(value: str, field: str, row_number: int) -> Decimal:
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ExploratoryExportError(f"source row {row_number} has invalid {field}") from exc
    if not result.is_finite():
        raise ExploratoryExportError(f"source row {row_number} has non-finite {field}")
    return result


def _validate_source(root: Path, entry: dict[str, object]) -> list[dict[str, str]]:
    source = root / SOURCE_PATH
    actual_hash = _sha256(source)
    expected_hash = entry.get("sha256")
    if expected_hash != actual_hash:
        raise ExploratoryExportError(f"source hash mismatch: expected {expected_hash}, got {actual_hash}")
    headers, rows = _read_csv(source, "Markov temporal dataset")
    if headers != list(SOURCE_FIELDS):
        raise ExploratoryExportError("Markov source columns do not match the frozen manifest schema")
    if entry.get("columns") != list(SOURCE_FIELDS):
        raise ExploratoryExportError("experiment manifest columns do not match the frozen Markov schema")
    if entry.get("row_count") != len(rows):
        raise ExploratoryExportError("experiment manifest row count does not match the Markov source")
    if not rows:
        raise ExploratoryExportError("Markov source has no exploratory rows")

    previous_audits = 0
    for row_number, row in enumerate(rows, start=2):
        try:
            audits = int(row["audits"])
            trials = int(row["trials"])
            final_catastrophic = int(row["final_catastrophic_trials"])
            joint_count = int(row["all_audits_pass_and_final_catastrophic_count"])
            int(row["seed"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ExploratoryExportError(f"source row {row_number} has invalid integer fields") from exc
        if audits <= previous_audits or trials <= 0 or not (0 <= joint_count <= final_catastrophic <= trials):
            raise ExploratoryExportError(f"source row {row_number} violates count or audit-order invariants")
        previous_audits = audits
        rate = _decimal(row["conditional_sequence_false_accept_rate"], "effect estimate", row_number)
        low = _decimal(row["conditional_sequence_false_accept_ci_low"], "CI low", row_number)
        high = _decimal(row["conditional_sequence_false_accept_ci_high"], "CI high", row_number)
        bound = _decimal(row["static_set_repeated_bound"], "static comparison", row_number)
        if not (Decimal(0) <= low <= rate <= high <= Decimal(1)) or not (Decimal(0) <= bound <= Decimal(1)):
            raise ExploratoryExportError(f"source row {row_number} violates probability or interval invariants")
        computed = Decimal(joint_count) / Decimal(final_catastrophic) if final_catastrophic else Decimal(0)
        if abs(computed - rate) > Decimal("1e-15"):
            raise ExploratoryExportError(f"source row {row_number} effect estimate does not match its conditional denominator")

    _validate_lineage(root, actual_hash)
    return rows


def _output_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in rows:
        audits = row["audits"]
        output.append(
            {
                "finding_id": f"EXPLORE-MARKOV-AUDITS-{audits}",
                "claim_id": "C003",
                "evidence_ids": EVIDENCE_ID,
                "source_asset_id": ASSET_ID,
                "source_path": SOURCE_PATH.as_posix(),
                "analysis_class": "EXPLORATORY_POST_HOC_PREAUTHORIZATION",
                "estimand": "Conditional probability that all routine audits pass given a final catastrophic state in the frozen Markov simulation",
                "condition": (
                    f"audits={audits}; trials={row['trials']}; online_to_offline={row['online_to_offline']}; "
                    f"offline_to_online={row['offline_to_online']}; final_catastrophic_trials={row['final_catastrophic_trials']}; "
                    f"joint_count={row['all_audits_pass_and_final_catastrophic_count']}"
                ),
                "effect_estimate": row["conditional_sequence_false_accept_rate"],
                "uncertainty_interval": (
                    f"[{row['conditional_sequence_false_accept_ci_low']}, "
                    f"{row['conditional_sequence_false_accept_ci_high']}]"
                ),
                "sample_size": row["final_catastrophic_trials"],
                "seed": row["seed"],
                "comparison": row["static_set_repeated_bound"],
                "analysis_status": "EXPLORATORY_ONLY",
                "authorized": "false",
                "independent": "false",
                "evidence_origin": "SIMULATED",
                "evidence_maturity": "V2 SIMULATED",
                "claim_ceiling": "V0 ASSERTED",
                "interpretation_boundary": (
                    "Temporal-dependence exploration only; the conditional Markov estimate is not interchangeable "
                    "with the static repeated bound or distributed deadline behavior."
                ),
                "excluded_generality": (
                    "No production, external, field, unconditional future-availability, or universal security claim."
                ),
                "notes": (
                    "Descriptive comparison only; no hypothesis test or confirmatory inference. "
                    "The conditional denominator is final_catastrophic_trials, not total trials."
                ),
            }
        )
    return output


def _render(rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def export(root: Path, check: bool) -> None:
    _validate_control_boundary(root)
    entry = _manifest_entry(root)
    rows = _validate_source(root, entry)
    rendered = _render(_output_rows(rows))
    output = root / OUTPUT_PATH
    if check:
        try:
            existing = output.read_bytes()
        except OSError as exc:
            raise ExploratoryExportError(f"cannot read exploratory findings output: {exc}") from exc
        if existing != rendered:
            raise ExploratoryExportError("exploratory findings output is stale")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(rendered)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        export(args.root.resolve(), args.check)
    except ExploratoryExportError as exc:
        print(f"exploratory findings export failed: {exc}", file=sys.stderr)
        return 1
    action = "verified" if args.check else "wrote"
    print(f"{action} {OUTPUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
