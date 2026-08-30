Status: `DRAFT / SUBMISSION-TIME NOVELTY REFRESH`
System: `KEYSTONE-MPP-F1`
Refresh date: `2026-08-30`
Prior canonical cutoff: `2026-08-29`
Current disposition ceiling: `NOVELTY_UNRESOLVED`

## Purpose

This artifact is the submission-phase refresh required by
`research-case/artifact-registry.csv` for
`09-submission/novelty-refresh.md`. It updates the bounded prior-art record
through `2026-08-30` without changing program state, certifying novelty, or
replacing the independently signed novelty challenge.

This file is not an independent review, not a verification event, and not a
phase-promotion artifact.

## Inputs reviewed

Local canonical novelty inputs:

- `01-novelty/search-protocol.md`
- `01-novelty/search-coverage.csv`
- `01-novelty/novelty-matrix.csv`
- `01-novelty/citation-audit.md`
- `07-manuscript/manuscript.md`

Current-source refresh surfaces checked on `2026-08-30`:

1. `EIP-7594: PeerDAS - Peer Data Availability Sampling`
   (`https://eips.ethereum.org/EIPS/eip-7594`)
2. `EIP-8371: RowDAS - Distributed Blob Reconstruction`
   (`https://eips.ethereum.org/EIPS/eip-8371`)
3. `Balancing Privacy and Compliance in DeFi: A Zero-Knowledge-Based Auditable Cross-Chain Framework`
   (`https://arxiv.org/abs/2608.15276`)
4. `Accountable Liveness`
   (`https://doi.org/10.1145/3719027.3765032`)
5. `Context-Dependent Threshold Decryption and Its Applications`
   (`https://doi.org/10.1007/978-981-95-5119-4_16`)
6. `UQ-Vote: Consensus-Authorized Threshold Decryption for End-to-End Verifiable Elections`
   (`https://doi.org/10.1109/ACCESS.2026.3725080`)
7. `ETHTID: Deployable Threshold Information Disclosure on Ethereum`
   (`https://arxiv.org/abs/2107.01600`)

## Current-source observations

| Source | Current fact confirmed on 2026-08-30 | Pressure on KEYSTONE |
| --- | --- | --- |
| EIP-7594 | Final Ethereum standards-track core EIP created `2024-01-12`; it formalizes peer data-availability sampling for blob data and gives withholding-probability analysis for public DA sampling. | This continues to defeat any broad KEYSTONE wording that sounds like data-availability sampling itself is novel. |
| EIP-8371 | Draft Ethereum networking EIP created `2026-08-05`; it extends the PeerDAS line toward distributed blob reconstruction and explicitly depends on `EIP-7594`. | This further separates public DA / reconstruction engineering from KEYSTONE's narrower dispute-key serviceability question; it does not rescue a broad availability claim. |
| arXiv:2608.15276 | New arXiv paper posted `2026-08-15` combines ZK proofs, threshold cryptography, and authorized threshold view-key access for auditable cross-chain compliance. | This is not a direct rollup dispute-readiness predecessor, but it increases crowding around authorized threshold-audit access narratives and weakens any broad “auditability + threshold access” novelty framing. |
| Accountable Liveness | Current DOI metadata resolves to CCS 2025 and preserves timing-qualified liveness/accountability as a live prior-art surface. | KEYSTONE cannot claim timing-free accountability or deadline accountability as a primitive contribution. |
| Context-Dependent Threshold Decryption | Current Springer/DOI metadata resolves to ASIACRYPT 2025; the paper explicitly introduces context as a threshold-decryption argument that isolates shares across contexts. | KEYSTONE must continue to treat context-bound partial-decryption transcripts as adopted machinery, not a new decryption primitive. |
| UQ-Vote | Current Crossref and OpenAlex metadata converge on IEEE Access 2026, volume `14`, pages `128905-128916`, DOI `10.1109/access.2026.3725080`. | This stabilizes the authorization/workflow predecessor reference and keeps consensus-authorized threshold decryption clearly inside prior art. |
| ETHTID | Current arXiv/BCCA metadata still supports an Ethereum threshold-disclosure coordination predecessor with on-chain coordination and deployability framing. | KEYSTONE cannot claim first Ethereum threshold-release coordination or generic on-chain threshold-release novelty. |

## Resulting novelty position

The `2026-08-30` refresh does not uncover evidence that rescues broad
novelty. Instead, it reinforces the earlier `REFRAME` and keeps the canonical
ceiling at `NOVELTY_UNRESOLVED`.

The strongest safe position after this refresh remains:

- broad primitive novelty: rejected;
- broad rollup / threshold-release / auditable-decryption novelty: rejected;
- public or ciphertext-oriented data-availability novelty: rejected;
- timing-free accountability novelty: rejected;
- current narrow candidate: at most a dispute-specific, pre-authorization,
  non-production serviceability-audit composition with explicit false-accept,
  correlation, and selective-withholding qualifications;
- even that narrow candidate remains `UNRESOLVED` pending independent
  submission-time challenge and strongest-predecessor reconciliation.

## Manuscript impact

`07-manuscript/manuscript.md` must continue to obey all of the following:

1. distinguish ciphertext/public DA from dispute-key serviceability;
2. treat threshold decryption, DLEQ-style proofing, context binding,
   authorization workflows, and timing-qualified accountability as inherited
   building blocks;
3. preserve selective withholding as a central negative result and limitation;
4. avoid any wording that implies KEYSTONE is the first threshold-release
   system, first auditable threshold-access design, or first rollup/L2
   threshold-decryption architecture;
5. keep all novelty language below `NOVELTY_SURVIVES` and below any
   manuscript claim that would require independent closure not yet present.

## Access limits and residual uncertainty

- This refresh used bounded public sources only; it is not a proprietary or
  exhaustive scholarly-database search.
- A live OpenAlex metadata retry hit `HTTP 429` during this refresh window, so
  the final metadata stabilization for `UQ-Vote` relied on a successful later
  OpenAlex retry plus Crossref convergence rather than a single uninterrupted
  query path.
- No private design documents, unpublished implementations, or subscription-only
  venue databases were added here.
- `EIP-8371` is still a draft networking EIP and should be treated as live
  prior-art pressure rather than stable accepted literature.
- Absence of a direct, perfect predecessor in this bounded refresh is not proof
  that the remaining narrow candidate survives novelty attack.

## Required next action

Before any honest submission-readiness claim:

1. rerun the independent novelty challenge against this updated cutoff;
2. reconcile any manuscript wording that still overstates novelty;
3. carry the refreshed cutoff and residual uncertainty into
   `09-submission/submission-audit.md` and
   `09-submission/acceptance-readiness.md`.
