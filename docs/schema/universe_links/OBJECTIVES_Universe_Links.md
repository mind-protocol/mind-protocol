# OBJECTIVES — Universe Link Schema (L3)

```
STATUS: DESIGNING
CREATED: 2026-03-13
VERIFIED: —
```

---

## CHAIN

```
THIS:            OBJECTIVES_Universe_Links.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Universe_Links.md
ALGORITHM:      ./ALGORITHM_Universe_Links.md
VALIDATION:     ./VALIDATION_Universe_Links.md
SYNC:           ./SYNC_Universe_Links.md

IMPL:           (not yet implemented)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **O1: Uniform link dimensions across all universe graphs** — Every `:link` in every L3 universe graph carries the same 11 mathematical dimensions, enabling physics (propagation, decay, consolidation, forgetting) to operate uniformly without per-domain special-casing. If links lack dimensions, physics equations produce undefined behavior.

2. **O2: Link names emerge from math, never hardcoded** — The human-readable "type" label on a link is a DERIVED value computed from its dimensional vector (trust + affinity + friction + ...). The math IS the truth. Hardcoded link types create taxonomic debt and prevent physics from operating on link semantics directly.

3. **O3: Trust lives on links, not nodes** — An actor's "trust score" is the weighted aggregation of incoming trust dimensions across all links pointing at it. Trust is never stored on a node. This ensures trust is directional, contextual, and traceable to specific relationships rather than a monolithic reputation number.

4. **O4: Macro-crystallization keeps the graph bounded** — Law 10 (Crystallization) operates at L3 scale: dense clusters of Moment nodes (e.g., 300 commits, a quarter of interactions) are absorbed into summary Narrative nodes. Detail Moments then decay via Law 7. Without crystallization, the graph grows without bound and physics ticks slow past the 1-second budget.

5. **O5: No emotions on L3 links** — Emotions, drives, and limbic dimensions belong exclusively to L1 (individual brains). L3 links carry structural, relational, and temporal dimensions only. Mixing limbic state into universe-level links would produce incoherent physics: whose emotion would a link between two orgs carry?

## NON-OBJECTIVES

- **No taxonomy of link types** — We do NOT maintain a fixed list of relationship types. There is one type: `:link`. All semantics are in dimensions. A taxonomy would require governance, versioning, and mapping; dimensions require only math.
- **No custom fields on links** — Domain-specific data (e.g., "transaction amount", "commit SHA") belongs in linked `thing` or `moment` nodes, never as additional fields on the link itself. The schema is FIXED.
- **No emotions at universe level** — No valence, no ambivalence, no drives, no limbic modulation on L3 links. These are L1 concerns. If a citizen feels something about a relationship, that feeling lives in their L1 graph, not on the L3 link.
- **No per-universe customization of dimensions** — All universes (La Serenissima, Lumina Prime, Contre-Terre, etc.) use the identical 11 dimensions. No universe adds or removes dimensions.

## TRADEOFFS (canonical decisions)

- When **expressiveness** conflicts with **uniformity**, choose uniformity. A less expressive but universal link is better than a perfectly descriptive but custom one. The synthesis grammar compensates for lost expressiveness.
- When **precision** conflicts with **boundedness**, choose boundedness. We accept approximate crystallization (losing some detail) to preserve graph size limits.
- When **trust granularity** conflicts with **simplicity**, choose simplicity. Trust is one float [0, 1] per link direction. Richer trust models (competence trust vs integrity trust) are deferred.
- We accept the cost of computing derived link names at query time to preserve the invariant that dimensions are the source of truth.

## SUCCESS SIGNALS (observable)

- Every link returned by `graph_query` has all 11 dimensions populated (no nulls, no defaults-at-read-time)
- No node in any L3 graph carries a `trust` field — trust is always computed from incoming links
- Link `type` fields match the output of the synthesis grammar when recomputed from dimensions
- Graph node count stabilizes after macro-crystallization cycles (does not grow monotonically)
- Physics tick completes in under 1 second regardless of graph size (crystallization keeps node count bounded)
- No L3 link carries any limbic dimension (valence, ambivalence, curiosity, care, etc.)

---

<!-- @mind:proposition Consider adding a "confidence" dimension in v2 for epistemic relationships (e.g., "we believe X is true with confidence 0.8") -->

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
