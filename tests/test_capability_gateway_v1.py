from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import unittest

from conformance import capability_gateway_v1 as contract

ROOT = Path(__file__).resolve().parents[1]


class CapabilityGatewayV1Tests(unittest.TestCase):
    def setUp(self):
        self.contract = contract
        self.fixtures = ROOT / "conformance" / "fixtures" / "v1"
        self.request = contract.load_json(self.fixtures / "positive" / "request.json")
        self.manifest = contract.load_json(self.fixtures / "positive" / "authorized-manifest.json")

    def test_positive_fixture_vector(self):
        expected_bytes = (self.fixtures / "positive" / "request.canonical.json").read_bytes()
        expected_digest = (self.fixtures / "positive" / "request.digest.txt").read_text(encoding="utf-8").strip()
        normalized = contract.normalize_request(self.request)
        self.assertEqual(contract.canonical_json_bytes(normalized), expected_bytes)
        self.assertEqual(contract.request_digest(self.request), expected_digest)

    def test_fixture_suite_passes(self):
        self.assertEqual(contract.run_fixture_suite(self.fixtures), [])

    def test_actor_spoof_is_rejected_as_unknown_request_field(self):
        candidate = dict(self.request)
        candidate["actor_ref"] = "workload:spoofed"
        with self.assertRaises(contract.ContractError) as caught:
            contract.normalize_request(candidate)
        self.assertEqual(caught.exception.code, "contract.unknown_field")

    def test_duplicate_key_is_rejected_before_map_construction(self):
        raw = b'{"contract_version":"1.0","request_id":"a","request_id":"b"}'
        with self.assertRaises(contract.ContractError) as caught:
            contract.parse_json_bytes(raw)
        self.assertEqual(caught.exception.code, "json.duplicate_key")

    def test_input_limit_is_enforced_before_parsing(self):
        with self.assertRaises(contract.ContractError) as caught:
            contract.parse_json_bytes(b"{" + b" " * 65536)
        self.assertEqual(caught.exception.code, "input.too_large")

    def test_unicode_is_not_silently_normalized(self):
        composed = dict(self.request)
        decomposed = dict(self.request)
        composed["payload"] = {"message": "caf\u00e9", "repeat": 1}
        decomposed["payload"] = {"message": "cafe\u0301", "repeat": 1}
        self.assertNotEqual(contract.request_digest(composed), contract.request_digest(decomposed))

    def test_floats_and_null_are_rejected(self):
        for value, code in ((1.5, "json.float_prohibited"), (None, "json.null_prohibited")):
            candidate = dict(self.request)
            candidate["payload"] = {"message": "hello", "repeat": value}
            with self.assertRaises(contract.ContractError) as caught:
                contract.normalize_request(candidate)
            self.assertEqual(caught.exception.code, code)

    def test_manifest_is_exact_and_unexpired(self):
        normalized = contract.validate_manifest(
            self.request,
            self.manifest,
            now=datetime(2030, 1, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(normalized["request_digest"], contract.request_digest(self.request))
        self.assertEqual(normalized["actor_ref"], "workload:synthetic-client")

    def test_manifest_single_fault_cases_fail_closed(self):
        cases = {
            "manifest-digest-mismatch.json": "manifest.digest_mismatch",
            "manifest-expired-rfc8785.json": "manifest.expired",
            "manifest-expiry-widening-rfc8785.json": "manifest.expiry_widening",
            "manifest-constraint-widening-rfc8785.json": "manifest.constraint_widening",
            "manifest-payload-mismatch-rfc8785.json": "manifest.payload_mismatch",
        }
        for filename, code in cases.items():
            with self.subTest(filename=filename):
                candidate = contract.load_json(self.fixtures / "negative" / filename)
                with self.assertRaises(contract.ContractError) as caught:
                    contract.validate_manifest(
                        self.request,
                        candidate,
                        now=datetime(2030, 1, 1, tzinfo=timezone.utc),
                    )
                self.assertEqual(caught.exception.code, code)

    def test_no_effect_provider_is_deterministic_and_bounded(self):
        first = contract.execute_no_effect(self.request, self.manifest)
        second = contract.execute_no_effect(self.request, self.manifest)
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "succeeded")
        self.assertEqual(first["output"], {"echo": ["hello", "hello"]})

    def test_canonicalization_has_no_trailing_newline_or_ascii_escape(self):
        encoded = contract.canonical_json_bytes({"z": "caf\u00e9", "a": 1})
        self.assertEqual(encoded, b'{"a":1,"z":"caf\xc3\xa9"}')
        self.assertFalse(encoded.endswith(b"\n"))

    def test_cli_fixture_command(self):
        self.assertEqual(contract.main(["run-fixtures", str(self.fixtures)]), 0)


if __name__ == "__main__":
    unittest.main()
