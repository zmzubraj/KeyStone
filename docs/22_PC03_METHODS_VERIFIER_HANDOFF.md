# KEYSTONE-MPP-F1 PC03 Methods Verifier Handoff

Status: `PREPARED_FOR_QUALIFIED_EXTERNAL_METHODS_REVIEW`

> Developmental methods-review handoff only. This packet does not certify the design, authorize execution, promote the research phase, establish novelty, or substitute for an authenticated independently signed verification event.

Author metadata is deferred and intentionally excluded from this packet.

## Frozen review boundary

Review the result-blind minimum synthetic design only. Independent synthetic scenario draws are the Monte Carlo sampling units for the frozen model-probability estimands; 32 primary seed blocks and four ordered reserve blocks are execution, dispersion, and reproducibility units. Each included cell schedules 131,072 primary draws against a distribution-free requirement of 73,778 draws.

Included result IDs: `RID-C003-IID-001`, `RID-C003-STRAT-001`, and `RID-C003-SW-001`.

Excluded boundaries:

- `RID-C003-CORR-001`: `EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE`
- `RID-C003-DEADLINE-001`: `EXCLUDED_PENDING_ENVIRONMENT_PROFILE`

Existing exploratory outcomes may be inspected only for contamination and denominator-risk detection. They may not set, repair, or justify the prospective thresholds.

## Canonical state

- status: `ACTIVE`
- phase: `INTAKE`
- novelty: `UNRESOLVED`
- feasibility: `UNASSESSED`
- solution viability: `ASSERTED_ONLY`
- acceptance readiness: `NOT_ASSESSABLE`
- accepted independent methods verification events on canonical review paths: `0`

## Required reviewer determinations

Return `PASS`, `PARTIAL`, `FAIL`, or `UNKNOWN` for every item, with direct artifact locations, recomputation or code evidence, consequence, and the smallest adequate correction:

1. Does the sampling-unit definition match the actual simulator semantics, without treating a seed-run aggregate as a Bernoulli observation?
2. Are scenario draws independent under the frozen generator, and are blockwise estimates sufficient to expose implementation-level dependence or drift?
3. For `RID-C003-STRAT-001`, does the implementation create true common-random-number matched policy pairs with identical latent scenarios and no unpaired substitution?
4. For `RID-C003-SW-001`, are audit-pass and dispute-success outcomes evaluated within the same synthetic draw, with the signed gap direction fixed before execution?
5. Recompute both Hoeffding requirements of 73,778 and confirm that 32 x 4,096 = 131,072 valid primary draws exceeds them under the stated bounded outcomes.
6. Are all 108 seed-schedule rows unique and deterministic, with exactly 32 primary and four reserve streams for each included result ID?
7. Does the reserve rule replace only documented infrastructure failures and prohibit replacement of valid unfavorable blocks?
8. Is one primary cell per included family sufficient for the frozen minimum claim, with optional secondary tests correctly confined to Holm control?
9. Are CORR and DEADLINE correctly excluded, and is every existing correlated/deadline display prevented from becoming confirmatory evidence?
10. Are missingness, invalid-run, deviation, stopping, negative-result retention, and exploratory-quarantine rules complete and operationally testable?
11. Could any existing exploratory value, figure, or code default have contaminated the chosen cells, precision targets, or decision rules?
12. Does the pilot run contract reproduce the same included/excluded boundaries without introducing a stronger claim or execution authorization?

Any critical `FAIL` or `UNKNOWN` leaves PC03 unverified and execution blocked. `PARTIAL` must identify the exact claim ceiling and remediation. No aggregate score or majority vote can compensate for a critical defect.

## Transfer and execution gate

This packet must not be transferred until `REM-001` is recorded through the canonical independent-INTAKE workflow, `REM-002` remains confined to the bounded novelty `REFRAME` lane, and the accountable human names the reviewer and disclosure boundary for this exact packet.

A methods-review `ACCEPT_AS_DRAFT` disposition does not authorize confirmatory execution. `REM-003` closes only after the signed return is recorded and a separate accountable start decision preserves the same included and excluded result-family boundary.

## Hash-bound review inventory

