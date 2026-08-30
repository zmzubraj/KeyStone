# KEYSTONE novelty claim specification

Status: `DRAFT / PREDECLARED CLAIM SPEC`
System: `KEYSTONE-MPP-F1`
Date: `2026-08-29`
Disposition ceiling: `NOVELTY_UNRESOLVED`

## 1. Historical broad claim

The intake novelty statement is preserved as the historical hypothesis:

> We formalize dispute-key availability as deadline-bounded, authorized
> reconstructability distinct from ciphertext data availability, and instantiate
> it with non-revealing canary partial-decryption sampling, explicit false-accept
> bounds, correlation-aware committee audits, and public deadline evidence.

This wording is not submission-safe as a novelty claim without further
qualification.

## 2. Narrow working claim

The only claim-safe working novelty candidate is:

> KEYSTONE studies a rollup-dispute-specific serviceability property distinct
> from ciphertext availability, and instantiates a non-production,
> pre-authorization canary partial-decryption audit whose contribution is the
> combination of property separation, explicit catastrophic false-accept
> analysis, correlated-failure qualification, and a conditional deadline-evidence
> interface.

This is a property, composition, and analysis claim. It is not a primitive
claim.

## 3. Claim axes

| Axis | Predeclared question | Current status | Safe ceiling |
| --- | --- | --- | --- |
| Problem novelty | Is dispute-key serviceability framed as distinct from ciphertext availability and static share validity? | plausible but challenged | narrow hypothesis only |
| Mechanism novelty | Is a pre-authorization non-production canary readiness probe materially distinct from prior timed/authorized release systems? | unresolved | no standalone novelty claim |
| Method or architecture novelty | Is the exact combination of canonical canary, proof transcript, and bulletin-board evidence materially new? | weak because components are prior art | integration only |
| Evaluation novelty | Is correlation-aware readiness analysis materially beyond existing committee/liveness evaluation? | unresolved | contribution only if tightly matched |
| Consequence novelty | Does the work newly establish practical dispute reliability or accountability? | not supported | do not claim |

## 4. Falsifiable central claim

`C001-narrow`:

There exists a meaningful class of encrypted-rollup executions in which
ciphertext availability and dispute-key serviceability diverge, and a
pre-authorization canary partial-decryption audit can quantify catastrophic
false acceptance for present readiness under declared static or correlated
failure assumptions.

This claim is falsified if either of these conditions holds:

- the divergence is already fully captured by a stronger predecessor using
  essentially the same property and probe; or
- the audit cannot support a distinct readiness estimand beyond static share
  registration or generic heartbeat evidence.

## 5. Supporting claim map

| Claim ID | Working claim | Required support | Disallowed upgrade |
| --- | --- | --- | --- |
| `C001` | DKA is distinct from ciphertext availability | formal counterexample class and property definitions | do not imply first-ever timed threshold release |
| `C003` | static catastrophic false-accept is explicitly bounded | theorem plus exact or simulated validation | do not claim time-evolving guarantee |
| `K-C1` | canary uses non-production current-serviceability evidence | transcript binding and no-record-audit path | do not claim new cryptography |
| `K-C2` | invalid response and equivocation evidence are objective | deterministic verification and identity binding | do not claim timing-free guilt attribution |
| `K-C3` | correlated failures materially affect readiness | failure-domain model and comparison results | do not claim universal real-world calibration |
| `K-C4` | audit-time readiness differs from dispute-time cooperation | selective-withholding qualification | do not claim audit implies future cooperation |
| `K-C5` | deadline evidence is conditional on synchrony assumptions | declared timing model and public request/response traces | do not claim unconditional liveness accountability |

## 6. Submission-safe language

Use:

- `We formalize a dispute-specific serviceability property distinct from public ciphertext availability.`
- `We instantiate an internal non-production readiness probe using established verifiable partial-decryption techniques.`
- `We quantify catastrophic false acceptance under declared static and correlated failure models.`
- `We treat deadline evidence as conditional on declared synchrony assumptions.`

Do not use:

- `first threshold decryption system for encrypted rollups`
- `new context-bound threshold decryption`
- `new proof of share possession`
- `new accountable threshold decryption primitive`
- `proof of future availability`

## 7. Materiality thresholds by axis

Problem axis survives only if:

- the manuscript exhibits at least one concrete counterexample where `CA` holds
  and dispute serviceability fails; and
- prior timed-release or encrypted-mempool systems do not already make the same
  property explicit at equivalent granularity.

Mechanism axis survives only if:

- the probe is clearly pre-authorization and non-production; and
- the strongest predecessor does not already use a substantially equivalent
  readiness drill.

Evaluation axis survives only if:

- the correlated-failure analysis changes a decision, ranking, or safety
  conclusion relative to IID-only treatment.

## 8. Defeating evidence

Any of the following defeats the narrow novelty claim:

- a predecessor with dispute or challenge authorization plus a non-production
  partial-decryption readiness audit before authorization;
- a predecessor with explicit readiness false-accept analysis for threshold
  dispute serviceability;
- a predecessor that combines the above with correlation-aware committee
  sampling or equivalent domain-aware readiness evaluation.

## 9. Explicit non-claims and scope lock

KEYSTONE does not claim novelty for:

- threshold encryption itself;
- context-binding itself;
- DLEQ or Chaum-Pedersen proofs;
- proactive or dynamic secret sharing;
- public bulletin-board escalation by itself;
- authorized threshold release by itself;
- liveness accountability without timing assumptions.

## 10. Decision rule

Current disposition remains `NOVELTY_UNRESOLVED`.

Allowed next outcomes after additional search closure:

- `REFRAME` if only the property-separation wording survives;
- `NOVELTY_SURVIVES` only if no defeating predecessor is found for the narrow
  composition and analysis claim;
- `STOP` if the narrow slice is also clearly anticipated.
