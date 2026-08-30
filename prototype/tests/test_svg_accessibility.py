from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import shutil

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "annotate_svg_accessibility.py"

EXPECTED_CODES = (
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "D1",
    "D2",
    "D3",
    "D4",
    "D5",
    "D6",
    "D7",
    "D8",
)

EXPECTED_PATHS = (
    "prototype/results/figures/figure_1_theoretical_detection_bound.svg",
    "prototype/results/figures/figure_2_iid_failure_sweep.svg",
    "prototype/results/figures/figure_3_domain_diversity.svg",
    "prototype/results/figures/figure_4_selective_withholding_gap.svg",
    "prototype/results/figures/figure_5_sampling_strategy.svg",
    "diagrams/01_system_architecture.svg",
    "diagrams/02_property_separation.svg",
    "diagrams/03_audit_sequence.svg",
    "diagrams/04_dispute_sequence.svg",
    "diagrams/05_state_machines.svg",
    "diagrams/06_threat_model.svg",
    "diagrams/07_sampling_domains.svg",
    "diagrams/08_experiment_pipeline.svg",
)


def load_module():
    spec = importlib.util.spec_from_file_location("svg_accessibility_annotator", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clone_asset_tree(tmp_path: Path) -> Path:
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    for relative_path in EXPECTED_PATHS:
        source = ROOT / relative_path
        target = sandbox / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return sandbox


def assert_accessibility_metadata(svg_text: str, spec) -> None:
    assert f'role="img"' in svg_text
    assert f'aria-labelledby="{spec.stable_id}-title {spec.stable_id}-desc"' in svg_text
    assert f'<title id="{spec.stable_id}-title">{spec.title}</title>' in svg_text
    assert f'<desc id="{spec.stable_id}-desc">{spec.description}</desc>' in svg_text


def assert_leading_root_metadata_block(svg_text: str, spec) -> None:
    pattern = re.compile(
        re.escape("aria-labelledby")
        + r'="[^"]*">\s*'
        + re.escape(f'<title id="{spec.stable_id}-title">{spec.title}</title>')
        + r"\s*"
        + re.escape(f'<desc id="{spec.stable_id}-desc">{spec.description}</desc>')
        + r"\s*<",
        re.DOTALL,
    )
    assert pattern.search(svg_text) is not None


def strip_expected_accessibility_metadata(svg_text: str, spec) -> str:
    svg_text = svg_text.replace(f' role="img"', "", 1)
    svg_text = svg_text.replace(
        f' aria-labelledby="{spec.stable_id}-title {spec.stable_id}-desc"',
        "",
        1,
    )
    svg_text = svg_text.replace(
        f'\n<title id="{spec.stable_id}-title">{spec.title}</title>',
        "",
        1,
    )
    svg_text = svg_text.replace(
        f'\n<desc id="{spec.stable_id}-desc">{spec.description}</desc>',
        "",
        1,
    )
    return svg_text


def test_inventory_is_exact_and_paths_exist() -> None:
    module = load_module()

    assert tuple(spec.code for spec in module.INVENTORY) == EXPECTED_CODES
    assert tuple(spec.relative_path for spec in module.INVENTORY) == EXPECTED_PATHS
    assert all((ROOT / relative_path).exists() for relative_path in EXPECTED_PATHS)


def test_metadata_injection_is_exact_and_preserves_content(tmp_path: Path) -> None:
    module = load_module()
    sandbox = clone_asset_tree(tmp_path)

    figure_spec = module.INVENTORY_BY_CODE["F1"]
    figure_path = sandbox / figure_spec.relative_path
    figure_original = strip_expected_accessibility_metadata(
        figure_path.read_text(encoding="utf-8"),
        figure_spec,
    )
    figure_updated = module.annotate_svg_text(figure_original, figure_spec)

    assert_accessibility_metadata(figure_updated, figure_spec)
    assert_leading_root_metadata_block(figure_updated, figure_spec)
    assert "<g id=\"figure_1\">" in figure_updated
    assert "<metadata>" in figure_updated
    assert "<path d=\"M 71.509091" in figure_updated

    diagram_spec = module.INVENTORY_BY_CODE["D1"]
    diagram_path = sandbox / diagram_spec.relative_path
    diagram_original = strip_expected_accessibility_metadata(
        diagram_path.read_text(encoding="utf-8"),
        diagram_spec,
    )
    diagram_updated = module.annotate_svg_text(diagram_original, diagram_spec)

    assert_accessibility_metadata(diagram_updated, diagram_spec)
    assert_leading_root_metadata_block(diagram_updated, diagram_spec)
    assert "Threshold Custodian Committee" in diagram_updated
    assert "<polygon fill=\"#555555\"" in diagram_updated
    assert "AEAD&#45;encrypt record with Kᵣ" in diagram_updated

    assert figure_updated != figure_original
    assert diagram_updated != diagram_original


def test_check_mode_detects_missing_metadata(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    module = load_module()
    sandbox = clone_asset_tree(tmp_path)
    figure_spec = module.INVENTORY_BY_CODE["F1"]
    figure_path = sandbox / figure_spec.relative_path
    figure_path.write_text(
        strip_expected_accessibility_metadata(
            figure_path.read_text(encoding="utf-8"),
            figure_spec,
        ),
        encoding="utf-8",
    )

    exit_code = module.main(["--project-root", str(sandbox)])

    captured = capsys.readouterr()
    assert exit_code == module.EXIT_MISMATCH
    assert "missing accessibility metadata" in captured.err
    assert "figure_1_theoretical_detection_bound.svg" in captured.err


def test_apply_is_idempotent_and_check_passes(tmp_path: Path) -> None:
    module = load_module()
    sandbox = clone_asset_tree(tmp_path)
    d2_spec = module.INVENTORY_BY_CODE["D2"]
    d2_path = sandbox / d2_spec.relative_path
    d2_before = d2_path.read_bytes()

    first_exit = module.main(["--apply", "--project-root", str(sandbox)])
    assert first_exit == module.EXIT_OK

    snapshots_after_first_apply = {
        relative_path: (sandbox / relative_path).read_bytes()
        for relative_path in EXPECTED_PATHS
    }

    second_exit = module.main(["--apply", "--project-root", str(sandbox)])
    assert second_exit == module.EXIT_OK

    snapshots_after_second_apply = {
        relative_path: (sandbox / relative_path).read_bytes()
        for relative_path in EXPECTED_PATHS
    }

    assert snapshots_after_second_apply == snapshots_after_first_apply
    assert module.main(["--check", "--project-root", str(sandbox)]) == module.EXIT_OK
    assert d2_path.read_bytes() == d2_before


def test_d2_validation_succeeds_and_bytes_remain_unchanged(tmp_path: Path) -> None:
    module = load_module()
    sandbox = clone_asset_tree(tmp_path)
    d2_spec = module.INVENTORY_BY_CODE["D2"]
    d2_path = sandbox / d2_spec.relative_path
    original_bytes = d2_path.read_bytes()

    problems = module.validate_svg_text(d2_path.read_text(encoding="utf-8"), d2_spec)

    assert problems == []
    assert module.apply_inventory(sandbox) == module.EXIT_OK
    assert d2_path.read_bytes() == original_bytes


def test_nested_title_and_desc_do_not_satisfy_root_metadata_validation() -> None:
    module = load_module()
    spec = module.INVENTORY_BY_CODE["D1"]
    nested_svg = f"""<svg role="img" aria-labelledby="{spec.stable_id}-title {spec.stable_id}-desc">
<g>
<title id="{spec.stable_id}-title">{spec.title}</title>
<desc id="{spec.stable_id}-desc">{spec.description}</desc>
</g>
<rect width="10" height="10"/>
</svg>
"""

    problems = module.validate_svg_text(nested_svg, spec)

    assert "missing accessibility metadata: root title" in problems
    assert "missing accessibility metadata: root desc" in problems


def test_attr_strings_inside_other_attr_values_do_not_satisfy_root_attrs() -> None:
    module = load_module()
    spec = module.INVENTORY_BY_CODE["D1"]
    deceptive_svg = f"""<svg data-note='role="img" aria-labelledby="{spec.stable_id}-title {spec.stable_id}-desc"'>
<title id="{spec.stable_id}-title">{spec.title}</title>
<desc id="{spec.stable_id}-desc">{spec.description}</desc>
<rect width="10" height="10"/>
</svg>
"""

    problems = module.validate_svg_text(deceptive_svg, spec)

    assert "missing accessibility metadata: root role=\"img\"" in problems
    assert "missing accessibility metadata: root aria-labelledby" in problems


def test_single_quoted_existing_root_attrs_are_rewritten_without_duplicates() -> None:
    module = load_module()
    spec = module.INVENTORY_BY_CODE["D1"]
    single_quoted_svg = f"""<svg role='presentation' aria-labelledby='wrong-title wrong-desc' data-note='keep'>
<title id="wrong-title">Wrong</title>
<desc id="wrong-desc">Wrong</desc>
<rect width="10" height="10"/>
</svg>
"""

    updated = module.annotate_svg_text(single_quoted_svg, spec)

    assert updated.count(' role="img"') == 1
    assert updated.count(' aria-labelledby="d1-title d1-desc"') == 1
    assert "role='presentation'" not in updated
    assert "aria-labelledby='wrong-title wrong-desc'" not in updated
    assert "data-note='keep'" in updated
    assert module.validate_svg_text(updated, spec) == []


def test_apply_fails_closed_without_writing_when_inventory_is_incomplete(tmp_path: Path) -> None:
    module = load_module()
    sandbox = clone_asset_tree(tmp_path)
    missing_relative_path = "diagrams/08_experiment_pipeline.svg"
    missing_path = sandbox / missing_relative_path
    preserved_path = sandbox / "prototype/results/figures/figure_1_theoretical_detection_bound.svg"
    preserved_before = preserved_path.read_bytes()
    missing_path.unlink()

    exit_code = module.main(["--apply", "--project-root", str(sandbox)])

    assert exit_code == module.EXIT_MISMATCH
    assert preserved_path.read_bytes() == preserved_before


def test_svgx_tag_is_not_accepted_as_svg_root() -> None:
    module = load_module()
    spec = module.INVENTORY_BY_CODE["D1"]
    fake_svg = f"""<svgx role="img" aria-labelledby="{spec.stable_id}-title {spec.stable_id}-desc">
<title id="{spec.stable_id}-title">{spec.title}</title>
<desc id="{spec.stable_id}-desc">{spec.description}</desc>
</svgx>
"""

    problems = module.validate_svg_text(fake_svg, spec)

    assert problems == ["missing root <svg> element"]


def test_leading_comment_and_declaration_with_svg_text_are_ignored() -> None:
    module = load_module()
    spec = module.INVENTORY_BY_CODE["D1"]
    compliant_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- deceptive text: <svg role="none"> -->
<!DOCTYPE note [<!ENTITY example "<svg not-a-root>">]>
<svg role="img" aria-labelledby="{spec.stable_id}-title {spec.stable_id}-desc">
<title id="{spec.stable_id}-title">{spec.title}</title>
<desc id="{spec.stable_id}-desc">{spec.description}</desc>
<rect width="10" height="10"/>
</svg>
"""

    assert module.validate_svg_text(compliant_svg, spec) == []
