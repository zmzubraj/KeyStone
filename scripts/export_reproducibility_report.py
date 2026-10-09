#!/usr/bin/env python3
"""Export a canonical, fail-closed reproducibility status report."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = Path("research-case/program-state.json")
PRIMARY_RESULTS_PATH = Path("research-case/03-design/primary-results-contract.csv")
SOURCE_MANIFEST_PATH = Path("research-case/07-manuscript/source-manifest.json")
RECEIPT_PATH = Path("prototype/results/engineering_qa/isolated_reproduction/receipt.json")
RECEIPT_SHA_PATH = Path("prototype/results/engineering_qa/isolated_reproduction/receipt.json.sha256")
HANDOFF_PATH = Path("research-case/03-design/independent-reproduction-handoff.md")
OUTPUT_PATH = Path("research-case/05-analysis/reproducibility-report.md")
EXTERNAL_VALIDATION_PATHS = (
    Path("research-case/05-analysis/external-validation/protocol.md"),
    Path("research-case/05-analysis/external-validation/results.csv"),
    Path("research-case/05-analysis/external-validation/real-world-validation-report.md"),
    Path("research-case/05-analysis/external-validation/challenge.md"),
)
REQUIRED_STATE = {
    "status": "ACTIVE",
    "current_phase": "INTAKE",
    "resume_from": "INTAKE",
    "novelty_status": "UNRESOLVED",
    "feasibility_decision": "UNASSESSED",
    "solution_viability_status": "ASSERTED_ONLY",
    "acceptance_readiness": "NOT_ASSESSABLE",
}
REQUIRED_RECEIPT = {
    "schema_id": "KEYSTONE_ISOLATED_MECHANICAL_REPRODUCTION_RECEIPT",
    "status": "MECHANICAL_PASS",
    "executor_class": "SECOND_AGENT_SAME_HOST_ISOLATED_COPY",
    "scientific_evidence_status": "NOT_INDEPENDENT_SCIENTIFIC_VERIFICATION",
    "external_sharing": "NOT_PERFORMED",
    "canonical_phase": "INTAKE",
    "novelty_status": "UNRESOLVED",
    "feasibility_decision": "UNASSESSED",
    "solution_viability": "ASSERTED_ONLY",
    "acceptance_readiness": "NOT_ASSESSABLE",
}


class ReproducibilityReportError(RuntimeError):
    """Raised when inputs cannot support a claim-safe report."""


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ReproducibilityReportError(f"cannot hash {path}: {exc}") from exc


def _json(path: Path, label: str) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReproducibilityReportError(f"cannot read {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReproducibilityReportError(f"{label} must be a JSON object")
    return payload


def _validate_state(root: Path) -> dict[str, object]:
    state = _json(root / STATE_PATH, "canonical program state")
    for field, expected in REQUIRED_STATE.items():
        actual = state.get(field)
        if actual != expected:
            raise ReproducibilityReportError(f"canonical {field} expected {expected}, got {actual}")
    return state


def _validate_receipt(root: Path) -> dict[str, object]:
    receipt_path = root / RECEIPT_PATH
    receipt = _json(receipt_path, "isolated reproduction receipt")
    for field, expected in REQUIRED_RECEIPT.items():
        actual = receipt.get(field)
        if actual != expected:
            if field == "scientific_evidence_status":
                raise ReproducibilityReportError(
                    f"scientific evidence status must remain {expected}; got {actual}"
                )
            raise ReproducibilityReportError(f"receipt {field} expected {expected}, got {actual}")

    commands = receipt.get("commands")
    if not isinstance(commands, list) or not commands:
        raise ReproducibilityReportError("receipt must contain executed commands")
    if any(not isinstance(command, dict) or command.get("returncode") != 0 for command in commands):
        raise ReproducibilityReportError("receipt contains a missing or failed command")
    limitations = receipt.get("residual_limitations")
    if not isinstance(limitations, list) or "no distributed deadline execution" not in limitations:
        raise ReproducibilityReportError("receipt lacks the distributed-deadline limitation")

    try:
        sidecar = (root / RECEIPT_SHA_PATH).read_text(encoding="utf-8").strip().split()
    except OSError as exc:
        raise ReproducibilityReportError(f"cannot read receipt hash sidecar: {exc}") from exc
    if len(sidecar) != 2 or sidecar[0] != _sha256(receipt_path) or sidecar[1] != "receipt.json":
        raise ReproducibilityReportError("receipt hash sidecar mismatch")
    return receipt


def _validate_primary_contract(root: Path) -> list[dict[str, str]]:
    try:
        with (root / PRIMARY_RESULTS_PATH).open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ReproducibilityReportError(f"cannot read primary-results planning contract: {exc}") from exc
    if len(rows) != 9:
        raise ReproducibilityReportError("primary-results planning contract must contain 9 result slots")
    for row in rows:
        result_id = row.get("result_id", "UNKNOWN")
        expected = {
            "authorized": "false",
            "independent": "false",
            "observed_outcome": "NOT_COLLECTED",
            "estimate": "NOT_ESTIMATED",
            "uncertainty": "NOT_ESTIMATED",
            "analysis_status": "DRAFT_RESULT_CONTRACT_ONLY",
            "evidence_maturity": "V0 ASSERTED",
            "claim_ceiling": "V0 ASSERTED",
        }
        for field, wanted in expected.items():
            if row.get(field) != wanted:
                raise ReproducibilityReportError(f"{result_id} {field} must remain {wanted}")
    return rows


def _render(root: Path) -> str:
    state = _validate_state(root)
    receipt = _validate_receipt(root)
    primary_rows = _validate_primary_contract(root)
    try:
        handoff = (root / HANDOFF_PATH).read_text(encoding="utf-8")
    except OSError as exc:
        raise ReproducibilityReportError(f"cannot read independent reproduction handoff: {exc}") from exc
    normalized_handoff = " ".join(handoff.split())
    if "Same-author rerun is not independent scientific verification" not in normalized_handoff:
        raise ReproducibilityReportError("handoff lacks the scientific-independence boundary")

    current_source_manifest_hash = _sha256(root / SOURCE_MANIFEST_PATH)
    current_state_hash = _sha256(root / STATE_PATH)
    receipt_source_manifest_hash = str(receipt.get("source_manifest_sha256", ""))
    receipt_state_hash = str(receipt.get("program_state_sha256", ""))
    source_manifest_matches = current_source_manifest_hash == receipt_source_manifest_hash
    state_matches = current_state_hash == receipt_state_hash
    current_binding = source_manifest_matches and state_matches
    disposition = (
        "MECHANICAL_SNAPSHOT_CURRENT_BUT_INDEPENDENCE_MISSING"
        if current_binding
        else "CURRENT_TREE_REPLAY_REQUIRED"
    )

    commands = receipt["commands"]
    assert isinstance(commands, list)
    passed_commands = sum(
        1 for command in commands if isinstance(command, dict) and command.get("returncode") == 0
    )
    external_present = [path.as_posix() for path in EXTERNAL_VALIDATION_PATHS if (root / path).is_file()]
    external_status = "DRAFT_PARTIAL" if external_present else "MISSING"
    limitations = receipt.get("residual_limitations", [])
    assert isinstance(limitations, list)
    limitation_lines = "\n".join(f"- {item}" for item in limitations)
    external_lines = (
        "\n".join(f"- `{path}`" for path in external_present)
        if external_present
        else "- No canonical external-validation artifact exists."
    )
    return f"""# KEYSTONE reproducibility report

