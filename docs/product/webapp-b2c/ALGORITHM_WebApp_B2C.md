# WebApp B2C -- Algorithm: Application Flows and Logic

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_WebApp_B2C.md
BEHAVIORS:       ./BEHAVIORS_WebApp_B2C.md
PATTERNS:        ./PATTERNS_WebApp_B2C.md
THIS:            ALGORITHM_WebApp_B2C.md (you are here)
VALIDATION:      ./VALIDATION_WebApp_B2C.md
IMPLEMENTATION:  ./IMPLEMENTATION_WebApp_B2C.md
SYNC:            ./SYNC_WebApp_B2C.md

IMPL:            mind-platform/app/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The WebApp B2C is a Next.js 14 App Router application. The "algorithm" here is not a single function -- it is the set of flows that the app executes in response to user actions. Six primary flows cover the full user journey: authentication, chat, brief display, biometric dashboard, model selection, and data export.

Each flow crosses the boundary between client (browser) and server (Next.js API routes / server actions / mind-mcp backend). The logic lives in the transitions: when to fetch server-side vs. client-side, when to stream vs. batch, when to cache vs. refetch.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O2 Zero-friction auth | B1 (30s to chat) | Auth flow determines first-session conversion |
| O3 Chat is primary | B2 (streaming), B4 (history) | Chat flow is the core product interaction |
| O4 Brief is retention | B3 (brief renders) | Brief flow drives daily return visits |
| O5 Biometric dashboard | B5 (charts), B7 (export), B8 (Garmin) | Dashboard flow proves the citizen knows the user's body |
| O6 Model selector | B6 (switch model) | Model flow gives power users agency |

---

## ALGORITHM: Authentication Flow

### Step 1: Provider Selection

User lands on sign-in page. Two options: Google OAuth (one-tap) or email magic link. No username/password form.

```
IF user clicks "Sign in with Google":
    redirect to Google OAuth consent screen
    Google returns authorization code to callback URL
    exchange code for tokens via Auth.js
ELSE IF user enters email:
    generate magic link token (JWT, 15-min expiry)
    send email via configured SMTP / Resend
    user clicks link -> token validated by Auth.js
```

### Step 2: Session Creation

Auth.js creates a session. Session token stored as HTTP-only cookie. Session contains: user ID, email, citizen ID (if paired), auth provider.

```
session = {
    user_id: string (UUID)
    email: string
    citizen_id: string | null  -- null for brand-new users
    provider: "google" | "email"
    expires_at: timestamp (30 days rolling)
}
```

### Step 3: Citizen Pairing Check

```
IF session.citizen_id is null:
    query registry for citizen paired to this user
    IF citizen found:
        update session with citizen_id
    ELSE:
        redirect to onboarding (minimal: name, timezone, wake time)
        after onboarding, assign citizen from matching pool or trigger fallback spawn
```

### Step 4: Redirect to Chat

Session established, citizen paired. Redirect to `/chat`. Middleware on all `/(app)` routes verifies session on every request.

---

## ALGORITHM: Chat Flow

### Step 1: Message Submission

User types message in chat input. Client sends POST to `/api/chat/send`.

```
request = {
    conversation_id: string | null  -- null starts new conversation
    message: string
    model_override: string | null  -- from user preference
}
```

### Step 2: Context Assembly

Server-side, before calling the LLM Router:

```
context = assemble_context(citizen_id, conversation_id)
    -> last N messages from conversation history
    -> citizen personality prompt (from L1 graph)
    -> recent brief summary (if available)
    -> biometric summary (if Garmin connected, last 24h)
    -> user preferences (timezone, communication style)
```

Context assembly is the citizen's "memory" for this conversation turn. It draws from multiple sources but is assembled into a single prompt.

### Step 3: LLM Routing and Streaming

```
stream = llm_router.route(
    model: user_preference or default_for_tier,
    messages: context + user_message,
    stream: true
)
```

Server returns a ReadableStream (via Response API). Client reads chunks and renders tokens incrementally.

### Step 4: Persistence

After stream completes:

```
save_message(conversation_id, role="user", content=user_message)
save_message(conversation_id, role="assistant", content=full_response)
update_conversation_metadata(conversation_id, last_message_at=now())
```

Both messages are persisted. Conversation metadata updated for history ordering.

---

## ALGORITHM: Brief Display Flow

### Step 1: Brief Retrieval (Server Component)

Brief page is a server component. On request:

```
brief = await fetch_brief(citizen_id, date=today)
IF brief is null AND time < wake_time:
    show "Brief arriving at {wake_time}"
    show yesterday's brief as fallback
ELSE IF brief is null AND time >= wake_time:
    show "Brief is being prepared..."
    trigger brief generation if not already queued
ELSE:
    render brief content
```

### Step 2: Brief Rendering

The brief is structured as sections. Each section corresponds to a data source:

```
brief.sections = [
    { type: "relational", content: "..." }     -- citizen's memory of the user
    { type: "calendar", content: "..." }        -- day's schedule
    { type: "biometric", content: "..." }       -- sleep, HRV, recovery
    { type: "email", content: "..." }           -- important emails
]
```

Only sections with data are rendered. Missing sections are silently omitted. The brief adapts its length to available data.

### Step 3: Interaction

