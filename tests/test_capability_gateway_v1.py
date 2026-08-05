from __future__ import annotations

import copy
import json
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference.capability_gateway_v1 import (  # noqa: E402
    ContractViolation,
    InMemoryGateway,
    build_manifest,
    canonical_bytes,
    execute_echo,
    parse_json_bytes,
    problem,
    request_digest,
    validate_manifest,
    validate_request,
)

FIXTURES = ROOT / "conformance" / "capability-gateway" / "v1" / "fixtures"
POSITIVE = FIXTURES / "positive"
NEGATIVE = FIXTURES / "negative"
SYNTHETIC = FIXTURES / "synthetic"
NOW = "2026-08-05T20:00:02Z"


def load_strict(path: Path):
    return parse_json_bytes(path.read_bytes())


def shuffled(value, rng: random.Random):
    if isinstance(value, dict):
        items = list(value.items())
        rng.shuffle(items)
        return {key: shuffled(item, rng) for key, item in items}
    if isinstance(value, list):
        return [shuffled(item, rng) for item in value]
    return value


class CapabilityGatewayV1Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.request_path = POSITIVE / "echo-request.json"
        self.request = load_strict(self.request_path)
        self.expected_canonical = (
            POSITIVE / "echo-request.canonical.json"
        ).read_bytes()
        self.expected_digest = (
            POSITIVE / "echo-request.digest.txt"
        ).read_text(encoding="utf-8").strip()

    def assert_violation(self, code: str, operation) -> ContractViolation:
        with self.assertRaises(ContractViolation) as raised:
            operation()
        self.assertEqual(code, raised.exception.code)
        return raised.exception

    def test_positive_canonical_bytes_and_digest(self) -> None:
        validate_request(self.request)
        self.assertEqual(self.expected_canonical, canonical_bytes(self.request))
        self.assertEqual(self.expected_digest, request_digest(self.request))

    def test_positive_manifest_and_echo_result(self) -> None:
        manifest = load_strict(POSITIVE / "echo-manifest.json")
        validate_manifest(manifest, now=NOW)
        expected = load_strict(POSITIVE / "echo-result.json")
        self.assertEqual(expected, execute_echo(manifest, now=NOW))

    def test_builder_binds_runtime_actor_outside_request(self) -> None:
        self.assertNotIn("actor", self.request)
        manifest = build_manifest(
            self.request,
            manifest_id="manifest_builder_0001",
            actor_ref="urn:dubnium:actor:transport-derived",
            authentication_method="loopback-profile",
            decision_ref="urn:anthesis:decision:synthetic-builder",
            issued_at="2026-08-05T20:00:01Z",
            expires_at="2026-08-05T20:09:00Z",
            granted_constraints={"max_output_bytes": 48},
        )
        self.assertEqual(
            "urn:dubnium:actor:transport-derived",
            manifest["actor"]["reference"],
        )
        self.assertEqual(self.expected_digest, manifest["request_digest"])

    def test_idempotent_retry_does_not_duplicate_dispatch(self) -> None:
        gateway = InMemoryGateway(
            actor_ref="urn:dubnium:actor:synthetic-loopback"
        )
        first = gateway.submit_and_execute(self.request_path.read_bytes(), now=NOW)
        second = gateway.submit_and_execute(self.request_path.read_bytes(), now=NOW)
        self.assertEqual(first, second)
        self.assertEqual(1, gateway.dispatch_count(self.request["request_id"]))

    def test_conflicting_request_id_fails_closed(self) -> None:
        fixture = json.loads(
            (NEGATIVE / "conflicting-request-id.json").read_text(encoding="utf-8")
        )
        gateway = InMemoryGateway(
            actor_ref="urn:dubnium:actor:synthetic-loopback"
        )
        gateway.submit_and_execute(
            json.dumps(fixture["first"], separators=(",", ":")).encode(),
            now=NOW,
        )
        self.assert_violation(
            "request_id_conflict",
            lambda: gateway.submit_and_execute(
                json.dumps(fixture["second"], separators=(",", ":")).encode(),
                now=NOW,
            ),
        )
        self.assertEqual(1, gateway.dispatch_count(fixture["first"]["request_id"]))

    def test_negative_request_fixtures(self) -> None:
        cases = {
            "unknown-field.json": "schema_validation_failed",
            "actor-spoof.json": "schema_validation_failed",
            "duplicate-key.json": "duplicate_key",
            "malformed-request-id.json": "schema_validation_failed",
            "malformed-timestamp.json": "invalid_timestamp",
            "lone-surrogate.json": "schema_validation_failed",
        }
        for filename, code in cases.items():
            with self.subTest(filename=filename):
                path = NEGATIVE / filename
                self.assert_violation(
                    code,
                    lambda path=path: validate_request(
                        parse_json_bytes(path.read_bytes())
                    ),
                )

    def test_oversized_body_is_rejected_before_parsing(self) -> None:
        descriptor = json.loads(
            (NEGATIVE / "oversized-body.json").read_text(encoding="utf-8")
        )
        body = bytes.fromhex(descriptor["repeat_byte"]) * descriptor["count"]
        self.assert_violation(
            descriptor["expected_code"], lambda: parse_json_bytes(body)
        )

    def test_negative_manifest_fixtures(self) -> None:
        cases = {
            "digest-mismatch-manifest.json": "manifest_invalid",
            "expired-manifest.json": "manifest_expired",
            "constraint-widening-manifest.json": "manifest_widening",
        }
        for filename, code in cases.items():
            with self.subTest(filename=filename):
                manifest = load_strict(NEGATIVE / filename)
                self.assert_violation(
                    code, lambda manifest=manifest: validate_manifest(manifest, now=NOW)
                )

    def test_key_order_does_not_change_canonical_bytes_or_digest(self) -> None:
        rng = random.Random(20260805)
        for _ in range(100):
            candidate = shuffled(self.request, rng)
            self.assertEqual(self.expected_canonical, canonical_bytes(candidate))
            self.assertEqual(self.expected_digest, request_digest(candidate))

    def test_mutated_payload_changes_digest(self) -> None:
        candidate = copy.deepcopy(self.request)
        candidate["payload"]["message"] = "Changed"
        self.assertNotEqual(self.expected_digest, request_digest(candidate))

    def test_safe_integer_boundaries_and_floats(self) -> None:
        candidate = copy.deepcopy(self.request)
        candidate["payload"]["max_output_bytes"] = 9_007_199_254_740_992
        self.assert_violation(
            "schema_validation_failed", lambda: canonical_bytes(candidate)
        )
        self.assert_violation(
            "schema_validation_failed",
            lambda: parse_json_bytes(b'{"value":1.5}'),
        )
        self.assert_violation(
            "schema_validation_failed",
            lambda: parse_json_bytes(b'{"value":NaN}'),
        )

    def test_lone_surrogate_is_rejected(self) -> None:
        self.assert_violation(
            "schema_validation_failed",
            lambda: canonical_bytes({"value": "\ud800"}),
        )

    def test_synthetic_deployment_fixture_is_non_executable_reference(self) -> None:
        request = load_strict(SYNTHETIC / "deployment-apply-request.json")
        validate_request(request)
        self.assertEqual("deployment.apply", request["capability"]["name"])
        manifest = build_manifest(
            request,
            manifest_id="manifest_deploy_synth01",
            actor_ref="urn:dubnium:actor:synthetic-loopback",
            authentication_method="loopback-profile",
            decision_ref="urn:anthesis:decision:synthetic-deployment",
            issued_at="2026-08-05T20:00:01Z",
            expires_at="2026-08-05T20:04:00Z",
            granted_constraints={},
        )
        self.assert_violation(
            "provider_failed", lambda: execute_echo(manifest, now=NOW)
        )

    def test_problem_details_are_bounded_and_stable(self) -> None:
        violation = ContractViolation("request_id_conflict", "x" * 1000)
        document = problem(
            violation,
            request_id=self.request["request_id"],
            digest=self.expected_digest,
        )
        self.assertEqual(409, document["status"])
        self.assertEqual("request_id_conflict", document["code"])
        self.assertLessEqual(len(document["detail"]), 512)
        self.assertEqual(self.expected_digest, document["request_digest"])


if __name__ == "__main__":
    unittest.main()
