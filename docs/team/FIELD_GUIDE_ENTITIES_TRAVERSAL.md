# Mind Protocol v2 — Team Field Guide (Entities, Traversal, Bootstrap)

> **TL;DR for the bug you hit:**
> Subentities are **not** Mechanisms. Don't look for `Mechanism` seeds.
> **Create functional entities from config**, then (when embeddings exist) add semantic entities by clustering. That immediately fixes "0 entities" and lets Iris render WM and beams.

---

## 0) Truths vs. Myths (pin this)

### Truths

* **T1 — Single activation energy per node.**
  Nodes carry dynamic `energy` (activation). Links transport energy; links **do not** store activation energy.
  `link.energy` = *affect metadata* (how urgent/intense the relation feels), used in **valence**, not as a budget.

* **T2 — Entities = neighborhoods.**
  An **Entity** is a neighborhood (topic or role) defined by **memberships** from nodes (`BELONGS_TO` with weights).
  Entities live in the DB as first‑class nodes (`Entity`), with fields like `centroid_embedding`, `log_weight`, `color`, etc.

* **T3 — "Sub‑entity" = an **active** Entity this frame.**
  The **same** entity can be inactive this frame and active next frame. Activation is dynamic (energy‑driven), membership can adapt slowly (learning).

* **T4 — Stimuli inject activation; TRACE changes weights.**
  **Stimuli** raise node `energy` (activation). **TRACE** updates **weights** (`log_weight` of nodes/links, memberships), not activation energy.

