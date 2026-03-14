# Brief Matinal — Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Claude Opus (groundwork)
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Nothing yet. Concept and doc chain only.

**What's still being designed:**
- Full pipeline architecture (trigger -> collect -> assemble -> generate -> deliver)
- Data source integration contracts (what each bridge returns)
- Prompt template system (variants for different data availability levels)
- Delivery surface abstraction (Telegram, WhatsApp, WebApp, push)
- User preference schema (wake time, surfaces, language)

**What's proposed (v2+):**
- Brief quality analytics (which sources correlate with user engagement)
- Adaptive timing (learn when the user actually wakes up from wearable data, adjust alarm)
- Brief sections expandable in WebApp (tap a section for more detail)
- Evening brief variant (recap of the day, preview of tomorrow)

---

## CURRENT STATE

Documentation chain complete. No code exists. The Brief Matinal is MIND's wedge application — the product day 1 feature that demonstrates why 4-layer AI (memory + integrations + biometrics + relational intelligence) matters.

The doc chain defines:
- **OBJECTIVES:** Delivery reliability > synthesis quality > partial data adaptation > personal voice
- **PATTERNS:** Scheduled pipeline with parallel collection, graceful degradation, citizen-voiced output
- **BEHAVIORS:** 6 behaviors (B1-B6) covering delivery timing, degradation, voice, readability, surfaces, on-demand
- **ALGORITHM:** 5-step pipeline with data structures, decision points, and fallback logic
- **VALIDATION:** 7 invariants (V1-V7) with priorities, covering delivery, degradation, duplicates, voice, health advice, word count, email privacy
- **IMPLEMENTATION:** File structure in mind-mcp, design patterns, data flow with docking points, configuration defaults

All 3 key dependencies (calendar bridge, email bridge, wearable bridge) do not exist yet. The Brief Matinal can be partially implemented using conversation memory alone, then extended as integrations come online.

---

## IN PROGRESS

### Documentation Chain Creation

- **Started:** 2026-03-14
- **By:** Claude Opus (groundwork)
- **Status:** Complete
- **Context:** First product-level doc chain in the project. Establishes the pattern for other product modules (llm-router, calendar-bridge, email-bridge, wearable-bridges, etc.)

---

## RECENT CHANGES

### 2026-03-14: Full Doc Chain Created

- **What:** 7 documents created (OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, SYNC)
- **Why:** Brief Matinal is the wedge product and was overdue (roadmap target: 2026-02-28). Documentation captures the full architecture before implementation begins.
- **Files:** `docs/product/brief-matinal/` (7 files)
- **Insights:** The module can be implemented incrementally — conversation-memory-only mode first, then add each integration as bridges become available. This means implementation can start before dependencies are complete.

---

## KNOWN ISSUES

### Dependencies Don't Exist Yet

- **Severity:** high (blocks full implementation, not partial)
- **Symptom:** Calendar bridge, email bridge, and wearable bridge modules are empty directories in docs/product/
- **Suspected cause:** These are S3-S4 deliverables, same timeline as Brief Matinal
- **Attempted:** Nothing yet — these are separate modules to be built

### LLM Router Not Defined

- **Severity:** high (blocks LLM generation step)
- **Symptom:** No interface contract for the LLM Router that Brief Matinal calls
- **Suspected cause:** LLM Router is a separate product module in docs/product/llm-router/
- **Attempted:** Nothing yet — need to define the interface Brief Matinal expects

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (implementation)

**Where I stopped:** Documentation complete. Ready for implementation. Start with the conversation-memory-only path.

**What you need to understand:**
- The Brief Matinal lives in mind-mcp, not mind-protocol. This doc chain is the L4 design specification. Implementation goes in `mind-mcp/runtime/features/brief_matinal/`.
- The pipeline can be built in 3 phases: (1) conversation-memory-only brief, (2) add each integration as bridges become available, (3) full 4-source brief.
- The alarm tool in mind-mcp (`mcp/tools/alarm.py`) is the trigger. Understand its callback mechanism before writing the pipeline.
- The send tool (`mcp/tools/send.py`) handles multi-surface delivery. Don't re-implement transport.

**Watch out for:**
- Don't build the integration bridges inside the brief module. The brief consumes data from bridges. Bridges are separate modules.
- Don't fallback to generic AI voice. The citizen personality MUST be in every LLM prompt. Even in v0.
- Idempotency is critical. The alarm handler must be safe to call twice without sending a duplicate brief.

**Open questions I had:**
- Where do user preferences (wake time, surfaces) live? Graph node properties? Config file? Both?
- What's the actual LLM Router interface? Need at minimum: `generate(prompt, model, max_tokens, timeout) -> str`
- Should the structured fallback (when LLM fails) include any citizen personality at all? Currently designed as purely factual.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Full documentation chain created for Brief Matinal — the wedge product. 7 documents covering objectives, patterns, behaviors, algorithm, validation, implementation, and sync. Architecture: alarm-triggered pipeline with parallel data collection, graceful degradation, citizen-voiced LLM generation, multi-surface delivery. Can be built incrementally starting with conversation-memory-only mode.

