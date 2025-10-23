---
title: Subentity Layer (Overview)
status: stable
owner: @luca
last_updated: 2025-10-22
supersedes:
  - ../consciousness_engine/mechanisms/05_sub_entity_system.md (overview & phenomenology)
  - ../consciousness_engine/mechanisms/ENTITY_LAYER_ADDENDUM.md (schema/energy/bootstrap)
depends_on:
  - ../foundations/multi_energy.md
  - ../runtime_engine/traversal_v2.md
  - ../ops_and_viz/observability_events.md
summary: >
  Subentities are weighted neighborhoods (functional roles or semantic topics)
  whose activation derives from member nodes’ single-node energies and membership
  weights. They enable two-scale traversal, entity-first working memory, and
  a tractable branching factor.
---

# Subentity Layer (Overview)

## 1. Context — What problem are we solving?

Atomic traversal over thousands of outgoing edges causes a combinatorial explosion and fails to match experience: people think and remember in **chunks** (topics/roles), not isolated nodes. We need a layer that:
- **Aggregates** meaning at the scale of neighborhoods (roles/topics),
- Provides a **two-scale traversal** (between subentities, then within),
- Anchors **Working Memory** (WM) in ~5–7 coherent chunks,
- Remains faithful to our **single-energy per node** substrate and avoids per-entity energy channels. :contentReference[oaicite:0]{index=0}

## 2. Mechanism (Design)

### 2.1 What is a subentity?

A **subentity** is a **weighted neighborhood** of nodes—either a **functional role** (e.g., Architect, Validator) or a **semantic topic** (e.g., consciousness_architecture). Members connect to the subentity with soft membership `BELONGS_TO.weight ∈ [0,1]`. :contentReference[oaicite:1]{index=1}

### 2.2 Single-energy substrate → entity activation

Nodes hold one activation energy \(E_i\). Subentity activation is **derived**, not stored:  
\[
E_\text{entity} = \sum_{i \in M_E} \tilde{m}_{iE} \cdot \max(0, E_i - \Theta_i)
\]
with normalized memberships \(\tilde{m}_{iE}\). This respects the **single-energy per node** rule (no per-entity buffers) and uses **effective** (above-threshold) node energy only. :contentReference[oaicite:2]{index=2}

### 2.3 Dynamic entity threshold & flip

Entity thresholds follow the same cohort logic as nodes (rolling mean/std over “touched this frame,” modulated by health). Flip occurs when \(E_\text{entity}\) crosses its \(\Theta_\text{entity}\). Emit `subentity.flip` on crossings. :contentReference[oaicite:3]{index=3}

### 2.4 Two-scale traversal

- **Between-entity:** pick target entity by 7-hunger valence at the entity level; select representative nodes for a boundary stride; learn **RELATES_TO** ease/dominance from boundary strides.  
- **Within-entity:** distribute budget over members and run atomic selection constrained to the entity neighborhood.  
Entity-scale selection drastically reduces branching before atomic moves. :contentReference[oaicite:4]{index=4}

### 2.5 Schema (essentials)

- **Subentity node:** fields for kind (`functional|semantic`), centroid embedding, coherence, and learning EMAs.  
- **BELONGS_TO (node→subentity):** soft membership `weight` learned from co-activation.  
- **RELATES_TO (subentity→subentity):** boundary ease (log-weight), dominance prior, semantic distance, counts. :contentReference[oaicite:5]{index=5}

## 3. Why this makes sense (three lenses)

### 3.1 Phenomenology (subentity feels like a growing pattern)

The layer captures the felt dynamics described in the original narrative: subentities grow, integrate with larger patterns, or dissolve when falling below threshold; **integration is continuation**, not “death,” and WM surfaces dominant neighborhoods rather than scattered atoms. :contentReference[oaicite:6]{index=6}

### 3.2 Human bio-inspiration

Neural assemblies and cortical columns suggest **population-level codes**; chunks/roles/topics are a pragmatic abstraction for control, consistent with “entity-first WM” and dynamic thresholds (attention-like gain).

### 3.3 Systems dynamics

- **Single energy per node** keeps the substrate conservative and simple; entities are **read-outs**.  
- **Type-dependent decay** maintains long-lived knowledge vs transient thoughts at the substrate, while entity aggregation rides on that substrate (no double-decay). :contentReference[oaicite:7]{index=7}  
- **Tick-speed regulation** aligns entity flips/WM updates with stimulus cadence. :contentReference[oaicite:8]{index=8}

## 4. Expected resulting behaviors

