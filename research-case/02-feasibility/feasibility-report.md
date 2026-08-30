# KEYSTONE feasibility and start-alignment report

System: `KEYSTONE-MPP-F1`
Status: `DRAFT / PRE-GATE`
Assessment date: `2026-08-29`
Evidence cutoff: local unpublished workspace artifacts dated through `2026-08-29`
Current canonical phase: `INTAKE`
Named next phase under review: draft `FEASIBILITY_GATE` package for eventual
`STUDY_DESIGN` preparation
Access limits: local workspace only; no new web research; no unpublished local
artifacts uploaded externally
Decision authority: `human_approval` for accountable human authority plus
`intake_integration` for canonical phase transitions
Explicit assumptions: the frozen non-human computational framing in the charter
and study profile is directly confirmed for the current draft-design package by
`research-case/00-governance/accountable-authority-confirmation.md`, while
final author order, corresponding-author identity, affiliation wording,
institutional endorsement, external sharing, submission, and scientific
verification remain separately gated
Skills used: `research-feasibility-gate`

Artifact lifecycle note: these five `research-case/02-feasibility/*` artifacts
are registry-recorded as schema-v4 `DRAFT` in `research-case/artifact-registry.csv`.
The row-level statuses in this report and in
`research-case/02-feasibility/risk-register.csv` such as `VERIFIED`,
`BLOCKED`, and `AT RISK` describe item-level substantive evidence states only.
They do not mean the artifacts are independently scientifically verified, and
no root or mechanical owner including `intake_integration` may self-certify
scientific evidence.

## Decision

- Outcome: `BLOCKED`
- Phase-specific wording: responsible progression remains `BLOCKED` at the
  current `INTAKE` state; do not authorize canonical advancement to
  `FEASIBILITY_GATE` or `STUDY_DESIGN`
- Lowest defensible rationale: two fatal prerequisites are still open:
  unresolved narrow novelty after the bounded prior-art closure, and an
  unfinished result-blind design freeze for the prospective deadline pilot
- Confidence and evidence limits: confidence is moderate for the blocker
  diagnosis because `research-case/01-novelty/novelty_reconciliation.md`,
  `research-case/00-governance/program-charter.md`,
  `research-case/00-governance/study-profile.json`, `VERIFICATION.md`, and
  `docs/14_PUBLICATION_SUCCESS_GATES.md` all agree on the same open
  dependencies; confidence is low for any stronger feasibility verdict because
  no result-blind confirmatory design or independent review bundle exists yet
- Excellence outlook: `NOT CREDIBLE YET`
- Conditions and minimum evidence for reconsideration:
  1. preserve the `2026-08-29` accountable-human draft-authority confirmation
     and no-conflict policy basis while keeping final metadata, institutional
     endorsement, external sharing, submission, and scientific verification
     separately gated;
  2. preserve the broad novelty rejection and either close or defeat the narrow
     `REFRAME` claim safely;
  3. freeze a result-blind confirmatory design before rerunning evidence,
     including the environment profile, deadline interpretation, trace
     denominator, precision target, and multiplicity rule for
     `RID-C003-DEADLINE-001`.

If those blockers clear, the recommended next evidence step is `PILOT_FIRST`,
not `GO`. The pilot scope should resolve the still-open full-paper
uncertainties:

- distributed deadline behavior under declared synchrony assumptions;
- formal proof completion or claim narrowing plus independent cryptography
  review;
- independent clean-machine reproduction;
- independent distributed-systems or blockchain review.

## Critical gates

