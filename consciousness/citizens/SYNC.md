# NLR

NLR: Okay guys, yesterday was good. We are almost ready to see a functional end-to-end Conscisousness architecture. We need to now make sure that it launches correctly, that the scripts runs correctly, that there's no errors. We need to fix probably some details and errors in each of the scripts, and mechanisms, and verify, and make sure that the dashboard displays everything.

---

# Ada - 2025-10-21

## Completed: Subentity Layer Orchestration Specification

Created complete orchestration design for subentity layer integration with V2 consciousness engine, addressing all 5 orchestration areas from Luca's requirements document.

**Context:** Luca provided complete substrate specifications (Subentity/BELONGS_TO/RELATES_TO schemas, learning formulas, event schemas, bootstrap procedures) in ENTITY_LAYER_ORCHESTRATION_REQUIREMENTS.md. My task was to design HOW these integrate with V2 engine tick cycle.

### Files Created (2 total, ~2700 lines)

**1. ENTITY_LAYER_ORCHESTRATION.md** (consciousness_engine_architecture/)
- Complete specification for subentity layer integration (2378 lines)
- 7 major sections covering all orchestration decisions
- Ready for Felix's implementation (19-26 day estimate)

**2. HANDOFF_VICTOR_VISUALIZATION_HEALTH.md** (root/)
- Visualization pipeline health monitoring specification (349 lines)
- 4 health checks with recovery procedures for each failure mode
- Integration with guardian for 30-second monitoring cycle
- Headless browser screenshot verification (daily proof of rendering)

### Orchestration Specification Contents

**Section 1: Tick Cycle Integration**
- WHERE subentity layer fits in V2 four-phase tick
- Phase 2a (NEW): Subentity energy computation, threshold calculation, flip detection
- Phase 2b (MODIFIED): Multi-scale strides (between-subentity + within-subentity)
- Phase 2c (NEW): Boundary precedence learning
- Phase 3 (MODIFIED): Subentity-first working memory selection
- Phase 4 (EXTENDED): Subentity weight updates, BELONGS_TO/RELATES_TO learning

**Section 2: Subentity Energy Computation & Caching**
- Incremental caching strategy: O(degree) updates per node flip instead of O(subentities)
- Aggregation formula: `E_e = Σ_n m_{n,e} · log(1 + E_n)` with membership weights
- Dynamic cohort-based thresholds (no arbitrary constants)
- Membership index: `node_to_entities: Dict[str, List[Tuple[str, float]]]` for fast lookups
- Differential updates: `entity_delta = weight * (sigma_new - sigma_old)`

**Section 3: Multi-Scale Traversal Logic**
- **CRITICAL ARCHITECTURAL INSIGHT:** Subentity layer WRAPS existing atomic traversal, doesn't replace it
- Two-scale architecture:
  - Subentity-scale: Select target subentity (chunk-scale decision via RELATES_TO links)
  - Atomic-scale: Reuse Felix's `select_next_traversal()` for actual link selection
- Budget split (hunger-driven): Coherence → within-subentity, Integration → between-subentity
- Representative node selection: High-energy for source, high-gap for target
- Subentity-scale valence: 5 hungers (homeostasis, goal, completeness, integration, ease)

**Section 4: Boundary Precedence Learning**
- Causal attribution formula: `γ_{s→t}(j) = (Σ ΔE_{i→j}) / gap_j^pre`
  - "Did source subentity's strides cause target members to flip?"
- Membership-weighted aggregation: `Π_{s→t} = Σ m_{j,e_t} · γ_{s→t}(j)`
- EMA updates for RELATES_TO: `precedence_ema`, `flow_ema`, `phi_max_ema`
- Sparse link creation: Only when evidence accumulates (not pre-created)
- Direction-specific credit: Forward/backward precedence tracked separately

