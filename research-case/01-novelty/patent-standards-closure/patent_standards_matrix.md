# DRAFT/PRIMARY_SEARCH — patent and standards overlap matrix

This matrix adds public patents and standards/design documents to the novelty case. It does not change canonical program state.

| Source | Surface | Verified overlap with KEYSTONE/MPP | What broad claim it weakens | What it does **not** show | Closure implication |
| --- | --- | --- | --- | --- | --- |
| `EP3811560B1` | public patent | permissioned blockchain system stores ciphertexts and, when an audit procedure is needed, sends threshold decryption shares to an auditor who verifies correctness | any broad claim that blockchain-linked audit-triggered threshold-share release is new | no verified disclosure here of rollup public-DA vs private-dispute-key separation, pre-dispute canary audit, false-accept analysis, or correlation-aware sampling | strong adjacent patent overlap; pushes residual novelty away from “audit + threshold release” framing |
| `US20170005797A1` | public patent | system periodically challenges stored secret shares using proof-of-retrievability | any broad claim that operational secret-share availability or retrievability auditing is new | not rollup/dispute specific; not a threshold-decryption committee serviceability analysis | strong adjacency against generic “share readiness audit” language |
| `WO2024228005A1` | public patent | threshold decryption method explicitly performs a correctness check before decryption | any broad claim that correctness-check gating around threshold decryption is novel | no evidence of blockchain dispute procedure, public evidence layer, or readiness sampling | background only; confirms modern patent activity around correctness-checked threshold decryption |
| `EIP-7594` | official standard | public probabilistic sampling for rollup/blob data availability; explicit withholding-attack reasoning | any broad claim to new DAS, public blob sampling, or rollup data-availability verification | does not address private dispute-key serviceability or threshold decryption readiness | decisive against broad C001/K-C1 wording; residual claim must be about the gap between public ciphertext availability and private key serviceability |
| `Shutterized Optimism` | public OP Stack technical architecture | threshold-encrypted mempool for OP Stack / Bedrock; keyper set; DKG; liveness failures; finality assumptions; encrypted tx flow | any broad claim that rollup/L2 threshold-encryption deployment architecture is new | does not show pre-dispute canary auditing or KEYSTONE’s exact residual measurement claim | very strong architecture overlap; residual claim cannot be “first rollup threshold-release architecture” |
| `Fhenix` FHE rollups page | public design/architecture statement | threshold decryption network used to release confidential computation outputs in Ethereum-oriented systems | any broad claim that a threshold decryption service/network for private L2-like computation is novel | does not directly show dispute-triggered readiness auditing, false-accept math, or canary sampling | strong practical-consequence overlap; broad private-computation threshold-release framing becomes unsafe |
| `Long Live The Honey Badger` | known-item recovery / public conference page | asynchronous high-threshold DPSS with churn/fault handling | any broad claim that dynamic/proactive share maintenance under churn is new | does not target rollup dispute-readiness auditing itself | confirms that committee refresh / churn handling must be treated as inherited prior art |

## Net effect on the residual claim

After adding these public patent and standards/doc surfaces:

- the public-DA part is clearly occupied by `PeerDAS`;
- the rollup/L2 threshold-encryption deployment part is clearly occupied by the `Shutterized Optimism` and adjacent encrypted-mempool / confidential-computation line;
- the generic “audit or readiness of shares” language is weakened further by `EP3811560B1` and `US20170005797A1`;
- correctness checking before decryption is not a clean novelty surface.

What remains potentially distinct is much narrower:

1. ciphertext/data may be publicly available while dispute-key serviceability is still unverified;
2. serviceability is audited before the real dispute path using non-production canaries / proof transcripts;
3. the contribution is framed as a measurable readiness problem with explicit false-accept / repeat-audit / correlation assumptions;
4. the evidence layer is limited to declared deadline and network assumptions rather than universal blame.

That residual area remains only a bounded candidate, not a verified novelty clearance.
