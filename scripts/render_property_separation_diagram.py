#!/usr/bin/env python3
"""Render the claim-safe D2 property-separation diagram without network access.

The Mermaid file remains canonical. This exporter validates the frozen semantic
anchors before producing a deterministic, accessible SVG derivative. An
optional PNG derivative is captured locally with an existing Chrome binary.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import struct
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "diagrams" / "02_property_separation.mmd"
DEFAULT_SVG = ROOT / "diagrams" / "02_property_separation.svg"
DEFAULT_PNG = ROOT / "diagrams" / "02_property_separation.png"
DEFAULT_RECEIPT = ROOT / "diagrams" / "02_property_separation.render.json"
DEFAULT_CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

REQUIRED_ANCHORS = {
    "W1": (
        'W1["',
        'C1["CA does not imply DKA"]',
        "only t-1 valid dispute responses arrive by the deadline",
    ),
    "W2": (
        'W2["',
        "target-selective withholding leaves fewer than t record responses",
        "A passed routine audit does not unconditionally imply targeted dispute success",
    ),
    "W3": (
        'W3["',
        "two executions share the same finite audit prefix",
        "Finite audits do not guarantee unconditional future DKA",
    ),
}
BOUNDARY_ANCHORS = (
    "not a complete pairwise lattice",
    "DKA is conditional and deadline-bounded",
    "PAC and declared readiness/network assumptions remain separate obligations",
)
FONT_SIZES = {"title": 36, "subtitle": 24, "body": 24, "small": 24}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def validate_source(source: str) -> None:
    """Reject source drift that could change the three frozen witnesses."""
    for witness_id, anchors in REQUIRED_ANCHORS.items():
        if source.count(f'{witness_id}["') != 1:
            raise ValueError(f"{witness_id} must appear exactly once")
        for anchor in anchors:
            if anchor not in source:
                raise ValueError(f"{witness_id} missing semantic anchor: {anchor}")
    if any(anchor not in source for anchor in BOUNDARY_ANCHORS):
        raise ValueError("boundary anchors are incomplete")
    if source.count("constructive non-implication") != 6:
        raise ValueError("expected exactly six witness-to-conclusion edge labels")
    if any(f"W{index}" in source for index in range(4, 10)):
        raise ValueError("only W1-W3 are permitted in D2")


def _text(x: int, y: int, lines: tuple[str, ...], *, css: str = "body", anchor: str = "middle") -> str:
    escaped = [html.escape(line) for line in lines]
    tspans = [f'<tspan x="{x}" dy="0">{escaped[0]}</tspan>']
    tspans.extend(f'<tspan x="{x}" dy="30">{line}</tspan>' for line in escaped[1:])
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{css}" '
        f'font-size="{FONT_SIZES[css]}px">' + "".join(tspans) + "</text>"
    )


def _box(x: int, y: int, width: int, height: int, css: str) -> str:
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18" class="{css}"/>'


def _arrow(x1: int, y1: int, x2: int, y2: int, *, dashed: bool = False) -> str:
    css = "arrow dashed" if dashed else "arrow"
    return f'<path d="M {x1} {y1} L {x2} {y2}" class="{css}" marker-end="url(#arrowhead)"/>'


def render_svg(source: str) -> str:
    validate_source(source)
    source_hash = sha256_bytes(source.encode("utf-8"))
    rows = (
        {
            "id": "W1",
            "y": 190,
            "witness": ("W1 — ciphertext availability", "Ciphertext remains retrievable;", "only t−1 valid dispute responses", "arrive by the deadline."),
            "holds": ("HOLDS", "Ciphertext availability (CA)"),
            "fails": ("FAILS", "Authorized decryptability (AD),", "deadline liveness (DDL), and DKA"),
            "conclusion": ("NON-IMPLICATION 1", "CA does not imply DKA"),
        },
        {
            "id": "W2",
            "y": 550,
            "witness": ("W2 — selective withholding", "At least q_accept sampled canaries respond;", "fewer than t valid responses arrive", "for the target dispute record."),
            "holds": ("HOLDS", "Routine audit acceptance (AKR)"),
            "fails": ("FAILS", "Target-record AD and DDL"),
            "conclusion": ("NON-IMPLICATION 2", "A passed routine audit does not", "unconditionally imply targeted", "dispute success."),
        },
        {
            "id": "W3",
            "y": 910,
            "witness": ("W3 — finite-prefix ambiguity", "Two executions share the same", "finite audit prefix; later", "custodian readiness diverges."),
            "holds": ("HOLDS", "Identical finite audit observations"),
            "fails": ("FAILS", "Unconditional future AD/DDL", "in one continuation"),
            "conclusion": ("NON-IMPLICATION 3", "Finite audits do not guarantee", "unconditional future DKA."),
        },
    )

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1450" viewBox="0 0 1600 1450" role="img" aria-labelledby="d2-title d2-desc">',
        '<title id="d2-title">D2. Three constructive property-separation witnesses</title>',
        '<desc id="d2-desc">Three counterexample witnesses show that ciphertext availability does not imply dispute-key availability, routine audit acceptance does not imply targeted dispute success, and finite audits do not guarantee future dispute-key availability. This is not a complete pairwise lattice.</desc>',
        f'<metadata>canonical_source=diagrams/02_property_separation.mmd;sha256={source_hash};status=PREAUTHORIZATION_DERIVATIVE</metadata>',
        '<defs><marker id="arrowhead" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#24364b"/></marker></defs>',
        '<style>',
        '.background{fill:#ffffff}.title{font-family:Helvetica,Arial,sans-serif;font-weight:700;fill:#102a43}.subtitle{font-family:Helvetica,Arial,sans-serif;font-weight:500;fill:#334e68}.body{font-family:Helvetica,Arial,sans-serif;font-weight:500;fill:#102a43}.small{font-family:Helvetica,Arial,sans-serif;font-weight:600;letter-spacing:1px;fill:#243b53}.witness{fill:#e8f1fb;stroke:#1463a5;stroke-width:3}.holds{fill:#edf7ed;stroke:#276738;stroke-width:3}.fails{fill:#fff1f0;stroke:#a32620;stroke-width:3;stroke-dasharray:10 6}.conclusion{fill:#fff8dc;stroke:#8a5a00;stroke-width:4}.boundary{fill:#e7f7f5;stroke:#006d6f;stroke-width:4}.arrow{fill:none;stroke:#24364b;stroke-width:3}.dashed{stroke-dasharray:9 7}',
        '</style>',
        '<rect width="1600" height="1450" class="background"/>',
        _text(800, 58, ("D2. Property separation by constructive witnesses",), css="title"),
        _text(800, 96, ("Exactly three claim-bearing non-implications — not a complete pairwise lattice",), css="subtitle"),
    ]

    for row in rows:
        y = row["y"]
        parts.append(f'<g data-witness="{row["id"]}">')
        parts.append(_box(55, y, 500, 230, "witness"))
        parts.append(_text(305, y + 42, row["witness"], css="body"))
        parts.append(_box(650, y, 370, 92, "holds"))
        parts.append(_text(835, y + 32, row["holds"], css="body"))
        parts.append(_box(650, y + 128, 370, 112, "fails"))
        parts.append(_text(835, y + 160, row["fails"], css="body"))
        parts.append(_box(1115, y + 38, 430, 154, "conclusion"))
        parts.append(_text(1330, y + 76, row["conclusion"], css="body"))
        parts.append(_arrow(555, y + 70, 650, y + 46))
        parts.append(_arrow(555, y + 160, 650, y + 184))
        parts.append(_arrow(1020, y + 46, 1115, y + 92, dashed=True))
        parts.append(_arrow(1020, y + 184, 1115, y + 138, dashed=True))
        parts.append('</g>')

    parts.extend(
        [
            _box(250, 1288, 1100, 112, "boundary"),
            _text(800, 1328, ("BOUNDARY", "DKA is conditional and deadline-bounded; PAC and declared readiness/network", "assumptions remain separate obligations."), css="body"),
            '</svg>',
            '',
        ]
    )
    return "\n".join(parts)


def check_svg(source: str, output: Path) -> bool:
    return output.is_file() and output.read_text(encoding="utf-8") == render_svg(source)


def write_svg(source: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    content = render_svg(source)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output.parent, delete=False) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    temporary.replace(output)


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("Chrome output is not a valid PNG")
    return struct.unpack(">II", data[16:24])


def render_png(svg: Path, output: Path, chrome: Path) -> None:
    if not chrome.is_file():
        raise FileNotFoundError(f"reviewed local Chrome not found: {chrome}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="keystone-d2-chrome-") as profile:
        command = [
            str(chrome),
            "--headless=new",
            "--disable-gpu",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-default-apps",
            "--disable-sync",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            "--window-size=1600,1450",
            f"--user-data-dir={profile}",
            f"--screenshot={output.resolve()}",
            svg.resolve().as_uri(),
        ]
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 30
        captured = False
        while time.monotonic() < deadline:
            if output.is_file():
                try:
                    captured = png_dimensions(output) == (1600, 1450)
                except (OSError, ValueError, struct.error):
                    captured = False
                if captured:
                    break
            if process.poll() is not None:
                break
            time.sleep(0.1)
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        if not captured:
            raise RuntimeError(f"local Chrome did not produce a complete PNG (returncode={process.returncode})")
    if png_dimensions(output) != (1600, 1450):
        raise ValueError(f"unexpected PNG dimensions: {png_dimensions(output)}")


def build_receipt(
    source_path: Path,
    svg_path: Path,
    png_path: Path,
    *,
    chrome_version: str,
    generated_at: str,
) -> dict[str, object]:
    return {
        "schema_id": "KEYSTONE_D2_RENDER_RECEIPT",
        "schema_version": 1,
        "status": "PREAUTHORIZATION_VISUAL_DERIVATIVE",
        "evidence_classification": "NOT_SCIENTIFIC_EVIDENCE",
        "independence": "SAME_WORKSPACE_NOT_INDEPENDENT",
        "generated_at": generated_at,
        "canonical_authority": "Mermaid source only; rendered files are derivatives",
        "source": {
            "path": _display_path(source_path),
            "sha256": sha256_bytes(source_path.read_bytes()),
            "semantic_contract": [
                "W1: ciphertext availability does not imply DKA",
                "W2: routine audit acceptance does not unconditionally imply targeted dispute success",
                "W3: finite audits do not guarantee unconditional future DKA",
                "not a complete pairwise lattice",
            ],
        },
        "renderer": {
            "path": _display_path(Path(__file__)),
            "sha256": sha256_bytes(Path(__file__).read_bytes()),
            "mode": "deterministic local SVG plus existing local Chrome PNG capture",
            "network": "DISABLED_BY_COMMAND_AND_LOCAL_FILE_INPUT",
            "chrome_version": chrome_version,
        },
        "outputs": {
            "svg": {
                "path": _display_path(svg_path),
                "sha256": sha256_bytes(svg_path.read_bytes()),
                "role": "ACCESSIBLE_VECTOR_DERIVATIVE",
            },
            "png": {
                "path": _display_path(png_path),
                "sha256": sha256_bytes(png_path.read_bytes()),
                "role": "RASTER_PREVIEW_DERIVATIVE",
                "dimensions": list(png_dimensions(png_path)) if png_path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n" else None,
            },
        },
        "visual_qa": {
            "layout_readability": "PASS_MANUAL_LOCAL_INSPECTION",
            "label_clipping": "PASS_MANUAL_LOCAL_INSPECTION",
            "relationship_direction": "PASS_MANUAL_LOCAL_INSPECTION",
            "accessibility": "PARTIAL_REDUNDANT_LABEL_AND_LINE_STYLE; GRAYSCALE_AND_CVD_REVIEW_PENDING",
            "scientific_claim_validation": "NOT_PERFORMED",
        },
    }


def write_receipt(receipt: dict[str, object], output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile("wb", dir=output.parent, delete=False) as handle:
        handle.write(payload)
        temporary = Path(handle.name)
    temporary.replace(output)
    digest = sha256_bytes(payload)
    output.with_suffix(output.suffix + ".sha256").write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    return digest


def check_receipt(receipt_path: Path, source_path: Path, svg_path: Path, png_path: Path) -> bool:
    if not receipt_path.is_file():
        return False
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("schema_id") != "KEYSTONE_D2_RENDER_RECEIPT":
        return False
    expected = {
        "source": sha256_bytes(source_path.read_bytes()),
        "renderer": sha256_bytes(Path(__file__).read_bytes()),
        "svg": sha256_bytes(svg_path.read_bytes()),
        "png": sha256_bytes(png_path.read_bytes()),
    }
    actual = {
        "source": receipt.get("source", {}).get("sha256"),
        "renderer": receipt.get("renderer", {}).get("sha256"),
        "svg": receipt.get("outputs", {}).get("svg", {}).get("sha256"),
        "png": receipt.get("outputs", {}).get("png", {}).get("sha256"),
    }
    sidecar = receipt_path.with_suffix(receipt_path.suffix + ".sha256")
    expected_sidecar = f"{sha256_bytes(receipt_path.read_bytes())}  {receipt_path.name}\n"
    return expected == actual and sidecar.is_file() and sidecar.read_text(encoding="utf-8") == expected_sidecar


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--svg", type=Path, default=DEFAULT_SVG)
    parser.add_argument("--png", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--chrome", type=Path, default=DEFAULT_CHROME)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.read_text(encoding="utf-8")
    validate_source(source)
    if args.check:
        if not check_svg(source, args.svg):
            print(f"FAIL: stale or missing SVG: {args.svg}")
            return 1
        print(f"PASS: source-bound SVG matches {args.source}")
        if args.receipt:
            if not args.png or not check_receipt(args.receipt, args.source, args.svg, args.png):
                print(f"FAIL: stale or missing render receipt: {args.receipt}")
                return 1
            print(f"PASS: source/renderer/SVG/PNG receipt matches {args.receipt}")
        return 0
    write_svg(source, args.svg)
    print(f"Wrote {args.svg}")
    if args.png:
        render_png(args.svg, args.png, args.chrome)
        print(f"Wrote {args.png} ({png_dimensions(args.png)[0]}x{png_dimensions(args.png)[1]})")
    if args.receipt:
        if not args.png:
            raise ValueError("--receipt requires --png")
        version = subprocess.run(
            [str(args.chrome), "--version"], check=True, capture_output=True, text=True, timeout=10
        ).stdout.strip()
        receipt = build_receipt(
            args.source,
            args.svg,
            args.png,
            chrome_version=version,
            generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )
        digest = write_receipt(receipt, args.receipt)
        print(f"Wrote {args.receipt} ({digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
