from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "check_workflow_security.py"
SPEC = importlib.util.spec_from_file_location("check_workflow_security", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

CHECKOUT_SHA = "11d5960a326750d5838078e36cf38b85af677262"


def valid_workflow() -> str:
    return f"""name: Test

on:
  pull_request:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Checkout
        uses: actions/checkout@{CHECKOUT_SHA}
        with:
          persist-credentials: false
      - name: Test
        run: python3 -m unittest
"""


class WorkflowSecurityTests(unittest.TestCase):
    def validate_text(self, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "workflow.yml"
            path.write_text(text, encoding="utf-8")
            return MODULE.validate_workflow(path)

    def test_accepts_pinned_read_only_workflow(self) -> None:
        self.assertEqual([], self.validate_text(valid_workflow()))

    def test_rejects_mutable_action_tag(self) -> None:
        errors = self.validate_text(valid_workflow().replace(f"actions/checkout@{CHECKOUT_SHA}", "actions/checkout@v6"))
        self.assertTrue(any("full immutable SHA" in error for error in errors))

    def test_rejects_pull_request_target(self) -> None:
        errors = self.validate_text(valid_workflow().replace("  pull_request:", "  pull_request_target:"))
        self.assertTrue(any("pull_request_target" in error for error in errors))

    def test_rejects_write_permissions_on_pr(self) -> None:
        errors = self.validate_text(valid_workflow().replace("contents: read", "contents: write"))
        self.assertTrue(any("write permissions" in error for error in errors))

    def test_rejects_persisted_checkout_credentials(self) -> None:
        errors = self.validate_text(valid_workflow().replace("persist-credentials: false", "persist-credentials: true"))
        self.assertTrue(any("persist-credentials" in error for error in errors))

    def test_rejects_self_hosted_runner(self) -> None:
        errors = self.validate_text(valid_workflow().replace("runs-on: ubuntu-latest", "runs-on: [self-hosted, linux]"))
        self.assertTrue(any("self-hosted" in error for error in errors))

    def test_rejects_missing_timeout(self) -> None:
        errors = self.validate_text(valid_workflow().replace("    timeout-minutes: 5\n", ""))
        self.assertTrue(any("requires timeout-minutes" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
