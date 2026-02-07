# Claude Code Integrations Comparison

Generated: 2026-02-07 23:06

## Projects Overview

| Project | Repository | Status | Integration Types |
|---------|-----------|--------|-------------------|
| _template | https://github.com/org/repo | pending | - |
| aider | https://github.com/paul-gauthier/aider | comprehensive | sdk |
| alphacodium | https://github.com/Codium-ai/AlphaCodium | comprehensive | sdk |
| anthropic-cookbook | https://github.com/anthropics/anthropic-cookbook | comprehensive | sdk, cli, skills, mcp |
| claude-code-action | https://github.com/anthropics/claude-code-action | comprehensive | sdk, cli, mcp, plugins |
| claude-code-mcp | https://github.com/steipete/claude-code-mcp | comprehensive | cli, mcp |
| claude-flow | https://github.com/ruvnet/claude-flow | comprehensive | cli, mcp |
| cline | https://github.com/cline/cline | comprehensive | cli, sdk |
| continue | https://github.com/continuedev/continue | comprehensive | sdk |
| fastmcp | https://github.com/jlowin/fastmcp | comprehensive | cli, sdk, skills, mcp |
| goose | https://github.com/block/goose | comprehensive | cli, sdk |
| gptme | https://github.com/ErikBjare/gptme | comprehensive | sdk, mcp |
| openhands | https://github.com/All-Hands-AI/OpenHands | comprehensive | sdk |


## CLI Flags Usage

| Flag | _template | aider | alphacodium | anthropic-cookbook | claude-code-action | claude-code-mcp | claude-flow | cline | continue | fastmcp | goose | gptme | openhands | 
|------|:---:| :---:| :---:| :---:| :---:| :---:| :---:| :---:| :---:| :---:| :---:| :---:| :---:| 
| `--session` | - | - | - | - | - | - | - | - | - | - | - | - | - | 
| `--resume` | - | - | - | - | - | - | - | - | - | - | - | - | - | 
| `-c` | - | - | - | - | - | - | - | - | - | - | - | - | - | 
| `-p` | - | - | - | - | - | ✓ | ✓ | ✓ | - | - | - | - | - | 
| `--output-format` | - | - | - | - | - | - | ✓ | ✓ | - | - | ✓ | - | - | 
| `--dangerously-skip-permissions` | - | - | - | - | - | ✓ | ✓ | - | - | - | ✓ | - | - | 
| `--model` | - | - | - | - | - | - | - | ✓ | - | - | ✓ | - | - | 
| `--max-turns` | - | - | - | - | - | - | - | ✓ | - | - | - | - | - | 
| `--system-prompt` | - | - | - | - | - | - | - | ✓ | - | - | ✓ | - | - | 
| `--mcp-config` | - | - | - | - | - | - | - | - | - | - | - | - | - | 
| `--allowedTools` | - | - | - | - | - | - | - | - | - | - | - | - | - | 
| `--verbose` | - | - | - | - | - | - | ✓ | ✓ | - | - | ✓ | - | - | 


## SDK Patterns Usage

| Pattern | _template | aider | alphacodium | anthropic-cookbook | claude-code-action | claude-code-mcp | claude-flow | cline | continue | fastmcp | goose | gptme | openhands | 
|---------|:---:| :---:| :---:| :---:| :---:| :---:| :---:| :---:| :---:| :---:| :---:| :---:| :---:| 
| messages-create | - | - | ✓ | - | - | - | - | - | - | ✓ | - | - | - | 
| messages-stream | - | - | - | - | - | - | - | - | - | - | - | ✓ | - | 
| tool-use | - | - | - | - | - | - | - | - | - | - | - | ✓ | - | 
| vision | - | - | - | - | - | - | - | - | - | - | - | ✓ | - | 
| agent-create | - | - | - | ✓ | - | - | - | - | - | - | - | - | - | 
| agent-run | - | - | - | - | - | - | - | - | - | - | - | - | - | 
| conversation-management | - | - | - | - | - | - | - | - | - | - | - | - | - | 
| error-handling | - | - | - | - | - | - | - | - | - | - | - | - | - | 


## Integration Details


### _template


* **Repository**: https://github.com/org/repo
* **Analyzed commit**: `00000000`
* **Status**: pending







### aider


* **Repository**: https://github.com/paul-gauthier/aider
* **Analyzed commit**: `4bf56b77`
* **Status**: comprehensive





#### SDK Integration

Uses LiteLLM as abstraction layer for Anthropic API access. Deep customization for Claude models
including prompt caching with cache warming (background thread), extended thinking tokens,
model-specific configuration via YAML settings, and multi-provider support (direct, Bedrock, Vertex, OpenRouter).


**SDK patterns used**: 3



### alphacodium


* **Repository**: https://github.com/Codium-ai/AlphaCodium
* **Analyzed commit**: `eb7577db`
* **Status**: comprehensive





#### SDK Integration

Uses LiteLLM as abstraction layer for LLM provider access. No direct Anthropic SDK
import or Claude CLI invocation. Claude models supported through LiteLLM's model routing
(model name prefix determines provider). Default model is GPT-4; Claude usable by
configuring model="claude-3-opus" in configuration.toml. Features async completion,
model fallback chains, and rate limiting.


**SDK patterns used**: 2



### anthropic-cookbook


* **Repository**: https://github.com/anthropics/anthropic-cookbook
* **Analyzed commit**: `7cb72a9c`
* **Status**: comprehensive



