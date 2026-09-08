from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "prepare_public_book.py"
WORKFLOW_PATH = Path(__file__).parents[1] / ".github" / "workflows" / "build-public-book.yml"
SPEC = importlib.util.spec_from_file_location("prepare_public_book", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PreparePublicBookTests(unittest.TestCase):
    def make_root(self, directory: str) -> tuple[Path, Path]:
        root = Path(directory)
        source = root / "docs" / "external"
        source.mkdir(parents=True)
        summary = ["# Summary", ""]
        for target in sorted(MODULE.PUBLIC_SUMMARY_TARGETS):
            (source / target).write_text(f"# {target}\n", encoding="utf-8")
            summary.append(f"- [{target}]({target})")
        (source / "SUMMARY.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
        output = root / "build"
        output.mkdir()
        (output / "index.html").write_text("<html>public</html>", encoding="utf-8")
        return root, output

    def test_accepts_curated_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, output = self.make_root(directory)
            self.assertEqual([], MODULE.validate_source(root))
            self.assertEqual([], MODULE.validate_output(output))

    def test_rejects_unlinked_source_page(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, _ = self.make_root(directory)
            (root / "docs" / "external" / "control-plane.md").write_text(
                "# Unlinked operational detail\n", encoding="utf-8"
            )
            errors = MODULE.validate_source(root)
            self.assertTrue(
                any("unallowlisted files" in error and "control-plane.md" in error for error in errors)
            )

    def test_rejects_unallowlisted_source_asset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, _ = self.make_root(directory)
            (root / "docs" / "external" / "diagram.png").write_bytes(b"not-really-an-image")
            errors = MODULE.validate_source(root)
            self.assertTrue(
                any("unallowlisted files" in error and "diagram.png" in error for error in errors)
            )

    def test_rejects_non_overview_summary_page(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, _ = self.make_root(directory)
            summary = root / "docs" / "external" / "SUMMARY.md"
            summary.write_text(summary.read_text(encoding="utf-8") + "- [Runbook](runtime-runbook.md)\n", encoding="utf-8")
            errors = MODULE.validate_source(root)
            self.assertTrue(any("non-overview pages" in error for error in errors))

    def test_rejects_missing_required_overview_page(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, _ = self.make_root(directory)
            summary = root / "docs" / "external" / "SUMMARY.md"
            summary.write_text(
                summary.read_text(encoding="utf-8").replace("- [status.md](status.md)\n", ""),
                encoding="utf-8",
            )
            errors = MODULE.validate_source(root)
            self.assertTrue(any("missing required overview pages" in error for error in errors))

    def test_accepts_mdbook_nojekyll_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, output = self.make_root(directory)
            (output / ".nojekyll").write_text("", encoding="utf-8")
            self.assertEqual([], MODULE.validate_output(output))

    def test_rejects_unexpected_generated_file_type(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, output = self.make_root(directory)
            (output / "unexpected.bin").write_bytes(b"data")
            errors = MODULE.validate_output(output)
            self.assertTrue(any("unexpected generated file type" in error for error in errors))

    def test_rejects_source_map_to_match_destination_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, output = self.make_root(directory)
            (output / "private-paths.js.map").write_text("{}", encoding="utf-8")
            errors = MODULE.validate_output(output)
            self.assertTrue(any("unexpected generated file type" in error for error in errors))

    def test_rejects_private_repository_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, output = self.make_root(directory)
            (output / "index.html").write_text(
                '<a href="https://github.com/ryjen/dubnium">private</a>', encoding="utf-8"
            )
            errors = MODULE.validate_output(output)
            self.assertTrue(any("private repository URL" in error for error in errors))

    def test_rejects_private_issue_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, output = self.make_root(directory)
            (output / "index.html").write_text("Tracked by ryjen/dubnium#403", encoding="utf-8")
            errors = MODULE.validate_output(output)
            self.assertTrue(any("private issue reference" in error for error in errors))

    def test_rejects_internal_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, output = self.make_root(directory)
            (output / "index.html").write_text("docs/internal/runbook.md", encoding="utf-8")
            errors = MODULE.validate_output(output)
            self.assertTrue(any("internal documentation path" in error for error in errors))

    def test_allows_localhost_documentation_example(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, output = self.make_root(directory)
            (output / "index.html").write_text(
                "<p>For local development, open http://localhost:8000.</p>",
                encoding="utf-8",
            )
            self.assertEqual([], MODULE.validate_output(output))

    def test_rejects_localhost_link_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, output = self.make_root(directory)
            (output / "index.html").write_text(
                '<a href="http://localhost:8000/admin">admin</a>', encoding="utf-8"
            )
            errors = MODULE.validate_output(output)
            self.assertTrue(any("localhost endpoint" in error for error in errors))

    def test_rejects_unquoted_localhost_link_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, output = self.make_root(directory)
            (output / "index.html").write_text(
                '<a href=http://localhost:8000/admin>admin</a>', encoding="utf-8"
            )
            errors = MODULE.validate_output(output)
            self.assertTrue(any("localhost endpoint" in error for error in errors))

    def test_allows_localhost_text_in_generated_search_index(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, output = self.make_root(directory)
            (output / "searchindex-d035b8e1.js").write_text(
                'window.search = "http://localhost:8000";', encoding="utf-8"
            )
            self.assertEqual([], MODULE.validate_output(output))

    def test_allows_secret_like_token_in_generated_mermaid_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, output = self.make_root(directory)
            (output / "mermaid-eefea253.min.js").write_text(
                "TOKEN=parserToken;", encoding="utf-8"
            )
            self.assertEqual([], MODULE.validate_output(output))

    def test_rejects_secret_like_assignment_in_regular_script(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, output = self.make_root(directory)
            (output / "custom.js").write_text(
                "TOKEN=actualValue;", encoding="utf-8"
            )
            errors = MODULE.validate_output(output)
            self.assertTrue(any("secret-like assignment" in error for error in errors))

    def test_writes_deterministic_public_safe_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, output = self.make_root(directory)
            MODULE.write_provenance(
                output,
                "mdbook 0.5.2; mdbook-mermaid 0.17.0",
                "2026-07-28T05:00:00+00:00",
            )
            first = (output / "publication.json").read_text(encoding="utf-8")
            MODULE.write_provenance(
                output,
                "mdbook 0.5.2; mdbook-mermaid 0.17.0",
                "2026-07-28T05:00:00Z",
            )
            second = (output / "publication.json").read_text(encoding="utf-8")
            payload = json.loads(second)
            self.assertEqual(first, second)
            self.assertEqual(2, payload["schema_version"])
            self.assertTrue(payload["publication_id"].startswith("dubnium-book-"))
            self.assertRegex(payload["content_digest"], r"^sha256:[0-9a-f]{64}$")
            self.assertEqual("2026-07-28T05:00:00Z", payload["generated_at"])
            self.assertNotIn("source_repository", payload)
            self.assertNotIn("source_commit", payload)
            self.assertNotIn("workflow_run_id", payload)

    def test_content_digest_changes_with_public_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, output = self.make_root(directory)
            before = MODULE.calculate_content_digest(output)
            (output / "index.html").write_text("<html>changed</html>", encoding="utf-8")
            after = MODULE.calculate_content_digest(output)
            self.assertNotEqual(before, after)

    def test_replaces_only_site_docs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, output = self.make_root(directory)
            destination = root / "destination"
            (destination / "site").mkdir(parents=True)
            (destination / "site" / "index.html").write_text("landing", encoding="utf-8")
            MODULE.replace_destination(output, destination)
            self.assertEqual("landing", (destination / "site" / "index.html").read_text(encoding="utf-8"))
            self.assertTrue((destination / "site" / "docs" / "index.html").is_file())

    def test_build_workflow_runs_generator_and_validator(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("run: scripts/build-public-book.sh", workflow)
        self.assertIn("run: python3 scripts/validate_publication.py", workflow)


if __name__ == "__main__":
    unittest.main()
