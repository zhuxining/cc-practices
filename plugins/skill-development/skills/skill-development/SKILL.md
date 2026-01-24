---
name: skill-development
description: Knowledge base for creating effective Claude Code Skills. This skill should be used when creating a new skill, designing skill structure, writing skill instructions, creating skill scripts, or troubleshooting skill issues.
---


## What are Skills?

> Agent Skills are a lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows.

At its core, a skill is a folder containing a `SKILL.md` file with metadata and instructions. Skills can also bundle scripts, templates, and reference materials.

```directory
my-skill/
├── SKILL.md          # Required: instructions + metadata
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
└── assets/           # Optional: templates, resources
```

## How Skills Work

Skills use **progressive disclosure** to manage context efficiently:

1. **Discovery**: At startup, agents load only the name and description
2. **Activation**: When a task matches, the full `SKILL.md` is loaded
3. **Execution**: References and scripts are loaded as needed

## Core Reference (Required)

### Skill Specification ([references/skill-specification.md](references/skill-specification.md))

Core format specification for Agent Skills. **All skills must follow this specification.**

**Topics covered**:

- Directory structure (minimum vs optional)
- SKILL.md frontmatter (required vs optional fields)
- Progressive disclosure strategy
- Optional directories usage (`scripts/`, `references/`, `assets/`)

**Field constraints**:

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | Max 64 chars, lowercase/numbers/hyphens |
| `description` | Yes | Max 1024 chars |

---

## Script References

**When skill includes executable scripts**, follow the relevant standards:

### Python Scripts ([references/scripts-standards/python.md](references/scripts-standards/python.md))

PEP 723 metadata, docstrings, error handling, I/O standards.

### Bash Scripts ([references/scripts-standards/bash.md](references/scripts-standards/bash.md))

Script header, error handling, documentation, I/O standards.

---

## Optional References

### Workflow Patterns ([references/workflows.md](references/workflows.md))

**When skill uses workflow** - Multi-step procedures with sequential or conditional logic.

**Topics covered**:

- Sequential Workflows - Break complex tasks into clear steps
- Conditional Workflows - Guide through decision points with branching logic

### Output Patterns ([references/output-patterns.md](references/output-patterns.md))

**When skill requires formatted output** - Generating consistent, structured output with templates or examples.

**Topics covered**:

- Template Pattern - Strict vs flexible guidance
- Examples Pattern - Input/output pairs for style alignment
