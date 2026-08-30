from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export_robustness_boundaries.py"


SOURCES = {
    "iid": {
        "path": "prototype/results/iid_failure_sweep.csv",
        "asset_id": "ASSET-IID-FAILURE-SWEEP",
        "evidence_id": "RID-C003-IID-001",
        "experiment_id": "EXP-IID-FAILURE-SWEEP",
        "kind": "SEEDED_MONTE_CARLO",
        "fields": [
            "offline_probability",
            "reconstruction_success_rate",
            "reconstruction_success_ci_low",
            "reconstruction_success_ci_high",
            "audit_pass_rate",
            "audit_pass_ci_low",
            "audit_pass_ci_high",
            "catastrophic_detection_rate",
            "catastrophic_trials",
        ],
        "rows": [
            {
                "offline_probability": "0.0",
                "reconstruction_success_rate": "1.0",
                "reconstruction_success_ci_low": "0.99",
                "reconstruction_success_ci_high": "1.0",
                "audit_pass_rate": "1.0",
                "audit_pass_ci_low": "0.99",
                "audit_pass_ci_high": "1.0",
                "catastrophic_detection_rate": "1.0",
                "catastrophic_trials": "0",
            },
            {
                "offline_probability": "0.4",
                "reconstruction_success_rate": "0.2",
                "reconstruction_success_ci_low": "0.19",
                "reconstruction_success_ci_high": "0.21",
                "audit_pass_rate": "0.02",
                "audit_pass_ci_low": "0.01",
                "audit_pass_ci_high": "0.03",
                "catastrophic_detection_rate": "0.99",
                "catastrophic_trials": "9500",
            },
        ],
        "parameters": {
            "independent_offline_probabilities": [0.0, 0.4],
            "seeds": [202600, 203000],
            "trials_per_scenario": 12000,
            "n": 32,
            "threshold": 22,
            "sample_size": 8,
            "required_audit_responses": 8,
            "domains": 4,
            "domain_outage_probability": 0.0,
        },
    },
    "domain": {
        "path": "prototype/results/domain_diversity.csv",
        "asset_id": "ASSET-DOMAIN-DIVERSITY",
        "evidence_id": "RID-C003-CORR-001",
        "experiment_id": "EXP-DOMAIN-DIVERSITY",
        "kind": "SEEDED_MONTE_CARLO",
        "fields": [
            "domains",
            "reconstruction_success_rate",
            "reconstruction_success_ci_low",
            "reconstruction_success_ci_high",
            "catastrophic_rate",
            "catastrophic_ci_low",
            "catastrophic_ci_high",
        ],
        "rows": [
            {
                "domains": "2",
                "reconstruction_success_rate": "0.72",
                "reconstruction_success_ci_low": "0.71",
                "reconstruction_success_ci_high": "0.73",
                "catastrophic_rate": "0.28",
                "catastrophic_ci_low": "0.27",
                "catastrophic_ci_high": "0.29",
            },
            {
                "domains": "16",
                "reconstruction_success_rate": "0.97",
                "reconstruction_success_ci_low": "0.96",
                "reconstruction_success_ci_high": "0.98",
                "catastrophic_rate": "0.03",
                "catastrophic_ci_low": "0.02",
                "catastrophic_ci_high": "0.04",
            },
        ],
        "parameters": {
            "domain_counts": [2, 16],
            "seeds": [3302, 3316],
            "trials_per_scenario": 20000,
            "n": 32,
            "threshold": 22,
            "independent_offline_probability": 0.01,
            "domain_outage_probability": 0.15,
            "sample_size_rule": "max(8, domains)",
            "required_audit_responses_rule": "max(8, domains)",
        },
    },
    "sampling": {
        "path": "prototype/results/sampling_strategy.csv",
        "asset_id": "ASSET-SAMPLING-STRATEGY",
        "evidence_id": "RID-C003-STRAT-001",
        "experiment_id": "EXP-SAMPLING-STRATEGY",
        "kind": "SEEDED_MATCHED_POLICY_MONTE_CARLO",
        "fields": [
            "sample_size",
            "strategy",
            "catastrophic_detection_rate",
            "catastrophic_detection_ci_low",
            "catastrophic_detection_ci_high",
            "catastrophic_trials",
            "audit_pass_rate",
            "audit_pass_ci_low",
            "audit_pass_ci_high",
        ],
        "rows": [
            {
                "sample_size": "4",
                "strategy": "uniform",
                "catastrophic_detection_rate": "0.95",
                "catastrophic_detection_ci_low": "0.94",
                "catastrophic_detection_ci_high": "0.96",
                "catastrophic_trials": "2994",
                "audit_pass_rate": "0.52",
                "audit_pass_ci_low": "0.51",
                "audit_pass_ci_high": "0.53",
            },
            {
                "sample_size": "4",
                "strategy": "stratified",
                "catastrophic_detection_rate": "1.0",
                "catastrophic_detection_ci_low": "0.99",
                "catastrophic_detection_ci_high": "1.0",
                "catastrophic_trials": "3003",
                "audit_pass_rate": "0.38",
                "audit_pass_ci_low": "0.37",
                "audit_pass_ci_high": "0.39",
            },
        ],
        "parameters": {
            "sample_sizes": [4],
            "strategies": ["uniform", "stratified"],
            "seeds": [5504],
            "seed_rule": "5500 + sample_size; shared by both strategies",
            "trials_per_scenario": 16000,
            "n": 32,
            "threshold": 22,
            "domains": 4,
            "independent_offline_probability": 0.01,
            "domain_outage_probability": 0.2,
            "required_audit_responses_rule": "sample_size",
        },
    },
}

