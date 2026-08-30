# KEYSTONE study-design protocol

Status: `DRAFT / PRE-AUTHORIZATION`
System: `KEYSTONE-MPP-F1`
Date: `2026-08-29`
Current canonical phase: `INTAKE`
Upstream blockers preserved: `NOVELTY_UNRESOLVED`, `feasibility_decision=UNASSESSED`

This protocol is a result-blind study-design draft. It does not authorize
execution, does not issue `GO`, does not create `04-data/*`, and does not
override `research-case/program-state.json`.

## Research question

Primary research question:

> Under the frozen non-production KEYSTONE boundary, can an encrypted-rollup
> dispute workflow expose public, pre-authorization evidence about present
> threshold-decryption serviceability that is distinct from ciphertext
> availability, while preserving explicit limits for selective withholding,
> correlated failure, and deadline-conditioned accountability?

Claim mapping:

| Claim ID | Design target | Claim-safe output type |
| --- | --- | --- |
| `C001` | property separation, bounded novelty-supporting formalization inputs, and falsifier-preserving counterexample reproduction | definition, theorem, or counterexample artifact only |
| `C002` | feasibility of a reproducible non-production prototype, simulator, and bulletin-board boundary under frozen scope | internal prototype and reproducibility evidence only |
| `C003` | analytical, simulated, and pilot-design evidence for readiness sampling, correlation qualification, and conditional deadline wording | analytic, simulation, internal prototype, and later pilot evidence only |

Result IDs reserved by this protocol:

| Result ID | Surface | Claims |
| --- | --- | --- |
| `RID-C001-SEP-001` | property-separation counterexample reproduction | `C001` |
| `RID-C001-STATIC-001` | exact static false-accept and detection bound at the frozen baseline | `C001`, `C003` |
| `RID-C002-CRYPTO-001` | threshold-KEM correctness, invalid-partial rejection, and context-bound transcript checks | `C002`, `C003` |
| `RID-C002-CONTRACT-001` | bulletin-board lifecycle, equivocation, missing-response, and evidence-record behavior | `C002` |
| `RID-C003-IID-001` | IID readiness simulation family | `C003` |
| `RID-C003-CORR-001` | correlated-failure simulation family | `C003` |
| `RID-C003-STRAT-001` | stratified-versus-uniform sampling comparison | `C003` |
| `RID-C003-SW-001` | selective-withholding negative-result family | `C003` |
| `RID-C003-DEADLINE-001` | conditional deadline distributed benchmark family | `C003` |

Result-contract closure:

| Result ID | Endpoint class | Unit-level denominator | Pairing or blocking structure | Manuscript traceability intent |
| --- | --- | --- | --- | --- |
| `RID-C001-SEP-001` | deterministic counterexample witness | one preserved counterexample class per theorem or parameter cell | blocked by theorem revision and code revision | property-separation theorem, counterexample note, or limitation text |
| `RID-C001-STATIC-001` | exact analytic quantity | one frozen parameter cell per exact semantics | blocked by parameter cell and model semantics | analytical theorem or primary results table |
| `RID-C002-CRYPTO-001` | deterministic correctness obligation | one named correctness case per required boundary class | blocked by code revision, transcript version, and seed batch; no pairing across cases | correctness theorem, methods, and verification table |
| `RID-C002-CONTRACT-001` | deterministic contract-evidence obligation | one complete request lifecycle trace per named contract case | blocked by contract revision, toolchain version, and seed batch; case families reported separately | contract-boundary table and evidence-interface description |
| `RID-C003-IID-001` | stochastic scenario family | one complete scenario run per seed and config cell | blocked by scenario family, config revision, runtime, and seed block | primary or robustness results table for IID scenarios |
| `RID-C003-CORR-001` | stochastic correlated scenario family | one complete scenario run per seed, config cell, and placement policy | blocked by domain-label source, placement policy, config revision, and seed block | correlation results table or figure |
| `RID-C003-STRAT-001` | paired stochastic policy comparison | one matched seed pair spanning both policies under one semantic cell | paired within seed; blocked by scenario cell, draw semantics, and seed block | policy-comparison table or figure |
| `RID-C003-SW-001` | stochastic negative-result family | one complete adversary scenario run per seed and config cell | blocked by adversary configuration, config revision, runtime, and seed block | limitation table, figure, and discussion text |
| `RID-C003-DEADLINE-001` | stochastic distributed benchmark family | one complete end-to-end distributed trace per seed and environment profile | blocked by environment profile, host topology, run day, and seed block | deadline-results table, figure, and limitations text |

