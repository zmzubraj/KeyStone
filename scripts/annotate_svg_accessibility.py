#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
import html
import os
from pathlib import Path
import re
import sys
import tempfile


EXIT_OK = 0
EXIT_MISMATCH = 1
EXIT_USAGE = 2
EXIT_ERROR = 3

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ROOT_ATTR_RE = re.compile(
    r"(?P<leading>\s+)"
    r"(?P<name>[A-Za-z_:][A-Za-z0-9_.:-]*)"
    r"\s*=\s*"
    r"(?P<quote>['\"])"
    r"(?P<value>.*?)"
    r"(?P=quote)",
    re.DOTALL,
)
LEADING_TITLE_DESC_RE = re.compile(
    r"^\s*(?:"
    r"(<title\b[^>]*>.*?</title>)(?:\s*"
    r"(<desc\b[^>]*>.*?</desc>)"
    r")?"
    r"|(<desc\b[^>]*>.*?</desc>)"
    r")",
    re.DOTALL,
)


@dataclass(frozen=True)
class AssetSpec:
    code: str
    relative_path: str
    stable_id: str
    title: str
    description: str
    validate_only: bool = False


INVENTORY = (
    AssetSpec(
        code="F1",
        relative_path="prototype/results/figures/figure_1_theoretical_detection_bound.svg",
        stable_id="f1",
        title="F1. Static catastrophic false-accept detection bound",
        description=(
            "Analytical line chart for a 32-member committee showing the worst-case "
            "probability of detecting a static catastrophic ready-set failure as audit "
            "sample size increases, with separate curves for thresholds t=17, t=22, and "
            "t=25 under the fixed-set uniform-sampling model."
        ),
    ),
    AssetSpec(
        code="F2",
        relative_path="prototype/results/figures/figure_2_iid_failure_sweep.svg",
        stable_id="f2",
        title="F2. Reconstruction and audit pass rates under independent failures",
        description=(
            "Monte Carlo sweep over independent custodian offline probability from 0.0 to "
            "0.4, comparing target-dispute reconstruction success with all-response audit "
            "pass rate and reporting catastrophic detections only within the sampled "
            "catastrophic trials."
        ),
    ),
    AssetSpec(
        code="F3",
        relative_path="prototype/results/figures/figure_3_domain_diversity.svg",
        stable_id="f3",
        title="F3. Committee diversity reduces correlated-outage risk",
        description=(
            "Simulation line chart showing dispute reconstruction success as the number of "
            "independent failure domains increases from 2 to 16 for the fixed correlated-"
            "outage scenario used in the prototype experiments."
        ),
    ),
    AssetSpec(
        code="F4",
        relative_path="prototype/results/figures/figure_4_selective_withholding_gap.svg",
        stable_id="f4",
        title="F4. Selective withholding separates prior audit success from target opening",
        description=(
            "Monte Carlo plot comparing prior canary-audit pass probability with target-"
            "dispute reconstruction probability as more custodians answer audits but "
            "withhold the target record, making the limitation explicit rather than "
            "claiming unconditional future availability."
        ),
    ),
    AssetSpec(
        code="F5",
        relative_path="prototype/results/figures/figure_5_sampling_strategy.svg",
        stable_id="f5",
        title="F5. Uniform versus domain-stratified sampling under correlated failure",
        description=(
            "Monte Carlo comparison of catastrophic-state detection rates for uniform and "
            "failure-domain-stratified audit sampling across sample sizes 4 through 16 in "
            "the correlated four-domain outage model."
        ),
    ),
    AssetSpec(
        code="D1",
        relative_path="diagrams/01_system_architecture.svg",
        stable_id="d1",
        title="D1. KEYSTONE system architecture",
        description=(
            "Architecture diagram separating ciphertext availability, policy and bulletin-"
            "board coordination, authorized dispute release, threshold combination, "
            "private re-execution, and final dispute verdict generation."
        ),
    ),
    AssetSpec(
        code="D2",
        relative_path="diagrams/02_property_separation.svg",
        stable_id="d2",
        title="D2. Three constructive property-separation witnesses",
        description=(
            "Three counterexample witnesses show that ciphertext availability does not "
            "imply dispute-key availability, routine audit acceptance does not imply "
            "targeted dispute success, and finite audits do not guarantee future dispute-"
            "key availability. This is not a complete pairwise lattice."
        ),
        validate_only=True,
    ),
    AssetSpec(
        code="D3",
        relative_path="diagrams/03_audit_sequence.svg",
        stable_id="d3",
        title="D3. Readiness audit sequence",
        description=(
            "Protocol-sequence diagram for the readiness audit path: commit the epoch "
            "roster and labels, sample from beacon randomness, collect canary responses "
            "and proofs before the deadline, and publish the resulting evidence."
        ),
    ),
    AssetSpec(
        code="D4",
        relative_path="diagrams/04_dispute_sequence.svg",
        stable_id="d4",
        title="D4. Authorized dispute opening sequence",
        description=(
            "Protocol-sequence diagram for an authorized challenge: post the dispute "
            "request and bond, release confidential partials under policy, combine at "
            "least t verified responses, re-execute privately, and record the verdict."
        ),
    ),
    AssetSpec(
        code="D5",
        relative_path="diagrams/05_state_machines.svg",
        stable_id="d5",
        title="D5. Epoch, audit, and dispute state machines",
        description=(
            "State-machine view of the KEYSTONE epoch lifecycle together with the audit "
            "and dispute lifecycles, showing the allowed transitions rather than implying "
            "stronger guarantees than the protocol defines."
        ),
    ),
    AssetSpec(
        code="D6",
        relative_path="diagrams/06_threat_model.svg",
        stable_id="d6",
        title="D6. Threat model, controls, and residual risk",
        description=(
            "Threat-model diagram mapping adversary or fault classes to the controls the "
            "prototype applies and to the residual risks that remain outside the paper's "
            "claim boundary."
        ),
    ),
    AssetSpec(
        code="D7",
        relative_path="diagrams/07_sampling_domains.svg",
        stable_id="d7",
        title="D7. Uniform and domain-stratified sampling under domain outage",
        description=(
            "Illustration of a 32-member committee partitioned across four fault domains "
            "with one domain offline, contrasting uniform sampling with domain-stratified "
            "sampling for correlated-failure detection."
        ),
    ),
    AssetSpec(
        code="D8",
        relative_path="diagrams/08_experiment_pipeline.svg",
        stable_id="d8",
        title="D8. Reproducible minimum publishable prototype pipeline",
        description=(
            "Pipeline diagram linking frozen configuration, adversarial simulation, "
            "metrics, figures, and paper-ready evidence so the prototype outputs remain "
            "traceable to the declared experimental inputs."
        ),
    ),
)

