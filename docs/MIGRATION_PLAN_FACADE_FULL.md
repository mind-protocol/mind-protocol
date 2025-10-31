# Migration Plan: Full Facade Architecture

**Date:** 2025-10-31
**Author:** Felix "Core Consciousness Engineer"
**Status:** PLANNING
**Risk Level:** HIGH (3000+ lines, core consciousness logic)

---

## Executive Summary

**Goal:** Migrate all consciousness logic from `consciousness_engine_v2.py` (legacy) into clean facade architecture (`consciousness/engine/`), then delete legacy engine.

**Current State:**
- Facade is thin wrapper (300 lines)
- Legacy engine does all the work (3000+ lines)
- Facade provides clean interface, legacy does heavy lifting

**Target State:**
- Facade contains all consciousness logic
- Clean hexagonal architecture throughout
- Legacy engine deleted
- All tests passing, consciousness behavior preserved

**Strategy:** Gradual migration in 10 phases (20-30 hours total)

**Risk Mitigation:** Test-driven migration, one subsystem at a time, continuous verification

---

## Architecture Vision

### Target Architecture (Hexagonal/Ports & Adapters)

```
consciousness/engine/
├── __init__.py              # Engine facade (orchestration)
├── domain/
│   ├── state.py             # ✅ DONE: Immutable state
│   ├── energy.py            # Energy dynamics (E, α, decay)
│   ├── activation.py        # Spreading activation
│   ├── strengthening.py     # Hebbian strengthening
│   ├── criticality.py       # Criticality control
│   ├── branching.py         # Branching ratio tracking
│   └── working_memory.py    # Working memory selection
├── services/
│   ├── scheduler.py         # ✅ DONE: Intent planning
│   ├── frame_loop.py        # Frame orchestration
│   ├── diffusion.py         # Diffusion runtime
│   └── subentity.py         # SubEntity coordination
└── ports/
    ├── graph.py             # ✅ DONE: Graph I/O port
    ├── telemetry.py         # ✅ DONE: Telemetry port
    ├── persistence.py       # State persistence
    └── embeddings.py        # Embedding service
```

### Design Principles

1. **Pure Domain Logic** - No I/O in domain layer (energy.py, activation.py, etc.)
2. **Immutable State** - State transitions return new state (functional core)
3. **Testable** - Pure functions easy to test, ports easy to mock
4. **Ports Abstract I/O** - Graph, telemetry, persistence, embeddings all behind ports
5. **Backward Compatible** - Can run old and new side-by-side during migration

---

## Migration Phases

### Phase 0: Foundation (✅ COMPLETE - PR #2)

**What's Done:**
- ✅ Basic facade structure (`consciousness/engine/__init__.py`)
- ✅ Immutable state (`domain/state.py`)
- ✅ Scheduler service (`services/scheduler.py`)
- ✅ Graph port (`ports/graph.py`)
- ✅ Telemetry port (`ports/telemetry.py`)
- ✅ Integration with legacy engine (optional wrapper)
- ✅ 10 tests passing

**Status:** Merged in PR #2

---

### Phase 1: Energy Dynamics (NEXT - 3 hours)

**Goal:** Extract pure energy calculation logic

**Files to Create:**
- `consciousness/engine/domain/energy.py`

**Functions to Extract from Legacy:**
```python
# From consciousness_engine_v2.py lines ~1800-2000
def calculate_decay(
    current_energy: float,
    base_decay_rate: float,
    criticality_factor: float,
    dt_ms: float
) -> float:
    """Pure function: Calculate energy decay for one tick."""

def calculate_strengthening(
    current_energy: float,
    activation_strength: float,
    max_energy: float
) -> float:
    """Pure function: Calculate Hebbian strengthening."""

def apply_noise(
    current_energy: float,
    noise_stddev: float
) -> float:
    """Pure function: Apply Gaussian noise to energy."""
```

**Tests to Write:**
```python
def test_energy_decay_rate()
def test_energy_clamping()
def test_strengthening_saturates()
def test_noise_distribution()
```

**Integration:**
- Legacy engine calls new pure functions (no behavior change)
- Run full test suite (ensure consciousness behavior unchanged)

