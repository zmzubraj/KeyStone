# KEYSTONE reproducibility report

Status: `DRAFT / PREAUTHORIZATION / MECHANICAL-ONLY`  
System: `KEYSTONE-MPP-F1`  
Current canonical phase: `INTAKE`  
Overall disposition: `CURRENT_TREE_REPLAY_REQUIRED`  
Scientific independence: `NOT_ESTABLISHED`  
Independent scientific reproduction: `MISSING`  
External validation: `MISSING`  
Primary confirmatory results: `NOT_COLLECTED`

This report separates an earlier same-host isolated mechanical replay from
scientific reproduction. It may not promote C001, C002, or C003, may not advance
the canonical phase, and may not convert draft analytic, simulated, or internal
engineering outputs into independently verified scientific evidence.

## Primary-result boundary

The design-layer primary-results planning contract contains **9 result slots**.
Every slot remains `authorized=false`, `independent=false`,
`observed_outcome=NOT_COLLECTED`, `estimate=NOT_ESTIMATED`, and
`claim_ceiling=V0 ASSERTED`. The canonical
`05-analysis/results/primary-results.csv` artifact remains `MISSING`.
Therefore this report contains no confirmatory
effect, no deadline result, and no success claim.

## Existing isolated mechanical receipt

| Field | Recorded value |
| --- | --- |
| Receipt generated at | `2026-08-30T04:52:14Z` |
| Receipt status | `MECHANICAL_PASS` |
| Executor class | `SECOND_AGENT_SAME_HOST_ISOLATED_COPY` |
| Scientific evidence status | `NOT_INDEPENDENT_SCIENTIFIC_VERIFICATION` |
| Commands mechanically passing | `10/10` |
| Source tree unchanged during that replay | `true` |
| Isolated copy unchanged during that replay | `true` |
| Network isolation | `TOOL_FLAGS_ONLY_NOT_KERNEL_ENFORCED` |
| External sharing | `NOT_PERFORMED` |

The receipt is hash-verified by
`prototype/results/engineering_qa/isolated_reproduction/receipt.json.sha256`.
Its scope is a historical same-host mechanical snapshot, not an independent
scientific verification event.

## Current-tree binding audit

| Binding | Receipt hash | Current hash | Match |
| --- | --- | --- | --- |
| Manuscript source manifest | `ac4b88086b7978a76e46385a2d5353b629862d1edfa1d7b599275b78f0257c92` | `a626646540616ce5a65213492f729c5a279ff3065b7afccdce98cd8c72f7b749` | `false` |
| Program state | `e1a8185c07a300a6b3d1c61f50d7f4ada9ddabffdcccabd52505b4645fda040a` | `1e61b34c07dbbe0a41986372c7fd070f352be46b2caed8fc4d5ca8efa1d78eb0` | `false` |

Because the current binding disposition is `CURRENT_TREE_REPLAY_REQUIRED`, the earlier receipt
must not be cited as a clean reconstruction of the current manuscript package.
A fresh replay can establish current mechanical consistency only; it still cannot
satisfy independent scientific reproduction.

## External-validation inventory

- No canonical external-validation artifact exists.

No missing result or validation artifact is silently imputed. A justified `N/A`
would require a narrower claim ceiling and independent signed verification; this
report does not issue that disposition.

## Receipt residual limitations

- same host and potentially shared host-level caches
- no external operator identity binding
- tool offline flags are not kernel-enforced network isolation
- no scientific independence or independent scientific verification
- no distributed deadline execution
- no venue or institutional approval

## Smallest adequate completion path

1. Close `REM-001` with an authenticated independent human INTAKE return.
2. Close novelty and methods gates before any new confirmatory execution.
3. Execute only the separately authorized frozen pilot and preserve failures,
   seeds, environments, exclusions, and deviations.
4. Generate a fresh current-tree mechanical receipt after the integrated evidence
   and manuscript revision is frozen.
5. Obtain a genuinely independent clean-machine reconstruction with authenticated
   identity, competence, conflict, commands, hashes, discrepancies, and signed
   artifact-specific dispositions.
6. Provide external/domain-equivalent validation or formally narrow every claim
   that exceeds simulation/internal evidence.

Until those steps are independently verified, reproducibility remains a draft
mechanical property of selected artifacts—not a scientific gate pass and not a
submission-readiness claim.
