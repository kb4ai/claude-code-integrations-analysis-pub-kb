# Quickstart for New Research Agents

You're an AI assistant picking up this research. Here's how to get oriented fast.

## 30-Second Overview

This repo documents **how projects integrate with Claude Code** (the CLI tool). We analyze source code, extract patterns, and store findings in structured YAML files.

## First Commands to Run

```bash
# 1. Where are we?
pwd
# Should be: .../claude-code-integrations-analysis-pub-kb/

# 2. What's the current state?
./scripts/research_status.py

# 3. What needs to be done?
./scripts/research_status.py --missing
```

## Key Files to Read

| File | Purpose | When to Read |
|------|---------|--------------|
| `FUTURE_WORK.md` | Prioritized task list | First - to pick what to work on |
| `AGENTS.md` | Step-by-step methodology | When analyzing a project |
| `GUIDELINES.md` | Quality standards | Before committing |
| `WHY.md` | Motivation and context | If you need background |

## The Workflow

```
┌─────────────────┐
│ Pick a project  │  ← Check FUTURE_WORK.md or research_status.py --missing
└────────┬────────┘
         ▼
┌─────────────────┐
│ Add submodule   │  ← git submodule add https://github.com/org/repo submodules/name
└────────┬────────┘
         ▼
┌─────────────────┐
│ Copy template   │  ← cp -r projects/_template projects/name
└────────┬────────┘
         ▼
┌─────────────────┐
│ Run discovery   │  ← See AGENTS.md Phase 1 (grep for "claude", "anthropic")
└────────┬────────┘
         ▼
┌─────────────────┐
│ Document in YAML│  ← Fill in cli.cli-integration.yaml, sdk.sdk-integration.yaml
└────────┬────────┘
         ▼
┌─────────────────┐
│ Verify          │  ← ./scripts/verify_yamls.py projects/name/
└────────┬────────┘
         ▼
┌─────────────────┐
│ Commit          │  ← git add && git commit
└─────────────────┘
```

## Common Tasks

### "Start analyzing a new project"

```bash
# Example: analyzing goose
git submodule add https://github.com/block/goose.git submodules/goose
cp -r projects/_template projects/goose

# Edit metadata
# Then follow AGENTS.md for discovery and documentation
```

### "Check what's already been analyzed"

```bash
./scripts/research_status.py
ls projects/
```

### "Validate my work"

```bash
./scripts/verify_yamls.py projects/{name}/
./scripts/research_status.py --project {name}
```

### "Generate reports"

```bash
./scripts/regenerate_comparison_tables_and_reports.py
cat reports/generated/comparison.md
```

## Data Structure

```
projects/{name}/
├── metadata.project.yaml      # Basic info, commit analyzed, status
├── cli.cli-integration.yaml   # CLI flag usage (if applicable)
├── sdk.sdk-integration.yaml   # SDK usage (if applicable)
└── notes.md                   # Observations, comparisons
```

Each YAML file follows a spec in `specs/`. Run verify_yamls.py to check compliance.

## Discovery Commands (copy-paste ready)

When analyzing a project, use these in `submodules/{project}/`:

```bash
# Find Claude references
rg -i "claude" --type py --type ts --type go --type rust

# Find CLI invocations
rg "subprocess|spawn|exec" -A5 | rg -i claude
rg "claude --" .
rg "claude -p" .

# Find SDK imports
rg "from anthropic|import anthropic" .
rg "@anthropic-ai/sdk" .
```

## What Makes a Good Analysis

* [ ] Every claim has a code reference (repo, commit, path, lines)
* [ ] Code snippets are verbatim (not modified)
* [ ] Negative findings documented ("does NOT use X")
* [ ] Checklist items systematically covered
* [ ] Scripts pass validation

## Questions?

* **Methodology unclear?** → Read `AGENTS.md`
* **Standards unclear?** → Read `GUIDELINES.md`
* **Why are we doing this?** → Read `WHY.md`
* **What to work on?** → Read `FUTURE_WORK.md`
