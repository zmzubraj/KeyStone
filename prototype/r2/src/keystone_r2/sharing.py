"""Dealer Shamir sharing with Feldman commitments over ristretto255.

The dealer is the prototype's explicit substitution for distributed key
generation (as in R1). Shares are scalars modulo the group order; custodian
``i`` (1-based) holds ``x_i = f(i)`` and publishes ``h_i = x_i * G``.
"""
from __future__ import annotations

from dataclasses import dataclass

from keystone_r2 import ristretto as rs


@dataclass(frozen=True)
class Committee:
    """Public epoch material plus the custodians' private shares (dealer output)."""

    n: int
    t: int
    public_key: bytes
    public_shares: dict[int, bytes]
    shares: dict[int, int]
    commitments: tuple[bytes, ...]


def deal(n: int, t: int) -> Committee:
    """Share a fresh random secret with a degree t-1 polynomial among n custodians."""
    if not 1 <= t <= n:
        raise ValueError("require 1 <= t <= n")
    coefficients = [rs.random_scalar() for _ in range(t)]
    shares = {i: sum(c * pow(i, k, rs.ORDER) for k, c in enumerate(coefficients)) % rs.ORDER
              for i in range(1, n + 1)}
    commitments = tuple(rs.base_multiply(c) for c in coefficients)
    return Committee(
        n=n,
        t=t,
        public_key=commitments[0],
        public_shares={i: rs.base_multiply(x) for i, x in shares.items()},
        shares=shares,
        commitments=commitments,
    )


def verify_share(committee: Committee, index: int, share: int) -> bool:
    """Feldman check: ``share*G == sum_k index^k * C_k``."""
    expected = None
    for k, commitment in enumerate(committee.commitments):
        exponent = pow(index, k, rs.ORDER)
        term = rs.multiply(exponent, commitment)
        expected = term if expected is None else rs.add(expected, term)
    return rs.base_multiply(share) == expected


def lagrange_at_zero(index: int, indices: list[int]) -> int:
    """Lagrange coefficient for ``index`` at 0 over the distinct ``indices``."""
    if len(set(indices)) != len(indices) or index not in indices:
        raise ValueError("indices must be distinct and contain index")
    numerator, denominator = 1, 1
    for other in indices:
        if other != index:
            numerator = numerator * (-other) % rs.ORDER
            denominator = denominator * (index - other) % rs.ORDER
    return numerator * pow(denominator, -1, rs.ORDER) % rs.ORDER


def combine_in_exponent(partials: dict[int, bytes]) -> bytes:
    """Interpolate ``sum_i lambda_i * P_i`` for partials keyed by distinct custodian index."""
    indices = sorted(partials)
    combined = None
    for i in indices:
        term = rs.multiply(lagrange_at_zero(i, indices), partials[i])
        combined = term if combined is None else rs.add(combined, term)
    if combined is None:
        raise ValueError("no partials to combine")
    return combined
