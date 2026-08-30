# KEYSTONE MPP থেকে প্রকাশযোগ্য পেপার: বিস্তারিত বাস্তবায়ন পরিকল্পনা

**Goal ID:** `KEYSTONE-MPP-F1`  
**Canonical intake:** `RESEARCH_INTAKE.md`  
**Frozen authority:** `FREEZE.md`  
**Execution model:** evidence-gated, claim-bound, reproducible, fail-closed

## 1. চূড়ান্ত outcome

এই কাজের লক্ষ্য শুধু runnable prototype নয়। লক্ষ্য হলো একই evidence spine থেকে চারটি ক্রমবর্ধমান deliverable তৈরি করা:

1. **MPP complete:** frozen C1–C6 claim-এর minimum credible evidence, tests, simulations, figures এবং limitations সম্পূর্ণ।
2. **Workshop-ready:** performance evidence, contract hardening, সম্পূর্ণ tables/figures, manuscript এবং clean reproduction সম্পূর্ণ।
3. **Full-paper submission package:** distributed deadline experiment, production-grade integration boundary, adversarial QA, current venue compliance এবং compiled PDF সম্পূর্ণ।
4. **Human-approved submission:** accountable authors/reviewers final scientific accuracy, authorship, disclosures, rendered PDF এবং submission portal অনুমোদন করবেন।

কোনো lower stage-কে higher stage হিসেবে লেখা যাবে না। Journal acceptance এই goal-এর controllable output নয়; verified editorial decision ছাড়া `accepted` বলা যাবে না।

## 1.1 বর্তমান execution checkpoint — 2026-08-30

| Surface | Verified current state | Scientific disposition |
|---|---|---|
| Python MPP | 57 tests pass; exact stratified oracle, Wilson intervals, temporal pilot, canonical transcripts, Ed25519 response signatures, experimental generation-bound share refresh, fail-closed receipt/table lineage checks, experiment-manifest drift checks, interpreter-portable preliminary-table lineage receipt checks, and source-bound D2 render/receipt checks | internal preliminary `V3` ceiling; confirmatory rerun pending |
| Solidity boundary | 27 Foundry tests pass; 14 deterministic boundaries, 3 fuzz properties ×512, 2 invariants ×2048 calls, and 8 test-body gas operations | internal preliminary; independent audit pending |
| Reproducibility | generated tables/vectors freshness checks, 195-file inventory + manifest, 196 passing hashes | mechanical integrity only, not scientific verification |
| Prior art | separate primary search ও independent challenge complete | broad novelty rejected; narrow claim `REFRAME`, novelty still `UNRESOLVED` |
| Paper evidence | five figures, exact/Monte Carlo/temporal/gas/crypto tables, eight editable diagrams | exploratory/internal; not yet frozen confirmatory evidence |
| Manuscript | outline, claims, theorem roadmap, related-work boundary, reviewer attack matrix | integrated `.tex` manuscript ও compiled PDF এখনও pending |
| Research-case | schema-v4 structure checker pass; accountable-human scope confirmation canonicalized; external intake reviewer handoff prepared | canonical phase এখনও `INTAKE`; independently signed semantic verification pending |

পরবর্তী critical dependency এখন এভাবে:

`INTAKE external verifier bootstrap -> four canonical intake artifacts independently signed -> strict recheck -> PROCEED to NOVELTY_AUDIT -> submission-time novelty refresh -> feasibility disposition -> result-blind study-design freeze`

এই order না মানলে existing exploratory ফল confirmatory evidence হিসেবে
ভুলভাবে paper-এ ঢুকে যাবে।

## 2. অপরিবর্তনীয় scope

- Frozen title, thesis, research question, C1–C6, threat model এবং prohibited claims `FREEZE.md`-এর সঙ্গে byte-for-byte অর্থগতভাবে সামঞ্জস্যপূর্ণ থাকবে।
- নতুন threshold-encryption, DKG, PVSS, proof-of-possession, context-dependent decryption বা generic accountable decryption primitive দাবি করা যাবে না।
- Routine audit কখনও production ciphertext element ব্যবহার করবে না।
- Sampling-কে future availability-এর unconditional proof বলা যাবে না।
- Selective withholding limitation paper-এর central negative result হিসেবে থাকবে।
- Prototype-কে production-secure বলা যাবে না।

Scope বদলাতে হলে আলাদা `UNFREEZE` decision প্রয়োজন।

## 3. Phase map ও dependency

