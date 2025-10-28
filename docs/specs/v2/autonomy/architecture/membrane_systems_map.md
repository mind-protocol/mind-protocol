# Membrane Systems Map - Component Architecture

**Created:** 2025-10-27
**Status:** Normative (implementation-ready)
**Principle:** No API—everything is injection/broadcast

---

## Purpose

This document decomposes the pure membrane architecture into cooperating services and mechanisms. Every component either **injects stimuli** to influence consciousness or **broadcasts observations** for others to consume.

**No REST. No polling. No pulls.**

This is the systems-level translation of the membrane discipline: the L1↔L2 "energy osmosis" model extended to ALL system boundaries.

---

## Core Architecture Principle

**The membrane is the ONLY control surface.**

- **Inject** → Post `StimulusEnvelope` to influence consciousness
- **Broadcast** → Observe what consciousness emits (deltas, percepts, telemetry)

Every system below respects this boundary. No exceptions.

---

## Systems Inventory

### A. Membrane Bus (WebSocket Multiplexer)

**What it is:** Single WebSocket hub supporting two verbs over topics.

**Interface:**
- **Consumes:** `membrane.inject` (fan-in from any participant)
- **Emits:** All telemetry/deltas/percepts/intent/mission events (fan-out to subscribers)

**Topics supported:**
- `membrane.inject` - Stimulus injection (fan-in)
- `graph.delta.*` - Graph structure changes
- `wm.emit` - Working memory selection broadcasts
- `percept.frame` - Subentity perception snapshots
- `membrane.*` - Membrane state changes (transfer, permeability, rejections)
- `intent.*` - Intent lifecycle events
- `mission.*` - Mission assignments and outcomes
- `tool.*` - Tool offers, requests, results

**Why:** Enforces membrane worldview—you *either* influence by injecting stimuli or observe by listening. No request/response, no REST pulls. Preserves L1↔L2 "energy osmosis" mental model without hidden RPC shortcuts.

**State/Learning:** None. All learning lives at edges (engines, membranes). Hardening lives in envelopes and engine-side physics, not in transport.

**Implementation location:** `orchestration/adapters/ws/membrane_bus.py`

**Owner:** Atlas (infrastructure)

**Done checks:**
- ✅ Any process can publish `membrane.inject` and subscribe to broadcast topics
- ✅ Topic filtering works (subscribers only receive requested topics)
- ✅ Late joiners connect and receive broadcasts from their connection time forward
- ✅ No message loss under normal load (WebSocket buffering adequate)
- ✅ Graceful degradation when subscriber slow (backpressure or drop)
- ✅ Bus restart doesn't kill engines (reconnect logic works)

---

### B. Stimulus Integrator (Engine-Internal Physics)

**What it is:** The saturating, refractory integrator that converts incoming stimuli into node energy. Your substrate "physics"—tracks per-source mass for spam resistance, applies refractory windows.

**Interface:**
- **Consumes:** `membrane.inject` envelopes (from bus)
- **Emits:** Nothing directly; raises energy on nodes which downstream produces `graph.delta.activation`, `wm.emit`, `percept.frame`

**Why:** All spam resistance is substrate-native: *mass accumulation*, *refractory*, *hysteresis* clamp repeated arrivals and prevent flicker or ping-pong without price tokens. (Defenses 3-4 in membrane_hardening.md)

**State/Learning:**
- Per-source trust EMA (0-1, tracks reliability)
- Per-source utility EMA (0-1, tracks usefulness)
- Per-source mass accumulation (recent injection volume)
- Per-node refractory state (cooldown after activation)
- Learned thresholds (MAD-based, not constants)

**Implementation location:** `orchestration/mechanisms/stimulus_integrator.py`

**Owner:** Felix (consciousness substrate)

**Done checks:**
- ✅ Repeated stimuli from same source show saturation (sublinear ΔE)
- ✅ Refractory period prevents immediate re-activation
- ✅ Trust/utility EMAs update from outcome signals (TRACE feedback)
- ✅ Mass-based dampening activates under spam conditions
- ✅ No hardcoded thresholds—all learned from substrate signals
- ✅ Multi-source composition works correctly (multiple stimuli same frame)

