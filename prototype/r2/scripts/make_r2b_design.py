"""Write the R2B design freeze and deadline record (run once, before any R2B testbed trace).

Inputs: the R2 freeze (profiles, committee, audit), the R2b calibration summary (B0) and
keystone_r2.deadline_model. Outputs in research-case/03-design/r2b-replication/:
r2b-design-freeze.json, r2b-deadline-record.json and r2b-design-freeze.SHA256SUMS.
Refuses to overwrite an existing freeze.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

from keystone_r2 import deadline_model as dm

R2_DIR = Path(__file__).resolve().parents[1]
ROOT = R2_DIR.parents[1]
R2_DESIGN = ROOT / "research-case/03-design/r2-design-amendment"
DESIGN = ROOT / "research-case/03-design/r2b-replication"
CALIBRATION = ROOT / "research-case/05-analysis/results/r2b/calibration/calibration-summary.json"
TARGET = 0.99


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if (DESIGN / "r2b-design-freeze.json").exists():
        sys.exit("ABORT: r2b-design-freeze.json exists; the freeze is append-only")
    DESIGN.mkdir(parents=True, exist_ok=True)
    r2 = json.loads((R2_DESIGN / "r2-design-freeze.json").read_text())["families"]["R2_DEADLINE_TESTBED"]
    calibration = json.loads(CALIBRATION.read_text())
    b0 = calibration["B0_ms"]
    n, t = r2["committee"]["n"], r2["committee"]["t"]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    profiles = {}
    for pid, p in r2["profiles"].items():
        live = n - p["crashed"] - (8 if p["domain_outage"] else 0)
        deadline = dm.order_statistic_deadline(live, t, p["median_ms"], p["sigma"], p["loss"], b0, TARGET)
        profiles[pid] = {"n_live": live,
                         "delta_os_ms": None if math.isinf(deadline) else round(deadline, 4),
                         "reconstructable": not math.isinf(deadline)}
    record = {
        "schema_id": "KEYSTONE_R2B_DEADLINE_RECORD", "created_utc": now, "created_before_any_r2b_trace": True,
        "rule": "Delta_os = smallest x with Pr[Bin(n_live, (1-loss)^2 F_RTT(x - B0)) >= t] >= 0.99; "
                "F_RTT = CDF of the sum of two lognormal one-way delays of the profile; none if unattainable",
        "target": TARGET, "B0_ms": b0, "B0_source": "p99 of FULL_PATH_ZERO_DELAY dispute completion",
        "calibration_summary_sha256": sha(CALIBRATION), "r2_freeze_sha256": sha(R2_DESIGN / "r2-design-freeze.json"),
        "model": "prototype/r2/src/keystone_r2/deadline_model.py", "profiles": profiles,
    }
    freeze = {
        "schema_id": "KEYSTONE_R2B_DESIGN_FREEZE", "frozen_at_utc": now, "frozen_before_any_r2b_trace": True,
        "purpose": "Confirmatory replication of R2_DEADLINE_TESTBED with a deadline corrected after R2: the R2 "
                   "primary deadline missed on D0 (zero network slack; host overhead not in the formula) and "
                   "fell short of 99% on D4 (per-leg p99 instead of the quantile of the t-th arrival). The "
                   "corrected deadline is fixed here from the R2b calibration and the order-statistic model, "
                   "and tested on fresh traces.",
        "result_blind_statement": "R2 outcomes were known when this was designed and motivated it; no R2b trace "
                                  "existed. The deadline uses only the calibration run and frozen parameters.",
        "deviation_log": "research-case/03-design/r2-design-amendment/r2-deviation-log.md (entries 10-12)",
        "testbed": {**{k: r2[k] for k in ("label", "topology", "network_emulation", "delay_model", "committee",
                                          "crypto", "profiles", "crash_selection", "traces_per_profile",
                                          "hard_timeout_s")},
                    "code": "prototype/r2/scripts/run_r2_deadline_testbed.py (unchanged), driven by "
                            "prototype/r2/scripts/run_r2b_deadline_testbed.py",
                    "trace_seed": "int.from_bytes(SHA256('KEYSTONE-R2B|DEADLINE|' + profile_id + '|' + str(i))"
                                  "[:8], 'big'), identical for both variants (paired)",
                    "variants": r2["variants"], "audit": {"s": 8, "q": 8}},
        "deadline_record": "r2b-deadline-record.json",
        "primary_endpoint": "Pr[dispute decrypts the correct plaintext by Delta_os(profile)], SERIAL, per "
                            "reconstructable profile; for D5-GLOBAL-CRASH11 (no Delta_os) success at any time",
        "criterion": "a reconstructable profile meets the endpoint if the 95% Wilson upper bound of its success "
                     "rate is at least 0.99; D5 is expected at 0%",
        "secondary_endpoints": [
            "the same for BATCH",
            "paired SERIAL vs BATCH: exact two-sided McNemar test on success by Delta_os; paired completion-time "
            "difference (median and exact sign test) over traces where both succeed",
            "model check: predicted vs observed success at the R2 deadline Delta_d_star and at Delta_os "
            "(prediction inside the Wilson interval)",
            "success at 0.05, 0.1, 0.25, 0.5, 1, 2, 5 s; completion-time median and p95",
            "audit pass rate versus exact expectation",
        ],
        "interval_method": "Wilson 95% for proportions; order-statistic quantiles for times",
        "pre_stated_expectation": "success by Delta_os at or near 99% in every reconstructable profile, 0% in D5; "
                                  "no material SERIAL vs BATCH difference; reported whatever the outcome",
        "claim_boundary": "single host, synthetic delay laws; a replication, not field data",
    }
    (DESIGN / "r2b-deadline-record.json").write_text(json.dumps(record, indent=2) + "\n")
    (DESIGN / "r2b-design-freeze.json").write_text(json.dumps(freeze, indent=2) + "\n")
    sums = "".join(f"{sha(DESIGN / f)}  {f}\n" for f in ("r2b-design-freeze.json", "r2b-deadline-record.json"))
    (DESIGN / "r2b-design-freeze.SHA256SUMS").write_text(sums)
    print(json.dumps(profiles, indent=1))
    print(sums)


if __name__ == "__main__":
    main()
