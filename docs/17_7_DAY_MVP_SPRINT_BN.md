# ৭ দিনের Rapid MVP Sprint — KEYSTONE

## Sprint goal

সপ্তাহ শেষে এমন একটি reproducible research demo থাকবে যা একজন reviewer এক command-এ চালিয়ে audit, authorized opening, exact bound, fault simulation, figures এবং tests দেখতে পারবে। Current package এই sprint-এর working baseline; taskগুলো production-quality MPP polish-এর জন্য।

## Day 1 — Freeze and reproduce

- `FREEZE.md` এবং `MASTER_GUIDE_BN.md` team review;
- clean Python 3.11+ environment-এ `./scripts/run_baseline.sh` চালানো;
- generated hashes, Python/OS/CPU metadata record করা;
- failed install/run steps issue log-এ লেখা।

**Exit gate:** clean machine-এ 17 tests pass এবং five figures regenerate।

## Day 2 — Formal model lock

- CA, VSR, AKR, AD, DDL, PAC, DKA definitions notation-normalize;
- audit/dispute readiness আলাদা set হিসেবে রাখা;
- static-set, beacon, synchrony, threshold assumptions numbered list করা;
- Proposition: finite audits do not prove unconditional future availability formalize করা।

**Exit gate:** every claim in `paper/claims.md` points to a definition/theorem/test/figure।

## Day 3 — Protocol and transcript hardening

- canonical hash-to-group canary transcript freeze;
- chain ID, contract, version, epoch, slot, request ID, member index transcript fields specify;
- serialized response test vectors add;
- replay, stale epoch, wrong member, wrong context tests add;
- audit request cannot carry arbitrary/production `C1`—contract/interface validation specify।

**Exit gate:** canonical transcript table complete; negative tests pass।

## Day 4 — Contract compilation and evidence path

- Foundry install;
- bulletin-board contract compile;
- epoch/open/respond/finalize tests run;
- fuzz bitmap bounds and duplicate/equivocation flows;
- gas snapshot export;
- admin trust noted as MPP limitation।

**Exit gate:** `forge test` green এবং gas CSV available।

## Day 5 — Full experiment run

Run matrix:

- `n ∈ {16,32,64,128}`;
- threshold ratios `{1/2,2/3,3/4}` rounded safely;
- `s ∈ {4,8,12,16}`;
- `q ∈ {s,s-1,ceil(0.75s)}`;
- IID offline rate `0–0.5`;
- domain outage rate `0–0.5`;
- domains `{2,4,8}`;
- selective withholders `0–(n-t+1)`;
- uniform vs stratified vs full audit।

Use fixed seeds, at least 20,000 trials per main point, and confidence intervals.

**Exit gate:** raw CSV/JSON, manifest, figure captions, and exact-vs-Monte-Carlo sanity table।

## Day 6 — Paper assembly

- Introduction: availability gap and motivating failure;
- Related work: PeerDAS, threshold encryption, PVSS/PSS/DPSS, threshold KMS/private AI, encrypted mempools, accountable liveness;
- Model/definitions;
- protocol algorithms;
- theorem/proof sketches;
- experiment setup/results;
- limitations and ethics;
- artifact appendix।

**Exit gate:** complete 8–12 page workshop/technical-report draft, no empty contribution evidence।

## Day 7 — Reviewer attack and release

Run three reviews:

1. **Crypto reviewer:** Is canary merely generic PoK? Are group/transcript assumptions explicit?
2. **Distributed-systems reviewer:** Does deadline blame require unjustified synchrony?
3. **Blockchain reviewer:** Why is this not just PeerDAS + threshold KMS?

Then:

- soften/remove unsupported “first” wording;
- rerun clean artifact;
- update `VERIFICATION.md`, checksums, and release archive;
- tag `keystone-mpp-v1.1`।

**Exit gate:** every reviewer attack has evidence, limitation, or explicit future-work response।

## Minimal team ownership

| Workstream | Owner | Backup |
|---|---|---|
| Formal model/theorems | cryptography researcher | protocol engineer |
| Python crypto/simulator | protocol engineer | research engineer |
| Contract/evidence | Solidity engineer | protocol engineer |
| Experiments/statistics | research engineer | formal lead |
| Paper/related work | paper lead | all authors |
| Reproducibility/release | artifact lead | research engineer |

A solo author executes in that priority order and treats TEE integration as non-critical.
