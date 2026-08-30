# DRAFT/PRIMARY_SEARCH — patent-standards-closure search protocol

Access date for this closure pass: 2026-08-29.

Scope:
- bounded extension of the existing primary strongest-predecessor search;
- public patent search;
- public standards / protocol / design-document search;
- deeper backward / forward citation chaining from already recovered strongest predecessors.

Out of scope:
- canonical novelty disposition updates;
- edits to `program-state.json`, claim graph, manuscript, or reconciled matrices outside this folder;
- proprietary databases, private vendor documents, internal patent counsel review, or paywalled full-text retrieval.

Closure question:
- after the primary paper search, do public patents, standards/protocol documents, or citation-lineage evidence supply direct defeating evidence against the narrow residual KEYSTONE/MPP claim family, or do they mainly further weaken broad framing?

Claim surfaces challenged in this pass:
- C001 / K-C1: public ciphertext/data availability versus private dispute-key availability/readiness;
- K-C2: threshold release / dispute-triggered decryption / committee serviceability;
- K-C3: non-production readiness auditing, partial-decryption correctness, DLEQ/PoP-style proof use, invalid-share detection;
- K-C4: proactive/dynamic share maintenance and operational liveness/accountability;
- K-C5: rollup / L2 / blockchain deployment consequences and practical architecture overlap.

Inclusion rule:
- include a source if it materially overlaps at least one of: threshold release conditioned on an event or audit, public logging / bulletin-board release semantics, share retrievability or readiness auditing, rollup/L2 encrypted transaction or decryption architecture, DPSS/share-maintenance lineage, or citation-lineage evidence from strongest predecessors.

Exclusion rule:
- exclude results that are only generic cryptography with no operational overlap, unrelated domains, or noisy search-engine returns that do not bear on KEYSTONE/MPP novelty.

Important limitation:
- zero-hit or no-direct-hit results in this folder are not evidence of novelty. They only show that this bounded public closure pass did not recover a stronger direct public predecessor on that exact wording.

## Search surfaces

1. Google Patents public pages
2. Official/public standards or protocol/design surfaces:
   - Ethereum EIPs
   - Optimism governance technical proposal pages
   - public Fhenix architecture/blog documentation
   - USENIX conference page for DPSS known-item recovery
3. Citation-lineage / metadata surfaces:
   - OpenAlex public API DOI lookups
   - Crossref raw metadata snapshots already captured in `../primary-search/raw/`

## Exact patent queries

- `site:patents.google.com threshold decryption blockchain patent`
- `site:patents.google.com threshold encryption blockchain privacy patent`
- `site:patents.google.com verifiable partial decryption patent`
- `site:patents.google.com secret share availability audit patent`
- `site:patents.google.com "threshold decryption" blockchain "patent"`
- `site:patents.google.com "mempool privacy" threshold decryption patent`
- `site:patents.google.com "threshold key" blockchain secret patent`
- `site:patents.google.com "publicly verifiable secret sharing" patent blockchain`
- `site:patents.google.com "encrypted mempool" patent`
- `site:patents.google.com "threshold services network" patent`
- `site:patents.google.com "challenge window" threshold decryption patent blockchain`
- `site:patents.google.com "public bulletin board" threshold decryption patent`
- `site:patents.google.com "threshold decryption" audit patent`
- `site:patents.google.com "secret share" retrievability patent`
- `site:patents.google.com "proof of retrievability" patent threshold`
- `site:patents.google.com "key availability" threshold patent blockchain`
- `site:patents.google.com "audit procedure" "threshold decryption shares" blockchain`
- `site:patents.google.com "proof-of-retrievability" "secret shares"`

## Exact standards / protocol / design-document queries

- `site:ethresear.ch threshold decryption mempool privacy rollup`
- `site:gov.optimism.io shutterized optimism encrypted mempool`
- `site:fhenix.io FHE rollups threshold decryption network`
- `site:ethresear.ch private optimistic rollup threshold decryption`
- `site:ethresear.ch "threshold decryption" rollup dispute`
- `site:gov.optimism.io "encrypted mempool" "threshold encryption" OP Stack`
- `site:fhenix.io "Threshold Services Network"`
- `site:fhenix.io "threshold decryption" "whitepaper"`
- `site:fhenix.io "FHE Rollups" threshold decryption network`
- `site:fhenix.io "threshold network" decryption requests`

## Exact citation-chain lookups

Known-item DOI / API lookups:
- `https://api.openalex.org/works?filter=doi:10.1109/access.2026.3725080`
- `https://api.openalex.org/works?filter=doi:10.1007/978-981-95-5119-4_16`
- `https://api.openalex.org/works?filter=doi:10.1145/3719027.3765032`
- `https://api.openalex.org/works?filter=doi:10.1007/11605805_15`

Local Crossref snapshot inspection from the already captured public-metadata bundle:
- `../primary-search/raw/crossref_uq_vote.json`
- `../primary-search/raw/crossref_accountable_liveness.json`
- `../primary-search/raw/crossref_mempool_privacy_2025.json`

Known-item recovery checked:
- `EIP-7594: PeerDAS - Peer Data Availability Sampling`
- `Shutterized Optimism – An Encrypted Mempool for the OP Stack`
- `Long Live The Honey Badger: Robust Asynchronous DPSS and its Applications`

## Screening method

For search-engine queries, the logged counts in `screening_log.csv` represent manual review of returned snippets and the subset of opened pages. They are not stable engine-wide hit totals.

For included sources, this pass extracted only source-backed facts needed for closure:
- title / identifier / date / surface;
- direct overlap statement;
- what the source weakens;
- what the source does not prove.

## Principal recovered closure sources

Patents:
- `EP3811560B1` — permissioned blockchain + confidentiality-preserving messaging + threshold decryption shares released to an auditor during an audit procedure;
- `US20170005797A1` — secret-share storage system with periodic proof-of-retrievability challenges against cloud-stored shares;
- `WO2024228005A1` — threshold decryption method with explicit correctness check before decryption.

Standards / design / protocol:
- `EIP-7594` — official PeerDAS standard for public rollup/blob data availability sampling;
- `Shutterized Optimism` — threshold-encryption-based OP Stack / Bedrock architecture with keyper set, DKG, shielded mempool, liveness/finality discussion;
- `FHE Rollups: Scaling Private Smart Contracts on Ethereum L2` — public Fhenix material referencing a threshold decryption network for confidential computation release;
- `Long Live The Honey Badger` USENIX page — known-item recovery for DPSS under churn/faults.

Citation-chain anchors:
- `UQ-Vote`;
- `Context-Dependent Threshold Decryption and Its Applications`;
- `Accountable Liveness`;
- `Weighted Batched Threshold Encryption With Applications to Mempool Privacy`;
- `Chosen Ciphertext Secure Public Key Threshold Encryption Without Random Oracles`.

## Residual limits after this closure pass

- patent coverage remains bounded to public Google Patents discovery and directly accessible public pages;
- no Espacenet, Lens, USPTO full-classification review, or patent-attorney claim construction was performed;
- private or unpublished rollup/vendor designs may still exist;
- early citation counts in OpenAlex are incomplete for 2025–2026 items;
- citation chaining here is sufficient to show lineage crowding, not to prove exhaustive closure of all descendants.
