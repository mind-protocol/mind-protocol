# React Native App — Algorithm: Screen Flows, Data Pipelines, and Sync Logic

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_React_Native_App.md
BEHAVIORS:       ./BEHAVIORS_React_Native_App.md
PATTERNS:        ./PATTERNS_React_Native_App.md
THIS:            ALGORITHM_React_Native_App.md (you are here)
VALIDATION:      ./VALIDATION_React_Native_App.md
HEALTH:          ./HEALTH_React_Native_App.md
IMPLEMENTATION:  ./IMPLEMENTATION_React_Native_App.md
SYNC:            ./SYNC_React_Native_App.md

IMPL:            mind-app/ (external repo)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The React Native app has three major algorithmic pipelines: the onboarding flow (auth to first message), the biometric sync pipeline (wearable to citizen graph), and the push notification routing system (server event to correct screen). Each pipeline crosses the boundary between native platform APIs and the mind-platform backend. The app's logic is primarily orchestration — calling the right API at the right time and rendering the response correctly.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O3 (Onboarding < 90s) | B1 | Minimizes steps between install and first chat |
| O4 (Biometric bridge) | B4, B7 | Moves health data from native API to citizen graph |
| O5 (Push notifications) | B3, B6 | Routes server events to correct screen with correct context |
| O2 (One codebase) | B4 | Platform abstraction layer handles HealthKit vs Health Connect |

---

## DATA STRUCTURES

### BiometricSample

```
BiometricSample {
  type: enum(heart_rate, sleep_stage, steps, hrv, workout)
  value: float
  unit: string                    // "bpm", "minutes", "count", "ms"
  timestamp: ISO8601
  source: string                  // device identifier
  platform: enum(ios, android)
}
```

### SyncState

```
SyncState {
  last_sync_timestamp: ISO8601    // persisted in AsyncStorage
  pending_samples: BiometricSample[]  // queued if network unavailable
  sync_status: enum(idle, syncing, error)
  connection_status: enum(connected, disconnected, permission_revoked)
}
```

### NotificationPayload

```
NotificationPayload {
  type: enum(brief_matinal, biometric_alert, chat_reply, upsell)
  target_screen: string           // Expo Router path
  params: Record<string, string>  // screen-specific parameters
  citizen_voice: string           // notification body text in citizen's voice
  priority: enum(high, default, low)
}
```

### ChatMessage

```
ChatMessage {
  id: string                      // UUID
  conversation_id: string
  role: enum(human, citizen)
  content: string                 // markdown
  model_used: string | null       // which LLM generated this (null for human)
  timestamp: ISO8601
  status: enum(sending, sent, streaming, complete, error)
}
```

---

## ALGORITHM: Onboarding Flow

### Step 1: Welcome Screen

User sees the citizen's greeting and a single CTA: "Begin." No feature tour, no carousel. One screen, one button.

### Step 2: Authentication

```
IF user has existing account:
    Show email magic link or social login (Google/Apple)
    On success → receive JWT + refresh token
    Store tokens in Expo SecureStore
ELSE:
    Show sign-up (email or social)
    On success → create account via mind-platform API
    API creates citizen and returns JWT
    Store tokens in Expo SecureStore
```

### Step 3: First Message

```
Navigate to Chat screen
Citizen sends its first message automatically (server-triggered on new account)
Message streams token-by-token
User sees text input ready for their first reply
```

Total screens: 2 (Welcome, Chat). Auth is a modal overlay, not a separate screen.

---

## ALGORITHM: Biometric Sync Pipeline

### Step 1: Platform Detection and Permission Check

```
platform = detect_platform()   // ios or android

IF platform == ios:
    health_api = HealthKit
    permission_types = [heartRate, sleepAnalysis, stepCount, heartRateVariability]
ELSE:
    health_api = HealthConnect
    permission_types = [HeartRate, SleepSession, Steps, HeartRateVariability]

permission_status = await health_api.check_permissions(permission_types)

IF permission_status == not_determined:
    // Do nothing — wait for user to initiate from Settings
    return
IF permission_status == denied:
    update_sync_state(connection_status: permission_revoked)
    return
```

### Step 2: Data Fetch

```
last_sync = await AsyncStorage.get("last_biometric_sync")
now = Date.now()

// Fetch all sample types since last sync
samples = []
FOR EACH type IN permission_types:
    IF type.is_granted:
        new_samples = await health_api.query(
            type,
            start: last_sync || (now - 24h),
            end: now,
            limit: 1000
        )
        samples.append(...new_samples)

// Filter implausible values
samples = samples.filter(s => plausibility_check(s))
```

