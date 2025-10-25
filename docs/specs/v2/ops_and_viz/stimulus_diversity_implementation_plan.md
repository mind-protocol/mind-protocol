---
title: Stimulus Diversity Implementation Plan
status: draft
owner: @ada (coordination), @felix @atlas @iris @victor (implementation)
last_updated: 2025-10-25
depends_on:
  - ../subentity_layer/stimulus_diversity.md
  - ../subentity_layer/stimulus_injection.md
summary: >
  Implementation plan for stimulus diversity (L1/L2). Clearly separates substrate
  specification (complete), orchestration design (Ada), and implementation work
  (Felix/Atlas/Iris/Victor). Based on Nicolas's Phase A-D plan.
---

# Stimulus Diversity Implementation Plan

## 0. Ownership & Boundaries

### Substrate Specification (COMPLETE)
**Owner:** Luca
**Deliverable:** `stimulus_diversity.md` ✅
**Status:** Complete — all L1/L2 schemas, attribution model, routing model, evidence linking defined

### Orchestration Design (THIS DOCUMENT)
**Owner:** Ada
**Scope:** Service architecture, watcher design, deriver logic, phase sequencing, rollout coordination

### Implementation
**Owners:** Felix (consciousness integration), Atlas (services/API), Iris (UI), Victor (ops)
**Scope:** Build watchers, deriver, UI panels, ops tooling per Ada's orchestration design

---

## 1. Current State (from Nicolas's snapshot)

### ✅ Working (L1 → injection)
- **Conversations** → injected and processed
- **Console errors** → collected by signals_collector, forwarded to injection (rate-limited, deduped)
- **Screenshots** → accepted by `/api/signals/screenshot`, stored (no OCR yet)

### ⚠️ Partial
- **Self-observation events** → flowing as telemetry (health, weights, tier, mismatch)
  - NOT yet converted to L1 stimuli and re-injected
- **Persistence** → being added (dirty set + bulk persist)

### ❌ Not Yet (L1 collectors)
- **Git commits** (local/remote) → no collector
- **File changes** → hot-reload works, but no "file change → stimulus" path
- **Backend errors** from logs → not collected

### ❌ Not Yet (L2 derivation)
- **L2 deriver service** → not implemented
- **Derived intents** → not created
- **Attribution logic** → not implemented
- **Routing specialization** → not implemented

---

## 2. Implementation Phases (Nicolas's A-D structure)

### Phase A — L1 Coverage (Fast Wins)

**Goal:** Fill L1 collector gaps (git, fs, backend logs)

#### A1: Git Commit Watcher
**Owner:** Atlas
**Service:** `services/git_watcher.py` (guardian-managed)

**Implementation:**
1. Poll `git rev-parse HEAD` every 3-5s
2. On change, collect: sha, author, message, files changed, diffstat
3. Extract tags from message: `fix:`, `feat:`, `schema`, `guardian`, `emitter`, `test`
4. Emit L1 stimulus type `commit` per substrate spec (§3.2)
5. POST to signals_collector

**Acceptance:**
- Create a commit → L1 `commit` stimulus appears in logs
- Tags correctly extracted from commit message
- Rate limiting prevents flood on bulk commits
- Guardian auto-restarts on crash

#### A2: File System Watcher
**Owner:** Atlas
**Service:** `services/fs_watcher.py`

**Implementation:**
1. Watch globs: `orchestration/**/*.py`, `app/**`, `tests/**`
2. Debounce & decimate (group rapid changes, ignore node_modules/.next)
3. Bucket: `{create, modify, delete}`, extract package from path
4. Emit L1 stimulus type `file_change` per substrate spec
5. POST to signals_collector

**Acceptance:**
- Modify a Python file → L1 `file_change` stimulus appears
- No flood from hot-reload cascades (debounce working)
- Package correctly extracted (e.g., "orchestration", "app/consciousness")

#### A3: Backend Log Error Watcher
**Owner:** Victor
**Service:** `services/log_watcher.py`

