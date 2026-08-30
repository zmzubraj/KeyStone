# KEYSTONE novelty reconciliation

**Status:** `DRAFT_ROOT_RECONCILIATION / NOVELTY_UNRESOLVED`  
**System:** `KEYSTONE-MPP-F1`  
**Review date:** 2026-08-29  
**Claim under review:** `C001` and operational claims `K-C1`–`K-C5`

## Decision boundary

This document reconciles the separately owned primary prior-art search and
independent adversarial challenge. It does not amend the immutable intake, sign
a scientific verification event, promote the research-case phase, or certify
novelty. The broad intake claim is retained as the historical hypothesis; the
manuscript must use the narrower working claim below unless later evidence
justifies a revision.

## Reconciled finding

Both searches independently found that broad novelty is not defensible. Prior
work already covers the principal component surfaces:

- probabilistic rollup data-availability sampling (`EIP-7594 / PeerDAS`);
- blockchain threshold decryption after ordering or finalization (`Ferveo`,
  `BEAT-MEV`, and related encrypted-mempool systems);
- scheduled or condition-dependent threshold disclosure with on-chain timing
  and release conditions (`ETHTID`, time-lock systems, and `tTLES`);
- context-isolated threshold decryption (`Context-Dependent Threshold
  Decryption and Its Applications`);
- threshold-decryption accountability, public escalation, and service
  incentives (`Accountability for Misbehavior in Threshold Decryption` and
  cryptoeconomic data-availability committee work);
- proactive/dynamic secret sharing under churn (`Long Live The Honey Badger`);
- verifiable partial decryptions and equality-of-discrete-log proofs (classical
  threshold-encryption and Chaum–Pedersen lineage); and
- timing-sensitive limits on liveness accountability (`Accountable Liveness`).

No single source in the bounded searches was found to combine every element of
the proposed KEYSTONE composition. That negative search result is not proof of
novelty.

## Claim-safe working differentiator

The surviving candidate contribution is deliberately narrow:

> KEYSTONE separates ciphertext data availability from present dispute-key
> serviceability in an encrypted-rollup dispute workflow, then studies a
> pre-authorization, non-production canary partial-decryption audit with
> explicit catastrophic false-accept analysis, temporal and correlated-failure
> qualifications, and a deadline-evidence interface under declared timing
> assumptions.

This is a property, composition, and analysis hypothesis. It is not a new
threshold-encryption, DLEQ, context-dependent decryption, proactive-sharing,
data-availability, bulletin-board, slashing, or key-release primitive.

## Required manuscript language

Use:

- `We formalize a rollup-dispute-specific serviceability property distinct from ciphertext data availability.`
- `We instantiate an internal non-production readiness probe using established verifiable partial-decryption techniques.`
- `We quantify false acceptance and evaluate explicitly scoped correlated and time-evolving failure models.`
- `We record conditional deadline evidence; we do not claim timing-free attribution or unconditional future availability.`

Do not use:

- `first threshold decryption for encrypted AI or rollups`;
- `new context-bound threshold decryption`;
- `new proof of share possession`;
- `new bulletin-board threshold release or slashing mechanism`;
- `proof that a successful audit guarantees future dispute decryption`; or
- `timing-free proof of custodian guilt for non-response`.

## Strongest-predecessor synthesis

| KEYSTONE slice | Strongest recovered predecessor cluster | Reconciled consequence |
|---|---|---|
| Public ciphertext availability | PeerDAS | Treat only as the contrasting property; never claim DAS novelty. |
| Encrypted transaction / AI key release | Ferveo, BEAT-MEV, EigenAI | Narrow to pre-authorization serviceability measurement for disputes. |
| Conditional or scheduled release | ETHTID, decentralized time-lock machines, tTLES, UQ-Vote | Do not claim deadline-bounded authorization or public release logging alone. |
| Context binding | Context-Dependent Threshold Decryption | Describe MPP transcript binding as use of an established security surface, not cryptographic novelty. |
| Accountability and escalation | Threshold traitor tracing, DAC cryptoeconomics, Accountable Liveness | Claim only invalid-response/equivocation evidence and timing-qualified deadline records. |
| Churn and committee maintenance | Long Live The Honey Badger | Correlation-aware audit analysis may be studied; proactive sharing itself is prior art. |
| Partial-decryption correctness | Classical robust threshold encryption and DLEQ lineage | Canary use and serviceability estimand are the candidate composition; the proofs are established tools. |

## Evidence reviewed

Primary-search package:

- `primary-search/search_log.md`
- `primary-search/sources.csv`
- `primary-search/strongest_predecessor_matrix.md`
- `primary-search/primary_novelty_assessment.md`
- reproducibility metadata snapshots under `primary-search/raw/`

Independent challenge package:

- `independent-challenge/challenge_search_log.md`
- `independent-challenge/challenge_sources.csv`
- `independent-challenge/defeating_evidence_matrix.md`
- `independent-challenge/novelty_objections.md`

Root cross-checks included the official or primary landing records for
`EIP-7594`, `Ferveo` (IACR ePrint 2022/898), `Context-Dependent Threshold
Decryption` (IACR ePrint 2025/279), `ETHTID` (arXiv:2107.01600), threshold
traitor tracing (IACR ePrint 2023/1724), DAC cryptoeconomic security
(arXiv:2208.02999), and `BEAT-MEV` (USENIX Security 2025).

Subsequent bounded closure packages now also exist and were reconciled into
this status statement:

- `patent-standards-closure/closure_assessment.md` and its public-source,
  screening, and citation-chain ledgers;
- `independent-patent-code-challenge/challenge_assessment.md`; and
- `independent-citation-audit/citation_audit.md` plus the canonical
  `citation-audit.md` correction pass.

These later packages close the earlier *artifact-absence* gaps for a bounded
public patent/standards search, strongest-predecessor citation chaining, and a
canonical coverage/citation reconciliation. They remain `DRAFT`, bounded, and
unsigned; their existence neither proves novelty nor satisfies independent
scientific verification.

## Residual novelty blockers

Novelty remains `UNRESOLVED` because:

1. the patent/standards and citation-chain closure is intentionally bounded,
   not classification-complete or exhaustive;
2. commercial, proprietary, private-design, and otherwise inaccessible prior
   art was not covered;
3. publisher-page, correction/retraction, and final bibliographic refreshes
   remain required at submission even where Crossref/OpenAlex metadata now
   converges;
4. the narrow differentiator has not received an independently signed
   scientific verification event from an authenticated qualified reviewer;
5. the positive KEYSTONE clauses still require their own formal, simulated,
   prototype, and deadline evidence at the maturity claimed; and
6. a submission-time refresh against the final title, abstract, exact claim
   wording, venue, and current cutoff has not occurred.

## Root disposition

`REFRAME` the broad novelty wording to the claim-safe working differentiator
above. Continue engineering only as preliminary feasibility work. Do not label
the paper novel, phase-promote the research case, or freeze confirmatory claims
until the remaining novelty gates are resolved.
