from __future__ import annotations

import importlib.util
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "render_preview_sheet.py"


def load_module():
    spec = importlib.util.spec_from_file_location("render_preview_sheet", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_preview_sheet_uses_canonical_inventory_and_is_deterministic(tmp_path: Path) -> None:
    module = load_module()
    paths = []
    colors = ("red", "green", "blue", "yellow", "purple", "orange", "gray", "cyan")
    for index, name in enumerate(module.INVENTORY):
        path = tmp_path / name
        Image.new("RGB", (1600, 800 + index * 25), colors[index]).save(path)
        paths.append(path)

    first = module.build_preview_sheet(tuple(paths))
    second = module.build_preview_sheet(tuple(paths))

    assert first.size == second.size
    assert first.mode == "RGB"
    assert first.tobytes() == second.tobytes()
    assert first.size[0] == module.SHEET_WIDTH
    assert first.size[1] > first.size[0]
