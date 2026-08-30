# Mischaracterization Risks

Status: `DRAFT_INDEPENDENT_CITATION_AUDIT`
Date: `2026-08-29`

## Critical

1. `paper/references.bib` does not contain several strongest predecessors already named in `novelty_reconciliation.md` and `docs/15` / `docs/18`. Missing at minimum in this audit: `ETHTID`, `Ferveo`, `tTLES`, `Practical Mempool Privacy via One-time Setup Batched Threshold Encryption`, and `vetKeys`.

2. `UQ-Vote` is citation-usable only with caution. The accessible accepted-version page exposes conflicting DOI strings inside the visible copy. The wrapper presents `10.1109/ACCESS.2026.3725080`, but the visible accepted-version text also includes `10.1109/ACCESS.2024.0429000`. Do not present it as fully bibliographically settled until IEEE Xplore is independently confirmed.

3. Any sentence implying that KEYSTONE newly provides `context-bound threshold decryption`, `share isolation by context`, or equivalent is directly contradicted by `Context-Dependent Threshold Decryption and its Applications`.

4. Any sentence implying timing-free guilt, unconditional slashability, or guaranteed future decryptability after a successful readiness audit is contradicted by the accountable-liveness boundary and by the narrow wording already adopted in reconciliation.

## High

5. `primary-search/sources.csv` misstates the Boneh-Boyen-Halevi threshold-encryption paper as `2005` and `CRYPTO / Springer`. The authoritative Springer page shows `CT-RSA 2006`. If this row is copied into manuscript materials unchanged, it becomes an avoidable citation error.

6. The current reconciled wording is safe only if the paper clearly separates:
   - adopted primitives and prior-art systems, from
   - KEYSTONE's own property/protocol/analysis claims.
   If those are merged in prose, the paper will sound broader than the evidence supports.

7. `docs/18_LATEST_PRIOR_ART_WATCH_2026-08-29.md` introduces two extra surviving-claim elements not present in `novelty_reconciliation.md`: `explicit measurement of the selective-withholding gap` and `a reproducible encrypted-AI-rollup dispute prototype`. That drift can silently broaden the claim boundary if reused in abstract or intro drafting.

8. `EigenAI` is adjacent prior art, not proof that KEYSTONE's exact serviceability question is solved elsewhere. Overstating it as a direct predecessor to the exact readiness-audit claim would also be inaccurate.

## Medium

9. `Wallet Databases with Observers` has a conference/book year convention issue (`CRYPTO '92` versus Springer publication metadata `1993`). Choose one bibliography convention and keep it consistent.

10. `ETHTID`, `tTLES`, and `UQ-Vote` support conditional authorization and release boundaries, but they do not by themselves validate the exact KEYSTONE property `present dispute-key serviceability`. If the manuscript cites them as if they do, the claim will be overstated.

11. The narrowed sentence in `novelty_reconciliation.md` is a claim-safe framing, not a proof-complete contribution statement. Without theorem/experiment anchors, even that narrower wording will still read as aspirational.

## Safest immediate corrections

- Keep all positive KEYSTONE clauses in `we define / we propose / we analyze / we evaluate` form.
- Add the missing bibliography entries before drafting literature-sensitive sections.
- Treat `UQ-Vote` as metadata-sensitive until the final IEEE record is checked.
- Do not let `docs/18` broaden the reconciled claim without a fresh novelty review.
