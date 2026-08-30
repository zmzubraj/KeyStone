DRAFT / PRIMARY_SEARCH
Date: 2026-08-29

# Strongest predecessor matrix

| Axis | Strongest predecessor(s) recovered | Verified overlap with KEYSTONE | What KEYSTONE cannot claim after this search | Possible surviving differentiator if later evidence holds | Risk |
| --- | --- | --- | --- | --- | --- |
| Public data availability for rollups | `EIP-7594: PeerDAS` | probabilistic sampling of public rollup/blob data availability | any claim to new DAS, rollup data sampling, or public-blob availability measurement | explicit separation between public ciphertext availability and private dispute-key serviceability | High if wording drifts |
| Encrypted AI / challenge-window threshold key release | `EigenAI` | encrypted AI execution, challenge window, threshold-released key, public auditability framing | any broad claim to threshold-released private AI verification or challenge-window key release | rollup-dispute-specific readiness audit before authorization and before revealing production decryptions | High |
| Context binding / share isolation | `Context-Dependent Threshold Decryption and Its Applications` | context as a first-class cryptographic input that isolates partial decryptions | context binding, transcript binding, or share isolation as new cryptography | bounded claim that MPP uses context-bound proof transcripts only, unless production scheme integrates this primitive | Critical |
| Consensus-authorized threshold release with public log | `UQ-Vote` | consensus-finalized authorization, public bulletin board, threshold release, liveness/fault scenarios | finalized authorization, bulletin-board logging, deadline-like release gating, or fault-scenario evaluation as standalone novelty | rollup-specific DKA property plus pre-dispute confidential readiness sampling and false-accept/correlation analysis | Critical |
| Proactive/dynamic secret sharing under churn | `Long Live The Honey Badger` | DPSS, churn handling, fault tolerance, share refresh/transfer under dynamic committees | dynamic/proactive secret sharing, churn tolerance, or high-level committee maintenance | sampled operational audit between setup/refresh events and during dispute windows | High |
| Verifiable partial decryptions / invalid-share detection | `Chosen Ciphertext Secure Public Key Threshold Encryption Without Random Oracles`; `Wallet Databases with Observers` lineage | partial decryption correctness proofs, robust detection of invalid responses, equality-of-discrete-log proof family | DLEQ/Chaum-Pedersen style correctness proof, verifiable partial decryption, or invalid-share identification | using these established proofs in a non-production canary audit tied to DKA measurement | High |
| Formal liveness accountability limits | `Accountable Liveness` | timing/network assumptions matter for accountable liveness and blame | timing-free blame for non-response, unconditional slashability, or guilt proof without network assumptions | narrow public evidence for invalid response/equivocation/conditional deadline miss under declared assumptions | Critical |
| Blockchain threshold decryption deployment | `Ferveo`; `Practical Mempool Privacy via One-time Setup Batched Threshold Encryption`; adjacent mempool privacy line | threshold decryption already deployed conceptually for blockchain privacy with liveness/security constraints | blockchain threshold encryption, batched threshold decryption, or committee release semantics as new | a dispute-readiness audit question distinct from transaction reveal liveness | High |
| Blockchain threshold key-service adjacency | `vetKeys` | blockchain can host a distributed threshold key service for many secrets | generic blockchain key-service availability framing | narrow dispute-key readiness property and audit procedure under authorized dispute deadlines | Medium |

# Provisional reading

The strongest collisions are not one single paper; they are a composite frontier:

- `PeerDAS` defeats any DA-sampling claim.
- `EigenAI` defeats broad encrypted-AI threshold-release novelty.
- `Context-Dependent Threshold Decryption` defeats context-binding novelty.
- `UQ-Vote` defeats finalized authorization plus public bulletin-board novelty.
- `Long Live The Honey Badger` defeats DPSS novelty.
- classical threshold-decryption and DLEQ lineage defeat proof-of-correctness novelty.
- `Accountable Liveness` defeats timing-free blame.

If KEYSTONE remains claimable, it is most plausibly as a narrow composition / property / analysis paper, not as a primitive or generic threshold-decryption paper.
