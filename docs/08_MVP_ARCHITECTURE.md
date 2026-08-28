# Minimum Publishable Prototype Architecture

## 1. MPP objective

Build the smallest artifact that directly tests the paper’s central property without building a complete AI rollup.

The MPP includes:

- encrypted inference-receipt object;
- epoch threshold-KEM committee;
- canary readiness audit;
- authorized dispute decryption;
- evidence records;
- uniform and stratified sampling;
- independent/correlated/selective fault simulator;
- analytical bound calculator;
- paper figures and benchmarks;
- Solidity bulletin-board interface.

## 2. Technology choices

| Layer | MPP technology | Reason |
|---|---|---|
| Crypto/protocol | Python 3.11+ | fastest formal-to-code iteration and reproducibility |
| AEAD | `cryptography` AESGCM | authenticated record/key wrapping |
| Tests | pytest | concise TDD and deterministic verification |
| Simulation | Python standard library | no heavy dependency required |
| Figures | matplotlib | reproducible paper plots |
| Ledger interface | Solidity 0.8.24 skeleton | natural rollup/dispute integration boundary |
| Diagrams | Graphviz + Mermaid | editable and renderable |

## 3. Code modules

| Module | Responsibility |
|---|---|
| `group.py` | subgroup parameters, transcript scalar hashing |
| `shamir.py` | sharing, interpolation, Feldman validation |
| `dleq.py` | context-bound Chaum–Pedersen proofs |
| `threshold_kem.py` | epoch key, record sealing, partials, combination/opening |
| `sampling.py` | exact bounds and deterministic sample derivation |
| `protocol.py` | custodian behavior, audit/dispute execution, evidence |
| `simulation.py` | independent/domain/selective failure Monte Carlo |
| `cli.py` | demo, bound, and simulation commands |
| `scripts/run_experiments.py` | datasets and Figures 1–5 |
| `scripts/benchmark_crypto.py` | operation-level latency table |

## 4. Trust boundaries

- Python dealer key generation is a research substitute, not a trusted production dealer recommendation.
- The simulator’s domain metadata is assumed accurate.
- The contract records responses; it does not verify large DLEQ proofs on-chain.
- Authorized plaintext handling is represented by the combiner; a production TEE/HSM adapter is external.
- The prototype demonstrates cryptographic mechanics and research measurements, not hardened key custody.

## 5. Implemented end-to-end path

1. Generate threshold epoch.
2. Seal an encrypted record with threshold KEM + AES-GCM.
3. Create fresh canary.
4. Generate and verify sampled DLEQ partials.
5. Produce invalid/non-response evidence in adversarial tests.
6. Open target record with `t` valid partials.
7. Reject `t-1` or proof-invalid partial sets.
8. Simulate independent, correlated, and selective failures.
9. Regenerate analytical/empirical figures and benchmark table.

## 6. Definition of MPP done

- [x] Exact property and claim boundary frozen.
- [x] Cryptographic round-trip works.
- [x] Invalid proof is rejected.
- [x] Threshold insufficiency is rejected.
- [x] Static false-accept formula implemented.
- [x] Uniform and stratified sampling implemented.
- [x] Correlated outage model implemented.
- [x] Selective-withholding limitation encoded as a test/figure.
- [x] One-command reproducibility script exists.
- [x] Paper-oriented diagrams, datasets, and documentation included.
- [ ] External cryptographer reviews proof transcript/domain separation.
- [ ] Distributed multi-process deployment measures network/ledger latency.
- [ ] Production DKG/PVSS replaces dealer setup.
- [ ] Contract is compiled, fuzzed, and gas-benchmarked in Foundry.

The unchecked items are full-paper strengthening tasks, not blockers for the minimum publishable prototype.

## 7. Recommended next implementation increment

Create a Docker Compose testbed with 32 custodian processes, four network domains, a coordinator, and an Anvil chain. Preserve the current Python interfaces so the simulator and distributed testbed consume the same scenario schema.
