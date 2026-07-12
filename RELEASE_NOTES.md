# Release Notes

## v0.1.1 - 2026-07-12

`塔罗树洞` v0.1.1 在 v0.1.0 之上修复了跨平台安装后的关键健壮性问题：抽牌 HTML 现在可以脱离 skill 安装目录单独运行。

### 主要变更

- **新增 `scripts/build_draw_page.py`**：把 `assets/draw.html` 打包成单个自包含 HTML。
  - 所有 CSS `url("images/...")` 替换为 base64 data URI（共 3 张布局图）
  - 78 张牌面图通过 `window.__tarotCardImages` 注入，运行时查表获取 data URI
  - `<script src="deck-data.js">` 与 `<script src="tarot-codec.js">` 内联为内嵌脚本块
  - 输出一个 HTML 文件，**拷贝到任意目录、贴到聊天附件、放在 `/tmp` 都能正常显示**
- **`SKILL.md` 路由更新**：明确告知 Agent 必须使用 builder 生成单文件 HTML，并把相对路径版本仅用于本地预览。
- **`scripts/package_skill.py`**：`expected_layout()` 校验新增 `scripts/build_draw_page.py`，确保包内必带。

### 为什么需要这个变更

旧版 `assets/draw.html` 用的是相对路径（`images/...`、`deck-data.js`、`tarot-codec.js`）。当 Agent 把 HTML 发给用户时（拷贝、附件、临时目录、聊天消息等），HTML 与它的同级资产目录会分离，所有图片和脚本立即失效。v0.1.1 通过单文件打包彻底解决该问题。

### 验收

- `python3 -m unittest discover -s tests` → **68 passed**（含 11 个新增 `test_build_draw_page.py` 用例）
- 单文件 HTML 经实测：在 `/tmp` 单独目录中无任何 sibling 文件即可正常打开
- 三种牌阵（`F1` / `S3` / `R3`）均可生成，输出大小约 32 MB（含全部 78 张牌的 base64）

### 安装

```bash
# 拉取 0.1.1 发行包
tar -xzf tarot-confessional-0.1.1.tar.gz
# 生成单文件抽牌页
python3 tarot-confessional-0.1.1/scripts/build_draw_page.py \
  --skill-dir tarot-confessional-0.1.1 \
  --output ~/Desktop/draw.html \
  --spread S3 \
  --title "关于下一步的三张牌"
# 解码用户返回的抽牌码
python3 tarot-confessional-0.1.1/scripts/tarot_codec.py decode "TC1-S3-..." \
  --deck tarot-confessional-0.1.1/references/deck.json
```

### 已知限制（沿用 v0.1.0）

- 尚未实现 Agent 动态生成个性化解读报告的渲染器
- 完整牌面为项目生成资产，正式发布前仍需确认生成渠道条款与仓库许可证声明
- 不提供确定性预测、专业诊断或紧急救援服务

---

## v0.1.0 - 2026-07-12

v0.1.0 完成离线抽牌、TC1 协议解码、牌库与 Skill 分发骨架。

## v0.0.1 - 2026-07-12

`塔罗树洞` 的首个开源开发预览建立了项目骨架，完成 v0.1 的核心抽牌闭环，并保留 v0.2 MNEME 本地记忆方案。当前版本可离线体验抽牌与密码回传，但 Agent 动态报告生成仍在开发中。

### 主要内容

- 定义 Agent、离线抽牌 HTML、确定性脚本和解读报告之间的完整闭环
- 定义版本化抽牌码、牌库事实层、HTML 安全渲染和失败状态
- 完成抽牌页与报告页的视觉、交互、移动端和无障碍规范
- 完成 v0.2 MNEME 本地记忆、日记、检索、dream 和删除机制设计
- 加入医疗、法律、财务、自伤、人身安全和长期记忆相关边界
- 补齐 README、贡献指南、行为准则、安全策略和开源许可证
- 完成 C 风格「新工笔幻色」78 张东方塔罗牌组与完整牌组联系表
- 抽牌页接入完整牌库，并通过正式 `TC1` 协议生成可校验密码
- 提供浏览器与 Python 同构编码器、稳定牌表、断点生图和统一后处理脚本

### 当前限制

- 尚未实现由 Agent 动态生成个性化解读报告的渲染器
- 完整牌面为项目生成资产，正式发布前仍需确认生成渠道条款与仓库许可证声明
- 尚未建立自动化评测、浏览器测试与跨 Agent 平台兼容性测试
- 不提供确定性预测、专业诊断或紧急救援服务
