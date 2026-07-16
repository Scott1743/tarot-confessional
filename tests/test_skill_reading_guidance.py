"""Contract tests for the agent-facing reading instructions."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "tarot-confessional" / "SKILL.md"
GUIDANCE = ROOT / "skills" / "tarot-confessional" / "references" / "reading-guidance.md"


def test_skill_requires_a_direct_but_calibrated_answer():
    text = SKILL.read_text(encoding="utf-8")
    assert "先回答用户实际问的问题" in text
    assert "核心答复" in text
    assert "明确不等于绝对" in text


def test_guidance_keeps_direct_answers_inside_safety_boundaries():
    text = GUIDANCE.read_text(encoding="utf-8")
    assert "Answer the question directly" in text
    assert "不声称知道第三方未表达的想法" in text
    assert "这件事不适合依据牌面判断或行动" in text
