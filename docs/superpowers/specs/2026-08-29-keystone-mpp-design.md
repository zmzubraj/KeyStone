# KEYSTONE MPP Design Specification

**Date:** 2026-08-29  
**Status:** frozen and implemented as v1.0

## Goal

Produce a minimum publishable research artifact that formalizes and prototypes auditable dispute-key availability for encrypted AI rollups without claiming a new threshold-cryptography primitive.

## User-visible outcome

A researcher can run one command to verify the threshold cryptographic path, calculate the exact static sampling bound, simulate independent/correlated/selective failures, regenerate paper figures, and inspect protocol/contract/diagram specifications.

## Architecture

- Epoch-level threshold DH key with one share per custodian.
- Per-record AES-GCM key and threshold-KEM wrapping.
- Fresh canary partial-decryption audits with DLEQ proofs.
- Uniform and failure-domain-stratified sampling.
- Public request/deadline/evidence interface.
- Authorized threshold combination and record opening.
- Monte Carlo evaluation separated from cryptographic operation benchmarks.

## Components and interfaces

### Crypto core

`dealer_keygen(n,t,domains) -> EpochKey`

`seal_record(PK,group,record_id,plaintext,aad) -> SealedRecord`

`create_partial_decryption(member,c1,group,context) -> PartialDecryption`

`verify_partial_decryption(...) -> bool`

`open_record(epoch,sealed,partials,context) -> bytes`

### Sampling

`catastrophic_false_accept_probability(n,t,s,q) -> float`

`sample_uniform(population,s,beacon) -> list`

`sample_stratified(member_domains,s,beacon,minimum_per_domain) -> list`

### Protocol

`execute_audit(...) -> AuditResult`

`execute_dispute(...) -> DisputeResult`

### Simulation

`run_monte_carlo(Scenario) -> metrics`

## Invariants

- Routine audits never use production record `C1`.
- A proof is bound to request context and member index.
- Duplicate member indices do not count twice.
- Fewer than `t` valid partials cannot open a record.
- Invalid partials do not count toward threshold.
- Audit readiness and dispute readiness remain separate variables.
- Every probability output names or encodes its scenario parameters and seed.

## Error handling

- Invalid parameters raise `ValueError`.
- Insufficient threshold raises `InsufficientValidShares`.
- Authentication failure raises `RecordDecryptionError`.
- Protocol nonresponse/invalid response is represented as evidence rather than an unhandled exception.

## Testing

Six test files cover cryptographic correctness, proof tampering/context, exact bounds, deterministic sampling, protocol evidence, selective withholding, simulation reproducibility, and domain-diversity effects.

## Non-goals

- production DKG/PVSS;
- audited/standardized threshold library;
- complete AI rollup;
- on-chain DLEQ verification;
- unconditional future availability;
- full adaptive selective-withholding defense.
