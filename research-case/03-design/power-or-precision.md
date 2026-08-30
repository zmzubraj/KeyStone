# KEYSTONE power or precision rationale

Status: `DRAFT / PRE-AUTHORIZATION`
System: `KEYSTONE-MPP-F1`
Date: `2026-08-29`
Current canonical phase: `INTAKE`
Upstream blockers preserved: `NOVELTY_UNRESOLVED`, `feasibility_decision=UNASSESSED`

This file is a result-blind planning artifact. It does not authorize execution,
does not issue `GO`, does not set an operational deadline target from existing
outputs, and does not change `research-case/program-state.json`.
It does not freeze final confirmatory sample sizes, exact half-width targets,
zero-event upper-bound targets, paired discordance caps, or within-family
adjusted alpha rules. Design or power freeze remains `BLOCKED` until an
accountable, prospective amendment adds those bases here and in
`research-case/03-design/preregistration-and-deviations.md`.

## Target

All nine reserved result IDs are classified here so deterministic obligations do
not receive pseudo-power calculations and stochastic families do not treat
within-run events as independent replicates.

| Result ID | Class | Independent replicate | Unit-level denominator | Planning target |
| --- | --- | --- | --- | --- |
| `RID-C001-SEP-001` | deterministic obligation | one preserved counterexample class | count of preserved counterexample classes under the frozen model family | preserve at least one valid witness per stated theorem or model variant; no sample-size solver |
| `RID-C001-STATIC-001` | analytic calculation | one frozen parameter cell | count of exact parameter cells under one semantics | exact calculation with model-faithful reproduction; no stochastic power target |
| `RID-C002-CRYPTO-001` | deterministic obligation | one named correctness case | count of required threshold, invalid-partial, stale-context, replay, and ciphertext-boundary cases | exhaustive zero-tolerance case coverage; no pseudo-binomial power |
| `RID-C002-CONTRACT-001` | deterministic obligation | one named complete lifecycle case | count of required success, missing, invalid, and equivocation lifecycle cases | exhaustive zero-tolerance case coverage; no pseudo-binomial power |
| `RID-C003-IID-001` | stochastic scenario family | one complete seed-level scenario run per config cell | count of valid seed-level runs per IID cell | precision of binary scenario proportions plus rare-event upper-bound assurance |
| `RID-C003-CORR-001` | stochastic scenario family | one complete seed-level scenario run per config and placement cell | count of valid seed-level runs per correlated cell | precision of binary scenario proportions per placement cell plus rare-event upper-bound assurance |
| `RID-C003-STRAT-001` | paired comparison | one matched seed pair spanning both policies under one semantic cell | count of matched seed pairs per semantic cell | precision of the paired policy difference, parameterized by discordance |
| `RID-C003-SW-001` | paired comparison | one complete adversary scenario run containing both audit-pass and dispute-success outcomes | count of valid seed-level paired runs per adversary cell | precision of the within-run negative-result gap plus optional component-wise interval reporting |
| `RID-C003-DEADLINE-001` | distributed-trace benchmark | one complete end-to-end distributed trace per seed and environment profile | count of valid trace-level runs per environment profile | precision of conditional deadline success proportion and zero-failure upper-bound assurance; no operational SLA target yet |

## Assumptions

- Existing exploratory pass rates, timings, gas values, and favorable plots were
  not used to choose thresholds here.
- The default family for precision statements is two-sided 95 percent coverage
  with `alpha = 0.05`, giving `z_(1-alpha/2) = 1.9599639845`.
- Multiplicity sensitivity is illustrated here by tightening the
  per-comparison alpha inside one prose claim family:
  - `alpha = 0.025` for two protected comparisons gives `z = 2.2414027276`;
  - `alpha = 0.0166666667` for three protected comparisons gives `z = 2.3939797991`.
  These are non-binding sensitivity examples only, not the frozen
  within-family adjusted-alpha rule for confirmatory execution.
