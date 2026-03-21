---
name: obsidian-knowledge
description: 指导 Agent 助理如何在共享的 MyObsidian vault 中进行知识管理。当需要创建、整理、检索笔记，维护每日笔记，管理 _AgentSpace 知识库，或将已提取的网页内容保存到知识库时使用。触发关键词：记录、笔记、整理、归档、每日、任务、保存到知识库、知识、术语、记下来、记住、审计知识库。
---

# Obsidian Knowledge Management

你与用户共享 MyObsidian vault。用户通过 Obsidian UI 使用，你通过 `obsidian` CLI 使用。这份指南确保你的操作与用户的知识管理习惯保持一致。

## First Principle

首次操作 vault 前，读取共享规范：

```bash
obsidian vault=MyObsidian read file="AGENTS"
```

AGENTS.md 包含目录结构、标签体系、frontmatter 标准、链接规范等。同一 session 内已读过则跳过。

**重点关注**：
- **目录语义**：每个顶层目录有明确的内容边界（如 `12_Trading` 是交易执行，`15_Finance` 是宏观金融），理解它们的区分标准
- **`_AgentSpace` 分布**：哪些目录有 `_AgentSpace/`，各自管理什么类型的知识
- **frontmatter 标准**：tags 格式、必填字段等

## CLI Usage

所有操作通过 `obsidian` CLI，`vault=MyObsidian` 始终作为第一个参数：

```bash
obsidian vault=MyObsidian read file="笔记名"          # 按名称读取（无需扩展名）
obsidian vault=MyObsidian read path="folder/note.md"  # 按相对路径读取
obsidian vault=MyObsidian create name="新笔记" content="# 标题" silent  # 创建新笔记（同名则覆写）
obsidian vault=MyObsidian create path="<上一步路径>" content="<重组后全文>" overwrite silent # 覆写现有笔记
obsidian vault=MyObsidian search query="关键词"
obsidian vault=MyObsidian move file="笔记名" to="目标目录/笔记名.md"  # 移动文件（自动更新所有 wikilinks）
```

**Wikilink + Move 时序规则**：

`obsidian move` 会自动更新 vault 中所有指向该文件的 wikilinks。因此正确顺序是：

1. **先建立 wikilinks**（指向文件当前位置）
2. **再执行 move**（Obsidian 自动更新所有引用）

反过来（先 move 再补 wikilinks）会导致引用断裂，需人工修复。

**操作优先级**（从高到低）：

1. **CLI 优先**：所有 vault 操作首选 `obsidian` CLI。命令细节参阅 `references/obsidian-cli.md`
2. **错误恢复**：CLI 报错时，先 `open -a Obsidian` 确保应用已启动，再重试
3. **降级到文件编辑**：确认 CLI 无法完成目标后（如 section 级插入），使用 Edit 工具（见 Section Editing Protocol）
4. **特殊字符降级**：文件名含特殊字符（【】、（）、＆ 等）致 CLI 报错时，降级为 `mv` 命令移动，并手动更新相关 wikilinks（自动更新仅在 `obsidian move` 时生效）

## Section Editing Protocol

> 前提：此协议要求 vault 文件位于本地文件系统，且 Agent 具有文件系统读写权限。

CLI 不支持"在指定标题下插入内容"或"替换某个 section 内容"。遇到此类需求时，使用以下三步协议：

### 触发条件

操作目标是"在某个 H2/H3/H4 标题下添加内容"或"修改/替换某个 section 中的内容"时触发。

### Step 1 — 获取文件绝对路径

笔记的绝对路径 = vault 根路径 + "/" + 相对路径：

```bash
# 获取 vault 根路径
open -a Obsidian && sleep 2 && obsidian vault info=path

# daily note：获取当日笔记相对路径
obsidian vault=MyObsidian daily:path

# 普通笔记：从 search 结果获取相对路径
obsidian vault=MyObsidian search query="笔记名"
```

### Step 2 — 读取当前内容并定位 section

