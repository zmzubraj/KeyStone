from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "export_intake_verifier_packet.py"

BEGIN_MARKER = "<!-- BEGIN GENERATED INTAKE SNAPSHOT -->"
END_MARKER = "<!-- END GENERATED INTAKE SNAPSHOT -->"

INPUT_PATHS = (
    "research-case/artifact-registry.csv",
    "research-case/program-state.json",
    "research-case/00-governance/verifier-registry.json",
    "research-case/00-governance/verification-ledger.jsonl",
    "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md",
    "research-case/00-governance/intake-original.md",
    "research-case/00-governance/intake.json",
    "research-case/00-governance/program-charter.md",
    "research-case/00-governance/study-profile.json",
)

REQUIRED_ARTIFACTS = (
    "00-governance/intake-original.md",
    "00-governance/intake.json",
    "00-governance/program-charter.md",
    "00-governance/study-profile.json",
)


def run_cli(project_root: Path, *argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(project_root), *argv],
        text=True,
        capture_output=True,
        check=False,
    )


def copy_inputs(project_root: Path) -> None:
    for rel in INPUT_PATHS:
        src = ROOT / rel
        dst = project_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def write_markers(project_root: Path) -> None:
    path = project_root / "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md"
    path.write_text(
        "# TOP\n\nBEFORE\n\n"
        f"{BEGIN_MARKER}\nPLACEHOLDER SNAPSHOT\n{END_MARKER}\n\nAFTER\n",
        encoding="utf-8",
    )


def split_marked_sections(document: Path) -> tuple[str, str, str]:
    text = document.read_text(encoding="utf-8")
    begin = text.index(BEGIN_MARKER)
    end = text.index(END_MARKER)
    return text[:begin], text[begin + len(BEGIN_MARKER) : end], text[end + len(END_MARKER) :]


