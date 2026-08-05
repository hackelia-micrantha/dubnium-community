from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "check_contract_tree.py"
SPEC = importlib.util.spec_from_file_location("check_contract_tree", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ContractTreeTests(unittest.TestCase):
    def make_root(self, directory: str) -> Path:
        root = Path(directory)
        for name in ("spec", "schemas", "api", "examples", "changes"):
            (root / name).mkdir()
        return root

    def write_schema(self, root: Path, name: str = "request.json", extra: dict | None = None) -> Path:
        document = {
            "$schema": MODULE.JSON_SCHEMA_2020_12,
            "$id": MODULE.SCHEMA_ID_PREFIX + name,
            "type": "object",
        }
        if extra:
            document.update(extra)
        path = root / "schemas" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document), encoding="utf-8")
        return path

    def test_accepts_minimal_contract_tree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            self.write_schema(root)
            (root / "spec" / "request.md").write_text(
                "# Request\n\nStatus: experimental\nContent: normative\nCanonical source: this file\nGenerated: no\n\nA client MUST send an object.\n",
                encoding="utf-8",
            )
            (root / "api" / "openapi.json").write_text(
                json.dumps(
                    {
                        "openapi": MODULE.OPENAPI_VERSION,
                        "info": {},
                        "paths": {},
                        "components": {
                            "schemas": {
                                "Request": {"$ref": "../schemas/request.json"}
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            (root / "examples" / "request.json").write_text(
                json.dumps({"$schema": "../schemas/request.json"}),
                encoding="utf-8",
            )
            self.assertEqual([], MODULE.validate(root))

    def test_rejects_duplicate_json_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / "schemas" / "duplicate.json").write_text(
                '{"$schema":"x","$schema":"y","$id":"z"}', encoding="utf-8"
            )
            errors = MODULE.validate(root)
            self.assertTrue(any("duplicate key" in error for error in errors))

    def test_rejects_remote_schema_ref(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            self.write_schema(root, extra={"$ref": "https://example.invalid/schema.json"})
            errors = MODULE.validate(root)
            self.assertTrue(any("remote reference" in error for error in errors))

    def test_rejects_traversal_ref(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / "outside.json").write_text("{}", encoding="utf-8")
            self.write_schema(root, extra={"$ref": "../outside.json"})
            errors = MODULE.validate(root)
            self.assertTrue(any("escapes bundled root" in error for error in errors))

    def test_rejects_cyclic_file_refs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            self.write_schema(root, "a.json", {"$ref": "b.json"})
            self.write_schema(root, "b.json", {"$ref": "a.json"})
            errors = MODULE.validate(root)
            self.assertTrue(any("cyclic schema reference" in error for error in errors))

    def test_rejects_yaml_openapi_without_reviewed_parser(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / "api" / "openapi.yml").write_text("openapi: 3.1.2\n", encoding="utf-8")
            errors = MODULE.validate(root)
            self.assertTrue(any("reviewed pinned parser" in error for error in errors))

    def test_openapi_may_reference_bundled_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            self.write_schema(root)
            (root / "api" / "openapi.json").write_text(
                json.dumps(
                    {
                        "openapi": MODULE.OPENAPI_VERSION,
                        "info": {},
                        "paths": {},
                        "components": {
                            "schemas": {
                                "Request": {"$ref": "../schemas/request.json"}
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual([], MODULE.validate_openapi(root))

    def test_openapi_rejects_reference_to_unapproved_bundled_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / "private.json").write_text("{}", encoding="utf-8")
            (root / "api" / "openapi.json").write_text(
                json.dumps(
                    {
                        "openapi": MODULE.OPENAPI_VERSION,
                        "info": {},
                        "paths": {},
                        "components": {
                            "schemas": {
                                "Private": {"$ref": "../private.json"}
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            errors = MODULE.validate_openapi(root)
            self.assertTrue(any("unapproved bundled path" in error for error in errors))

    def test_rejects_unmarked_normative_spec(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / "spec" / "bad.md").write_text("# Bad\n\nClients must send data.\n", encoding="utf-8")
            errors = MODULE.validate(root)
            self.assertTrue(any("markers" in error for error in errors))
            self.assertTrue(any("BCP 14" in error for error in errors))

    def test_contract_change_requires_record(self) -> None:
        self.assertTrue(MODULE.validate_change_record(["schemas/request.json"]))
        self.assertEqual(
            [],
            MODULE.validate_change_record(["schemas/request.json", "changes/0001-request.md"]),
        )

    def test_dot_prefixed_paths_are_not_mangled(self) -> None:
        self.assertEqual(".github/workflows/test.yml", MODULE.normalize_repo_path("./.github/workflows/test.yml"))

    def test_rejects_nonfinite_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            path = root / "schemas" / "bad.json"
            path.write_text('{"value": NaN}', encoding="utf-8")
            errors = MODULE.validate(root)
            self.assertTrue(any("non-finite" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
