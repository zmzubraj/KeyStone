# Verification Record

**Artifact:** KEYSTONE MPP v1.0  
**Verification date:** 2026-08-29  
**Frozen research status:** GO for MPP implementation, conditional on the claim
boundary in `FREEZE.md`

## Latest workspace environment

- macOS 15.1, Darwin 24.1.0, arm64
- Apple M4 Pro, 12 logical CPUs
- uv 0.11.8
- uv-managed Python 3.13.13
- pytest 9.1.1
- cryptography 50.0.1
- matplotlib 3.11.1
- Foundry 1.5.1-stable
- Solc 0.8.24 through Foundry

These measurements are a local research baseline. They are not production
throughput, security, availability, or cost claims.

## Workspace commands executed

```bash
uv lock --python 3.13
uv sync --locked --extra dev --python 3.13
make reproduce
forge build --root contracts
forge test --root contracts -vv
forge snapshot --root contracts --snap .gas-snapshot
```

The root `Makefile` and `WORKSPACE.md` preserve the setup, fast-verification,
full-reproduction, and checksum paths. Generated environments and build outputs
are excluded by `.gitignore`; evidence datasets, figures, the uv lock, and the
gas snapshot remain workspace artifacts.

## Verified Python result

```text
17 passed in 0.14s
```

Verified behavior includes:

- canonical beacon/context-derived hash-to-group canary generation;
- rejection of non-canonical or context-mismatched audit challenges;
- Shamir/Feldman share validation;
- valid and tampered DLEQ audit proofs;
- threshold-DH KEM record sealing and opening;
- failure below threshold;
- exact and generalized sampling probability calculations;
- uniform and failure-domain-stratified sampling;
- IID, correlated-domain, and selective-withholding fault scenarios.

## End-to-end demo

```json
{
  "audit_passed": true,
  "audit_valid_responses": 5,
  "dispute_success": true,
  "plaintext": "encrypted AI inference receipt"
}
```

## Frozen analytical result

For `n=32`, `t=22`, `s=q=8`:

```text
P(false accept | worst static catastrophic state) = 0.01934628219389065
P(detect | worst static catastrophic state)       = 0.9806537178061093
```

This is a one-audit bound under a fixed ready set and uniform sampling without
replacement. It is not a proof of unconditional future availability.

## Frozen Monte Carlo scenarios

| Scenario | Trials | Reconstruction success | Audit pass | Catastrophic detection |
|---|---:|---:|---:|---:|
| IID 10%, uniform | 20,000 | 0.99975 | 0.42905 | 1.00000 in observed catastrophic trials |
| Domain outage 20%, uniform | 20,000 | 0.81360 | 0.37125 | 0.99758584 |
| Domain outage 20%, stratified | 20,000 | 0.81430 | 0.33895 | 1.00000 in this frozen run |
| 11 selective withholders | 20,000 | 0.00000 | 1.00000 | 0.00000 |

The selective-withholding scenario intentionally demonstrates that routine
canary audits do not guarantee cooperation on a targeted dispute.

## Latest local cryptographic microbenchmark

| `n` | `t` | Keygen median (ms) | Seal median (ms) | Partial proof median (ms) | Verify median (ms) | Open median (ms) |
|---:|---:|---:|---:|---:|---:|---:|
| 16 | 11 | 18.011 | 0.272 | 0.630 | 0.772 | 9.135 |
| 32 | 22 | 71.908 | 0.276 | 0.629 | 0.784 | 18.421 |
| 64 | 43 | 319.212 | 0.294 | 0.621 | 0.772 | 36.711 |

The implementation uses a compact generated safe-prime subgroup and is not a
benchmark for a standardized production threshold-cryptography library.

## Solidity result

```text
Compiler: Solc 0.8.24
Foundry tests: 2 passed; 0 failed; 0 skipped
```

Current test evidence covers:

- audit finalization with response and missing-response bitmaps;
- exclusion of an equivocating response from the valid-response count.

The checked-in `.gas-snapshot` records:

| Test | Gas |
|---|---:|
| `testAuditFinalizesWithMissingBitmap` | 246,178 |
| `testEquivocationExcludesResponse` | 240,867 |

This closes the previous compile/dependency blocker. It does **not** complete the
full Day-4 research gate: fuzz/invariant tests, invalid-response and boundary
coverage, and a complete operation-level gas table remain pending.

## Generated research outputs

- five publication-oriented figures in PNG and SVG;
- exact-bound, IID-failure, domain-diversity, selective-withholding, and
  sampling-strategy CSV files;
- deterministic experiment manifest and frozen seeds;
- baseline JSON and execution evidence;
- eight architecture/protocol/threat-model diagrams in editable and rendered
  formats;
- a checked-in uv dependency lock and baseline Foundry gas snapshot.

## Reproducibility verdict

- **Python cryptographic/simulation MPP:** freshly reproduced.
- **Figures and datasets:** freshly regenerated.
- **Python dependency environment:** locked and synchronized with uv.
- **Solidity source/current unit tests:** compiled and passed.
- **Artifact hashes:** must be refreshed after each reviewed evidence update and
  verified by `make checksums`.
- **Formal paper claims:** theorem/proposition roadmaps, not machine-checked
  proofs.
- **Distributed and contract hardening:** incomplete.
- **Production security:** explicitly not claimed.

## Historical evidence

The original packaged release was also verified on Linux x86_64 with Python
3.13.5 and reported 17 tests passing in 0.26 seconds. That run remains useful as
cross-platform evidence, but this document leads with the latest reproducible
workspace result.
