"""Dealer Shamir sharing with Feldman commitments over any R2 group.

The dealer is the prototype's explicit substitution for distributed key
generation (as in R1). Shares are scalars modulo the group order; custodian
``i`` (1-based) holds ``x_i = f(i)`` and publishes ``h_i = x_i * G``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from keystone_r2.groups import RISTRETTO, Element


@dataclass(frozen=True)
class Committee:
    """Public epoch material plus the custodians' private shares (dealer output)."""

    n: int
    t: int
    public_key: Element
    public_shares: dict[int, Element]
    shares: dict[int, int]
    commitments: tuple[Element, ...]
    group: Any = RISTRETTO


def deal(n: int, t: int, group=RISTRETTO) -> Committee:
    """Share a fresh random secret with a degree t-1 polynomial among n custodians."""
    if not 1 <= t <= n:
        raise ValueError("require 1 <= t <= n")
    coefficients = [group.random_scalar() for _ in range(t)]
    shares = {i: sum(c * pow(i, k, group.order) for k, c in enumerate(coefficients)) % group.order
              for i in range(1, n + 1)}
    commitments = tuple(group.base_mul(c) for c in coefficients)
    return Committee(
        n=n,
        t=t,
        public_key=commitments[0],
        public_shares={i: group.base_mul(x) for i, x in shares.items()},
        shares=shares,
        commitments=commitments,
        group=group,
    )


def verify_share(committee: Committee, index: int, share: int) -> bool:
    """Feldman check: ``share*G == sum_k index^k * C_k``."""
    group = committee.group
    expected = None
    for k, commitment in enumerate(committee.commitments):
        term = group.mul(pow(index, k, group.order), commitment)
        expected = term if expected is None else group.add(expected, term)
    return group.base_mul(share) == expected


def lagrange_at_zero(index: int, indices: list[int], order: int) -> int:
    """Lagrange coefficient for ``index`` at 0 over the distinct ``indices`` modulo ``order``."""
    if len(set(indices)) != len(indices) or index not in indices:
        raise ValueError("indices must be distinct and contain index")
    numerator, denominator = 1, 1
    for other in indices:
        if other != index:
            numerator = numerator * (-other) % order
            denominator = denominator * (index - other) % order
    return numerator * pow(denominator, -1, order) % order


def combine_in_exponent(partials: dict[int, Element], group=RISTRETTO) -> Element:
    """Interpolate ``sum_i lambda_i * P_i`` for partials keyed by distinct custodian index."""
    indices = sorted(partials)
    combined = None
    for i in indices:
        term = group.mul(lagrange_at_zero(i, indices, group.order), partials[i])
        combined = term if combined is None else group.add(combined, term)
    if combined is None:
        raise ValueError("no partials to combine")
    return combined
