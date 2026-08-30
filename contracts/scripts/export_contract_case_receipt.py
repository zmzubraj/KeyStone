#!/usr/bin/env python3
"""Export a fail-closed Foundry receipt for RID-C002-CONTRACT-001.

The receipt is PREAUTHORIZATION_ENGINEERING_QA only. It is not scientific
evidence, an independent reproduction, a smart-contract security audit, a gas
benchmark, or a production-security claim.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "contracts"
OUTPUT_DIR = CONTRACTS / "results" / "engineering_qa"
RECEIPT_PATH = OUTPUT_DIR / "rid-c002-contract-001-preauth-receipt.json"
RECEIPT_HASH_PATH = OUTPUT_DIR / "rid-c002-contract-001-preauth-receipt.json.sha256"
JUNIT_PATH = OUTPUT_DIR / "rid-c002-contract-001-foundry.junit.xml"
STDERR_PATH = OUTPUT_DIR / "rid-c002-contract-001-foundry.stderr.txt"

UNIT_SUITE = "test/KeystoneBulletinBoard.t.sol:KeystoneBulletinBoardTest"
INVARIANT_SUITE = "test/KeystoneBulletinBoard.t.sol:KeystoneBulletinBoardInvariantTest"

FORGE_TEST_ARGV = (
    "forge",
    "test",
    "--root",
    "contracts",
    "--match-path",
    "test/KeystoneBulletinBoard.t.sol",
    "--junit",
)


class ReceiptError(RuntimeError):
    """Raised when a receipt observation is incomplete or ambiguous."""


@dataclass(frozen=True, slots=True)
class CaseSpec:
    case_id: str
    suite_name: str
    test_name: str
    case_role: str


@dataclass(frozen=True, slots=True)
class ObservedCase:
    case_id: str
    suite_name: str
    test_name: str
    case_role: str
    expected_status: str
    status: str
    duration_seconds: float
    detail: str | None
    foundry_system_out: str
    execution_configuration: dict[str, object]
    test_body_gas: int | None
    gas_scope: str


def _unit(case_id: str, test_name: str, role: str = "deterministic_boundary") -> CaseSpec:
    return CaseSpec(case_id, UNIT_SUITE, test_name, role)


CASE_SPECS = (
    _unit("KBB-D01-AUDIT-MISSING-FAIL", "testAuditFinalizesWithMissingBitmap()"),
    _unit("KBB-D02-EQUIVOCATION-EXCLUSION", "testEquivocationExcludesResponse()"),
    _unit("KBB-D03-EPOCH-DUPLICATE-IDENTITY", "testRegisterEpochRejectsDuplicateCustodianIdentity()"),
    _unit("KBB-D04-EPOCH-ZERO-DESCRIPTORS", "testRegisterEpochRejectsZeroDescriptorCommitments()"),
    _unit("KBB-D05-ZERO-SUBJECT-BINDING", "testRequestRejectsZeroSubjectBinding()"),
    _unit("KBB-D06-INVALID-EVIDENCE-NONZERO", "testInvalidResponseRequiresEvidenceBinding()"),
    _unit("KBB-D07-AUDIT-COMPLETE-PASS", "testAuditFinalizesPassingWithCompleteSample()"),
    _unit("KBB-D08-FINALIZE-STATE-BOUNDARIES", "testFinalizeRejectsTooEarlyAndAfterFinalization()"),
    _unit("KBB-D09-DEADLINE-EQUALITY", "testDeadlineEqualityAcceptsResponseButRejectsFinalization()"),
    _unit(
        "KBB-D10-DEADLINE-PLUS-ONE",
        "testResponseAfterDeadlineIsRejectedAndFinalizationRecordsMissing()",
    ),
    _unit("KBB-D11-REQUEST-ID-OPEN-UNIQUENESS", "testRequestIdentifiersRejectZeroAndDuplicateOpenRequest()"),
    _unit(
        "KBB-D12-REQUEST-ID-TERMINAL-NONREUSE",
        "testRequestIdentifierCannotBeReusedAfterFinalizationOrCancellation()",
    ),
    _unit("KBB-D13-CANCELLED-CLOSED", "testCancelledRequestRejectsSubmissionAndFinalization()"),
    _unit("KBB-D14-DISPUTE-THRESHOLD-PASS", "testDisputeCompletesThresholdResponseLifecycle()"),
    _unit(
        "KBB-F01-FUZZ-DUPLICATE-IDENTITY",
        "testFuzzRegisterEpochRejectsDuplicateCustodianIdentity(uint8)",
        "fuzz_boundary",
    ),
    _unit(
        "KBB-F02-FUZZ-REQUIRED-ABOVE-SAMPLE",
        "testFuzzAuditRejectsThresholdAboveSample(uint256)",
        "fuzz_boundary",
    ),
    _unit(
        "KBB-F03-FUZZ-UNAUTHORIZED-OPEN-AUDIT",
        "testFuzzUnauthorizedCallerCannotOpenAudit(address)",
        "fuzz_boundary",
    ),
    _unit("KBB-G01-REGISTER-EPOCH-5", "testGas_RegisterEpochFiveMembers()", "gas_test_body"),
    _unit("KBB-G02-OPEN-AUDIT-3", "testGas_OpenAuditThreeMembers()", "gas_test_body"),
    _unit("KBB-G03-SUBMIT-FIRST-RESPONSE", "testGas_SubmitAuditResponse()", "gas_test_body"),
    _unit("KBB-G04-MARK-INVALID", "testGas_MarkInvalidResponse()", "gas_test_body"),
    _unit("KBB-G05-RECORD-EQUIVOCATION", "testGas_RecordEquivocation()", "gas_test_body"),
    _unit("KBB-G06-FINALIZE-AUDIT-2-OF-3", "testGas_FinalizeAudit()", "gas_test_body"),
    _unit("KBB-G07-OPEN-DISPUTE", "testGas_OpenDispute()", "gas_test_body"),
    _unit("KBB-G08-CANCEL-OPEN-REQUEST", "testGas_CancelRequest()", "gas_test_body"),
    CaseSpec(
        "KBB-I01-ADMIN-NONZERO",
        INVARIANT_SUITE,
        "invariant_AdminRemainsNonzero()",
        "stateful_invariant",
    ),
    CaseSpec(
        "KBB-I02-BITMAP-OUTCOME-CONSISTENCY",
        INVARIANT_SUITE,
        "invariant_ResponseAndOutcomeBitmapsRemainConsistent()",
        "stateful_invariant",
    ),
)

HASHED_INPUTS = (
    "contracts/src/KeystoneBulletinBoard.sol",
    "contracts/test/KeystoneBulletinBoard.t.sol",
    "contracts/foundry.toml",
    "contracts/scripts/export_contract_case_receipt.py",
)

FUZZ_PATTERN = re.compile(r"\(runs: (?P<runs>[0-9]+), μ: (?P<mean>[0-9]+), ~: (?P<median>[0-9]+)\)")
INVARIANT_PATTERN = re.compile(
    r"\(runs: (?P<runs>[0-9]+), calls: (?P<calls>[0-9]+), reverts: (?P<reverts>[0-9]+)\)"
)
GAS_PATTERN = re.compile(r"\(gas: (?P<gas>[0-9]+)\)")


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_to_root(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def validate_case_specs(specs: tuple[CaseSpec, ...]) -> None:
    if not specs:
        raise ReceiptError("case mapping must not be empty")
    case_ids = [spec.case_id for spec in specs]
    test_keys = [(spec.suite_name, spec.test_name) for spec in specs]
    if len(case_ids) != len(set(case_ids)):
        raise ReceiptError("duplicate case_id in case mapping")
    if len(test_keys) != len(set(test_keys)):
        raise ReceiptError("duplicate suite/test key in case mapping")
    for spec in specs:
        if not spec.case_id or not spec.suite_name or not spec.test_name or not spec.case_role:
            raise ReceiptError("case mapping contains a blank required field")


def _case_status(element: ET.Element) -> tuple[str, str | None]:
    for tag, status in (("failure", "FAIL"), ("error", "ERROR"), ("skipped", "SKIP")):
        child = element.find(tag)
        if child is not None:
            detail = child.get("message") or (child.text or "").strip() or None
            return status, detail
    return "PASS", None


def _execution_configuration(spec: CaseSpec, system_out: str) -> dict[str, object]:
    if spec.case_role == "fuzz_boundary":
        match = FUZZ_PATTERN.search(system_out)
        if match is None:
            return {"kind": "fuzz", "availability": "UNAVAILABLE_IN_JUNIT_SYSTEM_OUT"}
        return {
            "kind": "fuzz",
            "availability": "REPORTED_IN_JUNIT_SYSTEM_OUT",
            "runs": int(match.group("runs")),
            "mean_gas": int(match.group("mean")),
            "median_gas": int(match.group("median")),
            "gas_scope": "Foundry fuzz-test body statistic; not production gas evidence",
        }
    if spec.case_role == "stateful_invariant":
        match = INVARIANT_PATTERN.search(system_out)
        if match is None:
            return {"kind": "invariant", "availability": "UNAVAILABLE_IN_JUNIT_SYSTEM_OUT"}
        return {
            "kind": "invariant",
            "availability": "REPORTED_IN_JUNIT_SYSTEM_OUT",
            "runs": int(match.group("runs")),
            "calls": int(match.group("calls")),
            "reverts": int(match.group("reverts")),
        }
    return {"kind": "fixed", "availability": "NOT_APPLICABLE"}


def parse_junit_results(xml_bytes: bytes, specs: tuple[CaseSpec, ...]) -> list[ObservedCase]:
    validate_case_specs(specs)
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as error:
        raise ReceiptError(f"invalid Foundry JUnit XML: {error}") from error
    if root.tag != "testsuites":
        raise ReceiptError(f"unexpected JUnit root tag: {root.tag}")

    expected = {(spec.suite_name, spec.test_name): spec for spec in specs}
    observed: dict[tuple[str, str], ObservedCase] = {}
    unexpected: list[str] = []
    duplicates: list[str] = []
    suite_names: list[str] = []

    for suite in root.findall("testsuite"):
        suite_name = suite.get("name", "")
        suite_names.append(suite_name)
        testcases = suite.findall("testcase")
        try:
            declared_tests = int(suite.get("tests", "-1"))
        except ValueError as error:
            raise ReceiptError(f"invalid test count for suite {suite_name!r}") from error
        if declared_tests != len(testcases):
            raise ReceiptError(
                f"suite {suite_name!r} declares {declared_tests} tests but contains {len(testcases)} cases"
            )
        for testcase in testcases:
            test_name = testcase.get("name", "")
            key = (suite_name, test_name)
            spec = expected.get(key)
            if spec is None:
                unexpected.append(f"{suite_name}::{test_name or '<blank>'}")
                continue
            if key in observed:
                duplicates.append(spec.case_id)
                continue
            status, detail = _case_status(testcase)
            try:
                duration = float(testcase.get("time", "0") or "0")
            except ValueError as error:
                raise ReceiptError(f"invalid duration for {spec.case_id}") from error
            system_out = (testcase.findtext("system-out") or "").strip()
            gas_match = GAS_PATTERN.search(system_out)
            observed[key] = ObservedCase(
                case_id=spec.case_id,
                suite_name=spec.suite_name,
                test_name=spec.test_name,
                case_role=spec.case_role,
                expected_status="PASS",
                status=status,
                duration_seconds=duration,
                detail=detail,
                foundry_system_out=system_out,
                execution_configuration=_execution_configuration(spec, system_out),
                test_body_gas=int(gas_match.group("gas")) if gas_match else None,
                gas_scope=(
                    "Foundry test-body gas with possible harness/setup effects; not production deployment or transaction cost"
                    if gas_match
                    else "NOT_REPORTED"
                ),
            )

    if len(suite_names) != len(set(suite_names)):
        raise ReceiptError("duplicate testsuite names in JUnit report")
    expected_suites = {spec.suite_name for spec in specs}
    if set(suite_names) != expected_suites:
        raise ReceiptError(
            f"testsuite mismatch: expected {sorted(expected_suites)}, observed {sorted(set(suite_names))}"
        )
    if unexpected:
        raise ReceiptError(f"unexpected test results: {sorted(unexpected)}")
    if duplicates:
        raise ReceiptError(f"duplicate test results: {sorted(duplicates)}")
    missing = [spec.case_id for spec in specs if (spec.suite_name, spec.test_name) not in observed]
    if missing:
        raise ReceiptError(f"missing test results: {missing}")

    try:
        declared_total = int(root.get("tests", "-1"))
        declared_failures = int(root.get("failures", "-1"))
        declared_errors = int(root.get("errors", "-1"))
    except ValueError as error:
        raise ReceiptError("invalid root JUnit count attribute") from error
    if declared_total != len(specs) or len(observed) != len(specs):
        raise ReceiptError(
            f"root case-count mismatch: declared={declared_total}, mapped={len(specs)}, observed={len(observed)}"
        )
    actual_failures = sum(case.status == "FAIL" for case in observed.values())
    actual_errors = sum(case.status == "ERROR" for case in observed.values())
    if declared_failures != actual_failures or declared_errors != actual_errors:
        raise ReceiptError(
            "root failure/error mismatch: "
            f"declared=({declared_failures},{declared_errors}), "
            f"observed=({actual_failures},{actual_errors})"
        )
    return [observed[(spec.suite_name, spec.test_name)] for spec in specs]


def run_command(argv: list[str]) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["NO_COLOR"] = "1"
    environment["TERM"] = "dumb"
    return subprocess.run(
        argv,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )


def input_hashes() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw_path in HASHED_INPUTS:
        path = ROOT / raw_path
        if not path.is_file():
            raise ReceiptError(f"missing hashed input: {path}")
        rows.append({"path": raw_path, "sha256": sha256_file(path)})
    return rows


def git_metadata() -> dict[str, object]:
    commit = run_command(["git", "rev-parse", "HEAD"])
    full_status = run_command(["git", "status", "--porcelain"])
    scoped_status = run_command(
        [
            "git",
            "status",
            "--porcelain",
            "--",
            "contracts/src/KeystoneBulletinBoard.sol",
            "contracts/test/KeystoneBulletinBoard.t.sol",
            "contracts/foundry.toml",
            "contracts/scripts/export_contract_case_receipt.py",
        ]
    )
    if commit.returncode != 0 or full_status.returncode != 0 or scoped_status.returncode != 0:
        raise ReceiptError("git metadata command failed")
    full_rows = [line for line in full_status.stdout.splitlines() if line]
    scoped_rows = [line for line in scoped_status.stdout.splitlines() if line]
    return {
        "available": True,
        "commit": commit.stdout.strip(),
        "worktree_dirty": bool(full_rows),
        "status_porcelain": full_rows,
        "scoped_worktree_dirty": bool(scoped_rows),
        "scoped_status_porcelain": scoped_rows,
    }


def foundry_runtime() -> tuple[dict[str, object], dict[str, object]]:
    forge_path = shutil.which("forge")
    if forge_path is None:
        raise ReceiptError("forge executable not found")
    version = run_command(["forge", "--version"])
    config = run_command(["forge", "config", "--root", "contracts", "--json"])
    if version.returncode != 0:
        raise ReceiptError(f"forge --version returned {version.returncode}")
    if config.returncode != 0:
        raise ReceiptError(f"forge config returned {config.returncode}: {config.stderr.strip()}")
    try:
        parsed_config = json.loads(config.stdout)
    except json.JSONDecodeError as error:
        raise ReceiptError(f"invalid forge config JSON: {error}") from error
    fuzz = parsed_config.get("fuzz")
    invariant = parsed_config.get("invariant")
    if not isinstance(fuzz, dict) or not isinstance(invariant, dict):
        raise ReceiptError("forge config JSON lacks fuzz or invariant objects")
    runtime = {
        "forge_executable": str(Path(forge_path).resolve()),
        "forge_version_output": version.stdout.strip(),
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "platform_machine": platform.machine(),
        "relevant_environment": {
            key: os.environ.get(key)
            for key in (
                "FOUNDRY_PROFILE",
                "FOUNDRY_FUZZ_RUNS",
                "FOUNDRY_INVARIANT_RUNS",
                "FOUNDRY_INVARIANT_DEPTH",
            )
            if key in os.environ
        },
    }
    effective = {
        "solc": parsed_config.get("solc"),
        "optimizer": parsed_config.get("optimizer"),
        "optimizer_runs": parsed_config.get("optimizer_runs"),
        "fuzz": {"runs": fuzz.get("runs"), "seed": fuzz.get("seed")},
        "invariant": {
            "runs": invariant.get("runs"),
            "depth": invariant.get("depth"),
            "fail_on_revert": invariant.get("fail_on_revert"),
        },
    }
    return runtime, effective


def validate_reported_configuration(cases: list[ObservedCase], effective: dict[str, object]) -> None:
    fuzz_config = effective.get("fuzz")
    invariant_config = effective.get("invariant")
    if not isinstance(fuzz_config, dict) or not isinstance(invariant_config, dict):
        raise ReceiptError("effective Foundry configuration is incomplete")
    for case in cases:
        reported = case.execution_configuration
        if case.case_role == "fuzz_boundary" and reported.get("availability") == "REPORTED_IN_JUNIT_SYSTEM_OUT":
            if reported.get("runs") != fuzz_config.get("runs"):
                raise ReceiptError(f"fuzz-run mismatch for {case.case_id}")
        if case.case_role == "stateful_invariant" and reported.get("availability") == "REPORTED_IN_JUNIT_SYSTEM_OUT":
            if reported.get("runs") != invariant_config.get("runs"):
                raise ReceiptError(f"invariant-run mismatch for {case.case_id}")
            depth = invariant_config.get("depth")
            runs = reported.get("runs")
            calls = reported.get("calls")
            if isinstance(depth, int) and isinstance(runs, int) and calls != runs * depth:
                raise ReceiptError(f"invariant call-count mismatch for {case.case_id}")


def run_self_check() -> dict[str, object]:
    specs = (
        CaseSpec("CASE-U", "suite:unit", "testUnit()", "deterministic_boundary"),
        CaseSpec("CASE-F", "suite:unit", "testFuzz(uint256)", "fuzz_boundary"),
        CaseSpec("CASE-I", "suite:invariant", "invariant_State()", "stateful_invariant"),
    )
    valid = b"""<?xml version='1.0' encoding='UTF-8'?>
