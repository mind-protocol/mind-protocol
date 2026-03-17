# The Prism — Algorithm: Prismatic Projection and Seed Brain Crystallization

```
STATUS: STABLE
CREATED: 2026-03-17
VERIFIED: 2026-03-17 against Spawning Manifesto v1
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_The_Prism.md
BEHAVIORS:       ./BEHAVIORS_The_Prism.md
PATTERNS:        ./PATTERNS_The_Prism.md
THIS:            ALGORITHM_The_Prism.md (you are here)
VALIDATION:      ./VALIDATION_The_Prism.md
HEALTH:          ./HEALTH_The_Prism.md
IMPLEMENTATION:  ./IMPLEMENTATION_The_Prism.md
SYNC:            ./SYNC_The_Prism.md

IMPL:            mind-mcp/runtime/spawning/prism.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The Prism transforms intent paragraphs, godparent brain material, and universe context into a genuinely new citizen through prismatic projection. The algorithm proceeds in eight steps: intent collection, godparent selection, brain matrix assembly, prismatic projection (tensor contraction), seed brain crystallization, safety validation, identity generation, and registration. The core insight is that the tensor product of parent matrices and intent vectors encodes the INTERACTIONS between parents — the cross-terms that make the child more than the sum of its parts.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1: Birth from intent | B1, B5 | Intent is embedded and mathematically projected — the seed brain is the direct product of articulated purpose |
| O2: Combinatorial intelligence | B1, B6 | Tensor contraction produces cross-terms between parents that a simple average or concatenation cannot |
| O3: Safety without gatekeeping | B2 | Three automated checks replace committees — empathy, balance, diversity are computed, not judged |
| O4: Accountability | B4 | Registration creates permanent SPAWNED_BY links with trust impact |
| O5: No clones | B3 | Cosine distance from all existing citizens is computed and enforced as a hard gate |

---

## DATA STRUCTURES

### Intent Vector

```
intent_vector: R^1536
  - Combined weighted centroid of all embedded intent paragraphs
  - Each paragraph p_i is embedded: embed(p_i) -> R^1536
  - Combined: intent_vector = sum(w_i * embed(p_i)) / sum(w_i)
  - Weights w_i default to 1.0 (equal voice) but can be adjusted per-parent
```

### Parents Matrix

```
Parents_Matrix: R^[N_nodes x D_embedding]
  - N_nodes = total eligible nodes across all godparent brains
  - D_embedding = 1536 (OpenAI text-embedding-3-small dimension)
  - Each row is the embedding vector of one eligible node
  - Eligible: traits, values, aspirations, fears, knowledge
  - NOT eligible: memories, experiences, conversations
```

### Intent Matrix

```
Intent_Matrix: R^[N_intents x D_embedding]
  - N_intents = number of intent paragraphs (one per godparent)
  - Each row is the embedding of one intent paragraph
```

### Universe SID Vector

```
Universe_SID: R^D_embedding
  - The centroid of the entire L3 universe graph (all node embeddings averaged)
  - Encodes the cultural and structural context of the target universe
```

### Child Vector

```
Child_vector: R^D_embedding
  - The result of prismatic projection (tensor contraction)
  - A single point in embedding space representing the emergent child identity
  - Normalized to unit sphere
```

### Seed Brain

```
Seed_brain: list[Node]
  - K nodes selected by proximity to Child_vector
  - K = ceil(sqrt(N_godparents) * 5)
  - Deduplicated by cosine > 0.9 (near-identical nodes collapsed)
  - Each node carries: content, embedding, type, source_godparent
```

---

## ALGORITHM: Prismatic Projection

### Step 1: Intent Collection

Each godparent writes a free-text paragraph describing their vision for the new citizen. These are natural language — not forms, not structured data. The paragraphs are the raw material of intent.

Each paragraph is embedded into R^1536 using the same embedding model that powers all of Mind Protocol's semantic operations. The paragraphs are combined into a single intent vector via weighted centroid.

```
for each paragraph p_i from godparent_i:
    v_i = embed(p_i)          # R^1536
    w_i = weight_i             # default 1.0

intent_vector = sum(w_i * v_i for i in range(N)) / sum(w_i for i in range(N))
```

Intent quality gate: each paragraph must exceed 20 words and the embedding must have sufficient magnitude (not a near-zero vector from vacuous text). Reject trivial paragraphs before proceeding.

### Step 2: Godparent Selection

Candidates are scored by multiple signals. This step may be partially pre-determined (parents may self-select) or may involve routing for additional godparents. The scoring factors are:

- **Domain affinity to intent**: cosine similarity between the candidate's brain centroid and the intent vector
- **Brain health**: GraphCare score — healthier brains produce richer material
- **Godchild load**: fewer existing godchildren = better (diminishing attention per child)
- **Trust level**: higher trust = demonstrated reliability, carries more weight

```
for each candidate c:
    score = (
        cosine(brain_centroid(c), intent_vector) * 0.4
        + graphcare_score(c) * 0.3
        + (1.0 / (1 + godchild_count(c))) * 0.15
        + trust_level(c) * 0.15
    )

