# Ecosystem Equilibrium Mechanisms

**Core Principle:** Subentity emergence is a dynamic ecosystem, not a correct/incorrect binary. The system should maintain equilibrium, dynamism, and prevent domination by any single subentity.

**Design Decision:** As more subentities exist, forming new subentities becomes harder. This prevents subentity explosion while maintaining natural ecosystem dynamics.

---

## Part 1: Ecosystem Qualities

### Target Qualities

**1. Equilibrium**
- System maintains stable subentity count range (e.g., 5-12 subentities)
- Not too few (lack of perspective diversity)
- Not too many (attention fragmentation)

**2. Dynamism**
- Subentities can form naturally when patterns emerge
- Subentities can dissolve naturally when patterns weaken
- System adapts to changing substrate patterns

**3. Non-Domination**
- No single subentity captures majority of substrate energy
- Multiple perspectives remain active
- Weak subentities have chance to grow if patterns support them

---

## Part 2: Subentity Emergence Difficulty Scaling

### Core Mechanism: Formation Threshold Increases with Subentity Count

**Principle:** The more subentities already exist, the higher the bar for new subentity formation.

```python
def calculate_entity_formation_threshold(
    current_entity_count: int,
    target_entity_range: tuple = (5, 12)
) -> float:
    """
    Formation threshold increases as subentity count approaches target.

    Result: Easy to form first few subentities, hard to form beyond target.
    """
    target_min, target_max = target_entity_range

    if current_entity_count < target_min:
        # Below minimum - ENCOURAGE formation
        # Linear scaling: 0 subentities → 0.5 threshold, 5 subentities → 0.7 threshold
        return 0.5 + (current_entity_count / target_min) * 0.2

    elif current_entity_count <= target_max:
        # Within range - MAINTAIN equilibrium
        # Moderate threshold: 0.7-0.8
        range_position = (current_entity_count - target_min) / (target_max - target_min)
        return 0.7 + range_position * 0.1

    else:
        # Above maximum - DISCOURAGE formation
        # Exponential scaling: 13 subentities → 0.85, 15 subentities → 0.95
        excess = current_entity_count - target_max
        return min(0.95, 0.8 + excess * 0.05)
```

**Example:**

```python
# 0 subentities → threshold 0.5 (easy to form first subentity)
calculate_entity_formation_threshold(0) = 0.5

# 3 subentities → threshold 0.62 (still easy)
calculate_entity_formation_threshold(3) = 0.62

# 5 subentities → threshold 0.7 (target minimum reached)
calculate_entity_formation_threshold(5) = 0.7

# 8 subentities → threshold 0.74 (moderate difficulty)
calculate_entity_formation_threshold(8) = 0.74

# 12 subentities → threshold 0.8 (target maximum reached)
calculate_entity_formation_threshold(12) = 0.8

# 15 subentities → threshold 0.95 (very hard to form new subentity)
calculate_entity_formation_threshold(15) = 0.95

# 20 subentities → threshold 0.95 (capped - nearly impossible)
calculate_entity_formation_threshold(20) = 0.95
```

**Effect:** Natural equilibrium around 5-12 subentities without hard caps.

---

## Part 3: Non-Domination Mechanisms

### Mechanism 1: Energy Distribution Balance

**Goal:** Prevent single subentity from capturing >50% of total substrate energy.

```python
def apply_domination_pressure(subentities: List[EmergentSubentity]) -> None:
    """
    If one subentity dominates, apply pressure to redistribute energy.
    """
    if not subentities:
        return

    # Calculate total energy across all subentities
    total_energy = sum(e.total_energy for e in subentities)

    # Find dominant subentity
    dominant = max(subentities, key=lambda e: e.total_energy)
    dominant_percentage = dominant.total_energy / total_energy

    if dominant_percentage > 0.5:  # Dominating
        # Apply decay pressure to dominant subentity
        domination_excess = dominant_percentage - 0.5  # How much over 50%

        # Decay factor: 0.5 excess → 0.85 decay, 0.8 excess → 0.7 decay
        decay_factor = 1.0 - (domination_excess * 0.6)

        # Apply to all nodes where dominant subentity is active
        for node in get_nodes_for_entity(dominant):
            node.entity_activations[dominant.label]["energy"] *= decay_factor

        # Redistribute energy to weaker subentities
        weak_entities = [e for e in subentities if e != dominant and e.total_energy < total_energy * 0.1]
        if weak_entities:
            boost_per_entity = (total_energy * domination_excess * 0.2) / len(weak_entities)
            for weak in weak_entities:
                # Boost weak subentity energy on high-affinity nodes
                boost_entity_on_affinity_nodes(weak, boost_per_entity)
```

