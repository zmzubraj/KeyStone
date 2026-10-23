"""Repair on alarm and selective withholding (R2c)."""
from __future__ import annotations

import math
import random

import numpy as np

from keystone_r2 import temporal, withholding
from keystone_r2.temporal import DomainShockModel, IndependentModel

LAM, MU = 1 / (7 * 24), 1 / 24


def test_reset_preserves_mass_and_domains() -> None:
    dom = DomainShockModel(8, LAM, MU, 1 / 500, 1 / 6, domains=4)
    dist = dom.stationary()
    out = temporal.reset_members(dom, dist)
    assert math.isclose(out.sum(), 1.0)
    # every domain's members are all up after the reset, domain states keep their marginals
    m1 = dom.m + 1
    for axis in range(4):
        marg = np.moveaxis(out, axis, 0).reshape(2, m1, -1).sum(axis=2)
        assert np.allclose(marg[:, :-1], 0.0)
        before = np.moveaxis(dist, axis, 0).reshape(2, m1, -1).sum(axis=(1, 2))
        assert np.allclose(marg.sum(axis=1), before)
    ind = IndependentModel(6, LAM, MU)
    assert temporal.reset_members(ind, ind.stationary())[-1] == 1.0


def test_no_rejections_gives_stationary_failure() -> None:
    model = IndependentModel(32, LAM, MU)
    # q = 0 accepts always, so repair never triggers and the failure probability is stationary
    metrics = temporal.repair_metrics(model, 6.0, 8, 0, 22, 1.0)
    assert math.isclose(metrics["failure"], temporal.stationary_catastrophic(model, 22), rel_tol=1e-9)
    assert metrics["p_reject"] == 0.0


def test_repair_lowers_failure_and_domain_variant_reduces() -> None:
    ind = IndependentModel(8, LAM, MU)
    dom = DomainShockModel(8, LAM, MU, 0.0, 1.0, domains=4)
    a = temporal.repair_metrics(ind, 6.0, 4, 4, 6, 1.0)
    b = temporal.repair_metrics(dom, 6.0, 4, 4, 6, 1.0)
    for key in ("failure", "undetected", "p_reject"):
        assert math.isclose(a[key], b[key], rel_tol=1e-8, abs_tol=1e-15)
    assert a["failure"] < temporal.stationary_catastrophic(ind, 6)


def test_repair_failure_matches_simulation_small() -> None:
    n, t, s, q, T, dr = 6, 4, 3, 3, 6.0, 1.0
    model = IndependentModel(n, LAM, MU)
    exact = temporal.repair_metrics(model, T, s, q, t, dr)
    rng = random.Random(11)
    up = [rng.random() < MU / (LAM + MU) for _ in range(n)]
    nxt = [rng.expovariate(LAM if u else MU) for u in up]

    def at(time):
        for i in range(n):
            while nxt[i] <= time:
                up[i] = not up[i]
                nxt[i] += rng.expovariate(LAM if up[i] else MU)
        return sum(up)

    fail = rej = 0
    intervals = 120_000
    for m in range(intervals + 2_000):
        a = m * T
        at(a)
        reject = sum(up[i] for i in rng.sample(range(n), s)) < q
        u = rng.random() * T
        if reject and u >= dr:
            at(a + dr)
            for i in range(n):
                up[i] = True
                nxt[i] = a + dr + rng.expovariate(LAM)
        cat = at(a + u) < t
        if reject and u < dr:
            at(a + dr)
            for i in range(n):
                up[i] = True
                nxt[i] = a + dr + rng.expovariate(LAM)
        if m >= 2_000:
            fail += cat
            rej += reject
    assert abs(fail / intervals - exact["failure"]) < 4 * math.sqrt(exact["failure"] / intervals) + 1e-4
    assert abs(rej / intervals - exact["p_reject"]) < 4 * math.sqrt(exact["p_reject"] / intervals) + 1e-4


def test_withholding_formulas() -> None:
    assert math.isclose(withholding.dispute_success(32, 22, 0, 1.0), 1.0)
    assert withholding.dispute_success(32, 22, 11, 1.0) == 0.0
    # withholders always answer audits, so audits pass at least as often as with honest custodians
    assert withholding.audit_pass(32, 8, 8, 11, 0.99) >= withholding.audit_pass(32, 8, 8, 0, 0.99)
    assert withholding.minimal_coalition(32, 22, 1.0, 0.5) == 11
    assert withholding.minimal_coalition(32, 22, 0.9, 0.5) < 11
