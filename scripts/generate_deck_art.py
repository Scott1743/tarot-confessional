#!/usr/bin/env python3
"""Generate the full Style C tarot deck through the configured mmx CLI."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK_PATH = ROOT / "references" / "deck.json"
DEFAULT_OUT = ROOT / "assets" / "images" / "generated-sources" / "full-deck-c"

STYLE = (
    "Original Eastern tarot card artwork for a Chinese Agent Skill. "
    "Modern meticulous Chinese gongbi fantasy, fine expressive line drawing, clean editorial color blocks, silk texture, refined faces, airy composition, and high mobile readability. "
    "High-dopamine palette using violet, cyan blue, jade green, tangerine, warm yellow, rose pink, cinnabar and restrained gold with ink-black contrast. "
    "Vertical 2:3 full-bleed artwork with one clear focal hierarchy. No generated frame or border. "
    "Culturally coherent Chinese architecture, clothing, objects and landscape. Original composition. "
    "Absolutely no text, calligraphy, pseudo-letters, numbers, labels, title plaques, logos, signature, watermark, talisman, religious icon, caption area, signboard, scroll, inscribed pillar, Western medieval clothing, European occult symbols, direct Rider-Waite-Smith copy, photorealism or 3D render. "
)

MAJOR_SCENES = {
    0: "A young wanderer in flowing travel robes steps beyond a mountain pass into colorful clouds, a white dog beside them, curiosity and risk.",
    1: "A composed practitioner at a black lacquer table with brush, straight sword, porcelain cup and jade bi disc, one hand linking sky and earth, focused agency.",
    2: "A serene keeper of night sits before layered silk curtains and a round water mirror, moonlit mountains behind, quiet inner knowledge.",
    3: "A dignified garden steward among mulberry, grain, pomegranate, woven silk and flowing water, abundance through cultivation.",
    4: "A firm ruler seated on a carved stone platform above terraced mountains, holding a square seal and measuring cord, stable authority.",
    5: "A respected teacher in an open courtyard guiding two students with ritual vessels and old books kept closed, shared tradition without readable writing.",
    6: "Two equal figures meet beneath intertwined flowering branches and paired birds, choosing one another across a bright river bridge.",
    7: "A determined traveler drives a lacquer chariot drawn by a black horse and white horse through windblown banners, disciplined momentum.",
    8: "A calm woman gently guides a powerful guardian lion with a silk ribbon, courage expressed through patience rather than force.",
    9: "A solitary traveler crosses a snowy ridge carrying a warm paper lantern, distant roofs hidden in violet mist, precise inner guidance.",
    10: "A vast turning celestial wheel inspired by an armillary sphere above changing seasons, figures rising and descending through colorful clouds.",
    11: "An impartial magistrate-like figure holds balanced scales and an upright straight sword in a clear symmetrical hall, truth and consequence.",
    12: "A contemplative figure hangs peacefully by one ankle from a flowering tree over water, robes flowing downward, voluntary pause and changed perspective.",
    13: "An empty dark robe rides through a field where old leaves fall and new plum blossoms open, transformation and irreversible passage without horror.",
    14: "A graceful figure pours water between two porcelain vessels while standing with one foot on stone and one in a stream, measured integration.",
    15: "Two people remain loosely bound to a lavish shadow-market pavilion by ribbons they could remove, desire, attachment and self-deception.",
    16: "A high watchtower struck by white lightning as its roof opens and bright fragments fall into storm clouds, sudden truth and collapse of false structure.",
    17: "A calm figure beside a lotus pool pours water from two vessels while an abstract Chinese star map glows across a violet sky, restoration.",
    18: "A circular moon opening, a pale dog and dark hound beside a winding water path, reflected moonlight and colorful clouds, ambiguity without horror.",
    19: "A joyful child runs through an open cinnabar gate into a vivid flower garden under a large warm sun disc, vitality and clarity.",
    20: "People rise from sleep as a great bronze bell sounds across mountains at dawn, answering a call to review and renewal.",
    21: "A dancing figure encircled by a flowing silk ring above a complete landscape of four seasons, integration, completion and belonging.",
}

SUIT_SCENES = {
    "wands": [
        "A single flowering staff sprouts fire-colored leaves above a mountain sunrise, raw creative force.",
        "A figure on a terrace holds one staff while another stands beside a mapless horizon, choosing a direction.",
        "A figure watches three flowering staffs planted above a river port, plans beginning to expand.",
        "Four staffs form a bright celebration canopy with ribbons, friends arriving through a garden gate.",
        "Five young people cross staffs in spirited practice, energetic friction without cruelty.",
        "A returning rider carries a flowering staff through cheering banners, earned recognition.",
        "A figure on high ground protects a narrow path with one staff against six rising staffs, defending position.",
        "Eight staffs streak diagonally through colorful cloud bands like swift arrows, acceleration and messages.",
        "A bandaged guardian stands before nine upright staffs at dusk, resilience and alert boundaries.",
        "A traveler carries ten heavy staffs toward a gate, ambition becoming burden.",
        "A curious young messenger studies a sprouting staff in a bright desert garden, emerging enthusiasm.",
        "A fast rider lifts a flaming staff through red and violet clouds, bold pursuit and impatience.",
        "A confident woman sits with a flowering staff and a black cat in a vivid courtyard, warmth and self-possession.",
        "A charismatic leader holds a mature flowering staff above volcanic mountains, vision and creative command.",
    ],
    "cups": [
        "A single luminous porcelain cup overflows into a lotus pool, emotional opening and abundance.",
        "Two people exchange matching cups beneath paired cranes and a rose-colored moon, mutual recognition.",
        "Three friends raise porcelain cups in a flower garden, shared joy and community.",
        "A seated figure overlooks three cups while a fourth appears through mist, withdrawal and overlooked possibility.",
        "A grieving figure faces three spilled cups while two remain upright beside a bridge, loss and remaining support.",
        "Two children exchange a cup filled with blossoms in an old courtyard, memory and gentle familiarity.",
        "Seven cups float within vivid clouds, each holding a different alluring image, fantasy and too many choices.",
        "A traveler leaves eight arranged cups beside a moonlit lake and walks toward mountains, conscious departure.",
        "A satisfied host sits before nine displayed cups in a colorful pavilion, pleasure and wishes fulfilled.",
        "A family watches a rainbow arc above ten cups and a river village, emotional belonging.",
        "A curious young messenger holds a cup from which a small fish rises, imagination and surprising feeling.",
        "A graceful rider carries a cup across shallow water, romance, invitation and idealism.",
        "A compassionate woman holds an ornate cup beside a deep lotus lake, emotional insight and containment.",
        "A calm leader sits above turbulent water holding a cup steadily, mature feeling and diplomacy.",
    ],
    "swords": [
        "A single upright jian sword rises through clouds beneath a bright crown-like ring of light, clear thought and truth.",
        "A blindfolded figure holds two crossed swords beside still water, guarded indecision.",
        "Three straight swords pierce a red paper heart beneath rain clouds, grief and painful clarity without gore.",
        "A resting figure lies in a quiet hall beneath four arranged swords, recovery and deliberate pause.",
        "A smug figure gathers swords after a conflict while two people walk away by the shore, hollow victory.",
        "A boat carries a family and six sheathed swords across misty water, transition toward calmer ground.",
        "A stealthy figure carries five swords away from a camp while two remain, strategy and questionable tactics.",
        "A loosely bound figure stands among eight swords in wet ground with an open path behind, perceived restriction.",
        "A sleepless figure sits upright beneath nine hanging swords and indigo night, anxiety and mental repetition.",
        "Ten swords lie embedded around an empty fallen cloak at dawn, painful ending with light returning, no body or gore.",
        "An alert young messenger raises a sword into strong wind on a high ridge, curiosity and sharp observation.",
        "A swift rider charges through storm clouds with an upright sword, direct action and haste.",
        "A clear-eyed woman holds a sword upright above windblown clouds, discernment and honest boundaries.",
        "A composed leader sits on a high stone seat with a straight sword, intellectual authority and fair judgement.",
    ],
    "pentacles": [
        "A single glowing jade bi disc hovers above a lush garden path, tangible opportunity and grounded beginning.",
        "A performer balances two jade discs linked by an infinity ribbon beside changing waves, adaptability.",
        "Three artisans collaborate on a colorful pavilion while three jade discs align above them, skilled teamwork.",
        "A guarded figure holds one jade disc while three surround the body in a city courtyard, control and holding tight.",
        "Two travelers pass a warmly lit hall in winter while five jade discs glow in its window, hardship and available help.",
        "A generous merchant gives grain and coins to two people while holding balanced scales, fair exchange.",
        "A gardener pauses beside a vine bearing seven jade discs, patience and evaluation.",
        "A focused artisan carves the eighth jade disc at a workbench, practice and mastery.",
        "An independent woman walks through a rich garden with nine jade discs and a small bird, self-sufficiency.",
        "Three generations gather in a courtyard beneath ten jade discs, continuity, inheritance and shared resources.",
        "A diligent young student studies a jade disc in a bright field, practical learning and new opportunity.",
        "A steady rider carries a jade disc through cultivated land, reliability and patient progress.",
        "A nurturing woman holds a jade disc among grain, fruit and a small rabbit, practical care and abundance.",
        "A prosperous leader sits in a garden pavilion holding a jade disc, stewardship and material competence.",
    ],
}


def prompt_for(card: dict) -> str:
    if card["arcana"] == "major":
        scene = MAJOR_SCENES[card["id"]]
    else:
        suit_start = {"wands": 22, "cups": 36, "swords": 50, "pentacles": 64}[card["suit"]]
        scene = SUIT_SCENES[card["suit"]][card["id"] - suit_start]
    return STYLE + "Scene: " + scene


def generate(card: dict, out_dir: Path, force: bool) -> tuple:
    target_prefix = out_dir / Path(card["image"]).stem
    existing = sorted(out_dir.glob(target_prefix.name + "_*.jpg"))
    if existing and not force:
        return card["id"], "skipped"
    command = [
        "mmx", "image", "generate", "--prompt", prompt_for(card),
        "--width", "768", "--height", "1152", "--n", "1",
        "--seed", str(120000 + card["id"]), "--out-dir", str(out_dir),
        "--out-prefix", target_prefix.name, "--non-interactive", "--quiet", "--output", "json",
    ]
    for attempt in range(1, 5):
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if not completed.returncode:
            return card["id"], "generated"
        error = completed.stderr or completed.stdout
        transient = any(marker in error.lower() for marker in ("rate limit", "rpc timeout", "timed out", "timeout"))
        if transient and attempt < 4:
            time.sleep(attempt * 6)
            continue
        return card["id"], "failed", error.strip()
    return card["id"], "failed", "retry limit reached"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=77)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    deck = json.loads(DECK_PATH.read_text(encoding="utf-8"))["cards"]
    cards = [card for card in deck if args.start <= card["id"] <= args.end]
    if args.dry_run:
        print(json.dumps([{"id": card["id"], "image": card["image"], "prompt": prompt_for(card)} for card in cards], ensure_ascii=False, indent=2))
        return 0
    args.out_dir.mkdir(parents=True, exist_ok=True)
    counts = {"generated": 0, "skipped": 0, "failed": 0}
    failures = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(generate, card, args.out_dir, args.force): card for card in cards}
        for future in as_completed(futures):
            result = future.result()
            card_id, status = result[:2]
            counts[status] += 1
            event = {"id": card_id, "status": status}
            if status == "failed":
                event["error"] = result[2]
                failures.append(card_id)
            print(json.dumps(event), flush=True)
    print(json.dumps({**counts, "failure_ids": sorted(failures)}), flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
