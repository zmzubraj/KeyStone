# Novelty Objections

Status: `DRAFT_INDEPENDENT_CHALLENGE`
Date accessed: `2026-08-29`

## Objection 1: The intake wording overclaims novelty at the problem-definition layer

Direct evidence:

- `ETHTID` already states safety and liveness for threshold-shared disclosure on Ethereum with predefined release time and on-chain deadlines.
- `tTLES` explicitly formalizes a blockchain storage/decryption service where decryption is allowed only when both inclusion and the target time condition hold.

Objection:

If KEYSTONE is described as newly formalizing "deadline-bounded authorized reconstructability" in a blockchain threshold-decryption setting, a reviewer can argue that this is too close to prior timed or conditional threshold-release formulations.

What would need to be narrower:

- emphasize dispute-triggered readiness *before* authorization
- emphasize that the audited object is current share serviceability, not merely eventual scheduled release

## Objection 2: Context binding is not novel on its own

Direct evidence:

- `Context-Dependent Threshold Decryption and its Applications` introduces a decryption context so shares from different contexts cannot be mixed, and explicitly positions encrypted mempool deployment as a major application.

Objection:

Any KEYSTONE novelty statement leaning on "context-bound DLEQ proofs" or "decryption shares tied to a specific authorization context" is vulnerable unless the novelty is in the readiness-audit composition, not in context-binding itself.

## Objection 3: Accountability and on-chain escalation are already populated prior-art surfaces

Direct evidence:

- `Accountability for Misbehavior in Threshold Decryption via Threshold Traitor Tracing` adds accountability to threshold decryption against rational misbehavior.
- `Cryptoeconomic Security for Data Availability Committees` already studies a committee service with client query, contract escalation, slashing, and explicit response-probability analysis under bribes.

Objection:

Public blame, slashing, deadline evidence, and committee-availability enforcement are not fresh by themselves. KEYSTONE must avoid presenting them as if they were the central novelty.

## Objection 4: Encrypted transaction systems already rely on threshold decryption liveness after ordering/finalization

Direct evidence:

- `Ferveo` defines mempool privacy such that transactions remain encrypted until inclusion is finalized and inclusion guarantees decryption and execution.
- `BEAT-MEV` continues that line with batched threshold decryption and publicly testable partial decryptions.

Objection:

If KEYSTONE is framed broadly as "encrypted rollups need publicly auditable decryption readiness," a reviewer may see it as a natural follow-on engineering concern inside an already established threshold-encrypted transaction literature rather than a new research object.

## Objection 5: The strongest remaining differentiator is narrower and must be stated exactly

Current adversarial inference from the bounded search:

I did **not** find a paper that clearly already performs all of the following together:

- a dispute-triggered authorization model
- a non-production canary partial-decryption exercise before authorization
- explicit false-accept bounds for present serviceability
- correlation-aware / failure-domain-aware sampling of committee members

Objection:

If KEYSTONE does not freeze the claim to this narrow composition, the prior-art bundle above can likely defeat the broader wording.

## Objection 6: The challenge is still incomplete on some surfaces

Access limits and residual risk:

- No full patent search in this pass
- No standards or industry design-doc sweep beyond visible public sources
- No commercial scholarly database coverage
- No exhaustive citation-chain expansion from every seed paper

Consequence:

This challenge is strong enough to narrow the claim boundary, but not strong enough to certify that the remaining narrow slice survives a submission-grade novelty audit.
