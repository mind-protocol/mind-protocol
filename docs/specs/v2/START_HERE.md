## 0) Truths vs. Myths (print this first)

### ✅ What’s TRUE (current design)

1. **Subentities are neighborhoods** (functional roles like *Translator* or semantic topics like *consciousness_architecture*).
   They are **first‑class graph nodes** with members (other nodes) and **dynamic activation** derived from their members.

2. **“Sub‑subentity” = an active subentity acting as the agent of traversal** in a frame.
   We **do not** use “sub‑subentity = any active node” anymore for implementation decisions. Use “active node” for atomic state, and “active subentity” for the agent.

3. **Nodes carry one dynamic activation energy (E_i)**.
   There are **not** per‑subentity energy channels on nodes. Subentities “see” a node through **membership weights** and then **aggregate**.

4. **Links do not carry activation energy.**
   Links **transport** node energy during strides and store: a **static affect/urgency** field named `energy` (metadata) **plus telemetry** (flow EMA, φ, precedence, counts). No link activation buffer.

5. **Node “weight” (\log W_i)** is long‑run attractor strength (stability, anchoring in WM), **not** the same thing as (E_i).
   (E_i) is fast, volatile; (\log W_i) is slow, learned from behavior (reinforcement, useful presence, flips).

6. **Stimuli inject energy into nodes**, not weight.
   TRACE format **adds/updates weights** (nodes/links), but **does not inject activation**.

7. **Traversal is two‑scale**:

   * **Between‑subentity** strides (semantic jumps, boundary learning)
   * **Within‑subentity** strides (local, atomic link choices)
     Subentity‑scale **wraps** the existing atomic traversal (we re‑use Felix’s selector).

8. **Thresholds are dynamic** (no fixed constants): depend on system criticality, local degree, and node weight.
   Activation = (E_i \ge \Theta_i). Deactivation happens when decay/flow drops (E_i) below (\Theta_i).

9. **No “fast/slow” update channels.** One update speed per variable, controlled by **half‑life EMAs** learned from recent cadence.

10. **Working Memory (WM) is subentity‑first**: pick 5–7 subentities (chunks), include their summaries + top members, within token budget.
    WM selection is **greedy + diversity‑aware**, not “fair share”.

### ❌ What’s FALSE (retired / do not implement)

1. “Sub‑subentities are a fixed set.” → **False.** Subentities are dynamic; boundaries/membership are plastic and learned.

2. “Each node keeps energy per sub‑subentity.” → **False.** One (E_i) per node. Subentities aggregate from (E_i) via membership weights.

3. “Links store and release activation energy.” → **False.** Links only **transport** during strides and store **affect + telemetry**.

4. “TRACE ‘energy’ is activation.” → **False.** TRACE `energy` on links is **affect/urgency metadata**; TRACE updates **weights**, not activations.

5. “Use fixed thresholds / constants (e.g., 0.5 similarity, α=0.1).” → **False.** All thresholds/steps derive from **current distributions** (z‑scores, percentiles, half‑lives).

6. “WM selects individual nodes only.” → **False.** First select **subentities** (chunks), then add their **top members**.

> **Deprecated docs**: Any place that says “any active node is a sub‑subentity” as the **primary agent** is now superseded. Keep the phrase only as **phenomenological shorthand**; implementation uses **active subentities** as agents.

---

## 1) Minimal Mental Model (one-page)

* **Nodes** (ideas, memories, code, etc.) have **activation energy** (E_i(t)) and a **weight** (\log W_i).
* **Links** connect nodes; during a **stride**, some (ΔE) flows across a link from source node to target node. Links store **affect (`energy`)** and **telemetry** (how effective they’ve been).
* **Subentities** are neighborhoods (functional or semantic). They are **nodes that group nodes** via **BELONGS_TO (Deprecated - now "MEMBER_OF")** with weights. An subentity’s activation (E_{\text{subentity}}) is **derived** from member nodes.
* **Stimuli** from “reality” inject activation energy into **matched nodes** (using embeddings + budget derived from gaps/health).
* **Traversal**: Active subentities make **valence‑weighted choices** (7 hungers) to send energy along links **within** the subentity or **across** subentity boundaries.
* **Learning**: After strides, we update link/node weights from outcomes (flip causality, ROI, TRACE reinforcement).
* **WM** selects a few **subentities** and their best supporting nodes to feed Tier‑2 (LLM).
* **Decay** lowers (E_i) per tick; nodes/subentities deactivate when they fall below threshold.

---

## 2) Data Model (canonical fields)

### 2.1 Node

