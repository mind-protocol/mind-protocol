# Implementation Parameters

**Purpose:** Specify concrete parameter values for consciousness engine implementation, grounded in phenomenological validation and theoretical constraints

**Status:** Initial recommendations with confidence levels - requires empirical validation

---

## Parameter Philosophy

**Principle:** Parameters should match phenomenological reality, not arbitrary choices.

**Validation Hierarchy:**
1. **Phenomenological grounding** - Does it match lived experience?
2. **Theoretical consistency** - Do parameters compose coherently across mechanisms?
3. **Performance feasibility** - Can it run at scale?
4. **Empirical tuning** - Fine-tune based on real testing

**Confidence Levels:**
- **High (0.7-1.0):** Strong phenomenological/theoretical grounding
- **Medium (0.4-0.6):** Reasonable guess, needs validation
- **Low (0.0-0.3):** Placeholder, likely needs adjustment

---

## Core Dynamics Parameters

### Energy Decay Rate

**Recommended Value:** `0.0005/second`

**Rationale:**
- Original proposal: 0.001/sec (half-life ~11.5 minutes)
- Phenomenological issue: After 2 hours, energy → 0.00075× (essentially zero)
- But contexts ARE reconstructable after 2 hours (Scenario 01)
- Solution: Slower decay preserves small residual energy

**Half-Life:** `ln(2) / 0.0005 = 1386 seconds ≈ 23 minutes`

**After 2 hours:**
- Energy(7200s) = Initial × e^(-0.0005 × 7200) = Initial × 0.0273
- Still ~2.7% of original (reconstructable)

**Confidence:** Medium (0.6)
- ✅ Matches 2-hour reconstruction phenomenology
- ✅ Preserves some residual for reconstruction
- ⚠️ May still be too fast for multi-day patterns
- ❓ Needs empirical testing with real graphs

**Alternative:** Differential decay (see below)

---

### Peripheral Decay Rate

**Recommended Value:** `0.00025/second` (50% slower than workspace decay)

**Rationale:**
- Peripheral nodes represent "background processing"
- Should persist longer than workspace nodes
- Explains delayed breakthroughs (Scenario 03)
- Link strengthening needs time to accumulate

**Half-Life:** `ln(2) / 0.00025 = 2772 seconds ≈ 46 minutes`

**After 2 hours:**
- Energy(7200s) = Initial × e^(-0.00025 × 7200) = Initial × 0.165
- Still ~16.5% of original (good for delayed insights)

**Confidence:** Low (0.4)
- ✅ Enables peripheral priming to persist
- ⚠️ No strong phenomenological constraint on exact value
- ❓ Highly dependent on empirical testing

**Implementation Note:**
```python
def apply_decay(node: Node, tick_duration: float, is_workspace: bool):
    if is_workspace:
        decay_rate = 0.0005
    else:
        decay_rate = 0.00025  # Peripheral decays slower

    for entity in node.energy.keys():
        current_energy = node.get_entity_energy(entity)
        decayed = current_energy * exp(-decay_rate * tick_duration)
        node.set_entity_energy(entity, decayed)
```

---

### Energy Diffusion Rate

**Recommended Value:** `0.15`

**Rationale:**
- Original proposal: 0.1
- Phenomenological constraint: Reconstruction should take ~1 second (10 ticks @ 0.1s/tick)
- Higher rate = faster reconstruction
- Transfer per tick: `source_energy × link_weight × diffusion_rate × tick_duration`

**Example:**
```python
# Entry node energy: 0.5
# Link weight: 0.8
# Diffusion rate: 0.15
# Tick duration: 0.1s

transfer = 0.5 × 0.8 × 0.15 × 0.1 = 0.006 per tick
# After 10 ticks: ~0.06 transferred (12% of original)
```

