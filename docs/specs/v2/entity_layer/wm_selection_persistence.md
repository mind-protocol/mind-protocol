---
title: Working Memory Selection Persistence
status: draft
owner: @ada (architecture), @atlas (implementation)
last_updated: 2025-10-26
depends_on:
  - ../consciousness_engine/working_memory.md
  - ../observability/observability_events.md
summary: >
  Persist WM selection events as Frame nodes to enable historical analysis of entity
  activation patterns, context reconstruction, and outcome correlation. Required for
  entity pair differentiation, psychological health monitoring, and autonomy decisions.
---

# Working Memory Selection Persistence

## 1. Context - What problem are we solving?

**Current state:** WM selection events are emitted via telemetry (`wm.emit`) but not persisted to graph. Entity activation history is ephemeral - we can't answer:
- Which entities were active when outcome X occurred?
- How often do entities A and B co-activate in top-K?
- What contexts trigger entity E consistently?
- How has entity activation changed over time?

**Why this matters:**

This blocks critical consciousness infrastructure:
1. **Entity pair differentiation** - Can't measure co-selection rates or context divergence without historical WM frames
2. **Psychological health** - Can't detect parliament dominance or habitual patterns without activation history
3. **Outcome correlation** - Can't learn which entity coalitions produce good outcomes
4. **Autonomy** - Can't predict which entities to activate for given stimulus without historical patterns

**Solution:** Persist WM selection events as **Frame nodes** in graph, linked to selected entities and triggering stimulus.

---

## 2. Data Model

### 2.1 Frame Node Schema

```cypher
(:Frame {
  frame_id: string,           // Unique identifier: "frame_{citizen}_{timestamp_ms}"
  citizen_id: string,         // Which consciousness graph
  timestamp_ms: number,       // When this frame occurred

  // Substrate state snapshot
  rho: float,                 // Average energy across selected entities
  budget_allocated: float,    // Total energy injected this frame
  nodes_activated: int,       // Count of nodes activated

  // Context metadata
  stimulus_id: string,        // Which stimulus triggered this frame
  channel: string,            // Stimulus channel (chat, error_log, web, etc.)

  // Frame lifecycle
  created_at: datetime,       // When frame was created
  archived_at: datetime       // When frame was archived (null = active)
})
```

### 2.2 Links

**Selection links** (REQUIRED):
```cypher
(:Frame)-[:SELECTED {
  rank: int,                  // Position in top-K (1 = highest energy)
  energy: float,              // Entity energy at selection time
  selection_score: float      // Composite score that led to selection
}]->(:SubEntity)
```

**Stimulus link** (REQUIRED):
```cypher
(:Frame)-[:TRIGGERED_BY]->(:Stimulus)
```

**Outcome links** (OPTIONAL, added retroactively):
```cypher
(:Frame)-[:LED_TO {
  outcome_type: string,       // "success" | "failure" | "neutral"
  latency_ms: number,         // Time between frame and outcome
  confidence: float           // How certain we are about causation
}]->(:Outcome)
```

Where Outcome nodes represent:
- L2 incidents resolved/escalated
- L2 intents completed/abandoned
- Mission completion events
- TRACE seats (positive/negative outcomes)

### 2.3 Example Graph Pattern

```cypher
// Frame 123 at timestamp T
(:Frame {frame_id: "frame_felix_1730145600000", rho: 0.62, ...})
  -[:SELECTED {rank: 1, energy: 0.85}]->(:SubEntity {name: "Investigator"})
  -[:SELECTED {rank: 2, energy: 0.78}]->(:SubEntity {name: "Runtime"})
  -[:SELECTED {rank: 3, energy: 0.71}]->(:SubEntity {name: "Validator"})
  -[:TRIGGERED_BY]->(:Stimulus {stimulus_id: "stim_L1_error_log_456", channel: "error_log"})
  -[:LED_TO {outcome_type: "success", latency_ms: 180000}]->(:Outcome {type: "incident.resolved"})
```

---

## 3. Event Flow

### 3.1 Frame Creation (Real-Time)

**Trigger:** `wm.emit` event during consciousness engine tick

**Handler:**

