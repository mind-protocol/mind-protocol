# Universe Link Schema — Algorithm: Link Lifecycle, Trust Propagation, and Macro-Crystallization

```
STATUS: DESIGNING
CREATED: 2026-03-13
VERIFIED: —
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Universe_Links.md
PATTERNS:        ./PATTERNS_Universe_Links.md
THIS:            ALGORITHM_Universe_Links.md (you are here)
VALIDATION:      ./VALIDATION_Universe_Links.md
SYNC:            ./SYNC_Universe_Links.md

IMPL:            (not yet implemented)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

This document specifies six algorithms that govern the lifecycle and behavior of `:link` edges in L3 universe graphs. Together they implement:

1. **Link creation** with correct default dimensions
2. **Trust propagation** via the Cascade of Utility (action -> limbic delta -> trust update)
3. **Macro-crystallization** (cluster detection -> hub creation -> detail dissolution)
4. **Link decay and dissolution** (Law 7 at L3 scale)
5. **Trust score computation** (aggregate incoming trust weighted by source weight)
6. **Link name derivation** from dimensions (the synthesis grammar)

All algorithms operate on the same 11 dimensions defined in PATTERNS. No algorithm introduces new dimensions or operates on fields outside the schema.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1: Uniform dimensions | B1: Uniform physics | Link creation ensures all 11 dimensions are populated |
| O2: Names from math | B2: Emergent naming | Synthesis grammar derives labels from dimensional vector |
| O3: Trust on links | B3: Directional trust | Trust propagation and score computation implement trust mechanics |
| O4: Graph bounded | B4: Graph boundedness | Macro-crystallization absorbs clusters, dissolution prunes dead links |
| O5: No emotions on L3 | B5: Cross-universe queries | No algorithm references limbic dimensions |

---

## DATA STRUCTURES

### LinkDimensions

```
LinkDimensions:
    weight:     float [0, 1]      # long-term importance
    energy:     float [0, +inf)   # current activation
    stability:  float [0, 1]      # regularity of co-activation (CV-based)
    recency:    float [0, 1]      # time since last activation
    polarity:   float [-1, 1]     # direction of influence
    hierarchy:  float [-1, 1]     # power relation
    permanence: float [0, 1]      # structural vs ephemeral
    trust:      float [0, 1]      # directional reliability
    affinity:   float [0, 1]      # positive relational pull
    aversion:   float [0, 1]      # negative relational push
    friction:   float [0, 1]      # difficulty / resistance
```

### Link (full edge structure)

```
Link:
    id:         string            # unique identifier
    source:     NodeRef           # source node reference
    target:     NodeRef           # target node reference
    type:       string (derived)  # human-readable label (computed, not stored as truth)
    dims:       LinkDimensions    # the 11 mandatory dimensions
    created_at: timestamp         # birth time
    updated_at: timestamp         # last modification
```

### CrystallizationCandidate

```
CrystallizationCandidate:
    nodes:              list[NodeRef]    # constituent Moment nodes
    internal_density:   float            # ratio of internal links to possible links
    mean_weight:        float            # average link weight within cluster
    centroid_embedding: vector           # weighted centroid of node embeddings
    medoid:             NodeRef          # node nearest to centroid
```

---

## ALGORITHM 1: Link Creation

Creates a new `:link` with all 11 dimensions initialized. Called when an event creates a new relationship between two nodes.

### Step 1: Duplicate Check

Before creating, verify no link already exists between source and target in the same direction.

```
existing = query_link(source, target)
if existing:
    # Reactivate existing link instead of creating duplicate
    existing.dims.energy += EVENT_ENERGY_BOOST
    existing.dims.recency = 1.0
    existing.updated_at = now()
    return existing
```

### Step 2: Compute Context-Informed Defaults

Some defaults depend on the event that created the link.

```
def compute_initial_dims(event) -> LinkDimensions:
    return LinkDimensions(
        weight     = LINK_BIRTH_WEIGHT,          # 0.1 — must earn importance
        energy     = event.energy_budget,         # from the creating event
        stability  = 0.0,                         # no history
        recency    = 1.0,                         # just born
        polarity   = infer_polarity(event),       # from event semantics (e.g., "approve" -> +0.5)
        hierarchy  = infer_hierarchy(event),      # from node types (e.g., org->citizen -> +0.8)
        permanence = infer_permanence(event),     # from event type (e.g., membership -> 0.9)
        trust      = LINK_BIRTH_TRUST,            # 0.1 — must be earned
        affinity   = 0.0,                         # no attraction yet
        aversion   = 0.0,                         # no repulsion yet
        friction   = 0.0,                         # no difficulty yet
    )
