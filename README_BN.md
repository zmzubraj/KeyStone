# KEYSTONE: বাংলা Executive Guide

## এক লাইনে frozen outcome

আমরা এটাকে **নতুন threshold-crypto primitive** হিসেবে claim করব না। আমরা এটাকে freeze করছি:

> **Encrypted AI rollup-এর জন্য Auditable Dispute-Key Availability:** authorized dispute শুরু হলে নির্দিষ্ট deadline-এর মধ্যে অন্তত `t`টি valid partial decryption পাওয়ার সম্ভাব্যতা/প্রস্তুতি, production key বা plaintext আগেভাগে প্রকাশ না করে audit করা।

Frozen title:

**KEYSTONE: Auditable Dispute-Key Availability for Encrypted AI Rollups**

Subtitle:

**Confidential Readiness Sampling, Correlation-Aware Bounds, and Deadline Accountability**

## কেন এই framing শক্তিশালী

PeerDAS ciphertext/blob data available কি না sample করে। Threshold encryption/VSS/PVSS share correctness ও decryption capability দেয়। EigenAI threshold KMS ও TEE-based private re-execution ব্যবহার করে। KEYSTONE-এর publishable gap হলো এই building blocks-এর মাঝখানে একটি আলাদা property ও protocol layer:

- ciphertext available হলেও key-service unavailable হতে পারে;
- valid share provision করা হয়েছে মানেই dispute deadline-এ custodian respond করবে না;
- সাধারণ heartbeat share possession cryptographically প্রমাণ করে না;
- actual production ciphertext-এর partial decryption audit হিসেবে প্রকাশ করা নিরাপদ নয়;
- random independent sampling correlated cloud/region outage miss করতে পারে;
- sampling unconditional future availability guarantee করে না।

## Frozen contribution set

1. **Formal property suite:** Ciphertext Availability, Share Validity, Audit Readiness, Authorized Decryptability, Deadline Liveness, এবং composite Dispute-Key Availability।
2. **Canary audit protocol:** finalized beacon, epoch ও audit slot থেকে canonical hash-to-group canary; partial decryption + DLEQ proof হয়, actual record decrypt হয় না।
3. **Analytical bound:** catastrophic state-এ false-pass-এর hypergeometric bound এবং repeated-audit bound।
4. **Correlation-aware sampling:** failure-domain metadata ও stratified sampling evaluation।
5. **Deadline accountability:** public request, response commitment, invalid proof/equivocation/non-response evidence interface।
6. **Runnable MPP:** crypto demo, simulator, tests, figures, datasets, contract skeleton, এবং paper blueprint।

## Frozen baseline parameters

| Parameter | Frozen baseline |
|---|---:|
| Committee size `n` | 32 |
| Threshold `t` | 22 |
| Audit sample `s` | 8 |
| Required valid audit responses `q` | 8 for the clean theorem; `q<8` evaluated separately |
| Failure domains | 4, approximately 8 custodians per domain |
| Static catastrophic false-pass bound | `C(21,8)/C(32,8) ≈ 0.0193463` |
| Static catastrophic detection per audit | `≈ 98.0654%` |
| Repeated audits | only under a static failure-set/independent beacon assumption |

## MVP run করার দ্রুত পথ

```bash
cd prototype
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
./scripts/run_baseline.sh
```

এতে crypto demo, bound calculator, Monte Carlo simulation, figures, benchmark এবং tests চলবে।

## কী সফল হলে MPP publishable বলব

- formal definitions internally consistent;
- theorem/closed-form bound simulator-এর সাথে match করে;
- invalid partial proof detect হয়;
- `t` valid partials record খুলে, `t-1` খুলতে পারে না;
- correlated outages independent model-এর চেয়ে materially different result দেয়;
- domain-stratified sampling একটি measurable advantage দেখায়;
- selective withholding limitation experiment স্পষ্টভাবে দেখানো হয়, লুকানো হয় না;
- full reproducibility package এক command-এ regenerate হয়।

## Aggressive timeline

- **দিন 1–3:** definitions, threat model, theorem statements freeze।
- **দিন 4–7:** current prototype polish, contract interface, benchmark।
- **দিন 8–12:** full experiment matrix ও figures।
- **দিন 13–16:** paper draft sections 1–6।
- **দিন 17–21:** related work, reviewer-attack review, reproducibility, arXiv-ready draft।

এই package-এর code core ইতিমধ্যে runnable; তাই remaining work-এর বড় অংশ formal writing, experiment expansion, এবং external review।

## Verification status

- Python crypto/simulator: **17/17 tests pass**।
- End-to-end encrypted receipt demo: successful।
- Frozen bound ও Monte Carlo datasets/figures: regenerated।
- Solidity bulletin-board source: **Solc 0.8.24 দিয়ে compile হয়েছে; বর্তমান Foundry tests 2/2 pass**।
- Baseline gas snapshot generated; fuzz/invariant tests এবং full contract-overhead table এখনও pending, তাই Day-4 research gate আংশিক complete।
- Reproducible workspace setup: root থেকে `make setup`, `make verify`, এবং `make reproduce`।
- পূর্ণ executed evidence: `VERIFICATION.md`।
- সর্বশেষ 2026 prior-art boundary: `docs/18_LATEST_PRIOR_ART_WATCH_2026-08-29.md`।
