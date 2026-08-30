# Research Program Charter

## Identity

- System: KEYSTONE-MPP-F1
- Research topic: KEYSTONE: Auditable Dispute-Key Availability for Encrypted AI Rollups
- Target venue/article type: venue-neutral original full research paper; the dated primary/fallback venue portfolio remains a SUBMISSION_QA decision
- Program owner: root integration owner
- Accountable human decision authority: accountable-human identity and in-scope authority are confirmed in `research-case/00-governance/accountable-authority-confirmation.md`; final author order, corresponding-author designation, affiliation wording, institutional naming, and submission-time institutional authority remain deferred
- Confidentiality class: public research topic with unpublished local working artifacts
- External-processing permission: approved only for public web metadata, official public documents, and public literature queries; unpublished local artifacts and source files must not be uploaded to third parties

## User-asserted starting contract

These items are intake assertions (`E1 ASSERTED`), not verified novelty, feasibility, or evidence.

- Core research question: How can an encrypted AI rollup obtain publicly auditable, non-revealing evidence that at least t valid threshold-decryption contributions are currently serviceable for an authorized dispute before deadline Delta, under explicit churn and correlated-failure assumptions, without releasing a production key or plaintext before authorization?
- Novelty statement: We formalize dispute-key availability as deadline-bounded, authorized reconstructability distinct from ciphertext data availability, and instantiate it with non-revealing canary partial-decryption sampling, explicit false-accept bounds, correlation-aware committee audits, and public deadline evidence.
- Target contribution: A formal DKA property suite; a canonical non-production canary audit with context-bound DLEQ proofs; static and repeated-audit probability analysis with explicit temporal assumptions; failure-domain-aware placement and stratified sampling; a public deadline-accountability interface; and a reproducible threshold-KEM prototype, adversarial simulator, datasets, figures, tests, and bulletin-board contract boundary, without claiming a new cryptographic primitive or production security.
- Possible feasibility: The workspace already contains a reproducible Python threshold-KEM and DLEQ prototype, 17 passing tests, deterministic simulations and datasets, five quantitative figures, eight editable diagrams, a compiling Solidity bulletin-board skeleton with two passing tests and gas snapshots, locked dependencies, and a one-command verification path; remaining constraints are expanded exact and stochastic experiment coverage, fuzz and invariant contract tests, complete performance and deadline measurements, formal proof completion, a distributed testbed, production DKG or PVSS substitution for a full-paper claim, current prior-art and venue verification, independent cryptography and systems review, and accountable human submission approval.
- External or real-world validation requirement: claim matched; external or field claims require V4/V5 evidence, otherwise manuscript language is limited to the analytical, simulated, and internal prototype settings
- Exploratory versus confirmatory analysis boundary: existing frozen runs are baseline/exploratory evidence; the expanded grid, declared thresholds, seeds, uncertainty procedures, and deadline testbed must be frozen before confirmatory execution
- Feasibility-pilot status and authority: the existing prototype is prior internal evidence, not an independently verified feasibility pilot; FEASIBILITY_GATE will decide GO, PILOT_FIRST, REDESIGN, BLOCKED, RESUME, or STOP
- Solution-viability status: ASSERTED ONLY; claim-matched evidence is required
- Acceptance-readiness status: NOT ASSESSABLE; editorial decisions remain external

## Claim ladder

| Claim ID | Exact claim | Type | Required evidence | Current evidence | Stage | Falsifier | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C001 | We formalize dispute-key availability as deadline-bounded, authorized reconstructability distinct from ciphertext data availability, and instantiate it with non-revealing canary partial-decryption sampling, explicit false-accept bounds, correlation-aware committee audits, and public deadline evidence. | novelty hypothesis | strongest-prior-art search plus material differentiator | E1 ASSERTED | UNRESOLVED | a credible predecessor with no material difference | UNASSIGNED |
| C002 | The workspace already contains a reproducible Python threshold-KEM and DLEQ prototype, 17 passing tests, deterministic simulations and datasets, five quantitative figures, eight editable diagrams, a compiling Solidity bulletin-board skeleton with two passing tests and gas snapshots, locked dependencies, and a one-command verification path; remaining constraints are expanded exact and stochastic experiment coverage, fuzz and invariant contract tests, complete performance and deadline measurements, formal proof completion, a distributed testbed, production DKG or PVSS substitution for a full-paper claim, current prior-art and venue verification, independent cryptography and systems review, and accountable human submission approval. | feasibility hypothesis | access, resource, safety, ethics, validity, and pilot evidence | E1 ASSERTED | UNRESOLVED | a blocking feasibility gate | UNASSIGNED |
| C003 | A formal DKA property suite; a canonical non-production canary audit with context-bound DLEQ proofs; static and repeated-audit probability analysis with explicit temporal assumptions; failure-domain-aware placement and stratified sampling; a public deadline-accountability interface; and a reproducible threshold-KEM prototype, adversarial simulator, datasets, figures, tests, and bulletin-board contract boundary, without claiming a new cryptographic primitive or production security. | solution-viability hypothesis | analytic, simulated, prototype, external, or field evidence matched to the exact claim | E1 ASSERTED | UNRESOLVED | failure to meet the prespecified viability threshold or failure envelope | UNASSIGNED |