Status: `DRAFT / PREAUTHORIZATION / MECHANICAL-ONLY`  
System: `KEYSTONE-MPP-F1`  
Current canonical phase: `{state['current_phase']}`  
Overall disposition: `{disposition}`  
Scientific independence: `NOT_ESTABLISHED`  
Independent scientific reproduction: `MISSING`  
External validation: `{external_status}`  
Primary confirmatory results: `NOT_COLLECTED`

This report separates an earlier same-host isolated mechanical replay from
scientific reproduction. It may not promote C001, C002, or C003, may not advance
the canonical phase, and may not convert draft analytic, simulated, or internal
engineering outputs into independently verified scientific evidence.

## Primary-result boundary

The design-layer primary-results planning contract contains **{len(primary_rows)} result slots**.
Every slot remains `authorized=false`, `independent=false`,
`observed_outcome=NOT_COLLECTED`, `estimate=NOT_ESTIMATED`, and
`claim_ceiling=V0 ASSERTED`. The canonical
`05-analysis/results/primary-results.csv` artifact remains `MISSING`.
Therefore this report contains no confirmatory
effect, no deadline result, and no success claim.

## Existing isolated mechanical receipt

| Field | Recorded value |
| --- | --- |
| Receipt generated at | `{receipt.get('generated_at')}` |
| Receipt status | `{receipt.get('status')}` |
| Executor class | `{receipt.get('executor_class')}` |
| Scientific evidence status | `{receipt.get('scientific_evidence_status')}` |
| Commands mechanically passing | `{passed_commands}/{len(commands)}` |
| Source tree unchanged during that replay | `{str(receipt.get('source_tree_unchanged')).lower()}` |
| Isolated copy unchanged during that replay | `{str(receipt.get('isolated_copy_unchanged')).lower()}` |
| Network isolation | `{receipt.get('network_isolation')}` |
| External sharing | `{receipt.get('external_sharing')}` |

