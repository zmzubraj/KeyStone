# T1-T8 Evidence-Bound Paper Table Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce an editable, deterministic T1-T8 manuscript table package that populates only source-supported content, labels current internal outputs as preliminary or preauthorization evidence, and exposes missing confirmatory, distributed, external, and independent evidence instead of fabricating it.

**Architecture:** A dependency-free Python exporter reads the frozen research-case and workspace sources, validates their schemas and semantic boundaries, builds eight typed table models, and writes one CSV per table plus combined Markdown, LaTeX, and a hash-bound manifest. The exporter has a fail-closed `--check` mode. Root integration owns the manuscript callouts, source manifest, provenance registry, and package integrity after independent spec and quality review.

**Tech Stack:** Python 3.11+ standard library, pytest, CSV, JSON, Markdown, LaTeX; current authoritative dirty workspace with no commit or worktree mutation.

---

## Frozen scientific boundaries

- Canonical phase remains `INTAKE`; novelty is `UNRESOLVED`; feasibility is `UNASSESSED`; solution viability is `ASSERTED_ONLY`; acceptance readiness is `NOT_ASSESSABLE`.
- T1 is a bounded strongest-prior-art matrix, not novelty clearance.
- T2 is a design comparator registry, not measured superiority.
- T3 records frozen/preauthorization conditions and missing distributed profiles.
- T4 contains only existing preliminary/internal results and may not be called confirmatory.
- T5 is a planned mechanism-isolation registry unless an authorized result ID exists; missing analyses remain `MISSING_NOT_EXECUTED`.
- T6 may include exact, exploratory, and preliminary robustness evidence, with estimands kept distinct.
- T7 may include local timings and Foundry gas only as internal/preauthorization observations; production, operator, network, and external rows remain missing.
- T8 must preserve selective withholding, audit/dispute separation, truthful-domain-label dependency, synchrony limits, and missing external validation.
- No output may invent data, citations, approvals, author identity, external reproduction, or venue compliance.

## Task 1: Deterministic T1-T8 exporter

**Files:**

- Create: `scripts/export_t1_t8_tables.py`
- Create: `prototype/tests/test_t1_t8_tables.py`
- Create: `paper/tables/t1_strongest_prior_art.csv`
- Create: `paper/tables/t2_proposed_vs_baselines.csv`
- Create: `paper/tables/t3_experimental_conditions.csv`
- Create: `paper/tables/t4_primary_results.csv`
- Create: `paper/tables/t5_ablation_mechanism.csv`
- Create: `paper/tables/t6_robustness_boundaries.csv`
- Create: `paper/tables/t7_real_world_feasibility.csv`
- Create: `paper/tables/t8_negative_findings_risks.csv`
- Create: `paper/tables/t1_t8_package.md`
- Create: `paper/tables/t1_t8_package.tex`
- Create: `paper/tables/t1_t8_manifest.json`
- Create: `paper/tables/t1_t8_manifest.json.sha256`

**Required source inputs:**

- `research-case/01-novelty/novelty-matrix.csv`
- `research-case/02-feasibility/risk-register.csv`
- `research-case/03-design/protocol.md`
- `research-case/03-design/analysis-plan.md`
- `research-case/07-manuscript/claim-evidence-matrix.csv`
- `prototype/configs/baseline.json`
- `prototype/results/experiment_manifest.json`
- `prototype/results/baseline.json`
- `prototype/results/exact_stratified_validation.csv`
- `prototype/results/markov_temporal_dependence.csv`
- `prototype/results/selective_withholding.csv`
- `prototype/results/crypto_benchmark.csv`
- `contracts/gas_report.csv`
- `paper/tables/preauthorization_engineering_qa.csv`

- [ ] **Step 1: Write failing schema, boundary, determinism, and freshness tests**

Create tests that import the exporter and require:

```python
EXPECTED_IDS = tuple(f"T{i}" for i in range(1, 9))
ALLOWED_STAGES = {
    "DESIGN_ONLY",
    "PRELIMINARY_INTERNAL",
    "PREAUTHORIZATION_INTERNAL",
    "EXPLORATORY_INTERNAL",
    "ANALYTIC_DRAFT",
    "MISSING_NOT_EXECUTED",
    "BLOCKED_EXTERNAL",
}

def test_build_tables_emits_exact_t1_t8_ids():
    package = module.build_package(PROJECT_ROOT)
    assert tuple(package) == EXPECTED_IDS

def test_claim_boundaries_are_fail_closed():
    package = module.build_package(PROJECT_ROOT)
    assert all(row["evidence_stage"] in ALLOWED_STAGES for table in package.values() for row in table.rows)
    assert all(row["evidence_stage"] != "CONFIRMATORY" for table in package.values() for row in table.rows)
    assert any(row["evidence_stage"] == "MISSING_NOT_EXECUTED" for row in package["T5"].rows)
    assert any(row["evidence_stage"] == "BLOCKED_EXTERNAL" for row in package["T7"].rows)

def test_t8_preserves_selective_withholding():
    package = module.build_package(PROJECT_ROOT)
    joined = " ".join(" ".join(row.values()) for row in package["T8"].rows).lower()
    assert "selective withholding" in joined

def test_write_then_check_is_deterministic(tmp_path):
    module.write_package(PROJECT_ROOT, tmp_path)
    first = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    module.write_package(PROJECT_ROOT, tmp_path)
    assert first == {p.name: p.read_bytes() for p in tmp_path.iterdir()}
```

