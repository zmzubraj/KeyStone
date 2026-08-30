#!/usr/bin/env python3
"""Export bounded preauthorization simulation robustness and boundary rows."""

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
EXPERIMENT_MANIFEST_PATH = Path("prototype/results/experiment_manifest.json")
PROVENANCE_PATH = Path("research-case/04-data/provenance-manifest.csv")
EVIDENCE_PATH = Path("research-case/04-data/evidence-status.csv")
OUTPUT_PATH = Path("research-case/05-analysis/results/robustness-and-boundaries.csv")

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
FORBIDDEN_ASSETS = {
    "ASSET-DOMAIN-DIVERSITY",
    "ASSET-MARKOV-TEMPORAL-DEPENDENCE",
    "ASSET-SELECTIVE-WITHHOLDING",
    "ASSET-DEADLINE",
}
OUTPUT_FIELDS = (
    "robustness_id",
    "claim_ids",
    "evidence_ids",
    "source_asset_id",
    "source_path",
    "experiment_id",
    "analysis_class",
    "boundary_axis",
    "condition",
    "result",
    "uncertainty",
    "comparison",
    "sample_size",
    "seed",
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

SOURCE_SPECS = (
    {
        "label": "IID failure sweep",
        "path": Path("prototype/results/iid_failure_sweep.csv"),
        "asset_id": "ASSET-IID-FAILURE-SWEEP",
        "evidence_id": "RID-C003-IID-001",
        "experiment_id": "EXP-IID-FAILURE-SWEEP",
        "kind": "SEEDED_MONTE_CARLO",
        "fields": (
            "offline_probability",
            "reconstruction_success_rate",
            "reconstruction_success_ci_low",
            "reconstruction_success_ci_high",
            "audit_pass_rate",
            "audit_pass_ci_low",
            "audit_pass_ci_high",
            "catastrophic_detection_rate",
            "catastrophic_trials",
        ),
    },
    {
        "label": "sampling strategy",
        "path": Path("prototype/results/sampling_strategy.csv"),
        "asset_id": "ASSET-SAMPLING-STRATEGY",
        "evidence_id": "RID-C003-STRAT-001",
        "experiment_id": "EXP-SAMPLING-STRATEGY",
        "kind": "SEEDED_MATCHED_POLICY_MONTE_CARLO",
        "fields": (
            "sample_size",
            "strategy",
            "catastrophic_detection_rate",
            "catastrophic_detection_ci_low",
            "catastrophic_detection_ci_high",
            "catastrophic_trials",
            "audit_pass_rate",
            "audit_pass_ci_low",
            "audit_pass_ci_high",
        ),
    },
)


class RobustnessBoundaryError(RuntimeError):
    """Raised when a bounded robustness ledger cannot be exported safely."""


def _read_json(path: Path, label: str) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RobustnessBoundaryError(f"cannot read {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RobustnessBoundaryError(f"{label} must be a JSON object")
    return payload


def _read_csv(path: Path, label: str) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return list(reader.fieldnames or []), list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise RobustnessBoundaryError(f"cannot read {label}: {exc}") from exc


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise RobustnessBoundaryError(f"cannot hash source {path}: {exc}") from exc


def _decimal(value: str, field: str, row_number: int) -> Decimal:
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise RobustnessBoundaryError(f"source row {row_number} has invalid {field}") from exc
    if not result.is_finite():
        raise RobustnessBoundaryError(f"source row {row_number} has non-finite {field}")
    return result


def _integer(value: str, field: str, row_number: int) -> int:
    number = _decimal(value, field, row_number)
    if number != number.to_integral_value() or number < 0:
        raise RobustnessBoundaryError(f"source row {row_number} has invalid integer {field}")
    return int(number)


def _rate(row: dict[str, str], field: str, row_number: int) -> Decimal:
    value = _decimal(row[field], field, row_number)
    if value < 0 or value > 1:
        raise RobustnessBoundaryError(f"source row {row_number} {field} is outside [0,1]")
    return value


def _interval(row: dict[str, str], stem: str, row_number: int) -> None:
    value = _rate(row, stem, row_number)
    interval_stem = stem.removesuffix("_rate")
    low = _rate(row, f"{interval_stem}_ci_low", row_number)
    high = _rate(row, f"{interval_stem}_ci_high", row_number)
    if not low <= value <= high:
        raise RobustnessBoundaryError(f"source row {row_number} invalid interval for {stem}")


def _validate_control_boundary(root: Path) -> None:
    state = _read_json(root / STATE_PATH, "canonical program state")
    for field, expected in REQUIRED_STATE.items():
        actual = state.get(field)
        if actual != expected:
            raise RobustnessBoundaryError(f"canonical {field} expected {expected}, got {actual}")
    if "feasibility_decision" in state and state.get("feasibility_decision") != "UNASSESSED":
        raise RobustnessBoundaryError("canonical feasibility_decision expected UNASSESSED")
    try:
        charter = (root / CHARTER_PATH).read_text(encoding="utf-8").lower()
    except OSError as exc:
        raise RobustnessBoundaryError(f"cannot read program charter: {exc}") from exc
    required = ("final author order", "corresponding-author", "affiliation wording", "remain deferred")
    if not all(phrase in charter for phrase in required):
        raise RobustnessBoundaryError("program charter does not preserve author metadata deferral")


def _manifest_contract(root: Path) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    manifest = _read_json(root / EXPERIMENT_MANIFEST_PATH, "experiment manifest")
    for field, expected in REQUIRED_BOUNDARY.items():
        actual = manifest.get(field)
        if actual != expected:
            raise RobustnessBoundaryError(f"experiment manifest {field} expected {expected}, got {actual}")
    outputs = manifest.get("outputs")
    datasets = outputs.get("datasets") if isinstance(outputs, dict) else None
    experiments = manifest.get("experiments")
    if not isinstance(datasets, list) or not all(isinstance(item, dict) for item in datasets):
        raise RobustnessBoundaryError("experiment manifest lacks valid outputs.datasets")
    if not isinstance(experiments, list) or not all(isinstance(item, dict) for item in experiments):
        raise RobustnessBoundaryError("experiment manifest lacks valid experiments")
    return manifest, datasets, experiments


def _unique(items: list[dict[str, object]], field: str, value: str, label: str) -> dict[str, object]:
    matches = [item for item in items if item.get(field) == value]
    if len(matches) != 1:
        raise RobustnessBoundaryError(f"{label} must contain exactly one {value} entry")
    return matches[0]


def _validate_dataset_entry(
    root: Path,
    datasets: list[dict[str, object]],
    spec: dict[str, object],
) -> tuple[list[dict[str, str]], dict[str, object]]:
    source_path = spec["path"]
    assert isinstance(source_path, Path)
    entry = _unique(datasets, "path", source_path.as_posix(), "experiment manifest datasets")
    fields, rows = _read_csv(root / source_path, str(spec["label"]))
    expected_fields = list(spec["fields"])
    if fields != expected_fields:
        raise RobustnessBoundaryError(f"{spec['label']} source schema mismatch")
    if entry.get("columns") != expected_fields:
        raise RobustnessBoundaryError(f"{spec['label']} manifest columns mismatch")
    if entry.get("row_count") != len(rows):
        raise RobustnessBoundaryError(f"{spec['label']} manifest row_count mismatch")
    digest = _sha256(root / source_path)
    if entry.get("sha256") != digest:
        raise RobustnessBoundaryError(f"{spec['label']} source hash mismatch")
    if not rows:
        raise RobustnessBoundaryError(f"{spec['label']} source must not be empty")
    return rows, entry


def _validate_provenance_and_evidence(root: Path, spec: dict[str, object], digest: str) -> None:
    _, provenance_rows = _read_csv(root / PROVENANCE_PATH, "provenance manifest")
    provenance = [row for row in provenance_rows if row.get("asset_id") == spec["asset_id"]]
    if len(provenance) != 1:
        raise RobustnessBoundaryError(f"provenance must contain exactly one {spec['asset_id']} row")
    row = provenance[0]
    expected_path = spec["path"]
    assert isinstance(expected_path, Path)
    if row.get("source") != expected_path.as_posix() or row.get("sha256") != digest:
        raise RobustnessBoundaryError(f"provenance binding mismatch for {spec['asset_id']}")
    if row.get("authorization") != "PREAUTHORIZATION_ONLY / NOT_SCIENTIFIC_EVIDENCE":
        raise RobustnessBoundaryError(f"provenance authorization mismatch for {spec['asset_id']}")

    _, evidence_rows = _read_csv(root / EVIDENCE_PATH, "evidence status")
    evidence = [item for item in evidence_rows if item.get("evidence_id") == spec["evidence_id"]]
    if len(evidence) != 1:
        raise RobustnessBoundaryError(f"evidence status must contain exactly one {spec['evidence_id']} row")
    item = evidence[0]
    required = {
        "claim_ids": "C003",
        "origin": "SIMULATED",
        "maturity": "V2 SIMULATED",
        "scope": "SIMULATED",
        "status": "PARTIAL",
        "authorized": "false",
        "independent": "false",
        "source_artifact": "04-data/provenance-manifest.csv",
        "authorization": "PREAUTHORIZATION_ONLY",
    }
    for field, expected in required.items():
        actual = item.get(field)
        if actual != expected:
            raise RobustnessBoundaryError(
                f"evidence {field} expected {expected}, got {actual} for {spec['evidence_id']}"
            )
    asset_ids = set((item.get("source_asset_ids") or "").split("|"))
    if spec["asset_id"] not in asset_ids:
        raise RobustnessBoundaryError(f"evidence does not bind {spec['asset_id']}")
    forbidden = asset_ids & FORBIDDEN_ASSETS
    if forbidden:
        raise RobustnessBoundaryError(
            f"evidence binding includes excluded assets for {spec['evidence_id']}: {sorted(forbidden)}"
        )


def _validate_common_parameters(parameters: dict[str, object], label: str) -> None:
    expected = {"n": 32, "threshold": 22}
    for field, value in expected.items():
        if parameters.get(field) != value:
            raise RobustnessBoundaryError(f"{label} parameter {field} expected {value}")
    trials = parameters.get("trials_per_scenario")
    if not isinstance(trials, int) or trials <= 0:
        raise RobustnessBoundaryError(f"{label} trials_per_scenario must be a positive integer")


def _validate_iid(rows: list[dict[str, str]], experiment: dict[str, object]) -> list[dict[str, str]]:
    parameters = experiment.get("parameters")
    if not isinstance(parameters, dict):
        raise RobustnessBoundaryError("IID experiment parameters missing")
    _validate_common_parameters(parameters, "IID")
    required = {
        "sample_size": 8,
        "required_audit_responses": 8,
        "domains": 4,
        "domain_outage_probability": 0.0,
    }
    for field, expected in required.items():
        if parameters.get(field) != expected:
            raise RobustnessBoundaryError(f"IID parameter {field} expected {expected}")
    declared = parameters.get("independent_offline_probabilities")
    seeds = parameters.get("seeds")
    if not isinstance(declared, list) or not isinstance(seeds, list) or len(declared) != len(rows) or len(seeds) != len(rows):
        raise RobustnessBoundaryError("IID probability and seed mapping length mismatch")
    actual: list[float] = []
    previous: Decimal | None = None
    for number, row in enumerate(rows, start=2):
        probability = _decimal(row["offline_probability"], "offline_probability", number)
        if probability < 0 or probability > 1 or (previous is not None and probability <= previous):
            raise RobustnessBoundaryError("IID offline probabilities must be strictly increasing within [0,1]")
        previous = probability
        actual.append(float(probability))
        _interval(row, "reconstruction_success_rate", number)
        _interval(row, "audit_pass_rate", number)
        _rate(row, "catastrophic_detection_rate", number)
        _integer(row["catastrophic_trials"], "catastrophic_trials", number)
    if actual != declared or not all(isinstance(seed, int) for seed in seeds):
        raise RobustnessBoundaryError("IID probability or seed mapping does not match source order")
    return rows


def _validate_sampling(rows: list[dict[str, str]], experiment: dict[str, object]) -> list[dict[str, str]]:
    parameters = experiment.get("parameters")
    if not isinstance(parameters, dict):
        raise RobustnessBoundaryError("sampling experiment parameters missing")
    _validate_common_parameters(parameters, "sampling")
    required = {
        "domains": 4,
        "domain_outage_probability": 0.2,
        "independent_offline_probability": 0.01,
        "required_audit_responses_rule": "sample_size",
        "seed_rule": "5500 + sample_size; shared by both strategies",
    }
    for field, expected in required.items():
        if parameters.get(field) != expected:
            raise RobustnessBoundaryError(f"sampling parameter {field} expected {expected}")
    sample_sizes = parameters.get("sample_sizes")
    strategies = parameters.get("strategies")
    seeds = parameters.get("seeds")
    if not isinstance(sample_sizes, list) or not all(isinstance(value, int) and value > 0 for value in sample_sizes):
        raise RobustnessBoundaryError("sampling sample_sizes must be positive integers")
    if strategies != ["uniform", "stratified"]:
        raise RobustnessBoundaryError("sampling strategies must be uniform and stratified")
    if not isinstance(seeds, list) or len(seeds) != len(sample_sizes):
        raise RobustnessBoundaryError("sampling seed mapping length mismatch")
    if seeds != [5500 + value for value in sample_sizes]:
        raise RobustnessBoundaryError("sampling seed mapping does not follow the declared rule")
    expected_cells = [(size, strategy) for size in sample_sizes for strategy in strategies]
    actual_cells: list[tuple[int, str]] = []
    for number, row in enumerate(rows, start=2):
        size = _integer(row["sample_size"], "sample_size", number)
        strategy = row["strategy"]
        actual_cells.append((size, strategy))
        _interval(row, "catastrophic_detection_rate", number)
        _interval(row, "audit_pass_rate", number)
        _integer(row["catastrophic_trials"], "catastrophic_trials", number)
    if actual_cells != expected_cells:
        raise RobustnessBoundaryError("sampling source cells do not match the declared sample-size/strategy order")
    return rows


def _base_row(spec: dict[str, object], experiment: dict[str, object], seed: int) -> dict[str, str]:
    source_path = spec["path"]
    assert isinstance(source_path, Path)
    parameters = experiment["parameters"]
    assert isinstance(parameters, dict)
    return {
        "claim_ids": "C003",
        "evidence_ids": str(spec["evidence_id"]),
        "source_asset_id": str(spec["asset_id"]),
        "source_path": source_path.as_posix(),
        "experiment_id": str(spec["experiment_id"]),
        "analysis_class": "PREAUTHORIZATION_SIMULATION_ROBUSTNESS_OR_BOUNDARY",
        "sample_size": str(parameters["trials_per_scenario"]),
        "seed": str(seed),
        "analysis_status": "DRAFT_ROBUSTNESS_BOUNDARY_ONLY",
        "authorized": "false",
        "independent": "false",
        "evidence_origin": "SIMULATED",
        "evidence_maturity": "V2 SIMULATED",
        "claim_ceiling": "V0 ASSERTED",
        "excluded_generality": (
            "No production, field, external-replication, deadline, universal-security, or deployment claim."
        ),
        "notes": (
            "Descriptive frozen preauthorization simulation row only; Monte Carlo trials per scenario are recorded "
            "in sample_size; no hypothesis test, confirmatory inference, gate promotion, or author-metadata freeze."
        ),
    }


def _iid_output(spec: dict[str, object], rows: list[dict[str, str]], experiment: dict[str, object]) -> list[dict[str, str]]:
    parameters = experiment["parameters"]
    assert isinstance(parameters, dict)
    seeds = parameters["seeds"]
    assert isinstance(seeds, list)
    output: list[dict[str, str]] = []
    for row, seed in zip(rows, seeds, strict=True):
        probability = _decimal(row["offline_probability"], "offline_probability", 0)
        identifier = int(probability * 1000)
        item = _base_row(spec, experiment, seed)
        item.update(
            {
                "robustness_id": f"ROB-IID-{identifier:04d}",
                "boundary_axis": "iid_offline_probability",
                "condition": (
                    f"offline_probability={row['offline_probability']}; n=32; threshold=22; "
                    "audit_sample_size=8; required_audit_responses=8; domains=4; domain_outage_probability=0.0"
                ),
                "result": (
                    f"reconstruction_success_rate={row['reconstruction_success_rate']}; "
                    f"audit_pass_rate={row['audit_pass_rate']}; "
                    f"catastrophic_detection_rate={row['catastrophic_detection_rate']}; "
                    f"catastrophic_trials={row['catastrophic_trials']}"
                ),
                "uncertainty": (
                    f"reconstruction_ci=[{row['reconstruction_success_ci_low']}, {row['reconstruction_success_ci_high']}]; "
                    f"audit_pass_ci=[{row['audit_pass_ci_low']}, {row['audit_pass_ci_high']}]; "
                    "no detection CI is present in the frozen source"
                ),
                "comparison": "descriptive IID sweep cell; no synthesized contrast or inferential comparison",
                "interpretation_boundary": (
                    "IID outage sweep only; correlated, temporal, targeted-withholding, deadline, and deployed behavior are excluded."
                ),
            }
        )
        output.append(item)
    return output


def _sampling_output(spec: dict[str, object], rows: list[dict[str, str]], experiment: dict[str, object]) -> list[dict[str, str]]:
    parameters = experiment["parameters"]
    assert isinstance(parameters, dict)
    sample_sizes = parameters["sample_sizes"]
    seeds = parameters["seeds"]
    assert isinstance(sample_sizes, list) and isinstance(seeds, list)
    seed_by_size = dict(zip(sample_sizes, seeds, strict=True))
    output: list[dict[str, str]] = []
    for row in rows:
        size = int(row["sample_size"])
        strategy = row["strategy"]
        item = _base_row(spec, experiment, seed_by_size[size])
        item.update(
            {
                "robustness_id": f"ROB-SAMPLING-{size:02d}-{strategy.upper()}",
                "boundary_axis": "sampling_policy_and_audit_sample_size",
                "condition": (
                    f"audit_sample_size={size}; strategy={strategy}; n=32; threshold=22; domains=4; "
                    "domain_outage_probability=0.2; independent_offline_probability=0.01; "
                    f"required_audit_responses={size}"
                ),
                "result": (
                    f"catastrophic_detection_rate={row['catastrophic_detection_rate']}; "
                    f"catastrophic_trials={row['catastrophic_trials']}; audit_pass_rate={row['audit_pass_rate']}"
                ),
                "uncertainty": (
                    f"catastrophic_detection_ci=[{row['catastrophic_detection_ci_low']}, "
                    f"{row['catastrophic_detection_ci_high']}]; audit_pass_ci=[{row['audit_pass_ci_low']}, "
                    f"{row['audit_pass_ci_high']}]"
                ),
                "comparison": "uniform versus stratified under the declared matched seed schedule",
                "interpretation_boundary": (
                    "Matched-seed descriptive comparison of the declared policies only; it does not establish "
                    "policy optimality, independent replication, or robustness outside evaluated cells."
                ),
            }
        )
        output.append(item)
    return output


def _render(rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def export(root: Path, check: bool) -> None:
    _validate_control_boundary(root)
    _, datasets, experiments = _manifest_contract(root)
    output_rows: list[dict[str, str]] = []
    for spec in SOURCE_SPECS:
        source_rows, dataset = _validate_dataset_entry(root, datasets, spec)
        _validate_provenance_and_evidence(root, spec, str(dataset["sha256"]))
        experiment = _unique(experiments, "experiment_id", str(spec["experiment_id"]), "experiment manifest")
        if experiment.get("kind") != spec["kind"]:
            raise RobustnessBoundaryError(
                f"experiment kind expected {spec['kind']}, got {experiment.get('kind')} for {spec['experiment_id']}"
            )
        source_path = spec["path"]
        assert isinstance(source_path, Path)
        if experiment.get("datasets") != [source_path.as_posix()]:
            raise RobustnessBoundaryError(f"experiment {spec['experiment_id']} does not bind only {source_path}")
        if spec["experiment_id"] == "EXP-IID-FAILURE-SWEEP":
            output_rows.extend(_iid_output(spec, _validate_iid(source_rows, experiment), experiment))
        elif spec["experiment_id"] == "EXP-SAMPLING-STRATEGY":
            output_rows.extend(_sampling_output(spec, _validate_sampling(source_rows, experiment), experiment))
        else:
            raise RobustnessBoundaryError(f"unsupported experiment {spec['experiment_id']}")

    rendered = _render(output_rows)
    output = root / OUTPUT_PATH
    if check:
        try:
            existing = output.read_bytes()
        except OSError as exc:
            raise RobustnessBoundaryError(f"cannot read robustness-and-boundaries output: {exc}") from exc
        if existing != rendered:
            raise RobustnessBoundaryError("robustness-and-boundaries output is stale")
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
    except RobustnessBoundaryError as exc:
        print(f"robustness-and-boundaries export failed: {exc}", file=sys.stderr)
        return 1
    action = "verified" if args.check else "wrote"
    print(f"{action} {OUTPUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
