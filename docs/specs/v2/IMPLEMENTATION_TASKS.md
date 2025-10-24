# Implementation Tasks Tracker

**Purpose:** Track all implementation tasks derived from mechanism specifications
**Owner:** Coordination (Ada) with input from spec authors (Luca)
**Status:** Living document - update as tasks complete or new specs add requirements

---

## How to Use This Document

**For Spec Authors (Luca):**
- When creating/updating specs, add implementation tasks to relevant sections
- Mark priority (P0 = blocking, P1 = high, P2 = medium, P3 = nice-to-have)
- Specify owner (Felix for consciousness, Atlas for infrastructure, Iris for UI)
- Include verification criteria from spec

**For Implementation Team (Felix/Atlas/Iris):**
- Check this document for your assigned tasks
- Update status as you work (🔴 Not Started → 🟡 In Progress → 🟢 Complete)
- Add notes/blockers in Comments column
- Cross-reference spec file for full context

**For Coordination (Ada):**
- Maintain task prioritization
- Resolve blockers
- Ensure verification criteria are met before marking complete

---

## Task Status Legend

- 🔴 **Not Started** - No work begun
- 🟡 **In Progress** - Actively being implemented
- 🟢 **Complete** - Implemented and verified
- ⏸️ **Blocked** - Cannot proceed (see Comments for blocker)
- ⏭️ **Deferred** - Deprioritized, will address later

---

## Priority 0: Critical Path (Blocks L1 Autonomy)

### From: tick_speed_semantics.md (v1.1)

| Task | Owner | Status | Spec Reference | Verification | Comments |
|------|-------|--------|----------------|--------------|----------|
| Add `tick_reason` field to frame.start or tick.update event | Felix | 🔴 | §Event Emission Contract | Every frame event includes tick_reason field | Decide: add to existing frame.start or create new tick.update? |
| Implement `classify_tick_reason()` function in tick scheduler | Felix | 🔴 | §Algorithm | Deterministic classification matches minimum interval source | Returns 'stimulus' \| 'activation' \| 'arousal_floor' |
| Fix units mismatch: `MAX_INTERVAL_S` → `MAX_INTERVAL_MS` | Felix | 🔴 | Line 36, 400 | Config parameter named MAX_INTERVAL_MS | Simple rename |
| Wire tick_reason into engine emission at frame start | Felix | 🔴 | §Event Emission Contract | AutonomyIndicator receives tick_reason within 1 tick | Must emit BEFORE tick processing begins |

### From: phenomenological_health.md (v1.1)

| Task | Owner | Status | Spec Reference | Verification | Comments |
|------|-------|--------|----------------|--------------|----------|
| Implement `compute_thrashing_score()` function | Felix/Atlas | 🔴 | §Algorithm, Component 4 | Thrashing score computed from flip EMA + inverse progress/efficiency | Returns (thrashing_score, is_thrashing) |
| Add thrashing fields to health.phenomenological event | Felix/Atlas | 🔴 | §Event Emission Contract | Event includes thrashing_score and is_thrashing fields | Optional fields (only if multiplicity signals available) |
| Implement `generate_health_narrative()` function | Felix/Atlas | 🔴 | §Narrative Template Wiring | Narrative matches degradation cause (coherence < 0.4 → "fragmentation") | Backend generates narrative, not UI |
| Emit health.phenomenological events (periodic + on change) | Felix/Atlas | 🔴 | §Event Emission Contract, When to Emit | Events emitted every 5 ticks AND when \|Δhealth\| > 0.1 | Must emit AFTER WM, entities, multiplicity available |

### From: dual_learning_authoring.md (v1.1)

| Task | Owner | Status | Spec Reference | Verification | Comments |
|------|-------|--------|----------------|--------------|----------|
| Create golden set (12 examples + FalkorDB verification) | Luca | 🔴 | §Phase 2 Deliverable #3 | 12 worked examples (4 per scope) that pass parser and appear in FalkorDB | Required for Felix's end-to-end parser tests |

---

## Priority 1: High Impact (Enables Core Features)

### From: tick_speed_semantics.md (v1.1)

