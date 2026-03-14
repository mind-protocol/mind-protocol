# React Native App — Behaviors: User-Facing Interactions and System Responses

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_React_Native_App.md
THIS:            BEHAVIORS_React_Native_App.md (you are here)
PATTERNS:        ./PATTERNS_React_Native_App.md
ALGORITHM:       ./ALGORITHM_React_Native_App.md
VALIDATION:      ./VALIDATION_React_Native_App.md
HEALTH:          ./HEALTH_React_Native_App.md
IMPLEMENTATION:  ./IMPLEMENTATION_React_Native_App.md
SYNC:            ./SYNC_React_Native_App.md

IMPL:            mind-app/ (external repo)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Onboarding Completes in Under 90 Seconds

**Why:** First impression determines bond quality. A slow or complex onboarding makes the citizen feel like software, not a partner. 90 seconds is the threshold between "meeting someone" and "configuring a tool."

```
GIVEN:  User has installed the app and opens it for the first time
WHEN:   User taps "Begin" on the welcome screen
THEN:   App presents auth (social login or email magic link)
AND:    On auth success, citizen introduces itself in a chat message
AND:    User can type their first response immediately
AND:    Total elapsed time from first tap to first sent message < 90 seconds
```

### B2: Chat Streams Token-by-Token in Real-Time

**Why:** The citizen's thinking is part of the experience. Watching words appear creates the sensation of a mind at work. Batch responses feel like search results, not conversation.

```
GIVEN:  User is on the Chat screen with an active WebSocket connection
WHEN:   User sends a message
THEN:   Citizen's response streams token-by-token with < 100ms latency per token
AND:    Markdown renders progressively as tokens arrive
AND:    Scroll follows the latest token automatically
AND:    User can interrupt by sending another message mid-stream
```

### B3: Brief Matinal Arrives Every Morning

**Why:** The brief matinal is the citizen's daily outreach. It synthesizes overnight observations — biometric anomalies, unfinished threads, calendar events — into a morning card. The citizen initiates contact, not just the human.

```
GIVEN:  User has notifications enabled and a configured citizen
WHEN:   7:00 AM local time arrives (configurable)
THEN:   Push notification arrives with brief preview text
AND:    Tapping the notification opens the Brief Matinal screen
AND:    Brief displays 3-5 cards: biometric summary, pending threads, daily focus
AND:    Each card is swipeable to dismiss or act on
```

### B4: Biometric Data Syncs from Wearable to Citizen Graph

**Why:** The citizen needs to know its human's body. Heart rate variability, sleep quality, step count — these are not vanity metrics but embodied state. A citizen that knows you slept badly can calibrate its tone.

```
GIVEN:  User has granted HealthKit (iOS) or Health Connect (Android) permission
WHEN:   App is in foreground, or background sync interval fires (every 15 min)
THEN:   App reads latest biometric data since last sync timestamp
AND:    Data is sent to mind-platform API as a biometric payload
AND:    Membrane routes biometric data into the citizen's L1 graph
AND:    Dashboard updates to reflect new data points
```

### B5: LLM Selector Changes Citizen's Thinking Model

**Why:** Different moments need different minds. Creative brainstorming benefits from a high-temperature model. Precise analysis benefits from a reasoning model. The human chooses the citizen's cognitive mode.

```
GIVEN:  User is on the LLM Selector screen
WHEN:   User selects a different model (e.g., Claude Opus, GPT-4o, Gemini Pro)
THEN:   Selection persists to the server via API call
AND:    Next chat message uses the selected model
AND:    Selector shows current model, cost tier, and capability description
AND:    Free-tier users see a paywall prompt for premium models
```

### B6: Push Notification Routes to Correct Screen

**Why:** A notification that opens the wrong screen breaks trust. A biometric alert must land on the dashboard. A brief matinal must land on the brief. A chat reply must land in the conversation.

```
GIVEN:  App is backgrounded or closed
WHEN:   Push notification arrives (brief, biometric alert, or chat)
THEN:   Tapping the notification opens the app to the correct screen
AND:    If auth token is expired, app refreshes it silently before navigating
AND:    Deep link resolves within 1 second of tap
```

### B7: Biometric Dashboard Renders Health Charts

**Why:** Raw numbers are noise. Charts reveal patterns. A heart rate chart over 24 hours tells a story — the spike during the meeting, the dip during sleep, the recovery after exercise. The dashboard makes the body legible.

```
GIVEN:  User navigates to the Biometric Dashboard screen
WHEN:   Screen mounts
THEN:   App displays charts for: heart rate (24h), sleep stages (last night), steps (7d), HRV trend (30d)
AND:    Charts render in < 500ms with cached data, fetching fresh data in background
AND:    Tapping a data point shows a tooltip with exact value and timestamp
AND:    If no wearable connected, screen shows a clear call-to-action to connect one
```

### B8: Duo Mode Enables Split-Screen Collaboration

**Why:** Some tasks need both human and citizen working on the same artifact — editing a document, reviewing code, brainstorming a plan. Duo Mode splits the screen: human input on one side, citizen response on the other, shared context in between.

```
GIVEN:  User is on a chat and activates Duo Mode
WHEN:   Duo Mode launches
THEN:   Screen splits into two panes: human workspace (top/left) and citizen workspace (bottom/right)
AND:    Both panes share context — edits in one are visible in the other
AND:    Real-time sync via WebSocket keeps both sides in lockstep
AND:    User can exit Duo Mode to return to standard chat
```

