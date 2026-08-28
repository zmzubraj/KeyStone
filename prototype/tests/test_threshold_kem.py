import random

import pytest

from keystone.threshold_kem import (
    InsufficientValidShares,
    create_partial_decryption,
    dealer_keygen,
    open_record,
    seal_record,
)


def _epoch():
    rng = random.Random(31)
    domains = ["aws-eu", "aws-eu", "gcp-us", "gcp-us", "azure-ap", "azure-ap", "independent"]
    return dealer_keygen(7, 5, domains, randbelow=rng.randrange)


def test_threshold_partials_open_encrypted_record() -> None:
    epoch = _epoch()
    sealed = seal_record(
        epoch.public_key,
        epoch.group,
        record_id="record-42",
        plaintext=b"private inference input and output",
        aad=b"rollup-7",
    )
    context = b"dispute:record-42:verifier-set-8"
    partials = [
        create_partial_decryption(epoch.members[i], sealed.c1, epoch.group, context)
        for i in [1, 2, 4, 5, 7]
    ]

    opened = open_record(epoch, sealed, partials, context)

    assert opened == b"private inference input and output"


def test_fewer_than_threshold_valid_partials_cannot_open_record() -> None:
    epoch = _epoch()
    sealed = seal_record(epoch.public_key, epoch.group, "record-7", b"secret", b"aad")
    context = b"dispute:record-7"
    partials = [
        create_partial_decryption(epoch.members[i], sealed.c1, epoch.group, context)
        for i in [1, 2, 3, 4]
    ]

    with pytest.raises(InsufficientValidShares):
        open_record(epoch, sealed, partials, context)


def test_invalid_partial_is_excluded_before_threshold_counting() -> None:
    epoch = _epoch()
    sealed = seal_record(epoch.public_key, epoch.group, "record-8", b"secret", b"aad")
    context = b"dispute:record-8"
    partials = [
        create_partial_decryption(epoch.members[i], sealed.c1, epoch.group, context)
        for i in [1, 2, 3, 4, 5]
    ]
    partials[0] = partials[0].with_value((partials[0].value * epoch.group.g) % epoch.group.p)

    with pytest.raises(InsufficientValidShares):
        open_record(epoch, sealed, partials, context)
