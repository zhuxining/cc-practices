# Bash Script Standards

This document provides standards for creating Bash scripts.

## Script Header

All Bash scripts MUST include a header with shebang and metadata:

```bash
#!/usr/bin/env bash
#
# Name: script_name.sh
# Description: Brief description of what the script does.
#
# Usage:
#   ./script_name.sh [options]
#
# Options:
#   -h, --help     Show this help message
#   -v, --verbose  Enable verbose output
#
# Example:
#   ./script_name.sh --input data.txt --output result.txt
#
# Requires: bash 5.0+, coreutils
#

set -euo pipefail
```

**Key Rules:**

1. Use `#!/usr/bin/env bash` for portability
2. Include script name, description, and usage
3. List all options with descriptions
4. Include an example usage
5. Specify minimum bash version (default: 5.0+)
6. Always use `set -euo pipefail` for strict error handling

## Execution

Run scripts directly or with `bash`:

```bash
# Make executable and run directly
chmod +x script.sh
./script.sh

# Or run with bash
bash script.sh
```

## Documentation Standards

**Script Header:**

```bash
#
# Description: Process input files and generate summary report.
#
# Usage:
#   ./process.sh [directory]
#
# Arguments:
#   directory    Path to directory containing input files (default: current directory)
#
# Example:
#   ./process.sh /path/to/data
#
```

**Function Documentation:**

```bash
# Process a single input file and append results to output
# Arguments:
#   $1 - Input file path
#   $2 - Output file path
# Returns:
#   0 on success, 1 on error
process_file() {
    local input_file="$1"
    local output_file="$2"

    if [[ ! -f "$input_file" ]]; then
        echo "✗ Error: File not found: $input_file" >&2
        return 1
    fi

    # Processing logic here
    echo "Processing: $input_file" >> "$output_file"
}
```

## Error Handling

**Use `set -euo pipefail`:**

```bash
set -euo pipefail
# -e: Exit on error
# -u: Exit on undefined variable
# -o pipefail: Exit on pipe failure
```

**Error Handling Patterns:**

```bash
# Trap errors for cleanup
trap 'echo "✗ Error: Script failed at line $LINENO"; exit 1' ERR

# Check required commands
check_dependencies() {
    local deps=("curl" "jq" "grep")
    for cmd in "${deps[@]}"; do
        if ! command -v "$cmd" &>/dev/null; then
            echo "✗ Error: Required command not found: $cmd" >&2
            exit 1
        fi
    done
}

# Validate arguments
if [[ $# -lt 1 ]]; then
    echo "✗ Error: Missing required argument" >&2
    echo "Usage: $0 <input_file>" >&2
    exit 1
fi
```

## Output Formatting

Use consistent indicators:

- `✓` - Success (file saved, processing completed)
- `✗` - Error (with context)

```bash
# Basic
echo "✓ Saved: $output_path (${file_size} bytes)"
echo "✗ Error: $message" >&2

# With color (optional)
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly NC='\033[0m' # No Color

echo -e "${GREEN}✓${NC} Success"
echo -e "${RED}✗${NC} Error occurred" >&2
```

## Input/Output Standards

### Input

**Positional Arguments:**

```bash
#!/usr/bin/env bash

INPUT_FILE="${1:-}"
OUTPUT_DIR="${2:-./output}"

if [[ -z "$INPUT_FILE" ]]; then
    echo "✗ Error: Input file is required" >&2
    exit 1
fi
```

**Flag-based Arguments (getopts):**

```bash
VERBOSE=false
OUTPUT_FILE=""
DRY_RUN=false

while getopts "hvno:" opt; do
    case $opt in
        h) show_help; exit 0 ;;
        v) VERBOSE=true ;;
        n) DRY_RUN=true ;;
        o) OUTPUT_FILE="$OPTARG" ;;
        *) echo "✗ Error: Invalid option" >&2; exit 1 ;;
    esac
done

shift $((OPTIND-1))
```

**Long Options (using bash built-in):**

```bash
INPUT_FILE=""
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            INPUT_FILE="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "✗ Error: Unknown option: $1" >&2
            exit 1
            ;;
    esac
done
```

### Output

**Recommended Directory Structure:**

```
project/
├── scripts/           # Executable scripts
│   └── script.sh
├── data/              # Input data files
│   └── sample.txt
└── results/           # Output results
    └── output.txt
```

**Path Handling:**

```bash
# Get script directory
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Define output directory
OUTPUT_DIR="${OUTPUT_DIR:-$SCRIPT_DIR/results}"
mkdir -p "$OUTPUT_DIR"

# Output file path
OUTPUT_FILE="$OUTPUT_DIR/output.txt"
```

**Data Format:**

- Text files: UTF-8 encoding, Unix line endings
- CSV: Comma-separated, headers in first row
- JSON: Use `jq` for formatting
- Console: Aligned columns, include units

```bash
# CSV output
echo "timestamp,value,status" > "$OUTPUT_FILE"
echo "$(date +%Y-%m-%d),$value,$status" >> "$OUTPUT_FILE"

# JSON output (with jq)
jq -n \
    --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg value "$value" \
    --arg status "$status" \
    '{timestamp: $timestamp, value: ($value | tonumber), status: $status}' > "$OUTPUT_FILE"
```

## Best Practices

1. **Use `readonly` for constants**

   ```bash
   readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   readonly MAX_RETRIES=3
   ```

2. **Use `local` for function variables**

   ```bash
   process_item() {
       local item="$1"
       local result
       result=$(process "$item")
       echo "$result"
   }
   ```

3. **Quote variables to prevent word splitting**

   ```bash
   # Good
   "$file"
   "${array[@]}"

   # Bad (unquoted)
   $file
   ${array[@]}
   ```

4. **Use `[[` for tests instead of `[`**

   ```bash
   # Good
   if [[ -f "$file" ]]; then
       # ...
   fi

   # Avoid
   if [ -f "$file" ]; then
       # ...
   fi
   ```

5. **Avoid backticks, use `$()` for command substitution**

   ```bash
   # Good
   result=$(command)

   # Avoid
   result=`command`
   ```

## Performance Considerations

- **Small files**: Native bash, built-in commands
- **Large files**: Use `awk`, `sed`, or specialized tools
- **Parallel processing**: Use `xargs -P` or GNU `parallel`
- **Network operations**: Use timeout and retries

## Quick Checklist

### Required

- [ ] Shebang with `#!/usr/bin/env bash`
- [ ] Script header with name, description, usage
- [ ] `set -euo pipefail` for error handling
- [ ] Help message (`-h, --help`)
- [ ] Error messages to stderr (`>&2`)

### Recommended

- [ ] Function documentation comments
- [ ] `readonly` for constants
- [ ] `local` for function variables
- [ ] Consistent output format (`✓`/`✗`)
- [ ] Exit codes (0=success, 1=error)
- [ ] Dependency checks
- [ ] Dry-run mode when applicable
