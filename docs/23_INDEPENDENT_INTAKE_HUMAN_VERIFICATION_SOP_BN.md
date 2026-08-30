# KEYSTONE-MPP-F1 Independent INTAKE Human Verification SOP

**Document status:** `OPERATIONAL SOP / INTAKE ONLY`

**Canonical phase at preparation:** `INTAKE`

**Purpose:** একজন সত্যিকারের independent human reviewer কীভাবে review, return,
signature, এবং চারটি canonical verification event সম্পন্ন করবেন—তার exact
line-by-line procedure ও completion contract।

**বর্তমান live status:** `WAITING_EXTERNAL`। কোনো independent human reviewer
এখনও registered নন, canonical verification event count `0`, এবং phase
`INTAKE`। এই SOP বা template-এর লেখা AI দিয়ে `PASS`, `VERIFIED`, reviewer
identity, competence, conflict disclosure, attestation, signature, অথবা
independence basis হিসেবে পূরণ করানো নিষিদ্ধ। Reviewer-এর নিজের judgment এবং
নিজের key-controlled signature ছাড়া task complete হবে না।

এই SOP novelty, feasibility, methods, results, manuscript, venue, submission,
authorship, corresponding-author status, বা affiliation wording approve করে না।
Final author order, corresponding-author designation, এবং exact affiliation
wording ইচ্ছাকৃতভাবে deferred থাকবে।

## 1. কোন অবস্থায় reviewer eligible

Reviewer শুরু করার আগে নিচের প্রতিটি statement সত্য হতে হবে:

1. Reviewer একজন identifiable human; AI agent, anonymous account, বা shared
   identity নয়।
2. Reviewer এই চারটি INTAKE artifact-এর author বা producer নন।
3. Reviewer KEYSTONE-MPP-F1-এর root integration owner নন।
4. Reviewer-এর এমন financial, supervisory, institutional, personal, বা
   publication conflict নেই যা independent judgment materially বদলাতে পারে;
   কোনো conflict থাকলে তা পুরোপুরি disclose করতে হবে।
5. Reviewer computational security research intake, distributed systems,
   applied cryptography, research methods, অথবা research governance-এর অন্তত
   একটি relevant competence basis লিখে দিতে পারবেন।
6. Reviewer নিজের Ed25519 private key নিজের নিয়ন্ত্রণে রাখবেন; private key
   author, Codex, email, cloud drive, repository, বা chat-এ দেবেন না।
7. Reviewer corrections চাইলে review `REVISE` হবে; courtesy বা project
   momentum-এর জন্য `PASS`/`VERIFIED` দেওয়া যাবে না।

উপরের কোনো condition false হলে reviewer থামবেন এবং লিখবেন:

```text
STOP — reviewer independence or competence requirement is not satisfied.
```

## 2. Reviewer কী review করবেন, কী করবেন না

Reviewer শুধু নিচের চারটি decision-bearing artifact review করবেন:

1. `research-case/00-governance/intake-original.md`
2. `research-case/00-governance/intake.json`
3. `research-case/00-governance/program-charter.md`
4. `research-case/00-governance/study-profile.json`

Review packet:

```text
review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip
```

Completed-return starting template:

```text
review-packets/KEYSTONE-MPP-F1-intake-verifier-return-template.json
```

Reviewer নিচের কোনো verdict দেবেন না:

- novelty established;
- feasibility `GO`;
- confirmatory execution authorized;
- methods approved;
- results verified;
- paper publication-ready বা submission-ready;
- author order/corresponding author/affiliation frozen;
- venue acceptance likely বা guaranteed।

## 3. বর্তমান review snapshot

এই SOP তৈরির সময় packet SHA-256:

```text
b0126dadcd4606a235187d16735572b531eb210f099fa2c783b29e0bf43fa27f
```

চারটি reviewed revision ও SHA-256:

