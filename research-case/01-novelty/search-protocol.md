Status: `DRAFT / CANONICAL NOVELTY SEARCH PROTOCOL`
System: `KEYSTONE-MPP-F1`
Review date: `2026-08-29`
Disposition ceiling: `NOVELTY_UNRESOLVED`

## Surfaces

This canonical protocol reconciles the supplied novelty materials without
changing program state. The bounded public surfaces already searched in the
input package were:

- live metadata queries recorded in `prior-art-query-log.json` against
  `arxiv_api` and `openalex_works`;
- primary-search package:
  `primary-search/search_log.md`,
  `primary-search/sources.csv`,
  `primary-search/strongest_predecessor_matrix.md`,
  `primary-search/primary_novelty_assessment.md`;
- independent novelty challenge package:
  `independent-challenge/challenge_search_log.md`,
  `independent-challenge/challenge_sources.csv`,
  `independent-challenge/defeating_evidence_matrix.md`,
  `independent-challenge/novelty_objections.md`;
- independent citation audit package:
  `independent-citation-audit/citation_audit.md`,
  `independent-citation-audit/claim_source_matrix.csv`,
  `independent-citation-audit/mischaracterization_risks.md`;
- patent and standards closure package:
  `patent-standards-closure/search_protocol.md`,
  `patent-standards-closure/sources.csv`,
  `patent-standards-closure/patent_standards_matrix.md`,
  `patent-standards-closure/closure_assessment.md`;
- independent patent/code challenge:
  `independent-patent-code-challenge/challenge_assessment.md`;
- reproducibility metadata:
  `prior-art-raw-snapshots.json` and `prior-art-dedup-report.json`.

These sources are sufficient to reject broad novelty framing, preserve the
working `REFRAME`, and keep novelty at `NOVELTY_UNRESOLVED`. They are not
sufficient to certify novelty survival.

Canonical namespace rule for this six-artifact package:

- CSV `claim_id` and `claim_ids` fields use only the charter-level IDs `C001`,
  `C002`, and `C003` from `research-case/00-governance/program-charter.md`;
- the narrower supporting-claim `C003` in
  `research-case/01-novelty/novelty-claim-specification.md` and operational
  `K-C1` through `K-C6` are separate namespaces and appear here only as prose
  cross-references.

## Queries

The canonical live query set is the exact 12-query bundle recorded in
`prior-art-query-log.json`. The six semantic query families were:

1. `dispute key availability threshold decryption rollup`
2. `pre authorization threshold decryption readiness audit canary`
3. `threshold decryption liveness blockchain`
4. `secret share retrievability audit`
5. `context dependent threshold decryption`
6. `accountable liveness threshold decryption`

Each family was executed once against `arxiv_api` and once against
`openalex_works`, yielding 12 logged queries total. All 12 raw responses are
present under `prior-art-raw/`, and each returned 5 records in the captured
snapshot.

Supplemental known-item recovery, reconciliation, and closure work came from
the supplied folders rather than new web research. The strongest recovered
predecessor cluster includes:

- `EIP-7594` / `PeerDAS`;
- `EigenAI`;
- `Ferveo`;
- `BEAT-MEV`;
- `Context-Dependent Threshold Decryption and Its Applications`;
- `UQ-Vote`;
- `Deployable Threshold Information Disclosure on Ethereum`;
- `Time-Lock Encrypted Storage for Blockchains`;
- `Accountability for Misbehavior in Threshold Decryption via Threshold Traitor Tracing`;
- `Accountable Liveness`;
- `Long Live The Honey Badger`;
- `Chosen Ciphertext Secure Public Key Threshold Encryption Without Random Oracles`;
- `Wallet Databases with Observers`;
- patent and design-doc pressure from `EP3811560B1`, `US20170005797A1`,
  `US20240354753A1`, `Shutterized Optimism`, Fhenix threshold-network
  documentation, and Optimism fault-proof security documentation.

Zero-hit or noisy query wording was retained as search log evidence only. It is
explicitly non-evidence for novelty.

## Screening

Screening followed the reconciled rule set from the supplied primary,
independent, and closure materials:

- include a source if it materially overlaps at least one claim slice around
  public ciphertext availability, authorized threshold release, context-bound
  threshold decryption, threshold-decryption accountability, share-readiness or
  retrievability auditing, correlation-aware committee behavior, or rollup/L2
  threshold-decryption deployment;
- keep exact-phrase misses, noisy free-text returns, and open questions in the
  query ledger, but mark them as non-evidence;
- preserve broad novelty rejection and the narrow working `REFRAME`;
- do not upgrade beyond a property/composition/analysis hypothesis unless a
  direct predecessor gap survives all remaining closure work.

Result counts in `search-coverage.csv` reflect the raw snapshot return counts.
Screened counts reflect manual review of all returned records in the bounded
live-query pass. Because the query strings were broad and often noisy,
inclusion decisions depend heavily on known-item recovery and cross-package
reconciliation rather than on free-text rank position alone.

## Citation chaining

The canonical reconciliation preserves the bounded citation work already
performed in the input package:

- backward chaining from `UQ-Vote` to older bulletin-board / threshold-release
  lineage;
- backward and conceptual chaining from `Accountable Liveness` to timing-aware
  accountability limits;
- forward-adjacent pressure from encrypted-mempool and threshold-decryption
  lines tying together `Ferveo`, `Shutter`, `vetKeys`, and `BEAT-MEV`;
- patent and standards closure known-item recovery for `EP3811560B1`,
  `US20170005797A1`, `EIP-7594`, `Shutterized Optimism`, and Fhenix threshold
  network documentation.

Citation chaining in this canonical file is sufficient to show a dense,
composite prior-art frontier. It is not a full submission-grade graph closure.

## Access limits

The reconciled package retains the stated access limits from the supplied
artifacts:

- some `eprint.iacr.org` discovery paths were partially blocked, so known-item
  pages and public metadata recovery were used instead of full search coverage;
- OpenAlex free-text results were often noisy and required known-item recovery
  or exact-title interpretation;
- `UQ-Vote` is now stabilized at the public-metadata level by matching Crossref
  and OpenAlex records for DOI `10.1109/access.2026.3725080`, IEEE Access
  volume 14, pages 128905--128916; the conflicting DOI string in an earlier
  accepted-version wrapper is treated as a superseded header artifact, while a
  normal submission-time publisher refresh remains required;
- patent coverage is bounded to public Google Patents / WIPO visibility in the
  supplied materials and is not an exhaustive classification review;
- no proprietary scholarly databases, private design documents, internal vendor
  systems, or unpublished implementations were searched;
- absence of a direct hit in the bounded searches is not proof of novelty.

## Cutoff

Canonical novelty cutoff for this draft reconciliation: `2026-08-29`.

This file preserves the current novelty state only:

- broad novelty: rejected;
- working disposition: `REFRAME`;
- canonical novelty verdict: `NOVELTY_UNRESOLVED`;
- registration status for downstream systems: `DRAFT` only.