## Design

Overall design: a staged, mixed-method computational study with four linked
surfaces.

1. Deterministic analytical surface:
   property definitions, counterexamples, exact probability calculations, and
   theorem-linked correctness checks.
2. Seeded stochastic simulation surface:
   prespecified IID, correlated-domain, stratified-sampling, and
   selective-withholding scenario families.
3. Reproducible prototype-validation surface:
   canonical transcript, threshold-boundary, invalid-proof, and
   authorization-boundary tests under the frozen prototype.
4. Conditional deadline pilot-design surface:
   a future distributed benchmark under synthetic traffic and declared
   synchrony assumptions only after blocker clearance.

Primary confirmatory design posture:

- no execution may begin until accountable authority closes `PC01` and the
  narrow novelty blocker in `PC02` is resolved or safely narrowed;
- this document freezes result semantics, endpoint families, and execution
  boundaries before any new confirmatory rerun;
- the exact replicate counts, precision targets, and any numeric acceptance
  tolerances not justified here are explicitly deferred to
  `research-case/03-design/power-or-precision.md`.

Experimental unit and independent replicate by surface:

| Surface | Experimental unit | Independent replicate | Pseudoreplication rule |
| --- | --- | --- | --- |
| deterministic analytic checks | one fully specified parameter cell or theorem obligation | one parameter cell or proof obligation | derived rows from the same exact computation do not count as extra replicates |
| prototype correctness tests | one fresh seeded end-to-end run or one isolated negative test case | one run using one seed and one code revision | multiple assertions from the same run are one replicate for that run-level endpoint |
| stochastic simulations | one full scenario execution under one seed and one config cell | one seed-level scenario run | audits within the same scenario trajectory are nested observations, not independent replicates |
| distributed deadline benchmark | one full multi-node trace for one environment profile and one seed | one end-to-end trace | messages, retries, or node-local events inside the trace are not independent replicates |

Factors and levels frozen here:

| Factor | Levels frozen now | Notes |
| --- | --- | --- |
| protocol role family | static bound, IID simulation, correlated simulation, stratified comparison, selective withholding, prototype correctness, contract boundary, distributed deadline | separate result families; no pooling across roles |
| baseline committee parameters | primary confirmatory baseline `n=32`, `t=22`, `s=8`, `q=8` | inherited from `FREEZE.md` |
| readiness failure model | IID member unavailability; correlated domain outage; selective withholding; conditional synchrony deadline stress | each family has separate estimands |
| sampling policy | uniform without replacement; fixed-quota stratified design; canary response-only routine audit | full-committee or escalated policies may appear only as exploratory side analyses unless added by later preregistered amendment |
| domain placement policy | frozen cap-respecting placement; stress cases that approach or violate the cap | used only for correlation-qualified comparisons |
| authorization context | routine pre-authorization audit; authorized dispute-specific release | routine audit must never use production ciphertext elements |
| benchmark environment profile | synthetic single-host prototype; future multi-host synthetic deadline pilot | multi-host numeric latency or loss levels remain unresolved pending power/precision and authority |

Primary experiment grid frozen now:

| Result ID | Design cell | Run-order policy | Blocking or nuisance structure |
| --- | --- | --- | --- |
| `RID-C001-SEP-001` | reproduce one or more counterexample classes where ciphertext bytes remain available but dispute-key readiness fails | deterministic order fixed by result manifest | blocked by code revision and theorem-claim revision |
| `RID-C001-STATIC-001` | exact static catastrophic-state calculation at the frozen baseline | deterministic order fixed by result manifest | blocked by parameter cell and model semantics |
| `RID-C002-CRYPTO-001` | end-to-end threshold/opening boundary, invalid partials, stale context, replay, and `t` versus `t-1` cases | seeded order randomized across case labels within one revision | blocked by code revision, runtime, and seed batch |
| `RID-C002-CONTRACT-001` | bulletin-board lifecycle plus invalid, missing, and equivocation evidence cases | seeded order randomized across request types within one revision | blocked by contract revision, toolchain version, and seed batch |
| `RID-C003-IID-001` | IID stochastic scenario family at the frozen baseline and any later power-approved sensitivity cells | randomized by seed within scenario family | blocked by scenario family, config revision, and runtime |
| `RID-C003-CORR-001` | correlated-domain outage family using prespecified truthful domain labels and outage models | randomized by seed and placement permutation within family | blocked by domain-label source, placement policy, and config revision |
| `RID-C003-STRAT-001` | stratified-versus-uniform comparison under matched total draws and matched catastrophic semantics | paired seeded ordering across the two policies | blocked by scenario family and draw semantics |
| `RID-C003-SW-001` | selective-withholding family where routine audits and targeted disputes differ by adversary behavior | randomized by seed within adversary configuration | blocked by adversary policy revision and config revision |
| `RID-C003-DEADLINE-001` | future synthetic distributed benchmark under declared synchrony assumptions | randomized by seed within environment block; block order randomized across environment profiles | blocked by environment profile, host topology, network-fault profile, and clock model |

