#!/usr/bin/env python3
"""Local cryptographic microbenchmarks and message sizes for revision R1.

Measures per-operation wall time for the canary audit and dispute paths over
the prototype research group and the RFC 7919 groups, plus the canonical
transcript sizes used to compute audit and dispute bandwidth. Single process,
pure Python: an upper bound on compute cost, not optimized-library speed.
"""

from __future__ import annotations

import csv
import json
import platform
from pathlib import Path
import random
import statistics
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
sys.path.insert(0, str(PROJECT / "src"))
sys.path.insert(0, str(PROJECT / "scripts"))

from keystone.protocol import derive_canary, epoch_bound_context  # noqa: E402
from keystone.serialization import AuditRequestTranscript, PartialResponseTranscript  # noqa: E402
from keystone.standard_groups import GROUPS  # noqa: E402
from keystone.threshold_kem import (  # noqa: E402
    combine_partial_decryptions,
    create_partial_decryption,
    dealer_keygen,

    seal_record,
    verify_partial_decryption,
)
from run_r1_pc03 import freeze_sha256  # noqa: E402

OUT = ROOT / "research-case/05-analysis/results/r1"
REPEATS = {"keystone-safe-prime-256-v1": 50, "ffdhe2048": 30, "ffdhe3072": 20}
N_GRID = (16, 32, 64, 128)
WARMUP = 3


def timed(fn, repeats: int) -> tuple[float, float]:
    """Median and p95 milliseconds of ``fn`` after WARMUP discarded calls."""
    for _ in range(WARMUP):
        fn()
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - start) * 1000)
    ordered = sorted(samples)
    return statistics.median(ordered), ordered[max(0, int(0.95 * len(ordered)) - 1)]


def int_bytes(value: int) -> bytes:
    return value.to_bytes(max(1, (value.bit_length() + 7) // 8), "big")


def main() -> None:
    freeze_hash = freeze_sha256()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261009)
    randbelow = lambda bound: rng.randrange(bound)  # noqa: E731
    op_rows, size_rows = [], []

    for name, group in GROUPS.items():
        repeats = REPEATS[name]
        n_max = max(N_GRID)
        t_max = n_max - (n_max - 1) // 3
        epoch = dealer_keygen(n_max, t_max, [f"d{i % 4}" for i in range(n_max)], group=group, randbelow=randbelow)
        context = epoch_bound_context(epoch, b"r1-bench")
        member = epoch.members[1]
        canary = derive_canary(epoch, b"beacon-r1", b"audit-slot-1")
        partial = create_partial_decryption(member, canary, group, context, randbelow=randbelow)

        for op, fn in {
            "canary_derivation": lambda: derive_canary(epoch, b"beacon-r1", b"audit-slot-1"),
            "partial_plus_dleq_proof": lambda: create_partial_decryption(member, canary, group, context, randbelow=randbelow),
            "dleq_verification": lambda: verify_partial_decryption(member, canary, partial, group, context),
            "record_seal_1KiB": lambda: seal_record(epoch.public_key, group, "rec-1", b"x" * 1024, b"aad", randbelow=randbelow),
        }.items():
            median, p95 = timed(fn, repeats)
            op_rows.append({"group": name, "operation": op, "n": "", "t": "", "repeats": repeats,
                            "median_ms": median, "p95_ms": p95})
            print(name, op, round(median, 3))

        sealed = seal_record(epoch.public_key, group, "rec-1", b"x" * 1024, b"aad", randbelow=randbelow)
        partials_all = [create_partial_decryption(epoch.members[i], sealed.c1, group, context, randbelow=randbelow)
                        for i in range(1, t_max + 1)]
        for n in N_GRID:
            t = n - (n - 1) // 3
            subset = partials_all[:t]
            median, p95 = timed(lambda: combine_partial_decryptions(subset, group), repeats)
            op_rows.append({"group": name, "operation": "combine_t_partials", "n": n, "t": t, "repeats": repeats,
                            "median_ms": median, "p95_ms": p95})
            median, p95 = timed(lambda: _open_t(epoch, sealed, subset, context, t), max(5, repeats // 3))
            op_rows.append({"group": name, "operation": "verify_t_and_combine", "n": n, "t": t,
                            "repeats": max(5, repeats // 3), "median_ms": median, "p95_ms": p95})
            print(name, "combine/open", n, t, round(median, 2))

        request = AuditRequestTranscript(
            chain_id=1, contract_address=b"\x11" * 20, epoch_id=epoch.epoch_id, request_id=b"\x22" * 32,
            audit_slot=1, beacon_hash=b"\x33" * 32, canary_element=int_bytes(canary),
            sampled_bitmap=(2**8 - 1).to_bytes(32, "big"), required_valid=8, deadline_unix_ms=1)
        response = PartialResponseTranscript(
            chain_id=1, contract_address=b"\x11" * 20, epoch_id=epoch.epoch_id, request_id=b"\x22" * 32,
            request_hash=b"\x44" * 32, member_index=1, partial_element=int_bytes(partial.value),
            proof_a1=int_bytes(partial.proof.a1), proof_a2=int_bytes(partial.proof.a2),
            proof_z=int_bytes(partial.proof.z), response_unix_ms=1)
        size_rows.append({"group": name, "element_bytes": group.byte_length,
                          "audit_request_bytes": len(request.to_bytes()),
                          "partial_response_bytes": len(response.to_bytes())})

    with (OUT / "microbench-operations.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(op_rows[0]))
        writer.writeheader()
        writer.writerows(op_rows)
    with (OUT / "microbench-message-sizes.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(size_rows[0]))
        writer.writeheader()
        writer.writerows(size_rows)
    (OUT / "microbench-environment.json").write_text(json.dumps({
        "freeze_sha256": freeze_hash, "label": "LOCAL_MICROBENCHMARK_PURE_PYTHON_UPPER_BOUND",
        "python": sys.version.split()[0], "machine": platform.machine(), "platform": platform.platform(),
        "cpu": "Apple M4 Pro (12 cores)", "warmup": WARMUP, "repeats": REPEATS}, indent=2) + "\n")


def _open_t(epoch, sealed, partials, context, t):
    """Verify t partial proofs and combine them, mirroring open_record for a smaller threshold."""
    for partial in partials:
        if not verify_partial_decryption(epoch.members[partial.member_index], sealed.c1, partial, epoch.group, context):
            raise RuntimeError("benchmark partial failed verification")
    return combine_partial_decryptions(partials[:t], epoch.group)


if __name__ == "__main__":
    main()
