from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "classify_changes.py"
SPEC = importlib.util.spec_from_file_location("classify_changes", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ChangeClassificationTests(unittest.TestCase):
    def test_contract_paths(self) -> None:
        result = MODULE.classify(["spec/capability.md", "schemas/capability/request.json"])
        self.assertTrue(result["contract"])
        self.assertFalse(result["site"])

    def test_publication_workflow_is_site_and_build(self) -> None:
        categories = MODULE.classify_path(".github/workflows/validate-publication.yml")
        self.assertEqual({"site", "build"}, categories)

    def test_policy_paths(self) -> None:
        result = MODULE.classify(["COMPATIBILITY.md", "docs/standards.md"])
        self.assertTrue(result["policy"])

    def test_unknown_source_defaults_to_implementation(self) -> None:
        self.assertEqual({"implementation"}, MODULE.classify_path("tools/example.py"))

    def test_windows_paths_are_normalized(self) -> None:
        self.assertEqual({"contract"}, MODULE.classify_path(r"schemas\example.json"))

    def test_github_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output"
            MODULE.write_github_output(MODULE.classify(["README.md"]), str(output))
            text = output.read_text(encoding="utf-8")
            self.assertIn("policy=true", text)
            self.assertIn("any=true", text)


if __name__ == "__main__":
    unittest.main()
