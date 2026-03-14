# Wearable Bridges — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## PURPOSE OF THIS FILE

This HEALTH file covers the Wearable Bridges module: the sync pipeline that fetches body data from wearable devices (via aggregator APIs and on-device health stores), normalizes it, deduplicates it, and writes it to the citizen's graph.

It exists because wearable sync is inherently unreliable — APIs go down, tokens expire, rate limits hit, devices disconnect. Tests verify logic; health checks verify that data is actually flowing in production. A test can confirm deduplication logic works; only a health check can confirm that Garmin hasn't revoked our API access.

**Boundaries:** This file verifies data pipeline health (fetch, normalize, dedup, write). It does not verify downstream consumers (Brief Matinal's use of body data, citizen reasoning quality). Those belong to their own HEALTH files.

---

## WHY THIS PATTERN

The failure mode this pattern avoids: tests pass, code deploys, but no body data reaches the graph because a token silently expired, a rate limit changed, or Health Connect permissions were revoked. These are runtime failures invisible to tests.

Docking-based checks are the right tradeoff because the pipeline has clear stages (fetch, normalize, dedup, write) with measurable inputs and outputs at each stage. We can verify health by comparing stage outputs without modifying pipeline code.

Throttling protects against alert storms during expected API maintenance windows.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Wearable_Bridges.md
PATTERNS:        ./PATTERNS_Wearable_Bridges.md
BEHAVIORS:       ./BEHAVIORS_Wearable_Bridges.md
ALGORITHM:       ./ALGORITHM_Wearable_Bridges.md
VALIDATION:      ./VALIDATION_Wearable_Bridges.md
IMPLEMENTATION:  ./IMPLEMENTATION_Wearable_Bridges.md
THIS:            HEALTH_Wearable_Bridges.md (you are here)
SYNC:            ./SYNC_Wearable_Bridges.md
```

---

## IMPLEMENTS

This HEALTH file is a **spec**. The actual code lives in runtime:

```yaml
implements:
  runtime: runtime/integrations/wearables/health_checks.py
  decorator: @check
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update runtime or add TODO to SYNC.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: cloud_api_sync
    purpose: If this flow fails, citizens with Garmin (and post-launch direct API) devices get no body data in their graph — the citizen is blind to physiology
    triggers:
      - type: schedule
        source: sync_pipeline_fetch_normalize_dedup_write.py:run_sync_cycle
        notes: Hourly cron triggers sync for all active citizens
    frequency:
      expected_rate: 1/hour per citizen
      peak_rate: 1/hour per citizen (scheduler-controlled, no bursts)
      burst_behavior: No bursts expected — scheduler is rate-controlled. API rate limits provide backpressure.
    risks:
      - OAuth2 token expiry without successful refresh (V4)
      - Garmin API rate limit changes (undocumented limits)
      - API response schema changes breaking normalization (V1)
      - Network failures during fetch (V3)
    notes: Each citizen's sync is independent — one failure doesn't cascade (V3)

  - flow_id: on_device_bridge
    purpose: If this flow fails, citizens with Apple Watch / Android wearables get no body data — the largest market segments (~95% combined with Garmin) are dark
    triggers:
      - type: event
        source: healthkit_bridge_adapter.py:receive_healthkit_data (or health_connect equivalent)
        notes: Triggered by HTTP POST from mind-app after on-device sync
    frequency:
      expected_rate: 1-4/hour per citizen (app background refresh interval varies by OS)
      peak_rate: 10/hour per citizen (user opens app multiple times, force-refreshes)
      burst_behavior: App may batch samples — a single POST can contain 50-500 samples covering hours of data
    risks:
      - mind-app fails to send data (app crash, background task killed by OS)
      - Malformed samples bypass validation (V1, V7)
      - Network timeout during large batch POST
    notes: On-device data arrives in batches, not real-time. A 6-hour silence is normal if user's phone was in airplane mode.
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1 (MIND knows your body) | data_flow_active, graph_nodes_written | If either is unhealthy, body data is not reaching the graph — the core promise is broken |
| O2 (95% coverage at launch) | source_auth_healthy, bridge_receiving | If auth fails or bridges stop receiving, entire market segments lose coverage |
| O3 (Typed nodes, not raw metrics) | normalization_valid | If normalization breaks, raw vendor data enters the graph — downstream reasoning breaks |

```yaml
health_indicators:
  - name: data_flow_active
    flow_id: cloud_api_sync
    priority: high
    rationale: Confirms at least one successful sync per source in the last 2 hours. If no data flows, the module has silently stopped working.

  - name: graph_nodes_written
    flow_id: cloud_api_sync
    priority: high
    rationale: Confirms body data nodes are actually persisted in the graph after sync. A sync can "succeed" (no errors) but write zero nodes if normalization silently drops everything.

  - name: source_auth_healthy
    flow_id: cloud_api_sync
    priority: high
    rationale: Monitors OAuth2 token status across all cloud sources. An expired token means zero data from that source until manually re-authenticated.

  - name: bridge_receiving
    flow_id: on_device_bridge
    priority: high
    rationale: Confirms the on-device bridge endpoints are receiving data from mind-app. If the bridge stops receiving, Apple Watch and Android wearable users are dark.

  - name: normalization_valid
    flow_id: cloud_api_sync
    priority: med
    rationale: Tracks the ratio of successfully normalized samples vs dropped/invalid samples. A spike in normalization failures indicates an API schema change.

  - name: dedup_ratio
    flow_id: cloud_api_sync
    priority: low
    rationale: Monitors what fraction of samples are deduplicated. A sudden change (0% to 50% or 50% to 0%) indicates either a new overlapping source or a broken source.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: runtime/integrations/wearables/health_checks.py
  result:
    representation: enum
    value: PENDING
    updated_at: 2026-03-14T00:00:00Z
    source: data_flow_active
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: check_data_flow_active
    purpose: Verifies at least one sync cycle produced data per active source in the last 2 hours (V1, V3)
    status: pending
    priority: high
  - name: check_graph_nodes_written
    purpose: Verifies body data nodes exist in graph for recently synced citizens (V7)
    status: pending
    priority: high
  - name: check_source_auth_healthy
    purpose: Verifies OAuth2 tokens are valid and refresh is working for all cloud sources (V4)
    status: pending
    priority: high
  - name: check_bridge_receiving
    purpose: Verifies on-device bridge endpoints received data in the last 4 hours (V1)
    status: pending
    priority: high
  - name: check_normalization_ratio
    purpose: Verifies normalization success rate is above 95% (V1)
    status: pending
    priority: med
  - name: check_dedup_ratio
    purpose: Monitors dedup ratio for anomalies — sudden changes indicate source issues (V2)
    status: pending
    priority: low
```

---

## INDICATOR: data_flow_active

This indicator confirms that the sync pipeline is running and producing data. It is the primary "is the module alive?" signal.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: data_flow_active
  client_value: Citizens with connected wearables see fresh body data in their graph. Without this, the Brief Matinal has no biometric context and the citizen cannot reason about the human's physical state.
  validation:
    - validation_id: V1
      criteria: Body data nodes conform to NormalizedBodySample schema
    - validation_id: V3
      criteria: Each source syncs independently — one failure doesn't block others
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum:
      OK: All active sources produced data in the last 2 hours
      WARN: At least one source has not produced data in the last 2 hours but others are working
      ERROR: No source has produced data in the last 4 hours
      UNKNOWN: No active wearable connections exist (not an error — wearables are optional)
  aggregation:
    method: Worst-case across sources. If any source is ERROR, overall is ERROR. If any is WARN but none ERROR, overall is WARN.
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_fetch
    type: api
    payload: {source, sample_count, http_status, latency_ms}
  - point: dock_graph_write
    type: graph_ops
    payload: {citizen_id, nodes_written, node_types, sources}
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="data_flow_active",
    triggers=[
        triggers.cron.every(hours=1),
    ],
    on_problem="WEARABLE_SYNC_STALE",
    task="investigate_wearable_sync_failure",
)
def check_data_flow_active(ctx) -> dict:
    """Verify all active wearable sources have synced recently."""
    active_sources = get_active_sources(ctx.citizen_id)
    if not active_sources:
        return Signal.healthy(details={"reason": "no_active_connections"})

    stale = []
    for source in active_sources:
        state = get_sync_state(ctx.citizen_id, source)
        if state.last_synced_at < now() - timedelta(hours=4):
            stale.append(source)
        elif state.last_synced_at < now() - timedelta(hours=2):
            stale.append(source)  # warn-level

    if len(stale) == len(active_sources):
        return Signal.critical(details={"stale_sources": stale})
    if stale:
        return Signal.degraded(details={"stale_sources": stale})
    return Signal.healthy()
