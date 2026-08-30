#!/usr/bin/env python3
"""Export the integrated, result-blind, non-executable KEYSTONE PC03 amendment."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import sys
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
STATE = Path("research-case/program-state.json")
CHARTER = Path("research-case/00-governance/program-charter.md")
AMENDMENT = Path("research-case/03-design/pc03-prospective-amendment.md")
COUNTS = Path("research-case/03-design/pc03-prospective-counts.csv")
SEEDS = Path("research-case/03-design/pc03-seed-schedule.csv")
CHALLENGE_DIR = Path("research-case/03-design/pc03-independent-methods-challenge")

DESIGN_INPUTS = (
    Path("research-case/03-design/protocol.md"),
    Path("research-case/03-design/analysis-plan.md"),
    Path("research-case/03-design/power-or-precision.md"),
    Path("research-case/03-design/preregistration-and-deviations.md"),
)
CHALLENGE_INPUTS = (
    CHALLENGE_DIR / "design-assessment.md",
    CHALLENGE_DIR / "prospective-counts.csv",
    CHALLENGE_DIR / "calculation-notes.md",
)

PRIMARY_BLOCKS = 32
RESERVE_BLOCKS = 4
DRAWS_PER_BLOCK = 4096
CAPACITY = PRIMARY_BLOCKS * DRAWS_PER_BLOCK
FAMILY_ALPHA = 0.05
UNPAIRED_EPSILON = 0.005
PAIRED_EPSILON = 0.01


class AmendmentError(RuntimeError):
    pass


def _text(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AmendmentError(f"cannot read {label}: {exc}") from exc


def _json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(_text(path, label))
    except json.JSONDecodeError as exc:
        raise AmendmentError(f"invalid JSON in {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise AmendmentError(f"{label} must be an object")
    return value


def _validate(root: Path) -> None:
    state = _json(root / STATE, "program state")
    expected = {
        "schema_version": 4,
        "status": "ACTIVE",
        "current_phase": "INTAKE",
        "novelty_status": "UNRESOLVED",
        "feasibility_decision": "UNASSESSED",
        "solution_viability_status": "ASSERTED_ONLY",
        "acceptance_readiness": "NOT_ASSESSABLE",
    }
    mismatches = [
        f"{field}={state.get(field)!r} expected={wanted!r}"
        for field, wanted in expected.items()
        if state.get(field) != wanted
    ]
    if mismatches:
        raise AmendmentError(
            "PC03 amendment requires fail-closed INTAKE: "
            + "; ".join(mismatches)
        )

    charter = _text(root / CHARTER, "program charter").lower()
    if not all(
        phrase in charter
        for phrase in ("final author order", "corresponding-author", "affiliation wording", "remain deferred")
    ):
        raise AmendmentError("program charter does not preserve author metadata deferral")

    design = "\n".join(_text(root / path, path.as_posix()) for path in DESIGN_INPUTS)
    for result_id in (
        "RID-C003-IID-001",
        "RID-C003-CORR-001",
        "RID-C003-STRAT-001",
        "RID-C003-SW-001",
        "RID-C003-DEADLINE-001",
    ):
        if result_id not in design:
            raise AmendmentError(f"design inputs do not reserve {result_id}")
    if "does not authorize execution" not in design.lower():
        raise AmendmentError("design inputs do not preserve the execution prohibition")

    challenge_parts = []
    for path in CHALLENGE_INPUTS:
        challenge_parts.append(_text(root / path, f"methods challenge {path.name}"))
    challenge = "\n".join(challenge_parts)
    required = (
        "Developmental AI methods review only",
        "iid-10pct-uniform",
        "sample_size=8",
        "selective_withholders = n - t + 1 = 11",
        "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE",
        "EXCLUDED_PENDING_ENVIRONMENT_PROFILE",
    )
    if not all(marker in challenge for marker in required):
        raise AmendmentError("developmental methods challenge is incomplete or has drifted")


def _required_draws(epsilon: float, value_range: float) -> int:
    # Hoeffding for one prespecified cell:
    # 2 exp(-2 n epsilon^2 / range^2) <= alpha.
    return math.ceil(value_range**2 * math.log(2 / FAMILY_ALPHA) / (2 * epsilon**2))


INCLUDED = {
    "RID-C003-IID-001": {
        "lane": "MINIMUM_SHORT_PAPER_SUPPORT",
        "cell_id": "iid-10pct-uniform;n=32;t=22;s=8;q=8;p_offline=0.10",
        "estimand": "reconstruction-success and audit-pass probabilities in one frozen IID baseline cell",
        "epsilon": UNPAIRED_EPSILON,
        "value_range": 1.0,
        "method": "HOEFFDING_BERNOULLI_MODEL_DRAW",
    },
    "RID-C003-STRAT-001": {
        "lane": "MINIMUM_SHORT_PAPER_SUPPORT",
        "cell_id": "domain-outage-20pct;sample-size-8;uniform-vs-stratified;domains=4",
        "estimand": "matched-draw stratified-minus-uniform policy difference in one frozen baseline cell",
        "epsilon": PAIRED_EPSILON,
        "value_range": 2.0,
        "method": "HOEFFDING_PAIRED_DIFFERENCE_RANGE_MINUS1_TO_1",
    },
    "RID-C003-SW-001": {
        "lane": "MINIMUM_SHORT_PAPER_CORE",
        "cell_id": "selective-withholders-11;n=32;t=22;s=8;q=8",
        "estimand": "within-draw audit-pass-minus-dispute-success gap at the first non-reconstructable boundary",
        "epsilon": PAIRED_EPSILON,
        "value_range": 2.0,
        "method": "HOEFFDING_PAIRED_DIFFERENCE_RANGE_MINUS1_TO_1",
    },
}

COUNT_FIELDS = (
    "result_id",
    "mpp_lane",
    "cell_id",
    "estimand",
    "planned_cells",
    "primary_seed_blocks_per_cell",
    "reserve_seed_blocks_per_cell",
    "draws_per_seed_block",
    "primary_draws_per_cell",
    "required_draws_per_cell",
    "familywise_alpha",
    "precision_target",
    "precision_method",
    "multiplicity_rule",
    "environment_status",
    "execution_status",
    "authorized",
    "independent",
    "observed_outcome",
    "historical_output_reuse",
    "exclusion_basis",
)


def _count_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for result_id, spec in INCLUDED.items():
        epsilon = float(spec["epsilon"])
        required = _required_draws(epsilon, float(spec["value_range"]))
        if required > CAPACITY:
            raise AmendmentError(f"scheduled capacity is below the bound for {result_id}")
        rows.append(
            {
                "result_id": result_id,
                "mpp_lane": str(spec["lane"]),
                "cell_id": str(spec["cell_id"]),
                "estimand": str(spec["estimand"]),
                "planned_cells": "1",
                "primary_seed_blocks_per_cell": str(PRIMARY_BLOCKS),
                "reserve_seed_blocks_per_cell": str(RESERVE_BLOCKS),
                "draws_per_seed_block": str(DRAWS_PER_BLOCK),
                "primary_draws_per_cell": str(CAPACITY),
                "required_draws_per_cell": str(required),
                "familywise_alpha": f"{FAMILY_ALPHA:.2f}",
                "precision_target": f"ABSOLUTE_HALF_WIDTH_LE_{epsilon:.3f}",
                "precision_method": str(spec["method"]),
                "multiplicity_rule": "NONE_SINGLE_PRESPECIFIED_PRIMARY_CELL;HOLM_FOR_OPTIONAL_SECONDARY_TESTS",
                "environment_status": "LOCAL_SYNTHETIC_FROZEN",
                "execution_status": "BLOCKED_PENDING_GATE",
                "authorized": "false",
                "independent": "false",
                "observed_outcome": "NOT_COLLECTED",
                "historical_output_reuse": "PROHIBITED_AS_CONFIRMATORY_EVIDENCE",
                "exclusion_basis": "",
            }
        )
    rows.insert(
        1,
        {
            "result_id": "RID-C003-CORR-001",
            "mpp_lane": "MINIMUM_SHORT_PAPER_SUPPORT",
            "cell_id": "NONE",
            "estimand": "correlated-domain qualification",
            "planned_cells": "0",
            "primary_seed_blocks_per_cell": "0",
            "reserve_seed_blocks_per_cell": "0",
            "draws_per_seed_block": "0",
            "primary_draws_per_cell": "0",
            "required_draws_per_cell": "UNRESOLVED",
            "familywise_alpha": "UNRESOLVED",
            "precision_target": "UNRESOLVED",
            "precision_method": "NOT_APPLICABLE_WHILE_EXCLUDED",
            "multiplicity_rule": "UNRESOLVED",
            "environment_status": "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE",
            "execution_status": "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE",
            "authorized": "false",
            "independent": "false",
            "observed_outcome": "NOT_COLLECTED",
            "historical_output_reuse": "PROHIBITED_AS_CONFIRMATORY_EVIDENCE",
            "exclusion_basis": "truthful domain-label source and concentrated-placement comparator are not frozen",
        },
    )
    rows.append(
        {
            "result_id": "RID-C003-DEADLINE-001",
            "mpp_lane": "EXTENDED_FULL_PAPER",
            "cell_id": "NONE",
            "estimand": "conditional distributed deadline success",
            "planned_cells": "0",
            "primary_seed_blocks_per_cell": "0",
            "reserve_seed_blocks_per_cell": "0",
            "draws_per_seed_block": "0",
            "primary_draws_per_cell": "0",
            "required_draws_per_cell": "UNRESOLVED",
            "familywise_alpha": "UNRESOLVED",
            "precision_target": "UNRESOLVED",
            "precision_method": "NOT_APPLICABLE_WHILE_EXCLUDED",
            "multiplicity_rule": "UNRESOLVED",
            "environment_status": "EXCLUDED_PENDING_ENVIRONMENT_PROFILE",
            "execution_status": "EXCLUDED_PENDING_ENVIRONMENT_PROFILE",
            "authorized": "false",
            "independent": "false",
            "observed_outcome": "NOT_COLLECTED",
            "historical_output_reuse": "PROHIBITED_AS_CONFIRMATORY_EVIDENCE",
            "exclusion_basis": "environment topology load synchrony deadline interpretation and trace denominator are not frozen",
        }
    )
    return rows


SEED_FIELDS = (
    "result_id",
    "cell_id",
    "block_index",
    "role",
    "seed",
    "seed_derivation",
    "draws",
    "execution_status",
)


def _seed_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[int] = set()
    for result_id, spec in INCLUDED.items():
        cell_id = str(spec["cell_id"])
        for index in range(1, PRIMARY_BLOCKS + RESERVE_BLOCKS + 1):
            material = f"KEYSTONE-MPP-F1|PC03|v2|{result_id}|{cell_id}|{index:02d}"
            seed = int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")
            if seed in seen:
                raise AmendmentError("unexpected deterministic seed collision")
            seen.add(seed)
            rows.append(
                {
                    "result_id": result_id,
                    "cell_id": cell_id,
                    "block_index": str(index),
                    "role": "PRIMARY" if index <= PRIMARY_BLOCKS else "RESERVE",
                    "seed": str(seed),
                    "seed_derivation": f"SHA256({material})[0:8]_BIG_ENDIAN",
                    "draws": str(DRAWS_PER_BLOCK),
                    "execution_status": "BLOCKED_PENDING_GATE",
                }
            )
    return rows


def _csv(fields: tuple[str, ...], rows: list[dict[str, str]]) -> str:
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def _amendment(rows: list[dict[str, str]]) -> str:
    table = "\n".join(
        f"| `{row['result_id']}` | `{row['cell_id']}` | `{row['primary_draws_per_cell']}` | `{row['required_draws_per_cell']}` | `{row['precision_target']}` | `{row['execution_status']}` |"
        for row in rows
    )
    return f"""# KEYSTONE PC03 integrated prospective design amendment

