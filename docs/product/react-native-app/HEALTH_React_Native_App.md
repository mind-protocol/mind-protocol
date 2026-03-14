# React Native App — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_React_Native_App.md
PATTERNS:        ./PATTERNS_React_Native_App.md
BEHAVIORS:       ./BEHAVIORS_React_Native_App.md
ALGORITHM:       ./ALGORITHM_React_Native_App.md
VALIDATION:      ./VALIDATION_React_Native_App.md
IMPLEMENTATION:  ./IMPLEMENTATION_React_Native_App.md
THIS:            HEALTH_React_Native_App.md (you are here)
SYNC:            ./SYNC_React_Native_App.md
```

---

## PURPOSE OF THIS FILE

This HEALTH file covers the React Native App module — the mobile client through which humans interact with their citizens. It verifies that the app delivers on its core promises: fast onboarding, reliable chat, correct biometric data flow, and proper push notification routing.

This file exists because a mobile app operates in hostile conditions — unreliable networks, OS-level background killing, permission revocations, and device fragmentation. Tests verify logic in isolation; health checks verify the system behaves correctly in the real world.

**Boundaries:** This file verifies app-side behavior only. API-side validation (does the biometric data actually reach the graph?) belongs in mind-platform's health checks. This file covers: client sends correctly, client routes correctly, client performs acceptably.

---

## WHY THIS PATTERN

Tests pass in CI but the app crashes on a Pixel 6 with Android 14. Tests mock WebSocket connections but real reconnection logic fails under 3G. Tests filter biometric samples correctly but the native bridge returns unexpected data shapes on Health Connect API v2.

Docking-based health checks verify behavior at real boundaries — the WebSocket wire, the native health bridge, the notification routing logic — without requiring full integration test infrastructure. Throttling prevents these checks from draining battery or flooding monitoring.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: chat_message_exchange
    purpose: If chat fails, the citizen is unreachable — the core product is broken
    triggers:
      - type: event
        source: components/chat/chat_input_bar.tsx:onSend
        notes: User taps send button, initiating WebSocket exchange
    frequency:
      expected_rate: 10-50 messages/day per user
      peak_rate: 5 messages/min during active conversation
      burst_behavior: WebSocket handles burst natively; no backpressure needed on client
    risks:
      - WebSocket drops silently under network transition (WiFi ↔ cellular) — V2
      - Token rendering out of order on reconnection — V2
      - Message marked "sent" but never acknowledged — V2
    notes: WebSocket boundary is the primary risk — everything else is local state

  - flow_id: biometric_sync_pipeline
    purpose: If sync fails silently, citizen operates without body awareness — biometric features become theater
    triggers:
      - type: schedule
        source: hooks/use_biometric_sync.ts (background fetch)
        notes: OS-triggered background task every ~15 minutes
      - type: event
        source: app/(tabs)/dashboard.tsx mount
        notes: Foreground sync on dashboard screen open
    frequency:
      expected_rate: 4-6 syncs/hour (background) + on-demand (foreground)
      peak_rate: 10/hour during active use with dashboard open
      burst_behavior: Sync is idempotent — duplicate uploads are handled server-side by timestamp dedup
    risks:
      - Permission silently revoked between syncs — V3
      - Native bridge returns malformed data on OS update — V7
      - Auth token expires during background sync — V5
    notes: Crosses two boundaries (native health API + remote API), making it the highest-risk pipeline

  - flow_id: push_notification_routing
    purpose: If notifications route to wrong screen, user loses trust in notifications and disables them — citizen loses outreach channel
    triggers:
      - type: external
        source: Firebase Cloud Messaging / APNs
        notes: Server sends notification, OS delivers to app
    frequency:
      expected_rate: 1-3/day per user
      peak_rate: 5/day (opt-in users)
      burst_behavior: Server-side throttling enforces limits; app receives whatever arrives
    risks:
      - Deep link resolves to nonexistent screen after app update — V4
      - Auth token expired on notification tap, redirect loop — V4, V5
    notes: Notification routing is low-frequency but high-impact per event
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1 (MIND on every smartphone) | onboarding_time, cold_start_perf | If the app is slow to start or onboard, users uninstall |
| O2 (One codebase) | platform_parity | Divergence between iOS and Android means half the users are underserved |
| O4 (Biometric bridge) | biometric_sync_health, biometric_data_quality | Body data must flow correctly or the citizen is disembodied |
| O5 (Push notifications) | notification_routing_accuracy | Wrong routing trains users to ignore notifications |

```yaml
health_indicators:
  - name: chat_delivery_integrity
    flow_id: chat_message_exchange
    priority: high
    rationale: Every undelivered or misordered message erodes bond trust. Users cannot verify message state independently.

  - name: biometric_sync_health
    flow_id: biometric_sync_pipeline
    priority: high
    rationale: Silent sync failures mean the citizen lacks body awareness. User sees stale dashboard data without realizing sync is broken.

  - name: biometric_data_quality
    flow_id: biometric_sync_pipeline
    priority: med
    rationale: Implausible data corrupts citizen's understanding. Less critical than sync failure but degrades experience over time.

  - name: notification_routing_accuracy
    flow_id: push_notification_routing
    priority: high
    rationale: Each misrouted notification is a trust violation. Low frequency means each event is high-leverage.

  - name: cold_start_perf
    flow_id: chat_message_exchange
    priority: med
    rationale: Slow cold start makes users avoid opening the app. 2-second threshold is the line between native and web feel.

  - name: crash_free_rate
    flow_id: chat_message_exchange
    priority: high
    rationale: Crashes during chat feel like the citizen died. Below 99.5% crash-free means frequent user-visible failures.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: docs/product/react-native-app/HEALTH_React_Native_App.md
  result:
    representation: enum
    value: PENDING
    updated_at: 2026-03-14T00:00:00Z
    source: manual
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: chat_ws_delivery
    purpose: Verify WebSocket messages are acknowledged and tokens arrive in order (V2)
    status: pending
    priority: high
  - name: biometric_sync_success_rate
    purpose: Verify biometric sync completes without silent failure (V3, V7)
    status: pending
    priority: high
  - name: notification_deep_link_resolution
    purpose: Verify notification payloads route to correct screens (V4)
    status: pending
    priority: high
  - name: cold_start_time
    purpose: Verify time-to-interactive < 2 seconds on mid-range devices (V9)
    status: pending
    priority: med
  - name: crash_monitoring
    purpose: Verify crash-free session rate > 99.5% (V10)
    status: pending
    priority: high
  - name: plausibility_filter_coverage
    purpose: Verify implausible biometric values never reach the API (V7)
    status: pending
    priority: med