<testsuites tests='3' failures='0' errors='0'>
  <testsuite name='suite:unit' tests='2'>
    <testcase name='testUnit()' time='0.1'><system-out>[PASS] testUnit() (gas: 10)</system-out></testcase>
    <testcase name='testFuzz(uint256)' time='0.2'><system-out>[PASS] testFuzz(uint256) (runs: 8, &#956;: 11, ~: 10)</system-out></testcase>
  </testsuite>
  <testsuite name='suite:invariant' tests='1'>
    <testcase name='invariant_State()' time='0.3'><system-out>[PASS] invariant_State() (runs: 2, calls: 6, reverts: 0)</system-out></testcase>
  </testsuite>
</testsuites>"""
    observed = parse_junit_results(valid, specs)
    if [case.status for case in observed] != ["PASS", "PASS", "PASS"]:
        raise ReceiptError("self-check valid fixture did not parse as PASS")
    negative_checks: list[str] = []
    for check_id, candidate_specs, candidate_xml in (
        ("duplicate_mapping", (specs[0], specs[0]), valid),
        (
            "duplicate_result",
            specs,
            valid.replace(b"tests='3'", b"tests='4'", 1)
            .replace(b"name='suite:unit' tests='2'", b"name='suite:unit' tests='3'", 1)
            .replace(
                b"    <testcase name='testUnit()' time='0.1'><system-out>[PASS] testUnit() (gas: 10)</system-out></testcase>\n",
                b"    <testcase name='testUnit()' time='0.1'><system-out>[PASS] testUnit() (gas: 10)</system-out></testcase>\n"
                b"    <testcase name='testUnit()' time='0.1'><system-out>[PASS] testUnit() (gas: 10)</system-out></testcase>\n",
                1,
            ),
        ),
        (
            "missing_case",
            specs,
            valid.replace(b" tests='3'", b" tests='2'", 1).replace(
                b"  <testsuite name='suite:invariant' tests='1'>\n    <testcase name='invariant_State()' time='0.3'><system-out>[PASS] invariant_State() (runs: 2, calls: 6, reverts: 0)</system-out></testcase>\n  </testsuite>\n",
                b"",
            ),
        ),
    ):
        try:
            parse_junit_results(candidate_xml, candidate_specs)
        except ReceiptError:
            negative_checks.append(check_id)
        else:
            raise ReceiptError(f"self-check failed to reject {check_id}")
    return {
        "status": "PASS",
        "valid_fixture_case_count": len(observed),
        "negative_checks_rejected": negative_checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true", help="run parser fail-closed fixtures without Forge")
    args = parser.parse_args()
    try:
        self_check = run_self_check()
    except ReceiptError as error:
        print(f"BLOCKED: self-check failed: {error}", file=sys.stderr)
        return 2
    if args.self_check:
        print(json.dumps(self_check, indent=2, sort_keys=True))
        return 0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for stale in (RECEIPT_PATH, RECEIPT_HASH_PATH):
        stale.unlink(missing_ok=True)

    started_at = utc_now()
    try:
        validate_case_specs(CASE_SPECS)
        before_hashes = input_hashes()
        git_before = git_metadata()
        runtime, effective_config = foundry_runtime()
    except ReceiptError as error:
        print(f"BLOCKED: preflight failed: {error}", file=sys.stderr)
        return 2

    result = run_command(list(FORGE_TEST_ARGV))
    stdout_bytes = result.stdout.encode("utf-8")
    stderr_bytes = result.stderr.encode("utf-8")
    atomic_write(JUNIT_PATH, stdout_bytes)
    atomic_write(STDERR_PATH, stderr_bytes)

    try:
        if result.returncode != 0:
            raise ReceiptError(f"forge test returned {result.returncode}")
        observed = parse_junit_results(stdout_bytes, CASE_SPECS)
        nonpassing = [case.case_id for case in observed if case.status != "PASS"]
        if nonpassing:
            raise ReceiptError(f"nonpassing mapped cases: {nonpassing}")
        validate_reported_configuration(observed, effective_config)
        after_hashes = input_hashes()
        if before_hashes != after_hashes:
            raise ReceiptError("hashed inputs changed during Foundry execution")
        git_after = git_metadata()
    except ReceiptError as error:
        print(f"BLOCKED: machine-readable Foundry receipt rejected: {error}", file=sys.stderr)
        print(f"Raw JUnit: {relative_to_root(JUNIT_PATH)}", file=sys.stderr)
        print(f"Raw stderr: {relative_to_root(STDERR_PATH)}", file=sys.stderr)
        return 2

    completed_at = utc_now()
    receipt = {
        "schema_version": 1,
        "receipt_type": "PREAUTHORIZATION_ENGINEERING_QA",
        "result_id": "RID-C002-CONTRACT-001",
        "overall_status": "PASS",
        "evidence_origin": "INTERNAL_NON_EMPIRICAL_ENGINEERING_QA",
        "scientific_evidence_status": "NOT_SCIENTIFIC_EVIDENCE",
        "independence_status": "SAME_WORKSPACE_NOT_INDEPENDENT",
        "security_review_status": "NOT_A_SECURITY_AUDIT",
        "production_security_status": "NOT_ASSESSED",
        "authorization_boundary": "PREAUTHORIZATION_ONLY",
        "gas_claim": "Foundry test-body observations only; not production deployment or transaction costs",
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "self_check": self_check,
        "scope": {
            "mapped_case_count": len(CASE_SPECS),
            "observed_case_count": len(observed),
            "case_mapping": [asdict(spec) for spec in CASE_SPECS],
            "mapped_cases_are_not_a_scientific_denominator": True,
        },
        "execution": {
            "command_argv": list(FORGE_TEST_ARGV),
            "working_directory": relative_to_root(ROOT),
            "returncode": result.returncode,
            "machine_readable_format": "Foundry JUnit XML from --junit",
            "cases": [asdict(case) for case in observed],
            "effective_foundry_configuration": effective_config,
            "configuration_availability_note": (
                "Per-case fuzz/invariant run metadata is parsed from JUnit system-out when present; "
                "otherwise it is explicitly marked unavailable. Effective configuration is parsed from forge config --json."
            ),
        },
        "runtime": runtime,
        "git": {"before": git_before, "after": git_after},
        "sha256": {
            "inputs_verified_unchanged": before_hashes,
            "execution_outputs": [
                {"path": relative_to_root(JUNIT_PATH), "sha256": sha256_bytes(stdout_bytes)},
                {"path": relative_to_root(STDERR_PATH), "sha256": sha256_bytes(stderr_bytes)},
            ],
            "stdout_sha256": sha256_bytes(stdout_bytes),
            "stderr_sha256": sha256_bytes(stderr_bytes),
            "receipt_hash_location": relative_to_root(RECEIPT_HASH_PATH),
        },
        "limitations": [
            "This receipt is preauthorization engineering QA, not scientific evidence.",
            "It is a same-workspace run and not an independent reproduction.",
            "It is not a smart-contract security audit, formal verification, deployment study, or production-security assessment.",
            "Passing mapped cases prove only the asserted behavior of the current local source/test/config hashes.",
            "The contract remains a research-only ledger boundary and records admin-adjudicated off-chain proof outcomes.",
            "Foundry gas values are test-body observations with possible harness/setup effects and are not production cost evidence.",
            "Fuzz and invariant exploration is bounded by the recorded effective configuration and is not exhaustive proof.",
        ],
    }
    rendered = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    atomic_write(RECEIPT_PATH, rendered)
    receipt_hash = sha256_bytes(rendered)
    atomic_write(RECEIPT_HASH_PATH, f"{receipt_hash}  {RECEIPT_PATH.name}\n".encode("utf-8"))

    print(f"PASS: {relative_to_root(RECEIPT_PATH)}")
    print(f"SHA256: {receipt_hash}")
    print(f"Cases: {len(observed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
