# LLM Router — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_LLM_Router.md
PATTERNS:        ./PATTERNS_LLM_Router.md
BEHAVIORS:       ./BEHAVIORS_LLM_Router.md
THIS:            VALIDATION_LLM_Router.md (you are here)
ALGORITHM:       ./ALGORITHM_LLM_Router.md
IMPLEMENTATION:  ./IMPLEMENTATION_LLM_Router.md
SYNC:            ./SYNC_LLM_Router.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These are the properties that, if violated, mean the LLM Router has failed its purpose. The Router is MIND's single chokepoint for all LLM communication. If these invariants break, citizens lose the ability to talk to their AI, or MIND loses money, or both.

---

## INVARIANTS

### V1: No Message Is Lost

**Why we care:** A citizen sends a message and expects a response. If the Router drops the message (silently fails, swallows an error, returns None), the citizen's experience breaks and trust erodes. In a system built on 1:1 bilateral bonds, losing a message is losing a piece of the relationship.

```
MUST:   Every message submitted to route_request() either produces a streamed response OR raises an explicit error
NEVER:  Return an empty stream, return None, or silently drop a request without error signaling
```

### V2: Streaming Is Universal

**Why we care:** All downstream consumers (Telegram, Discord, web app, API) are built on async streams. A non-streaming response would require a separate code path in every consumer. Two code paths means two sets of bugs. The Router's contract is: you always get a stream.

```
MUST:   Every successful response is an AsyncGenerator[StreamChunk], even if the underlying provider returns synchronously
NEVER:  Return a complete string response or a non-iterable object from route_request()
```

### V3: Fallback Engages Within 2 Seconds

**Why we care:** If the primary provider is down and the Router takes 30 seconds to try it before falling back, the citizen waits 30+ seconds for a response. That is indistinguishable from broken. The 2-second budget means: detect failure fast, move on fast.

```
MUST:   Time from primary provider failure detection to first byte from fallback provider is under 2 seconds
NEVER:  Retry the same failed provider before attempting fallback (retry loops consume the fallback budget)
```

### V4: Cost Tracking Is Accurate

**Why we care:** MIND's economic model depends on knowing what each request costs. If cost tracking is inaccurate, the free tier might run at a loss without anyone knowing. If cost attribution is wrong, paid citizens are billed incorrectly. Cost tracking is not analytics; it is a financial control.

```
MUST:   Every completed request emits a cost event with provider, model, input_tokens, output_tokens, and estimated_cost_usd
NEVER:  Complete a request without emitting cost data
NEVER:  Estimate cost using wrong model pricing (e.g., charging Opus price for a Flash response)
```

### V5: Tier Isolation

**Why we care:** Free-tier citizens must not accidentally route to expensive models (burns money). Paid-tier citizens must not be degraded to free-tier models (breaks the value proposition). The tier determines the model pool, and the pools must not mix.

```
MUST:   Free-tier requests only route to models in the free-tier pool
MUST:   Paid-tier requests only route to models in the paid-tier pool (or above)
NEVER:  Route a free-tier request to a premium model (unless BYOAI with citizen's own key)
```

### V6: BYOAI Key Isolation

**Why we care:** When a citizen provides their own API key, MIND must not use its system key as a fallback. If MIND silently falls back to the system key, MIND pays for the citizen's usage without their knowledge. This is both a financial risk and a trust violation.

```
MUST:   BYOAI requests use only the citizen's key
MUST:   BYOAI failures return errors to the citizen (their key, their problem)
NEVER:  Fall back from a citizen's key to MIND's system key
```

### V7: Adapter Isolation

**Why we care:** If provider-specific logic leaks into the core router, adding a new provider means modifying the router itself. At 8+ providers and growing, this creates merge conflicts, regression risk, and cognitive load. Each provider must be fully encapsulated in its adapter.

```
MUST:   Adding a new provider requires only: (1) creating a new adapter file, (2) registering it in the provider registry
NEVER:  Require modifying router.py, fallback.py, or cost_tracker.py to add a new provider
```

### V8: Rate Limits Enforced Before Provider Call

**Why we care:** Sending a request to a provider and then discarding the response because rate limits were exceeded wastes money. The rate limit check must happen before any network call.

```
MUST:   Rate limit check occurs before any provider API call
MUST:   Rate-limited requests return a RateLimitError with retry-after information
NEVER:  Call a provider API and then discard the response due to rate limits
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Citizens cannot communicate with their AI |
| **HIGH** | Major value lost | Financial loss or severe UX degradation |
| **MEDIUM** | Partial value lost | System works but suboptimally |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | No message lost | CRITICAL |
| V2 | Streaming is universal | CRITICAL |
| V3 | Fallback within 2s | HIGH |
| V4 | Cost tracking accurate | HIGH |
| V5 | Tier isolation | HIGH |
| V6 | BYOAI key isolation | HIGH |
| V7 | Adapter isolation (extensibility) | MEDIUM |
| V8 | Rate limits pre-check | MEDIUM |

---

## MARKERS

<!-- @mind:todo Write integration tests that verify V3 (fallback timing) with mocked provider failures -->
<!-- @mind:todo Define the cost accuracy tolerance: is 5% variance acceptable for estimated_cost_usd? Token counts must be exact. -->
<!-- @mind:proposition V9 candidate: "Provider health tracking" — track error rates per provider and proactively remove unhealthy providers from fallback chains before they waste time -->