def parse_independent_event_count(document_section: str) -> int:
    match = re.search(
        r"Independent verification events for these four artifacts: `(?P<count>\d+)`",
        document_section,
    )
    if not match:
        raise AssertionError("snapshot missing independent event count")
    return int(match.group("count"))


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_rows(project_root: Path) -> list[dict[str, str]]:
    with (project_root / "research-case/artifact-registry.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        return list(csv.DictReader(handle))


def required_rows(project_root: Path) -> list[dict[str, str]]:
    rows = artifact_rows(project_root)
    row_by_path = {row["path"]: row for row in rows if "path" in row}
    return [row_by_path[path] for path in REQUIRED_ARTIFACTS]


def expected_state_tokens(project_root: Path) -> tuple[str, ...]:
    state = json.loads((project_root / "research-case/program-state.json").read_text(encoding="utf-8"))
    return (
        state["status"],
        state["current_phase"],
        state["novelty_status"],
        state["feasibility_decision"],
        state["solution_viability_status"],
        state["acceptance_readiness"],
    )


def mutate_artifact_row(
    project_root: Path,
    *,
    path: str,
    revision: str | None = None,
    sha256: str | None = None,
) -> None:
    csv_path = project_root / "research-case/artifact-registry.csv"
    rows = required_rows(project_root)
    updated = False

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise RuntimeError("artifact-registry.csv has no header")
        new_rows = [row.copy() for row in reader]

    for row in new_rows:
        if row.get("path") == path:
            if revision is not None:
                row["revision"] = str(revision)
            if sha256 is not None:
                row["sha256"] = sha256
            updated = True

    if not updated:
        raise RuntimeError(f"Did not find artifact row {path}")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(new_rows)


def set_malformed_csv_extra_column(project_root: Path) -> None:
    csv_path = project_root / "research-case/artifact-registry.csv"
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise RuntimeError("artifact-registry.csv is unexpectedly empty")
    lines[1] = f"{lines[1]},extra"
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def active_independent_reviewer_ids(verifier_registry: dict[str, object]) -> set[str]:
    entries = verifier_registry.get("entries", [])
    ids = {
        str(entry.get("registry_id"))
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("verifier_type") == "INDEPENDENT_REVIEWER"
        and entry.get("active", True)
    }
    return {value for value in ids if value}


def independent_verification_events(
    ledger_path: Path, verifier_registry: dict[str, object], required_paths: set[str]
) -> list[dict[str, object]]:
    active_ids = active_independent_reviewer_ids(verifier_registry)
    accepted: list[dict[str, object]] = []

    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        event = payload.get("verification_event", {})
        if not isinstance(event, dict):
            continue
        if event.get("independence_mode") != "INDEPENDENT":
            continue

        artifact_path = str(
            event.get("artifact_path")
            or event.get("path")
            or ""
        )
        if artifact_path not in required_paths:
            continue

        verifier_registry_id = event.get("verifier_registry_id")
        if not isinstance(verifier_registry_id, str):
            continue
        if verifier_registry_id not in active_ids:
            continue

        accepted.append(payload)

    return accepted


def test_generation_writes_deterministic_snapshot_and_preserves_prose(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    write_markers(project_root)

    doc = project_root / "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md"
    before_prefix, _, before_suffix = split_marked_sections(doc)

    result = run_cli(project_root)
    assert result.returncode == 0, result.stderr or result.stdout

    after_text = doc.read_text(encoding="utf-8")
    after_prefix, section, after_suffix = split_marked_sections(doc)

    assert after_prefix == before_prefix
    assert after_suffix == before_suffix
    assert "PLACEHOLDER SNAPSHOT" not in after_text

    rows = required_rows(project_root)
    latest_timestamp = max(row["updated_at"] for row in rows)
    assert latest_timestamp in section
    assert "Current phase" in section or "Current status" in section

    state_tokens = expected_state_tokens(project_root)
    for token in state_tokens:
        assert token in section

    trust = json.loads((project_root / "research-case/00-governance/verifier-registry.json").read_text(encoding="utf-8"))
    trust_mode = trust.get("trust_mode") or ""
    assert trust_mode in section

    independent_reviewers = sum(
        1
        for entry in trust.get("entries", [])
        if entry.get("verifier_type") == "INDEPENDENT_REVIEWER"
    )
    assert str(independent_reviewers) in section

    ledger = project_root / "research-case/00-governance/verification-ledger.jsonl"
    independent_events = 0
    for line in ledger.read_text(encoding="utf-8").splitlines():
        payload = json.loads(line)
        event = payload.get("verification_event", {})
        if event.get("independence_mode") == "INDEPENDENT":
            independent_events += 1
    assert str(independent_events) in section

    for row in rows:
        path = row["path"]
        assert (
            f"{path}" in section
            and row["revision"] in section
            and row["sha256"] in section
            and row["status"] in section
            and row["required"] in section
        )
        expected_hash = sha256_hex(project_root / f"research-case/{path}")
        assert expected_hash == row["sha256"]


def test_check_succeeds_after_generation_and_fails_after_registry_mutation(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    write_markers(project_root)

    assert run_cli(project_root).returncode == 0
    assert run_cli(project_root, "--check").returncode == 0

    mutate_artifact_row(project_root, path=REQUIRED_ARTIFACTS[0], revision="999")
    check_after_revision = run_cli(project_root, "--check")
    assert check_after_revision.returncode != 0
    assert "error" in (check_after_revision.stdout + check_after_revision.stderr).lower()


def test_hash_mismatch_fails_and_does_not_rewrite_document(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    write_markers(project_root)

    doc = project_root / "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md"
    assert run_cli(project_root).returncode == 0
    before = doc.read_text(encoding="utf-8")

    target = project_root / f"research-case/{REQUIRED_ARTIFACTS[0]}"
    target.write_text(target.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    check = run_cli(project_root, "--check")
    assert check.returncode != 0
    assert "error" in (check.stdout + check.stderr).lower()
    assert doc.read_text(encoding="utf-8") == before


def test_missing_required_artifact_row_fails_closed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    write_markers(project_root)

    mutate_artifact_row(
        project_root,
        path=REQUIRED_ARTIFACTS[0],
        sha256="000000000000000000000000000000000000000000000000000000000000000000",
    )
    result = run_cli(project_root)

    assert result.returncode != 0
    output = (result.stdout + result.stderr).lower()
    assert "error" in output or "errno 2" in output or "no such file" in output


def test_malformed_csv_with_extra_columns_fails_closed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    write_markers(project_root)

    set_malformed_csv_extra_column(project_root)
    result = run_cli(project_root)

    assert result.returncode != 0
    output = (result.stdout + result.stderr).lower()
    assert "error" in output or "errno 2" in output or "no such file" in output


def test_independent_event_count_excludes_non_target_artifact_without_failing_fixture_paths(
    tmp_path: Path,
) -> None:
    ledger_path = tmp_path / "verification-ledger.jsonl"
    ledger_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "verification_event": {
                            "artifact_path": "00-governance/intake-original.md",
                            "independence_mode": "INDEPENDENT",
                            "verifier_registry_id": "independent-reviewer-01",
                        }
                    }
                ),
                json.dumps(
                    {
                        "verification_event": {
                            "artifact_path": "01-novelty/problem-investigation.md",
                            "independence_mode": "INDEPENDENT",
                            "verifier_registry_id": "independent-reviewer-01",
                        }
                    }
                ),
                ]
        )
        + "\n",
        encoding="utf-8",
    )

    verifier_registry = {
        "entries": [
            {
                "registry_id": "independent-reviewer-01",
                "verifier_type": "INDEPENDENT_REVIEWER",
                "active": True,
            },
            {
                "registry_id": "mechanical-reviewer-01",
                "verifier_type": "ROOT_MECHANICAL_CHECK",
                "active": True,
            },
        ]
    }

    events = independent_verification_events(
        ledger_path,
        verifier_registry,
        set(REQUIRED_ARTIFACTS),
    )
    assert len(events) == 1
    assert events[0]["verification_event"]["artifact_path"] == "00-governance/intake-original.md"


