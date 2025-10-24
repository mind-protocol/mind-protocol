# Executive Summary — L2 Citizen Autonomy

## Goal
Operationalize **citizen autonomy on Layer 2 (L2)**: decisions and actions emerge from graph energy dynamics (activation, fanout, decay, diffusion) under guardrails (quotas, thresholds, tick scheduling, safety telemetry), with clear interfaces to UI/API and persistence.

## Scope (citizens/components)
- **Citizens:** ada, iris, luca, felix, victor (+ collective).
- **Core runtime:** traversal_v2, fanout_strategy, tick_speed, decay/diffusion, quotas, thresholds, multi_energy, weight_learning_v2.
- **Persistence & IO:** storage adapters (engine_registry/insertion/retrieval), websocket emitters, API routes in pp/api/consciousness/*.
- **Viz/ops:** AutonomyIndicator, TaskModeInfluencePanel, Health/Status panels.

## Invariants (must hold)
1. **Single energy per node** (ADR-0003); no hidden side-channels.
2. **Causality:** every activation is traceable (events + forensic trail).
3. **Safety:** quotas + thresholds bound fanout per tick and per citizen.
4. **Tick determinism:** L2 decisions derive from state at the start of tick.
5. **Decay/Diffusion monotonicity:** energy never increases without input.
6. **Bitemporal integrity:** write-time vs event-time preserved where used.
7. **Observability:** emit minimal, structured telemetry for each tick.

## Primary control loops
- **Traversal loop:** entity_activation ? fanout_strategy ? graph updates.
- **Timing loop:** 	ick_speed adjusts frequency under load/health.
- **Safety loop:** quotas + thresholds cap breadth/energy per tick.
- **Learning loop:** weight_learning_v2 updates link weights from traces.
- **Health loop:** coherence_metric + visualization_health gate actions.

Data flow (happy path):
stimulus_injection ? scheduler/tick ? traversal_v2 ? quotas/thresholds ? multi_energy/decay/diffusion ? updates + telemetry ? websocket emitters ? UI.

## L2 specifics (design stance)
- **Energy flow is first-class:** Layer 2 decisions are *functions of* energy distributions, not ad-hoc heuristics.
- **Fanout bounded + prioritized:** direction priors + valence gate + quotas.
- **Autonomy surfaces:** task-mode influence + autonomy indicator + citizen monitor (UI) reflect internal energy dynamics, not static flags.

## Interfaces (we will wire against)
- API: pp/api/consciousness/system-status, oundations/status, identity-multiplicity/status, ffective-telemetry/metrics, multi-pattern/recent-events.
- UI: AutonomyIndicator.tsx, TaskModeInfluencePanel.tsx, ConsciousnessHealthDashboard.tsx, GraphCanvas.tsx.
- WS: 	raversal_event_emitter, weight_learning_emitter.

## Open decisions
1. **Quota policy:** per-tick vs sliding window; per-citizen vs global pool.
2. **Tick scaling:** boundaries and backoff for 	ick_speed under saturation.
3. **Learning cadence:** online every tick vs batched after N events.
4. **Criticality coupling:** when to elevate activation based on criticality.
5. **Autonomy thresholds:** exact mapping ? UI indicator levels.
6. **Persistence SLAs:** sync vs async writes for action-critical edges.

## Success criteria
- Unit/integration tests green for traversal, tick, quotas, multi_energy.
- Coherence metric non-degrading across N ticks during stress tests.
- UI autonomy indicator tracks internal decision boundaries within ±1 tick.
- No safety violations (quota/threshold) in long-running sessions.

