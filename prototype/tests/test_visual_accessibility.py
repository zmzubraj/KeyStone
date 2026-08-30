import json
import hashlib
from pathlib import Path
import subprocess
import sys

from PIL import Image


PROJECT = Path(__file__).resolve().parents[2]
SCRIPT = PROJECT / "scripts" / "validate_visual_accessibility.py"
EXPECTED_CODES = ["F1", "F2", "F3", "F4", "F5", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]
SVG_PATHS = {
    "F1": "prototype/results/figures/figure_1_theoretical_detection_bound.svg",
    "F2": "prototype/results/figures/figure_2_iid_failure_sweep.svg",
    "F3": "prototype/results/figures/figure_3_domain_diversity.svg",
    "F4": "prototype/results/figures/figure_4_selective_withholding_gap.svg",
    "F5": "prototype/results/figures/figure_5_sampling_strategy.svg",
    "D1": "diagrams/01_system_architecture.svg",
    "D2": "diagrams/02_property_separation.svg",
    "D3": "diagrams/03_audit_sequence.svg",
    "D4": "diagrams/04_dispute_sequence.svg",
    "D5": "diagrams/05_state_machines.svg",
    "D6": "diagrams/06_threat_model.svg",
    "D7": "diagrams/07_sampling_domains.svg",
    "D8": "diagrams/08_experiment_pipeline.svg",
}


def run_cli(root: Path, report: str = "qa.json", fail_on: str = "integrity"):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--project-root", str(root), "--report", report, "--fail-on", fail_on],
        text=True,
        capture_output=True,
        check=False,
    )


def make_inventory(root: Path, svg_text=None):
    svg_text = svg_text or '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" viewBox="0 0 600 300"><text font-size="10">x</text></svg>'
    for relative in SVG_PATHS.values():
        svg = root / relative
        svg.parent.mkdir(parents=True, exist_ok=True)
        svg.write_text(svg_text, encoding="utf-8")
        Image.new("RGBA", (1200, 600), (255, 255, 255, 255)).save(svg.with_suffix(".png"))


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_inventory_and_missing_inputs_fail_closed(tmp_path):
    result = run_cli(tmp_path)
    assert result.returncode == 1
    report = json.loads((tmp_path / "qa.json").read_text())
    assert [item["code"] for item in report["inventory"]] == EXPECTED_CODES
    assert report["summary"]["expected_pairs"] == 13
    assert report["summary"]["integrity_failure_count"] == 26


def test_symlink_and_non_regular_inputs_are_integrity_failures(tmp_path):
    make_inventory(tmp_path)
    target = tmp_path / SVG_PATHS["F1"]
    target.unlink()
    target.symlink_to(tmp_path / SVG_PATHS["F2"])
    png = (tmp_path / SVG_PATHS["D8"]).with_suffix(".png")
    png.unlink()
    png.mkdir()
    result = run_cli(tmp_path)
    report = json.loads((tmp_path / "qa.json").read_text())
    assert result.returncode == 1
    reasons = {(f["code"], f["reason"]) for f in report["integrity_failures"]}
    assert ("F1", "symlink") in reasons
    assert ("D8", "not_regular_file") in reasons


def test_root_escape_is_rejected_even_when_symlink_target_exists(tmp_path):
    make_inventory(tmp_path)
    outside = tmp_path.parent / "outside.svg"
    outside.write_text('<svg width="1" height="1"/>')
    target = tmp_path / SVG_PATHS["F1"]
    target.unlink()
    target.symlink_to(outside)
    result = run_cli(tmp_path)
    report = json.loads((tmp_path / "qa.json").read_text())
    assert result.returncode == 1
    assert any(f["code"] == "F1" and f["reason"] == "root_escape" for f in report["integrity_failures"])


def test_broken_symlink_is_normalized_as_symlink_failure(tmp_path):
    make_inventory(tmp_path)
    target = tmp_path / SVG_PATHS["F1"]
    target.unlink()
    target.symlink_to(tmp_path / "does-not-exist.svg")
    result = run_cli(tmp_path)
    report = json.loads((tmp_path / "qa.json").read_text())
    assert result.returncode == 1
    failure = next(f for f in report["integrity_failures"] if f["code"] == "F1")
    assert failure["reason"] == "symlink"


