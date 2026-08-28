# Frozen Claims and Required Evidence

| Claim | Assumptions | Evidence required |
|---|---|---|
| DKA is distinct from ciphertext DA | definitions/timeline | formal counterexample: ciphertext retrievable, fewer than `t` responders |
| Canary audits exercise valid current shares without using production ciphertext | DLEQ/threshold group assumptions | protocol proof sketch, transcript test, no-record audit code path |
| Static catastrophic false accept has hypergeometric bound | fixed ready set, uniform sample | theorem and exhaustive/Monte Carlo validation |
| Domain concentration increases outage risk | domain model truthful | placement theorem and experiments |
| Stratification improves detection for some correlated states | declared domain model | exact/Monte Carlo comparison |
| `t` verified partials open target record | correct shares/KEM/AEAD | theorem and tests |
| Invalid partials are attributable | signatures/identity binding | verification transcript and evidence event |
| Deadline liveness is conditional | bounded delivery and `t` ready nodes | conditional theorem and distributed test |
| Sampling does not defeat selective withholding | adversary distinguishes requests | counterexample test and Figure 4 |
| Context/authorization mechanisms are building blocks, not novelty | context-dependent threshold decryption and consensus-finalized authorization prior art | explicit related-work comparison and no standalone novelty wording |

## Wording rule

Each paper claim must end with either a theorem/lemma reference, an experiment/table reference, or a clearly labeled design rationale. Unsupported contribution wording is removed.

## Prohibited standalone novelty wording

Context binding, consensus authorization, public bulletin boards, threshold release, DLEQ proofs, and proactive refresh may appear only as adopted/integrated mechanisms. The contribution sentence must attach novelty to DKA readiness sampling and its analysis, not to these primitives.
