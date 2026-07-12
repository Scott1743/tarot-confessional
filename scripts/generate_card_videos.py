#!/usr/bin/env python3
"""Generate resumable three-second MiniMax motion loops for the tarot deck."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from pathlib import Path
from shutil import copy2

ROOT = Path(__file__).resolve().parents[1]
DECK_PATH = ROOT / "references" / "deck.json"
CARD_DIR = ROOT / "assets" / "images" / "cards"
RAW_DIR = ROOT / "assets" / "videos" / "generated-sources"
FINAL_DIR = ROOT / "assets" / "videos" / "cards"
SKILL_VIDEO_DIR = ROOT / "skills" / "tarot-confessional" / "assets" / "videos" / "cards"

PROMPT = (
    "Create a subtle living-painting animation from this exact Eastern gongbi tarot artwork. "
    "The camera is completely locked: no zoom, pan, tilt, rotation, crop, reframing, or scene cut. "
    "Preserve the original composition, faces, hands, anatomy, clothing, architecture, objects, symbolism, colors, and illustration style. "
    "Animate only small secondary details already present in the painting: gentle cloud and mist drift, slight water movement, restrained fabric-edge motion, "
    "soft petals or particles, delicate lantern or celestial light breathing, and natural minimal breathing when a person is present. "
    "The motion rises calmly and returns exactly to the starting image for a seamless loop. "
    "No new objects or people, no text or calligraphy, no morphing, melting, flicker, facial change, hand change, large body movement, or dramatic camera motion."
)


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True)


def duration_seconds(path: Path) -> float:
    completed = run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ])
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or "ffprobe failed")
    return float(completed.stdout.strip())


def normalize_video(raw: Path, image: Path, target: Path) -> None:
    duration = duration_seconds(raw)
    if duration <= 0:
        raise RuntimeError("generated video has invalid duration")
    speed = 3.0 / duration
    filter_graph = (
        f"[0:v]setpts={speed:.10f}*PTS,fps=30,"
        "scale=768:1152:force_original_aspect_ratio=decrease,"
        "pad=768:1152:(ow-iw)/2:(oh-ih)/2:black,trim=duration=3[video];"
        "[1:v]scale=768:1152:force_original_aspect_ratio=decrease,"
        "pad=768:1152:(ow-iw)/2:(oh-ih)/2:black[still];"
        "[video][still]overlay=enable='eq(n,0)+gte(n,89)'[out]"
    )
    completed = run([
        "ffmpeg", "-y", "-i", str(raw), "-loop", "1", "-i", str(image),
        "-filter_complex", filter_graph, "-map", "[out]", "-an",
        "-frames:v", "90", "-r", "30", "-c:v", "libx264", "-preset", "medium",
        "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target),
    ])
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or "ffmpeg failed")


def generate(card: dict, force: bool) -> tuple[int, str, str | None]:
    stem = Path(card["image"]).stem
    image = CARD_DIR / card["image"]
    raw = RAW_DIR / f"{stem}.mp4"
    target = FINAL_DIR / f"{stem}.mp4"
    if target.is_file() and not force:
        return card["id"], "skipped", None
    for attempt in range(1, 4):
        completed = run([
            "mmx", "video", "generate", "--prompt", PROMPT,
            "--first-frame", str(image), "--last-frame", str(image),
            "--download", str(raw), "--poll-interval", "8",
            "--non-interactive", "--quiet", "--output", "json",
        ])
        if completed.returncode == 0 and raw.is_file():
            try:
                normalize_video(raw, image, target)
                if (ROOT / "skills" / "tarot-confessional").is_dir():
                    SKILL_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
                    copy2(target, SKILL_VIDEO_DIR / target.name)
                return card["id"], "generated", None
            except (RuntimeError, ValueError) as exc:
                error = str(exc)
        else:
            error = (completed.stderr or completed.stdout or "MiniMax generation failed").strip()
        if attempt < 3:
            time.sleep(attempt * 10)
    return card["id"], "failed", error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=77)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--max-new", type=int, default=3, help="Maximum videos to generate in this run (default: daily quota of 3)")
    parser.add_argument("--daily-limit", type=int, default=3, help="Maximum completed videos dated today")
    parser.add_argument("--ignore-daily-limit", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cards = json.loads(DECK_PATH.read_text(encoding="utf-8"))["cards"]
    cards = [card for card in cards if args.start <= card["id"] <= args.end]
    if not args.force:
        cards = [card for card in cards if not (FINAL_DIR / f"{Path(card['image']).stem}.mp4").is_file()]
    today = date.today()
    completed_today = sum(
        1 for path in FINAL_DIR.glob("*.mp4")
        if datetime.fromtimestamp(path.stat().st_mtime).date() == today
    ) if FINAL_DIR.is_dir() else 0
    daily_remaining = args.max_new if args.ignore_daily_limit else max(0, args.daily_limit - completed_today)
    run_limit = min(max(0, args.max_new), daily_remaining)
    cards = cards[:run_limit]
    if args.dry_run:
        print(json.dumps({
            "date": today.isoformat(),
            "completed_today": completed_today,
            "daily_remaining": daily_remaining,
            "cards": [card["id"] for card in cards],
            "prompt": PROMPT,
        }, ensure_ascii=False, indent=2))
        return 0

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    counts = {"generated": 0, "skipped": 0, "failed": 0}
    failures = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(generate, card, args.force): card for card in cards}
        for future in as_completed(futures):
            card_id, status, error = future.result()
            counts[status] += 1
            event = {"id": card_id, "status": status}
            if error:
                event["error"] = error
                failures.append(card_id)
            print(json.dumps(event, ensure_ascii=False), flush=True)
    print(json.dumps({**counts, "failure_ids": sorted(failures)}, ensure_ascii=False), flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
