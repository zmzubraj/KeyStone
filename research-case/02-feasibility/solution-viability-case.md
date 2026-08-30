# KEYSTONE solution-viability case

Status: `DRAFT / PRE-GATE`
System: `KEYSTONE-MPP-F1`
Date: `2026-08-29`
Current canonical phase: `INTAKE`
Canonical novelty state: `NOVELTY_UNRESOLVED`
Canonical feasibility decision: `UNASSESSED`

## Claim boundary

This document is a draft feasibility input only. It does not phase-promote the
research case, does not issue `GO`, and does not override
`research-case/program-state.json`.

The only claim-safe working boundary is the narrow `REFRAME` position already
captured by the novelty package:

> KEYSTONE studies a rollup-dispute-specific serviceability property distinct
> from ciphertext availability, and instantiates a non-production,
> pre-authorization canary partial-decryption audit whose contribution is the
> combination of property separation, explicit catastrophic false-accept
> analysis, correlated-failure qualification, and a conditional
> deadline-evidence interface.

Claim-specific viability posture:

| Claim ID | Claim-safe boundary for this package | Current direct support | Current ceiling |
| --- | --- | --- | --- |
| `C001` | novelty remains a narrow property/composition/analysis hypothesis only | `research-case/01-novelty/novelty_reconciliation.md` and `research-case/01-novelty/independent-search-challenge.md` show broad novelty is rejected and narrow novelty is still unresolved | `V0 ASSERTED` until remaining novelty closure and independent verification |
| `C002` | feasibility may rely on local prototype and verification artifacts only as planning evidence | `VERIFICATION.md`, `WORKSPACE.md`, `prototype/README.md`, and `contracts/README.md` show a reproducible local prototype, simulations, contract boundary, figures, and tests | internal planning ceiling only; no canonical promotion beyond `INTAKE` |
| `C003` | solution viability is limited to analytical, simulated, and internal prototype scope under frozen non-production boundaries | `paper/theorem_roadmap.md`, `VERIFICATION.md`, `prototype/README.md`, and `contracts/README.md` provide current direct internal support | `V3 INTERNAL` planning ceiling only; no external or field wording |

Non-claims that remain locked:

- no new threshold-encryption, DKG, PVSS, DLEQ, or context-dependent
  cryptographic primitive;
- no proof that a passed canary audit guarantees future dispute cooperation;
- no timing-free guilt attribution for non-response;
- no production-security claim for the prototype or contract boundary;
- no external, deployment, or field claim without claim-matched `V4` or `V5`
  evidence.

## Thresholds

These thresholds are result-blind. They come from claim safety, proof
obligations, and phase-gate requirements rather than from the currently
observed favorable outputs.

| Surface | Minimum threshold for a claim-safe next step | Current local evidence | If threshold is not met |
| --- | --- | --- | --- |
| Governance and authority | accountable human authority, study profile, and institutional or venue basis must be explicitly verified for the named next phase | draft charter and study profile exist, but accountable confirmation is missing | keep progression `BLOCKED` |
| Novelty | patent/standards closure, citation-chain closure, and independent verification must leave the narrow `REFRAME` claim undefeated | broad claim already rejected; narrow claim still unresolved | keep novelty `UNRESOLVED`; do not broaden claims |
| Property separation | at least one formal counterexample class must preserve `ciphertext availability != present dispute-key serviceability` | `research-case/01-novelty/problem-investigation.md`, `paper/theorem_roadmap.md`, and `research-case/01-novelty/novelty-claim-specification.md` define the intended separation | narrow to a systems note or `STOP` if the distinction collapses |
| Cryptographic correctness | confirmatory package must preserve `t` opens, `t-1` fails, invalid partials are rejected, and routine audits never touch production ciphertext | local tests and frozen scope document these properties | `REDESIGN` if any property fails under the frozen protocol |
| Static sampling analysis | confirmatory exact or exhaustive checks must match the declared hypergeometric or exact-stratified model for each frozen semantics | exact bound and validation artifacts exist locally | narrow or remove any theorem that lacks model-faithful validation |
| Correlation contribution | at least one prespecified correlated-failure case must change a design, ranking, or safety conclusion relative to IID-only reasoning | local correlated simulations and stratified calculations exist, but confirmatory interpretation is not frozen | drop correlation as a headline contribution if no decision-changing divergence survives |
| Deadline evidence | any deadline or accountability wording beyond a toy artifact requires a frozen distributed benchmark under declared synchrony assumptions and preserved traces | no representative distributed benchmark evidence exists yet | keep deadline language conditional and limited to the design model |
| Independent challenge | threshold-cryptography, distributed-systems, and reproduction challenges must be completed before stronger full-paper wording | novelty challenge exists; proof, systems, and reproduction challenges are still missing | recommend `PILOT_FIRST` after blockers clear |

Threshold-setting actions required before any numeric performance rule:

1. Define the target deployment envelope for any deadline or latency claim.
2. Freeze the benchmark environment, network profiles, and failure injections.
3. Freeze the confirmatory result IDs and decision rules before rerunning.

Until those actions are complete, no numeric performance threshold is justified.

## Failure envelope

The current evidence supports only a bounded failure envelope:

- static catastrophic false-accept analysis is limited to the declared sampling
  model and ready-set semantics;
- repeated-audit reasoning must remain separate from time-evolving availability;
- selective withholding is a preserved negative result, not a solved problem;
- correlated-failure findings depend on truthful domain labels and the tested
  outage models;
- deadline evidence is conditional on synchrony, delivery, and clock
  assumptions;
- the prototype uses dealer-based setup and experimental refresh for controlled
  research only;
- the contract records public evidence but does not on-chain verify DLEQ proofs
  or timing blame;
- existing runs are exploratory or internal and cannot set confirmatory
  thresholds retroactively.

Failure conditions that force claim narrowing, redesign, or stop:

- a credible predecessor defeats the narrow `REFRAME` claim;
- the canary audit fails to carry information beyond static registration or
  ordinary heartbeat monitoring;
- confirmatory correlated-failure analysis does not change any meaningful
  recommendation;
- distributed evidence contradicts even the conditional deadline wording;
- independent reproduction cannot recreate the authoritative local results from
  the frozen inputs;
- proof obligations fail or reveal that the advertised property is weaker than
  claimed.

Useful negative result preserved by this package:

- an audit can pass while the targeted dispute still fails under selective
  withholding, so readiness evidence must remain a present-state proxy rather
  than a future-cooperation guarantee.

## Falsification sequence

1. Close novelty first: complete the remaining patent, standards-adjacent, and
   citation-chain surfaces and keep the broad claim rejected unless the narrow
   claim survives independent verification.
2. Lock the result-blind confirmatory protocol before any new evidence rerun.
3. Reproduce the property-separation counterexample and the exact false-accept
   model from authoritative inputs.
4. Preserve the selective-withholding counterexample in the confirmatory bundle
   as a live refutation risk, not as a removable limitation.
5. Run a bounded `PILOT_FIRST` distributed deadline benchmark under declared
   synchrony assumptions using only synthetic or sacrificial data.
6. Obtain one independent clean-machine reproduction and one threshold-crypto
   review plus one distributed-systems review.
7. Reassess the claim ceiling:
   - remain `BLOCKED` if authority or novelty gaps persist;
   - move to `PILOT_FIRST` only after those blockers clear;
   - use `REDESIGN` or `STOP` if the pilot or reviews collapse the claim-safe
     boundary.
