from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "verify_public_book_artifact.py"
SPEC = importlib.util.spec_from_file_location("verify_public_book_artifact", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class PublicBookArtifactTests(unittest.TestCase):
    def test_normalizes_search_index_filename_and_json_key_order(self) -> None:
        prefix = b"window.search = Object.assign(window.search, JSON.parse('"
        suffix = b"'));"
        committed = {
            "index.html": b'<script src="searchindex-a1.js"></script>',
            "searchindex-a1.js": prefix + b'{"index":{"b":2,"a":1},"doc_urls":["status.html"]}' + suffix,
            "publication.json": b'{"schema_version":2,"generator":"mdbook 0.5.4","generated_at":"2026-09-01T00:00:00Z"}',
        }
        generated = {
            "index.html": b'<script src="searchindex-b2.js"></script>',
            "searchindex-b2.js": prefix + b'{"doc_urls":["status.html"],"index":{"a":1,"b":2}}' + suffix,
            "publication.json": b'{"schema_version":2,"generator":"mdbook 0.5.4","generated_at":"2026-09-02T00:00:00Z"}',
        }
        self.assertEqual([], MODULE.compare_artifacts(committed, generated))

    def test_rejects_semantic_search_index_changes(self) -> None:
        prefix = b"window.search = Object.assign(window.search, JSON.parse('"
        suffix = b"'));"
        committed = {"searchindex-a1.js": prefix + b'{"doc_urls":["status.html"]}' + suffix}
        generated = {"searchindex-b2.js": prefix + b'{"doc_urls":["community.html"]}' + suffix}
        errors = MODULE.compare_artifacts(committed, generated)
        self.assertTrue(any("searchindex-canonical.js" in error for error in errors))

    def test_rejects_other_generated_content_changes(self) -> None:
        errors = MODULE.compare_artifacts({"status.html": b"old"}, {"status.html": b"new"})
        self.assertTrue(any("status.html" in error for error in errors))

if __name__ == "__main__":
    unittest.main()
