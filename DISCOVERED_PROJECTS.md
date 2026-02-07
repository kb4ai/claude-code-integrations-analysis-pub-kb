# Discovered Projects

Projects discovered through systematic research that integrate with Claude Code CLI, Claude Agent SDK, or Anthropic API.

## Tier 1: Direct Claude Code CLI Integration

Projects that invoke the `claude` binary via subprocess/spawn.

| Project | Repository | Integration Type | Language | Notes |
|---------|-----------|-----------------|----------|-------|
| **claude-code-action** | https://github.com/anthropics/claude-code-action | CLI (official) | TypeScript | Official GitHub Action, canonical CLI usage |
| **claude-code-mcp** | https://github.com/steipete/claude-code-mcp | CLI + MCP | TypeScript | Wraps Claude Code as MCP server (agent-in-agent) |
| **claude-flow** | https://github.com/ruvnet/claude-flow | CLI orchestration | TypeScript/Python | Multi-agent orchestration, stream chaining |
| **claude-code-sdk-python** | https://github.com/anthropics/claude-agent-sdk-python | CLI (official SDK) | Python | Official Python SDK with SubprocessTransport |
| **claude-code-sdk-typescript** | https://github.com/anthropics/claude-agent-sdk-typescript | CLI (official SDK) | TypeScript | Official TypeScript SDK |
| **claude-wrapper** | https://github.com/ChrisColeTech/claude-wrapper | CLI wrapper | Python | OpenAI-compatible API wrapper |
| **claude-stream-format** | https://github.com/jemmyw/claude-stream-format | CLI output parser | Rust | Formats streaming-json output |
| **claude-clean** | https://github.com/ariel-frischer/claude-clean | CLI output parser | Rust | Terminal parser for JSON logs |

## Tier 2: Anthropic SDK Integration (Coding Assistants)

Projects using the Anthropic Python/TypeScript SDK for Claude as an LLM provider.

| Project | Repository | SDK Used | Language | Stars |
|---------|-----------|---------|----------|-------|
| **cline** | https://github.com/cline/cline | @anthropic-ai/sdk | TypeScript | 57.7k |
| **aider** | https://github.com/paul-gauthier/aider | litellm (anthropic) | Python | ~30k |
| **continue** | https://github.com/continuedev/continue | anthropic (Python) | TypeScript/Python | ~20k |
| **openhands** | https://github.com/All-Hands-AI/OpenHands | litellm (anthropic) | Python | 67.6k |
| **goose** | https://github.com/block/goose | anthropic (Rust) | Rust/TypeScript | 30k |
| **gptme** | https://github.com/ErikBjare/gptme | anthropic (Python) | Python | ~5k |
| **fabric** | https://github.com/danielmiessler/Fabric | anthropic (Go) | Go | 38.9k |

## Tier 3: MCP Servers & Ecosystem Tools

| Project | Repository | Type | Language |
|---------|-----------|------|----------|
| **fastmcp** | https://github.com/jlowin/fastmcp | MCP framework | Python |
| **anthropic-cookbook** | https://github.com/anthropics/anthropic-cookbook | Examples/recipes | Python/TypeScript |
| **claude-code-mcp-enhanced** | https://github.com/grahama1970/claude-code-mcp-enhanced | MCP server | TypeScript |
| **github-mcp-server** | https://github.com/github/github-mcp-server | MCP server | Go |
| **claude-context** | https://github.com/zilliztech/claude-context | MCP code search | Python |

## Tier 4: Skills, Plugins & Configuration

| Project | Repository | Type |
|---------|-----------|------|
| **anthropics/skills** | https://github.com/anthropics/skills | Official skills repo |
| **awesome-claude-code** | https://github.com/hesreallyhim/awesome-claude-code | Curated collection |
| **claude-code-plugins-plus-skills** | https://github.com/jeremylongshore/claude-code-plugins-plus-skills | 270+ plugins |
| **everything-claude-code** | https://github.com/affaan-m/everything-claude-code | Config collection |
| **claude-hooks** | https://github.com/decider/claude-hooks | Hook implementations |

## Tier 5: Multi-Agent Orchestration

| Project | Repository | Language | Notes |
|---------|-----------|----------|-------|
| **claude-flow** | https://github.com/ruvnet/claude-flow | TS/Python | Stream chaining, 60+ agents |
| **oh-my-claudecode** | https://github.com/Yeachan-Heo/oh-my-claudecode | Python | 5 execution modes |
| **claude-code-agents-orchestra** | https://github.com/0ldh/claude-code-agents-orchestra | Python | 40+ specialized agents |
| **claude_code_agent_farm** | https://github.com/Dicklesworthstone/claude_code_agent_farm | Python | Parallel session execution |

## Tier 6: Community SDKs (Unofficial)

| Project | Repository | Language |
|---------|-----------|----------|
| **claude-sdk-rs** | https://github.com/bredmond1019/claude-sdk-rs | Rust |
| **claude-code-go** | https://github.com/lancekrogers/claude-code-go | Go |
| **claude-code-js** | https://github.com/s-soroosh/claude-code-js | TypeScript |
| **claude-code-sdk-ts** | https://github.com/instantlyeasy/claude-code-sdk-ts | TypeScript |

## Analysis Priority

For this repository, we prioritize in this order:

1. **Tier 1** projects first (direct CLI integration = most relevant)
2. **Tier 2** projects (SDK integration = common pattern)
3. **Tier 3-6** as time permits

## Currently Analyzed (Submodules Added)

* [x] goose
* [x] aider
* [x] cline
* [x] continue
* [x] openhands
* [x] claude-code-action
* [x] claude-code-mcp
* [x] claude-flow
* [x] fastmcp
* [x] anthropic-cookbook
* [x] gptme
* [x] alphacodium
