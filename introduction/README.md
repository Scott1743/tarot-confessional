# 塔罗树洞 · 介绍页（营销）

`introduction/index.html` 是项目面向终端用户的营销落地页。它不在 `skills/tarot-confessional/` 里——它是独立的内容资产，可以托管在 GitHub Pages、个人站点、Notion 嵌入或公众号预览里。

## 内容结构

| 屏 | 内容 | 文件引用 |
|---|---|---|
| 1 · Hero | 森林主视觉 + 钩子文案 + CTA | `森林密语.png` |
| 2 · 怎么玩 | 三步抽牌流程 + 三张真实截图 + MNEME 敬请期待 | `assets/screenshots/draw-{ready,picking,revealed}.jpg` |
| 3 · 私人阅读档案 | 报告页结构 + 三张真实截图 | `assets/screenshots/reading-{cover,spread,body}.jpg` |
| 4 · 安装 | CLI 命令 + 推荐提示词模板 + 发布 CTA | 仅内嵌代码块 |

## 资产来源

| 资源 | 用途 | 来源 |
|---|---|---|
| `森林密语.png` | 页面主视觉 | 品牌主视觉参考 |
| `assets/forest-whisper-bg.jpg` | 长页面背景 | 由主视觉衍生的网页优化版本 |
| `assets/eastern-night-bg_001.jpg` | 旧版夜空背景，暂留素材库 | 项目自带 |
| `assets/purple-silk.jpg` | 复用材质 | 项目自带 |
| `assets/card-back.jpg` | 牌背特写 | 项目自带 |
| `assets/0?-*.jpg`（6 张） | Hero 飘浮牌 | 项目牌库抽出 |
| `assets/screenshots/*.jpg`（6 张） | 真实截图 | 用 `kimi-webbridge` 在用户真实浏览器中对 `draw.html` 与 `reading.html` 各状态实时截取 |

更新截图：

```bash
~/.kimi-webbridge/bin/kimi-webbridge status
# 然后用 navigate / snapshot / click / screenshot 重新生成
```

参考 `scripts/introduction_screenshots.md`（如存在）记录了截图会话步骤。

## 版本同步

`index.html` 里出现以下占位符：

| 占位符 | 来源 |
|---|---|
| `{{VERSION}}` | 由 `scripts/package_skill.py --version` 指定 |
| `{{RELEASE_DATE}}` | 解析 `CHANGELOG.md` 中对应版本小节的日期 |
| `{{PROTOCOL}}` | 写死 `TC1` |
| `{{DECK_SIZE}}` | 数 `skills/tarot-confessional/assets/images/cards/*.jpg` |
| `{{CHANGELOG_SUMMARY}}` | 取 CHANGELOG 该版本前 3 条 bullet 拼接 |

### 工作流

- **源文件**：`introduction/index.html`（保留占位符，由内容作者编辑）
- **渲染脚本**：`scripts/render_introduction.py`
- **发行副本**：`dist/tarot-confessional-<version>/introduction.html`（占位符已替换）
- **触发器**：每次运行 `python3 scripts/package_skill.py --version <x.y.z>`，渲染脚本会自动跑，把渲染好的 `introduction.html` 放进 `dist/` 包。

> 编辑 `introduction/index.html` 后不需要手动渲染——下次 `package_skill.py` 会自动同步。

## 修改文案

直接编辑 `introduction/index.html`。占位符使用 SCREAMING_SNAKE_CASE，前后都用 `{{` `}}`。下次打包生效。

## 本地预览

```bash
# 直接打开 introduction/index.html 预览源版本（含占位符）
open introduction/index.html

# 预览已渲染版本（需要先打包）
python3 scripts/package_skill.py --version 0.1.2
open dist/tarot-confessional-0.1.2/introduction.html
```

或者跑一个简单的本地 server：

```bash
python3 -m http.server -d introduction 8000
# 浏览器打开 http://127.0.0.1:8000
```

## 自媒体风格守则

- 文案围绕"懂你"和"不评判"，避免任何"宇宙告诉你""命中注定"等权威语
- 不宣称预知未来，不替代专业咨询
- 视觉以主视觉的森林绿、天空蓝和日光黄为准，正文用纸张色承接
- 标题使用楷体栈，正文使用系统黑体栈，不引入远程字体

## 不做的事

- 不在 introduction 里调用 `tarot_codec.py`（那是 Agent 的工作）
- 不把 `assets/screenshots/*.jpg` 删掉——它们是真实素材证明
- 不改 `introduction/index.html` 里的占位符写法（破坏渲染脚本）
