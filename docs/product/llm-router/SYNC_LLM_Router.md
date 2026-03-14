# LLM Router — Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Claude Opus (architect)
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Nothing yet. Module is in documentation phase.

**What's still being designed:**
- Provider adapter interface (LLMProvider ABC)
- Fallback chain resolution algorithm
- Tier-based model selection mapping
- Cost tracking and rate limiting approach
- Streaming normalization format (StreamChunk)
- BYOAI key detection and isolation

**What's proposed (v2+):**
- Adaptive fallback ordering based on provider reliability metrics
- Response caching for identical prompts
- Automatic provider health monitoring with proactive removal from chains
- Function calling / tool use abstraction across providers
- Vision / multimodal input routing

---

## CURRENT STATE

The LLM Router does not exist yet. MIND currently calls Gemini directly in `mind-mcp` with no abstraction layer. Every LLM interaction is hardcoded to a single provider with no fallback, no tier differentiation, and no cost tracking.

This doc chain (7 files) captures the complete design for the Router. The architecture is: Strategy pattern with fallback chain, one adapter file per provider, unified async streaming, tier-based model selection, BYOAI passthrough, and cost tracking per request.

Target repository: `mind-mcp/runtime/llm_router/`

---

## IN PROGRESS

### Documentation Chain — COMPLETE

- **Started:** 2026-03-14
- **By:** Claude Opus (architect)
- **Status:** Complete
- **Context:** Full doc chain created: OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, SYNC. Ready for implementation.

---

## RECENT CHANGES

### 2026-03-14: Doc Chain Created

- **What:** Created complete documentation chain for the LLM Router module (7 files)
- **Why:** Router was due 14 Feb (S1-S2 roadmap) but had not started. Documentation-first approach per Mind Protocol principles.
- **Files:** `docs/product/llm-router/` (7 files)
- **Key decisions captured:**
  - Strategy + Chain of Responsibility pattern
  - 8 direct providers + OpenRouter catch-all
  - BYOAI gets no fallback (citizen's key, citizen's failure)
  - Mid-stream failure is terminal (no fallback after partial delivery)
  - Free tier: Gemini Flash, DeepSeek, Llama 70B, Mistral Large
  - Paid tier: Claude Opus, GPT-4o, Gemini Pro, Claude Sonnet
  - OpenRouter as last entry in every fallback chain (except BYOAI)

---

## KNOWN ISSUES

### Existing Gemini Direct Calls Must Be Migrated

- **Severity:** high
- **Symptom:** `mind-mcp` calls Gemini directly; Router cannot enforce routing until all calls go through it
- **Suspected cause:** Router did not exist when Gemini integration was built
- **Attempted:** Nothing yet. Migration is part of the implementation plan.

### Roadmap Delay

- **Severity:** medium
- **Symptom:** Router was due 14 Feb (S1-S2). It is 2026-03-14 and not started.
- **Suspected cause:** Other priorities (spawning, bonds, laws, wallet recovery) took precedence.
- **Attempted:** Doc chain created today to unblock implementation.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (implement)

**Where I stopped:** Documentation complete. No code written. The implementing agent starts from scratch in `mind-mcp/runtime/llm_router/`.

**What you need to understand:**
- Read all 7 docs in this chain before writing code. The ALGORITHM doc has full pseudocode for every function. The IMPLEMENTATION doc has the exact file structure and dependencies. Do not deviate from the designed architecture without updating the docs first.
- The existing Gemini code in `mind-mcp` is the reference for how the Orchestrator currently calls LLMs. The Router must replace those calls, not wrap them.
- All providers that support OpenAI-compatible APIs (Mistral, DeepSeek, Llama/Together, Grok/xAI) can share significant adapter code. Consider a `base_openai_compatible_adapter.py` to avoid duplication -- but each provider still gets its own file for registration and configuration differences.

**Watch out for:**
- Anthropic's API is NOT OpenAI-compatible. System messages are a separate parameter, not a role in the messages array. The adapter must handle this.
- Google Gemini uses `model` and `user` roles, not `system`/`user`/`assistant`. System instructions go in a separate `system_instruction` parameter.
- OpenRouter requires extra headers (`HTTP-Referer`, `X-Title`) and supports model routing via the model parameter.
- DeepSeek and Together AI are OpenAI-compatible but may have quirks in streaming (chunk format, finish_reason values). Test each.

