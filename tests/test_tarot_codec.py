import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from tarot_codec import DrawCodeError, decode, encode, enrich  # noqa: E402


class TarotCodecTests(unittest.TestCase):
    def test_round_trip_three_cards(self):
        cards = [{"id": 1, "reversed": False}, {"id": 18, "reversed": True}, {"id": 9, "reversed": False}]
        code = encode("S3", cards)
        self.assertEqual(code, "TC1-S3-02150J-YZ6")
        self.assertEqual(decode(code)["cards"], [
            {"id": 1, "reversed": False, "orientation": "upright"},
            {"id": 18, "reversed": True, "orientation": "reversed"},
            {"id": 9, "reversed": False, "orientation": "upright"},
        ])

    def test_one_card_spread(self):
        self.assertEqual(decode(encode("F1", [{"id": 77, "reversed": True}]))["cards"][0]["id"], 77)

    def test_checksum_error(self):
        code = encode("S3", [{"id": 0}, {"id": 1}, {"id": 2}])
        with self.assertRaisesRegex(DrawCodeError, "checksum"):
            decode(code[:-1] + ("0" if code[-1] != "0" else "1"))

    def test_duplicate_card_error(self):
        with self.assertRaisesRegex(DrawCodeError, "duplicate"):
            encode("S3", [{"id": 2}, {"id": 2}, {"id": 3}])

    def test_deck_has_stable_78_ids(self):
        data = json.loads((ROOT / "references" / "deck.json").read_text(encoding="utf-8"))
        self.assertEqual(data["card_count"], 78)
        self.assertEqual([card["id"] for card in data["cards"]], list(range(78)))
        self.assertEqual(len({card["key"] for card in data["cards"]}), 78)

    def test_enrich_uses_deck_table(self):
        result = enrich(decode(encode("F1", [{"id": 18, "reversed": True}])), ROOT / "references" / "deck.json")
        self.assertEqual(result["cards"][0]["name_zh"], "月亮")


if __name__ == "__main__":
    unittest.main()
