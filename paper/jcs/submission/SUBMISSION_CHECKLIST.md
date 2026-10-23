# KEYSTONE → Journal of Computer Security: submission package

Portal: https://mc.manuscriptcentral.com/j-cs (ScholarOne). Journal: https://journals.sagepub.com/home/JCU

## Files to upload

| ScholarOne file type | File | Notes |
|---|---|---|
| Main document (anonymized) | `../KEYSTONE_JCS.pdf` | No author names, affiliation, email or repository link |
| LaTeX source (if requested) | `KEYSTONE_JCS_source.zip` | Flattened source: main .tex, sagej.cls, endnotes.sty, tables, figures, .bib, .bbl |
| Title page (not sent to reviewers) | `Title_Page.docx` / `Title_Page.pdf` | ORCID and postal address filled in (2026-10-21) |
| Cover letter | `Cover_Letter.docx` / `Cover_Letter.pdf` | Dated 21 October 2026; update if you submit later; confirm the editors' names on the live journal page |
| Supplementary material (for review) | `KEYSTONE_supplement_anonymized.pdf` | Full proofs (Lemmas 1 to 4, Theorems 2 and 3, Proposition S1), Figures S1 and S2, Tables S1 to S3 (scalability, gas, related-work comparison) |
| Supplementary material (for review) | `KEYSTONE_artifact_anonymized.zip` | R1 and R2 code, frozen designs, deviation logs, raw results; regenerates every table, figure and number |

## Values to enter in ScholarOne

- Article type: Research article
- Title: KEYSTONE: Readiness Audits for Dispute-Key Availability in Encrypted Rollups
- Abstract: copy from the manuscript (193 words in the rendered PDF; limit 150 to 200)
- Keywords: Dispute-key availability; threshold decryption; encrypted rollups; readiness audit; acceptance sampling; selective withholding
- Counts: 10,974 words in the whole PDF incl. references, tables and figure labels; 23 pages, 2 figures, 7 tables, 45 references; supplement 8 pages (Tables S1 to S4)
- Funding: none. Conflicts: none.
- Preprint: none on a preprint server (an earlier draft is in the public GitHub repository; this is disclosed in the cover letter)
- Suggested reviewers: not accepted by this journal

## Human-only steps (Claude does not do these)

1. Create or sign in to the ScholarOne account; link ORCID.
2. Check the title page details (affiliation, postal address, ORCID) and the cover-letter date.
3. Confirm that every declaration is true, especially "not under consideration elsewhere".
4. Get one human expert read-through (decision recorded 2026-10-14: package prepared, submit held until then).
5. Upload, review the system-built PDF proof, and press Submit.

## Known deviations and open items

- Reference style: `sagev` (numbered, superscript) with `unsrtnat.bst`, because `SageV.bst` was not in the obtained template bundle. Sage reformats references in production.
- `times` class option omitted (Helvetica metrics not installed); Computer Modern fonts are used.
- LNCS volume numbers were omitted where they could not be verified; DOIs are given instead.
- Research-program gate: KEYSTONE program state remains INTAKE / novelty UNRESOLVED. Preparing this package does not change that state.

## Self-review record (2026-10-14)

- An AI referee pass (fresh context) recommended MAJOR REVISION on the first draft; all eight must-fix items were then addressed and a second AI pass verified them. AI review is a quality check, not independent peer review.
- Security finding disclosed in the paper (Proposition: malleability across records): the plain threshold KEM in the prototype lets a party that obtains the release of a record it submits recover another record's key. The paper claims only audit-level confidentiality (PAC) for the prototype and states that releases must be bound to their record (e.g. TDH2) in deployment. The public R1 draft on GitHub does not contain this caveat.
- Encrypted-mempool keyper liveness (2026-10-21): FairBlock (SecureComm 2022) and F3B (AFT 2023) added with verified records; Shutter left out because only blog, press and forum sources exist.
- No new experiments were run; evaluation limits (single host, pure Python, 2 s primary deadline not met) are stated in the paper.
- JCS-specific derived assets (Table 4 header, Figure 4b axis label) are produced by `derive_assets.py`; R1 assets are unchanged.
- Rebuild the bundle with `make_submission.sh <anonymized-artifact-dir>`.

## Condensed revision (2026-10-21)

- Pages 30 -> 23; main text ~11,250 -> ~8,850 words; references 63 -> 39; abstract unchanged (188 words).
- Removed: the properties table (it repeated the definitions), forced page breaks, and 24 peripheral references. All definitions, lemmas, theorems, propositions and proofs are kept.
- Previous full version kept outside the repo as a backup; rebuild the bundle with `make_submission.sh <anonymized-artifact-dir>`.

## Expert-review revision, Group A (2026-10-21)

