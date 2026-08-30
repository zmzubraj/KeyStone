#!/usr/bin/env python3
"""Emit a fail-closed engineering-QA receipt for deterministic crypto cases.

This receipt is explicitly preauthorization engineering QA.  It is not
scientific evidence, an independent reproduction, a cryptographic audit, or a
production-security claim.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
OUTPUT_DIR = PROJECT / "results" / "engineering_qa"
RECEIPT_PATH = OUTPUT_DIR / "rid-c002-crypto-001-preauth-receipt.json"
RECEIPT_HASH_PATH = OUTPUT_DIR / "rid-c002-crypto-001-preauth-receipt.json.sha256"
JUNIT_PATH = OUTPUT_DIR / "rid-c002-crypto-001-pytest.xml"
STDOUT_PATH = OUTPUT_DIR / "rid-c002-crypto-001-pytest.stdout.txt"
STDERR_PATH = OUTPUT_DIR / "rid-c002-crypto-001-pytest.stderr.txt"
MANIFEST_PATH = (
    ROOT
    / ".superpowers/sdd/keystone_mpp_goal_plan/prospective-deterministic-case-manifest.csv"
)


class ReceiptError(RuntimeError):
    """Raised when receipt inputs or observations are incomplete or ambiguous."""


@dataclass(frozen=True, slots=True)
class CaseSpec:
    case_id: str
    test_node_id: str
    case_role: str


@dataclass(frozen=True, slots=True)
class ObservedCase:
    case_id: str
    test_node_id: str
    case_role: str
    expected_status: str
    status: str
    duration_seconds: float
    detail: str | None


@dataclass(frozen=True, slots=True)
class ManifestBinding:
    manifest_case_id: str
    binding_type: str
    receipt_case_ids: tuple[str, ...]
    binding_note: str


CASE_SPECS = (
    CaseSpec(
        "C002-CRYPTO-T-OPEN-001",
        "tests/test_threshold_kem.py::test_threshold_partials_open_encrypted_record",
        "direct_boundary",
    ),
    CaseSpec(
        "C002-CRYPTO-TMINUS1-REJECT-001",
        "tests/test_threshold_kem.py::test_fewer_than_threshold_valid_partials_cannot_open_record",
        "direct_boundary",
    ),
    CaseSpec(
        "C002-CRYPTO-INVALID-PARTIAL-EXCLUDE-001",
        "tests/test_threshold_kem.py::test_invalid_partial_is_excluded_before_threshold_counting",
        "direct_boundary",
    ),
    CaseSpec(
        "C002-CRYPTO-DLEQ-CONTEXT-MATRIX-001",
        "tests/test_dleq.py::test_valid_dleq_proof_verifies_and_is_context_bound",
        "direct_boundary_bundled_outcomes",
    ),
    CaseSpec(
        "C002-CRYPTO-DLEQ-TAMPER-REJECT-001",
        "tests/test_dleq.py::test_tampered_partial_decryption_fails_dleq_verification",
        "direct_boundary",
    ),
    CaseSpec(
        "C002-COMPONENT-SHAMIR-T-SUBSET-001",
        "tests/test_shamir.py::test_any_threshold_subset_reconstructs_secret",
        "supporting_component",
    ),
    CaseSpec(
        "C002-COMPONENT-FELDMAN-CORRUPT-REJECT-001",
        "tests/test_shamir.py::test_feldman_commitments_reject_corrupted_share",
        "supporting_component_bundled_outcomes",
    ),
    CaseSpec(
        "C002-INTEROP-AUDIT-REQUEST-GOLDEN-001",
        "tests/test_serialization.py::test_audit_request_encoding_matches_independent_golden_layout",
        "interoperability",
    ),
    CaseSpec(
        "C002-INTEROP-PARTIAL-RESPONSE-HASH-001",
        "tests/test_serialization.py::test_partial_response_round_trips_and_binds_request_hash",
        "interoperability_bundled_outcomes",
    ),
    CaseSpec(
        "C002-INTEROP-DECODER-NEGATIVE-MATRIX-001",
        "tests/test_serialization.py::test_decoder_rejects_trailing_bytes_wrong_kind_and_noncanonical_integer",
        "interoperability_bundled_outcomes",
    ),
    CaseSpec(
        "C002-INTEROP-PUBKEY-GOLDEN-001",
        "tests/test_signatures.py::test_public_key_derivation_from_fixed_seed_is_deterministic",
        "interoperability",
    ),
    CaseSpec(
        "C002-INTEROP-SIGN-CANONICAL-RESPONSE-001",
        "tests/test_signatures.py::test_signs_exact_canonical_partial_response_bytes",
        "interoperability",
    ),
    CaseSpec(
        "C002-INTEROP-SIGN-NEGATIVE-MATRIX-001",
        "tests/test_signatures.py::test_verification_rejects_wrong_message_signature_or_key",
        "interoperability_bundled_outcomes",
    ),
    CaseSpec(
        "C002-INTEROP-SIGN-REPLAY-MATRIX-001",
        "tests/test_signatures.py::test_context_change_cannot_replay_across_chain_or_contract",
        "interoperability_bundled_outcomes",
    ),
    CaseSpec(
        "C002-INTEROP-SIGN-LENGTH-MATRIX-001",
        "tests/test_signatures.py::test_key_and_signature_lengths_are_validated",
        "interoperability_bundled_outcomes",
    ),
    CaseSpec(
        "C002-CRYPTO-REFRESH-PRESERVE-OPEN-001",
        "tests/test_refresh.py::test_zero_polynomial_refresh_preserves_public_key_and_authorized_opening",
        "supporting_component_bundled_outcomes",
    ),
    CaseSpec(
        "C002-CRYPTO-STALE-PARTIAL-REJECT-001",
        "tests/test_refresh.py::test_old_and_new_partials_cannot_be_mixed_under_refreshed_epoch",
        "direct_boundary_bundled_outcomes",
    ),
    CaseSpec(
        "C002-CRYPTO-REFRESH-CONTEXT-ROTATION-001",
        "tests/test_refresh.py::test_refresh_generation_changes_canary_and_proof_context",
        "direct_boundary_bundled_outcomes",
    ),
    CaseSpec(
        "C002-CRYPTO-CANARY-CONTEXT-MATRIX-001",
        "tests/test_protocol.py::test_canary_is_publicly_deterministic_context_separated_and_in_group",
        "direct_boundary_bundled_outcomes",
    ),
    CaseSpec(
        "C002-CRYPTO-ROUTINE-AUDIT-EVIDENCE-001",
        "tests/test_protocol.py::test_audit_produces_objective_invalid_and_nonresponse_evidence",
        "direct_boundary_bundled_outcomes",
    ),
    CaseSpec(
        "C002-CRYPTO-AUDIT-INTERNAL-CANARY-DERIVATION-001",
        "tests/test_protocol.py::test_audit_derives_challenge_internally_from_beacon",
        "direct_boundary_bundled_outcomes",
    ),
    CaseSpec(
        "C002-CRYPTO-DISPUTE-T-OPEN-001",
        "tests/test_protocol.py::test_dispute_decrypts_when_threshold_valid_responses_arrive",
        "direct_boundary",
    ),
)


MANIFEST_BINDINGS = (
    ManifestBinding("C002-CRYPTO-T-OPEN-001", "exact", ("C002-CRYPTO-T-OPEN-001",), "exact receipt case ID"),
    ManifestBinding("C002-CRYPTO-TMINUS1-REJECT-001", "exact", ("C002-CRYPTO-TMINUS1-REJECT-001",), "exact receipt case ID"),
    ManifestBinding("C002-CRYPTO-INVALID-PARTIAL-EXCLUDE-001", "exact", ("C002-CRYPTO-INVALID-PARTIAL-EXCLUDE-001",), "exact receipt case ID"),
    ManifestBinding("C002-CRYPTO-DLEQ-VALID-CONTEXT-001", "bundled", ("C002-CRYPTO-DLEQ-CONTEXT-MATRIX-001",), "one receipt node bundles valid and wrong-context outcomes"),
    ManifestBinding("C002-CRYPTO-DLEQ-WRONG-CONTEXT-REJECT-001", "bundled", ("C002-CRYPTO-DLEQ-CONTEXT-MATRIX-001",), "one receipt node bundles valid and wrong-context outcomes"),
    ManifestBinding("C002-CRYPTO-DLEQ-TAMPER-REJECT-001", "exact", ("C002-CRYPTO-DLEQ-TAMPER-REJECT-001",), "exact receipt case ID"),
    ManifestBinding("C002-CRYPTO-STALE-PARTIAL-REJECT-001", "exact", ("C002-CRYPTO-STALE-PARTIAL-REJECT-001",), "exact receipt case ID; its test node has bundled assertions"),
    ManifestBinding("C002-CRYPTO-REFRESH-CONTEXT-ROTATION-001", "exact", ("C002-CRYPTO-REFRESH-CONTEXT-ROTATION-001",), "exact receipt case ID; its test node has bundled assertions"),
    ManifestBinding("C002-CRYPTO-CANARY-DETERMINISM-001", "bundled", ("C002-CRYPTO-CANARY-CONTEXT-MATRIX-001",), "one receipt node bundles deterministic, separation, and subgroup outcomes"),
    ManifestBinding("C002-CRYPTO-CANARY-CONTEXT-SEPARATION-001", "bundled", ("C002-CRYPTO-CANARY-CONTEXT-MATRIX-001",), "one receipt node bundles deterministic, separation, and subgroup outcomes"),
    ManifestBinding("C002-CRYPTO-CANARY-NONTRIVIAL-MAP-001", "bundled", ("C002-CRYPTO-CANARY-CONTEXT-MATRIX-001",), "receipt node checks subgroup/non-identity behavior; unknown discrete log remains an assumption"),
    ManifestBinding(
        "C002-CRYPTO-ROUTINE-AUDIT-EVIDENCE-001",
        "bundled",
        (
            "C002-CRYPTO-ROUTINE-AUDIT-EVIDENCE-001",
            "C002-CRYPTO-AUDIT-INTERNAL-CANARY-DERIVATION-001",
        ),
        "manifest row bundles evidence attribution and internal challenge derivation across two receipt nodes",
    ),
    ManifestBinding("C002-CRYPTO-DISPUTE-T-OPEN-001", "exact", ("C002-CRYPTO-DISPUTE-T-OPEN-001",), "exact receipt case ID"),
    ManifestBinding("C002-CRYPTO-SIGN-CANONICAL-RESPONSE-001", "alias", ("C002-INTEROP-SIGN-CANONICAL-RESPONSE-001",), "manifest CRYPTO namespace aliases the receipt INTEROP namespace"),
    ManifestBinding("C002-CRYPTO-SIGN-WRONG-MESSAGE-REJECT-001", "alias", ("C002-INTEROP-SIGN-NEGATIVE-MATRIX-001",), "namespace alias to a receipt node with bundled negative outcomes"),
    ManifestBinding("C002-CRYPTO-SIGN-WRONG-KEY-REJECT-001", "alias", ("C002-INTEROP-SIGN-NEGATIVE-MATRIX-001",), "namespace alias to a receipt node with bundled negative outcomes"),
    ManifestBinding("C002-CRYPTO-SIGN-TAMPER-REJECT-001", "alias", ("C002-INTEROP-SIGN-NEGATIVE-MATRIX-001",), "namespace alias to a receipt node with bundled negative outcomes"),
    ManifestBinding("C002-CRYPTO-SIGN-CROSSCHAIN-REPLAY-REJECT-001", "alias", ("C002-INTEROP-SIGN-REPLAY-MATRIX-001",), "namespace alias to a receipt node with bundled replay outcomes"),
    ManifestBinding("C002-CRYPTO-SIGN-CROSSCONTRACT-REPLAY-REJECT-001", "alias", ("C002-INTEROP-SIGN-REPLAY-MATRIX-001",), "namespace alias to a receipt node with bundled replay outcomes"),
)


HASHED_INPUTS = (
    "pyproject.toml",
    "uv.lock",
    "requirements-lock.txt",
    "scripts/export_crypto_case_receipt.py",
    "scripts/export_test_vectors.py",
    "scripts/export_signature_vectors.py",
    "src/keystone/group.py",
    "src/keystone/shamir.py",
    "src/keystone/dleq.py",
    "src/keystone/threshold_kem.py",
    "src/keystone/serialization.py",
    "src/keystone/signatures.py",
    "src/keystone/protocol.py",
    "tests/test_threshold_kem.py",
    "tests/test_dleq.py",
    "tests/test_shamir.py",
    "tests/test_serialization.py",
    "tests/test_signatures.py",
    "tests/test_refresh.py",
    "tests/test_protocol.py",
    "../paper/test_vectors.json",
    "../paper/signature_test_vectors.json",
    "../.superpowers/sdd/keystone_mpp_goal_plan/prospective-deterministic-case-manifest.csv",
)


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_to_root(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def remove_stale_receipt_outputs(receipt_path: Path, sidecar_path: Path) -> None:
    """Remove prior decision-bearing outputs before any preflight can fail."""
    for path in (receipt_path, sidecar_path):
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def atomic_publish_receipt(receipt_path: Path, sidecar_path: Path, rendered: str) -> str:
    """Atomically replace each receipt artifact, removing a partial pair on error."""
    try:
        _atomic_write_text(receipt_path, rendered)
        receipt_hash = sha256_file(receipt_path)
        _atomic_write_text(sidecar_path, f"{receipt_hash}  {receipt_path.name}\n")
    except OSError:
        remove_stale_receipt_outputs(receipt_path, sidecar_path)
        raise
    return receipt_hash


def require_unchanged_input_hashes(
    before: list[dict[str, str]], after: list[dict[str, str]]
) -> None:
    before_by_path = {row["path"]: row["sha256"] for row in before}
    after_by_path = {row["path"]: row["sha256"] for row in after}
    if len(before_by_path) != len(before) or len(after_by_path) != len(after):
        raise ReceiptError("duplicate path in input hash inventory")
    if before_by_path != after_by_path:
        changed = sorted(
            path
            for path in before_by_path.keys() | after_by_path.keys()
            if before_by_path.get(path) != after_by_path.get(path)
        )
        raise ReceiptError(f"input drift detected during execution: {changed}")


def read_crypto_manifest_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise ReceiptError(f"missing deterministic case manifest: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [
            dict(row)
            for row in csv.DictReader(handle)
            if row.get("result_id") == "RID-C002-CRYPTO-001"
        ]
    case_ids = [row.get("case_id", "") for row in rows]
    if len(rows) != 19:
        raise ReceiptError(f"expected 19 RID-C002-CRYPTO-001 manifest rows, found {len(rows)}")
    if any(not case_id for case_id in case_ids):
        raise ReceiptError("blank case_id in RID-C002-CRYPTO-001 manifest rows")
    if len(case_ids) != len(set(case_ids)):
        raise ReceiptError("duplicate case_id in RID-C002-CRYPTO-001 manifest rows")
    return rows


def validate_manifest_bindings(
    manifest_rows: list[dict[str, str]],
    bindings: tuple[ManifestBinding, ...],
    case_specs: tuple[CaseSpec, ...],
) -> list[dict[str, object]]:
    manifest_by_id = {row["case_id"]: row for row in manifest_rows}
    binding_ids = [binding.manifest_case_id for binding in bindings]
    if len(binding_ids) != len(set(binding_ids)):
        raise ReceiptError("duplicate manifest_case_id in manifest bindings")
    if set(binding_ids) != set(manifest_by_id):
        missing = sorted(set(manifest_by_id) - set(binding_ids))
        extra = sorted(set(binding_ids) - set(manifest_by_id))
        raise ReceiptError(
            f"manifest binding coverage mismatch: missing={missing}, extra={extra}"
        )

    receipt_case_ids = {spec.case_id for spec in case_specs}
    allowed_types = {"exact", "bundled", "alias", "unmapped"}
    validated: list[dict[str, object]] = []
    for binding in bindings:
        if binding.binding_type not in allowed_types:
            raise ReceiptError(f"invalid binding_type for {binding.manifest_case_id}")
        referenced_ids = tuple(binding.receipt_case_ids)
        if binding.binding_type == "unmapped":
            if referenced_ids:
                raise ReceiptError(f"unmapped binding references receipt cases: {binding.manifest_case_id}")
        else:
            if not referenced_ids or len(referenced_ids) != len(set(referenced_ids)):
                raise ReceiptError(f"invalid receipt case references: {binding.manifest_case_id}")
            unknown = sorted(set(referenced_ids) - receipt_case_ids)
            if unknown:
                raise ReceiptError(f"unknown receipt case IDs for {binding.manifest_case_id}: {unknown}")
        if binding.binding_type == "exact" and referenced_ids != (binding.manifest_case_id,):
            raise ReceiptError(f"exact binding does not preserve case ID: {binding.manifest_case_id}")

        manifest_row = manifest_by_id[binding.manifest_case_id]
        validated.append(
            {
                "manifest_case_id": binding.manifest_case_id,
                "binding_type": binding.binding_type,
                "receipt_case_ids": list(referenced_ids),
                "binding_note": binding.binding_note,
                "manifest_source_ref": manifest_row.get("source_ref"),
                "manifest_expected_outcome": manifest_row.get("expected_outcome"),
                "manifest_evidence_origin": manifest_row.get("evidence_origin"),
                "manifest_authorization_state": manifest_row.get("authorization_state"),
                "manifest_blocking_gap": manifest_row.get("blocking_gap"),
            }
        )
    return validated


def validate_case_specs(specs: tuple[CaseSpec, ...]) -> None:
    if not specs:
        raise ReceiptError("case mapping must not be empty")
    case_ids = [spec.case_id for spec in specs]
    node_ids = [spec.test_node_id for spec in specs]
    if len(case_ids) != len(set(case_ids)):
        raise ReceiptError("duplicate case_id in case mapping")
    if len(node_ids) != len(set(node_ids)):
        raise ReceiptError("duplicate test_node_id in case mapping")
    for spec in specs:
        if not spec.case_id or not spec.test_node_id or not spec.case_role:
            raise ReceiptError("case mapping contains a blank required field")
        test_file = PROJECT / spec.test_node_id.split("::", 1)[0]
        if not test_file.is_file():
            raise ReceiptError(f"missing mapped test file: {test_file}")


def _testcase_status(element: ET.Element) -> tuple[str, str | None]:
    for tag, status in (("failure", "FAIL"), ("error", "ERROR"), ("skipped", "SKIP")):
        child = element.find(tag)
        if child is not None:
            detail = child.get("message") or (child.text or "").strip() or None
            return status, detail
    return "PASS", None


def parse_junit_results(path: Path, specs: tuple[CaseSpec, ...]) -> list[ObservedCase]:
    validate_case_specs(specs)
    if not path.is_file():
        raise ReceiptError(f"missing JUnit report: {path}")
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        raise ReceiptError(f"invalid JUnit XML: {error}") from error

    by_name = {spec.test_node_id.rsplit("::", 1)[1]: spec for spec in specs}
    if len(by_name) != len(specs):
        raise ReceiptError("mapped test function names are not unique")

    observed: dict[str, ObservedCase] = {}
    unknown: list[str] = []
    duplicates: list[str] = []
    for testcase in root.iter("testcase"):
        name = testcase.get("name", "")
        spec = by_name.get(name)
        if spec is None:
            unknown.append(name or "<blank>")
            continue
        if spec.case_id in observed:
            duplicates.append(spec.case_id)
            continue
        status, detail = _testcase_status(testcase)
        try:
            duration = float(testcase.get("time", "0") or "0")
        except ValueError as error:
            raise ReceiptError(f"invalid duration for {spec.case_id}") from error
        observed[spec.case_id] = ObservedCase(
            case_id=spec.case_id,
            test_node_id=spec.test_node_id,
            case_role=spec.case_role,
            expected_status="PASS",
            status=status,
            duration_seconds=duration,
            detail=detail,
        )

    if unknown:
        raise ReceiptError(f"unexpected test results: {sorted(unknown)}")
    if duplicates:
        raise ReceiptError(f"duplicate test results: {sorted(duplicates)}")
    missing = [spec.case_id for spec in specs if spec.case_id not in observed]
    if missing:
        raise ReceiptError(f"missing test results: {missing}")
    return [observed[spec.case_id] for spec in specs]


def run_command(argv: list[str]) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        argv,
        cwd=PROJECT,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )


def checked_input_hashes() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw_path in HASHED_INPUTS:
        path = (PROJECT / raw_path).resolve()
        if not path.is_file():
            raise ReceiptError(f"missing hashed input: {path}")
        rows.append({"path": relative_to_root(path), "sha256": sha256_file(path)})
    return rows


def git_metadata() -> dict[str, object]:
    commit = run_command(["git", "rev-parse", "HEAD"])
    status = run_command(
        [
            "git",
            "status",
            "--porcelain",
            "--",
            ".",
            "../paper/test_vectors.json",
            "../paper/signature_test_vectors.json",
        ]
    )
    if commit.returncode != 0 or status.returncode != 0:
        return {"available": False, "commit": None, "scoped_worktree_dirty": None}
    return {
        "available": True,
        "commit": commit.stdout.strip(),
        "scoped_worktree_dirty": bool(status.stdout.strip()),
    }


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_stale_receipt_outputs(RECEIPT_PATH, RECEIPT_HASH_PATH)
    started_at = utc_now()
    fatal_errors: list[str] = []
    observed_cases: list[ObservedCase] = []

    try:
        validate_case_specs(CASE_SPECS)
        manifest_rows = read_crypto_manifest_rows(MANIFEST_PATH)
        manifest_binding_rows = validate_manifest_bindings(
            manifest_rows,
            MANIFEST_BINDINGS,
            CASE_SPECS,
        )
        input_hashes_before = checked_input_hashes()
    except ReceiptError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    pytest_argv = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        f"--junitxml={JUNIT_PATH}",
        *[spec.test_node_id for spec in CASE_SPECS],
    ]
    pytest_result = run_command(pytest_argv)
    STDOUT_PATH.write_text(pytest_result.stdout, encoding="utf-8")
    STDERR_PATH.write_text(pytest_result.stderr, encoding="utf-8")
    try:
        observed_cases = parse_junit_results(JUNIT_PATH, CASE_SPECS)
    except ReceiptError as error:
        fatal_errors.append(str(error))
    if pytest_result.returncode != 0:
        fatal_errors.append(f"pytest returned {pytest_result.returncode}")

    freshness_checks: list[dict[str, object]] = []
    for check_id, argv in (
        (
            "C002-INTEROP-PROTOCOL-VECTOR-FRESHNESS-001",
            [sys.executable, "scripts/export_test_vectors.py", "--check"],
        ),
        (
            "C002-INTEROP-SIGNATURE-VECTOR-FRESHNESS-001",
            [sys.executable, "scripts/export_signature_vectors.py", "--check"],
        ),
    ):
        result = run_command(argv)
        status = "PASS" if result.returncode == 0 else "FAIL"
        freshness_checks.append(
            {
                "check_id": check_id,
                "command_argv": argv,
                "expected_status": "PASS",
                "observed_status": status,
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
        )
        if result.returncode != 0:
            fatal_errors.append(f"{check_id} returned {result.returncode}")

    input_hashes_after: list[dict[str, str]] = []
    inputs_verified_unchanged = False
    try:
        input_hashes_after = checked_input_hashes()
        require_unchanged_input_hashes(input_hashes_before, input_hashes_after)
        inputs_verified_unchanged = True
    except ReceiptError as error:
        fatal_errors.append(str(error))

    nonpassing = [case.case_id for case in observed_cases if case.status != "PASS"]
    if nonpassing:
        fatal_errors.append(f"nonpassing cases: {nonpassing}")
    overall_status = "PASS" if not fatal_errors else "FAIL"
    completed_at = utc_now()

    output_hashes = []
    for path in (JUNIT_PATH, STDOUT_PATH, STDERR_PATH):
        if path.is_file():
            output_hashes.append({"path": relative_to_root(path), "sha256": sha256_file(path)})

    receipt = {
        "schema_version": 1,
        "receipt_type": "PREAUTHORIZATION_ENGINEERING_QA",
        "result_id": "RID-C002-CRYPTO-001",
        "evidence_origin": "INTERNAL_NON_EMPIRICAL_ENGINEERING_QA",
        "scientific_evidence_status": "NOT_SCIENTIFIC_EVIDENCE",
        "independence_status": "SAME_WORKSPACE_NOT_INDEPENDENT",
        "production_security_status": "NOT_ASSESSED",
        "authorization_boundary": "PREAUTHORIZATION_ONLY",
        "randomness_claim": "NONE; receipt records only the tested pass/fail invariants",
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "overall_status": overall_status,
        "fatal_errors": fatal_errors,
        "scope": {
            "mapped_case_count": len(CASE_SPECS),
            "observed_case_count": len(observed_cases),
            "direct_and_supporting_cases_are_not_a_scientific_denominator": True,
            "case_mapping": [asdict(spec) for spec in CASE_SPECS],
        },
        "manifest_binding": {
            "manifest_path": relative_to_root(MANIFEST_PATH),
            "manifest_result_id": "RID-C002-CRYPTO-001",
            "manifest_row_count": len(manifest_rows),
            "allowed_binding_types": ["exact", "bundled", "alias", "unmapped"],
            "bindings": manifest_binding_rows,
        },
        "runtime": {
            "python_executable": sys.executable,
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "pytest_version": importlib.metadata.version("pytest"),
            "platform_system": platform.system(),
            "platform_release": platform.release(),
            "platform_machine": platform.machine(),
            "git": git_metadata(),
        },
        "pytest": {
            "command_argv": pytest_argv,
            "working_directory": relative_to_root(PROJECT),
            "returncode": pytest_result.returncode,
            "cases": [asdict(case) for case in observed_cases],
        },
        "fixture_freshness_checks": freshness_checks,
        "sha256": {
            "inputs": input_hashes_after,
            "inputs_before_execution": input_hashes_before,
            "inputs_after_execution": input_hashes_after,
            "inputs_verified_unchanged": inputs_verified_unchanged,
            "execution_outputs": output_hashes,
            "receipt_hash_location": relative_to_root(RECEIPT_HASH_PATH),
        },
        "limitations": [
            "This receipt is preauthorization engineering QA, not scientific evidence.",
            "It is not an independent reproduction or cryptographic audit.",
            "Bundled-outcome test nodes do not prove separately manifested subcases.",
            "The receipt makes no claim that cryptographic randomness is deterministic.",
            "The MPP uses dealer-based sharing/refresh and a non-standardized research group.",
            "The audit challenge is derived internally from public beacon/context inputs; this local test is not a production misuse-resistance audit.",
            "The response request_hash field is serialized and signed but not end-to-end matched to a supplied request by the inspected helper.",
        ],
    }
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    try:
        receipt_hash = atomic_publish_receipt(RECEIPT_PATH, RECEIPT_HASH_PATH, rendered)
    except OSError as error:
        print(f"ERROR: atomic receipt publication failed: {error}", file=sys.stderr)
        return 2

    print(f"{overall_status}: {relative_to_root(RECEIPT_PATH)}")
    print(f"SHA256: {receipt_hash}")
    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
