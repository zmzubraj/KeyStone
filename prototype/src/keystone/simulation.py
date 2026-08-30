from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import NormalDist
import random
from typing import Literal

from .sampling import catastrophic_false_accept_probability

SamplingStrategy = Literal["uniform", "stratified"]


@dataclass(frozen=True, slots=True)
class MarkovReadinessModel:
    states: tuple[str, ...]
    transition_matrix: tuple[tuple[float, ...], ...]

    def validate(self) -> None:
        if not self.states or len(set(self.states)) != len(self.states):
            raise ValueError("Markov states must be non-empty and unique")
        if "online" not in self.states or "offline" not in self.states:
            raise ValueError("Markov readiness model requires online and offline states")
        if len(self.transition_matrix) != len(self.states):
            raise ValueError("transition matrix row count must match states")
        for row in self.transition_matrix:
            if len(row) != len(self.states):
                raise ValueError("transition matrix must be square")
            if any(probability < 0.0 or probability > 1.0 for probability in row):
                raise ValueError("transition probabilities must be between zero and one")
            if abs(sum(row) - 1.0) > 1e-12:
                raise ValueError("each transition row must sum to one")

    def next_state(self, current: str, draw: float) -> str:
        self.validate()
        if current not in self.states:
            raise ValueError("unknown Markov readiness state")
        if not 0.0 <= draw < 1.0:
            raise ValueError("draw must satisfy 0 <= draw < 1")
        row = self.transition_matrix[self.states.index(current)]
        cumulative = 0.0
        for state, probability in zip(self.states, row, strict=True):
            cumulative += probability
            if draw < cumulative:
                return state
        return self.states[-1]


def two_state_readiness_model(
    online_to_offline: float,
    offline_to_online: float,
) -> MarkovReadinessModel:
    model = MarkovReadinessModel(
        states=("online", "offline"),
        transition_matrix=(
            (1.0 - online_to_offline, online_to_offline),
            (offline_to_online, 1.0 - offline_to_online),
        ),
    )
    model.validate()
    return model


def three_state_readiness_model(
    online_to_degraded: float,
    degraded_to_online: float,
    degraded_to_offline: float,
    offline_to_degraded: float,
) -> MarkovReadinessModel:
    degraded_stay = 1.0 - degraded_to_online - degraded_to_offline
    model = MarkovReadinessModel(
        states=("online", "degraded", "offline"),
        transition_matrix=(
            (1.0 - online_to_degraded, online_to_degraded, 0.0),
            (degraded_to_online, degraded_stay, degraded_to_offline),
            (0.0, offline_to_degraded, 1.0 - offline_to_degraded),
        ),
    )
    model.validate()
    return model


def transition_event(previous: str, current: str) -> str:
    if previous == "offline" and current != "offline":
        return "recovered"
    if previous != "offline" and current == "offline":
        return "failed"
    return current


def wilson_score_interval(
    successes: int,
    trials: int,
    confidence_level: float = 0.95,
) -> tuple[float, float]:
    """Two-sided Wilson score interval for a binomial proportion."""

    if trials <= 0:
        raise ValueError("trials must be positive")
    if not 0 <= successes <= trials:
        raise ValueError("successes must satisfy 0 <= successes <= trials")
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level must be between zero and one")

    z = NormalDist().inv_cdf(0.5 + confidence_level / 2.0)
    proportion = successes / trials
    z_squared = z * z
    denominator = 1.0 + z_squared / trials
    center = (proportion + z_squared / (2.0 * trials)) / denominator
    margin = (
        z
        * (
            proportion * (1.0 - proportion) / trials
            + z_squared / (4.0 * trials * trials)
        )
        ** 0.5
        / denominator
    )
    low = max(0.0, center - margin)
    high = min(1.0, center + margin)
    if successes == 0:
        low = 0.0
    if successes == trials:
        high = 1.0
    return low, high