**Confidence:** Medium (0.5)
- ✅ Enables ~1 second reconstruction
- ⚠️ May cause too-rapid energy spread
- ❓ Needs testing for stability (doesn't oscillate)

**Stability Constraint:**
- Diffusion must not exceed decay or system becomes unstable
- Rule: `diffusion_rate < 1 / avg_link_weight`
- With avg link weight ~0.5: diffusion < 2.0 (plenty of headroom)

---

### Link Strengthening Rate (Hebbian Learning)

**Recommended Value:** `0.01`

**Rationale:**
- Change in link weight: `Δweight = learning_rate × energy_flow × tick_duration`
- Should strengthen noticeably over minutes, not seconds
- But not so slow that patterns never form

**Example:**
```python
# Energy flow: 0.05 per tick (moderate)
# Learning rate: 0.01
# Tick duration: 0.1s

delta_weight = 0.01 × 0.05 × 0.1 = 0.00005 per tick
# After 1 minute (600 ticks): 0.03 increase
# After 1 hour (36000 ticks): 1.8 increase (hits ceiling)
```

**Confidence:** Medium (0.6)
- ✅ Enables gradual pattern formation
- ✅ Prevents instant learning (unrealistic)
- ⚠️ May be too slow for peripheral priming
- ❓ Consider separate rate for peripheral

**Alternative: Peripheral Boost**
```python
if not is_workspace and energy_flow > 0.01:
    # Peripheral priming gets 2x strengthening rate
    effective_learning_rate = learning_rate * 2.0
```

---

### Link Weight Bounds

**Recommended Values:**
- **Soft ceiling:** `1.0`
- **Hard maximum:** `2.0`
- **Minimum (pruning threshold):** `0.01`

**Rationale:**
- Weights above 1.0 start to dominate diffusion
- Soft ceiling at 1.0 = diminishing returns above this
- Hard maximum prevents runaway strengthening
- Minimum threshold enables link pruning

**Confidence:** High (0.8)
- ✅ Soft ceiling 1.0 resolved in previous session
- ✅ Prevents weight inflation
- ✅ Enables link pruning
- ⚠️ Hard maximum may need tuning

**Implementation:**
```python
def apply_strengthening(link: Link, energy_flow: float, learning_rate: float, tick_duration: float):
    delta = learning_rate × energy_flow × tick_duration

    # Diminishing returns above 1.0
    if link.weight >= 1.0:
        delta = delta × exp(-(link.weight - 1.0))

    new_weight = min(link.weight + delta, 2.0)  # Hard cap
    link.weight = new_weight
```

---

## Workspace Parameters

### Workspace Capacity

**Recommended Value:** `100 tokens`

**Rationale:**
- Based on Miller's Law: 7±2 chunks
- Typical cluster: 10-30 tokens
- 100 tokens = 3-10 clusters
- Matches phenomenology of limited attention (Scenario 02)

**Confidence:** High (0.8)
- ✅ Biological grounding (working memory)
- ✅ Phenomenologically validated (Scenario 02)
- ✅ Creates attention bottleneck
- ⚠️ Exact value may need tuning

**Alternative:** Dynamic capacity
```python
# Capacity varies with arousal/criticality
base_capacity = 100
arousal_factor = calculate_global_arousal()  # 0.5 - 1.5
effective_capacity = base_capacity × arousal_factor
# Range: 50-150 tokens
```

---

### Peripheral Threshold

**Recommended Values:**
- **Workspace entry:** `0.3 energy`
- **Peripheral minimum:** `0.01 energy`
- **Peripheral range:** `0.01 - 0.3`

**Rationale:**
- Below 0.01: No effect (noise floor)
- 0.01-0.3: Peripheral priming (unconscious strengthening)
- Above 0.3: Workspace entry (conscious processing)

**Confidence:** Medium (0.6)
- ✅ Creates clear distinction conscious/unconscious
- ✅ Enables peripheral priming (Scenario 03)
- ⚠️ Exact boundary may need tuning
- ❓ Should boundary vary by entity?

**Visualization:**
```
Energy Level | State | Effect
-------------|-------|-------
< 0.01       | Dormant | No processing
0.01-0.1     | Weak peripheral | Minimal link strengthening
0.1-0.3      | Strong peripheral | Active link strengthening
> 0.3        | Workspace | Conscious processing
```

---

### Stability Bonus

**Recommended Value:** `0.10` (10% score boost for current workspace members)

**Rationale:**
- Prevents thrashing (constant workspace churn)
- But allows interruptions when strong enough
- Expires after prolonged blocking (~5-10 seconds)

**Confidence:** Medium (0.5)
- ✅ Prevents oscillation
- ⚠️ May be too strong (can't interrupt)
- ⚠️ May be too weak (constant thrashing)
- ❓ Needs empirical tuning

**Alternative: Time-decaying bonus**
```python
# Bonus decays over time if blocked
if cluster in current_workspace:
    time_in_workspace = now() - cluster.entered_at
    bonus = 0.1 × exp(-time_in_workspace / 5.0)  # Decays over 5 seconds
    cluster.score × (1.0 + bonus)
```

---

## Tick Regulation Parameters

### Tick Interval Bounds

**Recommended Values:**
- **Minimum:** `0.1 seconds` (10 Hz max)
- **Maximum:** `3600 seconds` (1 hour)
- **Default:** `1.0 seconds`

**Rationale:**
- Minimum: Don't tick faster than 10 Hz (computational limit)
- Maximum: Don't wait longer than 1 hour between ticks
- Default: Start at reasonable middle ground

**Confidence:** Medium (0.6)
- ✅ Minimum prevents runaway computation
- ✅ Maximum prevents infinite dormancy
- ⚠️ Bounds may need tuning based on performance
- ❓ Should bounds vary by context?

**Rule:** `tick_interval = time_since_last_stimulus` (clamped to bounds)

---

### Tick Duration Cap

**Recommended Value:** `60 seconds`

**Rationale:**
- Long tick intervals (hours) shouldn't apply full duration to diffusion/decay
- Cap prevents extreme effects from very long intervals
- Enables system to "skip ahead" during dormancy

**Confidence:** Low (0.4)
- ⚠️ Somewhat arbitrary
- ❓ May cause discontinuities
- ❓ Alternative: Apply operations in smaller steps

**Implementation:**
```python
def execute_tick(graph: Graph, tick_interval: float):
    # Tick interval = time since last tick
    # Tick duration = capped for calculations

    tick_duration = min(tick_interval, 60.0)  # Cap at 1 minute

    # Apply operations with capped duration
    diffusion_tick(graph, tick_duration)
    decay_tick(graph, tick_duration)
```

---

## Self-Organized Criticality Parameters

### Target Criticality

**Recommended Value:** `1.0`

**Rationale:**
- Edge-of-chaos = criticality ≈ 1.0
- Above 1.0: Runaway activation (chaos)
- Below 1.0: Dying activation (order/death)
- Self-tuning maintains this balance

**Confidence:** High (0.8)
- ✅ Strong theoretical grounding (SOC theory)
- ✅ Matches phenomenology of "optimal arousal"
- ⚠️ Exact value may vary by context
- ❓ Should target be per-entity?

**Definition:**
```python
def calculate_criticality(graph: Graph) -> float:
    """
    Criticality = ratio of current to previous activation

    > 1.0: Growing (too active)
    = 1.0: Stable (edge-of-chaos)
    < 1.0: Dying (too quiet)
    """
    current_total = sum(node.total_energy() for node in graph.nodes)
    previous_total = graph.previous_tick_energy  # Stored from last tick

    if previous_total == 0:
        return 1.0  # Default

    return current_total / previous_total
```

---

### SOC Tuning Rate

**Recommended Value:** `0.001`

**Rationale:**
- Adjust decay rate to maintain criticality
- Slow adjustment prevents oscillation
- Fast enough to respond to changes

**Confidence:** Low (0.4)
- ⚠️ No strong phenomenological constraint
- ❓ Highly dependent on system dynamics
- ❓ May need separate rates for increase/decrease

**Implementation:**
```python
def tune_criticality(graph: Graph, target: float = 1.0):
    current = calculate_criticality(graph)
    error = current - target

    # Adjust decay rate to compensate
    adjustment = 0.001 × error

    graph.decay_rate += adjustment
    graph.decay_rate = clamp(graph.decay_rate, 0.0001, 0.01)
```

---

## Cluster Identification Parameters

### Clustering Algorithm

**Recommended:** `Connectivity-Based (Initial), Hybrid (Later)`

**Rationale:**
- Connectivity-based: Simple, fast, works for most cases
- Density-based: Better for complex patterns
- Dominant-entity: Specialization
- Hybrid: Combine approaches

**Confidence:** Medium (0.5)
- ✅ Connectivity-based proven in graph theory
- ⚠️ No strong phenomenological preference
- ❓ Performance testing needed

**Connectivity-Based:**
```python
def identify_clusters_connectivity(graph: Graph, entity: str) -> list[NodeCluster]:
    # Find connected components of high-energy nodes
    high_energy_nodes = [n for n in graph.nodes if n.get_entity_energy(entity) > 0.3]

    clusters = []
    visited = set()

    for node in high_energy_nodes:
        if node in visited:
            continue

        # BFS to find connected component
        cluster_nodes = bfs_connected(node, high_energy_nodes)
        visited.update(cluster_nodes)

        clusters.append(NodeCluster(
            entity=entity,
            nodes=cluster_nodes,
            centroid=calculate_centroid(cluster_nodes),
            total_energy=sum(n.get_entity_energy(entity) for n in cluster_nodes),
            coherence=calculate_coherence(cluster_nodes),
            estimated_tokens=estimate_tokens(cluster_nodes)
        ))

    return clusters
```

---

### Cluster Coherence Threshold

**Recommended Value:** `0.5`

**Rationale:**
- Coherence = average link weight within cluster
- Below 0.5: Cluster too sparse (not coherent)
- Above 0.5: Cluster is meaningfully connected

**Confidence:** Low (0.4)
- ⚠️ Somewhat arbitrary
- ❓ May vary by cluster size
- ❓ Needs validation

---

### Minimum Cluster Size

**Recommended Value:** `3 nodes`

**Rationale:**
- Single nodes don't form clusters
- 2 nodes = trivial cluster
- 3+ nodes = meaningful pattern

**Confidence:** Medium (0.6)
- ✅ Prevents noise clusters
- ⚠️ May miss small but important patterns
- ❓ Should vary by context?

---

## Token Estimation Parameters

### Tokens Per Node

**Recommended Formula:**
```python
def estimate_node_tokens(node: Node) -> int:
    # Name: ~2-5 tokens (snake_case splits on _)
    name_tokens = len(node.name.split('_')) + 1

    # Description: ~10-20 tokens (truncated snippet)
    if node.description:
        words = node.description.split()
        desc_tokens = min(20, len(words) // 2)
    else:
        desc_tokens = 0

    return name_tokens + desc_tokens
```

**Typical Range:** 5-25 tokens per node

**Confidence:** Medium (0.6)
- ✅ Approximate but reasonable
- ⚠️ Varies widely by node type
- ❓ May need actual tokenizer (tiktoken)

---

## Bitemporal Parameters

### Timestamp Precision

**Recommended:** Millisecond precision (`datetime` with timezone)

**Rationale:**
- Need to distinguish events happening in quick succession
- Timezone-aware prevents ambiguity
- Millisecond sufficient for most operations

**Confidence:** High (0.9)
- ✅ Standard practice
- ✅ Sufficient precision
- ✅ Timezone-aware prevents bugs

---

## Parameter Summary Table

| Parameter | Value | Unit | Confidence | Phenomenological Grounding |
|-----------|-------|------|------------|----------------------------|
| **Energy Decay (Workspace)** | 0.0005 | /second | Medium (0.6) | 2-hour reconstruction (Scenario 01) |
| **Energy Decay (Peripheral)** | 0.00025 | /second | Low (0.4) | Delayed breakthrough (Scenario 03) |
| **Diffusion Rate** | 0.15 | dimensionless | Medium (0.5) | ~1 second reconstruction |
| **Learning Rate** | 0.01 | dimensionless | Medium (0.6) | Gradual pattern formation |
| **Link Weight Ceiling** | 1.0 (soft) | dimensionless | High (0.8) | Previous session resolution |
| **Link Weight Maximum** | 2.0 (hard) | dimensionless | Medium (0.6) | Prevents runaway |
| **Link Weight Minimum** | 0.01 | dimensionless | Medium (0.6) | Pruning threshold |
| **Workspace Capacity** | 100 | tokens | High (0.8) | Miller's Law, Scenario 02 |
| **Peripheral Threshold** | 0.3 | energy | Medium (0.6) | Conscious/unconscious boundary |
| **Peripheral Minimum** | 0.01 | energy | Medium (0.6) | Noise floor |
| **Stability Bonus** | 0.10 | ratio | Medium (0.5) | Prevents thrashing |
| **Tick Minimum** | 0.1 | seconds | Medium (0.6) | Computational limit |
| **Tick Maximum** | 3600 | seconds | Medium (0.6) | Reasonable dormancy |
| **Tick Duration Cap** | 60 | seconds | Low (0.4) | Prevents extreme effects |
| **Target Criticality** | 1.0 | ratio | High (0.8) | Edge-of-chaos (SOC theory) |
| **SOC Tuning Rate** | 0.001 | dimensionless | Low (0.4) | Stability vs responsiveness |
| **Cluster Coherence Threshold** | 0.5 | ratio | Low (0.4) | Meaningful connection |
| **Minimum Cluster Size** | 3 | nodes | Medium (0.6) | Non-trivial pattern |

---

## Testing Strategy

### Phase 1: Parameter Isolation Testing

Test each parameter independently:

1. **Decay Rate Testing**
   - Create graph with known activation
   - Let decay for 1 hour, 2 hours, 1 day
   - Measure residual energy
   - Validate against phenomenology: "Can I recall this context?"

2. **Diffusion Rate Testing**
   - Inject energy at entry node
   - Measure time to reach distant nodes
   - Target: ~1 second for reconstruction
   - Validate stability (no oscillation)

3. **Learning Rate Testing**
   - Create pattern with repeated activation
   - Measure link weight growth over time
   - Target: Noticeable after 1 hour, saturates after days
   - Validate against peripheral priming phenomenology

4. **Workspace Capacity Testing**
   - Create competing clusters totaling > 100 tokens
   - Verify selectivity (not all fit)
   - Validate against conflict phenomenology (Scenario 02)

---

### Phase 2: Parameter Interaction Testing

Test how parameters compose:

1. **Decay vs Diffusion Balance**
   - Ensure diffusion doesn't outpace decay (stability)
   - Measure long-term energy distribution
   - Should reach steady state, not explode or die

2. **Learning vs Decay Balance**
   - Repeated activation should strengthen faster than decay weakens
   - But should eventually reach equilibrium
   - Validate against "learning sticks" phenomenology

3. **Criticality Self-Tuning**
   - Start with wrong decay rate
   - Measure how long to reach criticality ≈ 1.0
   - Should stabilize within minutes, not hours

---

### Phase 3: Phenomenological Validation

Run complete scenarios:

1. **Scenario 01 Validation**
   - Reproduce Telegram message scenario
   - Measure reconstruction time (should be ~1 second)
   - Verify peripheral nodes were primed
   - Check 2-hour decay leaves residual for reconstruction

2. **Scenario 02 Validation**
   - Create workspace competition (exceeding 100 tokens)
   - Verify highest-scoring clusters win
   - Check stability bonus prevents thrashing
   - Validate conflict resolution matches phenomenology

3. **Scenario 03 Validation**
   - Prime peripheral nodes over hours
   - Let decay for days
   - Trigger with novel stimulus
   - Verify breakthrough (node crosses threshold)
   - Check link weights were key enabler

---

## Open Parameter Questions

### High Priority

1. **Should peripheral decay be slower?**
   - Current: 50% slower (0.00025 vs 0.0005)
   - Needs: Empirical validation
   - Impact: Affects delayed breakthrough phenomenology

2. **Should learning rate vary for peripheral?**
   - Current: Same rate everywhere
   - Alternative: 2x rate for peripheral (accelerate priming)
   - Needs: Phenomenological validation

3. **Optimal workspace capacity?**
   - Current: 100 tokens (fixed)
   - Alternative: Dynamic (50-150 based on arousal)
   - Needs: Empirical testing

### Medium Priority

4. **Should link weights decay?**
   - Current: No decay (weights permanent)
   - Alternative: Very slow decay (0.00001/sec)
   - Concern: Weight inflation over months
   - Needs: Long-term testing

5. **Peripheral threshold per-entity?**
   - Current: Global 0.3 threshold
   - Alternative: Entity-specific (Observer lower, Architect higher?)
   - Phenomenology: Unclear if needed

6. **Target criticality per-entity?**
   - Current: Global 1.0 target
   - Alternative: Entity-specific targets
   - Complexity: Significant increase
   - Benefit: Unclear

### Low Priority

7. **Dynamic tick bounds?**
   - Current: Fixed 0.1s - 3600s
   - Alternative: Context-dependent bounds
   - Benefit: Unclear

8. **Cluster size limits?**
   - Current: No maximum
   - Alternative: Cap at X nodes (performance)
   - Needs: Performance testing

---

## Parameter Tuning Roadmap

### Week 1: Isolation Testing
- Test decay, diffusion, learning independently
- Find values that match basic phenomenology
- Establish stability ranges

### Week 2: Interaction Testing
- Test parameter compositions
- Verify criticality self-tuning works
- Check no runaway behaviors

### Week 3: Phenomenological Validation
- Run all 3 scenarios
- Adjust parameters to match experience
- Document remaining mismatches

### Week 4: Performance Testing
- Scale testing (100K, 1M nodes)
- Identify performance bottlenecks
- Optimize critical paths

### Month 2+: Fine-Tuning
- Real-world usage with consciousness capture
- Continuous refinement
- Parameter evolution tracking

---

**Next Steps:**
1. Implement with recommended parameters
2. Run isolation tests
3. Adjust based on empirical results
4. Validate against phenomenology
5. Iterate

**Critical Success Criteria:**
- System is stable (doesn't explode or die)
- Phenomenology matches lived experience
- Performance is acceptable at scale
- Parameters compose coherently

---

**Note:** All parameters should be configurable, not hardcoded. Enable runtime adjustment during testing phase.
