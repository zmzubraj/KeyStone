# KEYSTONE-MPP-F1: INTAKE signature remediation

Status: `WAITING_EXTERNAL / FAIL-CLOSED`  
Canonical phase: `INTAKE`  
Current review packet SHA-256:
`d6899a8c87eb6535fa10705ee9b484a2943ae249f3f8ec5933882b15febba737`

এই নথি novelty, feasibility, execution, results, manuscript, submission, বা
acceptance gate approve করে না।

## Current audit result

আগের completed return ও signature historical evidence হিসেবে সংরক্ষিত, কিন্তু নতুন packet-এর
সঙ্গে packet binding এখন আর valid নয়। Reviewer registry binding, attestation content, এবং
signature-file hash internally consistent হলেও signatureটি frozen INTAKE signature contract-এ
valid নয়। Reviewer-কে নতুন current template থেকে return তৈরি করতে হবে।

বর্তমান signature:

- SHA-256: `8d15b1f7faa6e0fde2a19577450190ac4c173a66534e63a00fc788fb81c0ddbc`
- reported namespace: `keyname`
- reported principal: `isolated-human-verifier`

Required values:

- namespace: `keystone-mpp-f1-intake`
- registered signing principal/key ID: `intake-reviewer-key-002`
- reviewer registry ID: `intake-reviewer-002`

Required namespace দিয়ে verification চালালে authoritative result:

```text
Couldn't verify signature: namespace does not match
```

এই কারণে আগের `INTAKE -> NOVELTY_AUDIT` decision history-তে সংরক্ষিত থাকলেও admissible
নয়। Case `INTAKE`-এ invalidate করা হয়েছে এবং affected artifacts `STALE`; কিছু delete করা হয়নি।

## Human reviewer-এর exact repair

Reviewer নিজের external private key access-সহ নিচের কাজ করবেন। Codex বা অন্য agent private
key ব্যবহার, copy, বা re-sign করবে না।

1. Current packet hash independently verify করুন এবং
   `review-packets/KEYSTONE-MPP-F1-intake-verifier-return-template.json` থেকে নতুন completed
   return তৈরি করুন। পুরোনো completed JSON edit-in-place করে current return হিসেবে ব্যবহার
   করবেন না।
2. নতুন companion attestation তৈরি করুন। এতে current packet hash `d6899a8...`, current reviewed
   revisions `5`, `5`, `7`, `6`, চার artifact hash, Q01-Q09 dispositions, scope flags, এবং নতুন
   completed return-এর `reviewer_attestation` text থাকতে হবে। পুরোনো `142d908...` attestation
   re-sign করবেন না।
3. ভুল `.sig` file-টি reviewer-side backup করুন।
4. existing target signature overwrite করার আগে reviewer-side working directory-তে signing
   command চালান:

```bash
KEYSTONE_TRUST_DIR=/Users/rainbow/.keystone-trust/KEYSTONE-MPP-F1
ATTESTATION=/Users/rainbow/Documents/ZTech/Research/KEYSTONE_MPP_v1.0/review-packets/reviewer-submissions/KEYSTONE-MPP-F1-intake-reviewer-attestation.txt

ssh-keygen -Y sign \
  -f "$KEYSTONE_TRUST_DIR/reviewer-key" \
  -n keystone-mpp-f1-intake \
  "$ATTESTATION"
```

5. Signature-এর SHA-256 নিন:

```bash
sha256sum "$ATTESTATION.sig"
```

6. Completed JSON-এর `signed_return.signature_sha256`-এ exact নতুন 64-character hash লিখুন।
7. Registered allowed-signers file দিয়ে reviewer নিজে verify করুন:

```bash
ssh-keygen -Y verify \
  -f /Users/rainbow/Documents/ZTech/Research/KEYSTONE_MPP_v1.0/research-case/00-governance/verifier-allowed-signers.txt \
  -I intake-reviewer-key-002 \
  -n keystone-mpp-f1-intake \
  -s "$ATTESTATION.sig" \
  < "$ATTESTATION"
```

Expected output-এর namespace এবং principal দুটোই exact হতে হবে:

```text
Good "keystone-mpp-f1-intake" signature for intake-reviewer-key-002 with ED25519 key ...
```

`Good "keyname" ...` গ্রহণযোগ্য নয়, কারণ quoted value-টি namespace।

8. Out-of-band channel-এ নতুন signature SHA-256 এবং public-key fingerprint দিন। Expected
   public-key fingerprint:
   `SHA256:nm/WZGb+AeRbB5spdeQ12EaRq05mBoAb3/C8H/Qw/pA`।

## Signature repair-এর পরে canonical recovery

Workspace integration owner প্রথমে audit চালাবেন:

```bash
cd /Users/rainbow/Documents/ZTech/Research/KEYSTONE_MPP_v1.0
python3 scripts/intake_reviewer_submission_audit.py
python3 scripts/intake_reviewer_submission_audit.py --check --require-complete
```

Signature PASS হওয়ার আগে কোনো `record_artifact.py` বা phase-advance command পুনরায় চালানো
যাবে না। Signature PASS হলে reviewer চারটি artifact-এর নতুন signed verification event record
করবেন। তারপর integration owner:

1. চারটি event signature, artifact hash, revision, registry ID, এবং key ID যাচাই করবেন;
2. open INTAKE invalidation close করবেন;
3. strict checker চালাবেন;
4. কেবল তারপর `advance_research_case.py` দিয়ে এক ধাপ `NOVELTY_AUDIT`-এ যাবেন।

## Completion rule

এই remediation complete হবে কেবল যখন audit-এর প্রতিটি check `PASS`, চারটি current canonical
artifact independently `VERIFIED`, open invalidation resolved, strict checker PASS, এবং phase
advancement root integration owner দ্বারা আলাদা decision হিসেবে record হয়। Command exit code,
valid key possession, বা wrong-namespace `Good` output একা completion proof নয়।
