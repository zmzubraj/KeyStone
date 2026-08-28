# KEYSTONE Frozen Master Guide — বাংলা

## 1. Final frozen decision

**Status: GO — 8.1/10 for a minimum publishable paper/prototype.**

Frozen title:

**KEYSTONE: Auditable Dispute-Key Availability for Encrypted AI Rollups**

Frozen research category:

- নতুন threshold-encryption primitive নয়;
- নতুন VSS/PVSS/PSS primitive নয়;
- **formal security property + auditable protocol composition + analytical bound + adversarial systems evaluation**;
- selective withholding-কে solved claim না করে explicit limitation/counterexample হিসেবে রাখা হবে।

## 2. Paper-এর defensible novelty

1. Ciphertext availability এবং authorized dispute-time decryptability আলাদা করা।
2. Production ciphertext ব্যবহার না করে canonical hash-to-group canary দিয়ে threshold service readiness পরীক্ষা করা।
3. Static catastrophic state-এর exact hypergeometric false-accept bound দেওয়া।
4. Provider/region/software failure-domain correlation ও stratified sampling evaluate করা।
5. Public deadline, invalid response, equivocation এবং missing-response evidence interface দেওয়া।
6. One-command reproducible code, figures, datasets এবং contract boundary দেওয়া।

## 3. Frozen baseline

| Parameter | Value |
|---|---:|
| Committee `n` | 32 |
| Threshold `t` | 22 |
| Sample `s` | 8 |
| Required audit responses `q` | 8 |
| Failure domains | 4 × approximately 8 members |
| Worst catastrophic false accept | `C(21,8)/C(32,8) ≈ 0.0193463` |
| Detection per static audit | `≈ 98.0654%` |

Repeated-audit multiplication কেবল static failure set এবং independently unpredictable beacons-এর অধীনে ব্যবহার করা যাবে।

## 4. Architecture in one flow

1. Worker fresh record key `K_r` তৈরি করে।
2. Inference record AES-GCM দিয়ে `K_r`-এর অধীনে encrypt হয়।
3. Epoch threshold public key `PK_E` দিয়ে `K_r` wrap হয়; per-record Shamir shares তৈরি হয় না।
4. Encrypted envelope DA layer-এ যায়।
5. Audit slot commit হওয়ার পরে beacon sample ও canonical canary নির্ধারণ করে।
6. Sampled custodian `D_i=X^{x_i}` এবং DLEQ proof দেয়।
7. Audit verifier valid/invalid/missing responses classify করে।
8. Valid dispute হলে policy contract verifier set authorize করে।
9. At least `t` record-specific partial decryptions threshold KEM shared secret recover করে।
10. Authorized environment record খুলে re-execute করে এবং verdict final করে।

## 5. Role map

| Role | Holds secret? | Main duty | Failure evidence |
|---|---|---|---|
| Rollup worker | record key temporarily | seal record and publish commitment | malformed envelope/receipt |
| DA layer | no threshold share | retain encrypted record/receipt | retrieval failure |
| Custodian | one epoch share | audit and authorized dispute response | invalid proof, equivocation, missing deadline |
| Beacon | no | unpredictable post-commit seed | bias/predictability assumption violation |
| Audit coordinator | no | derive sample/canary and collect responses | non-canonical request is rejected |
| Policy contract | no | authorize requests and fix deadlines | public state/evidence |
| Authorized verifier | recovered record key temporarily | combine, decrypt, re-execute | outside core if malicious |
| Adjudicator | no | verify evidence and apply policy | governance/adjudication risk |

Full role details: `docs/05_ROLES_AND_RESPONSIBILITIES.md`.

## 6. Algorithm map

| ID | Algorithm |
|---|---|
| A1 | Epoch setup via external DKG/PVSS; dealer/Feldman in MPP |
| A2 | Record sealing with threshold KEM + AES-GCM DEM |
| A3 | Uniform beacon-derived sample |
| A4 | Failure-domain-stratified sample |
| A5 | Canonical hash-to-group canary derivation |
| A6 | Custodian audit partial + DLEQ proof |
| A7 | Audit response verification |
| A8 | Audit evaluation and evidence |
| A9 | Authorized dispute creation |
| A10 | Custodian dispute partial |
| A11 | Threshold combination and record opening |
| A12 | Evidence classification |
| A13 | Refresh/replacement/rotation policy |
| A14 | Adversarial Monte Carlo simulation |

Full pseudocode and complexity: `docs/06_ALGORITHM_CATALOG.md`.

## 7. Prototype structure

```text
prototype/
├── src/keystone/
│   ├── group.py          # research subgroup, hashing
│   ├── shamir.py         # shares, interpolation, Feldman checks
│   ├── dleq.py           # Chaum–Pedersen/Fiat–Shamir proof
│   ├── threshold_kem.py  # epoch key, record seal/open
│   ├── sampling.py       # exact bound, uniform/stratified sample
│   ├── protocol.py       # audit/dispute state and evidence
│   ├── simulation.py     # IID/domain/selective fault model
│   └── cli.py            # demo/bound/simulation commands
├── tests/                # 17 passing tests
├── scripts/              # baseline, experiments, benchmark
├── configs/              # frozen scenarios
└── results/              # CSV/JSON, figures, benchmark
```

## 8. One-command verification

```bash
cd prototype
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
./scripts/run_baseline.sh
```

Pass criteria:

- all 17 tests pass;
- threshold-valid partials decrypt the record;
- fewer than `t` valid partials cannot open it;
- tampered DLEQ response fails;
- exact baseline bound matches expected value;
- Monte Carlo data and five figures regenerate;
- selective-withholding experiment shows the audit/dispute gap rather than hiding it.

## 9. Publication path

### Minimum publishable workshop/technical report

Use the current formal property, theorem, runnable prototype, analytical/Monte Carlo experiments, five figures, and limitations section.

### Stronger full conference version

Add:

- production DKG/PVSS or a well-audited library integration;
- 32–128 node distributed testbed across real failure domains;
- compiled/fuzzed contract and gas table;
- exact or bounded stratified-analysis theorem;
- request-indistinguishability/selective-withholding defense or a formal impossibility boundary;
- independent cryptography and systems review.

## 10. Documents to read in order

1. `FREEZE.md`
2. `docs/00_FROZEN_OUTCOME_BN.md`
3. `docs/01_RESEARCH_POSITIONING.md`
4. `docs/03_FORMAL_SECURITY_MODEL.md`
5. `docs/04_PROTOCOL_SPECIFICATION.md`
6. `docs/06_ALGORITHM_CATALOG.md`
7. `docs/08_MVP_ARCHITECTURE.md`
8. `docs/17_7_DAY_MVP_SPRINT_BN.md`
9. `docs/10_EXPERIMENT_AND_EVALUATION_PLAN.md`
10. `docs/11_PAPER_BLUEPRINT.md`
11. `docs/14_PUBLICATION_SUCCESS_GATES.md`
12. `paper/reviewer_attack_matrix.md`

## 11. Freeze rule

Central claim, property, architecture, and limitation boundary change করা যাবে না unless an explicit **UNFREEZE** decision is recorded. Parameter sweeps, implementation hardening, proof polishing, and additional baselines are allowed without unfreezing.
