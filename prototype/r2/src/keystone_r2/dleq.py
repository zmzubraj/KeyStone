"""Chaum--Pedersen equality-of-discrete-logarithm proofs over ristretto255.

A proof shows ``log_{base_1} public_1 == log_{base_2} public_2`` without revealing
the witness. The Fiat--Shamir challenge hashes a domain tag, both bases, both
public values, both commitments and a caller-supplied context, so each proof is
bound to one request. All points are validated through ``ristretto.validate_point``.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from keystone_r2 import ristretto as rs

_DOMAIN = b"KEYSTONE-R2-DLEQ-v1"


@dataclass(frozen=True)
class DLEQProof:
    """Commitments ``a_1 = k*base_1``, ``a_2 = k*base_2`` and response ``z = k + c*w``."""

    a1: bytes
    a2: bytes
    z: int


def challenge(*items: bytes) -> int:
    """Hash length-prefixed items to a scalar mod the group order (64-byte wide reduction)."""
    digest = hashlib.sha512()
    for item in (_DOMAIN, *items):
        digest.update(len(item).to_bytes(4, "big"))
        digest.update(item)
    return int.from_bytes(digest.digest(), "big") % rs.ORDER


def prove(witness: int, base_1: bytes, public_1: bytes, base_2: bytes, public_2: bytes,
          context: bytes) -> DLEQProof:
    """Prove that ``public_1 = witness*base_1`` and ``public_2 = witness*base_2``."""
    nonce = rs.random_scalar()
    a1 = rs.multiply(nonce, base_1)
    a2 = rs.multiply(nonce, base_2)
    c = challenge(base_1, public_1, base_2, public_2, a1, a2, context)
    return DLEQProof(a1=a1, a2=a2, z=(nonce + c * witness) % rs.ORDER)


def verify(proof: DLEQProof, base_1: bytes, public_1: bytes, base_2: bytes, public_2: bytes,
           context: bytes) -> bool:
    """Return True iff the proof verifies; malformed points or scalars return False."""
    try:
        for point in (base_1, public_1, base_2, public_2, proof.a1, proof.a2):
            rs.validate_point(point)
        if not 0 < proof.z < rs.ORDER:
            return False
        c = challenge(base_1, public_1, base_2, public_2, proof.a1, proof.a2, context)
        left_1 = rs.multiply(proof.z, base_1)
        left_2 = rs.multiply(proof.z, base_2)
        right_1 = rs.add(proof.a1, rs.multiply(c, public_1)) if c else proof.a1
        right_2 = rs.add(proof.a2, rs.multiply(c, public_2)) if c else proof.a2
        return left_1 == right_1 and left_2 == right_2
    except (rs.InvalidPoint, ValueError):
        return False
