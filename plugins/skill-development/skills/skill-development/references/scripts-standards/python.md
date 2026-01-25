# Python Script Standards

Python 脚本开发规范（基于 PEP 723）

---

## PEP 723 元数据

所有脚本必须包含 PEP 723 元数据块：

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests>=2.31.0",
# ]
# ///

"""脚本功能描述.

Usage:
    uv run script.py --help
"""
```

**关键规则**：

1. 元数据必须位于代码之前
2. 使用 `# /// script` 和 `# ///` 分隔符（内嵌 TOML 格式）
3. 列出所有外部依赖及版本约束 (`>=` 最低版本)
4. 指定 Python 版本（默认 `>=3.12`）

---

## 执行与格式化

**执行**：所有示例必须使用 `uv run` 前缀

```bash
uv run script.py
uv run script.py --help
```

**格式化**：开发完成后必须用 `ruff` 检查

```bash
uvx ruff check script.py
uvx ruff check . --fix
```

---

## 文档规范

```python
"""模块功能简要描述.

Usage:
    uv run module.py --help
"""

def process_data(data: list, threshold: float) -> dict | None:
    """处理输入数据并返回过滤结果.

    Args:
        data: 输入数据列表
        threshold: 最小阈值

    Returns:
        处理结果字典，错误时返回 None
    """
```

**规则**：简单函数用单行，复杂函数用多行（summary + Args + Returns），关注"做什么"而非"怎么做"。

---

## 错误处理

**规则**：

1. 尽可能捕获特定异常
2. 向 stderr 打印用户友好的错误消息
3. 验证时返回 `(bool, str)` 元组
4. 允许不可恢复错误向上传播
5. **重新抛出时保留异常链** - 使用 `raise ... from e`

**异常链最佳实践**：

```python
# ❌ 错误 - 丢失原始异常上下文
try:
    data = fetch_from_api()
except Exception as e:
    raise RuntimeError(f"Failed to fetch data: {e}")

# ✓ 正确 - 保留异常链便于调试
try:
    data = fetch_from_api()
except Exception as e:
    raise RuntimeError(f"Failed to fetch data: {e}") from e
```

---

## 导入规范

**规则**：始终使用**绝对导入**（完整模块路径），禁止相对导入

```python
# ❌ 错误
from .utils import helper
from ..config import settings

# ✓ 正确
from core.utils import helper
from core.config import settings
```

**原因**：清晰明确模块来源，避免重构混淆，更好的 IDE/工具支持。

---

## 输入输出

**命令行参数**：

```python
parser.add_argument("--symbol", required=True, help="股票代码")
parser.add_argument("--period", default="day", help="周期（默认：day）")
parser.add_argument("--output", help="输出文件路径")
```

**输出格式**：

```python
# 基础
print(f"✓ Saved: {path} ({size:.1f} KB)")
print(f"✗ Error: {message}", file=sys.stderr)

# 数据格式
# CSV: UTF-8, 带表头, ISO 8601 日期, 2-4 位小数
# JSON: snake_case 键名, ISO 8601 日期, 包含元数据
# 控制台: 列对齐, 包含单位
```

---

## 快速检查清单

### 必需项

- [ ] PEP 723 元数据块存在
- [ ] 所有依赖列出版本约束
- [ ] 模块文档字符串包含使用示例
- [ ] **所有执行示例使用 `uv run`**
- [ ] 错误处理包含友好消息
- [ ] 异常链已保留 (`raise ... from e`)
- [ ] `--help` 参数已实现

### 完成前检查

- [ ] **运行 `uvx ruff check .` 验证无问题**
- [ ] 测试 `uv run script.py --help`

### 推荐项

- [ ] 复杂函数添加文档字符串
- [ ] 参数和返回值使用类型提示
- [ ] 仅使用绝对导入（禁用相对导入）
- [ ] 一致的输出格式 (`✓`/`✗`)
- [ ] 退出码 (0=成功, 1=错误)
- [ ] 适用时添加 dry-run 模式