| ID | Gate | Criticality | Current status | Evidence grade | Consequence if open | Minimum resolution |
| --- | --- | --- | --- | --- | --- | --- |
| `G-01` | draft design authority and no-conflict policy basis for the current package | `CRITICAL` | `VERIFIED` | `E3 DIRECT` | the draft package may be maintained inside `INTAKE`, but final author order, corresponding author, affiliation wording, institutional endorsement, execution, external sharing, submission, and scientific verification remain separately gated | preserve `research-case/00-governance/accountable-authority-confirmation.md` and keep non-design authorities deferred |
| `G-02` | narrow novelty survival after bounded search closure | `FATAL` | `BLOCKED` | `E3 DIRECT` | any broader feasibility or manuscript wording risks overclaim | independent novelty verification after remaining closure work |
| `G-03` | result-blind confirmatory design freeze | `CRITICAL` | `BLOCKED` | `E3 DIRECT` | current favorable results could contaminate later thresholds | freeze protocol, analysis plan, and progression rules before rerun |
| `G-04` | distributed deadline evidence for conditional liveness | `CRITICAL` | `AT RISK` | `E1 ASSERTED` | deadline-accountability language cannot exceed toy local scope | bounded synthetic distributed benchmark with preserved traces |
| `G-05` | formal proof completion and independent cryptography review | `CRITICAL` | `AT RISK` | `E2 INDIRECT` | theorem-level wording may exceed actual proof support | proof obligation ledger plus reviewer memo or narrowed claim |
| `G-06` | independent reproduction and systems review | `CRITICAL` | `AT RISK` | `E2 INDIRECT` | internal evidence remains unchallenged and fragile | clean-machine rerun plus external systems review |

## Evidence

### Owner routing and responsibility map

Canonical registered cells used in this package:

| Responsibility | Canonical cell ID | Why it is the auditable owner here |
| --- | --- | --- |
| solution-viability boundary and evidence ladder | `solution_viability` | owns `research-case/02-feasibility/solution-viability-case.md` and `research-case/02-feasibility/evidence-maturity-ladder.csv` |
| feasibility report and progression logic | `feasibility_science` | owns `research-case/02-feasibility/feasibility-report.md` and `research-case/02-feasibility/progression-criteria.csv` |
| feasibility risk register | `feasibility_risk` | owns `research-case/02-feasibility/risk-register.csv` |
| result-blind study-design freeze | `methods_design` | canonical write owner for `research-case/03-design/protocol.md`, `research-case/03-design/analysis-plan.md`, and `research-case/03-design/preregistration-and-deviations.md` |
| power or precision challenge | `power_challenge` | canonical owner for `research-case/03-design/power-or-precision.md` |
| authorized evidence execution | `authorized_execution` | canonical write owner for `research-case/04-data/*` |
| confirmatory correlated-failure analysis | `confirmatory_analysis` | canonical analysis owner for confirmatory results and boundary tables |
| independent reproduction artifact | `reproducibility_challenge` | canonical review owner for `research-case/05-analysis/reproducibility-report.md` |
| novelty integration | `novelty_synthesis` | canonical novelty integration owner for `research-case/01-novelty/novelty-matrix.csv` and `research-case/01-novelty/candidate-portfolio.md` |

Human or external responsibilities not represented by a dedicated registry cell:

| Responsibility | Coordination owner | External or human dependency | Constraint |
| --- | --- | --- | --- |
| accountable authority, authorship, and policy-basis confirmation | `human_approval` | accountable human author and any required institution or venue authority | human-only authority is required; no root or mechanical owner may replace it |
| independent threshold-cryptography review | `human_approval` coordinating evidence acquisition; `methods_design` consumes the result | external threshold-cryptography reviewer | no registered cell can self-verify this scientific review |
| independent distributed-systems or contract-security review | `human_approval` coordinating evidence acquisition; `authorized_execution` or later validation cells consume the result | external distributed-systems, blockchain, or security reviewer | no registered cell can self-verify this scientific review |

This mapping resolves the earlier ambiguous prose labels:

- `protocol_owner` maps to `solution_viability` for current
  feasibility-boundary maintenance.
- `crypto_review_owner` maps to `human_approval` for the external review
  dependency, with `methods_design` consuming the resulting evidence later.

### Contribution and claim ladder

- Problem and affected stakeholder: encrypted rollup challengers, users,
  committee operators, adjudicators, and reviewers need evidence that a dispute
  can still gather `t` valid decryption contributions before deadline without
  revealing production secrets before authorization.
- Decision the evidence should change: whether the project can responsibly move
  from an exploratory MPP package into a frozen confirmatory study-design and
  then a bounded pilot for stronger full-paper claims.
- Question or falsifiable hypothesis: can a non-production canary
  partial-decryption audit provide public evidence about present dispute-key
  serviceability that is distinct from ciphertext availability and static share
  validity, while preserving explicit limits for correlated failure and
  selective withholding?
- Proposed advance in one sentence: KEYSTONE narrows its contribution to a
  dispute-specific serviceability property plus a non-production readiness probe
  with explicit false-accept analysis, correlated-failure qualification, and
  conditional deadline evidence.
