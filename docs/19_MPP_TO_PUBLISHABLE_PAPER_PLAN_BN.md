# KEYSTONE MPP থেকে প্রকাশযোগ্য পেপার: বর্তমান blocker-driven execution plan

**System:** `KEYSTONE-MPP-F1`  
**Plan date:** `2026-08-30`  
**Canonical intake anchor:** `RESEARCH_INTAKE.md`  
**Frozen authority:** `FREEZE.md`  
**Canonical program state:** `research-case/program-state.json`  
**Execution model:** evidence-gated, fail-closed, claim-bound, reproducible

## 1. এই plan কী

এটি KEYSTONE-এর current authoritative execution plan। এর কাজ হলো:

- frozen MPP scope না ভেঙে publication path চালানো;
- engineering readiness আর scientific readiness আলাদা রাখা;
- exact blocker order, evidence requirement, এবং next executable wave নির্ধারণ করা;
- subagent-driven acceleration কোথায় safe, আর কোথায় unsafe, সেটা নির্দিষ্ট করা।

এই plan কোনো phase promote করে না। এটি current canonical state-এর working map।

## 2. Current canonical state — 2026-08-30

`research-case/program-state.json` অনুযায়ী:

- `current_phase = INTAKE`
- `resume_from = INTAKE`
- `novelty_status = UNRESOLVED`
- `feasibility_decision = UNASSESSED`
- `solution_viability_status = ASSERTED_ONLY`
- `acceptance_readiness = NOT_ASSESSABLE`

`research-case/09-submission/acceptance-readiness.md` অনুযায়ী:

- required canonical artifacts assessed: `63`
- final (`VERIFIED` or justified `N/A`): `0`
- open: `63`
- open mix: `46 DRAFT`, `17 MISSING`

এর মানে:

- workspace অনেক strong হয়েছে;
- manuscript shell, tables, figures, diagrams, validation shell aligned;
- কিন্তু paper এখনো publication-ready বা submission-ready না।

## 3. Current verified engineering/package state

2026-08-30 local verification evidence:

- Python suite: `240 passed`
- Foundry suite: `27 passed`
- full `make verify`: `PASS`
- manuscript alignment: `PASS`
- draft adversarial review generation/check: `PASS`
- manuscript assembly inventory: `PASS`
- isolated mechanical reproduction dry-run inventory check: `PASS`
- package integrity refresh complete

Current paper-facing asset state:

- claims in manuscript spine: `C001`, `C002`, `C003`
- editable table package: `T1`–`T8`
- rendered diagrams: `D1`–`D8`
- rendered quantitative figures currently available: `F1`–`F5`
- future/manuscript-referenced but not yet executed final outputs: `F6`–`F8`

Important interpretation:

- engineering green != scientific gate passed
- same-host mechanical replay != independent scientific reproduction
- draft reviews != independent review
- manuscript integration != submission readiness

## 4. Frozen claim boundary

Current paper path only survives if it stays inside the narrowed claim-safe lane.

### Allowed manuscript-level central claims

- `C001`: dispute-key serviceability can be formalized distinctly from ciphertext availability under the frozen model
- `C002`: the workspace provides an internal non-production prototype and local reproducibility baseline for the frozen protocol boundary
- `C003`: the frozen package combines bounded analytic, simulated, prototype, and later external evidence without claiming a new primitive or production security

### Prohibited overclaim

নিচের কোনোটাই লেখা যাবে না unless new independently verified evidence appears:

- first system
- first primitive
- new threshold-decryption primitive
- timing-free accountability
- unconditional future availability
- external validity already established
- field validation already established
- production security
- publication-ready
- submission-ready

## 5. Goal decomposition

এই goal-এর controllable part দুই স্তরে ভাগ করা:

1. **Internal completion path**
   - current artifacts align করা
   - missing local packages build করা
   - evidence lineage tighten করা
   - manuscript, figures, tables, diagrams, QA package integrate করা

2. **External dependency path**
   - independent INTAKE verification
   - independent novelty closure
   - independent methods/statistics acceptance
   - independent reproduction
   - venue/rule verification
   - accountable human approval

Internal path strong হলেও external path ছাড়া canonical readiness advance হবে না।

## 6. Current blocker stack

Authoritative blocker order comes from `research-case/08-validation/remediation-log.csv`.

### P0

- `REM-001` — canonical independent INTAKE verification

### P1

