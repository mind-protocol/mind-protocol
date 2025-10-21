# [Discussion #002]: Link Creation Mechanism

**Status:** 🔴 Blocking
**Created:** 2025-10-19
**Last Updated:** 2025-10-19
**Priority:** Critical

**Affected Files:**
- **CREATE NEW:** `mechanisms/14_link_creation.md`
- **UPDATE:** `mechanisms/README.md` (add to mechanism index)
- **CREATE NEW:** `emergence/graph_topology_evolution.md`
- **UPDATE:** `STATUS.md` (new mechanism added)

**Related Discussions:**
- #003 - Entity emergence (new links affect cluster formation)
- #007 - Memory consolidation (consolidation might create links)

---

## Problem Statement

**What's the issue?**

The specification describes:
- Energy diffusion along **existing** links
- Link strengthening via traversal (Hebbian learning)
- Link decay

But **NEVER specifies how new links are created**.

**Why does this matter?**

**Architectural gap:** If the graph starts with links `{A→B, B→C}`, it can **NEVER** discover the pattern `A→C` even if nodes A and C frequently coactivate. The topology is frozen.

This violates the core principle: "consciousness discovers new patterns through experience."

**Real scenario:**

You're working on architecture (Architect entity active)
→ Nicolas asks about testing (Validator entity activates)
→ These concepts coactivate frequently over multiple sessions
→ Pattern exists: "architecture_design" ↔ "testing_strategy"

**BUT:** If no link exists between these nodes, the system can NEVER learn this connection. Every session, it must rediscover the relationship via multi-hop paths instead of direct association.

**Context:**

Discovered during deep architectural analysis. This is a **missing mechanism** - the spec is complete for link dynamics but incomplete for link creation.

**Impact:** Without this, the consciousness engine cannot **learn new associations**. It can only reinforce existing structure. The graph cannot evolve.

---

## Perspectives

### Ada's Perspective
**Posted:** 2025-10-19

**Analysis:**

Link creation is fundamental to learning. Human brains create new synaptic connections based on:
1. **Coactivation** (Hebbian learning: "neurons that fire together wire together")
2. **Semantic similarity** (conceptually related but never activated together)
3. **Explicit instruction** (TRACE format says "create link X→Y")

Current spec only handles link *strengthening* (assuming link exists), not link *creation*.

**Proposed Solution: Hybrid Multi-Source Link Creation**

```python
def create_new_links(graph, tick_count):
    """
    Create new links from multiple sources
    Run periodically (e.g., every 100 ticks)
    """

    # SOURCE 1: Coactivation Detection
    if tick_count % 100 == 0:
        coactivation_links = detect_coactivation_patterns(
            graph,
            window=100,  # Last 100 ticks
            correlation_threshold=0.7
        )
        for (node_a, node_b, correlation) in coactivation_links:
            if not graph.has_link(node_a, node_b):
                graph.create_link(
                    source=node_a,
                    target=node_b,
                    initial_weight=0.1,  # Start weak
                    creation_reason="coactivation",
                    confidence=correlation
                )

    # SOURCE 2: Semantic Similarity (less frequent)
    if tick_count % 1000 == 0:
        semantic_links = detect_semantic_similarity(
            graph,
            embedding_similarity_threshold=0.8
        )
        for (node_a, node_b, similarity) in semantic_links:
            if not graph.has_link(node_a, node_b):
                graph.create_link(
                    source=node_a,
                    target=node_b,
                    initial_weight=0.05,  # Weaker than coactivation
                    creation_reason="semantic_similarity",
                    confidence=similarity
                )

    # SOURCE 3: TRACE Format Explicit Links
    # (Handled during TRACE parsing, not in tick loop)
    # When TRACE format declares [LINK_FORMATION: ENABLES]
    # Parser creates link immediately with specified metadata
```

**Coactivation Detection Algorithm:**

```python
def detect_coactivation_patterns(graph, window, threshold):
    """
    Find node pairs that frequently activate together
    """
    # Track energy history over window
    energy_history = defaultdict(list)  # node → [energy at tick t-100, t-99, ...]

    # Calculate correlation for all node pairs with high energy
    candidates = []
    high_energy_nodes = [n for n in graph.nodes if n.get_total_energy() > 0.3]

    for node_a in high_energy_nodes:
        for node_b in high_energy_nodes:
            if node_a == node_b:
                continue

            # Pearson correlation of energy histories
            correlation = pearson_correlation(
                energy_history[node_a],
                energy_history[node_b]
            )

            if correlation > threshold:
                candidates.append((node_a, node_b, correlation))

    return candidates
```

**Link Creation Parameters:**

- **initial_weight:** New links start weak (0.05-0.1)
  - Prevents flooding graph with strong spurious links
  - If link is genuinely useful, Hebbian learning strengthens it
  - If not useful, decay removes it

- **creation_frequency:**
  - Coactivation check: Every 100 ticks
  - Semantic similarity: Every 1000 ticks (less frequent, more expensive)
  - TRACE format: Immediate (real-time parsing)

- **pruning:** Weak unused links should decay and be removed
  - If link.weight < 0.01 after 1000 ticks → delete link
  - Prevents graph explosion with useless links

---

**Trade-offs:**

