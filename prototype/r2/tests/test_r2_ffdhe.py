"""W11 tests: RFC 9380 expander vectors, Jacobi membership, and the fixed ffdhe hash-to-group.

R2_CORRECTNESS in r2-design-freeze.json requires the expanded hash and the
Jacobi-symbol membership test to agree with ``x^q mod p == 1`` on random and
adversarial inputs.
"""
from __future__ import annotations

import json
import secrets
from pathlib import Path

import pytest

from keystone.group import hash_to_group as r1_hash_to_group
from keystone_r2 import ffdhe

VECTORS = json.loads((Path(__file__).parent / "data" / "rfc9380_k1_xmd_sha256.json").read_text())


@pytest.mark.parametrize("case", VECTORS["cases"], ids=lambda c: f"len{len(c['msg'])}-out{c['len_in_bytes']}")
def test_expand_message_xmd_matches_rfc9380_vectors(case: dict) -> None:
    out = ffdhe.expand_message_xmd(case["msg"].encode(), VECTORS["dst"].encode(), case["len_in_bytes"])
    assert out.hex() == case["uniform_bytes"]


@pytest.mark.parametrize("name", sorted(ffdhe.GROUPS))
def test_jacobi_membership_agrees_with_full_exponentiation(name: str) -> None:
    group = ffdhe.GROUPS[name]
    p, q = group.p, group.q
    adversarial = [1, 2, 3, 4, p - 1, p - 2, (p - 1) // 2, (p + 1) // 2, group.g, pow(group.g, 7, p)]
    randoms = [secrets.randbelow(p - 1) + 1 for _ in range(200)]
    for x in adversarial + randoms:
        assert ffdhe.is_member(group, x) == (pow(x, q, p) == 1), x
    for x in (0, p, p + 1, -1):
        assert not ffdhe.is_member(group, x)


@pytest.mark.parametrize("name", sorted(ffdhe.GROUPS))
def test_hash_to_group_output_is_member_deterministic_and_separated(name: str) -> None:
    group = ffdhe.GROUPS[name]
    element = ffdhe.hash_to_group(group, b"canary", b"E7", b"slot-3")
    assert ffdhe.is_member(group, element) and element != 1
    assert pow(element, group.q, group.p) == 1
    assert element == ffdhe.hash_to_group(group, b"canary", b"E7", b"slot-3")
    assert element != ffdhe.hash_to_group(group, b"dispute", b"E7", b"slot-3")
    assert element != ffdhe.hash_to_group(group, b"canary", b"E7slot-3")


def test_w11_defect_documented_and_fixed() -> None:
    """R1 canaries are squares of integers below about 2^256, hence below 2^512;
    the R2 map spans the whole 2048-bit group."""
    group = ffdhe.GROUPS["ffdhe2048"]
    r1 = [r1_hash_to_group(group, b"KEYSTONE-CANARY-v1", i.to_bytes(4, "big")) for i in range(64)]
    r2 = [ffdhe.hash_to_group(group, b"canary", i.to_bytes(4, "big")) for i in range(64)]
    assert max(v.bit_length() for v in r1) <= 514
    assert min(v.bit_length() for v in r2) > 2000
