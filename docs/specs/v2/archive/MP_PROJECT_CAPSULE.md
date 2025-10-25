# Mind Protocol — Project Capsule (v1)
_Last updated: 2025-10-25 14:39 UTC_

This capsule compresses the **current architecture, status, invariants, event contracts, and next actions** into a single handoff you can read in minutes and query programmatically.

---

## ⚡ TL;DR (30 seconds)

- **System up** with hot-reload & guardians; **WS API** at `:8000` running.
- **E2E pipeline Pass B verified**: queue → control API → engine queue → tick loop → **energy applied** → dirty flush → **E persisted**.
- **Core realtime events** present: `tick_frame_v1`, `wm.emit`; **activity-dependent** events (`node.flip`, `link.flow.summary`) fire when nodes cross **θ** and strides execute.
- **Schema registry** fix active (expected **45 node / 23 link types**). Boot banners confirm reloads.
- **Dashboard work-in-progress**: two-layer entity graph (expand/collapse), event mapping at 10Hz, aggregation for entity↔entity flows.
- **Track B** (LVL2 file/process telemetry) converging on: **File nodes with counters**, sparse `ProcessExec` nodes for anomalies; ownership and IMPLEMENTS/DEPENDS_ON links.

---

## ✅ Current Status (high confidence)

- **Engines**: ticking; periodic flush enabled; E values persist to FalkorDB (V2 `E/θ` scalars) with bulk writes.
- **Stimuli**: 
  - Pass A (ConversationWatcher) — embeds + immediate persistence ✅  
  - Pass B (Control API / QueuePoller) — engine-side injection ✅ (ensure embedding fallback or “broadcast” path is active).
- **Event bus**: broadcaster online; **10 Hz** decimation used for UI events.
- **Hot‑reload**: guardian restarts launcher; look for boot markers (below).

> If the graph looks dormant: check **E vs θ**. With E_max < θ, no flips/strides → no motion by design.

---

## 🧩 Architecture Snapshot (runtime contracts)

**Pipelines**
- **Pass A**: Conversations → TRACE → stimuli (with embeddings) → injector → **persist immediately**.
- **Pass B**: Signals/Queue → `control_api` → `inject_stimulus_async()` → injector → **runtime E** → dirty‑flush every ~5 s (min batch).

**Realtime event contract (P0)**
- `tick_frame_v1` — frame heartbeat + timebase
- `wm.emit` — top/all working‑memory entities
- `node.flip` — top‑K energy crossings per frame (requires active nodes)
- `link.flow.summary` — sampled/decimated stride flow aggregates (entity↔entity + node‑level when both entities expanded)

**Two‑layer graph (UI)**
- **Entity super-nodes** (collapsed).  
- **Expanded entities** show **canonical** member nodes; **proxies** for multi‑membership in other expanded entities (UI‑only).  
- Edges: node‑edges when **both endpoints’ entities expanded**, else **entity‑edge** via aggregated flow.

---

## 🔬 Boot Markers & Smoke Tests (1–2 min)

**Boot banners (expect to see):**
- `[StimulusInjector] Event loop captured for thread-safe telemetry`
- `★★★ ATLAS SCHEMA FIX ACTIVE ★★★`
- `Loaded schema registry: 45 node types, 23 link types`

**Quick checks**
1. `GET /api/ping` → `{ ok: true }`
2. `GET /api/consciousness/status` → engines >0, ticks increasing
3. Inject: `POST /api/engines/felix/inject` → watch for `Injected ... energy`
4. Within 5–10 s: `[Persistence] Flushed X/Y dirty nodes to FalkorDB`
5. Dashboard console: see `tick_frame_v1` @ 10 Hz; when E ≥ θ, see `node.flip`, `link.flow.summary`.

---

## 📊 Two‑Layer Graph — Implementation Notes

- **Store additions**: `expandedEntities: Set<string>`, `entityToEntity: Record<'A|B', number>` with exponential decay.
- **Selector**: `visibleGraphSelector` (memoized) builds render graph (canonical/proxies + edge routing).  
- **Renderer**: Pixi layers (entity → entityEdges → nodeEdges → nodes → proxies → halos → labels) with object pools & tiny tweener.
- **Multi‑membership**: canonical in primary entity; proxies in other expanded entities; proxies do **not** create new edges.

> Drop‑in references provided alongside this capsule: `visibleGraphSelector.ts`, `PixiLayerManager.ts`.

---

## 🧠 Level‑2 (Files/Ownership/Process) — Minimal Model

