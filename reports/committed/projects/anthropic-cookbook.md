# Anthropic Cookbook

| Field | Value |
|-------|-------|
| Repository | [https://github.com/anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook) |
| Analyzed commit | `7cb72a9c879e` ([full](https://github.com/anthropics/anthropic-cookbook/tree/7cb72a9c879e3b95f58d30a3d7483906e9ad548e)) |
| Language | Python |
| Integration types | sdk, cli, skills, mcp |
| Status | comprehensive |


Anthropic's official cookbook repository. Contains canonical examples for all integration patterns:
1. Claude Agent SDK: 3 progressive tutorials (research agent, chief-of-staff, observability)
   using ClaudeAgentOptions + ClaudeSDKClient with query()/receive_response() pattern
2. Claude Code: .claude/commands/ (7 custom commands), .claude/skills/ (cookbook-audit),
   GitHub Actions workflows for automated PR review and notebook quality
3. SDK patterns: messages.create, messages.stream, extended thinking, prompt caching,
   tool use, vision, batch processing, JSON mode, memory tool (beta)
4. MCP: Docker-containerized MCP servers (GitHub, git) with allowed/disallowed tools
5. Skills: cookbook-audit skill with validation scripts and scoring rubrics
Registry has 150+ cookbook entries covering RAG, classification, summarization, etc.


---


## CLI Integration

Uses Claude Code via .claude/commands/ (7 custom slash commands) and .claude/skills/
(cookbook-audit skill). GitHub Actions workflows invoke Claude Code for automated
PR review, model checking, link review, and notebook quality. The Claude Agent SDK
tutorials demonstrate ClaudeSDKClient which spawns Claude Code internally.


### claude-commands

7 custom Claude Code commands for repository operations


**Source:** [`.claude/commands/notebook-review.md` L1-L10](https://github.com/anthropics/anthropic-cookbook/blob/7cb72a9c879e3b95f58d30a3d7483906e9ad548e/.claude/commands/notebook-review.md#L1-L10)







```yaml
---
allowed-tools: Bash(gh pr comment:*),Bash(gh pr diff:*),Bash(gh pr view:*),Bash(echo:*),Read,Glob,Grep,WebFetch
description: Comprehensive review of Jupyter notebooks and Python scripts
---
Review the specified Jupyter notebooks and Python scripts using the Notebook review skill.```





> Commands: /notebook-review, /model-check, /link-review, /review-pr, /add-registry, /review-issue, /review-pr-ci. Each specifies allowed-tools in YAML frontmatter for tool restriction.



### claude-skills

Cookbook audit skill with validation scripts and scoring rubrics


**Source:** [`.claude/skills/cookbook-audit/SKILL.md` L1-L30](https://github.com/anthropics/anthropic-cookbook/blob/7cb72a9c879e3b95f58d30a3d7483906e9ad548e/.claude/skills/cookbook-audit/SKILL.md#L1-L30)











> Skill at .claude/skills/cookbook-audit/ with SKILL.md, style_guide.md, validate_notebook.py. Scores notebooks on 4 dimensions: Narrative Quality, Code Quality, Technical Accuracy, Actionability.






## SDK Integration

Anthropic's official cookbook with canonical examples of all Claude integration patterns.
Claude Agent SDK tutorials (ClaudeSDKClient + ClaudeAgentOptions), direct Anthropic SDK
usage (messages.create, messages.stream), extended thinking, prompt caching, tool use,
vision, MCP server integration, memory tool (beta), batch processing, and Claude Code
commands/skills. Serves as the authoritative reference for Claude Code integration patterns.

**SDK(s) used:**


* `claude-agent-sdk` >=0.0.20

* `anthropic` *



### agent-sdk-research

One-liner research agent using ClaudeSDKClient async iterator pattern


**Source:** [`claude_agent_sdk/research_agent/agent.py` L1-L80](https://github.com/anthropics/anthropic-cookbook/blob/7cb72a9c879e3b95f58d30a3d7483906e9ad548e/claude_agent_sdk/research_agent/agent.py#L1-L80)
  • Function: `send_query`




```python
options = ClaudeAgentOptions(
    model=model,
    allowed_tools=["WebSearch", "Read"],
    continue_conversation=continue_conversation,
    system_prompt=RESEARCH_SYSTEM_PROMPT,
    max_buffer_size=10 * 1024 * 1024,
)
async with ClaudeSDKClient(options=options) as agent:
    await agent.query(prompt=prompt)
    async for msg in agent.receive_response():
        messages.append(msg)```



> Canonical one-liner agent pattern. Default model: claude-opus-4-5.



### agent-sdk-chief-of-staff

Advanced agent with subagent delegation, permission modes, hooks, and custom commands


**Source:** [`claude_agent_sdk/chief_of_staff_agent/agent.py` L1-L100](https://github.com/anthropics/anthropic-cookbook/blob/7cb72a9c879e3b95f58d30a3d7483906e9ad548e/claude_agent_sdk/chief_of_staff_agent/agent.py#L1-L100)
  • Function: `send_query`




```python
options = ClaudeAgentOptions(
    model="claude-opus-4-5",
    allowed_tools=["Task", "Read", "Write", "Edit", "Bash", "WebSearch"],
    continue_conversation=continue_conversation,
    system_prompt=system_prompt,
    permission_mode=permission_mode,
    cwd=os.path.dirname(os.path.abspath(__file__)),
    settings=settings,
    setting_sources=["project", "local"],
)```



> Demonstrates: Task tool for subagent delegation, permission modes (default/plan/acceptEdits), .claude/agents/ directory for agent definitions, .claude/commands/ for slash commands, .claude/output-styles/ for output formatting, .claude/hooks/ for automation.



### agent-sdk-mcp-observability

Agent with Docker-containerized MCP servers for GitHub and git operations


**Source:** [`claude_agent_sdk/observability_agent/agent.py` L1-L100](https://github.com/anthropics/anthropic-cookbook/blob/7cb72a9c879e3b95f58d30a3d7483906e9ad548e/claude_agent_sdk/observability_agent/agent.py#L1-L100)
  • Function: `send_query`




```python
mcp_servers = {
    "github": {
        "command": "docker",
        "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                 "ghcr.io/github/github-mcp-server"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": token},
    }
}
options = ClaudeAgentOptions(
    mcp_servers=servers,
    allowed_tools=["mcp__github"],
    disallowed_tools=["Bash", "Task", "WebSearch", "WebFetch"],
    permission_mode="acceptEdits",
)```



> Pattern: mcp__{server_name} for allowed_tools. Disallowed tools prevent MCP bypass. Docker-containerized for isolation. GitHub + git MCP servers demonstrated.



### extended-thinking-example

Canonical extended thinking pattern with streaming and tool use


**Source:** [`extended_thinking/extended_thinking.ipynb` L1-L50](https://github.com/anthropics/anthropic-cookbook/blob/7cb72a9c879e3b95f58d30a3d7483906e9ad548e/extended_thinking/extended_thinking.ipynb#L1-L50)





```python
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=4000,
    thinking={"type": "enabled", "budget_tokens": 2000},
    messages=[{"role": "user", "content": "Solve this puzzle: ..."}]
)
for block in response.content:
    if block.type == "thinking":
        print(f"THINKING: {block.thinking}")
    elif block.type == "text":
        print(f"ANSWER: {block.text}")```



> Constraints: min budget 1024 tokens, temperature must be 1, incompatible with top_p/top_k. Response blocks include thinking (with signature), redacted_thinking, and text.



### memory-tool-beta

Beta memory tool with context management for persistent agent memory


**Source:** [`tool_use/memory_tool.py` L1-L50](https://github.com/anthropics/anthropic-cookbook/blob/7cb72a9c879e3b95f58d30a3d7483906e9ad548e/tool_use/memory_tool.py#L1-L50)





```python
response = client.beta.messages.create(
    model=MODEL,
    max_tokens=4096,
    system=system_prompt,
    messages=messages,
    tools=[{"type": "memory_20250818", "name": "memory"}],
    betas=["context-management-2025-06-27"],
    context_management=CONTEXT_MANAGEMENT,
)```



> Beta feature. Memory commands: view, create, str_replace, insert, delete, rename. Context management auto-clears old tool uses at token threshold.





---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