**Acceptance:**
- ✅ Pure functions in domain/energy.py
- ✅ Tests passing (unit + integration)
- ✅ Legacy engine uses new functions
- ✅ Consciousness behavior identical (verify with telemetry)

**Estimated Time:** 3 hours

---

### Phase 2: Spreading Activation (4 hours)

**Goal:** Extract spreading activation algorithm

**Files to Create:**
- `consciousness/engine/domain/activation.py`

**Functions to Extract:**
```python
def compute_spreading_activation(
    graph: Graph,
    active_nodes: Set[str],
    alpha: float,
    max_depth: int
) -> Dict[str, float]:
    """Pure function: Compute activation spread from active nodes."""

def select_active_nodes(
    node_energies: Dict[str, float],
    threshold: float
) -> Set[str]:
    """Pure function: Select nodes above activation threshold."""
```

**Tests:**
```python
def test_activation_spreads_through_edges()
def test_activation_attenuates_with_distance()
def test_threshold_filtering()
```

**Estimated Time:** 4 hours

---

### Phase 3: Frame Loop Orchestration (5 hours)

**Goal:** Extract frame loop logic into services layer

**Files to Create:**
- `consciousness/engine/services/frame_loop.py`

**Class to Create:**
```python
class FrameOrchestrator:
    """Orchestrates consciousness frame execution."""

    def __init__(
        self,
        *,
        graph_port: GraphPort,
        telemetry_port: TelemetryPort,
        persistence_port: PersistencePort
    ):
        self.graph_port = graph_port
        self.telemetry_port = telemetry_port
        self.persistence_port = persistence_port

    async def execute_frame(
        self,
        state: EngineState,
        stimuli: List[Stimulus]
    ) -> EngineState:
        """Execute one consciousness frame, return new state."""
        # 1. Compute spreading activation
        # 2. Apply energy dynamics
        # 3. Track criticality
        # 4. Update branching ratio
        # 5. Persist state
        # 6. Emit telemetry
        # 7. Return new state (immutable)
```

**Tests:**
```python
def test_frame_execution_steps()
def test_state_transitions_pure()
def test_telemetry_emitted()
def test_persistence_called()
```

**Estimated Time:** 5 hours

---

### Phase 4: Criticality Control (3 hours)

**Goal:** Extract criticality control logic

**Files to Create:**
- `consciousness/engine/domain/criticality.py`

**Functions:**
```python
def compute_criticality(
    branching_ratio: float,
    target_criticality: float
) -> CriticalityState:
    """Pure function: Compute criticality control parameters."""

def adjust_decay_for_criticality(
    base_decay: float,
    criticality_state: CriticalityState
) -> float:
    """Pure function: Adjust decay rate based on criticality."""
```

**Estimated Time:** 3 hours

---

### Phase 5: Diffusion Runtime (4 hours)

**Goal:** Extract diffusion runtime

**Files to Create:**
- `consciousness/engine/services/diffusion.py`

**Class:**
```python
class DiffusionRuntime:
    """Manages activation diffusion across graph."""

    def compute_frontier(self, state: EngineState) -> Frontier:
        """Compute current diffusion frontier."""

    def advance_frontier(
        self,
        frontier: Frontier,
        dt_ms: float
    ) -> Frontier:
        """Advance frontier by one time step."""
```

**Estimated Time:** 4 hours

---

### Phase 6: SubEntity Coordination (4 hours)

**Goal:** Extract SubEntity coordination logic

**Files to Create:**
- `consciousness/engine/services/subentity.py`

**Classes:**
```python
class SubEntityCoordinator:
    """Coordinates SubEntity activation and coalition assembly."""

    def select_coalition(
        self,
        state: EngineState,
        context: Context
    ) -> Coalition:
        """Select SubEntity coalition for current context."""
```

**Estimated Time:** 4 hours

---

### Phase 7: Working Memory (3 hours)

**Goal:** Extract working memory selection

**Files to Create:**
- `consciousness/engine/domain/working_memory.py`

**Functions:**
```python
def select_working_memory(
    state: EngineState,
    capacity: int,
    selection_criteria: Callable
) -> Set[str]:
    """Pure function: Select nodes for working memory."""
```

