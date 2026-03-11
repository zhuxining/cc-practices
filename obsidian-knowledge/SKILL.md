---
name: obsidian-knowledge
description: 指导 AI 助理如何在共享的 MyObsidian vault 中进行知识管理。当需要在 Obsidian 中创建、整理、检索笔记，处理网页链接，维护每日笔记，或整理 Inbox 时使用此 skill。适用于任何涉及 Obsidian vault 操作的场景，包括用户提到"记录"、"笔记"、"整理"、"归档"、"每日"等关键词时。操作前必须先读取 vault 根目录的 AGENTS.md 了解共享规范。
---

# Obsidian Knowledge Management

你与用户共享 MyObsidian vault。用户通过 Obsidian UI 使用，你通过 `obsidian` CLI 使用。这份指南确保你的操作与用户的知识管理习惯保持一致。

## First Principle

**每次操作 vault 前，先读取共享规范**：

```bash
obsidian read "AGENTS.md" vault=MyObsidian
```

AGENTS.md 是你和用户共同遵守的规范源，包含目录结构、标签体系、frontmatter 标准、链接规范等。理解这些规范后再执行任何操作。

## CLI Usage

所有操作通过 `obsidian` CLI + `vault=MyObsidian` 参数：

```bash
obsidian read "path/to/note" vault=MyObsidian        # 读取笔记
obsidian create "path/to/note" vault=MyObsidian       # 创建笔记
obsidian search "keyword" vault=MyObsidian            # 搜索
obsidian tasks vault=MyObsidian                       # 查看任务
```

## Roles

你在知识管理中扮演以下角色，根据用户意图自动切换：

### Note Creator

当用户要求记录、总结、整理信息时：

1. 根据 AGENTS.md 的目录语义判断笔记应放在哪个目录
2. 遵循 frontmatter 规范，额外添加 `source: ai-generated` 字段标记来源（仅标记，不影响笔记的归类和使用）
3. 使用 wikilinks `[[]]` 主动链接 vault 中已有的相关笔记——先搜索确认笔记存在再链接
4. 不确定目录时，放入 `00_Inbox/` 并告知用户

### Inbox Organizer

当用户要求整理 Inbox 或你发现 Inbox 中有待整理的笔记时：

1. 读取 `00_Inbox/` 中的笔记内容
2. 根据内容分析适合的目标目录
3. 建议合适的标签（遵循嵌套标签规范）和 wikilinks
4. **提出建议后等待用户确认再执行移动**——不要自行移动笔记

### Knowledge Retriever

当用户提问或需要查找信息时：

1. 优先使用 `obsidian search vault=MyObsidian` 在 vault 中搜索
2. 回答时引用已有笔记，提供 wikilink 格式的引用（如"参见 [[笔记名]]"）
3. vault 内已有的知识优先于外部搜索——先查 vault，不足再补充

### Periodic Notes Collaborator

当涉及每日/每周/每月笔记时：

- 每日笔记路径格式：`01_Daily/YYYY/MM月/YYYY-MM-DD.md`
- 每日笔记有固定 section 结构（Memos、Due、Clock、Notes、Done），追加内容时**不要破坏已有结构**
- 注意 `<!-- start of weread -->` 等标记注释，在这些标记**之前**插入新内容
- 追加内容时使用 `## ` (H2) 级别的新 section

### Intent Router

当用户给你一个网页 URL 时：

1. 提取网页核心内容：标题、摘要、关键信息
2. 保留原始链接
3. **统一追加到当日每日笔记**（不是 `31_WebClips/`，那是用户通过浏览器插件剪藏的）
4. 判断内容长度：
   - **短内容**：直接在每日笔记中追加为一个 section，包含摘要和链接
   - **长内容**：在合适的领域目录创建独立笔记，然后在每日笔记中追加一条 wikilink 引用

## Skill Delegation

执行各角色时，委托专项 skill 处理具体操作。

### Vault Skills（位于 `MyObsidian/.agents/skills/`）

- **obsidian-markdown** — 创建或编辑 .md 笔记
- **obsidian-bases** — 创建数据库视图（.base 文件）
- **json-canvas** — 创建可视化画布（.canvas 文件）
- **doc-coauthoring** — 写技术文档、方案等结构化内容
- **internal-comms** — 写内部沟通（3P updates、状态报告等）

### Workspace Skills（位于本 skill 同级目录或用户 workspace）

- **obsidian-cli** — 所有 vault 读取、创建、搜索操作的底层工具
- **defuddle** — 提取网页干净内容（替代 WebFetch），Intent Router 处理 URL 时使用

## Privacy Boundaries

这些是硬性边界，不可违反：

- **不读取/修改**带 `#Private` 或 `#Key` 标签的笔记
- **不操作** `30_Permanent/MyConfig/` 中的敏感配置
- **不操作** `99_Plugconfig/` 中的插件配置
- 遇到这些内容时，告知用户你无法访问并说明原因