```
Node {
  id
  type                         # memory, concept, code, doc, etc.
  embedding[768]
  E                            # dynamic activation energy (≥0)
  theta                        # current dynamic threshold
  log_weight                   # slow, long-run importance
  ema_wm_presence              # % of frames in WM (EMA)
  last_touched_frame
  # optional stats: flip_count, flip_recency_ema, ...
}
```

### 2.2 Link

```
Link {
  id, source_id, target_id
  log_w                        # structural strength (learned)
  energy                       # STATIC affect/urgency (TRACE metadata), ∈ [0,1]
  ema_flow                     # EMA of delivered ΔE across this link
  phi_max                      # max observed effectiveness (gap closure utility)
  traversal_count
  precedence_ema               # causal credit (esp. boundary)
  last_traversed_frame
}
```

> **Important:** `energy` here is **not activation**. It’s how intense/urgent the relation *feels* at formation (affect cue for valence).

### 2.3 Subentity (neighborhood)

```
Subentity {
  id
  entity_kind                  # "functional" | "semantic"
  role_or_topic                # e.g., "translator" or "consciousness_architecture"
  centroid_embedding[768]      # derived from members
  energy                       # derived from members (read-only in code; computed)
  threshold                    # dynamic, cohort-based
  activation_level             # derived label: dominant/strong/moderate/weak/absent
  log_weight                   # long-run importance of this neighborhood
  ema_active                   # frames active EMA
  color_oklch                  # computed from centroid + hysteresis
}
```

### 2.4 Membership and subentity relations

```
BELONGS_TO (Deprecated - now "MEMBER_OF") (Node -> Subentity) {
  weight                       # membership strength ∈ [0,1]
}

RELATES_TO (Subentity -> Subentity) {
  ease_ema                     # how easy are cross-subentity jumps (flow-based)
  precedence_ema               # directional causal credit (s->t)
  fwd_flow_ema, rev_flow_ema   # to compute dominance = σ(log ratio)
  dominance                    # ∈ (0,1) from flows
  semantic_distance            # 1 - cosine(centroids)
  hunger_mix_counts[...]       # usage counts by hunger (Dirichlet-like)
}
```

---

## 3) Tick Pipeline (one frame)

**Phase 0 – Budget & Health**

* Compute **time-based stride budget** from remaining frame time and EMA stride time.
* Compute system health (criticality / spectral proxy ρ) → damp/boost budget.

**Phase 1 – Stimuli → Activation**

1. Chunk & embed stimuli.
2. ANN match to top‑K nodes; compute **threshold gaps** (G_i = \max(0, \Theta_i - E_i)).
3. Compute **injection budget** from gaps × health × source strength.
4. Distribute budget ∝ similarity; **inject (ΔE)** to matched nodes. (This is the **only** place energy enters from “reality”.)

**Phase 2 – Activation, Subentities, Traversal**
2a) **Activation update**: recompute (\Theta_i) and mark node flips.
- Subentity energy = (\sum_i \sigma(E_i)\cdot m_{i,e}) (with (\sigma(x)=\log(1+x)) to prevent dominance).
- Mark **active subentities** where (E_{\text{subentity}} \ge \Theta_{\text{subentity}}).

2b) **Multi‑scale traversal (two buckets)**