**Open questions I had:**
- Should we use LiteLLM as a dependency or build custom adapters? Custom = more code, less risk. LiteLLM = less code, dependency risk. I leaned toward custom adapters but this is a decision for Nicolas or the implementing agent.
- Rate limiting backend: in-memory (simple, single-instance) or Redis (distributed, multi-instance)? Depends on mind-mcp deployment topology.
- Should OpenRouter be the fallback-of-last-resort in every chain, or should it be a peer provider that can be primary?

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete documentation chain for the LLM Router created (7 files). No code written yet. The Router is designed as a Strategy + Chain of Responsibility pattern with 8 direct providers plus OpenRouter as catch-all. Architecture: unified async streaming, tier-based model selection (free vs. paid), BYOAI passthrough, fallback chain with 2s target, cost tracking per request. Estimated effort: 3-4 days for architecture + 1 day per new provider adapter.

**Decisions made:**
- BYOAI failure does not fall back to system key (citizen owns their key and its failures)
- Mid-stream failure is terminal (no fallback after partial delivery -- would confuse the user)
- Free tier model pool: Gemini Flash, DeepSeek, Llama 70B, Mistral Large
- Paid tier model pool: Claude Opus, GPT-4o, Gemini Pro, Claude Sonnet
- OpenRouter as catch-all last entry in fallback chains

**Needs your input:**
- LiteLLM vs. custom adapters decision
- Rate limiting backend (memory vs. Redis) depends on deployment topology
- Confirm free/paid tier model pools
- Priority: start implementation now, or continue with other roadmap items?

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: Entire module needs implementing (no code exists yet)

### Tests to Run

```bash
# Once implemented:
pytest tests/runtime/test_llm_router*.py -v
```

### Immediate

- [ ] Create `mind-mcp/runtime/llm_router/` directory structure
- [ ] Implement `types.py` (Message, StreamChunk, Usage, RoutingContext, FallbackChain)
- [ ] Implement `base_llm_provider_interface.py` (LLMProvider ABC)
- [ ] Implement `provider_registry.py` (adapter registration and lookup)
- [ ] Implement `google_gemini_adapter.py` (replace existing direct Gemini calls)
- [ ] Implement `router.py` (core routing: resolve, execute, normalize)
- [ ] Implement `fallback.py` (chain builder and executor)
- [ ] Create `config/providers.yaml` and `config/models.yaml`
- [ ] Migrate existing Gemini direct calls to use the Router
- [ ] Write tests for route resolution, fallback, and streaming normalization

### Next (1 day each)

- [ ] Implement `anthropic_claude_adapter.py`
- [ ] Implement `openai_gpt_adapter.py`
- [ ] Implement `mistral_adapter.py`
- [ ] Implement `deepseek_adapter.py`
- [ ] Implement `llama_together_fireworks_adapter.py`
- [ ] Implement `grok_xai_adapter.py`
- [ ] Implement `openrouter_catch_all_adapter.py`

### Later

- [ ] Implement `rate_limiter.py`
- [ ] Implement `cost_tracker.py`
- [ ] Integration tests with real provider APIs (requires API keys)
- [ ] Load testing for concurrent request handling
- IDEA: Base class for OpenAI-compatible providers to reduce duplication across Mistral/DeepSeek/Together/xAI adapters

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the architecture. The Strategy + Chain of Responsibility pattern is well-suited for this problem. The main uncertainty is the LiteLLM vs. custom adapters decision -- both are defensible.

**Threads I was holding:**
- Many providers (Mistral, DeepSeek, Together, xAI) use OpenAI-compatible APIs. A shared base class could reduce per-adapter code from ~100 lines to ~30 lines. But each provider still needs its own file for discoverability.
- The cost tracking system needs to be fire-and-forget (don't block the stream). But cost events also need to be reliable (don't lose billing data). Tension between latency and durability.
- Rate limiting in a distributed deployment (multiple mind-mcp instances) requires shared state. Redis is the obvious answer but adds infrastructure.

**Intuitions:**
- Start with Gemini adapter (replace existing) + one non-Google provider (Anthropic or OpenAI) to prove the abstraction works. Then add the rest.
- The fallback chain will rarely trigger in practice (providers are reliable 99%+ of the time), but when it does, it will save the user experience. Worth the investment.
- OpenRouter as catch-all is powerful insurance but should not be the default. Direct provider calls are faster and cheaper.

**What I wish I'd known at the start:**
- The exact current Gemini integration code in mind-mcp, to ensure the Router interface is compatible with how the Orchestrator currently sends messages.

---

## POINTERS

| What | Where |
|------|-------|
| This doc chain | `docs/product/llm-router/` |
| Target implementation | `mind-mcp/runtime/llm_router/` |
| Existing Gemini integration | `mind-mcp/` (exact location TBD by implementing agent) |
| MCP Membrane redesign | `mind-mcp/mcp/server.py` + `mind-mcp/mcp/tools/*.py` |
| Model/provider config | `mind-mcp/runtime/config/` (to be created) |
