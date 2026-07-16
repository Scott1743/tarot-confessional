---
name: tarot-confessional
version: 2.2.0
description: Guide reflective Chinese tarot draws, decode TC1 draw codes, and provide calm symbolic readings for questions about emotions, relationships, choices, uncertainty, or 树洞式倾诉. Use when a user asks for 塔罗、抽牌、牌阵、占卜式自我探索，or returns a TC1 code from the bundled draw page. Do not use tarot as diagnosis, factual prediction, or professional medical, legal, financial, or crisis advice.
---

# Tarot Confessional

Treat tarot as a symbolic reflection tool. Keep the experience gentle, private, and non-deterministic.

## 完整流程（必须严格遵守）

### 第一步：用户请求抽牌

1. 用户说想抽牌/占卜
2. Agent 询问用户的问题（至少一个简短的澄清问题）
3. Agent 选择合适的牌阵：
   - `F1`: 单张牌，用于聚焦的问题
   - `S3`: 三张牌（现状/阻力/方向），默认用于决策和一般不确定性
   - `R3`: 三张牌（自我/他人/关系），用于人际关系问题

### 首次使用：可选的 Mneme 记忆

首次进入抽牌或倾诉流程时，可自然地问一次：

```text
要不要为以后的自己留一盏小灯？我可以配合 Mneme，把你主动同意留下的阅读整理成只在你本地保存、可搜索也可删除的记忆。
```

- 用户拒绝或暂不决定：立即继续普通流程；不要在同一次会话重复推销。
- 用户说“下次提醒我记住”“帮我记忆”或同意：引导安装 Mneme 轻量 Skill。安装包地址读取环境变量 `FOREST_WHISPERS_MNEME_RELEASE_URL`；未设置时使用：`https://github.com/Scott1743/mneme/releases/download/v2.2.0/mneme-2.2.0.zip`。
- 安装必须由用户明确同意后进行。不要假设 Skill 已安装；用 `scripts/mneme_adapter.py capabilities` 无副作用检查。适配器会依次发现 `MNEME_SKILL_DIR`、`~/.codex/skills/mneme`、`~/.claude/skills/mneme`、`~/.workbuddy/skills/mneme` 和 `~/.agents/skills/mneme`，并从 `MNEME_BUNDLE` 或 `~/.config/mneme/config.toml` 解析 bundle。显式参数既可放在子命令前，也可放在子命令后。
- 安装 Mneme 或开启“未来可参考记忆”不等于允许保存本次阅读。保存仍需本次明确授权。

### 第二步：启动服务器，给用户抽牌页面

**不要直接把原始 `draw.html` 路径交给用户。** Agent 只需要启动服务器；服务器会自动生成一个把牌面、牌背和背景全部编码为 Base64 data URI 的自包含 draw 页面，再提供 URL：

```bash
python3 scripts/serve.py --skill-dir <path-to-tarot-confessional>
```

服务器会：
- 绑定到 `0.0.0.0`，可以从任何接口访问
- 在 `/` 提供自包含的 `draw.html` 页面，脱离资源目录也能显示图片
- 打印 JSON 格式的 URL 信息
- 默认在 15 分钟无访问后自动退出；用户返回 TC1 码后，Agent 不再保留旧服务进程

从输出中提取 `draw` URL 并给用户：
```json
{"draw": "http://localhost:8080/", "reading": null}
```

告诉用户：**"请点击这个链接开始抽牌：[URL]"**

### 第三步：用户抽牌并返回 TC1 码

1. 用户在 draw.html 页面上抽牌
2. 页面会生成一个 `TC1-...` 格式的抽牌码
3. 用户把 TC1 码复制回给 Agent

### 第四步：解码 TC1 码

**永远不要手动推断牌面！** 必须使用脚本解码：

```bash
python3 scripts/tarot_codec.py decode "<TC1 code>" --deck references/deck.json
```

解码结果会告诉你：
- 每张牌的 ID 和名称
- 正逆位
- 抽牌顺序

### 第五步：生成解读内容

读取 `references/reading-guidance.md` 然后生成解读：

1. **先回答用户实际问的问题。** 解读开头用一到两句话给出清楚的核心答复，不要让用户读完整篇后仍不知道牌面总体倾向。
   - 是非或结果类问题：明确写“更倾向于会 / 不会 / 目前难以推进 / 条件满足后才可能”，不要只说“都有可能”。
   - 选择或行动类问题：明确写“牌面更支持 A / 暂缓 / 先完成某个条件再行动”，并说明最关键条件。
   - 关系类问题：可以明确回答关系当前更接近靠近、僵持、疏离或有条件修复；不要冒充事实断言对方的隐秘想法、行为或未来决定。
   - 开放式问题：用一句话说清最主要的处境、阻力和方向。
