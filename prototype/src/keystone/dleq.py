from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import secrets

from .group import GroupParameters, hash_to_scalar

RandBelow = Callable[[int], int]


@dataclass(frozen=True, slots=True)
class DLEQProof:
    a1: int
    a2: int
    z: int


def _challenge(
    group: GroupParameters,
    base_1: int,
    public_1: int,
    base_2: int,
    public_2: int,
    a1: int,
    a2: int,
    context: bytes,
) -> int:
    return hash_to_scalar(
        group,
        b"dleq-proof",
        base_1,
        public_1,
        base_2,
        public_2,
        a1,
        a2,
        context,
    )


def prove_equal_discrete_logs(
    witness: int,
    base_1: int,
    public_1: int,
    base_2: int,
    public_2: int,
    group: GroupParameters,
    context: bytes,
    randbelow: RandBelow = secrets.randbelow,
) -> DLEQProof:
    if not all(group.validate_element(value) for value in (base_1, public_1, base_2, public_2)):
        raise ValueError("all DLEQ values must be subgroup elements")
    witness %= group.q
    nonce = randbelow(group.q) % group.q
    a1 = pow(base_1, nonce, group.p)
    a2 = pow(base_2, nonce, group.p)
    challenge = _challenge(group, base_1, public_1, base_2, public_2, a1, a2, context)
    z = (nonce + challenge * witness) % group.q
    return DLEQProof(a1=a1, a2=a2, z=z)


def verify_equal_discrete_logs(
    proof: DLEQProof,
    base_1: int,
    public_1: int,
    base_2: int,
    public_2: int,
    group: GroupParameters,
    context: bytes,
) -> bool:
    if not all(
        group.validate_element(value)
        for value in (base_1, public_1, base_2, public_2, proof.a1, proof.a2)
    ):
        return False
    if not 0 <= proof.z < group.q:
        return False
    challenge = _challenge(
        group,
        base_1,
        public_1,
        base_2,
        public_2,
        proof.a1,
        proof.a2,
        context,
    )
    left_1 = pow(base_1, proof.z, group.p)
    right_1 = (proof.a1 * pow(public_1, challenge, group.p)) % group.p
    left_2 = pow(base_2, proof.z, group.p)
    right_2 = (proof.a2 * pow(public_2, challenge, group.p)) % group.p
    return left_1 == right_1 and left_2 == right_2
