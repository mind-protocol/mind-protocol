# Wearable Bridges — Patterns: Aggregator-First Body Data Pipeline

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Wearable_Bridges.md
THIS:            PATTERNS_Wearable_Bridges.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Wearable_Bridges.md
ALGORITHM:       ./ALGORITHM_Wearable_Bridges.md
VALIDATION:      ./VALIDATION_Wearable_Bridges.md
IMPLEMENTATION:  ./IMPLEMENTATION_Wearable_Bridges.md
SYNC:            ./SYNC_Wearable_Bridges.md

IMPL:            mind-mcp: runtime/integrations/wearables/
                 mind-app: (HealthKit + Health Connect native modules)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source files

**After modifying this doc:**
1. Update the IMPL source files to match, OR
2. Add a TODO in SYNC_Wearable_Bridges.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Wearable_Bridges.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

MIND citizens reason about their human partner's state — energy, readiness, stress, sleep quality — but without physiological data, this reasoning is hollow. The citizen can see conversation tone and calendar density, but cannot see that the human's HRV crashed overnight, that sleep was fragmented, that resting heart rate is elevated.

Without body data:
- The Brief Matinal guesses about energy instead of measuring it.
- The citizen cannot distinguish "busy day" from "exhausted human who should reschedule."
- Patterns that emerge from the intersection of behavior and physiology (poor sleep correlating with poor decisions) are invisible.
- MIND's claim that "your AI knows you" has a blind spot covering the entire body.

The secondary problem is fragmentation. There are 10+ wearable brands, each with its own API, auth flow, data schema, and rate limits. Building direct integrations for all of them before launch is a time trap that delays the product value by months.

---

## THE PATTERN

**Aggregator-first, direct-API-second.**

Three aggregator integrations cover ~95% of wearable users:

| Aggregator | Coverage | Implementation Home | Status |
|------------|----------|---------------------|--------|
| **Garmin Connect API** | ~8-10% market, Garmin devices | mind-mcp (`runtime/integrations/wearables/`) | LIVE |
| **Apple HealthKit** | ~55% US market, Apple Watch + all iOS wearables (Oura, WHOOP, etc.) | mind-app (iOS native module) | S15-S16 |
| **Google Health Connect** | ~40% global, Samsung + Fitbit + Xiaomi + Amazfit + Polar + Withings + all Android | mind-app (Android native module) | S15-S16 |

The pattern has two layers:

1. **Native layer (mind-app):** HealthKit and Health Connect require native iOS/Android modules because they are on-device APIs — no cloud endpoint exists. The mind-app reads from the on-device health store and forwards normalized data to mind-mcp.

2. **API layer (mind-mcp):** Garmin Connect (and all post-launch direct APIs) are cloud APIs called server-side. mind-mcp handles OAuth, polling, and data normalization.

Both layers produce the same output: **normalized body data nodes** that enter the citizen's graph through the standard graph_write pipeline. The graph doesn't know or care whether a heart rate reading came from HealthKit, Health Connect, or a direct Garmin API call.

Post-launch, direct APIs add data that aggregators don't expose:

| Direct API | Premium Data | Effort | When |
|------------|--------------|--------|------|
| Oura Ring API | Readiness score, skin temperature | 2 days | Post-launch |
| WHOOP API | Strain score, recovery score | 2 days + partnership | Post-launch |
| Strava API | Activities, performance metrics | 2 days | Post-launch |
| Fitbit API | Fitbit Premium insights | 1-2 days | Post-launch |
| Samsung Health SDK | Body composition, blood pressure | 2 days | Post-launch |
| Polar AccessLink | Advanced sport/recovery metrics | 1-2 days | Post-launch |
| Withings API | Weight trends, blood pressure, ECG | 1-2 days | Post-launch |

---

## BEHAVIORS SUPPORTED

- **B1 (Body Data Reaches Graph)** — The aggregator pattern ensures that data from any wearable flows through one of three entry points into the graph, rather than requiring device-specific graph logic.
- **B2 (Unified Data Model)** — All integrations produce the same normalized schema. The graph sees "sleep_duration: 7.2h" not "Garmin sleep data" vs "Apple sleep data."
- **B3 (Graceful Degradation Without Wearable)** — Because body data is optional graph nodes (not required infrastructure), citizens without wearables simply have fewer nodes. No special null-handling needed.
- **B5 (Post-Launch Extension)** — The pattern explicitly separates launch (aggregators) from post-launch (direct APIs), so adding Oura or WHOOP never touches the core pipeline.

## BEHAVIORS PREVENTED

- **A1 (Device-Specific Graph Logic)** — Normalization happens before graph entry. The graph never contains raw Garmin JSON or Apple HealthKit samples.
- **A2 (Launch Blocked by Integration Count)** — The aggregator strategy prevents the trap of "we need 10 integrations before we can ship."
- **A3 (Duplicate Data from Overlapping Sources)** — Deduplication logic handles the case where the same data arrives via both an aggregator and a direct API (e.g., Oura sleep via HealthKit AND Oura direct API).

