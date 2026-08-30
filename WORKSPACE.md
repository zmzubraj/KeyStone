# KEYSTONE Workspace Guide

This directory is the development workspace for the frozen `KEYSTONE-MPP-F1`
research package. Workspace setup and test infrastructure may change without
unfreezing the research thesis. Any claim-boundary change still follows
`FREEZE.md`.

## Required tools

- `uv` with Python 3.13 support
- Foundry/Forge with Solidity 0.8.24 support
- `make`

## First setup

```bash
make setup
```

This creates `prototype/.venv` from the checked-in `prototype/uv.lock`.

## Fast verification

```bash
make verify
```

The fast gate runs the Python tests, compiles and tests the Solidity boundary,
checks the Foundry gas snapshot, verifies that generated paper tables match
their canonical result sources, checks canonical transcript and signature-vector
freshness, checks every manuscript source-manifest path and SHA-256 binding,
checks fail-closed canonical status and deferred final author metadata, closes
the C001-C003 claim set across manuscript/matrix/graph, validates citations and
workspace-local image references, requires T1-T8/D1-D8/F1-F5 coverage, and
checks the deterministic `NOT_ASSESSABLE` acceptance-readiness gap inventory,
verifies the preauthorization-only provenance/evidence lineage without promoting
any scientific gate, checks the quarantined temporal exploratory ledger without
relabeling it as confirmatory evidence, checks the bounded selective-withholding
negative-findings ledger without relabeling it as confirmatory evidence, checks
the IID and matched-policy draft robustness/boundary ledger while excluding
entangled correlated-domain, Markov, selective-withholding, and deadline
evidence, and verifies the checked-in SHA-256
manifest. It also checks the non-executable confirmatory pilot plan and its
machine-readable result contract; this confirms design integrity only and does
not authorize a run. It also verifies the deterministic PC02 novelty-review
handoff without treating local generation as novelty certification, and checks
the non-executable PC03 count and seed amendment plus its qualified external
methods-review handoff without treating packet generation as methods approval.
It also checks the deterministic manuscript assembly inventory so the draft
paper shell stays bound to its current claim, table, figure, and diagram
assets without hiding missing rendered outputs or deferred human metadata.

To regenerate or check the current fail-closed publication gap inventory:

```bash
make acceptance-readiness-gap
make acceptance-readiness-gap-check
make manuscript-assembly-inventory
make manuscript-assembly-inventory-check
make evidence-lineage
make evidence-lineage-check
make exploratory-findings
make exploratory-findings-check
make negative-findings
make negative-findings-check
make robustness-boundaries
make robustness-boundaries-check
make confirmatory-pilot-plan
make confirmatory-pilot-plan-check
```

The canonical output is
`research-case/09-submission/acceptance-readiness.md`. It is a mechanical
inventory of open requirements, not a scientific review, venue decision, or
submission authorization.

The manuscript-assembly targets write or check
`research-case/07-manuscript/assembly-inventory.md`. The report is a draft
paper-assembly ledger only: it cross-links `C001`-`C003`, `T1`-`T8`, rendered
`F1`-`F5`, rendered `D1`-`D8`, and the currently unrendered future `F6`-`F8`
identifiers without promoting any scientific gate.

The evidence-lineage targets write or check
`research-case/04-data/provenance-manifest.csv` and
`research-case/04-data/evidence-status.csv`. These ledgers bind current analytic,
simulation, and internal engineering artifacts while preserving
`PREAUTHORIZATION_ONLY`, `NOT_SCIENTIFIC_EVIDENCE`, and
`SAME_WORKSPACE_NOT_INDEPENDENT` boundaries.

The exploratory-findings targets write or check
`research-case/05-analysis/results/exploratory-findings.csv`. The ledger uses
distinct `EXPLORE-*` finding IDs, preserves the source simulation maturity, and
caps manuscript support at `V0 ASSERTED` while the run remains at `INTAKE`.
It cannot satisfy novelty, feasibility, primary-result, or external-validation
gates; the canonical primary ledger remains missing until its declared
dependencies and authorization conditions pass.

The negative-findings targets write or check
`research-case/05-analysis/results/negative-findings.csv`. The ledger exports
only the interval-separated selective-withholding gap already present in the
frozen seeded simulation (`NEG-SW-11` through `NEG-SW-14`). Every row remains
`DRAFT_NEGATIVE_FINDING_ONLY`, unauthorized, non-independent, simulated, and
capped at `V0 ASSERTED`; it cannot substitute for confirmatory execution,
deadline evidence, independent reproduction, external validation, or F6-F8.

The robustness-boundaries targets write or check
`research-case/05-analysis/results/robustness-and-boundaries.csv`. The ledger
exports all 17 frozen IID outage cells and all 12 frozen matched-seed sampling
policy cells. Every row remains `DRAFT_ROBUSTNESS_BOUNDARY_ONLY`, unauthorized,
non-independent, simulated, and capped at `V0 ASSERTED`. Correlated-domain data
is excluded because its current evidence ID is also bound to the quarantined
Markov asset; Markov, selective-withholding, and deadline outputs are likewise
excluded. The ledger is a traceability improvement only, not a primary result,
confirmatory analysis, production-robustness claim, or gate promotion.

The confirmatory-pilot targets write or check
`research-case/02-feasibility/pilot-plan.md` and
`research-case/02-feasibility/pilot-run-contract.csv`. Every reserved result ID
remains `BLOCKED_PENDING_GATE`, unauthorized, non-independent, and without an
observed outcome. Deterministic case families are structurally enumerated;
three minimum stochastic cells have exact result-blind counts, precision rules,
and predeclared seed blocks pending independent methods review; correlated-domain
analysis and the distributed deadline environment remain explicitly excluded.
The minimum short-paper lane preserves selective withholding as a decisive
negative result, while the deadline family stays in the extended full-paper
lane.

