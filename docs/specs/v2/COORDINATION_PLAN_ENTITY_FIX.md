# v2 SubEntity Layer Implementation - Coordination Plan

**Created:** 2025-10-24
**Coordinator:** Ada (Orchestration Architect)
**Based on:** Field Guide from Nicolas
**Status:** ACTIVE - Critical Path Execution

---

## Terminology Note

This specification references the two-scale architecture from **TAXONOMY_RECONCILIATION.md**:
- **Scale A: SubEntity Layer** - Weighted neighborhoods (200-500), semantic/functional clustering
- **Scale B: Mode Layer** - IFS-level meta-roles (5-15), emergent from COACTIVATES_WITH communities

See `subentity_layer.md` §2.1.1 for detailed architecture.

---

## Executive Summary

**Root Cause:** SubEntity bootstrap (entity_bootstrap.py) looks for Mechanism nodes to seed SubEntities. But Mechanism nodes represent algorithms (how_it_works/inputs/outputs) while SubEntities represent modes/patterns. Zero Mechanism nodes with "subentity" in name → zero SubEntities created.

**Fix:** Config-driven functional SubEntities + clustering-driven semantic SubEntities.

**Impact:** Unblocks SubEntity-first WM, two-scale traversal, boundary learning, visualization.

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

#### Item 2: Add Config-Driven Functional SubEntities
**New File:** `orchestration/config/functional_subentities.yml`

```yaml
subentities:
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
class SubEntityBootstrap:
    def __init__(self, graph, config_path="orchestration/config/functional_subentities.yml"):
        self.graph = graph
        self.config = self._load_config(config_path)

    def run_complete_bootstrap(self):
        """
        Bootstrap functional SubEntities from config.
        Returns stats dict for logging.
        """
        stats = {"subentities_created": 0, "memberships_seeded": 0}

        for subentity_def in self.config["subentities"]:
            # Upsert SubEntity (idempotent)
            subentity = self._upsert_subentity(subentity_def)
            stats["subentities_created"] += 1

            # Seed memberships via keyword matching
            count = self._seed_memberships(subentity, subentity_def.get("keywords", {}))
            stats["memberships_seeded"] += count

            # Initialize threshold (cohort-based after first frame)
            self._seed_threshold(subentity)

            # Generate stable color from key
            self._seed_color(subentity)

        # Normalize memberships (Σ_e m_{i,e} ≤ 1 per node)
        self._normalize_memberships()

        return stats

    def _seed_memberships(self, subentity, keywords):
        """
        Assign nodes to SubEntity based on keyword matching.

        Searches node name + description for keyword hits.
        Creates MEMBER_OF links with weights based on match score.
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

        # Create MEMBER_OF links
        for node, score in hits:
            weight = self._squash_score(score)  # 1 - exp(-score)
            self.graph.upsert_member_of(node.id, subentity.id, weight=weight)

        return len(hits)

    def _normalize_memberships(self):
        """
        Ensure Σ_e m_{i,e} ≤ 1 for each node.

        Normalize membership weights so total across all SubEntities doesn't exceed 1.
        This prevents nodes from being "over-committed" to multiple SubEntities.
        """
        node_totals = {}  # node_id -> sum of weights

        # Calculate totals
        for link in self.graph.links.values():
            if link.link_type == "MEMBER_OF":
                node_id = link.source
                node_totals[node_id] = node_totals.get(node_id, 0) + link.weight

        # Normalize if > 1
        for link in self.graph.links.values():
            if link.link_type == "MEMBER_OF":
                total = node_totals.get(link.source, 1.0)
                if total > 1.0:
                    link.weight = link.weight / total
```

#### Item 3: Bootstrap Runs After Graph Load
**File:** `orchestration/adapters/ws/websocket_server.py` (lines 402-418)
**Status:** Already implemented correctly
**Verify:** Bootstrap runs when `graph.subentities` is empty

#### Item 4: Engine Loop - SubEntity Energy & WM
**File:** `orchestration/mechanisms/consciousness_engine_v2.py`

**Add to tick() method:**

