## Title

KEYSTONE: A Draft Study of Dispute-Key Serviceability Distinct from Ciphertext Availability in Encrypted AI Rollups

Status: `DRAFT / PRE-MANUSCRIPT / PRE-AUTHORIZATION`  
System: `KEYSTONE-MPP-F1`  
Date: `2026-08-29`  
Canonical phase at draft time: `INTAKE`

Draft author and repository public-release authority: **Zubaer Mahmood Zubraj**
([`@zmzubraj`](https://github.com/zmzubraj)). Final publication byline order,
affiliations, CRediT roles, declarations, and submission approval remain open.

## Abstract

Encrypted optimistic AI rollups can preserve ciphertext availability while
still failing to deliver timely dispute-key serviceability. KEYSTONE studies
that separation through a non-production readiness-audit workflow assembled
from established threshold-decryption components rather than a new
cryptographic primitive. The present draft is bounded to three research-case
claims: a property-separation hypothesis (`C001`), an internal prototype and
reproducibility hypothesis (`C002`), and a broader solution-viability hypothesis
that still requires external evidence (`C003`). Existing tests, simulations,
figures, diagrams, and contract-boundary artifacts are internal, analytic,
preliminary, or exploratory evidence only. Novelty remains unresolved,
feasibility is unassessed in canonical state, and confirmatory execution is not
authorized. Accordingly, this shell records admissible wording, planned
sections, and explicit evidence gaps; it does not make a publication-readiness
claim.

## 1. Introduction

The motivating problem is not ciphertext publication alone. A rollup dispute
may require authorized recovery of a record key or threshold-decryption output
within a deadline, and that requirement can fail even when ciphertext bytes or
receipts remain retrievable. The current draft treats that gap as the core
research question.

The manuscript remains within `FREEZE.md`, `docs/11_PAPER_BLUEPRINT.md`, and the
canonical novelty case. It does not claim a new threshold-decryption primitive,
timing-free accountability, adaptive selective-withholding resistance,
unconditional future availability, or production security.

The three manuscript-level claim anchors are:

- `C001`: study and formalize dispute-key availability as distinct from
  ciphertext availability under the frozen model, subject to unresolved
  strongest-prior-art closure;
- `C002`: document the internal, non-production prototype and local
  reproducibility boundary;
- `C003`: test the frozen analytic, simulated, prototype, and eventually
  external evidence package without wording above its current maturity ceiling.

## Methods

The detailed methods architecture is organized across Sections 2–6. Those
sections remain a pre-authorization manuscript view of the canonical novelty,
protocol, analysis-plan, and implementation artifacts.

The feasibility package now includes a non-executable confirmatory pilot plan,
machine-readable result contract, and a result-blind PC03 amendment. They reserve
all nine `RID-*` result families, separate the minimum short-paper core from the
extended deadline lane, prohibit reuse of historical outputs as confirmatory
evidence, and leave all observed outcomes missing. For three minimum synthetic
cells—IID baseline, stratified-versus-uniform at `s=8`, and selective withholding
at `w=11`—the draft amendment predeclares 32 primary and four reserve seed
blocks, 4,096 draws per block, result-blind precision rules, and deterministic
seed schedules. Correlated-domain analysis is
`EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE`; its current plots remain
exploratory only. The distributed deadline family is
`EXCLUDED_PENDING_ENVIRONMENT_PROFILE`. This design-readiness package does not
issue `GO`: it still needs independent methods verification and separate
execution authority.

## 2. Background and Related Work

`PENDING — NOVELTY_UNRESOLVED.` This section will compare KEYSTONE with data
availability sampling, threshold encryption and verifiable partial decryption,
VSS/PVSS and DKG, proactive or dynamic sharing, proof of retrievability,
encrypted execution, threshold KMS, and accountable liveness. The current
novelty matrix rejects broad primitive or first-system novelty. Until the
independent, signed novelty closure exists, only narrow property-separation and
integration language is admissible.

PeerDAS is the relevant contrast class for public or ciphertext-oriented data
availability rather than dispute-key serviceability [@eip7594]. Established
secret-sharing, PVSS, proactive sharing, robust DPSS, threshold-decryption, and
DLEQ-style proof lineage are adopted building blocks rather than claimable
novelty [@shamir1979share; @schoenmakers1999pvss; @herzberg1995proactive;
@yurek2023dpss; @boneh2006threshold; @chaum1992dleq].

The adjacent encrypted-rollup, threshold-release, and authorized-decryption
design space is already populated by encrypted optimistic-execution and
threshold-release systems, including EigenAI, ETHTID, Ferveo, vetKeys,
BEAT-MEV, practical one-time-setup batched threshold encryption, time-lock
encrypted storage, context-dependent threshold decryption, and consensus-
authorized threshold decryption for voting
[@eigenai2026; @stengele2021ethtid; @bebel2022ferveo; @cerulli2023vetkeys;
@bormet2025epochless; @choudhuri2025practical; @agarwal2025ttles;
@boneh2025context; @liu2026uqvote]. Accountability and timing assumptions are
also prior-art surfaces rather than KEYSTONE-owned primitives
[@boneh2023accountability; @lewis2025accountable]. Accordingly, the only
currently admissible contribution language is the narrower distinction between
ciphertext availability and dispute-key serviceability under the frozen model,
plus the claim-bounded audit and analysis surfaces that still require
independent review.

## 3. Model and Definitions

The pre-authorization formal source defines ciphertext availability, valid-share
registration, audit-time readiness, authorized decryptability, deadline
liveness, pre-authorization confidentiality, and conditional dispute-key
availability. Three constructive obligations are currently preserved: (i)
ciphertext availability does not imply deadline-bounded dispute-key
availability when only `t-1` record contributions are serviceable; (ii) a
routine audit may pass while a target-aware selective withholder prevents an
authorized dispute from reaching `t` contributions; and (iii) a finite audit
prefix cannot guarantee unconditional future availability without temporal
assumptions. These are draft logical non-implication witnesses, not prevalence,
novelty, or production-security results. The paper does not claim a complete
pairwise property lattice, and all three obligations remain subject to formal
and novelty review.

## 4. KEYSTONE Protocol

The authoritative pre-authorization protocol is
`research-case/03-design/protocol.md`. The manuscript-facing protocol will
cover epoch setup, record KEM/DEM handling, beacon-derived canary challenges,
context-bound partial decryptions and proofs, audit verification, authorized
dispute release, evidence records, recovery, and domain-aware placement.

The current local package contains deterministic transcript and signature
fixtures that exercise audit-request and partial-response interfaces. These are
interoperability fixtures, not empirical evidence or proof of production
security. The current local audit API accepts beacon and context inputs and
derives the canary challenge internally, removing the direct caller-supplied
group-element path from routine audit execution. This is a pre-authorization
prototype boundary, not a formal non-substitution proof or production-security
claim, and it still requires independent cryptographic review.
The current draft treats threshold decryption, DLEQ-style verification, and
hash-to-curve usage as adopted components rather than new cryptographic claims
[@boneh2006threshold; @chaum1992dleq; @rfc9380; @boneh2025context].

## 5. Analysis

The current analysis surface includes a static catastrophic-state
hypergeometric calculation and internal simulation models for IID,
correlated-domain, stratified-sampling, and selective-withholding scenarios.
Any static probability statement must be qualified as one-audit reasoning under
the declared fixed-ready-set and sampling assumptions. Repeated-audit and
deadline claims require explicit temporal and synchrony assumptions.

Current boundaries are mandatory:

- temporal Markov outputs are exploratory only;
- selective withholding is a negative finding and limitation;
- deadline success remains blocked pending an accountable environment profile,
  synchronized trace design, and authorized distributed benchmark;
- no analysis statement may exceed the claim ceilings encoded in the canonical
  research case.

## 6. Implementation

The workspace contains a Python threshold-KEM/DLEQ prototype, deterministic
fixtures, local experiment scripts, and a Solidity bulletin-board boundary.
Local cryptographic timings and contract test-body gas measurements are
implementation artifacts only. They do not establish production throughput,
deployment cost, audited cryptographic security, or independent
reproducibility.

Two fail-closed pre-authorization engineering receipts currently bind local
source/configuration hashes to observed test outcomes. The crypto receipt maps
22 pytest nodes and two vector-freshness checks; the contract receipt maps 27
Foundry cases, including 14 deterministic boundary tests, three fuzz
properties, eight test-body gas operations, and two stateful invariants. All
mapped cases passed in the current same-workspace runs. The receipts explicitly
remain non-empirical, non-independent engineering QA; they are not canonical
scientific results, cryptographic or smart-contract audits, or production
validation. An editable pre-authorization QA coverage table is generated from
the two receipts and their hash sidecars at
`paper/tables/preauthorization_engineering_qa.csv` for paper drafting, but it
is not a canonical T-series result table and cannot be used to promote any
scientific claim or raise the maturity or supported scope of `C002`.

Production DKG/PVSS, audited cryptographic libraries, distributed deployment,
and independently controlled reproduction remain outside the current internal
prototype boundary.

### 6.1 Draft protocol and method display map

The following diagram callouts bind the current editable sources and rendered
derivatives to their intended manuscript roles. They communicate definitions,
protocol structure, methods, and limitations; they are not result evidence and
do not raise the maturity of `C001`, `C002`, or `C003`. Final placement remains
subject to the target venue, final-size review, and accountable-human approval.

![D1. System architecture separating ciphertext publication, policy coordination, readiness auditing, authorized release, threshold combination, private re-execution, and the dispute verdict.](diagrams/01_system_architecture.png)

**D1 — System architecture.** Ciphertext availability, routine canary auditing,
and authorized dispute-key release are shown as separate paths. The diagram is
a protocol map for `C002`/`C003`, not evidence that each path is externally
available or production-secure.

![D2. Three constructive property-separation witnesses, each routing a held condition and a failed condition to one bounded non-implication.](diagrams/02_property_separation.png)

**D2 — Constructive property separation.** Exactly three witnesses support the
draft analytic obligations in `C001`: ciphertext availability does not imply
deadline-bounded DKA; routine audit acceptance does not unconditionally imply
targeted dispute success; and a finite audit prefix does not guarantee future
DKA. This is not a complete pairwise property lattice.

![D3. Eight-step readiness-audit sequence from committed epoch data and beacon sampling through canary proof verification and evidence emission.](diagrams/03_audit_sequence.png)

**D3 — Readiness-audit sequence.** The routine path uses fresh, context-bound
canaries and classifies valid, invalid, and missing responses at the declared
deadline. It does not exercise production ciphertext.

![D4. Eight-step authorized-dispute sequence from challenge validation through confidential partial release, threshold combination, re-execution, and verdict.](diagrams/04_dispute_sequence.png)

**D4 — Authorized dispute sequence.** The diagram records the intended policy
and threshold-release ordering; it does not establish deployed confidential
transport, deadline success, or production authorization.

![D5. Epoch, audit, and dispute state machines with explicit successful, failed, expired, and retired terminal paths.](diagrams/05_state_machines.png)

**D5 — State machines.** Allowed transitions make terminal and failure paths
explicit for implementation review. The current contract is still a
non-production boundary with admin-adjudicated off-chain proof outcomes.

![D6. Six adversary or fault classes mapped through KEYSTONE controls to six residual assumptions or risks.](diagrams/06_threat_model.png)

**D6 — Threat model and residual risk.** Each control is paired with a residual
assumption. In particular, domain labels may be dishonest, audits do not prove
future cooperation, and the pre-authorization collusion threshold remains an
assumption rather than an observed result.

![D7. Four fault domains with one offline domain and contrasting uniform versus domain-stratified sample routes.](diagrams/07_sampling_domains.png)

**D7 — Sampling and failure domains.** This is a method illustration under
truthful domain labels. It does not claim universal superiority of
stratification or field prevalence of the illustrated outage.

![D8. Reproducibility pipeline from frozen configuration through tests, simulation, data products, figures, claim mapping, manuscript assembly, and publication gates.](diagrams/08_experiment_pipeline.png)

**D8 — Experiment-to-manuscript pipeline.** The flow separates configuration,
execution, versioned outputs, displays, claim binding, and review gates. A clean
local pipeline does not substitute for authorized confirmatory analysis,
independent reproduction, or human submission approval.

## Results

The present results surface is an explicitly preliminary inventory. It does not
replace missing authorized `05-analysis` evidence or the still-missing canonical
primary-results ledger.

The temporary Markdown/LaTeX preliminary-table bundle has a fail-closed
same-workspace lineage receipt that binds its five input files, exporter,
selected fields and row identities, section mapping, and both outputs. This
improves draft reproducibility only; it is not a canonical T-series result,
scientific verification, or independent reproduction.

A second-agent, same-host isolated-copy mechanical rerun subsequently executed
the frozen ten-command package check under tool-level offline flags. The first
fresh attempt failed closed when Foundry rejected a non-boolean offline setting;
its hash-bound failure receipt and logs were preserved. After the environment
contract was corrected and independently re-reviewed, a new operator completed
all ten commands with zero return codes, unchanged source and isolated-copy
inventories, and a valid `MECHANICAL_PASS` receipt. This establishes bounded
same-host mechanical replay only: it used the same machine and potentially the
same tool caches, did not enforce network isolation at the kernel level, did not
execute the distributed deadline study, and is neither external reproduction
nor independent scientific verification, institutional approval, venue
approval, or evidence that changes the current claim-maturity ceilings.

## 7. Evaluation

Only a limited set of result classes is admissible for drafting:

- analytic static catastrophic false-accept and detection calculations;
- deterministic correctness and interoperability fixtures;
- internal preliminary IID, correlated-domain, stratified-sampling, and
  selective-withholding simulation outputs;
- internal local cryptographic timings and contract test-body gas measurements.

The current figures F1–F5 and `paper/tables/t1_t8_package.*` are draft
preauthorization display assets. They are not canonical confirmatory tables or
publication evidence. Missing or blocked evaluation outputs include the
canonical `05-analysis` primary ledger, authorized confirmatory robustness and
negative-result analyses, deadline Figures F6–F7, the planned recovery-timeline
Figure F8, independent reproduction, and external validation for `C003`. The canonical
`05-analysis/results/exploratory-findings.csv` now records the four temporal
Markov rows under distinct `EXPLORE-*` identifiers. It preserves the simulated
source maturity but caps claim support at `V0 ASSERTED`: each row is explicitly
post-hoc, preauthorization-only, unauthorized, non-independent, and descriptive
rather than confirmatory. Its conditional denominator is the number of trials
ending in the catastrophic state, not all simulated trials. Draft `04-data`
provenance and evidence-status ledgers hash-bind the source inputs; the deadline
result remains explicitly `BLOCKED` with no executed provenance row. These
ledgers improve traceability only and do not activate scientific support edges
or advance the canonical `INTAKE` phase.

The canonical draft `05-analysis/results/negative-findings.csv` now records
only the interval-separated selective-withholding gap already present in the
frozen simulation (`NEG-SW-11` through `NEG-SW-14`). Each row remains a
preauthorization simulated negative finding, unauthorized, non-independent,
and capped at `V0 ASSERTED`. This closes a traceability gap but is not an
authorized confirmatory result and does not provide deadline, production,
external, field, adaptive-adversary, or universal-security evidence.

The canonical draft `05-analysis/results/robustness-and-boundaries.csv` now
preserves all 17 frozen IID outage cells and all 12 frozen matched-seed sampling
policy cells as a deterministic traceability ledger. Every row is explicitly
`DRAFT_ROBUSTNESS_BOUNDARY_ONLY`, preauthorization, simulated, unauthorized,
non-independent, and capped at `V0 ASSERTED`. Correlated-domain output is
excluded because its current result-ID binding is entangled with the quarantined
Markov asset; Markov, selective-withholding, and deadline rows are also excluded
from this ledger. The file therefore does not establish confirmatory robustness,
policy optimality, production behavior, deadline performance, generality, or
external validity.

The future confirmatory outputs are predeclared in
`02-feasibility/pilot-run-contract.csv`. The minimum core comprises the
separation witness, exact static result, deterministic crypto and contract
boundaries, and the limitation-bearing selective-withholding family. IID and
stratification are supporting qualification families; correlated-domain
analysis is excluded pending a truthful domain-label source. The included draft
counts and stream schedule are recorded in
`03-design/pc03-prospective-counts.csv` and
`03-design/pc03-seed-schedule.csv`; these are design inputs, not results. The
distributed deadline result remains an extended full-paper family and must be
excluded, rather than imputed, if its environment and precision gates remain
open.

### 7.1 Preliminary quantitative display map

The five available quantitative figures are included below only to freeze their
drafting roles and captions. Their source data, generator, SVG/PNG hashes, and
automated visual-QA status are recorded in the source and figure manifests.
They remain preliminary and must be replaced or re-authorized from canonical
analysis ledgers before submission.

![F1. Static one-audit detection bound under uniform sampling as the sample size changes.](prototype/results/figures/figure_1_theoretical_detection_bound.png)

**F1 — Static detection bound.** Analytic one-audit probability under the
declared fixed catastrophic state and uniform-sampling assumptions; not a
temporal availability or field-frequency result.

![F2. Internal IID outage sweep showing reconstruction and audit-pass estimates with Wilson intervals.](prototype/results/figures/figure_2_iid_failure_sweep.png)

**F2 — IID failure sweep.** Internal preliminary simulation with the configured
scenario grid and uncertainty calculation; not confirmatory or externally
validated evidence.

![F3. Internal correlated-domain outage sweep under declared truthful domain labels.](prototype/results/figures/figure_3_domain_diversity.png)

**F3 — Correlated-domain behavior.** Internal model-bounded simulation; domain
identity correctness and real outage structure remain unverified assumptions.

![F4. Selective-withholding negative-result figure showing that routine audit acceptance can coexist with failed targeted dispute reconstruction.](prototype/results/figures/figure_4_selective_withholding_gap.png)

**F4 — Selective-withholding limitation.** Preserved negative result that blocks
an unconditional audit-to-dispute-success inference.

![F5. Matched internal comparison of uniform and domain-stratified sampling under the configured conditioned catastrophic states.](prototype/results/figures/figure_5_sampling_strategy.png)

**F5 — Sampling-strategy comparison.** A matched, model-specific internal
comparison. It does not establish universal dominance, external validity, or
production benefit.

### 7.2 Draft evidence-bound table map

The editable T1–T8 package is now available in `paper/tables/t1_t8_package.md`
and `paper/tables/t1_t8_package.tex`. Every table remains draft /
pre-authorization only and inherits the canonical ceiling of the underlying
claim or evidence source.

- `T1` bounds the strongest-prior-art matrix and does not clear novelty.
- `T2` is a design-comparator registry only and makes no measured-superiority claim.
- `T3` records frozen local conditions and the still-missing `RID-C003-DEADLINE-001` distributed profile.
- `T4` displays preauthorization simulated results parsed from canonical JSON outputs only, capped at `V0 ASSERTED` for manuscript claims.
- `T5` is a planned mechanism-isolation registry; every row remains `MISSING_NOT_EXECUTED`.
- `T6` presents the canonical robustness ledger plus separately classified exact and exploratory temporal checks; selective-withholding negative findings remain in `T8`.
- `T7` limits feasibility evidence to local timings and Foundry gas while leaving distributed, operator, network, and external rows blocked.
- `T8` preserves selective withholding, synchrony limits, truthful-domain-label dependency, and missing external validation as explicit negative or unresolved findings.

## 8. Discussion

The current safe interpretation is that ciphertext availability and
dispute-key serviceability should not be treated as interchangeable; routine
readiness audits may characterize present serviceability only under stated
assumptions; failure-domain modeling and sampling semantics affect the meaning
of reported probabilities; and local prototype success does not establish
external reproducibility, field readiness, or production security.

Stronger interpretation must await reconciled prior art, authorized analysis,
and claim-matched independent evidence.

## 9. Limitations and Future Work

- Novelty remains `UNRESOLVED`; the broad historical claim is not
  submission-safe.
- The canonical feasibility decision remains `UNASSESSED`; the draft
  feasibility package recommends a blocked posture and only a conditional
  `PILOT_FIRST` path after prerequisites clear.
- Current stochastic outputs are internal and mostly pre-authorization.
- Temporal dependence is exploratory; selective withholding is a preserved
  negative result.
- The distributed deadline benchmark and independent external validation are
  absent.
- Independent threshold-cryptography and distributed-systems reviews are
  absent.
- No venue portfolio, current reporting checklist, hermetic PDF package,
  rendered-page review, or accountable human approval exists.

## 10. Conclusion

`PENDING — EVIDENCE-BOUND SYNTHESIS.` The conclusion may restate the distinction
between ciphertext availability and dispute-key serviceability and the
conditional nature of any audit assurance. It must not imply future-proof
availability, external validity, production readiness, or publication readiness
unless the corresponding canonical gates later pass.

## Data and Code Availability

Current local source assets include `prototype/src/keystone/*`,
`prototype/tests/*`, `prototype/results/*`, `contracts/src/*`,
`contracts/test/*`, `contracts/gas_report.csv`, `paper/test_vectors.json`,
`paper/signature_test_vectors.json`, `diagrams/*`, and the two
`*/results/engineering_qa/*-preauth-receipt.json` bundles. Availability does
not imply evidence authorization or final reproducibility. The manuscript
assembly inventory is tracked in `07-manuscript/source-manifest.json`.
Draft source-to-result lineage is recorded in `04-data/provenance-manifest.csv`
and `04-data/evidence-status.csv`; those files retain the preauthorization and
same-workspace limitations of their inputs. The derived temporal ledger at
`05-analysis/results/exploratory-findings.csv` is reproducible from the
hash-bound Markov dataset through `scripts/export_exploratory_findings.py`, but
is quarantined from confirmatory, novelty, feasibility, and external-validation
claims.
The derived robustness ledger at
`05-analysis/results/robustness-and-boundaries.csv` is reproducible from the
hash-bound IID and sampling-policy datasets through
`scripts/export_robustness_boundaries.py`; it remains a draft traceability
surface and cannot substitute for the missing primary ledger, authorized
confirmatory analysis, independent reproduction, or external validation.
The non-executable future-run contract is recorded in
`02-feasibility/pilot-plan.md` and `02-feasibility/pilot-run-contract.csv`; it
contains no collected outcome and grants no authorization. The PC03 amendment,
count contract, and seed schedule under `03-design/` are likewise result-blind,
non-executable planning artifacts pending independent methods verification.

## Declarations and Pending Human Inputs

Draft author metadata inputs have been supplied for prospective authors, and
the accountable human reported no institution, employer, funding agreement,
NDA, venue policy, or export-control conflict with the current charter or
study profile. At the author's request, final author order,
corresponding-author designation, accountable metadata freeze, and exact
affiliation wording remain deferred.
Funding, conflicts of interest, CRediT roles, data/code release terms, AI-use
disclosure, and venue-specific institutional checks also remain pending. No
AI-generated text in this shell constitutes author approval or submission
authorization.