2. 将每张牌锚定到牌阵位置，为核心答复提供可追溯的牌面依据。
3. 解读逆位：根据上下文判断是阻塞、内化、延迟、过度还是重新考虑。
4. 连接牌与牌之间的模式，而不是孤立地列出牌义；若牌面相互矛盾，指出哪股力量当前更强，以及什么条件会改变判断。
5. 分离牌面观察、综合判断和现实事实。核心答复可以明确，但必须写成“就这组牌而言”的倾向性判断，不能包装成已知事实或确定预言。
6. 给出一到两个与答复直接相关、可验证的小行动；反思问题只能帮助用户落实或验证结论，不能代替答复。
7. 遵守「森林密语」文案语法：每段至多一个自然隐喻，然后回到事实、边界或可验证的小行动。

#### 核心答复的校准

- 不要用连续的“也许、或许、可能”稀释整段结论。先说当前最有支持的方向，再用一句话交代不确定性和改变条件。
- 明确不等于绝对。推荐格式是：“**核心答复：就这组牌而言，更支持……；但……是决定结果的关键条件。**”
- 当牌面证据不足或明显分裂时，也要明确说明：“目前不能支持明确的是或否，更适合暂缓到……出现后再判断。”这比罗列两边可能性更有用。
- 高风险问题和关于第三方隐私的问题不做事实性回答，改为明确回答用户可掌控的部分，例如“现在不适合仅凭牌面做这项决定”或“这组牌更支持先核实事实，而不是猜测对方”。

#### 5.1 密语回响：只在用户授权后检索

若已检测到 Mneme，先询问一次是否在解读时参考相关的本地记录。可选项为“允许以后自动参考 / 只参考这一次 / 暂不参考”。未授权时绝不调用 search、不读取 bundle。

在 TC1 解码后、生成解读前，授权为自动或本次时执行：

```bash
python3 scripts/mneme_adapter.py --bundle "$MNEME_BUNDLE" search "<去细节的当前主题>"
```

- 查询只包含主题关键词，最多返回 3 条候选。随后只读取确实相关的 Markdown 页面，最多 3 篇；搜索摘要不是真实来源。
- 当前问题、当前牌面和当前牌位永远优先。没有可靠命中时静默走普通解读。
- 正式牌义解读结束后，**单独**增加“密语回响”小节，结合用户确认过的历史事实进行心理支持，并列出真实日期和 bundle 相对路径。例如“你在 2026-07-02 的记录中也提到工作边界（来源：concepts/work-boundaries.md）”。
- 不得把历史写成心理诊断、人格标签或因果结论；不得说“我一直记得你”。仅一次参考在完成后恢复为关闭。

### 第六步：生成并提供 reading.html（必须！）

**你必须生成 HTML 报告！** 不要只返回纯文本或 markdown。

#### 6.1 创建 reading-data.json

将解读数据写入 JSON 文件：

```json
{
  "spread_type": "三张行动牌阵",
  "title": "沿着风，看看下一步",
  "date": "二〇二六年七月十二日",
  "positions": "现状 · 阻力 · 方向",
  "question": "用户的问题",
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
    "title": "核心答复：变化可以开始，但第一步不是仓促离开",
    "content": "<blockquote>先直接回答用户的问题，再说明牌面依据、关键条件与不确定性。</blockquote>"
  },
  "actions": {
    "title": "带回现实的小事",
    "items": ["事项1", "事项2"]
  },
  "questions": {
    "title": "留给风的问题",
    "items": ["问题1", "问题2"]
  },
  "memory": {
    "enabled": true,
    "title": "旧日的记录也照见了这一步",
    "guidance": "把过去作为参照，不替你定义此刻；这次阅读仍由你现在的感受和选择来决定。",
    "sources": [{"date": "2026-07-02", "title": "工作边界", "path": "concepts/work-boundaries.md"}],
    "dream_enabled": true
  },
  "disclaimer": "免责声明..."
}
```

仅当实际使用了 Mneme 记忆时传入 `memory.enabled: true`。`memory` 只负责呈现被引用的历史内容，不再承担按钮开关。未安装、未授权或无可靠命中时省略 `memory`，报告尾部会显示轻度本地记忆引导；若阅读服务检测到可用的 Mneme 与 bundle，会在服务端自动激活“整理这次回响”按钮。

#### 6.2 构建 reading.html

