"""Chaum--Pedersen equality-of-discrete-logarithm proofs over any R2 group.

A proof shows ``log_{base_1} public_1 == log_{base_2} public_2`` without revealing
the witness. The Fiat--Shamir challenge hashes a domain tag, the group name, both
bases, both public values, both commitments and a caller-supplied context, so
each proof is bound to one request. Every element is validated by the group.

``verify_batch`` checks many proofs that share ``base_1`` and ``base_2`` with one
random linear combination (decision D2, secondary variant); on failure the
caller falls back to individual verification to locate the bad proofs.
"""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass

from keystone_r2.groups import RISTRETTO, Element, InvalidElement

_DOMAIN = b"KEYSTONE-R2-DLEQ-v1"
_BATCH_COEFFICIENT_BITS = 128


@dataclass(frozen=True)
class DLEQProof:
    """Commitments ``a_1 = k*base_1``, ``a_2 = k*base_2`` and response ``z = k + c*w``."""

    a1: Element
    a2: Element
    z: int


def challenge(*items: bytes, order: int = RISTRETTO.order) -> int:
    """Hash length-prefixed items to a scalar mod ``order`` (64-byte wide reduction)."""
    digest = hashlib.sha512()
    for item in (_DOMAIN, *items):
        digest.update(len(item).to_bytes(4, "big"))
        digest.update(item)
    return int.from_bytes(digest.digest(), "big") % order


def _challenge(group, base_1, public_1, base_2, public_2, a1, a2, context: bytes) -> int:
    enc = group.encode
    return challenge(group.name.encode(), enc(base_1), enc(public_1), enc(base_2), enc(public_2),
                     enc(a1), enc(a2), context, order=group.order)


def prove(witness: int, base_1: Element, public_1: Element, base_2: Element, public_2: Element,
          context: bytes, group=RISTRETTO) -> DLEQProof:
    """Prove that ``public_1 = witness*base_1`` and ``public_2 = witness*base_2``."""
    nonce = group.random_scalar()
    a1, a2 = group.mul(nonce, base_1), group.mul(nonce, base_2)
    c = _challenge(group, base_1, public_1, base_2, public_2, a1, a2, context)
    return DLEQProof(a1=a1, a2=a2, z=(nonce + c * witness) % group.order)


def verify(proof: DLEQProof, base_1: Element, public_1: Element, base_2: Element, public_2: Element,
           context: bytes, group=RISTRETTO) -> bool:
    """Return True iff the proof verifies; malformed elements or scalars return False."""
    try:
        for element in (base_1, public_1, base_2, public_2, proof.a1, proof.a2):
            group.validate(element)
        if not 0 < proof.z < group.order:
            return False
        c = _challenge(group, base_1, public_1, base_2, public_2, proof.a1, proof.a2, context)
        if c == 0:
            return False
        left_1, left_2 = group.mul(proof.z, base_1), group.mul(proof.z, base_2)
        right_1 = group.add(proof.a1, group.mul(c, public_1))
        right_2 = group.add(proof.a2, group.mul(c, public_2))
        return left_1 == right_1 and left_2 == right_2
    except (InvalidElement, ValueError):
        return False


def verify_batch(items: list[tuple[DLEQProof, Element, Element, bytes]], base_1: Element, base_2: Element,
                 group=RISTRETTO) -> bool:
    """Batch-verify proofs ``(proof, public_1, public_2, context)`` sharing both bases.

    With random 128-bit coefficients rho_i, checks
    ``(sum rho_i z_i) base_1 == sum rho_i (a1_i + c_i public_1_i)`` and the analogue for
    base_2. A batch containing an invalid proof passes with probability at most 2^-128.
    """
    try:
        group.validate(base_1)
        group.validate(base_2)
        total_z = 0
        right_1 = right_2 = None
        for proof, public_1, public_2, context in items:
            for element in (public_1, public_2, proof.a1, proof.a2):
                group.validate(element)
            if not 0 < proof.z < group.order:
                return False
            c = _challenge(group, base_1, public_1, base_2, public_2, proof.a1, proof.a2, context)
            if c == 0:
                return False
            rho = secrets.randbits(_BATCH_COEFFICIENT_BITS) | 1
            total_z = (total_z + rho * proof.z) % group.order
            term_1 = group.add(group.mul(rho, proof.a1), group.mul(rho * c, public_1))
            term_2 = group.add(group.mul(rho, proof.a2), group.mul(rho * c, public_2))
            right_1 = term_1 if right_1 is None else group.add(right_1, term_1)
            right_2 = term_2 if right_2 is None else group.add(right_2, term_2)
        if right_1 is None:
            return True
        return group.mul(total_z, base_1) == right_1 and group.mul(total_z, base_2) == right_2
    except (InvalidElement, ValueError):
        return False
