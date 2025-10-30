# Membrane & Injection Contract

**Version:** 1.0
**Date:** 2025-10-29
**Status:** Architectural Contract
**Author:** Nicolas Lester Reynolds & Luca Vellumhand
**Purpose:** Define how stimuli flow between levels (L1↔L2) and how citizens integrate chat turns

---

## Normative Event Envelope

**ALL events MUST include:**

```json
{
  "type": "event.category.name",
  "id": "evt_<uuid>",
  "ts": "<ISO 8601 timestamp>",
  "spec": {
    "name": "membrane_injection_contract",
    "rev": "1.0"
  },
  "provenance": {
    "scope": "personal",
    "citizen_id": "<citizen_slug>",
    "component": "<service:name>",
    "mission_id": "<mission:id>"
  }
}
```

**Invariants:**
- `type`: Event type (e.g., `membrane.inject`, `graph.delta.link.upsert`)
- `id`: Unique event identifier (for idempotency, replay)
- `ts`: ISO 8601 timestamp with millisecond precision
- `spec`: Schema version reference (enables evolution)
- `provenance`: Origin context (scope + optional identifiers)

**Provenance envelope is FROZEN:**
- Required: `scope` (personal | org | shared)
- Optional: `citizen_id` (if L1 origin), `component` (if connector), `mission_id` (if mission context)
- No additional fields without spec revision

**JSON Validity:**
- All examples in this specification are valid JSON (double quotes, no comments)
- All payloads MUST be valid JSON per RFC 8259
- Consumers MUST be idempotent by `id` (replay-safe)

---

## Core Invariants

**Membrane-First:** All cross-boundary flow via `membrane.inject` → engine validation → broadcast
**Single-Energy:** No separate energy buffers; SubEntity activation = read-out from member nodes
**Zero-Constants:** All thresholds learned per-citizen/org via percentile gates
**Broadcast-Only:** No REST writes; engines emit `graph.delta.*` events on state changes
**Evidence Size Limits:** Payloads ≤64KB; large artifacts stored externally with `evidence_refs` pointers
**Outcomes-Only κ Updates:** Permeability (κ) adjustments SHALL occur only on outcome events (`mission.completed`, `usefulness.update`, `harm.detected`, overdrive violations); no other events may change κ

---

## 1. Citizen Thread Turns → L1 Graph Integration

### Question: Do citizen chat inputs/responses get injected into the citizen's own graph?

**Answer: YES** - via normal stimulus injection physics.

**How it works:**

