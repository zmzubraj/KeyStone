#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
from typing import Any

import matplotlib.pyplot as plt

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parent
sys.path.insert(0, str(PROJECT / "src"))

from keystone.sampling import (  # noqa: E402
    catastrophic_false_accept_probability,
    stratified_tail_probability,
)
from keystone.simulation import (  # noqa: E402
    Scenario,
    run_monte_carlo,
    simulate_markov_audit_series,
    two_state_readiness_model,
)

RESULTS = PROJECT / "results"
FIGURES = RESULTS / "figures"
MANIFEST = RESULTS / "experiment_manifest.json"

DATASET_COLUMNS = {
    "theoretical_bound.csv": {
        "n", "threshold", "sample_size", "detection_probability",
    },
    "iid_failure_sweep.csv": {
        "offline_probability", "reconstruction_success_rate",
        "reconstruction_success_ci_low", "reconstruction_success_ci_high",
        "audit_pass_rate", "audit_pass_ci_low", "audit_pass_ci_high",
        "catastrophic_detection_rate", "catastrophic_trials",
    },
    "domain_diversity.csv": {
        "domains", "reconstruction_success_rate", "reconstruction_success_ci_low",
        "reconstruction_success_ci_high", "catastrophic_rate",
        "catastrophic_ci_low", "catastrophic_ci_high",
    },
    "selective_withholding.csv": {
        "selective_withholders", "reconstruction_success_rate",
        "reconstruction_success_ci_low", "reconstruction_success_ci_high",
        "audit_pass_rate", "audit_pass_ci_low", "audit_pass_ci_high",
    },
    "sampling_strategy.csv": {
        "sample_size", "strategy", "catastrophic_detection_rate",
        "catastrophic_detection_ci_low", "catastrophic_detection_ci_high",
        "catastrophic_trials", "audit_pass_rate", "audit_pass_ci_low",
        "audit_pass_ci_high",
    },
    "exact_stratified_validation.csv": {
        "design", "strata", "required_successes", "exact_tail_probability",
        "monte_carlo_tail_probability", "absolute_error", "trials", "seed",
    },
    "markov_temporal_dependence.csv": {
        "audits", "trials", "seed", "online_to_offline", "offline_to_online",
        "final_catastrophic_trials", "all_audits_pass_and_final_catastrophic_count",
        "conditional_sequence_false_accept_rate",
        "conditional_sequence_false_accept_ci_low",
        "conditional_sequence_false_accept_ci_high", "static_set_repeated_bound",
    },
}

EXPECTED_DATASET_ROWS = {
    "theoretical_bound.csv": 48,
    "iid_failure_sweep.csv": 17,
    "domain_diversity.csv": 4,
    "selective_withholding.csv": 15,
    "sampling_strategy.csv": 12,
    "exact_stratified_validation.csv": 1,
    "markov_temporal_dependence.csv": 4,
}

EXPECTED_FIGURES = tuple(
    f"figure_{index}_{stem}.{extension}"
    for index, stem in (
        (1, "theoretical_detection_bound"),
        (2, "iid_failure_sweep"),
        (3, "domain_diversity"),
        (4, "selective_withholding_gap"),
        (5, "sampling_strategy"),
    )
    for extension in ("png", "svg")
)

HASH_BOUND_INPUTS = (
    "prototype/scripts/run_experiments.py",
    "prototype/src/keystone/sampling.py",
    "prototype/src/keystone/simulation.py",
    "prototype/pyproject.toml",
    "prototype/uv.lock",
)


class ManifestError(RuntimeError):
    """Raised when the preliminary experiment manifest cannot be trusted."""


def _write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _save_figure(stem: str) -> None:
    png = FIGURES / f"{stem}.png"
    svg = FIGURES / f"{stem}.svg"
    plt.savefig(png, dpi=180)
    plt.savefig(svg)
    normalized = "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())
    svg.write_text(normalized + "\n", encoding="utf-8")


def theoretical_bound_figure() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    plt.figure(figsize=(8, 5))
    for threshold in (17, 22, 25):
        xs = list(range(1, 17))
        ys = [1.0 - catastrophic_false_accept_probability(32, threshold, s) for s in xs]
        for sample_size, detection in zip(xs, ys, strict=True):
            rows.append({
                "n": 32,
                "threshold": threshold,
                "sample_size": sample_size,
                "detection_probability": detection,
            })
        plt.plot(xs, ys, marker="o", label=f"t={threshold}")
    plt.xlabel("Audit sample size s")
    plt.ylabel("Worst-case catastrophic-state detection probability")
    plt.title("KEYSTONE analytical detection bound (n=32, q=s)")
    plt.ylim(0.0, 1.02)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    _save_figure("figure_1_theoretical_detection_bound")
    plt.close()
    return rows


