# Referee Report

**Journal:** Journal of Computer Security
**Manuscript:** "KEYSTONE: Auditable Dispute-Key Availability for Encrypted AI Rollups" (anonymized, 23 pp.)
**Supplementary material:** KEYSTONE_artifact_anonymized.zip (read statically; no code executed)
**Date:** 2026-10-21

---

## 1. Summary of the submission

The paper considers optimistic rollups whose disputed inputs are published only as ciphertexts, with the decryption key Shamir-shared among a custodian committee. It argues that data availability of the ciphertext is not enough: a dispute also needs t custodians to serve partial decryptions of the disputed record before the dispute deadline. The authors call this *dispute-key availability* (DKA).

The claimed contributions are:

1. **A property decomposition (Sec. 4).** Ciphertext availability (CA), valid-share registration (VSR), audit-time readiness (AKR), authorized decryptability (AD), deadline liveness (DDL), pre-authorization confidentiality (PAC/PAC+), and (ε, Δd)-DKA. Proposition 1 gives three counterexamples showing that weaker properties do not imply AD/DDL.
2. **A "confidentiality-preserving" readiness audit (Sec. 5).** A beacon-sampled subset of s custodians returns X^{x_i} on a hash-derived canary X = H_G(ctx) with a Chaum–Pedersen DLEQ proof. Lemma 2 shows the transcripts can be simulated from public shares in the ROM. Lemma 3 shows a canary cannot be steered onto a production C1. Proposition 2 shows that the plain threshold ElGamal KEM used for disputes is malleable across records, so PAC+ needs record-bound releases (e.g., TDH2).
3. **Analysis (Sec. 6).** A hypergeometric false-accept probability (Thm. 1), a static repeated-audit corollary, a stratified product formula (Prop. 3), a placement cap (Prop. 4), a binomial benign-pass probability (Prop. 5), and an additive deadline budget (Prop. 6).
4. **Evaluation (Sec. 7).** Exact computations, three "prespecified" Monte Carlo cells, pure-Python microbenchmarks at ffdhe2048/3072, a 32-process single-host emulated testbed, and Foundry gas numbers. The negative results are reported openly: the strict audit has a high benign alarm rate, selective withholders pass every audit and defeat every dispute, and no profile met the prespecified 2 s deadline.

The paper is careful, candid about its limits, and supported by a well-organized artifact. My main concerns are (i) depth and novelty, (ii) the absence of the result the title promises, namely a theorem that links passing audits to a DKA guarantee, (iii) a dispute construction that is insecure in the threat model a rollup actually faces, and (iv) an evaluation whose central empirical finding is mostly an artifact of the implementation.

---

## 2. Significance and novelty

**Is the problem important?** Yes, in principle. Systems that make liveness depend on a threshold committee releasing a key, including encrypted mempools (Ferveo, FairBlock, F3B, batched threshold encryption), timelock or threshold-release services, and threshold-wallet custody, do have an operational question that is under-studied: how do you know *before* you need it that the committee can still serve a release? Separating "the bytes are available" from "the key is serviceable" is a useful framing, and Proposition 1 makes it precise.

**Is the "dispute-key availability" framing convincing or contrived?** It is half convincing. The separation between CA and DDL is real. However:

- **The timescale is off.** Deployed optimistic rollups have dispute windows of days (typically about a week), and interactive bisection games have per-move timers of hours. At that timescale a decryption that takes 4 s, or even 40 s, is irrelevant. The binding risks are different: whether the key survives *at all* across the window, across committee rotation or resharing, and under bribery. The paper's deadline machinery (Prop. 6, the 0.25 to 5 s testbed grid) answers a question that a rollup designer would rarely ask. Disputes that straddle an epoch boundary (records sealed under PK_E, disputed after the committee for E has rotated) are the more realistic DKA failure, and the paper does not address them.
- **DKA as defined (Def. 7) is never established for KEYSTONE.** No theorem says that if KEYSTONE audits pass under some model then the epoch provides (ε, Δd)-DKA for a stated ε. Prop. 1(3) shows that no such statement exists without a temporal model, and the paper stops there (Corollary 1 covers only a frozen catastrophic state). The word "Auditable" in the title is therefore a claim the paper does not deliver. This is the most important gap in the paper (see W1).

**Is the AI-rollup motivation credible or decorative?** Mostly decorative. Nothing in the model, protocol, analysis or evaluation depends on the workload being ML inference: records are opaque 1 KiB blobs, and the paper itself observes (Sec. 9) that encrypted mempools face "the same operational concerns". The two AI citations (opML, and an arXiv EigenAI paper) motivate private inputs, but EigenAI, as the paper describes it, decrypts into a TEE. That raises questions the paper does not discuss, such as attestation and whether the TEE or the custodians are the real availability bottleneck. I would either drop "AI" from the title and frame the work as threshold-release readiness for dispute-driven protocols, or add AI-specific content (record sizes, TEE-mediated release, opML dispute timing).

