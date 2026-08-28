# Publication Success Gates

## Gate G0 — Scope freeze

Pass condition: title, question, claim boundary, architecture, and exclusions match `FREEZE.md`.

## Gate G1 — Formal consistency

Pass condition:

- every property has a timeline and adversary condition;
- audit readiness and dispute readiness are distinct;
- probability statements name their sample/failure model;
- liveness statements name their timing assumption;
- no theorem claims unconditional future availability.

## Gate G2 — Cryptographic core

Pass condition:

- `t` valid partials open a record;
- `t-1` do not;
- malformed partials are excluded;
- DLEQ context replay fails;
- production records are never used as routine audit canaries.

Current state: passed by automated tests.

## Gate G3 — Analytical validation

Pass condition: exhaustive/simulation results match the hypergeometric formula inside statistical tolerance across a parameter grid.

Current state: baseline formula and deterministic simulator implemented; full exhaustive grid remains a strengthening task.

## Gate G4 — Correlation result

Pass condition: the paper shows at least one significant divergence between independent and correlated models and reports placement/sampling implications.

Current state: baseline domain-diversity and stratified figures generated.

## Gate G5 — Limitation honesty

Pass condition: selective withholding is explicitly modeled, illustrated, and excluded from stronger claims unless a new construction is added.

Current state: passed; automated test and Figure 4.

## Gate G6 — Performance evidence

Pass condition: median/p95 proof generation, verification, combination/opening, network deadline, and contract overhead reported with hardware/software metadata.

Current state: single-machine crypto baseline and a two-test Foundry gas
snapshot are included; distributed-network measurements, fuzz/invariant
coverage, and a complete contract-overhead table remain.

## Gate G7 — Reproducibility

Pass condition:

- clean environment setup documented;
- all seeds/configurations included;
- one command regenerates tests, datasets, and figures;
- artifact hash manifest included;
- limitations and non-production status visible.

Current state: the Python environment is locked with `uv`, root `make` targets
cover setup/fast verification/full reproduction, and the macOS/Apple-Silicon
baseline was regenerated. Cross-platform clean-machine reproduction remains an
external confirmation task.

## Gate G8 — External review

Pass condition:

- one threshold-cryptography reviewer;
- one distributed-systems/blockchain reviewer;
- one adversarial “novelty attack” review;
- all blocking comments resolved or documented.

## Outcome tiers

- **MPP success:** G0–G5 and G7 pass.
- **Workshop-ready:** G0–G7 pass.
- **Full-paper-ready:** G0–G8 pass with distributed testbed and production DKG/PVSS substitution.
