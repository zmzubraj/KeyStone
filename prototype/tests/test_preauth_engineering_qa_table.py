from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export_preauth_engineering_qa_table.py"
SPEC = importlib.util.spec_from_file_location("export_preauth_engineering_qa_table", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
table_export = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = table_export
SPEC.loader.exec_module(table_export)


def _crypto_receipt() -> dict[str, object]:
    path = ROOT / "prototype/results/engineering_qa/rid-c002-crypto-001-preauth-receipt.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_current_crypto_manifest_matches_hash_bound_receipt() -> None:
    table_export.validate_current_crypto_manifest(_crypto_receipt(), ROOT)


def test_crypto_manifest_mutation_is_rejected_by_receipt_hash(tmp_path: Path) -> None:
    receipt = copy.deepcopy(_crypto_receipt())
    relative = Path(table_export.EXPECTED_CRYPTO_MANIFEST_PATH)
    copied_manifest = tmp_path / relative
    copied_manifest.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / relative, copied_manifest)

    table_export.validate_current_crypto_manifest(receipt, tmp_path)
    copied_manifest.write_text(
        copied_manifest.read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )
    with pytest.raises(table_export.ExportError, match="manifest SHA-256 mismatch"):
        table_export.validate_current_crypto_manifest(receipt, tmp_path)


def test_wrong_or_escaping_manifest_path_is_rejected(tmp_path: Path) -> None:
    receipt = copy.deepcopy(_crypto_receipt())
    receipt["manifest_binding"]["manifest_path"] = "../outside-workspace.csv"

    with pytest.raises(table_export.ExportError, match="unexpected declared manifest path"):
        table_export.validate_current_crypto_manifest(receipt, tmp_path)


def test_hash_rebound_semantic_manifest_classification_drift_is_rejected(
    tmp_path: Path,
) -> None:
    receipt = copy.deepcopy(_crypto_receipt())
    relative = Path(table_export.EXPECTED_CRYPTO_MANIFEST_PATH)
    copied_manifest = tmp_path / relative
    copied_manifest.parent.mkdir(parents=True)

    with (ROOT / relative).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        assert fieldnames is not None
        rows = list(reader)
    target = next(row for row in rows if row["result_id"] == "RID-C002-CRYPTO-001")
    target["case_class"] = "SEMANTIC_DRIFT"
    with copied_manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    rebound_hash = hashlib.sha256(copied_manifest.read_bytes()).hexdigest()
    for snapshot_name in ("inputs", "inputs_before_execution", "inputs_after_execution"):
        manifest_entry = next(
            row
            for row in receipt["sha256"][snapshot_name]
            if row["path"] == table_export.EXPECTED_CRYPTO_MANIFEST_PATH
        )
        manifest_entry["sha256"] = rebound_hash

    with pytest.raises(table_export.ExportError, match="unexpected case classification"):
        table_export.validate_current_crypto_manifest(receipt, tmp_path)