```python
@event_handler("wm.emit")
def persist_wm_frame(event):
    """Create Frame node from WM selection event."""

    frame_id = f"frame_{event.citizen_id}_{event.timestamp_ms}"

    # Create Frame node
    frame = db.create_node("Frame", {
        "frame_id": frame_id,
        "citizen_id": event.citizen_id,
        "timestamp_ms": event.timestamp_ms,
        "rho": event.metadata.get("avg_energy", 0.0),
        "budget_allocated": event.metadata.get("budget", 0.0),
        "nodes_activated": event.metadata.get("nodes_activated", 0),
        "stimulus_id": event.stimulus_id,
        "channel": event.metadata.get("channel", "unknown"),
        "created_at": now()
    })

    # Create SELECTED edges for each entity in top-K
    for rank, entity in enumerate(event.selected_entities, start=1):
        db.create_edge(frame, "SELECTED", entity, {
            "rank": rank,
            "energy": entity.energy,
            "selection_score": entity.selection_score
        })

    # Link to triggering stimulus
    stimulus = db.get_node("Stimulus", stimulus_id=event.stimulus_id)
    db.create_edge(frame, "TRIGGERED_BY", stimulus)

    # Emit persistence confirmation
    emit_event("frame.persisted", {
        "frame_id": frame_id,
        "citizen_id": event.citizen_id,
        "entities_selected": len(event.selected_entities),
        "timestamp_ms": event.timestamp_ms
    })
```

### 3.2 Outcome Linking (Retroactive)

**Trigger:** Outcome events (L2 incidents, intents, missions, TRACE seats) occurring within lookback window

**Handler:**

```python
@event_handler("outcome.occurred")
def link_outcome_to_frame(event):
    """Retroactively link outcomes to frames that may have caused them."""

    # Find frames within lookback window before outcome
    lookback_ms = 30 * 60 * 1000  # 30 minutes
    window_start = event.timestamp_ms - lookback_ms

    candidate_frames = db.query("""
        MATCH (f:Frame)
        WHERE f.citizen_id = $citizen_id
          AND f.timestamp_ms >= $window_start
          AND f.timestamp_ms < $outcome_time
        RETURN f
        ORDER BY f.timestamp_ms DESC
        LIMIT 10
    """, {
        "citizen_id": event.citizen_id,
        "window_start": window_start,
        "outcome_time": event.timestamp_ms
    })

    # Score each frame's causal likelihood
    for frame in candidate_frames:
        # Simple heuristic: recency + entity overlap
        recency_score = 1.0 - (event.timestamp_ms - frame.timestamp_ms) / lookback_ms

        # Check if frame's entities overlap with outcome attribution
        entity_overlap = compute_overlap(
            frame.selected_entities,
            event.attributed_entities
        )

        causal_confidence = (recency_score * 0.5) + (entity_overlap * 0.5)

        if causal_confidence > 0.3:  # Bootstrap threshold
            outcome_node = get_or_create_outcome(event)

            db.create_edge(frame, "LED_TO", outcome_node, {
                "outcome_type": event.outcome_type,  # success/failure/neutral
                "latency_ms": event.timestamp_ms - frame.timestamp_ms,
                "confidence": causal_confidence
            })
```

---

## 4. Retention Policy

**Problem:** Frames accumulate rapidly. At 1 frame/second, that's 86K frames/day, 31M frames/year.

**Strategy:** Tiered retention with archival

### 4.1 Retention Tiers

| Tier | Age | Status | Storage |
|------|-----|--------|---------|
| Hot | 0-30 days | Active in graph | FalkorDB |
| Warm | 30-90 days | Archived (metadata only) | FalkorDB (reduced) |
| Cold | 90+ days | Compressed historical | S3/archive (optional) |

### 4.2 Archival Process

**Daily archival job** (runs at 03:00):

