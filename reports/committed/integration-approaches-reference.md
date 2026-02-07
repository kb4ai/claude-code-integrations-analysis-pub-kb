# Claude Code Integration Approaches Reference

A practical guide to every integration approach discovered across 12 open-source projects,
with clickable GitHub permalinks to real production code.

## Approaches at a Glance

| # | Approach | What It Does | Projects |
|---|----------|-------------|----------|
| **CLI Approaches** | | | |
| 1 | [Persistent Subprocess](#1-persistent-subprocess-bidirectional-ndjson) | Long-running Claude process, bidirectional NDJSON | goose |
| 2 | [Per-Request Spawn (Simple)](#2-per-request-spawn-simple) | Fresh process per request, raw text output | claude-code-mcp |
| 3 | [Per-Request Spawn (Structured)](#3-per-request-spawn-structured-output) | Fresh process per request, stream-json output | cline |
| 4 | [Multi-Instance Orchestration](#4-multi-instance-orchestration) | Parallel Claude processes with DAG resolution | claude-flow |
| 5 | [Commands & Skills](#5-commands--skills-declarative) | Declarative .claude/commands/ and .claude/skills/ | anthropic-cookbook, fastmcp |
| **SDK Approaches** | | | |
| 6 | [Claude Agent SDK](#6-claude-agent-sdk) | query() async iterator wrapping Claude Code | claude-code-action, anthropic-cookbook |
| 7 | [Direct Anthropic SDK](#7-direct-anthropic-sdk) | client.messages.create/stream directly | gptme, cline, continue, fastmcp |
| 8 | [LiteLLM Abstraction](#8-litellm-abstraction) | Multi-provider routing via LiteLLM | aider, openhands, alphacodium |
| **Cross-Cutting Patterns** | | | |
| 9 | [Prompt Caching](#9-prompt-caching) | Cache breakpoints to reduce cost | gptme, cline, aider, continue, openhands |
| 10 | [Extended Thinking](#10-extended-thinking) | Reasoning budget tokens | gptme, cline, aider, continue, anthropic-cookbook |
| 11 | [NDJSON Stream Parsing](#11-ndjson-stream-parsing) | Parse stream-json output events | goose, cline, claude-flow |

---

## CLI Approaches

### 1. Persistent Subprocess (Bidirectional NDJSON)

**Project:** goose (Block)
**Language:** Rust

Spawns Claude Code once and keeps it running. Sends messages via stdin NDJSON,
receives responses via stdout NDJSON. Lowest latency for multi-turn conversations.

**Flags:** `--input-format stream-json --output-format stream-json --verbose --system-prompt {prompt}`

**Source:** [`crates/goose-llm/src/claude_code_provider.rs` L1-L80](https://github.com/block/goose/blob/b18120bec310365d96cafcc34ea63d8534e3ee57/crates/goose-llm/src/claude_code_provider.rs#L1-L80)

```rust
// Spawns Claude Code as persistent subprocess
let mut cmd = Command::new(claude_code_command);
cmd.arg("--input-format").arg("stream-json")
   .arg("--output-format").arg("stream-json")
   .arg("--verbose")
   .arg("--system-prompt").arg(&system_prompt);

// Model selection - only for specific values
if model == "sonnet" || model == "opus" {
    cmd.arg("--model").arg(&model);
}

// Permission mode mapping from GOOSE_MODE env var
match goose_mode.as_str() {
    "auto" => { cmd.arg("--dangerously-skip-permissions"); }
    "smart-approve" => { cmd.arg("--permission-mode").arg("acceptEdits"); }
    _ => {}
}
```

**Sending messages** via stdin NDJSON:
[`claude_code_provider.rs` L85-L120](https://github.com/block/goose/blob/b18120bec310365d96cafcc34ea63d8534e3ee57/crates/goose-llm/src/claude_code_provider.rs#L85-L120)

```rust
let msg = json!({
    "type": "user",
    "message": {
        "role": "user",
        "content": content_blocks
    }
});
stdin.write_all(serde_json::to_string(&msg)?.as_bytes())?;
stdin.write_all(b"\n")?;
```

**Parsing responses** from stdout NDJSON:
[`claude_code_provider.rs` L125-L180](https://github.com/block/goose/blob/b18120bec310365d96cafcc34ea63d8534e3ee57/crates/goose-llm/src/claude_code_provider.rs#L125-L180)

```rust
for line in reader.lines() {
    let event: Value = serde_json::from_str(&line?)?;
    match event["type"].as_str() {
        Some("assistant") => { /* content blocks: text, tool_use */ }
        Some("result")    => { /* final: cost, duration, session_id */ break; }
        Some("error")     => { /* error handling */ }
        _ => {}
    }
}
```

---

### 2. Per-Request Spawn (Simple)

**Project:** claude-code-mcp (steipete)
**Language:** TypeScript

Spawns a fresh Claude Code process for each MCP tool invocation. Minimal flags,
collects raw stdout text. Simplest possible integration.

**Flags:** `--dangerously-skip-permissions -p {prompt}`

**Source:** [`src/claude-api.ts` L40-L95](https://github.com/steipete/claude-code-mcp/blob/24dfd389393cf35cc1390567bedda2d165756ef3/src/claude-api.ts#L40-L95)

```typescript
const claudeProcess = spawn(claudeCommand, [
  '--dangerously-skip-permissions',
  '-p',
  prompt,
], {
  shell: false,
  stdio: ['ignore', 'pipe', 'pipe'],
  cwd: workFolder || process.cwd(),
  timeout: 30 * 60 * 1000, // 30 minutes
});
```

**Binary resolution** (3-stage fallback):
[`src/claude-api.ts` L10-L35](https://github.com/steipete/claude-code-mcp/blob/24dfd389393cf35cc1390567bedda2d165756ef3/src/claude-api.ts#L10-L35)

```typescript
function findClaudeCommand(): string {
  if (process.env.CLAUDE_CLI_NAME) return process.env.CLAUDE_CLI_NAME;
  const defaultPath = path.join(os.homedir(), '.claude', 'local', 'claude');
  if (fs.existsSync(defaultPath)) return defaultPath;
  return 'claude';
}
```

---

### 3. Per-Request Spawn (Structured Output)

**Project:** cline
**Language:** TypeScript

Spawns per-request like approach 2, but uses `--output-format stream-json` for
structured events. Richest flag usage of any CLI integration. Key insight:
`--max-turns 1` + `--disallowedTools` makes Claude Code act as a single-turn LLM
while Cline handles orchestration.

**Flags:** `--system-prompt {prompt} --verbose --output-format stream-json --disallowedTools {tools} --max-turns 1 --model {model} -p`

**Source:** [`src/integrations/claude-code/run.ts` L189-L242](https://github.com/cline/cline/blob/844038084c6e559ee131c32e5d5da93dcff68a73/src/integrations/claude-code/run.ts#L189-L242)

```typescript
const args = [
  shouldUseFile ? "--system-prompt-file" : "--system-prompt",
  systemPrompt,
  "--verbose",
  "--output-format", "stream-json",
  "--disallowedTools", claudeCodeTools,
  "--max-turns", "1",
  "--model", modelId,
  "-p",
];

const env: NodeJS.ProcessEnv = {
  ...process.env,
  CLAUDE_CODE_MAX_OUTPUT_TOKENS: process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS || "32000",
  CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC: "1",
  DISABLE_NON_ESSENTIAL_MODEL_CALLS: "1",
  MAX_THINKING_TOKENS: (thinkingBudgetTokens || 0).toString(),
};
delete env["ANTHROPIC_API_KEY"];  // Let Claude Code handle auth

const claudeCodeProcess = execa(claudePath, args, {
  stdin: "pipe", stdout: "pipe", stderr: "pipe",
  env, cwd, maxBuffer: BUFFER_SIZE, timeout: CLAUDE_CODE_TIMEOUT,
});
claudeCodeProcess.stdin.write(JSON.stringify(messages));
claudeCodeProcess.stdin.end();
```

---

### 4. Multi-Instance Orchestration

**Project:** claude-flow (ruvnet)
**Language:** JavaScript

Spawns multiple Claude Code instances in parallel for multi-agent workflows.
Phase-based execution: tasks within a phase run in parallel (Promise.allSettled),
phases run sequentially. Supports stream chaining (stdout of one agent piped
as context to the next).

**Flags:** `--print --output-format stream-json --verbose [--input-format stream-json] --dangerously-skip-permissions`

**Primary spawn:** [`v2/src/cli/simple-commands/automation-executor.js` L229-L275](https://github.com/ruvnet/claude-flow/blob/e82a79419c6a648a36de3529ab5d44a8a4d818a4/v2/src/cli/simple-commands/automation-executor.js#L229-L275)

```javascript
async spawnClaudeInstance(agent, prompt, options = {}) {
  const claudeArgs = [];
  if (this.options.nonInteractive) {
    claudeArgs.push('--print');
    if (this.options.outputFormat === 'stream-json') {
      claudeArgs.push('--output-format', 'stream-json');
      claudeArgs.push('--verbose');
      if (options.inputStream) {
        claudeArgs.push('--input-format', 'stream-json');
      }
    }
  }
  claudeArgs.push('--dangerously-skip-permissions');
  claudeArgs.push(prompt);

  const claudeProcess = spawn('claude', claudeArgs, {
    stdio: stdioConfig,
    shell: false,
  });
```

**Stream chaining** between agents:
[`v2/src/cli/simple-commands/stream-chain.js` L49-L156](https://github.com/ruvnet/claude-flow/blob/e82a79419c6a648a36de3529ab5d44a8a4d818a4/v2/src/cli/simple-commands/stream-chain.js#L49-L156)

```javascript
async function executeStep(prompt, previousContent, stepNum, totalSteps, flags) {
  let fullPrompt = prompt;
  if (previousContent) {
    fullPrompt = `Previous step output:\n${previousContent}\n\nNext step: ${prompt}`;
  }
  const args = ['-p'];
  args.push('--output-format', 'stream-json', '--verbose');
  args.push(fullPrompt);
  const claudeProcess = spawn('claude', args, {
    stdio: ['pipe', 'pipe', 'pipe'],
    env: process.env
  });
```

---

### 5. Commands & Skills (Declarative)

**Projects:** anthropic-cookbook (Anthropic), fastmcp (jlowin)

No subprocess management. Uses Claude Code's built-in extensibility:
`.claude/commands/` for slash commands, `.claude/skills/` for reusable skills,
`claude mcp add` for MCP server registration.

**anthropic-cookbook commands** (7 custom slash commands):
[`.claude/commands/notebook-review.md` L1-L10](https://github.com/anthropics/anthropic-cookbook/blob/7cb72a9c879e3b95f58d30a3d7483906e9ad548e/.claude/commands/notebook-review.md#L1-L10)

```yaml
---
allowed-tools: Bash(gh pr comment:*),Bash(gh pr diff:*),Bash(gh pr view:*),Bash(echo:*),Read,Glob,Grep,WebFetch
description: Comprehensive review of Jupyter notebooks and Python scripts
---
Review the specified Jupyter notebooks and Python scripts using the Notebook review skill.
```

**anthropic-cookbook skills** (cookbook-audit with validation scripts):
[`.claude/skills/cookbook-audit/SKILL.md` L1-L30](https://github.com/anthropics/anthropic-cookbook/blob/7cb72a9c879e3b95f58d30a3d7483906e9ad548e/.claude/skills/cookbook-audit/SKILL.md#L1-L30)

**fastmcp MCP registration** via `claude mcp add`:
[`src/fastmcp/cli/install/claude_code.py` L73-L150](https://github.com/jlowin/fastmcp/blob/806aa8c57985d5a0cdacfd9b22a2051e1a18a838/src/fastmcp/cli/install/claude_code.py#L73-L150)

```python
full_command = env_config.build_command(["fastmcp", "run", server_spec])
cmd_parts = [claude_cmd, "mcp", "add", name]
if env_vars:
    for key, value in env_vars.items():
        cmd_parts.extend(["-e", f"{key}={value}"])
cmd_parts.append("--")
cmd_parts.extend(full_command)
```

**fastmcp skills provider** (exposes ~/.claude/skills/ as MCP resources):
[`src/fastmcp/server/providers/skills/claude_provider.py` L11-L44](https://github.com/jlowin/fastmcp/blob/806aa8c57985d5a0cdacfd9b22a2051e1a18a838/src/fastmcp/server/providers/skills/claude_provider.py#L11-L44)

---

## SDK Approaches

### 6. Claude Agent SDK

**Projects:** claude-code-action (Anthropic), anthropic-cookbook (Anthropic)
**Package:** `@anthropic-ai/claude-agent-sdk` (TS) / `claude-agent-sdk` (Python)

Higher-level SDK that wraps Claude Code itself. The `query()` function returns an
async iterator yielding messages (system, assistant, tool calls). Manages sessions,
tools, and permissions internally. This is the official programmatic interface.

**claude-code-action** (TypeScript - query() async iterator):
[`src/claude.ts` L50-L120](https://github.com/anthropics/claude-code-action/blob/db388438c199401cf36c143bb877ba3c3e6a9be5/src/claude.ts#L50-L120)

```typescript
import { query } from '@anthropic-ai/claude-agent-sdk'

const messages = query({
  model: config.model,
  maxTurns: config.maxTurns,
  allowedTools: config.allowedTools,
  disallowedTools: config.disallowedTools,
  systemPrompt: config.systemPrompt,
  fallbackModel: config.fallbackModel,
  prompt: userPrompt,
  env: {
    ...process.env,
    ANTHROPIC_API_KEY: config.apiKey,
  },
});

for await (const message of messages) {
  if (message.type === 'system' && message.subtype === 'init') {
    sessionId = message.session_id;
  }
  // Process assistant messages, tool calls, results
}
```

**anthropic-cookbook** (Python - ClaudeSDKClient + ClaudeAgentOptions):
[`claude_agent_sdk/research_agent/agent.py` L1-L80](https://github.com/anthropics/anthropic-cookbook/blob/7cb72a9c879e3b95f58d30a3d7483906e9ad548e/claude_agent_sdk/research_agent/agent.py#L1-L80)

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

options = ClaudeAgentOptions(
    model="claude-opus-4-5",
    allowed_tools=["WebSearch", "Read"],
    continue_conversation=continue_conversation,
    system_prompt=RESEARCH_SYSTEM_PROMPT,
    max_buffer_size=10 * 1024 * 1024,
)
async with ClaudeSDKClient(options=options) as agent:
    await agent.query(prompt=prompt)
    async for msg in agent.receive_response():
        messages.append(msg)
```

**anthropic-cookbook** (Python - advanced agent with MCP, subagents, permissions):
[`claude_agent_sdk/chief_of_staff_agent/agent.py` L1-L100](https://github.com/anthropics/anthropic-cookbook/blob/7cb72a9c879e3b95f58d30a3d7483906e9ad548e/claude_agent_sdk/chief_of_staff_agent/agent.py#L1-L100)

```python
options = ClaudeAgentOptions(
    model="claude-opus-4-5",
    allowed_tools=["Task", "Read", "Write", "Edit", "Bash", "WebSearch"],
    permission_mode="acceptEdits",
    cwd=os.path.dirname(os.path.abspath(__file__)),
    settings=settings,
    setting_sources=["project", "local"],
)
```

**anthropic-cookbook** (Python - Docker-containerized MCP servers):
[`claude_agent_sdk/observability_agent/agent.py` L1-L100](https://github.com/anthropics/anthropic-cookbook/blob/7cb72a9c879e3b95f58d30a3d7483906e9ad548e/claude_agent_sdk/observability_agent/agent.py#L1-L100)

```python
mcp_servers = {
    "github": {
        "command": "docker",
        "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                 "ghcr.io/github/github-mcp-server"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": token},
    }
}
options = ClaudeAgentOptions(
    mcp_servers=servers,
    allowed_tools=["mcp__github"],
    disallowed_tools=["Bash", "Task", "WebSearch", "WebFetch"],
    permission_mode="acceptEdits",
)
```

---

### 7. Direct Anthropic SDK

**Projects:** gptme, cline, continue, fastmcp
**Package:** `anthropic` (Python) / `@anthropic-ai/sdk` (TypeScript)

Direct use of the official Anthropic client libraries. Projects call
`client.messages.create()` or `client.messages.stream()` directly.
Most control over API parameters but most code to write.

**gptme** (Python - streaming with all features):
[`gptme/llm/llm_anthropic.py` L444-L595](https://github.com/ErikBjare/gptme/blob/f564bb70722589b4ee6d5aab9a815939832f7e24/gptme/llm/llm_anthropic.py#L444-L595)

```python
with _anthropic.messages.stream(
    model=api_model,
    messages=messages_dicts,
    system=system_messages,
    temperature=TEMPERATURE if not model_meta.supports_reasoning else 1,
    top_p=TOP_P if not model_meta.supports_reasoning else NOT_GIVEN,
    max_tokens=max_tokens,
    tools=tools_dict if tools_dict else NOT_GIVEN,
    thinking=(
        {"type": "enabled", "budget_tokens": thinking_budget}
        if use_thinking
        else NOT_GIVEN
    ),
) as stream:
    # Handles TextDelta, ThinkingDelta, InputJSONDelta, CitationsDelta
```

**cline** (TypeScript - streaming with prompt caching and extended thinking):
[`src/core/api/providers/anthropic.ts` L66-L116](https://github.com/cline/cline/blob/844038084c6e559ee131c32e5d5da93dcff68a73/src/core/api/providers/anthropic.ts#L66-L116)

```typescript
stream = await client.messages.create({
  model: modelId,
  thinking: reasoningOn ? { type: "enabled", budget_tokens } : undefined,
  max_tokens: model.info.maxTokens || 8192,
  temperature: reasoningOn ? undefined : 0,
  system: [{
    text: systemPrompt, type: "text",
    cache_control: { type: "ephemeral" },
  }],
  messages: anthropicMessages,
  stream: true,
  tools: nativeToolsOn ? tools : undefined,
  tool_choice: nativeToolsOn && !reasoningOn ? { type: "any" } : undefined,
}, enable1mContextWindow ? {
  headers: { "anthropic-beta": "context-1m-2025-08-07" },
} : undefined);
```

**continue** (TypeScript - SSE streaming with direct HTTP fetch):
[`core/llm/llms/Anthropic.ts` L403-L454](https://github.com/continuedev/continue/blob/d585c3b8e8d49f7ef2df7a1ff7463caf1d1c9550/core/llm/llms/Anthropic.ts#L403-L454)

```typescript
const response = await this.fetch(new URL("messages", this.apiBase), {
  method: "POST",
  headers: getAnthropicHeaders(this.apiKey, shouldCachePrompt, this.apiBase),
  body: JSON.stringify({
    ...this.convertArgs(options),
    messages: msgs,
    system: shouldCacheSystemMessage ? [...] : systemMessage,
  }),
  signal,
});
yield* this.handleResponse(response, options.stream);
```

**fastmcp** (Python - MCP sampling protocol via AsyncAnthropic):
[`src/fastmcp/client/sampling/handlers/anthropic.py` L46-L121](https://github.com/jlowin/fastmcp/blob/806aa8c57985d5a0cdacfd9b22a2051e1a18a838/src/fastmcp/client/sampling/handlers/anthropic.py#L46-L121)

```python
kwargs = {
    "model": model,
    "messages": anthropic_messages,
    "max_tokens": params.maxTokens,
}
if params.systemPrompt is not None:
    kwargs["system"] = params.systemPrompt
if anthropic_tools is not None:
    kwargs["tools"] = anthropic_tools
if anthropic_tool_choice is not None:
    kwargs["tool_choice"] = anthropic_tool_choice
response = await self.client.messages.create(**kwargs)
```

---

### 8. LiteLLM Abstraction

**Projects:** aider, openhands, alphacodium
**Package:** `litellm`

Multi-provider abstraction layer. Claude is one of many supported providers.
Model name prefix determines routing (e.g., `anthropic/claude-sonnet-4-20250514`).
Anthropic-specific features passed via extra parameters.

**aider** (Python - LiteLLM completion with Claude-specific params):
[`aider/models.py` L950-L1002](https://github.com/paul-gauthier/aider/blob/4bf56b77145b0be593ed48c3c90cdecead217496/aider/models.py#L950-L1002)

```python
kwargs = dict(model=self.name, stream=stream)
if functions is not None:
    function = functions[0]
    kwargs["tools"] = [dict(type="function", function=function)]
    kwargs["tool_choice"] = {"type": "function", "function": {"name": function["name"]}}
res = litellm.completion(**kwargs)
```

**openhands** (Python - model-specific constraint handling):
[`openhands/llm/llm.py` L196-L210](https://github.com/All-Hands-AI/OpenHands/blob/0d13c57d9f9eaa69aebec2c12eef8806548c6ea2/openhands/llm/llm.py#L196-L210)

```python
# Disable extended thinking for Opus 4.1
if 'claude-opus-4-1' in self.config.model.lower():
    kwargs['thinking'] = {'type': 'disabled'}

# Opus 4.1, 4.5, and Sonnet 4 cannot accept both temperature and top_p
if ('claude-opus-4-1' in _model_lower or 'claude-opus-4-5' in _model_lower
    or 'claude-sonnet-4' in _model_lower):
    if 'temperature' in kwargs and 'top_p' in kwargs:
        kwargs.pop('top_p', None)
```

**alphacodium** (Python - minimal LiteLLM usage):
[`alpha_codium/llm/ai_handler.py`](https://github.com/Codium-ai/AlphaCodium/blob/eb7577dbe998ae7e55696264591ac3c5dde75638/alpha_codium/llm/ai_handler.py)

```python
response = await acompletion(
    model=model,
    deployment_id=deployment_id,
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ],
    temperature=temperature,
    frequency_penalty=frequency_penalty,
    force_timeout=get_settings().config.ai_timeout,
)
```

---

## Cross-Cutting Patterns

### 9. Prompt Caching

Six projects implement Anthropic's prompt caching with `cache_control: { type: "ephemeral" }`.
The key decision is where to place cache breakpoints.

**gptme** (3 breakpoints: system + last 2 user messages):
[`gptme/llm/utils.py` L197-L280](https://github.com/ErikBjare/gptme/blob/f564bb70722589b4ee6d5aab9a815939832f7e24/gptme/llm/utils.py#L197-L280)

```python
def _set_cache_control_on_last_part(content: list[dict]) -> list[dict]:
    """Add cache_control to the last non-empty content part."""
    content[i] = {**part, "cache_control": {"type": "ephemeral"}}
```

**aider** (3 breakpoints + unique cache warming):
[`aider/coders/chat_chunks.py` L28-L55](https://github.com/paul-gauthier/aider/blob/4bf56b77145b0be593ed48c3c90cdecead217496/aider/coders/chat_chunks.py#L28-L55)

```python
def add_cache_control_headers(self):
    if self.examples:
        self.add_cache_control(self.examples)
    else:
        self.add_cache_control(self.system)
    if self.repo:
        self.add_cache_control(self.repo)
    else:
        self.add_cache_control(self.readonly_files)
    self.add_cache_control(self.chat_files)

def add_cache_control(self, messages):
    content = messages[-1]["content"]
    if type(content) is str:
        content = dict(type="text", text=content)
    content["cache_control"] = {"type": "ephemeral"}
    messages[-1]["content"] = [content]
```

**continue** (4 strategies as configurable option):
[`packages/openai-adapters/src/apis/AnthropicCachingStrategies.ts` L1-L100](https://github.com/continuedev/continue/blob/d585c3b8e8d49f7ef2df7a1ff7463caf1d1c9550/packages/openai-adapters/src/apis/AnthropicCachingStrategies.ts#L1-L100)

```typescript
// System + tools strategy
const systemAndToolsStrategy: CachingStrategy = (body) => {
  if (result.system && Array.isArray(result.system)) {
    result.system = result.system.map((item) => ({
      ...item, cache_control: { type: "ephemeral" },
    }));
  }
  if (result.tools?.length > 0) {
    result.tools[result.tools.length - 1] = {
      ...lastTool, cache_control: { type: "ephemeral" },
    };
  }
  return result;
};
```

**openhands** (2 breakpoints: system + last user/tool):
[`openhands/memory/conversation_memory.py` L696-L709](https://github.com/All-Hands-AI/OpenHands/blob/0d13c57d9f9eaa69aebec2c12eef8806548c6ea2/openhands/memory/conversation_memory.py#L696-L709)

```python
def apply_prompt_caching(self, messages: list[Message]) -> None:
    if len(messages) > 0 and messages[0].role == 'system':
        messages[0].content[-1].cache_prompt = True
    for message in reversed(messages):
        if message.role in ('user', 'tool'):
            message.content[-1].cache_prompt = True
            break
```

**Caching strategy summary:**

| Project | Breakpoints | Unique Feature |
|---------|-------------|----------------|
| gptme | system + last 2 user msgs | Cache metrics tracking |
| cline | system + last 2 user msgs | 1M context window beta |
| aider | system + repo + chat | Cache warming (background keepalive) |
| continue | configurable (4 strategies) | Caches tools + large messages |
| openhands | system + last user/tool | Minimal, Anthropic-specific |

---

### 10. Extended Thinking

Six projects implement extended thinking. All enforce `temperature=1` when
thinking is enabled (Anthropic API requirement).

**gptme** (env-configurable reasoning budget):
[`gptme/llm/llm_anthropic.py` L156-L173](https://github.com/ErikBjare/gptme/blob/f564bb70722589b4ee6d5aab9a815939832f7e24/gptme/llm/llm_anthropic.py#L156-L173)

```python
def _should_use_thinking(model_meta: ModelMeta, tools: list[ToolSpec] | None) -> bool:
    env_reasoning = os.environ.get(ENV_REASONING)
    if env_reasoning and env_reasoning.lower() in ("1", "true", "yes"):
        return True
    elif env_reasoning and env_reasoning.lower() in ("0", "false", "no"):
        return False
    if not model_meta.supports_reasoning:
        return False
    return True
```

**aider** (human-readable budget format + OpenRouter handling):
[`aider/models.py` L803-L829](https://github.com/paul-gauthier/aider/blob/4bf56b77145b0be593ed48c3c90cdecead217496/aider/models.py#L803-L829)

```python
def set_thinking_tokens(self, value):
    num_tokens = self.parse_token_value(value)  # "8k", "10.5k", "0.5M"
    self.use_temperature = False  # Thinking incompatible with temperature
    if self.name.startswith("openrouter/"):
        # OpenRouter uses 'reasoning' instead of 'thinking'
        self.extra_params["extra_body"] = {"reasoning": {"max_tokens": num_tokens}}
    else:
        self.extra_params["thinking"] = {"type": "enabled", "budget_tokens": num_tokens}
```

**anthropic-cookbook** (canonical example):
[`extended_thinking/extended_thinking.ipynb`](https://github.com/anthropics/anthropic-cookbook/blob/7cb72a9c879e3b95f58d30a3d7483906e9ad548e/extended_thinking/extended_thinking.ipynb)

```python
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=4000,
    thinking={"type": "enabled", "budget_tokens": 2000},
    messages=[{"role": "user", "content": "Solve this puzzle: ..."}]
)
for block in response.content:
    if block.type == "thinking":
        print(f"THINKING: {block.thinking}")
    elif block.type == "text":
        print(f"ANSWER: {block.text}")
```

**Thinking configuration summary:**

| Project | Default Budget | Configurable Via | Provider Handling |
|---------|---------------|------------------|-------------------|
| gptme | 16,000 | GPTME_REASONING_BUDGET env | - |
| cline | 6,000 | UI setting | - |
| aider | 32,000 | --thinking-tokens flag | OpenRouter: "reasoning" param |
| continue | 2,048 | Config option | - |
| cookbook | 2,000 | Example code | - |
| openhands | Disabled for Opus 4.1 | Config | Drops top_p for Claude 4+ |

---

### 11. NDJSON Stream Parsing

Three CLI-spawning projects parse the `--output-format stream-json` NDJSON output.

**goose** (Rust - typed event matching):
[`crates/goose-llm/src/claude_code_provider.rs` L125-L180](https://github.com/block/goose/blob/b18120bec310365d96cafcc34ea63d8534e3ee57/crates/goose-llm/src/claude_code_provider.rs#L125-L180)

```rust
match event["type"].as_str() {
    Some("assistant") => { /* message content blocks */ }
    Some("result")    => { /* cost, duration, session_id */ break; }
    Some("error")     => { /* error handling */ }
    _ => {}
}
```

**claude-flow** (JavaScript - content extraction from stream):
[`v2/src/cli/simple-commands/stream-chain.js` L24-L44](https://github.com/ruvnet/claude-flow/blob/e82a79419c6a648a36de3529ab5d44a8a4d818a4/v2/src/cli/simple-commands/stream-chain.js#L24-L44)

```javascript
function extractContentFromStream(streamOutput) {
  const lines = streamOutput.split('\n').filter(line => line.trim());
  let content = '';
  for (const line of lines) {
    try {
      const json = JSON.parse(line);
      if (json.type === 'assistant' && json.message && json.message.content) {
        for (const item of json.message.content) {
          if (item.type === 'text' && item.text) {
            content += item.text;
          }
        }
      }
    } catch (e) { /* Skip non-JSON lines */ }
  }
  return content.trim();
}
```

**cline** (TypeScript - full event stream processing with thinking):
[`src/core/api/providers/anthropic.ts` L120-L240](https://github.com/cline/cline/blob/844038084c6e559ee131c32e5d5da93dcff68a73/src/core/api/providers/anthropic.ts#L120-L240)

```typescript
for await (const chunk of stream) {
  switch (chunk?.type) {
    case "message_start":
      yield { type: "usage", inputTokens, outputTokens, cacheWriteTokens, cacheReadTokens };
      break;
    case "content_block_start":
      switch (chunk.content_block.type) {
        case "thinking":
          yield { type: "reasoning", reasoning: chunk.content_block.thinking };
          break;
        case "redacted_thinking":
          yield { type: "reasoning", reasoning: "[Redacted]", redacted_data };
          break;
        case "tool_use":
          // Convert to internal tool format
          break;
        case "text":
          yield { type: "text", text: chunk.content_block.text };
          break;
      }
  }
}
```

---

## Quick Reference: Which Approach for Your Use Case?

| Use Case | Recommended Approach | Example Project |
|----------|---------------------|-----------------|
| GitHub Action / CI bot | Claude Agent SDK | [claude-code-action](https://github.com/anthropics/claude-code-action) |
| MCP tool wrapper | Per-request spawn (simple) | [claude-code-mcp](https://github.com/steipete/claude-code-mcp) |
| IDE extension | Per-request spawn (structured) + Direct SDK | [cline](https://github.com/cline/cline) |
| AI assistant with Claude backend | Persistent subprocess | [goose](https://github.com/block/goose) |
| Multi-agent orchestrator | Multi-instance spawn | [claude-flow](https://github.com/ruvnet/claude-flow) |
| AI coding tool (multi-provider) | LiteLLM | [aider](https://github.com/paul-gauthier/aider) |
| Feature-rich CLI tool | Direct Anthropic SDK | [gptme](https://github.com/ErikBjare/gptme) |
| Extend Claude Code itself | Commands & Skills | [anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook) |
| MCP sampling handler | Direct SDK (AsyncAnthropic) | [fastmcp](https://github.com/jlowin/fastmcp) |

---
*All permalinks verified against analyzed commits. Extracted from 12 project analyses.*
*Generated: 2026-02-07*
