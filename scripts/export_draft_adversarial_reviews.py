#!/usr/bin/env python3
"""Generate deterministic internal draft adversarial reviews for KEYSTONE."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys

from check_manuscript_alignment import AlignmentError, check_alignment


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
STATE_RELATIVE = Path("research-case/program-state.json")
MANUSCRIPT_RELATIVE = Path("research-case/07-manuscript/manuscript.md")
CLAIM_MATRIX_RELATIVE = Path("research-case/07-manuscript/claim-evidence-matrix.csv")
NOVELTY_RECON_RELATIVE = Path("research-case/01-novelty/novelty_reconciliation.md")
NOVELTY_MATRIX_RELATIVE = Path("research-case/01-novelty/novelty-matrix.csv")
CITATION_AUDIT_RELATIVE = Path("research-case/01-novelty/citation-audit.md")
REDLINES_RELATIVE = Path("research-case/01-novelty/independent-citation-audit/manuscript_language_redlines.md")
OUTPUTS = {
    "editor": Path("research-case/08-validation/reviews/editor.md"),
    "novelty": Path("research-case/08-validation/reviews/novelty-domain.md"),
    "clarity": Path("research-case/08-validation/reviews/clarity-coherence.md"),
}
EXPECTED_STATE = {
    "status": "ACTIVE",
    "current_phase": "INTAKE",
    "resume_from": "INTAKE",
    "novelty_status": "UNRESOLVED",
    "feasibility_decision": "UNASSESSED",
    "solution_viability_status": "ASSERTED_ONLY",
    "acceptance_readiness": "NOT_ASSESSABLE",
    "maturity_stage": "CONCEPT",
}


class ReviewError(RuntimeError):
    """Raised when the draft review inputs drift from the expected contract."""


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ReviewError(f"cannot read required file {path}: {exc}") from exc


def _check_state(root: Path) -> None:
    import json

    path = root / STATE_RELATIVE
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        raise ReviewError(f"cannot read canonical program state {path}: {exc}") from exc
    if not isinstance(state, dict):
        raise ReviewError(f"canonical program state must be a JSON object: {path}")
    for field, expected in EXPECTED_STATE.items():
        actual = state.get(field)
        if actual != expected:
            raise ReviewError(
                f"canonical state mismatch: {field} expected {expected}, got {actual}"
            )


def _line_ref(root: Path, relative: Path, needle: str) -> str:
    path = root / relative
    for number, line in enumerate(_read_text(path).splitlines(), start=1):
        if needle in line:
            return f"{relative.as_posix()}:{number}"
    raise ReviewError(f"cannot locate required evidence marker in {relative}: {needle}")


def _evidence(refs: dict[str, str], *keys: str) -> str:
    return "; ".join(f"`{refs[key]}`" for key in keys)


def _render_editor(refs: dict[str, str], today: str) -> str:
    return "\n".join(
        [
            "# Editor Review",
            "",
            "Status: `DRAFT / INTERNAL DEVELOPMENTAL REVIEW / NOT INDEPENDENT`  ",
            "System: `KEYSTONE-MPP-F1`  ",
            f"Date: `{today}`  ",
            "Canonical phase: `INTAKE`",
            "",
            "This review is an internal editorial challenge only. It does not assert novelty,",
            "independent review, venue fit, phase promotion, or submission readiness.",
            "",
            "## Supported stage",
            "",
            "- Lowest defensible developmental stage: `NOT ASSESSABLE`.",
            "- Strongest desk-reject sentence: novelty is still unresolved, the canonical primary ledger remains missing, and the robustness and negative ledgers are only unauthorized preauthorization drafts, so an editor cannot yet assess contribution strength on final evidence.",
            "",
            "## Verified facts",
            "",
            f"- The manuscript is explicitly marked pre-manuscript and pre-authorization at {_evidence(refs, 'manuscript_status')}.",
            f"- The reconciled novelty state remains `REFRAME` / `NOVELTY_UNRESOLVED` at {_evidence(refs, 'novelty_reframe', 'novelty_blocker')}.",
            f"- The Results and Evaluation sections distinguish the missing canonical primary ledger and authorized confirmatory evidence from the present draft robustness and negative ledgers at {_evidence(refs, 'results_preliminary', 'results_missing_ledgers', 'eval_missing_outputs', 'robustness_ledger_boundary', 'negative_ledger_boundary')}.",
            "",
            "## Findings",
            "",
            "| ID | Severity | Confidence | Disposition | Evidence | Impacted boundary | Recommended next step |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            f"| ED-01 | High | High | FAIL | {_evidence(refs, 'related_work_pending', 'novelty_reframe', 'novelty_blocker')} | Novelty and editor screen | Keep the manuscript in the narrowed `REFRAME` lane and do not pitch broad protocol novelty until a signed independent novelty review exists. |",
            f"| ED-02 | High | High | FAIL | {_evidence(refs, 'results_preliminary', 'results_missing_ledgers', 'eval_missing_outputs', 'robustness_ledger_boundary', 'negative_ledger_boundary')} | Results sufficiency | Produce the canonical primary ledger through authorized execution, then independently review and prospectively authorize any confirmatory robustness or negative-result use instead of relying on draft preauthorization ledgers or display assets. |",
            f"| ED-03 | Medium | High | PARTIAL | {_evidence(refs, 'abstract_boundaries', 'intro_claims')} | Claim honesty | Preserve the current bounded wording because it prevents the manuscript from silently outrunning the evidence ceiling. |",
            f"| ED-04 | Medium | Medium | PARTIAL | {_evidence(refs, 'mechanical_rerun', 'data_code_limits')} | Reproducibility narrative | Convert the same-host mechanical replay into a later independent reproduction plan, but keep the present text because it accurately rejects stronger reproducibility claims. |",
            f"| ED-05 | High | High | FAIL | {_evidence(refs, 'limitations_missing_reviews', 'limitations_missing_submission_artifacts')} | Submission readiness | Build the missing adversarial-review, venue, reporting, hermetic-build, and human-approval artifacts before any venue-facing claim. |",
            "",
            "## Residual risks",
            "",
            "- Even a cleaner editorial narrative would not remove the current gate blockers because the missing evidence is substantive, not stylistic.",
            "- The current title can remain for drafting, but it should be rechecked against the final novelty and evidence ceiling before venue selection.",
            "",
        ]
    )


def _render_novelty(refs: dict[str, str], today: str) -> str:
    return "\n".join(
        [
            "# Novelty and Domain Review",
            "",
            "Status: `DRAFT / INTERNAL DEVELOPMENTAL REVIEW / NOT INDEPENDENT`  ",
            "System: `KEYSTONE-MPP-F1`  ",
            f"Date: `{today}`  ",
            "Canonical phase: `INTAKE`",
            "",
            "This review is a local novelty-domain challenge only. It does not certify novelty,",
            "exhaustive prior-art coverage, or external scientific verification.",
            "",
            "## Supported stage",
            "",
            "- Lowest defensible developmental stage: `NOT ASSESSABLE`.",
            "- Strongest novelty objection: the manuscript is safe only while it stays with the narrowed serviceability-distinction claim; any drift toward first-system, new primitive, new context-bound decryption, or timing-free accountability language is already contradicted by the bounded prior-art record.",
            "",
            "## Verified facts",
            "",
            f"- Broad novelty is explicitly rejected in the reconciled novelty review at {_evidence(refs, 'novelty_reframe', 'predecessor_cluster')}.",
            f"- The canonical citation audit says the bibliography is still not promotion-safe at {_evidence(refs, 'citation_not_certified', 'citation_access_limits')}.",
            f"- The independent redlines already define unsafe versus safer novelty language at {_evidence(refs, 'redline_first', 'redline_context', 'redline_deadline')}.",
            "",
            "## Findings",
            "",
            "| ID | Severity | Confidence | Disposition | Evidence | Impacted boundary | Recommended next step |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            f"| ND-01 | High | High | FAIL | {_evidence(refs, 'novelty_reframe', 'predecessor_cluster')} | Central novelty claim | Keep broad protocol novelty rejected; only the narrow dispute-serviceability distinction may remain under review. |",
            f"| ND-02 | High | High | FAIL | {_evidence(refs, 'novelty_blocker', 'citation_not_certified', 'citation_access_limits')} | Novelty closure | Obtain authenticated independent novelty review and final submission-time metadata refresh before any stronger novelty wording. |",
            f"| ND-03 | Medium | High | PARTIAL | {_evidence(refs, 'related_work_pending', 'adopted_components', 'redline_context')} | Related-work framing | The manuscript mostly respects adopted-component boundaries, but the section is still placeholder-heavy and should stay explicitly provisional. |",
            f"| ND-04 | Medium | Medium | PARTIAL | {_evidence(refs, 'title_line', 'claim_matrix_c001', 'redline_first')} | Title and contribution emphasis | Keep the current draft title in the narrowed serviceability-distinction lane, but freeze the final title only after the novelty-safe contribution sentence is fully settled. |",
            f"| ND-05 | Medium | High | FAIL | {_evidence(refs, 'redline_deadline', 'claim_matrix_c003')} | Accountability and deadline wording | Preserve timing-qualified, conditional deadline language and do not imply timing-free blame or external deadline success. |",
            "",
            "## Residual risks",
            "",
            "- The bounded public-source search can reject overclaiming, but it cannot certify absence of proprietary or inaccessible predecessors.",
            "- The surviving differentiator is still only a hypothesis until later formal, empirical, and independent review artifacts exist.",
            "",
        ]
    )


def _render_clarity(refs: dict[str, str], today: str) -> str:
    return "\n".join(
        [
            "# Clarity and Coherence Review",
            "",
            "Status: `DRAFT / INTERNAL DEVELOPMENTAL REVIEW / NOT INDEPENDENT`  ",
            "System: `KEYSTONE-MPP-F1`  ",
            f"Date: `{today}`  ",
            "Canonical phase: `INTAKE`",
            "",
            "This review is a local writing and coherence challenge only. It does not replace",
            "scientific review, editor judgment, or accountable-human manuscript approval.",
            "",
            "## Supported stage",
            "",
            "- Lowest defensible developmental stage: `NOT ASSESSABLE`.",
            "- Strongest coherence objection: the manuscript is internally honest and traceable, but it still reads like a controlled evidence shell rather than a decision-complete paper because too many core sections remain explicitly contingent on future gates.",
            "",
            "## Verified facts",
            "",
            f"- The manuscript carries one stable throughline from abstract to discussion: ciphertext availability is not the same as dispute-key serviceability at {_evidence(refs, 'abstract_boundaries', 'discussion_safe_interpretation')}.",
            f"- The display map for D1-D8 and F1-F5 is explicit at {_evidence(refs, 'diagram_map', 'figure_map', 'table_map')}.",
            f"- Several key sections remain deliberately provisional at {_evidence(refs, 'related_work_pending', 'conclusion_pending', 'limitations_missing_submission_artifacts')}.",
            "",
            "## Findings",
            "",
            "| ID | Severity | Confidence | Disposition | Evidence | Impacted boundary | Recommended next step |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            f"| CC-01 | Medium | High | PARTIAL | {_evidence(refs, 'abstract_boundaries', 'intro_claims', 'discussion_safe_interpretation')} | Core narrative coherence | Preserve the current single-message structure because the main distinction remains consistent across the draft. |",
            f"| CC-02 | Medium | High | FAIL | {_evidence(refs, 'related_work_pending', 'conclusion_pending')} | Standalone readability | Replace placeholder section openers with evidence-bound prose once the corresponding novelty and results gates produce final artifacts. |",
            f"| CC-03 | Medium | Medium | FAIL | {_evidence(refs, 'intro_claims', 'claim_matrix_c003', 'pc03_jargon')} | Reader load | Reduce internal code names and gate jargon in venue-facing prose by translating them into one reader-facing contribution map after the underlying artifacts stabilize. |",
            f"| CC-04 | Low | High | PARTIAL | {_evidence(refs, 'diagram_map', 'figure_map', 'table_map')} | Cross-artifact navigation | Keep the current explicit diagram/figure/table mapping because it materially improves auditability for later integration. |",
            f"| CC-05 | Medium | High | FAIL | {_evidence(refs, 'limitations_missing_reviews', 'limitations_missing_submission_artifacts', 'data_code_limits')} | Ending coherence | The paper cannot yet land a full conclusion because the current ending must still point outward to missing review, venue, and approval artifacts. |",
            "",
            "## Residual risks",
            "",
            "- Tightening prose alone would risk hiding legitimate uncertainty; clarity work should follow, not precede, gate-resolving evidence.",
            "- If future sections add results without rebalancing the introduction and conclusion, the manuscript may become internally inconsistent even if each new artifact is individually valid.",
            "",
        ]
    )


def render_reviews(root: Path) -> dict[Path, str]:
    root = root.resolve()
    _check_state(root)
    try:
        check_alignment(root)
    except AlignmentError as exc:
        raise ReviewError(f"manuscript alignment precondition failed: {exc}") from exc
    refs = {
        "title_line": _line_ref(root, MANUSCRIPT_RELATIVE, "Dispute-Key Serviceability Distinct from Ciphertext Availability"),
        "manuscript_status": _line_ref(root, MANUSCRIPT_RELATIVE, "Status: `DRAFT / PRE-MANUSCRIPT / PRE-AUTHORIZATION`"),
        "abstract_boundaries": _line_ref(root, MANUSCRIPT_RELATIVE, "Novelty remains unresolved,"),
        "intro_claims": _line_ref(root, MANUSCRIPT_RELATIVE, "The three manuscript-level claim anchors are:"),
        "related_work_pending": _line_ref(root, MANUSCRIPT_RELATIVE, "`PENDING — NOVELTY_UNRESOLVED.`"),
        "adopted_components": _line_ref(root, MANUSCRIPT_RELATIVE, "DLEQ-style proof lineage are adopted building blocks"),
        "results_preliminary": _line_ref(root, MANUSCRIPT_RELATIVE, "The present results surface is an explicitly preliminary inventory."),
        "results_missing_ledgers": _line_ref(root, MANUSCRIPT_RELATIVE, "replace missing authorized `05-analysis` evidence"),
        "mechanical_rerun": _line_ref(root, MANUSCRIPT_RELATIVE, "A second-agent, same-host isolated-copy mechanical rerun"),
        "eval_missing_outputs": _line_ref(root, MANUSCRIPT_RELATIVE, "Missing or blocked evaluation outputs include the"),
        "negative_ledger_boundary": _line_ref(root, MANUSCRIPT_RELATIVE, "The canonical draft `05-analysis/results/negative-findings.csv` now records"),
        "robustness_ledger_boundary": _line_ref(root, MANUSCRIPT_RELATIVE, "The canonical draft `05-analysis/results/robustness-and-boundaries.csv` now"),
        "figure_map": _line_ref(root, MANUSCRIPT_RELATIVE, "The five available quantitative figures are included below only"),
        "table_map": _line_ref(root, MANUSCRIPT_RELATIVE, "The editable T1–T8 package is now available"),
        "discussion_safe_interpretation": _line_ref(root, MANUSCRIPT_RELATIVE, "The current safe interpretation is that ciphertext availability"),
        "pc03_jargon": _line_ref(root, MANUSCRIPT_RELATIVE, "The PC03 amendment,"),
        "limitations_missing_reviews": _line_ref(root, MANUSCRIPT_RELATIVE, "Independent threshold-cryptography and distributed-systems reviews are"),
        "limitations_missing_submission_artifacts": _line_ref(root, MANUSCRIPT_RELATIVE, "No venue portfolio, current reporting checklist, hermetic PDF package,"),
        "conclusion_pending": _line_ref(root, MANUSCRIPT_RELATIVE, "`PENDING — EVIDENCE-BOUND SYNTHESIS.`"),
        "data_code_limits": _line_ref(root, MANUSCRIPT_RELATIVE, "not imply evidence authorization or final reproducibility."),
        "diagram_map": _line_ref(root, MANUSCRIPT_RELATIVE, "The following diagram callouts bind the current editable sources"),
        "claim_matrix_c001": _line_ref(root, CLAIM_MATRIX_RELATIVE, "We formalize dispute-key availability"),
        "claim_matrix_c003": _line_ref(root, CLAIM_MATRIX_RELATIVE, "RID-C003-DEADLINE-001 absent"),
        "novelty_reframe": _line_ref(root, NOVELTY_RECON_RELATIVE, "`REFRAME` the broad novelty wording"),
        "novelty_blocker": _line_ref(root, NOVELTY_RECON_RELATIVE, "Novelty remains `UNRESOLVED` because:"),
        "predecessor_cluster": _line_ref(root, NOVELTY_MATRIX_RELATIVE, "Composite-Predecessor-Cluster"),
        "citation_not_certified": _line_ref(root, CITATION_AUDIT_RELATIVE, "bibliography-certified enough for safe manuscript promotion"),
        "citation_access_limits": _line_ref(root, CITATION_AUDIT_RELATIVE, "no new browsing or proprietary index access was performed here;"),
        "redline_first": _line_ref(root, REDLINES_RELATIVE, "KEYSTONE is the first protocol to prove dispute-key availability"),
        "redline_context": _line_ref(root, REDLINES_RELATIVE, "We introduce a new context-bound threshold decryption mechanism."),
        "redline_deadline": _line_ref(root, REDLINES_RELATIVE, "Missed deadlines prove which committee members are guilty."),
    }
    today = date.today().isoformat()
    return {
        OUTPUTS["editor"]: _render_editor(refs, today),
        OUTPUTS["novelty"]: _render_novelty(refs, today),
        OUTPUTS["clarity"]: _render_clarity(refs, today),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        outputs = render_reviews(root)
    except ReviewError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for relative, expected in outputs.items():
        path = root / relative
        if args.check:
            if not path.is_file():
                print(f"error: missing generated review {relative}", file=sys.stderr)
                return 1
            actual = _read_text(path)
            if actual != expected:
                print(f"error: stale generated review {relative}", file=sys.stderr)
                return 1
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8")
        print(f"wrote {relative.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
