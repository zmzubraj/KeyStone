#!/usr/bin/env python3
"""Export deterministic preauthorization provenance and evidence-status ledgers."""

from __future__ import annotations

import argparse
import csv
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

BOUNDARY = {
    "authorization_boundary": "PREAUTHORIZATION_ONLY",
    "scientific_evidence_status": "NOT_SCIENTIFIC_EVIDENCE",
    "independence_status": "SAME_WORKSPACE_NOT_INDEPENDENT",
}
REQUIRED_STATE = {
    "status": "ACTIVE",
    "current_phase": "INTAKE",
    "resume_from": "INTAKE",
    "novelty_status": "UNRESOLVED",
    "solution_viability_status": "ASSERTED_ONLY",
    "acceptance_readiness": "NOT_ASSESSABLE",
}

PROVENANCE_FIELDS = (
    "asset_id",
    "asset_type",
    "source",
    "authorization",
    "acquired_at",
    "sha256",
    "processing",
    "owner",
)
EVIDENCE_FIELDS = (
    "evidence_id",
    "claim_ids",
    "origin",
    "maturity",
    "scope",
    "status",
    "authorized",
    "independent",
    "source_artifact",
    "source_asset_ids",
    "authorization",
    "directness",
    "uncertainty",
    "tested_setting",
    "failure_envelope",
    "excluded_generality",
    "notes",
)

FIXED_ASSETS = (
    (
        "ASSET-PROPERTY-SEPARATION",
        "ANALYTIC_SPECIFICATION",
        "paper/property_separation_obligations.md",
        "SOURCE_DATE_EPOCH_OR_OMITTED",
        "Authored preauthorization property-separation specification; no empirical transformation.",
    ),
    (
        "ASSET-BASELINE",
        "SYNTHETIC_CONFIGURATION",
        "prototype/results/baseline.json",
        "SOURCE_DATE_EPOCH_OR_OMITTED",
        "Separately invoked deterministic baseline workflow output.",
    ),
    (
        "ASSET-CRYPTO-BENCHMARK",
        "INTERNAL_ENGINEERING_QA_OUTPUT",
        "prototype/results/crypto_benchmark.csv",
        "SOURCE_DATE_EPOCH_OR_OMITTED",
        "Internal non-empirical benchmark output; not independently reproduced.",
    ),
    (
        "ASSET-GAS-REPORT",
        "INTERNAL_ENGINEERING_QA_OUTPUT",
        "contracts/gas_report.csv",
        "SOURCE_DATE_EPOCH_OR_OMITTED",
        "Internal Foundry gas snapshot export; not field-cost evidence.",
    ),
)

RECEIPT_ASSETS = (
    (
        "ASSET-CRYPTO-QA-RECEIPT",
        "prototype/results/engineering_qa/rid-c002-crypto-001-preauth-receipt.json",
        "Internal cryptographic prototype QA receipt; not a cryptographic audit.",
    ),
    (
        "ASSET-CONTRACT-QA-RECEIPT",
        "contracts/results/engineering_qa/rid-c002-contract-001-preauth-receipt.json",
        "Internal smart-contract QA receipt; not a production security audit.",
    ),
)

DATASET_ASSET_IDS = {
    "prototype/results/theoretical_bound.csv": "ASSET-THEORETICAL-BOUND",
    "prototype/results/iid_failure_sweep.csv": "ASSET-IID-FAILURE-SWEEP",
    "prototype/results/domain_diversity.csv": "ASSET-DOMAIN-DIVERSITY",
    "prototype/results/selective_withholding.csv": "ASSET-SELECTIVE-WITHHOLDING",
    "prototype/results/sampling_strategy.csv": "ASSET-SAMPLING-STRATEGY",
    "prototype/results/exact_stratified_validation.csv": "ASSET-EXACT-STRATIFIED-VALIDATION",
    "prototype/results/markov_temporal_dependence.csv": "ASSET-MARKOV-TEMPORAL-DEPENDENCE",
}


class LineageError(RuntimeError):
    """Raised when source state cannot support a bounded lineage export."""


