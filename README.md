# cc-practices

> Claude Code 实践指南与插件市场

## 概述

这是一个自用的 Claude Code 插件市场，包含实践指南文档和可复用的插件集合。

- **实践指南**: [sample-project/README.md](sample-project/README.md) - Claude Code 核心概念、配置方法、工作流实战
- **示例项目**: [sample-project/](sample-project/) - 展示 Claude Code 配置的最佳实践结构
- **插件集合**: [plugins/](plugins/) - React 最佳实践、代码审查等技能

## 使用方式

### 添加到 Claude Code

```bash
claude plugin marketplace add <本地路径或 git URL>
```

### 插件列表

#### 本地插件 (cc-practices)

| 分类 | 插件 | 说明 |
|------|------|------|
| 最佳实践 | `react-best-practices` | React 性能优化和测试指南（57 条规则） |
| 文档指南 | `skill-development` | Claude Code 技能开发指南和最佳实践 |

#### 官方插件 (claude-plugins-official)

| 分类 | 插件 | 说明 |
|------|------|------|
| Git 工作流 | `commit-commands` | Git 提交、推送、创建 PR |
| Git 工作流 | `github` | GitHub 集成 |
| 代码审查 | `pr-review-toolkit` | PR 审查工具包 |
| 代码审查 | `code-review` | 代码审查技能 |
| 安全 | `security-guidance` | 安全警告（命令注入、XSS） |
| 开发流程 | `feature-dev` | 功能开发完整流程 |
| 开发流程 | `superpowers` | 高级功能集合 |
| 前端开发 | `frontend-design` | 生产级 UI 设计流程 |
| 代码优化 | `code-simplifier` | 代码简化工具 |
| 测试 | `playwright` | 浏览器自动化测试 |
| 上下文管理 | `context7` | 上下文优化工具 |
| 语言服务 | `pyright-lsp` | Python 静态类型检查 |
| 语言服务 | `typescript-lsp` | TypeScript/JavaScript 语言服务 |
| 工作流 | `ralph-loop` | 迭代开发循环 |
| 工具 | `hookify` | 钩子生成工具 |
| 配置 | `claude-code-setup` | Claude Code 自动化设置 |
| 配置 | `claude-md-management` | CLAUDE.md 管理 |

## 文档

详细的 Claude Code 实战指南请查看 [sample-project/README.md](sample-project/README.md)。

## License

MIT
