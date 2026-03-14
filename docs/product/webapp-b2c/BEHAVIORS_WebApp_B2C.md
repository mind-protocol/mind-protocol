# WebApp B2C -- Behaviors: Observable Effects

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_WebApp_B2C.md
THIS:            BEHAVIORS_WebApp_B2C.md (you are here)
PATTERNS:        ./PATTERNS_WebApp_B2C.md
ALGORITHM:       ./ALGORITHM_WebApp_B2C.md
VALIDATION:      ./VALIDATION_WebApp_B2C.md
IMPLEMENTATION:  ./IMPLEMENTATION_WebApp_B2C.md
SYNC:            ./SYNC_WebApp_B2C.md

IMPL:            mind-platform/app/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: New User Reaches Chat in Under 30 Seconds

**Why:** The first session determines whether a user comes back. Every second of friction between "I want to try MIND" and "I'm talking to my citizen" is a user lost. Auth must be invisible, onboarding minimal, chat immediate.

```
GIVEN:  User arrives at the app for the first time
WHEN:   User clicks "Sign in with Google" or enters email for magic link
THEN:   Auth completes and user lands on chat interface
AND:    Total elapsed time from landing page to chat is under 30 seconds
AND:    If new user, a default citizen is assigned (or onboarding collects minimal info)
```

### B2: Chat Message Gets Streaming Response

**Why:** The chat is the bond. Latency kills intimacy. The user types, the citizen responds -- immediately, word by word, like a real conversation. Not a loading spinner followed by a wall of text.

```
GIVEN:  Authenticated user on chat page
WHEN:   User sends a message
THEN:   Streaming response begins within 2 seconds
AND:    Tokens appear incrementally (not buffered)
AND:    Message is persisted to conversation history
AND:    Citizen personality and context are reflected in response tone
```

### B3: Morning Brief Renders on First Visit

**Why:** The brief is the retention hook. It must be visible, prominent, and fast. When the user opens the app in the morning, the brief is already there -- not loading, not computing, already rendered.

```
GIVEN:  User opens the app after their configured wake time
WHEN:   Brief page loads (or brief card on chat page)
THEN:   Brief content renders within 1 second (server-side rendered)
AND:    Brief shows all available sections (memory, calendar, biometrics, relational)
AND:    Missing data sources are omitted silently (no "connect your Garmin" nagging)
```

### B4: Returning User Sees Conversation History

**Why:** The bond accumulates through memory. A citizen that forgets yesterday's conversation is not a partner. The user must see continuity -- past conversations accessible, searchable, persistent.

```
GIVEN:  Authenticated user with previous conversations
WHEN:   User navigates to history or opens chat
THEN:   Previous conversations are listed in reverse chronological order
AND:    User can search conversations by keyword
AND:    Clicking a conversation loads its full content
AND:    Current conversation continues where last session left off
```

### B5: Biometric Dashboard Shows Garmin Data

**Why:** The citizen knows your body. The dashboard proves it. HR trends, HRV patterns, sleep quality, stress levels -- rendered as charts the user can actually read and interpret. Not raw numbers, not a data table.

```
GIVEN:  User has connected Garmin account via OAuth
WHEN:   User navigates to dashboard
THEN:   Charts render for HR, HRV, sleep, and stress
AND:    Default view is 7 days, switchable to 30 and 90
AND:    Trend lines show directional change
AND:    Color zones indicate healthy/warning/alert ranges
AND:    Data loads within 3 seconds
```

### B6: User Switches LLM Model

**Why:** Power users want control. Some prefer Claude's reasoning, some prefer GPT's speed, some bring their own API key. The selector must be clear about what each model offers without requiring AI expertise.

```
GIVEN:  Authenticated user on profile or settings page
WHEN:   User selects a different LLM model from the selector
THEN:   Selection is saved immediately
AND:    Next chat message uses the selected model
AND:    If BYOAI, user can enter their own API key
AND:    Model capabilities (context window, speed, cost tier) are visible
```

### B7: Biometric Data Exports Successfully

**Why:** Users need their data for coaches, doctors, personal tracking. Export is a trust feature -- it proves the data is theirs, not locked in. CSV for data-literate users, PDF for sharing with non-technical recipients.

