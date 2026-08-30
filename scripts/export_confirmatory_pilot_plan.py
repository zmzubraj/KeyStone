#!/usr/bin/env python3
"""Export the fail-closed KEYSTONE confirmatory pilot plan and run contract."""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
import sys


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = Path("research-case/program-state.json")
CHARTER_PATH = Path("research-case/00-governance/program-charter.md")
PLAN_PATH = Path("research-case/02-feasibility/pilot-plan.md")
CONTRACT_PATH = Path("research-case/02-feasibility/pilot-run-contract.csv")
DESIGN_PATHS = (
    Path("research-case/03-design/protocol.md"),
    Path("research-case/03-design/analysis-plan.md"),
    Path("research-case/03-design/power-or-precision.md"),
    Path("research-case/03-design/preregistration-and-deviations.md"),
    Path("research-case/03-design/pc03-prospective-amendment.md"),
    Path("research-case/03-design/pc03-prospective-counts.csv"),
    Path("research-case/03-design/pc03-seed-schedule.csv"),
)
PC03_COUNTS_PATH = Path("research-case/03-design/pc03-prospective-counts.csv")

FIELDS = (
    "result_id",
    "claim_ids",
    "mpp_lane",
    "result_class",
    "decision_role",
    "experimental_unit",
    "denominator",
    "planned_replicates",
    "environment_status",
    "execution_status",
    "authorized",
    "independent",
    "observed_outcome",
    "output_status",
    "historical_output_reuse",
    "green_rule",
    "amber_rule",
    "red_stop_rule",
    "required_predecessors",
    "planned_output",
)


class PilotPlanError(RuntimeError):
    """Raised when the pilot package cannot preserve its fail-closed boundary."""