def iid_failure_figure() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    probabilities = [round(x * 0.025, 3) for x in range(0, 17)]
    for offline_probability in probabilities:
        result = run_monte_carlo(Scenario(
            name=f"iid-{offline_probability}",
            n=32,
            threshold=22,
            sample_size=8,
            required_audit_responses=8,
            independent_offline_probability=offline_probability,
            domain_outage_probability=0.0,
            domains=4,
            trials=12000,
            seed=202600 + int(offline_probability * 1000),
        ))
        rows.append({
            "offline_probability": offline_probability,
            "reconstruction_success_rate": result["reconstruction_success_rate"],
            "reconstruction_success_ci_low": result["reconstruction_success_ci_low"],
            "reconstruction_success_ci_high": result["reconstruction_success_ci_high"],
            "audit_pass_rate": result["audit_pass_rate"],
            "audit_pass_ci_low": result["audit_pass_ci_low"],
            "audit_pass_ci_high": result["audit_pass_ci_high"],
            "catastrophic_detection_rate": result["catastrophic_detection_rate"],
            "catastrophic_trials": result["catastrophic_trials"],
        })
    plt.figure(figsize=(8, 5))
    plt.plot(
        [row["offline_probability"] for row in rows],
        [row["reconstruction_success_rate"] for row in rows],
        marker="o",
        label="Dispute reconstruction success",
    )
    plt.fill_between(
        [row["offline_probability"] for row in rows],
        [row["reconstruction_success_ci_low"] for row in rows],
        [row["reconstruction_success_ci_high"] for row in rows],
        alpha=0.15,
    )
    plt.plot(
        [row["offline_probability"] for row in rows],
        [row["audit_pass_rate"] for row in rows],
        marker="s",
        label="All-response audit pass",
    )
    plt.fill_between(
        [row["offline_probability"] for row in rows],
        [row["audit_pass_ci_low"] for row in rows],
        [row["audit_pass_ci_high"] for row in rows],
        alpha=0.15,
    )
    plt.xlabel("Independent custodian offline probability")
    plt.ylabel("Probability")
    plt.title("Reconstructability and audit pass rate under independent failures")
    plt.ylim(0.0, 1.02)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    _save_figure("figure_2_iid_failure_sweep")
    plt.close()
    return rows


def domain_diversity_figure() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for domains in (2, 4, 8, 16):
        result = run_monte_carlo(Scenario(
            name=f"domains-{domains}",
            n=32,
            threshold=22,
            sample_size=max(8, domains),
            required_audit_responses=max(8, domains),
            independent_offline_probability=0.01,
            domain_outage_probability=0.15,
            domains=domains,
            trials=20000,
            seed=3300 + domains,
        ))
        rows.append({
            "domains": domains,
            "reconstruction_success_rate": result["reconstruction_success_rate"],
            "reconstruction_success_ci_low": result["reconstruction_success_ci_low"],
            "reconstruction_success_ci_high": result["reconstruction_success_ci_high"],
            "catastrophic_rate": result["catastrophic_rate"],
            "catastrophic_ci_low": result["catastrophic_ci_low"],
            "catastrophic_ci_high": result["catastrophic_ci_high"],
        })
    plt.figure(figsize=(8, 5))
    plt.plot(
        [row["domains"] for row in rows],
        [row["reconstruction_success_rate"] for row in rows],
        marker="o",
    )
    plt.fill_between(
        [row["domains"] for row in rows],
        [row["reconstruction_success_ci_low"] for row in rows],
        [row["reconstruction_success_ci_high"] for row in rows],
        alpha=0.15,
    )
    plt.xlabel("Independent failure domains")
    plt.ylabel("Dispute reconstruction success probability")
    plt.title("Committee diversity reduces correlated-outage risk")
    plt.ylim(0.0, 1.02)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    _save_figure("figure_3_domain_diversity")
    plt.close()
    return rows


