# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-07-16

### Changed

- 解读流程要求先对用户原问题给出相对明确的“核心答复”，再展开逐牌依据、关键条件和现实验证点。
- 是非、选择、关系和开放式问题分别采用可执行的倾向性答复；牌面冲突时判断主次，证据不足时明确说明暂不能下结论。
- 明确答复仍保持反思工具边界：不预测第三方隐秘事实，不把牌面包装成确定预言，高风险问题直接说明不应依据牌面行动。
- README、介绍页、测试与发行产物同步升级至 `2.2.0`。

## [2.1.1] - 2026-07-15

### Changed

- Mneme 轻量联动默认指向 v2.2.0，写入流程改为加载 Mneme 批准后的 dream 写侧工作流；明确本地文件转换只使用用户已有的工具，不在此流程自动安装软件。
- 安装命令、下载链接、介绍页与 README 同步升级至 `2.1.1`。

## [2.1.0] - 2026-07-14

### Changed

- introduction 页面新增「密语回响」路径段，明确展示当下阅读、保存授权与未来引用的关系，并区分 2.1.0 当前版和 1.2.0 无记忆版。
- 安装命令改为指向仓库中的完整 Skill 路径，当前发行下载链接升级至 `2.1.0`。

### Fixed

- Mneme 适配器现在可默认发现 `~/.workbuddy/skills/mneme` 与 `~/.agents/skills/mneme`，并允许运行参数放在子命令前后。
- 阅读服务会从 Mneme 配置自动解析 bundle，在 CLI 与 bundle 都可用时为现有报告自动激活“整理这次回响”，避免接口已启动但 HTML 没有按钮。
- 服务端激活兼容 2.0.0 已生成的 `memory-invite` 与 `memory-echo` 报告，不要求重新构建 HTML。
- Mneme 联动流程新增交付前端到端验证与准确汇报规则，禁止在未检查实际 HTML/端点时宣称按钮可用，也禁止把一次阅读保存授权扩张为额外过程记忆。

## [2.0.0] - 2026-07-14

### Added

- 「密语回响」可选 Mneme 联动：首次使用可征询安装，轻量 Skill 下载地址由 `FOREST_WHISPERS_MNEME_RELEASE_URL` 配置，默认指向 Mneme `2.0.0`。
- `mneme_adapter.py` 提供无副作用的安装检测、最多三条的受限检索与只读 `dream` 审阅调用。
- 阅读报告支持仅在实际使用记忆时显示的“密语回响”心理支持与来源；未安装 Mneme 时显示轻度、可跳过的本地记忆引导。
- 本地阅读服务可选提供 `POST /mneme/dream`，供报告页按钮请求 Mneme 的只读审阅。

### Changed

- 解读流程在 TC1 解码后、牌义生成前增加明确授权的本地记忆检索；正式牌义后才单独结合记忆回应。
- 发布版本升级至 `2.0.0`，版本概念为「密语回响」。

## [1.2.0] - 2026-07-14

### Changed

- 阅读报告完整切换为「森林密语 · 林间回信」，包含明亮森林背景、微风动效、段落入场和同一套文案语法。
- 介绍页截图为宽屏展示做了紧凑优化，并压缩素材以改善网页加载。
- 发布版本升级至 `1.2.0`。

### Fixed

- 抽牌舞台在 `16:9` 宽屏和低高度视口不再让牌组遮住牌位文字。

## [1.1.0] - 2026-07-14

### Changed

- 抽牌页牌桌高度改为跟随牌背实际尺寸，为牌组、三张牌位和文字标签保留稳定间距。
- 宽而矮的桌面视口使用独立紧凑布局，统一收紧标题、牌槽、操作区和页脚的纵向节奏。
- `reading.html` 从旧的钴蓝仪式档案改为明亮的「森林密语 · 林间回信」，统一背景、动效、标题和长文阅读语气。
- 自包含阅读页新增内联专用森林背景，脱离 Skill 资源目录时仍可完整显示。

