"""Tests for the self-contained reading page builder."""

from __future__ import annotations

import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "tarot-confessional"
SCRIPT = SKILL / "scripts" / "build_reading_page.py"
SPEC = importlib.util.spec_from_file_location("build_reading_page", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def reading_data() -> dict:
    cards = []
    for image, name, orientation, position in (
        ("01-magician.jpg", "魔术师", "正位", "现状 · 此刻之势"),
        ("18-moon.jpg", "月亮", "逆位", "阻力 · 未明之处"),
        ("09-hermit.jpg", "隐者", "正位", "方向 · 可以尝试"),
    ):
        cards.append({
            "image": image,
            "name": name,
            "orientation": orientation,
            "position": position,
            "title": f"{name}的提示",
            "content": "<p>测试解读。</p>",
        })
    return {
        "spread_type": "三张行动牌阵",
        "title": "测试阅读",
        "date": "二〇二六年七月十三日",
        "positions": "现状 · 阻力 · 方向",
        "question": "测试问题",
        "cards": cards,
        "synthesis": {"title": "合观", "content": "<blockquote>测试合观。</blockquote>"},
        "actions": {"title": "可行之事", "items": ["行动一", "行动二"]},
        "questions": {"title": "留待自问", "items": ["问题一", "问题二"]},
        "disclaimer": "仅用于自我反思。",
    }


class BuildReadingPageTests(unittest.TestCase):
    def test_dynamic_card_images_are_base64_after_rendering(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "reading.html"
            MODULE.build(skill_dir=SKILL, output=output, data=reading_data())
            html = output.read_text(encoding="utf-8")
            self.assertNotIn('src="images/cards/', html)
            self.assertNotIn('src="images/cards-reversed/', html)
            cards = re.findall(r'<img src="data:image/jpeg;base64,[A-Za-z0-9+/=]+" alt="(?:魔术师正位|月亮逆位|隐者正位)"', html)
            self.assertEqual(len(cards), 3)

    def test_layout_images_are_base64_and_file_is_standalone(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "reading.html"
            MODULE.build(skill_dir=SKILL, output=output, data=reading_data())
            html = output.read_text(encoding="utf-8")
            self.assertNotIn('url("images/', html)
            self.assertEqual(html.count("data:image/jpeg;base64,"), 4)

    def test_generated_page_uses_forest_whispers_language_and_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "reading.html"
            MODULE.build(skill_dir=SKILL, output=output, data=reading_data())
            html = output.read_text(encoding="utf-8")
            self.assertIn("森林密语 · 林间回信", html)
            self.assertIn("风里的共同方向", html)
            self.assertIn('class="entry-marker"', html)
            self.assertNotIn("塔罗树洞 · 阅读档案", html)

    def test_closing_sections_render_one_heading_when_title_matches_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "reading.html"
            MODULE.build(skill_dir=SKILL, output=output, data=reading_data())
            html = output.read_text(encoding="utf-8")
            self.assertEqual(html.count('<h2 class="section-heading">可行之事</h2>'), 1)
            self.assertEqual(html.count('<h2 class="section-heading">留待自问</h2>'), 1)
            self.assertNotIn('<div class="label">可行之事</div>', html)

    def test_no_mneme_reading_has_a_lightweight_memory_invite(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "reading.html"
            MODULE.build(skill_dir=SKILL, output=output, data=reading_data())
            html = output.read_text(encoding="utf-8")
            self.assertIn("想把这次的感受留给未来的自己吗？", html)
            self.assertNotIn('<button class="memory-action" type="button" data-mneme-dream>', html)
            self.assertIn("<!-- mneme-dream-action -->", html)

    def test_mneme_reading_renders_sources_and_dream_button(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "reading.html"
            data = reading_data()
            data["memory"] = {
                "enabled": True,
                "title": "旧日的记录也照见了这一步",
                "guidance": "过去只作参照，不替你定义现在。",
                "sources": [{"date": "2026-07-02", "title": "工作边界", "path": "concepts/work-boundaries.md"}],
                "dream_enabled": True,
            }
            MODULE.build(skill_dir=SKILL, output=output, data=data)
            html = output.read_text(encoding="utf-8")
            self.assertIn("密语回响", html)
            self.assertIn("concepts/work-boundaries.md", html)
            self.assertIn('data-mneme-dream', html)

    def test_mneme_metadata_is_html_escaped(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "reading.html"
            data = reading_data()
            data["memory"] = {
                "enabled": True,
                "title": "<script>bad()</script>",
                "guidance": "现在 < 过去",
                "sources": [{"date": "today", "title": "<b>note</b>", "path": "concepts/a&b.md"}],
            }
            MODULE.build(skill_dir=SKILL, output=output, data=data)
            html = output.read_text(encoding="utf-8")
            self.assertNotIn("<script>bad()</script>", html)
            self.assertIn("&lt;script&gt;bad()&lt;/script&gt;", html)
            self.assertIn("concepts/a&amp;b.md", html)


if __name__ == "__main__":
    unittest.main()
