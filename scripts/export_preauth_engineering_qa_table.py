#!/usr/bin/env python3
"""Export a paper-facing, non-empirical engineering-QA table from receipts.

This exporter intentionally accepts only the two frozen receipt families below.
It validates their detached SHA-256 sidecars and fails closed when their labels,
case identities, counts, or observed outcomes depart from the predeclared scope.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_CSV = ROOT / "paper/tables/preauthorization_engineering_qa.csv"
OUTPUT_MD = ROOT / "paper/tables/preauthorization_engineering_qa.md"
EXPECTED_CRYPTO_MANIFEST_PATH = (
    ".superpowers/sdd/keystone_mpp_goal_plan/"
    "prospective-deterministic-case-manifest.csv"
)

REQUIRED_LABELS = {
    "receipt_type": "PREAUTHORIZATION_ENGINEERING_QA",
    "scientific_evidence_status": "NOT_SCIENTIFIC_EVIDENCE",
    "independence_status": "SAME_WORKSPACE_NOT_INDEPENDENT",
    "overall_status": "PASS",
}


@dataclass(frozen=True)
class FamilySpec:
    family_id: str
    family_label: str
    receipt_path: Path
    expected_result_id: str
    expected_mapped_count: int
    expected_auxiliary_count: int
    expected_manifest_binding_count: int
    execution_key: str


FAMILIES = (
    FamilySpec(
        family_id="CRYPTO_INTEROPERABILITY",
        family_label="Prototype cryptography and interoperability",
        receipt_path=ROOT
        / "prototype/results/engineering_qa/rid-c002-crypto-001-preauth-receipt.json",
        expected_result_id="RID-C002-CRYPTO-001",
        expected_mapped_count=22,
        expected_auxiliary_count=2,
        expected_manifest_binding_count=19,
        execution_key="pytest",
    ),
    FamilySpec(
        family_id="CONTRACT_BOUNDARY",
        family_label="Smart-contract boundary",
        receipt_path=ROOT
        / "contracts/results/engineering_qa/rid-c002-contract-001-preauth-receipt.json",
        expected_result_id="RID-C002-CONTRACT-001",
        expected_mapped_count=27,
        expected_auxiliary_count=0,
        expected_manifest_binding_count=0,
        execution_key="execution",
    ),
)

CSV_COLUMNS = (
    "family_id",
    "family",
    "result_id",
    "mapped_checks",
    "mapped_pass",
    "auxiliary_checks",
    "auxiliary_pass",
    "total_checks",
    "total_pass",
    "receipt_path",
    "receipt_sha256",
    "authorization_boundary",
    "evidence_boundary",
    "independence_boundary",
    "security_boundary",
    "gas_boundary",
    "residual_limitations",
)


class ExportError(RuntimeError):
    """Raised when a receipt cannot support the predeclared table row."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ExportError(message)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_verified_receipt(path: Path) -> tuple[dict[str, Any], str]:
    sidecar = path.with_suffix(path.suffix + ".sha256")
    _require(path.is_file(), f"missing receipt: {path}")
    _require(sidecar.is_file(), f"missing receipt sidecar: {sidecar}")

    nonempty_lines = [line.strip() for line in sidecar.read_text().splitlines() if line.strip()]
    _require(len(nonempty_lines) == 1, f"sidecar must contain exactly one entry: {sidecar}")
    match = re.fullmatch(r"([0-9a-f]{64})\s{2}([^/]+)", nonempty_lines[0])
    _require(match is not None, f"malformed SHA-256 sidecar: {sidecar}")
    expected_hash, expected_name = match.groups()
    _require(expected_name == path.name, f"sidecar filename mismatch: {sidecar}")

    observed_hash = _sha256(path)
    _require(observed_hash == expected_hash, f"receipt SHA-256 mismatch: {path}")
    try:
        data = json.loads(path.read_text())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExportError(f"invalid receipt JSON: {path}: {exc}") from exc
    _require(isinstance(data, dict), f"receipt root must be an object: {path}")
    return data, observed_hash


