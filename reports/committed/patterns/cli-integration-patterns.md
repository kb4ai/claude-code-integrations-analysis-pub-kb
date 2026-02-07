# CLI Integration Patterns

Cross-cutting analysis of how projects spawn and interact with the Claude Code CLI binary.

## Pattern Taxonomy

Five distinct CLI integration patterns emerged from the 12 analyzed projects.
Six projects use CLI integration; the remaining six use SDK-only approaches.

### 1. Persistent Subprocess (Bidirectional NDJSON)

**Used by:** goose

**Description:** Spawns Claude Code as a long-running subprocess and communicates via
bidirectional NDJSON (newline-delimited JSON) on stdin/stdout. The process persists
across multiple user interactions.

**Key flags:** `--input-format stream-json --output-format stream-json --verbose`

**Trade-offs:**

* (+) Lower latency for subsequent messages (no process spawn overhead)
* (+) Natural session continuity within a single process
* (-) Process lifecycle management complexity
* (-) Must handle process crashes and restarts

**Reference:** `projects/goose/cli.cli-integration.yaml#claude-code-provider-spawn`

```rust
let mut cmd = Command::new(claude_code_command);
cmd.arg("--input-format").arg("stream-json")
   .arg("--output-format").arg("stream-json")
   .arg("--verbose")
   .arg("--system-prompt").arg(&system_prompt);
```

### 2. Per-Request Spawn (Simple)

**Used by:** claude-code-mcp

**Description:** Spawns a fresh Claude Code process for each request. Minimal flags,
collects raw stdout/stderr text. Simplest integration pattern.

**Key flags:** `--dangerously-skip-permissions -p {prompt}`

**Trade-offs:**

* (+) Stateless, no process management
* (+) Simple error handling (process exit = done)
* (-) Cold start overhead per request
* (-) No structured output parsing

**Reference:** `projects/claude-code-mcp/cli.cli-integration.yaml#mcp-tool-spawn`

```typescript
const claudeProcess = spawn(claudeCommand, [
  '--dangerously-skip-permissions',
  '-p',
  prompt,
], { shell: false, timeout: 30 * 60 * 1000 });
```

### 3. Per-Request Spawn (Structured Output)

**Used by:** cline

**Description:** Spawns per-request like pattern 2, but uses `--output-format stream-json`
for structured NDJSON output. Rich flag usage for fine-grained control.

**Key flags:** `--output-format stream-json --verbose --max-turns 1 --disallowedTools {tools} --model {model} -p`

**Trade-offs:**

* (+) Structured output enables precise event handling
* (+) Tool restrictions keep Claude Code as pure LLM (orchestration stays external)
* (+) Model selection per-request
* (-) More complex output parsing
* (-) Still has cold start overhead

**Reference:** `projects/cline/cli.cli-integration.yaml#claude-code-handler-spawn`

```typescript
const args = [
  "--system-prompt", systemPrompt,
  "--verbose", "--output-format", "stream-json",
  "--disallowedTools", claudeCodeTools,
  "--max-turns", "1",
  "--model", modelId,
  "-p",
];
```

### 4. Multi-Instance Spawn (Parallel Orchestration)

**Used by:** claude-flow

**Description:** Spawns multiple Claude Code instances simultaneously for parallel
multi-agent orchestration. Supports stream chaining (stdout of one instance piped
as context to stdin of the next).

**Key flags:** `--print --output-format stream-json --verbose [--input-format stream-json] --dangerously-skip-permissions`

**Trade-offs:**

* (+) Parallelism for independent tasks
* (+) DAG-based dependency resolution between agents
* (+) Stream chaining for sequential pipelines
* (-) Resource-intensive (multiple Claude processes)
* (-) Complex coordination logic

**Reference:** `projects/claude-flow/cli.cli-integration.yaml#automation-executor-spawn`

