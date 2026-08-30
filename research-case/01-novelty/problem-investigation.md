# KEYSTONE problem investigation

Status: `DRAFT / PRE-SEARCH PROBLEM SPECIFICATION`
System: `KEYSTONE-MPP-F1`
Date: `2026-08-29`
Scope: frozen claims `C1`-`C6`; manuscript claims `C001`, `C003`, `K-C1`-`K-C5`

## 1. Problem statement

The operational gap is not whether ciphertext bytes are retrievable. The gap is
whether, after a valid dispute authorization, an encrypted rollup can obtain at
least `t` valid decryption contributions before deadline `Delta_d` without
revealing a production plaintext or production decryption key before that
authorization.

The problem exists because these conditions can diverge:

- ciphertext or receipt bytes can remain publicly available while fewer than
  `t` custodians are currently dispute-serviceable;
- registered shares can be valid at setup time while current dispute-time
  serviceability has failed because of outage, churn, invalid response, or
  selective withholding;
- a routine audit can show present operational readiness for a sampled subset
  without implying unconditional future dispute success.

## 2. Why the problem matters

For encrypted AI rollups, the dispute path is the safety valve for incorrect or
malicious execution. If the dispute opens but threshold decryption misses the
deadline, the system can have:

- public ciphertext availability without usable adjudication;
- formally valid cryptographic setup without operational decryptability;
- liveness evidence that is too weak to distinguish current serviceability from
  future guaranteed cooperation.

This makes "data available" and "dispute decryption serviceable" different
security properties.

## 3. Stakeholders and failure consequences

| Stakeholder | Dependency | Failure if DKA is absent |
| --- | --- | --- |
| Honest challenger | must open one authorized dispute before deadline | cannot prove the challenged execution |
| Rollup users | rely on dispute path for safety | ciphertext exists but dispute remedy fails |
| Custodian committee operator | must maintain serviceable threshold path | latent outages stay hidden until a real dispute |
| Adjudicator or contract | needs auditable evidence of response behavior | cannot separate invalid response from non-response evidence |
| Research reader or reviewer | needs a claim-safe contribution boundary | may reject the paper as DA or threshold-encryption repackaging |

## 4. Core estimand and measurable question

The narrow measurable object is:

`P(DDL(r,E,tau,Delta_d)=1 | declared readiness model, valid authorization)`

under a stated class of failures.

The canary audit does not measure `DDL` directly. It measures an audit-side
proxy:

`P(AKR(E,S,tau)=1 | current sampled custodians, canonical canary, Delta_a)`.

The scientific question is therefore two-step:

1. can a non-production canary audit produce public, cryptographically checked
   evidence about current sampled serviceability; and
2. under which declared assumptions does that evidence bound catastrophic false
   acceptance for present dispute readiness?

## 5. Causal bottleneck

The bottleneck is not missing cryptographic decryption capability in the
abstract. The bottleneck is the hidden state between setup correctness and
deadline-bounded dispute execution.

Necessary upstream conditions:

- `CA`: encrypted record and receipt bytes remain retrievable;
- `VSR`: custodian shares were validly registered;
- sample unpredictability is preserved until the sample is fixed;
- audit transcripts are canonical and identity-bound.

Latent operational state:

- whether each custodian can access its current valid share;
- whether the custodian process is online in time;
- whether the failure is correlated by provider, region, or software domain;
- whether the custodian will cooperate on a targeted dispute, not only a canary.

Observed outputs:

- valid canary partial decryptions with proof;
- invalid responses;
- equivocation evidence;
- absence by deadline.

Outcome of interest:

- `DKA` or `DDL` success on an authorized dispute.

## 6. Alternative explanations that can defeat the claim

- The apparent problem is already fully captured by prior timed or authorized
  threshold-release formulations.
- A routine canary audit is only a monitoring trick and does not define a
  distinct property from existing liveness/accountability work.
- The claimed separation from ciphertext availability is too weak because
  existing encrypted-rollup papers already imply the same distinction.
- Correlation-aware sampling adds engineering detail but not a material research
  contribution.

These objections must remain live until a stronger novelty closure is complete.

## 7. Materiality thresholds for the narrow working claim

The narrow claim is materially differentiating only if all of the following hold:

1. the paper defines `DKA` or an equivalent dispute-specific serviceability
   property that is explicitly distinct from ciphertext availability and from
   one-time share validity;
2. the protocol exercises non-production current serviceability before
   authorization rather than only scheduled release or post-authorization
   decryption;
3. the analysis gives an explicit catastrophic false-accept quantity for the
   readiness probe under a declared sampling model;
4. the evaluation studies correlated or failure-domain-aware readiness, not only
   IID outages; and
5. the manuscript does not slide into primitive-level novelty claims.

If any one of these fails, the surviving contribution narrows sharply or
collapses into prior art.

## 8. Defeating evidence criteria

The narrow novelty claim is defeated if a credible predecessor already combines,
for the same substantive setting:

- dispute-triggered or equivalently challenge-triggered authorization;
- a non-production pre-authorization partial-decryption readiness probe;
- explicit present-serviceability false-accept or detection analysis; and
- correlation-aware or stratified committee readiness evaluation.

The broader claim is already effectively defeated by the current bounded search.

## 9. Explicit non-claims

This problem framing does not assert:

- a new threshold-encryption primitive;
- new context-dependent threshold cryptography;
- a new DLEQ or proof-of-share-possession primitive;
- unconditional proof of future availability from a current audit;
- timing-free blame for non-response;
- resistance to a fully adaptive selective-withholding adversary.

## 10. Cheapest falsification tests

1. Counterexample construction:
   show an execution where ciphertext is retrievable but fewer than `t`
   custodians are dispute-ready. If such an execution is impossible under the
   actual deployment model, the property separation weakens.
2. Prior-art closure:
   find one predecessor that already performs pre-authorization canary
   threshold-decryption readiness probing with explicit false-accept analysis.
3. Operational proxy failure:
   show that the canary transcript can be answered while providing no meaningful
   information about current serviceability beyond existing heartbeats or static
   registration checks.
4. Selective-withholding gap:
   show that audit success systematically coexists with dispute failure under a
   realistic adversary, forcing the claim down to a very narrow monitoring
   utility statement.

## 11. Current disposition

`NOVELTY_UNRESOLVED`.

The problem itself is valid enough to study, but the research contribution must
remain framed as a narrow property-composition-analysis hypothesis until patent,
standards-adjacent, and citation-chain closure are complete.
