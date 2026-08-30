from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export_deadline_pilot_start_package.py"

PACKAGE_CONSTANTS = {
    "schema_id": "KEYSTONE_DEADLINE_PILOT_START_PACKAGE",
    "schema_version": 1,
    "status": "DRAFT_PREAUTHORIZATION",
    "execution_authorization": "NOT_AUTHORIZED",
    "canonical_phase": "INTAKE",
    "scientific_evidence_boundary": "DESIGN_ONLY_NOT_CONFIRMATORY_EVIDENCE",
    "result_id": "RID-C003-DEADLINE-001",
    "claim_ids": "C002|C003",
    "author_metadata_freeze": "DEFERRED_BY_ACCOUNTABLE_HUMAN",
}

ENVIRONMENT_IDS = (
    "ENV-DEADLINE-CONTROL-001",
    "ENV-DEADLINE-LATENCY-001",
    "ENV-DEADLINE-LOSS-001",
    "ENV-DEADLINE-CRASH-001",
)

ABLATION_IDS = (
    "ABL-CANARY-001",
    "ABL-STRAT-001",
    "ABL-DOMAIN-001",
    "ABL-TEMPORAL-001",
)

ABLATION_RESULT_IDS = {
    "ABL-CANARY-001": "RID-C003-DEADLINE-001",
    "ABL-STRAT-001": "RID-C003-STRAT-001",
    "ABL-DOMAIN-001": "RID-C003-CORR-001",
    "ABL-TEMPORAL-001": "RID-C003-IID-001",
}

ENVIRONMENT_HEADER = (
    "profile_id",
    "profile_role",
    "process_count",
    "failure_domain_count",
    "host_topology",
    "run_day_block",
    "network_latency_profile",
    "packet_loss_profile",
    "crash_profile",
    "synchrony_assumption",
    "deadline_interpretation",
    "trace_denominator",
    "precision_target",
    "multiplicity_rule",
    "execution_status",
    "result_id",
    "claim_ids",
    "source_path",
    "claim_ceiling",
)

ABLATION_HEADER = (
    "ablation_id",
    "treatment",
    "control",
    "mechanism_question",
    "paired_seed_policy",
    "blocking_factors",
    "required_endpoint",
    "execution_status",
    "result_id",
    "claim_ids",
    "source_path",
    "claim_ceiling",
)

FORBIDDEN_PACKAGE_TEXT = ("GO", "CONFIRMATORY_EVIDENCE", "FEASIBILITY_GATE", "STUDY_DESIGN")
UNRESOLVED_LITERAL = "UNRESOLVED_BEFORE_EXECUTION"
OUTPUT_FILES = (
    "deadline-environment-profiles.csv",
    "t5-ablation-run-matrix.csv",
    "deadline-pilot-execution-contract.md",
    "independent-reproduction-handoff.md",
    "deadline-pilot-start-package-manifest.json",
    "deadline-pilot-start-package-manifest.json.sha256",
)

CONTENT_OUTPUT_FILES = OUTPUT_FILES[:4]

AUTHORITY_REQUIRED_SNIPPETS = (
    "The authorship position above is recorded only as the supplied current default.",
    "The complete author list, final author order, corresponding-author designation, affiliation wording, institutional naming, and contact metadata remain deferred and subject to accountable-human and institutional verification before submission.",
    "does not independently verify novelty, feasibility, study design, scientific evidence, external validation, manuscript readiness, or venue compliance",
    "promotes no scientific or submission gate by itself.",
)

HANDOFF_REQUIRED_COMMANDS = (
    "`python3 scripts/export_deadline_pilot_start_package.py --check`",
    "`python3 -m pytest prototype/tests/test_deadline_pilot_start_package.py -q`",
    "`cd prototype && uv run --locked --extra dev pytest -q`",
    "`forge test --root contracts`",
    "`python3 scripts/export_t1_t8_tables.py --check`",
)


