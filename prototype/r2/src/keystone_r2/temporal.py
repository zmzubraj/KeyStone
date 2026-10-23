"""Temporal readiness model for W1 (family R2_TEMPORAL_EXACT of the R2 freeze).

Non-selective faults: a custodian is ready for an audit exactly when it is ready
for a dispute. Each custodian alternates between ready and not ready as an
independent two-state continuous-time Markov chain (failure rate ``lam``, repair
rate ``mu``). In the domain-shock variant each of ``domains`` equal domains also
fails as a unit (rate ``lam_d``) and recovers (rate ``mu_d``); a custodian is
ready when both it and its domain are up.

Audits run every ``T`` with a fresh uniform sample of ``s`` custodians and
accept when at least ``q`` sampled custodians are ready, so the emission
probability given ``k`` ready custodians is the hypergeometric tail of the
paper's Theorem 1. Disputes arrive independently of the process.

The hidden state is

* independent model: ``K``, the number of ready custodians (a lumped,
  birth--death chain whose transition over time ``u`` is a convolution of two
  binomials, W1-THEOREMS.md, Lemma 1);
* domain-shock model: for every domain the pair (domain up, number of its
  members individually up), a product of per-domain chains (Lemma 2). ``K`` is
  a function of this state. The freeze names this chain "(domain states, k)";
  the per-domain member counts are needed for the chain to be Markov.

Distributions over the hidden state are numpy arrays; ``Model.ready`` gives
``K`` for every state, with the same shape.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

HOUR = 1.0
DAY = 24.0 * HOUR


def flip_probabilities(lam: float, mu: float, u: float) -> tuple[float, float]:
    """``(Pr[up at u | up at 0], Pr[up at u | down at 0])`` for one two-state chain."""
    a = mu / (lam + mu)
    decay = math.exp(-(lam + mu) * u)
    return a + (1.0 - a) * decay, a * (1.0 - decay)


def binomial_pmf(n: int, p: float) -> np.ndarray:
    return np.array([math.comb(n, i) * p**i * (1.0 - p) ** (n - i) for i in range(n + 1)])


def count_transition(n: int, lam: float, mu: float, u: float) -> np.ndarray:
    """Transition matrix over time ``u`` of the number of up members among ``n`` independent chains.

    Row ``k``: the ``k`` up members stay up with ``p_uu`` and the ``n - k`` down
    members come up with ``p_du``, independently, so the next count is the sum of
    two binomials.
    """
    p_uu, p_du = flip_probabilities(lam, mu, u)
    matrix = np.zeros((n + 1, n + 1))
    for k in range(n + 1):
        matrix[k] = np.convolve(binomial_pmf(k, p_uu), binomial_pmf(n - k, p_du))
    return matrix


@lru_cache(maxsize=None)
def acceptance(n: int, s: int, q: int) -> tuple[float, ...]:
    """``Pr[audit accepts | k ready]`` for k = 0..n (hypergeometric tail, paper Theorem 1)."""
    total = math.comb(n, s)
    return tuple(sum(math.comb(k, j) * math.comb(n - k, s - j) for j in range(q, min(s, k) + 1)) / total
                 for k in range(n + 1))


@dataclass
class IndependentModel:
    """``n`` custodians, each an independent two-state chain; hidden state ``K``."""

    n: int
    lam: float
    mu: float
    _cache: dict = field(default_factory=dict, repr=False)

    @property
    def ready(self) -> np.ndarray:
        return np.arange(self.n + 1)

    def stationary(self) -> np.ndarray:
        return binomial_pmf(self.n, self.mu / (self.lam + self.mu))

    def propagate(self, dist: np.ndarray, u: float) -> np.ndarray:
        if u not in self._cache:
            self._cache[u] = count_transition(self.n, self.lam, self.mu, u)
        return dist @ self._cache[u]


@dataclass
class DomainShockModel:
    """``domains`` domains of ``n // domains`` custodians; hidden state per domain is (domain up, members up)."""

    n: int
    lam: float
    mu: float
    lam_d: float
    mu_d: float
    domains: int = 4
    _cache: dict = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        if self.n % self.domains:
            raise ValueError("domains must divide n")
        self.m = self.n // self.domains
        # per-domain state index: domain_up * (m + 1) + members_up
        per_domain = np.array([d * j for d in (0, 1) for j in range(self.m + 1)])
        grids = np.meshgrid(*([per_domain] * self.domains), indexing="ij")
        self._ready = sum(grids)

    @property
    def ready(self) -> np.ndarray:
        return self._ready

    def _domain_transition(self, u: float) -> np.ndarray:
        d_uu, d_du = flip_probabilities(self.lam_d, self.mu_d, u)
        domain = np.array([[1.0 - d_du, d_du], [1.0 - d_uu, d_uu]])  # rows/cols: down, up
        return np.kron(domain, count_transition(self.m, self.lam, self.mu, u))

    def stationary(self) -> np.ndarray:
        a_d = self.mu_d / (self.lam_d + self.mu_d)
        one = np.kron(np.array([1.0 - a_d, a_d]), binomial_pmf(self.m, self.mu / (self.lam + self.mu)))
        dist = one
        for _ in range(self.domains - 1):
            dist = np.multiply.outer(dist, one)
        return dist

    def propagate(self, dist: np.ndarray, u: float) -> np.ndarray:
        if u not in self._cache:
            self._cache[u] = self._domain_transition(u)
        step = self._cache[u]
        for axis in range(self.domains):
            dist = np.moveaxis(np.tensordot(dist, step, axes=([axis], [0])), -1, axis)
        return dist


