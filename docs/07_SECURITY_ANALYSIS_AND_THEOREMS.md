# Security Analysis and Theorem Roadmap

## Theorem T1 — Threshold-KEM reconstruction correctness

Let shares be evaluations of a degree-`t-1` polynomial `f` with `f(0)=x`. For any distinct index set `I` of size `t`, each partial is `D_i=C1^{f(i)}`. Lagrange interpolation in the exponent yields:

`Π_{i∈I} D_i^{λ_i} = C1^{Σ_i λ_i f(i)} = C1^{f(0)} = C1^x`.

Therefore the combiner derives the same KEM shared secret as the encryptor and successfully authenticates the wrapped data key and record, assuming correct AEAD operation.

## Lemma L1 — Canary response correctness

An honest custodian holding share `x_i` produces `D_i=X^{x_i}` and a Chaum–Pedersen transcript accepted by the verifier.

## Lemma L2 — Canary response knowledge/soundness

Under the discrete-log assumption and Fiat–Shamir model used by the instantiated proof, a party that produces an accepting transcript for registered `Y_i` and challenge `X` demonstrates knowledge/use of the same exponent relation except with negligible probability. The paper should phrase this as use of an established DLEQ proof, not as a new primitive theorem.

## Theorem T2 — Static catastrophic-state false-accept bound

Suppose exactly `r<t` custodians are audit-ready during one request, and `s` members are sampled uniformly without replacement. If acceptance requires at least `q` valid responses:

`Pr[accept | r] = Σ_{j=q}^{min(s,r)} C(r,j) C(n-r,s-j) / C(n,s)`.

This probability is monotone in `r`, so the worst catastrophic case is `r=t-1`.

For `q=s`:

`Pr[false accept] ≤ C(t-1,s)/C(n,s)`.

Frozen baseline:

- `n=32`
- `t=22`
- `s=q=8`
- `P_FA=0.01934628219389065`
- `P_detect=0.9806537178061093`

## Corollary C1 — Repeated static audits

If the catastrophic ready set remains fixed and each sample is independently unpredictable, the probability of false acceptance in all `m` audits is at most:

`(P_FA)^m`.

This corollary must not be applied to adaptive or time-varying selective withholding without an explicit temporal model.

## Proposition P1 — No unconditional future-availability inference

For any finite audit transcript, an adversary can behave honestly through the final audit and make at least `n-t+1` custodians unavailable immediately before a later dispute. Therefore current audit acceptance alone cannot imply unconditional future reconstructability.

This proposition is simple but central: KEYSTONE provides conditional evidence and risk reduction, not a time-independent proof.

## Theorem T3 — Conditional dispute liveness

Assume:

1. a valid dispute request is globally visible at time `τ`;
2. at least `t` custodians are dispute-ready for that request;
3. messages from those custodians to the authorized combiner arrive within `Δ_d`;
4. their shares and proofs are valid;
5. the target ciphertext remains available.

Then the authorized combiner opens the record by `τ+Δ_d`.

The result is deterministic conditioned on these assumptions. Probability enters through the readiness/failure model.

## Proposition P2 — Placement cap for one-domain tolerance

If every failure domain contains at most `n-t` shares, the complete loss of any one domain leaves at least `t` custodians. This is a sufficient, not necessary, placement rule.

For the frozen `n=32,t=22`, each domain should contain at most ten custodians; the baseline uses four groups of eight.

## Domain-stratified analysis

Uniform sampling has a closed hypergeometric form. Stratified sampling depends on domain sizes and domain states. For fixed ready counts `r_d`, the response-count distribution is a convolution of per-domain hypergeometric distributions. The MPP may:

- compute exact convolution for small `k,s`;
- use Monte Carlo for arbitrary correlated models;
- report confidence intervals and frozen seeds.

## Accountability soundness

### Positive evidence

Invalid proofs and equivocation are deterministic positive evidence when identity binding is secure.

### Negative evidence

No-response evidence proves absence from the canonical bulletin board, not necessarily malicious intent. A hard-slashing theorem requires network and timing assumptions. The MPP therefore separates:

- health warning;
- temporary inactivity penalty;
- committee replacement;
- hard slashing after adjudication.

## Security claims table

| Goal | Required assumptions | MPP evidence |
|---|---|---|
| Pre-dispute confidentiality | fewer than `t` compromised shares, secure KEM/AEAD | threshold construction and tests |
| Invalid partial detection | DLEQ soundness and identity binding | unit tests |
| Record opening with `t` | correct Shamir shares and AEAD | proof sketch and tests |
| Failure detection | static/declared sampling model | exact formula and simulator |
| Domain resilience | truthful domain metadata and placement | Monte Carlo evaluation |
| Deadline liveness | `t` ready nodes and bounded delivery | conditional theorem |
| Non-response accountability | canonical request clock plus timing model | contract interface, not unconditional theorem |
| Selective-withholding resistance | stronger request-indistinguishability/incentive assumptions | not claimed; counterexample evaluated |
