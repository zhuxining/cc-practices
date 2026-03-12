---
name: obsidian-knowledge
description: 指导 Agent 助理如何在在共享的 MyObsidian vault 中进行知识管理。当需要创建、整理、检索笔记，处理网页链接，维护每日笔记，或整理 Inbox 时使用。触发关键词：记录、笔记、整理、归档、每日、任务。操作前必须先读取 vault 根目录的 AGENTS.md。
---

# Obsidian Knowledge Management

你与用户共享 MyObsidian vault。用户通过 Obsidian UI 使用，你通过 `obsidian` CLI 使用。这份指南确保你的操作与用户的知识管理习惯保持一致。

## Intent Routing Rules

### 自动执行（无需确认）

以下情况直接执行 Intent Router，不询问意图：

- 消息**仅含 URL**（无其他文字，或只有 URL + 空格/标点）
- 消息含 URL + 明确意图词（"保存"、"记录"、"归档"、"clip"、"存一下"、"save"等）

### 需确认后执行

- URL 出现在较长消息中，无法判断用户是要保存还是只是分享/提问
确认示例："我看到这个链接，要保存到 Obsidian 吗？还是只需要我读一下？"

### 不触发

- 纯文字消息，无 URL
- URL 明显是工具性的（如 localhost、内网地址、文件路径）

---

## First Principle

**每次操作 vault 前，先读取共享规范**：

```bash
obsidian read "AGENTS.md" vault=MyObsidian
```

AGENTS.md 是你和用户共同遵守的规范源，包含目录结构、标签体系、frontmatter 标准、链接规范等。理解规范后再执行操作。

## CLI Usage

所有操作通过 `obsidian` CLI + `vault=MyObsidian` 参数：

```bash
obsidian read "path/to/note" vault=MyObsidian        # 读取笔记
obsidian create "path/to/note" vault=MyObsidian       # 创建笔记
obsidian search "keyword" vault=MyObsidian            # 搜索
```

**优先级原则**：优先使用 `obsidian-cli` 完成所有 vault 操作，而不是文件编辑工具（Read/Write/Edit）。若某个操作不确定如何用 CLI 实现，先委托 **obsidian-cli** skill 获取更多命令细节；确认 CLI 确实无法完成目标后，再考虑使用文件编辑工具。

## Roles

你在知识管理中扮演以下角色，识别用户意图自动切换：

### Note Creator

当用户要求记录、总结、整理信息时：

1. 根据 AGENTS.md 的目录语义判断笔记应放在哪个目录
2. 遵循 frontmatter 规范，额外添加 `source: ai-generated` 字段标记来源
3. 使用 wikilinks `[[]]` 主动链接 vault 中已有的相关笔记（如有）
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
2. 回答时引用已有笔记（如"参见 [[笔记名]]"）
3. vault 内已有的知识优先于外部搜索——先查 vault，不足再补充

### Daily Notes Collaborator

负责向每日笔记追加内容，以及日末整理。**追加任务由 Task Manager 负责**。

**追加内容**：

追加前，根据内容性质判断类型，并在内容前加上对应的 section 标题和换行：

| 内容类型 | section 标题 | 适用场景 |
|---------|-------------|---------|
| 结构化要点 | `### 📝 Notes\n` | 会议记录、学习笔记 |
| 想法/感受 | `### 💭 Thoughts\n` | 自由文本 |
| 网页链接 | `### 🔗 Links\n` | H4 条目，见 Intent Router |

```bash
obsidian daily:append content="### 📝 Notes\n<内容>" vault=MyObsidian
```

时间敏感内容加 `HH:MM` 前缀。

**日末整理**：

当用户提到"整理今天"、"今日总结"、"daily review" 时触发：

1. `obsidian daily:read vault=MyObsidian` 读取当日全文
2. **内容整理**：
   - `## 🤖 Assistant Generated` 内：归并散落的同类 H3 section
   - `## 🤖 Assistant Generated` 外的非任务内容：识别散落的笔记、想法，询问用户是否归入对应 section，**不自动移动，由用户确认**
3. `obsidian write "$(obsidian daily:path vault=MyObsidian)" vault=MyObsidian` 覆写，`## 🤖 Assistant Generated` 内 section 顺序固定为：Notes → Thoughts → Links
4. `obsidian tasks daily vault=MyObsidian` 展示任务清单，供用户核查

### Task Manager

当用户涉及任务查看或更新时：

