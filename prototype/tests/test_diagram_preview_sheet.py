from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path

import pytest
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "render_diagram_preview_sheet.py"
EXPECTED_NAMES = tuple(
    f"{index:02d}_{slug}.png"
    for index, slug in enumerate(
        (
            "system_architecture",
            "property_separation",
            "audit_sequence",
            "dispute_sequence",
            "state_machines",
            "threat_model",
            "sampling_domains",
            "experiment_pipeline",
        ),
        start=1,
    )
)


def load_renderer():
    spec = importlib.util.spec_from_file_location("diagram_preview_sheet_renderer", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture_inputs(tmp_path: Path) -> tuple[Path, ...]:
    paths: list[Path] = []
    for index, name in enumerate(EXPECTED_NAMES, start=1):
        path = tmp_path / name
        image = Image.new(
            "RGB",
            (600 + index * 7, 420 + index * 11),
            (235 - index, 240 - index, 245 - index),
        )
        image.save(path, format="PNG")
        paths.append(path)
    return tuple(paths)


def test_inventory_is_exact_numeric_d1_through_d8() -> None:
    renderer = load_renderer()

    assert tuple(path.name for path in renderer.INPUTS) == EXPECTED_NAMES
    assert tuple(renderer.LABELS) == tuple(f"D{index}" for index in range(1, 9))


def test_render_is_deterministic_legibly_labeled_and_machine_classified(tmp_path: Path) -> None:
    renderer = load_renderer()
    inputs = _fixture_inputs(tmp_path)

    first = renderer.render_sheet(inputs)
    second = renderer.render_sheet(inputs)

    assert first == second
    with Image.open(io.BytesIO(first)) as image:
        assert image.mode == "RGB"
        assert image.size == renderer.SHEET_SIZE
        assert image.info["DiagramOrder"] == "D1,D2,D3,D4,D5,D6,D7,D8"
        assert image.info["Status"] == "PREAUTHORIZATION_VISUAL_DERIVATIVE"
        assert image.info["EvidenceClassification"] == "NOT_SCIENTIFIC_EVIDENCE"
        assert image.info["Independence"] == "SAME_WORKSPACE_NOT_INDEPENDENT"
        assert image.info["Title"].isascii()

        # Every label band must contain dark rendered glyph pixels, rather than
        # relying only on metadata to claim the visible D1-D8 labels exist.
        for cell in renderer.layout_cells():
            crop = image.crop(cell.label_box)
            dark_pixels = sum(
                1
                for red, green, blue in crop.get_flattened_data()
                if max(red, green, blue) < 110
            )
            assert dark_pixels >= 20, cell.label


def test_receipt_binds_inputs_renderer_output_dimensions_and_boundaries(tmp_path: Path) -> None:
    renderer = load_renderer()
    inputs = _fixture_inputs(tmp_path)
    output = tmp_path / "preview_sheet.png"
    output.write_bytes(renderer.render_sheet(inputs))

    receipt = renderer.build_receipt(
        inputs,
        output,
        generated_at="2026-08-29T00:00:00Z",
    )

    assert receipt["schema_id"] == "KEYSTONE_DIAGRAM_PREVIEW_SHEET_RENDER_RECEIPT"
    assert receipt["status"] == "PREAUTHORIZATION_VISUAL_DERIVATIVE"
    assert receipt["evidence_classification"] == "NOT_SCIENTIFIC_EVIDENCE"
    assert receipt["independence"] == "SAME_WORKSPACE_NOT_INDEPENDENT"
    assert receipt["diagram_order"] == list(renderer.LABELS)
    assert [row["path"] for row in receipt["inputs"]] == [path.name for path in inputs]
    assert [row["sha256"] for row in receipt["inputs"]] == [
        renderer.sha256_bytes(path.read_bytes()) for path in inputs
    ]
    assert receipt["renderer"]["sha256"] == renderer.sha256_bytes(SCRIPT.read_bytes())
    assert receipt["output"]["sha256"] == renderer.sha256_bytes(output.read_bytes())
    assert receipt["output"]["width_px"] == renderer.SHEET_SIZE[0]
    assert receipt["output"]["height_px"] == renderer.SHEET_SIZE[1]


def test_receipt_sidecar_and_check_fail_closed_on_input_or_output_drift(tmp_path: Path) -> None:
    renderer = load_renderer()
    inputs = _fixture_inputs(tmp_path)
    output = tmp_path / "preview_sheet.png"
    receipt_path = tmp_path / "preview_sheet.render.json"
    output.write_bytes(renderer.render_sheet(inputs))
    renderer.write_receipt(
        renderer.build_receipt(inputs, output, generated_at="2026-08-29T00:00:00Z"),
        receipt_path,
    )

    assert renderer.check_bundle(inputs, output, receipt_path) is True
    sidecar = receipt_path.with_suffix(receipt_path.suffix + ".sha256")
    assert sidecar.read_text(encoding="utf-8") == (
        f"{renderer.sha256_bytes(receipt_path.read_bytes())}  {receipt_path.name}\n"
    )

    inputs[2].write_bytes(inputs[2].read_bytes() + b"drift")
    assert renderer.check_bundle(inputs, output, receipt_path) is False

    inputs = _fixture_inputs(tmp_path)
    output.write_bytes(output.read_bytes() + b"drift")
    assert renderer.check_bundle(inputs, output, receipt_path) is False


def test_missing_or_misordered_inputs_are_rejected(tmp_path: Path) -> None:
    renderer = load_renderer()
    inputs = _fixture_inputs(tmp_path)

    with pytest.raises(ValueError, match="exactly eight"):
        renderer.render_sheet(inputs[:-1])
    with pytest.raises(ValueError, match="fixed D1-D8 order"):
        renderer.render_sheet((inputs[1], inputs[0], *inputs[2:]))

    inputs[4].unlink()
    with pytest.raises(ValueError, match="missing input"):
        renderer.render_sheet(inputs)