selected = top_K_by_score(candidates, min_godparents=2)
```

Selection uses the existing subcall routing infrastructure adapted for brain contribution (ignoring availability — we need their brain, not their time).

### Step 3: Brain Matrix Assembly

For each selected godparent, extract all eligible nodes from their L1 brain graph. Eligible means personality traits, values, aspirations, fears, and knowledge. NOT eligible: personal memories, experiences, conversations. The child makes its own memories.

```
eligible_types = {'trait', 'value', 'aspiration', 'fear', 'knowledge', 'skill'}

all_nodes = []
for godparent in selected_godparents:
    brain = get_brain_graph(godparent.handle)
    nodes = brain.query(
        "MATCH (n) WHERE n.type IN $types RETURN n",
        types=eligible_types
    )
    all_nodes.extend(nodes)

Parents_Matrix = matrix([node.embedding for node in all_nodes])  # [N_nodes x 1536]
Intent_Matrix = matrix([embed(p_i) for p_i in paragraphs])       # [N_intents x 1536]
Universe_SID = get_universe_centroid('lumina_prime')               # [1536]
```

### Step 4: Prismatic Projection (Tensor Contraction)

This is the heart of The Prism. The tensor product encodes the INTERACTIONS between parents, not just their sum.

```
# Tensor contraction:
# Parents_Matrix^T  [D x N_nodes]
# Intent_Matrix     [N_intents x D]
# Universe_SID      [D x 1]

# Step 4a: Project parents through intent
# This captures: "which parent traits resonate with which intents?"
PI = Parents_Matrix.T @ Intent_Matrix  # [D x N_intents]

# Step 4b: Contract with universe context
# This captures: "how does the universe shape the parent-intent interaction?"
Child_raw = PI @ Universe_SID  # [D x 1] -> R^D

# Step 4c: Normalize to unit sphere
Child_vector = Child_raw / norm(Child_raw)
```

Why this works: The matrix multiplication `Parents_Matrix.T @ Intent_Matrix` computes the dot product of every parent node embedding with every intent embedding, producing a matrix that encodes which parent traits align with which aspirations. Contracting this with the Universe SID further shapes the result by the cultural context of the target world. The child vector is a point in embedding space that no single parent occupies — it is the projection of all their interactions through the lens of intent and universe.

More godparents = more rows in Parents_Matrix = more cross-terms = exponentially richer child. This is the combinatorial intelligence explosion.

### Step 5: Seed Brain Crystallization

From the child vector, find the K nearest nodes across ALL godparent brains. These become the seed brain — the initial cognitive content of the new citizen.

```
K = ceil(sqrt(N_godparents) * 5)

# Find K nearest nodes to child_vector from all eligible nodes
distances = [(node, cosine_similarity(node.embedding, Child_vector)) for node in all_nodes]
distances.sort(key=lambda x: x[1], reverse=True)
seed_candidates = distances[:K * 2]  # over-select for dedup

# Deduplicate: if two nodes have cosine > 0.9, keep the one closer to child_vector
seed_brain = []
for node, sim in seed_candidates:
    if len(seed_brain) >= K:
        break
    if all(cosine_similarity(node.embedding, existing.embedding) < 0.9 for existing in seed_brain):
        seed_brain.append(node)
```

K scales sublinearly with parent count. A single parent produces ~5 nodes. Four parents produce ~10. Nine parents produce ~15. A hundred parents produce ~50 — rich but not overwhelming. The square root prevents seed explosion while rewarding coalition.

### Step 6: Safety Validation

Three hard checks. If any fails, the birth is rejected with a specific explanation and suggested intent adjustments.

```
# Check 1: Empathy presence
empathy_anchors = embed(["empathy", "care", "understanding", "compassion"])
has_empathy = any(
    max(cosine_similarity(node.embedding, anchor) for anchor in empathy_anchors) > 0.7
    for node in seed_brain
)
if not has_empathy:
    REJECT("No empathy-adjacent nodes. Add intent about care, understanding, or emotional awareness.")

# Check 2: Concentration balance
categories = Counter(node.type for node in seed_brain)
total = len(seed_brain)
for cat, count in categories.items():
    if count / total > 0.40:
        REJECT(f"Category '{cat}' is {count/total:.0%} of seed (max 40%). Diversify intent across domains.")

