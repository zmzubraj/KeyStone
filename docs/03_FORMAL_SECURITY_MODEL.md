# Formal Security Model

## 1. System parameters

Let:

- `λ` be the security parameter;
- `n` be the number of custodians;
- `t` be the threshold;
- `s` be the audit sample size;
- `q` be the number of valid sampled responses required for audit acceptance;
- `Δ_a` be the audit response deadline;
- `Δ_d` be the authorized dispute response deadline;
- `E` be an epoch with threshold public key `PK_E`;
- `C_r` be the encrypted record for record identifier `r`.

Each custodian `i∈[n]` holds a share `x_i` and has a registered public share `Y_i=g^{x_i}`. A record uses a fresh data key `K_r`, encrypted by an AEAD scheme. `K_r` is wrapped through a threshold KEM under `PK_E`.

## 2. Entities

- Rollup worker/operator `W`
- Data-availability layer `DA`
- Custodian committee `C={C_1,…,C_n}`
- Randomness beacon `B`
- Audit coordinator/watcher `A`
- Policy and dispute contract `P`
- Authorized verifier/combiner `V`
- Adjudicator/slashing logic `J`

## 3. Time and network model

The ledger supplies an ordered public clock. A request committed at ledger time `τ` has deadline `τ+Δ`. Positive cryptographic evidence is timing-independent. A missing response is attributable only under the paper’s declared network assumption: requests and valid responses submitted by honest online participants reach the bulletin board inside the deadline budget.

The main analytical sampling theorem uses a **static readiness set** during one audit. Repeated-audit multiplication additionally assumes the catastrophic set remains static and each sample is independently unpredictable. The simulator separately models churn, domain outages, and selective withholding.

## 4. Readiness predicates

For request type `u∈{audit,dispute}`, define:

`Ready_i(E,τ,u,Δ)=1`

iff custodian `i` can access its current valid epoch share, execute the required partial-decryption operation, produce a valid proof, and deliver the response before `τ+Δ`.

Define the ready set:

`R_u(E,τ,Δ)={i∈[n] : Ready_i(E,τ,u,Δ)=1}`.

Audit and dispute readiness are deliberately separate. A selective withholder may belong to `R_audit` but not `R_dispute` for a target record.

## 5. Property decomposition

### 5.1 Ciphertext Availability (CA)

`CA(r,τ)` holds when an authorized verifier can retrieve the committed encrypted record and receipt bytes for `r` from the DA layer.

### 5.2 Valid-Share Registration (VSR)

`VSR(E)` holds when registered share commitments/public shares are consistent with one threshold public key and each admitted custodian received a valid share according to the chosen VSS/PVSS/DKG layer.

### 5.3 Audit-Time Key-Service Readiness (AKR)

Given sampled set `S` and canonical `X=H_G(E,slot,beacon)`, `AKR(E,S,τ)` holds when at least `q` sampled custodians return valid context-bound canary partial decryptions before `τ+Δ_a`. `H_G` is modeled as a domain-separated hash-to-group map whose output discrete logarithm is not exposed.

### 5.4 Authorized Decryptability (AD)

`AD(r,E,τ)` holds when a valid authorization for record `r` exists and the authorized combiner obtains at least `t` distinct valid partial decryptions for the record’s KEM ciphertext.

### 5.5 Dispute Deadline Liveness (DDL)

`DDL(r,E,τ,Δ_d)` holds when `AD` is completed no later than `τ+Δ_d`.

### 5.6 Pre-Authorization Confidentiality (PAC)

Before a valid authorization event, an adversary controlling fewer than `t` shares and the public transcript learns no information about `K_r` or the plaintext beyond the leakage of the base encryption/metadata scheme.

### 5.7 Dispute-Key Availability (DKA)

A protocol satisfies `(ε,Δ_d)`-DKA for a class of executions when, conditioned on the stated readiness/network assumptions and a valid authorization at `τ`, the authorized combiner obtains `t` valid contributions by `τ+Δ_d` with probability at least `1-ε`, while PAC holds before authorization.

DKA is therefore not unconditional future availability. It is a conditional, deadline-bounded service property.

## 6. Audit soundness definition

Let `Accept(E,S,X)` be the audit verifier’s decision. For a catastrophic audit-readiness state `|R_audit|<t`, define:

`P_FA = Pr[Accept(E,S,X)=1 | |R_audit|<t]`.

The protocol is `(n,t,s,q,ε_a)` audit-sound for the stated sampling model when `P_FA≤ε_a`.

When sampling uniformly without replacement and exactly `r` custodians are ready:

`Pr[accept | r] = Σ_{j=q}^{min(s,r)} C(r,j) C(n-r,s-j) / C(n,s)`.

The worst catastrophic state has `r=t-1`, yielding:

`ε_a = Σ_{j=q}^{min(s,t-1)} C(t-1,j) C(n-t+1,s-j) / C(n,s)`.

For `q=s`:

`ε_a = C(t-1,s)/C(n,s)`.

## 7. Accountability properties

### Invalid-response accountability

A response is positively attributable when it carries the custodian’s registered identity/signature and fails deterministic proof verification.

### Equivocation accountability

Two different signed/ledger-bound response commitments for the same request and custodian form positive evidence.

### Deadline-miss evidence

A public request plus an absent response at the deadline is objective ledger evidence of non-submission, but guilt attribution additionally depends on the declared network/timing assumption.

## 8. Adversary classes

- `A_conf`: compromises fewer than `t` shares and attempts early decryption.
- `A_invalid`: sends malformed or inconsistent partial decryptions.
- `A_crash`: makes custodians offline independently.
- `A_corr`: causes provider/region/software-domain correlated outages.
- `A_mobile`: compromises changing custodians across epochs; handled by external proactive refresh assumptions.
- `A_select`: answers routine audits but withholds a target dispute.
- `A_beacon`: attempts to predict or bias sampling or substitute a non-canonical canary.
- `A_request`: submits malicious or unauthorized dispute requests.

## 9. Explicit non-guarantees

The MPP does not prove:

- `Ready_i` at all future times from one current audit;
- liveness under arbitrary asynchronous partitions;
- confidentiality after compromise of `t` current shares;
- security of an authorized but malicious verifier/TEE;
- protection from all adaptive selective-withholding strategies;
- correctness of an external DKG/PVSS implementation.
