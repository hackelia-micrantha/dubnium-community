from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "validate_publication.py"
SPEC = importlib.util.spec_from_file_location("validate_publication", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PublicationValidationTests(unittest.TestCase):
    def make_book(self, root: Path, html: str = "<html>public</html>") -> Path:
        docs = root / "site" / "docs"
        docs.mkdir(parents=True)
        (docs / "index.html").write_text(html, encoding="utf-8")
        (docs / "publication.json").write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "publication_id": "dubnium-docs-example-0001",
                    "content_digest": "sha256:" + "b" * 64,
                    "generator": "mdbook 0.5.2; mdbook-mermaid 0.17.0",
                    "generated_at": "2026-08-05T20:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        return docs

    def make_legacy_book(self, root: Path) -> Path:
        docs = root / "site" / "docs"
        docs.mkdir(parents=True)
        (docs / "index.html").write_text("<html>legacy</html>", encoding="utf-8")
        (docs / "publication.json").write_text(
            json.dumps(
                {
                    "source_repository": "legacy/private-producer",
                    "source_commit": "a" * 40,
                    "generator": "mdbook 0.5.2; mdbook-mermaid 0.17.0",
                    "generated_at": "2026-07-28T04:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        return docs

    def test_accepts_valid_publication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_book(root)
            self.assertEqual([], MODULE.validate(root))

    def test_accepts_existing_legacy_publication_without_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_legacy_book(root)
            self.assertEqual([], MODULE.validate(root))

    def test_rejects_legacy_metadata_for_changed_publication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_legacy_book(root)
            errors = MODULE.validate(root, require_public_schema=True)
            self.assertTrue(any("schema_version 2" in error for error in errors))

    def test_accepts_mdbook_generated_exceptions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = self.make_book(root, "<p>Use http://localhost:8000 locally.</p>")
            (docs / ".nojekyll").write_text("", encoding="utf-8")
            (docs / "searchindex-d035b8e1.js").write_text(
                'window.search = "http://localhost:8000";', encoding="utf-8"
            )
            (docs / "mermaid-eefea253.min.js").write_text(
                "TOKEN=parserToken;", encoding="utf-8"
            )
            self.assertEqual([], MODULE.validate(root))

    def test_rejects_localhost_link_targets(self) -> None:
        for html in (
            '<a href="http://localhost:8000/admin">admin</a>',
            '<a href=http://localhost:8000/admin>admin</a>',
        ):
            with self.subTest(html=html), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.make_book(root, html)
                errors = MODULE.validate(root)
                self.assertTrue(any("localhost endpoint" in error for error in errors))

    def test_rejects_secret_assignment_in_regular_script(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = self.make_book(root)
            (docs / "custom.js").write_text("TOKEN=actualValue;", encoding="utf-8")
            errors = MODULE.validate(root)
            self.assertTrue(any("secret-like assignment" in error for error in errors))

    def test_rejects_unexpected_extensionless_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = self.make_book(root)
            (docs / "unexpected").write_text("data", encoding="utf-8")
            errors = MODULE.validate(root)
            self.assertTrue(any("unexpected generated file type" in error for error in errors))

    def test_rejects_private_repository_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_book(root, '<a href="https://github.com/ryjen/dubnium/edit/main/docs/external/README.md">edit</a>')
            errors = MODULE.validate(root)
            self.assertTrue(any("private repository URL" in error for error in errors))

    def test_rejects_internal_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_book(root, "docs/internal/runbooks/example.md")
            errors = MODULE.validate(root)
            self.assertTrue(any("internal documentation path" in error for error in errors))

    def test_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = self.make_book(root)
            target = docs / "index.html"
            target.unlink()
            target.symlink_to("publication.json")
            errors = MODULE.validate(root)
            self.assertTrue(any("symlinks are not allowed" in error for error in errors))

    def test_rejects_malformed_public_digest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = self.make_book(root)
            metadata = json.loads((docs / "publication.json").read_text(encoding="utf-8"))
            metadata["content_digest"] = "sha256:not-a-digest"
            (docs / "publication.json").write_text(json.dumps(metadata), encoding="utf-8")
            errors = MODULE.validate(root)
            self.assertTrue(any("64 lowercase hex" in error for error in errors))

    def test_rejects_private_fields_in_public_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = self.make_book(root)
            metadata = json.loads((docs / "publication.json").read_text(encoding="utf-8"))
            metadata["source_commit"] = "a" * 40
            (docs / "publication.json").write_text(json.dumps(metadata), encoding="utf-8")
            errors = MODULE.validate(root)
            self.assertTrue(any("forbids private provenance fields" in error for error in errors))

    def test_accepts_publication_only_changed_paths(self) -> None:
        self.assertEqual([], MODULE.validate_changed_paths(["site/docs/index.html", "site/docs/publication.json"]))

    def test_rejects_mixed_publication_changes(self) -> None:
        errors = MODULE.validate_changed_paths(["site/docs/index.html", ".github/workflows/pages.yml"])
        self.assertTrue(any("confined to site/docs" in error for error in errors))

    def test_detects_changed_publication_metadata(self) -> None:
        self.assertTrue(MODULE.publication_metadata_changed(["site/docs/publication.json"]))
        self.assertFalse(MODULE.publication_metadata_changed(["site/docs/index.html"]))


if __name__ == "__main__":
    unittest.main()
