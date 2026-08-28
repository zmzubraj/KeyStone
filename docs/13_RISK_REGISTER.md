# Risk Register

| ID | Risk | Probability | Impact | Mitigation / decision |
|---|---|---:|---:|---|
| R1 | Reviewer says “this is just threshold encryption” | High | High | lead with property separation, canary audit semantics, correlation and deadline model |
| R2 | “Key availability” terminology already exists | High | Medium | use narrow “Dispute-Key Availability” and avoid first-ever broad claim |
| R3 | Sampling is misread as future proof | High | High | formal counterexample and selective-withholding figure |
| R4 | PoP/share proof prior art collision | High | Medium | cite it as established building block, claim composition only |
| R5 | Non-response slashing frames honest partitions | Medium | High | declare timing model; use graded warning/replacement/slashing |
| R6 | Correlated domain metadata is false | Medium | High | require attestable/operator metadata; evaluate sensitivity and concentration |
| R7 | Dealer prototype weakens credibility | High | Medium | explicit substitution boundary; add production DKG/PVSS for full paper |
| R8 | Non-standard group/handwritten crypto | Medium | High | research-only label, test vectors, external review, standard library migration |
| R9 | TEE dominates the narrative | Medium | Medium | keep TEE optional; DKA ends at authorized contribution delivery |
| R10 | Selective withholding defeats main claim | High | High | define audit/dispute readiness separately; scope main theorem; offer extension |
| R11 | Audit all-response rule causes false alarms | High | Medium | evaluate `q<s`, escalation, and health-versus-catastrophic semantics |
| R12 | Refresh confused with forward secrecy | Medium | High | explicitly separate share refresh and epoch key rotation |
| R13 | Contract cannot verify proofs cheaply | High | Medium | off-chain deterministic verification + commitments; report trust/cost |
| R14 | AI-specific contribution seems narrow | Medium | Medium | motivate with AI but formulate for encrypted optimistic execution generally |
| R15 | Experiment rare-event estimates are weak | Medium | Medium | exact formulas, confidence intervals, targeted importance sampling |
| R16 | Scope expands into full rollup | High | High | enforce `FREEZE.md`; no GPU/inference correctness implementation in MPP |

## Kill criteria

Reconsider the topic if a direct prior paper is found that already provides all of the following together: a rollup-specific DKA definition, non-revealing threshold-share readiness sampling, explicit failure/correlation bounds, authorization/deadline evidence, and an evaluation. Individual overlap with any one element is expected and does not invalidate the paper.
