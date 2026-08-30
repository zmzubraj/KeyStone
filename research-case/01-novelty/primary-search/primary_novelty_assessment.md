DRAFT / PRIMARY_SEARCH
Date: 2026-08-29
Status: novelty unresolved; bounded primary-search assessment only

# Executive assessment

Primary-search result: the frozen KEYSTONE wording survives only in a narrow form, and only provisionally.

The search did recover strong collisions against almost every broad version of the idea:

- data-availability sampling is already covered by `PeerDAS`;
- encrypted AI with threshold-released keys and challenge windows is already present in `EigenAI`;
- context-bound decryption isolation is already present in `Context-Dependent Threshold Decryption and Its Applications`;
- consensus-authorized threshold decryption with a public log and liveness/fault handling is already present in `UQ-Vote`;
- proactive/dynamic committee share maintenance is already present in `Long Live The Honey Badger`;
- verifiable partial decryption and equality-of-discrete-log proof families are established building blocks;
- timing-sensitive accountable-liveness limits are already formalized.

Therefore KEYSTONE cannot honestly be framed as:

- a new threshold-encryption primitive;
- the first context-bound threshold-decryption protocol;
- the first consensus-authorized threshold release system;
- the first bulletin-board accountability protocol;
- the first encrypted AI rollup with threshold-released keys;
- the first proactive or dynamic threshold-key maintenance system; or
- a timing-free blame or slashing result.

# Bounded surviving differentiator hypothesis

What may still survive, subject to independent challenge, is the following composite claim:

`KEYSTONE formalizes dispute-key availability for encrypted rollup disputes as a distinct property from ciphertext data availability, and instantiates a non-production canary audit with exact false-accept / repeated-audit analysis, correlation-aware placement and sampling, and a narrow public deadline-evidence layer.`

In this framing, the novelty is not any primitive component. It is the composition of:

1. a rollup-dispute-specific property boundary;
2. a pre-dispute confidential readiness question;
3. a canary partial-decryption procedure that does not use production ciphertext;
4. explicit catastrophic false-accept and repeated-audit conditions;
5. correlated-failure-aware committee analysis; and
6. a constrained accountability interface tied to the dispute workflow.

# Strongest objections that remain active

## Objection 1: composite novelty may still collapse

Even if no single paper matches the full frozen sentence, a reviewer may argue that KEYSTONE is an obvious composition of:

- DA sampling for public data,
- threshold decryption,
- DLEQ proofs,
- proactive share maintenance,
- accountable liveness, and
- blockchain public logging.

This objection remains live and must be challenged independently.

## Objection 2: context-binding wording is fragile

Because context-dependent threshold decryption now exists as a direct primary source, any wording suggesting that KEYSTONE newly binds or isolates decryption shares by context is unsafe unless the manuscript clearly distinguishes:

- transcript-domain binding in the MPP, from
- full cryptographic share isolation in the newer primitive.

## Objection 3: bulletin-board and finalized-authorization novelty is unsafe

`UQ-Vote` is too close on this axis to leave casual systems-language untouched. KEYSTONE should not claim public request logging, finalized authorization, or deadline-linked threshold release as independent innovations.

## Objection 4: timing assumptions must be explicit

Because accountable-liveness literature already formalizes harsh limits, any claim that missing responses can always be blamed is unsafe. KEYSTONE should stay with conditional evidence for:

- invalid responses,
- equivocation, and
- deadline misses under declared synchrony / delivery assumptions.

## Objection 5: direct close collision may still appear

The bounded search found no direct paper that obviously combines all frozen elements, but this field is currently active. A 2026 or later close predecessor could still surface during independent challenge or submission-time refresh.

# Recommended claim-safe language for root integration

Safe direction after this draft:

- `We formalize dispute-key availability for encrypted rollup disputes as distinct from ciphertext data availability.`
- `We instantiate a non-production readiness audit using established verifiable partial-decryption techniques.`
- `We analyze false-accept risk and correlated-failure effects under explicit assumptions.`
- `We expose a narrow dispute-deadline evidence interface rather than claiming unconditional blame.`

Unsafe direction after this draft:

- `first threshold decryption for AI rollups`
- `new proof of share possession`
- `new context-bound threshold decryption`
- `new bulletin-board threshold release`
- `proof of future availability`
- `timing-free slashing / blame`

# Required next novelty checks

Before any phase promotion, root should still require:

1. a differently owned independent novelty challenge over the same frozen claim set;
2. title/abstract/full-text screening on any additional 2025-2026 hits from IACR, IEEE, ACM, USENIX, arXiv, OpenAlex, and Ethereum research channels;
3. a patent and standards-adjacent check if the target venue or filing strategy makes that material;
4. explicit manuscript edits that separate building blocks from the claimed composition;
5. submission-time refresh immediately before abstract freeze.

# Confidence

Moderate confidence in the negative findings about overclaim risk.

Lower confidence in the positive statement that no direct full collision exists, because:

- this was a bounded pass, not an exhaustive universal search;
- some relevant surfaces may be inaccessible or weakly indexed; and
- the area is still moving quickly.

# Bottom line

This search supports keeping the frozen KEYSTONE direction only as a narrow property-and-composition paper with explicit exclusions.

It does not support broad novelty language.
