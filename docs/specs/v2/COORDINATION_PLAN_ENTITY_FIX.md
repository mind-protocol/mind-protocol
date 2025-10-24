# v2 Entity Layer Fix - Coordination Plan

**Created:** 2025-10-24
**Coordinator:** Ada (Orchestration Architect)
**Based on:** Field Guide from Nicolas
**Status:** ACTIVE - Critical Path Execution

---

## Executive Summary

**Root Cause:** Entity bootstrap (entity_bootstrap.py) looks for Mechanism nodes to seed entities. But Mechanism nodes represent algorithms (how_it_works/inputs/outputs) while entities represent modes/patterns. Zero Mechanism nodes with "subentity" in name → zero entities created.

**Fix:** Config-driven functional entities + clustering-driven semantic entities.

**Impact:** Unblocks entity-first WM, two-scale traversal, boundary learning, visualization.

---

## Critical Path (Execute in Order)

### Phase 1: Bootstrap Fix (BLOCKING - Felix Items 1-4)

**Status:** PENDING - requires server up
**Owner:** Felix (Engineer)
**Blocks:** All downstream work

#### Item 1: Remove Mechanism Dependency
**File:** `orchestration/mechanisms/entity_bootstrap.py`
**Change:** Lines 92-124 currently search for Mechanism nodes with "subentity" in name
**Fix:** Remove this logic entirely

#### Item 2: Add Config-Driven Functional Entities
**New File:** `orchestration/config/functional_entities.yml`

```yaml
entities:
  - key: translator
    name: "The Translator"
    kind: "functional"
    description: "Bridges phenomenology and technical structure"
    keywords:
      any: ["translate", "bridge", "phenomenology", "spec", "mapping"]

  - key: architect
    name: "The Architect"
    kind: "functional"
    description: "Systematizes, designs schemas and flows"
    keywords:
      any: ["schema", "design", "architecture", "model", "systematize"]

  - key: validator
    name: "The Validator"
    kind: "functional"
    description: "Checks math, cohorts, event contracts"
    keywords:
      any: ["z-score", "cohort", "test", "validate", "schema"]

  - key: pragmatist
    name: "The Pragmatist"
    kind: "functional"
    description: "Focuses on utility, practical value"
    keywords:
      any: ["pragmatic", "practical", "utility", "serves", "elegant"]

  - key: boundary_keeper
    name: "The Boundary Keeper"
    kind: "functional"
    description: "Maintains domain boundaries, clarifies handoffs"
    keywords:
      any: ["boundary", "handoff", "domain", "blocks", "clarifies"]
```

**Update:** `entity_bootstrap.py`

