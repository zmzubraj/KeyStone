from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "export_pc03_design_amendment.py"
AMENDMENT = Path("research-case/03-design/pc03-prospective-amendment.md")
COUNTS = Path("research-case/03-design/pc03-prospective-counts.csv")
SEEDS = Path("research-case/03-design/pc03-seed-schedule.csv")

INPUTS = (
    "research-case/program-state.json",
    "research-case/00-governance/program-charter.md",
    "research-case/03-design/protocol.md",
    "research-case/03-design/analysis-plan.md",
    "research-case/03-design/power-or-precision.md",
    "research-case/03-design/preregistration-and-deviations.md",
    "research-case/03-design/pc03-independent-methods-challenge/design-assessment.md",
    "research-case/03-design/pc03-independent-methods-challenge/prospective-counts.csv",
    "research-case/03-design/pc03-independent-methods-challenge/calculation-notes.md",
)


def copy_inputs(target: Path) -> None:
    for rel in INPUTS:
        source = ROOT / rel
        destination = target / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def run_cli(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_amendment_is_minimal_result_blind_and_fail_closed(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copy_inputs(project)
    result = run_cli(project)
    assert result.returncode == 0, result.stderr or result.stdout

    text = (project / AMENDMENT).read_text(encoding="utf-8")
    assert "DRAFT / PREAUTHORIZATION / NON-EXECUTABLE" in text
    assert "does not authorize execution" in text
    assert "author metadata remains deferred" in text.lower()
    assert "exploratory outputs were not used" in text.lower()
    assert "developmental ai methods challenge" in text.lower()
    assert "32" in text and "4,096" in text and "131,072" in text
    assert "denominator mismatch" in text.lower()

    rows = {row["result_id"]: row for row in read_rows(project / COUNTS)}
    assert set(rows) == {
        "RID-C003-IID-001",
        "RID-C003-CORR-001",
        "RID-C003-STRAT-001",
        "RID-C003-SW-001",
        "RID-C003-DEADLINE-001",
    }

    included = {
        "RID-C003-IID-001": "iid-10pct-uniform",
        "RID-C003-STRAT-001": "sample-size-8",
        "RID-C003-SW-001": "selective-withholders-11",
    }
    for result_id, cell_fragment in included.items():
        row = rows[result_id]
        assert cell_fragment in row["cell_id"]
        assert row["planned_cells"] == "1"
        assert row["primary_seed_blocks_per_cell"] == "32"
        assert row["reserve_seed_blocks_per_cell"] == "4"
        assert row["draws_per_seed_block"] == "4096"
        assert row["primary_draws_per_cell"] == "131072"
        assert row["required_draws_per_cell"] == "73778"
        assert row["execution_status"] == "BLOCKED_PENDING_GATE"
        assert row["authorized"] == "false"
        assert row["independent"] == "false"
        assert row["observed_outcome"] == "NOT_COLLECTED"
        assert row["historical_output_reuse"] == "PROHIBITED_AS_CONFIRMATORY_EVIDENCE"

    assert rows["RID-C003-CORR-001"]["execution_status"] == "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE"
    assert rows["RID-C003-CORR-001"]["primary_draws_per_cell"] == "0"
    assert rows["RID-C003-DEADLINE-001"]["execution_status"] == "EXCLUDED_PENDING_ENVIRONMENT_PROFILE"
    assert rows["RID-C003-DEADLINE-001"]["primary_draws_per_cell"] == "0"


def test_seed_schedule_is_complete_unique_and_deterministic(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copy_inputs(project)
    assert run_cli(project).returncode == 0
    rows = read_rows(project / SEEDS)
    assert len(rows) == 3 * 36
    assert len({row["seed"] for row in rows}) == len(rows)
    assert {row["result_id"] for row in rows} == {
        "RID-C003-IID-001",
        "RID-C003-STRAT-001",
        "RID-C003-SW-001",
    }
    assert all(row["role"] in {"PRIMARY", "RESERVE"} for row in rows)
    assert all(row["execution_status"] == "BLOCKED_PENDING_GATE" for row in rows)

    before = tuple((project / path).read_bytes() for path in (AMENDMENT, COUNTS, SEEDS))
    assert run_cli(project).returncode == 0
    assert tuple((project / path).read_bytes() for path in (AMENDMENT, COUNTS, SEEDS)) == before
    assert run_cli(project, "--check").returncode == 0

    counts = project / COUNTS
    counts.write_text(counts.read_text(encoding="utf-8") + "DRIFT\n", encoding="utf-8")
    stale = run_cli(project, "--check")
    assert stale.returncode != 0
    assert "stale" in (stale.stdout + stale.stderr).lower()


def test_export_refuses_phase_promotion_author_freeze_or_missing_challenge(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copy_inputs(project)

    state_path = project / "research-case/program-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["current_phase"] = "STUDY_DESIGN"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    result = run_cli(project)
    assert result.returncode != 0
    assert "intake" in (result.stdout + result.stderr).lower()

    copy_inputs(project)
    charter = project / "research-case/00-governance/program-charter.md"
    charter.write_text("Final author order is frozen.\n", encoding="utf-8")
    result = run_cli(project)
    assert result.returncode != 0
    assert "author metadata deferral" in (result.stdout + result.stderr).lower()

    copy_inputs(project)
    (project / INPUTS[-1]).unlink()
    result = run_cli(project)
    assert result.returncode != 0
    assert "methods challenge" in (result.stdout + result.stderr).lower()


def test_outputs_exclude_contact_identity(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copy_inputs(project)
    assert run_cli(project).returncode == 0
    payload = b"\n".join((project / path).read_bytes() for path in (AMENDMENT, COUNTS, SEEDS))
    assert b"@gmail.com" not in payload
    assert b"@omu.ac.jp" not in payload
