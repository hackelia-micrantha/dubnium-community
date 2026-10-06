from __future__ import annotations

import json
from pathlib import Path
import unittest

from conformance.event_contract_v1 import ContractError, validate_event

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "conformance" / "fixtures" / "events-v1" / "fixtures.json"
SCHEMA = ROOT / "schemas" / "v1alpha" / "event.schema.json"


class EventContractV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        document = json.loads(FIXTURES.read_text(encoding="utf-8"))
        cls.cases = {case["id"]: case for case in document["cases"]}

    def test_positive_fixtures_validate(self) -> None:
        for case in self.cases.values():
            if case["valid"]:
                with self.subTest(case=case["id"]):
                    validate_event(case["event"])

    def test_negative_fixtures_reject_with_expected_code(self) -> None:
        for case in self.cases.values():
            if not case["valid"]:
                with self.subTest(case=case["id"]):
                    with self.assertRaises(ContractError) as caught:
                        validate_event(case["event"])
                    self.assertEqual(case["error"], caught.exception.code)

    def test_trace_context_is_correlation_not_authority_data(self) -> None:
        event = dict(self.cases["supervisor-traced"]["event"])
        event["data"] = {
            "severity": "warning",
            "authorization": "synthetic-allow",
        }
        with self.assertRaises(ContractError) as caught:
            validate_event(event)
        self.assertEqual("data.sensitive_field", caught.exception.code)

    def test_schema_identifies_cloud_events_and_dubnium_patterns(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual("1.0", schema["properties"]["specversion"]["const"])
        self.assertIn("urn:dubnium:", schema["properties"]["source"]["pattern"])
        self.assertIn("micrantha", schema["properties"]["type"]["pattern"])
        self.assertEqual(
            ["debug", "info", "warning", "error", "critical"],
            schema["properties"]["data"]["properties"]["severity"]["enum"],
        )


if __name__ == "__main__":
    unittest.main()
