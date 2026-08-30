# KEYSTONE Python Minimum Publishable Prototype

## Requirements

- Python 3.11 or newer
- `cryptography`, `matplotlib`, and `pytest`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Run everything

```bash
./scripts/run_baseline.sh
```

This executes:

1. an end-to-end encrypted-record demo;
2. the frozen `n=32,t=22,s=8,q=8` analytical bound;
3. baseline Monte Carlo scenarios;
4. CSV/SVG/PNG figure generation;
5. cryptographic microbenchmarks;
6. all 35 tests, including exact stratified-distribution, Wilson-interval,
   canonical transcript, Ed25519 signature/golden-vector, and experimental
   share-refresh generation oracles.

## Individual commands

```bash
keystone demo
keystone bound --n 32 --threshold 22 --sample-size 8 --required-valid 8
keystone simulate --config configs/baseline.json --output results/baseline.json
python scripts/run_experiments.py
python scripts/benchmark_crypto.py
pytest -q
```

## What the cryptographic demo implements

- dealer-based Shamir shares with Feldman commitments;
- dealer-based zero-polynomial share refresh for controlled experiments only;
- public per-member share commitments;
- deterministic beacon/context-derived hash-to-group canaries;
- Chaum–Pedersen/DLEQ proofs of equal discrete logs;
- threshold DH KEM wrapping a random AES-256 record key;
- AES-GCM record encryption and authenticated opening;
- invalid-partial and non-response evidence objects;
- separate audit and target-dispute behavior for selective withholding.

## What it deliberately does not implement

- production DKG/PVSS or proactive resharing;
- standardized curve/library-grade threshold cryptography;
- network transport, production key management, stake, or a TEE;
- proof that audit success guarantees future dispute cooperation;
- security against `t` compromised shares;
- cryptographic audit or production hardening.

## Result files

- `results/baseline.json` — baseline scenarios;
- `results/*.csv` — plot-ready data;
- `results/figures/*.{svg,png}` — paper-oriented figures;
- `results/crypto_benchmark.csv` — local single-process timings;
- `results/experiment_manifest.json` — frozen parameters/seeds.

All reported performance numbers are environment-specific research baselines, not production capacity claims.
The Ed25519 response-signature helper signs the exact canonical transcript bytes;
its fixed-seed vector is test-only interoperability data, not secure key generation.
