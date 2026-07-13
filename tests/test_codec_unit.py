"""Unit tests for the tarot TC1 codec.

Designed with Superpowers TDD discipline:
- Each test names a single behavior.
- Tests cover valid paths, edge cases, and explicit error paths.
- Tests use real production code (no mocks).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "tarot-confessional"
sys.path.insert(0, str(SKILL / "scripts"))

from tarot_codec import (  # noqa: E402
    ALPHABET,
    DECODE_MAP,
    SPREAD_COUNTS,
    DrawCodeError,
    _decode_base32,
    _encode_base32,
    crc16_ccitt,
    decode,
    encode,
    enrich,
    load_deck,
)


class Base32Tests(unittest.TestCase):
    def test_alphabet_excludes_ambiguous_characters(self):
        for ch in "OIL":
            self.assertNotIn(ch, ALPHABET)

    def test_alphabet_has_32_unique_symbols(self):
        self.assertEqual(len(ALPHABET), 32)
        self.assertEqual(len(set(ALPHABET)), 32)

    def test_decode_map_normalizes_O_to_zero(self):
        self.assertEqual(DECODE_MAP["O"], 0)
        self.assertEqual(DECODE_MAP["I"], 1)
        self.assertEqual(DECODE_MAP["L"], 1)

    def test_encode_zero_produces_padded_zeros(self):
        self.assertEqual(_encode_base32(0, 3), "000")

    def test_encode_max_fits_in_width(self):
        self.assertEqual(_encode_base32(31, 1), ALPHABET[31])
        self.assertEqual(_encode_base32(1023, 2), ALPHABET[31] + ALPHABET[31])

    def test_encode_rejects_out_of_range(self):
        with self.assertRaises(DrawCodeError):
            _encode_base32(32, 1)
        with self.assertRaises(DrawCodeError):
            _encode_base32(-1, 1)

    def test_round_trip_base32(self):
        for value in (0, 1, 31, 32, 77, 155, 1023):
            self.assertEqual(_decode_base32(_encode_base32(value, 2)), value)

    def test_decode_rejects_invalid_character(self):
        with self.assertRaises(DrawCodeError):
            _decode_base32("!")


class Crc16CcittTests(unittest.TestCase):
    def test_known_empty_string(self):
        # CRC-16/CCITT-FALSE initial 0xFFFF, no data: 0xFFFF
        self.assertEqual(crc16_ccitt(b""), 0xFFFF)

    def test_known_ascii(self):
        # Reference value: CRC16/CCITT-FALSE of "123456789" is 0x29B1
        self.assertEqual(crc16_ccitt(b"123456789"), 0x29B1)

    def test_deterministic_across_calls(self):
        data = b"TC1-S3-02150J"
        self.assertEqual(crc16_ccitt(data), crc16_ccitt(data))


class SpreadValidationTests(unittest.TestCase):
    def test_spread_counts_match_protocol(self):
        self.assertEqual(SPREAD_COUNTS, {"F1": 1, "S3": 3, "R3": 3})

    def test_encode_rejects_unknown_spread(self):
        with self.assertRaisesRegex(DrawCodeError, "unknown spread"):
            encode("X9", [{"id": 0}])

    def test_encode_rejects_wrong_card_count(self):
        with self.assertRaisesRegex(DrawCodeError, "requires 3 cards"):
            encode("S3", [{"id": 0}, {"id": 1}])
        with self.assertRaisesRegex(DrawCodeError, "requires 1 card"):
            encode("F1", [{"id": 0}, {"id": 1}])


class CardValidationTests(unittest.TestCase):
    def test_encode_rejects_duplicate_card_ids(self):
        with self.assertRaisesRegex(DrawCodeError, "duplicate"):
            encode("S3", [{"id": 5}, {"id": 5}, {"id": 7}])

    def test_encode_rejects_out_of_range_card_id(self):
        with self.assertRaisesRegex(DrawCodeError, "out of range"):
            encode("F1", [{"id": 78}])
        with self.assertRaisesRegex(DrawCodeError, "out of range"):
            encode("F1", [{"id": -1}])

    def test_encode_rejects_upper_bound_exclusive(self):
        with self.assertRaisesRegex(DrawCodeError, "out of range"):
            encode("F1", [{"id": 78}])


class EncodeDecodeRoundTripTests(unittest.TestCase):
    def test_three_card_round_trip(self):
        cards = [{"id": 1}, {"id": 18, "reversed": True}, {"id": 9}]
        code = encode("S3", cards)
        self.assertTrue(code.startswith("TC1-S3-"))
        decoded = decode(code)
        self.assertEqual(decoded["spread"], "S3")
        self.assertEqual([c["id"] for c in decoded["cards"]], [1, 18, 9])
        self.assertEqual([c["reversed"] for c in decoded["cards"]], [False, True, False])

    def test_relationship_spread_round_trip(self):
        cards = [{"id": 0}, {"id": 36}, {"id": 50}]
        code = encode("R3", cards)
        decoded = decode(code)
        self.assertEqual(decoded["spread"], "R3")
        self.assertEqual(len(decoded["cards"]), 3)

    def test_one_card_spread(self):
        code = encode("F1", [{"id": 77, "reversed": True}])
        self.assertTrue(code.startswith("TC1-F1-"))
        self.assertEqual(decode(code)["cards"][0]["id"], 77)

    def test_orientation_string_matches_bit(self):
        result = decode(encode("S3", [{"id": 18, "reversed": True}, {"id": 0}, {"id": 1}]))
        self.assertEqual(result["cards"][0]["orientation"], "reversed")
        self.assertEqual(result["cards"][1]["orientation"], "upright")

    def test_lowercase_normalizes_to_uppercase(self):
        code = encode("F1", [{"id": 21}])
        self.assertEqual(decode(code.lower()), decode(code))


class DecodeErrorTests(unittest.TestCase):
    def test_decode_rejects_missing_prefix(self):
        with self.assertRaisesRegex(DrawCodeError, "TC1"):
            decode("XX1-S3-000102-XYZ")

    def test_decode_rejects_wrong_payload_length(self):
        with self.assertRaisesRegex(DrawCodeError, "6-character payload"):
            decode("TC1-S3-0001-XYZ")

    def test_decode_rejects_bad_checksum(self):
        bad = "TC1-S3-000102-AAA"
        with self.assertRaisesRegex(DrawCodeError, "checksum"):
            decode(bad)

    def test_decode_rejects_corrupted_payload_char(self):
        good = encode("S3", [{"id": 0}, {"id": 1}, {"id": 2}])
        # Corrupt a character inside the payload (position 9), leaving spread and checksum intact.
        target = 9
        corrupted = good[:target] + ("A" if good[target] != "A" else "B") + good[target + 1:]
        self.assertNotEqual(corrupted, good)
        with self.assertRaisesRegex(DrawCodeError, "checksum"):
            decode(corrupted)

    def test_decode_rejects_duplicate_cards_in_payload(self):
        # Manually build a payload with duplicate IDs (id=2 appears twice with diff orientation)
        # 2U=04, 2R=05. Choose 3 distinct valid codes where two share same id.
        prefix = "TC1-S3-040506"
        # Compute the proper checksum so only the duplicate trip fails:
        from tarot_codec import _encode_base32, crc16_ccitt
        checksum = _encode_base32(crc16_ccitt(prefix.encode("ascii")) & 0x7FFF, 3)
        code = f"{prefix}-{checksum}"
        with self.assertRaisesRegex(DrawCodeError, "duplicate"):
            decode(code)

    def test_decode_rejects_out_of_range_id_in_payload(self):
        # 78 * 2 = 156 -> encoded as 2 chars base32, but card_id > 77 should fail
        prefix = "TC1-S3-0001ZZ"
        from tarot_codec import _encode_base32, crc16_ccitt
        checksum = _encode_base32(crc16_ccitt(prefix.encode("ascii")) & 0x7FFF, 3)
        code = f"{prefix}-{checksum}"
        with self.assertRaisesRegex(DrawCodeError, "out of range"):
            decode(code)


class DeckEnrichmentTests(unittest.TestCase):
    def setUp(self):
        self.deck = load_deck(SKILL / "references" / "deck.json")

    def test_deck_has_exactly_78_cards(self):
        self.assertEqual(len(self.deck), 78)

    def test_deck_ids_are_contiguous_zero_to_seventy_seven(self):
        self.assertEqual(sorted(self.deck.keys()), list(range(78)))

    def test_deck_names_include_chinese(self):
        self.assertEqual(self.deck[0]["name_zh"], "愚者")
        self.assertEqual(self.deck[18]["name_zh"], "月亮")

    def test_enrich_merges_metadata_into_cards(self):
        result = enrich(decode(encode("F1", [{"id": 18, "reversed": True}])), SKILL / "references" / "deck.json")
        card = result["cards"][0]
        self.assertEqual(card["name_zh"], "月亮")
        self.assertEqual(card["name_en"], "The Moon")
        self.assertEqual(card["orientation"], "reversed")

    def test_enrich_preserves_decode_order(self):
        result = enrich(decode(encode("S3", [{"id": 0}, {"id": 1}, {"id": 2}])), SKILL / "references" / "deck.json")
        self.assertEqual([c["id"] for c in result["cards"]], [0, 1, 2])


class CodeFormatTests(unittest.TestCase):
    def test_code_structure_has_four_dash_segments(self):
        code = encode("F1", [{"id": 0}])
        self.assertEqual(code.count("-"), 3)
        self.assertEqual(len(code.split("-")), 4)

    def test_payload_length_matches_spread(self):
        self.assertEqual(len(encode("F1", [{"id": 0}]).split("-")[2]), 2)
        self.assertEqual(len(encode("S3", [{"id": 0}, {"id": 1}, {"id": 2}]).split("-")[2]), 6)
        self.assertEqual(len(encode("R3", [{"id": 0}, {"id": 1}, {"id": 2}]).split("-")[2]), 6)

    def test_checksum_is_three_chars(self):
        code = encode("F1", [{"id": 0}])
        self.assertEqual(len(code.split("-")[3]), 3)


if __name__ == "__main__":
    unittest.main()
