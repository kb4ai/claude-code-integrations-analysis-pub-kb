# OpenHands (All-Hands-AI)

| Field | Value |
|-------|-------|
| Repository | [https://github.com/All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands) |
| Analyzed commit | `0d13c57d9f9e` ([full](https://github.com/All-Hands-AI/OpenHands/tree/0d13c57d9f9eaa69aebec2c12eef8806548c6ea2)) |
| Language | Python |
| Integration types | sdk |
| Status | comprehensive |


Default model: claude-opus-4-5-20251101. Uses LiteLLM with custom OpenHands proxy
(openhands/claude-* → litellm_proxy/claude-*). Extensive model-specific handling:
extended thinking disabled for Opus 4.1, temperature+top_p conflict resolution,
max output 64000 for Sonnet models. Runs production A/B tests (Claude 4 vs GPT-5).


---




## SDK Integration

Uses LiteLLM for Anthropic API access with Claude Opus 4.5 as default model.
Multi-provider support (direct, OpenRouter, Bedrock, OpenHands proxy).
Anthropic-specific handling: prompt caching with cache_control breakpoints,
extended thinking disabled for Opus 4.1, temperature+top_p conflict resolution.

**SDK(s) used:**


* `litellm` >=1.74.3,!=1.64.4,!=1.67.*

* `anthropic[vertex]` *



### prompt-caching

Anthropic prompt caching with ephemeral cache_control breakpoints


**Source:** [`openhands/memory/conversation_memory.py` L696-L709](https://github.com/All-Hands-AI/OpenHands/blob/0d13c57d9f9eaa69aebec2c12eef8806548c6ea2/openhands/memory/conversation_memory.py#L696-L709)
  • Function: `apply_prompt_caching`




```python
def apply_prompt_caching(self, messages: list[Message]) -> None:
    """Applies caching breakpoints to the messages.

    For new Anthropic API, we only need to mark the last user or tool message as cacheable.
    """
    if len(messages) > 0 and messages[0].role == 'system':
        messages[0].content[-1].cache_prompt = True
    # NOTE: this is only needed for anthropic
    for message in reversed(messages):
        if message.role in ('user', 'tool'):
            message.content[
                -1
            ].cache_prompt = True  # Last item inside the message content
            break```



> Two breakpoints: system message + last user/tool message. Anthropic-specific.



### model-constraints

Claude-specific API parameter constraint handling


**Source:** [`openhands/llm/llm.py` L196-L210](https://github.com/All-Hands-AI/OpenHands/blob/0d13c57d9f9eaa69aebec2c12eef8806548c6ea2/openhands/llm/llm.py#L196-L210)
  • Function: `__init__`
  • Class: `LLM`



```python
# Explicitly disable Anthropic extended thinking for Opus 4.1 to avoid
# requiring 'thinking' content blocks. See issue #10510.
if 'claude-opus-4-1' in self.config.model.lower():
    kwargs['thinking'] = {'type': 'disabled'}

# Anthropic constraint: Opus 4.1, Opus 4.5, and Sonnet 4 models cannot accept both temperature and top_p
# Prefer temperature (drop top_p) if both are specified.
_model_lower = self.config.model.lower()
# Apply to Opus 4.1, Opus 4.5, and Sonnet 4 models to avoid API errors
if (
    ('claude-opus-4-1' in _model_lower)
    or ('claude-opus-4-5' in _model_lower)
    or ('claude-sonnet-4' in _model_lower)
) and ('temperature' in kwargs and 'top_p' in kwargs):
    kwargs.pop('top_p', None)```



> Extended thinking disabled for Opus 4.1. top_p dropped when temperature set for Claude 4+ models



### openhands-proxy

OpenHands provider proxy rewrites to litellm_proxy


**Source:** [`openhands/llm/llm.py` L136-L139](https://github.com/All-Hands-AI/OpenHands/blob/0d13c57d9f9eaa69aebec2c12eef8806548c6ea2/openhands/llm/llm.py#L136-L139)





```python
if self.config.model.startswith('openhands/'):
    model_name = self.config.model.removeprefix('openhands/')
    self.config.model = f'litellm_proxy/{model_name}'
    self.config.base_url = _get_openhands_llm_base_url()```



> openhands/claude-* → litellm_proxy/claude-* with custom proxy URL



### model-versioning

User settings version to Claude model mapping


**Source:** [`enterprise/server/constants.py` L23-L29](https://github.com/All-Hands-AI/OpenHands/blob/0d13c57d9f9eaa69aebec2c12eef8806548c6ea2/enterprise/server/constants.py#L23-L29)





```python
PERSONAL_WORKSPACE_VERSION_TO_MODEL = {
    1: 'claude-3-5-sonnet-20241022',
    2: 'claude-3-7-sonnet-20250219',
    3: 'claude-sonnet-4-20250514',
    4: 'claude-sonnet-4-20250514',
    5: 'claude-opus-4-5-20251101',
}```



> Shows model evolution: 3.5 Sonnet → 3.7 Sonnet → Sonnet 4 → Opus 4.5





---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
