"""W11-fixed hash-to-group and membership test for the retained ffdhe groups (R2).

R1's ``keystone.group.hash_to_group`` squares a candidate taken from a single
SHA-256 digest, so every ffdhe canary was the square of an integer below about
2^256: a tiny, structured subset of the group rather than a near-uniform element.
This module (used only by R2; R1 code is unchanged) instead:

* expands the input with ``expand_message_xmd`` (RFC 9380, Section 5.3.1, SHA-256)
  to ``ceil((bitlen(p) + 128) / 8)`` bytes, reduces mod ``p`` (statistical distance
  from uniform below 2^-128) and squares into the quadratic-residue subgroup of
  order ``q = (p - 1) / 2``;
* tests subgroup membership with the Jacobi symbol, which for a safe prime ``p``
  is equivalent to ``x^q mod p == 1`` but far cheaper.
"""
from __future__ import annotations

import hashlib

from keystone.group import GroupParameters
from keystone.standard_groups import FFDHE2048, FFDHE3072

GROUPS: dict[str, GroupParameters] = {"ffdhe2048": FFDHE2048, "ffdhe3072": FFDHE3072}
_DST = b"KEYSTONE-R2-FFDHE-H2G-XMD:SHA-256-v1"


def expand_message_xmd(msg: bytes, dst: bytes, len_in_bytes: int) -> bytes:
    """RFC 9380 expand_message_xmd with SHA-256 (b_in_bytes = 32, s_in_bytes = 64)."""
    b_in_bytes, s_in_bytes = 32, 64
    ell = -(-len_in_bytes // b_in_bytes)
    if ell > 255 or len_in_bytes > 65535 or len(dst) > 255:
        raise ValueError("expand_message_xmd parameters out of range")
    dst_prime = dst + len(dst).to_bytes(1, "big")
    msg_prime = bytes(s_in_bytes) + msg + len_in_bytes.to_bytes(2, "big") + b"\x00" + dst_prime
    b_0 = hashlib.sha256(msg_prime).digest()
    b_vals = [hashlib.sha256(b_0 + b"\x01" + dst_prime).digest()]
    for i in range(2, ell + 1):
        mixed = bytes(x ^ y for x, y in zip(b_0, b_vals[-1]))
        b_vals.append(hashlib.sha256(mixed + i.to_bytes(1, "big") + dst_prime).digest())
    return b"".join(b_vals)[:len_in_bytes]


def jacobi(a: int, n: int) -> int:
    """Jacobi symbol (a/n) for odd positive n."""
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be odd and positive")
    a %= n
    result = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a %= n
    return result if n == 1 else 0


def is_member(group: GroupParameters, value: int) -> bool:
    """Order-q subgroup membership for a safe-prime group, via the Jacobi symbol."""
    return 1 <= value < group.p and jacobi(value, group.p) == 1


def hash_to_group(group: GroupParameters, domain: bytes, *parts: bytes) -> int:
    """Map domain-separated, length-prefixed inputs to a near-uniform non-identity subgroup element."""
    msg = b"".join(len(p).to_bytes(4, "big") + p for p in (domain, *parts))
    length = -(-(group.p.bit_length() + 128) // 8)
    counter = 0
    while True:
        wide = expand_message_xmd(msg + counter.to_bytes(4, "big"), _DST, length)
        candidate = int.from_bytes(wide, "big") % group.p
        element = pow(candidate, 2, group.p)
        if candidate not in (0, 1, group.p - 1) and element != 1:
            return element
        counter += 1
