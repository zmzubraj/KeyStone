"""Transport calibration for the R2b deadline (deviation-log entry 10, designed before this ran).

Measures the time the testbed harness itself takes to collect t = 22 of 32 responses with no
cryptography and no injected delay: 32 null custodian processes (asyncio TCP servers on
127.0.0.1, length-prefixed JSON, dispute-sized request and response payloads) and a combiner
that opens fresh connections, sends to all, and stops at 22 responses. Two modes:

* THREAD: each response passes through a no-op "verification" in a worker thread, as the
  R2 testbed's serial variant does;
* INLINE: the no-op runs on the event loop.

20 warm-up and 300 recorded traces per mode; (THREAD median - INLINE median)/22 estimates the
per-response hand-off cost.

Part B (deviation-log entry 11, revised after the smoke test and before any recorded run):
the full R2 dispute path at zero injected delay, with real cryptography and the testbed's own
code (run_r2_deadline_testbed.run_profile, serial variant), 20 warm-up and 300 recorded traces
with seeds SHA256("KEYSTONE-R2B|CALIBRATION|" + i). Fixed use: B0 = the p99 of its dispute
completion is the deterministic term of the R2b deadline.

Outputs to research-case/05-analysis/results/r2b/calibration/.
Run from prototype/r2:  uv run --locked --extra dev python -u scripts/run_r2_transport_calibration.py
"""
from __future__ import annotations

import asyncio
import csv
import json
import multiprocessing as mp
import os
import platform
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_r2_deadline_testbed as bed  # noqa: E402  (reuses the testbed's framing and connection handling)

R2_DIR = Path(__file__).resolve().parents[1]
ROOT = R2_DIR.parents[1]
OUT = Path(os.environ.get("KEYSTONE_R2_SMOKE_DIR") or ROOT / "research-case/05-analysis/results/r2b/calibration")
BASE_PORT = 47500
N, NEEDED = 32, 22
WARMUP, TRACES = (2, 3) if os.environ.get("KEYSTONE_R2_SMOKE_DIR") else (20, 300)


def null_custodian(index: int, port: int, ready) -> None:
    """Answers every request with a dispute-sized body after no computation."""
    body = json.dumps({"index": index, "value": "ab" * 32, "a1": "cd" * 32, "a2": "ef" * 32,
                       "z": int("9" * 76)}).encode()

    async def handle(reader, writer):
        try:
            while True:
                request = json.loads(await bed._recv(reader))
                if request["drop"]:
                    continue
                await bed._send(writer, body)
        except (asyncio.IncompleteReadError, ConnectionResetError):
            writer.close()

    async def serve():
        server = await asyncio.start_server(handle, "127.0.0.1", port)
        ready.set()
        async with server:
            await server.serve_forever()

    asyncio.run(serve())


def dispute_sized_request() -> dict:
    """A request with the same JSON shape and sizes as an R2 dispute request."""
    from keystone_r2 import sharing, tdh2
    from keystone_r2.groups import RISTRETTO
    committee = sharing.deal(N, NEEDED, RISTRETTO)
    label = tdh2.Label(bed.EPOCH, "rec-calibration", bytes(32))
    sealed = tdh2.seal(committee.public_key, label, bytes(1024))
    return {"kind": "dispute", "ciphertext": bed._ciphertext_to_json(sealed.ciphertext),
            "authorized_record": "rec-calibration", "policy_hash": bytes(32).hex(),
            "delay_in": 0.0, "delay_out": 0.0, "drop": False}


async def one_trace(request: dict, mode: str, pool: ThreadPoolExecutor) -> float:
    loop = asyncio.get_running_loop()
    connections = {i: await asyncio.open_connection("127.0.0.1", BASE_PORT + i) for i in range(1, N + 1)}
    start = time.perf_counter()
    payload = json.dumps(request).encode()
    for i in range(1, N + 1):
        await bed._send(connections[i][1], payload)
    queue: asyncio.Queue = asyncio.Queue()

    async def reader(i):
        queue.put_nowait(json.loads(await bed._recv(connections[i][0])))

    tasks = [asyncio.create_task(reader(i)) for i in range(1, N + 1)]
    seen: set[int] = set()
    while len(seen) < NEEDED:
        body = await queue.get()
        if mode == "THREAD":
            await loop.run_in_executor(pool, lambda b=body: True)
        seen.add(body["index"])
    elapsed = time.perf_counter() - start
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    bed.close_all(connections)
    return elapsed