**Implementation:**
1. Tail `logs/*.log` for `ERROR|Traceback|RuntimeError`
2. Extract: service, exception type, message, stack trace
3. Compute `stack_fingerprint` for deduplication
4. Group identical stacks within time window, count occurrences
5. Emit L1 stimulus type `backend_error` per substrate spec
6. POST to signals_collector

**Acceptance:**
- Force a backend error → L1 `backend_error` stimulus appears
- Identical errors grouped (not N individual stimuli)
- Stack fingerprint stable across identical exceptions

#### A4: Self-Observation → L1 Conversion
**Owner:** Felix
**Integration:** Existing event emitters + new L1 wrapper

**Implementation:**
1. Wrap existing telemetry events in L1 `self_observation` stimulus:
   - `health.phenomenological` → L1 with observation_type="health"
   - `weights.updated.trace` → L1 with observation_type="learning"
   - `tier.link.strengthened` → L1 with observation_type="tier"
   - `phenomenology.mismatch` → L1 with observation_type="mismatch"
2. POST to signals_collector (same path as external signals)
3. Add flag `SELF_OBS_AS_STIMULI=true` to enable

**Acceptance:**
- Health event emitted → L1 `self_observation` stimulus created
- Event payload preserved in L1 metadata
- Can toggle self-observation → stimulus conversion via config

**Phase A Completion Criteria:**
- ✅ All 4 watcher services running under guardian
- ✅ Create commit, modify file, trigger error, emit health event → 4 L1 stimuli appear
- ✅ Rate limiting prevents floods
- ✅ Services auto-restart on crash

---

### Phase B — L2 Derivation (Meaningful Layer)

**Goal:** Aggregate L1 patterns → L2 intents/incidents

#### B1: Stimulus Deriver Service
**Owner:** Atlas
**Service:** `services/stimulus_deriver_v2.py` (guardian-managed)

**Architecture:**
```
L1 stream (from signals_collector or JSONL)
  ↓
Deriver (sliding windows, pattern matching)
  ↓
L2 stimuli (intents/incidents with attribution + routing)
  ↓
POST to stimulus injection (existing /inject endpoint)
```

**Implementation:**
1. Subscribe to L1 stream (Redis queue or JSONL tail)
2. Maintain sliding windows (1min, 5min, 15min)
3. Apply derivation rules (see B2)
4. Compute attribution (see B3)
5. Compute routing (see B4)
6. Emit L2 stimuli per substrate spec (§4)
7. POST to injection service

**Data structures:**
```python
@dataclass
class SlidingWindow:
    duration_minutes: int
    l1_events: deque[L1Stimulus]  # Max size by duration

    def add(self, event: L1Stimulus):
        """Add event, evict old beyond window."""

    def query(self, filter_fn: Callable) -> List[L1Stimulus]:
        """Query events matching filter."""
```

**Acceptance:**
- Deriver consumes L1 events from queue
- Sliding windows maintain correct duration
- Old events evicted properly
- Derivation rules trigger correctly (see B2 acceptance)

#### B2: Derivation Rules (MVP Set)
**Owner:** Atlas (implementation), Nicolas (threshold tuning)

**Rule 1: intent.stabilize_narrative**
```python
def derive_stabilize_narrative(
    windows: Dict[str, SlidingWindow]
) -> Optional[L2Stimulus]:
    """
    Trigger: health.phenomenological.state == "fragmented"
             for ≥5 consecutive observations
    """
    health_events = windows['5min'].query(
        lambda e: e.type == 'self_observation'
        and e.metadata['observation_type'] == 'health'
    )

    # Check for sustained fragmentation
    fragmented_count = sum(
        1 for e in health_events[-5:]
        if e.metadata['event_payload']['state'] == 'fragmented'
    )

    if fragmented_count >= 5:
        return L2Stimulus(
            type='intent.stabilize_narrative',
            explanation=f"Fragmented state observed {fragmented_count}x in 25 ticks",
            evidence=[e.stimulus_id for e in health_events[-5:]],
            confidence=0.85,
            attribution=compute_attribution(['sentinel', 'planner'], 0.85),
            routing=Routing(mode='amplify', budget_hint=3.0)
        )

    return None
```

