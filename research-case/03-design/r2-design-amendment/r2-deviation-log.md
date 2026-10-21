# KEYSTONE R2 deviation log

Frozen design: `r2-design-freeze.json` (SHA-256 in `r2-design-freeze.SHA256SUMS`).
Entries are append-only. Times are UTC.

| # | Time | Family | Deviation | Reason | Effect on claims |
|---|---|---|---|---|---|
| 1 | 2026-10-21T15:58:43Z | D1 (library choice, pre-run) | D1 resolved: rbcl 1.1.2 + barriers 1.2.0, conditional pass of the static review in D1-SUPPLY-CHAIN-REVIEW.md | Required by decision D1 of the freeze (choice recorded here) | None on claims; six usage conditions added (pinned wheel, embedded-library hash test, own point validation, no ed25519 API, linearity tests before measurement, temp-file cleanup) |
| 2 | 2026-10-21T16:05:42Z | R2_CORRECTNESS (environment, pre-measurement) | R2 code and its dependencies (rbcl, barriers) live in a separate locked sub-project prototype/r2/ instead of prototype/pyproject.toml | Adding rbcl to the main project changed prototype/pyproject.toml and uv.lock, which the original experiment manifest pins as inputs; a bare regeneration does not reproduce the committed accessible SVGs, so rehashing would have misstated provenance. The committed results were restored unchanged | None on claims; R1 and earlier provenance stays byte-identical; R2 has its own lockfile with the reviewed wheel hashes |
