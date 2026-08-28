#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
python -m keystone.cli demo
python -m keystone.cli bound --n 32 --threshold 22 --sample-size 8
python -m keystone.cli simulate --config configs/baseline.json --output results/baseline.json
python scripts/run_experiments.py
python scripts/benchmark_crypto.py
pytest