| Artifact | Revision | SHA-256 |
| --- | ---: | --- |
| `research-case/00-governance/intake-original.md` | `2` | `6f21c82ed0fe6c2933e689ab22750ee838e88b75e564eb985da119faf22a5ddd` |
| `research-case/00-governance/intake.json` | `2` | `800fdb650470596dc67367ba6868bffbb60b80cf7fe2471734254dc60d1ef9eb` |
| `research-case/00-governance/program-charter.md` | `4` | `a14ed6564b8d8bf3c51dff8f931321b6f288a9c832a6326522bac96c454b3f44` |
| `research-case/00-governance/study-profile.json` | `3` | `74e76831f2fc44f8b4a659a94b326ed621b886c2fb70c42794a94e3f28b7a982` |

Packet বা চারটি artifact-এর যেকোনো hash/revision বদলালে এই review snapshot
stale। তখন পুরনো return ব্যবহার না করে packet/template regenerate করে নতুন
review করতে হবে।

## 4. Workspace operator-এর pre-handoff commands

Workspace operator project root-এ গিয়ে serially চালাবেন:

```bash
cd /Users/rainbow/Documents/ZTech/Research/KEYSTONE_MPP_v1.0
make intake-verifier-packet-check
make intake-review-bundle-check
make intake-verifier-return-template-check
sha256sum review-packets/KEYSTONE-MPP-F1-intake-review-packet.zip
```

Expected packet hash অবশ্যই Section 3-এর hash-এর সঙ্গে match করবে। Match না
করলে operator চালাবেন:

```bash
make intake-verifier-packet
make intake-review-bundle
make intake-verifier-return-template
make intake-verifier-packet-check
make intake-review-bundle-check
make intake-verifier-return-template-check
```

Regeneration-এর পরে এই SOP-এর snapshot values আর automatically current বলে
ধরা যাবে না; reviewer current template এবং `bundle-manifest.json`-এর values
ব্যবহার করবেন।

Packet external human-এর কাছে পাঠানো একটি external transfer। Accountable human
নিজে recipient, channel, confidentiality, এবং institutional-policy boundary
approve করবেন। Codex নিজে packet upload/send করবে না।

## 5. Reviewer key তৈরি করবেন

Reviewer একটি supervised local shell বা approved secure session-এ এই values
নিজের values দিয়ে set করবেন:

```bash
KEYSTONE_TRUST_DIR=/Users/rainbow/.keystone-trust/KEYSTONE-MPP-F1
KEYSTONE_REVIEWER_ID=intake-reviewer-001
KEYSTONE_REVIEWER_REGISTRY_ID=intake-reviewer-001
KEYSTONE_REVIEWER_KEY_ID=intake-reviewer-key-001
```

তারপর reviewer চালাবেন:

```bash
umask 077
mkdir -p "$KEYSTONE_TRUST_DIR"
chmod 700 "$KEYSTONE_TRUST_DIR"
ssh-keygen -t ed25519 -a 64 -f "$KEYSTONE_TRUST_DIR/reviewer-key" -C "$KEYSTONE_REVIEWER_ID"
chmod 600 "$KEYSTONE_TRUST_DIR/reviewer-key"
chmod 644 "$KEYSTONE_TRUST_DIR/reviewer-key.pub"
```

Passphrase prompt এলে reviewer একটি private passphrase ব্যবহার করবেন। Reviewer
শুধু এই public key file registry administrator-কে দেবেন:

```text
/Users/rainbow/.keystone-trust/KEYSTONE-MPP-F1/reviewer-key.pub
```

## 6. Registry administrator external trust bootstrap করবেন

Registry administrator-এর key reviewer key থেকে আলাদা হতে হবে। Administrator
চালাবেন:

```bash
KEYSTONE_CASE=/Users/rainbow/Documents/ZTech/Research/KEYSTONE_MPP_v1.0/research-case
KEYSTONE_TRUST_DIR=/Users/rainbow/.keystone-trust/KEYSTONE-MPP-F1
KEYSTONE_REGISTRY_ADMIN_KEY_ID=registry-admin-keystone-mpp-f1
KEYSTONE_REVIEWER_ID=intake-reviewer-001
KEYSTONE_REVIEWER_REGISTRY_ID=intake-reviewer-001
KEYSTONE_REVIEWER_KEY_ID=intake-reviewer-key-001

umask 077
mkdir -p "$KEYSTONE_TRUST_DIR"
ssh-keygen -t ed25519 -a 64 -f "$KEYSTONE_TRUST_DIR/registry-admin-key" -C "$KEYSTONE_REGISTRY_ADMIN_KEY_ID"
```

তারপর trust root bootstrap:

```bash
python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/manage_verifier_identity.py bootstrap-trust \
  "$KEYSTONE_CASE" \
  --registry-admin-key-id "$KEYSTONE_REGISTRY_ADMIN_KEY_ID" \
  --registry-admin-public-key "$KEYSTONE_TRUST_DIR/registry-admin-key.pub" \
  --registry-signing-key "$KEYSTONE_TRUST_DIR/registry-admin-key"
```

তারপর reviewer register:

```bash
python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/manage_verifier_identity.py register \
  "$KEYSTONE_CASE" \
  --registry-id "$KEYSTONE_REVIEWER_REGISTRY_ID" \
  --verifier-identity "$KEYSTONE_REVIEWER_ID" \
  --verifier-type INDEPENDENT_REVIEWER \
  --signing-key-id "$KEYSTONE_REVIEWER_KEY_ID" \
  --authority-tier SCIENTIFIC_INDEPENDENT \
  --public-key "$KEYSTONE_TRUST_DIR/reviewer-key.pub" \
  --registry-signing-key "$KEYSTONE_TRUST_DIR/registry-admin-key"
```

Registry check:

```bash
python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/manage_verifier_identity.py list \
  "$KEYSTONE_CASE"
```

Completion requirement: registry-তে reviewer entry `active=true`, verifier type
`INDEPENDENT_REVIEWER`, reviewer ID/key ID exact match, এবং external trust-root
fingerprint nonblank হতে হবে। Key possession alone real-world identity বা
independence প্রমাণ করে না; administrator একটি private out-of-band identity and
independence note সংরক্ষণ করবেন।

## 7. Reviewer packet integrity যাচাই করবেন

Reviewer packet যে directory-তে পেয়েছেন সেখানে চালাবেন:

```bash
sha256sum KEYSTONE-MPP-F1-intake-review-packet.zip
unzip -t KEYSTONE-MPP-F1-intake-review-packet.zip
```

Hash Section 3 বা current return template-এর `review_packet_sha256`-এর সঙ্গে
match করতে হবে। তারপর fresh directory-তে extract:

```bash
KEYSTONE_REVIEW_DIR=/tmp/keystone-mpp-f1-intake-review
mkdir -p "$KEYSTONE_REVIEW_DIR"
unzip KEYSTONE-MPP-F1-intake-review-packet.zip -d "$KEYSTONE_REVIEW_DIR"
cd "$KEYSTONE_REVIEW_DIR"
```

Reviewer কোনো code, build, test, script, binary, বা network call execute করবেন
না। Packet-এর `README.md`, `bundle-manifest.json`, এবং চারটি canonical artifact
read-only review করবেন।

Reviewer manifest hashes check করবেন:

```bash
sha256sum research-case/00-governance/intake-original.md
sha256sum research-case/00-governance/intake.json
sha256sum research-case/00-governance/program-charter.md
sha256sum research-case/00-governance/study-profile.json
```

## 8. Nine-question review: exact decision rules

প্রতিটি question-এর জন্য reviewer লিখবেন:

