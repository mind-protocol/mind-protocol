# OBJECTIVES — LLM Router

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
THIS:            OBJECTIVES_LLM_Router.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_LLM_Router.md
BEHAVIORS:      ./BEHAVIORS_LLM_Router.md
ALGORITHM:      ./ALGORITHM_LLM_Router.md
VALIDATION:     ./VALIDATION_LLM_Router.md
IMPLEMENTATION: ./IMPLEMENTATION_LLM_Router.md
SYNC:           ./SYNC_LLM_Router.md

IMPL:           mind-mcp/runtime/llm_router/router.py
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Universal LLM access** — Every citizen communicates through the Router. It must abstract away provider differences so the rest of MIND never thinks about which LLM is behind the call. One interface, any model. This is the structuring component: if it breaks, all of MIND goes silent.

2. **Fallback resilience** — Provider outages are routine (rate limits, downtime, region blocks). The Router must detect failure and cascade to the next viable provider within 2 seconds. No user message should be lost because a single provider is down.

3. **Cost optimization** — Free-tier citizens route to the cheapest viable models. Paid citizens get premium models. The Router enforces this transparently. MIND's unit economics depend on routing the right model to the right tier. Without this, either the free tier bleeds money or the paid tier underwhelms.

4. **BYOAI (Bring Your Own AI)** — Citizens who provide their own API key bypass MIND's key and rate limits entirely. Their key, their cost, their quota. This creates an escape valve for power users and removes MIND from the billing path for heavy consumers.

5. **Streaming uniformity** — All providers must emit responses as a unified async stream. The downstream consumer (Orchestrator, chat bridges, API) should never need to know which provider generated the tokens. Same event shape, same chunk format, same error signals.

## NON-OBJECTIVES

- **Model fine-tuning or training** — The Router routes, it does not train. Fine-tuning is a separate concern.
- **Prompt engineering** — The Router formats prompts per provider spec (system/user/assistant), but it does not decide *what* to say. Prompt content belongs to the Orchestrator.
- **Semantic evaluation of responses** — The Router does not judge quality. It delivers whatever the LLM returns. Quality evaluation, if needed, belongs upstream.
- **Caching responses** — Response caching is a potential future optimization but is not in scope for v1. The Router is stateless per request.
- **Provider negotiation or contracts** — Business relationships with providers are external. The Router consumes API keys and endpoints as configuration.

## TRADEOFFS (canonical decisions)

- When **latency** conflicts with **cost**, choose cost for free-tier and latency for paid-tier.
- When **provider preference** conflicts with **availability**, choose availability. A user who prefers Claude but Claude is down gets GPT, not an error.
- When **streaming complexity** conflicts with **implementation speed**, choose streaming. Non-streaming is not acceptable even as a temporary state.
- We accept **higher implementation effort per provider** to preserve a clean adapter interface. No provider leaks its quirks into the core.

## SUCCESS SIGNALS (observable)

- A message sent through the Router returns a streamed response regardless of which provider handles it
- When the primary provider fails, fallback engages and the user sees a response (not an error) within 2 seconds of failure detection
- Free-tier citizens demonstrably route to cheaper models; paid-tier citizens route to premium models
- BYOAI citizens use their own key and see no MIND rate limits
- Adding a new provider requires implementing one adapter file, not modifying the core router
