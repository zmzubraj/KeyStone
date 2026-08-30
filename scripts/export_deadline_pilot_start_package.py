#!/usr/bin/env python3
"""Export the bounded KEYSTONE deadline-pilot start package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PACKAGE_CONSTANTS = {
    "schema_id": "KEYSTONE_DEADLINE_PILOT_START_PACKAGE",
    "schema_version": 1,
    "status": "DRAFT_PREAUTHORIZATION",
    "execution_authorization": "NOT_AUTHORIZED",
    "canonical_phase": "INTAKE",
    "scientific_evidence_boundary": "DESIGN_ONLY_NOT_CONFIRMATORY_EVIDENCE",
    "result_id": "RID-C003-DEADLINE-001",
    "claim_ids": "C002|C003",
    "author_metadata_freeze": "DEFERRED_BY_ACCOUNTABLE_HUMAN",
}

CANONICAL_OUTPUT_DIR = "research-case/03-design"
MANIFEST_FILENAME = "deadline-pilot-start-package-manifest.json"
MANIFEST_SIDECAR_FILENAME = "deadline-pilot-start-package-manifest.json.sha256"
UNRESOLVED_LITERAL = "UNRESOLVED_BEFORE_EXECUTION"

INPUT_PATHS = (
    "research-case/program-state.json",
    "research-case/00-governance/accountable-authority-confirmation.md",
    "research-case/03-design/protocol.md",
    "research-case/03-design/analysis-plan.md",
    "research-case/03-design/power-or-precision.md",
)

OUTPUT_FILES = (
    "deadline-environment-profiles.csv",
    "t5-ablation-run-matrix.csv",
    "deadline-pilot-execution-contract.md",
    "independent-reproduction-handoff.md",
    MANIFEST_FILENAME,
    MANIFEST_SIDECAR_FILENAME,
)

CONTENT_OUTPUT_FILES = OUTPUT_FILES[:4]

ENVIRONMENT_HEADER = (
    "profile_id",
    "profile_role",
    "process_count",
    "failure_domain_count",
    "host_topology",
    "run_day_block",
    "network_latency_profile",
    "packet_loss_profile",
    "crash_profile",
    "synchrony_assumption",
    "deadline_interpretation",
    "trace_denominator",
    "precision_target",
    "multiplicity_rule",
    "execution_status",
    "result_id",
    "claim_ids",
    "source_path",
    "claim_ceiling",
)

ABLATION_HEADER = (
    "ablation_id",
    "treatment",
    "control",
    "mechanism_question",
    "paired_seed_policy",
    "blocking_factors",
    "required_endpoint",
    "execution_status",
    "result_id",
    "claim_ids",
    "source_path",
    "claim_ceiling",
)

EXPECTED_ENVIRONMENT_IDS = (
    "ENV-DEADLINE-CONTROL-001",
    "ENV-DEADLINE-LATENCY-001",
    "ENV-DEADLINE-LOSS-001",
    "ENV-DEADLINE-CRASH-001",
)

EXPECTED_ABLATION_IDS = (
    "ABL-CANARY-001",
    "ABL-STRAT-001",
    "ABL-DOMAIN-001",
    "ABL-TEMPORAL-001",
)

ALLOWED_ABLATION_RESULT_IDS = {
    "ABL-CANARY-001": "RID-C003-DEADLINE-001",
    "ABL-STRAT-001": "RID-C003-STRAT-001",
    "ABL-DOMAIN-001": "RID-C003-CORR-001",
    "ABL-TEMPORAL-001": "RID-C003-IID-001",
}

PROTOCOL_REQUIRED_SNIPPETS = (
    "RID-C003-DEADLINE-001",
    "one complete end-to-end distributed trace per seed and environment profile",
    "future synthetic distributed benchmark under declared synchrony assumptions",
    "multi-host numeric latency or loss levels remain unresolved pending power/precision and authority",
)

ANALYSIS_REQUIRED_SNIPPETS = (
    "`EST-09`",
    "`RID-C003-DEADLINE-001`",
    "one complete distributed trace under one seed and environment profile",
)

POWER_REQUIRED_SNIPPETS = (
    "RID-C003-DEADLINE-001",
    "still needs an accountable environment profile",
    "claim-safe deadline interpretation target",
    "trace denominator",
    "multiplicity rule",
)

AUTHORITY_REQUIRED_SNIPPETS = (
    "Status: `CONFIRMED_DRAFT_AUTHORITY`",
    "Phase: `INTAKE`",
    "current study basis is non-human computational research",
    "The authorship position above is recorded only as the supplied current default.",
    "The complete author list, final author order, corresponding-author designation, affiliation wording, institutional naming, and contact metadata remain deferred and subject to accountable-human and institutional verification before submission.",
    "The canonical program phase nevertheless remains `INTAKE`",
    "does not independently verify novelty, feasibility, study design, scientific evidence, external validation, manuscript readiness, or venue compliance",
    "promotes no scientific or submission gate by itself.",
)


class PackageValidationError(ValueError):
    """Raised when a source or generated package artifact violates the boundary."""


@dataclass(frozen=True)
class EnvironmentProfile:
    profile_id: str
    profile_role: str
    host_topology: str
    run_day_block: str
    synchrony_assumption: str
    source_path: str
    claim_ceiling: str = "ASSERTED_ONLY"

    def as_row(self) -> dict[str, str]:
        return {
            "profile_id": self.profile_id,
            "profile_role": self.profile_role,
            "process_count": "32",
            "failure_domain_count": "4",
            "host_topology": self.host_topology,
            "run_day_block": self.run_day_block,
            "network_latency_profile": UNRESOLVED_LITERAL,
            "packet_loss_profile": UNRESOLVED_LITERAL,
            "crash_profile": UNRESOLVED_LITERAL,
            "synchrony_assumption": self.synchrony_assumption,
            "deadline_interpretation": UNRESOLVED_LITERAL,
            "trace_denominator": UNRESOLVED_LITERAL,
            "precision_target": UNRESOLVED_LITERAL,
            "multiplicity_rule": UNRESOLVED_LITERAL,
            "execution_status": "BLOCKED_UNRESOLVED_DESIGN",
            "result_id": PACKAGE_CONSTANTS["result_id"],
            "claim_ids": PACKAGE_CONSTANTS["claim_ids"],
            "source_path": self.source_path,
            "claim_ceiling": self.claim_ceiling,
        }


@dataclass(frozen=True)
class AblationRow:
    ablation_id: str
    treatment: str
    control: str
    mechanism_question: str
    paired_seed_policy: str
    blocking_factors: str
    required_endpoint: str
    source_path: str
    claim_ceiling: str = "ASSERTED_ONLY"

    def as_row(self) -> dict[str, str]:
        return {
            "ablation_id": self.ablation_id,
            "treatment": self.treatment,
            "control": self.control,
            "mechanism_question": self.mechanism_question,
            "paired_seed_policy": self.paired_seed_policy,
            "blocking_factors": self.blocking_factors,
            "required_endpoint": self.required_endpoint,
            "execution_status": "DESIGN_ONLY_NOT_EXECUTED",
            "result_id": ALLOWED_ABLATION_RESULT_IDS[self.ablation_id],
            "claim_ids": PACKAGE_CONSTANTS["claim_ids"],
            "source_path": self.source_path,
            "claim_ceiling": self.claim_ceiling,
        }


@dataclass(frozen=True)
class DeadlinePilotPackage:
    environment_rows: tuple[dict[str, str], ...]
    ablation_rows: tuple[dict[str, str], ...]
    markdown_documents: dict[str, str]
    manifest_payload: dict[str, object]


ENVIRONMENT_PROFILES = (
    EnvironmentProfile(
        profile_id="ENV-DEADLINE-CONTROL-001",
        profile_role="non-adversarial control",
        host_topology="DECLARED_MULTI_HOST_CONTROL_ROLE_ONLY",
        run_day_block=UNRESOLVED_LITERAL,
        synchrony_assumption="DECLARED_SYNTHETIC_CONDITIONAL_SYNCHRONY_PENDING_FREEZE",
        source_path="research-case/03-design/protocol.md; research-case/03-design/power-or-precision.md",
    ),
    EnvironmentProfile(
        profile_id="ENV-DEADLINE-LATENCY-001",
        profile_role="controlled latency injection",
        host_topology="DECLARED_MULTI_HOST_LATENCY_ROLE_ONLY",
        run_day_block=UNRESOLVED_LITERAL,
        synchrony_assumption="DECLARED_SYNTHETIC_CONDITIONAL_SYNCHRONY_PENDING_FREEZE",
        source_path="research-case/03-design/protocol.md; research-case/03-design/power-or-precision.md",
    ),
    EnvironmentProfile(
        profile_id="ENV-DEADLINE-LOSS-001",
        profile_role="controlled packet-loss injection",
        host_topology="DECLARED_MULTI_HOST_LOSS_ROLE_ONLY",
        run_day_block=UNRESOLVED_LITERAL,
        synchrony_assumption="DECLARED_SYNTHETIC_CONDITIONAL_SYNCHRONY_PENDING_FREEZE",
        source_path="research-case/03-design/protocol.md; research-case/03-design/power-or-precision.md",
    ),
    EnvironmentProfile(
        profile_id="ENV-DEADLINE-CRASH-001",
        profile_role="controlled crash injection",
        host_topology="DECLARED_MULTI_HOST_CRASH_ROLE_ONLY",
        run_day_block=UNRESOLVED_LITERAL,
        synchrony_assumption="DECLARED_SYNTHETIC_CONDITIONAL_SYNCHRONY_PENDING_FREEZE",
        source_path="research-case/03-design/protocol.md; research-case/03-design/power-or-precision.md",
    ),
)

ABLATION_ROWS = (
    AblationRow(
        ablation_id="ABL-CANARY-001",
        treatment="canary readiness audit",
        control="no canary readiness audit",
        mechanism_question="Does the readiness audit contribute distinct evidence before the deadline trace is interpreted?",
        paired_seed_policy="MATCHED_SEED_WITHIN_ENVIRONMENT_PROFILE",
        blocking_factors="environment profile; host topology; run day; seed block",
        required_endpoint="EP-04",
        source_path="research-case/03-design/analysis-plan.md",
    ),
    AblationRow(
        ablation_id="ABL-STRAT-001",
        treatment="fixed-quota stratified sampling",
        control="uniform sampling",
        mechanism_question="Does the fixed-quota stratified design change the seed-level readiness comparison under matched total draws?",
        paired_seed_policy="MATCHED_SEED_PAIR_PER_SEMANTIC_CELL",
        blocking_factors="scenario family; draw semantics; seed block",
        required_endpoint="secondary support for readiness interpretation",
        source_path="research-case/03-design/analysis-plan.md",
    ),
    AblationRow(
        ablation_id="ABL-DOMAIN-001",
        treatment="failure-domain-aware analysis",
        control="domain labels removed",
        mechanism_question="Do truthful failure-domain labels materially change the correlated-outage interpretation?",
        paired_seed_policy="MATCHED_SEED_WITH_DOMAIN_LABEL_TOGGLE",
        blocking_factors="domain-label source; placement policy; config revision; seed block",
        required_endpoint="secondary support for readiness interpretation",
        source_path="research-case/03-design/analysis-plan.md",
    ),
    AblationRow(
        ablation_id="ABL-TEMPORAL-001",
        treatment="Markov temporal dependence",
        control="static IID availability",
        mechanism_question="Would temporal dependence alter the claim-safe interpretation relative to the static IID family without creating a new confirmatory result?",
        paired_seed_policy="MATCHED_SEED_WITH_TEMPORAL_TOGGLE",
        blocking_factors="temporal model; environment profile; seed block",
        required_endpoint="secondary support for readiness interpretation",
        source_path="research-case/03-design/analysis-plan.md",
    ),
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _read_text(project_root: Path, relative: str) -> str:
    try:
        return (project_root / relative).read_text(encoding="utf-8")
    except OSError as exc:
        raise PackageValidationError(f"{relative}: unreadable text source: {exc}") from exc


def _read_json(project_root: Path, relative: str) -> object:
    try:
        return json.loads((project_root / relative).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PackageValidationError(f"{relative}: invalid JSON source: {exc}") from exc


def _require_snippets(text: str, relative: str, snippets: Iterable[str]) -> None:
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        raise PackageValidationError(
            f"{relative}: missing required boundary text: {missing[0]!r}"
        )


def _validate_program_state(project_root: Path) -> None:
    relative = "research-case/program-state.json"
    data = _read_json(project_root, relative)
    if not isinstance(data, dict):
        raise PackageValidationError(f"{relative}: expected JSON object")
    expected = {
        "current_phase": "INTAKE",
        "resume_from": "INTAKE",
        "novelty_status": "UNRESOLVED",
        "feasibility_decision": "UNASSESSED",
        "solution_viability_status": "ASSERTED_ONLY",
        "acceptance_readiness": "NOT_ASSESSABLE",
    }
    for field, value in expected.items():
        if data.get(field) != value:
            raise PackageValidationError(
                f"{relative}: boundary drift for {field}; expected {value!r}"
            )


def _validate_authority_confirmation(project_root: Path) -> None:
    relative = "research-case/00-governance/accountable-authority-confirmation.md"
    _require_snippets(_read_text(project_root, relative), relative, AUTHORITY_REQUIRED_SNIPPETS)


def _validate_design_sources(project_root: Path) -> None:
    protocol_relative = "research-case/03-design/protocol.md"
    analysis_relative = "research-case/03-design/analysis-plan.md"
    power_relative = "research-case/03-design/power-or-precision.md"
    _require_snippets(_read_text(project_root, protocol_relative), protocol_relative, PROTOCOL_REQUIRED_SNIPPETS)
    _require_snippets(_read_text(project_root, analysis_relative), analysis_relative, ANALYSIS_REQUIRED_SNIPPETS)
    _require_snippets(_read_text(project_root, power_relative), power_relative, POWER_REQUIRED_SNIPPETS)


def validate_environment_rows(rows: Iterable[dict[str, str]]) -> tuple[dict[str, str], ...]:
    normalized = tuple(rows)
    if tuple(row.get("profile_id", "") for row in normalized) != EXPECTED_ENVIRONMENT_IDS:
        raise PackageValidationError("environment profile ID drift")
    required_unresolved_fields = (
        "run_day_block",
        "network_latency_profile",
        "packet_loss_profile",
        "crash_profile",
        "deadline_interpretation",
        "trace_denominator",
        "precision_target",
        "multiplicity_rule",
    )
    for row in normalized:
        if tuple(row) != ENVIRONMENT_HEADER:
            raise PackageValidationError("deadline-environment-profiles.csv: header drift")
        if row["process_count"] != "32":
            raise PackageValidationError("deadline-environment-profiles.csv: process_count drift")
        if row["failure_domain_count"] != "4":
            raise PackageValidationError("deadline-environment-profiles.csv: failure_domain_count drift")
        if row["execution_status"] != "BLOCKED_UNRESOLVED_DESIGN":
            raise PackageValidationError("deadline-environment-profiles.csv: execution_status drift")
        if row["result_id"] != PACKAGE_CONSTANTS["result_id"]:
            raise PackageValidationError("deadline-environment-profiles.csv: result_id drift")
        if row["claim_ids"] != PACKAGE_CONSTANTS["claim_ids"]:
            raise PackageValidationError("deadline-environment-profiles.csv: claim_ids drift")
        if not row["source_path"].strip():
            raise PackageValidationError("deadline-environment-profiles.csv: missing source_path")
        for field in required_unresolved_fields:
            if row[field] != UNRESOLVED_LITERAL:
                raise PackageValidationError(
                    f"deadline-environment-profiles.csv: resolved numeric execution choice in {field}"
                )
    return normalized


def validate_ablation_rows(rows: Iterable[dict[str, str]]) -> tuple[dict[str, str], ...]:
    normalized = tuple(rows)
    if tuple(row.get("ablation_id", "") for row in normalized) != EXPECTED_ABLATION_IDS:
        raise PackageValidationError("t5-ablation-run-matrix.csv: ablation ID drift")
    for row in normalized:
        if tuple(row) != ABLATION_HEADER:
            raise PackageValidationError("t5-ablation-run-matrix.csv: header drift")
        ablation_id = row["ablation_id"]
        if row["execution_status"] != "DESIGN_ONLY_NOT_EXECUTED":
            raise PackageValidationError("t5-ablation-run-matrix.csv: execution_status drift")
        if row["result_id"] != ALLOWED_ABLATION_RESULT_IDS[ablation_id]:
            raise PackageValidationError("t5-ablation-run-matrix.csv: result mapping drift")
        if row["claim_ids"] != PACKAGE_CONSTANTS["claim_ids"]:
            raise PackageValidationError("t5-ablation-run-matrix.csv: claim_ids drift")
        if not row["source_path"].strip():
            raise PackageValidationError("t5-ablation-run-matrix.csv: missing source_path")
    return normalized


def _render_execution_contract() -> str:
    return """# KEYSTONE deadline-pilot execution contract