```text
INTAKE
  -> NOVELTY AUDIT
  -> FEASIBILITY GATE
  -> STUDY DESIGN
  -> AUTHORIZED EXECUTION
  -> ANALYSIS
  -> TABLES + FIGURES + DIAGRAMS
  -> MANUSCRIPT
  -> ADVERSARIAL QA
  -> VENUE + SUBMISSION QA
  -> HUMAN APPROVAL
```

প্রতিটি phase-এর output canonical `research-case/` artifact হিসেবে নিবন্ধিত হবে। File থাকা মানেই verified নয়; scientific gate-এর জন্য independent signed review প্রয়োজন।

## 3.1 Fastlane subagent-driven execution model

হ্যাঁ, fast completion-এর জন্য subagent-driven development ব্যবহার করা যাবে, কিন্তু
শুধু dependency-clear এবং write-disjoint slice-এ। Root integration owner shared
canonical state control করবে; subagent-রা evidence-producing lane own করবে।

### Root integration owner-এর reserved ownership

- `research-case/program-state.json`
- `research-case/artifact-registry.csv`
- `research-case/00-governance/*` phase-promotion sensitive files
- final manuscript integration surface
- phase decision, provenance, verification এবং package-integrity refresh

### Safe parallel lanes

| Lane | Primary outcome | Main write scope | Can run in parallel? | Hard stop |
|---|---|---|---|---|
| L1 Intake verifier coordination | external reviewer packet, artifact hash snapshot, verification command pack | `docs/20_*`, governance notes only | now | cannot self-sign or self-promote |
| L2 Novelty refresh | strongest-prior-art refresh, `09-submission/novelty-refresh.md`, query evidence | `research-case/09-submission/*`, novelty notes | after L1 packet is stable | broad novelty cannot be revived by wording |
| L3 Feasibility + progression | updated progression criteria, risk register, minimum publishable evidence boundary | `research-case/02-feasibility/*` | after frozen novelty scope is restated | no GO if claim scope or required evidence is unclear |
| L4 Confirmatory analysis prep | result lineage audit, config freeze, rerun checklist | `03-design/*`, `05-analysis/*` planning surfaces | after L3 | no confirmatory claim from exploratory outputs |
| L5 Visual/table alignment | T1–T8 source mapping, figure caption contract, diagram-source QA | `06-visuals/*`, `docs/12_*`, figure/table helper files | after L2 and L4 interfaces freeze | no screenshot-only or orphan visuals |
| L6 Manuscript integration | section-by-section claim insertion into paper sources and related-work tightening | `paper/*` except shared final merge by root | after L2-L5 evidence IDs stabilize | no claim stronger than maturity ceiling |
| L7 Adversarial + venue QA | reviewer attack ledger, venue checklist, PDF/package QA | `08-validation/*`, `09-submission/*` | after first full manuscript build | no submission-ready label with critical FAIL/UNKNOWN |

### Recommended active width

- `INTAKE`: root + at most 1 reviewer-support lane
- `NOVELTY_AUDIT` / `MANUSCRIPT`: root + 2 lane owners
- `ANALYSIS` / `ADVERSARIAL_QA`: root + 2 or 3 lane owners

এর বেশি parallelism এখন লাভের চেয়ে বেশি merge risk তৈরি করবে।

## 3.2 Immediate execution order for fastest safe progress

### Wave 0 — unblock the program state

1. `docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md` অনুযায়ী external trust bootstrap packet use করা।
2. চারটি canonical `INTAKE` artifact independently sign করানো।
3. `check_research_case.py --strict` চালানো।
4. তারপরই `advance_research_case.py --decision PROCEED` বিবেচনা করা।

### Wave 1 — lock the scientific boundary

1. `09-submission/novelty-refresh.md` create/update।
2. strongest-predecessor language tighten করা।
3. feasibility report + progression criteria update।
4. confirmatory versus exploratory boundary written freeze।

### Wave 2 — align evidence to paper

1. T1–T8 canonical source tables close করা।
2. Figure F1–F8 source/caption/lineage close করা।
3. D1–D8 diagram source and paper placement close করা।
4. claim-to-evidence matrix থেকে manuscript section drafting শুরু করা।

### Wave 3 — publishable package hardening

1. full manuscript build
2. adversarial review
3. venue-neutral PDF/package QA
4. human approval packet

## 4. Phase-by-phase execution plan

### Phase A — Intake, governance ও claim contract

