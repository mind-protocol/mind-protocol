# React Native App — Implementation: Code Architecture and Structure

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
ALGORITHM:       ./ALGORITHM_React_Native_App.md
VALIDATION:      ./VALIDATION_React_Native_App.md
THIS:            IMPLEMENTATION_React_Native_App.md (you are here)
HEALTH:          ./HEALTH_React_Native_App.md
SYNC:            ./SYNC_React_Native_App.md

IMPL:            mind-app/ (external repo)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mind-app/
├── app/                                  # Expo Router file-based routing
│   ├── _layout.tsx                       # Root layout (providers, auth guard)
│   ├── index.tsx                         # Welcome/onboarding entry point
│   ├── (auth)/
│   │   └── login.tsx                     # Auth screen (magic link + social)
│   ├── (tabs)/
│   │   ├── _layout.tsx                   # Tab navigator layout
│   │   ├── chat.tsx                      # Chat screen (primary)
│   │   ├── brief.tsx                     # Brief matinal screen
│   │   ├── dashboard.tsx                 # Biometric dashboard screen
│   │   └── profile.tsx                   # Profile screen
│   ├── settings/
│   │   ├── index.tsx                     # Settings hub
│   │   ├── wearable.tsx                  # Wearable connection management
│   │   ├── llm-selector.tsx              # LLM model selector
│   │   └── notifications.tsx             # Notification preferences
│   └── duo/
│       └── index.tsx                     # Duo Mode screen
├── components/
│   ├── chat/
│   │   ├── chat_message_bubble.tsx       # Single message (human or citizen)
│   │   ├── chat_input_bar.tsx            # Text input + send button
│   │   ├── streaming_text_renderer.tsx   # Token-by-token markdown renderer
│   │   └── connection_status_banner.tsx  # WebSocket status indicator
│   ├── brief/
│   │   ├── brief_card.tsx               # Single brief card (swipeable)
│   │   └── brief_card_stack.tsx         # Swipeable card stack container
│   ├── dashboard/
│   │   ├── heart_rate_chart.tsx          # 24h heart rate line chart
│   │   ├── sleep_stage_chart.tsx         # Last night sleep visualization
│   │   ├── steps_bar_chart.tsx           # 7-day step bar chart
│   │   ├── hrv_trend_chart.tsx           # 30-day HRV trend line
│   │   └── empty_dashboard_cta.tsx      # CTA when no wearable connected
│   ├── shared/
│   │   ├── loading_skeleton.tsx          # Skeleton loading states
│   │   ├── error_boundary.tsx            # React error boundary with recovery UI
│   │   └── in_app_notification.tsx       # Foreground notification banner
│   └── onboarding/
│       └── citizen_greeting.tsx          # Citizen's first message animation
├── hooks/
│   ├── use_chat_websocket.ts            # WebSocket connection + streaming logic
│   ├── use_biometric_sync.ts            # HealthKit/Health Connect sync pipeline
│   ├── use_auth.ts                      # Auth state, token refresh, login/logout
│   ├── use_push_notifications.ts        # Notification registration + handlers
│   └── use_citizen_profile.ts           # Citizen data fetching + caching
├── services/
│   ├── api_client.ts                    # REST API client (fetch + auth headers)
│   ├── websocket_manager.ts             # WebSocket lifecycle (connect, heartbeat, reconnect)
│   ├── biometric_platform_bridge.ts     # Platform abstraction: HealthKit vs Health Connect
│   ├── notification_router.ts           # Parse notification payload → navigate to screen
│   └── secure_storage.ts               # Expo SecureStore wrapper for tokens
├── stores/
│   ├── auth_store.ts                    # Zustand: auth state (user, tokens, status)
│   ├── chat_store.ts                    # Zustand: messages, conversation state
│   └── sync_store.ts                    # Zustand: biometric sync state
├── types/
│   ├── biometric.ts                     # BiometricSample, SyncState types
│   ├── chat.ts                         # ChatMessage, WebSocketEvent types
│   ├── notification.ts                  # NotificationPayload type
│   └── api.ts                          # API request/response types
├── constants/
│   ├── biometric_bounds.ts              # Plausibility thresholds per data type
│   ├── notification_limits.ts           # Max daily notifications, priority rules
│   └── app_config.ts                   # API URLs, WebSocket URLs, feature flags
├── app.json                             # Expo configuration
├── eas.json                             # EAS Build configuration
├── tsconfig.json                        # TypeScript configuration
└── package.json                         # Dependencies
```

### File Responsibilities

| File | Purpose | Key Exports | Status |
|------|---------|-------------|--------|
| `app/_layout.tsx` | Root layout: providers, auth guard, navigation | RootLayout | PLANNED |
| `hooks/use_chat_websocket.ts` | WebSocket connection, streaming, reconnection | useChatWebSocket() | PLANNED |
| `hooks/use_biometric_sync.ts` | Full sync pipeline: fetch, filter, upload | useBiometricSync() | PLANNED |
| `services/biometric_platform_bridge.ts` | Abstracts HealthKit vs Health Connect | BiometricBridge | PLANNED |
| `services/websocket_manager.ts` | WebSocket lifecycle management | WebSocketManager | PLANNED |
| `services/notification_router.ts` | Notification payload → screen navigation | routeNotification() | PLANNED |
| `stores/auth_store.ts` | Auth state: user, tokens, login/logout | useAuthStore | PLANNED |
| `stores/chat_store.ts` | Chat state: messages, streaming, conversation | useChatStore | PLANNED |

**Size Thresholds:**
- **OK** (<400 lines): Healthy size, easy to understand
- **WATCH** (400-700 lines): Getting large, consider extraction opportunities
- **SPLIT** (>700 lines): Too large, must split before adding more code

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Feature-based with Hooks + Services + Stores

**Why this pattern:** Expo Router gives us file-based routing (screens are the entry points). Hooks encapsulate reusable logic (WebSocket, sync, auth). Services handle external communication (API, health platform, storage). Stores manage cross-screen state (Zustand). This separation makes each layer testable in isolation.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Platform Bridge | `biometric_platform_bridge.ts` | Single interface for HealthKit (iOS) and Health Connect (Android) |
| Observer (hooks) | `use_chat_websocket.ts` | Component subscribes to WebSocket events via hook |
| Repository | `api_client.ts` | Centralized API access with auth header injection |
| State Machine | `websocket_manager.ts` | Connection states: connecting, connected, disconnecting, closed, error |
| Error Boundary | `error_boundary.tsx` | Catches unhandled exceptions, shows recovery UI |

### Anti-Patterns to Avoid

- **God Screen**: Don't put business logic in screen components. Screens compose hooks and render components. Logic lives in hooks/services.
- **Platform Conditionals in Components**: Don't scatter `Platform.OS === 'ios'` through UI code. All platform branching happens in `biometric_platform_bridge.ts`.
- **Direct Fetch in Components**: Don't call `fetch()` from components. All API calls go through `api_client.ts` which handles auth, retry, and error formatting.
- **Mutable Refs for State**: Don't use `useRef` to track state that affects rendering. State that drives UI goes in Zustand stores or local `useState`.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Platform Health API | HealthKit/Health Connect native calls | All app code | `BiometricBridge.querySamples()` |
| Auth | Token storage, refresh logic | Screen components | `useAuth()` hook |
| API | HTTP requests, error handling | UI components | `api_client.get/post/put()` |
| WebSocket | Connection lifecycle, reconnection | Chat UI | `useChatWebSocket()` hook |

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| App launch | `app/_layout.tsx` | User opens app |
| Tab navigation | `app/(tabs)/_layout.tsx` | User taps tab bar |
| Push notification tap | `services/notification_router.ts` | User taps notification |
| Background biometric sync | `hooks/use_biometric_sync.ts` | OS background fetch timer |
| Deep link | `app/_layout.tsx` | External URL scheme |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Chat Message Flow: Human sends message, citizen responds

This flow covers the core interaction loop: human types a message, it's sent via WebSocket, the citizen's response streams back token-by-token. This flow is high-impact (the primary feature) and crosses the WebSocket boundary.

```yaml
flow:
  name: chat_message_exchange
  purpose: Deliver human message to citizen and stream response
  scope: Chat screen to mind-platform API via WebSocket
  steps:
    - id: user_types
      description: User composes message in chat input bar
      file: components/chat/chat_input_bar.tsx
      function: onSend()
      input: string (message text)
      output: void (dispatches to store)
      trigger: User taps send button
      side_effects: Message added to chat_store with status "sending"
    - id: ws_send
      description: Message sent over WebSocket
      file: services/websocket_manager.ts
      function: send()
      input: ChatMessage (serialized JSON)
      output: void
      trigger: chat_store dispatch
      side_effects: Network I/O
    - id: stream_receive
      description: Citizen response tokens arrive
      file: hooks/use_chat_websocket.ts
      function: onMessage handler
      input: WebSocketEvent (stream_start | stream_token | stream_end)
      output: void (updates chat_store)
      trigger: WebSocket message event
      side_effects: chat_store updated with each token
    - id: render_token
      description: UI renders each token as it arrives
      file: components/chat/streaming_text_renderer.tsx
      function: React render cycle
      input: message.content (accumulating string)
      output: Rendered markdown
      trigger: chat_store state change
      side_effects: Auto-scroll to bottom
  docking_points:
    guidance:
      include_when: WebSocket boundary, state mutation, user-visible output
      omit_when: Pure UI rendering without state change
    available:
      - id: dock_ws_send
        type: stream
        direction: output
        file: services/websocket_manager.ts
        function: send()
        trigger: chat_store dispatch
        payload: ChatMessage JSON
        async_hook: not_applicable
        needs: none
        notes: Outbound message — verify delivery
      - id: dock_ws_receive
        type: stream
        direction: input
        file: hooks/use_chat_websocket.ts
        function: onMessage
        trigger: WebSocket message event
        payload: WebSocketEvent JSON
        async_hook: not_applicable
        needs: none
        notes: Inbound tokens — verify ordering and completeness
    health_recommended:
      - dock_id: dock_ws_send
        reason: Outbound messages must be acknowledged — silent drops break V2
      - dock_id: dock_ws_receive
        reason: Token ordering verification protects V2 (message integrity)
