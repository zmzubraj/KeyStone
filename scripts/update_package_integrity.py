#!/usr/bin/env python3
"""Regenerate the KEYSTONE package inventory and SHA-256 manifest."""

from __future__ import annotations

import hashlib
import subprocess
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "PACKAGE_MANIFEST.md"
CHECKSUMS = ROOT / "SHA256SUMS"
EXCLUDED = {"PACKAGE_MANIFEST.md", "SHA256SUMS"}
EXTRA_INVENTORY_FILES = (
    Path(".superpowers/sdd/keystone_mpp_goal_plan/prospective-deterministic-case-manifest.csv"),
)


def workspace_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        relative = Path(raw.decode("utf-8"))
        if relative.as_posix() in EXCLUDED:
            continue
        candidate = ROOT / relative
        if candidate.is_file():
            paths.append(relative)

    seen = {path.as_posix() for path in paths}
    for relative in EXTRA_INVENTORY_FILES:
        if relative.as_posix() in EXCLUDED or relative.as_posix() in seen:
            continue
        candidate = ROOT / relative
        if candidate.is_file():
            paths.append(relative)
            seen.add(relative.as_posix())
    return sorted(paths, key=lambda item: item.as_posix())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def render_manifest(files: list[Path]) -> str:
    lines = [
        "# Package Manifest",
        "",
        "**Artifact:** KEYSTONE MPP v1.0 active research workspace",
        f"**Generated:** {date.today().isoformat()}",
        "",
        "This inventory covers source, preliminary research evidence, workspace controls,",
        "the schema-v4 research case, and reproducibility artifacts. It excludes `.git`,",
        "virtual environments, caches, Foundry build output, OS metadata, and the transient",
        "research-case runtime lock. Presence in this manifest does not make a scientific",
        "artifact independently verified.",
        "",
        f"**Inventoried files:** {len(files)} plus `PACKAGE_MANIFEST.md`; `SHA256SUMS` is excluded from its own checksum set.",
        "",
        "## Entry points",
        "",
        "- `FREEZE.md` — frozen thesis, claim boundaries, and change control.",
        "- `RESEARCH_INTAKE.md` — canonical six-field program intake.",
        "- `research-case/program-state.json` — authoritative research phase and resume state.",
        "- `docs/19_MPP_TO_PUBLISHABLE_PAPER_PLAN_BN.md` — detailed Bangla execution contract.",
        "- `WORKSPACE.md` and `Makefile` — setup, verification, reproduction, and integrity workflow.",
        "- `VERIFICATION.md` — latest executed evidence and limitations.",
        "- `contracts/gas_report.csv` — generated preliminary contract-operation gas table.",
        "",
        "## File inventory",
        "",
    ]
    for relative in files:
        size = (ROOT / relative).stat().st_size
        lines.append(f"- `./{relative.as_posix()}` ({size} bytes)")
    lines.extend(
        [
            "",
            "`SHA256SUMS` covers every file above plus `PACKAGE_MANIFEST.md` and excludes itself.",
            "Regenerate both artifacts with `make refresh-integrity` after reviewing a material change.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    files = workspace_files()
    MANIFEST.write_text(render_manifest(files), encoding="utf-8")
    checksum_files = sorted(files + [Path("PACKAGE_MANIFEST.md")], key=lambda item: item.as_posix())
    CHECKSUMS.write_text(
        "".join(f"{sha256(ROOT / relative)}  ./{relative.as_posix()}\n" for relative in checksum_files),
        encoding="utf-8",
    )
    print(f"Wrote {MANIFEST.relative_to(ROOT)} with {len(files)} inventory entries")
    print(f"Wrote {CHECKSUMS.relative_to(ROOT)} with {len(checksum_files)} hashes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