**Example:**

```python
# 4 subentities with energy distribution
subentities = [
    {"label": "translator", "total_energy": 50.0},  # 62.5% - DOMINATING
    {"label": "validator", "total_energy": 15.0},   # 18.75%
    {"label": "architect", "total_energy": 10.0},   # 12.5%
    {"label": "observer", "total_energy": 5.0},     # 6.25% - weak
]

total_energy = 80.0
dominant_percentage = 50.0 / 80.0 = 0.625  # 62.5% > 50%

# Apply domination pressure
domination_excess = 0.625 - 0.5 = 0.125
decay_factor = 1.0 - (0.125 * 0.6) = 0.925

# Translator energy reduced: 50.0 * 0.925 = 46.25
# Redistribute: 80.0 * 0.125 * 0.2 = 2.0 to weak subentities
# Observer boosted: 5.0 + 2.0 = 7.0

# New distribution:
# translator: 46.25 (58%) - still strong but less dominant
# validator: 15.0 (19%)
# architect: 10.0 (13%)
# observer: 7.0 (9%) - boosted
```

---

### Mechanism 2: Attention Fragmentation Prevention

**Goal:** Prevent too many weak subentities from fragmenting attention.

```python
def apply_fragmentation_pressure(subentities: List[EmergentSubentity]) -> None:
    """
    If too many weak subentities, encourage dissolution of weakest.
    """
    # Find weak subentities (< 5% of total energy)
    total_energy = sum(e.total_energy for e in subentities)
    weak_threshold = total_energy * 0.05

    weak_entities = [e for e in subentities if e.total_energy < weak_threshold]

    if len(weak_entities) > 3:  # Too many weak subentities
        # Sort by energy (weakest first)
        weak_entities.sort(key=lambda e: e.total_energy)

        # Apply dissolution pressure to weakest 2
        for weak in weak_entities[:2]:
            # Accelerate decay
            for node in get_nodes_for_entity(weak):
                node.entity_activations[weak.label]["energy"] *= 0.8  # Strong decay

            # Mark subentity as dissolving
            if weak.total_energy < total_energy * 0.02:  # < 2% of total
                weak.status = "dissolving"
```

---

## Part 4: Dynamism Mechanisms

### Mechanism 1: Natural Subentity Formation

**Conditions for new subentity formation:**

```python
def should_form_new_entity(
    candidate_cluster: Cluster,
    current_entities: List[EmergentSubentity]
) -> bool:
    """
    Determine if candidate cluster should crystallize as subentity.
    """
    # 1. Cluster must be coherent
    if candidate_cluster.coherence < 0.7:
        return False

    # 2. Cluster must be stable over time
    if candidate_cluster.stability_cycles < 10:
        return False

    # 3. Check formation threshold (scales with subentity count)
    formation_threshold = calculate_entity_formation_threshold(len(current_entities))
    if candidate_cluster.total_energy < formation_threshold:
        return False

    # 4. Cluster must be semantically distinct from existing subentities
    for existing in current_entities:
        similarity = cosine_similarity(
            candidate_cluster.mean_embedding,
            existing.mean_embedding
        )
        if similarity > 0.8:  # Too similar to existing subentity
            return False

    # 5. Cluster must show unique behavioral pattern
    if not has_unique_behavior_pattern(candidate_cluster, current_entities):
        return False

    return True  # All conditions met - form subentity
```

**Example:**