Status: `DRAFT / PREAUTHORIZATION / NON-EXECUTABLE`
System: `KEYSTONE-MPP-F1`
Date: `2026-08-30`
Canonical phase: `INTAKE`

This is a result-blind integration artifact. It does not authorize execution,
issue `GO`, certify methods, promote the research phase, or convert historical
outputs into confirmatory evidence. Author metadata remains deferred.
Exploratory outputs were not used to choose the count, precision, or decision
thresholds.

## Independent challenge disposition

The developmental AI methods challenge under
`{CHALLENGE_DIR.as_posix()}/` recommended the minimum decisive cell set:
one IID baseline cell, one matched sampling-policy cell, and the
selective-withholding boundary at `n-t+1=11`; it recommended excluding CORR
and DEADLINE until their missing contracts are frozen. This narrowing is
accepted because it matches the minimum publishable claim and avoids silently
promoting broad exploratory sweeps.

The challenge's proposed counts of 97 and 193 seed-level runs are not adopted.
The current simulator returns aggregate proportions from many scenario draws
inside each seed run, so treating each aggregate as a Bernoulli replicate creates
a denominator mismatch. The integrated design instead treats independent
synthetic scenario draws as the Monte Carlo denominator and seed blocks as
execution and reproducibility units. This is a root integration decision, not
an independent methods sign-off.