- **Reduced branching:** between-entity selection prunes 10–30× before atomic moves. :contentReference[oaicite:9]{index=9}  
- **Stable WM chunks:** WM holds 5–7 entities with summaries and top members. :contentReference[oaicite:10]{index=10}  
- **Natural integration:** small patterns merge into stronger, coherent ones (boundary beams increase). :contentReference[oaicite:11]{index=11}  
- **Phenomenological alignment:** focus/centering, peripheral pull, goal-consistent flow are visible in entity metrics. :contentReference[oaicite:12]{index=12}

## 5. Why this algorithm vs alternatives

- **Vs “every active node is a subentity”:** preserves the clarity that **subentity = neighborhood**, while still allowing any active node to participate via membership; avoids flooding WM with thousands of “micro-entities.” :contentReference[oaicite:13]{index=13}  
- **Vs per-entity energy channels:** would explode storage/compute and contradict the single-energy invariant; aggregation is cheaper and matches semantics. :contentReference[oaicite:14]{index=14}  
- **Vs clustering-only approach:** we retain **functional** entities and **learn** the graph’s semantics via **RELATES_TO** from boundary strides, not just static clusters. :contentReference[oaicite:15]{index=15}

## 6. Observability — how and what to measure

**Events.**  
- `subentity.flip` on crossings; payload: \(E\), \(\Theta\), activation_level.  
- `subentity.boundary.summary`: beams between entities (count, \(\sum\Delta E\), top hunger, \(\phi_{\max}\)).  
- `subentity.weights.updated` when entity-scale log-weights change. Event contract lives in the Viz WS spec. :contentReference[oaicite:16]{index=16}

**Derived metrics.**  
- **Entity vitality:** \(E/\Theta\).  
- **Coherence:** member similarity EMA.  
- **Integration index:** boundary \(\phi\) density into a target entity.  
- **Diversity (completeness) index:** semantic spread of member set.  
All are consumable via the snapshot + deltas WS contract. :contentReference[oaicite:17]{index=17}

## 7. Failure Modes & Guards

- **Entity creep (ever-growing memberships):** require periodic membership sparsification & floor on `BELONGS_TO.weight`. Guard: EMA-based pruning + minimum meaningful weight. :contentReference[oaicite:18]{index=18}  
- **Flip thrash:** add hysteresis around \(\Theta_\text{entity}\); guard with small ratio bands. :contentReference[oaicite:19]{index=19}  
- **Boundary noise:** only learn `RELATES_TO` on **executed** boundary strides with non-trivial \(\phi\). :contentReference[oaicite:20]{index=20}  
- **Over-chunked WM:** cap entity count for WM and score by energy-per-token and diversity bonus. :contentReference[oaicite:21]{index=21}

## 8. Integration points

- **Mechanisms:** `mechanisms/sub_entity_traversal.py` (two-scale selection & boundary stride accounting). :contentReference[oaicite:22]{index=22}  
- **Learning:** `entity_weight_learning` (BELONGS_TO updates); `RELATES_TO` ease/dominance from boundary stride outcomes. :contentReference[oaicite:23]{index=23}  
- **Runtime:** tick pacing from `tick_speed` (stimulus-paced). :contentReference[oaicite:24]{index=24}  
- **Observability:** WS contract & snapshot. :contentReference[oaicite:25]{index=25}

## 9. What success looks like

- WM shows 5–7 coherent entities with stable summaries (minutes), while atomic nodes churn faster.  
- Active-frontier traversal cost drops (fewer candidates per step), yet coverage & \(\phi\) improve across frames.  
- Boundary summaries reveal stable “entity highways” that correlate with successful TRACEs. :contentReference[oaicite:26]{index=26}

## 10. Open questions & future improvements

- Adaptive **promotion/demotion**: runtime → provisional → mature entity lifecycle thresholds. :contentReference[oaicite:27]{index=27}  
- Better **centroid drift** handling (hysteresis & palette stability). :contentReference[oaicite:28]{index=28}  
- Cross-entity **goal priors** (dominance learning schedules) from boundary statistics. :contentReference[oaicite:29]{index=29}
```

**Changes made (summary):**

* Rewrote “what is a subentity” to unambiguously mean a **weighted neighborhood**; removed implication that “any active node is itself a subentity” as the *primary* definition (still participates via membership). 
* Ensured **single-energy per node** is a hard invariant; entity energy is a **read-out** (no per-entity channels). 
* Added **two-scale traversal** articulation, WM policy, and boundary learning hooks with references to the WS contract. 
* Added **failure modes & guards**, success criteria, and explicit integration points across traversal, learning, tick speed, and viz. 
