from __future__ import annotations

from pathlib import Path
import unittest

from conformance import gateway_envelopes_v1 as envelopes

ROOT = Path(__file__).resolve().parents[1]


class GatewayEnvelopeV1Tests(unittest.TestCase):
    def setUp(self):
        self.module = envelopes
        self.fixtures = ROOT / "conformance" / "envelopes" / "v1"

    def test_fixture_suite_passes(self):
        self.assertEqual(self.module.run_fixture_suite(self.fixtures), [])

    def test_accepted_submission_requires_status_reference(self):
        candidate = self.module.core.load_json(self.fixtures / "positive" / "submission.json")
        result = self.module.validate_submission(candidate)
        self.assertEqual(result["outcome"], "accepted")
        self.assertIn("status_ref", result)
        self.assertNotIn("error", result)

    def test_rejected_submission_requires_retryable_error(self):
        candidate = self.module.core.load_json(self.fixtures / "positive" / "submission-rejected.json")
        result = self.module.validate_submission(candidate)
        self.assertEqual(result["outcome"], "rejected")
        self.assertIsInstance(result["error"]["retryable"], bool)
        self.assertNotIn("status_ref", result)

    def test_status_requires_error_for_failure(self):
        candidate = self.module.core.load_json(self.fixtures / "negative" / "status-succeeded-with-error.json")
        with self.assertRaises(self.module.core.ContractError) as caught:
            self.module.validate_status(candidate)
        self.assertEqual(caught.exception.code, "status.error_on_success")

    def test_terminal_status_is_immutable(self):
        succeeded = self.module.core.load_json(self.fixtures / "positive" / "status-succeeded.json")
        changed = dict(succeeded)
        changed["updated_at"] = "2026-08-05T20:00:03Z"
        with self.assertRaises(self.module.core.ContractError) as caught:
            self.module.validate_status_transition(succeeded, changed)
        self.assertEqual(caught.exception.code, "status.terminal_mutation")


if __name__ == "__main__":
    unittest.main()