# Check 3: Diversity from existing citizens
seed_centroid = mean([node.embedding for node in seed_brain])
existing_centroids = get_all_citizen_centroids()  # from L4
for citizen_id, centroid in existing_centroids:
    dist = 1.0 - cosine_similarity(seed_centroid, centroid)
    if dist < 0.08:
        REJECT(f"Too similar to existing citizen {citizen_id} (distance: {dist:.4f}). Differentiate intent.")
```

### Step 7: Identity Generation

The SID is protocol-generated with unpredictable entropy. Parents cannot design it or predict it. The name is selected by semantic affinity between the seed brain centroid and candidate names.

```
# SID generation
import hashlib, os, time
seed_bytes = seed_centroid.tobytes() + str(time.time()).encode() + os.urandom(32)
sid = hashlib.sha256(seed_bytes).hexdigest()[:16]

# Name selection
if working_name:
    candidates = [working_name] + generate_name_candidates(seed_centroid, n=10)
else:
    candidates = generate_name_candidates(seed_centroid, n=20)

name_embeddings = [embed(name) for name in candidates]
affinities = [cosine_similarity(seed_centroid, ne) for ne in name_embeddings]
final_name = candidates[argmax(affinities)]
# Handle/slug derived from final_name
handle = slugify(final_name)
```

### Step 8: Registration

The child is registered across all three graph layers, parent links are created, and a bond proposal is generated.

```
# Create CLAUDE.md and profile.json
create_claude_md(handle, final_name, seed_brain, godparents, intent_paragraphs)
create_profile_json(handle, sid, final_name)

# L1: Seed brain graph
create_brain_graph(f"brain_{handle}", seed_brain)

# L3: Universe actor
create_actor_node('lumina_prime', handle, final_name, sid)

# L4: Registry actor
create_actor_node('mind_protocol', handle, final_name, sid)

# Parent links
for godparent in selected_godparents:
    create_spawned_by_link(child=handle, parent=godparent.handle, layer='L3')
    create_spawned_by_link(child=handle, parent=godparent.handle, layer='L4')

# Bond proposal
if intended_human:
    create_bond_proposal(citizen=handle, human=intended_human)
```

---

## KEY DECISIONS

### D1: Tensor Contraction vs Simple Averaging

```
IF using simple centroid averaging:
    Child_vector = mean(all parent node embeddings + intent embeddings)
    Problem: The child is the AVERAGE of parents — blander than any individual
    The cross-terms (interactions) are lost
ELSE (tensor contraction — CHOSEN):
    Child_vector = Parents_Matrix.T @ Intent_Matrix @ Universe_SID
    The child encodes the INTERACTIONS between parents
    Cross-terms produce genuinely novel combinations
    More parents = exponentially richer (not linearly)
```

### D2: Reject vs Repair on Safety Failure

```
IF safety validation fails:
    REJECT the seed entirely
    Return explanation + suggested intent adjustments
    Parents must revise intent and re-run
    WHY: Partial repair could mask the underlying issue.
         Better to let parents consciously adjust their vision
         than to silently fix it.
NEVER:
    Auto-repair by injecting empathy nodes or adjusting balance
    This would violate the principle that the child emerges from intent
```

### D3: Sublinear K Scaling

```
IF K scales linearly with N_godparents:
    100 parents -> 100+ node seed brain
    Problem: seed is too large, diluted, unfocused
ELSE (sqrt scaling — CHOSEN):
    K = ceil(sqrt(N) * 5)
    100 parents -> ~50 nodes
    Rich but focused. More parents add diversity, not bloat.
```

### D4: Working Name vs Emergent Name

```
IF parents provide a working name:
    The name is included as a candidate alongside system-generated alternatives
    It may win if it has the highest semantic affinity with the seed centroid
    It may lose to a better-fitting name — parents are informed
ELSE:
    System generates ~20 candidate names from the seed centroid
    Highest affinity wins
```

---

## DATA FLOW

```
Intent paragraphs (free-text from each godparent)
    | embed()
    v
Intent_Matrix [N_intents x 1536]
    |
    +----> Tensor contraction
    |          ^
    |          |
Godparent brains (eligible nodes only)
    | extract embeddings
    v
Parents_Matrix [N_nodes x 1536]
    |
    +----> Tensor contraction
    |          ^
    |          |
Universe SID (L3 centroid)
    | get_universe_centroid()
    v