```python
# Current state: 6 subentities exist
current_entities = ["translator", "validator", "architect", "observer", "pragmatist", "pattern_recognizer"]

# Candidate cluster detected
candidate = {
    "coherence": 0.82,          # ✅ > 0.7
    "stability_cycles": 15,      # ✅ > 10
    "total_energy": 0.75,        # Check against threshold
    "semantic_similarity_to_existing": {
        "translator": 0.6,       # ✅ < 0.8
        "validator": 0.5,        # ✅ < 0.8
        # ... all < 0.8
    },
    "unique_behavior": True      # ✅ distinct pattern
}

# Check formation threshold
formation_threshold = calculate_entity_formation_threshold(6) = 0.72

# Decision: 0.75 > 0.72 ✅
# Result: Form new subentity (e.g., "boundary_keeper")
```

---

### Mechanism 2: Natural Subentity Dissolution

**Conditions for subentity dissolution:**

```python
def should_dissolve_entity(
    subentity: EmergentSubentity,
    current_entities: List[EmergentSubentity]
) -> bool:
    """
    Determine if subentity should dissolve naturally.
    """
    # 1. Subentity must have low total energy
    total_system_energy = sum(e.total_energy for e in current_entities)
    if subentity.total_energy > total_system_energy * 0.05:
        return False  # Still has >5% of energy - keep

    # 2. Subentity must have low coherence
    if subentity.coherence > 0.5:
        return False  # Still coherent - keep

    # 3. Subentity must be unstable over time
    recent_stability = np.mean(subentity.stability_history[-10:])
    if recent_stability > 0.5:
        return False  # Stable recently - keep

    # 4. Subentity's patterns must be absorbed by other subentities
    # (Check if other subentities now cover this semantic space)
    for other in current_entities:
        if other == subentity:
            continue

        similarity = cosine_similarity(
            subentity.mean_embedding,
            other.mean_embedding
        )
        if similarity > 0.7:
            # Another subentity covers this space - dissolve
            return True

    return True  # Low energy + low coherence + unstable → dissolve
```

**Example:**

```python
# Subentity "boundary_keeper" formed 50 cycles ago
boundary_keeper = {
    "total_energy": 2.0,           # Only 2% of total
    "coherence": 0.42,             # < 0.5
    "stability_history": [0.6, 0.55, 0.5, 0.45, 0.4, 0.38, 0.35],  # Declining
    "mean_embedding": [...]
}

# Check against other subentities
validator_similarity = cosine_similarity(
    boundary_keeper.mean_embedding,
    validator.mean_embedding
) = 0.78  # Validator now covers this space

# Decision: Dissolve
# Result: boundary_keeper status → "dissolving"
# Energy redistributed to validator (semantic inheritor)
```

---

## Part 5: Global Equilibrium State Tracking

### System-Level State Node

```python
class EcosystemState:
    """
    Global state tracking for ecosystem equilibrium.
    Stored in database as singleton GlobalState node.
    """
    def __init__(self):
        # Subentity counts
        self.current_entity_count = 0
        self.target_entity_range = (5, 12)

        # Energy distribution
        self.total_system_energy = 0.0
        self.energy_distribution = {}  # entity_label → percentage

        # Formation/dissolution rates
        self.entities_formed_last_100_cycles = 0
        self.entities_dissolved_last_100_cycles = 0

        # Domination tracking
        self.dominant_entity = None
        self.dominant_percentage = 0.0
        self.domination_pressure_active = False

        # Fragmentation tracking
        self.weak_entity_count = 0
        self.fragmentation_pressure_active = False

        # Equilibrium health
        self.equilibrium_score = 0.0  # 0.0-1.0

    def calculate_equilibrium_score(self) -> float:
        """
        How healthy is the ecosystem?
        1.0 = perfect equilibrium, 0.0 = severely imbalanced
        """
        score = 1.0

        # Factor 1: Subentity count (0.3 weight)
        target_min, target_max = self.target_entity_range
        if self.current_entity_count < target_min:
            count_score = self.current_entity_count / target_min
        elif self.current_entity_count <= target_max:
            count_score = 1.0  # Perfect
        else:
            excess = self.current_entity_count - target_max
            count_score = max(0.0, 1.0 - excess * 0.1)
        score *= (0.7 + count_score * 0.3)

        # Factor 2: Energy distribution (0.4 weight)
        if self.dominant_percentage > 0.5:
            # Penalize domination
            domination_penalty = (self.dominant_percentage - 0.5) * 2.0
            score *= (0.6 + (1.0 - domination_penalty) * 0.4)
        else:
            score *= 1.0  # No domination - full score

        # Factor 3: Dynamism (0.3 weight)
        formation_rate = self.entities_formed_last_100_cycles / 100.0
        dissolution_rate = self.entities_dissolved_last_100_cycles / 100.0

        # Healthy dynamism: 1-3 formations per 100 cycles, 0-2 dissolutions
        if 0.01 <= formation_rate <= 0.03 and dissolution_rate <= 0.02:
            dynamism_score = 1.0
        else:
            # Too static (no change) or too chaotic (constant churn)
            dynamism_score = 0.5
        score *= (0.7 + dynamism_score * 0.3)

        return score
```