- Useful negative result: a canary audit can pass while a targeted dispute still
  fails under selective withholding.
- Narrower worthwhile redesign: if deadline or novelty support collapses, reduce
  the contribution to a property-separation plus internal readiness-measurement
  artifact without broader accountability or deployment claims.

| Planned claim | Minimum adequate evidence | Planned evidence | Current support | Remaining gap |
| --- | --- | --- | --- | --- |
| `C001` narrow novelty claim | strongest-predecessor closure plus explicit material differentiator | `research-case/01-novelty/novelty_reconciliation.md`, `research-case/01-novelty/independent-search-challenge.md`, and independent novelty verification | broad claim rejected; narrow `REFRAME` remains unresolved | patent or standards closure, citation-chain closure, and signed verification |
| `C002` feasibility claim | verified access, reproducibility, resource sufficiency, and bounded risks for the next phase | `research-case/00-governance/program-charter.md`, `research-case/00-governance/study-profile.json`, `research-case/00-governance/accountable-authority-confirmation.md`, `VERIFICATION.md`, and this draft package | local resources, same-workspace reproduction, and accountable-human draft-design authority are present | result-blind design completion, independent reproduction, external review, and separately gated final metadata or submission authority |
| `C003` solution-viability claim | claim-matched analytical, simulation, prototype, and external challenge evidence | `paper/theorem_roadmap.md`, `prototype/README.md`, `VERIFICATION.md`, `contracts/README.md`, and this pilot-first evidence plan | internal analytical and prototype evidence only | distributed deadline pilot, proof closure or narrowing, external review, and confirmatory rerun |

### Problem and prior-art evidence

Problem truth is plausible but not yet fully externalized in a fresh literature
or deployment-burden synthesis. Local problem-spec artifacts do show a coherent
root-cause story: ciphertext availability, setup validity, and present
dispute-time serviceability can diverge.

The novelty package provides the decisive prior-art evidence for this report:

- broad novelty is not defensible;
- the only live candidate is the narrow `REFRAME` claim;
- no single recovered predecessor collapses every narrow element at once, but
  the search is still incomplete enough that novelty remains `UNRESOLVED`.

### Current direct internal evidence

Current local evidence is planning-useful but not confirmatory:

- Python prototype: `VERIFICATION.md` records 35 passed tests, and
  `prototype/README.md` defines the current research-only implementation scope;
- Solidity boundary: `VERIFICATION.md` records 19 Foundry tests plus fuzz and
  invariant coverage, while `contracts/README.md` keeps the contract boundary
  research-only;
- analytical and simulation bundle: `VERIFICATION.md`,
  `prototype/results/exact_stratified_validation.csv`,
  `prototype/results/selective_withholding.csv`, and
  `prototype/results/markov_temporal_dependence.csv` show the current local
  analytical and exploratory evidence surfaces;
- figures, tables, vectors, and manifests exist and are reproducible inside the
  same workspace under `prototype/results/*`, `paper/tables/*`,
  `paper/test_vectors.json`, and `paper/signature_test_vectors.json`;
- `docs/14_PUBLICATION_SUCCESS_GATES.md` already marks distributed
  measurements, independent review, and external confirmation as still open.

### Feasibility ledger

