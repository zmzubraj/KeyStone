# KEYSTONE deadline-pilot execution contract

Status: `DRAFT_PREAUTHORIZATION`
System: `KEYSTONE-MPP-F1`
Result ID: `RID-C003-DEADLINE-001`
Current canonical phase: `INTAKE`
Execution authorization: `NOT_AUTHORIZED`
Scientific evidence boundary: design-only and not confirmatory evidence

This contract freezes the design-only boundary for the deadline pilot package.
It does not authorize any distributed run.

## Replicate definition

A replicate is one complete end-to-end distributed trace per seed and
environment profile. Events inside a trace are nested observations and are not
replicates.

## Required trace metadata

- seed
- environment profile
- host topology
- run day
- version or commit
- timestamps
- outcome
- failure classification
- artifact hashes

## Blocking factors

- the environment profile remains unresolved before execution
- the deadline interpretation remains unresolved before execution
- the trace denominator remains unresolved before execution
- the precision target remains unresolved before execution
- the multiplicity rule remains unresolved before execution
- novelty, accountable approval, and independent verification remain open

## Required endpoint and telemetry

The required endpoint is the conditional deadline success measure under the
declared synthetic synchrony model. Telemetry must preserve seed, profile,
topology, run-day block, node outcome, trace outcome, failure class, and output
artifact hashes without backfilling missing fields.

## Forbidden inputs and actions

- production ciphertext
- live secrets
- personal data
- production systems
- unpublished third-party data
- external sharing
- performance inspection before design freeze

## Permitted preauthorization activity

Only integrity and completeness checks are permitted before accountable
authorization. Any attempted distributed execution remains blocked.
