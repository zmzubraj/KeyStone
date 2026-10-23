"""Post hoc exact prediction of R2 deadline success from the order-statistic model.

Label: POST_HOC_EXACT. Written after the R2 testbed results existed (deviation-log entry 10);
it uses only the frozen profile parameters and the frozen deadline record, never the
traces, and compares the prediction with the observed rates in deadline-summary.csv.

The model (keystone_r2.deadline_model) counts the same deterministic work as the frozen
deadline formula, fixed = c_p + t*c_v + c_c, and no transport overhead; a gap between
prediction and observation therefore measures what the formula omits.

Writes research-case/05-analysis/results/r2/deadline/deadline-predictions.csv.
Run from prototype/r2:  uv run --locked --extra dev python scripts/predict_r2_deadline.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

from keystone_r2 import deadline_model as dm

R2_DIR = Path(__file__).resolve().parents[1]
ROOT = R2_DIR.parents[1]
DESIGN = ROOT / "research-case/03-design/r2-design-amendment"
RESULTS = ROOT / "research-case/05-analysis/results/r2/deadline"
N, T = 32, 22


def check(sums: str, name: str) -> str:
    actual = hashlib.sha256((DESIGN / name).read_bytes()).hexdigest()
    recorded = next(l.split()[0] for l in (DESIGN / sums).read_text().splitlines() if l.endswith(name))
    if actual != recorded:
        sys.exit(f"ABORT: {name} hash mismatch")
    return actual


def main() -> None:
    freeze_hash = check("r2-design-freeze.SHA256SUMS", "r2-design-freeze.json")
    record_hash = check("r2-deadline-record.SHA256SUMS", "r2-deadline-record.json")
    spec = json.loads((DESIGN / "r2-design-freeze.json").read_text())["families"]["R2_DEADLINE_TESTBED"]
    record = json.loads((DESIGN / "r2-deadline-record.json").read_text())
    inputs = record["inputs_ms"]
    fixed = inputs["c_p"] + T * inputs["c_v"] + inputs["c_c"]
    with (RESULTS / "deadline-summary.csv").open() as f:
        observed = {(r["variant"], r["profile_id"]): r for r in csv.DictReader(f)}
    rows = []
    for pid, p in spec["profiles"].items():
        live = N - p["crashed"] - (8 if p["domain_outage"] else 0)
        for endpoint, key in (("primary", "primary_delta_d_star_ms"), ("secondary", "secondary_frozen_delta_d_star_ms")):
            x = record["profiles"][pid][key]
            slack = x - fixed
            # With no injected delay and zero slack the model's verdict is a knife edge; report it as undefined.
            zero_slack = p["median_ms"] == 0 and abs(slack) < 1e-3
            pred = None if zero_slack else dm.success_probability(x, live, T, p["median_ms"], p["sigma"], p["loss"],
                                                                   fixed)
            for variant in ("SERIAL", "BATCH"):
                o = observed[(variant, pid)]
                lo, hi = (float(v) for v in o[f"{endpoint}_wilson95"].strip("[]").split(","))
                rows.append({"label": "POST_HOC_EXACT", "freeze_sha256": freeze_hash,
                             "deadline_record_sha256": record_hash, "profile_id": pid, "variant": variant,
                             "endpoint": endpoint, "deadline_ms": f"{x:.4f}", "n_live": live,
                             "model_fixed_ms": f"{fixed:.4f}", "network_slack_ms": f"{slack:.4f}",
                             "predicted": "undefined (zero slack)" if pred is None else f"{pred:.6f}",
                             "observed": o[f"{endpoint}_rate"], "observed_wilson95": o[f"{endpoint}_wilson95"],
                             "predicted_in_wilson95": "" if pred is None else lo <= pred <= hi})
    with (RESULTS / "deadline-predictions.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        if r["endpoint"] == "primary":
            print(f"{r['variant']:6s} {r['profile_id']:24s} predicted {r['predicted']} observed "
                  f"{r['observed']} {r['observed_wilson95']} inside={r['predicted_in_wilson95']}")


if __name__ == "__main__":
    main()
