# KEYSTONE PC03 Prospective Design Assessment

Status: `DRAFT / PREAUTHORIZATION / NON-EXECUTABLE`
System: `KEYSTONE-MPP-F1`
Date: `2026-08-30`
Current canonical phase: `INTAKE`

> Developmental AI methods review only. This package does not authorize execution, does not independently verify feasibility, and does not promote the research phase.

## Scope

This developmental challenge records the smallest stochastic design surface that
the current frozen baseline appeared to support before root-level integration
reconciled the simulator denominator semantics. It does not define the
operative confirmatory count contract.

It preserves three boundaries:

- author metadata remains deferred;
- the integrated amendment remains the only operative count contract;
- all five result families remain `BLOCKED_PENDING_GATE`, historically proposed,
  or explicitly excluded;
- historical sweeps remain exploratory context and do not determine confirmatory family size.

## Challenge proposal disposition

| Result ID | Lane | Proposed cell | Challenge-only disposition | Proposed count or exclusion |
| --- | --- | --- | --- | --- |
| `RID-C003-IID-001` | support | `iid-10pct-uniform` at the frozen baseline `n=32, t=22, s=8, q=8` | proposed, not adopted | `97` valid seed-level runs in the single primary baseline cell |
| `RID-C003-CORR-001` | support | truthful-domain correlated placement comparison | excluded for now | `EXCLUDED_PENDING_TRUTHFUL_DOMAIN_LABEL_SOURCE` |
| `RID-C003-STRAT-001` | support | matched `uniform` versus `stratified` comparison at `sample_size=8` under the frozen domain-outage baseline | proposed, not adopted | `193` matched seed pairs in the single primary baseline cell |
| `RID-C003-SW-001` | minimum-core limitation | `selective_withholders = n - t + 1 = 11` under the frozen baseline | proposed, not adopted | `193` paired runs in the single limitation-bearing baseline cell |
| `RID-C003-DEADLINE-001` | extended full-paper | distributed conditional-deadline benchmark | excluded for now | `EXCLUDED_PENDING_ENVIRONMENT_PROFILE` |

## Decision logic

- `RID-C003-IID-001` uses a result-blind two-sided Wilson precision target of `+/- 0.10` at `alpha=0.05`. That yielded a challenge proposal of `97` seed-level runs in one baseline cell and already dominated the one-sided zero-failure `< 0.10` upper-bound check (`29` runs).
- `RID-C003-STRAT-001` and `RID-C003-SW-001` use the paired-gap variable `D_i in {-1,0,1}` with the conservative bound `Var(D_i) <= 0.50`, a two-sided precision target of `+/- 0.10`, and `alpha=0.05`. That yielded a challenge proposal of `193` matched pairs per operative cell without importing exploratory discordance estimates.
- `RID-C003-CORR-001` is not frozen into the confirmatory minimum lane because the current artifacts do not yet freeze both the truthful domain-label source and the required concentrated-placement comparison cell. If those are later frozen, a separate amendment can adopt the non-operative sensitivity count of `126` runs per cell for two protected cells at `alpha=0.025`.
- `RID-C003-DEADLINE-001` remains excluded because every current environment-profile field that would define the unit, denominator, and claim-safe deadline interpretation is still `UNRESOLVED_BEFORE_EXECUTION`.
- Root integration later found that the simulator returns aggregate proportions from many independent synthetic scenario draws inside each seed block. The operative integrated amendment therefore uses draw-level Hoeffding bounds with 32 primary seed blocks x 4,096 draws = 131,072 primary draws per included cell. This challenge file remains a historical developmental input, not the final operative count contract.

## Operational rules

- Every included challenge proposal uses one deterministic seed per replicate; no nested events inside a proposed seed-level run count as extra replicates.
- One same-seed rerun is permitted only for infrastructure failure before a valid result object exists; otherwise the run remains failed or missing.
- Included support lanes may inform bounded manuscript wording only after `PC01`, `PC02`, and an independent PC03 review are satisfied.
- The selective-withholding family remains limitation-bearing regardless of direction; it may not be omitted if the observed gap is inconvenient.

## Residual risks

- Excluding the correlated-domain and deadline lanes means broader `C003` wording still requires either later amendment or explicit manuscript narrowing.
- The integrated amendment supersedes the 97/193 seed-level proposals because the final confirmatory denominator is independent synthetic scenario draws, not seed-run aggregates.
- The chosen precision target is decision-oriented for a minimum publishable prototype, not a field-level operating guarantee.
- No authenticated independent methods sign-off exists yet; this is only a prepared internal package.