* **T5 — Traversal is two‑scale.**
  **Entity‑scale** selection chooses where to go (topic/role jumps), then **atomic‑scale** (Felix's link selector) picks the concrete link/node stride.

* **T6 — WM is entity‑first.**
  We select **5–7 entities (chunks)** into WM, then include their top members. This matches phenomenology and scales.

* **T7 — No fixed magic constants.**
  Use cohort z‑scores, percentiles, EMAs with time constants tied to observed cadence — no hardcoded "3.0" multipliers.

### Myths

* **M1 — "Subentities are fixed."**
  ❌ No. Entities are persistent *neighborhoods*; **sub‑entities** are just the **currently active** ones.

* **M2 — "Nodes have different energies per entity."**
  ❌ No. We deliberately use **one** activation energy per node (greatly simplifies traversal and learning).

* **M3 — "Mechanism nodes are required to seed entities."**
  ❌ No. That requirement was accidental. Subentities are *modes/patterns*, not algorithms.

* **M4 — "Links store activation energy."**
  ❌ No. Links store affect + telemetry (flow stats, precedence). Activation energy lives on nodes only.

---

## 1) What is an Entity? What is a Sub‑entity?

* **Entity (persistent, first‑class graph node)**
  A neighborhood (topic or role) with:

  * `members`: list of (node_id, membership_weight ∈ [0,1])
  * `energy`: aggregated from member node energies
  * `threshold`: dynamic cohort threshold for "comes into focus"
  * `centroid_embedding`: mean/robust centroid of member embeddings
  * `log_weight`: long‑run importance (learned from TRACE & traversal)
  * `color`: derived from centroid (OKLCH hashing + hysteresis)

* **Sub‑entity (runtime notion)**
  An **Entity** whose aggregated `energy` ≥ `threshold` **this frame** → "active". That's it.

### Entity energy aggregation (simple, fast, correct)

For entity `e` with members `(i, m_i)`:

```
energy_e = Σ_i  m_i · log1p( max(0, energy_i - threshold_i) )
```

Where we use **surplus-only** energy (above each node's threshold) with **log damping** to prevent both sub-threshold leakage and single-node domination. Optional: use softplus for smooth knee near threshold.

**Threshold_e** is a dynamic cohort statistic (e.g., median + k·MAD within entity kind/scope); no fixed constants.

---

## 2) Activation, Decay, Deactivation

* **Stimuli** raise node `energy` (bounded by local gap & health guards).
* **Decay** reduces node `energy` per tick (type‑dependent rates; ticks cadence may be tied to recent stimulus recency if using adaptive ticks).
* A node **flips active** when `energy ≥ threshold(node)`.
* An entity **flips active** when `energy_e ≥ threshold_e`.
* **Deactivation** is just energy falling below threshold again (after decay / energy redistributed elsewhere).

---

## 3) Traversal (two‑scale)

**Phase 2b execution outline:**

1. **Entity‑scale** (chunk selection)

   * Compute entity‑to‑entity **valence** with 7 hungers (goal, identity, completeness, complementarity, homeostasis, integration, ease).
   * Choose target entity (stochastic, valence‑weighted).
   * Choose representative nodes: source (high energy), target (high gap), membership‑weighted.
2. **Atomic‑scale**

   * Reuse Felix's `select_next_traversal` to pick the concrete link between those nodes (or a short path in v2.1), then **execute stride** (move ΔE).
3. **Boundary learning**

   * If cross‑entity strides helped target members flip, update `RELATES_TO` (precedence/flow/ease).

**Within‑entity** traversal is the same atomic selection but constrained to links whose targets are in the same entity.

Budget split is hunger‑driven (coherence → more within; integration/surprise → more between).

---

## 4) Learning & TRACE

* **TRACE**: marks **usefulness** and declares **formations** → updates **`log_weight`** (nodes/links) and **membership weights**.
* **Traversal telemetry on links**: `flow_ema`, `phi_max`, precedence counters (no activation buffers).
* **"Fire together, wire together"**: co‑activation strengthens memberships & links (with gating to avoid noise).

---

## 4.5) Entity Lifecycle & Quality (CRITICAL)

**Problem:** How do entities get promoted, mature, or dissolved? When does an entity prove valuable vs. noise?

**Solution:** Entity **quality scores** aggregate health signals → lifecycle transitions (runtime → provisional → mature → dissolved).

### Quality Scoring

Entity quality = **geometric mean** of 5 EMAs:

```
quality = (ema_active · coherence_ema · ema_wm_presence · ema_trace_seats · ema_formation_quality) ^ (1/5)
```

**Why geometric mean?** All dimensions must be healthy—if any dimension is near zero, quality collapses. This enforces "all dimensions matter."

**Critical property:** Geometric mean with zero-initialized EMAs → quality ≈ 0.01 (doomed). Must initialize carefully.

### Lifecycle States

1. **runtime**: Newly created, undergoing evaluation
2. **provisional**: Demonstrating utility, not yet proven
3. **mature**: Sustained high quality, proven valuable
4. **dissolved**: Quality too low, removed from graph

### Type-Based Rules (CRITICAL FIX)

**Entity `kind` determines operational semantics:**

* **functional entities** (`kind='functional'`): Translator, Architect, Validator, etc.
  * **NEVER dissolve** (permanent infrastructure)
  * Quality computed for telemetry only
  * Lifecycle evaluation **skipped entirely**
  * Rationale: Curated scaffolding roles, not hypotheses

* **emergent/semantic entities** (`kind='emergent'|'semantic'`): Discovered patterns
  * Full lifecycle evaluation
  * Can promote or dissolve based on quality
  * Subject to age gates (see below)

### Three-Layer Protection

**Historical bug:** Zero-initialized EMAs → geometric mean ≈ 0.01 → dissolution after ~20 frames (~70 seconds). Functional entities dissolved despite being valid infrastructure.

**Layer 1: Type Guard (Policy)** — Never evaluate functional entities for dissolution:

```python
if entity.kind == "functional":
    return None  # Skip lifecycle entirely
```

**Layer 2: Neutral Initialization (Data Hygiene)** — Initialize functional entities with neutral EMAs on load:

```python
# In falkordb_adapter.load_graph(), for functional entities:
entity.ema_active = 0.6
entity.coherence_ema = 0.6
entity.ema_wm_presence = 0.5
entity.ema_trace_seats = 0.4
entity.ema_formation_quality = 0.6
entity.frames_since_creation = 1000  # Start "old enough"
entity.stability_state = "mature"
```

Result: Geometric mean ≈ 0.56-0.65 (healthy), not ≈ 0.01 (doomed).

**Layer 3: Age Gate (Mechanism Maturity)** — Prevent dissolution of brand-new entities before EMAs stabilize:

```python
MIN_AGE_FOR_DISSOLUTION_FRAMES = 1000  # ~100s at 100ms/tick

if entity.frames_since_creation < MIN_AGE_FOR_DISSOLUTION_FRAMES:
    return None  # Too young to dissolve
```

### Verification

After implementing:

1. Functional entities persist indefinitely (no dissolution events)
2. Quality scores for functional entities ≥ 0.5 on initial frames
3. Emergent/semantic entities still subject to lifecycle
4. No entities dissolve within first 1000 frames

**Observability:** Emit `subentity.lifecycle` events on state transitions (but **never** for functional entities).

---

## 5) Why Mechanism nodes are *not* for subentities

* `Mechanism` = algorithm/function (fields: how_it_works, inputs, outputs).
* A subentity like **The Translator** is a **mode/pattern**, not an algorithm.
* If you coded the bootstrap to "find Mechanism seeds", it will find nothing (and it shouldn't). That's the entire 0‑entities bug.

---

## 6) Minimal Path to Green (fix "0 entities" today)

**Goal:** Have active entities within 1–3 frames so Iris can render WM and beams — even **without** embeddings yet.

### Step A — Functional entities from config (no graph seeds needed)

Create `orchestration/config/functional_entities.yml`:

```yaml
entities:
  - key: translator
    name: "The Translator"
    kind: "functional"
    description: "Bridges phenomenology and technical structure."
    keywords:
      any: ["translate", "bridge", "phenomenology", "spec", "mapping"]
    initial_threshold_policy: "cohort_median_plus_mad"
  - key: architect
    name: "The Architect"
    kind: "functional"
    description: "Systematizes, designs schemas and flows."
    keywords:
      any: ["schema", "design", "architecture", "model", "systematize"]
  - key: validator
    name: "The Validator"
    kind: "functional"
    description: "Checks math, cohorts, event contracts."
    keywords:
      any: ["z-score", "cohort", "test", "validate", "schema"]
# add pragmatist, boundary_keeper, etc.
```

Update `entity_bootstrap.py`:

* **Do not** query for Mechanism nodes.
* Load config, **create Entity nodes** if missing (idempotent upsert).
* Seed **`BELONGS_TO`** memberships by **keyword matching** against node `name`/`description`:

  ```
  score_i,e = sigmoid( tf-idf(keyword hits) )  → normalize per node: Σ_e m_i,e ≤ 1
  ```
* If embeddings **are not present**, skip centroid computation for now; set `color` from key hash (temporary).
* Set `threshold_e` via cohort stats across functional entities (no constants).
* Persist. Emit `bootstrap.summary` log.

**Outcome:** You have **non‑zero entities** immediately, with memberships weak but serviceable. WM will start selecting them.

### Step B — Node embeddings (to unlock **semantic entities**)

* Ensure `embedding_service.py` runs and writes embeddings to nodes (idempotent; skip existing).
* Batch over content‑bearing nodes (Concept, Realization, Personal_Pattern, Document…).
* After embeddings exist → create **semantic entities** by clustering:

  * KMeans/HDBSCAN over embeddings **per scope**.
  * For each cluster: create `Entity(kind="semantic")`, compute centroid, color (OKLCH), and memberships (soft assignment by distance).
  * Create sparse `RELATES_TO` among semantic entities by centroid proximity or observed boundary flow later.

### Step C — Entity events & WM

* On each frame:

  * Recompute (or incrementally update) entity `energy` from members.
  * Flip detection → emit `entity.flip`.
  * Run WM **entity‑first** greedy selection → emit `wm.emit` including `selected_entities` & top members.
  * Aggregate cross‑entity strides → emit `entity.boundary.summary`.

**Acceptance (staging):**

* Within 3 frames after a stimulus:

  * `wm.emit.total_entities > 0`
  * `wm.emit.selected_entities.length ≥ 1`
  * Iris shows 5–7 entity bubbles and particles/beam summaries when boundary traffic occurs.

---

## 7) Data Model (what to store, briefly)

**Node**

* `energy` (dynamic), `threshold` (dynamic), `log_weight` (learned), `embedding` (when available), metadata.

**Link**

* `weight/log_weight` (learned), `energy` (**affect metadata**, 0–1), `flow_ema`, `phi_max`, precedence counts, timestamps.

**Entity**

* `kind` (`functional`|`semantic`), `name`, `color`, `centroid_embedding` (optional until available),
  `energy`, `threshold`, `log_weight`, `ema_wm_presence`, and **memberships** (`(node_id, membership_weight)`).

**Relations**

* `BELONGS_TO(node→entity){weight}`
* `RELATES_TO(entity↔entity){semantic_distance, precedence_ema, flow_ema, dominance}`

---

## 8) Traversal & Learning — the few formulas you need handy

**Entity energy:** `energy_e = Σ_i m_i,e · log1p( max(0, energy_i - threshold_i) )`
**Entity flip:** `active_e = 1[ energy_e ≥ threshold_e ]` (threshold by cohort stats)
**Representative nodes:** source: sample by `energy_i · m_i,e`; target: sample by `gap_i · m_i,e`
**Boundary precedence (s→t):**

```
γ_{s→t}(j) = (Σ ΔE_{i→j} from s)/gap_pre_j
Π_{s→t}    = Σ_j  m_{j,t} · γ_{s→t}(j)
EMA on RELATES_TO.precedence_ema with α learned/derived (no fixed constants)
```

---

## 9) Concrete next actions (owners & order)

**Today (to fix 0‑entities)**

1. **Remove Mechanism dependency** in `entity_bootstrap.py`. *(Felix)*
2. Add **config‑driven functional entities** + keyword seeding. *(Felix)*
3. Ensure bootstrap runs after graph load (you already added WS hooks — keep). *(Felix)*
4. In engine loop: compute entity `energy/threshold`, emit `entity.flip`, select WM entities, emit `wm.emit`. *(Felix)*
5. Iris: render bubbles from `wm.emit`; show beams from `entity.boundary.summary`. *(Iris)*

**Next (semantic entities)**
6) Run `embedding_service` over nodes; persist embeddings. *(Ada)*
7) Add clustering → create semantic entities + memberships + centroid/color. *(Ada)*
8) Start emitting `RELATES_TO` creation/updates as boundary evidence accumulates. *(Felix)*