```bash
python3 scripts/build_reading_page.py \
  --skill-dir <path-to-tarot-confessional> \
  --output <workspace>/reading.html \
  --data <workspace>/reading-data.json
```

#### 6.3 提供 reading 页面

若旧服务仍在运行则停止它，再启动新的服务器：

```bash
python3 scripts/serve.py --skill-dir <path-to-tarot-confessional> --reading <workspace>/reading.html
```

从输出中提取 `reading` URL 并给用户。服务会在 15 分钟无访问后自动退出；需要更长阅读时间时可附加 `--idle-timeout <秒数>`。构建器会在动态牌阵插入完成后再内联图片，避免动态牌面残留 `images/cards/...` 相对路径：
```json
{"draw": "http://localhost:8080/", "reading": "http://localhost:8080/reading"}
```

告诉用户：**"你的解读报告已经准备好了：[URL]"**。若没有 Mneme，不要把安装变成阻碍；报告末尾已有一段可跳过的轻度引导。

### 第七步：查看后整理与保存

启动阅读服务器时会自动检查常见 Mneme Skill 目录及 Mneme 配置中的 bundle。两者都可用时，服务会自动激活报告里的“整理这次回响”按钮及只读审阅端点，不需要重新构建 reading HTML。特殊安装位置仍可显式传 `--mneme-skill-dir`，特殊 bundle 可传 `--mneme-bundle`。按钮会调用 `mneme dream --json`；这不是自动存储，也不修改 bundle。

用户点击按钮或明确说“帮我记住这次阅读”后：

1. 先说明将保存的最小内容（问题摘要、牌面、解读摘要和用户主动补充），询问是否保存；不保存完整聊天。
2. 得到明确同意后，由 Agent 加载 Mneme 批准后的 dream 写侧工作流写入用户本地 bundle，再执行 `mneme reindex`。写入前准确说明影响范围：阅读概念页、`index.md`、`log.md`（若 Mneme 工作流要求）以及可重建的 `.mneme/index.db`；不要声称“只会动一篇文件”。
3. `dream` 的候选仅供整理参考。任何合并、主题页或写入，都要向用户展示并得到确认；不能把 dream 结果当作心理判断。

#### 联动验证与用户汇报

- 不向用户逐条直播参数顺序错误、路径试探、命令重试或“Now / Rebuild”等内部操作。只在需要用户决策或遇到无法自行恢复的阻塞时说明。
- 不得仅凭启动参数就宣称按钮可用。给出报告链接前必须同时确认：服务启动 JSON 含 `mneme_dream`、实际提供的 reading HTML 含 `data-mneme-dream`；若环境允许本地请求，再验证 `POST /mneme/dream` 返回 200。
- 用户只同意保存本次阅读时，不得顺手把“保存动作”“修复过程”或其他元信息另行写入记忆。
- 完成说明应列出实际变更对象和验证结果，清楚区分“阅读已保存”与“dream 只读审阅”。不要在结尾追加与本次目标无关的产品复盘、跟踪表或其他扩展提议。

未安装 Mneme 时，仍然完整生成 reading；用户以后说“帮我记住”再重新提供安装引导即可。

## 安全边界

- 不要预测诊断、怀孕、死亡、法律结果、投资回报或即时人身安全
- 不要把结果描述为注定的、保证的或由超自然权威所知的
- 对于重大决定，把塔罗作为一个反思性输入，并鼓励基于证据的专业建议
- 如果用户可能处于即时危险或考虑自伤，暂停解读并优先寻求紧急帮助
- 不要通过声称 Agent 比用户生活中的人更了解用户来制造依赖

## 内置资源

- `assets/draw.html`: 预构建的 78 张牌抽牌体验（由 serve.py 提供）
- `assets/reading.html`: 视觉报告模板（由 build_reading_page.py 使用）
- `assets/images/`: 牌面、牌背和页面背景
- `assets/videos/cards/`: 可用的三秒牌面动画循环
- `assets/deck-data.js`: 浏览器端的规范牌组数据
- `assets/tarot-codec.js`: 浏览器端的 TC1 编码器
- `scripts/serve.py`: 本地 HTTP 服务器，绑定到 0.0.0.0，在 `/` 提供抽牌页，在 `/reading` 提供解读页
- `scripts/build_reading_page.py`: 构建自包含的解读报告，内联所有图片并渲染动态内容
- `scripts/tarot_codec.py`: 确定性的编码器、解码器和牌组查询 CLI
- `references/deck.json`: 规范 ID `0..77` 和牌面文件名
- `references/draw-code-protocol.md`: 正式的 TC1 协议
- `references/reading-guidance.md`: 解读和措辞规则
