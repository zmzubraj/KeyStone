#!/usr/bin/env python3
"""Build a deterministic preview sheet from the current diagram PNG inventory."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "diagrams" / "preview_sheet.png"
INVENTORY = (
    "01_system_architecture.png",
    "02_property_separation.png",
    "03_audit_sequence.png",
    "04_dispute_sequence.png",
    "05_state_machines.png",
    "06_threat_model.png",
    "07_sampling_domains.png",
    "08_experiment_pipeline.png",
)
SHEET_WIDTH = 1440
MARGIN_X = 36
MARGIN_Y = 20
GUTTER_X = 48
GUTTER_Y = 42
LABEL_GAP = 12
LABEL_HEIGHT = 16


def _font():
    return ImageFont.load_default()


def _inventory_paths() -> tuple[Path, ...]:
    return tuple(ROOT / "diagrams" / name for name in INVENTORY)


def build_preview_sheet(paths: tuple[Path, ...]) -> Image.Image:
    if len(paths) != len(INVENTORY):
        raise ValueError("preview inventory must match the eight canonical diagram PNGs")
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)

    font = _font()
    cell_width = (SHEET_WIDTH - (2 * MARGIN_X) - GUTTER_X) // 2
    prepared_rows: list[tuple[tuple[str, Image.Image], tuple[str, Image.Image], int]] = []

    for row_start in range(0, len(paths), 2):
        row_images = []
        row_height = 0
        for path in paths[row_start:row_start + 2]:
            label = path.name
            with Image.open(path) as image:
                rendered = image.convert("RGB")
                target_height = round(rendered.height * (cell_width / rendered.width))
                scaled = rendered.resize((cell_width, target_height), Image.Resampling.LANCZOS)
            row_images.append((label, scaled))
            row_height = max(row_height, scaled.height)
        prepared_rows.append((row_images[0], row_images[1], row_height))

    sheet_height = (
        (2 * MARGIN_Y)
        + sum(row_height + LABEL_HEIGHT + LABEL_GAP for _, _, row_height in prepared_rows)
        + (GUTTER_Y * (len(prepared_rows) - 1))
    )
    sheet = Image.new("RGB", (SHEET_WIDTH, sheet_height), "white")
    draw = ImageDraw.Draw(sheet)

    top = MARGIN_Y
    for left_item, right_item, row_height in prepared_rows:
        for column, (label, image) in enumerate((left_item, right_item)):
            left = MARGIN_X + column * (cell_width + GUTTER_X)
            draw.text((left, top), label, fill="black", font=font)
            image_top = top + LABEL_HEIGHT + LABEL_GAP
            centered_left = left + (cell_width - image.width) // 2
            sheet.paste(image, (centered_left, image_top))
        top += LABEL_HEIGHT + LABEL_GAP + row_height + GUTTER_Y
    return sheet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    image = build_preview_sheet(_inventory_paths())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, format="PNG")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