### Step 3: Plausibility Filter

```
plausibility_check(sample):
    MATCH sample.type:
        heart_rate:    return 30 <= sample.value <= 220
        steps:         return 0 <= sample.value <= 100000  // per day
        hrv:           return 1 <= sample.value <= 300      // ms
        sleep_stage:   return sample.value IN valid_stages
        workout:       return sample.duration <= 24h
```

### Step 4: Upload to API

```
IF samples.length == 0:
    update_sync_state(sync_status: idle, last_sync: now)
    return

update_sync_state(sync_status: syncing)

TRY:
    response = await api.post("/biometrics/sync", {
        citizen_id: current_user.citizen_id,
        samples: samples,
        platform: platform,
        sync_timestamp: now
    })
    update_sync_state(
        sync_status: idle,
        last_sync: now,
        pending_samples: []
    )
CATCH network_error:
    update_sync_state(
        sync_status: error,
        pending_samples: samples   // queue for retry
    )
```

### Step 5: Background Sync Scheduling

```
// Register background task (runs every 15 minutes)
TaskManager.defineTask("biometric-sync", async () => {
    await biometric_sync_pipeline()
    return BackgroundFetch.Result.NewData
})

BackgroundFetch.registerTaskAsync("biometric-sync", {
    minimumInterval: 15 * 60,      // 15 minutes
    stopOnTerminate: false,
    startOnBoot: true
})
```

---

## ALGORITHM: Push Notification Routing

### Step 1: Token Registration

```
ON app_launch:
    push_token = await Notifications.getExpoPushTokenAsync()
    device_token = await Notifications.getDevicePushTokenAsync()

    await api.post("/notifications/register", {
        citizen_id: current_user.citizen_id,
        expo_token: push_token,
        device_token: device_token,     // raw FCM or APNs token
        platform: platform
    })
```

### Step 2: Notification Reception

```
// Foreground handler — app is open
Notifications.addNotificationReceivedListener((notification) => {
    payload = parse_notification_payload(notification)

    MATCH payload.type:
        brief_matinal:     show_in_app_banner(payload.citizen_voice)
        biometric_alert:   show_in_app_alert(payload.citizen_voice)
        chat_reply:        // already on chat screen — just update
        upsell:            show_in_app_banner(payload.citizen_voice)
})

// Background/closed handler — user tapped notification
Notifications.addNotificationResponseReceivedListener((response) => {
    payload = parse_notification_payload(response.notification)

    // Ensure auth is valid
    IF auth_token_expired():
        success = await refresh_auth_token()
        IF NOT success:
            navigate("/login", { returnTo: payload.target_screen })
            return

    navigate(payload.target_screen, payload.params)
})
```

### Step 3: Notification Frequency Governance

```
// Server-side enforcement (not in app — documented for context)
daily_count = count_notifications_sent_today(citizen_id)

IF daily_count >= 3 AND NOT user.opted_into_more:
    queue_notification_for_tomorrow(payload)
    return

// Priority override: biometric alerts always send
IF payload.type == biometric_alert AND payload.priority == high:
    send_immediately(payload)
    return
```

---

## ALGORITHM: Chat WebSocket Management

### Step 1: Connection Establishment

```
ON chat_screen_mount:
    ws = new WebSocket(WS_URL, {
        headers: { Authorization: `Bearer ${auth_token}` }
    })

    ws.on("open", () => {
        set_connection_status("connected")
        send_heartbeat_interval = setInterval(() => ws.ping(), 30_000)
    })

    ws.on("close", (code) => {
        set_connection_status("disconnected")
        IF code != 1000:  // abnormal close
            schedule_reconnect(backoff: exponential, max: 30s)
    })
```

### Step 2: Message Sending

```
send_message(text):
    message = ChatMessage {
        id: uuid(),
        conversation_id: current_conversation,
        role: "human",
        content: text,
        status: "sending"
    }
    append_to_local_state(message)

    ws.send(JSON.stringify({
        type: "message",
        conversation_id: current_conversation,
        content: text,
        model: selected_llm
    }))

    // Optimistic: mark as sent
    update_message_status(message.id, "sent")
```

### Step 3: Streaming Response

