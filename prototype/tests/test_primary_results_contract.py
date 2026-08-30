from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export_primary_results_contract.py"
OUTPUT = ROOT / "research-case/05-analysis/results/primary-results.csv"


RESULT_IDS = {
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


def _run(*extra: str, root: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *extra],
        text=True,
        capture_output=True,
        check=False,
    )


def _rows(path: Path = OUTPUT) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_export_is_complete_result_blind_and_fail_closed() -> None:
    result = _run()
    assert result.returncode == 0, result.stderr

    rows = _rows()
    assert {row["result_id"] for row in rows} == RESULT_IDS
    assert {row["estimand_id"] for row in rows} == {f"EST-{index:02d}" for index in range(1, 10)}
    assert all(row["observed_outcome"] == "NOT_COLLECTED" for row in rows)
    assert all(row["estimate"] == "NOT_ESTIMATED" for row in rows)
    assert all(row["uncertainty"] == "NOT_ESTIMATED" for row in rows)
    assert all(row["authorized"] == "false" for row in rows)
    assert all(row["independent"] == "false" for row in rows)
    assert all(row["analysis_status"] == "DRAFT_RESULT_CONTRACT_ONLY" for row in rows)
    assert all(row["evidence_maturity"] == "V0 ASSERTED" for row in rows)
    assert all(row["claim_ceiling"] == "V0 ASSERTED" for row in rows)
    assert all(row["source_contract"] == "research-case/02-feasibility/pilot-run-contract.csv" for row in rows)

    excluded = {
        row["result_id"]: row["execution_status"]
        for row in rows
        if row["result_id"] in {"RID-C003-CORR-001", "RID-C003-DEADLINE-001"}
    }
    assert excluded == {
        "RID-C003-CORR-001": "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE",
        "RID-C003-DEADLINE-001": "EXCLUDED_PENDING_ENVIRONMENT_PROFILE",
    }


def test_check_detects_output_drift() -> None:
    assert _run().returncode == 0
    original = OUTPUT.read_text(encoding="utf-8")
    OUTPUT.write_text(original.replace("NOT_ESTIMATED", "0.99", 1), encoding="utf-8")
    result = _run("--check")
    assert result.returncode == 1
    assert "primary-results contract is stale" in result.stderr
    OUTPUT.write_text(original, encoding="utf-8")
    assert _run("--check").returncode == 0


def test_export_refuses_phase_promotion_or_authorized_contract(tmp_path: Path) -> None:
    case = tmp_path / "case"
    (case / "research-case/00-governance").mkdir(parents=True)
    (case / "research-case/02-feasibility").mkdir(parents=True)
    (case / "research-case/03-design").mkdir(parents=True)

    state = json.loads((ROOT / "research-case/program-state.json").read_text(encoding="utf-8"))
    state["current_phase"] = "ANALYSIS"
    (case / "research-case/program-state.json").write_text(json.dumps(state), encoding="utf-8")
    for relative in (
        "research-case/00-governance/program-charter.md",
        "research-case/02-feasibility/pilot-run-contract.csv",
        "research-case/03-design/analysis-plan.md",
    ):
        target = case / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())

    result = _run(root=case)
    assert result.returncode == 1
    assert "current_phase expected INTAKE" in result.stderr

    state["current_phase"] = "INTAKE"
    (case / "research-case/program-state.json").write_text(json.dumps(state), encoding="utf-8")
    contract = case / "research-case/02-feasibility/pilot-run-contract.csv"
    contract.write_text(contract.read_text(encoding="utf-8").replace(",false,false,", ",true,false,", 1), encoding="utf-8")
    result = _run(root=case)
    assert result.returncode == 1
    assert "authorized must remain false" in result.stderr
