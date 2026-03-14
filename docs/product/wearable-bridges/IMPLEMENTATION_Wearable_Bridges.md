# Wearable Bridges — Implementation: Code Architecture and Structure

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
ALGORITHM:       ./ALGORITHM_Wearable_Bridges.md
VALIDATION:      ./VALIDATION_Wearable_Bridges.md
THIS:            IMPLEMENTATION_Wearable_Bridges.md (you are here)
HEALTH:          ./HEALTH_Wearable_Bridges.md
SYNC:            ./SYNC_Wearable_Bridges.md

IMPL:            mind-mcp: runtime/integrations/wearables/
                 mind-app: (HealthKit + Health Connect native modules)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

This module spans two repositories with distinct responsibilities.

### mind-mcp (Server-Side — API Bridges + Core Pipeline)

```
runtime/integrations/wearables/
├── __init__.py                                    # Exports: sync_wearable_data, WearableAdapter
├── wearable_adapter_interface_and_registry.py     # Abstract adapter protocol + adapter factory
├── normalized_body_sample_schema.py               # NormalizedBodySample dataclass + validation
├── sync_pipeline_fetch_normalize_dedup_write.py   # Core pipeline: fetch -> normalize -> dedup -> graph_write
├── deduplication_engine_cross_source.py            # Dedup logic: key generation, conflict resolution by confidence
├── sync_state_watermark_tracker.py                # Per-citizen per-source sync state and watermark management
├── adapters/
│   ├── __init__.py
│   ├── garmin_connect_api_adapter.py              # Garmin Connect OAuth2 + endpoint polling (LIVE)
│   ├── healthkit_bridge_adapter.py                # Receives normalized data from mind-app iOS module
│   ├── health_connect_bridge_adapter.py           # Receives normalized data from mind-app Android module
│   └── (post-launch direct API adapters added here)
└── graph_writer_body_data_nodes_and_links.py      # Converts NormalizedBodySample -> graph nodes + links
```

### mind-app (Client-Side — On-Device Health Store Access)

```
ios/
├── HealthKit/
│   ├── MINDHealthKitManager.swift                 # HealthKit permission requests + data queries
│   ├── MINDHealthKitNormalizer.swift               # HKQuantitySample -> NormalizedBodySample translation
│   └── MINDHealthKitBridge.swift                   # Sends normalized data to mind-mcp endpoint

android/
├── healthconnect/
│   ├── MINDHealthConnectManager.kt                # Health Connect permission requests + data reads
│   ├── MINDHealthConnectNormalizer.kt             # HealthConnect records -> NormalizedBodySample translation
│   └── MINDHealthConnectBridge.kt                 # Sends normalized data to mind-mcp endpoint
```

### File Responsibilities (mind-mcp)

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `wearable_adapter_interface_and_registry.py` | Adapter contract + factory | `WearableAdapter`, `get_adapter()` | ~80 | PLANNED |
| `normalized_body_sample_schema.py` | Canonical data schema | `NormalizedBodySample`, `validate_sample()` | ~100 | PLANNED |
| `sync_pipeline_fetch_normalize_dedup_write.py` | Core orchestration | `sync_wearable_data()`, `run_sync_cycle()` | ~200 | PLANNED |
| `deduplication_engine_cross_source.py` | Cross-source dedup | `make_dedup_key()`, `deduplicate()` | ~120 | PLANNED |
| `sync_state_watermark_tracker.py` | Sync state persistence | `SyncState`, `get_sync_state()`, `update_watermark()` | ~100 | PLANNED |
| `garmin_connect_api_adapter.py` | Garmin integration | `GarminAdapter`, `fetch()`, `normalize()` | ~250 | LIVE |
| `healthkit_bridge_adapter.py` | HealthKit data receiver | `HealthKitBridgeAdapter`, `receive()` | ~80 | PLANNED |
| `health_connect_bridge_adapter.py` | Health Connect data receiver | `HealthConnectBridgeAdapter`, `receive()` | ~80 | PLANNED |
| `graph_writer_body_data_nodes_and_links.py` | Graph node creation | `write_body_data()`, `create_body_node()` | ~150 | PLANNED |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Adapter + Pipeline

