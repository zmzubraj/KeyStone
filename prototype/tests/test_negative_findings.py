from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export_negative_findings.py"


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

    source = root / "prototype/results/selective_withholding.csv"
    fields = [
        "selective_withholders",
        "reconstruction_success_rate",
        "reconstruction_success_ci_low",
        "reconstruction_success_ci_high",
        "audit_pass_rate",
        "audit_pass_ci_low",
        "audit_pass_ci_high",
    ]
    rows: list[dict[str, object]] = []
    for withholders in range(15):
        divergent = withholders >= 11
        rows.append(
            {
                "selective_withholders": withholders,
                "reconstruction_success_rate": 0.0 if divergent else 1.0,
                "reconstruction_success_ci_low": 0.0 if divergent else 0.9990405567102987,
                "reconstruction_success_ci_high": 0.0009594432897014858 if divergent else 1.0,
                "audit_pass_rate": 1.0,
                "audit_pass_ci_low": 0.9990405567102987,
                "audit_pass_ci_high": 1.0,
            }
        )
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
                        "path": "prototype/results/selective_withholding.csv",
                        "sha256": _sha256(source),
                        "row_count": 15,
                        "columns": fields,
                    }
                ]
            },
            "experiments": [
                {
                    "experiment_id": "EXP-SELECTIVE-WITHHOLDING",
                    "kind": "SEEDED_MONTE_CARLO_NEGATIVE_RESULT",
                    "datasets": ["prototype/results/selective_withholding.csv"],
                    "parameters": {
                        "n": 32,
                        "threshold": 22,
                        "sample_size": 8,
                        "required_audit_responses": 8,
                        "selective_withholders": list(range(15)),
                        "trials_per_scenario": 4000,
                        "seeds": [4400 + value for value in range(15)],
                    },
                }
            ],
        },
    )
    _write_csv(
        root / "research-case/04-data/provenance-manifest.csv",
        ["asset_id", "asset_type", "source", "authorization", "acquired_at", "sha256", "processing", "owner"],
        [
            {
                "asset_id": "ASSET-SELECTIVE-WITHHOLDING",
                "asset_type": "SIMULATION_OR_ANALYTIC_DATASET",
                "source": "prototype/results/selective_withholding.csv",
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
                "evidence_id": "RID-C003-SW-001",
                "claim_ids": "C003",
                "origin": "SIMULATED",
                "maturity": "V2 SIMULATED",
                "scope": "SIMULATED",
                "status": "PARTIAL",
                "authorized": "false",
                "independent": "false",
                "source_artifact": "04-data/provenance-manifest.csv",
                "source_asset_ids": "ASSET-BASELINE|ASSET-SELECTIVE-WITHHOLDING",
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


def test_export_records_only_the_preserved_selective_withholding_gap(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")

    result = _run(root)

    assert result.returncode == 0, result.stderr
    rows = _read_csv(root / "research-case/05-analysis/results/negative-findings.csv")
    assert [row["finding_id"] for row in rows] == ["NEG-SW-11", "NEG-SW-12", "NEG-SW-13", "NEG-SW-14"]
    assert all(row["claim_ids"] == "C003" for row in rows)
    assert all(row["evidence_ids"] == "RID-C003-SW-001" for row in rows)
    assert all(row["analysis_class"] == "PREAUTHORIZATION_SIMULATION_NEGATIVE_FINDING" for row in rows)
    assert all(row["analysis_status"] == "DRAFT_NEGATIVE_FINDING_ONLY" for row in rows)
    assert all(row["authorized"] == "false" and row["independent"] == "false" for row in rows)
    assert all(row["claim_ceiling"] == "V0 ASSERTED" for row in rows)
    assert all(row["sample_size"] == "4000" for row in rows)
    assert rows[0]["test"] == "routine audit pass versus targeted dispute reconstruction"
    assert "audit_pass_rate=1.0" in rows[0]["result"]
    assert "reconstruction_success_rate=0.0" in rows[0]["result"]
    assert "does not imply" in rows[0]["implication"]
    assert "No production" in rows[0]["excluded_generality"]


def test_check_detects_output_or_source_drift(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "output")
    assert _run(root).returncode == 0
    output = root / "research-case/05-analysis/results/negative-findings.csv"
    output.write_text(output.read_text().replace("DRAFT_NEGATIVE_FINDING_ONLY", "CONFIRMATORY", 1), encoding="utf-8")
    result = _run(root, "--check")
    assert result.returncode == 1
    assert "negative-findings output is stale" in result.stderr

    root = _write_case(tmp_path / "source")
    source = root / "prototype/results/selective_withholding.csv"
    source.write_text(source.read_text() + "changed\n", encoding="utf-8")
    result = _run(root)
    assert result.returncode == 1
    assert "source hash mismatch" in result.stderr


def test_refuses_phase_evidence_or_manifest_relabeling(tmp_path: Path) -> None:
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

    root = _write_case(tmp_path / "manifest")
    manifest_path = root / "prototype/results/experiment_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["experiments"][0]["kind"] = "CONFIRMATORY"
    _write_json(manifest_path, manifest)
    result = _run(root)
    assert result.returncode == 1
    assert "experiment kind" in result.stderr

    root = _write_case(tmp_path / "dataset-binding")
    manifest_path = root / "prototype/results/experiment_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["experiments"][0]["datasets"] = []
    _write_json(manifest_path, manifest)
    result = _run(root)
    assert result.returncode == 1
    assert "does not bind" in result.stderr
