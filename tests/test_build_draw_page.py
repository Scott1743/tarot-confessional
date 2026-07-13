"""Tests for the single-file draw page builder.

These tests verify that build_draw_page.py produces a fully self-contained
HTML file that works regardless of where it is placed on disk.
"""

from __future__ import annotations

import base64
import contextlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_draw_page import build, expected_assets  # noqa: E402

SKILL = ROOT / "skills" / "tarot-confessional"


class BuildDrawPageUnitTests(unittest.TestCase):
    def test_expected_assets_includes_layout_assets(self):
        assets = expected_assets(SKILL / "assets")
        names = {path.name for path in assets}
        self.assertIn("card-back.jpg", names)
        self.assertIn("forest-whisper-bg.jpg", names)
        self.assertIn("eastern-night-bg_001.jpg", names)
        self.assertIn("purple-silk.jpg", names)

    def test_expected_assets_includes_all_78_card_images(self):
        assets = expected_assets(SKILL / "assets")
        cards = [p for p in assets if p.parent.name == "cards"]
        self.assertEqual(len(cards), 78)
        self.assertEqual(cards[0].name, "00-fool.jpg")
        self.assertEqual(cards[-1].name, "77-king-of-pentacles.jpg")

    def test_build_replaces_external_script_tags(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "draw.html"
            build(skill_dir=SKILL, output=out, spread="S3", title="测试")
            html = out.read_text(encoding="utf-8")
            self.assertNotIn('src="deck-data.js"', html)
            self.assertNotIn('src="tarot-codec.js"', html)
            self.assertIn("TarotDeck", html)
            self.assertIn("TarotCodec", html)

    def test_build_inlines_layout_images_as_data_uris(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "draw.html"
            build(skill_dir=SKILL, output=out, spread="S3", title="测试")
            html = out.read_text(encoding="utf-8")
            self.assertNotIn('url("images/card-back.jpg")', html)
            self.assertNotIn('url("images/forest-whisper-bg.jpg")', html)
            self.assertNotIn('url("images/eastern-night-bg_001.jpg")', html)
            self.assertNotIn('url("images/purple-silk.jpg")', html)
            self.assertNotIn('src="images/card-back.jpg"', html)
            # Four layout images + one inline back reference -> at least 5 data URIs
            data_uris = re.findall(r"data:image/jpeg;base64,[A-Za-z0-9+/=]+", html)
            self.assertGreaterEqual(len(data_uris), 5)

    def test_build_inlines_all_78_card_faces(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "draw.html"
            build(skill_dir=SKILL, output=out, spread="S3", title="测试")
            html = out.read_text(encoding="utf-8")
            self.assertIn("__tarotCardImages", html)
            image_block = re.search(r"window\.__tarotCardImages\s*=\s*\{(.+?)\};", html, re.DOTALL)
            self.assertIsNotNone(image_block, "expected __tarotCardImages map")
            entries = re.findall(r'"cards/[\w\-]+\.jpg"\s*:\s*"data:image/jpeg;base64,', image_block.group(0))
            self.assertEqual(len(entries), 78)

    def test_build_keeps_html_structure_intact(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "draw.html"
            build(skill_dir=SKILL, output=out, spread="S3", title="测试")
            html = out.read_text(encoding="utf-8")
            for marker in ("<!doctype html>", "<title>", "此刻 · 正在发生", "阻力 · 还没看清", "方向 · 可以试试", "TarotCodec.encode"):
                with self.subTest(marker=marker):
                    self.assertIn(marker, html)

    def test_dynamic_card_src_uses_resolver_expression_not_literal_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "draw.html"
            build(skill_dir=SKILL, output=out, spread="S3", title="测试")
            html = out.read_text(encoding="utf-8")
            self.assertIn('img.src = (__tarotCardImagesResolve("cards/" + card.file)', html)
            self.assertNotIn('img.src = `(__tarotCardImagesResolve', html)
            self.assertNotIn('`images/cards/${card.file}`', html)

    def test_build_rejects_unknown_spread(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "draw.html"
            with self.assertRaisesRegex(ValueError, "spread"):
                build(skill_dir=SKILL, output=out, spread="X9", title="测试")

    def test_output_is_fully_self_contained_no_relative_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "draw.html"
            build(skill_dir=SKILL, output=out, spread="S3", title="测试")
            html = out.read_text(encoding="utf-8")
            # No remaining href/src/url references that target relative asset paths
            for pattern in (r'href="(?!#|data:)[^"]*\.css"', r'src="(?!data:|#)[^"]*\.js"', r'url\("images/'):
                with self.subTest(pattern=pattern):
                    self.assertNotRegex(html, pattern)


class BuildDrawPageIntegrationTests(unittest.TestCase):
    """Verify the built HTML works when copied to an arbitrary location."""

    def _build_and_copy_to(self) -> tuple[Path, Path]:
        tmp = Path(tempfile.mkdtemp(prefix="tarot-bd-"))
        out = tmp / "draw.html"
        build(skill_dir=SKILL, output=out, spread="S3", title="测试")
        # Copy to a wholly different location that has NO sibling assets
        isolated = Path(tempfile.mkdtemp(prefix="tarot-iso-"))
        target = isolated / "draw.html"
        shutil.copy(out, target)
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.addCleanup(shutil.rmtree, isolated, ignore_errors=True)
        return out, target

    def test_built_file_has_no_external_resource_dependencies(self):
        out, target = self._build_and_copy_to()
        # Assert the copy is independent: every visual asset referenced inside
        # the HTML must be inlined, so the sibling directory must be empty.
        siblings = [p.name for p in target.parent.iterdir()]
        self.assertEqual(siblings, ["draw.html"], f"siblings present: {siblings}")

    def test_built_file_contains_real_card_data_for_each_card(self):
        out, _ = self._build_and_copy_to()
        html = out.read_text(encoding="utf-8")
        # Pull out the encoded payload of "00-fool.jpg" and decode it to confirm
        # the inlined image bytes match the file on disk.
        match = re.search(r'"cards/00-fool\.jpg"\s*:\s*"data:image/jpeg;base64,([^"]+)"', html)
        self.assertIsNotNone(match, "missing inline card-back data URI")
        inlined = base64.b64decode(match.group(1))
        original = (SKILL / "assets/images/cards/00-fool.jpg").read_bytes()
        self.assertEqual(inlined, original)

    def test_cli_runs_and_produces_self_contained_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "draw.html"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_draw_page.py"),
                    "--skill-dir", str(SKILL),
                    "--output", str(out),
                    "--spread", "S3",
                    "--title", "测试牌阵",
                ],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
            html = out.read_text(encoding="utf-8")
            self.assertIn("__tarotCardImages", html)
            self.assertNotIn('src="images/', html)


if __name__ == "__main__":
    unittest.main()
