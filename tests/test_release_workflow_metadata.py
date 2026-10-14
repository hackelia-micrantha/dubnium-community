"""Exercise the actual tag-publication shell without GitHub/network effects."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/release-contracts.yml"


def publication_script() -> str:
    text = WORKFLOW.read_text(encoding="utf-8")
    step = text.split("      - name: Publish immutable GitHub release\n", 1)[1]
    block = step.split("        run: |\n", 1)[1].split("\n  verify-published-release:", 1)[0]
    return "\n".join(line[10:] for line in block.splitlines() if line.strip())


class ReleaseMetadataTests(unittest.TestCase):
    def test_published_prerelease_flag_follows_semver_suffix(self) -> None:
        script = publication_script()
        self.assertIn("gh release create", script)
        self.assertIn("--verify-tag", script)
        self.assertIn('"\u0024{release_flags[@]}"', script)
        cases = (
            ("0.1.0-alpha.1", True),
            ("1.0.0-rc.1", True),
            ("1.0.0", False),
        )
        for version, expected_prerelease in cases:
            with self.subTest(version=version), tempfile.TemporaryDirectory() as temp:
                work = Path(temp)
                (work / "release").mkdir()
                (work / "release/contract-bundle-version.txt").write_text(version + "\n")
                (work / "dist").mkdir()
                (work / "dist/SHA256SUMS").write_text("fake local argument only\n")
                argfile = work / "gh-args.txt"
                mock_gh = 'gh() { printf "%s\\n" "$@" > "$GH_ARGS_FILE"; }'
                result = subprocess.run(
                    ["bash", "-c", mock_gh + "\n" + script],
                    cwd=work,
                    text=True,
                    capture_output=True,
                    check=False,
                    env={**os.environ,
                         "GH_ARGS_FILE": str(argfile),
                         "GITHUB_REF_NAME": "contract-v" + version,
                         "GITHUB_REPOSITORY": "hackelia-micrantha/dubnium-community"},
                )
                self.assertEqual(0, result.returncode, result.stderr)
                args = argfile.read_text().splitlines()
                self.assertEqual(["release", "create", "contract-v" + version], args[:3])
                self.assertEqual(expected_prerelease, "--prerelease" in args)
                self.assertIn("--verify-tag", args)


if __name__ == "__main__":
    unittest.main()