ALLOWED_SOURCE_KEYS = ("iid", "sampling")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_case(root: Path) -> Path:
    _write_json(
        root / "research-case/program-state.json",
        {
            "status": "ACTIVE",
            "current_phase": "INTAKE",
            "resume_from": "INTAKE",
            "novelty_status": "UNRESOLVED",
            "solution_viability_status": "ASSERTED_ONLY",
            "acceptance_readiness": "NOT_ASSESSABLE",
        },
    )
    charter = root / "research-case/00-governance/program-charter.md"
    charter.parent.mkdir(parents=True, exist_ok=True)
    charter.write_text(
        "Final author order, corresponding-author designation, affiliation wording, "
        "institutional naming, and submission-time institutional authority remain deferred.\n",
        encoding="utf-8",
    )

    datasets: list[dict[str, object]] = []
    experiments: list[dict[str, object]] = []
    provenance_rows: list[dict[str, object]] = []
    evidence_rows: list[dict[str, object]] = []
    for spec in SOURCES.values():
        source = root / str(spec["path"])
        fields = list(spec["fields"])
        rows = list(spec["rows"])
        _write_csv(source, fields, rows)
        digest = _sha256(source)
        datasets.append(
            {
                "path": spec["path"],
                "sha256": digest,
                "row_count": len(rows),
                "columns": fields,
            }
        )
        experiments.append(
            {
                "experiment_id": spec["experiment_id"],
                "kind": spec["kind"],
                "datasets": [spec["path"]],
                "parameters": spec["parameters"],
            }
        )
        provenance_rows.append(
            {
                "asset_id": spec["asset_id"],
                "asset_type": "SIMULATION_OR_ANALYTIC_DATASET",
                "source": spec["path"],
                "authorization": "PREAUTHORIZATION_ONLY / NOT_SCIENTIFIC_EVIDENCE",
                "acquired_at": "SOURCE_DATE_EPOCH_OR_OMITTED",
                "sha256": digest,
                "processing": "Deterministic local experiment pipeline.",
                "owner": "root-integration-owner",
            }
        )
        evidence_rows.append(
            {
                "evidence_id": spec["evidence_id"],
                "claim_ids": "C003",
                "origin": "SIMULATED",
                "maturity": "V2 SIMULATED",
                "scope": "SIMULATED",
                "status": "PARTIAL",
                "authorized": "false",
                "independent": "false",
                "source_artifact": "04-data/provenance-manifest.csv",
                "source_asset_ids": spec["asset_id"],
                "authorization": "PREAUTHORIZATION_ONLY",
            }
        )

    _write_json(
        root / "prototype/results/experiment_manifest.json",
        {
            "authorization_boundary": "PREAUTHORIZATION_ONLY",
            "scientific_evidence_status": "NOT_SCIENTIFIC_EVIDENCE",
            "independence_status": "SAME_WORKSPACE_NOT_INDEPENDENT",
            "outputs": {"datasets": datasets},
            "experiments": experiments,
        },
    )
    _write_csv(
        root / "research-case/04-data/provenance-manifest.csv",
        ["asset_id", "asset_type", "source", "authorization", "acquired_at", "sha256", "processing", "owner"],
        provenance_rows,
    )
    _write_csv(
        root / "research-case/04-data/evidence-status.csv",
        ["evidence_id", "claim_ids", "origin", "maturity", "scope", "status", "authorized", "independent", "source_artifact", "source_asset_ids", "authorization"],
        evidence_rows,
    )
    return root


def _run(root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *extra],
        text=True,
        capture_output=True,
        check=False,
    )