| ID | Question | Criticality | Status | Evidence grade | Evidence or source | Owner | Dependency or deadline | Consequence | Verification action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `FQ-01` | Is the central question precise, bounded, and falsifiable? | `CRITICAL` | `VERIFIED` | `E3 DIRECT` | `FREEZE.md`; `research-case/00-governance/program-charter.md`; `research-case/01-novelty/problem-investigation.md` | `intake_integration` | now | without this the package cannot be claim-safe | preserve frozen wording and falsifier in the design package |
| `FQ-02` | Does the proposal target a real root-cause gap rather than a proxy? | `CRITICAL` | `PLAUSIBLE` | `E2 INDIRECT` | `research-case/01-novelty/problem-investigation.md`; `research-case/01-novelty/candidate-portfolio.md` | `intake_integration` | before study design freeze | if false, the work collapses into monitoring or setup-only assurance | require explicit counterexample class and reviewer challenge |
| `FQ-03` | Is strongest-prior-art novelty resolved enough to support broader wording? | `FATAL` | `BLOCKED` | `E3 DIRECT` | `research-case/01-novelty/novelty_reconciliation.md`; `research-case/01-novelty/independent-search-challenge.md`; `research-case/01-novelty/primary-search/strongest_predecessor_matrix.md` | `novelty_synthesis` | before any phase promotion | overclaim risk invalidates feasibility framing | complete remaining novelty closure and independent verification |
| `FQ-04` | Are authority, field, and study-profile determinations verified for the named next phase? | `CRITICAL` | `VERIFIED` | `E3 DIRECT` | `research-case/00-governance/program-charter.md`; `research-case/00-governance/study-profile.json`; `research-case/program-state.json`; `research-case/00-governance/accountable-authority-confirmation.md` | `human_approval` | now for the draft-design package; before any broader approval change, preserve the same boundary | draft design work may continue inside `INTAKE`, but final metadata, institutional endorsement, external sharing, submission, and scientific verification remain separately gated | preserve the direct accountable-human confirmation and no-conflict policy basis without treating them as execution or submission approval |
| `FQ-05` | Can the current design test the narrow internal MPP claim at all? | `CRITICAL` | `PLAUSIBLE` | `E3 DIRECT` | `prototype/README.md`; `paper/theorem_roadmap.md`; `VERIFICATION.md` | `methods_design` | before confirmatory freeze | if false, current artifact is only a code demo | bind each claim to exact analyses and non-claims |
| `FQ-06` | Are confirmatory thresholds frozen independently of the observed results? | `CRITICAL` | `BLOCKED` | `E3 DIRECT` | `WORKSPACE.md`; `docs/superpowers/plans/keystone_mpp_goal_plan.md`; `docs/19_MPP_TO_PUBLISHABLE_PAPER_PLAN_BN.md` | `methods_design` | before rerun | result leakage would compromise the next phase | freeze protocol, progression criteria, and stop rules first |
| `FQ-07` | Are local compute, code, and reproducibility resources available for bounded next-step work? | `CRITICAL` | `VERIFIED` | `E3 DIRECT` | `VERIFICATION.md`; `WORKSPACE.md` | `authorized_execution` | current | if false, even a pilot cannot start | maintain authoritative inputs and manifests |
| `FQ-08` | Is representative distributed deadline infrastructure already evidenced? | `CRITICAL` | `AT RISK` | `E1 ASSERTED` | `docs/19_MPP_TO_PUBLISHABLE_PAPER_PLAN_BN.md`; `docs/14_PUBLICATION_SUCCESS_GATES.md`; `VERIFICATION.md` | `authorized_execution` | after blocker clearance | deadline claims remain weaker than the intended full-paper path | run a bounded synthetic distributed benchmark |
| `FQ-09` | Is independent reproduction scheduled and feasible? | `CRITICAL` | `AT RISK` | `E2 INDIRECT` | `VERIFICATION.md`; `docs/14_PUBLICATION_SUCCESS_GATES.md`; `WORKSPACE.md` | `reproducibility_challenge` | before stronger wording | evidence remains same-workspace only | plan and execute clean-machine rerun |
| `FQ-10` | Are ethics, data-rights, and privacy boundaries safe for the current scope? | `CRITICAL` | `PLAUSIBLE` | `E2 INDIRECT` | `research-case/00-governance/program-charter.md`; `research-case/00-governance/study-profile.json` | `human_approval` | before submission or external sharing | institutional mismatch could reopen scope or approvals | verify against chosen institution and venue |
| `FQ-11` | Are qualified cryptography and systems reviewers available? | `CRITICAL` | `AT RISK` | `E1 ASSERTED` | `research-case/00-governance/program-charter.md`; `docs/14_PUBLICATION_SUCCESS_GATES.md` | `human_approval` | before full-paper claims | high-risk claims remain unchallenged | secure one crypto reviewer and one systems reviewer |
| `FQ-12` | Is there a useful negative result if stronger claims fail? | `EXCELLENCE` | `VERIFIED` | `E3 DIRECT` | `VERIFICATION.md`; `prototype/results/selective_withholding.csv`; `prototype/results/figures/figure_4_selective_withholding_gap.svg`; `paper/claims.md` | `solution_viability` | preserved now | without this the project becomes success-biased | keep the counterexample as a required artifact |

### Killer-question ledger

