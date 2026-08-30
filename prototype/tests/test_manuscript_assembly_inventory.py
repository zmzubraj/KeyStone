from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export_manuscript_assembly_inventory.py"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    _write(
        root / "paper/references.bib",
        "@article{known2026,\n  title={Known work},\n  author={A. Author}\n}\n",
    )
    _write(root / "scripts/check_manuscript_alignment.py", "# checker stub\n")
    _write(root / "prototype/tests/test_manuscript_alignment.py", "# checker tests\n")
    _write(root / "research-case/05-analysis/results/negative-findings.csv", "result_id,status\nRID-NEG-001,MISSING\n")
    _write(root / "research-case/05-analysis/results/robustness-and-boundaries.csv", "result_id,status\nRID-ROB-001,MISSING\n")
    _write(root / "scripts/export_negative_findings.py", "# negative findings exporter stub\n")
    _write(root / "scripts/export_robustness_boundaries.py", "# robustness boundaries exporter stub\n")
    _write(root / "prototype/tests/test_negative_findings.py", "# negative findings tests\n")
    _write(root / "prototype/tests/test_robustness_boundaries.py", "# robustness boundaries tests\n")
    _write(root / "scripts/export_manuscript_assembly_inventory.py", "# exporter stub\n")
    _write(
        root / "prototype/tests/test_manuscript_assembly_inventory.py",
        "# exporter tests\n",
    )
    _write(root / "prototype/scripts/run_experiments.py", "# experiment runner stub\n")
    _write(root / "scripts/annotate_svg_accessibility.py", "# accessibility stub\n")

    for name in (
        "01_system_architecture",
        "02_property_separation",
        "03_audit_sequence",
        "04_dispute_sequence",
        "05_state_machines",
        "06_threat_model",
        "07_sampling_domains",
        "08_experiment_pipeline",
    ):
        _write(root / f"diagrams/{name}.svg", "<svg/>\n")
        _write(root / f"diagrams/{name}.mmd", "graph TD;\n")
        _write(root / f"diagrams/{name}.dot", "digraph G {}\n")
        _write(root / f"diagrams/{name}.png", "png\n")

    for name in (
        "figure_1_theoretical_detection_bound",
        "figure_2_iid_failure_sweep",
        "figure_3_domain_diversity",
        "figure_4_selective_withholding_gap",
        "figure_5_sampling_strategy",
    ):
        _write(root / f"prototype/results/figures/{name}.svg", "<svg/>\n")
        _write(root / f"prototype/results/figures/{name}.png", "png\n")
    for name in (
        "theoretical_bound.csv",
        "iid_failure_sweep.csv",
        "domain_diversity.csv",
        "selective_withholding.csv",
        "sampling_strategy.csv",
    ):
        _write(root / f"prototype/results/{name}", "x,y\n1,2\n")

    manuscript = """# Draft

Status: `DRAFT / PRE-MANUSCRIPT / PRE-AUTHORIZATION`

Novelty remains `UNRESOLVED`; feasibility remains `UNASSESSED`; execution is not authorized.
Final author order, corresponding-author designation, and exact affiliation wording are deferred.

Claims: `C001`, `C002`, and `C003` [@known2026].

![D1. Architecture](../../diagrams/01_system_architecture.svg)
![D2. Property separation](../../diagrams/02_property_separation.svg)
![D3. Audit sequence](../../diagrams/03_audit_sequence.svg)
![D4. Dispute sequence](../../diagrams/04_dispute_sequence.svg)
![D5. State machines](../../diagrams/05_state_machines.svg)
![D6. Threat model](../../diagrams/06_threat_model.svg)
![D7. Sampling domains](../../diagrams/07_sampling_domains.svg)
![D8. Experiment pipeline](../../diagrams/08_experiment_pipeline.svg)

![F1. Static detection bound](../../prototype/results/figures/figure_1_theoretical_detection_bound.svg)
![F2. IID sweep](../../prototype/results/figures/figure_2_iid_failure_sweep.svg)
![F3. Domain diversity](../../prototype/results/figures/figure_3_domain_diversity.svg)
![F4. Selective withholding](../../prototype/results/figures/figure_4_selective_withholding_gap.svg)
![F5. Sampling strategy](../../prototype/results/figures/figure_5_sampling_strategy.svg)

Tables: `T1`, `T2`, `T3`, `T4`, `T5`, `T6`, `T7`, `T8`.
Future figures remain `F6`, `F7`, and `F8`.
"""
    _write(root / "research-case/07-manuscript/manuscript.md", manuscript)

    with (root / "research-case/07-manuscript/claim-evidence-matrix.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        fieldnames = [
            "claim_id",
            "claim_text",
            "table_targets",
            "figure_targets",
            "diagram_targets",
            "current_status",
            "blocked_by",
            "allowed_wording",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "claim_id": "C001",
                "claim_text": "Analytic distinction",
                "table_targets": "T1|T4",
                "figure_targets": "F1",
                "diagram_targets": "D2",
                "current_status": "BLOCKED",
                "blocked_by": "NOVELTY_UNRESOLVED",
                "allowed_wording": "This paper studies|under the stated static catastrophic model",
            }
        )
        writer.writerow(
            {
                "claim_id": "C002",
                "claim_text": "Internal prototype boundary",
                "table_targets": "T3|T7",
                "figure_targets": "",
                "diagram_targets": "D1|D3|D4|D5|D8",
                "current_status": "AT_RISK",
                "blocked_by": "independent reproduction and external review are missing",
                "allowed_wording": "internal prototype evidence shows|local reproducibility evidence records",
            }
        )
        writer.writerow(
            {
                "claim_id": "C003",
                "claim_text": "Combined evidence package",
                "table_targets": "T2|T3|T4|T5|T6|T7|T8",
                "figure_targets": "F1|F2|F3|F4|F5|F6|F7|F8",
                "diagram_targets": "D1|D2|D3|D4|D5|D6|D7|D8",
                "current_status": "AT_RISK",
                "blocked_by": "RID-C003-DEADLINE-001 absent; independent reproduction and external validation are missing; F6-F8 remain future outputs",
                "allowed_wording": "bounded internal evidence indicates|within the declared model|conditional on synchrony assumptions|selective withholding remains a limitation",
            }
        )

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

    figure_manifest_path = root / "research-case/06-visuals/figures/figure-manifest.csv"
    figure_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with figure_manifest_path.open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "figure_id",
                "panels",
                "source_data",
                "source_data_sha256",
                "source_code",
                "source_code_sha256",
                "accessibility_postprocessor_path",
                "accessibility_postprocessor_sha256",
                "canonical_output_path",
                "canonical_output_sha256",
                "derivative_png_path",
                "derivative_png_sha256",
                "canonical_format",
                "final_size_check",
                "accessibility_check",
                "status",
            ],
        )
        writer.writeheader()
        for figure_id, stem, status in (
            ("F1", "figure_1_theoretical_detection_bound", "PRELIMINARY_PREAUTHORIZATION"),
            ("F2", "figure_2_iid_failure_sweep", "PRELIMINARY_PREAUTHORIZATION"),
            ("F3", "figure_3_domain_diversity", "PRELIMINARY_PREAUTHORIZATION"),
            ("F4", "figure_4_selective_withholding_gap", "PRELIMINARY_LIMITATION"),
            ("F5", "figure_5_sampling_strategy", "PRELIMINARY_PREAUTHORIZATION"),
        ):
            svg = root / f"prototype/results/figures/{stem}.svg"
            png = root / f"prototype/results/figures/{stem}.png"
            data = root / "prototype/results/theoretical_bound.csv"
            writer.writerow(
                {
                    "figure_id": figure_id,
                    "panels": "A",
                    "source_data": "prototype/results/theoretical_bound.csv",
                    "source_data_sha256": _sha256(data),
                    "source_code": "prototype/scripts/run_experiments.py",
                    "source_code_sha256": "a" * 64,
                    "accessibility_postprocessor_path": "scripts/annotate_svg_accessibility.py",
                    "accessibility_postprocessor_sha256": "b" * 64,
                    "canonical_output_path": f"prototype/results/figures/{stem}.svg",
                    "canonical_output_sha256": _sha256(svg),
                    "derivative_png_path": f"prototype/results/figures/{stem}.png",
                    "derivative_png_sha256": _sha256(png),
                    "canonical_format": "SVG",
                    "final_size_check": "PROVISIONAL",
                    "accessibility_check": "SEMANTIC_SVG_PASS",
                    "status": status,
                }
            )

    manifest = {
        "canonical_dispositions": {
            "acceptance_readiness": "NOT_ASSESSABLE",
            "feasibility": "UNASSESSED",
            "novelty": "UNRESOLVED",
            "phase": "INTAKE",
            "solution_viability": "ASSERTED_ONLY",
        },
        "missing_required_evidence": [
            "RID-C003-DEADLINE-001",
            "independent reproduction",
            "external validation",
        ],
        "outputs": [
            {"path": f"t{index}_placeholder.csv", "sha256": "c" * 64}
            for index in range(1, 9)
        ],
        "schema_id": "KEYSTONE_T1_T8_TABLE_PACKAGE",
        "schema_version": 1,
        "status": "DRAFT_PREAUTHORIZATION",
        "table_dispositions": {
            "T1": "bounded strongest-prior-art matrix only; not novelty clearance",
            "T2": "design comparator registry only; no measured superiority claim",
            "T3": "frozen local conditions and missing deadline profile",
            "T4": "preliminary internal result display only",
            "T5": "planned mechanism-isolation registry only",
            "T6": "exact, exploratory, and preliminary robustness checks",
            "T7": "local timing and gas observations only",
            "T8": "negative findings and unresolved risks ledger",
        },
        "table_ids": [f"T{index}" for index in range(1, 9)],
    }
    _write(
        root / "paper/tables/t1_t8_manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )
    return root


def _run(root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *extra],
        text=True,
        capture_output=True,
        check=False,
    )