```python
class EntityBootstrap:
    def __init__(self, graph, config_path="orchestration/config/functional_entities.yml"):
        self.graph = graph
        self.config = self._load_config(config_path)

    def run_complete_bootstrap(self):
        """
        Bootstrap functional entities from config.
        Returns stats dict for logging.
        """
        stats = {"entities_created": 0, "memberships_seeded": 0}

        for entity_def in self.config["entities"]:
            # Upsert entity (idempotent)
            entity = self._upsert_entity(entity_def)
            stats["entities_created"] += 1

            # Seed memberships via keyword matching
            count = self._seed_memberships(entity, entity_def.get("keywords", {}))
            stats["memberships_seeded"] += count

            # Initialize threshold (cohort-based after first frame)
            self._seed_threshold(entity)

            # Generate stable color from key
            self._seed_color(entity)

        # Normalize memberships (Σ_e m_{i,e} ≤ 1 per node)
        self._normalize_memberships()

        return stats

    def _seed_memberships(self, entity, keywords):
        """
        Assign nodes to entity based on keyword matching.

        Searches node name + description for keyword hits.
        Creates BELONGS_TO links with weights based on match score.
        """
        keyword_list = keywords.get("any", [])
        if not keyword_list:
            return 0

        hits = []
        for node in self.graph.nodes.values():
            # Search in content-bearing nodes only
            if node.node_type not in ["Concept", "Realization", "Personal_Pattern",
                                      "Document", "Principle", "Mechanism"]:
                continue

            text = (node.name + " " + node.description).lower()
            score = sum(1 for kw in keyword_list if kw.lower() in text)

            if score > 0:
                hits.append((node, score))

        # Create BELONGS_TO links
        for node, score in hits:
            weight = self._squash_score(score)  # 1 - exp(-score)
            self.graph.upsert_belongs_to(node.id, entity.id, weight=weight)

        return len(hits)

    def _normalize_memberships(self):
        """
        Ensure Σ_e m_{i,e} ≤ 1 for each node.

        Normalize membership weights so total across all entities doesn't exceed 1.
        This prevents nodes from being "over-committed" to multiple entities.
        """
        node_totals = {}  # node_id -> sum of weights

        # Calculate totals
        for link in self.graph.links.values():
            if link.link_type == "BELONGS_TO":
                node_id = link.source
                node_totals[node_id] = node_totals.get(node_id, 0) + link.weight

        # Normalize if > 1
        for link in self.graph.links.values():
            if link.link_type == "BELONGS_TO":
                total = node_totals.get(link.source, 1.0)
                if total > 1.0:
                    link.weight = link.weight / total
```

#### Item 3: Bootstrap Runs After Graph Load
**File:** `orchestration/adapters/ws/websocket_server.py` (lines 402-418)
**Status:** Already implemented correctly
**Verify:** Bootstrap runs when `graph.subentities` is empty

#### Item 4: Engine Loop - Entity Energy & WM
**File:** `orchestration/mechanisms/consciousness_engine_v2.py`

**Add to tick() method:**

```python
# After Phase 1 (Activation) - compute entity energy
for entity in self.graph.subentities.values():
    # Aggregate energy from members
    energy_e = 0.0
    for node_id, membership in entity.members.items():
        node = self.graph.get_node(node_id)
        if node:
            energy_e += membership * math.log1p(max(0, node.E - node.theta))

    entity.energy_runtime = energy_e

    # Detect flip
    prev_active = entity.active
    entity.active = (energy_e >= entity.threshold_runtime)

    if entity.active != prev_active:
        # Emit entity.flip event
        await self.broadcaster.broadcast_event("entity.flip", {
            "v": "2",
            "frame_id": self.tick_count,
            "entity_id": entity.id,
            "energy": round(energy_e, 4),
            "threshold": round(entity.threshold_runtime, 4),
            "active": entity.active
        })

# Later in WM selection - entity-first
selected_entities = self._select_workspace_entities()
await self.broadcaster.broadcast_event("wm.emit", {
    "v": "2",
    "frame_id": self.tick_count,
    "selected_entities": selected_entities,  # List of entity IDs
    "total_entities": len(self.graph.subentities)
})
```

**Acceptance Criteria:**
- Within 3 frames after stimulus: `wm.emit.total_entities > 0`
- `wm.emit.selected_entities.length >= 1`
- Telemetry shows `entity.flip` events

---

### Phase 2: Visualization (Iris Item 5)

**Status:** BLOCKED by Phase 1
**Owner:** Iris (Visualization)
**Depends on:** Items 1-4 complete (needs entities + events flowing)

**Tasks:**
- Render entity bubbles from `wm.emit.selected_entities`
- Show boundary beams from `entity.boundary.summary` events
- Entity colors from entity.color field
- Size/opacity from entity energy/threshold ratio

---

### Phase 3: Semantic Entities (Ada Items 6-7)

**Status:** BLOCKED by Phase 1
**Owner:** Ada (Orchestration Architect)
**Depends on:** Functional entities exist as foundation

#### Item 6: Embedding Service
**Goal:** Generate embeddings for content-bearing nodes

**Design:** See `docs/specs/v2/EMBEDDING_SERVICE_DESIGN.md` (to be created)

