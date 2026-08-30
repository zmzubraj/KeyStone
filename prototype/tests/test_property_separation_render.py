from __future__ import annotations

import importlib.util
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "render_property_separation_diagram.py"
SOURCE = ROOT / "diagrams" / "02_property_separation.mmd"


def load_renderer():
    spec = importlib.util.spec_from_file_location("property_separation_renderer", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_renderer_requires_exact_three_witnesses_and_boundary() -> None:
    renderer = load_renderer()
    source = SOURCE.read_text(encoding="utf-8")

    renderer.validate_source(source)
    svg = renderer.render_svg(source)

    assert svg.count('data-witness="W') == 3
    assert "CA does not imply DKA" in svg
    assert "routine audit" in svg
    assert "Finite audits do not guarantee" in svg
    assert "not a complete pairwise lattice" in svg
    assert "role=\"img\"" in svg
    assert "<title" in svg and "<desc" in svg


def test_renderer_exposes_measurable_final_size_typography() -> None:
    renderer = load_renderer()
    svg = renderer.render_svg(SOURCE.read_text(encoding="utf-8"))
    root = ET.fromstring(svg)
    viewbox_width = float(root.attrib["viewBox"].split()[2])
    text_nodes = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "text"]

    assert text_nodes
    assert all("font-size" in node.attrib for node in text_nodes)
    explicit_sizes = [float(node.attrib["font-size"].removesuffix("px")) for node in text_nodes]
    body_sizes = [
        float(node.attrib["font-size"].removesuffix("px"))
        for node in text_nodes
        if "body" in node.attrib.get("class", "").split()
    ]
    assert body_sizes
    assert min(explicit_sizes) == min(body_sizes)
    projected_at_180_mm = min(body_sizes) * ((180 / 25.4 * 72) / viewbox_width)
    assert projected_at_180_mm >= 7.0


def test_renderer_rejects_semantic_source_drift() -> None:
    renderer = load_renderer()
    source = SOURCE.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="W3"):
        renderer.validate_source(source.replace('W3["', 'WX["', 1))


def test_check_mode_detects_stale_svg(tmp_path: Path) -> None:
    renderer = load_renderer()
    source = SOURCE.read_text(encoding="utf-8")
    output = tmp_path / "diagram.svg"
    output.write_text("<svg>stale</svg>\n", encoding="utf-8")

    assert renderer.check_svg(source, output) is False
    output.write_text(renderer.render_svg(source), encoding="utf-8")
    assert renderer.check_svg(source, output) is True


def test_render_receipt_binds_source_renderer_and_derivatives(tmp_path: Path) -> None:
    renderer = load_renderer()
    source_path = tmp_path / "source.mmd"
    svg_path = tmp_path / "diagram.svg"
    png_path = tmp_path / "diagram.png"
    source_path.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
    svg_path.write_text(renderer.render_svg(source_path.read_text(encoding="utf-8")), encoding="utf-8")
    png_path.write_bytes(b"png-derivative-fixture")

    receipt = renderer.build_receipt(
        source_path,
        svg_path,
        png_path,
        chrome_version="Google Chrome test",
        generated_at="2026-08-29T00:00:00Z",
    )

    assert receipt["schema_id"] == "KEYSTONE_D2_RENDER_RECEIPT"
    assert receipt["evidence_classification"] == "NOT_SCIENTIFIC_EVIDENCE"
    assert receipt["independence"] == "SAME_WORKSPACE_NOT_INDEPENDENT"
    assert receipt["source"]["sha256"] == renderer.sha256_bytes(source_path.read_bytes())
    assert receipt["renderer"]["sha256"] == renderer.sha256_bytes(SCRIPT.read_bytes())
    assert receipt["outputs"]["svg"]["sha256"] == renderer.sha256_bytes(svg_path.read_bytes())
    assert receipt["outputs"]["png"]["sha256"] == renderer.sha256_bytes(png_path.read_bytes())


def test_png_capture_terminates_chrome_after_screenshot(monkeypatch, tmp_path: Path) -> None:
    renderer = load_renderer()
    chrome = tmp_path / "chrome"
    svg = tmp_path / "diagram.svg"
    png = tmp_path / "diagram.png"
    chrome.write_text("fixture", encoding="utf-8")
    svg.write_text("<svg/>", encoding="utf-8")

    class FakeChrome:
        instance = None

        def __init__(self, command, **kwargs):
            del kwargs
            self.terminated = False
            self.killed = False
            self.returncode = None
            FakeChrome.instance = self
            screenshot = next(item.split("=", 1)[1] for item in command if item.startswith("--screenshot="))
            Path(screenshot).write_bytes(
                b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0dIHDR" + struct.pack(">II", 1600, 1450)
            )

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

    renderer.render_png(svg, png, chrome)

    assert FakeChrome.instance is not None
    assert FakeChrome.instance.terminated is True
    assert FakeChrome.instance.killed is False
