# KEYSTONE R2 design amendment (DRAFT, not frozen)

Status: **DRAFT for author approval.** Nothing in this file is frozen, no R2 code has been written and no R2 experiment has been run. After the author approves the decisions in Section 7, the frozen parts are transcribed into `r2-design-freeze.json`, hashed into `r2-design-freeze.SHA256SUMS`, and only then is any R2 code run. Changes after the first R2 run go to `r2-deviation-log.md`.

Date drafted: 2026-10-21. Base: commit `2670827` (JCS manuscript, Group A revision). Source of the work items: `paper/jcs/reviews/expert_review_2026-10-21.md` (W1, W3, W5, W11).

## 1. Scope

| Item | Review weakness | R2 deliverable |
|---|---|---|
| W1 | No theorem links audits to DKA | Temporal readiness model; exact posterior risk given an audit history; optimal audit interval; simulation check |
| W3 | Dispute KEM fails PAC+ | Record-bound CCA-secure threshold KEM (TDH2); proof sketch of PAC+ with audits; implementation and benchmarks |
| W5 | Verification-bound finding is a pure-Python artifact | Elliptic-curve core; non-blocking verification; microbenchmarks; testbed rerun |
| W11 | Hash-to-group does not match the random-oracle model | Standard hash-to-group in the EC core; corrected wide hash for the retained ffdhe path |

Out of scope (Group C, future work in the paper): multi-host or multi-region deployment and real failure traces (W8), decoy disputes against selective withholding (W4a), on-chain beacon sampling and on-chain proof verification (W9).

## 2. Compatibility with `FREEZE.md` (KEYSTONE-MPP-F1)

- The central property (DKA), the committee baseline (`n=32, t=22`), the claim boundary and the prohibited claims are unchanged.
- TDH2 is an established construction (Shoup and Gennaro). Using it is an implementation choice, not a primitive-novelty claim.
- The EC core, non-blocking verification and the hash fix are implementation optimizations. The temporal analysis is an improved proof. Section 9 of `FREEZE.md` lists these as changes that do **not** require an UNFREEZE.
- R1 results stay in `research-case/05-analysis/results/r1/` unchanged. R2 results go to `results/r2/` and are reported as a separate evidence family.
- Program state remains INTAKE with novelty UNRESOLVED. R2 does not change those gates.

## 3. W5 and W11: elliptic-curve core and testbed rerun

### 3.1 Group and library (decision D1)

Target group: **ristretto255** (prime-order group over Curve25519, RFC 9496). Hash-to-group uses the 64-byte uniform-to-element map (`from_hash`), which matches the random-oracle model of Lemmas 2 and 3. That closes W11 for the EC path.

| Option | What it is | Pros | Cons |
|---|---|---|---|
| **A. `rbcl`** (recommended, subject to review) | Python binding to libsodium's ristretto255 functions | Native speed; standard group; exposes `from_hash`, scalar multiplication and point addition | New third-party dependency; needs a supply-chain review before install (wheel contents, maintainer, pinned hash in `uv.lock`) |
| B. Own `ctypes` wrapper over libsodium | About 100 lines binding the needed libsodium symbols | No new Python package | Needs a system libsodium (e.g. Homebrew), so a machine-level change; more code to maintain |
| C. Pure-Python ristretto255 | Implement the group in Python | No dependency | Slow, which defeats the purpose of W5 |

PyNaCl was checked and does **not** expose ristretto255 bindings (changelog up to 1.6.2).

### 3.2 Retained ffdhe path (W11 fix)

- `hash_to_group` for ffdhe: expand the input with an XMD-style expander to `|p| + 128` bits before reducing mod `p` and squaring. This replaces the current 256-bit candidate.
- Subgroup membership: replace full exponentiation (`x^q mod p`) with a Jacobi-symbol test. This is valid for safe primes.
- R1 microbenchmarks are kept as historical. R2 re-measures ffdhe2048 with the fixed hash and membership test, so the comparison stays like-for-like.

### 3.3 Verification (decision D2)

- Move proof verification off the combiner's event loop (worker thread or process), so reading responses does not stall.
- Primary mode: serial verification on arrival, the same rule as Proposition 3 (deadline budget).
- Secondary mode (D2, optional): batched DLEQ verification by a random linear combination, reported as a separate variant.

### 3.4 Microbenchmarks (frozen before the testbed)

Groups: ristretto255 (new), ffdhe2048 (fixed hash), ffdhe3072 (fixed hash). Operations as in R1 Table 5 (canary derivation, partial plus proof, proof verification, seal, combine `t` partials), plus the TDH2 operations of Section 4. Single process, the same host as R1, median of at least 1,000 runs per operation, with environment recorded.

### 3.5 Testbed rerun (outcome-blind deadline)

- Same topology and the same eight profiles as R1 (control, regional, global, 2% loss, 10 crashes, 11 crashes, one-domain outage, heavy tail), 300 traces per profile, new seed namespace `KEYSTONE-R2|DEADLINE|`.
- Cryptography: ristretto255 with TDH2 dispute shares.
- **Primary deadline, frozen as a formula and not a number:** `Δd* = δ_b + c_p + δ_p99 + t·c_v + c_c`. Here `c_p`, `c_v` and `c_c` are the R2 microbenchmark medians for ristretto255, `δ_p99` is the profile's 99th-percentile one-way delay from its declared delay law, and `δ_b = 0` on the single host. `Δd*` is computed after the microbenchmarks and **before** any testbed trace runs, written to `r2-deadline-record.json` and hashed.
- Primary endpoint: Pr[dispute decrypts the correct plaintext by `Δd*`] per profile, with 95% Wilson intervals. Secondary: success at 0.25, 0.5, 1, 2 and 5 s; completion-time quantiles; audit pass versus exact expectation.
- Pre-stated expectation: success is near 100% for reconstructable profiles, and completion is no longer verification-bound. Whatever the outcome, it is reported. The R1 finding is then restated as conditional on unoptimized code.