```python
# After Phase 1 (Activation) - compute SubEntity energy
for subentity in self.graph.subentities.values():
    # Aggregate energy from members
    energy_e = 0.0
    for node_id, membership in subentity.members.items():
        node = self.graph.get_node(node_id)
        if node:
            energy_e += membership * math.log1p(max(0, node.E - node.theta))

    subentity.energy_runtime = energy_e

    # Detect flip
    prev_active = subentity.active
    subentity.active = (energy_e >= subentity.threshold_runtime)

    if subentity.active != prev_active:
        # Emit subentity.flip event
        await self.broadcaster.broadcast_event("subentity.flip", {
            "v": "2",
            "frame_id": self.tick_count,
            "subentity_id": subentity.id,
            "energy": round(energy_e, 4),
            "threshold": round(subentity.threshold_runtime, 4),
            "active": subentity.active
        })

# Later in WM selection - SubEntity-first
selected_subentities = self._select_workspace_subentities()
await self.broadcaster.broadcast_event("wm.emit", {
    "v": "2",
    "frame_id": self.tick_count,
    "selected_subentities": selected_subentities,  # List of SubEntity IDs
    "total_subentities": len(self.graph.subentities)
})
```

**Acceptance Criteria:**
- Within 3 frames after stimulus: `wm.emit.total_subentities > 0`
- `wm.emit.selected_subentities.length >= 1`
- Telemetry shows `subentity.flip` events

---

### Phase 2: Visualization (Iris Item 5)

**Status:** BLOCKED by Phase 1
**Owner:** Iris (Visualization)
**Depends on:** Items 1-4 complete (needs SubEntities + events flowing)

**Tasks:**
- Render SubEntity bubbles from `wm.emit.selected_subentities`
- Show boundary beams from `subentity.boundary.summary` events
- SubEntity colors from subentity.color field
- Size/opacity from SubEntity energy/threshold ratio

---

### Phase 3: Semantic SubEntities (Ada Items 6-7)

**Status:** BLOCKED by Phase 1
**Owner:** Ada (Orchestration Architect)
**Depends on:** Functional SubEntities exist as foundation

#### Item 6: Embedding Service
**Goal:** Generate embeddings for content-bearing nodes

**Design:** See `docs/specs/v2/EMBEDDING_SERVICE_DESIGN.md` (to be created)

**Key Points:**
- Batch over Concept, Realization, Personal_Pattern, Document, Principle nodes
- Use existing embedding provider (check config)
- Idempotent (skip nodes that already have embeddings)
- Persist embeddings to node.embedding field
- Progress logging + metrics

#### Item 7: Semantic SubEntity Clustering
**Goal:** Create topic-based SubEntities from embedding clusters

**Design:** See `docs/specs/v2/SEMANTIC_SUBENTITY_CLUSTERING_DESIGN.md` (to be created)

**Key Points:**
- Cluster embeddings per scope (personal/organizational)
- Use HDBSCAN or KMeans with adaptive K
- Create SubEntity(kind="semantic") for each cluster
- Compute centroid embedding + OKLCH color
- Assign memberships by distance to centroid (soft assignment)
- Create sparse RELATES_TO between semantic SubEntities (by centroid proximity)

**Acceptance:**
- Semantic SubEntities appear in WM alongside functional SubEntities
- SubEntity colors stable and visually distinct
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
# Should show subentity.flip, wm.emit events

curl http://localhost:8000/api/consciousness/status
# Should show total_subentities > 0 for each citizen
```

**Verify via logs:**
```bash
grep "subentity_bootstrap" launcher.log
# Should show: created=5-8 subentities, memberships_seeded=50-200
```

**Verify via FalkorDB:**
```cypher
MATCH (e:SubEntity) RETURN e.key, e.kind, e.energy, e.threshold
MATCH ()-[r:MEMBER_OF]->(:SubEntity) RETURN count(r)
```

### After Phase 3 Complete:

**Verify semantic SubEntities:**
```cypher
MATCH (e:SubEntity {kind: "semantic"})
RETURN e.key, e.centroid_embedding, e.color
```

**Verify visualization:**
- Open Iris dashboard
- Should see 5-7 SubEntity bubbles in WM view
- Colors should be stable and distinct
- Boundary beams should appear when cross-SubEntity strides occur

---

## Risk Mitigation

### Risk 1: Config keywords don't match well
**Mitigation:** Start with broad keywords, refine after seeing membership distributions
**Fallback:** Manual membership assignment for critical SubEntities

### Risk 2: Semantic clustering produces too many/few SubEntities
**Mitigation:** Adaptive K selection based on elbow method + silhouette scores
**Fallback:** Manual cluster count parameter

### Risk 3: SubEntity thresholds too high/low
**Mitigation:** Use cohort statistics (median + k·MAD) computed per frame
**Guard:** Hysteresis to prevent flip thrashing

---

## Next Actions

**When server comes back up:**
1. Ada: Verify telemetry integration working (Option 1)
2. Ada: Check current SubEntity count in running engines
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