## Count and stream contract

Every included cell uses 32 primary seed blocks and four ordered reserve blocks,
with 4,096 independent synthetic scenario draws per block and 131,072 primary
draws per cell. Blockwise estimates and between-block dispersion are mandatory.
A failed primary block stays in the deviation ledger and may be replaced only by
the next reserve block; a valid unfavorable block is never replaceable.

For one Bernoulli cell, Hoeffding requires
`n >= ceil(log(2/0.05)/(2*0.005^2)) = 73,778` draws. For one paired
difference in `[-1,1]`, it requires
`n >= ceil(2*log(2/0.05)/0.01^2) = 73,778` matched draws. The scheduled
131,072 draws exceed both bounds. These guarantees concern precision under the
frozen synthetic model only; they are not field power, deployment reliability,
or external validation.

| Result ID | Operative cell | Capacity | Required | Precision | Status |
| --- | --- | ---: | ---: | --- | --- |
{table}

## Analysis boundary

- `RID-C003-IID-001`: empirical reconstruction and audit-pass proportions,
  absolute error target 0.005, plus blockwise estimates and exact zero-event
  upper bounds.
- `RID-C003-STRAT-001`: common-random-number paired difference at sample size
  8, absolute error target 0.01; unpaired substitution is prohibited.
- `RID-C003-SW-001`: within-draw audit-pass minus dispute-success gap at 11
  selective withholders, absolute error target 0.01; the limitation is reported
  regardless of direction.
