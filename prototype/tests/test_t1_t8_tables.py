from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export_t1_t8_tables.py"
SPEC = importlib.util.spec_from_file_location("export_t1_t8_tables", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
tables = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = tables
SPEC.loader.exec_module(tables)


EXPECTED_IDS = tuple(f"T{i}" for i in range(1, 9))
REQUIRED_FIELDS = {"claim_ids", "source_path", "evidence_stage", "claim_ceiling"}
ALLOWED_STAGES = {
    "DESIGN_ONLY",
    "PRELIMINARY_INTERNAL",
    "PREAUTHORIZATION_INTERNAL",
    "EXPLORATORY_INTERNAL",
    "ANALYTIC_DRAFT",
    "MISSING_NOT_EXECUTED",
    "BLOCKED_EXTERNAL",
}
EXPECTED_HEADERS = {
    "T1": ("claim_id", "predecessor_id", "bounded_difference", "defeating_evidence", "residual_uncertainty", "claim_ids", "source_path", "evidence_stage", "claim_ceiling"),
    "T2": ("comparator_id", "comparator_class", "compared_property", "design_difference", "measured_superiority", "claim_ids", "source_path", "evidence_stage", "claim_ceiling"),
    "T3": ("condition_id", "n", "threshold", "sample_size", "required_responses", "offline_probability", "domain_outage_probability", "domains", "trials", "seed", "sampling_strategy", "selective_withholders", "environment_profile", "claim_ids", "source_path", "evidence_stage", "claim_ceiling"),
    "T4": ("result_id", "condition_id", "estimand", "estimate", "ci_low", "ci_high", "denominator", "trials", "claim_ids", "source_path", "evidence_stage", "claim_ceiling"),
    "T5": ("ablation_id", "planned_change", "mechanism_question", "execution_status", "estimate", "claim_ids", "source_path", "evidence_stage", "claim_ceiling"),
    "T6": ("check_id", "estimand", "condition", "estimate", "comparison", "uncertainty_or_error", "interpretation_boundary", "claim_ids", "source_path", "evidence_stage", "claim_ceiling"),
    "T7": ("evidence_id", "surface", "metric", "value", "unit", "scope_or_blocker", "claim_ids", "source_path", "evidence_stage", "claim_ceiling"),
    "T8": ("finding_id", "finding", "status", "consequence", "required_resolution", "claim_ids", "source_path", "evidence_stage", "claim_ceiling"),
}


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _copy_inputs(destination_root: Path) -> None:
    for relative in tables.INPUT_PATHS:
        destination = destination_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)


def test_build_package_has_exact_ids_and_traceability_fields() -> None:
    package = tables.build_package(ROOT)
    assert tuple(package) == EXPECTED_IDS
    for table_id, table in package.items():
        assert table.table_id == table_id
        assert table.headers == EXPECTED_HEADERS[table_id]
        assert REQUIRED_FIELDS <= set(table.headers)
        assert table.rows
        for row in table.rows:
            assert set(row) == set(table.headers)
            assert all(row[field].strip() for field in REQUIRED_FIELDS)


def test_evidence_stages_are_fail_closed_and_never_confirmatory() -> None:
    package = tables.build_package(ROOT)
    stages = {
        row["evidence_stage"]
        for table in package.values()
        for row in table.rows
    }
    assert stages <= ALLOWED_STAGES
    assert "CONFIRMATORY" not in " ".join(stages).upper()


def test_required_missing_and_blocked_rows_are_explicit() -> None:
    package = tables.build_package(ROOT)
    assert any(
        row["evidence_stage"] == "MISSING_NOT_EXECUTED"
        for row in package["T5"].rows
    )
    assert any(
        row["evidence_stage"] == "BLOCKED_EXTERNAL"
        for row in package["T7"].rows
    )
    t8_text = " ".join(value for row in package["T8"].rows for value in row.values())
    assert "selective withholding" in t8_text.lower()
    assert "truthful domain" in t8_text.lower()
    assert "external validation" in t8_text.lower()


def test_numeric_values_are_bound_directly_to_canonical_csv_and_json() -> None:
    package = tables.build_package(ROOT)
    baseline = json.loads((ROOT / "prototype/results/baseline.json").read_text())
    source_baseline = next(row for row in baseline if row["name"] == "domain-20pct-uniform")
    t4_row = next(
        row for row in package["T4"].rows if row.get("result_id") == "RID-C003-CORR-001"
    )
    assert t4_row["estimate"] == str(source_baseline["catastrophic_false_pass_rate"])
    assert t4_row["ci_low"] == str(source_baseline["catastrophic_false_pass_ci_low"])
    assert t4_row["ci_high"] == str(source_baseline["catastrophic_false_pass_ci_high"])

    exact_source = _csv_rows(ROOT / "prototype/results/exact_stratified_validation.csv")[0]
    t6_row = next(row for row in package["T6"].rows if row.get("check_id") == "EXACT_STRATIFIED")
    assert t6_row["estimate"] == exact_source["exact_tail_probability"]
    assert t6_row["comparison"] == exact_source["monte_carlo_tail_probability"]


