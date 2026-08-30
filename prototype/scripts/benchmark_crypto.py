#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path
import random
import statistics
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from keystone.threshold_kem import (  # noqa: E402
    create_partial_decryption,
    dealer_keygen,
    open_record,
    seal_record,
    verify_partial_decryption,
)
from keystone.serialization import (  # noqa: E402
    AuditRequestTranscript,
    PartialResponseTranscript,
    transcript_hash,
)
from keystone.signatures import (  # noqa: E402
    SIGNATURE_LENGTH,
    derive_public_key,
    sign_transcript,
    verify_transcript_signature,
)


SIGNATURE_BENCHMARK_SEED = bytes.fromhex(
    "a17c9e281c8d1aa735c00c0f0b21cd1ce289b6386f81fd46ab987f6528a12e5f"
)


def _p95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[max(0, int(0.95 * len(ordered)) - 1)]


def _canonical_integer_bytes(value: int) -> bytes:
    return value.to_bytes(max(1, (value.bit_length() + 7) // 8), "big")


def benchmark(n: int, threshold: int, repeats: int, seed: int) -> dict[str, float | int]:
    rng = random.Random(seed)
    domains = [f"domain-{index % 8}" for index in range(n)]

    keygen_ms: list[float] = []
    seal_ms: list[float] = []
    prove_ms: list[float] = []
    verify_ms: list[float] = []
    open_ms: list[float] = []
    signature_sign_ms: list[float] = []
    signature_verify_ms: list[float] = []
    signature_public_key = derive_public_key(SIGNATURE_BENCHMARK_SEED)

    for repeat in range(repeats):
        start = time.perf_counter()
        epoch = dealer_keygen(
            n,
            threshold,
            domains,
            epoch_id=f"bench-{n}-{repeat}",
            randbelow=rng.randrange,
        )
        keygen_ms.append((time.perf_counter() - start) * 1000)

        start = time.perf_counter()
        sealed = seal_record(
            epoch.public_key,
            epoch.group,
            f"record-{repeat}",
            b"x" * 1024,
            b"benchmark",
            randbelow=rng.randrange,
        )
        seal_ms.append((time.perf_counter() - start) * 1000)

        context = f"dispute-{repeat}".encode()
        start = time.perf_counter()
        first = create_partial_decryption(
            epoch.members[1],
            sealed.c1,
            epoch.group,
            context,
            randbelow=rng.randrange,
        )
        prove_ms.append((time.perf_counter() - start) * 1000)

        start = time.perf_counter()
        assert verify_partial_decryption(epoch.members[1], sealed.c1, first, epoch.group, context)
        verify_ms.append((time.perf_counter() - start) * 1000)

        partials = [first]
        for index in range(2, threshold + 1):
            partials.append(create_partial_decryption(
                epoch.members[index],
                sealed.c1,
                epoch.group,
                context,
                randbelow=rng.randrange,
            ))
        start = time.perf_counter()
        opened = open_record(epoch, sealed, partials, context)
        open_ms.append((time.perf_counter() - start) * 1000)
        assert opened == b"x" * 1024

        audit_request = AuditRequestTranscript(
            chain_id=8453,
            contract_address=bytes.fromhex("11" * 20),
            epoch_id=epoch.epoch_id,
            request_id=repeat.to_bytes(32, "big"),
            audit_slot=repeat,
            beacon_hash=bytes.fromhex("22" * 32),
            canary_element=_canonical_integer_bytes(sealed.c1),
            sampled_bitmap=((1 << min(n, 256)) - 1).to_bytes(32, "big"),
            required_valid=min(threshold, 255),
            deadline_unix_ms=1_700_000_000_000 + repeat,
        )
        response = PartialResponseTranscript(
            chain_id=audit_request.chain_id,
            contract_address=audit_request.contract_address,
            epoch_id=audit_request.epoch_id,
            request_id=audit_request.request_id,
            request_hash=transcript_hash(audit_request.to_bytes()),
            member_index=first.member_index,
            partial_element=_canonical_integer_bytes(first.value),
            proof_a1=_canonical_integer_bytes(first.proof.a1),
            proof_a2=_canonical_integer_bytes(first.proof.a2),
            proof_z=_canonical_integer_bytes(first.proof.z),
            response_unix_ms=1_699_999_999_999 + repeat,
        )
        start = time.perf_counter()
        signature = sign_transcript(SIGNATURE_BENCHMARK_SEED, response)
        signature_sign_ms.append((time.perf_counter() - start) * 1000)

        start = time.perf_counter()
        verify_transcript_signature(signature_public_key, response, signature)
        signature_verify_ms.append((time.perf_counter() - start) * 1000)

    return {
        "n": n,
        "threshold": threshold,
        "repeats": repeats,
        "keygen_median_ms": statistics.median(keygen_ms),
        "keygen_p95_ms": _p95(keygen_ms),
        "seal_median_ms": statistics.median(seal_ms),
        "partial_proof_median_ms": statistics.median(prove_ms),
        "partial_verify_median_ms": statistics.median(verify_ms),
        "open_median_ms": statistics.median(open_ms),
        "open_p95_ms": _p95(open_ms),
        "signature_size_bytes": SIGNATURE_LENGTH,
        "signature_sign_median_ms": statistics.median(signature_sign_ms),
        "signature_verify_median_ms": statistics.median(signature_verify_ms),
    }


def main() -> None:
    rows = [
        benchmark(16, 11, 20, 6101),
        benchmark(32, 22, 20, 6102),
        benchmark(64, 43, 12, 6103),
    ]
    output = PROJECT / "results" / "crypto_benchmark.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