#### CLI Integration

Uses Claude Code via .claude/commands/ (7 custom slash commands) and .claude/skills/
(cookbook-audit skill). GitHub Actions workflows invoke Claude Code for automated
PR review, model checking, link review, and notebook quality. The Claude Agent SDK
tutorials demonstrate ClaudeSDKClient which spawns Claude Code internally.


**Invocations found**: 2



#### SDK Integration

Anthropic's official cookbook with canonical examples of all Claude integration patterns.
Claude Agent SDK tutorials (ClaudeSDKClient + ClaudeAgentOptions), direct Anthropic SDK
usage (messages.create, messages.stream), extended thinking, prompt caching, tool use,
vision, MCP server integration, memory tool (beta), batch processing, and Claude Code
commands/skills. Serves as the authoritative reference for Claude Code integration patterns.


**SDK patterns used**: 5



### claude-code-action


* **Repository**: https://github.com/anthropics/claude-code-action
* **Analyzed commit**: `db388438`
* **Status**: comprehensive





#### SDK Integration

Uses @anthropic-ai/claude-agent-sdk v0.2.36 as primary integration. The query() async iterator
is the main entry point for Claude Code interactions. Supports model selection, tool restrictions,
system prompts, and session management. Plugin installation uses CLI subprocess.


**SDK patterns used**: 3



### claude-code-mcp


* **Repository**: https://github.com/steipete/claude-code-mcp
* **Analyzed commit**: `24dfd389`
* **Status**: comprehensive



#### CLI Integration

Spawns `claude` CLI per-request via Node.js child_process.spawn() with --dangerously-skip-permissions -p flags.
Stateless execution with 30-minute timeout. Single MCP tool interface.


**Invocations found**: 2





### claude-flow


* **Repository**: https://github.com/ruvnet/claude-flow
* **Analyzed commit**: `e82a7941`
* **Status**: comprehensive



#### CLI Integration

Spawns multiple Claude Code CLI instances via child_process.spawn() for parallel multi-agent
orchestration. Uses stream-json for NDJSON output with stdout→stdin piping for stream chaining
between agents. Phase-based execution with DAG dependency resolution.


**Invocations found**: 3





### cline


* **Repository**: https://github.com/cline/cline
* **Analyzed commit**: `84403808`
* **Status**: comprehensive



#### CLI Integration

Cline spawns Claude Code CLI via execa with stream-json output format.
Uses --max-turns 1 (Cline handles orchestration), --disallowedTools to restrict
Claude Code's built-in tools, and passes messages as JSON via stdin.


**Invocations found**: 1



#### SDK Integration

Direct Anthropic SDK integration via @anthropic-ai/sdk v0.37.0 with full streaming support,
prompt caching (ephemeral cache control on last 2 user messages), extended thinking with
budget tokens, native tool calling, and 1M context window support via beta headers.


**SDK patterns used**: 2



### continue


* **Repository**: https://github.com/continuedev/continue
* **Analyzed commit**: `d585c3b8`
* **Status**: comprehensive





#### SDK Integration

Direct Anthropic SDK integration with SSE streaming, 4 caching strategies, extended thinking,
tool calling, vision support, and Azure-hosted endpoint detection. Also supports Vercel AI SDK
as fallback and includes Bedrock integration via @aws-sdk/client-bedrock-runtime.


**SDK patterns used**: 4



### fastmcp


* **Repository**: https://github.com/jlowin/fastmcp
* **Analyzed commit**: `806aa8c5`
* **Status**: comprehensive





#### SDK Integration

AnthropicSamplingHandler implements MCP sampling protocol using AsyncAnthropic client.
Converts MCP messages/tools to Anthropic format. Also provides CLI integration via
`claude mcp add` command for registering MCP servers with Claude Code.


**SDK patterns used**: 3



### goose


* **Repository**: https://github.com/block/goose
* **Analyzed commit**: `b18120be`
* **Status**: comprehensive



#### CLI Integration

Goose spawns `claude` CLI as a persistent subprocess using bidirectional NDJSON (stream-json)
protocol. Unlike most integrations that spawn per-request, Goose keeps a long-running Claude process
and communicates via stdin/stdout JSON messages. Supports model selection, permission mode mapping,
and custom system prompts.


**Invocations found**: 3





### gptme


* **Repository**: https://github.com/ErikBjare/gptme
* **Analyzed commit**: `f564bb70`
* **Status**: comprehensive





#### SDK Integration

Deep native Anthropic SDK integration using anthropic ^0.47 Python package.
Direct client.messages.stream() for streaming responses. Advanced features:
extended thinking with configurable budget, prompt caching (ephemeral cache_control),
vision, native web search, tool use, constrained output via Pydantic schemas,
MCP server integration, and ACP protocol support. Does NOT invoke Claude CLI binary.


**SDK patterns used**: 6



### openhands


* **Repository**: https://github.com/All-Hands-AI/OpenHands
* **Analyzed commit**: `0d13c57d`
* **Status**: comprehensive





#### SDK Integration

Uses LiteLLM for Anthropic API access with Claude Opus 4.5 as default model.
Multi-provider support (direct, OpenRouter, Bedrock, OpenHands proxy).
Anthropic-specific handling: prompt caching with cache_control breakpoints,
extended thinking disabled for Opus 4.1, temperature+top_p conflict resolution.


**SDK patterns used**: 4




---
*Report generated by `scripts/regenerate_comparison_tables_and_reports.py`*