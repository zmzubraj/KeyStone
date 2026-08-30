SHELL := /bin/bash

PYTHON_VERSION ?= 3.13
GAS_TEST_PATTERN ?= ^testGas_

.PHONY: setup test-python test-contract build-contract snapshot snapshot-check reproduce paper-tables paper-tables-check test-vectors test-vectors-check signature-vectors signature-vectors-check intake-verifier-packet intake-verifier-packet-check intake-review-bundle intake-review-bundle-check manuscript-source-check manuscript-alignment-check refresh-integrity checksums verify clean

setup:
	cd prototype && uv sync --locked --extra dev --python "$(PYTHON_VERSION)"

test-python:
	cd prototype && uv run --locked --extra dev pytest -q

build-contract:
	forge build --root contracts

test-contract:
	forge test --root contracts

snapshot:
	forge snapshot --root contracts --match-test '$(GAS_TEST_PATTERN)' --snap .gas-snapshot
	python3 contracts/scripts/export_gas_snapshot.py .gas-snapshot contracts/gas_report.csv

snapshot-check:
	forge snapshot --root contracts --match-test '$(GAS_TEST_PATTERN)' --check .gas-snapshot
	python3 contracts/scripts/export_gas_snapshot.py --check .gas-snapshot contracts/gas_report.csv

reproduce:
	cd prototype && uv run --locked --extra dev ./scripts/run_baseline.sh
	python3 scripts/export_paper_tables.py
	cd prototype && uv run --locked --extra dev python scripts/export_test_vectors.py
	cd prototype && uv run --locked --extra dev python scripts/export_signature_vectors.py

paper-tables:
	python3 scripts/export_paper_tables.py

paper-tables-check:
	python3 scripts/export_paper_tables.py --check

test-vectors:
	cd prototype && uv run --locked --extra dev python scripts/export_test_vectors.py

test-vectors-check:
	cd prototype && uv run --locked --extra dev python scripts/export_test_vectors.py --check

signature-vectors:
	cd prototype && uv run --locked --extra dev python scripts/export_signature_vectors.py

signature-vectors-check:
	cd prototype && uv run --locked --extra dev python scripts/export_signature_vectors.py --check

intake-verifier-packet:
	python3 scripts/export_intake_verifier_packet.py

intake-verifier-packet-check:
	python3 scripts/export_intake_verifier_packet.py --check

intake-review-bundle:
	python3 scripts/export_intake_review_bundle.py

intake-review-bundle-check:
	python3 scripts/export_intake_review_bundle.py --check

manuscript-source-check:
	python3 scripts/run_isolated_mechanical_reproduction.py --dry-run

manuscript-alignment-check:
	python3 scripts/check_manuscript_alignment.py

refresh-integrity:
	python3 scripts/update_package_integrity.py

checksums:
	LC_ALL=C LANG=C shasum -a 256 -c SHA256SUMS

verify: test-python build-contract test-contract snapshot-check paper-tables-check test-vectors-check signature-vectors-check intake-verifier-packet-check intake-review-bundle-check manuscript-source-check manuscript-alignment-check checksums

clean:
	cd prototype && rm -rf .pytest_cache src/keystone_mpp.egg-info
	forge clean --root contracts
