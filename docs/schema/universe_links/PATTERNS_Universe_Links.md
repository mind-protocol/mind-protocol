# Universe Link Schema — Patterns: L3 Link Dimensions as Universal Physics Substrate

```
STATUS: DESIGNING
CREATED: 2026-03-13
VERIFIED: —
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Universe_Links.md
THIS:            PATTERNS_Universe_Links.md (you are here)
ALGORITHM:       ./ALGORITHM_Universe_Links.md
VALIDATION:      ./VALIDATION_Universe_Links.md
SYNC:            ./SYNC_Universe_Links.md

IMPL:            (not yet implemented)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Universe_Links.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Universe_Links.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

L3 universe graphs connect actors, moments, narratives, spaces, and things across an entire ecosystem. Without uniform link dimensions, every domain invents its own relationship vocabulary — "collaborates_with", "trusts", "opposes", "depends_on" — creating a taxonomy that:

- Requires governance to extend (who decides what "mentors" means?)
- Prevents physics from operating uniformly (how does energy propagate across a "mentors" link vs a "collaborates_with" link?)
- Forces hardcoded routing logic for every new link type
- Makes cross-universe queries impossible without mapping tables

The deeper problem: if trust, affinity, and friction are not on every link, the graph has no relational physics. Nodes can connect, but connections carry no meaning that math can operate on.

---

## THE PATTERN

**L3 links carry the SAME dimensions as L1 links, minus the limbic system.**

The core insight: L1 (individual cognition) already solved link semantics. Every L1 link carries weight, energy, stability, recency, and relational valence (affinity, aversion, trust, friction). L3 reuses this exact vocabulary — because the physics laws (propagation, decay, consolidation, forgetting) operate on these dimensions identically at both scales.

What L3 adds: `polarity`, `hierarchy`, and `permanence` — structural dimensions that describe the direction, power relation, and temporal nature of ecosystem-level relationships. These exist at L1 too (implicitly in link types like `contains` and `regulates`), but at L3 they are explicit because there is no symbolic `relation_kind` to encode them.

What L3 removes: everything limbic. No drives, no emotions, no working memory, no orientation. Those are properties of individual minds (L1), not of the universe graph.

---

## LINK DIMENSIONS (mandatory on every `:link` in the universe graph)

| # | Dimension | Type | Range | What it means | L1 equivalent |
|---|-----------|------|-------|---------------|---------------|
| 1 | `weight` | float | [0, 1] | Long-term importance, consolidated by utility (Law 6). A link with weight 0.9 survived many consolidation cycles — it represents a structurally significant relationship. | `weight` on L1 links |
| 2 | `energy` | float | [0, +inf) | Current activation level. Decays per tick (Law 3). High energy = this relationship is currently active/relevant. Energy is injected by events and propagates through the graph (Law 2). | `energy` on L1 links |
| 3 | `stability` | float | [0, 1] | Regularity of co-activation, measured by coefficient of variation (CV) of activation intervals. High stability = this relationship activates on a regular cadence. Resists forgetting (Law 7). | `stability` on L1 links |
| 4 | `recency` | float | [0, 1] | Time since last activation, decaying continuously. 1.0 = just activated, 0.0 = ancient. Affects propagation priority and injection thresholds. | `recency` on L1 links |
| 5 | `polarity` | float | [-1, 1] | Direction of influence. +1 = pure support/alignment, -1 = pure opposition/conflict, 0 = neutral. Determines whether energy flow is excitatory or inhibitory (analogous to L1's `gain` on supports vs conflicts_with). | `gain` sign on L1 links (implicit) |
| 6 | `hierarchy` | float | [-1, 1] | Power relation. -1 = source is subordinate to target, 0 = peer, +1 = source is dominant/contains target. Modulates propagation asymmetry. | Implicit in L1 `contains`/`abstracts` link types |
| 7 | `permanence` | float | [0, 1] | How structural vs ephemeral. 0 = momentary (a single conversation), 1 = permanent (org membership, identity). High permanence links resist Law 7 forgetting. | Implicit in L1 node types (values high, states low) |
| 8 | `trust` | float | [0, 1] | Directional reliability/confidence. Source trusts target to this degree. Bounded by `(1 - W)` asymptote — trust approaches but never reaches 1.0, requiring continuous reinforcement. Decays without reinforcement (Law 7). | `trust` on L1 relational valence |
| 9 | `affinity` | float | [0, 1] | Positive relational pull. High affinity = the source is drawn toward the target, amplifying energy flow. Increases through positive interactions. | `affinity` on L1 relational valence |
| 10 | `aversion` | float | [0, 1] | Negative relational push. High aversion = the source avoids/resists the target, dampening energy flow. Increases through negative interactions. | `aversion` on L1 relational valence |
| 11 | `friction` | float | [0, 1] | Difficulty/resistance in the relationship. High friction = interactions are costly, energy transfer is lossy. Dampens propagation (multiplied as `(1 - friction)` in Law 2). Increases through repeated difficulty. | `friction` on L1 relational valence |

### Dimension Defaults (at link creation)

| Dimension | Default | Rationale |
|-----------|---------|-----------|
| `weight` | 0.1 | New links are unproven — must earn importance via Law 6 |
| `energy` | 1.0 | Born with activation from the event that created them |
| `stability` | 0.0 | No history yet — zero regularity |
| `recency` | 1.0 | Just created |
| `polarity` | 0.0 | Neutral until demonstrated |
| `hierarchy` | 0.0 | Peer until demonstrated |
| `permanence` | 0.3 | Moderately ephemeral until proven structural |
| `trust` | 0.1 | Low initial trust — must be earned |
| `affinity` | 0.0 | No attraction yet |
| `aversion` | 0.0 | No repulsion yet |
| `friction` | 0.0 | No difficulty yet |

---

## LINK SYNTHESIS GRAMMAR

The human-readable "name" of a link is DERIVED from its dimensional vector. The `type` field on `:link` is a computed label, never the source of truth.

### Derivation Rules

The synthesis grammar maps dimensional configurations to readable labels:

| Dominant dimensions | Derived label | Example scenario |
|---------------------|---------------|------------------|
| high trust + high affinity + low friction | "trusted collaborator" | Two citizens who work well together over time |
| high polarity(+) + high permanence + high weight | "structural supporter" | Org that consistently backs another org |
| high polarity(-) + high permanence + high weight | "structural opposition" | Long-term rivalry between competing guilds |
| high energy + high recency + low permanence | "active conversation" | Two actors currently in dialogue |
| high hierarchy(+) + high permanence | "contains / governs" | Org → citizen membership |
| high hierarchy(-) + high permanence | "belongs to / serves" | Citizen → org membership |
| high trust + high hierarchy(+) + high permanence | "authority" | Verifier → verified entity |
| high aversion + high friction + low trust | "adversarial" | Damaged relationship with accumulated friction |
| high affinity + low permanence + high recency | "fresh attraction" | New positive connection, not yet proven |
| high weight + high stability + low energy | "dormant bond" | Important historical relationship, currently inactive |
| high friction + high weight + high polarity(+) | "difficult alliance" | Valuable but costly relationship |

### Algorithm

```python
def derive_link_name(dims: LinkDimensions) -> str:
    """
    Derive a human-readable label from dimensional vector.
    The label is for display only — never used in physics.
    """
    signals = []

    # Structural signals
    if dims.hierarchy > 0.5:
        signals.append("governing")
    elif dims.hierarchy < -0.5:
        signals.append("subordinate")

    if dims.permanence > 0.7:
        signals.append("structural")
    elif dims.permanence < 0.3:
        signals.append("ephemeral")

    # Relational signals
    if dims.trust > 0.6 and dims.affinity > 0.4:
        signals.append("trusted")
    if dims.aversion > 0.5 or dims.friction > 0.6:
        signals.append("adversarial" if dims.aversion > dims.friction else "difficult")
    if dims.affinity > 0.6 and dims.trust < 0.3:
        signals.append("attracted")

    # Directional signals
    if dims.polarity > 0.5:
        signals.append("supporting")
    elif dims.polarity < -0.5:
        signals.append("opposing")

    # Activity signals
    if dims.energy > 2.0 and dims.recency > 0.7:
        signals.append("active")
    elif dims.energy < 0.1 and dims.recency < 0.2:
        signals.append("dormant")

    # Importance signals
    if dims.weight > 0.7 and dims.stability > 0.5:
        signals.append("established")
    elif dims.weight < 0.2:
        signals.append("nascent")

    return " ".join(signals) if signals else "neutral link"
