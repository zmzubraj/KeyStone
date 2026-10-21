"""TDH2 threshold KEM (Shoup and Gennaro) over any R2 group, with record-bound labels.

Sealing a record under the epoch key ``PK = x*G`` produces ``u = r*G``,
``u_bar = r*G_bar`` and a Fiat--Shamir proof ``(e, f)`` that both use the same
``r``. The proof's challenge hashes the label ``(epoch, record id, policy hash)``
and the wrapped data key, so a ciphertext cannot be re-labelled or malleated
without invalidating it, and a fresh proof requires knowing ``r``. Custodians
release ``u_i = x_i*u`` (with a DLEQ proof) only for a valid ciphertext whose
label equals the authorized one. This blocks the cross-record attack of the
plain threshold KEM (paper, Proposition 2).

The data key encrypts the record with AES-GCM; the key-encryption key is derived
from ``r*PK`` and the label.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from keystone_r2 import dleq, sharing
from keystone_r2.groups import RISTRETTO, Element, InvalidElement


@lru_cache(maxsize=None)
def second_generator(group=RISTRETTO) -> Element:
    """``G_bar`` with unknown discrete log relative to ``G`` (hash-to-group of a fixed string)."""
    return group.hash_to_group(b"TDH2-second-generator", b"KEYSTONE-R2")


G_BAR = second_generator(RISTRETTO)


class RejectedRequest(ValueError):
    """Raised by a custodian that refuses to release a decryption share."""


class InsufficientShares(ValueError):
    """Raised when fewer than t valid shares from distinct custodians are available."""


@dataclass(frozen=True)
class Label:
    """Binds a ciphertext to one record: epoch, record identifier and policy hash."""

    epoch: str
    record_id: str
    policy_hash: bytes

    def encode(self) -> bytes:
        parts = [b"KEYSTONE-R2-LABEL-v1", self.epoch.encode(), self.record_id.encode(), self.policy_hash]
        return b"".join(len(p).to_bytes(4, "big") + p for p in parts)


@dataclass(frozen=True)
class Ciphertext:
    """TDH2 KEM ciphertext plus the AES-GCM-wrapped data key."""

    label: Label
    u: Element
    u_bar: Element
    e: int
    f: int
    key_nonce: bytes
    wrapped_key: bytes
    group: Any = RISTRETTO


@dataclass(frozen=True)
class SealedRecord:
    """A sealed record: the KEM ciphertext and the record ciphertext under the data key."""

    ciphertext: Ciphertext
    record_nonce: bytes
    record_ciphertext: bytes


@dataclass(frozen=True)
class DecryptionShare:
    """Custodian ``index`` releases ``u_i = x_i*u`` with a DLEQ proof against ``h_i``."""

    index: int
    value: Element
    proof: dleq.DLEQProof


def _proof_challenge(group, label: Label, key_nonce: bytes, wrapped_key: bytes, u, w, u_bar, w_bar) -> int:
    enc = group.encode
    return dleq.challenge(b"TDH2-ciphertext", group.name.encode(), label.encode(), key_nonce, wrapped_key,
                          enc(u), enc(w), enc(u_bar), enc(w_bar), order=group.order)


def _kek(group, shared: Element, label: Label) -> bytes:
    return hashlib.sha256(b"KEYSTONE-R2-KEK-v1" + group.encode(shared) + label.encode()).digest()


def seal(public_key: Element, label: Label, plaintext: bytes, group=RISTRETTO) -> SealedRecord:
    """Encrypt ``plaintext`` under a fresh data key wrapped by TDH2 for ``label``."""
    group.validate(public_key)
    g_bar = second_generator(group)
    r, s = group.random_scalar(), group.random_scalar()
    u, w = group.base_mul(r), group.base_mul(s)
    u_bar, w_bar = group.mul(r, g_bar), group.mul(s, g_bar)
    data_key = AESGCM.generate_key(bit_length=256)
    key_nonce, record_nonce = os.urandom(12), os.urandom(12)
    kek = _kek(group, group.mul(r, public_key), label)
    wrapped_key = AESGCM(kek).encrypt(key_nonce, data_key, label.encode())
    e = _proof_challenge(group, label, key_nonce, wrapped_key, u, w, u_bar, w_bar)
    ciphertext = Ciphertext(label, u, u_bar, e, (s + r * e) % group.order, key_nonce, wrapped_key, group)
    record_ciphertext = AESGCM(data_key).encrypt(record_nonce, plaintext, label.encode())
    return SealedRecord(ciphertext, record_nonce, record_ciphertext)


def ciphertext_is_valid(ciphertext: Ciphertext) -> bool:
    """Check the TDH2 proof that ``log_G u == log_{G_bar} u_bar``, bound to label and wrapped key."""
    group = ciphertext.group
    try:
        group.validate(ciphertext.u)
        group.validate(ciphertext.u_bar)
        if not (0 < ciphertext.e < group.order and 0 < ciphertext.f < group.order):
            return False
        g_bar = second_generator(group)
        w = group.sub(group.base_mul(ciphertext.f), group.mul(ciphertext.e, ciphertext.u))
        w_bar = group.sub(group.mul(ciphertext.f, g_bar), group.mul(ciphertext.e, ciphertext.u_bar))
        expected = _proof_challenge(group, ciphertext.label, ciphertext.key_nonce, ciphertext.wrapped_key,
                                    ciphertext.u, w, ciphertext.u_bar, w_bar)
        return expected == ciphertext.e
    except (InvalidElement, ValueError):
        return False


def _share_context(label: Label, index: int) -> bytes:
    return b"TDH2-share|" + label.encode() + b"|" + index.to_bytes(4, "big")


def create_share(committee: sharing.Committee, index: int, ciphertext: Ciphertext,
                 authorized: Label) -> DecryptionShare:
    """Custodian ``index`` releases its share only for a valid ciphertext with the authorized label."""
    if ciphertext.label != authorized:
        raise RejectedRequest("ciphertext label does not match the authorized record")
    if not ciphertext_is_valid(ciphertext):
        raise RejectedRequest("invalid TDH2 ciphertext proof")
    group = committee.group
    x_i = committee.shares[index]
    value = group.mul(x_i, ciphertext.u)
    proof = dleq.prove(x_i, group.generator(), committee.public_shares[index], ciphertext.u, value,
                       _share_context(ciphertext.label, index), group)
    return DecryptionShare(index, value, proof)


def share_is_valid(committee: sharing.Committee, ciphertext: Ciphertext, share: DecryptionShare) -> bool:
    """Verify a custodian's DLEQ proof that ``log_G h_i == log_u u_i``."""
    public_share = committee.public_shares.get(share.index)
    if public_share is None:
        return False
    return dleq.verify(share.proof, committee.group.generator(), public_share, ciphertext.u, share.value,
                       _share_context(ciphertext.label, share.index), committee.group)


