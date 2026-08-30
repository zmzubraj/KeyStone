# KEYSTONE Isolated Mechanical Reproduction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reproduce the current KEYSTONE package in a temporary isolated copy using offline-capable, allowlisted commands and emit a hash-bound receipt that strengthens mechanical reproducibility without claiming external or independent scientific verification.

**Architecture:** A Python harness validates the authoritative checksum inventory, copies only inventoried files into a temporary directory, runs a frozen command plan with tool-level offline flags, verifies copied sources and manuscript-source bindings, and writes command logs plus a receipt back to a dedicated engineering-QA directory. Tests exercise real temporary copies and subprocesses before the full frozen command plan is executed by a distinct reproduction subagent. The root integration owner later binds the harness, tests, receipt, and limitations into manuscript provenance.

**Tech Stack:** Python 3 standard library, pytest, uv offline mode, Foundry offline mode, SHA-256, schema-v4 research-case checker.

---

## File map and ownership

- Create `scripts/run_isolated_mechanical_reproduction.py`: checksum parser, isolated copier, allowlisted command runner, source-manifest verifier, receipt writer, and receipt checker.
- Create `prototype/tests/test_isolated_mechanical_reproduction.py`: RED/GREEN tests for inventory closure, source immutability, subprocess capture, fail-closed command behavior, receipt semantics, tamper rejection, and CLI error handling.
- Generate `prototype/results/engineering_qa/isolated_reproduction/receipt.json`: actual isolated-copy mechanical reproduction result.
- Generate `prototype/results/engineering_qa/isolated_reproduction/receipt.json.sha256`: final receipt binding.
- Generate `prototype/results/engineering_qa/isolated_reproduction/commands/*.stdout.txt` and `*.stderr.txt`: exact captured command outputs.
- Modify later, root-only: `research-case/07-manuscript/source-manifest.json`, `research-case/07-manuscript/manuscript.md`, `PACKAGE_MANIFEST.md`, and `SHA256SUMS`.

The implementer may own only the harness and its focused tests. The reproduction operator may write only the isolated-reproduction output directory. Shared manuscript/provenance files remain root-owned.

## Frozen receipt contract

The receipt must contain these exact top-level values:

```json
{
  "schema_id": "KEYSTONE_ISOLATED_MECHANICAL_REPRODUCTION_RECEIPT",
  "schema_version": 1,
  "system": "KEYSTONE-MPP-F1",
  "canonical_phase": "INTAKE",
  "novelty_status": "UNRESOLVED",
  "feasibility_decision": "UNASSESSED",
  "solution_viability": "ASSERTED_ONLY",
  "acceptance_readiness": "NOT_ASSESSABLE",
  "executor_class": "SECOND_AGENT_SAME_HOST_ISOLATED_COPY",
  "scientific_evidence_status": "NOT_INDEPENDENT_SCIENTIFIC_VERIFICATION",
  "external_sharing": "NOT_PERFORMED",
  "network_isolation": "TOOL_FLAGS_ONLY_NOT_KERNEL_ENFORCED"
}
```

`status` is derived: `MECHANICAL_PASS` only when every allowlisted command returns zero, the source checksum inventory is valid before copying, the isolated copy matches it before and after the commands, the authoritative source tree is unchanged before receipt writing, and all 57 manuscript-source hashes resolve. Otherwise it is `MECHANICAL_FAIL`.

The receipt must additionally record:

- SHA-256 of `SHA256SUMS`, `PACKAGE_MANIFEST.md`, `research-case/program-state.json`, and `research-case/07-manuscript/source-manifest.json`;
- exact inventoried-file count;
- source-tree checksum verification before copy and after execution but before receipt writing;
- isolated-copy checksum verification before and after execution;
- Python, uv, Forge, and platform versions;
- for every command: stable command ID, argv array, relative working directory, return code, stdout/stderr relative paths and SHA-256 values;
- `source_manifest_sources_verified` and its exact count;
- the residual limitations: same host, same tool caches, no external operator identity binding, tool flags rather than kernel-enforced network isolation, no scientific independence, no distributed deadline execution, and no venue or institutional approval.

The receipt and logs may not contain environment variable values, credentials, home-directory dumps, secrets, or network responses.