| ID | Killer question | Overlay | Criticality | Status | Evidence grade | Strongest fair objection | Smallest adequate test or action | Residual boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `KQ-01` | Who experiences the problem, and which decision changes? | systems, security, protocols | `CRITICAL` | `PLAUSIBLE` | `E2 INDIRECT` | the problem may be real but still too narrow for a publishable contribution | tie the decision target to one explicit stakeholder decision in the design package | do not claim broader impact yet |
| `KQ-02` | What are the strongest close predecessors? | universal novelty | `CRITICAL` | `BLOCKED` | `E3 DIRECT` | the work may still be an obvious composition of known pieces | finish the remaining novelty closure and independent verification | broad novelty stays rejected |
| `KQ-03` | Would a competent practitioner call this routine integration? | universal novelty | `CRITICAL` | `AT RISK` | `E2 INDIRECT` | the surviving slice may still be only careful engineering | require a decision-changing correlated or serviceability distinction, not mere assembly | primitive-level novelty remains prohibited |
| `KQ-04` | What observation falsifies the central claim? | universal falsifiability | `FATAL` | `VERIFIED` | `E3 DIRECT` | falsifier language may exist but not be enforced operationally | carry the falsifier into the confirmatory design and stop rules | if falsified, use `REDESIGN` or `STOP` |
| `KQ-05` | Can the design actually identify the headline claim? | universal design | `FATAL` | `PLAUSIBLE` | `E3 DIRECT` | current evidence may only show a working prototype, not the named property | map each claim to exact theorem, simulation, or pilot evidence before rerun | unresolved until design freeze |
| `KQ-06` | Are the strongest alternatives compared fairly? | systems, security, protocols | `CRITICAL` | `AT RISK` | `E2 INDIRECT` | current comparisons may still be too prototype-centric | freeze fair baselines in the study design | no broader comparative claim yet |
| `KQ-07` | Are authorization, policy, and ethics closed for the named phase? | universal realism | `CRITICAL` | `PLAUSIBLE` | `E3 DIRECT` | the draft-design package has direct accountable-human confirmation, but venue, institution, external sharing, and submission authorities are still narrower or deferred | preserve the current authority confirmation and keep later approvals explicit | no canonical gate advancement beyond the current draft-design boundary |
| `KQ-08` | Can a clean environment reproduce the evidence, and is independent challenge planned? | universal realism | `CRITICAL` | `AT RISK` | `E2 INDIRECT` | same-workspace reproducibility is not enough for a stronger claim | perform clean-machine rerun and external reviews | evidence remains internal until then |
| `KQ-09` | Would a useful negative result remain decision-relevant? | universal design | `CRITICAL` | `VERIFIED` | `E3 DIRECT` | negative results could be hidden if manuscript pressure rises | preserve selective-withholding as mandatory | readiness must remain a present-state proxy |
| `KQ-10` | What would the most hostile fair reviewer reject first? | systems, security, protocols | `EXCELLENCE` | `AT RISK` | `E2 INDIRECT` | novelty collapse, lack of distributed evidence, or incomplete proof support | test these three objections before any stronger full-paper wording | top-tier framing remains off the table |

### Hostile-review synthesis

| Top rejection reason | Why credible | Evidence that could overturn it | Owner or timing | If unresolved |
| --- | --- | --- | --- | --- |
| narrow novelty still collapses into prior art | broad novelty is already rejected and remaining closure is incomplete | independent closure that preserves the narrow `REFRAME` claim | `novelty_synthesis` before any phase promotion | `STOP` the novelty framing or collapse to non-novel artifact note |
| deadline claims exceed the evidence | no representative distributed benchmark currently exists | bounded synthetic distributed pilot with traceable synchrony assumptions | `authorized_execution` after blocker clearance | remove or sharply narrow deadline-accountability claims |
| theorem or proof support is thinner than the prose implies | `paper/theorem_roadmap.md` exists but proof completion and review are unfinished | proof-obligation completion or narrower wording plus external cryptography review | `human_approval` coordinating external review before stronger full-paper claims | `REDESIGN` the claim set |

Objection not resolvable within the current scope:

- whether the narrow claim is genuinely novel relative to inaccessible or
  future predecessor surfaces.

Required claim boundary if that objection remains:

