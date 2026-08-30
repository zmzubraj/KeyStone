#!/usr/bin/env python3
"""Build and verify the KEYSTONE preauthorization manuscript PDF."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = Path("research-case/07-manuscript/manuscript.md")
BIBLIOGRAPHY = Path("paper/references.bib")
PROGRAM_STATE = Path("research-case/program-state.json")
OUTPUT_DIR = Path("paper/preauthorization-build")
STATUS = "DRAFT_PREAUTHORIZATION_NOT_SUBMISSION_READY"
WATERMARK = "NONE"
SUBMISSION_PREREQUISITE_REMEDIATIONS = [
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

IMAGE_RE = re.compile(r"(!\[[^\]]*\]\()([^\s)]+\.svg)(\))")


class BuildError(RuntimeError):
    """Raised when the fail-closed draft build cannot be completed."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rewrite_svg_references(
    markdown: str,
    *,
    manuscript_dir: Path,
    workspace_root: Path,
) -> tuple[str, list[dict[str, str]]]:
    """Rewrite manuscript SVG images to checked PNG derivatives for PDF input."""
    assets: list[dict[str, str]] = []

    def replace(match: re.Match[str]) -> str:
        raw = match.group(2)
        svg = (manuscript_dir / raw).resolve()
        try:
            canonical_svg = svg.relative_to(workspace_root.resolve())
        except ValueError as exc:
            raise BuildError(f"SVG reference escapes workspace: {raw}") from exc
        if not svg.is_file():
            raise BuildError(f"missing canonical SVG: {canonical_svg.as_posix()}")
        png = svg.with_suffix(".png")
        if not png.is_file():
            raise BuildError(
                f"missing PNG derivative for {canonical_svg.as_posix()}"
            )
        canonical_png = png.relative_to(workspace_root.resolve())
        record = {
            "canonical_svg": canonical_svg.as_posix(),
            "pdf_derivative_png": canonical_png.as_posix(),
        }
        if record not in assets:
            assets.append(record)
        return f"{match.group(1)}{canonical_png.as_posix()}{match.group(3)}"

    return IMAGE_RE.sub(replace, markdown), assets


