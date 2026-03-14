# LLM Router — Algorithm: Route Selection, Fallback, and Streaming Adapter

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
THIS:            ALGORITHM_LLM_Router.md (you are here)
VALIDATION:      ./VALIDATION_LLM_Router.md
IMPLEMENTATION:  ./IMPLEMENTATION_LLM_Router.md
SYNC:            ./SYNC_LLM_Router.md

IMPL:            mind-mcp/runtime/llm_router/router.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The LLM Router processes every LLM request in MIND through four stages: **resolve** (pick a model and provider), **format** (transform messages to provider format), **stream** (call the provider and yield a unified stream), and **fallback** (on failure, advance to the next provider in the chain). The algorithm is stateless per request -- all state (tier, preferences, rate limits) is resolved at the start of each call.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1 Universal LLM access | B1, B6 | Route selection + prompt formatting make all providers interchangeable |
| O2 Fallback resilience | B2 | Fallback chain ensures no single provider failure reaches the user |
| O3 Cost optimization | B3, B4, B7, B8 | Tier-based model selection and cost tracking enforce sustainability |
| O4 BYOAI support | B5 | BYOAI resolution bypasses system key and rate limits |
| O5 Streaming uniformity | B1 | Streaming adapter pattern normalizes all provider responses |

---

## DATA STRUCTURES

### RoutingContext

```
RoutingContext:
    citizen_id: str               # Who is requesting
    tier: "free" | "paid"         # Determines model pool and rate limits
    provider_preference: str?     # Citizen's preferred provider (nullable)
    byoai_key: str?               # Citizen's own API key (nullable)
    model_override: str?          # Specific model requested (nullable)
    messages: list[Message]       # Universal message format
```

### Message

```
Message:
    role: "system" | "user" | "assistant"
    content: str
```

### StreamChunk

```
StreamChunk:
    text: str                     # Token(s) in this chunk (empty string for metadata-only chunks)
    finish_reason: str?           # null during stream, "stop" | "length" | "error" at end
    usage: Usage?                 # Only present in final chunk
    provider: str                 # Which provider generated this chunk
    model: str                    # Which model generated this chunk
```

### Usage

```
Usage:
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float    # Based on model pricing table
```

### FallbackChain

```
FallbackChain:
    providers: list[ProviderEntry]   # Ordered by priority for the given tier

ProviderEntry:
    provider_name: str               # e.g. "anthropic", "openai", "gemini"
    model: str                       # e.g. "claude-opus-4-20250514", "gpt-4o"
    timeout_ms: int                  # Max wait before declaring failure (default: 10000)
```

---

## ALGORITHM: route_request()

### Step 1: Resolve Routing Context

Determine which model and provider chain to use. This is pure configuration lookup with no network calls.

```
def resolve(ctx: RoutingContext) -> FallbackChain:
    if ctx.byoai_key:
        # BYOAI: single provider, citizen's key, no fallback
        provider = detect_provider_from_key(ctx.byoai_key)
        model = ctx.model_override or default_model(provider)
        return FallbackChain(providers=[ProviderEntry(provider, model)])

    if ctx.model_override:
        # Specific model: find its provider, put it first, then tier defaults
        provider = provider_for_model(ctx.model_override)
        chain = [ProviderEntry(provider, ctx.model_override)]
        chain += tier_fallback_chain(ctx.tier, exclude=provider)
        return FallbackChain(providers=chain)

    if ctx.provider_preference:
        # Preferred provider: put it first with tier-appropriate model
        model = best_model_for_tier(ctx.provider_preference, ctx.tier)
        chain = [ProviderEntry(ctx.provider_preference, model)]
        chain += tier_fallback_chain(ctx.tier, exclude=ctx.provider_preference)
        return FallbackChain(providers=chain)

    # Default: full tier fallback chain
    return tier_fallback_chain(ctx.tier)
```

Why this order: BYOAI is checked first because it overrides everything. Model override next because it narrows to a specific provider. Provider preference next. Default last.

