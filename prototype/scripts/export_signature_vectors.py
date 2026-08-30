#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
sys.path.insert(0, str(PROJECT / "src"))

from keystone.serialization import (  # noqa: E402
    AuditRequestTranscript,
    PartialResponseTranscript,
    transcript_hash,
)
from keystone.signatures import (  # noqa: E402
    derive_public_key,
    sign_transcript,
)


OUTPUT = ROOT / "paper" / "signature_test_vectors.json"
FIXTURE_SEED = bytes.fromhex(
    "00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff"
)


def _request() -> AuditRequestTranscript:
    return AuditRequestTranscript(
        chain_id=8453,
        contract_address=bytes.fromhex("11" * 20),
        epoch_id="epoch-1",
        request_id=bytes.fromhex("22" * 32),
        audit_slot=42,
        beacon_hash=bytes.fromhex("33" * 32),
        canary_element=bytes.fromhex("0102"),
        sampled_bitmap=(0b10101).to_bytes(32, "big"),
        required_valid=2,
        deadline_unix_ms=1_700_000_000_000,
    )


def _response() -> PartialResponseTranscript:
    request = _request()
    return PartialResponseTranscript(
        chain_id=8453,
        contract_address=bytes.fromhex("11" * 20),
        epoch_id="epoch-1",
        request_id=bytes.fromhex("22" * 32),
        request_hash=transcript_hash(request.to_bytes()),
        member_index=3,
        partial_element=bytes.fromhex("0203"),
        proof_a1=bytes.fromhex("0405"),
        proof_a2=bytes.fromhex("0607"),
        proof_z=bytes.fromhex("0809"),
        response_unix_ms=1_699_999_999_999,
    )


def render() -> str:
    request = _request()
    request_bytes = request.to_bytes()
    request_hash = transcript_hash(request_bytes)
    response = _response()
    response_bytes = response.to_bytes()
    public_key = derive_public_key(FIXTURE_SEED)
    signature = sign_transcript(FIXTURE_SEED, response)
    payload = {
        "evidence_label": (
            "internal deterministic interoperability fixture; "
            "test-only seed; not empirical evidence or secure key generation"
        ),
        "generated_on": "2026-08-29",
        "signature_scheme": "Ed25519 over canonical PartialResponseTranscript.to_bytes()",
        "vectors": [
            {
                "id": "TV-PARTIAL-RESPONSE-SIGNATURE-001",
                "seed_label": "test-only deterministic seed fixture",
                "private_seed_hex": FIXTURE_SEED.hex(),
                "public_key_hex": public_key.hex(),
                "request_transcript_hash_hex": request_hash.hex(),
                "response_transcript_hex": response_bytes.hex(),
                "response_transcript_hash_hex": transcript_hash(response_bytes).hex(),
                "signature_hex": signature.hex(),
                "fields": {
                    "chain_id": response.chain_id,
                    "contract_address_hex": response.contract_address.hex(),
                    "epoch_id": response.epoch_id,
                    "request_id_hex": response.request_id.hex(),
                    "request_hash_hex": response.request_hash.hex(),
                    "member_index": response.member_index,
                    "partial_element_hex": response.partial_element.hex(),
                    "proof_a1_hex": response.proof_a1.hex(),
                    "proof_a2_hex": response.proof_a2.hex(),
                    "proof_z_hex": response.proof_z.hex(),
                    "response_unix_ms": response.response_unix_ms,
                },
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}")
            return 1
        print("PASS: signature test vectors match signature implementation")
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