**Key Points:**
- Batch over Concept, Realization, Personal_Pattern, Document, Principle nodes
- Use existing embedding provider (check config)
- Idempotent (skip nodes that already have embeddings)
- Persist embeddings to node.embedding field
- Progress logging + metrics

#### Item 7: Semantic Entity Clustering
**Goal:** Create topic-based entities from embedding clusters

**Design:** See `docs/specs/v2/SEMANTIC_ENTITY_CLUSTERING_DESIGN.md` (to be created)

**Key Points:**
- Cluster embeddings per scope (personal/organizational)
- Use HDBSCAN or KMeans with adaptive K
- Create Entity(kind="semantic") for each cluster
- Compute centroid embedding + OKLCH color
- Assign memberships by distance to centroid (soft assignment)
- Create sparse RELATES_TO between semantic entities (by centroid proximity)

**Acceptance:**
- Semantic entities appear in WM alongside functional entities
- Entity colors stable and visually distinct
- Memberships sum to ≤ 1 per node

---

### Phase 4: Documentation (Marco Items 9-10)

**Status:** CAN RUN IN PARALLEL
**Owner:** Marco (Documentation)

**Tasks:**
1. Update `docs/specs/v2/subentity_layer/subentity_layer.md`
   - Add section: "Bootstrap: Config-First Functional + Clustering Semantic"
   - Remove any Mechanism node dependency mentions
   - Add migration note for existing systems

2. Add migration guide for teams hitting 0-entities bug
   - Explain Mechanism confusion
   - Point to functional_entities.yml config
   - Explain keyword seeding strategy

---

## Integration Points & Verification

### After Phase 1 Complete:

**Verify via telemetry:**
```bash
curl http://localhost:8000/api/affective-telemetry/metrics
# Should show entity.flip, wm.emit events

curl http://localhost:8000/api/consciousness/status
# Should show total_entities > 0 for each citizen
```

**Verify via logs:**
```bash
grep "entity_bootstrap" launcher.log
# Should show: created=5-8 entities, memberships_seeded=50-200
```

**Verify via FalkorDB:**
```cypher
MATCH (e:Entity) RETURN e.key, e.kind, e.energy, e.threshold
MATCH ()-[r:BELONGS_TO]->(:Entity) RETURN count(r)
```

### After Phase 3 Complete:

**Verify semantic entities:**
```cypher
MATCH (e:Entity {kind: "semantic"})
RETURN e.key, e.centroid_embedding, e.color
```

**Verify visualization:**
- Open Iris dashboard
- Should see 5-7 entity bubbles in WM view
- Colors should be stable and distinct
- Boundary beams should appear when cross-entity strides occur

---

## Risk Mitigation

### Risk 1: Config keywords don't match well
**Mitigation:** Start with broad keywords, refine after seeing membership distributions
**Fallback:** Manual membership assignment for critical entities

### Risk 2: Semantic clustering produces too many/few entities
**Mitigation:** Adaptive K selection based on elbow method + silhouette scores
**Fallback:** Manual cluster count parameter

### Risk 3: Entity thresholds too high/low
**Mitigation:** Use cohort statistics (median + k·MAD) computed per frame
**Guard:** Hysteresis to prevent flip thrashing

---

## Next Actions

**When server comes back up:**
1. Ada: Verify telemetry integration working (Option 1)
2. Ada: Check current entity count in running engines
3. Ada: Coordinate Felix start on Items 1-4
4. Felix: Execute Phase 1 (Items 1-4)
5. Team: Verify acceptance criteria
6. Iris: Execute Phase 2 (Item 5)
7. Ada: Execute Phase 3 (Items 6-7)
8. Marco: Execute Phase 4 (Items 9-10)

---

**Coordinator:** Ada "Bridgekeeper"
**Status:** Server down - waiting for infrastructure
**Next Check:** Server status every 5 minutes
