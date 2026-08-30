# PC03 Calculation Notes

Status: `DRAFT / PREAUTHORIZATION / NON-EXECUTABLE`
Date: `2026-08-30`

Exploratory outputs were not used to set confirmatory thresholds in this file.
These calculations document the developmental challenge's historical
seed-level proposal only. They are not the operative integrated count contract.

## Inputs

- Unpaired families: `alpha=0.05`, `z=1.9599639845`, target half-width `h=0.10`.
- Paired families: `alpha=0.05`, `z=1.9599639845`, target half-width `h=0.10`, conservative discordance variance cap `q=0.50`.
- Future correlated-lane sensitivity only: two protected cells with `alpha=0.025`, `z=2.2414027276`, and `h=0.10`.

## Equations

1. Unpaired binary precision:
   `n = ceil(z^2 * 0.25 / h^2)`

2. Zero-failure upper-bound assurance:
   `n >= ceil(log(0.05) / log(0.90)) = 29` for a one-sided 95 percent upper bound below `0.10`.

3. Paired-gap precision with `D_i in {-1,0,1}` and `Var(D_i) <= q`:
   `n = ceil(z^2 * q / h^2)`

## Historical derived counts

- `RID-C003-IID-001`: `ceil(1.9599639845^2 * 0.25 / 0.10^2) = 97`.
- `RID-C003-STRAT-001`: `ceil(1.9599639845^2 * 0.50 / 0.10^2) = 193`.
- `RID-C003-SW-001`: same paired-gap envelope as `RID-C003-STRAT-001`, so `193`.
- `RID-C003-CORR-001`: non-operative future sensitivity only, `ceil(2.2414027276^2 * 0.25 / 0.10^2) = 126` per cell if two protected cells are later frozen. Not operative in this amendment.
- `RID-C003-DEADLINE-001`: no valid count is derivable while the environment profile, trace denominator, and claim-safe deadline interpretation remain unresolved; the lane stays excluded.

## Integrated operative contract

The root-integrated amendment at
`research-case/03-design/pc03-prospective-amendment.md` supersedes the
historical 97/193 seed-level proposal. The current simulator emits aggregate
proportions from many independent synthetic scenario draws inside each seed
block, so treating each seed aggregate as a Bernoulli replicate creates a
denominator mismatch. The operative confirmatory contract therefore uses:

- 32 primary seed blocks and four reserve blocks per included cell;
- 4,096 independent synthetic scenario draws per block;
- 131,072 primary draws per included cell;
- a distribution-free requirement of 73,778 draws under the draw-level
  Hoeffding bounds recorded in the integrated amendment.

## Why the historical proposal was still useful

- The frozen baseline already names one primary IID cell (`iid-10pct-uniform`), one primary sampling-policy cell at `sample_size=8`, and one limitation-bearing selective-withholding cell at `w=11`. Converting broader exploratory sweeps into confirmatory families would be hindsight inflation.
- The `+/- 0.10` and `+/- 0.10` targets are coarse but decision-relevant for an MPP because these lanes qualify bounded model behavior rather than estimate a field deployment rate.
- Using the worst-case paired variance cap `q=0.50` avoids importing exploratory discordance estimates.
- Exclusion is preferred over guessed counts when the unit or denominator is not yet frozen.

## Historical deterministic seed proposal

- `RID-C003-IID-001`: derive seed `i` from `SHA256("KEYSTONE-PC03|RID-C003-IID-001|iid-10pct-uniform|i")` and use ascending replicate index `1..97`.
- `RID-C003-STRAT-001`: derive pair seed `i` from `SHA256("KEYSTONE-PC03|RID-C003-STRAT-001|sample-size-8|i")`; both policies use the same seed, and policy order alternates by pair-index parity.
- `RID-C003-SW-001`: derive seed `i` from `SHA256("KEYSTONE-PC03|RID-C003-SW-001|withholders-11|i")` and use ascending replicate index `1..193`.

The operative deterministic stream contract is the block schedule in
`research-case/03-design/pc03-seed-schedule.csv`.
