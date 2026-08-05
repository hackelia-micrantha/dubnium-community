"""RFC 8785 JCS and strict JSON parsing for Capability Gateway v1alpha."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

MAX_REQUEST_BYTES = 65_536
MAX_DEPTH = 32
MAX_COLLECTION_ITEMS = 1_024
MAX_SAFE_INTEGER = 9_007_199_254_740_991
REQUEST_DIGEST_DOMAIN = b"dubnium.capability-request.v1\x00"
PAYLOAD_DIGEST_DOMAIN = b"dubnium.capability-payload.v1\x00"


class ContractError(ValueError):
    def __init__(self, code: str, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable

    def envelope(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message[:512],
            "retryable": self.retryable,
        }


class _DuplicateKey(ValueError):
    pass


def _pairs_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _reject_number(value: str) -> None:
    raise ContractError("json.float_prohibited", f"floating-point JSON number is prohibited: {value}")


def _parse_integer(value: str) -> int:
    parsed = int(value, 10)
    if abs(parsed) > MAX_SAFE_INTEGER:
        raise ContractError("json.integer_out_of_range", "integer exceeds the interoperable 53-bit range")
    return parsed


def _reject_surrogates(value: str) -> None:
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise ContractError("json.invalid_unicode", "lone UTF-16 surrogate code points are prohibited")


def parse_json_bytes(data: bytes, *, max_bytes: int = MAX_REQUEST_BYTES) -> Any:
    if len(data) > max_bytes:
        raise ContractError("input.too_large", f"input exceeds {max_bytes} bytes")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as caught:
        raise ContractError("json.invalid_utf8", "input must be valid UTF-8") from caught
    if text.startswith("\ufeff"):
        raise ContractError("json.bom_prohibited", "UTF-8 byte-order marks are prohibited")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs_without_duplicates,
            parse_constant=_reject_number,
            parse_float=_reject_number,
            parse_int=_parse_integer,
        )
    except _DuplicateKey as caught:
        raise ContractError("json.duplicate_key", f"duplicate JSON object key: {caught}") from caught
    except ContractError:
        raise
    except json.JSONDecodeError as caught:
        raise ContractError("json.invalid", f"invalid JSON at line {caught.lineno}, column {caught.colno}") from caught
    return normalize_json(value)


def load_json(path: Path, *, max_bytes: int = MAX_REQUEST_BYTES) -> Any:
    try:
        return parse_json_bytes(path.read_bytes(), max_bytes=max_bytes)
    except OSError as caught:
        raise ContractError("input.unreadable", f"cannot read input: {caught}") from caught


def normalize_json(value: Any, *, depth: int = 0) -> Any:
    """Validate the v1 I-JSON subset without altering caller strings or keys."""

    if depth > MAX_DEPTH:
        raise ContractError("json.too_deep", f"JSON nesting exceeds {MAX_DEPTH}")
    if value is None:
        raise ContractError("json.null_prohibited", "null is prohibited; omit optional fields instead")
    if isinstance(value, str):
        _reject_surrogates(value)
        return value
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if abs(value) > MAX_SAFE_INTEGER:
            raise ContractError("json.integer_out_of_range", "integer exceeds the interoperable 53-bit range")
        return value
    if isinstance(value, float):
        raise ContractError("json.float_prohibited", "floating-point numbers are prohibited in v1")
    if isinstance(value, list):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise ContractError("json.collection_too_large", "array exceeds the item limit")
        return [normalize_json(item, depth=depth + 1) for item in value]
    if isinstance(value, dict):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise ContractError("json.collection_too_large", "object exceeds the entry limit")
        result: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ContractError("json.invalid_key", "object keys must be strings")
            _reject_surrogates(key)
            result[key] = normalize_json(item, depth=depth + 1)
        return result
    raise ContractError("json.unsupported_type", f"unsupported JSON value: {type(value).__name__}")


def _utf16_sort_key(value: str) -> tuple[int, ...]:
    encoded = value.encode("utf-16-be")
    return tuple(int.from_bytes(encoded[index:index + 2], "big") for index in range(0, len(encoded), 2))


def _serialize(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "[" + ",".join(_serialize(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(
            json.dumps(key, ensure_ascii=False, separators=(",", ":")) + ":" + _serialize(value[key])
            for key in sorted(value, key=_utf16_sort_key)
        ) + "}"
    raise ContractError("json.unsupported_type", f"unsupported JSON value: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    return _serialize(normalize_json(value)).encode("utf-8")


def digest_value(value: Any, *, domain: bytes = REQUEST_DIGEST_DOMAIN) -> str:
    return "sha256:" + hashlib.sha256(domain + canonical_json_bytes(value)).hexdigest()


def payload_digest(value: Any) -> str:
    return digest_value(value, domain=PAYLOAD_DIGEST_DOMAIN)