@pytest.fixture
def deadline_package_module():
    spec = importlib.util.spec_from_file_location("deadline_package", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _copy_inputs(deadline_package_module, destination_root: Path) -> None:
    for relative in deadline_package_module.INPUT_PATHS:
        destination = destination_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)


def test_package_constants_ids_headers_and_mappings(deadline_package_module) -> None:
    assert deadline_package_module.PACKAGE_CONSTANTS == PACKAGE_CONSTANTS
    assert deadline_package_module.ENVIRONMENT_HEADER == ENVIRONMENT_HEADER
    assert deadline_package_module.ABLATION_HEADER == ABLATION_HEADER
    assert deadline_package_module.OUTPUT_FILES == OUTPUT_FILES

    package = deadline_package_module.build_package(ROOT)

    assert tuple(row["profile_id"] for row in package.environment_rows) == ENVIRONMENT_IDS
    assert tuple(row["ablation_id"] for row in package.ablation_rows) == ABLATION_IDS
    assert all(row["result_id"] == PACKAGE_CONSTANTS["result_id"] for row in package.environment_rows)
    assert {
        row["ablation_id"]: row["result_id"] for row in package.ablation_rows
    } == ABLATION_RESULT_IDS
    assert all(row["claim_ids"] == PACKAGE_CONSTANTS["claim_ids"] for row in package.environment_rows)
    assert package.manifest_payload["package_constants"] == PACKAGE_CONSTANTS


def test_environment_rows_reject_resolved_numeric_execution_choices(deadline_package_module) -> None:
    package = deadline_package_module.build_package(ROOT)

    forbidden_fields = (
        "network_latency_profile",
        "packet_loss_profile",
        "crash_profile",
        "deadline_interpretation",
        "trace_denominator",
        "precision_target",
        "multiplicity_rule",
    )
    for row in package.environment_rows:
        assert row["process_count"] == "32"
        assert row["failure_domain_count"] == "4"
        for field in forbidden_fields:
            assert row[field] == UNRESOLVED_LITERAL

    with pytest.raises(deadline_package_module.PackageValidationError, match="resolved numeric"):
        deadline_package_module.validate_environment_rows(
            [
                {
                    **package.environment_rows[0],
                    "network_latency_profile": "75",
                },
                *package.environment_rows[1:],
            ]
        )


def test_statuses_and_rendered_text_stay_design_only(deadline_package_module, tmp_path: Path) -> None:
    package = deadline_package_module.build_package(ROOT)

    assert all(
        row["execution_status"] == "BLOCKED_UNRESOLVED_DESIGN"
        for row in package.environment_rows
    )
    assert all(
        row["execution_status"] == "DESIGN_ONLY_NOT_EXECUTED"
        for row in package.ablation_rows
    )
    rendered_text = "\n".join(package.markdown_documents.values())
    for token in FORBIDDEN_PACKAGE_TEXT:
        assert token not in rendered_text

    outputs = deadline_package_module.write_package(ROOT, tmp_path)
    for relative_name in OUTPUT_FILES:
        assert relative_name in outputs
    rows = _csv_rows(tmp_path / "deadline-environment-profiles.csv")
    assert [row["profile_id"] for row in rows] == list(ENVIRONMENT_IDS)


