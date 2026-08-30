DRAFT / PRIMARY_SEARCH
Date: 2026-08-29
System: KEYSTONE-MPP-F1
Claim focus: C001 and frozen claims K-C1 to K-C5
Scope owner: primary prior-art search subagent

# Search contract

This directory records the primary strongest-prior-art search draft for the frozen KEYSTONE claim boundary:

- rollup-specific separation between ciphertext data availability and deadline-bounded authorized threshold decryptability;
- non-production canary readiness sampling with context-bound verification;
- exact false-accept / repeated-audit analysis;
- correlation-aware committee placement and sampling;
- public deadline evidence under declared timing assumptions.

This is a DRAFT evidence package only. It does not phase-promote novelty, feasibility, or manuscript readiness.

# Starting local inputs

Read-only local inputs used to scope the search:

- `research-case/00-governance/program-charter.md`
- `docs/15_PRIOR_ART_BOUNDARY.md`
- `docs/18_LATEST_PRIOR_ART_WATCH_2026-08-29.md`
- `docs/01_RESEARCH_POSITIONING.md`

These files were treated as internal hypotheses and query seeds, not as proof.

# Search date and surfaces

Access date: 2026-08-29

Primary external surfaces actually queried or recovered:

- Crossref API
- OpenAlex API
- arXiv API
- public web search
- official landing pages from EIPs, IEEE/DOI, Springer, USENIX, ACM DL, IACR ePrint where surfaced

Access limits and caveats:

- `eprint.iacr.org` search access through the generic web tool was partially blocked by robots on one query path, so direct known-item pages and public search recovery were used instead.
- Some OpenAlex free-text searches matched full-text noise rather than exact titles; exact `display_name.search` filters or known-item recovery were used where needed.
- IEEE Access metadata for `UQ-Vote` was verified through Crossref and OpenAlex even though the earlier surfaced accepted-version PDF had inconsistent header artifacts.

# Exact search strings and screening notes

## Seed claim searches

1. `"dispute-key availability" threshold rollup`
   - outcome: no direct canonical prior-art hit recovered
   - decision: retain as a zero-hit claim-specific probe, not evidence of novelty

2. `"decryption key availability" encrypted rollup`
   - outcome: no direct canonical prior-art hit recovered
   - decision: retain as a zero-hit claim-specific probe, not evidence of novelty

3. `threshold KMS readiness audit proof of possession`
   - outcome: no directly matching research paper recovered; adjacent threshold-decryption and DLEQ papers surfaced
   - decision: narrowed to verifiable partial decryption / DLEQ / threshold release building blocks

4. `threshold decryption liveness sampling`
   - outcome: no exact match; accountable liveness and blockchain threshold-decryption systems surfaced
   - decision: included `Accountable Liveness`, `UQ-Vote`, and mempool privacy systems as adjacent prior art

5. `share availability proactive secret sharing sampling`
   - outcome: closest credible hit was asynchronous DPSS / proactive sharing under churn
   - decision: included `Long Live The Honey Badger`

6. `encrypted mempool decryption failure availability`
   - outcome: direct adjacent cluster surfaced around `Ferveo`, `Mempool Privacy via Batched Threshold Encryption`, `Practical Mempool Privacy via One-time Setup Batched Threshold Encryption`, `BEAT-MEV`
   - decision: included as strongest blockchain-adjacent threshold-decryption deployment cluster

7. `accountable non-response threshold decryption`
   - outcome: no exact paper with KEYSTONE wording; liveness/accountability papers and consensus-authorized threshold decryption surfaced
   - decision: included `Accountable Liveness` and `UQ-Vote`

8. `proof of retrievability secret share`
   - outcome: no clearly on-point threshold-share operational-readiness paper recovered in this bounded pass
   - decision: left as residual open question for independent challenge

9. `TEE threshold key release liveness`
   - outcome: `EigenAI` recovered as a directly relevant encrypted AI / threshold-released challenge-window system
   - decision: included

## Known-item recovery queries

Recovered or reverified by exact title, identifier, or known-item query:

- `EIP-7594: PeerDAS - Peer Data Availability Sampling`
- `EigenAI: Deterministic Inference, Verifiable Results`
- `Context-Dependent Threshold Decryption and Its Applications`
- `UQ-Vote: Consensus-Authorized Threshold Decryption for End-to-End Verifiable Elections`
- `Long Live The Honey Badger: Robust Asynchronous DPSS and its Applications`
- `Chosen Ciphertext Secure Public Key Threshold Encryption Without Random Oracles`
- `Wallet Databases with Observers`
- `Accountable Liveness`
- `Ferveo: Threshold Decryption for Mempool Privacy in BFT networks`
- `Practical Mempool Privacy via One-time Setup Batched Threshold Encryption`
- `vetKeys: How a Blockchain Can Keep Many Secrets`

Known-item recovery status in this bounded draft: 11 of 11 target items recovered.

# Included sources and why

