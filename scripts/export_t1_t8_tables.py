#!/usr/bin/env python3
"""Export the bounded KEYSTONE T1--T8 draft/preauthorization table package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


INPUT_PATHS = (
    "research-case/01-novelty/novelty-matrix.csv",
    "research-case/02-feasibility/risk-register.csv",
    "research-case/03-design/protocol.md",
    "research-case/03-design/analysis-plan.md",
    "research-case/04-data/evidence-status.csv",
    "research-case/05-analysis/results/exploratory-findings.csv",
    "research-case/05-analysis/results/negative-findings.csv",
    "research-case/05-analysis/results/robustness-and-boundaries.csv",
    "research-case/07-manuscript/claim-evidence-matrix.csv",
    "prototype/configs/baseline.json",
    "prototype/results/experiment_manifest.json",
    "prototype/results/baseline.json",
    "prototype/results/exact_stratified_validation.csv",
    "prototype/results/markov_temporal_dependence.csv",
    "prototype/results/selective_withholding.csv",
    "prototype/results/crypto_benchmark.csv",
    "contracts/gas_report.csv",
    "paper/tables/preauthorization_engineering_qa.csv",
)

TABLE_FILENAMES = {
    "T1": "t1_strongest_prior_art.csv",
    "T2": "t2_proposed_vs_baselines.csv",
    "T3": "t3_experimental_conditions.csv",
    "T4": "t4_primary_results.csv",
    "T5": "t5_ablation_mechanism.csv",
    "T6": "t6_robustness_boundaries.csv",
    "T7": "t7_real_world_feasibility.csv",
    "T8": "t8_negative_findings_risks.csv",
}

TABLE_DISPOSITIONS = {
    "T1": "bounded strongest-prior-art matrix only; not novelty clearance",
    "T2": "design comparator registry only; no measured superiority claim",
    "T3": "frozen local conditions plus explicit missing distributed deadline profile",
    "T4": "preauthorization simulated result display only; numeric values remain source-bound and claim-capped",
    "T5": "planned mechanism-isolation registry only; all rows missing and unexecuted",
    "T6": "canonical robustness ledger plus separately classified exact and exploratory checks",
    "T7": "local timing and gas observations only; distributed, operator, network, and external evidence blocked",
    "T8": "negative findings and unresolved risks ledger with selective withholding preserved",
}

ALLOWED_STAGES = {
    "DESIGN_ONLY",
    "PREAUTHORIZATION_SIMULATION_INPUT",
    "PREAUTHORIZATION_SIMULATED",
    "EXPLORATORY_PREAUTHORIZATION_SIMULATED",
    "NEGATIVE_FINDING_PREAUTHORIZATION_SIMULATED",
    "PREAUTHORIZATION_INTERNAL",
    "ANALYTIC_DRAFT",
    "MISSING_NOT_EXECUTED",
    "BLOCKED_EXTERNAL",
}

COMMON_HEADERS = ("claim_ids", "source_path", "evidence_stage", "claim_ceiling")

EXPECTED_HEADERS = {
    "T1": ("claim_id", "predecessor_id", "bounded_difference", "defeating_evidence", "residual_uncertainty", *COMMON_HEADERS),
    "T2": ("comparator_id", "comparator_class", "compared_property", "design_difference", "measured_superiority", *COMMON_HEADERS),
    "T3": ("condition_id", "n", "threshold", "sample_size", "required_responses", "offline_probability", "domain_outage_probability", "domains", "trials", "seed", "sampling_strategy", "selective_withholders", "environment_profile", *COMMON_HEADERS),
    "T4": ("result_id", "condition_id", "estimand", "estimate", "ci_low", "ci_high", "denominator", "trials", *COMMON_HEADERS),
    "T5": ("ablation_id", "planned_change", "mechanism_question", "execution_status", "estimate", *COMMON_HEADERS),
    "T6": ("check_id", "estimand", "condition", "estimate", "comparison", "uncertainty_or_error", "interpretation_boundary", *COMMON_HEADERS),
    "T7": ("evidence_id", "surface", "metric", "value", "unit", "scope_or_blocker", *COMMON_HEADERS),
    "T8": ("finding_id", "finding", "status", "consequence", "required_resolution", *COMMON_HEADERS),
}

PREAUTH_QA_HEADERS = (
    "family_id", "family", "result_id", "mapped_checks", "mapped_pass",
    "auxiliary_checks", "auxiliary_pass", "total_checks", "total_pass",
    "receipt_path", "receipt_sha256", "authorization_boundary",
    "evidence_boundary", "independence_boundary", "security_boundary",
    "gas_boundary", "residual_limitations",
)

SOURCE_HEADERS = {
    "research-case/01-novelty/novelty-matrix.csv": ("claim_id", "predecessor_id", "material_difference", "defeating_evidence", "residual_uncertainty"),
    "research-case/02-feasibility/risk-register.csv": ("risk_id", "category", "description", "likelihood", "impact", "status", "evidence_grade", "evidence_source", "owner", "mitigation", "verification", "related_claims", "trigger"),
    "research-case/04-data/evidence-status.csv": ("evidence_id", "claim_ids", "origin", "maturity", "scope", "status", "authorized", "independent", "source_artifact", "source_asset_ids", "authorization", "directness", "uncertainty", "tested_setting", "failure_envelope", "excluded_generality", "notes"),
    "research-case/05-analysis/results/exploratory-findings.csv": ("finding_id", "claim_id", "evidence_ids", "source_asset_id", "source_path", "analysis_class", "estimand", "condition", "effect_estimate", "uncertainty_interval", "sample_size", "seed", "comparison", "analysis_status", "authorized", "independent", "evidence_origin", "evidence_maturity", "claim_ceiling", "interpretation_boundary", "excluded_generality", "notes"),
    "research-case/05-analysis/results/negative-findings.csv": ("finding_id", "claim_ids", "evidence_ids", "source_asset_id", "source_path", "analysis_class", "test", "result", "uncertainty", "implication", "condition", "sample_size", "seed", "analysis_status", "authorized", "independent", "evidence_origin", "evidence_maturity", "claim_ceiling", "excluded_generality", "notes"),
    "research-case/05-analysis/results/robustness-and-boundaries.csv": ("robustness_id", "claim_ids", "evidence_ids", "source_asset_id", "source_path", "experiment_id", "analysis_class", "boundary_axis", "condition", "result", "uncertainty", "comparison", "sample_size", "seed", "analysis_status", "authorized", "independent", "evidence_origin", "evidence_maturity", "claim_ceiling", "interpretation_boundary", "excluded_generality", "notes"),
    "prototype/results/exact_stratified_validation.csv": ("design", "strata", "required_successes", "exact_tail_probability", "monte_carlo_tail_probability", "absolute_error", "trials", "seed"),
    "prototype/results/markov_temporal_dependence.csv": ("audits", "trials", "seed", "online_to_offline", "offline_to_online", "final_catastrophic_trials", "all_audits_pass_and_final_catastrophic_count", "conditional_sequence_false_accept_rate", "conditional_sequence_false_accept_ci_low", "conditional_sequence_false_accept_ci_high", "static_set_repeated_bound"),
    "prototype/results/selective_withholding.csv": ("selective_withholders", "reconstruction_success_rate", "reconstruction_success_ci_low", "reconstruction_success_ci_high", "audit_pass_rate", "audit_pass_ci_low", "audit_pass_ci_high"),
    "prototype/results/crypto_benchmark.csv": ("n", "threshold", "repeats", "keygen_median_ms", "keygen_p95_ms", "seal_median_ms", "partial_proof_median_ms", "partial_verify_median_ms", "open_median_ms", "open_p95_ms", "signature_size_bytes", "signature_sign_median_ms", "signature_verify_median_ms"),
    "contracts/gas_report.csv": ("operation", "test", "gas", "measurement_scope", "notes"),
}

CONFIG_KEYS = ("name", "n", "threshold", "sample_size", "required_audit_responses", "independent_offline_probability", "domain_outage_probability", "domains", "trials", "seed", "sampling_strategy", "selective_withholders")
BASELINE_RESULT_KEYS = ("name", "trials", "catastrophic_false_pass_rate", "catastrophic_false_pass_ci_low", "catastrophic_false_pass_ci_high", "catastrophic_trials")
BASELINE_IDS = ("iid-10pct-uniform", "domain-20pct-uniform", "domain-20pct-stratified", "selective-withholding-11")


class PackageValidationError(ValueError):
    """Raised when a required source or generated table violates its boundary."""


@dataclass(frozen=True)
class PaperTable:
    table_id: str
    title: str
    headers: tuple[str, ...]
    rows: tuple[dict[str, str], ...]
    notes: tuple[str, ...]


def _read_csv(project_root: Path, relative: str) -> list[dict[str, str]]:
    try:
        with (project_root / relative).open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            expected = SOURCE_HEADERS.get(relative)
            if expected is not None and tuple(reader.fieldnames or ()) != expected:
                raise PackageValidationError(f"{relative}: header drift; expected {expected!r}")
            rows = list(reader)
    except OSError as exc:
        raise PackageValidationError(f"{relative}: unreadable source: {exc}") from exc
    if not rows:
        raise PackageValidationError(f"{relative}: expected at least one data row")
    return rows


def _read_json(project_root: Path, relative: str) -> object:
    try:
        return json.loads((project_root / relative).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PackageValidationError(f"{relative}: invalid JSON source: {exc}") from exc


def _require_mapping_keys(
    item: object,
    required_keys: Iterable[str],
    relative: str,
    row_label: str,
) -> dict[str, object]:
    if not isinstance(item, dict):
        raise PackageValidationError(f"{relative}: {row_label} must be an object")
    missing = [key for key in required_keys if key not in item]
    if missing:
        raise PackageValidationError(
            f"{relative}: {row_label} missing required keys: {', '.join(missing)}"
        )
    return item


def _require_json_rows(
    project_root: Path,
    relative: str,
    required_keys: Iterable[str],
    id_field: str,
    required_ids: Iterable[str],
) -> dict[str, dict[str, object]]:
    data = _read_json(project_root, relative)
    if not isinstance(data, list) or not data:
        raise PackageValidationError(f"{relative}: expected non-empty JSON list")
    indexed: dict[str, dict[str, object]] = {}
    for index, raw in enumerate(data):
        item = _require_mapping_keys(raw, required_keys, relative, f"row {index}")
        identifier = _string(item[id_field])
        if not identifier:
            raise PackageValidationError(f"{relative}: row {index} has empty {id_field}")
        if identifier in indexed:
            raise PackageValidationError(f"{relative}: duplicate ID: {identifier}")
        indexed[identifier] = item
    expected = tuple(required_ids)
    missing = [identifier for identifier in expected if identifier not in indexed]
    if missing:
        raise PackageValidationError(f"{relative}: missing required IDs: {', '.join(missing)}")
    unexpected = [identifier for identifier in indexed if identifier not in expected]
    if unexpected:
        raise PackageValidationError(f"{relative}: unexpected IDs: {', '.join(unexpected)}")
    return indexed


def _require_csv_rows(
    project_root: Path,
    relative: str,
    id_field: str,
    required_ids: Iterable[str],
) -> dict[str, dict[str, str]]:
    rows = _read_csv(project_root, relative)
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        identifier = row.get(id_field, "")
        if not identifier:
            raise PackageValidationError(f"{relative}: row has empty {id_field}")
        if identifier in indexed:
            raise PackageValidationError(f"{relative}: duplicate ID: {identifier}")
        indexed[identifier] = row
    missing = [identifier for identifier in required_ids if identifier not in indexed]
    if missing:
        raise PackageValidationError(f"{relative}: missing required IDs: {', '.join(missing)}")
    return indexed


def _validate_experiment_manifest(project_root: Path) -> None:
    relative = "prototype/results/experiment_manifest.json"
    manifest = _read_json(project_root, relative)
    if not isinstance(manifest, dict):
        raise PackageValidationError(f"{relative}: expected JSON object")
    expected = {
        "schema_id": "KEYSTONE_PREAUTH_EXPERIMENT_MANIFEST",
        "schema_version": 1,
        "status": "PRELIMINARY_PREAUTHORIZATION",
        "authorization_boundary": "PREAUTHORIZATION_ONLY",
        "scientific_evidence_status": "NOT_SCIENTIFIC_EVIDENCE",
        "independence_status": "SAME_WORKSPACE_NOT_INDEPENDENT",
        "production_validation_status": "NOT_ASSESSED",
    }
    for field, value in expected.items():
        if manifest.get(field) != value:
            raise PackageValidationError(
                f"{relative}: {field} must be {value!r}"
            )
    if not isinstance(manifest.get("inputs"), list) or not manifest["inputs"]:
        raise PackageValidationError(f"{relative}: inputs must be a non-empty list")
    if not isinstance(manifest.get("outputs"), dict) or not manifest["outputs"]:
        raise PackageValidationError(f"{relative}: outputs must be a non-empty object")
    if not isinstance(manifest.get("experiments"), list) or not manifest["experiments"]:
        raise PackageValidationError(f"{relative}: experiments must be a non-empty list")


def _validate_preauthorization_qa(project_root: Path) -> None:
    relative = "paper/tables/preauthorization_engineering_qa.csv"
    path = project_root / relative
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != PREAUTH_QA_HEADERS:
            raise PackageValidationError(f"{relative}: header drift")
        rows = list(reader)
    expected_ids = {
        "RID-C002-CRYPTO-001": "CRYPTO_INTEROPERABILITY",
        "RID-C002-CONTRACT-001": "CONTRACT_BOUNDARY",
    }
    if {row.get("result_id"): row.get("family_id") for row in rows} != expected_ids:
        raise PackageValidationError(f"{relative}: result/family lineage drift")
    for row in rows:
        result_id = row["result_id"]
        if row["authorization_boundary"] != "PREAUTHORIZATION_ONLY":
            raise PackageValidationError(
                f"{relative}: {result_id} authorization_boundary drift"
            )
        if "NOT_SCIENTIFIC_EVIDENCE" not in row["evidence_boundary"]:
            raise PackageValidationError(
                f"{relative}: {result_id} evidence_boundary drift"
            )
        if row["independence_boundary"] != "SAME_WORKSPACE_NOT_INDEPENDENT":
            raise PackageValidationError(
                f"{relative}: {result_id} independence_boundary drift"
            )
        if "production_security_status=NOT_ASSESSED" not in row["security_boundary"]:
            raise PackageValidationError(
                f"{relative}: {result_id} security_boundary drift"
            )


def _validate_required_lineage_inputs(project_root: Path) -> None:
    _validate_experiment_manifest(project_root)
    _validate_preauthorization_qa(project_root)
    evidence = _require_csv_rows(
        project_root,
        "research-case/04-data/evidence-status.csv",
        "evidence_id",
        ("RID-C003-IID-001", "RID-C003-CORR-001", "RID-C003-STRAT-001", "RID-C003-SW-001"),
    )
    for evidence_id in ("RID-C003-IID-001", "RID-C003-CORR-001", "RID-C003-STRAT-001", "RID-C003-SW-001"):
        row = evidence[evidence_id]
        expected = {
            "origin": "SIMULATED",
            "maturity": "V2 SIMULATED",
            "authorized": "false",
            "independent": "false",
            "authorization": "PREAUTHORIZATION_ONLY",
        }
        for field, value in expected.items():
            if row[field] != value:
                raise PackageValidationError(
                    f"research-case/04-data/evidence-status.csv: {evidence_id} {field} must be {value!r}"
                )


def _string(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _row(values: dict[str, object], *, claim_ids: str, source_path: str,
         evidence_stage: str, claim_ceiling: str) -> dict[str, str]:
    if evidence_stage not in ALLOWED_STAGES:
        raise ValueError(f"disallowed evidence stage: {evidence_stage}")
    result = {key: _string(value) for key, value in values.items()}
    result.update(
        claim_ids=claim_ids,
        source_path=source_path,
        evidence_stage=evidence_stage,
        claim_ceiling=claim_ceiling,
    )
    return result


def _table(table_id: str, title: str, specific_headers: Iterable[str],
           rows: Iterable[dict[str, str]], notes: Iterable[str]) -> PaperTable:
    headers = tuple(specific_headers) + COMMON_HEADERS
    if table_id not in EXPECTED_HEADERS or headers != EXPECTED_HEADERS[table_id]:
        raise PackageValidationError(f"{table_id} header drift")
    normalized_rows = tuple(rows)
    for row in normalized_rows:
        if set(row) != set(headers):
            raise ValueError(f"{table_id} row/header mismatch: {set(row) ^ set(headers)}")
    return PaperTable(table_id, title, headers, normalized_rows, tuple(notes))


def _build_t1(project_root: Path) -> PaperTable:
    source = "research-case/01-novelty/novelty-matrix.csv"
    rows = []
    for item in _read_csv(project_root, source):
        rows.append(_row(
            {
                "claim_id": item["claim_id"],
                "predecessor_id": item["predecessor_id"],
                "bounded_difference": item["material_difference"],
                "defeating_evidence": item["defeating_evidence"],
                "residual_uncertainty": item["residual_uncertainty"],
            },
            claim_ids=item["claim_id"], source_path=source,
            evidence_stage="ANALYTIC_DRAFT", claim_ceiling="NOVELTY_UNRESOLVED",
        ))
    return _table("T1", "Bounded strongest-prior-art matrix",
                  ("claim_id", "predecessor_id", "bounded_difference",
                   "defeating_evidence", "residual_uncertainty"), rows,
                  ("Bounded prior-art synthesis only; this table is not novelty clearance.",))


def _build_t2(project_root: Path) -> PaperTable:
    source = "research-case/03-design/protocol.md"
    rows = (
        _row({"comparator_id": "KEYSTONE_FROZEN_DESIGN", "comparator_class": "proposed composition",
              "compared_property": "pre-authorization evidence of present dispute-key serviceability",
              "design_difference": "separates ciphertext availability from current authorized reconstructability",
              "measured_superiority": "NOT_MEASURED"}, claim_ids="C001|C003", source_path=source,
             evidence_stage="DESIGN_ONLY", claim_ceiling="ASSERTED_ONLY"),
        _row({"comparator_id": "CIPHERTEXT_DA", "comparator_class": "design comparator",
              "compared_property": "public ciphertext availability",
              "design_difference": "does not by itself establish threshold-key serviceability",
              "measured_superiority": "NOT_MEASURED"}, claim_ids="C001", source_path=source,
             evidence_stage="DESIGN_ONLY", claim_ceiling="NOVELTY_UNRESOLVED"),
        _row({"comparator_id": "GENERIC_THRESHOLD_RELEASE", "comparator_class": "design comparator",
              "compared_property": "authorized threshold release",
              "design_difference": "prior art already occupies generic threshold release; KEYSTONE comparison is narrower",
              "measured_superiority": "NOT_MEASURED"}, claim_ids="C001|C003", source_path=source,
             evidence_stage="DESIGN_ONLY", claim_ceiling="NOVELTY_UNRESOLVED"),
        _row({"comparator_id": "UNIFORM_CANARY_SAMPLING", "comparator_class": "internal baseline design",
              "compared_property": "uniform sample response under frozen n=32, t=22, s=8, q=8",
              "design_difference": "reference policy for planned stratified and correlated comparisons",
              "measured_superiority": "NOT_MEASURED"}, claim_ids="C003", source_path=source,
             evidence_stage="DESIGN_ONLY", claim_ceiling="ASSERTED_ONLY"),
    )
    return _table("T2", "Proposed design versus bounded comparators",
                  ("comparator_id", "comparator_class", "compared_property",
                   "design_difference", "measured_superiority"), rows,
                  ("Comparators are design-level only; no measured superiority is claimed.",))


def _build_t3(project_root: Path) -> PaperTable:
    source = "prototype/configs/baseline.json"
    configs = _require_json_rows(
        project_root, source, CONFIG_KEYS, "name", BASELINE_IDS
    )
    rows = []
    for config_id in BASELINE_IDS:
        config = configs[config_id]
        rows.append(_row(
            {"condition_id": config["name"], "n": config["n"], "threshold": config["threshold"],
             "sample_size": config["sample_size"], "required_responses": config["required_audit_responses"],
             "offline_probability": config["independent_offline_probability"],
             "domain_outage_probability": config["domain_outage_probability"], "domains": config["domains"],
             "trials": config["trials"], "seed": config["seed"], "sampling_strategy": config["sampling_strategy"],
             "selective_withholders": config["selective_withholders"], "environment_profile": "LOCAL_SIMULATION"},
            claim_ids="C003", source_path=source,
            evidence_stage="PREAUTHORIZATION_SIMULATION_INPUT",
            claim_ceiling="V0 ASSERTED",
        ))
    rows.append(_row(
        {"condition_id": "RID-C003-DEADLINE-001", "n": "MISSING", "threshold": "MISSING",
         "sample_size": "MISSING", "required_responses": "MISSING", "offline_probability": "MISSING",
         "domain_outage_probability": "MISSING", "domains": "MISSING", "trials": "MISSING", "seed": "MISSING",
         "sampling_strategy": "MISSING", "selective_withholders": "MISSING",
         "environment_profile": "DISTRIBUTED_MULTI_PROCESS_OR_MULTI_MACHINE_PROFILE_MISSING"},
        claim_ids="C003", source_path="research-case/03-design/protocol.md",
        evidence_stage="MISSING_NOT_EXECUTED", claim_ceiling="ASSERTED_ONLY",
    ))
    return _table("T3", "Frozen and missing experimental conditions",
                  ("condition_id", "n", "threshold", "sample_size", "required_responses",
                   "offline_probability", "domain_outage_probability", "domains", "trials", "seed",
                   "sampling_strategy", "selective_withholders", "environment_profile"), rows,
                  ("Frozen local conditions are preauthorization inputs; the distributed deadline profile is absent.",))


def _build_t4(project_root: Path) -> PaperTable:
    source = "prototype/results/baseline.json"
    result_ids = {
        "iid-10pct-uniform": "RID-C003-IID-001",
        "domain-20pct-uniform": "RID-C003-CORR-001",
        "domain-20pct-stratified": "RID-C003-STRAT-001",
        "selective-withholding-11": "RID-C003-SW-001",
    }
    data = _require_json_rows(
        project_root, source, BASELINE_RESULT_KEYS, "name", result_ids
    )
    rows = []
    for condition_id in BASELINE_IDS:
        item = data[condition_id]
        result_id = result_ids[condition_id]
        rows.append(_row(
            {"result_id": result_id, "condition_id": item["name"],
             "estimand": "catastrophic_false_pass_rate_conditional_on_catastrophic_trials",
             "estimate": item["catastrophic_false_pass_rate"],
             "ci_low": item["catastrophic_false_pass_ci_low"],
             "ci_high": item["catastrophic_false_pass_ci_high"],
             "denominator": item["catastrophic_trials"], "trials": item["trials"]},
            claim_ids="C003", source_path=source,
            evidence_stage="PREAUTHORIZATION_SIMULATED",
            claim_ceiling="V0 ASSERTED",
        ))
    return _table("T4", "Current preliminary internal results",
                  ("result_id", "condition_id", "estimand", "estimate", "ci_low", "ci_high",
                   "denominator", "trials"), rows,
                  ("Values are parsed from canonical JSON and remain preliminary/internal, not authorized confirmation.",))


def _build_t5(project_root: Path) -> PaperTable:
    source = "research-case/03-design/analysis-plan.md"
    planned = (
        ("ABL-CANARY-001", "remove canary readiness audit", "separate audit contribution from ciphertext availability"),
        ("ABL-STRAT-001", "replace stratified sampling with uniform sampling", "isolate sampling-policy contribution"),
        ("ABL-DOMAIN-001", "remove failure-domain labels", "test dependency on domain metadata"),
        ("ABL-TEMPORAL-001", "replace temporal dependence with static IID assumptions", "isolate temporal-model sensitivity"),
    )
    rows = tuple(_row(
        {"ablation_id": ablation_id, "planned_change": change, "mechanism_question": question,
         "execution_status": "MISSING_NOT_EXECUTED", "estimate": "MISSING"},
        claim_ids="C001|C003", source_path=source, evidence_stage="MISSING_NOT_EXECUTED",
        claim_ceiling="ASSERTED_ONLY",
    ) for ablation_id, change, question in planned)
    return _table("T5", "Planned mechanism-isolation ablations",
                  ("ablation_id", "planned_change", "mechanism_question", "execution_status", "estimate"), rows,
                  ("All rows are planned and unexecuted; no ablation effect is asserted.",))


def _build_t6(project_root: Path) -> PaperTable:
    robustness_source = "research-case/05-analysis/results/robustness-and-boundaries.csv"
    rows = []
    for item in _read_csv(project_root, robustness_source):
        if item["authorized"] != "false" or item["independent"] != "false":
            raise PackageValidationError(
                f"{robustness_source}: {item['robustness_id']} must remain unauthorized and non-independent"
            )
        if item["evidence_origin"] != "SIMULATED" or item["evidence_maturity"] != "V2 SIMULATED" or item["claim_ceiling"] != "V0 ASSERTED":
            raise PackageValidationError(
                f"{robustness_source}: {item['robustness_id']} evidence boundary drift"
            )
        rows.append(_row(
            {"check_id": item["robustness_id"], "estimand": item["boundary_axis"],
             "condition": item["condition"], "estimate": item["result"],
             "comparison": item["comparison"], "uncertainty_or_error": item["uncertainty"],
             "interpretation_boundary": item["interpretation_boundary"]},
            claim_ids=item["claim_ids"], source_path=robustness_source,
            evidence_stage="PREAUTHORIZATION_SIMULATED", claim_ceiling="V0 ASSERTED",
        ))
    exact_source = "prototype/results/exact_stratified_validation.csv"
    exact_rows = _read_csv(project_root, exact_source)
    if len(exact_rows) != 1:
        raise PackageValidationError(
            f"{exact_source}: expected exactly one data row, found {len(exact_rows)}"
        )
    (exact,) = exact_rows
    rows.append(_row(
        {"check_id": "EXACT_STRATIFIED", "estimand": "tail probability for the declared fixed-quota strata",
         "condition": exact["strata"], "estimate": exact["exact_tail_probability"],
         "comparison": exact["monte_carlo_tail_probability"], "uncertainty_or_error": exact["absolute_error"],
         "interpretation_boundary": "exact-versus-Monte-Carlo validation for one declared parameter cell"},
        claim_ids="C003", source_path=exact_source,
        evidence_stage="EXPLORATORY_PREAUTHORIZATION_SIMULATED",
        claim_ceiling="V0 ASSERTED",
    ))
    exploratory_source = "research-case/05-analysis/results/exploratory-findings.csv"
    exploratory_rows = _read_csv(project_root, exploratory_source)
    for item in exploratory_rows:
        if item["authorized"] != "false" or item["independent"] != "false":
            raise PackageValidationError(
                f"{exploratory_source}: {item['finding_id']} must remain unauthorized and non-independent"
            )
        if item["evidence_origin"] != "SIMULATED" or item["evidence_maturity"] != "V2 SIMULATED" or item["claim_ceiling"] != "V0 ASSERTED":
            raise PackageValidationError(
                f"{exploratory_source}: {item['finding_id']} evidence boundary drift"
            )
        rows.append(_row(
            {"check_id": item["finding_id"], "estimand": item["estimand"],
             "condition": item["condition"], "estimate": item["effect_estimate"],
             "comparison": item["comparison"], "uncertainty_or_error": item["uncertainty_interval"],
             "interpretation_boundary": item["interpretation_boundary"]},
            claim_ids=item["claim_id"], source_path=exploratory_source,
            evidence_stage="EXPLORATORY_PREAUTHORIZATION_SIMULATED",
            claim_ceiling="V0 ASSERTED",
        ))
    return _table("T6", "Robustness and boundary-condition checks",
                  ("check_id", "estimand", "condition", "estimate", "comparison",
                   "uncertainty_or_error", "interpretation_boundary"), rows,
                  ("Canonical robustness rows and exploratory temporal rows remain separately classified; selective-withholding negative findings are in T8.",))


def _build_t7(project_root: Path) -> PaperTable:
    rows = []
    crypto_source = "prototype/results/crypto_benchmark.csv"
    crypto_rows = _require_csv_rows(
        project_root, crypto_source, "n", ("16", "32", "64")
    )
    for n in ("16", "32", "64"):
        item = crypto_rows[n]
        rows.append(_row(
            {"evidence_id": f"LOCAL_CRYPTO_N{item['n']}", "surface": "local cryptographic timing",
             "metric": "open_median_ms", "value": item["open_median_ms"], "unit": "ms",
             "scope_or_blocker": f"local repeats={item['repeats']}; non-production research group"},
            claim_ids="C002", source_path=crypto_source, evidence_stage="PREAUTHORIZATION_INTERNAL",
            claim_ceiling="V3_INTERNAL",
        ))
    gas_source = "contracts/gas_report.csv"
    gas_operations = (
        "register_epoch", "open_audit", "submit_audit_response",
        "mark_invalid_response", "record_equivocation", "finalize_audit",
        "open_dispute", "cancel_request",
    )
    gas_rows = _require_csv_rows(project_root, gas_source, "operation", gas_operations)
    for operation in gas_operations:
        item = gas_rows[operation]
        rows.append(_row(
            {"evidence_id": f"FOUNDRY_GAS_{item['operation'].upper()}", "surface": "Foundry gas snapshot",
             "metric": item["operation"], "value": item["gas"], "unit": "test-body gas",
             "scope_or_blocker": f"{item['measurement_scope']}; {item['notes']}"},
            claim_ids="C002", source_path=gas_source, evidence_stage="PREAUTHORIZATION_INTERNAL",
            claim_ceiling="V3_INTERNAL",
        ))
    for evidence_id, surface, blocker in (
        ("RID-C003-DEADLINE-001", "distributed deadline behavior", "representative distributed profile not executed"),
        ("PRODUCTION_OPERATOR", "operator feasibility", "production operator evidence absent"),
        ("PRODUCTION_NETWORK", "network feasibility", "production network evidence absent"),
        ("EXTERNAL_VALIDATION", "external feasibility", "claim-matched external validation absent"),
    ):
        rows.append(_row(
            {"evidence_id": evidence_id, "surface": surface, "metric": "MISSING", "value": "MISSING",
             "unit": "N/A", "scope_or_blocker": blocker}, claim_ids="C003",
            source_path="research-case/02-feasibility/risk-register.csv",
            evidence_stage="BLOCKED_EXTERNAL", claim_ceiling="ASSERTED_ONLY",
        ))
    return _table("T7", "Real-world feasibility and resource boundary",
                  ("evidence_id", "surface", "metric", "value", "unit", "scope_or_blocker"), rows,
                  ("Local timings and Foundry observations are preauthorization/internal only; external and production rows remain blocked.",))


def _build_t8(project_root: Path) -> PaperTable:
    risk_source = "research-case/02-feasibility/risk-register.csv"
    selected = ("R005", "R007", "R008", "R009", "R010")
    risk_rows = _require_csv_rows(project_root, risk_source, "risk_id", selected)
    rows = []
    for risk_id in selected:
        item = risk_rows[risk_id]
        stage = "BLOCKED_EXTERNAL" if risk_id in {"R005", "R007"} else "DESIGN_ONLY"
        rows.append(_row(
            {"finding_id": risk_id, "finding": item["description"], "status": item["status"],
             "consequence": item["trigger"], "required_resolution": item["verification"]},
            claim_ids=item["related_claims"], source_path=risk_source, evidence_stage=stage,
            claim_ceiling="ASSERTED_ONLY",
        ))
    negative_source = "research-case/05-analysis/results/negative-findings.csv"
    for item in _read_csv(project_root, negative_source):
        if item["authorized"] != "false" or item["independent"] != "false":
            raise PackageValidationError(
                f"{negative_source}: {item['finding_id']} must remain unauthorized and non-independent"
            )
        if item["evidence_origin"] != "SIMULATED" or item["evidence_maturity"] != "V2 SIMULATED" or item["claim_ceiling"] != "V0 ASSERTED":
            raise PackageValidationError(
                f"{negative_source}: {item['finding_id']} evidence boundary drift"
            )
        rows.append(_row(
            {"finding_id": item["finding_id"],
             "finding": f"Selective withholding: {item['implication']}",
             "status": item["analysis_status"],
             "consequence": item["excluded_generality"],
             "required_resolution": item["notes"]},
            claim_ids=item["claim_ids"], source_path=negative_source,
            evidence_stage="NEGATIVE_FINDING_PREAUTHORIZATION_SIMULATED",
            claim_ceiling="V0 ASSERTED",
        ))
    rows.extend((
        _row({"finding_id": "AUDIT_DISPUTE_SEPARATION", "finding": "routine audit response is not a dispute reconstruction guarantee",
              "status": "PRESERVED_LIMIT", "consequence": "audit evidence cannot be relabeled as dispute success",
              "required_resolution": "retain separate estimands and claim language"}, claim_ids="C001|C003",
             source_path="research-case/03-design/analysis-plan.md", evidence_stage="DESIGN_ONLY", claim_ceiling="ASSERTED_ONLY"),
        _row({"finding_id": "SYNCHRONY_LIMIT", "finding": "deadline accountability is conditional on declared synchrony assumptions",
              "status": "MISSING", "consequence": "unconditional deadline claims remain blocked",
              "required_resolution": "execute RID-C003-DEADLINE-001 under frozen distributed profiles"}, claim_ids="C003",
             source_path="research-case/03-design/protocol.md", evidence_stage="MISSING_NOT_EXECUTED", claim_ceiling="ASSERTED_ONLY"),
        _row({"finding_id": "TRUTHFUL_DOMAIN_LABEL_DEPENDENCY", "finding": "correlation and placement guidance depends on truthful domain labels",
              "status": "AT_RISK", "consequence": "unsupported or adversarial labels can invalidate domain-based guidance",
              "required_resolution": "validate domain-label provenance and run sensitivity analysis before operational guidance"}, claim_ids="C003",
             source_path="research-case/02-feasibility/risk-register.csv", evidence_stage="DESIGN_ONLY", claim_ceiling="ASSERTED_ONLY"),
        _row({"finding_id": "EXTERNAL_VALIDATION_MISSING", "finding": "external validation is absent",
              "status": "BLOCKED", "consequence": "no production, operator, network, or generality claim",
              "required_resolution": "obtain authorized claim-matched external validation"}, claim_ids="C003",
             source_path="research-case/07-manuscript/claim-evidence-matrix.csv", evidence_stage="BLOCKED_EXTERNAL", claim_ceiling="ASSERTED_ONLY"),
    ))
    return _table("T8", "Negative findings and unresolved risks",
                  ("finding_id", "finding", "status", "consequence", "required_resolution"), rows,
                  ("Selective withholding, truthful domain-label dependence, synchrony, production limits, and missing external validation remain explicit.",))


def build_package(project_root: Path) -> dict[str, PaperTable]:
    """Build T1--T8 from the canonical bounded inputs without writing files."""
    root = project_root.resolve()
    _validate_required_lineage_inputs(root)
    builders = (_build_t1, _build_t2, _build_t3, _build_t4,
                _build_t5, _build_t6, _build_t7, _build_t8)
    package = {table.table_id: table for table in (builder(root) for builder in builders)}
    if tuple(package) != tuple(f"T{i}" for i in range(1, 9)):
        raise ValueError("table package must contain exact ordered IDs T1--T8")
    return package


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_csv(path: Path, table: PaperTable) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=table.headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(table.rows)


def _md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def _markdown(package: dict[str, PaperTable]) -> str:
    lines = ["# KEYSTONE T1--T8 Paper Table Package", "",
             "**Status: DRAFT / PRE-AUTHORIZATION. Not confirmatory or independent evidence.**", ""]
    for table in package.values():
        lines.extend((f"## {table.table_id} — {table.title}", "",
                      "**DRAFT / PRE-AUTHORIZATION**", "",
                      "| " + " | ".join(table.headers) + " |",
                      "| " + " | ".join("---" for _ in table.headers) + " |"))
        for row in table.rows:
            lines.append("| " + " | ".join(_md(row[h]) for h in table.headers) + " |")
        lines.extend(("", "Notes:", ""))
        lines.extend(f"- {_md(note)}" for note in table.notes)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value).replace("\n", r"\newline{}")


def _latex_cell(value: str) -> str:
    """Escape a cell while adding safe discretionary breaks for long identifiers."""
    return (
        latex_escape(value)
        .replace(r"\_", r"\_\allowbreak{}")
        .replace("; ", r";\allowbreak{} ")
    )


def _latex(package: dict[str, PaperTable]) -> str:
    lines = [r"% KEYSTONE T1--T8 editable table source",
             r"% DRAFT / PRE-AUTHORIZATION; NOT CONFIRMATORY OR INDEPENDENT EVIDENCE",
             r"\providecommand{\KeystoneDraftTableNotice}{\textbf{DRAFT / PRE-AUTHORIZATION}}", ""]
    for table in package.values():
        # A vertical record layout keeps every table editable and width-bounded,
        # including T3/T7/T8. Fractions sum to 0.92\linewidth; the remaining
        # width covers four 2pt tab-column paddings and vertical rules.
        lines.extend((f"% {table.table_id} -- DRAFT / PRE-AUTHORIZATION",
                      r"\begingroup",
                      r"\setlength{\tabcolsep}{2pt}",
                      r"\small\sloppy",
                      r"\begin{longtable}{|p{0.24\linewidth}|p{0.68\linewidth}|}", r"\hline",
                      r"\multicolumn{2}{|l|}{\KeystoneDraftTableNotice{} -- "
                      + latex_escape(f"{table.table_id}: {table.title}") + r"} \\ \hline",
                      r"\textbf{Field} & \textbf{Value} \\ \hline"))
        for row_number, row in enumerate(table.rows, start=1):
            lines.append(
                r"\multicolumn{2}{|l|}{\textbf{Record "
                + str(row_number) + r"}} \\ \hline"
            )
            for header in table.headers:
                lines.append(
                    _latex_cell(header) + " & " + _latex_cell(row[header])
                    + r" \\ \hline"
                )
        notes = " ".join(table.notes)
        lines.extend((r"\multicolumn{2}{|p{0.92\linewidth}|}{\textit{Notes:} "
                      + latex_escape(notes) + r"} \\ \hline",
                      r"\end{longtable}", r"\endgroup", ""))
    return "\n".join(lines).rstrip() + "\n"


def write_package(project_root: Path, output_dir: Path) -> dict[str, str]:
    """Write deterministic CSV, Markdown, LaTeX, manifest, and sidecar outputs."""
    root = project_root.resolve()
    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    package = build_package(root)
    written: dict[str, str] = {}
    for table_id, table in package.items():
        name = TABLE_FILENAMES[table_id]
        _write_csv(destination / name, table)
        written[name] = str(destination / name)
    for name, content in (("t1_t8_package.md", _markdown(package)),
                          ("t1_t8_package.tex", _latex(package))):
        (destination / name).write_text(content, encoding="utf-8")
        written[name] = str(destination / name)

    outputs = [
        {"path": name, "sha256": _sha256(destination / name)}
        for name in sorted(written)
    ]
    manifest = {
        "schema_id": "KEYSTONE_T1_T8_TABLE_PACKAGE",
        "schema_version": 1,
        "status": "DRAFT_PREAUTHORIZATION",
        "scientific_evidence_boundary": "NOT_CONFIRMATORY_OR_INDEPENDENT_EVIDENCE",
        "canonical_dispositions": {
            "phase": "INTAKE", "novelty": "UNRESOLVED", "feasibility": "UNASSESSED",
            "solution_viability": "ASSERTED_ONLY", "acceptance_readiness": "NOT_ASSESSABLE",
        },
        "table_ids": list(package),
        "inputs": [
            {"path": relative, "sha256": _sha256(root / relative)}
            for relative in INPUT_PATHS
        ],
        "outputs": outputs,
        "table_dispositions": TABLE_DISPOSITIONS,
        "missing_required_evidence": ["RID-C003-DEADLINE-001", "independent reproduction", "external validation"],
    }
    manifest_name = "t1_t8_manifest.json"
    manifest_path = destination / manifest_name
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    written[manifest_name] = str(manifest_path)
    sidecar_name = "t1_t8_manifest.json.sha256"
    (destination / sidecar_name).write_text(f"{_sha256(manifest_path)}  {manifest_name}\n", encoding="utf-8")
    written[sidecar_name] = str(destination / sidecar_name)
    return written


def check_package(project_root: Path, output_dir: Path) -> list[str]:
    """Return fail-closed drift errors for an existing package."""
    root = project_root.resolve()
    destination = output_dir.resolve()
    manifest_path = destination / "t1_t8_manifest.json"
    sidecar_path = destination / "t1_t8_manifest.json.sha256"
    errors: list[str] = []
    try:
        _validate_required_lineage_inputs(root)
    except (PackageValidationError, json.JSONDecodeError, OSError) as exc:
        errors.append(f"required source validation failed: {exc}")
    if not manifest_path.is_file():
        return ["missing t1_t8_manifest.json"]
    if not sidecar_path.is_file():
        errors.append("missing t1_t8_manifest.json.sha256")
    else:
        expected_sidecar = f"{_sha256(manifest_path)}  t1_t8_manifest.json"
        if sidecar_path.read_text(encoding="utf-8").strip() != expected_sidecar:
            errors.append("t1_t8_manifest.json.sha256 drift")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return errors + [f"invalid t1_t8_manifest.json: {exc}"]
    if manifest.get("schema_id") != "KEYSTONE_T1_T8_TABLE_PACKAGE" or manifest.get("schema_version") != 1:
        errors.append("manifest schema drift")
    if manifest.get("status") != "DRAFT_PREAUTHORIZATION":
        errors.append("manifest status drift")
    if manifest.get("scientific_evidence_boundary") != "NOT_CONFIRMATORY_OR_INDEPENDENT_EVIDENCE":
        errors.append("manifest scientific_evidence_boundary drift")
    if manifest.get("table_dispositions") != TABLE_DISPOSITIONS:
        errors.append("manifest table_dispositions drift")
    if manifest.get("table_ids") != list(TABLE_FILENAMES):
        errors.append("manifest table_ids drift")
    declared_input_paths = [item.get("path", "") for item in manifest.get("inputs", [])]
    if declared_input_paths != list(INPUT_PATHS):
        errors.append("manifest input inventory drift")
    expected_output_paths = sorted(
        (*TABLE_FILENAMES.values(), "t1_t8_package.md", "t1_t8_package.tex")
    )
    declared_output_paths = [item.get("path", "") for item in manifest.get("outputs", [])]
    if declared_output_paths != expected_output_paths:
        errors.append("manifest output inventory drift")
    for item in manifest.get("inputs", []):
        relative = item.get("path", "")
        expected = item.get("sha256", "")
        path = root / relative
        if not relative or not expected or not path.is_file() or _sha256(path) != expected:
            errors.append(f"input drift: {relative or 'UNKNOWN'}")
    for item in manifest.get("outputs", []):
        name = item.get("path", "")
        expected = item.get("sha256", "")
        path = destination / name
        if not name or not expected or not path.is_file() or _sha256(path) != expected:
            errors.append(f"output drift: {name or 'UNKNOWN'}")
    # The on-disk manifest is evidence to check, never the source of truth.
    # Reconstruct every owned output from canonical inputs in isolation so an
    # attacker cannot hide output drift by rebinding manifest hashes/sidecar.
    try:
        with tempfile.TemporaryDirectory(prefix="keystone-t1-t8-check-") as raw:
            expected_dir = Path(raw)
            expected_paths = write_package(root, expected_dir)
            for name in expected_paths:
                actual_path = destination / name
                expected_path = expected_dir / name
                if not actual_path.is_file() or actual_path.read_bytes() != expected_path.read_bytes():
                    errors.append(f"canonical reconstruction drift: {name}")
    except (PackageValidationError, OSError, json.JSONDecodeError) as exc:
        errors.append(f"canonical reconstruction failed: {exc}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    output_dir = args.output_dir or args.project_root / "paper/tables"
    if args.check:
        errors = check_package(args.project_root, output_dir)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print("T1--T8 package check passed")
        return 0
    paths = write_package(args.project_root, output_dir)
    for name in sorted(paths):
        print(paths[name])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
