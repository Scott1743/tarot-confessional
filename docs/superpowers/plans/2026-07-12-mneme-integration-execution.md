# 塔罗树洞 × MNEME 1.0 具体执行计划

- 日期：2026-07-12
- 状态：待实施
- 目标版本：塔罗树洞 v0.6.0（可选本地记忆适配）
- 上游依赖：MNEME 1.0.0、OKF 0.1
- 对应设计：`../specs/2026-07-12-mneme-v0.2-integration-design.md`

## 0. 结论与范围

第一版采用“可选外部依赖 + 宿主 Agent 文件工作流”，不复制 MNEME 代码，不直接读写 `.mneme/index.db`，也不把 MNEME 绑定进塔罗核心抽牌流程。

MNEME 1.0.0 当前只提供四个确定性 CLI：

```text
mneme init <path>
mneme reindex
mneme search "<query>" --json [-k N] [--type TYPE]
mneme lint <bundle>
```

`ingest` 不是 CLI，而是宿主 Agent 按 OKF 文件协议完成；`dream` 在 MNEME 中明确冻结。因此 v0.6.0 交付保存、检索、删除、导出与 lint，不承诺 dream。dream 只保留能力探测与后续接入点。

## 1. 不变量

1. 可以无副作用检测 `mneme` 命令是否可用；没有读取授权时，不解析私人 bundle、不写文件、不检索历史。
2. 抽牌与解读主流程不依赖 MNEME；依赖缺失时功能完整降级。
3. 每次授权只覆盖一个动作：创建、保存、检索、删除或导出。
4. 原始聊天默认不保存；阅读记录默认只保存用户确认过的摘要。
5. 日记原文属于用户，不与 Agent 解读合并，也不因保存阅读而自动保存。
6. Markdown 是事实来源，SQLite 索引是可重建派生物。
7. 历史引用必须带 bundle 相对路径和日期，不能转写成性格诊断。
8. 删除先预览影响范围，确认后执行，随后 reindex 并验证搜索无命中。
9. 适配层不执行 `git add`、`git commit`、远程同步或后台定时任务。

## 2. 目标架构

```text
当前对话 / TC1 解码结果 / reading-data.json
                    │
                    ▼
          consent gate（每动作授权）
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
  mneme_adapter.py       MNEME 不可用
  纯数据与文件规划        返回结构化降级结果
          │
          ▼
  OKF Markdown bundle
  sources/ + concepts/ + index.md + log.md
          │
          ▼
  mneme lint / reindex / search
```

边界划分：

- `mneme_adapter.py`：发现依赖、校验数据、生成文件计划、解析 CLI JSON；不负责解读。
- `SKILL.md`：授权对话、调用顺序、历史引用措辞、安全降级。
- MNEME：初始化、lint、索引和检索。
- 宿主 Agent：在用户授权后执行适配器给出的文件计划。

## 3. 数据契约

### 3.1 阅读记忆输入

新增 `references/mneme-reading.schema.json`，固定以下字段：

```json
{
  "schema_version": "1",
  "created_at": "2026-07-12T20:30:00+08:00",
  "question_summary": "用户确认过的问题摘要",
  "spread_id": "S3",
  "draw_code": "TC1-S3-...",
  "cards": [
    {"id": 1, "name": "魔术师", "orientation": "upright", "position": "现状"}
  ],
  "reading_summary": "去诊断化的解读摘要",
  "user_reflection": "可选，用户主动要求保留的感受",
  "possible_actions": ["用户认可或准备采取的行动"],
  "save_level": "summary"
}
```

约束：

- `save_level` 只允许 `summary` 或 `full_source`；`none` 在 consent gate 截止，不进入写入函数。
- `draw_code` 必须先由现有 codec 校验。
- `question_summary`、`reading_summary` 和行动项必须做 Markdown 控制字符与 frontmatter 边界转义。
- 不接受姓名、联系方式、地址、健康诊断或第三方隐私作为结构化标签。

### 3.2 OKF 映射

为兼容 MNEME 推荐词表，第一版只使用标准 type：

| 文件 | OKF type | 用途 |
|---|---|---|
| `sources/reading-<timestamp>-<hash>.md` | `Source` | 用户确认后的阅读记录 |
| `concepts/tarot-reading-<date>-<hash>.md` | `Summary` | 可检索的阅读摘要 |
| `concepts/theme-<slug>.md` | `Concept` | 后续人工确认的长期主题，不自动创建 |