def test_geometry_hashes_ppi_and_no_input_mutation(tmp_path):
    make_inventory(tmp_path)
    before = {str(p.relative_to(tmp_path)): sha(p) for p in tmp_path.rglob("*") if p.is_file()}
    result = run_cli(tmp_path)
    assert result.returncode == 0
    report = json.loads((tmp_path / "qa.json").read_text())
    asset = report["assets"][0]
    assert asset["svg"]["width"] == 600
    assert asset["svg"]["height"] == 300
    assert asset["svg"]["viewBox"] == [0, 0, 600, 300]
    assert asset["png"]["width_px"] == 1200
    assert asset["png"]["height_px"] == 600
    assert asset["png"]["mode"] == "RGBA"
    assert asset["png"]["has_alpha"] is True
    assert asset["aspect_ratio_agrees"] is True
    assert asset["effective_raster_ppi"]["85_mm"] == 358.588235
    assert asset["effective_raster_ppi"]["180_mm"] == 169.333333
    assert asset["svg"]["sha256"] == before[SVG_PATHS["F1"]]
    after = {str(p.relative_to(tmp_path)): sha(p) for p in tmp_path.rglob("*") if p.is_file() and p.name != "qa.json"}
    assert after == before


def test_malformed_svg_unreadable_png_and_aspect_mismatch_fail_integrity(tmp_path):
    make_inventory(tmp_path)
    (tmp_path / SVG_PATHS["F1"]).write_text("<svg>", encoding="utf-8")
    (tmp_path / SVG_PATHS["F2"]).with_suffix(".png").write_bytes(b"not png")
    Image.new("RGB", (1200, 500)).save((tmp_path / SVG_PATHS["F3"]).with_suffix(".png"))
    result = run_cli(tmp_path)
    report = json.loads((tmp_path / "qa.json").read_text())
    assert result.returncode == 1
    reasons = {(f["code"], f["reason"]) for f in report["integrity_failures"]}
    assert ("F1", "malformed_xml") in reasons
    assert ("F2", "unreadable_png") in reasons
    assert ("F3", "aspect_ratio_mismatch") in reasons
    by_code = {asset["code"]: asset for asset in report["assets"]}
    assert by_code["F1"]["svg"]["sha256"] == sha(tmp_path / SVG_PATHS["F1"])
    assert by_code["F2"]["png"]["sha256"] == sha((tmp_path / SVG_PATHS["F2"]).with_suffix(".png"))


def test_typography_sources_projection_and_unknown_boundary(tmp_path):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="600pt" height="300pt" viewBox="0 0 600 300">
      <style>.css { font-size: 8px; }</style><text font-size="6pt">small</text>
      <text class="css">css</text><g id="text_1" transform="translate(1 2) scale(0.1 -0.1)"><path d="M0 0"/></g>
      <defs><path transform="scale(0.015625)" d="M0 0"/></defs>
    </svg>'''
    make_inventory(tmp_path, svg)
    result = run_cli(tmp_path)
    report = json.loads((tmp_path / "qa.json").read_text())
    typography = report["assets"][0]["typography"]
    assert result.returncode == 0
    assert typography["status"] == "MEASURED_PROXY"
    assert {s["method"] for s in typography["sources"]} == {"attribute", "css", "matplotlib_transform"}
    assert typography["smallest_source_pt"] == 6
    assert typography["projected_smallest_pt"]["85_mm"] == 2.409449
    assert typography["projected_smallest_pt"]["180_mm"] == 5.102362
    assert any(w["type"] == "small_text" for w in report["proxy_warnings"])

    no_text = '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" viewBox="0 0 600 300"><path d="M0 0"/></svg>'
    (tmp_path / SVG_PATHS["F1"]).write_text(no_text, encoding="utf-8")
    run_cli(tmp_path)
    report = json.loads((tmp_path / "qa.json").read_text())
    assert report["assets"][0]["typography"]["status"] == "UNKNOWN"


def test_scale_only_identified_text_group_is_a_defensible_matplotlib_proxy(tmp_path):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="600pt" height="300pt" viewBox="0 0 600 300">
      <g id="text_42" transform="scale(0.2 -0.2)"><path d="M0 0"/></g>
      <defs><path transform="scale(0.015625)" d="M0 0"/></defs>
    </svg>'''
    make_inventory(tmp_path, svg)
    run_cli(tmp_path)
    report = json.loads((tmp_path / "qa.json").read_text())
    typography = report["assets"][0]["typography"]
    assert typography["status"] == "MEASURED_PROXY"
    assert typography["sources"] == [{"method": "matplotlib_transform", "source_pt": 20}]


