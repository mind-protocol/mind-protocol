# Wearable Bridges — Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Claude Opus (architect)
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Strategy: 3 aggregators (Garmin, HealthKit, Health Connect) cover ~95% of wearable market at launch
- Garmin Connect API adapter is LIVE in mind-mcp
- Normalized data schema (NormalizedBodySample) is defined
- Pipeline architecture: fetch -> normalize -> dedup -> graph_write

**What's still being designed:**
- HealthKit native module (mind-app iOS) — scheduled S15-S16 (12-23 May 2026)
- Health Connect native module (mind-app Android) — scheduled S15-S16 (12-23 May 2026)
- App-to-server bridge transport (HTTP POST vs gRPC vs WebSocket)
- Sync state storage location (graph nodes vs separate DB table)
- Deduplication key format and timestamp bucketing details
- Health checks (all 6 pending)

**What's proposed (v2+):**
- Oura Ring direct API — readiness, skin temperature (2 days, post-launch)
- WHOOP direct API — strain, recovery (2 days + partnership agreement, post-launch)
- Strava direct API — activities, performance (2 days, post-launch)
- Fitbit direct API — Premium insights (1-2 days, post-launch)
- Samsung Health SDK — body composition, blood pressure (2 days, post-launch)
- Polar AccessLink — advanced sport/recovery (1-2 days, post-launch)
- Withings API — weight, blood pressure, ECG (1-2 days, post-launch)
- Webhook/push model for Garmin (if supported) instead of polling

---

## CURRENT STATE

The Wearable Bridges module exists as a complete documentation chain (7 files) with clear architecture but limited implementation. The Garmin Connect API adapter is live in the mind-mcp repository, providing the first working wearable integration. The remaining two launch integrations (HealthKit, Health Connect) require native mobile modules that will be built in mind-app during S15-S16.

The core pipeline design is settled: every wearable source produces NormalizedBodySample structs that flow through a common dedup/write pipeline into the citizen's graph. The adapter interface is defined but not yet codified as an abstract class. The dedup logic is designed but not yet implemented.

No code exists yet in this repository (mind-protocol) — the Wearable Bridges module lives in mind-mcp (server-side) and mind-app (client-side). This doc chain in mind-protocol serves as the L4 specification.

---

## IN PROGRESS

### Doc Chain Creation

- **Started:** 2026-03-14
- **By:** Claude Opus (architect)
- **Status:** Complete
- **Context:** 7-file doc chain created covering objectives, patterns, behaviors, algorithm, validation, implementation, health, and sync. Captures the aggregator-first strategy, normalized data schema, pipeline architecture, and health check specifications.

---

## RECENT CHANGES

### 2026-03-14: Doc Chain Created

- **What:** Full documentation chain for Wearable Bridges module (7 files)
- **Why:** Codify the aggregator-first strategy, normalize the data pipeline design, establish validation invariants before HealthKit/Health Connect implementation begins in S15-S16
- **Files:** `docs/product/wearable-bridges/` (OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC)
- **Struggles/Insights:** The main tension is between the two repos (mind-mcp for server-side, mind-app for native modules). The doc chain lives in mind-protocol as L4 spec, but implementation will span mind-mcp and mind-app. This is by design — the doc chain describes the system boundary, not the code location.

---

## KNOWN ISSUES

### WHOOP API Requires Partnership

- **Severity:** low (post-launch)
- **Symptom:** Cannot integrate WHOOP API without a formal partnership agreement
- **Suspected cause:** WHOOP restricts API access to approved partners
- **Attempted:** Nothing yet — this is a post-launch item

### App-to-Server Transport Undecided

- **Severity:** medium (blocks HealthKit/Health Connect implementation)
- **Symptom:** No decision on how mind-app sends normalized body data to mind-mcp
- **Suspected cause:** Multiple viable options (REST POST, gRPC, WebSocket) with different tradeoffs
- **Attempted:** Documented in IMPLEMENTATION as an escalation marker

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (when implementing HealthKit/Health Connect in S15-S16)

**Where I stopped:** Documentation chain complete. No implementation code written in mind-protocol. Garmin adapter exists in mind-mcp.

**What you need to understand:**
- This module spans TWO repos: mind-mcp (server pipeline + cloud APIs) and mind-app (native HealthKit/Health Connect modules). The doc chain here in mind-protocol is the L4 specification that both repos implement against.
- The Garmin adapter is already live — study it before building HealthKit/Health Connect. It establishes the adapter pattern.
- The dedup logic is critical and not yet implemented. When Oura data arrives via both HealthKit AND Oura direct API (post-launch), dedup must resolve correctly.

