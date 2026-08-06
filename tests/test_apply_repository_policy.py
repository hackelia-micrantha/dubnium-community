from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "apply_repository_policy", ROOT / "scripts" / "apply_repository_policy.py"
)
assert SPEC and SPEC.loader
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)


class RepositoryPolicyTests(unittest.TestCase):
    def test_repository_allows_only_squash_merge(self) -> None:
        settings = policy.repository_settings()
        self.assertFalse(settings["allow_merge_commit"])
        self.assertFalse(settings["allow_rebase_merge"])
        self.assertTrue(settings["allow_squash_merge"])

    def test_main_requires_stable_aggregate_checks(self) -> None:
        protection = policy.branch_protection()
        self.assertTrue(protection["required_status_checks"]["strict"])
        self.assertEqual(
            sorted(policy.REQUIRED_CHECKS),
            sorted(protection["required_status_checks"]["contexts"]),
        )

    def test_main_fails_closed_without_impossible_approval_count(self) -> None:
        protection = policy.branch_protection()
        reviews = protection["required_pull_request_reviews"]
        self.assertEqual(0, reviews["required_approving_review_count"])
        self.assertTrue(reviews["dismiss_stale_reviews"])
        self.assertTrue(protection["enforce_admins"])
        self.assertTrue(protection["required_linear_history"])
        self.assertTrue(protection["required_conversation_resolution"])
        self.assertFalse(protection["allow_force_pushes"])
        self.assertFalse(protection["allow_deletions"])

    def test_active_response_normalizes_to_expected_policy(self) -> None:
        repo = policy.repository_settings()
        protection = {
            "required_status_checks": {"strict": True, "contexts": list(reversed(policy.REQUIRED_CHECKS))},
            "enforce_admins": {"enabled": True},
            "required_pull_request_reviews": {
                "dismiss_stale_reviews": True,
                "required_approving_review_count": 0,
            },
            "required_linear_history": {"enabled": True},
            "allow_force_pushes": {"enabled": False},
            "allow_deletions": {"enabled": False},
            "required_conversation_resolution": {"enabled": True},
        }
        self.assertEqual(policy.expected_active(), policy.normalized_active(repo, protection))


if __name__ == "__main__":
    unittest.main()
