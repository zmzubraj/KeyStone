SHELL := /bin/bash

PYTHON_VERSION ?= 3.13

.PHONY: setup test-python test-contract build-contract snapshot snapshot-check reproduce checksums verify clean

setup:
	cd prototype && uv sync --locked --extra dev --python "$(PYTHON_VERSION)"

test-python:
	cd prototype && uv run --locked --extra dev pytest -q

build-contract:
	forge build --root contracts

test-contract:
	forge test --root contracts

snapshot:
	forge snapshot --root contracts --snap .gas-snapshot

snapshot-check:
	forge snapshot --root contracts --check .gas-snapshot

reproduce:
	cd prototype && uv run --locked --extra dev ./scripts/run_baseline.sh

checksums:
	LC_ALL=C LANG=C shasum -a 256 -c SHA256SUMS

verify: test-python build-contract test-contract snapshot-check checksums

clean:
	cd prototype && rm -rf .pytest_cache src/keystone_mpp.egg-info
	forge clean --root contracts