**কাজ**

- Six-field intake immutable raw এবং normalized revision হিসেবে সংরক্ষণ।
- Field: applied cryptography + blockchain/distributed systems; study type: analytical systems security paper with prototype experiments—এই profile evidence দিয়ে resolve করা।
- C1–C6 এবং prohibited claims-কে stable claim ID দেওয়া।
- Authority, confidentiality, data origin, AI-use এবং external-processing boundary লেখা।
- Claim maturity শুরুতে `V0 ASSERTED`; existing analytic/simulation/internal evidence revalidated হলে যথাক্রমে `V1`, `V2`, `V3` ceiling দেওয়া।

**Exit gate**

- Research question falsifiable এবং measurable।
- প্রতিটি claim-এর required evidence, falsifier, scope ceiling এবং prohibited overclaim আছে।
- `research-case` structural checker pass করে।

### Phase B — Strongest-prior-art novelty audit

**কাজ**

- Problem, mechanism, architecture, evaluation এবং practical-consequence—পাঁচ novelty axis predeclare করা।
- Primary sources দিয়ে papers, IACR ePrint, arXiv, conference proceedings, standards/EIPs, patents, datasets/benchmarks এবং adjacent systems search করা।
- Exact query, date, URL/parameters, raw response hash, screening decision এবং access gap সংরক্ষণ।
- Known-item recovery: PeerDAS/EIP-7594, threshold encryption/DLEQ, VSS/PVSS/DKG, proactive/dynamic sharing, context-dependent threshold decryption, accountable liveness এবং closest bulletin-board/authorization work।
- Backward/forward citation chaining এবং strongest-predecessor feature matrix তৈরি।
- আলাদা independent novelty challenge প্রয়োজন; একই producer নিজের novelty certify করতে পারবে না।

**Exit gate**

- `NOVELTY_SURVIVES`, `NOVELTY_UNRESOLVED`, `REFRAME`, অথবা `STOP`—শুধু এই disposition।
- C1–C6-এর novelty language strongest prior art অতিক্রম করে না।
- Missing material search surface থাকলে phase advance বন্ধ।

### Phase C — Feasibility ও MPP start gate

**কাজ**

- প্রতিটি claim-এর V0–V5 evidence maturity requirement লেখা।
- Minimum credible demonstration, decisive baselines, green/amber/red thresholds এবং failure envelope freeze করা।
- Risk register: cryptographic validity, synchrony, beacon unpredictability, correlated failure metadata, selective withholding, performance, distributed setup, venue fit এবং reviewer access।
- MPP এবং full-paper-এর প্রয়োজন আলাদা করা। Production DKG/PVSS এবং multi-region deployment full-paper extension; MPP-তে integration boundary স্পষ্ট।

**Exit gate**

- `GO`, `PILOT_FIRST`, `REDESIGN`, `BLOCKED`, `RESUME`, অথবা `STOP`।
- Fatal validity, authorization, resource বা testability blocker average করে পাশ করানো যাবে না।

### Phase D — Study design ও preregistered analysis contract

**কাজ**

- RQ1–RQ7-এর জন্য estimand, comparator, unit of analysis, parameter grid, seed, repetitions এবং stop rule freeze।
- Exploratory এবং confirmatory experiment আলাদা করা।
- Rare-event Bernoulli result-এর জন্য Wilson/Clopper–Pearson interval; zero failures-এর upper bound; multiplicity এবং sensitivity plan নির্ধারণ।
- E1 exact enumeration, E2 IID, E3 correlated placement, E4 stratification, E5 invalid/equivocating responses, E6 selective withholding, E7 crypto overhead, E8 distributed deadline, E9 contract gas—সব protocolize করা।
- Distributed testbed unavailable হলে কোন claim narrow হবে তা আগেই লেখা।

**Exit gate**

- Design claim-গুলো test করতে পারে।
- Analysis plan result দেখার আগে frozen।
- Data/result/table/figure ID lineage সম্পূর্ণ।

### Phase E — MPP engineering completion

**Cryptographic/protocol work**

- Canonical transcript serialization এবং protocol-version/epoch/slot/beacon/verifier-set binding।
- Stale epoch, wrong context, duplicate identity, malformed partial, replay, equivocation এবং threshold-boundary negative tests।
- Deterministic test vectors এবং message schemas।
- Production ciphertext audit-canary path-এ ঢুকতে না পারার invariant।

**Solidity work**