### Step 2: Check Rate Limits

Before calling any provider, verify the citizen's tier has not exhausted its rate limits.

```
def check_rate_limit(citizen_id: str, tier: str) -> None:
    limits = rate_limits_for_tier(tier)  # {requests_per_min, tokens_per_min}
    current = get_current_usage(citizen_id, window=60s)

    if current.requests >= limits.requests_per_min:
        raise RateLimitError(retry_after=seconds_until_window_reset())

    # Token limit is checked post-response (we don't know output tokens yet)
    # But we check if input tokens alone would exceed the limit
    if current.tokens + estimated_input_tokens >= limits.tokens_per_min:
        raise RateLimitError(retry_after=seconds_until_window_reset())
```

Why pre-check: sending a request to a provider only to discard the response because rate limits were exceeded wastes money. Check first.

### Step 3: Execute Fallback Chain

Iterate through the provider chain. On success, stream and return. On failure, log and try next.

```
def execute_chain(chain: FallbackChain, messages: list[Message], api_key: str?) -> AsyncGenerator[StreamChunk]:
    errors = []

    for entry in chain.providers:
        adapter = get_adapter(entry.provider_name)
        key = api_key or system_key(entry.provider_name)

        try:
            formatted = adapter.format_messages(messages)
            stream = adapter.stream(formatted, model=entry.model, api_key=key, timeout=entry.timeout_ms)

            async for chunk in stream:
                yield normalize_chunk(chunk, provider=entry.provider_name, model=entry.model)

            # Stream completed successfully — emit cost event and return
            emit_cost_event(entry.provider_name, entry.model, stream.usage)
            return

        except ProviderError as e:
            errors.append((entry.provider_name, e))
            log_fallback_event(entry.provider_name, e)
            continue

    # All providers exhausted
    raise RoutingExhaustedError(attempted=errors)
```

Why no retry within a provider: retrying a rate-limited or erroring provider wastes the fallback time budget. Moving to the next provider is almost always faster.

### Step 4: Normalize Stream Chunks

Each provider adapter returns chunks in its own format. The normalize step ensures downstream consumers see a uniform StreamChunk.

```
def normalize_chunk(raw_chunk, provider: str, model: str) -> StreamChunk:
    return StreamChunk(
        text=raw_chunk.get_text(),          # Adapter extracts text from provider-specific field
        finish_reason=raw_chunk.get_finish_reason(),   # "stop", "length", or null
        usage=raw_chunk.get_usage() if raw_chunk.is_final else None,
        provider=provider,
        model=model
    )
```

---

## KEY DECISIONS

### D1: BYOAI Gets No Fallback

```
IF citizen provides a BYOAI key:
    Fallback chain has exactly ONE entry (the citizen's provider)
    On failure: raise error to citizen, do NOT fall back to system key
    WHY: The citizen chose to use their own key. Silently falling back to MIND's key
         would charge MIND for the citizen's usage. The citizen owns their failures.
ELSE:
    Full fallback chain based on tier
```

### D2: Free Tier Model Selection

```
IF tier == "free":
    Model pool: [gemini-flash, deepseek-chat, llama-3.1-70b, mistral-large]
    Selection: cheapest available, ordered by $/million tokens
    WHY: Free tier must be sustainable. These models are capable enough for
         general conversation at a fraction of premium model cost.
ELSE (tier == "paid"):
    Model pool: [claude-opus, gpt-4o, gemini-pro, claude-sonnet]
    Selection: provider preference first, then quality-ranked
    WHY: Paid users are paying for quality. Premium models justify the subscription.
```

### D3: OpenRouter as Catch-All

```
IF all direct provider adapters in the chain fail:
    Last entry in every fallback chain is OpenRouter
    OpenRouter routes to the best available model matching the tier's capability threshold
    WHY: OpenRouter aggregates 100+ models. Even if Anthropic, OpenAI, and Google are
         all down simultaneously, something on OpenRouter will be available.
EXCEPT:
    BYOAI requests never use OpenRouter (citizen chose a specific provider)
```

