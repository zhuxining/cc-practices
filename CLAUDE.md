# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库概述

这是一个 Claude Code Skills 集合仓库。每个顶层目录是一个独立的技能（skill），技能之间**没有关联**，不要跨技能探索或修改。

## 核心工作流

### 创建/修改技能

使用 `skill-creator` 插件（已启用）来创建新技能。每个技能是一个独立目录，包含 `SKILL.md` 作为入口定义文件。

### 探索技能时的行为准则

- **只聚焦用户所选的技能目录**，不要探索或修改其他技能
- 每个技能是完全独立的，不存在技能间的依赖关系

## 技能目录结构

每个技能的 `SKILL.md` 使用 YAML frontmatter 定义 `name` 和 `description`，后跟详细的技能指令内容。技能可选包含：

- `rules/` — 分类规则文件（如 react-best-practices、rest-api-standards）
- `scripts/` — 可执行脚本（如 stock-analysis 的 Python CLI 工具）
- `config/` — 配置文件
- `references/` — 参考文档
- `assets/` — 模板等资源文件

## 脚本开发

- **Python 脚本**：必须包含 PEP 723 元数据块，使用 `uv run` 执行，用 `uvx ruff check` 检查格式
- **Bash 脚本**：必须使用 `set -euo pipefail`，包含标准头部元数据

详细规范见 `.claude/rules/` 下的对应文件。
