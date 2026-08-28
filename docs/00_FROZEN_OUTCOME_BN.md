# Frozen Outcome — বাংলা পূর্ণ ব্যাখ্যা

## Final recommendation

**GO — 8.1/10 overall**, তবে শুধু এই frozen framing-এ:

> KEYSTONE একটি নতুন cryptographic primitive নয়; এটি encrypted rollup dispute-এর জন্য একটি নতুন formal property boundary, non-revealing readiness-audit composition, probability/correlation analysis, এবং accountable systems protocol।

এই distinction না রাখলে novelty score প্রায় `4.5–5.5/10`-এ নেমে যাবে। Frozen framing রাখলে claimability, feasibility এবং MPP readiness একসাথে শক্ত হয়।

## Overall score

| Dimension | Score | Meaning |
|---|---:|---|
| Problem significance | 8.5/10 | Private AI dispute সত্যিই decryption-service liveness-এর উপর নির্ভর করে |
| Primitive novelty | 3.0/10 | intentionally claimed নয় |
| Property/formalization novelty | 7.8/10 | strongest research contribution |
| Protocol composition novelty | 7.2/10 | canary PoP + sampling + policy/deadline composition |
| Claimability | 7.6/10 | narrow wording ও strong prior-art table প্রয়োজন |
| Technical feasibility | 8.8/10 | core prototype already runs |
| Evaluation potential | 8.5/10 | analytical, Monte Carlo, crypto overhead, adversarial cases |
| MPP readiness | 9.0/10 | runnable code, tests, figures, datasets included |
| Top-tier full-paper readiness now | 5.8/10 | distributed testbed/DKG/strong extension এখনও প্রয়োজন |
| Weighted final outcome | **8.1/10** | strong MPP/working-paper direction |

## Paper-এর এক বাক্যের contribution

> We formalize dispute-key availability as deadline-bounded, authorized reconstructability distinct from ciphertext data availability, and instantiate it with non-revealing canary partial-decryption sampling, explicit false-accept bounds, correlation-aware committee audits, and public deadline evidence.

## Novelty কোথায়

Novelty threshold encryption-এ নয়। Novelty হলো চারটি boundary একসাথে করা:

1. **Available bytes বনাম available decryption capability** আলাদা property।
2. **Secret object public sample না করে readiness sample** করা।
3. **Static/correlated failure assumptions-এর অধীনে explicit probability bound**।
4. **Dispute authorization ও deadline evidence-এর সাথে protocol wiring**।

## কেন canary প্রয়োজন

Production ciphertext-এর partial decryptions নিয়মিত publish করলে সময়ের সাথে adversary ভিন্ন custodians-এর `t`টি contribution জড়ো করে আগেভাগে record decrypt করতে পারে। KEYSTONE finalized beacon, epoch এবং audit slot থেকে `X=HashToGroup(...)` deterministically derive করে; mappingটি `g`-এর তুলনায় canary-এর discrete log প্রকাশ করে না। Custodian `X^{x_i}` দেয় এবং DLEQ proof দেখায় যে সে registered public share-এর একই secret exponent ব্যবহার করেছে। Coordinator canary বেছে নিতে পারে না, এবং combined canary value কোনো production record খুলে না।

## Freeze করা architecture

- epoch-level threshold key;
- per-record random AES data key;
- threshold KEM দিয়ে data key wrap;
- actual record DA layer-এ encrypted;
- canonical beacon-derived hash-to-group audit canary, never record ciphertext;
- beacon-driven uniform/stratified sample;
- DLEQ proof verification;
- public request/deadline bulletin board;
- authorized dispute-এ `t` partial decryptions;
- optional TEE destination;
- external DKG/PVSS/PSS integration boundary।

## সবচেয়ে গুরুত্বপূর্ণ limitation

Sampling future availability প্রমাণ করে না। বিশেষ করে selective withholding attacker:

- audit-এ response দেয়;
- target dispute শনাক্ত করে;
- ওই request-এ response বন্ধ করে।

Package-এর Figure 4 এই attack intentionally দেখায়। এটাকে গোপন না করে formal limitation হিসেবে লেখা paper-এর credibility বাড়াবে। Stronger follow-on contribution হতে পারে request indistinguishability, encrypted authorization, bonded pre-commitment, বা an impossibility/assumption theorem।

## Fast success path

MPP-এর জন্য full AI rollup বানাবে না। শুধু:

- encrypted inference receipt object;
- threshold KEM committee;
- audit coordinator;
- dispute release path;
- bulletin-board contract;
- fault simulator;
- figures/tables।

এতেই central research question directly evaluate হয়।
