# Forest Whispers Tarot Generation

This directory is the source of truth for the next 78-card visual generation pass.
It is intentionally separate from `assets/images/cards/`: generated candidates stay
in a versioned staging directory until they pass review and are normalized into the
runtime card files.

## Design Read

This is a reflective tarot deck for a private, browser-local ritual. The visual
language is **Art Nouveau shoujo jewel tarot**: an elegant human figure, refined
manga linework, a symmetrical ornamental frame, luminous pastel jewel colors and a
dense field of readable symbols. The reference image is used for general visual
qualities only; no composition, character or decorative motif is copied.

### Visual language, written down

- **Composition:** vertical 2:3 full card face, human portrait or three-quarter figure
  as the emotional center, with symbolic foreground, middle distance and dreamlike
  background woven into one continuous vignette.
- **Line and surface:** crisp dark-blue contour, delicate interior manga linework,
  clean cel shading, white highlights and controlled crystalline sparkle.
- **Palette:** powder blue, ice white, blush pink, pale lavender and cool silver,
  plus one deeper jewel-tone accent chosen per suit. Avoid sepia and muddy neutrals.
- **Card grammar:** rounded white outer edge, symmetrical Art Nouveau frame integrated
  with flowers, crystals, vines and suit emblems, plus one blank bottom title plaque.
- **Symbol hierarchy:** face first, meaningful gesture second, defining tarot symbol
  third, environmental metaphor last. Numbered Minor Arcana retain exact suit counts.

### Extra style prompt

Append this mental check to every generation request: **“A collectible tarot card,
not a character poster. Let the face carry emotion, the gesture reveal the conflict,
and the border repeat the card's symbol. Use crisp ink, pale jewel color and precise
ornament. Keep every detail readable; do not fill space with unrelated decoration.”**

Human figures carry the Major Arcana and court-card roles. Their age, clothing,
gesture and gaze communicate archetype without becoming generic fantasy portraits.
Animals may appear as small symbolic companions when a card calls for one, but they
never replace the human archetype or become the deck-wide hook.

The forest setting is optional rather than mandatory. Weather, architecture, plants,
crystals and distant figures should be chosen only when they clarify the card meaning.
Prompts must not name, imitate or reproduce a specific film, artist, animation studio,
copyrighted character or recognizable franchise design.

The four suits use stable material anchors:

| Suit | Material language | Emotional register |
|---|---|---|
| Wands | flowering branch, ember, sun-warmed wood | initiative, heat, courage |
| Cups | porcelain vessel, water, lotus, rain | feeling, intimacy, imagination |
| Swords | straight blade, wind, paper, clear sky | thought, conflict, truth |
| Pentacles | jade disc, grain, soil, craft | body, work, resources |

Every numbered Minor Arcana must show the exact rank count of its original suit
object. Human gesture provides action and emotion but may never replace the staffs,
cups, swords or jade discs.

Major Arcana cards use recurring **ornamental thresholds**: arches, mirrors, windows,
chains, stairs, curtains and portals that connect portrait and symbolic landscape.

## Upright / Reversed Pair Contract

Every card is generated as a pair, in this order:

1. Generate the upright image at `768x1152`.
2. Use that exact upright file as the `--subject-ref` input for the reversed call.
3. Keep the same character, costume, objects, palette, line quality, camera,
   border treatment, and location. Change only the `reversed_transform` described
   in `card_plan.json`.
4. Reject a reversed image when it invents a new protagonist, changes the suit
   material, removes the defining symbols, or becomes a generic dark version.

The reversed image is **not** a 180-degree CSS rotation. The pair shares a visual
identity while the reversed state changes the relationship between the same
elements: blocked path, spilled water, hidden light, tangled branch, broken rhythm,
or a figure turning away. Runtime integration must add an explicit `upright` and
`reversed` image path to deck data and stop rotating the upright bitmap.

## Files

- `card_plan.json`: 78 card records. Each record has a stable anchor, upright scene,
  and reversed transformation.
- `generate_deck_mmx.py`: deterministic, resumable `mmx` wrapper. It generates
  upright first, then reversed from the upright reference.
- `deck_generation_plan.md`: human review sheet with all 78 card directions.

