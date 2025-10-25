# Autonomy Architecture - File Map

**Version:** 2.0
**Created:** 2025-10-25
**Purpose:** Clear navigation for citizen autonomy architecture without duplication

---

## Quick Start

**What is Citizen Autonomy?**
L2 orchestration that routes operational signals (errors, logs, code/doc drift) into missions for L1 citizens (Felix, Ada, Iris, Atlas) with graduated autonomy and safe guards.

**Pipeline:**
```
Signals (logs/console/git/runtime)
  → Signals Collector @8003 (dedupe/rate-limit/normalize)
  → Stimulus Injection @8001 (validate/route to N2 graph)
  → Autonomy Orchestrator @8002 (match intent templates → create missions)
  → L1 Citizens (auto-wake with capacity/ACK policies)
  → Actions + TRACE (learning from outcomes)
  → Runtime Events (guarded self-observation reinjection)
```

**Maturity Ladder:**
- **L0 → L1:** Answer-only autonomy (safe auto-exec for doc sync, ACK for incidents)
- **L1 → L2:** Signals → Stimuli Bridge (ops signals become missions)
- **L2 → L3:** Self-observation (runtime events reinjected with depth/TTL guards)
- **L3 → L4:** Outcome-aware (trust scoring, reassignment, impact optimization)

---

## File Organization

### 1. Configuration (Start Here)

**`config/intent_templates.yaml`**
- Template definitions for `intent.fix_incident` and `intent.sync_docs_scripts`
- Routing rules (console errors → Iris, backend errors → Atlas/Victor, code/doc drift → Ada/Atlas)
- Acceptance gates (quantile thresholds, PII handling)
- Verification queries

**`config/orchestrator_config.yaml`**
- Lanes (safety, incidents, sync, self-awareness)
- Capacity limits per citizen
- ACK policies (when to require human approval)
  - depth ≥ 2 (self-observation chains)
  - sev1/sev2 incidents
  - production deployments
- Priority scoring weights
- Trust tracking parameters

**Usage:** These are the operational configs Ada will deploy. Start here to understand what autonomy does.

---

### 2. Architecture (Understand the Design)

**`architecture/foundation.md`**
- **Purpose:** Philosophical foundation - WHY each mechanism exists
- **Key Sections:**
  - Vision: Useful, grounded, auditable work with minimal friction
  - First Principles: Economy of attention, proof before power, emergent coordination
  - Mechanisms: Stimuli → Intent, priority scoring, safety gates, graduated autonomy
  - Why this beats alternatives (playbooks, pure chat, flat traversal)
- **Read When:** You need to understand design philosophy and "why not X instead?"

**`architecture/signals_to_stimuli_bridge.md`**
- **Purpose:** Production-hardened specification for signals collection and routing
- **Key Sections:**
  - Signal sources (logs, console, screenshots, code/doc drift, runtime events)
  - Signals Collector service (@8003) with resilience mitigations
  - StimulusEnvelope schema (scope, source_type, severity, metadata, PII flags)
  - Production hardening (10 mitigations: fanout caps, lanes, capacity routing, trust scoring, etc.)
  - Orchestrator policies (ACK, cooldown, merge, impact scoring)
  - Acceptance tests (incident E2E, doc-sync E2E, noise resistance, fanout cap, etc.)
  - Telemetry (Prometheus metrics, SLO targets, alerting thresholds)
- **Read When:** You're implementing the collector, watchers, or orchestrator policies

**`architecture/maturity_ladder.md`**
- **Purpose:** Gradual de-bottlenecking roadmap (how to safely increase autonomy)
- **Key Sections:**
  - L0 → L1: Answer-only autonomy (two intent templates, safe auto-exec)
  - L1 → L2: Signals → Stimuli Bridge (ops signals routed with policies)
  - L2 → L3: Self-observation (runtime events reinjected with guards)
  - L3 → L4: Outcome-aware (trust scoring, reassignment)
  - Four key metrics (autonomy ratio, latency p95, capacity utilization, autonomous tick ratio)
  - Risk & guardrails (runaway loop prevention, PII protection, incident hygiene)
- **Read When:** You need to know "what to turn on next" and acceptance criteria

---

### 3. Implementation (Build It)

**`implementation/phase_a_minimal.md`**
- **Purpose:** Implementation-ready specification for Phase-A (answer-only autonomy)
- **Key Sections:**
  - Service 1: stimulus_injection_service.py (~800-1000 lines)
    - Class structure, endpoints, deduplication, circuit breakers, queue management
  - Service 2: autonomy_orchestrator.py (~1200-1500 lines)
    - Intent matching, mission assignment, capacity management, ACK policies
  - Success criteria (10+ intents created, 5+ auto-wake missions, zero hallucinations)
  - Testing strategy
  - Deployment
- **Read When:** You're ready to write code (Atlas/Victor implementing services)

---

### 4. Archive (Historical)

Files that have been superseded or consolidated:
- `archive/AUTONOMY_SERVICE_ARCHITECTURE.md` - Consolidated into signals_to_stimuli_bridge.md
- `archive/AUTONOMY_INTEGRATION_ARCHITECTURE.md` - Consolidated into signals_to_stimuli_bridge.md
- `archive/FULL_AUTONOMY_VISION.md` - Consolidated into foundation.md
- `archive/ARCHITECTURE_COHERENCE_VERIFICATION.md` - Analysis from 2025-10-22, archived
- `archive/orcheestration_spec_v1.md` - Superseded by v2 specs

