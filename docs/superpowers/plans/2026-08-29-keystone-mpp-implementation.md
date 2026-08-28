# KEYSTONE MPP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use a task-by-task TDD workflow. Steps use checkbox syntax for tracking.

**Goal:** Build and validate a reproducible minimum publishable prototype for auditable dispute-key availability.

**Architecture:** Use an epoch threshold-DH KEM to wrap per-record AES keys, canary DLEQ partial-decryption audits for readiness, a separate authorized dispute path, exact/Monte Carlo probability analysis, and a Solidity bulletin-board boundary.

**Tech Stack:** Python 3.11+, cryptography/AESGCM, pytest, matplotlib, Solidity 0.8.24, Graphviz.

**Spec:** `docs/superpowers/specs/2026-08-29-keystone-mpp-design.md`

## Global Constraints

- Do not claim primitive-level novelty.
- Never use a production record ciphertext as a routine canary.
- Bind proofs to protocol version, request context, epoch, and member index.
- Distinguish audit readiness from target-dispute readiness.
- Label handwritten cryptography as research-only.

---

### Task 1: Shamir and share commitments

**Files:** `prototype/src/keystone/group.py`, `shamir.py`; tests `test_shamir.py`.

- [x] Write a failing threshold-reconstruction test.
- [x] Observe import/behavior failure.
- [x] Implement polynomial sharing and interpolation.
- [x] Write a failing corrupted-share test.
- [x] Implement Feldman commitments and verification.
- [x] Run full tests.

### Task 2: DLEQ proof

**Files:** `dleq.py`; tests `test_dleq.py`.

- [x] Specify valid proof and context replay rejection.
- [x] Implement Fiat–Shamir Chaum–Pedersen transcript.
- [x] Specify tampered partial rejection.
- [x] Run full tests.

### Task 3: Threshold KEM/DEM

**Files:** `threshold_kem.py`; tests `test_threshold_kem.py`.

- [x] Specify `t`-of-`n` record opening.
- [x] Implement dealer epoch, threshold DH, AES-GCM key wrap and record encryption.
- [x] Specify failure with `t-1` and invalid proof exclusion.
- [x] Run full tests.

### Task 4: Sampling and exact bound

**Files:** `sampling.py`; tests `test_sampling.py`.

- [x] Specify exact `n=32,t=22,s=8` bound.
- [x] Implement hypergeometric tail and repeated-audit helper.
- [x] Specify deterministic uniform and domain-stratified sampling.
- [x] Run full tests.

### Task 5: Audit/dispute protocol

**Files:** `protocol.py`; tests `test_protocol.py`.

- [x] Specify invalid/nonresponse evidence.
- [x] Implement canary audit.
- [x] Specify successful authorized dispute.
- [x] Implement threshold opening path.
- [x] Specify selective-withholding counterexample.
- [x] Run full tests.

### Task 6: Failure simulator

**Files:** `simulation.py`; tests `test_simulation.py`.

- [x] Specify deterministic metric output.
- [x] Implement independent and domain outages.
- [x] Specify diversity advantage.
- [x] Implement selective dispute withholding.
- [x] Run full tests.

### Task 7: CLI and experiment artifact

**Files:** `cli.py`, `scripts/run_experiments.py`, `scripts/benchmark_crypto.py`, configs/results.

- [x] Add demo, bound, and scenario commands.
- [x] Generate baseline JSON/CSV.
- [x] Generate five PNG/SVG figures.
- [x] Generate crypto benchmark table.
- [x] Run one-command baseline.

### Task 8: Contract boundary

**Files:** `contracts/src/KeystoneBulletinBoard.sol`, contract documentation.

- [x] Define epoch/member registration.
- [x] Define audit/dispute request and response commitment events.
- [x] Define deadline finalization and missing-response bitmap.
- [ ] Compile/fuzz/gas-test in Foundry.

### Task 9: Research documentation and diagrams

**Files:** `FREEZE.md`, `docs/`, `paper/`, `diagrams/`.

- [x] Freeze claims and exclusions.
- [x] Document model, protocol, roles, algorithms, theorems, evaluation, risks, and paper outline.
- [x] Render architecture/sequence/state/threat/experiment diagrams.
- [x] Create manifest and checksums.

### Task 10: Final verification

- [x] Run `pytest`.
- [x] Run end-to-end demo.
- [x] Run bound calculator.
- [x] Regenerate simulations, figures, and benchmarks.
- [ ] Obtain external cryptography and systems reviews before publication.