**Rule 2: intent.reconcile_beliefs**
```python
def derive_reconcile_beliefs(
    windows: Dict[str, SlidingWindow]
) -> Optional[L2Stimulus]:
    """
    Trigger: mismatch + schema commit + file changes in schema area
    """
    mismatch_events = windows['5min'].query(
        lambda e: e.type == 'self_observation'
        and e.metadata['observation_type'] == 'mismatch'
    )

    schema_commits = windows['15min'].query(
        lambda e: e.type == 'commit'
        and 'schema' in e.metadata['tags']
    )

    schema_file_changes = windows['15min'].query(
        lambda e: e.type == 'file_change'
        and 'schema' in e.metadata['path'].lower()
    )

    if mismatch_events and schema_commits and schema_file_changes:
        return L2Stimulus(
            type='intent.reconcile_beliefs',
            explanation="Mismatch detected after schema changes",
            evidence=[
                *[e.stimulus_id for e in mismatch_events],
                *[e.stimulus_id for e in schema_commits],
                *[e.stimulus_id for e in schema_file_changes]
            ],
            confidence=0.8,
            attribution=compute_attribution(['architect', 'validator'], 0.8),
            routing=Routing(mode='top_up', budget_hint=2.5),
            metadata={'schema_area': extract_schema_area(schema_file_changes)}
        )

    return None
```

**Rule 3: incident.backend_error**
```python
def derive_backend_error_incident(
    windows: Dict[str, SlidingWindow],
    threshold: int = 5,
    window_minutes: int = 5
) -> Optional[L2Stimulus]:
    """
    Trigger: ≥X identical errors in Y minutes
    """
    error_events = windows[f'{window_minutes}min'].query(
        lambda e: e.type == 'backend_error'
    )

    # Group by stack_fingerprint
    by_fingerprint = defaultdict(list)
    for e in error_events:
        fp = e.metadata['stack_fingerprint']
        by_fingerprint[fp].append(e)

    # Find storms
    for fingerprint, events in by_fingerprint.items():
        if len(events) >= threshold:
            return L2Stimulus(
                type='incident.backend_error',
                explanation=f"Error storm: {len(events)} identical errors in {window_minutes}min",
                evidence=[e.stimulus_id for e in events],
                confidence=0.95,
                attribution=compute_attribution(['ops', 'investigator'], 0.95),
                routing=Routing(
                    mode='top_up',
                    budget_hint=4.0,
                    alert=True,
                    alert_severity='critical'
                ),
                metadata={
                    'error_fingerprint': fingerprint,
                    'error_count': len(events),
                    'time_window_minutes': window_minutes
                }
            )

    return None
```

**Additional rules (implement in priority order):**
4. `intent.consolidate_learning` (learning spike)
5. `intent.promote_pattern` (link strengthening surge)
6. `intent.protect_fix` (commit + error reduction)

**Acceptance (per rule):**
- Force trigger condition → L2 stimulus created
- Attribution correct (right entities)
- Routing mode correct (top_up vs amplify)
- Evidence links to triggering L1 events
- Confidence in expected range

#### B3: Attribution Computation
**Owner:** Felix (WM integration), Atlas (implementation)

**Implementation:**
```python
def compute_attribution(
    primary_entities: List[str],
    confidence: float,
    method: str = "rule_based"
) -> Attribution:
    """
    Compute attribution with WM context.

    For MVP: use rule-based (explicit entity list).
    Phase 2: enhance with WM snapshot + entity affinity.
    """

    # MVP: explicit entities from derivation rule
    attribution = Attribution(
        primary_entities=primary_entities,
        primary_confidence=confidence,
        attribution_method=method
    )

    # Optional: enrich with WM context
    wm_snapshot = get_current_wm_snapshot()  # From Felix
    if wm_snapshot:
        attribution.wm_snapshot_id = wm_snapshot.id
        attribution.active_entities_at_time = wm_snapshot.top_entities

        # Add secondary entities from WM if not in primary
        secondary = [
            e for e in wm_snapshot.top_entities
            if e not in primary_entities
        ][:3]  # Top 3
        attribution.secondary_entities = secondary
        attribution.secondary_confidence = confidence * 0.7

    return attribution
```

