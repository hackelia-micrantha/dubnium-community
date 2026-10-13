from __future__ import annotations

import importlib.util
import io
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_contract_tag_rulesets", ROOT / "scripts/check_contract_tag_rulesets.py"
)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class ContractTagRulesetTests(unittest.TestCase):
    def setUp(self):
        self.expected = checker.desired("User", 12345)

    def test_plan_has_disjoint_creator_and_immutability_permissions(self):
        creator, immutable = self.expected
        self.assertEqual(creator["conditions"]["ref_name"]["include"], ["refs/tags/contract-v*"])
        self.assertEqual([r["type"] for r in creator["rules"]], ["creation"])
        self.assertEqual(creator["bypass_actors"], [
            {"actor_type": "User", "actor_id": 12345, "bypass_mode": "always"}
        ])
        self.assertEqual([r["type"] for r in immutable["rules"]], ["update", "deletion"])
        self.assertEqual(immutable["bypass_actors"], [])
        self.assertEqual([], checker.validate_rulesets(deepcopy(self.expected), self.expected))

    def test_broad_creator_roles_are_rejected(self):
        for actor in ("OrganizationAdmin", "RepositoryRole", "DeployKey"):
            with self.subTest(actor=actor), self.assertRaises(ValueError):
                checker.desired(actor, 123)
        with self.assertRaises(ValueError):
            checker.desired("User", 0)

    def test_missing_bypass_visibility_fails_closed(self):
        data = deepcopy(self.expected)
        del data[1]["bypass_actors"]
        self.assertTrue(any("not visible" in x for x in checker.validate_rulesets(data, self.expected)))

    def test_update_or_delete_bypass_fails_closed(self):
        data = deepcopy(self.expected)
        data[1]["bypass_actors"] = list(data[0]["bypass_actors"])
        self.assertTrue(any("bypass actors mismatch" in x for x in checker.validate_rulesets(data, self.expected)))

    def test_creation_bypass_cannot_be_broad_or_wrong_identity(self):
        data = deepcopy(self.expected)
        data[0]["bypass_actors"] = [
            {"actor_type": "OrganizationAdmin", "actor_id": None, "bypass_mode": "always"}
        ]
        self.assertTrue(any("bypass actors mismatch" in x for x in checker.validate_rulesets(data, self.expected)))

    def test_inactive_missing_or_incomplete_rules_fail_closed(self):
        data = deepcopy(self.expected)
        data[1]["enforcement"] = "disabled"
        self.assertTrue(any("missing active" in x for x in checker.validate_rulesets(data, self.expected)))
        data = deepcopy(self.expected)
        data[1]["rules"] = [{"type": "deletion"}]
        self.assertTrue(any("restrictions mismatch" in x for x in checker.validate_rulesets(data, self.expected)))

    def test_ref_patterns_must_match_and_have_no_exclusions(self):
        data = deepcopy(self.expected)
        data[0]["conditions"]["ref_name"]["include"] = ["refs/tags/*"]
        self.assertTrue(any("pattern" in x for x in checker.validate_rulesets(data, self.expected)))
        data = deepcopy(self.expected)
        data[0]["conditions"]["ref_name"]["exclude"] = ["refs/tags/contract-v0.1*"]
        self.assertTrue(any("pattern" in x for x in checker.validate_rulesets(data, self.expected)))

    def test_unknown_tag_rulesets_are_not_silently_ignored(self):
        data = deepcopy(self.expected)
        extra = deepcopy(data[0])
        extra["name"] = "other-active-tag-controls"
        data.append(extra)
        self.assertTrue(any("unexpected active" in x for x in checker.validate_rulesets(data, self.expected)))

    def test_network_client_is_read_only(self):
        with patch.object(checker.urllib.request, "urlopen") as mock_open:
            mock_open.return_value.__enter__.return_value = io.BytesIO(b"[]")
            self.assertEqual([], checker.get("placeholder", "/repos/hackelia-micrantha/dubnium-community/rulesets"))
            req = mock_open.call_args.args[0]
            self.assertEqual(req.get_method(), "GET")
            self.assertTrue(req.full_url.startswith("https://api.github.com/"))


if __name__ == "__main__":
    unittest.main()