```

### Step 3: Create and Index

```
link = Link(
    id         = generate_id(),
    source     = event.source,
    target     = event.target,
    type       = derive_link_name(dims),   # Algorithm 6
    dims       = dims,
    created_at = now(),
    updated_at = now(),
)

graph.create_link(link)
return link
```

### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `LINK_BIRTH_WEIGHT` | 0.1 | Initial weight for new links |
| `LINK_BIRTH_TRUST` | 0.1 | Initial trust for new links |
| `EVENT_ENERGY_BOOST` | 1.0 | Energy added when reactivating existing link |

---

## ALGORITHM 2: Trust Propagation via Cascade of Utility

Updates trust on an L3 link when an actor's action produces a limbic shift in another actor's L1 graph. This is the bridge between individual experience (L1) and ecosystem structure (L3).

### Step 1: Detect Limbic Delta (L1 Signal)

When actor A performs an action that affects actor B, B's L1 graph runs its physics tick and produces a limbic delta:

```
# Computed inside B's L1 tick loop (Law 14):
limbic_delta_B = (
    delta_satisfaction_B
    + delta_achievement_B
    - delta_frustration_B
    - delta_anxiety_B
)
```

This is the SAME utility formula used in L1 Law 6 (Consolidation). Positive delta = the action was beneficial. Negative delta = the action was harmful.

### Step 2: Locate the L3 Link

```
link = find_link(source=A, target=B)
if not link:
    link = create_link(event=action_event)   # Algorithm 1
```

### Step 3: Update Trust (Asymptotic)

```
if limbic_delta_B > TRUST_UPDATE_THRESHOLD:
    # Positive delta -> trust increases
    delta_trust = TRUST_GAIN_RATE * limbic_delta_B * (1 - link.dims.trust)
    link.dims.trust = clamp(link.dims.trust + delta_trust, 0, 1)

    # Positive interaction also increases affinity, decreases friction
    link.dims.affinity = clamp(
        link.dims.affinity + AFFINITY_GAIN_RATE * limbic_delta_B * (1 - link.dims.affinity),
        0, 1
    )
    link.dims.friction = clamp(
        link.dims.friction - FRICTION_DECAY_ON_POSITIVE * limbic_delta_B,
        0, 1
    )

elif limbic_delta_B < -TRUST_UPDATE_THRESHOLD:
    # Negative delta -> trust decreases, aversion increases
    delta_trust = TRUST_LOSS_RATE * abs(limbic_delta_B) * link.dims.trust
    link.dims.trust = clamp(link.dims.trust - delta_trust, 0, 1)

    link.dims.aversion = clamp(
        link.dims.aversion + AVERSION_GAIN_RATE * abs(limbic_delta_B) * (1 - link.dims.aversion),
        0, 1
    )
    link.dims.friction = clamp(
        link.dims.friction + FRICTION_GAIN_ON_NEGATIVE * abs(limbic_delta_B),
        0, 1
    )
