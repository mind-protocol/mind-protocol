# Wearable Bridges — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Wearable_Bridges.md
PATTERNS:        ./PATTERNS_Wearable_Bridges.md
BEHAVIORS:       ./BEHAVIORS_Wearable_Bridges.md
THIS:            VALIDATION_Wearable_Bridges.md (you are here)
ALGORITHM:       ./ALGORITHM_Wearable_Bridges.md
IMPLEMENTATION:  ./IMPLEMENTATION_Wearable_Bridges.md
SYNC:            ./SYNC_Wearable_Bridges.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These invariants protect the core value of the Wearable Bridges module: body data flows reliably from wearable devices into the citizen's graph in a normalized, deduplicated form, without corrupting the graph, leaking credentials, or creating dependencies that break citizens without wearables.

---

## INVARIANTS

### V1: Body Data Integrity

**Why we care:** If body data enters the graph in raw vendor format, every downstream consumer must parse vendor-specific schemas. This makes the graph vendor-dependent and breaks the unified reasoning model. The citizen cannot reason about "heart rate" if Garmin stores it differently than HealthKit.

```
MUST:   Every body data node in the graph conforms to the NormalizedBodySample schema
        (canonical metric_type, canonical unit, UTC timestamp, confidence score)
NEVER:  Raw vendor payloads, vendor-specific field names, or non-UTC timestamps
        appear in graph nodes
```

### V2: No Duplicate Measurements

**Why we care:** Duplicate body data corrupts pattern detection. If the same sleep session appears twice, the citizen sees 14 hours of sleep instead of 7. If the same HR reading appears from two sources, trend analysis is distorted. Deduplication is a correctness requirement, not an optimization.

```
MUST:   For any (citizen_id, metric_type, timestamp_bucket) tuple, at most one
        body data node exists in the graph
NEVER:  Two nodes representing the same physical measurement from different sources
        coexist in the graph
```

### V3: Source Isolation — No Cross-Integration Failure Cascade

**Why we care:** If a Garmin API outage prevents HealthKit data from syncing, the entire module is as unreliable as its weakest integration. Each source must fail independently. A user with both Garmin and Apple Watch must still get Apple Watch data when Garmin is down.

```
MUST:   Each integration source fetches, normalizes, and writes independently
NEVER:  A failure in one source's sync cycle prevents another source's sync cycle
        from executing or completing
```

### V4: Credentials Never Leak

**Why we care:** OAuth2 tokens grant access to sensitive health data. Leaked tokens expose the user's biometrics. This is both a privacy violation and a trust-destroying event.

```
MUST:   OAuth2 tokens and refresh tokens are encrypted at rest and never appear
        in logs, error messages, graph nodes, or git repositories
NEVER:  Tokens appear in plaintext outside of the secure credential store
```

### V5: Wearable-Free Citizens Are First-Class

**Why we care:** If any system breaks or degrades for citizens without wearables, the module has imposed a dependency it was never supposed to create. Body data is enrichment, not infrastructure.

```
MUST:   All citizen-facing systems (Brief Matinal, reasoning, graph queries)
        function identically with zero body data nodes as with thousands
NEVER:  A missing wearable connection causes errors, null reference exceptions,
        or degraded behavior in any system outside the wearable bridges module
```

### V6: Data Gaps Are Truthful

**Why we care:** If the system fills gaps with synthetic or interpolated data, the citizen reasons on fiction. A 3-day gap without wearable data is real — the human took off their watch. Fabricating data to fill that gap is worse than no data at all.

```
MUST:   Periods with no wearable data produce zero body data nodes — the gap
        is preserved as-is in the graph
NEVER:  Interpolated, estimated, or synthetic data is generated to fill
        gaps in wearable data
```

### V7: Graph Nodes Are Schema-Valid

**Why we care:** Body data nodes must be valid L4 schema nodes (moment or thing with proper fields). Invalid nodes corrupt the graph and break traversal, embedding, and physics. The graph is not a dumping ground.

```
MUST:   Every body data node passes L4 schema validation before graph write
        (valid node_type, non-empty content, non-empty synthesis, valid links)
NEVER:  A body data node is written to the graph without passing schema validation
```

### V8: Sync Progress Is Monotonic

**Why we care:** If the sync watermark goes backward, data is re-fetched and potentially re-written (creating duplicates despite dedup, if the dedup window has shifted). The watermark must only advance.

```
MUST:   The last_synced_at watermark for each (citizen_id, source) pair only
        moves forward in time
NEVER:  A sync cycle sets the watermark to a time earlier than the current value
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable |
| **HIGH** | Major value lost | Degraded severely |
| **MEDIUM** | Partial value lost | Works but worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Body data integrity (normalized, canonical) | CRITICAL |
| V2 | No duplicate measurements | CRITICAL |
| V3 | Source isolation (no failure cascade) | HIGH |
| V4 | Credentials never leak | CRITICAL |
| V5 | Wearable-free citizens are first-class | HIGH |
| V6 | Data gaps are truthful (no fabrication) | HIGH |
| V7 | Graph nodes are schema-valid | CRITICAL |
| V8 | Sync progress is monotonic | MEDIUM |

---

## MARKERS

<!-- @mind:todo Add invariant for rate limiting compliance (per-API limits respected) -->
<!-- @mind:proposition Consider an invariant for data freshness — body data older than N hours triggers a warning -->
<!-- @mind:escalation V4 implementation depends on credential store choice — what secure storage does mind-mcp use? -->
