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


**Source:** [`base-action/src/run-claude-sdk.ts` L136-L244](https://github.com/anthropics/claude-code-action/blob/db388438c199401cf36c143bb877ba3c3e6a9be5/base-action/src/run-claude-sdk.ts#L136-L244)
  • Function: `runClaudeWithSdk`




```typescript
for await (const message of query({ prompt, options: sdkOptions })) {
  messages.push(message);

  const sanitized = sanitizeSdkOutput(message, showFullOutput);
  if (sanitized) {
    console.log(sanitized);
  }

  if (message.type === "result") {
    resultMessage = message as SDKResultMessage;
  }
}```



> Async iterator pattern - yields SDKMessage objects in real-time. Options built via parseSdkOptions() in base-action/src/parse-sdk-options.ts. Session ID extracted post-loop via messages.find() on system.init message. Supports both tag mode (@claude) and full agent mode.



### plugin-installation-cli

Plugin installation via Claude CLI subprocess


**Source:** [`base-action/src/install-plugins.ts` L171-L182](https://github.com/anthropics/claude-code-action/blob/db388438c199401cf36c143bb877ba3c3e6a9be5/base-action/src/install-plugins.ts#L171-L182)
  • Function: `installPlugin`




```typescript
async function installPlugin(
  pluginName: string,
  claudeExecutable: string,
): Promise<void> {
  console.log(`Installing plugin: ${pluginName}`);

  return executeClaudeCommand(
    claudeExecutable,
    ["plugin", "install", pluginName],
    `Failed to install plugin '${pluginName}'`,
  );
}```



> Hybrid approach: SDK for queries, CLI spawn for plugin management. Uses child_process.spawn (not execSync) via executeClaudeCommand helper. Also supports marketplace add via addMarketplace() (lines 191-202). Exported installPlugins() (lines 212-243) orchestrates marketplace + plugin setup.



### session-id-extraction

Extracts session ID from system.init message


**Source:** [`base-action/src/run-claude-sdk.ts` L191-L198](https://github.com/anthropics/claude-code-action/blob/db388438c199401cf36c143bb877ba3c3e6a9be5/base-action/src/run-claude-sdk.ts#L191-L198)
  • Function: `runClaudeWithSdk`




```typescript
// Extract session_id from system.init message
const initMessage = messages.find(
  (m) => m.type === "system" && "subtype" in m && m.subtype === "init",
);
if (initMessage && "session_id" in initMessage && initMessage.session_id) {
  result.sessionId = initMessage.session_id as string;
  core.info(`Set session_id: ${result.sessionId}`);
}```



> Session ID extracted post-loop via Array.find() on collected messages. Exposed as GitHub Action output via core.setOutput in base-action/src/index.ts (line 52). Enables resume capability across GitHub Action runs.





---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
