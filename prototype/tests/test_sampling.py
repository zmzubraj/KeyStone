from math import comb, isclose
import random

from keystone.sampling import (
    catastrophic_false_accept_probability,
    repeated_false_accept_probability,
    sample_stratified,
    sample_uniform,
    stratified_success_distribution,
    stratified_tail_probability,
)


def test_closed_form_catastrophic_false_accept_bound() -> None:
    probability = catastrophic_false_accept_probability(n=32, threshold=22, sample_size=8)
    expected = comb(21, 8) / comb(32, 8)

    assert isclose(probability, expected, rel_tol=1e-15)
    assert isclose(1.0 - probability, 0.9806537178061093, rel_tol=1e-12)


def test_repeated_audits_multiply_bound_for_static_failure_set() -> None:
    one = catastrophic_false_accept_probability(32, 22, 8)
    assert repeated_false_accept_probability(one, audits=4) == one**4


def test_uniform_sampling_is_beacon_deterministic() -> None:
    population = [f"c{i}" for i in range(16)]
    a = sample_uniform(population, 6, b"beacon-100")
    b = sample_uniform(population, 6, b"beacon-100")
    c = sample_uniform(population, 6, b"beacon-101")

    assert a == b
    assert a != c
    assert len(set(a)) == 6


def test_stratified_sample_covers_each_failure_domain() -> None:
    domains = {
        "a1": "aws-eu",
        "a2": "aws-eu",
        "g1": "gcp-us",
        "g2": "gcp-us",
        "z1": "azure-ap",
        "z2": "azure-ap",
    }
    sampled = sample_stratified(domains, sample_size=6, beacon=b"epoch-5", minimum_per_domain=1)

    assert len(sampled) == 6
    assert {domains[item] for item in sampled} == {"aws-eu", "gcp-us", "azure-ap"}


def test_exact_stratified_distribution_matches_hand_enumerated_two_domain_case() -> None:
    strata = [(2, 1, 1), (3, 2, 1)]

    distribution = stratified_success_distribution(strata)

    assert set(distribution) == {0, 1, 2}
    assert isclose(distribution[0], 1 / 6, rel_tol=1e-15)
    assert isclose(distribution[1], 1 / 2, rel_tol=1e-15)
    assert isclose(distribution[2], 1 / 3, rel_tol=1e-15)
    assert isclose(sum(distribution.values()), 1.0, rel_tol=1e-15)
    assert isclose(stratified_tail_probability(strata, required_successes=2), 1 / 3, rel_tol=1e-15)


def test_exact_stratified_tail_matches_seeded_monte_carlo() -> None:
    strata = [(8, 5, 2), (6, 2, 2), (4, 3, 1)]
    exact = stratified_tail_probability(strata, required_successes=3)
    rng = random.Random(20260829)
    trials = 80_000
    passes = 0
    for _ in range(trials):
        observed = 0
        for population, successes, draws in strata:
            stratum = [1] * successes + [0] * (population - successes)
            observed += sum(rng.sample(stratum, draws))
        passes += observed >= 3

    empirical = passes / trials
    assert abs(empirical - exact) < 0.01