def shares_are_valid_batch(committee: sharing.Committee, ciphertext: Ciphertext,
                           shares: list[DecryptionShare]) -> bool:
    """Batch-verify shares from distinct known custodians (decision D2, secondary variant)."""
    items = []
    for share in shares:
        public_share = committee.public_shares.get(share.index)
        if public_share is None:
            return False
        items.append((share.proof, public_share, share.value, _share_context(ciphertext.label, share.index)))
    return dleq.verify_batch(items, committee.group.generator(), ciphertext.u, committee.group)


def combine_and_decrypt(committee: sharing.Committee, sealed: SealedRecord, valid: dict[int, Element]) -> bytes:
    """Interpolate t verified share values and decrypt the record."""
    group, ciphertext = committee.group, sealed.ciphertext
    shared = sharing.combine_in_exponent(valid, group)
    data_key = AESGCM(_kek(group, shared, ciphertext.label)).decrypt(
        ciphertext.key_nonce, ciphertext.wrapped_key, ciphertext.label.encode())
    return AESGCM(data_key).decrypt(sealed.record_nonce, sealed.record_ciphertext, ciphertext.label.encode())


def open_record(committee: sharing.Committee, sealed: SealedRecord, shares: list[DecryptionShare],
                batch: bool = False) -> bytes:
    """Combine t valid shares from distinct custodians and decrypt the record.

    ``batch=True`` first batch-verifies the first t distinct shares and falls back to
    individual verification if the batch fails.
    """
    ciphertext = sealed.ciphertext
    if not ciphertext_is_valid(ciphertext):
        raise RejectedRequest("invalid TDH2 ciphertext proof")
    if batch:
        first_per_index: dict[int, DecryptionShare] = {}
        for share in shares:
            first_per_index.setdefault(share.index, share)
        candidates = list(first_per_index.values())[: committee.t]
        if len(candidates) == committee.t and shares_are_valid_batch(committee, ciphertext, candidates):
            return combine_and_decrypt(committee, sealed, {s.index: s.value for s in candidates})
    # Serial path (and batch fallback): keep trying shares for an index until one verifies.
    valid: dict[int, Element] = {}
    for share in shares:
        if share.index not in valid and share_is_valid(committee, ciphertext, share):
            valid[share.index] = share.value
        if len(valid) == committee.t:
            break
    if len(valid) < committee.t:
        raise InsufficientShares(f"need {committee.t} valid shares, got {len(valid)}")
    return combine_and_decrypt(committee, sealed, valid)
