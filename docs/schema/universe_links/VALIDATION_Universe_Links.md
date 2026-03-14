# Universe Link Schema — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Universe_Links.md
PATTERNS:        ./PATTERNS_Universe_Links.md
ALGORITHM:       ./ALGORITHM_Universe_Links.md
THIS:            VALIDATION_Universe_Links.md (you are here)
SYNC:            ./SYNC_Universe_Links.md
```

---

## PURPOSE

**Validation = what we care about being true.**

Not mechanisms. Not test paths. Not how things work.

What properties, if violated, would mean the system has failed its purpose?

These are the value-producing invariants — the things that make the L3 link schema worth building.

---

## INVARIANTS

### V1: Complete Dimensional Coverage

**Why we care:** If any link is missing a dimension, physics equations operating on that dimension produce undefined behavior. Propagation (Law 2) divides by zero on missing friction. Consolidation (Law 6) cannot compute utility on missing weight. The entire physics pipeline depends on all 11 dimensions being present and within bounds on every link, always.

```
MUST:   Every `:link` in every L3 universe graph has all 11 dimensions
        populated with values within their defined ranges:
        - weight:     [0, 1]
        - energy:     [0, +inf)
        - stability:  [0, 1]
        - recency:    [0, 1]
        - polarity:   [-1, 1]
        - hierarchy:  [-1, 1]
        - permanence: [0, 1]
        - trust:      [0, 1]
        - affinity:   [0, 1]
        - aversion:   [0, 1]
        - friction:   [0, 1]

NEVER:  A link exists with a null, NaN, or out-of-range dimension value
NEVER:  A link is created without initializing all 11 dimensions
```

### V2: Trust Lives Exclusively on Links

**Why we care:** If trust is stored on nodes, it becomes a monolithic reputation that cannot distinguish between directional relationships. Actor A trusting Actor B is independent of Actor C trusting Actor B. If trust lives on the node, these two signals collapse into one number, destroying directional information. Every system that computes "how much does the ecosystem trust actor X" must aggregate from links — there is no shortcut.

```
MUST:   Trust is a dimension on `:link` edges, never a property of nodes
MUST:   An actor's "trust score" is computed at query time by aggregating
        incoming link trust values weighted by link weight (Algorithm 5)

NEVER:  A node in any L3 graph carries a `trust`, `trust_score`, or
        `reputation` field
NEVER:  Trust is written directly to a node by any process
```

### V3: Link Names Are Derived, Not Canonical

**Why we care:** If link names (types/labels) are treated as the source of truth, they become a taxonomy that must be governed, versioned, and mapped. Worse, two links with identical dimensions but different names would be treated differently by queries, creating semantic inconsistency. The synthesis grammar (Algorithm 6) ensures that names always reflect the current dimensional state — if dimensions change, the name changes automatically.

```
MUST:   The `type` field on `:link` is recomputable from the 11 dimensions
        at any time via Algorithm 6 (derive_link_name)
MUST:   No physics operation, propagation rule, or consolidation formula
        references the `type` field — only dimensions

NEVER:  A query filters or routes based on link `type` as the primary
        discriminator (dimensions must be used instead)
NEVER:  A link name is set manually or hardcoded outside the synthesis grammar
```

### V4: Graph Size Bounded by Crystallization

**Why we care:** Without macro-crystallization, the universe graph grows without bound as events accumulate. At 186 citizens generating ~50 events/day, the graph reaches 1M Moment nodes in ~100 days. Physics tick on 1M nodes exceeds the 1-second budget. The graph must breathe: expand with events, contract during crystallization. After N crystallization cycles, total active nodes must stabilize below a ceiling C.

```
MUST:   After K crystallization cycles (K > 3), the count of active
        (non-dormant) nodes stabilizes: |nodes_active(t+1) - nodes_active(t)| < GROWTH_TOLERANCE
MUST:   Physics tick completes in < 1 second for any graph that has run
        at least 3 crystallization cycles

NEVER:  Active node count grows monotonically beyond MAX_ACTIVE_NODES
        without triggering crystallization
NEVER:  Crystallization produces more nodes than it absorbs (net node count
        must decrease or remain stable after crystallization)
```

### V5: No Limbic Dimensions on L3 Links

**Why we care:** Limbic dimensions (valence, ambivalence, drives, emotions, working memory flags) are properties of individual minds — L1 graphs. Putting them on L3 links would create incoherent physics: whose emotion does a link between two orgs carry? Which mind's curiosity modulates a commit→module link? The L1/L3 boundary is where individual subjectivity meets shared structure. Violating this boundary produces a universe graph that thinks it has feelings.

```
MUST:   No `:link` in any L3 graph carries any of these dimensions:
        valence, ambivalence, activation_gain, goal_relevance,
        novelty_affinity, care_affinity, achievement_affinity,
        risk_affinity, in_working_memory, or any drive-coupling field

NEVER:  An L3 link is created or updated with a limbic dimension
NEVER:  An L3 physics tick references limbic state (drives, emotions)
        when computing propagation, decay, or consolidation on L3 links
```

### V6: Trust Bounded by Asymptote

**Why we care:** If trust can reach 1.0, it represents absolute certainty — which is epistemically dangerous and creates a governance problem (who deserves absolute trust?). The asymptotic bound `(1 - current_trust)` ensures that trust increases face diminishing returns, requiring exponentially more positive interactions to approach the ceiling. This mirrors real-world trust dynamics: the first good interaction moves trust a lot; the thousandth barely moves it at all. Without this bound, a burst of positive events could pump trust to 1.0, creating an unearned maximum.

```
MUST:   Trust increase on any single event is bounded by:
        delta_trust <= TRUST_GAIN_RATE * limbic_delta * (1 - current_trust)
MUST:   Trust approaches 1.0 asymptotically — the function
        trust(n) = 1 - (1 - trust_0) * (1 - rate)^n never equals 1.0
        for finite n

NEVER:  Trust equals exactly 1.0 on any link (floating-point edge case:
        clamp to 0.999 if rounding would produce 1.0)
NEVER:  Trust increases by more than 0.1 in a single event (hard cap
        as safety net beyond the asymptotic math)
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable |
| **HIGH** | Major value lost | Degraded severely |
| **MEDIUM** | Partial value lost | Works but worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Complete dimensional coverage — physics correctness | CRITICAL |
| V2 | Trust directionality — no trust on nodes | CRITICAL |
| V3 | Names are derived — no taxonomy lock-in | HIGH |
| V4 | Graph boundedness — physics stays within time budget | HIGH |
| V5 | L1/L3 boundary — no emotional contamination | HIGH |
| V6 | Trust asymptote — no absolute trust | MEDIUM |

---

## MARKERS

<!-- @mind:todo Define concrete values for MAX_ACTIVE_NODES and GROWTH_TOLERANCE in V4 -->
<!-- @mind:proposition Consider V7: "Energy conservation — total energy in graph is bounded by injection minus decay" -->
<!-- @mind:proposition Consider V8: "Symmetry — if link A->B exists with hierarchy +0.8, link B->A (if it exists) must have hierarchy close to -0.8" -->

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