def simulate_markov_audit_series(
    *,
    n: int,
    threshold: int,
    sample_size: int,
    required_valid: int,
    audits: int,
    trials: int,
    seed: int,
    model: MarkovReadinessModel,
) -> dict[str, object]:
    """Simulate repeated audits while custodian readiness evolves over time.

    A custodian in ``online`` or ``degraded`` is counted as ready; ``offline``
    is not. The reported sequence metric is intentionally distinct from the
    static-ready-set repeated bound.
    """

    if not 1 <= threshold <= n:
        raise ValueError("threshold must satisfy 1 <= threshold <= n")
    if not 0 <= sample_size <= n:
        raise ValueError("sample_size must satisfy 0 <= sample_size <= n")
    if not 0 <= required_valid <= sample_size:
        raise ValueError("required_valid must fit inside the sample")
    if audits <= 0 or trials <= 0:
        raise ValueError("audits and trials must be positive")
    model.validate()

    rng = random.Random(seed)
    final_catastrophic_trials = 0
    misleading_sequences = 0
    for _ in range(trials):
        states = ["online"] * n
        all_audits_pass = True
        for _ in range(audits):
            states = [model.next_state(state, rng.random()) for state in states]
            sampled = rng.sample(range(n), sample_size)
            valid = sum(states[index] != "offline" for index in sampled)
            all_audits_pass = all_audits_pass and valid >= required_valid

        final_ready = sum(state != "offline" for state in states)
        final_catastrophic = final_ready < threshold
        final_catastrophic_trials += int(final_catastrophic)
        misleading_sequences += int(final_catastrophic and all_audits_pass)

    conditional_rate = (
        misleading_sequences / final_catastrophic_trials
        if final_catastrophic_trials
        else 0.0
    )
    if final_catastrophic_trials:
        conditional_ci: tuple[float, float] | None = wilson_score_interval(
            misleading_sequences,
            final_catastrophic_trials,
        )
    else:
        conditional_ci = None
    static_single = catastrophic_false_accept_probability(
        n,
        threshold,
        sample_size,
        required_valid,
    )
    return {
        "n": n,
        "threshold": threshold,
        "sample_size": sample_size,
        "required_valid": required_valid,
        "audits": audits,
        "trials": trials,
        "seed": seed,
        "model_states": model.states,
        "transition_matrix": model.transition_matrix,
        "final_catastrophic_trials": final_catastrophic_trials,
        "all_audits_pass_and_final_catastrophic_count": misleading_sequences,
        "conditional_sequence_false_accept_rate": conditional_rate,
        "conditional_sequence_false_accept_ci_low": conditional_ci[0]
        if conditional_ci
        else None,
        "conditional_sequence_false_accept_ci_high": conditional_ci[1]
        if conditional_ci
        else None,
        "static_set_single_audit_bound": static_single,
        "static_set_repeated_bound": static_single**audits,
    }


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    n: int
    threshold: int
    sample_size: int
    required_audit_responses: int
    independent_offline_probability: float
    domain_outage_probability: float
    domains: int
    trials: int
    seed: int
    sampling_strategy: SamplingStrategy = "uniform"
    selective_withholders: int = 0

    def validate(self) -> None:
        if not 1 <= self.threshold <= self.n:
            raise ValueError("threshold must satisfy 1 <= threshold <= n")
        if not 0 <= self.sample_size <= self.n:
            raise ValueError("sample_size must satisfy 0 <= sample_size <= n")
        if not 0 <= self.required_audit_responses <= self.sample_size:
            raise ValueError("required audit responses must fit inside the sample")
        if not 1 <= self.domains <= self.n:
            raise ValueError("domains must satisfy 1 <= domains <= n")
        if self.sampling_strategy == "stratified" and self.sample_size < self.domains:
            raise ValueError("stratified sampling requires at least one draw per domain")
        for probability in (
            self.independent_offline_probability,
            self.domain_outage_probability,
        ):
            if not 0.0 <= probability <= 1.0:
                raise ValueError("failure probabilities must be between zero and one")
        if self.trials <= 0:
            raise ValueError("trials must be positive")
        if not 0 <= self.selective_withholders <= self.n:
            raise ValueError("selective_withholders must fit inside the committee")


def _domain_assignments(n: int, domains: int) -> list[int]:
    return [index % domains for index in range(n)]


def _stratified_draw(
    assignments: list[int],
    sample_size: int,
    domains: int,
    rng: random.Random,
) -> list[int]:
    selected: list[int] = []
    for domain in range(domains):
        candidates = [index for index, assigned in enumerate(assignments) if assigned == domain]
        selected.append(rng.choice(candidates))
    remaining = [index for index in range(len(assignments)) if index not in selected]
    selected.extend(rng.sample(remaining, sample_size - len(selected)))
    return selected


