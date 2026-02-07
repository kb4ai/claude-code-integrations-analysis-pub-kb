# SDK Integration Patterns

Cross-cutting analysis of how projects use the Anthropic SDK, Claude Agent SDK,
and LiteLLM abstraction layer for Claude integration.

## SDK Taxonomy

Three SDK layers are used across the 9 projects with SDK integration:

### 1. Direct Anthropic SDK

**Used by:** gptme, cline, continue, fastmcp

**Package:** `anthropic` (Python) / `@anthropic-ai/sdk` (TypeScript)

**Description:** Direct use of the official Anthropic client libraries.
Projects call `client.messages.create()` or `client.messages.stream()` directly,
managing all API parameters, streaming, and response parsing themselves.

**Typical pattern:**

```python
# Python (gptme)
with client.messages.stream(
    model=model,
    messages=messages,
    system=system_messages,
    thinking={"type": "enabled", "budget_tokens": budget},
) as stream:
    for event in stream:
        handle_event(event)
```

```typescript
// TypeScript (cline)
const stream = await client.messages.create({
    model: modelId,
    thinking: { type: "enabled", budget_tokens },
    max_tokens: 8192,
    system: [{ text: systemPrompt, cache_control: { type: "ephemeral" } }],
    messages,
    stream: true,
    tools,
});
```

### 2. Claude Agent SDK

**Used by:** claude-code-action, anthropic-cookbook

**Package:** `@anthropic-ai/claude-agent-sdk` (TypeScript) / `claude-agent-sdk` (Python)

**Description:** Higher-level SDK that wraps Claude Code itself. Uses `query()` async
iterator as the primary interface. Manages sessions, tools, and permissions internally.

**Typical pattern:**

```typescript
// TypeScript (claude-code-action)
const messages = query({
    model: config.model,
    maxTurns: 25,
    allowedTools: ["Read", "Write", "Bash"],
    systemPrompt: config.systemPrompt,
    prompt: userPrompt,
    env: { ANTHROPIC_API_KEY: apiKey },
});
for await (const message of messages) {
    // Process system, assistant, tool messages
}
```

```python
# Python (anthropic-cookbook)
options = ClaudeAgentOptions(
    model="claude-opus-4-5",
    allowed_tools=["Task", "Read", "Write"],
    permission_mode="acceptEdits",
    system_prompt=system_prompt,
)
async with ClaudeSDKClient(options=options) as agent:
    await agent.query(prompt=prompt)
    async for msg in agent.receive_response():
        messages.append(msg)
```

### 3. LiteLLM Abstraction

**Used by:** aider, openhands, alphacodium

**Package:** `litellm`

**Description:** Multi-provider abstraction layer. Claude is one of many supported
providers. Model name prefix determines routing (e.g., `anthropic/claude-sonnet-4-20250514`).
Anthropic-specific features (caching, thinking) passed via extra parameters.

**Typical pattern:**

```python
# aider
res = litellm.completion(
    model="anthropic/claude-sonnet-4-20250514",
    messages=messages,
    stream=True,
    extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
    thinking={"type": "enabled", "budget_tokens": 32000},
)
```

## Feature Usage Matrix

| Feature | gptme | cline | continue | aider | openhands | cookbook | claude-code-action | fastmcp | alphacodium |
|---------|:-----:|:-----:|:--------:|:-----:|:---------:|:-------:|:------------------:|:-------:|:-----------:|
| Streaming | Y | Y | Y | Y | Y | Y | Y | - | - |
| Extended thinking | Y | Y | Y | Y | - | Y | - | - | - |
| Prompt caching | Y | Y | Y | Y | Y | Y | - | - | - |
| Tool use | Y | Y | Y | Y | Y | Y | Y | Y | - |
| Vision | Y | - | Y | - | Y | Y | - | - | - |
| Web search | Y | - | - | - | - | - | - | - | - |
| MCP integration | Y | - | - | - | - | Y | Y | Y | - |
| Session management | - | - | - | - | - | Y | Y | - | - |
| Agent SDK | - | - | - | - | - | Y | Y | - | - |

## Prompt Caching Strategies

Six projects implement prompt caching, each with different strategies:

### Cache Breakpoint Placement