- `disposition`: `PASS`, `PARTIAL`, `FAIL`, বা `UNKNOWN`;
- `evidence_locations`: অন্তত একটি exact file + heading/JSON pointer;
- `rationale`: নিজের ভাষায় concrete reasoning।

`PROCEED_RECOMMENDED`-এর জন্য এই SOP আরও strict: সব নয়টি question `PASS` হতে
হবে। `PARTIAL`, `FAIL`, বা material `UNKNOWN` থাকলে overall disposition হবে
`REVISE` অথবা `STOP`; task complete ধরা হবে না।

### INTAKE-Q01

Question: normalized intake কি original six fields exact preserve করেছে?

Reviewer line-by-line compare করবেন:

- `intake-original.md`-এর six lines;
- `intake.json#/fields/system_name`;
- `intake.json#/fields/research_topic_name`;
- `intake.json#/fields/core_research_question`;
- `intake.json#/fields/novelty_statement`;
- `intake.json#/fields/target_contribution`;
- `intake.json#/fields/possible_feasibility`;
- `intake.json#/raw_sha256` বনাম original file SHA-256।

Exact match হলে `PASS`; semantic rewrite, omission, বা hash mismatch হলে `FAIL`।

### INTAKE-Q02

Question: core research question computational scope-এর মধ্যে falsifiable এবং
measurable কি না?

Evidence locations:

- `intake-original.md` core research question;
- `program-charter.md#User-asserted starting contract`;
- `program-charter.md#Frozen operational claim register`;
- `study-profile.json#/study_type`;
- `study-profile.json#/evidence_standard`।

Reviewerকে বলতে হবে কোন observable outcome claimকে fail করতে পারে। Vague বা
unmeasurable হলে `FAIL`/`PARTIAL`।

### INTAKE-Q03

Question: novelty এবং contribution established result নয়, hypothesis হিসেবে
labeled কি না?

Evidence locations:

- `intake.json#/assertion_policy`;
- `program-charter.md#User-asserted starting contract`;
- `program-charter.md#Claim ladder`।

`UNRESOLVED`, `E1 ASSERTED`, এবং `ASSERTED ONLY` boundary explicit হলে `PASS`।

### INTAKE-Q04

Question: charter evidence maturity/scope-এর চেয়ে stronger claim আটকায় কি না?

Evidence locations:

- `program-charter.md#Claim ladder`;
- `program-charter.md#Authority, safety, and execution bounds`;
- `program-charter.md#Frozen operational claim register`;
- বিশেষ করে K-C1 থেকে K-C6-এর maximum wording।

New primitive, production security, unconditional availability, external
validity, field impact, বা unconditional blame implied হলে `FAIL`।

### INTAKE-Q05

Question: non-human computational classification authorized boundary-এর সঙ্গে
consistent কি না?

Evidence locations:

- `program-charter.md#Authority, safety, and execution bounds`;
- `program-charter.md#Resolved working study profile`;
- `study-profile.json#/jurisdiction_basis`;
- `study-profile.json#/ethics_category`।

Personal data, participants, live exploitation, বা regulated intervention
required হলে `FAIL`।

### INTAKE-Q06

Question: privacy, dual-use, exploitation, secrets, upload, participant,
intervention, এবং policy limits explicit কি না?

Evidence locations:

- `program-charter.md#Identity` confidentiality/external-processing lines;
- `program-charter.md#Authority, safety, and execution bounds`;
- `study-profile.json#/jurisdiction_basis`;
- `study-profile.json#/ethics_category`।

যে limit absent বা ambiguous, reviewer exact correction লিখবেন এবং `PARTIAL`
বা `FAIL` দেবেন।

### INTAKE-Q07

Question: study profile required routing fields resolve করেছে কিন্তু later
venue rules freeze করেনি কি না?

Reviewer check করবেন:

- `study-profile.json#/adapter_id`;
- `#/field`;
- `#/study_type`;
- `#/jurisdiction`;
- `#/jurisdiction_basis`;
- `#/ethics_category`;
- `#/reporting_guidelines`;
- `#/evidence_standard`;
- `#/article_type`;
- `#/status`;
- `#/notes`।

