# KEYSTONE Deadline Pilot Start Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, fail-closed preauthorization package that specifies the `RID-C003-DEADLINE-001` pilot inputs, the four T5 mechanism-isolation ablations, and an independent-reproduction handoff without executing a confirmatory run or promoting any scientific gate.

**Architecture:** One Python exporter reads the frozen design and governance sources, validates their scientific boundaries, and emits editable CSV/Markdown artifacts plus a hash-bound manifest. A focused pytest module drives the exporter test-first and proves that unresolved numeric or environment choices prevent execution readiness. The package remains `DRAFT_PREAUTHORIZATION`, while integration updates only the draft feasibility/risk wording and provenance inventories.

**Tech Stack:** Python 3 standard library, pytest, CSV, Markdown, JSON, SHA-256, existing KEYSTONE integrity scripts.

---

## File map and ownership

- Create `scripts/export_deadline_pilot_start_package.py`: sole generator and validator for the package.
- Create `prototype/tests/test_deadline_pilot_start_package.py`: behavior, schema, determinism, tamper, and fail-closed tests.
- Generate `research-case/03-design/deadline-environment-profiles.csv`: exact environment-field registry with unresolved values represented by the literal `UNRESOLVED_BEFORE_EXECUTION`.
- Generate `research-case/03-design/t5-ablation-run-matrix.csv`: four design-only treatment/control rows for canary, stratification, failure-domain, and temporal-dependence mechanisms.
- Generate `research-case/03-design/deadline-pilot-execution-contract.md`: unit, endpoints, blocking factors, telemetry, stopping rules, forbidden inputs, and no-execution boundary.
- Generate `research-case/03-design/independent-reproduction-handoff.md`: clean-machine commands, expected mechanical evidence, confidentiality boundary, and return contract.
- Generate `research-case/03-design/deadline-pilot-start-package-manifest.json` and `.sha256`: complete input/content-output hashes and package-level boundary. The manifest and its sidecar are integrity artifacts, not self-hashed content outputs; the sidecar alone records the final manifest SHA-256 so the package makes no impossible self-referential hash claim.
- Modify `research-case/02-feasibility/feasibility-report.md`: acknowledge the confirmed draft/design authority while keeping the overall disposition `BLOCKED` because novelty, result-blind numeric freeze, and independent scientific verification remain open.
- Modify `research-case/02-feasibility/risk-register.csv`: narrow R001 to verified draft/design authority only; do not imply final authorship, institutional approval, scientific verification, or submission authority.
- Modify `research-case/03-design/preregistration-and-deviations.md`: bind the generated package as a preauthorization design artifact and preserve unresolved numerical choices.
- Modify `research-case/07-manuscript/source-manifest.json`, `PACKAGE_MANIFEST.md`, and `SHA256SUMS`: integration owner only, after reviews.

## Frozen package contract

The exporter must enforce these exact package-wide values:

- `schema_id = KEYSTONE_DEADLINE_PILOT_START_PACKAGE`
- `schema_version = 1`
- `status = DRAFT_PREAUTHORIZATION`
- `execution_authorization = NOT_AUTHORIZED`
- `canonical_phase = INTAKE`
- `scientific_evidence_boundary = DESIGN_ONLY_NOT_CONFIRMATORY_EVIDENCE`
- `result_id = RID-C003-DEADLINE-001`
- `claim_ids = C002|C003`
- `author_metadata_freeze = DEFERRED_BY_ACCOUNTABLE_HUMAN`

The environment CSV must use the exact header:

```text
profile_id,profile_role,process_count,failure_domain_count,host_topology,run_day_block,network_latency_profile,packet_loss_profile,crash_profile,synchrony_assumption,deadline_interpretation,trace_denominator,precision_target,multiplicity_rule,execution_status,result_id,claim_ids,source_path,claim_ceiling
```

It must contain exactly these profile IDs:

- `ENV-DEADLINE-CONTROL-001`: non-adversarial control.
- `ENV-DEADLINE-LATENCY-001`: controlled latency injection.
- `ENV-DEADLINE-LOSS-001`: controlled packet-loss injection.
- `ENV-DEADLINE-CRASH-001`: controlled crash injection.

