from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export_reproducibility_report.py"
OUTPUT = ROOT / "research-case/05-analysis/reproducibility-report.md"
RECEIPT = ROOT / "prototype/results/engineering_qa/isolated_reproduction/receipt.json"


def _run(*extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(ROOT), *extra],
        text=True,
        capture_output=True,
        check=False,
    )


def test_report_is_fail_closed_and_evidence_bound() -> None:
    result = _run()
    assert result.returncode == 0, result.stderr

    text = OUTPUT.read_text(encoding="utf-8")
    assert "DRAFT / PREAUTHORIZATION / MECHANICAL-ONLY" in text
    assert "Current canonical phase: `INTAKE`" in text
    assert "Overall disposition: `CURRENT_TREE_REPLAY_REQUIRED`" in text
    assert "Scientific independence: `NOT_ESTABLISHED`" in text
    assert "Independent scientific reproduction: `MISSING`" in text
    assert "External validation: `MISSING`" in text
    assert "Primary confirmatory results: `NOT_COLLECTED`" in text
    assert "9 result slots" in text
    assert "10/10" in text
    assert "SECOND_AGENT_SAME_HOST_ISOLATED_COPY" in text
    assert "NOT_INDEPENDENT_SCIENTIFIC_VERIFICATION" in text
    assert "may not promote C001, C002, or C003" in text
    assert "no distributed deadline execution" in text


def test_check_detects_report_drift() -> None:
    assert _run().returncode == 0
    original = OUTPUT.read_text(encoding="utf-8")
    OUTPUT.write_text(original.replace("NOT_ESTABLISHED", "ESTABLISHED", 1), encoding="utf-8")
    result = _run("--check")
    assert result.returncode == 1
    assert "reproducibility report is stale" in result.stderr
    OUTPUT.write_text(original, encoding="utf-8")
    assert _run("--check").returncode == 0


def test_export_refuses_receipt_independence_relabeling() -> None:
    original = RECEIPT.read_text(encoding="utf-8")
    payload = json.loads(original)
    payload["scientific_evidence_status"] = "INDEPENDENT_SCIENTIFIC_VERIFICATION"
    RECEIPT.write_text(json.dumps(payload), encoding="utf-8")
    try:
        result = _run()
        assert result.returncode == 1
        assert "scientific evidence status must remain" in result.stderr
    finally:
        RECEIPT.write_text(original, encoding="utf-8")

