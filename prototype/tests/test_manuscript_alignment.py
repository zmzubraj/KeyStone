from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/check_manuscript_alignment.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _build_case(root: Path) -> Path:
    state = {
        "status": "ACTIVE",
        "current_phase": "INTAKE",
        "resume_from": "INTAKE",
        "novelty_status": "UNRESOLVED",
        "feasibility_decision": "UNASSESSED",
        "solution_viability_status": "ASSERTED_ONLY",
        "acceptance_readiness": "NOT_ASSESSABLE",
        "maturity_stage": "CONCEPT",
    }
    _write(
        root / "research-case/program-state.json",
        json.dumps(state, indent=2, sort_keys=True) + "\n",
    )
    _write(root / "diagrams/d1.svg", "<svg/>\n")
    _write(root / "prototype/results/figures/f1.svg", "<svg/>\n")
    _write(
        root / "paper/references.bib",
        "@article{known2026,\n  title={Known work},\n  author={A. Author}\n}\n",
    )
    _write(root / "scripts/check_manuscript_alignment.py", "# manifest-bound checker stub\n")
    _write(root / "prototype/tests/test_manuscript_alignment.py", "# manifest-bound tests stub\n")
    _write(root / "research-case/05-analysis/results/negative-findings.csv", "result_id,status\nRID-NEG-001,MISSING\n")
    _write(root / "research-case/05-analysis/results/robustness-and-boundaries.csv", "result_id,status\nRID-ROB-001,MISSING\n")
    _write(root / "scripts/export_negative_findings.py", "# negative findings exporter stub\n")
    _write(root / "scripts/export_robustness_boundaries.py", "# robustness boundaries exporter stub\n")
    _write(root / "prototype/tests/test_negative_findings.py", "# negative findings tests stub\n")
    _write(root / "prototype/tests/test_robustness_boundaries.py", "# robustness boundaries tests stub\n")
    _write(
        root / "research-case/07-manuscript/manuscript.md",
        """# Draft

Status: `DRAFT / PRE-MANUSCRIPT / PRE-AUTHORIZATION`

Novelty remains `UNRESOLVED`; feasibility remains `UNASSESSED`; execution is not authorized.
Final author order, corresponding-author designation, and exact affiliation wording are deferred.

Claims: `C001`, `C002`, and `C003` [@known2026].

![D1. Architecture](../../diagrams/d1.svg)
![F1. Result](../../prototype/results/figures/f1.svg)

Tables: `T1`, `T2`, `T3`, `T4`, `T5`, `T6`, `T7`, `T8`.
Diagrams: `D1`, `D2`, `D3`, `D4`, `D5`, `D6`, `D7`, `D8`.
Figures: `F1`, `F2`, `F3`, `F4`, `F5`.
""",
    )
    matrix_path = root / "research-case/07-manuscript/claim-evidence-matrix.csv"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "claim_id",
        "claim_text",
        "current_status",
        "blocked_by",
        "allowed_wording",
    ]
    rows = {
        "C001": {
            "claim_text": "C001",
            "current_status": "BLOCKED",
            "blocked_by": "NOVELTY_UNRESOLVED; signed independent closure absent",
            "allowed_wording": "This paper studies|under the stated static catastrophic model",
        },
        "C002": {
            "claim_text": "C002",
            "current_status": "AT_RISK",
            "blocked_by": "independent reproduction and external review are missing",
            "allowed_wording": "internal prototype evidence shows|local reproducibility evidence records",
        },
        "C003": {
            "claim_text": "C003",
            "current_status": "AT_RISK",
            "blocked_by": "RID-C003-DEADLINE-001 absent; independent reproduction and external validation are missing; F6-F8 remain future outputs",
            "allowed_wording": "bounded internal evidence indicates|within the declared model|conditional on synchrony assumptions|selective withholding remains a limitation",
        },
    }
    with matrix_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for claim_id in ("C001", "C002", "C003"):
            writer.writerow({"claim_id": claim_id, **rows[claim_id]})
    _write(
        root / "research-case/07-manuscript/claim-graph.json",
        json.dumps(
            {"claims": {claim_id: {"claim_id": claim_id} for claim_id in ("C001", "C002", "C003")}},
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    sources = []
    for source_id, relative in (
        ("SRC-MANUSCRIPT", "research-case/07-manuscript/manuscript.md"),
        ("SRC-BIB", "paper/references.bib"),
        ("SRC-MANUSCRIPT-ALIGNMENT-CHECKER", "scripts/check_manuscript_alignment.py"),
        ("SRC-MANUSCRIPT-ALIGNMENT-TESTS", "prototype/tests/test_manuscript_alignment.py"),
        ("SRC-CANONICAL-NEGATIVE-FINDINGS", "research-case/05-analysis/results/negative-findings.csv"),
        ("SRC-CANONICAL-ROBUSTNESS-BOUNDARIES", "research-case/05-analysis/results/robustness-and-boundaries.csv"),
        ("SRC-NEGATIVE-FINDINGS-EXPORTER", "scripts/export_negative_findings.py"),
        ("SRC-ROBUSTNESS-BOUNDARIES-EXPORTER", "scripts/export_robustness_boundaries.py"),
        ("SRC-NEGATIVE-FINDINGS-TESTS", "prototype/tests/test_negative_findings.py"),
        ("SRC-ROBUSTNESS-BOUNDARIES-TESTS", "prototype/tests/test_robustness_boundaries.py"),
    ):
        path = root / relative
        sources.append(
            {
                "source_id": source_id,
                "path": relative,
                "path_base": "workspace_root",
                "sha256": _sha256(path),
            }
        )
    _write(
        root / "research-case/07-manuscript/source-manifest.json",
        json.dumps({"schema_version": 1, "sources": sources}, indent=2, sort_keys=True) + "\n",
    )
    return root


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        text=True,
        capture_output=True,
        check=False,
    )


def test_valid_alignment_passes_with_a_machine_readable_summary(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")

    result = _run(root)

    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary == {
        "citation_count": 1,
        "claim_ids": ["C001", "C002", "C003"],
        "diagram_ids": ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"],
        "figure_ids": ["F1", "F2", "F3", "F4", "F5"],
        "image_reference_count": 2,
        "source_count": 10,
        "status": "PASS",
        "table_ids": ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"],
    }


def test_unknown_citation_fails_closed(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")
    manuscript = root / "research-case/07-manuscript/manuscript.md"
    manuscript.write_text(manuscript.read_text() + "\nUnknown [@missing2026].\n", encoding="utf-8")

    result = _run(root)

    assert result.returncode == 1
    assert "unknown citation key: missing2026" in result.stderr


def test_fail_closed_markers_may_span_markdown_line_wraps(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")
    manuscript = root / "research-case/07-manuscript/manuscript.md"
    manuscript.write_text(
        manuscript.read_text().replace("execution is not authorized", "execution is not\nauthorized"),
        encoding="utf-8",
    )
    source_manifest_path = root / "research-case/07-manuscript/source-manifest.json"
    source_manifest = json.loads(source_manifest_path.read_text())
    source_manifest["sources"][0]["sha256"] = _sha256(manuscript)
    source_manifest_path.write_text(json.dumps(source_manifest) + "\n", encoding="utf-8")

    result = _run(root)

    assert result.returncode == 0, result.stderr


def test_missing_or_escaping_image_reference_fails_closed(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")
    manuscript = root / "research-case/07-manuscript/manuscript.md"
    manuscript.write_text(
        manuscript.read_text() + "\n![Unsafe](../../../../outside.svg)\n",
        encoding="utf-8",
    )

    result = _run(root)

    assert result.returncode == 1
    assert "image reference escapes workspace root" in result.stderr


def test_claim_set_mismatch_fails_closed(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")
    graph = root / "research-case/07-manuscript/claim-graph.json"
    graph.write_text(json.dumps({"claims": {"C001": {}, "C002": {}}}) + "\n", encoding="utf-8")

    result = _run(root)

    assert result.returncode == 1
    assert "claim set mismatch" in result.stderr


def test_missing_required_artifact_family_member_fails_closed(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")
    manuscript = root / "research-case/07-manuscript/manuscript.md"
    manuscript.write_text(manuscript.read_text().replace("`T8`", "table eight"), encoding="utf-8")

    result = _run(root)

    assert result.returncode == 1
    assert "missing manuscript table identifiers: T8" in result.stderr


def test_unexpected_artifact_family_member_fails_closed(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")
    manuscript = root / "research-case/07-manuscript/manuscript.md"
    manuscript.write_text(manuscript.read_text() + "\nUnexpected figure `F9`.\n", encoding="utf-8")

    result = _run(root)

    assert result.returncode == 1
    assert "unexpected manuscript figure identifiers: F9" in result.stderr


def test_canonical_state_drift_fails_closed(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")
    state_path = root / "research-case/program-state.json"
    state = json.loads(state_path.read_text())
    state["current_phase"] = "MANUSCRIPT"
    state_path.write_text(json.dumps(state) + "\n", encoding="utf-8")

    result = _run(root)

    assert result.returncode == 1
    assert "canonical state mismatch: current_phase expected INTAKE, got MANUSCRIPT" in result.stderr


def test_source_hash_drift_fails_closed(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")
    bibliography = root / "paper/references.bib"
    bibliography.write_text(bibliography.read_text() + "\n% drift\n", encoding="utf-8")

    result = _run(root)

    assert result.returncode == 1
    assert "source manifest hash mismatch for SRC-BIB" in result.stderr


def test_missing_required_source_binding_fails_closed(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")
    source_manifest_path = root / "research-case/07-manuscript/source-manifest.json"
    source_manifest = json.loads(source_manifest_path.read_text())
    source_manifest["sources"] = [
        row
        for row in source_manifest["sources"]
        if row["source_id"] != "SRC-MANUSCRIPT-ALIGNMENT-CHECKER"
    ]
    source_manifest_path.write_text(json.dumps(source_manifest) + "\n", encoding="utf-8")

    result = _run(root)

    assert result.returncode == 1
    assert "missing required source manifest bindings: SRC-MANUSCRIPT-ALIGNMENT-CHECKER" in result.stderr


def test_claim_matrix_guard_drift_fails_closed(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")
    matrix = root / "research-case/07-manuscript/claim-evidence-matrix.csv"
    matrix.write_text(
        matrix.read_text().replace(
            "RID-C003-DEADLINE-001 absent; independent reproduction and external validation are missing; F6-F8 remain future outputs",
            "independent reproduction and external validation are missing",
        ),
        encoding="utf-8",
    )

    result = _run(root)

    assert result.returncode == 1
    assert "claim matrix blocked_by drift for C003" in result.stderr
