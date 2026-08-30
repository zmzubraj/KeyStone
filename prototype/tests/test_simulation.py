from math import isclose

from keystone.simulation import (
    Scenario,
    run_monte_carlo,
    simulate_markov_audit_series,
    three_state_readiness_model,
    transition_event,
    two_state_readiness_model,
    wilson_score_interval,
)


def test_wilson_interval_matches_known_binomial_counts() -> None:
    low, high = wilson_score_interval(successes=5, trials=10)
    assert isclose(low, 0.236593090512564, rel_tol=1e-12)
    assert isclose(high, 0.7634069094874361, rel_tol=1e-12)

    zero_low, zero_high = wilson_score_interval(successes=0, trials=10)
    assert zero_low == 0.0
    assert isclose(zero_high, 0.2775327998628892, rel_tol=1e-12)

    full_low, full_high = wilson_score_interval(successes=10, trials=10)
    assert isclose(full_low, 0.7224672001371107, rel_tol=1e-12)
    assert full_high == 1.0


def test_monte_carlo_reports_wilson_intervals_and_raw_counts() -> None:
    result = run_monte_carlo(Scenario(
        name="interval-baseline",
        n=8,
        threshold=5,
        sample_size=4,
        required_audit_responses=4,
        independent_offline_probability=0.25,
        domain_outage_probability=0.0,
        domains=2,
        trials=1_000,
        seed=987,
    ))

    for metric in ("reconstruction_success", "audit_pass", "catastrophic"):
        assert 0 <= result[f"{metric}_count"] <= result["trials"]
        assert 0.0 <= result[f"{metric}_ci_low"] <= result[f"{metric}_ci_high"] <= 1.0

    assert result["catastrophic_trials"] == result["catastrophic_count"]
    assert result["catastrophic_false_pass_count"] <= result["catastrophic_trials"]
    assert (
        result["catastrophic_detection_ci_low"]
        <= result["catastrophic_detection_rate"]
        <= result["catastrophic_detection_ci_high"]
    )


def test_monte_carlo_is_reproducible_and_reports_required_metrics() -> None:
    scenario = Scenario(
        name="iid-baseline",
        n=32,
        threshold=22,
        sample_size=8,
        required_audit_responses=8,
        independent_offline_probability=0.10,
        domain_outage_probability=0.0,
        domains=4,
        trials=500,
        seed=123,
    )

    a = run_monte_carlo(scenario)
    b = run_monte_carlo(scenario)

    assert a == b
    assert 0.0 <= a["reconstruction_success_rate"] <= 1.0
    assert 0.0 <= a["audit_pass_rate"] <= 1.0
    assert 0.0 <= a["catastrophic_false_pass_rate"] <= 1.0
    assert a["trials"] == 500


def test_domain_outages_reduce_reconstruction_when_shares_are_concentrated() -> None:
    diversified = Scenario(
        name="diversified",
        n=24,
        threshold=16,
        sample_size=8,
        required_audit_responses=8,
        independent_offline_probability=0.0,
        domain_outage_probability=0.25,
        domains=6,
        trials=3000,
        seed=77,
    )
    concentrated = Scenario(
        name="concentrated",
        n=24,
        threshold=16,
        sample_size=8,
        required_audit_responses=8,
        independent_offline_probability=0.0,
        domain_outage_probability=0.25,
        domains=2,
        trials=3000,
        seed=77,
    )

    diverse_result = run_monte_carlo(diversified)
    concentrated_result = run_monte_carlo(concentrated)

    assert diverse_result["reconstruction_success_rate"] > concentrated_result["reconstruction_success_rate"]


def test_three_state_markov_transitions_and_recovery_event_are_deterministic() -> None:
    model = three_state_readiness_model(
        online_to_degraded=1.0,
        degraded_to_online=0.0,
        degraded_to_offline=1.0,
        offline_to_degraded=1.0,
    )

    degraded = model.next_state("online", draw=0.25)
    offline = model.next_state(degraded, draw=0.25)
    recovering = model.next_state(offline, draw=0.25)

    assert (degraded, offline, recovering) == ("degraded", "offline", "degraded")
    assert transition_event("offline", recovering) == "recovered"


def test_markov_audit_series_is_reproducible_and_not_a_static_set_bound() -> None:
    model = two_state_readiness_model(
        online_to_offline=0.22,
        offline_to_online=0.08,
    )
    first = simulate_markov_audit_series(
        n=12,
        threshold=8,
        sample_size=4,
        required_valid=3,
        audits=4,
        trials=8_000,
        seed=20260830,
        model=model,
    )
    second = simulate_markov_audit_series(
        n=12,
        threshold=8,
        sample_size=4,
        required_valid=3,
        audits=4,
        trials=8_000,
        seed=20260830,
        model=model,
    )

    assert first == second
    assert first["final_catastrophic_trials"] > 0
    assert first["all_audits_pass_and_final_catastrophic_count"] > 0
    assert 0.0 <= first["conditional_sequence_false_accept_rate"] <= 1.0
    assert first["conditional_sequence_false_accept_rate"] != first["static_set_repeated_bound"]
