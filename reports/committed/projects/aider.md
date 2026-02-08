# Aider

| Field | Value |
|-------|-------|
| Repository | [https://github.com/paul-gauthier/aider](https://github.com/paul-gauthier/aider) |
| Analyzed commit | `4bf56b77145b` ([full](https://github.com/paul-gauthier/aider/tree/4bf56b77145b0be593ed48c3c90cdecead217496)) |
| Language | Python |
| Integration types | sdk |
| Status | comprehensive |


Aider uses LiteLLM as abstraction layer for all LLM providers including Anthropic.
Does NOT use Claude Code CLI directly. Deep Anthropic-specific features: prompt caching
with cache warming (background keep-alive), extended thinking tokens, Bedrock/Vertex/OpenRouter
support. Default model is Claude Sonnet 4 when ANTHROPIC_API_KEY is set.


---




## SDK Integration

Uses LiteLLM as abstraction layer for Anthropic API access. Deep customization for Claude models
including prompt caching with cache warming (background thread), extended thinking tokens,
model-specific configuration via YAML settings, and multi-provider support (direct, Bedrock, Vertex, OpenRouter).

**SDK(s) used:**


* `litellm` >=1.0.0



### litellm-completion

Main completion call via litellm.completion() with Anthropic-specific parameters


**Source:** [`aider/models.py` L950-L1002](https://github.com/paul-gauthier/aider/blob/4bf56b77145b0be593ed48c3c90cdecead217496/aider/models.py#L950-L1002)
  • Function: `send_completion`
  • Class: `Model`



```python
kwargs = dict(model=self.name, stream=stream)
if functions is not None:
    function = functions[0]
    kwargs["tools"] = [dict(type="function", function=function)]
    kwargs["tool_choice"] = {"type": "function", "function": {"name": function["name"]}}
res = litellm.completion(**kwargs)
return hash_object, res```



> Uses litellm.completion() which routes to Anthropic SDK internally



### prompt-caching

Anthropic prompt caching with ephemeral cache control and background cache warming


**Source:** [`aider/coders/chat_chunks.py` L28-L55](https://github.com/paul-gauthier/aider/blob/4bf56b77145b0be593ed48c3c90cdecead217496/aider/coders/chat_chunks.py#L28-L55)
  • Function: `add_cache_control_headers`




```python
def add_cache_control_headers(self):
    if self.examples:
        self.add_cache_control(self.examples)
    else:
        self.add_cache_control(self.system)
    if self.repo:
        self.add_cache_control(self.repo)
    else:
        self.add_cache_control(self.readonly_files)
    self.add_cache_control(self.chat_files)

def add_cache_control(self, messages):
    if not messages:
        return
    content = messages[-1]["content"]
    if type(content) is str:
        content = dict(type="text", text=content)
    content["cache_control"] = {"type": "ephemeral"}
    messages[-1]["content"] = [content]```



> Three cache breakpoints: examples/system, repo/readonly_files, chat_files. Background cache warming thread sends periodic API calls (max_tokens=1) every ~5 minutes to keep cache alive. AIDER_CACHE_KEEPALIVE_DELAY env configurable.



### extended-thinking

Extended thinking configuration with budget tokens


**Source:** [`aider/models.py` L803-L829](https://github.com/paul-gauthier/aider/blob/4bf56b77145b0be593ed48c3c90cdecead217496/aider/models.py#L803-L829)
  • Function: `set_thinking_tokens`
  • Class: `Model`



```python
def set_thinking_tokens(self, value):
    if value is not None:
        num_tokens = self.parse_token_value(value)
        self.use_temperature = False  # Thinking incompatible with temperature
        if not self.extra_params:
            self.extra_params = {}
        if self.name.startswith("openrouter/"):
            # OpenRouter uses 'reasoning' instead of 'thinking'
            self.extra_params["extra_body"] = {"reasoning": {"max_tokens": num_tokens}}
        else:
            self.extra_params["thinking"] = {"type": "enabled", "budget_tokens": num_tokens}```



> Supports format: 8096, "8k", "10.5k", "0.5M", "10K". Temperature automatically disabled when thinking enabled. OpenRouter uses different parameter name ('reasoning' vs 'thinking').





---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