**Acceptance:**
- Attribution includes primary entities from rule
- If WM available, includes WM snapshot context
- Secondary entities populated from WM top-K
- Confidence propagates correctly

#### B4: Routing Computation
**Owner:** Atlas (implementation), validates against stimulus_injection.md v2.1

**Implementation:**
```python
def compute_routing(
    mode: str,
    budget_hint: float,
    target_entities: List[str],
    alert: bool = False
) -> Routing:
    """
    Create routing per substrate spec (§6).
    Integrates with injection v2.1 dual-channel policy.
    """

    routing = Routing(
        mode=mode,
        budget_hint=budget_hint,
        target_entities=target_entities
    )

    # Lambda override based on mode
    if mode == "top_up":
        routing.lambda_override = 0.75  # Favor floor channel
    elif mode == "amplify":
        routing.lambda_override = 0.35  # Favor amplifier channel
    # else: use adaptive lambda from injector

    # Alert configuration
    if alert:
        routing.alert = True
        routing.alert_severity = determine_severity(budget_hint)

    return routing
```

**Acceptance:**
- Mode correctly influences lambda override
- Budget hint in valid range [0.5, 5.0]
- Alert configuration propagates to injection
- Integrates cleanly with injection v2.1 (no conflicts)

**Phase B Completion Criteria:**
- ✅ Deriver service running, consuming L1 stream
- ✅ All 3 MVP rules implemented and tested
- ✅ Force fragmentation → `intent.stabilize_narrative` created
- ✅ Force error storm → `incident.backend_error` created
- ✅ Force mismatch+schema-commit → `intent.reconcile_beliefs` created
- ✅ Attribution includes entity targeting
- ✅ Routing integrates with injection v2.1
- ✅ L2 stimuli visible in injection logs

---

### Phase C — Attribution & Routing Integration

**Goal:** Connect attribution to entity membership, specialize injection targeting

#### C1: Entity Member Retrieval
**Owner:** Felix
**Integration:** Injection candidate selection

**Implementation:**
```python
def retrieve_entity_members(
    entities: List[str],
    similarity_threshold: float = 0.6,
    limit: int = 50
) -> List[Candidate]:
    """
    Retrieve nodes that are members of target entities.
    Used when stimulus has high-confidence attribution.
    """

    # Query for entity members
    query = """
    MATCH (n:Node)-[:MEMBER_OF]->(e:Subentity)
    WHERE e.name IN $entities
    RETURN n, e.name as entity
    LIMIT $limit
    """

    results = db.query(query, entities=entities, limit=limit)

    # Convert to candidates
    candidates = []
    for record in results:
        node = record['n']
        candidate = Candidate(
            node_id=node.id,
            E=node.energy,
            theta=node.threshold or compute_threshold(node),
            type=node.node_type,
            entity=record['entity']
        )
        candidates.append(candidate)

    return candidates
```

**Acceptance:**
- Query returns members of specified entities
- Empty result triggers fallback to semantic search
- Member candidates include entity context
- Performance acceptable (< 100ms for 50 members)

#### C2: Attribution-Biased Injection
**Owner:** Felix
**Integration:** stimulus_injection.py

**Implementation:**
```python
def select_candidates_with_attribution(
    stimulus: StimulusEnvelope,
    attribution: Optional[Attribution]
) -> List[Candidate]:
    """
    Bias candidate selection toward attributed entities.
    Fallback to semantic search if attribution weak/absent.
    """

    # High-confidence attribution: use entity members
    if attribution and attribution.primary_confidence > 0.7:
        candidates = retrieve_entity_members(
            entities=attribution.primary_entities,
            similarity_threshold=0.6
        )

        # Fallback if insufficient members
        if len(candidates) < 10:
            semantic_candidates = retrieve_by_embedding(
                stimulus.content,
                exclude_ids=[c.node_id for c in candidates]
            )
            candidates.extend(semantic_candidates[:20])

    else:
        # Low/no attribution: standard semantic search
        candidates = retrieve_by_embedding(stimulus.content)

    return candidates
```

**Acceptance:**
- High-confidence attribution → entity members retrieved first
- Low-confidence attribution → semantic search used
- Hybrid approach when entity members insufficient
- Candidates correctly tagged with entity membership