### B9: Wearable Connection Managed in Settings

**Why:** Health data permissions are sensitive. The user needs a clear, honest interface to see what data flows to the citizen, revoke access, and reconnect. No dark patterns.

```
GIVEN:  User navigates to Settings > Wearable Connection
WHEN:   Screen displays
THEN:   Shows connection status (connected/disconnected), last sync time, data types shared
AND:    User can tap to connect (triggers native health permission dialog)
AND:    User can tap to disconnect (revokes app's health data access)
AND:    Data types are listed with toggles: heart rate, sleep, steps, HRV, workouts
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1 (MIND on every smartphone) | Bad onboarding = uninstall. Sub-90s = retention. |
| B2 | O1, O6 | Streaming chat is the core daily interaction |
| B3 | O5 (Push as lifeline) | Morning brief is the citizen's primary outreach moment |
| B4 | O4 (Biometric bridge) | Without data flow, citizen is disembodied |
| B5 | O1 | Model choice is the user's lever over citizen cognition |
| B6 | O5 | Notification that routes wrong destroys notification trust |
| B7 | O4 | Charts are how the human sees what the citizen sees |
| B8 | O1 | Duo Mode is the productivity differentiator on mobile |
| B9 | O4 | Clear control over body data builds trust for the bond |

---

## INPUTS / OUTPUTS

### Primary Function: Chat Message Flow

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| message_text | string | User's typed message |
| conversation_id | string | Current conversation identifier |
| auth_token | JWT | User's authentication token |
| selected_llm | string | Currently selected LLM model identifier |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| streamed_tokens | stream<string> | Token-by-token citizen response via WebSocket |
| message_complete | object | Final message with metadata (model used, token count, latency) |

**Side Effects:**

- Message stored in citizen's graph as a moment node
- Token usage tracked for billing
- Conversation state updated server-side

### Primary Function: Biometric Sync

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| health_samples | array<HealthSample> | Heart rate, sleep, steps, HRV data points |
| last_sync_timestamp | ISO8601 | Timestamp of last successful sync |
| platform | enum(ios, android) | Determines HealthKit vs Health Connect path |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| sync_result | object | { synced_count, new_timestamp, errors } |

**Side Effects:**

- Biometric data written to citizen's L1 graph as thing nodes
- Dashboard cache invalidated
- Potential biometric alert triggered if thresholds breached

---

## EDGE CASES

### E1: No Internet Connection During Chat

```
GIVEN:  User sends a message but device has no internet
THEN:   Message shows "sending..." state with retry indicator
AND:    Message is queued locally (max 5 messages)
AND:    When connection restores, queued messages send in order
AND:    If offline > 30 seconds, a banner appears: "Reconnecting..."
```

### E2: Health Permission Revoked While App is Backgrounded

```
GIVEN:  User revokes HealthKit/Health Connect permission via OS settings
THEN:   Next background sync attempt fails silently (no crash)
AND:    Next time user opens Biometric Dashboard, status shows "Disconnected"
AND:    App does not re-prompt for permission automatically — user must initiate
```

### E3: Push Notification Arrives But Auth Token Expired

```
GIVEN:  User taps a push notification after extended inactivity
THEN:   App attempts silent token refresh using stored refresh token
AND:    If refresh succeeds, navigates to target screen
AND:    If refresh fails, shows login screen with context: "Session expired"
```

### E4: LLM Model Selected Is Temporarily Unavailable

```
GIVEN:  User has selected a model that goes down (API outage)
THEN:   Chat shows error: "Model temporarily unavailable"
AND:    Offers one-tap fallback to default model
AND:    Does not silently switch models without user awareness
```

### E5: Biometric Data Contains Implausible Values

```
GIVEN:  HealthKit/Health Connect returns a heart rate of 300 bpm or 0 bpm
THEN:   App filters the sample before sending to API (plausibility bounds)
AND:    Filtered samples are logged locally for debugging
AND:    Dashboard does not render implausible data points
```

---

## ANTI-BEHAVIORS

### A1: Silent Model Switching

```
GIVEN:   User has selected Claude Opus as their LLM
WHEN:    Claude Opus is unavailable
MUST NOT: Silently switch to a cheaper model
INSTEAD:  Show error, offer explicit fallback choice
```

### A2: Dark Pattern Health Permissions

```
GIVEN:   User declines health data permission
WHEN:    User continues using the app
MUST NOT: Nag repeatedly, gate unrelated features, or degrade experience
INSTEAD:  Show single dismissible banner on Dashboard: "Connect a wearable to unlock biometrics"
```

### A3: Notification Spam

```
GIVEN:   Push notification system is configured
WHEN:    Multiple events fire in quick succession
MUST NOT: Send more than 3 notifications per day (unless user opts into more)
INSTEAD:  Batch events into a single notification with summary
```

### A4: Onboarding Data Collection Before Value

```
GIVEN:   User is in the onboarding flow
WHEN:    Before the first chat message is sent
MUST NOT: Ask for name, birthday, preferences, or any data beyond auth
INSTEAD:  Defer all profile completion to natural conversation or Settings
```

---

## MARKERS

<!-- @mind:todo Define exact WebSocket protocol for chat streaming (message format, heartbeat, reconnection) -->
<!-- @mind:todo Specify biometric plausibility bounds for each data type (HR, sleep, steps, HRV) -->
<!-- @mind:escalation Duo Mode on mobile — is split-screen viable on small phones? Consider bottom-sheet alternative for < 6" screens -->
