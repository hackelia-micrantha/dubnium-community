from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_repository_policy", ROOT / "scripts" / "check_repository_policy.py"
)
assert SPEC and SPEC.loader
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)


class CloudflareBuildPolicyTests(unittest.TestCase):
    def write_valid_contract(self, root: Path) -> None:
        (root / "site").mkdir(parents=True)
        (root / "site" / "index.html").write_text("<!doctype html>\n", encoding="utf-8")
        (root / "wrangler.jsonc").write_text(
            json.dumps(
                {
                    "name": "dubnium",
                    "compatibility_date": "2026-08-06",
                    "assets": {"directory": "./site/"},
                }
            ),
            encoding="utf-8",
        )
        (root / "package.json").write_text(
            json.dumps(
                {
                    "name": "dubnium-community-site",
                    "private": True,
                    "version": "0.0.0",
                    "scripts": {
                        "deploy": "wrangler deploy",
                        "preview": "wrangler versions upload",
                    },
                    "devDependencies": {"wrangler": "4.114.0"},
                }
            ),
            encoding="utf-8",
        )

    def check(self, root: Path) -> list[str]:
        errors: list[str] = []
        with patch.object(policy, "ROOT", root):
            policy.check_cloudflare_build(errors)
        return errors

    def read_object(self, path: Path) -> dict[str, object]:
        value = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(value, dict)
        return value

    def write_object(self, path: Path, value: dict[str, object]) -> None:
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_valid_static_assets_contract_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_valid_contract(root)
            self.assertEqual([], self.check(root))

    def test_worker_name_and_asset_directory_are_fixed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_valid_contract(root)
            wrangler = self.read_object(root / "wrangler.jsonc")
            wrangler["name"] = "wrong-worker"
            wrangler["assets"] = {"directory": "./dist"}
            self.write_object(root / "wrangler.jsonc", wrangler)
            errors = self.check(root)
            self.assertIn("Cloudflare Worker name must be exactly 'dubnium'", errors)
            self.assertIn("Cloudflare assets.directory must resolve to './site/'", errors)

    def test_compatibility_date_is_fixed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_valid_contract(root)
            wrangler = self.read_object(root / "wrangler.jsonc")
            wrangler["compatibility_date"] = "2026-08-07"
            self.write_object(root / "wrangler.jsonc", wrangler)
            self.assertIn(
                "Cloudflare compatibility_date must be exactly '2026-08-06'",
                self.check(root),
            )

    def test_wrangler_version_is_fixed_and_exact(self) -> None:
        for version in ("^4.114.0", "4.115.0"):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_valid_contract(root)
                package = self.read_object(root / "package.json")
                dependencies = package["devDependencies"]
                assert isinstance(dependencies, dict)
                dependencies["wrangler"] = version
                self.write_object(root / "package.json", package)
                self.assertIn(
                    "Wrangler must be pinned exactly to 4.114.0",
                    self.check(root),
                )

    def test_package_privacy_and_deploy_commands_are_fixed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_valid_contract(root)
            package = self.read_object(root / "package.json")
            package["private"] = False
            package["scripts"] = {
                "deploy": "wrangler deploy --env production",
                "preview": "wrangler dev",
            }
            self.write_object(root / "package.json", package)
            errors = self.check(root)
            self.assertIn("Cloudflare package must be private", errors)
            self.assertIn("package.json deploy script must be 'wrangler deploy'", errors)
            self.assertIn(
                "package.json preview script must be 'wrangler versions upload'",
                errors,
            )

    def test_site_entry_point_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_valid_contract(root)
            (root / "site" / "index.html").unlink()
            self.assertIn(
                "missing Cloudflare static asset entry point: site/index.html",
                self.check(root),
            )

    def test_invalid_json_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_valid_contract(root)
            (root / "package.json").write_text("{invalid", encoding="utf-8")
            self.assertTrue(
                any(error.startswith("invalid package.json:") for error in self.check(root))
            )


if __name__ == "__main__":
    unittest.main()