def selective_withholding_figure() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for withholders in range(0, 15):
        result = run_monte_carlo(Scenario(
            name=f"withholders-{withholders}",
            n=32,
            threshold=22,
            sample_size=8,
            required_audit_responses=8,
            independent_offline_probability=0.0,
            domain_outage_probability=0.0,
            domains=4,
            trials=4000,
            seed=4400 + withholders,
            selective_withholders=withholders,
        ))
        rows.append({
            "selective_withholders": withholders,
            "reconstruction_success_rate": result["reconstruction_success_rate"],
            "reconstruction_success_ci_low": result["reconstruction_success_ci_low"],
            "reconstruction_success_ci_high": result["reconstruction_success_ci_high"],
            "audit_pass_rate": result["audit_pass_rate"],
            "audit_pass_ci_low": result["audit_pass_ci_low"],
            "audit_pass_ci_high": result["audit_pass_ci_high"],
        })
    plt.figure(figsize=(8, 5))
    plt.plot(
        [row["selective_withholders"] for row in rows],
        [row["reconstruction_success_rate"] for row in rows],
        marker="o",
        label="Target dispute reconstruction",
    )
    plt.fill_between(
        [row["selective_withholders"] for row in rows],
        [row["reconstruction_success_ci_low"] for row in rows],
        [row["reconstruction_success_ci_high"] for row in rows],
        alpha=0.15,
    )
    plt.plot(
        [row["selective_withholders"] for row in rows],
        [row["audit_pass_rate"] for row in rows],
        marker="s",
        label="Prior canary audit",
    )
    plt.fill_between(
        [row["selective_withholders"] for row in rows],
        [row["audit_pass_ci_low"] for row in rows],
        [row["audit_pass_ci_high"] for row in rows],
        alpha=0.15,
    )
    plt.axvline(11, linestyle="--", label="n-t+1 = 11")
    plt.xlabel("Custodians that answer audits but withhold target dispute")
    plt.ylabel("Probability")
    plt.title("Selective withholding is a stated limitation of ordinary readiness sampling")
    plt.ylim(-0.02, 1.02)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    _save_figure("figure_4_selective_withholding_gap")
    plt.close()
    return rows


def sampling_strategy_figure() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for sample_size in (4, 6, 8, 10, 12, 16):
        for strategy in ("uniform", "stratified"):
            result = run_monte_carlo(Scenario(
                name=f"{strategy}-{sample_size}",
                n=32,
                threshold=22,
                sample_size=sample_size,
                required_audit_responses=sample_size,
                independent_offline_probability=0.01,
                domain_outage_probability=0.20,
                domains=4,
                trials=16000,
                seed=5500 + sample_size,
                sampling_strategy=strategy,
            ))
            rows.append({
                "sample_size": sample_size,
                "strategy": strategy,
                "catastrophic_detection_rate": result["catastrophic_detection_rate"],
                "catastrophic_detection_ci_low": result["catastrophic_detection_ci_low"],
                "catastrophic_detection_ci_high": result["catastrophic_detection_ci_high"],
                "catastrophic_trials": result["catastrophic_trials"],
                "audit_pass_rate": result["audit_pass_rate"],
                "audit_pass_ci_low": result["audit_pass_ci_low"],
                "audit_pass_ci_high": result["audit_pass_ci_high"],
            })
    plt.figure(figsize=(8, 5))
    for strategy, marker in (("uniform", "o"), ("stratified", "s")):
        selected = [row for row in rows if row["strategy"] == strategy]
        plt.plot(
            [row["sample_size"] for row in selected],
            [row["catastrophic_detection_rate"] for row in selected],
            marker=marker,
            label=strategy,
        )
        interval_rows = [
            row
            for row in selected
            if row["catastrophic_detection_ci_low"] is not None
        ]
        plt.fill_between(
            [row["sample_size"] for row in interval_rows],
            [row["catastrophic_detection_ci_low"] for row in interval_rows],
            [row["catastrophic_detection_ci_high"] for row in interval_rows],
            alpha=0.15,
        )
    plt.xlabel("Audit sample size")
    plt.ylabel("Detection rate conditioned on catastrophic state")
    plt.title("Uniform versus failure-domain-stratified sampling")
    plt.ylim(0.0, 1.02)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    _save_figure("figure_5_sampling_strategy")
    plt.close()
    return rows


