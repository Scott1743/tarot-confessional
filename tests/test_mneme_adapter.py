"""Tests for the optional Mneme bridge without touching a real bundle."""

from __future__ import annotations

import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stdout
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

    def test_find_cli_discovers_workbuddy_installation(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            cli = home / ".workbuddy" / "skills" / "mneme" / "scripts" / "mneme.py"
            cli.parent.mkdir(parents=True)
            cli.write_text("# test", encoding="utf-8")
            self.assertEqual(MODULE.find_cli(home=home), cli)

    def test_find_cli_discovers_agents_installation(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            cli = home / ".agents" / "skills" / "mneme" / "scripts" / "mneme.py"
            cli.parent.mkdir(parents=True)
            cli.write_text("# test", encoding="utf-8")
            self.assertEqual(MODULE.find_cli(home=home), cli)

    def test_resolve_bundle_reads_mneme_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "wiki"
            bundle.mkdir()
            config = root / "config.toml"
            config.write_text(f'bundle_path = "{bundle}"\n', encoding="utf-8")
            self.assertEqual(MODULE.resolve_bundle(config=config), bundle)

    def test_runtime_options_work_before_or_after_subcommand(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cli = root / "scripts" / "mneme.py"
            cli.parent.mkdir()
            cli.write_text("# test", encoding="utf-8")
            for argv in (
                ["--skill-dir", str(root), "capabilities"],
                ["capabilities", "--skill-dir", str(root)],
            ):
                with self.subTest(argv=argv), redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(MODULE.main(argv), 0)
                    self.assertIn('"status": "available"', output.getvalue())


if __name__ == "__main__":
    unittest.main()
