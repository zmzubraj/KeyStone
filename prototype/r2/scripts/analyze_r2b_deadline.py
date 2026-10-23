"""Analysis of R2B_DEADLINE_REPLICATION as frozen in r2b-design-freeze.json.

Checks hashes, row counts and the shared seeds, then writes
research-case/05-analysis/results/r2b/deadline/r2b-summary.csv (per variant and profile) and
r2b-paired.csv (SERIAL vs BATCH per profile).

Run from prototype/r2:  uv run --locked --extra dev python scripts/analyze_r2b_deadline.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_r2_deadline import FIXED_DEADLINES_S, audit_expectation, fmt_time, order_quantile, wilson  # noqa: E402

from keystone_r2 import deadline_model as dm  # noqa: E402

R2_DIR = Path(__file__).resolve().parents[1]
ROOT = R2_DIR.parents[1]
DESIGN = ROOT / "research-case/03-design/r2b-replication"
R2_DESIGN = ROOT / "research-case/03-design/r2-design-amendment"
RESULTS = ROOT / "research-case/05-analysis/results/r2b/deadline"
VARIANTS = ("SERIAL", "BATCH")
T = 22


def check(name: str) -> str:
    actual = hashlib.sha256((DESIGN / name).read_bytes()).hexdigest()
    recorded = next(l.split()[0] for l in (DESIGN / "r2b-design-freeze.SHA256SUMS").read_text().splitlines()
                    if l.endswith(name))
    if actual != recorded:
        sys.exit(f"ABORT: {name} hash mismatch")
    return actual


def exact_two_sided_binomial(k: int, n: int) -> float:
    """Exact two-sided p-value of k successes in n fair trials (McNemar and sign tests)."""
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2**n
    return min(1.0, 2 * tail)


def main() -> None:
    freeze_hash, record_hash = check("r2b-design-freeze.json"), check("r2b-deadline-record.json")
    freeze = json.loads((DESIGN / "r2b-design-freeze.json").read_text())
    record = json.loads((DESIGN / "r2b-deadline-record.json").read_text())
    r2_record = json.loads((R2_DESIGN / "r2-deadline-record.json").read_text())
    spec = freeze["testbed"]
    fixed_r2 = r2_record["inputs_ms"]["c_p"] + T * r2_record["inputs_ms"]["c_v"] + r2_record["inputs_ms"]["c_c"]
    b0 = record["B0_ms"]
    data: dict[tuple[str, str], list[dict]] = {}
    rows = []
    for variant in VARIANTS:
        for pid, profile in spec["profiles"].items():
            meta = json.loads((RESULTS / variant / f"{pid}.meta.json").read_text())
            if meta["freeze_sha256"] != freeze_hash or meta["deadline_record_sha256"] != record_hash:
                sys.exit(f"ABORT: {variant}/{pid} meta not stamped with the R2B hashes")
            with (RESULTS / variant / f"{pid}.csv").open() as f:
                traces = list(csv.DictReader(f))
            if len(traces) != spec["traces_per_profile"]:
                sys.exit(f"ABORT: {variant}/{pid} has {len(traces)} rows")
            for i, r in enumerate(traces):
                seed = int.from_bytes(hashlib.sha256(f"KEYSTONE-R2B|DEADLINE|{pid}|{i}".encode()).digest()[:8], "big")
                if int(r["trace"]) != i or int(r["seed"]) != seed:
                    sys.exit(f"ABORT: {variant}/{pid} trace {i} seed mismatch")
            data[(variant, pid)] = traces
            n = len(traces)
            times = [1000 * float(r["dispute_time_s"]) if r["dispute_success"] == "True" else math.inf for r in traces]
            info = record["profiles"][pid]
            live = info["n_live"]
            deadline = info["delta_os_ms"]
            if deadline is None:
                k = sum(not math.isinf(x) for x in times)
                criterion = k == 0
                pred_os = 0.0
            else:
                k = sum(x <= deadline for x in times)
                criterion = wilson(k, n)[1] >= 0.99
                pred_os = dm.success_probability(deadline, live, T, profile["median_ms"], profile["sigma"],
                                                 profile["loss"], b0)
            lo, hi = wilson(k, n)
            d_star = r2_record["profiles"][pid]["primary_delta_d_star_ms"]
            k_star = sum(x <= d_star for x in times)
            lo_s, hi_s = wilson(k_star, n)
            pred_star = dm.success_probability(d_star, live, T, profile["median_ms"], profile["sigma"],
                                               profile["loss"], b0)
            out = {"freeze_sha256": freeze_hash, "variant": variant, "profile_id": pid, "traces": n,
                   "delta_os_ms": "none" if deadline is None else f"{deadline:.3f}",
                   "success_by_delta_os": k, "rate": f"{k / n:.4f}", "wilson95": f"[{lo:.4f}, {hi:.4f}]",
                   "meets_criterion": criterion, "model_predicted_at_delta_os": f"{pred_os:.4f}",
                   "model_in_wilson95": lo <= pred_os <= hi,
                   "r2_delta_d_star_ms": f"{d_star:.3f}", "success_by_r2_delta_d_star": k_star,
                   "rate_at_r2_delta_d_star": f"{k_star / n:.4f}",
                   "wilson95_at_r2_delta_d_star": f"[{lo_s:.4f}, {hi_s:.4f}]",
                   "model_predicted_at_r2_delta_d_star_with_B0": f"{pred_star:.4f}",
                   "model_predicted_at_r2_delta_d_star_frozen_terms": f"{dm.success_probability(d_star, live, T, profile['median_ms'], profile['sigma'], profile['loss'], fixed_r2):.4f}" if profile["median_ms"] else "undefined (zero slack)"}
            for d in FIXED_DEADLINES_S:
                out[f"rate_at_{d:g}s"] = f"{sum(x <= 1000 * d for x in times) / n:.4f}"
            for label, p in (("median", 0.5), ("p95", 0.95)):
                point, qlo, qhi = order_quantile([x / 1000 for x in times], p)
                out[f"completion_{label}_s"] = fmt_time(point)
                out[f"completion_{label}_ci95_s"] = f"[{fmt_time(qlo)}, {fmt_time(qhi)}]"
            passes = sum(r["audit_pass"] == "True" for r in traces)
            alo, ahi = wilson(passes, n)
            expected = audit_expectation(profile, spec["hard_timeout_s"])
            out.update({"audit_pass_rate": f"{passes / n:.4f}", "audit_wilson95": f"[{alo:.4f}, {ahi:.4f}]",
                        "audit_expected": f"{expected:.4f}", "audit_expected_in_wilson95": alo <= expected <= ahi})
            rows.append(out)
    with (RESULTS / "r2b-summary.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    paired = []
    for pid in spec["profiles"]:
        deadline = record["profiles"][pid]["delta_os_ms"]
        s, b = data[("SERIAL", pid)], data[("BATCH", pid)]

        def ok(r, dl=deadline):
            if r["dispute_success"] != "True":
                return False
            return dl is None or 1000 * float(r["dispute_time_s"]) <= dl

        only_serial = sum(ok(x) and not ok(y) for x, y in zip(s, b))
        only_batch = sum(ok(y) and not ok(x) for x, y in zip(s, b))
        diffs = [1000 * (float(y["dispute_time_s"]) - float(x["dispute_time_s"])) for x, y in zip(s, b)
                 if x["dispute_success"] == "True" and y["dispute_success"] == "True"]
        positive = sum(d > 0 for d in diffs)
        nonzero = sum(d != 0 for d in diffs)
        paired.append({"freeze_sha256": freeze_hash, "profile_id": pid, "pairs": len(s),
                       "serial_only_success": only_serial, "batch_only_success": only_batch,
                       "mcnemar_exact_p": f"{exact_two_sided_binomial(only_serial, only_serial + only_batch):.4f}",
                       "pairs_both_succeeded": len(diffs),
                       "median_batch_minus_serial_ms": f"{sorted(diffs)[len(diffs) // 2]:.3f}" if diffs else "",
                       "batch_slower_pairs": positive,
                       "sign_test_exact_p": f"{exact_two_sided_binomial(positive, nonzero):.4g}" if diffs else ""})
    with (RESULTS / "r2b-paired.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(paired[0]))
        w.writeheader()
        w.writerows(paired)
    print("wrote r2b-summary.csv and r2b-paired.csv")


if __name__ == "__main__":
    main()
