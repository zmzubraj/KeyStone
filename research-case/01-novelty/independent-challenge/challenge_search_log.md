# DRAFT_INDEPENDENT_CHALLENGE

Date accessed: 2026-08-29
Owner scope: independent novelty challenge only

## Objective

Attempt to defeat `C001` by finding prior work that already covers one or more of:

- deadline-bounded authorized reconstructability
- separation of ciphertext/data availability from decryption-service readiness
- non-production or non-revealing partial-decryption exercises before authorized release
- context-bound share proofs / DLEQ-style correctness
- public deadline accountability or slashing for committee non-response
- correlated-failure or stratified audit treatment

## Canonical claim challenged

Source: `research-case/00-governance/intake-original.md`

Claim under challenge: "We formalize dispute-key availability as deadline-bounded, authorized reconstructability distinct from ciphertext data availability, and instantiate it with non-revealing canary partial-decryption sampling, explicit false-accept bounds, correlation-aware committee audits, and public deadline evidence."

## Search tracks

### Track A: threshold decryption in encrypted mempools / rollups

Queries used:

- `threshold decryption service availability proof DLEQ canary partial decryption threshold cryptography paper`
- `"encrypted mempool" threshold decryption slashing paper`
- `"Ferveo" threshold decryption DLEQ paper`
- `site:usenix.org threshold decryption encrypted mempool partial decryptions verified shares`

High-signal hits:

- Ferveo: Threshold Decryption for Mempool Privacy in BFT networks
- BEAT-MEV: Epochless Approach to Batched Threshold Encryption for MEV Prevention
- Shutter research notes on encrypted mempools

Assessment:

- Strong evidence that encrypted-transaction systems already treat "timely decryption after finalization" as a core liveness property.
- Did not find a paper in this track that already performs a pre-authorization canary exercise of live decryption shares without revealing production plaintext.

### Track B: accountability / traceability / context-binding in threshold decryption

Queries used:

- `accountable threshold decryption paper verifiable partial decryption availability`
- `traceable threshold decryption paper accountability partial decryptions`
- `"decryption context" threshold decryption paper`

High-signal hits:

- Accountability for Misbehavior in Threshold Decryption via Threshold Traitor Tracing
- Context-Dependent Threshold Decryption and its Applications

Assessment:

- Strong evidence that accountability and context isolation are already active prior-art surfaces.
- These results materially weaken any novelty claim based only on "context-bound decryption shares" or "accountable threshold decryption" in isolation.

### Track C: deadline- or time-conditioned threshold release

Queries used:

- `"threshold information disclosure" scheduled reconstruction blockchain paper`
- `"Blockchain-based Decentralized Time Lock Machines: Automated Reveal of Time-sensitive Information"`
- `"Time-Lock Encrypted Storage for Blockchains"`

High-signal hits:

- Deployable Threshold Information Disclosure on Ethereum
- Blockchain-based Decentralized Time Lock Machines: Automated Reveal of Time-sensitive Information
- Time-Lock Encrypted Storage for Blockchains

Assessment:

- Strong evidence that blockchain-coordinated threshold release with explicit time / inclusion conditions predates KEYSTONE.
- Did not find direct evidence in this track of a "dispute-key readiness" audit that exercises serviceability before authorization while preserving production confidentiality.

### Track D: availability committees and public on-chain escalation

Queries used:

- `cryptoeconomic security for data availability committees paper`
- `"data availability committee" cryptoeconomic security paper decryption committee availability`
- `"threshold decryption" "data availability" paper blockchain`

High-signal hits:

- Cryptoeconomic Security for Data Availability Committees

Assessment:

- Strong adjacent prior art for query-based service availability, contract escalation, slashing, and explicit success-probability analysis.
- This is not threshold decryption, but it directly challenges any broad claim that "publicly auditable committee availability with deadline/accountability" is new by itself.

## Known-item recovery and chaining

- Known item recovered directly for `Ferveo`, `ETHTID`, `DAC security`, `Context-Dependent Threshold Decryption`, and `tTLES`.
- Citation-chaining quality was limited by available browser snippets in this run; no separate commercial scholarly index was used.
- The `Context-Dependent Threshold Decryption` abstract itself names encrypted mempool deployment as a major application, tightening overlap with the KEYSTONE surface.

## Failed or inconclusive searches

- No high-confidence paper found that already combines all of the following in one source:
  - dispute-triggered authorized decryption,
  - explicit pre-authorization canary partial decryptions,
  - false-accept sampling analysis for current share serviceability,
  - correlated-failure-aware stratified auditing.
- Searches for exact phrases around `canary partial decryption`, `health check threshold decryption`, and `non-production threshold audit` produced mostly irrelevant or weak results.
- Patent and standards searches were not completed in this bounded pass.
- Some adjacent results were accessible only via snippets, not full open PDFs, so they remain lower-confidence lead signals rather than settled defeating evidence.

## Working objection summary

1. The broad "deadline-bounded authorized reconstructability" layer appears substantially prefigured by ETHTID, time-lock systems, and tTLES.
2. The "context-bound share" layer appears directly prefigured by Context-Dependent Threshold Decryption.
3. The "public accountability / on-chain escalation for committee service failure" layer appears prefigured at least adjacently by DAC work and directly for threshold-decryption misbehavior by Boneh et al.
4. The remaining potentially differentiating slice is narrower than the intake wording suggests: a non-revealing, pre-authorization readiness audit for dispute decryption under explicit churn/correlation assumptions.
