# LLM Router — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_LLM_Router.md
BEHAVIORS:       ./BEHAVIORS_LLM_Router.md
PATTERNS:        ./PATTERNS_LLM_Router.md
ALGORITHM:       ./ALGORITHM_LLM_Router.md
VALIDATION:      ./VALIDATION_LLM_Router.md
THIS:            IMPLEMENTATION_LLM_Router.md (you are here)
SYNC:            ./SYNC_LLM_Router.md

IMPL:            mind-mcp/runtime/llm_router/router.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mind-mcp/runtime/llm_router/
├── __init__.py                        # Exports: LLMRouter, StreamChunk, route_request
├── router.py                          # Core routing logic: resolve, execute chain, normalize
├── fallback.py                        # Fallback chain builder and executor
├── cost_tracker.py                    # Cost event emission and model pricing lookup
├── rate_limiter.py                    # Per-tier rate limiting with sliding window
├── types.py                           # Shared types: Message, StreamChunk, Usage, RoutingContext
├── provider_registry.py              # Provider adapter registration and lookup
└── providers/
    ├── __init__.py                    # Exports all provider adapters
    ├── base_llm_provider_interface.py # Abstract base: format_messages, stream, close
    ├── anthropic_claude_adapter.py    # Claude (Anthropic API)
    ├── openai_gpt_adapter.py         # GPT (OpenAI API)
    ├── google_gemini_adapter.py      # Gemini (Google AI API)
    ├── mistral_adapter.py            # Mistral (Mistral API)
    ├── deepseek_adapter.py           # DeepSeek (DeepSeek API)
    ├── llama_together_fireworks_adapter.py  # Llama via Together AI or Fireworks
    ├── grok_xai_adapter.py           # Grok (xAI API)
    └── openrouter_catch_all_adapter.py     # OpenRouter (100+ models, catch-all fallback)
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `router.py` | Core routing: resolves provider chain, executes, normalizes stream | `LLMRouter`, `route_request()`, `resolve()` | ~200 | DESIGNING |
| `fallback.py` | Builds and executes fallback chains per tier | `FallbackChainBuilder`, `execute_chain()` | ~120 | DESIGNING |
| `cost_tracker.py` | Calculates and emits cost events per request | `CostTracker`, `emit_cost_event()`, `lookup_model_pricing()` | ~100 | DESIGNING |
| `rate_limiter.py` | Sliding-window rate limiting per citizen per tier | `RateLimiter`, `check_rate_limit()`, `increment_usage()` | ~80 | DESIGNING |
| `types.py` | Data classes for all shared types | `Message`, `StreamChunk`, `Usage`, `RoutingContext`, `FallbackChain` | ~60 | DESIGNING |
| `provider_registry.py` | Maps provider names to adapter instances | `ProviderRegistry`, `get_adapter()`, `register()` | ~40 | DESIGNING |
| `base_llm_provider_interface.py` | Abstract interface all adapters implement | `LLMProvider` (ABC) | ~50 | DESIGNING |
| `anthropic_claude_adapter.py` | Anthropic-specific: system param, Messages API, streaming | `AnthropicAdapter` | ~100 | DESIGNING |
| `openai_gpt_adapter.py` | OpenAI-specific: chat completions, streaming, function calling | `OpenAIAdapter` | ~100 | DESIGNING |
| `google_gemini_adapter.py` | Google-specific: generateContent, model/user turns | `GeminiAdapter` | ~120 | DESIGNING |
| `mistral_adapter.py` | Mistral-specific: chat completions (OpenAI-compatible) | `MistralAdapter` | ~80 | DESIGNING |
| `deepseek_adapter.py` | DeepSeek-specific: OpenAI-compatible API | `DeepSeekAdapter` | ~80 | DESIGNING |
| `llama_together_fireworks_adapter.py` | Llama via Together/Fireworks: OpenAI-compatible with model routing | `LlamaAdapter` | ~90 | DESIGNING |
| `grok_xai_adapter.py` | xAI-specific: Grok API, OpenAI-compatible | `GrokAdapter` | ~80 | DESIGNING |
| `openrouter_catch_all_adapter.py` | OpenRouter: model passthrough, extra headers, 100+ models | `OpenRouterAdapter` | ~100 | DESIGNING |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Strategy + Chain of Responsibility

**Why this pattern:** Each provider is a Strategy (same interface, different implementation). The fallback mechanism is Chain of Responsibility (try handler, fail, pass to next). This combination gives us pluggable providers with resilient execution.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Strategy | `providers/*.py` : `LLMProvider` | Each provider implements the same interface; router selects at runtime |
| Chain of Responsibility | `fallback.py` : `execute_chain()` | On failure, request passes to next provider in chain |
| Factory | `provider_registry.py` : `ProviderRegistry` | Creates and caches provider adapter instances |
| Adapter | Each `providers/*.py` file | Translates provider-specific API to unified interface |
| AsyncGenerator | `router.py` : `route_request()` | Streaming as the only response mode |