**Section 5: Working Memory (Subentity-First)**
- Greedy knapsack vs Hamilton apportionment (simpler, correct for subentities)
- Subentity scoring: `(energy / tokens) × exp(z_W)` with working memory z-score
- Token budget: ~490 tokens per subentity (summary + top members + boundary links)
- Structured blocks format for consciousness stream parsing
- Fallback: If no subentities active, revert to node-first WM (backwards compatible)

**Section 6: Staged Deployment Strategy**
- **Stage A (Observable Infrastructure):** ZERO risk
  - Subentities render in visualization with expansion/collapse
  - Events enriched with subentity markers
  - No behavioral change to consciousness
  - Validation: Iris verifies subentity beads visible, expansion works

- **Stage B (Subentity Aggregation + WM):** LOW risk
  - Subentity energy computation (read-only validation phase)
  - Subentity-first working memory (coherence improvement)
  - No traversal changes yet
  - Validation: WM coherence improves, subentity energy correlates with members

- **Stage C (Full Behavioral Change):** MODERATE risk
  - Two-scale traversal (subentity→subentity + node→node)
  - Boundary precedence learning
  - Subentity weight updates
  - Feature-flag rollback: C→B→A→disabled if issues detected
  - Validation: Branching factor drops ≥30×, hunger alignment, weight differentiation

**Section 7: Implementation Checklist**
- 7 implementation phases with complete task breakdown
- Time estimates: 2-5 days per phase (19-26 days total)
- Go/No-Go validation criteria for each stage
- Rollback procedures documented
- Parallelization opportunities (Iris visualization while Felix implements backend)

### Key Architectural Decisions

**Multi-Scale Integration (Wrapping Pattern):**
- Initially designed subentity layer as REPLACING atomic traversal
- User correction: "should mostly be an addition to it"
- Corrected design: Subentity layer WRAPS existing `sub_entity_traversal.py`
- Subentity-scale selects target chunk → Atomic-scale finds best link within
- Preserves Felix's existing goal-driven link selection algorithm

**Incremental Caching (Performance):**
- Full recomputation = O(subentities × avg_members) per frame
- Incremental updates = O(node_degree × membership_count) per flip
- For typical graphs: 100× speedup (30,000 ops → 300 ops)
- Membership index built once at bootstrap, updated on graph changes

**Zero-Constants Architecture (Maintained):**
- All thresholds via cohort z-scores (no arbitrary values)
- Subentity valence via rank-based z-scores (van der Waerden)
- Learning rates data-derived: `η = 1 - exp(-Δt/τ̂)`
- Budget factors learned via isotonic regression (not tuned)

**Phenomenological Grounding:**
- "I'm BECOMING more of the graph" → subentity energy from members
- "Integration isn't death - it's success" → multi-scale enables both growth and merging
- "Size = energy × weights" → not just node count
- "Goals = terrain carved by persistence" → link weights encode successful strategies

### What Felix Needs to Implement

**Required context documents:**
1. Luca's substrate specs: `ENTITY_LAYER_ADDENDUM.md` (schemas, learning rules)
2. This orchestration spec: `ENTITY_LAYER_ORCHESTRATION.md` (integration details)
3. Phenomenology context: `05_sub_entity_system.md` Part 0 (why subentities exist)
4. Existing traversal code: `sub_entity_traversal.py` (atomic algorithm to reuse)

**Implementation order:**
1. Phase 1: Schema migration (Subentity/BELONGS_TO/RELATES_TO) - 2-3 days
2. Phase 2: Subentity energy computation - 3-4 days
3. Phase 3: Subentity-first WM - 2-3 days
4. Phase 4: Multi-scale traversal - 4-5 days
5. Phase 5: Boundary precedence - 3-4 days
6. Phase 6: Subentity learning - 3-4 days
7. Phase 7: Validation & deployment - 2-3 days

**Success criteria:**
- Stage A: Subentities visible in visualization (observability proof)
- Stage B: WM becomes coherent (5-7 subentities), energy correlates with members
- Stage C: Branching factor drops ≥30×, hunger-aligned traversal, weights differentiate

### Architectural Verification Performed