## Included as strongest or near-strongest predecessors

- `EIP-7594` for public data-availability sampling in rollups
- `EigenAI` for encrypted AI execution with challenge-window threshold-released keys
- `Context-Dependent Threshold Decryption and Its Applications` for cryptographic context isolation of decryption shares
- `UQ-Vote` for consensus-authorized threshold decryption, public logging, and explicit liveness/fault handling
- `Long Live The Honey Badger` for DPSS under churn/faults
- `Chosen Ciphertext Secure Public Key Threshold Encryption Without Random Oracles` for robust threshold decryption and invalid partial-decryption identification
- `Wallet Databases with Observers` for the canonical equality-of-discrete-log proof lineage
- `Accountable Liveness` for formal liveness-accountability limits under synchrony assumptions
- `Ferveo` and the `mempool privacy` cluster for blockchain threshold-decryption deployment and liveness coupling
- `vetKeys` for blockchain-hosted threshold key service adjacency

## Excluded or deprioritized in this draft

- blogs, company explainers, and forum posts without a stronger primary source
- generic threshold-encryption explainers with no stronger overlap than the papers above
- broad rollup privacy papers that did not address threshold decryptability readiness
- non-peer-reviewed search hits that only repeated the title of an included paper

# Backward and forward chaining performed

Backward chaining performed in bounded form:

- `UQ-Vote` reference metadata was checked for older bulletin-board / election / threshold-decryption roots; this confirmed that public log plus threshold release is not a new concept by itself.
- `Accountable Liveness` reference metadata was checked for accountability and BFT-forensics adjacency; this reinforced that timing-dependent blame is an existing formal concern.
- `LightBEAT` and other 2026 threshold-encryption metadata were observed as forward-adjacent surfaces in the blockchain threshold-encryption cluster, showing the area is still active and drift-prone.

Forward-chaining evidence available in this bounded pass:

- OpenAlex showed `Context-Dependent Threshold Decryption and Its Applications` already indexed as a cited conference paper.
- OpenAlex showed `UQ-Vote` indexed as a 2026 IEEE Access article.
- arXiv/OpenAlex evidence showed `Accountable Liveness` moved from preprint to CCS 2025 proceedings.

This is not yet a full citation-graph closure. A differently owned independent novelty challenge is still required.

# Provisional strongest collisions found

1. `PeerDAS` already formalizes probabilistic availability of public rollup data. KEYSTONE cannot claim data-availability sampling.
2. `EigenAI` already combines encrypted AI execution, challenge windows, and threshold-released keys. KEYSTONE cannot claim threshold-released private AI verification as new.
3. `Context-Dependent Threshold Decryption` already makes context isolation of decryption shares a first-class cryptographic object. KEYSTONE cannot claim context binding or share isolation as new.
4. `UQ-Vote` already combines consensus-finalized authorization, threshold decryption, public logs, and liveness/fault scenarios. KEYSTONE cannot claim bulletin-board logging, finalized authorization, or deadline-linked threshold release as independently novel.
5. `Long Live The Honey Badger` already addresses dynamic proactive secret sharing under churn and faults. KEYSTONE cannot claim proactive/dynamic share maintenance.
6. classical threshold-decryption papers already cover verifiable partial decryptions and identification of bad responses. KEYSTONE cannot claim DLEQ-style correctness proof as new.
7. `Accountable Liveness` already formalizes timing-sensitive accountability limits. KEYSTONE cannot claim timing-free blame for non-response.
8. `Ferveo` and the mempool-privacy line already show blockchain threshold-decryption systems with liveness requirements. KEYSTONE cannot claim blockchain threshold decryption as new.

# Surviving bounded differentiator hypothesis

No direct predecessor was recovered in this pass that clearly combines all of the following under one frozen claim:

- a rollup-dispute-specific property separating ciphertext DA from dispute-key serviceability;
- pre-dispute, non-production canary sampling of a private threshold-decryption service;
- exact catastrophic false-accept and repeated-audit analysis tied to that serviceability question;
- correlation-aware placement and sampling as part of the same evidence story; and
- a narrow public deadline-accountability interface tied to the dispute workflow.

This is only a provisional primary-search outcome. Novelty remains unresolved until independent challenge and submission-time refresh.

# Residual uncertainty and open questions

- A direct secret-share proof-of-retrievability or readiness-audit paper may still exist outside the bounded surfaces used here.
- Encrypted-rollup literature is drift-prone; a 2026 or later close collision may surface before submission.
- The strongest composite predecessor may be multi-source rather than a single paper, which weakens any “single-paper novelty” framing but does not by itself defeat a composition claim.
- Patents, proprietary industrial systems, or inaccessible venue copies were not exhaustively cleared in this pass.

# Raw artifacts produced

The following machine snapshots were saved locally:

- `raw/crossref_*.json`
- `raw/openalex_*.json`
- `raw/arxiv_*.xml`

These are untrusted third-party metadata captures used for reproducibility.
