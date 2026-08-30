from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export_confirmatory_pilot_plan.py"
PLAN = ROOT / "research-case/02-feasibility/pilot-plan.md"
CONTRACT = ROOT / "research-case/02-feasibility/pilot-run-contract.csv"


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


def _run(*extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(ROOT), *extra],
        text=True,
        capture_output=True,
        check=False,
    )


def _rows() -> list[dict[str, str]]:
    with CONTRACT.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_exported_plan_is_fail_closed_and_complete() -> None:
    result = _run()
    assert result.returncode == 0, result.stderr

    text = PLAN.read_text(encoding="utf-8")
    assert "DRAFT / PREAUTHORIZATION / NON-EXECUTABLE" in text
    assert "Decision: `BLOCKED`" in text
    assert "Recommended later path: `PILOT_FIRST`" in text
    assert "Current canonical phase: `INTAKE`" in text
    assert "Final author order" in text and "remain deferred" in text
    assert "does not issue `GO`" in text
    assert "must never be relabeled" in text
    assert "no separate pilot execution approval exists" in text
    assert "authority and study-profile evidence still need independent verification" not in text
    assert all(result_id in text for result_id in RESULT_IDS)

    rows = _rows()
    assert {row["result_id"] for row in rows} == RESULT_IDS
    assert all(
        row["execution_status"] in {
            "BLOCKED_PENDING_GATE",
            "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE",
            "EXCLUDED_PENDING_ENVIRONMENT_PROFILE",
        }
        for row in rows
    )
    assert all(row["authorized"] == "false" for row in rows)
    assert all(row["independent"] == "false" for row in rows)
    assert all(row["observed_outcome"] == "NOT_COLLECTED" for row in rows)
    assert all(row["historical_output_reuse"] == "PROHIBITED_AS_CONFIRMATORY_EVIDENCE" for row in rows)
    assert all(row["output_status"] == "MISSING_NOT_AUTHORIZED" for row in rows)


def test_pc03_counts_are_bound_and_deadline_profile_remains_excluded() -> None:
    assert _run().returncode == 0
    rows = {row["result_id"]: row for row in _rows()}
    scheduled = {
        "RID-C003-IID-001",
        "RID-C003-STRAT-001",
        "RID-C003-SW-001",
    }
    assert all(
        rows[result_id]["planned_replicates"] == "32_PRIMARY_SEED_BLOCKS_X_4096_DRAWS_PER_CELL_PLUS_4_RESERVE"
        for result_id in scheduled
    )
    assert rows["RID-C003-CORR-001"]["planned_replicates"] == "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE"
    assert rows["RID-C003-CORR-001"]["environment_status"] == "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE"
    assert rows["RID-C003-DEADLINE-001"]["planned_replicates"] == "EXCLUDED_PENDING_ENVIRONMENT_PROFILE"
    assert rows["RID-C003-DEADLINE-001"]["environment_status"] == "EXCLUDED_PENDING_ENVIRONMENT_PROFILE"
    assert rows["RID-C003-DEADLINE-001"]["mpp_lane"] == "EXTENDED_FULL_PAPER"
    assert rows["RID-C003-SW-001"]["mpp_lane"] == "MINIMUM_SHORT_PAPER_CORE"


def test_check_detects_plan_or_contract_drift(tmp_path: Path) -> None:
    assert _run().returncode == 0
    original_plan = PLAN.read_text(encoding="utf-8")
    PLAN.write_text(original_plan.replace("Decision: `BLOCKED`", "Decision: `GO`", 1), encoding="utf-8")
    result = _run("--check")
    assert result.returncode == 1
    assert "pilot plan is stale" in result.stderr
    PLAN.write_text(original_plan, encoding="utf-8")

    original_contract = CONTRACT.read_text(encoding="utf-8")
    CONTRACT.write_text(original_contract.replace("BLOCKED_PENDING_GATE", "AUTHORIZED", 1), encoding="utf-8")
    result = _run("--check")
    assert result.returncode == 1
    assert "pilot run contract is stale" in result.stderr
    CONTRACT.write_text(original_contract, encoding="utf-8")
    assert _run("--check").returncode == 0


def test_export_refuses_canonical_phase_or_metadata_freeze(tmp_path: Path) -> None:
    case = tmp_path / "case"
    (case / "research-case/00-governance").mkdir(parents=True)
    (case / "research-case/03-design").mkdir(parents=True)
    state = json.loads((ROOT / "research-case/program-state.json").read_text(encoding="utf-8"))
    state["current_phase"] = "ANALYSIS"
    (case / "research-case/program-state.json").write_text(json.dumps(state), encoding="utf-8")
    (case / "research-case/00-governance/program-charter.md").write_text(
        (ROOT / "research-case/00-governance/program-charter.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    for name in ("protocol.md", "analysis-plan.md", "power-or-precision.md", "preregistration-and-deviations.md"):
        (case / f"research-case/03-design/{name}").write_text(
            (ROOT / f"research-case/03-design/{name}").read_text(encoding="utf-8"), encoding="utf-8"
        )
    for name in ("pc03-prospective-amendment.md", "pc03-prospective-counts.csv", "pc03-seed-schedule.csv"):
        (case / f"research-case/03-design/{name}").write_text(
            (ROOT / f"research-case/03-design/{name}").read_text(encoding="utf-8"), encoding="utf-8"
        )
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(case)], text=True, capture_output=True, check=False
    )
    assert result.returncode == 1
    assert "current_phase expected INTAKE" in result.stderr

    state["current_phase"] = "INTAKE"
    (case / "research-case/program-state.json").write_text(json.dumps(state), encoding="utf-8")
    (case / "research-case/00-governance/program-charter.md").write_text(
        "Final author order is frozen.\n", encoding="utf-8"
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(case)], text=True, capture_output=True, check=False
    )
    assert result.returncode == 1
    assert "author metadata deferral" in result.stderr
