# Wearable Bridges — Algorithm: Sync Pipeline and Normalization Logic

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Wearable_Bridges.md
BEHAVIORS:       ./BEHAVIORS_Wearable_Bridges.md
PATTERNS:        ./PATTERNS_Wearable_Bridges.md
THIS:            ALGORITHM_Wearable_Bridges.md (you are here)
VALIDATION:      ./VALIDATION_Wearable_Bridges.md
IMPLEMENTATION:  ./IMPLEMENTATION_Wearable_Bridges.md
SYNC:            ./SYNC_Wearable_Bridges.md

IMPL:            mind-mcp: runtime/integrations/wearables/
                 mind-app: (HealthKit + Health Connect native modules)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The Wearable Bridges module runs a periodic sync pipeline that fetches body data from connected wearable sources, normalizes it into a canonical schema, deduplicates across overlapping sources, and writes the results as typed nodes into the citizen's graph.

The pipeline is source-agnostic: it doesn't care whether data comes from a cloud API (Garmin, Oura, WHOOP) or an on-device health store (HealthKit, Health Connect). All sources implement the same adapter interface, and the core pipeline treats their output identically.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1 (MIND knows your body) | B1, B3, B7 | The sync pipeline is the only path for body data to enter the graph |
| O2 (95% coverage) | B5, B6 | The adapter interface enables 3 aggregators at launch + N direct APIs post-launch |
| O3 (Typed nodes, not raw metrics) | B2, B4 | Normalization and dedup guarantee clean, uniform graph nodes |

---

## DATA STRUCTURES

### NormalizedBodySample

The canonical output of every adapter, regardless of source.

```
NormalizedBodySample:
    metric_type: str          # Canonical type: "heart_rate", "hrv", "sleep_session", "spo2", "stress",
                              #   "body_battery", "temperature", "vo2max", "steps", "calories", "ecg",
                              #   "sleep_stage", "resting_heart_rate"
    value: float | dict       # Scalar for simple metrics, dict for complex (sleep_session has stages, duration, score)
    unit: str                 # Canonical unit: "bpm", "ms", "hours", "percent", "celsius", "ml/kg/min", "count", "kcal"
    timestamp: datetime       # UTC, when the measurement was taken (or start of window for aggregates)
    duration: timedelta | None  # For window-based metrics (sleep session, activity)
    source: str               # Integration that produced this: "garmin_connect", "healthkit", "health_connect",
                              #   "oura_api", "whoop_api", "strava_api", etc.
    source_device: str | None  # Device name if known: "Apple Watch Series 9", "Oura Ring Gen 3"
    confidence: float          # 0.0-1.0, how reliable this reading is (aggregator=0.8, direct_api=0.95, manual=0.5)
    raw_id: str | None         # Vendor's unique ID for this sample, used for deduplication
```

### SyncState

Tracks per-citizen, per-source sync progress.

```
SyncState:
    citizen_id: str           # Actor node ID
    source: str               # Integration name
    last_synced_at: datetime   # Watermark — only fetch data after this
    status: str               # "active", "auth_expired", "disabled", "error"
    error_count: int           # Consecutive errors (for backoff)
    last_error: str | None     # Most recent error message
    tokens: dict | None        # OAuth2 tokens (encrypted at rest), None for on-device sources
```

### DeduplicationKey

How we identify duplicate samples across sources.

```
DeduplicationKey:
    citizen_id: str
    metric_type: str
    timestamp_bucket: datetime   # Rounded to nearest minute for HR/stress, to start-of-session for sleep
    source_priority: int         # Direct API = 2, Aggregator = 1. Higher wins.
```

---

## ALGORITHM: Sync Pipeline

### Step 1: Determine Active Sources

For a given citizen, enumerate all connected and active wearable sources. Skip sources with expired auth or that the citizen has disabled.

```
active_sources = []
for source in citizen.wearable_connections:
    state = get_sync_state(citizen.id, source)
    if state.status == "active":
        active_sources.append(source)
    elif state.status == "auth_expired":
        attempt_token_refresh(state)
        if refresh_succeeded:
            active_sources.append(source)
        else:
            log_warning(citizen.id, source, "auth_expired_and_refresh_failed")
```

### Step 2: Fetch Raw Data from Each Source

Each source has an adapter implementing `fetch(since: datetime) -> list[RawSample]`. Adapters are isolated — a failure in one does not affect others.

