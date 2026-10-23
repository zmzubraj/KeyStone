# R2 paper integration plan (draft for author approval)

Date: 2026-10-23. Base: commit `55f5d93`. Target: `paper/jcs/KEYSTONE_JCS.tex` and the submission package.
Decisions D5 and D6 of the R2 freeze apply: Definition 7 moves to PAC+, and the W1 result enters as a theorem.

## 1. Constraints

| Constraint | Now | Limit |
|---|---|---|
| Words (pdftotext of the full PDF, the measure used so far) | 10,807 | 11,000 |
| Cited references | 45 | 45 |
| Abstract | 185 words | unchanged length target |
| Evidence labels | exact, simulation, microbenchmark, emulation | R2 additions also carry an "R2" label |
| House style | no em dashes, Sage `sagej` class, anonymized build identical to standalone | same |

Headroom is about 190 words, so every addition must be paid for by a cut.

## 2. What enters the paper

| # | Change | Where | Words (net) |
|---|---|---|---|
| A1 | Definition 7 (DKA) requires PAC+ instead of PAC | Sec. 4 | +10 |
| A2 | PAC+ for the TDH2 instantiation: lemma with proof sketch (TDH2 chosen-ciphertext security with the record label, custodians refuse invalid or unauthorized ciphertexts; canary path unchanged, so Lemma 2 still holds). Replace "our prototype implements the plain KEM" | Sec. 5.2 | +150 |
| A3 | W1 theorem: exact posterior risk by forward recursion (Theorem 3 of W1-THEOREMS.md), all-accepted limit (Prop. 4), closed-form bound and frequency floor (Thm 5, Cor. 6), design rule for the audit interval. Proof sketches in the paper | new Sec. 6.3 "Readiness over time" | +600 |
| A4 | Q3 testbed rewritten on R2: ristretto255 + TDH2, verification off the event loop, primary endpoint by Delta_d_star, SERIAL vs BATCH, audit versus exact expectation; R1 kept only as a comparison column (median about 3.8 s vs 0.1 to 0.6 s). Report the D0 negative finding (0/300: host IPC overhead not in the formula) and D4 at 94.7 to 97.3% | Sec. 7.3, Table t4b replaced | +60 (replaces 330) |
| A5 | Q4 microbenchmark: ristretto255 next to ffdhe2048/3072 (verify 0.15 ms vs 48 ms; batch 0.93x on this host) | Sec. 7.4, Table t6 replaced | +80 |
| A6 | New Q5: temporal results on the synthetic grid. One compact table of selected cells (no shock vs domain shocks; metrics 1 and 2; floor; largest interval for 1e-3 and 1e-4) and one sentence on the simulation check (32 of 33 inside 99% Wilson; the miss investigated) | new Sec. 7.5 + table | +300 |
| A7 | Discussion, validity, conclusion: domain shocks dominate risk; floor means "audit more often" can be useless; bigger samples are not uniformly better under shocks; D0 deadline-formula limitation; W1 parameters synthetic; AI-assisted proofs need independent review (internal note, not paper text) | Secs. 8, 10, 11 | +120 |
| A8 | Abstract and introduction contributions list updated (TDH2/PAC+, temporal theorem, R2 testbed) | front | +40 |
| A9 | W11 sentence: standard hash-to-group (RFC 9496 / RFC 9380) | Sec. 5 | +30 |
| | **Total additions** | | **about +1,390** |

New references needed: RFC 9496 (ristretto255) and RFC 9380 (hash to curve). Each needs a swap to stay at 45.

## 3. Cuts to pay for it (recommended set)

| # | Cut | Saves |
|---|---|---|
| C1 | Related work tightened from 866 words (merge two paragraphs, shorten the comparison-table notes) | 250 |
| C2 | Full proofs of Lemmas 1 to 3 shortened to sketches; full proofs move to the online supplement (anonymized artifact) | 250 |
| C3 | Gas table (t8) and its paragraph move to the supplement; one sentence remains | 150 |
| C4 | Analysis: Stratified-sample proposition and the two observations compressed | 150 |
| C5 | System model and preliminaries tightened | 150 |
| C6 | Introduction tightened | 100 |
| C7 | Q2 robustness and Discussion tightened | 150 |
| C8 | Two least-load-bearing references swapped for RFC 9496 and RFC 9380 | 0 words, keeps 45 |
| | **Total cuts** | **about 1,200** |

Additions minus cuts is about +190, which uses the current headroom. The target is a final count of 10,950 or less, with a margin for the R2 numbers macros.

## 4. Assets and provenance

1. `derive_assets.py` gains R2 builders that read only committed R2 files:
   `results/r2/microbench-summary.csv`, `results/r2/deadline/deadline-summary.csv`,
   `results/r2/temporal/{exact-grid,design,sim-check}.csv`. It writes `tables/t4b_testbed.tex` (R2),
   `tables/t6_operations_r2.tex`, `tables/t9_temporal.tex` and R2 macros into `tables/jcs_numbers.tex`.
   No number is typed by hand.
2. Each R2 table caption carries its label (EMULATION, MICROBENCHMARK, EXACT_UNDER_DECLARED_SYNTHETIC_MODEL)
   and the freeze hash prefix.
3. R1 assets stay untouched; the R1 testbed is cited only as the comparison column.

## 5. Order of work and checks

1. Build the R2 assets (step 4), and check every macro against the CSVs with a small test.
2. Make edits A1 to A9, then cuts C1 to C8, section by section, rebuilding after each section.
3. QA pass:
   - LaTeX build with no undefined references or citations.
   - Word count of 11,000 or less, exactly 45 cited references.
   - No em dashes.
   - The anonymized build is text-identical to the standalone build.
   - The identity scan is clean.
   - Every number in the text traces to an R2 or R1 file.
4. Rebuild the submission package (`make_submission.sh`): anonymized PDF, source zip and artifact zip. The artifact gains
   the R2 code, results, W1-THEOREMS.md and the deviation log, and loses the governance files as before.
5. An independent AI cold read of the changed sections, then the human expert read-through, which is still the gate
   before submission (submission itself stays with the author).

## 6. Decisions for the author

1. Cut strategy: the recommended set C1 to C8, which moves the full proofs of Lemmas 1 to 3 and the gas table to the
   supplement, or keep the proofs in the paper and cut related work and evaluation harder.
2. R1 testbed: keep it as a comparison column (recommended), or drop it.
3. BATCH variant: one sentence plus a table column (recommended), or a sentence only.
4. W1 proofs: sketches in the paper and full proofs in the supplement (recommended), or full proofs in an appendix,
   which needs about 600 more words of cuts.
