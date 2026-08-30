# DRAFT/PRIMARY_SEARCH — citation chain matrix

This matrix records the strongest backward / forward lineage recovered in the bounded closure pass.

| Anchor source | Recovery method | Backward / adjacent chain recovered | Forward / metadata signal recovered | Why it matters for KEYSTONE/MPP |
| --- | --- | --- | --- | --- |
| `UQ-Vote: Consensus-Authorized Threshold Decryption for End-to-End Verifiable Elections` | OpenAlex DOI lookup + Crossref raw snapshot | references include election public-audit lineage, PBFT-style consensus references, and `Wallet Databases with Observers` | OpenAlex record recovered, but early `cited_by_count` was still low; forward counts are immature for a 2026 item | shows consensus-authorized threshold release with public-audit / bulletin-board semantics is already a composite, citable literature line rather than a new pattern |
| `Context-Dependent Threshold Decryption and Its Applications` | OpenAlex DOI lookup | source already stands on 39 references in recovered metadata | OpenAlex recovered nonzero citation count (`1`) and DOI-backed landing page | shows context binding / share isolation is already explicit enough that KEYSTONE cannot claim it as new cryptography |
| `Accountable Liveness` | OpenAlex DOI lookup + Crossref raw snapshot | references include accountable-consensus and availability-accountability lineage, including the availability-accountability dilemma line | OpenAlex recovered the item, but forward counts remained immature | shows timing / accountability / blame conditions already have a formal lineage; KEYSTONE cannot claim timing-free liveness blame by default |
| `Weighted Batched Threshold Encryption With Applications to Mempool Privacy` | Crossref raw snapshot | backward chain explicitly links `Ferveo`, `Shutter`, `vetKeys`, `Practical mempool privacy via one-time setup batched threshold encryption`, `BEAT-MEV`, and related encrypted-mempool work | 2026 metadata snapshot indicates a dense active frontier | shows blockchain threshold decryption and release committees already sit inside a crowded applied literature, reducing room for broad architectural novelty |
| `Chosen Ciphertext Secure Public Key Threshold Encryption Without Random Oracles` | OpenAlex DOI lookup | classical threshold-encryption root with a large earlier citation ecosystem | OpenAlex recovered a high citation count (`133`) | anchors the point that partial-decryption correctness and robust threshold-decryption proof families are established building blocks |
| `Long Live The Honey Badger` | known-item recovery via USENIX page | DPSS lineage under churn/fault handling was explicitly recovered even when generic acronym search was noisy | conference-page recovery confirms the exact item exists and is relevant | prevents KEYSTONE from treating dynamic/proactive share refresh under churn as a fresh contribution |

## Closure interpretation

The citation-chain evidence does not by itself prove a direct one-document anticipation of the narrow residual KEYSTONE claim. It does show something important:

- the nearest predecessor set is not isolated;
- each broad building block already belongs to a living citation network;
- the operational story around threshold release, bulletin-board logging, liveness assumptions, DPSS maintenance, and encrypted-mempool deployment is crowded enough that composite novelty language is high risk.

Bounded implication:

- any surviving claim should be written as a narrow operational-measurement contribution built from inherited cryptographic and systems components, not as a new threshold-cryptography or rollup-architecture family.
