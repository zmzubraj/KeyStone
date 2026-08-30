#!/usr/bin/env python3
"""Generate preliminary paper tables from canonical KEYSTONE result files."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "paper" / "tables"
MARKDOWN = TABLE_DIR / "preliminary_results.md"
LATEX = TABLE_DIR / "preliminary_results.tex"


def _format_interval(value: float, low: float, high: float) -> str:
    return f"{value:.5f} [{low:.5f}, {high:.5f}]"


def _latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(character, character) for character in value)


def _load_sources() -> tuple[
    list[dict[str, object]],
    dict[str, str],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    baseline = json.loads((ROOT / "prototype" / "results" / "baseline.json").read_text())
    with (ROOT / "prototype" / "results" / "exact_stratified_validation.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        exact = next(csv.DictReader(handle))
    with (ROOT / "contracts" / "gas_report.csv").open(newline="", encoding="utf-8") as handle:
        gas = list(csv.DictReader(handle))
    with (ROOT / "prototype" / "results" / "markov_temporal_dependence.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        temporal = list(csv.DictReader(handle))
    with (ROOT / "prototype" / "results" / "crypto_benchmark.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        crypto = list(csv.DictReader(handle))
    return baseline, exact, gas, temporal, crypto


def _scenario_label(name: str) -> str:
    labels = {
        "iid-10pct-uniform": "IID 10%, uniform",
        "domain-20pct-uniform": "Domain outage 20%, uniform",
        "domain-20pct-stratified": "Domain outage 20%, stratified",
        "selective-withholding-11": "11 selective withholders",
    }
    return labels.get(name, name)


def render_markdown() -> str:
    baseline, exact, gas, temporal, crypto = _load_sources()
    lines = [
        "# Preliminary KEYSTONE Paper Tables",
        "",
        "> Evidence label: internal preliminary simulation/contract evidence. These tables are",
        "> not confirmatory or independently verified until the frozen study-design and",
        "> research-case gates authorize their rerun.",
        "",
        "## Monte Carlo outcomes",
        "",
        "| Scenario | Trials | Reconstruction success (95% Wilson CI) | Audit pass (95% Wilson CI) | Catastrophic detection (95% Wilson CI; conditional n) |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in baseline:
        detection = _format_interval(
            float(row["catastrophic_detection_rate"]),
            float(row["catastrophic_detection_ci_low"]),
            float(row["catastrophic_detection_ci_high"]),
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    _scenario_label(str(row["name"])),
                    f"{int(row['trials']):,}",
                    _format_interval(
                        float(row["reconstruction_success_rate"]),
                        float(row["reconstruction_success_ci_low"]),
                        float(row["reconstruction_success_ci_high"]),
                    ),
                    _format_interval(
                        float(row["audit_pass_rate"]),
                        float(row["audit_pass_ci_low"]),
                        float(row["audit_pass_ci_high"]),
                    ),
                    f"{detection}; n={int(row['catastrophic_trials']):,}",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Exact fixed-quota stratified validation",
            "",
            "| Design | Required valid | Exact tail | Monte Carlo tail | Absolute error | Trials | Seed |",
            "|---|---:|---:|---:|---:|---:|---:|",
            f"| {exact['design']} | {exact['required_successes']} | {float(exact['exact_tail_probability']):.9f} | {float(exact['monte_carlo_tail_probability']):.9f} | {float(exact['absolute_error']):.9f} | {int(exact['trials']):,} | {exact['seed']} |",
            "",
            "The fixed-quota exact calculation is not interchangeable with the",
            "minimum-domain-coverage plus uniform-remainder sampler.",
            "",
            "## Exploratory temporal-dependence boundary",
            "",
            "| Audits | Final catastrophic trials | All audits pass + final catastrophic | Conditional sequence rate (95% Wilson CI) | Static-set repeated bound |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    for row in temporal:
        lines.append(
            f"| {row['audits']} | {int(row['final_catastrophic_trials']):,} | "
            f"{int(row['all_audits_pass_and_final_catastrophic_count']):,} | "
            f"{_format_interval(float(row['conditional_sequence_false_accept_rate']), float(row['conditional_sequence_false_accept_ci_low']), float(row['conditional_sequence_false_accept_ci_high']))} | "
            f"{float(row['static_set_repeated_bound']):.6f} |"
        )
    lines.extend(
        [
            "",
            "The evolving-state sequence rate and static-ready-set bound have different",
            "estimands and must not be substituted for one another.",
            "",
            "## Local cryptographic and signature microbenchmark",
            "",
            "| n | t | Keygen median (ms) | Seal median (ms) | Partial proof median (ms) | Partial verify median (ms) | Open median (ms) | Ed25519 sign median (ms) | Ed25519 verify median (ms) | Signature bytes |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in crypto:
        lines.append(
            f"| {row['n']} | {row['threshold']} | {float(row['keygen_median_ms']):.3f} | "
            f"{float(row['seal_median_ms']):.3f} | {float(row['partial_proof_median_ms']):.3f} | "
            f"{float(row['partial_verify_median_ms']):.3f} | {float(row['open_median_ms']):.3f} | "
            f"{float(row['signature_sign_median_ms']):.3f} | "
            f"{float(row['signature_verify_median_ms']):.3f} | {row['signature_size_bytes']} |"
        )
    lines.extend(
        [
            "",
            "These are local single-process research timings, not production throughput claims.",
            "",
            "## Solidity operation gas",
            "",
            "| Operation | Gas | Scope |",
            "|---|---:|---|",
        ]
    )
    for row in gas:
        lines.append(
            f"| `{row['operation']}` | {int(row['gas']):,} | {row['measurement_scope']} |"
        )
    lines.extend(
        [
            "",
            "Canonical sources: `prototype/results/baseline.json`,",
            "`prototype/results/exact_stratified_validation.csv`,",
            "`prototype/results/markov_temporal_dependence.csv`, and",
            "`prototype/results/crypto_benchmark.csv`, and",
            "`contracts/gas_report.csv`.",
            "",
        ]
    )
    return "\n".join(lines)


def render_latex() -> str:
    baseline, exact, gas, temporal, crypto = _load_sources()
    lines = [
        "% Generated by scripts/export_paper_tables.py; do not edit manually.",
        "% Evidence label: internal preliminary; rerun after study-design freeze.",
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Preliminary Monte Carlo outcomes. Intervals are two-sided 95\% Wilson score intervals; catastrophic detection is conditioned on the reported number of catastrophic trials.}",
        r"\label{tab:preliminary-monte-carlo}",
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Scenario & Trials & Reconstruction & Audit pass & Detection (conditional $n$) \\",
        r"\midrule",
    ]
    for row in baseline:
        reconstruction = _format_interval(
            float(row["reconstruction_success_rate"]),
            float(row["reconstruction_success_ci_low"]),
            float(row["reconstruction_success_ci_high"]),
        )
        audit = _format_interval(
            float(row["audit_pass_rate"]),
            float(row["audit_pass_ci_low"]),
            float(row["audit_pass_ci_high"]),
        )
        detection = _format_interval(
            float(row["catastrophic_detection_rate"]),
            float(row["catastrophic_detection_ci_low"]),
            float(row["catastrophic_detection_ci_high"]),
        )
        lines.append(
            f"{_latex_escape(_scenario_label(str(row['name'])))} & {int(row['trials']):,} & "
            f"{reconstruction} & {audit} & {detection} ({int(row['catastrophic_trials']):,}) \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table*}",
            "",
            r"\begin{table}[t]",
            r"\centering",
            r"\caption{Exact validation for fixed-quota domain-stratified sampling.}",
            r"\label{tab:exact-stratified-validation}",
            r"\begin{tabular}{rrr}",
            r"\toprule",
            r"Exact tail & Monte Carlo tail & Absolute error \\",
            r"\midrule",
            f"{float(exact['exact_tail_probability']):.9f} & {float(exact['monte_carlo_tail_probability']):.9f} & {float(exact['absolute_error']):.9f} \\\\ ".rstrip(),
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
            "",
            r"\begin{table*}[t]",
            r"\centering",
            r"\caption{Local single-process cryptographic and Ed25519 signature microbenchmarks. These timings do not establish production throughput.}",
            r"\label{tab:preliminary-crypto-benchmark}",
            r"\begin{tabular}{rrrrrrrrrr}",
            r"\toprule",
            r"$n$ & $t$ & Keygen & Seal & Proof & Proof verify & Open & Sign & Sig. verify & Sig. bytes \\",
            r"\midrule",
        ]
    )
    for row in crypto:
        lines.append(
            f"{row['n']} & {row['threshold']} & {float(row['keygen_median_ms']):.3f} & "
            f"{float(row['seal_median_ms']):.3f} & {float(row['partial_proof_median_ms']):.3f} & "
            f"{float(row['partial_verify_median_ms']):.3f} & {float(row['open_median_ms']):.3f} & "
            f"{float(row['signature_sign_median_ms']):.3f} & "
            f"{float(row['signature_verify_median_ms']):.3f} & {row['signature_size_bytes']} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table*}",
            "",
            r"\begin{table}[t]",
            r"\centering",
            r"\caption{Exploratory temporal-dependence boundary. The sequence rate is not the static-ready-set repeated-audit bound.}",
            r"\label{tab:temporal-boundary}",
            r"\begin{tabular}{rrrr}",
            r"\toprule",
            r"Audits & Final catastrophic & Sequence rate [95\% CI] & Static bound \\",
            r"\midrule",
        ]
    )
    for row in temporal:
        interval = _format_interval(
            float(row["conditional_sequence_false_accept_rate"]),
            float(row["conditional_sequence_false_accept_ci_low"]),
            float(row["conditional_sequence_false_accept_ci_high"]),
        )
        lines.append(
            f"{row['audits']} & {int(row['final_catastrophic_trials']):,} & {interval} & "
            f"{float(row['static_set_repeated_bound']):.6f} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
            "",
            r"\begin{table}[t]",
            r"\centering",
            r"\caption{Preliminary Foundry test-body gas measurements; setup is excluded and small harness overhead may remain.}",
            r"\label{tab:preliminary-gas}",
            r"\begin{tabular}{lr}",
            r"\toprule",
            r"Operation & Gas \\",
            r"\midrule",
        ]
    )
    for row in gas:
        lines.append(f"{_latex_escape(row['operation'])} & {int(row['gas']):,} \\\\ ".rstrip())
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = {MARKDOWN: render_markdown(), LATEX: render_latex()}
    if args.check:
        stale = [path for path, content in expected.items() if not path.exists() or path.read_text() != content]
        if stale:
            for path in stale:
                print(f"STALE: {path.relative_to(ROOT)}")
            return 1
        print("PASS: paper tables match canonical result sources")
        return 0

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
        print(f"Wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
