# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-07-12

### Added

- `scripts/build_draw_page.py` to produce a single-file, fully self-contained draw HTML (all CSS images inlined as data URIs, all 78 card faces inlined through `window.__tarotCardImages`, and both `deck-data.js` / `tarot-codec.js` inlined as `<script>` blocks). The resulting HTML works when copied, attached, or placed in any directory on Windows, macOS, or Linux.
- `tests/test_build_draw_page.py` with 11 cases covering layout inlining, script inlining, 78-card inlining, CLI invocation, and self-containment guarantees.
- `SKILL.md` updated to route Agents through `build_draw_page.py` for any HTML that will be moved, while keeping the bundled `assets/draw.html` only for local preview.
- Package layout now requires `scripts/build_draw_page.py` in the skill bundle.

## [0.1.0] - 2026-07-12

### Added

- Distributable `tarot-confessional` Agent Skill package (`dist/tarot-confessional-0.1.0.{tar.gz,zip}`) with `manifest.json`, `SHA256SUMS`, and `MANIFEST.md`.
- `scripts/package_skill.py` to stage, archive, checksum, and document the skill for release.
- Shared TC1 test vectors confirmed across Python and JavaScript encoders.
- Single-file CLI decoder verified from the staged and archived packages.

## [Unreleased]

### Added

- Interactive offline draw-page prototype with secure local shuffling, three-card selection, reversals, and a copyable prototype draw code.
- Printable offline reading-report prototype with a complete Chinese three-card interpretation.
- Cohesive eight-card Major Arcana prototype image set, card back, and page textures.
- Superpowers-style implementation specification and reproducible image prompts.
- Eastern mystical redesign using Chinese silk-painting imagery, imperial-purple dynamic skies, animated star tracks, moving light, and a dark silk-scroll reading report.
- Canonical 78-card identity table and versioned `TC1` draw-code protocol.
- Matching browser and Python encoders with CRC validation, duplicate-card checks, and deterministic decoding.
- Complete 78-card Style C "New Gongbi Chromatic" deck with Eastern subjects and high-dopamine color contrasts.
- Full-deck browser data export and draw-page integration using the production `TC1` encoder.
- Resumable deck generation, deterministic seeds, normalized Web assets, and a full-deck contact sheet.

## [0.0.1] - 2026-07-12

### Added

- Initial `SKILL.md` skeleton for reflective Chinese tarot readings and emotional support.
- Safety boundaries for high-stakes and crisis-related requests.
- Open-source project documentation and community guidelines.
- Product specification for the offline draw-code-report workflow.
- Visual specification for the draw and reading HTML experiences.
- Opt-in MNEME local memory integration design and phased roadmap.
