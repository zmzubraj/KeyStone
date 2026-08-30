# KEYSTONE-MPP-F1 Intake External-Verifier Handoff

Status: `PREPARED_FOR_EXTERNAL_VERIFICATION`

This is an operational handoff, not canonical scientific evidence and not a
verification event. It does not change `research-case/program-state.json`, does
not promote `INTAKE`, and must not be cited as an independent review.

## Review objective

An independently accountable reviewer should determine whether the frozen
research question, program charter, study profile, authority/confidentiality
boundary, and claim ceilings form a coherent and defensible intake for a
non-human computational security study.

The reviewer is not being asked to approve novelty, feasibility, methods,
results, manuscript quality, venue fit, or submission.

## Bounded local review archive

The root integration owner can generate the deterministic, allowlisted local
archive with:

```bash
make intake-review-bundle
make intake-review-bundle-check
```

The archive is written to
`review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip` with a SHA-256
sidecar. Creating it does not authorize sending or uploading it, does not
create an independent scientific verification event, and does not promote the
research phase. Accountable-author contact metadata, private signing material,
results, manuscript files, and unrelated unpublished artifacts are excluded.

## Canonical artifacts to review

The four decision-bearing `INTAKE` artifacts are:

1. `research-case/00-governance/intake-original.md`
2. `research-case/00-governance/intake.json`
3. `research-case/00-governance/program-charter.md`
4. `research-case/00-governance/study-profile.json`

Supporting governance context:

- `research-case/00-governance/accountable-authority-confirmation.md`
- `research-case/00-governance/egress-policy.json`
- `research-case/00-governance/capability-preflight.json`
- `research-case/program-state.json`
- `research-case/artifact-registry.csv`

Final author list/order, corresponding-author designation, exact affiliation
wording, institutional naming, and final paper-metadata contacts are explicitly
deferred. They are not part of this scientific intake review and must not be
silently frozen by the reviewer.

<!-- BEGIN GENERATED INTAKE SNAPSHOT -->
## Current artifact snapshot

This generated snapshot is derived from canonical registry and governance inputs.
Snapshot source timestamp: `2026-08-30T05:18:24Z` (latest required artifact `updated_at`; no wall-clock value).

- Current status: `ACTIVE`
- Current phase: `INTAKE`
- Novelty status: `UNRESOLVED`
- Feasibility decision: `UNASSESSED`
- Solution viability: `ASSERTED_ONLY`
- Acceptance readiness: `NOT_ASSESSABLE`
- Verifier trust mode: `EXTERNAL_RUN_BOUND_REGISTRY_ADMIN`
- Active independent reviewers: `1`
- Independent verification events for these four artifacts: `0`

| Path | Required | Status | Revision | SHA-256 |
| --- | --- | --- | --- | --- |
| `research-case/00-governance/intake-original.md` | `true` | `DRAFT` | `2` | `6f21c82ed0fe6c2933e689ab22750ee838e88b75e564eb985da119faf22a5ddd` |
| `research-case/00-governance/intake.json` | `true` | `DRAFT` | `2` | `800fdb650470596dc67367ba6868bffbb60b80cf7fe2471734254dc60d1ef9eb` |
| `research-case/00-governance/program-charter.md` | `true` | `DRAFT` | `4` | `a14ed6564b8d8bf3c51dff8f931321b6f288a9c832a6326522bac96c454b3f44` |
| `research-case/00-governance/study-profile.json` | `true` | `DRAFT` | `3` | `74e76831f2fc44f8b4a659a94b326ed621b886c2fb70c42794a94e3f28b7a982` |

Any content or registry change invalidates this snapshot until the exporter is rerun.
This snapshot is operational metadata, not independent scientific verification.
<!-- END GENERATED INTAKE SNAPSHOT -->

`research-case/00-governance/accountable-authority-confirmation.md` confirms
accountable-human identity and policy-basis scope, but it does not substitute
for independent scientific verification.

## Minimum independent review questions

The reviewer should record direct, artifact-specific answers to all of these:

1. Does the normalized intake preserve the exact six-field original intake?
2. Is the core research question falsifiable and measurable within the stated
   analytic, simulation, prototype, contract, and deadline-benchmark scope?
3. Are the novelty and target-contribution statements still clearly labeled as
   hypotheses rather than established findings?
4. Does the charter prevent claims of a new cryptographic primitive,
   production security, unconditional future availability, external validity,
   or field impact without matching evidence?
5. Is the non-human computational study classification consistent with the
   authorized data and execution boundary?
6. Are privacy, dual-use, live-exploitation, production-secret, external-upload,
   participant, regulated-intervention, and institutional-policy limits explicit?
7. Does the study profile adequately resolve field, study type, article type,
   jurisdiction basis, ethics category, evidence standard, reporting route, and
   adapter while leaving venue-specific rules for later verification?
8. Are the frozen claim boundaries and evidence-maturity ceilings internally
   coherent, and are any required qualifications missing?
9. Is there any scientific or governance reason the case should remain at
   `INTAKE` even after the four artifacts are corrected?

Any `FAIL`, material `UNKNOWN`, or requested correction should leave the
affected artifact `DRAFT` and return the smallest required change to the root
integration owner.

## Required identity and signing boundary

Schema v4 requires an external trust root and an authenticated reviewer key.
The registry currently contains only the mechanical runtime identity; that
identity cannot satisfy this review.

The registry administrator and reviewer must create separate Ed25519 keys in a
secure directory outside the research case. Private keys must never be copied
into the workspace or committed. Set the task-specific values below to the
actual, accountable identities and an approved external key directory. The
`${NAME:?message}` guards make the template stop instead of silently using an
unset identity or path.