Every profile must set `process_count=32`, `failure_domain_count=4`, `execution_status=BLOCKED_UNRESOLVED_DESIGN`, and unresolved execution choices to `UNRESOLVED_BEFORE_EXECUTION`. No row may contain a numeric deadline, latency, loss, crash rate, replicate count, precision target, or alpha rule.

The ablation CSV must use the exact header:

```text
ablation_id,treatment,control,mechanism_question,paired_seed_policy,blocking_factors,required_endpoint,execution_status,result_id,claim_ids,source_path,claim_ceiling
```

It must contain exactly:

- `ABL-CANARY-001`: canary readiness audit versus no canary readiness audit.
- `ABL-STRAT-001`: fixed-quota stratified sampling versus uniform sampling.
- `ABL-DOMAIN-001`: failure-domain-aware analysis versus domain labels removed.
- `ABL-TEMPORAL-001`: Markov temporal dependence versus static IID availability.

All rows must remain `DESIGN_ONLY_NOT_EXECUTED`. The first row maps to `RID-C003-DEADLINE-001`; the remaining rows map only to already reserved C003 result families and may not create a new confirmatory result ID silently.

The execution contract must state that a replicate is one complete end-to-end distributed trace per seed and environment profile; events inside a trace are not replicates. It must require seed, profile, topology, run day, version/commit, timestamps, outcome, failure classification, and artifact hashes. It must prohibit production ciphertext, live secrets, personal data, production systems, unpublished third-party data, external sharing, and performance inspection before design freeze. It must permit only integrity/completeness checks before authorization.

The reproduction handoff must require a clean checkout or isolated copy, read-only authoritative inputs, no network for the mechanical rerun unless separately authorized, `python scripts/export_deadline_pilot_start_package.py --check`, the focused pytest, the full Python suite, Foundry tests, T1-T8 check, source-manifest check, checksum check, and a returned manifest/report with commands, tool versions, hashes, deviations, and residual risks. It must say that same-author rerun is not independent scientific verification and that sending the bundle externally requires accountable human approval.

## Task 1: RED tests for package semantics

**Files:**
- Create: `prototype/tests/test_deadline_pilot_start_package.py`

- [ ] Write an import fixture for `scripts/export_deadline_pilot_start_package.py` and a test asserting the exact package constants, four environment IDs, four ablation IDs, headers, and claim/result mappings.
- [ ] Add a test that rejects any generated environment row containing a resolved numeric deadline, latency, loss, crash rate, replicate count, precision target, or multiplicity rule.
- [ ] Add a test that asserts every profile is `BLOCKED_UNRESOLVED_DESIGN`, every ablation is `DESIGN_ONLY_NOT_EXECUTED`, and no package text contains `GO`, `CONFIRMATORY_EVIDENCE`, `FEASIBILITY_GATE`, or `STUDY_DESIGN` as a promoted state.
- [ ] Run `python -m pytest prototype/tests/test_deadline_pilot_start_package.py -q` and record the expected failure because the exporter does not exist.

## Task 2: GREEN minimal exporter and generated package

**Files:**
- Create: `scripts/export_deadline_pilot_start_package.py`
- Generate: all seven `research-case/03-design/deadline-*` and `t5-*` package outputs listed above.

- [ ] Implement dataclasses or immutable row constants for the two CSVs; validate exact headers, exact row IDs, non-empty provenance fields, and allowed status values.
- [ ] Validate canonical source boundaries before generation: `program-state.json` must remain `INTAKE` with novelty `UNRESOLVED`, feasibility `UNASSESSED`, viability `ASSERTED_ONLY`, and acceptance `NOT_ASSESSABLE`; authority confirmation must preserve the deferred author-metadata freeze; protocol and power files must contain `RID-C003-DEADLINE-001` and unresolved prospective targets.
- [ ] Implement deterministic Markdown renderers for the execution contract and reproduction handoff using only frozen language in this plan.
- [ ] Implement a sorted JSON manifest containing every input and four content-output relative paths and SHA-256, plus the package-wide constants and an unhashed `integrity_artifacts` inventory naming the manifest and sidecar. The sidecar records the final manifest SHA-256; neither integrity artifact may claim its own SHA-256 inside the manifest.
- [ ] Implement `--write` as the default and `--check` as regeneration-to-temporary-directory plus byte comparison, complete inventory validation, and sidecar validation.
- [ ] Run the focused pytest and confirm it passes.

