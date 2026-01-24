# Python Script Standards

This document provides standards for creating Python scripts with PEP 723 metadata.

## PEP 723 – Inline Script Metadata

All Python scripts MUST include a PEP 723 metadata block after the shebang:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests>=2.31.0",
# ]
# ///

"""One-line description. Longer description if needed.

Usage:
    uv run script_name.py --help
"""
```

**Key Rules:**

1. Metadata must appear before any code
2. Use `# /// script` and `# ///` delimiters (TOML format inside)
3. List ALL external dependencies with version constraints (`>=` minimum version)
4. Specify Python version (default: `>=3.12`)

**Common Dependencies:**

```toml
"requests>=2.31.0",      # HTTP requests
"pandas>=3.0.0",         # Data manipulation
"rich>=13.0.0",          # CLI formatting
```

## Execution

Run scripts using `uv run`:

```bash
uv run script.py
```

`uv` automatically reads PEP 723 metadata, installs dependencies, and runs the script.

**Install uv** (if needed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Documentation Standards

**Module Docstring:**

```python
"""Brief description explaining what the script does.

Usage:
    uv run script_name.py --input value
    uv run script_name.py --help
"""
```

**Function Docstring:**

```python
def process_data(data: list, threshold: float) -> dict | None:
    """Process input data and return filtered results.

    Args:
        data: Input data list
        threshold: Minimum threshold value

    Returns:
        Processed result dict, or None on error
    """
```

**Rules:** One-line for simple functions, multi-line (summary + Args + Returns) for complex ones. Focus on **what** not **how**.

## Error Handling

**Rules:**

1. Catch specific exceptions when possible
2. Print user-friendly messages to stderr
3. Return `None` on error, valid value on success
4. For validation: return `(bool, str)` tuple
5. Allow exceptions to propagate for unrecoverable errors

**Example:**

```python
import sys
import requests
import json

def fetch_data(url: str) -> dict | None:
    """Fetch data from API.

    Returns:
        JSON response or None on error.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error: Failed to fetch data: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON response: {e}", file=sys.stderr)
        return None
```

## Output Formatting

Use consistent indicators:

- `✓` - Success (file saved, processing completed)
- `✗` - Error (with context)

```python
# Basic
print(f"✓ Saved: {path} ({size:.1f} KB)")
print(f"✗ Error: {message}", file=sys.stderr)

# With color (optional, using colorama)
from colorama import Fore, Style
print(f"{Fore.GREEN}✓{Style.RESET_ALL} Success")
```

## Input/Output Standards

### Input

**Command-line Arguments:**

```python
parser.add_argument("--symbol", required=True, help="Stock symbol (e.g., 700.HK)")
parser.add_argument("--period", default="day", help="Period (default: day)")
parser.add_argument("--output", help="Output file path")
```

**Rules:** Required args for critical inputs, optional with defaults for config, validate early.

### Output

**Recommended Directory Structure:**

```
project/
├── scripts/           # Executable scripts
│   └── script.py
├── data/              # Input data files
│   └── sample.csv
└── results/           # Output results
    └── output.csv
```

**Flexible Path Handling:**

```python
from pathlib import Path

# Option 1: Command-line argument
parser.add_argument("--output", help="Output file path")

# Option 2: Relative to script directory
SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "results"
OUTPUT_DIR.mkdir(exist_ok=True)

# Option 3: Current working directory
OUTPUT_DIR = Path.cwd() / "results"
```

**Data Format:**

- CSV: UTF-8, headers, ISO 8601 dates, 2-4 decimals
- JSON: snake_case keys, ISO 8601 dates, with metadata
- Console: aligned columns, include units

## Quick Checklist

### Required

- [ ] PEP 723 metadata block present
- [ ] All dependencies listed with versions
- [ ] Module docstring with usage example
- [ ] Error handling with user-friendly messages
- [ ] `--help` argument implemented

### Recommended

- [ ] Function docstrings for complex functions
- [ ] Type hints for parameters and returns
- [ ] Consistent output format (`✓`/`✗`)
- [ ] Exit codes (0=success, 1=error)
- [ ] Dry-run mode when applicable
