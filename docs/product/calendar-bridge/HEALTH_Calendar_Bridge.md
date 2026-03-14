# Calendar Bridge — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Sync freshness drift | A sync cycle that silently stops running won't be caught by unit tests |
| Token expiration patterns | Real OAuth tokens expire on unpredictable schedules |
| Provider availability | CalDAV server downtime or Google API quota exhaustion are runtime conditions |
| Event count anomalies | A calendar that suddenly drops from 50 events/week to 0 suggests a broken sync, not an empty schedule |

**Tests gate completion. Health monitors runtime.**

---

## PURPOSE OF THIS FILE

This HEALTH file covers the Calendar Bridge module's runtime verification. It exists to detect silent sync failures, stale graph state, and provider degradation that unit tests cannot catch because they depend on real API responses over time.

**Boundaries:** This file verifies that calendar data flows correctly from providers to graph. It does not verify downstream consumers (Brief Matinal health is in its own HEALTH file). It does not verify OAuth infrastructure (that's the auth module's health concern).

---

## WHY THIS PATTERN

Calendar sync is a background process. If it breaks, nothing crashes. No exception reaches a user. The graph just quietly stops updating. The human doesn't notice until they ask "why didn't you remind me about my meeting?" and by then trust is damaged. Health checks catch the silence.

Docking-based checks work here because the sync loop has clear input (API response) and output (graph nodes) boundaries. We can verify the pipeline without modifying the sync code by observing what enters and exits.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Calendar_Bridge.md
PATTERNS:        ./PATTERNS_Calendar_Bridge.md
BEHAVIORS:       ./BEHAVIORS_Calendar_Bridge.md
ALGORITHM:       ./ALGORITHM_Calendar_Bridge.md
VALIDATION:      ./VALIDATION_Calendar_Bridge.md
IMPLEMENTATION:  ./IMPLEMENTATION_Calendar_Bridge.md
THIS:            HEALTH_Calendar_Bridge.md (you are here)
SYNC:            ./SYNC_Calendar_Bridge.md
```

---

## IMPLEMENTS

This HEALTH file is a **spec**. The actual code lives in runtime:

```yaml
implements:
  runtime: mind-mcp/runtime/checks/calendar_bridge_health_checks.py
  decorator: @check
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: calendar_sync_loop
    purpose: "Core sync pipeline -- if this fails, the citizen's schedule goes stale"
    triggers:
      - type: schedule
        source: runtime/scheduler
        notes: "Fires every 5 minutes (configurable CALENDAR_SYNC_INTERVAL)"
    frequency:
      expected_rate: 12/hour per provider
      peak_rate: 12/hour (capped by interval)
      burst_behavior: "No bursting -- fixed interval. If a cycle takes >5min, next cycle is skipped (lock held)."
    risks:
      - "Silent failure: token expires, sync stops, graph goes stale (V5)"
      - "Partial sync: API pagination error drops events from later pages (V1)"
      - "Stale state: provider API changes response format, normalization silently produces empty fields (V2)"
    notes: "Three provider types share this flow. Each citizen may have 1-3 providers configured."

  - flow_id: graph_injection
    purpose: "Events written to L1 graph as moment nodes -- if this fails, fetched events are lost"
    triggers:
      - type: event
        source: runtime/integrations/calendar/sync.py:apply_to_graph
        notes: "Triggered by diff_events producing non-empty create/update/delete lists"
    frequency:
      expected_rate: "Proportional to calendar activity: 1-5 events/day for typical human"
      peak_rate: "20-30 events in first sync (full calendar load)"
      burst_behavior: "First sync is bursty; subsequent syncs are incremental (1-3 events per cycle)"
    risks:
      - "Duplicate nodes from concurrent sync (V4)"
      - "Orphaned attendee links if event is deleted but links remain (V3)"
    notes: "Graph ops are the final boundary -- after this, data is in the graph for consumers."
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| MIND knows your schedule | sync_freshness, event_count_sanity | If sync is stale or event count drops to zero, the citizen is schedule-blind |
| Three providers cover 100% | provider_availability | If a provider goes down and we don't detect it, that user segment loses coverage |
| Calendar feeds downstream | graph_event_integrity | If events are in the graph but malformed, downstream consumers produce garbage |

