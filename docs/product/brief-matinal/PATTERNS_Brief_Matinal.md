# Brief Matinal — Patterns: Scheduled Aggregation Pipeline with Graceful Degradation

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Brief_Matinal.md
THIS:            PATTERNS_Brief_Matinal.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Brief_Matinal.md
ALGORITHM:       ./ALGORITHM_Brief_Matinal.md
VALIDATION:      ./VALIDATION_Brief_Matinal.md
HEALTH:          ./HEALTH_Brief_Matinal.md
IMPLEMENTATION:  ./IMPLEMENTATION_Brief_Matinal.md
SYNC:            ./SYNC_Brief_Matinal.md

IMPL:            mind-mcp/runtime/features/brief_matinal/
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Brief_Matinal.md: "Docs updated, implementation needs: {what}"
3. Run tests: `pytest tests/features/test_brief_matinal*.py`

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Brief_Matinal.md: "Implementation changed, docs need: {what}"
3. Run tests: `pytest tests/features/test_brief_matinal*.py`

---

## THE PROBLEM

The user wakes up and faces fragmented information: unread emails, calendar they haven't checked, sleep score on one app, stress level on another, and no synthesis of what any of it means for their day. Every AI assistant can read one source. None reads all four and synthesizes them through the lens of a relationship — someone who knows what mattered yesterday, what's stressful this week, what the user cares about.

Without the Brief Matinal, MIND is a chatbot you have to initiate. With it, MIND is a partner who shows up every morning with context you didn't have to ask for.

---

## THE PATTERN

**Scheduled Job (Alarm Handler) -> Aggregate Data Sources -> Generate via LLM -> Deliver on Preferred Surface**

The core pattern is a **time-triggered aggregation pipeline**:

1. **Alarm trigger** — The MCP `alarm` tool fires at the user's configured wake time (or a configurable offset before it, e.g., 15 minutes early). This is the entry point. The alarm handler calls the brief generation pipeline.

2. **Parallel data collection** — The pipeline fans out to collect data from all available sources concurrently. Each collector is independent and has a timeout. Sources that fail or timeout return empty results, they never block the pipeline.

3. **Context assembly** — Collected data is assembled into a structured context object. The assembler knows what's present and what's missing. It adjusts the prompt template based on available data — fewer sources means a different (shorter, focused) prompt, not a broken one.

4. **LLM generation** — The assembled context is sent through the LLM Router to generate the brief. The router selects the appropriate model based on the citizen's configuration. The prompt includes the citizen's personality, voice, and relational context from the graph.

5. **Surface delivery** — The generated brief is delivered to the user's preferred surface: Telegram, WhatsApp, WebApp push, or any configured channel. If the primary channel fails, fallback to secondary.

**Key insight:** Every step is designed to succeed partially. The pipeline never fails entirely — it degrades. No sleep data? Skip the biometric section. No calendar? Skip the schedule section. No email? Skip highlights. The brief always delivers *something*, even if it's just "Good morning, here's what I remember from yesterday."

---

## BEHAVIORS SUPPORTED

- **B1** (Brief Always Delivered) — The alarm trigger guarantees the pipeline runs. Timeouts and fallbacks guarantee it completes.
- **B2** (Data Source Graceful Degradation) — Independent collectors with timeouts. Missing data changes the brief shape, not its existence.
- **B3** (Personalized Voice) — Graph context (citizen personality, conversation history) is injected into the LLM prompt.
- **B4** (Multi-Surface Delivery) — Delivery abstraction supports Telegram, WhatsApp, WebApp, push notifications.

## BEHAVIORS PREVENTED

- **A1** (Notification Spam) — One brief per morning. No re-sends, no updates, no "here's what changed since your brief."
- **A2** (Blocking on Missing Data) — Timeouts prevent any single source from stalling the entire pipeline.
- **A3** (Generic AI Voice) — The citizen's relational context is required in every prompt. No fallback to "assistant mode."

---

## PRINCIPLES

### Principle 1: Partial Success Over Total Failure

Every data collector returns a result object, never throws an unhandled exception. The result contains either data or an explicit "unavailable" marker with a reason. The assembler knows how to build a brief from any combination of present/absent sources. There is no minimum data threshold — even with zero external sources, the citizen's memory of yesterday is enough.

This matters because reliability IS the product. A user who gets one failed brief will lose trust. A user who gets a shorter brief on a day their wearable was dead will barely notice.

