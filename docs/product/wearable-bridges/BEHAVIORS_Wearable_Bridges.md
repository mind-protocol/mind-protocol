# Wearable Bridges — Behaviors: Body Data Acquisition and Graph Ingestion

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Wearable_Bridges.md
THIS:            BEHAVIORS_Wearable_Bridges.md (you are here)
PATTERNS:        ./PATTERNS_Wearable_Bridges.md
ALGORITHM:       ./ALGORITHM_Wearable_Bridges.md
VALIDATION:      ./VALIDATION_Wearable_Bridges.md
IMPLEMENTATION:  ./IMPLEMENTATION_Wearable_Bridges.md
SYNC:            ./SYNC_Wearable_Bridges.md

IMPL:            mind-mcp: runtime/integrations/wearables/
                 mind-app: (HealthKit + Health Connect native modules)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Body Data Reaches the Citizen's Graph

**Why:** The entire module exists so that physiological data becomes part of the citizen's knowledge graph. If data is fetched but never written to the graph, the module has failed. Every sync cycle must produce graph nodes or explicitly confirm there is nothing new to write.

```
GIVEN:  A citizen has connected a wearable via one of the three aggregator bridges (Garmin API, HealthKit, Health Connect)
WHEN:   A sync cycle executes (hourly schedule or manual trigger)
THEN:   New body data since the last sync is normalized, deduplicated, and written as typed nodes to the citizen's graph
AND:    Each node is linked to the citizen's actor node with appropriate typed links
AND:    The sync watermark (last_synced_at) is updated to prevent re-fetching
```

### B2: All Integrations Produce Unified Data Schema

**Why:** Downstream consumers (Brief Matinal, citizen reasoning, pattern detection) must not care which wearable or which bridge produced the data. A heart rate reading from Garmin and a heart rate reading from Apple Watch must be structurally identical in the graph.

```
GIVEN:  Body data arrives from any integration (Garmin API, HealthKit, Health Connect, or any post-launch direct API)
WHEN:   The normalization step processes raw vendor data
THEN:   The output conforms to the normalized body data schema (type, value, unit, timestamp, source, confidence)
AND:    Vendor-specific field names, units, and structures are translated to canonical types
AND:    No raw vendor payload is written to the graph
```

### B3: Citizens Without Wearables Are Unaffected

**Why:** Body data is an enrichment layer, not a dependency. The graph, citizen reasoning, Brief Matinal, and all other systems must work fully without any body data nodes. Wearable connection is opt-in, and absence of body data is a normal state.

```
GIVEN:  A citizen has no connected wearable
WHEN:   Any system queries for body data nodes
THEN:   The query returns empty results (not errors, not null, not defaults)
AND:    No special handling or fallback logic is required — the graph simply has fewer nodes
```

### B4: Deduplication Across Overlapping Sources

