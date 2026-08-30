from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export_evidence_lineage.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_case(root: Path) -> Path:
    state = {
        "status": "ACTIVE",
        "current_phase": "INTAKE",
        "resume_from": "INTAKE",
        "novelty_status": "UNRESOLVED",
        "solution_viability_status": "ASSERTED_ONLY",
        "acceptance_readiness": "NOT_ASSESSABLE",
    }
    _write_json(root / "research-case/program-state.json", state)
    charter = root / "research-case/00-governance/program-charter.md"
    charter.parent.mkdir(parents=True, exist_ok=True)
    charter.write_text(
        "Final author order, corresponding-author designation, affiliation wording, "
        "institutional naming, and submission-time institutional authority remain deferred.\n",
        encoding="utf-8",
    )

    sources = {
        "paper/property_separation_obligations.md": "# Separation obligations\n",
        "prototype/results/baseline.json": '{"n":32,"threshold":22}\n',
        "prototype/results/crypto_benchmark.csv": "operation,seconds\nopen,0.1\n",
        "contracts/gas_report.csv": "operation,gas\nopen,100\n",
    }
    dataset_paths = [
        "prototype/results/theoretical_bound.csv",
        "prototype/results/iid_failure_sweep.csv",
        "prototype/results/domain_diversity.csv",
        "prototype/results/selective_withholding.csv",
        "prototype/results/sampling_strategy.csv",
        "prototype/results/exact_stratified_validation.csv",
        "prototype/results/markov_temporal_dependence.csv",
    ]
    for index, relative in enumerate(dataset_paths):
        sources[relative] = f"scenario,value\n{index},1\n"
    for relative, content in sources.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    manifest = {
        "authorization_boundary": "PREAUTHORIZATION_ONLY",
        "scientific_evidence_status": "NOT_SCIENTIFIC_EVIDENCE",
        "independence_status": "SAME_WORKSPACE_NOT_INDEPENDENT",
        "generation_timestamp": {
            "generated_at_utc": None,
            "policy": "SOURCE_DATE_EPOCH_OR_OMITTED",
        },
        "outputs": {
            "datasets": [
                {"path": relative, "sha256": _sha256(root / relative)}
                for relative in dataset_paths
            ]
        },
    }
    _write_json(root / "prototype/results/experiment_manifest.json", manifest)

    receipt = {
        "authorization_boundary": "PREAUTHORIZATION_ONLY",
        "scientific_evidence_status": "NOT_SCIENTIFIC_EVIDENCE",
        "independence_status": "SAME_WORKSPACE_NOT_INDEPENDENT",
        "completed_at_utc": "2026-08-29T01:05:32Z",
    }
    _write_json(
        root / "prototype/results/engineering_qa/rid-c002-crypto-001-preauth-receipt.json",
        receipt,
    )
    receipt["completed_at_utc"] = "2026-08-29T03:27:35Z"
    _write_json(
        root / "contracts/results/engineering_qa/rid-c002-contract-001-preauth-receipt.json",
        receipt,
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


def test_export_writes_traceable_but_non_authorizing_lineage(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")

    result = _run(root)

    assert result.returncode == 0, result.stderr
    provenance = _read_csv(root / "research-case/04-data/provenance-manifest.csv")
    evidence = _read_csv(root / "research-case/04-data/evidence-status.csv")
    assert {row["asset_id"] for row in provenance} >= {
        "ASSET-SELECTIVE-WITHHOLDING",
        "ASSET-CRYPTO-QA-RECEIPT",
        "ASSET-CONTRACT-QA-RECEIPT",
    }
    assert {row["evidence_id"] for row in evidence} == {
        "RID-C001-SEP-001",
        "RID-C001-STATIC-001",
        "RID-C002-CRYPTO-001",
        "RID-C002-CONTRACT-001",
        "RID-C003-IID-001",
        "RID-C003-CORR-001",
        "RID-C003-STRAT-001",
        "RID-C003-SW-001",
        "RID-C003-DEADLINE-001",
    }
    assert all(row["authorized"] == "false" for row in evidence)
    assert all(row["independent"] == "false" for row in evidence)
    assert not {row["status"] for row in evidence} & {"SUPPORTED", "VERIFIED", "PASS"}
    deadline = next(row for row in evidence if row["evidence_id"] == "RID-C003-DEADLINE-001")
    assert deadline["status"] == "BLOCKED"
    assert deadline["maturity"] == "V0 ASSERTED"
    assert deadline["source_artifact"] == "04-data/provenance-manifest.csv"


def test_check_detects_source_drift(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")
    assert _run(root).returncode == 0
    path = root / "prototype/results/selective_withholding.csv"
    path.write_text(path.read_text() + "changed,0\n", encoding="utf-8")

    result = _run(root, "--check")

    assert result.returncode == 1
    assert "source hash mismatch" in result.stderr


def test_check_detects_stale_outputs(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")
    assert _run(root).returncode == 0
    evidence = root / "research-case/04-data/evidence-status.csv"
    evidence.write_text(evidence.read_text().replace("PARTIAL", "PASS", 1), encoding="utf-8")

    result = _run(root, "--check")

    assert result.returncode == 1
    assert "evidence lineage outputs are stale" in result.stderr


def test_refuses_relabelled_or_post_intake_sources(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")
    manifest_path = root / "prototype/results/experiment_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["scientific_evidence_status"] = "SCIENTIFIC_EVIDENCE"
    _write_json(manifest_path, manifest)

    result = _run(root)

    assert result.returncode == 1
    assert "scientific_evidence_status" in result.stderr

    root = _write_case(tmp_path / "later")
    state_path = root / "research-case/program-state.json"
    state = json.loads(state_path.read_text())
    state["current_phase"] = "AUTHORIZED_EXECUTION"
    _write_json(state_path, state)

    result = _run(root)

    assert result.returncode == 1
    assert "current_phase expected INTAKE" in result.stderr


def test_refuses_author_metadata_freeze(tmp_path: Path) -> None:
    root = _write_case(tmp_path / "case")
    charter = root / "research-case/00-governance/program-charter.md"
    charter.write_text("Final author order is now frozen.\n", encoding="utf-8")

    result = _run(root)

    assert result.returncode == 1
    assert "author metadata deferral" in result.stderr