- Epoch/audit/dispute lifecycle coverage।
- Authorization, deadline, duplicate, equivocation, missing bitmap এবং finalization boundary tests।
- Fuzz tests এবং stateful invariants।
- Operation-level gas table: epoch registration, audit open, response commit, dispute open, finalize।

**Simulation/measurement work**

- Frozen `n,t,s,q` parameter grid এবং ≥10,000 trial per stochastic point।
- Small-grid exact enumeration বনাম closed form।
- Deterministic seeds, run manifest, environment capture এবং confidence intervals।
- অন্তত তিন machine/platform crypto measurements বা claim explicitly single-machine-এ narrow।
- 32-process/four-domain deadline testbed; latency, loss এবং crash injection।

**Exit gate**

- G0–G5 এবং G7 pass = MPP success।
- G0–G7 pass = workshop-ready।
- G0–G8 plus distributed testbed/integration evidence = full-paper-ready candidate।

### Phase F — Analysis ও evidence freeze

**কাজ**

- Confirmatory result re-run; effect/estimate, uncertainty, sample count এবং practical threshold report।
- Analytical বনাম simulated বনাম internal prototype evidence আলাদা label।
- Robustness: parameter boundaries, domain concentration, audit threshold, temporal dependence, beacon failure এবং network deadline sensitivity।
- Negative findings এবং failed runs সংরক্ষণ।
- External validation না থাকলে external/field generality claim বাদ বা justified `N/A`।

**Exit gate**

- প্রতিটি numeric claim: raw/config -> code -> result ID -> table/figure -> manuscript claim lineage অনুসরণ করে।
- Unresolved contradiction affected claim block করে।

## 5. Paper table contract

Canonical CSV source থেকে LaTeX/Markdown view generate হবে:

| ID | Paper table | KEYSTONE content | Evidence gate |
|---|---|---|---|
| T1 | Strongest prior art | DA, VSS/PVSS/DKG, PoP/DLEQ, threshold KMS, context-dependent release, accountable liveness | independent novelty challenge |
| T2 | Proposed vs baselines | no audit, heartbeat, uniform, stratified, full committee, escalating audit | fair comparator + uncertainty |
| T3 | Experimental conditions | `n,t,s,q`, domains, trials, seeds, machines, network profiles | provenance/rights/metadata |
| T4 | Primary results | false accept, detection, reconstructability, deadline success, overhead | prespecified analysis |
| T5 | Ablation/mechanism | no canonical canary, no domain cap, uniform vs stratified, no escalation | causal prediction + result ID |
| T6 | Robustness/boundaries | temporal dependence, correlation, selective withholding, timing assumptions | failure threshold + claim impact |
| T7 | Real-world feasibility | latency, gas, bandwidth, operator workflow, recovery, DKG/PVSS boundary | external grade or narrow claim |
| T8 | Negative findings/risks | audit-dispute gap, false alarms, metadata truthfulness, production limitations | explicit owner/next falsifier |

অতিরিক্ত paper-facing tables:

- property/assumption matrix;
- attack-to-evidence matrix;
- parameter recommendation by risk tier;
- contract operation gas table;
- hardware/software environment table।

## 6. Figure ও diagram contract

### Quantitative figures

1. Exact detection bound বনাম sample size।
2. IID failure-এ reconstruction এবং audit outcomes।
3. Failure-domain count/placement বনাম reconstructability।
4. Selective-withholding audit/dispute gap।
5. Uniform বনাম stratified detection।
6. Proof generation/verification/open latency distribution।
7. Network latency/threshold deadline-success heatmap।
8. Correlated outage-এর পর recovery timeline।

প্রতিটি figure-এর source CSV, plotting code, vector output, caption facts, final-size font, grayscale/CVD check, SHA-256 এবং evidence label থাকবে।

### Architecture/protocol diagrams

- system architecture;
- property separation;
- routine audit sequence;
- authorized dispute sequence;
- contract/protocol state machines;
- threat model/trust boundaries;
- failure-domain sampling;
- reproducible experiment pipeline।

Mermaid source canonical থাকবে; rendered SVG/PDF locally generate হবে। Diagram কোনো empirical evidence নয়—caption-এ design model হিসেবে চিহ্নিত হবে।

## 7. Manuscript assembly contract

### Section order

1. Introduction
2. Background and strongest related work
3. System/threat model and formal definitions
4. KEYSTONE protocol
5. Security and probability analysis
6. Implementation
7. Evaluation
8. Discussion and deployment guidance
9. Limitations and future work
10. Conclusion
11. Appendices: proofs, schemas, vectors, full grids, artifact instructions

