from __future__ import annotations

from dataclasses import asdict, dataclass
import random
from typing import Literal

SamplingStrategy = Literal["uniform", "stratified"]


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
    return {
        "name": scenario.name,
        "trials": scenario.trials,
        "reconstruction_success_rate": reconstruction_successes / scenario.trials,
        "audit_pass_rate": audit_passes / scenario.trials,
        "catastrophic_rate": catastrophic_trials / scenario.trials,
        "catastrophic_false_pass_rate": conditional_false_pass,
        "catastrophic_detection_rate": 1.0 - conditional_false_pass if catastrophic_trials else 1.0,
        "average_dispute_ready": ready_total / scenario.trials,
        "sampling_strategy": scenario.sampling_strategy,
        "scenario": asdict(scenario),
    }
