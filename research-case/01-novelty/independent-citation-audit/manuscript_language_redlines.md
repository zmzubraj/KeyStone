# Manuscript Language Redlines

Status: `DRAFT_INDEPENDENT_CITATION_AUDIT`
Date: `2026-08-29`

These are redlines for future manuscript prose. They are not file edits.

## Core contribution sentence

Unsafe:

- `KEYSTONE is the first protocol to prove dispute-key availability for encrypted AI rollups.`

Safer:

- `KEYSTONE defines a rollup-dispute-specific serviceability property distinct from ciphertext data availability and studies one candidate readiness-audit construction for that setting.`

Reason:

- `first` is not supported by the current novelty package.

## Context binding

Unsafe:

- `We introduce a new context-bound threshold decryption mechanism.`

Safer:

- `We bind audit transcripts to a dispute context while treating context-dependent threshold decryption as prior art.`

Required citations:

- `Context-Dependent Threshold Decryption and its Applications`

## Partial decryptions / DLEQ

Unsafe:

- `We develop a new proof of valid share possession.`

Safer:

- `Our audit path uses established verifiable partial-decryption techniques and equality-of-discrete-log proof lineage in a non-production readiness probe.`

Required citations:

- `Chosen Ciphertext Secure Public Key Threshold Encryption Without Random Oracles`
- `Wallet Databases with Observers`

## Deadline evidence and blame

Unsafe:

- `Missed deadlines prove which committee members are guilty.`

Safer:

- `The interface records timing-qualified deadline evidence for invalid responses, equivocation, and conditional deadline misses under the stated delivery assumptions.`

Required citations:

- `Accountable Liveness`
- adjacent system/accountability citations as needed

## Authorization / bulletin board

Unsafe:

- `We introduce consensus-authorized threshold release with a public bulletin board.`

Safer:

- `We reuse consensus-finalized authorization and public logging as established design surfaces and focus our claim on dispute-readiness measurement before authorized reveal.`

Required citations:

- `UQ-Vote`
- `ETHTID`
- `tTLES`

## Availability distinction

Unsafe:

- `Data availability sampling does not address key availability, which we prove here.`

Safer:

- `PeerDAS and related schemes address public data availability; KEYSTONE separately defines a private decryption-serviceability property for authorized disputes.`

Required citations:

- `EIP-7594`

Note:

- The second clause still needs KEYSTONE's own formal definition and evidence.

## Canary audit

Unsafe:

- `Prior work already shows that canary audits establish current decryption readiness.`

Safer:

- `We propose a non-production canary partial-decryption audit as one way to exercise a current service path without revealing production plaintext.`

Note:

- No direct predecessor or validating source for this exact move was recovered in this bounded audit.

## Correlation and false acceptance

Unsafe:

- `Our correlation-aware audit is standard in the literature.`

Safer:

- `We analyze catastrophic false acceptance and correlated-failure effects under an explicit committee and timing model.`

Note:

- This is a self-claim and must point to theorem/figure/table evidence.

## Literature section warning

Do not write any related-work sentence that implies:

- context isolation is new;
- threshold-decryption accountability is new;
- on-chain deadline-conditioned release is new;
- PBFT-finalized authorization is new; or
- a successful audit guarantees future decryptability without model qualifications.
