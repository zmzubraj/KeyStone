# R3 pre-submission revision plan (2026-10-23)

This plan comes from the self-review of the R2b manuscript (commit `e487214`), which was a pre-submission check by the AI that drafted the paper, not peer review. The author approved the order: Phase 1 (writing), Phase 2 (new analyses M3 and M1), then Phase 3 (minor items and figures).

## Budget

- **Words.** JCS sets no length limit; its guidelines require an abstract of 150 to 200 words and the reported counts of words, figures and tables. The author raised the target to about 12,500 words.
- **References.** Stay at 45 or fewer cited works.
- **Style.** No em dashes.
- **Numbers.** Every number is generated from committed data.

## Phase 1: writing fixes (no new experiments)

| Item | Change |
|---|---|
| m1 | Replace "pre-registered" by "pre-specified and publicly timestamped" everywhere. The timestamps can be verified after review. |
| m3 | In the main text, state that R2b treats the calibrated 99th percentile as B in Corollary 2, so the 0.99 target is approximate. |
| m4 | Add a short evidence map to the Method paragraph: R1, R2 and R2b, what each produced, and how each was fixed in advance. |
| M2 | Reframe the contributions around three security findings: a small audit cannot separate k = t-1 from k = t; there is a floor that frequency cannot beat; selective withholding is invisible to any audit of this kind. Primitives stay credited as known. |
| M5 | Reframe Q3 as a test of the deadline model's predictive power (Corollary 2 on fresh data) and of verification placement, not of absolute latency. Explain why millisecond scale is the right regime for that test (per-move timers; the model is scale-free in the delay law). |
| M4(a) | Recast the dispute ciphertext as a tag-KEM/DEM hybrid: TDH2's threshold KEM, with the label and the wrapped key as tag, and AES-GCM as DEM (Abe, Gennaro and Kurosawa, J. Cryptology 2008). Assumption 5 narrows to CCA security of the TDH2 tag-KEM in the threshold model. Update the Lemma 4 sketch and the supplement proof. |

## Phase 2: new analyses (designed and frozen before any output)

**M3: repair on alarm (temporal model).**
- A rejected audit triggers repair. After a delay D_r the committee is reshared to fully ready, which resets the custodian chain to all up. Domains stay as they are, because resharing does not repair a provider outage, and the variant keeps that.
- Exact computation:
  - Embedded Markov chain at audit epochs, with a reset branch.
  - Time-average dispute-failure probability over a renewal cycle (numerical integration within intervals).
  - Rate of resharings per day, which includes benign alarms.
- Design result: the cheapest (T, s, q) meeting a target on actual failure probability, with a cost of audits plus resharings. This turns the larger-sample question into a real trade-off.
- Validation: the event simulation is extended with resets, on three frozen cells, with a 99% Wilson criterion.
- Freeze: `research-case/03-design/r2c-temporal-repair/` holds the grid, metrics, cells and seeds. It is committed and pushed before running.

**M1: selective withholding, quantified.**
- (a) Exact. With w withholders among n and the honest custodians failing as in the temporal model, the dispute fails iff fewer than t honest custodians are ready. Audit acceptance is unaffected by w, which is a corollary of the model.
- (b) Proposition (impossibility). Any pre-dispute test whose requests a custodian can tell apart from the targeted dispute cannot detect withholding targeted at that dispute. Decoy disputes over protocol-sealed records bound only withholding as a policy. The per-refusal detection probability is the decoy fraction.
- (c) Accountability bound. A failed dispute names the non-responders under Assumption 4, so withholding is unprofitable if w times the stake times the attribution probability exceeds the value of blocking. This states the stake needed for given (n, t).
- Exact tables only; no testbed run. Frozen together with M3.

## Phase 3: minor items and figures

- **Remark 1.** Cite the Arbitrum chain parameters: dispute window 45,818 L1 blocks, about 6.4 days, on Arbitrum One and Nova. Verified on docs.arbitrum.io (chain-params).
- **Abstract.** Rewrite the last sentence in plain terms. Keep the abstract at 200 words or fewer.
- **Figures.**
  - A new temporal figure: U(T) and actual failure with repair against T, for (8,8) and (24,20), with floors U_0.
  - Consider restoring detection versus s from the supplement if the budget allows.
  - Rebalance the tables so the paper is not text-heavy.
- **References.** Add Abe, Gennaro and Kurosawa 2008 and the Arbitrum docs. Drop two lower-value references (`buterin2017casper`, `bormet2025epochless`) to stay at 45.

## Gates

- Each phase ends with a build, these counts, and an identity scan:
  - words
  - abstract
  - references
  - em dashes
  - undefined or overfull warnings
- Phase 2 also needs the frozen design pushed before computing, a deviation log, and an artifact that reproduces the new tables byte-identically.
- The final package is rebuilt and checked. The new theorems join the list for the human expert read-through.
