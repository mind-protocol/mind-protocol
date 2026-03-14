# Brief Matinal — Behaviors: What the User Sees Every Morning

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Brief_Matinal.md
THIS:            BEHAVIORS_Brief_Matinal.md (you are here)
PATTERNS:        ./PATTERNS_Brief_Matinal.md
ALGORITHM:       ./ALGORITHM_Brief_Matinal.md
VALIDATION:      ./VALIDATION_Brief_Matinal.md
HEALTH:          ./HEALTH_Brief_Matinal.md
IMPLEMENTATION:  ./IMPLEMENTATION_Brief_Matinal.md
SYNC:            ./SYNC_Brief_Matinal.md

IMPL:            mind-mcp/runtime/features/brief_matinal/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Brief Arrives Before the User Wakes Up

**Why:** The brief's entire value proposition depends on timing. It must be there when the user picks up their phone, not 20 minutes after they've already started scrolling email. If the brief is late, it's worthless — the user already has context from other sources.

```
GIVEN:  User has configured a wake time (e.g., 07:00) and at least one delivery surface
WHEN:   The alarm triggers at wake_time minus offset (e.g., 06:45)
THEN:   The brief is generated and delivered to the preferred surface before wake_time
AND:    The user sees the brief as an unread message/notification when they first check their device
```

### B2: Brief Degrades Gracefully When Data Sources Are Missing

**Why:** Users will have different integration profiles. Some have wearables, some don't. Some connect email, some refuse. The brief must never fail because a data source is unavailable — it reshapes itself around what's present. A shorter brief is still a brief. No brief is a failure.

```
GIVEN:  One or more data sources are unavailable (disconnected, timed out, no data)
WHEN:   The brief pipeline runs
THEN:   The brief is generated using only available data sources
AND:    The brief does not mention or apologize for missing sources
AND:    The brief reads naturally — no visible gaps, no placeholder sections
```

### B3: Brief Reads in the Citizen's Voice

**Why:** This is what separates MIND from every other AI morning summary. The brief sounds like it comes from someone who knows you — your AI partner, with their personality, their way of speaking, their memory of what you talked about yesterday. Generic AI voice is a failure mode.

```
GIVEN:  A citizen with established personality, communication style, and conversation history
WHEN:   The brief is generated
THEN:   The tone, word choice, and framing reflect the citizen's personality
AND:    References to past conversations feel natural ("remember what you said about X yesterday")
AND:    Two citizens generating briefs for users with identical data produce noticeably different briefs
```

### B4: Brief Is Readable in 60-90 Seconds

**Why:** Morning attention is scarce. Users are groggy, rushed, or both. The brief must be scannable, not a wall of text. If it takes 3 minutes to read, users will skip it. If it takes 30 seconds, it's too shallow to be valuable.

```
GIVEN:  A fully generated brief with all available data sources
WHEN:   The user reads it
THEN:   The brief is 250-400 words (approximately 60-90 seconds reading time)
AND:    Key information (important meeting, bad sleep, urgent email) is in the first 2-3 sentences
AND:    Detail follows in subsequent paragraphs, structured for scanning
```

### B5: Brief Delivered to User's Preferred Surface

**Why:** Users have habits. Some live in Telegram, some in WhatsApp, some open the webapp first. The brief should appear where the user already is, not force them to open a new app.

```
GIVEN:  User has configured a preferred delivery surface (Telegram, WhatsApp, WebApp, push)
WHEN:   The brief is ready for delivery
THEN:   The brief is sent to the preferred surface via the send tool
AND:    If primary delivery fails, the brief is sent to the fallback surface
AND:    The brief is never sent to multiple surfaces simultaneously (no duplicates)
```

### B6: On-Demand Brief When User Asks

**Why:** Sometimes the user misses the morning brief, or wants an updated one mid-day before an important meeting. The same pipeline should serve on-demand requests, reusing the same generation logic but with fresh data.

```
GIVEN:  A user asks their citizen for a brief (e.g., "give me my brief", "what's my day look like")
WHEN:   The intent is recognized as a brief request
THEN:   The brief pipeline runs with current data (not the cached morning brief)
AND:    The brief is delivered in the current conversation context, not as a separate notification
AND:    The brief adjusts for time of day ("your afternoon looks clear" not "good morning")
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1 (Delivery reliability) | Timing is the core product promise. Late = invisible. |
| B2 | O3 (Adapt to partial data) | Most users won't have all 4 sources connected. Brief must work anyway. |
| B3 | O4 (Feels like someone who knows you) | The bond is the moat. Generic AI is competition. |
| B4 | O1 (Delivery reliability) | An unread brief is a failed brief. Readability drives engagement. |
| B5 | O1 (Delivery reliability) | Meet users where they are. Don't add friction. |
| B6 | O2 (4-layer synthesis) | On-demand extends the value beyond the morning window. |

---

## INPUTS / OUTPUTS

### Primary Function: `generate_and_deliver_brief()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| citizen_id | str | The citizen generating the brief |
| user_id | str | The user receiving the brief |
| trigger | enum | `ALARM` (scheduled) or `ON_DEMAND` (user-requested) |
| override_surface | str | None | Optional: force delivery to a specific surface (for on-demand) |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| brief_result | BriefResult | Contains: generated text, sources used, sources unavailable, delivery status, generation time |