```javascript
claudeArgs.push('--print');
claudeArgs.push('--output-format', 'stream-json');
claudeArgs.push('--verbose');
if (options.inputStream) {
  claudeArgs.push('--input-format', 'stream-json');
}
claudeArgs.push('--dangerously-skip-permissions');
```

### 5. Commands & Skills (Declarative)

**Used by:** anthropic-cookbook, fastmcp

**Description:** Uses Claude Code's built-in extensibility (`.claude/commands/`,
`.claude/skills/`, `claude mcp add`) rather than spawning processes directly.
Declarative configuration instead of imperative subprocess management.

**Key mechanism:** YAML frontmatter with `allowed-tools` restrictions per command

**Trade-offs:**

* (+) No subprocess management code
* (+) Declarative tool restrictions
* (+) Native Claude Code integration
* (-) Less control over execution
* (-) Depends on Claude Code's internal command system

**Reference:** `projects/anthropic-cookbook/cli.cli-integration.yaml#claude-commands`

```yaml
---
allowed-tools: Bash(gh pr comment:*),Bash(gh pr diff:*),Read,Glob,Grep,WebFetch
description: Comprehensive review of Jupyter notebooks and Python scripts
---
```

## CLI Flag Usage Summary

| Flag | goose | claude-code-mcp | claude-flow | cline | anthropic-cookbook |
|------|:-----:|:---------------:|:-----------:|:-----:|:-----------------:|
| `-p` | - | Y | Y | Y | - |
| `--output-format stream-json` | Y | - | Y | Y | - |
| `--input-format stream-json` | Y | - | Y | - | - |
| `--verbose` | Y | - | Y | Y | - |
| `--dangerously-skip-permissions` | Y | Y | Y | - | - |
| `--model` | Y | - | - | Y | - |
| `--system-prompt` | Y | - | - | Y | - |
| `--max-turns` | - | - | - | Y | - |
| `--disallowedTools` | - | - | - | Y | - |
| `--permission-mode` | Y | - | - | - | - |
| `--print` | - | - | Y | - | - |
| `allowed-tools` (frontmatter) | - | - | - | - | Y |

## Common Patterns Across Projects

### Output Format: stream-json Dominates

4 of 5 CLI-spawning projects use `--output-format stream-json` for structured NDJSON.
Only claude-code-mcp collects raw text. The standard NDJSON event types are:

* `assistant` - Content blocks (text, tool_use)
* `result` - Final result with cost, duration, session_id
* `error` - Error events

### Permission Handling

Three approaches to permissions:

1. **Skip entirely:** `--dangerously-skip-permissions` (goose, claude-code-mcp, claude-flow)
2. **Accept edits:** `--permission-mode acceptEdits` (goose with GOOSE_MODE=smart-approve)
3. **External handling:** Cline manages permissions itself, doesn't pass permission flags

### Binary Resolution

Projects locate the Claude binary through multi-step resolution:

1. **Environment variable** (CLAUDE_CLI_NAME, CLAUDE_CODE_COMMAND)
2. **Known install path** (~/.claude/local/claude)
3. **PATH fallback** ("claude")

### Stdin Message Format

Two projects use stdin for message input:

* **goose:** NDJSON objects `{"type":"user","message":{"role":"user","content":[...]}}`
* **cline:** JSON array of messages written once, then stdin closed

### Environment Variables

Common env vars used across CLI integrations:

| Variable | Used By | Purpose |
|----------|---------|---------|
| ANTHROPIC_API_KEY | cline (removed), claude-code-action | API authentication |
| CLAUDE_CODE_MAX_OUTPUT_TOKENS | cline | Max output tokens |
| CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC | cline | Disable telemetry |
| MAX_THINKING_TOKENS | cline | Thinking budget |
| GOOSE_MODE | goose | Permission mode mapping |
| CLAUDE_CODE_COMMAND | goose | Binary path override |
| CLAUDE_CLI_NAME | claude-code-mcp | Binary name override |

---
*Extracted from 12 project analyses in projects/*
