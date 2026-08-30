#!/usr/bin/env python3
"""Deterministic local visual-QA proxy for the canonical KEYSTONE assets."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
import math

from PIL import Image, UnidentifiedImageError


SCHEMA_VERSION = "1.0"
TOOL_VERSION = "1.0"
SVG_PATHS = (
    ("F1", "prototype/results/figures/figure_1_theoretical_detection_bound.svg"),
    ("F2", "prototype/results/figures/figure_2_iid_failure_sweep.svg"),
    ("F3", "prototype/results/figures/figure_3_domain_diversity.svg"),
    ("F4", "prototype/results/figures/figure_4_selective_withholding_gap.svg"),
    ("F5", "prototype/results/figures/figure_5_sampling_strategy.svg"),
    ("D1", "diagrams/01_system_architecture.svg"),
    ("D2", "diagrams/02_property_separation.svg"),
    ("D3", "diagrams/03_audit_sequence.svg"),
    ("D4", "diagrams/04_dispute_sequence.svg"),
    ("D5", "diagrams/05_state_machines.svg"),
    ("D6", "diagrams/06_threat_model.svg"),
    ("D7", "diagrams/07_sampling_domains.svg"),
    ("D8", "diagrams/08_experiment_pipeline.svg"),
)


def build_inventory():
    return [
        {"code": code, "svg": relative, "png": str(Path(relative).with_suffix(".png"))}
        for code, relative in SVG_PATHS
    ]


def input_problem(path: Path, root: Path):
    if not path.exists() and not path.is_symlink():
        return "missing"
    if path.is_symlink() and not path.exists():
        return "symlink"
    try:
        path.resolve(strict=True).relative_to(root)
    except ValueError:
        return "root_escape"
    except OSError:
        return "unresolvable"
    if path.is_symlink():
        return "symlink"
    if not path.is_file():
        return "not_regular_file"
    return None


DIMENSION_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*(px|pt|mm|cm|in)?\s*$", re.I)
FONT_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*(px|pt)?\s*$", re.I)
COLOR_RE = re.compile(r"^(#[0-9a-fA-F]{3}|#[0-9a-fA-F]{6}|rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\))$")
NAMED_COLORS = {
    "black": "#000000", "silver": "#c0c0c0", "gray": "#808080", "white": "#ffffff",
    "maroon": "#800000", "red": "#ff0000", "purple": "#800080", "fuchsia": "#ff00ff",
    "green": "#008000", "lime": "#00ff00", "olive": "#808000", "yellow": "#ffff00",
    "navy": "#000080", "blue": "#0000ff", "teal": "#008080", "aqua": "#00ffff",
}
GLYPH_HREF_RE = re.compile(r"#(?:DejaVu|Liberation|Arial|Helvetica|Times|STIX|CMR|CMSY|CMMI)")
CVD_MATRICES = {
    "protanopia": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deuteranopia": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritanopia": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dimension(value):
    if value is None:
        raise ValueError("missing dimension")
    match = DIMENSION_RE.fullmatch(value)
    if not match or float(match.group(1)) <= 0:
        raise ValueError("invalid dimension")
    return float(match.group(1))


def physical_points(value):
    match = DIMENSION_RE.fullmatch(value or "")
    if not match:
        return None
    number = float(match.group(1))
    return number * {None: 0.75, "px": 0.75, "pt": 1.0, "mm": 72 / 25.4, "cm": 72 / 2.54, "in": 72}[match.group(2).lower() if match.group(2) else None]


def clean_number(value):
    return int(value) if float(value).is_integer() else round(float(value), 6)


def font_points(value):
    match = FONT_RE.fullmatch(value)
    if not match or float(match.group(1)) <= 0:
        return None
    return float(match.group(1)) * (1 if (match.group(2) or "px").lower() == "pt" else 0.75)


def font_user_units(value):
    match = FONT_RE.fullmatch(value)
    if not match or float(match.group(1)) <= 0:
        return None
    number = float(match.group(1))
    return number * (96 / 72 if (match.group(2) or "px").lower() == "pt" else 1)


def typography_proxy(svg_root, width_text, coordinate_width, geometry_basis):
    uses_viewbox_coordinates = geometry_basis == "viewBox"
    source_key = "source_user_units" if uses_viewbox_coordinates else "source_pt"

    def add_source(method, value):
        measured = font_user_units(value) if uses_viewbox_coordinates else font_points(value)
        if measured is not None:
            sources.append({"method": method, source_key: round(measured, 6)})

    sources = []
    for element in svg_root.iter():
        if "font-size" in element.attrib:
            add_source("attribute", element.attrib["font-size"])
        style = element.attrib.get("style", "")
        for value in re.findall(r"font-size\s*:\s*([^;}]+)", style, re.I):
            add_source("css", value)
        transform = element.attrib.get("transform", "")
        element_id = element.attrib.get("id", "")
        has_glyph_use = any(
            descendant.tag.rsplit("}", 1)[-1] == "use"
            and any(GLYPH_HREF_RE.match(href) for name, href in descendant.attrib.items() if name.rsplit("}", 1)[-1] == "href")
            for descendant in element.iter()
        )
        is_text_group = bool(re.fullmatch(r"text_[A-Za-z0-9_.:-]+", element_id)) or has_glyph_use
        if element.tag.rsplit("}", 1)[-1] == "g" and is_text_group:
            for value in re.findall(r"scale\(\s*([0-9]*\.?[0-9]+)(?:[ ,]+-?[0-9]*\.?[0-9]+)?\s*\)", transform):
                scale = float(value)
                if 0 < scale <= 1:
                    sources.append({"method": "matplotlib_transform", source_key: round(scale * 100, 6)})
        if element.tag.rsplit("}", 1)[-1] == "style" and element.text:
            for value in re.findall(r"font-size\s*:\s*([^;}]+)", element.text, re.I):
                add_source("css", value)
    unique = sorted({(source["method"], source[source_key]) for source in sources})
    sources = [{"method": method, source_key: measurement} for method, measurement in unique]
    width_basis = coordinate_width if uses_viewbox_coordinates else physical_points(width_text)
    measurement_basis = "viewBox_user_coordinates" if uses_viewbox_coordinates else "physical_width_points"
    if not sources or not width_basis:
        return {
            "status": "UNKNOWN", "measurement_basis": measurement_basis, "sources": sources,
            "smallest_source_user_units" if uses_viewbox_coordinates else "smallest_source_pt": None,
            "projected_smallest_pt": None,
        }
    smallest = min(source[source_key] for source in sources)
    projected = {
        "85_mm": round(smallest * ((85 / 25.4 * 72) / width_basis), 6),
        "180_mm": round(smallest * ((180 / 25.4 * 72) / width_basis), 6),
    }
    return {
        "status": "MEASURED_PROXY", "measurement_basis": measurement_basis, "sources": sources,
        "smallest_source_user_units" if uses_viewbox_coordinates else "smallest_source_pt": clean_number(smallest),
        "projected_smallest_pt": projected,
    }


def parse_color(value):
    value = value.strip().lower()
    if value in {
        "none", "currentcolor", "transparent", "inherit", "initial", "unset", "revert",
        "revert-layer", "context-fill", "context-stroke",
    } or value.startswith(("url(", "var(")):
        return None
    if value in NAMED_COLORS:
        return NAMED_COLORS[value]
    if not COLOR_RE.fullmatch(value):
        if value.startswith("#") or value.startswith("rgb("):
            raise ValueError(value)
        return None
    if value.startswith("#"):
        digits = value[1:]
        if len(digits) == 3:
            digits = "".join(char * 2 for char in digits)
        rgb = tuple(int(digits[index:index + 2], 16) for index in (0, 2, 4))
    else:
        rgb = tuple(int(number) for number in re.findall(r"\d+", value))
        if any(number > 255 for number in rgb):
            raise ValueError(value)
    return "#" + "".join(f"{number:02x}" for number in rgb)


def rgb_tuple(color):
    return tuple(int(color[index:index + 2], 16) / 255 for index in (1, 3, 5))


def linearize(channel):
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def encode(channel):
    channel = min(1.0, max(0.0, channel))
    return 12.92 * channel if channel <= 0.0031308 else 1.055 * channel ** (1 / 2.4) - 0.055


def relative_luminance(color):
    red, green, blue = (linearize(value) for value in rgb_tuple(color))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def lab(rgb):
    red, green, blue = (linearize(value) for value in rgb)
    x = (0.4124564 * red + 0.3575761 * green + 0.1804375 * blue) / 0.95047
    y = 0.2126729 * red + 0.7151522 * green + 0.0721750 * blue
    z = (0.0193339 * red + 0.1191920 * green + 0.9503041 * blue) / 1.08883
    def f(value):
        return value ** (1 / 3) if value > 216 / 24389 else (24389 / 27 * value + 16) / 116
    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def delta_e(left, right):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def color_proxy(svg_root):
    found = set()
    for element in svg_root.iter():
        candidates = []
        for name in ("fill", "stroke"):
            if name in element.attrib:
                candidates.append(element.attrib[name])
        for style in [element.attrib.get("style", "")]:
            candidates.extend(re.findall(r"(?:fill|stroke)\s*:\s*([^;}]+)", style, re.I))
        for candidate in candidates:
            parsed = parse_color(candidate)
            if parsed:
                found.add(parsed)
    colors = sorted(found)
    contrast = {color: round(1.05 / (relative_luminance(color) + 0.05), 6) for color in colors}
    labs = {color: lab(rgb_tuple(color)) for color in colors}
    grayscale = []
    cvd = {mode: [] for mode in CVD_MATRICES}
    for index, left in enumerate(colors):
        for right in colors[index + 1:]:
            grayscale.append({"colors": [left, right], "delta_l": round(abs(labs[left][0] - labs[right][0]), 6)})
            for mode, matrix in CVD_MATRICES.items():
                transformed = []
                for color in (left, right):
                    linear = tuple(linearize(value) for value in rgb_tuple(color))
                    result = tuple(sum(row[i] * linear[i] for i in range(3)) for row in matrix)
                    transformed.append(lab(tuple(encode(value) for value in result)))
                cvd[mode].append({"colors": [left, right], "delta_e": round(delta_e(*transformed), 6)})
    return {"literal_colors": colors, "white_contrast": contrast, "grayscale_pairs": grayscale, "cvd_pairs": cvd}


def inspect_pair(item, root, failures, warnings):
    svg_path = root / item["svg"]
    png_path = root / item["png"]
    asset = {
        "code": item["code"],
        "svg": {"path": item["svg"], "sha256": sha256(svg_path)},
        "png": {"path": item["png"], "sha256": sha256(png_path)},
    }
    try:
        tree = ET.parse(svg_path)
        svg_root = tree.getroot()
        width_raw = svg_root.get("width")
        height_raw = svg_root.get("height")
        view_box_text = svg_root.get("viewBox")
        view_box = [float(part) for part in re.split(r"[\s,]+", view_box_text.strip())] if view_box_text else None
        if view_box is not None and (len(view_box) != 4 or view_box[2] <= 0 or view_box[3] <= 0):
            raise ValueError("invalid viewBox")
        explicit_dimensions = DIMENSION_RE.fullmatch(width_raw or "") and DIMENSION_RE.fullmatch(height_raw or "")
        if explicit_dimensions:
            width = dimension(width_raw)
            height = dimension(height_raw)
            geometry_basis = "explicit_dimensions"
        else:
            fallback_token = re.compile(r"^\s*[0-9]+(?:\.[0-9]+)?%\s*$")
            fallback_allowed = all(value is None or fallback_token.fullmatch(value) for value in (width_raw, height_raw))
            if not fallback_allowed or view_box is None:
                raise ValueError("invalid dimensions without a defensible viewBox fallback")
            width, height = view_box[2], view_box[3]
            geometry_basis = "viewBox"
        asset["svg"].update({
            "width": clean_number(width), "height": clean_number(height),
            "width_raw": width_raw, "height_raw": height_raw, "geometry_basis": geometry_basis,
            "viewBox": [clean_number(v) for v in view_box] if view_box else None,
        })
        asset["typography"] = typography_proxy(svg_root, width_raw, width, geometry_basis)
        try:
            asset["colors"] = color_proxy(svg_root)
        except ValueError:
            failures.append({"code": item["code"], "kind": "svg", "path": item["svg"], "reason": "invalid_color"})
            return asset
        typography = asset["typography"]
        if typography["status"] == "UNKNOWN":
            warnings.append({"code": item["code"], "type": "typography_unknown"})
        else:
            for width_label, projected in typography["projected_smallest_pt"].items():
                if projected < 7:
                    warnings.append({"code": item["code"], "type": "small_text", "width": width_label, "projected_pt": projected})
        colors = asset["colors"]
        for color, ratio in colors["white_contrast"].items():
            if ratio < 3:
                warnings.append({"code": item["code"], "type": "low_contrast", "color": color, "ratio": ratio})
        for pair in colors["grayscale_pairs"]:
            if pair["delta_l"] < 10:
                warnings.append({"code": item["code"], "type": "low_grayscale_separation", **pair})
        for mode, pairs in colors["cvd_pairs"].items():
            for pair in pairs:
                if pair["delta_e"] < 10:
                    warnings.append({"code": item["code"], "type": "cvd_collision", "mode": mode, **pair})
    except ET.ParseError:
        failures.append({"code": item["code"], "kind": "svg", "path": item["svg"], "reason": "malformed_xml"})
        return asset
    except (ValueError, TypeError):
        failures.append({"code": item["code"], "kind": "svg", "path": item["svg"], "reason": "invalid_dimensions"})
        return asset
    try:
        with Image.open(png_path) as image:
            image.verify()
        with Image.open(png_path) as image:
            png_width, png_height = image.size
            mode = image.mode
            has_alpha = "A" in image.getbands() or "transparency" in image.info
        asset["png"].update({
            "width_px": png_width, "height_px": png_height,
            "mode": mode, "has_alpha": has_alpha,
        })
    except (UnidentifiedImageError, OSError, ValueError):
        failures.append({"code": item["code"], "kind": "png", "path": item["png"], "reason": "unreadable_png"})
        return asset
    svg_ratio = (view_box[2] / view_box[3]) if view_box else (width / height)
    png_ratio = png_width / png_height
    agrees = abs(png_width - png_height * svg_ratio) <= 1.0
    asset["aspect_ratio_agrees"] = agrees
    if not agrees:
        failures.append({"code": item["code"], "kind": "pair", "path": item["svg"], "reason": "aspect_ratio_mismatch"})
    asset["effective_raster_ppi"] = {
        "85_mm": round(png_width / (85 / 25.4), 6),
        "180_mm": round(png_width / (180 / 25.4), 6),
    }
    return asset


def resolve_report_path(root, requested):
    report = requested if requested.is_absolute() else root / requested
    if report.is_symlink():
        raise ValueError("report path must not be a symlink")
    try:
        report.resolve(strict=False).relative_to(root)
    except ValueError as exc:
        raise ValueError("report path must remain within project root") from exc
    if report.exists() and not report.is_file():
        raise ValueError("report path conflicts with a non-regular file")
    if not report.parent.exists() or not report.parent.is_dir() or report.parent.is_symlink():
        raise ValueError("report parent must be an existing non-symlink directory")
    return report


def atomic_write_json(report, payload):
    content = json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(prefix=".visual-qa-", suffix=".tmp", dir=report.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, report)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--fail-on", choices=("integrity", "proxy"), default="integrity")
    args = parser.parse_args(argv)
    root = args.project_root.resolve()
    try:
        report = resolve_report_path(root, args.report)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    failures = []
    inventory = build_inventory()
    assets = []
    warnings = []
    valid_items = []
    for item in inventory:
        valid = True
        for kind in ("svg", "png"):
            path = root / item[kind]
            problem = input_problem(path, root)
            if problem:
                failures.append({"code": item["code"], "kind": kind, "path": item[kind], "reason": problem})
                valid = False
        if valid:
            valid_items.append(item)
    for item in valid_items:
        assets.append(inspect_pair(item, root, failures, warnings))
    payload = {
        "tool_version": TOOL_VERSION,
        "schema_version": SCHEMA_VERSION,
        "inventory": inventory,
        "assets": assets,
        "integrity_failures": failures,
        "proxy_warnings": warnings,
        "methodology": {
            "classification": "conservative_engineering_heuristics_not_standards",
            "declared_widths_mm": [85, 180],
            "thresholds": {
                "cvd_delta_e": 10,
                "grayscale_delta_l": 10,
                "minimum_contrast": 3,
                "minimum_projected_font_pt": 7,
                "raster_ppi": 300,
            },
            "typography_projection_bases": {
                "physical_width_points": "Source font sizes are normalized to points and scaled from the declared physical SVG width.",
                "viewBox_user_coordinates": "Source font sizes are SVG user units scaled from the resolved viewBox width to the provisional target width; the percentage viewport is not treated as a physical point width.",
            },
            "notes": [
                "Widths, 300 PPI, 7 pt, 3:1, delta-L 10, and delta-E 10 are provisional screening parameters.",
                "Results are engineering QA proxies, not accessibility certification or venue compliance.",
                "CVD screening uses deterministic severity-100 matrices and CIE76 pairwise distance.",
            ],
        },
        "limitations": [
            "adjacency", "line_thickness", "redundant_encoding", "print_conversion",
            "contextual_semantics", "assistive_technology", "human_review",
            "target_venue_current_rules", "stylesheet_selector_resolution",
        ],
        "summary": {"expected_pairs": 13, "integrity_failure_count": len(failures), "proxy_warning_count": len(warnings)},
    }
    atomic_write_json(report, payload)
    return 1 if failures or (args.fail_on == "proxy" and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