def test_manifest_inventory_and_sidecar_are_complete_and_deterministic(
    deadline_package_module, tmp_path: Path
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_outputs = deadline_package_module.write_package(ROOT, first)
    second_outputs = deadline_package_module.write_package(ROOT, second)
    assert first_outputs == second_outputs

    manifest = json.loads((first / OUTPUT_FILES[-2]).read_text(encoding="utf-8"))
    assert tuple(item["path"] for item in manifest["inputs"]) == tuple(
        sorted(deadline_package_module.INPUT_PATHS)
    )
    assert tuple(item["path"] for item in manifest["outputs"]) == tuple(
        f"{deadline_package_module.CANONICAL_OUTPUT_DIR}/{name}" for name in CONTENT_OUTPUT_FILES
    )
    assert tuple(manifest["integrity_artifacts"]) == (
        f"{deadline_package_module.CANONICAL_OUTPUT_DIR}/{OUTPUT_FILES[-2]}",
        f"{deadline_package_module.CANONICAL_OUTPUT_DIR}/{OUTPUT_FILES[-1]}",
    )
    assert all(
        item["path"].endswith(name) and item["sha256"] == hashlib.sha256((first / name).read_bytes()).hexdigest()
        for item, name in zip(manifest["outputs"], CONTENT_OUTPUT_FILES, strict=True)
    )
    assert all(not item["path"].endswith(OUTPUT_FILES[-2]) for item in manifest["outputs"])
    assert all(not item["path"].endswith(OUTPUT_FILES[-1]) for item in manifest["outputs"])

    expected_hash = hashlib.sha256((first / OUTPUT_FILES[-2]).read_bytes()).hexdigest()
    assert (first / OUTPUT_FILES[-1]).read_text(encoding="utf-8").strip() == (
        f"{expected_hash}  {OUTPUT_FILES[-2]}"
    )


def test_check_fails_on_tampered_output_even_if_manifest_and_sidecar_are_rebound(
    deadline_package_module, tmp_path: Path
) -> None:
    deadline_package_module.write_package(ROOT, tmp_path)
    target = tmp_path / "deadline-environment-profiles.csv"
    rows = _csv_rows(target)
    rows[0]["profile_role"] = "tampered role"
    _write_csv(target, deadline_package_module.ENVIRONMENT_HEADER, rows)

    manifest_path = tmp_path / OUTPUT_FILES[-2]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for item in manifest["outputs"]:
        if item["path"].endswith(target.name):
            item["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rebound = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    (tmp_path / OUTPUT_FILES[-1]).write_text(
        f"{rebound}  {OUTPUT_FILES[-2]}\n",
        encoding="utf-8",
    )

    errors = deadline_package_module.check_package(ROOT, tmp_path)
    assert any(
        "canonical reconstruction drift: deadline-environment-profiles.csv" == error
        for error in errors
    )


def test_check_reports_explicit_manifest_inventory_drift(deadline_package_module, tmp_path: Path) -> None:
    deadline_package_module.write_package(ROOT, tmp_path)
    manifest_path = tmp_path / OUTPUT_FILES[-2]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["inputs"] = manifest["inputs"][:-1]
    manifest["outputs"] = manifest["outputs"][:-1]
    manifest["integrity_artifacts"] = manifest["integrity_artifacts"][:-1]
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rebound = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    (tmp_path / OUTPUT_FILES[-1]).write_text(
        f"{rebound}  {OUTPUT_FILES[-2]}\n",
        encoding="utf-8",
    )

    errors = deadline_package_module.check_package(ROOT, tmp_path)
    assert "manifest input inventory drift" in errors
    assert "manifest output inventory drift" in errors
    assert "manifest integrity artifact inventory drift" in errors


def test_check_rejects_promoted_program_state_boundary(deadline_package_module, tmp_path: Path) -> None:
    copied_root = tmp_path / "project"
    copied_output = tmp_path / "output"
    _copy_inputs(deadline_package_module, copied_root)
    deadline_package_module.write_package(copied_root, copied_output)

    path = copied_root / "research-case/program-state.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["current_phase"] = "STUDY_DESIGN"
    data["novelty_status"] = "RESOLVED"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(deadline_package_module.PackageValidationError, match="boundary drift"):
        deadline_package_module.check_package(copied_root, copied_output)


def test_environment_schema_rejects_numeric_resolution(deadline_package_module, tmp_path: Path) -> None:
    deadline_package_module.write_package(ROOT, tmp_path)
    path = tmp_path / "deadline-environment-profiles.csv"
    rows = _csv_rows(path)
    rows[0]["precision_target"] = "0.05"
    _write_csv(path, deadline_package_module.ENVIRONMENT_HEADER, rows)

    with pytest.raises(deadline_package_module.PackageValidationError, match="resolved numeric"):
        deadline_package_module.validate_environment_rows(tuple(rows))


def test_authority_boundary_requires_explicit_metadata_and_submission_deferrals(
    deadline_package_module, tmp_path: Path
) -> None:
    authority_text = (ROOT / "research-case/00-governance/accountable-authority-confirmation.md").read_text(
        encoding="utf-8"
    )
    for snippet in AUTHORITY_REQUIRED_SNIPPETS:
        assert snippet in authority_text

    copied_root = tmp_path / "project"
    _copy_inputs(deadline_package_module, copied_root)
    path = copied_root / "research-case/00-governance/accountable-authority-confirmation.md"
    path.write_text(
        authority_text.replace(
            "The complete author list, final author order, corresponding-author designation, affiliation wording, institutional naming, and contact metadata remain deferred and subject to accountable-human and institutional verification before submission.",
            "The complete author list, final author order, corresponding-author designation, affiliation wording, institutional naming, and contact metadata are fixed for submission.",
        ),
        encoding="utf-8",
    )

    with pytest.raises(deadline_package_module.PackageValidationError, match="missing required boundary text"):
        deadline_package_module.build_package(copied_root)


def test_reproduction_handoff_uses_workspace_realistic_commands(deadline_package_module) -> None:
    package = deadline_package_module.build_package(ROOT)
    handoff = package.markdown_documents["independent-reproduction-handoff.md"]
    for command in HANDOFF_REQUIRED_COMMANDS:
        assert command in handoff
    assert "verify the canonical source-manifest entry and verification state in the canonical integration workflow" in handoff
    assert "verify the canonical checksum records in the canonical integration workflow" in handoff
    assert "`python scripts/export_deadline_pilot_start_package.py --check`" not in handoff
    assert "`forge test`" not in handoff
    assert "`python3 -m pytest prototype/tests -q`" not in handoff


def test_cli_supports_default_write_and_explicit_write(deadline_package_module, tmp_path: Path) -> None:
    default_output = tmp_path / "default"
    explicit_output = tmp_path / "explicit"
    assert deadline_package_module.main(
        ["--project-root", str(ROOT), "--output-dir", str(default_output)]
    ) == 0
    assert deadline_package_module.main(
        ["--project-root", str(ROOT), "--output-dir", str(explicit_output), "--write"]
    ) == 0
    for name in OUTPUT_FILES:
        assert (default_output / name).read_bytes() == (explicit_output / name).read_bytes()


def test_cli_returns_concise_error_for_boundary_drift(
    deadline_package_module, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    copied_root = tmp_path / "project"
    copied_output = tmp_path / "output"
    _copy_inputs(deadline_package_module, copied_root)
    path = copied_root / "research-case/program-state.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["current_phase"] = "STUDY_DESIGN"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    assert deadline_package_module.main(
        ["--project-root", str(copied_root), "--output-dir", str(copied_output), "--write"]
    ) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Traceback" not in captured.err
    assert captured.err.count("\n") == 1
    assert captured.err.startswith("error: research-case/program-state.json: boundary drift for current_phase; expected 'INTAKE'")


def test_cli_returns_concise_error_for_invalid_source_json(
    deadline_package_module, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    copied_root = tmp_path / "project"
    copied_output = tmp_path / "output"
    _copy_inputs(deadline_package_module, copied_root)
    path = copied_root / "research-case/program-state.json"
    path.write_text("{\n", encoding="utf-8")

    assert deadline_package_module.main(
        ["--project-root", str(copied_root), "--output-dir", str(copied_output), "--check"]
    ) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Traceback" not in captured.err
    assert captured.err.count("\n") == 1
    assert captured.err.startswith("error: research-case/program-state.json: invalid JSON source:")