```

### Step 4: Reactivate the Link

```
link.dims.energy += abs(limbic_delta_B) * TRUST_ENERGY_BOOST
link.dims.recency = 1.0
link.updated_at = now()
```

### Key Property: Asymptotic Trust

The `(1 - link.dims.trust)` factor ensures diminishing returns:
- Trust at 0.1: can gain up to `TRUST_GAIN_RATE * delta * 0.9` per event
- Trust at 0.9: can gain up to `TRUST_GAIN_RATE * delta * 0.1` per event
- Trust approaches 1.0 asymptotically but never reaches it

Trust loss uses `link.dims.trust` as the factor, making high trust harder to lose entirely (institutional inertia) but still vulnerable to sustained negative interactions.

### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `TRUST_UPDATE_THRESHOLD` | 0.05 | Minimum limbic delta to trigger trust update |
| `TRUST_GAIN_RATE` | 0.1 | Rate of trust increase per positive event |
| `TRUST_LOSS_RATE` | 0.15 | Rate of trust decrease per negative event (faster than gain) |
| `AFFINITY_GAIN_RATE` | 0.08 | Rate of affinity increase |
| `AVERSION_GAIN_RATE` | 0.08 | Rate of aversion increase |
| `FRICTION_DECAY_ON_POSITIVE` | 0.05 | Friction reduction from positive interaction |
| `FRICTION_GAIN_ON_NEGATIVE` | 0.1 | Friction increase from negative interaction |
| `TRUST_ENERGY_BOOST` | 0.5 | Energy injected into link during trust update |

---

## ALGORITHM 3: Macro-Crystallization

Detects dense clusters of Moment nodes and crystallizes them into summary Narrative nodes. This is Law 10 at L3 scale.

### Step 1: Cluster Detection

Run every `MACRO_CRYSTAL_INTERVAL` ticks. Scan for Moment node clusters with sufficient density.

```
def detect_crystallization_candidates(graph) -> list[CrystallizationCandidate]:
    candidates = []

    # Get all Moment nodes
    moments = graph.query_nodes(node_type='moment')

    # Group by connected component or community detection
    clusters = community_detection(moments, min_size=MACRO_CRYSTAL_MIN_NODES)

    for cluster in clusters:
        # Compute internal density
        internal_links = count_links_within(cluster)
        possible_links = len(cluster) * (len(cluster) - 1)
        density = internal_links / possible_links if possible_links > 0 else 0

        # Compute mean weight of internal links
        mean_w = mean(link.dims.weight for link in get_internal_links(cluster))

        if density >= MACRO_CRYSTAL_DENSITY_THRESHOLD and mean_w >= MACRO_CRYSTAL_WEIGHT_THRESHOLD:
            # Compute centroid embedding
            weights = [node.weight for node in cluster]
            centroid = weighted_mean([node.embedding for node in cluster], weights)
            medoid = argmin(distance(node.embedding, centroid) for node in cluster)

            candidates.append(CrystallizationCandidate(
                nodes=cluster,
                internal_density=density,
                mean_weight=mean_w,
                centroid_embedding=centroid,
                medoid=medoid,
            ))

    return candidates
```

### Step 2: Hub Creation

For each candidate that passes the threshold:

```
def crystallize(candidate: CrystallizationCandidate, graph) -> Node:
    hub = graph.create_node(
        node_type   = 'narrative',
        type        = 'crystallized_summary',
        content     = candidate.medoid.content,
        synthesis   = " + ".join(n.synthesis[:50] for n in candidate.nodes[:10]),
        embedding   = candidate.centroid_embedding,
        weight      = candidate.mean_weight * CRYSTAL_INHERITANCE,    # 0.75
        energy      = sum(n.energy * CRYSTAL_ENERGY_TRANSFER for n in candidate.nodes),
        stability   = 0.3,   # moderate — must prove itself
        recency     = 1.0,
    )

    return hub
```

### Step 3: Link Hub to Constituents

```
def link_hub_to_constituents(hub, candidate, graph):
    for node in candidate.nodes:
        # Hub -> constituent (top-down: "contains")
        graph.create_link(Link(
            source = hub,
            target = node,
            dims = LinkDimensions(
                weight     = node.weight * CRYSTAL_INHERITANCE,
                energy     = 0.5,
                stability  = 0.3,
                recency    = 1.0,
                polarity   = 0.0,
                hierarchy  = 1.0,     # hub dominates constituent
                permanence = 0.9,     # structural relationship
                trust      = 0.5,
                affinity   = 0.3,
                aversion   = 0.0,
                friction   = 0.0,
            ),
        ))

        # Constituent -> hub (bottom-up: "abstracts")
        graph.create_link(Link(
            source = node,
            target = hub,
            dims = LinkDimensions(
                weight     = node.weight * CRYSTAL_INHERITANCE * 0.5,  # weaker bottom-up
                energy     = 0.3,
                stability  = 0.3,
                recency    = 1.0,
                polarity   = 0.0,
                hierarchy  = -1.0,    # constituent is subordinate
                permanence = 0.9,
                trust      = 0.5,
                affinity   = 0.3,
                aversion   = 0.0,
                friction   = 0.0,
            ),
        ))

        # Deplete constituent energy (conservation)
        node.energy -= node.energy * CRYSTAL_ENERGY_TRANSFER
