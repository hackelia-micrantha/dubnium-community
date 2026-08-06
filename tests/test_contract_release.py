from __future__ import annotations

import io
import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest

from scripts.build_contract_release import build
from scripts.verify_contract_release import safe_members, verify

ROOT = Path(__file__).resolve().parents[1]


class ContractReleaseTests(unittest.TestCase):
    def test_build_is_byte_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first"
            second = Path(temp) / "second"
            build(first, "0123456789abcdef0123456789abcdef01234567")
            build(second, "0123456789abcdef0123456789abcdef01234567")
            self.assertEqual(
                {path.name: path.read_bytes() for path in first.iterdir()},
                {path.name: path.read_bytes() for path in second.iterdir()},
            )

    def test_consumer_verifies_and_runs_conformance(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "dist"
            build(output, "0123456789abcdef0123456789abcdef01234567")
            verify(output)

    def test_checksum_tampering_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "dist"
            paths = build(output, "0123456789abcdef0123456789abcdef01234567")
            archive = next(path for path in paths if path.name.endswith(".tar.gz"))
            archive.write_bytes(archive.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                verify(output, run_tests=False)

    def test_archive_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "bad.tar.gz"
            with tarfile.open(archive, mode="w:gz") as tar:
                info = tarfile.TarInfo("bundle/../../escape")
                info.size = 1
                tar.addfile(info, io.BytesIO(b"x"))
            with self.assertRaisesRegex(ValueError, "unsafe archive path"):
                safe_members(archive)

    def test_manifest_contains_no_private_coordinates(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "dist"
            build(output, "0123456789abcdef0123456789abcdef01234567")
            manifest_path = next(output.glob("*.manifest.json"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            text = json.dumps(manifest)
            self.assertNotIn("ryjen/dubnium", text)
            self.assertNotIn("private", text.lower())
            self.assertEqual("capability-gateway-v1alpha", manifest["contract_profile"])


if __name__ == "__main__":
    unittest.main()
