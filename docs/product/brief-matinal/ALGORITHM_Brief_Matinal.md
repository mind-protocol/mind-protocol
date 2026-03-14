# Brief Matinal — Algorithm: Data Collection, Assembly, Generation, Delivery

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
THIS:            ALGORITHM_Brief_Matinal.md (you are here)
VALIDATION:      ./VALIDATION_Brief_Matinal.md
HEALTH:          ./HEALTH_Brief_Matinal.md
IMPLEMENTATION:  ./IMPLEMENTATION_Brief_Matinal.md
SYNC:            ./SYNC_Brief_Matinal.md

IMPL:            mind-mcp/runtime/features/brief_matinal/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The Brief Matinal algorithm is a 5-step pipeline: **Trigger -> Collect -> Assemble -> Generate -> Deliver**. Each step has hard timeouts and fallback behavior. The pipeline is designed so that no single failure can prevent a brief from being delivered. The worst case is a shorter, simpler brief — never no brief.

The pipeline runs as a single async operation triggered by the alarm handler or an on-demand user request. Total wall-clock time target: < 30 seconds from trigger to delivery, with generation itself targeting < 10 seconds.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1 (Delivery reliability) | B1, B4, B5 | Pipeline timeouts and fallbacks guarantee delivery |
| O2 (4-layer synthesis) | B3, B6 | Parallel collection + assembly ensures all layers are considered |
| O3 (Partial data adaptation) | B2 | Independent collectors with "unavailable" markers enable graceful degradation |
| O4 (Personal voice) | B3 | Graph context injection into the prompt produces citizen-voiced output |

---

## DATA STRUCTURES

### CollectionResult

```
CollectionResult:
    source: str              # "wearable", "calendar", "email", "conversation"
    status: enum             # AVAILABLE, UNAVAILABLE, TIMEOUT, ERROR
    data: dict | None        # Source-specific structured data, None if unavailable
    collected_at: datetime   # When collection completed
    latency_ms: int          # How long collection took
    reason: str | None       # Why unavailable, if applicable
```

### BriefContext

```
BriefContext:
    citizen_id: str
    user_id: str
    trigger: enum                    # ALARM | ON_DEMAND
    wake_time: datetime
    timezone: str
    day_type: enum                   # WEEKDAY | WEEKEND | REST_DAY
    language: str                    # User's configured language
    collections: list[CollectionResult]
    citizen_personality: dict        # From graph: voice, style, traits
    conversation_memory: list[dict]  # Recent conversation highlights
    available_sources: list[str]     # Which sources returned data
    missing_sources: list[str]       # Which sources were unavailable
```

### BriefResult

```
BriefResult:
    brief_text: str                  # The generated brief
    generation_method: enum          # LLM | STRUCTURED_FALLBACK
    model_used: str | None           # Which LLM model was used
    sources_used: list[str]          # Data sources that contributed
    sources_unavailable: list[str]   # Data sources that were absent
    generation_time_ms: int          # LLM generation latency
    total_pipeline_time_ms: int      # End-to-end pipeline latency
    delivery_status: enum            # DELIVERED | FALLBACK_DELIVERED | STORED
    delivery_surface: str            # Where it was delivered
    word_count: int                  # For monitoring brief length
    idempotency_key: str             # date + citizen_id, prevents duplicates
```

---

## ALGORITHM: generate_and_deliver_brief()

### Step 1: Trigger Validation

Validates the trigger and checks idempotency. For alarm triggers, verifies no brief has been delivered today. For on-demand triggers, skips idempotency (user explicitly asked).

```
def validate_trigger(citizen_id, trigger):
    if trigger == ALARM:
        key = f"{today_date}:{citizen_id}"
        if brief_already_delivered(key):
            return SKIP  # Idempotency: don't re-deliver
    load user preferences: wake_time, timezone, surfaces, language
    load citizen personality from graph
    return PROCEED with context
```

### Step 2: Parallel Data Collection

Fans out to all configured data source collectors simultaneously. Each collector runs independently with its own timeout. Failures in one collector never affect others.

```
async def collect_all_sources(user_id, timeout_per_source=5000ms):
    collectors = [
        collect_wearable_data(user_id),    # Sleep, HRV, stress, body battery
        collect_calendar_data(user_id),     # Today's meetings
        collect_email_data(user_id),        # Highlights, unread count
        collect_conversation_memory(citizen_id)  # Recent conversation context
    ]
    results = await gather_with_timeouts(collectors, timeout=timeout_per_source)
    return results  # Each result is a CollectionResult (AVAILABLE or UNAVAILABLE)
```

**Individual collectors:**

