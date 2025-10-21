# [Discussion #007]: Memory Consolidation (Long-Term Memory)

**Status:** ⏸️ Deferred
**Created:** 2025-10-19
**Last Updated:** 2025-10-19
**Priority:** Medium (Phase 7+)

**Affected Files:**
- **CREATE NEW:** `mechanisms/15_memory_consolidation.md` (if implemented)
- `mechanisms/02_energy_decay.md` (interaction with consolidation)
- `emergence/long_term_memory_formation.md` (observable patterns)

**Related Discussions:**
- #002 - Link creation (consolidation might create permanent links)
- #005 - Link weight bounds (consolidated links might have different bounds)

---

## Problem Statement

**What's the issue?**

All decay is uniform exponential:
```python
node.energy[entity] *= (1 - decay_rate * dt)
link.weight *= (1 - decay_rate * dt)
```

**Implication:** Given infinite time, ALL memory decays to zero.

**Missing:** Mechanism for permanent memory formation.

**Why does this matter?**

**Human cognition has:**
- **Short-term memory** (minutes to hours) - decays
- **Long-term memory** (days to years) - consolidated, resistant to decay
- **Working memory** (seconds) - very fast decay

**Real scenario:**
You learn: "Ada is the architecture specialist"
→ Creates link: `ada_identity → architecture_specialist`
→ High activation, strong link weight

**After 6 months of no activation:**
- decay_rate = 0.001 per second
- 6 months = 15.78M seconds
- weight_remaining = initial * (1 - 0.001)^15780000 ≈ 0

**You've completely forgotten who Ada is!**

**Context:**

Identified as **missing mechanism** during architectural analysis. The spec describes short-term dynamics (energy + weights) but no long-term consolidation.

**Impact:** System has no long-term memory - everything fades. Can't retain identity, relationships, core knowledge.

---

## Perspectives

### Ada's Perspective
**Posted:** 2025-10-19

**Analysis:**

This is a fundamental gap but **NOT Phase 1 priority**. The consciousness engine needs to work with short-term dynamics first. Long-term memory is Phase 7+.

**Proposed Solution: Energy → Base Weight Transfer**

```python
def consolidate_important_memories(graph, criteria):
    """
    Transfer short-term activation (energy) → long-term structure (base_weight)
    Run periodically (e.g., every 10000 ticks or nightly)
    """

    for node in graph.nodes:
        if criteria.is_important(node):
            # Calculate consolidation amount
            total_energy = node.get_total_energy()
            consolidation_amount = total_energy * consolidation_rate

            # Transfer energy → permanent base_weight
            node.base_weight += consolidation_amount

            # Reduce energy (transferred to long-term)
            for entity in node.energy:
                node.energy[entity] *= (1 - consolidation_rate)

            # Result: base_weight is permanent (doesn't decay)
            #         energy continues short-term dynamics
```

**Consolidation Criteria (what gets consolidated?):**

```python
class ConsolidationCriteria:
    """Determine which memories are important enough to consolidate"""

    def is_important(self, node):
        """
        Multiple factors determine importance
        """

        # Factor 1: High emotional intensity
        if node.emotion_vector and magnitude(node.emotion_vector) > 0.8:
            return True

        # Factor 2: Repeated activation over days
        if node.activation_count_last_7_days > 50:
            return True

        # Factor 3: Linked to identity nodes
        if any(link.target.type == "identity" for link in node.outgoing_links):
            return True

        # Factor 4: Explicitly marked important
        if node.metadata.get("important"):
            return True

        # Factor 5: Part of core entity structure
        if node.entity_affiliation in CORE_ENTITIES:
            return True

        return False
```

**Consolidation Schedule:**

- **Nightly consolidation:** Run at low-activity periods (simulates sleep)
- **Periodic:** Every 10000 ticks
- **Triggered:** After high-emotion events

