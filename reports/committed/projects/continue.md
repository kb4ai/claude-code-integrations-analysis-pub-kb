# Continue.dev

| Field | Value |
|-------|-------|
| Repository | [https://github.com/continuedev/continue](https://github.com/continuedev/continue) |
| Analyzed commit | `d585c3b8e8d4` ([full](https://github.com/continuedev/continue/tree/d585c3b8e8d49f7ef2df7a1ff7463caf1d1c9550)) |
| Language | TypeScript |
| Integration types | sdk |
| Status | comprehensive |


Continue uses direct Anthropic SDK with a sophisticated adapter pattern:
1. Core LLM Layer (core/llm/llms/Anthropic.ts) - low-level SDK with SSE streaming
2. OpenAI Adapter (packages/openai-adapters/src/apis/Anthropic.ts) - format conversion
3. Vercel AI SDK fallback (@ai-sdk/anthropic)
4 caching strategies (no cache, system only, system+tools, optimized).
Azure-hosted Anthropic endpoint support.


---




## SDK Integration

Direct Anthropic SDK integration with SSE streaming, 4 caching strategies, extended thinking,
tool calling, vision support, and Azure-hosted endpoint detection. Also supports Vercel AI SDK
as fallback and includes Bedrock integration via @aws-sdk/client-bedrock-runtime.

**SDK(s) used:**


* `@anthropic-ai/sdk` >=0.67.0

* `@ai-sdk/anthropic` v2



### streaming-sse

SSE-based streaming with direct HTTP fetch to Anthropic API


**Source:** [`core/llm/llms/Anthropic.ts` L403-L454](https://github.com/continuedev/continue/blob/d585c3b8e8d49f7ef2df7a1ff7463caf1d1c9550/core/llm/llms/Anthropic.ts#L403-L454)
  • Function: `_streamChat`
  • Class: `Anthropic`



```typescript
const response = await this.fetch(new URL("messages", this.apiBase), {
  method: "POST",
  headers: getAnthropicHeaders(this.apiKey, shouldCachePrompt, this.apiBase),
  body: JSON.stringify({
    ...this.convertArgs(options),
    messages: msgs,
    system: shouldCacheSystemMessage ? [...] : systemMessage,
  }),
  signal,
});
yield* this.handleResponse(response, options.stream);```



> Uses direct HTTP fetch + SSE parsing rather than SDK client methods



### caching-strategies

4 caching strategies: no cache, system only, system+tools, optimized


**Source:** [`packages/openai-adapters/src/apis/AnthropicCachingStrategies.ts` L1-L100](https://github.com/continuedev/continue/blob/d585c3b8e8d49f7ef2df7a1ff7463caf1d1c9550/packages/openai-adapters/src/apis/AnthropicCachingStrategies.ts#L1-L100)





```typescript
// System + tools strategy
const systemAndToolsStrategy: CachingStrategy = (body) => {
  if (result.system && Array.isArray(result.system)) {
    result.system = result.system.map((item) => ({
      ...item, cache_control: { type: "ephemeral" },
    }));
  }
  if (result.tools?.length > 0) {
    result.tools[result.tools.length - 1] = {
      ...lastTool, cache_control: { type: "ephemeral" },
    };
  }
  return result;
};```



> Optimized strategy caches system, tools, and large messages (>500 tokens)



### extended-thinking

Extended thinking with budget tokens and signature handling


**Source:** [`core/llm/llms/Anthropic.ts` L70-L76](https://github.com/continuedev/continue/blob/d585c3b8e8d49f7ef2df7a1ff7463caf1d1c9550/core/llm/llms/Anthropic.ts#L70-L76)
  • Function: `convertArgs`
  • Class: `Anthropic`



```typescript
thinking: options.reasoning ? {
  type: "enabled" as const,
  budget_tokens: options.reasoningBudgetTokens ?? DEFAULT_REASONING_TOKENS,
} : undefined,```



> DEFAULT_REASONING_TOKENS = 2048. Handles thinking, redacted_thinking, and signature blocks



### azure-endpoint-detection

Detects Azure-hosted Anthropic endpoints and adjusts auth headers


**Source:** [`packages/openai-adapters/src/apis/AnthropicUtils.ts` L37-L94](https://github.com/continuedev/continue/blob/d585c3b8e8d49f7ef2df7a1ff7463caf1d1c9550/packages/openai-adapters/src/apis/AnthropicUtils.ts#L37-L94)
  • Function: `isAzureAnthropicEndpoint`




```typescript
export function isAzureAnthropicEndpoint(apiBase?: string): boolean {
  const hostname = url.hostname.toLowerCase();
  return hostname.endsWith(".services.ai.azure.com") ||
         hostname.endsWith(".cognitiveservices.azure.com");
}
// Uses "api-key" header for Azure, "x-api-key" for Anthropic```



> Azure detection for .services.ai.azure.com and .cognitiveservices.azure.com





---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
