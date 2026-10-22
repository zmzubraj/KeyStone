"""R2_DEADLINE_TESTBED: single-host emulated deadline testbed with ristretto255 and TDH2.

Implements family R2_DEADLINE_TESTBED of research-case/03-design/r2-design-amendment/
r2-design-freeze.json. The emulation is R1's (prototype/scripts/run_r1_deadline_testbed.py)
unchanged: n custodian OS processes, each an asyncio TCP server on 127.0.0.1 holding
only its own share; per-message lognormal one-way delays on the request and the
response leg; loss on either leg; crashed custodians never answer; fresh connections
for the dispute; 6 s hard timeout. What changes, as frozen:

* cryptography: ristretto255; the audit uses the R2 canary and cryptographic sampler;
  disputes use TDH2, and custodians verify the ciphertext proof and the authorized
  label before releasing a share;
* verification runs in a worker thread, off the combiner's event loop;
* variants SERIAL (verify each response on arrival, stop at the required count) and
  BATCH (batch-verify the first required count, fall back to individual verification);
* trace seeds: SHA256("KEYSTONE-R2|DEADLINE|" + variant + "|" + profile + "|" + i).

Before running, the script checks the freeze hash, the deadline-record hash and the
R2 correctness suite. Dispute times are recorded raw; success by each deadline
(primary and secondary from r2-deadline-record.json, and the fixed grid) is computed
in analysis, not here.

Usage (from prototype/r2):
    uv run --locked --extra dev python -u scripts/run_r2_deadline_testbed.py VARIANT [PROFILE ...]
Smoke mode: set KEYSTONE_R2_SMOKE_DIR to write 3 traces per profile outside the results tree.
"""
from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import math
import multiprocessing as mp
import os
import random
import socket
import struct
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

R2_DIR = Path(__file__).resolve().parents[1]
ROOT = R2_DIR.parents[1]
DESIGN = ROOT / "research-case/03-design/r2-design-amendment"
OUT = ROOT / "research-case/05-analysis/results/r2/deadline"
SMOKE_DIR = os.environ.get("KEYSTONE_R2_SMOKE_DIR")
BASE_PORT = 47300
EPOCH = "epoch-r2"
VARIANTS = ("SERIAL", "BATCH")
S_AUDIT, Q_AUDIT = 8, 8


def _check_sums(sums_name: str, file_name: str) -> str:
    actual = hashlib.sha256((DESIGN / file_name).read_bytes()).hexdigest()
    recorded = next(line.split()[0] for line in (DESIGN / sums_name).read_text().splitlines()
                    if line.endswith(file_name))
    if actual != recorded:
        sys.exit(f"ABORT: {file_name} hash {actual} != recorded {recorded}")
    return actual


def require_correctness() -> None:
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=R2_DIR,
                            capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit("ABORT: R2 correctness tests failed\n" + result.stdout[-2000:])


async def _send(writer: asyncio.StreamWriter, payload: bytes) -> None:
    writer.write(struct.pack(">I", len(payload)) + payload)
    await writer.drain()


async def _recv(reader: asyncio.StreamReader) -> bytes:
    (length,) = struct.unpack(">I", await reader.readexactly(4))
    return await reader.readexactly(length)


def _ciphertext_to_json(ct) -> dict:
    return {"epoch": ct.label.epoch, "record_id": ct.label.record_id, "policy_hash": ct.label.policy_hash.hex(),
            "u": ct.u.hex(), "u_bar": ct.u_bar.hex(), "e": ct.e, "f": ct.f,
            "key_nonce": ct.key_nonce.hex(), "wrapped_key": ct.wrapped_key.hex()}


def _ciphertext_from_json(data: dict):
    from keystone_r2 import tdh2
    label = tdh2.Label(data["epoch"], data["record_id"], bytes.fromhex(data["policy_hash"]))
    return tdh2.Ciphertext(label, bytes.fromhex(data["u"]), bytes.fromhex(data["u_bar"]), data["e"], data["f"],
                           bytes.fromhex(data["key_nonce"]), bytes.fromhex(data["wrapped_key"]))


