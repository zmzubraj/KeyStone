# KEYSTONE-MPP-F1 Revision R1: accountable-human execution authorization

Date (UTC): 2026-10-09
Recorded by: AI integration assistant (Claude Code), on the accountable human's instruction
Accountable human: Zubaer Mahmood Zubraj (author)

## Trigger

An external reviewer returned `Jubyer.docx` (author metadata naming the reviewer,
created 2026-08-31) asking the author to fill, align, add and adjust tables and
figures with real data. The returned document is eight screenshots of an
AI-chat answer. It contains placeholder values explicitly labelled
"illustrative" (Tables 4 and 5, Figures 3 and 4). None of those placeholder
values are used anywhere in R1. They are not evidence.

## Decisions taken by the accountable human (verbatim choices, 2026-10-09)

1. "Yes, run frozen PC03": execute the already-frozen PC03 cells
   (`RID-C003-IID-001`, `RID-C003-STRAT-001`, `RID-C003-SW-001`) with the frozen
   counts and seed schedule, labelled prespecified-synthetic. The paper must
   disclose that the PC03 methods review was not independent.
2. "Local emulated testbed": run a deadline experiment as a single-host
   emulation with real cryptography and injected latency, loss and crash
   profiles frozen before running. Labelled emulation, not field data.
3. "Synthetic domain model": include correlated-failure analysis as a
   declared synthetic four-domain model, with no claim about real provider
   behaviour.
4. "Use Sep 20 repo build": the manuscript base is
   `paper/external-review/KEYSTONE_PhD_Reviewer_Manuscript.tex` (2026-09-20).

## What this authorization does NOT do

- It does not make the PC03 methods review independent. The paper discloses this.
- It does not resolve novelty (`NOVELTY_AUDIT` remains `UNRESOLVED`).
- It does not establish INTAKE reviewer independence. The INTAKE signing key
  was created on the author's own machine (see `docs/27`); that gap stays open.
- It does not convert the August exploratory datasets into confirmatory
  evidence. They remain exploratory and are labelled so.
- It does not authorize submission. Submission is a separate human decision.

## Ordering rule

`r1-design-freeze.json` was written and hashed before any R1 run started.
Every R1 output records the freeze SHA-256 it ran under. Any change to the
frozen design after the first run is a logged deviation, never a silent edit.