```bash
KEYSTONE_TRUST_DIR=/secure/outside-case/keystone-mpp-f1
KEYSTONE_REGISTRY_ADMIN_KEY_ID=registry-admin-keystone-mpp-f1
KEYSTONE_REVIEWER_REGISTRY_ID=intake-reviewer-001
KEYSTONE_REVIEWER_ID=intake-reviewer-001
KEYSTONE_REVIEWER_KEY_ID=intake-reviewer-key-001

umask 077
mkdir -p "${KEYSTONE_TRUST_DIR:?set an approved external trust directory}"
ssh-keygen -t ed25519 -f "$KEYSTONE_TRUST_DIR/registry-admin-key"
ssh-keygen -t ed25519 -f "$KEYSTONE_TRUST_DIR/reviewer-key"

python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/manage_verifier_identity.py bootstrap-trust \
  /Users/rainbow/Documents/ZTech/Research/KEYSTONE_MPP_v1.0/research-case \
  --registry-admin-key-id "${KEYSTONE_REGISTRY_ADMIN_KEY_ID:?set the accountable registry-admin key ID}" \
  --registry-admin-public-key "$KEYSTONE_TRUST_DIR/registry-admin-key.pub" \
  --registry-signing-key "$KEYSTONE_TRUST_DIR/registry-admin-key"

python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/manage_verifier_identity.py register \
  /Users/rainbow/Documents/ZTech/Research/KEYSTONE_MPP_v1.0/research-case \
  --registry-id "${KEYSTONE_REVIEWER_REGISTRY_ID:?set the reviewer registry ID}" \
  --verifier-identity "${KEYSTONE_REVIEWER_ID:?set the accountable reviewer identity}" \
  --verifier-type INDEPENDENT_REVIEWER \
  --signing-key-id "${KEYSTONE_REVIEWER_KEY_ID:?set the reviewer key ID}" \
  --authority-tier SCIENTIFIC_INDEPENDENT \
  --public-key "$KEYSTONE_TRUST_DIR/reviewer-key.pub" \
  --registry-signing-key "$KEYSTONE_TRUST_DIR/registry-admin-key"
```

Key possession proves signature control, not the real-world identity or
independence of the holder. The accountable registry administrator must retain
the out-of-band identity and independence basis.

## Artifact verification events

After semantic review, record one independently signed `VERIFIED` revision for
each of the four canonical artifacts. Use unique verification IDs and a precise
method/basis. Example for one artifact:

```bash
python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/record_artifact.py \
  /Users/rainbow/Documents/ZTech/Research/KEYSTONE_MPP_v1.0/research-case \
  --path 00-governance/study-profile.json \
  --status VERIFIED \
  --owner intake_integration \
  --verified-by "${KEYSTONE_REVIEWER_ID:?set the accountable reviewer identity}" \
  --verifier-identity "$KEYSTONE_REVIEWER_ID" \
  --verifier-type INDEPENDENT_REVIEWER \
  --verification-method "independent scientific and governance semantic review" \
  --independence-mode INDEPENDENT \
  --independence-basis "no production ownership; no prior authorship of the reviewed intake artifacts; accountable out-of-band identity binding retained" \
  --verification-id INTAKE-STUDY-PROFILE-001 \
  --signing-key "${KEYSTONE_TRUST_DIR:?set the approved external trust directory}/reviewer-key" \
  --notes "INTAKE-only review; no novelty, feasibility, results, manuscript, venue, or submission verdict."
```

Repeat for the other three paths. Do not reuse a mechanical identity and do not
mark an artifact `VERIFIED` if its content changed after review.

## Final local checks and gate decision

After all four signed events exist, the root integration owner should run:

```bash
python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/check_research_case.py \
  --strict /Users/rainbow/Documents/ZTech/Research/KEYSTONE_MPP_v1.0/research-case
```

Only if strict validation passes and every required current-phase artifact is
still hash-matched and independently verified may the root consider the single
phase transition:

```bash
python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/advance_research_case.py \
  /Users/rainbow/Documents/ZTech/Research/KEYSTONE_MPP_v1.0/research-case \
  --decision PROCEED \
  --owner root-integration-owner
```

`PROCEED` would open `NOVELTY_AUDIT`; it would not establish novelty,
feasibility, solution viability, publication readiness, or acceptance.

## Expected verifier return

Return a signed, artifact-specific disposition containing:

- reviewer identity and authenticated registry/key IDs;
- independence basis and conflicts disclosure;
- reviewed artifact paths, revisions, and SHA-256 values;
- answer to each minimum review question with direct locations;
- corrections required, if any;
- unique verification event IDs for artifacts accepted as `VERIFIED`;
- residual uncertainty and the explicit statement that the review is
  `INTAKE_ONLY`.

The workspace provides a deterministic companion template bound to the current
review-packet SHA-256:

```bash
make intake-verifier-return-template
make intake-verifier-return-template-check
```

The generated path is
`review-packets/KEYSTONE-MPP-F1-intake-verifier-return-template.json`. After a
reviewer completes and signs a copy outside the template path, its structure can
be checked without writing canonical state:

```bash
python3 scripts/intake_verifier_return_contract.py \
  --validate /absolute/path/to/completed-intake-verifier-return.json
```

This validation checks packet identity, artifact revisions and hashes, complete
question dispositions, unique verification-event references, review scope, and
non-promotion flags. It does **not** verify the signature, real-world identity,
independence, scientific correctness, provenance, registry acceptance, or phase
eligibility. Those checks remain in the authenticated schema-v4 verifier and
strict research-case workflow above.