- **Wearable collector:** Queries the wearable bridge for last night's sleep data, current HRV, stress level, body battery/recovery. Returns structured biometric summary.
- **Calendar collector:** Queries the calendar bridge for today's events. Returns list of meetings with time, title, duration, attendee count. Flags meetings with known important contacts.
- **Email collector:** Queries the email bridge for unread count, starred/flagged messages, messages from contacts marked important in the graph. Does NOT return email bodies — only metadata.
- **Conversation collector:** Queries the citizen's L1 graph for recent conversation highlights. Extracts: topics discussed in the last 24-48 hours, open threads (things the user said they'd do), emotional tone of recent interactions.

### Step 3: Context Assembly

Builds a BriefContext from the collection results. Determines which prompt template to use based on available sources. Adjusts for time of day and day type.

```
def assemble_context(collections, citizen_personality, preferences, trigger):
    available = [c for c in collections if c.status == AVAILABLE]
    missing = [c for c in collections if c.status != AVAILABLE]

    # Determine prompt variant based on available sources
    # Full: all 4 sources -> rich narrative brief
    # Partial: 2-3 sources -> focused brief
    # Minimal: 0-1 sources -> conversation-memory-only brief

    day_type = detect_day_type(preferences.calendar, today)
    time_context = "morning" if trigger == ALARM else get_time_of_day()

    return BriefContext(
        collections=collections,
        available_sources=[c.source for c in available],
        missing_sources=[c.source for c in missing],
        citizen_personality=citizen_personality,
        day_type=day_type,
        ...
    )
```

### Step 4: LLM Generation

Sends the assembled context to the LLM Router for generation. The prompt is built dynamically based on available data. If LLM generation fails, falls back to structured (non-narrative) brief.

```
def generate_brief(context: BriefContext, timeout=10000ms):
    prompt = build_prompt(context)
    # Prompt includes:
    # - System: citizen personality, voice, style directives
    # - Context: assembled data from all available sources
    # - Instructions: brevity constraints (250-400 words), no health advice,
    #                 no apologies for missing data, time-of-day awareness
    # - Relational: recent conversation references to weave in naturally

    try:
        result = await llm_router.generate(
            prompt=prompt,
            model_preference=context.citizen_model_preference,
            max_tokens=600,
            timeout=timeout
        )
        return result.text, LLM
    except (Timeout, RateLimitError, ServiceError):
        return build_structured_fallback(context), STRUCTURED_FALLBACK
```

**Structured fallback (when LLM fails):**
```
def build_structured_fallback(context):
    # Not a narrative. Just the facts, formatted cleanly.
    lines = [f"Good morning."]
    if "wearable" in context.available_sources:
        lines.append(f"Sleep: {context.sleep_duration}h. Recovery: {context.body_battery}%.")
    if "calendar" in context.available_sources:
        count = len(context.meetings)
        lines.append(f"Today: {count} meeting{'s' if count != 1 else ''}.")
    if "email" in context.available_sources:
        lines.append(f"Inbox: {context.unread_count} unread.")
    return "\n".join(lines)
```

### Step 5: Delivery

Sends the generated brief to the user's preferred surface. Handles delivery failures with retry and fallback.

```
def deliver_brief(brief_text, preferences, context):
    primary = preferences.primary_surface
    fallback = preferences.fallback_surface

    # Attempt primary delivery
    try:
        await send(surface=primary, user_id=context.user_id, text=brief_text)
        return DELIVERED, primary
    except DeliveryError:
        await sleep(30_seconds)
        # Retry primary once
        try:
            await send(surface=primary, user_id=context.user_id, text=brief_text)
            return DELIVERED, primary
        except DeliveryError:
            pass

    # Fallback delivery
    if fallback:
        try:
            await send(surface=fallback, user_id=context.user_id, text=brief_text)
            return FALLBACK_DELIVERED, fallback
        except DeliveryError:
            pass

    # Store for later delivery
    store_pending_brief(context.citizen_id, brief_text)
    return STORED, None
```

---

## KEY DECISIONS

### D1: Parallel vs Sequential Collection

```
IF collection is parallel:
    Total collection time = max(individual times) ≈ 3-5 seconds
    One slow source doesn't delay others
    Requires async runtime
ELSE (sequential):
    Total collection time = sum(individual times) ≈ 12-20 seconds
    Too slow for morning delivery
-> CHOSE: Parallel. Latency budget demands it.
```

### D2: LLM Failure Handling

```
IF LLM generation fails:
    Send structured fallback (factual, no narrative, no personality)
    User gets data without the citizen's voice
    Better than no brief at all
ELSE:
    Full narrative brief in citizen's voice
-> Structured fallback is an acceptable degradation. No brief is not.
```

### D3: Email Content Depth

