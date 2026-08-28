# Experiment and Evaluation Plan

## Research questions

- **RQ1:** Does the measured catastrophic false-pass rate match the analytical hypergeometric bound?
- **RQ2:** How do `n,t,s,q` trade audit bandwidth, false alarms, and catastrophic-state detection?
- **RQ3:** How much do correlated provider/region outages reduce dispute reconstructability relative to independent-failure models?
- **RQ4:** Does domain-stratified sampling improve catastrophic-state detection under correlated failures?
- **RQ5:** What are the cryptographic and end-to-end latency/byte costs of canary audits and authorized reconstruction?
- **RQ6:** How badly can selective withholding decouple audit success from target-dispute success?
- **RQ7:** How quickly do recovery/replacement/refresh policies restore the DKA target after churn?

## Baselines

1. **No readiness audit:** rely only on initial VSS/DKG.
2. **Unsigned heartbeat:** custodian says “online” without share operation.
3. **Uniform canary sampling:** KEYSTONE analytical baseline.
4. **Domain-stratified canary sampling:** KEYSTONE correlation-aware variant.
5. **Full-committee canary:** maximum detection, maximum bandwidth.
6. **Escalating audit:** small sample, then larger/full audit after failure.

## Frozen parameter grid

| Parameter | Values |
|---|---|
| `n` | 16, 32, 64, 128 |
| `t/n` | 0.50, 0.67, 0.75, 0.80 |
| `s` | 4, 8, 12, 16, 24 |
| `q` | `s`, `s-1`, `ceil(0.75s)` |
| independent offline probability | 0.00–0.40 |
| domain outage probability | 0.00–0.30 |
| domains | 2, 4, 8, 16 |
| Byzantine invalid-response fraction | 0.00–0.33 |
| selective withholders | 0 through `n-t+1` and beyond |
| trials | at least 10,000 per stochastic point; increase near rare-event boundaries |

## Metrics

### Security/reliability

- dispute reconstruction success rate;
- catastrophic state rate;
- catastrophic false-pass rate conditioned on catastrophic state;
- catastrophic detection rate;
- unauthorized/invalid response acceptance rate;
- selective-withholding audit/dispute gap;
- time to recovery after replacement/refresh.

### Performance

- key setup latency;
- partial-decryption proof generation/verification latency;
- audit bytes per response and total per epoch;
- threshold combination/open latency;
- ledger transactions and gas;
- coordinator CPU/memory;
- deadline success versus injected latency distribution.

### Operational

- false health alarms while `≥t` nodes remain ready;
- sample-domain coverage;
- number of nodes replaced/slashed;
- cost per avoided unreconstructable dispute.

## Experiments

### E1 — Closed-form validation

For each small `(n,t,s,q)`, enumerate all ready sets and compare the exact acceptance probability with the implementation. For larger values, compare Monte Carlo confidence intervals with the formula.

### E2 — Independent outages

Sweep node offline probability. Plot reconstruction success and audit pass. Show that an all-response audit is a health signal and may fail before catastrophic loss, creating conservative warnings.

### E3 — Correlated outages and placement

Compare committees concentrated in 2 domains versus diversified across 4/8/16 domains at equal marginal domain outage probability. Enforce and violate the `n_d≤n-t` placement cap.

### E4 — Uniform versus stratified sampling

Condition on catastrophic domain-failure states and compare detection. Report both detection and benign audit pass because stratification may be more sensitive to one-domain degradation.

### E5 — Invalid/equivocating custodians

Inject malformed partials, wrong contexts, duplicate identities, stale epoch responses, and conflicting commitments. Measure deterministic rejection and evidence creation.

### E6 — Selective withholding

Keep audit readiness at 100% while `w` custodians refuse a target dispute. The expected phase transition occurs at `w=n-t+1`. This experiment establishes a limitation, not a success claim.

### E7 — Cryptographic overhead

Benchmark `n/t` settings on at least three machines. Report median, p95, and standard deviation after warm-up. The included single-machine baseline is a starting point.

### E8 — Distributed deadline experiment

Deploy 32 processes across four network namespaces/regions. Inject latency, packet loss, and process crash. Measure probability of receiving `t` verified responses before `Δ_d`.

### E9 — Contract overhead

Measure epoch registration, audit opening, response commitment, dispute opening, and finalization gas. DLEQ verification remains off-chain in the MPP unless a precompile/zk-verifier design is separately justified.

## Required paper figures

1. Analytical detection bound versus sample size.
2. Reconstruction/audit rates under independent outages.
3. Reconstruction versus number of failure domains.
4. Selective-withholding gap.
5. Uniform versus stratified detection.
6. Latency CDF for partial proof and threshold open.
7. Deadline success heatmap over latency and threshold.
8. Recovery timeline after correlated outage.

Figures 1–5 are generated in `prototype/results/figures`.

## Required tables

- Property comparison with DA/VSS/PSS/threshold KMS.
- Claim-to-assumption matrix.
- Crypto benchmark table.
- Network/ledger overhead table.
- Attack and evidence table.
- Parameter recommendations by risk tier.

## Statistical reporting

- Freeze random seeds in the artifact.
- Report conditional false-pass rates with the number of catastrophic trials.
- Use Wilson or Clopper–Pearson intervals for rare Bernoulli events.
- Do not report zero observed failures as zero true probability; state the upper confidence bound.
- Separate analytical assumptions from simulator assumptions.
