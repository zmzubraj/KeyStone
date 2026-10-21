# KEYSTONE R2 deviation log

Frozen design: `r2-design-freeze.json` (SHA-256 in `r2-design-freeze.SHA256SUMS`).
Entries are append-only. Times are UTC.

| # | Time | Family | Deviation | Reason | Effect on claims |
|---|---|---|---|---|---|
| 1 | 2026-10-21T15:58:43Z | D1 (library choice, pre-run) | D1 resolved: rbcl 1.1.2 + barriers 1.2.0, conditional pass of the static review in D1-SUPPLY-CHAIN-REVIEW.md | Required by decision D1 of the freeze (choice recorded here) | None on claims; six usage conditions added (pinned wheel, embedded-library hash test, own point validation, no ed25519 API, linearity tests before measurement, temp-file cleanup) |