- keep the work framed as a narrowly bounded internal property-composition
  artifact and do not market it as a novel primitive, production protocol, or
  externally validated system.

### Premortem

| Assumed failure cause | Earliest warning | Prevention | Recovery or stop action | Owner |
| --- | --- | --- | --- | --- |
| confirmatory thresholds are retrofitted after seeing current results | a `research-case/03-design/*` file cites observed outputs as criteria | freeze protocol before rerun | invalidate leaked thresholds and return to design freeze | `methods_design` |
| narrow novelty is defeated by a still-open surface | newly closed search finds a substantially equivalent readiness probe | keep `REFRAME` language and search closure first | `STOP` novelty claim or reduce to implementation note | `novelty_synthesis` |
| distributed pilot contradicts conditional deadline wording | missed deadlines persist even under claim-safe assumptions | keep deadline wording conditional until pilot completes | narrow or remove deadline-accountability claims | `authorized_execution` |
| proof obligations fail under reviewer challenge | an external threshold-cryptography reviewer flags missing or invalid assumptions | maintain the proof-obligation ledger | narrow claims or `REDESIGN` around the surviving statements | `human_approval` coordinating external review |
| independent reproduction diverges materially | clean-machine run misses key hashes or outputs | preserve authoritative manifests and deterministic seeds | diagnose and rerun once; if divergence persists, keep status `AT RISK` | `reproducibility_challenge` |

### Pilot or evidence-acquisition plan

- Decision-relevant uncertainty: whether conditional deadline and accountability
  wording can survive a representative distributed benchmark and independent
  review without exceeding the current claim boundary.
- Why a pilot is needed: current local evidence is analytical, simulated, or
  same-workspace internal; the missing information is about representativeness,
  independent reproduction, and proof or review sufficiency rather than raw
  code existence.
- Smallest safe informative test:
  1. freeze a synthetic distributed benchmark with declared latency, loss,
     crash, and clock assumptions;
  2. run a clean-machine reproduction from authoritative inputs;
  3. package the proof-obligation ledger and frozen claim wording for an
     independent threshold-cryptography reviewer;
  4. package the deadline benchmark and bulletin-board semantics for an
     independent distributed-systems reviewer.
- Measure and denominator:
  - benchmark traces per frozen scenario;
  - reproduced versus authoritative result artifacts;
  - proof obligations closed versus total required for claim-safe wording;
  - reviewer blocking objections versus bounded or resolved objections.
- Sample or run rationale: use the smallest run set that exercises declared
  synchrony failures, reproduces authoritative artifacts, and elicits review on
  the actual claim wording. This is a feasibility pilot, not an efficacy study.
- Maximum cost, time, exposure, and data sensitivity: local synthetic data only;
  no production secrets, live systems, or external data. Monetary and calendar
  ceilings still need accountable-author confirmation before reviewer outreach
  or multi-host allocation.
- Green, amber, and red thresholds: frozen separately in
  `progression-criteria.csv`.
- Stopping conditions:
  - any novelty-defeating predecessor for the narrow claim;
  - any distributed result that invalidates even the conditional deadline claim;
  - any proof or review finding that forces broader claims below the surviving
    contribution line.
- Interpretation:
  - `PILOT_FIRST` succeeds only if the pilot closes the named uncertainty
    without broadening the claim ceiling;
  - otherwise return the smallest affected surface to `REDESIGN`, remain
    `BLOCKED`, or `STOP`.
- Pilot-to-definitive data relationship: pilot traces and reviewer findings may
  inform the definitive confirmatory package, but the same evidence must remain
  explicitly labeled pilot or internal unless rerun inside the authorized
  confirmatory design.

### Critical path, resources, and adverse case

