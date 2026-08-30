from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export_draft_adversarial_reviews.py"


def _run(root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *extra],
        text=True,
        capture_output=True,
        check=False,
    )


def _copy_subset(destination: Path) -> Path:
    project = destination / "case"
    for relative in (
        "research-case",
        "paper",
        "diagrams",
        "prototype/results",
        "scripts/check_manuscript_alignment.py",
        "prototype/tests/test_manuscript_alignment.py",
    ):
        source = ROOT / relative
        target = project / relative
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return project


def test_workspace_reviews_are_current() -> None:
    result = _run(ROOT, "--check")
    assert result.returncode == 0, result.stderr


def test_manuscript_drift_makes_reviews_stale(tmp_path: Path) -> None:
    project = _copy_subset(tmp_path)
    manuscript = project / "research-case/07-manuscript/manuscript.md"
    original = manuscript.read_text(encoding="utf-8")
    manuscript.write_text(
        original.replace("Novelty remains unresolved,", "Novelty seems resolved,"),
        encoding="utf-8",
    )

    result = _run(project, "--check")

    assert result.returncode == 1
    assert "manuscript alignment precondition failed" in result.stderr