**Why:** A user with an Oura Ring on iOS will have sleep data in both HealthKit (via Oura's HealthKit integration) and the Oura direct API (post-launch). Writing the same sleep session twice to the graph would corrupt pattern detection and inflate metrics. Deduplication must happen before graph write.

```
GIVEN:  The same body data point arrives from two different sources (e.g., Oura sleep via HealthKit AND Oura direct API)
WHEN:   The normalization pipeline processes both data points
THEN:   Only one node is written to the graph
AND:    The source with higher fidelity/granularity is preferred (direct API over aggregator when both available)
AND:    The discarded duplicate is logged for observability, not silently dropped
```

### B5: Post-Launch Direct APIs Extend Without Modifying Core

**Why:** Adding a direct API integration (Oura, WHOOP, Strava, etc.) should be additive. The core pipeline — normalize, deduplicate, write to graph — must not change when a new integration is added. Each direct API is a new data source that feeds into the same pipeline.

```
GIVEN:  A new direct API integration (e.g., WHOOP) is being added post-launch
WHEN:   The integration produces normalized body data
THEN:   It feeds into the existing normalization/dedup/graph-write pipeline
AND:    No changes to the core pipeline code are required
AND:    No changes to the graph schema are required (new metric types use existing node types)
```

### B6: OAuth and Permission Flows Complete Successfully

**Why:** Cloud APIs require OAuth2 tokens. On-device APIs require explicit user permission grants. If auth fails, no data flows. The auth flows must be clear, recoverable, and must store credentials securely.

```
GIVEN:  A user initiates wearable connection (cloud API or on-device)
WHEN:   The OAuth2 flow completes (cloud) or the permission dialog is accepted (on-device)
THEN:   Credentials/tokens are stored securely (never in git, never in plaintext logs)
AND:    The first sync cycle triggers automatically after successful auth
AND:    Token refresh is handled transparently before expiry (cloud APIs)
```

### B7: Sync Failures Are Visible and Non-Fatal

**Why:** Wearable APIs go down. Tokens expire. Rate limits hit. These failures must be visible (logged, trackable) but must never crash the citizen's graph operations or block other integrations. A Garmin API outage must not prevent HealthKit data from flowing.

```
GIVEN:  A sync cycle for one integration fails (API error, auth expired, rate limited)
WHEN:   The sync scheduler processes integrations
THEN:   The failure is logged with source, error type, and timestamp
AND:    Other integrations continue their sync cycles unaffected
AND:    The failed integration is retried on the next cycle with backoff
AND:    No partial/corrupt data is written to the graph
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1 (MIND knows your body) | Without graph nodes, body data doesn't exist in the citizen's world |
| B2 | O3 (Data as typed nodes) | Uniform schema enables uniform reasoning across all body data |
| B3 | O1 (MIND knows your body) | Body data enriches but must not gate core functionality |
| B4 | O3 (Data as typed nodes) | Duplicates corrupt the graph and break pattern detection |
| B5 | O2 (95% coverage at launch) | Launch with aggregators, extend with direct APIs, same pipeline |
| B6 | O2 (95% coverage at launch) | Without working auth, zero data flows |
| B7 | O1 (MIND knows your body) | Reliability — partial data is better than no data due to cascading failure |

---

## INPUTS / OUTPUTS

### Primary Function: `sync_wearable_data(citizen_id, source)`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| citizen_id | str | The citizen's actor node ID in the graph |
| source | enum | Which integration to sync: GARMIN, HEALTHKIT, HEALTH_CONNECT, or a direct API name |
| since | datetime | Last sync watermark — only fetch data after this timestamp |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| nodes_written | int | Number of new body data nodes written to the graph |
| errors | list[SyncError] | Any errors encountered during fetch, normalize, or write |
| next_watermark | datetime | Updated watermark for the next sync cycle |

**Side Effects:**

- Body data nodes created in the citizen's graph (moment nodes for time-series, thing nodes for measurements)
- Links created between body data nodes and the citizen's actor node
- Sync watermark updated in integration state
- OAuth tokens refreshed if nearing expiry (cloud APIs)

---

## EDGE CASES

### E1: Wearable Disconnected Mid-Sync

```
GIVEN:  A user revokes wearable permissions (unlinks app or revokes OAuth) while a sync is in progress
THEN:   The current sync completes with whatever data was already fetched (no partial writes)
AND:    Subsequent syncs fail gracefully with "auth_revoked" error
AND:    Existing body data nodes in the graph remain (they are historical fact)
```

### E2: Wearable Reports Zero Data for a Period

```
GIVEN:  A user removes their wearable for 3 days (no HR, no sleep, no steps)
THEN:   The sync returns zero new data points — this is a valid result, not an error
AND:    No "gap-filling" or interpolation occurs — absence of data is data
```

### E3: Clock Skew Between Wearable and Server

```
GIVEN:  A wearable's internal clock is offset from UTC by more than 1 hour
THEN:   Timestamps are normalized to UTC using the timezone reported by the wearable or the user's configured timezone
AND:    If no timezone information is available, the timestamp is stored with a "timezone_unknown" flag
```

### E4: User Connects Multiple Wearables on Same Platform

```
GIVEN:  A user wears both an Apple Watch and an Oura Ring, both reporting to HealthKit
THEN:   HealthKit bridge fetches all available data (it doesn't know or care about the source device)
AND:    Deduplication handles any overlapping metrics (both devices report HR)
AND:    Device-specific data (Oura temperature, Apple Watch ECG) is captured without conflict
```

---

## ANTI-BEHAVIORS

### A1: Raw Vendor Data in the Graph

```
GIVEN:   Body data from any integration
WHEN:    Writing to the citizen's graph
MUST NOT: Write raw vendor JSON, vendor-specific field names, or vendor-specific units
INSTEAD:  All data passes through normalization before graph write
```

### A2: Silent Data Loss

```
GIVEN:   A sync cycle encounters data it cannot normalize (unknown metric type, corrupt payload)
WHEN:    The normalization step processes the data
MUST NOT: Silently drop the data without logging
INSTEAD:  Log the raw data and error, skip the record, continue with remaining data
```

### A3: Cross-Integration Failure Cascade

```
GIVEN:   Garmin API returns 503
WHEN:    The sync scheduler runs
MUST NOT: Skip HealthKit or Health Connect syncs because Garmin failed
INSTEAD:  Each integration syncs independently — failures are isolated
```

### A4: Backfilling Gaps with Synthetic Data

```
GIVEN:   No wearable data exists for a 3-day period
WHEN:    The citizen or Brief Matinal queries body data
MUST NOT: Generate interpolated, estimated, or synthetic data to fill the gap
INSTEAD:  Return the gap as-is — absence of data is truthful
```

---

## MARKERS

<!-- @mind:todo Define the full list of normalized body data types and their canonical units -->
<!-- @mind:todo Specify deduplication key format (source + metric_type + timestamp window?) -->
<!-- @mind:escalation Need to confirm: does Health Connect provide source device info, or just aggregated data? -->
