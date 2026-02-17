# Claude Flow

| Field | Value |
|-------|-------|
| Repository | [https://github.com/ruvnet/claude-flow](https://github.com/ruvnet/claude-flow) |
| Analyzed commit | `e82a79419c6a` ([full](https://github.com/ruvnet/claude-flow/tree/e82a79419c6a648a36de3529ab5d44a8a4d818a4)) |
| Language | TypeScript |
| Integration types | cli, mcp |
| Status | comprehensive |


Most sophisticated CLI orchestration in the ecosystem. Spawns multiple Claude Code
instances with phase-based parallel execution (Promise.allSettled), stream chaining
via stdout→stdin piping, DAG-based dependency resolution with cycle detection,
NDJSON output parsing, hooks integration, and memory coordination.
Supports interactive, non-interactive, and headless (CI/Docker) modes.


---


## CLI Integration

Spawns multiple Claude Code CLI instances via child_process.spawn() for parallel multi-agent
orchestration. Uses stream-json for NDJSON output with stdout→stdin piping for stream chaining
between agents. Phase-based execution with DAG dependency resolution.


### automation-executor-spawn

Primary spawn method for per-task Claude Code instances


**Source:** [`v2/bin/automation-executor.js` L229-L275](https://github.com/ruvnet/claude-flow/blob/e82a79419c6a648a36de3529ab5d44a8a4d818a4/v2/bin/automation-executor.js#L229-L275)
  • Function: `spawnClaudeInstance`




**Flags:**

| Flag | Purpose |
|------|---------|
| `--print` | Headless mode for piped output |
| `--output-format` | Real-time streaming JSON output for parsing |
| `--verbose` | Required for stream-json output |
| `--input-format` | Accept chained input from previous agent (when stream chaining) |
| `--dangerously-skip-permissions` | Auto-approve all operations for automated workflows |




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
  });```



**Environment variables:**

| Variable | Purpose |
|----------|---------|
| `CLAUDE_FLOW_CONFIG` | Config file path (default: claude-flow.config.json) |
| `CLAUDE_FLOW_LOG_LEVEL` | Log level |
| `ANTHROPIC_API_KEY` | API authentication |




> shell:false for security. Multiple Claude instances tracked in Map<agentId, process>. Phase-based execution: Promise.allSettled() for parallel within phases, sequential between phases. Default timeout: 1 hour (2 hours for ML workflows).



### stream-chain-execution

Sequential stream chaining between Claude instances


**Source:** [`v2/bin/stream-chain.js` L49-L156](https://github.com/ruvnet/claude-flow/blob/e82a79419c6a648a36de3529ab5d44a8a4d818a4/v2/bin/stream-chain.js#L49-L156)
  • Function: `executeStep`






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
  });```





> Passes previous agent output as context prefix in prompt



### ndjson-content-extraction

Parses stream-json NDJSON output to extract text content


**Source:** [`v2/bin/stream-chain.js` L24-L44](https://github.com/ruvnet/claude-flow/blob/e82a79419c6a648a36de3529ab5d44a8a4d818a4/v2/bin/stream-chain.js#L24-L44)
  • Function: `extractContentFromStream`






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
}```





> Line-by-line JSON parsing; extracts text from assistant message content blocks







---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
