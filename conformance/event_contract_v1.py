#!/usr/bin/env python3
"""Dependency-free conformance checks for Dubnium Event Contract v1alpha."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import re
from typing import Any

MAX_EVENT_BYTES = 16 * 1024
MAX_DATA_PROPERTIES = 32
MAX_COLLECTION_ITEMS = 128
MAX_DATA_DEPTH = 8
MAX_STRING_BYTES = 4096

ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SOURCE = re.compile(
    r"^urn:dubnium:[a-z0-9][a-z0-9._-]{0,63}"
    r"(?::[a-z0-9][a-z0-9._-]{0,63})*$"
)
EVENT_TYPE = re.compile(
    r"^org\.micrantha\.dubnium\.[a-z0-9]+(?:\.[a-z0-9]+)*\.v1$"
)
ATTRIBUTE_NAME = re.compile(r"^[a-z0-9]{1,20}$")
TRACEPARENT = re.compile(
    r"^(?P<version>[0-9a-f]{2})-"
    r"(?P<trace>[0-9a-f]{32})-"
    r"(?P<parent>[0-9a-f]{16})-"
    r"(?P<flags>[0-9a-f]{2})$"
)
SEVERITIES = {"debug", "info", "warning", "error", "critical"}
CORE_ATTRIBUTES = {
    "specversion",
    "id",
    "source",
    "type",
    "time",
    "subject",
    "datacontenttype",
    "dataschema",
    "data",
    "traceparent",
    "tracestate",
}
REQUIRED = {
    "specversion",
    "id",
    "source",
    "type",
    "time",
    "datacontenttype",
    "data",
}
SENSITIVE_EXACT = {
    "secret",
    "password",
    "credential",
    "credentials",
    "authorization",
    "authorization_header",
    "api_key",
    "apikey",
    "bearer",
    "prompt",
    "completion",
    "memory_content",
    "memory_body",
    "request_body",
    "capability_request_body",
    "workflow_payload",
    "environment",
    "env",
    "jit_config",
}
SENSITIVE_SUFFIXES = (
    "_secret",
    "_password",
    "_credential",
    "_credentials",
    "_api_key",
    "_apikey",
    "_authorization",
    "_bearer",
)


class ContractError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def fail(code: str, message: str) -> None:
    raise ContractError(code, message)


def _reject_nonfinite(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_nonfinite)


def _serialized_size(value: Any) -> int:
    return len(
        json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    )


def _sensitive_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return normalized in SENSITIVE_EXACT or normalized.endswith(SENSITIVE_SUFFIXES)


def _check_data_value(value: Any, *, depth: int, path: str) -> None:
    if depth > MAX_DATA_DEPTH:
        fail("data.depth", f"{path} exceeds maximum nesting depth {MAX_DATA_DEPTH}")

    if value is None or isinstance(value, bool):
        return

    if isinstance(value, int):
        if not -(2**53 - 1) <= value <= 2**53 - 1:
            fail("data.integer", f"{path} exceeds interoperable integer range")
        return

    if isinstance(value, float):
        if not math.isfinite(value):
            fail("data.number", f"{path} must be finite")
        return

    if isinstance(value, str):
        if len(value.encode("utf-8")) > MAX_STRING_BYTES:
            fail("data.string", f"{path} exceeds {MAX_STRING_BYTES} bytes")
        return

    if isinstance(value, list):
        if len(value) > MAX_COLLECTION_ITEMS:
            fail("data.collection", f"{path} exceeds {MAX_COLLECTION_ITEMS} items")
        for index, child in enumerate(value):
            _check_data_value(child, depth=depth + 1, path=f"{path}[{index}]")
        return

    if isinstance(value, dict):
        if len(value) > MAX_COLLECTION_ITEMS:
            fail("data.collection", f"{path} exceeds {MAX_COLLECTION_ITEMS} properties")
        for key, child in value.items():
            if not isinstance(key, str):
                fail("data.key", f"{path} contains a non-string key")
            if _sensitive_key(key):
                fail("data.sensitive_field", f"{path}.{key} is prohibited by the generic event profile")
            _check_data_value(child, depth=depth + 1, path=f"{path}.{key}")
        return

    fail("data.value", f"{path} uses unsupported JSON value type")


def _check_timestamp(value: str) -> None:
    if len(value) > 32 or not value.endswith("Z"):
        fail("time.format", "time must be a bounded UTC RFC3339 timestamp")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        fail("time.format", f"invalid RFC3339 timestamp: {exc}")


def _check_traceparent(value: str) -> None:
    match = TRACEPARENT.fullmatch(value)
    if not match:
        fail("traceparent.format", "traceparent must use the W3C four-field lowercase hex shape")
    if match.group("version") == "ff":
        fail("traceparent.version", "traceparent version ff is invalid")
    if match.group("trace") == "0" * 32:
        fail("traceparent.zero_trace_id", "traceparent trace ID must be non-zero")
    if match.group("parent") == "0" * 16:
        fail("traceparent.zero_parent_id", "traceparent parent ID must be non-zero")


def validate_event(event: Any) -> None:
    if not isinstance(event, dict):
        fail("event.type", "event root must be a JSON object")

    if _serialized_size(event) > MAX_EVENT_BYTES:
        fail("event.size", f"event exceeds {MAX_EVENT_BYTES} bytes")

    missing = sorted(REQUIRED - set(event))
    if missing:
        fail("required.missing", "missing required attributes: " + ", ".join(missing))

    for name in event:
        if not isinstance(name, str) or not ATTRIBUTE_NAME.fullmatch(name):
            fail("attribute.name", f"invalid CloudEvents attribute name: {name!r}")

    if event["specversion"] != "1.0":
        fail("specversion", "specversion must be 1.0")

    event_id = event["id"]
    if not isinstance(event_id, str) or not ID.fullmatch(event_id):
        fail("id.format", "id must use the bounded Dubnium identifier profile")

    source = event["source"]
    if not isinstance(source, str) or len(source) > 256 or not SOURCE.fullmatch(source):
        fail("source.format", "source must use urn:dubnium:<component>[:<subcomponent>]")

    event_type = event["type"]
    if (
        not isinstance(event_type, str)
        or len(event_type) > 192
        or not EVENT_TYPE.fullmatch(event_type)
    ):
        fail("type.format", "type must use org.micrantha.dubnium.<domain>.<event>.v1")

    timestamp = event["time"]
    if not isinstance(timestamp, str):
        fail("time.format", "time must be a string")
    _check_timestamp(timestamp)

    if event["datacontenttype"] != "application/json":
        fail("datacontenttype", "datacontenttype must be application/json")

    subject = event.get("subject")
    if subject is not None:
        if not isinstance(subject, str) or not subject or len(subject.encode("utf-8")) > 256:
            fail("subject.format", "subject must be a non-empty string no larger than 256 bytes")
        if any(ord(char) < 0x20 for char in subject):
            fail("subject.format", "subject must not contain control characters")

    traceparent = event.get("traceparent")
    if traceparent is not None:
        if not isinstance(traceparent, str):
            fail("traceparent.format", "traceparent must be a string")
        _check_traceparent(traceparent)

    tracestate = event.get("tracestate")
    if tracestate is not None:
        if traceparent is None:
            fail("tracestate.traceparent_required", "tracestate requires traceparent")
        if (
            not isinstance(tracestate, str)
            or not tracestate
            or len(tracestate.encode("utf-8")) > 512
            or any(ord(char) < 0x20 or ord(char) > 0x7E for char in tracestate)
        ):
            fail("tracestate.format", "tracestate must be bounded printable ASCII")

    dataschema = event.get("dataschema")
    if dataschema is not None and (
        not isinstance(dataschema, str)
        or not dataschema
        or len(dataschema.encode("utf-8")) > 256
    ):
        fail("dataschema.format", "dataschema must be a bounded URI string")

    data = event["data"]
    if not isinstance(data, dict):
        fail("data.type", "data must be an object")
    if len(data) > MAX_DATA_PROPERTIES:
        fail("data.properties", f"data exceeds {MAX_DATA_PROPERTIES} top-level properties")
    if data.get("severity") not in SEVERITIES:
        fail("data.severity", "data.severity is required and must use the public severity vocabulary")
    _check_data_value(data, depth=0, path="data")

    for name, value in event.items():
        if name in CORE_ATTRIBUTES:
            continue
        if not isinstance(value, (str, bool, int)) or isinstance(value, float):
            fail("extension.value", f"extension {name} must use a scalar CloudEvents-compatible value")


def run_fixtures(path: Path) -> None:
    document = load_json(path)
    if not isinstance(document, dict) or document.get("version") != 1:
        fail("fixtures.format", "fixture document must be version 1")
    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        fail("fixtures.format", "fixture document requires a non-empty cases array")

    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            fail("fixtures.format", "fixture case must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            fail("fixtures.format", "fixture IDs must be unique non-empty strings")
        seen.add(case_id)
        expected_valid = case.get("valid")
        if not isinstance(expected_valid, bool):
            fail("fixtures.format", f"{case_id}: valid must be boolean")
        event = case.get("event")

        try:
            validate_event(event)
        except ContractError as exc:
            if expected_valid:
                raise AssertionError(f"{case_id}: expected valid, got {exc.code}: {exc}") from exc
            expected_error = case.get("error")
            if expected_error is not None and expected_error != exc.code:
                raise AssertionError(
                    f"{case_id}: expected error {expected_error}, got {exc.code}"
                ) from exc
        else:
            if not expected_valid:
                raise AssertionError(f"{case_id}: expected invalid event")

    print(f"event contract fixtures passed: {len(cases)} cases")


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    fixtures = subparsers.add_parser("run-fixtures")
    fixtures.add_argument("path", type=Path)
    args = parser.parse_args()

    if args.command == "run-fixtures":
        run_fixtures(args.path)
        return 0
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