```
GIVEN:  User is on biometric dashboard with data loaded
WHEN:   User clicks export and selects format (CSV or PDF)
THEN:   File downloads within 5 seconds
AND:    CSV contains all visible data points with headers
AND:    PDF contains charts as rendered plus summary statistics
AND:    Date range of export matches the currently selected view
```

### B8: Garmin Connection Flow Completes

**Why:** The wearable connection is a one-time setup that unlocks the biometric layer. If the OAuth flow is confusing or broken, the user never connects, and the citizen never learns their body.

```
GIVEN:  User navigates to profile and clicks "Connect Garmin"
WHEN:   OAuth2 flow redirects to Garmin and user authorizes
THEN:   Redirect returns to app with confirmation
AND:    Garmin data begins syncing within 60 seconds
AND:    Dashboard becomes available with initial data
AND:    Connection status shows "Connected" with last sync time
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1 (Product surface), O2 (Zero-friction auth) | First impression determines retention |
| B2 | O1 (Product surface), O3 (Chat is primary) | Chat quality IS product quality |
| B3 | O4 (Brief is retention hook) | Daily habit formation requires reliability |
| B4 | O3 (Chat is primary) | Memory continuity deepens the bond |
| B5 | O5 (Biometric dashboard) | Health visibility differentiates MIND from other AI |
| B6 | O6 (Model selector) | User agency builds trust |
| B7 | O5 (Biometric dashboard) | Data portability builds trust |
| B8 | O5 (Biometric dashboard) | Wearable connection enables biometric layer |

---

## EDGE CASES

### E1: Magic Link Expires

```
GIVEN:  User clicks a magic link email after the token expires (15 min default)
THEN:   Error page shows "Link expired" with one-click resend
AND:    No cryptic error messages or redirect loops
```

### E2: Garmin API Rate Limited

```
GIVEN:  Garmin API returns 429 during sync
THEN:   Dashboard shows cached data with "Last synced: X hours ago"
AND:    Background retry with exponential backoff
AND:    No error displayed to user unless data is older than 24 hours
```

### E3: LLM Provider Down During Chat

```
GIVEN:  Selected LLM provider fails mid-stream
THEN:   Router falls back to next provider (per LLM Router module)
AND:    User sees brief indicator "Switched model" but conversation continues
AND:    No message is lost
```

### E4: Empty Conversation History

```
GIVEN:  New user with no conversation history
THEN:   Chat page shows a welcome message from the citizen
AND:    History section shows "Start your first conversation"
AND:    No empty state that looks broken
```

### E5: Brief Not Yet Generated

```
GIVEN:  User opens app before their wake time (brief not generated yet)
THEN:   Brief section shows "Your brief will be ready at {wake_time}"
AND:    Previous day's brief is still accessible
```

---

## ANTI-BEHAVIORS

### A1: Unauthenticated Access to User Data

```
GIVEN:   Unauthenticated request to any feature route
WHEN:    Middleware checks session
MUST NOT: Render any user data, conversation, or biometric content
INSTEAD:  Redirect to sign-in page
```

### A2: Chat Without Streaming

```
GIVEN:   Any chat interaction
WHEN:    Response is generated
MUST NOT: Buffer entire response and display at once
INSTEAD:  Stream tokens incrementally as they arrive
```

### A3: Biometric Dashboard Shows Stale Data Without Indicator

```
GIVEN:   Garmin sync has not completed in over 6 hours
WHEN:    User views dashboard
MUST NOT: Show charts without staleness indicator
INSTEAD:  Show "Last synced: X hours ago" prominently
```

### A4: Error Messages Expose Technical Details

```
GIVEN:   Any API error
WHEN:    Error is displayed to user
MUST NOT: Show stack traces, error codes, or internal service names
INSTEAD:  Show human-readable error with actionable suggestion
```

---

## MARKERS

<!-- @mind:todo Define the citizen assignment flow for new users -- is it immediate or requires onboarding? -->
<!-- @mind:escalation What is the minimum data required for a first morning brief? Can it generate with conversation history only? -->
<!-- @mind:proposition Consider "citizen typing" indicator in chat to increase perceived responsiveness -->