def test_anonymous_transform_only_geometry_is_not_inferred_as_typography(tmp_path):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" viewBox="0 0 600 300">
      <g transform="translate(5 6) scale(0.02 -0.02)"><path d="M0 0 L10 10"/></g>
    </svg>'''
    make_inventory(tmp_path, svg)
    run_cli(tmp_path)
    report = json.loads((tmp_path / "qa.json").read_text())
    typography = report["assets"][0]["typography"]
    assert typography["status"] == "UNKNOWN"
    assert not any(w["type"] == "small_text" for w in report["proxy_warnings"])


def test_color_filtering_metrics_and_all_three_cvd_collision_modes(tmp_path):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" viewBox="0 0 600 300">
      <path fill="none" stroke="currentColor" d="M0 0"/><path fill="url(#gradient)" d="M0 0"/>
      <path fill="white" stroke="transparent" d="M0 0"/>
      <path style="fill: #aaaaaa; stroke: rgb(255, 0, 0)" d="M0 0"/>
      <path fill="#fe0000" style="stroke: #777777" d="M0 0"/><path fill="#787878" d="M0 0"/>
    </svg>'''
    make_inventory(tmp_path, svg)
    run_cli(tmp_path)
    report = json.loads((tmp_path / "qa.json").read_text())
    colors = report["assets"][0]["colors"]
    assert colors["literal_colors"] == ["#777777", "#787878", "#aaaaaa", "#fe0000", "#ff0000", "#ffffff"]
    assert colors["white_contrast"]["#aaaaaa"] < 3
    assert any(pair["delta_l"] < 10 for pair in colors["grayscale_pairs"])
    modes = {w["mode"] for w in report["proxy_warnings"] if w["type"] == "cvd_collision"}
    assert modes == {"protanopia", "deuteranopia", "tritanopia"}
    assert any(w["type"] == "low_contrast" for w in report["proxy_warnings"])
    assert any(w["type"] == "low_grayscale_separation" for w in report["proxy_warnings"])


