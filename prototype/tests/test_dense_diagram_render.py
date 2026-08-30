from __future__ import annotations

import importlib.util
import json
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "render_dense_diagrams.py"
EXPECTED_CODES = ("D1", "D5", "D6", "D7", "D8")


def load_renderer():
    spec = importlib.util.spec_from_file_location("dense_diagram_renderer", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _png(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0dIHDR" + struct.pack(">II", width, height)


def test_inventory_is_exact_and_canonical_sources_validate() -> None:
    renderer = load_renderer()

    assert tuple(renderer.SPECS) == EXPECTED_CODES
    for code, spec in renderer.SPECS.items():
        assert spec.source == ROOT / "diagrams" / f"{int(code[1:]):02d}_{spec.slug}.mmd"
        source = spec.source.read_text(encoding="utf-8")
        renderer.validate_source(spec, source)
        with pytest.raises(ValueError, match="semantic anchor|source drift"):
            renderer.validate_source(spec, source.replace(spec.semantic_tokens[0], "DRIFT", 1))


def test_svg_is_deterministic_accessible_source_bound_and_measurable() -> None:
    renderer = load_renderer()

    for code, spec in renderer.SPECS.items():
        source = spec.source.read_text(encoding="utf-8")
        first = renderer.render_svg(spec, source)
        second = renderer.render_svg(spec, source)
        assert first == second
        root = ET.fromstring(first)
        assert root.attrib["role"] == "img"
        assert root.attrib["aria-labelledby"] == f"{code.lower()}-title {code.lower()}-desc"
        assert root.find("{http://www.w3.org/2000/svg}title") is not None
        assert root.find("{http://www.w3.org/2000/svg}desc") is not None
        metadata = root.find("{http://www.w3.org/2000/svg}metadata")
        assert metadata is not None and spec.source_sha256 in (metadata.text or "")
        text_nodes = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "text"]
        assert text_nodes and all("font-size" in node.attrib for node in text_nodes)
        body_sizes = [
            float(node.attrib["font-size"].removesuffix("px"))
            for node in text_nodes
            if "body" in node.attrib.get("class", "").split()
        ]
        assert body_sizes
        viewbox_width = float(root.attrib["viewBox"].split()[2])
        projected = min(body_sizes) * ((180 / 25.4 * 72) / viewbox_width)
        assert projected >= 7.0, (code, projected)
        assert "stroke-dasharray" in first
        for token in spec.output_tokens:
            assert token in first

    d1 = renderer.SPECS["D1"]
    d1_svg = renderer.render_svg(d1, d1.source.read_text(encoding="utf-8"))
    assert 'aria-label="Threshold Custodian Committee"' in d1_svg
    assert "Threshold Custodian Committee" in d1_svg
    assert '<polygon fill="#555555"' in d1_svg
    assert 'aria-label="AEAD&#45;encrypt record with Kᵣ"' in d1_svg


def test_png_capture_uses_declared_dimensions_and_terminates(monkeypatch, tmp_path: Path) -> None:
    renderer = load_renderer()
    spec = renderer.SPECS["D1"]
    chrome = tmp_path / "chrome"
    svg = tmp_path / "diagram.svg"
    png = tmp_path / "diagram.png"
    chrome.write_text("fixture", encoding="utf-8")
    svg.write_text(renderer.render_svg(spec, spec.source.read_text(encoding="utf-8")), encoding="utf-8")

    class FakeChrome:
        instance = None

        def __init__(self, command, **kwargs):
            del kwargs
            self.command = command
            self.terminated = False
            self.killed = False
            self.returncode = None
            FakeChrome.instance = self
            screenshot = next(item.split("=", 1)[1] for item in command if item.startswith("--screenshot="))
            Path(screenshot).write_bytes(_png(spec.width, spec.height))

        def poll(self):
            return self.returncode

        def terminate(self):
            self.terminated = True
            self.returncode = 0

        def kill(self):
            self.killed = True
            self.returncode = -9

        def wait(self, timeout=None):
            del timeout
            return self.returncode

    monkeypatch.setattr(renderer.subprocess, "Popen", FakeChrome)
    monkeypatch.setattr(renderer.time, "sleep", lambda _: None)

    renderer.render_png(svg, png, chrome, spec.width, spec.height)

    assert renderer.png_dimensions(png) == (spec.width, spec.height)
    assert f"--window-size={spec.width},{spec.height}" in FakeChrome.instance.command
    assert "--disable-background-networking" in FakeChrome.instance.command
    assert FakeChrome.instance.terminated is True
    assert FakeChrome.instance.killed is False


def test_receipt_hashes_every_input_output_and_check_fails_closed(tmp_path: Path) -> None:
    renderer = load_renderer()
    sources = {}
    outputs = {}
    for code, spec in renderer.SPECS.items():
        source_path = tmp_path / spec.source.name
        svg_path = tmp_path / spec.svg.name
        png_path = tmp_path / spec.png.name
        source_path.write_bytes(spec.source.read_bytes())
        svg_path.write_text(renderer.render_svg(spec, source_path.read_text(encoding="utf-8")), encoding="utf-8")
        png_path.write_bytes(_png(spec.width, spec.height))
        sources[code] = source_path
        outputs[code] = (svg_path, png_path)
    receipt_path = tmp_path / "dense_diagrams.render.json"

    receipt = renderer.build_receipt(
        sources,
        outputs,
        chrome_version="Google Chrome test",
        generated_at="2026-08-29T00:00:00Z",
    )
    renderer.write_receipt(receipt, receipt_path)

    assert receipt["status"] == "PREAUTHORIZATION_VISUAL_DERIVATIVE"
    assert receipt["evidence_classification"] == "NOT_SCIENTIFIC_EVIDENCE"
    assert receipt["independence"] == "SAME_WORKSPACE_NOT_INDEPENDENT"
    assert tuple(receipt["inventory"]) == EXPECTED_CODES
    assert renderer.check_bundle(sources, outputs, receipt_path) is True
    sidecar = receipt_path.with_suffix(receipt_path.suffix + ".sha256")
    assert sidecar.read_text(encoding="utf-8") == (
        f"{renderer.sha256_bytes(receipt_path.read_bytes())}  {receipt_path.name}\n"
    )

    outputs["D7"][0].write_text("<svg>stale</svg>\n", encoding="utf-8")
    assert renderer.check_bundle(sources, outputs, receipt_path) is False


def test_receipt_renderer_hash_detects_renderer_drift(tmp_path: Path, monkeypatch) -> None:
    renderer = load_renderer()
    sources = {}
    outputs = {}
    for code, spec in renderer.SPECS.items():
        source_path = tmp_path / spec.source.name
        svg_path = tmp_path / spec.svg.name
        png_path = tmp_path / spec.png.name
        source_path.write_bytes(spec.source.read_bytes())
        svg_path.write_text(renderer.render_svg(spec, source_path.read_text(encoding="utf-8")), encoding="utf-8")
        png_path.write_bytes(_png(spec.width, spec.height))
        sources[code] = source_path
        outputs[code] = (svg_path, png_path)
    receipt_path = tmp_path / "dense_diagrams.render.json"
    renderer.write_receipt(
        renderer.build_receipt(sources, outputs, chrome_version="test", generated_at="2026-08-29T00:00:00Z"),
        receipt_path,
    )
    original = renderer.RENDERER_PATH
    drifted = tmp_path / "renderer.py"
    drifted.write_bytes(original.read_bytes() + b"\n# drift\n")
    monkeypatch.setattr(renderer, "RENDERER_PATH", drifted)

    assert renderer.check_bundle(sources, outputs, receipt_path) is False
