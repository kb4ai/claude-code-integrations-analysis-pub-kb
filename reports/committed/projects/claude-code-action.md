# Claude Code Action (Anthropic)

| Field | Value |
|-------|-------|
| Repository | [https://github.com/anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) |
| Analyzed commit | `db388438c199` ([full](https://github.com/anthropics/claude-code-action/tree/db388438c199401cf36c143bb877ba3c3e6a9be5)) |
| Language | TypeScript |
| Integration types | sdk, cli, mcp, plugins |
| Status | comprehensive |


Canonical reference for Claude Agent SDK usage. Primary integration via @anthropic-ai/claude-agent-sdk
query() async iterator. Also uses CLI subprocess for plugin installation. Custom MCP servers
for GitHub comment/CI integration. Supports Anthropic API, Bedrock, Vertex AI, Foundry auth.
Two modes: tag mode (@claude mentions) and agent mode.


---




## SDK Integration

Uses @anthropic-ai/claude-agent-sdk v0.2.36 as primary integration. The query() async iterator
is the main entry point for Claude Code interactions. Supports model selection, tool restrictions,
system prompts, and session management. Plugin installation uses CLI subprocess.

**SDK(s) used:**


* `@anthropic-ai/claude-agent-sdk` 0.2.36



### query-async-iterator

Primary Claude Code interaction via query() async iterator


**Source:** [`src/claude.ts` L50-L120](https://github.com/anthropics/claude-code-action/blob/db388438c199401cf36c143bb877ba3c3e6a9be5/src/claude.ts#L50-L120)
  • Function: `runClaude`




```typescript
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
}```



> Async iterator pattern - yields messages in real-time. Session ID extracted from system.init message. Supports both tag mode (@claude) and full agent mode.



### plugin-installation-cli

Plugin installation via Claude CLI subprocess


**Source:** [`src/plugins.ts` L10-L40](https://github.com/anthropics/claude-code-action/blob/db388438c199401cf36c143bb877ba3c3e6a9be5/src/plugins.ts#L10-L40)
  • Function: `installPlugin`




```typescript
// Plugin installation uses CLI directly
execSync(`claude plugin install ${pluginName}`, {
  env: { ...process.env, ANTHROPIC_API_KEY: apiKey },
});```



> Hybrid approach: SDK for queries, CLI for plugin management



### session-id-extraction

Extracts session ID from system.init message


**Source:** [`src/claude.ts` L85-L100](https://github.com/anthropics/claude-code-action/blob/db388438c199401cf36c143bb877ba3c3e6a9be5/src/claude.ts#L85-L100)
  • Function: `runClaude`




```typescript
for await (const message of messages) {
  if (message.type === 'system' && message.subtype === 'init') {
    sessionId = message.session_id;
    // session_id used for conversation continuity
  }
}```



> Session ID enables resume capability across GitHub Action runs





---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