def exact_stratified_validation_table() -> list[dict[str, object]]:
    strata = [(8, 5, 2), (8, 5, 2), (8, 5, 2), (8, 5, 2)]
    required_successes = 6
    exact = stratified_tail_probability(strata, required_successes)
    trials = 100_000
    seed = 20260829
    rng = random.Random(seed)
    passes = 0
    for _ in range(trials):
        observed = 0
        for population, successes, draws in strata:
            values = [1] * successes + [0] * (population - successes)
            observed += sum(rng.sample(values, draws))
        passes += observed >= required_successes
    empirical = passes / trials
    return [{
        "design": "fixed-quota domain-stratified sampling",
        "strata": json.dumps(strata, separators=(",", ":")),
        "required_successes": required_successes,
        "exact_tail_probability": exact,
        "monte_carlo_tail_probability": empirical,
        "absolute_error": abs(empirical - exact),
        "trials": trials,
        "seed": seed,
    }]


def markov_temporal_dependence_table() -> list[dict[str, object]]:
    model = two_state_readiness_model(
        online_to_offline=0.22,
        offline_to_online=0.08,
    )
    rows: list[dict[str, object]] = []
    for audits in (1, 2, 4, 8):
        result = simulate_markov_audit_series(
            n=12,
            threshold=8,
            sample_size=4,
            required_valid=3,
            audits=audits,
            trials=12_000,
            seed=20260830 + audits,
            model=model,
        )
        rows.append({
            "audits": audits,
            "trials": result["trials"],
            "seed": result["seed"],
            "online_to_offline": 0.22,
            "offline_to_online": 0.08,
            "final_catastrophic_trials": result["final_catastrophic_trials"],
            "all_audits_pass_and_final_catastrophic_count": result[
                "all_audits_pass_and_final_catastrophic_count"
            ],
            "conditional_sequence_false_accept_rate": result[
                "conditional_sequence_false_accept_rate"
            ],
            "conditional_sequence_false_accept_ci_low": result[
                "conditional_sequence_false_accept_ci_low"
            ],
            "conditional_sequence_false_accept_ci_high": result[
                "conditional_sequence_false_accept_ci_high"
            ],
            "static_set_repeated_bound": result["static_set_repeated_bound"],
        })
    return rows


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _workspace_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(WORKSPACE.resolve()).as_posix()
    except ValueError as exc:
        raise ManifestError(f"path escapes workspace: {path}") from exc


def _resolve_workspace_path(relative: str) -> Path:
    candidate = (WORKSPACE / relative).resolve()
    try:
        candidate.relative_to(WORKSPACE.resolve())
    except ValueError as exc:
        raise ManifestError(f"manifest path escapes workspace: {relative}") from exc
    return candidate


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ManifestError(message)


def _dataset_record(filename: str) -> dict[str, Any]:
    path = RESULTS / filename
    _require(path.is_file(), f"missing dataset: {filename}")
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames
            rows = list(reader)
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ManifestError(f"invalid dataset {filename}: {exc}") from exc
    _require(fieldnames is not None, f"dataset has no header: {filename}")
    _require(set(fieldnames) == DATASET_COLUMNS[filename], f"dataset columns mismatch: {filename}")
    _require(len(rows) == EXPECTED_DATASET_ROWS[filename], f"dataset row count mismatch: {filename}")
    return {
        "path": _workspace_path(path),
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
        "row_count": len(rows),
        "columns": fieldnames,
    }


def _file_record(path: Path, role: str | None = None) -> dict[str, Any]:
    _require(path.is_file(), f"missing file: {_workspace_path(path)}")
    record = {
        "path": _workspace_path(path),
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
    }
    if role is not None:
        record["role"] = role
    return record


def _package_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "UNAVAILABLE"


def _git_state() -> dict[str, Any]:
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=WORKSPACE,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status_lines = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=normal"],
            cwd=WORKSPACE,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        return {
            "available": False,
            "head_commit": None,
            "repository_dirty": None,
            "relevant_paths_dirty": None,
            "disclosure": "Git metadata unavailable; no raw diff is stored.",
        }

    relevant_prefixes = (
        "prototype/scripts/run_experiments.py",
        "prototype/src/keystone/sampling.py",
        "prototype/src/keystone/simulation.py",
        "prototype/pyproject.toml",
        "prototype/uv.lock",
        "prototype/results/",
    )
    changed_paths = [line[3:] for line in status_lines if len(line) >= 4]
    return {
        "available": True,
        "head_commit": head,
        "repository_dirty": bool(status_lines),
        "relevant_paths_dirty": any(
            path.startswith(relevant_prefixes) for path in changed_paths
        ),
        "disclosure": "Boolean dirty-state disclosure only; raw diff and filenames are not embedded.",
    }


