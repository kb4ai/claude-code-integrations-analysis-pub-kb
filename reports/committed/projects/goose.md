# Goose (Block)

| Field | Value |
|-------|-------|
| Repository | [https://github.com/block/goose](https://github.com/block/goose) |
| Analyzed commit | `b18120bec310` ([full](https://github.com/block/goose/tree/b18120bec310365d96cafcc34ea63d8534e3ee57)) |
| Language | Rust |
| Integration types | cli, sdk |
| Status | comprehensive |


Goose has TWO distinct Claude integration paths:
1. ClaudeCodeProvider - spawns `claude` CLI as persistent subprocess with stream-json NDJSON protocol
2. AnthropicProvider - direct Anthropic API access via anthropic crate
The CLI integration is unique in the ecosystem for using persistent process + NDJSON bidirectional communication
rather than per-request spawning.


---


## CLI Integration

Goose spawns `claude` CLI as a persistent subprocess using bidirectional NDJSON (stream-json)
protocol. Unlike most integrations that spawn per-request, Goose keeps a long-running Claude process
and communicates via stdin/stdout JSON messages. Supports model selection, permission mode mapping,
and custom system prompts.


### claude-code-provider-spawn

Spawns Claude Code CLI as persistent subprocess with stream-json I/O


**Source:** [`crates/goose-llm/src/claude_code_provider.rs` L1-L80](https://github.com/block/goose/blob/b18120bec310365d96cafcc34ea63d8534e3ee57/crates/goose-llm/src/claude_code_provider.rs#L1-L80)
  • Function: `start_process`
  • Class: `ClaudeCodeProvider`



**Flags:**

| Flag | Purpose |
|------|---------|
| `--input-format` | Accept NDJSON messages on stdin for bidirectional communication |
| `--output-format` | Emit NDJSON messages on stdout for real-time streaming |
| `--verbose` | Required for stream-json output format |
| `--system-prompt` | Pass custom system prompt for agent behavior |
| `--model` | Model selection - only passed for 'sonnet' or 'opus' values |
| `--dangerously-skip-permissions` | Auto-approve all operations when GOOSE_MODE=auto |
| `--permission-mode` | Accept edits mode when GOOSE_MODE=smart-approve |




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

// Permission mode mapping from GOOSE_MODE
match goose_mode.as_str() {
    "auto" => { cmd.arg("--dangerously-skip-permissions"); }
    "smart-approve" => { cmd.arg("--permission-mode").arg("acceptEdits"); }
    _ => {}
}```



**Environment variables:**

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_COMMAND` | Override Claude Code binary path (default: 'claude') |
| `GOOSE_MODE` | Maps to CLI permission flags: auto→--dangerously-skip-permissions, smart-approve→--permission-mode acceptEdits |




> Unique persistent process pattern: Unlike claude-code-mcp which spawns per-request, Goose keeps a long-running Claude process and sends NDJSON messages via stdin. Default model is claude-sonnet-4-20250514.



### ndjson-input-protocol

Sends user messages as NDJSON objects to Claude stdin


**Source:** [`crates/goose-llm/src/claude_code_provider.rs` L85-L120](https://github.com/block/goose/blob/b18120bec310365d96cafcc34ea63d8534e3ee57/crates/goose-llm/src/claude_code_provider.rs#L85-L120)
  • Function: `send_message`
  • Class: `ClaudeCodeProvider`





```rust
// Each message is a single JSON line written to stdin
let msg = json!({
    "type": "user",
    "message": {
        "role": "user",
        "content": content_blocks
    }
});
stdin.write_all(serde_json::to_string(&msg)?.as_bytes())?;
stdin.write_all(b"\n")?;```





> Bidirectional NDJSON protocol - each line is a complete JSON object



### ndjson-response-parsing

Parses Claude stdout NDJSON for assistant/result/error events


**Source:** [`crates/goose-llm/src/claude_code_provider.rs` L125-L180](https://github.com/block/goose/blob/b18120bec310365d96cafcc34ea63d8534e3ee57/crates/goose-llm/src/claude_code_provider.rs#L125-L180)
  • Function: `read_response`
  • Class: `ClaudeCodeProvider`





```rust
// Parse each line from stdout as JSON event
for line in reader.lines() {
    let event: Value = serde_json::from_str(&line?)?;
    match event["type"].as_str() {
        Some("assistant") => {
            // Extract message content from assistant response
            let message = &event["message"];
            // Process content blocks (text, tool_use, etc.)
        }
        Some("result") => {
            // Final result with cost, duration, session_id
            break;
        }
        Some("error") => {
            // Handle error events
        }
        _ => {} // Skip unknown event types
    }
}```





> Three event types: assistant (content), result (final), error







---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
