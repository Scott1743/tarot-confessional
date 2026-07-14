"""Tests for the optional Mneme bridge without touching a real bundle."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "tarot-confessional" / "scripts" / "mneme_adapter.py"
SPEC = importlib.util.spec_from_file_location("mneme_adapter", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MnemeAdapterTests(unittest.TestCase):
    def test_capabilities_are_unavailable_without_a_skill(self):
        self.assertEqual(MODULE.capabilities("/definitely/not/mneme")["status"], "unavailable")

    def test_find_cli_accepts_only_the_skill_entry_point(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertIsNone(MODULE.find_cli(root))
            cli = root / "scripts" / "mneme.py"
            cli.parent.mkdir()
            cli.write_text("# test", encoding="utf-8")
            self.assertEqual(MODULE.find_cli(root), cli)


if __name__ == "__main__":
    unittest.main()