def _read_text(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PilotPlanError(f"cannot read {label}: {exc}") from exc


def _validate(root: Path) -> None:
    try:
        state = json.loads(_read_text(root / STATE_PATH, "program state"))
    except json.JSONDecodeError as exc:
        raise PilotPlanError(f"cannot parse program state: {exc}") from exc
    required = {
        "status": "ACTIVE",
        "current_phase": "INTAKE",
        "resume_from": "INTAKE",
        "novelty_status": "UNRESOLVED",
        "feasibility_decision": "UNASSESSED",
        "solution_viability_status": "ASSERTED_ONLY",
        "acceptance_readiness": "NOT_ASSESSABLE",
    }
    for field, expected in required.items():
        actual = state.get(field)
        if actual != expected:
            raise PilotPlanError(f"canonical {field} expected {expected}, got {actual}")

    charter = _read_text(root / CHARTER_PATH, "program charter").lower()
    phrases = ("final author order", "corresponding-author", "affiliation wording", "remain deferred")
    if not all(phrase in charter for phrase in phrases):
        raise PilotPlanError("program charter does not preserve the required author metadata deferral")

    design_text = "\n".join(_read_text(root / path, path.as_posix()) for path in DESIGN_PATHS)
    for result_id in _result_ids():
        if result_id not in design_text:
            raise PilotPlanError(f"design package does not close reserved result ID {result_id}")
    if "does not authorize execution" not in design_text.lower():
        raise PilotPlanError("design package lacks a non-authorization boundary")
    if "historical outputs may guide feasibility but may not act as the control arm" not in design_text.lower():
        raise PilotPlanError("design package lacks the historical-output reuse prohibition")
    required_amendment_phrases = (
        "32 primary seed blocks",
        "131,072 primary draws",
        "exploratory outputs were not used",
        "excluded_pending_environment_profile",
    )
    if not all(phrase in design_text.lower() for phrase in required_amendment_phrases):
        raise PilotPlanError("PC03 amendment does not freeze the required result-blind count boundary")

    try:
        with (root / PC03_COUNTS_PATH).open(encoding="utf-8", newline="") as handle:
            pc03_rows = {row["result_id"]: row for row in csv.DictReader(handle)}
    except (OSError, KeyError, csv.Error) as exc:
        raise PilotPlanError(f"cannot parse PC03 count contract: {exc}") from exc
    scheduled = {
        "RID-C003-IID-001",
        "RID-C003-STRAT-001",
        "RID-C003-SW-001",
    }
    for result_id in scheduled:
        row = pc03_rows.get(result_id)
        if row is None:
            raise PilotPlanError(f"PC03 count contract is missing {result_id}")
        expected = {
            "primary_seed_blocks_per_cell": "32",
            "reserve_seed_blocks_per_cell": "4",
            "draws_per_seed_block": "4096",
            "primary_draws_per_cell": "131072",
            "execution_status": "BLOCKED_PENDING_GATE",
            "authorized": "false",
            "observed_outcome": "NOT_COLLECTED",
        }
        for field, wanted in expected.items():
            if row.get(field) != wanted:
                raise PilotPlanError(f"PC03 {result_id} {field} is not frozen at {wanted}")
    deadline = pc03_rows.get("RID-C003-DEADLINE-001", {})
    if deadline.get("execution_status") != "EXCLUDED_PENDING_ENVIRONMENT_PROFILE":
        raise PilotPlanError("PC03 deadline family is not fail-closed and excluded")
    correlated = pc03_rows.get("RID-C003-CORR-001", {})
    if correlated.get("execution_status") != "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE":
        raise PilotPlanError("PC03 correlated family is not fail-closed and excluded")


def _result_ids() -> tuple[str, ...]:
    return (
        "RID-C001-SEP-001",
        "RID-C001-STATIC-001",
        "RID-C002-CRYPTO-001",
        "RID-C002-CONTRACT-001",
        "RID-C003-IID-001",
        "RID-C003-CORR-001",
        "RID-C003-STRAT-001",
        "RID-C003-SW-001",
        "RID-C003-DEADLINE-001",
    )


def _row(
    result_id: str,
    claims: str,
    lane: str,
    result_class: str,
    role: str,
    unit: str,
    denominator: str,
    planned: str,
    environment: str,
    green: str,
    amber: str,
    red: str,
    predecessors: str,
    output: str,
    execution_status: str = "BLOCKED_PENDING_GATE",
) -> dict[str, str]:
    return {
        "result_id": result_id,
        "claim_ids": claims,
        "mpp_lane": lane,
        "result_class": result_class,
        "decision_role": role,
        "experimental_unit": unit,
        "denominator": denominator,
        "planned_replicates": planned,
        "environment_status": environment,
        "execution_status": execution_status,
        "authorized": "false",
        "independent": "false",
        "observed_outcome": "NOT_COLLECTED",
        "output_status": "MISSING_NOT_AUTHORIZED",
        "historical_output_reuse": "PROHIBITED_AS_CONFIRMATORY_EVIDENCE",
        "green_rule": green,
        "amber_rule": amber,
        "red_stop_rule": red,
        "required_predecessors": predecessors,
        "planned_output": output,
    }


def _rows() -> list[dict[str, str]]:
    common = "PC01 authority verified|PC02 narrow novelty safely disposed|PC03 prospective design amendment independently verified"
    scheduled = "32_PRIMARY_SEED_BLOCKS_X_4096_DRAWS_PER_CELL_PLUS_4_RESERVE"
    return [
        _row("RID-C001-SEP-001", "C001", "MINIMUM_SHORT_PAPER_CORE", "DETERMINISTIC_OBLIGATION", "PRIMARY_SEPARATION", "preserved counterexample class", "counterexample classes per stated model variant", "EXHAUSTIVE_STATED_MODEL_VARIANTS", "LOCAL_SYNTHETIC_FROZEN", "Every stated variant has a reproducible witness", "A variant or wording remains underspecified; no execution", "Any required witness fails or novelty defeats the bounded distinction", common, "05-analysis/results/confirmatory/RID-C001-SEP-001.json"),
        _row("RID-C001-STATIC-001", "C001|C003", "MINIMUM_SHORT_PAPER_CORE", "ANALYTIC_CALCULATION", "PRIMARY_STATIC_BOUND", "frozen parameter cell", "exact parameter cells under one semantics", "EXHAUSTIVE_FROZEN_PARAMETER_CELLS", "LOCAL_SYNTHETIC_FROZEN", "Independent exact implementations agree on every frozen cell", "Semantics or parameter-cell closure is incomplete; no execution", "Any exact mismatch or silent semantics drift", common, "05-analysis/results/confirmatory/RID-C001-STATIC-001.json"),
        _row("RID-C002-CRYPTO-001", "C002|C003", "MINIMUM_SHORT_PAPER_CORE", "DETERMINISTIC_OBLIGATION", "PROTOTYPE_CORRECTNESS", "named cryptographic correctness case", "required threshold invalid-partial stale-context replay and ciphertext-boundary cases", "EXHAUSTIVE_NAMED_CASE_SET", "LOCAL_NON_PRODUCTION_FROZEN", "Every prespecified case matches its expected pass or fail outcome", "Named-case inventory or independent reproduction setup is incomplete; no execution", "Any threshold boundary context binding or invalid-partial rejection failure", common, "05-analysis/results/confirmatory/RID-C002-CRYPTO-001.json"),
        _row("RID-C002-CONTRACT-001", "C002", "MINIMUM_SHORT_PAPER_CORE", "DETERMINISTIC_OBLIGATION", "CONTRACT_EVIDENCE_BOUNDARY", "complete named lifecycle trace", "required success missing invalid and equivocation lifecycle cases", "EXHAUSTIVE_NAMED_CASE_SET", "LOCAL_NON_PRODUCTION_FROZEN", "Every prespecified lifecycle case matches its expected state and evidence record", "Case inventory or toolchain freeze is incomplete; no execution", "Any invalid transition evidence omission or equivocation-handling failure", common, "05-analysis/results/confirmatory/RID-C002-CONTRACT-001.json"),
        _row("RID-C003-IID-001", "C003", "MINIMUM_SHORT_PAPER_SUPPORT", "STOCHASTIC_SCENARIO_FAMILY", "MODEL_QUALIFICATION", "one prespecified seed block containing 4096 independent model draws", "131072 prespecified draws plus 32 blockwise estimates per IID cell", scheduled, "LOCAL_SYNTHETIC_FROZEN", "All cells meet the simultaneous +/-0.005 family bound and block reporting contract", "Count is frozen but independent review or execution authority remains open; no execution", "Retrofitted threshold invalid pooling overlapping streams or unmet frozen count", common + "|PC03 count and seed contract", "05-analysis/results/confirmatory/RID-C003-IID-001.csv"),
        _row("RID-C003-CORR-001", "C003", "MINIMUM_SHORT_PAPER_SUPPORT", "STOCHASTIC_SCENARIO_FAMILY", "CORRELATION_QUALIFICATION", "excluded pending truthful domain-label source", "no confirmatory denominator while excluded", "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE", "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE", "A later amendment freezes truthful domain labels placement comparator and count", "Excluded from the minimum confirmatory run", "Any correlated confirmatory execution or claim before the missing contract is frozen", common + "|separate correlated-domain amendment", "05-analysis/results/confirmatory/RID-C003-CORR-001.csv", "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE"),
        _row("RID-C003-STRAT-001", "C003", "MINIMUM_SHORT_PAPER_SUPPORT", "PAIRED_COMPARISON", "SAMPLING_POLICY_QUALIFICATION", "one matched seed block containing 4096 common-random-number policy pairs", "131072 matched draws plus 32 blockwise paired estimates per sample-size cell", scheduled, "LOCAL_SYNTHETIC_MATCHED_STREAMS_FROZEN", "All cells meet the simultaneous +/-0.01 paired-gap family bound", "Count is frozen but independent review or execution authority remains open; no execution", "Unpaired substitution invalid pooling overlapping streams or unmet frozen count", common + "|PC03 paired count and seed contract", "05-analysis/results/confirmatory/RID-C003-STRAT-001.csv"),
        _row("RID-C003-SW-001", "C003", "MINIMUM_SHORT_PAPER_CORE", "PAIRED_NEGATIVE_RESULT", "DECISIVE_LIMITATION", "one seed block containing 4096 draws with both audit and dispute outcomes", "131072 paired draws plus 32 blockwise gap estimates per adversary cell", scheduled, "LOCAL_SYNTHETIC_ADVERSARY_CELLS_FROZEN", "All cells meet the simultaneous +/-0.01 paired-gap family bound and the limitation is reported regardless of direction", "Count is frozen but independent review or execution authority remains open; no execution", "Outcome suppression unpaired treatment overlapping streams retrofitted threshold or claim expansion", common + "|PC03 paired count and seed contract", "05-analysis/results/confirmatory/RID-C003-SW-001.csv"),
        _row("RID-C003-DEADLINE-001", "C003", "EXTENDED_FULL_PAPER", "DISTRIBUTED_TRACE_BENCHMARK", "CONDITIONAL_DEADLINE_LIVENESS", "excluded pending environment profile", "no trace-level denominator while excluded", "EXCLUDED_PENDING_ENVIRONMENT_PROFILE", "EXCLUDED_PENDING_ENVIRONMENT_PROFILE", "Environment profile deadline interpretation precision target and per-profile count are frozen by a later amendment", "Excluded until profile trace denominator and deadline target are prospectively frozen", "Any execution before environment freeze live systems or secrets unsupported SLA wording or invalid pooling", common + "|separate deadline environment and precision amendment", "05-analysis/results/confirmatory/RID-C003-DEADLINE-001.csv", "EXCLUDED_PENDING_ENVIRONMENT_PROFILE"),
    ]


def _csv_text(rows: list[dict[str, str]]) -> str:
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def _plan_text(rows: list[dict[str, str]]) -> str:
    table = "\n".join(
        f"| `{r['result_id']}` | `{r['claim_ids']}` | `{r['mpp_lane']}` | {r['result_class']} | `{r['planned_replicates']}` | `{r['execution_status']}` |"
        for r in rows
    )
    return f"""# KEYSTONE minimum confirmatory pilot plan

Status: `DRAFT / PREAUTHORIZATION / NON-EXECUTABLE`
System: `KEYSTONE-MPP-F1`
Date: `2026-08-30`
Current canonical phase: `INTAKE`
Decision: `BLOCKED`
Recommended later path: `PILOT_FIRST`

This artifact is a result-blind design-readiness package. It does not issue `GO`,
does not authorize collection or execution, does not promote the canonical phase,
and does not convert any existing locally generated output into scientific evidence.
Final author order, corresponding-author designation, and exact affiliation wording
remain deferred for later accountable-human freeze.

## Decision target and contribution boundary

The minimum publishable target is a bounded short-paper case: public
pre-authorization evidence about present threshold-decryption serviceability is
distinct from ciphertext availability, while selective withholding remains a
decisive limitation. The stronger full-paper lane adds correlation-qualified
recommendations, a synthetic distributed deadline benchmark, external
reproduction, and independent specialist review. Neither lane may claim a new
cryptographic primitive, production security, unconditional liveness, deployment
impact, or universal novelty.

## Why execution remains blocked

- `PC01`: draft-design authority and no-conflict policy basis are recorded, but no separate pilot execution approval exists.
- `PC02`: narrow novelty remains unresolved until the open search and independent challenge surfaces close.
- `PC03`: IID, stratified-policy, and selective-withholding cells now have a
  result-blind count, precision, and seed amendment, but it remains developmental
  pending independent methods verification; correlated-domain and deadline cells
  remain excluded.
- `PC04`-`PC08`: distributed deadline evidence, proof review, independent reproduction, and systems/security challenge remain incomplete.

The current exploratory and internal outputs may inform feasibility only. They
must never be relabeled, copied, or reused as confirmatory evidence or as the
control arm for a future confirmatory result.

## Pilot objectives

1. Reproduce the property-separation witness and exact static calculation under frozen semantics.
2. Exercise the exhaustive cryptographic and contract boundary case sets under a bound revision.
3. Prospectively test the selective-withholding limitation and the minimum model-qualification families only after independent verification of the PC03 amendment and a separate signed start decision.
4. Keep deadline-conditioned liveness in the extended lane until the environment profile and trace-level target are frozen.
5. Produce claim-linked outputs that preserve failures, negative findings, denominators, seeds, environment metadata, and deviations.

## Result contract

| Result ID | Claims | Lane | Class | Planned replicates | Execution status |
| --- | --- | --- | --- | --- | --- |
{table}

The machine-readable source of this table is
`research-case/02-feasibility/pilot-run-contract.csv`.

## Progression and stop rules

Green means every predecessor is independently verified, an accountable
prospective amendment freezes all applicable decision parameters, the planned
denominator is met, and the output is bound to the preregistered result ID.
Amber means design detail remains unresolved; amber permits remediation only,
not execution. Red means stop or redesign: authority or novelty failure,
retrofitted thresholds, pseudoreplication, invalid pooling, prohibited secret or
production-system use, correctness-boundary failure, missing negative results,
or claim wording beyond the result contract.

## Minimum and extended lanes

The minimum short-paper core is `RID-C001-SEP-001`,
`RID-C001-STATIC-001`, `RID-C002-CRYPTO-001`,
`RID-C002-CONTRACT-001`, and the limitation-bearing
`RID-C003-SW-001`. IID and stratification are supporting qualification families
bound by the draft PC03 amendment but still require independent design
verification and separate execution authority. Correlated-domain and distributed
deadline row is an extended full-paper family; if its gate remains open, the
deadline result and any SLA-like wording must be excluded rather than imputed.

## Contamination barrier and provenance

- Future confirmatory files must be newly generated under the reserved `RID-*` paths.
- Existing `prototype/results/*` and `05-analysis/results/exploratory-findings.csv` remain exploratory or internal only.
- No observed numeric outcome appears in this plan or run contract.
- Infrastructure failures, exclusions, reruns, seeds, code hashes, environment blocks, and deviations must be logged before analysis.
- Producer verification cannot satisfy independent scientific review.

## Critical path and reassessment

1. Preserve the recorded intake authority and policy basis without freezing author metadata.
2. Close or safely reframe the narrow novelty claim through the documented search challenge.
3. Independently verify the stochastic precision, count, seed, and pairing
   amendment; freeze the correlated-domain and deadline contracts separately.
4. Independently review the full result contract and start checklist.
5. Only then may the accountable authority issue a separate `PILOT_FIRST` authorization.
6. After execution, verify provenance, analyze negative and positive findings, and reassess feasibility; no automatic `GO` follows.

## Premortem

Likely failure modes are novelty defeat, leakage from exploratory outputs,
underpowered or pseudo-replicated stochastic runs, selective-withholding results
being narratively suppressed, and single-host timing being overstated as
distributed liveness. The cheapest prevention is the present non-executable
contract plus independent review before any run.
"""


def _write_or_check(path: Path, expected: str, check: bool, label: str) -> None:
    if check:
        try:
            actual = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise PilotPlanError(f"cannot read {label}: {exc}") from exc
        if actual != expected:
            raise PilotPlanError(f"{label} is stale: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        _validate(root)
        rows = _rows()
        _write_or_check(root / CONTRACT_PATH, _csv_text(rows), args.check, "pilot run contract")
        _write_or_check(root / PLAN_PATH, _plan_text(rows), args.check, "pilot plan")
    except PilotPlanError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    action = "current" if args.check else "wrote"
    print(f"OK: confirmatory pilot package {action}; execution remains blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
