# Claude Code 实战指南

> [!abstract] 概述
> 本文系统性地介绍 Claude Code 的核心概念、最佳实践、配置方法与工作流，帮助你构建高效的 AI 辅助开发环境。

## 目录

- [第一部分：核心概念与最佳实践](#第一部分核心概念与最佳实践)
  - [上下文约束](#上下文约束)  
    - [Memory 精简原则](#memory-精简原则)
    - [Skills 与 Memory 对比](#skills-与-memory-对比)
    - [规则分层策略](#规则分层策略)
  - [插件 vs MCP vs Skills](#插件-vs-mcp-vs-skills)
  - [子代理触发机制](#子代理触发机制)
  - [钩子系统](#钩子系统)
- [第二部分：快速开始](#第二部分快速开始)
- [第三部分：配置详解](#第三部分配置详解)
- [第四部分：工作流实战](#第四部分工作流实战)
- [附录](#附录)

---

## 第一部分：核心概念与最佳实践

### 上下文约束

#### Memory 精简原则

**CLAUDE.md 是什么**

CLAUDE.md 是 Agent 会话的"Memory"，会在每次对话开始时自动加载到上下文中。它充当 Claude Code 的项目知识库和规则手册。

| 原则                 | 说明                  | 示例                         |
| -------------------- | --------------------- | ---------------------------- |
| **Memory ≤ 2000 字** | 只放关键信息          | 语言偏好、架构约束、核心规范 |
| **规则放入 Skills**  | 渐进式加载，按需调用  | 代码风格、测试规范、安全要求 |
| **分层组织**         | 通用 → 领域 → 架构    | 见下方规则分层策略           |
| **显式导入**         | 使用 `@` 控制加载顺序 | `@rules/code-style.md`       |

#### Skills 与 Memory 对比

> [!tip] 核心区别
> **Memory 是"始终记住的"，Skills 是"需要时查手册的"**

| 维度         | Memory (CLAUDE.md)                 | Skills                                                        |
| ------------ | ---------------------------------- | ------------------------------------------------------------- |
| **加载时机** | 每次会话启动时自动加载             | 按需渐进式载入                                                |
| **适用内容** | 语言偏好、架构约束、关键规范       | 代码风格、测试规范、最佳实践、工作流                          |
| **内容大小** | 精简（≤ 2000 字）                  | 可以很详细                                                    |
| **更新频率** | 较少（项目核心信息）               | 较频繁（迭代改进）                                            |
| **递归导入** | 支持最多 5 层                      | 作为被导入对象                                                |
| **性能影响** | 每次对话都占用上下文               | 只在需要时占用                                                |
| **典型示例** | `Language: 中文`、`架构: 微服务`   | `Python PEP 8 规范`、`TDD 工作流`、`React Hooks 最佳实践`     |

**实践示例**：

❌ **错误做法**：将所有规则放入 CLAUDE.md

```text
.claude/CLAUDE.md (5000+ 字)
├── 语言偏好
├── 代码风格（800 字）
├── 测试规范（1200 字）
├── 安全要求（600 字）
├── Git 工作流（400 字）
└── 部署流程（300 字）
```

✅ **正确做法**：Memory 保持精简，规则放入 Skills

```text
.claude/
├── CLAUDE.md (200 字)
│   ├── Language: 中文
│   ├── Tech Stack: Python + FastAPI
│   └── 代码风格: @skills/python-style.md
└── skills/
    ├── python-style.md (800 字)
    ├── testing-standards.md (1200 字)
    └── security-requirements.md (600 字)
```

#### 规则分层策略

Claude Code 支持多层级 CLAUDE.md，每层负责不同粒度的规则：

```text
your-project/
├── .claude/
│   ├── CLAUDE.md            # 通用规则（语言、重要规范）
│   ├── rules/
│   │   ├── code-style.md    # 代码风格指南
│   │   ├── testing.md       # 测试约定
│   │   └── security.md      # 安全要求
│   └── skills/              # 最佳实践集合
│       ├── coding-standards
│       ├── web-design-guidelines
│       ├── tdd-workflow
│       └── git-commit-conventions
├── src/api/
│   └── CLAUDE.md            # 领域规则（API 设计、数据模型）
├── src/frontend/
│   └── CLAUDE.md            # 领域规则（组件规范、状态管理）
├── CLAUDE.md                # 架构规则（项目结构、运行流程）
└── README.md
```

**三层规则模型**：

| 层级       | 位置                   | 职责                     | 示例                         |
| ---------- | ---------------------- | ------------------------ | ---------------------------- |
| **通用层** | `.claude/CLAUDE.md`    | 全局规则，适用于整个项目 | 语言偏好、编码标准、Git 约定 |
| **领域层** | `src/domain/CLAUDE.md` | 特定领域的约束和规范     | API 设计规范、数据库命名规则 |
| **架构层** | `项目根/CLAUDE.md`     | 项目级架构和流程         | 技术栈、目录结构、启动命令   |

### 插件 Vs MCP Vs Skills

| 机制       | 定义                                       | 使用场景                         | 维护方式                                 |
| ---------- | ------------------------------------------ | -------------------------------- | ---------------------------------------- |
| **Plugin** | 斜杠命令、代理、钩子、Skills 和 MCP 的集合 | 某领域完整工作流                 | 官方/社区 Marketplace                    |
| **MCP**    | Model Context Protocol，独立的扩展协议     | 特定工具集成（如数据库、浏览器） | 手动配置到 `.mcp.json`，或者直接使用插件 |
| **Skills** | 项目内可复用的能力模块                     | 项目特定的规范和工作流           | 本地维护在 `.claude/skills/`             |
| **Hooks**  | 在特定事件触发时自动执行的脚本             | 自动化任务（如格式化、测试）     | 配置在 `project/.claude/settings.json`   |

**选择建议**：

1. **优先使用插件**：官方/社区维护，开箱即用
   - Git 工作流：`commit-commands`, `code-review`, `pr-review-toolkit`
   - 开发流程：`feature-dev`, `frontend-design`
   - 安全防护：`security-guidance
   - 浏览器自动化：`playwright`
   - 上下文管理：`context7`

2. **按需配置 MCP**：插件不满足时
   - 自定义工具服务

3. **自定义 Skills**：项目特定的规范
   - 代码风格约定
   - 团队工作流程
   - 业务领域规则

### 子代理触发机制

**子代理是什么**

子代理是处理特定任务的专门 AI 助手，每个子代理：

- 在自己的上下文窗口中运行
- 具有自定义系统提示
- 拥有特定的工具访问权限
- 独立的权限设置

**触发机制**

当 Claude 遇到与子代理描述匹配的任务时，会**自动委托**给该子代理：

```text
用户请求 → Claude 主代理 → 匹配子代理描述 → 委托执行 → 返回结果
```

**内置子代理**：

| 子代理              | 类型     | 触发条件         | 能力                             |
| ------------------- | -------- | ---------------- | -------------------------------- |
| **Explore**         | 只读代理 | 搜索和分析代码库 | 快速遍历、模式匹配、只读操作     |
| **Plan**            | 只读代理 | 进入计划模式     | 收集上下文、制定计划、不执行修改 |
| **General-purpose** | 读写代理 | 复杂多步骤任务   | 探索 + 操作，需要全面能力        |

**扩展子代理**（通过 Plugins 添加）：

| 子代理       | 用途       | 触发示例                 |
| ------------ | ---------- | ------------------------ |
| `architect`  | 架构设计   | "设计这个系统的架构"     |
| `planner`    | 详细规划   | "制定这个功能的实施计划" |
| `e2e-runner` | 端到端测试 | "运行完整的 E2E 测试"    |

**子代理 vs Skills**：

- **子代理**：独立运行的 AI 实例，适合复杂、多步骤任务
- **Skills**：主代理的能力扩展，适合规范、流程、检查清单

### 钩子系统

**什么是钩子**

钩子是在特定事件触发时自动执行的脚本，用于自动化重复性任务。

**执行时机**：

| 钩子类型       | 触发时机   | 典型用途             |
| -------------- | ---------- | -------------------- |
| `PreToolUse`   | 工具执行前 | 验证、警告、参数检查 |
| `PostToolUse`  | 工具执行后 | 格式化、测试、通知   |
| `PreResponse`  | 响应生成前 | 内容过滤、格式检查   |
| `PostResponse` | 响应生成后 | 日志记录、分析       |

**实用钩子示例**：

1. **自动格式化**：代码修改后运行 `prettier --write`
2. **自动测试**：文件保存后运行相关测试
3. **安全检查**：执行 `rm -rf` 命令前发出警告
4. **类型检查**：编辑 TypeScript 文件后运行 `tsc --noEmit`

---

## 第二部分：快速开始

### 新项目初始化流程

> [!note] 前置要求
> 已安装 Claude Code CLI 并完成基础配置

#### 步骤 1：运行自动化设置

```bash
# 在项目根目录运行
claude-code-setup
```

或直接在 Claude Code 中说：

```text
"帮我设置这个项目的 Claude Code"
"推荐这个项目的自动化配置"
```

**Claude 会自动**：

1. 分析代码库结构和技术栈
2. 推荐适合的插件和钩子
3. 生成初始配置文件

#### 步骤 2：创建 CLAUDE.md

在 `/CLAUDE.md` 创建项目记忆（见下方的模板[CLAUDE.md](CLAUDE.md)）。

#### 步骤 3：安装基础插件

```bash
# 添加官方插件市场
claude plugin marketplace add https://github.com/anthropics/claude-plugins-official

# 安装最小化插件集
claude plugin install commit-commands
claude plugin install security-guidance
claude plugin install pr-review-toolkit
```

#### 步骤 4：配置钩子

编辑 `.claude/settings.json`，添加自动化任务（见配置详解部分）。

#### 步骤 5：验证安装

在 Claude Code 中运行：

```bash
/memory          # 查看已加载的 Memory 文件
/plugin:list     # 查看已安装的插件
/hook:list       # 查看已配置的钩子
```

### 配置清单

#### 最小化配置（必装）

适合所有项目的基础配置：

| 插件                | 用途                             | 命令                           |
| ------------------- | -------------------------------- | ------------------------------ |
| `commit-commands`   | Git 提交、推送、创建 PR          | `/commit`, `/commit-push-pr`   |
| `security-guidance` | 安全警告（命令注入、XSS）        | 自动触发                       |
| `pr-review-toolkit` | 代码审查（测试、错误处理、注释） | `/pr-review-toolkit:review-pr` |

#### 前端开发配置

| 插件/工具         | 用途                           |
| ----------------- | ------------------------------ |
| `frontend-design` | 生产级 UI 设计流程             |
| `typescript-lsp`  | TypeScript/JavaScript 语言服务 |
| `biome` (hook)    | 自动格式化                     |

#### Python 开发配置

| 插件/工具     | 用途                |
| ------------- | ------------------- |
| `pyright-lsp` | Python 静态类型检查 |
| `ruff` (hook) | 快速 Python linter  |

#### 全功能配置

包含 19 个插件的完整配置（见原文的 Project Settings）。

---

## 第三部分：配置详解

### CLAUDE.md 模板

#### 基础模板

见[CLAUDE.md](CLAUDE.md)

#### 高级模板（多层导入）

```markdown
---
title: Enterprise Project Rules
version: 2.0.0
---

# 全局规则

## 语言与风格

- Language: 中文
- Code Style: @skills/coding-standards.md
- Git Conventions: @skills/git-commit-conventions.md

## 架构约束

- Architecture: 微服务架构
- API Design: @docs/api-design-principles.md
- Data Modeling: @docs/database-conventions.md

## 开发流程

- TDD Workflow: @skills/tdd-workflow.md
- Review Process: @skills/code-review-checklist.md

## 安全与合规

- Security: @rules/security.md
- Privacy: @docs/privacy-requirements.md

## 领域特定规则

各子项目有独立的 CLAUDE.md：

- @src/api/CLAUDE.md - API 设计规范
- @src/frontend/CLAUDE.md - UI/UX 约定
- @src/worker/CLAUDE.md - 后台任务规则

## 外部引用

- @~/.claude/company-standards.md - 公司级编码标准
- @docs/oncall-runbook.md - 运维手册
```

### Project Settings 详解

#### 完整配置示例

```json
{
  // 钩子配置
  "hooks": {
    "PostToolUse": [
      {
        // 匹配 Write 和 Edit 工具
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bun run check", // 运行检查脚本
            "timeout": 30 // 超时时间（秒）
          }
        ]
      }
    ]
  },

  // 启用的插件
  "enabledPlugins": {
    // Git 工作流
    "github@claude-plugins-official": true,
    "pr-review-toolkit@claude-plugins-official": true,
    "code-review@claude-plugins-official": true,
    "commit-commands@claude-plugins-official": true,

    // 安全与质量
    "security-guidance@claude-plugins-official": true,

    // 开发流程
    "feature-dev@claude-plugins-official": true,
    "superpowers@claude-plugins-official": true,

    // 前端开发
    "frontend-design@claude-plugins-official": true,
    "code-simplifier@claude-plugins-official": true,

    // 浏览器自动化
    "playwright@claude-plugins-official": true,

    // 上下文管理
    "context7@claude-plugins-official": true,

    // 语言服务器
    "pyright-lsp@claude-plugins-official": true,
    "typescript-lsp@claude-plugins-official": true,

    // 开发工具
    "ralph-loop@claude-plugins-official": true,
    "hookify@claude-plugins-official": true,
    "claude-code-setup@claude-plugins-official": true,
    "claude-md-management@claude-plugins-official": true,
    "mgrep@Mixedbread-Grep": true
  }
}
```

### User Settings 配置

#### 完整配置

```json
{
  // 环境变量
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your-api-key",
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
    "API_TIMEOUT_MS": "3000000",
    "FORCE_AUTOUPDATE_PLUGINS": true
  },

  // 自定义状态行
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 0 // 0 = 延伸到边缘
  },

  // 用户级插件（所有项目共享）
  "enabledPlugins": {
    // 用户特定插件
  },

  // 语言设置
  "language": "chinese"
}
```

### Statusline 自定义

#### 状态行配置

在 `~/.claude/settings.json` 中添加：

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 0
  }
}
```

#### 状态行脚本

创建 `~/.claude/statusline.sh`：

```bash
#!/bin/bash
# 从 stdin 读取 JSON 输入
input=$(cat)

# 使用 jq 提取值
MODEL_DISPLAY=$(echo "$input" | jq -r '.model.display_name')
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir')

# 如果在 git 仓库中，显示 git 分支
GIT_BRANCH=""
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null)
    if [ -n "$BRANCH" ]; then
        GIT_BRANCH=" | 🌿 $BRANCH"
    fi
fi

echo "[$MODEL_DISPLAY] 📁 ${CURRENT_DIR##*/}$GIT_BRANCH"
```

**效果示例**：

```text
[Claude Sonnet 4.5] 📁 my-project | 🌿 feature/auth
```

---

## 第四部分：工作流实战

### 场景 1：日常开发流程

```text
1. 编写代码
   ↓
2. /commit                    # 提交代码（自动生成 commit message）
   ↓
3. 继续开发...
   ↓
4. /commit                    # 再次提交
   ↓
5. /pr-review-toolkit:review-pr tests errors  # 提交前审查
   ↓
6. 修复发现的问题
   ↓
7. /commit-push-pr            # 推送并创建 PR
   ↓
8. /code-review               # PR 自动审查（4 个并行代理）
   ↓
9. 根据反馈修改
   ↓
10. PR 合并后
   ↓
11. /clean_gone               # 清理已删除的分支
```

### 场景 2：功能开发流程

使用 `feature-dev` 插件的完整流程：

```bash
/feature-dev Add user authentication with OAuth
```

**Claude 会自动**：

1. 分析需求
2. 制定实施计划
3. 编写代码
4. 编写测试
5. 运行测试
6. 代码审查
7. 文档更新

### 场景 3：前端设计流程

使用 `frontend-design` 插件：

```text
"Create a dashboard for a music streaming app"
"Build a landing page for an AI security startup"
"Design a settings panel with dark mode"
```

**Claude 会自动**：

1. 分析需求
2. 设计布局
3. 选择配色方案（避免通用 AI 美学）
4. 实现响应式设计
5. 添加交互效果

### 场景 4：代码审查流程

#### 提交前审查

```bash
# 1. 编写代码完成
# 2. 运行审查
/pr-review-toolkit:review-pr code errors

# 3. 修复关键问题
# 4. 提交
/commit
```

#### PR 创建后审查

```bash
# 1. 创建 PR
/commit-push-pr

# 2. 自动审查
/code-review

# Claude 会：
# - 启动 4 个审查代理并行运行
# - 对每个问题评分（置信度）
# - 发布置信度 ≥80 的问题评论
# - 如果没有高置信度问题，跳过发布
```

#### 根据反馈修改

```bash
# 1. 收到审查反馈
# 2. 运行针对性审查
/pr-review-toolkit:review-pr comments
# 3. 修复问题
# 4. 推送更新
git push
```

### 场景 5：Ralph Loop（迭代开发）

适用于需要多次迭代的复杂任务：

```bash
/ralph-loop "实现完整的用户认证系统" --completion-promise "DONE"
```

**工作原理**：

1. Claude 开始工作
2. 尝试退出
3. Stop hook 阻止退出
4. Stop hook 将相同的提示反馈回来
5. 重复直到达成完成承诺

---

## 附录

> [!info] 插件清单
> 完整的 19 个插件分类请参见 [第二部分：配置清单](#配置清单)

### A. 推荐子代理库

- [everything-claude-code](https://github.com/affaan-m/everything-claude-code)
  - `architect` - 架构设计
  - `planner` - 详细规划
  - `e2e-runner` - 端到端测试
  - `doc-update` - 文档更新

### B. 参考资料

- [Claude Code 官方文档](https://code.claude.com/docs/zh-CN)
- [Claude Plugins Official](https://github.com/anthropics/claude-plugins-official)

---

> [!tip] 持续改进
> Claude Code 的配置是迭代的。从最小化配置开始，根据项目需求逐步添加插件和规则。定期运行 `/memory` 和 `/plugin:list` 审查配置，保持精简高效。
