# Claude Code Integrations Analysis - AI Agent Instructions

This repository systematically analyzes how external projects integrate with Claude Code.

## New Here? Start With These

| Document | Purpose |
|----------|---------|
| `QUICKSTART.md` | **Start here** - 5-minute orientation |
| `FUTURE_WORK.md` | What to work on next, prioritized |
| `AGENTS.md` | Detailed research methodology |
| `GUIDELINES.md` | Quality standards and best practices |
| `WHY.md` | Motivation and context for this research |

## First Commands

```bash
./scripts/research_status.py          # What's done/pending?
./scripts/research_status.py --missing # What's missing?
cat FUTURE_WORK.md                     # What to work on?
```

## Mission

Document **exactly how** projects integrate with Claude Code, with precise code references:

* Repository URL, commit hash, file path, line numbers
* Function/class names containing the integration logic
* Verbatim code snippets (properly attributed)
* CLI flags, SDK methods, configuration patterns used

## Key Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Detailed research methodology and criteria |
| `specs/*.spec.yaml` | YAML schemas for data files |
| `checklists/*.checklist.yaml` | Research criteria checklists |
| `projects/{name}/*.yaml` | Per-project analysis data |
| `submodules/{name}/` | Git submodules of analyzed repos |

## Workflow for Research Agents

### 1. Check Current Status

```bash
./scripts/research_status.py
```

This shows:

* Projects analyzed vs. pending
* Checklist coverage per project
* Missing data fields

### 2. Select a Project to Analyze

Pick from uncovered projects or deepen existing analysis per checklist gaps.

### 3. Clone/Update Submodule

```bash
# New project
git submodule add https://github.com/org/repo.git submodules/{name}

# Existing - update to latest
cd submodules/{name} && git fetch && git checkout origin/main && cd ../..
```

### 4. Perform Analysis

Follow `AGENTS.md` research methodology. Key questions:

* How does it invoke Claude Code CLI? Which flags?
* Does it use Claude Agents SDK? Which functions?
* Does it support Skills? How are they loaded/invoked?
* Does it support Plugins/Marketplace? How?

### 5. Document Findings

Create/update YAML files in `projects/{name}/`:

* `metadata.project.yaml` - Basic project info
* `cli.cli-integration.yaml` - CLI integration details
* `sdk.sdk-integration.yaml` - SDK usage (if applicable)
* `*.code-reference.yaml` - Code snippets with references

### 6. Verify and Commit

```bash
./scripts/verify_yamls.py projects/{name}/
./scripts/research_status.py --project {name}
git add projects/{name}/ submodules/{name}
git commit -m "Add/update {name} integration analysis"
```

## Code Reference Requirements

**Every claim must have a code reference.** Structure:

```yaml
- claim: "Goose uses --output-format=streaming-json"
  reference:
    repository: https://github.com/block/goose
    commit: abc123def456
    path: src/claude/client.py
    lines: [142, 158]
    function: invoke_claude
    snippet: |
      subprocess.run([
          "claude",
          "--output-format=streaming-json",
          "-p", prompt
      ])
```

## Specs and Validation

Data files must conform to specs in `specs/`:

* `project.spec.yaml` - Project metadata schema
* `cli-integration.spec.yaml` - CLI analysis schema
* `sdk-integration.spec.yaml` - SDK analysis schema
* `code-reference.spec.yaml` - Code reference schema

Run `./scripts/verify_yamls.py` before committing.

## Integration Patterns to Investigate

From `checklists/`:

### CLI Flags (checklists/cli-flags.checklist.yaml)

* `--session $UUID` / `--resume $UUID` - Session management
* `-p "$PROMPT"` / `--print` - Prompt passing
* `--output-format` - Output format (text, json, streaming-json)
* `--dangerously-skip-permissions` - Permission bypass
* `--model` - Model selection
* `--max-turns` - Turn limits
* `--system-prompt` - Custom system prompts
* `--allowedTools` - Tool restrictions
* `--mcp-config` - MCP configuration
* Environment variables (ANTHROPIC_API_KEY, CLAUDE_CODE_*, etc.)

### SDK Features (checklists/sdk-features.checklist.yaml)

* Agent creation and configuration
* Tool registration
* Message/conversation management
* Streaming vs. synchronous execution
* Error handling patterns
* Context/memory management

### Skills & Plugins (checklists/skills-plugins.checklist.yaml)

* Skill discovery and loading
* Skill invocation patterns
* Plugin registration
* Marketplace integration
* Custom command creation

## Cross-References

When documenting, always link:

* To relevant checklist items
* To spec field definitions
* Between related projects (e.g., "similar pattern to goose, see projects/goose/cli.cli-integration.yaml:45")

## Detailed Methodology

@AGENTS.md