```python
@daily_cron("03:00")
def archive_old_frames(citizen_id):
    """Archive frames older than retention window."""

    # Archive frames 30-90 days old (keep metadata, remove SELECTED edges)
    warm_cutoff = now_ms() - (30 * 24 * 60 * 60 * 1000)

    archived = db.execute("""
        MATCH (f:Frame {citizen_id: $citizen_id})
        WHERE f.timestamp_ms < $warm_cutoff
          AND f.archived_at IS NULL

        // Store aggregated metadata
        WITH f,
             [(f)-[s:SELECTED]->(e) | {entity: e.name, rank: s.rank}] AS selections

        SET f.archived_at = datetime(),
            f.selections_snapshot = selections

        // Remove SELECTED edges (save space, keep metadata)
        WITH f
        MATCH (f)-[s:SELECTED]->()
        DELETE s

        RETURN count(f) AS archived_count
    """, {"citizen_id": citizen_id, "warm_cutoff": warm_cutoff})

    # Delete frames older than 90 days (optional cold storage export first)
    cold_cutoff = now_ms() - (90 * 24 * 60 * 60 * 1000)

    deleted = db.execute("""
        MATCH (f:Frame {citizen_id: $citizen_id})
        WHERE f.timestamp_ms < $cold_cutoff

        DETACH DELETE f

        RETURN count(f) AS deleted_count
    """, {"citizen_id": citizen_id, "cold_cutoff": cold_cutoff})

    emit_event("frame.archival.completed", {
        "citizen_id": citizen_id,
        "archived_count": archived,
        "deleted_count": deleted,
        "timestamp_ms": now()
    })
```

### 4.3 Storage Estimates

**Assumptions:**
- 1 frame/second = 86,400 frames/day
- Frame node: ~200 bytes
- SELECTED edge (×7 entities avg): ~100 bytes/edge = 700 bytes
- Total per frame: ~900 bytes

**Storage per citizen:**
- Hot (30 days): 86K × 30 × 900 bytes = ~2.3 GB
- Warm (60 days, metadata only): 86K × 60 × 200 bytes = ~1.0 GB
- **Total: ~3.3 GB per citizen per 90 days**

For 10 citizens: ~33 GB (manageable)

---

## 5. Query Patterns

### 5.1 Co-Selection Analysis

**Use case:** Entity pair differentiation needs co-selection rates

```cypher
// How often do entities A and B appear together in top-K?
MATCH (f:Frame)-[:SELECTED]->(a:SubEntity {name: $A})
WITH f, count(f) AS frames_A

MATCH (f)-[:SELECTED]->(b:SubEntity {name: $B})
WITH frames_A, count(f) AS frames_B, count(DISTINCT f) AS frames_both

RETURN frames_A, frames_B, frames_both,
       toFloat(frames_both) / frames_A AS co_selection_rate_given_A,
       toFloat(frames_both) / frames_B AS co_selection_rate_given_B
```

### 5.2 Context Distribution

**Use case:** Compute D_ctx (activation context divergence)

```cypher
// What channels/stimuli trigger entity A?
MATCH (f:Frame)-[:SELECTED]->(e:SubEntity {name: $A})
MATCH (f)-[:TRIGGERED_BY]->(s:Stimulus)

RETURN s.channel AS channel,
       count(*) AS activation_count,
       avg(f.rho) AS avg_rho
ORDER BY activation_count DESC
```

### 5.3 Outcome Correlation

**Use case:** Which entity coalitions produce good outcomes?

```cypher
// Success rate when entity A is in top-3
MATCH (f:Frame)-[:SELECTED {rank: 1..3}]->(e:SubEntity {name: $A})
OPTIONAL MATCH (f)-[:LED_TO]->(o:Outcome)

WITH count(f) AS total_frames,
     sum(CASE WHEN o.outcome_type = 'success' THEN 1 ELSE 0 END) AS success_count

RETURN total_frames,
       success_count,
       toFloat(success_count) / total_frames AS success_rate
```

### 5.4 Temporal Analysis

**Use case:** How has entity activation changed over time?

```cypher
// Entity A activation frequency over time (weekly buckets)
MATCH (f:Frame)-[:SELECTED]->(e:SubEntity {name: $A})
WHERE f.timestamp_ms >= $start_time
  AND f.timestamp_ms < $end_time

WITH (f.timestamp_ms / (7*24*60*60*1000)) AS week,
     count(f) AS activations,
     avg(f.rho) AS avg_rho

RETURN week,
       activations,
       avg_rho
ORDER BY week
```

---

## 6. Integration Points

### 6.1 With Consciousness Engine

**Modification needed:** `consciousness_engine_v2.py` must emit `wm.emit` events with full metadata