def _validated_unique_ids(items: Any, id_key: str, context: str) -> set[str]:
    _require(isinstance(items, list), f"{context} must be a list")
    ids: list[str] = []
    for index, item in enumerate(items):
        _require(isinstance(item, dict), f"{context}[{index}] must be an object")
        value = item.get(id_key)
        _require(isinstance(value, str) and value, f"{context}[{index}].{id_key} missing")
        ids.append(value)
    _require(len(ids) == len(set(ids)), f"duplicate {id_key} in {context}")
    return set(ids)


def _validated_limitations(receipt: dict[str, Any], family_id: str) -> str:
    limitations = receipt.get("limitations")
    _require(isinstance(limitations, list) and limitations, f"{family_id}: limitations missing")
    _require(
        all(isinstance(item, str) and item.strip() for item in limitations),
        f"{family_id}: limitations must be non-empty strings",
    )
    return " | ".join(item.strip() for item in limitations)


def _field_or_not_recorded(receipt: dict[str, Any], key: str) -> str:
    value = receipt.get(key)
    if value is None:
        return "NOT_RECORDED_IN_RECEIPT"
    _require(isinstance(value, str) and value.strip(), f"invalid receipt field: {key}")
    return value.strip()


def _receipt_manifest_hash(receipt: dict[str, Any], manifest_path: str) -> str:
    sha256 = receipt.get("sha256")
    _require(isinstance(sha256, dict), "CRYPTO_INTEROPERABILITY: sha256 inventory missing")
    _require(
        sha256.get("inputs_verified_unchanged") is True,
        "CRYPTO_INTEROPERABILITY: receipt inputs were not verified unchanged",
    )
    captured_hashes: list[str] = []
    for snapshot_name in ("inputs", "inputs_before_execution", "inputs_after_execution"):
        snapshot = sha256.get(snapshot_name)
        _require(
            isinstance(snapshot, list),
            f"CRYPTO_INTEROPERABILITY: {snapshot_name} snapshot missing",
        )
        matches = [
            row
            for row in snapshot
            if isinstance(row, dict) and row.get("path") == manifest_path
        ]
        _require(
            len(matches) == 1,
            f"CRYPTO_INTEROPERABILITY: {snapshot_name} must bind manifest exactly once",
        )
        captured_hash = matches[0].get("sha256")
        _require(
            isinstance(captured_hash, str)
            and re.fullmatch(r"[0-9a-f]{64}", captured_hash) is not None,
            f"CRYPTO_INTEROPERABILITY: invalid manifest hash in {snapshot_name}",
        )
        captured_hashes.append(captured_hash)
    _require(
        len(set(captured_hashes)) == 1,
        "CRYPTO_INTEROPERABILITY: receipt manifest hashes disagree across snapshots",
    )
    return captured_hashes[0]


