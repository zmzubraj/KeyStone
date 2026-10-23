"""Analysis of R2_DEADLINE_TESTBED, as frozen in r2-design-freeze.json.

Reads research-case/05-analysis/results/r2/deadline/{SERIAL,BATCH}/<profile>.csv and writes
deadline-summary.csv next to them. Checks first: freeze and deadline-record hashes, 300 rows
per file, trace seeds equal to the frozen formula, and meta files stamped with both hashes.

Per variant and profile:
* primary endpoint: Pr[dispute decrypts the correct plaintext by Delta_d_star] (primary
  deadline of r2-deadline-record.json, deviation entry 4), Wilson 95%;
* the same for the secondary (frozen single-leg) deadline and for the fixed deadlines
  0.05, 0.1, 0.25, 0.5, 1, 2, 5 s;
* completion-time median and 95th percentile as order statistics over all traces, failed
  traces counted as +inf (a quantile that falls on a failure is reported as "censored"),
  with distribution-free 95% order-statistic intervals;
* audit pass rate (s = q = 8) versus the exact expectation: sampling avoids silent members
  (hypergeometric), no loss on either leg of the 8 sampled requests, and request plus
  response delay below the 6 s timeout (numerical convolution of the two lognormal legs).

Run from prototype/r2:  uv run --locked --extra dev python scripts/analyze_r2_deadline.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

R2_DIR = Path(__file__).resolve().parents[1]
ROOT = R2_DIR.parents[1]
DESIGN = ROOT / "research-case/03-design/r2-design-amendment"
RESULTS = ROOT / "research-case/05-analysis/results/r2/deadline"
VARIANTS = ("SERIAL", "BATCH")
FIXED_DEADLINES_S = (0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0)
Z95 = 1.959963984540054
N, S_AUDIT = 32, 8


def check_sums(sums_name: str, file_name: str) -> str:
    actual = hashlib.sha256((DESIGN / file_name).read_bytes()).hexdigest()
    recorded = next(line.split()[0] for line in (DESIGN / sums_name).read_text().splitlines()
                    if line.endswith(file_name))
    if actual != recorded:
        sys.exit(f"ABORT: {file_name} hash {actual} != recorded {recorded}")
    return actual


def wilson(k: int, n: int) -> tuple[float, float]:
    p, z2 = k / n, Z95**2
    centre = (p + z2 / (2 * n)) / (1 + z2 / n)
    half = Z95 * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / (1 + z2 / n)
    # The Wilson bounds at k = 0 and k = n are exactly 0 and 1; avoid rounding just inside them.
    return (0.0 if k == 0 else max(0.0, centre - half)), (1.0 if k == n else min(1.0, centre + half))


def order_quantile(times: list[float], p: float) -> tuple[float, float, float]:
    """Order-statistic quantile with a distribution-free 95% interval; inf marks failures."""
    xs, n = sorted(times), len(times)
    point = xs[math.ceil(p * n) - 1]
    cdf = np.cumsum([math.comb(n, j) * p**j * (1 - p) ** (n - j) for j in range(n + 1)])
    lo_rank = int(np.searchsorted(cdf, 0.025))       # largest j with Pr[Bin < j] <= 0.025, 0-based
    hi_rank = min(int(np.searchsorted(cdf, 0.975)), n - 1)
    return point, xs[max(lo_rank - 1, 0)], xs[hi_rank]


def leg_timeout_probability(median_ms: float, sigma: float, timeout_s: float) -> float:
    """Pr[request + response delay >= timeout] for two independent lognormal legs."""
    if median_ms == 0:
        return 0.0
    mu, c = math.log(median_ms / 1000), timeout_s
    xs = np.linspace(1e-9, c, 200_001)
    z = (np.log(xs) - mu) / sigma
    pdf = np.exp(-0.5 * z**2) / (xs * sigma * math.sqrt(2 * math.pi))
    tail_y = 0.5 * np.array([math.erfc(((math.log(c - x) - mu) / sigma) / math.sqrt(2)) if x < c else 1.0
                             for x in xs])
    inside = np.trapezoid(pdf * tail_y, xs)
    tail_x = 0.5 * math.erfc(((math.log(c) - mu) / sigma) / math.sqrt(2))
    return float(inside + tail_x)


def audit_expectation(profile: dict, timeout_s: float) -> float:
    silent = profile["crashed"] + (8 if profile["domain_outage"] else 0)
    sample_ok = math.comb(N - silent, S_AUDIT) / math.comb(N, S_AUDIT)
    per_member = (1 - profile["loss"]) ** 2 * (1 - leg_timeout_probability(profile["median_ms"], profile["sigma"],
                                                                           timeout_s))
    return sample_ok * per_member**S_AUDIT


def fmt_time(x: float) -> str:
    return "censored" if math.isinf(x) else f"{x:.4f}"


def main() -> None:
    freeze_hash = check_sums("r2-design-freeze.SHA256SUMS", "r2-design-freeze.json")
    record_hash = check_sums("r2-deadline-record.SHA256SUMS", "r2-deadline-record.json")
    spec = json.loads((DESIGN / "r2-design-freeze.json").read_text())["families"]["R2_DEADLINE_TESTBED"]
    record = json.loads((DESIGN / "r2-deadline-record.json").read_text())["profiles"]
    timeout = spec["hard_timeout_s"]
    rows = []
    for variant in VARIANTS:
        for profile_id, profile in spec["profiles"].items():
            meta = json.loads((RESULTS / variant / f"{profile_id}.meta.json").read_text())
            if meta["freeze_sha256"] != freeze_hash or meta["deadline_record_sha256"] != record_hash:
                sys.exit(f"ABORT: {variant}/{profile_id} meta not stamped with the current hashes")
            with (RESULTS / variant / f"{profile_id}.csv").open() as f:
                data = list(csv.DictReader(f))
            if len(data) != spec["traces_per_profile"]:
                sys.exit(f"ABORT: {variant}/{profile_id} has {len(data)} rows")
            for i, row in enumerate(data):
                seed = int.from_bytes(hashlib.sha256(
                    f"KEYSTONE-R2|DEADLINE|{variant}|{profile_id}|{i}".encode()).digest()[:8], "big")
                if int(row["trace"]) != i or int(row["seed"]) != seed:
                    sys.exit(f"ABORT: {variant}/{profile_id} trace {i} seed mismatch")
            n = len(data)
            times = [float(r["dispute_time_s"]) if r["dispute_success"] == "True" else math.inf for r in data]
            primary_s = record[profile_id]["primary_delta_d_star_ms"] / 1000
            secondary_s = record[profile_id]["secondary_frozen_delta_d_star_ms"] / 1000
            out = {"freeze_sha256": freeze_hash, "deadline_record_sha256": record_hash, "variant": variant,
                   "profile_id": profile_id, "traces": n,
                   "dispute_success_any_time": sum(not math.isinf(x) for x in times)}
            for name, deadline in [("primary", primary_s), ("secondary", secondary_s)] + \
                    [(f"at_{d:g}s", d) for d in FIXED_DEADLINES_S]:
                k = sum(x <= deadline for x in times)
                lo, hi = wilson(k, n)
                out[f"{name}_deadline_s"] = f"{deadline:.6f}"
                out[f"{name}_success"] = k
                out[f"{name}_rate"] = f"{k / n:.4f}"
                out[f"{name}_wilson95"] = f"[{lo:.4f}, {hi:.4f}]"
            for label, p in (("median", 0.5), ("p95", 0.95)):
                point, lo, hi = order_quantile(times, p)
                out[f"completion_{label}_s"] = fmt_time(point)
                out[f"completion_{label}_ci95_s"] = f"[{fmt_time(lo)}, {fmt_time(hi)}]"
            passes = sum(r["audit_pass"] == "True" for r in data)
            lo, hi = wilson(passes, n)
            expected = audit_expectation(profile, timeout)
            out.update({"audit_pass": passes, "audit_pass_rate": f"{passes / n:.4f}",
                        "audit_pass_wilson95": f"[{lo:.4f}, {hi:.4f}]", "audit_pass_expected": f"{expected:.4f}",
                        "audit_expected_in_wilson95": lo <= expected <= hi})
            rows.append(out)
    path = RESULTS / "deadline-summary.csv"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
