#!/usr/bin/env python3
"""Export the frozen, non-executable primary-results contract without observations."""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
import re
import sys


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = Path("research-case/program-state.json")
CHARTER_PATH = Path("research-case/00-governance/program-charter.md")
PILOT_CONTRACT_PATH = Path("research-case/02-feasibility/pilot-run-contract.csv")
ANALYSIS_PLAN_PATH = Path("research-case/03-design/analysis-plan.md")
OUTPUT_PATH = Path("research-case/05-analysis/results/primary-results.csv")

REQUIRED_STATE = {
    "status": "ACTIVE",
    "current_phase": "INTAKE",
    "resume_from": "INTAKE",
    "novelty_status": "UNRESOLVED",
    "feasibility_decision": "UNASSESSED",
    "solution_viability_status": "ASSERTED_ONLY",
    "acceptance_readiness": "NOT_ASSESSABLE",
}
REQUIRED_RESULT_IDS = (
    "RID-C001-SEP-001",
    "RID-C001-STATIC-001",
    "RID-C002-CRYPTO-001",
    "RID-C002-CONTRACT-001",
    "RID-C003-IID-001",
    "RID-C003-CORR-001",
    "RID-C003-STRAT-001",
    "RID-C003-SW-001",
    "RID-C003-DEADLINE-001",
)
FIELDS = (
    "result_id",
    "estimand_id",
    "claim_ids",
    "mpp_lane",
    "result_class",
    "decision_role",
    "experimental_unit",
    "denominator",
    "planned_replicates",
    "execution_status",
    "authorized",
    "independent",
    "observed_outcome",
    "estimate",
    "uncertainty",
    "analysis_status",
    "evidence_origin",
    "evidence_maturity",
    "claim_ceiling",
    "source_contract",
    "planned_output",
    "required_predecessors",
    "notes",
)


class PrimaryResultsContractError(RuntimeError):
    """Raised when the contract cannot be exported without result leakage."""


def _state(root: Path) -> dict[str, object]:
    try:
        payload = json.loads((root / STATE_PATH).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PrimaryResultsContractError(f"cannot read canonical program state: {exc}") from exc
    if not isinstance(payload, dict):
        raise PrimaryResultsContractError("canonical program state must be an object")
    for field, expected in REQUIRED_STATE.items():
        actual = payload.get(field)
        if actual != expected:
            raise PrimaryResultsContractError(f"canonical {field} expected {expected}, got {actual}")
    return payload


def _author_boundary(root: Path) -> None:
    try:
        charter = (root / CHARTER_PATH).read_text(encoding="utf-8").lower()
    except OSError as exc:
        raise PrimaryResultsContractError(f"cannot read program charter: {exc}") from exc
    phrases = ("final author order", "corresponding-author", "affiliation wording", "remain deferred")
    if not all(phrase in charter for phrase in phrases):
        raise PrimaryResultsContractError("program charter does not preserve author metadata deferral")


def _pilot_rows(root: Path) -> list[dict[str, str]]:
    try:
        with (root / PILOT_CONTRACT_PATH).open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise PrimaryResultsContractError(f"cannot read pilot contract: {exc}") from exc
    if tuple(row.get("result_id", "") for row in rows) != REQUIRED_RESULT_IDS:
        raise PrimaryResultsContractError("pilot contract result IDs or ordering drifted")
    for row in rows:
        result_id = row["result_id"]
        if row.get("authorized") != "false":
            raise PrimaryResultsContractError(f"{result_id} authorized must remain false")
        if row.get("independent") != "false":
            raise PrimaryResultsContractError(f"{result_id} independent must remain false")
        if row.get("observed_outcome") != "NOT_COLLECTED":
            raise PrimaryResultsContractError(f"{result_id} observed_outcome must remain NOT_COLLECTED")
        if row.get("output_status") != "MISSING_NOT_AUTHORIZED":
            raise PrimaryResultsContractError(f"{result_id} output_status must remain MISSING_NOT_AUTHORIZED")
        allowed = {
            "BLOCKED_PENDING_GATE",
            "EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE",
            "EXCLUDED_PENDING_ENVIRONMENT_PROFILE",
        }
        if row.get("execution_status") not in allowed:
            raise PrimaryResultsContractError(f"{result_id} has non-fail-closed execution_status")
    return rows


def _estimand_map(root: Path) -> dict[str, str]:
    try:
        text = (root / ANALYSIS_PLAN_PATH).read_text(encoding="utf-8")
    except OSError as exc:
        raise PrimaryResultsContractError(f"cannot read analysis plan: {exc}") from exc
    if "does not authorize\nexecution" not in text.lower() and "does not authorize execution" not in text.lower():
        raise PrimaryResultsContractError("analysis plan lacks its non-authorization boundary")
    matches = re.findall(r"\| `(EST-\d{2})` \|.*?\| `(RID-[A-Z0-9-]+)` \|", text)
    mapping = {result_id: estimand_id for estimand_id, result_id in matches}
    expected = {result_id: f"EST-{index:02d}" for index, result_id in enumerate(REQUIRED_RESULT_IDS, start=1)}
    if mapping != expected:
        raise PrimaryResultsContractError("analysis plan estimand-to-result mapping drifted")
    return mapping


def _render(rows: list[dict[str, str]], estimands: dict[str, str]) -> bytes:
    output: list[dict[str, str]] = []
    for row in rows:
        result_id = row["result_id"]
        output.append(
            {
                "result_id": result_id,
                "estimand_id": estimands[result_id],
                "claim_ids": row["claim_ids"],
                "mpp_lane": row["mpp_lane"],
                "result_class": row["result_class"],
                "decision_role": row["decision_role"],
                "experimental_unit": row["experimental_unit"],
                "denominator": row["denominator"],
                "planned_replicates": row["planned_replicates"],
                "execution_status": row["execution_status"],
                "authorized": "false",
                "independent": "false",
                "observed_outcome": "NOT_COLLECTED",
                "estimate": "NOT_ESTIMATED",
                "uncertainty": "NOT_ESTIMATED",
                "analysis_status": "DRAFT_RESULT_CONTRACT_ONLY",
                "evidence_origin": "NO_NEW_EVIDENCE",
                "evidence_maturity": "V0 ASSERTED",
                "claim_ceiling": "V0 ASSERTED",
                "source_contract": PILOT_CONTRACT_PATH.as_posix(),
                "planned_output": row["planned_output"],
                "required_predecessors": row["required_predecessors"],
                "notes": "Schema-complete preauthorization result slot only; no observation, execution, verification, or phase promotion.",
            }
        )
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(output)
    return stream.getvalue().encode("utf-8")


def export(root: Path, check: bool) -> None:
    _state(root)
    _author_boundary(root)
    rendered = _render(_pilot_rows(root), _estimand_map(root))
    output = root / OUTPUT_PATH
    if check:
        try:
            current = output.read_bytes()
        except OSError as exc:
            raise PrimaryResultsContractError(f"cannot read primary-results contract: {exc}") from exc
        if current != rendered:
            raise PrimaryResultsContractError("primary-results contract is stale")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(rendered)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        export(args.root.resolve(), args.check)
    except PrimaryResultsContractError as exc:
        print(f"primary-results-contract: FAIL: {exc}", file=sys.stderr)
        return 1
    print("primary-results-contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