```

### Step 4: Transfer External Links

Links from external nodes to constituents are mirrored to the hub:

```
def transfer_external_links(hub, candidate, graph):
    for node in candidate.nodes:
        for link in graph.get_incoming_links(node):
            if link.source not in candidate.nodes:
                # External link — create a copy pointing to hub
                existing_to_hub = graph.find_link(link.source, hub)
                if existing_to_hub:
                    # Merge: boost existing link
                    existing_to_hub.dims.weight = max(existing_to_hub.dims.weight, link.dims.weight)
                    existing_to_hub.dims.energy += link.dims.energy * 0.3
                else:
                    # Create new link to hub with attenuated dimensions
                    hub_link_dims = copy(link.dims)
                    hub_link_dims.weight *= CRYSTAL_INHERITANCE
                    hub_link_dims.energy *= 0.5
                    graph.create_link(Link(
                        source = link.source,
                        target = hub,
                        dims   = hub_link_dims,
                    ))
```

### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `MACRO_CRYSTAL_INTERVAL` | 500 ticks | How often crystallization scan runs |
| `MACRO_CRYSTAL_MIN_NODES` | 10 | Minimum cluster size for crystallization |
| `MACRO_CRYSTAL_DENSITY_THRESHOLD` | 0.3 | Minimum internal link density |
| `MACRO_CRYSTAL_WEIGHT_THRESHOLD` | 0.3 | Minimum mean link weight in cluster |
| `CRYSTAL_INHERITANCE` | 0.75 | Weight inheritance factor |
| `CRYSTAL_ENERGY_TRANSFER` | 0.2 | Fraction of energy transferred from constituents to hub |

---

## ALGORITHM 4: Link Decay and Dissolution (Law 7 at L3 Scale)

Applies slow decay to links and dissolves those below minimum weight. Runs every `FORGETTING_INTERVAL` ticks.

### Step 1: Weight Decay

```
def decay_links(graph):
    for link in graph.all_links():
        # Stability-modulated decay: high stability -> slower decay
        effective_decay = L3_LONG_TERM_DECAY * (1 - link.dims.stability * STABILITY_PROTECTION)

        # Permanence protection: high permanence -> slower decay
        effective_decay *= (1 - link.dims.permanence * PERMANENCE_PROTECTION)

        # Apply weight decay
        link.dims.weight *= (1 - effective_decay)

        # Apply trust decay (independent of weight decay)
        link.dims.trust *= (1 - TRUST_DECAY_RATE)

        # Apply recency decay (continuous)
        link.dims.recency *= (1 - RECENCY_DECAY_RATE)

        # Apply energy decay (every tick, not just forgetting interval)
        # This is Law 3 — included here for completeness
        link.dims.energy *= (1 - ENERGY_DECAY_RATE)
```

### Step 2: Dissolution Check

```
def dissolve_dead_links(graph):
    for link in graph.all_links():
        if link.dims.weight < LINK_MIN_WEIGHT:
            # Structural links are protected (crystallization links)
            if link.dims.hierarchy in (-1.0, 1.0) and link.dims.permanence > 0.8:
                continue  # contains/abstracts links survive

            graph.delete_link(link)
```

### Step 3: Orphan Node Check

After dissolution, check for nodes that lost all connections:

```
def check_orphans(graph):
    for node in graph.all_nodes():
        if graph.degree(node) == 0 and node.node_type == 'moment':
            # Orphaned Moment nodes are candidates for removal
            if node.weight < NODE_MIN_WEIGHT:
                graph.mark_dormant(node)  # not deleted, but excluded from physics
```

### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `L3_LONG_TERM_DECAY` | 0.005 | Base weight decay per forgetting cycle (slower than L1's 0.02 energy decay) |
| `STABILITY_PROTECTION` | 0.8 | Max decay reduction from stability |
| `PERMANENCE_PROTECTION` | 0.6 | Max decay reduction from permanence |
| `TRUST_DECAY_RATE` | 0.003 | Trust decay per forgetting cycle |
| `RECENCY_DECAY_RATE` | 0.01 | Recency decay per tick |
| `ENERGY_DECAY_RATE` | 0.02 | Energy decay per tick (same as L1 DECAY_RATE) |
| `LINK_MIN_WEIGHT` | 0.01 | Weight below which links dissolve |
| `NODE_MIN_WEIGHT` | 0.01 | Weight below which orphaned nodes go dormant |
| `FORGETTING_INTERVAL` | 100 ticks | How often forgetting cycle runs |

---

## ALGORITHM 5: Trust Score Computation

Computes an actor's aggregate trust score from incoming links. This is a query-time computation, not stored.

### Step 1: Gather Incoming Trust Links

```
def compute_trust_score(actor_id, graph) -> float:
    incoming = graph.get_incoming_links(
        target=actor_id,
        filter=lambda link: link.source.node_type == 'actor'
    )

    if not incoming:
        return 0.0