Status: `DRAFT_PREAUTHORIZATION`
System: `KEYSTONE-MPP-F1`
Result ID: `RID-C003-DEADLINE-001`
Current canonical phase: `INTAKE`
Execution authorization: `NOT_AUTHORIZED`
Scientific evidence boundary: design-only and not confirmatory evidence

This contract freezes the design-only boundary for the deadline pilot package.
It does not authorize any distributed run.

## Replicate definition

A replicate is one complete end-to-end distributed trace per seed and
environment profile. Events inside a trace are nested observations and are not
replicates.

## Required trace metadata

- seed
- environment profile
- host topology
- run day
- version or commit
- timestamps
- outcome
- failure classification
- artifact hashes

## Blocking factors

- the environment profile remains unresolved before execution
- the deadline interpretation remains unresolved before execution
- the trace denominator remains unresolved before execution
- the precision target remains unresolved before execution
- the multiplicity rule remains unresolved before execution
- novelty, accountable approval, and independent verification remain open

## Required endpoint and telemetry

The required endpoint is the conditional deadline success measure under the
declared synthetic synchrony model. Telemetry must preserve seed, profile,
topology, run-day block, node outcome, trace outcome, failure class, and output
artifact hashes without backfilling missing fields.

## Forbidden inputs and actions

- production ciphertext
- live secrets
- personal data
- production systems
- unpublished third-party data
- external sharing
- performance inspection before design freeze

