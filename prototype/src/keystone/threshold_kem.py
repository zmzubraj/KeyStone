from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, replace
import hashlib
import os
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .dleq import DLEQProof, prove_equal_discrete_logs, verify_equal_discrete_logs
from .group import GroupParameters, RESEARCH_GROUP, encode_int
from .shamir import (
    feldman_commitments,
    lagrange_coefficient_at_zero,
    share_secret,
    verify_share,
)

RandBelow = Callable[[int], int]
RandomBytes = Callable[[int], bytes]


class InsufficientValidShares(RuntimeError):
    pass


class RecordDecryptionError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class MemberShare:
    member_id: str
    index: int
    domain: str
    share: int
    public_share: int


@dataclass(frozen=True, slots=True)
class EpochKey:
    epoch_id: str
    threshold: int
    public_key: int
    commitments: tuple[int, ...]
    members: dict[int, MemberShare]
    group: GroupParameters = RESEARCH_GROUP

    @property
    def n(self) -> int:
        return len(self.members)


@dataclass(frozen=True, slots=True)
class SealedRecord:
    record_id: str
    c1: int
    key_nonce: bytes
    wrapped_data_key: bytes
    record_nonce: bytes
    ciphertext: bytes
    aad: bytes


@dataclass(frozen=True, slots=True)
class PartialDecryption:
    member_id: str
    member_index: int
    value: int
    proof: DLEQProof

    def with_value(self, value: int) -> "PartialDecryption":
        return replace(self, value=value)


def _nonzero_scalar(group: GroupParameters, randbelow: RandBelow) -> int:
    while True:
        value = randbelow(group.q) % group.q
        if value != 0:
            return value


def _derive_kek(shared_secret: int, group: GroupParameters, record_id: str, aad: bytes) -> bytes:
    digest = hashlib.sha256()
    digest.update(b"KEYSTONE-KEM-DEM-v1")
    digest.update(encode_int(shared_secret, group.byte_length))
    digest.update(record_id.encode("utf-8"))
    digest.update(len(aad).to_bytes(4, "big"))
    digest.update(aad)
    return digest.digest()


def dealer_keygen(
    n: int,
    threshold: int,
    domains: Sequence[str],
    *,
    epoch_id: str = "epoch-1",
    group: GroupParameters = RESEARCH_GROUP,
    randbelow: RandBelow = secrets.randbelow,
) -> EpochKey:
    """Dealer-based key generation used only by the MPP.

    A production version replaces this boundary with DKG plus VSS/PVSS.
    """

    if len(domains) != n:
        raise ValueError("domains must contain exactly n entries")
    secret = _nonzero_scalar(group, randbelow)
    coefficients, shares = share_secret(secret, n, threshold, group.q, randbelow)
    commitments = feldman_commitments(coefficients, group)
    members: dict[int, MemberShare] = {}
    for index in range(1, n + 1):
        share = shares[index]
        if not verify_share(index, share, commitments, group):
            raise RuntimeError("internal VSS consistency failure")
        members[index] = MemberShare(
            member_id=f"custodian-{index}",
            index=index,
            domain=domains[index - 1],
            share=share,
            public_share=pow(group.g, share, group.p),
        )
    return EpochKey(
        epoch_id=epoch_id,
        threshold=threshold,
        public_key=pow(group.g, secret, group.p),
        commitments=commitments,
        members=members,
        group=group,
    )


