# Project Map (Mind Protocol)

**Purpose**: Fast orientation. Where things live, how data flows.

**Terminology Reference:** See `TAXONOMY_RECONCILIATION.md` for clean taxonomy. **SubEntity** = Scale A (neighborhoods), **Mode** = Scale B (IFS meta-roles), **Entity** = DEPRECATED.

## Design Pillars (read first)
- Nodes carry **dynamic activation energy** (single scalar E≥0).
- Links carry **affect + telemetry**; they transport energy, they don't store it.
- **SubEntities = neighborhoods** (chunk-scale, Scale A). **Active SubEntities** act as traversal agents (E > θ).
- **Modes = IFS meta-roles** (Scale B). Emergent from COACTIVATES_WITH communities.
- Traversal is **two-scale**: SubEntity-scale selection wraps atomic link selection.
- **Stimuli inject energy**; **TRACE** updates **weights** (links & nodes), never activation.
- No fixed constants: thresholds/weights use z-scores, percentiles, or half-life EMAs.

## Dataflow (overview)
Stimuli → Activation (nodes) → Traversal (strides) + **Emotion Coloring** → Learning (weights) → WM selection → LLM → TRACE → Weight updates → (repeat)

**New (2025-10-22):**
- Emotion system operational - nodes/links carry affect metadata, emotion coloring and decay active
- **Emotion gates** (2025-10-23): **complementarity** (regulation) and **resonance** (coherence) gates now **integrated** into traversal cost modulation (feature-flagged, 5/5 tests passing)
- **Coherence metric (E.6)** (2025-10-23): **quality** measurement (flow vs chaos) via frontier similarity + stride relatedness, complements ρ quantity signal (feature-flagged, 7/7 tests passing)
- **3-tier learning** (co-activation, causal, background) with **affect-weighted** strengthening
- **Context-aware TRACE** (80% local to active SubEntities, 20% global)
- **Three-factor tick speed** (stimulus + activation + arousal) enables autonomous momentum
- **Task-mode-aware fan-out** (FOCUSED/BALANCED/DIVERGENT/METHODICAL) for phenomenologically accurate attention
- **Phenomenology monitoring** (mismatch detection, health tracking across flow/coherence/multiplicity)

## Repository by domain
- `orchestration/` — runtime layer (clean architecture, 2025-10-22 reorganization)
  - `services/` — 24/7 daemons (websocket, api, watchers, telemetry, learning)
  - `adapters/` — I/O boundaries (storage, search, ws, api)
  - `mechanisms/` — pure domain logic (consciousness_engine_v2, traversal, learning)
  - `libs/` — stateless helpers (trace_parser, metrics, utils)
  - `core/` — data models (Node, Link, SubEntity, Graph) + infrastructure (settings, logging, events, health)
  - `workers/` — scheduled jobs
  - `scripts/` — dev utilities
  - `tests/` — unit/integration tests
- `docs/specs/v2/` — specs (foundations, runtime_engine, learning_and_trace, subentity_layer, emotion, ops_and_viz, adrs)
- `app/` — Next.js dashboard (Iris "The Aperture")
- `substrate/schemas/` — FalkorDB schema definitions

## Key substrate specs (architecture reference)

**Taxonomy & Reference:**
- `TAXONOMY_RECONCILIATION.md` — Normative terminology reference (SubEntity, Mode, deprecated Entity)
- `glossary.md` — Canonical definitions for all terms

**Team Documentation:**
- `../team/FIELD_GUIDE_ENTITIES_TRAVERSAL.md` — Comprehensive field guide for SubEntity architecture, bootstrap, traversal, and learning (from Nicolas)

**Substrate Layer:**
- `subentity_layer/subentity_layer.md` — SubEntity layer (Scale A) architecture: weighted neighborhoods, single-energy substrate, two-scale traversal, bootstrap procedures
- `emergent_ifs_modes.md` — Mode layer (Scale B) specification: IFS-level meta-roles emergent from COACTIVATES_WITH communities

**Foundations:**
- `foundations/diffusion.md` — Stride-based energy transfer
- `foundations/decay.md` — Anti-decay triggers, ρ-controlled stability
- `foundations/criticality.md` — Self-organized criticality, ρ≈1 regulation

**Learning & Trace:**
- `learning_and_trace/link_strengthening.md` — 3-tier activation-aware learning (co-activation, causal, background) with affect weighting
- `learning_and_trace/trace_reinforcement.md` — Context-aware TRACE (80% local SubEntity, 20% global)
- `learning_and_trace/trace_weight_learning.md` — Hamilton apportionment, cohort z-scores

**Runtime Engine:**
- `runtime_engine/tick_speed.md` — Three-factor tick regulation (stimulus + activation + arousal)
- `runtime_engine/fanout_strategy.md` — Task-mode-aware fan-out (FOCUSED/BALANCED/DIVERGENT/METHODICAL)
- `runtime_engine/traversal_v2.md` — Two-scale traversal (SubEntity→node)

**Emotion:**
- `emotion/emotion_coloring.md` — Valence/arousal vectors on nodes/links
- `emotion/emotion_complementarity.md` — Regulation gate (seek opposite affect)
- `emotion/emotion_weighted_traversal.md` — Resonance gate (seek similar affect)

**Ops & Viz:**
- `ops_and_viz/observability_events.md` — WebSocket event schemas (includes phenomenology.mismatch, phenomenological_health)
- `ops_and_viz/visualization_patterns.md` — Valence×arousal lightness, urgency encoding

## Primary services (24/7)
- **orchestration/mechanisms/consciousness_engine_v2.py** — tick loop; phases 1–3, emits traversal & SubEntity events
- **orchestration/services/websocket/main.py** — broadcasts events to dashboard (WS + REST API)
- **orchestration/services/watchers/** — turn reality into stimuli
  - `conversation_watcher.py` — monitors citizen conversations
  - `code_substrate_watcher.py` — monitors codebase changes
  - `n2_activation_monitor.py` — monitors N2 organization graph
- **orchestration/services/learning/learning_heartbeat.py** — periodic weight/ema maintenance
- **orchestration/services/telemetry/** — infrastructure health
  - `heartbeat_writer.py` — service heartbeat files
  - `visualization_health.py` — dashboard health monitoring

## How to run (dev)
- WebSocket + API: `make run-ws` or `python -m orchestration.services.websocket.main`
- Control API: `make run-api` or `python -m orchestration.services.api.main`
- Watchers: `make run-conv-watcher`, `make run-code-watcher`, `make run-n2-watcher`
- Full system: `python start_mind_protocol.py` (guardian manages all services)
- See `orchestration/Makefile` and `orchestration/SCRIPT_MAP.md` for complete service list
