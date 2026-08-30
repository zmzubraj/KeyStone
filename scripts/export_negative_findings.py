#!/usr/bin/env python3
"""Export the frozen selective-withholding result as a bounded draft negative ledger."""

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
SOURCE_PATH = Path("prototype/results/selective_withholding.csv")
EXPERIMENT_MANIFEST_PATH = Path("prototype/results/experiment_manifest.json")
PROVENANCE_PATH = Path("research-case/04-data/provenance-manifest.csv")
EVIDENCE_PATH = Path("research-case/04-data/evidence-status.csv")
OUTPUT_PATH = Path("research-case/05-analysis/results/negative-findings.csv")

ASSET_ID = "ASSET-SELECTIVE-WITHHOLDING"
EVIDENCE_ID = "RID-C003-SW-001"
EXPERIMENT_ID = "EXP-SELECTIVE-WITHHOLDING"
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
    "selective_withholders",
    "reconstruction_success_rate",
    "reconstruction_success_ci_low",
    "reconstruction_success_ci_high",
    "audit_pass_rate",
    "audit_pass_ci_low",
    "audit_pass_ci_high",
)
OUTPUT_FIELDS = (
    "finding_id",
    "claim_ids",
    "evidence_ids",
    "source_asset_id",
    "source_path",
    "analysis_class",
    "test",
    "result",
    "uncertainty",
    "implication",
    "condition",
    "sample_size",
    "seed",
    "analysis_status",
    "authorized",
    "independent",
    "evidence_origin",
    "evidence_maturity",
    "claim_ceiling",
    "excluded_generality",
    "notes",
)


class NegativeFindingError(RuntimeError):
    """Raised when the negative result cannot be exported without overclaiming."""