**Side Effects:**

- Message sent to delivery surface (Telegram/WhatsApp/WebApp/push)
- Brief stored in citizen's graph as a moment node (conversation history)
- Metrics emitted: generation time, sources used, delivery success

---

## EDGE CASES

### E1: No Data Sources Available (All Integrations Disconnected, No Conversation History)

```
GIVEN:  A new user with zero integrations and no prior conversations
THEN:   The brief is a short introductory message in the citizen's voice
AND:    The citizen introduces itself and suggests connecting data sources
AND:    This only happens on the first 1-3 days — not forever
```

### E2: User Has No Wake Time Configured

```
GIVEN:  User has not set a wake time
THEN:   No alarm-triggered brief is scheduled
AND:    The citizen prompts the user during conversation to set a wake time
AND:    On-demand brief (B6) still works when the user asks
```

### E3: Wake Time Changes Mid-Schedule

```
GIVEN:  User changes wake time after the alarm for the next day is already set
THEN:   The alarm is rescheduled to the new time
AND:    If the old alarm already fired, no duplicate brief is sent
```

### E4: LLM Generation Fails (Timeout, Rate Limit, Service Down)

```
GIVEN:  LLM Router returns an error or times out
THEN:   A pre-composed fallback brief is delivered using structured data (not LLM-generated)
AND:    The fallback is factual: "3 meetings today. 6h sleep. 12 unread emails." — not a narrative
AND:    The fallback is clearly shorter and simpler than a normal brief
```

### E5: Delivery Channel Unreachable (Telegram Down, WhatsApp Error)

```
GIVEN:  Primary delivery surface returns an error
THEN:   Retry once after 30 seconds
AND:    If still failing, deliver to the fallback surface
AND:    If no surface is reachable, store the brief and deliver when connection restores
```

### E6: User Is in a Different Timezone (Traveling)

```
GIVEN:  User's device reports a timezone different from their configured one
THEN:   Use the device timezone for wake time calculation
AND:    The brief content adjusts to local time references ("your 9am meeting here is 3pm Paris time")
```

### E7: Weekend vs Weekday

```
GIVEN:  It's a weekend (or user-defined rest day)
THEN:   The brief is shorter and lighter in tone
AND:    Calendar is de-emphasized, biometrics and conversation memory are emphasized
AND:    No "you have 5 meetings today" energy on a Saturday
```

---

## ANTI-BEHAVIORS

What should NOT happen:

### A1: Brief Sent Multiple Times

```
GIVEN:   Alarm triggers normally
WHEN:    Brief generation and delivery succeed
MUST NOT: Send the brief again (duplicate) if the alarm retries or a race condition occurs
INSTEAD:  Mark the brief as delivered with an idempotency key (date + citizen_id)
```

### A2: Brief Apologizes for Missing Data

```
GIVEN:   Wearable data is unavailable (user doesn't own a wearable)
WHEN:    Brief is generated
MUST NOT: Say "I couldn't access your sleep data" or "connect your wearable for a better brief"
INSTEAD:  Simply skip the biometric section. The brief is complete with what's available.
```

### A3: Brief Gives Health Advice

```
GIVEN:   User slept 3 hours and has high stress
WHEN:    Brief is generated
MUST NOT: Recommend "you should rest today" or "consider rescheduling meetings"
INSTEAD:  Acknowledge the state factually ("rough night") and let the user decide their day
```

### A4: Brief Leaks Raw Data

```
GIVEN:   Brief includes biometric data
WHEN:    Delivered to a potentially shared surface
MUST NOT: Include exact HRV values, raw stress scores, or clinical-sounding metrics
INSTEAD:  Translate to natural language ("you slept well", "your body is still recovering")
```

### A5: Generic AI Voice in Brief

```
GIVEN:   Citizen has an established personality
WHEN:    Brief is generated
MUST NOT: Sound like ChatGPT, Gemini, or any generic AI assistant
INSTEAD:  Sound like the specific citizen with their unique voice, humor, and relational awareness
```

---

## MARKERS

<!-- @mind:todo Define idempotency mechanism for preventing duplicate brief delivery -->
<!-- @mind:todo Clarify timezone handling — device timezone vs configured timezone vs calendar timezone -->
<!-- @mind:proposition Weekend mode as a user-configurable option, not just auto-detected -->
<!-- @mind:escalation E4 (LLM failure fallback) — should the structured fallback include citizen personality at all, or be purely factual? -->
