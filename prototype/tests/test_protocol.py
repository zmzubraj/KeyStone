import random

from keystone.group import hash_to_scalar
from keystone.protocol import CustodianBehavior, derive_canary, execute_audit, execute_dispute
from keystone.threshold_kem import dealer_keygen, seal_record


def _setup():
    rng = random.Random(41)
    domains = ["aws", "aws", "gcp", "gcp", "azure", "azure", "independent"]
    epoch = dealer_keygen(7, 5, domains, randbelow=rng.randrange)
    sealed = seal_record(epoch.public_key, epoch.group, "r-1", b"sensitive inference", b"rollup")
    return epoch, sealed



def test_canary_is_publicly_deterministic_and_context_separated() -> None:
    epoch, _ = _setup()

    first = derive_canary(epoch, b"beacon-finalized", b"audit-slot-9")
    repeated = derive_canary(epoch, b"beacon-finalized", b"audit-slot-9")
    other_slot = derive_canary(epoch, b"beacon-finalized", b"audit-slot-10")
    other_beacon = derive_canary(epoch, b"different-beacon", b"audit-slot-9")

    assert first == repeated
    assert first != other_slot
    assert first != other_beacon
    assert epoch.group.validate_element(first)

    known_exponent = hash_to_scalar(
        epoch.group,
        b"KEYSTONE-CANARY-v1",
        epoch.epoch_id.encode("utf-8"),
        b"beacon-finalized",
        b"audit-slot-9",
        0,
    )
    assert first != pow(epoch.group.g, known_exponent, epoch.group.p)

def test_audit_produces_objective_invalid_and_nonresponse_evidence() -> None:
    epoch, _ = _setup()
    canary = derive_canary(epoch, b"beacon-43", b"audit-12")
    behaviors = {i: CustodianBehavior() for i in epoch.members}
    behaviors[2] = CustodianBehavior(latency_ms=900)
    behaviors[4] = CustodianBehavior(invalid_partial=True)

    result = execute_audit(
        epoch=epoch,
        canary_c1=canary,
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

    canary = derive_canary(epoch, b"beacon-47", b"audit-before-target")
    audit = execute_audit(
        epoch,
        canary,
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
