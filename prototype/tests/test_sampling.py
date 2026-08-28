from math import comb, isclose

from keystone.sampling import (
    catastrophic_false_accept_probability,
    repeated_false_accept_probability,
    sample_stratified,
    sample_uniform,
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
