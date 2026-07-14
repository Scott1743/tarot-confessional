# 密语回响：Mneme 2.2.0 轻量联动

森林密语 2.0.0 将 Mneme 视为可选、本地优先的记忆能力。默认不安装、不搜索、不保存。

## 配置

`FOREST_WHISPERS_MNEME_RELEASE_URL` 配置轻量 Skill 的下载地址。默认值：

```text
https://github.com/Scott1743/mneme/releases/download/v2.2.0/mneme-2.2.0.zip
```

`MNEME_SKILL_DIR` 可指向已安装的 Mneme Skill；未设置时依次检查 `~/.codex/skills/mneme`、`~/.claude/skills/mneme`、`~/.workbuddy/skills/mneme`、`~/.agents/skills/mneme`。`MNEME_BUNDLE` 可指向用户的 OKF 本地 bundle；未设置时读取 `~/.config/mneme/config.toml` 的 `bundle_path`。使用 `scripts/mneme_adapter.py capabilities` 检测安装状态时不得读取 bundle 内容。

适配器的运行参数可以放在子命令前或后，以下两种写法等价：

```bash
python3 scripts/mneme_adapter.py --skill-dir <mneme> capabilities
python3 scripts/mneme_adapter.py capabilities --skill-dir <mneme>
```

## 边界

- `search` 只在用户允许参考历史时运行，最多取得三条候选，阅读具体页面后才可引用。
- `dream` 是只读整理审阅；不会保存本次阅读。真正写入须由 Agent 在用户同意后加载 Mneme 批准后的 dream 写侧工作流完成。
- Mneme 2.2.0 的本地文件转换是可选预处理：只会调用用户已经安装的工具，不能作为安装或保存本次阅读的理由。
- 报告中的 `memory` 数据只表示实际引用过的历史内容，不决定按钮是否出现。本地阅读服务检测到可用的 Mneme CLI 和 bundle 后会自动激活整理按钮；显式参数只用于覆盖自动发现。静态离线报告不发网络请求。
- 历史引用必须给出日期和 bundle 相对路径，且只能作为当下解读后的独立支持段落。

## 验证清单

向用户宣告“整理这次回响可用”前，依次确认：

1. `serve.py` 的启动 JSON 包含 `mneme_dream`。
2. 服务实际返回的 reading HTML 包含 `data-mneme-dream`，不能只检查构建输入或模板。
3. 环境允许本地 HTTP 请求时，`POST /mneme/dream` 返回 200；否则明确说明只完成了静态与启动状态验证。

保存一次阅读通常不只新增概念页，还会更新导航、日志与可重建索引。汇报时列出实际改动，不要用“只写一篇”掩盖这些配套变更。一次保存授权不覆盖额外的过程记忆或调试记录。