User can:
- Tap a section to expand details
- Jump to chat with "Discuss this with your citizen" button
- Navigate to previous briefs by date

---

## ALGORITHM: Biometric Dashboard Flow

### Step 1: Data Retrieval

Dashboard is a client component (charts require client-side rendering).

```
data = await fetch_biometrics(citizen_id, {
    metrics: ["hr", "hrv", "sleep", "stress"],
    range: selected_range,  -- 7 | 30 | 90 days
    granularity: auto       -- hourly for 7d, daily for 30/90d
})
```

### Step 2: Chart Rendering

Four chart panels, each with:

```
for each metric in [HR, HRV, Sleep, Stress]:
    render_chart({
        data: data[metric],
        type: metric.chart_type,    -- line for HR/HRV, stacked bar for sleep stages, area for stress
        zones: metric.zones,        -- green/yellow/red thresholds
        trend: compute_trend(data[metric]),  -- rising, stable, declining
        range: selected_range
    })
```

Zone thresholds per metric:
- **HR resting**: green < 60, yellow 60-80, red > 80
- **HRV**: green > 50ms, yellow 30-50ms, red < 30ms (age-adjusted later)
- **Sleep**: green > 7h, yellow 6-7h, red < 6h
- **Stress**: green < 30, yellow 30-60, red > 60

### Step 3: Trend Computation

```
trend(data, range) =
    IF range == 7d:
        compare average of last 3 days vs previous 4 days
    IF range == 30d:
        compare average of last 7 days vs previous 23 days
    IF range == 90d:
        compare average of last 30 days vs previous 60 days

    delta = recent_avg - earlier_avg
    IF abs(delta) < threshold: return "stable"
    IF delta > 0: return "rising"
    ELSE: return "declining"
```

---

## ALGORITHM: Model Selection Flow

### Step 1: Load Available Models

```
models = await fetch_available_models(user_tier)
    -> returns list of models the user's tier can access
    -> includes: model_id, name, provider, context_window, speed_tier, cost_tier
    -> if BYOAI enabled, includes user's custom model entries
```

### Step 2: Selection

User picks from the list. Selection saved as user preference:

```
save_user_preference(user_id, {
    preferred_model: model_id,
    byoai_key: encrypted_key | null
})
```

### Step 3: Effect on Chat

Next chat message picks up the new model via context assembly. No restart, no reconnection. The change is immediate.

---

## ALGORITHM: Export Flow

### Step 1: Format Selection

```
IF format == "csv":
    data = query_biometrics(citizen_id, date_range, all_metrics)
    csv = serialize_to_csv(data)  -- timestamp, metric_name, value per row
    return Response(csv, content-type: text/csv)

IF format == "pdf":
    data = query_biometrics(citizen_id, date_range, all_metrics)
    charts = render_charts_server_side(data)  -- using a headless renderer
    summary = compute_summary_statistics(data)
    pdf = generate_pdf(charts, summary, metadata)
    return Response(pdf, content-type: application/pdf)
```

### Step 2: Delivery

File downloads in the browser. No email, no async delivery for v0. Under 5 seconds for 90-day range.

---

## KEY DECISIONS

### D1: SSR vs. Client for Each Feature

```
IF feature is mostly static (brief, profile, history list):
    use Server Components
    WHY: faster first paint, less JS shipped, cacheable
ELSE IF feature is interactive (chat, dashboard charts):
    use Client Components
    WHY: needs state, event handlers, real-time updates
```

### D2: Streaming Protocol for Chat

```
IF bidirectional needed (typing indicators, presence):
    WebSocket (future, v2)
ELSE (v0, response streaming only):
    Server-Sent Events (SSE) via ReadableStream
    WHY: simpler, works with Next.js API routes, sufficient for one-directional streaming
```

### D3: Biometric Data Granularity

```
IF range <= 7 days:
    granularity = hourly
    WHY: enough data points for smooth curves without overwhelming
ELSE IF range <= 30 days:
    granularity = daily averages
    WHY: hourly would be 720 points, too dense
ELSE (90 days):
    granularity = daily averages
    WHY: still manageable, trend is the focus not individual hours
```

---

## DATA FLOW

```
User Action (browser)
    |
    v
Next.js Middleware (auth check)
    |
    v
API Route / Server Action / Server Component
    |
    v
mind-mcp Backend (chat, brief, biometrics, registry)
    |
    v
Response (JSON | Stream | SSR HTML)
    |
    v
Client Rendering (React, Recharts)
    |
    v
User Sees Result
```

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| mind-mcp `/api/chat` | Send message + context | Streaming LLM response |
| mind-mcp `/api/brief` | Request brief by date | Brief content (sections) |
| mind-mcp `/api/biometrics` | Request metrics by range | Time-series data |
| mind-mcp `/api/models` | List available models | Model capabilities |
| Garmin Connect API | OAuth2 token exchange | Authorization for data sync |
| Auth.js | Session management | User identity + session token |

---

## MARKERS

<!-- @mind:todo Define exact API contract for mind-mcp endpoints (OpenAPI spec or similar) -->
<!-- @mind:escalation PDF export requires server-side chart rendering -- evaluate puppeteer vs react-pdf vs alternative -->
<!-- @mind:proposition Consider edge caching for brief content since it changes at most once per day -->
