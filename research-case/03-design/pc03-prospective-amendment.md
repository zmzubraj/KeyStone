# KEYSTONE PC03 integrated prospective design amendment

Status: `DRAFT / PREAUTHORIZATION / NON-EXECUTABLE`
System: `KEYSTONE-MPP-F1`
Date: `2026-08-30`
Canonical phase: `INTAKE`

This is a result-blind integration artifact. It does not authorize execution,
issue `GO`, certify methods, promote the research phase, or convert historical
outputs into confirmatory evidence. Author metadata remains deferred.
Exploratory outputs were not used to choose the count, precision, or decision
thresholds.

## Independent challenge disposition

The developmental AI methods challenge under
`research-case/03-design/pc03-independent-methods-challenge/` recommended the minimum decisive cell set:
one IID baseline cell, one matched sampling-policy cell, and the
selective-withholding boundary at `n-t+1=11`; it recommended excluding CORR
and DEADLINE until their missing contracts are frozen. This narrowing is
accepted because it matches the minimum publishable claim and avoids silently
promoting broad exploratory sweeps.

The challenge's proposed counts of 97 and 193 seed-level runs are not adopted.
The current simulator returns aggregate proportions from many scenario draws
inside each seed run, so treating each aggregate as a Bernoulli replicate creates
a denominator mismatch. The integrated design instead treats independent
synthetic scenario draws as the Monte Carlo denominator and seed blocks as
execution and reproducibility units. This is a root integration decision, not
an independent methods sign-off.

## Count and stream contract

Every included cell uses 32 primary seed blocks and four ordered reserve blocks,
with 4,096 independent synthetic scenario draws per block and 131,072 primary
draws per cell. Blockwise estimates and between-block dispersion are mandatory.
A failed primary block stays in the deviation ledger and may be replaced only by
the next reserve block; a valid unfavorable block is never replaceable.

For one Bernoulli cell, Hoeffding requires
`n >= ceil(log(2/0.05)/(2*0.005^2)) = 73,778` draws. For one paired
difference in `[-1,1]`, it requires
`n >= ceil(2*log(2/0.05)/0.01^2) = 73,778` matched draws. The scheduled
131,072 draws exceed both bounds. These guarantees concern precision under the
frozen synthetic model only; they are not field power, deployment reliability,
or external validation.

| Result ID | Operative cell | Capacity | Required | Precision | Status |
| --- | --- | ---: | ---: | --- | --- |
| `RID-C003-IID-001` | `iid-10pct-uniform;n=32;t=22;s=8;q=8;p_offline=0.10` | `131072` | `73778` | `ABSOLUTE_HALF_WIDTH_LE_0.005` | `BLOCKED_PENDING_GATE` |
| `RID-C003-CORR-001` | `NONE` | `0` | `UNRESOLVED` | `UNRESOLVED` | `EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE` |
| `RID-C003-STRAT-001` | `domain-outage-20pct;sample-size-8;uniform-vs-stratified;domains=4` | `131072` | `73778` | `ABSOLUTE_HALF_WIDTH_LE_0.010` | `BLOCKED_PENDING_GATE` |
| `RID-C003-SW-001` | `selective-withholders-11;n=32;t=22;s=8;q=8` | `131072` | `73778` | `ABSOLUTE_HALF_WIDTH_LE_0.010` | `BLOCKED_PENDING_GATE` |
| `RID-C003-DEADLINE-001` | `NONE` | `0` | `UNRESOLVED` | `UNRESOLVED` | `EXCLUDED_PENDING_ENVIRONMENT_PROFILE` |

## Analysis boundary

- `RID-C003-IID-001`: empirical reconstruction and audit-pass proportions,
  absolute error target 0.005, plus blockwise estimates and exact zero-event
  upper bounds.
- `RID-C003-STRAT-001`: common-random-number paired difference at sample size
  8, absolute error target 0.01; unpaired substitution is prohibited.
- `RID-C003-SW-001`: within-draw audit-pass minus dispute-success gap at 11
  selective withholders, absolute error target 0.01; the limitation is reported
  regardless of direction.
- `RID-C003-CORR-001`: `EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE`.
- `RID-C003-DEADLINE-001`: `EXCLUDED_PENDING_ENVIRONMENT_PROFILE`.

There is one primary cell per included result family, so no primary within-family
multiplicity adjustment is needed. Optional secondary hypothesis tests use Holm
within their named family and cannot upgrade a claim.

## Stop rules

Stop or redesign on overlapping random streams, exploratory-outcome-dependent
thresholds, cross-cell pooling, unpaired treatment of matched outcomes, hidden
failed blocks, suppressed negative findings, execution of an excluded lane,
use of personal data or production secrets, or manuscript wording beyond
simulated-model maturity.

The machine-readable sources are `research-case/03-design/pc03-prospective-counts.csv` and
`research-case/03-design/pc03-seed-schedule.csv`. All execution remains blocked pending PC01 authority,
PC02 novelty disposition, authenticated independent PC03 methods verification,
and a separate accountable start decision.