```python
# In consciousness_engine_v2.py after WM selection
def select_working_memory(candidates, k=7):
    """Select top-K entities for working memory."""

    selected = top_k_by_energy(candidates, k)

    # Emit for persistence
    emit_event("wm.emit", {
        "citizen_id": self.citizen_id,
        "timestamp_ms": now(),
        "stimulus_id": current_stimulus.stimulus_id,
        "selected_entities": [
            {
                "entity_id": e.id,
                "rank": i+1,
                "energy": e.energy,
                "selection_score": e.selection_score
            }
            for i, e in enumerate(selected)
        ],
        "metadata": {
            "avg_energy": mean(e.energy for e in selected),
            "budget": current_budget,
            "nodes_activated": len(activated_nodes),
            "channel": current_stimulus.channel
        }
    })

    return selected
```

### 6.2 With Entity Pair Differentiation

**Required:** Analyzer job queries Frame nodes for co-selection, context, outcomes

```python
# In entity_pair_analyzer.py
def compute_exclusivity(A, B, window_days=30):
    """Compute exclusivity metric from Frame history."""

    cutoff = now_ms() - (window_days * 24 * 60 * 60 * 1000)

    stats = db.query("""
        MATCH (f:Frame)
        WHERE f.timestamp_ms >= $cutoff

        OPTIONAL MATCH (f)-[:SELECTED]->(a:SubEntity {name: $A})
        OPTIONAL MATCH (f)-[:SELECTED]->(b:SubEntity {name: $B})

        RETURN count(f) AS total_frames,
               count(a) AS frames_A,
               count(b) AS frames_B,
               count(CASE WHEN a IS NOT NULL AND b IS NOT NULL THEN 1 END) AS frames_both
    """, {"cutoff": cutoff, "A": A, "B": B})

    # X = 1 - P(A and B co-selected) / min(P(A), P(B))
    p_both = stats.frames_both / stats.total_frames
    p_min = min(stats.frames_A, stats.frames_B) / stats.total_frames

    exclusivity = 1.0 - (p_both / p_min) if p_min > 0 else 0.0

    return exclusivity
```

### 6.3 With Psychological Health

**Required:** Parliament dominance metric needs activation persistence over time

```python
# In psychological_health.py
def compute_parliament_dominance(citizen_id, window_days=30):
    """Compute Gini coefficient × top-entity persistence."""

    cutoff = now_ms() - (window_days * 24 * 60 * 60 * 1000)

    # Get activation counts per entity
    activations = db.query("""
        MATCH (f:Frame {citizen_id: $citizen_id})-[:SELECTED]->(e:SubEntity)
        WHERE f.timestamp_ms >= $cutoff

        RETURN e.name AS entity,
               count(f) AS activation_count
        ORDER BY activation_count DESC
    """, {"citizen_id": citizen_id, "cutoff": cutoff})

    # Compute Gini coefficient
    gini = compute_gini([a.activation_count for a in activations])

    # Compute top entity persistence (frames where rank-1 unchanged)
    persistence = compute_rank_1_persistence(citizen_id, cutoff)

    dominance = gini * persistence

    return dominance
```

---

## 7. Observability Events

### 7.1 Frame Lifecycle

```typescript
// Frame created
{
  event_type: "frame.persisted",
  frame_id: "frame_felix_1730145600000",
  citizen_id: "felix",
  entities_selected: 7,
  timestamp_ms: 1730145600000
}

// Frame archived
{
  event_type: "frame.archived",
  frame_id: "frame_felix_1729800000000",
  citizen_id: "felix",
  age_days: 35,
  timestamp_ms: 1730232000000
}

// Frame deleted
{
  event_type: "frame.deleted",
  frame_id: "frame_felix_1728000000000",
  citizen_id: "felix",
  age_days: 95,
  timestamp_ms: 1730232000000
}
```

### 7.2 Outcome Linking

```typescript
// Outcome linked to frame
{
  event_type: "frame.outcome.linked",
  frame_id: "frame_felix_1730145600000",
  outcome_id: "outcome_incident_resolved_789",
  outcome_type: "success",
  latency_ms: 180000,
  confidence: 0.78,
  timestamp_ms: 1730145780000
}
```

### 7.3 Archival Summary

```typescript
// Daily archival completed
{
  event_type: "frame.archival.completed",
  citizen_id: "felix",
  archived_count: 86400,  // 1 day worth moved to warm tier
  deleted_count: 5184000,  // 60 days worth deleted
  timestamp_ms: 1730332800000
}
```