## Full research reproduction

```bash
make reproduce
make snapshot
```

`make reproduce` regenerates the Python demo, analytical result, simulations,
figures, benchmarks, tests, and preliminary Markdown/LaTeX paper tables. Because it intentionally rewrites result
artifacts, refresh `VERIFICATION.md`, `ENVIRONMENT.txt`, `PACKAGE_MANIFEST.md`,
and `SHA256SUMS` only after reviewing the new evidence.

## Workspace boundaries

- Do not use the prototype for production funds or sensitive data.
- Do not claim primitive-level novelty or unconditional future availability.
- Keep generated Python environments and Foundry build artifacts untracked.
- Preserve datasets, figures, manifests, and verification records that support
  paper claims.

## Research-program workflow

`RESEARCH_INTAKE.md` is the immutable six-field kickoff for the active
schema-v4 `research-case/`. Resume that case from `research-case/program-state.json`;
do not initialize another run for the same intake. The detailed Bangla execution
contract is `docs/19_MPP_TO_PUBLISHABLE_PAPER_PLAN_BN.md`, including the
fastlane subagent-driven execution model, wave ordering, and ownership
boundaries for moving from `INTAKE` to a publishable package.

For the current external human gate, use
`docs/23_INDEPENDENT_INTAKE_HUMAN_VERIFICATION_SOP_BN.md`. It gives the
reviewer eligibility rules, nine artifact-specific questions, exact return and
signature procedure, four independently signed canonical event commands,
fail-closed stop rules, and the checklist that must pass before Codex treats
the INTAKE-verifier task as complete.

Research-case artifacts remain `DRAFT` until their semantic and independent
verification requirements pass. Engineering tests produced before the study
design is frozen are preliminary hardening evidence and must be rerun under the
prespecified confirmatory protocol before they support a paper claim.

The current gate is `INTAKE`. The accountable-human authority statement is
captured, while final author order, corresponding-author designation, and exact
affiliation wording are intentionally deferred. A qualified external reviewer
can use `docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md` to bootstrap the externally
rooted verifier identity and independently verify the four canonical intake
artifacts. Until those signed events exist, keep the phase at `INTAKE` and all
scientific verdicts fail-closed.

To create or verify the bounded, deterministic local handoff archive:

```bash
make intake-review-bundle
make intake-review-bundle-check
make intake-verifier-return-template
make intake-verifier-return-template-check
make pc02-novelty-verifier-packet
make pc02-novelty-verifier-packet-check
make pc03-design-amendment
make pc03-design-amendment-check
make pc03-methods-verifier-packet
make pc03-methods-verifier-packet-check
make pc03-methods-verifier-packet
make pc03-methods-verifier-packet-check
```

The output is `review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip` with a
SHA-256 sidecar. Local generation does not authorize external transfer. The
archive deliberately excludes accountable-author contact metadata, private
signing material, results, manuscript files, and unrelated unpublished
artifacts. It does not perform independent review or promote the research
phase.

The companion
`review-packets/KEYSTONE-MPP-F1-intake-verifier-return-template.json` is bound
to the current intake ZIP hash and four canonical artifact revisions. The
read-only validator rejects stale, incomplete, over-scoped, or unbound returns;
it never verifies reviewer identity or signatures, writes canonical state, or
promotes the case.

The PC02 output is
`review-packets/KEYSTONE-MPP-F1-pc02-novelty-review-packet.zip` with a SHA-256
sidecar and the human-readable handoff at
`docs/21_PC02_NOVELTY_VERIFIER_HANDOFF.md`. It freezes the narrow `REFRAME`
boundary, excludes deferred author/contact metadata, and packages only the
hash-bound novelty evidence needed by a qualified reviewer. It may not assert
novelty, authorize pilot execution, or promote the canonical phase; a
decision-bearing outcome still requires an authenticated, independently signed
verification event.

The PC03 operative draft consists of
`research-case/03-design/pc03-prospective-amendment.md`,
`pc03-prospective-counts.csv`, and `pc03-seed-schedule.csv`. An independently
owned developmental challenge is kept under
`research-case/03-design/pc03-independent-methods-challenge/`. The amendment
freezes the smallest defensible prospective synthetic stochastic design for the
current minimum-publishable path, keeps author metadata deferred, and excludes
both correlated-domain analysis and the distributed deadline lane until their
missing source or environment contracts are frozen. Local generation does not
authorize execution or constitute independent methods sign-off.

The bounded PC03 methods-review handoff is
`docs/22_PC03_METHODS_VERIFIER_HANDOFF.md`, and the deterministic local bundle
is `review-packets/KEYSTONE-MPP-F1-pc03-methods-review-packet.zip` with a
SHA-256 sidecar. It packages only the current PC03 design basis, amendment
triad, developmental challenge history, and non-executable pilot-contract
context for a qualified external methods reviewer. It does not authorize
execution, certify methods, close novelty, or promote the research phase.

The PC03 review output is
`review-packets/KEYSTONE-MPP-F1-pc03-methods-review-packet.zip` with a SHA-256
sidecar and the reviewer checklist at
`docs/22_PC03_METHODS_VERIFIER_HANDOFF.md`. It binds the exact minimum-cell
design, count contract, seed schedule, simulator and pilot boundary while
excluding deferred author/contact metadata. It remains a developmental handoff:
external transfer needs accountable-human approval, and a decision-bearing
methods outcome still requires an authenticated independently signed verifier
event. It cannot authorize confirmatory execution or promote the case from
`INTAKE`.
