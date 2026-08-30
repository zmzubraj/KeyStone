# Changelog

## 2026-08-29 — Exact sampling and uncertainty tranche

- Added an exact fixed-quota domain-stratified success distribution by
  convolution of per-domain hypergeometric PMFs.
- Added a hand-enumerated oracle and seeded Monte Carlo comparison.
- Added raw Monte Carlo counts and two-sided 95% Wilson score intervals.
- Regenerated CSV/figure evidence with uncertainty bands and added
  `exact_stratified_validation.csv`.
- Expanded the Python suite from 17 to 21 passing tests.

## 2026-08-29 — Canonical transcript tranche

- Added strict version-1 binary serialization for audit requests and partial
  responses, including chain/contract/epoch/request binding.
- Added domain-separated transcript hashes and rejection of noncanonical or
  trailing encodings.
- Added deterministic request/response fixtures in `paper/test_vectors.json`.
- Expanded the Python suite from 21 to 24 passing tests.

## 2026-08-29 — Temporal readiness pilot

- Added validated two-state and three-state custodian-readiness Markov models.
- Added deterministic transition/recovery and repeated-audit sequence tests.
- Added an exploratory temporal-dependence CSV and paper-table section that
  separates its evolving-state estimand from the static-set repeated bound.

## 2026-08-29 — Canonical response-signature tranche

- Added Ed25519 signatures over exact canonical partial-response transcript bytes.
- Added tamper, wrong-key, cross-chain, and cross-contract replay rejection tests.
- Added deterministic test-only signature vectors and freshness checks.
- Added 64-byte signature size plus local sign/verify latency to the cryptographic
  benchmark and generated paper tables.
- Expanded the Python suite from 24 to 32 passing tests, including the temporal pilot.

## 2026-08-29 — Experimental share-refresh tranche

- Added a dealer-based zero-polynomial share refresh that preserves the epoch
  public key and increments an explicit refresh generation.
- Bound canary derivation and protocol proof contexts to the refresh generation.
- Added tests for refreshed authorized opening, stale/mixed partial rejection,
  and generation-separated canaries/contexts.
- Expanded the Python suite from 32 to 35 passing tests.

## MPP contract hardening — 2026-08-29

- Rejected duplicate custodian identities and zero epoch descriptor commitments.
- Rejected zero audit/dispute subject bindings and zero invalid-response
  evidence hashes.
- Expanded the Foundry suite from 2 to 19 tests, including three 512-run fuzz
  properties and two stateful invariants at 64 runs × 32 calls.
- Added eight dedicated operation-level gas snapshots and a deterministic CSV
  exporter/checker.
- Initialized the canonical six-field schema-v4 research case and added the
  detailed Bangla MPP-to-publication execution contract.

## Workspace readiness — 2026-08-29

- Added a checked-in `uv.lock`, isolated Python 3.13 setup, and root `make`
  targets for setup, testing, reproduction, gas snapshots, and checksum checks.
- Added workspace ignore rules and a dedicated `WORKSPACE.md` entry point.
- Removed the unpinned `forge-std` test dependency by using a minimal local
  Foundry cheatcode interface.
- Replaced unsupported Solidity binary literals in the contract tests.
- Reproduced the complete Python baseline on macOS/Apple Silicon: 17 tests pass.
- Compiled the Solidity source with Solc 0.8.24, passed 2 current Foundry tests,
  and generated a baseline gas snapshot.

## v1.0 — 2026-08-29

- Froze the paper as a property/protocol/systems contribution rather than a primitive claim.
- Replaced per-record Shamir sharing with an epoch threshold-KEM architecture.
- Added canary partial-decryption readiness audits with DLEQ proofs.
- Added exact hypergeometric and repeated-audit probability functions.
- Added uniform and failure-domain-stratified sampling.
- Added threshold-KEM/DEM record sealing and opening with AES-GCM.
- Added audit/dispute evidence and selective-withholding counterexample tests.
- Added Monte Carlo scenarios, five generated figures, datasets, and cryptographic benchmarks.
- Added Solidity bulletin-board skeleton, formal-model documents, algorithms, TDD plan, paper blueprint, and diagrams.
- Hardened audit challenges to canonical beacon/epoch/slot-derived hash-to-group canaries whose discrete logarithm is not exposed.
- Added a deterministic/context-separation regression test and raised the Python suite to 17 tests.
- Added a Bangla master guide, seven-day MVP sprint, prototype README, and Foundry configuration.