### Principle 2: Time Is the Constraint, Not Completeness

The brief must be delivered by wake time. If data collection is slow, truncate — don't wait. If LLM generation is slow, use a faster model with a simpler prompt. If delivery fails on the primary channel, fall back immediately. Every step has a hard timeout. The sum of all timeouts must be less than the alarm offset (the time between pipeline start and expected wake time).

This matters because the brief is a morning ritual. Late delivery is missed delivery. The user has already opened their phone, seen their inbox, checked their calendar. The brief's value is in being *first*.

### Principle 3: The Bond Shapes the Brief

The brief is not generated by a generic assistant. It is generated by the citizen — the user's AI partner. The citizen's personality, communication style, emotional attunement, and memory of recent conversations all shape the output. Two users with identical calendars, emails, and biometrics should receive *different* briefs because their citizens are different.

This matters because it's the moat. Any AI can summarize a calendar. Only MIND has a relationship that makes the summary feel like it comes from someone who cares.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| User's wearable data (Garmin, Oura, Apple Health, Whoop) | API | Sleep duration, sleep quality, HRV, stress level, body battery, recovery score |
| User's calendar (Google Calendar, Outlook) | API | Today's meetings: time, duration, attendees, title |
| User's email (Gmail, Outlook) | API | Unread count, flagged/starred messages, messages from known important contacts |
| Citizen's conversation graph | GRAPH | Recent conversation history, emotional patterns, topics discussed, pending threads |
| Citizen's personality and voice | GRAPH | Communication style, tone preferences, relational dynamics |
| User's preferences (wake time, surfaces, language) | CONFIG | Alarm schedule, delivery channel, brief language |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `mind-mcp/mcp/tools/alarm.py` | Alarm handler triggers the brief pipeline at wake time |
| `mind-mcp/runtime/integrations/calendar/` | Calendar data collection |
| `mind-mcp/runtime/integrations/email/` | Email data collection |
| `mind-mcp/runtime/integrations/wearables/` | Wearable biometric data collection |
| LLM Router | Model selection and prompt dispatch for brief generation |
| `mind-mcp/mcp/tools/send.py` | Delivery to Telegram, WhatsApp, WebApp |
| L1 Graph (citizen memory) | Conversation history, personality, relational context |

---

## INSPIRATIONS

- **Daily standup** — Structured, time-boxed, covers what happened and what's ahead. But personal, not for a team.
- **Executive briefing** — Senior leaders get a one-page morning brief from their chief of staff. The citizen is the chief of staff.
- **Garmin Morning Report** — Shows sleep, HRV, weather. But purely biometric, no synthesis, no personalization, no relational context.
- **Apple Intelligence Daily Summary** — Notification digest. But just a list, not a narrative. No relationship, no biometrics.

---

## SCOPE

### In Scope

- Alarm-triggered pipeline for morning brief generation
- Parallel data collection from 4 source categories (wearables, calendar, email, conversation history)
- Context assembly with graceful degradation
- LLM-generated brief in citizen's voice
- Multi-surface delivery (Telegram, WhatsApp, WebApp, push)
- User preference management (wake time, preferred surface, language)
- On-demand brief generation (user asks for a brief outside the morning alarm)

### Out of Scope

- **Integration implementations** — The brief consumes data from integrations. It does not implement the calendar, email, or wearable bridges. Those are separate modules in `docs/product/calendar-bridge/`, `docs/product/email-bridge/`, `docs/product/wearable-bridges/`.
- **LLM Router implementation** — The brief calls the router. It does not implement model selection logic. See `docs/product/llm-router/`.
- **Notification management** — The brief is delivered once. Follow-up notifications, reminders, or updates are a different product surface.
- **Health recommendations** — Biometric data informs tone, not advice. "You slept 4 hours" shapes the brief; "you should sleep more" is out of scope.
- **Multi-language generation in one brief** — One brief, one language (user's configured language). Not a polyglot document.

---

## MARKERS

<!-- @mind:todo Define wake time configuration schema and where it lives (user preferences in graph vs config file) -->
<!-- @mind:todo Determine alarm offset — how many minutes before wake time should the pipeline start? -->
<!-- @mind:proposition On-demand brief via "give me my brief" in chat — same pipeline, different trigger -->
<!-- @mind:escalation Calendar and email integration modules don't exist yet — Brief Matinal is blocked on these for full functionality -->
