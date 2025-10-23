---
title: Observability Events — WebSocket Contract
status: stable
owner: @iris
last_updated: 2025-10-22
depends_on:
  - entity_layer/entity_layer.md
  - runtime_engine/traversal_v2.md
  - learning_and_trace/trace_weight_learning.md
summary: >
  Canonical schema for live visualization: snapshots and frame-delta events for nodes, links, and entities (subentities).
  Wire format is versioned, compact, and attribution-friendly.
---

# 0) Transport & framing

- **Protocol:** WebSocket; messages are **JSON Lines** (one JSON object per line). Server may enable gzip; client advertises `Accept-Encoding: gzip`.
- **Versioning:** Every message carries a `kind` field (e.g., `"tick_frame.v1"`, `"node.flip.v1"`). We only **append** fields in v1; breaking changes → v2 kind.
- **Ordering:** Each message includes `frame_id` (monotone) and `ts`. Clients keep a **2-frame reorder buffer** and render on `frame.end.v1`.
- **Rates:** ≤10 fps target; sampling rules keep payloads bounded (see §5).
- **IDs:** String IDs are stable logical IDs; do not assume incrementality.

# 1) Snapshot (cold start / reconnect)

**Endpoint:** `GET /viz/snapshot` returns a compact bootstrap state:

```json
{
  "kind": "snapshot.v1",
  "ts": "2025-10-22T14:10:02.481Z",
  "frame_id": 123456,
  "entities": [
    {"id":"e.arch","name":"Architect","kind":"functional","color":"#8A84FF",
     "energy":4.6,"theta":4.1,"active":true,"members_count":42,"coherence":0.68}
  ],
  "nodes": [
    {"id":"n.B","energy":1.45,"theta":1.12,"log_weight":2.58,"primary_entity":"e.arch"}
  ],
  "links": [
    {"id":"l.A→B","src":"n.A","dst":"n.B","ema_phi":0.42,"dominance":0.71, "z_flow":0.00}
  ]
}
````

Notes:

* **Single‑energy substrate:** Nodes expose `energy` & `theta`; **links do not** carry energy; they expose telemetry (e.g., `ema_phi`, `z_flow`).
* Entities expose **derived** energy (aggregation), not per‑entity node channels.

# 2) Tick frame envelope

```json
{
  "kind": "tick_frame.v1",
  "ts": "2025-10-22T14:10:02.481Z",
  "frame_id": 123457,
  "dt_ms": 48,
  "rho": 1.03,
  "budget": {"used": 0.62, "cap": 1.00},
  "active_frontier": {"nodes": 812, "shadow": 2273},
  "nodes": [
    {"id":"n.B","energy":1.51,"theta":1.12,"active":true, "a":0.77}
  ],
  "nodes_removed": ["n.X42"],
  "links": [
    {"src":"n.A","dst":"n.B","flow":0.14,"z_flow":0.32,"active":true}
  ],
  "links_removed": [["n.C","n.D"]],
  "entities": [
    {"id":"e.arch","energy":4.8,"theta":4.1,"active":true,"coherence":0.70}
  ],
  "wm": {
    "entities": [{"id":"e.arch","score":0.82,"cost":0.34,"incumbent":true}],
    "budget_used": 0.58, "budget_cap": 1.00
  },
  "health": {"conservation_eps": 1e-6},
  "notes": ["stride sampling: 0.1"]
}
```

**Field semantics**

* `a` is **soft activation** (σ(κ(E−Θ))) for visual emphasis near threshold.
* `flow` is per‑frame selected stride flow; `z_flow` is cohort‑standardized EMA (learning input).
* `coherence` is entity‑internal pattern coherence (0–1).

# 3) Atomic events (deltas)

### 3.1 Node/Link energy & flips

```json
{"kind":"node.flip.v1","frame_id":123457,"ts":"...","id":"n.B","active":true,"energy":1.51,"theta":1.12}
```

```json
{"kind":"node.emotion.update.v1","frame_id":123457,"ts":"...","id":"n.B",
 "vec":{"valence":-0.62,"arousal":0.35},"mag":0.71,
 "top_axes":[{"axis":"valence","value":-0.62},{"axis":"arousal","value":0.35}]}
```

```json
{"kind":"link.emotion.update.v1","frame_id":123457,"ts":"...","id":"l.A→B","mag":0.42,
 "top_axes":[{"axis":"valence","value":-0.20},{"axis":"arousal","value":0.38}]}
```

### 3.2 Stride execution (attribution)

```json
{"kind":"stride.exec.v1","frame_id":123457,"ts":"...","src":"n.A","dst":"n.B","dE":0.036,
 "phi":0.42,"ease":1.31,"resonance":0.48,"res_mult":0.79,"comp_score":0.31,"comp_mult":0.86}
```

### 3.3 Entity and boundary summaries

```json
{"kind":"se.state.v1","frame_id":123457,"ts":"...","id":"e.arch","energy":4.8,"theta":4.1,"active":true,"coherence":0.70,
 "active_goal":"schema_validation","goal_strength":0.85,"urgency":0.62}
```

**Field additions (v1.1):**
- `active_goal` (optional string): Current dominant goal for this entity
- `goal_strength` (optional float 0-1): Activation strength of the active goal
- `urgency` (optional float 0-1): Urgency level driving behavior

```json
{"kind":"se.boundary.summary.v1","frame_id":123457,"ts":"...","src":"e.arch","dst":"e.op","count":23,
 "dE_sum":0.94,"precedence":0.63,"phi_max":0.51,"dominance":0.58}