def custodian_main(index: int, share: int, public_shares: dict, n: int, t: int, port: int, ready) -> None:
    """Custodian process: holds only its own share; answers audit and dispute requests."""
    from keystone_r2 import audit, sharing, tdh2
    from keystone_r2.groups import RISTRETTO

    own = sharing.Committee(n=n, t=t, public_key=b"", public_shares=public_shares, shares={index: share},
                            commitments=(), group=RISTRETTO)

    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            while True:
                request = json.loads(await _recv(reader))
                if request["drop"]:
                    continue
                await asyncio.sleep(request["delay_in"])
                if request["kind"] == "audit":
                    canary = bytes.fromhex(request["canary"])
                    resp = audit.respond(own, index, canary, EPOCH, request["slot"], bytes.fromhex(request["beacon"]))
                    body = {"index": index, "value": resp.value.hex(), "a1": resp.proof.a1.hex(),
                            "a2": resp.proof.a2.hex(), "z": resp.proof.z}
                else:
                    ct = _ciphertext_from_json(request["ciphertext"])
                    authorized = tdh2.Label(EPOCH, request["authorized_record"], bytes.fromhex(request["policy_hash"]))
                    try:
                        share_obj = tdh2.create_share(own, index, ct, authorized)
                        body = {"index": index, "value": share_obj.value.hex(), "a1": share_obj.proof.a1.hex(),
                                "a2": share_obj.proof.a2.hex(), "z": share_obj.proof.z}
                    except tdh2.RejectedRequest:
                        body = {"index": index, "rejected": True}
                await asyncio.sleep(request["delay_out"])
                await _send(writer, json.dumps(body).encode())
        except (asyncio.IncompleteReadError, ConnectionResetError):
            writer.close()

    async def serve() -> None:
        server = await asyncio.start_server(handle, "127.0.0.1", port)
        ready.set()
        async with server:
            await server.serve_forever()

    asyncio.run(serve())


def trace_seed(variant: str, profile_id: str, index: int) -> int:
    text = f"KEYSTONE-R2|DEADLINE|{variant}|{profile_id}|{index}"
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big")


def one_way(rng: random.Random, profile: dict) -> float:
    if profile["median_ms"] == 0:
        return 0.0
    return profile["median_ms"] / 1000 * math.exp(profile["sigma"] * rng.gauss(0.0, 1.0))


async def collect(connections, targets, plan, payload_base, needed, timeout, verify_one, verify_many, variant, pool):
    """Send requests, gather responses, verify off the event loop; return (valid items, completion time)."""
    loop = asyncio.get_running_loop()
    start = time.perf_counter()
    for index in targets:
        await _send(connections[index][1], json.dumps({**payload_base, **plan[index]}).encode())
    queue: asyncio.Queue = asyncio.Queue()

    async def reader_task(index):
        queue.put_nowait(json.loads(await _recv(connections[index][0])))

    tasks = [asyncio.create_task(reader_task(i)) for i in targets if not plan[i]["drop"]]
    valid: dict[int, dict] = {}
    pending: dict[int, dict] = {}
    done_at = None
    deadline = start + timeout
    try:
        while len(valid) < needed and (remaining := deadline - time.perf_counter()) > 0:
            try:
                body = await asyncio.wait_for(queue.get(), remaining)
            except TimeoutError:
                break
            if body.get("rejected") or body["index"] in valid:
                continue
            if variant == "SERIAL":
                if await loop.run_in_executor(pool, verify_one, body):
                    valid[body["index"]] = body
            else:
                pending.setdefault(body["index"], body)
                if len(valid) + len(pending) >= needed:
                    batch = list(pending.values())[: needed - len(valid)]
                    if await loop.run_in_executor(pool, verify_many, batch):
                        valid.update({b["index"]: b for b in batch})
                    else:
                        for b in batch:
                            if await loop.run_in_executor(pool, verify_one, b):
                                valid[b["index"]] = b
                    for b in batch:
                        pending.pop(b["index"], None)
        if len(valid) >= needed:
            done_at = time.perf_counter() - start
        else:
            # Failed collection: verify leftover BATCH arrivals so the recorded valid count matches SERIAL.
            for b in pending.values():
                if await loop.run_in_executor(pool, verify_one, b):
                    valid[b["index"]] = b
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    return list(valid.values())[:needed], done_at, start


