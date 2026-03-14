# LLM Router — Behaviors: Observable Effects of Multi-Provider Routing

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_LLM_Router.md
THIS:            BEHAVIORS_LLM_Router.md (you are here)
PATTERNS:        ./PATTERNS_LLM_Router.md
ALGORITHM:       ./ALGORITHM_LLM_Router.md
VALIDATION:      ./VALIDATION_LLM_Router.md
IMPLEMENTATION:  ./IMPLEMENTATION_LLM_Router.md
SYNC:            ./SYNC_LLM_Router.md

IMPL:            mind-mcp/runtime/llm_router/router.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Streaming Works Across All Providers

**Why:** The Orchestrator and all downstream consumers (Telegram bridge, Discord bridge, web app, API) expect a single stream interface. If streaming breaks for one provider, the entire user experience breaks for citizens routed to that provider. Streaming is not optional for any provider.

```
GIVEN:  A valid message payload and a selected provider (any of the 8 direct + OpenRouter)
WHEN:   The Router calls the provider adapter
THEN:   An async generator yields StreamChunk objects with consistent schema (text, finish_reason, usage)
AND:    The first chunk arrives within 3 seconds of request initiation (TTFB)
AND:    The stream terminates cleanly with a final chunk containing usage metadata
```

### B2: Fallback Triggers on Provider Error

**Why:** Provider outages, rate limits, and transient errors are routine. A single provider failure must not produce a user-visible error. The fallback chain absorbs failures silently from the user's perspective.

```
GIVEN:  A fallback chain of [provider_a, provider_b, provider_c]
WHEN:   provider_a returns an error (HTTP 429, 500, 503, timeout, auth failure)
THEN:   The Router immediately attempts provider_b with the same message payload
AND:    The total time from initial request to first streamed chunk is under 5 seconds
AND:    The fallback event is logged with provider, error type, and latency
```

### B3: Free Tier Routes to Cheaper Models

**Why:** MIND's free tier must be sustainable. Routing free citizens to GPT-4 or Claude Opus would make the free tier economically unviable. The Router enforces tier-based model selection so the Orchestrator never needs to think about cost.

```
GIVEN:  A citizen with tier = "free"
WHEN:   The Router selects a model
THEN:   The selected model is from the free-tier model list (e.g., Gemini Flash, DeepSeek, Llama 70B)
AND:    The model is the cheapest available that meets the minimum capability threshold
AND:    The cost per request is tracked and attributed to the free-tier pool
```

### B4: Paid Tier Routes to Premium Models

**Why:** Paid citizens are paying for quality. They should get the best available model unless they specify a preference. The tier system must create a tangible quality difference.

```
GIVEN:  A citizen with tier = "paid"
WHEN:   The Router selects a model
THEN:   The selected model is from the paid-tier model list (e.g., Claude Opus, GPT-4o, Gemini Pro)
AND:    If the citizen has a provider preference, that provider is tried first
AND:    The cost per request is tracked and attributed to the citizen's account
```

### B5: BYOAI Uses Customer Key

**Why:** Power users who bring their own API key should not be constrained by MIND's rate limits or model restrictions. Their key, their rules. This also removes MIND from the billing path for heavy usage.

```
GIVEN:  A citizen with a configured BYOAI key for a specific provider
WHEN:   The Router processes their request
THEN:   The provider adapter uses the citizen's API key instead of the system key
AND:    MIND's rate limits do not apply to this request
AND:    The cost is not tracked against MIND's pool (it's the citizen's direct cost)
AND:    If the citizen's key fails (invalid, exhausted), the Router does NOT fall back to the system key
```

### B6: Prompt Formatting Adapts Per Provider

**Why:** Each LLM provider has its own message format. Anthropic uses `system` as a separate parameter. OpenAI uses `system` as a role in messages. Gemini uses `model`/`user` turns. The Orchestrator should not know about any of this.

```
GIVEN:  A universal message array with roles [system, user, assistant]
WHEN:   The Router passes messages to a provider adapter
THEN:   The adapter transforms messages to the provider's native format
AND:    System instructions are placed where the provider expects them
AND:    Multi-turn conversation history preserves order and role attribution
```

### B7: Rate Limiting Enforced Per Tier

**Why:** Without rate limits, a single citizen (or bot) could exhaust the system's API quota, degrading service for everyone. Rate limits are per-tier because free and paid citizens have different allowances.

```
GIVEN:  A tier with configured limits (e.g., free: 20 req/min, 50k tokens/min)
WHEN:   A request would exceed the tier's rate limit
THEN:   The Router returns a rate-limit error with retry-after information
AND:    The request is NOT sent to any provider
AND:    The rate-limit event is logged with citizen_id, tier, and current usage
```

### B8: Cost Tracking Per Request

**Why:** MIND needs to know what each request costs to optimize routing, detect abuse, and bill paid users accurately. Cost tracking is not optional instrumentation; it is a core Router responsibility.

