# Independent Patent/Code Challenge Assessment

Date: 2026-08-29
Scope: ultra-bounded independent challenge against `C001-narrow` using only (a) public Google Patents / WIPO records and (b) official Shutter / Optimism / Fhenix documentation.
Source constraint observed: I did not read the primary closure folder.

## Bottom line

I did **not** find a single public patent/doc source in this bounded slice that combines all of the following in one place:

1. dispute/challenge-authorization context,
2. a **pre-authorization, non-production** threshold-decryption readiness probe or drill,
3. explicit catastrophic **false-accept** analysis for present readiness, and
4. **correlation-aware** committee/failure analysis.

This search therefore does **not defeat** the narrow KEYSTONE composition/analysis claim on its face. It does, however, show that each component family has close adjacent predecessors, so the manuscript should keep the novelty claim narrow and integration-focused.

## Exact searches run on 2026-08-29

Patent/public-record queries:

- `site:patents.google.com threshold decryption readiness audit false accept patent`
- `site:patents.google.com threshold decryption canary partial decryption authorization patent`
- `site:patentscope.wipo.int threshold decryption readiness audit false accept`
- `site:patentscope.wipo.int partial decryption canary threshold authorization`
- `site:patents.google.com blockchain threshold decryption committee key shares patent`
- `site:patents.google.com encrypted mempool threshold decryption patent`
- `site:patents.google.com dispute challenge threshold decryption blockchain patent`
- `site:patentscope.wipo.int blockchain threshold decryption committee patent`
- `site:patents.google.com "false accept" threshold decryption blockchain patent`
- `site:patents.google.com "correlated" threshold decryption committee patent`
- `site:patents.google.com quorum decrypt shard proof verification patent`
- `site:patents.google.com pre-authorization partial decryption audit patent`
- `"WO2019191378" patentscope`
- `"WO2023156105" patentscope`
- `"digital wallet" "key shards" patentscope`

Official-doc queries:

- `Shutter Network threshold decryption docs keyper`
- `Optimism fault proof dispute game docs encryption threshold decryption`
- `Fhenix threshold decryption docs fhe coprocessor`
- `site:docs.shutter.network threshold decryption keyper audit readiness canary`
- `site:docs.optimism.io dispute game threshold encryption decryption challenge readiness`
- `site:docs.fhenix.zone OR site:docs.fhenix.io threshold decryption network audit readiness`

## Direct evidence and overlap assessment

### 1. Shutter official docs: threshold release and trigger-based availability, but no readiness-audit FAR/correlation analysis

Source:

- https://docs.shutter.network/docs/protocol/api/how_it_works

Observed:

- Shutter documents threshold key generation and conditional release: Keypers monitor registrations, perform threshold key generation, and release decryption keys once the trigger condition is met.
- The same page documents both time-based and event-based triggers.

Direct overlap with KEYSTONE:

- **Adjacent overlap** on authorized/conditional decryption release and public trigger handling.
- **Adjacent overlap** on separating ciphertext publication from later decryptability.

Missing relative to KEYSTONE narrow claim:

- no dispute-game or rollup-challenge context,
- no explicit pre-authorization **readiness drill** or canary audit,
- no explicit catastrophic false-accept formulation,
- no correlation-aware committee/failure analysis.

Consequence:

- Shutter is good defeating pressure against any broad “timed/triggered threshold release is new” language, but not a clean defeat of the narrow pre-authorization readiness-audit-plus-analysis claim.

### 2. Optimism official docs: dispute-game authorization context, but no threshold-decryption readiness audit

Source:

- https://docs.optimism.io/op-stack/fault-proofs/fp-security

Observed:

- Optimism documents permissionless fault dispute games via `DisputeGameFactory`.
- The security page is clearly dispute/challenge oriented.

Direct overlap with KEYSTONE:

- **Adjacent overlap** on dispute/challenge context and authorization boundary.

Missing relative to KEYSTONE narrow claim:

- no threshold decryption or share-serviceability mechanism,
- no pre-authorization canary partial-decryption probe,
- no false-accept analysis,
- no correlation-aware committee analysis.

Consequence:

- Optimism supplies the dispute-side context, but not the threshold-readiness mechanism or its analysis.

### 3. Fhenix official docs: access-controlled threshold decryption and integrity checks before decryption, but no readiness audit

Source:

- https://cofhe-docs.fhenix.zone/get-started/introduction/what-is-cofhe

Observed:

- Fhenix states that decryption is handled by a Threshold Network through multi-party computation.
- Decryption is optional and gated by signed access-control permissions.
- The docs also state that integrity is checked before decryption.

Direct overlap with KEYSTONE:

- **Adjacent overlap** on authorization-gated threshold decryption.
- **Adjacent overlap** on pre-decryption integrity verification.

Missing relative to KEYSTONE narrow claim:

- no rollup dispute/challenge readiness property,
- no non-production readiness drill/canary,
- no explicit false-accept bound for current serviceability,
- no correlation-aware committee/failure analysis.

Consequence:

- Fhenix narrows any claim that “authorized threshold decryption with integrity checks” is novel, but still does not show the specific readiness-audit framing.

