# Specification Contradiction: Energy Activation Detection

**Date:** 2025-10-21
**Issue:** Internal contradiction in `05_sub_entity_system.md` about how activation is detected
**Impact:** CRITICAL - determines core behavior of sub-entity system

---

## The Contradiction

The specification **contradicts itself** about whether activation uses **total energy** or **per-channel energy**.

### Version A: Total Energy (Lines 1518-1521, Section 1.1)

**Location:** `05_sub_entity_system.md:1518-1521`

```python
def is_sub_entity(node: Node) -> bool:
    """
    Is this node currently a sub-entity?

    Simple: total energy >= activation threshold
    """
    total_energy = node.get_total_energy()  # Sum across all entity energies
    return total_energy >= ACTIVATION_THRESHOLD
```

**Also supported by:**
- Line 1556-1557: "When: total_energy >= threshold / Result: Node becomes sub-entity"
- Line 1562-1563: "While: total_energy >= threshold / Behavior: Sub-entity continues"
- Line 1571-1572: "When: total_energy < threshold / Result: Sub-entity ceases"
- Line 1595: "Small entities (few active nodes, low total energy)"
- Line 1628: "When a weak entity (low total energy, small extent)"
- Line 2006: "Dissolution: Total energy drops below threshold"
- Line 3202-3203: `source_active = link.source.get_total_energy() >= ACTIVATION_THRESHOLD`

**Summary:** Section 1.1-1.4 consistently uses **total energy** for activation detection.

---

### Version B: Per-Channel Energy (Lines 2019-2025)

**Location:** `05_sub_entity_system.md:2019-2025`

```
Each node maintains separate energy values per entity. When multiple entities
are active at the same node, their energies coexist as independent channels.
The node's total energy is the sum across all entity channels.

When computing activation (Section 1.4), threshold is checked per entity channel.
A node can be "active for entity A" while "inactive for entity B" if A's energy
at that node exceeds threshold but B's doesn't.

For traversal purposes, an entity only "sees" its own energy channel and the
TOTAL energy of other entities (summed, not individuated).
```

**Summary:** This section says activation is **per-channel**, allowing same node to be "active for A but inactive for B".

---

## Evidence from 05_sub_entity_weight_learning_addendum.md

**Lines 105-106:**
```python
A node is **active** if:
node.energy >= node.threshold
```

Uses `node.energy` (singular) - doesn't mention channels.

**Lines 467-469:**
```
**Nodes** carry dynamic activation energy E (unbounded)
**Links** have static metadata field `energy` (affects valence, bounded [0,1])
Links do NOT carry activation energy; they transport node energy via strides
```

Again, singular energy on nodes.

**Conclusion:** Addendum uses **singular energy**, aligning with Version A (total energy).

---

## Engineering Plan Alignment

**Your provided engineering plan assumes:**
```python
# CORRECT (per plan)
active_nodes = [n for n in graph.nodes if n.get_total_energy() >= n.get_threshold()]
```

**This aligns with Version A** (lines 1518-1521, Section 1.1).

**This CONTRADICTS Version B** (lines 2019-2025).

---

## Which Is Correct?

### Arguments for Version A (Total Energy):

1. **Phenomenology section (0.1)** describes sub-entity as "total energy × link weights" (line 66, 431, 1436)
2. **Lifecycle section (1.3)** explicitly uses `total_energy >= threshold` (lines 1556, 1562, 1571)
3. **Newness gate (addendum §3.2)** uses `node.energy >= node.threshold` (singular)
4. **Code example in spec** at line 3202 uses `get_total_energy()`
5. **Consistency:** 90% of references use total energy
6. **Simplicity:** One activation state per node, not N states for N channels

### Arguments for Version B (Per-Channel):

1. **Multi-entity coordination section** (lines 2019-2025) explicitly states it
2. **Allows overlapping activations** - same node can be active for different entities simultaneously
3. **Biological plausibility** - different brain regions can activate same memory differently

### Problem with Version B:

If activation is per-channel, then:
- What does `node.get_total_energy()` mean?
- How does "sub-entity = any active node" work when activation is multi-state?
- Why do all lifecycle examples use total energy?

**Hypothesis:** Lines 2019-2025 are **OUTDATED** or describe a **different concept** (per-channel **routing** not **activation**).

---

## Recommendation

### Most Likely Truth:

**Version A (Total Energy) is correct** for activation detection. Lines 2019-2025 likely describe:

1. **Energy storage structure:** Nodes DO have per-channel energy storage (`entity_energy: Dict[str, float]`)
2. **Routing/traversal:** Entities DO only see their own channel during traversal decisions
3. **Integration sensing:** Entities DO see total energy of others for integration detection

**BUT activation (threshold crossing) uses total energy summed across all channels.**

This reconciles both versions:
- **Storage:** Per-channel (Version B correct about structure)
- **Activation:** Total energy (Version A correct about detection)
- **Traversal routing:** Per-channel (Version B correct about "seeing own channel")
- **Integration sensing:** Total of others (Version B correct about sensing)

### Proposed Clarification:

**Lines 2019-2025 should be REWRITTEN as:**

```
Each node maintains separate energy values per entity. When multiple entities
are active at the same node, their energies coexist as independent channels.
The node's total energy is the sum across all entity channels.

When computing activation, threshold is checked against TOTAL energy across
all channels. A node is either active (total >= threshold) or inactive
(total < threshold). This creates a single sub-entity per active node.

For traversal purposes, an entity accesses its own energy channel for
routing decisions, but senses the TOTAL energy of other entities at
shared nodes for integration detection.
```

---

## Impact on Engineering Plan

**Your engineering plan is CORRECT** assuming Version A (total energy activation).

**Changes needed to spec:**
1. Fix lines 2019-2025 to remove "threshold is checked per entity channel"
2. Clarify distinction between:
   - **Energy storage structure** (per-channel dict)
   - **Activation detection** (total energy sum)
   - **Traversal routing** (own channel access)
   - **Integration sensing** (total of others)

**No changes needed to plan** - it already implements the correct (Version A) interpretation.

---

## Questions for Clarification

1. **Is Version A (total energy) correct for activation?**
   - If YES: Fix lines 2019-2025 in spec
   - If NO: Rewrite all of Section 1.1-1.4 and addendum

2. **What is the TRUE purpose of per-channel energy storage?**
   - Option A: Routing decisions during traversal (entity sees own channel)
   - Option B: Multi-state activation (node can be active for some entities but not others)
   - Option C: Learning/reinforcement tracking (different entities reinforce different nodes)

3. **Can a node be "active for entity A but inactive for entity B"?**
   - If YES: How does that reconcile with "sub-entity = active node" (singular state)?
   - If NO: Fix line 2021

---

## Recommended Action

**Before implementing the engineering plan:**

1. **Confirm:** Activation uses `total_energy >= threshold` (Version A)
2. **Update spec:** Rewrite lines 2019-2025 to clarify per-channel is for storage/routing NOT activation
3. **Implement:** Follow engineering plan as written (uses total energy)

**Your engineering plan is solid - the spec just needs fixing to match it.**
