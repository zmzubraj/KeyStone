"""Tests for the R2 ristretto255 core: the D1 supply-chain usage conditions and
the group arithmetic that Shamir sharing and Lagrange reconstruction rely on.

These run before any R2 measurement (R2_CORRECTNESS in r2-design-freeze.json).
"""
from __future__ import annotations

import os
import secrets
from pathlib import Path

import pytest

from keystone_r2 import ristretto as rs

SRC = Path(__file__).resolve().parents[1] / "src" / "keystone_r2"


def _random_full_range_scalar() -> int:
    return secrets.randbelow(rs.ORDER - 1) + 1


def _lagrange_at_zero(index: int, indices: list[int]) -> int:
    numerator, denominator = 1, 1
    for other in indices:
        if other != index:
            numerator = numerator * (-other) % rs.ORDER
            denominator = denominator * (index - other) % rs.ORDER
    return numerator * pow(denominator, -1, rs.ORDER) % rs.ORDER


def test_embedded_libsodium_matches_reviewed_binary() -> None:
    """Condition 2: the installed rbcl embeds exactly the reviewed libsodium build."""
    assert rs.embedded_library_sha256() == rs.EMBEDDED_LIBSODIUM_SHA256


def test_rbcl_temporary_library_is_removed() -> None:
    """Condition 6: the temporary libsodium copy written at import is deleted."""
    assert not os.path.exists(rs._RBCL_LOADER.lib_path)


@pytest.mark.parametrize("bad", [bytes(32), b"\x01" * 32, b"\xff" * 32, b"\x00" * 31])
def test_invalid_points_are_rejected_by_our_validation(bad: bytes) -> None:
    """Condition 3: KEYSTONE validates points itself, including the identity encoding."""
    with pytest.raises(rs.InvalidPoint):
        rs.validate_point(bad)
    with pytest.raises(rs.InvalidPoint):
        rs.multiply(5, bad)


def test_no_ed25519_api_is_used() -> None:
    """Condition 4: the source never calls the ed25519 API (CVE-2025-69277 scope)."""
    offenders = [p.name for p in SRC.glob("*.py") if "ed25519" in p.read_text() and p.name != "ristretto.py"]
    ristretto_calls = [line for line in (SRC / "ristretto.py").read_text().splitlines()
                       if "rbcl.crypto_core_ed25519" in line or "crypto_scalarmult_ed25519" in line]
    assert offenders == [] or all("Ed25519" in (SRC / name).read_text() for name in offenders)
    assert ristretto_calls == []


def test_small_multiples_detect_scalar_clamping() -> None:
    """Condition 5: 1P = P, 2P = P+P, 3P = P+P+P, 8P = 2(4P); clamping would break these."""
    point = rs.hash_to_group(b"clamping", b"probe")
    assert rs.multiply(1, point) == point
    assert rs.multiply(2, point) == rs.add(point, point)
    assert rs.multiply(3, point) == rs.add(rs.add(point, point), point)
    assert rs.multiply(8, point) == rs.multiply(2, rs.multiply(4, point))
    assert rs.base_multiply(1) == rs.generator()


@pytest.mark.parametrize("trial", range(25))
def test_scalar_multiplication_is_linear_over_the_full_range(trial: int) -> None:
    """Condition 5: (a+b)P = aP + bP and (ab)P = a(bP) for random full-range scalars."""
    point = rs.hash_to_group(b"linearity", trial.to_bytes(4, "big"))
    a, b = _random_full_range_scalar(), _random_full_range_scalar()
    if (a + b) % rs.ORDER and (a * b) % rs.ORDER:
        assert rs.multiply(a + b, point) == rs.add(rs.multiply(a, point), rs.multiply(b, point))
        assert rs.multiply(a * b, point) == rs.multiply(a, rs.multiply(b, point))


def test_order_minus_one_is_negation() -> None:
    """(ORDER-1)P acts as -P: adding 2P to it gives P, and 2P - P = P."""
    point = rs.hash_to_group(b"order", b"probe")
    minus_point = rs.multiply(rs.ORDER - 1, point)
    assert rs.subtract(rs.multiply(2, point), point) == point
    assert rs.add(minus_point, rs.multiply(2, point)) == point


@pytest.mark.parametrize("trial", range(5))
def test_lagrange_reconstruction_in_the_exponent(trial: int) -> None:
    """Condition 5: any t partials x_i P combine to xP; t-1 partials do not."""
    n, t = 32, 22
    coefficients = [_random_full_range_scalar() for _ in range(t)]
    secret = coefficients[0]
    shares = {i: sum(c * pow(i, k, rs.ORDER) for k, c in enumerate(coefficients)) % rs.ORDER
              for i in range(1, n + 1)}
    point = rs.hash_to_group(b"lagrange", trial.to_bytes(4, "big"))
    partials = {i: rs.multiply(x_i, point) for i, x_i in shares.items()}
    chosen = sorted(secrets.SystemRandom().sample(range(1, n + 1), t))
    combined = None
    for i in chosen:
        term = rs.multiply(_lagrange_at_zero(i, chosen), partials[i])
        combined = term if combined is None else rs.add(combined, term)
    assert combined == rs.multiply(secret, point)

    short = chosen[:-1]
    partial_sum = None
    for i in short:
        term = rs.multiply(_lagrange_at_zero(i, short), partials[i])
        partial_sum = term if partial_sum is None else rs.add(partial_sum, term)
    assert partial_sum != rs.multiply(secret, point)


def test_hash_to_group_is_deterministic_and_domain_separated() -> None:
    first = rs.hash_to_group(b"canary", b"epoch-1", b"slot-7")
    assert first == rs.hash_to_group(b"canary", b"epoch-1", b"slot-7")
    assert first != rs.hash_to_group(b"dispute", b"epoch-1", b"slot-7")
    assert first != rs.hash_to_group(b"canary", b"epoch-1slot-7")
    rs.validate_point(first)
