# 塔罗树洞

一个面向中文场景的 Agent Skill。它用 Agent 对话理解用户诉求，用离线 HTML 提供有仪式感的抽牌与报告体验，再由大模型完成结合上下文的塔罗解读。

本项目把塔罗视为自我探索工具，而不是确定性预测、专业诊断或高风险决策依据。

> 当前状态：v0.1 开发预览。双 HTML、C 风格「新工笔幻色」完整 78 张牌组、正式抽牌码协议与离线解码器已经完成；Agent 动态报告生成器仍待实现。

## 原型预览

- [打开抽牌页](assets/draw.html)
- [打开解读报告](assets/reading.html)
- [查看完整牌组联系表](assets/images/full-deck-contact-sheet.jpg)

两个 HTML 均可直接离线打开，不加载远程字体、脚本、图片或统计服务。

## 功能

- Agent 先通过对话理解问题并选择合适牌阵
- 浏览器在本地完成安全随机抽牌，生成可校验的抽牌码
- Agent 通过确定性脚本还原牌面，再结合牌义参考和用户上下文解读
- 最终生成可离线阅读、保存和打印的 HTML 报告
- v0.2 可选接入 MNEME，把用户授权的阅读和日记保存在本地知识库
- 内置医疗、法律、财务、危机干预和长期记忆安全边界

## 设计文稿

- [产品与技术总设计](docs/superpowers/specs/2026-07-12-tarot-confessional-product-design.md)
- [双 HTML 体验设计](docs/superpowers/specs/2026-07-12-tarot-html-experience-design.md)
- [v0.2 MNEME 集成设计](docs/superpowers/specs/2026-07-12-mneme-v0.2-integration-design.md)
- [双 HTML 原型实现规格](docs/superpowers/specs/2026-07-12-tarot-html-prototype-implementation.md)
- [分阶段实施计划](docs/superpowers/plans/2026-07-12-tarot-confessional-roadmap.md)

## 抽牌码协议

- `references/deck.json` 提供完整 78 张牌的稳定 ID 与文件名。
- `references/draw-code-protocol.md` 定义正式 `TC1` 密码格式。
- `scripts/tarot_codec.py` 负责确定性编码、解码、校验和牌名查询。
- `assets/tarot-codec.js` 与 Python 使用相同算法，抽牌页已接入正式协议。

## 牌面资产

- `assets/images/cards/` 包含完整 78 张 Web 牌面，统一为 768 × 1152 JPEG。
- 视觉方向为 C 风格「新工笔幻色」：东方人物、建筑与山水叙事，配合紫、青、翠、橙、黄、粉的高明度反差色。
- `references/card-art-direction-c.md` 记录可复现的美术方向，`scripts/generate_deck_art.py` 和 `scripts/process_deck_art.py` 支持断点生成与统一后处理。

## 安装

当前版本用于设计审阅和早期协作，不建议作为完成品安装。未来可用版本会以根目录 `SKILL.md` 为入口，并把脚本、参考资料和 HTML 资产一起打包。

不同 Agent 平台的安装位置和加载方式可能不同，请以对应平台文档为准。

## 使用示例

```text
我最近在考虑要不要换工作，请用三张牌帮我梳理一下。
```

```text
我想找个树洞说说最近的人际关系，不一定要抽牌。
```

## 项目结构

```text
.
├── SKILL.md                 # 当前对话式 Skill 骨架
├── skills/
│   └── tarot-confessional/  # 可独立分发的 Agent Skill
├── Agent.md                 # 仓库内 Agent 协作指南
├── docs/superpowers/        # 产品规格与实施计划
├── README.md                # 项目说明
├── CHANGELOG.md             # 版本变更记录
└── RELEASE_NOTES.md         # 当前设计预览说明
```

## 参与贡献

提交改动前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。安全问题请按 [SECURITY.md](SECURITY.md) 私下报告。

## 免责声明

本项目仅用于娱乐、自我反思和一般性情绪支持，不能替代医生、心理咨询师、律师、财务顾问或紧急救援服务提供的专业帮助。

## 许可证

本项目采用 [MIT License](LICENSE)。
