# KEYSTONE Protocol Specification v1

## 1. Protocol overview

KEYSTONE operates at epoch granularity. One threshold public key protects many record-specific data keys. Routine audits exercise custodians on fresh canary group elements. Authorized disputes exercise custodians on the target record’s threshold-KEM component.

## 2. Cryptographic suite used by the MPP

- Shamir secret sharing over subgroup order `q`
- Feldman coefficient commitments for share validation in the dealer prototype
- Threshold Diffie–Hellman KEM
- Chaum–Pedersen/DLEQ proofs for verifiable partial decryption
- SHA-256 Fiat–Shamir transcript hashing and KEM key derivation
- AES-256-GCM for data-key wrapping and record encryption

Production substitution points are explicitly defined for DKG/PVSS, standardized groups/curves, signatures, and attestation.

## 3. Data structures

### EpochDescriptor

| Field | Meaning |
|---|---|
| `epoch_id` | unique epoch identifier |
| `n`, `t` | committee size and threshold |
| `PK_E` | threshold public key |
| `commitments` | VSS/PVSS/DKG verification material |
| `members_root` | commitment to identity, public share, stake, and domain metadata |
| `active_from`, `active_until` | authorized record-encryption window |
| `policy_hash` | release policy and verifier-attestation policy |

### RecordEnvelope

| Field | Meaning |
|---|---|
| `record_id` | unique inference record |
| `epoch_id` | key epoch |
| `C1=g^r` | threshold-KEM component |
| `wrapped_K` | AEAD-wrapped record data key |
| `record_nonce` | record AEAD nonce |
| `ciphertext` | encrypted request/response/receipt |
| `aad` | rollup/model/receipt metadata bound by AEAD |
| `da_pointer` | location/inclusion reference |

### AuditRequest

| Field | Meaning |
|---|---|
| `audit_id` | unique request identifier |
| `epoch_id` | audited epoch |
| `beacon_value` | post-commit randomness |
| `sample` | selected custodian indices or derivation seed |
| `canary_X` | canonical `HashToGroup(protocol, epoch, audit_slot, beacon_value)` element with undisclosed discrete log |
| `q` | required valid responses |
| `deadline` | ledger deadline |
| `context` | domain-separated transcript context |

### AuditResponse

| Field | Meaning |
|---|---|
| `custodian_index` | registered index |
| `D_i=X^{x_i}` | canary partial decryption |
| `π_i` | DLEQ proof |
| `request_id` | transcript binding |
| `signature` | identity binding in production |
| `submitted_at` | ledger/relay timestamp |

### DisputeRequest

| Field | Meaning |
|---|---|
| `dispute_id` | unique dispute |
| `record_id` | target record |
| `epoch_id` | threshold-key epoch |
| `verifier_set_hash` | authorized destination identity/policy |
| `authorization_proof` | contract state or governance proof |
| `deadline` | release deadline |

### Evidence

`INVALID_PARTIAL`, `EQUIVOCATION`, `UNAUTHORIZED_RELEASE`, `NON_RESPONSE`, `STALE_EPOCH`, or `DOMAIN_POLICY_VIOLATION`, plus the public transcript required to verify the event.

## 4. Phase A — Epoch setup

1. Committee manager selects `n` custodians satisfying stake/identity and failure-domain placement constraints.
2. DKG/PVSS creates `PK_E` and one valid share per custodian. The MPP uses a dealer plus Feldman commitments only as a compact substitution.
3. Public shares and member/domain commitments are registered.
4. Each custodian performs a local self-test and signs an epoch-ready acknowledgement.
5. The contract activates the epoch only after admission policy is satisfied.

## 5. Phase B — Record sealing

1. Worker samples a fresh 256-bit data key `K_r`.
2. Worker encrypts the inference request/output/receipt with AEAD under `K_r`.
3. Worker samples threshold-KEM randomness `r` and publishes `C1=g^r`.
4. Worker derives `Z=PK_E^r`, derives a key-encryption key, and AEAD-wraps `K_r`.
5. Worker publishes `RecordEnvelope` to the DA layer and commits its hash on the rollup/settlement layer.
6. No custodian stores a per-record Shamir share.

