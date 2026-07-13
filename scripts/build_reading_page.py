#!/usr/bin/env python3
"""Build a fully self-contained reading HTML page.

Why this exists
---------------
The skill's `assets/reading.html` is a static reference template with
example content. When the Agent generates a reading for the user, we need
to render the dynamic content into a standalone HTML file that works
anywhere — just like `build_draw_page.py` does for the draw page.

This script:
  1. Reads the `reading.html` template
  2. Inlines all image assets as data URIs
  3. Replaces the static example content with the provided reading data
  4. Writes a single self-contained HTML file

Usage
-----
```bash
python3 scripts/build_reading_page.py \
  --skill-dir <path-to-tarot-confessional> \
  --output <workspace>/reading.html \
  --data <path-to-reading-data.json>
```

The JSON data file should have this structure:
{
  "spread_type": "三张行动牌阵",
  "title": "关于下一步的三张牌",
  "date": "二〇二六年七月十二日",
  "positions": "现状 · 阻力 · 方向",
  "question": "我是否应该在近期改变工作方向？",
  "cards": [
    {
      "image": "01-magician.jpg",
      "name": "魔术师",
      "orientation": "正位",
      "position": "现状 · 此刻之势",
      "title": "你手里已经有可以开始的东西",
      "content": "<p>解读内容...</p>"
    }
  ],
  "synthesis": {
    "title": "变化可以开始，但第一步不是仓促离开",
    "content": "<blockquote>合观内容...</blockquote>"
  },
  "actions": {
    "title": "先做两件小事",
    "items": ["事项1", "事项2"]
  },
  "questions": {
    "title": "慢一点回答",
    "items": ["问题1", "问题2", "问题3"]
  },
  "disclaimer": "这份阅读把塔罗作为整理问题的象征工具..."
}
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import datetime
from pathlib import Path


def _data_uri(path: Path) -> str:
    """Convert an image file to a data URI."""
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{payload}"


def _inline_images(html: str, images_dir: Path) -> str:
    """Replace all image references with data URIs."""
    # Layout images in CSS
    for name in ("eastern-night-bg_001.jpg", "purple-silk.jpg"):
        data_uri = _data_uri(images_dir / name)
        html = html.replace(f'url("images/{name}")', f'url("{data_uri}")')

    # Upright and reversed card images in HTML
    for directory in ("cards", "cards-reversed"):
        for card_file in sorted((images_dir / directory).glob("*.jpg")):
            data_uri = _data_uri(card_file)
            html = html.replace(f'src="images/{directory}/{card_file.name}"', f'src="{data_uri}"')

    return html


def _render_card(card: dict, index: int) -> str:
    """Render a single card article."""
    reversed_class = ' reversed' if card.get("orientation") == "逆位" else ""
    alt_text = f"{card['name']}{'逆位' if card.get('orientation') == '逆位' else '正位'}"

    directory = "cards-reversed" if reversed_class else "cards"
    return f'''        <article class="spread-card"><div class="card-frame{reversed_class}"><img src="images/{directory}/{card['image']}" alt="{alt_text}"></div><div class="spread-position">{card['position']}</div><h2 class="spread-name">{card['name']}</h2><span class="orientation">{card['orientation']}</span></article>'''


def _render_entry(card: dict) -> str:
    """Render a reading entry for a card."""
    orientation_suffix = f" · {card['orientation']}" if card.get("orientation") else ""
    return f'''        <article class="entry"><div class="label">{card['position'].split('·')[0].strip()}<br>{card['name']}{orientation_suffix}</div><div class="entry-copy"><h2>{card['title']}</h2>{card['content']}</div></article>'''


def _render_list_items(items: list[str]) -> str:
    """Render a list of items as <li> elements."""
    return "\n".join(f"<li>{item}</li>" for item in items)


def build(*, skill_dir: Path, output: Path, data: dict) -> Path:
    """Build a self-contained reading HTML page."""
    assets_dir = skill_dir / "assets"
    template_path = assets_dir / "reading.html"

    if not template_path.is_file():
        raise FileNotFoundError(f"missing template: {template_path}")

    html = template_path.read_text(encoding="utf-8")

    # Replace cover section
    cover_html = f'''    <header class="cover"><div class="vertical-mark">{data['spread_type']}</div><h1>{data['title']}</h1><div class="cover-meta">{data['date']}<br>{data['positions']}</div></header>'''
    html = _replace_section(html, '<header class="cover">', '</header>', cover_html)

    # Replace summary section
    summary_html = f'''      <section class="summary"><div class="label">所问之事</div><p>{data['question']}</p></section>'''
    html = _replace_section(html, '<section class="summary">', '</section>', summary_html)

    # Replace spread section
    cards_html = "\n".join(_render_card(card, i) for i, card in enumerate(data["cards"]))
    spread_html = f'''      <section class="spread" aria-label="本次牌阵">
{cards_html}
      </section>'''
    html = _replace_section(html, '<section class="spread"', '</section>', spread_html)

    # Replace reading-axis section
    entries_html = "\n".join(_render_entry(card) for card in data["cards"])
    reading_html = f'''      <section class="reading-axis"><div class="qi-line" aria-hidden="true"></div>
{entries_html}
      </section>'''
    html = _replace_section(html, '<section class="reading-axis">', '</section>', reading_html)

    # Replace synthesis section
    synthesis_html = f'''      <section class="synthesis"><div class="label">三牌合观</div><div><h2>{data['synthesis']['title']}</h2>{data['synthesis']['content']}</div></section>'''
    html = _replace_section(html, '<section class="synthesis">', '</section>', synthesis_html)

    # Replace closing section
    actions_html = _render_list_items(data["actions"]["items"])
    questions_html = _render_list_items(data["questions"]["items"])
    closing_html = f'''      <section class="closing">
        <div><div class="label">可行之事</div><h2>{data['actions']['title']}</h2><ol class="numbered">{actions_html}</ol></div>
        <div><div class="label">留待自问</div><h2>{data['questions']['title']}</h2><ol class="numbered">{questions_html}</ol></div>
      </section>'''
    html = _replace_section(html, '<section class="closing">', '</section>', closing_html)

    # Replace disclaimer
    html = html.replace(
        '<footer class="boundary">这份阅读把塔罗作为整理问题的象征工具，不是对职业结果的保证。涉及收入、合同和重大职业决策时，请同时参考真实数据与专业建议。</footer>',
        f'<footer class="boundary">{data["disclaimer"]}</footer>'
    )

    # Inline after dynamic card sections are rendered. Otherwise the newly
    # inserted spread cards retain relative paths and disappear when the file
    # is opened outside the skill directory.
    html = _inline_images(html, assets_dir / "images")

    # Add build stamp
    stamp = f"<!-- tarot-confessional reading build: {datetime.now().isoformat()} -->\n"
    html = html.replace("<!doctype html>", stamp + "<!doctype html>", 1)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    return output


def _replace_section(html: str, start_marker: str, end_marker: str, replacement: str) -> str:
    """Replace a section of HTML between markers."""
    start_idx = html.find(start_marker)
    if start_idx == -1:
        raise ValueError(f"could not find start marker: {start_marker}")

    # Find the matching end marker, accounting for nesting
    depth = 0
    i = start_idx
    while i < len(html):
        if html[i:i + len(start_marker)] == start_marker:
            depth += 1
            i += len(start_marker)
        elif html[i:i + len(end_marker)] == end_marker:
            depth -= 1
            if depth == 0:
                end_idx = i + len(end_marker)
                return html[:start_idx] + replacement + html[end_idx:]
            i += len(end_marker)
        else:
            i += 1

    raise ValueError(f"could not find matching end marker: {end_marker}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--data", required=True, type=Path, help="JSON file with reading data")
    args = parser.parse_args()

    try:
        data = json.loads(args.data.read_text(encoding="utf-8"))
        build(skill_dir=args.skill_dir, output=args.output, data=data)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps({"output": str(args.output), "size_bytes": args.output.stat().st_size}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