INVENTORY_BY_CODE = {spec.code: spec for spec in INVENTORY}


def _escape_text(value: str) -> str:
    return html.escape(value, quote=False)


def _root_label_value(spec: AssetSpec) -> str:
    return f"{spec.stable_id}-title {spec.stable_id}-desc"


def _expected_title(spec: AssetSpec) -> str:
    return f'<title id="{spec.stable_id}-title">{_escape_text(spec.title)}</title>'


def _expected_desc(spec: AssetSpec) -> str:
    return f'<desc id="{spec.stable_id}-desc">{_escape_text(spec.description)}</desc>'


def _leading_metadata_remainder(svg_text: str) -> tuple[re.Match[str], str]:
    root_tag_start = _find_root_svg_start(svg_text)
    if root_tag_start == -1:
        raise ValueError("missing root <svg> element")
    tag_end = _find_root_tag_end(svg_text, root_tag_start)
    attrs_start = root_tag_start + len("<svg")
    attrs = svg_text[attrs_start:tag_end - 1]
    return _RootSvgMatch(root_tag_start, tag_end, attrs), svg_text[tag_end:]


class _RootSvgMatch:
    def __init__(self, start: int, end: int, attrs: str) -> None:
        self._start = start
        self._end = end
        self._attrs = attrs

    def start(self) -> int:
        return self._start

    def end(self) -> int:
        return self._end

    def group(self, name_or_index: str | int) -> str:
        if name_or_index == 0:
            raise ValueError("full tag retrieval is not supported")
        if name_or_index != "attrs":
            raise KeyError(name_or_index)
        return self._attrs


