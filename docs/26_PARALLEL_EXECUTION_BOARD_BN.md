# KEYSTONE-MPP-F1 — Parallel Execution Board

**Date:** `2026-08-30`  
**Mode:** bounded internal acceleration only  
**Gate policy:** no lane may self-promote the research phase

## 1. Current top-level state

- `current_phase = INTAKE`
- `blocking gate = REM-001`
- `acceptance_readiness = NOT_ASSESSABLE`
- `author metadata freeze = DEFERRED`

This board exists to reduce coordination loss while the external INTAKE blocker remains open.

## 2. Root-owned non-parallel surfaces

নিচের জিনিসগুলো root integration owner ছাড়া আর কেউ final write ownership নেবে না:

- `research-case/program-state.json`
- `research-case/artifact-registry.csv`
- `research-case/orchestration-plan.json`
- final phase decisions
- final claim-ceiling decisions
- any `PROCEED` / phase-advance action

## 3. Safe active lanes

| Lane | Current purpose | Owned scope | Depends on | Current admissible output |
| --- | --- | --- | --- | --- |
| `intake_verifier_packet_owner` | REM-001 packet coherence and handoff clarity | `docs/20_*`, `docs/23_*`, `docs/24_*`, `review-packets/KEYSTONE-MPP-F1-intake-*` | current frozen intake only | stable packet + stable SOP + stable template |
| `narrow_novelty_refresh_owner` | REM-002 prep without transfer | `01-novelty/*`, `docs/21_*`, `09-submission/novelty-refresh.md` | `REM-001` still open but packet prep allowed | challenge-ready novelty package bounded to `REFRAME` |
| `result_blind_methods_owner` | REM-003 prep without execution | `03-design/*`, selected `02-feasibility/*`, `docs/22_*` | novelty wording ceiling stable | accepted draft methods packet |
| `deadline_pilot_contract_owner` | REM-004 planning surface only | `04-data/*`, planning-only `05-analysis/*` | `REM-003` conceptual interface | execution checklist + provenance contract only |
| `visual_lineage_owner` | REM-007 and REM-012 draft lineage closure | `06-visuals/*`, `paper/tables/*`, `07-manuscript/source-manifest.json` | evidence IDs stable | lineage-complete draft visual package |
| `manuscript_claim_integration_owner` | claim-safe manuscript integration | `07-manuscript/*`, `paper/preauthorization-build/*` | novelty + methods + visuals interface stable | claim-capped draft manuscript revision |
| `submission_package_owner` | venue and submission QA preparation | `09-submission/*` | integrated manuscript exists | non-promoting submission QA package |

## 4. Unsafe lanes

নিচের কাজগুলো parallelize করা যাবে না:

- same file-এ simultaneous edits
- independent review and producer update by same owner
- novelty verdict issuance
- methods approval issuance
- phase promotion
- final author order/corresponding-author/affiliation freeze
- external transfer authorization
- final acceptance-readiness claim

## 5. Dependency spine

```text
REM-001
  -> REM-002
  -> REM-003
      -> REM-004
      -> REM-007
      -> REM-012
          -> REM-005
              -> REM-006
              -> REM-008
                  -> REM-009
                      -> REM-011
                          -> HUMAN APPROVAL
```

Interpretation:

- lane work can continue as draft preparation,
- but serial scientific advancement still follows the dependency spine above.

## 6. Lane-level done conditions

| Lane | Done only if |
| --- | --- |
| `intake_verifier_packet_owner` | packet, template, SOP, and handoff note all current and hash-matched |
| `narrow_novelty_refresh_owner` | bounded novelty packet exists and broad primitive claim stays rejected |
| `result_blind_methods_owner` | design packet is frozen enough for external methods review without outcome leakage |
| `deadline_pilot_contract_owner` | every planned result ID, provenance rule, and stop condition is explicit without execution |
| `visual_lineage_owner` | T/F/D assets, manifests, and captions align without introducing unsupported outputs |
| `manuscript_claim_integration_owner` | manuscript wording stays inside C001-C003 ceilings and current figure boundary |
| `submission_package_owner` | venue/rule/checklist package exists but does not imply readiness before blockers close |

## 7. Recommended next internal sequence

1. keep `REM-001` packet path stable
2. keep `REM-002` and `REM-003` packets current but non-transferable
3. tighten manuscript/visual lineage so no future evidence is silently treated as present
4. prepare venue/checklist shell only as draft
5. wait for authenticated external INTAKE return before any phase advance

## 8. Current practical status

As of `2026-08-30`:

- external intake packet exists
- novelty packet exists
- methods packet exists
- preauthorization draft build exists
- acceptance-readiness gap report exists
- manuscript assembly inventory exists

Therefore the workspace is coordination-ready for bounded internal work, but not yet scientifically cleared for the next serial phase.
