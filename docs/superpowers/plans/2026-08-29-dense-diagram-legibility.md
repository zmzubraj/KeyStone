# Dense Diagram Legibility Remediation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use strict RED-GREEN TDD and the subagent-driven two-stage review loop. Do not phase-promote or treat visual QA as scientific verification.

**Goal:** Replace the stale, oversized derivatives for D1, D2, and D5-D8 with deterministic, source-bound SVG/PNG derivatives whose smallest body text meets the existing provisional 7 pt proxy at 180 mm, while preserving the frozen diagram semantics and explicit accessibility/venue limitations.

**Architecture:** D2's existing deterministic renderer will expose explicit SVG font-size attributes and use a body size that survives 180 mm projection. A new local-only dense-diagram renderer will validate the canonical Mermaid source for D1 and D5-D8 against a frozen semantic contract, produce publication-oriented source-bound SVGs with explicit typography and redundant non-color cues, capture PNG previews using the already-reviewed local Chrome path, and emit a hash-bound aggregate receipt. D3 and D4 remain unchanged because they already pass the provisional 180 mm typography proxy. Root owns canonical integration, ledgers, provenance, package integrity, and final verification.

**Evidence boundary:** Passing the automated typography proxy establishes only deterministic final-size screening under the declared 180 mm heuristic. It does not establish scientific correctness, venue compliance, contextual color-vision accessibility, print quality, assistive-technology behavior, or accountable-human approval.

## Task 1: D2 explicit typography

**Owned files:**

- Modify `scripts/render_property_separation_diagram.py`
- Modify `prototype/tests/test_property_separation_render.py`
- Regenerate `diagrams/02_property_separation.svg`
- Regenerate `diagrams/02_property_separation.png`
- Regenerate `diagrams/02_property_separation.render.json` and sidecar

- [ ] Add a failing test proving the generated SVG exposes explicit font-size attributes and that the smallest body size projects to at least 7 pt at 180 mm.
- [ ] Run the focused test and capture the correct RED failure.
- [ ] Implement the smallest layout-safe renderer change, regenerate derivatives locally, and run GREEN.
- [ ] Preserve the exact three constructive witnesses, the no-complete-lattice boundary, source hash, semantic metadata, and receipt classification.

## Task 2: Deterministic D1/D5-D8 renderer

**Owned files:**

- Create `scripts/render_dense_diagrams.py`
- Create `prototype/tests/test_dense_diagram_render.py`
- Regenerate only `diagrams/01_system_architecture.{svg,png}`
- Regenerate only `diagrams/05_state_machines.{svg,png}`
- Regenerate only `diagrams/06_threat_model.{svg,png}`
- Regenerate only `diagrams/07_sampling_domains.{svg,png}`
- Regenerate only `diagrams/08_experiment_pipeline.{svg,png}`
- Create `diagrams/dense_diagrams.render.json` and adjacent `.sha256`

- [ ] Write failing tests for exact D1/D5-D8 inventory, canonical Mermaid source validation, source-drift rejection, deterministic SVG bytes, semantic metadata, explicit font sizes, 180 mm body-text projection of at least 7 pt, PNG dimensions, receipt hashes, and fail-closed check mode.
- [ ] Run the focused tests and capture RED because the renderer does not exist.
- [ ] Implement a bounded standard-library SVG renderer with source-specific declarative layouts. Do not install dependencies, access the network, or mutate canonical Mermaid sources.
- [ ] Use text plus shape/line-style cues so meaning is not carried by color alone.
- [ ] Capture PNG previews through the existing reviewed Chrome path and write an aggregate preauthorization derivative receipt.
- [ ] Run focused GREEN tests, semantic SVG checks, and the automated visual-QA tool in a temporary or canonical-safe mode.

## Task 3: Independent review and root integration

- [ ] Fresh spec reviewer checks every requirement and frozen semantic boundary; the implementer fixes all Critical/Important gaps and the reviewer rechecks.
- [ ] Fresh code/visual-quality reviewer checks deterministic safety, renderer drift handling, layout, clipping, final-size proxy, source binding, receipt integrity, and claim-safe wording; the implementer fixes all Critical/Important gaps and the reviewer rechecks.
- [ ] Root visually inspects the refreshed diagrams and a regenerated preview sheet/contact sheet if created.
- [ ] Root regenerates the canonical visual-QA report and requires 13/13 integrity pass, D2 no longer `UNKNOWN`, and D1/D2/D5-D8 at least 7 pt under the 180 mm proxy.
- [ ] Root updates the visual ledger, source manifest, rendered hashes, provenance revisions, package manifest, and checksums without promoting `INTAKE` or any scientific gate.
- [ ] Run the focused tests, full Python suite, Foundry suite, freshness checks, strict schema-v4 validation, source-manifest hash closure, checksum verification, and `git diff --check`.