Nuisance variables to block, record, or randomize across:

- code revision and manifest hash;
- Python, Foundry, and compiler versions;
- host hardware and operating system;
- scenario-family order and seed batch;
- domain-label source revision;
- deadline benchmark environment profile, host topology, and run day.

Randomization and ordering policy:

- all stochastic and benchmark runs use recorded seeds;
- run order is randomized within each block to avoid time-drift confounding;
- paired comparisons such as uniform versus stratified use matched seeds where
  the estimand permits;
- deterministic analytical cells keep fixed manifest order for auditability;
- if a run fails for an infrastructure reason before producing a valid result
  object, one rerun with the same seed is allowed and must be logged; further
  reruns require explicit deviation recording.

## Population or system

Study population:

- synthetic or locally generated KEYSTONE protocol instances only;
- no human participants, no personal data, no live rollup keys, and no
  production ciphertext material;
- one logical committee per scenario with four failure domains in the frozen
  baseline;
- one research-only bulletin-board contract boundary and one research-only
  threshold-KEM prototype boundary.

System boundaries:

- dealer-based setup and experimental share refresh remain research-only
  boundaries;
- no production DKG, PVSS, staking, or on-chain DLEQ verification is assumed;
- deadline accountability claims remain conditional on a later synthetic
  distributed benchmark and may not be inferred from single-host timing.

## Controls

Required controls and comparators:

- `t` valid partials versus `t-1` partials for opening correctness;
- valid versus malformed partials and valid versus wrong-context transcripts;
- routine audit versus authorized dispute behavior for selective withholding;
- uniform sampling versus fixed-quota stratified sampling under matched draw
  counts and matched catastrophic semantics;
- cap-respecting versus concentrated placement under matched failure exposure;
- IID unavailability versus correlated-domain outage under comparable marginal
  readiness assumptions;
- success-path versus missing-response or equivocation contract traces.

Control rules:

- all comparisons are concurrent within the same code revision and manifest
  family;
- historical outputs may guide feasibility but may not act as the control arm
  for confirmatory claims;
- deadline pilot controls must include at least one non-adversarial synthetic
  synchrony profile and one stress profile, but their numeric settings remain
  unresolved until power/precision review.

## Endpoints

Primary endpoints:

| Endpoint ID | Description | Claims | Evidence class |
| --- | --- | --- | --- |
| `EP-01` | property-separation witness exists: ciphertext/data availability can hold while dispute-key readiness fails | `C001` | deterministic counterexample |
| `EP-02` | exact static false-accept and detection quantities under the frozen catastrophic model | `C001`, `C003` | analytic exact result |
| `EP-03` | threshold correctness boundary: `t` valid partials open, `t-1` do not, invalid proofs are excluded, and routine audits avoid production ciphertext | `C002`, `C003` | deterministic prototype tests |
| `EP-04` | conditional deadline success measure under the declared synchrony model | `C003` | future synthetic distributed benchmark |

Secondary endpoints:

- contract evidence integrity for invalid, missing, and equivocation cases;
- reconstructability and audit outcomes under IID scenario families;
- reconstructability and audit outcomes under correlated-domain scenario families;
- difference between uniform and stratified sampling under matched semantics;
- audit-pass versus dispute-success gap under selective withholding;
- local resource and reproducibility outputs needed to sustain `C002`.

Endpoint-to-result-ID closure:

