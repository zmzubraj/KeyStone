# ২১ দিনের Aggressive MPP-to-Paper Execution Plan

## Assumption

একজন experienced blockchain/crypto engineer full-time কাজ করবে। Current ZIP-এর code core starting point। এই timeline ambitious; external review বা DKG integration delay হলে ১–২ সপ্তাহ buffer যুক্ত হবে।

## Week 1 — Formal core এবং artifact stabilization

### Day 1

- `FREEZE.md` review;
- research question ও contribution paragraph paper repo-তে copy;
- direct prior-art search log শুরু;
- definitions CA/VSR/AKR/AD/DDL/PAC/DKA edit।

**Deliverable:** Model v1.

### Day 2

- Theorem T1/T2/T3 এবং Proposition P1/P2 formal proof draft;
- temporal assumptions আলাদা subsection;
- selective-withholding counterexample formal execution।

**Deliverable:** Proof skeleton v1.

### Day 3

- exact stratified probability/convolution TDD;
- exhaustive small-parameter validation;
- confidence interval implementation।

**Deliverable:** Analytical engine v2.

### Day 4

- response serialization এবং transcript domain separation;
- signature/replay tests;
- test vectors।

**Deliverable:** Protocol wire format v1.

### Day 5

- Solidity Foundry project;
- epoch/audit/dispute deadline tests;
- response bitmap/equivocation events;
- initial gas table।

**Deliverable:** Compiled contract artifact.

### Day 6

- 32 custodian local multi-process harness;
- delay/offline injection;
- audit/dispute integration tests।

**Deliverable:** Distributed local demo.

### Day 7

- run all tests;
- fix spec/code mismatches;
- tag `mpp-alpha`।

**Deliverable:** stable alpha release.

## Week 2 — Experiments

### Day 8

- full `n,t,s,q` grid;
- analytical versus Monte Carlo validation;
- Figure 1 final।

### Day 9

- independent failure/churn sweeps;
- audit false-alarm analysis;
- Figure 2 এবং table।

### Day 10

- provider/region outage models;
- placement cap experiments;
- Figure 3।

### Day 11

- uniform/stratified/escalating sampling comparison;
- Figure 5 এবং overhead table।

### Day 12

- invalid proof, equivocation, stale epoch, replay attacks;
- evidence matrix।

### Day 13

- selective withholding sweep;
- Figure 4;
- stronger extension feasibility note।

### Day 14

- crypto/network/contract benchmark rerun;
- hardware metadata;
- statistical intervals;
- artifact freeze `mpp-beta`।

## Week 3 — Paper

### Day 15

- Introduction এবং contribution list;
- motivating failure scenario;
- limitations paragraph।

### Day 16

- Background/related work;
- prior-art comparison table;
- claim wording audit।

### Day 17

- Model/definitions section;
- property diagram;
- theorem statements।

### Day 18

- Protocol section;
- audit/dispute sequence diagrams;
- algorithm pseudocode।

### Day 19

- Analysis ও evaluation section;
- figures/tables/captions;
- parameter recommendations।

### Day 20

- Discussion, limitations, conclusion;
- reproducibility appendix;
- artifact README।

### Day 21

- adversarial reviewer pass;
- cryptography reviewer pass;
- consistency check;
- arXiv-ready PDF/source and artifact release।

## Solo priority order when time slips

1. definitions and theorem correctness;
2. exact/Monte Carlo validation;
3. selective-withholding limitation;
4. reproducible code/figures;
5. distributed benchmark;
6. contract gas;
7. TEE adapter।

TEE adapter first paper-এর critical path নয়।
