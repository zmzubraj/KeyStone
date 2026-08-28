#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from keystone.sampling import catastrophic_false_accept_probability  # noqa: E402
from keystone.simulation import Scenario, run_monte_carlo  # noqa: E402

RESULTS = PROJECT / "results"
FIGURES = RESULTS / "figures"


def _write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


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
    plt.savefig(FIGURES / "figure_1_theoretical_detection_bound.png", dpi=180)
    plt.savefig(FIGURES / "figure_1_theoretical_detection_bound.svg")
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
            "audit_pass_rate": result["audit_pass_rate"],
            "catastrophic_detection_rate": result["catastrophic_detection_rate"],
        })
    plt.figure(figsize=(8, 5))
    plt.plot(
        [row["offline_probability"] for row in rows],
        [row["reconstruction_success_rate"] for row in rows],
        marker="o",
        label="Dispute reconstruction success",
    )
    plt.plot(
        [row["offline_probability"] for row in rows],
        [row["audit_pass_rate"] for row in rows],
        marker="s",
        label="All-response audit pass",
    )
    plt.xlabel("Independent custodian offline probability")
    plt.ylabel("Probability")
    plt.title("Reconstructability and audit pass rate under independent failures")
    plt.ylim(0.0, 1.02)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "figure_2_iid_failure_sweep.png", dpi=180)
    plt.savefig(FIGURES / "figure_2_iid_failure_sweep.svg")
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
            "catastrophic_rate": result["catastrophic_rate"],
        })
    plt.figure(figsize=(8, 5))
    plt.plot(
        [row["domains"] for row in rows],
        [row["reconstruction_success_rate"] for row in rows],
        marker="o",
    )
    plt.xlabel("Independent failure domains")
    plt.ylabel("Dispute reconstruction success probability")
    plt.title("Committee diversity reduces correlated-outage risk")
    plt.ylim(0.0, 1.02)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES / "figure_3_domain_diversity.png", dpi=180)
    plt.savefig(FIGURES / "figure_3_domain_diversity.svg")
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
            "audit_pass_rate": result["audit_pass_rate"],
        })
    plt.figure(figsize=(8, 5))
    plt.plot(
        [row["selective_withholders"] for row in rows],
        [row["reconstruction_success_rate"] for row in rows],
        marker="o",
        label="Target dispute reconstruction",
    )
    plt.plot(
        [row["selective_withholders"] for row in rows],
        [row["audit_pass_rate"] for row in rows],
        marker="s",
        label="Prior canary audit",
    )
    plt.axvline(11, linestyle="--", label="n-t+1 = 11")
    plt.xlabel("Custodians that answer audits but withhold target dispute")
    plt.ylabel("Probability")
    plt.title("Selective withholding is a stated limitation of ordinary readiness sampling")
    plt.ylim(-0.02, 1.02)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "figure_4_selective_withholding_gap.png", dpi=180)
    plt.savefig(FIGURES / "figure_4_selective_withholding_gap.svg")
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
                "audit_pass_rate": result["audit_pass_rate"],
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
    plt.xlabel("Audit sample size")
    plt.ylabel("Detection rate conditioned on catastrophic state")
    plt.title("Uniform versus failure-domain-stratified sampling")
    plt.ylim(0.0, 1.02)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "figure_5_sampling_strategy.png", dpi=180)
    plt.savefig(FIGURES / "figure_5_sampling_strategy.svg")
    plt.close()
    return rows


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    datasets = {
        "theoretical_bound.csv": theoretical_bound_figure(),
        "iid_failure_sweep.csv": iid_failure_figure(),
        "domain_diversity.csv": domain_diversity_figure(),
        "selective_withholding.csv": selective_withholding_figure(),
        "sampling_strategy.csv": sampling_strategy_figure(),
    }
    for filename, rows in datasets.items():
        _write_rows(RESULTS / filename, rows)

    manifest = {
        "datasets": list(datasets),
        "figures": sorted(path.name for path in FIGURES.iterdir()),
        "notes": [
            "Monte Carlo outputs are deterministic for the frozen seeds.",
            "The selective-withholding experiment intentionally demonstrates a protocol limitation.",
            "Production claims require repeating experiments on real distributed nodes and a standard cryptographic library.",
        ],
    }
    (RESULTS / "experiment_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