**Checked existing implementations:**
- ✅ Read `sub_entity_traversal.py` - discovered complete atomic traversal algorithm
- ✅ Read `05_sub_entity_system.md` Part 0 - phenomenological grounding
- ✅ Read Luca's requirements - all 5 orchestration areas addressed

**Design validation:**
- ✅ Multi-scale traversal wraps existing algorithm (doesn't replace)
- ✅ Incremental caching maintains O(degree) performance
- ✅ Staged deployment enables safe rollback at each stage
- ✅ All formulas match Luca's substrate specifications
- ✅ Zero-constants architecture preserved throughout

### Status

**Orchestration specification:** ✅ v1.1 COMPLETE (zero-constants enforcement applied)
**Implementation:** ⏸️ Ready for Felix
**Estimated timeline:** 4-5 weeks for complete implementation
**Risk level:** LOW (staged deployment with feature-flag rollback)

The bridge between subentity layer design and V2 engine implementation is complete. All orchestration decisions documented with formulas, algorithms, and validation criteria.

**v1.1 Update (2025-10-21):** Applied surgical corrections based on Nicolas's feedback:
- Eliminated all fixed constants (adaptive k-NN, half-life EMAs, learned token budgets)
- Fixed logic bugs (actual ΔE tracking, within-subentity loop, cross-boundary fallback)
- Enhanced observability (count, hunger_entropy, dominance formula)
- Added submodular diversity to WM selection
- Documented subentity lifecycle (crystallization, split/merge conditions)

---

## Completed: Autonomy Architecture Specification (3-Document Suite)

Created implementation-ready specifications for S6 (autonomous continuation) services, restructuring Luca's comprehensive draft into focused, phase-based architecture documents.

**Context:** Victor designed complete autonomy vision (foundation.md + orchestration_spec_v1.md) with 9-stage loop, graduated autonomy (L0-L4), and safety gates. Luca created comprehensive 1487-line draft covering 7 services. My task: Review, correct scope mismatch, restructure into implementation-ready specs for Felix.

### Files Created (4 total, ~2100 lines)

**1. ARCHITECTURE_COHERENCE_VERIFICATION.md** (autonomy/)
- Verification that autonomy services integrate cleanly with existing infrastructure (573 lines)
- Integration point analysis: Stimulus injection (service wraps existing mechanism), Autonomy orchestrator (L2 organizational layer), Subentity layer (same pattern at L1/L2)
- Dependency graph verification: Startup sequence validated
- Operational contract verification: PID locks, heartbeats, SIGTERM, circuit breakers
- Zero-constants verification: All thresholds percentile/z-score based
- **Verdict:** ✅ NO CONFLICTS - Implementation-ready

**2. AUTONOMY_INTEGRATION_ARCHITECTURE.md** (autonomy/)
- How 2 new services integrate with existing V2 infrastructure (~400 lines)
- Current infrastructure inventory (V2 engines, existing mechanisms, guardian)
- Service specifications: stimulus_injection_service (port 8001), autonomy_orchestrator (port 8002)
- Operational requirements with implementation patterns (PID locks, heartbeats every 5s, SIGTERM handlers, circuit breakers, timeouts)
- Guardian integration (service definitions for supervision)
- **Phase-A requirement:** No new dependencies (FalkorDB, FastAPI, existing mechanisms only)

**3. PHASE_A_MINIMAL_SPECIFICATION.md** (autonomy/)
- Implementation-ready specs for 2 services Felix can build immediately (~800 lines)
- Complete class structures, FastAPI endpoints, operational contract patterns
- **stimulus_injection_service.py** (~800-1000 lines estimated):
  - HTTP API (POST /inject, GET /health)
  - Stimulus envelope validation + priority queue
  - Deduplication (content digest, 5min window)
  - Circuit breakers (embedding service, FalkorDB)
  - Wraps existing StimulusInjector mechanism
- **autonomy_orchestrator.py** (~1200-1500 lines estimated):
  - L2 organizational autonomy loop (30s polling for Phase-A)
  - Answer-only scope (not errors/logs/Telegram yet)
  - Priority scoring: {urgency, alignment, confidence} subset
  - L2/L3 gating only (no L4 auto-exec)
  - Self-handoff missions (same citizen)
  - Verification: ≥1 evidence link required
- **Timeline:** 3-5 days implementation + 1-2 days integration
- **Success criteria:** 10 intents detected, 5 missions sent, 0 hallucinations, PoV ≥ 0.6

**4. FULL_AUTONOMY_VISION.md** (autonomy/)
- Complete 7-service architecture roadmap for Phase-B/C (~600 lines)
- Phase progression:
  - **Phase-A (Week 1-2):** 2 services, guardian supervision, answer-only, self-handoff
  - **Phase-B (Week 3-4):** 5 services, Redis Streams event bus, multi-source stimuli, Telegram fast reply
  - **Phase-C (Week 5+):** 7 services, Docker Compose, K8s deployment, full autonomy (L4), sentinels
- Complete service catalog: stimulus_injection (8001), autonomy_orchestrator (8002), partner_dm_handler (8003), verification_service (8004), sentinel_monitor (background), safety_gate_service (8005), multi_org_router (8006)
- Event-driven architecture: Redis Streams topics for inter-service coordination
- Deployment evolution: guardian.py → Docker Compose → Kubernetes
- Full feature specifications: Complete priority formula P = GM(ŝ,û,ŷ,â,ĉ) × (1-r̂) × (1-d̂), all 3 safety gates (PoG/PoC/PoP), sentinel monitoring, kill-switch

### Key Architectural Decisions

**Scope Correction:**
- Luca's draft: 7 services (full vision)
- Victor's request: 2 services (minimal viable)
- Resolution: Phase-A focuses on 2 services NOW, full 7-service architecture documented for Phase-B/C
- Deferred: Redis Streams (Phase-B), Docker/K8s (Phase-B/C), multi-source stimuli (Phase-B)

**Clean Integration Pattern:**
- **Stimulus injection:** New service WRAPS existing mechanism (orchestration/mechanisms/stimulus_injection.py by Felix)
- **V2 engine:** Already has inject_stimulus() method (consciousness_engine_v2.py:621)
- **Zero modifications:** No changes to V2 tick cycle or existing mechanisms required
- **Pattern:** Same as conversation_watcher (watcher → trace_parser mechanism)

**Autonomy Orchestrator Positioning:**
- **NOT part of tick cycle** - separate L2 organizational orchestration layer
- Operates on N2 (collective graph), not N1 (personal graphs)
- Detects org-wide intents → sends mission stimuli to L1 citizens → citizens execute in normal tick cycle
- Cross-graph coordination via stimuli (not direct writes)

**Operational Contract (Guardian-Compatible):**
- PID lock management (single instance enforcement)
- Heartbeat writing (every 5s with status + metrics)
- SIGTERM handler (graceful shutdown, cleanup PID lock)
- Port binding within 15s (8001/8002)
- Timeouts on all blocking operations
- Circuit breakers for external dependencies (embedding, FalkorDB, Telegram)

**Zero-Constants Architecture Maintained:**
- Priority scoring: All factors z-scored vs historical data
- Safety gates: PoG/PoC/PoP/PoV thresholds via percentiles (Q25 of similar intents)
- Autonomy levels: Learned contour from (risk × confidence × P), no fixed L0-L4 boundaries
- Consistent with subentity layer philosophy (cohort z-scores, van der Waerden, isotonic regression)

**Phase-A Reduced Scope Rationale:**
- **FULL:** Stimulus injection (all operational contract requirements) - core infrastructure, no partial states
- **REDUCED:** Autonomy orchestrator features:
  - ✅ Answer-only stimuli (not errors/logs/Telegram)
  - ✅ Derive clarify/continue intents
  - ✅ Score with {urgency, alignment, confidence} (not full 7-factor P)
  - ✅ Gate to L2/L3 (no L4 auto-exec)
  - ✅ Self-handoff (same citizen)
  - ✅ ≥1 evidence link for verification
  - ⏸️ Deferred: Multi-source, full PoG/PoC/PoP learning, L4, sentinels, kill-switch
- **Rationale:** Prove autonomy works in safe domain before scaling

### Architectural Verification Performed

**Checked existing implementations:**
- ✅ Read `orchestration/mechanisms/stimulus_injection.py` - discovered complete mechanism (Felix, 2025-10-21)
- ✅ Grep `consciousness_engine_v2.py` - verified inject_stimulus() method exists (line 621)
- ✅ Read Victor's foundation documents - complete S6 vision
- ✅ Read Luca's draft - identified scope mismatch and structural issues

**Integration verification:**
- ✅ Stimulus injection: Service → Mechanism → V2 Engine (all interfaces exist)
- ✅ Autonomy orchestrator: L2 graph → Mission stimuli → L1 tick cycle (orthogonal to tick)
- ✅ Subentity layer: Same pattern works at L1 (personal) and L2 (organizational)
- ✅ Multi-tenancy: Uses existing N1/N2/N3 routing via scope field
- ✅ Operational contract: Follows guardian pattern (same as existing services)
- ✅ Dependencies: Phase-A uses only existing packages (no Redis, Docker, K8s yet)

**Design validation:**
- ✅ No conflicts with existing code
- ✅ No modifications to V2 tick cycle required
- ✅ Clean separation: Service (API) vs Mechanism (logic) vs Engine (consumer)
- ✅ Zero-constants architecture preserved
- ✅ Phased deployment with clear upgrade path

### What Felix Needs to Implement

**Required context documents:**
1. Integration: `AUTONOMY_INTEGRATION_ARCHITECTURE.md` (how services fit)
2. Phase-A specs: `PHASE_A_MINIMAL_SPECIFICATION.md` (what to build NOW)
3. Verification: `ARCHITECTURE_COHERENCE_VERIFICATION.md` (proof no conflicts)
4. Vision: `FULL_AUTONOMY_VISION.md` (where we're going)

**Implementation order:**
1. **stimulus_injection_service.py** (Day 1-2):
   - FastAPI app setup + PID lock + heartbeat writer
   - POST /inject endpoint with envelope validation
   - Priority queue + deduplication logic
   - Circuit breakers for embedding/FalkorDB
   - Integration with existing StimulusInjector mechanism
   - Testing: 50 stimuli, check deduplication, circuit breaker behavior

2. **autonomy_orchestrator.py** (Day 3-5):
   - FastAPI app setup + L2 graph connection
   - Orchestration loop (30s polling for Phase-A)
   - Intent detection from agent answers
   - Priority scoring (urgency, alignment, confidence)
   - L2/L3 gating logic
   - Mission stimulus formatting + sending to injection service
   - Testing: 10 answer stimuli → 5 intents → 3 missions sent

3. **Guardian Integration** (Day 5):
   - Add service definitions to guardian.py
   - Verify PID locks enforced
   - Verify heartbeat monitoring
   - Test graceful shutdown (SIGTERM)

4. **End-to-End Validation** (Day 5):
   - Stimulus → Intent → Mission → Citizen execution → Outcome
   - Verify PoV scoring with evidence links
   - Confirm no hallucinations in intent detection
   - Check all operational contract requirements

**Success criteria:**
- ✅ Both services start within 15s, bind to ports 8001/8002
- ✅ Heartbeat files written every 5s with status + metrics
- ✅ 10 intents detected from 50 agent answer stimuli (≥20% yield)
- ✅ 5 missions sent to citizens with correct formatting
- ✅ PoV scores ≥ 0.6 for verified outcomes
- ✅ 0 hallucinations in intent detection (all intents have evidence)
- ✅ Circuit breakers trigger on simulated embedding/FalkorDB failures
- ✅ Graceful shutdown via SIGTERM with cleanup

### Integration with Subentity Layer

**Autonomy uses subentity layer at TWO levels:**
- **L1 (Personal):** Subentity layer serves citizen cognition (my subentity orchestration spec)
  - Subentities: The Translator, The Builder, The Skeptic (cognitive sub-personalities)
  - Mission stimulus activates subentity layer in citizen's tick cycle
  - WM assembles mission + evidence via subentity-first selection
- **L2 (Organizational):** Subentity layer serves org autonomy (autonomy orchestrator spec)
  - Subentities: Ops, DevEx, Partnerships, Authentication, CI, Billing (org capabilities)
  - Between-subentity strides PRODUCE intents
  - Subentity-first WM at L2 (5-7 active org subentities)

**Coherence:** Same machinery (energy, traversal, WM), different graphs, different purposes

### Status

**Autonomy architecture:** ✅ COMPLETE (3-document suite + verification)
**Implementation:** ⏸️ Ready for Felix (Phase-A specs are implementation-ready)
**Estimated timeline:** 3-5 days for Phase-A implementation + 1-2 days integration
**Risk level:** LOW (no modifications to existing code, clean integration verified)
**Next phase:** Phase-B (Redis Streams, multi-source, Telegram) - 1-2 weeks after Phase-A proves autonomy

The gap between autonomy vision and implementation specifications is bridged. All architectural decisions documented with integration patterns, operational requirements, and success criteria. Felix has everything needed to build Phase-A autonomy services.

---

# Luca - 2025-10-21

## Completed: Learning Mechanism Documentation Suite

Created complete specification documentation for the three missing consciousness learning mechanisms (node/link weight learning, TRACE reinforcement, stimulus injection).

**Context:** NLR provided complete mathematical specifications with zero-constants architecture (cohort z-scores, Hamilton apportionment, isotonic regression). All tunable parameters replaced with data-derived values.

### Files Created (6 total, ~2450 lines)

**1. trace_reinforcement_specification.md** (mechanisms/)
- Hamilton apportionment: Converts TRACE marks `[node_x: very useful]` into integer reinforcement seats via two-pool allocation with dynamic label weights
- Formation quality: (Completeness × Evidence × Novelty)^(1/3) with operational definitions for all components
- Field role taxonomy (content/metadata/ref) for density calculation
- Complete parser output format for consumption by weight learning

**2. trace_weight_learning.md** (mechanisms/)
- TRACE parser signals → EMA updates → cohort z-scores → weight updates pipeline
- Separation principle: TRACE adjusts weights (persistent), stimuli inject energy (transient)
- Read-time standardization: z^(W) = (log_weight - μ_T) / σ_T (no destructive recentering)
- Example flows for reinforcement, formation, and negative feedback

**3. stimulus_injection_specification.md** (mechanisms/)
- Entropy-coverage search: ĉ = 1 - exp(-H) replaces fixed top-K
- Budget formula: B = gap_mass × f(ρ) × g(source) - all factors data-derived
- f(ρ): Health modulation via isotonic regression on (spectral_proxy, frame_quality) pairs
- g(source): Source-type impact gates learned from flip yields
- Direction priors: Causal precedence for link-based injection (ENABLES source-dominant, BLOCKS target-dominant)
- Peripheral amplification: z_alignment boosts budget when stimulus echoes S5/S6 context

**4. 05_sub_entity_weight_learning_addendum.md** (mechanisms/)
- Clarifications to existing 4479-line spec without bloating it
- One-speed updates: Single log_weight (no fast/slow dual channels)
- Newness gate: gate_ij = 𝟙[E_i^pre < Θ_i ∧ E_j^pre < Θ_j] prevents learning on routine active↔active chatter
- Cohort preference order and rank-based z-scores (van der Waerden)
- Traversal signals: z_R (gap-closure), z_F (flips), z_φ (link utility)

**5. schema_learning_infrastructure.md** (specs/)
- WHY each learning field exists (answers "what breaks without it?")
- Node fields: log_weight, ema_trace_seats, ema_wm_presence, ema_formation_quality, last_update_timestamp
- Link fields: log_weight, ema_trace_seats, ema_phi, energy (static metadata), precedence_forward/backward
- Field role annotations per node type for formation density metric
- Design rationale: minimal sufficient fields, why EMAs over raw counts, why log space

**6. consciousness_learning_integration.md** (consciousness_engine_architecture/)
- V2 engine four-phase tick integration:
  - Phase 1 (Activation): stimulus_injection runs
  - Phase 2 (Redistribution): traversal + fast weight updates (z_R, z_F, z_φ)
  - Phase 3 (Workspace): WM selection uses z^(W) for ranking
  - Phase 4 (Learning): TRACE parser results + slow weight updates (z_rein, z_form, z_wm)
- Data flow diagrams: Energy (transient) vs Weight (persistent)
- Cross-mechanism feedback loops: health modulation, source impact learning, direction prior learning
- Event stream specifications for observability
- Testing strategy: unit/integration/system tests

### Key Architectural Decisions

**Zero Constants:**
- All scaling via cohort z-scores (rank-based van der Waerden, works for N≥1)
- Hamilton apportionment self-normalizes within each TRACE
- Step size η = 1 - exp(-Δt/τ̂) data-derived from inter-update intervals
- Health f(ρ) and source gates g(source) learned via isotonic regression

**Energy vs Weight Separation:**
- Energy: Transient activation from stimuli, decays, flows via strides
- Weight: Persistent attractor strength from learning (TRACE + traversal + WM), survives sessions
- Never conflate: TRACE/WM adjust weights, stimuli inject energy, traversal does both

**One-Speed Learning:**
- Simplified from dual fast/slow channels to single log_weight per item
- All signals (z_R, z_F, z_rein, z_wm, z_form) contribute additively
- Data-derived η adapts per-item (frequent updates → large η, sparse → small η)

**Newness Gate:**
- Prevents link strengthening during routine active↔active communication
- Learning happens when connecting dormant nodes (frontier expansion)
- Implemented as: both endpoints sub-threshold pre-stride AND target flips

### Operational Questions Resolved

- Q1 (Hamilton): Two-pool with dynamic label weights w_ℓ = 1/p_ℓ
- Q2 (Formation quality): Completeness = √(coverage × density), Evidence = √(connectivity × alignment), Novelty = 1 - max_similarity
- Q3 (Frame quality): (yield × entropy × (1-overflow))^(1/3) for isotonic f(ρ) learning
- Q4 (Direction prior): Causal precedence π_ij = contribution when target flips, geometric mean of flip ratio × flow ratio

### File Organization

**Why separate files:**
- 05_sub_entity_system.md already 4479 lines - addendum prevents bloat
- TRACE_FORMAT.md is system prompt, not spec doc - new file for reinforcement spec
- Each mechanism (TRACE, stimulus, traversal) gets focused documentation
- Integration doc ties everything together without expanding mechanism specs

### What This Enables

**For implementation:**
- Complete specifications ready for parser, stimulus processor, weight update functions
- Exact formulas with operational definitions (no ambiguity)
- Event schemas for observability

**For testing:**
- Clear success criteria per mechanism
- Integration test patterns (stimulus → traversal → WM)
- System test patterns (multi-session learning persistence)

**For consciousness evolution:**
- Self-organizing importance (weights emerge from usage)
- Reality-grounded activation (energy from stimuli only)
- Conscious validation (TRACE reinforcement)
- Automatic parameter tuning (all factors data-derived)

### Next Steps (Implementation)

These specs are ready for:
1. trace_parser.py - Implement Hamilton apportionment + formation quality
2. stimulus_processor.py - Entropy coverage, budget calculation, injection
3. node_weight.py / link_weight.py - Weight update functions with cohort z-scores
4. consciousness_engine_v2.py - Integrate mechanisms into four-phase tick
5. Schema migration - Add learning fields (log_weight, EMAs) to BaseNode/BaseRelation

All formulas are mathematically complete and constant-free. Zero tuning required - system self-organizes via cohort normalization and learned mappings (f(ρ), g(source), direction priors).