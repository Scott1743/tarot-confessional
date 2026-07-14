"""Tests for the local tarot server lifecycle."""

from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "tarot-confessional"
SERVE = SKILL / "scripts" / "serve.py"
sys.path.insert(0, str(SKILL / "scripts"))
SPEC = importlib.util.spec_from_file_location("tarot_serve", SERVE)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ServeLifecycleTests(unittest.TestCase):
    def test_server_injects_dream_action_into_current_fallback(self):
        html = '<section class="memory-invite"><div><p>optional</p><div data-mneme-action-slot><!-- mneme-dream-action --></div></div></section>'
        activated = MODULE.enable_mneme_action(html)
        self.assertIn("data-mneme-dream", activated)
        self.assertNotIn("<!-- mneme-dream-action -->", activated)

    def test_server_injects_dream_action_into_legacy_fallback(self):
        html = '<section class="memory-invite"><div>label</div><div><p>optional</p></div></section>'
        activated = MODULE.enable_mneme_action(html)
        self.assertIn("data-mneme-dream", activated)
        self.assertIn("data-mneme-status", activated)

    def test_server_injects_dream_action_into_legacy_memory_echo(self):
        html = '<section class="memory-echo"><div>label</div><div><p>remembered</p></div></section>'
        self.assertIn("data-mneme-dream", MODULE.enable_mneme_action(html))

    def test_server_does_not_duplicate_existing_action(self):
        html = '<button data-mneme-dream>existing</button><!-- mneme-dream-action -->'
        self.assertEqual(MODULE.enable_mneme_action(html), html)

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