| Artifact | Registry status | Revision | SHA-256 |
| --- | --- | ---: | --- |
| `research-case/03-design/protocol.md` | `DRAFT` | `2` | `4ab6e396a75a6c5cab6290de681b7c3ba8de468606a591a19ee951ae6963efc3` |
| `research-case/03-design/analysis-plan.md` | `DRAFT` | `3` | `ef2c05bff11d9c7aca886737d342eaa77f5c9f26096869e9b9eba9bfb313c1ef` |
| `research-case/03-design/power-or-precision.md` | `DRAFT` | `4` | `dfb678063d914134d78950620654d8907c84784f612bc529cd53a6518886bde5` |
| `research-case/03-design/preregistration-and-deviations.md` | `DRAFT` | `4` | `b82ac6378281ce132bf8ae763128e83af02d7267f38216bbcfd1f475ccc0c71d` |
| `research-case/03-design/pc03-prospective-amendment.md` | `AUXILIARY_HASH_BOUND_INPUT` | `N/A` | `fa92cf52c7db2bb4377bb6b94303b086ca1ec37d372b8bf9af1a23b4c47e82e0` |
| `research-case/03-design/pc03-prospective-counts.csv` | `AUXILIARY_HASH_BOUND_INPUT` | `N/A` | `840db07ed3f228662625beeac1d42d74cfb78dc85610f2b9ddd4a05c2f8d5a2b` |
| `research-case/03-design/pc03-seed-schedule.csv` | `AUXILIARY_HASH_BOUND_INPUT` | `N/A` | `7063adc013979905e0e296f4ace7daa5dde2053c3f78c080c586f567ac18954a` |
| `research-case/03-design/pc03-independent-methods-challenge/design-assessment.md` | `AUXILIARY_HASH_BOUND_INPUT` | `N/A` | `e2759aefb89dd6e082b7db10cd8a85b75df759e91309d83e975bf85eaa5ab9f8` |
| `research-case/03-design/pc03-independent-methods-challenge/prospective-counts.csv` | `AUXILIARY_HASH_BOUND_INPUT` | `N/A` | `f04946b030306e376745e938dea9f1ddd11e0df6cbddbeaf54368ecb138c75e0` |
| `research-case/03-design/pc03-independent-methods-challenge/calculation-notes.md` | `AUXILIARY_HASH_BOUND_INPUT` | `N/A` | `365f620a5e166d429b6b805de5404e7e67cae4db361a16e6a4e880c632434696` |
| `research-case/02-feasibility/pilot-plan.md` | `DRAFT` | `3` | `907d9c6f954daa44216b5ee83f56bd42a7c990c2fd8d0dccaacf1f5a7e134b8a` |
| `research-case/02-feasibility/pilot-run-contract.csv` | `AUXILIARY_HASH_BOUND_INPUT` | `N/A` | `918dacfae714329d9b37a174421ee02806f3c06a2777b09de07f59c40627db95` |
| `prototype/src/keystone/simulation.py` | `AUXILIARY_HASH_BOUND_INPUT` | `N/A` | `61662f7c144723aeaa9b75e3f6c51991f9b8006543d68f801b47be1d4254ff77` |
| `prototype/scripts/run_experiments.py` | `AUXILIARY_HASH_BOUND_INPUT` | `N/A` | `4488593cba625e3732c1cd3e6633f21b284142967795a1056051b7c10eef8424` |
| `prototype/configs/baseline.json` | `AUXILIARY_HASH_BOUND_INPUT` | `N/A` | `ceef72707f92f3b5a17a7343339222114e92110b145f9db3f7ff5b17a4631c59` |

## Required signed return

A decision-bearing return must include reviewer identity, verifier registry ID, signing key ID, conflict disclosure, independence basis, competence basis in statistical simulation or experimental methods, every question disposition, reviewed path/revision/SHA-256, calculations or code evidence, residual risks, and one overall disposition: `ACCEPT_AS_DRAFT`, `REVISE`, or `STOP`.

The reviewer must sign current canonical artifact revisions through the schema-v4 verifier workflow. A same-host AI review, unsigned email, prose endorsement, or possession of a public key is developmental evidence only. If upstream novelty or claim semantics later change, affected methods verification becomes stale and must be repeated.

Local packet generation does not authorize external transfer. The accountable human must approve transfer to a named reviewer and confirm the disclosure boundary. Review acceptance does not authorize confirmatory execution; a separate accountable start decision remains mandatory.