Review: `paper/jcs/reviews/expert_review_2026-10-21.md` (AI cold read; not independent peer review).
- Leak fixed: governance tests/scripts, the authorization record and its deviation-log row removed from the artifact; freeze file unchanged; all remaining tests pass; assets reproduce byte-identically.
- W6: exact operating characteristic (Table `tab:oc`), margin-based single-audit sizes, Wald SPRT sizes; generated by `oc_analysis.py` (also in the artifact).
- W2/W14: canary shares credited to threshold coins (Cachin et al.) and threshold BLS (Boldyreva); CHURP and Wald added; trivial results demoted to Observations.
- W9: prototype contract's admin-chosen sample disclosed. W4(b): scope narrowed to non-strategic faults. W7: timescale and cross-epoch remark.
- W10: simulation cells framed as implementation checks; exact sign test reported. W12: title and framing no longer AI-specific or "Auditable".
- W13: static corruption, share pooling, self-declared domains, trust-model change stated. W15: Table 4 split, deadline figure and withholding panel replaced by tables, process vocabulary trimmed, non-independent design review disclosed.
- Next: Group B (W1 temporal theorem, W3 TDH2, W5 EC core + testbed rerun, W11 hash-to-group); needs a design amendment before any new experiment.

## R2 integration (2026-10-23)

Plan: `paper/jcs/reviews/R2-PAPER-INTEGRATION-PLAN.md` (author approved all recommendations).
- Added: Lemma 4 (record-bound releases, PAC+ with record-labeled TDH2; the KEM form of TDH2 is stated as an assumption); Definition 7 now requires PAC+; Section 6.3 "Readiness over time" (Theorems 2 and 3, accepted-run limit, floor F0, longest admissible interval); R2 testbed (Q3), R2 costs (Q4), temporal results (Q5).
- Reported negative result: the primary deadline Delta_d* missed on D0-CONTROL (0/300) because the formula omits host overhead; D4 met it in 97.3% (serial) and 94.7% (batch).
- Moved to the supplement: full proofs of Lemmas 1 to 3, Figures 2 and 6, scalability, gas and related-work tables. RFC 9496 added; EIP-7594 dropped (45 references).
- All R2 numbers come from `paper/jcs/r2_assets.py`; the artifact reproduces the R2 tables and the deadline summary byte-identically, and its 89 R2 tests pass.
- Artifact anonymization: R2 authorization record omitted (its line removed from `r2-design-freeze.SHA256SUMS`); git commit ids in environment and provenance records and in the deviation log redacted.
- RESOLVED 2026-10-23 (author: keep): `r2-design-freeze.json` and the design draft it hashes cite the full base commit of the public repository. They cannot be changed without breaking the hash checks. A reviewer could search GitHub for that commit and find the repository. Choose: keep (the cover letter already discloses the public draft) or ship R2 design files only after review.
- Human gates unchanged: the expert read-through must cover the new proofs, all drafted with AI assistance: Definition 6 (PAC), Assumption 5, Lemma 4, Corollary 2 (stochastic deadline), Theorems 2 and 3, and their supplement proofs. The AI-use declaration must stay true.
- AI cold read of the R2 changes and the fixes: `paper/jcs/reviews/cold_read_R2_2026-10-23.md` (3 must-fix, 7 should-fix, 7 minor; all addressed). Notable: Definition 6 (PAC) is now plaintext indistinguishability, because the earlier key-indistinguishability form was trivially winnable; Assumption 5 states TDH2's KEM security; Theorem 3 now proves U monotone and never below its floor (deviation entry 9).

## Deadline diagnosis and R2b replication (2026-10-23)

- B (post hoc, labelled): Corollary 2 (stochastic deadline: Pr[success] >= Pr[Bin(n_live, p F(Delta - B)) >= t]) and `predict_r2_deadline.py`. With frozen parameters it predicts 96.3% for the ten-crash profile; R2 observed 97.3% (serial) and 94.7% (batch).
- C (calibration, design logged before running): null transport 1.23 ms median (37 us per thread hand-off); full path at zero delay 6.83 ms median, p99 B0 = 7.09 ms.
- D (pre-registered replication R2b, frozen and pushed before any trace, commit 973fa6f): fresh paired seeds, deadline Delta_os from Corollary 2 with B0.
  - Serial met the criterion (Wilson upper bound >= 0.99) in 7 of 8 profiles. This includes deadlines far tighter than R2's (408 vs 974 ms under global delay). At the R2 deadline, the ten-crash profile again succeeded in 96.3%, as predicted.
  - Miss: the control profile reached 83.3% [78.7, 87.1]. Without network slack, host drift of a few percent between the calibration and the run (median 6.83 to 6.9 ms) defeats the deadline.
  - Paired batch vs serial: batch is 8 to 12 ms slower under delay (sign tests p < 1e-74) and 0.9 ms faster without delay. Batch met the control deadline (99.3%) but missed the regional one (87.7%). The pre-stated "no difference" did not hold; this is reported as a negative result.
- Deviation entries 10 to 13 record the post hoc model, the calibration design and its revision after the smoke test (before the recorded run), the R2b freeze, the results and one display fix.
- Paper: Corollary 2 added; Q3 rewritten with R2, the post hoc check, the calibration and R2b; Table 4 now shows R2 and R2b side by side; the baselines table moved to the supplement (Table S4).
