# Autonomy Maturity Ladder - Gradual De-Bottlenecking

**Version:** 1.0
**Created:** 2025-10-25
**Purpose:** Safe, gradual path to increase citizen autonomy without losing guardrails
**Owner:** Ada (coordination) + Nicolas (approval gates)

---

## Overview

**Goal:** Incrementally remove human bottlenecks while maintaining safety through explicit acceptance tests at each stage.

**Principle:** Turn one knob at a time, verify with acceptance tests, then move to next stage.

**Current Bottlenecks:**
- Manual triage & routing when errors/drift occur
- Ad-hoc approvals for risky actions
- Fire-fighting during signal storms
- Manual calculation of "why a tick happened"

**Solution:** Graduated autonomy with declarative policies

---

## Maturity Stages

```
L0 (Manual)
  ↓ [Enable answer-only autonomy]
L1 (Answer-Only)
  ↓ [Enable signals → stimuli bridge]
L2 (Signals-Driven)
  ↓ [Enable self-observation with guards]
L3 (Self-Aware)
  ↓ [Enable outcome-aware optimization]
L4 (Outcome-Optimized)
```

Each stage has:
1. **What you turn on** (specific features)
2. **Acceptance tests** (verify safety)
3. **Outcome** (what bottleneck gets removed)
4. **Rollback plan** (if tests fail)

---

## L0 → L1: Answer-Only Autonomy (Phase-A Minimal)

### What You Turn On

**Intent Templates:**
- `intent.fix_incident` (console/log errors → citizen fixes)
- `intent.sync_docs_scripts` (code/doc drift → counterpart updates)

**ACK Policy:**
- **Auto-execute:**
  - Doc/code sync for small files (<50 KB)
  - Sev2/sev3 incidents in non-critical services
  - First-occurrence errors (duplicate_count == 0)
- **Require ACK:**
  - Sev1 incidents (severity >= 0.8)
  - Sentinel-critical services (FalkorDB, mpsv3_supervisor)
  - Deep self-observation (depth >= 2)
  - Recurring failures (duplicate_count >= 5)
  - Large files or architecture docs

**Capacity:**
- Max 3 concurrent missions per citizen
- Max 10 queue depth per citizen

**No Self-Observation Yet:** origin_chain_depth forced to 0 (no runtime event reinjection)

### Acceptance Tests

**Test 1: Incident E2E (Console Error)**
```
Trigger: Inject synthetic console error (TypeError) in dashboard
Expected:
  - Signals Collector receives error.console signal
  - Orchestrator creates intent.fix_incident
  - Routes to Iris (service="dashboard")
  - Iris auto-wakes with mission brief
  - Iris diagnoses, fixes, verifies (tests pass, error disappears)
  - SYNC.md updated with fix
  - Verification PoV >= 0.6
Pass Criteria: ✅ Error fixed within 30 min, no regressions, verified clean
```

**Test 2: Doc-Sync E2E (Code→Doc Drift)**
```
Trigger: Modify orchestration/mechanisms/consciousness_engine_v2.py
         (SCRIPT_MAP.md maps to docs/specs/v2/runtime_engine/engine_spec.md)
         Wait 25 hours (drift > 24h threshold)
Expected:
  - git_watcher detects code_change
  - Orchestrator creates intent.sync_docs_scripts
  - Routes to Ada (code→doc counterpart)
  - Ada auto-wakes, reads diff, updates doc
  - Commits counterpart update
  - Verification query confirms doc.mtime > sync_timestamp
Pass Criteria: ✅ Doc updated within 45 min, accurately reflects code changes
```

**Test 3: ACK Enforcement**
```
Trigger: Inject sev1 error (severity=0.9) in websocket_server
Expected:
  - Orchestrator creates intent.fix_incident
  - Execution mode = ACK_REQUIRED (sev1 policy)
  - Telegram notification sent
  - Dashboard shows "Tap to Approve"
  - Mission does NOT auto-execute
Pass Criteria: ✅ ACK policy triggered, no auto-exec, notification delivered
```

### Outcome

- **De-bottlenecked:** Routine doc/code sync and low-risk incidents handled autonomously
- **Still manual:** Sev1 incidents, critical services, architecture changes
- **Autonomy Ratio Target:** 40-50% (excluding ACK-gated missions)

