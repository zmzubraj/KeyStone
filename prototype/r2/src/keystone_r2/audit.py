"""Canary readiness audit over any R2 group.

An audit for (epoch, slot) uses a beacon value fixed after the audit was
committed. From it, everyone derives

* the canary ``X = H_G("KEYSTONE-CANARY", epoch, slot, beacon)``, which is never a
  production KEM component (paper, Lemma 3); and
* a uniform sample of ``s`` distinct custodians, drawn with a cryptographic sampler
  (SHA-256 counter stream with rejection sampling), as Assumption 2 of the paper
  recommends for production.

A sampled custodian answers with ``D_i = x_i * X`` and a DLEQ proof against its
public share. The audit accepts if at least ``q`` distinct sampled custodians
return valid responses.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from keystone_r2 import dleq, sharing
from keystone_r2.groups import RISTRETTO, Element


@dataclass(frozen=True)
class AuditResponse:
    """Custodian ``index`` returns ``value = x_i * X`` with a DLEQ proof."""

    index: int
    value: Element
    proof: dleq.DLEQProof


def _context(epoch: str, slot: int, beacon: bytes) -> bytes:
    parts = [epoch.encode(), slot.to_bytes(8, "big"), beacon]
    return b"KEYSTONE-R2-AUDIT-v1" + b"".join(len(p).to_bytes(4, "big") + p for p in parts)


def derive_canary(epoch: str, slot: int, beacon: bytes, group=RISTRETTO) -> Element:
    """Hash the public audit context to the canary element."""
    return group.hash_to_group(b"KEYSTONE-CANARY", _context(epoch, slot, beacon))


def sample(n: int, s: int, epoch: str, slot: int, beacon: bytes) -> list[int]:
    """Uniform sample of ``s`` distinct custodian indices in 1..n (Fisher--Yates, rejection sampling)."""
    if not 0 <= s <= n:
        raise ValueError("require 0 <= s <= n")
    seed = hashlib.sha256(b"KEYSTONE-R2-SAMPLE-v1" + _context(epoch, slot, beacon)).digest()
    counter = 0

    def uniform_below(bound: int) -> int:
        nonlocal counter
        limit = (1 << 64) - ((1 << 64) % bound)
        while True:
            block = hashlib.sha256(seed + counter.to_bytes(8, "big")).digest()
            counter += 1
            value = int.from_bytes(block[:8], "big")
            if value < limit:
                return value % bound

    pool = list(range(1, n + 1))
    for i in range(s):
        j = i + uniform_below(n - i)
        pool[i], pool[j] = pool[j], pool[i]
    return pool[:s]


def respond(committee: sharing.Committee, index: int, canary: Element, epoch: str, slot: int,
            beacon: bytes) -> AuditResponse:
    """Custodian ``index`` applies its share to the canary and proves it."""
    group = committee.group
    x_i = committee.shares[index]
    value = group.mul(x_i, canary)
    context = _context(epoch, slot, beacon) + index.to_bytes(4, "big")
    proof = dleq.prove(x_i, group.generator(), committee.public_shares[index], canary, value, context, group)
    return AuditResponse(index, value, proof)


def response_is_valid(committee: sharing.Committee, canary: Element, response: AuditResponse, epoch: str,
                      slot: int, beacon: bytes) -> bool:
    """Verify one audit response against the custodian's registered public share."""
    public_share = committee.public_shares.get(response.index)
    if public_share is None:
        return False
    context = _context(epoch, slot, beacon) + response.index.to_bytes(4, "big")
    return dleq.verify(response.proof, committee.group.generator(), public_share, canary, response.value,
                       context, committee.group)


def accepts(committee: sharing.Committee, epoch: str, slot: int, beacon: bytes, s: int, q: int,
            responses: list[AuditResponse]) -> bool:
    """Accept iff at least ``q`` distinct sampled custodians returned valid responses."""
    canary = derive_canary(epoch, slot, beacon, committee.group)
    sampled = set(sample(committee.n, s, epoch, slot, beacon))
    valid: set[int] = set()
    for response in responses:
        if response.index in sampled and response.index not in valid and \
                response_is_valid(committee, canary, response, epoch, slot, beacon):
            valid.add(response.index)
    return len(valid) >= q