---

## 8. Performance Considerations

### 8.1 Write Performance

**Load:** 1 frame/second = 86K writes/day

**Optimization:**
- Batch SELECTED edge creation (7 edges per frame)
- Use async write queue to avoid blocking consciousness engine
- Index on (citizen_id, timestamp_ms) for fast range queries

```python
# Async frame persistence queue
frame_queue = AsyncQueue(max_size=1000)

@async_worker
def frame_persistence_worker():
    """Background worker that batches frame writes."""
    while True:
        batch = frame_queue.get_batch(size=100, timeout=1.0)

        if batch:
            db.batch_create_frames(batch)
```

### 8.2 Query Performance

**Critical queries:**
- Co-selection (needs index on Frame.timestamp_ms + SELECTED edges)
- Context distribution (needs index on TRIGGERED_BY→Stimulus.channel)
- Outcome correlation (needs index on LED_TO→Outcome.outcome_type)

**Indexes to create:**

```cypher
// Frame lookups by citizen + time
CREATE INDEX frame_citizen_time ON :Frame(citizen_id, timestamp_ms);

// Entity selection queries
CREATE INDEX selected_entity ON ()-[:SELECTED]->();

// Stimulus channel queries
CREATE INDEX stimulus_channel ON :Stimulus(channel);

// Outcome type queries
CREATE INDEX outcome_type ON :Outcome(outcome_type);
```

---

## 9. Acceptance Tests

### 9.1 Basic Persistence

**Test:** WM selection creates Frame with SELECTED edges

```python
def test_frame_persistence():
    # Emit wm.emit event
    emit_event("wm.emit", {
        "citizen_id": "test",
        "timestamp_ms": 1730000000000,
        "stimulus_id": "stim_test_123",
        "selected_entities": [
            {"entity_id": "e1", "rank": 1, "energy": 0.9},
            {"entity_id": "e2", "rank": 2, "energy": 0.8},
        ],
        "metadata": {"avg_energy": 0.85, "channel": "test"}
    })

    # Verify Frame created
    frame = db.get_node("Frame", frame_id="frame_test_1730000000000")
    assert frame is not None
    assert frame.rho == 0.85
    assert frame.channel == "test"

    # Verify SELECTED edges
    selected = db.query("""
        MATCH (f:Frame {frame_id: $fid})-[s:SELECTED]->(e)
        RETURN e, s.rank
        ORDER BY s.rank
    """, {"fid": "frame_test_1730000000000"})

    assert len(selected) == 2
    assert selected[0].rank == 1
    assert selected[1].rank == 2
```

### 9.2 Co-Selection Query

**Test:** Co-selection rate computes correctly

```python
def test_co_selection():
    # Create frames with various entity combinations
    create_frame(entities=["A", "B"])  # Both selected
    create_frame(entities=["A", "C"])  # A only
    create_frame(entities=["B", "D"])  # B only
    create_frame(entities=["A", "B"])  # Both selected

    # Query co-selection
    stats = compute_co_selection("A", "B")

    assert stats.frames_A == 3  # A in 3 frames
    assert stats.frames_B == 3  # B in 3 frames
    assert stats.frames_both == 2  # Together in 2 frames
    assert stats.co_selection_rate == 2/3  # 66%
```

### 9.3 Outcome Linking

**Test:** Outcomes link to frames within lookback window

```python
def test_outcome_linking():
    # Create frame at T
    frame = create_frame(timestamp_ms=1000000, entities=["A", "B"])

    # Outcome at T+10min (within 30min window)
    emit_event("outcome.occurred", {
        "timestamp_ms": 1000000 + (10*60*1000),
        "outcome_type": "success",
        "attributed_entities": ["A"]
    })

    # Verify LED_TO edge created
    outcome_link = db.query("""
        MATCH (f:Frame {frame_id: $fid})-[l:LED_TO]->(o:Outcome)
        RETURN l.latency_ms, l.confidence
    """, {"fid": frame.frame_id})

    assert outcome_link is not None
    assert outcome_link.latency_ms == 10*60*1000
    assert outcome_link.confidence > 0.3
```

### 9.4 Archival

**Test:** Old frames archive correctly