```

### SIGNALS

```yaml
signals:
  healthy: All active sources synced within the last 2 hours
  degraded: At least one source is stale (2-4 hours since last sync)
  critical: All sources are stale (4+ hours since last sync) or no data has ever been written
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: cron every 1 hour
  max_frequency: 1/hour
  burst_limit: 1
  backoff: No backoff — fixed hourly check aligned with sync schedule
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: runtime/integrations/wearables/health_checks.py
      transport: file
      notes: Doctor reads health status from checker output
display:
  locations:
    - surface: CLI
      location: mind doctor
      signal: OK/WARN/ERROR
      notes: Shows wearable sync health in doctor output
    - surface: Log
      location: runtime logs
      signal: Structured log entry with source details
      notes: Per-source sync status logged each cycle
```

### MANUAL RUN

```yaml
manual_run:
  command: mind doctor --check wearable_data_flow
  notes: Run when investigating missing body data for a citizen
```

---

## HOW TO RUN

```bash
# Run all health checks for wearable bridges
mind doctor --module wearable-bridges

# Run a specific checker
mind doctor --check wearable_data_flow
mind doctor --check wearable_auth_health
mind doctor --check wearable_normalization
```

---

## KNOWN GAPS

- All checkers are currently `pending` — implementation blocked on pipeline code being written
- No health check for deduplication correctness (V2) beyond ratio monitoring — would need to query graph for duplicates
- No health check for credential encryption (V4) — this is a security audit concern, not a runtime health check

<!-- @mind:todo Implement check_data_flow_active when sync pipeline is built -->
<!-- @mind:todo Implement check_source_auth_healthy when OAuth2 flow is built -->
<!-- @mind:todo Implement check_bridge_receiving when on-device bridge endpoints are built -->

---

## MARKERS

<!-- @mind:todo All 6 checkers are pending — implement as pipeline code lands -->
<!-- @mind:proposition Add a health check for data latency (time between wearable measurement and graph write) -->
<!-- @mind:escalation Should health checks run per-citizen or per-source globally? Per-citizen is more accurate but more expensive. -->