| Task | Owner | Status | Spec Reference | Verification | Comments |
|------|-------|--------|----------------|--------------|----------|
| Implement QuantileGate class for zero-constants enforcement | Felix | 🔴 | §Zero Constants Enforcement | Rolling histograms track energy/arousal, gates computed from percentiles | Phase 2 (after 1 week of telemetry) |
| Replace ACTIVATION_ENERGY_THRESHOLD with Q75 gate | Felix | 🔴 | §Zero Constants Enforcement | Gate computed from rolling histogram of total_active_energy | Phase 2 |
| Replace AROUSAL_INTERVAL_CAP with Q90 gate | Felix | 🔴 | §Zero Constants Enforcement | Gate computed from rolling histogram of mean_arousal | Phase 2 |
| Implement EMA-based ACTIVATION_INTERVAL_SCALE adaptation | Felix | 🔴 | §Zero Constants Enforcement | Scale adapts to tick reason distribution (target 40-60% activation) | Phase 2 |

### From: phenomenological_health.md (v1.1)

| Task | Owner | Status | Spec Reference | Verification | Comments |
|------|-------|--------|----------------|--------------|----------|
| Implement health band mapping function | Felix/Atlas | 🔴 | §Verification Criteria, Health Band Definitions | Continuous health score → discrete band ('excellent' \| 'good' \| 'adequate' \| 'degraded' \| 'critical') | Maps 0.85-1.0 → excellent, 0.70-0.84 → good, etc. |
| Wire health events to AutonomyMonitor for health-gated autonomy | Iris | 🔴 | §Event Emission Contract, Consumer Contract | Health thresholds gate autonomy levels (excellent → L3/L4, degraded → L0/L1) | UI component receives health.phenomenological events |
| Implement HealthDashboard health bands + narrative display | Iris | 🔴 | §Event Emission Contract, Consumer Contract | Dashboard renders health_band with color coding + health_narrative text | Primary consumer of health.phenomenological events |

### From: dual_learning_authoring.md (v1.1)

| Task | Owner | Status | Spec Reference | Verification | Comments |
|------|-------|--------|----------------|--------------|----------|
| Update EventType enum to include health.phenomenological | Felix/Atlas | 🔴 | Nicolas feedback §1.2 | Enum includes 'health.phenomenological', not just 'health_update' | Event name drift fix |
| Update EventType enum to include weights.updated | Felix/Atlas | 🔴 | Nicolas feedback §1.2 | Enum includes 'weights.updated' | Currently emitted but not in enum |
| Update EventType enum to include wm.emit | Felix/Atlas | 🔴 | Nicolas feedback §1.2 | Enum includes 'wm.emit' with selected_entities + token shares | Currently emitted but not in enum |

---

## Priority 2: Operational Completeness

### From: System-wide (Nicolas feedback §1.3, 6.1, 6.2)

| Task | Owner | Status | Spec Reference | Verification | Comments |
|------|-------|--------|----------------|--------------|----------|
| Fix system-status heartbeat sources | Atlas | 🔴 | Nicolas feedback §1.3 | /consciousness/system-status reads separate heartbeat files for stimulus_injection and autonomy_orchestrator | Currently reads conversation_watcher heartbeat for all services |
| Track timestamp of last stimulus in engine | Felix | 🔴 | Nicolas feedback §6.1 | Engine tracks last_stimulus_timestamp_ms, feeds into state broadcast | Fill TODO, enables autonomy badge "time since stimulus" |
| Add scope-routing to Stimulus Injection service | Atlas | 🔴 | Nicolas feedback §6.2 | Use metadata (actor, conversation_id) to route to correct N1 graph | Prevents "personal → all citizens" cross-talk |

### From: tick_speed_semantics.md (v1.1)

| Task | Owner | Status | Spec Reference | Verification | Comments |
|------|-------|--------|----------------|--------------|----------|
| Implement autonomy.window_summary event emission | Felix | 🔴 | §Telemetry | Emitted every 10 ticks with rolling window stats | Secondary event, lower priority than tick_reason in frame events |
| Add test_tick_reason_emission() acceptance test | Felix | 🔴 | §Event Emission Contract, Verification Hook | Test verifies every event has tick_reason field | Unit test |
| Add test_zero_constants_convergence() acceptance test | Felix | 🔴 | §Zero Constants Enforcement, Acceptance check | Test verifies gates converge over 1-hour mixed workload | Integration test, Phase 2 |

