# KEYSTONE Solidity Bulletin Board

`KeystoneBulletinBoard.sol` is a research-only ledger boundary for:

- epoch/member registration;
- audit and dispute request opening;
- canonical deadlines;
- one response commitment per sampled custodian;
- equivocation observations;
- off-chain proof-invalid verdict recording;
- final response/missing/invalid bitmaps.

## What it proves

The contract makes request timing, membership, and submission/non-submission publicly observable. It does not itself prove that a missing member was malicious; that conclusion depends on the network/timing model. It also does not verify DLEQ proofs on-chain. The MPP assumes deterministic off-chain verification and records an evidence hash through an adjudication interface.

## Recommended production evolution

1. Replace `admin` with governance/multisig or an optimistic adjudication protocol.
2. Bind epoch registration to DKG/PVSS output and stake.
3. Add signatures or proof bytes to DA rather than storing large payloads on-chain.
4. Add challengeable proof-verdict commitments or a zk verifier if justified.
5. Add graded penalties: warning, inactivity, replacement, hard slash.
6. Replace the research-only bounded test profile with a larger independent
   audit campaign before production use.

## Foundry setup

```bash
forge build --root contracts
forge test --root contracts -vvv
make snapshot
make snapshot-check
```

The current tests use a minimal local Foundry cheatcode interface, so no
`forge-std` download is required. On 2026-08-29 the source compiled with Solc
0.8.24 and 19 tests passed: deterministic boundary/lifecycle tests, three
512-run fuzz properties, eight dedicated gas measurements, and two stateful
invariants exercised across 64 runs × 32 calls. The operation table is generated
as `contracts/gas_report.csv` from `.gas-snapshot`; setup gas is excluded, but
small harness overhead may remain. These are internal research measurements,
not production audit evidence.