```

### 3.4 Phenomenological health and alignment

```json
{"kind":"phenomenology.mismatch.v1","frame_id":123457,"ts":"...","entity_id":"e.arch",
 "substrate_valence":-0.35,"substrate_arousal":0.62,"substrate_mag":0.71,
 "selfreport_valence":0.20,"selfreport_arousal":0.45,"selfreport_mag":0.49,
 "divergence":0.73,"threshold":0.50,"mismatch_detected":true,
 "mismatch_type":"valence_flip"}
```

**Purpose:** Detect divergence between substrate-inferred affective state (from emotion vectors) and entity self-report (citizen introspection).

**Field semantics:**
- `substrate_*`: Valence/arousal/magnitude computed from aggregate emotion vectors
- `selfreport_*`: Valence/arousal/magnitude from entity's explicit self-report
- `divergence`: Euclidean distance between substrate and self-report vectors
- `threshold`: Divergence threshold for mismatch detection
- `mismatch_detected`: Boolean flag when divergence > threshold
- `mismatch_type`: Classification (valence_flip | arousal_mismatch | magnitude_divergence | coherent)

```json
{"kind":"phenomenological_health.v1","frame_id":123457,"ts":"...","entity_id":"e.arch",
 "flow_state":0.78,"flow_components":{"wm_challenge_balance":0.82,"engagement":0.91,"skill_demand_match":0.62},
 "coherence_alignment":0.85,"resonance_dominance_ratio":2.31,
 "multiplicity_health":0.68,"multiplicity_components":{"distinct_entities_coactive":3,"thrashing_detected":false,"co_activation_stability":0.71},
 "overall_health":0.77}
```

**Purpose:** Track phenomenological health across three dimensions: flow, coherence alignment, and multiplicity health.

**Field semantics:**
- `flow_state` (0-1): Overall flow quality (WM-challenge balance, engagement, skill-demand match)
  - `wm_challenge_balance`: How well WM capacity matches challenge level
  - `engagement`: Energy investment relative to capacity
  - `skill_demand_match`: Entity capability vs task demands
- `coherence_alignment` (0-1): How well resonance dominates over complementarity (healthy = resonance-driven)
- `resonance_dominance_ratio`: Ratio of resonance gates to complementarity gates (>1 = healthy)
- `multiplicity_health` (0-1): Health of multi-entity co-activation
  - `distinct_entities_coactive`: Count of simultaneously active entities
  - `thrashing_detected`: Boolean flag for entity thrashing
  - `co_activation_stability`: Stability of entity coalition over recent frames
- `overall_health` (0-1): Aggregate phenomenological health score

### 3.5 Learning updates

```json
{"kind":"weights.updated.trace.v1","frame_id":123457,"ts":"...","scope":"link","cohort":"task",
 "n":1542,"d_mu":0.012,"d_sigma":-0.004}
```

```json
{"kind":"weights.updated.traversal.v1","frame_id":123457,"ts":"...","scope":"link","cohort":"task",
 "n":550,"d_mu":0.006,"d_sigma":0.001}
```

### 3.6 Stimuli

```json
{"kind":"stimulus.injected.v1","frame_id":123457,"ts":"...","source":"user_message","chunks":3,
 "matches_selected":12,"entropy":2.3,"coverage_target":0.90,
 "budget_base":18.5,"health_factor":0.92,"source_gate":1.15,"peripheral_amp":1.30,
 "budget_final":25.6,"energy_injected":24.2,"nodes_activated":8,"flips":5}
```

```json
{"kind":"stimulus.item_injected.v1","frame_id":123457,"ts":"...","item_id":"n.X","item_type":"node",
 "similarity":0.85,"delta_energy":3.2,"gap_before":4.5,"gap_after":1.3}
```

# 4) Frame boundary

```json
{"kind":"frame.end.v1","frame_id":123457,"ts":"...","deltaE_total":-1e-06,
 "active":{"nodes":812,"shadow":2273},"duration_ms":48}
```

# 5) Sampling & throttling

* **Frontier‑first:** only nodes in **active** and top‑degree **shadow** are eligible for node deltas.
* **Stride sampling:** default 10% of `stride.exec`; always include top‑φ strides.
* **Aggregation windows:** EMAs emitted every N frames (default 30).
* **Quantization:** numeric fields may be quantized (e.g., 1e‑3) and compacted to save bandwidth.

# 6) Interpretation primers (what to read & why it matters)

* **Why a link was chosen:** look at `stride.exec` → `phi` (usefulness), `res_mult/comp_mult` (emotion gates), and `ease` (`exp(log_weight)`).
* **Is the system stable?** watch `rho` near 1; `deltaE_total≈0` (conservation, excluding decay/stimuli).
* **Are we regulated or coherent?** compute **Regulation vs Coherence Index** from counts where `comp_mult<1` vs `res_mult<1`.
* **Is tint trustworthy?** `node.emotion.update.mag` histograms and **Staining Watch** (see viz patterns doc).

# 7) Backpressure & error semantics

* **Backpressure:** server may drop low‑priority deltas first (node emotion updates), then reduce stride sampling; `notes` lists applied reductions.
* **Error/Schema:** any unknown `kind` is ignored by clients; fields may be omitted (forward compatible).