**Watch out for:**
- HealthKit and Health Connect are ON-DEVICE APIs — they cannot be called from a server. The mind-app must read from the health store and send data to mind-mcp. This is fundamentally different from the Garmin pattern (cloud API called from server).
- Apple and Google both have strict permission models. HealthKit requires specific entitlements. Health Connect requires declaring data types upfront. Missing a permission = silent data absence.
- Background refresh on iOS is unreliable (iOS kills background tasks aggressively). Plan for batched data arriving hours after measurement.

**Open questions I had:**
- Should sync state (watermarks, tokens) live in the graph as nodes, or in a separate DB table? Graph-as-truth suggests graph nodes, but the operational overhead of querying the graph for sync metadata on every cycle might be high.
- What authentication does the bridge endpoint use? The mind-app POSTs body data — how does mind-mcp verify the request is from a legitimate app instance and not a spoofed sender?

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Full doc chain created for Wearable Bridges. Strategy is aggregator-first: 3 integrations (Garmin LIVE, HealthKit S15-S16, Health Connect S15-S16) cover ~95% of wearable market at launch. Post-launch, 7 direct APIs add premium data. All data normalized to canonical schema before graph write. 8 validation invariants defined. Health checks specified but pending implementation.

**Decisions made:**
- Aggregator-first strategy (3 integrations at launch vs 10+ direct APIs)
- NormalizedBodySample as the canonical data schema across all sources
- Confidence-based dedup (direct API wins over aggregator when same data arrives from both)
- Body data as graph nodes (moments for time-series, things for measurements) with decay
- Permanence 0.3 for body data links (recent readings matter, old ones decay naturally)

**Needs your input:**
- WHOOP partnership: need to initiate contact for API access (post-launch but lead time may be long)
- App-to-server transport: REST POST seems simplest, but gRPC would be more efficient for large batches. Preference?
- S15-S16 timeline for HealthKit + Health Connect: still accurate?

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: Adapter interface defined in docs but not codified as abstract class in mind-mcp
- [ ] DOCS->IMPL: NormalizedBodySample schema defined in docs but not as Pydantic model in mind-mcp
- [ ] DOCS->IMPL: Dedup logic designed but not implemented
- [ ] DOCS->IMPL: Health checks specified but all pending

### Tests to Run

```bash
# No tests exist yet — pipeline code not written
# When pipeline exists:
pytest tests/integrations/test_wearable_sync_pipeline.py
pytest tests/integrations/test_wearable_normalization.py
pytest tests/integrations/test_wearable_deduplication.py
```

### Immediate

- [ ] Verify Garmin adapter in mind-mcp matches patterns described here
- [ ] Decide app-to-server transport (REST vs gRPC)
- [ ] Codify WearableAdapter abstract class in mind-mcp

### Later

- [ ] Build HealthKit native module in mind-app (S15-S16)
- [ ] Build Health Connect native module in mind-app (S15-S16)
- [ ] Implement dedup engine
- [ ] Implement health checks
- [ ] Initiate WHOOP partnership conversation
- IDEA: Body data could feed into a "physical readiness score" that the citizen computes — not a dashboard metric, but a graph-derived synthesis

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the architecture. The aggregator-first strategy is well-reasoned and avoids the trap of building 10 integrations before proving value. The doc chain is thorough. The main uncertainty is the app-to-server transport — it's an implementation detail but it affects the HealthKit/Health Connect adapter shape.

**Threads I was holding:**
- The Garmin adapter exists but I haven't verified its current structure against this doc chain. There may be drift.
- The dedup logic handles the "same metric from two sources" case well, but what about the "similar but not identical metric" case? Garmin's stress score and Apple Watch's stress estimate may measure different things but have the same metric_type. Need to think about whether these are the same measurement or different ones.
- The confidence scoring (direct API=0.95 vs aggregator=0.85) is a reasonable starting point but will need calibration with real data.

**Intuitions:**
- The Brief Matinal will be the killer use case for body data. A morning brief that says "your HRV crashed and you only got 5 hours of sleep" is immediately, viscerally useful.
- Post-launch, Oura and WHOOP direct APIs will be the most valuable additions — their proprietary metrics (readiness, strain) are genuinely useful and not available through aggregators.
- The dedup problem will be harder than it looks when we have both aggregator and direct API for the same device.

**What I wish I'd known at the start:**
That HealthKit and Health Connect are fundamentally different from cloud APIs — they're on-device stores that require native code. This shapes the entire architecture (two-repo split, bridge pattern, batch delivery).

---

## POINTERS

| What | Where |
|------|-------|
| Garmin adapter (live) | mind-mcp: `runtime/integrations/wearables/` |
| Brief Matinal (consumer of body data) | `docs/product/brief-matinal/OBJECTIVES_Brief_Matinal.md` |
| L4 Schema (node type constraints) | `docs/l4/schema/` |
| Graph write pipeline | mind-mcp: `graph_write` tool |
| HealthKit/Health Connect roadmap | S15-S16 (12-23 May 2026) |
