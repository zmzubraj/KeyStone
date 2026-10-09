#!/usr/bin/env python3
"""Single-host emulated deadline testbed for KEYSTONE revision R1.

Starts n custodian OS processes, each an asyncio TCP server on 127.0.0.1 that
holds only its own share. A combiner issues one canary audit and one authorized
dispute per trace, verifies each DLEQ proof as the response arrives, stops at t
valid partials, combines in the exponent, unwraps the record key and decrypts.
One-way network delay, loss and crash are injected per message from the trace
seed under the frozen profiles. This is an emulation with real cryptography,
not a geo-distributed or field measurement.

Usage: run_r1_deadline_testbed.py [PROFILE_ID ...]   (default: all profiles)
"""

from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import random
import struct
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
sys.path.insert(0, str(PROJECT / "src"))
sys.path.insert(0, str(PROJECT / "scripts"))

from keystone.dleq import DLEQProof  # noqa: E402
from keystone.protocol import derive_canary, epoch_bound_context  # noqa: E402
from keystone.sampling import sample_uniform  # noqa: E402
from keystone.serialization import PartialResponseTranscript  # noqa: E402
from keystone.standard_groups import GROUPS  # noqa: E402
from keystone.threshold_kem import (  # noqa: E402
    PartialDecryption,
    combine_partial_decryptions,
    create_partial_decryption,
    dealer_keygen,
    seal_record,
    verify_partial_decryption,
    _derive_kek,
)
from run_r1_pc03 import FREEZE, freeze_sha256  # noqa: E402
from cryptography.exceptions import InvalidTag  # noqa: E402
from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # noqa: E402

OUT = ROOT / "research-case/05-analysis/results/r1/deadline"
# Smoke mode: a 3-trace engineering check written outside the results tree and discarded.
SMOKE_DIR = os.environ.get("KEYSTONE_R1_SMOKE_DIR")
BASE_PORT = 47100
CHAIN = 1
CONTRACT = b"\x11" * 20


