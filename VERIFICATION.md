# Verification Record

**Artifact:** KEYSTONE MPP v1.0  
**Verification date:** 2026-08-29  
**Canonical research status:** `INTAKE`; the historical engineering-only “GO
for MPP implementation” wording is superseded by
`research-case/program-state.json`. All results below remain preliminary or
preauthorization-only unless a stronger disposition is stated explicitly.

## Revision R1 (reviewer response), 2026-10-09 to 2026-10-10

Trigger: reviewer return `Jubyer.docx` (eight screenshots of an AI-chat answer
with values labelled "illustrative"). No placeholder value from it is used.
Authorization and choices: `research-case/03-design/r1-reviewer-revision/R1-AUTHORIZATION.md`.

Frozen design: `research-case/03-design/r1-reviewer-revision/r1-design-freeze.json`,
SHA-256 `4c852969b615ba0dc6f935cff83aa3f0f35743168695948cf6898e8ba1932385`,
written and hashed at 2026-10-09T13:05Z before any R1 run. Three logged
deviations in `r1-deviation-log.md` (post hoc s=12/16 extension of the
acceptance analysis; a discarded 3-trace smoke test; one D0 control trace that
timed out under host contention and is kept as a failure).

Executed (CPython 3.13.13, Apple M4 Pro, macOS 15.1):

| Family | Script | Output | Label |
|---|---|---|---|
| PC03 cells IID/STRAT/SW, 131,072 draws each | `prototype/scripts/run_r1_pc03.py` | `research-case/05-analysis/results/r1/pc03-summary.json`, `*-blocks.csv` | prespecified synthetic simulation; methods review not independent |
| Correlation, acceptance rule, scalability | `prototype/scripts/run_r1_analytic.py` | `analytic-*.csv` (MC cross-check max error 0.0085) | exact; acceptance rule post hoc |
| Crypto microbenchmarks (256-bit, ffdhe2048, ffdhe3072) | `prototype/scripts/run_r1_microbench.py` | `microbench-*.csv` | local, pure Python, upper bound |
| Emulated deadline testbed, 8 profiles x 300 traces | `prototype/scripts/run_r1_deadline_testbed.py` | `results/r1/deadline/D*.csv` | single-host emulation, real ffdhe2048 crypto |
| Tables, figures, prose macros | `prototype/scripts/build_r1_figures_tables.py` | `paper/r1/tables`, `paper/r1/figures`, `paper/r1/r1-asset-manifest.json` | generated only from the outputs above |

Headline results: strict s=q=8 audit passes 43.1% at 10% IID unavailability
while reconstruction succeeds 99.98%; stratification raises conditional
detection 99.89% to 100% (primary paired difference 0.00021); 11 selective
withholders pass 100% of audits and 0% of disputes; testbed disputes succeed
0% by the 2 s primary deadline and 100% by 5 s wherever reconstruction is
possible (medians 3.69-3.88 s), dominated by ~135 ms per pure-Python
ffdhe2048 proof verification; 11 crashes defeat all 300 disputes.

Checks run: `pytest tests/test_r1_revision.py` (17 passed); freeze hash
re-verified by every R1 script; manuscript `paper/r1/KEYSTONE_R1.tex` builds
with latexmk (12 pages, no undefined references or overfull boxes).

Gas re-run: `make snapshot` at 2026-10-09T19:50Z (Foundry 1.5.1, Solc 0.8.24),
8/8 gas tests passed, values identical to the 2026-08-29 snapshot; Table 8 is
rendered from `contracts/gas_report.csv` with each operation's harness scope.

Not done: independent novelty review, geo-distributed deployment,
optimized-library timing, external cryptographic or contract audit.

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
