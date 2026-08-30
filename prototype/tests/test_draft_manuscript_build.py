from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/build_draft_manuscript.py"
OUTPUT_DIR = ROOT / "paper/preauthorization-build"


def _load_module():
    spec = importlib.util.spec_from_file_location("build_draft_manuscript", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_svg_references_are_rewritten_to_existing_png_derivatives(tmp_path: Path) -> None:
    module = _load_module()
    root = tmp_path / "workspace"
    manuscript_dir = root / "research-case/07-manuscript"
    svg = root / "diagrams/example.svg"
    png = root / "diagrams/example.png"
    manuscript_dir.mkdir(parents=True)
    svg.parent.mkdir(parents=True)
    svg.write_text("<svg/>\n", encoding="utf-8")
    png.write_bytes(b"png")

    rewritten, assets = module.rewrite_svg_references(
        "![Example](../../diagrams/example.svg)\n",
        manuscript_dir=manuscript_dir,
        workspace_root=root,
    )

    assert rewritten == "![Example](diagrams/example.png)\n"
    assert assets == [
        {
            "canonical_svg": "diagrams/example.svg",
            "pdf_derivative_png": "diagrams/example.png",
        }
    ]


def test_missing_png_derivative_fails_closed(tmp_path: Path) -> None:
    module = _load_module()
    root = tmp_path / "workspace"
    manuscript_dir = root / "research-case/07-manuscript"
    svg = root / "diagrams/example.svg"
    manuscript_dir.mkdir(parents=True)
    svg.parent.mkdir(parents=True)
    svg.write_text("<svg/>\n", encoding="utf-8")

    try:
        module.rewrite_svg_references(
            "![Example](../../diagrams/example.svg)\n",
            manuscript_dir=manuscript_dir,
            workspace_root=root,
        )
    except module.BuildError as exc:
        assert "missing PNG derivative" in str(exc)
    else:
        raise AssertionError("missing derivative must fail closed")


def test_checked_in_preauthorization_build_is_current() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    manifest = json.loads((OUTPUT_DIR / "build-manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "DRAFT_PREAUTHORIZATION_NOT_SUBMISSION_READY"
    assert manifest["canonical_phase"] == "INTAKE"
    assert manifest["canonical_acceptance_readiness"] == "NOT_ASSESSABLE"
    assert manifest["watermark"] == "NONE"
    assert manifest["visual_watermark_present"] is False
    assert manifest["watermark_removed_by_accountable_author"] is True
    assert manifest["build_classification"] == "INTERNAL_PREAUTHORIZATION_ONLY"
    assert manifest["scientific_gate_promoted"] is False
    assert manifest["submission_authorized"] is False
    assert manifest["external_transfer_authorized"] is False
    assert manifest["blocking_serial_gate"] == "INTAKE"
    assert manifest["external_review_blocker"] == "REM-001"
    assert manifest["submission_prerequisite_remediations"] == [
        "REM-001",
        "REM-002",
        "REM-003",
        "REM-004",
        "REM-005",
        "REM-006",
        "REM-007",
        "REM-008",
        "REM-009",
        "REM-011",
        "REM-012",
    ]
    assert manifest["pdf_sha256"]
    assert manifest["page_count"] > 0
    assert manifest["unresolved_reference_count"] == 0