def _read_json(path: Path, label: str) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise NegativeFindingError(f"cannot read {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise NegativeFindingError(f"{label} must be a JSON object")
    return payload


def _read_csv(path: Path, label: str) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return list(reader.fieldnames or []), list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise NegativeFindingError(f"cannot read {label}: {exc}") from exc


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise NegativeFindingError(f"cannot hash source {path}: {exc}") from exc


def _decimal(value: str, field: str, row_number: int) -> Decimal:
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise NegativeFindingError(f"source row {row_number} has invalid {field}") from exc
    if not result.is_finite():
        raise NegativeFindingError(f"source row {row_number} has non-finite {field}")
    return result


def _validate_control_boundary(root: Path) -> None:
    state = _read_json(root / STATE_PATH, "canonical program state")
    for field, expected in REQUIRED_STATE.items():
        actual = state.get(field)
        if actual != expected:
            raise NegativeFindingError(f"canonical {field} expected {expected}, got {actual}")
    try:
        charter = (root / CHARTER_PATH).read_text(encoding="utf-8").lower()
    except OSError as exc:
        raise NegativeFindingError(f"cannot read program charter: {exc}") from exc
    required = ("final author order", "corresponding-author", "affiliation wording", "remain deferred")
    if not all(phrase in charter for phrase in required):
        raise NegativeFindingError("program charter does not preserve author metadata deferral")


def _manifest_contract(root: Path) -> tuple[dict[str, object], dict[str, object]]:
    manifest = _read_json(root / EXPERIMENT_MANIFEST_PATH, "experiment manifest")
    for field, expected in REQUIRED_BOUNDARY.items():
        actual = manifest.get(field)
        if actual != expected:
            raise NegativeFindingError(f"experiment manifest {field} expected {expected}, got {actual}")
    outputs = manifest.get("outputs")
    datasets = outputs.get("datasets") if isinstance(outputs, dict) else None
    if not isinstance(datasets, list):
        raise NegativeFindingError("experiment manifest lacks outputs.datasets")
    entries = [item for item in datasets if isinstance(item, dict) and item.get("path") == SOURCE_PATH.as_posix()]
    if len(entries) != 1:
        raise NegativeFindingError("experiment manifest must contain exactly one selective-withholding dataset")
    experiments = manifest.get("experiments")
    matches = [item for item in experiments if isinstance(item, dict) and item.get("experiment_id") == EXPERIMENT_ID] if isinstance(experiments, list) else []
    if len(matches) != 1:
        raise NegativeFindingError(f"experiment manifest must contain exactly one {EXPERIMENT_ID}")
    experiment = matches[0]
    if experiment.get("kind") != "SEEDED_MONTE_CARLO_NEGATIVE_RESULT":
        raise NegativeFindingError("experiment kind must remain SEEDED_MONTE_CARLO_NEGATIVE_RESULT")
    experiment_datasets = experiment.get("datasets")
    if not isinstance(experiment_datasets, list) or SOURCE_PATH.as_posix() not in experiment_datasets:
        raise NegativeFindingError("negative-result experiment does not bind the selective-withholding dataset")
    return entries[0], experiment


def _validate_lineage(root: Path, source_hash: str) -> None:
    _, provenance = _read_csv(root / PROVENANCE_PATH, "provenance manifest")
    rows = [row for row in provenance if row.get("asset_id") == ASSET_ID]
    if len(rows) != 1:
        raise NegativeFindingError(f"provenance manifest must contain exactly one {ASSET_ID}")
    asset = rows[0]
    if asset.get("source") != SOURCE_PATH.as_posix() or asset.get("sha256") != source_hash:
        raise NegativeFindingError("provenance path or source hash does not match selective-withholding data")
    if asset.get("authorization") != "PREAUTHORIZATION_ONLY / NOT_SCIENTIFIC_EVIDENCE":
        raise NegativeFindingError("provenance authorization boundary is not fail-closed")

    _, evidence = _read_csv(root / EVIDENCE_PATH, "evidence status ledger")
    rows = [row for row in evidence if row.get("evidence_id") == EVIDENCE_ID]
    if len(rows) != 1:
        raise NegativeFindingError(f"evidence ledger must contain exactly one {EVIDENCE_ID}")
    row = rows[0]
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
        actual = row.get(field)
        if actual != expected:
            raise NegativeFindingError(f"evidence {field} expected {expected}, got {actual}")
    if ASSET_ID not in set((row.get("source_asset_ids") or "").split("|")):
        raise NegativeFindingError(f"evidence {EVIDENCE_ID} does not reference {ASSET_ID}")


def _validate_source(
    root: Path,
    dataset: dict[str, object],
    experiment: dict[str, object],
) -> tuple[list[dict[str, str]], int, list[int]]:
    source = root / SOURCE_PATH
    source_hash = _sha256(source)
    if dataset.get("sha256") != source_hash:
        raise NegativeFindingError(f"source hash mismatch: expected {dataset.get('sha256')}, got {source_hash}")
    headers, rows = _read_csv(source, "selective-withholding dataset")
    if headers != list(SOURCE_FIELDS) or dataset.get("columns") != list(SOURCE_FIELDS):
        raise NegativeFindingError("selective-withholding columns do not match the frozen schema")
    if dataset.get("row_count") != len(rows) or len(rows) != 15:
        raise NegativeFindingError("selective-withholding row count must remain 15")

    parameters = experiment.get("parameters")
    if not isinstance(parameters, dict):
        raise NegativeFindingError("negative-result experiment lacks parameters")
    expected_parameters = {
        "n": 32,
        "threshold": 22,
        "sample_size": 8,
        "required_audit_responses": 8,
        "selective_withholders": list(range(15)),
        "trials_per_scenario": 4000,
        "seeds": [4400 + value for value in range(15)],
    }
    for field, expected in expected_parameters.items():
        if parameters.get(field) != expected:
            raise NegativeFindingError(f"experiment parameter {field} expected {expected}, got {parameters.get(field)}")

    divergence = int(parameters["n"]) - int(parameters["threshold"]) + 1
    for row_number, row in enumerate(rows, start=2):
        try:
            withholders = int(row["selective_withholders"])
        except (KeyError, TypeError, ValueError) as exc:
            raise NegativeFindingError(f"source row {row_number} has invalid selective_withholders") from exc
        if withholders != row_number - 2:
            raise NegativeFindingError("selective-withholding rows must be ordered from 0 through 14")
        values = {
            field: _decimal(row[field], field, row_number)
            for field in SOURCE_FIELDS
            if field != "selective_withholders"
        }
        for prefix in ("reconstruction_success", "audit_pass"):
            low = values[f"{prefix}_ci_low"]
            rate = values[f"{prefix}_rate"]
            high = values[f"{prefix}_ci_high"]
            if not (Decimal(0) <= low <= rate <= high <= Decimal(1)):
                raise NegativeFindingError(f"source row {row_number} violates {prefix} probability bounds")
        expected_reconstruction = Decimal(0) if withholders >= divergence else Decimal(1)
        if values["audit_pass_rate"] != Decimal(1) or values["reconstruction_success_rate"] != expected_reconstruction:
            raise NegativeFindingError(f"source row {row_number} violates the frozen selective-withholding pattern")
        if withholders >= divergence and values["audit_pass_ci_low"] <= values["reconstruction_success_ci_high"]:
            raise NegativeFindingError(f"source row {row_number} does not establish an interval-separated negative gap")

    _validate_lineage(root, source_hash)
    return rows, int(parameters["trials_per_scenario"]), list(parameters["seeds"])


def _output_rows(rows: list[dict[str, str]], trials: int, seeds: list[int]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        withholders = int(row["selective_withholders"])
        if row["audit_pass_ci_low"] <= row["reconstruction_success_ci_high"]:
            continue
        output.append(
            {
                "finding_id": f"NEG-SW-{withholders}",
                "claim_ids": "C003",
                "evidence_ids": EVIDENCE_ID,
                "source_asset_id": ASSET_ID,
                "source_path": SOURCE_PATH.as_posix(),
                "analysis_class": "PREAUTHORIZATION_SIMULATION_NEGATIVE_FINDING",
                "test": "routine audit pass versus targeted dispute reconstruction",
                "result": (
                    f"audit_pass_rate={row['audit_pass_rate']}; "
                    f"reconstruction_success_rate={row['reconstruction_success_rate']}"
                ),
                "uncertainty": (
                    f"audit=[{row['audit_pass_ci_low']}, {row['audit_pass_ci_high']}]; "
                    f"reconstruction=[{row['reconstruction_success_ci_low']}, {row['reconstruction_success_ci_high']}]"
                ),
                "implication": "Routine canary-audit success does not imply targeted dispute reconstruction under the frozen selective-withholding adversary.",
                "condition": f"n=32; threshold=22; sample_size=8; required_audit_responses=8; selective_withholders={withholders}",
                "sample_size": str(trials),
                "seed": str(seeds[index]),
                "analysis_status": "DRAFT_NEGATIVE_FINDING_ONLY",
                "authorized": "false",
                "independent": "false",
                "evidence_origin": "SIMULATED",
                "evidence_maturity": "V2 SIMULATED",
                "claim_ceiling": "V0 ASSERTED",
                "excluded_generality": "No production, external, field, deadline, adaptive-adversary, or universal security claim.",
                "notes": "Preserved limitation from a deterministic preauthorization pipeline; not an authorized confirmatory result.",
            }
        )
    if [row["finding_id"] for row in output] != ["NEG-SW-11", "NEG-SW-12", "NEG-SW-13", "NEG-SW-14"]:
        raise NegativeFindingError("negative gap rows do not match the frozen n-t+1 boundary")
    return output


def _render(rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def export(root: Path, check: bool) -> None:
    _validate_control_boundary(root)
    dataset, experiment = _manifest_contract(root)
    rows, trials, seeds = _validate_source(root, dataset, experiment)
    rendered = _render(_output_rows(rows, trials, seeds))
    output = root / OUTPUT_PATH
    if check:
        try:
            existing = output.read_bytes()
        except OSError as exc:
            raise NegativeFindingError(f"cannot read negative-findings output: {exc}") from exc
        if existing != rendered:
            raise NegativeFindingError("negative-findings output is stale")
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
    except NegativeFindingError as exc:
        print(f"negative findings export failed: {exc}", file=sys.stderr)
        return 1
    action = "verified" if args.check else "wrote"
    print(f"{action} {OUTPUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
