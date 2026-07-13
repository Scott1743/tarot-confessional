# Cloud Deployment Guide

本文件说明 Skill 的云端部署与分发规范。

## Skill 源目录结构

Skill 源码唯一位于 `skills/tarot-confessional/`，并作为打包脚本的输入源。仓库根目录不得再放置 `SKILL.md` 或第二套运行时资产。

```text
skills/tarot-confessional/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── draw.html
│   ├── reading.html
│   ├── deck-data.js
│   ├── tarot-codec.js
│   └── images/
│       ├── card-back.jpg
│       ├── eastern-night-bg_001.jpg
│       ├── purple-silk.jpg
│       └── cards/  (78 jpg)
├── references/
│   ├── deck.json
│   ├── draw-code-protocol.md
│   └── reading-guidance.md
└── scripts/
    ├── build_draw_page.py
    ├── build_reading_page.py
    └── tarot_codec.py
```

## dist 输出规则

**打包生成出来的目录不应有版本号，但打包的文件要有版本号。**

| 产物 | 命名规则 | 示例 |
|------|----------|------|
| 解压目录 | `tarot-confessional/`（无版本号） | `dist/tarot-confessional/` |
| tar.gz 归档 | `tarot-confessional-<version>.tar.gz` | `dist/tarot-confessional-0.1.4.tar.gz` |
| zip 归档 | `tarot-confessional-<version>.zip` | `dist/tarot-confessional-0.1.4.zip` |
| 校验清单 | `SHA256SUMS` | `dist/SHA256SUMS` |
| 发布说明 | `MANIFEST.md` | `dist/MANIFEST.md` |

### 打包流程

```bash
# 执行打包
python3 scripts/package_skill.py --version <version>
```

### 验证

```bash
# 校验归档完整性
shasum -a 256 -c dist/SHA256SUMS

# 解压验证目录名无版本号
tar -xzf dist/tarot-confessional-<version>.tar.gz -C /tmp/
ls /tmp/tarot-confessional/
```

## 注意事项

- dist 目录中**不应出现带版本号的子目录**（如 `tarot-confessional-0.1.4/`），只保留不带版本号的 `tarot-confessional/`。
- 历史归档文件（`.tar.gz` / `.zip`）保留版本号，可共存于 dist 目录中。
- 每次打包前修改并检查 `skills/tarot-confessional/` 中的唯一运行时源。
