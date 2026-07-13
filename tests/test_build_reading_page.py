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
            self.assertGreaterEqual(html.count("data:image/jpeg;base64,"), 5)


if __name__ == "__main__":
    unittest.main()
