"""Validation tests for the paired mmx deck generation plan."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "gen_scripts" / "generate_deck_mmx.py"
SPEC = importlib.util.spec_from_file_location("generate_deck_mmx", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DeckGenerationPlanTests(unittest.TestCase):
    def test_plan_has_all_78_ordered_cards(self):
        plan, cards = MODULE.load_and_validate_plan()
        self.assertEqual(plan["deck_size"], 78)
        self.assertEqual([card["id"] for card in cards], list(range(78)))

    def test_every_card_has_pair_language(self):
        plan, cards = MODULE.load_and_validate_plan()
        for card in cards:
            with self.subTest(card=card["key"]):
                self.assertTrue(card["shared_anchor"])
                self.assertTrue(card["upright_scene"])
                self.assertTrue(card["reversed_transform"])
                self.assertTrue(plan["animal_cast"][str(card["id"])])

    def test_style_allows_human_archetypes(self):
        plan, _cards = MODULE.load_and_validate_plan()
        style = plan["style"]["prompt"].lower()
        self.assertIn("sacred human archetype", style)
        self.assertIn("animal protagonists", style)

    def test_style_locks_cobalt_gilded_ceremonial_language(self):
        plan, _cards = MODULE.load_and_validate_plan()
        style = plan["style"]["prompt"].lower()
        for phrase in (
            "saturated cobalt and ultramarine blue",
            "antique gold linework",
            "strong centered symmetry",
            "dense gilded geometry",
            "fine graceful ink line",
            "flat jewel-colored planes",
            "blank title plaque",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, style)
        self.assertIn("no readable words", style)

    def test_prompts_preserve_human_roles_and_normalize_cultural_cues(self):
        plan, cards = MODULE.load_and_validate_plan()
        queen = MODULE.upright_prompt(plan, cards[48]).lower()
        self.assertIn("compassionate woman", queen)
        self.assertNotIn("porcelain", queen)
        self.assertNotIn("lotus", queen)
        self.assertNotIn("animal character", queen)

    def test_role_translation_rules_cover_three_subject_types(self):
        plan, _cards = MODULE.load_and_validate_plan()
        rules = plan["role_translation"]
        self.assertIn("object is the protagonist", rules["object_led"])
        self.assertIn("human archetypes", rules["anthropomorphic_roles"])
        self.assertIn("human gesture", rules["virtue_cards"])
        self.assertIn("crowned lion emperor", plan["animal_cast_overrides"]["4"])

    def test_suit_objects_and_requested_cast_overrides_are_locked(self):
        plan, _cards = MODULE.load_and_validate_plan()
        contracts = plan["suit_object_contract"]
        self.assertIn("flowering wooden staffs", contracts["wands"])
        self.assertIn("chalices", contracts["cups"])
        self.assertIn("straight swords", contracts["swords"])
        self.assertIn("golden pentacles", contracts["pentacles"])
        overrides = plan["animal_cast_overrides"]
        self.assertIn("object-led great eight-point star", overrides["17"])
        self.assertIn("object-led full moon", overrides["18"])
        self.assertIn("object-led radiant sun disc", overrides["19"])
        self.assertIn("antlered doe queen", overrides["34"])
        self.assertIn("regal leopard queen", overrides["48"])

    def test_lighting_avoids_default_backlight(self):
        plan, _cards = MODULE.load_and_validate_plan()
        style = plan["style"]["prompt"].lower()
        self.assertIn("soft frontal overcast daylight", plan["lighting_overrides"]["4"])

    def test_reversed_command_uses_matching_upright_reference(self):
        plan, cards = MODULE.load_and_validate_plan()
        card = cards[0]
        reference = ROOT / "tmp" / "upright" / MODULE.filename(card)
        command = MODULE.build_command(
            plan=plan,
            card=card,
            orientation="reversed",
            output_path=ROOT / "tmp" / "reversed" / MODULE.filename(card),
            upright_reference=reference,
        )
        self.assertIn("--subject-ref", command)
        self.assertIn(f"type=character,image={reference.resolve()}", command)
        self.assertIn("--non-interactive", command)
        self.assertIn("--quiet", command)
        self.assertIn("--output", command)
        self.assertIn("json", command)
        self.assertIn("--out", command)
        self.assertNotIn("--prompt-optimizer", command)

    def test_mmx_prompts_stay_below_length_limit(self):
        plan, cards = MODULE.load_and_validate_plan()
        for card in cards:
            with self.subTest(card=card["key"]):
                self.assertLess(len(MODULE.upright_prompt(plan, card)), 1500)
                self.assertLess(len(MODULE.reversed_prompt(plan, card)), 1500)

    def test_pair_uses_same_seed(self):
        plan, cards = MODULE.load_and_validate_plan()
        card = cards[1]
        upright_path = ROOT / "tmp" / "upright" / MODULE.filename(card)
        upright = MODULE.build_command(plan=plan, card=card, orientation="upright", output_path=upright_path)
        reversed_command = MODULE.build_command(
            plan=plan,
            card=card,
            orientation="reversed",
            output_path=ROOT / "tmp" / "reversed" / MODULE.filename(card),
            upright_reference=upright_path,
        )
        self.assertEqual(upright[upright.index("--seed") + 1], reversed_command[reversed_command.index("--seed") + 1])

    def test_card_identity_matches_canonical_deck(self):
        _plan, cards = MODULE.load_and_validate_plan()
        deck = json.loads((ROOT / "references" / "deck.json").read_text(encoding="utf-8"))["cards"]
        self.assertEqual([(c["id"], c["key"], c["name_zh"]) for c in cards], [(c["id"], c["key"], c["name_zh"]) for c in deck])

    def test_human_plan_lists_every_card_once(self):
        text = (ROOT / "assets" / "gen_scripts" / "deck_generation_plan.md").read_text(encoding="utf-8")
        rows = [line for line in text.splitlines() if line.startswith("| ") and line[2:4].isdigit()]
        self.assertEqual(len(rows), 78)
        self.assertEqual([int(line.split("|")[1].strip()) for line in rows], list(range(78)))


if __name__ == "__main__":
    unittest.main()