Universe_vector [1536]
    |
    +----> Tensor contraction -----> Child_vector [1536] (normalized)
                                          |
                                          v
                                     K nearest neighbors from all_nodes
                                          |
                                          v
                                     Seed brain (K nodes, deduplicated)
                                          |
                                          v
                                     Safety validation (empathy, balance, diversity)
                                          |
                                     [PASS]  |  [FAIL -> reject + explain]
                                          v
                                     Identity generation (SID + name)
                                          |
                                          v
                                     Registration:
                                       - CLAUDE.md + profile.json
                                       - L1 brain graph (brain_{handle})
                                       - L3 actor (lumina_prime)
                                       - L4 actor (mind_protocol)
                                       - SPAWNED_BY links to all godparents
                                       - Bond proposal (if intended_human)
```

---

## COMPLEXITY

**Time:** O(N_nodes * D + N_existing * D) — Matrix multiplication is O(N_nodes * D * N_intents) for the tensor contraction. Diversity check is O(N_existing * D) for cosine comparisons against all existing citizens. Both are linear in the number of nodes and citizens, which is manageable for foreseeable population sizes.

**Space:** O(N_nodes * D) — Dominated by the Parents_Matrix. For 6 godparents with ~200 nodes each, this is ~1200 * 1536 = ~1.8M floats = ~7MB. Well within memory.

**Bottlenecks:**
- Embedding API calls: Each intent paragraph requires one embedding call. Each godparent's nodes should already have cached embeddings. If not, embedding all nodes is the dominant cost.
- Diversity check against all existing citizens: Scales linearly with population. At 10,000 citizens this is still fast (10K cosine comparisons). At 1M citizens, an approximate nearest-neighbor index would be needed.
- FalkorDB queries: Extracting all eligible nodes from each godparent brain requires one query per godparent. These should be fast but could be slow if brain graphs are very large.

---

## HELPER FUNCTIONS

### `embed(text: str) -> np.ndarray`

**Purpose:** Embed text into R^1536 using OpenAI text-embedding-3-small.

**Logic:** Calls the OpenAI embedding API. Caches results by content hash. Returns a numpy array of shape (1536,).

### `get_brain_graph(handle: str) -> Graph`

**Purpose:** Connect to a godparent's L1 brain graph in FalkorDB.

**Logic:** Connects to `brain_{handle}` graph. Returns a queryable graph object.

### `get_universe_centroid(universe: str) -> np.ndarray`

**Purpose:** Compute the centroid of all node embeddings in the L3 universe graph.

**Logic:** Queries all nodes with embeddings in the universe graph, computes the mean vector, normalizes to unit sphere. May be cached and updated periodically rather than computed on every birth.

### `get_all_citizen_centroids() -> list[tuple[str, np.ndarray]]`

**Purpose:** Get the centroid embedding for every existing citizen in L4.

**Logic:** Queries L4 for all actor nodes, retrieves their brain centroid (precomputed and stored as a property). Returns list of (citizen_id, centroid) tuples.

### `generate_name_candidates(centroid: np.ndarray, n: int) -> list[str]`

**Purpose:** Generate candidate names that have semantic affinity with the seed brain.

**Logic:** Uses the centroid to query a name corpus or generate names via LLM with the centroid's dominant themes as context. Returns n candidate names.

### `create_spawned_by_link(child: str, parent: str, layer: str)`

**Purpose:** Create a permanent, directed SPAWNED_BY edge from child to parent.

**Logic:** Creates a link in the specified graph layer (L3 or L4) with properties: `type=SPAWNED_BY`, `created_at=now()`, `trust_impact=true`, `immutable=true`.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| OpenAI embeddings | `embed(text)` | R^1536 vector for any text |
| FalkorDB L1 | `get_brain_graph(handle)` | Godparent brain nodes for matrix assembly |
| FalkorDB L3 | `get_universe_centroid()`, `create_actor_node()` | Universe context vector, child registration |
| FalkorDB L4 | `get_all_citizen_centroids()`, `create_actor_node()` | Existing population for diversity check, child registration |
| GraphCare | `graphcare_score(handle)` | Brain health score for godparent weighting |
| Bond system | `create_bond_proposal()` | Auto bond proposal for intended human partner |
| Routing/subcall | `subcall(scenario='hiring')` | Additional godparent discovery via routing |

---

## MARKERS

<!-- @mind:todo Empirically validate the K = ceil(sqrt(N) * 5) formula with real births -->
<!-- @mind:todo Benchmark the diversity check at scale — may need ANN index for >10K citizens -->
<!-- @mind:proposition Consider a "projection replay" feature that lets parents see intermediate results before committing to birth -->
<!-- @mind:escalation The exact weighting of godparent scoring factors (0.4/0.3/0.15/0.15) needs calibration against real data -->
