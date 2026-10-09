# Decision Log

Append decisions; never overwrite history. Record timestamp, owner, phase, decision, evidence hashes, alternatives, consequence, rollback condition, and human authority when required.

## 2026-08-30T10:33:05Z — INTAKE

- Owner: intake-reviewer-002
- Decision: PROCEED
- Evidence: 00-governance/intake-original.md [sha256:6f21c82ed0fe6c2933e689ab22750ee838e88b75e564eb985da119faf22a5ddd], 00-governance/intake.json [sha256:800fdb650470596dc67367ba6868bffbb60b80cf7fe2471734254dc60d1ef9eb], 00-governance/program-charter.md [sha256:a14ed6564b8d8bf3c51dff8f931321b6f288a9c832a6326522bac96c454b3f44], 00-governance/study-profile.json [sha256:74e76831f2fc44f8b4a659a94b326ed621b886c2fb70c42794a94e3f28b7a982]
- Consequence: Advanced to NOVELTY_AUDIT.

## 2026-08-30T10:38:38Z — INTAKE

- Owner: root-integration-owner
- Decision: INVALIDATED
- Evidence: NONE
- Consequence: Resume from INTAKE; affected evidence is stale. Reason: INTAKE detached signature was created under namespace keyname and principal isolated-human-verifier, not the frozen namespace keystone-mpp-f1-intake and registered principal intake-reviewer-key-002; post-advance signature verification therefore fails and the phase decision is not admissible.

## 2026-08-30T11:09:24Z — INTAKE

- Owner: root-integration-owner
- Decision: PROCEED
- Evidence: 00-governance/intake-original.md [sha256:6f21c82ed0fe6c2933e689ab22750ee838e88b75e564eb985da119faf22a5ddd], 00-governance/intake.json [sha256:800fdb650470596dc67367ba6868bffbb60b80cf7fe2471734254dc60d1ef9eb], 00-governance/program-charter.md [sha256:a14ed6564b8d8bf3c51dff8f931321b6f288a9c832a6326522bac96c454b3f44], 00-governance/study-profile.json [sha256:74e76831f2fc44f8b4a659a94b326ed621b886c2fb70c42794a94e3f28b7a982]
- Consequence: Advanced to NOVELTY_AUDIT.

## 2026-10-09T20:11:24Z — INTAKE

- Owner: root-integration-owner
- Decision: INVALIDATED
- Evidence: NONE
- Consequence: Resume from INTAKE; affected evidence is stale. Reason: INTAKE advance at 2026-08-30T11:09Z was recorded before the reviewer submission audit passed (audit status INCOMPLETE; docs/27 requires audit PASS before advancement) and the intake-reviewer-002 signing key resides on the author's workstation, so reviewer independence is not established. Accountable human approved restoring fail-closed INTAKE on 2026-10-10.