## Authority, safety, and execution bounds

- Ethics or IRB status: no human or animal participants are planned; institutional and venue-specific confirmation is still required before submission
- Consent status: not applicable to the currently planned synthetic, simulated, and software-prototype study; this disposition requires accountable human confirmation
- Data rights and privacy status: current evidence is locally generated synthetic/simulated/prototype output; no personal, confidential, or production user data is authorized
- Safety, biosafety, security, or dual-use status: cryptographic/distributed-systems security research with bounded dual-use review; no production secrets, live exploitation, or sensitive infrastructure data are authorized
- Legal or regulatory status: no regulated intervention is planned; applicable author-institution, software-license, cryptographic-export, venue, and artifact policies remain to be checked
- Required qualified experts: at least one threshold-cryptography reviewer and one distributed-systems/blockchain reviewer, plus an independent novelty challenge
- AI postdoctoral-standard audit: UNASSESSED; assistive only
- Acceptance guarantee: PROHIBITED; a calibrated forecast is optional when target-matched data and uncertainty exist
- AI substitution for empirical evidence, ethics authority, or accountable authors: PROHIBITED
- Irreversible collection, recruitment, intervention, scraping, procurement, or external sharing: NOT AUTHORIZED

## Resolved working study profile

- Field: applied cryptography, blockchain/distributed systems, and systems security.
- Study type: analytical security model plus reproducible simulation, prototype experiment, smart-contract evaluation, and claim-matched distributed-systems benchmark.
- Article type: original full research paper, initially venue neutral.
- Evidence standard: formal definitions/proofs or bounded proof sketches; exact probability checks; prespecified stochastic experiments with uncertainty; internal prototype and contract evidence; external evidence only for external or field claims.
- Reporting route: current venue author/artifact rules and field-specific reproducibility practices, verified at SUBMISSION_QA.
- Jurisdiction basis: non-human computational research; author institution and selected venue remain the accountable policy authorities.

This profile is a root-owned draft derived from the user's explicit full-paper goal, the frozen repository contract, and the accountable-human authority confirmation. The authority confirmation does not independently verify the scientific classification or claim boundaries, so this profile cannot by itself advance the INTAKE gate.

## Frozen operational claim register

| Claim ID | Frozen contribution | Maximum wording before new evidence |
| --- | --- | --- |
| K-C1 | DKA property suite separates ciphertext availability, share validity, audit readiness, authorized decryptability, deadline liveness, and pre-authorization confidentiality. | Formal definition and counterexample only until novelty survives the strongest-prior-art challenge. |
| K-C2 | Canonical beacon-derived canary partial decryptions with context-bound DLEQ proofs exercise a current share path without using production ciphertext. | Protocol composition and internal prototype claim; not a new cryptographic primitive. |
| K-C3 | Static catastrophic false-accept and detection bounds, plus repeated-audit bounds under stated temporal assumptions. | Analytic/simulated scope only; never unconditional future availability. |
| K-C4 | Failure-domain placement and stratified sampling are evaluated under correlated outages. | Only within the declared domain model and tested parameter range. |
| K-C5 | Public request/deadline records support evidence for invalid responses, equivocation, and conditional deadline misses. | Non-response blame remains conditional on synchrony and delivery assumptions. |
| K-C6 | Reproducible threshold-KEM prototype, simulator, tests, datasets, figures, diagrams, and bulletin-board boundary. | Non-production internal artifact; no production-security claim. |

The typed claim graph will import these operational IDs only after the novelty, feasibility, and evidence ledgers define their required maturity, support, qualifications, refutations, and scope ceilings.