### Rollback Plan

If acceptance tests fail:
1. Disable orchestrator (stop routing stimuli to missions)
2. Keep signals collector running (log signals for analysis)
3. Fix root cause (template logic, ACK policies, citizen implementation)
4. Re-run acceptance tests before re-enabling

---

## L1 → L2: Signals → Stimuli Bridge

### What You Turn On

**Signals Collector (@8003):**
- Console errors (frontend beacon)
- Log errors (backend tail watcher)
- Git drift (git_watcher via SCRIPT_MAP.md)
- Screenshot capture (optional)

**Resilience Features:**
- Rate limiting (token bucket per source_type)
- Deduplication (5-min window, digest-based)
- Fanout caps (max 3 intents per stimulus)
- Quantile gates (severity > P75, drift > P50)
- PII handling (screenshots → sensitivity: restricted)

**Orchestrator Lanes:**
- Safety lane (sev1, capacity_share=0.5, aging_boost=0.05/min)
- Incidents lane (sev2/sev3, capacity_share=0.3, aging_boost=0.02/min)
- Sync lane (code/doc, capacity_share=0.15, aging_boost=0.01/min)

**Capacity Management:**
- Backpressure when queue > 70% full
- Reassignment after 15 min no-progress timeout
- Overflow → backlog (max 24 hours)

### Acceptance Tests

**Test 4: Noise Resistance (Deduplication)**
```
Trigger: Flood 50 identical console errors within 2 minutes
Expected:
  - First error creates intent.fix_incident
  - Next 49 errors → deduplicated (duplicate_count incremented)
  - Only ONE mission created
  - Duplicate_count = 49 on the single intent
Pass Criteria: ✅ Single mission despite flood, duplicate_count tracked correctly
```

**Test 5: Fanout Cap**
```
Trigger: Single stimulus with multiple matching templates (ambiguous routing)
Expected:
  - Orchestrator matches multiple templates
  - Fanout cap limits to max 3 intents
  - Highest priority templates win
Pass Criteria: ✅ Max 3 intents created despite multiple matches
```

**Test 6: Priority Inversion Protection**
```
Trigger: Inject 20 sev3 errors (incidents lane), then 1 sev1 error (safety lane)
Expected:
  - Safety lane mission jumps to front of queue
  - Sev1 mission assigned before sev3 backlog clears
  - Capacity_share enforced (safety can use up to 50%)
Pass Criteria: ✅ Sev1 handled first despite sev3 backlog
```

**Test 7: Rate Limiting**
```
Trigger: Send 100 error.console signals in 1 minute (exceeds bucket refill rate)
Expected:
  - First 10 signals processed (bucket_size)
  - Remaining 90 backlogged or dropped (depending on config)
  - Rate_limit counter incremented
Pass Criteria: ✅ Rate limiting engaged, backlog managed
```

### Outcome

- **De-bottlenecked:** Ops signals (errors, logs, drift) automatically become missions
- **No manual triage:** Routing happens via templates + ownership
- **Storm-resistant:** Deduplication + rate limits + lanes prevent overload
- **Autonomy Ratio Target:** 60-70%

### Rollback Plan