| Endpoint ID | Result IDs that satisfy it | Denominator rule |
| --- | --- | --- |
| `EP-01` | `RID-C001-SEP-001` | one preserved counterexample class per stated model variant |
| `EP-02` | `RID-C001-STATIC-001` | one exact parameter cell per frozen semantics |
| `EP-03` | `RID-C002-CRYPTO-001`, `RID-C002-CONTRACT-001` | one named deterministic case or one complete lifecycle trace per case family |
| `EP-04` | `RID-C003-DEADLINE-001` | one complete distributed trace per seed and environment profile |
| secondary support for readiness interpretation | `RID-C003-IID-001`, `RID-C003-CORR-001`, `RID-C003-STRAT-001`, `RID-C003-SW-001` | one complete scenario run per seed-level cell, except `RID-C003-STRAT-001` which uses one matched seed pair |

Robustness endpoints:

- sensitivity of exact or stochastic conclusions to placement concentration,
  outage structure, and draw policy;
- persistence of the selective-withholding gap under prespecified adversary
  configurations;
- environment drift across runtime or toolchain blocks;
- divergence between single-host prototype timing and distributed synthetic
  deadline traces.

Exploratory-only endpoints:

- any temporal-dependence or adaptive audit schedule result not explicitly
  frozen by a later preregistered amendment;
- any scale-up benchmark, multi-region test, or deployment-style overhead study
  beyond the declared synthetic pilot;
- any baseline or ablation added after this protocol date.

## Bias and leakage

Known bias risks and the prevention rule:

- novelty leakage: no wording upgrade from this design package; `C001` remains
  bounded by the novelty blocker until independent closure;
- outcome leakage: current exploratory pass rates, gas values, and timings may
  not set confirmatory thresholds, futility cutoffs, or acceptance criteria;
- model leakage: static ready-set formulas and time-evolving availability claims
  remain separated; no exponentiation shortcut may be imported into deadline
  claims without a dedicated model;
- pseudoreplication: nested audits, node-local events, or repeated assertions
  inside one scenario run do not increase the replicate count;
- environment confounding: run order is randomized within blocks and environment
  metadata is recorded for every result;
- selection bias: failed or contradictory runs are kept in the result ledger and
  are not dropped for narrative convenience.

Leakage barrier:

- all future confirmatory outputs must use the result IDs and endpoint classes
  frozen here;
- any post-hoc analysis, added baseline, or altered threshold goes to a new
  exploratory result ID and may not silently replace confirmatory evidence;
- the power or precision owner may add replicate counts or precision targets,
  but may not change endpoint semantics or introduce observed-value thresholds
  without a logged preregistration deviation.

## Stopping rules

This computational study does not use naive sequential efficacy peeking.
Interim checks are restricted to integrity, scope, and claim-safety rules.

Immediate stop conditions:

- accountable authority for the next phase is not verified;
- a newly closed novelty surface defeats the narrow claim-safe boundary;
- routine audit code touches a production ciphertext element or equivalent
  prohibited secret path;
- the `t` versus `t-1` correctness boundary fails;
- invalid partial rejection or context binding fails;
- a distributed deadline benchmark would require live secrets, live production
  systems, or prohibited external data.

Futility or redesign conditions:

- the claim-safe theorem or counterexample structure collapses into an already
  defeated or irrelevant formulation;
- correlated-failure scenarios no longer change any design, ranking, or safety
  recommendation relative to IID-only reasoning;
- the synthetic deadline benchmark cannot be specified without ungrounded or
  policy-contradicting assumptions;
- independent reproduction cannot map authoritative inputs to the frozen result
  IDs.

Tranche policy for future deadline pilot:

- traces may be collected in prespecified blocks;
- after each block, the team may inspect only integrity, completeness, and
  declared stop-condition triggers unless and until `power-or-precision.md`
  defines a valid blinded or claim-safe interim rule;
- no performance-based early-success threshold is set in this document.

## Ethics

Current ethical and authorization boundary:

- non-human computational research only;
- synthetic or locally generated research artifacts only;
- no external sharing of unpublished local artifacts without accountable human
  authorization and the existing confidentiality boundary;
- no claim beyond internal, analytic, simulated, or later synthetic-pilot scope
  without claim-matched evidence and reviewer challenge.

Required human-only authorizations before execution:

- accountable human confirmation of authorship and institutional or venue policy
  basis;
- explicit confirmation that the synthetic deadline pilot remains within
  non-human computational scope;
- explicit approval before any external reviewer receives unpublished local
  material.

Preserved negative-result obligation:

- selective withholding remains a mandatory negative-result surface and may not
  be omitted from confirmatory reporting if it contradicts stronger readiness
  language.
