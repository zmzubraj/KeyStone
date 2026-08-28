# Roles, Trust Boundaries, and Responsibilities

## Role catalogue

| Role | Holds secrets? | Core responsibility | Evidence produced | Failure consequence |
|---|---|---|---|---|
| User/client | plaintext request | submit request and verify receipt | request commitment | request unavailable or privacy leak at client |
| Rollup worker/operator | transient plaintext and data key | execute inference, seal record, publish receipt | signed receipt and DA commitment | correctness challenge/slashing |
| DA layer | ciphertext only | retain/retrieve encrypted envelope | inclusion/availability evidence | ciphertext unavailable |
| Custodian | one epoch share | answer audits and authorized disputes | partial decryption, proof, signature | warning, replacement, slash depending on evidence |
| Committee manager | membership policy | select diverse committee, rotate/replace | epoch descriptor | correlated-risk or governance failure |
| Randomness beacon | no key share | unpredictable post-commit sample seed | beacon output | biased/predictable audit |
| Audit coordinator/watcher | no production key | schedule audit, verify responses, trigger escalation | audit transcript | missed degradation |
| Policy/dispute contract | no plaintext | authorize requests, record deadlines/evidence | canonical ledger state | unauthorized release or ambiguous deadline |
| Authorized combiner/verifier | reconstructs KEM secret/data key transiently | collect `t` valid partials and decrypt inside policy boundary | decryption/re-execution verdict | plaintext exposure or failed dispute |
| TEE/attestation service | transient plaintext when used | enforce code identity and protected execution | attestation quote | outside core DKA; confidentiality risk |
| Adjudicator/slasher | no plaintext required for proof failures | classify evidence and apply penalties | verdict | false penalty or weak deterrence |
| Governance/recovery operator | may coordinate refresh | replace nodes and preserve challengeability | rotation/reshare transcript | loss of old-record decryptability |

## RACI matrix

Legend: R=responsible, A=accountable, C=consulted, I=informed.

| Activity | Worker | Custodian | Audit coordinator | Policy contract | Verifier | Committee manager |
|---|---|---|---|---|---|---|
| Create encrypted record | R/A | I | I | I | I | I |
| Publish record commitment | R | I | I | A | I | I |
| Create epoch key | I | R | I | I | I | A |
| Schedule audit | I | I | R | A | C | C |
| Answer audit | I | R/A | C | I | I | I |
| Evaluate audit | I | C | R | A | C | I |
| Open dispute | C | I | C | A | R | I |
| Release partials | I | R/A | I | C | C | I |
| Combine/decrypt | I | C | I | I | R/A | I |
| Replace custodian | I | C | C | I | I | R/A |
| Apply slashing | I | C | C | A | C | C |

## Custodian local components

Each custodian implementation should isolate:

1. **Share vault:** HSM/TEE/filesystem abstraction holding current share and epoch metadata.
2. **Policy verifier:** checks audit/dispute authorization, chain state, epoch, deadline, and destination.
3. **Partial-decryption engine:** computes the exponentiation.
4. **Proof engine:** creates DLEQ proof and response signature.
5. **Response relay:** submits public commitment and sends confidential payload where required.
6. **Audit log:** stores request/response hashes, timing, and local failures.
7. **Refresh agent:** participates in external proactive refresh/resharing.

## Separation-of-duty recommendations

- Committee selection and slashing adjudication should not be controlled by one unreviewed key.
- Audit coordinators may be permissionless; canonical audit slots and beacons must be contract-defined.
- The verifier destination should not select the custodian sample.
- Custodians should not rely solely on the worker for authorization data.
- Domain metadata should be externally attestable or economically accountable; self-declared “independence” is insufficient.