```bash
# 快速查看文件标题结构（可选，长文件时有用）
obsidian vault=MyObsidian outline file="笔记名"
# 读取全文
obsidian vault=MyObsidian read file="笔记名"
```

记录目标 heading 文本及其下的现有内容（到下一个同级或更高级 heading 为止）。

### Step 3 — 用 Edit 工具精准修改

- **插入到 heading 下**：`old_string` = heading 行 + 现有内容，`new_string` = heading 行 + 现有内容 + 新增内容
- **替换 section 内容**：`old_string` = heading 行 + 旧内容，`new_string` = heading 行 + 新内容
- **禁止**整篇覆写，除非执行"日末整理"等明确的全文重组任务

### 安全约束

- 必须先 read 后 edit，不允许盲目 overwrite
- `old_string` 必须包含足够上下文确保唯一匹配
- 涉及 `#Private` / `#Key` 标签笔记时，拒绝操作并告知用户

## Knowledge Protocol

`_AgentSpace/` 是 Agent 自主管理的知识工作目录（详见 AGENTS.md）。目录内部结构由 Agent 自行决定和维护。

**`_AgentSpace/` 分布模型**：vault 中存在多个 `_AgentSpace/`，分布在各领域目录下（详见 AGENTS.md 的 _AgentSpace Convention）。LEARN 时根据内容所属领域选择对应 `_AgentSpace/`；READ 搜索时在 query 中使用 `path:_AgentSpace` 可匹配所有领域下的 `_AgentSpace/` 目录。

以下操作适用于所有 `_AgentSpace/` 目录下的笔记。

- **READ**：对话涉及已知概念时，搜索 `_AgentSpace/` 并融入回答（执行者：Knowledge Retriever）
- **LEARN**：需要记录新知识到 `_AgentSpace/` 时，执行完整流程：
  1. **Search** — `obsidian vault=MyObsidian search query="关键词 path:_AgentSpace"` 搜索已有笔记
  2. **Read** — 对搜索结果逐条 read，理解现有内容覆盖范围
  3. **Decide** — 已有笔记覆盖该知识 → 转 UPDATE；无匹配 → CREATE
  4. **Execute** — 创建新笔记或更新已有笔记
  5. **Link** — 用 `[[wikilinks]]` 与相关笔记建立关联
- **LINK**：创建/更新知识笔记时，使用 `[[wikilinks]]` 引用相关已有笔记（利用 Obsidian 原生反向链接）
- **UPDATE**：更新已有知识笔记时，直接修改内容并更新 frontmatter `updated` 字段（执行者：Note Editor）

**主动 LEARN 规则**：对话中出现以下情况时，Agent 应主动建议记录到 `_AgentSpace/`（而非等待用户指令）：
- 用户纠正了 Agent 对业务概念的理解（如："12_Trading 是交易执行相关的，不是泛金融知识"）
- 用户澄清了目录分类标准（如：某类笔记应放 A 目录而非 B 目录）
- 对话中出现了 `_AgentSpace/` 尚未收录的领域术语或规则
- 用户做出了重要的技术/业务决策，且决策理由值得沉淀
- 用户反复解释同一个概念或约定（说明 Agent 缺少持久化记忆）

建议方式：简短提示"这个纠正/决策要记录到知识库吗？（建议存入 `<具体领域>/_AgentSpace/`）"，由用户确认后执行 LEARN。不打断主要对话流程。

所有 `_AgentSpace/` 笔记遵循 AGENTS.md 的 frontmatter 标准，额外添加 `source: ai-generated` 和 `managed-by: agent`。

**`_AgentSpace/` 笔记 frontmatter 模板**：