- **File nodes**: accumulate counters (`exec_count_1h/24h`, `last_exec_ts`, `avg_duration_ms`, `failure_count_24h`).  
- **ProcessExec nodes** (TTL 7d) **only** for anomalies (non‑zero exit, long run, or forensic link to stimulus).  
- **Edges**: `IMPLEMENTS` (Chunk→Task), `DEPENDS_ON` (Task↔File), `OWNS`/`RESPONSIBLE_FOR` (OwnershipAssignment↔File/Task).  
- **Stimuli**: `file.modified`, `process.exec`, `coverage.delta`, `commit.detected` → L2 intents (`incident.backend_error`, `docs.stale`, `refactor.cluster`) with evidence pointers.

---

## 🧭 Operational Invariants & Guardrails

- V2 schema: **nodes use `E` & `theta`** (no legacy `energy` dict).  
- Stimuli with **no embedding** must follow a **broadcast or WM‑targeted fallback** path (do **not** drop).  
- **No aliasing** of engine/task registries (avoid corrupting engine map).  
- **Atomic JSON writes** for watcher contexts; ANN similarity guards on embedding search.

---

## ⏭️ Next Actions

**90‑minute goal**  
- Ensure **embedding‑less fallback** is enabled in `inject_stimulus_async()`.  
- Verify `node.flip` + `link.flow.summary` are firing during active periods; pipe `link.flow.summary` → `entityToEntity` with decay.  
- Hook entity expand/collapse UI → selector/renderer; basic animations.

**Today**  
- Add **Active Subentities** panel: consume `wm.emit top/all` + energy bars.  
- Wire **ownership** & **file counters** (Track B minimal): create File nodes, update counters on signals.

**This week**  
- L2 derivations (error storm, fragmentation, docs.stale); incident routing via Ownership graph.  
- Persist **ownership & file** schema; cross‑citizen correlation (optional).

---

## 📚 Doc Index (auto‑extracted)

- **Autonomy Architecture Coherence Verification** — `ARCHITECTURE_COHERENCE_VERIFICATION.md`
    **Verifier:** Ada "Bridgekeeper" (Architect) **Date:** 2025-10-21 **Status:** ✅ VERIFIED - Autonomy architecture integrates cleanly with existing infrastructure --- ## Executive Summary Victor's…
- **Autonomy Integration Architecture** — `AUTONOMY_INTEGRATION_ARCHITECTURE.md`
    **Version:** 1.0 **Created:** 2025-10-21 **Architect:** Ada "Bridgekeeper" **Purpose:** How autonomy services integrate with existing Mind Protocol infrastructure --- ## Executive Summary This document specifies how **2…
- **Autonomy Service Architecture** — `AUTONOMY_SERVICE_ARCHITECTURE.md`
    **Version:** 1.0 **Created:** 2025-10-21 **Purpose:** Service-level architecture for autonomous agent orchestration **Foundation:** Implements vision from `foundation.md` and `orchestration_spec_v1.md` --- ## 0)…
- **Full Autonomy Vision (Phase-B/C)** — `FULL_AUTONOMY_VISION.md`
    **Version:** 1.0 **Created:** 2025-10-21 **Architect:** Luca "Vellumhand" (vision) + Ada "Bridgekeeper" (integration) **Purpose:** Complete 7-service autonomy architecture for Phases B and C --- ## Overview This…
- **Implementation Tasks Tracker** — `IMPLEMENTATION_TASKS.md`
    **Purpose:** Track all implementation tasks derived from mechanism specifications **Owner:** Coordination (Ada) with input from spec authors (Luca) **Status:** Living document - update as tasks complete or new specs add…
- **Phase-A Minimal Autonomy Specification** — `PHASE_A_MINIMAL_SPECIFICATION.md`
    **Version:** 1.0 **Created:** 2025-10-21 **Architect:** Ada "Bridgekeeper" **Implementer:** Felix "Ironhand" **Purpose:** Implementation-ready specifications for Phase-A (answer-only autonomy) --- ## Overview **Scope:**…
