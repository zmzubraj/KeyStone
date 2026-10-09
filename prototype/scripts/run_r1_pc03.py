#!/usr/bin/env python3
"""Execute the frozen PC03 cells for KEYSTONE revision R1.

Reads the cell parameters from ``r1-design-freeze.json`` and the block seeds
from ``pc03-seed-schedule.csv``; refuses to run if the freeze hash differs from
the recorded SHA256SUMS line. Writes per-block rows and a cell summary to
``research-case/05-analysis/results/r1/``. Labels every output as
prespecified synthetic simulation with a non-independent methods review.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import random
import sys

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
sys.path.insert(0, str(PROJECT / "src"))

from keystone.simulation import wilson_score_interval  # noqa: E402

DESIGN = ROOT / "research-case/03-design"
FREEZE = DESIGN / "r1-reviewer-revision/r1-design-freeze.json"
FREEZE_SUMS = DESIGN / "r1-reviewer-revision/r1-design-freeze.SHA256SUMS"
SEEDS = DESIGN / "pc03-seed-schedule.csv"
OUT = ROOT / "research-case/05-analysis/results/r1"
LABEL = "PRESPECIFIED_SYNTHETIC_SIMULATION_NONINDEPENDENT_METHODS_REVIEW"
ALPHA = 0.05


def freeze_sha256() -> str:
    """Return the freeze hash after checking it against the recorded sum."""
    actual = hashlib.sha256(FREEZE.read_bytes()).hexdigest()
    recorded = next(
        line.split()[0]
        for line in FREEZE_SUMS.read_text().splitlines()
        if line.endswith("r1-design-freeze.json")
    )
    if actual != recorded:
        raise SystemExit(f"freeze hash mismatch: {actual} != {recorded}")
    return actual


def hoeffding_half_width(draws: int, value_range: float) -> float:
    """Two-sided Hoeffding half-width for a bounded mean at ALPHA."""
    return value_range * math.sqrt(math.log(2 / ALPHA) / (2 * draws))


def failure_state(cell: dict, rng: random.Random) -> list[bool]:
    """Draw infrastructure readiness for every member (True = ready)."""
    domains = cell["domains"]
    down = {d for d in range(domains) if rng.random() < cell["domain_outage_probability"]}
    return [
        (member % domains) not in down
        and rng.random() >= cell["independent_offline_probability"]
        for member in range(cell["n"])
    ]


def uniform_sample(n: int, s: int, rng: random.Random) -> list[int]:
    return rng.sample(range(n), s)


def fixed_quota_sample(n: int, domains: int, s: int, rng: random.Random) -> list[int]:
    """Fixed quota of s/domains members per domain, uniform within domain."""
    quota = s // domains
    picked: list[int] = []
    for domain in range(domains):
        picked.extend(rng.sample([m for m in range(n) if m % domains == domain], quota))
    return picked


def run_iid_block(cell: dict, seed: int, draws: int) -> dict[str, int]:
    rng = random.Random(seed)
    recon = audit = 0
    for _ in range(draws):
        ready = failure_state(cell, rng)
        recon += sum(ready) >= cell["t"]
        audit += sum(ready[i] for i in uniform_sample(cell["n"], cell["s"], rng)) >= cell["q"]
    return {"reconstruction_success": recon, "audit_pass": audit}


def run_strat_block(cell: dict, seed: int, draws: int) -> dict[str, int]:
    rng = random.Random(seed)
    counts = dict.fromkeys(
        ["catastrophic", "z_unif", "z_strat", "pass_unif", "pass_strat", "d_sum", "d_pos", "d_neg"], 0
    )
    for index in range(draws):
        ready = failure_state(cell, rng)
        catastrophic = sum(ready) < cell["t"]
        state = rng.getstate()
        order = ("uniform", "stratified") if index % 2 == 0 else ("stratified", "uniform")
        passes: dict[str, bool] = {}
        for policy in order:
            rng.setstate(state)
            sample = (
                uniform_sample(cell["n"], cell["s"], rng)
                if policy == "uniform"
                else fixed_quota_sample(cell["n"], cell["domains"], cell["s"], rng)
            )
            passes[policy] = sum(ready[i] for i in sample) >= cell["q"]
        z_u = int(catastrophic and not passes["uniform"])
        z_s = int(catastrophic and not passes["stratified"])
        counts["catastrophic"] += catastrophic
        counts["z_unif"] += z_u
        counts["z_strat"] += z_s
        counts["pass_unif"] += passes["uniform"]
        counts["pass_strat"] += passes["stratified"]
        counts["d_sum"] += z_s - z_u
        counts["d_pos"] += z_s > z_u
        counts["d_neg"] += z_s < z_u
    return counts


def run_sw_block(cell: dict, seed: int, draws: int) -> dict[str, int]:
    rng = random.Random(seed)
    withholders = set(range(cell["n"] - cell["selective_withholders"], cell["n"]))
    audit = dispute = gap = 0
    for _ in range(draws):
        ready = failure_state(cell, rng)
        dispute_ready = [r and m not in withholders for m, r in enumerate(ready)]
        a = sum(ready[i] for i in uniform_sample(cell["n"], cell["s"], rng)) >= cell["q"]
        d = sum(dispute_ready) >= cell["t"]
        audit += a
        dispute += d
        gap += int(a) - int(d)
    return {"audit_pass": audit, "dispute_success": dispute, "gap_sum": gap}


RUNNERS = {
    "RID-C003-IID-001": run_iid_block,
    "RID-C003-STRAT-001": run_strat_block,
    "RID-C003-SW-001": run_sw_block,
}


def main() -> None:
    freeze_hash = freeze_sha256()
    freeze = json.loads(FREEZE.read_text())
    cells = freeze["families"]["PC03"]["cells"]
    schedule = list(csv.DictReader(SEEDS.open()))
    OUT.mkdir(parents=True, exist_ok=True)
    summary: dict[str, dict] = {}

    for result_id, runner in RUNNERS.items():
        cell = cells[result_id]
        primaries = [r for r in schedule if r["result_id"] == result_id and r["role"] == "PRIMARY"]
        if len(primaries) != 32:
            raise SystemExit(f"{result_id}: expected 32 primary blocks, found {len(primaries)}")
        block_rows = []
        for row in sorted(primaries, key=lambda r: int(r["block_index"])):
            counts = runner(cell, int(row["seed"]), int(row["draws"]))
            block_rows.append({"block_index": int(row["block_index"]), "seed": row["seed"],
                               "draws": int(row["draws"]), **counts})
        with (OUT / f"{result_id}-blocks.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(block_rows[0]))
            writer.writeheader()
            writer.writerows(block_rows)

        total = sum(r["draws"] for r in block_rows)
        totals = {k: sum(r[k] for r in block_rows) for k in block_rows[0] if k not in ("block_index", "seed", "draws")}
        cell_summary: dict = {"draws": total, "blocks": len(block_rows), "reserve_blocks_used": 0, "counts": totals}
        if result_id == "RID-C003-IID-001":
            for key in ("reconstruction_success", "audit_pass"):
                cell_summary[key] = {"estimate": totals[key] / total,
                                     "wilson95": wilson_score_interval(totals[key], total),
                                     "hoeffding_half_width": hoeffding_half_width(total, 1.0),
                                     "block_min": min(r[key] / r["draws"] for r in block_rows),
                                     "block_max": max(r[key] / r["draws"] for r in block_rows)}
        elif result_id == "RID-C003-STRAT-001":
            cat = totals["catastrophic"]
            cell_summary["primary_D"] = {"estimate": totals["d_sum"] / total,
                                         "hoeffding_half_width": hoeffding_half_width(total, 2.0),
                                         "discordant_strat_better": totals["d_pos"],
                                         "discordant_unif_better": totals["d_neg"],
                                         "block_estimates": [r["d_sum"] / r["draws"] for r in block_rows]}
            cell_summary["catastrophic_rate"] = {"estimate": cat / total, "wilson95": wilson_score_interval(cat, total)}
            for policy, key in (("uniform", "z_unif"), ("stratified", "z_strat")):
                cell_summary[f"conditional_detection_{policy}"] = {
                    "estimate": totals[key] / cat, "wilson95": wilson_score_interval(totals[key], cat)}
            for policy, key in (("uniform", "pass_unif"), ("stratified", "pass_strat")):
                cell_summary[f"audit_pass_{policy}"] = {
                    "estimate": totals[key] / total, "wilson95": wilson_score_interval(totals[key], total)}
        else:
            cell_summary["primary_G"] = {"estimate": totals["gap_sum"] / total,
                                         "hoeffding_half_width": hoeffding_half_width(total, 2.0)}
            for key in ("audit_pass", "dispute_success"):
                cell_summary[key] = {"estimate": totals[key] / total,
                                     "wilson95": wilson_score_interval(totals[key], total)}
        summary[result_id] = cell_summary
        print(result_id, json.dumps({k: v for k, v in cell_summary.items() if k != "counts"}, default=str)[:600])

    (OUT / "pc03-summary.json").write_text(json.dumps(
        {"label": LABEL, "freeze_sha256": freeze_hash, "python": sys.version.split()[0], "cells": summary},
        indent=2) + "\n")


if __name__ == "__main__":
    main()
