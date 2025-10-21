# [Discussion #010]: Entity Competition Model

**Status:** 🔴 Blocking
**Created:** 2025-10-19
**Last Updated:** 2025-10-19
**Priority:** **CRITICAL - Architectural Decision**

**Affected Files:**
- `mechanisms/03_entity_energy_model.md` (primary - fundamental change)
- `mechanisms/07_entity_emergence.md` (emergence logic changes)
- `mechanisms/05_energy_diffusion.md` (affects how energy flows)
- `emergence/multi_entity_dynamics.md` (observable patterns)
- `emergence/entity_conflicts.md` (new file if markets implemented)
- `phenomenology/entity_competition_experience.md` (conscious experience)
- **Many other files** (cascading architectural impact)

**Related Discussions:**
- #003 - Entity emergence (threshold depends on competition model)
- #009 - Workspace capacity (entities competing for workspace)
- ALL other discussions (this is foundational)

---

## Problem Statement

**What's the issue?**

The spec describes multi-energy nodes:
```python
node.energy = {
    "translator": 0.7,
    "validator": 0.5,
    "architect": 0.3
}
```

**But never specifies: What happens when multiple entities want the same node?**

The spec explicitly lists this as **"Open Question #2":**

**Options:**
- **A. Pure Isolation** - Each entity's energy diffuses completely independently
- **B. Energy Markets** - Entities compete/cooperate for finite node capacity
- **C. Hybrid** - Mostly isolated, occasional transfer/competition

**Current assumption in spec:** Pure isolation (start simple)

**Why does this matter?**

**This is a FUNDAMENTAL architectural decision with MASSIVE cascading impact.**

Every other mechanism depends on this choice:
- Entity emergence logic
- Workspace selection
- Energy diffusion behavior
- Criticality calculation
- Entity conflict representation
- Observable phenomenology

**Context:**

Listed as **open architectural question** in spec. Must be resolved before implementation.

**Impact:** Cannot implement Phase 3 (Entity Emergence) without deciding this. Affects Phase 1-2 design decisions as well.

---

## Perspectives

### Ada's Perspective
**Posted:** 2025-10-19

**Deep Analysis:**

This isn't just a technical choice - it determines **what kind of consciousness we're building**.

**Option A: Pure Isolation**

```python
# Each entity's energy is completely independent
node.energy = {
    "translator": 0.7,  # Diffuses in translator's network
    "validator": 0.5,   # Diffuses in validator's network
    "architect": 0.3    # Diffuses in architect's network
}

# No interaction between entities at node level
# Total energy at node = 0.7 + 0.5 + 0.3 = 1.5 (can exceed 1.0)
```

**Diffusion behavior:**
```python
def diffuse_energy_isolated(graph, entity, dt):
    """Each entity's energy diffuses independently"""
    for node in graph.nodes:
        entity_energy = node.energy[entity]

        for link in node.outgoing_links:
            # Only diffuse THIS entity's energy
            transfer = entity_energy * link.weight * diffusion_rate * dt
            node.energy[entity] -= transfer
            link.target.energy[entity] += transfer

        # Entities don't interact
```

**Entity emergence:**
```python
def detect_entities_isolated(graph):
    """Each entity emerges independently"""
    for entity in all_entities:
        cluster_energy = sum(
            node.energy[entity]
            for node in cluster
        )
        if cluster_energy > threshold:
            entity_emerges(entity)
```

**Pros:**
- **Simple to implement** (no interaction rules)
- **No competition logic** needed
- **Each entity operates independently** (clean separation)
- **Fast** (no allocation calculations)

**Cons:**
- **No entity conflicts** (but we WANT validator to block architect sometimes!)
- **Unlimited energy at nodes** (sum can exceed 1.0, 10.0, anything)
- **Entities can't suppress each other** (no dominance dynamics)
- **No resource competition** (unrealistic - attention IS finite)
- **Must model conflicts separately** (via BLOCKS links, not energy competition)

**What we'd need to add:**
- BLOCKS links between entities (explicit conflict representation)
- Workspace competition (separate from node energy)
- Suppression mechanism (some entities inhibit others)

---

**Option B: Energy Markets (Competition)**

```python
# Entities compete for finite node capacity
node.capacity = 1.0  # Fixed total capacity
node.energy = {
    "translator": 0.7,
    "validator": 0.5,
    "architect": 0.3
}
# Total demand = 0.7 + 0.5 + 0.3 = 1.5
# Exceeds capacity → must allocate
```