## 4. W3: record-bound CCA threshold KEM (TDH2)

- Construction: TDH2 (Shoup and Gennaro) in ristretto255. The label is `(epoch, record id, policy hash)`. The ciphertext carries `u = g^r`, `ū = ḡ^r` and a NIZK that `log_g u = log_ḡ ū`, bound to the label. A custodian verifies the ciphertext proof and the label against the authorized record before releasing `u^{x_i}` with a DLEQ proof.
- Effect: the re-submission attack of Proposition 2 fails. Re-using `C1` under a new record id changes the label and invalidates the proof, and a malleated `C1·g^γ` has no valid proof.
- Paper: Definition 7 (DKA) uses PAC+. A new lemma states PAC+ in the presence of audits by a hybrid argument: (i) simulate audits from public shares (Lemma 2); (ii) apply TDH2's chosen-ciphertext security under DDH in the random-oracle model against static corruption of fewer than `t` custodians. The random oracles are domain separated, so the two programmings are independent. TDH2's theorem is cited, not re-proved.
- Tests: label binding, rejection of re-submitted and malleated components, invalid-proof rejection, end-to-end open.
- Cost: one extra proof verification per custodian per dispute, and two extra exponentiations for the sender. Reported in the microbenchmark table.

## 5. W1: temporal readiness model and audit-to-DKA theorem

### 5.1 Model

- Non-selective faults: audit readiness equals dispute readiness (the scope of the paper after W4(b)).
- Each custodian alternates independently between ready and not ready as a two-state continuous-time Markov chain, with failure rate `λ` and repair rate `μ`. Stationary availability is `a = μ/(λ+μ)`.
- Optional extension: domain shocks, where each of 4 domains fails as a unit at rate `λ_d` and recovers at rate `μ_d`. This uses the product chain over domains.
- Audits run at times `T, 2T, ...`, each with a fresh uniform sample `(s, q)` and the static acceptance probability of Theorem 1 at the current `k`.
- A dispute arrives at a time independent of the process.

### 5.2 Results to state and prove

1. **Exact posterior risk.** `K(τ)`, the number of ready custodians, is a birth–death Markov chain whose transition probabilities over time `u` are explicit convolutions of binomials, with per-custodian `p_up→up(u) = a + (1−a)e^{−(λ+μ)u}` and `p_down→up(u) = a(1 − e^{−(λ+μ)u})`. The audit outcomes are observations with emission probability `Pr[accept | k]`. The probability that a dispute at time `τ` finds `K(τ) < t`, conditioned on the full audit history, is therefore given exactly by a hidden-Markov forward recursion over `k ∈ {0..n}`.
2. **Stationary design bound.** For a history of accepted audits, a closed form for the risk at the worst dispute time within an interval, and for the long-run fraction of time spent catastrophic and undetected, as functions of `(T, s, q, λ, μ)`.
3. **Design result.** For a target risk `ε`, the largest audit interval `T` (equivalently the lowest audit cost) achieving it for each `(s, q)`, including the sequential tests of Section 6.2 of the paper.

### 5.3 Validation and parameters

- A discrete-event simulation of the custodian chains and audits checks the exact recursion. This is an implementation check: fixed seeds, frozen before running.
- Parameters form a declared **synthetic** grid, because real traces are Group C. MTBF per custodian ∈ {7, 30, 90} days, MTTR ∈ {1, 6, 24} hours, audit interval `T` ∈ {1, 6, 24} hours, designs `(8,8), (16,14), (24,20)`, plus a domain-shock variant. The paper labels this as synthetic.

## 6. Outcome-blind protocol

1. The author approves the decisions in Section 7.
2. Frozen items (Sections 3–5) are written to `r2-design-freeze.json` and hashed. Every R2 script checks the hash before running, and every output records it.
3. Order of execution: unit tests and correctness first, then microbenchmarks, then `Δd*` computed and recorded, then testbed traces, then W1 exact analysis and simulation check.
4. Any change after the first run goes to `r2-deviation-log.md` with time, reason and effect on claims. No outcome-dependent retuning of endpoints.
5. The paper keeps the evidence labels: exact, simulation (implementation check), microbenchmark, emulation. R2 additions are labeled as R2.

## 7. Decisions needed from the author

| # | Decision | Recommendation |
|---|---|---|
| D1 | EC library | Option A (`rbcl`) after a static supply-chain review; fall back to B if the review fails |
| D2 | Batched verification variant | Include as a secondary variant (small extra effort) |
| D3 | Keep ffdhe in the paper | Yes, as the like-for-like baseline with the W11 fix |
| D4 | W1 domain-shock extension | Include; it is the realistic case and the chain stays small (4 domains) |
| D5 | Primary deadline rule | The formula `Δd*` in Section 3.5, frozen before the testbed |
| D6 | Paper scope after R2 | Title stays "Readiness Audits ..."; add W1 as a theorem, and Definition 7 moves to PAC+ |

## 8. Estimated effort

| Work package | Effort |
|---|---|
| Supply-chain review and EC core (ristretto255), tests | 3–4 days |
| W11 ffdhe fix, non-blocking verification | 1 day |
| TDH2 implementation, tests, PAC+ lemma | 4–5 days |
| Microbenchmarks and testbed rerun | 2–3 days |
| W1 model, recursion, theorems, simulation check | 5–7 days |
| Paper integration and QA | 3–4 days |
| **Total** | **about 4–5 weeks** |