```

### Biometric Sync Flow: Wearable data reaches citizen graph

This flow is critical because it crosses two boundaries: native health API and remote API. Data transformation (plausibility filtering) happens in between. Integrity failure means the citizen misreads its human's body.

```yaml
flow:
  name: biometric_sync_pipeline
  purpose: Move health data from wearable → native API → app → mind-platform → citizen graph
  scope: HealthKit/Health Connect to mind-platform API
  steps:
    - id: native_query
      description: Query HealthKit or Health Connect for new samples
      file: services/biometric_platform_bridge.ts
      function: querySamples()
      input: { types, startDate, endDate }
      output: BiometricSample[]
      trigger: Foreground mount or background fetch timer
      side_effects: Native API read
    - id: plausibility_filter
      description: Remove implausible values
      file: hooks/use_biometric_sync.ts
      function: filterPlausible()
      input: BiometricSample[]
      output: BiometricSample[] (filtered)
      trigger: After native_query completes
      side_effects: Filtered samples logged locally
    - id: api_upload
      description: POST samples to mind-platform API
      file: services/api_client.ts
      function: post("/biometrics/sync", payload)
      input: { citizen_id, samples, platform, sync_timestamp }
      output: { synced_count, new_timestamp }
      trigger: After filter completes
      side_effects: Network I/O, sync_store updated
  docking_points:
    guidance:
      include_when: Boundary crossing, data transformation, integrity risk
      omit_when: Internal state updates without external effect
    available:
      - id: dock_native_health_read
        type: api
        direction: input
        file: services/biometric_platform_bridge.ts
        function: querySamples()
        trigger: sync interval or screen mount
        payload: BiometricSample[]
        async_hook: required
        needs: none
        notes: Native API boundary — permission state may change between calls
      - id: dock_filter_output
        type: custom
        direction: output
        file: hooks/use_biometric_sync.ts
        function: filterPlausible()
        trigger: after native query
        payload: BiometricSample[] (filtered)
        async_hook: not_applicable
        needs: none
        notes: Data quality gate — protects V7
      - id: dock_api_upload
        type: api
        direction: output
        file: services/api_client.ts
        function: post()
        trigger: after filter
        payload: BiometricSyncRequest
        async_hook: not_applicable
        needs: none
        notes: Auth token required — protects V3 and V5
    health_recommended:
      - dock_id: dock_native_health_read
        reason: Permission state changes break the pipeline silently
      - dock_id: dock_api_upload
        reason: Biometric data reaching wrong citizen is CRITICAL (V3)
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
app/ (screens)
    └── imports → hooks/ (business logic)
        └── imports → services/ (external communication)
            └── imports → types/ (shared type definitions)
    └── imports → components/ (UI elements)
        └── imports → stores/ (state management)
    └── imports → constants/ (configuration)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `expo` ~54 | Managed workflow runtime | Root |