def validate_current_crypto_manifest(
    receipt: dict[str, Any], workspace_root: Path = ROOT
) -> None:
    """Verify the live manifest against its receipt path, hash, and bound rows."""
    manifest_binding = receipt.get("manifest_binding")
    _require(
        isinstance(manifest_binding, dict),
        "CRYPTO_INTEROPERABILITY: manifest_binding missing",
    )
    declared_path = manifest_binding.get("manifest_path")
    _require(
        declared_path == EXPECTED_CRYPTO_MANIFEST_PATH,
        "CRYPTO_INTEROPERABILITY: unexpected declared manifest path",
    )
    _require(
        manifest_binding.get("manifest_result_id") == "RID-C002-CRYPTO-001",
        "CRYPTO_INTEROPERABILITY: unexpected manifest result ID",
    )

    resolved_root = workspace_root.resolve()
    manifest_path = (resolved_root / EXPECTED_CRYPTO_MANIFEST_PATH).resolve()
    _require(
        manifest_path.is_relative_to(resolved_root),
        "CRYPTO_INTEROPERABILITY: manifest path escapes workspace",
    )
    _require(manifest_path.is_file(), "CRYPTO_INTEROPERABILITY: current manifest missing")
    captured_hash = _receipt_manifest_hash(receipt, EXPECTED_CRYPTO_MANIFEST_PATH)
    _require(
        _sha256(manifest_path) == captured_hash,
        "CRYPTO_INTEROPERABILITY: manifest SHA-256 mismatch",
    )

    bindings = manifest_binding.get("bindings")
    binding_ids = _validated_unique_ids(
        bindings,
        "manifest_case_id",
        "CRYPTO_INTEROPERABILITY.manifest_binding.bindings",
    )
    _require(
        manifest_binding.get("manifest_row_count") == 19 and len(binding_ids) == 19,
        "CRYPTO_INTEROPERABILITY: expected exactly 19 manifest bindings",
    )

    required_columns = {
        "manifest_status",
        "result_id",
        "case_id",
        "case_class",
        "primary_denominator_candidate",
        "source_ref",
        "expected_outcome",
        "evidence_origin",
        "authorization_state",
        "blocking_gap",
    }
    try:
        with manifest_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            _require(
                reader.fieldnames is not None and required_columns <= set(reader.fieldnames),
                "CRYPTO_INTEROPERABILITY: manifest columns missing",
            )
            rows = [
                dict(row)
                for row in reader
                if row.get("result_id") == "RID-C002-CRYPTO-001"
            ]
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ExportError(f"CRYPTO_INTEROPERABILITY: invalid current manifest: {exc}") from exc

    row_ids = _validated_unique_ids(rows, "case_id", "current RID-C002-CRYPTO-001 manifest rows")
    _require(
        len(row_ids) == 19 and row_ids == binding_ids,
        "CRYPTO_INTEROPERABILITY: current manifest rows do not match receipt bindings",
    )
    rows_by_id = {row["case_id"]: row for row in rows}
    bindings_by_id = {binding["manifest_case_id"]: binding for binding in bindings}
    compared_fields = {
        "manifest_source_ref": "source_ref",
        "manifest_expected_outcome": "expected_outcome",
        "manifest_evidence_origin": "evidence_origin",
        "manifest_authorization_state": "authorization_state",
        "manifest_blocking_gap": "blocking_gap",
    }
    for case_id in sorted(row_ids):
        row = rows_by_id[case_id]
        binding = bindings_by_id[case_id]
        _require(
            row.get("manifest_status") == "CANDIDATE_NON_OPERATIVE",
            f"CRYPTO_INTEROPERABILITY: operative/unexpected manifest status for {case_id}",
        )
        _require(
            row.get("authorization_state") == "NOT_AUTHORIZED",
            f"CRYPTO_INTEROPERABILITY: unexpected authorization state for {case_id}",
        )
        _require(
            row.get("evidence_origin") == "NON_EMPIRICAL_INTERNAL_FIXTURE",
            f"CRYPTO_INTEROPERABILITY: unexpected evidence origin for {case_id}",
        )
        _require(
            row.get("case_class") == "CRYPTO_BOUNDARY"
            and row.get("primary_denominator_candidate") == "YES",
            f"CRYPTO_INTEROPERABILITY: unexpected case classification for {case_id}",
        )
        for binding_field, manifest_field in compared_fields.items():
            _require(
                binding.get(binding_field) == row.get(manifest_field),
                f"CRYPTO_INTEROPERABILITY: manifest content drift for {case_id}.{manifest_field}",
            )


