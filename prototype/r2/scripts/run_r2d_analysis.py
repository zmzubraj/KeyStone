"""R2d: repair on alarm with gated resharing, as frozen in
research-case/03-design/r2d-gated-repair/r2d-design-freeze.json.

Same grid, design rule and simulation cells as R2c, with one change found in review: a resharing
needs at least t ready custodians when it completes (fewer shares cannot reconstruct the epoch
secret), so the reset applies only then; otherwise nothing happens until the next audit. The R2c
runner is reused with its freeze, output directory, seed prefix and gate set for R2d; the
withholding tables are not recomputed (they do not involve repair).
Run from prototype/r2:  uv run --locked --extra dev python -u scripts/run_r2d_analysis.py
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_r2c_analysis as r2c  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
r2c.DESIGN = ROOT / "research-case/03-design/r2d-gated-repair"
r2c.FREEZE_NAME = "r2d-design-freeze"
r2c.SEED_PREFIX = "KEYSTONE-R2D|REPAIR|"
smoke = os.environ.get("KEYSTONE_R2C_SMOKE_DIR")
r2c.OUT = Path(smoke) if smoke else ROOT / "research-case/05-analysis/results/r2d"


def main() -> None:
    fh, spec = r2c.freeze()
    r2c.GATE = spec["repair_gate_threshold"]
    r2c.require_correctness()
    r2c.OUT.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    r2c.run_repair_sim(fh, spec)
    r2c.run_repair(fh, spec)
    env = {"family": "R2D", "freeze_sha256": fh, "gate": r2c.GATE, "started_utc": started, "smoke": bool(smoke),
           "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "python": sys.version.split()[0]}
    (r2c.OUT / "r2d-environment.json").write_text(json.dumps(env, indent=2) + "\n")


if __name__ == "__main__":
    main()