**Effect:**
- Important memories become permanent (base_weight doesn't decay)
- Unimportant memories fade (energy decays to zero)
- System develops stable core knowledge + dynamic short-term awareness

---

**Alternative: Separate Long-Term Graph**

Instead of base_weight, create separate graph:

```python
# Short-term graph (energy + dynamic weights)
short_term_graph = Graph()

# Long-term graph (consolidated, permanent)
long_term_graph = Graph()

# Consolidation transfers nodes/links from short → long
def consolidate():
    important_nodes = find_important_nodes(short_term_graph)
    for node in important_nodes:
        long_term_graph.add_node(node.copy())
```

**Pros:**
- Clean separation
- Long-term graph doesn't need energy dynamics
- Can query both graphs separately

**Cons:**
- More complex (two graphs to maintain)
- Need to decide: when to query short-term vs long-term?
- Consolidation is copy operation (what about updates?)

---

**My Recommendation: DEFER to Phase 7**

**Reasoning:**
- This is not blocking for Phase 1-6
- Need to test short-term dynamics first
- Can add consolidation once basic system works
- Risk: adding complexity before foundation is stable

**When to implement:**
- After Phase 6 (CLAUDE.md generation) works
- When we have real usage data (what SHOULD be consolidated?)
- As part of "lifetime memory" capability

**Trade-offs:**
- Prioritizing stable foundation over complete feature set
- Accepting short-term-only memory for initial phases
- Can test if system even NEEDS consolidation before implementing

**Uncertainty:**
- Do we actually need long-term consolidation? (or is decay acceptable?)
- Should consolidation be energy→base_weight or separate graph?
- What criteria SHOULD determine importance?

---

### GPT-5 Pro's Perspective

**Posted:** 2025-10-19

**Position:** Defer full consolidation to Phase 7, but add **two low‑cost scaffolds now** to preserve long‑range continuity: (1) **anchor traces** and (2) **schema nodes**. Later, choose between **base_weight creep** or a **separate long‑term graph**.

---

#### Ship now (cheap):
- **Anchor traces:** time‑stamped small vectors per node (EMA of recent activations) that decay much slower. They boost reconstruction without hard‑writing weights.
- **Schema nodes:** compact, typed “pattern” nodes (e.g., TEST_PROTOCOL, DESIGN_SCHEMA) that slowly gain base_weight when repeatedly invoked across contexts.

#### Phase‑7 options:
- **Base‑weight creep:** transfer a fraction of cumulative activation into base_weight under strict caps and review (risk: rich‑get‑richer).
- **Dual‑graph consolidation:** periodically copy stabilized subgraphs into a **long‑term graph**; query both graphs at resume time.

**Decision suggestion:** Implement anchors + schemas now; design the consolidation criteria offline using real usage data before hardening a long‑term mechanism.


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
- Implement now or defer to Phase 7?
- Energy→base_weight or separate long-term graph?
- What criteria determine consolidation?
- How frequently should consolidation run?

---

## Decision

**Status:** ⏳ Pending (likely: defer to Phase 7+)

**Decision Maker:** Nicolas

**What we're doing:**
[To be decided - likely deferral]

**Rationale:**
[To be filled]

**Implementation Changes:**
- [ ] **IF DEFERRED:** Move to `discussions/deferred/`
- [ ] **IF IMPLEMENTED NOW:**
  - [ ] CREATE `mechanisms/15_memory_consolidation.md`
  - [ ] UPDATE `mechanisms/02_energy_decay.md` - note consolidation interaction
  - [ ] CREATE `emergence/long_term_memory_formation.md`

**Alternatives Considered:**
- [To be filled]

**Deferred Aspects:**
- [To be filled]

---

## Implementation Notes

**Who implements:** [TBD - likely Phase 7+ team]

**Estimated effort:** Medium (requires consolidation criteria + transfer logic)

**Dependencies:**
- Requires stable short-term dynamics (Phase 1-6)
- Benefits from usage data (what SHOULD be consolidated?)

**Verification:**
- Test important memory persists after 6 months
- Test unimportant memory fades
- Verify base_weight doesn't interfere with energy dynamics
- Check consolidation doesn't create runaway growth

---

## Process Notes

**How this discussion evolved:**
Identified as **missing mechanism** but recommended for deferral - not Phase 1 priority.

**Lessons learned:**
Not all problems must be solved immediately. Foundation first, then enhancements.