### Fixed

- 修复 `16:9` 宽屏下中央牌组压住下方牌位文字的问题。
- 修复短视口中扇形牌组展开后可能侵入牌位标签的问题。

## [1.0.0] - 2026-07-14

### Added

- 78 张「钴蓝金线仪式塔罗」正位牌面资产：钴蓝群青底场、古金几何装饰、强中轴对称与人物/物件象征体系。
- 完整 78 张联系表候选与可复现生成计划，作为牌面艺术的审阅来源。

### Changed

- 逆位统一复用正位牌图并在抽牌页、解读页和自包含 HTML 构建中旋转 `180°`。
- 自包含抽牌页从内联 156 张独立正逆位资源收敛为内联 78 张正位资源，减小发行包体积并消除双资源漂移。
- 发布版本升级至 `1.0.0`。

## [0.9.0] - 2026-07-13

### Added

- 78 张全新正位与 78 张逆位森林动画牌面资产，运行时分别读取对应图片。
- 介绍页 Hero 三张 3 秒动态牌面示例：力量、星星、圣杯王后。

### Fixed

- `serve.py` 默认自动构建 Base64 自包含抽牌页，脱离资源目录也能显示图片。
- 修复动态 `reading.html` 牌阵在图片内联之后插入、导致相对路径失效的问题。
- 逆位牌面不再旋转正位图片，改为使用独立逆位资产。

## [0.5.1] - 2026-07-12

### Fixed

- 修复自包含抽牌页翻牌后把图片解析表达式误放进字符串、导致牌面图片地址无效的问题。
- 修复 `serve.py` 调用父类 `do_GET` 时多传 `self`、导致 Python 3.12 请求失败的问题。

### Changed

- 在源码与发行版 `SKILL.md` 的 YAML frontmatter 中加入显式版本号；后续发布均需同步更新。

## [0.5.0] - 2026-07-12

### Added

- **完整 Agent 流程文档**：SKILL.md 重写为六步流程，明确 draw.html 是预构建的，reading.html 是 Agent 生成的。
- **本地服务器 `serve.py`**：绑定到 0.0.0.0，在 `/` 提供抽牌页，在 `/reading` 提供解读页。
- **skills.sh 集成**：README 添加 skills.sh 标签和一键安装命令。

### Changed

- **流程明确化**：draw.html 预构建，Agent 只需生成 reading.html，避免 Agent 错误创建 draw.html。
- **README 全面重写**：更有吸引力的文案，突出产品特点。

## [0.3.0] - 2026-07-12

### Added

- **README 全面重写**：更有吸引力的文案，突出产品特点和使用场景，添加 skills.sh 标签和在线体验链接。
- **GitHub Pages 配置**：新增 `.github/workflows/deploy-pages.yml`，自动部署 introduction 页面到 GitHub Pages。
- **RELEASE_NOTES.md 更新**：明确 v0.3.0 功能状态和版本规划。

### Changed

- **打包规范明确**：dist 输出目录不带版本号，归档文件带版本号（已在 Agent.md 和 cloud.md 中记录）。
- **SKILL.md 强化**：强调必须生成 HTML 报告文件，而非仅返回纯文本或 markdown 格式。

### Fixed

- 修复 Agent 未按设计生成 HTML 报告的问题：通过在 SKILL.md 中明确要求 "You MUST generate an HTML report file"。

## [0.2.0] - 2026-07-12

### Added

- `scripts/build_reading_page.py`：新增解读报告 HTML 生成脚本，将 `reading.html` 模板中的静态示例内容替换为实际解读数据，并内联所有图片资源为 data URI，生成自包含的 HTML 文件。
- `introduction/` 营销页：四屏结构（Hero / 抽牌玩法 / 私人阅读档案 / 安装与提示词），女性向温柔语气，所有文案围绕"懂你"与"不评判"。

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