def test_write_is_deterministic_and_manifest_sidecar_hashes_match(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_paths = tables.write_package(ROOT, first)
    second_paths = tables.write_package(ROOT, second)
    assert set(first_paths) == set(second_paths)
    for name in first_paths:
        assert (first / name).read_bytes() == (second / name).read_bytes()

    manifest_path = first / "t1_t8_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema_id"] == "KEYSTONE_T1_T8_TABLE_PACKAGE"
    assert manifest["schema_version"] == 1
    assert manifest["status"] == "DRAFT_PREAUTHORIZATION"
    assert manifest["scientific_evidence_boundary"] == "NOT_CONFIRMATORY_OR_INDEPENDENT_EVIDENCE"
    assert "RID-C003-DEADLINE-001" in manifest["missing_required_evidence"]
    assert "independent reproduction" in manifest["missing_required_evidence"]
    assert "external validation" in manifest["missing_required_evidence"]
    assert manifest["inputs"]
    assert manifest["outputs"]
    assert tuple(manifest["table_dispositions"]) == EXPECTED_IDS

    expected_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    assert (first / "t1_t8_manifest.json.sha256").read_text().strip() == (
        f"{expected_hash}  t1_t8_manifest.json"
    )


def test_markdown_and_latex_are_editable_and_each_table_is_marked_draft(
    tmp_path: Path,
) -> None:
    tables.write_package(ROOT, tmp_path)
    markdown = (tmp_path / "t1_t8_package.md").read_text(encoding="utf-8")
    latex = (tmp_path / "t1_t8_package.tex").read_text(encoding="utf-8")
    for table_id in EXPECTED_IDS:
        assert f"## {table_id}" in markdown
        assert f"{table_id} -- DRAFT / PRE-AUTHORIZATION" in latex
    assert "\\begin{longtable}" in latex
    assert "DRAFT / PRE-AUTHORIZATION" in markdown


def test_latex_escaping_covers_reserved_characters() -> None:
    assert tables.latex_escape("a&b_c%#d$e{f}~g^h\\i") == (
        r"a\&b\_c\%\#d\$e\{f\}\textasciitilde{}g\textasciicircum{}h"
        r"\textbackslash{}i"
    )


def test_cli_check_fails_closed_on_output_drift(tmp_path: Path) -> None:
    tables.write_package(ROOT, tmp_path)
    assert tables.check_package(ROOT, tmp_path) == []
    target = tmp_path / "t4_primary_results.csv"
    target.write_text(target.read_text(encoding="utf-8") + "drift\n", encoding="utf-8")
    errors = tables.check_package(ROOT, tmp_path)
    assert errors
    assert any("t4_primary_results.csv" in error for error in errors)
    assert tables.main([
        "--project-root", str(ROOT),
        "--output-dir", str(tmp_path),
        "--check",
    ]) == 1


