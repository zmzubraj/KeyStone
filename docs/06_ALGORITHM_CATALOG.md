# Algorithm Catalogue

## A1 — EpochSetup

**Input:** security parameters, `n`, `t`, member identities, domain metadata.  
**Output:** `EpochDescriptor`, one private share per custodian.

```text
1. Validate 1 ≤ t ≤ n and placement cap max_d n_d ≤ n-t.
2. Run external DKG/PVSS to obtain PK_E, public verification data, and shares x_i.
3. For every i, verify the share/public-share relation.
4. Commit (identity_i, public_share_i, stake_i, domain_i) in members_root.
5. Require admission acknowledgements from the policy-defined quorum.
6. Register and activate epoch E.
```

**MPP substitution:** dealer-generated Shamir polynomial with Feldman commitments.  
**Complexity:** external DKG-dependent; local validation `O(nt)` exponentiations in the compact prototype.

## A2 — SealRecord

```text
Input: PK_E, record_id, plaintext M, associated data aad
1. Sample K_r ← {0,1}^256.
2. C_data ← AEAD.Enc(K_r, M, aad).
3. Sample r ← Z_q*.
4. C1 ← g^r; Z ← PK_E^r.
5. KEK ← KDF(Z, record_id, aad, protocol_version).
6. C_key ← AEAD.Enc(KEK, K_r, "key-wrap" || record_id || aad).
7. Publish envelope (E, record_id, C1, C_key, C_data, aad).
```

**Complexity:** two exponentiations plus two AEAD operations.

## A3 — DeriveUniformSample

```text
Input: ordered member list L, beacon β, sample size s
1. seed ← H("sample" || epoch || slot || β).
2. S ← deterministic sample-without-replacement(L, s, seed).
3. Return S.
```

**Security condition:** `β` is unpredictable before the audit commitment.

## A4 — DeriveStratifiedSample

```text
Input: members partitioned by failure domain D_1...D_k, beacon β, s, minimum m
1. Require km ≤ s.
2. For each domain D_j, draw m members with domain-separated seed H(β || D_j).
3. Draw remaining s-km members uniformly from unselected members.
4. Return S.
```

## A5 — DeriveCanonicalCanary

```text
Input: group G, protocol version v, epoch E, audit slot a, finalized beacon β
1. transcript ← "KEYSTONE-CANARY" || v || E || a || β.
2. X ← HashToGroup_G(transcript).
3. Require X ≠ 1 and subgroup membership.
4. Publish the transcript; every custodian independently recomputes X.
```

The coordinator does not select the challenge. The hash-to-group mapping does not expose `log_g(X)`, and no production ciphertext is used. Custodians reject any non-canonical challenge.

## A6 — CustodianAuditResponse

```text
Input: share x_i, public share Y_i, canary X, audit context ctx
1. Verify epoch, sample membership, freshness, deadline, and context.
2. D_i ← X^{x_i}.
3. Choose w ← Z_q.
4. A_1 ← g^w; A_2 ← X^w.
5. e ← H("DLEQ" || g || Y_i || X || D_i || A_1 || A_2 || ctx || i).
6. z ← w + e x_i mod q.
7. Return (i, D_i, π_i=(A_1,A_2,z), signature).
```

## A7 — VerifyAuditResponse

```text
Input: registered Y_i, response (D_i,A_1,A_2,z), X, ctx
1. Reject wrong identity/index, stale context, duplicate, or late response.
2. Check subgroup membership of X, Y_i, D_i, A_1, A_2.
3. Recompute e.
4. Accept iff g^z = A_1 Y_i^e and X^z = A_2 D_i^e.
```

**Complexity:** approximately four multi/exponentiation checks per response.

## A8 — EvaluateAudit

```text
Input: sample S, valid-response set V, threshold q
1. passed ← |V| ≥ q.
2. For each invalid signed response, emit INVALID_PARTIAL evidence.
3. For each conflicting signed response, emit EQUIVOCATION evidence.
4. After deadline, record missing sample members as NON_RESPONSE observations.
5. If failed, apply escalation policy: larger sample, full check, recovery, or rotation.
6. Return audit result and evidence bundle.
```

## A9 — AuthorizedDispute

```text
Input: record_id, challenge proof, verifier_set_hash, deadline
1. Verify record remains challengeable.
2. Verify challenger bond and dispute predicate.
3. Bind request to epoch, record C1, verifier identity/policy, and deadline.
4. Publish canonical DisputeRequest.
```

## A10 — CustodianDisputeResponse

```text
Input: share x_i, record C1, authorized dispute context ctx_d
1. Verify authorization and destination policy.
2. D_i ← C1^{x_i}.
3. Produce context-bound DLEQ proof.
4. Publish response commitment/signature.
5. Deliver D_i and proof through the policy-authorized channel.
```

## A11 — CombineAndOpen

```text
Input: t distinct verified partials (i,D_i), sealed record
1. For each i, λ_i ← Π_{j≠i} (-j)/(i-j) mod q.
2. Z ← Π_i D_i^{λ_i} mod p.          // equals C1^x = PK_E^r
3. KEK ← KDF(Z, record_id, aad, version).
4. K_r ← AEAD.Dec(KEK, wrapped_K, wrap_aad).
5. M ← AEAD.Dec(K_r, record_ciphertext, aad).
6. Return M or authentication failure.
```

**Complexity:** `O(t^2)` scalar arithmetic in the simple implementation and `O(t)` exponentiations. Batch inversion can reduce coefficient work.

## A12 — GenerateAccountabilityEvidence

```text
Input: canonical request, signed response transcript, ledger timestamps
1. INVALID_PARTIAL: include response and failed deterministic verification.
2. EQUIVOCATION: include two conflicting signed commitments.
3. UNAUTHORIZED_RELEASE: include response bound to a context with no valid authorization.
4. NON_RESPONSE: include request/deadline and absence bitmap; classify under network model.
5. Return evidence hash and adjudication class.
```

## A13 — RefreshAndReshare Integration

```text
1. Trigger before compromise/churn budget is exceeded.
2. Run external proactive refresh or dynamic resharing.
3. Preserve PK_E when old challengeable records must remain decryptable.
4. Verify new share/public-share data and retire old local shares.
5. Re-run admission audit before marking the refreshed committee active.
```

## A14 — MonteCarloDKA

```text
Input: n,t,s,q, domain placement, independent failure p_i, domain failure p_d,
       selective-withholder set, trials N
For trial = 1...N:
  1. Draw failed domains.
  2. Draw independent node outages.
  3. Derive audit-ready and dispute-ready sets.
  4. Sample custodians using selected strategy.
  5. Record audit pass, catastrophic state, false pass, and reconstruction success.
Return rates, confidence intervals, and raw seed/configuration.
```

## Algorithm-to-code map

| Algorithm | File |
|---|---|
| A1 | `prototype/src/keystone/threshold_kem.py:dealer_keygen` |
| A2 | `threshold_kem.py:seal_record` |
| A3/A4 | `sampling.py` |
| A5–A8 | `protocol.py`, `dleq.py` |
| A9 | `contracts/src/KeystoneBulletinBoard.sol` |
| A10/A11 | `threshold_kem.py`, `protocol.py` |
| A12 | `protocol.py` and contract events |
| A14 | `simulation.py`, `scripts/run_experiments.py` |
| Canonical request/response transcript | `serialization.py`, `paper/test_vectors.json` |
| Canonical response signature | `signatures.py`, `paper/signature_test_vectors.json` |
| Experimental zero-polynomial share refresh | `threshold_kem.py:refresh_epoch_shares`, `tests/test_refresh.py` |