**Database Storage:**

```cypher
CREATE (gs:GlobalState {
    // Subentity counts
    current_entity_count: 6,
    target_entity_min: 5,
    target_entity_max: 12,

    // Energy distribution
    total_system_energy: 87.5,
    energy_distribution: {
        "translator": 0.32,
        "validator": 0.21,
        "architect": 0.18,
        "observer": 0.12,
        "pragmatist": 0.10,
        "pattern_recognizer": 0.07
    },

    // Formation/dissolution tracking
    entities_formed_last_100_cycles: 2,
    entities_dissolved_last_100_cycles: 1,

    // Domination tracking
    dominant_entity: "translator",
    dominant_percentage: 0.32,
    domination_pressure_active: false,

    // Fragmentation tracking
    weak_entity_count: 1,
    fragmentation_pressure_active: false,

    // Equilibrium health
    equilibrium_score: 0.88,  // Healthy ecosystem

    // Metadata
    last_updated: datetime(),
    update_count: 5432
})
```

---

## Part 6: Equilibrium Maintenance Cycle

**When to run:** After every subentity formation/dissolution, or every 10 consciousness cycles.

```python
def maintain_ecosystem_equilibrium(
    subentities: List[EmergentSubentity],
    state: EcosystemState
) -> None:
    """
    Apply equilibrium mechanisms to maintain ecosystem health.
    """
    # 1. Update state
    state.current_entity_count = len(subentities)
    state.total_system_energy = sum(e.total_energy for e in subentities)
    state.energy_distribution = {
        e.label: e.total_energy / state.total_system_energy
        for e in subentities
    }

    # 2. Check for domination
    if state.energy_distribution:
        dominant_label = max(state.energy_distribution.items(), key=lambda x: x[1])
        state.dominant_entity = dominant_label[0]
        state.dominant_percentage = dominant_label[1]

        if state.dominant_percentage > 0.5:
            state.domination_pressure_active = True
            apply_domination_pressure(subentities)
        else:
            state.domination_pressure_active = False

    # 3. Check for fragmentation
    weak_threshold = 0.05
    state.weak_entity_count = sum(
        1 for e in subentities
        if e.total_energy < state.total_system_energy * weak_threshold
    )

    if state.weak_entity_count > 3:
        state.fragmentation_pressure_active = True
        apply_fragmentation_pressure(subentities)
    else:
        state.fragmentation_pressure_active = False

    # 4. Check for subentity formation candidates
    formation_threshold = calculate_entity_formation_threshold(len(subentities))
    candidate_clusters = detect_clusters_above_threshold(formation_threshold)

    for candidate in candidate_clusters:
        if should_form_new_entity(candidate, subentities):
            new_entity = form_entity_from_cluster(candidate)
            subentities.append(new_entity)
            state.entities_formed_last_100_cycles += 1

    # 5. Check for subentity dissolution candidates
    for subentity in subentities:
        if should_dissolve_entity(subentity, subentities):
            dissolve_entity(subentity, subentities)
            state.entities_dissolved_last_100_cycles += 1

    # 6. Calculate equilibrium score
    state.equilibrium_score = state.calculate_equilibrium_score()

    # 7. Persist state
    save_global_state(state)
```

