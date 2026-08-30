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

## Completed TDD tasks

### Task 1 — Exact stratified distribution — complete

- A hand-enumerated two-domain RED test was observed failing before implementation.
- Per-domain hypergeometric PMFs are convolved for fixed draw quotas.
- Exact and seeded Monte Carlo tails are checked within a 0.01 absolute tolerance;
  the frozen 100,000-trial evidence row differs by 0.000427.

### Task 2 — Confidence intervals — complete

- Known-count Wilson interval RED tests were observed failing before implementation.
- Simulation results now expose raw event counts, denominators, point estimates,
  and two-sided 95% Wilson score intervals.
- Regenerated CSVs and applicable plots include interval fields/bands. Conditional
  catastrophic detection intervals remain undefined when no catastrophic trial
  was observed.

## Next TDD tasks

### Task 3 — Churn and Markov readiness — complete

- Deterministic online → degraded → offline transitions and the offline →
  degraded recovery event are covered by tests.
- Validated two-state and three-state transition-matrix constructors are implemented.
- A reproducible repeated-audit sequence simulator reports the conditional event
  “all audits pass and the final state is catastrophic,” its Wilson interval,
  and the non-equivalent static-ready-set repeated bound side by side.
- `markov_temporal_dependence.csv` is explicitly exploratory because the grid
  was selected during implementation and is not the frozen confirmatory design.

### Task 4 — Epoch refresh model — experimental MPP gate complete

- Three RED/GREEN tests verify that zero-polynomial refresh preserves the epoch
  public key and authorized opening, rejects old/new partial mixing, and changes
  generation-bound canaries/proof contexts.
- `refresh_epoch_shares` is explicitly dealer-based experimental scaffolding.
- Production proactive refresh still requires authenticated DPSS/DKG and is not
  claimed by this artifact.

### Task 5 — Public response serialization — complete

- RED tests fixed the byte layout independently before implementation.
- Versioned, big-endian, length-delimited audit-request and partial-response
  transcripts bind chain, contract, epoch, request, member, deadline, and proof fields.
- Strict decoders reject wrong kinds, trailing bytes, malformed lengths, and
  noncanonical unsigned integers.
- `paper/test_vectors.json` is generated deterministically and freshness-checked.

### Task 6 — Signatures — internal MPP gate complete

- Six RED/GREEN tests cover deterministic Ed25519 identity binding, tampering,
  wrong-key rejection, cross-chain/contract replay, and exact key/signature lengths.
- The adapter signs the canonical partial-response bytes without a second encoding.
- `paper/signature_test_vectors.json` is deterministic and freshness-checked.
- The local benchmark records 64-byte signatures plus median signing and
  verification latency; production key management remains explicitly out of scope.

### Task 7 — Multi-process testbed

- Add integration test launching `n=5,t=3` local custodians.
- Inject delay and process failure.
- Verify audit/dispute outcomes match the in-memory protocol.

### Task 8 — Contract test suite — internal MPP gate complete

- Foundry is initialized without an external test dependency.
- Boundary, lifecycle, fuzz, gas, and stateful-invariant tests are implemented.
- The current internal suite contains 19 passing tests, including three
  512-run fuzz properties and two invariants at 64 runs × 32 calls.
- Eight operation-level gas measurements are exported to
  `contracts/gas_report.csv`.
- Remaining production gate: independent audit and a larger, separately owned
  fuzz/invariant campaign.

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