def _generation_timestamp() -> dict[str, Any]:
    raw_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if raw_epoch is None:
        return {
            "policy": "SOURCE_DATE_EPOCH_OR_OMITTED",
            "source_date_epoch": None,
            "generated_at_utc": None,
            "reason": "Wall-clock time is omitted to keep manifest-only regeneration deterministic.",
        }
    try:
        epoch = int(raw_epoch)
        generated = datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    except (ValueError, OverflowError, OSError) as exc:
        raise ManifestError("SOURCE_DATE_EPOCH must be a valid integer timestamp") from exc
    return {
        "policy": "SOURCE_DATE_EPOCH_OR_OMITTED",
        "source_date_epoch": epoch,
        "generated_at_utc": generated,
        "reason": "Timestamp is derived only from the caller-supplied reproducible epoch.",
    }


def _experiment_declarations() -> list[dict[str, Any]]:
    iid_probabilities = [round(x * 0.025, 3) for x in range(17)]
    domain_counts = [2, 4, 8, 16]
    withholder_counts = list(range(15))
    sample_sizes = [4, 6, 8, 10, 12, 16]
    audit_counts = [1, 2, 4, 8]
    return [
        {
            "experiment_id": "EXP-THEORETICAL-BOUND",
            "kind": "DETERMINISTIC_ANALYTIC",
            "parameters": {
                "n": 32,
                "thresholds": [17, 22, 25],
                "sample_sizes": list(range(1, 17)),
                "seed": None,
            },
            "datasets": ["prototype/results/theoretical_bound.csv"],
            "figures": [
                "prototype/results/figures/figure_1_theoretical_detection_bound.png",
                "prototype/results/figures/figure_1_theoretical_detection_bound.svg",
            ],
        },
        {
            "experiment_id": "EXP-IID-FAILURE-SWEEP",
            "kind": "SEEDED_MONTE_CARLO",
            "parameters": {
                "n": 32, "threshold": 22, "sample_size": 8,
                "required_audit_responses": 8,
                "independent_offline_probabilities": iid_probabilities,
                "domain_outage_probability": 0.0, "domains": 4,
                "trials_per_scenario": 12000,
                "seeds": [202600 + int(value * 1000) for value in iid_probabilities],
            },
            "datasets": ["prototype/results/iid_failure_sweep.csv"],
            "figures": [
                "prototype/results/figures/figure_2_iid_failure_sweep.png",
                "prototype/results/figures/figure_2_iid_failure_sweep.svg",
            ],
        },
        {
            "experiment_id": "EXP-DOMAIN-DIVERSITY",
            "kind": "SEEDED_MONTE_CARLO",
            "parameters": {
                "n": 32, "threshold": 22, "domain_counts": domain_counts,
                "sample_size_rule": "max(8, domains)",
                "required_audit_responses_rule": "max(8, domains)",
                "independent_offline_probability": 0.01,
                "domain_outage_probability": 0.15,
                "trials_per_scenario": 20000,
                "seeds": [3300 + value for value in domain_counts],
            },
            "datasets": ["prototype/results/domain_diversity.csv"],
            "figures": [
                "prototype/results/figures/figure_3_domain_diversity.png",
                "prototype/results/figures/figure_3_domain_diversity.svg",
            ],
        },
        {
            "experiment_id": "EXP-SELECTIVE-WITHHOLDING",
            "kind": "SEEDED_MONTE_CARLO_NEGATIVE_RESULT",
            "parameters": {
                "n": 32, "threshold": 22, "sample_size": 8,
                "required_audit_responses": 8,
                "independent_offline_probability": 0.0,
                "domain_outage_probability": 0.0, "domains": 4,
                "selective_withholders": withholder_counts,
                "trials_per_scenario": 4000,
                "seeds": [4400 + value for value in withholder_counts],
            },
            "datasets": ["prototype/results/selective_withholding.csv"],
            "figures": [
                "prototype/results/figures/figure_4_selective_withholding_gap.png",
                "prototype/results/figures/figure_4_selective_withholding_gap.svg",
            ],
        },
        {
            "experiment_id": "EXP-SAMPLING-STRATEGY",
            "kind": "SEEDED_MATCHED_POLICY_MONTE_CARLO",
            "parameters": {
                "n": 32, "threshold": 22, "sample_sizes": sample_sizes,
                "strategies": ["uniform", "stratified"],
                "required_audit_responses_rule": "sample_size",
                "independent_offline_probability": 0.01,
                "domain_outage_probability": 0.20, "domains": 4,
                "trials_per_scenario": 16000,
                "seed_rule": "5500 + sample_size; shared by both strategies",
                "seeds": [5500 + value for value in sample_sizes],
            },
            "datasets": ["prototype/results/sampling_strategy.csv"],
            "figures": [
                "prototype/results/figures/figure_5_sampling_strategy.png",
                "prototype/results/figures/figure_5_sampling_strategy.svg",
            ],
        },
        {
            "experiment_id": "EXP-EXACT-STRATIFIED-VALIDATION",
            "kind": "EXACT_PLUS_SEEDED_MONTE_CARLO",
            "parameters": {
                "strata": [[8, 5, 2], [8, 5, 2], [8, 5, 2], [8, 5, 2]],
                "required_successes": 6, "trials": 100000, "seed": 20260829,
            },
            "datasets": ["prototype/results/exact_stratified_validation.csv"],
            "figures": [],
        },
        {
            "experiment_id": "EXP-MARKOV-TEMPORAL-DEPENDENCE",
            "kind": "EXPLORATORY_SEEDED_MONTE_CARLO",
            "parameters": {
                "n": 12, "threshold": 8, "sample_size": 4,
                "required_valid": 3, "audit_counts": audit_counts,
                "trials_per_scenario": 12000,
                "online_to_offline": 0.22, "offline_to_online": 0.08,
                "initial_state": "online",
                "seeds": [20260830 + value for value in audit_counts],
            },
            "datasets": ["prototype/results/markov_temporal_dependence.csv"],
            "figures": [],
        },
    ]