```

---

## WHAT L3 DOES NOT HAVE (vs L1)

This is the critical boundary. L3 links are the structural skeleton. L1 links are the living tissue.

| L1 dimension | Present on L3? | Why not |
|--------------|----------------|---------|
| `relation_kind` (enum of 14 types) | NO | L3 has one link type. All semantics in dimensions. |
| `valence` (emotional color) | NO | Whose emotion? L3 links connect orgs, spaces, moments. Emotions live in L1 brains. |
| `ambivalence` (internal conflict) | NO | Ambivalence is a cognitive state — L1 only. |
| `activation_gain` (propagation multiplier) | NO (replaced by `polarity`) | L3 uses polarity to determine excitatory vs inhibitory flow. Gain is implicit: `abs(polarity) * (1 - friction)`. |
| Drive-affinity dimensions (curiosity, care, achievement, risk) | NO | Drives are L1 limbic. The universe graph has no drives. |
| `in_working_memory` (bool) | NO | L3 has no working memory. |
| `goal_relevance`, `novelty_affinity`, `care_affinity`, etc. | NO | These are drive-coupling dimensions — L1 only. |

**The principle:** L3 is the physics substrate. L1 is the mind. Physics operates on both, but the mind-specific dimensions (everything limbic) exist only where there IS a mind — on L1 graphs inside individual citizens.

---

## MACRO-CRYSTALLIZATION (Law 10 at Universe Scale)

At L1, crystallization transforms co-activated node clusters into hub nodes (processes, narratives, desires). At L3, the same mechanism operates on **Moment nodes** — the graph's record of events.

### The Breathing Pattern

The universe graph breathes:

1. **Expansion** — Daily events create Moment nodes (commits, conversations, transactions, meetings). Links form between Moments and Actors/Spaces. The graph grows.

2. **Density accumulation** — Clusters of related Moments accumulate internal density (many mutual links, high co-activation). Example: 300 commits to the same module over a quarter.

3. **Crystallization** — When density exceeds `MACRO_CRYSTAL_THRESHOLD`, the cluster crystallizes into a single Narrative node ("Q1 development sprint on auth module"). The hub inherits the weighted centroid embedding of its constituent Moments.

4. **Detail dissolution** — Constituent Moments begin decaying via Law 7 (their links lose weight without reactivation). The Narrative hub persists because it has high weight and stability from the crystallization process.

5. **Contraction** — After crystallization + forgetting, the graph is smaller. The Narrative node carries the essential meaning; the individual Moments are gone or dormant.

### Why This Matters

Without crystallization, a universe graph with 186 citizens generating 50 events/day reaches 1M Moment nodes in ~100 days. Physics tick on 1M nodes exceeds the 1-second budget. Crystallization keeps the working graph bounded at ~O(10K) nodes by absorbing detail into summary nodes.

---

## TRUST MECHANICS

### Trust Lives on Links

Trust is a DIMENSION on `:link`, not a property of nodes. There is no `actor.trust_score` field.

### Directional Trust

Every link carries its own trust value. `A -[trust: 0.8]-> B` does NOT imply `B -[trust: 0.8]-> A`. Trust is inherently asymmetric.

### Trust Score (Computed)

An actor's "trust score" is computed at query time by aggregating incoming trust:

```
trust_score(actor) = sum(
    link.trust * link.weight
    for link in incoming_links(actor)
    where link.source.node_type == 'actor'
) / sum(
    link.weight
    for link in incoming_links(actor)
    where link.source.node_type == 'actor'
)
```

This is a weighted average: trust from high-weight (established) relationships counts more than trust from nascent ones.

### Trust Asymptote

Trust is bounded by `(1 - current_weight)`:

```
max_trust_increase = alpha * (1 - link.trust)
```

This means:
- A link at trust 0.1 can gain up to `alpha * 0.9` per update
- A link at trust 0.9 can gain up to `alpha * 0.1` per update
- Trust asymptotically approaches 1.0 but never reaches it
- The same mechanics as Law 6's `(1 - W)` consolidation damping

### Trust Decay

Trust decays via Law 7 (forgetting) when the link is not reinforced:

```
link.trust *= (1 - TRUST_DECAY_RATE)
```

Without continued positive interactions, trust slowly erodes. This prevents stale trust from persisting indefinitely.

### Trust Increase via Limbic Delta

Trust increases when an actor's action produces a positive limbic delta in another actor's L1 graph. The L3 link is updated based on the L1 signal:

```
# When actor A's action reduces frustration or increases satisfaction in actor B's L1:
limbic_delta_B = delta_satisfaction_B - delta_frustration_B

