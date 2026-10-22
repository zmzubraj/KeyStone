"""W1 temporal model: lumped chains, filter and metrics against brute force on small committees."""
from __future__ import annotations

import itertools
import math

import numpy as np
import pytest

from keystone_r2 import temporal
from keystone_r2.temporal import DomainShockModel, IndependentModel

LAM, MU = 1 / 72.0, 1 / 6.0


def expm(generator: np.ndarray, u: float) -> np.ndarray:
    """Matrix exponential by scaling and squaring with a Taylor series (independent of the closed forms)."""
    a = generator * u
    squarings = max(0, int(math.ceil(math.log2(max(np.abs(a).sum(axis=1).max(), 1e-300)))) + 4)
    a = a / 2**squarings
    result, term = np.eye(len(a)), np.eye(len(a))
    for i in range(1, 30):
        term = term @ a / i
        result = result + term
    for _ in range(squarings):
        result = result @ result
    return result


def full_generator(rates: list[tuple[float, float]]) -> np.ndarray:
    """Generator of independent two-state chains (state bit 1 = up) over all 2**len(rates) joint states."""
    size = 2 ** len(rates)
    q = np.zeros((size, size))
    for state in range(size):
        for i, (lam, mu) in enumerate(rates):
            other = state ^ (1 << i)
            q[state, other] = lam if state >> i & 1 else mu
        q[state, state] = -q[state].sum()
    return q


def test_count_transition_matches_full_chain_expm() -> None:
    n, u = 4, 5.0
    full = expm(full_generator([(LAM, MU)] * n), u)
    lumped = temporal.count_transition(n, LAM, MU, u)
    for state in range(2**n):
        k = bin(state).count("1")
        by_count = np.zeros(n + 1)
        for other in range(2**n):
            by_count[bin(other).count("1")] += full[state, other]
        assert np.allclose(by_count, lumped[k], atol=1e-12)


def test_chapman_kolmogorov_and_stationarity() -> None:
    model = IndependentModel(6, LAM, MU)
    a, b = temporal.count_transition(6, LAM, MU, 2.0), temporal.count_transition(6, LAM, MU, 3.0)
    assert np.allclose(a @ b, temporal.count_transition(6, LAM, MU, 5.0), atol=1e-13)
    assert np.allclose(a.sum(axis=1), 1.0)
    assert np.allclose(model.propagate(model.stationary(), 7.0), model.stationary(), atol=1e-14)


def test_domain_model_matches_full_chain_expm() -> None:
    # 2 domains of 2 custodians; joint bits: members 0..3 (member i in domain i // 2), domains 4..5
    lam_d, mu_d, u = 1 / 200.0, 1 / 6.0, 4.0
    rates = [(LAM, MU)] * 4 + [(lam_d, mu_d)] * 2
    full = expm(full_generator(rates), u)
    model = DomainShockModel(4, LAM, MU, lam_d, mu_d, domains=2)

    def ready(state: int) -> int:
        return sum(1 for i in range(4) if state >> i & 1 and state >> (4 + i // 2) & 1)

    def model_index(state: int) -> tuple[int, int]:
        out = []
        for d in range(2):
            members = sum(state >> i & 1 for i in (2 * d, 2 * d + 1))
            out.append((state >> (4 + d) & 1) * 3 + members)
        return tuple(out)

    for start in (0b111111, 0b011111, 0b100101):
        dist = np.zeros(model.ready.shape)
        dist[model_index(start)] = 1.0
        got = model.propagate(dist, u)
        want = np.zeros(5)
        for other in range(2**6):
            want[ready(other)] += full[start, other]
        got_k = np.array([got[model.ready == k].sum() for k in range(5)])
        assert np.allclose(got_k, want, atol=1e-12)


def test_domain_model_without_shocks_reduces_to_independent() -> None:
    dom = DomainShockModel(8, LAM, MU, 0.0, 1.0, domains=4)
    ind = IndependentModel(8, LAM, MU)
    for s, q, t, T in ((4, 4, 6, 6.0), (6, 5, 5, 24.0)):
        assert math.isclose(temporal.stationary_undetected(dom, T, s, q, t),
                            temporal.stationary_undetected(ind, T, s, q, t), rel_tol=1e-10, abs_tol=1e-15)
        assert math.isclose(temporal.posterior_worst_risk(dom, T, s, q, t)["risk"],
                            temporal.posterior_worst_risk(ind, T, s, q, t)["risk"], rel_tol=1e-8, abs_tol=1e-15)


def test_acceptance_matches_paper_theorem_1() -> None:
    accept = temporal.acceptance(32, 8, 8)
    assert math.isclose(accept[21], math.comb(21, 8) / math.comb(32, 8))
    assert accept[7] == 0.0 and accept[32] == 1.0
    assert all(x <= y for x, y in zip(accept, accept[1:]))


def test_filter_matches_path_enumeration() -> None:
    n, s, q, T = 4, 2, 2, 6.0
    model = IndependentModel(n, LAM, MU)
    outcomes = [True, False, True]
    accept = np.asarray(temporal.acceptance(n, s, q))
    pi, step = model.stationary(), temporal.count_transition(n, LAM, MU, T)
    post = np.zeros(n + 1)
    for path in itertools.product(range(n + 1), repeat=len(outcomes)):
        weight = pi[path[0]]
        for i, k in enumerate(path):
            if i:
                weight *= step[path[i - 1], k]
            weight *= accept[k] if outcomes[i] else 1 - accept[k]
        post[path[-1]] += weight
    assert np.allclose(post / post.sum(), temporal.posterior_after(model, T, s, q, outcomes), atol=1e-14)


def test_fixed_point_is_invariant() -> None:
    model = IndependentModel(32, 1 / (7 * 24), 1 / 24)
    fixed, steps = temporal.accepted_fixed_point(model, 6.0, 16, 14)
    again = temporal.filter_step(model, fixed, 6.0, temporal.emission(model, 16, 14))
    assert steps > 0 and np.abs(again - fixed).sum() < 1e-12


@pytest.mark.parametrize("T", [1.0, 6.0, 24.0])
def test_bound_floor_and_metric_ordering(T: float) -> None:
    n, t, s, q = 32, 22, 8, 8
    lam, mu = 1 / (7 * 24), 1 / 24
    model = IndependentModel(n, lam, mu)
    metric = temporal.stationary_undetected(model, T, s, q, t)
    assert metric <= temporal.undetected_bound(n, lam, mu, T, s, q, t) * (1 + 1e-12)
    assert temporal.undetected_floor(model, s, q, t) <= metric * (1 + 1e-9)
    assert metric <= temporal.stationary_catastrophic(model, t)


def test_bound_is_non_decreasing_in_T() -> None:
    values = [temporal.undetected_bound(32, 1 / (7 * 24), 1 / 24, T, 16, 14, 22) for T in np.geomspace(0.1, 2000, 40)]
    assert all(b >= a for a, b in zip(values, values[1:]))


def test_metric_two_tends_to_floor() -> None:
    model = IndependentModel(32, 1 / (7 * 24), 1 / 24)
    floor = temporal.undetected_floor(model, 8, 8, 22)
    assert math.isclose(temporal.stationary_undetected(model, 1e-6, 8, 8, 22), floor, rel_tol=1e-5)


def test_largest_interval_bisection() -> None:
    result = temporal.largest_interval(lambda T: T / 10.0, 0.5, 0.01, 100.0)
    assert result["status"] == "bisected" and math.isclose(result["T"], 5.0, rel_tol=1e-9)
    assert temporal.largest_interval(lambda T: 1.0, 0.5, 0.01, 100.0)["status"] == "infeasible_at_lo"
