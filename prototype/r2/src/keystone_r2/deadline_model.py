"""Order-statistic model of dispute completion in the emulated testbed.

A dispute succeeds by time x when at least t of the n_live custodians that can answer
have delivered a valid partial by x. Each live custodian's response is lost with
probability 1 - (1 - loss)^2 (request or response dropped) and otherwise arrives after
a round trip R = d_in + d_out + fixed, with d_in and d_out independent lognormal one-way
delays (median, sigma) and fixed the deterministic work and overhead outside the
network. Responses are independent given the profile, so the number delivered by x is
Binomial(n_live, F(x)) with F(x) = (1 - loss)^2 * Pr[d_in + d_out <= x - fixed], and

    Pr[success by x] = Pr[Binomial(n_live, F(x)) >= t].

This ignores the combiner's own verification after the t-th arrival, which the caller
adds to ``fixed`` (a conservative shift). With median 0 the network contributes nothing.
"""
from __future__ import annotations

import math

import numpy as np


def two_leg_cdf(x_ms: float, median_ms: float, sigma: float, points: int = 40_001) -> float:
    """Pr[d_in + d_out <= x] for two independent lognormal legs (numerical convolution)."""
    if median_ms == 0:
        return 1.0 if x_ms >= 0 else 0.0
    if x_ms <= 0:
        return 0.0
    mu = math.log(median_ms)
    xs = np.linspace(x_ms * 1e-9, x_ms, points)
    pdf = np.exp(-0.5 * ((np.log(xs) - mu) / sigma) ** 2) / (xs * sigma * math.sqrt(2 * math.pi))
    rest = np.array([0.5 * math.erfc(-((math.log(x_ms - x) - mu) / sigma) / math.sqrt(2)) if x < x_ms else 0.0
                     for x in xs])
    return float(min(1.0, max(0.0, np.trapezoid(pdf * rest, xs))))


def binomial_tail(n: int, p: float, t: int) -> float:
    """Pr[Binomial(n, p) >= t]."""
    if t > n:
        return 0.0
    return float(min(1.0, sum(math.comb(n, k) * p**k * (1 - p) ** (n - k) for k in range(t, n + 1))))


def success_probability(x_ms: float, n_live: int, t: int, median_ms: float, sigma: float, loss: float,
                        fixed_ms: float) -> float:
    """Pr[at least t of n_live responses delivered by x]."""
    f = (1 - loss) ** 2 * two_leg_cdf(x_ms - fixed_ms, median_ms, sigma)
    return binomial_tail(n_live, f, t)


def order_statistic_deadline(n_live: int, t: int, median_ms: float, sigma: float, loss: float, fixed_ms: float,
                             target: float = 0.99, hi_ms: float = 60_000.0) -> float:
    """Smallest x with Pr[success by x] >= target; inf if unattainable (too few live custodians or too much loss)."""
    if n_live < t or binomial_tail(n_live, (1 - loss) ** 2, t) < target:
        return math.inf
    if median_ms == 0:
        return fixed_ms
    lo, hi = fixed_ms, fixed_ms + hi_ms
    if success_probability(hi, n_live, t, median_ms, sigma, loss, fixed_ms) < target:
        return math.inf
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if success_probability(mid, n_live, t, median_ms, sigma, loss, fixed_ms) >= target:
            hi = mid
        else:
            lo = mid
    return hi
