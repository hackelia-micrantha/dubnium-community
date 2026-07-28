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
                    "source_repository": "ryjen/dubnium",
                    "source_commit": "a" * 40,
                    "generator": "mdbook 0.4.52",
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

    def test_rejects_private_repository_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_book(root, '<a href="https://github.com/ryjen/dubnium/edit/main/docs/external/README.md">edit</a>')
            errors = MODULE.validate(root)
            self.assertTrue(any("private repository URL" in error for error in errors))

    def test_rejects_internal_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_book(root, "docs/internal/runbooks/secrets.md")
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

    def test_rejects_malformed_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = self.make_book(root)
            metadata = json.loads((docs / "publication.json").read_text(encoding="utf-8"))
            metadata["source_commit"] = "main"
            (docs / "publication.json").write_text(json.dumps(metadata), encoding="utf-8")
            errors = MODULE.validate(root)
            self.assertTrue(any("full lowercase SHA-1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
