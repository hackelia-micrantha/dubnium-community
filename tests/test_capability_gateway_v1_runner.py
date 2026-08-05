from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
RUNNER = ROOT / "conformance" / "capability-gateway" / "v1" / "run.py"


class CapabilityGatewayV1RunnerTests(unittest.TestCase):
    def test_bundled_conformance_command(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(RUNNER)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        document = json.loads(completed.stdout)
        self.assertEqual("dubnium.capability-gateway.v1", document["contract"])
        self.assertEqual("passed", document["status"])
        self.assertFalse(document["remote_target"])
        self.assertGreaterEqual(document["check_count"], 18)


if __name__ == "__main__":
    unittest.main()
