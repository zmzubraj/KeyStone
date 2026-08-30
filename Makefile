SHELL := /bin/bash

PYTHON_VERSION ?= 3.13
GAS_TEST_PATTERN ?= ^testGas_

.PHONY: setup test-python test-contract build-contract snapshot snapshot-check reproduce paper-tables paper-tables-check test-vectors test-vectors-check signature-vectors signature-vectors-check intake-verifier-packet intake-verifier-packet-check intake-review-bundle intake-review-bundle-check intake-verifier-return-template intake-verifier-return-template-check pc02-novelty-verifier-packet pc02-novelty-verifier-packet-check pc03-design-amendment pc03-design-amendment-check pc03-methods-verifier-packet pc03-methods-verifier-packet-check draft-adversarial-reviews draft-adversarial-reviews-check manuscript-source-check manuscript-alignment-check manuscript-assembly-inventory manuscript-assembly-inventory-check draft-manuscript draft-manuscript-check acceptance-readiness-gap acceptance-readiness-gap-check evidence-lineage evidence-lineage-check exploratory-findings exploratory-findings-check primary-results-contract primary-results-contract-check negative-findings negative-findings-check robustness-boundaries robustness-boundaries-check confirmatory-pilot-plan confirmatory-pilot-plan-check refresh-integrity checksums verify clean

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

intake-verifier-return-template:
	python3 scripts/intake_verifier_return_contract.py

intake-verifier-return-template-check:
	python3 scripts/intake_verifier_return_contract.py --check

pc02-novelty-verifier-packet:
	python3 scripts/export_pc02_novelty_verifier_packet.py

pc02-novelty-verifier-packet-check:
	python3 scripts/export_pc02_novelty_verifier_packet.py --check

pc03-design-amendment:
	python3 scripts/export_pc03_design_amendment.py

pc03-design-amendment-check:
	python3 scripts/export_pc03_design_amendment.py --check

pc03-methods-verifier-packet:
	python3 scripts/export_pc03_methods_verifier_packet.py

pc03-methods-verifier-packet-check:
	python3 scripts/export_pc03_methods_verifier_packet.py --check

draft-adversarial-reviews:
	python3 scripts/export_draft_adversarial_reviews.py

draft-adversarial-reviews-check:
	python3 scripts/export_draft_adversarial_reviews.py --check

manuscript-source-check:
	python3 scripts/run_isolated_mechanical_reproduction.py --dry-run

manuscript-alignment-check:
	python3 scripts/check_manuscript_alignment.py

manuscript-assembly-inventory:
	python3 scripts/export_manuscript_assembly_inventory.py

manuscript-assembly-inventory-check:
	python3 scripts/export_manuscript_assembly_inventory.py --check

draft-manuscript:
	python3 scripts/build_draft_manuscript.py

draft-manuscript-check:
	python3 scripts/build_draft_manuscript.py --check

acceptance-readiness-gap:
	python3 scripts/export_acceptance_readiness_gap_report.py

acceptance-readiness-gap-check:
	python3 scripts/export_acceptance_readiness_gap_report.py --check

evidence-lineage:
	python3 scripts/export_evidence_lineage.py

evidence-lineage-check:
	python3 scripts/export_evidence_lineage.py --check

exploratory-findings:
	python3 scripts/export_exploratory_findings.py

exploratory-findings-check:
	python3 scripts/export_exploratory_findings.py --check

primary-results-contract:
	python3 scripts/export_primary_results_contract.py

primary-results-contract-check:
	python3 scripts/export_primary_results_contract.py --check

negative-findings:
	python3 scripts/export_negative_findings.py

negative-findings-check:
	python3 scripts/export_negative_findings.py --check

robustness-boundaries:
	python3 scripts/export_robustness_boundaries.py

robustness-boundaries-check:
	python3 scripts/export_robustness_boundaries.py --check

confirmatory-pilot-plan:
	python3 scripts/export_confirmatory_pilot_plan.py

confirmatory-pilot-plan-check:
	python3 scripts/export_confirmatory_pilot_plan.py --check

refresh-integrity:
	python3 scripts/update_package_integrity.py

checksums:
	LC_ALL=C LANG=C shasum -a 256 -c SHA256SUMS

verify: test-python build-contract test-contract snapshot-check paper-tables-check test-vectors-check signature-vectors-check intake-verifier-packet-check intake-review-bundle-check intake-verifier-return-template-check pc02-novelty-verifier-packet-check pc03-design-amendment-check pc03-methods-verifier-packet-check draft-adversarial-reviews-check manuscript-source-check manuscript-alignment-check manuscript-assembly-inventory-check draft-manuscript-check acceptance-readiness-gap-check evidence-lineage-check exploratory-findings-check primary-results-contract-check negative-findings-check robustness-boundaries-check confirmatory-pilot-plan-check checksums

clean:
	cd prototype && rm -rf .pytest_cache src/keystone_mpp.egg-info
	forge clean --root contracts
