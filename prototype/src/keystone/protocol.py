from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping, Sequence

from .group import hash_to_group
from .threshold_kem import (
    EpochKey,
    InsufficientValidShares,
    PartialDecryption,
    SealedRecord,
    create_partial_decryption,
    open_record,
    verify_partial_decryption,
)


@dataclass(frozen=True, slots=True)
class CustodianBehavior:
    ready_for_audit: bool = True
    ready_for_dispute: bool = True
    latency_ms: int = 10
    invalid_partial: bool = False


@dataclass(frozen=True, slots=True)
class Evidence:
    request_kind: str
    member_index: int
    member_id: str
    kind: str
    detail: str


@dataclass(frozen=True, slots=True)
class AuditResult:
    passed: bool
    valid_responses: int
    required_valid: int
    evidence: tuple[Evidence, ...]


@dataclass(frozen=True, slots=True)
class DisputeResult:
    success: bool
    valid_responses: int
    plaintext: bytes | None
    evidence: tuple[Evidence, ...]


def derive_canary(epoch: EpochKey, beacon: bytes, context: bytes) -> int:
    """Derive a canonical canary from public post-commit randomness.

    The hash-to-group mapping does not expose the canary's discrete logarithm
    relative to the epoch generator.  Deterministic derivation also prevents
    a coordinator from substituting a production KEM component as an audit.
    """

    if not beacon:
        raise ValueError("beacon must not be empty")
    if not context:
        raise ValueError("context must not be empty")
    return hash_to_group(
        epoch.group,
        b"KEYSTONE-CANARY-v1",
        epoch.epoch_id.encode("utf-8"),
        beacon,
        context,
    )


def _behavior(behaviors: Mapping[int, CustodianBehavior], index: int) -> CustodianBehavior:
    return behaviors.get(index, CustodianBehavior())


def _possibly_corrupt(
    epoch: EpochKey,
    partial: PartialDecryption,
    behavior: CustodianBehavior,
) -> PartialDecryption:
    if not behavior.invalid_partial:
        return partial
    return partial.with_value((partial.value * epoch.group.g) % epoch.group.p)


def execute_audit(
    epoch: EpochKey,
    canary_c1: int,
    sampled_indices: Sequence[int],
    behaviors: Mapping[int, CustodianBehavior],
    deadline_ms: int,
    required_valid: int,
    context: bytes,
) -> AuditResult:
    if not 0 <= required_valid <= len(sampled_indices):
        raise ValueError("required_valid must fit inside the sample")
    evidence: list[Evidence] = []
    valid_count = 0
    for index in sampled_indices:
        member = epoch.members[index]
        behavior = _behavior(behaviors, index)
        if not behavior.ready_for_audit or behavior.latency_ms > deadline_ms:
            evidence.append(
                Evidence(
                    "AUDIT",
                    index,
                    member.member_id,
                    "NON_RESPONSE",
                    f"no valid response before {deadline_ms} ms",
                )
            )
            continue
        partial = create_partial_decryption(member, canary_c1, epoch.group, context)
        partial = _possibly_corrupt(epoch, partial, behavior)
        if verify_partial_decryption(member, canary_c1, partial, epoch.group, context):
            valid_count += 1
        else:
            evidence.append(
                Evidence(
                    "AUDIT",
                    index,
                    member.member_id,
                    "INVALID_PARTIAL",
                    "DLEQ verification failed",
                )
            )
    return AuditResult(valid_count >= required_valid, valid_count, required_valid, tuple(evidence))


def execute_dispute(
    epoch: EpochKey,
    sealed: SealedRecord,
    behaviors: Mapping[int, CustodianBehavior],
    deadline_ms: int,
    context: bytes,
) -> DisputeResult:
    evidence: list[Evidence] = []
    valid_partials: list[PartialDecryption] = []
    ordering = sorted(epoch.members, key=lambda index: (_behavior(behaviors, index).latency_ms, index))
    for index in ordering:
        member = epoch.members[index]
        behavior = _behavior(behaviors, index)
        if not behavior.ready_for_dispute or behavior.latency_ms > deadline_ms:
            evidence.append(
                Evidence(
                    "DISPUTE",
                    index,
                    member.member_id,
                    "NON_RESPONSE",
                    f"no authorized response before {deadline_ms} ms",
                )
            )
            continue
        partial = create_partial_decryption(member, sealed.c1, epoch.group, context)
        partial = _possibly_corrupt(epoch, partial, behavior)
        if verify_partial_decryption(member, sealed.c1, partial, epoch.group, context):
            valid_partials.append(partial)
        else:
            evidence.append(
                Evidence(
                    "DISPUTE",
                    index,
                    member.member_id,
                    "INVALID_PARTIAL",
                    "DLEQ verification failed",
                )
            )

    if len(valid_partials) < epoch.threshold:
        return DisputeResult(False, len(valid_partials), None, tuple(evidence))
    try:
        plaintext = open_record(epoch, sealed, valid_partials, context)
    except InsufficientValidShares:
        return DisputeResult(False, len(valid_partials), None, tuple(evidence))
    return DisputeResult(True, len(valid_partials), plaintext, tuple(evidence))