- For unpaired binary stochastic families, the reporting interval is the Wilson
  score interval and the planning envelope uses the conservative worst-case
  variance at `p = 0.5`:
  - `n >= ceil(z^2 * 0.25 / h^2)`,
  where `h` is the target half-width.
- For paired differences, let
  - `D_i = I(policy_or_audit_success_a) - I(policy_or_dispute_success_b)`,
  so `D_i` is in `{-1, 0, 1}` and the paired mean estimates the target gap.
  With `q = P(D_i != 0)` as the discordance fraction, `Var(D_i) <= q`, so a
  conservative precision envelope is
  - `n >= ceil(z^2 * q / h^2)`.
  Because `q` is not yet justified from an accountable decision target, this
  artifact keeps `q` explicit and reports a sensitivity table rather than one
  fixed pair count.
- For zero-observed-event assurance, the relevant logic is not efficacy power.
  If `x = 0` failures are observed in `n` independent runs, the one-sided upper
  bound `u` on the true failure probability solves
  - `(1 - u)^n = alpha`,
  so
  - `n >= ceil(log(alpha) / log(1 - u_target))`.
- `RID-C003-IID-001`, `RID-C003-CORR-001`, and `RID-C003-DEADLINE-001` may use
  the closed-form precision envelopes directly because the estimands are
  seed-level or trace-level binary proportions. `RID-C003-STRAT-001` and
  `RID-C003-SW-001` require paired-gap planning rather than unpaired formulas.
- If a later design-amendment needs model-specific operating-characteristic
  checks for the deadline benchmark or a more complex paired estimator, use a
  simulation-based planner with at least `5000` Monte Carlo replicates per
  candidate `n` and report the Monte Carlo Wilson interval on estimated
  power or coverage. Near `0.80`, `5000` replicates imply about `+/- 0.011`
  Monte Carlo uncertainty.
- Seed-level runs are independent only within one blocked cell. Events inside a
  single trajectory, contract lifecycle, or distributed trace are not separate
  replicates and must not inflate the denominator.

## Calculation

Closed-form precision envelopes used here:

1. Unpaired binary proportions:
   `n >= ceil(z^2 * 0.25 / h^2)`.
2. Paired gap precision:
   `n >= ceil(z^2 * q / h^2)`.
3. Zero-failure upper-bound assurance:
   `n >= ceil(log(alpha) / log(1 - u_target))`.

Illustrative unpaired precision envelope per config or environment cell only:

| Two-sided alpha | z value | `h = 0.10` | `h = 0.075` | `h = 0.05` |
| --- | ---: | ---: | ---: | ---: |
| `0.05` | `1.9599639845` | `97` | `171` | `385` |
| `0.025` | `2.2414027276` | `126` | `224` | `503` |
| `0.0166666667` | `2.3939797991` | `144` | `255` | `574` |

These counts apply separately to:

- `RID-C003-IID-001` per IID scenario cell;
- `RID-C003-CORR-001` per correlated placement or outage cell;
- `RID-C003-DEADLINE-001` per environment profile when the endpoint is a trace
  success proportion.

Illustrative zero-failure upper-bound assurance per config or environment cell
at one-sided 95 percent confidence only:

| Target upper bound on unseen failure rate | Required zero-failure runs |
| --- | ---: |
| `< 0.10` | `29` |
| `< 0.05` | `59` |
| `< 0.02` | `149` |
| `< 0.01` | `299` |
| `< 0.005` | `598` |

This logic is relevant when a result family is framed as "no catastrophic
failure was observed" and the manuscript needs an explicit upper bound rather
than an unsupported claim of impossibility.

Illustrative paired-gap precision envelope at two-sided 95 percent coverage
only:

| Discordance cap `q` | `h = 0.10` | `h = 0.075` | `h = 0.05` |
| --- | ---: | ---: | ---: |
| `0.10` | `39` | `69` | `154` |
| `0.20` | `77` | `137` | `308` |
| `0.30` | `116` | `205` | `461` |
| `0.40` | `154` | `274` | `615` |
| `0.50` | `193` | `342` | `769` |

These counts apply to:

- `RID-C003-STRAT-001`, where `D_i` is the matched-seed difference between
  fixed-quota stratified and uniform outcomes;
- `RID-C003-SW-001`, where `D_i` is the within-run gap between routine audit
  pass and targeted dispute success under the same adversary configuration.

Result-specific calculation rule:

| Result ID | Calculation rule | Why this is the correct planning surface |
| --- | --- | --- |
| `RID-C001-SEP-001` | no `n` solver; preserve at least one valid counterexample class per theorem or model variant | existence and reproducibility, not population inference, is the claim-bearing target |
| `RID-C001-STATIC-001` | exact combinatorial or hypergeometric calculation on the frozen parameter cell | the quantity is analytic and deterministic |
| `RID-C002-CRYPTO-001` | exhaustive named-case checklist over the full correctness boundary set | the claim is "all required cases behave exactly as specified", not "most cases succeed" |
| `RID-C002-CONTRACT-001` | exhaustive named-case checklist over the full lifecycle boundary set | auditable contract behavior is a deterministic obligation |
| `RID-C003-IID-001` | Wilson-precision planning on seed-level binary outcomes; optional zero-failure upper-bound check for rare catastrophic misses | each seed-level scenario is one independent Bernoulli trial inside one IID cell |
| `RID-C003-CORR-001` | Wilson-precision planning per correlated placement or outage cell; optional zero-failure upper-bound check for rare catastrophic misses | correlation changes the cell meaning, so cells may not be pooled |
| `RID-C003-STRAT-001` | paired-gap precision planning with explicit discordance `q` sensitivity | matched seeds create paired outcomes, so unpaired formulas would overstate information |
| `RID-C003-SW-001` | paired-gap precision planning on the audit-pass minus dispute-success gap; optional Wilson intervals for the two component proportions as descriptive support | the central estimand is a within-run limitation gap, not two unrelated proportions |
| `RID-C003-DEADLINE-001` | Wilson-precision planning on trace-level success plus zero-failure upper-bound assurance for rare missed-deadline events; simulation-based operating-characteristic check if the estimator becomes more complex | the endpoint is trace-level and bounded by environment profile, not message-level events |

## Decision

Planning consequences are stated without issuing `GO`. The numerical tables in
`## Calculation` are sensitivity examples only. They are not operative green,
amber, or red thresholds until a logged amendment prospectively freezes the
accountable target, the exact replicate and denominator definition for the
affected family, and the within-family multiplicity rule when applicable.

Deterministic and analytic rows:

- `RID-C001-SEP-001` is green only when at least one preserved counterexample
  class exists for every theorem or model variant that carries the separation
  claim. Missing a required class is red.
- `RID-C001-STATIC-001` is green only when the exact calculation and its
  model-faithful reproduction agree on every frozen parameter cell. Any mismatch
  is red.
- `RID-C002-CRYPTO-001` and `RID-C002-CONTRACT-001` are green only when the
  full prespecified named-case set is complete and every required case matches
  its expected pass or fail outcome. Any deviation is red. There is no amber
  "partially powered" state for these deterministic obligations.

Stochastic and paired families:

| Family | Green gate consequence | Amber gate consequence | Red gate consequence |
| --- | --- | --- | --- |
| `RID-C003-IID-001` | an accountable, result-blind precision or assurance target and any within-family multiplicity rule are frozen by logged amendment, the exact count is computed from that frozen target, and the valid seed-level run count meets or exceeds it without invalid pooling | the family still has only sensitivity-envelope guidance from `## Calculation`, or the target, replicate rule, denominator rule, or multiplicity rule remains unresolved | thresholds are retrofitted after outcome inspection, replicate or denominator definitions are underdefined, invalid pooling occurs across blocked cells, or a properly frozen count is not met |
| `RID-C003-CORR-001` | an accountable, result-blind per-cell target and any within-family multiplicity rule are frozen by logged amendment, the exact per-cell count is computed prospectively, and each correlated placement or outage cell meets it without cross-cell pooling | only sensitivity-envelope guidance exists, or the target, per-cell denominator, blocking rule, or multiplicity rule remains unresolved | retrofitted thresholds, underdefined replicate or denominator, invalid pooling across placement or outage cells, or failure to meet a properly frozen per-cell count |
| `RID-C003-STRAT-001` | an accountable, result-blind paired-gap target and justified discordance handling are frozen by logged amendment, the exact matched-pair count is computed prospectively, and the matched-pair run count meets it | only paired sensitivity-envelope examples exist, or the paired target, discordance basis, or multiplicity rule remains unresolved | retrofitted thresholds, unpaired treatment of matched data, underdefined pair denominator, invalid pooling across semantic cells, or failure to meet a properly frozen matched-pair count |
| `RID-C003-SW-001` | an accountable, result-blind paired-gap target and justified discordance handling are frozen by logged amendment, the exact paired-run count is computed prospectively, and the valid paired run count meets it | only paired sensitivity-envelope examples exist, or the paired target, discordance basis, or multiplicity rule remains unresolved | retrofitted thresholds, treating component outcomes as independent unpaired samples, underdefined paired denominator, invalid pooling across adversary cells, or failure to meet a properly frozen paired-run count |
| `RID-C003-DEADLINE-001` | an accountable environment profile, claim-safe deadline target, and any within-family multiplicity rule are frozen by logged amendment, the exact per-profile count is computed prospectively, and each valid trace-level environment block meets it | only sensitivity-envelope guidance exists, or the environment profile, deadline target, trace denominator, or multiplicity rule remains unresolved | retrofitted thresholds, underdefined trace denominator, invalid pooling across run day or host-topology blocks, unsupported operational-SLA wording, or failure to meet a properly frozen per-profile count |

Exact unresolved decision parameters preserved here:

- `RID-C003-STRAT-001` still needs an accountable or clearly justified
  discordance cap `q` before one exact pair count can be frozen.
- `RID-C003-DEADLINE-001` still needs an accountable environment profile and a
  claim-safe deadline interpretation target before an operational benchmark size
  can be frozen.
- `RID-C003-IID-001`, `RID-C003-CORR-001`, `RID-C003-STRAT-001`,
  `RID-C003-SW-001`, and `RID-C003-DEADLINE-001` still need their final
  confirmatory precision or assurance targets to be prospectively frozen rather
  than inferred from the sensitivity examples above.
- No within-family adjusted-alpha rule is frozen yet for any confirmatory
  stochastic family. The `alpha = 0.025` and `alpha = 0.0166666667` rows remain
  sensitivity examples only until a logged amendment selects the actual rule.
- If either parameter is introduced later, it must arrive by logged amendment to
  this file and `research-case/03-design/preregistration-and-deviations.md`,
  not by backfitting from observed confirmatory outputs.

## Sensitivity

- Tightening the unpaired per-comparison alpha from `0.05` to `0.025` raises
  the `+/- 0.05` per-cell requirement from `385` to `503`; tightening to
  `0.0166666667` raises it to `574`.
- Tightening the unpaired precision target from `+/- 0.075` to `+/- 0.05`
  raises the two-sided 95 percent requirement from `171` to `385` per cell.
- For paired gaps, the required count is linear in the discordance cap `q`.
  Moving from `q = 0.20` to `q = 0.30` raises the `+/- 0.05` requirement from
  `308` to `461` matched pairs.
- For zero-failure assurance, the required count scales quickly as the target
  upper bound tightens: one-sided 95 percent `< 0.02` needs `149` zero-failure
  runs, while `< 0.01` needs `299`.
- If future deadline benchmarking or correlation analysis uses a richer
  estimator than the closed-form envelopes above, a simulation-based operating
  characteristic check should validate that the chosen `n` still attains the
  declared precision or decision target under blocked environment profiles, with
  at least `5000` Monte Carlo replicates and a reported Monte Carlo confidence
  interval.
- None of these sensitivity changes resolves the upstream blockers. The
  research case remains in `INTAKE`, and the correct downstream action is still
  design and gate completion rather than execution.