**Docs**
9) Update `entity_layer/entity_layer.md` to state: **config‑first functional bootstrap; semantic via clustering when embeddings exist.** *(Marco)*
10) Remove any mention of Mechanism requirement; add migration note. *(Marco)*

---

## 10) FAQ (for the team)

**Q: Are subentities fixed lists?**
**A:** No. Entities are persistent neighborhoods; **sub‑entities** are the **active** ones this frame. Membership evolves slowly via learning; new semantic entities can appear via clustering.

**Q: Do nodes have energy per entity?**
**A:** No. One activation energy per node. Entities aggregate from members via membership weights.

**Q: How do we deactivate?**
**A:** Automatic — decay + redistribution pull node energies below thresholds; entity energy drops; they flip to inactive.

**Q: Why does `link.energy` exist if links don't carry energy?**
**A:** It's affect metadata (urgency/intensity theme) that influences **valence** (which edges feel attractive), not how much energy moves.

**Q: Why are entities required for WM?**
**A:** Working memory is **chunks** (5–7), not 50 atoms. Entities give coherent, scalable WM and reduce traversal branching by ~30–100×.

---

## 11) Minimal code sketch for config‑driven bootstrap

```python
# orchestration/mechanisms/entity_bootstrap.py

class EntityBootstrap:
    def __init__(self, graph, cfg):
        self.g = graph
        self.cfg = cfg  # parsed YAML with functional entities

    def run_complete_bootstrap(self):
        created = 0
        for e in self.cfg.entities:
            ent = self._upsert_entity(e)
            created += self._seed_memberships(ent, e.get("keywords", {}))
            self._seed_threshold(ent)
            self._seed_color(ent)
        return {"entities": len(self.g.entities), "memberships_seeded": created}

    def _upsert_entity(self, e):
        ent = self.g.get_entity_by_key(e["key"])
        if not ent:
            ent = self.g.create_entity(
                key=e["key"], name=e["name"], kind=e["kind"],
                description=e.get("description",""),
                log_weight=0.0, energy=0.0, threshold=0.0
            )
        return ent

    def _seed_memberships(self, ent, kw):
        hits = []
        for n in self.g.iter_nodes(types=["Concept","Realization","Personal_Pattern","Document"]):
            text = (n.name + " " + n.description).lower()
            score = self._keyword_score(text, kw)
            if score > 0:
                hits.append((n, score))
        if not hits: return 0
        # normalize per node across all entities later; here attach provisional
        for n, s in hits:
            w = self._squash(s)  # e.g., w = 1 - exp(-s)
            self.g.upsert_belongs_to(n.id, ent.id, weight=w)
        return len(hits)

    def _seed_threshold(self, ent):
        # After first frame, thresholds become cohort-based. Here set neutral.
        ent.threshold = 0.0

    def _seed_color(self, ent):
        # temp stable color from key; later recompute from centroid
        ent.color = stable_oklch_from_string(ent.key)

    def _keyword_score(self, text, kw):
        words = kw.get("any", [])
        return sum(1 for w in words if w in text)

    def _squash(self, s):  # simple monotone
        import math
        return 1 - math.exp(-s)
```

> **Important:** After this runs once, the engine loop should keep the entity layer alive (energy aggregation, flips, WM emit, boundary summaries). When embeddings arrive, add semantic entities in a second pass; don't block on them now.

---

**If you adopt the plan above, the "0 entities" problem is solved today** without touching Mechanism nodes, and the team has a crisp mental model to stop conflating "entities", "sub‑entities", and "mechanisms".

---

**Author:** Nicolas Le Roux (NLR)
**Date:** 2025-10-24
**Purpose:** Team field guide for v2 entity architecture and 0-entities bug fix