def test_export_preserves_only_frozen_simulation_robustness_boundaries(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")

    result = _run(root)

    assert result.returncode == 0, result.stderr
    rows = _read_csv(root / "research-case/05-analysis/results/robustness-and-boundaries.csv")
    assert len(rows) == 4
    assert [row["robustness_id"] for row in rows] == [
        "ROB-IID-0000",
        "ROB-IID-0400",
        "ROB-SAMPLING-04-UNIFORM",
        "ROB-SAMPLING-04-STRATIFIED",
    ]
    assert {row["source_path"] for row in rows} == {
        SOURCES[key]["path"] for key in ALLOWED_SOURCE_KEYS
    }
    assert all(row["claim_ids"] == "C003" for row in rows)
    assert all(row["analysis_class"] == "PREAUTHORIZATION_SIMULATION_ROBUSTNESS_OR_BOUNDARY" for row in rows)
    assert all(row["analysis_status"] == "DRAFT_ROBUSTNESS_BOUNDARY_ONLY" for row in rows)
    assert all(row["authorized"] == "false" and row["independent"] == "false" for row in rows)
    assert all(row["evidence_origin"] == "SIMULATED" for row in rows)
    assert all(row["evidence_maturity"] == "V2 SIMULATED" for row in rows)
    assert all(row["claim_ceiling"] == "V0 ASSERTED" for row in rows)
    assert all("No production" in row["excluded_generality"] for row in rows)
    assert all("confirmatory" in row["notes"].lower() for row in rows)
    assert all("selective_withholding" not in row["source_path"] for row in rows)
    assert all("markov_temporal" not in row["source_path"] for row in rows)
    assert all("domain_diversity" not in row["source_path"] for row in rows)


def test_export_binds_conditions_to_declared_counts_and_seeds(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")
    assert _run(root).returncode == 0
    rows = {row["robustness_id"]: row for row in _read_csv(root / "research-case/05-analysis/results/robustness-and-boundaries.csv")}

    assert rows["ROB-IID-0400"]["sample_size"] == "12000"
    assert rows["ROB-IID-0400"]["seed"] == "203000"
    assert "offline_probability=0.4" in rows["ROB-IID-0400"]["condition"]
    assert "reconstruction_success_rate=0.2" in rows["ROB-IID-0400"]["result"]
    assert rows["ROB-SAMPLING-04-STRATIFIED"]["sample_size"] == "16000"
    assert rows["ROB-SAMPLING-04-STRATIFIED"]["seed"] == "5504"
    assert "matched seed" in rows["ROB-SAMPLING-04-STRATIFIED"]["comparison"]


def test_check_detects_output_source_or_manifest_drift(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "output")
    assert _run(root).returncode == 0
    output = root / "research-case/05-analysis/results/robustness-and-boundaries.csv"
    output.write_text(output.read_text().replace("DRAFT_ROBUSTNESS_BOUNDARY_ONLY", "CONFIRMATORY", 1), encoding="utf-8")
    result = _run(root, "--check")
    assert result.returncode == 1
    assert "robustness-and-boundaries output is stale" in result.stderr

    root = _write_case(tmp_path / "source")
    source = root / str(SOURCES["iid"]["path"])
    source.write_text(source.read_text().replace("0.4,0.2", "0.4,0.3", 1), encoding="utf-8")
    result = _run(root)
    assert result.returncode == 1
    assert "source hash mismatch" in result.stderr

    root = _write_case(tmp_path / "binding")
    manifest_path = root / "prototype/results/experiment_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["experiments"][0]["datasets"] = []
    _write_json(manifest_path, manifest)
    result = _run(root)
    assert result.returncode == 1
    assert "does not bind" in result.stderr


def test_refuses_phase_evidence_or_experiment_relabeling(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "phase")
    state_path = root / "research-case/program-state.json"
    state = json.loads(state_path.read_text())
    state["current_phase"] = "ANALYSIS"
    _write_json(state_path, state)
    result = _run(root)
    assert result.returncode == 1
    assert "current_phase expected INTAKE" in result.stderr

    root = _write_case(tmp_path / "evidence")
    evidence = root / "research-case/04-data/evidence-status.csv"
    evidence.write_text(evidence.read_text().replace("false,false", "true,true"), encoding="utf-8")
    result = _run(root)
    assert result.returncode == 1
    assert "evidence authorized expected false" in result.stderr

    root = _write_case(tmp_path / "experiment")
    manifest_path = root / "prototype/results/experiment_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["experiments"][0]["kind"] = "CONFIRMATORY"
    _write_json(manifest_path, manifest)
    result = _run(root)
    assert result.returncode == 1
    assert "experiment kind" in result.stderr

    root = _write_case(tmp_path / "seed")
    manifest_path = root / "prototype/results/experiment_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["experiments"][2]["parameters"]["seeds"] = [9999]
    _write_json(manifest_path, manifest)
    result = _run(root)
    assert result.returncode == 1
    assert "sampling seed mapping" in result.stderr