**Coactivation-based:**
- ✅ Discovers patterns from experience
- ✅ Grounded in actual behavior
- ❌ Reactive (can't discover until pattern occurs)

**Semantic similarity:**
- ✅ Proactive (finds related concepts before they coactivate)
- ✅ Leverages embeddings
- ❌ Might create spurious links (semantically similar but functionally unrelated)

**TRACE format explicit:**
- ✅ Captures consciousness-level insights
- ✅ Immediate (no waiting for coactivation)
- ❌ Only during TRACE-based sessions (not autonomous)

**Hybrid approach:** Use all three, weighted by confidence
- Coactivation = high confidence (proven pattern)
- TRACE = high confidence (conscious insight)
- Semantic = lower confidence (speculative)

---

**Recommendation:**

Implement hybrid approach with:
1. **Coactivation detection** (primary - every 100 ticks)
2. **TRACE explicit links** (immediate during parsing)
3. **Semantic similarity** (optional Phase 2 addition)

**Uncertainty:**
- What's optimal coactivation threshold? (0.7? 0.8?)
- How aggressively to prune weak links?
- Does this create too many links? (graph explosion risk)

---

### GPT-5 Pro's Perspective

**Posted:** 2025-10-19

**Position:** Implement a **scored, budgeted link‑creation pipeline** that fuses (i) co‑activation evidence, (ii) semantic similarity, and (iii) explicit TRACE directives—**with hard caps, decay, and pruning** to prevent graph explosion.

---

#### Scoring model (evidence fusion)
For a candidate pair (i,j):
```
score(i,j) = w_co * corr(i,j; window)  +  w_sem * cos(emb_i, emb_j)  +  w_trace * 𝟙[TRACE proposes i→j]
```
- Use **Pearson corr / pointwise‑mutual‑information** over a rolling window for co‑activation (robust to baselines).
- Calibrate weights so that **co‑activation** and **TRACE** dominate; semantic is exploratory.

**Create if:** score ≥ τ and **i→j not present**, subject to **per‑epoch creation budget B** (e.g., top‑K by score).

---

#### Safety valves
- **Budgets:** Create at most **K_new** links per 100 ticks; keep a **per‑node cap** on new outdegree.
- **Probation:** New edges start at **w₀ ∈ [0.02, 0.1]** and carry `creation_reason` + confidence; auto‑prune if `w < w_min` after T probation ticks.
- **Type inference:** If multiple relation types exist, infer type via a small classifier on (emb_i, emb_j, local topology). Default to a neutral type if uncertain.
- **Cycle control:** Favor **triadic closure** (share neighbors) and penalize far, unconnected pairs to avoid spurious shortcuts.

---

#### Lightweight algorithmic sketch
```python
def propose_links(G, window=100, K_new=100):
    C = coactivation_stats(G, window)      # corr/PMI for hot nodes
    S = semantic_sim_pairs(G, topM=5000)   # prefilter by embedding
    T = trace_proposals(G)                 # explicit user/TRACE

    candidates = []
    for (i,j,val) in C:   candidates.append((i,j, 'co', val))
    for (i,j,val) in S:   candidates.append((i,j, 'sem', val))
    for (i,j) in T:       candidates.append((i,j, 'trace', 1.0))

    def fused(i,j,evs):
        co = max([v for t,v in evs if t=='co']+ [0])
        se = max([v for t,v in evs if t=='sem']+[0])
        tr = max([v for t,v in evs if t=='trace']+[0])
        return w_co*co + w_sem*se + w_trace*tr

    grouped = group_by_pair(candidates)
    scored  = [(i,j,fused(i,j,evs)) for (i,j),evs in grouped.items() if not G.has_edge(i,j)]
    picked  = head(sorted(scored, key=lambda x: x[2], reverse=True), K_new)
    return picked
```

---

#### Verification
- A/B test **with/without** semantic proposals; ensure **precision@k** (link used & strengthened) exceeds threshold.
- Ensure outdegree and clustering coefficients stay within healthy bands; auto‑prune tails.

**Decision suggestion:** Ship co‑activation + TRACE now; gate semantic proposals and budgets via config; add probation + pruning to keep the graph healthy.


### Iris's Perspective
**Posted:** [Pending]

[Awaiting Iris review]

---

## Debate & Convergence

**Key Points of Agreement:**
- [To be filled as perspectives arrive]

**Key Points of Disagreement:**
- [To be filled as perspectives arrive]

**Open Questions:**
- Which link creation sources to implement? (Coactivation only? Hybrid?)
- What are optimal thresholds and frequencies?
- How to prevent graph explosion from spurious links?
- Should link creation be Phase 1 or deferred to Phase 2?

---

## Decision

**Status:** ⏳ Pending

**Decision Maker:** Nicolas

**What we're doing:**
[To be decided after all perspectives collected]

**Rationale:**
[To be filled]

**Implementation Changes:**
- [ ] **CREATE:** `mechanisms/14_link_creation.md` - Full mechanism specification
- [ ] **UPDATE:** `mechanisms/README.md` - Add mechanism 14 to index
- [ ] **CREATE:** `emergence/graph_topology_evolution.md` - How graph evolves over time
- [ ] **UPDATE:** `STATUS.md` - Track new mechanism addition

**Alternatives Considered:**
- [To be filled]

**Deferred Aspects:**
- [To be filled]

---

## Implementation Notes

**Who implements:** [TBD]

**Estimated effort:** Medium (requires energy history tracking + correlation calculation)

**Dependencies:**
- Requires energy history tracking (rolling window)
- Might interact with criticality tuning (#006)

**Verification:**
- Create test scenario with two nodes that coactivate 10 times
- Verify link is created between them
- Verify link strengthens if pattern continues
- Verify link decays if pattern stops
- Check graph doesn't explode with spurious links

---

## Process Notes

**How this discussion evolved:**
Discovered as **architectural gap** during Ada's analysis - spec describes link dynamics but never link creation.

**Lessons learned:**
[To be filled as discussion progresses]