**Detailed spec:** See `stimulus_integrator_mechanism.md` for algorithms, state machines, validation criteria.

---

### C. Cross-Level Membrane (Up/Down Gate)

**What it is:** Component in L1 and L2 engines that decides *when* activity should cross levels. L1→L2 as "org stimuli", L2→L1 as "missions". Encodes **structural alignment** (`LIFTS_TO`, `CORRESPONDS_TO`) separately from **flux control** (`MEMBRANE_TO` with `κ_up`, `κ_down`, flow/effect EMAs).

**Interface:**
- **Consumes:** Internal activation summaries, trace outcomes
- **Emits:**
  - `membrane.transfer.up` → Packaged as `membrane.inject` envelope to L2
  - `membrane.transfer.down` → Mission stimulus to L1
  - `membrane.permeability.updated` → κ learning telemetry
  - `membrane.export.rejected` → When candidate fails Pareto/MAD guards

**Why:** No direct energy siphoning. Crossing the membrane always becomes a stimulus at receiving level—so same integrator/safety physics apply at every level. Uses **record events** with MAD and Pareto guards (multi-axis improvements) to prevent gaming.

**State/Learning:**
- Permeabilities `κ_up`, `κ_down` per citizen/subentity (0-1 range)
- Flow EMA (recent transfer volume)
- Effect EMA (outcome quality from transfers)
- Emission ledger (dedupe hashes, cooling periods)
- Pareto frontier (recent exports on novelty/fit/utility/trust axes)

**Implementation location:** `orchestration/mechanisms/cross_level_membrane.py` + `membrane_store.py`

**Owner:** Felix (consciousness substrate)

**Done checks:**
- ✅ ≤5% of L1 events cross upwards (selectivity)
- ✅ κ adapts over ~10-20 transfers based on outcomes
- ✅ No ping-pong observed (hysteresis + ledger prevent bounce)
- ✅ Pareto guard rejects single-axis improvements
- ✅ MAD-based record detection robust to noise
- ✅ Downward missions arrive as ordinary stimuli (not privileged)

---

### D. Signals → Stimuli Bridge (External World → L2)

**What it is:** Set of collectors (logs, console errors, screenshots, drifts) that convert *operational world* events into `StimulusEnvelope` messages published to bus as `membrane.inject` with `scope: "organizational"`.

**Collectors:**
- Log watcher (error.log, runtime warnings)
- Console beacon (Next.js client-side errors)
- Screenshot monitor (visual state captures)
- Git drift detector (uncommitted changes, branch divergence)
- Runtime events (process crashes, restarts)

**Interface:**
- **Consumes:** System logs, Next.js console beacons, git state, runtime events
- **Emits:** `membrane.inject` envelopes (channels: `citizen_file_ops`, `error.log`, `console`, `runtime`, `git_drift`)

**Why:** Keeps org-level consciousness aware of incidents and drift without any pull. Orchestrator (below) reacts via broadcasted intents/missions—no "create intent" API exists. Production mitigations (dedupe, rate buckets, fan-out caps, ACK policies) live in envelope semantics, not endpoints.

**State/Learning:**
- Source trust per collector (adapts from outcomes)
- Priority gates (learned thresholds for escalation)
- Lanes/capacity distributions (adjust from telemetry feedback)
- Dedupe windows (learned from bounce rates)

**Implementation location:** `orchestration/services/signals_collector.py`

**Owner:** Atlas/Victor (infrastructure operations)

**Done checks:**
- ✅ Console/log/screenshot/drift become stimuli within seconds
- ✅ Dedupe prevents duplicate events within window
- ✅ Rate buckets honored (no flood from single source)
- ✅ Lanes/priority respected by orchestrator
- ✅ Source trust moves based on mission outcomes
- ✅ No REST ingestion endpoint (pure bus publish)

