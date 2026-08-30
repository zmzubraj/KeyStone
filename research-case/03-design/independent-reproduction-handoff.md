# KEYSTONE independent reproduction handoff

Status: `DRAFT_PREAUTHORIZATION`
System: `KEYSTONE-MPP-F1`
Current canonical phase: `INTAKE`

This handoff defines a mechanical rerun of the deadline-pilot start package on
a clean checkout or isolated copy. Same-author rerun is not independent
scientific verification.

## Preconditions

- use a clean checkout or isolated copy
- preserve the authoritative inputs as read-only
- do not enable network access for the mechanical rerun unless separately
  authorized by the accountable human

## Required commands

- `python3 scripts/export_deadline_pilot_start_package.py --check`
- `python3 -m pytest prototype/tests/test_deadline_pilot_start_package.py -q`
- `cd prototype && uv run --locked --extra dev pytest -q`
- `forge test --root contracts`
- `python3 scripts/export_t1_t8_tables.py --check`
- verify the canonical source-manifest entry and verification state in the canonical integration workflow
- verify the canonical checksum records in the canonical integration workflow

## Expected mechanical evidence

Return the package manifest and report with:

- commands executed
- tool versions
- output hashes
- deviations
- residual risks

## Boundaries

- external sharing of the bundle requires accountable human approval
- the rerun may establish mechanical consistency only
- the rerun may not be labeled independent scientific verification
