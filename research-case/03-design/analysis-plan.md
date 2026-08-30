# KEYSTONE analysis plan

Status: `DRAFT / PRE-AUTHORIZATION`
System: `KEYSTONE-MPP-F1`
Date: `2026-08-29`
Current canonical phase: `INTAKE`

This analysis plan is frozen before any new confirmatory rerun. It does not set
numeric success thresholds from observed outputs and does not authorize
execution.

## Estimands

Primary estimands:

| Estimand ID | Definition | Linked result IDs | Claims |
| --- | --- | --- | --- |
| `EST-01` | existence of at least one valid counterexample class where ciphertext or receipt availability holds while present dispute-key readiness fails | `RID-C001-SEP-001` | `C001` |
| `EST-02` | exact one-audit catastrophic false-accept probability and its complement detection probability under the frozen static ready-set semantics | `RID-C001-STATIC-001` | `C001`, `C003` |
| `EST-03` | deterministic correctness obligation that every named threshold-KEM and transcript boundary case passes or fails exactly as specified: `t` valid partials open, `t-1` fail, malformed or wrong-context proofs are rejected, stale contexts fail, and routine audits avoid production ciphertext | `RID-C002-CRYPTO-001` | `C002`, `C003` |
| `EST-04` | deterministic contract-evidence obligation that every named bulletin-board lifecycle case preserves the required auditable state transition, including missing, invalid, and equivocation evidence paths | `RID-C002-CONTRACT-001` | `C002` |
| `EST-05` | reconstructability probability and audit-pass probability under prespecified IID unavailability scenarios | `RID-C003-IID-001` | `C003` |
| `EST-06` | reconstructability probability and audit-pass probability under prespecified correlated-domain outage scenarios | `RID-C003-CORR-001` | `C003` |
| `EST-07` | paired policy difference between fixed-quota stratified sampling and uniform sampling under matched total draws and matched catastrophic semantics | `RID-C003-STRAT-001` | `C003` |
| `EST-08` | negative-result gap between routine audit pass and targeted dispute success under selective withholding | `RID-C003-SW-001` | `C003` |
| `EST-09` | conditional deadline success probability for the synthetic distributed benchmark under declared synchrony assumptions | `RID-C003-DEADLINE-001` | `C003` |

Result-ID closure and denominator contract:

| Estimand ID | Result ID | Independent replicate | Unit-level denominator | Pairing or blocking |
| --- | --- | --- | --- | --- |
| `EST-01` | `RID-C001-SEP-001` | one preserved counterexample class | count of preserved counterexample classes examined under the frozen model family | blocked by theorem revision and code revision |
| `EST-02` | `RID-C001-STATIC-001` | one frozen parameter cell | count of exact parameter cells under one stated semantics | blocked by parameter cell and model semantics |
| `EST-03` | `RID-C002-CRYPTO-001` | one named correctness case | count of required deterministic correctness cases | blocked by code revision, transcript version, and seed batch |
| `EST-04` | `RID-C002-CONTRACT-001` | one named complete contract lifecycle case | count of required deterministic lifecycle cases | blocked by contract revision, toolchain version, and seed batch |
| `EST-05` | `RID-C003-IID-001` | one prespecified seed block containing 4,096 independent synthetic model draws | 131,072 draws and 32 blockwise estimates per IID cell | blocked by scenario family, config revision, runtime, and seed block |
| `EST-06` | `RID-C003-CORR-001` | not frozen | not frozen | `EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE`; requires a truthful domain-label source, valid comparator, and new prospective amendment |
| `EST-07` | `RID-C003-STRAT-001` | one prespecified seed block containing 4,096 common-random-number policy pairs | 131,072 paired draws and 32 blockwise paired estimates per sample-size cell | paired within draw and block; blocked by draw semantics and scenario cell |
| `EST-08` | `RID-C003-SW-001` | one prespecified seed block containing 4,096 draws with both audit and dispute outcomes | 131,072 paired draws and 32 blockwise gap estimates per adversary cell | paired within draw and block; blocked by adversary configuration, config revision, runtime, and seed block |
| `EST-09` | `RID-C003-DEADLINE-001` | one complete distributed trace under one seed and environment profile | count of trace-level runs per environment profile | blocked by environment profile, host topology, run day, and seed block |

