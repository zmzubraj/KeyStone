# Property-separation obligations

Status: `DRAFT — PREAUTHORIZATION ANALYTIC ARTIFACT`

Claim scope: `C001 / RID-C001-SEP-001`. This artifact records constructive
model witnesses that a later formal reviewer must check. It is not an
independent proof, novelty verdict, or claim of operational prevalence.

## Frozen notation

- `CA(r, tau)`: the committed encrypted record and receipt for `r` are
  retrievable at `tau`.
- `VSR(E)`: the epoch has consistent registered public shares and admitted
  custodians initially received valid shares.
- `AKR(E,S,tau)`: at least `q_accept` sampled custodians return valid canonical
  canary responses by the audit deadline.
- `AD(r,E,tau)`: after valid authorization, at least `t` distinct valid record
  partial decryptions are obtained.
- `DDL(r,E,tau,Delta_d)`: `AD` completes by `tau + Delta_d`.
- `(epsilon,Delta_d)-DKA`: conditioned on the declared readiness and network
  assumptions, authorized threshold contributions arrive by the deadline with
  probability at least `1-epsilon`, while pre-authorization confidentiality
  holds.

`q_accept` is the required valid-response count. It must never be confused
with `q_disc`, the paired outcome-discordance fraction used by prospective
paired analyses.

## Minimum claim-bearing witnesses

| Witness ID | State construction | Holds | Fails | Permitted conclusion | Explicit non-conclusion |
|---|---|---|---|---|---|
| `SEP-CA-NOT-DKA-RDISP-TM1` | The DA layer retains `C_r`, but only `t-1` current custodians can produce valid record partials by `tau+Delta_d`. | `CA(r,tau)` | `AD`, `DDL`, and the corresponding deadline-bounded DKA execution | Ciphertext availability alone does not imply dispute-key availability. | Does not estimate how often this state occurs. |
| `SEP-AKR-NOT-AD-SELECTIVE` | A sampled set supplies at least `q_accept` valid canary responses, while a target-aware selective withholder leaves fewer than `t` valid record responses at dispute time. | `AKR(E,S,tau)` | `AD` and `DDL` for the target record | A passed routine audit does not unconditionally imply targeted dispute success. | Does not invalidate the bounded static false-accept calculation under its own assumptions. |
| `SEP-FINITE-AUDITS-NOT-FUTURE-DKA` | Any finite audit prefix is identical across two executions; after the last audit, one continuation preserves at least `t` ready custodians and the other drops below `t` before a later authorized dispute. | the same finite audit observations in both executions | unconditional future `AD`/`DDL` in one continuation | Finite observations cannot guarantee unconditional future availability without temporal assumptions. | Does not preclude a conditional probabilistic forecast under a frozen temporal model. |

## Obligation checks

Each witness is admissible only if all of the following remain explicit:

1. the threshold, sample, `q_accept`, audit deadline, and dispute deadline are
   fixed for the witness;
2. audit readiness and target-record dispute readiness are separate predicates;
3. absence-based deadline attribution is conditioned on the declared network
   and bulletin-board delivery assumptions;
4. pre-authorization confidentiality is not inferred from a liveness witness;
5. the witness establishes logical non-implication only, not novelty,
   prevalence, effect size, deployment robustness, or production security; and
6. any repeated-audit expression states the readiness-state persistence and
   sample-independence assumptions required for multiplication.

## Pairwise-lattice boundary

The paper does **not** claim a complete pairwise independence lattice among
`CA`, `VSR`, `AKR`, `AD`, `DDL`, confidentiality, and DKA. Only the three
non-implications above are currently claim-bearing. Any additional arrow or
non-implication requires its own constructive witness or proof and independent
formal review before manuscript promotion.

## Required external closure

- qualified formal/cryptographic review of definitions and witness validity;
- strongest-prior-art reconciliation for the narrow property-separation claim;
- signed verification event bound to the final artifact hash; and
- manuscript wording constrained to the independently verified subset.