### D4: Mid-Stream Failure Is Terminal

```
IF a provider starts streaming but fails mid-stream:
    Emit StreamInterruptedError
    Do NOT attempt fallback (partial content already sent to user)
    WHY: The user has already seen partial text. Starting over with a different
         provider would produce a confusing experience (two partial responses).
         Better: show error, let user retry explicitly.
```

---

## DATA FLOW

```
RoutingContext (messages, citizen_id, tier, preferences)
    |
    v
[Resolve] --> FallbackChain (ordered provider + model entries)
    |
    v
[Rate Limit Check] --> pass or RateLimitError
    |
    v
[Execute Chain]
    |-- Provider A adapter.format_messages() --> provider-native format
    |-- Provider A adapter.stream() --> raw chunks
    |   |-- success? --> [Normalize] --> StreamChunk --> yield to caller
    |   |-- failure? --> log, try Provider B
    |       |-- Provider B success? --> normalize + yield
    |       |-- failure? --> try Provider C (or OpenRouter catch-all)
    |           |-- all failed? --> RoutingExhaustedError
    |
    v
[Cost Event] (provider, model, input_tokens, output_tokens, estimated_cost)
```

---

## COMPLEXITY

**Time:** O(P) worst case where P = number of providers in fallback chain (typically 3-4). Each provider attempt is bounded by timeout_ms. Worst case: sum of all timeouts (e.g., 4 providers * 10s = 40s, but the 2s fallback target means shorter timeouts for later entries).

**Space:** O(1) per request -- streaming means we don't buffer the full response. The RoutingContext and FallbackChain are small fixed structures.

**Bottlenecks:**
- Network latency to provider APIs dominates. Nothing the Router can optimize.
- Rate limit storage (per-citizen counters) needs to be fast. Redis or in-memory with sliding window.
- Provider SDK initialization should happen once at startup, not per-request.

---

## HELPER FUNCTIONS

### `tier_fallback_chain(tier, exclude=None)`

**Purpose:** Build the default fallback chain for a tier, optionally excluding a provider (already tried or used as primary).

**Logic:** Look up `providers.yaml` for the tier's ordered provider list. For each, resolve the default model. Filter out `exclude`. Append OpenRouter as final entry.

### `detect_provider_from_key(api_key)`

**Purpose:** Determine which provider a BYOAI key belongs to, based on key format.

**Logic:** Anthropic keys start with `sk-ant-`. OpenAI keys start with `sk-`. Google keys are long base64. Mistral keys start with specific prefix. If unrecognized, check against OpenRouter format. If still unknown, raise `UnrecognizedKeyError`.

### `best_model_for_tier(provider, tier)`

**Purpose:** Given a provider and tier, return the best model allowed for that tier.

**Logic:** Look up model registry. Filter by provider and tier. Return highest-ranked model.

### `emit_cost_event(provider, model, usage)`

**Purpose:** Record the cost of a completed request for tracking and billing.

**Logic:** Look up model pricing ($/million input tokens, $/million output tokens). Calculate cost. Emit structured event to cost tracking system.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `runtime/config/` | `load_model_registry()`, `load_provider_config()` | Model-to-provider mappings, tier configurations |
| `runtime/orchestrator/` | (called by orchestrator) | We receive messages, return AsyncGenerator[StreamChunk] |
| Provider SDKs | `anthropic.messages.stream()`, `openai.chat.completions.create(stream=True)`, etc. | Raw streamed responses |
| Rate limit store | `get_current_usage()`, `increment_usage()` | Current request/token counts per citizen |

---

## MARKERS

<!-- @mind:todo Design the provider adapter interface (abstract class or protocol) -->
<!-- @mind:todo Define timeout strategy: fixed per provider or adaptive based on recent latency? -->
<!-- @mind:proposition Adaptive fallback ordering: track provider reliability and reorder the chain dynamically. Not in v1 but worth designing for. -->
