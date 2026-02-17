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


**Source:** [`crates/goose/src/providers/claude_code.rs` L278-L298](https://github.com/block/goose/blob/b18120bec310365d96cafcc34ea63d8534e3ee57/crates/goose/src/providers/claude_code.rs#L278-L298)
  • Function: `execute_command`
  • Class: `ClaudeCodeProvider`



**Flags:**

| Flag | Purpose |
|------|---------|
| `--input-format` | Accept NDJSON messages on stdin for bidirectional communication |
| `--output-format` | Emit NDJSON messages on stdout for real-time streaming |
| `--verbose` | Required for stream-json output format |
| `--system-prompt` | Pass custom system prompt for agent behavior (filtered to remove extensions) |
| `--model` | Model selection - only passed for values in CLAUDE_CODE_KNOWN_MODELS ('sonnet', 'opus') |
| `--dangerously-skip-permissions` | Auto-approve all operations when GooseMode::Auto |
| `--permission-mode` | Accept edits mode when GooseMode::SmartApprove |




```rust
// In execute_command(), lines 278-298: lazy spawn via OnceCell
let mut cmd = Command::new(&self.command);
// NO -p flag — persistent mode
configure_command_no_window(&mut cmd);
cmd.arg("--input-format")
    .arg("stream-json")
    .arg("--output-format")
    .arg("stream-json")
    .arg("--verbose")
    .arg("--system-prompt")
    .arg(&filtered_system);

// Only pass model parameter if it's in the known models list
if CLAUDE_CODE_KNOWN_MODELS.contains(&self.model.model_name.as_str()) {
    cmd.arg("--model").arg(&self.model.model_name);
}

// Add permission mode based on GOOSE_MODE setting
Self::apply_permission_flags(&mut cmd)?;

// apply_permission_flags (lines 122-147) maps GooseMode enum:
// GooseMode::Auto => --dangerously-skip-permissions
// GooseMode::SmartApprove => --permission-mode acceptEdits
// GooseMode::Approve => error (not supported)
// GooseMode::Chat => no flags```



**Environment variables:**

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_COMMAND` | Override Claude Code binary path (default: 'claude') - resolved via Config::get_claude_code_command() |
| `GOOSE_MODE` | Maps to CLI permission flags via GooseMode enum: Auto→--dangerously-skip-permissions, SmartApprove→--permission-mode acceptEdits |




> Unique persistent process pattern: Unlike claude-code-mcp which spawns per-request, Goose keeps a long-running Claude process via OnceCell (spawned exactly once on first call) and sends NDJSON messages via stdin. Default model is claude-sonnet-4-20250514. The apply_permission_flags helper (lines 122-147) handles GooseMode mapping.



### ndjson-input-protocol

Sends user messages as NDJSON objects to Claude stdin


**Source:** [`crates/goose/src/providers/claude_code.rs` L351-L362](https://github.com/block/goose/blob/b18120bec310365d96cafcc34ea63d8534e3ee57/crates/goose/src/providers/claude_code.rs#L351-L362)
  • Function: `execute_command`
  • Class: `ClaudeCodeProvider`





```rust
// build_stream_json_input (free function, lines 459-462) constructs the JSON:
fn build_stream_json_input(content_blocks: &[Value]) -> String {
    let msg = json!({"type":"user","message":{"role":"user","content":content_blocks}});
    serde_json::to_string(&msg).expect("serializing JSON content blocks cannot fail")
}

// In execute_command(), lines 351-362: write NDJSON line to stdin
let ndjson_line = build_stream_json_input(&new_blocks);
process
    .stdin
    .write_all(ndjson_line.as_bytes())
    .await
    .map_err(|e| {
        ProviderError::RequestFailed(format!("Failed to write to stdin: {}", e))
    })?;
process.stdin.write_all(b"\n").await.map_err(|e| {
    ProviderError::RequestFailed(format!("Failed to write newline to stdin: {}", e))
})?;```





> Bidirectional NDJSON protocol - each line is a complete JSON object. build_stream_json_input() is a free function (lines 459-462) that serializes the message. Content blocks are built by messages_to_content_blocks() (lines 73-120), which supports text, image (base64), tool_request, and tool_response message types.



### ndjson-response-parsing

Parses Claude stdout NDJSON for assistant/result/error events


**Source:** [`crates/goose/src/providers/claude_code.rs` L150-L253](https://github.com/block/goose/blob/b18120bec310365d96cafcc34ea63d8534e3ee57/crates/goose/src/providers/claude_code.rs#L150-L253)
  • Function: `parse_claude_response`
  • Class: `ClaudeCodeProvider`





```rust
fn parse_claude_response(
    &self,
    json_lines: &[String],
) -> Result<(Message, Usage), ProviderError> {
    let mut all_text_content = Vec::new();
    let mut usage = Usage::default();

    for line in json_lines {
        if let Ok(parsed) = serde_json::from_str::<Value>(line) {
            match parsed.get("type").and_then(|t| t.as_str()) {
                Some("assistant") => {
                    if let Some(message) = parsed.get("message") {
                        // Extract text content from this assistant message
                        if let Some(content) = message.get("content").and_then(|c| c.as_array())
                        {
                            for item in content {
                                if item.get("type").and_then(|t| t.as_str()) == Some("text") {
                                    if let Some(text) =
                                        item.get("text").and_then(|t| t.as_str())
                                    {
                                        all_text_content.push(text.to_string());
                                    }
                                }
                                // Skip tool_use - those are claude CLI's internal tools
                            }
                        }
                        // Extract usage information from message.usage
                    }
                }
                Some("result") => {
                    // Extract additional usage info from result if available
                }
                Some("error") => {
                    let error_msg = parsed
                        .get("error")
                        .and_then(|e| e.as_str())
                        .unwrap_or("Unknown error");
                    if error_msg.contains("context") && error_msg.contains("exceeded") {
                        return Err(ProviderError::ContextLengthExceeded(
                            error_msg.to_string(),
                        ));
                    }
                    return Err(ProviderError::RequestFailed(format!(
                        "Claude CLI error: {}",
                        error_msg
                    )));
                }
                Some("system") => {} // Ignore system init events
                _ => {}              // Ignore other event types
            }
        }
    }
    // Combine all text content into a single message with "\n\n" separator
    let combined_text = all_text_content.join("\n\n");
    // ...returns (Message, Usage)```





> Four event types handled: assistant (content), result (final usage), error, system (ignored). Lines are collected first by execute_command() (lines 364-400) which reads stdout until a "result" or "error" event, then passed to parse_claude_response for extraction. Error handling distinguishes context length exceeded from other errors.







---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
