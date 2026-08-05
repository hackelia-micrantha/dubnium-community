#!/usr/bin/env python3
"""Run the bundled Capability Gateway v1 conformance vectors."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference.capability_gateway_v1 import (  # noqa: E402
    ContractViolation,
    InMemoryGateway,
    canonical_bytes,
    execute_echo,
    parse_json_bytes,
    request_digest,
    validate_manifest,
    validate_request,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
POSITIVE = FIXTURES / "positive"
NEGATIVE = FIXTURES / "negative"
SYNTHETIC = FIXTURES / "synthetic"
NOW = "2026-08-05T20:00:02Z"


class ConformanceFailure(AssertionError):
    pass


def load_strict(path: Path):
    return parse_json_bytes(path.read_bytes())


def expect_violation(code: str, operation: Callable[[], object], label: str) -> None:
    try:
        operation()
    except ContractViolation as exc:
        if exc.code != code:
            raise ConformanceFailure(
                f"{label}: expected {code}, received {exc.code}: {exc.detail}"
            ) from exc
        return
    raise ConformanceFailure(f"{label}: expected {code}, operation succeeded")


def positive_vectors() -> list[str]:
    checks: list[str] = []
    request_path = POSITIVE / "echo-request.json"
    request = load_strict(request_path)
    validate_request(request)
    checks.append("positive.request")

    actual_canonical = canonical_bytes(request)
    expected_canonical = (POSITIVE / "echo-request.canonical.json").read_bytes()
    if actual_canonical != expected_canonical:
        raise ConformanceFailure("positive.canonical: canonical bytes differ")
    checks.append("positive.canonical")

    actual_digest = request_digest(request)
    expected_digest = (POSITIVE / "echo-request.digest.txt").read_text(
        encoding="utf-8"
    ).strip()
    if actual_digest != expected_digest:
        raise ConformanceFailure(
            f"positive.digest: expected {expected_digest}, received {actual_digest}"
        )
    checks.append("positive.digest")

    manifest = load_strict(POSITIVE / "echo-manifest.json")
    validate_manifest(manifest, now=NOW)
    checks.append("positive.manifest")

    actual_result = execute_echo(manifest, now=NOW)
    expected_result = load_strict(POSITIVE / "echo-result.json")
    if actual_result != expected_result:
        raise ConformanceFailure("positive.result: echo result differs")
    checks.append("positive.result")

    gateway = InMemoryGateway(actor_ref="urn:dubnium:actor:synthetic-loopback")
    first_submission, first_status = gateway.submit_and_execute(
        request_path.read_bytes(), now=NOW
    )
    second_submission, second_status = gateway.submit_and_execute(
        request_path.read_bytes(), now=NOW
    )
    if first_submission != second_submission or first_status != second_status:
        raise ConformanceFailure("positive.idempotency: identical retry changed state")
    if gateway.dispatch_count(request["request_id"]) != 1:
        raise ConformanceFailure("positive.idempotency: request dispatched more than once")
    if first_status["result"] != expected_result:
        raise ConformanceFailure("positive.gateway: stored result differs")
    checks.extend(["positive.idempotency", "positive.gateway"])
    return checks


def negative_vectors() -> list[str]:
    checks: list[str] = []
    request_cases = {
        "unknown-field.json": "schema_validation_failed",
        "actor-spoof.json": "schema_validation_failed",
        "duplicate-key.json": "duplicate_key",
        "malformed-request-id.json": "schema_validation_failed",
        "malformed-timestamp.json": "invalid_timestamp",
        "lone-surrogate.json": "schema_validation_failed",
    }
    for filename, expected_code in request_cases.items():
        path = NEGATIVE / filename

        def operation(path: Path = path) -> None:
            validate_request(parse_json_bytes(path.read_bytes()))

        expect_violation(expected_code, operation, f"negative.{filename}")
        checks.append(f"negative.{filename}")

    oversized = json.loads(
        (NEGATIVE / "oversized-body.json").read_text(encoding="utf-8")
    )
    oversized_body = bytes.fromhex(oversized["repeat_byte"]) * oversized["count"]
    expect_violation(
        oversized["expected_code"],
        lambda: parse_json_bytes(oversized_body),
        "negative.oversized-body",
    )
    checks.append("negative.oversized-body")

    conflict = json.loads(
        (NEGATIVE / "conflicting-request-id.json").read_text(encoding="utf-8")
    )
    gateway = InMemoryGateway(actor_ref="urn:dubnium:actor:synthetic-loopback")
    gateway.submit_and_execute(
        json.dumps(conflict["first"], separators=(",", ":")).encode("utf-8"),
        now=NOW,
    )
    expect_violation(
        conflict["expected_code"],
        lambda: gateway.submit_and_execute(
            json.dumps(conflict["second"], separators=(",", ":")).encode("utf-8"),
            now=NOW,
        ),
        "negative.conflicting-request-id",
    )
    if gateway.dispatch_count(conflict["first"]["request_id"]) != 1:
        raise ConformanceFailure(
            "negative.conflicting-request-id: conflict caused duplicate dispatch"
        )
    checks.append("negative.conflicting-request-id")

    manifest_cases = {
        "digest-mismatch-manifest.json": "manifest_invalid",
        "expired-manifest.json": "manifest_expired",
        "constraint-widening-manifest.json": "manifest_widening",
    }
    for filename, expected_code in manifest_cases.items():
        manifest = load_strict(NEGATIVE / filename)
        expect_violation(
            expected_code,
            lambda manifest=manifest: validate_manifest(manifest, now=NOW),
            f"negative.{filename}",
        )
        checks.append(f"negative.{filename}")
    return checks


def synthetic_vectors() -> list[str]:
    request = load_strict(SYNTHETIC / "deployment-apply-request.json")
    validate_request(request)
    if request["capability"]["name"] != "deployment.apply":
        raise ConformanceFailure("synthetic.deployment: effect name drifted")
    if request["capability"]["name"] == "deployment.request":
        raise ConformanceFailure("synthetic.deployment: submission verb used as effect")
    request_digest(request)
    return ["synthetic.deployment-apply"]


def main() -> int:
    try:
        checks = positive_vectors() + negative_vectors() + synthetic_vectors()
    except (ConformanceFailure, ContractViolation, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Capability Gateway v1 conformance failed: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "contract": "dubnium.capability-gateway.v1",
                "status": "passed",
                "checks": checks,
                "check_count": len(checks),
                "remote_target": False,
                "effects": "example.echo only",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