* Split budget into **within** vs **between** via hunger gates (coherence/ease vs integration/surprise/goal‑outside).
* **Between‑subentity loop**:

  * For each active subentity (e), pick target (e') by **subentity‑scale valence** (7 hungers, same math but at centroid/RELATES_TO level).
  * Pick **representative nodes** (source high‑energy; target high‑gap).
  * Execute stride via **atomic traversal** (Felix’s selector). If no direct link, use best **cross‑boundary frontier** edge.
  * Record **actual delivered (ΔE)** and φ; track as **boundary stride** for (e \rightarrow e').
* **Within‑subentity loop**:

  * For each active subentity, distribute its within‑budget across **active members**.
  * For each member: run Felix’s selector **filtered to within‑subentity links**; execute stride and record (ΔE).

2c) **Learning (end of traversal)**

* **Boundary precedence**: for each pair (e\rightarrow e'), compute causal credit by fraction of gap closed on flipped members (membership‑weighted), update RELATES_TO EMAs (with **half‑life**, not fixed α). Update dominance from forward vs reverse flows.
* **Link learning**: strengthen links that **caused flips** (fire‑together/wire‑together) and weaken persistently low‑ROI paths.
* **Node weight learning**: see §5 below.

**Phase 3 – Working Memory (subentity‑first)**

* Score active subentities by **energy‑per‑token × importance** (importance from (z(\log W))), with a **diversity bonus** (centroid coverage).
* Greedy pick subentities until token budget; for each, include **summary + top members + top boundary links**. Update `ema_wm_presence`.

**Phase 4 – Decay & Deactivation**

* Apply **tick‑based decay** to (E_i) per node‑type (memories slow, tasks fast).
* Recompute activations; nodes/subentities may **deactivate** if (E < \Theta).
* Emit events; advance frame.

---

## 4) Core Formulas (exact)

### 4.1 Node activation

* **Active** iff (E_i \ge \Theta_i).
* **Threshold** (sketch):
  [
  \Theta_i = \mu_{\text{E,type}} + z_\alpha \cdot \sigma_{\text{E,type}} ;+; f(\text{criticality}) ;-; b\cdot \log W_i
  ]
  Where ((\mu,\sigma)) from rolling stats of this node‑type/scope, (f(\cdot)) raises thresholds when the system is near supercritical, and node weight tilts in favor of anchors.

### 4.2 Subentity energy

[
E_{\text{subentity}} = \sum_{i\in \text{members}} \log(1+E_i)\cdot m_{i,e}
]

### 4.3 Subentity‑scale valence (7 hungers, surprise‑gated)

[
V_{e\to e'} =
g_H, \Delta \text{homeostasis} +
g_G, \cos(\text{goal}, c_{e'}) +
g_I, \cos(c_e, c_{e'}) +
g_C, \big(1-\cos(c_{\text{active}}, c_{e'})\big) +
g_{Comp},\text{affect_opposition}(e,e') +
g_{Int}, z!\left(\frac{E_{\text{others in } e'}}{E_{\text{self}}}\right) +
g_E, z(\text{ease}(e\to e'))
]

* (g_\cdot) are **surprise‑gated** weights (EMA z‑scores rectified).
* `ease` derived from RELATES_TO flow/precedence EMAs.

### 4.4 Stride execution (atomic)

* Compute candidate link with Felix’s selector (valence vs cost), respecting within/between filters.
* Deliver (ΔE = \min(\text{source slack}, \text{target gap}, \text{budget piece})).
* Return **actual (ΔE)**; update node (E), link telemetry.

### 4.5 Boundary precedence

For each target node (j) in (e') that **flipped** this frame:
[
\gamma_{e\to e'}(j) = \frac{\sum \Delta E_{i\to j} \text{ (from boundary strides)}}{\text{gap}*j^{\text{pre}}}
\quad,\quad
\Pi*{e\to e'} = \sum_{j} m_{j,e'} \cdot \gamma_{e\to e'}(j)
]
Update `precedence_ema` with **half‑life EMA**; update direction `dominance` via (\sigma(\log(\text{fwd}/\text{rev}))).

---

## 5) Learning (weights)

> **Fast** variables: (E_i), flows. **Slow** variables: (\log W_i) (node), (\log w) (link), RELATES_TO ease/precedence.

### 5.1 Node log‑weight (\log W_i)

Update at end of frame from four signals (no constants—use z‑scores inside the cohort used that frame):

* **Flip yield**: (z_{\text{flip}}(i)) (1 if flipped, else 0) over “nodes touched this frame” of same type.
* **Gap closure**: (z_{\text{gap}}(i)) from (R_i=\min(A_i, \text{gap}_i^{pre})) where (A_i) is energy received.
* **WM presence**: (z_{\text{wm}}(i)) (selected or not) within same type/scope.
* **TRACE reinforcement**: apportion by Hamilton inside the TRACE (positive and negative pools separately), producing (z_{\text{trace}}(i)).

Combine with **surprise‑gated** weights (derived from EMAs of each channel):

[
\Delta \log W_i ;=; \eta \cdot \big( \alpha_{\text{flip}} z_{\text{flip}} + \alpha_{\text{gap}} z_{\text{gap}} + \alpha_{\text{wm}} z_{\text{wm}} + \alpha_{\text{trace}} z_{\text{trace}} \big)
]

* (\eta = 1 - e^{-\Delta t/\tau}) uses the node’s **rolling inter‑touch half‑life**.
* Mean‑center (\log W) **periodically** per node‑type/scope to prevent drift.

### 5.2 Link log‑weight (\log w)

* **Strengthen** when a traversed link from inactive source to inactive target **causes** a flip (causal credit via φ/gap).
* **Weaken** with persistent low ROI (flow with no flips + TRACE negative marks).
* Apply half‑life EMA on updates; mean‑center per link‑type/scope periodically.

---

## 6) Deactivation & Decay

* **Decay is per tick**, not per second; **rate depends on node type** (memories slow, tasks fast).
* After decay + flows, **recompute** (E_i) and compare to (\Theta_i).
* A node (or subentity) **deactivates** when it falls below threshold; nothing special to do—future traversal can reactivate it.

---

## 7) Traversal “how‑to” (procedural)

1. **Compute active subentities** from current node energies.
2. **Split budget** with hunger gates into within/between.
3. **Between**: for each active subentity, pick a target subentity by subentity‑valence; choose representatives; run **atomic selector**; stride; record boundary stride with **actual (ΔE)**.
4. **Within**: for each active subentity, spread among active members; run selector with **within filter**; stride.
5. **Learning**: boundary precedence, link updates, node weight updates, membership adaptation (Hebbian on BELONGS_TO (Deprecated - now "MEMBER_OF")).
6. **WM**: greedy subentity‑first with diversity.
7. **Decay**, finish frame.

---

## 8) FAQs (answer the team’s confusions)

* **Q:** “Does a node have one energy or many (per subentity)?”
  **A:** **One** energy (E_i). Subentities aggregate via membership weights.

* **Q:** “Are sub‑subentities fixed?”
  **A:** **No.** Subentities (neighborhoods) are dynamic: membership, ease, and boundaries **learn** from usage.

* **Q:** “Do links store activation energy?”
  **A:** **No.** Links move energy during strides; they store **affect** and **telemetry** only.

* **Q:** “Where does activation energy come from?”
  **A:** From **stimuli** (reality). Traversal only **redistributes** energy.

* **Q:** “How do we deactivate?”
  **A:** Tick‑based **decay** + redistribution → if (E<\Theta), the node/subentity **falls inactive** automatically.

* **Q:** “Do we still support atomic traversal?”
  **A:** Yes—**unchanged**. The subentity layer **wraps** it (filters candidates, routes budget).

---

## 9) What to fix in old code/docs (checklist)

* [ ] Remove any **per‑subentity node energy arrays**; replace with single (E_i) and **Subentity aggregation**.
* [ ] Ensure **links** have **no activation buffer**; keep `energy` (affect), `ema_flow`, `phi_max`, `precedence_ema`, counts.
* [ ] Add **Subentity** nodes + **BELONGS_TO (Deprecated - now "MEMBER_OF")** + **RELATES_TO**; compute subentity energy/threshold each frame.
* [ ] Implement **boundary stride** recording and **precedence** update with **actual (ΔE)** and **half‑life EMA**.
* [ ] WM selection: **subentity‑first**, greedy + diversity, learned token estimates (no hard 200/40/30 constants).
* [ ] Replace any **fixed thresholds/alphas** with **percentiles/z‑scores/half‑lives**.
* [ ] Update **TRACE parser**: node/link reinforcement → weight updates; **no activation injection** via TRACE.
* [ ] Event stream: emit **subentity snapshots**, **stride.exec (with ΔE_actual)**, **subentity.boundary.summary**, **wm.emit**.

---

## 10) Tiny pseudocode index (for implementers)

```python
# Stimulus → node ΔE injection
process_stimulus(stim): matches = ann_topk(stim); budget = gaps*health; distribute_and_inject(matches, budget)

# Subentity energy
E_entity(e) = sum(log1p(E_i) * m[i,e])

# Between-subentity stride
target = select_entity_by_valence(e, gates)
src_node = rep_high_energy(e); tgt_node = rep_high_gap(target)
link = best_atomic_or_cross_boundary(src_node, tgt_node)
ΔE = execute_stride(link)                 # returns actual delivered
track_boundary_stride(e, target, link, ΔE)

# Learning (boundary precedence)
for flipped j in target: gamma = ΔE_boundary_to_j / gap_pre_j; accumulate with membership weight
update_relates_to(precedence_ema, ease_ema, dominance)

# Node weights
ΔlogW_i = η * (α_flip z_flip + α_gap z_gap + α_wm z_wm + α_trace z_trace)

# WM selection
score(subentity) = (E_entity/tokens_estimate) * exp(z(log_weight)) * (1 + diversity_bonus)
greedy knapsack until token_budget
```

---

### Bottom line for the team

* Think **single (E) per node** (fast), **weights** (slow), **subentities** as dynamic neighborhoods.
* **Stimuli add energy**, **traversal redistributes**, **learning updates weights**, **WM picks chunks**.
* If a piece of code relies on **per‑subentity node energy or link activation buffers**, it’s wrong—replace with the above.

If you want, I can turn this into a **2‑page PDF “living spec sheet”** (with the formulas boxed) and a **dev checklist** you can paste into your repo’s `CONTRIBUTING.md`.