def _find_root_svg_start(svg_text: str) -> int:
    index = 0
    length = len(svg_text)
    while index < length:
        while index < length and svg_text[index].isspace():
            index += 1
        if index >= length:
            return -1
        if svg_text.startswith("<?", index):
            end = svg_text.find("?>", index + 2)
            if end == -1:
                return -1
            index = end + 2
            continue
        if svg_text.startswith("<!--", index):
            end = svg_text.find("-->", index + 4)
            if end == -1:
                return -1
            index = end + 3
            continue
        if svg_text.startswith("<!", index):
            end = _find_declaration_end(svg_text, index + 2)
            if end == -1:
                return -1
            index = end + 1
            continue
        if svg_text.startswith("<svg", index) and _is_svg_tag_boundary(svg_text, index + 4):
            return index
        return -1
    return -1


def _find_declaration_end(svg_text: str, index: int) -> int:
    bracket_depth = 0
    quote: str | None = None
    while index < len(svg_text):
        char = svg_text[index]
        if quote is None:
            if char in ("'", '"'):
                quote = char
            elif char == "[":
                bracket_depth += 1
            elif char == "]" and bracket_depth > 0:
                bracket_depth -= 1
            elif char == ">" and bracket_depth == 0:
                return index
        elif char == quote:
            quote = None
        index += 1
    return -1


def _is_svg_tag_boundary(svg_text: str, index: int) -> bool:
    if index >= len(svg_text):
        return False
    return svg_text[index].isspace() or svg_text[index] == ">"


def _find_root_tag_end(svg_text: str, start: int) -> int:
    index = start + len("<svg")
    quote: str | None = None
    while index < len(svg_text):
        char = svg_text[index]
        if quote is None:
            if char in ("'", '"'):
                quote = char
            elif char == ">":
                return index + 1
        elif char == quote:
            quote = None
        index += 1
    raise ValueError("unterminated root <svg> element")


def _parse_root_attrs(root_attrs: str) -> list[dict[str, object]]:
    attrs: list[dict[str, object]] = []
    index = 0
    while index < len(root_attrs):
        match = ROOT_ATTR_RE.match(root_attrs, index)
        if match is None:
            index += 1
            continue
        attrs.append({
            "name": match.group("name"),
            "value": match.group("value"),
            "span": match.span(),
        })
        index = match.end()
    return attrs


def _root_attr_value(root_attrs: str, name: str) -> str | None:
    for attr in _parse_root_attrs(root_attrs):
        if attr["name"] == name:
            value = attr["value"]
            assert isinstance(value, str)
            return value
    return None


def _rewrite_root_attrs(root_attrs: str, spec: AssetSpec) -> str:
    kept_segments: list[str] = []
    cursor = 0
    for attr in _parse_root_attrs(root_attrs):
        span = attr["span"]
        assert isinstance(span, tuple)
        start, end = span
        name = attr["name"]
        assert isinstance(name, str)
        if name in {"role", "aria-labelledby"}:
            kept_segments.append(root_attrs[cursor:start])
            cursor = end
    kept_segments.append(root_attrs[cursor:])
    cleaned_attrs = "".join(kept_segments).rstrip()
    if cleaned_attrs and not cleaned_attrs[0].isspace():
        cleaned_attrs = f" {cleaned_attrs}"
    return (
        f'{cleaned_attrs} role="img" aria-labelledby="{_root_label_value(spec)}"'
    )


def _leading_root_metadata_match(remainder: str) -> re.Match[str] | None:
    return LEADING_TITLE_DESC_RE.match(remainder)


def validate_svg_text(svg_text: str, spec: AssetSpec) -> list[str]:
    problems: list[str] = []
    try:
        match, remainder = _leading_metadata_remainder(svg_text)
    except ValueError as exc:
        return [str(exc)]

    root_attrs = match.group("attrs")
    role_value = _root_attr_value(root_attrs, "role")
    aria_value = _root_attr_value(root_attrs, "aria-labelledby")

    if role_value != "img":
        problems.append("missing accessibility metadata: root role=\"img\"")
    if aria_value != _root_label_value(spec):
        problems.append("missing accessibility metadata: root aria-labelledby")

    leading_match = _leading_root_metadata_match(remainder)
    actual_title = None
    actual_desc = None
    if leading_match is not None:
        actual_title = leading_match.group(1)
        actual_desc = leading_match.group(2) or leading_match.group(3)

    if actual_title != _expected_title(spec):
        problems.append("missing accessibility metadata: root title")
    if actual_desc != _expected_desc(spec):
        problems.append("missing accessibility metadata: root desc")
    return problems


