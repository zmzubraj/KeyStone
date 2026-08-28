from keystone.simulation import Scenario, run_monte_carlo


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