```yaml
health_indicators:
  - name: sync_freshness
    flow_id: calendar_sync_loop
    priority: high
    rationale: "Detects silent sync death. If last_sync_time is >3x the expected interval, something is wrong."

  - name: provider_availability
    flow_id: calendar_sync_loop
    priority: high
    rationale: "Detects provider-side failures (API down, quota exceeded, server unreachable). Distinguished from auth failures."

  - name: event_count_sanity
    flow_id: graph_injection
    priority: med
    rationale: "Detects anomalous drops in synced event count. A calendar going from 40 events to 0 is likely a bug, not an empty schedule."

  - name: graph_event_integrity
    flow_id: graph_injection
    priority: med
    rationale: "Spot-checks that moment nodes have required fields populated (title, start_time, end_time). Catches normalization regressions."
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: mind-mcp/runtime/checks/results/calendar_bridge.json
  result:
    representation: enum
    value: UNKNOWN
    updated_at: 2026-03-14T00:00:00Z
    source: sync_freshness
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: sync_freshness_checker
    purpose: "Verify last_sync_time is within expected bounds for each configured provider (V1, V5)"
    status: pending
    priority: high
  - name: provider_availability_checker
    purpose: "Verify each configured provider is reachable and responding (V5, V8)"
    status: pending
    priority: high
  - name: event_count_sanity_checker
    purpose: "Compare current event count against rolling 7-day average, flag >80% drops (V1)"
    status: pending
    priority: med
  - name: graph_event_integrity_checker
    purpose: "Sample 10 random calendar moment nodes, verify required fields non-null (V2)"
    status: pending
    priority: med
```

---

## INDICATOR: sync_freshness

Detects when a calendar sync has silently stopped running. This is the highest-priority health signal because the failure mode is invisible -- no error, no crash, just a graph that quietly stops updating.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: sync_freshness
  client_value: "Human's AI partner has up-to-date schedule awareness. Stale = wrong meeting prep."
  validation:
    - validation_id: V1
      criteria: "Every source event reaches the graph within a sync cycle"
    - validation_id: V5
      criteria: "Token failure surfaces, never hides"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum:
      OK: "Last sync within 2x expected interval (default: last 10 minutes)"
      WARN: "Last sync between 2x and 5x expected interval (10-25 minutes)"
      ERROR: "Last sync beyond 5x expected interval (>25 minutes) or no sync recorded"
  aggregation:
    method: "Worst-of across all configured providers per citizen"
    display: enum
```

### SIGNALS

```yaml
signals:
  healthy: "All configured providers synced within 2x interval"
  degraded: "One or more providers last synced 2x-5x interval ago"
  critical: "One or more providers last synced >5x interval ago or never synced"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: schedule
  max_frequency: 1/5min
  burst_limit: 1
  backoff: "No backoff needed -- runs on fixed schedule alongside sync loop"
```

---

## INDICATOR: provider_availability

Detects when a specific calendar provider is down or unreachable, distinguishing between auth failures (token problem) and provider failures (API down).

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: provider_availability
  client_value: "Distinguishes 'reconnect your calendar' (auth) from 'provider is having issues' (wait)."
  validation:
    - validation_id: V5
      criteria: "Token failure surfaces, never hides"
    - validation_id: V8
      criteria: "CalDAV works without provider-specific code"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum:
      OK: "Provider responded successfully on last sync attempt"
      WARN: "Provider returned a transient error (rate limit, timeout) on last attempt"
      ERROR: "Provider returned auth error or 3+ consecutive failures"
  aggregation:
    method: "Per-provider, then worst-of for citizen-level view"
    display: enum
```

### SIGNALS

```yaml
signals:
  healthy: "All configured providers responding normally"
  degraded: "One provider returning transient errors but still syncing"
  critical: "One or more providers returning auth errors or persistently unreachable"
```

---

## HOW TO RUN

```bash
# Run all calendar bridge health checks
mind doctor --module calendar-bridge

# Run a specific checker
mind doctor --checker sync_freshness_checker
```

---

## KNOWN GAPS

- No checker yet for cross-provider deduplication accuracy (V4 adjacent)
- No checker for recurrence expansion correctness (V6) -- hard to verify at runtime without source-of-truth comparison

<!-- @mind:todo Implement sync_freshness_checker as first health check -->
<!-- @mind:todo Implement provider_availability_checker with distinction between auth and API errors -->
<!-- @mind:todo Design event_count_sanity_checker with 7-day rolling average baseline -->

---

## MARKERS

<!-- @mind:todo All checkers are pending -- implement during S7-S8 alongside the bridge code -->
<!-- @mind:proposition Consider a unified "bridge health" pattern shared across calendar, email, and wearable bridges -->
