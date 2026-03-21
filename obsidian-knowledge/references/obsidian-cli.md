---
name: obsidian-cli
description: Interact with Obsidian vaults using the Obsidian CLI to read, create, search, and manage notes, tasks, properties, and more. Use when the user asks to interact with their Obsidian vault, manage notes, search vault content, perform vault operations from the command line.
---

# Obsidian CLI

Use the `obsidian` CLI to interact with a running Obsidian instance. Requires Obsidian to be open.

**IMPORTANT**:before running `obsidian create`, read `obsidian vault="MyObsidian" read file="AGENTS"` and follow the rules in it.

## Command reference

Run `obsidian help` to see all available commands. This is always up to date. Full docs: <https://help.obsidian.md/cli>

## Syntax

**Parameters** take a value with `=`. Quote values with spaces:

```bash
obsidian create name="My Note" content="Hello world"
```

**Flags** are boolean switches with no value:

```bash
obsidian create name="My Note" silent overwrite
```

For multiline content use `\n` for newline and `\t` for tab.

## File targeting

Many commands accept `file` or `path` to target a file. Without either, the active file is used.

- `file=<name>` — resolves like a wikilink (name only, no path or extension needed)
- `path=<path>` — exact path from vault root, e.g. `folder/note.md`

## Vault targeting

Commands target the most recently focused vault by default. Use `vault=<name>` as the first parameter to target a specific vault:

```bash
obsidian vault="My Vault" search query="test"
```

## Browsing vault structure

```bash
# List files in a folder
obsidian vault=MyObsidian files folder="31_WebClips"

# List files with extension filter
obsidian vault=MyObsidian files folder="20_Projects" ext=canvas

# Count files in a folder
obsidian vault=MyObsidian files folder="01_Daily" total

# List subfolders
obsidian vault=MyObsidian folders folder="10_Area"
```

## Search commands

Two search commands with different return types:

- **`search`** — returns matching **file paths** only (like `find`)
- **`search:context`** — returns **content with line numbers** in `path:line: text` format (like `grep`)

Use `search` to locate files, then `read` to view content. Use `search:context` when you need to find specific text across files.

```bash
# search: returns file paths
obsidian vault=MyObsidian search query="关键词"
obsidian vault=MyObsidian search query="关键词" limit=10

# search:context: returns matching lines with context
obsidian vault=MyObsidian search:context query="关键词"
```

### Search operators

`search query=` supports Obsidian search syntax. Available operators:

- `path:folder` — restrict to path
- `-path:folder` — exclude path
- `file:name` — restrict to filename
- `tag:#tag` — search by tag
- `/regex/` — regular expression matching

Operators can be combined:

```bash
# Full-text search
obsidian vault=MyObsidian search query="关键词"

# Search within a specific path
obsidian vault=MyObsidian search query="关键词 path:_AgentSpace"

# Exclude a subdirectory
obsidian vault=MyObsidian search query="path:31_WebClips -path:_Archive"

# Search by tag
obsidian vault=MyObsidian search query="tag:#Clippings"

# Regex match on file paths
obsidian vault=MyObsidian search query="path:/\d{4}-\d{2}-\d{2}/"
```

## File info and outline

```bash
# Show file metadata (path, size, created, modified)
obsidian vault=MyObsidian file file="My Note"

# Show heading outline of a file
obsidian vault=MyObsidian outline file="My Note"
```

## Moving and renaming files

```bash
# Move a file (auto-updates all wikilinks referencing it)
obsidian vault=MyObsidian move file="My Note" to="Archive/My Note.md"
```

## Common patterns

```bash
obsidian read file="My Note"
obsidian create name="New Note" content="# Hello" template="Template" silent
obsidian append file="My Note" content="New line"
obsidian search query="search term" limit=10
obsidian daily:read
obsidian daily:append content="- [ ] New task"
obsidian property:set name="status" value="done" file="My Note"
obsidian tasks daily todo
obsidian tags sort=count counts
obsidian backlinks file="My Note"
```

Use `--copy` on any command to copy output to clipboard. Use `silent` to prevent files from opening. Use `total` on list commands to get a count.

Run `obsidian help` to see additional developer commands including CDP and debugger controls.
