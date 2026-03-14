# WebApp B2C -- Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_WebApp_B2C.md
PATTERNS:        ./PATTERNS_WebApp_B2C.md
BEHAVIORS:       ./BEHAVIORS_WebApp_B2C.md
ALGORITHM:       ./ALGORITHM_WebApp_B2C.md
VALIDATION:      ./VALIDATION_WebApp_B2C.md
IMPLEMENTATION:  ./IMPLEMENTATION_WebApp_B2C.md
THIS:            HEALTH_WebApp_B2C.md (you are here)
SYNC:            ./SYNC_WebApp_B2C.md
```

---

## PURPOSE

This HEALTH file defines runtime verification for the WebApp B2C module. It covers the properties that must be continuously true in production, not just at test time: that auth actually blocks unauthenticated access, that chat actually streams, that biometric data actually refreshes, that briefs actually appear by wake time.

These checks matter because a web app can pass all tests and still fail in production -- sessions expire differently under load, streaming breaks behind certain proxies, Garmin OAuth tokens silently expire, LLM providers go down. Tests verify code logic. Health verifies production behavior.

**Boundaries:** This file covers the webapp surface only. LLM routing health is in the LLM Router module. Brief generation health is in the Brief Matinal module. Garmin data sync health is in the Wearable Bridges module. This module checks what reaches the user's browser.

---

## WHY THIS PATTERN

Frontend health checks are unusual because the "runtime" is someone else's browser. Traditional health checks poll a server endpoint. For a web app, we need to verify:
1. That the server responds correctly (API health)
2. That the client renders correctly (synthetic monitoring)
3. That the integration chain works end-to-end (E2E probes)

Docking-based checks at the API layer catch most issues. Synthetic browser checks (Playwright probes) catch rendering failures. The combination covers the full stack without instrumenting every React component.

---

## IMPLEMENTS

```yaml
implements:
  runtime: mind-platform/health/webapp_b2c_health_checks.ts
  e2e_probes: mind-platform/e2e/health_probes/
  decorator: scheduled (cron-based probes, not event-driven)
```

> **Separation:** This doc defines WHAT to check and WHEN. The health check scripts define HOW.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: chat_message_flow
    purpose: Core product interaction -- if chat fails, the product is dead
    triggers:
      - type: event
        source: app/api/chat/send/route.ts:POST
        notes: Every user message triggers this flow
    frequency:
      expected_rate: 10-50/min (across all users)
      peak_rate: 200/min (high engagement periods)
      burst_behavior: LLM Router queues, may increase latency but should not drop
    risks:
      - V2 (message persistence) -- messages could be lost on API failure
      - V3 (streaming) -- proxy/CDN could buffer stream
    notes: Crosses browser -> API route -> mind-mcp -> LLM provider

  - flow_id: biometric_data_flow
    purpose: Dashboard data freshness -- stale data erodes trust
    triggers:
      - type: event
        source: app/(app)/dashboard/page.tsx (page load)
        notes: Triggered on dashboard navigation
    frequency:
      expected_rate: 1-5/min
      peak_rate: 20/min
      burst_behavior: Garmin API rate limits apply (429 -> cached data shown)
    risks:
      - V4 (data accuracy) -- transformation errors could show wrong values
      - Garmin token expiry could silently break data fetch
    notes: Depends on Garmin API availability

  - flow_id: brief_display_flow
    purpose: Daily retention hook -- if brief is missing at wake time, habit breaks
    triggers:
      - type: schedule
        source: Brief generation runs pre-wake-time, display triggered by page load
        notes: One brief per user per day
    frequency:
      expected_rate: 1/user/day
      peak_rate: all users in same timezone accessing within 30-min window
      burst_behavior: SSR + caching should handle burst
    risks:
      - V5 (brief availability) -- brief generation failure leaves empty page
    notes: Server-side rendered, cacheable per user per day

  - flow_id: auth_flow
    purpose: Security boundary -- if auth fails, everything is exposed
    triggers:
      - type: event
        source: middleware.ts
        notes: Every request to /(app) routes
    frequency:
      expected_rate: matches total request rate
      peak_rate: same as total request peak
      burst_behavior: middleware is lightweight, should not bottleneck
    risks:
      - V1 (auth boundary) -- misconfigured middleware could leak routes
      - V7 (session continuity) -- token rotation could break sessions
    notes: Middleware runs on every request, must be fast
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: auth_boundary_integrity
    flow_id: auth_flow
    priority: high
    rationale: If auth fails, user data is exposed. Must verify unauthenticated requests are blocked.

  - name: chat_stream_latency
    flow_id: chat_message_flow
    priority: high
    rationale: First-token latency determines whether chat feels alive or dead. > 2s = broken.

  - name: chat_message_persistence
    flow_id: chat_message_flow
    priority: high
    rationale: Lost messages break the bond. Must verify messages survive API round-trip.

  - name: biometric_data_freshness
    flow_id: biometric_data_flow
    priority: med
    rationale: Stale dashboard data erodes trust. Must verify sync is recent.

  - name: brief_availability
    flow_id: brief_display_flow
    priority: high
    rationale: Missing brief at wake time breaks the retention loop.

  - name: error_state_quality
    flow_id: all
    priority: med
    rationale: Technical error messages destroy user trust. Must verify errors are human-readable.
```