def seal_record(
    public_key: int,
    group: GroupParameters,
    record_id: str,
    plaintext: bytes,
    aad: bytes,
    *,
    randbelow: RandBelow = secrets.randbelow,
    random_bytes: RandomBytes = os.urandom,
) -> SealedRecord:
    if not group.validate_element(public_key):
        raise ValueError("public key is not a valid subgroup element")
    randomness = _nonzero_scalar(group, randbelow)
    c1 = pow(group.g, randomness, group.p)
    shared_secret = pow(public_key, randomness, group.p)
    kek = _derive_kek(shared_secret, group, record_id, aad)

    data_key = random_bytes(32)
    key_nonce = random_bytes(12)
    record_nonce = random_bytes(12)
    wrap_aad = b"key-wrap|" + record_id.encode("utf-8") + b"|" + aad
    wrapped_data_key = AESGCM(kek).encrypt(key_nonce, data_key, wrap_aad)
    ciphertext = AESGCM(data_key).encrypt(record_nonce, plaintext, aad)
    return SealedRecord(
        record_id=record_id,
        c1=c1,
        key_nonce=key_nonce,
        wrapped_data_key=wrapped_data_key,
        record_nonce=record_nonce,
        ciphertext=ciphertext,
        aad=aad,
    )


def _proof_context(context: bytes, member_index: int) -> bytes:
    return context + b"|member-index=" + str(member_index).encode("ascii")


def create_partial_decryption(
    member: MemberShare,
    c1: int,
    group: GroupParameters,
    context: bytes,
    *,
    randbelow: RandBelow = secrets.randbelow,
) -> PartialDecryption:
    if not group.validate_element(c1):
        raise ValueError("c1 is not a valid subgroup element")
    value = pow(c1, member.share, group.p)
    proof = prove_equal_discrete_logs(
        member.share,
        group.g,
        member.public_share,
        c1,
        value,
        group,
        _proof_context(context, member.index),
        randbelow,
    )
    return PartialDecryption(member.member_id, member.index, value, proof)


def verify_partial_decryption(
    member: MemberShare,
    c1: int,
    partial: PartialDecryption,
    group: GroupParameters,
    context: bytes,
) -> bool:
    if partial.member_index != member.index or partial.member_id != member.member_id:
        return False
    return verify_equal_discrete_logs(
        partial.proof,
        group.g,
        member.public_share,
        c1,
        partial.value,
        group,
        _proof_context(context, member.index),
    )


def combine_partial_decryptions(
    partials: Iterable[PartialDecryption],
    group: GroupParameters,
) -> int:
    selected = list(partials)
    indices = [partial.member_index for partial in selected]
    if len(set(indices)) != len(indices):
        raise ValueError("partial-decryption indices must be unique")
    shared_secret = 1
    for partial in selected:
        coefficient = lagrange_coefficient_at_zero(partial.member_index, indices, group.q)
        shared_secret = (shared_secret * pow(partial.value, coefficient, group.p)) % group.p
    return shared_secret


def open_record(
    epoch: EpochKey,
    sealed: SealedRecord,
    partials: Iterable[PartialDecryption],
    context: bytes,
) -> bytes:
    valid: list[PartialDecryption] = []
    seen: set[int] = set()
    for partial in partials:
        if partial.member_index in seen:
            continue
        member = epoch.members.get(partial.member_index)
        if member is None:
            continue
        if verify_partial_decryption(member, sealed.c1, partial, epoch.group, context):
            valid.append(partial)
            seen.add(partial.member_index)
    if len(valid) < epoch.threshold:
        raise InsufficientValidShares(
            f"need {epoch.threshold} valid partial decryptions, received {len(valid)}"
        )

    selected = valid[: epoch.threshold]
    shared_secret = combine_partial_decryptions(selected, epoch.group)
    kek = _derive_kek(shared_secret, epoch.group, sealed.record_id, sealed.aad)
    wrap_aad = b"key-wrap|" + sealed.record_id.encode("utf-8") + b"|" + sealed.aad
    try:
        data_key = AESGCM(kek).decrypt(sealed.key_nonce, sealed.wrapped_data_key, wrap_aad)
        return AESGCM(data_key).decrypt(sealed.record_nonce, sealed.ciphertext, sealed.aad)
    except InvalidTag as exc:
        raise RecordDecryptionError("combined shares did not authenticate the sealed record") from exc
