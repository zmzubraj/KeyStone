"""Order-statistic deadline model against Monte Carlo and limiting cases."""
from __future__ import annotations

import math
import random

from keystone_r2 import deadline_model as dm


def test_two_leg_cdf_matches_monte_carlo() -> None:
    rng = random.Random(7)
    med, sig = 120.0, 0.6
    draws = [med * math.exp(sig * rng.gauss(0, 1)) + med * math.exp(sig * rng.gauss(0, 1)) for _ in range(200_000)]
    for x in (150.0, 300.0, 600.0, 1200.0):
        mc = sum(d <= x for d in draws) / len(draws)
        assert abs(dm.two_leg_cdf(x, med, sig) - mc) < 4e-3


def test_zero_median_is_a_step() -> None:
    assert dm.two_leg_cdf(0.0, 0, 0) == 1.0 and dm.two_leg_cdf(-1e-9, 0, 0) == 0.0


def test_success_probability_limits_and_monotonicity() -> None:
    args = dict(n_live=22, t=22, median_ms=120.0, sigma=0.6, loss=0.0, fixed_ms=4.0)
    values = [dm.success_probability(x, **args) for x in (100.0, 500.0, 1000.0, 3000.0)]
    assert values == sorted(values) and values[-1] > 0.999
    # with exactly t live, success is the product of t independent arrivals
    f = dm.two_leg_cdf(996.0, 120.0, 0.6)
    assert math.isclose(dm.success_probability(1000.0, **args), f**22, rel_tol=1e-9)
    assert dm.success_probability(1e6, 21, 22, 120.0, 0.6, 0.0, 0.0) == 0.0


def test_order_statistic_deadline() -> None:
    x = dm.order_statistic_deadline(22, 22, 120.0, 0.6, 0.0, 4.0, target=0.99)
    assert math.isclose(dm.success_probability(x, 22, 22, 120.0, 0.6, 0.0, 4.0), 0.99, abs_tol=1e-6)
    assert dm.order_statistic_deadline(21, 22, 120.0, 0.6, 0.0, 4.0) == math.inf
    assert dm.order_statistic_deadline(32, 22, 0, 0, 0.0, 7.5) == 7.5
    # heavy loss can make the target unattainable even with time
    assert dm.order_statistic_deadline(22, 22, 120.0, 0.6, 0.02, 4.0, target=0.99) == math.inf