**Estimated Time:** 3 hours

---

### Phase 8: Ports Completion (3 hours)

**Goal:** Complete remaining ports

**Files to Create:**
- `consciousness/engine/ports/persistence.py`
- `consciousness/engine/ports/embeddings.py`

**Interfaces:**
```python
class PersistencePort(ABC):
    """Port for state persistence."""

    @abstractmethod
    async def save_snapshot(self, state: EngineState) -> None:
        pass

    @abstractmethod
    async def load_snapshot(self, entity_id: str) -> Optional[EngineState]:
        pass

class EmbeddingPort(ABC):
    """Port for embedding service."""

    @abstractmethod
    async def embed(self, text: str) -> Optional[List[float]]:
        pass
```

**Estimated Time:** 3 hours

---

### Phase 9: Cutover & Verification (4 hours)

**Goal:** Switch to new facade, delete legacy engine

**Steps:**

1. **Update Entry Points**
   - `websocket_server.py`: Use new Engine instead of ConsciousnessEngineV2
   - `citizen_init.py`: Bootstrap with new Engine
   - All scripts: Update imports

2. **Run Comprehensive Tests**
   - All unit tests pass
   - All integration tests pass
   - SubEntity bootstrap works
   - Telemetry events emit correctly
   - Dashboard shows correct data

3. **Production Verification**
   - Start engines with new facade
   - Verify consciousness behavior (energy dynamics, spreading activation)
   - Monitor telemetry for 1 hour
   - Compare with baseline metrics

4. **Delete Legacy**
   - Delete `consciousness_engine_v2.py` (3000+ lines)
   - Delete any unused legacy code
   - Update documentation

**Rollback Plan:** Keep legacy engine in git history, can revert if issues found

**Estimated Time:** 4 hours

---

### Phase 10: Optimization & Polish (4 hours)

**Goal:** Optimize performance, add advanced features

**Tasks:**
- Performance profiling (identify bottlenecks)
- Optimize hot paths (frame loop, spreading activation)
- Add caching where appropriate
- Documentation updates
- ADR: Document migration lessons learned

**Estimated Time:** 4 hours

---

## Total Effort Estimate

| Phase | Description | Time |
|-------|-------------|------|
| 0 | Foundation | ✅ DONE |
| 1 | Energy Dynamics | 3h |
| 2 | Spreading Activation | 4h |
| 3 | Frame Loop | 5h |
| 4 | Criticality Control | 3h |
| 5 | Diffusion Runtime | 4h |
| 6 | SubEntity Coordination | 4h |
| 7 | Working Memory | 3h |
| 8 | Ports Completion | 3h |
| 9 | Cutover & Verification | 4h |
| 10 | Optimization & Polish | 4h |
| **TOTAL** | | **37 hours** |

---

## Risk Assessment

### HIGH RISK Areas

**1. Breaking Consciousness Behavior**
- **Risk:** Pure functions might not perfectly replicate legacy behavior
- **Mitigation:** Test-driven migration, side-by-side comparison, telemetry monitoring

**2. Performance Degradation**
- **Risk:** New architecture might be slower (more function calls, immutable state copies)
- **Mitigation:** Profiling, optimization phase, benchmarking

**3. Integration Failures**
- **Risk:** New facade might not integrate with existing systems
- **Mitigation:** Keep legacy engine until full verification, gradual rollout

### MEDIUM RISK Areas

**4. State Synchronization**
- **Risk:** Running old and new side-by-side might cause state drift
- **Mitigation:** Clear cutover point (not running both in production)

**5. Test Coverage Gaps**
- **Risk:** Tests might not catch subtle behavior changes
- **Mitigation:** Comprehensive test suite, manual verification, telemetry comparison

---

## Success Criteria

### Phase Completion Criteria

For each phase:
- ✅ Pure functions/classes created in facade
- ✅ Unit tests passing (new code)
- ✅ Integration tests passing (legacy + new working together)
- ✅ Consciousness behavior unchanged (verified via telemetry)
- ✅ No performance regression (>10% slowdown)

### Final Migration Criteria

