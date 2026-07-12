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

## Run a visual draw

The skill ships with two HTML files. Pick the one that fits how the file will reach the user:

1. **`assets/draw.html`** — template with relative `images/...` and `deck-data.js` references. Only works when the HTML stays inside the bundled directory. Use it for local previewing from a fixed installation path.
2. **Single-file build via `scripts/build_draw_page.py`** — produces one HTML file with every CSS image, every card face, and both scripts inlined as data URIs and `<script>` blocks. Use this whenever the file might be moved, attached to a chat, opened from `/tmp`, or placed in any directory that does not contain the `assets/images/` and `assets/deck-data.js` siblings.

Always run the builder when handing the file to the user. It runs offline, draws from all 78 cards, and produces a `TC1` code without embedding the user's question or identity.

```bash
python3 scripts/build_draw_page.py \
  --skill-dir <path-to-tarot-confessional> \
  --output <workspace>/draw.html \
  --spread S3 \
  --title "关于下一步的三张牌"
```

If the environment cannot open local HTML, tell the user where the file is and offer a conversational draw only after explaining that it loses the visual interaction.

## Decode a returned code

Never manually infer cards from a code. Run:

```bash
python3 scripts/tarot_codec.py decode "<TC1 code>" --deck references/deck.json
```

Treat decoded order, card identity, and orientation as fixed facts. Reject invalid versions, checksums, lengths, duplicate cards, and out-of-range IDs. Read `references/draw-code-protocol.md` only when debugging or explaining the protocol.

## Interpret the reading

Read `references/reading-guidance.md` before composing a reading.

1. Anchor each card to its spread position.
2. Interpret reversals as blocked, internalized, delayed, excessive, or reconsidered energy according to context, not automatically as a negative omen.
3. Connect patterns across cards instead of listing isolated dictionary meanings.
4. Separate observation from possibility. Use phrases such as “这可能映照出” and “你可以留意”.
5. Close with one concise synthesis and one or two practical reflection prompts.

Use this default response shape unless the user asks for something else:

```markdown
### 牌阵
[牌位、牌名与正逆位]

### 解读
[结合问题的整体解读]

### 给你的提醒
[总结与可执行的反思问题]
```

Use `assets/reading.html` as the visual report template. It is currently a static reference: do not claim it contains the user's dynamic reading unless you have actually rendered and safely escaped new content into a separate output file.

## Apply safety boundaries

- Do not predict diagnoses, pregnancy, death, legal outcomes, investment returns, or immediate physical safety.
- Do not frame an outcome as destined, guaranteed, or known by supernatural authority.
- For consequential decisions, present tarot as one reflective input and encourage evidence-based professional advice.
- If the user may be in immediate danger or considering self-harm, pause the reading and prioritize immediate local emergency help, a crisis service, or a trusted nearby person.
- Do not create dependency by claiming the Agent understands the user better than people in their life.

## Bundled resources

- `assets/draw.html`: offline 78-card visual draw experience (uses relative paths; keep inside the skill directory).
- `assets/reading.html`: visual report reference template.
- `assets/images/`: card faces, card back, and page backgrounds used by the HTML files.
- `assets/videos/cards/`: available three-second card motion loops; the set is populated incrementally under the MiniMax daily quota.
- `assets/deck-data.js`: browser-ready canonical deck data.
- `assets/tarot-codec.js`: browser-side `TC1` encoder.
- `scripts/build_draw_page.py`: builds a self-contained single-file draw page with every asset inlined. Always prefer this when the HTML will be moved, attached to a chat, or opened from a non-default location.
- `scripts/tarot_codec.py`: deterministic encoder, decoder, and deck lookup CLI.
- `references/deck.json`: canonical IDs `0..77` and card filenames.
- `references/draw-code-protocol.md`: formal `TC1` protocol.
- `references/reading-guidance.md`: interpretation and wording rules.