def test_independent_event_count_excludes_missing_verifier_registry_id(
    tmp_path: Path,
) -> None:
    ledger_path = tmp_path / "verification-ledger.jsonl"
    ledger_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "verification_event": {
                            "artifact_path": "00-governance/intake-original.md",
                            "independence_mode": "INDEPENDENT",
                        }
                    }
                ),
                json.dumps(
                    {
                        "verification_event": {
                            "artifact_path": "00-governance/intake.json",
                            "independence_mode": "INDEPENDENT",
                            "verifier_registry_id": "",
                        }
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    verifier_registry = {
        "entries": [
            {
                "registry_id": "independent-reviewer-01",
                "verifier_type": "INDEPENDENT_REVIEWER",
                "active": True,
            }
        ]
    }

    events = independent_verification_events(
        ledger_path,
        verifier_registry,
        set(REQUIRED_ARTIFACTS),
    )
    assert len(events) == 0


def test_independent_event_count_excludes_unknown_verifier_registry_id(
    tmp_path: Path,
) -> None:
    ledger_path = tmp_path / "verification-ledger.jsonl"
    ledger_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "verification_event": {
                            "artifact_path": "00-governance/study-profile.json",
                            "independence_mode": "INDEPENDENT",
                            "verifier_registry_id": "rogue-reviewer-999",
                        }
                    }
                )
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    verifier_registry = {
        "entries": [
            {
                "registry_id": "independent-reviewer-01",
                "verifier_type": "INDEPENDENT_REVIEWER",
                "active": True,
            }
        ]
    }

    events = independent_verification_events(
        ledger_path,
        verifier_registry,
        set(REQUIRED_ARTIFACTS),
    )
    assert len(events) == 0


def test_cli_count_uses_only_valid_required_independent_events(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)
    write_markers(project_root)

    registry_path = project_root / "research-case/00-governance/verifier-registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": 4,
                "registry_revision": 1,
                "trust_mode": "CASE_LOCAL_MECHANICAL_ONLY",
                "registry_signing_key_id": "runtime-governance",
                "trust_root_fingerprint": "",
                "entries": [
                    {
                        "registry_id": "independent-reviewer-01",
                        "verifier_type": "INDEPENDENT_REVIEWER",
                        "active": True,
                        "identity_pattern": "^independent-reviewer-01$",
                    },
                    {
                        "registry_id": "independent-reviewer-02",
                        "verifier_type": "INDEPENDENT_REVIEWER",
                        "active": False,
                        "identity_pattern": "^inactive-reviewer$",
                    },
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    ledger_path = project_root / "research-case/00-governance/verification-ledger.jsonl"
    ledger_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "verification_event": {
                            "artifact_path": "00-governance/intake-original.md",
                            "independence_mode": "INDEPENDENT",
                            "verifier_registry_id": "independent-reviewer-01",
                        }
                    }
                ),
                json.dumps(
                    {
                        "verification_event": {
                            "artifact_path": "01-novelty/problem-investigation.md",
                            "independence_mode": "INDEPENDENT",
                            "verifier_registry_id": "independent-reviewer-01",
                        }
                    }
                ),
                json.dumps(
                    {
                        "verification_event": {
                            "artifact_path": "00-governance/intake.json",
                            "independence_mode": "INDEPENDENT",
                        }
                    }
                ),
                json.dumps(
                    {
                        "verification_event": {
                            "artifact_path": "00-governance/program-charter.md",
                            "independence_mode": "INDEPENDENT",
                            "verifier_registry_id": "rogue-reviewer-99",
                        }
                    }
                ),
                json.dumps(
                    {
                        "verification_event": {
                            "artifact_path": "00-governance/study-profile.json",
                            "independence_mode": "INDEPENDENT",
                            "verifier_registry_id": "independent-reviewer-02",
                        }
                    }
                ),
                json.dumps(
                    {
                        "verification_event": {
                            "artifact_path": "00-governance/study-profile.json",
                            "independence_mode": "MECHANICAL",
                            "verifier_registry_id": "independent-reviewer-01",
                        }
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    assert run_cli(project_root).returncode == 0
    generated = project_root / "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md"
    _, section, _ = split_marked_sections(generated)

    event_count = parse_independent_event_count(section)
    assert event_count == 1


def test_missing_markers_fail_closed_and_do_not_modify_text(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    copy_inputs(project_root)

    doc = project_root / "docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md"
    doc.write_text("BEFORE\n", encoding="utf-8")
    original = doc.read_text(encoding="utf-8")

    result = run_cli(project_root)
    assert result.returncode != 0
    output = (result.stdout + result.stderr).lower()
    assert "marker" in output or "errno 2" in output or "not found" in output
    assert doc.read_text(encoding="utf-8") == original