#### C3: Routing Mode → Lambda Adjustment
**Owner:** Felix
**Integration:** stimulus_injection.py inject() function

**Implementation:**
```python
def compute_lambda_with_routing(
    routing: Optional[Routing],
    coldness: float,
    concentration: float
) -> float:
    """
    Compute adaptive λ with routing mode override.
    Integrates with stimulus_injection.md v2.1 §2.1.1
    """

    # Start with adaptive baseline
    lam = adaptive_lambda(coldness, concentration)

    # Apply routing override if present
    if routing and routing.lambda_override:
        lam = routing.lambda_override

    # Mode-based adjustment if no explicit override
    elif routing and routing.mode:
        if routing.mode == "top_up":
            lam = max(lam, 0.7)  # Favor floor channel
        elif routing.mode == "amplify":
            lam = min(lam, 0.4)  # Favor amplifier channel

    return clamp(lam, 0.3, 0.8)
```

**Acceptance:**
- Routing mode correctly influences lambda
- Explicit override takes precedence
- Mode-based adjustment applied if no override
- Result stays within [0.3, 0.8] bounds

**Phase C Completion Criteria:**
- ✅ Attribution-biased retrieval working
- ✅ Entity members retrieved for high-confidence attribution
- ✅ Routing mode influences lambda correctly
- ✅ Telemetry shows attribution → targeting → injection path
- ✅ Schema commit stimulus targets architect/validator nodes preferentially

---

### Phase D — UI & Observability

**Goal:** Make stimulus diversity visible and debuggable

#### D1: Stimuli Feed Panel
**Owner:** Iris
**Component:** `app/consciousness/components/StimuliFeed.tsx`

**Features:**
- **Tabs:** All | L1 | L2 | Self-Obs (filter by citizen)
- **Columns:** Time, Type, Explanation, Attribution, Evidence
- **Actions:** Click to expand evidence, click entity to filter, click correlation_id to group

**Implementation:**
```typescript
interface StimulusFeedProps {
  citizen_id: string
}

interface StimulusDisplay {
  stimulus_id: string
  level: "L1" | "L2"
  type: string
  timestamp_ms: number
  content: string
  explanation?: string  // L2 only
  attribution?: Attribution
  evidence?: string[]
  correlation_id: string
}

function StimuliFeed({ citizen_id }: StimulusFeedProps) {
  const [filter, setFilter] = useState<"all" | "L1" | "L2" | "self-obs">("all")
  const stimuli = useStimuli(citizen_id, filter)

  return (
    <Panel title="Stimuli Feed">
      <Tabs value={filter} onChange={setFilter}>
        <Tab value="all">All</Tab>
        <Tab value="L1">L1 Raw</Tab>
        <Tab value="L2">L2 Derived</Tab>
        <Tab value="self-obs">Self-Observation</Tab>
      </Tabs>

      <Table>
        {stimuli.map(s => (
          <StimulusRow
            key={s.stimulus_id}
            stimulus={s}
            onEntityClick={(entity) => setFilter(entity)}
          />
        ))}
      </Table>
    </Panel>
  )
}
```

**Acceptance:**
- Panel shows stimuli in reverse chronological order
- Tabs filter correctly
- Attribution shows entity badges (clickable)
- Evidence expands to show L1 references
- Correlation ID groups related stimuli

#### D2: Timeline Markers
**Owner:** Iris
**Integration:** Existing frame timeline

**Implementation:**
- Add L2 stimulus markers to timeline at `timestamp_ms`
- Color-code by type (intent vs incident)
- Click marker → jump to Stimuli Feed at that time
- Hover marker → show tooltip with type + explanation

**Acceptance:**
- L2 markers appear on timeline
- Click marker → Stimuli Feed opens and scrolls to event
- Tooltip shows type and short explanation

#### D3: Stimulus Metrics
**Owner:** Iris (UI), Atlas (backend API)

**Metrics to display:**
- L1 rate per minute (by type)
- L2 rate per minute (by type)
- Dropped/decimated count (rate limiting)
- Attribution hit rate (% with high-confidence attribution)
- Injection success rate (% resulting in flips)