**Novelty of the mechanism.** The canary audit asks a custodian for H(ctx)^{x_i} with a DLEQ proof against g^{x_i}. Structurally, this is a share of a threshold coin, distributed PRF or threshold BLS-style signature on a beacon-derived message. Lemma 2 (simulation from public shares by programming H_G as g^a) is the standard argument used for those primitives. The prior art to engage with includes:

- Cachin, Kursawe and Shoup, threshold coin-tossing in "Random oracles in Constantinople" (PODC 2000 / J. Cryptology 2005). Coin shares are H(C)^{x_i} with DLEQ proofs, simulated exactly as in Lemma 2. *(to verify the precise venue details; the construction is well known)*
- Naor, Pinkas and Reingold, distributed PRFs (EUROCRYPT 1999). *(to verify)*
- Threshold BLS (Boldyreva, PKC 2003) and drand-style threshold beacons. *(to verify)*

Once the audit is seen as "periodically collect sampled threshold-coin shares", contribution 2 reduces to "use a threshold coin as a heartbeat, sampled". That is close to the tBTC v2 heartbeat, which the paper cites, but with sampling. Lemma 3 is a one-line union bound. Theorem 1, Corollary 1 and Propositions 3–5 are textbook hypergeometric, binomial and product computations (acceptance sampling by attributes), and Proposition 4 is the inequality n − d ≥ t. The paper is admirably explicit that the components are standard (Sec. 1, Sec. 10 "Novelty"). The difficulty is that once the components are set aside, the remaining contribution consists of definitions, an elementary sampling analysis, and an evaluation that mostly confirms closed forms.

**What would make me say "incremental"?** In its current form I do say it, for the reasons above. What would move it out of that category is one of the following: (a) a real theorem connecting audit histories to a DKA guarantee under a stated temporal model (for example, a failure/repair Markov process), including optimal audit scheduling; (b) a mechanism that actually addresses selective withholding (see W4), which is the threat the introduction uses to motivate the work; or (c) a deployment-grade evaluation with real failure data that changes how practitioners should size committees or audits. Any one of these would justify a JCS article. Two would make it a strong one.

---

## 3. Technical soundness

I checked every definition, lemma, proposition and proof.

**Definitions (Sec. 4).**

- *Def. 3/4/8.* "Catastrophic" is defined via *audit*-readiness (k ≤ t − 1 audit-ready), while the property of interest is *dispute*-readiness. The text acknowledges that the two can differ (Prop. 1(2)), so the detection guarantee of Theorem 1 is about a proxy. That is acceptable, but it should be stated as an explicit assumption ("non-selective faults: audit-ready ⇔ dispute-ready") wherever detection is interpreted as protection of disputes. This includes the abstract's "detects 98.07% of worst-case catastrophic states".
- *Def. 6 (PAC).* The adversary sees audit transcripts but **no dispute releases of any record**. In a running system other records *are* disputed, so PAC is the property of a system in which disputes never happen. Def. 7 builds DKA on PAC, not PAC+. Since the prototype provides only PAC (Sec. 5.2), the (ε, Δd)-DKA notion the paper instantiates is confidentiality-vacuous for any deployment where disputes occur and the disputing party is not fully trusted. Def. 7 should use PAC+ (or a properly defined CCA-style notion), and the construction should meet it.
- *Def. 7.* The probability is "over the readiness model and the protocol's randomness", but Def. 7 contains no audit at all. An "auditable DKA" definition needs a statement of the form: "conditioned on the audit history H, Pr[DDL] ≥ 1 − ε(H)", or a Neyman–Pearson-style guarantee on the audit as a test of DKA. Without it, the audit and DKA are two disconnected objects.
- *Corruption model.* Assumption 1 says the adversary "learns fewer than t current shares", and Sec. 3 lets corruption "move across epochs". It is not stated whether corruption *within* an epoch is static. Lemma 2's simulator knows only the Y_i. If the adversary may corrupt custodian i adaptively after seeing audits, the simulator must produce an x_i consistent with Y_i, which it cannot do. Adaptive security of threshold ElGamal is non-trivial and is not covered. State static corruption explicitly, or handle adaptive corruption.

**Proposition 1.** Correct and elementary, as the authors say. Item (2) uses w = n − t + 1 withholders, all of them audit-ready, which is fine. Item (3) is the standard indistinguishability-of-histories argument. These are useful framing devices, but I would call them observations or examples, not a proposition.