```
all_raw = {}
for source in active_sources:
    adapter = get_adapter(source)
    state = get_sync_state(citizen.id, source)
    try:
        raw_samples = adapter.fetch(since=state.last_synced_at)
        all_raw[source] = raw_samples
        reset_error_count(state)
    except AdapterError as e:
        increment_error_count(state, e)
        log_error(citizen.id, source, e)
        apply_backoff(state)
        # Continue to next source — no cascade
```

For on-device sources (HealthKit, Health Connect), `fetch()` doesn't make a network call to a cloud API. Instead, the mind-app native module reads from the on-device store and sends normalized data to mind-mcp. From the pipeline's perspective, the adapter just returns data — the transport mechanism is abstracted away.

### Step 3: Normalize Raw Samples

Each adapter transforms vendor-specific data into `NormalizedBodySample`. This is where Garmin's "restingHeartRate" becomes `metric_type="resting_heart_rate"`, where Apple's HKQuantityType becomes a canonical type, where milliseconds become the standard HRV unit.

```
all_normalized = []
for source, raw_samples in all_raw.items():
    normalizer = get_normalizer(source)
    for raw in raw_samples:
        try:
            normalized = normalizer.normalize(raw)
            all_normalized.append(normalized)
        except NormalizationError as e:
            log_warning(citizen.id, source, f"skipping_unnormalizable: {e}", raw_data=raw)
            # Skip this sample, continue with others
```

### Step 4: Deduplicate Across Sources

When the same data arrives from multiple sources (e.g., Oura sleep via HealthKit and Oura direct API), keep only the highest-fidelity version.

```
dedup_map = {}
for sample in all_normalized:
    key = make_dedup_key(sample)
    if key in dedup_map:
        existing = dedup_map[key]
        if sample.confidence > existing.confidence:
            log_info(f"dedup_replacing: {existing.source} -> {sample.source} for {key}")
            dedup_map[key] = sample
        else:
            log_info(f"dedup_discarding: {sample.source} (lower confidence than {existing.source})")
    else:
        dedup_map[key] = sample

deduplicated = list(dedup_map.values())
```

### Step 5: Write to Citizen's Graph

Convert each deduplicated sample into a graph node and write via `graph_write`. Body data becomes:
- **moment** nodes for time-series events (heart rate at 14:32, sleep session from 23:00-07:00)
- **thing** nodes for derived measurements (VO2max estimate, body battery level)

```
nodes_written = 0
for sample in deduplicated:
    node_type = "moment" if sample.duration or is_time_series(sample.metric_type) else "thing"

    node = create_node(
        node_type=node_type,
        type=f"body_{sample.metric_type}",
        content=format_content(sample),
        synthesis=format_synthesis(sample),  # Embeddable summary: "Heart rate: 62 bpm at 14:32 UTC"
        metadata={
            "metric_type": sample.metric_type,
            "value": sample.value,
            "unit": sample.unit,
            "source": sample.source,
            "confidence": sample.confidence,
        }
    )

    link = create_link(
        from_node=citizen.actor_node_id,
        to_node=node.id,
        type="body_data",
        polarity=1.0,
        permanence=0.3,  # Body data is ephemeral — recent readings matter, old ones decay
    )

    graph_write(node, link)
    nodes_written += 1
```

### Step 6: Update Watermarks

After successful write, advance the sync watermark so the next cycle doesn't re-fetch.

```
for source in active_sources:
    if source in all_raw and len(all_raw[source]) > 0:
        latest_timestamp = max(s.timestamp for s in all_normalized if s.source == source)
        update_watermark(citizen.id, source, latest_timestamp)
```

---

## KEY DECISIONS

### D1: Deduplication Timestamp Bucketing

```
IF metric_type is time-series (HR, HRV, stress, SpO2):
    bucket = round_to_nearest_minute(timestamp)
    Rationale: HR readings within the same minute from different sources are the same measurement
ELSE IF metric_type is session-based (sleep, activity):
    bucket = session_start_time
    Rationale: Two sleep sessions starting at the same time are the same session
ELSE:
    bucket = round_to_nearest_hour(timestamp)
    Rationale: Daily summary metrics (VO2max, body battery) are inherently coarse
```

### D2: Node Type Selection

```
IF sample has duration OR metric is inherently time-series (HR, HRV, steps, calories):
    node_type = "moment"
    Rationale: These are events in time — they happened at a point or during a window
ELSE IF metric is a derived measurement (VO2max, body battery, readiness score):
    node_type = "thing"
    Rationale: These are computed values, not events — they describe a state
```