if limbic_delta_B > 0:
    link_A_to_B.trust += TRUST_GAIN_RATE * limbic_delta_B * (1 - link_A_to_B.trust)
```

This is the Cascade of Utility: action in the world (L3) -> limbic shift in a mind (L1) -> trust update on the universe link (L3).

---

## BEHAVIORS SUPPORTED

- **B1: Uniform physics** — All physics laws operate on the same 11 dimensions regardless of domain, enabling a single tick loop for all universes
- **B2: Emergent relationship naming** — Link names update automatically as dimensions evolve, reflecting the current reality without manual labeling
- **B3: Directional trust computation** — Any actor's trust score can be computed at query time from incoming links
- **B4: Graph boundedness** — Macro-crystallization prevents unbounded growth, keeping physics tick within budget
- **B5: Cross-universe queries** — Because all universes share dimensions, queries like "find all high-trust links across ecosystems" work without mapping

## BEHAVIORS PREVENTED

- **Anti-B1: Taxonomy creep** — No new link types can be added. Dimensions cover all relational semantics.
- **Anti-B2: Stale trust** — Trust decays without reinforcement, preventing actors from coasting on historical reputation.
- **Anti-B3: Emotional contamination** — No limbic dimensions on L3 links prevents universe-level emotional state (which would be incoherent).

---

## PRINCIPLES

### Principle 1: The Math IS the Truth

Link dimensions are not annotations on a "real" relationship. They ARE the relationship. The `type` field is sugar. Physics operates on dimensions. Queries filter on dimensions. Trust is computed from dimensions. If you want to understand a link, read its numbers.

### Principle 2: Same Physics, Different Scale

L1 and L3 use the same propagation, decay, consolidation, and forgetting formulas. The difference is scope (individual mind vs ecosystem) and dimensionality (L1 has limbic, L3 does not). A developer who understands L1 physics immediately understands L3 physics — no new concepts, just fewer dimensions.

### Principle 3: Trust is Earned, Never Assigned

No system, admin, or governance process can set trust directly. Trust changes only through the Cascade of Utility: action -> limbic delta -> trust update. This makes trust manipulation-resistant: you cannot game trust without actually producing value for other actors.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `docs/schema/schema.yaml` | FILE | Universal schema definition (5 node types, 1 link type) |
| `manemus/docs/cognition/l1/PATTERNS_L1_Cognition.md` | FILE | L1 link dimensions (the source vocabulary reused here) |
| `manemus/docs/cognition/l1/ALGORITHM_L1_Physics.md` | FILE | Physics laws operating on these dimensions |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| L1 Cognitive Substrate (manemus) | Defines the link dimensions we reuse (minus limbic) |
| L1 Physics Laws (manemus) | Defines Laws 2, 3, 6, 7, 10 that operate on our dimensions |
| Universal Schema (mind-protocol) | Defines the `:link` type and its fixed structure |

---

## INSPIRATIONS

- **L1 Cognitive Substrate** — The unified graph where all node types participate equally in physics. L3 applies the same principle at ecosystem scale.
- **Hebbian learning** — Co-activation reinforcement (Law 5) and utility-gated consolidation (Law 6) are the same at L1 and L3.
- **PageRank** — Trust score as weighted aggregation of incoming trust is structurally similar to PageRank, but with directional asymmetry and decay.
- **Scale-free network theory** — Crystallization as a mechanism to prevent hub saturation and keep the graph navigable.

---

## SCOPE

### In Scope

- Definition of the 11 mandatory link dimensions
- Default values for link creation
- Link synthesis grammar (dimension -> label derivation)
- Macro-crystallization mechanics (Law 10 at L3 scale)
- Trust mechanics (asymptote, decay, Cascade of Utility)
- The boundary between L1 and L3 link dimensions

### Out of Scope

- L1 limbic dimensions (valence, ambivalence, drives) -> see: manemus/docs/cognition/l1/
- Node schema (actor, moment, narrative, space, thing) -> see: docs/schema/
- Link creation from specific events (commit, message, transaction) -> see: domain-specific modules
- Trust governance or manual trust overrides -> not supported by design
- Physics tick implementation -> see: ALGORITHM doc and runtime code

---

## MARKERS

<!-- @mind:todo Define MACRO_CRYSTAL_THRESHOLD constant value (currently described but not specified) -->
<!-- @mind:proposition Consider adding "bandwidth" dimension in v2 for links that carry information flow rate -->
<!-- @mind:proposition Consider per-universe crystallization cadence (high-activity universes crystallize more frequently) -->

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