**Lemma 1.** Standard (completeness, special soundness, forking lemma). Fine. Note that knowledge soundness shows that *whoever answered* knows x_i, not that the registered custodian does. Share pooling or outsourcing (one operator or cloud KMS answering for several custodians) and false failure-domain declarations are undetectable. This directly undermines the correlated-failure story of Prop. 4 and Fig. 3, because placement is self-declared and never verified. This should be discussed.

**Lemma 2.** The argument is correct for static corruption: programming H_G to g^a, D_i = Y_i^a, and HVZK-simulated proofs with a Q/ℓ collision bound per proof. The composition claim ("does not interfere with a reduction to the KEM that programs the key-derivation oracle") is plausible but asserted, not shown. I would like an explicit hybrid argument, especially once the dispute path switches to TDH2, whose proofs also program a random oracle. As noted above, the lemma is the standard threshold-coin simulation and should be credited as such.

**Lemma 3.** Correct and trivial. Also note that the implementation does not realize the RO model the lemma assumes (see below).

**Remark 1 versus the code.** The paper says the prototype "hashes to an integer modulo p and squares". In `group.py::hash_to_group` the candidate is `2 + (SHA-256 digest mod (p − 3))`. For ffdhe2048 that is an integer below 2^256 + 2, so every canary is a square of a 256-bit integer and lies below 2^512, a tiny and highly structured subset of a 2048-bit group. This is not a random oracle onto G \ {1}, and it is the opposite of what Remark 1 states. I do not see a practical attack at 2048 bits. Still, small and structured bases are exactly what index-calculus individual-log steps prefer for a fixed, standardized group (Logjam-style precomputation). Lemmas 2 and 3 are stated for an idealized map the artifact does not implement. Fix: expand the hash to at least |p| + 128 bits (expand_message_xmd style) before reducing, or move to an elliptic-curve group with RFC 9380 hash-to-curve.

**Proposition 2 (malleability).** Correct, and it is the most informative result in Sec. 5, though not in the authors' favor. The attack needs no algebra (γ = 0): re-commit the target's C1 under a fresh record identifier and dispute it. In an optimistic rollup, *any* party can be a challenger and any user can cause records to be committed, so PAC+ is the baseline requirement, not a stronger optional notion. The paper's own threat model (Sec. 3: "act as a worker that commits records of its choice and obtains disputes on them") is precisely the PAC+ adversary. The submitted construction is therefore insecure in its own stated threat model, and the fix (TDH2 / labeled CCA threshold KEM, or CDTD) is described but neither implemented, proved in composition with the audit, nor benchmarked. The paper presents this as a finding ("we show that confidentiality ... additionally requires binding"). It is well-known folklore that threshold ElGamal without labels is not CCA-secure, which is exactly why Shoup–Gennaro exists. A referee will read Prop. 2 as evidence that the core construction is weak, not as a contribution. The construction should be fixed, with Prop. 2 kept as a one-paragraph motivating remark.

**Theorem 1 and Corollary 1.** Correct. The monotonicity coupling is fine. My concern is with *interpretation*. With s = q = 8, n = 32, t = 22 (my computation from Eq. (1)):

| ready k | 21 (catastrophic) | 22 (= t, live) | 24 | 26 | 28 | 30 |
|---|---|---|---|---|---|---|
| Pr[accept] | 0.019 | 0.030 | 0.070 | 0.149 | 0.296 | 0.557 |

The audit hardly separates k = t − 1 (dead) from k = t (live, no margin), and it passes a committee with four spare custodians only 15% of the time. It is a detector of "k close to n", not of "k ≥ t". Reporting only the worst-case detection (98.07%) together with the IID benign pass rate hides this. The right object is the full operating-characteristic (OC) curve, together with a test designed to separate k ≤ t − 1 from k ≥ t + m for an explicit safety margin m. A sequential test (Wald SPRT) across repeated audits would be the natural tool. Table 1 and Fig. 4b show the problem but do not draw this conclusion.

**Proposition 3.** Correct, and it is a product of independent hypergeometrics. The paper says the worst stratified catastrophic state "depends on how the t − 1 ready custodians are spread". That maximization is an easy finite optimization and should simply be solved and reported.

**Proposition 4.** n − d ≥ t ⇔ d ≤ n − t. Not a proposition.

**Proposition 5.** Binomial tail. Correct. Not a proposition.