## Task 3: RED/GREEN tamper and fail-closed checks

**Files:**
- Modify: `prototype/tests/test_deadline_pilot_start_package.py`
- Modify: `scripts/export_deadline_pilot_start_package.py`

- [ ] Add a RED test that tampers with one CSV while rebinding the manifest and sidecar, and require `--check` to fail from regenerated expected bytes.
- [ ] Add a RED test that removes one manifest input/output row and require explicit inventory-drift errors.
- [ ] Add a RED test that mutates copied `program-state.json` to a promoted phase or resolved novelty and require a boundary error rather than a regenerated package.
- [ ] Add a RED test that changes `UNRESOLVED_BEFORE_EXECUTION` to a numeric value and require schema rejection.
- [ ] Implement the minimal validations, rerun the focused test file, then run `python scripts/export_deadline_pilot_start_package.py --check`.

## Task 4: Draft governance/design alignment

**Files:**
- Modify: `research-case/02-feasibility/feasibility-report.md`
- Modify: `research-case/02-feasibility/risk-register.csv`
- Modify: `research-case/03-design/preregistration-and-deviations.md`

- [ ] Replace only the stale draft/design-authority blocker language with the direct accountable-human confirmation and no-conflict policy basis.
- [ ] State explicitly that final author order, corresponding author, affiliation wording, institutional endorsement, external sharing, submission, and scientific verification remain deferred or separately gated.
- [ ] Keep the report decision `BLOCKED`, G-02 and G-03 blocking, G-04 and G-06 at risk, and canonical state unchanged.
- [ ] Bind the generated package as design-only and state that execution remains prohibited until the environment profile, deadline interpretation, trace denominator, precision target, multiplicity rule, novelty gate, and required approval are prospectively resolved.

## Task 5: Independent reviews

**Files:** read-only review of all Task 1-4 files.

- [ ] Dispatch a fresh read-only specification reviewer and require exactly `SPEC_APPROVED` or a numbered defect list.
- [ ] Resolve any defect through the implementer and rerun focused checks.
- [ ] Dispatch a different fresh read-only quality reviewer and require exactly `QUALITY_APPROVED` or a numbered defect list.
- [ ] Do not accept a review that edits files, runs integrity refreshers, or changes canonical state.

## Task 6: Integration and full verification

**Files:**
- Modify: `research-case/07-manuscript/source-manifest.json`
- Modify: `PACKAGE_MANIFEST.md`
- Modify: `SHA256SUMS`

- [ ] Add the exporter, focused tests, plan, generated package, and aligned draft feasibility/design sources to the manuscript source manifest without upgrading their evidence maturity.
- [ ] Refresh package inventory and checksums only after review approval.
- [ ] Run focused pytest, full Python pytest, Foundry tests, gas snapshot checks, T1-T8 `--check`, deadline-package `--check`, strict research-case validation at `INTAKE`, source-manifest verification, citation verification, checksum verification, and `git diff --check`.
- [ ] Report the lowest defensible outcome as continued `BLOCKED` at `INTAKE` with a completed design-start package; do not call the MPP confirmatory-ready, publication-ready, or independently reproduced.

## Self-review result

- Spec coverage: deadline profile schema, T5 ablations, reproduction handoff, governance boundary, tamper resistance, and integration QA are each owned by a task.
- Placeholder scan: no implementation placeholder is used; `UNRESOLVED_BEFORE_EXECUTION` is an intentional fail-closed scientific value and execution blocker.
- Type consistency: package constants, row IDs, statuses, and result/claim mappings are identical across the file map, frozen contract, tests, and integration steps.
- Commit policy: no commit step is included because this workspace already contains extensive user-owned uncommitted changes; all edits must preserve and integrate those changes without staging or committing them.
