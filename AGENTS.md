# Research Agent Instructions

Detailed methodology for analyzing Claude Code integrations.

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
    sdk: "anthropic"  # or "claude-agents-sdk", etc.
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

* Include enough context to understand the snippet (±5 lines)
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

Suggested analysis order:

1. **goose** (Block) - Known Claude Code integration
2. **aider** - Popular AI coding assistant
3. **continue** - VS Code/JetBrains extension
4. **cursor** - AI-native editor
5. **cline** - VS Code Claude extension
6. **claude-dev** - Official examples/templates
7. **mentat** - AI coding assistant
8. **gptme** - Multi-model assistant

## Updating Existing Analysis

When a project releases updates:

1. Update submodule to new commit
2. Re-run discovery searches
3. Update YAML files with new/changed references
4. Add `updated_at` timestamp
5. Note changes in `CHANGELOG.md` (if significant)
