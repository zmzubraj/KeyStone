# Defeating Evidence Matrix

Status: `DRAFT_INDEPENDENT_CHALLENGE`
Date accessed: `2026-08-29`

## Read this table conservatively

- `Direct overlap` means the source explicitly covers a KEYSTONE claim slice.
- `Defeat strength` is my adversarial assessment of how much that source weakens the frozen novelty wording.
- Absence of a full defeat is not a novelty pass; it only means this bounded challenge did not find a single source that collapses the entire composite claim.

| Source | Direct overlap with KEYSTONE claim | What this threatens | What still appears different | Defeat strength |
| --- | --- | --- | --- | --- |
| `ETHTID` (2021) | Threshold-shared decryption key, explicit future release time, safety/liveness, on-chain deadlines, deposits, scheduled reconstruction | The broad idea of deadline-bounded authorized reconstructability on chain is not new | No pre-authorization readiness audit; no canary partial decryptions; no churn/correlation sampling | strong partial |
| `Ferveo` (2022) | Encrypted transaction flow, threshold decryption after finalization, mempool/rollup-adjacent setting | The broad "encrypted rollup uses threshold decryption with liveness after ordering/finalization" framing is not new | No explicit audit of serviceability before authorized release; no public canary readiness protocol | strong partial |
| `Boneh et al. Accountability` (2023) | Threshold-decryption accountability; encrypted mempool motivation | Any claim to novelty from "accountable threshold decryption" alone | Focus is tracing leaked decoder misuse, not proving current serviceability before a dispute deadline | medium-strong partial |
| `Tas-Boneh DAC` (2023) | Query-triggered service availability, contract escalation, slashing, explicit success probability under bribes | Publicly auditable committee availability with on-chain enforcement is not new as a systems pattern | Data availability, not threshold decryption; no partial-decryption readiness test | medium-strong adjacent |
| `Time Lock Machines` (2024) | Reveal-verifiability in reconstruction stage; provisional challenge window for submitted shares; smart-contract threshold release | Novelty of public dispute windows and reveal-stage verifiability alone | Time-release setting; not dispute-key serviceability; not non-revealing pre-release sampling | medium partial |
| `Context-Dependent Threshold Decryption` (2025) | Explicit decryption context; shares under different contexts cannot be mixed; encrypted mempool application | Any novelty from context-bound decryption shares or context isolation alone | Does not by itself provide a canary sampling audit or correlation-aware readiness analysis | strong partial |
| `tTLES` (2025) | Formalization that decryption requires both inclusion and target time; blockchain threshold-decryption composition | Broad formal novelty around conditional authorized decryptability is weakened | Inclusion+time is not the same as "currently serviceable before dispute deadline"; no canary audit | strong partial |
| `BEAT-MEV` (2025) | Publicly testable partial decryptions and efficient batched decryption after finalization | Novelty of verifiable partial decryptions in threshold-encrypted transaction systems is weakened | Partial decryptions are for actual decryption flow, not a non-production serviceability probe | medium partial |

## Strongest combined objection

No single source found in this pass fully defeats the entire composite KEYSTONE intake claim. But the combination of prior work compresses the genuinely open territory sharply:

- `ETHTID` and `tTLES` attack the deadline-bounded / authorized-release formalization.
- `Ferveo` and `BEAT-MEV` attack the encrypted-transaction / threshold-decryption setting.
- `Context-Dependent Threshold Decryption` attacks context-bound share isolation.
- `Boneh accountability` and `DAC security` attack accountability and public enforcement patterns.

If KEYSTONE is described too broadly, reviewers could reasonably say it is an integration of known ingredients rather than a materially new problem or mechanism.

## Narrow remaining candidate differentiator

The narrow slice that I did **not** find preempted directly is:

`pre-authorization, non-revealing readiness auditing of dispute decryption serviceability using canary partial decryptions plus explicit false-accept analysis under churn/correlated failures`

Even that slice remains only a candidate differentiator, not a validated novelty result.
