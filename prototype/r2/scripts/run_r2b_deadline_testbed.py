"""R2B_DEADLINE_REPLICATION: confirmatory replication of the R2 deadline testbed.

Implements research-case/03-design/r2b-replication/r2b-design-freeze.json. The testbed code is
R2's (run_r2_deadline_testbed.py, unchanged); this wrapper changes only

* the trace seeds, SHA256("KEYSTONE-R2B|DEADLINE|" + profile + "|" + i), the same for both
  variants, so SERIAL and BATCH see identical crashes, losses and delays (paired design);
* the output directory, research-case/05-analysis/results/r2b/deadline/<variant>/;
* the hash checks and metadata, which use the R2B freeze and deadline record.

Usage (from prototype/r2):
    uv run --locked --extra dev python -u scripts/run_r2b_deadline_testbed.py VARIANT [PROFILE ...]
Smoke mode: set KEYSTONE_R2_SMOKE_DIR (3 traces per profile, outside the results tree).
"""
from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_r2_deadline_testbed as bed  # noqa: E402

R2_DIR = Path(__file__).resolve().parents[1]
ROOT = R2_DIR.parents[1]
DESIGN = ROOT / "research-case/03-design/r2b-replication"
OUT = ROOT / "research-case/05-analysis/results/r2b/deadline"
SMOKE_DIR = os.environ.get("KEYSTONE_R2_SMOKE_DIR")


def r2b_seed(variant: str, profile_id: str, index: int) -> int:
    return int.from_bytes(hashlib.sha256(f"KEYSTONE-R2B|DEADLINE|{profile_id}|{index}".encode()).digest()[:8], "big")


def check(sums: str, name: str) -> str:
    actual = hashlib.sha256((DESIGN / name).read_bytes()).hexdigest()
    recorded = next(l.split()[0] for l in (DESIGN / sums).read_text().splitlines() if l.endswith(name))
    if actual != recorded:
        sys.exit(f"ABORT: {name} hash {actual} != recorded {recorded}")
    return actual


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in bed.VARIANTS:
        sys.exit(f"usage: {Path(__file__).name} {{SERIAL|BATCH}} [PROFILE ...]")
    variant = sys.argv[1]
    freeze_hash = check("r2b-design-freeze.SHA256SUMS", "r2b-design-freeze.json")
    record_hash = check("r2b-design-freeze.SHA256SUMS", "r2b-deadline-record.json")
    bed.require_correctness()
    bed.trace_seed = r2b_seed
    from keystone_r2 import sharing
    from keystone_r2.groups import RISTRETTO

    freeze = json.loads((DESIGN / "r2b-design-freeze.json").read_text())
    spec = freeze["testbed"]
    selected = sys.argv[2:] or list(spec["profiles"])
    traces = 3 if SMOKE_DIR else spec["traces_per_profile"]
    out = (Path(SMOKE_DIR) if SMOKE_DIR else OUT) / variant
    out.mkdir(parents=True, exist_ok=True)
    n, t = spec["committee"]["n"], spec["committee"]["t"]
    fields = ["variant", "profile_id", "trace", "seed", "silent_members", "down_domain", "audit_valid",
              "audit_pass", "audit_time_s", "dispute_valid", "dispute_success", "dispute_time_s"]
    for profile_id in selected:
        profile = spec["profiles"][profile_id]
        committee = sharing.deal(n, t, RISTRETTO)
        ctx = mp.get_context("spawn")
        processes = []
        for index in range(1, n + 1):
            ready = ctx.Event()
            proc = ctx.Process(target=bed.custodian_main,
                               args=(index, committee.shares[index], committee.public_shares, n, t,
                                     bed.BASE_PORT + index, ready), daemon=True)
            proc.start()
            processes.append((proc, ready))
        for _, ready in processes:
            ready.wait(30)
        started = time.time()
        with (out / f"{profile_id}.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            asyncio.run(bed.run_profile(variant, profile_id, profile, spec, committee, writer, traces))
        for proc, _ in processes:
            proc.terminate()
            proc.join()
        meta = {"family": "R2B_DEADLINE_REPLICATION", "variant": variant, "profile_id": profile_id,
                "profile": profile, "freeze_sha256": freeze_hash, "deadline_record_sha256": record_hash,
                "seed_rule": "SHA256('KEYSTONE-R2B|DEADLINE|' + profile + '|' + i), shared by both variants",
                "elapsed_s": time.time() - started, "traces": traces, "label": spec["label"],
                "python": sys.version.split()[0]}
        (out / f"{profile_id}.meta.json").write_text(json.dumps(meta, indent=2) + "\n")
        print(variant, profile_id, "done in", round(meta["elapsed_s"], 1), "s", flush=True)


if __name__ == "__main__":
    main()