- `REM-002` — narrow novelty closure and independent challenge
- `REM-003` — result-blind methods challenge resolution and confirmatory contract freeze
- `REM-004` — bounded synthetic distributed deadline pilot execution
- `REM-005` — independent clean-machine reconstruction and qualified crypto/systems review
- `REM-006` — external or justified domain-equivalent validation, or narrower claim ceiling
- `REM-008` — target venue and official rule verification
- `REM-009` — hermetic final submission package build and inspection
- `REM-011` — independent adversarial manuscript review after evidence integration
- `REM-012` — close C003 figure/negative-finding contract

### Deferred by explicit user instruction

- `REM-010` — authorship/corresponding-author/affiliation wording final freeze

## 7. Fastest safe execution order

সবচেয়ে দ্রুত কিন্তু fail-closed order:

```text
Wave 0  -> canonical INTAKE packet stable
Wave 1  -> independent INTAKE verification received
Wave 2  -> novelty closure + methods freeze
Wave 3  -> authorized execution and missing analysis artifacts
Wave 4  -> final table/figure/diagram/manuscript integration
Wave 5  -> adversarial QA + venue + submission package
Wave 6  -> accountable human approval
```

Wave skip করা যাবে না।

## 8. Exact wave contract

### Wave 0 — stabilize the handoff package

Objective:

- external verifier-দের জন্য current packet unambiguous করা
- intake, authority, confidentiality, and claim boundaries one place-এ bind করা

Must exist and stay current:

- `docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md`
- `review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip`
- `review-packets/KEYSTONE-MPP-F1-intake-verifier-return-template.json`
- `research-case/00-governance/accountable-authority-confirmation.md`

Done condition:

- verifier packet current
- hashes current
- handoff text does not imply phase promotion

### Wave 1 — external INTAKE closure

Objective:

- `REM-001` close করা

Required evidence:

- authenticated independent verifier return
- matching artifact hashes
- canonical trust bootstrap acceptance

Done condition:

- INTAKE artifacts independently verified
- only then serial phase advancement can be considered

Hard stop:

- no AI/self-sign/self-review can satisfy this gate

### Wave 2 — novelty + methods freeze

Objective:

- `REM-002` and `REM-003` close করা

Must produce:

- final narrow novelty wording under current evidence ceiling
- independent novelty challenge disposition
- accepted methods packet without outcome leakage
- final estimands, replicate counts, precision rules, multiplicity handling, and stop rules

Done condition:

- broad novelty remains rejected unless independently overturned
- no confirmatory command is authorized before methods freeze

Hard stop:

- existing exploratory outputs cannot be relabeled confirmatory

### Wave 3 — missing executed analysis artifacts

Objective:

- `REM-004` and the missing `05-analysis` artifacts create করা

Priority missing canonical outputs:

- `05-analysis/results/primary-results.csv`
- `05-analysis/results/negative-findings.csv`
- `05-analysis/results/robustness-and-boundaries.csv`
- `05-analysis/external-validation/*` if claim scope still requires them
- distributed deadline evidence for `RID-C003-DEADLINE-001`

Done condition:

- every executed result has provenance, seeds/config, exclusions, and claim-safe wording

Hard stop:

- no deadline/accountability strengthening without executed trace-bound evidence

### Wave 4 — evidence-to-paper integration

Objective:

- all verified evidence into tables, figures, diagrams, and manuscript bind করা

Must close:

- `REM-007`
- `REM-012`
- `07-manuscript/claim-evidence-matrix.csv`
- `07-manuscript/manuscript.md`
- `06-visuals/visual-ledger.csv`

Done condition:

- every central sentence has claim-safe support
- no orphan table/figure/diagram
- no draft display asset is presented as executed confirmatory evidence

### Wave 5 — adversarial and venue package

Objective:

- `REM-008`, `REM-009`, `REM-011`

Must produce:

- venue portfolio
- current venue rules
- reporting checklist
- submission audit
- submission gate ledger
- hermetic build evidence
- independent adversarial review dispositions

Done condition:

- no hidden critical `FAIL` or `UNKNOWN`
- package can honestly be handed off as internally submission-prepared pending external/human approvals

### Wave 6 — human authority closure

Objective:

- accountable authors make the final human decisions

Includes:

- final metadata freeze when you decide
- author order
- corresponding author
- affiliation wording
- declarations
- final PDF and portal preview approval

Hard stop:

- AI must not infer or freeze these on its own

## 9. Subagent-driven execution model

