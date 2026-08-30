# DRAFT_INDEPENDENT_CITATION_AUDIT

Date: 2026-08-29
Scope: `C001`, `K-C1`–`K-C5`
Status: citation and claim audit only; no phase verdict

## Answer

The narrowed working differentiator in `research-case/01-novelty/novelty_reconciliation.md` is mostly safe as a **reframed hypothesis**, but it is not yet fully source-complete.

What is already well supported by current sources:

- `PeerDAS` is plainly about public blob/data availability sampling, not decryption-service readiness.
- `Ferveo`, `BEAT-MEV`, and `EigenAI` already occupy the encrypted-blockchain / threshold-release adjacency.
- `ETHTID`, `tTLES`, and `UQ-Vote` already occupy conditional authorization, deadline/release, and public-log surfaces.
- `Context-Dependent Threshold Decryption` already occupies context isolation as cryptographic prior art.
- `Accountability for Misbehavior in Threshold Decryption` and `Accountable Liveness` already constrain how far KEYSTONE can go on accountability and blame.

What is **not** affirmatively established by the current source set and must therefore be carried by KEYSTONE's own formalism, proofs, and experiments:

- the exact property `present dispute-key serviceability`;
- the exact protocol move `pre-authorization, non-production canary partial-decryption audit`;
- the exact theorem/result `catastrophic false-accept analysis`;
- the exact claim `correlated-failure qualifications` for the proposed audit; and
- the exact system surface `deadline-evidence interface` as a distinct contribution rather than a reuse of public-log/accountability patterns.

## Direct evidence

### Supported negative boundaries

1. `PeerDAS` says nodes can ensure blob data availability by downloading only a subset, with rollup scalability as the motivation. That supports using it only as the contrast class for ciphertext/data availability, not as anything about decryption readiness. Source: EIP-7594 (`https://eips.ethereum.org/EIPS/eip-7594`, accessed 2026-08-29).

2. `EigenAI` already combines encrypted AI logs, a challenge window, and threshold-released decryption inside a TEE. That defeats broad novelty language around encrypted AI plus threshold-released verification. Source: arXiv `2602.00182` (`https://arxiv.org/abs/2602.00182`, accessed 2026-08-29).

3. `ETHTID` already uses threshold-shared decryption reconstructed at a predefined time and recorded on-chain. That defeats any broad claim that deadline-bounded authorized reconstructability on chain is new. Source: arXiv `2107.01600` (`https://arxiv.org/abs/2107.01600`, accessed 2026-08-29).

4. `tTLES` already formalizes blockchain decryption conditioned on both inclusion and target time. That further narrows any claim built around conditional authorized decryptability alone. Source: IACR ePrint `2025/2048` (`https://eprint.iacr.org/2025/2048`, accessed 2026-08-29).

5. `Context-Dependent Threshold Decryption and its Applications` already introduces decryption context as a first-class cryptographic input that isolates shares across contexts. That defeats any claim that KEYSTONE newly provides context-bound share isolation. Source: IACR ePrint `2025/279` (`https://eprint.iacr.org/2025/279`, accessed 2026-08-29).

6. `UQ-Vote` already ties threshold decryption authorization to a consensus-finalized replicated state and explicit public workflow. That defeats novelty language around finalized authorization plus bulletin-board logging alone. Accessible source used in this audit: ResearchGate accepted-version page for the author copy (`https://www.researchgate.net/publication/412595509_UQ-Vote_Consensus-Authorized_Threshold_Decryption_for_End-to-End_Verifiable_Elections`, accessed 2026-08-29). IEEE final record was not independently confirmed in this run.

7. `Accountability for Misbehavior in Threshold Decryption via Threshold Traitor Tracing` already adds accountability to threshold decryption against leaked decryption capability. That defeats any claim that accountability in threshold decryption is itself the contribution. Source: IACR ePrint `2023/1724` (`https://eprint.iacr.org/2023/1724`, accessed 2026-08-29).

8. `Accountable Liveness` shows that deadline-based liveness accountability needs explicit timing assumptions and cannot be treated as timing-free blame. That strongly supports KEYSTONE's narrowed caveat around conditional deadline evidence only. Sources: ACM DOI `10.1145/3719027.3765032` and arXiv `2504.12218` (`https://dl.acm.org/doi/10.1145/3719027.3765032`, `https://arxiv.org/abs/2504.12218`, accessed 2026-08-29).

### Unsupported or only internally supportable clauses

The following narrowed clauses are not supported as established facts by the current predecessor set. They are only supportable as KEYSTONE's own proposed contributions if the manuscript provides direct internal evidence:

- `separates ciphertext data availability from present dispute-key serviceability`
- `pre-authorization, non-production canary partial-decryption audit`
- `explicit catastrophic false-accept analysis`
- `correlated-failure qualifications`
- `deadline-evidence interface` as a distinct contribution rather than inherited workflow machinery

These are not problems by themselves, but they must be written as `we define`, `we propose`, `we analyze`, or `we evaluate`, not as if prior literature has already validated them.

## Citation integrity findings

1. `paper/references.bib` is materially incomplete relative to the reconciled novelty boundary. It currently lacks entries for at least `ETHTID`, `Ferveo`, `tTLES`, `Practical Mempool Privacy via One-time Setup Batched Threshold Encryption`, and `vetKeys`. If the manuscript relies on the reconciliation wording, those missing entries are blocking citation gaps.

2. `UQ-Vote` metadata is not stable in the accessible copy used here. The ResearchGate wrapper shows DOI `10.1109/ACCESS.2026.3725080`, while the accepted-version PDF text visible on the same page also contains an inconsistent legacy-looking DOI string `10.1109/ACCESS.2024.0429000`. Safest treatment: cite it as an accessible accepted-version source only after independent IEEE Xplore confirmation, or keep it outside any sentence that requires exact final bibliographic certainty.

3. `primary-search/sources.csv` contains a metadata error for `Chosen Ciphertext Secure Public Key Threshold Encryption Without Random Oracles`: the current row says `2005` and `CRYPTO / Springer`, but the authoritative Springer record is `CT-RSA 2006`, pages `226-243`, DOI `10.1007/11605805_15`.

4. `Wallet Databases with Observers` needs consistent year handling. The conference is `CRYPTO '92`, but the Springer chapter metadata is published as `1993`. Pick one consistent bibliography convention and keep it stable.

5. `docs/18_LATEST_PRIOR_ART_WATCH_2026-08-29.md` adds `selective-withholding gap` and `reproducible encrypted-AI-rollup dispute prototype` to the "surviving claim", but `novelty_reconciliation.md` does not. That is a cross-document claim-boundary drift risk.

## Safest reading for root integration

- Treat the narrowed sentence in `novelty_reconciliation.md` as a claim-safe framing, not a source-proven conclusion.
- Add the missing bibliography entries before any manuscript prose adopts the reconciled predecessor table.
- Keep `UQ-Vote` marked as metadata-sensitive until the final IEEE record is independently checked.
- Keep every positive KEYSTONE clause attached to a theorem, experiment, or protocol artifact, not to related-work citations.

## Confidence

- High confidence on the negative findings about overclaim risk and missing bibliography coverage.
- Medium confidence on the positive differentiator wording, because it still depends on KEYSTONE's own unreviewed formal and empirical support.
