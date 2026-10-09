#!/usr/bin/env python3
"""Exact analytic families for KEYSTONE revision R1.

Computes (1) IID versus domain-correlated reconstructability and audit pass,
(2) the post hoc audit-acceptance sensitivity over q, and (3) the scalability
detection grid. All values are closed-form under the declared models in
``r1-design-freeze.json``; a seeded Monte Carlo cross-check validates the
domain-model code only.
"""

from __future__ import annotations

import csv
import json
from math import comb
from pathlib import Path
import random
import sys

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
sys.path.insert(0, str(PROJECT / "scripts"))

from run_r1_pc03 import freeze_sha256  # noqa: E402

OUT = ROOT / "research-case/05-analysis/results/r1"
N, T, S, Q = 32, 22, 8, 8
GRID = [round(0.025 * i, 3) for i in range(17)]
DOMAIN_MODELS = {"DOMAIN_2x16": 2, "DOMAIN_4x8": 4, "DOMAIN_8x4": 8}


def binom_pmf(k: int, n: int, p: float) -> float:
    return comb(n, k) * p**k * (1 - p) ** (n - k)


def hyper_tail(ready: int, n: int, s: int, q: int) -> float:
    """P[at least q ready members in a uniform sample of s from n]."""
    return sum(comb(ready, j) * comb(n - ready, s - j) for j in range(q, min(s, ready) + 1)) / comb(n, s)


def iid_exact(f: float, s: int = S, q: int = Q) -> tuple[float, float]:
    recon = sum(binom_pmf(k, N, 1 - f) for k in range(T, N + 1))
    audit = sum(binom_pmf(j, s, 1 - f) for j in range(q, s + 1))
    return recon, audit


def domain_exact(f: float, domains: int) -> tuple[float, float]:
    size = N // domains
    recon = audit = 0.0
    for down in range(domains + 1):
        weight = binom_pmf(down, domains, f)
        ready = size * (domains - down)
        recon += weight * (ready >= T)
        audit += weight * hyper_tail(ready, N, S, Q)
    return recon, audit


def domain_monte_carlo(f: float, domains: int, seed: int, draws: int = 20000) -> tuple[float, float]:
    rng = random.Random(seed)
    recon = audit = 0
    for _ in range(draws):
        down = {d for d in range(domains) if rng.random() < f}
        ready = [m % domains not in down for m in range(N)]
        recon += sum(ready) >= T
        audit += sum(ready[i] for i in rng.sample(range(N), S)) >= Q
    return recon / draws, audit / draws


def main() -> None:
    freeze_hash = freeze_sha256()
    OUT.mkdir(parents=True, exist_ok=True)

    rows = []
    for f in GRID:
        recon, audit = iid_exact(f)
        rows.append({"model": "IID", "unavailability": f, "reconstructability": recon, "audit_pass": audit})
        for name, domains in DOMAIN_MODELS.items():
            recon, audit = domain_exact(f, domains)
            rows.append({"model": name, "unavailability": f, "reconstructability": recon, "audit_pass": audit})
    with (OUT / "analytic-domain-correlation.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    checks = []
    for index, (name, domains) in enumerate(DOMAIN_MODELS.items()):
        for f in (0.10, 0.20):
            exact = domain_exact(f, domains)
            simulated = domain_monte_carlo(f, domains, 20261009 + index)
            checks.append({"model": name, "unavailability": f,
                           "exact_reconstructability": exact[0], "mc_reconstructability": simulated[0],
                           "exact_audit_pass": exact[1], "mc_audit_pass": simulated[1],
                           "max_abs_error": max(abs(exact[0] - simulated[0]), abs(exact[1] - simulated[1]))})
    with (OUT / "analytic-domain-mc-check.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(checks[0]))
        writer.writeheader()
        writer.writerows(checks)

    sensitivity = []
    # s=8, q=5..8 is the frozen grid; s=12 and s=16 are deviation #1 (post hoc extension).
    for s in (8, 12, 16):
        for q in range((s + 1) // 2, s + 1):
            if s == 8 and q < 5:
                continue
            row = {"s": s, "q": q, "frozen_grid": s == 8,
                   "worst_case_detection": 1 - hyper_tail(T - 1, N, s, q)}
            for f in (0.05, 0.10, 0.20):
                row[f"benign_audit_pass_iid_{f:.2f}"] = iid_exact(f, s, q)[1]
            sensitivity.append(row)
    with (OUT / "analytic-acceptance-sensitivity.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sensitivity[0]))
        writer.writeheader()
        writer.writerows(sensitivity)

    scal = []
    for n in (16, 32, 64, 128):
        t = n - (n - 1) // 3
        for s in (4, 8, 12, 16):
            false_accept = comb(t - 1, s) / comb(n, s)
            scal.append({"n": n, "t": t, "s": s, "q": s, "worst_case_false_accept": false_accept,
                         "worst_case_detection": 1 - false_accept})
    with (OUT / "analytic-scalability-detection.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(scal[0]))
        writer.writeheader()
        writer.writerows(scal)

    (OUT / "analytic-manifest.json").write_text(json.dumps({
        "freeze_sha256": freeze_hash,
        "labels": {"analytic-domain-correlation.csv": "EXACT_ANALYTIC_DECLARED_SYNTHETIC_MODEL",
                   "analytic-domain-mc-check.csv": "CODE_VALIDATION_ONLY",
                   "analytic-acceptance-sensitivity.csv": "POST_HOC_EXACT_ANALYTIC",
                   "analytic-scalability-detection.csv": "EXACT_ANALYTIC"},
        "max_mc_abs_error": max(c["max_abs_error"] for c in checks)}, indent=2) + "\n")
    for row in sensitivity:
        print(row)
    print("max MC abs error", max(c["max_abs_error"] for c in checks))


if __name__ == "__main__":
    main()