## Commands

Check auth and inspect the exact calls without spending quota:

```bash
mmx auth status
python3 assets/gen_scripts/generate_deck_mmx.py --dry-run --stage both
```

## Generation Plan and Gates

1. **Plan lock**: validate all 78 identities, anchors and pair transforms.
2. **Four-pair pilot**: generate upright + reversed for one character, object,
   group and landscape card. Approve pair consistency before continuing.
3. **Upright pass**: generate all 78 upright candidates only.
4. **Upright review**: reject unreadable symbols, wrong counts, generic fantasy,
   fake writing and cards that cannot be identified at 160px width.
5. **Reversed pass**: after upright approval, generate reversed candidates using
   each approved upright as the mandatory reference.
6. **Pair review**: compare every pair side by side. Reject identity, costume,
   location, palette or symbol drift.
7. **Promotion and runtime migration**: normalize approved files, mirror them into
   the Skill, add explicit upright/reversed paths to deck data, and remove runtime
   bitmap rotation.

Generate a small pilot first. Run the four IDs separately so failures remain easy
to diagnose:

```bash
python3 assets/gen_scripts/generate_deck_mmx.py \
  --stage both --start 1 --end 1 --workers 1
python3 assets/gen_scripts/generate_deck_mmx.py \
  --stage both --start 29 --end 29 --workers 1
python3 assets/gen_scripts/generate_deck_mmx.py \
  --stage both --start 36 --end 36 --workers 1
python3 assets/gen_scripts/generate_deck_mmx.py \
  --stage both --start 45 --end 45 --workers 1
```

Do not start the full run until four representative pair types pass review:

- Character: `01-magician`
- Object-led: `36-ace-of-cups`
- Group: `45-ten-of-cups`
- Landscape/action: `29-eight-of-wands`

`mmx --subject-ref` is documented as a character-consistency reference, not a
general image-edit endpoint. It is still the required upright input for every
reversed call, but object-led and landscape cards need this pilot gate. If those
pairs drift, stop and revise the prompt/reference strategy before spending quota
on all 156 images.

After the pilot gate passes, generate and review all upright images:

```bash
python3 assets/gen_scripts/generate_deck_mmx.py \
  --stage upright --start 0 --end 77 --workers 2
```

Only after upright approval, generate the reversed pass:

```bash
python3 assets/gen_scripts/generate_deck_mmx.py \
  --stage reversed --start 0 --end 77 --workers 2
```

Existing files are skipped unless `--force` is passed. Keep workers at `1` or `2`
unless the active MiniMax quota explicitly supports more concurrency.

Outputs are written to:

```text
assets/images/generated-sources/forest-deck-v2-animals/
  upright/00-fool.jpg
  reversed/00-fool.jpg
  ...
  generation-log.jsonl
```

Do not copy candidates over `assets/images/cards/` directly. Review contact sheets,
run the pair checklist, then normalize approved upright and reversed files with a
separate promotion step. Keep the same filenames and card IDs across both source
and `skills/tarot-confessional/` copies.

The reversed stage uploads the generated upright candidate to MiniMax as a subject
reference. Generated card art must not contain user questions, readings, personal
data, or other private workspace material.

## Review Checklist

- [ ] All 78 upright records exist and are visually legible at 160px wide.
- [ ] Each reversed record has the matching upright image as its reference.
- [ ] Major Arcana symbols remain recognizable without relying on text.
- [ ] Minor Arcana show the correct suit material and count/rank cue.
- [ ] Every living protagonist is a small woodland animal; no human anatomy appears.
- [ ] Court cards read as animal + role + suit, not generic animal portraits.
- [ ] Mist and bloom create depth without obscuring the focal action or suit count.
- [ ] Finish combines lively drawn gesture, CG gouache texture and cinematic animation light.
- [ ] No image imitates a recognizable film, studio, artist or copyrighted character.
- [ ] No card contains generated writing, pseudo-letters, watermark, logo, or frame text.
- [ ] No card makes a diagnosis, prophecy, threat, or claim of certainty.
- [ ] Upright and reversed are one pair, not two unrelated artworks.
- [ ] Approved assets are normalized to `768x1152` JPEG and mirrored into the Skill.
