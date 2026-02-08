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


**Source:** [`src/claude-api.ts` L40-L95](https://github.com/steipete/claude-code-mcp/blob/24dfd389393cf35cc1390567bedda2d165756ef3/src/claude-api.ts#L40-L95)
  • Function: `executeClaudeCode`




**Flags:**

| Flag | Purpose |
|------|---------|
| `--dangerously-skip-permissions` | Auto-approve all operations (required for non-interactive MCP context) |
| `-p` | Pass prompt for non-interactive execution |




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
});```



**Environment variables:**

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CLI_NAME` | Override Claude Code binary name/path |
| `MCP_CLAUDE_DEBUG` | Enable debug logging |




> Stateless per-request spawning (contrast with Goose's persistent process). Binary resolution: CLAUDE_CLI_NAME env → ~/.claude/local/claude → PATH lookup. shell:false for security. 30-minute timeout.



### binary-resolution

Resolves Claude Code binary location


**Source:** [`src/claude-api.ts` L10-L35](https://github.com/steipete/claude-code-mcp/blob/24dfd389393cf35cc1390567bedda2d165756ef3/src/claude-api.ts#L10-L35)
  • Function: `findClaudeCommand`






```typescript
function findClaudeCommand(): string {
  // 1. Check environment variable
  if (process.env.CLAUDE_CLI_NAME) {
    return process.env.CLAUDE_CLI_NAME;
  }
  // 2. Check default install location
  const defaultPath = path.join(os.homedir(), '.claude', 'local', 'claude');
  if (fs.existsSync(defaultPath)) {
    return defaultPath;
  }
  // 3. Fall back to PATH
  return 'claude';
}```





> Three-stage binary resolution with environment override







---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