### Anti-Patterns to Avoid

- **God Router**: Don't let `router.py` handle formatting, cost tracking, rate limiting, AND fallback logic. Each concern has its own file.
- **Provider Sniffing**: Never write `if provider == "anthropic"` in the router. If you need provider-specific behavior, it belongs in the adapter.
- **Synchronous Fallback**: Don't wait for a full timeout before trying fallback. Use async timeouts with immediate cancellation on the first error signal.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Router Core | Route resolution, chain execution, normalization | Provider-specific logic, cost calculation | `route_request(ctx) -> AsyncGenerator[StreamChunk]` |
| Provider Adapter | API formatting, SDK calls, stream translation | Route selection, fallback decisions | `LLMProvider.stream(messages, model, key) -> AsyncGenerator` |
| Cost Tracker | Pricing lookup, cost calculation, event emission | Billing, invoicing, payment | `emit_cost_event(provider, model, usage) -> CostEvent` |

---

## SCHEMA

### LLMProvider (Abstract Interface)

```yaml
LLMProvider:
  required:
    - name: str                    # Provider identifier (e.g., "anthropic")
    - format_messages: callable    # (list[Message]) -> provider-native format
    - stream: callable             # (formatted, model, api_key, timeout) -> AsyncGenerator
  optional:
    - close: callable              # Cleanup resources on shutdown
  constraints:
    - stream() MUST return AsyncGenerator yielding objects with get_text(), get_finish_reason(), get_usage()
    - format_messages() MUST handle system, user, assistant roles
    - All methods MUST be async
```

### ProviderConfig (from providers.yaml)

```yaml
ProviderConfig:
  required:
    - name: str                    # "anthropic", "openai", etc.
    - api_base: str                # Base URL for API calls
    - env_key: str                 # Environment variable for API key
    - default_model: dict          # {free: "model-name", paid: "model-name"}
  optional:
    - timeout_ms: int              # Default: 10000
    - max_retries: int             # SDK-level retries (default: 1)
    - custom_headers: dict         # Provider-specific headers (e.g., OpenRouter site info)
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `route_request()` | `router.py` | Orchestrator sending a message for LLM completion |
| `LLMRouter.__init__()` | `router.py` | Application startup (loads config, initializes adapters) |
| `ProviderRegistry.register()` | `provider_registry.py` | Startup: registers all provider adapters |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Request Flow: Message to Streamed Response

This is the primary flow. Every LLM interaction in MIND traverses this path. It transforms a universal message list into a provider-specific API call and normalizes the response back into a unified stream.

```yaml
flow:
  name: message_to_stream
  purpose: Route a citizen's message to the best available LLM and stream the response
  scope: RoutingContext in, AsyncGenerator[StreamChunk] out
  steps:
    - id: step_1_resolve
      description: Determine provider chain from tier, preferences, and BYOAI config
      file: runtime/llm_router/router.py
      function: resolve()
      input: RoutingContext
      output: FallbackChain
      trigger: route_request() called by Orchestrator
      side_effects: none
    - id: step_2_rate_check
      description: Verify citizen has not exceeded tier rate limits
      file: runtime/llm_router/rate_limiter.py
      function: check_rate_limit()
      input: citizen_id, tier
      output: pass or RateLimitError
      trigger: After resolve, before provider call
      side_effects: none (read-only check)
    - id: step_3_execute
      description: Iterate fallback chain, call provider adapters, stream response
      file: runtime/llm_router/fallback.py
      function: execute_chain()
      input: FallbackChain, messages, api_key
      output: AsyncGenerator[StreamChunk]
      trigger: After rate limit passes
      side_effects: Provider API calls, fallback logging
    - id: step_4_cost
      description: Emit cost event with token counts and estimated USD cost
      file: runtime/llm_router/cost_tracker.py
      function: emit_cost_event()
      input: provider, model, Usage
      output: CostEvent
      trigger: Stream completion (final chunk received)
      side_effects: Cost event emitted to tracking system
```

---

## LOGIC CHAINS

### LC1: Happy Path (Primary Provider Succeeds)

**Purpose:** The most common path -- primary provider responds successfully.

```
RoutingContext
  -> router.resolve()              # Pick provider chain
    -> rate_limiter.check()        # Verify quota
      -> adapter.format_messages() # Transform to provider format
        -> adapter.stream()        # Call provider API
          -> normalize_chunk()     # Unify chunk format
            -> yield StreamChunk   # To caller
              -> cost_tracker.emit() # Record cost