def _required_tool(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise BuildError(f"required tool not found: {name}")
    return path


def _tool_version(argv: list[str]) -> str:
    result = subprocess.run(argv, text=True, capture_output=True, check=False)
    output = (result.stdout or result.stderr).strip().splitlines()
    return output[0] if output else "UNKNOWN"


def _header_text() -> str:
    return r"""\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\footnotesize INTAKE --- NOT SUBMISSION READY --- AUTHOR METADATA DEFERRED}
\fancyfoot[R]{\thepage}
\setlength{\headheight}{14pt}
"""


def _source_inventory(root: Path, assets: list[dict[str, str]]) -> list[dict[str, str]]:
    paths = [MANUSCRIPT, BIBLIOGRAPHY, PROGRAM_STATE]
    for asset in assets:
        paths.extend((Path(asset["canonical_svg"]), Path(asset["pdf_derivative_png"])))
    unique = sorted(set(paths), key=lambda path: path.as_posix())
    return [
        {"path": path.as_posix(), "sha256": sha256(root / path)}
        for path in unique
    ]


def build(root: Path = ROOT, output_dir: Path | None = None) -> dict[str, object]:
    root = root.resolve()
    out = (root / (output_dir or OUTPUT_DIR)).resolve()
    manuscript_path = root / MANUSCRIPT
    state = json.loads((root / PROGRAM_STATE).read_text(encoding="utf-8"))
    phase = state.get("current_phase")
    if phase != "INTAKE":
        raise BuildError(f"draft builder is phase-bound to INTAKE; found {phase!r}")

    rewritten, assets = rewrite_svg_references(
        manuscript_path.read_text(encoding="utf-8"),
        manuscript_dir=manuscript_path.parent,
        workspace_root=root,
    )
    out.mkdir(parents=True, exist_ok=True)
    prepared = out / "manuscript-prepared.md"
    header = out / "preauthorization-header.tex"
    tex = out / "main.tex"
    pdf = out / "main.pdf"
    log = out / "build.log"
    prepared.write_text(rewritten, encoding="utf-8")
    header.write_text(_header_text(), encoding="utf-8")

    pandoc = _required_tool("pandoc")
    xelatex = _required_tool("xelatex")
    pdfinfo = _required_tool("pdfinfo")
    pdffonts = _required_tool("pdffonts")
    common = [
        pandoc,
        str(prepared),
        "--from=markdown",
        "--standalone",
        "--citeproc",
        f"--bibliography={root / BIBLIOGRAPHY}",
        f"--resource-path={root}",
        f"--include-in-header={header}",
        "--metadata=title:KEYSTONE-MPP-F1 --- DRAFT PREAUTHORIZATION MANUSCRIPT",
        "--metadata=author:Author metadata deferred",
        "--metadata=date:2026-08-30",
    ]
    env = os.environ.copy()
    env.update({"SOURCE_DATE_EPOCH": "1788048000", "TZ": "UTC"})

    tex_result = subprocess.run(
        [*common, "--output", str(tex)],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    pdf_result = subprocess.run(
        [*common, "--pdf-engine", xelatex, "--output", str(pdf)],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    log_text = (
        "PANDOC TEX\n" + tex_result.stdout + tex_result.stderr
        + "\nPANDOC PDF\n" + pdf_result.stdout + pdf_result.stderr
    )
    log.write_text(log_text, encoding="utf-8")
    if tex_result.returncode != 0 or pdf_result.returncode != 0 or not pdf.is_file():
        raise BuildError(f"Pandoc/XeLaTeX build failed; inspect {log.relative_to(root)}")

    info_result = subprocess.run(
        [pdfinfo, str(pdf)], text=True, capture_output=True, check=False
    )
    fonts_result = subprocess.run(
        [pdffonts, str(pdf)], text=True, capture_output=True, check=False
    )
    if info_result.returncode != 0 or fonts_result.returncode != 0:
        raise BuildError("PDF mechanical inspection failed")
    pages_match = re.search(r"^Pages:\s+(\d+)$", info_result.stdout, re.MULTILINE)
    if pages_match is None:
        raise BuildError("pdfinfo did not report a page count")
    page_count = int(pages_match.group(1))
    font_lines = [line for line in fonts_result.stdout.splitlines()[2:] if line.strip()]
    font_flags = [
        re.search(r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", line)
        for line in font_lines
    ]
    if any(match is None for match in font_flags):
        raise BuildError("could not parse pdffonts output")
    unembedded = [
        line for line, match in zip(font_lines, font_flags, strict=True)
        if match is not None and match.group(1) != "yes"
    ]
    if unembedded:
        raise BuildError("PDF contains unembedded fonts")

    unresolved_patterns = (
        r"citation not found", r"undefined references", r"undefined citation",
        r"there were undefined references",
    )
    unresolved = sum(
        len(re.findall(pattern, log_text, flags=re.IGNORECASE))
        for pattern in unresolved_patterns
    )
    if unresolved:
        raise BuildError("unresolved citation/reference warning in build log")

    qa = {
        "page_count": page_count,
        "fonts_embedded": True,
        "font_count": len(font_lines),
        "unresolved_reference_count": unresolved,
        "rendered_page_human_review": "PENDING",
        "official_venue_template": "NOT_SELECTED",
    }
    (out / "pdf-qa.json").write_text(
        json.dumps(qa, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    sources = _source_inventory(root, assets)
    outputs = []
    for path in (prepared, header, tex, pdf, log, out / "pdf-qa.json"):
        outputs.append({"path": path.relative_to(root).as_posix(), "sha256": sha256(path)})
    manifest: dict[str, object] = {
        "schema_id": "KEYSTONE_DRAFT_MANUSCRIPT_BUILD",
        "schema_version": 1,
        "status": STATUS,
        "canonical_phase": "INTAKE",
        "canonical_acceptance_readiness": state.get("acceptance_readiness"),
        "watermark": WATERMARK,
        "visual_watermark_present": False,
        "watermark_removed_by_accountable_author": True,
        "build_classification": "INTERNAL_PREAUTHORIZATION_ONLY",
        "scientific_gate_promoted": False,
        "submission_authorized": False,
        "external_transfer_authorized": False,
        "blocking_serial_gate": "INTAKE",
        "external_review_blocker": "REM-001",
        "submission_prerequisite_remediations": SUBMISSION_PREREQUISITE_REMEDIATIONS,
        "official_venue_template": "NOT_SELECTED",
        "author_metadata_status": "DEFERRED_BY_ACCOUNTABLE_AUTHOR",
        "page_count": page_count,
        "unresolved_reference_count": unresolved,
        "pdf_sha256": sha256(pdf),
        "assets": assets,
        "sources": sources,
        "outputs": outputs,
        "tools": {
            "pandoc": _tool_version([pandoc, "--version"]),
            "xelatex": _tool_version([xelatex, "--version"]),
            "pdfinfo": _tool_version([pdfinfo, "-v"]),
            "pdffonts": _tool_version([pdffonts, "-v"]),
        },
        "limitations": [
            "Draft preauthorization build only; no scientific gate is promoted.",
            "External transfer is not authorized from this build package.",
            "Rendered-page accountable human review remains pending.",
            "No official venue or venue template has been selected.",
            "Novelty, feasibility, independent verification, and submission approval remain unresolved.",
        ],
    }
    manifest_path = out / "build-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def check(root: Path = ROOT, output_dir: Path | None = None) -> list[str]:
    root = root.resolve()
    out = (root / (output_dir or OUTPUT_DIR)).resolve()
    manifest_path = out / "build-manifest.json"
    errors: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid build manifest: {exc}"]
    required = {
        "status": STATUS,
        "canonical_phase": "INTAKE",
        "canonical_acceptance_readiness": "NOT_ASSESSABLE",
        "watermark": WATERMARK,
        "visual_watermark_present": False,
        "watermark_removed_by_accountable_author": True,
        "build_classification": "INTERNAL_PREAUTHORIZATION_ONLY",
        "scientific_gate_promoted": False,
        "submission_authorized": False,
        "external_transfer_authorized": False,
        "blocking_serial_gate": "INTAKE",
        "external_review_blocker": "REM-001",
    }
    for key, value in required.items():
        if manifest.get(key) != value:
            errors.append(f"manifest {key} drift")
    state = json.loads((root / PROGRAM_STATE).read_text(encoding="utf-8"))
    if state.get("current_phase") != "INTAKE":
        errors.append("canonical phase is not INTAKE")
    for item in manifest.get("sources", []):
        path = root / item.get("path", "")
        if not path.is_file() or sha256(path) != item.get("sha256"):
            errors.append(f"source drift: {item.get('path')}")
    for item in manifest.get("outputs", []):
        path = root / item.get("path", "")
        if not path.is_file() or sha256(path) != item.get("sha256"):
            errors.append(f"output drift: {item.get('path')}")
    pdf = out / "main.pdf"
    if not pdf.is_file() or sha256(pdf) != manifest.get("pdf_sha256"):
        errors.append("PDF hash drift")
    if not isinstance(manifest.get("page_count"), int) or manifest["page_count"] <= 0:
        errors.append("invalid page count")
    if manifest.get("unresolved_reference_count") != 0:
        errors.append("unresolved references present")
    if manifest.get("submission_prerequisite_remediations") != SUBMISSION_PREREQUISITE_REMEDIATIONS:
        errors.append("submission prerequisite remediation drift")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args(argv)
    try:
        if args.check:
            errors = check(args.project_root, args.output_dir)
            if errors:
                print("\n".join(errors), file=sys.stderr)
                return 1
            print("Draft manuscript build check passed")
            return 0
        manifest = build(args.project_root, args.output_dir)
        print(json.dumps({
            "status": manifest["status"],
            "pdf_sha256": manifest["pdf_sha256"],
            "page_count": manifest["page_count"],
        }, sort_keys=True))
        return 0
    except (BuildError, OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
