# LLM Router — Patterns: Multi-Provider Abstraction with Fallback Chain

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_LLM_Router.md
THIS:            PATTERNS_LLM_Router.md (you are here)
BEHAVIORS:       ./BEHAVIORS_LLM_Router.md
ALGORITHM:       ./ALGORITHM_LLM_Router.md
VALIDATION:      ./VALIDATION_LLM_Router.md
IMPLEMENTATION:  ./IMPLEMENTATION_LLM_Router.md
SYNC:            ./SYNC_LLM_Router.md

IMPL:            mind-mcp/runtime/llm_router/router.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_LLM_Router.md: "Docs updated, implementation needs: {what}"
3. Run tests: `pytest tests/runtime/test_llm_router*.py`

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_LLM_Router.md: "Implementation changed, docs need: {what}"
3. Run tests: `pytest tests/runtime/test_llm_router*.py`

---

## THE PROBLEM

MIND currently calls Gemini directly in `mind-mcp`. Every LLM interaction is hardcoded to one provider. This creates three failures:

1. **Single point of failure.** Gemini goes down, MIND goes silent. No fallback.
2. **No model selection.** Free and paid citizens get the same model. No cost optimization. No tier differentiation.
3. **Provider lock-in.** Adding Claude, GPT, or any other model requires rewriting the call site, not plugging in an adapter.

Every LLM call in MIND must go through a single routing layer. Without it, provider-specific code spreads across the codebase, each with its own error handling, streaming format, and prompt structure. That fragmentation is fatal at scale.

---

## THE PATTERN

**Strategy pattern with fallback chain.**

The Router sits between the Orchestrator and all LLM providers. It receives a unified request (messages + model preference + tier), selects a provider, formats the prompt for that provider's API spec, streams the response back in a unified format, and falls back to the next provider on failure.

```
User Message
    |
    v
Orchestrator (decides WHAT to say)
    |
    v
LLM Router (decides WHO says it)
    |-- select_provider(tier, preference, availability)
    |-- format_prompt(messages, provider_spec)
    |-- stream_response(provider_api)
    |-- on_failure: fallback_to_next(chain)
    |
    v
Provider Adapter (Claude | GPT | Gemini | Mistral | DeepSeek | Llama | Grok | OpenRouter)
    |
    v
Provider API
    |
    v
Unified Stream Response
```

The key insight: **each provider is an adapter implementing the same interface**. The Router never knows which provider it is talking to after selection. The adapter handles all provider-specific formatting, authentication, and streaming translation.

---

## BEHAVIORS SUPPORTED

- **B1** (Streaming works across all providers) — The adapter interface mandates async streaming. No provider can be added without implementing it.
- **B2** (Fallback triggers on error) — The fallback chain is a first-class concept, not an afterthought. Each call wraps in a try-with-next pattern.
- **B3** (Free tier routes to cheaper models) — Model selection is a function of tier, not hardcoded. The mapping tier-to-models is configuration.
- **B4** (BYOAI uses customer key) — The adapter accepts an API key parameter. If the citizen provides one, it overrides the system key.

## BEHAVIORS PREVENTED

- **A1** (Provider lock-in) — No provider-specific code exists outside its adapter file. The core router is provider-agnostic.
- **A2** (Silent failure) — Failures raise, fallback engages, and if the entire chain exhausts, the error surfaces with full context.
- **A3** (Prompt format leaking) — The Orchestrator sends a universal message format. Only the adapter knows how to translate it to `system`/`user`/`assistant` or `model`/`user` or whatever the provider expects.

---

## PRINCIPLES

### Principle 1: Adapter Isolation

Each provider lives in exactly one file: `providers/{name}.py`. That file implements the `LLMProvider` interface (connect, format, stream, close). No provider-specific logic exists anywhere else. If you find yourself writing `if provider == "anthropic"` in the router, the abstraction is broken.

This matters because MIND will support 8+ direct providers and 100+ via OpenRouter. The only way this scales is if adding a provider means writing one file and registering it in the provider registry.

### Principle 2: Streaming as the Only Mode

There is no non-streaming path. Every provider adapter returns an async generator of `StreamChunk` objects. If a provider's SDK doesn't support streaming natively, the adapter wraps the synchronous response into a single-chunk stream. This eliminates an entire class of branching logic downstream.

This matters because the Orchestrator, chat bridges, and API all consume streams. Two code paths (streaming vs. buffered) means two sets of bugs, two sets of tests, two mental models. One path.

### Principle 3: Fail Fast, Fall Next

When a provider returns an error (rate limit, timeout, 500, auth failure), the Router does not retry the same provider. It immediately moves to the next provider in the fallback chain. Retries within a provider are the provider SDK's concern, not ours. The Router's job is provider selection, not provider babysitting.

This matters because retry loops against a rate-limited provider waste the 2-second fallback budget. Moving to the next provider is almost always faster than waiting for the same one to recover.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `mind-mcp/runtime/config/models.yaml` | FILE | Model registry: available models, their providers, cost tiers, context windows |
| `mind-mcp/runtime/config/providers.yaml` | FILE | Provider configuration: API endpoints, default models, rate limits per tier |
| Provider API keys | ENV | `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `MISTRAL_API_KEY`, `DEEPSEEK_API_KEY`, `TOGETHER_API_KEY`, `XAI_API_KEY`, `OPENROUTER_API_KEY` |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `mind-mcp/runtime/orchestrator/` | Sends messages to the Router, receives streamed responses |
| `mind-mcp/runtime/config/` | Provides model registry, provider config, tier-to-model mappings |
| Citizen tier data (from graph) | Determines whether citizen is free or paid, affects model selection |

---

## INSPIRATIONS

- **LiteLLM** — Unified interface for 100+ LLM providers. Demonstrates that a thin adapter layer can abstract provider differences effectively. We take the adapter-per-provider approach but not the dependency (LiteLLM is a heavy dependency with its own opinions about retries and caching).
- **OpenRouter** — Acts as a meta-provider routing to many models. We use OpenRouter as our catch-all adapter for long-tail models, but the Router itself handles primary providers directly for latency and cost control.
- **Nginx upstream fallback** — The pattern of trying the next upstream on failure, with configurable timeouts, is well-proven in infrastructure. Our fallback chain applies the same principle to LLM providers.

---

## SCOPE

### In Scope

- Provider adapter interface definition and implementation for 8 primary providers
- OpenRouter as catch-all for 100+ additional models
- Prompt formatting per provider (system/user/assistant role mapping)
- Unified async streaming response format
- Fallback chain with configurable priority per tier
- Model selection based on citizen tier (free vs. paid)
- BYOAI key passthrough
- Cost tracking per request (model, tokens, estimated cost)
- Rate limiting per tier (requests/minute, tokens/minute)

### Out of Scope

- **Prompt content decisions** -> see: `mind-mcp/runtime/orchestrator/`
- **Response quality evaluation** -> not in v1; future concern
- **Response caching** -> not in v1; potential optimization
- **Model fine-tuning** -> separate infrastructure entirely
- **Billing integration** -> cost tracking feeds into billing, but billing logic is separate
- **Chat history management** -> belongs to Orchestrator / session management

---

## MARKERS

<!-- @mind:todo Finalize the model registry YAML schema with tier-to-model mappings -->
<!-- @mind:todo Decide on OpenRouter as fallback-of-last-resort vs. peer in the chain -->
<!-- @mind:proposition Consider LiteLLM as a dependency instead of custom adapters — tradeoff: less code vs. heavy dependency with upgrade risk -->
