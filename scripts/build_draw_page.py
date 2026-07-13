#!/usr/bin/env python3
"""Build a fully self-contained draw HTML page.

Why this exists
---------------
The skill may be installed on Windows, macOS, or Linux in any directory the
user chooses. The Agent may also copy or download just the HTML file to a
different location (e.g. a chat attachment, /tmp, the user's working dir).

The bundled `assets/draw.html` references:
  - 3 layout images via CSS url("images/...")
  - 1 layout image via <img src="images/...">
  - 78 card images via JS template literal `images/cards/${card.file}`
  - 2 scripts via <script src="...">

Relative paths break the moment the HTML is separated from its sibling
directory. To guarantee the HTML works from anywhere we inline every asset:

  - <script src="...">      -> <script>...inline JS...</script>
  - CSS url("images/X")     -> url("data:image/jpeg;base64,...")
  - <img src="images/X">    -> src="data:image/jpeg;base64,..."
  - JS template literal     -> lookup against window.__tarotCardImages

The output is one HTML file the Agent can hand to the user without worry.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from pathlib import Path

VALID_SPREADS = {"F1", "S3", "R3"}


def expected_assets(assets_dir: Path) -> list[Path]:
    """Return every asset the draw page needs (layout + 78 cards)."""
    layout = [
        assets_dir / "images" / "card-back.jpg",
        assets_dir / "images" / "forest-whisper-bg.jpg",
        assets_dir / "images" / "eastern-night-bg_001.jpg",
        assets_dir / "images" / "purple-silk.jpg",
    ]
    cards_dir = assets_dir / "images" / "cards"
    cards = sorted(cards_dir.glob("*.jpg"))
    return layout + cards


def _data_uri(path: Path) -> str:
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{payload}"


def _inline_layout_images(html: str, assets: dict[str, str]) -> str:
    """Replace layout image references with their data URI counterparts."""
    html = html.replace('url("images/card-back.jpg")', f'url("{assets["card-back.jpg"]}")')
    html = html.replace('url("images/forest-whisper-bg.jpg")', f'url("{assets["forest-whisper-bg.jpg"]}")')
    html = html.replace('url("images/eastern-night-bg_001.jpg")', f'url("{assets["eastern-night-bg_001.jpg"]}")')
    html = html.replace('url("images/purple-silk.jpg")', f'url("{assets["purple-silk.jpg"]}")')
    html = html.replace('src="images/card-back.jpg"', f'src="{assets["card-back.jpg"]}"')
    # JS inline string used when a card is selected but not yet revealed.
    html = html.replace(
        "'#160c24 url(\"images/card-back.jpg\") center / cover'",
        f"'#160c24 url(\"{assets['card-back.jpg']}\") center / cover'",
    )
    return html


def _inline_scripts(html: str, scripts: dict[str, str]) -> str:
    """Replace external <script src=...> tags with inlined contents."""
    for src, content in scripts.items():
        tag = f'<script src="{src}"></script>'
        replacement = f'<script>\n{content}\n</script>'
        if tag not in html:
            raise ValueError(f"draw.html missing expected script tag: {src}")
        html = html.replace(tag, replacement, 1)
    return html


def _inject_card_image_map(html: str, card_assets: dict[str, str]) -> str:
    """Insert a JS map so the runtime can resolve `cards/${card.file}` to a data URI."""
    payload = json.dumps(card_assets, ensure_ascii=False, indent=2)
    bootstrap = (
        "<script>\n"
        "window.__tarotCardImages = " + payload + ";\n"
        "window.__tarotCardImagesResolve = function(rel) { return window.__tarotCardImages[rel] || ''; };\n"
        "</script>\n"
    )
    if "</head>" not in html:
        raise ValueError("draw.html missing </head> closing tag")
    html = html.replace("</head>", bootstrap + "</head>", 1)

    # Rewrite the dynamic reference inside the inline JS:
    # `images/cards/${card.file}` -> (__tarotCardImagesResolve("cards/" + card.file) || ("images/cards/" + card.file))
    html = html.replace(
        '`images/cards/${card.file}`',
        '(__tarotCardImagesResolve("cards/" + card.file) || ("images/cards/" + card.file))',
    )
    return html


def build(*, skill_dir: Path, output: Path, spread: str, title: str = "") -> Path:
    if spread not in VALID_SPREADS:
        raise ValueError(f"spread must be one of {sorted(VALID_SPREADS)}, got {spread!r}")

    assets_dir = skill_dir / "assets"
    template_path = assets_dir / "draw.html"
    if not template_path.is_file():
        raise FileNotFoundError(f"missing template: {template_path}")

    html = template_path.read_text(encoding="utf-8")

    layout_names = ("card-back.jpg", "forest-whisper-bg.jpg", "eastern-night-bg_001.jpg", "purple-silk.jpg")
    layout_assets = {name: _data_uri(assets_dir / "images" / name) for name in layout_names}
    card_assets = {
        f"cards/{path.name}": _data_uri(path)
        for path in sorted((assets_dir / "images" / "cards").glob("*.jpg"))
    }
    if len(card_assets) != 78:
        raise ValueError(f"expected 78 card images, found {len(card_assets)}")

    scripts = {
        "deck-data.js": (assets_dir / "deck-data.js").read_text(encoding="utf-8"),
        "tarot-codec.js": (assets_dir / "tarot-codec.js").read_text(encoding="utf-8"),
    }

    html = _inline_layout_images(html, layout_assets)
    html = _inline_scripts(html, scripts)
    html = _inject_card_image_map(html, card_assets)

    # Stamp spread + title so future Agent flows can read them back.
    stamp = f"<!-- tarot-confessional single-file build: spread={spread} -->\n"
    if title:
        stamp += f"<!-- title={title} -->\n"
    html = html.replace("<!DOCTYPE html>", stamp + "<!DOCTYPE html>", 1)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--spread", required=True, choices=sorted(VALID_SPREADS))
    parser.add_argument("--title", default="")
    args = parser.parse_args()
    try:
        build(skill_dir=args.skill_dir, output=args.output, spread=args.spread, title=args.title)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps({"output": str(args.output), "spread": args.spread, "size_bytes": args.output.stat().st_size}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
