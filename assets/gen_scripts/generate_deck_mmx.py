#!/usr/bin/env python3
"""Generate upright Forest Whispers tarot art through mmx-cli.

Reversed cards intentionally reuse the upright bitmap and rotate it 180 degrees
at runtime; no second image-generation request is made.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = Path(__file__).with_name("card_plan.json")
DECK_PATH = ROOT / "references" / "deck.json"
DEFAULT_OUT = ROOT / "assets" / "images" / "generated-sources" / "forest-deck-v2-animals"
LOG_LOCK = threading.Lock()

CULTURAL_REPLACEMENTS = (
    (r"\bporcelain\b", "ceramic"),
    (r"\blotus\b", "water-lily"),
    (r"\bjade discs\b", "golden pentacles"),
    (r"\bjade disc\b", "golden pentacle"),
    (r"\bcinnabar gate\b", "sunlit garden gate"),
    (r"\bjian\b", "straight sword"),
    (r"\bsilk\b", "woven"),
    (r"\bpavilion\b", "forest shelter"),
    (r"\bsquare seal\b", "royal insignia"),
)


def neutralize_scene_text(text: str) -> str:
    """Normalize material terms while preserving the card's human roles."""
    for pattern, replacement in CULTURAL_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def load_and_validate_plan() -> tuple[dict, list[dict]]:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    cards = plan.get("cards", [])
    deck = json.loads(DECK_PATH.read_text(encoding="utf-8"))["cards"]
    if len(cards) != 78 or [card.get("id") for card in cards] != list(range(78)):
        raise ValueError("card_plan.json must contain ordered card IDs 0..77")
    expected = {(card["id"], card["key"], card["name_zh"]) for card in deck}
    actual = {(card["id"], card["key"], card["name_zh"]) for card in cards}
    if actual != expected:
        raise ValueError("card_plan.json card identity does not match references/deck.json")
    required = ("shared_anchor", "upright_scene", "reversed_transform")
    for card in cards:
        missing = [key for key in required if not str(card.get(key, "")).strip()]
        if missing:
            raise ValueError(f"card {card['id']} missing fields: {missing}")
        if str(card["id"]) not in plan.get("animal_cast", {}):
            raise ValueError(f"card {card['id']} missing animal cast")
    return plan, cards


def filename(card: dict) -> str:
    return f"{card['id']:02d}-{card['key']}.jpg"


def upright_prompt(plan: dict, card: dict) -> str:
    style_prompt = plan["style"]["prompt"][:900]
    anchors = neutralize_scene_text(card["shared_anchor"])
    scene = neutralize_scene_text(card["upright_scene"])
    lighting = plan.get("lighting_overrides", {}).get(str(card["id"]), "soft side or diffuse daylight, never default backlight")
    return " ".join(
        (
            style_prompt,
            f"Brief {card['id']:02d}-{card['key']}; no visible ID or name. Anchors: {anchors}. Scene: {scene}.",
            f"Light: {lighting}. Show exact suit-object count. Corners are pure painted scenery without marks.",
        )
    )


def reversed_prompt(plan: dict, card: dict) -> str:
    style_prompt = plan["style"]["prompt"][:900]
    invariants = "same protagonist or focal object, face, costume, anchors, composition, palette and light"
    transform = neutralize_scene_text(card["reversed_transform"])
    lighting = plan.get("lighting_overrides", {}).get(str(card["id"]), "the same soft side or diffuse light as upright")
    return " ".join(
        (
            style_prompt,
            "Reversed partner; no visible text. The upright reference is binding.",
            f"Preserve {invariants}. Change only: {transform}. Same light: {lighting}. No rotation, new subject or camera move.",
        )
    )


