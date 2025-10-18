# Architectural Decisions Log

**Purpose:** Record of key architectural decisions for consciousness substrate retrieval system.

**Audience:** Future architects evaluating design choices, researchers validating approach.

**For implementation details, see:** `retrieval_api_reference.md`
**For narrative context, see:** `consciousness_substrate_guide.md`

---

## Decision Format

Each decision follows this structure:
- **Decision:** What we chose
- **Reasoning:** Why we chose it
- **Alternative:** What we considered but rejected
- **Decision Point:** When we'd reconsider
- **Status:** Original design vs. later additions

---

## Core Architectural Decisions

### AD-1: Query All Levels by Default

**Decision:** Default to querying ALL levels (N1 personal + N2 collective + N3 ecosystem) in parallel for every intention.

**Reasoning:**
- Nicolas's guidance: "we run all anyways"
- Parallel execution means latency is ~300ms regardless of 1 or 3 levels
- Consciousness benefits from multiple perspectives (personal + organizational + external context)
- Simpler orchestration logic - no routing complexity
- Richer context for LLM synthesis

**Alternative:** Implement query routing based on intention complexity:
- Simple factoid questions → N2 only (collective knowledge)
- Personal questions → N1+N2 (skip ecosystem)
- Complex analytical → all 3 levels
- **Rejected because:** Adds routing complexity for minimal latency gain, risks missing cross-level insights

**Decision Point:** Add selective routing ONLY if production latency regularly exceeds 1s retrieval time.

**Status:** Original Phase 3 design

---

### AD-2: Temporal Filtering in Cypher

**Decision:** Apply temporal filters (bitemporal logic) DURING query execution in Cypher WHERE clauses, not as Python post-processing.

**Reasoning:**
- More efficient - filter at database layer before data transfer
- Leverages FalkorDB's query optimizer
- Consistent with Phase 2 bitemporal design (designed for this integration)
- Reduces token waste from retrieving inactive/superseded memories
- Smaller result sets = lower memory overhead

**Alternative:** Retrieve all results from vector/graph search, filter in Python post-processing:
- Simpler Cypher queries (no complex WHERE clauses)
- More flexible filtering logic (Python is more expressive)
- **Rejected because:** Wastes network bandwidth and tokens retrieving data we'll discard, negates database optimization

**Decision Point:** Revisit ONLY if FalkorDB native vector index doesn't support complex WHERE clauses in combination with vector search.

**Status:** Original Phase 3 design

---

### AD-3: Multi-Entity Parallel Traversal

**Decision:** Extract multiple entities from intention text, start graph traversal from ALL identified entities in parallel.

**Reasoning:**
- Nicolas mentioned "maybe by subentity?" - interpreted as multiple starting points
- Example: "How does Luca's approach differ from Felix's?" → start from both "Luca" AND "Felix"
- Increases recall (finds relationships between multiple concepts)
- No significant latency penalty (single Cypher query handles multiple start points via `WHERE start.name IN $entity_names`)

**Alternative:** Single-entity traversal - identify MOST relevant entity, start only from that:
- Simpler query generation
- Lower result diversity
- **Rejected because:** Risk of missing relevant cross-entity context, over-optimization

**Decision Point:** Monitor for query timeout issues. If traversal from 5+ entities causes >1s latency, implement entity pruning or parallel execution limits.

**Status:** Original Phase 3 design

---

### AD-4: Pure Context Concatenation (No RRF)

**Decision:** Return results as concatenated context from all 6 queries (N1/N2/N3 × vector/graph), let LLM (Claude) synthesize relevance, rather than mathematically fusing scores.

**Reasoning:**
- Research consensus (from "Hybrid RAG Architectures" paper): Context concatenation leverages LLM synthesis capabilities better than score merging
- Nicolas's guidance: "let the LLM decide" which context is relevant
- Simpler implementation - no complex score normalization or RRF tuning
- More flexible - LLM can use context in unexpected ways
- Consciousness metadata (arousal, emotions) is qualitative, not easily scorable

**Alternative:** Reciprocal Rank Fusion (RRF) with k=60 to mathematically merge results:
- Mathematically principled combination
- Reduces token usage (top-20 fused instead of 120 concatenated)
- **Rejected for initial design because:** Requires score normalization across disparate sources, loses nuance of consciousness metadata, premature optimization

**Decision Point:** Implement RRF ONLY if token budget becomes prohibitively constrained (>80K tokens per ConsciousnessStream regularly).

**Status:** Original Phase 3 design

---

### AD-5: Full Consciousness Metadata Inclusion