```
IF we fetch email bodies:
    Richer context, but privacy risk, larger payload, slower
    Users may not consent to full email body access
ELSE (metadata only):
    Unread count, senders, subject lines
    Lower privacy risk, faster, sufficient for morning context
-> CHOSE: Metadata only. Subject lines and sender names are enough for "you got an email from your boss about the Q3 report."
```

### D4: Conversation Memory Window

```
IF we include last 7 days of conversation:
    Rich context but large prompt, higher LLM cost
    Risk of referencing something the user has forgotten
ELSE (last 24-48 hours):
    Fresh, relevant, manageable prompt size
    Misses important multi-day threads
-> CHOSE: 48 hours as default, with ability to pull specific older threads if they have high energy in the graph.
```

---

## DATA FLOW

```
Alarm fires (or on-demand trigger)
    |
    v
Trigger validation (idempotency check)
    |
    v
Parallel data collection (4 sources, 5s timeout each)
    |
    +-- wearable_collector -----> CollectionResult
    +-- calendar_collector -----> CollectionResult
    +-- email_collector --------> CollectionResult
    +-- conversation_collector -> CollectionResult
    |
    v
Context assembly (merge results + citizen personality + preferences)
    |
    v
BriefContext
    |
    v
LLM generation (prompt built from context, 10s timeout)
    |                                         |
    v [success]                               v [failure]
Narrative brief in citizen's voice            Structured factual fallback
    |                                         |
    +-------------------+---------------------+
                        |
                        v
Delivery (primary surface -> retry -> fallback surface -> store)
    |
    v
BriefResult (logged, stored as moment in graph)
```

---

## COMPLEXITY

**Time:** O(1) per brief generation — fixed number of sources, single LLM call. Not dependent on user count (each user's brief is independent).

**Space:** O(n) where n = combined size of collection results. In practice < 10KB of structured data per brief.

**Bottlenecks:**
- LLM generation latency (3-10 seconds depending on model and load)
- Wearable API latency (Garmin/Oura APIs can be slow, 2-5 seconds)
- Calendar API rate limits (Google Calendar API has per-user quotas)

---

## HELPER FUNCTIONS

### `build_prompt(context: BriefContext)`

**Purpose:** Constructs the LLM prompt from the assembled context. Dynamically includes/excludes sections based on available data. Injects citizen personality directives.

**Logic:** Template-based with conditional sections. System prompt sets the citizen's voice. User prompt contains the data. Instruction section enforces word count, anti-behaviors (no health advice, no apologies), and time-of-day awareness.

### `detect_day_type(calendar_data, date)`

**Purpose:** Determines if today is a weekday, weekend, or user-defined rest day. Affects brief tone and content emphasis.

**Logic:** Check day of week. If weekend but calendar has meetings, treat as "working weekend" (lighter tone but include calendar). If user has rest days configured, respect those.

### `build_structured_fallback(context: BriefContext)`

**Purpose:** Creates a no-LLM factual brief when generation fails. Purely data-driven, no personality.

**Logic:** Extract key numbers from each available collection result. Format as clean, short bullet-style text. No narrative, no citizen voice.

### `store_pending_brief(citizen_id, brief_text)`

**Purpose:** Stores a brief that couldn't be delivered for later delivery when the channel becomes available.

**Logic:** Store in graph as a pending moment. Background job checks periodically for pending briefs and attempts redelivery.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| Wearable bridge | `get_last_night_sleep(user_id)` | Sleep duration, quality, HRV, stress, body battery |
| Calendar bridge | `get_today_events(user_id)` | List of meetings with metadata |
| Email bridge | `get_inbox_highlights(user_id)` | Unread count, starred messages, important sender activity |
| L1 Graph | `get_recent_conversations(citizen_id, hours=48)` | Conversation highlights, open threads, emotional patterns |
| L1 Graph | `get_citizen_personality(citizen_id)` | Voice, style, traits, communication preferences |
| LLM Router | `generate(prompt, model_preference, max_tokens)` | Generated brief text |
| Send tool | `send(surface, user_id, text)` | Delivery confirmation |
| Alarm tool | `set_alarm(citizen_id, time, handler)` | Alarm registration |

---

## MARKERS

<!-- @mind:todo Define prompt templates for each data availability variant (full, partial-3, partial-2, partial-1, minimal) -->
<!-- @mind:todo Specify conversation memory extraction logic — what counts as a "highlight" worth including in the brief? -->
<!-- @mind:proposition Cache wearable data overnight so collection is instant at alarm time -->
<!-- @mind:proposition Brief versioning — store each brief as a moment node for later analysis of what the user found useful -->
<!-- @mind:escalation LLM Router module doesn't exist yet — need to define the interface this module expects -->
