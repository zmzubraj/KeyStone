from __future__ import annotations

from collections.abc import Callable, Iterable
import secrets

from .group import GroupParameters

RandBelow = Callable[[int], int]


def _validate_parameters(n: int, threshold: int, modulus: int) -> None:
    if not 1 <= threshold <= n:
        raise ValueError("threshold must satisfy 1 <= threshold <= n")
    if modulus <= n:
        raise ValueError("modulus must exceed the participant indices")


def share_secret(
    secret: int,
    n: int,
    threshold: int,
    modulus: int,
    randbelow: RandBelow = secrets.randbelow,
) -> tuple[list[int], dict[int, int]]:
    """Create Shamir shares indexed from 1 through n."""

    _validate_parameters(n, threshold, modulus)
    secret %= modulus
    coefficients = [secret]
    coefficients.extend(randbelow(modulus) % modulus for _ in range(threshold - 1))
    shares = {index: evaluate_polynomial(coefficients, index, modulus) for index in range(1, n + 1)}
    return coefficients, shares


def evaluate_polynomial(coefficients: Iterable[int], x: int, modulus: int) -> int:
    value = 0
    for coefficient in reversed(list(coefficients)):
        value = (value * x + coefficient) % modulus
    return value


def lagrange_coefficient_at_zero(index: int, indices: Iterable[int], modulus: int) -> int:
    index_list = list(indices)
    if index not in index_list:
        raise ValueError("index must be included in indices")
    if len(set(index_list)) != len(index_list):
        raise ValueError("indices must be unique")

    numerator = 1
    denominator = 1
    for other in index_list:
        if other == index:
            continue
        numerator = (numerator * (-other % modulus)) % modulus
        denominator = (denominator * ((index - other) % modulus)) % modulus
    return (numerator * pow(denominator, -1, modulus)) % modulus


def interpolate_at_zero(shares: Iterable[tuple[int, int]], modulus: int) -> int:
    points = list(shares)
    if not points:
        raise ValueError("at least one share is required")
    indices = [index for index, _ in points]
    if len(set(indices)) != len(indices):
        raise ValueError("share indices must be unique")
    result = 0
    for index, value in points:
        coefficient = lagrange_coefficient_at_zero(index, indices, modulus)
        result = (result + value * coefficient) % modulus
    return result


def feldman_commitments(coefficients: Iterable[int], group: GroupParameters) -> tuple[int, ...]:
    return tuple(pow(group.g, coefficient % group.q, group.p) for coefficient in coefficients)


def verify_share(
    index: int,
    share: int,
    commitments: Iterable[int],
    group: GroupParameters,
) -> bool:
    commitment_list = tuple(commitments)
    if index <= 0 or not commitment_list:
        return False
    left = pow(group.g, share % group.q, group.p)
    right = 1
    index_power = 1
    for commitment in commitment_list:
        if not group.validate_element(commitment):
            return False
        right = (right * pow(commitment, index_power, group.p)) % group.p
        index_power = (index_power * index) % group.q
    return left == right