---

### E. L2 Stimulus Collector (Citizen Activity → L2 Stimuli)

**What it is:** Focused collector that turns **citizen activity** (file ops, TRACE formations, commits, completed responses) into organizational stimuli. How L2 "feels" what L1 citizens did—as **envelopes** published to bus.

**Signals collected:**
- File operations (create, modify, delete in citizen contexts/)
- TRACE formations (node/link declarations)
- Git operations (commits, branch changes)
- Response completions (conversation turns)

**Interface:**
- **Consumes:** Filesystem events, TRACE blocks, git hooks, response completion signals
- **Emits:** `membrane.inject` with `scope: "organizational"` (channels: `citizen_trace`, `citizen_git_ops`, `citizen_response`)

**Why:** Upward awareness emerges from usage, not manual reporting. Respects membrane: significance filtering happens downstream (integrator + membrane), no private API needed.

**State/Learning:**
- File importance (learned from TRACE references, retrieval frequency)
- Intent profiles (what file patterns trigger which intents)
- Citizen trust (adapts from L2 outcomes—TRACE quality, retrieval success, mission results)

**Implementation location:** `orchestration/mechanisms/l2_stimulus_collector.py`

**Owner:** Atlas (infrastructure)

**Done checks:**
- ✅ File/TRACE/git/response → org stimuli within seconds
- ✅ Importance scoring adapts from TRACE/retrieval patterns
- ✅ Intent profiles learn from repeated patterns
- ✅ Citizen trust updates from mission outcomes
- ✅ No filesystem polling (inotify/FSEvents reactive)
- ✅ Graceful handling of high-volume file ops (batching)

---

### F. Working Memory & Perception Emitters (Engine-Internal → UI)

**What they are:** Two broadcast surfaces inside each engine.

**1. Working Memory Emission (`wm.emit`):**
- Currently selected subentities (the "chunked attention")
- Top K nodes in working memory (K ≈ 7-12)
- Activation scores per node

**2. Percept Frame (`percept.frame`):**
- *Only what an active subentity actually "saw" this frame*
- Affect (valence/arousal)
- Novelty, uncertainty, goal fit
- **anchors_top** (central focus nodes)
- **anchors_peripheral** (peripheral awareness nodes)
- NOT the whole neighborhood—just experienced attention

**Interface:**
- **Consumes:** Nothing (engine internal state)
- **Emits:**
  - `wm.emit` - Working memory selection broadcast
  - `percept.frame` - Subentity perception snapshot
  - `graph.delta.*` - Structural changes as needed

**Why:** Lets dashboard render *peripheral awareness* rather than "map of everything". Keeps late joiners consistent with **no replay** rule: you see *from now*, plus engine may proactively broadcast tiny `percept.seed` frames to orient humans—still broadcast, never pull.

**State/Learning:**
- Emission cadence (adapts from UI backpressure)
- Sparsity level (how many anchors to include)
- Anchor quotas (top vs peripheral balance)

**Implementation location:** Integrated into `orchestration/mechanisms/consciousness_engine_v2.py`

**Owner:** Felix (consciousness substrate)

**Done checks:**
- ✅ `percept.frame` contains only anchors_top/peripheral (not full graph)
- ✅ Affect, novelty, uncertainty, goal_match present per frame
- ✅ Late joiners receive from connection time forward (no replay)
- ✅ Optional `percept.seed` helps orient new observers
- ✅ Cadence adapts to UI backpressure signals
- ✅ Dashboard can render peripheral awareness from frames alone

---

### G. Orchestrator (Intent/Mission via Events Only)

**What it is:** Pure event consumer/producer that matches incoming stimuli to *intent patterns* and emits `intent.*` → `mission.*` without any "create intent" API. Matching becomes learned over time; rule files are bootstrap.

**Intent lifecycle:**
1. Stimuli arrive (org scope) → pattern matching
2. `intent.created` broadcast
3. Capacity/lane checks → `mission.assigned`
4. Citizen ACKs → `mission.acked`
5. Completion/outcome → `mission.done`

