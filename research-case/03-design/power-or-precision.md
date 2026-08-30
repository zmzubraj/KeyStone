# KEYSTONE power or precision rationale

Status: `DRAFT / PRE-AUTHORIZATION`
System: `KEYSTONE-MPP-F1`
Date: `2026-08-29`
Current canonical phase: `INTAKE`
Upstream blockers preserved: `NOVELTY_UNRESOLVED`, `feasibility_decision=UNASSESSED`

This file is a result-blind planning artifact. It does not authorize execution,
does not issue `GO`, does not set an operational deadline target from existing
outputs, and does not change `research-case/program-state.json`.
The result-blind draft amendment at
`research-case/03-design/pc03-prospective-amendment.md` now specifies exact
counts, precision targets, multiplicity rules, and seed blocks for three
minimum synthetic cells: IID baseline, stratified-versus-uniform at `s=8`, and
selective withholding at `w=11`. Those parameters remain developmental and
non-executable until independently verified and separately authorized.
Correlated-domain analysis remains
`EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE`; the deadline family remains
`EXCLUDED_PENDING_ENVIRONMENT_PROFILE`.

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
| `RID-C003-IID-001` | stochastic scenario family | one seed block containing 4,096 independent model draws | 131,072 prespecified draws plus 32 blockwise estimates for the single `iid-10pct-uniform` cell | absolute error at most 0.005 under the frozen synthetic model |
| `RID-C003-CORR-001` | excluded stochastic family | not frozen | not frozen | `EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE`; current correlated-domain displays remain exploratory only |
| `RID-C003-STRAT-001` | paired comparison | one seed block containing 4,096 common-random-number policy pairs | 131,072 paired draws plus 32 blockwise estimates for the single `s=8` matched cell | absolute error at most 0.01 for the paired policy difference |
| `RID-C003-SW-001` | paired comparison | one seed block containing 4,096 draws with both audit-pass and dispute-success outcomes | 131,072 paired draws plus 32 blockwise estimates for the single `w=11` cell | absolute error at most 0.01 for the within-draw limitation gap |
| `RID-C003-DEADLINE-001` | excluded distributed-trace benchmark | not frozen | not frozen | `EXCLUDED_PENDING_ENVIRONMENT_PROFILE`; no operational SLA target |

## Operative PC03 amendment

The machine-readable operative draft is
`research-case/03-design/pc03-prospective-counts.csv`; the deterministic primary
and reserve streams are in `research-case/03-design/pc03-seed-schedule.csv`.
Every scheduled cell uses 32 primary seed blocks and four reserve blocks, with
4,096 draws per block and 131,072 primary draws per cell. The reserve blocks do
not increase the planned denominator; they replace documented infrastructure
failures in order and never replace an unfavorable valid outcome.

For the single scheduled Bernoulli cell, the result-blind planning rule is the
Hoeffding bound `n >= ceil(log(2/0.05)/(2 epsilon^2))`. At
`epsilon=0.005`, the requirement is 73,778 independent synthetic draws. For
each single scheduled paired-difference cell in `[-1,1]`, the rule is
`n >= ceil(2 log(2/0.05)/epsilon^2)`; at `epsilon=0.01`, the requirement is
also 73,778 matched synthetic draws. The scheduled 131,072 draws per included
cell satisfy both envelopes without using an exploratory effect size or
discordance estimate. Seed blocks are execution and reproducibility units;
model draws are the Monte Carlo sampling units for the frozen synthetic
probability estimands.

## Assumptions

- Existing exploratory pass rates, timings, gas values, and favorable plots were
  not used to choose thresholds here.
- The default family for precision statements is two-sided 95 percent coverage
  with `alpha = 0.05`, giving `z_(1-alpha/2) = 1.9599639845`.
- Historical multiplicity sensitivity is illustrated here by tightening the
  per-comparison alpha inside one prose claim family:
  - `alpha = 0.025` for two protected comparisons gives `z = 2.2414027276`;
  - `alpha = 0.0166666667` for three protected comparisons gives `z = 2.3939797991`.
  These remain non-binding sensitivity examples. The operative draft contains
  one primary cell in each included family, so no within-family primary
  multiplicity adjustment is required; optional secondary tests use Holm.
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
  The historical sensitivity table below keeps `q` explicit. The operative
  amendment avoids outcome-derived `q` by using the distribution-free range-two
  Hoeffding bound.
- For zero-observed-event assurance, the relevant logic is not efficacy power.
  If `x = 0` failures are observed in `n` independent runs, the one-sided upper
  bound `u` on the true failure probability solves
  - `(1 - u)^n = alpha`,
  so
  - `n >= ceil(log(alpha) / log(1 - u_target))`.