## Permitted preauthorization activity

Only integrity and completeness checks are permitted before accountable
authorization. Any attempted distributed execution remains blocked.
"""


def _render_reproduction_handoff() -> str:
    return """# KEYSTONE independent reproduction handoff

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
"""


def _csv_bytes(header: tuple[str, ...], rows: Iterable[dict[str, str]]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=header, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def _manifest_input_records(project_root: Path) -> list[dict[str, str]]:
    return [
        {"path": relative, "sha256": _sha256_file(project_root / relative)}
        for relative in sorted(INPUT_PATHS)
    ]


def _expected_output_records(file_bytes: dict[str, bytes]) -> list[dict[str, str]]:
    return [
        {
            "path": f"{CANONICAL_OUTPUT_DIR}/{name}",
            "sha256": _sha256_bytes(file_bytes[name]),
        }
        for name in CONTENT_OUTPUT_FILES
    ]


def build_package(project_root: Path) -> DeadlinePilotPackage:
    _validate_program_state(project_root)
    _validate_authority_confirmation(project_root)
    _validate_design_sources(project_root)

    environment_rows = validate_environment_rows(
        profile.as_row() for profile in ENVIRONMENT_PROFILES
    )
    ablation_rows = validate_ablation_rows(
        row.as_row() for row in ABLATION_ROWS
    )
    markdown_documents = {
        "deadline-pilot-execution-contract.md": _render_execution_contract(),
        "independent-reproduction-handoff.md": _render_reproduction_handoff(),
    }

    file_bytes: dict[str, bytes] = {
        "deadline-environment-profiles.csv": _csv_bytes(ENVIRONMENT_HEADER, environment_rows),
        "t5-ablation-run-matrix.csv": _csv_bytes(ABLATION_HEADER, ablation_rows),
        "deadline-pilot-execution-contract.md": markdown_documents["deadline-pilot-execution-contract.md"].encode("utf-8"),
        "independent-reproduction-handoff.md": markdown_documents["independent-reproduction-handoff.md"].encode("utf-8"),
    }
    manifest_payload = {
        **PACKAGE_CONSTANTS,
        "package_constants": dict(PACKAGE_CONSTANTS),
        "inputs": _manifest_input_records(project_root),
        "outputs": _expected_output_records(file_bytes),
        "integrity_artifacts": [
            f"{CANONICAL_OUTPUT_DIR}/{MANIFEST_FILENAME}",
            f"{CANONICAL_OUTPUT_DIR}/{MANIFEST_SIDECAR_FILENAME}",
        ],
    }
    return DeadlinePilotPackage(
        environment_rows=environment_rows,
        ablation_rows=ablation_rows,
        markdown_documents=markdown_documents,
        manifest_payload=manifest_payload,
    )


def _package_file_bytes(project_root: Path) -> dict[str, bytes]:
    package = build_package(project_root)
    file_bytes: dict[str, bytes] = {
        "deadline-environment-profiles.csv": _csv_bytes(ENVIRONMENT_HEADER, package.environment_rows),
        "t5-ablation-run-matrix.csv": _csv_bytes(ABLATION_HEADER, package.ablation_rows),
        "deadline-pilot-execution-contract.md": package.markdown_documents["deadline-pilot-execution-contract.md"].encode("utf-8"),
        "independent-reproduction-handoff.md": package.markdown_documents["independent-reproduction-handoff.md"].encode("utf-8"),
    }
    manifest_payload = {
        **package.manifest_payload,
        "outputs": _expected_output_records(file_bytes),
    }
    manifest_bytes = (
        json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    file_bytes[MANIFEST_FILENAME] = manifest_bytes
    file_bytes[MANIFEST_SIDECAR_FILENAME] = (
        f"{_sha256_bytes(manifest_bytes)}  {MANIFEST_FILENAME}\n".encode("utf-8")
    )
    return file_bytes


def write_package(project_root: Path, output_dir: Path) -> dict[str, bytes]:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_bytes = _package_file_bytes(project_root)
    for name, data in file_bytes.items():
        (output_dir / name).write_bytes(data)
    return file_bytes


def _load_actual_manifest(output_dir: Path) -> dict[str, object]:
    manifest_path = output_dir / MANIFEST_FILENAME
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PackageValidationError(f"{MANIFEST_FILENAME}: invalid manifest: {exc}") from exc
    if not isinstance(data, dict):
        raise PackageValidationError(f"{MANIFEST_FILENAME}: expected JSON object")
    return data


def check_package(project_root: Path, output_dir: Path | None = None) -> list[str]:
    target_dir = output_dir or (project_root / CANONICAL_OUTPUT_DIR)
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as temp_dir_name:
        expected_dir = Path(temp_dir_name)
        expected_bytes = write_package(project_root, expected_dir)
        for name in OUTPUT_FILES:
            actual_path = target_dir / name
            if not actual_path.exists():
                errors.append(f"missing output: {name}")
                continue
            if actual_path.read_bytes() != expected_bytes[name]:
                errors.append(f"canonical reconstruction drift: {name}")
        manifest_path = target_dir / MANIFEST_FILENAME
        sidecar_path = target_dir / MANIFEST_SIDECAR_FILENAME
        if manifest_path.exists() and sidecar_path.exists():
            expected_sidecar = f"{_sha256_file(manifest_path)}  {MANIFEST_FILENAME}"
            actual_sidecar = sidecar_path.read_text(encoding="utf-8").strip()
            if actual_sidecar != expected_sidecar:
                errors.append("manifest sidecar drift")
            actual_manifest = _load_actual_manifest(target_dir)
            actual_input_paths = tuple(
                item.get("path", "")
                for item in actual_manifest.get("inputs", [])
                if isinstance(item, dict)
            )
            actual_output_paths = tuple(
                item.get("path", "")
                for item in actual_manifest.get("outputs", [])
                if isinstance(item, dict)
            )
            actual_integrity_artifacts = tuple(
                item for item in actual_manifest.get("integrity_artifacts", [])
                if isinstance(item, str)
            )
            expected_input_paths = tuple(sorted(INPUT_PATHS))
            expected_output_paths = tuple(
                f"{CANONICAL_OUTPUT_DIR}/{name}" for name in CONTENT_OUTPUT_FILES
            )
            expected_integrity_artifacts = (
                f"{CANONICAL_OUTPUT_DIR}/{MANIFEST_FILENAME}",
                f"{CANONICAL_OUTPUT_DIR}/{MANIFEST_SIDECAR_FILENAME}",
            )
            if actual_input_paths != expected_input_paths:
                errors.append("manifest input inventory drift")
            if actual_output_paths != expected_output_paths:
                errors.append("manifest output inventory drift")
            if actual_integrity_artifacts != expected_integrity_artifacts:
                errors.append("manifest integrity artifact inventory drift")
            if actual_manifest.get("package_constants") != PACKAGE_CONSTANTS:
                errors.append("manifest package-constant drift")
            for item in actual_manifest.get("outputs", []):
                if not isinstance(item, dict):
                    continue
                relative = item.get("path", "")
                expected_name = relative.removeprefix(f"{CANONICAL_OUTPUT_DIR}/")
                if expected_name not in CONTENT_OUTPUT_FILES:
                    continue
                actual_file = target_dir / expected_name
                if item.get("sha256") != _sha256_file(actual_file):
                    errors.append(f"manifest output hash drift: {expected_name}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--output-dir", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    output_dir = args.output_dir or (project_root / CANONICAL_OUTPUT_DIR)
    try:
        if args.check:
            errors = check_package(project_root, output_dir)
            if errors:
                print(f"error: {errors[0]}", file=sys.stderr)
                return 1
            return 0
        write_package(project_root, output_dir)
        return 0
    except PackageValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