### 4. Patent family: threshold-share authentication proof / secure blockchain voting

Sources:

- Google Patents: https://patents.google.com/patent/US20190305938A1/en
- WIPO search record result: https://patentscope.wipo.int/search/en/WO2019191378

Observed:

- The family title is `Threshold secret share authentication proof and secure blockchain voting with hardware security modules`.
- Public result metadata confirms WIPO publication `WO2019191378`.

Direct overlap with KEYSTONE:

- **Adjacent overlap** on threshold shares, blockchain setting, and proof/verification vocabulary.

Missing relative to KEYSTONE narrow claim:

- no public evidence here of a dispute-specific readiness property,
- no clear pre-authorization non-production partial-decryption drill,
- no false-accept readiness analysis,
- no correlation-aware committee analysis.

Consequence:

- This family weakens any attempt to market threshold-share proofing in blockchain as new by itself, but it does not, from the public record reviewed here, defeat the narrower KEYSTONE composition claim.

### 5. Patent family: provable backup confirmation for digital wallets using key shards

Source:

- https://patents.google.com/patent/US20240354753A1/en

Observed:

- The patent claims cryptographic proofs that a quorum of devices can decrypt encrypted shards without revealing the wallet private key.
- It also claims proof verifications indicating that the set of shards can reconstruct the key, including a second layer where decrypted shards can reconstruct a decryption key for an encrypted private key.

Direct overlap with KEYSTONE:

- **Closest adjacent overlap found in this bounded search** for a proof-of-can-decrypt / proof-of-reconstructability idea without full secret revelation.
- This is the strongest pressure against broad novelty language around “authorized reconstructability distinct from plaintext disclosure.”

Missing relative to KEYSTONE narrow claim:

- wallet-backup rather than rollup-dispute serviceability,
- no dispute/challenge authorization flow,
- no explicit non-production canary readiness drill,
- no catastrophic false-accept analysis,
- no correlation-aware committee/failure model.

Consequence:

- This appears to be the strongest adjacent predecessor in the searched patent slice. It pushes KEYSTONE toward a **context-specific property + audit framing** rather than any broad “proof of threshold readiness” claim.

### 6. WIPO/Google patent family: blockchain transaction with time-lock puzzle

Source:

- https://patents.google.com/patent/WO2023156105A1/en

Observed:

- The family covers time-locking a blockchain transaction so it decrypts only after a minimum time via a time-lock puzzle.
- Public Google Patents metadata identifies it as WIPO publication `WO2023156105A1`.

Direct overlap with KEYSTONE:

- **Adjacent overlap** on delayed/conditional decryptability in a blockchain setting.

Missing relative to KEYSTONE narrow claim:

- no threshold committee readiness,
- no pre-authorization canary partial-decryption probe,
- no dispute-serviceability framing,
- no false-accept or correlation analysis.

Consequence:

- This defeats any broad implication that conditional future decryptability in blockchains is new, but it is materially different from KEYSTONE’s threshold-readiness audit framing.

## Combined assessment: direct vs adjacent overlap

No searched source provided a **direct overlap** that matches the claim-spec defeating pattern:

- dispute/challenge authorization,
- pre-authorization non-production partial-decryption readiness audit,
- explicit readiness false-accept analysis,
- and correlation-aware committee sampling/failure analysis.

What I found is a **distributed adjacent-overlap picture**:

- Shutter: trigger-based threshold release,
- Optimism: dispute-game challenge context,
- Fhenix: access-controlled threshold decryption with integrity checks,
- `US20240354753A1`: proof-like evidence that a quorum can decrypt/reconstruct without exposing the protected secret,
- `WO2023156105A1`: conditional/time-based future decryptability in blockchain.

That combination means the manuscript should claim novelty, if at all, only at the **specific composition + property-separation + analysis** level.

## Access limits

- PATENTSCOPE search results were partially discoverable, but direct fetches for at least one WIPO record returned `403 Forbidden` in this environment, so I could not inspect the full WIPO detail page text.
- The official-doc search slice did not surface any Shutter / Optimism / Fhenix page discussing explicit false-accept-rate formulas or correlation-aware readiness analysis.
- Because this challenge was intentionally ultra-bounded, a non-patent literature predecessor could still exist outside this slice.

## Manuscript consequence

Recommended consequence for the current novelty position:

- keep disposition at **`NOVELTY_UNRESOLVED`** after this challenge alone;
- do **not** claim novelty for threshold decryption, authorized release, timed/event-triggered release, integrity checks before decryption, or proof-of-share/proof-of-quorum ideas in the abstract;
- if the manuscript proceeds, frame KEYSTONE as a **rollup-dispute-specific serviceability property** plus a **non-production pre-authorization readiness audit** plus **explicit static/correlated failure analysis**;
- treat `US20240354753A1` as the strongest adjacent patent pressure and Shutter/Fhenix/Optimism as the strongest code/doc pressure in this bounded slice.

Provisional bounded outcome:

- `No defeating predecessor found in this patent+official-doc slice.`
- `Strong adjacent art exists; broad novelty language would be unsafe.`