def emission(model, s: int, q: int) -> np.ndarray:
    """``Pr[accept | state]`` for every hidden state."""
    return np.asarray(acceptance(model.n, s, q))[model.ready]


def catastrophic_mass(model, dist: np.ndarray, t: int) -> float:
    """``Pr[K < t]`` under ``dist`` (mass, if ``dist`` is not normalized)."""
    return float(dist[model.ready < t].sum())


def filter_step(model, dist: np.ndarray, T: float, accept: np.ndarray, accepted: bool = True) -> np.ndarray:
    """One step of the forward recursion: predict over ``T``, condition on the audit outcome, normalize."""
    predicted = model.propagate(dist, T)
    weighted = predicted * (accept if accepted else 1.0 - accept)
    return weighted / weighted.sum()


def posterior_after(model, T: float, s: int, q: int, outcomes: list[bool]) -> np.ndarray:
    """Filtering distribution just after the given audit outcomes, starting stationary before the first audit.

    The first audit sees the stationary distribution itself (no prediction step).
    """
    accept = emission(model, s, q)
    dist = model.stationary()
    for i, accepted in enumerate(outcomes):
        if i:
            dist = model.propagate(dist, T)
        dist = dist * (accept if accepted else 1.0 - accept)
        dist = dist / dist.sum()
    return dist


def accepted_fixed_point(model, T: float, s: int, q: int, tol: float = 1e-13, max_steps: int = 200_000,
                         start: np.ndarray | None = None) -> tuple[np.ndarray, int]:
    """Limit of the posterior after an unbroken run of accepted audits (W1-THEOREMS.md, Proposition 4).

    The limit does not depend on the start (Proposition 4); ``start`` only speeds up convergence.
    """
    accept = emission(model, s, q)
    dist = posterior_after(model, T, s, q, [True]) if start is None else start
    for step in range(1, max_steps + 1):
        nxt = filter_step(model, dist, T, accept)
        if np.abs(nxt - dist).sum() < tol:
            return nxt, step
        dist = nxt
    raise RuntimeError(f"posterior did not converge in {max_steps} steps")


def risk_curve(model, dist: np.ndarray, T: float, t: int, points: int = 96) -> tuple[np.ndarray, np.ndarray]:
    """``Pr[K(u) < t]`` for ``u`` on a grid of ``[0, T]`` starting from ``dist`` (the endpoint is the limit u -> T)."""
    us = np.linspace(0.0, T, points + 1)
    return us, np.array([catastrophic_mass(model, model.propagate(dist, float(u)), t) for u in us])


def posterior_worst_risk(model, T: float, s: int, q: int, t: int, points: int = 96,
                         start: np.ndarray | None = None) -> dict:
    """Metric 1: sup over the dispute offset of the fixed-point posterior risk given all audits accepted."""
    fixed, steps = accepted_fixed_point(model, T, s, q, start=start)
    us, risks = risk_curve(model, fixed, T, t, points)
    worst = int(np.argmax(risks))
    return {"risk": float(risks[worst]), "u_worst": float(us[worst]), "risk_at_audit": float(risks[0]),
            "steps": steps, "monotone_in_u": bool(np.all(np.diff(risks) >= -1e-15)), "fixed_point": fixed}


_GL_NODES, _GL_WEIGHTS = np.polynomial.legendre.leggauss(24)


def _average_over_interval(fn, T: float) -> float:
    """Mean of ``fn(u)`` for ``u`` uniform on ``[0, T)`` (24-point Gauss--Legendre; ``fn`` is a sum of exponentials)."""
    us = 0.5 * T * (_GL_NODES + 1.0)
    return float(0.5 * sum(w * fn(float(u)) for u, w in zip(us, _GL_WEIGHTS)))


def stationary_undetected(model, T: float, s: int, q: int, t: int) -> float:
    """Metric 2: stationary ``Pr[K(tau) < t and the most recent audit before tau accepted]``, u uniform on [0, T)."""
    joint = model.stationary() * emission(model, s, q)
    return _average_over_interval(lambda u: catastrophic_mass(model, model.propagate(joint, u), t), T)


def stationary_catastrophic(model, t: int) -> float:
    """``Pr[K < t]`` under the stationary distribution (no conditioning on audits)."""
    return catastrophic_mass(model, model.stationary(), t)


def undetected_floor(model, s: int, q: int, t: int) -> float:
    """``lim_{T -> 0}`` of metric 2: catastrophic states the audit itself accepts (Corollary 6)."""
    return catastrophic_mass(model, model.stationary() * emission(model, s, q), t)


