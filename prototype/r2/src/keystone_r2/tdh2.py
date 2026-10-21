"""TDH2 threshold KEM (Shoup and Gennaro) over ristretto255, with record-bound labels.

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

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from keystone_r2 import dleq
from keystone_r2 import ristretto as rs
from keystone_r2 import sharing

G_BAR = rs.hash_to_group(b"TDH2-second-generator", b"KEYSTONE-R2")


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
    u: bytes
    u_bar: bytes
    e: int
    f: int
    key_nonce: bytes
    wrapped_key: bytes


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
    value: bytes
    proof: dleq.DLEQProof


def _proof_challenge(label: Label, key_nonce: bytes, wrapped_key: bytes,
                     u: bytes, w: bytes, u_bar: bytes, w_bar: bytes) -> int:
    return dleq.challenge(b"TDH2-ciphertext", label.encode(), key_nonce, wrapped_key, u, w, u_bar, w_bar)


def _kek(shared: bytes, label: Label) -> bytes:
    return hashlib.sha256(b"KEYSTONE-R2-KEK-v1" + shared + label.encode()).digest()


def seal(public_key: bytes, label: Label, plaintext: bytes) -> SealedRecord:
    """Encrypt ``plaintext`` under a fresh data key wrapped by TDH2 for ``label``."""
    rs.validate_point(public_key)
    r, s = rs.random_scalar(), rs.random_scalar()
    u, w = rs.base_multiply(r), rs.base_multiply(s)
    u_bar, w_bar = rs.multiply(r, G_BAR), rs.multiply(s, G_BAR)
    data_key = AESGCM.generate_key(bit_length=256)
    key_nonce, record_nonce = os.urandom(12), os.urandom(12)
    wrapped_key = AESGCM(_kek(rs.multiply(r, public_key), label)).encrypt(key_nonce, data_key, label.encode())
    e = _proof_challenge(label, key_nonce, wrapped_key, u, w, u_bar, w_bar)
    ciphertext = Ciphertext(label, u, u_bar, e, (s + r * e) % rs.ORDER, key_nonce, wrapped_key)
    record_ciphertext = AESGCM(data_key).encrypt(record_nonce, plaintext, label.encode())
    return SealedRecord(ciphertext, record_nonce, record_ciphertext)


def ciphertext_is_valid(ciphertext: Ciphertext) -> bool:
    """Check the TDH2 proof that ``log_G u == log_{G_bar} u_bar``, bound to label and wrapped key."""
    try:
        rs.validate_point(ciphertext.u)
        rs.validate_point(ciphertext.u_bar)
        if not (0 < ciphertext.e < rs.ORDER and 0 < ciphertext.f < rs.ORDER):
            return False
        w = rs.subtract(rs.base_multiply(ciphertext.f), rs.multiply(ciphertext.e, ciphertext.u))
        w_bar = rs.subtract(rs.multiply(ciphertext.f, G_BAR), rs.multiply(ciphertext.e, ciphertext.u_bar))
        expected = _proof_challenge(ciphertext.label, ciphertext.key_nonce, ciphertext.wrapped_key,
                                    ciphertext.u, w, ciphertext.u_bar, w_bar)
        return expected == ciphertext.e
    except (rs.InvalidPoint, ValueError):
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
    x_i = committee.shares[index]
    value = rs.multiply(x_i, ciphertext.u)
    proof = dleq.prove(x_i, rs.generator(), committee.public_shares[index], ciphertext.u, value,
                       _share_context(ciphertext.label, index))
    return DecryptionShare(index, value, proof)


def share_is_valid(committee: sharing.Committee, ciphertext: Ciphertext, share: DecryptionShare) -> bool:
    """Verify a custodian's DLEQ proof that ``log_G h_i == log_u u_i``."""
    public_share = committee.public_shares.get(share.index)
    if public_share is None:
        return False
    return dleq.verify(share.proof, rs.generator(), public_share, ciphertext.u, share.value,
                       _share_context(ciphertext.label, share.index))


def open_record(committee: sharing.Committee, sealed: SealedRecord, shares: list[DecryptionShare]) -> bytes:
    """Combine t valid shares from distinct custodians and decrypt the record."""
    ciphertext = sealed.ciphertext
    if not ciphertext_is_valid(ciphertext):
        raise RejectedRequest("invalid TDH2 ciphertext proof")
    valid: dict[int, bytes] = {}
    for share in shares:
        if share.index not in valid and share_is_valid(committee, ciphertext, share):
            valid[share.index] = share.value
        if len(valid) == committee.t:
            break
    if len(valid) < committee.t:
        raise InsufficientShares(f"need {committee.t} valid shares, got {len(valid)}")
    shared = sharing.combine_in_exponent(valid)
    data_key = AESGCM(_kek(shared, ciphertext.label)).decrypt(
        ciphertext.key_nonce, ciphertext.wrapped_key, ciphertext.label.encode())
    return AESGCM(data_key).decrypt(sealed.record_nonce, sealed.record_ciphertext, ciphertext.label.encode())