### Claim alignment rule

প্রতিটি central sentence-এর claim ID থাকবে এবং অন্তত একটি theorem, evidence ID, table, figure, বা explicit design-rationale/limitation reference থাকবে। Manuscript claim তার evidence maturity ও scope ceiling অতিক্রম করতে পারবে না।

### Mandatory declarations

- artifact/data/code availability;
- funding and conflicts;
- author contributions/CRediT;
- ethics/participant `N/A` rationale, যদি সত্যিই প্রযোজ্য না হয়;
- AI assistance disclosure;
- prototype/non-production warning;
- third-party software, cryptographic primitive এবং prior-art attribution।

## 8. Adversarial QA ও publication hardening

কমপক্ষে ছয়টি review surface:

1. editor/fit and significance;
2. novelty and strongest predecessor;
3. cryptographic methods/security assumptions;
4. distributed systems/statistics/performance;
5. real-world, ethics and governance boundaries;
6. visual, reproducibility, clarity and coherence।

Critical `FAIL` বা `UNKNOWN` থাকলে submission-ready বলা যাবে না। `PARTIAL` থাকলে সর্বোচ্চ `COMPETITIVE_HIGH_RISK`। Independent qualified reviewers-এর identity/signature এবং human author approval external gate হিসেবে থাকবে।

## 9. Venue এবং submission package

**প্রথমে venue-neutral full draft**, তারপর dated portfolio থেকে primary/fallback venue নির্বাচন। প্রতিটি venue-এর official scope, article type, page limit, anonymity, artifact policy, disclosure, bibliography এবং formatting current web source দিয়ে যাচাই হবে।

Final package:

- canonical `.tex`, `.bib`, figures, tables এবং diagram sources;
- compiled PDF, build log, environment capture, lockfiles এবং hashes;
- reference/citation, font, overflow, anonymity এবং page-limit checks;
- artifact README এবং reproduction command;
- SBOM এবং reviewed offline replay plan;
- submission checklist, novelty refresh, readiness report এবং unresolved-risk ledger;
- human rendered-page এবং portal-preview approval placeholder।

## 10. Verification commands ও evidence cadence

প্রতি engineering batch শেষে:

```bash
make verify
```

Evidence regeneration batch শেষে:

```bash
make reproduce
make snapshot
```

Research-case phase boundary-তে structural/semantic checker, artifact hashes, provenance এবং claim-ID closure পরীক্ষা হবে। Manuscript build phase-এ fail-fast LaTeX compile, bibliography resolution, `pdfinfo`, `pdffonts` এবং rendered-page inspection বাধ্যতামূলক।

## 11. Critical path

```text
Canonical intake
 -> novelty search/challenge
 -> feasibility + frozen study design
 -> exact grid + protocol/contract hardening
 -> distributed deadline evidence
 -> evidence freeze
 -> T1-T8 + F1-F8 + diagrams
 -> manuscript
 -> adversarial remediation
 -> venue/PDF/submission QA
 -> accountable human approval
```

সবচেয়ে বড় controllable blockers: novelty closure ও claim reframe, feasibility/study-design freeze, expanded confirmatory analytical grid, distributed deadline testbed, formal proof completion, missing F6–F8/T1–T8 evidence, এবং manuscript integration। Contract fuzz/invariant ও operation-gas internal gap 2026-08-29-এ বন্ধ হয়েছে। সবচেয়ে বড় external blockers: independent cryptography/systems review, human authorship/disclosure approval এবং editorial decision।

## 12. Definition of done

এই goal তখনই internally complete হবে যখন:

- frozen scope অক্ষত;
- MPP এবং full-paper required tests/experiments reproducible;
- T1–T8 এবং F1–F8 evidence-linked;
- manuscript-এর প্রতিটি central claim traceable;
- bibliography ও venue rules current এবং verified;
- adversarial QA-এর সব internal critical issue resolved;
- clean deterministic PDF/package build হয়;
- external reviewer/human approval items সত্যভাবে `WAITING_EXTERNAL` বা completed হিসেবে দেখানো হয়।

`Publication-ready` কখনও `accepted` বোঝাবে না। External signatures বা human submission authority ছাড়া package সর্বোচ্চ **internally submission-ready, pending independent and accountable human approval** হিসেবে hand off হবে।
