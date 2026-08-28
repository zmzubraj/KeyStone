# Reviewer Attack Matrix

| Reviewer objection | Best response | Artifact pointer |
|---|---|---|
| “This is just threshold encryption.” | Threshold encryption is a building block; DKA formalizes an unmet deadline service property and sampled audit objective. | `docs/03`, `docs/15` |
| “PVSS already proves shares exist.” | Initial correctness does not imply ongoing share access, online service, policy path, or dispute deadline. | `docs/01`, `docs/03` |
| “A ping is enough.” | A ping does not exercise the current share or produce a cryptographically verified partial operation. | DLEQ tests/protocol |
| “Sampling cannot prove the future.” | Correct; the paper explicitly proves a bound only for its temporal model and gives a counterexample. | Proposition P1, Figure 4 |
| “Nonresponse cannot be fairly slashed.” | Hard blame is conditioned on timing assumptions; the design separates warning/replacement from cryptographic guilt. | `docs/07`, contract README |
| “Correlated failures invalidate the bound.” | Uniform theorem is static-node level; correlation is modeled separately and motivates placement/stratified sampling. | Figures 3/5 |
| “TEE is trusted.” | TEE is an optional authorized destination; DKA can be defined independently. | `FREEZE.md` |
| “Dealer setup is insecure.” | It is an MPP substitution with a frozen production DKG/PVSS boundary. | `docs/08` |
| “AI is irrelevant.” | AI is the motivating encrypted optimistic workload; the property generalizes to encrypted rollups. | Introduction framing |