```
ws.on("message", (data) => {
    event = JSON.parse(data)

    MATCH event.type:
        "stream_start":
            citizen_message = ChatMessage {
                id: event.message_id,
                role: "citizen",
                content: "",
                model_used: event.model,
                status: "streaming"
            }
            append_to_local_state(citizen_message)

        "stream_token":
            append_token_to_message(event.message_id, event.token)
            scroll_to_bottom()

        "stream_end":
            update_message_status(event.message_id, "complete")
            update_message_metadata(event.message_id, {
                token_count: event.token_count,
                latency_ms: event.latency_ms
            })

        "error":
            show_error_toast(event.message)
            update_message_status(event.message_id, "error")
})
```

---

## KEY DECISIONS

### D1: Expo Managed vs Bare Workflow

```
IF we need full native build control (custom Swift/Kotlin):
    Use bare workflow — more flexibility, more maintenance
ELSE:
    Use managed workflow — Expo handles builds, updates, signing
    CHOSEN: Managed workflow with config plugins for health modules
    WHY: Build infrastructure is Expo's problem, not ours
```

### D2: Background Sync Interval

```
IF user has app foregrounded:
    Sync biometrics on screen mount (real-time)
ELSE:
    Background fetch every 15 minutes
    WHY: Apple limits background execution. 15 min is the minimum reliable interval.
    More frequent polling drains battery and gets throttled by iOS.
```

### D3: Chart Library Selection

```
IF we need high-performance native charts:
    Victory Native — SVG-based, React Native optimized
ELSE IF we need web-compatible charting:
    Recharts via react-native-svg — shared with WebApp
    TRADE-OFF: Decide based on shared design system constraint
```

### D4: State Management

```
IF global state is complex (many cross-screen dependencies):
    Zustand — lightweight, no boilerplate, TypeScript-native
ELSE IF server state dominates:
    TanStack Query — cache, refetch, optimistic updates
    CHOSEN: TanStack Query for server state + Zustand for UI state
    WHY: 90% of app state is server-derived (chat, biometrics, profile)
```

---

## DATA FLOW

```
User Input (chat, settings, navigation)
    |
    v
React Components (screens)
    |
    v
State Management (Zustand UI state + TanStack Query server state)
    |
    v
API Layer (REST for mutations, WebSocket for streaming)
    |
    v
mind-platform API
    |
    v
Membrane (MCP tools)
    |
    v
Citizen Graph (L1) + LLM
```

```
Wearable (Apple Watch, Fitbit, etc.)
    |
    v
HealthKit / Health Connect (OS-level)
    |
    v
Platform Abstraction Layer (mind-app)
    |
    v
BiometricSyncPipeline
    |
    v
mind-platform API POST /biometrics/sync
    |
    v
Citizen Graph (thing nodes)
```

---

## COMPLEXITY

**Chat streaming:** O(n) where n = tokens in response. Linear, bounded by LLM output limits. No performance concern.

**Biometric sync:** O(m) where m = health samples since last sync. Bounded by 15-min interval and 1000-sample cap per query. Worst case: 6 sample types x 1000 = 6000 samples per sync. Acceptable.

**Push notification routing:** O(1) per notification. Parse payload, navigate. No computation.

**Bottlenecks:**
- WebSocket reconnection under poor network: exponential backoff prevents thundering herd but can delay messages by up to 30s
- HealthKit/Health Connect query on first sync (24h of data): may take 1-2 seconds on data-rich users. Show loading indicator.
- Chart rendering with 30 days of HR data (~43,000 points): requires downsampling to ~500 points for smooth rendering

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| mind-platform API | POST /auth/login | JWT + refresh token |
| mind-platform API | WebSocket /chat | Streaming chat tokens |
| mind-platform API | POST /biometrics/sync | Sync confirmation |
| mind-platform API | GET /briefs/today | Brief matinal content |
| mind-platform API | PUT /settings/llm | LLM selection persistence |
| HealthKit (iOS) | HKSampleQuery | BiometricSample[] |
| Health Connect (Android) | readRecords() | BiometricSample[] |
| Expo Notifications | getExpoPushTokenAsync() | Push token string |
| Expo SecureStore | getItemAsync/setItemAsync | JWT storage |

---

## MARKERS

<!-- @mind:todo Define WebSocket message protocol schema (TypeScript types for all event.type values) -->
<!-- @mind:todo Specify chart downsampling algorithm (LTTB vs simple averaging vs min-max bucketing) -->
<!-- @mind:proposition Consider react-native-mmkv instead of AsyncStorage for sync state — 30x faster reads -->
<!-- @mind:escalation Background fetch reliability on iOS — Apple's 15-min minimum is not guaranteed. Need fallback strategy for critical biometric alerts. -->