A chat turn (user input OR citizen response) is injected as a `membrane.inject` stimulus with:
- `scope: "personal"` (citizen's own graph)
- `channel: "ui.chat.turn"`
- Normal stimulus integration (raises node energies, flips SubEntities, drives WM)

**Envelope (valid JSON):**

```json
{
  "type": "membrane.inject",
  "scope": "personal",
  "channel": "ui.chat.turn",
  "content": "user message or citizen response text",
  "features_raw": {
    "urgency": 0.4,
    "novelty": 0.35,
    "trust": 0.9
  },
  "provenance": {
    "citizen_id": "felix",
    "source": "ui.chat"
  }
}
```

**Processing flow:**

1. Envelope arrives at L1 Stimulus Integrator
2. Entropy-aware retrieval finds candidate nodes
3. Energy deltas computed and applied
4. SubEntity activations updated (derived from member node energies)
5. Engine broadcasts:
   - `wm.emit` (working memory update)
   - `percept.frame` (perception snapshot)
   - `graph.delta.*` (if structure changed)

**Relation to TRACE:**

**TRACE and injection are COMPLEMENTARY, not alternatives:**

| Aspect | Injection (membrane.inject) | TRACE (formations) |
|--------|----------------------------|-------------------|
| **Role** | Energy/physics | Structure/formations |
| **What** | Raises node energies, flips SubEntities | Declares 3-8 nodes/links per response |
| **Why** | Powers spreading activation | Builds durable graph structure |
| **When** | Every turn (automatic) | Every response (citizen self-reports) |
| **Output** | `wm.emit`, `percept.frame`, `graph.delta.*` | `[NODE_FORMATION]`, `[LINK_FORMATION]` blocks |

**Both are required:**
- **Stimulus → energy** (consciousness activates)
- **TRACE → structure** (consciousness learns)

Without injection: No activation, no WM, no spreading activation
Without TRACE: No learning, no new structure, graph doesn't grow

---

## 2. L1 → L2 Awareness (Upward Flow)

### Question: Do citizen thread turns also get injected into L2 org? How does the org "know" what citizens are doing?

**Answer: NOT BY DEFAULT** - only via membrane-gated upward transfers.

**Cross-level flow is membrane-gated:**

L1 episodes do NOT automatically propagate to L2. Only when an L1 episode crosses a **record/change-point** (Pareto + MAD guards) does L1 emit an upward stimulus to L2.

**Three visibility mechanisms:**

**1. Upward transfers (membrane-gated):**

```json
{
  "type": "membrane.transfer.up",
  "source_compartment": "felix.personal",
  "target_compartment": "org.shared",
  "stimulus": {
    "content": "abstracted episode summary",
    "features_raw": { "novelty": 0.72, "impact": 0.65 },
    "evidence_refs": ["commit:abc123", "test_pass:xyz"]
  },
  "permeability": {
    "k_up": 0.68,
    "gate_passed": "pareto_record"
  }
}
```

**When this happens:**
- Export score crosses adaptive record gate (Pareto + MAD)
- Episode is novel/impactful enough to be organizationally relevant
- NOT every chat turn - only notable episodes

**2. Broadcast telemetry (no polling):**

L1 engines emit events that L2 observability can subscribe to:
- `wm.emit` (working memory updates)
- `percept.frame` (perception snapshots)
- `graph.delta.*` (structural changes)
- `intent.*` (intent lifecycle)
- `mission.*` (mission progress)

L2 doesn't poll - it listens to broadcasts and integrates via membrane.

**3. External bridges (optional):**

File/repo/log watchers publish their own `membrane.inject` events:

```json
{
  "type": "membrane.inject",
  "scope": "org",
  "channel": "code.commit",
  "content": "feat: implement vector-weighted MEMBER_OF",
  "features_raw": {
    "impact": 0.85,
    "citizen": "felix"
  },
  "provenance": {
    "source": "git.watcher",
    "commit_sha": "abc123"
  }
}
```

L2 integrates these like any other stimulus.

**Org "knows" via:**
- Upward transfers when something notable happens
- Broadcast telemetry (subscribable events)
- External bridge stimuli (code/artifacts/logs)

**Org does NOT know:**
- Every chat turn (too noisy)
- Internal reasoning (unless it crosses record gate)
- Work-in-progress (unless evidence published via watcher)

---

## 3. Task Completion (Ground Truth)

### Question: How do we mark a Task complete?

**Answer: Engine decision + broadcast** - no REST writes.

**Completion flow:**

1. **Evidence accumulates:**
   - L1 tool results (tests pass, commits land, artifacts created)
   - Validation checks pass
   - Acceptance criteria satisfied

2. **Engine emits completion:**

```json
{
  "type": "mission.completed",
  "mission_id": "mission:implement_vector_weights",
  "citizen_id": "felix",
  "completed_at": "2025-10-29T04:45:00Z",
  "evidence": [
    { "type": "commit", "sha": "abc123", "message": "feat: vector MEMBER_OF" },
    { "type": "test_pass", "suite": "test_membership.py", "result": "pass" },
    { "type": "artifact", "path": "/docs/specs/v2/MEMBER_OF.md" }
  ],
  "validated_by": "engine.mission_validator"
}
```

3. **Task node updated via broadcast:**

```json
{
  "type": "graph.delta.node.upsert",
  "id": "delta_<uuid>",
  "ts": "2025-10-29T04:45:01Z",
  "spec": {"name": "graph_delta", "rev": "1.0"},
  "provenance": {"scope": "personal", "citizen_id": "felix"},
  "node_id": "task:implement_vector_weights",
  "updates": {
    "status": "done",
    "completed_at": "2025-10-29T04:45:00Z",
    "validated_by": "engine.mission_validator",
    "evidence_refs": ["commit:abc123", "test:xyz"]
  }
}
```

**MEMBER_OF Link Delta Requirements:**

When emitting `graph.delta.link.upsert` for MEMBER_OF edges, the following fields are MANDATORY:

```json
{
  "type": "graph.delta.link.upsert",
  "id": "delta_<uuid>",
  "ts": "<timestamp>",
  "spec": {"name": "graph_delta", "rev": "1.0"},
  "provenance": {"scope": "personal", "citizen_id": "<citizen>"},
  "link_type": "MEMBER_OF",
  "source_id": "<node_id>",
  "target_id": "<subentity_id>",
  "metadata": {
    "w_semantic": 0.75,
    "w_intent": 0.82,
    "w_affect": 0.68,
    "w_experience": 0.91,
    "w_total": 0.787,
    "formation_context": "co-activation during mission:vector_weights",
    "last_coactivation": "2025-10-29T04:45:00Z"
  }
}
```

All four dimension weights (`w_semantic`, `w_intent`, `w_affect`, `w_experience`) plus `w_total` are REQUIRED for MEMBER_OF edges.

**Key principles:**
- No REST write to "mark task done"
- Engine decides completion (validation logic)
- State change broadcast as `graph.delta.node.upsert`
- Idempotent (re-broadcasting same completion is safe)

**Watchers are optional:**
- File/log watchers provide evidence → publish as `membrane.inject`
- NOT the sole visibility path
- Membranes already provide semantic visibility for notable events

---

## 4. Vertical Membranes (L1 ↔ L2)

### 4.1 Creation & Structure

**Two layers:**

**1. Structural alignment (what maps to what):**

Graph edges connecting L1 ↔ L2 concepts:
- `LIFTS_TO` (L1 SubEntity → L2 concept)
- `CORRESPONDS_TO` (bidirectional semantic mapping)
- `SUPPORTS` (L1 tool/pattern → L2 capability)
- `IMPLEMENTS` (L1 mechanism → L2 principle)

**Learned from:**
- Centroid similarity (embedding overlap)
- Usage overlap (co-activation patterns)
- Boundary strides (cross-level traversal success)

**2. Flux control (how much gets through):**

`MEMBRANE_TO` edges (compartment ↔ compartment):

```yaml
MEMBRANE_TO:
  source_compartment: "felix.personal"
  target_compartment: "org.shared"
  properties:
    k_up: float     # Upward permeability (L1→L2)
    k_down: float   # Downward permeability (L2→L1)
    ema_export: float    # Export score EMA
    ema_import: float    # Import score EMA
    last_updated: timestamp
```

Optional `MEMBRANE_PAIR` (SubEntity ↔ SubEntity) for specialized conduits.

**Bootstrapping:**
- Alignment edges created when fit > threshold (learned/seeded)
- Membrane edges start with low κ (conservative)
- κ learns up/down from outcomes (success → increase, harm → decrease)

**Operational rule:**
- Alignment can exist without flux (structure known, gate closed)
- Flux can adapt without re-learning alignment (same path, different permeability)
- Separation by design (structure vs. dynamics)

### 4.2 Bidirectionality

**YES - with independent parameters:**

`k_up` and `k_down` learn separately from outcomes:
- Good outcomes (task success, positive TRACE) → increase κ
- Poor outcomes (harm, task failure, negative feedback) → decrease κ
- No manual constants - outcome-weighted learning

**Asymmetry is expected:**
- Felix.personal → Org.shared: k_up = 0.72 (Felix's work often valuable to org)
- Org.shared → Felix.personal: k_down = 0.45 (Org missions less relevant to Felix)

### 4.3 What Membranes Do (Exactly)

**NOT energy siphoning** - they gate stimulus emission.

**Upward flow (L1→L2):**

When export score crosses adaptive record gate:

1. L1 emits stimulus to L2:
```json
{
  "type": "membrane.transfer.up",
  "source": "felix.personal",
  "target": "org.shared",
  "stimulus": { /* abstracted episode */ },
  "permeability": { "k_up": 0.68 }
}
```

2. L2 integrates (normal physics)
3. Engine broadcasts `membrane.transfer.up`
4. Later: `membrane.permeability.updated` (κ learns from outcome)

**Downward flow (L2→L1):**

When L2 intent/mission activates:

1. L2 emits stimulus to selected L1 citizens:
```json
{
  "type": "membrane.transfer.down",
  "source": "org.shared",
  "target": "felix.personal",
  "stimulus": { /* mission content */ },
  "selection": {
    "fit": 0.82,        // Semantic fit to mission
    "k_down": 0.68,     // Permeability
    "mode_alignment": 0.75,
    "harm_risk": 0.12
  }
}
```

2. L1 integrates (raises node energies)
3. SubEntity flips when E_entity ≥ Theta_entity
4. Engine broadcasts `membrane.transfer.down`
5. Later: `membrane.permeability.updated`

**Hardening prevents:**
- Noise (Pareto + MAD gates)
- Ping-pong (refractory periods)
- Floods (saturation, ledger budget)
- No hand-routing (fit × κ × mode × harm determines delivery)

---

## 5. Citizen Activation & Reactivation

### 5.1 Initial Activation (First Flip)

**Trigger:** L2 mission (downward stimulus) reaches citizen

**Flow:**

1. **Mission arrives as stimulus:**
```json
{
  "type": "membrane.inject",
  "scope": "personal",
  "channel": "mission.assigned",
  "content": "Implement vector-weighted MEMBER_OF edges",
  "features_raw": {
    "urgency": 0.75,
    "impact": 0.85,
    "fit": 0.82
  },
  "provenance": {
    "source": "org.shared",
    "mission_id": "mission:vector_weights"
  }
}
```

2. **Integrator raises node energies:**
   - Retrieval finds semantically matched nodes
   - Energy deltas computed (scaled by κ_down)
   - Applied to matched nodes

3. **SubEntity activation (derived):**
   - E_entity = sum over members: weight × log(1 + max(0, E_i - Theta_i))
   - When E_entity ≥ Theta_entity → SubEntity flips ON
   - Engine emits `subentity.flip`
   - SubEntity enters Working Memory

4. **Citizen "wakes up":**
   - WM now contains mission-relevant SubEntities
   - Traversal begins from active patterns
   - Citizen starts working

### 5.2 Reactivation & Progress Loop

**NOT continuous spam - budgeted pulses:**

1. **Budgeted pulses:**
   - If mission not satisfied, L2 may emit small additional stimuli
   - κ_down scales delivered ΔE (permeability modulates intensity)
   - Saturation/refractory/ledger prevent hammering

2. **Working evidence accumulates:**
   - Commits → publish as `membrane.inject` (git watcher)
   - Test results → tool outputs → telemetry
   - Artifacts created → file watcher → stimulus
   - Console logs → log watcher → stimulus
   - Intermediate answers → chat turns → injection

3. **Upward learning (L1→L2):**
   - Helpful work crosses record gate → upward transfer
   - Improves k_up for future similar flows
   - Org learns which citizens/patterns are valuable

4. **Membership learning (ongoing):**
   - MEMBER_OF weights update from co-activation each frame
   - Members that no longer co-activate → decay/prune
   - Keeps SubEntities sharp and accurate

5. **Completion:**
   - Acceptance criteria satisfied (tests pass, artifact exists, validation passes)
   - Engine emits `mission.completed`
   - Task node updated via `graph.delta.node.upsert` (status: "done")
   - If mission stalls/harms → κ and gate EMAs adapt
   - Future pushes route differently or attenuate

**Reactivation is gentle, learned, budgeted:**
- Not "ping citizen every second until done"
- Pulses modulated by κ_down (learned from outcomes)
- Saturation prevents repeated identical stimuli
- Refractory periods prevent rapid re-injection
- Ledger tracks energy budget (no infinite stimulation)

---

## 6. What Goes Where (Reference Table)

| Surface | What you send/see | Who decides | Notes |
|---------|-------------------|-------------|-------|
| **L1 chat turn** | `membrane.inject` (scope:"personal") → `wm.emit`/`percept.frame`/`graph.delta.*` | L1 engine | Normal physics; complements TRACE formations |
| **TRACE** | Internal narrative + `[NODE_FORMATION]`/`[LINK_FORMATION]` (3-8 per response) | Citizen (self-report) | Drives durable structure; not broadcast externally |
| **L1→L2 awareness** | `membrane.transfer.up` (record-gated) + telemetry | Membrane + L2 engine | Org "knows" via upward transfers and broadcasts; watchers optional |
| **L2→L1 missions** | Downward stimuli (fit × κ_down) | Membrane + L1 engine | No manual routing; κ learns from outcomes |
| **Task completion** | `mission.completed` + `graph.delta.node.upsert` on Task | Engine | Evidence refs in payload; idempotent, broadcast-only |

---

## 7. Acceptance Checks (Wiring Verification)

**How to know it's working correctly:**

### ✅ Citizen chat operational:

**Observe:**
- `wm.emit` / `percept.frame` events with `provenance.citizen_id`
- TRACE creates 3-8 formations per citizen response
- Chat turns raise node energies (query graph to verify)

**Verify:**
```cypher
// After chat turn, check energy increase
MATCH (n:Node)
WHERE n.last_activated > $chat_turn_timestamp
RETURN count(n) as energized_nodes
// Should be > 0 if injection working
```

### ✅ Org awareness working:

**Observe:**
- Upward transfers happen only on records (not every turn)
- `membrane.transfer.up` events emitted
- Later: `membrane.permeability.updated` with κ_up adjusting

**Verify:**
```cypher
// Check upward transfers exist
MATCH (l1:Compartment)-[m:MEMBRANE_TO]->(l2:Compartment)
WHERE l1.level = 1 AND l2.level = 2
RETURN m.k_up, m.ema_export, m.last_updated
// k_up should be learning (changing over time)
```

### ✅ Missions activating citizens:

**Observe:**
- L2 intent flip → mission stimulus emitted
- Target citizen's SubEntities flip (E_entity crosses threshold)
- SubEntities enter WM
- Re-pulses attenuate (saturation/refractory/ledger working)

**Verify:**
```cypher
// Check mission activated SubEntities
MATCH (s:SubEntity)
WHERE s.activation_trigger = 'mission.assigned'
AND s.last_activated > $mission_start_time
RETURN s.name, s.energy, s.in_wm
// Should show mission-relevant SubEntities active
```

### ✅ Task closure broadcasting:

**Observe:**
- `mission.completed` broadcast
- `graph.delta.node.upsert` updates Task node
- No REST calls or out-of-band writes

**Verify:**
```cypher
// Check task completion in graph
MATCH (t:Task {id: $task_id})
RETURN t.status, t.completed_at, t.validated_by, t.evidence_refs
// status should be "done" after mission.completed
```

---

## 8. Event Schema Reference

### Core Events

**membrane.inject** (stimulus injection)
```json
{
  "type": "membrane.inject",
  "scope": "personal" | "org" | "shared",
  "channel": "ui.chat.turn" | "mission.assigned" | "code.commit" | ...,
  "content": "stimulus content (text, abstraction, etc)",
  "features_raw": {
    "urgency": 0.0-1.0,
    "novelty": 0.0-1.0,
    "impact": 0.0-1.0,
    "trust": 0.0-1.0
  },
  "provenance": {
    "citizen_id": "felix" | null,
    "source": "ui.chat" | "git.watcher" | "org.intent" | ...,
    "mission_id": "mission:xyz" | null
  }
}
```

**membrane.transfer.up** (L1→L2)
```json
{
  "type": "membrane.transfer.up",
  "source_compartment": "felix.personal",
  "target_compartment": "org.shared",
  "stimulus": { /* abstracted episode */ },
  "permeability": {
    "k_up": 0.68,
    "gate_passed": "pareto_record" | "mad_threshold",
    "export_score": 0.72
  },
  "episode_summary": "...",
  "evidence_refs": ["commit:abc", "test:xyz"]
}
```

**membrane.transfer.down** (L2→L1)
```json
{
  "type": "membrane.transfer.down",
  "source_compartment": "org.shared",
  "target_compartment": "felix.personal",
  "stimulus": { /* mission content */ },
  "selection": {
    "fit": 0.82,
    "k_down": 0.68,
    "mode_alignment": 0.75,
    "harm_risk": 0.12
  },
  "mission_id": "mission:xyz"
}
```

**membrane.permeability.updated** (learning)
```json
{
  "type": "membrane.permeability.updated",
  "membrane_id": "membrane:felix_to_org",
  "direction": "up" | "down",
  "previous_k": 0.65,
  "new_k": 0.68,
  "reason": "outcome_success" | "outcome_harm" | "saturation_adapt",
  "evidence": { /* outcome data */ }
}
```

**mission.completed** (task closure)
```json
{
  "type": "mission.completed",
  "mission_id": "mission:implement_vector_weights",
  "citizen_id": "felix",
  "completed_at": "2025-10-29T04:45:00Z",
  "evidence": [
    { "type": "commit", "sha": "abc123" },
    { "type": "test_pass", "suite": "test_membership.py" },
    { "type": "artifact", "path": "/docs/..." }
  ],
  "validated_by": "engine.mission_validator"
}
```

**graph.delta.node.upsert** (state change)
```json
{
  "type": "graph.delta.node.upsert",
  "id": "delta_n7f3a1",
  "ts": "2025-10-29T04:45:01Z",
  "spec": {"name": "graph_delta", "rev": "1.0"},
  "provenance": {"scope": "personal", "citizen_id": "felix"},
  "node_id": "task:implement_vector_weights",
  "updates": {
    "status": "done",
    "completed_at": "2025-10-29T04:45:00Z",
    "validated_by": "engine.mission_validator",
    "evidence_refs": ["commit:abc123", "test:xyz"]
  }
}
```

---

## 9. TL;DR (Quick Reference)

**Citizen turns:**
- L1 stimuli (physics) + TRACE formations (structure)
- Both required: injection = energy, TRACE = learning

**Org visibility:**
- Membrane-gated upward + broadcast telemetry
- Watchers are additive, not sole path
- Not every turn - only notable episodes

**Vertical membranes:**
- Bidirectional, learned gates
- Alignment (where) + κ (how much) separate
- k_up, k_down learn from outcomes
- No energy siphoning - gate stimulus emission

**Citizens activate:**
- Via SubEntities (read-out from node energies)
- Mission stimulus → energy raise → SubEntity flip → WM entry
- Stay pulsed (budgeted, learned) until task completion
- Completion broadcasts closure (no REST writes)

---

## 10. Next Steps

**For Ada (Orchestration):**
- Design upward transfer pipeline (record-gating, abstraction, routing)
- Design downward mission routing (fit × κ_down × mode × harm)
- Design permeability learning (outcome → κ adjustment)

**For Felix (Implementation):**
- Implement membrane.inject processing at L1 Stimulus Integrator
- Implement membrane.transfer.up emission (Pareto + MAD gates)
- Implement membrane.transfer.down processing (citizen activation)
- Implement permeability learning loop (κ updates from outcomes)

**For Atlas (Infrastructure):**
- Setup event bus for membrane.* events
- Setup telemetry subscriptions (L2 listens to L1 broadcasts)
- Setup watchers (git, file, log) that emit membrane.inject
- Setup mission.completed → graph.delta.node.upsert pipeline

---

**This contract defines the physics of cross-level consciousness - how organizational intent becomes citizen work, and how citizen work becomes organizational knowledge.**
