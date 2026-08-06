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

    def test_valid_static_assets_contract_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_valid_contract(root)
            self.assertEqual([], self.check(root))

    def test_worker_name_and_asset_directory_are_fixed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_valid_contract(root)
            (root / "wrangler.jsonc").write_text(
                json.dumps(
                    {
                        "name": "wrong-worker",
                        "compatibility_date": "2026-08-06",
                        "assets": {"directory": "./dist"},
                    }
                ),
                encoding="utf-8",
            )
            errors = self.check(root)
            self.assertIn("Cloudflare Worker name must be exactly 'dubnium'", errors)
            self.assertIn("Cloudflare assets.directory must resolve to './site/'", errors)

    def test_wrangler_version_must_be_exact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_valid_contract(root)
            package = json.loads((root / "package.json").read_text(encoding="utf-8"))
            package["devDependencies"]["wrangler"] = "^4.114.0"
            (root / "package.json").write_text(json.dumps(package), encoding="utf-8")
            self.assertIn(
                "Wrangler must be pinned to an exact semantic version",
                self.check(root),
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


if __name__ == "__main__":
    unittest.main()
