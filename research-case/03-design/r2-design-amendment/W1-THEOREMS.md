# W1: temporal readiness model and audit-to-DKA results

Status: statements and proofs written before any R2_TEMPORAL output existed.
Implementation: `prototype/r2/src/keystone_r2/temporal.py`; tests: `prototype/r2/tests/test_r2_temporal.py`;
runner: `prototype/r2/scripts/run_r2_temporal.py`. Frozen families: `R2_TEMPORAL_EXACT`, `R2_TEMPORAL_SIM_CHECK`
in `r2-design-freeze.json`.

Evidence label for every number derived from these results: EXACT_UNDER_DECLARED_SYNTHETIC_MODEL.
The parameters are synthetic; real availability traces are future work (Group C).

## 1. Model and notation

- Committee of `n` custodians, dispute threshold `t`. `K(τ)` is the number of custodians ready at time `τ`.
  A dispute at `τ` is catastrophic when `K(τ) < t`.
- **Non-selective faults.** A custodian is ready for an audit exactly when it is ready for a dispute,
  and a ready custodian answers both correctly. Selective (adversarial) withholding is out of scope (W4(a), Group C).
- **Custodian dynamics.** Each custodian is an independent two-state continuous-time Markov chain with failure rate
  `λ` and repair rate `μ`. Write `a = μ/(λ+μ)` for its availability and, for an elapsed time `u ≥ 0`,

  `p_uu(u) = a + (1−a) e^{−(λ+μ)u}`, `p_du(u) = a (1 − e^{−(λ+μ)u})`

  for the probability of being up at `u` given up, respectively down, at 0.
- **Domain shocks (variant).** The custodians form `D` domains of `m = n/D` (here `D = 4`, `m = 8`).
  Each domain is a further independent two-state chain with rates `λ_d`, `μ_d`. A custodian is ready when it and its
  domain are both up.
- **Audits.** At times `T, 2T, ...` an audit draws a fresh uniform sample of `s` distinct custodians, independent of
  the process and of earlier samples, and accepts when at least `q` sampled custodians are ready. By Theorem 1 of the
  paper, given `k` ready custodians,

  `A(k) = Pr[accept | K = k] = Σ_{j ≥ q} C(k, j) C(n−k, s−j) / C(n, s)`.

  `A` is non-decreasing in `k` (couple the samples: adding a ready custodian can only raise the ready count in the
  sample).
- **Disputes** arrive at a time independent of the custodian, domain and sampling processes.
  Write `τ = mT + u` with `0 ≤ u < T` for a dispute after the `m`-th audit.

All vectors below are row vectors over the hidden state; `1_{<t}` is the indicator column of `K < t`.

## 2. Exact state process

**Lemma 1 (lumped count chain).** Without domain shocks, `K` is a time-homogeneous Markov chain with

`P_u(k, k') = Σ_i Bin(i; k, p_uu(u)) · Bin(k' − i; n − k, p_du(u))`,

and stationary law `π = Bin(n, a)`.

*Proof.* The configuration process (which custodians are up) is a product of independent two-state chains.
Started from any configuration with `k` custodians up, after time `u` each of the `k` up custodians is up
independently with probability `p_uu(u)` and each of the `n − k` down custodians with probability `p_du(u)`.
So the law of `K(u)` is the convolution of `Bin(k, p_uu)` and `Bin(n−k, p_du)`. It depends on the
configuration only through `k`, which is Dynkin's criterion for strong lumpability. Hence `K` is Markov with kernel
`P_u`. The stationary law of each custodian is `(1−a, a)`, and the custodians are independent, so `π = Bin(n, a)`. ∎

**Lemma 2 (domain shocks).** For every domain `d` let `δ_d ∈ {0, 1}` be its state and `J_d ∈ {0..m}` the number of its
members that are individually up. Then `X = ((δ_d, J_d))_{d=1..D}` is a Markov chain whose kernel is the
`D`-fold product of the per-domain kernel `P^δ_u ⊗ P^{(m)}_u`. Here `P^δ_u` is the two-state kernel with
`(λ_d, μ_d)` and `P^{(m)}_u` is Lemma 1 with `m` members. Moreover `K = Σ_d δ_d J_d`.

*Proof.* Domains are mutually independent, and inside a domain the domain chain is independent of the member chains.
Lemma 1 applied inside each domain lumps the members of that domain to `J_d`. Product and lumping commute because the
blocks are independent. A member is ready iff it and its domain are up, so `K = Σ δ_d J_d`. ∎

*Remark (why not `(domain states, K)`).* The freeze describes the variant as "the product chain over
(domain states, k)". That pair is a function of `X` but is not Markov in general. Take two configurations with the
same domain states and the same `K` whose down domain has different individually-up counts `J_d`. Their
future `K` differs once that domain recovers. The implementation therefore uses `X`, of size `(2(m+1))^D = 18^4`.
This is recorded in the deviation log before any temporal run.

## 3. Exact posterior risk given an audit history

