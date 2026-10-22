"""R2_TEMPORAL_EXACT and R2_TEMPORAL_SIM_CHECK: W1 temporal readiness analysis.

Implements the two temporal families of research-case/03-design/r2-design-amendment/
r2-design-freeze.json with keystone_r2.temporal. Before running, the script checks the
freeze hash and runs the R2 correctness suite.

Exact analysis (label EXACT_UNDER_DECLARED_SYNTHETIC_MODEL), committee n=32, t=22, over the
frozen grid (MTBF x MTTR x audit interval T x design), without domain shocks and with each
frozen domain-shock setting:

* metric 1: sup over the dispute offset u of Pr[K < t | all audits accepted] at the filter's
  fixed point (96 + 1 points on [0, T]);
* metric 2: stationary Pr[K < t and most recent audit accepted], u uniform on [0, T);
* design: per risk target, the largest grid T meeting it, and the largest continuous T by
  bisection on log T over [0.25 h, 30 d] (metric 1 with a 24 + 1 point offset grid), with
  monotonicity checked on 25 log-spaced points; for the model without shocks also the
  interval from the closed-form bound of Theorem 5, which is provably non-decreasing in T.

Simulation check (label SIMULATION_IMPLEMENTATION_CHECK): an event-driven simulation with
exponential holding times, independent of the closed forms, on the three frozen cells;
200,000 recorded intervals after 10,000 burn-in; each estimate against the exact value with
a 99% Wilson interval (the frozen criterion) and, as a diagnostic for autocorrelation, a 99%
batch-means interval (100 batches).

Outputs go to research-case/05-analysis/results/r2/temporal/, each row stamped with the
freeze hash. Run from prototype/r2:
    uv run --locked --extra dev python -u scripts/run_r2_temporal.py [exact|sim|all]
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import random
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

import numpy as np

from keystone_r2 import temporal
from keystone_r2.temporal import DAY, DomainShockModel, IndependentModel

R2_DIR = Path(__file__).resolve().parents[1]
ROOT = R2_DIR.parents[1]
DESIGN = ROOT / "research-case/03-design/r2-design-amendment"
OUT = ROOT / "research-case/05-analysis/results/r2/temporal"
N, THRESHOLD = 32, 22
TARGETS = (1e-2, 1e-3, 1e-4)
T_LO, T_HI = 0.25, 30 * DAY
WILSON_Z = 2.5758293035489004  # 99%
BATCHES, T_99_DF99 = 100, 2.6264054563851857
RUN_LENGTH = 8  # metric-1 surrogate in the simulation: last RUN_LENGTH audits accepted
K_MIN_PROB = 1e-3  # occupancy of K at audit times is checked for k with exact probability >= this


def freeze() -> tuple[str, dict]:
    raw = (DESIGN / "r2-design-freeze.json").read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    recorded = next(line.split()[0] for line in (DESIGN / "r2-design-freeze.SHA256SUMS").read_text().splitlines()
                    if line.endswith("r2-design-freeze.json"))
    if actual != recorded:
        sys.exit(f"ABORT: r2-design-freeze.json hash {actual} != recorded {recorded}")
    return actual, json.loads(raw)["families"]


def require_correctness() -> None:
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=R2_DIR,
                            capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit("ABORT: R2 correctness tests failed\n" + result.stdout[-2000:])


def make_model(mtbf_days: float, mttr_hours: float, shock: tuple[float, float] | None):
    lam, mu = 1.0 / (mtbf_days * DAY), 1.0 / mttr_hours
    if shock is None:
        return IndependentModel(N, lam, mu)
    return DomainShockModel(N, lam, mu, 1.0 / (shock[0] * DAY), 1.0 / shock[1], domains=4)


def shock_label(shock: tuple[float, float] | None) -> str:
    return "none" if shock is None else f"MTBF_d={shock[0]:g}d,MTTR_d={shock[1]:g}h"


# ------------------------------------------------------------------ exact grid and design
def run_exact(freeze_hash: str, spec: dict) -> None:
    grid = spec["grid"]
    shocks = [None] + [(d, r) for d in grid["domain_shock"]["MTBF_domain_days"]
                       for r in grid["domain_shock"]["MTTR_domain_hours"]]
    designs = [tuple(d) for d in grid["designs_s_q"]]
    grid_path, design_path = OUT / "exact-grid.csv", OUT / "design.csv"
    with grid_path.open("w", newline="") as gf, design_path.open("w", newline="") as df:
        gw, dw = csv.writer(gf), csv.writer(df)
        gw.writerow(["freeze_sha256", "domain_shock", "mtbf_days", "mttr_hours", "T_hours", "s", "q",
                     "metric1_posterior_worst", "metric1_u_worst_hours", "metric1_at_audit", "metric1_monotone_in_u",
                     "fixed_point_steps", "metric2_undetected", "metric2_floor_T0", "metric2_bound_closed_form",
                     "stationary_catastrophic", "stationary_accept"])
        dw.writerow(["freeze_sha256", "domain_shock", "mtbf_days", "mttr_hours", "s", "q", "metric", "target",
                     "largest_grid_T_hours", "continuous_T_hours", "status", "monotone_on_check_grid"])
        for shock in shocks:
            for mtbf in grid["MTBF_days"]:
                for mttr in grid["MTTR_hours"]:
                    model = make_model(mtbf, mttr, shock)
                    cat = temporal.stationary_catastrophic(model, THRESHOLD)
                    for s, q in designs:
                        accept_rate = float((model.stationary() * temporal.emission(model, s, q)).sum())
                        floor = temporal.undetected_floor(model, s, q, THRESHOLD)
                        per_T = {}
                        for T in grid["audit_interval_hours"]:
                            m1 = temporal.posterior_worst_risk(model, T, s, q, THRESHOLD)
                            m2 = temporal.stationary_undetected(model, T, s, q, THRESHOLD)
                            bound = ("" if shock is not None else
                                     f"{temporal.undetected_bound(N, model.lam, model.mu, T, s, q, THRESHOLD):.6e}")
                            per_T[T] = (m1["risk"], m2, float(bound) if bound else None)
                            gw.writerow([freeze_hash, shock_label(shock), mtbf, mttr, T, s, q, f"{m1['risk']:.6e}",
                                         f"{m1['u_worst']:.4f}", f"{m1['risk_at_audit']:.6e}", m1["monotone_in_u"],
                                         m1["steps"], f"{m2:.6e}", f"{floor:.6e}", bound, f"{cat:.6e}",
                                         f"{accept_rate:.6f}"])
                        gf.flush()
                        for metric_name, index, fn in design_metrics(model, s, q):
                            check = [fn(T) for T in np.geomspace(T_LO, T_HI, 25)]
                            monotone = all(b >= a * (1 - 1e-9) - 1e-18 for a, b in zip(check, check[1:]))
                            for target in TARGETS:
                                ok = [T for T in grid["audit_interval_hours"] if per_T[T][index] <= target]
                                result = temporal.largest_interval(fn, target, T_LO, T_HI)
                                dw.writerow([freeze_hash, shock_label(shock), mtbf, mttr, s, q, metric_name, target,
                                             max(ok) if ok else "", "" if result["T"] is None else
                                             f"{result['T']:.4f}", result["status"], monotone])
                        df.flush()
                        print(f"exact {shock_label(shock):24s} MTBF {mtbf:>3}d MTTR {mttr:>2}h ({s},{q}) done",
                              flush=True)


def design_metrics(model, s: int, q: int):
    """Metric functions of T for the bisection; metric 1 warm-starts the fixed point from the last T."""
    state = {"start": None}

    def metric1(T: float) -> float:
        result = temporal.posterior_worst_risk(model, T, s, q, THRESHOLD, points=24, start=state["start"])
        state["start"] = result["fixed_point"]
        return result["risk"]

    def metric2(T: float) -> float:
        return temporal.stationary_undetected(model, T, s, q, THRESHOLD)

    metrics = [("metric1_posterior_worst", 0, metric1), ("metric2_undetected", 1, metric2)]
    if isinstance(model, IndependentModel):
        # Theorem 5 bound: non-decreasing in T, so the bisected interval is a guaranteed (conservative) design.
        metrics.append(("metric2_bound_closed_form", 2,
                        lambda T: temporal.undetected_bound(N, model.lam, model.mu, T, s, q, THRESHOLD)))
    return metrics


# ------------------------------------------------------------------ simulation check
SIM_CELLS = [
    ("MTBF30d-MTTR6h-T6h-s8q8", 30, 6, 6, (8, 8), None),
    ("MTBF7d-MTTR24h-T24h-s16q14", 7, 24, 24, (16, 14), None),
    ("MTBF30d-MTTR6h-T6h-s16q14-domainMTBF90d", 30, 6, 6, (16, 14), (90, 6)),
]


class Chain:
    """Two-state chain with exponential holding times (up -> down at ``lam``, down -> up at ``mu``)."""

    __slots__ = ("lam", "mu", "up", "next")

    def __init__(self, rng: random.Random, lam: float, mu: float) -> None:
        self.lam, self.mu = lam, mu
        self.up = rng.random() < mu / (lam + mu)
        self.next = rng.expovariate(lam if self.up else mu)

    def at(self, rng: random.Random, when: float) -> bool:
        while self.next <= when:
            self.up = not self.up
            self.next += rng.expovariate(self.lam if self.up else self.mu)
        return self.up


def wilson(successes: int, trials: int) -> tuple[float, float]:
    if trials == 0:
        return 0.0, 1.0
    p, z2 = successes / trials, WILSON_Z**2
    centre = (p + z2 / (2 * trials)) / (1 + z2 / trials)
    half = WILSON_Z * math.sqrt(p * (1 - p) / trials + z2 / (4 * trials**2)) / (1 + z2 / trials)
    return max(0.0, centre - half), min(1.0, centre + half)


def batch_means(values: list[int]) -> tuple[float, float]:
    size = len(values) // BATCHES
    means = [sum(values[b * size:(b + 1) * size]) / size for b in range(BATCHES)]
    centre, sd = statistics.fmean(means), statistics.stdev(means)
    half = T_99_DF99 * sd / math.sqrt(BATCHES)
    return centre - half, centre + half


def simulate(cell_id: str, mtbf: float, mttr: float, T: float, design: tuple[int, int], shock, intervals: int,
             burn_in: int) -> dict:
    s, q = design
    seed = int.from_bytes(hashlib.sha256(f"KEYSTONE-R2|TEMPORAL|{cell_id}".encode()).digest()[:8], "big")
    rng = random.Random(seed)
    lam, mu = 1.0 / (mtbf * DAY), 1.0 / mttr
    members = [Chain(rng, lam, mu) for _ in range(N)]
    domains = [] if shock is None else [Chain(rng, 1.0 / (shock[0] * DAY), 1.0 / shock[1]) for _ in range(4)]

    def ready_at(when: float) -> list[bool]:
        dom = [d.at(rng, when) for d in domains]
        return [c.at(rng, when) and (not dom or dom[i % 4]) for i, c in enumerate(members)]

    accepted, undetected, catastrophic, k_at_audit, after_run = [], [], [], [], []
    run = 0
    for m in range(burn_in + intervals):
        ready = ready_at(m * T)
        accept = sum(ready[i] for i in rng.sample(range(N), s)) >= q
        run = run + 1 if accept else 0
        u = rng.random() * T
        cat = sum(ready_at(m * T + u)) < THRESHOLD
        if m < burn_in:
            continue
        accepted.append(int(accept))
        undetected.append(int(accept and cat))
        catastrophic.append(int(cat))
        k_at_audit.append(sum(ready))
        if run >= RUN_LENGTH:
            after_run.append(int(cat))
    return {"seed": seed, "accepted": accepted, "undetected": undetected, "catastrophic": catastrophic,
            "k_at_audit": k_at_audit, "after_run": after_run}


def run_sim(freeze_hash: str, spec: dict) -> None:
    intervals, burn_in = 200_000, 10_000
    path = OUT / "sim-check.csv"
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["freeze_sha256", "cell_id", "seed", "quantity", "exact", "estimate", "successes", "trials",
                     "wilson99_lo", "wilson99_hi", "wilson_pass", "batch99_lo", "batch99_hi", "batch_pass"])
        for cell_id, mtbf, mttr, T, (s, q), shock in SIM_CELLS:
            started = time.time()
            sim = simulate(cell_id, mtbf, mttr, T, (s, q), shock, intervals, burn_in)
            model = make_model(mtbf, mttr, shock)
            pi_k = [float(model.stationary()[model.ready == k].sum()) for k in range(N + 1)]
            checks = [
                ("pr_accept", float((model.stationary() * temporal.emission(model, s, q)).sum()), sim["accepted"]),
                ("metric2_undetected", temporal.stationary_undetected(model, T, s, q, THRESHOLD), sim["undetected"]),
                ("stationary_catastrophic", temporal.stationary_catastrophic(model, THRESHOLD), sim["catastrophic"]),
                (f"after_run{RUN_LENGTH}_risk", temporal.after_run_risk(model, T, s, q, THRESHOLD, RUN_LENGTH),
                 sim["after_run"]),
            ]
            checks += [(f"K_at_audit={k}", pi_k[k], [int(x == k) for x in sim["k_at_audit"]])
                       for k in range(N + 1) if pi_k[k] >= K_MIN_PROB]
            for name, exact, values in checks:
                lo, hi = wilson(sum(values), len(values))
                blo, bhi = batch_means(values) if len(values) >= BATCHES * 2 else (float("nan"), float("nan"))
                w.writerow([freeze_hash, cell_id, sim["seed"], name, f"{exact:.6e}",
                            f"{sum(values) / max(len(values), 1):.6e}", sum(values), len(values), f"{lo:.6e}",
                            f"{hi:.6e}", lo <= exact <= hi, f"{blo:.6e}", f"{bhi:.6e}", blo <= exact <= bhi])
            f.flush()
            print(f"sim {cell_id} done in {time.time() - started:.1f} s", flush=True)


def main() -> None:
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which not in ("exact", "sim", "all"):
        sys.exit(f"usage: {Path(__file__).name} [exact|sim|all]")
    freeze_hash, families = freeze()
    require_correctness()
    OUT.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if which in ("exact", "all"):
        run_exact(freeze_hash, families["R2_TEMPORAL_EXACT"])
    if which in ("sim", "all"):
        run_sim(freeze_hash, families["R2_TEMPORAL_SIM_CHECK"])
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    env = {"families": ["R2_TEMPORAL_EXACT", "R2_TEMPORAL_SIM_CHECK"], "part": which, "freeze_sha256": freeze_hash,
           "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "git_commit": commit, "committee": {"n": N, "t": THRESHOLD}, "targets": TARGETS,
           "continuous_T_bracket_hours": [T_LO, T_HI], "metric1_offset_points": {"grid": 97, "bisection": 25},
           "sim_run_length": RUN_LENGTH, "sim_k_min_prob": K_MIN_PROB, "python": sys.version.split()[0],
           "numpy": metadata.version("numpy"), "host": platform.platform(),
           "labels": {"exact": families["R2_TEMPORAL_EXACT"]["label"],
                      "sim": families["R2_TEMPORAL_SIM_CHECK"]["label"]}}
    (OUT / f"temporal-{which}-environment.json").write_text(json.dumps(env, indent=2) + "\n")


if __name__ == "__main__":
    main()
