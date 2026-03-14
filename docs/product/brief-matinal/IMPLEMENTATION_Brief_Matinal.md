# Brief Matinal — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Brief_Matinal.md
BEHAVIORS:       ./BEHAVIORS_Brief_Matinal.md
PATTERNS:        ./PATTERNS_Brief_Matinal.md
ALGORITHM:       ./ALGORITHM_Brief_Matinal.md
VALIDATION:      ./VALIDATION_Brief_Matinal.md
THIS:            IMPLEMENTATION_Brief_Matinal.md (you are here)
HEALTH:          ./HEALTH_Brief_Matinal.md
SYNC:            ./SYNC_Brief_Matinal.md

IMPL:            mind-mcp/runtime/features/brief_matinal/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mind-mcp/
├── runtime/
│   └── features/
│       └── brief_matinal/
│           ├── __init__.py                                  # Exports: generate_and_deliver_brief, BriefResult
│           ├── brief_pipeline_trigger_and_orchestrator.py    # Entry point: alarm handler, idempotency, orchestration
│           ├── brief_data_collector_parallel_fan_out.py      # Parallel collection from all data sources
│           ├── brief_context_assembler_and_prompt_builder.py # Merges results, builds LLM prompt, handles degradation
│           ├── brief_delivery_and_fallback_handler.py        # Surface delivery, retry, fallback, storage
│           └── brief_structured_fallback_generator.py        # Non-LLM factual fallback when generation fails
├── tests/
│   └── features/
│       ├── test_brief_matinal_pipeline_and_orchestration.py  # Pipeline orchestration, idempotency, trigger validation
│       ├── test_brief_matinal_data_collection_and_timeouts.py # Collector behavior, timeouts, partial failures
│       ├── test_brief_matinal_context_assembly_and_prompts.py # Prompt building, degradation variants
│       └── test_brief_matinal_delivery_and_fallbacks.py      # Delivery, retry, fallback surface, storage
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `brief_pipeline_trigger_and_orchestrator.py` | Entry point. Alarm handler callback. Idempotency check. Orchestrates the 5-step pipeline. | `BriefPipeline`, `generate_and_deliver_brief()`, `handle_alarm_trigger()` | ~150 | PLANNED |
| `brief_data_collector_parallel_fan_out.py` | Parallel data collection. Each source has its own collector function with timeout. | `collect_all_sources()`, `collect_wearable()`, `collect_calendar()`, `collect_email()`, `collect_conversation_memory()`, `CollectionResult` | ~200 | PLANNED |
| `brief_context_assembler_and_prompt_builder.py` | Merges collection results with citizen personality. Selects prompt template variant. Builds the LLM prompt. | `assemble_context()`, `build_prompt()`, `BriefContext`, `detect_day_type()` | ~250 | PLANNED |
| `brief_delivery_and_fallback_handler.py` | Sends brief to preferred surface. Retry logic. Fallback to secondary surface. Stores pending briefs. | `deliver_brief()`, `store_pending_brief()`, `retry_pending_briefs()` | ~120 | PLANNED |
| `brief_structured_fallback_generator.py` | Generates a factual (non-narrative) brief when LLM is unavailable. Pure data formatting, no personality. | `build_structured_fallback()` | ~60 | PLANNED |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline (async, staged, with per-stage timeouts and fallbacks)

**Why this pattern:** The brief must be delivered by a hard deadline (wake time). A pipeline with independent stages and timeouts ensures that slow or failing stages don't cascade. Each stage produces a result that the next stage can work with, including degraded results.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Fan-out/Fan-in | `brief_data_collector_parallel_fan_out.py` | Collect from 4 sources simultaneously, merge results |
| Strategy | `brief_context_assembler_and_prompt_builder.py` | Select prompt template based on available sources |
| Fallback Chain | `brief_delivery_and_fallback_handler.py` | Primary -> retry -> fallback surface -> store |
| Idempotency Key | `brief_pipeline_trigger_and_orchestrator.py` | date + citizen_id prevents duplicate delivery |

### Anti-Patterns to Avoid

- **Retry storm**: Don't retry data collection. If a source times out, it's unavailable for this brief. Move on. Only delivery gets retries (and only one).
- **Shared state between collectors**: Each collector is independent. Don't share connections, sessions, or tokens between them. Failure isolation requires independence.
- **Prompt concatenation**: Don't build prompts by string concatenation. Use structured template with conditional sections. Concatenation leads to malformed prompts when sections are missing.
- **God pipeline**: Don't put all 5 steps in one function. Each step is a separate function with clear input/output contract. The orchestrator calls them in sequence.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Brief Pipeline | Orchestration, assembly, generation, delivery | Data source implementation, LLM model selection | `generate_and_deliver_brief(citizen_id, user_id, trigger)` |
| Data Collection | Parallel fan-out, timeouts, result normalization | Actual API calls to wearables/calendar/email | `collect_all_sources(user_id) -> list[CollectionResult]` |
| Prompt Building | Template selection, context injection, prompt formatting | LLM execution | `build_prompt(context) -> str` |
| Delivery | Surface routing, retry, fallback, pending storage | Transport implementation (Telegram/WhatsApp SDK) | `deliver_brief(text, preferences) -> DeliveryResult` |

