# Prior-Art Boundary and Reading Map

## Core comparison

### PeerDAS / EIP-7594

PeerDAS samples public encoded blob data to assess data availability while downloading a subset. KEYSTONE does not modify PeerDAS and does not claim a new DAS scheme. It asks whether a private threshold decryption service will be able to serve an authorized dispute.

Primary source: https://eips.ethereum.org/EIPS/eip-7594

### EigenAI

EigenAI uses encrypted receipts/data availability plus threshold KMS shares released to attested enclaves for private deterministic re-execution. Therefore “threshold-released keys for private AI verification” is prior art. KEYSTONE’s gap is a separately parameterized and audited key-service availability property/protocol.

Primary source: https://arxiv.org/abs/2602.00182

### VSS/PVSS

VSS/PVSS provides correctness/consistency and public verification properties for secret sharing. KEYSTONE relies on these as setup/refresh building blocks; it does not claim them.

Representative source: Berry Schoenmakers, “A Simple Publicly Verifiable Secret Sharing Scheme and Its Application to Electronic Voting,” CRYPTO 1999, https://dl.acm.org/doi/10.5555/646764.703956

### Proactive and dynamic secret sharing

PSS/DPSS refreshes or transfers shares under mobile compromise and changing committees. KEYSTONE adds an operational audit between setup/refresh events and ties it to dispute deadlines.

Representative source: Thomas Yurek et al., “Robust Asynchronous DPSS and its Applications,” USENIX Security 2023, https://www.usenix.org/system/files/sec23fall-prepub-356-yurek.pdf

### Robust/verifiable threshold decryption

Threshold encryption already supports partial decryptions, robustness, and identification of invalid shares in established constructions. KEYSTONE uses verifiable partial decryptions as audit responses.

Representative source: Dan Boneh, Xavier Boyen, and Shai Halevi, “Chosen Ciphertext Secure Public Key Threshold Encryption Without Random Oracles,” https://ai.stanford.edu/~xb/ctrsa06/threshold.pdf

### Context-dependent threshold decryption

Boneh, Bünz, Nayak, Rotem, and Shoup introduce **decryption contexts** that cryptographically isolate partial decryptions generated for the same ciphertext under different contexts. KEYSTONE must therefore not claim that binding decryption shares to a request/context is new. Production KEYSTONE should either integrate a context-dependent threshold-decryption construction or state clearly that the MPP's transcript-bound DLEQ proofs provide verification-domain binding but not the full cryptographic share-isolation guarantee of context-dependent threshold decryption.

Primary source: Dan Boneh et al., “Context-Dependent Threshold Decryption and its Applications,” IACR ePrint 2025/279 / ASIACRYPT 2025, https://eprint.iacr.org/2025/279

### Consensus-authorized threshold decryption and bulletin boards

A surfaced 2026 IEEE Access accepted-version paper, **UQ-Vote**, couples a PBFT-finalized bulletin board with consensus-authorized threshold decryption and explicit liveness/fault scenarios for voting. Consequently, authorization by finalized state, a public request log, and a decryption deadline are not independently claimable as new ideas. KEYSTONE's claim must remain the rollup-specific DKA property, pre-dispute confidential readiness sampling, false-accept/correlation analysis, and the separation between ciphertext DA and decryption-service availability.

Citation metadata to verify against the final IEEE record before submission: Jingyu Liu, Jingjing Rao, and Tetsutaro Uehara, “UQ-Vote: Consensus-Authorized Threshold Decryption for End-to-End Verifiable Elections,” DOI 10.1109/ACCESS.2026.3725080.

### Accountability in threshold decryption

Recent work adds traitor tracing/accountability for coalitions that leak decryption capability. That is different from KEYSTONE’s deadline non-response/readiness objective.

Representative source: https://eprint.iacr.org/2023/1724

### Accountable liveness

Formal accountable-liveness work shows that identifying liveness violators depends strongly on timing/network assumptions. KEYSTONE must not claim timing-free non-response guilt.

Primary source: https://arxiv.org/abs/2504.12218

### Encrypted mempools

Threshold-encrypted mempools provide adjacent operational experience with committees, epochs, timely decryption, collusion, and failure. They are essential related work but do not automatically define rollup DKA.

Representative source: https://www.usenix.org/system/files/usenixsecurity25-bormet.pdf

## Systematic search strings

- `"dispute-key availability" threshold rollup`
- `"decryption key availability" encrypted rollup`
- `threshold KMS readiness audit proof of possession`
- `threshold decryption liveness sampling`
- `share availability proactive secret sharing sampling`
- `encrypted mempool decryption failure availability`
- `accountable non-response threshold decryption`
- `proof of retrievability secret share`
- `TEE threshold key release liveness`

## Claim review rule

For every contribution sentence, maintain three columns:

1. established primitive used;
2. new KEYSTONE composition/property/analysis;
3. exact evidence in theorem, implementation, or experiment.

A contribution with an empty third column must be removed or converted into future work.

## 2026 submission-time watch rule

Run a fresh search immediately before abstract freeze for: threshold KMS readiness, context-dependent threshold decryption, consensus-authorized decryption, encrypted-rollup disputes, secret-share proof of retrievability, and adaptive selective withholding. Any new work matching one of those phrases must update the comparison table before a “first” or “novel” sentence is retained.