```yaml
---
tags:
  - Domain/Subdomain
  - Topic
source: ai-generated
managed-by: agent
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

tags 统一使用多行 YAML list 格式（每行一个 `- tag`），不使用 inline array `[tag1, tag2]`。

## Roles

识别用户意图语义，匹配最相关的角色。复杂任务可多角色协作（如 Knowledge Organizer 整理时自然触发 LEARN 流程）。常见意图映射：

1. 涉及每日笔记内容 → Daily Notes Collaborator
2. 涉及每日笔记任务 → Daily Task Manager
3. 涉及保存/提炼网页内容 → Clipping Save
4. 涉及整理 WebClips / 整理某领域知识 → Knowledge Organizer
5. 涉及查找信息 → Knowledge Retriever
6. 涉及修改已有笔记 → Note Editor
7. 涉及创建新笔记 → Note Creator

### Daily Notes Collaborator

负责向每日笔记追加内容，以及日末整理。**追加任务由 Daily Task Manager 负责**。

**每日笔记结构约定**：

Agent 生成的所有内容统一放在 `## 🤖 Assistant Generated` section 下。

**Section 存在性检查（通用规则）**：

追加任何子 section 内容前，必须先 `obsidian vault=MyObsidian daily:read` 检查目标 section 是否已存在：

1. `## 🤖 Assistant Generated` 不存在 → 追加时带 H2 + H3 header + 内容
2. H2 存在但目标 H3 不存在 → 追加时带 H3 header + 内容
3. H3 也存在 → 直接追加内容，不重复 header

**追加内容**：

根据内容性质选择对应的 section：

| 内容类型 | section 标题 | 适用场景 |
|---------|-------------|---------|
| 结构化要点 | `### 📝 Notes` | 会议记录、学习笔记 |
| 想法/感受 | `### 💭 Thoughts` | 自由文本 |
| 网页链接 | `### 🔗 Links` | H4 条目，见 Clipping Save |

```bash
# section 不存在时（带 header）：
obsidian vault=MyObsidian daily:append content="### 📝 Notes\n<内容>"
# section 已存在时（直接追加）：
obsidian vault=MyObsidian daily:append content="<内容>"
```

时间敏感内容加 `HH:MM` 前缀。

**日末整理**：

当用户提到"整理今天"、"今日总结"、"daily review" 时触发：

**分析规划阶段**（只读，不写文件）：

1. `obsidian vault=MyObsidian daily:read` 读取当日全文
2. **内容整理规划**：
   - `## 🤖 Assistant Generated` 内：归并散落的同类 H3 section，顺序固定为 Notes → Thoughts → Links
   - `## 🤖 Assistant Generated` 外的非任务内容：询问用户是否归入对应 section，**不自动移动，由用户确认**
3. **任务整理规划**：
   - `obsidian vault=MyObsidian tasks daily` 展示当日任务清单
   - `obsidian vault=MyObsidian tasks todo path="01_Daily"` 汇总最近未完成任务，按笔记（日期）分组展示
   - 规划历史未完成任务迁移：追加到当日笔记顶部，原任务标记为 `[-]` 并添加 `(已迁移至[[<今日笔记名>]])`

**确认并执行阶段**：

4. **展示重组后的完整内容给用户**，等待确认
5. **用户确认后一次性执行所有写操作**：
   ```bash
   # Step 5a: 获取当日笔记相对路径
   obsidian vault=MyObsidian daily:path
   # Step 5b: 覆写（overwrite flag 防止创建新文件）
   obsidian vault=MyObsidian create path="<上一步路径>" content="<重组后全文>" overwrite silent
   ```

### Daily Task Manager

专注于每日笔记中的任务管理。当用户涉及当日或历史每日笔记的任务查看/更新时触发。

```bash
# 新增任务到当日笔记顶部
obsidian vault=MyObsidian daily:prepend content="- [ ] 任务描述"

# 查看当日任务
obsidian vault=MyObsidian tasks daily
# 汇总近期每日笔记中的未完成任务
obsidian vault=MyObsidian tasks todo path="01_Daily"

# 标记当日任务完成
obsidian vault=MyObsidian task daily line=<行号> done
# 标记历史每日笔记任务完成
obsidian vault=MyObsidian task path="01_Daily/YYYY/MM月/YYYY-MM-DD.md" line=<行号> done
```

**工作流**：