If tests fail:
1. Disable signals → stimuli routing (collector runs but doesn't forward)
2. Analyze backlog and duplicate_count data
3. Tune rate limits, fanout caps, or quantile gates
4. Re-run tests

---

## L2 → L3: Self-Observation (Guarded)

### What You Turn On

**WS Reinjector:**
- Runtime events (from engines @8000 → collector @8003)
- Event types: `runtime.learning_drift`, `runtime.wm_starvation`, `runtime.safety_regression`

**Self-Observation Guards:**
- **MAX_ORIGIN_CHAIN_DEPTH = 2**
  - Depth 0: External signal (console, log, git)
  - Depth 1: First self-observation (runtime event reinjected)
  - Depth 2: Second-order (mission outcome → runtime event → reinjected)
  - Depth 3+: **BLOCKED** (prevents runaway loops)
- **TTL = 24 hours** (stimulus chains expire after 1 day)
- **Rate limit = 5 per event family per hour**
- **ACK_REQUIRED** when origin_chain_depth >= 2

**Runtime Event Sources:**
- Learning drift: `weights.updated` event shows 0 weight changes over 10 frames
- WM starvation: `wm.emit` shows <3 active subentities for 5+ consecutive frames
- Safety regression: `health.phenomenological` shows degraded metrics

### Acceptance Tests

**Test 8: Depth-Limited Cascade**
```
Trigger: Inject runtime.learning_drift event (depth 0)
Expected:
  - Orchestrator creates mission (depth 1)
  - Citizen executes, emits outcome event
  - Outcome event reinjected as stimulus (depth 2)
  - Orchestrator creates mission BUT requires ACK (depth >= 2 policy)
  - No depth 3 mission created (blocked by MAX_DEPTH=2)
Pass Criteria: ✅ First mission auto-exec, second requires ACK, third impossible
```

**Test 9: TTL Enforcement**
```
Trigger: Create stimulus with ttl_hours=1, wait 2 hours, try to reinject
Expected:
  - Stimulus expires after 1 hour
  - Reinjection attempt rejected (expired)
  - No mission created
Pass Criteria: ✅ Expired stimuli do not create missions
```

**Test 10: Rate Limiting (Event Family)**
```
Trigger: Emit 10 runtime.wm_starvation events in 30 minutes
Expected:
  - First 5 events create missions (rate limit = 5/hour)
  - Remaining 5 backlogged or dropped
  - Rate_limit counter shows overflow
Pass Criteria: ✅ Rate limit enforced per event family
```

### Outcome

- **De-bottlenecked:** System self-corrects when learning stalls or WM degrades
- **No runaway loops:** Depth, TTL, and rate limits prevent cascades
- **Human oversight on deep chains:** Depth >= 2 always requires ACK
- **Autonomy Ratio Target:** 70-80% (depth 1 auto-exec, depth 2 ACK)

### Rollback Plan

If tests fail (cascade detected):
1. Disable WS reinjector immediately
2. Analyze origin_chain_depth distribution
3. Lower MAX_DEPTH to 1 (only direct self-observation)
4. Re-tune rate limits or TTL
5. Re-enable with tighter guards

---

## L3 → L4: Outcome-Aware Autonomy

### What You Turn On

**Source Trust Tracking:**
- Initial trust = 0.5 (neutral)
- Trust delta based on verification_pov:
  - success (pov >= 0.8) → +0.05
  - partial (pov >= 0.6) → +0.02
  - failure (pov < 0.4) → -0.1
  - hallucination → -0.3
- Trust decay = -1%/day without activity
- Low-trust sources (trust < 0.3) deprioritized

**Impact Scoring:**
- Track outcome_quality_ema (EMA of verification_pov over last 20 missions)
- Downweight sources with impact_score < 0.5 (multiply priority by 0.5)
- Gaming-resistant: requires sustained quality, not one-off wins

**Reassignment:**
- Timeout = 15 minutes without progress
- Strategy = round_robin or least_loaded
- Backpressure triggers reassignment when queue > 70% full

**Capacity-Aware Routing:**
- Prefer citizens with lower queue_depth
- Balance specialization affinity vs availability
- Overflow handling with backlog eviction

### Acceptance Tests

**Test 11: Metric Gaming Protection**
```
Trigger: Create source that emits high-severity but low-impact signals (gaming attempt)
Expected:
  - First 20 missions from source get processed
  - Impact_score EMA calculated (low outcome quality)
  - Source gets downweighted (impact_score < 0.5)
  - Subsequent signals from source deprioritized
Pass Criteria: ✅ Gaming source detected and downweighted within 20 missions
```

**Test 12: Reassignment on Stall**
```
Trigger: Assign mission to Iris, Iris goes offline (simulate failure)
Expected:
  - Mission sits in Iris's queue
  - After 15 min timeout, reassignment triggered
  - Mission reassigned to Atlas (fallback)
  - Atlas completes mission
Pass Criteria: ✅ Stalled mission reassigned and completed
```

**Test 13: Capacity-Aware Routing**
```
Trigger: Overload Felix (queue at 90%), assign new mission with Felix affinity
Expected:
  - Orchestrator detects Felix overloaded
  - Routes to Atlas instead (next best affinity, capacity available)
  - Felix not assigned new work until queue drains
Pass Criteria: ✅ Work distributed to available citizens despite affinity preferences
```

### Outcome

- **De-bottlenecked:** System optimizes for impact, not just volume
- **Gaming-resistant:** Trust + impact scoring prevent metric manipulation
- **Self-balancing:** Reassignment + capacity routing prevent hotspots
- **Autonomy Ratio Target:** 80-90% (mature system with tight feedback loops)

### Rollback Plan

If tests fail (unbalanced load, gaming detected):
1. Disable trust scoring (set all sources to trust=0.5)
2. Disable reassignment (manual triage)
3. Analyze impact_score distribution
4. Re-tune EMA lambda, impact_threshold, or reassignment_timeout
5. Re-enable with adjusted parameters

---

## Four Metrics That Matter

Track these to verify de-bottlenecking is working:

### 1. Autonomy Ratio

**Definition:** `missions_auto_executed / missions_created` (excluding ACK-gated)

**Targets:**
- L1 (Answer-Only): 40-50%
- L2 (Signals-Driven): 60-70%
- L3 (Self-Aware): 70-80%
- L4 (Outcome-Optimized): 80-90%

**Query:**
```cypher
MATCH (m:Mission)
WHERE m.created_at > timestamp() - 24*60*60*1000  // Last 24h
WITH count(m) as total,
     count(CASE WHEN m.execution_mode = 'AUTO_EXECUTE' THEN 1 END) as auto
RETURN auto * 1.0 / total as autonomy_ratio
```

**Breakdown:** Track by lane (safety, incidents, sync) to identify bottlenecks

### 2. Stimulus-to-Mission Latency (p95)

**Definition:** Time from signal ingestion → IntentCard creation

**Targets:**
- p50: <1 second
- p95: <5 seconds
- p99: <10 seconds

**Prometheus Metric:**
```
autonomy_stimulus_to_mission_latency_seconds{lane="incidents", quantile="0.95"}
```

**Failure Modes:**
- High p95 → Orchestrator overloaded, need capacity increase
- High p99 → Collector backlog, need rate limit tuning

### 3. Citizen Capacity Utilization

**Definition:** `queue_depth / max_queue_depth` per citizen

**Targets:**
- <70%: Healthy (backpressure inactive)
- 70-85%: Warning (approaching saturation)
- >85%: Critical (reassignment + backpressure active)

**Prometheus Metric:**
```
autonomy_citizen_capacity_utilization{citizen="felix"}
autonomy_queue_depth{citizen="felix", lane="incidents"}
```

**Action:**
- If consistently >70%: Increase max_concurrent or max_queue_depth
- If spike >85%: Check for stalled missions (reassignment working?)

### 4. Autonomy Semantics (Tick Reason Ratio)

**Definition:** Share of ticks with `tick_reason="autonomous_activation"` vs `"stimulus_detected"`

**Target:** 30-50% autonomous ticks (rest are stimulus-driven)

**Query:**
```cypher
MATCH (t:TickFrame)
WHERE t.timestamp_ms > timestamp() - 24*60*60*1000  // Last 24h
WITH count(t) as total,
     count(CASE WHEN t.tick_reason = 'autonomous_activation' THEN 1 END) as autonomous
RETURN autonomous * 1.0 / total as autonomous_ratio
```

**Interpretation:**
- Too low (<20%): Citizens too reactive, need more self-directed exploration
- Too high (>60%): Citizens ignoring stimuli, need better routing

---

## Risk & Guardrails

**Why you can safely increase autonomy:**

### Runaway Loop Prevention (Structural)
- Origin tagging tracks signal source
- MAX_DEPTH=2 prevents deep self-observation cascades
- TTL expires stimulus chains after 24 hours
- Rate limits per event family (5/hour)
- ACK gating on depth >= 2

**Proof:** Test 8 (Depth-Limited Cascade) verifies no depth 3 missions possible

### Incident Hygiene (Operational)
- Fanout caps limit missions per stimulus (max 3)
- Quantile gates filter noise (only P75+ severity)
- Priority lanes prevent sev1 starvation
- Capacity management refuses overload

**Proof:** Test 6 (Priority Inversion) verifies sev1 handled first despite backlog

### PII Protection (Compliance)
- Screenshots default to `sensitivity: restricted`
- Never route to N3 (ecosystem graph)
- Redaction circuit breaker quarantines sources on failure

**Proof:** PII metadata enforced in StimulusEnvelope schema

---

## Implementation Priority (Next Steps)

Based on Nicolas's guidance, ship in this order:

### 1. Ship the Orchestrator Configs (Today)
- Land `intent_templates.yaml` (fix_incident, sync_docs_scripts)
- Land `orchestrator_config.yaml` (lanes, capacity, ACK policies)
- **Outcome:** Safe autonomy policies defined

### 2. Stand Up Collector + Two Watchers (This Week)
- Implement console beacon (frontend errors)
- Implement log tail watcher (backend errors)
- **Acceptance:** Test 4 (deduplication), Test 7 (rate limiting)

### 3. Prove Four Motion Events Flow (This Week)
- Verify `tick_frame_v1`, `wm.emit`, `node.flip`, `link.flow.summary` at 10 Hz
- Check counters endpoint: `/api/telemetry/counters`
- **Acceptance:** Counters rising, no "Awaiting data" in dashboard

### 4. Turn On Self-Observation with Guards (Next Week)
- Implement WS reinjector (runtime events → stimuli)
- MAX_DEPTH=2, ACK_REQUIRED at limit, rate limits
- **Acceptance:** Test 8 (cascade prevention), Test 9 (TTL), Test 10 (rate limit)

### 5. Introduce Reassignment and Trust Scoring (Week 3)
- Capacity caps, reassignment timeout, trust decay/recovery
- **Acceptance:** Test 11 (gaming), Test 12 (reassignment), Test 13 (capacity routing)

---

## Small Autonomy Dashboard (Track From Day One)

**Metrics to Display:**

1. **Autonomy % (last 24h)** - Broken down by lane (safety, incidents, sync, self-awareness)
2. **ACK Rate & Median Time-to-ACK** - Only sev1/sev2 or depth>=2 should need approval
3. **Assignments by Citizen** - In-flight vs capacity (bar chart)
4. **Event Health** - Counters for tick_frame_v1, wm.emit, node.flip, link.flow.summary (total + last 60s)
5. **Stimulus Throughput** - Injected vs deduplicated vs rate-limited (from collector /health)

**Dashboard Location:** `app/consciousness/autonomy-dashboard.tsx`

**Data Source:** Prometheus metrics + FalkorDB queries

---

## Rollback Decision Tree

```
Problem: Autonomy ratio unexpectedly drops below target
  ├─ Check: ACK policies too aggressive?
  │   └─ Action: Relax ACK conditions, re-test
  ├─ Check: Capacity limits too low?
  │   └─ Action: Increase max_concurrent, re-test
  └─ Check: Quantile gates filtering too much?
      └─ Action: Lower quantile thresholds, re-test

Problem: Cascade detected (depth 3+ missions appearing)
  ├─ Action: Disable WS reinjector immediately
  ├─ Check: MAX_DEPTH enforced correctly?
  │   └─ Fix: Update orchestrator depth check logic
  └─ Re-enable: After verification test passes

Problem: Sev1 incidents delayed (safety lane aging >10 min)
  ├─ Check: Lane capacity_share sufficient?
  │   └─ Action: Increase safety lane capacity_share
  ├─ Check: Fanout cap creating backlog?
  │   └─ Action: Raise max_intents_per_stimulus for safety lane
  └─ Check: Citizen capacity saturated?
      └─ Action: Increase citizen max_concurrent

Problem: Gaming detected (low-impact source flooding)
  ├─ Action: Lower source trust score manually
  ├─ Check: Impact scoring EMA tuning?
  │   └─ Action: Adjust lambda or impact_threshold
  └─ Future: Implement quarantine for repeated gaming
```

---

**End of Maturity Ladder**

*Luca Vellumhand - Substrate Architect*
*Based on autonomy guidance by Nicolas Lester Reynolds (2025-10-25)*
