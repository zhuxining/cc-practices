# 工具调用手册

搜索与提取工具的调用语法和参数速查。

---

## 搜索工具

### WebSearch（内置 DuckDuckGo）

```
WebSearch(query="搜索关键词")
```

- 返回搜索结果摘要
- 英文查询效果更好，中文查询可考虑同时使用 MCP 搜索工具

### MCP 搜索工具

使用当前环境中可用的 MCP 搜索工具。不要硬编码具体工具名——检查可用工具列表，选择合适的搜索 MCP 调用。

- 优先选用针对查询语言/地域优化的 MCP 搜索（如中文搜索 MCP 处理中文查询）
- 若有多个 MCP 搜索可用，可并行调用以扩大覆盖面
- 调用方式遵循 MCP 标准：`mcp__<server>__<tool>(参数)`

### Context7（技术文档搜索）

**两步调用，有顺序依赖：**

```bash
# Step 1: 解析库 ID
ctx7 library <name> <query>

# Step 2: 查询文档（使用 Step 1 返回的 libraryId）
ctx7 docs <libraryId> <query>
```

- 专用于编程库/框架的官方文档查询
- 始终先 `library` 解析再 `docs` 查询
- **每个问题最多调用 3 次**，3 次未找到则使用已有最佳结果

### agent-browser（浏览器搜索）

Rust 原生 CLI，使用 snapshot-ref 模式交互，token 开销极低。用于深度研究时访问搜索引擎：

```bash
# 打开搜索引擎
agent-browser open "https://www.google.com/search?q=搜索词"

# 获取可交互元素的无障碍树（返回 @e1, @e2 等引用）
agent-browser snapshot

# 点击某个搜索结果（使用 snapshot 返回的引用）
agent-browser click @e5

# 提取页面文本
agent-browser get text

# 完成后关闭
agent-browser close
```

- 仅在深度研究模式下使用
- 可以访问任何搜索引擎（Google、Bing、百度等）
- 通过 `snapshot` 获取元素引用后精确交互，避免脆弱的 CSS 选择器
- 也支持语义定位：`agent-browser find text "搜索结果" click`

---

## 提取工具

### crwl（首选）

```bash
# 提取适合阅读的精简 markdown（推荐）
crwl <url> -o md-fit

# 提取完整 markdown
crwl <url> -o md

# 跳过缓存重新爬取
crwl <url> -o md-fit -bc
```

- 支持 JavaScript 渲染，能处理动态页面
- `md-fit` 输出格式去除冗余内容，适合阅读
- 比 agent-browser 开销低
- 未安装时：`pip install crawl4ai` 后 `crwl` 即可使用

### agent-browser（最终手段）

用于 crwl 无法处理的场景（需要登录态、复杂交互、反爬严格的页面）：

```bash
# 打开页面
agent-browser open <url>

# 获取页面无障碍树快照（确认加载完成 + 获取元素引用）
agent-browser snapshot

# 提取全页文本
agent-browser get text

# 或提取特定区域的文本
agent-browser get text "article"
agent-browser get text "main"

# 提取特定区域 HTML
agent-browser get html "article"

# 完成后关闭
agent-browser close
```

- 支持页面交互（点击、滚动、等待加载），能应对反爬和动态加载
- 输出精简，节省 token
- 仅在 crwl 失败时使用
- 未安装时：`npm install -g agent-browser && agent-browser install`
