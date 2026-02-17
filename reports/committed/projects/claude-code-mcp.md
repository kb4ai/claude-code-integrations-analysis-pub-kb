# Claude Code MCP (steipete)

| Field | Value |
|-------|-------|
| Repository | [https://github.com/steipete/claude-code-mcp](https://github.com/steipete/claude-code-mcp) |
| Analyzed commit | `24dfd389393c` ([full](https://github.com/steipete/claude-code-mcp/tree/24dfd389393cf35cc1390567bedda2d165756ef3)) |
| Language | TypeScript |
| Integration types | cli, mcp |
| Status | comprehensive |


Agent-in-agent pattern: Exposes a single MCP tool `claude_code` that spawns
Claude Code CLI per-request. Stateless - no session management.
Binary resolution chain: CLAUDE_CLI_NAME env → ~/.claude/local/claude → PATH.


---


## CLI Integration

Spawns `claude` CLI per-request via Node.js child_process.spawn() with --dangerously-skip-permissions -p flags.
Stateless execution with 30-minute timeout. Single MCP tool interface.


### mcp-tool-spawn

Spawns Claude Code CLI for each MCP tool invocation


**Source:** [`src/server.ts` L293-L300](https://github.com/steipete/claude-code-mcp/blob/24dfd389393cf35cc1390567bedda2d165756ef3/src/server.ts#L293-L300)
  • Function: `setupToolHandlers`
  • Class: `ClaudeCodeServer`



**Flags:**

| Flag | Purpose |
|------|---------|
| `--dangerously-skip-permissions` | Auto-approve all operations (required for non-interactive MCP context) |
| `-p` | Pass prompt for non-interactive execution |




```typescript
const claudeProcessArgs = ['--dangerously-skip-permissions', '-p', prompt];
debugLog(`[Debug] Invoking Claude CLI: ${this.claudeCliPath} ${claudeProcessArgs.join(' ')}`);

const { stdout, stderr } = await spawnAsync(
  this.claudeCliPath, // Run the Claude CLI directly
  claudeProcessArgs, // Pass the arguments
  { timeout: executionTimeoutMs, cwd: effectiveCwd }
);```



**Environment variables:**

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CLI_NAME` | Override Claude Code binary name/path |
| `MCP_CLAUDE_DEBUG` | Enable debug logging |




> Stateless per-request spawning (contrast with Goose's persistent process). Binary resolution: CLAUDE_CLI_NAME env → ~/.claude/local/claude → PATH lookup. shell:false for security. 30-minute timeout.



### binary-resolution

Resolves Claude Code binary location


**Source:** [`src/server.ts` L46-L83](https://github.com/steipete/claude-code-mcp/blob/24dfd389393cf35cc1390567bedda2d165756ef3/src/server.ts#L46-L83)
  • Function: `findClaudeCli`






```typescript
export function findClaudeCli(): string {
  debugLog('[Debug] Attempting to find Claude CLI...');

  // Check for custom CLI name from environment variable
  const customCliName = process.env.CLAUDE_CLI_NAME;
  if (customCliName) {
    debugLog(`[Debug] Using custom Claude CLI name from CLAUDE_CLI_NAME: ${customCliName}`);

    // If it's an absolute path, use it directly
    if (path.isAbsolute(customCliName)) {
      return customCliName;
    }

    // If it starts with ~ or ./, reject as relative paths are not allowed
    if (customCliName.startsWith('./') || customCliName.startsWith('../') || customCliName.includes('/')) {
      throw new Error(`Invalid CLAUDE_CLI_NAME: Relative paths are not allowed.`);
    }
  }

  const cliName = customCliName || 'claude';

  // Try local install path: ~/.claude/local/claude
  const userPath = join(homedir(), '.claude', 'local', 'claude');
  if (existsSync(userPath)) {
    return userPath;
  }

  // Fallback to CLI name (PATH lookup)
  return cliName;
}```





> Three-stage binary resolution with environment override







---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