---

## PRINCIPLES

### Principle 1: Aggregator Coverage Before API Depth

Build the three aggregator bridges first. They cover ~95% of wearable users. Direct APIs add depth (readiness scores, strain, temperature trends) but serve only the subset of users on that specific device. Coverage first, depth second.

Why this matters: A user with an Apple Watch gets body data on day one via HealthKit. If we waited for a direct Apple Watch API (which doesn't exist as a separate cloud API anyway), we'd never ship.

### Principle 2: Normalize Before Graph Entry

Every integration — aggregator or direct — normalizes data into the same typed schema before writing nodes. The graph receives `{type: "heart_rate", value: 62, unit: "bpm", timestamp: ...}`, never raw vendor payloads.

Why this matters: If vendor-specific data enters the graph, every consumer (Brief Matinal, citizen reasoning, health patterns) needs vendor-specific parsing. Normalize once at the edge, consume uniformly everywhere.

### Principle 3: On-Device vs Cloud Is an Implementation Detail

HealthKit and Health Connect are on-device APIs (require native code in mind-app). Garmin Connect is a cloud API (called from mind-mcp). This distinction is real at the implementation level but invisible at the graph level. The citizen's graph has body data nodes. It doesn't know they came from an iPhone's HealthKit store vs a Garmin cloud API call.

Why this matters: It allows us to mix and match approaches per platform without architectural divergence. Adding a new cloud API is a mind-mcp integration. Adding a new on-device SDK is a mind-app native module. Both produce the same normalized output.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| Garmin Connect API | URL | Cloud OAuth2 API. HR, HRV, sleep, stress, body battery, SpO2, steps, calories. Already live. |
| Apple HealthKit | SDK | On-device iOS health store. Reads from Apple Watch, Oura, WHOOP, any iOS wearable. Requires native module. |
| Google Health Connect | SDK | On-device Android health store. Reads from Samsung, Fitbit, Xiaomi, Amazfit, Polar, Withings, any Android wearable. Requires native module. |
| Oura Ring API | URL | Cloud OAuth2. Readiness score, sleep stages, skin temperature. Post-launch. |
| WHOOP API | URL | Cloud OAuth2. Strain, recovery, sleep performance. Requires partnership. Post-launch. |
| Strava API | URL | Cloud OAuth2. Activities, segments, performance. Post-launch. |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| mind-mcp `runtime/integrations/wearables/` | Server-side API bridges (Garmin live, future direct APIs) |
| mind-app iOS native module | HealthKit access (on-device only) |
| mind-app Android native module | Health Connect access (on-device only) |
| mind-mcp `graph_write` | All normalized body data enters graph through standard write pipeline |
| L4 Schema | Body data nodes must be valid schema types (moment for time-series events, thing for measurements) |

---

## INSPIRATIONS

The aggregator-first pattern is borrowed from the fintech world where Plaid connects to thousands of banks through a handful of aggregation layers. Rather than integrating with every wearable brand, we integrate with the platform-level health stores that already aggregate device data.

Apple and Google have already done the hard work of standardizing wearable data into HealthKit and Health Connect. We leverage that effort rather than duplicating it.

---

## SCOPE

### In Scope

- Garmin Connect API integration (already live, maintenance and extension)
- Apple HealthKit native module in mind-app (S15-S16)
- Google Health Connect native module in mind-app (S15-S16)
- Normalized data schema for all body metrics (HR, HRV, sleep, stress, SpO2, temperature, VO2max, steps, calories, ECG)
- Graph node creation from normalized body data
- Deduplication when same data arrives from multiple sources
- OAuth2 flows for cloud APIs (Garmin, post-launch direct APIs)
- Permission request flows for on-device APIs (HealthKit, Health Connect)
- Post-launch direct API integration architecture (Oura, WHOOP, Strava, Fitbit, Samsung Health, Polar, Withings)

### Out of Scope

- **Health dashboards or visualizations** -> see: mind-app UI (if ever)
- **Medical analysis or diagnosis** -> not a MIND responsibility
- **Real-time biometric streaming** -> periodic sync only
- **Wearable device firmware or hardware** -> we read from software APIs
- **Replacing native health apps** -> complementary, not competitive
- **Data export or FHIR/HL7 compliance** -> not a healthcare platform

---

## MARKERS

<!-- @mind:todo Confirm Garmin Connect API scope — which endpoints are currently live in mind-mcp? -->
<!-- @mind:todo Define exact HealthKit data types to request permissions for in mind-app -->
<!-- @mind:proposition Consider a webhook/push model for Garmin instead of polling, if Garmin supports it -->
<!-- @mind:escalation WHOOP API requires partnership agreement — need Nicolas to initiate contact -->
