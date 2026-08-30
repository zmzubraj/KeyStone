from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from keystone.serialization import (
    AuditRequestTranscript,
    PartialResponseTranscript,
    transcript_hash,
)
from keystone.signatures import (
    PRIVATE_SEED_LENGTH,
    PUBLIC_KEY_LENGTH,
    SIGNATURE_LENGTH,
    InvalidSignatureError,
    derive_public_key,
    sign_transcript,
    verify_transcript_signature,
)


FIXTURE_SEED = bytes.fromhex(
    "00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff"
)
EXPECTED_PUBLIC_KEY = bytes.fromhex(
    "3ccd241cffc9b3618044b97d036d8614593d8b017c340f1dee8773385517654b"
)
EXPECTED_SIGNATURE = bytes.fromhex(
    "d627c22bf09f1d4f0369b12aec1516ef1b4a1dc96044a725df5e3f8effc1a496"
    "d03222fb9314819e419cc34614439b0d52d04bf4967a993b7ff0ffbc22f1f904"
)
PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
EXPORTER = PROJECT / "scripts" / "export_signature_vectors.py"
OUTPUT = ROOT / "paper" / "signature_test_vectors.json"


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


def _response(chain_id: int = 8453, contract_address: bytes | None = None) -> PartialResponseTranscript:
    request = _request()
    request_hash = transcript_hash(request.to_bytes())
    return PartialResponseTranscript(
        chain_id=chain_id,
        contract_address=contract_address or bytes.fromhex("11" * 20),
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


def test_public_key_derivation_from_fixed_seed_is_deterministic() -> None:
    public_key = derive_public_key(FIXTURE_SEED)

    assert PRIVATE_SEED_LENGTH == 32
    assert PUBLIC_KEY_LENGTH == 32
    assert SIGNATURE_LENGTH == 64
    assert public_key == EXPECTED_PUBLIC_KEY


def test_signs_exact_canonical_partial_response_bytes() -> None:
    response = _response()

    signature = sign_transcript(FIXTURE_SEED, response)

    assert signature == EXPECTED_SIGNATURE
    assert verify_transcript_signature(EXPECTED_PUBLIC_KEY, response, signature) is None


def test_verification_rejects_wrong_message_signature_or_key() -> None:
    response = _response()
    signature = sign_transcript(FIXTURE_SEED, response)

    tampered_response = _response(chain_id=1)
    wrong_key = derive_public_key(bytes.fromhex("ff" * 32))
    tampered_signature = bytes([signature[0] ^ 0x01]) + signature[1:]

    for public_key, transcript, candidate in (
        (EXPECTED_PUBLIC_KEY, tampered_response, signature),
        (wrong_key, response, signature),
        (EXPECTED_PUBLIC_KEY, response, tampered_signature),
    ):
        with pytest.raises(InvalidSignatureError):
            verify_transcript_signature(public_key, transcript, candidate)


def test_context_change_cannot_replay_across_chain_or_contract() -> None:
    response = _response()
    signature = sign_transcript(FIXTURE_SEED, response)

    different_chain = _response(chain_id=8454)
    different_contract = _response(contract_address=bytes.fromhex("44" * 20))

    assert different_chain.to_bytes() != response.to_bytes()
    assert different_contract.to_bytes() != response.to_bytes()

    with pytest.raises(InvalidSignatureError):
        verify_transcript_signature(EXPECTED_PUBLIC_KEY, different_chain, signature)
    with pytest.raises(InvalidSignatureError):
        verify_transcript_signature(EXPECTED_PUBLIC_KEY, different_contract, signature)


def test_key_and_signature_lengths_are_validated() -> None:
    response = _response()
    signature = sign_transcript(FIXTURE_SEED, response)

    with pytest.raises(ValueError, match="32 bytes"):
        derive_public_key(FIXTURE_SEED[:-1])
    with pytest.raises(ValueError, match="32 bytes"):
        sign_transcript(FIXTURE_SEED[:-1], response)
    with pytest.raises(ValueError, match="32 bytes"):
        verify_transcript_signature(EXPECTED_PUBLIC_KEY[:-1], response, signature)
    with pytest.raises(ValueError, match="64 bytes"):
        verify_transcript_signature(EXPECTED_PUBLIC_KEY, response, signature[:-1])


def test_signature_vector_export_is_deterministic_and_checkable() -> None:
    write = subprocess.run(
        [sys.executable, str(EXPORTER)],
        cwd=PROJECT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert write.returncode == 0, write.stderr

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["vectors"][0]["public_key_hex"] == EXPECTED_PUBLIC_KEY.hex()
    assert payload["vectors"][0]["signature_hex"] == EXPECTED_SIGNATURE.hex()

    check = subprocess.run(
        [sys.executable, str(EXPORTER), "--check"],
        cwd=PROJECT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert check.returncode == 0, check.stderr