def build_command(
    *,
    plan: dict,
    card: dict,
    orientation: str,
    output_path: Path,
    upright_reference: Path | None = None,
) -> list[str]:
    if orientation not in {"upright", "reversed"}:
        raise ValueError(f"unknown orientation: {orientation}")
    prompt = upright_prompt(plan, card) if orientation == "upright" else reversed_prompt(plan, card)
    if len(prompt) >= 1500:
        raise ValueError(f"prompt for {card['id']:02d}-{card['key']} is {len(prompt)} chars; mmx requires <1500")
    command = [
        "mmx", "image", "generate",
        "--prompt", prompt,
        "--width", str(plan["canvas"]["width"]),
        "--height", str(plan["canvas"]["height"]),
        "--n", "1",
        "--seed", str(410000 + card["id"]),
        "--response-format", "base64",
        "--out", str(output_path),
        "--non-interactive", "--quiet", "--output", "json",
    ]
    if orientation == "reversed":
        if upright_reference is None:
            raise ValueError("reversed generation requires an upright reference")
        command.extend(("--subject-ref", f"type=character,image={upright_reference.resolve()}"))
    return command


def append_log(log_path: Path, event: dict) -> None:
    event = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), **event}
    with LOG_LOCK:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def run_generation(command: list[str], target: Path, retries: int, log_path: Path, event: dict) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, retries + 1):
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if completed.returncode == 0:
            if not target.is_file() or target.stat().st_size == 0:
                raise FileNotFoundError(f"mmx completed without writing target: {target}")
            append_log(log_path, {**event, "status": "generated", "attempt": attempt, "target": str(target)})
            return
        error = (completed.stderr or completed.stdout).strip()
        append_log(log_path, {**event, "status": "retry", "attempt": attempt, "error": error[:1000]})
        transient = any(marker in error.lower() for marker in ("network", "rate limit", "timeout", "timed out", "temporarily unavailable", "rpc"))
        if transient and attempt < retries:
            time.sleep(attempt * 8)
            continue
        raise RuntimeError(f"mmx rejected generation for {target}: {error[:500]}")
    raise RuntimeError(f"mmx generation failed after {retries} attempts for {target}")


def generate_card(
    *,
    plan: dict,
    card: dict,
    stage: str,
    out_dir: Path,
    force: bool,
    retries: int,
    log_path: Path,
) -> dict:
    upright = out_dir / "upright" / filename(card)
    reversed_image = out_dir / "reversed" / filename(card)
    result = {"id": card["id"], "key": card["key"], "upright": "not-requested", "reversed": "not-requested"}

    if stage in {"upright", "both"}:
        if upright.exists() and not force:
            result["upright"] = "skipped"
        else:
            command = build_command(plan=plan, card=card, orientation="upright", output_path=upright)
            run_generation(command, upright, retries, log_path, {"id": card["id"], "orientation": "upright"})
            result["upright"] = "generated"

    if stage in {"reversed", "both"}:
        result["reversed"] = "runtime-rotate-180"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--stage", choices=("upright", "both"), default="upright")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=77)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    if not 0 <= args.start <= args.end <= 77:
        parser.error("expected 0 <= start <= end <= 77")
    plan, all_cards = load_and_validate_plan()
    cards = [card for card in all_cards if args.start <= card["id"] <= args.end]
    if args.validate_only:
        print(json.dumps({"valid": True, "cards": len(all_cards), "schema": plan["schema_version"]}))
        return 0
    if args.dry_run:
        preview = []
        for card in cards:
            upright = args.out_dir / "upright" / filename(card)
            record = {"id": card["id"], "key": card["key"]}
            if args.stage in {"upright", "both"}:
                record["upright_command"] = build_command(plan=plan, card=card, orientation="upright", output_path=upright)
            if args.stage == "both":
                record["reversed"] = "runtime-rotate-180"
            preview.append(record)
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return 0

    args.out_dir.mkdir(parents=True, exist_ok=True)
    log_path = args.out_dir / "generation-log.jsonl"
    failures: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(
                generate_card,
                plan=plan,
                card=card,
                stage=args.stage,
                out_dir=args.out_dir,
                force=args.force,
                retries=max(1, args.retries),
                log_path=log_path,
            ): card
            for card in cards
        }
        for future in as_completed(futures):
            card = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # keep the batch resumable
                result = {"id": card["id"], "key": card["key"], "status": "failed", "error": str(exc)}
                failures.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
    print(json.dumps({"requested": len(cards), "failed": len(failures), "failure_ids": [item["id"] for item in failures]}, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