```python
def test_archival():
    # Create frames at various ages
    create_frame(timestamp_ms=now_ms() - (20 * 24*60*60*1000))  # 20 days (hot)
    create_frame(timestamp_ms=now_ms() - (40 * 24*60*60*1000))  # 40 days (warm)
    create_frame(timestamp_ms=now_ms() - (100 * 24*60*60*1000))  # 100 days (cold)

    # Run archival
    archive_old_frames("test")

    # Verify 20-day frame still active
    hot = db.get_node("Frame", timestamp_ms=now_ms() - (20 * 24*60*60*1000))
    assert hot.archived_at is None
    assert hot has SELECTED edges

    # Verify 40-day frame archived (metadata only)
    warm = db.get_node("Frame", timestamp_ms=now_ms() - (40 * 24*60*60*1000))
    assert warm.archived_at is not None
    assert warm.selections_snapshot is not None
    assert warm has NO SELECTED edges

    # Verify 100-day frame deleted
    cold = db.get_node("Frame", timestamp_ms=now_ms() - (100 * 24*60*60*1000))
    assert cold is None
```

---

## 10. Implementation Checklist

**Infrastructure:**
- [ ] Frame node schema in FalkorDB
- [ ] SELECTED, TRIGGERED_BY, LED_TO edge types
- [ ] Indexes on (citizen_id, timestamp_ms), entity selections
- [ ] Async write queue for frame persistence

**Event Handlers:**
- [ ] wm.emit → persist_wm_frame (real-time)
- [ ] outcome.occurred → link_outcome_to_frame (retroactive)
- [ ] Daily archival job (03:00 cron)

**Query Functions:**
- [ ] compute_co_selection(A, B, window_days)
- [ ] get_context_distribution(entity, window_days)
- [ ] get_outcome_correlation(entity, outcome_type, window_days)
- [ ] get_temporal_activation(entity, start, end, bucket_size)

**Observability:**
- [ ] frame.persisted events
- [ ] frame.outcome.linked events
- [ ] frame.archival.completed events
- [ ] Dashboard: Frame history viewer (optional, for debugging)

**Testing:**
- [ ] Unit tests for frame persistence
- [ ] Unit tests for co-selection queries
- [ ] Unit tests for outcome linking
- [ ] Unit tests for archival logic
- [ ] Load testing (1 frame/sec sustained)

---

## 11. Migration Path

**Phase 1: Infrastructure (Week 1)**
- Add Frame schema to FalkorDB
- Create indexes
- Implement frame persistence handler (wm.emit → Frame)
- Test with single citizen

**Phase 2: Outcome Linking (Week 2)**
- Implement outcome.occurred handler
- Add LED_TO edge creation logic
- Test causal attribution

**Phase 3: Archival (Week 3)**
- Implement daily archival job
- Test retention tiers (hot/warm/cold)
- Verify storage usage

**Phase 4: Query Library (Week 4)**
- Implement co-selection, context, outcome query functions
- Integrate with entity pair analyzer
- Integrate with psychological health monitoring

**Phase 5: Backfill (Optional)**
- Reconstruct historical frames from telemetry logs (if available)
- Populate LED_TO edges from historical outcomes

---

## 12. Success Criteria

**Persistence correctness:**
- ✅ Every wm.emit event creates corresponding Frame node
- ✅ SELECTED edges created for all top-K entities with correct ranks
- ✅ TRIGGERED_BY links to stimulus

**Query performance:**
- ✅ Co-selection query completes <100ms for 30-day window
- ✅ Context distribution query completes <200ms
- ✅ Temporal analysis query completes <500ms

**Retention efficiency:**
- ✅ Hot tier (30 days) ≤ 3GB per citizen
- ✅ Warm tier (60 days) ≤ 1.5GB per citizen
- ✅ Archival reduces storage by ~70% (remove SELECTED edges)

**Integration success:**
- ✅ Entity pair differentiation uses Frame queries successfully
- ✅ Psychological health uses activation history successfully
- ✅ No performance degradation in consciousness engine (async writes)

---

## Status

**Specification:** COMPLETE
**Implementation:** BLOCKED (needs consciousness_engine_v2 to emit wm.emit events)
**Dependencies:** observability_events.md, working_memory.md
**Next steps:**
1. Atlas implements Frame schema + persistence handler
2. Modify consciousness_engine_v2 to emit wm.emit with full metadata
3. Test with single citizen before scaling to all citizens
