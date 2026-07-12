# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2026-07-12

### Added

- `scripts/build_reading_page.py`：新增解读报告 HTML 生成脚本，将 `reading.html` 模板中的静态示例内容替换为实际解读数据，并内联所有图片资源为 data URI，生成自包含的 HTML 文件。
- `SKILL.md`：强调必须生成 HTML 报告文件，而非仅返回纯文本或 markdown 格式。

### Fixed

- 修复 Agent 未按设计生成 HTML 报告的问题：通过在 SKILL.md 中明确要求 "You MUST generate an HTML report file"，确保 Agent 在解读完成后调用 `build_reading_page.py` 生成可视化报告。

## [0.1.2] - 2026-07-12

### Added

- `introduction/` 营销页：四屏结构（Hero / 抽牌玩法 / 私人阅读档案 / 安装与提示词），女性向温柔语气，所有文案围绕"懂你"与"不评判"。
- 真实素材：使用 kimi-webbridge 在真实浏览器中对 `draw.html` 与 `reading.html` 各状态截图（共 6 张），与项目自带牌图、纹理背景一同放进 `introduction/assets/`。
- `scripts/render_introduction.py`：将 `introduction/index.html` 中的 `{{VERSION}}` `{{RELEASE_DATE}}` `{{PROTOCOL}}` `{{DECK_SIZE}}` `{{CHANGELOG_SUMMARY}}` 占位符替换为当前发布版的实际值；CHANGELOG 未命中时退化为最近一条记录，保证 dist 页不会缺失字段。
- `scripts/package_skill.py` 在 stage 时自动调用 `render_introduction_into()`，把渲染好的 `introduction.html` 放进 `tarot-confessional-<version>/`。
- `tests/test_render_introduction.py`（4 用例）：占位符完全被替换、未支持版本走 fallback、渲染不留残余。

### Notes

- 用户后续每次打包时，`introduction` 页内的版本号和 changelog 摘要会由 packager 自动同步，无需手工修改。
- `introduction/index.html` 是源模板（含占位符），`dist/tarot-confessional-*/introduction.html` 才是已渲染的发行版本，二者分别由内容作者和打包流程维护，避免冲突。

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
- Responsive 78-card fan interaction with pointer-position lifting, neighboring-card spread, mobile tap mapping, and roving keyboard navigation.

## [0.0.1] - 2026-07-12

### Added

- Initial `SKILL.md` skeleton for reflective Chinese tarot readings and emotional support.
- Safety boundaries for high-stakes and crisis-related requests.
- Open-source project documentation and community guidelines.
- Product specification for the offline draw-code-report workflow.
- Visual specification for the draw and reading HTML experiences.
- Opt-in MNEME local memory integration design and phased roadmap.
