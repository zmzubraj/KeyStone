from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest


PROJECT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT / "scripts/run_experiments.py"
SPEC = importlib.util.spec_from_file_location("run_experiments_manifest", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
run_experiments = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = run_experiments
SPEC.loader.exec_module(run_experiments)


def test_current_experiment_outputs_build_a_valid_preauthorization_manifest() -> None:
    manifest = run_experiments.build_experiment_manifest()

    run_experiments.validate_experiment_manifest(manifest)
    assert manifest["schema_id"] == "KEYSTONE_PREAUTH_EXPERIMENT_MANIFEST"
    assert manifest["status"] == "PRELIMINARY_PREAUTHORIZATION"
    assert manifest["scientific_evidence_status"] == "NOT_SCIENTIFIC_EVIDENCE"
    assert manifest["authorization_boundary"] == "PREAUTHORIZATION_ONLY"
    assert len(manifest["experiments"]) == 7
    assert len(manifest["outputs"]["datasets"]) == 7
    assert len(manifest["outputs"]["figures"]) == 10
    assert manifest["generation_timestamp"]["generated_at_utc"] is None


@pytest.mark.parametrize("drift_kind", ["hash", "row_count"])
def test_manifest_validation_rejects_stale_dataset_hash_or_row_count(
    drift_kind: str,
) -> None:
    manifest = run_experiments.build_experiment_manifest()
    stale = copy.deepcopy(manifest)
    first = stale["outputs"]["datasets"][0]
    if drift_kind == "hash":
        first["sha256"] = "0" * 64
    else:
        first["row_count"] += 1

    with pytest.raises(run_experiments.ManifestError, match="dataset .* mismatch"):
        run_experiments.validate_experiment_manifest(stale)


def test_checked_in_manifest_matches_current_outputs() -> None:
    manifest = json.loads((PROJECT / "results/experiment_manifest.json").read_text())
    run_experiments.validate_experiment_manifest(manifest)

