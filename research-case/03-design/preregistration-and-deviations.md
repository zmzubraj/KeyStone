# KEYSTONE preregistration and deviations record

Status: `DRAFT / PRE-AUTHORIZATION`
System: `KEYSTONE-MPP-F1`
Date: `2026-08-29`
Current canonical phase: `INTAKE`

This file records what is frozen now and what remains unresolved. It is not an
execution authorization and does not change any canonical gate decision.

## Preregistered decisions

Frozen now:

- claim scope is limited to charter claims `C001`, `C002`, and `C003`;
- all broader novelty wording remains prohibited until the narrow novelty case
  survives independent closure;
- the generated deadline-pilot start package at
  `research-case/03-design/deadline-pilot-start-package-manifest.json` and its
  paired CSV or Markdown files are design-only preauthorization artifacts;
- all confirmatory outputs must map to the result IDs listed in
  `research-case/03-design/protocol.md`;
- `RID-C002-CRYPTO-001` and `RID-C002-CONTRACT-001` are frozen as
  deterministic zero-tolerance correctness or lifecycle obligations rather than
  stochastic population estimands;
- the primary committee baseline remains `n=32`, `t=22`, `s=8`, `q=8`;
- routine audits must use canonical canaries and must never use production
  ciphertext elements;
- selective withholding remains a mandatory negative-result family;
- static ready-set analysis, correlated-failure analysis, and conditional
  deadline analysis remain separate evidence families;
- run-order randomization, seed recording, and nuisance blocking follow the
  protocol;
- failed or contradictory runs remain in the evidence ledger and cannot be
  silently excluded;
- no numeric success, futility, or performance thresholds may be backfit from
  the existing exploratory outputs;
- the result-blind PC03 draft amendment freezes 32 primary and four reserve seed
  blocks per included cell, 4,096 independent synthetic model draws per block,
  131,072 primary draws per included cell, and the complete deterministic seed
  schedule for one IID baseline cell, one stratified-versus-uniform `s=8`
  matched cell, and one selective-withholding `w=11` cell;
- each included family has one primary cell, so no within-family primary
  multiplicity adjustment is required; optional secondary tests use Holm;
- `RID-C003-CORR-001` is
  `EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE`; current correlated-domain
  outputs remain exploratory and cannot determine a confirmatory denominator;
- `RID-C003-STRAT-001` and `RID-C003-SW-001` remain paired within synthetic
  draw and seed block; unpaired substitution is prohibited;
- `RID-C003-DEADLINE-001` is `EXCLUDED_PENDING_ENVIRONMENT_PROFILE`.

Frozen as unresolved and delegated:

- the three included stochastic cells have exact draft counts and
  precision targets in `pc03-prospective-amendment.md` and
  `pc03-prospective-counts.csv`, but they remain non-executable until an
  independent methods verifier accepts the denominator, pairing, stream,
  multiplicity, and analysis rules and a separate start decision is signed;
- the generated deadline environment profiles are role-only placeholders with
  `EXCLUDED_PENDING_ENVIRONMENT_PROFILE` for the environment profile, run-day block,
  deadline interpretation, trace denominator, precision target, and
  multiplicity rule;
- any distributed execution remains prohibited until the environment profile,
  deadline interpretation, trace denominator, precision target, multiplicity
  rule, novelty gate, and required accountable approval are prospectively
  resolved;
- the accountable-human draft-design authority and no-conflict policy basis are
  recorded for this package, but final author order, corresponding-author
  identity, affiliation wording, institutional endorsement, external sharing,
  and submission remain separately gated human decisions;
- external reviewer outreach and any external sharing of unpublished local
  artifacts remain human-only decisions.

## Timestamp

Preregistration draft timestamp: `2026-08-29 Asia/Dhaka`

PC03 result-blind amendment timestamp: `2026-08-30 Asia/Dhaka`

Evidence cutoff used for freezing this draft:

- local unpublished workspace artifacts available through `2026-08-29`;
- no new public-web or external-source material was introduced by this task;
- existing exploratory results were read only as feasibility context and were
  not used to derive confirmatory thresholds;
- count formulas use only the prespecified family sizes, alpha, absolute-error
  targets, bounded outcome ranges, and synthetic Monte Carlo draw contract.

## Deviations

No execution-time deviations exist yet because this is a pre-authorization
design freeze draft.

Future deviation classes are predeclared:

| Deviation class | Example | Required handling |
| --- | --- | --- |
| scope deviation | new claim family, new novelty wording, or new deployment claim | requires explicit logged amendment and may require `UNFREEZE` |
| endpoint deviation | changed result ID semantics, changed primary endpoint definition, or relabeling a deterministic boundary check as a stochastic estimand | blocked until a preregistered amendment is approved and historical outputs remain quarantined |
| threshold deviation | new numeric success or futility threshold after seeing confirmatory outcomes | prohibited; must remain exploratory only |
| environment deviation | different runtime, toolchain, host topology, or network profile | log in the run manifest and assess as a sensitivity or invalidating difference |
| data-integrity deviation | missing telemetry, missing seed manifest, or irreproducible output | mark failed or missing; do not silently impute |
| authority deviation | execution or sharing before accountable approval | stop and escalate; resulting outputs are not canonical confirmatory evidence |

## Impact

Impact of freezing these decisions now:

- prevents exploratory pass rates, timings, gas values, and favorable plots from
  contaminating later confirmatory criteria;
- binds the generated deadline-pilot start package as design-only and prevents
  it from being overread as execution authorization or independent scientific
  verification;
- preserves the negative-result and failure-envelope obligations that support
  claim honesty;
- gives the `power_challenge` owner a stable endpoint contract without allowing
  it to rewrite claim semantics;
- keeps the research case in a truthful `INTAKE` posture while design work
  continues.

Impact if a future deviation occurs:

- affected result IDs may become exploratory-only or invalid for the blocked
  claim;
- the corresponding claim ceiling cannot rise until the deviation is reconciled;
- severe deviations can force `REDESIGN`, `BLOCKED`, or `STOP` rather than
  phase advancement.