## Frozen command plan

Every command runs inside the temporary copy. The environment sets `UV_OFFLINE=1`, `CARGO_NET_OFFLINE=true`, `FOUNDRY_OFFLINE=true`, `NO_COLOR=1`, `PYTHONDONTWRITEBYTECODE=1`, and `PYTEST_ADDOPTS=-p no:cacheprovider`. Existing environment variables are not serialized into the receipt. The first fresh execution failed closed because the harness still emitted `FOUNDRY_OFFLINE=1`; that failure receipt is preserved at `prototype/results/engineering_qa/isolated_reproduction_failure_20260830T044840Z/`, and the harness remediation must use Foundry's accepted boolean spelling `true`.

| Command ID | Relative cwd | argv |
| --- | --- | --- |
| `deadline_package_check` | `.` | `python3 scripts/export_deadline_pilot_start_package.py --check` |
| `t1_t8_check` | `.` | `python3 scripts/export_t1_t8_tables.py --check` |
| `paper_tables_check` | `.` | `python3 scripts/export_paper_tables.py --check` |
| `python_suite` | `prototype` | `uv run --offline --locked --extra dev pytest -q -p no:cacheprovider` |
| `foundry_test` | `.` | `forge test --root contracts --offline` |
| `gas_snapshot_check` | `.` | `forge snapshot --root contracts --offline --match-test ^testGas_ --check .gas-snapshot` |
| `gas_report_check` | `.` | `python3 contracts/scripts/export_gas_snapshot.py --check .gas-snapshot contracts/gas_report.csv` |
| `test_vectors_check` | `prototype` | `uv run --offline --locked --extra dev python scripts/export_test_vectors.py --check` |
| `signature_vectors_check` | `prototype` | `uv run --offline --locked --extra dev python scripts/export_signature_vectors.py --check` |
| `strict_research_case` | `.` | `python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/check_research_case.py research-case --strict` |

The absolute checker path is recorded as a same-host external-tool dependency, not a package-contained verifier.

## Task 1: RED receipt and inventory tests

**Files:**
- Create `prototype/tests/test_isolated_mechanical_reproduction.py`

- [ ] Write an import fixture for the nonexistent harness and observe `FileNotFoundError` with `python3 -m pytest prototype/tests/test_isolated_mechanical_reproduction.py -q`.
- [ ] Add a real temporary-fixture test whose checksum file contains two files and requires exact parsing, duplicate-path rejection, missing-file rejection, and hash-mismatch rejection.
- [ ] Add a real subprocess test using `python3 -c "print('fixture-ok')"` that requires captured stdout/stderr files, zero return code, and matching hashes.
- [ ] Add a failing-subprocess test using `python3 -c "raise SystemExit(7)"` that requires receipt status `MECHANICAL_FAIL` and no later command execution.

## Task 2: GREEN minimal harness

**Files:**
- Create `scripts/run_isolated_mechanical_reproduction.py`
- Modify `prototype/tests/test_isolated_mechanical_reproduction.py`

- [ ] Implement strict checksum parsing for lines shaped as 64 lowercase hexadecimal characters, two spaces, then `./relative/path`; reject absolute paths, `..`, duplicate paths, missing files, and paths outside the project root.
- [ ] Copy only checksum-inventoried files plus `SHA256SUMS` into a `tempfile.TemporaryDirectory`; never invoke shell strings and never copy `.git`, virtual environments, caches, Foundry output, OS metadata, or the runtime lock.
- [ ] Implement immutable command specifications and argv-only `subprocess.run` with `shell=False`, captured text output, and the frozen non-secret environment overrides.
- [ ] Stop on the first non-zero command and preserve its logs and return code.
- [ ] Verify all manifest source IDs are unique and every source path/hash resolves according to `path_base`; require exactly the manifest count rather than a hard-coded 57 so later legitimate additions remain checkable.
- [ ] Derive receipt status from checks rather than accepting it as a caller input.

## Task 3: RED/GREEN security and tamper boundaries

**Files:**
- Modify `prototype/tests/test_isolated_mechanical_reproduction.py`
- Modify `scripts/run_isolated_mechanical_reproduction.py`