---

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O2 Zero-friction auth | auth_boundary_integrity | Auth must work AND be secure |
| O3 Chat is primary | chat_stream_latency, chat_message_persistence | Chat quality IS product quality |
| O4 Brief retention | brief_availability | Daily habit requires daily reliability |
| O5 Biometric dashboard | biometric_data_freshness | Dashboard without fresh data is useless |

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: mind-platform/health/status.json
  result:
    representation: enum
    value: PENDING
    updated_at: 2026-03-14T00:00:00Z
    source: not yet implemented
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: auth_boundary_probe
    purpose: Verify unauthenticated requests to /(app) routes return 401/redirect (V1)
    status: pending
    priority: high
  - name: chat_stream_probe
    purpose: Send test message, verify first token within 2s, verify stream (V3)
    status: pending
    priority: high
  - name: chat_persistence_probe
    purpose: Send message, retrieve conversation, verify message exists (V2)
    status: pending
    priority: high
  - name: biometric_freshness_probe
    purpose: Check last_synced timestamp on biometric data (V4)
    status: pending
    priority: med
  - name: brief_availability_probe
    purpose: Check brief exists for today after wake time (V5)
    status: pending
    priority: high
  - name: error_rendering_probe
    purpose: Trigger known error, verify response is human-readable (V8)
    status: pending
    priority: med
```

---

## INDICATOR: auth_boundary_integrity

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: auth_boundary_integrity
  client_value: User data is never exposed to unauthenticated visitors
  validation:
    - validation_id: V1
      criteria: Every /(app) route requires valid session; expired sessions redirect to sign-in
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: 1 = all probed routes return 401/redirect for unauthenticated requests, 0 = at least one route leaks
  aggregation:
    method: all-or-nothing (any leak = 0)
    display: binary
```

### SIGNALS

```yaml
signals:
  healthy: All probed routes block unauthenticated access
  degraded: N/A (this is binary -- either secure or not)
  critical: Any route returns user data without valid session
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: schedule (every 15 minutes)
  max_frequency: 4/hour
  burst_limit: 1
  backoff: immediate alert on first failure, no backoff
```

---

## INDICATOR: chat_stream_latency

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: chat_stream_latency
  client_value: Chat feels responsive and alive, not sluggish
  validation:
    - validation_id: V3
      criteria: First token appears within 2 seconds; tokens render incrementally
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: 1.0 = first token in <500ms, 0.5 = first token in ~2s, 0.0 = >5s or no stream
  aggregation:
    method: rolling average over last 10 probes
    display: float_0_1
```

### SIGNALS

```yaml
signals:
  healthy: Average first-token latency < 2s over last 10 probes
  degraded: Average first-token latency 2-5s (provider slowness or network)
  critical: Average first-token latency > 5s or stream fails entirely
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: schedule (every 5 minutes during active hours, every 30 minutes overnight)
  max_frequency: 12/hour
  burst_limit: 1
  backoff: exponential after 3 consecutive failures
```

---

## HOW TO RUN

```bash
# Run all health probes for webapp-b2c
cd mind-platform && npm run health:check

# Run a specific probe
cd mind-platform && npm run health:check -- --probe auth_boundary_probe
```

---

## KNOWN GAPS

- All checkers are pending (no code written yet)
- Synthetic browser probes (Playwright) not yet designed -- needed for V3 (streaming verification from browser perspective)
- PDF export verification not yet covered
- No probe for session continuity (V7) -- needs multi-step probe (auth, close, reopen)

<!-- @mind:todo Implement auth_boundary_probe first -- highest impact, simplest to build -->
<!-- @mind:todo Design Playwright probes for streaming verification (V3) -->
<!-- @mind:todo Add session continuity probe for V7 -->

---

## MARKERS

<!-- @mind:proposition Consider uptime monitoring service (Better Uptime, Checkly) for external probing in addition to internal health checks -->
<!-- @mind:escalation Health check infrastructure needs to be designed -- where do probes run? Separate service? CI? Cron? -->