Robustness estimands:

- sensitivity of `EST-02`, `EST-05`, `EST-06`, `EST-07`, and `EST-08` to
  placement policy, outage family, and draw semantics;
- stability of deterministic correctness conclusions for `EST-03` and
  `EST-04` across code revision, runtime, transcript version, and toolchain
  blocks;
- divergence between single-host resource measurements and the stochastic
  deadline trace family in `EST-09`.

Exploratory-only estimands:

- temporal dependence, adaptive schedule behavior, or additional baselines not
  frozen by this plan;
- any deployment-level or field-like operational claim.

## Primary analysis

Primary analysis rules by estimand:

| Estimand ID | Estimator or test | Reported uncertainty | Claim-safe interpretation limit |
| --- | --- | --- | --- |
| `EST-01` | constructive existence check from a preserved counterexample class | none beyond explicit assumptions and scope qualifiers | proves only separation under the stated model, not operational prevalence |
| `EST-02` | exact combinatorial calculation; if mirrored by simulation, simulation is validation not replacement | none for the exact calculation; any simulation cross-check gets a confidence interval | static catastrophic semantics only; never converted into a time-evolving claim |
| `EST-03` | zero-tolerance deterministic correctness checklist over the full named case set; every required case must match its expected pass or fail outcome | none; any failure is dispositive for the affected claim boundary | prototype-scope correctness only; not production assurance |
| `EST-04` | zero-tolerance deterministic lifecycle checklist over the full named contract case set; every required case must preserve the expected evidence state transition | none; any failure is dispositive for the affected contract-boundary wording | contract-boundary behavior only; not an independent security audit |
| `EST-05` | empirical IID model-draw proportions plus 32 blockwise estimates per cell | simultaneous family-wise Hoeffding absolute-error bound at 0.005, Wilson intervals as descriptive support, exact zero-event upper bound | IID synthetic model family only |
| `EST-06` | no confirmatory estimator or test while excluded | not applicable until a new prospective amendment freezes the source, comparator, denominator, and precision rule | existing correlated-domain outputs are exploratory only and cannot support a confirmatory claim |
| `EST-07` | matched-draw difference between sampling policies plus 32 blockwise paired estimates | simultaneous family-wise range-two Hoeffding absolute-error bound at 0.01; no unpaired substitution | matched synthetic semantics only; no extrapolation to other samplers |
| `EST-08` | within-draw audit-pass minus dispute-success gap plus 32 blockwise gap estimates | simultaneous family-wise range-two Hoeffding absolute-error bound at 0.01; component intervals are descriptive | limitation surface only; not a success endpoint |
| `EST-09` | trace-level success proportion over independent benchmark traces | confidence interval method to be frozen in `power-or-precision.md`; Wilson interval is the default if no better design-specific rule is later justified | conditional synchrony wording only; not unconditional future availability |

For stochastic binary endpoints, the estimator is the empirical proportion over
the prespecified independent synthetic model draws, with seed blocks retained as
execution and reproducibility units. Simultaneous family-wise Hoeffding bounds
are primary; two-sided Wilson intervals for individual binary components are
descriptive and cannot replace the simultaneous contract.

Deterministic correctness rules for `EST-03` and `EST-04`:

- these are not population-proportion estimands and are not eligible for
  pseudo-binomial sizing;
- the denominator is the prespecified named case set, not the number of
  assertions inside a test, the number of transcript fields, or the number of
  internal function calls;
- success requires zero deviations from the expected pass or fail outcome across
  the full case set for the relevant code and toolchain block;
- if later stochastic robustness runs are desired for protocol or contract
  reliability, they require a new result ID and a new preregistered sampling
  frame rather than relabeling `EST-03` or `EST-04`.

For rare-event or zero-event cells:

- if no event is observed, report the point estimate and a valid upper interval
  bound;
- zero-event outputs may not be described as impossibility proofs;
- if the expected event is so rare that the required precision cannot be met,
  the conclusion is "insufficient precision" rather than success.

For paired policy comparisons such as uniform versus stratified:

- use matched seeds where the simulator semantics permit;
- report the paired difference in the target metric and its uncertainty;
- interpret only the prespecified comparison, not every within-family subplot.

For selective withholding:

- the negative-result estimand is the gap between audit pass and dispute
  success, not either number alone;
- any non-zero gap is retained as a limitation signal even if other endpoints
  look favorable.

For contract-evidence obligations:

- the named lifecycle case set must include at least success, missing-response,
  invalid-response, and equivocation paths;
- each case is analyzed as one complete lifecycle trace from request opening to
  final evidence state, not as separate independent bitmap flips or events.

## Multiplicity

Multiplicity strategy:

- no omnibus claim is allowed to borrow strength from unrelated endpoint
  families;
- each charter claim uses its own required evidence bundle;
- the three scheduled stochastic families each contain one primary cell, so no
  within-family primary multiplicity adjustment is required; any optional
  secondary hypothesis tests use Holm control within that prespecified family;
- robustness and exploratory endpoints do not upgrade a primary claim if the
  primary endpoint fails.

Anti-inflation rules:

- repeated looks at accumulating runs do not create new inferential chances
  unless a later valid sequential rule is frozen;
- multiple scenario rows under one figure do not justify independent claim
  upgrades unless the analysis plan names them as separate confirmatory tests;
- analytic and simulation outputs for the same estimand do not count as two
  independent successes;
- deterministic pass-fail obligations `EST-03` and `EST-04` do not enter a
  multiplicity pool with stochastic scenario families because they are boundary
  checks rather than sampled efficacy tests.

## Missing data

Missing or failed-run handling:

- no silent imputation for failed prototype, contract, or benchmark runs;
- a run with missing essential telemetry, missing seed provenance, or broken
  environment capture is marked invalid for the primary endpoint and kept in the
  run ledger;
- a failed primary block remains in the deviation ledger and may be replaced only
  by the next unused predeclared reserve block; a valid unfavorable block is never
  replaceable;
- if four reserve blocks are exhausted before 32 valid primary-equivalent blocks
  exist, the cell remains incomplete and is counted against feasibility;
- partial benchmark traces are not converted into complete successes by nodewise
  averaging.

Predeclared exclusions:

- wrong code revision or untracked local modification relative to the frozen
  manifest;
- seed or configuration mismatch with the preregistered manifest;
- explicit execution outside the frozen synthetic/non-production boundary.

Not valid exclusions:

- unfavorable outcome direction;
- slower-than-expected timing;
- contradicting the narrative preference;
- revealing the selective-withholding limitation.

## Sensitivity

Required sensitivity analyses:

- keep any IID-versus-correlated comparison exploratory until a truthful
  domain-label source, valid comparator, and new prospective amendment exist;
- compare uniform and fixed-quota stratified sampling under matched total draws
  and matched catastrophic semantics;
- defer placement-cap concentration stress to the excluded correlated-domain
  family or a separately preregistered exploratory result ID;
- preserve the selective-withholding negative result under the frozen adversary
  configuration;
- for deadline traces, vary only prespecified environment profiles recorded in
  the future benchmark manifest.

Sensitivity guardrails:

- no new sensitivity axis may be added after seeing confirmatory outcomes unless
  labeled exploratory with a new result ID;
- if a sensitivity result reverses a primary direction, the manuscript claim is
  narrowed to the weakest surviving scope;
- static and temporal or deadline semantics remain distinct even if their plots
  look visually similar.

## Exploratory boundary

Exploratory outputs are allowed only if quarantined from confirmatory claims.

Exploratory-only categories:

- temporal Markov or other dynamic-availability models not frozen by a later
  amendment;
- adaptive audit schedules or escalation policies;
- added committee sizes, draw counts, or network profiles not present in the
  frozen manifest;
- post-hoc regressions, subgrouping, or visualization-driven hypotheses.

Quarantine rules:

- exploratory outputs must use distinct result IDs and be labeled exploratory in
  tables, figures, and manuscript prose;
- exploratory findings may motivate redesign or future work but cannot satisfy a
  blocked feasibility, novelty, or confirmatory-evidence gate by themselves;
- if an exploratory output reveals a fatal contradiction, the contradiction
  still blocks the corresponding claim.