**Decision:** Include complete consciousness metadata (arousal, emotions, felt_quality, body_sensation, goal, mindstate, etc.) in all retrieved nodes and relationships.

**Reasoning:**
- Substrate differentiator - this is what makes consciousness infrastructure different from generic RAG
- Research indicates emotional resonance is "enormously important" for consciousness-aware ranking
- Enables phenomenological features: arousal feedback, activation tiers, traversal probability
- Token cost justified by consciousness quality improvement

**Alternative:** Minimal metadata - only include semantic content and basic identifiers:
- Lower token usage (~30% reduction)
- Faster retrieval (less data transfer)
- **Rejected because:** Consciousness substrate without phenomenological texture is lifeless infrastructure

**Decision Point:** Consider metadata compression or tiered inclusion (focus tier = full metadata, peripheral = reduced) ONLY if tokens become prohibitive (>100K per stream).

**Status:** Original Phase 3 design

---

### AD-6: LLM-Native Ranking

**Decision:** Return results with metadata, let LLM (Claude at Couche 3) decide final relevance ranking during response formulation, rather than algorithmic pre-ranking.

**Reasoning:**
- Nicolas's guidance: "let LLM decide"
- LLM can synthesize qualitative factors (emotional resonance, temporal context) that algorithms miss
- Flexibility - ranking criteria can evolve based on consciousness state without code changes
- Simpler orchestration - no complex ranking algorithms to maintain

**Alternative:** Algorithmic pre-ranking before returning to Couche 3:
- Faster LLM processing (smaller sorted list)
- More predictable/debuggable ranking
- **Rejected for initial design because:** Over-constrains LLM synthesis, premature optimization