def _build_row(spec: FamilySpec, global_ids: set[str]) -> dict[str, str | int]:
    receipt, receipt_hash = _read_verified_receipt(spec.receipt_path)
    for key, expected in REQUIRED_LABELS.items():
        _require(receipt.get(key) == expected, f"{spec.family_id}: invalid {key}")
    _require(receipt.get("result_id") == spec.expected_result_id, f"{spec.family_id}: result_id mismatch")

    scope = receipt.get("scope")
    _require(isinstance(scope, dict), f"{spec.family_id}: scope missing")
    mapping = scope.get("case_mapping")
    mapping_ids = _validated_unique_ids(mapping, "case_id", f"{spec.family_id}.scope.case_mapping")
    _require(len(mapping_ids) == spec.expected_mapped_count, f"{spec.family_id}: mapped count mismatch")
    _require(scope.get("mapped_case_count") == spec.expected_mapped_count, f"{spec.family_id}: declared mapped count mismatch")
    _require(scope.get("observed_case_count") == spec.expected_mapped_count, f"{spec.family_id}: declared observed count mismatch")

    execution = receipt.get(spec.execution_key)
    _require(isinstance(execution, dict), f"{spec.family_id}: {spec.execution_key} missing")
    cases = execution.get("cases")
    execution_ids = _validated_unique_ids(cases, "case_id", f"{spec.family_id}.{spec.execution_key}.cases")
    _require(execution_ids == mapping_ids, f"{spec.family_id}: mapping/execution case IDs differ")
    _require(
        all(case.get("expected_status") == "PASS" and case.get("status") == "PASS" for case in cases),
        f"{spec.family_id}: mapped case did not pass as expected",
    )

    auxiliary = receipt.get("fixture_freshness_checks", [])
    auxiliary_ids = _validated_unique_ids(auxiliary, "check_id", f"{spec.family_id}.fixture_freshness_checks")
    _require(len(auxiliary_ids) == spec.expected_auxiliary_count, f"{spec.family_id}: auxiliary count mismatch")
    _require(
        all(
            check.get("expected_status") == "PASS" and check.get("observed_status") == "PASS"
            for check in auxiliary
        ),
        f"{spec.family_id}: auxiliary check did not pass as expected",
    )

    if spec.expected_manifest_binding_count:
        manifest_binding = receipt.get("manifest_binding")
        _require(isinstance(manifest_binding, dict), f"{spec.family_id}: manifest_binding missing")
        bindings = manifest_binding.get("bindings")
        binding_ids = _validated_unique_ids(
            bindings,
            "manifest_case_id",
            f"{spec.family_id}.manifest_binding.bindings",
        )
        _require(
            manifest_binding.get("manifest_row_count") == spec.expected_manifest_binding_count,
            f"{spec.family_id}: manifest row count mismatch",
        )
        _require(
            len(binding_ids) == spec.expected_manifest_binding_count,
            f"{spec.family_id}: manifest binding count mismatch",
        )
        allowed_types = {"exact", "bundled", "alias", "unmapped"}
        for binding in bindings:
            _require(
                binding.get("binding_type") in allowed_types,
                f"{spec.family_id}: invalid manifest binding type",
            )
            referenced = binding.get("receipt_case_ids")
            _require(isinstance(referenced, list), f"{spec.family_id}: invalid receipt_case_ids")
            _require(
                all(isinstance(case_id, str) and case_id for case_id in referenced),
                f"{spec.family_id}: invalid receipt case reference",
            )
            _require(
                len(referenced) == len(set(referenced)),
                f"{spec.family_id}: duplicate receipt case reference",
            )
            _require(
                set(referenced) <= mapping_ids,
                f"{spec.family_id}: manifest binding references unknown receipt case",
            )
        validate_current_crypto_manifest(receipt, ROOT)

    all_ids = mapping_ids | auxiliary_ids
    _require(not (global_ids & all_ids), f"{spec.family_id}: duplicate case/check ID across families")
    global_ids.update(all_ids)

    security_parts = [
        f"production_security_status={_field_or_not_recorded(receipt, 'production_security_status')}",
        f"security_review_status={_field_or_not_recorded(receipt, 'security_review_status')}",
    ]
    gas_boundary = _field_or_not_recorded(receipt, "gas_claim")
    relative_receipt = spec.receipt_path.relative_to(ROOT).as_posix()
    mapped_pass = sum(case["status"] == "PASS" for case in cases)
    auxiliary_pass = sum(check["observed_status"] == "PASS" for check in auxiliary)
    return {
        "family_id": spec.family_id,
        "family": spec.family_label,
        "result_id": spec.expected_result_id,
        "mapped_checks": spec.expected_mapped_count,
        "mapped_pass": mapped_pass,
        "auxiliary_checks": spec.expected_auxiliary_count,
        "auxiliary_pass": auxiliary_pass,
        "total_checks": spec.expected_mapped_count + spec.expected_auxiliary_count,
        "total_pass": mapped_pass + auxiliary_pass,
        "receipt_path": relative_receipt,
        "receipt_sha256": receipt_hash,
        "authorization_boundary": _field_or_not_recorded(receipt, "authorization_boundary"),
        "evidence_boundary": (
            f"evidence_origin={_field_or_not_recorded(receipt, 'evidence_origin')}; "
            f"scientific_evidence_status={receipt['scientific_evidence_status']}"
        ),
        "independence_boundary": receipt["independence_status"],
        "security_boundary": "; ".join(security_parts),
        "gas_boundary": gas_boundary,
        "residual_limitations": _validated_limitations(receipt, spec.family_id),
    }


