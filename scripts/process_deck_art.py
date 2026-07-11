#!/usr/bin/env python3
"""Normalize generated deck art into canonical web JPEG files."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "assets/images/generated-sources/full-deck-c")
    parser.add_argument("--output", type=Path, default=ROOT / "assets/images/cards")
    args = parser.parse_args()
    cards = json.loads((ROOT / "references/deck.json").read_text(encoding="utf-8"))["cards"]
    args.output.mkdir(parents=True, exist_ok=True)
    failures = []
    for card in cards:
        stem = Path(card["image"]).stem
        sources = sorted(args.source.glob(stem + "_*.jpg"))
        if not sources:
            failures.append({"id": card["id"], "reason": "source missing"})
            continue
        command = [
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(sources[-1]),
            "-vf", "crop=640:960:64:96,scale=768:1152,eq=saturation=1.22:contrast=1.05:brightness=0.01",
            "-q:v", "3", "-frames:v", "1", str(args.output / card["image"]),
        ]
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if completed.returncode:
            failures.append({"id": card["id"], "reason": completed.stderr.strip()})
    print(json.dumps({"processed": len(cards) - len(failures), "failures": failures}, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