def build_experiment_manifest(mode: str = "MANIFEST_ONLY") -> dict[str, Any]:
    datasets = [_dataset_record(filename) for filename in DATASET_COLUMNS]
    figures = [_file_record(FIGURES / filename) for filename in EXPECTED_FIGURES]
    input_roles = {
        "prototype/scripts/run_experiments.py": "GENERATOR",
        "prototype/src/keystone/sampling.py": "SOURCE",
        "prototype/src/keystone/simulation.py": "SOURCE",
        "prototype/pyproject.toml": "PROJECT_CONFIG",
        "prototype/uv.lock": "DEPENDENCY_LOCK",
    }
    inputs = [
        _file_record(WORKSPACE / relative, input_roles[relative])
        for relative in HASH_BOUND_INPUTS
    ]
    return {
        "schema_id": "KEYSTONE_PREAUTH_EXPERIMENT_MANIFEST",
        "schema_version": 1,
        "status": "PRELIMINARY_PREAUTHORIZATION",
        "authorization_boundary": "PREAUTHORIZATION_ONLY",
        "scientific_evidence_status": "NOT_SCIENTIFIC_EVIDENCE",
        "independence_status": "SAME_WORKSPACE_NOT_INDEPENDENT",
        "production_validation_status": "NOT_ASSESSED",
        "generator": {
            "mode": mode,
            "working_directory": "prototype",
            "full_generation_argv": ["python", "scripts/run_experiments.py"],
            "manifest_only_argv": ["python", "scripts/run_experiments.py", "--manifest-only"],
            "check_argv": ["python", "scripts/run_experiments.py", "--check-manifest"],
        },
        "generation_timestamp": _generation_timestamp(),
        "runtime": {
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "python_executable": sys.executable,
            "platform_system": platform.system(),
            "platform_release": platform.release(),
            "platform_machine": platform.machine(),
            "libraries": {
                "matplotlib": _package_version("matplotlib"),
                "numpy": _package_version("numpy"),
                "keystone-mpp": _package_version("keystone-mpp"),
            },
            "matplotlib_backend": plt.get_backend(),
        },
        "git": _git_state(),
        "inputs": inputs,
        "experiments": _experiment_declarations(),
        "outputs": {"datasets": datasets, "figures": figures},
        "exclusions": [
            {
                "path": "prototype/results/baseline.json",
                "reason": "Generated by the separately invoked CLI baseline workflow.",
            },
            {
                "path": "prototype/results/crypto_benchmark.csv",
                "reason": "Generated by prototype/scripts/benchmark_crypto.py and handled separately.",
            },
            {
                "path": "contracts/gas_report.csv",
                "reason": "Generated by the separate Foundry gas snapshot workflow.",
            },
            {
                "path": "paper/test_vectors.json|paper/signature_test_vectors.json",
                "reason": "Deterministic fixtures have separate exporters and freshness checks.",
            },
        ],
        "limitations": [
            "This manifest binds existing same-workspace preliminary outputs only.",
            "It does not prove authorized confirmatory execution, scientific validity, independence, external reproduction, or production behavior.",
            "CSV row counts and file hashes establish mechanical consistency, not evidentiary sufficiency.",
        ],
    }


