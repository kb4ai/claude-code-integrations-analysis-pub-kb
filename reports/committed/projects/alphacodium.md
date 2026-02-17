# AlphaCodium

| Field | Value |
|-------|-------|
| Repository | [https://github.com/Codium-ai/AlphaCodium](https://github.com/Codium-ai/AlphaCodium) |
| Analyzed commit | `eb7577dbe998` ([full](https://github.com/Codium-ai/AlphaCodium/tree/eb7577dbe998ae7e55696264591ac3c5dde75638)) |
| Language | Python |
| Integration types | sdk |
| Status | comprehensive |


Minimal Claude integration: uses LiteLLM acompletion() as abstraction layer.
No direct Anthropic SDK import, no Claude CLI invocation.
Claude models supported via LiteLLM routing (model name prefix determines provider).
Default model is GPT-4; Claude usable by setting model="claude-3-opus" in config.
Features: async completion, model fallback chains, rate limiting, configurable timeout.
README mentions Claude 3 Opus benchmarking on AlphaCodium leaderboard.
Token encoding defaults to cl100k_base for non-GPT models.


---




## SDK Integration

Uses LiteLLM as abstraction layer for LLM provider access. No direct Anthropic SDK
import or Claude CLI invocation. Claude models supported through LiteLLM's model routing
(model name prefix determines provider). Default model is GPT-4; Claude usable by
configuring model="claude-3-opus" in configuration.toml. Features async completion,
model fallback chains, and rate limiting.

**SDK(s) used:**


* `litellm` *



### litellm-acompletion

Async chat completion via LiteLLM acompletion() with model-agnostic routing


**Source:** [`alpha_codium/llm/ai_handler.py` L70-L135](https://github.com/Codium-ai/AlphaCodium/blob/eb7577dbe998ae7e55696264591ac3c5dde75638/alpha_codium/llm/ai_handler.py#L70-L135)
  • Function: `chat_completion`
  • Class: `AiHandler`



```python
response = await acompletion(
    model=model,
    deployment_id=deployment_id,
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ],
    temperature=temperature,
    frequency_penalty=frequency_penalty,
    force_timeout=get_settings().config.ai_timeout,
)```



> Model-agnostic: Claude models work by setting model="claude-3-opus" etc. Configuration via Dynaconf TOML files. Default model is GPT-4.



### model-fallback

Automatic model fallback chain on failure


**Source:** [`alpha_codium/llm/ai_invoker.py` L8-L23](https://github.com/Codium-ai/AlphaCodium/blob/eb7577dbe998ae7e55696264591ac3c5dde75638/alpha_codium/llm/ai_invoker.py#L8-L23)
  • Function: `send_inference`




```python
async def send_inference(f: Callable):
    all_models = _get_all_models()
    all_deployments = _get_all_deployments(all_models)
    # try each (model, deployment_id) pair until one is successful, otherwise raise exception
    for i, (model, deployment_id) in enumerate(zip(all_models, all_deployments)):
        try:
            get_settings().set("openai.deployment_id", deployment_id)
            return await f(model)
        except Exception:
            logging.warning(
                f"Failed to generate prediction with {model}"
                f"{(' from deployment ' + deployment_id) if deployment_id else ''}: "
                f"{traceback.format_exc()}"
            )
            if i == len(all_models) - 1:  # If it's the last iteration
                raise  # Re-raise the last exception```



> Supports fallback_models config for cascading through multiple models. Could cascade from Claude to GPT or vice versa.





---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
