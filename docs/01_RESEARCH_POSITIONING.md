# Research Positioning and Contribution Strategy

## 1. Recommended paper identity

KEYSTONE should be positioned as a **cryptographic-systems paper with a formal property contribution**, not as a new primitive paper.

The central observation is that encrypted rollups need two orthogonal resources:

1. retrievable ciphertext/receipt bytes; and
2. a serviceable threshold decryption capability after authorization.

Data-availability sampling addresses the first resource. Threshold encryption, VSS/PVSS, proactive refresh, and TEE-gated release supply components for the second. The paper studies the missing operational/security property connecting those components to a dispute deadline.

## 2. Frozen paper thesis

> Data availability is necessary but insufficient for private optimistic verification. An encrypted rollup also requires dispute-key availability: deadline-bounded access to enough valid decryption contributions after authorization, without reducing pre-authorization confidentiality.

## 3. Contribution hierarchy

### Primary contribution

A formal definition of **Dispute-Key Availability (DKA)** and its decomposition into independently testable properties.

### Secondary contribution

A **confidential readiness-sampling protocol** based on fresh canary partial decryptions and context-bound DLEQ proofs.

### Analytical contribution

Closed-form false-accept/detection bounds for static catastrophic states, plus explicit conditions under which repeated-audit multiplication is valid.

### Systems contribution

Failure-domain metadata, domain-aware placement/sampling, public deadline records, recovery/replacement triggers, and an executable prototype/evaluation.

### Optional strong extension

A protocol or impossibility result for selective withholding. This is not required for the MPP.

## 4. Safe novelty language

Use:

- “We formalize dispute-key availability for encrypted rollup disputes.”
- “We show that ciphertext DA and threshold-key serviceability are distinct.”
- “We instantiate a non-revealing readiness audit using established verifiable partial-decryption techniques.”
- “We derive explicit false-accept bounds under stated static and correlated failure models.”
- “To our knowledge, prior encrypted-rollup and threshold-decryption systems do not expose this property as a separately parameterized, sampled dispute-liveness objective.”

Avoid:

- “We invent key availability.”
- “We prove future key availability.”
- “We introduce proof of share possession.”
- “We introduce proactive threshold encryption.”
- “We solve selective withholding.”
- “Our slashing proof works without synchrony assumptions.”

## 5. Recommended title set

**Frozen primary:**

> KEYSTONE: Auditable Dispute-Key Availability for Encrypted AI Rollups

Backups:

- Data Availability Is Not Enough: Auditing Threshold-Key Readiness for Private Rollup Disputes
- Confidential Readiness Sampling for Threshold-Encrypted Rollup Verification
- Deadline-Bounded Decryptability for Encrypted Optimistic AI

## 6. Paper elevator pitch

Encrypted optimistic AI systems can publish ciphertexts to a data-availability layer and still fail exactly when a challenge needs decryption: enough key custodians may be offline, selectively withholding, invalid, or concentrated in a failed domain. KEYSTONE separates this failure from ciphertext DA, introduces a non-revealing canary audit for registered key shares, derives detection bounds, and evaluates committee configuration under churn, correlation, and adversarial behavior.

## 7. Reviewer-facing differentiation

| Existing area | What it already supplies | KEYSTONE boundary |
|---|---|---|
| DAS/PeerDAS | probabilistic availability of public encoded data | confidential serviceability of threshold decryption shares |
| VSS/PVSS | correctness/consistency of distributed shares | ongoing operational readiness and deadline response |
| Proactive secret sharing | refresh/reshare under mobile compromise and churn | sampled evidence between refresh events and during disputes |
| Threshold encryption | confidentiality and joint decryption | explicit rollup dispute authorization, deadlines, and failure probability |
| Proof of retrievability | sampled evidence that stored data can be retrieved | non-public share operation and threshold reconstruction semantics |
| Accountable liveness | conditions for identifying liveness violators | narrow bulletin-board evidence for custodian responses under declared timing assumptions |
| TEE-gated KMS | controlled plaintext/key release | readiness assurance before a specific dispute occurs |

## 8. Publication strategy

The minimum paper should emphasize:

- definitions and separations;
- one clean protocol;
- one clean theorem family;
- correlation-aware evaluation;
- honest limitations;
- a reproducible artifact.

Do not dilute the first paper with full deterministic inference, GPU reproducibility, complete rollup economics, generalized access control, post-quantum cryptography, or a new DKG.