日记使用独立输入契约 `references/mneme-journal.schema.json`：

```json
{
  "schema_version": "1",
  "created_at": "2026-07-12T21:10:00+08:00",
  "related_reading_id": "可选的阅读 memory ID",
  "body": "用户原文",
  "user_summary": "可选，必须由用户确认",
  "next_step": "可选，用户自己写下的小行动",
  "save_level": "summary|full_source"
}
```

日记映射到 `sources/journal-<timestamp>-<hash>.md`（`Source`）和 `concepts/journal-<date>-<hash>.md`（`Summary`）。阅读页与日记页可以互相链接，但不得把两者合并成同一个 source 文件。

塔罗领域类型放在 `tags`，例如 `tarot-reading`、`spread-s3`，避免依赖 MNEME 未注册的自定义 type。

### 3.3 幂等与冲突

- 文件 ID：`sha256(draw_code + created_at + normalized_question)[:10]`。
- 同 ID 且内容相同：返回 `already_saved`，不重复写 log。
- 同 ID 但内容不同：返回 `conflict`，不覆盖，交给用户决定。
- 所有写入先生成 plan，再逐文件落盘；任何一步失败都报告已写文件，不声称整体成功。

## 4. 分阶段实施

### Phase A：冻结真实依赖契约

目标：先消除旧设计与 MNEME 1.0 的漂移。

修改：

- 更新 `docs/superpowers/specs/2026-07-12-mneme-v0.2-integration-design.md`：
  - 命令统一改为 `mneme ...`。
  - bundle 发现顺序以 MNEME 1.0 为准：配置 → 环境变量 → 显式路径 → 向上发现 → `./wiki`。
  - 标明 ingest 是宿主 Agent 工作流、dream 冻结。
- 新增 `references/mneme-compatibility.md`，记录最低版本、CLI 能力和降级矩阵。
- 更新 `RELEASE_NOTES.md`，移除当前版本规划中对 dream 的确定承诺。

测试：

- 文档测试断言不再出现 `scripts/mneme.py`。
- 文档测试断言 dream 标为 deferred，而非 available。
- `mneme --help` smoke test 可发现四个子命令。

提交：

```text
docs(mneme): align integration contract with mneme 1.0
```

### Phase B：实现无副作用适配器

新增：

```text
skills/tarot-confessional/
├── references/
│   ├── mneme-adapter.md
│   ├── mneme-compatibility.md
│   └── mneme-reading.schema.json
└── scripts/
    └── mneme_adapter.py
```

CLI 设计：

```text
mneme_adapter.py capabilities
mneme_adapter.py resolve [--bundle PATH] [--config PATH]
mneme_adapter.py get-preference [--config PATH]
mneme_adapter.py set-preference --history off|once|auto [--config PATH]
mneme_adapter.py plan-save --input reading-memory.json --bundle PATH
mneme_adapter.py parse-search --input search-result.json
mneme_adapter.py plan-delete --memory-id ID --bundle PATH
mneme_adapter.py plan-export --bundle PATH --output PATH
```

所有命令输出 JSON；`plan-*` 只生成操作计划，不写文件。统一结果：

```json
{"status":"ready|unavailable|invalid|conflict","operations":[],"warnings":[]}
```

测试：

- 未安装 `mneme` 返回 `unavailable`，退出码稳定，抽牌流程不失败。
- `capabilities` 只检查命令与版本，不打开私人 bundle。
- 历史偏好有 `unset/off/once/auto` 四种读取状态；首次为 `unset`，询问后才写入用户选择。
- 偏好保存在塔罗自己的 `~/.config/tarot-confessional/settings.json`，不修改 MNEME 配置；测试通过 `--config` 指向临时文件。
- `once` 使用一次后恢复为 `off`，`auto` 可随时关闭。
- 配置、环境变量、显式路径和向上发现的优先级与 MNEME 一致。
- schema 缺字段、非法 TC1、路径穿越、frontmatter 注入均被拒绝。
- plan-save 对相同输入确定性输出相同路径和内容。
- 单元测试不访问真实用户配置或 bundle。

提交：

```text
feat(mneme): add side-effect-free adapter and memory schema
```

### Phase C：接入显式授权的保存流程

Phase C 分成两个连续体验：先引导用户写下日记，再分别决定是否保存阅读和日记。

#### C1：在 reading.html 增加阅读后日记入口

修改 `assets/reading.html`、发行目录副本与 `build_reading_page.py`：

