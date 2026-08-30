from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/run_isolated_mechanical_reproduction.py"


@pytest.fixture
def harness():
    spec = importlib.util.spec_from_file_location(
        "run_isolated_mechanical_reproduction",
        SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _rewrite_receipt_with_sidecar(output_dir: Path, payload: dict[str, object]) -> None:
    receipt_path = output_dir / "receipt.json"
    sidecar_path = output_dir / "receipt.json.sha256"
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    receipt_path.write_text(rendered, encoding="utf-8")
    sidecar_path.write_text(
        f"{_sha256_bytes(receipt_path.read_bytes())}  {receipt_path.name}\n",
        encoding="utf-8",
    )


def _clone_json(payload: dict[str, object]) -> dict[str, object]:
    return json.loads(json.dumps(payload))


def _set_nested(payload: dict[str, object], path: tuple[object, ...], value: object) -> None:
    target: object = payload
    for key in path[:-1]:
        if isinstance(key, int):
            target = target[key]  # type: ignore[index]
        else:
            target = target[key]  # type: ignore[index]
    last_key = path[-1]
    if isinstance(last_key, int):
        target[last_key] = value  # type: ignore[index]
    else:
        target[last_key] = value  # type: ignore[index]


def _mutate_live_execution_snapshot_state(root: Path) -> None:
    extra_text = "later source\n"
    extra_path = root / "paper/later-source.md"
    _write_text(extra_path, extra_text)
    _write_text(root / "PACKAGE_MANIFEST.md", "# package updated after receipt\n")
    _write_text(
        root / "research-case/program-state.json",
        json.dumps(
            {
                "system_name": "KEYSTONE-MPP-F1",
                "current_phase": "MANUSCRIPT",
                "novelty_status": "UNRESOLVED",
                "feasibility_decision": "UNASSESSED",
                "solution_viability_status": "ASSERTED_ONLY",
                "acceptance_readiness": "NOT_ASSESSABLE",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    manifest_path = root / "research-case/07-manuscript/source-manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["sources"].append(
        {
            "source_id": "SRC-LATER",
            "path": "paper/later-source.md",
            "path_base": "workspace_root",
            "sha256": _sha256_bytes(extra_text.encode("utf-8")),
        }
    )
    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    inventory_paths = [
        "PACKAGE_MANIFEST.md",
        "paper/later-source.md",
        "paper/source.md",
        "research-case/00-governance/authority.md",
        "research-case/07-manuscript/source-manifest.json",
        "research-case/program-state.json",
    ]
    lines: list[str] = []
    for relative in inventory_paths:
        payload_bytes = (root / relative).read_bytes()
        lines.append(f"{_sha256_bytes(payload_bytes)}  ./{relative}")
    _write_text(root / "SHA256SUMS", "\n".join(lines) + "\n")


def _build_project(root: Path) -> Path:
    governance_text = "authority: draft only\n"
    paper_text = "paper source\n"
    package_manifest_text = "# package\n"
    program_state = {
        "system_name": "KEYSTONE-MPP-F1",
        "current_phase": "INTAKE",
        "novelty_status": "UNRESOLVED",
        "feasibility_decision": "UNASSESSED",
        "solution_viability_status": "ASSERTED_ONLY",
        "acceptance_readiness": "NOT_ASSESSABLE",
    }

    _write_text(root / "research-case/00-governance/authority.md", governance_text)
    _write_text(root / "paper/source.md", paper_text)
    _write_text(root / "PACKAGE_MANIFEST.md", package_manifest_text)
    _write_text(
        root / "research-case/program-state.json",
        json.dumps(program_state, indent=2, sort_keys=True) + "\n",
    )

    manifest = {
        "schema_id": "KEYSTONE_MANUSCRIPT_SOURCE_MANIFEST",
        "schema_version": 1,
        "sources": [
            {
                "source_id": "SRC-AUTH",
                "path": "00-governance/authority.md",
                "path_base": "research_case_root",
                "sha256": _sha256_bytes(governance_text.encode("utf-8")),
            },
            {
                "source_id": "SRC-PAPER",
                "path": "paper/source.md",
                "path_base": "workspace_root",
                "sha256": _sha256_bytes(paper_text.encode("utf-8")),
            },
        ],
    }
    _write_text(
        root / "research-case/07-manuscript/source-manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )

    inventory_paths = [
        "PACKAGE_MANIFEST.md",
        "paper/source.md",
        "research-case/00-governance/authority.md",
        "research-case/07-manuscript/source-manifest.json",
        "research-case/program-state.json",
    ]
    lines: list[str] = []
    for relative in inventory_paths:
        payload = (root / relative).read_bytes()
        lines.append(f"{_sha256_bytes(payload)}  ./{relative}")
    _write_text(root / "SHA256SUMS", "\n".join(lines) + "\n")
    return root


def _command_spec(module, command_id: str, cwd: str, *argv: str):
    return module.CommandSpec(command_id=command_id, cwd=cwd, argv=tuple(argv))


def _set_fixture_output_dir(monkeypatch: pytest.MonkeyPatch, harness) -> str:
    relative = "isolated_out"
    monkeypatch.setattr(harness, "CANONICAL_OUTPUT_DIR_RELATIVE", relative)
    return relative


def test_sha256_inventory_requires_exact_format_and_matching_files(
    harness, tmp_path: Path
) -> None:
    project_root = _build_project(tmp_path / "project")

    inventory = harness.read_sha256_inventory(project_root)
    assert [entry.relative_path for entry in inventory] == [
        "PACKAGE_MANIFEST.md",
        "paper/source.md",
        "research-case/00-governance/authority.md",
        "research-case/07-manuscript/source-manifest.json",
        "research-case/program-state.json",
    ]

    (project_root / "SHA256SUMS").write_text(
        "A" * 64 + "  ./PACKAGE_MANIFEST.md\n",
        encoding="utf-8",
    )
    with pytest.raises(harness.OperationalError, match="invalid SHA256SUMS line"):
        harness.read_sha256_inventory(project_root)

    _build_project(project_root)
    manifest_path = project_root / "SHA256SUMS"
    manifest_path.write_text(
        manifest_path.read_text(encoding="utf-8")
        + manifest_path.read_text(encoding="utf-8").splitlines()[0]
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(harness.OperationalError, match="duplicate inventory path"):
        harness.read_sha256_inventory(project_root)


def test_source_manifest_check_rejects_upstream_hash_drift(
    harness, tmp_path: Path
) -> None:
    project_root = _build_project(tmp_path / "project")
    assert harness.verify_source_manifest(project_root) == 2

    source = project_root / "research-case/00-governance/authority.md"
    source.write_text(source.read_text(encoding="utf-8") + "drift\n", encoding="utf-8")

    with pytest.raises(
        harness.OperationalError,
        match="source manifest hash mismatch for SRC-AUTH",
    ):
        harness.verify_source_manifest(project_root)

    _build_project(project_root)
    (project_root / "paper/source.md").unlink()
    with pytest.raises(harness.OperationalError, match="missing inventoried file"):
        harness.read_sha256_inventory(project_root)

    _build_project(project_root)
    (project_root / "paper/source.md").write_text("changed\n", encoding="utf-8")
    with pytest.raises(harness.OperationalError, match="inventory hash mismatch"):
        harness.read_sha256_inventory(project_root)


def test_execute_captures_python_subprocess_logs_and_check_receipt_verifies(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = _build_project(tmp_path / "project")
    output_dir = project_root / _set_fixture_output_dir(monkeypatch, harness)
    monkeypatch.setattr(
        harness,
        "COMMAND_SPECS",
        (
            _command_spec(
                harness,
                "python_print",
                ".",
                "python3",
                "-c",
                "import sys; print('fixture-ok'); print('stderr-ok', file=sys.stderr)",
            ),
        ),
    )

    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 0
    )

    receipt = json.loads((output_dir / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "MECHANICAL_PASS"
    assert receipt["source_manifest_sources_verified"] == 2
    assert receipt["inventoried_file_count"] == 5
    assert receipt["pre_execution_source_inventory_sha256"] == receipt["post_execution_source_inventory_sha256"]
    assert (
        receipt["pre_execution_isolated_copy_inventory_sha256"]
        == receipt["post_execution_isolated_copy_inventory_sha256"]
    )
    command = receipt["commands"][0]
    assert command["command_id"] == "python_print"
    assert command["returncode"] == 0
    assert command["argv"] == [
        "python3",
        "-c",
        "import sys; print('fixture-ok'); print('stderr-ok', file=sys.stderr)",
    ]
    assert command["cwd"] == "."
    stdout_path = output_dir / command["stdout_path"]
    stderr_path = output_dir / command["stderr_path"]
    assert stdout_path.read_text(encoding="utf-8") == "fixture-ok\n"
    assert stderr_path.read_text(encoding="utf-8") == "stderr-ok\n"
    assert command["stdout_sha256"] == _sha256_bytes(stdout_path.read_bytes())
    assert command["stderr_sha256"] == _sha256_bytes(stderr_path.read_bytes())

    assert (
        harness.main(
            [
                "--check-receipt",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 0
    )


def test_check_receipt_accepts_historical_snapshot_after_live_state_changes(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = _build_project(tmp_path / "project")
    output_dir = project_root / _set_fixture_output_dir(monkeypatch, harness)
    monkeypatch.setattr(
        harness,
        "COMMAND_SPECS",
        (_command_spec(harness, "noop", ".", "python3", "-c", "print('ok')"),),
    )

    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 0
    )

    _mutate_live_execution_snapshot_state(project_root)

    assert (
        harness.main(
            [
                "--check-receipt",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 0
    )


def test_nonzero_subprocess_stops_after_first_failure(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = _build_project(tmp_path / "project")
    output_dir = project_root / _set_fixture_output_dir(monkeypatch, harness)
    marker_path = project_root / "second-command-ran.txt"
    monkeypatch.setattr(
        harness,
        "COMMAND_SPECS",
        (
            _command_spec(
                harness,
                "exit_seven",
                ".",
                "python3",
                "-c",
                "raise SystemExit(7)",
            ),
            _command_spec(
                harness,
                "should_not_run",
                ".",
                "python3",
                "-c",
                f"from pathlib import Path; Path({str(marker_path)!r}).write_text('ran', encoding='utf-8')",
            ),
        ),
    )

    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )

    receipt = json.loads((output_dir / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "MECHANICAL_FAIL"
    assert [row["command_id"] for row in receipt["commands"]] == ["exit_seven"]
    assert receipt["failure_reason"] == "command exit_seven returned 7"
    assert not marker_path.exists()


def test_execute_rejects_traversal_before_copy(harness, tmp_path: Path) -> None:
    project_root = _build_project(tmp_path / "project")
    (project_root / "SHA256SUMS").write_text(
        _sha256_bytes(b"escape") + "  ./../escape.txt\n",
        encoding="utf-8",
    )

    with pytest.raises(harness.OperationalError, match="path traversal"):
        harness.read_sha256_inventory(project_root)


def test_source_mutation_in_original_tree_marks_mechanical_fail(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = _build_project(tmp_path / "project")
    output_dir = project_root / _set_fixture_output_dir(monkeypatch, harness)
    target_path = project_root / "paper/source.md"
    monkeypatch.setattr(
        harness,
        "COMMAND_SPECS",
        (
            _command_spec(
                harness,
                "mutate_original",
                ".",
                "python3",
                "-c",
                (
                    "from pathlib import Path; "
                    f"Path({str(target_path)!r}).write_text('mutated\\n', encoding='utf-8')"
                ),
            ),
        ),
    )

    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )

    receipt = json.loads((output_dir / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "MECHANICAL_FAIL"
    assert receipt["source_tree_unchanged"] is False
    assert receipt["failure_reason"] == "source inventory changed during execution"


def test_isolated_copy_mutation_marks_mechanical_fail(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = _build_project(tmp_path / "project")
    output_dir = project_root / _set_fixture_output_dir(monkeypatch, harness)
    monkeypatch.setattr(
        harness,
        "COMMAND_SPECS",
        (
            _command_spec(
                harness,
                "mutate_isolated",
                ".",
                "python3",
                "-c",
                (
                    "from pathlib import Path; "
                    "Path('paper/source.md').write_text('mutated in isolated copy\\n', encoding='utf-8')"
                ),
            ),
        ),
    )

    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )

    receipt = json.loads((output_dir / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "MECHANICAL_FAIL"
    assert (
        receipt["pre_execution_isolated_copy_inventory_sha256"]
        != receipt["post_execution_isolated_copy_inventory_sha256"]
    )
    assert receipt["isolated_copy_unchanged"] is False
    assert receipt["failure_reason"] == "isolated copy inventory changed during execution"


def test_source_deletion_after_commands_preserves_fail_receipt_and_logs(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = _build_project(tmp_path / "project")
    output_dir = project_root / _set_fixture_output_dir(monkeypatch, harness)
    target_path = project_root / "paper/source.md"
    monkeypatch.setattr(
        harness,
        "COMMAND_SPECS",
        (
            _command_spec(
                harness,
                "log_then_delete_source",
                ".",
                "python3",
                "-c",
                (
                    "from pathlib import Path; "
                    "print('before-delete'); "
                    f"Path({str(target_path)!r}).unlink()"
                ),
            ),
        ),
    )

    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )

    receipt = json.loads((output_dir / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "MECHANICAL_FAIL"
    assert receipt["source_tree_unchanged"] is False
    assert receipt["post_execution_source_inventory_sha256"] is None
    assert (
        receipt["source_inventory_verification_error"]
        == "missing inventoried file during verification: paper/source.md"
    )
    assert (
        output_dir / "commands/log_then_delete_source.stdout.txt"
    ).read_text(encoding="utf-8") == "before-delete\n"


def test_isolated_deletion_after_commands_preserves_fail_receipt_and_logs(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = _build_project(tmp_path / "project")
    output_dir = project_root / _set_fixture_output_dir(monkeypatch, harness)
    monkeypatch.setattr(
        harness,
        "COMMAND_SPECS",
        (
            _command_spec(
                harness,
                "log_then_delete_isolated",
                ".",
                "python3",
                "-c",
                (
                    "from pathlib import Path; "
                    "print('before-delete'); "
                    "Path('paper/source.md').unlink()"
                ),
            ),
        ),
    )

    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )

    receipt = json.loads((output_dir / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "MECHANICAL_FAIL"
    assert receipt["isolated_copy_unchanged"] is False
    assert receipt["post_execution_isolated_copy_inventory_sha256"] is None
    assert (
        receipt["isolated_copy_inventory_verification_error"]
        == "missing inventoried file during verification: paper/source.md"
    )
    assert (
        output_dir / "commands/log_then_delete_isolated.stdout.txt"
    ).read_text(encoding="utf-8") == "before-delete\n"


def test_receipt_tamper_is_detected(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    project_root = _build_project(tmp_path / "project")
    output_dir = project_root / _set_fixture_output_dir(monkeypatch, harness)
    monkeypatch.setattr(
        harness,
        "COMMAND_SPECS",
        (_command_spec(harness, "noop", ".", "python3", "-c", "print('ok')"),),
    )

    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 0
    )

    receipt_path = output_dir / "receipt.json"
    payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    payload["status"] = "MECHANICAL_FAIL"
    _rewrite_receipt_with_sidecar(output_dir, payload)

    assert (
        harness.main(
            [
                "--check-receipt",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )
    captured = capsys.readouterr()
    assert captured.err.startswith("error: ")

    rendered_receipt = receipt_path.read_text(encoding="utf-8")
    payload = json.loads(rendered_receipt)
    payload["sha256sums_sha256"] = "0" * 64
    payload["post_execution_source_inventory_sha256"] = "1" * 64
    payload["pre_execution_source_inventory_sha256"] = "1" * 64
    _rewrite_receipt_with_sidecar(output_dir, payload)

    assert (
        harness.main(
            [
                "--check-receipt",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )
    captured = capsys.readouterr()
    assert captured.err.startswith("error: ")

    payload = json.loads(rendered_receipt)
    payload["tools_platform"]["command_environment_overrides"]["FOUNDRY_OFFLINE"] = "true"
    payload["tools_platform_sha256"] = _sha256_bytes(
        json.dumps(payload["tools_platform"], indent=2, sort_keys=True).encode("utf-8")
    )
    _rewrite_receipt_with_sidecar(output_dir, payload)
    assert (
        harness.main(
            [
                "--check-receipt",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )
    assert capsys.readouterr().err.startswith("error: ")

    payload = json.loads(rendered_receipt)
    payload["tools_platform_sha256"] = "0" * 64
    _rewrite_receipt_with_sidecar(output_dir, payload)
    assert (
        harness.main(
            [
                "--check-receipt",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )
    assert capsys.readouterr().err.startswith("error: ")

    payload = json.loads(rendered_receipt)
    payload["residual_limitations"] = payload["residual_limitations"][:-1]
    _rewrite_receipt_with_sidecar(output_dir, payload)
    assert (
        harness.main(
            [
                "--check-receipt",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )
    assert capsys.readouterr().err.startswith("error: ")


def test_secret_environment_values_are_not_serialized(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = _build_project(tmp_path / "project")
    output_dir = project_root / _set_fixture_output_dir(monkeypatch, harness)
    monkeypatch.setenv("TOP_SECRET_TOKEN", "very-secret-value")
    monkeypatch.setattr(
        harness,
        "COMMAND_SPECS",
        (
            _command_spec(
                harness,
                "env_probe",
                ".",
                "python3",
                "-c",
                "import os; print(os.environ.get('TOP_SECRET_TOKEN', 'missing'))",
            ),
        ),
    )

    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 0
    )

    rendered_receipt = (output_dir / "receipt.json").read_text(encoding="utf-8")
    rendered_stdout = (output_dir / "commands/env_probe.stdout.txt").read_text(encoding="utf-8")
    rendered_stderr = (output_dir / "commands/env_probe.stderr.txt").read_text(encoding="utf-8")
    assert rendered_stdout == "missing\n"
    assert "very-secret-value" not in rendered_receipt
    assert "very-secret-value" not in rendered_stdout
    assert "very-secret-value" not in rendered_stderr


def test_check_receipt_rejects_tampered_log_paths_and_command_contract(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    project_root = _build_project(tmp_path / "project")
    output_dir = project_root / _set_fixture_output_dir(monkeypatch, harness)
    monkeypatch.setattr(
        harness,
        "COMMAND_SPECS",
        (_command_spec(harness, "noop", ".", "python3", "-c", "print('ok')"),),
    )

    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 0
    )

    rendered_receipt = (output_dir / "receipt.json").read_text(encoding="utf-8")
    payload = json.loads(rendered_receipt)
    payload["commands"][0]["stdout_path"] = "../escape.txt"
    _rewrite_receipt_with_sidecar(output_dir, payload)
    assert (
        harness.main(
            [
                "--check-receipt",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )
    assert "error: " in capsys.readouterr().err

    payload = json.loads(rendered_receipt)
    payload["commands"][0]["argv"] = ["python3", "-V"]
    _rewrite_receipt_with_sidecar(output_dir, payload)
    assert (
        harness.main(
            [
                "--check-receipt",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )
    assert "error: " in capsys.readouterr().err

    payload = json.loads(rendered_receipt)
    payload["commands"][0]["cwd"] = "prototype"
    _rewrite_receipt_with_sidecar(output_dir, payload)
    assert (
        harness.main(
            [
                "--check-receipt",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )
    assert "error: " in capsys.readouterr().err


def test_check_receipt_rejects_invalid_execution_snapshot_fields(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    project_root = _build_project(tmp_path / "project")
    output_dir = project_root / _set_fixture_output_dir(monkeypatch, harness)
    monkeypatch.setattr(
        harness,
        "COMMAND_SPECS",
        (_command_spec(harness, "noop", ".", "python3", "-c", "print('ok')"),),
    )

    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 0
    )

    baseline = json.loads((output_dir / "receipt.json").read_text(encoding="utf-8"))

    invalid_counts = (
        ("inventoried_file_count", "5"),
        ("inventoried_file_count", 0),
        ("source_manifest_sources_verified", "2"),
        ("source_manifest_sources_verified", 0),
    )
    for field_name, invalid_value in invalid_counts:
        payload = _clone_json(baseline)
        payload[field_name] = invalid_value
        _rewrite_receipt_with_sidecar(output_dir, payload)
        assert (
            harness.main(
                [
                    "--check-receipt",
                    "--project-root",
                    str(project_root),
                    "--output-dir",
                    str(output_dir),
                ]
            )
            == 1
        )
        assert capsys.readouterr().err.startswith("error: ")

    invalid_digests = (
        "sha256sums_sha256",
        "package_manifest_sha256",
        "program_state_sha256",
        "source_manifest_sha256",
    )
    for field_name in invalid_digests:
        payload = _clone_json(baseline)
        payload[field_name] = "not-a-digest"
        _rewrite_receipt_with_sidecar(output_dir, payload)
        assert (
            harness.main(
                [
                    "--check-receipt",
                    "--project-root",
                    str(project_root),
                    "--output-dir",
                    str(output_dir),
                ]
        )
        == 1
    )
    assert capsys.readouterr().err.startswith("error: ")


@pytest.mark.parametrize(
    ("field_updates", "label"),
    (
        (((("pre_execution_source_inventory_sha256",), "not-a-digest"),), "bad_source_pre_digest"),
        (((("post_execution_source_inventory_sha256",), "not-a-digest"),), "bad_source_post_digest"),
        (((("pre_execution_isolated_copy_inventory_sha256",), "not-a-digest"),), "bad_isolated_pre_digest"),
        (((("post_execution_isolated_copy_inventory_sha256",), "not-a-digest"),), "bad_isolated_post_digest"),
        (((("source_tree_unchanged",), False),), "source_bool_mismatch"),
        (((("isolated_copy_unchanged",), False),), "isolated_bool_mismatch"),
        (((("source_inventory_verification_error",), ""),), "empty_source_error"),
        (((("isolated_copy_inventory_verification_error",), ""),), "empty_isolated_error"),
        (((("source_inventory_verification_error",), "unexpected"),), "source_error_with_post_digest"),
        (((("isolated_copy_inventory_verification_error",), "unexpected"),), "isolated_error_with_post_digest"),
        (((("post_execution_source_inventory_sha256",), None),), "source_post_missing_without_error"),
        (((("post_execution_isolated_copy_inventory_sha256",), None),), "isolated_post_missing_without_error"),
    ),
)
def test_check_receipt_rejects_invalid_inventory_digest_and_evidence_fields(
    harness,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    field_updates: tuple[tuple[tuple[object, ...], object], ...],
    label: str,
) -> None:
    project_root = _build_project(tmp_path / label)
    output_dir = project_root / _set_fixture_output_dir(monkeypatch, harness)
    monkeypatch.setattr(
        harness,
        "COMMAND_SPECS",
        (_command_spec(harness, "noop", ".", "python3", "-c", "print('ok')"),),
    )

    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 0
    )

    payload = json.loads((output_dir / "receipt.json").read_text(encoding="utf-8"))
    mutated = _clone_json(payload)
    for path, value in field_updates:
        _set_nested(mutated, path, value)
    _rewrite_receipt_with_sidecar(output_dir, mutated)

    assert (
        harness.main(
            [
                "--check-receipt",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )
    assert capsys.readouterr().err.startswith("error: ")


@pytest.mark.parametrize(
    ("path", "label"),
    (
        (("commands", 0, "stdout_sha256"), "bad_stdout_sha256"),
        (("commands", 0, "stderr_sha256"), "bad_stderr_sha256"),
        (("commands", 0, "argv_sha256"), "bad_argv_sha256"),
        (("commands", 0, "cwd_sha256"), "bad_cwd_sha256"),
    ),
)
def test_check_receipt_rejects_malformed_command_hash_fields(
    harness,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    path: tuple[object, ...],
    label: str,
) -> None:
    project_root = _build_project(tmp_path / label)
    output_dir = project_root / _set_fixture_output_dir(monkeypatch, harness)
    monkeypatch.setattr(
        harness,
        "COMMAND_SPECS",
        (_command_spec(harness, "noop", ".", "python3", "-c", "print('ok')"),),
    )

    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 0
    )

    payload = json.loads((output_dir / "receipt.json").read_text(encoding="utf-8"))
    mutated = _clone_json(payload)
    _set_nested(mutated, path, "not-a-digest")
    _rewrite_receipt_with_sidecar(output_dir, mutated)

    assert (
        harness.main(
            [
                "--check-receipt",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )
    assert capsys.readouterr().err.startswith("error: ")


def test_check_receipt_rejects_truncated_success_prefix_disguised_as_fail(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    project_root = _build_project(tmp_path / "project")
    output_dir = project_root / _set_fixture_output_dir(monkeypatch, harness)
    monkeypatch.setattr(
        harness,
        "COMMAND_SPECS",
        (
            _command_spec(harness, "first", ".", "python3", "-c", "print('first')"),
            _command_spec(harness, "second", ".", "python3", "-c", "print('second')"),
        ),
    )

    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 0
    )

    payload = json.loads((output_dir / "receipt.json").read_text(encoding="utf-8"))
    payload["status"] = "MECHANICAL_FAIL"
    payload["failure_reason"] = "command second returned 0"
    payload["commands"] = payload["commands"][:1]
    _rewrite_receipt_with_sidecar(output_dir, payload)
    assert (
        harness.main(
            [
                "--check-receipt",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 1
    )
    assert capsys.readouterr().err.startswith("error: ")


def test_output_dir_validation_and_cli_mode_rejection(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    project_root = _build_project(tmp_path / "project")
    canonical_relative = _set_fixture_output_dir(monkeypatch, harness)
    canonical_output = project_root / canonical_relative

    outside_output = tmp_path / "outside"
    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(outside_output),
            ]
        )
        == 1
    )
    assert "error: output directory escapes project root" in capsys.readouterr().err

    wrong_in_tree_output = project_root / "research-case/tmp-output"
    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(wrong_in_tree_output),
            ]
        )
        == 1
    )
    assert "error: output directory must match canonical path" in capsys.readouterr().err

    nonempty_output = canonical_output
    nonempty_output.mkdir()
    (nonempty_output / "stale.txt").write_text("stale\n", encoding="utf-8")
    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(nonempty_output),
            ]
        )
        == 1
    )
    assert "error: output directory must be empty" in capsys.readouterr().err

    symlink_target = tmp_path / "symlink-target"
    symlink_target.mkdir()
    symlink_output = canonical_output
    shutil.rmtree(nonempty_output)
    symlink_output.symlink_to(symlink_target, target_is_directory=True)
    assert (
        harness.main(
            [
                "--execute",
                "--project-root",
                str(project_root),
                "--output-dir",
                str(symlink_output),
            ]
        )
        == 1
    )
    assert "error: output directory may not be a symlink" in capsys.readouterr().err

    with pytest.raises(SystemExit):
        harness.parse_args(["--execute", "--dry-run"])

    assert canonical_output == project_root / canonical_relative


def test_command_environment_overrides_match_frozen_contract(harness) -> None:
    assert harness.COMMAND_ENV_OVERRIDES == {
        "UV_OFFLINE": "1",
        "CARGO_NET_OFFLINE": "true",
        "FOUNDRY_OFFLINE": "true",
        "NO_COLOR": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTEST_ADDOPTS": "-p no:cacheprovider",
    }


def test_dry_run_prints_frozen_ids_and_writes_nothing(
    harness, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    project_root = _build_project(tmp_path / "project")

    assert harness.main(["--project-root", str(project_root)]) == 0

    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "deadline_package_check",
        "t1_t8_check",
        "paper_tables_check",
        "python_suite",
        "foundry_test",
        "gas_snapshot_check",
        "gas_report_check",
        "test_vectors_check",
        "signature_vectors_check",
        "strict_research_case",
    ]
    assert not (project_root / "receipt.json").exists()
    assert not (project_root / "isolated_out").exists()
