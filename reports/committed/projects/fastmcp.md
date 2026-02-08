# FastMCP

| Field | Value |
|-------|-------|
| Repository | [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp) |
| Analyzed commit | `806aa8c57985` ([full](https://github.com/jlowin/fastmcp/tree/806aa8c57985d5a0cdacfd9b22a2051e1a18a838)) |
| Language | Python |
| Integration types | cli, sdk, skills, mcp |
| Status | comprehensive |


Three integration paths:
1. CLI: `fastmcp install claude-code` uses `claude mcp add` to register MCP servers
2. SDK: AnthropicSamplingHandler wraps AsyncAnthropic for MCP sampling protocol
3. Skills: ClaudeSkillsProvider exposes ~/.claude/skills/ via skill:// URI scheme
Binary resolution: ~/.claude/local/claude → /usr/local/bin/claude → ~/.npm-global/bin/claude


---




## SDK Integration

AnthropicSamplingHandler implements MCP sampling protocol using AsyncAnthropic client.
Converts MCP messages/tools to Anthropic format. Also provides CLI integration via
`claude mcp add` command for registering MCP servers with Claude Code.

**SDK(s) used:**


* `anthropic` >=0.40.0



### anthropic-sampling-handler

MCP sampling protocol implementation via AsyncAnthropic


**Source:** [`src/fastmcp/client/sampling/handlers/anthropic.py` L46-L121](https://github.com/jlowin/fastmcp/blob/806aa8c57985d5a0cdacfd9b22a2051e1a18a838/src/fastmcp/client/sampling/handlers/anthropic.py#L46-L121)
  • Function: `__call__`
  • Class: `AnthropicSamplingHandler`



```python
kwargs = {
    "model": model,
    "messages": anthropic_messages,
    "max_tokens": params.maxTokens,
}
if params.systemPrompt is not None:
    kwargs["system"] = params.systemPrompt
if params.temperature is not None:
    kwargs["temperature"] = params.temperature
if anthropic_tools is not None:
    kwargs["tools"] = anthropic_tools
if anthropic_tool_choice is not None:
    kwargs["tool_choice"] = anthropic_tool_choice
response = await self.client.messages.create(**kwargs)```



> Stop reason mapping: tool_use→toolUse, end_turn→endTurn, max_tokens→maxTokens. Model selection prioritizes models starting with "claude" from preferences.



### claude-code-mcp-add

Registers MCP servers with Claude Code via `claude mcp add` command


**Source:** [`src/fastmcp/cli/install/claude_code.py` L73-L150](https://github.com/jlowin/fastmcp/blob/806aa8c57985d5a0cdacfd9b22a2051e1a18a838/src/fastmcp/cli/install/claude_code.py#L73-L150)
  • Function: `install_claude_code`




```python
full_command = env_config.build_command(["fastmcp", "run", server_spec])
cmd_parts = [claude_cmd, "mcp", "add", name]
if env_vars:
    for key, value in env_vars.items():
        cmd_parts.extend(["-e", f"{key}={value}"])
cmd_parts.append("--")
cmd_parts.extend(full_command)```



> Uses `claude mcp add` command (not CLI flags like -p or --output-format). Binary resolution: ~/.claude/local/claude → /usr/local/bin/claude → ~/.npm-global/bin/claude



### claude-skills-provider

Exposes ~/.claude/skills/ as MCP resources via skill:// URI scheme


**Source:** [`src/fastmcp/server/providers/skills/claude_provider.py` L11-L44](https://github.com/jlowin/fastmcp/blob/806aa8c57985d5a0cdacfd9b22a2051e1a18a838/src/fastmcp/server/providers/skills/claude_provider.py#L11-L44)

  • Class: `ClaudeSkillsProvider`



```python
class ClaudeSkillsProvider(SkillsDirectoryProvider):
    # Hardcoded root: ~/.claude/skills/
    # Exposes skills as MCP resources via skill:// URI scheme
    # Supports progressive disclosure via frontmatter metadata
    pass```



> skill://{skill_name}/SKILL.md and skill://{skill_name}/_manifest URIs





---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
