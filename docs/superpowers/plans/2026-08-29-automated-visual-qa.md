# Automated Visual QA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic, local-only, pre-authorization visual-QA tool that checks the 13 frozen KEYSTONE SVG/PNG pairs for structural lineage, raster/vector geometry, provisional final-size legibility, foreground contrast, grayscale separation, and common color-vision-deficiency palette collisions without claiming venue compliance or accessibility certification.

**Architecture:** A standalone Python CLI owns an exact F1-F5/D1-D8 inventory, parses SVG metadata and semantic colors with the standard library, inspects paired PNGs with Pillow, and emits a stable JSON report. Integrity failures are fail-closed; provisional visual heuristics are reported separately as warnings so unknown venue rules and human contextual review remain explicit. Focused pytest tests create only temporary fixtures and verify the TDD contract before the tool is run on canonical assets.

**Tech Stack:** Python 3.11+, standard library (`argparse`, `hashlib`, `json`, `xml.etree.ElementTree`), Pillow already present in the locked project environment, pytest.

---

### Task 1: Deterministic visual-QA engine and CLI

**Files:**
- Create: `scripts/validate_visual_accessibility.py`
- Create: `prototype/tests/test_visual_accessibility.py`

- [ ] **Step 1: Write failing inventory and missing-input tests**

  Define tests that require an exact 13-item F1-F5/D1-D8 inventory, reject missing/non-regular/symlink inputs, and fail with an integrity result rather than silently skipping an asset.

- [ ] **Step 2: Run the focused tests and capture RED**

  Run `./prototype/.venv/bin/python3 -m pytest -q prototype/tests/test_visual_accessibility.py` and confirm failure because the new module/CLI does not exist.

- [ ] **Step 3: Implement minimal inventory, bounded path handling, hashing, and CLI**

  Add `--project-root`, `--report`, and `--fail-on {integrity,proxy}`. The default must fail only on integrity errors. Reject inputs that resolve outside the supplied project root or are symlinks. JSON output must omit wall-clock timestamps and use stable key ordering.

- [ ] **Step 4: Write failing SVG/PNG geometry tests**

  Test SVG width/height/viewBox parsing, PNG width/height/mode/alpha inspection, SHA-256 capture, aspect-ratio comparison, and effective raster PPI at provisional widths of 85 mm and 180 mm. A mismatched aspect ratio must be an integrity failure.

- [ ] **Step 5: Implement geometry and lineage inspection**

  Preserve both raw measurements and derived proxies. Treat 85/180 mm and 300 PPI as declared provisional screening parameters, not venue rules. Do not upsample or mutate any input.

- [ ] **Step 6: Write failing final-size typography tests**

  Test direct `font-size` attributes, CSS `font-size`, and Matplotlib path-text transforms of the form `scale(0.1 -0.1)`. Project the smallest detectable source font to 85 mm and 180 mm widths and compare with a declared 7 pt heuristic. Return `UNKNOWN` when no defensible font size can be extracted.

- [ ] **Step 7: Implement typography proxy**

  Record source minimum, projected minima, heuristic outcome, extraction method, and limitations. A proxy warning must never become an integrity failure unless `--fail-on proxy` is explicitly requested.

- [ ] **Step 8: Write failing palette/contrast/grayscale/CVD tests**

  Test extraction of literal SVG fill/stroke/style colors, exclusion of `none`, `currentColor`, gradients, and non-color tokens, white-background WCAG sRGB contrast, CIE L* grayscale separation, and deterministic protanopia/deuteranopia/tritanopia severity-100 matrix screening. Tests must confirm that intentionally colliding colors produce warnings.

- [ ] **Step 9: Implement palette screening**

  Use documented sRGB/linear RGB/XYZ/Lab transformations and fixed severity-100 matrices. Report 3:1 graphical-object contrast and pairwise delta-L/delta-E thresholds only as conservative heuristics. Explicitly state that adjacency, line thickness, redundant encoding, print conversion, contextual semantics, assistive technology, and venue rules still require human review.

- [ ] **Step 10: Write failing deterministic-report and real-inventory sandbox tests**

  Run the same fixture twice and require byte-identical JSON. Clone representative canonical assets to a temporary project root and prove that the tool does not write into the canonical workspace.

- [ ] **Step 11: Complete the report schema and run GREEN**

  The report must include tool/schema versions, methodology and thresholds, exact inventory, per-asset hashes and measurements, integrity failures, proxy warnings, summary counts, and explicit non-certification limitations. Run the focused test file until all tests pass with no warnings or canonical writes.

- [ ] **Step 12: Self-review**

  Confirm the implementation has no network path, no mutation of source assets, no venue or accessibility certification wording, no evidence-maturity or canonical phase change, and no dependency installation.

### Task 2: Review and canonical report integration

**Files:**
- Generate after approval: `prototype/results/engineering_qa/visual_accessibility_proxy.json`
- Modify after approval: `research-case/06-visuals/visual-ledger.csv`
- Modify after approval: `research-case/06-visuals/figures/figure-manifest.csv`
- Modify after approval: `research-case/07-manuscript/source-manifest.json`
- Modify after approval: `.superpowers/sdd/keystone_mpp_goal_plan/progress.md`
- Refresh after approval: `PACKAGE_MANIFEST.md`, `SHA256SUMS`

- [ ] **Step 1: Independent spec-compliance review**

  A read-only reviewer checks every Task 1 requirement and returns exact Critical/Important/Minor findings or `SPEC_APPROVED`.

- [ ] **Step 2: Remediate and re-review any spec gaps**

  The original implementer fixes only the owned implementation/test files; the same reviewer rechecks until approved.

- [ ] **Step 3: Independent code-quality review**

  A fresh read-only reviewer checks parser safety, numerical correctness, deterministic behavior, error handling, test quality, and claim-safe wording. Important findings must be fixed and re-reviewed.

- [ ] **Step 4: Root runs the approved tool on the exact canonical inventory**

  Generate the JSON report using the project venv. Do not modify figures or diagrams. If integrity fails, stop integration and remediate the source mismatch first. Proxy warnings are preserved, not hidden.

- [ ] **Step 5: Root integrates only evidence-supported status changes**

  Add the report path/hash to the source manifest and update visual ledgers from `PENDING` only to an explicit automated-proxy disposition. Keep final venue-size, contextual CVD, assistive-technology, independent scientific, and accountable-human review pending.

- [ ] **Step 6: Full verification**

  Run the focused tests, the full Python suite, Foundry tests, source-manifest hash validation, strict schema-v4 case validation, package checksum verification, and `git diff --check`. Do not promote `INTAKE`, novelty, feasibility, solution viability, or acceptance readiness.