def validate_experiment_manifest(manifest: dict[str, Any]) -> None:
    _require(isinstance(manifest, dict), "manifest root must be an object")
    expected_labels = {
        "schema_id": "KEYSTONE_PREAUTH_EXPERIMENT_MANIFEST",
        "schema_version": 1,
        "status": "PRELIMINARY_PREAUTHORIZATION",
        "authorization_boundary": "PREAUTHORIZATION_ONLY",
        "scientific_evidence_status": "NOT_SCIENTIFIC_EVIDENCE",
        "independence_status": "SAME_WORKSPACE_NOT_INDEPENDENT",
        "production_validation_status": "NOT_ASSESSED",
    }
    for key, expected in expected_labels.items():
        _require(manifest.get(key) == expected, f"manifest label mismatch: {key}")

    generator = manifest.get("generator")
    _require(isinstance(generator, dict), "generator metadata missing")
    _require(generator.get("mode") in {"MANIFEST_ONLY", "FULL_OUTPUT_GENERATION"}, "generator mode mismatch")
    _require(generator.get("working_directory") == "prototype", "generator working directory mismatch")
    expected_argv = {
        "full_generation_argv": ["python", "scripts/run_experiments.py"],
        "manifest_only_argv": ["python", "scripts/run_experiments.py", "--manifest-only"],
        "check_argv": ["python", "scripts/run_experiments.py", "--check-manifest"],
    }
    for key, expected in expected_argv.items():
        _require(generator.get(key) == expected, f"generator argv mismatch: {key}")

    timestamp = manifest.get("generation_timestamp")
    _require(isinstance(timestamp, dict), "generation timestamp policy missing")
    _require(timestamp.get("policy") == "SOURCE_DATE_EPOCH_OR_OMITTED", "timestamp policy mismatch")
    if timestamp.get("source_date_epoch") is None:
        _require(timestamp.get("generated_at_utc") is None, "non-reproducible generated timestamp")
    else:
        _require(isinstance(timestamp.get("source_date_epoch"), int), "invalid source date epoch")
        _require(isinstance(timestamp.get("generated_at_utc"), str), "derived timestamp missing")

    runtime = manifest.get("runtime")
    _require(isinstance(runtime, dict), "runtime metadata missing")
    for key in (
        "python_version", "python_implementation", "python_executable",
        "platform_system", "platform_release", "platform_machine",
        "matplotlib_backend",
    ):
        _require(isinstance(runtime.get(key), str) and runtime[key], f"runtime metadata missing: {key}")
    libraries = runtime.get("libraries")
    _require(isinstance(libraries, dict), "library environment missing")
    _require(set(libraries) == {"matplotlib", "numpy", "keystone-mpp"}, "library environment mismatch")

    git = manifest.get("git")
    _require(isinstance(git, dict), "git disclosure missing")
    _require(isinstance(git.get("available"), bool), "git availability disclosure invalid")
    if git["available"]:
        _require(
            isinstance(git.get("head_commit"), str)
            and len(git["head_commit"]) == 40
            and all(character in "0123456789abcdef" for character in git["head_commit"]),
            "git commit disclosure invalid",
        )
        _require(isinstance(git.get("repository_dirty"), bool), "repository dirty disclosure invalid")
        _require(isinstance(git.get("relevant_paths_dirty"), bool), "relevant dirty disclosure invalid")

    input_records = manifest.get("inputs")
    _require(isinstance(input_records, list), "manifest inputs missing")
    input_paths = [record.get("path") for record in input_records if isinstance(record, dict)]
    _require(len(input_paths) == len(set(input_paths)) == len(HASH_BOUND_INPUTS), "input path set mismatch")
    _require(set(input_paths) == set(HASH_BOUND_INPUTS), "input path set mismatch")
    expected_roles = {
        "prototype/scripts/run_experiments.py": "GENERATOR",
        "prototype/src/keystone/sampling.py": "SOURCE",
        "prototype/src/keystone/simulation.py": "SOURCE",
        "prototype/pyproject.toml": "PROJECT_CONFIG",
        "prototype/uv.lock": "DEPENDENCY_LOCK",
    }
    for record in input_records:
        _require(record.get("role") == expected_roles[record["path"]], f"input role mismatch: {record['path']}")
        path = _resolve_workspace_path(record["path"])
        _require(path.is_file(), f"missing input: {record['path']}")
        _require(_sha256(path) == record.get("sha256"), f"input hash mismatch: {record['path']}")
        _require(path.stat().st_size == record.get("bytes"), f"input bytes mismatch: {record['path']}")

    dataset_records = manifest.get("outputs", {}).get("datasets")
    _require(isinstance(dataset_records, list), "dataset output inventory missing")
    expected_dataset_paths = {f"prototype/results/{name}" for name in DATASET_COLUMNS}
    dataset_paths = [record.get("path") for record in dataset_records if isinstance(record, dict)]
    _require(len(dataset_paths) == len(set(dataset_paths)), "duplicate dataset output path")
    _require(set(dataset_paths) == expected_dataset_paths, "dataset output path set mismatch")
    for record in dataset_records:
        path = _resolve_workspace_path(record["path"])
        filename = path.name
        current = _dataset_record(filename)
        _require(current["sha256"] == record.get("sha256"), f"dataset hash mismatch: {filename}")
        _require(current["row_count"] == record.get("row_count"), f"dataset row count mismatch: {filename}")
        _require(current["bytes"] == record.get("bytes"), f"dataset bytes mismatch: {filename}")
        _require(current["columns"] == record.get("columns"), f"dataset columns mismatch: {filename}")

    figure_records = manifest.get("outputs", {}).get("figures")
    _require(isinstance(figure_records, list), "figure output inventory missing")
    expected_figure_paths = {f"prototype/results/figures/{name}" for name in EXPECTED_FIGURES}
    figure_paths = [record.get("path") for record in figure_records if isinstance(record, dict)]
    _require(len(figure_paths) == len(set(figure_paths)), "duplicate figure output path")
    _require(set(figure_paths) == expected_figure_paths, "figure output path set mismatch")
    for record in figure_records:
        path = _resolve_workspace_path(record["path"])
        _require(path.is_file(), f"missing figure: {record['path']}")
        _require(_sha256(path) == record.get("sha256"), f"figure hash mismatch: {record['path']}")
        _require(path.stat().st_size == record.get("bytes"), f"figure bytes mismatch: {record['path']}")

    experiments = manifest.get("experiments")
    _require(experiments == _experiment_declarations(), "experiment declarations mismatch")
    experiment_ids = [item.get("experiment_id") for item in experiments if isinstance(item, dict)]
    _require(len(experiment_ids) == len(set(experiment_ids)) == 7, "duplicate/missing experiment ID")
    declared_datasets = {path for item in experiments for path in item.get("datasets", [])}
    declared_figures = {path for item in experiments for path in item.get("figures", [])}
    _require(declared_datasets == expected_dataset_paths, "experiment-to-dataset mapping mismatch")
    _require(declared_figures == expected_figure_paths, "experiment-to-figure mapping mismatch")