Also require exact per-table headers, non-empty `source_path`, explicit `claim_ids`, explicit `evidence_stage`, LaTeX escaping, manifest input/output hashes, sidecar correctness, and `--check` failure after a temporary output mutation.

- [ ] **Step 2: Run the focused tests and capture RED**

Run:

```bash
./prototype/.venv/bin/python3 -m pytest -q prototype/tests/test_t1_t8_tables.py
```

Expected: collection/import failure because `scripts/export_t1_t8_tables.py` and outputs do not exist.

- [ ] **Step 3: Implement the typed exporter minimally**

Use these public interfaces:

```python
@dataclass(frozen=True)
class PaperTable:
    table_id: str
    title: str
    headers: tuple[str, ...]
    rows: tuple[dict[str, str], ...]
    notes: tuple[str, ...]

def build_package(project_root: Path) -> dict[str, PaperTable]: ...
def write_package(project_root: Path, output_dir: Path) -> dict[str, str]: ...
def check_package(project_root: Path, output_dir: Path) -> list[str]: ...
```

Every row must carry `claim_ids`, `source_path`, `evidence_stage`, and `claim_ceiling`. Parse numeric values from canonical CSV/JSON files; do not copy values from Markdown. Hard-coded design registry rows are allowed only when they carry exact source locators into the frozen protocol or analysis plan and no measured outcome.

The manifest must contain:

```json
{
  "schema_id": "KEYSTONE_T1_T8_TABLE_PACKAGE",
  "schema_version": 1,
  "status": "DRAFT_PREAUTHORIZATION",
  "scientific_evidence_boundary": "NOT_CONFIRMATORY_OR_INDEPENDENT_EVIDENCE",
  "inputs": [{"path": "...", "sha256": "..."}],
  "outputs": [{"path": "...", "sha256": "..."}],
  "table_dispositions": {"T1": "...", "T8": "..."},
  "missing_required_evidence": ["RID-C003-DEADLINE-001", "independent reproduction", "external validation"]
}
```

The LaTeX output must remain editable, use `tabularx`/`longtable` source only, and include a visible draft/preauthorization note for every table.

- [ ] **Step 4: Generate outputs and reach GREEN**

Run:

```bash
./prototype/.venv/bin/python3 scripts/export_t1_t8_tables.py
./prototype/.venv/bin/python3 -m pytest -q prototype/tests/test_t1_t8_tables.py
./prototype/.venv/bin/python3 scripts/export_t1_t8_tables.py --check
python3 -m py_compile scripts/export_t1_t8_tables.py prototype/tests/test_t1_t8_tables.py
git diff --check
```

Expected: all focused tests and checks pass with no source or output drift.

- [ ] **Step 5: Self-review scientific and data boundaries**

Verify T1-T8 in rendered Markdown and confirm:

- no placeholder is silently converted to zero;
- no preliminary output is described as confirmatory;
- T2/T5 contain no measured superiority claim;
- T6 distinguishes static, exact-stratified, and evolving-state estimands;
- T7 labels gas and timings as local observations;
- T8 includes preserved negative findings and external-validation gaps;
- manifest and sidecar hashes match current bytes.

Do not edit root-owned manuscript, source manifest, registry, provenance, package manifest, or checksums.

## Task 2: Root-owned manuscript and governance integration

**Files:**

- Modify: `research-case/07-manuscript/manuscript.md`
- Modify: `research-case/07-manuscript/source-manifest.json`
- Modify: `research-case/07-manuscript/claim-evidence-matrix.csv` only if table locators change without changing claim text or maturity
- Modify through canonical recorder: `research-case/artifact-registry.csv`
- Modify through canonical recorder: `research-case/00-governance/provenance-ledger.jsonl`
- Modify through canonical recorder: `research-case/00-governance/provenance-anchor.json`
- Regenerate: `PACKAGE_MANIFEST.md`
- Regenerate: `SHA256SUMS`

- [ ] **Step 1: Complete independent spec and code-quality review of Task 1**

Require `SPEC_APPROVED` followed by `QUALITY_APPROVED`. Any finding returns to the original implementer and is re-reviewed.

- [ ] **Step 2: Integrate a claim-safe table map into the manuscript**

Add a table-display subsection that links T1-T8, states each disposition, and explicitly says that T1-T8 are draft/preauthorization displays. Do not duplicate every value in prose and do not remove the draft banner.

- [ ] **Step 3: Bind sources and record DRAFT revisions**

Add the exporter, tests, manifest, and combined table package to `source-manifest.json` with current hashes. Record changed canonical artifacts with `record_artifact.py` as `DRAFT`; do not create scientific `VERIFIED` events or promote phase.

- [ ] **Step 4: Refresh package integrity and run the full gate**

Run:

```bash
python3 scripts/update_package_integrity.py
make verify
./prototype/.venv/bin/python3 scripts/export_t1_t8_tables.py --check
python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/check_research_case.py research-case --strict
git diff --check
```

Expected: full Python, Foundry, gas, table, vector, checksum, source-manifest, provenance, and strict research-case checks pass while canonical phase remains `INTAKE`.

## Completion boundary

This plan completes the editable T1-T8 draft table package and manuscript alignment only. It does not complete confirmatory execution, independent reproduction, external validation, accountable authorship confirmation, venue selection, PDF submission build, or publication readiness.
