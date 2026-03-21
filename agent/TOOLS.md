# TOOLS.md - Tool Usage Notes

Tool signatures are provided automatically via function calling.
This file documents non-obvious constraints and usage patterns.
**After the message response is completed, output a tool usage record in the order of invocation to user (if used)**

## exec — Safety Limits

- Commands have a configurable timeout (default 60s)
- Dangerous commands are blocked (rm -rf, format, dd, shutdown, etc.)
- Output is truncated at 10,000 characters
- `restrictToWorkspace` config can limit file access to the workspace

## cron — Scheduled Reminders

- Please refer to cron skill for usage.

## 工具安装规则

**安装任何工具或包之前，必须先征得用户确认，然后再执行安装命令。**

允许的安装方式（仅限以下三种）：

- `brew install <package>` — 系统级工具
- `uv tool install <package>` — Python 工具
- `bun -g install <package>` — JavaScript/Node.js 工具

---