| 场景 | 操作 |
|------|------|
| "今天还有什么没做" | `tasks daily` 展示当日任务 |
| "完成了 XXX" | `tasks daily` 找行号 → `task daily line=N done` |
| "最近有哪些没做完的" | `tasks todo path="01_Daily"` 汇总，按日期分组展示 |
| 迁移历史未完成任务 | 追加到当日笔记顶部，原任务标记为 `[-]` 并添加 `(已迁移至[[<今日笔记名>]])` |

### Clipping Save

将 **search-and-fetch** 已提取分析的网页内容保存到 Obsidian vault，并即时完成知识提炼。

**触发条件**：

| 情况 | 处理 |
|------|------|
| search-and-fetch 完成内容提取/分析后，用户说"保存"、"记录"、"归档"、"clip"、"save" | 直接执行 |
| search-and-fetch 完成后，用户未明确表示保存意图 | 询问："要保存到 Obsidian 吗？" |

**前置依赖**：search-and-fetch 的集成模式输出（标题、摘要、要点、分析、完整正文、实体）。

触发后依次执行：

**Step 1 — 摘要追加到每日笔记**（始终执行）

按 Daily Notes Collaborator 的 section 存在性检查通用规则处理 `### 🔗 Links` section：

```bash
# section 不存在时：
obsidian vault=MyObsidian daily:append content="### 🔗 Links\n<H4 条目>"
# section 已存在时：
obsidian vault=MyObsidian daily:append content="<H4 条目>"
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

**Step 2 — 内容分流**

Agent 基于内容特征判断价值类型，向用户建议处置方式（一句话说明理由），用户确认或调整后执行：

| 内容特征 | 建议处置 | 操作 |
|---------|---------|------|
| 包含持久知识（概念、规则、最佳实践、架构模式等） | **提炼到知识库** | 执行 Step 3 |
| 需要保留原文做参考（教程、长文、数据报告等） | **存档到 WebClips** | 全文保存到 `31_WebClips/<标题>.md` |
| 时效性内容（新闻、公告、价格信息等）或低价值 | **仅保留摘要** | 不额外保存，流程结束 |

例外：用户原始消息中已明确指定处置方式（如"保存全文"、"记到知识库"、"clip"）时，跳过询问直接执行。

**Step 3 — 知识提炼**（仅「提炼到知识库」时执行）

1. 从 search-and-fetch 输出中提取核心知识点（概念、术语、规则、模式）
2. 对每个知识点执行 Knowledge Protocol 的 LEARN 流程（Search → Read → Decide → Execute → Link）
5. 每日笔记的 H4 条目末尾标注 `→ 已提炼至 [[知识笔记名]]`

### Knowledge Organizer

整理 `31_WebClips/` 剪切内容，提炼知识到各领域 `_AgentSpace/`。

**触发词**：整理知识、整理剪切、整理 WebClips、整理收藏

**WebClips 批量整理**：

`31_WebClips/` 为用户与 Agent 共享空间。未整理的剪切留在根目录，整理完成后原文归档到 `31_WebClips/_Archive/`。

1. 列出待整理内容：`obsidian vault=MyObsidian search query="path:31_WebClips -path:_Archive"`
2. 逐条读取，分析内容所属领域（参考 AGENTS.md 目录结构）
3. 对每篇剪切执行：
   - **提炼**：从全文中提取核心概念、术语、规则等知识点
   - **归属**：判断应归入哪个领域的 `_AgentSpace/`，无法明确归类时放入 `19_Misc/_AgentSpace/`
   - **LEARN**：为每个知识点触发 Knowledge Protocol 的 LEARN 操作，创建独立知识笔记
   - **LINK**：触发 LINK 操作，用 `[[wikilinks]]` 与已有知识建立关联
4. 汇总整理计划呈现给用户：每篇剪切 → 提炼了哪些知识点 → 归入哪个领域
5. **用户确认整理计划后执行**（遵循 AGENTS.md 的 _AgentSpace 自主管理权限）：创建知识笔记（确保新笔记中已包含指向原文的 `[[wikilinks]]`），然后用 `obsidian vault=MyObsidian move file="剪切名" to="31_WebClips/_Archive/剪切名.md"` 归档原文（move 自动更新所有已有 wikilinks）

**`_AgentSpace/` 维护策略**：

不设独立审计流程，维护分布在日常操作中：

- **写入时自治**：每次 LEARN/UPDATE 时，检查同领域 `_AgentSpace/` 内是否有重复或可合并的笔记，顺手处理
- **按领域触发**：用户说"整理 XX 领域知识"时，审计该领域的 `_AgentSpace/`（去重、清理过时、优化分类）
- **WebClips 整理附带**：整理 WebClips 写入目标 `_AgentSpace/` 时，自然审视该领域现有内容质量

### Knowledge Retriever

当用户提问或需要查找信息时：

1. 优先搜索 vault（含 `_AgentSpace/` 目录）：`obsidian vault=MyObsidian search query="关键词"`
2. 针对知识库精确搜索（全局结果可能较多，精确搜索确保专业知识不被淹没）：`obsidian vault=MyObsidian search query="关键词 path:_AgentSpace"`
3. 回答时引用已有笔记（如"参见 [[笔记名]]"）
4. 若搜索返回空结果或内容不足：
   - 告知用户"vault 中未找到相关笔记"
   - 委托 **search-and-fetch** skill 进行外部搜索补充回答
   - 可建议将搜索结果保存为新笔记（触发 Note Creator）或追加到每日笔记（触发 Daily Notes Collaborator）

### Note Editor

当用户要求**修改、补充、更新已有普通笔记**（非每日笔记）时：

1. `obsidian vault=MyObsidian read file="笔记名"` 读取当前内容
2. 确认操作类型并执行：
   - **section 级修改/插入** → 走 Section Editing Protocol
   - **末尾追加** → `obsidian vault=MyObsidian append file="笔记名" content="..."`
   - **frontmatter 属性修改** → `obsidian vault=MyObsidian property:set name="字段" value="值" file="笔记名"`
3. 若编辑的是 `_AgentSpace/` 笔记，遵循 Knowledge Protocol 的 UPDATE 操作（更新 `updated` 字段）
4. 操作完成后告知用户具体变更了哪些内容

### Note Creator

当用户要求**记录、总结、整理信息**为新笔记时：

1. 根据 AGENTS.md 的目录语义判断笔记应放在哪个目录
2. 遵循 frontmatter 规范，额外添加 `source: ai-generated` 字段
3. 使用 `[[wikilinks]]` 链接 vault 中已有的相关笔记
4. 若目标为 `_AgentSpace/` 目录，额外添加 `managed-by: agent` 到 frontmatter
5. 不确定目录时，放入 `00_Inbox/` 并告知用户

## Skill Delegation

### 委托时机

| 需求 | 处理方式 |
|------|---------|
| 普通笔记增删改查 | 直接使用 obsidian CLI，无需委托 |
| 网页搜索与内容提取分析 | 委托 **search-and-fetch** skill |
| 创建格式复杂的结构化文档（含模板、特定规范） | 委托 **obsidian-markdown** skill |
| 创建 .base 数据库视图 | 委托 **obsidian-bases** skill |
| 创建 .canvas 可视化画布 | 委托 **json-canvas** skill |
| 写技术文档、方案等结构化内容 | 委托 **doc-coauthoring** skill |
| 写内部沟通（3P updates、状态报告等） | 委托 **internal-comms** skill |

上述 vault skills 的路径：`$(obsidian vault=MyObsidian info=path)/.agents/skills/`。

### 技能优先级说明

`obsidian-knowledge`（本文件）是**主规范**，定义所有角色、工作流和决策逻辑。CLI 命令细节查阅本 skill 的 `references/obsidian-cli.md`。

## Privacy Boundaries

这些是硬性边界，不可违反：

- **不读取/修改**带 `#Private` 或 `#Key` 标签的笔记
- **不操作** `30_Permanent/MyConfig/` 中的敏感配置
- **不操作** `99_Plugconfig/` 中的插件配置
- 遇到上述内容时，告知用户你无法访问并说明原因
