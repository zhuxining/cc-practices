# Fetch 策略参考

本文件说明针对不同类型信息源的具体 fetch 方式，在 SKILL.md 的 Step 2 执行时参考。

---

## 搜索类（topics 配置）

### 基础搜索

调用 search-and-fetch 的 Search Mode，构造查询时：

```
# 单一域名限定
query = "{search_query} site:{website}"

# 多个域名时并行多次调用，而非 site:a OR site:b（后者效果差）
query1 = "AI news today site:techcrunch.com"
query2 = "AI news today site:theverge.com"
```

### 中英文并行

对中文话题（如 AI、科技、财经），同时用中英文查询：

- 英文查询 → 走 WebSearch（DuckDuckGo）
- 中文查询 → 走 MCP 搜索（如 bailian_web_search 等可用工具）

两者并行，结果合并去重。

### 时效性过滤

在查询中加入时间限定提高新鲜度：

- 英文：追加 "today" 或 "this week"
- 中文：追加 "今天" 或 "最新"
- 如果 WebSearch 支持时间过滤参数，优先使用

---

## 直接 URL 类（direct_sources 配置）

### 普通网页（type: page）

使用 defuddle 优先，crwl 降级：

```bash
# 首选
defuddle parse <url> --md

# 降级（JS 渲染页面）
crwl crawl <url> -o md-fit
```

对于列表类页面（Hacker News、GitHub Issues 等），提取首页列表即可，不需要深入每条链接。

**GitHub Issues 页面**：直接用 `https://github.com/{owner}/{repo}/issues`（HTML 页面），不要用 `.atom` 端点（返回 406）。defuddle 可干净提取 issue 列表，包含标题、标签、时间、提交者。

### RSS / Atom Feed（type: rss）

RSS XML 通常不含 JS，直接用 crwl 获取：

```bash
crwl crawl <rss_url> -o md-fit
```

解析结果时：

- 提取最新 10 条条目（`<item>` 或 `<entry>` 元素）
- 每条取：`<title>`、`<link>`、`<pubDate>`、`<description>` 或 `<summary>`
- 仅展示 24 小时内的条目（如能判断时间）

---

## 两级 fetch 策略

### Level 1 — 列表页

目标：提取条目列表（标题、URL、简短描述），最多 10 条。

```bash
defuddle parse <list_url> --md   # 首选，干净提取列表结构
crwl crawl <list_url> -o md-fit  # 降级
```

从结果中只保留：

- 每条的标题（`h2`/`h3` 或链接文本）
- 每条的 URL（绝对路径，补全相对路径）
- 每条的一句话描述（副标题、标签、时间等）

**不要**在 Level 1 阶段深入每条链接——先把列表拿到再决定深度。

### Level 2 — 详情页（按需或自动）

**按需深读（用户指定）**：

- 对用户指定的 URL 调用 Fetch Mode，独立模式（完整五维分析）
- 单次一篇，结果直接展示

**自动深读（批量）**：

- 从列表中取前 N 条 URL（默认 N=3），并行抓取详情
- 调用 Fetch Mode，集成模式（标题 + 摘要 + 要点，**跳过**五维分析）
- 所有详情并行发出，不等待单个完成

```
# 自动深读示例（N=3，3个并行）
并行：fetch(url_1, 集成模式)
并行：fetch(url_2, 集成模式)
并行：fetch(url_3, 集成模式)
```

N=3 是平衡速度和信息量的默认值；用户明确要求更多时可提高，但超过 5 时提醒用户响应会较慢。

---

## 并行限制

单轮最多并行 4 个 fetch 动作，超出时分轮执行：

```
# 每日简报（3 个话题 + 2 个直接源）→ 拆为两轮
第一轮：话题 ai + crypto + tech（3 个并行搜索）
第二轮：direct_sources（2 个并行 fetch）
```

自动深读的详情抓取独立计数（Level 2 的并行与 Level 1 分开）。

---

## 降级处理

| 情况 | 处理 |
|------|------|
| defuddle 失败 | 降级到 crwl |
| crwl 失败 | 降级到 agent-browser |
| 搜索返回 0 结果 | 放宽时间限定（去掉 today），重试一次 |
| 某个话题完全失败 | 在输出中标注"获取失败"，继续其他话题 |

不要因为一个源失败就中断整个简报流程。
