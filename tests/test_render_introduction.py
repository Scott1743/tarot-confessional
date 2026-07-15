"""Tests for the introduction-page version renderer."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_introduction import (  # noqa: E402
    collect_substitutions,
    latest_release_entry,
    render,
)

TEMPLATE = ROOT / "introduction" / "index.html"


class SubstitutionCollectionTests(unittest.TestCase):
    def test_collect_for_requested_version(self):
        subs = collect_substitutions(ROOT / "skills" / "tarot-confessional", "0.1.1")
        self.assertEqual(subs["VERSION"], "0.1.1")
        self.assertEqual(subs["PROTOCOL"], "TC1")
        self.assertEqual(subs["DECK_SIZE"], "78")
        self.assertEqual(subs["RELEASE_DATE"], "2026-07-12")
        self.assertIn("build_draw_page", subs["CHANGELOG_SUMMARY"])

    def test_unknown_version_falls_back_to_latest(self):
        # When the requested version isn't in CHANGELOG yet, fall back to the
        # most recent entry so the dist page is never missing required fields.
        date, bullets = latest_release_entry((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), "9.9.9")
        self.assertEqual(date, "2026-07-15")
        self.assertTrue(bullets)


class RenderTests(unittest.TestCase):
    def test_introduction_presents_2_1_memory_flow_and_install(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn('id="echo"', template)
        self.assertIn("记忆不是默认开启的门", template)
        self.assertIn("tarot-confessional-2.1.1.zip", template)
        self.assertIn("Scott1743/tarot-confessional/skills/tarot-confessional", template)

    def test_template_placeholders_match_substitution_keys(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        placeholders = set(re.findall(r"\{\{([A-Z_]+)\}\}", template))
        subs = collect_substitutions(ROOT / "skills" / "tarot-confessional", "0.1.1")
        self.assertEqual(placeholders - set(subs), set(), f"unfilled placeholders: {placeholders - set(subs)}")

    def test_render_substitutes_every_placeholder(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        subs = {"VERSION": "9.9.9", "RELEASE_DATE": "2099-01-01", "PROTOCOL": "TCX", "DECK_SIZE": "0", "CHANGELOG_SUMMARY": "test"}
        rendered, leftover = render(template, subs)
        self.assertEqual(leftover, [])
        self.assertIn("9.9.9", rendered)
        self.assertNotIn("{{VERSION}}", rendered)
        self.assertNotIn("{{DECK_SIZE}}", rendered)
        self.assertIn("2099-01-01", rendered)


if __name__ == "__main__":
    unittest.main()