Let `o_1, ..., o_m ∈ {accept, reject}` be the outcomes of the first `m` audits. Let the process be stationary before
the first audit. Set `e_accept = A(K(·))` and `e_reject = 1 − A(K(·))`, as functions of the hidden state.

**Theorem 3 (forward recursion).** Define

`α_1 ∝ π ⊙ e_{o_1}`, `α_j ∝ (α_{j−1} P_T) ⊙ e_{o_j}` for `j = 2..m`,

each normalized to sum 1 (`⊙` is the entrywise product). Then `α_m(x) = Pr[X(mT) = x | o_1..o_m]`, and for a dispute
at `τ = mT + u`, `0 ≤ u < T`,

`Pr[K(τ) < t | o_1, ..., o_m] = α_m P_u 1_{<t}`.

The same holds for the domain-shock chain of Lemma 2 with `X` in place of `K`.

*Proof.* By Lemmas 1 and 2, the hidden state sampled at the audit times is a Markov chain with kernel `P_T`. Fix the
hidden path. The `j`-th audit's sample is fresh, uniform and independent of everything else, and faults are
non-selective. So the outcome `o_j` is conditionally independent of all other variables given `X(jT)`, and it is
accept with probability `A(K(jT))`: the hypergeometric tail depends on the configuration only through the number of
ready custodians. This is a hidden Markov model, and the stated recursion is Bayes' rule applied one audit at a time
(the forward algorithm). For the dispute, the Markov property at `mT` and the independence of `τ` from the process
give `Pr[X(mT+u) = · | o_{1..m}] = α_m P_u`. Summing over `K < t` gives the claim. ∎

**Proposition 4 (limit after an unbroken run of accepted audits).** Assume `λ, μ > 0`, `T > 0` and `q ≤ s`
(and `λ_d, μ_d > 0` in the domain variant). Let all audits accept. Then `α_m` converges geometrically, from any
start, to a unique `α*`: the normalized left Perron vector of `M = P_T · diag(e_accept)` restricted to
`S = {x : A(K(x)) > 0}`.

*Proof.* For `T > 0`, `0 < p_du(T) < a < p_uu(T) < 1`. So each row of `P_T` in Lemma 1 is a convolution of two
binomials with full supports `{0..k}` and `{0..n−k}`, which has full support `{0..n}`. Hence `P_T > 0` entrywise. In the
domain variant the per-domain kernel is a Kronecker product of positive matrices and is positive, and so is its
`D`-fold product. After the first accepted audit `α` is supported in `S`, and `M` restricted to `S × S` is strictly
positive. The Perron-Frobenius theorem for positive matrices gives a simple dominant eigenvalue with a positive left
eigenvector. Normalized iterates from any nonnegative nonzero start converge to it geometrically (Birkhoff
contraction of the Hilbert projective metric). ∎

**Metric 1** (frozen): `r_1(T) = sup_{0 ≤ u < T} α* P_u 1_{<t}`. This is the risk a dispute faces, at the worst point in an
audit cycle, after a long unbroken record of accepted audits. The runner evaluates `α*` by iteration (tolerance
`1e−13` in `L1`) and the supremum on 97 equally spaced offsets of `[0, T]`, the endpoint being the limit `u → T`.

## 4. Undetected catastrophe in steady state

**Metric 2** (frozen): the long-run probability that a dispute is catastrophic although the most recent audit before
it accepted,

`F(T) = (1/T) ∫_0^T (π ⊙ e_accept) P_u 1_{<t} du`.

This follows from stationarity, the independence of `τ` (the offset `u` is uniform on `[0, T)`) and Theorem 3 with one
audit. `F` is a finite sum of exponentials in `u`. The runner integrates it with 24-point Gauss-Legendre.

**Theorem 5 (closed-form bound).** Without domain shocks, for every `T > 0`,

`F(T) ≤ A(t−1) · π(K < t) + Σ_{k ≥ t} π(k) A(k) · Pr[Bin(k, p_uu(T)) < t]`,

with `π = Bin(n, a)` and `A` the hypergeometric tail. The right-hand side is non-decreasing in `T`.

*Proof.* Split `F` by the state `k = K(0)` at the audit. For `k < t`, bound `Pr_k[K(u) < t] ≤ 1` and
`A(k) ≤ A(t−1)` (monotonicity of `A`). For `k ≥ t`, let `U(u)` be the number of the `k` custodians up at 0 that are
up at `u`. Then `K(u) ≥ U(u)`, because custodians down at 0 can only add. Also `U(u) ~ Bin(k, p_uu(u))`, so
`Pr_k[K(u) < t] ≤ Pr[Bin(k, p_uu(u)) < t]`. Since `p_uu` is decreasing in `u`
(`d p_uu/du = −(1−a)(λ+μ) e^{−(λ+μ)u} < 0`) and the binomial is stochastically increasing in its success probability,
`Pr[Bin(k, p_uu(u)) < t] ≤ Pr[Bin(k, p_uu(T)) < t]` for `u ≤ T`. Averaging over `u` keeps the bound. The same two
facts show that the right-hand side is non-decreasing in `T`. ∎

