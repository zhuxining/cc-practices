# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

这是一个 **Claude Code 插件市场项目**，包含自用/自开发的插件集合和实践指南文档。

- **插件市场配置**: [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- **本地插件**: [plugins/](plugins/) - react-best-practices, review-plugin
- **示例项目**: [sample-project/](sample-project/) - 一个软件项目的配置示例

## Plugin Market Structure

插件通过 [marketplace.json](.claude-plugin/marketplace.json) 定义，支持本地路径和 Git 仓库两种来源：

```json
{
  "name": "cc-practice",
  "plugins": [
    { "name": "local-plugin", "source": "./plugins/xxx" },
    { "name": "remote-plugin", "source": { "source": "github", "repo": "owner/repo" } }
  ]
}
```

## Plugin Development Standards

### 目录结构

```
plugins/<plugin-name>/
├── commands/                   # 斜杠命令（可选）
│   └── <name>.md
├── agents/                     # 自定义代理（可选）
│   └── <name>.md
├── skills/                     # 代理 Skills（可选）
│   └── <skill-name>/
│       └── SKILL.md
├── hooks/                      # 钩子（可选）
│   └── hooks.json
├── .mcp.json                   # MCP 服务器（可选）
└── .lsp.json                   # LSP 服务器（可选）
```

### plugin.json 清单规范

```json
{
  "name": "plugin-name",           // 唯一标识符，斜杠命令命名空间
  "description": "简短描述",          // 在插件管理器中显示
  "version": "1.0.0",              // 语义版本控制
  "author": {
    "name": "作者名"
  },
  "homepage": "https://...",        // 可选
  "repository": "https://...",      // 可选
  "license": "MIT"                  // 可选
}
```

### Skills 规范

每个 Skill 需要包含前置内容和说明：

```markdown
---
name: skill-name
description: 简短描述，说明何时使用此技能
---

# 技能说明

详细说明 Claude 应该如何使用此技能...
```

### 钩子规范 (hooks/hooks.json)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "npm run lint" }]
      }
    ]
  }
}
```

### LSP 服务器规范 (.lsp.json)

```json
{
  "language-id": {
    "command": "server-binary",
    "args": ["serve"],
    "extensionToLanguage": {
      ".ext": "language-id"
    }
  }
}
```

## Current Plugins

| 插件 | 路径 | 说明 |
|------|------|------|
| react-best-practices | [plugins/react-best-practices/](plugins/react-best-practices/) | 57 条 React 优化规则 |
| review-plugin | [plugins/review-plugin/](plugins/review-plugin/) | 代码审查技能 |

## Common Tasks

### 添加新插件

1. 在 `plugins/` 创建插件目录
2. 在插件目录中添加相应目录（commands/skills/hooks 等）
3. 在 [marketplace.json](.claude-plugin/marketplace.json) 中注册

### 本地测试插件

```bash
claude --plugin-dir ./plugins/<plugin-name>
```

### 修改插件

编辑插件目录下的文件，重启 Claude Code 生效。