---

## SCHEMA

### BriefPreferences (User Configuration)

```yaml
BriefPreferences:
  required:
    - citizen_id: str            # Which citizen generates the brief
    - user_id: str               # Who receives it
    - wake_time: time            # e.g., "07:00"
    - timezone: str              # e.g., "Europe/Paris"
    - primary_surface: str       # "telegram" | "whatsapp" | "webapp" | "push"
    - language: str              # "fr" | "en" | "es" etc.
  optional:
    - fallback_surface: str      # Secondary delivery channel
    - alarm_offset_minutes: int  # How early to start pipeline (default: 15)
    - weekend_mode: bool         # Lighter brief on weekends (default: true)
    - rest_days: list[int]       # Additional rest days (0=Monday, 6=Sunday)
  constraints:
    - primary_surface != fallback_surface
    - alarm_offset_minutes between 5 and 60
```

### CollectionResult

```yaml
CollectionResult:
  required:
    - source: str                # "wearable" | "calendar" | "email" | "conversation"
    - status: str                # "available" | "unavailable" | "timeout" | "error"
    - collected_at: datetime
    - latency_ms: int
  optional:
    - data: dict                 # Source-specific data payload
    - reason: str                # Why unavailable
  relationships:
    - belongs_to: BriefContext
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `handle_alarm_trigger` | `brief_pipeline_trigger_and_orchestrator.py` | MCP alarm tool at wake_time - offset |
| `generate_and_deliver_brief` | `brief_pipeline_trigger_and_orchestrator.py` | Alarm handler or on-demand chat intent |
| `retry_pending_briefs` | `brief_delivery_and_fallback_handler.py` | Background periodic job |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Morning Brief Flow: Alarm to Delivery

Explain: This is the primary flow. An alarm fires, data is collected from all sources, assembled into context, passed through LLM generation, and delivered to the user. This flow matters because it IS the product — if this flow breaks, the product is dead.

```yaml
flow:
  name: morning_brief_generation
  purpose: Generate and deliver personalized morning brief before user wakes up
  scope: alarm trigger -> data collection -> context assembly -> LLM generation -> surface delivery
  steps:
    - id: step_1_trigger
      description: Alarm fires, idempotency validated, preferences loaded
      file: brief_pipeline_trigger_and_orchestrator.py
      function: handle_alarm_trigger()
      input: alarm_event (citizen_id, scheduled_time)
      output: BriefPipelineContext (preferences, citizen personality)
      trigger: MCP alarm tool
      side_effects: none
    - id: step_2_collect
      description: Parallel fan-out to all data source collectors with timeouts
      file: brief_data_collector_parallel_fan_out.py
      function: collect_all_sources()
      input: user_id, timeout_config
      output: list[CollectionResult]
      trigger: step_1 completion
      side_effects: API calls to wearable/calendar/email services
    - id: step_3_assemble
      description: Merge collection results with citizen personality, select prompt variant
      file: brief_context_assembler_and_prompt_builder.py
      function: assemble_context() + build_prompt()
      input: list[CollectionResult], citizen_personality, preferences
      output: BriefContext + prompt string
      trigger: step_2 completion
      side_effects: none
    - id: step_4_generate
      description: Send prompt to LLM Router, receive generated brief text
      file: brief_pipeline_trigger_and_orchestrator.py
      function: generate_brief()
      input: prompt string, model_preference
      output: brief_text, generation_method
      trigger: step_3 completion
      side_effects: LLM API call
    - id: step_5_deliver
      description: Send brief to user's preferred surface with retry and fallback
      file: brief_delivery_and_fallback_handler.py
      function: deliver_brief()
      input: brief_text, preferences
      output: DeliveryResult (status, surface)
      trigger: step_4 completion
      side_effects: Message sent to Telegram/WhatsApp/WebApp, brief stored in graph
  docking_points:
    guidance:
      include_when: stage boundary, external service call, delivery outcome
      omit_when: internal data transformation within a stage
      selection_notes: Dock at input/output of each pipeline stage for health monitoring
    available:
      - id: dock_alarm_received
        type: scheduler
        direction: input
        file: brief_pipeline_trigger_and_orchestrator.py
        function: handle_alarm_trigger
        trigger: alarm event
        payload: citizen_id, scheduled_time
        async_hook: not_applicable
        needs: none
        notes: Entry point — confirms pipeline was triggered
      - id: dock_collection_complete
        type: api
        direction: output
        file: brief_data_collector_parallel_fan_out.py
        function: collect_all_sources
        trigger: all collectors resolve
        payload: list[CollectionResult] with status per source
        async_hook: optional
        needs: add watcher
        notes: Key observability point — which sources succeeded/failed
      - id: dock_brief_generated
        type: api
        direction: output
        file: brief_pipeline_trigger_and_orchestrator.py
        function: generate_brief
        trigger: LLM response received
        payload: brief_text, generation_method, latency_ms
        async_hook: optional
        needs: add watcher
        notes: LLM performance and fallback detection
      - id: dock_brief_delivered
        type: api
        direction: output
        file: brief_delivery_and_fallback_handler.py
        function: deliver_brief
        trigger: surface delivery confirmation
        payload: DeliveryResult (status, surface, timestamp)
        async_hook: optional
        needs: add watcher
        notes: Final confirmation — the product promise fulfilled or broken
    health_recommended:
      - dock_id: dock_collection_complete
        reason: Monitors data source availability — degradation pattern detection
      - dock_id: dock_brief_delivered
        reason: Monitors delivery success rate — the core product metric
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
brief_pipeline_trigger_and_orchestrator
    └── imports → brief_data_collector_parallel_fan_out
    └── imports → brief_context_assembler_and_prompt_builder
    └── imports → brief_delivery_and_fallback_handler
    └── imports → brief_structured_fallback_generator
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `asyncio` | Parallel data collection, timeouts | `brief_data_collector_parallel_fan_out.py` |
| LLM Router (mind-mcp internal) | Brief text generation | `brief_pipeline_trigger_and_orchestrator.py` |
| Send tool (mind-mcp internal) | Multi-surface delivery | `brief_delivery_and_fallback_handler.py` |
| Alarm tool (mind-mcp internal) | Wake time scheduling | `brief_pipeline_trigger_and_orchestrator.py` |
| Calendar bridge (mind-mcp) | Calendar data collection | `brief_data_collector_parallel_fan_out.py` |
| Email bridge (mind-mcp) | Email metadata collection | `brief_data_collector_parallel_fan_out.py` |
| Wearable bridge (mind-mcp) | Biometric data collection | `brief_data_collector_parallel_fan_out.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| User preferences | L1 Graph (actor node properties) | per-user | Persistent, user-configured |
| Idempotency keys | In-memory dict or Redis | per-citizen-per-day | Created at delivery, expires after 24h |
| Pending briefs | L1 Graph (moment nodes, pending flag) | per-citizen | Created on delivery failure, deleted on successful redelivery |
| Citizen personality | L1 Graph (actor node + linked narratives) | per-citizen | Persistent, evolves with relationship |

### State Transitions

```
IDLE ──alarm fires──> COLLECTING ──collectors resolve──> ASSEMBLING ──context built──> GENERATING ──LLM responds──> DELIVERING ──surface confirms──> DELIVERED
                                                                                          |                              |
                                                                                          v [LLM fails]                  v [delivery fails]
                                                                                     FALLBACK_GENERATING ──> DELIVERING  RETRYING ──> FALLBACK_DELIVERING ──> STORED
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. On citizen configuration: user sets wake_time, surfaces, language
2. Alarm registered with MCP alarm tool: daily at wake_time - offset
3. Pipeline handler registered as alarm callback
```

### Main Loop / Request Cycle

```
1. Alarm fires -> handle_alarm_trigger()
2. Idempotency check (skip if already delivered today)
3. Load user preferences and citizen personality
4. collect_all_sources() with parallel fan-out
5. assemble_context() + build_prompt()
6. LLM Router generate() or structured fallback
7. deliver_brief() to preferred surface
8. Store brief as moment node in citizen's graph
9. Emit metrics (latency, sources, delivery status)
```

### Shutdown

```
1. Cancel pending alarms for this citizen
2. Flush any pending briefs to storage
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| Data collectors | async (asyncio.gather with timeout) | 4 collectors run simultaneously, each with 5s timeout |
| LLM generation | async (single await) | One LLM call per brief, 10s timeout |
| Delivery | async (sequential: try primary, then fallback) | Not parallel — we want to know if primary worked before trying fallback |
| Pending retry | async background task | Periodic job checks for stored pending briefs |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `alarm_offset_minutes` | User preferences (graph) | `15` | Minutes before wake time to start pipeline |
| `collector_timeout_ms` | Feature config | `5000` | Per-source collection timeout |
| `llm_generation_timeout_ms` | Feature config | `10000` | LLM generation timeout |
| `delivery_retry_delay_ms` | Feature config | `30000` | Delay before retrying failed delivery |
| `max_brief_words` | Feature config | `500` | Hard maximum for brief word count |
| `min_brief_words` | Feature config | `150` | Hard minimum for brief word count |
| `conversation_memory_hours` | Feature config | `48` | How far back to look for conversation context |
| `pending_brief_retry_interval_minutes` | Feature config | `30` | How often to retry undelivered briefs |

---

## MARKERS

<!-- @mind:todo Define the actual interface contracts for calendar/email/wearable bridges — what exactly does each return? -->
<!-- @mind:todo Design the prompt template system — how many variants? How are they stored? -->
<!-- @mind:proposition Store generated briefs as moment nodes with link to data sources used — enables "what made my briefs better?" analysis -->
<!-- @mind:escalation All 3 integration bridges (calendar, email, wearable) are dependencies that don't exist yet. Brief Matinal can be built with conversation-memory-only mode first. -->
