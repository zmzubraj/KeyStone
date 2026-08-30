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
verifies the checked-in SHA-256 manifest.

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
```

The output is `review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip` with a
SHA-256 sidecar. Local generation does not authorize external transfer. The
archive deliberately excludes accountable-author contact metadata, private
signing material, results, manuscript files, and unrelated unpublished
artifacts. It does not perform independent review or promote the research
phase.