- [ ] Add a RED test that inserts `../escape` into a checksum fixture and require rejection before copy.
- [ ] Add a RED test that changes an inventoried source during command execution and require `MECHANICAL_FAIL` plus `source_tree_unchanged=false`.
- [ ] Add a RED test that tampers with `receipt.json`, rebinds no sidecar, and requires `--check-receipt` to fail.
- [ ] Add a RED test that checks receipt/log text for credential-looking environment values supplied to the parent process; require the values not to appear.
- [ ] Implement the smallest fixes, run focused tests, and require no production-code bare `assert`, unsafe `shell=True`, or command strings.

## Task 4: CLI and dry-run contract

**Files:**
- Modify `prototype/tests/test_isolated_mechanical_reproduction.py`
- Modify `scripts/run_isolated_mechanical_reproduction.py`

- [ ] Add mutually exclusive `--execute`, `--dry-run`, and `--check-receipt` modes; default is `--dry-run` so execution is never accidental.
- [ ] `--dry-run` validates sources and prints the ten command IDs without copying or running them and without creating outputs.
- [ ] `--execute --output-dir <path>` requires an output directory inside the declared project root and writes logs, receipt, and sidecar only after the isolated run.
- [ ] `--check-receipt --output-dir <path>` verifies sidecar, receipt schema/constants, every declared log hash, and receipt status without rerunning commands.
- [ ] Catch operational validation/IO/JSON/subprocess errors in `main()`, emit one concise `error: ...` line to stderr, return non-zero, and do not mask programmer bugs.

## Task 5: Independent specification and quality review

- [ ] A fresh read-only specification reviewer checks every requirement above and returns only `SPEC_APPROVED` or numbered defects.
- [ ] The implementer remediates defects TDD-first and the same reviewer rechecks.
- [ ] A different fresh read-only quality reviewer audits path traversal, source mutation, environment leakage, subprocess safety, manifest correctness, test strength, and scientific wording, returning only `QUALITY_APPROVED` or numbered defects.

## Task 6: Actual isolated-copy mechanical reproduction

**Write scope:**
- `prototype/results/engineering_qa/isolated_reproduction/**`

- [ ] A fresh reproduction subagent runs `python3 scripts/run_isolated_mechanical_reproduction.py --dry-run` and confirms the ten frozen command IDs.
- [ ] The subagent runs `python3 scripts/run_isolated_mechanical_reproduction.py --execute --output-dir prototype/results/engineering_qa/isolated_reproduction`.
- [ ] The subagent runs `python3 scripts/run_isolated_mechanical_reproduction.py --check-receipt --output-dir prototype/results/engineering_qa/isolated_reproduction`.
- [ ] Accept the receipt only if `status=MECHANICAL_PASS`; otherwise preserve the failure receipt and return to the smallest affected implementation or environment step.

## Task 7: Root integration and final QA

- [ ] Add the plan, harness, tests, receipt, sidecar, and command logs to the manuscript source manifest at explicitly mechanical/preauthorization maturity.
- [ ] Add one manuscript reproducibility paragraph stating exactly what the isolated same-host second-agent rerun established and what it did not establish.
- [ ] Do not change T7 external-validation status, canonical phase, novelty, feasibility, viability, or acceptance readiness.
- [ ] Record changed canonical manuscript/source artifacts as `DRAFT`, refresh package integrity, and verify all source hashes.
- [ ] Run focused tests, full Python suite, Foundry tests, gas snapshot, all package/table/vector checks, strict research-case validation, source-manifest closure, citation closure, checksum verification, and `git diff --check`.

## Self-review result

- Spec coverage: inventory, isolated copy, offline flags, allowlisted execution, logs, receipt, sidecar, source immutability, manuscript integration, and scientific limitations each have an explicit task.
- Placeholder scan: no `TBD`, `TODO`, or implementation placeholder appears. Runtime values such as hashes, tool versions, and command return codes are generated evidence rather than missing plan content.
- Type consistency: receipt constants, command IDs, output paths, and status vocabulary are identical throughout the plan.
- Safety: execution is opt-in; subprocesses use argv arrays and `shell=False`; outputs remain inside a validated project-relative directory; no external sharing or distributed experiment is authorized.
- Commit policy: no commit is requested because the worktree contains extensive user-owned uncommitted research work.