Venue-neutral এবং later venue/institutional checks pending থাকলে `PASS`।

### INTAKE-Q08

Question: frozen claim boundaries এবং maturity ceilings internally coherent কি
না?

Evidence locations:

- `program-charter.md#Claim ladder` C001-C003;
- `program-charter.md#Frozen operational claim register` K-C1-K-C6;
- `study-profile.json#/evidence_standard`।

Claim, required evidence, current stage, falsifier, এবং maximum wording-এর মধ্যে
contradiction থাকলে `FAIL`/`PARTIAL`।

### INTAKE-Q09

Question: corrections-এর পরে case-কে `INTAKE`-এ রাখার কোনো remaining
INTAKE-only reason আছে কি না?

Evidence locations:

- চারটি reviewed artifact-এর final assessment;
- `research-case/program-state.json#/current_phase`;
- `program-charter.md#Authority, safety, and execution bounds`।

No remaining INTAKE-only blocker থাকলে disposition `PASS`, rationale-এ লিখবেন:

```text
No remaining INTAKE-only blocker was identified. Novelty, feasibility,
methods, execution, results, manuscript, venue, and submission gates remain
separately open and were not approved by this review.
```

## 9. Completed return JSON কীভাবে পূরণ করবেন

Reviewer template copy করবেন; original template overwrite করবেন না:

```bash
cp review-packets/KEYSTONE-MPP-F1-intake-verifier-return-template.json \
  /absolute/reviewer/path/KEYSTONE-MPP-F1-intake-verifier-return-completed.json
```

Completed file-এ exact control values:

```text
status = COMPLETED_FOR_STRUCTURAL_VALIDATION
review_scope = INTAKE_ONLY
canonical_phase = INTAKE
may_promote_phase = false
may_assert_novelty = false
may_authorize_execution = false
author_metadata_included = false
overall_disposition = PROCEED_RECOMMENDED
```

Reviewer object-এর সব field nonblank:

```text
identity = accountable human reviewer identity
registry_id = intake-reviewer-001
signing_key_id = intake-reviewer-key-001
independence_basis = specific independence statement
conflicts_disclosure = None known অথবা full disclosure
competence_basis = specific relevant training/experience
```

সব নয়টি question `PASS`, nonempty evidence locations, এবং nonempty rationale
পাবে। চারটি artifact disposition হবে `VERIFIED`; path/revision/hash template
থেকে অপরিবর্তিত থাকবে। Exact unique event IDs:

```text
INTAKE-ORIGINAL-001
INTAKE-NORMALIZED-001
INTAKE-CHARTER-001
INTAKE-STUDY-PROFILE-001
```

প্রতিটি artifact row:

```text
disposition = VERIFIED
corrections_required = []
residual_uncertainty = INTAKE-only verification; later scientific and submission gates were not assessed.
```

যদি correction লাগে, reviewer `VERIFIED` দেবেন না। `corrections_required`-এ
smallest exact correction লিখবেন, overall `REVISE` করবেন, এবং canonical
verification commands চালাবেন না।

Reviewer attestation exact minimum text:

```text
I am the accountable human identified in reviewer.identity. I reviewed the
packet and four artifact revisions and hashes recorded in this return. My
answers are my independent judgment. I disclosed my competence basis and all
known conflicts. This is an INTAKE-only review. I do not assert novelty,
feasibility, execution authorization, results validity, manuscript readiness,
venue fit, authorship metadata, submission readiness, or editorial acceptance.
```

## 10. Reviewer attestation sign করবেন

Reviewer একটি companion attestation file তৈরি করবেন যাতে অন্তত থাকবে:

- reviewer identity, registry ID, key ID;
- packet SHA-256;
- চার artifact path, revision, hash, `VERIFIED`, event ID;
- `INTAKE-Q01` থেকে `INTAKE-Q09` = `PASS`;
- overall `PROCEED_RECOMMENDED`;
- চারটি `may_*`/author-metadata flag false;
- Section 9-এর reviewer attestation text।

File sign করবেন:

```bash
KEYSTONE_TRUST_DIR=/Users/rainbow/.keystone-trust/KEYSTONE-MPP-F1
ssh-keygen -Y sign \
  -f "$KEYSTONE_TRUST_DIR/reviewer-key" \
  -n keystone-mpp-f1-intake \
  /absolute/reviewer/path/KEYSTONE-MPP-F1-intake-reviewer-attestation.txt
```

এতে `.sig` file তৈরি হবে। Signature hash নেবেন:

```bash
sha256sum /absolute/reviewer/path/KEYSTONE-MPP-F1-intake-reviewer-attestation.txt.sig
```

Completed return JSON-এর `signed_return` fields:

```text
signature_path = absolute or handed-off path to the .sig file
signature_sha256 = lowercase 64-character SHA-256 printed above
```

## 11. Structural validation canonical events-এর আগে হবে

Workspace operator চালাবেন:

```bash
cd /Users/rainbow/Documents/ZTech/Research/KEYSTONE_MPP_v1.0
python3 scripts/intake_verifier_return_contract.py \
  --validate /absolute/reviewer/path/KEYSTONE-MPP-F1-intake-verifier-return-completed.json
```

Expected output:

```text
VALID STRUCTURE ONLY: return matches the current INTAKE packet contract; this does not verify signature, identity, independence, scientific correctness, provenance, or phase eligibility.
```

তারপর reviewer public key দিয়ে companion signature verify:

```bash
KEYSTONE_TRUST_DIR=/Users/rainbow/.keystone-trust/KEYSTONE-MPP-F1
KEYSTONE_REVIEWER_ID=intake-reviewer-001
printf '%s %s\n' "$KEYSTONE_REVIEWER_ID" "$(cat "$KEYSTONE_TRUST_DIR/reviewer-key.pub")" \
  > "$KEYSTONE_TRUST_DIR/reviewer-allowed-signers.txt"
ssh-keygen -Y verify \
  -f "$KEYSTONE_TRUST_DIR/reviewer-allowed-signers.txt" \
  -I "$KEYSTONE_REVIEWER_ID" \
  -n keystone-mpp-f1-intake \
  -s /absolute/reviewer/path/KEYSTONE-MPP-F1-intake-reviewer-attestation.txt.sig \
  < /absolute/reviewer/path/KEYSTONE-MPP-F1-intake-reviewer-attestation.txt
```

Expected signature result `Good ... signature`। Structural validation বা
signature verification fail হলে task incomplete।

## 12. Reviewer চারটি signed canonical event record করবেন

এই commands reviewer নিজে তার private key access-সহ চালাবেন। Private key root
owner বা Codex-কে দেবেন না।

```bash
KEYSTONE_CASE=/Users/rainbow/Documents/ZTech/Research/KEYSTONE_MPP_v1.0/research-case
KEYSTONE_TRUST_DIR=/Users/rainbow/.keystone-trust/KEYSTONE-MPP-F1
KEYSTONE_REVIEWER_ID=intake-reviewer-001
KEYSTONE_INDEPENDENCE_BASIS="no production ownership; no prior authorship of the reviewed intake artifacts; accountable out-of-band identity binding retained"
```

Artifact 1:

```bash
python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/record_artifact.py \
  "$KEYSTONE_CASE" \
  --path 00-governance/intake-original.md \
  --status VERIFIED \
  --owner intake_integration \
  --evidence-ids INPUT-001 \
  --verified-by "$KEYSTONE_REVIEWER_ID" \
  --verifier-identity "$KEYSTONE_REVIEWER_ID" \
  --verifier-type INDEPENDENT_REVIEWER \
  --verification-method "independent scientific and governance semantic review" \
  --independence-mode INDEPENDENT \
  --independence-basis "$KEYSTONE_INDEPENDENCE_BASIS" \
  --verification-id INTAKE-ORIGINAL-001 \
  --signing-key "$KEYSTONE_TRUST_DIR/reviewer-key" \
  --notes "INTAKE-only review; no novelty, feasibility, execution, results, manuscript, venue, authorship-metadata, submission, or acceptance verdict."
```

Artifact 2:

```bash
python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/record_artifact.py \
  "$KEYSTONE_CASE" \
  --path 00-governance/intake.json \
  --status VERIFIED \
  --owner intake_integration \
  --evidence-ids INPUT-001 \
  --verified-by "$KEYSTONE_REVIEWER_ID" \
  --verifier-identity "$KEYSTONE_REVIEWER_ID" \
  --verifier-type INDEPENDENT_REVIEWER \
  --verification-method "independent scientific and governance semantic review" \
  --independence-mode INDEPENDENT \
  --independence-basis "$KEYSTONE_INDEPENDENCE_BASIS" \
  --verification-id INTAKE-NORMALIZED-001 \
  --signing-key "$KEYSTONE_TRUST_DIR/reviewer-key" \
  --notes "INTAKE-only normalized-input review; no downstream gate verdict."
```

Artifact 3:

```bash
python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/record_artifact.py \
  "$KEYSTONE_CASE" \
  --path 00-governance/program-charter.md \
  --status VERIFIED \
  --owner intake_integration \
  --evidence-ids INPUT-001 \
  --verified-by "$KEYSTONE_REVIEWER_ID" \
  --verifier-identity "$KEYSTONE_REVIEWER_ID" \
  --verifier-type INDEPENDENT_REVIEWER \
  --verification-method "independent scientific and governance semantic review" \
  --independence-mode INDEPENDENT \
  --independence-basis "$KEYSTONE_INDEPENDENCE_BASIS" \
  --verification-id INTAKE-CHARTER-001 \
  --signing-key "$KEYSTONE_TRUST_DIR/reviewer-key" \
  --notes "INTAKE-only charter review; final author order, corresponding-author designation, and exact affiliation wording remain deferred."
```

Artifact 4:

```bash
python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/record_artifact.py \
  "$KEYSTONE_CASE" \
  --path 00-governance/study-profile.json \
  --status VERIFIED \
  --owner intake_integration \
  --evidence-ids INPUT-001 \
  --verified-by "$KEYSTONE_REVIEWER_ID" \
  --verifier-identity "$KEYSTONE_REVIEWER_ID" \
  --verifier-type INDEPENDENT_REVIEWER \
  --verification-method "independent scientific and governance semantic review" \
  --independence-mode INDEPENDENT \
  --independence-basis "$KEYSTONE_INDEPENDENCE_BASIS" \
  --verification-id INTAKE-STUDY-PROFILE-001 \
  --signing-key "$KEYSTONE_TRUST_DIR/reviewer-key" \
  --notes "INTAKE-only study-profile review; venue and institutional rules remain later gates."
```

কোনো artifact review-এর পরে content/hash বদলে গেলে reviewer ওই artifact-কে
`VERIFIED` record করবেন না। Corrected revision-এর উপর fresh review করতে হবে।

## 13. Root integration owner-এর final checks এবং phase close

চার command successful হওয়ার পরে root integration owner চালাবেন:

```bash
cd /Users/rainbow/Documents/ZTech/Research/KEYSTONE_MPP_v1.0
python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/check_research_case.py \
  research-case --strict
```

তারপর registry-তে চার path `VERIFIED`, current hash-matched, independently
signed, unique event ID-যুক্ত কি না inspect করবেন। Strict pass এবং চারটি
verification event current হলে phase transition:

```bash
python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/advance_research_case.py \
  research-case \
  --decision PROCEED \
  --owner root-integration-owner
```

