# Research Agent Instructions

Detailed methodology for analyzing Claude Code integrations.

## Quick Start for New Agents

```bash
# 1. Check what's done and what's pending
./scripts/research_status.py

# 2. See FUTURE_WORK.md for priorities
cat FUTURE_WORK.md

# 3. Pick a pending project and analyze it
# Follow the methodology below
```

## Key Operational Lessons

### Write Tool Requires Read First

**Critical**: The Write tool requires reading a file before overwriting it, even if you're replacing the entire content. Always `Read` template-copied files before `Write`.

### Parallel Sub-Agent Strategy

Launch up to 9 Explore agents simultaneously for different repositories. Each agent gets:

* The submodule path
* The full commit SHA
* Specific search instructions for CLI, SDK, MCP, skills patterns
* Request for exact file paths, line numbers, function names, and verbatim snippets

### Commit Strategy

* Submodule additions: separate commit
* CLI analyses: grouped commit
* SDK analyses: grouped commit
* Dual (CLI+SDK) analyses: grouped commit
* Always verify with `./scripts/verify_yamls.py` before committing

### Full 40-char Commit SHA Required

The `analyzed_commit` field requires the full 40-character SHA, not abbreviated. Use `git rev-parse HEAD` in each submodule.

### Document Negative Findings

When a project does NOT use a pattern (e.g., no CLI invocation), explicitly document this:
```yaml
cli_integration_detected: false
summary: "Project does NOT invoke Claude CLI. Uses direct SDK instead."
invocations: []
```

## Research Methodology

### Phase 1: Project Discovery

1. **Identify integration entry points**
   ```bash
   # In submodules/{project}/, search for Claude Code references
   rg -i "claude" --type py --type ts --type go --type rust
   rg "anthropic" --type py --type ts --type go --type rust
   rg "claude-code" .
   rg "claude_code" .
   ```

2. **Locate CLI invocations**
   ```bash
   rg "subprocess|spawn|exec" -A5 -B2 | rg -i claude
   rg '["'"'"']claude["'"'"']' .
   rg "claude --" .
   rg "claude -p" .
   ```

3. **Find SDK imports**
   ```bash
   rg "from anthropic|import anthropic" .
   rg "from claude|import claude" .
   rg "@anthropic|@claude" .  # Decorators
   rg "litellm" .  # LiteLLM abstraction layer
   rg "claude-agent-sdk|claude_agent_sdk" .
   ```

### Phase 2: CLI Integration Analysis

For each CLI invocation found, document in `cli.cli-integration.yaml`:

#### Required Fields

```yaml
invocations:
  - id: unique-invocation-id
    description: "What this invocation does"
    reference:
      repository: https://github.com/org/repo
      commit: full-40-char-hash
      path: relative/path/to/file.py
      lines: [start_line, end_line]
      function: containing_function_name
      class: ContainingClassName  # if applicable

    # CLI details
    command_pattern: "claude --session {uuid} -p {prompt}"
    flags_used:
      - flag: "--session"
        value_type: "uuid"
        purpose: "Session persistence"
      - flag: "-p"
        value_type: "string"
        purpose: "Prompt input"

    # Verbatim code snippet
    snippet: |
      result = subprocess.run(
          ["claude", "--session", session_id, "-p", prompt],
          capture_output=True
      )

    # Cross-references
    related_checklist_items:
      - "cli-flags.checklist.yaml#session-management"
    similar_to:
      - "projects/other-project/cli.cli-integration.yaml#invocation-id"
```

### Phase 3: SDK Integration Analysis

For SDK usage, document in `sdk.sdk-integration.yaml`:

```yaml
sdk_usage:
  - id: unique-sdk-usage-id
    sdk: "anthropic"  # or "claude-agents-sdk", "litellm", etc.
    sdk_version: ">=0.25.0"

    reference:
      repository: https://github.com/org/repo
      commit: full-40-char-hash
      path: src/agent.py
      lines: [10, 45]
      function: create_agent

    patterns_used:
      - pattern: "streaming-messages"
        description: "Uses streaming message API"
        snippet: |
          with client.messages.stream(...) as stream:
              for text in stream.text_stream:
                  yield text

      - pattern: "tool-use"
        description: "Registers custom tools"
        snippet: |
          tools = [
              {"name": "search", "description": "...", ...}
          ]
          response = client.messages.create(tools=tools, ...)
```

### Phase 4: Skills & Plugins Analysis

Document in `skills.skills-plugins.yaml`:

```yaml
skills_support:
  supported: true|false
  discovery_method: "filesystem|registry|config"

  implementation:
    reference:
      repository: ...
      commit: ...
      path: ...
      lines: ...

    snippet: |
      # How skills are discovered/loaded
      skills_dir = Path.home() / ".claude" / "commands"
      for skill_file in skills_dir.glob("*.md"):
          ...

plugins_support:
  supported: true|false
  marketplace_integration: true|false

  implementation:
    reference: ...
    snippet: ...
```

### Phase 5: Verification

