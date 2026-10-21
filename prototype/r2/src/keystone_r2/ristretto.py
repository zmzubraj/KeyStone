"""ristretto255 group operations for the R2 KEYSTONE core (via rbcl / libsodium).

This module is the only place that touches ``rbcl``. It applies the usage
conditions of ``research-case/03-design/r2-design-amendment/D1-SUPPLY-CHAIN-REVIEW.md``:

* every point received from outside is validated here with
  ``crypto_core_ristretto255_is_valid_point``; rbcl's own checks are stripped
  in a normal installation and are not relied on (condition 3);
* only ristretto255, scalar and ``randombytes`` functions are used, never the
  ed25519 API (condition 4);
* the libsodium binary embedded in rbcl is pinned by SHA-256 (condition 2);
* the temporary copy of that binary which rbcl writes at import is deleted
  once it has been loaded (condition 6).

Scalars are Python integers modulo the group order ``ORDER``; points are the
32-byte canonical ristretto255 encodings.
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
from pathlib import Path

import rbcl

# rbcl rebinds the attribute ``rbcl._sodium`` to the loaded ctypes library, so the
# loader module (which holds ``lib_path`` and the embedded binary) is taken from
# ``sys.modules`` and its source file from the package directory.
_RBCL_LOADER = sys.modules["rbcl._sodium"]
_RBCL_LOADER_SOURCE = Path(rbcl.__file__).resolve().parent / "_sodium.py"

ORDER = 2**252 + 27742317777372353535851937790883648493
POINT_BYTES = 32
SCALAR_BYTES = 32
EMBEDDED_LIBSODIUM_SHA256 = "87e460d62a4b1291058f3b97c72fd9d4ead1492023a4237cd5fe68ae8ef7a21b"
IDENTITY_ENCODING = bytes(POINT_BYTES)
_HASH_DOMAIN = b"KEYSTONE-R2-H2G-v1"


def _remove_rbcl_temp_library() -> None:
    """Delete the temporary libsodium copy rbcl wrote at import (already mapped)."""
    lib_path = getattr(_RBCL_LOADER, "lib_path", None)
    if lib_path and os.path.exists(lib_path):
        os.remove(lib_path)


_remove_rbcl_temp_library()


class InvalidPoint(ValueError):
    """Raised when bytes do not encode a valid, non-identity ristretto255 point."""


def embedded_library_sha256() -> str:
    """Return the SHA-256 of the libsodium binary embedded in the installed rbcl."""
    source = _RBCL_LOADER_SOURCE.read_text()
    match = re.search(r"bytes\.fromhex\('([0-9a-f]+)'\)", source)
    if match is None:
        raise RuntimeError("embedded libsodium binary not found in rbcl")
    return hashlib.sha256(bytes.fromhex(match.group(1))).hexdigest()


def validate_point(point: bytes) -> bytes:
    """Return ``point`` if it is a valid, non-identity ristretto255 encoding."""
    if not isinstance(point, bytes) or len(point) != POINT_BYTES:
        raise InvalidPoint("point must be 32 bytes")
    if point == IDENTITY_ENCODING:
        # libsodium accepts the canonical identity encoding as valid; KEYSTONE never does.
        raise InvalidPoint("the identity element is not accepted")
    if not rbcl.crypto_core_ristretto255_is_valid_point(point):
        raise InvalidPoint("bytes do not encode a valid non-identity ristretto255 point")
    return point


def scalar_to_bytes(scalar: int) -> bytes:
    """Encode an integer as a canonical little-endian scalar modulo ORDER."""
    return (scalar % ORDER).to_bytes(SCALAR_BYTES, "little")


def scalar_from_bytes(data: bytes) -> int:
    """Decode a 32-byte little-endian scalar and reduce it modulo ORDER."""
    return int.from_bytes(data, "little") % ORDER


def random_scalar() -> int:
    """Return a uniformly random non-zero scalar."""
    while True:
        value = scalar_from_bytes(rbcl.crypto_core_ristretto255_scalar_random())
        if value:
            return value


def generator() -> bytes:
    """Return the canonical ristretto255 base point."""
    return rbcl.crypto_scalarmult_ristretto255_base(scalar_to_bytes(1))


def multiply(scalar: int, point: bytes) -> bytes:
    """Return ``scalar * point`` for a validated point and a non-zero scalar mod ORDER."""
    validate_point(point)
    reduced = scalar % ORDER
    if reduced == 0:
        raise ValueError("scalar must be non-zero modulo the group order")
    return rbcl.crypto_scalarmult_ristretto255(scalar_to_bytes(reduced), point)


def base_multiply(scalar: int) -> bytes:
    """Return ``scalar * G`` for a non-zero scalar mod ORDER."""
    reduced = scalar % ORDER
    if reduced == 0:
        raise ValueError("scalar must be non-zero modulo the group order")
    return rbcl.crypto_scalarmult_ristretto255_base(scalar_to_bytes(reduced))


def add(first: bytes, second: bytes) -> bytes:
    """Return the group sum of two validated points."""
    return rbcl.crypto_core_ristretto255_add(validate_point(first), validate_point(second))


def subtract(first: bytes, second: bytes) -> bytes:
    """Return ``first - second`` for two validated points."""
    return rbcl.crypto_core_ristretto255_sub(validate_point(first), validate_point(second))


def hash_to_group(domain: bytes, *parts: bytes) -> bytes:
    """Map domain-separated, length-prefixed inputs to a point via SHA-512 and ``from_hash``.

    ``crypto_core_ristretto255_from_hash`` maps 64 uniform bytes to a group element
    (RFC 9496 one-way map), which matches the random-oracle model of the paper.
    """
    digest = hashlib.sha512()
    for item in (_HASH_DOMAIN, domain, *parts):
        digest.update(len(item).to_bytes(4, "big"))
        digest.update(item)
    return validate_point(rbcl.crypto_core_ristretto255_from_hash(digest.digest()))