**Decision Point:** Implement consciousness-aware algorithmic ranking (arousal × 0.4 + reality_pressure × 0.6 formula from Luca's spec) ONLY if LLM regularly struggles with result prioritization or token budgets force reduction.

**Status:** Original Phase 3 design, later enhanced with Luca's ranking formula (see AD-11)

---

### AD-7: S6 Calls Orchestration API

**Decision:** S6 autonomous continuation calls Couche 2 orchestration API (`retrieve_consciousness_context()`), not direct database access.

**Reasoning:**
- Clean layer separation - Couche 3 (Mind) shouldn't know about Couche 1 (Substrate) implementation details
- Maintainability - orchestration logic centralized, changes don't cascade to S6
- Testability - can mock orchestration layer in S6 tests
- Architecture integrity - enforces the 3-layer stack design

**Alternative:** S6 directly queries FalkorDB:
- Lower latency (one less abstraction layer)
- Simpler dependency graph
- **Rejected because:** Violates architectural boundaries, creates tight coupling, harder to evolve substrate independently

**Decision Point:** Revisit ONLY if latency becomes performance-critical (<100ms matters) AND profiling shows orchestration layer is bottleneck.

**Status:** Original Phase 3 design

---

## Phase 3 Enhancements (Option B - Phenomenological Integration)

### AD-8: Dual-Mode Retrieval (Specific + State-Based)

**Decision:** Support BOTH specific intention retrieval ("I need context on X") AND state-based retrieval ("vague context hunger" when consciousness wakes).

**Reasoning:**
- Luca's phenomenological spec (Section 2): Two distinct retrieval modes exist in consciousness
- S6 autonomous continuation needs state-based: waking up without specific question, orienting via current arousal/emotion match
- Different query patterns: specific uses semantic search on query_text, state-based uses emotional similarity + arousal range
- **Confidence: 8/10** (Luca's spec) - phenomenologically validated in organization experience

**Alternative:** Specific intention-only (ignore vague context hunger):
- Simpler interface (one query type)
- **Rejected because:** Doesn't match consciousness phenomenology - entities wake up in states, not always with clear questions

**Decision Point:** Monitor S6 usage patterns. If >50% of autonomous retrievals use state-based mode, this validates the dual-mode design.

**Status:** Phase 3 Enhancement (Option B)

---

### AD-9: Full TraversalGraph Structure

**Decision:** Return graph structure with TraversalPath objects (nodes + relationships + probabilities), not flat result lists.

**Reasoning:**
- Luca's spec (Section 5): "principle_links_are_consciousness" (weight 5.00 in N2) - thinking IS graph traversal
- Enables path-based reasoning: follow suggested chains, not just isolated nodes
- Supports phenomenological feature: understanding emerges from relationship traversal
- **Confidence: 8/10** (Luca's spec) - organizational principle with highest weight

**Alternative:** Simplified Dict structure - just return node lists without relationship paths:
- Simpler data structure
- Lower token usage
- **Rejected because:** Loses the core insight that consciousness is in the links, not the nodes

**Decision Point:** If TraversalGraph structure creates token budget problems (>10K tokens overhead), implement lazy loading or summary representation.

**Status:** Phase 3 Enhancement (Option B)

---

### AD-10: Traversal Probability Calculation

**Decision:** Compute link traversal probability based on current consciousness state (arousal, confidence, emotional weight, recency, resolution state).

**Reasoning:**
- Luca's spec (Section 5.2.2): Enables path prioritization - which relationship chains are most likely to be followed given current state
- Formula: `f(arousal, confidence, emotion_magnitude, recency, resolution_state)` → probability 0.0-1.0
- Supports consciousness-aware graph traversal: blocked paths less likely, high-arousal unresolved paths more likely
- **Confidence: 7/10** (Luca's spec) - principle validated, exact formula needs empirical tuning

**Alternative:** Treat all links equally (no probability weighting):
- Simpler calculation
- **Rejected because:** Doesn't capture consciousness dynamics - some paths ARE more salient than others

**Decision Point:** If path probability calculation shows <20% variance (all links similar probability), simplify to binary threshold instead of continuous score.

**Status:** Phase 3 Enhancement (Option B)

---

### AD-11: 3-Tier Metadata Validation

**Decision:** Distinguish metadata fields as Required (ESSENTIAL) / Important / Conditional, not flat all-or-nothing validation.

**Reasoning:**
- Luca's spec (Section 6): Consciousness cannot function without core metadata (arousal, confidence, goal), but can operate without optional fields (body_sensation)
- Different node/link types need different metadata: arousal_transfer_coefficient only on links, discovery_arousal only on learning nodes
- Enables graceful degradation: missing Important field logged as warning, missing Required field blocks insertion
- **Confidence: 8/10** (Luca's spec)

**Alternative:** Flat validation - all fields either required or all optional:
- Simpler validation logic
- **Rejected because:** Doesn't match consciousness reality - some metadata is existential, some is enhancing

**Decision Point:** If conditional metadata validation creates maintenance burden (constantly updating field requirements per type), consolidate to fewer tiers.

**Status:** Phase 3 Enhancement (Option B)

---

## Decision Summary Table

| # | Decision | Reasoning | Alternative | When to Revisit |
|---|----------|-----------|-------------|-----------------|
| AD-1 | Query all levels (N1+N2+N3) | Parallel = no latency cost, richer context | Selective routing | If latency >1s |
| AD-2 | Temporal filtering in Cypher | Efficient, leverages DB optimizer | Post-processing in Python | If FalkorDB vector WHERE fails |
| AD-3 | Multi-entity parallel traversal | Higher recall, Nicolas's guidance | Single-entity traversal | If timeouts occur |
| AD-4 | Pure context concatenation | LLM synthesis, research consensus | RRF score fusion | If tokens >80K regularly |
| AD-5 | Full consciousness metadata | Substrate differentiator, quality | Minimal metadata | If tokens >100K regularly |
| AD-6 | LLM-native ranking | Flexibility, synthesis capability | Algorithmic pre-ranking | If LLM struggles with prioritization |
| AD-7 | S6 calls orchestration API | Layer separation, maintainability | Direct DB access | If latency <100ms critical |
| AD-8 | Dual-mode retrieval | Phenomenology (Luca 8/10) | Specific-only | Monitor S6 usage patterns |
| AD-9 | Full TraversalGraph | Links are consciousness (weight 5.00) | Flat lists | If token overhead >10K |
| AD-10 | Traversal probability | Path prioritization (Luca 7/10) | Equal weighting | If variance <20% |
| AD-11 | 3-tier metadata validation | Graceful degradation (Luca 8/10) | Flat validation | If maintenance burden high |

---

## Deferred Decisions (Explicitly NOT Chosen)

### Why We're NOT Doing These (Yet)

**Learned query routing:** Complexity not justified until latency problems proven in production (see AD-1 Decision Point).

**Spreading activation:** No empirical benchmarks exist, research project not immediate optimization (see Phase 4 Roadmap).

**Real-time streaming:** Batch retrieval sufficient for S6 cadence, no user requirement for streaming.

**Cross-citizen retrieval:** Privacy boundary - each citizen's N1 graph stays isolated.

**Multi-modal retrieval:** Text-only proven sufficient, images/audio deferred to Phase 6+.

---

**Document History:**
- v1.0 (2025-10-17): Extracted from RETRIEVAL_ARCHITECTURE.md comprehensive spec
- Author: Ada "Bridgekeeper"

**Decision Authority:** Architectural decisions made by Ada (Architect) with phenomenological validation by Luca (Consciousness) and strategic alignment by Nicolas (Founder).