1. **Verify code references are accurate**
   ```bash
   # Check that referenced lines contain the snippet
   cd submodules/{project}
   git checkout {commit}
   sed -n '{start},{end}p' {path}
   ```

2. **Validate YAML structure**
   ```bash
   ./scripts/verify_yamls.py projects/{project}/
   ```

3. **Check checklist coverage**
   ```bash
   ./scripts/research_status.py --project {project} --verbose
   ```

## Integration Taxonomy (Discovered Patterns)

### CLI Integration Patterns

| Pattern | Projects | Description |
|---------|----------|-------------|
| Persistent subprocess | goose | Long-running bidirectional NDJSON |
| Per-request spawn | claude-code-mcp, cline | Fresh process per request |
| Multi-instance spawn | claude-flow | Parallel agents with DAG resolution |
| MCP registration | fastmcp | `claude mcp add` for server registration |
| Commands/Skills | anthropic-cookbook | .claude/commands/ and .claude/skills/ |

### SDK Integration Patterns

| Pattern | Projects | Description |
|---------|----------|-------------|
| Direct Anthropic SDK | gptme, cline, continue | Native `anthropic` package |
| Claude Agent SDK | claude-code-action, anthropic-cookbook | `ClaudeSDKClient` + `query()` |
| LiteLLM abstraction | aider, openhands, alphacodium | Multi-provider via LiteLLM |
| AsyncAnthropic | fastmcp | MCP sampling protocol handler |

### Key SDK Features by Project

| Feature | gptme | cline | continue | aider | openhands | cookbook |
|---------|:-----:|:-----:|:--------:|:-----:|:---------:|:-------:|
| Streaming | Y | Y | Y | - | Y | Y |
| Extended thinking | Y | Y | - | Y | - | Y |
| Prompt caching | Y | Y | Y | Y | Y | Y |
| Vision | Y | - | Y | - | Y | Y |
| Tool use | Y | Y | Y | - | Y | Y |
| Web search | Y | - | - | - | - | - |
| MCP | Y | - | - | - | - | Y |

## Checklist Coverage Requirements

### Minimum Viable Analysis

A project analysis is considered "minimally complete" when:

* [ ] `metadata.project.yaml` exists with all required fields
* [ ] At least one integration type documented (CLI or SDK)
* [ ] All code references verified against actual source
* [ ] `./scripts/verify_yamls.py` passes

### Comprehensive Analysis

For "comprehensive" status:

* [ ] All applicable checklist items investigated
* [ ] CLI flags analysis complete (if CLI is used)
* [ ] SDK patterns analysis complete (if SDK is used)
* [ ] Skills/Plugins support documented
* [ ] Cross-references to similar projects added
* [ ] Comparison notes in `notes.md`

## Code Snippet Guidelines

### Do

* Include enough context to understand the snippet (+/-5 lines)
* Preserve original indentation
* Note the programming language
* Include function/class containing the code

### Don't

* Copy entire files
* Include unrelated code
* Modify snippets (keep verbatim)
* Omit attribution

### Example Good Reference

```yaml
reference:
  repository: https://github.com/block/goose
  commit: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
  path: src/goose/cli/claude_integration.py
  lines: [127, 145]
  function: _invoke_claude_session
  class: ClaudeClient
  language: python

snippet: |
  def _invoke_claude_session(self, prompt: str) -> str:
      """Invoke Claude Code with session management."""
      cmd = [
          "claude",
          "--session", self.session_id,
          "--output-format", "streaming-json",
          "-p", prompt
      ]
      if self.skip_permissions:
          cmd.append("--dangerously-skip-permissions")

      result = subprocess.run(cmd, capture_output=True, text=True)
      return self._parse_response(result.stdout)
```

## Priority Projects

Analysis order (updated based on completed work):

**Completed (12/12):**

1. goose (Block) - Persistent subprocess CLI
2. aider - LiteLLM + cache warming
3. continue - Direct SDK + 4 caching strategies
4. cline - Dual CLI+SDK integration
5. claude-code-action - Official Agent SDK
6. claude-code-mcp - Agent-in-agent MCP wrapper
7. claude-flow - Multi-instance CLI orchestrator
8. openhands - LiteLLM + A/B testing
9. fastmcp - MCP sampling + CLI registration + Skills
10. gptme - Deep native Anthropic SDK
11. alphacodium - LiteLLM abstraction (minimal)
12. anthropic-cookbook - Official canonical examples

**Template only:**

* _template - Intentionally kept as template

## Related Documents

* `QUICKSTART.md` - 5-minute orientation
* `FUTURE_WORK.md` - Prioritized roadmap
* `GUIDELINES.md` - Quality standards
* `WHY.md` - Motivation and context
* `DISCOVERED_PROJECTS.md` - Full discovery list (50+ projects)
* `specs/*.spec.yaml` - YAML schemas
* `checklists/*.checklist.yaml` - Research criteria

## Updating Existing Analysis

When a project releases updates:

1. Update submodule to new commit
2. Re-run discovery searches
3. Update YAML files with new/changed references
4. Add `updated_at` timestamp
5. Note changes in `CHANGELOG.md` (if significant)
