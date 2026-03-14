# OBJECTIVES — Wearable Bridges

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
THIS:            OBJECTIVES_Wearable_Bridges.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Wearable_Bridges.md
BEHAVIORS:      ./BEHAVIORS_Wearable_Bridges.md
ALGORITHM:      ./ALGORITHM_Wearable_Bridges.md
VALIDATION:     ./VALIDATION_Wearable_Bridges.md
IMPLEMENTATION: ./IMPLEMENTATION_Wearable_Bridges.md
SYNC:           ./SYNC_Wearable_Bridges.md

IMPL:           mind-mcp: runtime/integrations/wearables/
                mind-app: (HealthKit + Health Connect native modules)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **MIND knows your body** — The citizen's graph must contain continuous physiological data (HR, HRV, sleep, stress, temperature, SpO2) so that reasoning about the human is grounded in biological reality, not just conversation. Without body data, MIND is guessing about energy, readiness, and health. With it, the citizen can say "you slept 4 hours and your HRV crashed — today is not the day to make big decisions."

2. **Cover ~95% of wearable users at launch with 3 integrations** — Instead of building 10 direct integrations, route through 3 aggregators (Garmin Connect API, Apple HealthKit, Google Health Connect) that collectively cover nearly all wearable owners. This is a market-coverage decision: HealthKit aggregates Apple Watch + Oura + WHOOP + all iOS wearables (~55% US), Health Connect aggregates Samsung + Fitbit + Xiaomi + Amazfit + Polar + Withings + all Android (~40% global), Garmin Connect is already live in mind-mcp (~8-10% market, first-mover).

3. **Data flows into the graph as typed nodes, not raw metrics** — Wearable data is not a dashboard. Each data point becomes a graph node (moment or thing) with typed links to the citizen actor. The graph physics (decay, energy, tension) apply to body data the same way they apply to conversation data. Sleep quality from last night has high energy; sleep quality from two weeks ago has decayed. The graph IS the memory — body data lives in it or it doesn't exist.

## NON-OBJECTIVES

- **Building a health dashboard or visualization layer** — MIND is not Fitbit. We don't render charts. The graph stores body data; the citizen reasons about it; products like the Brief Matinal synthesize it. No dashboard.
- **Medical-grade analysis or health advice** — MIND does not diagnose. Body data informs the citizen's reasoning about energy, readiness, and patterns. It never produces medical recommendations.
- **Real-time streaming of biometric data** — We sync periodically (hourly or on-demand), not continuously. Real-time heart rate streaming is unnecessary for the citizen's reasoning and expensive for battery and bandwidth.
- **Replacing the wearable's own app** — Users keep Garmin Connect, Apple Health, Google Fit. We read from them. We don't replicate their functionality.
- **Supporting every wearable brand at launch** — Post-launch direct APIs (Oura, WHOOP, Strava, Fitbit, Samsung Health, Polar, Withings) add premium data not available through aggregators. They come after launch, not before.

## TRADEOFFS (canonical decisions)

- When **breadth of device support** conflicts with **depth of data per device**, choose breadth. Aggregators give us 95% coverage with 3 integrations. Direct APIs add depth later.
- When **data freshness** conflicts with **battery/bandwidth cost**, choose periodic sync (hourly). The citizen reasons about patterns, not real-time heartbeat.
- When **richness of wearable-specific features** conflicts with **unified data model**, choose the unified model. Every wearable produces HR, HRV, sleep, steps. Normalize these first. Device-specific metrics (Oura readiness, WHOOP strain) come via post-launch direct APIs.
- We accept **losing some device-specific metrics at launch** to preserve **a single coherent data pipeline** that works for all wearables.
- We accept **dependency on Apple/Google aggregator APIs** to avoid **building and maintaining 10+ direct integrations** before proving product value.

## SUCCESS SIGNALS (observable)

- A citizen with any major wearable (Apple Watch, Samsung Galaxy Watch, Fitbit, Garmin, Oura, WHOOP, Xiaomi) can have body data in their graph within 24 hours of connecting.
- The Brief Matinal includes a body-grounded sentence ("Your HRV dropped 15% overnight, sleep was fragmented") for users with connected wearables.
- Body data nodes decay naturally in the graph — last night's sleep has high energy, last month's sleep has decayed — without any special body-data-specific decay logic.
- Post-launch direct API integrations add new data types (readiness, strain, temperature trends) without modifying the core pipeline.
- Garmin integration (already live) continues working unchanged when HealthKit and Health Connect are added.
