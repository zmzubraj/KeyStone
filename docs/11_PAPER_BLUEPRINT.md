# Paper Blueprint

## Frozen title

**KEYSTONE: Auditable Dispute-Key Availability for Encrypted AI Rollups**

## Abstract structure

1. Context: encrypted optimistic AI enables private records but disputes need threshold decryption.
2. Gap: ciphertext DA does not imply deadline-bounded key-service availability.
3. Definition: DKA and its component properties.
4. Construction: canary partial-decryption sampling, policy-bound dispute release, and deadline evidence.
5. Analysis: false-accept bound and correlation model.
6. Evaluation: prototype, fault scenarios, overhead, selective-withholding limitation.
7. Claim: conditional probabilistic assurance, not future-proof availability.

## Recommended section outline

### 1. Introduction

- motivating failure story;
- “DA is not enough” distinction;
- research question;
- contribution list;
- limitations paragraph.

### 2. Background and Related Work

- data availability sampling;
- threshold encryption and verifiable partial decryption;
- VSS/PVSS and DKG;
- proactive/dynamic secret sharing;
- proof of retrievability;
- encrypted mempools and threshold KMS;
- accountable liveness and slashing.

### 3. Model and Definitions

- entities/timeline;
- threat model;
- CA, VSR, AKR, AD, DDL, PAC, DKA;
- audit soundness and accountability definitions.

### 4. KEYSTONE Protocol

- epoch setup;
- record KEM/DEM;
- canary sampling;
- audit verification;
- authorized dispute release;
- evidence/recovery;
- domain-aware placement.

### 5. Analysis

- reconstruction correctness;
- DLEQ usage/security reference;
- hypergeometric theorem;
- repeated audit corollary;
- conditional liveness theorem;
- selective-withholding counterexample;
- correlation analysis.

### 6. Implementation

- module architecture;
- cryptographic suite;
- contract bulletin board;
- assumptions and substitutions.

### 7. Evaluation

- RQs and methodology;
- analytical validation;
- independent/correlated faults;
- sampling strategies;
- selective withholding;
- crypto/network/contract overhead.

### 8. Discussion

- parameter selection;
- honest-versus-malicious nonresponse;
- TEE policy;
- refresh versus rotation;
- economics;
- deployment guidance.

### 9. Limitations and Future Work

- future availability impossible from finite samples without temporal assumptions;
- adaptive selective withholding;
- domain metadata truthfulness;
- production DKG and audited crypto;
- authorized-verifier compromise.

### 10. Conclusion

Restate dual availability and the conditional nature of the guarantee.

## Frozen contribution paragraph

> This paper makes five contributions. First, it formalizes dispute-key availability as a deadline-bounded authorized reconstructability property distinct from ciphertext availability and initial share validity. Second, it presents a confidential readiness audit in which randomly sampled custodians execute verifiable partial decryptions over fresh canary challenges rather than production ciphertexts. Third, it derives explicit false-accept bounds for static catastrophic states and states the temporal assumptions required for repeated audits. Fourth, it extends evaluation to correlated failure domains and public deadline evidence. Fifth, it provides a reproducible prototype and adversarial evaluation, including a selective-withholding counterexample that precisely limits the guarantee.

## Page budget for a 14-page main paper

| Section | Pages |
|---|---:|
| Introduction | 1.5 |
| Background/related work | 1.5 |
| Model/definitions | 2.0 |
| Protocol | 2.5 |
| Analysis | 2.0 |
| Implementation/evaluation | 3.0 |
| Discussion/limitations | 1.0 |
| Conclusion | 0.5 |

## Reviewer attack checklist

- Is “key availability” already a generic term? Narrow to DKA.
- Is the protocol just threshold encryption? Lead with property separation and audit semantics.
- Does PoP imply future response? Explicitly no; show counterexample.
- Can audits leak production plaintext? Use fresh canaries and explain transcript safety.
- Why not ping nodes? A heartbeat does not exercise a valid current share/proof path.
- Why not full committee every time? Quantify bandwidth and sample tradeoff.
- What about correlated failures? Include placement and stratified evaluation.
- Can non-response be slashed fairly? State timing assumptions and graded penalties.
- Why AI-specific? AI rollup is the motivating application; definitions can generalize to encrypted optimistic execution.
- Is TEE central? No; it is an authorized destination adapter.