## 6. Phase C — Routine readiness audit

1. Audit coordinator commits the epoch/audit slot before seeing the beacon.
2. Beacon output selects a uniform or domain-stratified set `S` of size `s`.
3. Every party derives the same canonical canary `X=HashToGroup("KEYSTONE-CANARY" || epoch_id || audit_slot || beacon_value)`. The coordinator cannot choose `X`, and the mapping does not expose `log_g(X)`.
4. Contract/bulletin board publishes `AuditRequest` and deadline.
5. Each sampled custodian checks epoch and request context, computes `D_i=X^{x_i}`, and produces DLEQ proof `π_i`.
6. Verifier checks identity, freshness, subgroup membership, proof validity, uniqueness, and deadline.
7. Audit passes when at least `q` valid responses arrive.
8. Failed audits trigger warning, focused re-audit, recovery, replacement, or epoch rotation according to policy.

Canary partial decryptions may be combined into `X^x`, but this does not decrypt a production record or reveal the threshold secret. Custodians reject non-canonical challenges, stale slots, or any request whose challenge was not derived from the registered beacon transcript.

## 7. Phase D — Authorized dispute release

1. Challenger opens a valid dispute against `record_id`.
2. Policy contract verifies challenge eligibility and binds the request to `verifier_set_hash` or an attested enclave identity.
3. The request is published with deadline `Δ_d`.
4. Custodians verify authorization and return partial decryption `D_i=C1^{x_i}` over an authenticated confidential channel to the authorized destination, with a publicly verifiable proof/commitment as policy permits.
5. Combiner verifies proofs and selects any `t` distinct valid responses.
6. Lagrange combination reconstructs `C1^x=PK_E^r` without reconstructing `x` itself.
7. The combiner derives the KEM key, unwraps `K_r`, decrypts the record, and performs deterministic re-execution.
8. The plaintext and data key are erased after adjudication according to policy.
9. Verdict and response evidence are finalized on-chain.

## 8. Phase E — Refresh, replacement, and rotation

- **Share refresh** changes shares while preserving the underlying epoch secret/public key; it limits accumulation by a mobile adversary.
- **Committee resharing** transfers the same secret to a revised committee.
- **Epoch rotation** creates a new underlying key and applies to new records; old challengeable records must retain an authorized decryption path until their retention window ends.
- A refresh is not forward secrecy for already encrypted records. Key rotation and retention policy must be analyzed separately.

## 9. Sampling modes

### Uniform

Every custodian has equal selection probability. This supports the clean hypergeometric bound.

### Domain-stratified

The sampler first draws a minimum number from each failure domain and fills remaining slots uniformly. It improves visibility into domain outages but changes the analytical distribution; the MPP evaluates it by exact enumeration where small and Monte Carlo otherwise.

### Escalating audit

A failed sample triggers a larger sample or full-committee challenge. Escalation reduces uncertainty at higher bandwidth and operational cost.

## 10. Evidence and slashing rules

- Invalid proof: positive cryptographic evidence; slashable after deterministic verification/adjudication.
- Equivocation: two conflicting signed/ledger-bound commitments; positive evidence.
- Unauthorized response/release: signed response bound to an invalid policy context; positive evidence when transcript is public.
- Non-response: request and deadline are public; penalty is justified only under the stated delivery/synchrony assumptions and should distinguish warning, temporary inactivity, replacement, and hard slashing.
- Correlated domain outage: generally a resilience failure, not automatically individual malice.

## 11. Domain-separation strings

The implementation uses separate transcript domains for:

- DLEQ proofs;
- audit request identity;
- dispute request identity;
- KEM key derivation;
- record key wrapping;
- member index binding;
- canonical canary hash-to-group derivation.

Production code must additionally bind chain ID, contract address, epoch, record/audit identifier, verifier policy, and protocol version.
