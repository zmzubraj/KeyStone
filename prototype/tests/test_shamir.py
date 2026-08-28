import random

from keystone.group import RESEARCH_GROUP
from keystone.shamir import (
    feldman_commitments,
    interpolate_at_zero,
    share_secret,
    verify_share,
)


def test_any_threshold_subset_reconstructs_secret() -> None:
    rng = random.Random(7)
    secret = 123456789
    coefficients, shares = share_secret(
        secret=secret,
        n=7,
        threshold=4,
        modulus=RESEARCH_GROUP.q,
        randbelow=rng.randrange,
    )

    recovered = interpolate_at_zero(
        [(1, shares[1]), (3, shares[3]), (5, shares[5]), (7, shares[7])],
        RESEARCH_GROUP.q,
    )

    assert recovered == secret
    assert len(coefficients) == 4


def test_feldman_commitments_reject_corrupted_share() -> None:
    rng = random.Random(11)
    coefficients, shares = share_secret(
        secret=987654321,
        n=5,
        threshold=3,
        modulus=RESEARCH_GROUP.q,
        randbelow=rng.randrange,
    )
    commitments = feldman_commitments(coefficients, RESEARCH_GROUP)

    assert verify_share(2, shares[2], commitments, RESEARCH_GROUP)
    assert not verify_share(2, (shares[2] + 1) % RESEARCH_GROUP.q, commitments, RESEARCH_GROUP)
