# Theorem Roadmap

- **Definition 1:** Ciphertext Availability.
- **Definition 2:** Valid-Share Registration.
- **Definition 3:** Audit-Time Key-Service Readiness.
- **Definition 4:** Authorized Decryptability.
- **Definition 5:** Dispute Deadline Liveness.
- **Definition 6:** Pre-Authorization Confidentiality.
- **Definition 7:** `(ε,Δ)` Dispute-Key Availability.
- **Definition 8:** Audit false accept and detection.
- **Lemma 1:** Correctness of honest canary partial and DLEQ transcript.
- **Lemma 2:** Context-binding and invalid-partial rejection.
- **Theorem 1:** Threshold KEM reconstruction correctness.
- **Theorem 2:** Hypergeometric false-accept bound.
- **Corollary 1:** Repeated static audit bound.
- **Proposition 1:** Finite audits cannot guarantee unconditional future availability.
- **Theorem 3:** Conditional dispute deadline liveness.
- **Proposition 2:** Single-domain placement cap.
- **Counterexample 1:** Selective audit/dispute withholding separation.
- **Optional Theorem 4:** Exact stratified acceptance distribution by convolution.

The current constructive separation obligations are enumerated in
`paper/property_separation_obligations.md`. They cover only: ciphertext
availability not implying deadline-bounded dispute-key availability, routine
audit acceptance not implying targeted authorized decryptability under
selective withholding, and finite audit observations not implying unconditional
future availability. A complete pairwise property lattice is not claimed.
