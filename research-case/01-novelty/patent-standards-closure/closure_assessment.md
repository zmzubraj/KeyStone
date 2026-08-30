# DRAFT/PRIMARY_SEARCH — closure assessment

This is a non-canonical recommendation from the bounded patent / standards / citation-lineage closure pass.

## Recommended disposition

`REFRAME`

## Why `REFRAME`

The closure pass did not recover one public patent or public standard that cleanly discloses the full narrow residual KEYSTONE/MPP story in one place. But it did recover enough adjacent evidence to make the broad framing even less defensible than it already was after the primary paper search.

### 1. Public patents further weaken broad “audit + threshold release” wording

- `EP3811560B1` explicitly places ciphertext storage, audit-triggered threshold decryption share release, and auditor verification into a blockchain-linked system.
- `US20170005797A1` shows that operational checking of share retrievability/readiness is not a novel idea at a generic system level.
- `WO2024228005A1` further shows that correctness-check-first threshold decryption is an active, public, modern design surface.

Result:
- it is not safe to present KEYSTONE as if “audit-triggered threshold-share release”, “share readiness audit”, or “correctness-checked threshold decryption” were new on their own.

### 2. Standards and public design documents crowd the rollup/L2 architectural surface

- `EIP-7594` occupies public DAS for rollup/blob availability.
- `Shutterized Optimism` occupies a public OP Stack threshold-encryption deployment architecture with committee roles, DKG, finality assumptions, and liveness-failure discussion.
- public `Fhenix` material occupies threshold-decryption-network framing for private Ethereum-oriented computation.

Result:
- KEYSTONE cannot honestly be framed as a first rollup threshold-encryption architecture, first threshold-release committee on L2, or first private-computation release network.

### 3. Citation chains confirm the literature is composite, not sparse

- `UQ-Vote` links consensus-authorized threshold release to a prior bulletin-board / threshold-decryption lineage.
- `Accountable Liveness` sits on an accountability and timing-assumption lineage.
- encrypted-mempool literature already cross-links `Ferveo`, `Shutter`, `vetKeys`, and later batched-threshold-decryption variants.
- classic threshold-encryption correctness/proof roots are old and heavily cited.

Result:
- broad combination claims are high risk because the combination space is already dense and historically layered.

## What may still survive after reframe

Only a much narrower candidate appears worth carrying forward:

1. the operational gap between public ciphertext/data availability and private dispute-key serviceability;
2. a pre-dispute, non-production readiness audit that avoids spending the real dispute path;
3. explicit false-accept / repeat-audit / correlation-aware analysis for that readiness signal;
4. a narrow public evidence layer under declared deadline/network assumptions.

Even this residual candidate remains unresolved, because:
- this closure pass was bounded;
- patent coverage was not exhaustive;
- private design documents and unpublished implementations remain outside reach;
- absence of a recovered direct public match is not proof of novelty.

## What should be removed from future framing

Remove or sharply narrow any wording that implies:

- new DAS;
- new threshold encryption or threshold decryption cryptography;
- first context-bound threshold release;
- first consensus-authorized threshold release with public logging;
- first dynamic/proactive share-maintenance method;
- first rollup encrypted-mempool / threshold-release architecture;
- first operational share-readiness audit in any broad sense.

## Exact bounded recommendation

Use the residual claim, if kept at all, as:

> a narrow operational measurement and dispute-readiness contribution built on inherited rollup DAS, threshold-decryption, DPSS, and accountability components

and not as:

> a new threshold-cryptography or rollup-architecture family.

## Residual risks

- Patent search was public-web bounded; Espacenet / Lens / classification review may still find stronger anticipation.
- Public standards/design docs are not the only relevant architecture evidence; private whitepapers or code may exist.
- Early OpenAlex forward counts understate the descendant literature for 2025–2026 items.
- If future wording drifts back toward “first system” or “new primitive” language, this closure pass already contains enough contrary evidence to defeat that framing.
