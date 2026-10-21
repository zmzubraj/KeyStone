"""Prime-order group interface for R2, with ristretto255 and W11-fixed ffdhe instances.

DLEQ proofs, Shamir sharing, TDH2 and the canary audit are written against this
interface so the R2 microbenchmarks can run the same operations in every group
listed in ``r2-design-freeze.json``. Elements are opaque: bytes for ristretto255,
integers for ffdhe. ``encode`` gives the canonical byte form used in hashes.
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Any

from keystone.group import GroupParameters
from keystone_r2 import ffdhe
from keystone_r2 import ristretto as rs

Element = Any


class InvalidElement(ValueError):
    """Raised when a value is not a valid, non-identity element of the group."""


class RistrettoGroup:
    """ristretto255 via libsodium (keystone_r2.ristretto)."""

    name = "ristretto255"
    order = rs.ORDER

    def generator(self) -> bytes:
        return rs.generator()

    def validate(self, element: Element) -> Element:
        try:
            return rs.validate_point(element)
        except rs.InvalidPoint as exc:
            raise InvalidElement(str(exc)) from exc

    def mul(self, scalar: int, element: Element) -> Element:
        try:
            return rs.multiply(scalar, element)
        except rs.InvalidPoint as exc:
            raise InvalidElement(str(exc)) from exc

    def base_mul(self, scalar: int) -> Element:
        return rs.base_multiply(scalar)

    def add(self, first: Element, second: Element) -> Element:
        try:
            return rs.add(first, second)
        except rs.InvalidPoint as exc:
            raise InvalidElement(str(exc)) from exc

    def sub(self, first: Element, second: Element) -> Element:
        try:
            return rs.subtract(first, second)
        except rs.InvalidPoint as exc:
            raise InvalidElement(str(exc)) from exc

    def hash_to_group(self, domain: bytes, *parts: bytes) -> Element:
        return rs.hash_to_group(domain, *parts)

    def encode(self, element: Element) -> bytes:
        return element

    def random_scalar(self) -> int:
        return rs.random_scalar()


@dataclass(frozen=True)
class FfdheGroup:
    """Order-q subgroup of an RFC 7919 safe-prime group, with the W11 fixes."""

    params: GroupParameters
    name: str

    @property
    def order(self) -> int:
        return self.params.q

    def generator(self) -> int:
        return self.params.g

    def validate(self, element: Element) -> Element:
        if not isinstance(element, int) or element == 1 or not ffdhe.is_member(self.params, element):
            raise InvalidElement("not a non-identity element of the order-q subgroup")
        return element

    def mul(self, scalar: int, element: Element) -> Element:
        self.validate(element)
        reduced = scalar % self.params.q
        if reduced == 0:
            raise ValueError("scalar must be non-zero modulo the group order")
        return pow(element, reduced, self.params.p)

    def base_mul(self, scalar: int) -> Element:
        return self.mul(scalar, self.params.g)

    def add(self, first: Element, second: Element) -> Element:
        self.validate(first)
        self.validate(second)
        result = first * second % self.params.p
        return self.validate(result)

    def sub(self, first: Element, second: Element) -> Element:
        self.validate(first)
        self.validate(second)
        return self.validate(first * pow(second, -1, self.params.p) % self.params.p)

    def hash_to_group(self, domain: bytes, *parts: bytes) -> Element:
        return ffdhe.hash_to_group(self.params, domain, *parts)

    def encode(self, element: Element) -> bytes:
        return element.to_bytes((self.params.p.bit_length() + 7) // 8, "big")

    def random_scalar(self) -> int:
        return secrets.randbelow(self.params.q - 1) + 1


RISTRETTO = RistrettoGroup()
FFDHE2048 = FfdheGroup(ffdhe.GROUPS["ffdhe2048"], "ffdhe2048")
FFDHE3072 = FfdheGroup(ffdhe.GROUPS["ffdhe3072"], "ffdhe3072")
GROUPS = {g.name: g for g in (RISTRETTO, FFDHE2048, FFDHE3072)}
