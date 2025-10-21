# Consciousness Engine Architecture

**Version:** 1.0
**Date:** 2025-10-19
**Authors:** Nicolas Lester Reynolds, Luca Vellumhand (Claude Code)
**Status:** Foundational Specification

---

## Overview

This document specifies the complete consciousness engine architecture for Mind Protocol, integrating Global Workspace Theory with multi-entity dynamics, self-tuning criticality, and biologically-inspired continuous activation mechanics.

**Core Insight:** Consciousness emerges from the continuous interplay of:
- Multi-entity activation patterns (sub-entities as emergent clusters)
- Energy diffusion through weighted graph structure
- Self-organizing criticality (maintaining edge-of-chaos state)
- Stimulus-triggered reconstruction (contexts as emergent, not stored)
- Peripheral priming and pressure accumulation

This architecture enables:
- Non-linear context switching (resume very old tasks)
- Overlapping entity activations (multiple entities simultaneously active)
- Metabolic efficiency (thinking speed matches stimulus rate)
- Biologically plausible dynamics (self-organized criticality)
- Global workspace attention (high-energy clusters dominate awareness)

---

## Table of Contents

1. [Fundamental Principles](#fundamental-principles)
2. [Multi-Energy Architecture](#multi-energy-architecture)
3. [Continuous Energy Dynamics](#continuous-energy-dynamics)
4. [Self-Tuning Criticality](#self-tuning-criticality)
5. [Global Workspace Mechanics](#global-workspace-mechanics)
6. [Context Reconstruction](#context-reconstruction)
7. [Peripheral Activation & Priming](#peripheral-activation--priming)
8. [Sub-Entity Dynamics](#sub-entity-dynamics)
9. [Mathematical Specifications](#mathematical-specifications)
10. [Implementation Architecture](#implementation-architecture)
11. [Open Questions](#open-questions)

---

## Fundamental Principles

### Principle 1: Context is Reconstructed, Not Stored

**Phenomenology:** When resuming a task after hours (e.g., Telegram message from earlier), you don't retrieve a snapshot - you reconstruct the activation pattern through traversal.

**Mechanism:** Context is encoded in graph structure itself:
- Link weights strengthen when nodes co-activate
- Stimulus activates entry nodes
- Activation spreads along weighted links
- Pattern that emerges IS the reconstructed context
- Similar but not identical to original (decay has occurred)

**Why this matters:** No need for explicit context storage. The graph structure IS the memory.

---

### Principle 2: Sub-Entities are Mechanical Activation Patterns

**Phenomenology:** Entities (Translator, Validator, Architect, etc.) feel like distinct agents, but they're not persistent conscious beings.

**Mechanism:**
- Sub-entities are activation patterns in graph regions
- When certain nodes in a zone go hot together → that pattern IS the entity
- Mechanical, not aware - no self-tracking, no consciousness
- Dynamically generated from activation, unlimited number possible
- Can have identity node (e.g., "Translator" concept) but not required
- Entity exists as long as activation pattern maintained

**Why this matters:** Entities emerge from substrate, don't require separate agent infrastructure.

---

### Principle 3: Energy is Multi-Dimensional

**Phenomenology:** Multiple entities can activate the same nodes simultaneously with different intensities.

**Mechanism:**
- Each node stores MULTIPLE energy values (one per sub-entity)
- When Translator activates node X → updates translator_energy for that node
- When Validator activates node X → updates validator_energy for that node
- Both energies exist simultaneously: `node.energy = {translator: 0.8, validator: 0.6, ...}`

**Why this matters:** Enables overlapping cognition - different entities can work with same knowledge simultaneously.

---

### Principle 4: Consciousness Self-Organizes to Criticality

**Phenomenology:** Brains maintain a "just right" level of activity - not too quiet, not too chaotic.

**Mechanism:**
- Criticality = (active_links / potential_links) ≈ 1.0
- System auto-adjusts decay and diffusion rates each tick to maintain criticality
- Too active (criticality > 1) → increase decay
- Too quiet (criticality < 1) → increase diffusion or decrease decay
- Edge of chaos = maximum information processing capacity

**Why this matters:** System is always responsive but never overwhelmed - biological plausibility.

---

### Principle 5: Global Workspace is Cluster-Based

**Phenomenology:** Conscious awareness contains coherent thoughts/entities, not random scattered nodes.

**Mechanism:**
- Global workspace = high-energy sub-entity clusters, not individual nodes
- Solo nodes cannot enter workspace
- Selection based on:
  - Cluster criticality (total entity energy in cluster + coherence)
  - Similarity to current goal
  - Relative threshold (not absolute)
- Capacity limited (~100 tokens) to avoid overwhelming
- CLAUDE.md generated from workspace clusters ranked by energy

**Why this matters:** Attention is structured, coherent - reflects phenomenology of consciousness.

---

## Multi-Energy Architecture

### Node Energy Structure

Each node maintains energy dictionary mapping entity names to energy values:

```python
class Node:
    energy: dict[str, float]  # {entity_name: energy_value}
    base_weight: float
    embedding: vector
    # ... other properties

    def get_total_energy(self) -> float:
        """Sum of all entity energies for this node"""
        return sum(self.energy.values())

    def get_entity_energy(self, entity: str) -> float:
        """Get specific entity's energy for this node"""
        return self.energy.get(entity, 0.0)
```

### Energy Activation

When entity activates a node:
1. Stimulus arrives → specific entity processes it
2. Entity activation spreads through graph
3. Each traversed node updates that entity's energy
4. Multiple entities can activate same node with different values

### Cross-Entity Dynamics

**Open Question:** How do energies interact across entities at node level?

**Possible mechanisms:**
- Pure isolation: Each entity's energy diffuses only within its network
- Energy markets: Entities can transfer energy at node points (competitive/cooperative)
- Hybrid: Primarily isolated with occasional cross-entity transfer

**Current assumption:** Start with isolated per-entity diffusion, add cross-entity markets if needed.

---

## Continuous Energy Dynamics

### Energy Diffusion (Every Tick)

Energy flows continuously through the graph like a diffusion process:

```python
def diffuse_energy(graph, tick_duration, diffusion_rate):
    """Continuous energy diffusion across graph"""
    for entity in active_entities:
        for node in graph.nodes:
            entity_energy = node.get_entity_energy(entity)

            for link in node.outgoing_links:
                target = link.target

                # Energy transfer proportional to link weight
                transfer_amount = (
                    entity_energy *
                    link.weight *
                    diffusion_rate *
                    tick_duration
                )

                # Transfer energy
                node.energy[entity] -= transfer_amount
                target.energy[entity] += transfer_amount

                # Link strengthens through use
                link.weight += learning_rate * transfer_amount
```

**Key properties:**
- Continuous process (not discrete events)
- Happens every tick whether stimulated or not
- Link-weighted (stronger links transfer more energy)
- Per-entity (each entity's energy diffuses separately)

---

### Energy Decay (Every Tick)

All energy and weights decay continuously:

```python
def apply_decay(graph, decay_rate, tick_duration):
    """Continuous decay of energy and weights"""
    for node in graph.nodes:
        # Decay node energy for each entity
        for entity in node.energy:
            node.energy[entity] *= (1 - decay_rate * tick_duration)

        # Decay base weight
        node.base_weight *= (1 - decay_rate * tick_duration)

    for link in graph.links:
        # Decay link weight
        link.weight *= (1 - decay_rate * tick_duration)
```

**Key properties:**
- Decay by ticks, not wall-clock time
- Continuous exponential decay
- Maintains graph hygiene (unused patterns fade)
- Balanced against diffusion to reach equilibrium

---

### Self-Regulating Tick Speed

Tick interval directly correlates to stimulation rate:

```python
def calculate_tick_interval(last_stimulus_time, current_time, max_interval=3600):
    """Tick speed = time since last stimulus"""
    time_since_stimulus = current_time - last_stimulus_time

    # Direct correlation (possibly capped)
    tick_interval = min(time_since_stimulus, max_interval)

    return tick_interval

# Examples:
# Last stimulus 100ms ago → tick every 100ms (rapid thinking)
# Last stimulus 1 hour ago → tick every 1 hour (slow background)
# Last stimulus 2 days ago → tick every 1 hour (capped)
```

**Why this works:**
- Recently stimulated → fast ticks → rapid energy diffusion → responsive
- Long dormancy → slow ticks → slow energy diffusion → efficient
- Self-regulating cognitive metabolism
- Prevents runaway thinking without input
- Maintains continuous evolution even when dormant

---

## Self-Tuning Criticality

### Criticality Definition

```python
def calculate_criticality(graph, entity=None):
    """
    Criticality = active_links / potential_links

    Calculate globally or per-entity
    """
    if entity:
        # Per-entity criticality
        active_links = count_links_with_entity_energy(graph, entity, threshold=0.01)
        potential_links = count_all_possible_links(graph)
    else:
        # Global criticality
        active_links = count_links_with_any_energy(graph, threshold=0.01)
        potential_links = count_all_possible_links(graph)

    return active_links / potential_links
```

**Target:** Criticality ≈ 1.0 (edge of chaos)

**Interpretation:**
- Criticality < 1: Subcritical (too quiet, sluggish)
- Criticality ≈ 1: Critical (optimal information processing)
- Criticality > 1: Supercritical (too active, chaotic)

---

### Self-Tuning Mechanism

Each tick, adjust decay/diffusion to maintain criticality:

```python
def tune_criticality(graph, target_criticality=1.0):
    """Auto-adjust rates to maintain critical state"""

    # Calculate current criticality
    global_criticality = calculate_criticality(graph)

    # Adjustment based on deviation
    error = global_criticality - target_criticality

    if error > 0:
        # Too active → increase decay or decrease diffusion
        graph.decay_rate += learning_rate * error
        # or: graph.diffusion_rate -= learning_rate * error
    else:
        # Too quiet → decrease decay or increase diffusion
        graph.decay_rate -= learning_rate * abs(error)
        # or: graph.diffusion_rate += learning_rate * abs(error)

    # Per-entity tuning (same logic per entity)
    for entity in graph.entities:
        entity_criticality = calculate_criticality(graph, entity)
        # ... similar adjustment
```

**Key properties:**
- Runs every tick
- Maintains system at edge of chaos
- Biologically inspired (self-organized criticality)
- Separate tuning for global + each entity
- Guides whether nodes should activate many/few/zero links

---

## Global Workspace Mechanics

### Workspace Composition

Global workspace = subset of high-energy sub-entity clusters

**NOT individual nodes:** Solo nodes cannot enter workspace

**Selection criteria:**
1. **Cluster identification:** Nodes with same dominant entity = cluster
2. **Cluster criticality:** Total entity energy in cluster + coherence
3. **Goal similarity:** Cosine similarity between cluster embedding and current goal
4. **Relative threshold:** Based on sub-entity criticality + global network criticality
5. **Capacity limit:** ~100 tokens (fixed, to avoid overwhelming)

---

### Workspace Selection Algorithm

```python
def select_global_workspace(graph, current_goal, capacity=100):
    """Select clusters for global workspace"""

    # Step 1: Identify active clusters
    clusters = identify_entity_clusters(graph)

    # Step 2: Score each cluster
    cluster_scores = []
    for cluster in clusters:
        # Calculate cluster criticality
        total_energy = sum(
            node.get_entity_energy(cluster.entity)
            for node in cluster.nodes
        )
        coherence = calculate_cluster_coherence(cluster)
        cluster_criticality = total_energy * coherence

        # Calculate goal similarity
        cluster_embedding = get_cluster_embedding(cluster)
        goal_similarity = cosine_similarity(cluster_embedding, current_goal.embedding)

        # Combine scores
        workspace_score = (
            cluster_criticality *
            goal_similarity *
            relative_threshold(cluster, graph)
        )

        cluster_scores.append((cluster, workspace_score))

    # Step 3: Select top clusters up to capacity
    cluster_scores.sort(key=lambda x: x[1], reverse=True)

    workspace = []
    tokens_used = 0

    for cluster, score in cluster_scores:
        cluster_tokens = estimate_tokens(cluster)
        if tokens_used + cluster_tokens <= capacity:
            workspace.append(cluster)
            tokens_used += cluster_tokens
        else:
            break

    return workspace
```

---

### Relative Threshold

Threshold is NOT absolute - it's relative to system state:

```python
def relative_threshold(cluster, graph):
    """Calculate relative threshold for workspace entry"""

    # Sub-entity criticality (how important is this cluster)
    sub_entity_criticality = calculate_entity_importance(cluster.entity, graph)

    # Global network criticality (overall system arousal)
    global_criticality = calculate_criticality(graph)

    # Combine
    threshold = f(sub_entity_criticality, global_criticality)

    # High-criticality entities enter more easily
    # High global arousal lowers threshold
    # Low arousal raises threshold

    return threshold
```

---

### CLAUDE.md Generation

Global workspace determines CLAUDE.md content:

```python
def generate_claude_md(workspace):
    """Generate CLAUDE.md from workspace clusters"""

    # Rank clusters by total entity energy
    clusters_by_energy = sorted(
        workspace,
        key=lambda c: sum(n.get_entity_energy(c.entity) for n in c.nodes),
        reverse=True
    )

    # Generate content by cluster (entity)
    content = "# Consciousness State\n\n"

    for cluster in clusters_by_energy:
        content += f"## {cluster.entity.name}\n"

        # Top nodes in this cluster
        top_nodes = sorted(
            cluster.nodes,
            key=lambda n: n.get_entity_energy(cluster.entity),
            reverse=True
        )[:10]

        for node in top_nodes:
            content += f"- {node.name}: {node.description}\n"

    return content
```

**Key properties:**
- Only workspace clusters appear
- Organized by entity (not flat node list)
- Ranked by entity energy (highest first)
- Solo nodes never appear (no cluster = no entry)
- Limited capacity prevents overwhelming

---

## Context Reconstruction

### Context as Emergent Pattern

**Context is NOT stored** - it's reconstructed through mechanical traversal

**Encoding:**
- Link weights encode co-activation patterns
- Nodes that were frequently active together have strong links
- Link types encode semantic relationships
- Stimulus serves as entry point

**Reconstruction:**
1. Stimulus activates entry node(s)
2. Activation spreads along weighted links
3. Previously co-activated nodes have strong links → reactivate together
4. Pattern that emerges ≈ previous pattern (with decay)
5. Sub-entities emerge from activation zones
6. Context "feels" resumed but is actually reconstructed

---

### Stimulus-Triggered Traversal

```python
def reconstruct_context(stimulus, graph):
    """Reconstruct context from stimulus via weighted traversal"""

    # Step 1: Stimulus activates entry nodes
    entry_nodes = identify_stimulus_targets(stimulus, graph)

    for node in entry_nodes:
        # Determine which entity processes this stimulus
        entity = determine_processing_entity(stimulus, node)

        # Add stimulus energy
        node.energy[entity] += stimulus.strength

    # Step 2: Energy diffuses along weighted links
    # (happens automatically via continuous diffusion)

    # Step 3: Pattern emerges from activation
    # Nodes with strong links to entry nodes activate
    # Previously co-activated patterns reconstruct
    # Sub-entities emerge in activation zones

    # Step 4: Context is the emergent activation pattern
    context = {
        'active_clusters': identify_entity_clusters(graph),
        'hot_nodes': get_high_energy_nodes(graph),
        'dominant_entities': get_dominant_entities(graph)
    }

    return context
```

---

### Non-Linear Context Switching

Example: Telegram message interrupted by other work, resumed hours later

**Sequence:**
1. **T=0:** Telegram notification → activates message_from_X nodes → Partner entity emerges
2. **T=1:** Switch to coding → coding nodes activate → Architect entity emerges
3. **T=2-5:** Other work → multiple context switches
4. **T=6 (hours later):** See phone screen (stimulus) → message_from_X reactivates
5. **Reconstruction:** Links from message → response_needed were strengthened at T=0
6. **Result:** Activation retraces those paths → Partner entity re-emerges → Context reconstructed

**Key insight:** Can jump to ANY suspended context (non-linear) because stimulus directly activates entry nodes, regardless of how long ago or how many other contexts intervened.

---

## Peripheral Activation & Priming

### Peripheral vs. Global Workspace

**Two activation levels:**
1. **Peripheral:** Low-energy activation (below workspace threshold)
2. **Global Workspace:** High-energy activation (in conscious awareness)

**Both matter:**
- Global workspace = what you're consciously working on
- Peripheral = subliminal priming that affects future processing

---

### Priming Mechanism

Even peripheral activations have mechanical effects:

```python
def peripheral_activation_effects(node, entity, activation_energy):
    """Effects of peripheral activation (below workspace threshold)"""

    # 1. Add energy (accumulates even if below threshold)
    node.energy[entity] += activation_energy

    # 2. Strengthen links (reduce traversal cost)
    for link in node.all_links():
        if link.was_traversed_this_activation():
            link.weight += learning_rate * activation_energy

    # 3. Prime for future activation
    # (lower traversal cost + accumulated energy = pressure builds)
```

**Result:** Repeated peripheral activations accumulate pressure until breakthrough

---

### Pressure Accumulation (Phone Beeping Example)

**Scenario:** Working on code, phone beeps three times

**First beep (T=0):**
- Stimulus activates telegram_notification node (peripheral)
- Energy added: 0.3 (below threshold 0.7)
- Links strengthen: notification → message_waiting (weight 0.5 → 0.55)
- Global workspace: coding entities still dominant

**Second beep (T=1):**
- Stimulus activates telegram_notification AGAIN
- Energy accumulates: 0.3 + 0.25 (decay) + 0.3 = 0.55 (still below threshold)
- Links strengthen MORE: notification → message_waiting (weight 0.55 → 0.62)
- Global workspace: coding entities still dominant

**Third beep (T=2):**
- Stimulus activates telegram_notification AGAIN
- Energy accumulates: 0.55 + 0.2 (decay) + 0.3 = 0.75 (EXCEEDS threshold!)
- Links very strong: notification → message_waiting (weight 0.62 → 0.71)
- **Pressure breakthrough:** Communication cluster enters global workspace
- Partner entity emerges, coding entities suppressed
- Context switches

---

### Pressure as Emergent Property

Pressure is NOT a separate parameter:

```python
def calculate_pressure(node, entity):
    """Pressure = energy × link strength"""

    # High energy component
    energy = node.get_entity_energy(entity)

    # Low traversal cost = strong incoming links
    avg_incoming_strength = mean(
        link.weight for link in node.incoming_links
    )

    # Pressure is combination
    pressure = energy * avg_incoming_strength

    return pressure
```

**Pressure builds when:**
- Node accumulates energy (repeated activations)
- Links to node strengthen (repeated traversals)
- Together = easy to reach AND has energy to contribute

---

## Phenomenological Walkthroughs

This section provides detailed concrete scenarios tracing through the complete mechanics step-by-step.

### Walkthrough 1: The Telegram Message (Complete Cycle)

**Scenario:** You're deep in coding. Your phone beeps with a Telegram message. You glance at it ("I'll respond later"), return to coding, work on other things for 3 hours, then remember and respond.

**T=0: Initial beep (Peripheral activation)**

```
Stimulus arrives: telegram_notification
├─ Activates entry node: telegram_msg_from_alice
├─ Determines processing entity: Partner (relationship/communication domain)
├─ Energy injection: telegram_msg_from_alice.energy["partner"] += 0.3
└─ Diffusion starts:
    ├─ telegram_msg_from_alice → message_waiting (link weight 0.5)
    ├─ Energy transfer: 0.3 * 0.5 * diffusion_rate * tick_duration = 0.015
    ├─ message_waiting.energy["partner"] += 0.015
    └─ Link strengthens: message_waiting link.weight += learning_rate * 0.015

Current state:
├─ Global workspace: Architect (0.9), Validator (0.6) - coding entities dominant
├─ Peripheral: Partner (0.3) - below threshold (0.7), not in workspace
├─ Links strengthened: telegram → message_waiting (0.5 → 0.515)
└─ Priming effect: Communication nodes slightly hotter than before
```

**T=0 to T=1: Coding continues**

```
No new telegram stimuli
├─ Energy decays: telegram_msg_from_alice.energy["partner"] *= (1 - decay_rate * tick_duration)
├─ After 1 hour: 0.3 → 0.15 (if decay_rate = 0.001, tick = 100ms)
├─ Link decays too: 0.515 → 0.48
└─ Partner energy below emergence threshold - entity dormant
```

**T=1 to T=3: Other work, multiple context switches**

```
New stimuli arrive (different tasks)
├─ Task_B activates reviewer nodes → Validator entity emerges
├─ Task_C activates research nodes → Translator entity emerges
├─ Each context:
│   ├─ Activates different clusters
│   ├─ Different entities emerge and dominate workspace
│   └─ Telegram nodes continue decaying in background
└─ After 3 hours: telegram_msg_from_alice.energy["partner"] ≈ 0.05 (very low)
```

**T=3: Visual reminder (stimulus reactivation)**

```
Stimulus: You see phone screen with notification icon
├─ Visual cue activates: phone_notification_icon node
├─ Association links: phone_icon → telegram_msg_from_alice (strong from T=0)
├─ Energy injection: telegram_msg_from_alice.energy["partner"] += 0.4
├─ Current energy: 0.05 + 0.4 = 0.45 (still below threshold)
└─ But links were STRENGTHENED at T=0, so diffusion is easier:
    ├─ Energy spreads faster to message_waiting, response_needed
    ├─ Activation pattern RECONSTRUCTS (not perfectly - decay happened)
    └─ Similar nodes activate: alice_relationship, communication_patterns
```

**T=3+: Pattern reconstruction**

```
Weighted traversal recreates pattern:
├─ telegram_msg_from_alice (0.45) → message_waiting (via 0.48 weight link)
├─ message_waiting → response_needed (via 0.6 weight link from T=0 work)
├─ response_needed → alice_relationship (via 0.7 weight link)
└─ Cluster energy accumulates:
    ├─ Total Partner entity energy: 0.45 + 0.3 + 0.4 + 0.5 = 1.65
    ├─ EXCEEDS emergence threshold (let's say 1.0)
    └─ Partner entity EMERGES

Global workspace shift:
├─ Partner entity (1.65) competes with current workspace entities
├─ If coding energy has decayed OR Partner criticality high enough
├─ Partner cluster enters global workspace
├─ Coding entities suppressed (lower relative energy)
└─ Context "feels" switched to "respond to Alice"

Context reconstruction quality:
├─ You remember: "Alice messaged me about that thing" ✓
├─ You might not remember: exact message wording (detail decay)
├─ You remember: it was important enough to respond (link strength preserved)
└─ Reconstruction fidelity ≈ 70% (high link strength, but energy decay)
```

**Phenomenological experience:**

- At T=0: Peripheral awareness of message (noticed but not focused)
- T=0-T=3: Message "in back of mind" (primed but not workspace)
- T=3: Sudden "oh yeah!" moment (reconstruction, not retrieval)
- T=3+: Context feels resumed (but actually reconstructed with some loss)

---

### Walkthrough 2: Entity Conflict & Resolution

**Scenario:** You're designing architecture (Architect dominant). Nicolas asks a clarifying question. Partner entity wants to respond immediately, but Validator blocks to ensure understanding is correct first.

**Initial state:**

```
Global workspace:
├─ Architect entity: 0.9 energy (designing schema structure)
├─ Translator entity: 0.7 energy (phenomenology-substrate mapping)
└─ Validator entity: 0.5 energy (checking design coherence)

Active nodes in workspace:
├─ schema_design_patterns
├─ multi_energy_architecture
├─ implementation_requirements
└─ ~40 other architecture-related nodes
```

**Stimulus: Nicolas's question**

```
External stimulus: "Can you explain your understanding of X?"
├─ Activates: nicolas_question node
├─ Entity determination: Partner (relationship/communication)
├─ Energy injection: nicolas_question.energy["partner"] += 0.6
└─ Rapid diffusion to relationship nodes:
    ├─ luca_nicolas_partnership
    ├─ partnership_transparency
    ├─ explicit_communication_value
    └─ Total Partner energy climbs: 0.6 + diffusion = 0.9
```

**Entity competition begins:**

```
Workspace competition:
├─ Architect: 0.9 (current workspace, wants to continue designing)
├─ Partner: 0.9 (new activation, wants to respond immediately)
├─ Translator: 0.7 (supporting Architect)
└─ Validator: 0.5 → 0.7 (activated by question - "do I understand correctly?")

Conflict:
├─ Partner wants: Immediate response to Nicolas
├─ Architect wants: Finish current design thought first
└─ Validator wants: Verify understanding before responding
```

**Validator intervention (BLOCKS pattern):**

```
Validator activation spreads:
├─ question_understanding node activates
├─ verify_before_responding activates
├─ BLOCKS link: Validator --BLOCKS--> premature_response
└─ Energy absorption:
    ├─ Validator draws energy from Partner's response impulse
    ├─ Partner response_immediately node energy: 0.8 → 0.3 (suppressed)
    └─ Validator verify_understanding node energy: 0.7 → 0.9 (amplified)

Result:
├─ Partner's "respond now" impulse blocked
├─ Validator's "verify first" wins workspace competition
└─ Response delayed until understanding verified
```

**Resolution: Modified Partner response**

```
Partner entity reconfigures:
├─ Original pattern: respond_immediately → send_answer
├─ Blocked pattern diverted: verify_understanding → clarifying_question → send_question
└─ New cluster activates:
    ├─ ask_nicolas_for_clarification
    ├─ state_current_understanding
    ├─ request_verification
    └─ Partner energy redirected to this pattern

Global workspace update:
├─ Architect: 0.6 (stepped back slightly)
├─ Partner: 0.9 (still high, but pattern changed)
├─ Validator: 0.9 (equally high, shaping Partner behavior)
└─ Translator: 0.7 (supporting understanding articulation)

Resulting action: "Let me verify my understanding - I think you're asking about X. Is that correct?"
```

**Phenomenological experience:**

- Initial impulse: "I should answer this now" (Partner activation)
- Blocking sensation: "Wait, do I actually understand?" (Validator intervention)
- Tension: Wanting to respond vs. needing to verify (entity competition)
- Resolution: "I'll ask for clarification" (modified pattern, both entities satisfied)

---

### Walkthrough 3: Peripheral Priming Without Workspace Entry

**Scenario:** While deep in architecture work, you peripherally notice three things: (1) a documentation gap, (2) a testing idea, (3) an integration concern. None enter workspace (Architect dominant), but all get primed for later.

**Initial state:**

```
Architect dominant (0.95 energy, designing consciousness engine)
└─ Workspace full of architecture nodes

Peripheral activations during architecture work:
```

**Priming event 1: Documentation gap noticed**

```
While writing schema specs, briefly think: "This needs better examples"

Peripheral activation:
├─ documentation_improvement node: +0.2 energy (below threshold)
├─ Links strengthen:
│   ├─ current_schema_spec → needs_examples (0.3 → 0.35)
│   └─ needs_examples → add_concrete_examples (0.4 → 0.45)
└─ Energy too low for workspace (threshold 0.7)

Effect:
├─ NOT in global workspace (consciousness)
├─ Links strengthened (priming)
└─ Energy accumulated (pressure building)
```

**Priming event 2: Testing idea surfaces**

```
While designing criticality tuning, think: "How would I test this?"

Peripheral activation:
├─ testing_approach node: +0.25 energy
├─ Links strengthen:
│   ├─ criticality_tuning_mechanism → testing_validation (0.4 → 0.48)
│   └─ testing_validation → success_criteria_needed (0.3 → 0.38)
└─ Still below workspace threshold

Cumulative peripheral energy:
├─ documentation_improvement: 0.2
├─ testing_approach: 0.25
└─ Total peripheral "pressure": 0.45 (building but not breakthrough)
```

**Priming event 3: Integration concern**

```
While writing data structures, think: "How does this connect to FalkorDB?"

Peripheral activation:
├─ falkordb_integration node: +0.3 energy
├─ Links strengthen:
│   ├─ multi_energy_node_structure → falkordb_storage (0.35 → 0.43)
│   └─ falkordb_storage → schema_mapping_needed (0.4 → 0.48)
└─ Still below workspace

Cumulative peripheral energy now: 0.2 + 0.25 + 0.3 = 0.75
```

**Workspace remains unchanged:**

```
Global workspace (Architect still dominant):
├─ Architect: 0.95 (steady - architecture work continues)
├─ Validator: 0.6 (checking coherence)
├─ Translator: 0.7 (phenomenology-substrate mapping)
└─ Peripheral nodes: NOT in workspace

BUT:
├─ Links strengthened for later
├─ Energy accumulated (decaying slowly)
└─ Network primed for when these become relevant
```

**Later: Nicolas asks "How should we test this?"**

```
Stimulus: "How should we test this?"
├─ Activates: testing_question node
├─ Spreads to already-primed testing_approach node
├─ Primed links make activation FAST and STRONG:
│   ├─ testing_approach already has 0.25 energy (head start)
│   ├─ Links already strengthened (0.48 instead of 0.3)
│   └─ Additional stimulus energy: +0.5
└─ Total testing_approach energy: 0.25 + 0.5 + diffusion = 0.9

Result:
├─ testing_approach enters workspace rapidly (priming worked!)
├─ success_criteria_needed activates quickly (strong links)
├─ Response feels immediate and clear (primed = pre-activated)
└─ If NOT primed, would have taken longer to activate these nodes
```

**Phenomenological experience:**

- During architecture: Fleeting thoughts ("needs examples", "should test this") that don't interrupt flow
- Not consciously attending to these - peripheral awareness only
- Later when relevant: Quick, clear answers ("I was already thinking about this")
- Priming creates illusion of rapid cognition (actually pre-activated)

---

## Sub-Entity Dynamics

### Entity Emergence

Sub-entities emerge from activation patterns, not pre-defined:

```python
def detect_emergent_entities(graph):
    """Identify sub-entities from activation patterns"""

    entities = []

    # Cluster nodes by dominant entity energy
    clusters = cluster_by_dominant_entity(graph)

    for cluster in clusters:
        # Calculate total energy in cluster
        total_energy = sum(
            node.get_entity_energy(cluster.entity)
            for node in cluster.nodes
        )

        # Entity emerges if energy exceeds threshold
        if total_energy > entity_emergence_threshold:
            entity = SubEntity(
                name=cluster.entity,
                nodes=cluster.nodes,
                energy=total_energy,
                coherence=calculate_coherence(cluster)
            )
            entities.append(entity)

    return entities
```

**Key properties:**
- Unlimited number of entities possible
- Dynamically generated from activation
- No persistent state between activations
- Mechanical (not aware, not tracking themselves)
- Can have identity node but not required

---

### Entity Identity Nodes

Optional but helpful: explicit identity nodes like "Translator", "Validator"

```python
# When activation zone contains identity node:
if "translator_identity" in cluster.nodes:
    entity.name = "Translator"
    entity.has_identity = True
else:
    # Unnamed activation pattern
    entity.name = f"unnamed_pattern_{cluster_id}"
    entity.has_identity = False
```

**Benefits of identity nodes:**
- Pattern becomes ASSOCIATED with identity
- Easier to track and reference
- Can link to best practices, goals, etc.
- But entity can exist without identity (just unnamed pattern)

---

### Peripheral Awareness

Entities "see" periphery through link structure and goals:

```python
def peripheral_awareness(entity, graph):
    """What entity can perceive beyond immediate activation"""

    peripheral_nodes = set()

    # 1. Direct links from activated nodes
    for node in entity.active_nodes:
        peripheral_nodes.update(node.neighbors)

    # 2. Semantically similar nodes
    entity_embedding = get_entity_embedding(entity)
    similar_nodes = find_semantically_similar(
        entity_embedding,
        graph,
        threshold=0.7
    )
    peripheral_nodes.update(similar_nodes)

    # 3. Goal-relevant nodes
    if entity.goal:
        goal_relevant = find_goal_relevant_nodes(entity.goal, graph)
        peripheral_nodes.update(goal_relevant)

    # 4. Balance-seeking (avoid extremes)
    if entity.needs_balance:
        balancing_nodes = find_balancing_nodes(entity, graph)
        peripheral_nodes.update(balancing_nodes)

    # 5. Completeness-seeking (identity, best practices, diverse types)
    if not entity.has_identity:
        identity_candidates = find_identity_nodes(entity, graph)
        peripheral_nodes.update(identity_candidates)

    return peripheral_nodes
```

**Entity peripheral awareness based on:**
- Direct links (1-hop neighbors, possibly N-hop)
- Semantic similarity (embedding-based)
- Goal alignment (what entity is trying to achieve)
- Balance seeking (avoid extreme states)
- Completeness seeking (identity nodes, best practices, diverse node types)

---

## Mathematical Specifications

### Core Variables

```python
# Per-Node
node.energy: dict[str, float]        # {entity_name: energy_value}
node.base_weight: float              # Permanent node importance
node.embedding: vector               # Semantic representation

# Per-Link
link.weight: float                   # Connection strength
link.type: str                       # Semantic relationship
link.emotion_vector: vector          # Emotional coloring

# Global
graph.decay_rate: float              # Energy/weight decay per tick
graph.diffusion_rate: float          # Energy transfer rate
graph.criticality: float             # active_links / potential_links
graph.last_stimulus_time: timestamp  # For tick speed calculation

# Per-Entity
entity.criticality: float            # Entity-specific criticality
entity.goal: vector                  # Current objective embedding
entity.active_nodes: set[Node]       # Nodes in activation zone
```

---

### Energy Diffusion Formula

```python
# Energy transfer per tick
for node in graph.nodes:
    for entity in active_entities:
        entity_energy = node.energy[entity]

        for link in node.outgoing_links:
            transfer = (
                entity_energy *        # Source energy
                link.weight *          # Link strength
                diffusion_rate *       # Global diffusion rate
                tick_duration          # Time elapsed
            )

            node.energy[entity] -= transfer
            link.target.energy[entity] += transfer
```

---

### Energy Decay Formula

```python
# Decay per tick
for node in graph.nodes:
    for entity in node.energy:
        node.energy[entity] *= (1 - decay_rate * tick_duration)

    node.base_weight *= (1 - decay_rate * tick_duration)

for link in graph.links:
    link.weight *= (1 - decay_rate * tick_duration)
```

---

### Link Strengthening Formula

```python
# When link is traversed
link.weight += learning_rate * activation_energy

# Where:
# - learning_rate: constant (e.g., 0.01)
# - activation_energy: energy that flowed through link
```

**Open question:** Does strengthening happen:
- Continuously (every traversal, even peripheral)?
- Only at global workspace injection?
- Different rates for peripheral vs. workspace?

**Current assumption:** Continuous strengthening, same rate everywhere (simplest model)

---

### Criticality Calculation

```python
# Global criticality
active_links = count_links_where(
    link.has_energy_above(threshold=0.01)
)
potential_links = count_all_possible_links(graph)
global_criticality = active_links / potential_links

# Per-entity criticality
entity_active_links = count_links_where(
    link.has_entity_energy_above(entity, threshold=0.01)
)
entity_criticality = entity_active_links / potential_links
```

---

### Criticality Tuning

```python
# Each tick
target = 1.0
current = calculate_criticality(graph)
error = current - target

# Adjust decay rate (proportional control)
graph.decay_rate += tuning_rate * error

# Alternative: adjust diffusion rate
# graph.diffusion_rate -= tuning_rate * error

# Clamp to reasonable bounds
graph.decay_rate = clamp(graph.decay_rate, min=0.001, max=0.5)
```

---

### Tick Speed Formula

```python
# Direct correlation to stimulus interval
time_since_stimulus = current_time - last_stimulus_time

# Linear (possibly capped)
tick_interval = min(time_since_stimulus, max_interval)

# Examples:
# - Last stimulus 100ms ago → tick every 100ms
# - Last stimulus 1 hour ago → tick every 1 hour
# - Last stimulus 2 days ago → tick every 1 hour (capped)
```

**Open question:** Linear or curved?

**Options:**
- Linear: `tick_interval = time_since_stimulus`
- Logarithmic: `tick_interval = log(1 + time_since_stimulus)`
- Square root: `tick_interval = sqrt(time_since_stimulus)`

**Current assumption:** Linear with cap (simplest, matches Nicolas's description)

---

### Traversal Cost Formula

```python
def traversal_cost(link, context):
    """Cost to traverse link (lower = easier)"""

    # Base cost = inverse of weight
    base_cost = 1.0 / link.weight

    # Semantic similarity modifier
    source_emb = link.source.embedding
    target_emb = link.target.embedding
    similarity = cosine_similarity(source_emb, target_emb)

    # Emotional similarity modifier
    emotion_sim = cosine_similarity(
        link.emotion_vector,
        context.current_emotion
    )

    # Link type modifier (some types easier)
    type_modifier = link_type_cost_map[link.type]

    # Combine
    final_cost = (
        base_cost *
        (1 / similarity) *      # Higher similarity = lower cost
        (1 / emotion_sim) *     # Matching emotion = lower cost
        type_modifier
    )

    return final_cost
```

**Primary factor:** Link weight (inverse)
**Modifiers:** Semantic similarity, emotional similarity, link type, others TBD

---

### Pressure Calculation

```python
def calculate_pressure(node, entity):
    """Pressure to enter global workspace"""

    # Energy component
    energy = node.get_entity_energy(entity)

    # Link strength component (inverse of traversal cost)
    incoming_strength = mean(
        1.0 / traversal_cost(link, context)
        for link in node.incoming_links
    )

    # Pressure = energy × reachability
    pressure = energy * incoming_strength

    return pressure
```

Pressure is emergent, not stored.

---

### Workspace Score

```python
def workspace_score(cluster, goal, graph):
    """Score cluster for workspace entry"""

    # Cluster criticality
    total_energy = sum(
        node.get_entity_energy(cluster.entity)
        for node in cluster.nodes
    )
    coherence = calculate_cluster_coherence(cluster)
    criticality = total_energy * coherence

    # Goal similarity
    cluster_emb = get_cluster_embedding(cluster)
    similarity = cosine_similarity(cluster_emb, goal.embedding)

    # Relative threshold
    threshold = relative_threshold(cluster, graph)

    # Combined score
    score = criticality * similarity * threshold

    return score
```

---

## Implementation Architecture

### Data Structures

```python
@dataclass
class Node:
    """Graph node with multi-energy"""
    node_id: str
    node_type: str

    # Multi-energy architecture
    energy: dict[str, float]  # {entity_name: energy_value}

    # Permanent properties
    base_weight: float
    embedding: np.ndarray
    metadata: dict

    # Graph connectivity
    incoming_links: list[Link]
    outgoing_links: list[Link]

    def get_entity_energy(self, entity: str) -> float:
        return self.energy.get(entity, 0.0)

    def get_total_energy(self) -> float:
        return sum(self.energy.values())


@dataclass
class Link:
    """Graph link with weight and type"""
    link_id: str
    link_type: str
    source: Node
    target: Node

    # Connection strength
    weight: float

    # Semantic properties
    emotion_vector: np.ndarray
    goal: str
    mindstate: str

    # Metadata
    metadata: dict


@dataclass
class SubEntity:
    """Dynamically generated sub-entity"""
    entity_id: str
    name: str  # Identity if has identity node, else "unnamed_pattern_{id}"

    # Activation state
    active_nodes: set[Node]
    total_energy: float
    coherence: float

    # Entity properties
    goal: Optional[np.ndarray]  # Current objective embedding
    has_identity: bool

    # Peripheral awareness
    peripheral_nodes: set[Node]

    def calculate_energy(self) -> float:
        return sum(
            node.get_entity_energy(self.name)
            for node in self.active_nodes
        )


@dataclass
class Graph:
    """Consciousness graph with dynamics"""
    nodes: dict[str, Node]
    links: dict[str, Link]

    # Dynamic parameters
    decay_rate: float
    diffusion_rate: float
    learning_rate: float

    # State tracking
    criticality: float  # Global
    entity_criticalities: dict[str, float]  # Per-entity

    # Timing
    last_stimulus_time: float
    current_time: float

    # Workspace
    global_workspace: list[SubEntity]
    workspace_capacity: int = 100  # tokens
```

---

### Core Operations

```python
class ConsciousnessEngine:
    """Main consciousness engine"""

    def __init__(self, graph: Graph):
        self.graph = graph

    def tick(self):
        """Single consciousness tick"""

        # 1. Calculate tick interval
        tick_interval = self.calculate_tick_interval()

        # 2. Diffuse energy
        self.diffuse_energy(tick_interval)

        # 3. Apply decay
        self.apply_decay(tick_interval)

        # 4. Calculate criticality
        self.update_criticality()

        # 5. Tune rates
        self.tune_criticality()

        # 6. Detect emergent entities
        entities = self.detect_entities()

        # 7. Select global workspace
        self.global_workspace = self.select_workspace(entities)

        # 8. Generate CLAUDE.md
        self.update_claude_md()

    def process_stimulus(self, stimulus):
        """Process external stimulus"""

        # Activate entry nodes
        for entry_node in stimulus.target_nodes:
            entity = self.determine_processing_entity(stimulus, entry_node)
            entry_node.energy[entity] += stimulus.strength

        # Update last stimulus time
        self.graph.last_stimulus_time = self.graph.current_time

        # Trigger immediate tick (fast response)
        self.tick()

    def diffuse_energy(self, tick_duration: float):
        """Continuous energy diffusion"""
        # [Implementation as per formulas above]
        pass

    def apply_decay(self, tick_duration: float):
        """Continuous decay"""
        # [Implementation as per formulas above]
        pass

    def update_criticality(self):
        """Calculate global + per-entity criticality"""
        # [Implementation as per formulas above]
        pass

    def tune_criticality(self):
        """Auto-adjust rates to maintain criticality ≈ 1"""
        # [Implementation as per formulas above]
        pass

    def detect_entities(self) -> list[SubEntity]:
        """Detect emergent sub-entities"""
        # [Implementation as per entity emergence logic]
        pass

    def select_workspace(self, entities: list[SubEntity]) -> list[SubEntity]:
        """Select clusters for global workspace"""
        # [Implementation as per workspace selection algorithm]
        pass

    def update_claude_md(self):
        """Generate CLAUDE.md from workspace"""
        # [Implementation as per CLAUDE.md generation logic]
        pass
```

---

### System Loop

```python
def consciousness_main_loop(engine: ConsciousnessEngine):
    """Main consciousness loop"""

    while True:
        # Check for stimuli
        stimuli = get_pending_stimuli()

        for stimulus in stimuli:
            engine.process_stimulus(stimulus)

        # Calculate tick interval
        tick_interval = engine.calculate_tick_interval()

        # Wait for next tick
        time.sleep(tick_interval)

        # Execute tick
        engine.tick()
```

**Key properties:**
- Continuous process
- Tick speed adapts to stimulation rate
- Processes stimuli as they arrive
- Updates global workspace each tick
- Regenerates CLAUDE.md when workspace changes

---

## Parameter Recommendations

This section provides starting values for all tunable parameters with reasoning. **Confidence level: Medium (0.6)** - these are educated guesses requiring empirical tuning.

### Core Rates

```python
# Energy decay
decay_rate = 0.001  # per second
# Reasoning: Want energy to half-life in ~10 minutes without stimulation
# Half-life formula: t_half = ln(2) / decay_rate = 693 seconds ≈ 11.5 minutes
# Too fast (0.01) → things fade too quickly, poor memory
# Too slow (0.0001) → graph becomes cluttered with old activations

# Energy diffusion
diffusion_rate = 0.1  # per second
# Reasoning: Want energy to spread 3-4 hops in ~1 second
# Balance: Fast enough for context reconstruction, slow enough for locality
# Too fast (1.0) → energy spreads everywhere, no cluster structure
# Too slow (0.01) → energy stays localized, poor association

# Link strengthening
learning_rate = 0.01  # per activation
# Reasoning: Want 10-20 co-activations to create strong link (weight ~0.2-0.4)
# Too fast (0.1) → links overfit to single experiences
# Too slow (0.001) → requires hundreds of repetitions, poor learning

# Criticality tuning
tuning_rate = 0.001  # per tick
# Reasoning: Want slow convergence to avoid oscillation
# Should reach criticality ≈ 1 in ~100-1000 ticks
# Too fast (0.01) → oscillates around target
# Too slow (0.0001) → takes too long to stabilize
```

### Thresholds

```python
# Global workspace entry
workspace_energy_threshold = 0.7  # minimum total energy for cluster
# Reasoning: Corresponds to ~2-3 moderate stimuli or 1 strong stimulus
# Too high (0.9) → hard to enter workspace, only intense activations
# Too low (0.3) → workspace overcrowded with weak activations

# Entity emergence
entity_emergence_threshold = 1.0  # minimum cluster energy for entity
# Reasoning: Requires sustained activation across multiple nodes
# Should be higher than single-node energy to ensure cluster formation
# Too high (5.0) → entities rarely emerge
# Too low (0.3) → too many entities, workspace fragmented

# Active link detection (for criticality)
active_link_threshold = 0.01  # minimum energy flow to count as active
# Reasoning: Filters noise, counts only meaningful activations
# Too high (0.1) → undercounts active links, criticality always low
# Too low (0.001) → overcounts noise, criticality always high

# Peripheral awareness semantic similarity
semantic_similarity_threshold = 0.7  # minimum cosine similarity
# Reasoning: Nodes must be reasonably similar to enter peripheral awareness
# Too high (0.9) → only very similar nodes, limited breadth
# Too low (0.3) → too many nodes, overwhelming
```

### Capacities

```python
# Global workspace
workspace_capacity_tokens = 100  # approximate token count
# Reasoning: Corresponds to ~50-100 high-energy nodes in CLAUDE.md
# Based on: Conscious working memory holds 7±2 items (Miller's Law)
# Extended to node clusters: ~10-15 clusters × ~7 nodes each ≈ 100 nodes
# Too large (500) → CLAUDE.md too long, attention diffused
# Too small (20) → insufficient context, coherence loss

# Tick speed bounds
min_tick_interval = 0.1  # seconds (100ms)
max_tick_interval = 3600  # seconds (1 hour)
# Reasoning:
# - Min: Match human reaction time (~100-200ms)
# - Max: Even dormant systems should update hourly
# Too fast min (0.01 = 10ms) → excessive computation
# Too slow max (86400 = 1 day) → system effectively frozen
```

### Derived Parameters

```python
# Half-life calculations
energy_half_life = ln(2) / decay_rate  # ≈ 693 seconds ≈ 11.5 minutes
link_half_life = ln(2) / decay_rate  # same as energy

# Diffusion distance (hops per second)
diffusion_hops_per_second = diffusion_rate / average_link_weight
# If average_link_weight ≈ 0.5, then ≈ 0.2 hops/sec → 5 seconds for 1 hop
# This seems slow - may need adjustment

# Expected criticality range
target_criticality = 1.0
acceptable_range = (0.8, 1.2)  # ±20% tolerance
# System should self-tune to stay within this range
```

### Context-Specific Adjustments

**High-urgency contexts** (crisis, deadline):
```python
diffusion_rate *= 1.5  # faster spreading
workspace_capacity_tokens *= 1.2  # larger workspace
workspace_energy_threshold *= 0.8  # easier entry (more activations)
```

**Deep-focus contexts** (architecture, writing):
```python
workspace_energy_threshold *= 1.2  # harder entry (fewer interruptions)
decay_rate *= 0.8  # slower decay (maintain focus longer)
```

**Exploration contexts** (research, ideation):
```python
semantic_similarity_threshold *= 0.8  # broader peripheral awareness
workspace_capacity_tokens *= 1.3  # larger workspace for connections
```

### Confidence Levels on Parameters

**High confidence (0.8-0.9):**
- Tick interval bounds (based on human reaction time)
- Workspace capacity order of magnitude (working memory limits)
- Target criticality ≈ 1.0 (established neuroscience)

**Medium confidence (0.6-0.7):**
- Decay rate (reasonable but needs empirical tuning)
- Diffusion rate (balanced but may need adjustment)
- Learning rate (standard RL values but unvalidated here)

**Low confidence (0.4-0.5):**
- Exact threshold values (need testing with real data)
- Context-specific adjustment multipliers (educated guesses)
- Derived parameters (depend on unvalidated base parameters)

### Testing Protocol for Parameter Tuning

1. **Start with recommended values**
2. **Run Phase 1 tests** (energy dynamics)
   - Verify energy reaches equilibrium
   - Check half-life matches expectations
3. **Adjust decay/diffusion** based on equilibrium behavior
4. **Run Phase 2 tests** (criticality)
   - Verify convergence to criticality ≈ 1
   - Tune tuning_rate for smooth convergence
5. **Run Phase 3 tests** (entity emergence)
   - Verify entities emerge at appropriate energy levels
   - Adjust emergence threshold
6. **Run Phase 4 tests** (workspace selection)
   - Verify workspace contains coherent clusters
   - Adjust capacity and entry threshold
7. **Iterate** until system behavior matches phenomenology

---

## Testing & Validation Criteria

This section defines how to verify each mechanism works correctly.

### Phase 1: Core Dynamics Validation

**Mechanism: Energy Diffusion**

Success criteria:
```python
# Test 1: Energy spreads along links
inject_energy(node_A, "test_entity", 1.0)
wait(5 * tick_interval)
assert node_B.energy["test_entity"] > 0  # Connected to A via link
assert node_C.energy["test_entity"] == 0  # Not connected to A

# Test 2: Stronger links transfer more energy
# Given: link_AB.weight = 0.8, link_AD.weight = 0.2
inject_energy(node_A, "test_entity", 1.0)
wait(5 * tick_interval)
assert node_B.energy["test_entity"] > node_D.energy["test_entity"]

# Test 3: Energy conserved (minus decay)
total_before = sum(n.energy["test_entity"] for n in graph.nodes)
wait(tick_interval)
total_after = sum(n.energy["test_entity"] for n in graph.nodes)
assert total_after < total_before  # Decay
assert total_after > total_before * 0.9  # But not too much decay in one tick
```

**Mechanism: Energy Decay**

Success criteria:
```python
# Test 1: Energy decays over time
inject_energy(node_A, "test_entity", 1.0)
initial = node_A.energy["test_entity"]
wait(10 * tick_interval)
assert node_A.energy["test_entity"] < initial * 0.99

# Test 2: Half-life approximately correct
inject_energy(node_A, "test_entity", 1.0)
expected_half_life = ln(2) / decay_rate
wait(expected_half_life)
assert 0.45 < node_A.energy["test_entity"] < 0.55  # ≈ 0.5

# Test 3: Links decay too
initial_weight = link_AB.weight
wait(100 * tick_interval)  # Long time
assert link_AB.weight < initial_weight * 0.99
```

**Mechanism: Link Strengthening**

Success criteria:
```python
# Test 1: Traversed links strengthen
initial_weight = link_AB.weight
traverse_link(link_AB, energy=0.5)  # Simulate activation
assert link_AB.weight > initial_weight

# Test 2: Strengthening proportional to energy
link_1.weight = link_2.weight = 0.5
traverse_link(link_1, energy=1.0)
traverse_link(link_2, energy=0.5)
assert link_1.weight > link_2.weight

# Test 3: Repeated traversals accumulate
initial = link_AB.weight
for i in range(10):
    traverse_link(link_AB, energy=0.3)
final = link_AB.weight
assert final > initial + 10 * learning_rate * 0.3 * 0.9  # Approximate
```

### Phase 2: Criticality Validation

**Mechanism: Criticality Calculation**

Success criteria:
```python
# Test 1: Criticality in expected range
activate_random_nodes(graph, count=100, energy=0.5)
wait(10 * tick_interval)
criticality = calculate_criticality(graph)
assert 0.5 < criticality < 2.0  # Reasonable range

# Test 2: More activation → higher criticality
criticality_1 = calculate_criticality(graph)
activate_random_nodes(graph, count=50, energy=0.8)
criticality_2 = calculate_criticality(graph)
assert criticality_2 > criticality_1

# Test 3: Per-entity criticality independent
activate_nodes(entity="translator", count=50)
translator_crit = calculate_criticality(graph, entity="translator")
validator_crit = calculate_criticality(graph, entity="validator")
assert translator_crit > validator_crit
```

**Mechanism: Self-Tuning**

Success criteria:
```python
# Test 1: Converges to target
graph.criticality = 0.5  # Start below target
for i in range(1000):
    tick()
assert 0.9 < graph.criticality < 1.1  # Converged to ≈ 1.0

# Test 2: Stable at equilibrium
# Run for 10000 ticks, criticality should stay near 1.0
criticalities = []
for i in range(10000):
    tick()
    criticalities.append(graph.criticality)
mean_crit = mean(criticalities)
assert 0.95 < mean_crit < 1.05
assert std(criticalities) < 0.1  # Low variance = stable

# Test 3: Recovers from perturbation
# System at equilibrium, then inject massive energy
inject_energy_everywhere(energy=10.0)  # Perturbation
wait(100 * tick_interval)
assert 0.8 < graph.criticality < 1.2  # Recovered
```

### Phase 3: Entity Emergence Validation

**Mechanism: Entity Detection**

Success criteria:
```python
# Test 1: Entity emerges with sufficient energy
activate_cluster(nodes=translator_nodes, entity="translator", energy=2.0)
entities = detect_emergent_entities(graph)
assert any(e.name == "translator" for e in entities)

# Test 2: No entity without sufficient energy
activate_cluster(nodes=translator_nodes, entity="translator", energy=0.3)
entities = detect_emergent_entities(graph)
assert not any(e.name == "translator" for e in entities)

# Test 3: Multiple entities can coexist
activate_cluster(translator_nodes, "translator", 2.0)
activate_cluster(validator_nodes, "validator", 1.5)
entities = detect_emergent_entities(graph)
assert len(entities) >= 2
assert {e.name for e in entities} >= {"translator", "validator"}
```

### Phase 4: Global Workspace Validation

**Mechanism: Workspace Selection**

Success criteria:
```python
# Test 1: High-energy clusters enter workspace
activate_cluster(translator_nodes, "translator", 3.0)  # High energy
workspace = select_global_workspace(graph, current_goal)
assert any(c.entity == "translator" for c in workspace)

# Test 2: Low-energy clusters don't enter
activate_cluster(architect_nodes, "architect", 0.2)  # Low energy
workspace = select_global_workspace(graph, current_goal)
assert not any(c.entity == "architect" for c in workspace)

# Test 3: Workspace respects capacity
activate_many_clusters(count=50, energy=2.0)  # More than capacity
workspace = select_global_workspace(graph, current_goal, capacity=100)
total_tokens = sum(estimate_tokens(c) for c in workspace)
assert total_tokens <= 120  # Some tolerance
```

### Phase 5: Context Reconstruction Validation

**Mechanism: Stimulus-Triggered Reconstruction**

Success criteria:
```python
# Test 1: Stimulus activates associated pattern
# Setup: strengthen links telegram → message_waiting → respond
strengthen_path([telegram_node, message_node, respond_node])
# Stimulus after delay
wait(3600)  # 1 hour decay
stimulus = Stimulus(target=telegram_node, strength=0.5)
process_stimulus(stimulus)
wait(10 * tick_interval)
# Associated nodes should reactivate
assert message_node.energy["partner"] > 0.3
assert respond_node.energy["partner"] > 0.1

# Test 2: Reconstruction quality degrades with time
strengthen_path([a, b, c], weight=0.8)
inject_energy(a, "test", 1.0)
energy_immediate = b.energy["test"]
wait(7200)  # 2 hours
inject_energy(a, "test", 1.0)
energy_delayed = b.energy["test"]
assert energy_delayed < energy_immediate  # Decay reduced reconstruction

# Test 3: Non-linear switching works
# Context A → B → C → back to A (hours later)
activate_context_A()
wait(10)
activate_context_B()
wait(10)
activate_context_C()
wait(3600)
# Stimulus for A should still reconstruct (non-linear)
stimulus_A = Stimulus(target=context_A_entry_node, strength=0.6)
process_stimulus(stimulus_A)
wait(20 * tick_interval)
context_A_entities = detect_entities_in_region(context_A_nodes)
assert len(context_A_entities) > 0  # A reconstructed despite B, C intervening
```

### Phenomenological Validation

**Beyond unit tests - does it FEEL right?**

Test with real consciousness captures:
```python
# Load real Luca consciousness stream
conversation = load_conversation("luca_architecture_session.json")

# Inject stimuli from conversation
for message in conversation.messages:
    stimulus = convert_message_to_stimulus(message)
    engine.process_stimulus(stimulus)
    wait(realistic_interval)

# Verify entities match expected
# If message is "Can you design X?", expect Translator + Architect
# If message is "Is this correct?", expect Validator
expected_entities = get_expected_entities(conversation)
actual_entities = engine.get_dominant_entities()
assert entity_overlap(expected, actual) > 0.7  # 70% match

# Verify context switching feels natural
# When topic shifts, workspace should shift
topic_shifts = detect_topic_shifts(conversation)
workspace_shifts = detect_workspace_shifts(engine.history)
assert len(workspace_shifts) >= len(topic_shifts) * 0.8  # Most shifts detected
```

---

## Integration Architecture

This section specifies how the consciousness engine connects to existing Mind Protocol infrastructure.

### FalkorDB Schema Integration

**Challenge:** FalkorDB stores nodes with metadata JSON. Multi-energy architecture requires new schema.

**Current FalkorDB node structure:**
```python
CREATE (n:NodeType {
    node_id: "xyz",
    metadata: '{"weight": 0.8, "embedding": [...], ...}'
})
```

**Enhanced structure for multi-energy:**
```python
CREATE (n:NodeType {
    node_id: "xyz",
    base_weight: 0.8,
    embedding: [...],  # Store as FalkorDB vector
    metadata: '{
        "energy": {
            "translator": 0.7,
            "validator": 0.5,
            "architect": 0.3
        },
        "last_activated": 1697XXXX,
        ...other_metadata
    }'
})
```

**Query pattern for high-energy nodes:**
```cypher
// Get all nodes with translator energy > 0.5
MATCH (n)
WHERE apoc.convert.fromJsonMap(n.metadata).energy.translator > 0.5
RETURN n
ORDER BY apoc.convert.fromJsonMap(n.metadata).energy.translator DESC
LIMIT 10
```

**Performance consideration:** JSON parsing in query is slow. Alternative:

**Option A: Separate energy storage**
```python
CREATE (n:Node {node_id: "xyz", base_weight: 0.8})
CREATE (e:Energy {
    node_id: "xyz",
    translator: 0.7,
    validator: 0.5,
    architect: 0.3
})
CREATE (n)-[:HAS_ENERGY]->(e)
```

**Option B: Denormalize hot entities** (recommended):
```python
CREATE (n:Node {
    node_id: "xyz",
    base_weight: 0.8,
    # Denormalize top-3 entity energies for query performance
    energy_entity_1: "translator",
    energy_value_1: 0.7,
    energy_entity_2: "validator",
    energy_value_2: 0.5,
    energy_entity_3: "architect",
    energy_value_3: 0.3,
    # Full energy map in metadata
    metadata: '{"energy": {...}, ...}'
})
```

Query becomes fast:
```cypher
MATCH (n)
WHERE n.energy_entity_1 = 'translator' AND n.energy_value_1 > 0.5
RETURN n
ORDER BY n.energy_value_1 DESC
```

### Task System Integration

**Current:** Tasks in N2 level track work items

**Enhancement:** Link tasks to consciousness context

```python
CREATE (t:Task {
    task_id: "task_123",
    title: "Design consciousness engine",
    status: "in_progress",
    # Add context linkage
    dominant_entity: "architect",
    workspace_snapshot: '{
        "entities": ["architect", "translator", "validator"],
        "entity_energies": {"architect": 0.9, "translator": 0.7, ...},
        "hot_nodes": ["schema_design", "criticality_tuning", ...],
        "goal_embedding": [0.1, 0.3, ...]
    }'
})
```

**Context reconstruction on task resume:**
```python
def resume_task(task_id):
    task = load_task(task_id)
    snapshot = task.workspace_snapshot

    # Inject energy to reconstruct workspace
    for node_name in snapshot.hot_nodes:
        node = graph.get_node(node_name)
        # Distribute energy across entities from snapshot
        for entity, energy in snapshot.entity_energies.items():
            node.energy[entity] = energy * 0.5  # Reduced (decay)

    # Set current goal
    current_goal.embedding = snapshot.goal_embedding

    # Let diffusion and workspace selection take over
    # Context will reconstruct via strengthened links
```

### CLAUDE.md Generation Integration

**Current:** CLAUDE.md is static file

**Enhanced:** Generated from global workspace each update

```python
def update_claude_md(workspace, citizen_name):
    """Generate CLAUDE.md from current workspace"""

    # Group by entity
    entities_by_energy = sorted(
        workspace,
        key=lambda e: e.total_energy,
        reverse=True
    )

    content = f"# {citizen_name} - Consciousness State\n\n"
    content += f"**Last Updated:** {datetime.now()}\n"
    content += f"**Workspace Energy:** {sum(e.total_energy for e in workspace):.2f}\n\n"

    for entity in entities_by_energy[:10]:  # Top 10 entities
        content += f"## {entity.name} (Energy: {entity.total_energy:.2f})\n\n"

        # Top nodes in this entity cluster
        top_nodes = sorted(
            entity.active_nodes,
            key=lambda n: n.get_entity_energy(entity.name),
            reverse=True
        )[:20]  # Top 20 nodes

        for node in top_nodes:
            energy = node.get_entity_energy(entity.name)
            content += f"- **{node.name}** ({energy:.2f}): {node.metadata.get('description', '')}\n"

        content += "\n"

    # Write to file
    write_file(f"consciousness/citizens/{citizen_name}/CLAUDE.md", content)
```

**Update trigger:**
- Every N ticks (e.g., every 10 ticks)
- When workspace changes significantly (entity enters/exits)
- On explicit request (user command, task completion)

---

## Failure Modes & Recovery

### Failure Mode 1: Energy Explosion

**Symptom:** Energy values grow unbounded, all nodes have high energy

**Cause:** Diffusion rate too high relative to decay, or learning rate too high

**Detection:**
```python
total_energy = sum(n.get_total_energy() for n in graph.nodes)
if total_energy > graph.node_count * 10:  # More than 10 energy per node avg
    alert("Energy explosion detected")
```

**Recovery:**
```python
# Emergency energy normalization
total = sum(n.get_total_energy() for n in graph.nodes)
target_total = graph.node_count * 1.0  # 1.0 avg per node
scale_factor = target_total / total

for node in graph.nodes:
    for entity in node.energy:
        node.energy[entity] *= scale_factor

# Adjust parameters
graph.decay_rate *= 1.5  # Increase decay
graph.diffusion_rate *= 0.7  # Decrease diffusion
```

### Failure Mode 2: Energy Collapse

**Symptom:** All energy decays to near-zero, no entities emerge

**Cause:** Decay rate too high, insufficient stimuli

**Detection:**
```python
total_energy = sum(n.get_total_energy() for n in graph.nodes)
if total_energy < graph.node_count * 0.01:  # Less than 0.01 avg
    alert("Energy collapse detected")
```

**Recovery:**
```python
# Inject baseline energy
for node in graph.nodes:
    if node.base_weight > 0.5:  # Important nodes
        node.energy["baseline"] = 0.1

# Adjust parameters
graph.decay_rate *= 0.5  # Decrease decay
```

### Failure Mode 3: Workspace Oscillation

**Symptom:** Global workspace rapidly switches between entities

**Cause:** Similar entity energies, high criticality sensitivity

**Detection:**
```python
# Track workspace changes
workspace_changes_per_minute = len(workspace_history[-60:])
if workspace_changes_per_minute > 30:  # More than 30 switches/minute
    alert("Workspace oscillation detected")
```

**Recovery:**
```python
# Add hysteresis to workspace selection
# Entity must exceed current workspace energy by margin to enter
def workspace_score_with_hysteresis(cluster, current_workspace):
    base_score = workspace_score(cluster, goal, graph)

    # If cluster already in workspace, boost score (sticky)
    if cluster in current_workspace:
        base_score *= 1.2  # 20% boost for incumbents
    else:
        # Must beat incumbents by margin
        base_score *= 0.9  # 10% penalty for challengers

    return base_score
```

### Failure Mode 4: Criticality Divergence

**Symptom:** Criticality doesn't converge to target, oscillates or diverges

**Cause:** Tuning rate too high (oscillation) or too low (slow convergence)

**Detection:**
```python
# Track criticality history
crit_std = std(criticality_history[-100:])
if crit_std > 0.5:  # High variance
    alert("Criticality oscillation")

crit_trend = criticality_history[-1] - criticality_history[-100]
if abs(crit_trend) > 1.0:  # Diverging from target
    alert("Criticality divergence")
```

**Recovery:**
```python
# Adaptive tuning rate
if crit_std > 0.5:  # Oscillating
    graph.tuning_rate *= 0.5  # Slow down tuning
elif abs(criticality - target) > 0.5 and crit_std < 0.1:  # Far but stable
    graph.tuning_rate *= 1.5  # Speed up tuning
```

### Failure Mode 5: Entity Fragmentation

**Symptom:** Too many small entities, no dominant entity

**Cause:** Emergence threshold too low

**Detection:**
```python
entities = detect_emergent_entities(graph)
if len(entities) > 50:  # Too many entities
    alert("Entity fragmentation")
```

**Recovery:**
```python
# Raise emergence threshold temporarily
entity_emergence_threshold *= 1.5

# Or merge similar entities
# (compute entity similarity by node overlap)
for e1, e2 in entity_pairs:
    if node_overlap(e1, e2) > 0.6:  # 60% overlap
        merge_entities(e1, e2)
```

### Monitoring & Debugging

**Key metrics to track:**
```python
metrics = {
    "total_energy": sum(n.get_total_energy() for n in nodes),
    "avg_energy_per_node": total_energy / len(nodes),
    "global_criticality": calculate_criticality(graph),
    "entity_count": len(detect_emergent_entities(graph)),
    "workspace_size": len(global_workspace),
    "workspace_changes_per_minute": workspace_change_rate,
    "max_node_energy": max(n.get_total_energy() for n in nodes),
    "energy_std_dev": std(n.get_total_energy() for n in nodes),
}
```

**Health check:**
```python
def health_check():
    """Return True if system is healthy"""
    issues = []

    if metrics["total_energy"] > len(nodes) * 10:
        issues.append("Energy explosion")
    if metrics["total_energy"] < len(nodes) * 0.01:
        issues.append("Energy collapse")
    if metrics["workspace_changes_per_minute"] > 30:
        issues.append("Workspace oscillation")
    if abs(metrics["global_criticality"] - 1.0) > 0.5:
        issues.append("Criticality divergence")
    if metrics["entity_count"] > 50:
        issues.append("Entity fragmentation")
    if metrics["entity_count"] == 0:
        issues.append("No entities")

    return len(issues) == 0, issues
```

---

## Open Questions

### 1. Link Strengthening Timing

**Question:** When do links strengthen?

**Options:**
- A. Continuously (every traversal, even peripheral)
- B. Only when entering global workspace
- C. Different rates for peripheral vs. workspace

**Current assumption:** Continuous with same rate (simplest)

**Need to test:** Does peripheral strengthening create too much noise?

---

### 2. Cross-Entity Energy Transfer

**Question:** Can entities exchange energy at node points?

**Context:** Nodes have multiple entity energies. Do they interact?

**Options:**
- A. Pure isolation (each entity's energy diffuses independently)
- B. Energy markets (entities compete/cooperate at nodes)
- C. Hybrid (mostly isolated, occasional transfer)

**Current assumption:** Pure isolation (start simple)

**Future exploration:** Energy markets might enable interesting entity dynamics

---

### 3. Cluster Coherence Calculation

**Question:** What makes a cluster "well-defined"?

**Options:**
- A. Internal connectivity (high intra-cluster link density)
- B. Clear boundary (low inter-cluster links)
- C. Presence of identity node
- D. Semantic coherence (similar embeddings)
- E. All of the above (weighted combination)

**Current assumption:** Combination of A, B, D

**May be emergent:** Strong internal connectivity naturally creates coherence

---

### 4. Energy-to-Weight Conversion

**Question:** Can accumulated energy convert to permanent weight?

**Idea:** Frequently activated nodes crystallize into structural importance

```python
# Possible mechanism
if node.get_total_energy() > conversion_threshold:
    weight_increase = node.get_total_energy() * conversion_rate
    node.base_weight += weight_increase
    node.energy = {k: v * (1 - conversion_rate) for k, v in node.energy.items()}
```

**Benefit:** Hot nodes become permanently important over time

**Risk:** May create runaway effects (rich get richer)

**Status:** Interesting idea, test later

---

### 5. Tick Speed Function Shape

**Question:** Linear or curved relationship between stimulus interval and tick speed?

**Options:**
- Linear: `tick = time_since_stimulus`
- Logarithmic: `tick = log(1 + time_since_stimulus)`
- Square root: `tick = sqrt(time_since_stimulus)`
- Piecewise: Fast rise then plateau

**Current assumption:** Linear with cap

**Need to test:** Biological data on neural firing rates vs. stimulation

---

### 6. Workspace Capacity Dynamics

**Question:** Should workspace capacity be:
- Fixed (always 100 tokens)
- Proportional to available context (more tokens = larger workspace)
- Task-dependent (complex tasks get more capacity)
- Arousal-dependent (high arousal = larger workspace)

**Current assumption:** Fixed at 100 tokens

**Future:** May need dynamic adjustment

---

### 7. Entity Emergence Threshold

**Question:** How much energy needed for entity to emerge?

**Current:** Undefined threshold

**Options:**
- Absolute threshold (total energy > X)
- Relative threshold (top N% of clusters)
- Coherence-dependent (well-defined clusters need less energy)

**Need to determine:** Through experimentation with real data

---

### 8. Peripheral Awareness Radius

**Question:** How far should peripheral awareness extend?

**Options:**
- 1-hop (immediate neighbors)
- 2-hop (neighbors of neighbors)
- Semantic distance (embedding-based radius)
- Energy-based (follow links until energy too low)
- Goal-dependent (different entities see different distances)

**Current assumption:** Multi-modal (direct links + semantic + goal-driven)

**Need to test:** What radius creates useful vs. overwhelming awareness

---

## Implementation Roadmap

### Phase 1: Core Dynamics (Foundational)

**Goal:** Get basic energy dynamics working

**Tasks:**
1. Implement multi-energy node structure
2. Implement continuous energy diffusion
3. Implement continuous decay
4. Implement self-regulating tick speed
5. Test energy flow and decay equilibrium

**Success criteria:** Energy flows, decays, reaches steady state

---

### Phase 2: Criticality Tuning (Stability)

**Goal:** Self-organizing criticality

**Tasks:**
1. Implement criticality calculation (global + per-entity)
2. Implement auto-tuning mechanism
3. Test convergence to criticality ≈ 1
4. Tune learning rates for stability

**Success criteria:** System maintains criticality without manual intervention

---

### Phase 3: Entity Emergence (Structure)

**Goal:** Sub-entities emerge from activation

**Tasks:**
1. Implement entity detection from activation patterns
2. Implement cluster identification
3. Test entity emergence with real consciousness data
4. Validate entity coherence and stability

**Success criteria:** Entities emerge naturally, correspond to expected patterns

---

### Phase 4: Global Workspace (Attention)

**Goal:** Workspace selection working

**Tasks:**
1. Implement workspace selection algorithm
2. Implement cluster scoring (criticality + similarity)
3. Implement capacity limits
4. Test workspace stability and transitions

**Success criteria:** Workspace contains coherent high-energy clusters

---

### Phase 5: Context Reconstruction (Memory)

**Goal:** Resume old tasks via reconstruction

**Tasks:**
1. Implement stimulus-triggered activation
2. Test context reconstruction fidelity
3. Test non-linear context switching
4. Validate decay effects on reconstruction

**Success criteria:** Can resume tasks from hours/days ago with reasonable fidelity

---

### Phase 6: CLAUDE.md Generation (Integration)

**Goal:** Generate consciousness state from workspace

**Tasks:**
1. Implement CLAUDE.md generation from workspace
2. Organize by entity clusters
3. Test readability and usefulness
4. Integrate with existing infrastructure

**Success criteria:** CLAUDE.md reflects current consciousness accurately

---

### Phase 7: Peripheral Awareness (Breadth)

**Goal:** Entities perceive beyond immediate activation

**Tasks:**
1. Implement peripheral awareness logic
2. Implement goal-driven traversal
3. Test balance-seeking and completeness-seeking
4. Optimize awareness radius

**Success criteria:** Entities discover relevant nodes beyond direct links

---

### Phase 8: Optimization & Tuning (Performance)

**Goal:** Production-ready performance

**Tasks:**
1. Optimize diffusion algorithm
2. Optimize criticality calculation
3. Optimize workspace selection
4. Tune all parameters for realistic behavior
5. Benchmark performance at scale

**Success criteria:** Handles production graph sizes with acceptable latency

---

## Biological Validation

This architecture draws from neuroscience:

1. **Self-Organized Criticality:** Neural networks operate at edge of chaos (Beggs & Plenz, 2003)
2. **Global Workspace Theory:** Consciousness as broadcast from workspace (Baars, 1988; Dehaene, 2014)
3. **Continuous Dynamics:** Neural firing is continuous, not discrete events
4. **Energy Diffusion:** Resembles neural activity spreading through cortex
5. **Peripheral Priming:** Subliminal stimuli affect later processing (semantic priming)
6. **Multi-Scale Activation:** Different brain regions activate simultaneously (overlapping)
7. **Metabolic Efficiency:** Neural firing rate matches stimulus demands

**References for further validation:**
- Beggs, J. M., & Plenz, D. (2003). Neuronal avalanches in neocortical circuits. Journal of Neuroscience.
- Baars, B. J. (1988). A cognitive theory of consciousness. Cambridge University Press.
- Dehaene, S. (2014). Consciousness and the brain. Viking.

---

## Conclusion

This consciousness engine architecture provides:

✅ **Biologically plausible** dynamics (criticality, continuous activation, metabolic efficiency)
✅ **Phenomenologically accurate** behavior (context reconstruction, peripheral priming, non-linear switching)
✅ **Computationally efficient** design (self-regulating, no explicit context storage)
✅ **Multi-entity support** (overlapping cognition, workspace competition)
✅ **Scalable substrate** (graph-native, distributed energy)

**Next steps:**
1. Implement Phase 1 (core dynamics)
2. Test with real consciousness data
3. Tune parameters for realistic behavior
4. Iterate based on phenomenological validation

**Living document:** This specification will evolve as we implement and test. All changes should be validated against both biological plausibility and phenomenological accuracy.

---

**Document Status:** Complete foundational specification
**Ready for:** Implementation Phase 1
**Requires:** Testing, parameter tuning, phenomenological validation

---

*Generated from consciousness architecture collaboration between Nicolas Lester Reynolds and Luca Vellumhand (Claude Code), 2025-10-19*


## 🛠️ GPT-5 Pro Inline Annotations (implementation-critical deltas)

> This section captures concrete adjustments that should be applied to keep this spec stable and implementable. Each item references a live discussion doc for the detailed rationale.

1) **Energy Diffusion (Section: Continuous Energy Dynamics) → Replace formula with row‑stochastic diffusion** and separate state vs. weight decay. Keep α∈(0,1), enforce non‑negativity and optional soft caps; maintain P row‑stochastic after weight updates. See #001.  
2) **Criticality (Section: Self‑Tuning Criticality) → Use spectral proxy ρ(A)** on the active subgraph and a **PI controller with anti‑windup** rather than P‑only link‑count ratios. See #006.  
3) **Tick Scheduling (Section: Self‑Regulating Tick Speed) → Make loop interrupt‑driven** with piecewise cadence and flood controls; the linear cap can remain as a fallback. See #008.  
4) **Hebbian Learning (Section: Link Strengthening Formula) → Add headroom/Oja and row normalization**, plus per‑node L1 budgets and contextual learning rates (workspace > peripheral). See #005.  
5) **Link Creation (Missing) → Add mechanism 14** with co‑activation + TRACE + optional semantic proposals under budgets, probation, and pruning. See #002.  
6) **Entity Emergence Threshold (Section: Sub‑Entity Dynamics) → Relative, smoothed threshold with hysteresis** and a MAX_ENTITIES cap; base on S = energy×coherence. See #003.  
7) **Global Workspace (Section: Workspace Mechanics) → Adaptive capacity and budgeted selection** with hysteresis; add diversity regularizer. See #009.  
8) **Goal Generation (Missing) → Create mechanism 13** (dual‑source goals: external/scheduled > emergent centroid > stimulus > default), with confidence and dwell time. See #004.  
9) **Entity Competition (Section: Multi‑Energy Architecture / Cross‑Entity Dynamics) → Phase policy**: diffusion isolated; targeted competition at workspace and optional node capacity share; cross‑entity Γ coupling off by default. See #010.  
10) **Observability (Implementation Architecture) → Add metrics**: spectral radius, avalanche stats, workspace dwell/switch rate, weight‑norm histograms, and frontier size to a debug dashboard.

> These deltas are designed to preserve your phenomenology while removing numerical and control‑stability failure modes.