def int_bytes(value: int) -> bytes:
    return value.to_bytes(max(1, (value.bit_length() + 7) // 8), "big")


async def _send(writer: asyncio.StreamWriter, payload: bytes) -> None:
    writer.write(struct.pack(">I", len(payload)) + payload)
    await writer.drain()


async def _recv(reader: asyncio.StreamReader) -> bytes:
    (length,) = struct.unpack(">I", await reader.readexactly(4))
    return await reader.readexactly(length)


def custodian_main(member, group_name: str, epoch_id: str, port: int, ready) -> None:
    """Custodian process: answer partial-decryption requests for one share."""
    group = GROUPS[group_name]

    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            while True:
                request = json.loads(await _recv(reader))
                if request["drop"]:
                    continue
                await asyncio.sleep(request["delay_in"])
                element = int(request["element"], 16)
                partial = create_partial_decryption(member, element, group, bytes.fromhex(request["context"]))
                response = PartialResponseTranscript(
                    chain_id=CHAIN, contract_address=CONTRACT, epoch_id=epoch_id,
                    request_id=bytes.fromhex(request["request_id"]), request_hash=bytes.fromhex(request["request_hash"]),
                    member_index=member.index, partial_element=int_bytes(partial.value),
                    proof_a1=int_bytes(partial.proof.a1), proof_a2=int_bytes(partial.proof.a2),
                    proof_z=int_bytes(partial.proof.z), response_unix_ms=int(time.time() * 1000)).to_bytes()
                await asyncio.sleep(request["delay_out"])
                await _send(writer, response)
        except (asyncio.IncompleteReadError, ConnectionResetError):
            writer.close()

    async def serve() -> None:
        server = await asyncio.start_server(handle, "127.0.0.1", port)
        ready.set()
        async with server:
            await server.serve_forever()

    asyncio.run(serve())


def trace_seed(profile_id: str, index: int) -> int:
    return int.from_bytes(hashlib.sha256(f"KEYSTONE-R1|DEADLINE|{profile_id}|{index}".encode()).digest()[:8], "big")


def one_way(rng: random.Random, profile: dict) -> float:
    if profile["median_ms"] == 0:
        return 0.0
    return profile["median_ms"] / 1000 * math.exp(profile["sigma"] * rng.gauss(0.0, 1.0))


async def collect(connections, epoch, element, context, targets, needed, plan, timeout, request_id):
    """Send to targets, verify responses as they arrive; return (valid partials, completion time)."""
    request_hash = hashlib.sha256(request_id + context).digest()
    start = time.perf_counter()
    for index in targets:
        payload = {"element": hex(element), "context": context.hex(), "request_id": request_id.hex(),
                   "request_hash": request_hash.hex(), **plan[index]}
        await _send(connections[index][1], json.dumps(payload).encode())
    queue: asyncio.Queue = asyncio.Queue()

    async def reader_task(index):
        try:
            queue.put_nowait((index, await _recv(connections[index][0])))
        except asyncio.CancelledError:
            raise

    tasks = [asyncio.create_task(reader_task(i)) for i in targets if not plan[i]["drop"]]
    valid: list[PartialDecryption] = []
    done_at = None
    deadline = start + timeout
    try:
        while len(valid) < needed and (remaining := deadline - time.perf_counter()) > 0:
            try:
                index, raw = await asyncio.wait_for(queue.get(), remaining)
            except TimeoutError:
                break
            msg = PartialResponseTranscript.from_bytes(raw)
            member = epoch.members[msg.member_index]
            partial = PartialDecryption(member.member_id, msg.member_index, int.from_bytes(msg.partial_element, "big"),
                                        DLEQProof(int.from_bytes(msg.proof_a1, "big"), int.from_bytes(msg.proof_a2, "big"),
                                                  int.from_bytes(msg.proof_z, "big")))
            if verify_partial_decryption(member, element, partial, epoch.group, context):
                valid.append(partial)
        if len(valid) >= needed:
            done_at = time.perf_counter() - start
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    return valid, done_at, start


async def open_all(n: int) -> dict:
    return {i: await asyncio.open_connection("127.0.0.1", BASE_PORT + i) for i in range(1, n + 1)}


def close_all(connections: dict) -> None:
    for _, writer in connections.values():
        writer.close()


async def run_profile(profile_id: str, profile: dict, spec: dict, epoch, writer_csv) -> None:
    n, t = spec["committee"]["n"], spec["committee"]["t"]
    s, q = 8, 8
    timeout = spec["hard_timeout_s"]
    for trace in range(spec["traces_per_profile"]):
        seed = trace_seed(profile_id, trace)
        rng = random.Random(seed)
        silent: set[int] = set()
        down_domain = ""
        if profile["crashed"]:
            silent |= set(rng.sample(range(1, n + 1), profile["crashed"]))
        if profile["domain_outage"]:
            domain = rng.randrange(4)
            down_domain = str(domain)
            silent |= {i for i in range(1, n + 1) if (i - 1) % 4 == domain}

        def plan_for(kind: str) -> dict[int, dict]:
            plan = {}
            for index in range(1, n + 1):
                lost = rng.random() < profile["loss"] or rng.random() < profile["loss"]
                plan[index] = {"delay_in": one_way(rng, profile), "delay_out": one_way(rng, profile),
                               "drop": index in silent or lost}
            return plan

        beacon = hashlib.sha256(seed.to_bytes(8, "big")).digest()
        audit_context = epoch_bound_context(epoch, f"audit|{profile_id}|{trace}".encode())
        canary = derive_canary(epoch, beacon, f"audit-slot|{profile_id}|{trace}".encode())
        sampled = [int(m.split("-")[1]) for m in sample_uniform([f"custodian-{i:03d}" for i in range(1, n + 1)], s, beacon)]
        connections = await open_all(n)
        audit_valid, audit_time, _ = await collect(connections, epoch, canary, audit_context, sampled, q,
                                                   plan_for("audit"), timeout, hashlib.sha256(b"A" + beacon).digest())

        plaintext = rng.randbytes(1024)
        record_id = f"rec-{profile_id}-{trace}"
        sealed = seal_record(epoch.public_key, epoch.group, record_id, plaintext, b"r1-aad")
        dispute_context = epoch_bound_context(epoch, f"dispute|{record_id}".encode())
        # Fresh connections for the dispute so no late audit reply can be read as a dispute reply.
        close_all(connections)
        connections = await open_all(n)
        dispute_valid, collect_time, start = await collect(
            connections, epoch, sealed.c1, dispute_context, list(range(1, n + 1)), t, plan_for("dispute"), timeout,
            hashlib.sha256(record_id.encode()).digest())
        dispute_time, plaintext_ok = None, False
        if collect_time is not None:
            shared = combine_partial_decryptions(dispute_valid[:t], epoch.group)
            kek = _derive_kek(shared, epoch.group, record_id, sealed.aad)
            try:
                key = AESGCM(kek).decrypt(sealed.key_nonce, sealed.wrapped_data_key, b"key-wrap|" + record_id.encode() + b"|" + sealed.aad)
                plaintext_ok = AESGCM(key).decrypt(sealed.record_nonce, sealed.ciphertext, sealed.aad) == plaintext
            except InvalidTag:
                plaintext_ok = False
            dispute_time = time.perf_counter() - start
        close_all(connections)
        writer_csv.writerow({
            "profile_id": profile_id, "trace": trace, "seed": seed, "silent_members": len(silent),
            "down_domain": down_domain, "audit_valid": len(audit_valid), "audit_pass": len(audit_valid) >= q,
            "audit_time_s": "" if audit_time is None else f"{audit_time:.6f}",
            "dispute_valid": len(dispute_valid), "dispute_success": bool(plaintext_ok),
            "dispute_time_s": "" if dispute_time is None or not plaintext_ok else f"{dispute_time:.6f}"})


def main() -> None:
    freeze_hash = freeze_sha256()
    spec = json.loads(FREEZE.read_text())["families"]["EMULATED_DEADLINE"]
    selected = sys.argv[1:] or list(spec["profiles"])
    out = Path(SMOKE_DIR) if SMOKE_DIR else OUT
    if SMOKE_DIR:
        spec = {**spec, "traces_per_profile": 3}
    out.mkdir(parents=True, exist_ok=True)
    group_name = spec["group"]
    n, t = spec["committee"]["n"], spec["committee"]["t"]
    for profile_id in selected:
        profile = spec["profiles"][profile_id]
        epoch = dealer_keygen(n, t, [f"domain-{i % 4}" for i in range(n)], epoch_id="epoch-r1", group=GROUPS[group_name])
        ctx = mp.get_context("spawn")
        processes = []
        for index, member in epoch.members.items():
            ready = ctx.Event()
            proc = ctx.Process(target=custodian_main, args=(member, group_name, epoch.epoch_id, BASE_PORT + index, ready), daemon=True)
            proc.start()
            processes.append((proc, ready))
        for _, ready in processes:
            ready.wait(30)
        path = out / f"{profile_id}.csv"
        started = time.time()
        with path.open("w", newline="") as handle:
            fields = ["profile_id", "trace", "seed", "silent_members", "down_domain", "audit_valid", "audit_pass",
                      "audit_time_s", "dispute_valid", "dispute_success", "dispute_time_s"]
            writer_csv = csv.DictWriter(handle, fieldnames=fields)
            writer_csv.writeheader()
            asyncio.run(run_profile(profile_id, profile, spec, epoch, writer_csv))
        for proc, _ in processes:
            proc.terminate()
            proc.join()
        meta = {"profile_id": profile_id, "profile": profile, "freeze_sha256": freeze_hash, "group": group_name,
                "pid": os.getpid(), "started_unix": started, "elapsed_s": time.time() - started,
                "label": spec["label"], "python": sys.version.split()[0]}
        (out / f"{profile_id}.meta.json").write_text(json.dumps(meta, indent=2) + "\n")
        print(profile_id, "done in", round(meta["elapsed_s"], 1), "s", flush=True)


if __name__ == "__main__":
    main()