**API Endpoint:**
```
GET /consciousness/:citizen/metrics/stimuli
→ {
    l1_rate_per_min: {conversation: 2.3, console_error: 0.5, ...},
    l2_rate_per_min: {intent_stabilize: 0.1, incident_error: 0.05},
    dropped_count_last_hour: 12,
    attribution_hit_rate: 0.73,
    injection_success_rate: 0.65
  }
```

**Acceptance:**
- Metrics panel shows real-time rates
- Dropped count visible (validates rate limiting)
- Attribution hit rate trackable
- Injection success rate correlates with L2 quality

**Phase D Completion Criteria:**
- ✅ Stimuli Feed panel functional
- ✅ Can filter by level, type, entity
- ✅ Evidence links clickable and navigable
- ✅ Timeline markers show L2 events
- ✅ Metrics panel shows rates and quality indicators
- ✅ Can replay dev loop: commit → mismatch → fix sequence visible

---

## 3. Roll-Out Sequencing

**Week 1: Phase A (L1 Coverage)**
- Day 1-2: Git watcher + File watcher (Atlas)
- Day 3: Log watcher (Victor)
- Day 4: Self-observation wrapper (Felix)
- Day 5: Integration testing, guardian config (Victor)

**Week 2: Phase B1-B2 (Deriver MVP)**
- Day 1-2: Deriver service skeleton + sliding windows (Atlas)
- Day 3: Rule 1 (stabilize_narrative) + attribution (Atlas + Felix)
- Day 4: Rule 2 (reconcile_beliefs) + routing (Atlas)
- Day 5: Rule 3 (backend_error) + testing (Atlas + Victor)

**Week 3: Phase B3-B4 + C (Attribution/Routing Integration)**
- Day 1-2: Entity member retrieval (Felix)
- Day 3: Attribution-biased injection (Felix)
- Day 4: Routing → lambda integration (Felix)
- Day 5: End-to-end testing (all)

**Week 4: Phase D (UI)**
- Day 1-2: Stimuli Feed panel (Iris)
- Day 3: Timeline markers (Iris)
- Day 4: Metrics API + panel (Atlas + Iris)
- Day 5: Polish, documentation, demo (all)

---

## 4. Acceptance Testing Strategy

### Unit Tests (per component)
- Each watcher service: mock events → L1 stimulus created
- Each derivation rule: mock L1 sequence → L2 stimulus created
- Attribution: mock WM → correct entities selected
- Routing: mode → correct lambda adjustment

### Integration Tests (cross-component)
- L1 watcher → signals_collector → injection: end-to-end
- L1 sequence → deriver → L2 → injection → flips: full path
- Attribution → entity members → targeted injection

### Scenario Tests (realistic workflows)
1. **Dev loop:** Commit (schema) → File change → Error → Fix commit
   - Expected: `intent.reconcile_beliefs` → `intent.protect_fix`

2. **Error storm:** 10 identical errors in 2 minutes
   - Expected: `incident.backend_error` with alert

3. **Fragmentation:** Force 5 consecutive health=fragmented
   - Expected: `intent.stabilize_narrative` → amplified to Sentinel

4. **Learning spike:** Trigger high weights.updated volume
   - Expected: `intent.consolidate_learning`

### Observability Validation
- All scenario tests: verify stimuli appear in Feed panel
- Timeline markers appear for L2 events
- Metrics show correct rates
- Evidence links trace back to source L1 events

---

## 5. Risk Mitigation

### Risk: L1 Flooding
**Mitigation:**
- Rate limiting in each watcher (per substrate spec)
- Decimation/debouncing in fs_watcher
- Grouping/fingerprinting in log_watcher
- Budget caps in injection v2.1

### Risk: L2 False Positives
**Mitigation:**
- Conservative thresholds initially (tune down from high)
- Confidence scoring on all L2 stimuli
- Metrics track L2 → flip success rate
- Manual review of first 100 L2 stimuli per type

### Risk: Attribution Misses
**Mitigation:**
- Fallback to semantic search on low-confidence attribution
- Log attribution confidence in telemetry
- Metrics show attribution hit rate
- Phase 2: learn from successful attributions

