"""Tests for the local tarot server lifecycle."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "tarot-confessional"
SERVE = SKILL / "scripts" / "serve.py"


class ServeLifecycleTests(unittest.TestCase):
    def test_server_exits_after_idle_timeout(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SERVE),
                "--skill-dir",
                str(SKILL),
                "--idle-timeout",
                "1",
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        if "Operation not permitted" in result.stderr:
            self.skipTest("test environment does not permit TCP port binding")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("draw", payload)
        self.assertEqual(payload["idle_timeout_seconds"], 1)


if __name__ == "__main__":
    unittest.main()