```

---

## INDICATOR: chat_delivery_integrity

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: chat_delivery_integrity
  client_value: Every message the human sends reaches the citizen. Every response the citizen generates reaches the human. No silent drops.
  validation:
    - validation_id: V2
      criteria: Every sent message is acknowledged; tokens render in order; status reflects true state
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum:
      OK: All messages acknowledged, tokens in order, no drops in last 24h
      WARN: 1-2 unacknowledged messages or reconnection events in last 24h
      ERROR: Messages dropped, tokens misordered, or WebSocket unable to reconnect
  aggregation:
    method: Worst-case across all active conversations
    display: enum surfaced in monitoring dashboard
```

### SIGNALS

```yaml
signals:
  healthy: All messages sent in the last session were acknowledged. Zero reconnections needed. Token order matches server sequence.
  degraded: 1-2 reconnections occurred. All messages eventually delivered. Minor token reordering corrected by client-side buffering.
  critical: Messages dropped permanently. WebSocket unable to reconnect for > 60 seconds. Token rendering showed visible reordering.
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: Per-session check on WebSocket close or app background
  max_frequency: 1 check per 5 minutes
  burst_limit: 3 checks per session
  backoff: Linear — if check fails, wait 30s before recheck
```

---

## INDICATOR: biometric_sync_health

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: biometric_sync_health
  client_value: User's wearable data actually reaches their citizen. Dashboard reflects real body state, not stale cache.
  validation:
    - validation_id: V3
      criteria: Biometric data reaches correct citizen, authenticated by valid token
    - validation_id: V5
      criteria: Auth tokens used during sync are valid and securely stored
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
    - float_0_1
  semantics:
    enum:
      OK: Last 10 syncs all succeeded
      WARN: 1-2 sync failures in last 10 attempts
      ERROR: 3+ consecutive sync failures or permission revoked
    float_0_1: success_count / total_attempts over last 24h
  aggregation:
    method: Float score for trending, enum for alerting
    display: enum on dashboard settings, float in monitoring
```

### SIGNALS

```yaml
signals:
  healthy: All sync attempts in the last 24h succeeded. Permissions granted. Data reaching API.
  degraded: Some sync failures due to transient network issues. Retries recovering. No permission change.
  critical: Sync repeatedly failing. Permission revoked. Or auth token expired during background sync with no recovery.
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: After each sync attempt (background or foreground)
  max_frequency: 1 check per 15 minutes (matches sync interval)
  burst_limit: 6 checks per hour
  backoff: Exponential — if sync consistently failing, reduce check frequency to avoid battery drain
```

---

## HOW TO RUN

```bash
# No runtime health checks exist yet — module is in DESIGNING status
# When implemented, health checks will run via:

# Run all health checks for React Native App
npx jest --testPathPattern='__health__' --config=jest.health.config.js

# Run biometric sync health check specifically
npx jest --testPathPattern='biometric_sync_health' --config=jest.health.config.js
```

---

## KNOWN GAPS

- V1 (Onboarding speed) — No automated timing measurement. Needs Detox e2e test with stopwatch.
- V4 (Notification routing) — Needs real device testing. Simulators don't fully replicate notification tap behavior.
- V8 (Platform parity) — Needs side-by-side screenshot comparison or visual regression tool.
- V9 (Cold start perf) — Needs real device profiling. Expo Dev Client measurements are not representative.
- V10 (Crash-free rate) — Depends on Sentry/Crashlytics integration (not yet set up).

<!-- @mind:todo Set up Sentry for crash monitoring to enable crash_free_rate checker -->
<!-- @mind:todo Build Detox e2e test for onboarding timing measurement -->
<!-- @mind:todo Implement biometric sync health check as the first active checker -->

---

## MARKERS

<!-- @mind:todo All checkers are pending — first implementation target is biometric_sync_health -->
<!-- @mind:proposition Consider Flipper plugin for real-time health indicator display during development -->
<!-- @mind:escalation Real-device testing infrastructure needed — simulators are insufficient for health checks involving HealthKit/Health Connect -->