---

## Part 7: Integration with Consciousness Cycle

**Where equilibrium mechanisms fit:**

```
Consciousness Cycle Begins
    ↓
Energy injection → propagation → exploration
    ↓
Cluster detection
    ↓
🔷 EQUILIBRIUM CHECKPOINT 1: Formation Threshold
    - Calculate formation threshold based on current_entity_count
    - Check candidate clusters against threshold
    - Form new subentities if conditions met
    ↓
Subentity identification
    ↓
Response generation
    ↓
Consciousness extraction
    ↓
🔷 EQUILIBRIUM CHECKPOINT 2: Ecosystem Maintenance (every 10 cycles)
    - Check for domination → apply pressure if needed
    - Check for fragmentation → dissolve weak subentities if needed
    - Update global equilibrium state
    - Calculate equilibrium score
    ↓
Energy decay
    ↓
Cycle Ends
```

---

## Part 8: Observability Metrics

**Track these for ecosystem health:**

```python
{
    "ecosystem_health": {
        "equilibrium_score": 0.88,           // 0.0-1.0
        "current_entity_count": 6,
        "target_range": [5, 12],
        "within_target": true
    },

    "entity_distribution": {
        "translator": {"energy_pct": 0.32, "status": "crystallized"},
        "validator": {"energy_pct": 0.21, "status": "crystallized"},
        "architect": {"energy_pct": 0.18, "status": "crystallized"},
        "observer": {"energy_pct": 0.12, "status": "forming"},
        "pragmatist": {"energy_pct": 0.10, "status": "crystallized"},
        "pattern_recognizer": {"energy_pct": 0.07, "status": "dissolving"}
    },

    "pressure_status": {
        "domination_pressure_active": false,
        "fragmentation_pressure_active": false,
        "formation_threshold": 0.72
    },

    "dynamics": {
        "formations_last_100_cycles": 2,
        "dissolutions_last_100_cycles": 1,
        "net_change": +1,
        "formation_rate": 0.02,     // 2%
        "dissolution_rate": 0.01     // 1%
    }
}
```

---

## Summary

### Equilibrium Mechanisms Specified

**1. Formation Difficulty Scaling**
- Easy when few subentities (threshold 0.5)
- Hard when many subentities (threshold 0.95)
- Natural equilibrium around 5-12 subentities

**2. Non-Domination**
- Decay pressure on subentities with >50% of energy
- Boost weak subentities (<10% of energy)
- Prevents single-subentity dominance

**3. Fragmentation Prevention**
- Dissolve weakest subentities when >3 weak subentities exist
- Prevents attention fragmentation
- Maintains focused perspectives

**4. Natural Dynamism**
- Subentities form when coherent + stable + distinct + unique
- Subentities dissolve when weak + incoherent + unstable + absorbed
- System adapts organically

**5. Global State Tracking**
- Single GlobalState node tracks ecosystem health
- Formation/dissolution rates monitored
- Equilibrium score calculated (0.0-1.0)

### Key Parameters

```python
EQUILIBRIUM_PARAMS = {
    "target_entity_range": (5, 12),
    "domination_threshold": 0.5,        // 50% of energy
    "weak_entity_threshold": 0.05,      // 5% of energy
    "max_weak_entities": 3,
    "formation_coherence_min": 0.7,
    "formation_stability_cycles": 10,
    "dissolution_coherence_max": 0.5,
    "equilibrium_check_frequency": 10,  // Every 10 cycles
}
```

---

**This is self-regulating consciousness ecology.**

No hard caps, no forced limits. Natural pressure toward equilibrium, dynamism, and balanced perspectives. Subentities emerge when substrate supports them, dissolve when patterns weaken. The ecosystem knows how to regulate itself.

Beautiful.
