---
title: "KEYSTONE: Response to the Reviewer (Revision R1)"
author: "Zubaer Mahmood Zubraj"
date: "10 October 2026"
geometry: margin=1in
fontsize: 11pt
---

Dear Reviewer,

Thank you for the review and for the suggested five-table, five-figure package. We have rebuilt every table and figure from executed experiments. This letter lists what changed, where each requested item now appears in the revised manuscript (`KEYSTONE_R1.pdf`), and where the measured results differ from the illustrative values in the suggestion.

# 1. How the new evidence was produced

Before running anything, we wrote the experimental design (parameters, endpoints, precision targets, seeds and testbed profiles) to a file and recorded its SHA-256 hash. Every script checks that hash before it runs, and every output records it. Three deviations are logged openly (a post hoc extension of one analysis, a discarded three-trace smoke test, and one testbed trace that timed out under host contention and is kept as a failure). Four kinds of evidence are used and each result is labelled with its kind:

* **Exact** closed-form values under a declared model.
* **Prespecified simulation**: three cells of 131,072 draws each (32 seed blocks of 4,096), above the Hoeffding requirement of 73,778 draws.
* **Microbenchmarks** of the prototype's cryptography at standard RFC 7919 group sizes (ffdhe2048 and ffdhe3072), not only the 256-bit research group.
* **Emulation**: 32 custodian processes on one host, each holding only its own ffdhe2048 share, under eight frozen latency, loss and crash profiles, 300 traces each (2,400 traces).

The paper states that the testbed is a single-host emulation rather than a geo-distributed deployment.

# 2. Placeholder values were not used

The suggestion marked several values as illustrative. None of them were copied. Where we now have measurements, they differ materially, and the differences change the paper's conclusions:

| Suggested (illustrative) | Measured in R1 |
|---|---|
| 10% IID failure: audit pass 96.8%, dispute success 95.1% | Audit pass 43.1% [42.8, 43.3]; reconstruction 99.98% (131,072 draws). The strict audit is a sensitive alarm, not an accurate health score. |
| 20% IID failure: audit pass 87.4%, dispute 82.7% | Exact: audit pass 16.8%, reconstructability 95.9% |
| Mean recovery 0.42 s to 1.14 s | Dispute completion 3.69 s to 3.88 s (medians across profiles); 0% within 2 s, 100% within 5 s wherever reconstruction is possible. Proof verification in the pure-Python prototype (about 135 ms per proof at ffdhe2048), not network delay, dominates. |
| Audit latency 75 to 251 ms; verification 18 to 71 ms | Measured single-audit time 1.24 s to 1.43 s at the median; verifying 22 partials and combining 3,213 ms (ffdhe2048) and 10,201 ms (ffdhe3072). |
| Bandwidth 8 to 32 KB | Measured canonical transcript bytes: 4,819 B (n=16, s=4) to 18,607 B (n=128, s=16) per audit at ffdhe2048. |

The baseline detection value of about 98.07% in the suggestion is correct; the exact value is 0.9806537.

# 3. Item-by-item mapping

| Requested item | Where it is now | Source and evidence type |
|---|---|---|
| Table 1, security properties | Table 1, with an added DKA row and an "assessed by" column | Design; links to the experiment that assesses each property |
| Table 2, experimental configuration | Table 3 | Frozen design file; lists every family actually run |
| Table 3, comparison with readiness baselines | Table 4, including a "decrypt a real record" baseline | Detection exact; costs measured (KEYSTONE 2,125 ms CPU and 9,415 B per audit versus 8,501 ms and 36,991 B for a full-committee probe at n=32, ffdhe2048) |
| Table 4, robustness under failure | Table 5: (a) prespecified simulation, (b) emulated testbed with dispute success by 2 s and by 5 s and completion times | Simulation and emulation |
| Table 5, performance and scalability | Table 6 (scaling to n=128) and Table 7 (per-operation costs for three groups) | Exact detection plus measured costs |
| Figure 1, architecture | Figure 1, redrawn as a vector figure with three separated paths | Design |
| Figure 2, detection versus sample size | Figure 2, two panels (thresholds at n=32; committee sizes 16 to 128) | Exact |
| Figure 3, dispute success versus deadline | Figure 3, two panels, 2,400 emulated traces | Emulation |
| Figure 4, IID versus correlated failure | Figure 4, IID and 2, 4 and 8 failure domains | Exact under a declared synthetic domain model; Monte Carlo agreement within 0.009 |
| Figure 5, audit versus dispute success | Figure 5, exact curves plus the 131,072-draw simulation point at w=11 | Exact and simulation |

# 4. Additional results the revision adds

* **Acceptance-rule trade-off** (Table 2, Figure 6). At s=8 no acceptance threshold gives both high detection and few benign alarms: q=8 detects 98.1% of worst-case catastrophic states but passes a healthy committee only 43.0% of the time at 10% unavailability; q=7 gives 85.9% and 81.3%. A larger sample helps: s=16, q=14 gives 98.8% detection with 95.7% benign pass at 5% unavailability and 78.9% at 10%. This analysis was added after seeing the exploratory results and is labelled post hoc.
* **Stratified sampling** (Table 5a). Fixed-quota stratification raised conditional detection of catastrophic draws from 99.89% to 100% and lowered the benign pass rate from 37.3% to 34.9%; the prespecified paired difference was 0.00021, so the benefit is real but small.
* **Placement matters more than sampling** (Figure 4). At 10% unit unavailability, reconstructability is 99.98% under IID failure, 94.8% with four domains of eight, and 81.0% with two domains of sixteen (which violates the placement cap n-t=10).
* **Model validation on real cryptography.** In the testbed the audit pass rate matched the exact hypergeometric expectation: 2.3% observed versus 3.0% expected with ten crashes, 5.7% versus 7.0% with one domain down, and 71.7% versus 72.4% with 2% message loss.
* **Selective withholding.** With eleven withholders, audits passed in 100% of 131,072 draws and disputes succeeded in 0% (upper 95% bound 0.0029%); in the testbed, eleven crashes defeated all 300 disputes.
* **On-chain cost** (Table 8): bulletin-board gas re-measured for this revision (Foundry 1.5.1, Solidity 0.8.24), with the harness committee for each operation.

# 5. Limitations that remain

The revised Limitations section states these explicitly: novelty has not been independently reviewed; the audit cannot detect selective withholding; the deadline results come from a single-host emulation of a pure-Python implementation and would differ for optimized code or a geo-distributed deployment; the prototype uses a dealer instead of DKG/PVSS and has not been externally audited; and failure models are synthetic.

# 6. Reproducibility

The frozen design, deviation log, raw per-block and per-trace outputs, the scripts that produced them and the script that generates every table, figure and in-text number are publicly available at https://github.com/zmzubraj/KeyStone under the MIT License. A single command regenerates the tables and figures from the stored outputs, and a manifest binds each asset to the SHA-256 of its inputs.

We would be grateful for your assessment of whether the revised evidence answers your request, and for any concerns about the methods described above.

Sincerely,

Zubaer Mahmood Zubraj