| `expo-router` | File-based navigation | `app/` |
| `expo-notifications` | Push notification registration + handling | `hooks/use_push_notifications.ts` |
| `expo-secure-store` | Encrypted token storage | `services/secure_storage.ts` |
| `expo-background-fetch` | Background biometric sync | `hooks/use_biometric_sync.ts` |
| `react-native-health` | HealthKit integration (iOS) | `services/biometric_platform_bridge.ts` |
| `react-native-health-connect` | Health Connect integration (Android) | `services/biometric_platform_bridge.ts` |
| `zustand` | UI state management | `stores/` |
| `@tanstack/react-query` | Server state caching + refetch | `hooks/` |
| `victory-native` or `recharts` | Biometric charts | `components/dashboard/` |
| `react-native-markdown-display` | Chat message markdown rendering | `components/chat/` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Auth (user, tokens) | `stores/auth_store.ts` + SecureStore | Global | App lifetime, persisted |
| Chat messages | `stores/chat_store.ts` | Per-conversation | Session, refetched on mount |
| Biometric sync state | `stores/sync_store.ts` | Global | Persisted (last_sync timestamp) |
| Server data (briefs, profile) | TanStack Query cache | Global | Cached with TTL |
| UI state (modals, form inputs) | Component `useState` | Local | Component lifetime |

