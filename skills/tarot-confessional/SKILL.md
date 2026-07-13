---
name: tarot-confessional
version: 1.0.0
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

### 第二步：启动服务器，给用户抽牌页面

**不要直接把原始 `draw.html` 路径交给用户。** Agent 只需要启动服务器；服务器会自动生成一个把牌面、牌背和背景全部编码为 Base64 data URI 的自包含 draw 页面，再提供 URL：

```bash
python3 scripts/serve.py --skill-dir <path-to-tarot-confessional>
```

服务器会：
- 绑定到 `0.0.0.0`，可以从任何接口访问
- 在 `/` 提供自包含的 `draw.html` 页面，脱离资源目录也能显示图片
- 打印 JSON 格式的 URL 信息

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

1. 将每张牌锚定到牌阵位置
2. 解读逆位：根据上下文判断是阻塞、内化、延迟、过度还是重新考虑
3. 连接牌与牌之间的模式，而不是孤立地列出牌义
4. 分离观察和可能性，使用"这可能映照出"和"你可以留意"等短语
5. 以一个简洁的总结和一两个反思问题结束

### 第六步：生成并提供 reading.html（必须！）

**你必须生成 HTML 报告！** 不要只返回纯文本或 markdown。

#### 6.1 创建 reading-data.json

将解读数据写入 JSON 文件：

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

#### 6.2 构建 reading.html

```bash
python3 scripts/build_reading_page.py \
  --skill-dir <path-to-tarot-confessional> \
  --output <workspace>/reading.html \
  --data <workspace>/reading-data.json
```

#### 6.3 提供 reading 页面

停止之前的服务器（如果还在运行），启动新的服务器：

```bash
python3 scripts/serve.py --skill-dir <path-to-tarot-confessional> --reading <workspace>/reading.html
```

从输出中提取 `reading` URL 并给用户。构建器会在动态牌阵插入完成后再内联图片，避免动态牌面残留 `images/cards/...` 相对路径：
```json
{"draw": "http://localhost:8080/", "reading": "http://localhost:8080/reading"}
```

告诉用户：**"你的解读报告已经准备好了：[URL]"**

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