async def open_all(n: int) -> dict:
    return {i: await asyncio.open_connection("127.0.0.1", BASE_PORT + i) for i in range(1, n + 1)}


def close_all(connections: dict) -> None:
    # Abortive close (SO_LINGER 0): no TIME_WAIT, so 64 fresh connections per trace cannot exhaust ephemeral ports.
    for _, writer in connections.values():
        sock = writer.get_extra_info("socket")
        if sock is not None:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
        writer.close()


async def run_profile(variant, profile_id, profile, spec, committee, writer_csv, traces) -> None:
    from keystone_r2 import audit, dleq, tdh2
    from keystone_r2.groups import RISTRETTO

    n, t, timeout = committee.n, committee.t, spec["hard_timeout_s"]
    pool = ThreadPoolExecutor(max_workers=1)
    gen = RISTRETTO.generator()

    def to_proof(b):
        return dleq.DLEQProof(bytes.fromhex(b["a1"]), bytes.fromhex(b["a2"]), b["z"])

    for trace in range(traces):
        seed = trace_seed(variant, profile_id, trace)
        rng = random.Random(seed)
        silent: set[int] = set()
        down_domain = ""
        if profile["crashed"]:
            silent |= set(rng.sample(range(1, n + 1), profile["crashed"]))
        if profile["domain_outage"]:
            domain = rng.randrange(4)
            down_domain = str(domain)
            silent |= {i for i in range(1, n + 1) if (i - 1) % 4 == domain}

        def plan_for() -> dict[int, dict]:
            plan = {}
            for index in range(1, n + 1):
                lost = rng.random() < profile["loss"] or rng.random() < profile["loss"]
                plan[index] = {"delay_in": one_way(rng, profile), "delay_out": one_way(rng, profile),
                               "drop": index in silent or lost}
            return plan

        beacon = hashlib.sha256(seed.to_bytes(8, "big")).digest()
        slot = trace
        canary = audit.derive_canary(EPOCH, slot, beacon)
        sampled = audit.sample(n, S_AUDIT, EPOCH, slot, beacon)

        def audit_one(b) -> bool:
            r = audit.AuditResponse(b["index"], bytes.fromhex(b["value"]), to_proof(b))
            return audit.response_is_valid(committee, canary, r, EPOCH, slot, beacon)

        def audit_many(batch) -> bool:
            ctx = lambda i: audit._context(EPOCH, slot, beacon) + i.to_bytes(4, "big")  # noqa: E731
            items = [(to_proof(b), committee.public_shares[b["index"]], bytes.fromhex(b["value"]), ctx(b["index"]))
                     for b in batch]
            return dleq.verify_batch(items, gen, canary)

        connections = await open_all(n)
        audit_valid, audit_time, _ = await collect(
            connections, sampled, plan_for(), {"kind": "audit", "canary": canary.hex(), "slot": slot,
                                               "beacon": beacon.hex()},
            Q_AUDIT, timeout, audit_one, audit_many, variant, pool)

        plaintext = rng.randbytes(1024)
        record_id = f"rec-{variant}-{profile_id}-{trace}"
        policy_hash = hashlib.sha256(b"policy|" + record_id.encode()).digest()
        label = tdh2.Label(EPOCH, record_id, policy_hash)
        sealed = tdh2.seal(committee.public_key, label, plaintext)
        ct = sealed.ciphertext

        def share_obj(b):
            return tdh2.DecryptionShare(b["index"], bytes.fromhex(b["value"]), to_proof(b))

        def dispute_one(b) -> bool:
            return tdh2.share_is_valid(committee, ct, share_obj(b))

        def dispute_many(batch) -> bool:
            return tdh2.shares_are_valid_batch(committee, ct, [share_obj(b) for b in batch])

        close_all(connections)
        connections = await open_all(n)
        dispute_valid, collect_time, start = await collect(
            connections, list(range(1, n + 1)), plan_for(),
            {"kind": "dispute", "ciphertext": _ciphertext_to_json(ct), "authorized_record": record_id,
             "policy_hash": policy_hash.hex()},
            t, timeout, dispute_one, dispute_many, variant, pool)
        dispute_time, plaintext_ok = None, False
        if collect_time is not None:
            try:
                recovered = tdh2.combine_and_decrypt(committee, sealed,
                                                     {b["index"]: bytes.fromhex(b["value"]) for b in dispute_valid})
                plaintext_ok = recovered == plaintext
            except Exception:  # noqa: BLE001 - any failure to decrypt is a failed dispute
                plaintext_ok = False
            dispute_time = time.perf_counter() - start
        close_all(connections)
        writer_csv.writerow({
            "variant": variant, "profile_id": profile_id, "trace": trace, "seed": seed,
            "silent_members": len(silent), "down_domain": down_domain,
            "audit_valid": len(audit_valid), "audit_pass": len(audit_valid) >= Q_AUDIT,
            "audit_time_s": "" if audit_time is None else f"{audit_time:.6f}",
            "dispute_valid": len(dispute_valid), "dispute_success": bool(plaintext_ok),
            "dispute_time_s": "" if dispute_time is None or not plaintext_ok else f"{dispute_time:.6f}"})
    pool.shutdown()


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in VARIANTS:
        sys.exit(f"usage: {Path(__file__).name} {{{'|'.join(VARIANTS)}}} [PROFILE ...]")
    variant = sys.argv[1]
    freeze_hash = _check_sums("r2-design-freeze.SHA256SUMS", "r2-design-freeze.json")
    deadline_hash = _check_sums("r2-deadline-record.SHA256SUMS", "r2-deadline-record.json")
    require_correctness()
    from keystone_r2 import sharing
    from keystone_r2.groups import RISTRETTO

    spec = json.loads((DESIGN / "r2-design-freeze.json").read_text())["families"]["R2_DEADLINE_TESTBED"]
    selected = sys.argv[2:] or list(spec["profiles"])
    traces = 3 if SMOKE_DIR else spec["traces_per_profile"]
    out = (Path(SMOKE_DIR) if SMOKE_DIR else OUT) / variant
    out.mkdir(parents=True, exist_ok=True)
    n, t = spec["committee"]["n"], spec["committee"]["t"]
    for profile_id in selected:
        profile = spec["profiles"][profile_id]
        committee = sharing.deal(n, t, RISTRETTO)
        ctx = mp.get_context("spawn")
        processes = []
        for index in range(1, n + 1):
            ready = ctx.Event()
            proc = ctx.Process(target=custodian_main,
                               args=(index, committee.shares[index], committee.public_shares, n, t,
                                     BASE_PORT + index, ready), daemon=True)
            proc.start()
            processes.append((proc, ready))
        for _, ready in processes:
            ready.wait(30)
        path = out / f"{profile_id}.csv"
        started = time.time()
        with path.open("w", newline="") as handle:
            fields = ["variant", "profile_id", "trace", "seed", "silent_members", "down_domain", "audit_valid",
                      "audit_pass", "audit_time_s", "dispute_valid", "dispute_success", "dispute_time_s"]
            writer_csv = csv.DictWriter(handle, fieldnames=fields)
            writer_csv.writeheader()
            asyncio.run(run_profile(variant, profile_id, profile, spec, committee, writer_csv, traces))
        for proc, _ in processes:
            proc.terminate()
            proc.join()
        meta = {"variant": variant, "profile_id": profile_id, "profile": profile, "freeze_sha256": freeze_hash,
                "deadline_record_sha256": deadline_hash, "group": "ristretto255", "dispute_kem": "TDH2",
                "pid": os.getpid(), "started_unix": started, "elapsed_s": time.time() - started,
                "traces": traces, "label": spec["label"], "python": sys.version.split()[0]}
        (out / f"{profile_id}.meta.json").write_text(json.dumps(meta, indent=2) + "\n")
        print(variant, profile_id, "done in", round(meta["elapsed_s"], 1), "s", flush=True)


if __name__ == "__main__":
    main()