### State Transitions

```
Auth: logged_out ──login──> logged_in ──token_expire──> refreshing ──success──> logged_in
                                                                    ──fail──> logged_out

WebSocket: closed ──mount──> connecting ──open──> connected ──error──> reconnecting ──open──> connected
                                                             ──unmount──> closing ──close──> closed

Sync: idle ──trigger──> syncing ──success──> idle
                                ──error──> error ──retry──> syncing
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Expo loads app/_layout.tsx
2. AuthProvider checks SecureStore for existing tokens
3. If tokens exist → validate with API → if valid → navigate to (tabs)
4. If no tokens or invalid → show Welcome/Login
5. Register push notification token with API
6. Start background biometric sync task
```

### Main Loop / Request Cycle

```
1. User interacts (tap, type, navigate)
2. Screen dispatches to hook
3. Hook calls service (API, WebSocket, health bridge)
4. Service returns data or stream
5. Hook updates store
6. React re-renders affected components
```

### Shutdown

```
1. App backgrounded → WebSocket moves to background mode (reduced heartbeat)
2. App killed → background fetch tasks continue independently
3. On next launch → full reinitialization from step 1
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| UI rendering | React single thread (JS) | Standard React Native bridge |
| WebSocket | Async (event-driven) | Non-blocking, handled in JS thread |
| Health API queries | Async (native bridge) | Runs on native thread, returns to JS |
| Background fetch | OS-managed task | Runs independently of app state |
| API calls | Async (Promise-based) | TanStack Query manages concurrency |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `API_BASE_URL` | `constants/app_config.ts` | `https://api.mind-protocol.com` | mind-platform API endpoint |
| `WS_URL` | `constants/app_config.ts` | `wss://api.mind-protocol.com/ws` | WebSocket endpoint |
| `SYNC_INTERVAL_MS` | `constants/app_config.ts` | `900000` (15 min) | Background biometric sync interval |
| `MAX_DAILY_NOTIFICATIONS` | `constants/notification_limits.ts` | `3` | Default push notification cap |
| `HR_BOUNDS` | `constants/biometric_bounds.ts` | `[30, 220]` | Heart rate plausibility range (bpm) |
| `STEPS_DAILY_MAX` | `constants/biometric_bounds.ts` | `100000` | Max plausible daily step count |
| `HRV_BOUNDS` | `constants/biometric_bounds.ts` | `[1, 300]` | HRV plausibility range (ms) |

---

## MARKERS

<!-- @mind:todo Define EAS Build profiles for development, staging, and production -->
<!-- @mind:todo Set up Sentry for crash reporting and performance monitoring -->
<!-- @mind:escalation Chart library decision (Victory Native vs Recharts) needs benchmarking on mid-range Android -->
<!-- @mind:proposition Consider expo-updates for OTA updates to bypass app store review for non-native changes -->