def test_export_writes_deterministic_manuscript_assembly_inventory(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")

    result = _run(root)

    assert result.returncode == 0, result.stderr
    report = (root / "research-case/07-manuscript/assembly-inventory.md").read_text(
        encoding="utf-8"
    )
    assert "Current serial gate: `INTAKE`" in report
    assert "Quantitative figures with rendered assets: **5**" in report
    assert "Referenced figure identifiers without rendered manuscript assets: `F6`, `F7`, `F8`." in report
    assert "## Future-figure boundary" in report
    assert "may reference `F6`, `F7`, and `F8` only as future confirmatory outputs" in report
    assert "| `C001` | `BLOCKED` | `T1`, `T4` | `F1` | `D2` | `NOVELTY_UNRESOLVED` | `This paper studies|under the stated static catastrophic model` |" in report
    assert "| `F4` | `PRELIMINARY_LIMITATION` | `../../prototype/results/figures/figure_4_selective_withholding_gap.svg` |" in report
    assert "| `T8` | negative findings and unresolved risks ledger | `t8_placeholder.csv` |" in report
    assert "RID-C003-DEADLINE-001" in report


def test_check_passes_for_current_inventory(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")
    assert _run(root).returncode == 0

    result = _run(root, "--check")

    assert result.returncode == 0, result.stderr
    assert "manuscript assembly inventory is current" in result.stdout


def test_check_detects_stale_inventory_after_claim_change(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")
    assert _run(root).returncode == 0
    matrix_path = root / "research-case/07-manuscript/claim-evidence-matrix.csv"
    matrix_path.write_text(
        matrix_path.read_text(encoding="utf-8").replace(
            "RID-C003-DEADLINE-001 absent", "deadline evidence still absent"
        ),
        encoding="utf-8",
    )

    result = _run(root, "--check")

    assert result.returncode == 1
    assert "claim matrix blocked_by drift for C003" in result.stderr


def test_state_drift_fails_closed(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")
    state_path = root / "research-case/program-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["current_phase"] = "MANUSCRIPT"
    state_path.write_text(json.dumps(state) + "\n", encoding="utf-8")

    result = _run(root)

    assert result.returncode == 1
    assert "canonical state mismatch: current_phase expected INTAKE, got MANUSCRIPT" in result.stderr


def test_future_figure_manifest_drift_fails_closed(tmp_path: Path) -> None:
    root = _build_case(tmp_path / "case")
    manifest_path = root / "research-case/06-visuals/figures/figure-manifest.csv"
    manifest_path.write_text(
        manifest_path.read_text(encoding="utf-8")
        + "F6,A,prototype/results/theoretical_bound.csv,"
        + ("d" * 64)
        + ",prototype/scripts/run_experiments.py,"
        + ("e" * 64)
        + ",scripts/annotate_svg_accessibility.py,"
        + ("f" * 64)
        + ",prototype/results/figures/future_f6.svg,"
        + ("1" * 64)
        + ",prototype/results/figures/future_f6.png,"
        + ("2" * 64)
        + ",SVG,PROVISIONAL,SEMANTIC_SVG_PASS,PRELIMINARY_PREAUTHORIZATION\n",
        encoding="utf-8",
    )

    result = _run(root)

    assert result.returncode == 1
    assert "future figure ids may not enter the rendered manifest during INTAKE: F6" in result.stderr
