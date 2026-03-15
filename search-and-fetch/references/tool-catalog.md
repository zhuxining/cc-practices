# 工具调用手册

搜索与提取工具的调用语法和参数速查。

---

## 搜索工具

### WebSearch（内置 DuckDuckGo）

```
WebSearch(query="搜索关键词")
```

- 返回搜索结果摘要
- 英文查询效果更好，中文查询可考虑同时使用 bailian

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

### browser-use（浏览器搜索）

用于深度研究时访问 Google/Bing 等搜索引擎：

```bash
# 打开搜索引擎
browser-use open "https://www.google.com/search?q=搜索词"

# 获取搜索结果页面状态
browser-use state

# 提取搜索结果文本
browser-use get text <index>

# 点击进入某个结果
browser-use click <index>

# 完成后关闭
browser-use close
```

- 仅在深度研究模式下使用
- 可以访问任何搜索引擎（Google、Bing、百度等）
- 能处理需要 JavaScript 渲染的搜索结果页

---

## 提取工具

### defuddle（首选）

```bash
# 提取干净 markdown 正文
defuddle parse <url> --md

# 保存到文件
defuddle parse <url> --md -o content.md

# 提取元数据
defuddle parse <url> -p title
defuddle parse <url> -p description
defuddle parse <url> -p domain
```

- 去除广告、导航、侧边栏等噪音
- 节省 token 开销
- 标准网页的首选提取方式
- 未安装时：`npm install -g defuddle-cli`

### WebFetch（内置降级）

```
WebFetch(url="https://example.com", prompt="Extract the article content")
```

- 内置工具，始终可用
- 可通过 prompt 参数引导提取重点

### MCP fetch 工具（降级选项）

使用当前环境中可用的 MCP fetch 工具。检查可用工具列表中是否有 fetch 类 MCP。

- 作为 WebFetch 之后的额外降级选项
- 调用方式遵循 MCP 标准：`mcp__<server>__<tool>(url=...)`

### browser-use（最终手段）

用于 JS 重度页面（SPA、动态渲染）：

```bash
# 打开页面
browser-use open <url>

# 等待页面加载
browser-use wait text "关键文本"

# 提取全页文本
browser-use eval "document.body.innerText"

# 或提取特定区域
browser-use get html --selector "article"
browser-use get html --selector "main"

# 完成后关闭
browser-use close
```

- 能处理需要 JavaScript 渲染的页面
- 开销最大，仅在其他工具都失败时使用