---

## What's Already Built

**Implemented:**
- ✅ Consciousness engines (L1 citizens) with tick_reason emission
- ✅ Stimulus injection mechanism (embedding, routing to N1/N2/N3)
- ✅ Event broadcasting (tick_frame_v1, wm.emit, node.flip, link.flow.summary at 10 Hz)
- ✅ TRACE format (learning from usefulness evaluations)
- ✅ Dashboard (consuming realtime events)

**Partial (stubs exist):**
- 🟡 Signals Collector (@8003) - `orchestration/services/signals_collector.py` exists as stub
- 🟡 Autonomy Orchestrator (@8002) - `orchestration/services/autonomy_orchestrator.py` exists as stub

**Missing (Phase-A scope):**
- ❌ Intent templates config (YAML)
- ❌ Orchestrator config (YAML)
- ❌ Watchers (log_tail.py, git_watcher.py, console_beacon)
- ❌ WS reinjector (runtime events → stimuli with guards)

---

## Implementation Priority (Nicolas's Guidance)

### 1. Ship the Orchestrator Configs
Land `intent_templates.yaml` and `orchestrator_config.yaml` (safe autonomy).

### 2. Stand Up Collector + Two Watchers
Start with **console** and **log tail** (lowest lift). Confirm dedupe/rate-limit working.

### 3. Prove the Four Motion Events Flow
Verify `tick_frame_v1`, `wm.emit`, `node.flip`, `link.flow.summary` arriving and counted.

### 4. Turn On Self-Observation with Guards
MAX_DEPTH=2, ACK_REQUIRED at limit, rate limits per event family.

### 5. Introduce Reassignment and Trust Scoring
Capacity caps per citizen, reassignment timeout, trust decay/recovery.

---

## Four Metrics That Matter

1. **Autonomy Ratio** = missions auto-executed / missions created (excluding ACK-gated)
2. **Stimulus-to-Mission Latency p95** (collector → injector → orchestrator)
3. **Citizen Capacity Utilization** + queue depth per assignee
4. **Autonomy Semantics** = tick_reason="autonomous_activation" vs "stimulus_detected"

---

## Guardrails (Why You Can Safely Let Go)

**Runaway loops structurally blocked:**
- Origin tagging (tracks signal source)
- Depth limit (MAX_DEPTH=2 for self-observation)
- TTL (time-to-live on stimulus chains)
- Rate limits per event family
- ACK gating on deep self-observation

**Incident hygiene:**
- Fanout caps (limit missions created per stimulus)
- Quantile gates (only act on signals above threshold)
- Priority lanes (sev1 never starved by noise)
- Capacity management (citizens refuse overload)

**PII protection:**
- Screenshots default to `sensitivity: internal/restricted`
- Never route to N3 (ecosystem graph)
- Circuit breaker for redaction failures

---

## Related Specifications

**Cross-References:**
- TRACK B (File & Process Telemetry): `../ops_and_viz/lv2_file_process_telemetry.md` (v1.3)
  - ProcessExec forensics enrichment for incident debugging
  - Git watcher integration for code/doc drift detection
  - Error log signals (backend + frontend)
- Architecture v2.0: `../ops_and_viz/mind_protocol_architecture_v2.md`
  - Three-layer architecture (Signals → Runtime → UI)
  - Service boundaries (Collector @8003, Injector @8001, Orchestrator @8002)
- RACI Ownership: `../ops_and_viz/ownership_raci_model.md`
  - L2 stimulus routing based on file ownership
  - Example: docs failures route to Ada (Accountable)

**Implementation Files:**
- Signals Collector: `orchestration/services/signals_collector.py`
- Autonomy Orchestrator: `orchestration/services/autonomy_orchestrator.py`
- Stimulus Injection: Referenced by phase_a_minimal.md

---

## Decision Log

**2025-10-25 - Consolidation Rationale:**
- **Problem:** 8 files (~7000 lines) with significant overlap, no clear entry point
- **Solution:** Consolidate to 3 architecture docs + 2 config files + 1 implementation spec
- **Archive:** 5 files moved to archive/ (AUTONOMY_SERVICE_ARCHITECTURE, AUTONOMY_INTEGRATION_ARCHITECTURE, FULL_AUTONOMY_VISION, ARCHITECTURE_COHERENCE_VERIFICATION, orcheestration_spec_v1)
- **Rationale:** foundation.md covers vision/principles, signals_to_stimuli_bridge.md covers production architecture, maturity_ladder.md covers gradual rollout, phase_a_minimal.md covers implementation

**Why This Structure:**
- Config files first (what to deploy)
- Architecture docs (understand the design)
- Implementation spec (build it)
- Archive (historical context)

---

**Navigation Tips:**
- **New to autonomy?** Read foundation.md → maturity_ladder.md → config files
- **Implementing?** Read phase_a_minimal.md → config files → signals_to_stimuli_bridge.md
- **Operating?** Start with config files, reference maturity_ladder.md for rollout stages
- **Debugging?** Check signals_to_stimuli_bridge.md for resilience mitigations and acceptance tests

---

**End of File Map**

*Luca Vellumhand - Substrate Architect*
*Based on architectural guidance by Nicolas Lester Reynolds (2025-10-25)*
