"""Cross-language parity tests: Python TC1 codec vs JavaScript TC1 codec.

Strategy:
- Drive both encoders with the same input vector.
- Assert their outputs are identical (the spec's invariant).
- Drive Python decoder with the JS encoder's output.
- Drive the JS encoder through Node to avoid jsdom/DOM mocking.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from tarot_codec import decode, encode  # noqa: E402

JS_SOURCE = (ROOT / "skills/tarot-confessional/assets/tarot-codec.js").read_text(encoding="utf-8")

VECTORS = [
    # (spread, [(card_id, reversed), ...])
    ("F1", [(0, False)]),
    ("F1", [(77, True)]),
    ("F1", [(21, False)]),
    ("S3", [(0, False), (1, False), (2, False)]),
    ("S3", [(1, False), (18, True), (9, False)]),
    ("S3", [(22, False), (36, True), (50, False)]),
    ("R3", [(6, False), (36, True), (77, False)]),
    ("S3", [(11, True), (33, False), (66, True)]),
]


class JsEncoderParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if subprocess.run(["which", "node"], capture_output=True, text=True).stdout.strip() == "":
            raise unittest.SkipTest("node not available; cross-language parity tests skipped")

    def _js_encode(self, spread: str, cards: list[dict]) -> str:
        cards_json = json.dumps(cards)
        # Use Node to load the IIFE source and call encode() through window.TarotCodec
        script = (
            "const fs = require('fs');"
            f"const src = {json.dumps(JS_SOURCE)};"
            "const sandbox = {};"
            "new Function('window', src)(sandbox);"
            f"const code = sandbox.TarotCodec.encode({json.dumps(spread)}, {cards_json});"
            "process.stdout.write(code);"
        )
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, f"node failed: {result.stderr}")
        return result.stdout.strip()

    def test_js_encoder_matches_python_for_all_vectors(self):
        for spread, pairs in VECTORS:
            cards = [{"id": cid, "reversed": rev} for cid, rev in pairs]
            py_code = encode(spread, cards)
            js_code = self._js_encode(spread, cards)
            with self.subTest(spread=spread, cards=cards):
                self.assertEqual(py_code, js_code, f"mismatch for {spread} {cards}")

    def test_python_decoder_accepts_js_encoder_output(self):
        js_code = self._js_encode("S3", [{"id": 1}, {"id": 18, "reversed": True}, {"id": 9}])
        result = decode(js_code)
        self.assertEqual([c["id"] for c in result["cards"]], [1, 18, 9])
        self.assertEqual([c["reversed"] for c in result["cards"]], [False, True, False])

    def test_js_encoder_rejects_unknown_spread(self):
        script = (
            "const fs = require('fs');"
            f"const src = {json.dumps(JS_SOURCE)};"
            "const sandbox = {};"
            "new Function('window', src)(sandbox);"
            "try { sandbox.TarotCodec.encode('X9', [{id:0}]); process.stdout.write('NO_THROW'); }"
            "catch (e) { process.stdout.write(e.message); }"
        )
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
        self.assertIn("unknown spread", result.stdout)

    def test_js_encoder_rejects_duplicate_cards(self):
        script = (
            "const fs = require('fs');"
            f"const src = {json.dumps(JS_SOURCE)};"
            "const sandbox = {};"
            "new Function('window', src)(sandbox);"
            "try { sandbox.TarotCodec.encode('S3', [{id:5},{id:5},{id:7}]); process.stdout.write('NO_THROW'); }"
            "catch (e) { process.stdout.write(e.message); }"
        )
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
        self.assertIn("duplicate", result.stdout)

    def test_js_crc16_matches_python_for_known_string(self):
        # CRC-16/CCITT-FALSE of "123456789" is 0x29B1
        script = (
            "const fs = require('fs');"
            f"const src = {json.dumps(JS_SOURCE)};"
            "const sandbox = {};"
            "new Function('window', src)(sandbox);"
            "process.stdout.write(String(sandbox.TarotCodec.crc16('123456789')));"
        )
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
        self.assertEqual(result.stdout.strip(), str(0x29B1))

    def test_js_crc16_matches_python_for_tc1_prefix(self):
        from tarot_codec import crc16_ccitt
        prefix = "TC1-S3-02150J"
        expected = crc16_ccitt(prefix.encode("ascii"))
        script = (
            "const fs = require('fs');"
            f"const src = {json.dumps(JS_SOURCE)};"
            "const sandbox = {};"
            "new Function('window', src)(sandbox);"
            f"process.stdout.write(String(sandbox.TarotCodec.crc16({json.dumps(prefix)})));"
        )
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
        self.assertEqual(result.stdout.strip(), str(expected))


if __name__ == "__main__":
    unittest.main()