def _read_json(path: Path, label: str) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LineageError(f"cannot read {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise LineageError(f"{label} must be a JSON object")
    return payload


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise LineageError(f"cannot hash source {path}: {exc}") from exc


def _validate_boundary(payload: dict[str, object], label: str) -> None:
    for field, expected in BOUNDARY.items():
        actual = payload.get(field)
        if actual != expected:
            raise LineageError(f"{label} {field} expected {expected}, got {actual}")


def _validate_control_boundary(root: Path) -> None:
    state = _read_json(root / STATE_PATH, "canonical program state")
    for field, expected in REQUIRED_STATE.items():
        actual = state.get(field)
        if actual != expected:
            raise LineageError(f"canonical {field} expected {expected}, got {actual}")
    try:
        charter = (root / CHARTER_PATH).read_text(encoding="utf-8").lower()
    except OSError as exc:
        raise LineageError(f"cannot read program charter: {exc}") from exc
    required_phrases = ("final author order", "corresponding-author", "affiliation wording", "remain deferred")
    if not all(phrase in charter for phrase in required_phrases):
        raise LineageError("program charter does not preserve the required author metadata deferral")


def _provenance_rows(root: Path) -> list[dict[str, str]]:
    manifest = _read_json(root / EXPERIMENT_MANIFEST_PATH, "experiment manifest")
    _validate_boundary(manifest, "experiment manifest")
    generation = manifest.get("generation_timestamp")
    if not isinstance(generation, dict) or generation.get("policy") != "SOURCE_DATE_EPOCH_OR_OMITTED":
        raise LineageError("experiment manifest lacks deterministic generation timestamp policy")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict) or not isinstance(outputs.get("datasets"), list):
        raise LineageError("experiment manifest lacks outputs.datasets")

    rows: list[dict[str, str]] = []
    observed_paths: set[str] = set()
    for item in outputs["datasets"]:
        if not isinstance(item, dict):
            raise LineageError("experiment manifest contains malformed dataset entry")
        source = str(item.get("path") or "")
        expected_hash = str(item.get("sha256") or "")
        if source not in DATASET_ASSET_IDS:
            raise LineageError(f"unexpected dataset path in experiment manifest: {source}")
        if source in observed_paths:
            raise LineageError(f"duplicate dataset path in experiment manifest: {source}")
        observed_paths.add(source)
        actual_hash = _sha256(root / source)
        if actual_hash != expected_hash:
            raise LineageError(
                f"source hash mismatch for {source}: expected {expected_hash}, got {actual_hash}"
            )
        rows.append(
            {
                "asset_id": DATASET_ASSET_IDS[source],
                "asset_type": "SIMULATION_OR_ANALYTIC_DATASET",
                "source": source,
                "authorization": "PREAUTHORIZATION_ONLY / NOT_SCIENTIFIC_EVIDENCE",
                "acquired_at": "SOURCE_DATE_EPOCH_OR_OMITTED",
                "sha256": actual_hash,
                "processing": "Generated by the deterministic local experiment pipeline and hash-bound by experiment_manifest.json.",
                "owner": "root-integration-owner",
            }
        )
    missing = sorted(set(DATASET_ASSET_IDS) - observed_paths)
    if missing:
        raise LineageError("experiment manifest is missing required datasets: " + ", ".join(missing))

    for asset_id, asset_type, source, acquired_at, processing in FIXED_ASSETS:
        rows.append(
            {
                "asset_id": asset_id,
                "asset_type": asset_type,
                "source": source,
                "authorization": "PREAUTHORIZATION_ONLY / NOT_SCIENTIFIC_EVIDENCE",
                "acquired_at": acquired_at,
                "sha256": _sha256(root / source),
                "processing": processing,
                "owner": "root-integration-owner",
            }
        )

    for asset_id, source, processing in RECEIPT_ASSETS:
        receipt = _read_json(root / source, f"receipt {source}")
        _validate_boundary(receipt, f"receipt {source}")
        completed = receipt.get("completed_at_utc")
        if not isinstance(completed, str) or not completed:
            raise LineageError(f"receipt {source} lacks completed_at_utc")
        rows.append(
            {
                "asset_id": asset_id,
                "asset_type": "PREAUTHORIZATION_ENGINEERING_QA_RECEIPT",
                "source": source,
                "authorization": "PREAUTHORIZATION_ONLY / NOT_SCIENTIFIC_EVIDENCE",
                "acquired_at": completed,
                "sha256": _sha256(root / source),
                "processing": processing,
                "owner": "root-integration-owner",
            }
        )
    return sorted(rows, key=lambda row: row["asset_id"])


def _evidence_row(
    evidence_id: str,
    claim_ids: str,
    origin: str,
    maturity: str,
    scope: str,
    status: str,
    source_asset_ids: str,
    directness: str,
    tested_setting: str,
    failure_envelope: str,
    excluded_generality: str,
    notes: str,
) -> dict[str, str]:
    return {
        "evidence_id": evidence_id,
        "claim_ids": claim_ids,
        "origin": origin,
        "maturity": maturity,
        "scope": scope,
        "status": status,
        "authorized": "false",
        "independent": "false",
        "source_artifact": "04-data/provenance-manifest.csv",
        "source_asset_ids": source_asset_ids,
        "authorization": "PREAUTHORIZATION_ONLY",
        "directness": directness,
        "uncertainty": "No independent scientific verification; current outputs are draft internal artifacts.",
        "tested_setting": tested_setting,
        "failure_envelope": failure_envelope,
        "excluded_generality": excluded_generality,
        "notes": notes,
    }


