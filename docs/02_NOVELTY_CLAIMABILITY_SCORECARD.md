# Novelty, Claimability, Feasibility, and Publication Scorecard

## Weighted decision

| Criterion | Weight | Frozen score | Weighted contribution |
|---|---:|---:|---:|
| Problem significance | 0.20 | 8.5 | 1.70 |
| Defensible novelty | 0.25 | 7.4 | 1.85 |
| Formal tractability | 0.15 | 8.5 | 1.275 |
| Prototype feasibility | 0.15 | 8.8 | 1.32 |
| Evaluation strength | 0.15 | 8.7 | 1.305 |
| Prior-art/claim risk | 0.10 | 6.5 | 0.65 |
| **Total** | **1.00** |  | **8.10/10** |

## Claim-by-claim assessment

| Claim candidate | Novelty | Feasibility | Claimability | Frozen status |
|---|---:|---:|---:|---|
| Broad “key availability” property | 3/10 | 10/10 | 2/10 | rejected |
| Rollup-specific deadline-bounded DKA | 8/10 | 9/10 | 7.5/10 | primary |
| Proof of valid share possession | 2/10 | 9/10 | 1/10 | building block only |
| Canary partial-decryption sampling | 6.5/10 | 9/10 | 6/10 | protocol claim |
| Static false-pass bound | 5.5/10 | 10/10 | 6/10 | analytical claim |
| Correlation-aware placement/sampling | 7/10 | 8.5/10 | 6.5/10 | secondary claim |
| Deadline evidence for invalid response | 5/10 | 8/10 | 5/10 | systems claim |
| Generic non-response slashing | 4/10 | 5/10 | 3/10 | narrowed to model |
| TEE-gated threshold release | 2/10 | 8/10 | 1/10 | integration only |
| Cryptographic decryption-context binding | 2/10 | 7/10 | 1/10 | prior art; integration only |
| Consensus-authorized decryption/bulletin board | 2.5/10 | 8/10 | 1.5/10 | prior art; systems boundary only |
| Selective-withholding resistance | 8/10 | 5/10 | 6.5/10 | optional extension |
| Dual availability: ciphertext + key service | 8/10 | 9/10 | 7.5/10 | framing claim |

## Readiness by publication level

| Target level | Current readiness | Missing evidence |
|---|---:|---|
| Internal research memo | 10/10 | none |
| Reproducible technical report/arXiv | 8.8/10 | formal prose polish and expanded related work |
| Focused workshop paper | 8.2/10 | complete experiment matrix and external review |
| Full blockchain/security conference paper | 6.5/10 | distributed testbed, production DKG/PVSS, contract measurements |
| Top-tier security/systems paper | 5.8/10 | deeper theorem/strong extension, audited implementation, broad evaluation |

## Decision rule

Proceed when the paper stays inside the frozen claim boundary. Pause and unfreeze if the project starts relying on “first threshold encryption for AI,” “proof of future availability,” or a fully adaptive selective-withholding guarantee without a new construction or impossibility theorem.

### Why the total remains 8.10 after the 2026 adjacent-work pass

The score does **not** credit context binding, finalized-state authorization, bulletin boards, threshold release, PVSS/PSS, or generic accountability as novelty. The defensible-novelty score is attached only to the combined DKA property boundary, non-production readiness sampling, exact false-accept analysis, correlation-aware evaluation, and encrypted-rollup dispute use case. If any direct prior work is found that combines all of those elements, recompute the score and unfreeze the claim set.