### From: phenomenological_health.md (v1.1)

| Task | Owner | Status | Spec Reference | Verification | Comments |
|------|-------|--------|----------------|--------------|----------|
| Implement health.rapid_degradation alert event | Felix/Atlas | 🔴 | §Telemetry, Alert Event | Emitted when health collapses rapidly (sentinel trigger) | For sentinel monitoring |
| Add test_health_event_emission() acceptance test | Felix/Atlas | 🔴 | §Event Emission Contract, Verification Hook | Test verifies event structure and health_band matches score | Unit test |
| Add Acceptance Test 1: Flow Drill | Felix | 🔴 | §Verification Criteria, Acceptance Test 1 | Optimal WM utilization → flow_state 0.8-1.0, health_band "good" or "excellent" | Integration test |
| Add Acceptance Test 2: Fragmentation Drill | Felix | 🔴 | §Verification Criteria, Acceptance Test 2 | Low coherence → health_band "degraded", narrative mentions "fragmentation" | Integration test |
| Add Acceptance Test 3: Identity Conflict Drill | Felix | 🔴 | §Verification Criteria, Acceptance Test 3 | Conflicting identities → multiplicity_health < 0.4, health_band "degraded" | Integration test |
| Add Acceptance Test 4: Recovery Drill | Felix | 🔴 | §Verification Criteria, Acceptance Test 4 | Health recovery from degraded → good within expected timeframe | Integration test |

---

## Priority 3: Nice-to-Have (Polish & Enhancement)

### From: dual_learning_authoring.md (v1.1)

| Task | Owner | Status | Spec Reference | Verification | Comments |
|------|-------|--------|----------------|--------------|----------|
| Create operator checklist (one-page) | Luca | 🔴 | Nicolas feedback §5 | Checklist mirrors required fields list for self-validation | Phase 2 Deliverable #3 |
| Add FalkorDB verification snippets to examples | Luca | 🔴 | Nicolas feedback §5 | Golden examples include Cypher queries showing formation succeeded | Phase 2 Deliverable #3 |

### From: phenomenological_health.md (v1.1)

| Task | Owner | Status | Spec Reference | Verification | Comments |
|------|-------|--------|----------------|--------------|----------|
| Display thrashing banner in UI when is_thrashing=true | Iris | 🔴 | §Algorithm, Component 4, UI Integration | Banner shows: flip rate, progress, efficiency + recommendation | Uses thrashing_score from health.phenomenological event |

---

## Test & Verification Tasks (Not Implementation)

### Single-Energy Substrate Test Rewrites (Nicolas feedback §3)

| Task | Owner | Status | Reference | Verification | Comments |
|------|-------|--------|-----------|--------------|----------|
| Rewrite "diffusion conserves energy" test for single-energy | Felix | 🔴 | Nicolas feedback §3 | Test sums node.E after stride diffusion (with decay off) | Currently asserts per-entity energies (wrong model) |
| Rewrite multi-entity tests to use selection/aggregation | Felix | 🔴 | Nicolas feedback §3 | Multi-entity independence asserted via selection/aggregation, not per-node channels | Remove set_entity_energy() calls |

---

## Verification Hooks (From Nicolas feedback §8)

### Autonomy Verification

- [ ] Live run shows autonomy % >60% in rumination scenes, <50% during heavy chat
- [ ] Badge flips within 1 tick of state changes

### Health Verification

- [ ] Fragmentation drill forces coherence <0.4 and health band degrades
- [ ] Health narrative mentions "fragmentation" when coherence collapses

### Status Verification

- [ ] Stopping injector toggles only its line to "degraded"
- [ ] Watcher/TRACE remain "running" when injector stops

---

## Completion Criteria

**Priority 0 tasks MUST complete** before L1 autonomy can ship.

**Priority 1 tasks SHOULD complete** to enable core features (adaptive thresholds, health-gated autonomy).

**Priority 2 tasks IMPROVE** operational quality (monitoring, testing, routing).

**Priority 3 tasks ENHANCE** UX/DX (thrashing banner, operator checklist).

---

**Last Updated:** 2025-10-24 (after Phase 1 spec fixes)
**Next Review:** After Priority 0 tasks complete (before L1 ship)