### Risk: Performance Degradation
**Mitigation:**
- Deriver runs as separate service (isolated from engines)
- Sliding windows bounded by time and size
- Entity member queries use indexes
- Monitor deriver latency (target: < 500ms per L2 derivation)

---

## 6. Success Metrics

**Diversity (breadth):**
- ≥5 L1 types active (conversation, console, commit, file, backend, self-obs)
- ≥3 L2 types created per day

**Quality (relevance):**
- Attribution confidence >0.7 for ≥70% of L2 stimuli
- L2 → flip success rate >50%

**Responsiveness (latency):**
- L1 event → stimulus in queue: <1s
- L1 sequence → L2 derivation: <5s
- L2 → injection → flips: <10s

**Observability (transparency):**
- 100% of L2 stimuli traceable to L1 evidence
- 100% of L2 stimuli visible in Feed panel
- Timeline markers for all L2 events

---

## 7. Handoff Protocol

### Luca → Ada
**Substrate spec complete:** `stimulus_diversity.md`
- All L1/L2 types defined ✅
- Attribution model specified ✅
- Routing model specified ✅
- Integration with injection v2.1 defined ✅

**Ada's orchestration design:** This document
- Service architecture (watchers, deriver)
- Derivation rules with thresholds
- Phase sequencing and rollout
- Acceptance criteria

### Ada → Implementation Team

**To Atlas:**
- Implement git_watcher, fs_watcher, stimulus_deriver_v2
- Build sliding window infrastructure
- Implement 3 MVP derivation rules
- Provide stimulus metrics API

**To Felix:**
- Wrap self-observation events in L1 stimuli
- Implement entity member retrieval
- Integrate attribution-biased injection
- Integrate routing → lambda adjustment

**To Iris:**
- Build Stimuli Feed panel
- Add timeline markers
- Display stimulus metrics

**To Victor:**
- Implement log_watcher
- Configure guardian for new services
- Set up health checks and auto-restart
- Monitor service performance

---

## 8. Implementation Decisions (Nicolas 2025-10-25)

**All blockers removed.** Concrete decisions on thresholds, OCR, alerts, correlation, persistence.

### 8.1 Threshold Strategy

**Phase 1 (Conservative Seeds):**
- **Fragmentation:** ≥5 fragmented frames in 60s AND mean_fragmentation ≥0.60 → `intent.stabilize_narrative`
- **Error Storm:** ≥10 identical errors in 2min (per stack-fingerprint) → `incident.backend_error`
- **Learning Spike:** ≥100 weights.updated in 5min OR above Q95 of last 24h → `intent.consolidate_learning`
- **Belief Mismatch:** commit touches schemas AND ≥3 related backend errors in 10min → `intent.reconcile_beliefs`

**Phase 2 (Learned Percentiles):**
- Replace seeds with per-citizen Q85-Q95 thresholds (7-day window)
- Daily `threshold_tuner` job computes and updates config
- Keep seeds as safety floors

### 8.2 Other Decisions

- **Screenshot OCR:** Phase 2 (simplifies MVP)
- **Alert Routing:** Dashboard always, Slack/email only for severity=critical with cooldowns + capacity limits
- **Cross-Citizen Correlation:** Phase 2
- **L2 Persistence:** Store ALL L2 + evidence + injection results (TTL 30-60d)

### 8.3 Ready-to-Use Config (Phase 1)

```yaml
# config/deriver_rules.yaml
windows:
  error_storm_minutes: 2
  fragmentation_seconds: 60
  learning_minutes: 5

rules:
  - name: incident.backend_error
    when:
      type: backend_error
      fingerprint: same
      count_ge: 10
      window_min: 2
    routing:
      mode: top_up
      budget_hint: 4.0
      alert: true
      alert_severity: critical

  - name: intent.stabilize_narrative
    when:
      type: health.phenomenological
      fragmented_frames_ge: 5
      mean_fragmentation_ge: 0.60
    routing:
      mode: amplify
      budget_hint: 2.5

  - name: intent.consolidate_learning
    when:
      type: weights.updated
      count_ge: 100
      window_min: 5
      or_above_percentile: 95
    routing:
      mode: hybrid
      budget_hint: 2.0

  - name: intent.reconcile_beliefs
    when:
      any_of:
        - type: git_commit
          touches: ["schema", "types"]
        - type: backend_error
          related_to_commit: true
          count_ge: 3
          window_min: 10
    routing:
      mode: top_up
      budget_hint: 3.0
```

