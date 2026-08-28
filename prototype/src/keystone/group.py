from __future__ import annotations

from dataclasses import dataclass
import hashlib


@dataclass(frozen=True, slots=True)
class GroupParameters:
    """Prime-order subgroup parameters used by the research prototype."""

    p: int
    q: int
    g: int
    name: str

    @property
    def byte_length(self) -> int:
        return (self.p.bit_length() + 7) // 8

    def validate_element(self, value: int) -> bool:
        return 1 <= value < self.p and pow(value, self.q, self.p) == 1


# A generated 256-bit safe-prime group.  It is adequate for a reproducible
# prototype but is not a standardized production parameter set.
RESEARCH_GROUP = GroupParameters(
    p=67977824682176678430743654077364272814869187573184577570246490578933777033703,
    q=33988912341088339215371827038682136407434593786592288785123245289466888516851,
    g=4,
    name="keystone-safe-prime-256-v1",
)


def encode_int(value: int, length: int) -> bytes:
    if value < 0:
        raise ValueError("cannot encode a negative integer")
    return value.to_bytes(length, "big")


def hash_to_scalar(group: GroupParameters, domain: bytes, *values: int | bytes) -> int:
    digest = hashlib.sha256()
    digest.update(b"KEYSTONE-FS-v1")
    digest.update(len(domain).to_bytes(4, "big"))
    digest.update(domain)
    for value in values:
        if isinstance(value, int):
            encoded = encode_int(value, group.byte_length)
            digest.update(b"I")
        else:
            encoded = value
            digest.update(b"B")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
    return int.from_bytes(digest.digest(), "big") % group.q


def hash_to_group(group: GroupParameters, domain: bytes, *values: int | bytes) -> int:
    """Map public transcript bytes to a subgroup element without exposing its log.

    For the safe-prime research group, squaring a non-zero field element maps
    into the order-q quadratic-residue subgroup.  The resulting element is
    deterministic, while its discrete logarithm relative to ``g`` is not
    revealed by the mapping.  Production code should use a standardized
    hash-to-curve/hash-to-group suite.
    """

    counter = 0
    while True:
        digest = hashlib.sha256()
        digest.update(b"KEYSTONE-H2G-v1")
        digest.update(len(domain).to_bytes(4, "big"))
        digest.update(domain)
        for value in values:
            if isinstance(value, int):
                encoded = encode_int(value, group.byte_length)
                digest.update(b"I")
            else:
                encoded = value
                digest.update(b"B")
            digest.update(len(encoded).to_bytes(4, "big"))
            digest.update(encoded)
        digest.update(counter.to_bytes(4, "big"))
        candidate = 2 + (int.from_bytes(digest.digest(), "big") % (group.p - 3))
        element = pow(candidate, 2, group.p)
        if element != 1 and group.validate_element(element):
            return element
        counter += 1
