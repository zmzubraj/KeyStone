# KEYSTONE candidate portfolio

Status: `DRAFT / PROBLEM-SOLUTION PORTFOLIO`
System: `KEYSTONE-MPP-F1`
Date: `2026-08-29`
Disposition: `NOVELTY_UNRESOLVED`

## 1. Objective

Identify causally distinct ways to address the hidden gap between valid setup
and deadline-bounded dispute decryptability, then retain only the candidate that
best matches the frozen scope and surviving novelty boundary.

## 2. Candidate families

| Candidate | Family | Core idea | Why causally distinct |
| --- | --- | --- | --- |
| A | cryptographic readiness probe | sampled custodians answer a canonical non-production canary with proof | measures current serviceability by exercising the partial-decryption path |
| B | operational telemetry or heartbeat | custodians attest online status, hardware health, or signed heartbeat freshness | infers readiness from external signals without exercising cryptographic serviceability |
| C | post-authorization live drill | periodically run a full or quasi-full authorized decryption exercise on sacrificial data | tests dispute-time execution by simulating the actual release path |
| D | setup-time assurance only | rely on VSS/PVSS/DKG validity, registration, and occasional refresh | treats correct setup as the main assurance object |

## 3. Candidate A: canonical canary readiness probe

Mechanism:

- fix a sample after a public beacon;
- derive a canonical non-production group element;
- require sampled custodians to return partial decryptions and proofs;
- accept only if at least `q` valid responses arrive by deadline.

Potential upside:

- directly exercises the cryptographic path without revealing production data;
- admits explicit false-accept analysis;
- supports invalid-response and equivocation evidence.

Hard gates:

- must not touch production ciphertext or plaintext;
- must have a falsifiable link to current serviceability rather than generic
  uptime;
- must remain framed as a readiness proxy, not a guarantee of future dispute
  success.

Cheapest falsification tests:

- show the same custodian set can pass canaries yet fail targeted disputes under
  selective withholding;
- find prior art with substantially equivalent pre-authorization canary probing.

Current decision:

`RETAIN`. This is the only candidate aligned with the frozen thesis.

## 4. Candidate B: operational telemetry or heartbeat

Mechanism:

- require signed heartbeats, process attestations, latency pings, or infrastructure
  telemetry from custodians.

Potential upside:

- cheap to deploy;
- may detect outages without cryptographic load.

Why it fails the contribution target:

- does not exercise the actual partial-decryption path;
- gives weaker evidence than a cryptographic transcript;
- collapses into ordinary monitoring rather than a claim-safe research
  contribution.

Hard gate failure:

cannot establish current decryption serviceability as required by the problem
specification.

Current decision:

`REJECT`.

## 5. Candidate C: post-authorization live drill

Mechanism:

- periodically authorize a sacrificial record and require actual threshold
  decryption before a deadline.

Potential upside:

- closest direct proxy to the dispute path;
- exposes timing and coordination failures.

Why it is distinct:

- it exercises the real authorization path instead of a non-production canary.

Why it misses the frozen MPP:

- higher operational and confidentiality complexity;
- risks leaking or normalizing release workflows before genuine disputes;
- no clean static false-accept theorem because the test is not a sampled proxy.

Hard gate failure:

does not preserve the clean non-production audit boundary required by the frozen
architecture.

Current decision:

`REJECT FOR MPP`, possible future extension.

## 6. Candidate D: setup-time assurance only

Mechanism:

- trust VSS/PVSS/DKG correctness, registration, and periodic refresh as
  sufficient evidence.

Potential upside:

- minimal runtime complexity.

Why it fails:

- setup correctness is not operational readiness;
- cannot surface current outage, invalid-response, or dispute-deadline failure.

Hard gate failure:

fails to address the actual causal bottleneck between correct setup and current
deadline-bounded decryptability.

Current decision:

`REJECT`.

## 7. Comparative judgment

| Criterion | A | B | C | D |
| --- | --- | --- | --- | --- |
| Exercises current cryptographic serviceability | yes | no | yes | no |
| Preserves pre-authorization confidentiality cleanly | yes | yes | mixed | yes |
| Supports explicit false-accept analysis | yes | weak | no clean proxy theorem | no |
| Fits frozen scope | yes | no | partial | no |
| Most vulnerable objection | selective withholding gap | "just monitoring" | too operational and broad | setup is not readiness |

## 8. Portfolio conclusion

The portfolio does not prove novelty. It only shows that candidate A is the
best-scoped hypothesis to test. The other families either fail the estimand,
fail the frozen confidentiality boundary, or collapse into ordinary monitoring
or setup correctness.

## 9. Residual risks

- Candidate A may still be anticipated by a stronger predecessor not yet found.
- The readiness estimand may end up too narrow if selective withholding dominates
  realistic failures.
- Correlation-aware sampling may improve engineering quality without yielding a
  material research differentiator.

## 10. Resume instruction

Use candidate A only as a narrow property-composition-analysis hypothesis, then
continue novelty closure with patent, standards-adjacent, and citation-chain
search before any claim upgrade.