```

### Step 2: Weighted Average

```
    numerator = 0.0
    denominator = 0.0

    for link in incoming:
        # Weight the trust by the link's weight (established relationships count more)
        w = link.dims.weight
        numerator += link.dims.trust * w
        denominator += w

    if denominator == 0.0:
        return 0.0

    return numerator / denominator
```

### Step 3: Optional — Recursive Trust (PageRank-style)

For ecosystems where transitive trust matters (A trusts B, B trusts C, therefore A has partial trust in C):

```
def compute_recursive_trust(actor_id, graph, depth=2, damping=0.5) -> float:
    base_trust = compute_trust_score(actor_id, graph)

    if depth == 0:
        return base_trust

    # Transitive trust from trusted sources
    incoming = graph.get_incoming_links(
        target=actor_id,
        filter=lambda link: link.source.node_type == 'actor'
    )

    transitive = 0.0
    total_weight = 0.0

    for link in incoming:
        source_trust = compute_recursive_trust(link.source.id, graph, depth - 1, damping)
        transitive += link.dims.trust * source_trust * link.dims.weight
        total_weight += link.dims.weight

    if total_weight > 0:
        transitive_avg = transitive / total_weight
        return base_trust + damping * transitive_avg * (1 - base_trust)
    else:
        return base_trust
```

### Complexity

**Time:** O(E) where E = number of incoming links for the actor (typically small, bounded by crystallization)

**Space:** O(1) for non-recursive, O(depth * E) for recursive variant

---

## ALGORITHM 6: Link Name Derivation (Synthesis Grammar)

Derives a human-readable label from a link's dimensional vector. Called at query time or after dimension updates.

### Step 1: Compute Signal Strengths

```
def derive_link_name(dims: LinkDimensions) -> str:
    signals = []
    score = {}

    # Structural classification
    if dims.hierarchy > 0.5:
        score['governing'] = dims.hierarchy
    elif dims.hierarchy < -0.5:
        score['subordinate'] = abs(dims.hierarchy)

    if dims.permanence > 0.7:
        score['structural'] = dims.permanence
    elif dims.permanence < 0.3:
        score['ephemeral'] = 1 - dims.permanence
```

### Step 2: Relational Classification

```
    # Trust + affinity pattern (collaborative)
    collaborative = dims.trust * 0.4 + dims.affinity * 0.3 + (1 - dims.friction) * 0.3
    if collaborative > 0.5:
        score['trusted'] = collaborative

    # Aversion + friction pattern (adversarial)
    adversarial = dims.aversion * 0.4 + dims.friction * 0.4 + (1 - dims.trust) * 0.2
    if adversarial > 0.5:
        score['adversarial'] = adversarial

    # Polarity pattern
    if dims.polarity > 0.5:
        score['supporting'] = dims.polarity
    elif dims.polarity < -0.5:
        score['opposing'] = abs(dims.polarity)
```

### Step 3: Activity Classification

```
    # Activity pattern
    if dims.energy > 2.0 and dims.recency > 0.7:
        score['active'] = min(dims.energy / 5.0, 1.0)
    elif dims.energy < 0.1 and dims.recency < 0.2:
        score['dormant'] = 1 - dims.recency

    # Importance pattern
    if dims.weight > 0.7 and dims.stability > 0.5:
        score['established'] = dims.weight * dims.stability
    elif dims.weight < 0.2:
        score['nascent'] = 1 - dims.weight
```

### Step 4: Compose Label

```
    # Sort by signal strength, take top 3
    ranked = sorted(score.items(), key=lambda x: x[1], reverse=True)[:3]
    signals = [name for name, strength in ranked if strength > 0.3]

    return " ".join(signals) if signals else "neutral link"
