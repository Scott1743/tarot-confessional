# Agent Guide

本文件说明自动化 Agent 在本仓库中的工作方式。

## 项目目标

维护一个安全、克制、易安装的中文塔罗与倾诉 Agent Skill。Agent 负责对话和解读，离线 HTML 负责抽牌与报告体验，确定性脚本负责抽牌码和模板渲染。塔罗解读应帮助用户反思，不应制造确定性、恐惧或依赖。

## 核心文件

- `SKILL.md`：运行时行为、触发描述、输出方式与安全边界的唯一事实来源。
- `README.md`：面向使用者的安装、示例和项目定位。
- `CHANGELOG.md`：遵循 Keep a Changelog 结构记录版本变化。
- `RELEASE_NOTES.md`：最近一次公开版本的摘要。
- `docs/superpowers/specs/`：已经确认的产品、协议、视觉和 MNEME 设计。
- `docs/superpowers/plans/`：分阶段实施顺序与验收条件。

实现前先阅读与任务相关的规格。若代码与规格冲突，先修订规格并说明决策，不要让协议和实现静默分叉。

## 修改原则

1. 保持 `SKILL.md` 的 YAML frontmatter 有效，且 `name` 与目录用途稳定。
2. 使用清晰、自然的中文；元数据和跨平台技术字段可使用英文。
3. 不把塔罗结果描述为事实、诊断、保证或不可改变的命运。
4. 涉及医疗、法律、财务、自伤或人身安全时，优先保留专业求助与危机处理边界。
5. 不引入与请求无关的依赖、生成物或大规模重构。
6. 新增行为时同步更新 README、测试样例和变更日志。
7. LLM 不参与抽牌码推测、随机数生成、HTML 转义或 schema 校验；这些工作交给脚本。
8. 抽牌和报告 HTML 默认离线运行，不添加 analytics、远程字体或隐式存储。
9. MNEME 集成默认关闭，任何写入、历史引用或 dream 整理都要求用户明确授权。

## 验证清单

- 检查 `SKILL.md` frontmatter 至少包含 `name` 和 `description`。
- 检查触发描述同时说明“做什么”和“何时使用”。
- 用至少三个场景人工验证：普通占卜、纯倾诉、高风险请求。
- 确认输出没有绝对化预测、隐私诱导或专业诊断。
- 检查 JavaScript 与 Python 抽牌协议共享测试向量。
- 检查 HTML 在断网、360px 移动端、键盘和减少动作模式下可用。
- 检查用户文本经过 schema 校验和 HTML 转义。
- 提交前运行 `git diff --check`，避免空白符错误。

## 提交约定

建议使用 Conventional Commits，例如：

```text
feat: add relationship spread guidance
fix: strengthen crisis response boundary
docs: clarify installation instructions
```

一次提交只处理一个清晰主题。不要提交密钥、个人对话、真实用户隐私或本地工具缓存。
