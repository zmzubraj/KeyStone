# Verification Record

**Artifact:** KEYSTONE MPP v1.0  
**Verification date:** 2026-08-29  
**Canonical research status:** `INTAKE`; the historical engineering-only “GO
for MPP implementation” wording is superseded by
`research-case/program-state.json`. All results below remain preliminary or
preauthorization-only unless a stronger disposition is stated explicitly.

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
make snapshot
make snapshot-check
```

The root `Makefile` and `WORKSPACE.md` preserve the setup, fast-verification,
full-reproduction, and checksum paths. Generated environments and build outputs
are excluded by `.gitignore`; evidence datasets, figures, the uv lock, and the
gas snapshot remain workspace artifacts.

## Verified Python result

```text
57 passed; 0 failed
```

This is a same-workspace local test result, not independent scientific
verification. The crypto receipt separately maps 22 claim-relevant pytest
nodes plus two deterministic vector-freshness checks; the remaining tests cover
supporting code, receipt safety, manifest drift, and table lineage.

Verified behavior includes:

- canonical beacon/context-derived hash-to-group canary generation;
- rejection of non-canonical or context-mismatched audit challenges;
- Shamir/Feldman share validation;
- valid and tampered DLEQ audit proofs;
- threshold-DH KEM record sealing and opening;
- failure below threshold;
- exact and generalized sampling probability calculations;
- exact fixed-quota stratified probability by convolution of per-domain
  hypergeometric PMFs, checked against hand enumeration and seeded Monte Carlo;
- uniform and failure-domain-stratified sampling;
- IID, correlated-domain, and selective-withholding fault scenarios;
- raw binomial counts and two-sided 95% Wilson score intervals for Monte Carlo
  proportions, with conditional intervals left undefined when no catastrophic
  trial was observed;
- version-1 canonical audit-request and partial-response binary transcripts,
  strict decoding, context-sensitive hashes, and deterministic golden vectors.
- Ed25519 signatures over the exact canonical partial-response bytes, including
  wrong-key, tamper, and cross-chain/contract replay rejection plus deterministic
  test-only signature vectors.
- experimental dealer-based zero-polynomial share refresh preserving the public
  key and authorized opening, with generation-bound canary/proof contexts and
  rejection of stale old/new partial mixing.

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

| Scenario | Trials | Reconstruction success (95% Wilson CI) | Audit pass (95% Wilson CI) | Catastrophic detection (95% Wilson CI) |
|---|---:|---:|---:|---:|
| IID 10%, uniform | 20,000 | 0.99975 [0.99941, 0.99989] | 0.42905 [0.42220, 0.43592] | 1.00000 [0.56552, 1.00000], 5 catastrophic trials |
| Domain outage 20%, uniform | 20,000 | 0.81360 [0.80814, 0.81894] | 0.37125 [0.36458, 0.37797] | 0.99759 [0.99542, 0.99873], 3,728 catastrophic trials |
| Domain outage 20%, stratified | 20,000 | 0.81430 [0.80885, 0.81963] | 0.33895 [0.33242, 0.34554] | 1.00000 [0.99897, 1.00000], 3,714 catastrophic trials |
| 11 selective withholders | 20,000 | 0.00000 [0.00000, 0.00019] | 1.00000 [0.99981, 1.00000] | 0.00000 [0.00000, 0.00019], 20,000 catastrophic trials |

The selective-withholding scenario intentionally demonstrates that routine
canary audits do not guarantee cooperation on a targeted dispute.

## Exact stratified validation

For four independent strata with `(population=8, ready=5, draws=2)` and an
acceptance threshold of six valid responses out of eight total draws:

| Method | Tail probability |
|---|---:|
| Exact convolution | 0.35304300291545193 |
| Seeded Monte Carlo, 100,000 trials | 0.35347 |
| Absolute error | 0.0004269970845480753 |

This validates the exact fixed-quota calculation. It is not interchangeable
with the prototype's minimum-one-per-domain plus uniform-remainder sampler;
each design must retain its own sampling semantics in the paper.

## Exploratory temporal-dependence boundary

The two-state Markov pilot starts every sequence online, uses
`P(online→offline)=0.22`, `P(offline→online)=0.08`, `n=12`, `t=8`, `s=4`, and
`q=3`, and reports 12,000 deterministic-seed trials per row. The measured event
is “all audits pass and the final state is catastrophic,” conditioned on the
final state being catastrophic.

| Audits | Final catastrophic trials | Conditional sequence rate (95% Wilson CI) | Static-set repeated bound |
|---:|---:|---:|---:|
| 1 | 1,278 | 0.37402 [0.34791, 0.40089] | 0.424242 |
| 2 | 5,828 | 0.22237 [0.21188, 0.23323] | 0.179982 |
| 4 | 10,749 | 0.04168 [0.03806, 0.04562] | 0.032393 |
| 8 | 11,850 | 0.00034 [0.00013, 0.00087] | 0.001049 |

These columns have different estimands. Their separation demonstrates why the
static ready-set exponentiation cannot be reused as a time-evolving availability
claim. This pilot is exploratory and must be redesigned/frozen before it can be
confirmatory evidence.

## Latest local cryptographic microbenchmark

| `n` | `t` | Keygen median (ms) | Seal median (ms) | Partial proof median (ms) | Verify median (ms) | Open median (ms) | Ed25519 sign median (ms) | Ed25519 verify median (ms) | Signature bytes |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 16 | 11 | 16.898 | 0.255 | 0.596 | 0.738 | 8.566 | 0.162 | 0.154 | 64 |
| 32 | 22 | 67.654 | 0.257 | 0.590 | 0.738 | 17.382 | 0.157 | 0.149 | 64 |
| 64 | 43 | 310.844 | 0.279 | 0.597 | 0.724 | 34.714 | 0.157 | 0.149 | 64 |

The implementation uses a compact generated safe-prime subgroup and is not a
benchmark for a standardized production threshold-cryptography library.

## Solidity result

```text
Compiler: Solc 0.8.24
Foundry cases: 27 passed; 0 failed
```

Current deterministic and fuzz evidence covers:

- audit finalization with response and missing-response bitmaps;
- exclusion of an equivocating response from the valid-response count;
- rejection of duplicate custodian identities and zero epoch commitments;
- rejection of zero audit/dispute subject bindings and zero invalid-evidence hashes;
- fuzzed duplicate-member, sample-threshold, and unauthorized-caller boundaries
  with 512 runs per fuzz property;
- two stateful invariants covering non-zero administration and consistency of
  response, invalid, equivocation, missing, valid-count, and pass/fail state
  across 64 runs × 32 handler calls;
- positive audit finalization and full dispute-threshold lifecycles;
- deadline equality and deadline-plus-one boundaries;
- zero, duplicate-open, and terminal request-ID nonreuse; and
- cancellation closure and finalization-state rejection.

The checked-in `.gas-snapshot` and generated `contracts/gas_report.csv` record:

| Operation | Gas |
|---|---:|
| Register epoch (`n=5,t=3`) | 223,628 |
| Open three-member audit | 125,107 |
| Submit audit response | 57,882 |
| Mark invalid response | 27,704 |
| Record equivocation | 51,710 |
| Finalize audit | 29,120 |
| Open dispute | 144,171 |
| Cancel request | 5,642 |

Setup work is excluded from the dedicated test bodies, although small harness
overhead may remain. This closes the internal fuzz/invariant and operation-table
gap. It does **not** establish production security or an independent audit, and
the measurements remain preliminary until rerun under the frozen confirmatory
study design.

## Generated research outputs

- five publication-oriented figures in PNG and SVG, with Wilson uncertainty
  bands on the applicable Monte Carlo proportions;
- exact-bound, IID-failure, domain-diversity, selective-withholding, and
  sampling-strategy CSV files plus exact stratified and temporal-dependence
  validation tables;
- a hash-bound preauthorization experiment manifest that records the current
  generator/source/lock hashes, seven parameter-and-seed declarations, seven
  CSV datasets, ten figure files, row counts, runtime metadata, dirty-state
  disclosure, and exclusions without claiming that the outputs were regenerated
  in this verification turn;
- generated preliminary Markdown and LaTeX paper tables whose current five
  inputs, exporter, selected rows/fields, section mapping, and outputs are bound
  by a fail-closed same-workspace lineage receipt;
- `paper/test_vectors.json` with reproducible request/response encodings and
  transcript hashes, also freshness-checked by `make verify`;
- `paper/signature_test_vectors.json` with a clearly labeled test-only seed,
  public key, canonical response bytes, and Ed25519 signature, also freshness-checked;
- baseline JSON and execution evidence;
- eight architecture/protocol/threat-model diagrams with canonical editable
  Mermaid sources; D2 has deterministic local SVG/PNG derivatives, a hash-bound
  same-workspace render receipt, and manual layout/clipping/relationship QA;
  grayscale/CVD review and independent scientific validation remain pending;
- a checked-in uv dependency lock and baseline Foundry gas snapshot.

## Reproducibility verdict

- **Python cryptographic/simulation MPP:** 57 local tests pass; the mapped
  claim-relevant subset is bound by a same-workspace preauthorization receipt.
- **Figures and datasets:** current bytes, row counts, parameters, seeds, and
  source/lock inputs are mechanically bound by the preauthorization experiment
  manifest; they were not regenerated in this verification turn.
- **Python dependency environment:** locked and synchronized with uv.
- **Solidity source/unit/fuzz/gas/invariant tests:** 27 mapped cases compiled and
  passed in a same-workspace receipt; this is not a security audit.
- **Preliminary tables:** source-to-output lineage and freshness checks pass;
  they are not canonical T-series results.
- **Artifact hashes:** the package manifest/checksum set is regenerated after
  reviewed edits settle and must pass with zero failures at each delivery
  checkpoint.
- **Formal paper claims:** theorem/proposition roadmaps, not machine-checked
  proofs.
- **Distributed testbed and independent contract audit:** incomplete.
- **Production security:** explicitly not claimed.

## Historical evidence

The original packaged release was also verified on Linux x86_64 with Python
3.13.5 and reported 17 tests passing in 0.26 seconds. That run remains useful as
cross-platform evidence, but this document leads with the latest reproducible
workspace result.
