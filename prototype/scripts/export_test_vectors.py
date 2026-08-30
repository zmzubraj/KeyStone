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


OUTPUT = ROOT / "paper" / "test_vectors.json"


def render() -> str:
    request = AuditRequestTranscript(
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
    request_bytes = request.to_bytes()
    request_digest = transcript_hash(request_bytes)
    response = PartialResponseTranscript(
        chain_id=8453,
        contract_address=bytes.fromhex("11" * 20),
        epoch_id="epoch-1",
        request_id=bytes.fromhex("22" * 32),
        request_hash=request_digest,
        member_index=3,
        partial_element=bytes.fromhex("0203"),
        proof_a1=bytes.fromhex("0405"),
        proof_a2=bytes.fromhex("0607"),
        proof_z=bytes.fromhex("0809"),
        response_unix_ms=1_699_999_999_999,
    )
    response_bytes = response.to_bytes()
    payload = {
        "evidence_label": "internal deterministic interoperability fixture; not empirical evidence",
        "format": {
            "byte_order": "big-endian",
            "length_prefix": "uint16 bytes for UTF-8 and unsigned-integer fields",
            "magic_ascii": "KSTN",
            "protocol_version": 1,
            "transcript_hash": "SHA-256(ASCII('KEYSTONE-TRANSCRIPT-HASH-v1') || encoded_message)",
        },
        "vectors": [
            {
                "id": "TV-AUDIT-REQUEST-001",
                "kind": "audit_request",
                "message_kind": 1,
                "fields": {
                    "chain_id": request.chain_id,
                    "contract_address_hex": request.contract_address.hex(),
                    "epoch_id": request.epoch_id,
                    "request_id_hex": request.request_id.hex(),
                    "audit_slot": request.audit_slot,
                    "beacon_hash_hex": request.beacon_hash.hex(),
                    "canary_element_hex": request.canary_element.hex(),
                    "sampled_bitmap_hex": request.sampled_bitmap.hex(),
                    "required_valid": request.required_valid,
                    "deadline_unix_ms": request.deadline_unix_ms,
                },
                "encoded_hex": request_bytes.hex(),
                "transcript_hash_hex": request_digest.hex(),
            },
            {
                "id": "TV-PARTIAL-RESPONSE-001",
                "kind": "partial_response",
                "message_kind": 2,
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
                "encoded_hex": response_bytes.hex(),
                "transcript_hash_hex": transcript_hash(response_bytes).hex(),
            },
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
        print("PASS: protocol test vectors match serialization implementation")
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
