from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export_exploratory_findings.py"


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

    source = root / "prototype/results/markov_temporal_dependence.csv"
    fields = [
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
    ]
    rows = [
        {
            "audits": 1,
            "trials": 12000,
            "seed": 20260831,
            "online_to_offline": 0.22,
            "offline_to_online": 0.08,
            "final_catastrophic_trials": 1278,
            "all_audits_pass_and_final_catastrophic_count": 478,
            "conditional_sequence_false_accept_rate": 0.37402190923317685,
            "conditional_sequence_false_accept_ci_low": 0.3479081526059559,
            "conditional_sequence_false_accept_ci_high": 0.4008907352875258,
            "static_set_repeated_bound": 0.42424242424242425,
        },
        {
            "audits": 8,
            "trials": 12000,
            "seed": 20260838,
            "online_to_offline": 0.22,
            "offline_to_online": 0.08,
            "final_catastrophic_trials": 11850,
            "all_audits_pass_and_final_catastrophic_count": 4,
            "conditional_sequence_false_accept_rate": 0.00033755274261603374,
            "conditional_sequence_false_accept_ci_low": 0.00013127525234485365,
            "conditional_sequence_false_accept_ci_high": 0.0008676801379250781,
            "static_set_repeated_bound": 0.0010493316358127659,
        },
    ]
    _write_csv(source, fields, rows)
    _write_json(
        root / "prototype/results/experiment_manifest.json",
        {
            "authorization_boundary": "PREAUTHORIZATION_ONLY",
            "scientific_evidence_status": "NOT_SCIENTIFIC_EVIDENCE",
            "independence_status": "SAME_WORKSPACE_NOT_INDEPENDENT",
            "outputs": {
                "datasets": [
                    {
                        "path": "prototype/results/markov_temporal_dependence.csv",
                        "sha256": _sha256(source),
                        "row_count": len(rows),
                        "columns": fields,
                    }
                ]
            },
        },
    )
    _write_csv(
        root / "research-case/04-data/provenance-manifest.csv",
        ["asset_id", "asset_type", "source", "authorization", "acquired_at", "sha256", "processing", "owner"],
        [
            {
                "asset_id": "ASSET-MARKOV-TEMPORAL-DEPENDENCE",
                "asset_type": "SIMULATION_OR_ANALYTIC_DATASET",
                "source": "prototype/results/markov_temporal_dependence.csv",
                "authorization": "PREAUTHORIZATION_ONLY / NOT_SCIENTIFIC_EVIDENCE",
                "acquired_at": "SOURCE_DATE_EPOCH_OR_OMITTED",
                "sha256": _sha256(source),
                "processing": "Deterministic local experiment pipeline.",
                "owner": "root-integration-owner",
            }
        ],
    )
    _write_csv(
        root / "research-case/04-data/evidence-status.csv",
        ["evidence_id", "claim_ids", "origin", "maturity", "scope", "status", "authorized", "independent", "source_artifact", "source_asset_ids", "authorization"],
        [
            {
                "evidence_id": "RID-C003-CORR-001",
                "claim_ids": "C003",
                "origin": "SIMULATED",
                "maturity": "V2 SIMULATED",
                "scope": "SIMULATED",
                "status": "PARTIAL",
                "authorized": "false",
                "independent": "false",
                "source_artifact": "04-data/provenance-manifest.csv",
                "source_asset_ids": "ASSET-DOMAIN-DIVERSITY|ASSET-MARKOV-TEMPORAL-DEPENDENCE",
                "authorization": "PREAUTHORIZATION_ONLY",
            }
        ],
    )
    return root


def _run(root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *extra],
        text=True,
        capture_output=True,
        check=False,
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_export_quarantines_markov_rows_as_exploratory_only(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")

    result = _run(root)

    assert result.returncode == 0, result.stderr
    rows = _read_csv(root / "research-case/05-analysis/results/exploratory-findings.csv")
    assert [row["finding_id"] for row in rows] == [
        "EXPLORE-MARKOV-AUDITS-1",
        "EXPLORE-MARKOV-AUDITS-8",
    ]
    assert all(row["claim_id"] == "C003" for row in rows)
    assert all(row["evidence_ids"] == "RID-C003-CORR-001" for row in rows)
    assert all(row["analysis_class"] == "EXPLORATORY_POST_HOC_PREAUTHORIZATION" for row in rows)
    assert all(row["analysis_status"] == "EXPLORATORY_ONLY" for row in rows)
    assert all(row["authorized"] == "false" for row in rows)
    assert all(row["independent"] == "false" for row in rows)
    assert all(row["evidence_origin"] == "SIMULATED" for row in rows)
    assert all(row["evidence_maturity"] == "V2 SIMULATED" for row in rows)
    assert all(row["claim_ceiling"] == "V0 ASSERTED" for row in rows)
    assert rows[0]["sample_size"] == "1278"
    assert rows[0]["effect_estimate"] == "0.37402190923317685"
    assert rows[0]["uncertainty_interval"] == "[0.3479081526059559, 0.4008907352875258]"
    assert "not interchangeable" in rows[0]["interpretation_boundary"]
    assert "no hypothesis test" in rows[0]["notes"].lower()


def test_check_detects_source_and_output_drift(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")
    assert _run(root).returncode == 0
    output = root / "research-case/05-analysis/results/exploratory-findings.csv"
    output.write_text(output.read_text().replace("EXPLORATORY_ONLY", "CONFIRMATORY", 1), encoding="utf-8")
    result = _run(root, "--check")
    assert result.returncode == 1
    assert "exploratory findings output is stale" in result.stderr

    root = _write_case(tmp_path / "drift")
    assert _run(root).returncode == 0
    source = root / "prototype/results/markov_temporal_dependence.csv"
    source.write_text(source.read_text() + "changed\n", encoding="utf-8")
    result = _run(root, "--check")
    assert result.returncode == 1
    assert "source hash mismatch" in result.stderr


def test_refuses_phase_or_evidence_relabeling(tmp_path: Path) -> None:
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
    evidence.write_text(evidence.read_text().replace("PARTIAL,false,false", "VERIFIED,true,true"), encoding="utf-8")
    result = _run(root)
    assert result.returncode == 1
    assert "evidence status expected PARTIAL" in result.stderr or "authorized expected false" in result.stderr


def test_refuses_provenance_or_author_metadata_drift(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "provenance")
    provenance = root / "research-case/04-data/provenance-manifest.csv"
    provenance.write_text(provenance.read_text().replace("PREAUTHORIZATION_ONLY / NOT_SCIENTIFIC_EVIDENCE", "AUTHORIZED_SCIENTIFIC_EVIDENCE"), encoding="utf-8")
    result = _run(root)
    assert result.returncode == 1
    assert "provenance authorization boundary" in result.stderr

    root = _write_case(tmp_path / "authors")
    charter = root / "research-case/00-governance/program-charter.md"
    charter.write_text("Final author order is frozen.\n", encoding="utf-8")
    result = _run(root)
    assert result.returncode == 1
    assert "author metadata deferral" in result.stderr