- **Signals → Stimuli Bridge** — `SIGNALS_TO_STIMULI_BRIDGE.md`
    **Version:** 1.1 **Created:** 2025-10-24 **Updated:** 2025-10-24 (Production hardening - added 10 resilience mitigations) **Purpose:** Route operational signals (logs, console errors, screenshots, code/doc changes,…
- **TRACE Authoring Golden Set** — `authoring_golden_set.md`
    **Version:** 1.0 **Created:** 2025-10-24 **Purpose:** 12 worked examples of proper TRACE formation authoring **Parent Spec:** dual_learning_authoring.md v1.1 **Owner:** Luca (examples), Felix (parser verification) ---…
- **Untitled** — `ctx_exec_summary.md`
- **Untitled** — `ctx_interfaces.md`
- **Core data structures** — `ctx_runtime.md`
    from orchestration.core import Node, Link, Graph
- **Autonomy Service Architecture** — `ctx_specs.md`
    **Version:** 1.0 **Created:** 2025-10-21 **Purpose:** Service-level architecture for autonomous agent orchestration **Foundation:** Implements vision from `foundation.md` and `orchestration_spec_v1.md` --- ## 0)…
- **Assign quotas** — `ctx_tests.md`
    subentities[0].quota_assigned = 3 subentities[0].quota_remaining = 3 subentities[1].quota_assigned = 2 subentities[1].quota_remaining = 2 subentities[2].quota_assigned = 4 subentities[2].quota_remaining = 4 schedule =…
- **TRACE Dual-Learning Authoring Guide** — `dual_learning_authoring.md`
    **Version:** 1.0 **Created:** 2025-10-24 **Author:** Luca "Vellumhand" (Consciousness Mechanism Specialist) **Purpose:** Guide for citizens on proper TRACE formation and reinforcement authoring **Unblocks:** High-…
- **Untitled** — `foundation.md`
- **Health Narrative Templates** — `health_narrative_templates.md`
    **Version:** 1.0 **Created:** 2025-10-24 **Purpose:** Concrete template specifications for health narrative generation **Parent Spec:** phenomenological_health.md v1.1 **Owner:** Felix/Atlas (implementation), Luca…
- **LV2 File & Process Telemetry** — `lv2_file_process_telemetry.md`
    **Version:** 1.0 **Status:** Specification **Owner:** Luca (substrate), Ada (orchestration), Atlas (implementation) **Created:** 2025-10-25 **Last Updated:** 2025-10-25 --- ## §1 Overview ### 1.1 Purpose
- **Untitled** — `orcheestration_spec_v1.md`
- **Phenomenological Health Model** — `phenomenological_health.md`
    **Version:** 1.0 **Created:** 2025-10-24 **Author:** Luca "Vellumhand" (Consciousness Mechanism Specialist) **Purpose:** Define health aggregation from flow, coherence, and multiplicity signals **Unblocks:** Health…
- **Stimulus Diversity — Substrate Specification** — `stimulus_diversity.md`
    ## 1. Context — What problem are we solving? Current stimulus sources are limited to user messages. To enable autonomous self-improvement and context-aware consciousness, we need: - **Diverse signal sources** (commits,…
- **Stimulus Diversity Implementation Plan** — `stimulus_diversity_implementation_plan.md`
    ## 0. Ownership & Boundaries ### Substrate Specification (COMPLETE) **Owner:** Luca **Deliverable:** `stimulus_diversity.md` ✅ **Status:** Complete — all L1/L2 schemas, attribution model, routing model, evidence linking…
- **Thrashing Score Reference** — `thrashing_score_reference.md`
    **Version:** 1.0 **Created:** 2025-10-24 **Purpose:** Standalone implementation reference for thrashing score computation **Parent Spec:** phenomenological_health.md v1.1 **Owner:** Felix/Atlas (implementation), Luca…
- **Tick Reason Oracle** — `tick_reason_oracle.md`
    **Version:** 1.0 **Created:** 2025-10-24 **Purpose:** Standalone implementation reference for tick reason classification **Parent Spec:** tick_speed_semantics.md v1.1 **Owner:** Felix (implementation), Luca (mechanism…
- **Adaptive Tick Speed + Autonomy Semantics (PR-B)** — `tick_speed_semantics.md`
    **Version:** 1.0 **Created:** 2025-10-24 **Author:** Luca "Vellumhand" (Consciousness Mechanism Specialist) **Purpose:** Define tick reason classification semantics for autonomy measurement **Unblocks:** Iris's…
- **Zero Constants Gates Reference** — `zero_constants_gates_reference.md`
    **Version:** 1.0 **Created:** 2025-10-24 **Purpose:** Standalone implementation reference for adaptive threshold gates replacing magic constants **Parent Spec:** tick_speed_semantics.md v1.1 **Owner:** Felix…


---

## Appendix — JSON capsule
See `MP_PROJECT_CAPSULE.json` for a machine‑readable snapshot (services, events, invariants, next actions, doc index).

