"""R2_MICROBENCH: per-operation timings in ristretto255, ffdhe2048 and ffdhe3072.

Implements family R2_MICROBENCH of research-case/03-design/r2-design-amendment/
r2-design-freeze.json. Before measuring, the script (1) checks the SHA-256 of the
freeze file against r2-design-freeze.SHA256SUMS and (2) runs the R2 correctness
suite (R2_CORRECTNESS); it aborts if either fails. Each operation gets 50 warm-up
runs and 1000 timed runs (time.perf_counter_ns). Outputs, each stamped with the
freeze hash, go to research-case/05-analysis/results/r2/:

* microbench-raw.csv      every timed run (group, operation, run, ns)
* microbench-summary.csv  median and 95th percentile per group and operation (ms)
* microbench-environment.json  host, Python, library versions, git commit, times

Run from prototype/r2:  uv run --locked --extra dev python scripts/run_r2_microbench.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from keystone_r2 import audit, ristretto, sharing, tdh2
from keystone_r2.groups import GROUPS

R2_DIR = Path(__file__).resolve().parents[1]
ROOT = R2_DIR.parents[1]
DESIGN = ROOT / "research-case/03-design/r2-design-amendment"
OUT = ROOT / "research-case/05-analysis/results/r2"
WARMUP, RUNS = 50, 1000
N, T = 32, 22
NAMESPACE = b"KEYSTONE-R2|MICROBENCH|"
RECORD = bytes(1024)
GROUP_ORDER = ["ristretto255", "ffdhe2048", "ffdhe3072"]


def freeze_sha256() -> str:
    """Return the freeze hash after checking it against the frozen SHA256SUMS line."""
    actual = hashlib.sha256((DESIGN / "r2-design-freeze.json").read_bytes()).hexdigest()
    recorded = next(line.split()[0] for line in (DESIGN / "r2-design-freeze.SHA256SUMS").read_text().splitlines()
                    if line.endswith("r2-design-freeze.json"))
    if actual != recorded:
        sys.exit(f"ABORT: r2-design-freeze.json hash {actual} != recorded {recorded}")
    return actual


def require_correctness() -> None:
    """R2_CORRECTNESS: all correctness tests must pass before any measurement."""
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=R2_DIR,
                            capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit("ABORT: R2 correctness tests failed\n" + result.stdout[-2000:])


def beacon(group_name: str, op: str, i: int) -> bytes:
    return hashlib.sha256(NAMESPACE + group_name.encode() + b"|" + op.encode() + b"|" + str(i).encode()).digest()


def plain_seal(group, public_key, label: tdh2.Label) -> bytes:
    """Plain threshold-DH KEM sealing (no TDH2 proof), for the cost comparison."""
    r = group.random_scalar()
    u = group.base_mul(r)
    kek = hashlib.sha256(b"KEYSTONE-R2-KEK-v1" + group.encode(group.mul(r, public_key)) + label.encode()).digest()
    data_key = AESGCM.generate_key(bit_length=256)
    wrapped = AESGCM(kek).encrypt(os.urandom(12), data_key, label.encode())
    return group.encode(u) + wrapped + AESGCM(data_key).encrypt(os.urandom(12), RECORD, label.encode())


def operations(group_name: str):
    """Build the frozen operation list for one group; each entry maps a run index to one call."""
    group = GROUPS[group_name]
    committee = sharing.deal(N, T, group)
    label = tdh2.Label("E-bench", "record-bench", b"\x01" * 32)
    sealed = tdh2.seal(committee.public_key, label, RECORD, group)
    ct = sealed.ciphertext
    shares = [tdh2.create_share(committee, i, ct, label) for i in range(1, T + 1)]
    partials = {s.index: s.value for s in shares}
    canary = audit.derive_canary("E-bench", 0, beacon(group_name, "fixed", 0), group)
    fixed_beacon = beacon(group_name, "fixed", 0)
    response = audit.respond(committee, 1, canary, "E-bench", 0, fixed_beacon)
    return [
        ("canary_derivation", lambda i: audit.derive_canary("E-bench", i, beacon(group_name, "canary", i), group)),
        ("partial_plus_dleq_proof", lambda i: audit.respond(committee, 1 + i % N, canary, "E-bench", 0, fixed_beacon)),
        ("dleq_verification_serial", lambda i: audit.response_is_valid(committee, canary, response, "E-bench", 0,
                                                                       fixed_beacon)),
        ("dleq_batch_verification_t", lambda i: tdh2.shares_are_valid_batch(committee, ct, shares)),
        ("seal_1KiB_plain_kem", lambda i: plain_seal(group, committee.public_key, label)),
        ("seal_1KiB_tdh2", lambda i: tdh2.seal(committee.public_key, label, RECORD, group)),
        ("tdh2_ciphertext_proof_verification", lambda i: tdh2.ciphertext_is_valid(ct)),
        ("combine_t_partials", lambda i: sharing.combine_in_exponent(partials, group)),
        ("combine_t_plus_unwrap_decrypt", lambda i: tdh2.combine_and_decrypt(committee, sealed, partials)),
    ]


def environment(freeze: str, started: str) -> dict:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout
    return {
        "family": "R2_MICROBENCH", "freeze_sha256": freeze, "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": commit, "git_worktree_dirty": bool(dirty.strip()),
        "host": {"machine": platform.machine(), "system": platform.platform(), "processor": platform.processor(),
                 "cpu_count": os.cpu_count()},
        "python": sys.version, "rbcl": metadata.version("rbcl"), "barriers": metadata.version("barriers"),
        "cryptography": metadata.version("cryptography"),
        "embedded_libsodium_sha256": ristretto.embedded_library_sha256(),
        "warmup_runs": WARMUP, "timed_runs": RUNS, "committee": {"n": N, "t": T}, "record_bytes": len(RECORD),
        "timer": "time.perf_counter_ns, single process",
    }


def main() -> None:
    freeze = freeze_sha256()
    require_correctness()
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    OUT.mkdir(parents=True, exist_ok=True)
    raw_path, summary_path = OUT / "microbench-raw.csv", OUT / "microbench-summary.csv"
    summary_rows = []
    with raw_path.open("w", newline="") as raw_file:
        raw = csv.writer(raw_file)
        raw.writerow(["freeze_sha256", "group", "operation", "run", "ns"])
        for group_name in GROUP_ORDER:
            for op_name, call in operations(group_name):
                for i in range(WARMUP):
                    call(i)
                samples = []
                for i in range(RUNS):
                    start = time.perf_counter_ns()
                    call(WARMUP + i)
                    samples.append(time.perf_counter_ns() - start)
                for i, ns in enumerate(samples):
                    raw.writerow([freeze, group_name, op_name, i, ns])
                raw_file.flush()
                ordered = sorted(samples)
                row = [freeze, group_name, op_name, RUNS, f"{statistics.median(ordered) / 1e6:.4f}",
                       f"{ordered[int(0.95 * (RUNS - 1))] / 1e6:.4f}"]
                summary_rows.append(row)
                print(f"{group_name:13s} {op_name:36s} median {row[4]:>10s} ms  p95 {row[5]:>10s} ms", flush=True)
    with summary_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["freeze_sha256", "group", "operation", "runs", "median_ms", "p95_ms"])
        writer.writerows(summary_rows)
    (OUT / "microbench-environment.json").write_text(json.dumps(environment(freeze, started), indent=2) + "\n")


if __name__ == "__main__":
    main()