**Corollary 6 (frequency floor).** `F(T) → F_0 = Σ_{k<t} π(k) A(k) ≤ A(t−1) · π(K < t)` as `T → 0`
(`P_u → I`, and the integrand is continuous). Auditing more often cannot push the undetected-catastrophe probability
below `F_0`. A target `ε < F_0` needs a stronger design `(s, q)`, which lowers `A(k)` for `k < t`, or a larger
availability margin. Auditing faster does not help.

## 5. Design result

For a risk target `ε` and a design `(s, q)`, the audit interval to deploy is the largest `T` with risk at most `ε`.
Longer intervals mean fewer audits, so this is the cheapest interval that meets the target:

- `T_1(ε) = sup{T : r_1(T) ≤ ε}` and `T_2(ε) = sup{T : F(T) ≤ ε}`, found by bisection on `log T` over
  `[0.25 h, 30 d]`. Bisection assumes monotonicity in `T`. This is not proved for `r_1` or `F`, so the runner checks it
  on 25 log-spaced points and reports the result next to each interval.
- `T_B(ε) = sup{T : bound(T) ≤ ε}` from Theorem 5. The bound is proved non-decreasing, so bisection is exact and
  `T_B(ε) ≤ T_2(ε)` is a guaranteed, conservative design (independent model).
- If `ε < F_0`, no interval meets the target (Corollary 6). The runner reports `infeasible_at_lo` when even
  `T = 0.25 h` fails.

The largest interval meeting each target on the frozen grid `T ∈ {1, 6, 24} h` is reported as well.

## 6. Implementation check by simulation (R2_TEMPORAL_SIM_CHECK)

An event-driven simulation with exponential holding times (no closed forms) runs on the three frozen cells.
Each cell has 200,000 recorded audit intervals after 10,000 burn-in intervals, with frozen seeds
`SHA256("KEYSTONE-R2|TEMPORAL|" + cell_id)`. In each interval it records:

- the audit outcome,
- the state at a uniform dispute offset, and
- `K` at the audit.

It compares each estimate with the exact value:

- `Pr[accept]` (stationary),
- metric 2,
- stationary `Pr[K < t]`,
- `Pr[K(τ) < t | the last 8 audits accepted]` (exact by Theorem 3 with eight accepted outcomes), which stands in for
  metric 1 because the all-accepted fixed point cannot be sampled directly,
- the occupancy `Pr[K = k]` at audit times for every `k` with exact probability at least `1e−3`.

The frozen criterion is a 99% Wilson interval. Consecutive intervals are correlated when `MTTR` is comparable to `T`,
which makes Wilson intervals too narrow, so a 99% batch-means interval (100 batches) is reported as a diagnostic. A miss
is investigated as a possible implementation error and logged.

Catastrophe probabilities in some frozen cells are far below `1/200,000`. There the simulation observes no events
and checks only that the exact value is small. This limits what those cells can show and is reported as such.

## 7. Claim boundary

- Exact under the declared model: independent exponential custodian and domain chains, non-selective faults,
  fresh uniform samples, disputes independent of the process.
- Synthetic parameters (MTBF, MTTR, domain rates); no field data.
- Says nothing about adaptive adversaries who answer audits and withhold disputes (W4(a), future work).

## Addendum (2026-10-23): monotonicity of U, and numbering in the article

Added after the temporal results existed and after an AI cold read of the article. It proves a property
that the frozen analysis had assumed and checked numerically; no number or analysis changes.

**Proposition 7 (monotone undetected failure).** With or without domain shocks, U(T) (metric 2, the
F(T) of Section 4) is non-decreasing in T and U(T) >= U_0 = sum_{k<t} pi(k) A(k) for every T > 0.

*Proof.* Order states coordinatewise (K; or each domain state and member count). A is non-decreasing
and 1_{<t} non-increasing in this order. The chain (i) is reversible with respect to pi (a product of
two-state and birth-death chains), (ii) changes one coordinate by one step per transition, and (iii)
maps non-increasing functions to non-increasing functions under P_u, because p_uu(u) >= p_du(u). With
g(u) = <A, P_u 1_{<t}>_pi, g'(u) = -E(A, P_u 1_{<t}), where E is the Dirichlet form
(1/2) sum pi(x) L(x,y) (f(y)-f(x))(h(y)-h(x)). By (ii) every jump joins comparable states, and by (iii)
each term is <= 0, so g' >= 0. U(T), the running mean of g, is then non-decreasing and at least g(0) = U_0.

Consequences: Corollary 6 holds for every T, not only in the limit; the bisection for the metric-2
interval is exact. Monotonicity of metric 1 (posterior risk) is not proved.

**Numbering and notation in the article.** Theorem 3 here is the article's Theorem 2; Proposition 4 is the
limit stated after it; Theorem 5, Corollary 6 and Proposition 7 together are the article's Theorem 3. The
article writes Z for K, omega for pi, (phi, psi) for (lambda, mu), v for a, U and U_0 for metric 2 and its
floor, and R(T) for metric 1, to avoid clashes with its other notation.
