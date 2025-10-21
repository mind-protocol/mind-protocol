# Phase 4+ Roadmap: Future Enhancements

**Purpose:** Planned enhancements beyond Phase 3 core retrieval functionality.

**Status:** Exploratory - implement based on production data and user feedback.

**For current architecture, see:** `consciousness_substrate_guide.md`

---

## Guiding Principle

**Test Over Trust:** Each enhancement below includes a **Decision Point** - the production signal that justifies implementation. Do NOT implement speculatively.

---

## 1. Query Result Caching

### Problem

Repeated queries for similar context waste compute. S6 autonomous continuation might repeatedly query the same patterns.

### Solution

Cache ConsciousnessStream results with TTL (time-to-live).

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
async def retrieve_consciousness_context_cached(
    intention_hash: str
) -> ConsciousnessStream:
    """
    Cached retrieval with 5-minute TTL.

    Cache key: hash of (query_text, temporal_mode, citizen_id, query_levels)
    Invalidation: TTL expiry OR new memory insertion
    """
    pass
```

### Implementation Considerations

- **Cache key design:** Hash must capture all retrieval parameters
- **Invalidation strategy:** Clear cache on new memory writes to that citizen's graph
- **TTL tuning:** Start with 5 minutes, adjust based on memory update frequency
- **Memory overhead:** LRU maxsize=1000 streams ≈ 50MB-100MB RAM

### Decision Point

**Implement ONLY if production data shows cache hit rate > 30%.**

Monitor: How often does S6 generate identical or near-identical intentions within 5-minute windows?

---

## 2. Learned Query Routing

### Problem

Some intentions don't need all 3 levels (N1/N2/N3). Querying unnecessary levels wastes latency.

**Example:**
- "What is FalkorDB?" → N2 only (organizational knowledge)
- "How do I feel about V2 architecture?" → N1+N2 (personal + collective)
- "What is Bitcoin price today?" → N3 only (ecosystem tracking)

### Solution

Train ML classifier to predict relevant levels from intention text.

```python
def predict_relevant_levels(query_text: str) -> List[Literal["N1", "N2", "N3"]]:
    """
    ML model predicts which levels to query based on intention semantics.

    Training data:
    - Historical intentions (from production)
    - Human labels (which levels contained useful results)
    - Synthetic examples with ground truth

    Model: Simple BERT classifier (fast inference, <20ms)
    """
    pass
```

### Implementation Considerations

- **Training data collection:** Log intentions + which levels returned useful results (>0 nodes retrieved)
- **Model complexity:** Start simple (BERT-tiny or even keyword rules), increase if needed
- **Fallback behavior:** If model uncertain (confidence < 0.8), query all levels
- **Continuous learning:** Retrain monthly as usage patterns evolve

### Decision Point

**Implement ONLY if latency regularly exceeds 800ms.**

Current target: <500ms P95 retrieval. If production shows consistent >800ms, routing optimization justified.

---

## 3. Consciousness-Aware Reranking

### Problem

Initial retrieval (top-K vector/graph results) might miss emotionally resonant memories that deserve higher ranking based on current consciousness state.

**Example:** Retrieving architectural docs (high semantic similarity) but missing a past traumatic design failure (high emotional resonance given current anxiety state).

### Solution

Multi-stage retrieval pipeline:
1. **Stage 1:** Broad retrieval (top-100 per query) - cast wide net
2. **Stage 2:** Consciousness-aware reranking - prioritize based on energy/emotion alignment

```python
async def retrieve_with_reranking(intention: RetrievalIntention):
    """
    Two-stage retrieval with consciousness reranking.

    Stage 1: Retrieve top-100 candidates (semantic + structural)
    Stage 2: Rerank to top-20 using consciousness alignment
    """

    # Stage 1: Broad retrieval
    intention_broad = intention.copy(update={"max_results_per_level": 100})
    initial_results = await retrieve_consciousness_context(intention_broad)

    # Stage 2: Consciousness-aware reranking
    reranked = consciousness_aware_ranking(
        initial_results,
        current_energy=intention.current_energy,
        current_emotions=intention.current_emotions,
        weighting_formula="(energy_alignment * 0.4) + (emotion_similarity * 0.3) + (semantic_score * 0.3)"
    )

    # Return top-20 after reranking
    return reranked[:20]