---

## 9. Next Steps (Nicolas's Priority Order)

**Lock Phase-A slice and ship.** Don't expand scope until watchers + deriver MVP + metrics are live.

### Priority 1: Metrics Foundation
**Owner:** Atlas (backend), Iris (UI)
**Why First:** Enables tuning + demos; unlocks parallel work

1. Implement `/consciousness/:citizen/metrics/stimuli` endpoint
2. Add counters in each watcher (L1 rates by type)
3. Add counters in deriver (L2 rates, dropped count, attribution hit rate)
4. Wire metrics panel in dashboard

**Acceptance:** Dashboard shows real-time L1/L2 rates, attribution quality, injection success.

### Priority 2: Watchers + Deriver MVP
**Owners:** Atlas (watchers, deriver), Felix (self-obs), Victor (log watcher, guardian)

1. Implement git_watcher, fs_watcher (Atlas)
2. Implement log_watcher (Victor)
3. Wrap self-observation events in L1 stimuli (Felix)
4. Build deriver service skeleton + sliding windows (Atlas)
5. Implement 3 MVP rules from config (Atlas):
   - incident.backend_error
   - intent.stabilize_narrative
   - intent.reconcile_beliefs
6. Wire attribution + routing per substrate spec (Atlas + Felix)
7. Guardian config for all new services (Victor)

**Acceptance:** Create commit, modify file, trigger error, emit health event → 4 L1 stimuli + derived L2 intents visible in logs.

### Priority 3: Alert Safety
**Owner:** Atlas (bridge), Ada (policy enforcement)

1. Add cooldowns per channel (prevent spam)
2. Add capacity limits per assignee (max_in_flight)
3. Add sensitivity metadata handling (never route restricted to N3)
4. Add circuit breakers for alert storms

**Acceptance:** Force error storm → alert fires → cooldown prevents spam → capacity limit respected.

### Priority 4: Threshold Tuner (Daily Job)
**Owner:** Atlas
**Depends on:** Metrics collecting for ≥7 days

1. Read 7-day histograms per citizen per metric
2. Compute Q85/Q95 thresholds
3. Write to config (YAML or DB)
4. Scheduled daily via cron/guardian

**Acceptance:** After 7 days, tuner computes percentiles → config updated → deriver uses learned thresholds.

**Spec needed:** See Nicolas's offer for threshold_tuner sketch.

### Priority 5: Full Observability
**Owner:** Iris (UI), Atlas (persistence)

1. Persist all L2 + evidence links + injection results
2. Build Stimuli Feed panel (tabs: All/L1/L2/Self-Obs)
3. Add timeline markers for L2 events
4. Add TTL policy (30-60d archival)

**Acceptance:** Can replay dev loop (commit → mismatch → fix) in Feed panel with full evidence trail.

---

### Immediate Next Actions (This Week)

**Day 1-2:**
- Atlas: Implement metrics endpoint + counters
- Iris: Wire metrics panel
- Victor: Set up log_watcher skeleton

**Day 3-4:**
- Atlas: Implement git_watcher, fs_watcher, deriver skeleton
- Felix: Self-obs → L1 wrapper
- Iris: Stimuli Feed mockup

**Day 5:**
- Team: Integration testing (L1 end-to-end)
- Victor: Guardian config for all services

**Week 2:** Deriver MVP (3 rules) + attribution/routing integration

**Week 3:** Alert safety + UI polish

**Week 4:** Threshold tuner + full observability

---

### Dependencies for Parallel Work

- **Metrics API spec** (see Nicolas's offer) → enables Iris to build UI in parallel
- **Threshold tuner spec** (see Nicolas's offer) → enables Atlas to implement in parallel

**Target:** Phase A complete in 1 week, Phase B in 2 weeks, metrics + tuner + UI in 4 weeks.