- `RID-C003-CORR-001`: `EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE`.
- `RID-C003-DEADLINE-001`: `EXCLUDED_PENDING_ENVIRONMENT_PROFILE`.

There is one primary cell per included result family, so no primary within-family
multiplicity adjustment is needed. Optional secondary hypothesis tests use Holm
within their named family and cannot upgrade a claim.

## Stop rules

Stop or redesign on overlapping random streams, exploratory-outcome-dependent
thresholds, cross-cell pooling, unpaired treatment of matched outcomes, hidden
failed blocks, suppressed negative findings, execution of an excluded lane,
use of personal data or production secrets, or manuscript wording beyond
simulated-model maturity.

The machine-readable sources are `{COUNTS.as_posix()}` and
`{SEEDS.as_posix()}`. All execution remains blocked pending PC01 authority,
PC02 novelty disposition, authenticated independent PC03 methods verification,
and a separate accountable start decision.
"""


def _write_or_check(path: Path, expected: str, check: bool, label: str) -> None:
    if check:
        try:
            actual = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise AmendmentError(f"cannot read {label}: {exc}") from exc
        if actual != expected:
            raise AmendmentError(f"{label} is stale: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        _validate(root)
        counts = _count_rows()
        seeds = _seed_rows()
        _write_or_check(root / AMENDMENT, _amendment(counts), args.check, "PC03 amendment")
        _write_or_check(root / COUNTS, _csv(COUNT_FIELDS, counts), args.check, "PC03 counts")
        _write_or_check(root / SEEDS, _csv(SEED_FIELDS, seeds), args.check, "PC03 seed schedule")
    except AmendmentError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"OK: PC03 integrated design {'current' if args.check else 'wrote'}; execution remains blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