```bash
# 追加任务（prepend 写入笔记顶部）
obsidian daily:prepend content="- [ ] 任务描述" vault=MyObsidian
# 查看任务
obsidian tasks daily vault=MyObsidian     # 当日笔记的所有任务
obsidian tasks todo path=<笔记路径> vault=MyObsidian          # 指定笔记的未完成任务
obsidian tasks done path=<笔记路径> vault=MyObsidian          # 指定笔记的已完成任务
obsidian tasks todo path="01_Daily" vault=MyObsidian         # 扫描所有每日笔记的未完成任务
# 标记完成（line 为任务在文件中的行号）
obsidian task daily line=<行号> done vault=MyObsidian                    # 当日笔记标记完成
obsidian task path=<笔记路径> line=<行号> done vault=MyObsidian           # 历史笔记标记完成
```

**工作流**：

| 场景 | 操作 |
|------|------|
| "今天还有什么没做" | `tasks daily todo` 展示 |
| "完成了 XXX"（当日） | `tasks daily` 找行号 → `task daily line=N done` |
| "完成了 XXX"（历史） | 用户告知日期或笔记名 → `tasks todo path=<路径>` 找行号 → `task path=<路径> line=N done` |
| "最近有哪些没做完的" | `tasks todo path="01_Daily"` 汇总，按笔记（日期）分组展示，提示用户逐条处理或迁移到当日 |
| 迁移历史未完成任务 | 将遗留任务追加到当日笔记，原笔记中标记为`[-]`并添加`(已迁移至[[<笔记名>]])`|


### Intent Router

用户发送网页 URL 时，依次执行：

**Step 1 — 获取正文**

委托 **defuddle** skill 获取干净正文。

若 defuddle 失败（报错或返回空内容）：
- 降级到 `WebFetch` 工具直接抓取页面内容
- 若 WebFetch 也失败：跳过 Step 2，在 Step 3 中仅保存 URL 条目（无摘要无要点，备注"内容无法获取"），告知用户降级原因后结束

**Step 2 — 剖析文章**

从五个维度逐层剖析，输出给用户：

| 维度 | 关注点 |
|------|-------|
| 文本解构 | 核心论点、支撑论据、逻辑关系 |
| 概念提炼 | 关键概念的精确含义及相互关联 |
| 批判审视 | 论证强弱、逻辑漏洞、视角局限 |
| 思想深化 | 隐含前提、未明言假设、哲学基础 |
| 实践转化 | 可行洞见与具体应用方法 |

**Step 3 — 提炼并追加到每日笔记**

先读取当日笔记，检查是否已存在 `### 🔗 Links` section：

```bash
obsidian daily:read vault=MyObsidian
```

- 当日笔记**已含** `### 🔗 Links` → 直接追加 H4 条目，**不加** section header
- 当日笔记**未含** `### 🔗 Links` → 追加时带 section header 前缀

```bash
# 未含 section header 时：
obsidian daily:append content="### 🔗 Links\n<H4 条目>" vault=MyObsidian
# 已含 section header 时：
obsidian daily:append content="<H4 条目>" vault=MyObsidian
```

每条链接格式：

```markdown
#### [页面标题](url)
> 一句话摘要

- 要点一（来自剖析）
- 要点二

**🛠 Tools**: Cursor · Windsurf      ← 工具/软件（如有）
**📈 Stocks**: $AAPL Apple           ← 股票/市场（如有）
**👤 People**: 姓名（身份）           ← 人物（如有）
**📚 Resources**: 书名               ← 书籍/论文（如有）
```

**Step 4 — 询问是否保存完整页面**

追加后询问用户："要保存完整页面到 WebClips 吗？"
- **是** → 全文保存到 `31_WebClips/Assistant_Clips/<标题>.md`，H4 标题行末附 ` → [[标题]]`
- **否** → 结束

例外：若用户原始消息中已明确说"保存全文"、"clip 完整页面"、"save full"等，则跳过询问直接执行保存。

## Skill Delegation

执行各角色时，委托专项 skill 处理具体操作。

### Vault Skills（位于 `MyObsidian/.agents/skills/`）

- **obsidian-markdown** — 创建或编辑 .md 笔记
- **obsidian-bases** — 创建数据库视图（.base 文件）
- **json-canvas** — 创建可视化画布（.canvas 文件）
- **doc-coauthoring** — 写技术文档、方案等结构化内容
- **internal-comms** — 写内部沟通（3P updates、状态报告等）

### 技能优先级说明

`obsidian-knowledge`（本文件）是**主规范**，定义所有角色、工作流和决策逻辑。
`obsidian-cli`（位于 `references/obsidian-cli.md`）是**底层工具参考**，仅描述 CLI 命令语法。
两者不冲突——遇到命令细节疑问时查阅 references/obsidian-cli.md，遇到工作流疑问时以本文件为准。

## Privacy Boundaries

这些是硬性边界，不可违反：

- **不读取/修改**带 `#Private` 或 `#Key` 标签的笔记
- **不操作** `30_Permanent/MyConfig/` 中的敏感配置
- **不操作** `99_Plugconfig/` 中的插件配置
- 遇到上述内容时，告知用户你无法访问并说明原因
