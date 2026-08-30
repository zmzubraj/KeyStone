#!/usr/bin/env python3
"""Export the dedicated KEYSTONE Foundry gas snapshot as a stable CSV table."""

from __future__ import annotations

import argparse
import csv
import io
import re
from pathlib import Path


TESTS = {
    "testGas_RegisterEpochFiveMembers": (
        "register_epoch",
        "n=5, t=3; duplicate-identity validation enabled",
    ),
    "testGas_OpenAuditThreeMembers": (
        "open_audit",
        "three sampled members; q=3",
    ),
    "testGas_SubmitAuditResponse": (
        "submit_audit_response",
        "first commitment from one sampled custodian",
    ),
    "testGas_MarkInvalidResponse": (
        "mark_invalid_response",
        "admin records a non-zero evidence hash",
    ),
    "testGas_RecordEquivocation": (
        "record_equivocation",
        "second conflicting commitment from one custodian",
    ),
    "testGas_FinalizeAudit": (
        "finalize_audit",
        "two responses for a three-member sample after deadline",
    ),
    "testGas_OpenDispute": (
        "open_dispute",
        "n=5, t=3; all members eligible",
    ),
    "testGas_CancelRequest": (
        "cancel_request",
        "admin cancels one open audit",
    ),
}

LINE = re.compile(
    r"^[^:]+:(?P<test>testGas_[A-Za-z0-9_]+)\(\) \(gas: (?P<gas>[0-9]+)\)$"
)


def render(snapshot: Path) -> str:
    observed: dict[str, int] = {}
    for line in snapshot.read_text(encoding="utf-8").splitlines():
        match = LINE.match(line.strip())
        if match:
            observed[match.group("test")] = int(match.group("gas"))

    missing = sorted(set(TESTS) - set(observed))
    if missing:
        raise SystemExit("missing dedicated gas snapshots: " + ", ".join(missing))

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(("operation", "test", "gas", "measurement_scope", "notes"))
    for test, (operation, notes) in TESTS.items():
        writer.writerow(
            (
                operation,
                test,
                observed[test],
                "Foundry test-body gas; setup excluded; small harness overhead may remain",
                notes,
            )
        )
    return output.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    expected = render(args.snapshot)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"gas report is stale: {args.output}")
        print(f"PASS: gas report matches {args.snapshot}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