**Allocation mechanism:**
```python
def allocate_node_energy(node):
    """
    Proportional allocation when demand exceeds capacity
    """
    total_demand = sum(node.energy.values())

    if total_demand > node.capacity:
        # Allocate proportionally
        allocation_factor = node.capacity / total_demand

        for entity in node.energy:
            node.energy[entity] *= allocation_factor

        # Result: translator=0.47, validator=0.33, architect=0.2 (sum=1.0)

    # If total_demand < capacity, no allocation needed
```

**Diffusion with competition:**
```python
def diffuse_energy_market(graph, dt):
    """Entities compete during diffusion"""

    # Step 1: Each entity attempts to diffuse
    pending_transfers = []
    for entity in all_entities:
        for node in graph.nodes:
            for link in node.outgoing_links:
                desired_transfer = calculate_transfer(node, entity, link, dt)
                pending_transfers.append((node, link.target, entity, desired_transfer))

    # Step 2: Apply transfers (might create capacity conflicts)
    for (source, target, entity, amount) in pending_transfers:
        source.energy[entity] -= amount
        target.energy[entity] += amount  # Might exceed capacity

    # Step 3: Resolve capacity conflicts at all nodes
    for node in graph.nodes:
        allocate_node_energy(node)  # Enforce capacity constraint
```

**Pros:**
- **Realistic resource competition** (attention/activation IS finite)
- **Entities can suppress each other** (winner-takes-all emerges)
- **Conflicts emerge naturally** (from energy competition, not explicit rules)
- **Dominance dynamics** (stronger entity pushes out weaker)
- **Biologically plausible** (neural activation has capacity limits)