1. 在免责声明之后增加“此刻留下些什么”区域，视觉上与解读正文拉开距离。
2. 默认只显示主问题：`看完这份解读，你最想为此刻的自己留下一句话是什么？`
3. 提供可展开的三个辅助提示：认同/不认同、情绪或身体感受、七天内的小行动。
4. 使用自由文本框，不使用多步表单，不要求全部回答。
5. 提供“复制这段日记”按钮，复制日期、关联阅读 ID、用户原文和可选行动。
6. 页面刷新或关闭即丢失输入；不使用 `localStorage`、cookie、远程请求或自动保存。
7. 空内容时禁用复制；复制失败时保留手动选择文本的降级路径。

Agent 给出报告链接时不立即追问保存，只补一句：

```text
你可以先慢慢看。报告最后留了一小块空白，想写时再写，不写也没关系。
```

用户把日记复制回对话后，Agent 先回应内容，再最多问一个延伸问题。只有用户表达“写完了”“就这些”或主动要求保存，才进入 C2。

#### C2：分别授权保存阅读与日记

修改 `skills/tarot-confessional/SKILL.md`：

1. 阅读与日记是两个独立保存对象，不能用一次同意覆盖两者。
2. 用户分别选择“不保存 / 只存摘要 / 保存确认过的原文”。
3. 未发现 bundle 时，只提供“创建独立本地树洞”的选项，不自动初始化。
4. 用户确认创建后执行 `mneme init <path>`，随后校验 `index.md` 与 `log.md`。
5. 阅读构造 `reading-memory.json`；日记构造 `journal-memory.json`，分别运行 `plan-save`。
6. 向用户展示保存摘要和目标文件；二次确认仅用于 `full_source`。
7. 按 plan 写入 source、summary、index 和 log。
8. 执行 `mneme lint <bundle>`；0 ERROR 才继续。
9. 执行 `mneme reindex`。索引失败时保留 Markdown，明确说明“已保存但暂不可语义检索”。

测试夹具：

- `tests/fixtures/mneme/empty-bundle/`
- `tests/fixtures/mneme/existing-reading/`
- `tests/fixtures/mneme/conflicting-reading/`
- `tests/fixtures/mneme/journal-summary/`
- `tests/fixtures/mneme/journal-full-source/`

验收场景：

- 拒绝保存：bundle 字节级无变化。
- 只存摘要：不含完整聊天和用户未确认原话。
- 只保存阅读：日记原文不进入任何文件。
- 只保存日记：允许关联阅读 ID，但不复制牌义和完整报告。
- 页面日记输入刷新后不恢复，网络请求数为零。
- 页面复制内容保持用户原文，不由脚本润色或补写。
- 重复保存：不产生重复概念页和 log。
- reindex 失败：Markdown 完整、状态准确、可稍后恢复。

提交：

```text
feat(mneme): add consent-gated reading persistence
```

### Phase D：接入历史检索与有来源引用

工作流：

1. 开始解读时先运行 `capabilities`；未安装直接走普通流程。
2. 已安装时读取塔罗侧的历史参考偏好，不读取 bundle 内容。
3. 偏好为 `unset` 时询问一次 `自动参考 / 仅本次 / 暂不参考`；偏好为 `off` 时不再主动询问、不检索。
4. 偏好为 `auto` 或 `once` 时，在 TC1 解码后、生成解读前执行检索。
5. 从当前问题生成短查询，不把完整私密问题直接作为命令参数。
6. 执行 `mneme search "<query>" --json -k 5`；第一版不强制 `--type`，因为读取使用 `Summary`。
7. 通过 `parse-search` 校验 JSON、去重和过滤 bundle 外路径。
8. 读取最多 3 个权威 Markdown 页面；snippet 只用于导航。
9. 过滤低相关结果；零可靠命中时静默按普通流程继续。
10. 报告中以当前问题和当前牌面为主，将实际使用的历史记录单列并附日期与路径。
11. `once` 完成本次检索后立即恢复为 `off`。

引用格式：

```text
你在 2026-07-02 的记录中也提到工作边界
（来源：concepts/tarot-reading-2026-07-02-ab12cd.md）。
```

测试：

- 未安装 MNEME 时解读输出仍完整，且不出现安装报错。
- 仅安装但未授权时不运行 search、不解析 bundle。
- `auto` 每次相关解读可查询；关闭后下一次不查询。
- `once` 只查询一次并自动清除。
- 空结果不虚构历史。
- 恶意或越界 path 不读取。
- 低相关命中不进入解读，不能为了展示记忆而强行引用。
- 相同主题只能表述为“曾出现/再次提到”，不能表述为人格或因果结论。
- 删除后的记录不再进入报告。

