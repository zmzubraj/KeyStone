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
checks the Foundry gas snapshot, and verifies the checked-in SHA-256 manifest.

## Full research reproduction

```bash
make reproduce
make snapshot
```

`make reproduce` regenerates the Python demo, analytical result, simulations,
figures, benchmarks, and tests. Because it intentionally rewrites result
artifacts, refresh `VERIFICATION.md`, `ENVIRONMENT.txt`, `PACKAGE_MANIFEST.md`,
and `SHA256SUMS` only after reviewing the new evidence.

## Workspace boundaries

- Do not use the prototype for production funds or sensitive data.
- Do not claim primitive-level novelty or unconditional future availability.
- Keep generated Python environments and Foundry build artifacts untracked.
- Preserve datasets, figures, manifests, and verification records that support
  paper claims.