The receipt is hash-verified by
`prototype/results/engineering_qa/isolated_reproduction/receipt.json.sha256`.
Its scope is a historical same-host mechanical snapshot, not an independent
scientific verification event.

## Current-tree binding audit

| Binding | Receipt hash | Current hash | Match |
| --- | --- | --- | --- |
| Manuscript source manifest | `{receipt_source_manifest_hash}` | `{current_source_manifest_hash}` | `{str(source_manifest_matches).lower()}` |
| Program state | `{receipt_state_hash}` | `{current_state_hash}` | `{str(state_matches).lower()}` |

Because the current binding disposition is `{disposition}`, the earlier receipt
must not be cited as a clean reconstruction of the current manuscript package.
A fresh replay can establish current mechanical consistency only; it still cannot
satisfy independent scientific reproduction.

## External-validation inventory

{external_lines}

No missing result or validation artifact is silently imputed. A justified `N/A`
would require a narrower claim ceiling and independent signed verification; this
report does not issue that disposition.

## Receipt residual limitations

{limitation_lines}

## Smallest adequate completion path

1. Close `REM-001` with an authenticated independent human INTAKE return.
2. Close novelty and methods gates before any new confirmatory execution.
3. Execute only the separately authorized frozen pilot and preserve failures,
   seeds, environments, exclusions, and deviations.
4. Generate a fresh current-tree mechanical receipt after the integrated evidence
   and manuscript revision is frozen.
5. Obtain a genuinely independent clean-machine reconstruction with authenticated
   identity, competence, conflict, commands, hashes, discrepancies, and signed
   artifact-specific dispositions.
6. Provide external/domain-equivalent validation or formally narrow every claim
   that exceeds simulation/internal evidence.

Until those steps are independently verified, reproducibility remains a draft
mechanical property of selected artifacts—not a scientific gate pass and not a
submission-readiness claim.
"""


def export(root: Path, check: bool) -> None:
    rendered = _render(root)
    output = root / OUTPUT_PATH
    if check:
        try:
            current = output.read_text(encoding="utf-8")
        except OSError as exc:
            raise ReproducibilityReportError(f"cannot read reproducibility report: {exc}") from exc
        if current != rendered:
            raise ReproducibilityReportError("reproducibility report is stale")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        export(args.root.resolve(), args.check)
    except ReproducibilityReportError as exc:
        print(f"reproducibility-report: FAIL: {exc}", file=sys.stderr)
        return 1
    print("reproducibility-report: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
