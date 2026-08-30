from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export_preliminary_table_lineage_receipt.py"
SPEC = importlib.util.spec_from_file_location(
    "export_preliminary_table_lineage_receipt", SCRIPT
)
assert SPEC is not None and SPEC.loader is not None
lineage = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = lineage
SPEC.loader.exec_module(lineage)


def test_current_preliminary_table_lineage_snapshot_is_valid() -> None:
    snapshot = lineage.collect_workspace_snapshot(ROOT)
    assert [row["row_count"] for row in snapshot["inputs"]] == [4, 1, 8, 4, 3]
    assert snapshot["classification"] == {
        "evidence_stage": "PRELIMINARY",
        "authorization_boundary": "PREAUTHORIZATION_ONLY",
        "scientific_evidence_status": "NOT_SCIENTIFIC_EVIDENCE",
        "independence_status": "SAME_WORKSPACE_NOT_INDEPENDENT",
        "canonical_table_status": "NOT_CANONICAL_T_SERIES",
    }


def test_input_hash_drift_is_rejected(tmp_path: Path) -> None:
    relative = Path("prototype/results/baseline.json")
    copied = tmp_path / relative
    copied.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / relative, copied)

    before = lineage.hash_relative_paths(tmp_path, (relative,))
    copied.write_text(copied.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    after = lineage.hash_relative_paths(tmp_path, (relative,))

    with pytest.raises(lineage.LineageError, match="artifact drift"):
        lineage.require_no_artifact_drift(before, after)


def test_table_check_argv_semantics_are_interpreter_portable() -> None:
    semantic_a, executed_a = lineage.table_check_argv("/runtime-a/python")
    semantic_b, executed_b = lineage.table_check_argv("/runtime-b/python")

    assert semantic_a == semantic_b
    assert executed_a != executed_b
    lineage.validate_table_check_argv_record(
        {"command_argv": semantic_a, "executed_argv": executed_a}
    )
    lineage.validate_table_check_argv_record(
        {"command_argv": semantic_b, "executed_argv": executed_b}
    )
