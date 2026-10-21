"""TDH2 correctness tests (R2_CORRECTNESS in r2-design-freeze.json).

Covers DLEQ completeness and soundness checks, Feldman share verification,
end-to-end opening with t of n shares, and rejection of the cross-record attacks
that break the plain threshold KEM (paper, Proposition 2).
"""
from __future__ import annotations

import dataclasses

import pytest

from keystone_r2 import dleq
from keystone_r2 import ristretto as rs
from keystone_r2 import sharing, tdh2
from keystone_r2.groups import RISTRETTO

N, T = 32, 22
RECORD = b"inference record: model output 0x2a"


@pytest.fixture(scope="module")
def committee() -> sharing.Committee:
    return sharing.deal(N, T)


@pytest.fixture(scope="module")
def target_label() -> tdh2.Label:
    return tdh2.Label(epoch="E7", record_id="record-0001", policy_hash=b"\x11" * 32)


@pytest.fixture(scope="module")
def sealed(committee: sharing.Committee, target_label: tdh2.Label) -> tdh2.SealedRecord:
    return tdh2.seal(committee.public_key, target_label, RECORD)


def _shares(committee, ciphertext, authorized, indices):
    return [tdh2.create_share(committee, i, ciphertext, authorized) for i in indices]


# ---------------------------------------------------------------- DLEQ
def test_dleq_completeness_and_rejections() -> None:
    w = rs.random_scalar()
    base_2 = rs.hash_to_group(b"dleq-test", b"base")
    public_1, public_2 = rs.base_multiply(w), rs.multiply(w, base_2)
    proof = dleq.prove(w, rs.generator(), public_1, base_2, public_2, b"ctx")
    assert dleq.verify(proof, rs.generator(), public_1, base_2, public_2, b"ctx")
    assert not dleq.verify(proof, rs.generator(), public_1, base_2, public_2, b"other-ctx")
    assert not dleq.verify(proof, rs.generator(), public_1, base_2, rs.add(public_2, base_2), b"ctx")
    assert not dleq.verify(proof, rs.generator(), rs.base_multiply(w + 1), base_2, public_2, b"ctx")
    tampered = dataclasses.replace(proof, z=(proof.z + 1) % rs.ORDER)
    assert not dleq.verify(tampered, rs.generator(), public_1, base_2, public_2, b"ctx")
    identity = dataclasses.replace(proof, a1=bytes(32))
    assert not dleq.verify(identity, rs.generator(), public_1, base_2, public_2, b"ctx")


# ---------------------------------------------------------------- sharing
def test_feldman_verification(committee: sharing.Committee) -> None:
    assert all(sharing.verify_share(committee, i, x) for i, x in committee.shares.items())
    assert not sharing.verify_share(committee, 1, (committee.shares[1] + 1) % rs.ORDER)


# ---------------------------------------------------------------- end-to-end
def test_open_with_t_shares(committee, sealed, target_label) -> None:
    shares = _shares(committee, sealed.ciphertext, target_label, range(5, 5 + T))
    assert tdh2.open_record(committee, sealed, shares) == RECORD


def test_open_fails_with_t_minus_one_shares(committee, sealed, target_label) -> None:
    shares = _shares(committee, sealed.ciphertext, target_label, range(1, T))
    with pytest.raises(tdh2.InsufficientShares):
        tdh2.open_record(committee, sealed, shares)


def test_invalid_and_duplicate_shares_are_skipped(committee, sealed, target_label) -> None:
    good = _shares(committee, sealed.ciphertext, target_label, range(1, T + 1))
    bad = [dataclasses.replace(s, value=rs.add(s.value, rs.generator())) for s in good[:3]]
    duplicates = good[:2]
    assert not any(tdh2.share_is_valid(committee, sealed.ciphertext, s) for s in bad)
    assert tdh2.open_record(committee, sealed, bad + duplicates + good) == RECORD


# ---------------------------------------------------------------- Proposition 2 attacks
def test_resubmitted_component_under_new_record_id_is_rejected(committee, sealed) -> None:
    """Attack with gamma = 0: re-label the target's ciphertext and get the new record authorized."""
    attacker_label = tdh2.Label(epoch="E7", record_id="attacker-record", policy_hash=b"\x22" * 32)
    relabelled = dataclasses.replace(sealed.ciphertext, label=attacker_label)
    assert not tdh2.ciphertext_is_valid(relabelled)
    with pytest.raises(tdh2.RejectedRequest):
        tdh2.create_share(committee, 1, relabelled, attacker_label)


@pytest.mark.parametrize("relabel", [False, True])
def test_malleated_component_is_rejected(committee, sealed, target_label, relabel) -> None:
    """Attack with gamma != 0: shift u and u_bar consistently; the proof no longer verifies."""
    gamma = rs.random_scalar()
    label = tdh2.Label("E7", "attacker-record", b"\x22" * 32) if relabel else target_label
    malleated = dataclasses.replace(
        sealed.ciphertext,
        label=label,
        u=rs.add(sealed.ciphertext.u, rs.base_multiply(gamma)),
        u_bar=rs.add(sealed.ciphertext.u_bar, rs.multiply(gamma, tdh2.G_BAR)),
    )
    assert not tdh2.ciphertext_is_valid(malleated)
    with pytest.raises(tdh2.RejectedRequest):
        tdh2.create_share(committee, 1, malleated, label)


def test_tampered_proof_and_swapped_wrapped_key_are_rejected(committee, sealed, target_label) -> None:
    tampered = dataclasses.replace(sealed.ciphertext, f=(sealed.ciphertext.f + 1) % rs.ORDER)
    swapped = dataclasses.replace(sealed.ciphertext, wrapped_key=bytes(len(sealed.ciphertext.wrapped_key)))
    for bad in (tampered, swapped):
        assert not tdh2.ciphertext_is_valid(bad)
        with pytest.raises(tdh2.RejectedRequest):
            tdh2.create_share(committee, 1, bad, target_label)


def test_valid_ciphertext_under_another_authorization_is_rejected(committee, sealed) -> None:
    other = tdh2.Label(epoch="E7", record_id="record-0002", policy_hash=b"\x11" * 32)
    with pytest.raises(tdh2.RejectedRequest):
        tdh2.create_share(committee, 1, sealed.ciphertext, other)


def test_fresh_ciphertext_is_valid(sealed) -> None:
    assert tdh2.ciphertext_is_valid(sealed.ciphertext)


def test_negative_control_attack_succeeds_without_tdh2_checks(committee, sealed, target_label) -> None:
    """Without the label and proof checks (plain threshold KEM), the gamma = 0 attack recovers
    the target's record, so the rejections above are due to TDH2 and not to the test setup."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    attacker_label = tdh2.Label(epoch="E7", record_id="attacker-record", policy_hash=b"\x22" * 32)
    relabelled = dataclasses.replace(sealed.ciphertext, label=attacker_label)
    # A plain-KEM custodian releases x_i * u for any authorized record, with no ciphertext check.
    released = {i: rs.multiply(committee.shares[i], relabelled.u) for i in range(1, T + 1)}
    shared = sharing.combine_in_exponent(released)
    # The attacker re-derives the target's key-encryption key from the target's public label.
    data_key = AESGCM(tdh2._kek(RISTRETTO, shared, target_label)).decrypt(
        sealed.ciphertext.key_nonce, sealed.ciphertext.wrapped_key, target_label.encode())
    recovered = AESGCM(data_key).decrypt(sealed.record_nonce, sealed.record_ciphertext, target_label.encode())
    assert recovered == RECORD