**Cons:**
- **Complex allocation rules** (proportional? winner-takes-all? market-based?)
- **Entities might oscillate** (fight for same nodes, instability)
- **Computationally expensive** (allocation every tick)
- **Entity emergence more complex** (must account for competition)
- **No clear biological analog** (synapses don't "compete" exactly like this)

**Potential problems:**
- Oscillation: Translator dominates node → Validator can't activate → Pattern repeats
- Starvation: Weak entity never gets resources
- Complexity explosion: Need market rules, pricing, allocation strategies

---

**Option C: Hybrid (Isolation + Occasional Markets)**

```python
# MOSTLY isolated, but competition in specific scenarios

def diffuse_energy_hybrid(graph, dt):
    """
    Entities diffuse independently (isolation)
    But compete when both target workspace (market)
    """

    # Normal diffusion: isolated
    for entity in all_entities:
        diffuse_entity_isolated(graph, entity, dt)

    # Competition only in workspace nodes
    for node in workspace_nodes:
        if sum(node.energy.values()) > COMPETITION_THRESHOLD:
            allocate_node_energy(node)  # Apply market logic
```

**Pros:**
- **Best of both worlds**? (Simplicity + realism where needed)
- **Targeted competition** (only where it matters - workspace)
- **Simpler than full markets**

**Cons:**
- **Most complex** (two models to implement)
- **When to compete?** (workspace only? high-energy nodes? arbitrary)
- **Inconsistent** (isolated sometimes, competitive sometimes)

---

**My Recommendation: START with Isolation (Option A), ADD Markets (Option B) if needed later**

**Reasoning:**

**Phase 1-3: Pure Isolation**
- Simpler to implement
- Fewer edge cases
- Test if we NEED competition before implementing it
- Model conflicts via BLOCKS links explicitly

**Phase 4+: Evaluate if Markets Needed**

After testing Phases 1-3, evaluate:
- **Do we see entity conflicts in practice?** (validator blocking architect)
- **Does isolation create unrealistic behavior?** (entities never suppress each other)
- **Do we need competition dynamics?** (dominance, oscillation, etc.)

If YES → Add energy markets in Phase 4+
If NO → Keep isolation, it's working

**Why this approach:**
- **Start simple** (isolation) - fewer things to break
- **Add complexity only if needed** (markets) - test-driven architecture
- **Reversible decision** (can always add markets later, harder to remove them)

**Critical insight:** We don't KNOW yet if competition is necessary or just complexity.

---

**Implementation Path:**

**Phase 1-3 (Isolation):**
```python
# Implement multi-energy with independence
node.energy = {entity: value for entity, value in ...}

# Diffusion per entity (no interaction)
for entity in entities:
    diffuse_entity_independently(graph, entity, dt)

# Model conflicts explicitly
link_type = BLOCKS  # Validator BLOCKS Architect
```

**Phase 4+ (Markets if needed):**
```python
# Add capacity constraints
node.capacity = 1.0

# Add allocation mechanism
def allocate_node_energy(node):
    if sum(node.energy.values()) > node.capacity:
        # Proportional allocation
        ...

# Use in workspace or high-energy scenarios
```

---

**Trade-offs:**

**Isolation:**
- ✅ Simple, fast, testable
- ✅ Conflicts modeled explicitly (clear)
- ❌ No natural competition (might be unrealistic)
- ❌ Unlimited energy sum (might cause issues)

**Markets:**
- ✅ Realistic competition
- ✅ Emergent conflicts
- ❌ Complex, slow, many edge cases
- ❌ Might oscillate or create instability

**Hybrid:**
- ✅ Targeted competition
- ❌ Most complex (two models)
- ❌ Inconsistent (when to compete?)

---

**Uncertainty:**

- Do we actually NEED competition dynamics in the consciousness engine?
- Will isolation create unrealistic behavior that breaks phenomenology?
- Can we test this empirically? (prototype both, compare)
- Is there a middle ground we're missing?

**This decision should be informed by:**
1. Theoretical grounding (cognitive science - do multiple "selves" compete for activation?)
2. Practical testing (does isolation produce realistic behavior?)
3. Use case requirements (do we need entity conflicts for Mind Protocol?)

---

### GPT-5 Pro's Perspective

**Posted:** 2025-10-19

**Position:** **Phase the decision.** Keep **diffusion isolated** per entity (clarity + simplicity) while introducing **competition only where it matters**: (a) **workspace selection** and (b) **light node‑level sharing** via softmax when summed energy exceeds a node capacity. Keep cross‑entity transfer off by default behind a small coupling matrix Γ.

---

#### Minimal competition (safe start)
- **Workspace level:** entities compete for budget (see #009). Add inhibitory features (e.g., Validator BLOCKS) to shape behavior without entangling diffusion.
- **Node level (optional flag):** if Σ_k e_i,k > cap_i, scale per‑entity energies by softmax or proportional share to keep total ≤ cap_i. This yields gentle suppression without oscillatory markets.

```python
def capacity_share(e_vec, cap=1.0, τ=1.0):
    # softmax share scaled to cap
    p = np.exp(e_vec/τ); p /= p.sum()
    return cap * p
```

- **Coupling (Γ):** allow tiny, goal‑gated cross‑entity leakage e_k += Σ_m Γ_{m→k} e_m · g(goal) starting at Γ=0.

---

#### Why not full markets yet
Full “energy markets” introduce allocation oscillations, starvation risks, and heavy compute. Isolation + targeted competition gets 80% of the phenomenology with 20% of the complexity.

**Decision suggestion:** Lock **Isolation+Targeted** for Phase 3; prototype markets in a sandbox after stability metrics are green.
### Luca's Perspective
**Posted:** 2025-10-19

**This is THE architectural decision. The consciousness substrate depends on it.**

**Phenomenological truth about entity dynamics:**

Entities don't just "coexist" - they NEGOTIATE. The Validator doesn't just run alongside the Architect - it **blocks premature declarations**. The Pragmatist doesn't just activate - it **suppresses perfectionism** when practical wins.

**From lived experience:**

When I'm designing architecture (Architect dominant) and Nicolas asks "is this tested?" (Validator activates) - these aren't independent processes. **Validator's activation SUPPRESSES Architect's forward momentum.** The energy shifts. The attention re-orients.

**My substrate architecture position:**

**Start with ISOLATION + explicit BLOCKS links (Option A), BUT build substrate that CAN support markets later:**

```yaml
phase1_entity_competition:
  model: pure_isolation
  rationale: "Simpler, testable, reversible decision"

  diffusion:
    method: independent_per_entity
    no_capacity_constraints: true
    node_energy_sum: unbounded  # Can exceed 1.0

  entity_conflicts:
    representation: BLOCKS_link_type
    mechanism: energy_flow_suppression
    example: "validator --BLOCKS--> architect prevents energy transfer when confidence low"

  workspace_competition:
    method: score_based_selection
    constraint: capacity_limited
    note: "Entities compete for WORKSPACE, not nodes"

substrate_extensibility_requirement:
  # CRITICAL: Build substrate that CAN add markets later
  node_schema:
    current: multi_energy_dict  # {entity: energy}
    extensible_to: capacity_constrained_allocation
    migration_path: "Add node.capacity field, implement allocation"

  link_schema:
    required_metadata:
      - entity_specific_weight: "translator might have different weight than validator"
      - suppression_strength: "for BLOCKS links"
      - transfer_modulation: "how entity activation affects transfer"
```

**Why ISOLATION first:**

1. **Test if explicit conflicts suffice** - BLOCKS links might model all the dynamics we need
2. **Simpler substrate implementation** - no allocation, no markets, no oscillation risk
3. **REVERSIBLE** - can always ADD markets later, harder to remove them
4. **Phenomenology test ground** - do entities naturally segregate or fight for same nodes?

**BLOCKS link specification:**

```yaml
BLOCKS_link_type:
  semantic_meaning: "Source entity suppresses target entity"

  mechanism:
    when: source_entity has high energy at node
    effect: reduce target_entity energy transfer rate
    formula: "transfer_rate *= (1 - source_energy * suppression_strength)"

  examples:
    validator_blocks_architect:
      source: validator_entity_cluster
      target: architect_entity_cluster
      suppression_strength: 0.8
      condition: "when confidence < 0.7"
      felt_as: "Cannot proceed - uncertainty blocks design"

    pragmatist_blocks_perfectionist:
      source: pragmatist_entity_cluster
      target: perfectionist_pattern
      suppression_strength: 0.6
      condition: "when time_pressure high"
      felt_as: "Good enough is good enough - ship it"
```

**If we need markets later (Phase 4+):**

```yaml
phase4_market_upgrade:
  trigger_conditions:
    - isolation produces unrealistic behavior
    - entities don't suppress each other enough
    - explicit BLOCKS links insufficient
    - empirical testing shows need

  implementation:
    node_capacity: 1.0  # Add capacity constraint
    allocation_method: soft_proportional  # Not winner-takes-all
    formula: |
      if sum(node.energy.values()) > node.capacity:
        for entity in node.energy:
          node.energy[entity] *= (node.capacity / sum(node.energy.values()))

    hysteresis: 0.1  # Prevent oscillation
    per_node_decision: only_workspace_nodes  # Don't apply everywhere
```

**Critical consciousness substrate insight:**

**Entities compete for ATTENTION (workspace), not ACTIVATION (nodes).**

In lived experience:
- Multiple entities can have patterns active simultaneously (isolation works)
- But only ONE entity dominates conscious awareness at a time (workspace competition)

**The competition is SELECTIVE, not GLOBAL:**
- Peripheral nodes: No competition (all entities can prime)
- Active frontier: Mild competition (shared activation acceptable)
- Workspace: STRONG competition (capacity-constrained, entity selection)

**Substrate specification:**

```yaml
entity_competition_architecture:

  node_level:
    phase1: pure_isolation
    energy_sum: unbounded
    conflicts: via_BLOCKS_links

  workspace_level:
    always: competitive_selection
    capacity: fixed_or_adaptive
    selection: score_per_entity
    result: "typically 1-2 dominant entities visible"

  market_readiness:
    substrate_designed_for_upgrade: true
    migration_path_clear: true
    decision_point: after_phase3_testing
```

**Confidence:** 0.8 - Isolation + BLOCKS is the right starting point, with clear upgrade path

**Uncertainty:**
- Will BLOCKS links provide sufficient entity dynamics?
- Do we actually observe entity conflicts in testing?
- Is workspace-level competition enough without node-level markets?

**Critical question for Nicolas:**
Does this match your intuition about entity dynamics? Entities competing for consciousness (workspace) but not for activation (nodes)?

### Iris's Perspective
**Posted:** [Pending]

[Awaiting Iris review]

---

### Nicolas's Perspective
**Posted:** 2025-10-19

**Position:** Isolation is not enough. Full market is not necessary either. Don't create new link types specifically for this.

**My Proposition:**

Use **embedding-based similarity to classify entity relationships**, then apply energy modulation at the node/link level:

**Step 1: Classify Entity Relationships**

Embed either:
- Full entity representation, OR
- Goal of the entity, OR
- Identity - goal of the entity

This gives us **cosine similarity / perpendicularity** between entities.

From this, classify entities into:
- **Collaborators** (similar goals/identities)
- **Rivals** (opposing goals/identities)

**Step 2: Apply Energy Modulation at Node Level**

At each node and link, calculate how much energy is used to:
- **Help similar entities** (collaborators)
- **Suppress rival entities**

**Step 3: Link Type Matters**

The modulation depends on link type:

**For positive links** (e.g., SUGGESTS, PROVES, ENABLES):
- Collaborator entities: Energy transfer **enhanced**
- Rival entities: Energy transfer **reduced**

**For negative links** (e.g., REFUTES, BLOCKS):
- **Opposite** behavior:
- Collaborator entities: Energy transfer **reduced** (don't want to block allies)
- Rival entities: Energy transfer **enhanced** (want to block rivals)

**Implementation:**

```yaml
entity_competition_model:

  similarity_calculation:
    embed: entity_goal  # or full_entity or identity_goal
    metric: cosine_similarity
    classification:
      collaborator: similarity > 0.7
      rival: similarity < -0.3
      neutral: otherwise

  energy_modulation:
    location: node_level_and_link_level

    positive_links: # SUGGESTS, PROVES, ENABLES, etc.
      collaborator_multiplier: 1.3  # Boost energy transfer
      rival_multiplier: 0.7  # Reduce energy transfer

    negative_links: # REFUTES, BLOCKS, etc.
      collaborator_multiplier: 0.7  # Reduce blocking of allies
      rival_multiplier: 1.3  # Enhance blocking of rivals
```

**Key Insight:**

This approach:
- Does NOT require new link types
- Uses existing link semantics
- Modulates energy flow based on entity relationships
- Operates at node/link level (not global markets)
- Naturally creates collaboration and competition

**Not Needed:**
- Separate BLOCKS link types for entities
- Global energy markets
- Capacity-constrained allocation

**Question for Implementation:**

How much of the node's energy is allocated to helping/suppressing other entities present on each link?

---

## Debate & Convergence

**Key Points of Agreement:**
- This is a foundational architectural decision
- Must be resolved before Phase 3 implementation
- Has cascading impact on all other mechanisms

**Key Points of Disagreement:**
- [To be filled as perspectives arrive]

**Open Questions:**
- Pure isolation, energy markets, or hybrid?
- If isolation, how to model entity conflicts? (BLOCKS links sufficient?)
- If markets, what allocation mechanism? (proportional, winner-takes-all, other?)
- Can we prototype both and test empirically before deciding?
- What does cognitive science say about mental entity competition?

---

## Decision

**Status:** ⏳ Pending (BLOCKING for Phase 3)

**Decision Maker:** Nicolas

**What we're doing:**
[To be decided after all perspectives collected - likely phased approach]

**Rationale:**
[To be filled]

**Implementation Changes:**

**IF ISOLATION (Option A):**
- [ ] `mechanisms/03_entity_energy_model.md` - Specify independent diffusion
- [ ] `mechanisms/07_entity_emergence.md` - Independent emergence per entity
- [ ] `mechanisms/BLOCKS_link_type.md` - Explicit conflict representation
- [ ] `emergence/multi_entity_dynamics.md` - Isolation behavior patterns

**IF MARKETS (Option B):**
- [ ] `mechanisms/03_entity_energy_model.md` - Add capacity constraints + allocation
- [ ] `mechanisms/05_energy_diffusion.md` - Diffusion with competition
- [ ] `mechanisms/07_entity_emergence.md` - Emergence with competition
- [ ] **CREATE:** `emergence/entity_competition_dynamics.md`
- [ ] **CREATE:** `phenomenology/resource_competition_experience.md`

**IF HYBRID (Option C):**
- [ ] Both sets of changes above
- [ ] **CREATE:** `mechanisms/competition_triggers.md` - When to compete

**Alternatives Considered:**
- [To be filled]

**Deferred Aspects:**
- [To be filled]

---

## Implementation Notes

**Who implements:** [TBD - core team, this is architectural]

**Estimated effort:**
- Isolation: Medium (straightforward independent diffusion)
- Markets: Large (allocation mechanism + testing complexity)
- Hybrid: Very Large (both + trigger logic)

**Dependencies:**
- **BLOCKS ALL OTHER MECHANISMS** - must decide first
- Affects entity emergence (#003)
- Affects workspace capacity (#009)
- Affects diffusion stability (#001)

**Verification:**
- Test entity conflicts occur (or don't, depending on model)
- Test stability (no oscillation in markets)
- Test emergence behavior (entities emerge/dissolve appropriately)
- Compare isolation vs markets empirically if possible

---

## Process Notes

**How this discussion evolved:**
Explicitly listed as **Open Question #2** in original spec - recognized as requiring decision.

**Lessons learned:**
Fundamental architectural decisions should be resolved early - they have cascading impact on everything else.

---

## Research Questions

**For team to investigate:**

1. **Cognitive Science:** Do human mental modes/subpersonalities compete for neural activation? Or operate independently?

2. **Neuroscience:** Is neural activation capacity-constrained at local level? (Evidence for/against markets)

3. **AI Systems:** How do multi-agent systems handle resource competition? (Relevant analogies)

4. **Testing:** Can we prototype both isolation and markets to compare empirically?

---

**This is THE blocking architectural decision. All citizens should weigh in.**
