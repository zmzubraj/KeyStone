from __future__ import annotations

import sys
import hashlib
import json
from pathlib import Path

import pytest


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

import export_crypto_case_receipt as receipt  # noqa: E402


def test_case_mapping_rejects_duplicate_case_ids_and_test_nodes() -> None:
    valid = (
        receipt.CaseSpec("CASE-1", "tests/test_dleq.py::test_one", "direct"),
        receipt.CaseSpec("CASE-2", "tests/test_shamir.py::test_two", "supporting"),
    )
    receipt.validate_case_specs(valid)

    with pytest.raises(receipt.ReceiptError, match="duplicate case_id"):
        receipt.validate_case_specs((valid[0], valid[0]))

    with pytest.raises(receipt.ReceiptError, match="duplicate test_node_id"):
        receipt.validate_case_specs(
            (
                valid[0],
                receipt.CaseSpec("CASE-3", valid[0].test_node_id, "direct"),
            )
        )


def test_junit_parser_fails_closed_on_missing_or_duplicate_cases(tmp_path: Path) -> None:
    specs = (
        receipt.CaseSpec("CASE-1", "tests/test_dleq.py::test_one", "direct"),
        receipt.CaseSpec("CASE-2", "tests/test_shamir.py::test_two", "supporting"),
    )

    complete = tmp_path / "complete.xml"
    complete.write_text(
        """<?xml version='1.0' encoding='utf-8'?>
<testsuites><testsuite>
  <testcase classname="tests.test_one" name="test_one" time="0.1" />
  <testcase classname="tests.test_two" name="test_two" time="0.2" />
</testsuite></testsuites>
""",
        encoding="utf-8",
    )
    observed = receipt.parse_junit_results(complete, specs)
    assert [row.status for row in observed] == ["PASS", "PASS"]

    missing = tmp_path / "missing.xml"
    missing.write_text(
        """<?xml version='1.0' encoding='utf-8'?>
<testsuites><testsuite>
  <testcase classname="tests.test_one" name="test_one" time="0.1" />
</testsuite></testsuites>
""",
        encoding="utf-8",
    )
    with pytest.raises(receipt.ReceiptError, match="missing test results"):
        receipt.parse_junit_results(missing, specs)

    duplicate = tmp_path / "duplicate.xml"
    duplicate.write_text(
        """<?xml version='1.0' encoding='utf-8'?>
<testsuites><testsuite>
  <testcase classname="tests.test_one" name="test_one" time="0.1" />
  <testcase classname="tests.test_one" name="test_one" time="0.1" />
  <testcase classname="tests.test_two" name="test_two" time="0.2" />
</testsuite></testsuites>
""",
        encoding="utf-8",
    )
    with pytest.raises(receipt.ReceiptError, match="duplicate test results"):
        receipt.parse_junit_results(duplicate, specs)


def test_receipt_cleanup_and_atomic_sidecar_publish(tmp_path: Path) -> None:
    receipt_path = tmp_path / "receipt.json"
    sidecar_path = tmp_path / "receipt.json.sha256"
    receipt_path.write_text("stale receipt", encoding="utf-8")
    sidecar_path.write_text("stale hash", encoding="utf-8")

    receipt.remove_stale_receipt_outputs(receipt_path, sidecar_path)
    assert not receipt_path.exists()
    assert not sidecar_path.exists()

    rendered = json.dumps({"overall_status": "PASS"}, sort_keys=True) + "\n"
    published_hash = receipt.atomic_publish_receipt(receipt_path, sidecar_path, rendered)
    assert receipt_path.read_text(encoding="utf-8") == rendered
    assert published_hash == hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    assert sidecar_path.read_text(encoding="utf-8") == (
        f"{published_hash}  {receipt_path.name}\n"
    )
    assert not list(tmp_path.glob(".*.tmp"))


def test_input_hash_drift_comparison_fails_closed() -> None:
    before = [
        {"path": "a.py", "sha256": "a" * 64},
        {"path": "b.py", "sha256": "b" * 64},
    ]
    receipt.require_unchanged_input_hashes(before, list(before))

    after = [
        {"path": "a.py", "sha256": "c" * 64},
        {"path": "b.py", "sha256": "b" * 64},
    ]
    with pytest.raises(receipt.ReceiptError, match="input drift"):
        receipt.require_unchanged_input_hashes(before, after)


def test_manifest_binding_is_complete_and_fails_on_missing_row() -> None:
    manifest_rows = receipt.read_crypto_manifest_rows(receipt.MANIFEST_PATH)
    validated = receipt.validate_manifest_bindings(
        manifest_rows,
        receipt.MANIFEST_BINDINGS,
        receipt.CASE_SPECS,
    )
    assert len(validated) == 19
    assert {row["binding_type"] for row in validated} <= {
        "exact",
        "bundled",
        "alias",
        "unmapped",
    }

    with pytest.raises(receipt.ReceiptError, match="manifest binding coverage mismatch"):
        receipt.validate_manifest_bindings(
            manifest_rows,
            receipt.MANIFEST_BINDINGS[:-1],
            receipt.CASE_SPECS,
        )
