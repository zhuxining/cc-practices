# Specification

> The complete format specification for Agent Skills.

This document defines the Agent Skills format.

## Directory structure

A skill is a directory containing at minimum a `SKILL.md` file:

```
skill-name/
└── SKILL.md          # Required
```

<Tip>
  You can optionally include [additional directories](#optional-directories) such as `scripts/`, `references/`, and `assets/` to support your skill.
</Tip>

## SKILL.md format

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content.

### Frontmatter (required)

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

With optional fields:

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---
```

| Field           | Required | Constraints                                                                                                       |
| --------------- | -------- | ----------------------------------------------------------------------------------------------------------------- |
| `name`          | Yes      | Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen.             |
| `description`   | Yes      | Max 1024 characters. Non-empty. Describes what the skill does and when to use it.                                 |
| `license`       | No       | License name or reference to a bundled license file.                                                              |
| `compatibility` | No       | Max 500 characters. Indicates environment requirements (intended product, system packages, network access, etc.). |
| `metadata`      | No       | Arbitrary key-value mapping for additional metadata.                                                              |
| `allowed-tools` | No       | Space-delimited list of pre-approved tools the skill may use. (Experimental)                                      |

### Body content

The Markdown body after the frontmatter contains the skill instructions. There are no format restrictions. Write whatever helps agents perform the task effectively.

Recommended sections:

* Step-by-step instructions
* Examples of inputs and outputs
* Common edge cases

Note that the agent will load this entire file once it's decided to activate a skill. Consider splitting longer `SKILL.md` content into referenced files.

## Optional directories

### scripts/

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

* Be self-contained or clearly document dependencies
* Include helpful error messages
* Handle edge cases gracefully
* **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
* **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
* **Benefits**: Token efficient, deterministic, may be executed without loading into context
* **Note**: Scripts may still need to be read by Claude for patching or environment-specific adjustments

### references/

Documentation and reference material intended to be loaded as needed into context to inform Claude's process and thinking.

* **When to include**: For documentation that Claude should reference while working
* **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
* **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
* **Benefits**: Keeps SKILL.md lean, loaded only when Claude determines it's needed
* **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
* **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.

Keep individual [reference files](#file-references) focused. Agents load these on demand, so smaller files mean less use of context.

### assets/

Files not intended to be loaded into context, but rather used within the output Claude produces.

* **When to include**: When the skill needs files that will be used in the final output
* **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
* **Benefits**: Separates output resources from documentation, enables Claude to use files without loading them into context

Contains static resources:

* Templates (document templates, configuration templates)
* Images (diagrams, examples)
* Data files (lookup tables, schemas)

## Progressive disclosure

Skills should be structured for efficient use of context:

1. **Metadata** (\~100 tokens): The `name` and `description` fields are loaded at startup for all skills
2. **Instructions** (\< 5000 tokens recommended): The full `SKILL.md` body is loaded when the skill is activated
3. **Resources** (as needed): Files (e.g. those in `scripts/`, `references/`, or `assets/`) are loaded only when required

Keep your main `SKILL.md` under 500 lines. Move detailed reference material to separate files.

## File references

When referencing other files in your skill, use relative paths from the skill root:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains.