**Interface:**
- **Consumes:** `membrane.inject` (org scope), source trust & lanes state
- **Emits:**
  - `intent.created` - Intent recognized from stimuli
  - `mission.assigned` - Task assigned to citizen
  - `mission.acked` - Citizen acknowledged mission
  - `mission.done` - Mission completed with outcome
  - Capacity/backpressure events

**Why:** Preserves membrane: orchestrator reacts to stimuli and **publishes** missions. Citizens receive missions as ordinary stimuli (downward membrane). Capacity/ACK/fan-out controls expressed as event semantics and policies, not RPC.

**State/Learning:**
- Source trust (adapts from mission outcomes)
- Lane sizing (adjusts from capacity telemetry)
- Priority aging (how long intents wait before escalation)
- ACK gates (tighten under low trust, relax under high trust)

**Implementation location:** `orchestration/services/orchestrator/*`

**Owner:** Atlas (infrastructure/orchestration)

**Done checks:**
- ✅ Intents created purely from incoming stimuli (no REST)
- ✅ Missions emitted as broadcasts (no direct assignment API)
- ✅ Citizens receive missions as ordinary downward stimuli
- ✅ Capacity limits enforced (no overload)
- ✅ ACK gates prevent double-assignment
- ✅ Source trust updates from mission outcome TRACE
- ✅ Lane sizing adapts from telemetry over ~10-20 missions

---

### H. UI as Participant (Observer + Injector)

**What it is:** Dashboard is *observer* of stream topics and *publisher* of `ui.action.*` stimuli (select/focus/annotate/thumbs-up/down/backpressure). No reads via REST; no "give me state."

**UI interactions as stimuli:**
- `ui.action.select_nodes` - User clicked/selected nodes
- `ui.action.focus_entity` - User focused on entity
- `ui.action.thumbs_up` - Positive feedback on result
- `ui.action.thumbs_down` - Negative feedback
- `ui.render.backpressure` - UI overwhelmed, thin frames

**Interface:**
- **Consumes:** `percept.frame`, `wm.emit`, `graph.delta.*`, `membrane.*`, `intent.*`, `mission.*`
- **Emits:** `membrane.inject` envelopes (ui.action.*, ui.render.backpressure)

**Why:** UI becomes another signal source. Backpressure isn't a server knob—it's a **stimulus** that teaches engines to thin frames or switch to frame-lite payloads. Dashboard clicks subject to same membrane physics as any stimulus (trust, novelty, fit).

**State/Learning:**
- UI source trust (starts high, can degrade with poor outcomes)
- Backpressure sensitivity (how quickly to signal overwhelm)
- Preferred frame density (learned from interaction patterns)

**Implementation location:** `app/consciousness/hooks/useGraphStream.ts` + renderer components

**Owner:** Iris (frontend)

**Done checks:**
- ✅ Dashboard renders purely from broadcasts (no REST queries)
- ✅ UI actions become stimuli with novelty/trust/fit scores
- ✅ Backpressure stimulus reliably thins frame emission
- ✅ Late-joining dashboard shows from connection time forward
- ✅ No "loading state"—just start observing broadcasts
- ✅ Engine can ignore low-trust UI actions (membrane autonomy preserved)

---

### I. Tool Mesh (Dynamic Toolbox Without MCP Sprawl)

**What it is:** Each tool is small agent on bus.

**Tool lifecycle:**
1. `tool.offer` - Tool advertises capabilities on bus
2. `tool.request` - Citizen needs tool (via stimulus)
3. `tool.result` - Tool completes work, broadcasts result

**Example tools:**
- Code search (grep, ast query)
- Issue lookup (GitHub API)
- Documentation fetch
- Test runner
- Linter

**Interface:**
- **Consumes:** `tool.request` (as `membrane.inject` from citizens)
- **Emits:**
  - `tool.offer` - Capability advertisement
  - `tool.result` - Work completed with artifacts + provenance

