# Claude Code Integration Approaches

*Generated: 2026-02-08*

A practical reference to every integration approach discovered across 12 open-source projects.

Each approach includes a copy-pasteable educational example and links to real production code in the per-project detail pages.

## Approaches at a Glance

| # | Approach | Projects |
|---|----------|----------|
| | **CLI** | |
| 1 | [Persistent Subprocess (Bidirectional NDJSON)](#persistent-subprocess-bidirectional-ndjson) | [goose](projects/goose.md) |
| 2 | [Per-Request Spawn (Simple)](#per-request-spawn-simple) | [claude-code-mcp](projects/claude-code-mcp.md) |
| 3 | [Per-Request Spawn (Structured Output)](#per-request-spawn-structured-output) | [cline](projects/cline.md) |
| 4 | [Multi-Instance Orchestration](#multi-instance-orchestration) | [claude-flow](projects/claude-flow.md) |
| 5 | [Commands & Skills (Declarative)](#commands--skills-declarative) | [anthropic-cookbook](projects/anthropic-cookbook.md), [fastmcp](projects/fastmcp.md) |
| | **SDK** | |
| 6 | [Claude Agent SDK](#claude-agent-sdk) | [claude-code-action](projects/claude-code-action.md), [anthropic-cookbook](projects/anthropic-cookbook.md) |
| 7 | [Direct Anthropic SDK](#direct-anthropic-sdk) | [gptme](projects/gptme.md), [cline](projects/cline.md), [continue](projects/continue.md), [fastmcp](projects/fastmcp.md) |
| 8 | [LiteLLM Abstraction](#litellm-abstraction) | [aider](projects/aider.md), [openhands](projects/openhands.md), [alphacodium](projects/alphacodium.md) |
| | **Cross-Cutting** | |
| 9 | [Prompt Caching](#prompt-caching) | [gptme](projects/gptme.md), [cline](projects/cline.md), [aider](projects/aider.md), [continue](projects/continue.md), [openhands](projects/openhands.md) |
| 10 | [Extended Thinking](#extended-thinking) | [gptme](projects/gptme.md), [cline](projects/cline.md), [aider](projects/aider.md), [continue](projects/continue.md), [anthropic-cookbook](projects/anthropic-cookbook.md) |


---

## CLI Approaches

### Persistent Subprocess (Bidirectional NDJSON)

Spawn Claude Code once as a long-running subprocess. Communicate via
stdin/stdout using newline-delimited JSON (NDJSON). The process persists
across many user messages, avoiding cold-start overhead.

```bash
# Start Claude Code as a persistent subprocess with NDJSON I/O
claude \
  --input-format stream-json \
  --output-format stream-json \
  --verbose \
  --system-prompt "You are a helpful coding assistant." &
CLAUDE_PID=$!

# Send a message via stdin (one JSON object per line)
echo '{"type":"user","message":{"role":"user","content":[{"type":"text","text":"Hello"}]}}' \
  > /proc/$CLAUDE_PID/fd/0

# Read NDJSON responses from stdout:
#   {"type":"assistant","message":{"role":"assistant","content":[...]}}
#   {"type":"result","cost":0.003,"duration_ms":1200,"session_id":"..."}
```

**Projects using this approach:**

| Project | Language | Detail Page |
|---------|----------|-------------|
| [Goose (Block)](https://github.com/block/goose) | Rust | [code quotes & permalinks](projects/goose.md) |

### Per-Request Spawn (Simple)

Spawn a fresh Claude Code process for each request. Pass the prompt
with `-p`, collect raw text from stdout. Simplest possible integration.

```bash
# One-shot: spawn, pass prompt, collect output
result=$(claude --dangerously-skip-permissions -p "Explain this error: $ERROR_MSG")
echo "$result"

# With timeout and working directory
timeout 1800 claude \
  --dangerously-skip-permissions \
  -p "Fix the failing test in tests/auth.py" \
  2>/dev/null
```

**Projects using this approach:**

| Project | Language | Detail Page |
|---------|----------|-------------|
| [Claude Code MCP (steipete)](https://github.com/steipete/claude-code-mcp) | TypeScript | [code quotes & permalinks](projects/claude-code-mcp.md) |

### Per-Request Spawn (Structured Output)

Spawn per-request with `--output-format stream-json` for structured NDJSON
events. Use `--max-turns 1` and `--disallowedTools` to make Claude Code act
as a single-turn LLM while your app handles orchestration.

```bash
# Structured single-turn: get NDJSON events back
echo '[{"role":"user","content":"Refactor this function"}]' | \
  claude \
    --output-format stream-json \
    --verbose \
    --max-turns 1 \
    --model claude-sonnet-4-5-20250929 \
    --disallowedTools "Bash,Write,Edit" \
    -p

# Each line of stdout is a JSON event:
#   {"type":"assistant","message":{"content":[{"type":"text","text":"..."}]}}
#   {"type":"result","session_id":"...","cost":0.002}
```

**Projects using this approach:**

| Project | Language | Detail Page |
|---------|----------|-------------|
| [Cline (VS Code Extension)](https://github.com/cline/cline) | TypeScript | [code quotes & permalinks](projects/cline.md) |

### Multi-Instance Orchestration

Spawn multiple Claude Code instances in parallel for multi-agent workflows.
Tasks within a phase run concurrently; phases run sequentially.
Stream-chain: pipe stdout of one agent as context to the next.

```bash
# Agent 1: Research
claude --print --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  "Research the authentication options" > /tmp/agent1.ndjson &

# Agent 2: Implementation (after agent 1 completes)
wait
CONTEXT=$(cat /tmp/agent1.ndjson | jq -r 'select(.type=="assistant") | .message.content[].text')
claude --print --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  "Previous research:\n$CONTEXT\n\nNow implement the chosen approach" > /tmp/agent2.ndjson &

# Agent 3: Testing (parallel with agent 2)
claude --print --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  "Write tests for the auth module" > /tmp/agent3.ndjson &
wait
```

**Projects using this approach:**

| Project | Language | Detail Page |
|---------|----------|-------------|
| [Claude Flow](https://github.com/ruvnet/claude-flow) | TypeScript | [code quotes & permalinks](projects/claude-flow.md) |

### Commands & Skills (Declarative)

No subprocess management code. Use Claude Code's built-in extensibility:
`.claude/commands/` for slash commands with YAML frontmatter,
`.claude/skills/` for reusable expertise, `claude mcp add` for MCP servers.

```markdown
<!-- .claude/commands/review-pr.md -->
---
allowed-tools: Bash(gh pr diff:*),Bash(gh pr comment:*),Read,Glob,Grep
description: Review a pull request
---
Review PR #$ARGUMENTS using best practices.
Check for security issues, test coverage, and code quality.

<!-- .claude/skills/python-testing/SKILL.md -->
---
description: Expert at writing Python tests with pytest
---
When writing tests, always use pytest fixtures and parametrize.

# Register an MCP server with Claude Code
claude mcp add my-server -e API_KEY=sk-123 -- npx my-mcp-server
```

**Projects using this approach:**

| Project | Language | Detail Page |
|---------|----------|-------------|
| [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook) | Python | [code quotes & permalinks](projects/anthropic-cookbook.md) |
| [FastMCP](https://github.com/jlowin/fastmcp) | Python | [code quotes & permalinks](projects/fastmcp.md) |


---

## SDK Approaches

### Claude Agent SDK

Higher-level SDK that wraps Claude Code itself. The `query()` async iterator
yields messages in real-time. Manages sessions, tools, and permissions.
Works with your Claude subscription (no separate API key needed with some setups).
This is the official programmatic interface to Claude Code.

```typescript
// TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

const messages = query({
  model: "claude-sonnet-4-5-20250929",
  prompt: "Add input validation to the signup form",
  maxTurns: 10,
  allowedTools: ["Read", "Write", "Edit", "Bash"],
  systemPrompt: "You are a senior engineer.",
});

for await (const msg of messages) {
  if (msg.type === "assistant") console.log(msg.message.content);
  if (msg.type === "result") console.log("Cost:", msg.cost_usd);
}
```

```python
# Python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

options = ClaudeAgentOptions(
    model="claude-sonnet-4-5-20250929",
    allowed_tools=["Read", "Write", "Edit", "Bash"],
    permission_mode="acceptEdits",
)
async with ClaudeSDKClient(options=options) as agent:
    await agent.query(prompt="Add input validation to the signup form")
    async for msg in agent.receive_response():
        print(msg)
```

**Projects using this approach:**

| Project | Language | Detail Page |
|---------|----------|-------------|
| [Claude Code Action (Anthropic)](https://github.com/anthropics/claude-code-action) | TypeScript | [code quotes & permalinks](projects/claude-code-action.md) |
| [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook) | Python | [code quotes & permalinks](projects/anthropic-cookbook.md) |

### Direct Anthropic SDK

Use the official Anthropic client library directly. Call
`client.messages.create()` or `client.messages.stream()` for full control
over API parameters, streaming, prompt caching, and extended thinking.

```python
from anthropic import Anthropic

client = Anthropic()  # uses ANTHROPIC_API_KEY env var

with client.messages.stream(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    system=[{
        "type": "text",
        "text": "You are a code reviewer.",
        "cache_control": {"type": "ephemeral"},  # prompt caching
    }],
    messages=[{"role": "user", "content": "Review this diff: ..."}],
    thinking={"type": "enabled", "budget_tokens": 10000},  # extended thinking
) as stream:
    for event in stream:
        if hasattr(event, "text"):
            print(event.text, end="")
```

```typescript
// TypeScript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();
const stream = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 4096,
  system: [{ type: "text", text: "You are a code reviewer.",
             cache_control: { type: "ephemeral" } }],
  messages: [{ role: "user", content: "Review this diff: ..." }],
  thinking: { type: "enabled", budget_tokens: 10000 },
  stream: true,
});
for await (const chunk of stream) {
  if (chunk.type === "content_block_delta") process.stdout.write(chunk.delta.text ?? "");
}
```

**Projects using this approach:**

| Project | Language | Detail Page |
|---------|----------|-------------|
| [gptme](https://github.com/ErikBjare/gptme) | Python | [code quotes & permalinks](projects/gptme.md) |
| [Cline (VS Code Extension)](https://github.com/cline/cline) | TypeScript | [code quotes & permalinks](projects/cline.md) |
| [Continue.dev](https://github.com/continuedev/continue) | TypeScript | [code quotes & permalinks](projects/continue.md) |
| [FastMCP](https://github.com/jlowin/fastmcp) | Python | [code quotes & permalinks](projects/fastmcp.md) |

### LiteLLM Abstraction

Multi-provider abstraction via LiteLLM. Claude is one of many supported
models. Prefix determines routing: `anthropic/claude-sonnet-4-20250514`.
Anthropic-specific features (caching, thinking) passed via extra parameters.

```python
import litellm

# LiteLLM routes to Anthropic based on model prefix
response = litellm.completion(
    model="anthropic/claude-sonnet-4-20250514",
    messages=[
        {"role": "system", "content": "You are a coding assistant."},
        {"role": "user", "content": "Explain this error: ..."},
    ],
    stream=True,
    # Anthropic-specific: prompt caching header
    extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
    # Anthropic-specific: extended thinking
    thinking={"type": "enabled", "budget_tokens": 10000},
)
for chunk in response:
    print(chunk.choices[0].delta.content or "", end="")
```

**Projects using this approach:**

| Project | Language | Detail Page |
|---------|----------|-------------|
| [Aider](https://github.com/paul-gauthier/aider) | Python | [code quotes & permalinks](projects/aider.md) |
| [OpenHands (All-Hands-AI)](https://github.com/All-Hands-AI/OpenHands) | Python | [code quotes & permalinks](projects/openhands.md) |
| [AlphaCodium](https://github.com/Codium-ai/AlphaCodium) | Python | [code quotes & permalinks](projects/alphacodium.md) |


---

## Cross-Cutting Approaches

### Prompt Caching

Reduce cost and latency by caching parts of the prompt across requests.
Add `cache_control: {type: "ephemeral"}` to message content blocks.
Place breakpoints on stable content (system prompt, tool definitions)
for highest cache hit rates.

```python
# Prompt caching: mark stable content with cache_control
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    system=[{
        "type": "text",
        "text": LARGE_SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"},     # breakpoint 1: system
    }],
    messages=[
        {"role": "user", "content": [
            {"type": "text", "text": repo_context,
             "cache_control": {"type": "ephemeral"}},  # breakpoint 2: context
        ]},
        {"role": "user", "content": user_question},     # changes each turn
    ],
)
# Check cache effectiveness in response.usage:
#   cache_creation_input_tokens, cache_read_input_tokens
```

**Projects using this approach:**

| Project | Language | Detail Page |
|---------|----------|-------------|
| [gptme](https://github.com/ErikBjare/gptme) | Python | [code quotes & permalinks](projects/gptme.md) |
| [Cline (VS Code Extension)](https://github.com/cline/cline) | TypeScript | [code quotes & permalinks](projects/cline.md) |
| [Aider](https://github.com/paul-gauthier/aider) | Python | [code quotes & permalinks](projects/aider.md) |
| [Continue.dev](https://github.com/continuedev/continue) | TypeScript | [code quotes & permalinks](projects/continue.md) |
| [OpenHands (All-Hands-AI)](https://github.com/All-Hands-AI/OpenHands) | Python | [code quotes & permalinks](projects/openhands.md) |

### Extended Thinking

Let Claude reason step-by-step before answering. Set a token budget for
the thinking phase. Temperature MUST be 1 (or omitted) when thinking is enabled.
Thinking content appears as separate blocks in the response.

```python
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=8192,
    temperature=1,  # REQUIRED when thinking is enabled
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "Find the bug in this code: ..."}],
)

for block in response.content:
    if block.type == "thinking":
        print(f"[Reasoning] {block.thinking}")
    elif block.type == "text":
        print(f"[Answer] {block.text}")
```

**Projects using this approach:**

| Project | Language | Detail Page |
|---------|----------|-------------|
| [gptme](https://github.com/ErikBjare/gptme) | Python | [code quotes & permalinks](projects/gptme.md) |
| [Cline (VS Code Extension)](https://github.com/cline/cline) | TypeScript | [code quotes & permalinks](projects/cline.md) |
| [Aider](https://github.com/paul-gauthier/aider) | Python | [code quotes & permalinks](projects/aider.md) |
| [Continue.dev](https://github.com/continuedev/continue) | TypeScript | [code quotes & permalinks](projects/continue.md) |
| [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook) | Python | [code quotes & permalinks](projects/anthropic-cookbook.md) |


---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
