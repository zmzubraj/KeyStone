"""Canary audit, batched verification (D2) and group-generic behaviour (ffdhe) for R2."""
from __future__ import annotations

import dataclasses
from collections import Counter

import pytest

from keystone_r2 import audit, dleq, sharing, tdh2
from keystone_r2.groups import FFDHE2048, RISTRETTO

EPOCH, SLOT, BEACON = "E7", 3, b"\x5a" * 32


@pytest.fixture(scope="module")
def committee() -> sharing.Committee:
    return sharing.deal(32, 22)


# ---------------------------------------------------------------- sampler
def test_sample_is_distinct_in_range_and_deterministic() -> None:
    s1 = audit.sample(32, 8, EPOCH, SLOT, BEACON)
    assert len(set(s1)) == 8 and all(1 <= i <= 32 for i in s1)
    assert s1 == audit.sample(32, 8, EPOCH, SLOT, BEACON)
    assert s1 != audit.sample(32, 8, EPOCH, SLOT, b"\x5b" * 32)
    assert sorted(audit.sample(32, 32, EPOCH, SLOT, BEACON)) == list(range(1, 33))


def test_sample_marginals_are_close_to_uniform() -> None:
    counts = Counter()
    trials = 4000
    for k in range(trials):
        counts.update(audit.sample(32, 8, EPOCH, k, BEACON))
    expected = trials * 8 / 32
    # each index's count is Binomial-like with sd ~ 27; allow 5 sd
    assert all(abs(counts[i] - expected) < 5 * 27.5 for i in range(1, 33))


# ---------------------------------------------------------------- audit
def test_canary_is_valid_and_context_bound(committee) -> None:
    x = audit.derive_canary(EPOCH, SLOT, BEACON)
    RISTRETTO.validate(x)
    assert x != audit.derive_canary(EPOCH, SLOT + 1, BEACON)
    assert x != committee.public_key


def test_audit_accepts_with_q_valid_and_rejects_otherwise(committee) -> None:
    canary = audit.derive_canary(EPOCH, SLOT, BEACON)
    sampled = audit.sample(32, 8, EPOCH, SLOT, BEACON)
    good = [audit.respond(committee, i, canary, EPOCH, SLOT, BEACON) for i in sampled]
    assert audit.accepts(committee, EPOCH, SLOT, BEACON, 8, 8, good)
    bad = dataclasses.replace(good[0], value=RISTRETTO.add(good[0].value, RISTRETTO.generator()))
    assert not audit.accepts(committee, EPOCH, SLOT, BEACON, 8, 8, [bad] + good[1:])
    assert audit.accepts(committee, EPOCH, SLOT, BEACON, 8, 7, [bad] + good[1:])
    # duplicates count once; non-sampled custodians are ignored
    outsider = next(i for i in range(1, 33) if i not in sampled)
    extra = audit.respond(committee, outsider, canary, EPOCH, SLOT, BEACON)
    assert not audit.accepts(committee, EPOCH, SLOT, BEACON, 8, 8, good[:7] + [good[0], extra])


def test_response_for_another_slot_is_rejected(committee) -> None:
    canary = audit.derive_canary(EPOCH, SLOT, BEACON)
    response = audit.respond(committee, 1, canary, EPOCH, SLOT, BEACON)
    other_canary = audit.derive_canary(EPOCH, SLOT + 1, BEACON)
    assert not audit.response_is_valid(committee, other_canary, response, EPOCH, SLOT + 1, BEACON)


# ---------------------------------------------------------------- batch verification (D2)
@pytest.fixture(scope="module")
def sealed_and_shares(committee):
    label = tdh2.Label("E7", "record-batch", b"\x33" * 32)
    sealed = tdh2.seal(committee.public_key, label, b"batch test")
    shares = [tdh2.create_share(committee, i, sealed.ciphertext, label) for i in range(1, 23)]
    return sealed, shares


def test_batch_accepts_valid_and_rejects_one_bad(committee, sealed_and_shares) -> None:
    sealed, shares = sealed_and_shares
    assert tdh2.shares_are_valid_batch(committee, sealed.ciphertext, shares)
    bad = dataclasses.replace(shares[5], value=RISTRETTO.add(shares[5].value, RISTRETTO.generator()))
    assert not tdh2.shares_are_valid_batch(committee, sealed.ciphertext, shares[:5] + [bad] + shares[6:])


def test_open_record_batch_mode_and_fallback(committee, sealed_and_shares) -> None:
    sealed, shares = sealed_and_shares
    assert tdh2.open_record(committee, sealed, shares, batch=True) == b"batch test"
    extra = [tdh2.create_share(committee, i, sealed.ciphertext, sealed.ciphertext.label) for i in (23, 24)]
    bad = dataclasses.replace(shares[0], value=RISTRETTO.add(shares[0].value, RISTRETTO.generator()))
    assert tdh2.open_record(committee, sealed, [bad] + shares[1:] + extra, batch=True) == b"batch test"


def test_dleq_batch_empty_and_tampered() -> None:
    assert dleq.verify_batch([], RISTRETTO.generator(), RISTRETTO.hash_to_group(b"b", b"2"))


# ---------------------------------------------------------------- ffdhe (group-generic)
@pytest.fixture(scope="module")
def small_ffdhe_committee() -> sharing.Committee:
    return sharing.deal(5, 3, FFDHE2048)


def test_ffdhe_feldman_tdh2_audit_and_batch(small_ffdhe_committee) -> None:
    committee = small_ffdhe_committee
    assert all(sharing.verify_share(committee, i, x) for i, x in committee.shares.items())
    label = tdh2.Label("E1", "record-ffdhe", b"\x44" * 32)
    sealed = tdh2.seal(committee.public_key, label, b"ffdhe record", FFDHE2048)
    assert tdh2.ciphertext_is_valid(sealed.ciphertext)
    shares = [tdh2.create_share(committee, i, sealed.ciphertext, label) for i in (1, 3, 5)]
    assert tdh2.open_record(committee, sealed, shares) == b"ffdhe record"
    assert tdh2.open_record(committee, sealed, shares, batch=True) == b"ffdhe record"
    relabelled = dataclasses.replace(sealed.ciphertext, label=tdh2.Label("E1", "attacker", b"\x44" * 32))
    with pytest.raises(tdh2.RejectedRequest):
        tdh2.create_share(committee, 1, relabelled, relabelled.label)
    canary = audit.derive_canary(EPOCH, SLOT, BEACON, FFDHE2048)
    sampled = audit.sample(5, 3, EPOCH, SLOT, BEACON)
    responses = [audit.respond(committee, i, canary, EPOCH, SLOT, BEACON) for i in sampled]
    assert audit.accepts(committee, EPOCH, SLOT, BEACON, 3, 3, responses)
