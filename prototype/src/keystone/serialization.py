from __future__ import annotations

from dataclasses import dataclass
import hashlib
import struct


MAGIC = b"KSTN"
PROTOCOL_VERSION = 1
AUDIT_REQUEST_KIND = 1
PARTIAL_RESPONSE_KIND = 2
TRANSCRIPT_HASH_DOMAIN = b"KEYSTONE-TRANSCRIPT-HASH-v1"


class _Reader:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.offset = 0

    def take(self, length: int, label: str) -> bytes:
        end = self.offset + length
        if length < 0 or end > len(self.payload):
            raise ValueError(f"truncated {label}")
        value = self.payload[self.offset:end]
        self.offset = end
        return value

    def uint16(self, label: str) -> int:
        return struct.unpack(">H", self.take(2, label))[0]

    def uint64(self, label: str) -> int:
        return struct.unpack(">Q", self.take(8, label))[0]

    def length_prefixed(self, label: str) -> bytes:
        return self.take(self.uint16(f"{label} length"), label)

    def finish(self) -> None:
        if self.offset != len(self.payload):
            raise ValueError("trailing bytes after canonical transcript")


def _header(kind: int) -> bytes:
    return MAGIC + bytes([PROTOCOL_VERSION, kind])


def _decode_header(reader: _Reader, expected_kind: int) -> None:
    if reader.take(4, "magic") != MAGIC:
        raise ValueError("invalid transcript magic")
    version = reader.take(1, "protocol version")[0]
    if version != PROTOCOL_VERSION:
        raise ValueError("unsupported protocol version")
    kind = reader.take(1, "message kind")[0]
    if kind != expected_kind:
        raise ValueError("unexpected message kind")


def _uint64(value: int, label: str) -> bytes:
    if not 0 <= value < 2**64:
        raise ValueError(f"{label} must fit uint64")
    return struct.pack(">Q", value)


def _uint16(value: int, label: str) -> bytes:
    if not 0 <= value < 2**16:
        raise ValueError(f"{label} must fit uint16")
    return struct.pack(">H", value)


def _fixed(value: bytes, length: int, label: str) -> bytes:
    if len(value) != length:
        raise ValueError(f"{label} must be {length} bytes")
    return value


def _length_prefixed(value: bytes, label: str) -> bytes:
    if not value or len(value) >= 2**16:
        raise ValueError(f"{label} length must satisfy 1 <= length < 65536")
    return _uint16(len(value), f"{label} length") + value


def _canonical_integer(value: bytes, label: str) -> bytes:
    if not value or (len(value) > 1 and value[0] == 0):
        raise ValueError(f"{label} must use canonical unsigned integer bytes")
    return _length_prefixed(value, label)


def _decode_integer(reader: _Reader, label: str) -> bytes:
    value = reader.length_prefixed(label)
    _canonical_integer(value, label)
    return value


def _epoch_bytes(epoch_id: str) -> bytes:
    try:
        encoded = epoch_id.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ValueError("epoch_id must be valid UTF-8") from error
    return _length_prefixed(encoded, "epoch_id")


def _decode_epoch(reader: _Reader) -> str:
    encoded = reader.length_prefixed("epoch_id")
    if not encoded:
        raise ValueError("epoch_id must not be empty")
    try:
        epoch_id = encoded.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("epoch_id must be valid UTF-8") from error
    if epoch_id.encode("utf-8") != encoded:
        raise ValueError("epoch_id must use canonical UTF-8")
    return epoch_id


def transcript_hash(encoded_transcript: bytes) -> bytes:
    if not encoded_transcript:
        raise ValueError("encoded transcript must not be empty")
    return hashlib.sha256(TRANSCRIPT_HASH_DOMAIN + encoded_transcript).digest()