def test_unused_stylesheet_colors_do_not_create_proxy_findings(tmp_path):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" viewBox="0 0 600 300">
      <style>.unused { fill: #aaaaaa; stroke: #ff0000; }</style><path fill="#000000"/>
    </svg>'''
    make_inventory(tmp_path, svg)
    run_cli(tmp_path)
    report = json.loads((tmp_path / "qa.json").read_text())
    assert report["assets"][0]["colors"]["literal_colors"] == ["#000000"]
    assert not any(w["type"] in {"low_contrast", "low_grayscale_separation", "cvd_collision"} for w in report["proxy_warnings"])
    assert "stylesheet_selector_resolution" in report["limitations"]


def test_valid_nonliteral_paint_tokens_are_ignored_not_integrity_failures(tmp_path):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" viewBox="0 0 600 300">
      <path fill="inherit" stroke="context-fill"/><path style="fill: unset; stroke: var(--accent)"/>
    </svg>'''
    make_inventory(tmp_path, svg)
    result = run_cli(tmp_path)
    report = json.loads((tmp_path / "qa.json").read_text())
    assert result.returncode == 0
    assert report["integrity_failures"] == []
    assert report["assets"][0]["colors"]["literal_colors"] == []


def test_deterministic_schema_methodology_limitations_and_exit_policy(tmp_path):
    make_inventory(tmp_path)
    first = run_cli(tmp_path, "one.json")
    second = run_cli(tmp_path, "two.json")
    assert first.returncode == 0
    assert second.returncode == 0
    assert (tmp_path / "one.json").read_bytes() == (tmp_path / "two.json").read_bytes()
    report = json.loads((tmp_path / "one.json").read_text())
    assert report["methodology"]["declared_widths_mm"] == [85, 180]
    assert report["methodology"]["thresholds"] == {
        "cvd_delta_e": 10,
        "grayscale_delta_l": 10,
        "minimum_contrast": 3,
        "minimum_projected_font_pt": 7,
        "raster_ppi": 300,
    }
    assert report["methodology"]["classification"] == "conservative_engineering_heuristics_not_standards"
    for limitation in ("adjacency", "line_thickness", "redundant_encoding", "print_conversion", "contextual_semantics", "assistive_technology", "human_review", "target_venue_current_rules"):
        assert limitation in report["limitations"]
    assert run_cli(tmp_path, "proxy.json", "proxy").returncode == 1


def test_report_must_be_new_or_regular_within_root_and_is_atomic(tmp_path):
    make_inventory(tmp_path)
    outside = tmp_path.parent / "visual-qa-outside.json"
    outside.unlink(missing_ok=True)
    escaped = run_cli(tmp_path, str(outside))
    assert escaped.returncode != 0
    assert not outside.exists()

    target = tmp_path / "linked.json"
    real = tmp_path / "real.json"
    real.write_text("preserve", encoding="utf-8")
    target.symlink_to(real)
    linked = run_cli(tmp_path, "linked.json")
    assert linked.returncode != 0
    assert real.read_text() == "preserve"

    directory = tmp_path / "directory-report"
    directory.mkdir()
    assert run_cli(tmp_path, "directory-report").returncode != 0
    assert not list(tmp_path.glob(".visual-qa-*.tmp"))


def test_invalid_dimensions_and_literal_colors_fail_closed(tmp_path):
    make_inventory(tmp_path)
    (tmp_path / SVG_PATHS["F1"]).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="bad" height="300"/>', encoding="utf-8")
    (tmp_path / SVG_PATHS["F2"]).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300"><path fill="#12"/></svg>', encoding="utf-8")
    result = run_cli(tmp_path)
    report = json.loads((tmp_path / "qa.json").read_text())
    assert result.returncode == 1
    reasons = {(f["code"], f["reason"]) for f in report["integrity_failures"]}
    assert ("F1", "invalid_dimensions") in reasons
    assert ("F2", "invalid_color") in reasons


def test_aspect_agreement_uses_viewbox_and_allows_one_pixel_raster_rounding(tmp_path):
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="637pt" height="708pt" viewBox="0 0 637 707.72"/>'
    make_inventory(tmp_path, svg)
    for relative in SVG_PATHS.values():
        Image.new("RGB", (1593, 1769)).save((tmp_path / relative).with_suffix(".png"))
    result = run_cli(tmp_path)
    report = json.loads((tmp_path / "qa.json").read_text())
    assert result.returncode == 0
    assert all(asset["aspect_ratio_agrees"] for asset in report["assets"])


def test_percentage_dimensions_use_valid_viewbox_geometry_with_recorded_basis(tmp_path):
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 640 360"><text font-size="7.5">label</text></svg>'
    make_inventory(tmp_path, svg)
    for relative in SVG_PATHS.values():
        Image.new("RGB", (1280, 720)).save((tmp_path / relative).with_suffix(".png"))
    result = run_cli(tmp_path)
    report = json.loads((tmp_path / "qa.json").read_text())
    assert result.returncode == 0
    geometry = report["assets"][0]["svg"]
    assert geometry["width_raw"] == "100%"
    assert geometry["height_raw"] == "100%"
    assert geometry["width"] == 640
    assert geometry["height"] == 360
    assert geometry["geometry_basis"] == "viewBox"
    typography = report["assets"][0]["typography"]
    assert typography["status"] == "MEASURED_PROXY"
    assert typography["measurement_basis"] == "viewBox_user_coordinates"
    assert typography["smallest_source_user_units"] == 7.5
    assert typography["projected_smallest_pt"] == {"85_mm": 2.823573, "180_mm": 5.979331}
    assert report["methodology"]["typography_projection_bases"]["viewBox_user_coordinates"].startswith("Source font sizes are SVG user units")
