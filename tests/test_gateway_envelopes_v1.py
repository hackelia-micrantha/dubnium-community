from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "conformance" / "gateway_envelopes_v1.py"
    spec = importlib.util.spec_from_file_location("gateway_envelopes_v1_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GatewayEnvelopeV1Tests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.fixtures = ROOT / "conformance" / "fixtures" / "v1"
        request = self.module.core.load_json(self.fixtures / "positive" / "request.json")
        self.request = self.module.core.normalize_request(request)
        self.digest = self.module.core.digest_value(self.request)

    def test_fixture_suite_passes(self):
        self.assertEqual(self.module.run_fixture_suite(self.fixtures), [])

    def test_rejection_before_normalization_may_omit_identity(self):
        candidate = self.module.core.load_json(
            self.fixtures / "positive" / "rejected-submission.json"
        )
        result = self.module.validate_submission(candidate)
        self.assertEqual(result["state"], "rejected")
        self.assertNotIn("request_id", result)

    def test_accepted_submission_requires_exact_identity(self):
        candidate = self.module.core.load_json(
            self.fixtures / "positive" / "submission.json"
        )
        result = self.module.validate_submission(
            candidate,
            expected_request_id=self.request["request_id"],
            expected_digest=self.digest,
        )
        self.assertEqual(result["request_digest"], self.digest)

    def test_status_requires_error_for_failure(self):
        candidate = self.module.core.load_json(
            self.fixtures / "negative" / "status-failure-without-error.json"
        )
        with self.assertRaises(self.module.core.ContractError) as caught:
            self.module.validate_status(candidate)
        self.assertEqual(caught.exception.code, "contract.missing_field")

    def test_terminal_result_is_bounded(self):
        candidate = self.module.core.load_json(
            self.fixtures / "positive" / "status.json"
        )
        candidate["terminal_result"] = {"value": "x" * 5000}
        with self.assertRaises(self.module.core.ContractError) as caught:
            self.module.validate_status(candidate)
        self.assertEqual(caught.exception.code, "status.result_too_large")


if __name__ == "__main__":
    unittest.main()
