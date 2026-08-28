import random

from keystone.dleq import prove_equal_discrete_logs, verify_equal_discrete_logs
from keystone.group import RESEARCH_GROUP


def test_valid_dleq_proof_verifies_and_is_context_bound() -> None:
    rng = random.Random(19)
    witness = 1122334455
    base_2 = pow(RESEARCH_GROUP.g, 17, RESEARCH_GROUP.p)
    public_1 = pow(RESEARCH_GROUP.g, witness, RESEARCH_GROUP.p)
    public_2 = pow(base_2, witness, RESEARCH_GROUP.p)

    proof = prove_equal_discrete_logs(
        witness=witness,
        base_1=RESEARCH_GROUP.g,
        public_1=public_1,
        base_2=base_2,
        public_2=public_2,
        group=RESEARCH_GROUP,
        context=b"epoch-3:audit-9",
        randbelow=rng.randrange,
    )

    assert verify_equal_discrete_logs(
        proof,
        RESEARCH_GROUP.g,
        public_1,
        base_2,
        public_2,
        RESEARCH_GROUP,
        b"epoch-3:audit-9",
    )
    assert not verify_equal_discrete_logs(
        proof,
        RESEARCH_GROUP.g,
        public_1,
        base_2,
        public_2,
        RESEARCH_GROUP,
        b"epoch-3:audit-10",
    )


def test_tampered_partial_decryption_fails_dleq_verification() -> None:
    rng = random.Random(23)
    witness = 445566
    base_2 = pow(RESEARCH_GROUP.g, 29, RESEARCH_GROUP.p)
    public_1 = pow(RESEARCH_GROUP.g, witness, RESEARCH_GROUP.p)
    public_2 = pow(base_2, witness, RESEARCH_GROUP.p)
    proof = prove_equal_discrete_logs(
        witness,
        RESEARCH_GROUP.g,
        public_1,
        base_2,
        public_2,
        RESEARCH_GROUP,
        b"audit",
        rng.randrange,
    )

    tampered = (public_2 * RESEARCH_GROUP.g) % RESEARCH_GROUP.p
    assert not verify_equal_discrete_logs(
        proof,
        RESEARCH_GROUP.g,
        public_1,
        base_2,
        tampered,
        RESEARCH_GROUP,
        b"audit",
    )
