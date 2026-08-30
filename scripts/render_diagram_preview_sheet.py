#!/usr/bin/env python3
"""Build a deterministic, non-evidentiary D1-D8 diagram contact sheet.

The eight existing PNG derivatives are the only visual inputs.  Their fixed
numeric order and hashes are recorded in a receipt.  This convenience preview
does not reinterpret diagram semantics and is not scientific evidence or an
independent verification artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple

from PIL import Image, ImageDraw, ImageFont, ImageOps, PngImagePlugin, __version__ as PILLOW_VERSION


ROOT = Path(__file__).resolve().parents[1]
RENDERER_PATH = Path(__file__).resolve()
DIAGRAMS = ROOT / "diagrams"
INPUTS = tuple(
    DIAGRAMS / name
    for name in (
        "01_system_architecture.png",
        "02_property_separation.png",
        "03_audit_sequence.png",
        "04_dispute_sequence.png",
        "05_state_machines.png",
        "06_threat_model.png",
        "07_sampling_domains.png",
        "08_experiment_pipeline.png",
    )
)
LABELS = tuple(f"D{index}" for index in range(1, 9))
DEFAULT_OUTPUT = DIAGRAMS / "preview_sheet.png"
DEFAULT_RECEIPT = DIAGRAMS / "preview_sheet.render.json"

SHEET_SIZE = (2400, 3400)
CELL_WIDTH = 1120
CELL_HEIGHT = 750
MARGIN_X = 60
TOP = 150
GAP_X = 40
GAP_Y = 40

STATUS = "PREAUTHORIZATION_VISUAL_DERIVATIVE"
EVIDENCE_CLASSIFICATION = "NOT_SCIENTIFIC_EVIDENCE"
INDEPENDENCE = "SAME_WORKSPACE_NOT_INDEPENDENT"


class Cell(NamedTuple):
    label: str
    box: tuple[int, int, int, int]
    label_box: tuple[int, int, int, int]
    image_box: tuple[int, int, int, int]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def _font(size: int, *, bold: bool = False):
    # Pillow's embedded font avoids a dependency on an unrecorded system font.
    # `bold` is expressed by a wider stroke below because the embedded face has
    # one weight only.
    del bold
    return ImageFont.load_default(size=size)


def layout_cells() -> tuple[Cell, ...]:
    cells: list[Cell] = []
    for index, label in enumerate(LABELS):
        row, column = divmod(index, 2)
        left = MARGIN_X + column * (CELL_WIDTH + GAP_X)
        top = TOP + row * (CELL_HEIGHT + GAP_Y)
        box = (left, top, left + CELL_WIDTH, top + CELL_HEIGHT)
        label_box = (left + 20, top + 8, left + CELL_WIDTH - 20, top + 74)
        image_box = (left + 24, top + 82, left + CELL_WIDTH - 24, top + CELL_HEIGHT - 24)
        cells.append(Cell(label, box, label_box, image_box))
    return tuple(cells)


def _validate_inputs(inputs: tuple[Path, ...]) -> None:
    if len(inputs) != 8:
        raise ValueError("preview sheet requires exactly eight diagram inputs")
    if tuple(path.name for path in inputs) != tuple(path.name for path in INPUTS):
        raise ValueError("diagram inputs must use the fixed D1-D8 order")
    for path in inputs:
        if not path.is_file():
            raise ValueError(f"missing input: {path}")


def _open_flattened(path: Path) -> Image.Image:
    try:
        with Image.open(path) as source:
            source.load()
            rgba = source.convert("RGBA")
    except (OSError, ValueError) as exc:
        raise ValueError(f"invalid PNG input: {path}") from exc
    background = Image.new("RGBA", rgba.size, "white")
    return Image.alpha_composite(background, rgba).convert("RGB")


def render_sheet(inputs: tuple[Path, ...]) -> bytes:
    _validate_inputs(inputs)
    sheet = Image.new("RGB", SHEET_SIZE, "white")
    draw = ImageDraw.Draw(sheet)
    title_font = _font(56, bold=True)
    label_font = _font(44, bold=True)
    footer_font = _font(28)

    title = "KEYSTONE MPP - D1-D8 diagram preview"
    draw.text(
        (SHEET_SIZE[0] // 2, 28),
        title,
        anchor="ma",
        font=title_font,
        fill="#102a43",
        stroke_width=1,
        stroke_fill="#102a43",
    )

    for path, cell in zip(inputs, layout_cells(), strict=True):
        draw.rounded_rectangle(cell.box, radius=18, fill="#f7fafc", outline="#627d98", width=3)
        draw.text(
            (cell.label_box[0] + 8, cell.label_box[1] + 3),
            cell.label,
            font=label_font,
            fill="#102a43",
            stroke_width=1,
            stroke_fill="#102a43",
        )
        image = _open_flattened(path)
        max_size = (
            cell.image_box[2] - cell.image_box[0],
            cell.image_box[3] - cell.image_box[1],
        )
        fitted = ImageOps.contain(image, max_size, method=Image.Resampling.LANCZOS)
        paste_x = cell.image_box[0] + (max_size[0] - fitted.width) // 2
        paste_y = cell.image_box[1] + (max_size[1] - fitted.height) // 2
        sheet.paste(fitted, (paste_x, paste_y))
        draw.rectangle(
            (paste_x - 1, paste_y - 1, paste_x + fitted.width, paste_y + fitted.height),
            outline="#c5d2df",
            width=2,
        )

    footer = "Preauthorization visual derivative - not scientific evidence - same workspace, not independent"
    draw.text(
        (SHEET_SIZE[0] // 2, 3330),
        footer,
        anchor="ma",
        font=footer_font,
        fill="#334e68",
    )

    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Title", title)
    metadata.add_text("DiagramOrder", ",".join(LABELS))
    metadata.add_text("Status", STATUS)
    metadata.add_text("EvidenceClassification", EVIDENCE_CLASSIFICATION)
    metadata.add_text("Independence", INDEPENDENCE)
    output = io.BytesIO()
    sheet.save(output, format="PNG", pnginfo=metadata, optimize=False, compress_level=9)
    return output.getvalue()


def _png_dimensions(path: Path) -> tuple[int, int]:
    try:
        with Image.open(path) as image:
            image.load()
            return image.size
    except (OSError, ValueError) as exc:
        raise ValueError(f"invalid preview PNG: {path}") from exc


def build_receipt(
    inputs: tuple[Path, ...],
    output: Path,
    *,
    generated_at: str,
) -> dict[str, object]:
    _validate_inputs(inputs)
    if not output.is_file():
        raise ValueError(f"missing output: {output}")
    dimensions = _png_dimensions(output)
    if dimensions != SHEET_SIZE:
        raise ValueError(f"preview dimensions mismatch: expected {SHEET_SIZE}, got {dimensions}")
    return {
        "schema_id": "KEYSTONE_DIAGRAM_PREVIEW_SHEET_RENDER_RECEIPT",
        "schema_version": 1,
        "generated_at": generated_at,
        "status": STATUS,
        "evidence_classification": EVIDENCE_CLASSIFICATION,
        "independence": INDEPENDENCE,
        "diagram_order": list(LABELS),
        "inputs": [
            {
                "label": label,
                "path": _display_path(path),
                "sha256": sha256_bytes(path.read_bytes()),
            }
            for label, path in zip(LABELS, inputs, strict=True)
        ],
        "renderer": {
            "path": _display_path(RENDERER_PATH),
            "sha256": sha256_bytes(RENDERER_PATH.read_bytes()),
            "pillow_version": PILLOW_VERSION,
        },
        "output": {
            "path": _display_path(output),
            "sha256": sha256_bytes(output.read_bytes()),
            "width_px": dimensions[0],
            "height_px": dimensions[1],
        },
    }


def write_receipt(receipt: dict[str, object], receipt_path: Path) -> None:
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    receipt_path.write_bytes(data)
    sidecar = receipt_path.with_suffix(receipt_path.suffix + ".sha256")
    sidecar.write_text(f"{sha256_bytes(data)}  {receipt_path.name}\n", encoding="utf-8")


def check_bundle(inputs: tuple[Path, ...], output: Path, receipt_path: Path) -> bool:
    sidecar = receipt_path.with_suffix(receipt_path.suffix + ".sha256")
    try:
        _validate_inputs(inputs)
        if not output.is_file() or not receipt_path.is_file() or not sidecar.is_file():
            return False
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        expected_sidecar = f"{sha256_bytes(receipt_path.read_bytes())}  {receipt_path.name}\n"
        if sidecar.read_text(encoding="utf-8") != expected_sidecar:
            return False
        actual = build_receipt(
            inputs,
            output,
            generated_at=str(receipt.get("generated_at", "")),
        )
        return receipt == actual and output.read_bytes() == render_sheet(inputs)
    except (OSError, ValueError, json.JSONDecodeError, KeyError, TypeError):
        return False


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify output and receipt without writing")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()

    if args.check:
        return 0 if check_bundle(INPUTS, args.output, args.receipt) else 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(render_sheet(INPUTS))
    write_receipt(build_receipt(INPUTS, args.output, generated_at=_now()), args.receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