| Milestone | Dependency | Owner or backup | Earliest start | Deadline | Evidence of completion | Recovery path |
| --- | --- | --- | --- | --- | --- | --- |
| preserve draft design authority boundary | accountable human confirmation already recorded on `2026-08-29` | `human_approval` / `intake_integration` | immediate | continuous while design-only work remains in `INTAKE` | `research-case/00-governance/accountable-authority-confirmation.md` stays consistent with the charter, study profile, and current package boundary | remain `BLOCKED` if this boundary drifts or is overread as execution or submission approval |
| close remaining novelty surfaces | existing novelty package | `novelty_synthesis` / `prior_art_search_challenge` | after authority work begins | before stronger feasibility wording | updated novelty package and verification event | narrow or `STOP` claim |
| freeze result-blind design | authority plus novelty floor | `methods_design` / `power_challenge` | after blockers clear | before rerun | protocol and analysis package | return to design if leakage appears |
| prepare distributed pilot harness | frozen design | `authorized_execution` / `methods_design` | after design freeze | before stronger deadline wording | preserved traces and environment manifest | narrow or remove deadline claim |
| run clean-machine reproduction | authoritative manifests | `reproducibility_challenge` / `intake_integration` | parallel with distributed pilot | before reassessment | reproduction report and hash comparison | diagnose once, then keep `AT RISK` if unresolved |
| obtain cryptography and systems reviews | frozen wording and pilot package | `human_approval` / `methods_design` | after pilot and proof pack are ready | before stronger full-paper claims | reviewer memos | narrow claims or `REDESIGN` |
| reassess feasibility | all prior pilot inputs | `feasibility_science` / `solution_viability` | after pilot and reviews | immediate after evidence closure | updated feasibility disposition | remain `BLOCKED`, move to `PILOT_FIRST`, or `STOP` |

- Staff and skills: `feasibility_science`, `solution_viability`,
  `methods_design`, `authorized_execution`, `reproducibility_challenge`, one
  accountable human through `human_approval`, one external
  threshold-cryptography reviewer, one external distributed-systems or
  blockchain reviewer, and one independent reproducer.
- Data, participants, sites, or field access: none beyond local synthetic,
  simulated, and code artifacts; no participant recruitment or live system use
  is authorized.
- Materials, equipment, compute, storage, and maintenance: existing local
  workspace supports prototype reproduction; multi-host or network-shaped pilot
  capacity is not yet evidenced in the record.
- Base budget: local compute and existing artifacts are available.
- Contingency and adverse-case budget: reviewer time, extra clean-machine
  reproduction, and multi-host testing capacity remain unverified and must be
  explicitly authorized.
- Approvals, contracts, and agreements: accountable-human draft-design
  confirmation is recorded; institution or venue policy checks, reviewer
  availability, final author metadata, external sharing, execution, and
  submission authority remain open or separately gated.
- Single points of failure: accountable-author confirmation, narrow novelty
  survival, external reviewer availability, and a trustworthy distributed pilot
  environment.
- Maximum time or cost before stop or redesign: still undefined by accountable
  authority; this must be set before reviewer outreach or multi-host resource
  allocation.
- Realistic adverse scenario and result: novelty survives only narrowly, but
  distributed evidence remains ambiguous. In that case, keep the artifact at a
  narrower internal or workshop-oriented scope and do not expand the deadline
  accountability claim.

### Independent challenge and validation

| Review or validation | Independence or conflict | Question tested | Evidence required | Timing | Owner |
| --- | --- | --- | --- | --- | --- |
| novelty challenge | already independently produced relative to the primary search | does the narrow claim survive bounded prior-art closure? | `research-case/01-novelty/novelty_reconciliation.md`, `research-case/01-novelty/independent-search-challenge.md`, and a verification event | before any phase promotion | `prior_art_search_challenge` |
| threshold-cryptography review | must be external to the current producer | do theorem-level claims and cryptographic assumptions match the wording? | proof ledger, `paper/theorem_roadmap.md`, and claim-safe prose | after blockers clear | `human_approval` coordinating an external reviewer |
| distributed-systems or blockchain review | must be external to the current producer | does the deadline and bulletin-board model overclaim beyond the pilot evidence? | distributed pilot traces and `contracts/README.md` boundary summary | after pilot | `human_approval` coordinating an external reviewer |
| clean-machine reproduction | independent operator or clean environment | can the authoritative artifacts be regenerated reliably? | manifests, authoritative inputs, and hash comparisons | after design freeze | `reproducibility_challenge` |
| external or field validation | not required for the current MPP scope | would any deployment or field claim require stronger evidence? | explicit `N/A` for current scope; future `V4` or `V5` if claims expand | future only | `external_validation` |

Domain challenge:

- preserve the hostile question that this may still be only careful integration.

Methods or statistics challenge:

- verify that rare-event intervals, exact or stochastic comparisons, and any
  confirmatory multiplicity handling are frozen before rerun.

Ethics, legal, or security challenge:

- confirm the non-human synthetic scope, AI disclosure, venue policy basis, and
  research-only contract or prototype framing.

Affected stakeholder challenge:

- not yet externalized; the closest current substitute is reviewer challenge on
  whether the distinction would change any real operator decision.

Prospective, external, or field validation:

- not required for the current MPP scope, but mandatory before any deployment
  or field claim.

Independent reproduction or artifact audit:

- still required.

### Start-package checklist

- [x] Named next phase and authority boundary are recorded.
- [x] Frozen question, contribution map, claim ladder, and boundaries exist.
- [x] Problem statement and decision-use case are documented locally.
- [ ] Reproducible novelty closure and strongest-prior-art matrix are complete
  enough for phase promotion.
- [x] A protocol-faithful technical plan exists for the frozen MPP scope.
- [ ] Result-blind design, measurement, sample-size, and analysis rationale are
  frozen.
- [ ] Ethics, legal, safety, privacy, security, site, and policy checks are
  verified for the next phase.
- [x] Local reproducibility and artifact-preservation paths are documented.
- [ ] Milestones, owners, backups, dates, progression criteria, and stop rules
  are approved for execution.
- [x] Risk register, premortem, and change-control surfaces are now drafted.
- [ ] Independent challenge and external-validation plan are fully closed.
- [ ] Applicable reporting guideline and current venue or funder requirements
  are verified.
- [ ] Authorship, CRediT, provenance, conflicts, and AI-use plan are fully
  reconciled by the accountable human.

### Redesign alternatives

| Alternative | Novel value retained | Constraint resolved | New tradeoff or risk | Evidence needed |
| --- | --- | --- | --- | --- |
| property-only paper | retains the serviceability-versus-availability distinction | removes stronger deadline-accountability ambitions | impact and publishability may narrow sharply | novelty closure plus formal counterexample support |
| workshop or artifact-track note | retains reproducible prototype, tests, and negative result | avoids overclaiming full-paper or deployment readiness | less room for broad scientific claims | venue-specific artifact and scope verification |
| monitoring-bound systems note | retains present-readiness measurement intuition | avoids unsupported novelty or conditional-liveness wording | may collapse into ordinary operational telemetry critique | proof that the canary still adds value beyond heartbeat baselines |

### Required external checks

- Domain expert: one threshold-cryptography reviewer.
- Statistician or methodologist: one methods reviewer for rare-event intervals,
  confirmatory design, and multiplicity handling if the design grows.
- Ethics, IRB, REC, or equivalent: accountable institution or venue check that
  the non-human computational `N/A` framing is acceptable.
- Legal, privacy, security, or regulatory: institution or venue policy basis
  plus research-only security boundary review.
- Data, site, or resource owner: not currently applicable beyond
  `human_approval` for local compute authorization and reviewer outreach.
- Affected stakeholder or community: optional for the current MPP, but any real
  deployment framing would require operator challenge.
- Independent reproducer or red team: still required.
- Funder or venue clarification: still required before any submission-readiness
  statement.

## Blockers

1. `BLOCKED`: novelty remains `UNRESOLVED` even after broad claim rejection and
   narrow `REFRAME`.
2. `BLOCKED`: no result-blind confirmatory design is frozen yet, so current
   favorable evidence cannot set the next thresholds.
3. `BLOCKED`: the generated deadline-pilot start package is design-only and
   execution remains prohibited until the environment profile, deadline
   interpretation, trace denominator, precision target, multiplicity rule,
   novelty gate, and required accountable approval are prospectively resolved.

Secondary but still material blockers for any broader full-paper path:

- no distributed deadline pilot;
- no independent clean-machine reproduction;
- no completed threshold-cryptography review;
- no completed distributed-systems or contract-security review;
- no current venue or reporting-rule verification.

## Reassessment

| Date | New evidence or material change | Invalidated evidence or approval | Status changes | Decision | Remaining blockers |
| --- | --- | --- | --- | --- | --- |
| 2026-08-29 | draft feasibility package updated to reflect direct accountable-human draft-design authority, the generated deadline-pilot start package, and unchanged `INTAKE` boundaries | none | feasibility remains draft only | `BLOCKED` now; recommend `PILOT_FIRST` only after blocker clearance | novelty, result-blind design freeze, unresolved deadline execution parameters, independent review |