def test_check_fails_closed_on_input_drift(tmp_path: Path) -> None:
    copied_root = tmp_path / "project"
    copied_output = tmp_path / "output"
    _copy_inputs(copied_root)
    tables.write_package(copied_root, copied_output)
    source = copied_root / "prototype/results/exact_stratified_validation.csv"
    source.write_text(source.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    errors = tables.check_package(copied_root, copied_output)
    assert errors
    assert any("input drift" in error.lower() for error in errors)


def test_check_rejects_hash_rebound_incomplete_manifest_inventory(tmp_path: Path) -> None:
    tables.write_package(ROOT, tmp_path)
    manifest_path = tmp_path / "t1_t8_manifest.json"
    sidecar_path = tmp_path / "t1_t8_manifest.json.sha256"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["inputs"] = manifest["inputs"][:-1]
    manifest["outputs"] = manifest["outputs"][:-1]
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rebound = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    sidecar_path.write_text(
        f"{rebound}  t1_t8_manifest.json\n",
        encoding="utf-8",
    )

    errors = tables.check_package(ROOT, tmp_path)
    assert "manifest input inventory drift" in errors
    assert "manifest output inventory drift" in errors


def test_build_rejects_experiment_manifest_boundary_drift(tmp_path: Path) -> None:
    copied_root = tmp_path / "project"
    _copy_inputs(copied_root)
    path = copied_root / "prototype/results/experiment_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["scientific_evidence_status"] = "SCIENTIFIC_EVIDENCE"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(tables.PackageValidationError, match="scientific_evidence_status"):
        tables.build_package(copied_root)


def test_build_rejects_preauthorization_qa_semantic_drift(tmp_path: Path) -> None:
    copied_root = tmp_path / "project"
    _copy_inputs(copied_root)
    path = copied_root / "paper/tables/preauthorization_engineering_qa.csv"
    rows = _csv_rows(path)
    rows[0]["authorization_boundary"] = "AUTHORIZED"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    with pytest.raises(tables.PackageValidationError, match="authorization_boundary"):
        tables.build_package(copied_root)


def test_table_header_drift_is_rejected() -> None:
    with pytest.raises(tables.PackageValidationError, match="header drift"):
        tables._table("T1", "drift", reversed(EXPECTED_HEADERS["T1"]), (), ())


def test_check_rejects_tampered_output_with_rebound_manifest_and_sidecar(
    tmp_path: Path,
) -> None:
    tables.write_package(ROOT, tmp_path)
    target = tmp_path / "t4_primary_results.csv"
    target.write_text(target.read_text(encoding="utf-8") + "rebound-drift\n", encoding="utf-8")
    manifest_path = tmp_path / "t1_t8_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output = next(item for item in manifest["outputs"] if item["path"] == target.name)
    output["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rebound = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    (tmp_path / "t1_t8_manifest.json.sha256").write_text(
        f"{rebound}  t1_t8_manifest.json\n",
        encoding="utf-8",
    )

    errors = tables.check_package(ROOT, tmp_path)
    assert any("canonical reconstruction drift: t4_primary_results.csv" in error for error in errors)


def test_malformed_baseline_object_fails_closed_under_optimized_python(
    tmp_path: Path,
) -> None:
    copied_root = tmp_path / "project"
    _copy_inputs(copied_root)
    (copied_root / "prototype/results/baseline.json").write_text("{}\n", encoding="utf-8")
    command = (
        "import importlib.util,sys; from pathlib import Path; "
        f"s=importlib.util.spec_from_file_location('optimized_tables',{str(SCRIPT)!r}); "
        "m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); "
        f"m.build_package(Path({str(copied_root)!r}))"
    )
    result = subprocess.run(
        [sys.executable, "-O", "-c", command],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert "prototype/results/baseline.json: expected non-empty JSON list" in result.stderr
    assert "AssertionError" not in result.stderr


def test_missing_required_baseline_row_is_named(tmp_path: Path) -> None:
    copied_root = tmp_path / "project"
    _copy_inputs(copied_root)
    path = copied_root / "prototype/results/baseline.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    rows = [row for row in rows if row["name"] != "domain-20pct-uniform"]
    path.write_text(json.dumps(rows), encoding="utf-8")

    with pytest.raises(
        tables.PackageValidationError,
        match="prototype/results/baseline.json: missing required IDs: domain-20pct-uniform",
    ):
        tables.build_package(copied_root)


def test_exact_stratified_header_drift_is_named(tmp_path: Path) -> None:
    copied_root = tmp_path / "project"
    _copy_inputs(copied_root)
    path = copied_root / "prototype/results/exact_stratified_validation.csv"
    rows = _csv_rows(path)
    fieldnames = tuple(rows[0])[1:]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    with pytest.raises(
        tables.PackageValidationError,
        match="prototype/results/exact_stratified_validation.csv: header drift",
    ):
        tables.build_package(copied_root)


def test_latex_layout_is_width_bounded_and_compiles_when_available(tmp_path: Path) -> None:
    tables.write_package(ROOT, tmp_path)
    fragment = (tmp_path / "t1_t8_package.tex").read_text(encoding="utf-8")
    assert fragment.count(r"\begin{longtable}{|p{0.24\linewidth}|p{0.68\linewidth}|}") == 8
    assert "p{0.17\\linewidth}" not in fragment
    width_pairs = re.findall(
        r"\\begin\{longtable\}\{\|p\{(0\.\d+)\\linewidth\}\|p\{(0\.\d+)\\linewidth\}\|\}",
        fragment,
    )
    assert len(width_pairs) == 8
    assert all(float(left) + float(right) <= 0.92 for left, right in width_pairs)

    pdflatex = shutil.which("pdflatex")
    if pdflatex is None:
        return
    wrapper = tmp_path / "compile_tables.tex"
    wrapper.write_text(
        "\\documentclass{article}\n"
        "\\usepackage[margin=20mm]{geometry}\n"
        "\\usepackage{longtable}\n"
        "\\begin{document}\n"
        "\\input{t1_t8_package.tex}\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [pdflatex, "-interaction=nonstopmode", "-halt-on-error", wrapper.name],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    log = (tmp_path / "compile_tables.log").read_text(encoding="utf-8", errors="replace")
    assert "Overfull \\hbox" not in log
