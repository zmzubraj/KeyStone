Status: `DRAFT / CANONICAL CITATION AUDIT`
System: `KEYSTONE-MPP-F1`
Review date: `2026-08-29`
Disposition ceiling: `NOVELTY_UNRESOLVED`

## Metadata

The supplied citation materials and the preserved Crossref/OpenAlex snapshots
support the reconciled novelty boundary with the following metadata handling:

- `UQ-Vote` is stabilized at the public-registry level: Crossref and OpenAlex
  converge on Jingyu Liu, Jingjing Rao, and Tetsutaro Uehara, IEEE Access,
  2026, volume 14, pages 128905--128916, DOI
  `10.1109/access.2026.3725080`. The conflicting legacy-looking DOI string in
  an earlier accepted-version wrapper is treated as a superseded header
  artifact, not as the canonical record. This does not waive the ordinary
  submission-time metadata refresh.
- `Chosen Ciphertext Secure Public Key Threshold Encryption Without Random
  Oracles` must be treated as `CT-RSA 2006`, DOI `10.1007/11605805_15`, not as
  a 2005 CRYPTO item.
- `Wallet Databases with Observers` needs stable year handling because the
  conference is `CRYPTO '92` while the Springer chapter publication metadata is
  1993.
- a current spot-check of `paper/references.bib:121-172` shows that the earlier
  audit's five named examples `ETHTID`, `Ferveo`, `tTLES`, `Practical Mempool
  Privacy via One-time Setup Batched Threshold Encryption`, and `vetKeys` are
  now present. That named-missing list is therefore inherited audit history,
  not a current local-file fact.

Canonical consequence: the reconciled novelty framing is not yet
bibliography-certified enough for safe manuscript promotion, and this file does
not assert a new exhaustive current missing-source list.

## Claim-source correspondence

Claim-safe correspondence after reconciliation is:

- canonical CSV claim fields use only charter-level `C001`, `C002`, and `C003`
  from `program-charter.md`; the narrower supporting-claim `C003` in
  `novelty-claim-specification.md` and operational `K-C*` IDs are separate
  namespaces used here only as prose cross-references;

- cite `PeerDAS` only as the contrast class for public data or ciphertext
  availability, not as support for dispute-key serviceability;
- cite `EigenAI`, `Ferveo`, `BEAT-MEV`, `Shutterized Optimism`, and Fhenix only
  to show the encrypted-rollup / encrypted-transaction / threshold-release
  design space is already populated;
- cite `ETHTID`, `tTLES`, and `UQ-Vote` only against broad deadline-bounded or
  authorized-release novelty claims;
- cite `Context-Dependent Threshold Decryption and Its Applications` only to
  show context-bound threshold decryption is already prior art;
- cite `Accountability for Misbehavior in Threshold Decryption via Threshold
  Traitor Tracing` and `Accountable Liveness` only to narrow accountability and
  timing claims;
- cite classical threshold-decryption and DLEQ lineage only as established
  building blocks, not as support that the KEYSTONE canary audit is previously
  validated;
- keep the following clauses attached to KEYSTONE's own proofs, simulations, or
  protocol artifacts rather than to related-work citations:
  `present dispute-key serviceability`,
  `pre-authorization non-production canary audit`,
  `catastrophic false-accept analysis`,
  `correlated-failure qualifications`,
  and the `deadline-evidence interface`.

This correspondence preserves the current narrow `REFRAME` and avoids turning
adjacent sources into overclaimed support.

## Corrections and retractions

No correction or retraction signal was reported in the supplied novelty,
challenge, or citation-audit inputs for the cited predecessor set.

That is not a clean external clearance. It only means:

- the bounded supplied audit did not record any correction or retraction event;
- this canonical file cannot certify absence of later corrections because no new
  external refresh was performed in this task.

Canonical handling:

- preserve `DRAFT` status;
- avoid stronger claims than the supplied source package can carry;
- recheck correction or retraction status during any future submission-time
  refresh.

## Access limits

The canonical citation audit inherits the supplied access limits:

- no new browsing or proprietary index access was performed here;
- some source recovery depended on abstracts, metadata, accepted-version pages,
  or official landing pages rather than on stable final publisher copies;
- the `UQ-Vote` public-registry metadata is reconciled, while publisher-page,
  correction/retraction, and final submission-time refreshes remain required;
- the earlier five-item bibliography-gap example list is stale as a current
  local-file statement, and no exhaustive refreshed missing-source list was
  produced in this fix pass;
- the current package is adequate to reject broad novelty wording, but not to
  certify submission-grade citation closure.

Canonical disposition preserved by this file:

- claim framing: `REFRAME`;
- novelty state: `NOVELTY_UNRESOLVED`;
- artifact state: `DRAFT`.
