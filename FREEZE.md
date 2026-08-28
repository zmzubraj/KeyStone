# KEYSTONE Research Freeze Record

**Freeze ID:** KEYSTONE-MPP-F1  
**Date:** 2026-08-29  
**Status:** FROZEN FOR MPP IMPLEMENTATION

## 1. Frozen title

**KEYSTONE: Auditable Dispute-Key Availability for Encrypted AI Rollups**

Optional subtitle:

**Confidential Readiness Sampling, Correlation-Aware Bounds, and Deadline Accountability**

## 2. Frozen thesis

KEYSTONE defines and evaluates **Dispute-Key Availability (DKA)** as a property distinct from public ciphertext/data availability: after an authorized dispute event, a threshold of valid decryption contributions must reach the authorized combiner before a deadline, while pre-dispute confidentiality remains intact.

## 3. Frozen research question

> How can an encrypted AI rollup obtain publicly auditable, non-revealing evidence that at least `t` valid threshold-decryption contributions are currently serviceable for an authorized dispute before deadline `Δ`, under explicit churn and correlated-failure assumptions, without releasing a production key or plaintext before authorization?

## 4. Frozen contribution claims

- **C1 — Property:** a formal property suite separating ciphertext availability, share validity, audit-time readiness, authorized decryptability, and deadline liveness.
- **C2 — Protocol:** unpredictable canary challenges whose sampled custodians return partial decryptions with context-bound DLEQ proofs.
- **C3 — Analysis:** a hypergeometric false-accept/detection bound for static catastrophic states, plus repeated-audit bounds under explicitly stated temporal assumptions.
- **C4 — Correlation:** failure-domain-aware committee placement and stratified sampling evaluated under provider/region outages.
- **C5 — Accountability interface:** public request/deadline records and evidence types for invalid responses, equivocation, and deadline misses under the stated synchrony model.
- **C6 — Artifact:** an executable threshold-KEM prototype, adversarial simulator, tests, datasets, figures, and contract bulletin-board skeleton.

## 5. Claims explicitly prohibited in the MPP

The paper must not claim:

- a new threshold encryption primitive;
- a new VSS/PVSS or proactive secret-sharing primitive;
- the first proof of share possession;
- the first accountable threshold decryption system;
- unconditional proof of future availability;
- protection against a fully adaptive selective-withholding adversary;
- TEE security as a contribution;
- production security of the included prototype.

## 6. Frozen architecture

1. Each epoch has one threshold public key `PK_e` and `n` custodian shares.
2. Each inference record uses a fresh symmetric data key `K_r`.
3. The record is encrypted with AES-GCM under `K_r`.
4. `K_r` is wrapped through a threshold DH KEM under `PK_e`; custodians do not store one Shamir object per record.
5. A routine audit uses the canonical canary `X = HashToGroup("KEYSTONE-CANARY" || epoch || slot || finalized_beacon)`, never a coordinator-chosen or production record element.
6. A sampled custodian returns `D_i = X^{x_i}` and a DLEQ proof that `log_g(PK_i)=log_X(D_i)`.
7. A public beacon determines the sample after the audit epoch is committed.
8. A dispute contract authorizes release for one record and one verifier-set identity.
9. At least `t` verified partial decryptions recover the KEM shared secret and unwrap `K_r` inside the authorized destination.
10. DKG/PVSS, proactive refresh, and TEE attestation are integration boundaries; the MPP does not reinvent them.

## 7. Frozen baseline configuration

- `n = 32`
- `t = 22`
- `s = 8`
- `q = 8` for the primary analytical result
- four failure domains with approximately eight custodians each
- per-domain placement cap `≤ n - t = 10`, so one complete domain outage cannot independently destroy reconstructability
- static catastrophic state: fewer than `t` dispute-ready custodians
- audit false accept in the most favorable catastrophic state: `C(t-1,s)/C(n,s)` when `q=s`

For the frozen baseline:

`P_FA = C(21,8)/C(32,8) = 0.01934628219389065`

`P_detect = 0.9806537178061093`

## 8. Frozen threat-model boundary

- Confidentiality assumes fewer than `t` custodian shares are compromised during an epoch.
- Deadline accountability requires a public clock/ledger and the declared synchrony/deadline assumptions.
- Beacon unpredictability is assumed until the sample is fixed.
- The DA layer makes ciphertext/receipt bytes retrievable; KEYSTONE does not replace DA.
- A compromised authorized verifier/TEE may reveal plaintext; that is outside the core DKA claim.
- Selective withholders may answer canary audits and refuse a targeted dispute; the MPP measures this gap and treats stronger resistance as follow-on work.

## 9. Change-control rule

The following changes require an explicit **UNFREEZE** decision:

- changing the central property from DKA;
- claiming primitive-level novelty;
- returning to per-record Shamir sharing;
- making TEE behavior the central novelty;
- claiming unconditional future availability;
- making adaptive selective-withholding resistance mandatory for the MPP;
- expanding the first paper into a complete production rollup.

Parameter sweeps, implementation optimizations, additional baselines, improved proofs, and wording refinements do not require unfreezing when they preserve the thesis and claim boundary.

## 10. Latest adjacent-work boundary

The freeze explicitly excludes standalone novelty for cryptographic decryption contexts and consensus-finalized decryption authorization/public bulletin boards. Those mechanisms are prior-art building blocks. This does not unfreeze the thesis because C1--C6 already attach the contribution to DKA separation, confidential readiness sampling, probability/correlation analysis, and the executable rollup-oriented artifact.