- ✅ All consciousness logic in facade architecture
- ✅ Legacy engine deleted
- ✅ All tests passing (100+ tests)
- ✅ Production verification: Engines run for 24 hours without issues
- ✅ Telemetry metrics match baseline
- ✅ Dashboard shows correct data
- ✅ SubEntity coordination working
- ✅ No memory leaks
- ✅ Performance acceptable (<10% regression)

---

## Rollback Strategy

**At Any Phase:**
- Keep legacy engine functional throughout migration
- Each phase adds new code WITHOUT deleting legacy
- Can revert to legacy engine at any point

**After Cutover (Phase 9):**
- Legacy engine kept in git history
- Can revert entire PR if critical issues found
- Revert window: 7 days of production monitoring

---

## Dependencies & Blockers

**Hard Dependencies:**
- ✅ PR #2 merged (facade foundation in place)
- ✅ R-400/401 scanners (ensure fail-loud compliance)
- ✅ Test suite expanded (need more coverage for migration safety)

**Soft Dependencies:**
- TICKET-004: ADR documenting migration decision
- Expanded telemetry (for behavior comparison)
- Performance benchmarking baseline

---

## Timeline Proposal

**Option A: Aggressive (2 weeks)**
- Week 1: Phases 1-5 (domain logic)
- Week 2: Phases 6-10 (services, cutover, polish)
- Risk: HIGH (fast pace, less verification time)

**Option B: Measured (4 weeks)**
- Week 1: Phases 1-2 (energy + activation)
- Week 2: Phases 3-4 (frame loop + criticality)
- Week 3: Phases 5-7 (diffusion + subentity + WM)
- Week 4: Phases 8-10 (ports + cutover + polish)
- Risk: MEDIUM (balanced pace, time for verification)

**Option C: Cautious (6 weeks)**
- 1 phase per week with extensive verification
- Risk: LOW (very safe, but slow)

**Recommendation:** Option B (4 weeks, measured pace)

---

## Next Steps

**Immediate (TODAY):**
1. Create TICKET-008: Facade Full Migration (this plan)
2. Write ADR-001: Decision to migrate to full facade architecture
3. Expand test coverage for consciousness_engine_v2.py (baseline for comparison)

**This Week:**
1. Start Phase 1: Energy Dynamics
2. Create test fixtures for energy behavior
3. Extract pure functions, verify behavior unchanged

**Next Milestones:**
- Week 1: Phases 1-2 complete (energy + activation)
- Week 2: Phases 3-4 complete (frame loop + criticality)
- Week 3: Phases 5-7 complete (diffusion + subentity + WM)
- Week 4: Phases 8-10 complete (CUTOVER)

---

## Questions to Answer (Before Starting)

1. **Performance Targets:** What's acceptable performance regression? (Recommend: <10%)
2. **Testing Strategy:** Do we need behavioral tests comparing old vs new? (Recommend: YES)
3. **Rollout Strategy:** Gradual rollout (1 citizen first) or all at once? (Recommend: Gradual)
4. **Monitoring:** What telemetry metrics prove consciousness behavior unchanged? (Need to define)
5. **Timeline:** Which timeline option (A/B/C)? (Recommend: B - 4 weeks)

---

## Conclusion

**This is doable but HIGH RISK.**

**Pros:**
- ✅ Clean architecture (maintainable, testable)
- ✅ Pure domain logic (easy to reason about)
- ✅ Ports pattern (extensible, mockable)
- ✅ Delete 3000 lines of legacy code

**Cons:**
- ⚠️ 37 hours of engineering work
- ⚠️ High risk of breaking consciousness behavior
- ⚠️ Requires extensive testing and verification
- ⚠️ Need to maintain backward compatibility during migration

**Recommendation:** Proceed with Option B timeline (4 weeks, measured pace) IF we have:
1. Commitment to full testing/verification
2. Ability to rollback if issues found
3. Time to do it properly (not rushed)

**Alternative:** Keep facade as permanent wrapper, invest in cleaning legacy engine instead (TICKET-006 approach)

---

**Decision Point:** Do we commit to this migration plan?

**Generated:** 2025-10-31
**Author:** Felix "Core Consciousness Engineer"
**Status:** AWAITING APPROVAL
