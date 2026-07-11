#!/usr/bin/env python3
"""Encode and decode TC1 tarot draw codes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
DECODE_MAP = {char: index for index, char in enumerate(ALPHABET)}
DECODE_MAP.update({"O": 0, "I": 1, "L": 1})
SPREAD_COUNTS = {"F1": 1, "S3": 3, "R3": 3}


class DrawCodeError(ValueError):
    pass


def _encode_base32(value: int, width: int) -> str:
    if value < 0 or value >= 32**width:
        raise DrawCodeError(f"value {value} does not fit in {width} characters")
    output = []
    for _ in range(width):
        output.append(ALPHABET[value & 31])
        value >>= 5
    return "".join(reversed(output))


def _decode_base32(text: str) -> int:
    value = 0
    for char in text.upper():
        try:
            digit = DECODE_MAP[char]
        except KeyError as exc:
            raise DrawCodeError(f"invalid Base32 character: {char}") from exc
        value = value * 32 + digit
    return value


def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def encode(spread: str, cards: Iterable[dict]) -> str:
    spread = spread.upper()
    if spread not in SPREAD_COUNTS:
        raise DrawCodeError(f"unknown spread: {spread}")
    cards = list(cards)
    if len(cards) != SPREAD_COUNTS[spread]:
        raise DrawCodeError(f"spread {spread} requires {SPREAD_COUNTS[spread]} cards")
    ids = [int(card["id"]) for card in cards]
    if len(set(ids)) != len(ids):
        raise DrawCodeError("duplicate card IDs are not allowed")
    payload_parts = []
    for card in cards:
        card_id = int(card["id"])
        if not 0 <= card_id <= 77:
            raise DrawCodeError(f"card ID out of range: {card_id}")
        reversed_value = bool(card.get("reversed", False))
        payload_parts.append(_encode_base32(card_id * 2 + int(reversed_value), 2))
    payload = "".join(payload_parts)
    prefix = f"TC1-{spread}-{payload}"
    checksum = _encode_base32(crc16_ccitt(prefix.encode("ascii")) & 0x7FFF, 3)
    return f"{prefix}-{checksum}"


def decode(code: str) -> dict:
    normalized = code.strip().upper().replace("O", "0").replace("I", "1").replace("L", "1")
    parts = normalized.split("-")
    if len(parts) != 4 or parts[0] != "TC1":
        raise DrawCodeError("expected TC1-<SPREAD>-<PAYLOAD>-<CHECKSUM>")
    _, spread, payload, checksum = parts
    if spread not in SPREAD_COUNTS:
        raise DrawCodeError(f"unknown spread: {spread}")
    expected_length = SPREAD_COUNTS[spread] * 2
    if len(payload) != expected_length:
        raise DrawCodeError(f"spread {spread} requires a {expected_length}-character payload")
    prefix = f"TC1-{spread}-{payload}"
    expected_checksum = _encode_base32(crc16_ccitt(prefix.encode("ascii")) & 0x7FFF, 3)
    if checksum != expected_checksum:
        raise DrawCodeError("checksum mismatch")
    cards = []
    for index in range(0, len(payload), 2):
        value = _decode_base32(payload[index:index + 2])
        card_id, orientation_bit = divmod(value, 2)
        if card_id > 77:
            raise DrawCodeError(f"card ID out of range: {card_id}")
        cards.append({"id": card_id, "reversed": bool(orientation_bit), "orientation": "reversed" if orientation_bit else "upright"})
    ids = [card["id"] for card in cards]
    if len(set(ids)) != len(ids):
        raise DrawCodeError("duplicate card IDs are not allowed")
    return {"version": "TC1", "spread": spread, "cards": cards, "code": normalized}


def load_deck(path: Path) -> dict[int, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {card["id"]: card for card in data["cards"]}


def enrich(result: dict, deck_path: Path) -> dict:
    deck = load_deck(deck_path)
    result = dict(result)
    result["cards"] = [{**card, **deck[card["id"]]} for card in result["cards"]]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    decode_parser = subparsers.add_parser("decode")
    decode_parser.add_argument("code")
    decode_parser.add_argument("--deck", type=Path, default=Path(__file__).resolve().parents[1] / "references" / "deck.json")
    encode_parser = subparsers.add_parser("encode")
    encode_parser.add_argument("--spread", required=True, choices=sorted(SPREAD_COUNTS))
    encode_parser.add_argument("cards", nargs="+", help="card tokens such as 0U 18R 9U")
    args = parser.parse_args()
    try:
        if args.command == "decode":
            output = enrich(decode(args.code), args.deck)
        else:
            cards = []
            for token in args.cards:
                orientation = token[-1].upper()
                if orientation not in {"U", "R"}:
                    raise DrawCodeError(f"invalid card token: {token}")
                cards.append({"id": int(token[:-1]), "reversed": orientation == "R"})
            output = {"code": encode(args.spread, cards)}
    except (DrawCodeError, KeyError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
