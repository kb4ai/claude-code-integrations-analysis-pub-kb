# gptme

| Field | Value |
|-------|-------|
| Repository | [https://github.com/ErikBjare/gptme](https://github.com/ErikBjare/gptme) |
| Analyzed commit | `f564bb707225` ([full](https://github.com/ErikBjare/gptme/tree/f564bb70722589b4ee6d5aab9a815939832f7e24)) |
| Language | Python |
| Integration types | sdk, mcp |
| Status | comprehensive |


Deep native Anthropic SDK integration (anthropic ^0.47). Does NOT invoke Claude CLI.
Features: streaming (messages.stream), extended thinking with configurable budget,
prompt caching (ephemeral cache_control on system + last 2 user messages),
vision (base64 images), native web search (web_search_20250305), tool use,
constrained output via Pydantic schemas, MCP server integration, ACP protocol support.
Model-aware: temperature=1 for reasoning models, top_p omitted.
Environment-driven config: GPTME_REASONING, GPTME_REASONING_BUDGET, GPTME_ANTHROPIC_WEB_SEARCH.


---




## SDK Integration

Deep native Anthropic SDK integration using anthropic ^0.47 Python package.
Direct client.messages.stream() for streaming responses. Advanced features:
extended thinking with configurable budget, prompt caching (ephemeral cache_control),
vision, native web search, tool use, constrained output via Pydantic schemas,
MCP server integration, and ACP protocol support. Does NOT invoke Claude CLI binary.

**SDK(s) used:**


* `anthropic` ^0.47



### streaming-messages

Streaming message API with full event handling for text, thinking, tools, citations


**Source:** [`gptme/llm/llm_anthropic.py` L444-L595](https://github.com/ErikBjare/gptme/blob/f564bb70722589b4ee6d5aab9a815939832f7e24/gptme/llm/llm_anthropic.py#L444-L595)
  • Function: `stream`




```python
with _anthropic.messages.stream(
    model=api_model,
    messages=messages_dicts,
    system=system_messages,
    temperature=TEMPERATURE if not model_meta.supports_reasoning else 1,
    top_p=TOP_P if not model_meta.supports_reasoning else NOT_GIVEN,
    max_tokens=max_tokens,
    tools=tools_dict if tools_dict else NOT_GIVEN,
    thinking=(
        {"type": "enabled", "budget_tokens": thinking_budget}
        if use_thinking
        else NOT_GIVEN
    ),
) as stream:```



> Handles TextDelta, ThinkingDelta, InputJSONDelta, CitationsDelta events. Temperature forced to 1 for reasoning models per Anthropic requirements.



### extended-thinking

Extended thinking with configurable budget via environment variables


**Source:** [`gptme/llm/llm_anthropic.py` L156-L173](https://github.com/ErikBjare/gptme/blob/f564bb70722589b4ee6d5aab9a815939832f7e24/gptme/llm/llm_anthropic.py#L156-L173)
  • Function: `_should_use_thinking`




```python
def _should_use_thinking(model_meta: ModelMeta, tools: list[ToolSpec] | None) -> bool:
    env_reasoning = os.environ.get(ENV_REASONING)
    if env_reasoning and env_reasoning.lower() in ("1", "true", "yes"):
        return True
    elif env_reasoning and env_reasoning.lower() in ("0", "false", "no"):
        return False
    if not model_meta.supports_reasoning:
        return False
    return True```



> GPTME_REASONING env var to enable/disable. GPTME_REASONING_BUDGET for budget (default 16000). Thinking content extracted and formatted as <think>...</think> tags.



### prompt-caching

Ephemeral cache control on system message and last 2 user messages


**Source:** [`gptme/llm/utils.py` L197-L280](https://github.com/ErikBjare/gptme/blob/f564bb70722589b4ee6d5aab9a815939832f7e24/gptme/llm/utils.py#L197-L280)
  • Function: `apply_cache_control`




```python
def _set_cache_control_on_last_part(content: list[dict]) -> list[dict]:
    """Add cache_control to the last non-empty content part."""
    content[i] = {**part, "cache_control": {"type": "ephemeral"}}```



> 3 cache breakpoints: system message + last 2 user messages. Tracks cache_read_tokens and cache_creation_tokens for cost monitoring.



### vision-support

Base64-encoded image support in message content blocks


**Source:** [`gptme/llm/llm_anthropic.py` L705-L737](https://github.com/ErikBjare/gptme/blob/f564bb70722589b4ee6d5aab9a815939832f7e24/gptme/llm/llm_anthropic.py#L705-L737)
  • Function: `_process_file`






> Supported formats: JPG, JPEG, PNG, GIF. Max 5MB. All Claude 3+ models have vision.



### web-search

Native Anthropic web search tool integration


**Source:** [`gptme/llm/llm_anthropic.py` L832-L845](https://github.com/ErikBjare/gptme/blob/f564bb70722589b4ee6d5aab9a815939832f7e24/gptme/llm/llm_anthropic.py#L832-L845)
  • Function: `_create_web_search_tool`




```python
def _create_web_search_tool(max_uses: int = 5) -> dict[str, Any]:
    return {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": max_uses,
    }```



> GPTME_ANTHROPIC_WEB_SEARCH env to enable. GPTME_ANTHROPIC_WEB_SEARCH_MAX_USES for limit.



### tool-use

Tool definitions converted from gptme ToolSpec to Anthropic format


**Source:** [`gptme/llm/llm_anthropic.py` L814-L829](https://github.com/ErikBjare/gptme/blob/f564bb70722589b4ee6d5aab9a815939832f7e24/gptme/llm/llm_anthropic.py#L814-L829)
  • Function: `_spec2tool`




```python
def _spec2tool(spec: ToolSpec) -> "anthropic.types.ToolParam":
    name = spec.name
    if spec.block_types:
        name = spec.block_types[0]
    return cast(
        "anthropic.types.ToolParam",
        {
            "name": name,
            "description": spec.get_instructions("tool"),
            "input_schema": parameters2dict(spec.parameters),
        },
    )```



> Full tool_use_id tracking. Tool results wrapped as tool_result content blocks.





---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