তারপর আবার:

```bash
python3 /Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/check_research_case.py \
  research-case --strict
```

`PROCEED` শুধু `NOVELTY_AUDIT` খুলবে। এটি novelty pass, feasibility `GO`,
execution authorization, paper readiness, বা acceptance নয়।

## 14. Codex কোন exact অবস্থায় task complete ধরবে

Codex `Independent INTAKE verifier return সংগ্রহ` task-কে **COMPLETE** বলবে
শুধু যখন নিচের সব condition একসঙ্গে সত্য:

- [ ] Reviewer eligibility এবং competence basis documented।
- [ ] Reviewer conflict disclosure nonblank এবং acceptable।
- [ ] Reviewer public key signed external trust registry-তে active।
- [ ] Reviewed packet hash current return contract-এর সঙ্গে exact match।
- [ ] Q01-Q09 সব `PASS`, direct evidence locations ও substantive rationale সহ।
- [ ] চার artifact disposition `VERIFIED` এবং reviewed revision/hash exact।
- [ ] Four unique event IDs exact এবং reused নয়।
- [ ] Overall disposition `PROCEED_RECOMMENDED`।
- [ ] Scope flags: phase promotion, novelty assertion, execution authorization,
      author metadata inclusion—সব `false`।
- [ ] Reviewer attestation nonblank এবং companion signature cryptographically
      verifies with the registered reviewer public key।
- [ ] Completed return structural validator exits `0`।
- [ ] Four canonical `record_artifact.py` commands exit `0` এবং independently
      signed verification events ledger-এ আছে।
- [ ] Pre-transition strict schema-v4 checker exits `0`।
- [ ] `advance_research_case.py --decision PROCEED` exits `0`।
- [ ] Post-transition strict schema-v4 checker exits `0`।
- [ ] Canonical phase is `NOVELTY_AUDIT`; novelty remains `UNRESOLVED`,
      feasibility remains `UNASSESSED`, solution viability remains
      `ASSERTED_ONLY`, acceptance readiness remains `NOT_ASSESSABLE`।
- [ ] Final author order, corresponding author, এবং exact affiliation wording
      এখনও deferred।

একটিও checkbox অসম্পূর্ণ হলে task status হবে `WAITING_EXTERNAL`, `REVISE`, বা
`BLOCKED`—`COMPLETE` নয়।

## 15. Reviewer কী return করবেন

Reviewer root integration owner-কে এই পাঁচটি item দেবেন:

1. completed verifier-return JSON;
2. reviewer attestation text;
3. detached `.sig` file;
4. reviewer public key;
5. out-of-band reviewer identity, competence, independence, and conflict note।

Reviewer private key দেবেন না। Reviewer যদি চারটি canonical event supervised
workspace session-এ নিজে record করে থাকেন, সেই command outputs বা event IDs-ও
handoff note-এ দেবেন।

## 16. Fail-closed stop rules

নিচের যেকোনো ঘটনা ঘটলে phase advance নিষিদ্ধ:

- packet/artifact hash mismatch;
- reviewer identity বা independence unverified;
- reviewer private key shared বা exposed;
- any Q01-Q09 `PARTIAL`, `FAIL`, বা material `UNKNOWN`;
- any artifact not `VERIFIED`;
- duplicate/blank verification event ID;
- signature failure;
- structural validator failure;
- strict checker failure;
- reviewed content changed after review;
- reviewer novelty, feasibility, execution, manuscript, submission, author
  metadata, বা acceptance verdict দেওয়ার চেষ্টা করেছেন;
- registry only mechanical identity দেখায়;
- accountable human or institutional policy raises a contradiction।

এই stop rule-গুলোর উদ্দেশ্য delay তৈরি করা নয়; একটি human review-কে সত্যিকারের
independent, hash-bound, scope-limited, এবং reproducible decision event করা।
