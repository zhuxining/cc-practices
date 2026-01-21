# AGENTS.md

This file provides guidance to AI coding agents (Claude Code, OpenCode, Copilot, etc.) when working with code in this repository.

## Overview

This project is Claude Code practices notes. It includes various guidelines, conventions, and best practices for different programming languages and frameworks.

## Structure

```
your-project/
├── .claude/
│   ├── CLAUDE.md                     # Universal agent rules/memory（Respond Language、Important Note）
│   ├── rules/                        # Domain agent rules/memory
│   │   ├── code-style.md             # Code style guidelines
│   │   ├── testing.md                # Testing conventions
│   │   └── security.md               # Security requirements
│   └── skills/                       # Progressive loading(workflow、guidelines、conventions、requirements) 
│       ├── coding-standards
│       ├── web-design-guidelines
│       ├── API-design-conventions
│       ├── react-best-practices
│       ├── python-best-practices
│       ├── sqlmodelORM-conventions
│       ├── drizzleORM-conventions
│       ├── tdd-workflow
│       └── git-commit-conventions
├── src/
│   ├── auth/
│   │    └── CLAUDE.md                  # Module agent rules/memory
│   ├── api/
│   │    └── CLAUDE.md                  # Module agent rules/memory
│   └── db/
│       └── CLAUDE.md                   # Module agent rules/memory   
└── CLAUDE.md                           # Architecture agent rules/memory (project structure, run, workflow)
```

**Important Note**: 

- `CLAUDE.md` and `rules/` automatically loaded into context when launched.
- `skills/` can be progressively loaded based on task requirements.

## Local Key References

| Task            | Location                      | Notes                                   |
| --------------- | ----------------------------- | --------------------------------------- |
| Web routing     | apps/web/src/routes/AGENTS.md | File-based routing, -components pattern |
| API endpoints   | packages/api/src/AGENTS.md    | oRPC, isomorphic handlers               |
| Database schema | packages/db/src/AGENTS.md     | Drizzle, migrations                     |
| Auth config     | packages/auth/src/index.ts    | Better-Auth + plugins                   |


## Commands

### Dev and Build

```bash
# start development server
uv run dev
bun run dev
```

### Database Sync

```bash
# Push schema changes to the database
uv run db:push
bun run db:push
```

### Code Quality

```bash
# Formatting and lint repair 
uv run ruff check --fix
bun run biome check .
```


##  Architecture

### 1. Route Architecture

### 2. API Architecture

### 3. Database (ORM)

## Coding Standards

### Formatter

### Components


## ANTI-PATTERNS

## References
