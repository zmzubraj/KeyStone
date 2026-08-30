import random

import keystone.protocol as protocol_module
from keystone.protocol import CustodianBehavior, derive_canary, execute_audit, execute_dispute
from keystone.threshold_kem import dealer_keygen, seal_record


def _setup():
    rng = random.Random(41)
    domains = ["aws", "aws", "gcp", "gcp", "azure", "azure", "independent"]
    epoch = dealer_keygen(7, 5, domains, randbelow=rng.randrange)
    sealed = seal_record(epoch.public_key, epoch.group, "r-1", b"sensitive inference", b"rollup")
    return epoch, sealed



def test_canary_is_publicly_deterministic_context_separated_and_in_group() -> None:
    epoch, _ = _setup()

    first = derive_canary(epoch, b"beacon-finalized", b"audit-slot-9")
    repeated = derive_canary(epoch, b"beacon-finalized", b"audit-slot-9")
    other_slot = derive_canary(epoch, b"beacon-finalized", b"audit-slot-10")
    other_beacon = derive_canary(epoch, b"different-beacon", b"audit-slot-9")

    assert first == repeated
    assert first != other_slot
    assert first != other_beacon
    assert epoch.group.validate_element(first)

def test_audit_produces_objective_invalid_and_nonresponse_evidence() -> None:
    epoch, _ = _setup()
    behaviors = {i: CustodianBehavior() for i in epoch.members}
    behaviors[2] = CustodianBehavior(latency_ms=900)
    behaviors[4] = CustodianBehavior(invalid_partial=True)

    result = execute_audit(
        epoch=epoch,
        beacon=b"beacon-43",
        sampled_indices=[1, 2, 3, 4],
        behaviors=behaviors,
        deadline_ms=500,
        required_valid=4,
        context=b"audit-12",
    )

    assert not result.passed
    assert result.valid_responses == 2
    assert {(e.member_index, e.kind) for e in result.evidence} == {
        (2, "NON_RESPONSE"),
        (4, "INVALID_PARTIAL"),
    }


def test_audit_derives_challenge_internally_from_beacon(monkeypatch) -> None:
    epoch, _ = _setup()
    beacon = b"beacon-internal-derivation"
    context = b"audit-internal-derivation"
    expected = derive_canary(epoch, beacon, context)
    observed: list[tuple[object, bytes, bytes]] = []

    def recording_derive_canary(epoch_arg, beacon_arg: bytes, context_arg: bytes) -> int:
        observed.append((epoch_arg, beacon_arg, context_arg))
        return expected

    monkeypatch.setattr(protocol_module, "derive_canary", recording_derive_canary)
    result = execute_audit(
        epoch,
        beacon,
        sampled_indices=[1],
        behaviors={1: CustodianBehavior()},
        deadline_ms=500,
        required_valid=1,
        context=context,
    )

    assert result.passed
    assert observed == [(epoch, beacon, context)]


def test_dispute_decrypts_when_threshold_valid_responses_arrive() -> None:
    epoch, sealed = _setup()
    behaviors = {i: CustodianBehavior(latency_ms=20 + i) for i in epoch.members}

    result = execute_dispute(
        epoch,
        sealed,
        behaviors,
        deadline_ms=200,
        context=b"dispute:r-1:committee-A",
    )

    assert result.success
    assert result.plaintext == b"sensitive inference"
    assert result.valid_responses >= epoch.threshold


def test_selective_withholding_can_pass_audit_but_fail_targeted_dispute() -> None:
    epoch, sealed = _setup()
    behaviors = {i: CustodianBehavior() for i in epoch.members}
    for i in [4, 5, 6]:
        behaviors[i] = CustodianBehavior(ready_for_audit=True, ready_for_dispute=False)

    audit = execute_audit(
        epoch,
        b"beacon-47",
        sampled_indices=[1, 4, 6],
        behaviors=behaviors,
        deadline_ms=500,
        required_valid=3,
        context=b"audit-before-target",
    )
    dispute = execute_dispute(
        epoch,
        sealed,
        behaviors,
        deadline_ms=500,
        context=b"dispute:r-1:targeted",
    )

    assert audit.passed
    assert not dispute.success
    assert dispute.valid_responses == 4
