from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
import hashlib
from math import comb, fsum
import random


def _validate_sampling(n: int, sample_size: int) -> None:
    if n <= 0:
        raise ValueError("population must be positive")
    if not 0 <= sample_size <= n:
        raise ValueError("sample size must satisfy 0 <= sample_size <= n")


def _seed(beacon: bytes, label: bytes = b"") -> int:
    return int.from_bytes(hashlib.sha256(b"KEYSTONE-SAMPLE-v1" + label + beacon).digest(), "big")


def sample_uniform(population: Sequence[str], sample_size: int, beacon: bytes) -> list[str]:
    ordered = sorted(population)
    _validate_sampling(len(ordered), sample_size)
    rng = random.Random(_seed(beacon))
    return rng.sample(ordered, sample_size)


def sample_stratified(
    member_domains: Mapping[str, str],
    sample_size: int,
    beacon: bytes,
    minimum_per_domain: int = 1,
) -> list[str]:
    if minimum_per_domain < 0:
        raise ValueError("minimum_per_domain cannot be negative")
    grouped: dict[str, list[str]] = defaultdict(list)
    for member, domain in member_domains.items():
        grouped[domain].append(member)
    if not grouped:
        if sample_size == 0:
            return []
        raise ValueError("cannot sample an empty committee")
    _validate_sampling(len(member_domains), sample_size)
    if minimum_per_domain * len(grouped) > sample_size:
        raise ValueError("sample is too small for minimum domain coverage")
    if any(len(members) < minimum_per_domain for members in grouped.values()):
        raise ValueError("a domain has fewer members than minimum_per_domain")

    selected: list[str] = []
    for domain in sorted(grouped):
        rng = random.Random(_seed(beacon, b"domain:" + domain.encode("utf-8")))
        selected.extend(rng.sample(sorted(grouped[domain]), minimum_per_domain))

    remaining = sorted(set(member_domains) - set(selected))
    needed = sample_size - len(selected)
    if needed:
        rng = random.Random(_seed(beacon, b"remainder"))
        selected.extend(rng.sample(remaining, needed))
    return selected


def hypergeometric_tail_probability(
    population: int,
    successes: int,
    draws: int,
    required_successes: int,
) -> float:
    _validate_sampling(population, draws)
    if not 0 <= successes <= population:
        raise ValueError("successes must satisfy 0 <= successes <= population")
    if not 0 <= required_successes <= draws:
        raise ValueError("required_successes must satisfy 0 <= q <= draws")
    denominator = comb(population, draws)
    total = 0
    upper = min(draws, successes)
    for observed in range(required_successes, upper + 1):
        failures_drawn = draws - observed
        if failures_drawn > population - successes:
            continue
        total += comb(successes, observed) * comb(population - successes, failures_drawn)
    return total / denominator


def stratified_success_distribution(
    strata: Sequence[tuple[int, int, int]],
) -> dict[int, float]:
    """Return the exact success-count PMF for fixed draws in independent strata.

    Each tuple is ``(population, successes, draws)``. Sampling is without
    replacement inside each stratum; strata are disjoint, so their
    hypergeometric PMFs can be convolved.
    """

    distribution = {0: 1.0}
    for population, successes, draws in strata:
        _validate_sampling(population, draws)
        if not 0 <= successes <= population:
            raise ValueError("successes must satisfy 0 <= successes <= population")

        denominator = comb(population, draws)
        lower = max(0, draws - (population - successes))
        upper = min(draws, successes)
        stratum_pmf = {
            observed: comb(successes, observed)
            * comb(population - successes, draws - observed)
            / denominator
            for observed in range(lower, upper + 1)
        }

        convolved: dict[int, float] = defaultdict(float)
        for prior_successes, prior_probability in distribution.items():
            for observed, probability in stratum_pmf.items():
                convolved[prior_successes + observed] += prior_probability * probability
        distribution = dict(sorted(convolved.items()))

    total = fsum(distribution.values())
    if total == 0.0:
        raise ValueError("stratified distribution has zero probability mass")
    return {observed: probability / total for observed, probability in distribution.items()}


def stratified_tail_probability(
    strata: Sequence[tuple[int, int, int]],
    required_successes: int,
) -> float:
    """Return P[X >= required_successes] for fixed per-stratum draws."""

    if required_successes < 0:
        raise ValueError("required_successes cannot be negative")
    total_draws = sum(draws for _, _, draws in strata)
    if required_successes > total_draws:
        raise ValueError("required_successes cannot exceed total draws")
    distribution = stratified_success_distribution(strata)
    return fsum(
        probability
        for observed, probability in distribution.items()
        if observed >= required_successes
    )


def catastrophic_false_accept_probability(
    n: int,
    threshold: int,
    sample_size: int,
    required_valid: int | None = None,
) -> float:
    """Worst-case false pass when fewer than threshold custodians are ready."""

    if not 1 <= threshold <= n:
        raise ValueError("threshold must satisfy 1 <= threshold <= n")
    required = sample_size if required_valid is None else required_valid
    return hypergeometric_tail_probability(n, threshold - 1, sample_size, required)


def repeated_false_accept_probability(single_audit_probability: float, audits: int) -> float:
    if not 0.0 <= single_audit_probability <= 1.0:
        raise ValueError("probability must be between zero and one")
    if audits < 0:
        raise ValueError("audits cannot be negative")
    return single_audit_probability**audits
