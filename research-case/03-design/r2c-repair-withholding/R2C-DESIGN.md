# R2c design: repair on alarm (M3) and selective withholding (M1)

Origin: the self-review of the R2b manuscript, items M3 and M1, in `paper/jcs/reviews/R3-REVISION-PLAN.md`.
Status: written before any R2c output existed. The machine-readable form is `r2c-design-freeze.json`, hashed in `r2c-design-freeze.SHA256SUMS`.
Label of every R2c number: EXACT_UNDER_DECLARED_SYNTHETIC_MODEL, except the simulation check, which is labelled SIMULATION_IMPLEMENTATION_CHECK.

## M3: repair on alarm

The custodian and domain model is that of R2_TEMPORAL_EXACT, with two changes: an alarm now triggers repair, and the
set of quantities computed is wider.

- At an audit at time a, the audit accepts with probability A(Z(a)), as in the paper's Theorem 1.
- If the audit rejects and no repair is pending, a resharing completes at a + D_r. At that moment every custodian
  becomes individually up. Domain states are unchanged, because resharing within the committee does not end a provider
  outage.
- A rejection while a repair is pending schedules nothing new.
- The grid requires D_r <= T, so a repair always completes before the next audit. Audits observe; repair is the only action.
- Exact method: the embedded chain at audit epochs has kernel
  M = diag(A) P_T + diag(1 - A) P_{D_r} Reset P_{T - D_r}.
  Its stationary law mu is found by power iteration to an L1 tolerance of 1e-13.
- Metrics per cell:
  - F_rep(T): the long-run probability that a dispute fails, with u uniform on [0, T), integrated with 24-point
    Gauss-Legendre on each piece.
  - U_rep(T): the long-run probability that a dispute fails and the latest audit accepted.
  - Repairs per day: 24/T times Pr_mu[reject].
  - Benign fraction: Pr_mu[reject and Z >= t] / Pr_mu[reject].
  - Audits per day: 24/T.
- Design: for each (s, q) and target eps in {1e-3, 1e-4, 1e-5}, find the largest T in [0.25 h, 30 d] with
  F_rep(T) <= eps. Use bisection on log T (40 iterations), with monotonicity checked on 25 log-spaced points, and
  report the audits and repairs per day at that T. No combined cost is formed, because there is no defensible weight.
- Grid:
  - MTBF in {7, 30, 90} d; MTTR in {1, 6, 24} h; T in {1, 6, 24} h.
  - Designs (s, q) in {(8, 8), (16, 14), (24, 20)}.
  - D_r in {0.25, 1} h.
  - Domain shocks: none, or MTBF_d in {90, 365} d with MTTR_d = 6 h.
  - Committee n = 32, t = 22, 4 domains of 8.
- Simulation check: the event simulation with exponential holding times, extended with the repair rule, on three cells:
  - MTBF 7 d, MTTR 24 h, T 6 h, (8, 8), D_r 1 h, no shocks
  - MTBF 7 d, MTTR 24 h, T 24 h, (16, 14), D_r 1 h, no shocks
  - MTBF 30 d, MTTR 6 h, T 6 h, (16, 14), D_r 1 h, MTBF_d 90 d
- Simulation runs: 200,000 intervals after a burn-in of 10,000. Seeds: SHA256("KEYSTONE-R2C|REPAIR|" + cell_id).
- Simulated quantities: Pr[reject], F_rep, U_rep and repairs per interval. Criterion: the exact value lies in the 99%
  Wilson interval; quantities with no events are reported as vacuous.

## M1: selective withholding

Static, per dispute. w selective custodians answer every audit (they are always audit-ready). The other n - w
custodians are each ready independently with probability v. The dispute succeeds if and only if at least t
non-withholders are ready.

- Exact table:
  - w in {0, 1, ..., 11}; v in {0.9, 0.99, 0.999}.
  - Dispute success Pr[Bin(n - w, v) >= t].
  - Audit pass, with ready count w + Bin(n - w, v) under hypergeometric sampling, for (s, q) in {(8, 8), (16, 14), (24, 20)}.
- Minimal coalition: for each v, the smallest w with Pr[dispute fails] >= 1/2 and the smallest w with
  Pr[dispute fails] >= 0.99.
- Accountability bound, stated as an inequality and not computed from data: if a failed dispute attributes each
  non-responder with probability p_a, then withholding by w custodians with stake S each is unprofitable when the
  blocked value V < w S p_a. The table reports the stake ratio S / V = 1 / (w_min p_a) for p_a in {0.5, 0.9, 1}.
- Proposition (paper), proved by construction: a custodian that answers every request except one it can identify as
  the target dispute has a transcript on all other requests identical to an honest one. So no test whose requests
  differ from the target dispute detects it. Decoy disputes over protocol-sealed records detect withholding as a policy
  (refusing a class of disputes) with probability equal to the decoy fraction per refusal. They do not detect
  withholding aimed at one known record.

## Outputs

`research-case/05-analysis/results/r2c/`:
- `repair-grid.csv`
- `repair-design.csv`
- `repair-sim-check.csv`
- `withholding.csv`
- `withholding-coalition.csv`
- `r2c-environment.json`

Each output carries the freeze hash.
