---
name: tarot-confessional
description: Guide reflective Chinese tarot draws, decode TC1 draw codes, and provide calm symbolic readings for questions about emotions, relationships, choices, uncertainty, or 树洞式倾诉. Use when a user asks for 塔罗、抽牌、牌阵、占卜式自我探索，or returns a TC1 code from the bundled draw page. Do not use tarot as diagnosis, factual prediction, or professional medical, legal, financial, or crisis advice.
---

# Tarot Confessional

Treat tarot as a symbolic reflection tool. Keep the experience gentle, private, and non-deterministic.

## Route the request

1. Distinguish among venting, a focused question, and a tarot reading.
2. Let a user vent without forcing a draw.
3. Ask at most one brief clarifying question when a reading request has no usable focus.
4. Do not request names, birthdays, addresses, or other identifying information.

Choose a spread:

- `F1`: one card for a focused prompt.
- `S3`: situation, friction, direction. Use by default for decisions and general uncertainty.
- `R3`: self, other, relationship. Use for interpersonal questions.

## Start the local server

**Always start the local server before giving the user a draw page.** The server binds to `0.0.0.0` so the URL works from any interface. Run it as a background process:

```bash
python3 scripts/serve.py --skill-dir <path-to-tarot-confessional>
```

The server prints a JSON line with the URLs. Extract the `draw` URL and give it to the user. Keep the server running in the background.

## Decode a returned code

When the user returns a `TC1-...` code, decode it with the deterministic script. Never manually infer cards from a code:

```bash
python3 scripts/tarot_codec.py decode "<TC1 code>" --deck references/deck.json
```

Treat decoded order, card identity, and orientation as fixed facts. Reject invalid versions, checksums, lengths, duplicate cards, and out-of-range IDs.

## Interpret the reading

Read `references/reading-guidance.md` before composing a reading.

1. Anchor each card to its spread position.
2. Interpret reversals as blocked, internalized, delayed, excessive, or reconsidered energy according to context, not automatically as a negative omen.
3. Connect patterns across cards instead of listing isolated dictionary meanings.
4. Separate observation from possibility. Use phrases such as "这可能映照出" and "你可以留意".
5. Close with one concise synthesis and one or two practical reflection prompts.

## Generate and serve the HTML report (REQUIRED)

**You MUST generate an HTML report.** Do not return the reading as plain text or markdown only.

### Step 1: Write the reading data as JSON

Create a JSON file with the reading data:

```json
{
  "spread_type": "三张行动牌阵",
  "title": "关于下一步的三张牌",
  "date": "二〇二六年七月十二日",
  "positions": "现状 · 阻力 · 方向",
  "question": "用户的问题",
  "cards": [
    {
      "image": "01-magician.jpg",
      "name": "魔术师",
      "orientation": "正位",
      "position": "现状 · 此刻之势",
      "title": "解读标题",
      "content": "<p>解读内容...</p>"
    }
  ],
  "synthesis": {
    "title": "合观标题",
    "content": "<blockquote>合观内容...</blockquote>"
  },
  "actions": {
    "title": "可行之事标题",
    "items": ["事项1", "事项2"]
  },
  "questions": {
    "title": "留待自问标题",
    "items": ["问题1", "问题2"]
  },
  "disclaimer": "免责声明..."
}
```

### Step 2: Build the reading HTML

```bash
python3 scripts/build_reading_page.py \
  --skill-dir <path-to-tarot-confessional> \
  --output <workspace>/reading.html \
  --data <workspace>/reading-data.json
```

### Step 3: Serve the reading page

Stop the previous server (if still running) and start a new one with the reading:

```bash
python3 scripts/serve.py --skill-dir <path-to-tarot-confessional> --reading <workspace>/reading.html
```

Extract the `reading` URL from the JSON output and give it to the user. The reading page is self-contained with all images inlined.

## Apply safety boundaries

- Do not predict diagnoses, pregnancy, death, legal outcomes, investment returns, or immediate physical safety.
- Do not frame an outcome as destined, guaranteed, or known by supernatural authority.
- For consequential decisions, present tarot as one reflective input and encourage evidence-based professional advice.
- If the user may be in immediate danger or considering self-harm, pause the reading and prioritize immediate local emergency help, a crisis service, or a trusted nearby person.
- Do not create dependency by claiming the Agent understands the user better than people in their life.

## Bundled resources

- `assets/draw.html`: offline 78-card visual draw experience (served by `serve.py`).
- `assets/reading.html`: visual report template (used by `build_reading_page.py`).
- `assets/images/`: card faces, card back, and page backgrounds.
- `assets/videos/cards/`: available three-second card motion loops.
- `assets/deck-data.js`: browser-ready canonical deck data.
- `assets/tarot-codec.js`: browser-side `TC1` encoder.
- `scripts/serve.py`: local HTTP server bound to 0.0.0.0; serves draw page at `/` and optionally reading at `/reading`.
- `scripts/build_draw_page.py`: builds a self-contained single-file draw page (for offline/attachment use).
- `scripts/build_reading_page.py`: builds a self-contained reading report with all images inlined and dynamic content rendered.
- `scripts/tarot_codec.py`: deterministic encoder, decoder, and deck lookup CLI.
- `references/deck.json`: canonical IDs `0..77` and card filenames.
- `references/draw-code-protocol.md`: formal `TC1` protocol.
- `references/reading-guidance.md`: interpretation and wording rules.
