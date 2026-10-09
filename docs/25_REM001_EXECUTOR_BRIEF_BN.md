# KEYSTONE-MPP-F1 — REM-001 Executor Brief

**Date:** `2026-08-30`  
**Purpose:** `REM-001` close করার জন্য accountable human, workspace operator, registry administrator, এবং independent reviewer-এর exact handoff sequence এক পাতায় নামিয়ে আনা।  
**Scope:** `INTAKE` only  
**This brief does not:** phase promote, novelty certify, methods approve, results verify, manuscript approve, venue select, or authorize submission.

## 1. Current canonical state

- `current_phase = INTAKE`
- `novelty_status = UNRESOLVED`
- `feasibility_decision = UNASSESSED`
- `solution_viability_status = ASSERTED_ONLY`
- `acceptance_readiness = NOT_ASSESSABLE`
- `REM-001 = OPEN`

Authoritative sources:

- `research-case/program-state.json`
- `research-case/09-submission/acceptance-readiness.md`
- `docs/20_INTAKE_EXTERNAL_VERIFIER_HANDOFF.md`
- `docs/23_INDEPENDENT_INTAKE_HUMAN_VERIFICATION_SOP_BN.md`

## 2. Objective

`REM-001` closed ধরা হবে only if:

1. একজন real independent human reviewer named and approved হন;
2. external trust root bootstrap complete হয়;
3. reviewer registry entry active হয়;
4. reviewer চারটি canonical INTAKE artifact review করেন;
5. reviewer চারটি independently signed `VERIFIED` event record করেন;
6. strict case check pass করে;
7. only then root integration owner `PROCEED` consider করতে পারেন।

উপরের যেকোনো একটা missing হলে `REM-001` open-ই থাকবে।

## 3. Required packet identity

- Intake review packet:
  `review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip`
- Current packet SHA-256:
  `b2b653a619ecfa3cc825b3a539b7e359aa1c8dec5485bfab6098b16d0d44008f`
- Return template:
  `review-packets/KEYSTONE-MPP-F1-intake-verifier-return-template.json`
- Current return-template SHA-256:
  `b1df9c2f18c269ae388a8f4c0c82650a72a930eebbae500faf44731faa5b7657`
- Transfer authorization template:
  `review-packets/KEYSTONE-MPP-F1-intake-transfer-authorization-template.json`
- Current transfer-authorization-template SHA-256:
  `d947916a98417b078e45534e3b1e59fe71c98d9f6e4c292c6c8e38007a554d82`
- Fill-ready draft:
  `review-packets/KEYSTONE-MPP-F1-intake-transfer-authorization-draft.json`
- Current fill-ready-draft SHA-256:
  `68f65c5231635b7c2d2bf86c744d1ee736c0dde2d2e45896847cb5b40904b3ba`

এই values stale হয়ে যাবে যদি packet বা canonical intake artifact revision/hash বদলায়।

## 4. Human roles and exact boundary

| Role | Must do | Must not do |
| --- | --- | --- |
| Accountable human | reviewer name, channel, confidentiality boundary approve | AI-generated review-কে independent review হিসেবে গ্রহণ |
| Workspace operator | packet/template/check commands চালানো, packet integrity confirm করা | packet send/upload করা without accountable-human approval |
| Registry administrator | external trust bootstrap, reviewer register | reviewer-এর private key collect/store করা |
| Independent reviewer | নিজের judgment-এ artifact review, own-key signing | author/root-integration-owner/Codex-এর language copy করে PASS দেওয়া |

## 5. Pre-handoff checklist

Workspace operator project root-এ:

```bash
cd /Users/rainbow/Documents/ZTech/Research/KEYSTONE_MPP_v1.0
make intake-verifier-packet-check
make intake-review-bundle-check
make intake-verifier-return-template-check
make intake-transfer-authorization-template-check
make intake-transfer-authorization-draft-check
LC_ALL=C LANG=C shasum -a 256 review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip
LC_ALL=C LANG=C shasum -a 256 review-packets/KEYSTONE-MPP-F1-intake-verifier-return-template.json
LC_ALL=C LANG=C shasum -a 256 review-packets/KEYSTONE-MPP-F1-intake-transfer-authorization-template.json
```

Expected outcome:

- packet check pass
- bundle check pass
- template check pass
- draft check pass
- packet SHA-256 matches Section 3
- template SHA-256 matches Section 3
- transfer-authorization-template SHA-256 matches Section 3

Mismatch হলে regenerate:

```bash
make intake-verifier-packet
make intake-review-bundle
make intake-verifier-return-template
make intake-transfer-authorization-template
make intake-transfer-authorization-draft
make intake-verifier-packet-check
make intake-review-bundle-check
make intake-verifier-return-template-check
make intake-transfer-authorization-template-check
make intake-transfer-authorization-draft-check
```

## 6. External authorization gate

Packet external reviewer-এর কাছে পাঠানোর আগে accountable human explicitভাবে approve করবেন:

1. reviewer identity
2. reviewer independence basis
3. transfer channel
4. confidentiality boundary
5. institutional-policy compatibility

Approval না থাকলে stop text:

```text
STOP — external transfer is not authorized in this run.
```

## 7. Reviewer workflow

Reviewer only these four artifacts review করবেন:

1. `research-case/00-governance/intake-original.md`
2. `research-case/00-governance/intake.json`
3. `research-case/00-governance/program-charter.md`
4. `research-case/00-governance/study-profile.json`

Reviewer verdict দেবেন না:

- novelty established
- feasibility GO
- methods approved
- results verified
- paper publication-ready
- submission-ready
- final author/corresponding-author/affiliation freeze

## 8. Mandatory stop rules

নিচের যেকোনো condition হলে reviewer বা operator থামবেন:

- reviewer is not a real identifiable human
- reviewer authored the intake artifacts
- reviewer is the root integration owner
- reviewer conflict not disclosed
- private key shared with author/Codex/workspace
- packet hash mismatch
- current artifact revision/hash changed after review
- any question remains material `FAIL` or `UNKNOWN`

## 9. Done condition for REM-001

`REM-001` closed only if all are true:

- reviewer registered as `INDEPENDENT_REVIEWER`
- four artifact-specific signed `VERIFIED` events exist
- completed verifier-return contract validates
- strict `check_research_case.py --strict` passes
- phase can be considered for `PROCEED`

If any of the above is absent, report:

```text
REM-001 remains OPEN.
```

## 10. Immediate next action

Next executable action is not a code change. It is:

1. confirm the current active reviewer entry or choose a replacement,
2. copy the fill-ready draft and complete reviewer, channel, and confidentiality boundary,
3. approve the transfer boundary,
4. deliver the packet,
5. wait for the authenticated human return.

Until that happens, the workspace may continue internal preparation, but `INTAKE` remains the blocking serial gate.