def _evidence_rows() -> list[dict[str, str]]:
    common_exclusion = "No production, field, external-replication, or universal security claim."
    rows = [
        _evidence_row("RID-C001-SEP-001", "C001", "ANALYTIC", "V1 ANALYTIC", "ANALYTIC", "PARTIAL", "ASSET-PROPERTY-SEPARATION", "Direct specification of audit/dispute predicate separation.", "Frozen model and property obligations.", "Specification may be incomplete or model assumptions may not hold.", common_exclusion, "Traceability only; not independently verified."),
        _evidence_row("RID-C001-STATIC-001", "C001|C003", "ANALYTIC", "V1 ANALYTIC", "ANALYTIC", "PARTIAL", "ASSET-THEORETICAL-BOUND", "Direct model-bounded analytic output.", "Static n=32 threshold scenarios recorded by the manifest.", "Bound is sensitive to frozen model assumptions.", common_exclusion, "Model-bounded analytic draft."),
        _evidence_row("RID-C002-CRYPTO-001", "C002|C003", "INTERNAL_EXPERIMENT", "V3 INTERNAL", "INTERNAL", "PARTIAL", "ASSET-CRYPTO-QA-RECEIPT|ASSET-CRYPTO-BENCHMARK", "Internal implementation QA and benchmark only.", "Local deterministic fixtures and benchmark environment.", "No independent cryptographic audit or adversarial production validation.", common_exclusion, "Engineering QA must not be relabelled as scientific evidence."),
        _evidence_row("RID-C002-CONTRACT-001", "C002", "INTERNAL_EXPERIMENT", "V3 INTERNAL", "INTERNAL", "PARTIAL", "ASSET-CONTRACT-QA-RECEIPT|ASSET-GAS-REPORT", "Internal contract tests and gas snapshot only.", "Local Foundry execution.", "No production deployment or independent security audit.", common_exclusion, "Engineering QA must not be relabelled as scientific evidence."),
        _evidence_row("RID-C003-IID-001", "C003", "SIMULATED", "V2 SIMULATED", "SIMULATED", "PARTIAL", "ASSET-IID-FAILURE-SWEEP", "Direct seeded simulation output.", "Frozen IID outage sweep.", "IID assumptions may not represent correlated failures.", common_exclusion, "Simulation only."),
        _evidence_row("RID-C003-CORR-001", "C003", "SIMULATED", "V2 SIMULATED", "SIMULATED", "PARTIAL", "ASSET-DOMAIN-DIVERSITY|ASSET-MARKOV-TEMPORAL-DEPENDENCE", "Direct seeded correlated-failure simulations.", "Frozen domain and Markov scenarios.", "Scenario coverage is bounded and parameter-dependent.", common_exclusion, "Simulation only."),
        _evidence_row("RID-C003-STRAT-001", "C003", "SIMULATED", "V2 SIMULATED", "SIMULATED", "PARTIAL", "ASSET-BASELINE|ASSET-SAMPLING-STRATEGY|ASSET-EXACT-STRATIFIED-VALIDATION", "Direct seeded strategy comparison with one exact-tail validation.", "Frozen n=32,t=22 sampling settings.", "Does not establish optimality outside evaluated strategies.", common_exclusion, "Simulation and analytic validation only."),
        _evidence_row("RID-C003-SW-001", "C003", "SIMULATED", "V2 SIMULATED", "SIMULATED", "PARTIAL", "ASSET-BASELINE|ASSET-SELECTIVE-WITHHOLDING", "Direct seeded negative-result simulation.", "Frozen selective-withholding sweep for n=32,t=22,s=8,q=8.", "Adversary and availability models are bounded.", common_exclusion, "Central limitation result; simulation only."),
        _evidence_row("RID-C003-DEADLINE-001", "C003", "EXPERT_JUDGMENT", "V0 ASSERTED", "ASSERTED", "BLOCKED", "", "No executed distributed evidence asset exists.", "Proposed future deadline-aware distributed pilot.", "Environment, protocol, authorization, and execution remain absent.", common_exclusion, "Blocked until a separately authorized and independently verified pilot is executed."),
    ]
    return sorted(rows, key=lambda row: row["evidence_id"])


def _render_csv(fields: tuple[str, ...], rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _expected_outputs(root: Path) -> tuple[str, str]:
    _validate_control_boundary(root)
    return (
        _render_csv(PROVENANCE_FIELDS, _provenance_rows(root)),
        _render_csv(EVIDENCE_FIELDS, _evidence_rows()),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        expected_provenance, expected_evidence = _expected_outputs(root)
    except LineageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    targets = (
        (root / PROVENANCE_PATH, expected_provenance),
        (root / EVIDENCE_PATH, expected_evidence),
    )
    if args.check:
        stale = []
        for path, expected in targets:
            try:
                actual = path.read_text(encoding="utf-8")
            except OSError:
                actual = ""
            if actual != expected:
                stale.append(str(path))
        if stale:
            print("error: evidence lineage outputs are stale: " + ", ".join(stale), file=sys.stderr)
            return 1
        print("OK: evidence lineage outputs are current")
        return 0

    for path, expected in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8", newline="")
        print(f"Wrote evidence lineage artifact: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