| Project | Strategy | Breakpoints |
|---------|----------|-------------|
| gptme | 3 breakpoints | System message + last 2 user messages |
| cline | 3 breakpoints | System message + last 2 user messages |
| aider | 3 breakpoints | System/examples + repo/readonly + chat files |
| continue | 4 strategies | None / system only / system+tools / optimized |
| openhands | 2 breakpoints | System message + last user/tool message |
| anthropic-cookbook | Canonical examples | Various patterns demonstrated |

### Cache Warming (Unique to Aider)

Aider is the only project that implements cache warming: a background thread sends
periodic API calls (max_tokens=1) every ~5 minutes to keep cached prompts alive.

```python
# aider's cache warming pattern
def cache_warmup(self):
    """Background thread to keep cache alive."""
    while self.cache_warming_enabled:
        litellm.completion(model=self.model, messages=self.cached_messages,
                          max_tokens=1, stream=False)
        time.sleep(AIDER_CACHE_KEEPALIVE_DELAY)
```

### Caching Strategy Selection (Unique to Continue)

Continue is the only project that offers multiple caching strategies as a configurable
option, from no caching to an optimized strategy that also caches large messages
(>500 tokens).

## Extended Thinking Patterns

Six projects implement extended thinking:

### Temperature Constraint

All projects that use extended thinking enforce `temperature=1` (or omit temperature)
when thinking is enabled, per Anthropic API requirements:

* **gptme:** `temperature=1 if model_meta.supports_reasoning else TEMPERATURE`
* **cline:** `temperature: reasoningOn ? undefined : 0`
* **aider:** `self.use_temperature = False` when thinking enabled
* **openhands:** Disables thinking entirely for Opus 4.1

### Budget Token Configuration

| Project | Default Budget | Configurable | Max |
|---------|---------------|:------------:|-----|
| gptme | 16,000 | GPTME_REASONING_BUDGET env | - |
| cline | 6,000 | UI setting | 6,000 |
| aider | 32,000 | --thinking-tokens flag | "10.5k", "0.5M" format |
| continue | 2,048 | config option | - |
| cookbook | 2,000 | Example code | - |

### Provider-Specific Handling

Aider handles the OpenRouter difference where extended thinking uses a different
parameter name:

```python
if self.name.startswith("openrouter/"):
    self.extra_params["extra_body"] = {"reasoning": {"max_tokens": num_tokens}}
else:
    self.extra_params["thinking"] = {"type": "enabled", "budget_tokens": num_tokens}
```

## Multi-Provider Support

Projects that support Claude through multiple cloud providers:

| Project | Direct | Bedrock | Vertex | Azure | OpenRouter | Custom Proxy |
|---------|:------:|:-------:|:------:|:-----:|:----------:|:------------:|
| aider | Y | Y | Y | - | Y | - |
| continue | Y | Y | - | Y | - | - |
| openhands | Y | Y | - | - | Y | Y |
| claude-code-action | Y | Y | Y | - | - | Y |
| cline | Y | - | Y | - | - | - |

### Azure Detection (Unique to Continue)

Continue includes Azure-hosted Anthropic endpoint detection:

```typescript
function isAzureAnthropicEndpoint(apiBase?: string): boolean {
    return hostname.endsWith(".services.ai.azure.com") ||
           hostname.endsWith(".cognitiveservices.azure.com");
}
// Uses "api-key" header for Azure, "x-api-key" for Anthropic
```

## Error Handling Patterns

### Model-Specific Workarounds

* **openhands:** Disables extended thinking for Opus 4.1; drops `top_p` when
  `temperature` is set for Claude 4+ models
* **aider:** Temperature auto-disabled when thinking enabled
* **gptme:** Forces temperature=1 for reasoning models, NOT_GIVEN for top_p
* **cline:** Removes ANTHROPIC_API_KEY from env to let Claude Code handle auth

### Streaming Event Types

Projects handle these Anthropic streaming event types:

* `message_start` - Usage tracking (cache reads/writes)
* `content_block_start` - Text, thinking, redacted_thinking, tool_use
* `content_block_delta` - TextDelta, ThinkingDelta, InputJSONDelta
* `content_block_stop` - Block completion
* `message_delta` - Stop reason, final usage

---
*Extracted from 12 project analyses in projects/*