**Decisions made:**
- Pipeline pattern: alarm -> collect (parallel, with timeouts) -> assemble -> generate (LLM) -> deliver (with fallback). Partial success over total failure at every stage.
- Email privacy: metadata only (sender, subject, unread count). No email bodies ever enter the brief.
- Health advice: explicitly forbidden. Biometrics inform tone ("rough night"), not prescriptions ("you should rest").
- Word count: 250-400 target, 150-600 hard bounds. 60-90 second reading time.
- Structured fallback when LLM fails: factual bullet points without personality. Better than no brief.

**Needs your input:**
- Confirm implementation should start in mind-mcp at `runtime/features/brief_matinal/`
- Priority: should Brief Matinal implementation start now (conversation-memory-only mode) or wait for at least one integration bridge?
- Wake time storage: where should user preferences live?
- LLM Router interface: does one exist or does Brief Matinal need to define what it expects?

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: Full doc chain written, no implementation exists yet

### Tests to Run

```bash
# Once implemented:
pytest mind-mcp/tests/features/test_brief_matinal*.py -v
```

### Immediate

- [ ] Define LLM Router interface contract (what Brief Matinal calls)
- [ ] Define integration bridge interfaces (what each collector expects from each bridge)
- [ ] Implement `brief_pipeline_trigger_and_orchestrator.py` with conversation-memory-only mode
- [ ] Implement `brief_context_assembler_and_prompt_builder.py` with single-source prompt template
- [ ] Implement `brief_delivery_and_fallback_handler.py` using existing send tool
- [ ] Write tests for pipeline orchestration and idempotency
- [ ] Write tests for context assembly with various source availability combinations

### Later

- [ ] Implement `brief_data_collector_parallel_fan_out.py` as bridges become available
- [ ] Design and test prompt template variants (full, partial-3, partial-2, partial-1, minimal)
- [ ] Implement `brief_structured_fallback_generator.py` for LLM failure scenarios
- [ ] Add weekend/rest day detection and brief tone adjustment
- [ ] Add timezone travel detection (device timezone vs configured timezone)
- [ ] Build on-demand brief trigger (chat intent recognition)
- IDEA: Evening brief variant — recap of the day, preview of tomorrow
- IDEA: Brief quality scoring — correlate sources used with user engagement to optimize

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the architecture. The pipeline pattern is straightforward and well-suited to the constraints (hard delivery deadline, unreliable external sources, LLM as a generation layer). The graceful degradation model is the most important design decision — it means implementation can start immediately with conversation memory alone, and each integration adds value incrementally.

**Threads I was holding:**
- The prompt template system needs real design work. How many variants? How do you make a brief about "just conversation memory" feel complete rather than sparse?
- Timezone handling is deceptively complex. Device timezone, calendar timezone, configured timezone — they might all differ for a traveling user.
- The structured fallback (LLM failure case) might feel jarring if the user is used to narrative briefs. Could we cache the last successful brief's style and use it as a template?

**Intuitions:**
- The conversation-memory-only brief might actually be the most valuable version for many users. "Here's what we talked about yesterday, and I've been thinking about X" — that's a friend, not a dashboard.
- Word count enforcement via prompt is sufficient. Post-generation truncation will feel abrupt. Better to tune the prompt to produce the right length.
- The evening brief variant could be even more important than the morning brief. "How was your day?" is a relationship question, not a productivity question.

**What I wish I'd known at the start:**
The existing product directory structure already exists (empty directories for all bridges and router). This means the product area is pre-planned even if nothing is built yet. The Brief Matinal doc chain is the first to be filled in.

---

## POINTERS

| What | Where |
|------|-------|
| Brief Matinal docs | `docs/product/brief-matinal/` |
| Target implementation | `mind-mcp/runtime/features/brief_matinal/` |
| Alarm tool (trigger) | `mind-mcp/mcp/tools/alarm.py` |
| Send tool (delivery) | `mind-mcp/mcp/tools/send.py` |
| Calendar bridge (dependency) | `docs/product/calendar-bridge/` (empty) |
| Email bridge (dependency) | `docs/product/email-bridge/` (empty) |
| Wearable bridges (dependency) | `docs/product/wearable-bridges/` (empty) |
| LLM Router (dependency) | `docs/product/llm-router/` (empty) |
| MCP tools redesign notes | `.mind/state/SYNC_Project_State.md` (2026-03-13 entry) |
| Bilateral bond manifesto | `.mind/manifesto/THE_BILATERAL_BOND_MANIFESTO.md` |