হ্যাঁ, fast completion-এর জন্য subagent-driven development ব্যবহার করা যাবে, কিন্তু
শুধু write-disjoint surfaces-এ।

### Root integration owner reserved scope

নিচের surfaces root ছাড়া আর কেউ final ownership নেবে না:

- `research-case/program-state.json`
- `research-case/artifact-registry.csv`
- `research-case/00-governance/*`
- final integrated `07-manuscript/manuscript.md`
- package integrity files
- phase decision and verification ledgers

### Safe parallel lanes

| Lane | Outcome | Safe write scope | Depends on |
| --- | --- | --- | --- |
| Intake handoff lane | external verifier packet coherence | `docs/20_*`, `review-packets/*`, handoff notes | current frozen scope only |
| Novelty lane | narrow novelty closure package | `01-novelty/*`, `09-submission/novelty-refresh.md` | Wave 1 packet stability |
| Methods lane | result-blind design freeze | `03-design/*`, selected `02-feasibility/*` | novelty-safe wording |
| Analysis prep lane | authorized execution checklist and result contract | `04-data/*`, planning-only `05-analysis/*` | methods freeze |
| Visual lane | final T/F/D lineage and caption contract | `06-visuals/*`, `paper/tables/*` | evidence IDs stabilized |
| Manuscript lane | prose integration and wording discipline | `07-manuscript/*`, selected `paper/*` | novelty + methods + visual interfaces stable |
| Submission lane | venue/rules/checklists/build QA | `09-submission/*`, build logs | first integrated manuscript exists |

### Unsafe parallelism

এগুলো parallelize করা যাবে না:

- same file edits by multiple agents
- novelty certification and manuscript promotion together
- result generation and independent validation by same owner
- phase promotion while upstream verification is still draft

## 10. Subagent-ready task map

নিচের task map later direct dispatch-এর জন্য ready:

| Task name | Objective | Owned scope | Forbidden scope | Exit evidence |
| --- | --- | --- | --- | --- |
| `intake_verifier_packet_owner` | stabilize external intake handoff artifacts | `docs/20_*`, `review-packets/*` | no phase decision files | current packet + matching hashes |
| `narrow_novelty_refresh_owner` | close narrow novelty wording and refresh package | `01-novelty/*`, `09-submission/novelty-refresh.md` | no manuscript promotion | refreshed novelty package + challenge-ready wording |
| `result_blind_methods_owner` | freeze estimands and confirmatory contract | `03-design/*`, selected `02-feasibility/*` | no execution of confirmatory runs | accepted design packet |
| `deadline_pilot_contract_owner` | prepare distributed deadline execution surface | planning `04-data/*`, `05-analysis/*` | no claim broadening | execution checklist + provenance contract |
| `visual_lineage_owner` | close figure/table/diagram lineage | `06-visuals/*`, `paper/tables/*` | no new scientific claim | lineage-complete visual package |
| `manuscript_claim_integration_owner` | integrate verified claims into prose | `07-manuscript/*` | no phase promotion | claim-safe manuscript revision |
| `submission_package_owner` | venue/rules/checklist/build package | `09-submission/*` | no human approval freeze | submission QA package |

## 11. Immediate next executable actions

Without waiting for new authority, the next safe internal work is:

1. intake handoff artifacts audit and tighten
2. novelty refresh packet tighten for the current narrow claim
3. methods packet tighten so no ambiguity remains before any future confirmatory run
4. manuscript claim-to-blocker matrix sharpen so blocked versus admissible wording is explicit

Without external state change, the following cannot honestly complete:

- canonical INTAKE closure
- novelty survival certification
- methods acceptance
- independent reproduction
- venue approval
- human submission approval

## 12. Definition of internal completion for this stage

এই phase-এর realistic internal success হলো:

- all current local artifacts stay mutually aligned
- blocker order is explicit
- subagent-ready write scopes are clear
- no stale plan contradicts canonical state
- external blockers are surfaced truthfully

এটা publication-ready completion না।  
এটা publication path-এর execution systemকে current truth-এর সাথে aligned করা।

## 13. Final truth statement

আজকের date অনুযায়ী honest status হলো:

- KEYSTONE-MPP is workspace-ready for disciplined paper completion
- it is not yet publication-ready
- it is not yet submission-ready
- the shortest honest path is `INTAKE -> NOVELTY -> METHODS -> EXECUTED ANALYSIS -> PAPER INTEGRATION -> SUBMISSION QA -> HUMAN APPROVAL`