**Proposition 6.** Correct under its assumptions. However: (a) it ignores the authorization check and the board read by custodians beyond δb; (b) the observed behaviour in the testbed is dominated by CPU contention among 33 processes on one host, which the model does not capture; and (c) δb (L1/L2 finality) is the dominant term in any real deployment and is set to approximately 0 in the evaluation. The bound itself is a sum of terms.

**Security model acceptability.** ROM, a trusted combiner, a dealer, and static readiness are each individually acceptable for a journal paper if clearly scoped. Their *combination* with a plain KEM that fails PAC+ and an on-chain component in which an administrator chooses the sample, chooses the canary hash, opens disputes and adjudicates validity (see Sec. 4 below) means that very little of the end-to-end "public evidence" story is actually trustless. A JCS referee will ask what the security theorem for the *system* is. At present there is none.

---

## 4. Evaluation

**What the evaluation does well.** The labels distinguishing exact, simulation, microbenchmark and emulation results, the Wilson intervals, the reporting of a failed primary endpoint, the retained timeout trace, and the complete raw outputs in the artifact are all better practice than most systems-security papers follow.

**What it does not do.**

1. **Most of the evaluation re-derives closed forms.** The three Monte Carlo cells estimate quantities that Eq. (1), Prop. 3 and Prop. 1(2) give exactly. The SW cell "only confirms that the implementation reproduces" a deterministic counterexample (the paper's own words). Drawing 131,072 samples from a hypergeometric whose pmf you can write down is a unit test, not an experiment. Simulation is worth its space where no closed form exists: temporal readiness processes, real failure traces, adaptive adversaries, multi-epoch disputes.
2. **The stratification endpoint is underpowered by design and analyzed suboptimally.** The Hoeffding-based plan with range 2 gives a half-width of 0.0075 for an effect of order 10^-4, so a null result was guaranteed. The 28 of 28 discordant pairs favoring stratification would give an exact McNemar p ≈ 7.5 × 10^-9. More to the point, the exact answer is available from Prop. 3 and needs no test at all.
3. **The headline Q3 finding is an implementation artifact.** "Serial proof verification, not emulated network delay, bounded completion time" follows from DLEQ verification at 135 ms in pure-Python ffdhe2048, against injected one-way delays of 0 to 120 ms. Reading the artifact:
   - `verify_equal_discrete_logs` runs `validate_element` (a full-length exponentiation x^q mod p) on six group elements *in addition to* the four verification exponentiations. In a safe-prime group, membership in the QR subgroup can be checked with a Jacobi symbol at negligible cost, so verification is roughly 2.5× slower than necessary even in pure Python.
   - Verification runs synchronously inside the combiner's asyncio event loop, so reading also stalls during verification.
   - No multi-exponentiation, no batch verification, no GMP-backed arithmetic, no elliptic-curve group.

   With ristretto255 or BLS12-381 via a standard library, a DLEQ verification costs on the order of 10^-1 ms *(order of magnitude; to verify on the authors' hardware)*, three orders of magnitude less. The conclusion would then reverse: network delay and especially ledger finality δb would dominate. The paper says this ("optimized libraries ... are substantially faster"; "we did not measure optimized or batched verification"), but then elevates the unoptimized observation to the abstract and the conclusions. As a scientific finding about DKA it has no external validity.
4. **The prespecified 2 s deadline.** Reporting it is honest, and I credit that. But it does reflect on the design process. The deadline was fixed without a pilot that would have shown that 22 × 135 ms alone exceeds 2 s, and the deviation log attributes the one control failure to the analyst compiling a TikZ figure on the same host. A referee will read this as a lab-notebook rather than a mature experimental design. Better: keep the disclosure in the artifact, and in the paper report the full Pr[DDL ≤ Δd] curves as the result, with one sentence noting that the prespecified threshold was mis-set and why.
5. **Single host, synthetic failures.** Loopback TCP, application-level `asyncio.sleep` delays, 33 processes on one M4 Pro, and synthetic IID or equal-domain failure models. The crash profiles finishing *faster* because fewer processes compete for CPU illustrates the confound. Missing:
   - At minimum a multi-machine LAN or multi-region cloud deployment (even 3 to 4 regions with 8 custodians each).
   - Realistic δb: L2 sequencer inclusion and L1 finality.
   - Real availability traces to calibrate f and the correlation structure. Possible public sources include Ethereum validator attestation participation, drand / League of Entropy node availability, Shutter keyper operations, and tBTC heartbeat failures *(availability of suitable public data to verify)*. The paper cites Ford et al. 2010 for correlated failures but does not use any data.
6. **Missing baselines.**
   - A *full-committee probe with aggregated or batched verification* (or threshold-BLS-style aggregation, where one pairing check verifies the combined value). The paper itself concedes that the full probe is "affordable for one audit per epoch at n = 32" (Sec. 7.1). That undercuts the case for sampling unless audit frequency must be high, and the paper never derives the required frequency.
   - *Proactive refresh as the audit*: refresh exercises every share. The paper dismisses it as "infrequent and costly" without measuring it.
   - *Decoy (indistinguishable) disputes* as a selective-withholding countermeasure (see W4).
7. **No audit-frequency or cost model.** Detection per audit is the wrong metric when failures arrive over time. The relevant quantities are time-to-detection, the probability that a dispute arrives during an undetected catastrophic period, and the cost per unit of risk reduction. None is computed.
8. **Gas (Table 7).** The numbers are for a harness with n = 5 and a contract that verifies nothing cryptographic. On-chain verification of ffdhe2048 DLEQ proofs via the MODEXP precompile would be expensive, while EC versions on BN254 precompiles are feasible. The ffdhe choice therefore also undermines the "public evidence" goal. Worse, in `KeystoneBulletinBoard.sol` the admin supplies `sampledBitmap` and `canaryHash` to `openAudit` with no beacon check. The admin also opens disputes and is the only party that can mark responses invalid. `finalize` counts every unflagged commitment as valid, so a custodian that lost its share can commit garbage and still "pass" on chain unless the admin intervenes. Section 5 discloses the admin role for invalid evidence and cancellation, but not that **sample selection, which Theorem 1 depends on, is admin-chosen and unverified**. An admin that avoids failed custodians defeats Theorem 1 entirely.

---

## 5. Related work and positioning

The related-work section is competent and fair to the systems it cites (CALYPSO, ETHTID, Ferveo, FairBlock, F3B, BEAT-MEV, batched threshold encryption, tBTC heartbeat, proof of custody, PoR/PDP/HAIL, DAS). An expert would raise the following. All items are to verify for exact bibliographic details.

- **Threshold coin-tossing, DPRFs and threshold BLS** (Cachin–Kursawe–Shoup; Naor–Pinkas–Reingold; Boldyreva). These are the direct technical ancestors of the canary audit and of Lemma 2. Their omission is the most serious positioning gap.
- **Committee-held secrets with eventual release on blockchains.** Benhamouda et al., "Can a public blockchain keep a secret?" (TCC 2020); Goyal et al., "Storing and retrieving secrets on a blockchain" (PKC 2022); YOSO (Gentry et al., CRYPTO 2021). These study exactly the long-lived custody and committee-handover setting in which DKA failures arise.
- **Dynamic proactive secret sharing for committee rotation.** CHURP (Maram et al., CCS 2019). The paper cites Yurek et al. but not CHURP, and it does not address disputes that straddle epochs.
- **Timelock / beacon-based release.** drand tlock (Gailly–Melissaris–Romailler, ePrint 2023/189). Release liveness depends on a threshold beacon network.
- **Deployed threshold-encryption committees.** Shutter keypers, Threshold Network TACo, Lit Protocol. Readiness is operational practice there, and any public liveness data would help the evaluation.
- **Data-availability committees** (e.g., Arbitrum AnyTrust DACs). This is the closest analogue of a committee-availability assumption in rollups, with a deployed fallback design.
- **Proofs of storage over time.** Filecoin Proof-of-Spacetime / WindowPoSt and academic "proof of storage-time" work. These are periodic sampled audits with penalties, and they are precisely the temporal-model gap of Prop. 1(3) solved in another setting.
- **Acceptance sampling and sequential testing.** OC curves, Wald SPRT. Theorem 1 is an acceptance-sampling-by-attributes statement, and the statistics literature already provides the design tools (choice of s and q, sequential plans).
- **Terminology.** "Proof of possession" (keywords) conventionally refers to Ristenpart–Yilek-style key registration. Using it for share-possession audits will confuse readers.

The characterization of encrypted mempools ("the published descriptions we found specify the release path but no pre-release readiness audit") is a fair reading of what I know, but it rests on "a bounded literature search" (Sec. 10). Deployed systems almost certainly run operational health checks. The paper should distinguish published protocols from operational practice and claim only the former.

---

## 6. Presentation

- The writing is precise and economical at the sentence level, and the figures are clean.
- **Hedging and process vocabulary.** "Prespecified", "post hoc", "evidence label", "PC03", "seed blocks", "deviation log", "concurrent analyst activity", and more than a dozen "we do not claim" statements in a 20-page body. This reads like a preregistered empirical-science report grafted onto a crypto/security paper. Some of it is good practice, but in a JCS article it signals immaturity and draws attention to weaknesses. Keep the provenance in the artifact, and keep one short "Methodology and evidence types" paragraph in the paper.
- **Length balance.** About 4 pages of elementary formal results labeled as theorems and propositions, against no system-level security theorem and no temporal analysis. Sec. 7.4 (performance) is a few lines. Fig. 5 is two panels of nearly identical step functions at about 3.8 s and carries almost no information beyond Table 4(b). Fig. 4a likewise plots a step at w = 11 that Prop. 1(2) already states.
- **Table 4** is rotated and mixes two incomparable meanings of "dispute success" (reconstructability versus success by 2 s), which the caption has to explain. Split it into two tables.
- **Abstract.** "Detects 98.07% of worst-case catastrophic states" should read "detects the worst-case catastrophic state with probability 0.9807 per audit under a static, non-selective fault model".
- **Prop. 4 and Prop. 5** should be inline facts. Prop. 1 could be an "Observation".
- **Title** promises "Auditable DKA" and "AI rollups". Neither is delivered as stated (see W1 and W12).

**Confidential comment to the editor (anonymity and disclosure).** The supplementary archive contains project-governance files, `research-case/03-design/r1-reviewer-revision/R1-AUTHORIZATION.md` and `r1-deviation-log.md`. They (a) state that the manuscript base is a file named `KEYSTONE_PhD_Reviewer_Manuscript.tex` and that this is a revision prompted by an earlier external reviewer; (b) refer to a public repository and record SHA-256 hashes that could be used to locate it, which is a de-anonymization risk; and (c) state that "the paper must disclose that the PC03 methods review was not independent". The manuscript does not make that disclosure in those terms: it says only that the design hash is "self-recorded" (Sec. 7, Sec. 10). The same file says the novelty audit "remains UNRESOLVED". Test-file names (e.g., `test_pc02_novelty_verifier_packet.py`, `test_draft_adversarial_reviews.py`) are similar process artifacts. None of this affects my technical assessment, but the editor may wish to ask the authors to strip governance material from the review artifact and to align the paper's disclosure with their own internal record.

---

## 7. Recommendation

**Major revision (borderline reject).** The paper is honest, careful and reproducible, and it isolates a real operational property. As submitted, however, it lacks the central theorem its title promises, its formal results are elementary or standard, its dispute construction fails the confidentiality notion that its own threat model requires, and its main empirical finding does not generalize beyond the unoptimized prototype. The revisions needed (W1–W6 below) are substantial but well defined. If done, they would make this a solid JCS paper.

**My honest estimate of first-round outcomes at JCS for this version:**

| Outcome | Probability |
|---|---|
| Reject | 45–55% |
| Major revision | 40–45% |
| Minor revision | about 5% |
| Accept | about 1% or less |

The outcome will depend heavily on referee mix. A crypto-leaning referee will focus on W2/W3 (standard components, malleable KEM) and lean toward reject. A systems or blockchain referee will credit the framing and the artifact but object to W5/W8 (single-host Python evaluation, timescale) and lean toward major revision.

---

## 8. Prioritized weaknesses

Severity scale: **Fatal** = blocks acceptance in any form; **Major** = must be fixed for acceptance; **Minor** = should be fixed.

### W1. No theorem connects audits to DKA. "Auditable DKA" is not established. **Major (near-fatal)**
- *Why it matters:* The title property is defined (Def. 7) but never proved for KEYSTONE under any model. Prop. 1(3) shows that a temporal model is required, and the paper stops there. A referee will ask what an operator can conclude from a passed audit history, and the paper answers "nothing beyond a frozen state".
- *Fix:* Introduce a simple temporal readiness model, for example an independent per-custodian failure/repair Markov chain with optional domain shocks, plus a non-selective fault assumption. Prove a bound of the form Pr[¬DDL at a dispute time | audit history] ≤ ε(s, q, audit interval, failure and repair rates), combining Thm. 1 with Prop. 6. Derive the optimal audit interval or sample size for a target ε and cost. Validate by simulation, which is where simulation earns its place.
- *Effort:* 1–2 weeks of theory, plus 2–4 days of new simulation code. No new testbed runs needed.

### W2. Depth and novelty: the formal results are elementary, and the audit is a known primitive. **Major**
- *Why it matters:* Thm. 1, Cor. 1 and Props. 3–5 are standard probability. Lemma 2 is the standard threshold-coin / DPRF simulation, and the canary audit is in effect sampled threshold-coin shares. Without crediting CKS, NPR and threshold BLS, the paper over-claims contribution 2. With that credit, the remaining contribution is thin for a journal.
- *Fix:* Cite and position against the threshold-coin, DPRF and threshold-BLS literature. Reframe contribution 2 as "the right use of a threshold-coin heartbeat for key readiness, with its exact sampling guarantees". Add at least one non-trivial result: W1, the W4 mechanism, or an optimal-design result (e.g., minimax choice of (s, q) or an SPRT plan). Demote Props. 4/5 and Prop. 1 to observations.
- *Effort:* Positioning, days. A new result, 1–3 weeks (overlaps with W1/W4).

### W3. The dispute construction fails PAC+, the notion the threat model requires. **Major**
- *Why it matters:* In a rollup any challenger can trigger disputes, and Sec. 3 explicitly lets the adversary commit records and obtain disputes. Prop. 2 shows the plain KEM leaks every record via a trivial replay. Shipping and evaluating a construction that is insecure in its own threat model, while the fix is textbook (TDH2), makes the core construction look weak. DKA (Def. 7) is built on PAC, which is vacuous once any dispute occurs.
- *Fix:* Make the record-bound CCA threshold KEM (TDH2 with label = record id and epoch, or CDTD) *the* construction. Redefine Def. 7 with PAC+. Prove PAC+ in the presence of audits with an explicit hybrid argument covering both RO-programmed proof systems. Implement it and add its costs to Tables 5 and 6. Reduce Prop. 2 to a short motivating remark.
- *Effort:* About 1 week of proofs, about 3–5 days of code and benchmarks.

### W4. Selective withholding, the motivating threat, is unaddressed, and its dismissal is unconvincing. **Major**
- *Why it matters:* The introduction motivates the work with strategic custodians "answering every routine check while refusing the one dispute that harms them". The mechanism detects only benign faults. Sec. 8 argues that indistinguishable canaries would prevent observers from checking that no production record was opened. That ignores commit-and-reveal decoys: the coordinator commits to decoy randomness ρ (or to a decoy-record set) in advance, issues decoy disputes indistinguishable to custodians, and reveals ρ afterwards so anyone can verify that C1 = g^ρ was a decoy. Combined with record-bound labels, decoys and real disputes look alike to custodians, which yields detection guarantees against non-adaptive withholders.
- *Fix:* Either (a) design and analyze decoy disputes (indistinguishability conditions, what custodians can observe on chain, detection probability against a withholder targeting a fraction of records, cost), or (b) narrow the scope in the title, abstract and introduction to non-strategic faults and remove the strategic motivation.
- *Effort:* (a) 2–4 weeks including a small implementation. (b) 1–2 days.

### W5. The Q3 finding (verification-bound completion) is an implementation artifact. **Major**
- *Why it matters:* Pure-Python ffdhe2048 with six redundant full-length membership exponentiations per verification and inline event-loop verification makes compute dominate by construction. With any production EC library the conclusion reverses. The finding currently sits in the abstract and the conclusion.
- *Fix:* Re-implement the cryptographic core on ristretto255 or BLS12-381 (libsodium / blst / arkworks via bindings). Use Jacobi-symbol membership if ffdhe is kept, plus batch verification. Rerun the microbenchmarks and the testbed. Remove the claim from the abstract unless it survives.
- *Effort:* 1–2 weeks of code and reruns.

### W6. The detection metric misleads; the OC curve shows the audit barely separates k = t − 1 from k = t. **Major**
- *Why it matters:* With s = q = 8, Pr[accept] is 0.019 at k = 21 versus 0.030 at k = 22, and 0.149 at k = 26. "98.07% detection" and "frequent benign alarms" are two faces of a test with almost no power at the boundary that matters. Operators cannot act on such an alarm.
- *Fix:* Plot full OC curves for the proposed (s, q). Define a margin m and design the test to separate k ≤ t − 1 from k ≥ t + m at stated error rates. Consider sequential (SPRT) plans across audits. Revise the abstract and Sec. 8 design guidance accordingly.
- *Effort:* 2–4 days, exact computation only.

### W7. The timescale mismatch with real optimistic rollups, and cross-epoch disputes are ignored. **Major**
- *Why it matters:* Dispute windows are days and bisection timers are hours, so a second-scale DDL is not the binding constraint. Key survival across committee rotation, resharing and churn is, and Def. 7 is per-epoch.
- *Fix:* Parameterize Δd against real rollup dispute protocols. Extend DKA and the analysis to multi-epoch records (handover via DPSS/CHURP, re-encryption, or retention of old epoch keys). State what the audit checks across epochs.
- *Effort:* 1 week of analysis. Optional small implementation of resharing, about 1 week.

### W8. The evaluation is single host with synthetic failures and no realistic ledger delay. **Major**
- *Why it matters:* 33 processes on one laptop CPU, loopback, sleep-based delays and δb ≈ 0 give no external validity for deadline liveness. Synthetic IID or equal-domain models give none for detection or benign alarms.
- *Fix:* (a) A multi-region deployment (e.g., 3–4 cloud regions × 8 custodians), or at least multiple hosts with tc/netem. (b) Include realistic δb from an L2 testnet or a measured finality distribution. (c) Calibrate f and the correlation structure on a public availability dataset (validator participation, drand nodes, or keyper logs), or explicitly justify parameter choices from such data.
- *Effort:* 1–3 weeks, new experiments.

### W9. The on-chain evidence path is admin-trusted, including the sample on which Theorem 1 depends. **Major/Minor**
- *Why it matters:* `openAudit` takes an admin-supplied `sampledBitmap` and `canaryHash` with no beacon verification. The admin alone marks invalid responses, and `finalize` counts unflagged commitments as valid. An admin that steers samples defeats Thm. 1, and the "public, transferable evidence" claim does not hold for the artifact.
- *Fix:* Derive the sample on chain from a committed beacon value (or verify a beacon proof). Verify DLEQ on chain using EC precompiles (BN254), or use an optimistic challenge with fraud proofs. Report the gas. Disclose admin trust in the sample explicitly in Sec. 5.
- *Effort:* About 1 week (Solidity plus EC proofs). Disclosure only: hours.

### W10. The simulation cells add little, and the statistics are suboptimal. **Minor**
- *Why it matters:* The cells estimate closed-form quantities. The prespecified paired endpoint was guaranteed to be uninformative, and a McNemar test on the 28/28 discordant pairs would have been decisive.
- *Fix:* Replace the cells with exact values, keep one sentence on Monte Carlo agreement as an implementation check, and reserve simulation for W1/W8. If any test is kept, use exact or McNemar tests.
- *Effort:* 1–2 days.

### W11. The H_G implementation does not match the RO model, and Remark 1 is inaccurate. **Minor**
- *Why it matters:* For ffdhe groups the canary is the square of a 256-bit integer (below 2^512), not a near-uniform group element. The lemmas assume an RO onto G \ {1}.
- *Fix:* Expand the hash to at least |p| + 128 bits before reduction, or switch to an EC group with RFC 9380. Correct Remark 1 and rerun the microbenchmarks.
- *Effort:* Hours of code, plus a microbenchmark rerun (less than 1 day).

### W12. The AI-rollup motivation is decorative. **Minor**
- *Why it matters:* Nothing is AI-specific, and the TEE-based release in the cited AI system raises unaddressed questions.
- *Fix:* Retitle and reframe around threshold-release readiness for dispute-driven or encrypted-input protocols, with AI rollups as one example. Alternatively, add AI-specific requirements (record sizes, TEE attestation, opML timing).
- *Effort:* 1–3 days of writing.

### W13. Model assumptions are not stated precisely enough. **Minor**
- *Why it matters:* Static versus adaptive corruption within an epoch, the trusted combiner, share pooling and outsourcing, and unverified failure-domain declarations each affect what an audit means.
- *Fix:* State static corruption explicitly. Add a paragraph on share pooling and on placement being self-declared, and note that the audit cannot verify either. Explain why a trusted combiner (TEE or verifier) is consistent with the rollup trust model, which otherwise relies on 1-of-N honest challengers. Threshold custody changes that trust model to t-of-n, and this should be said plainly.
- *Effort:* 1–2 days.

### W14. Missing related work. **Minor (Major in combination with W2)**
- *Fix:* Add threshold coins, DPRFs and threshold BLS; committee-held blockchain secrets (TCC 2020, PKC 2022, YOSO); CHURP; drand tlock; deployed keyper networks; DACs; proofs of storage-time; acceptance sampling and SPRT. Distinguish published protocols from operational practice.
- *Effort:* 2–3 days.

### W15. Presentation maturity. **Minor**
- *Fix:* Cut process vocabulary and repeated disclaimers. Merge Fig. 5 into a table or a single panel. Split Table 4. Demote trivial propositions. Fix the abstract's detection wording. Strip governance files from the review artifact and align the disclosure of non-independent design review with the authors' own records (see the confidential comment).
- *Effort:* 2–4 days.

---

### Summary of required versus optional work for a successful revision

- **Required:** W1, W3, W5, W6, W7, plus either W4(a) or W4(b).
- **Strongly recommended:** W8, W9, W2 (positioning), W14.
- **Housekeeping:** W10–W13, W15.

Realistic total effort: **6–10 weeks** of focused work, including new code (EC crypto core, TDH2 path, on-chain sampling and verification, temporal simulator) and new experiments (multi-host testbed, calibrated failure data).
