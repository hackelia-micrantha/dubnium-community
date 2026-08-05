"""Shared Capability Gateway v1alpha validation primitives."""

from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any

from .jcs_v1 import ContractError, _reject_surrogates

REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
REFERENCE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")
CAPABILITY_NAME = re.compile(r"^[a-z][a-z0-9]*(?:\.[a-z][a-z0-9-]*)+$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _expect_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError("contract.type", f"{name} must be an object")
    return value


def _expect_fields(value: dict[str, Any], allowed: set[str], name: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ContractError("contract.unknown_field", f"{name} contains unknown fields: {', '.join(unknown)}")


def _require(value: dict[str, Any], field: str, name: str) -> Any:
    if field not in value:
        raise ContractError("contract.missing_field", f"{name} is missing required field: {field}")
    return value[field]


def _expect_string(value: Any, name: str, *, max_length: int = 512) -> str:
    if not isinstance(value, str) or not value or len(value) > max_length:
        raise ContractError("contract.string", f"{name} must be a non-empty string up to {max_length} characters")
    _reject_surrogates(value)
    return value


def _expect_reference(value: Any, name: str) -> str:
    text = _expect_string(value, name, max_length=256)
    if not REFERENCE.fullmatch(text):
        raise ContractError("contract.reference", f"{name} must be a stable reference")
    return text


def _expect_digest(value: Any, name: str) -> str:
    text = _expect_string(value, name, max_length=71)
    if not DIGEST.fullmatch(text):
        raise ContractError("contract.digest", f"{name} must be a lowercase sha256 digest")
    return text


def _expect_timestamp(value: Any, name: str) -> str:
    text = _expect_string(value, name, max_length=20)
    if not UTC_TIMESTAMP.fullmatch(text):
        raise ContractError("contract.timestamp", f"{name} must use YYYY-MM-DDTHH:MM:SSZ")
    try:
        datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as caught:
        raise ContractError("contract.timestamp", f"{name} is not a valid UTC timestamp") from caught
    return text


def parse_timestamp(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _expect_reference_list(value: Any, name: str, *, max_items: int = 16) -> list[str]:
    if not isinstance(value, list) or len(value) > max_items:
        raise ContractError("contract.reference_list", f"{name} must be an array with at most {max_items} items")
    refs = [_expect_reference(item, f"{name}[{index}]") for index, item in enumerate(value)]
    if len(refs) != len(set(refs)):
        raise ContractError("contract.duplicate_reference", f"{name} contains duplicate references")
    return refs