@dataclass(frozen=True, slots=True)
class AuditRequestTranscript:
    chain_id: int
    contract_address: bytes
    epoch_id: str
    request_id: bytes
    audit_slot: int
    beacon_hash: bytes
    canary_element: bytes
    sampled_bitmap: bytes
    required_valid: int
    deadline_unix_ms: int

    def to_bytes(self) -> bytes:
        bitmap = _fixed(self.sampled_bitmap, 32, "sampled_bitmap")
        sampled_count = int.from_bytes(bitmap, "big").bit_count()
        if not 1 <= self.required_valid <= sampled_count:
            raise ValueError("required_valid must fit the non-empty sample")
        return b"".join(
            [
                _header(AUDIT_REQUEST_KIND),
                _uint64(self.chain_id, "chain_id"),
                _fixed(self.contract_address, 20, "contract_address"),
                _epoch_bytes(self.epoch_id),
                _fixed(self.request_id, 32, "request_id"),
                _uint64(self.audit_slot, "audit_slot"),
                _fixed(self.beacon_hash, 32, "beacon_hash"),
                _canonical_integer(self.canary_element, "canary_element"),
                bitmap,
                _uint16(self.required_valid, "required_valid"),
                _uint64(self.deadline_unix_ms, "deadline_unix_ms"),
            ]
        )

    @classmethod
    def from_bytes(cls, payload: bytes) -> AuditRequestTranscript:
        reader = _Reader(payload)
        _decode_header(reader, AUDIT_REQUEST_KIND)
        request = cls(
            chain_id=reader.uint64("chain_id"),
            contract_address=reader.take(20, "contract_address"),
            epoch_id=_decode_epoch(reader),
            request_id=reader.take(32, "request_id"),
            audit_slot=reader.uint64("audit_slot"),
            beacon_hash=reader.take(32, "beacon_hash"),
            canary_element=_decode_integer(reader, "canary_element"),
            sampled_bitmap=reader.take(32, "sampled_bitmap"),
            required_valid=reader.uint16("required_valid"),
            deadline_unix_ms=reader.uint64("deadline_unix_ms"),
        )
        reader.finish()
        if request.to_bytes() != payload:
            raise ValueError("noncanonical audit request transcript")
        return request


@dataclass(frozen=True, slots=True)
class PartialResponseTranscript:
    chain_id: int
    contract_address: bytes
    epoch_id: str
    request_id: bytes
    request_hash: bytes
    member_index: int
    partial_element: bytes
    proof_a1: bytes
    proof_a2: bytes
    proof_z: bytes
    response_unix_ms: int

    def to_bytes(self) -> bytes:
        if self.member_index == 0:
            raise ValueError("member_index is one-based")
        return b"".join(
            [
                _header(PARTIAL_RESPONSE_KIND),
                _uint64(self.chain_id, "chain_id"),
                _fixed(self.contract_address, 20, "contract_address"),
                _epoch_bytes(self.epoch_id),
                _fixed(self.request_id, 32, "request_id"),
                _fixed(self.request_hash, 32, "request_hash"),
                _uint16(self.member_index, "member_index"),
                _canonical_integer(self.partial_element, "partial_element"),
                _canonical_integer(self.proof_a1, "proof_a1"),
                _canonical_integer(self.proof_a2, "proof_a2"),
                _canonical_integer(self.proof_z, "proof_z"),
                _uint64(self.response_unix_ms, "response_unix_ms"),
            ]
        )

    @classmethod
    def from_bytes(cls, payload: bytes) -> PartialResponseTranscript:
        reader = _Reader(payload)
        _decode_header(reader, PARTIAL_RESPONSE_KIND)
        response = cls(
            chain_id=reader.uint64("chain_id"),
            contract_address=reader.take(20, "contract_address"),
            epoch_id=_decode_epoch(reader),
            request_id=reader.take(32, "request_id"),
            request_hash=reader.take(32, "request_hash"),
            member_index=reader.uint16("member_index"),
            partial_element=_decode_integer(reader, "partial_element"),
            proof_a1=_decode_integer(reader, "proof_a1"),
            proof_a2=_decode_integer(reader, "proof_a2"),
            proof_z=_decode_integer(reader, "proof_z"),
            response_unix_ms=reader.uint64("response_unix_ms"),
        )
        reader.finish()
        if response.to_bytes() != payload:
            raise ValueError("noncanonical partial response transcript")
        return response
