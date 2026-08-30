from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from keystone.serialization import PartialResponseTranscript


PRIVATE_SEED_LENGTH = 32
PUBLIC_KEY_LENGTH = 32
SIGNATURE_LENGTH = 64


class InvalidSignatureError(ValueError):
    """Raised when an Ed25519 signature does not verify."""


def _require_length(value: bytes, expected: int, label: str) -> bytes:
    if len(value) != expected:
        raise ValueError(f"{label} must be {expected} bytes")
    return value


def _private_key_from_seed(private_seed: bytes) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(
        _require_length(private_seed, PRIVATE_SEED_LENGTH, "private_seed")
    )


def _public_key_from_bytes(public_key: bytes) -> Ed25519PublicKey:
    return Ed25519PublicKey.from_public_bytes(
        _require_length(public_key, PUBLIC_KEY_LENGTH, "public_key")
    )


def derive_public_key(private_seed: bytes) -> bytes:
    public_key = _private_key_from_seed(private_seed).public_key()
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def sign_transcript(private_seed: bytes, transcript: PartialResponseTranscript) -> bytes:
    signature = _private_key_from_seed(private_seed).sign(transcript.to_bytes())
    return _require_length(signature, SIGNATURE_LENGTH, "signature")


def verify_transcript_signature(
    public_key: bytes,
    transcript: PartialResponseTranscript,
    signature: bytes,
) -> None:
    verifier = _public_key_from_bytes(public_key)
    checked_signature = _require_length(signature, SIGNATURE_LENGTH, "signature")
    try:
        verifier.verify(checked_signature, transcript.to_bytes())
    except InvalidSignature as error:
        raise InvalidSignatureError("invalid transcript signature") from error