def _write_manifest(mode: str) -> None:
    manifest = build_experiment_manifest(mode)
    validate_experiment_manifest(manifest)
    rendered = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    temporary = MANIFEST.with_suffix(".json.tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(MANIFEST)


def _check_manifest() -> None:
    _require(MANIFEST.is_file(), "experiment manifest is missing")
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"invalid experiment manifest JSON: {exc}") from exc
    validate_experiment_manifest(manifest)


def _generate_outputs() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    datasets = {
        "theoretical_bound.csv": theoretical_bound_figure(),
        "iid_failure_sweep.csv": iid_failure_figure(),
        "domain_diversity.csv": domain_diversity_figure(),
        "selective_withholding.csv": selective_withholding_figure(),
        "sampling_strategy.csv": sampling_strategy_figure(),
        "exact_stratified_validation.csv": exact_stratified_validation_table(),
        "markov_temporal_dependence.csv": markov_temporal_dependence_table(),
    }
    for filename, rows in datasets.items():
        _write_rows(RESULTS / filename, rows)
    _write_manifest("FULL_OUTPUT_GENERATION")


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--manifest-only", action="store_true")
    modes.add_argument("--check-manifest", action="store_true")
    args = parser.parse_args()
    try:
        if args.check_manifest:
            _check_manifest()
            print("PASS: experiment manifest matches current hash-bound outputs")
        elif args.manifest_only:
            _write_manifest("MANIFEST_ONLY")
            print(f"Wrote {_workspace_path(MANIFEST)} without regenerating experiments")
        else:
            _generate_outputs()
            print(f"Wrote {_workspace_path(MANIFEST)} after full output generation")
    except ManifestError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