def annotate_svg_text(svg_text: str, spec: AssetSpec) -> str:
    if spec.validate_only:
        return svg_text

    match, remainder = _leading_metadata_remainder(svg_text)
    root_tag = f'<svg{_rewrite_root_attrs(match.group("attrs"), spec)}>'

    leading_match = _leading_root_metadata_match(remainder)
    if leading_match is not None:
        remainder = remainder[leading_match.end():]

    separator = "" if remainder.startswith("\n") else "\n"
    metadata_block = f"\n{_expected_title(spec)}\n{_expected_desc(spec)}{separator}"
    return f"{svg_text[:match.start()]}{root_tag}{metadata_block}{remainder}"


def _atomic_write(path: Path, content: str) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        temp_path.chmod(path.stat().st_mode)
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _asset_path(project_root: Path, spec: AssetSpec) -> Path:
    return project_root / spec.relative_path


def validate_inventory(project_root: Path) -> list[str]:
    problems: list[str] = []
    for spec in INVENTORY:
        path = _asset_path(project_root, spec)
        if not path.exists():
            problems.append(f"{spec.relative_path}: missing file")
            continue
        asset_problems = validate_svg_text(path.read_text(encoding="utf-8"), spec)
        for problem in asset_problems:
            problems.append(f"{spec.relative_path}: {problem}")
    return problems


def _read_svg_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _plan_apply(project_root: Path) -> tuple[list[str], list[tuple[Path, str]]]:
    problems: list[str] = []
    planned_updates: list[tuple[Path, str]] = []
    for spec in INVENTORY:
        path = _asset_path(project_root, spec)
        if not path.exists():
            problems.append(f"{spec.relative_path}: missing file")
            continue
        try:
            original = _read_svg_text(path)
        except OSError as exc:
            problems.append(f"{spec.relative_path}: unreadable file: {exc}")
            continue
        except UnicodeDecodeError as exc:
            problems.append(f"{spec.relative_path}: unreadable utf-8 svg: {exc}")
            continue

        current_problems = validate_svg_text(original, spec)
        if spec.validate_only:
            for problem in current_problems:
                problems.append(f"{spec.relative_path}: {problem}")
            continue

        try:
            updated = annotate_svg_text(original, spec)
        except ValueError as exc:
            problems.append(f"{spec.relative_path}: unannotatable svg: {exc}")
            continue

        updated_problems = validate_svg_text(updated, spec)
        if updated_problems:
            for problem in updated_problems:
                problems.append(f"{spec.relative_path}: {problem}")
            continue

        if updated != original:
            planned_updates.append((path, updated))
    return problems, planned_updates


def apply_inventory(project_root: Path) -> int:
    problems, planned_updates = _plan_apply(project_root)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return EXIT_MISMATCH

    for path, updated in planned_updates:
        _atomic_write(path, updated)

    problems = validate_inventory(project_root)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return EXIT_MISMATCH

    print(
        f"Accessibility metadata verified for {len(INVENTORY)} SVG assets; updated {len(planned_updates)}.",
        file=sys.stderr,
    )
    return EXIT_OK


def check_inventory(project_root: Path) -> int:
    problems = validate_inventory(project_root)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return EXIT_MISMATCH

    print(f"Accessibility metadata verified for {len(INVENTORY)} SVG assets.", file=sys.stderr)
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="validate inventory without modifying files")
    mode.add_argument("--apply", action="store_true", help="atomically update non-compliant assets, then verify")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="project root containing the KEYSTONE SVG inventory",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    project_root = args.project_root.resolve()

    try:
        if args.apply:
            return apply_inventory(project_root)
        return check_inventory(project_root)
    except Exception as exc:  # pragma: no cover - fatal path
        print(f"fatal: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
