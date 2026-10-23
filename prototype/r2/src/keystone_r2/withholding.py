"""Selective withholding (R2c, design R2C-DESIGN.md, item M1).

w selective custodians answer every audit but withhold the targeted dispute; the other n - w
custodians are each ready independently with probability v. The dispute succeeds if and only if
at least t non-withholders are ready; the audit sees w + Bin(n - w, v) ready custodians.
"""
from __future__ import annotations

import math

from keystone_r2.temporal import acceptance


def _binom(n: int, p: float, k: int) -> float:
    return math.comb(n, k) * p**k * (1 - p) ** (n - k)


def dispute_success(n: int, t: int, w: int, v: float) -> float:
    return sum(_binom(n - w, v, k) for k in range(t, n - w + 1))


def audit_pass(n: int, s: int, q: int, w: int, v: float) -> float:
    accept = acceptance(n, s, q)
    return sum(_binom(n - w, v, k) * accept[w + k] for k in range(n - w + 1))


def minimal_coalition(n: int, t: int, v: float, failure_target: float) -> int | None:
    """Smallest w with Pr[dispute fails] >= failure_target, or None if even w = n - t + 1 ... n fails to reach it."""
    for w in range(0, n + 1):
        if 1 - dispute_success(n, t, w, v) >= failure_target:
            return w
    return None
