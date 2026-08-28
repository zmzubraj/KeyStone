# Changelog

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