**Why this pattern:** Each wearable source has a unique API, auth flow, and data format. The Adapter pattern isolates vendor-specific concerns. The Pipeline pattern (fetch -> normalize -> dedup -> write) ensures every source's data goes through the same processing stages. Adding a new source means adding one adapter file, not touching the pipeline.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Adapter | `adapters/*.py` | Isolate vendor-specific API logic behind a common interface |
| Pipeline | `sync_pipeline_*.py` | Sequential processing stages with clear data transformations |
| Factory | `wearable_adapter_interface_and_registry.py` | Instantiate the correct adapter by source name |
| Watermark | `sync_state_watermark_tracker.py` | Incremental sync — only fetch new data since last successful sync |

### Anti-Patterns to Avoid

- **God Adapter**: Don't put normalization logic in the pipeline — each adapter normalizes its own data via its specific normalizer
- **Shared State Between Adapters**: Adapters must not read each other's state. Cross-source logic (dedup) lives in the pipeline, not in adapters
- **Fallback Data**: If an adapter can't fetch, it raises an error. It never returns synthetic or cached data pretending to be fresh

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Adapter boundary | Vendor API calls, auth, raw parsing | Normalization schema, graph writes | `WearableAdapter.fetch(since) -> list[RawSample]` |
| Pipeline boundary | Normalize, dedup, write orchestration | Vendor API details, graph internals | `sync_wearable_data(citizen_id, source)` |
| Graph boundary | Node/link creation from normalized data | How the graph stores or indexes nodes | `graph_write(node, link)` |
| App-to-server boundary | On-device health store reads | Server-side processing | HTTP POST of NormalizedBodySample batches |

---

## SCHEMA

### NormalizedBodySample

```yaml
NormalizedBodySample:
  required:
    - metric_type: str        # Canonical enum: heart_rate, hrv, sleep_session, spo2, stress, etc.
    - value: float | dict     # Scalar or structured (sleep has stages)
    - unit: str               # Canonical: bpm, ms, hours, percent, celsius, ml/kg/min, count, kcal
    - timestamp: datetime     # UTC
    - source: str             # Integration name
    - confidence: float       # 0.0-1.0
  optional:
    - duration: timedelta     # For session/window metrics
    - source_device: str      # Device name if known
    - raw_id: str             # Vendor's sample ID for dedup
  constraints:
    - confidence must be between 0.0 and 1.0
    - timestamp must be UTC
    - metric_type must be from canonical enum
    - unit must match metric_type (heart_rate -> bpm, hrv -> ms, etc.)
```

### SyncState