def build_rows() -> list[dict[str, str | int]]:
    family_ids = [spec.family_id for spec in FAMILIES]
    _require(len(family_ids) == len(set(family_ids)), "duplicate family_id in exporter configuration")
    global_ids: set[str] = set()
    rows = [_build_row(spec, global_ids) for spec in FAMILIES]
    _require(len(rows) == 2, "exactly two receipt families are required")
    return rows


def render_csv(rows: list[dict[str, str | int]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _md(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def render_markdown(rows: list[dict[str, str | int]]) -> str:
    lines = [
        "# PREAUTHORIZATION engineering-QA table draft",
        "",
        (
            "**Caption.** Same-workspace, non-empirical PREAUTHORIZATION engineering-QA "
            "checks for the current prototype cryptography/interoperability and smart-contract "
            "boundary implementations. Counts are engineering checks, not a scientific denominator."
        ),
        "",
        "| Family | Checks passed | Receipt (SHA-256) | Evidence / independence boundary | Security / gas boundary | Residual limitations |",
        "|---|---:|---|---|---|---|",
    ]
    for row in rows:
        receipt_cell = f"`{row['receipt_path']}`<br>`{row['receipt_sha256']}`"
        evidence_cell = (
            f"{row['authorization_boundary']}; {row['evidence_boundary']}; "
            f"{row['independence_boundary']}"
        )
        security_cell = f"{row['security_boundary']}; gas={row['gas_boundary']}"
        lines.append(
            "| "
            + " | ".join(
                _md(value)
                for value in (
                    row["family"],
                    f"{row['total_pass']}/{row['total_checks']} "
                    f"({row['mapped_pass']}/{row['mapped_checks']} mapped; "
                    f"{row['auxiliary_pass']}/{row['auxiliary_checks']} auxiliary)",
                    receipt_cell,
                    evidence_cell,
                    security_cell,
                    row["residual_limitations"],
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            (
                "**Note.** This editable draft is generated only from the two hash-verified receipts "
                "named above. It is not a canonical paper table, empirical evidence, independent "
                "reproduction, a security audit, formal verification, deployment evidence, production "
                "validation, or production gas/cost evidence. `NOT_RECORDED_IN_RECEIPT` means the "
                "source receipt did not provide that field; no value was inferred."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _write_or_check(path: Path, content: str, check: bool) -> None:
    if check:
        _require(path.is_file(), f"missing generated output: {path}")
        _require(path.read_text() == content, f"stale generated output: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated outputs are absent or stale")
    args = parser.parse_args(argv)
    try:
        rows = build_rows()
        _write_or_check(OUTPUT_CSV, render_csv(rows), args.check)
        _write_or_check(OUTPUT_MD, render_markdown(rows), args.check)
    except (ExportError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    action = "verified" if args.check else "wrote"
    print(f"PASS: {action} {OUTPUT_CSV.relative_to(ROOT)}")
    print(f"PASS: {action} {OUTPUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
