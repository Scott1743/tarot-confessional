#!/usr/bin/env python3
"""Export the canonical Skill deck table for offline browser use."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "tarot-confessional"
source = json.loads((SKILL / "references" / "deck.json").read_text(encoding="utf-8"))
cards = [
    {"id": card["id"], "name": card["name_zh"], "file": card["image"]}
    for card in source["cards"]
]
payload = json.dumps({"schemaVersion": source["schema_version"], "cards": cards}, ensure_ascii=False, separators=(",", ":"))
(SKILL / "assets" / "deck-data.js").write_text(f"window.TarotDeck=Object.freeze({payload});\n", encoding="utf-8")