```yaml
SyncState:
  required:
    - citizen_id: str
    - source: str
    - last_synced_at: datetime
    - status: str             # active, auth_expired, disabled, error
    - error_count: int
  optional:
    - last_error: str
    - tokens: dict            # Encrypted OAuth2 tokens
  relationships:
    - citizen: actor node (via citizen_id)
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `sync_wearable_data()` | `sync_pipeline_*.py` | Hourly scheduler or manual trigger via MCP tool |
| `receive_healthkit_data()` | `healthkit_bridge_adapter.py` | HTTP POST from mind-app iOS module |
| `receive_health_connect_data()` | `health_connect_bridge_adapter.py` | HTTP POST from mind-app Android module |
| `garmin_oauth_callback()` | `garmin_connect_api_adapter.py` | OAuth2 redirect after user authorizes Garmin |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Flow 1: Cloud API Sync (Garmin + Post-Launch Direct APIs)

Covers server-side API polling for wearable data. This flow transforms vendor API responses into graph nodes and carries risk at the auth, rate-limit, and graph-write boundaries.

```yaml
flow:
  name: cloud_api_sync
  purpose: Fetch body data from cloud wearable APIs and write to citizen graph
  scope: OAuth2 auth -> API fetch -> normalize -> dedup -> graph write
  steps:
    - id: step_1_auth_check
      description: Verify OAuth2 token is valid, refresh if needed
      file: sync_pipeline_fetch_normalize_dedup_write.py
      function: sync_wearable_data()
      input: SyncState (citizen_id, source, tokens)
      output: Valid access_token or auth_expired error
      trigger: Hourly scheduler
      side_effects: Token refresh may update stored tokens
    - id: step_2_fetch
      description: Call vendor API with since=last_synced_at
      file: adapters/garmin_connect_api_adapter.py
      function: GarminAdapter.fetch()
      input: access_token, since timestamp
      output: list[RawSample]
      trigger: Called by pipeline step 1
      side_effects: API rate limit counter incremented
    - id: step_3_normalize
      description: Transform vendor-specific data to canonical schema
      file: adapters/garmin_connect_api_adapter.py
      function: GarminAdapter.normalize()
      input: list[RawSample]
      output: list[NormalizedBodySample]
      trigger: Called after fetch
      side_effects: None
    - id: step_4_dedup
      description: Remove duplicates across sources
      file: deduplication_engine_cross_source.py
      function: deduplicate()
      input: list[NormalizedBodySample]
      output: list[NormalizedBodySample] (unique)
      trigger: Called after all sources normalized
      side_effects: None
    - id: step_5_graph_write
      description: Create graph nodes + links for each deduplicated sample
      file: graph_writer_body_data_nodes_and_links.py
      function: write_body_data()
      input: citizen_id, list[NormalizedBodySample]
      output: int (nodes_written)
      trigger: Called after dedup
      side_effects: Graph nodes and links created
  docking_points:
    available:
      - id: dock_auth
        type: auth
        direction: output
        file: sync_pipeline_fetch_normalize_dedup_write.py
        function: sync_wearable_data()
        trigger: Token refresh attempt
        payload: {source, token_status, refresh_result}
        async_hook: optional
        needs: none
        notes: Monitors auth health across sources
      - id: dock_fetch
        type: api
        direction: input
        file: adapters/garmin_connect_api_adapter.py
        function: GarminAdapter.fetch()
        trigger: API response received
        payload: {source, sample_count, http_status, latency_ms}
        async_hook: optional
        needs: add metrics hook
        notes: Rate limit tracking and API health monitoring
      - id: dock_graph_write
        type: graph_ops
        direction: output
        file: graph_writer_body_data_nodes_and_links.py
        function: write_body_data()
        trigger: After batch write
        payload: {citizen_id, nodes_written, node_types, sources}
        async_hook: optional
        needs: add metrics hook
        notes: Verifies data actually reaches the graph
    health_recommended:
      - dock_id: dock_fetch
        reason: API failures are the most common sync failure mode
      - dock_id: dock_graph_write
        reason: Confirms body data actually persists in the graph
```

### Flow 2: On-Device Bridge (HealthKit / Health Connect)

Covers data path from mobile device health stores through to graph write. The mind-app native module handles the on-device read and normalization, then POSTs batches to mind-mcp.

```yaml
flow:
  name: on_device_bridge
  purpose: Receive normalized body data from mind-app and write to citizen graph
  scope: HTTP POST -> validate -> dedup -> graph write
  steps:
    - id: step_1_receive
      description: Receive batch of NormalizedBodySample from mind-app
      file: healthkit_bridge_adapter.py
      function: receive_healthkit_data()
      input: HTTP POST with list[NormalizedBodySample]
      output: Validated list[NormalizedBodySample]
      trigger: mind-app sends batch after on-device sync
      side_effects: None
    - id: step_2_validate
      description: Validate each sample conforms to NormalizedBodySample schema
      file: normalized_body_sample_schema.py
      function: validate_sample()
      input: NormalizedBodySample
      output: Valid sample or validation error
      trigger: Called for each received sample
      side_effects: None
    - id: step_3_dedup
      description: Deduplicate against existing graph data and other sources
      file: deduplication_engine_cross_source.py
      function: deduplicate()
      input: list[NormalizedBodySample]
      output: list[NormalizedBodySample] (unique)
      trigger: After validation
      side_effects: None
    - id: step_4_graph_write
      description: Write to graph (same as cloud flow)
      file: graph_writer_body_data_nodes_and_links.py
      function: write_body_data()
      input: citizen_id, list[NormalizedBodySample]
      output: int (nodes_written)
      trigger: After dedup
      side_effects: Graph nodes and links created
  docking_points:
    available:
      - id: dock_receive
        type: api
        direction: input
        file: healthkit_bridge_adapter.py
        function: receive_healthkit_data()
        trigger: HTTP POST from mind-app
        payload: {citizen_id, source, sample_count, batch_size_bytes}
        async_hook: optional
        needs: none
        notes: Entry point for all on-device data
      - id: dock_validate
        type: api
        direction: output
        file: normalized_body_sample_schema.py
        function: validate_sample()
        trigger: Each sample validated
        payload: {valid_count, invalid_count, error_types}
        async_hook: not_applicable
        needs: none
        notes: Catches malformed data from app before graph write
    health_recommended:
      - dock_id: dock_receive
        reason: Confirms on-device data is actually arriving at server
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
sync_pipeline_fetch_normalize_dedup_write.py
    └── imports -> wearable_adapter_interface_and_registry.py
    └── imports -> deduplication_engine_cross_source.py
    └── imports -> graph_writer_body_data_nodes_and_links.py
    └── imports -> sync_state_watermark_tracker.py