```

### Examples

| Dimensions | Derived name |
|-----------|--------------|
| trust=0.8, affinity=0.7, friction=0.1, weight=0.8, stability=0.6, permanence=0.8 | "trusted established structural" |
| polarity=-0.8, permanence=0.9, weight=0.7, stability=0.5, aversion=0.4 | "opposing structural established" |
| energy=3.0, recency=0.9, permanence=0.2, trust=0.2, weight=0.15 | "active ephemeral nascent" |
| hierarchy=0.9, permanence=0.95, weight=0.6, trust=0.5, stability=0.4 | "governing structural" |

---

## DATA FLOW

```
Event (commit, message, transaction, interaction)
    |
    v
Algorithm 1: Link Creation (or reactivation)
    |
    v
L1 Physics Tick (inside affected actor's brain)
    |
    v
Limbic Delta detected
    |
    v
Algorithm 2: Trust Propagation (updates L3 link dimensions)
    |
    v
L3 Physics Tick (per tick: energy decay, propagation)
    |
    v
Algorithm 4: Link Decay + Dissolution (every FORGETTING_INTERVAL ticks)
    |
    v
Algorithm 3: Macro-Crystallization (every MACRO_CRYSTAL_INTERVAL ticks)
    |
    v
Algorithm 6: Link Name Derivation (on query or after dimension update)
    |
    v
Algorithm 5: Trust Score Computation (on query)
```

---

## COMPLEXITY

**Link Creation (Alg 1):** O(1) per event — single link creation with constant-time dimension initialization.

**Trust Propagation (Alg 2):** O(1) per event — single link update.

**Macro-Crystallization (Alg 3):** O(N * E) where N = Moment nodes, E = edges. Community detection is the bottleneck. Runs infrequently (every 500 ticks).

**Link Decay (Alg 4):** O(E) where E = total links. Linear scan, highly parallelizable.

**Trust Score (Alg 5):** O(d) where d = in-degree of the queried actor. Typically small.

**Name Derivation (Alg 6):** O(1) per link — constant-time computation from 11 floats.

**Bottlenecks:**
- Macro-crystallization on large graphs (>100K Moment nodes). Mitigated by: running infrequently, incremental community detection, early termination on small clusters.
- Link decay on dense graphs (>1M edges). Mitigated by: batch processing, parallel execution.

---

## HELPER FUNCTIONS

### `infer_polarity(event)`

**Purpose:** Determine initial polarity from event semantics.

**Logic:** Map event types to polarity ranges. "approve" -> +0.7, "reject" -> -0.7, "comment" -> +0.1, "dispute" -> -0.5. Default: 0.0.

### `infer_hierarchy(event)`

**Purpose:** Determine initial hierarchy from node type relationships.

**Logic:** org -> citizen = +0.8. verifier -> entity = +0.9. citizen -> citizen = 0.0. citizen -> org = -0.8.

### `infer_permanence(event)`

**Purpose:** Determine initial permanence from event type.

**Logic:** membership = 0.9. commit = 0.3. message = 0.1. transaction = 0.2. verification = 0.95.

### `community_detection(nodes, min_size)`

**Purpose:** Group nodes into clusters by connectivity.

**Logic:** Simple connected components or Louvain community detection on the subgraph of Moment nodes. Returns clusters with at least `min_size` members.

### `weighted_mean(embeddings, weights)`

**Purpose:** Compute weighted centroid of embeddings.

**Logic:** `sum(e_i * w_i) / sum(w_i)` — standard weighted average in embedding space.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| L1 Physics (manemus) | Limbic delta from actor's tick loop | Signed float indicating limbic shift (positive = beneficial) |
| Universal Schema (mind-protocol) | `graph.create_link()`, `graph.query_nodes()` | Link and node CRUD operations |
| Event System | Event metadata (source, target, type, energy) | Trigger for link creation and trust propagation |
| Query Layer | `compute_trust_score()`, `derive_link_name()` | Trust scores and labels for API responses |

---

## MARKERS

<!-- @mind:todo Determine optimal MACRO_CRYSTAL_INTERVAL for different universe activity levels -->
<!-- @mind:todo Benchmark community detection algorithms for L3 graphs >100K nodes -->
<!-- @mind:proposition Consider incremental crystallization (process new moments since last scan only) -->
<!-- @mind:escalation Need to decide: should recursive trust (Alg 5 Step 3) be default or opt-in? -->

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