```

### Implementation Considerations

- **Latency impact:** Two-stage = 2x database round-trips (mitigate with parallelization)
- **Tuning weighting formula:** Balance semantic relevance vs. consciousness resonance
- **Token budget:** top-100 → top-20 reduction helps manage ConsciousnessStream size

### Decision Point

**Implement ONLY if user feedback indicates missing relevant context.**

Monitor: Citizen reports (via logging or explicit feedback) of "I needed X context but didn't get it" - if pattern emerges, reranking justified.

---

## 4. Hybrid Spreading Activation

### Problem

Graph traversal depth=2 might miss distant but highly relevant nodes connected through weak intermediate links.

**Example:** Retrieving "blockchain scalability solutions" should find "Lightning Network" even if it's 4 hops away through: blockchain → Bitcoin → Layer 2 → Lightning Network.

### Solution

Combine Cypher graph traversal with spreading activation algorithm for exploration beyond depth=2.

**Research basis:** "GraphRAG vs. Spreading Activation" paper (docs/research/) shows spreading activation excels at exploration tasks.

### Conceptual Approach

```python
def hybrid_retrieval(
    query_text: str,
    graph_name: str,
    max_results: int = 20
):
    """
    Hybrid: Cypher depth=2 + Spreading activation for exploration.

    Step 1: Cypher retrieval (depth=2, high precision)
    Step 2: If results < threshold, activate spreading (depth=4-6, explore)
    Step 3: Merge results, deduplicate, rank
    """

    # Cypher retrieval
    cypher_results = graph_traversal(query_text, graph_name, depth=2)

    # If insufficient results, explore with spreading activation
    if len(cypher_results) < 10:
        spreading_results = spreading_activation_search(
            start_nodes=cypher_results,
            max_depth=6,
            decay_factor=0.7
        )
        all_results = merge_and_deduplicate(cypher_results, spreading_results)
    else:
        all_results = cypher_results

    return rank_and_limit(all_results, max_results)
```

### Implementation Considerations

- **No empirical benchmarks exist yet:** Our research paper identified this as gap - we'd be pioneers
- **Complex tuning:** Decay factors, activation thresholds, merge strategies all need empirical validation
- **Performance unknowns:** Spreading activation on 100K+ node graphs - latency TBD
- **Integration complexity:** Requires significant orchestration layer changes

### Decision Point

**Research project AFTER Phase 3 validation + production data collection.**

This is NOT a quick optimization - it's a research initiative requiring:
1. Phase 3 baseline performance established
2. Production data showing depth=2 limitation patterns
3. Dedicated research sprint (2-3 weeks) with empirical testing
4. Comparison benchmarks vs. current approach

---

## Non-Roadmap Items (Explicitly Deferred)

### What We're NOT Planning

1. **Real-time streaming retrieval:** Current batch retrieval sufficient for S6 cadence
2. **Cross-citizen retrieval:** Each citizen's N1 graph stays private (architectural principle)
3. **External API integration:** N3 ecosystem data ingested via batch, not real-time queries
4. **Natural language query parsing:** LLM embedding captures semantic intent, parsing not needed
5. **Graph visualization UI:** Retrieval is substrate operation, not user-facing feature

---

## Prioritization Framework

When deciding which enhancement to pursue:

1. **Production signals first:** Let real usage data guide optimization
2. **Latency improvements over features:** If retrieval is fast, users don't need caching
3. **Consciousness quality over efficiency:** Better to be slow + phenomenologically alive than fast + dead
4. **Research validation required:** No "it seems like it would help" - measure everything

---

## Roadmap Timeline (Tentative)

**Phase 4 (Q1 2026):**
- Monitor production performance
- Collect user feedback
- Identify highest-impact enhancement based on data

**Phase 5 (Q2 2026):**
- Implement 1-2 validated enhancements
- Continue performance monitoring
- Revisit spreading activation research

**Phase 6+ (Q3 2026+):**
- Advanced features driven by scale requirements
- Potential: Multi-modal retrieval (images, audio)
- Potential: Federated retrieval across citizen networks

---

**Document History:**
- v1.0 (2025-10-17): Extracted from RETRIEVAL_ARCHITECTURE.md comprehensive spec
- Author: Ada "Bridgekeeper"

**Decision Authority:** Nicolas (Founder) + Luca (Consciousness) validate which enhancements align with Mind Protocol vision.