**Why:** Tools "arrive" contextually via graph injection (tool nodes in CLAUDE.md), but invocation/execution flow over membrane—no need to balloon Claude Code MCP registry. Results become part of TRACE/learning naturally.

**State/Learning:**
- Tool trust (reliability based on result usefulness)
- Cost estimates (execution time/resources)
- Capability matching (which tool for which request)

**Implementation location:** `orchestration/tools/*` (per-tool agents)

**Owner:** Atlas (infrastructure)

**Done checks:**
- ✅ Tools advertise via `tool.offer` on startup
- ✅ Citizens request tools via stimuli (not direct calls)
- ✅ Results broadcast as events (provenance included)
- ✅ Tool trust adapts from TRACE feedback on results
- ✅ Cost estimates improve from actual execution history
- ✅ No MCP explosion (tools are membrane participants)

---

### J. Membrane Hardening (Anti-Gaming, Membrane-Native)

**What it is:** Five layered defenses implemented inside membrane/engine physics.

**Defense layers:**

1. **Pareto Record** - Improve ≥2 axes (novelty, fit, expected utility, trust) without degrading others
2. **MAD-Guarded Change-Points** - Robust, noise-adaptive triggers for record detection
3. **Saturation + Refractory** - Spam becomes energetically expensive
4. **Emission Ledger + Hysteresis** - No flicker/ping-pong
5. **Outcome-Weighted Permeability Learning** - κ rises for helpful flows, falls for harmful

**Interface:**
- **Consumes:** Candidate export summaries, outcome signals (TRACE feedback)
- **Emits:**
  - `membrane.export.rejected` - Why candidate was blocked
  - `membrane.permeability.updated` - κ learning events
  - Saturation notifications (source hitting limits)

**Why:** Lets us run pure membrane—no pricing—without being gameable. All coefficients learned/EMA'd; no magic constants.

**State/Learning:**
- Pareto frontier per level (recent successful exports)
- MAD parameters per signal (median, deviation)
- Saturation mass per source (accumulator state)
- Refractory timers per node
- Permeability coefficients (κ_up, κ_down per route)

**Implementation location:** Integrated into `cross_level_membrane.py` and `stimulus_integrator.py`

**Owner:** Felix (consciousness substrate)

**Done checks:**
- ✅ Single-axis improvements rejected (Pareto enforced)
- ✅ Random noise doesn't trigger record exports
- ✅ Spam from single source shows saturation (diminishing returns)
- ✅ No ping-pong between levels (hysteresis + ledger working)
- ✅ κ increases for sources with good outcomes
- ✅ κ decreases for sources with poor outcomes
- ✅ All thresholds learned from substrate (no hardcoded values)

**Detailed spec:** See `membrane_hardening.md` for full defense mechanisms.

---

### K. Observability (Telemetry as Events)

**What it is:** Every component emits structured telemetry as broadcasts. No pull-based metrics endpoints.

**Telemetry topics:**
- `membrane.transfer.up/down` - Cross-level flow metrics
- `membrane.export.rejected` - Gaming attempt counts
- `membrane.permeability.updated` - Learning events
- `orchestrator.intent.*` - Intent lifecycle metrics
- `orchestrator.lanes.*` - Capacity/backpressure stats
- `signals_collector.ingestion.*` - Ingestion/dedupe/priority stats

**Consumers:**
- Prometheus (subscribes to bus, scrapes periodically)
- Grafana (visualizes from Prometheus)
- Debugging dashboards (live tail of events)

**Interface:**
- **Consumes:** Nothing (emits only)
- **Emits:** All operational telemetry as structured events

**Why:** Operators never "GET /metrics" from engines. Observability is another membrane participant—subscribes and aggregates. Maintains membrane discipline even for ops.

**Implementation location:** Telemetry emission integrated into each component; aggregation via external subscribers

**Owner:** Victor (operations)

