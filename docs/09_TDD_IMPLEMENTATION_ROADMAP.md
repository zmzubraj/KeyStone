# TDD Implementation Roadmap

## Development rule

Every behavior change begins with one failing test, the test is observed failing for the expected reason, the minimum implementation is added, and the full suite is rerun.

## Test inventory already implemented

| Test file | Behavior |
|---|---|
| `test_shamir.py` | threshold reconstruction and corrupted-share rejection |
| `test_dleq.py` | valid/context-bound proof and tamper rejection |
| `test_threshold_kem.py` | record opening with `t`, failure with `t-1`, invalid partial exclusion |
| `test_sampling.py` | exact bound, repetition, deterministic and stratified sampling |
| `test_protocol.py` | evidence, successful dispute, selective-withholding counterexample |
| `test_simulation.py` | reproducibility and correlation/diversity effect |

## Next TDD tasks

### Task 1 — Exact stratified distribution

- Add failing tests for a hand-enumerated two-domain case.
- Implement convolution of per-domain hypergeometric PMFs.
- Compare exact and Monte Carlo results within a stated tolerance.

### Task 2 — Confidence intervals

- Add failing tests for Wilson intervals at known counts.
- Add interval fields to simulation results.
- Include intervals in plots/tables.

### Task 3 — Churn and Markov readiness

- Add tests for deterministic state transitions: online → degraded → offline → recovered.
- Add a two-state/three-state Markov failure model.
- Compare repeated-audit inference with the static-set bound.

### Task 4 — Epoch refresh model

- Add tests ensuring refreshed shares reconstruct the same secret while old/new mixed shares are rejected by epoch context.
- Add a dealer-based zero-polynomial refresh for experimentation only.
- Bind proofs and requests to refresh generation.

### Task 5 — Public response serialization

- Add golden-vector tests for request/response encoding and transcript hashes.
- Implement canonical CBOR/SSZ or a fixed ABI-compatible encoding.
- Publish vectors in `paper/test_vectors.json`.

### Task 6 — Signatures

- Add tests for identity-bound response signatures, replay rejection, and wrong-chain context.
- Implement Ed25519 or secp256k1 adapter.
- Include signature bytes/verification time in benchmarks.

### Task 7 — Multi-process testbed

- Add integration test launching `n=5,t=3` local custodians.
- Inject delay and process failure.
- Verify audit/dispute outcomes match the in-memory protocol.

### Task 8 — Contract test suite

- Initialize Foundry.
- Write failing tests for epoch registration, request deadlines, response bitmap, duplicate response, and finalization.
- Compile, fuzz, and record gas.

### Task 9 — Authorized destination adapter

- Define an interface `ReleasePolicy.authorize(request, attestation) -> bool`.
- Add a mock-attestation test.
- Add one real TEE/HSM integration only after core distributed tests are stable.

## Verification commands

```bash
cd prototype
pytest
python -m keystone.cli demo
python -m keystone.cli bound --n 32 --threshold 22 --sample-size 8
./scripts/run_baseline.sh
```

## Commit granularity

Recommended commit sequence:

1. `test: specify exact stratified audit distribution`
2. `feat: add exact domain-stratified probability engine`
3. `test: specify Wilson confidence intervals`
4. `feat: report simulation confidence intervals`
5. `test: specify epoch refresh context separation`
6. `feat: add experimental zero-polynomial share refresh`
7. `test: add canonical response vectors`
8. `feat: serialize and sign audit responses`
9. `test: add multiprocess audit and dispute flow`
10. `feat: add local custodian service testbed`
