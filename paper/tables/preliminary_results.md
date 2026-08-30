# Preliminary KEYSTONE Paper Tables

> Evidence label: internal preliminary simulation/contract evidence. These tables are
> not confirmatory or independently verified until the frozen study-design and
> research-case gates authorize their rerun.

## Monte Carlo outcomes

| Scenario | Trials | Reconstruction success (95% Wilson CI) | Audit pass (95% Wilson CI) | Catastrophic detection (95% Wilson CI; conditional n) |
|---|---:|---:|---:|---:|
| IID 10%, uniform | 20,000 | 0.99975 [0.99941, 0.99989] | 0.42905 [0.42220, 0.43592] | 1.00000 [0.56552, 1.00000]; n=5 |
| Domain outage 20%, uniform | 20,000 | 0.81360 [0.80814, 0.81894] | 0.37125 [0.36458, 0.37797] | 0.99759 [0.99542, 0.99873]; n=3,728 |
| Domain outage 20%, stratified | 20,000 | 0.81430 [0.80885, 0.81963] | 0.33895 [0.33242, 0.34554] | 1.00000 [0.99897, 1.00000]; n=3,714 |
| 11 selective withholders | 20,000 | 0.00000 [0.00000, 0.00019] | 1.00000 [0.99981, 1.00000] | 0.00000 [0.00000, 0.00019]; n=20,000 |

## Exact fixed-quota stratified validation

| Design | Required valid | Exact tail | Monte Carlo tail | Absolute error | Trials | Seed |
|---|---:|---:|---:|---:|---:|---:|
| fixed-quota domain-stratified sampling | 6 | 0.353043003 | 0.353470000 | 0.000426997 | 100,000 | 20260829 |

The fixed-quota exact calculation is not interchangeable with the
minimum-domain-coverage plus uniform-remainder sampler.

## Exploratory temporal-dependence boundary

| Audits | Final catastrophic trials | All audits pass + final catastrophic | Conditional sequence rate (95% Wilson CI) | Static-set repeated bound |
|---:|---:|---:|---:|---:|
| 1 | 1,278 | 478 | 0.37402 [0.34791, 0.40089] | 0.424242 |
| 2 | 5,828 | 1,296 | 0.22237 [0.21188, 0.23323] | 0.179982 |
| 4 | 10,749 | 448 | 0.04168 [0.03806, 0.04562] | 0.032393 |
| 8 | 11,850 | 4 | 0.00034 [0.00013, 0.00087] | 0.001049 |

The evolving-state sequence rate and static-ready-set bound have different
estimands and must not be substituted for one another.

## Local cryptographic and signature microbenchmark

| n | t | Keygen median (ms) | Seal median (ms) | Partial proof median (ms) | Partial verify median (ms) | Open median (ms) | Ed25519 sign median (ms) | Ed25519 verify median (ms) | Signature bytes |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 16 | 11 | 16.898 | 0.255 | 0.596 | 0.738 | 8.566 | 0.162 | 0.154 | 64 |
| 32 | 22 | 67.654 | 0.257 | 0.590 | 0.738 | 17.382 | 0.157 | 0.149 | 64 |
| 64 | 43 | 310.844 | 0.279 | 0.597 | 0.724 | 34.714 | 0.157 | 0.149 | 64 |

These are local single-process research timings, not production throughput claims.

## Solidity operation gas

| Operation | Gas | Scope |
|---|---:|---|
| `register_epoch` | 223,629 | Foundry test-body gas; setup excluded; small harness overhead may remain |
| `open_audit` | 125,107 | Foundry test-body gas; setup excluded; small harness overhead may remain |
| `submit_audit_response` | 57,882 | Foundry test-body gas; setup excluded; small harness overhead may remain |
| `mark_invalid_response` | 27,704 | Foundry test-body gas; setup excluded; small harness overhead may remain |
| `record_equivocation` | 51,710 | Foundry test-body gas; setup excluded; small harness overhead may remain |
| `finalize_audit` | 29,142 | Foundry test-body gas; setup excluded; small harness overhead may remain |
| `open_dispute` | 144,149 | Foundry test-body gas; setup excluded; small harness overhead may remain |
| `cancel_request` | 5,709 | Foundry test-body gas; setup excluded; small harness overhead may remain |

Canonical sources: `prototype/results/baseline.json`,
`prototype/results/exact_stratified_validation.csv`,
`prototype/results/markov_temporal_dependence.csv`, and
`prototype/results/crypto_benchmark.csv`, and
`contracts/gas_report.csv`.
