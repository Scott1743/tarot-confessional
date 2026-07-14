# 密语回响：Mneme 2.0.0 轻量联动

森林密语 2.0.0 将 Mneme 视为可选、本地优先的记忆能力。默认不安装、不搜索、不保存。

## 配置

`FOREST_WHISPERS_MNEME_RELEASE_URL` 配置轻量 Skill 的下载地址。默认值：

```text
https://github.com/Scott1743/mneme/releases/download/v2.0.0/mneme-2.0.0.zip
```

`MNEME_SKILL_DIR` 可指向已安装的 Mneme Skill；`MNEME_BUNDLE` 可指向用户的 OKF 本地 bundle。使用 `scripts/mneme_adapter.py capabilities` 检测安装状态时不得读取 bundle。

## 边界

- `search` 只在用户允许参考历史时运行，最多取得三条候选，阅读具体页面后才可引用。
- `dream` 是只读整理审阅；不会保存本次阅读。真正写入须由 Agent 在用户同意后依 Mneme 的 ingest 工作流完成。
- 报告页的整理按钮仅在本地阅读服务配置 `--mneme-bundle` 时可用。静态离线报告不发网络请求。
- 历史引用必须给出日期和 bundle 相对路径，且只能作为当下解读后的独立支持段落。