def undetected_bound(n: int, lam: float, mu: float, T: float, s: int, q: int, t: int) -> float:
    """Closed-form upper bound on metric 2 for the independent model (Theorem 5)."""
    pi = binomial_pmf(n, mu / (lam + mu))
    accept = acceptance(n, s, q)
    p_uu, _ = flip_probabilities(lam, mu, T)
    low = accept[t - 1] * float(pi[:t].sum())
    high = sum(pi[k] * accept[k] * float(binomial_pmf(k, p_uu)[:t].sum()) for k in range(t, n + 1))
    return low + high


def after_run_risk(model, T: float, s: int, q: int, t: int, run: int) -> float:
    """Exact ``Pr[K(tau) < t | the last `run` audits accepted]``, stationary before the run, u uniform on [0, T).

    This is the quantity the simulation check estimates in place of the fixed point.
    """
    dist = posterior_after(model, T, s, q, [True] * run)
    return _average_over_interval(lambda u: catastrophic_mass(model, model.propagate(dist, u), t), T)


def largest_interval(metric, target: float, lo: float, hi: float, iterations: int = 50) -> dict:
    """Largest ``T`` in ``[lo, hi]`` with ``metric(T) <= target`` by bisection on log T.

    Assumes ``metric`` is non-decreasing on the bracket; the caller checks that on a grid.
    """
    if metric(lo) > target:
        return {"T": None, "status": "infeasible_at_lo"}
    if metric(hi) <= target:
        return {"T": hi, "status": "feasible_at_hi"}
    a, b = math.log(lo), math.log(hi)
    for _ in range(iterations):
        mid = 0.5 * (a + b)
        if metric(math.exp(mid)) <= target:
            a = mid
        else:
            b = mid
    return {"T": math.exp(a), "status": "bisected"}


# ---------------------------------------------------------------- repair on alarm (R2c, design R2C-DESIGN.md)
def reset_members(model, dist: np.ndarray) -> np.ndarray:
    """Resharing: every custodian becomes individually up; domain states are unchanged."""
    if isinstance(model, IndependentModel):
        out = np.zeros_like(dist)
        out[-1] = dist.sum()
        return out
    m1 = model.m + 1
    for axis in range(model.domains):
        moved = np.moveaxis(dist, axis, 0)
        shape = moved.shape
        blocks = moved.reshape(2, m1, -1)
        reset = np.zeros_like(blocks)
        reset[:, -1, :] = blocks.sum(axis=1)
        dist = np.moveaxis(reset.reshape(shape), 0, axis)
    return dist


def repair_step(model, dist: np.ndarray, T: float, accept: np.ndarray, repair_delay: float) -> np.ndarray:
    """One audit interval: accept and evolve over T, or reject, evolve over D_r, reset, evolve over T - D_r."""
    accepted = model.propagate(dist * accept, T)
    rejected = model.propagate(dist * (1.0 - accept), repair_delay)
    rejected = model.propagate(reset_members(model, rejected), T - repair_delay)
    return accepted + rejected


def repair_stationary(model, T: float, s: int, q: int, repair_delay: float, tol: float = 1e-13,
                      max_steps: int = 200_000, start: np.ndarray | None = None) -> tuple[np.ndarray, int]:
    """Stationary law of the state just before an audit under the repair rule (power iteration).

    The limit does not depend on the start (the kernel is positive for T > 0); ``start`` only speeds it up.
    """
    if not 0 <= repair_delay <= T:
        raise ValueError("require 0 <= D_r <= T")
    accept = emission(model, s, q)
    dist = model.stationary() if start is None else start
    for step in range(1, max_steps + 1):
        nxt = repair_step(model, dist, T, accept, repair_delay)
        nxt = nxt / nxt.sum()
        if np.abs(nxt - dist).sum() < tol:
            return nxt, step
        dist = nxt
    raise RuntimeError(f"repair chain did not converge in {max_steps} steps")


def repair_metrics(model, T: float, s: int, q: int, t: int, repair_delay: float,
                   start: np.ndarray | None = None) -> dict:
    """F_rep, U_rep, repairs per day and benign fraction under the repair rule."""
    mu, steps = repair_stationary(model, T, s, q, repair_delay, start=start)
    accept = emission(model, s, q)
    acc, rej = mu * accept, mu * (1.0 - accept)
    after = reset_members(model, model.propagate(rej, repair_delay))

    def integral(start: np.ndarray, length: float) -> float:
        if length <= 0:
            return 0.0
        return length * _average_over_interval(lambda u: catastrophic_mass(model, model.propagate(start, u), t),
                                               length)

    undetected = integral(acc, T) / T
    failure = (integral(acc, T) + integral(rej, repair_delay) + integral(after, T - repair_delay)) / T
    p_reject = float(rej.sum())
    benign = float(rej[model.ready >= t].sum()) / p_reject if p_reject > 0 else 0.0
    return {"failure": failure, "undetected": undetected, "p_reject": p_reject,
            "repairs_per_day": 24.0 / T * p_reject, "audits_per_day": 24.0 / T, "benign_fraction": benign,
            "steps": steps, "stationary": mu}
