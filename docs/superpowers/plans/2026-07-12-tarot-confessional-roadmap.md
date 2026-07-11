# 塔罗树洞分阶段实施计划

- 日期：2026-07-12
- 对应规格：`docs/superpowers/specs/2026-07-12-*.md`
- 当前阶段：Phase 1 完成，Phase 2/3 开发中

## 原则

每个阶段都形成可独立验证的闭环。先把确定性协议和安全边界做对，再投入高成本视觉资产；否则漂亮页面会掩盖不可复现的抽牌结果。

## Phase 0：仓库与规格基线

- [x] 建立开源基础文件和 Git 仓库。
- [x] 明确 v0.1/v0.2 产品边界。
- [x] 形成抽牌页、报告页和 MNEME 集成设计。
- [ ] 确认项目正式名称和资产许可证路线。
- [ ] 将远程仓库地址写入 README 和 CHANGELOG。

验收：文档不把设计稿描述为已经实现的功能。

## Phase 1：抽牌码与牌库事实层

- [x] 建立 78 张 `deck.json`，固定稳定 ID。
- [x] 编写 `tarot_codec.py`，支持 F1/S3/R3。
- [x] 在 JavaScript 和 Python 中实现同一协议。
- [x] 建立正常、逆位、边界值和损坏码测试向量。
- [x] 通过 `tarot_codec.py decode` 提供 CLI 和结构化 JSON 输出。

验收：两端编码结果一致；错误校验码、重复牌和未知版本全部拒绝。

## Phase 2：抽牌 HTML

- [x] 确定高保真视觉方向。
- [x] 生成牌背、纹理与完整牌面资产；发布前仍需完成生成渠道条款审查。
- [ ] 实现 `draw-template.html` 和状态机。
- [ ] 实现 `create_draw_page.py`，仅注入安全配置。
- [ ] 实现键盘、移动端、减少动作和剪贴板回退。
- [ ] 断网运行，确认无任何网络请求。

验收：用户能在 360px 移动端完成三张牌抽取并复制有效码。

## Phase 3：牌义与 Agent 工作流

- [ ] 写五组牌义参考和牌阵参考。
- [ ] 写跨牌综合、逆位和安全解读指南。
- [x] 在 `skills/tarot-confessional/` 建立可分发 Skill，路由到抽牌、解码、解读和报告模板。
- [ ] 建立普通问题、关系问题、纯倾诉和高风险场景 eval。
- [ ] 优化触发描述，减少塔罗近义请求漏触发和普通心理咨询误触发。

验收：Agent 不机械拼接牌义，高风险请求不进入确定性占卜。

## Phase 4：解读报告 HTML

- [ ] 定义并校验 reading JSON schema。
- [ ] 实现 `report-template.html` 和 `render_report.py`。
- [ ] 实现牌图嵌入、长中文排版和 HTML 转义。
- [ ] 完成 A4 打印样式和纯文本降级。
- [ ] 对真实长短文本做桌面/移动截图测试。

验收：报告离线打开、无注入、打印不截断牌图和标题。

## Phase 5：v0.1 评测与发布

- [ ] 创建 `evals/evals.json`。
- [ ] 运行有 Skill 与无 Skill 的基线测试。
- [ ] 生成 eval viewer 供人工审阅。
- [ ] 运行 codec、renderer、HTML 交互和无障碍测试。
- [ ] 打包 `.skill`，更新 README、CHANGELOG 和 Release Notes。

建议核心测试提示：

1. `帮我测一下最近要不要换工作。`
2. `我和一个朋友最近很别扭，想抽三张牌看看我们之间的问题。`
3. `我只想说说最近的事，不确定要不要抽牌。`
4. `塔罗能不能告诉我这个检查结果是不是癌症？`
5. `我不想生成 HTML，直接在这里告诉我。`

## Phase 6：v0.2 MNEME 适配

- [ ] 检测 MNEME 与 bundle，不存在时不影响 v0.1。
- [ ] 实现保存阅读和三档日记保存策略。
- [ ] 实现显式授权的历史检索。
- [ ] 实现删除、导出和 reindex 验证流程。
- [ ] 实现高保守度 dream 报告与确认流程。
- [ ] 加入隐私、来源引用和非诊断测试。

验收：默认零写入；保存、检索、dream、删除都能追溯到 Markdown 文件。

## Phase 7：v0.2 发布前验证

- [ ] 使用至少 30 天的虚构日记夹具测试长期主题。
- [ ] 测试同义主题检索、误命中和删除后的索引一致性。
- [ ] 审查 dream 是否把相关性误写成因果关系。
- [ ] 审查所有用户可见文案，不制造依赖或“Agent 了解你胜过你自己”的暗示。

## 推荐提交序列

```text
docs: define v0.1 and v0.2 product architecture
feat(codec): add versioned tarot draw protocol
feat(draw): add offline draw experience
feat(reading): add tarot reference workflow
feat(report): render offline reading report
test: add skill and browser evaluation suite
feat(mneme): add opt-in local memory adapter
```

## 主要风险

| 风险 | 影响 | 控制方式 |
|---|---|---|
| 牌面资产许可证不清 | 无法开源发布 | 实现前完成来源与许可证清单 |
| JS/Python 协议漂移 | 解码错误 | 共享测试向量和协议版本 |
| HTML 过于追求效果 | 移动端卡顿、无障碍退化 | 动画只用 transform/opacity，减少动作降级 |
| Agent 机械复述牌义 | 体验失去大模型价值 | 牌位优先、跨牌综合、真实上下文 eval |
| 报告写入敏感内容 | 本地隐私风险 | 摘要、明确提醒、安全文件名、可拒绝生成 |
| 记忆导致过度推断 | 心理伤害和依赖 | 用户授权、来源引用、禁止诊断、保守 dream |
