# Claude Code Integration Decision Guide

How to choose the right integration approach, based on patterns observed across 12 projects.

## Decision Tree

```
Do you need Claude Code's built-in tools (file editing, bash, etc.)?
├── YES → Do you need programmatic control from your application?
│   ├── YES → Use Claude Agent SDK (query() async iterator)
│   │         Examples: claude-code-action, anthropic-cookbook
│   └── NO → Use Claude Code Commands/Skills (.claude/commands/)
│            Examples: anthropic-cookbook, fastmcp
└── NO → Do you need Claude as an LLM?
    ├── YES → Use Anthropic SDK directly
    │   ├── Single provider? → Direct anthropic package
    │   │   Examples: gptme, cline, continue
    │   └── Multi-provider? → LiteLLM abstraction
    │       Examples: aider, openhands, alphacodium
    └── NO → Not a Claude integration
```

## Pattern Selection Guide

### When to Use CLI Subprocess Spawn

**Best for:** Projects that need Claude Code's agentic capabilities (file editing,
bash execution, web search) but want to control the orchestration externally.

**Choose persistent subprocess when:**

* High message volume (many interactions per session)
* Low latency requirements between messages
* Bidirectional communication needed
* Example: goose (AI assistant with ongoing conversation)

**Choose per-request spawn when:**

* Stateless execution model
* Simple request/response pattern
* Each request is independent
* Example: claude-code-mcp (MCP tool handler)

**Choose per-request with structured output when:**

* Need fine-grained control over Claude Code's behavior
* Want to restrict Claude Code's tools and manage orchestration externally
* Need structured event stream for UI updates
* Example: cline (VS Code extension managing tool execution)

**Choose multi-instance spawn when:**

* Parallel task execution across multiple agents
* Pipeline/DAG-based workflows
* Agent output feeds into next agent
* Example: claude-flow (multi-agent orchestrator)

### When to Use Claude Agent SDK

**Best for:** Projects that want Claude Code's full agentic capabilities with a clean
programmatic interface, without managing subprocess lifecycle directly.

**Choose when:**

* You want Claude Code's tools without subprocess management
* You need session persistence across interactions
* You want tool restriction (allowedTools/disallowedTools) via API
* You're building on top of Claude Code as a platform
* Examples: claude-code-action (GitHub Action), anthropic-cookbook agents

### When to Use Direct Anthropic SDK

**Best for:** Projects that need Claude as an LLM but handle tool execution,
context management, and orchestration themselves.

**Choose when:**

* You manage your own tool calling loop
* You need fine-grained control over API parameters
* You want streaming with custom event handling
* You need prompt caching optimization
* Examples: gptme, cline (SDK side), continue

### When to Use LiteLLM

**Best for:** Projects that support multiple LLM providers and want Claude as one option.

**Choose when:**

* Multi-provider support is a requirement
* Claude is one of several supported models
* You don't need Claude-specific features (or can add them via extra params)
* Examples: aider, openhands, alphacodium

## Feature Availability by Approach

| Feature | CLI Spawn | Agent SDK | Direct SDK | LiteLLM |
|---------|:---------:|:---------:|:----------:|:-------:|
| File editing tools | Y | Y | - | - |
| Bash execution | Y | Y | - | - |
| Tool restrictions | Y | Y | - | - |
| Custom system prompt | Y | Y | Y | Y |
| Streaming | Y (NDJSON) | Y | Y (SSE) | Y |
| Prompt caching | - | - | Y | Y |
| Extended thinking | - | - | Y | Y |
| Vision | - | - | Y | - |
| Web search | - | - | Y | - |
| Session management | Y | Y | - | - |
| Multi-provider | - | - | - | Y |
| MCP servers | Y | Y | Y | - |

## Prompt Caching Best Practices

Based on observed patterns across 6 projects:

1. **Place cache breakpoints strategically:**
   * System message (most stable, highest cache hit rate)
   * Tool definitions (stable across turns)
   * Repository/context files (change less frequently)
   * Recent messages (change every turn, lowest hit rate)

2. **Consider cache warming** for long-running sessions (aider pattern):
   Background thread sends minimal requests to keep cache alive

3. **Choose strategy based on context:**
   * High tool count? Cache tools (continue pattern)
   * Large system prompt? Cache system (all projects)
   * Long conversations? Cache last N user messages (gptme, cline)

4. **Monitor cache metrics:**
   Track cache_read_tokens and cache_creation_tokens (gptme pattern)

## Extended Thinking Best Practices

Based on observed patterns across 6 projects:

1. **Always disable temperature** when thinking is enabled (API requirement)
2. **Set reasonable defaults:** 2,000-16,000 tokens for most tasks
3. **Make budget configurable:** Via env vars (gptme) or UI (cline)
4. **Handle redacted_thinking blocks** in streaming responses
5. **Disable for certain models:** Opus 4.1 doesn't support thinking (openhands)

## Security Considerations

### Permission Handling

* **Never use** `--dangerously-skip-permissions` in user-facing tools unless the
  execution environment is fully sandboxed
* **Prefer** `--permission-mode acceptEdits` for semi-automated workflows
* **Best practice:** Let the calling application handle permission decisions
  (cline pattern: `--max-turns 1` + external orchestration)

### API Key Management

* **Remove ANTHROPIC_API_KEY** from child process env if Claude Code handles auth
  differently (cline pattern)
* **Use shell:false** when spawning to prevent injection (all projects)
* **Set timeouts** on subprocess execution (all projects)

### Binary Resolution

* Support environment variable override for binary path
* Check known install locations before PATH fallback
* Log which binary was found for debugging

---
*Synthesized from 12 project analyses in projects/*
