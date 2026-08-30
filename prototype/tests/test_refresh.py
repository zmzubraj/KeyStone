from __future__ import annotations

import random

import pytest

from keystone.protocol import derive_canary, epoch_bound_context
from keystone.threshold_kem import (
    create_partial_decryption,
    dealer_keygen,
    InsufficientValidShares,
    open_record,
    refresh_epoch_shares,
    seal_record,
    verify_partial_decryption,
)


def _epoch():
    rng = random.Random(2026082901)
    return dealer_keygen(
        5,
        3,
        ["a", "b", "c", "d", "e"],
        epoch_id="refresh-epoch",
        randbelow=rng.randrange,
    )


def test_zero_polynomial_refresh_preserves_public_key_and_authorized_opening() -> None:
    epoch = _epoch()
    sealed = seal_record(
        epoch.public_key,
        epoch.group,
        "record-1",
        b"refresh-safe plaintext",
        b"refresh-test",
    )
    refreshed = refresh_epoch_shares(epoch, randbelow=random.Random(2026082902).randrange)

    assert refreshed.epoch_id == epoch.epoch_id
    assert refreshed.refresh_generation == epoch.refresh_generation + 1
    assert refreshed.public_key == epoch.public_key
    assert refreshed.commitments[0] == epoch.commitments[0]
    assert any(
        refreshed.members[index].share != epoch.members[index].share
        for index in epoch.members
    )

    context = epoch_bound_context(refreshed, b"authorized-dispute")
    partials = [
        create_partial_decryption(
            refreshed.members[index],
            sealed.c1,
            refreshed.group,
            context,
            randbelow=random.Random(2026083000 + index).randrange,
        )
        for index in (1, 2, 3)
    ]
    assert open_record(refreshed, sealed, partials, context) == b"refresh-safe plaintext"


def test_old_and_new_partials_cannot_be_mixed_under_refreshed_epoch() -> None:
    epoch = _epoch()
    refreshed = refresh_epoch_shares(epoch, randbelow=random.Random(2026082903).randrange)
    sealed = seal_record(epoch.public_key, epoch.group, "record-2", b"secret", b"refresh-test")
    old_context = epoch_bound_context(epoch, b"authorized-dispute")
    new_context = epoch_bound_context(refreshed, b"authorized-dispute")

    old_partial = create_partial_decryption(
        epoch.members[1],
        sealed.c1,
        epoch.group,
        old_context,
        randbelow=random.Random(11).randrange,
    )
    new_partials = [
        create_partial_decryption(
            refreshed.members[index],
            sealed.c1,
            refreshed.group,
            new_context,
            randbelow=random.Random(20 + index).randrange,
        )
        for index in (2, 3)
    ]

    assert not verify_partial_decryption(
        refreshed.members[1],
        sealed.c1,
        old_partial,
        refreshed.group,
        new_context,
    )
    with pytest.raises(InsufficientValidShares):
        open_record(refreshed, sealed, [old_partial, *new_partials], new_context)


def test_refresh_generation_changes_canary_and_proof_context() -> None:
    epoch = _epoch()
    refreshed = refresh_epoch_shares(epoch, randbelow=random.Random(2026082904).randrange)

    assert epoch_bound_context(epoch, b"audit-42") != epoch_bound_context(
        refreshed, b"audit-42"
    )
    assert derive_canary(epoch, b"beacon", b"audit-42") != derive_canary(
        refreshed, b"beacon", b"audit-42"
    )