```
GIVEN:  A completed LLM request (successful or fallback)
WHEN:   The stream terminates
THEN:   The Router emits a cost event with: provider, model, input_tokens, output_tokens, estimated_cost_usd
AND:    The cost is attributed to the correct tier pool or citizen account
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O5 Streaming uniformity | Downstream consumers depend on a single stream format |
| B2 | O2 Fallback resilience | Provider failures must not become user-visible errors |
| B3 | O3 Cost optimization | Free tier sustainability depends on routing to cheap models |
| B4 | O3 Cost optimization | Paid tier value depends on routing to premium models |
| B5 | O4 BYOAI support | Power users escape MIND's constraints with their own key |
| B6 | O1 Universal LLM access | Provider differences hidden behind uniform interface |
| B7 | O3 Cost optimization | Rate limits prevent quota exhaustion and abuse |
| B8 | O3 Cost optimization | Can't optimize costs you don't measure |

---

## INPUTS / OUTPUTS

### Primary Function: `route_request()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| messages | `list[Message]` | Universal format: `{role: system|user|assistant, content: str}` |
| citizen_id | `str` | Identifies the requesting citizen for tier lookup and cost attribution |
| tier | `str` | `"free"` or `"paid"` — determines model selection and rate limits |
| provider_preference | `str | None` | Optional: citizen's preferred provider (e.g., `"anthropic"`) |
| byoai_key | `str | None` | Optional: citizen's own API key for a specific provider |
| model_override | `str | None` | Optional: specific model requested (e.g., `"claude-opus-4-20250514"`) |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| stream | `AsyncGenerator[StreamChunk]` | Unified stream of response chunks |

**Side Effects:**

- Cost event emitted (provider, model, tokens, cost)
- Rate limit counters incremented for the citizen's tier
- Fallback events logged if primary provider failed

---

## EDGE CASES

### E1: All Providers in Fallback Chain Are Down

```
GIVEN:  Every provider in the fallback chain returns an error
THEN:   The Router raises a RoutingExhaustedError with the list of attempted providers and their errors
AND:    The Orchestrator receives a clear signal that no LLM is available (not a silent failure)
```

### E2: BYOAI Key Is Invalid

```
GIVEN:  A citizen provides a BYOAI key that the provider rejects (401 Unauthorized)
THEN:   The Router returns an AuthenticationError specific to BYOAI
AND:    The Router does NOT fall back to the system key (citizen chose BYOAI, they own the failure)
AND:    The error message indicates the citizen's key is invalid, not MIND's
```

### E3: Provider Returns Non-Streaming Response

```
GIVEN:  A provider SDK returns a complete response instead of a stream (bug or misconfiguration)
THEN:   The adapter wraps it into a single StreamChunk and yields it
AND:    The downstream consumer sees a valid (if instant) stream
```

### E4: Mid-Stream Provider Failure

```
GIVEN:  A provider starts streaming but drops the connection mid-response
THEN:   The Router emits a StreamInterruptedError
AND:    Partial content already yielded is NOT retracted (already sent to user)
AND:    The Router does NOT attempt fallback (partial response already delivered)
```

### E5: Model Override Requests Unavailable Model

```
GIVEN:  A citizen requests a specific model that is not in the model registry
THEN:   The Router returns a ModelNotFoundError listing available models for the citizen's tier
AND:    No provider is called
```

---

## ANTI-BEHAVIORS

What should NOT happen:

### A1: Silent Swallowing of Provider Errors

```
GIVEN:   A provider returns an error
WHEN:    The Router processes the error
MUST NOT: Swallow the error and return an empty response or None
INSTEAD:  Attempt fallback, and if fallback exhausted, raise with full error context
```

### A2: Provider Logic Leaking Into Core

```
GIVEN:   Any code in router.py or outside a provider adapter
WHEN:    Processing a request
MUST NOT: Contain provider-specific branching (if provider == "anthropic": ...)
INSTEAD:  Call the adapter interface; let the adapter handle provider specifics
```

### A3: Falling Back to System Key on BYOAI Failure

```
GIVEN:   A BYOAI citizen's key fails authentication
WHEN:    The Router handles the error
MUST NOT: Silently switch to the system key and continue
INSTEAD:  Return an error to the citizen indicating their key is invalid
```

### A4: Non-Streaming Response Path

```
GIVEN:   Any request to the Router
WHEN:    Generating a response
MUST NOT: Return a complete string response (non-streaming)
INSTEAD:  Always return an AsyncGenerator[StreamChunk], even if it yields a single chunk
```

---

## MARKERS

<!-- @mind:todo Define StreamChunk schema (text, finish_reason, usage, metadata) -->
<!-- @mind:todo Clarify E4 behavior: should we attempt fallback on mid-stream failure or not? Tradeoff: user sees partial + new response vs. partial + error -->
<!-- @mind:escalation BYOAI fallback policy needs Nicolas's confirmation: should BYOAI failure NEVER fall back to system key, or should it be configurable? -->