async def run_mode(mode: str, request: dict) -> list[float]:
    pool = ThreadPoolExecutor(max_workers=1)
    for _ in range(WARMUP):
        await one_trace(request, mode, pool)
    times = [await one_trace(request, mode, pool) for _ in range(TRACES)]
    pool.shutdown()
    return times


def full_path(started_note: str) -> dict:
    """Part B: real R2 disputes with no injected delay, through the testbed's own code."""
    import hashlib
    from keystone_r2 import sharing
    from keystone_r2.groups import RISTRETTO

    bed.trace_seed = lambda variant, profile_id, i: int.from_bytes(
        hashlib.sha256(f"KEYSTONE-R2B|CALIBRATION|{i}".encode()).digest()[:8], "big")
    profile = {"median_ms": 0, "sigma": 0, "loss": 0.0, "crashed": 0, "domain_outage": False}
    spec = {"hard_timeout_s": 6.0}
    committee = sharing.deal(N, NEEDED, RISTRETTO)
    ctx = mp.get_context("spawn")
    procs = []
    for i in range(1, N + 1):
        ready = ctx.Event()
        proc = ctx.Process(target=bed.custodian_main, args=(i, committee.shares[i], committee.public_shares, N,
                                                             NEEDED, bed.BASE_PORT + i, ready), daemon=True)
        proc.start()
        procs.append((proc, ready))
    for _, ready in procs:
        ready.wait(30)
    fields = ["variant", "profile_id", "trace", "seed", "silent_members", "down_domain", "audit_valid",
              "audit_pass", "audit_time_s", "dispute_valid", "dispute_success", "dispute_time_s"]
    with open(os.devnull, "w", newline="") as sink:
        asyncio.run(bed.run_profile("SERIAL", "CAL-WARMUP", profile, spec, committee,
                                    csv.DictWriter(sink, fieldnames=fields), WARMUP))
    path = OUT / "full-path-traces.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        asyncio.run(bed.run_profile("SERIAL", "CAL-ZERO-DELAY", profile, spec, committee, writer, TRACES))
    for proc, _ in procs:
        proc.terminate()
        proc.join()
    with path.open() as handle:
        rows = list(csv.DictReader(handle))
    ok = [1000 * float(r["dispute_time_s"]) for r in rows if r["dispute_success"] == "True"]
    return {"traces": len(rows), "successes": len(ok), "median_ms": statistics.median(ok),
            "p95_ms": quantile(ok, 0.95), "p99_ms": quantile(ok, 0.99), "max_ms": max(ok)}


def quantile(xs: list[float], p: float) -> float:
    ordered = sorted(xs)
    return ordered[max(0, int(-(-p * len(ordered) // 1)) - 1)]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    request = dispute_sized_request()
    ctx = mp.get_context("spawn")
    procs = []
    for i in range(1, N + 1):
        ready = ctx.Event()
        proc = ctx.Process(target=null_custodian, args=(i, BASE_PORT + i, ready), daemon=True)
        proc.start()
        procs.append((proc, ready))
    for _, ready in procs:
        ready.wait(30)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    results = {}
    with (OUT / "calibration-traces.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mode", "trace", "completion_ms"])
        for mode in ("THREAD", "INLINE"):
            times = asyncio.run(run_mode(mode, request))
            results[mode] = times
            for i, t in enumerate(times):
                w.writerow([mode, i, f"{1000 * t:.4f}"])
    for proc, _ in procs:
        proc.terminate()
        proc.join()
    summary = {"label": "TRANSPORT_CALIBRATION_SAME_HOST", "design": "r2-deviation-log entry 10",
               "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "custodians": N, "needed": NEEDED, "warmup": WARMUP, "traces": TRACES,
               "request_bytes": len(json.dumps(request)), "host": platform.platform(),
               "python": sys.version.split()[0]}
    for mode, times in results.items():
        ms = [1000 * t for t in times]
        summary[mode] = {"median_ms": statistics.median(ms), "p95_ms": quantile(ms, 0.95),
                         "p99_ms": quantile(ms, 0.99), "max_ms": max(ms)}
    summary["handoff_per_response_ms"] = (summary["THREAD"]["median_ms"] - summary["INLINE"]["median_ms"]) / NEEDED
    summary["FULL_PATH_ZERO_DELAY"] = full_path(started)
    summary["B0_ms"] = summary["FULL_PATH_ZERO_DELAY"]["p99_ms"]
    summary["design"] = "r2-deviation-log entries 10 and 11"
    (OUT / "calibration-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("THREAD", "INLINE", "FULL_PATH_ZERO_DELAY", "B0_ms",
                                               "handoff_per_response_ms")}, indent=1))


if __name__ == "__main__":
    main()
