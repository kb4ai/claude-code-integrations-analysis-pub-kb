# Cline (VS Code Extension)

| Field | Value |
|-------|-------|
| Repository | [https://github.com/cline/cline](https://github.com/cline/cline) |
| Analyzed commit | `844038084c6e` ([full](https://github.com/cline/cline/tree/844038084c6e559ee131c32e5d5da93dcff68a73)) |
| Language | TypeScript |
| Integration types | cli, sdk |
| Status | comprehensive |


Cline has TWO distinct Claude integration paths:
1. AnthropicHandler - direct @anthropic-ai/sdk v0.37.0 with streaming, prompt caching, extended thinking
2. ClaudeCodeHandler - spawns Claude Code binary via execa with stream-json output
Both are first-class providers with UI configuration. Claude Code provider disables images
and prompt caching since CLI doesn't support those features directly.


---


## CLI Integration

Cline spawns Claude Code CLI via execa with stream-json output format.
Uses --max-turns 1 (Cline handles orchestration), --disallowedTools to restrict
Claude Code's built-in tools, and passes messages as JSON via stdin.


### claude-code-handler-spawn

Spawns Claude Code binary for each request via execa


**Source:** [`src/integrations/claude-code/run.ts` L189-L242](https://github.com/cline/cline/blob/844038084c6e559ee131c32e5d5da93dcff68a73/src/integrations/claude-code/run.ts#L189-L242)
  • Function: `runProcess`




**Flags:**

| Flag | Purpose |
|------|---------|
| `--system-prompt` | Pass system prompt directly (or --system-prompt-file for large prompts) |
| `--output-format` | Streaming JSON output for real-time processing |
| `--verbose` | Required for stream-json output |
| `--disallowedTools` | Disable Claude Code built-in tools (Task, Bash, Glob, etc.) - Cline handles tool execution |
| `--max-turns` | Limit to 1 turn - Cline manages multi-turn orchestration |
| `--model` | Model selection (claude-sonnet-4-5-20250929, claude-opus, etc.) |
| `-p` | Print/pipe mode - messages passed via stdin as JSON |




```typescript
const args = [
  shouldUseFile ? "--system-prompt-file" : "--system-prompt",
  systemPrompt,
  "--verbose",
  "--output-format",
  "stream-json",
  "--disallowedTools",
  claudeCodeTools,
  "--max-turns",
  "1",
  "--model",
  modelId,
  "-p",
];

const env: NodeJS.ProcessEnv = {
  ...process.env,
  CLAUDE_CODE_MAX_OUTPUT_TOKENS: process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS || "32000",
  CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC: "1",
  DISABLE_NON_ESSENTIAL_MODEL_CALLS: "1",
  MAX_THINKING_TOKENS: (thinkingBudgetTokens || 0).toString(),
};
delete env["ANTHROPIC_API_KEY"];

const claudeCodeProcess = execa(claudePath, args, {
  stdin: "pipe", stdout: "pipe", stderr: "pipe",
  env, cwd, maxBuffer: BUFFER_SIZE, timeout: CLAUDE_CODE_TIMEOUT,
});
claudeCodeProcess.stdin.write(JSON.stringify(messages));
claudeCodeProcess.stdin.end();```



**Environment variables:**

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Max output tokens (default 32000) |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Disable telemetry (set to 1) |
| `DISABLE_NON_ESSENTIAL_MODEL_CALLS` | Disable extra model calls (set to 1) |
| `MAX_THINKING_TOKENS` | Thinking budget tokens |
| `ANTHROPIC_API_KEY` | Explicitly REMOVED from env to let Claude Code handle auth |




> Unique pattern: --max-turns 1 + --disallowedTools to make Claude Code act as a single-turn LLM call while Cline handles orchestration. Messages passed as JSON via stdin. ANTHROPIC_API_KEY explicitly deleted from env. 10-minute timeout, 20MB buffer.






## SDK Integration

Direct Anthropic SDK integration via @anthropic-ai/sdk v0.37.0 with full streaming support,
prompt caching (ephemeral cache control on last 2 user messages), extended thinking with
budget tokens, native tool calling, and 1M context window support via beta headers.

**SDK(s) used:**


* `@anthropic-ai/sdk` ^0.37.0

* `@anthropic-ai/vertex-sdk` ^0.6.4



### streaming-messages-create

Primary streaming message creation with prompt caching and extended thinking


**Source:** [`src/core/api/providers/anthropic.ts` L66-L116](https://github.com/cline/cline/blob/844038084c6e559ee131c32e5d5da93dcff68a73/src/core/api/providers/anthropic.ts#L66-L116)
  • Function: `createMessage`
  • Class: `AnthropicHandler`



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
} : undefined);```



> Uses prompt caching (ephemeral) on system message and last 2 user messages. Extended thinking enabled when model supports it and budget > 0 (min 1024, max 6000). 1M context window via beta header. Native tool calling with streaming.



### stream-event-processing

Processes streaming events including thinking, text, and tool_use blocks


**Source:** [`src/core/api/providers/anthropic.ts` L120-L240](https://github.com/cline/cline/blob/844038084c6e559ee131c32e5d5da93dcff68a73/src/core/api/providers/anthropic.ts#L120-L240)
  • Function: `createMessage`
  • Class: `AnthropicHandler`



```typescript
for await (const chunk of stream) {
  switch (chunk?.type) {
    case "message_start":
      // Usage tracking: cache reads/writes
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
}```



> Handles thinking, redacted_thinking, text, and tool_use content blocks





---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