### D3: Confidence Assignment

```
IF source is a direct API (oura_api, whoop_api, etc.):
    confidence = 0.95
    Rationale: Direct vendor API provides highest-fidelity data
ELSE IF source is a platform aggregator (healthkit, health_connect):
    confidence = 0.85
    Rationale: Aggregators may round, downsample, or delay data
ELSE IF source is a cross-platform aggregator (garmin_connect):
    confidence = 0.80
    Rationale: Cloud aggregators add network latency and may cache stale data
ELSE IF source is manual entry:
    confidence = 0.50
    Rationale: Human-entered data is subjective and error-prone
```

---

## DATA FLOW

```
Wearable Device (watch, ring, band)
    |
    v
Platform Health Store (HealthKit / Health Connect) OR Cloud API (Garmin Connect)
    |
    v
[Adapter: fetch(since)] — source-specific, handles auth + pagination + rate limits
    |
    v
list[RawSample] — vendor-specific format
    |
    v
[Normalizer: normalize(raw)] — vendor-to-canonical translation
    |
    v
list[NormalizedBodySample] — canonical format
    |
    v
[Deduplicator: dedup(samples)] — cross-source conflict resolution
    |
    v
list[NormalizedBodySample] — unique, highest-fidelity
    |
    v
[GraphWriter: write(citizen_id, samples)] — node + link creation
    |
    v
Citizen's Graph — body data nodes with typed links to actor
```

---

## COMPLEXITY

**Time:** O(N * M) per sync cycle, where N = number of active sources and M = average samples per source. In practice, N <= 3 at launch and M ~ 100-500 per hourly sync (HR every 5 min = ~12/hr, sleep = 1, steps = 1 summary, etc.). Total: ~1500 samples/cycle max.

**Space:** O(M_total) for the in-memory normalization + dedup pass, where M_total = sum of samples across all sources. At ~1500 samples of ~200 bytes each, this is ~300KB. Negligible.

**Bottlenecks:**
- API rate limits on cloud sources (Garmin limits vary by endpoint, typically 25 req/min)
- HealthKit/Health Connect query performance on devices with years of historical data (first sync only — subsequent syncs are incremental)
- Graph write throughput if many citizens sync simultaneously (batch writes recommended)

---

## HELPER FUNCTIONS

### `get_adapter(source: str) -> WearableAdapter`

**Purpose:** Factory that returns the correct adapter for a given source name.

**Logic:** Lookup in adapter registry. Raises `UnknownSourceError` if source is not registered. Each adapter handles its own auth, pagination, and rate limiting.

### `make_dedup_key(sample: NormalizedBodySample) -> DeduplicationKey`

**Purpose:** Produces a deduplication key by bucketing the timestamp based on metric type.

**Logic:** Combines citizen_id + metric_type + bucketed timestamp. The bucket size varies by metric type (see D1).

### `format_synthesis(sample: NormalizedBodySample) -> str`

**Purpose:** Creates an embeddable summary string for the graph node's synthesis field.

**Logic:** Templates by metric type. Examples: "Heart rate: 62 bpm at 2026-03-14 14:32 UTC", "Sleep session: 7.2 hours (23:15-06:27), quality score 82/100", "HRV: 45 ms (RMSSD) at 2026-03-14 06:30 UTC".

### `attempt_token_refresh(state: SyncState) -> bool`

**Purpose:** Refreshes OAuth2 tokens for cloud API sources before they expire.

**Logic:** Uses the refresh_token from SyncState.tokens to request a new access_token. Updates SyncState on success. Returns False if refresh fails (user revoked access, refresh token expired).

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| mind-mcp `graph_write` | `graph_write(node, link)` | Confirmation that node + link are persisted in graph |
| L4 Schema | Node/link validators | Validation that body data nodes conform to schema |
| mind-app native modules | `adapter.fetch(since)` via bridge | Raw body data samples from on-device health stores |
| OAuth2 provider endpoints | Token refresh | New access_token for cloud API sources |

---

## MARKERS

<!-- @mind:todo Define the exact adapter interface (abstract class or protocol) -->
<!-- @mind:todo Specify the on-device-to-cloud bridge transport for HealthKit/Health Connect data -->
<!-- @mind:proposition Consider batch graph_write for performance — writing 500 nodes one-by-one is slow -->
<!-- @mind:escalation How does the mind-app native module send data to mind-mcp? REST? WebSocket? Direct function call? -->