graph_writer_body_data_nodes_and_links.py
    └── imports -> normalized_body_sample_schema.py

adapters/garmin_connect_api_adapter.py
    └── imports -> wearable_adapter_interface_and_registry.py
    └── imports -> normalized_body_sample_schema.py
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `httpx` | HTTP client for cloud API calls | `garmin_connect_api_adapter.py` |
| `pydantic` | Data validation for NormalizedBodySample | `normalized_body_sample_schema.py` |
| `cryptography` | OAuth2 token encryption at rest | `sync_state_watermark_tracker.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Sync watermarks | `SyncState` in DB (per citizen, per source) | Per-citizen | Created on first connect, updated each sync |
| OAuth2 tokens | `SyncState.tokens` (encrypted) | Per-citizen, per-source | Created on OAuth flow, refreshed periodically, deleted on disconnect |
| Adapter registry | In-memory dict | Global (process) | Created at startup, immutable |

### State Transitions

```
SyncState.status:
    (none) ──connect──> active ──auth_expires──> auth_expired ──refresh_succeeds──> active
                          │                         │
                          ├──user_disables──> disabled
                          │                         │
                          └──errors > threshold──> error ──manual_reset──> active
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Load adapter registry (register all known adapters)
2. Load sync states for all citizens with active connections
3. Start hourly sync scheduler
4. Register HTTP endpoints for on-device bridge receivers
```

### Main Loop (Hourly Sync Cycle)

```
1. For each citizen with active wearable connections:
   a. Determine active sources
   b. For each source: fetch -> normalize (adapter-specific)
   c. Collect all normalized samples across sources
   d. Deduplicate
   e. Write to graph
   f. Update watermarks
2. Log cycle summary (citizens synced, nodes written, errors)
```

### On-Demand (On-Device Bridge)

```
1. Receive HTTP POST with batch of NormalizedBodySample
2. Validate schema compliance
3. Deduplicate against graph + other pending sources
4. Write to graph
5. Return confirmation with nodes_written count
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| Sync scheduler | async (event loop) | Hourly trigger, fans out to per-citizen tasks |
| Per-citizen sync | async tasks | One task per citizen, adapters use async HTTP |
| Bridge receivers | async HTTP handlers | Handle POST from mind-app, non-blocking |
| Graph writes | async batched | Batch writes within a sync cycle for throughput |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `WEARABLE_SYNC_INTERVAL_SECONDS` | env / config | `3600` (1 hour) | How often the sync scheduler runs |
| `WEARABLE_MAX_BACKOFF_SECONDS` | env / config | `86400` (24 hours) | Max backoff for repeatedly failing sources |
| `WEARABLE_DEDUP_WINDOW_SECONDS` | env / config | `60` | Timestamp bucket size for time-series dedup |
| `GARMIN_CLIENT_ID` | env (secret) | — | Garmin Connect OAuth2 client ID |
| `GARMIN_CLIENT_SECRET` | env (secret) | — | Garmin Connect OAuth2 client secret |
| `WEARABLE_BRIDGE_ENDPOINT` | env / config | `/api/wearable/bridge` | HTTP endpoint for on-device data receiver |

---

## MARKERS

<!-- @mind:todo Verify Garmin adapter file structure against what currently exists in mind-mcp -->
<!-- @mind:todo Define HTTP endpoint contract for on-device bridge (request/response schema) -->
<!-- @mind:proposition Consider gRPC instead of REST for app-to-server bridge — lower latency, typed contracts -->
<!-- @mind:escalation Need to decide: does sync state live in the graph (as nodes) or in a separate DB table? -->
