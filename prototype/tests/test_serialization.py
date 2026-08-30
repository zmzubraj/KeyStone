import hashlib
import struct

import pytest

from keystone.serialization import (
    AuditRequestTranscript,
    PartialResponseTranscript,
    transcript_hash,
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


def test_audit_request_encoding_matches_independent_golden_layout() -> None:
    request = _request()
    expected = b"".join(
        [
            b"KSTN",
            bytes([1, 1]),
            struct.pack(">Q", 8453),
            bytes.fromhex("11" * 20),
            struct.pack(">H", 7),
            b"epoch-1",
            bytes.fromhex("22" * 32),
            struct.pack(">Q", 42),
            bytes.fromhex("33" * 32),
            struct.pack(">H", 2),
            bytes.fromhex("0102"),
            (0b10101).to_bytes(32, "big"),
            struct.pack(">H", 2),
            struct.pack(">Q", 1_700_000_000_000),
        ]
    )

    assert request.to_bytes() == expected
    assert AuditRequestTranscript.from_bytes(expected) == request


def test_partial_response_round_trips_and_binds_request_hash() -> None:
    request_hash = transcript_hash(_request().to_bytes())
    response = PartialResponseTranscript(
        chain_id=8453,
        contract_address=bytes.fromhex("11" * 20),
        epoch_id="epoch-1",
        request_id=bytes.fromhex("22" * 32),
        request_hash=request_hash,
        member_index=3,
        partial_element=bytes.fromhex("0203"),
        proof_a1=bytes.fromhex("0405"),
        proof_a2=bytes.fromhex("0607"),
        proof_z=bytes.fromhex("0809"),
        response_unix_ms=1_699_999_999_999,
    )

    encoded = response.to_bytes()

    assert PartialResponseTranscript.from_bytes(encoded) == response
    assert transcript_hash(encoded) == hashlib.sha256(
        b"KEYSTONE-TRANSCRIPT-HASH-v1" + encoded
    ).digest()

    other_chain = PartialResponseTranscript(
        chain_id=1,
        contract_address=response.contract_address,
        epoch_id=response.epoch_id,
        request_id=response.request_id,
        request_hash=response.request_hash,
        member_index=response.member_index,
        partial_element=response.partial_element,
        proof_a1=response.proof_a1,
        proof_a2=response.proof_a2,
        proof_z=response.proof_z,
        response_unix_ms=response.response_unix_ms,
    )
    assert transcript_hash(other_chain.to_bytes()) != transcript_hash(encoded)


def test_decoder_rejects_trailing_bytes_wrong_kind_and_noncanonical_integer() -> None:
    encoded = _request().to_bytes()
    with pytest.raises(ValueError, match="trailing"):
        AuditRequestTranscript.from_bytes(encoded + b"\x00")

    wrong_kind = encoded[:5] + bytes([2]) + encoded[6:]
    with pytest.raises(ValueError, match="message kind"):
        AuditRequestTranscript.from_bytes(wrong_kind)

    with pytest.raises(ValueError, match="canonical unsigned integer"):
        AuditRequestTranscript(
            chain_id=8453,
            contract_address=bytes.fromhex("11" * 20),
            epoch_id="epoch-1",
            request_id=bytes.fromhex("22" * 32),
            audit_slot=42,
            beacon_hash=bytes.fromhex("33" * 32),
            canary_element=b"\x00\x01",
            sampled_bitmap=(1).to_bytes(32, "big"),
            required_valid=1,
            deadline_unix_ms=1_700_000_000_000,
        ).to_bytes()