- `RID-C003-IID-001` uses the closed-form precision envelope directly because
  the estimand is a model-draw binary proportion with blockwise reporting.
  `RID-C003-CORR-001` remains excluded. `RID-C003-STRAT-001` and
  `RID-C003-SW-001` require paired-gap planning rather than unpaired formulas.
- If a later design-amendment needs model-specific operating-characteristic
  checks for the deadline benchmark or a more complex paired estimator, use a
  simulation-based planner with at least `5000` Monte Carlo replicates per
  candidate `n` and report the Monte Carlo Wilson interval on estimated
  power or coverage. Near `0.80`, `5000` replicates imply about `+/- 0.011`
  Monte Carlo uncertainty.
- Seed blocks use disjoint deterministic streams. Independent synthetic scenario
  draws estimate only a frozen model probability; blockwise estimates remain the
  execution and reproducibility units. Events inside one trajectory, contract
  lifecycle, or distributed trace are not separate draws and must not inflate
  the denominator.

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

These historical sensitivity counts could apply separately to a future
prospectively frozen cell; they are non-operative for the present amendment:

- `RID-C003-IID-001` per IID scenario cell;
- `RID-C003-CORR-001` only after a truthful domain-label source and a new
  prospective amendment;
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
| `RID-C003-IID-001` | distribution-free Hoeffding planning over independent synthetic draws, with blockwise reporting and descriptive Wilson intervals | model draws estimate the frozen synthetic probability; blocks preserve execution dispersion and reproducibility |
| `RID-C003-CORR-001` | no operative calculation while excluded | truthful domain labels and a valid comparator are missing, so current exploratory displays cannot determine a confirmatory denominator |
| `RID-C003-STRAT-001` | distribution-free range-two Hoeffding planning over common-random-number matched draws | matched draws create paired outcomes, so unpaired formulas would overstate information |
| `RID-C003-SW-001` | distribution-free range-two Hoeffding planning on the within-draw audit-pass minus dispute-success gap; component Wilson intervals are descriptive | the central estimand is a within-draw limitation gap, not two unrelated proportions |
| `RID-C003-DEADLINE-001` | no operative calculation while excluded | the environment profile and trace-level denominator are not frozen |

## Decision

Planning consequences are stated without issuing `GO`. The older numerical
tables in `## Calculation` remain sensitivity history. The operative draft
thresholds and denominators are those in the PC03 amendment and counts CSV, but
they cannot become executable until independent methods verification and a
separate accountable start decision are recorded.

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
| `RID-C003-CORR-001` | a truthful domain-label source, valid comparator, result-blind target, and new prospective amendment are independently verified before execution | remains `EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE` | exploratory outputs are relabeled as confirmatory, or execution occurs without the missing source and amendment |
| `RID-C003-STRAT-001` | an accountable, result-blind paired-gap target and justified discordance handling are frozen by logged amendment, the exact matched-pair count is computed prospectively, and the matched-pair run count meets it | only paired sensitivity-envelope examples exist, or the paired target, discordance basis, or multiplicity rule remains unresolved | retrofitted thresholds, unpaired treatment of matched data, underdefined pair denominator, invalid pooling across semantic cells, or failure to meet a properly frozen matched-pair count |
| `RID-C003-SW-001` | an accountable, result-blind paired-gap target and justified discordance handling are frozen by logged amendment, the exact paired-run count is computed prospectively, and the valid paired run count meets it | only paired sensitivity-envelope examples exist, or the paired target, discordance basis, or multiplicity rule remains unresolved | retrofitted thresholds, treating component outcomes as independent unpaired samples, underdefined paired denominator, invalid pooling across adversary cells, or failure to meet a properly frozen paired-run count |
| `RID-C003-DEADLINE-001` | an accountable environment profile and claim-safe trace-level target are independently verified in a new prospective amendment | remains `EXCLUDED_PENDING_ENVIRONMENT_PROFILE` | exploratory or local timing is relabeled as an operational deadline result, or execution occurs without the missing profile and amendment |

Exact unresolved decision parameters preserved here:

- Three minimum cells now have exact result-blind counts and deterministic seed
  schedules, but the amendment still needs independent methods verification and
  must remain non-executable until a separate start decision.
- `RID-C003-CORR-001` remains
  `EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE`; its existing displays are
  preliminary and cannot support a confirmatory correlation claim.
- `RID-C003-DEADLINE-001` still needs an accountable environment profile and a
  claim-safe deadline interpretation target before an operational benchmark size
  can be frozen.
- The deadline family still needs its final precision and multiplicity rule.
  Its environment profile, trace denominator, and claim-safe deadline
  interpretation remain unresolved.
  Each included family has one primary cell; optional secondary hypothesis tests
  use Holm within the same prespecified family.
- If a parameter is revised later, it must arrive by logged amendment to
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