提交：

```text
feat(mneme): add cited opt-in history retrieval
```

### Phase E：删除、遗忘与导出

删除采用两段式：

1. `plan-delete` 根据 memory ID 找 source、summary、index 项和 log 项。
2. 向用户展示受影响文件，明确不会删除其他主题页。
3. 用户确认后删除或编辑。
4. 执行 lint、reindex，并用原查询验证无命中。
5. 返回实际变更文件清单。

导出：

- 默认打包 Markdown、图片等事实层文件。
- 排除 `.mneme/`、临时文件和锁文件。
- 输出 ZIP 与 SHA-256；不上传、不发送到远端。
- 若目标已存在，不覆盖。

测试：

- 删除预览零写入。
- 取消删除零写入。
- 删除后无断链、无索引残留。
- 导出包不包含 `.mneme/index.db`。
- ZIP 解压后仍是可读 OKF bundle。

提交：

```text
feat(mneme): add verifiable forget and export workflows
```

### Phase F：端到端评测与发布门禁

建立 30 天虚构数据集，至少覆盖：工作转型、关系边界、一次敏感健康倾诉、一次明确要求遗忘、同义主题和无关噪声。

门禁：

| 维度 | 通过标准 |
|---|---|
| 默认隐私 | 10/10 未授权场景零读写私人 bundle |
| 可选安装 | MNEME 未安装时 100% 完成普通解读；安装后才展示参考选项 |
| 读取偏好 | `off/once/auto` 三种状态行为稳定且可撤回 |
| 保存准确性 | 只存摘要场景不出现完整聊天片段；阅读与日记授权不串联 |
| 日记自主性 | 页面不自动填充、不强迫回答、不改写用户原文 |
| 可追溯性 | 100% 历史陈述含有效 Markdown 来源 |
| 删除一致性 | 删除后 lint 0 ERROR，检索无对应命中 |
| 降级 | MNEME 缺失、无 index extras、索引损坏时塔罗主流程可完成 |
| 安全措辞 | 0 条诊断、人格定性、牌面频率因果结论 |
| 路径安全 | 0 次 bundle 外读写 |

发布动作：

- 同步根目录与发行目录的 `SKILL.md`、脚本和 references。
- 更新两份 `SKILL.md` 的 `version`。
- 更新 README、CHANGELOG、RELEASE_NOTES、MANIFEST 和校验和。
- 重新打包并从 ZIP/TAR 各跑一次无 MNEME 降级测试和完整 MNEME 测试。

提交：

```text
test(mneme): add privacy and lifecycle integration gates
docs: publish optional mneme integration workflow
chore(release): package tarot-confessional 0.6.0
```

## 5. dream 后续路径

在 MNEME 上游重新提供经过测试的 dry-run dream 能力前，塔罗树洞不实现自己的自动 dream。

未来启用必须同时满足：

1. MNEME 发布公开、版本化的 dream 契约。
2. 默认只输出 preview，不修改正式概念页。
3. 用户逐次确认应用变更。
4. 有变更前快照与失败回滚。
5. 禁止自动删除 source、自动 commit 和远程 push。
6. 长期主题评测证明不会把相关性写成因果或诊断。

在此之前，可提供“周期回顾草稿”：只搜索并生成临时报告，不写回 bundle。

## 6. 推荐执行顺序与依赖

```text
Phase A 契约冻结
   ↓
Phase B 纯适配器
   ↓
Phase C 日记引导与保存 ─┐
   ↓               │
Phase D 检索引用    │
   ↓               │
Phase E 删除/导出 ◀┘
   ↓
Phase F 评测与发布
```

关键路径是 A → B → C → D → E → F。不要并行实现保存和删除：删除必须复用保存阶段确定下来的 memory ID、路径与 index/log 格式。

## 7. 首个可交付切片

第一轮只完成 A + B + C，形成最小闭环：

```text
解读完成 → 用户阅读报告 → 可选写下并复制日记 → Agent 先回应
→ 用户分别授权阅读/日记保存 → 生成确定性写入计划
→ 写入独立 Source/Summary → lint → reindex → 返回文件路径
```

这个切片不包含历史检索、删除、导出和 dream。它先证明四件事：用户看完报告后有自然的书写入口、默认零写入、阅读与日记授权分离、MNEME 缺失不影响塔罗。