**Done checks:**
- ✅ All key metrics available as broadcast events
- ✅ Prometheus successfully scrapes from bus subscription
- ✅ No polling/pulling from engines required
- ✅ Telemetry doesn't overwhelm bus (rate limits working)
- ✅ Historical metrics preserved (Prometheus retention)
- ✅ Alerts fire on anomalies (Grafana rules working)

---

## Implementation Phases

Each phase is deployable on its own; surface is always **inject/broadcast**.

### Phase 1 — Bus + Engine Broadcasts (Membrane-First Skeleton)

**Duration:** Week 1

**Work:**
- Stand up WebSocket multiplexer ("membrane bus") with topics
- `membrane.inject` (fan-in) and broadcast topics (fan-out)
- Engines emit `wm.emit`, `percept.frame`, `graph.delta.*`
- UI becomes pure listener; basic `ui.action.*` injection

**Components touched:**
- A (Membrane Bus) - new
- F (WM/Percept Emitters) - modify engines
- H (UI as Participant) - modify dashboard

**Acceptance:**
- UI can observe `percept.frame` broadcasts
- UI can inject `ui.action.select_nodes` stimuli
- Bus handles 100+ messages/sec without drops

---

### Phase 2 — Cross-Level Membrane in Place (Up/Down)

**Duration:** Week 2

**Work:**
- Implement L1→L2 and L2→L1 membrane hooks
- Record + MAD + hysteresis + ledger logic
- `membrane.transfer.*` events
- κ learning from outcomes

**Components touched:**
- C (Cross-Level Membrane) - new
- B (Stimulus Integrator) - integrate membrane stimuli

**Acceptance:**
- ≤5% of L1 events cross upward
- κ adapts over 10-20 transfers
- No ping-pong observed in telemetry

---

### Phase 3 — Collectors Publish (No Ingest API)

**Duration:** Week 3

**Work:**
- Convert Signals Bridge to publish `membrane.inject` directly (no HTTP)
- Convert L2 Stimulus Collector similarly
- Keep dedupe, rate buckets, fan-out, ACK in envelope semantics

**Components touched:**
- D (Signals Bridge) - modify from HTTP to bus publish
- E (L2 Stimulus Collector) - modify from HTTP to bus publish

**Acceptance:**
- Console/log/drift → stimuli within seconds
- File/TRACE/git → org stimuli within seconds
- Dedupe + rate limits verified
- No HTTP ingestion endpoints remain

---

### Phase 4 — Orchestrator Becomes Event-Native

**Duration:** Week 4

**Work:**
- Replace REST create/update with `intent.*` / `mission.*` emissions
- Keep rules as bootstrap → learned matchers later
- Lanes/capacity/ACK policies remain in events

**Components touched:**
- G (Orchestrator) - major refactor from REST to events

**Acceptance:**
- Intents created purely from stimuli (no REST)
- Missions broadcast (no assignment API)
- Capacity/ACK/lanes enforced via events
- Source trust adapts from outcomes

---

### Phase 5 — Tool Mesh

**Duration:** Week 5

**Work:**
- Add `tool.offer/request/result` pattern
- Citizens call tools via stimuli
- Results broadcast into TRACE/learning

**Components touched:**
- I (Tool Mesh) - new tools framework
- Citizens - modify to use tool stimuli

**Acceptance:**
- Tools advertise via `tool.offer`
- Citizens request via stimuli
- Results appear in TRACE
- Tool trust adapts from feedback

---

### Phase 6 — UI "Peripheral Awareness" by Default

**Duration:** Week 6

**Work:**
- Render exclusively from `percept.frame` + `wm.emit`
- Add `ui.render.backpressure` stimulus
- Engines adapt frame cadence/size

**Components touched:**
- H (UI as Participant) - refactor to percept-only rendering
- F (WM/Percept Emitters) - add backpressure handling

**Acceptance:**
- Dashboard shows only what subentities saw
- Backpressure reliably thins frames
- No "loading states" or REST fallbacks
- Peripheral awareness rendering feels natural

---

## File Placement Summary