def run_monte_carlo(scenario: Scenario) -> dict[str, float | int | str]:
    scenario.validate()
    rng = random.Random(scenario.seed)
    assignments = _domain_assignments(scenario.n, scenario.domains)

    reconstruction_successes = 0
    audit_passes = 0
    catastrophic_trials = 0
    catastrophic_false_passes = 0
    ready_total = 0

    selective_set = set(range(scenario.n - scenario.selective_withholders, scenario.n))

    for _ in range(scenario.trials):
        down_domains = {
            domain
            for domain in range(scenario.domains)
            if rng.random() < scenario.domain_outage_probability
        }
        audit_ready: list[bool] = []
        dispute_ready: list[bool] = []
        for member, domain in enumerate(assignments):
            infrastructure_ready = (
                domain not in down_domains
                and rng.random() >= scenario.independent_offline_probability
            )
            audit_ready.append(infrastructure_ready)
            dispute_ready.append(infrastructure_ready and member not in selective_set)

        ready_count = sum(dispute_ready)
        ready_total += ready_count
        reconstructable = ready_count >= scenario.threshold
        reconstruction_successes += int(reconstructable)

        if scenario.sampling_strategy == "stratified":
            sample = _stratified_draw(assignments, scenario.sample_size, scenario.domains, rng)
        else:
            sample = rng.sample(range(scenario.n), scenario.sample_size)
        audit_responses = sum(audit_ready[index] for index in sample)
        audit_pass = audit_responses >= scenario.required_audit_responses
        audit_passes += int(audit_pass)

        catastrophic = not reconstructable
        catastrophic_trials += int(catastrophic)
        catastrophic_false_passes += int(catastrophic and audit_pass)

    conditional_false_pass = (
        catastrophic_false_passes / catastrophic_trials if catastrophic_trials else 0.0
    )
    reconstruction_ci = wilson_score_interval(reconstruction_successes, scenario.trials)
    audit_pass_ci = wilson_score_interval(audit_passes, scenario.trials)
    catastrophic_ci = wilson_score_interval(catastrophic_trials, scenario.trials)
    if catastrophic_trials:
        false_pass_ci: tuple[float, float] | None = wilson_score_interval(
            catastrophic_false_passes,
            catastrophic_trials,
        )
        detection_ci: tuple[float, float] | None = (
            1.0 - false_pass_ci[1],
            1.0 - false_pass_ci[0],
        )
    else:
        false_pass_ci = None
        detection_ci = None
    return {
        "name": scenario.name,
        "trials": scenario.trials,
        "reconstruction_success_count": reconstruction_successes,
        "reconstruction_success_rate": reconstruction_successes / scenario.trials,
        "reconstruction_success_ci_low": reconstruction_ci[0],
        "reconstruction_success_ci_high": reconstruction_ci[1],
        "audit_pass_count": audit_passes,
        "audit_pass_rate": audit_passes / scenario.trials,
        "audit_pass_ci_low": audit_pass_ci[0],
        "audit_pass_ci_high": audit_pass_ci[1],
        "catastrophic_count": catastrophic_trials,
        "catastrophic_rate": catastrophic_trials / scenario.trials,
        "catastrophic_ci_low": catastrophic_ci[0],
        "catastrophic_ci_high": catastrophic_ci[1],
        "catastrophic_trials": catastrophic_trials,
        "catastrophic_false_pass_count": catastrophic_false_passes,
        "catastrophic_false_pass_rate": conditional_false_pass,
        "catastrophic_false_pass_ci_low": false_pass_ci[0] if false_pass_ci else None,
        "catastrophic_false_pass_ci_high": false_pass_ci[1] if false_pass_ci else None,
        "catastrophic_detection_rate": 1.0 - conditional_false_pass if catastrophic_trials else 1.0,
        "catastrophic_detection_ci_low": detection_ci[0] if detection_ci else None,
        "catastrophic_detection_ci_high": detection_ci[1] if detection_ci else None,
        "average_dispute_ready": ready_total / scenario.trials,
        "sampling_strategy": scenario.sampling_strategy,
        "scenario": asdict(scenario),
    }
