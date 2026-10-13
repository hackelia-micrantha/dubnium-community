from __future__ import annotations

from pathlib import Path
import json
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

    def test_succeeded_status_rejects_error(self):
        candidate = self.module.core.load_json(self.fixtures / "negative" / "status-succeeded-with-error.json")
        with self.assertRaises(self.module.core.ContractError) as caught:
            self.module.validate_status(candidate)
        self.assertEqual(caught.exception.code, "status.error_on_success")

    def test_predispatch_indeterminate_has_no_provider_operation(self):
        candidate = self.module.core.load_json(self.fixtures / "positive" / "status-indeterminate-pre-policy.json")
        normalized = self.module.validate_status(candidate)
        self.assertNotIn("provider_operation", normalized)

    def test_public_schema_matches_provider_dispatch_boundary(self):
        schema = json.loads((ROOT / "schemas/v1/capability-status.schema.json").read_text())
        self.assertIn("indeterminate", schema["properties"]["gateway_state"]["enum"])
        rules = schema["allOf"]
        required = next(
            rule for rule in rules
            if rule.get("then") == {"required": ["provider_operation"]}
        )
        self.assertEqual(
            set(required["if"]["properties"]["gateway_state"]["enum"]),
            {"dispatched", "succeeded", "failed"},
        )
        forbidden = next(
            rule for rule in rules
            if rule.get("then") == {"not": {"required": ["provider_operation"]}}
        )
        self.assertEqual(
            set(forbidden["if"]["properties"]["gateway_state"]["enum"]),
            {"received", "validated", "policy-pending", "denied", "authorized"},
        )
        # An indeterminate status must not be constrained by either rule;
        # its dispatch history (not the single-document schema) decides.
        self.assertNotIn("indeterminate", required["if"]["properties"]["gateway_state"]["enum"])
        self.assertNotIn("indeterminate", forbidden["if"]["properties"]["gateway_state"]["enum"])

    def test_predispatch_indeterminate_transition_without_provider(self):
        indeterminate = self.module.core.load_json(
            self.fixtures / "positive" / "status-indeterminate-pre-restart.json"
        )
        pending = dict(indeterminate)
        pending["gateway_state"] = "policy-pending"
        pending.pop("error")
        pending["updated_at"] = "2026-08-05T20:00:02Z"
        result = self.module.validate_status_transition(pending, indeterminate)
        self.assertNotIn("provider_operation", result)

    def test_indeterminate_after_dispatch_keeps_same_provider(self):
        dispatched = self.module.core.load_json(
            self.fixtures / "positive" / "status-dispatched.json"
        )
        after = self.module.core.load_json(
            self.fixtures / "positive" / "status-indeterminate-post-restart.json"
        )
        self.assertEqual(
            self.module.validate_status_transition(dispatched, after)["provider_operation"]["operation_ref"],
            dispatched["provider_operation"]["operation_ref"],
        )

    def test_postdispatch_provider_reference_cannot_be_lost(self):
        dispatched = self.module.core.load_json(self.fixtures / "positive" / "status-dispatched.json")
        no_provider = self.module.core.load_json(self.fixtures / "positive" / "status-indeterminate-pre-restart.json")
        with self.assertRaises(self.module.core.ContractError) as caught:
            self.module.validate_status_transition(dispatched, no_provider)
        self.assertEqual(caught.exception.code, "status.operation_lost")

    def test_dispatched_to_succeeded_transition_is_valid(self):
        dispatched = self.module.core.load_json(self.fixtures / "positive" / "status-dispatched.json")
        succeeded = self.module.core.load_json(self.fixtures / "positive" / "status-succeeded.json")
        result = self.module.validate_status_transition(dispatched, succeeded)
        self.assertEqual(result["gateway_state"], "succeeded")


if __name__ == "__main__":
    unittest.main()
