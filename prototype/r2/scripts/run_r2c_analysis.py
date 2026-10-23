"""R2c: repair on alarm (M3) and selective withholding (M1), as frozen in
research-case/03-design/r2c-repair-withholding/r2c-design-freeze.json.

Checks the freeze hash and the R2 correctness suite, then writes to
research-case/05-analysis/results/r2c/: repair-grid.csv, repair-design.csv, repair-sim-check.csv,
withholding.csv, withholding-coalition.csv and r2c-environment.json.

Smoke mode (KEYSTONE_R2C_SMOKE_DIR set): one grid cell, one design row, 2,000 simulated
intervals per cell, outputs to that directory.
Run from prototype/r2:  uv run --locked --extra dev python -u scripts/run_r2c_analysis.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import random
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_r2_temporal import BATCHES, T_99_DF99, Chain, batch_means, make_model, shock_label, wilson  # noqa: E402

from keystone_r2 import temporal, withholding  # noqa: E402
from keystone_r2.temporal import DAY  # noqa: E402

R2_DIR = Path(__file__).resolve().parents[1]
ROOT = R2_DIR.parents[1]
DESIGN = ROOT / "research-case/03-design/r2c-repair-withholding"
SMOKE = os.environ.get("KEYSTONE_R2C_SMOKE_DIR")
OUT = Path(SMOKE) if SMOKE else ROOT / "research-case/05-analysis/results/r2c"
N, THRESHOLD = 32, 22


def freeze() -> tuple[str, dict]:
    raw = (DESIGN / "r2c-design-freeze.json").read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    recorded = (DESIGN / "r2c-design-freeze.SHA256SUMS").read_text().split()[0]
    if actual != recorded:
        sys.exit(f"ABORT: r2c-design-freeze.json hash {actual} != recorded {recorded}")
    return actual, json.loads(raw)


def require_correctness() -> None:
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=R2_DIR,
                            capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit("ABORT: R2 correctness tests failed\n" + result.stdout[-2000:])


def run_repair(fh: str, spec: dict) -> None:
    g = spec["grid"]
    shocks = [None] + [(d, g["domain_shock"]["MTTR_domain_hours"]) for d in g["domain_shock"]["MTBF_domain_days"]]
    designs = [tuple(d) for d in g["designs_s_q"]]
    cells = [(sh, mb, mr) for sh in shocks for mb in g["MTBF_days"] for mr in g["MTTR_hours"]]
    if SMOKE:
        cells, designs = cells[:1], designs[:1]
    with (OUT / "repair-grid.csv").open("w", newline="") as gf, (OUT / "repair-design.csv").open("w", newline="") as df:
        gw, dw = csv.writer(gf), csv.writer(df)
        gw.writerow(["freeze_sha256", "domain_shock", "mtbf_days", "mttr_hours", "T_hours", "repair_delay_hours", "s",
                     "q", "failure_with_repair", "undetected_with_repair", "failure_no_repair", "p_reject",
                     "repairs_per_day", "audits_per_day", "benign_fraction", "steps"])
        dw.writerow(["freeze_sha256", "domain_shock", "mtbf_days", "mttr_hours", "repair_delay_hours", "s", "q",
                     "target", "largest_grid_T_hours", "continuous_T_hours", "status", "monotone_on_check_grid",
                     "audits_per_day_at_T", "repairs_per_day_at_T", "benign_fraction_at_T"])
        for shock, mtbf, mttr in cells:
            model = make_model(mtbf, mttr, shock)
            base = temporal.stationary_catastrophic(model, THRESHOLD)
            for dr in g["repair_delay_hours"]:
                for s, q in designs:
                    per_T = {}
                    for T in g["audit_interval_hours"]:
                        r = temporal.repair_metrics(model, T, s, q, THRESHOLD, dr)
                        per_T[T] = r["failure"]
                        gw.writerow([fh, shock_label(shock), mtbf, mttr, T, dr, s, q, f"{r['failure']:.6e}",
                                     f"{r['undetected']:.6e}", f"{base:.6e}", f"{r['p_reject']:.6e}",
                                     f"{r['repairs_per_day']:.6e}", f"{r['audits_per_day']:.4f}",
                                     f"{r['benign_fraction']:.6f}", r["steps"]])
                    gf.flush()

                    warm = {"mu": None}

                    def metric(T: float) -> float:
                        r = temporal.repair_metrics(model, T, s, q, THRESHOLD, dr, start=warm["mu"])
                        warm["mu"] = r["stationary"]
                        return r["failure"]

                    lo_T, hi_T = max(spec["design"]["T_bracket_hours"][0], dr), spec["design"]["T_bracket_hours"][1]
                    check = [metric(T) for T in np.geomspace(lo_T, hi_T, spec["design"]["monotonicity_points"])]
                    monotone = all(b >= a * (1 - 1e-9) - 1e-18 for a, b in zip(check, check[1:]))
                    for target in spec["design"]["targets"]:
                        ok = [T for T in g["audit_interval_hours"] if per_T[T] <= target]
                        res = temporal.largest_interval(metric, target, lo_T, hi_T,
                                                        iterations=spec["design"]["bisection_iterations"])
                        if res["T"] is not None:
                            at = temporal.repair_metrics(model, res["T"], s, q, THRESHOLD, dr, start=warm["mu"])
                            extra = [f"{at['audits_per_day']:.4f}", f"{at['repairs_per_day']:.6e}",
                                     f"{at['benign_fraction']:.6f}"]
                        else:
                            extra = ["", "", ""]
                        dw.writerow([fh, shock_label(shock), mtbf, mttr, dr, s, q, target, max(ok) if ok else "",
                                     "" if res["T"] is None else f"{res['T']:.4f}", res["status"], monotone] + extra)
                    df.flush()
            print(f"repair {shock_label(shock):24s} MTBF {mtbf:>3}d MTTR {mttr:>2}h done", flush=True)


def simulate_repair(cell: dict, intervals: int, burn_in: int) -> dict:
    seed = int.from_bytes(hashlib.sha256(f"KEYSTONE-R2C|REPAIR|{cell['cell_id']}".encode()).digest()[:8], "big")
    rng = random.Random(seed)
    lam, mu = 1.0 / (cell["mtbf_days"] * DAY), 1.0 / cell["mttr_hours"]
    members = [Chain(rng, lam, mu) for _ in range(N)]
    shock = cell.get("mtbf_domain_days")
    domains = [] if shock is None else [Chain(rng, 1.0 / (shock * DAY), 1.0 / cell["mttr_domain_hours"])
                                        for _ in range(4)]
    s, q = cell["design"]
    T, dr = cell["T_hours"], cell["repair_delay_hours"]

    def ready_at(when: float) -> list[bool]:
        dom = [d.at(rng, when) for d in domains]
        return [c.at(rng, when) and (not dom or dom[i % 4]) for i, c in enumerate(members)]

    def reshare(when: float) -> None:
        for c in members:
            c.at(rng, when)
            c.up = True
            c.next = when + rng.expovariate(c.lam)

    rejected, failed, undetected = [], [], []
    for m in range(burn_in + intervals):
        a = m * T
        ready = ready_at(a)
        reject = sum(ready[i] for i in rng.sample(range(N), s)) < q
        u = rng.random() * T
        if reject and u >= dr:
            reshare(a + dr)
        cat = sum(ready_at(a + u)) < THRESHOLD
        if reject and u < dr:
            reshare(a + dr)
        if m >= burn_in:
            rejected.append(int(reject))
            failed.append(int(cat))
            undetected.append(int(cat and not reject))
    return {"seed": seed, "reject": rejected, "failure": failed, "undetected": undetected}


def run_repair_sim(fh: str, spec: dict) -> None:
    sim = spec["simulation_check"]
    intervals, burn_in = (2_000, 200) if SMOKE else (sim["intervals"], sim["burn_in"])
    with (OUT / "repair-sim-check.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["freeze_sha256", "cell_id", "seed", "quantity", "exact", "estimate", "successes", "trials",
                    "wilson99_lo", "wilson99_hi", "wilson_pass", "vacuous", "batch99_lo", "batch99_hi"])
        for cell in sim["cells"]:
            res = simulate_repair(cell, intervals, burn_in)
            shock = None if cell.get("mtbf_domain_days") is None else (cell["mtbf_domain_days"],
                                                                         cell["mttr_domain_hours"])
            model = make_model(cell["mtbf_days"], cell["mttr_hours"], shock)
            exact = temporal.repair_metrics(model, cell["T_hours"], *cell["design"], THRESHOLD,
                                            cell["repair_delay_hours"])
            for name, key, values in (("p_reject", "p_reject", res["reject"]), ("failure_with_repair", "failure",
                                      res["failure"]), ("undetected_with_repair", "undetected", res["undetected"])):
                lo, hi = wilson(sum(values), len(values))
                blo, bhi = batch_means(values) if len(values) >= 2 * BATCHES else (float("nan"), float("nan"))
                w.writerow([fh, cell["cell_id"], res["seed"], name, f"{exact[key]:.6e}",
                            f"{sum(values) / len(values):.6e}", sum(values), len(values), f"{lo:.6e}", f"{hi:.6e}",
                            lo <= exact[key] <= hi, sum(values) == 0, f"{blo:.6e}", f"{bhi:.6e}"])
            f.flush()
            print("sim", cell["cell_id"], "done", flush=True)


def run_withholding(fh: str, spec: dict) -> None:
    wh = spec["withholding"]
    with (OUT / "withholding.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["freeze_sha256", "v", "w", "dispute_success"] +
                   [f"audit_pass_s{s}q{q}" for s, q in wh["designs_s_q"]])
        for v in wh["v"]:
            for k in wh["w"]:
                w.writerow([fh, v, k, f"{withholding.dispute_success(N, THRESHOLD, k, v):.6e}"] +
                           [f"{withholding.audit_pass(N, s, q, k, v):.6f}" for s, q in wh["designs_s_q"]])
    with (OUT / "withholding-coalition.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["freeze_sha256", "v", "failure_target", "w_min", "p_a", "stake_to_value_ratio"])
        for v in wh["v"]:
            for target in wh["failure_targets"]:
                wmin = withholding.minimal_coalition(N, THRESHOLD, v, target)
                for pa in wh["attribution_probabilities"]:
                    ratio = "" if not wmin else f"{1.0 / (wmin * pa):.6f}"
                    w.writerow([fh, v, target, wmin, pa, ratio])


def main() -> None:
    fh, spec = freeze()
    require_correctness()
    OUT.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    run_withholding(fh, spec)
    run_repair_sim(fh, spec)
    run_repair(fh, spec)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    env = {"family": "R2C", "freeze_sha256": fh, "started_utc": started, "smoke": bool(SMOKE),
           "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "git_commit": commit,
           "python": sys.version.split()[0], "numpy": metadata.version("numpy"), "host": platform.platform(),
           "batch_means": {"batches": BATCHES, "t_99": T_99_DF99}}
    (OUT / "r2c-environment.json").write_text(json.dumps(env, indent=2) + "\n")


if __name__ == "__main__":
    main()