```

**Data transformation:**
- Input: `RoutingContext` -- universal messages + citizen metadata
- After resolve: `FallbackChain` -- ordered list of provider+model pairs
- After format: provider-native message format (varies per provider)
- After stream: raw provider chunks (provider-specific)
- After normalize: `StreamChunk` -- unified format
- Output: cost event emitted

### LC2: Fallback Path (Primary Provider Fails)

**Purpose:** Primary provider returns error; Router cascades to next.

```
RoutingContext
  -> resolve() -> FallbackChain[A, B, C, OpenRouter]
    -> rate_limiter.check() -> pass
      -> adapter_A.stream() -> ProviderError(429)
        -> log_fallback(A, 429)
          -> adapter_B.format_messages() -> adapter_B.stream()
            -> normalize_chunk() -> yield StreamChunk
              -> cost_tracker.emit(provider=B)
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
router.py
    └── imports -> types.py
    └── imports -> fallback.py
    └── imports -> rate_limiter.py
    └── imports -> provider_registry.py
    └── imports -> cost_tracker.py

fallback.py
    └── imports -> types.py
    └── imports -> provider_registry.py

provider_registry.py
    └── imports -> providers/base_llm_provider_interface.py

providers/*.py
    └── imports -> types.py
    └── imports -> providers/base_llm_provider_interface.py
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `anthropic` | Anthropic Messages API and streaming | `providers/anthropic_claude_adapter.py` |
| `openai` | OpenAI Chat Completions API and streaming | `providers/openai_gpt_adapter.py` |
| `google-genai` | Google Gemini GenerateContent API | `providers/google_gemini_adapter.py` |
| `mistralai` | Mistral Chat API | `providers/mistral_adapter.py` |
| `httpx` | Async HTTP for providers without official SDK (DeepSeek, xAI) | Multiple adapter files |
| `pydantic` | Data validation for types and config | `types.py`, config loaders |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Provider adapters | `ProviderRegistry` (singleton) | Global | Created at startup, destroyed at shutdown |
| Rate limit counters | `RateLimiter` (in-memory or Redis) | Per-citizen | Sliding window, auto-expires |
| Model pricing table | `CostTracker` (loaded from config) | Global | Loaded at startup, reloaded on config change |

### State Transitions

```
App Start ──[load config]──> Adapters Initialized ──[request]──> Routing ──[stream complete]──> Cost Emitted
                                                      |
                                                      v
                                                 [provider error] --> Fallback --> Routing (next provider)
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Load providers.yaml and models.yaml from config
2. For each configured provider: instantiate adapter, register in ProviderRegistry
3. Load model pricing table into CostTracker
4. Initialize RateLimiter (in-memory for single-instance, Redis for multi-instance)
5. Router ready to accept requests
```

### Main Request Cycle

```
1. Orchestrator calls route_request(ctx)
2. Router resolves FallbackChain from ctx
3. Rate limiter checks citizen quota
4. Execute chain: format -> stream -> normalize -> yield
5. On completion: emit cost event, increment rate limit counters
6. On failure: fallback to next provider or raise RoutingExhaustedError
```

### Shutdown

```
1. Close all provider adapter connections (SDK cleanup)
2. Flush pending cost events
3. Persist rate limit state if using in-memory store
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| `route_request()` | async | Each request runs as an async coroutine; multiple concurrent requests are supported |
| Provider adapters | async | All SDK calls use async clients; streaming is async generators |
| Rate limiter | thread-safe | Sliding window counters must be atomic (asyncio.Lock or Redis) |
| Cost tracker | async | Event emission is fire-and-forget (don't block the response stream) |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `providers` | `config/providers.yaml` | (required) | Provider endpoints, default models per tier, timeouts |
| `models` | `config/models.yaml` | (required) | Model registry: provider, tier, pricing, context window |
| `ANTHROPIC_API_KEY` | env | (required if using Anthropic) | Anthropic system API key |
| `OPENAI_API_KEY` | env | (required if using OpenAI) | OpenAI system API key |
| `GOOGLE_API_KEY` | env | (required if using Gemini) | Google AI system API key |
| `MISTRAL_API_KEY` | env | (required if using Mistral) | Mistral system API key |
| `DEEPSEEK_API_KEY` | env | (required if using DeepSeek) | DeepSeek system API key |
| `TOGETHER_API_KEY` | env | (required if using Llama) | Together AI or Fireworks API key |
| `XAI_API_KEY` | env | (required if using Grok) | xAI system API key |
| `OPENROUTER_API_KEY` | env | (required) | OpenRouter key (catch-all, always needed) |
| `RATE_LIMIT_BACKEND` | env | `memory` | `memory` for single-instance, `redis` for multi-instance |
| `RATE_LIMIT_FREE_RPM` | env | `20` | Requests per minute for free tier |
| `RATE_LIMIT_PAID_RPM` | env | `60` | Requests per minute for paid tier |

---

## MARKERS

<!-- @mind:todo Migrate existing Gemini direct calls in mind-mcp to use the Router -->
<!-- @mind:todo Create providers.yaml and models.yaml config schemas -->
<!-- @mind:escalation Need to decide: should we use LiteLLM as a dependency or build adapters from scratch? Custom adapters = more work but less dependency risk. LiteLLM = faster but we inherit their bugs and release cycle. -->