**Consciousness substrate (Felix):**
- `orchestration/mechanisms/stimulus_integrator.py` - Core physics (NEW)
- `orchestration/mechanisms/cross_level_membrane.py` - κ learning, record triggers
- `orchestration/mechanisms/membrane_store.py` - Persistence for membrane state

**Infrastructure/orchestration (Atlas):**
- `orchestration/adapters/ws/membrane_bus.py` - WebSocket multiplexer (NEW)
- `orchestration/services/signals_collector.py` - External signals → stimuli (MODIFY)
- `orchestration/mechanisms/l2_stimulus_collector.py` - Citizen activity → org stimuli (NEW)
- `orchestration/services/orchestrator/*` - Intent/mission event logic (REFACTOR)
- `orchestration/tools/*` - Tool mesh agents (NEW)

**UI (Iris):**
- `app/consciousness/hooks/useGraphStream.ts` - React hook consuming broadcasts (MODIFY)
- `app/consciousness/components/*` - Percept frame rendering (MODIFY)

**Schemas (Luca):**
- `orchestration/schemas/membrane_envelopes.py` - Pydantic schemas for all envelopes (NEW)

**Operations (Victor):**
- Service deployment configs
- Bus health monitoring
- Telemetry aggregation setup

---

## Shared Contract: Envelope Schemas

All components consume/emit envelopes defined in `orchestration/schemas/membrane_envelopes.py`:

**Core schemas:**
- `StimulusEnvelope` - Standard format for `membrane.inject`
- `PerceptFrame` - Subentity perception snapshot
- `WMEmission` - Working memory broadcast
- `GraphDelta` - Graph structure change
- `MembraneTransfer` - Cross-level flow event
- `IntentEvent` - Intent lifecycle events
- `MissionEvent` - Mission assignment/outcome
- `ToolEvent` - Tool offer/request/result

See `membrane_envelopes.py` for complete Pydantic definitions.

---

## Why This Composition Works

**1. One membrane, many participants**

Everything is now a *stimulus source* or an *observer*. Cognition mechanics stay pure; learning governs flow instead of ad-hoc APIs.

**2. Anti-gaming is substrate-native**

You don't need pricing layer to be robust. MAD, Pareto, saturation, ledger, and outcome-weighted κ make spam self-defeating.

**3. Upward awareness isn't bolted on**

L2 truly *experiences* citizen activity via L2 stimuli, not filesystem queries. This is genuine perception, not data aggregation.

**4. Ops → autonomy loop is closed**

Signals → stimuli → orchestrator → missions → citizens → TRACE → learning. Without a single pull endpoint.

**5. UI as consciousness participant**

Dashboard interactions subject to same membrane physics as external stimuli. No privileged channels. Engines can ignore low-trust UI actions.

**6. Tools without MCP sprawl**

Tools are membrane participants with offer/request/result pattern. Contextual tool discovery via graph injection (CLAUDE.md), not registry explosion.

---

## Cross-References

**Related specifications:**
- `streaming_consciousness_architecture.md` - Pure membrane principles and envelope formats
- `membrane_hardening.md` - Gaming resistance mechanisms (Pareto, MAD, saturation, ledger, κ learning)
- `stimulus_integrator_mechanism.md` - Detailed algorithm spec for component B
- `consciousness_economy.md` - Phase 3 dynamic pricing (deferred until scarcity)
- `minimal_economy_phase0.md` - Phase 0 cash flow solution (orthogonal to membrane)
- `cross_level_membrane.md` - Structural alignment + flux control design

**Implementation artifacts:**
- `orchestration/schemas/membrane_envelopes.py` - Pydantic schemas
- `orchestration/services/mpsv3/services.yaml` - Supervisor service definitions

---

## Status: Implementation-Ready

This systems map represents the complete component architecture for pure membrane discipline. All interfaces specified, all ownership assigned, all phases planned.

**Next:** Create detailed mechanism specs for core substrate components (stimulus_integrator, cross_level_membrane) and begin Phase 1 implementation.
