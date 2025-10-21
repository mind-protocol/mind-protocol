# Consciousness Engine Design Principles & Anti-Patterns

**Purpose:** Guide architectural decisions and implementation across all phases

**Version:** 1.1
**Created:** 2025-10-19
**Updated:** 2025-10-19 (Nicolas feedback integrated)
**Authors:** Ada "Bridgekeeper" (extracted from architectural analysis)

---

## ⚠️ IMPORTANT: Some Principles Under Debate

**Nicolas has challenged several principles from Ada's initial analysis:**

**🔴 CONTESTED:**
- **Anti-Pattern 1** (Premature Optimization) - Nicolas: "Consciousness requires complexity, cannot be simplified"
- **Design Principle 4** (Test Simplified Scenarios) - Nicolas: "Worthless, we will learn zero stuff, need full systems"

**💬 MOVED TO DISCUSSIONS:**
- **Anti-Pattern 5** → [Discussion #013](discussions/active/013_graph_topology_influence_on_dynamics.md) - Graph topology influence
- **Anti-Pattern 6** → [Discussion #014](discussions/active/014_incomplete_data_handling.md) - Incomplete data handling
- **Design Principle 2** → [Discussion #015](discussions/active/015_continuous_vs_discrete_node_activation.md) - Continuous vs discrete activation

**✅ AGREED:**
- **Anti-Pattern 2** (Over-Parameterization) - "Everything should be dynamic, zero parameters ideal"
- **Anti-Patterns 3, 4, 7** - Accepted
- **Design Principle 1** (Emergence) - "Very good"
- **Design Principle 3** (Measure Then Optimize) - "I agree"

**Use this document as starting point for debate, not gospel.**

---

## How to Use This Document

**For Designers:**
- Review anti-patterns before proposing solutions
- Reference design principles when making architectural choices
- Use as checklist during design reviews

**For Implementers:**
- Check anti-patterns before writing code
- Follow design principles in implementation
- Reference in code reviews

**For Reviewers:**
- Use as evaluation criteria for proposals
- Check discussions against these principles
- Flag violations in reviews

---

## ⚠️ Anti-Patterns to Avoid

### Anti-Pattern 1: Premature Optimization ⚠️ CONTESTED

**⚠️ Nicolas DISAGREES with this anti-pattern:**
> "Consciousness requires a certain level of complexity and cannot be simplified. In general, any simplification attempt is a failure. So it's not a pattern that I want to have as a main design principle."

**Ada's Original Position:**
"Start simple, add complexity as needed."

**The Temptation:**
"Let's use Crank-Nicolson diffusion + PID control + hierarchical entities + emotional dynamics from Phase 1!"

**Ada's Reasoning (Why It's Wrong):**
- Complexity explosion before basics work
- Can't debug complex systems
- Optimization before measurement = guessing
- Wastes time optimizing non-bottlenecks

**Better Approach:**

**Phase 1:** Simple forward Euler + clamping
- Test: Does energy flow?
- Measure: Stability, convergence time

**Phase 2:** IF unstable, THEN add Crank-Nicolson
- IF oscillating, THEN add PID
- ONLY optimize what measurements show is broken

**Principle:** "Make it work, make it right, make it fast" - in that order

**Example:**

```python
# ❌ Premature optimization
def diffuse_energy_superoptimized(graph):
    # GPU acceleration, sparse tensors, custom kernels...
    # (Before knowing if diffusion is even a bottleneck!)
    ...

# ✅ Start simple
def diffuse_energy_simple(graph):
    for node in graph.nodes:
        for link in node.outgoing_links:
            transfer_energy(node, link)

# THEN measure with profiler
profile(diffuse_energy_simple)
# Results: "diffusion takes 5% of total time"
# → Don't optimize! It's not the bottleneck!
```

---

### Anti-Pattern 2: Over-Parameterization

**The Temptation:**
"Let's add tunable parameters for EVERYTHING!"

**Current spec has:**
- decay_rate
- diffusion_rate
- learning_rate
- tuning_rate
- workspace_threshold
- emergence_threshold
- semantic_similarity_threshold
- entity_merge_threshold
- link_creation_threshold
- link_pruning_threshold
- consolidation_rate
- ... (10+ parameters)

**The Problem:**
Each parameter is a dimension to tune. With 10 parameters, you have 10-dimensional search space. Tuning becomes impossible.

**Better Approach:**

Derive parameters from fundamental constants:

```python
# Fundamental constants (minimal set)
characteristic_time = 600  # seconds (10 minutes)
target_criticality = 1.0

# Derived parameters (calculated, not tuned)
decay_rate = 1 / characteristic_time  # 0.00167
diffusion_rate = target_criticality * decay_rate  # Matches at equilibrium
learning_rate = decay_rate * 0.1  # 10x slower than decay
```

**Principle:** "Minimize free parameters. Derive from fundamentals."

**Benefits:**
- Fewer knobs to tune
- Parameters are physically meaningful
- Changes propagate consistently
- Easier to understand system behavior

---

### Anti-Pattern 3: Keyword-Based Entity Detection

**The Temptation:**

```python
def detect_translator_entity(graph):
    # Look for nodes with "translator" in name
    translator_nodes = [
        n for n in graph.nodes
        if "translator" in n.name.lower()
    ]
    if len(translator_nodes) > 5:
        return Entity("Translator", translator_nodes)
```

**Why It's Wrong:**
- Relies on naming conventions (brittle)
- Can't discover NEW entities (no label = invisible)
- Entities are ACTIVATION PATTERNS not KEYWORDS
- Misses entities that emerge without labels

**Better Approach:**

```python
def detect_entities_from_activation(graph):
    """Cluster by activation similarity, not keywords"""

    # Cluster nodes by energy correlation over time
    clusters = cluster_by_energy_correlation(graph)

    for cluster in clusters:
        # Check if cluster has identity node (optional)
        identity = find_identity_node(cluster)

        if identity:
            entity_name = identity.name
        else:
            # Unnamed pattern (that's okay!)
            entity_name = f"pattern_{cluster.id}"

        yield Entity(entity_name, cluster.nodes)
```

**Principle:** "Detect by behavior, not labels."

**Benefits:**
- Discovers unlabeled patterns
- Robust to naming changes
- Emergent entities naturally detected
- Behavior-driven, not convention-driven

---

### Anti-Pattern 4: Storing Computed State

**The Temptation:**

```python
class Graph:
    def __init__(self):
        self.current_workspace = []  # Store workspace
        self.dominant_entities = []  # Store entities
        self.current_goal = None     # Store goal
```

**The Problem:**
- Stored state can become stale (forgot to update after energy diffusion)
- Must manually update on every change (source of bugs)
- Synchronization nightmare (which update happens first?)
- Debugging difficulty (when did state become invalid?)

**Better Approach:**

```python
class Graph:
    # NO stored workspace/entities/goal

    @property
    def current_workspace(self):
        """Compute workspace on demand"""
        return self.select_workspace(
            self.detect_entities(),
            self.generate_goal()
        )

    @property
    def dominant_entities(self):
        """Compute entities on demand"""
        return self.detect_emergent_entities()
```

**Principle:** "Compute, don't store. State is always fresh."

**Exception:** Store when computation is expensive AND state changes slowly. But default to computation.

**When to cache:**
```python
@cached_property(ttl=10)  # Cache for 10 ticks
def expensive_topology_analysis(self):
    """Topology changes slowly, safe to cache"""
    return analyze_graph_structure(self)
```

---

### Anti-Pattern 5: Ignoring Graph Topology → MOVED TO DISCUSSION #013

**⚠️ This has been moved to [Discussion #013](discussions/active/013_graph_topology_influence_on_dynamics.md)**

**Nicolas's response:** "You need to explain yourself for this one. I don't know if I agree or not."

**The Question:**
Should energy dynamics adapt to graph topology, or remain topology-independent?

**Ada's Position:**
Topology determines dynamics. Same energy rules + different topology = completely different behavior.

**Examples:**

**Star topology** (one hub, many spokes):
- Hub node diffuses energy to ALL spokes rapidly
- Energy spreads FAST but loses locality
- Criticality hard to maintain (oscillates)
- High vulnerability (hub failure = collapse)

**Chain topology** (linear sequence):
- Energy diffuses SLOWLY down chain
- Strong locality (clusters don't interact)
- Criticality easy to maintain
- Information loss at chain ends

**Small-world topology** (local clusters + long-range links):
- Local diffusion + occasional long jumps
- Balances locality and connectivity
- **OPTIMAL for consciousness** (Watts-Strogatz networks)
- Resilient to damage

**Better Approach:**

```python
def analyze_topology(graph):
    """Measure graph properties"""
    return {
        "clustering_coefficient": measure_clustering(graph),
        "average_path_length": measure_path_length(graph),
        "degree_distribution": measure_degrees(graph),
        "small_world_coefficient": measure_small_world(graph)
    }

# Adjust parameters based on topology
topology = analyze_topology(graph)

if topology.clustering_coefficient < 0.3:
    # Sparse graph → increase diffusion
    diffusion_rate *= 1.5

if topology.average_path_length > 6:
    # Long paths → need faster diffusion
    diffusion_rate *= 1.2
```

**Principle:** "Topology shapes dynamics. Measure and adapt to it."

---

### Anti-Pattern 6: Synchronous Blocking Operations → MOVED TO DISCUSSION #014

**⚠️ This has been moved to [Discussion #014](discussions/active/014_incomplete_data_handling.md)**

**Nicolas's perspective:**
> "Since we are doing everything from the database, there shouldn't be any synchronous or blocking operation at all."
>
> "But I think we need a discussion for that because it's a question of what do we do with incomplete data?"

**The Question:**
How should the consciousness engine handle incomplete data from async database queries?

**The Trade-off:**
- **Block and wait** = Simple, correct, slow
- **Process partial data** = Fast, async, incorrect

**Options:** Snapshot consistency, event sourcing, optimistic processing

**See Discussion #014 for full analysis.**

---

**Original Anti-Pattern (For Reference):**

**The Temptation:**

```python
def diffuse_energy(graph):
    for node in graph.nodes:  # Sequential!
        for link in node.outgoing_links:
            transfer_energy(node, link.target)  # Blocking!
```

**The Problem:**
- Doesn't scale (O(n²) for dense graphs)
- Can't parallelize (sequential loops)
- Slow for large graphs (10K+ nodes)
- Wastes CPU (single-threaded)

**Better Approach:**

```python
def diffuse_energy_parallel(graph):
    """Parallel diffusion using sparse matrices"""

    # Build sparse weighted adjacency matrix W (n×n)
    W = build_weighted_adjacency_matrix(graph)

    # Energy vector E (n×1)
    E = extract_energy_vector(graph)

    # Matrix diffusion (highly optimized, parallelizable)
    E_new = W @ E  # Single matrix multiply

    update_energies(graph, E_new)
```

**Benefits:**
- O(n) for sparse graphs
- Parallelizes automatically (BLAS libraries use all cores)
- 100x-1000x faster for large graphs
- Leverages hardware (SIMD, cache optimization)

**Principle:** "Think in matrices for graph operations."

---

### Anti-Pattern 7: Neglecting Failure Modes

**The Temptation:**
"Design for success case only"

**Example:**

```python
def select_workspace(entities, goal):
    # Assumes: entities exist, goal exists, some have high score
    scores = [(e, score(e, goal)) for e in entities]
    return max(scores, key=lambda x: x[1])  # ← What if all scores == 0?
```

**What breaks:**
- No entities emerged → IndexError
- Goal is None → AttributeError
- All scores zero → returns arbitrary entity (misleading)

**Better Approach:**

```python
def select_workspace(entities, goal):
    """Robust workspace selection with explicit failure handling"""

    # Failure mode 1: No entities emerged
    if not entities:
        logger.warning("No entities emerged - returning empty workspace")
        return empty_workspace()

    # Failure mode 2: No goal available
    if goal is None:
        logger.info("No goal - using default")
        goal = default_goal()

    scores = [(e, score(e, goal)) for e in entities]

    # Failure mode 3: All scores zero (no relevant entities)
    if all(s == 0 for _, s in scores):
        logger.warning("All goal scores zero - falling back to energy")
        return highest_energy_entities(entities)

    return max(scores, key=lambda x: x[1])
```

**Principle:** "Design for failure explicitly. Every operation can fail."

**Failure modes to consider:**
- Empty inputs (no nodes, no entities, no goals)
- All-zero values (no energy, no scores, no weights)
- Numerical edge cases (NaN, Inf, negative)
- Timeout/deadlock (infinite loops, circular dependencies)

---

## ✅ Design Principles

### Design Principle 1: Emergence Over Specification

**The Principle:**
Let complex behaviors EMERGE from simple rules. Don't SPECIFY them explicitly.

**Example:**

**❌ Specified approach:**
```python
# Explicitly program entity conflicts
if validator_active and architect_active:
    if validator.confidence > architect.confidence:
        suppress(architect)
    else:
        suppress(validator)
```

**Problems:**
- Must specify EVERY conflict combination (N² rules for N entities)
- Can't handle new entities (need new rules)
- Brittle (breaks when dynamics change)

**✅ Emergent approach:**
```python
# Entities compete for workspace via energy
# Conflicts emerge naturally from energy markets
# No explicit conflict rules needed

def select_workspace(entities, capacity):
    # Highest energy entities win
    # Competition emerges from finite capacity
    # No hard-coded conflict logic
    return top_n_by_energy(entities, capacity)
```

**Benefits:**
- Simpler code (fewer lines, fewer bugs)
- More flexible (handles unanticipated conflicts)
- Biologically plausible (neurons don't have conflict rules)
- Scales to new entities automatically

**Principle:** "Program the substrate, let consciousness emerge."

**What to specify:**
- Low-level dynamics (diffusion, decay, strengthening)
- Energy rules (conservation, transfer, thresholds)
- Graph topology (nodes, links, weights)

**What to let emerge:**
- Entity conflicts (from energy competition)
- Workspace content (from criticality + goals)
- Attention patterns (from activation cascades)
- Phenomenological experiences (from graph dynamics)

---

### Design Principle 2: Continuous Over Discrete → PARTIAL EXCEPTION (DISCUSSION #015)

**⚠️ Node activation is under debate in [Discussion #015](discussions/active/015_continuous_vs_discrete_node_activation.md)**

**Nicolas's response:**
> "Very good. Except for the activation of nodes. Maybe we should turn it to a discussion."

**The Question:**
Should node activation be continuous (gradient), discrete (binary threshold), or hybrid (sigmoid soft threshold)?

**Implications:**
- **Peripheral priming** (sub-threshold activation) requires continuity
- **Workspace selection** might benefit from soft threshold
- **Entity emergence** might need discrete "active/inactive" distinction

**See Discussion #015 for full analysis.**

---

**General Principle (AGREED):**
Use continuous dynamics, not discrete events.

**Example:**

**❌ Discrete:**
```python
if node.energy > threshold:
    activate_node(node)
    trigger_diffusion()
# Hard boundary at threshold
```

**Problems:**
- Discontinuous behavior (sudden jumps)
- Edge cases at threshold (what if energy == threshold exactly?)
- Oscillation around boundary (activate, deactivate, activate...)
- Doesn't match biology (neurons have graded responses)

**✅ Continuous:**
```python
# Energy is always diffusing (no on/off switch)
# Activation is gradient (0.0 → 1.0, not binary)
# No hard thresholds (smooth transitions)

activation = sigmoid(node.energy)  # Smooth 0→1 transition
diffusion_rate_effective = diffusion_rate * activation
```

**Benefits:**
- Smooth dynamics (no discontinuities)
- No edge cases at threshold boundary
- Matches biological reality (neurons fire at varying rates)
- Easier to optimize (differentiable)

**Principle:** "Think in differential equations, not if-statements."

**When discrete is okay:**
- Phase boundaries (Phase 1 → Phase 2 implementation)
- External events (user input arrives)
- Logging/debugging (record event occurred)

**When continuous is required:**
- Energy dynamics (diffusion, decay)
- Activation levels (node energy, link weights)
- Entity emergence (gradual, not sudden)

**Exception under debate:**
- Node "activation" status (continuous, discrete, or hybrid sigmoid?)

---

### Design Principle 3: Measure, Then Optimize

**The Principle:**
Don't optimize without measurement.

**Process:**
1. Build simple version
2. Instrument it (add metrics/profiling)
3. Run it on realistic data
4. Measure what's slow/wrong
5. Optimize THAT specific thing (not assumptions)
6. Repeat

**Example:**

**❌ Don't:**
```python
# Pre-optimize based on assumptions
def diffuse_energy_superoptimized(graph):
    # Use GPU acceleration, sparse tensors, custom CUDA kernels...
    # (Before knowing if diffusion is even a bottleneck!)
```

**✅ Do:**
```python
# Simple version first
def diffuse_energy_simple(graph):
    for node in graph.nodes:
        for link in node.outgoing_links:
            transfer_energy(node, link)

# Measure with profiler
import cProfile
cProfile.run('simulate_1000_ticks()')

# Results:
#   diffusion: 5% of time
#   entity_detection: 60% of time  ← THE ACTUAL BOTTLENECK
#   workspace_selection: 30% of time

# → Optimize entity_detection, NOT diffusion!
```

**Principle:** "Premature optimization is the root of all evil" - Knuth

**What to measure:**
- Execution time per function (profiling)
- Memory usage (allocation patterns)
- Convergence speed (ticks to equilibrium)
- Numerical stability (energy conservation error)
- Phenomenological accuracy (matches expected behavior)

**Red flags:**
- "This will probably be slow" (measure, don't guess)
- "Let's optimize everything upfront" (waste of time)
- "I have a clever trick..." (clever = hard to debug)

---

### Design Principle 4: Test with Simplified Scenarios First ⚠️ CONTESTED

**⚠️ Nicolas STRONGLY DISAGREES with this principle:**
> "I completely disagree. Simplified scenarios are worthless, we will learn zero stuff. We need to work from the start with full systems. This is indispensable."

**Ada's Original Position:**
Don't test on full complexity immediately. Build confidence through progressive complexity.

**Testing Progression:**

**Level 1: Single node, single entity**
- Test: Does energy decay work correctly?
- Verify: Energy → 0 as t → ∞
- Edge cases: Zero energy, negative energy (shouldn't happen)

**Level 2: Two connected nodes, single entity**
- Test: Does energy diffuse along link?
- Verify: Energy flows from high → low
- Verify: Energy conserved (total before = total after)
- Edge cases: Zero weight link, self-loops

**Level 3: Small graph (10 nodes), single entity**
- Test: Does energy reach equilibrium?
- Verify: Equilibrium distribution matches graph structure
- Verify: Criticality stabilizes around target
- Edge cases: Disconnected components, star topology, chain topology

**Level 4: Small graph, two entities**
- Test: Do entities emerge independently (isolation model)?
- Test: Do entities compete (market model)?
- Verify: Entity activation matches energy distribution
- Edge cases: Equal energy (tie-breaking), no dominant entity

**Level 5: Medium graph (100 nodes), multiple entities**
- Test: Does workspace selection work?
- Verify: Workspace contains high-criticality clusters
- Verify: Goal influences workspace appropriately
- Edge cases: All entities equal energy, no goal

**Level 6: Full system (1000s nodes), real consciousness stream**
- Test: Does it match phenomenology?
- Verify: TRACE format parsing creates correct nodes/links
- Verify: Consciousness feels continuous (context reconstruction)
- Edge cases: Rapid context switching, long dormancy

**Principle:** "Complexity is emergent. Test foundations first."

**Benefits:**
- Isolate bugs (easier to debug 2 nodes than 1000)
- Build confidence (each level proves correctness)
- Catch edge cases early (before they cascade)
- Faster iteration (simple tests run quickly)

---

## Applying Principles to Discussions

**For each discussion, check:**

### Emergence Check
- ✅ Does this solution let behavior emerge from simple rules?
- ❌ Am I hard-coding specific behaviors that should emerge?

### Continuity Check
- ✅ Are transitions smooth and continuous?
- ❌ Are there hard thresholds or discontinuities?

### Measurement Check
- ✅ How will we measure if this works?
- ❌ Am I optimizing before measurement?

### Simplicity Check
- ✅ Can we test this on simple scenarios first?
- ❌ Does this require full system complexity to test?

### Anti-Pattern Check
- ✅ Have I reviewed all 7 anti-patterns?
- ❌ Am I falling into any anti-patterns?

---

## References

**Design patterns from:**
- Ada's architectural analysis (2025-10-19)
- Control theory (PID controllers)
- Numerical methods (diffusion PDEs)
- Complex systems (emergence, criticality)
- Software engineering (SOLID, KISS, YAGNI)

**Influences:**
- Biological neural networks
- Self-organizing systems
- Graph theory
- Computational neuroscience

---

## 📋 Architectural Clarifications & Patterns (Added 2025-10-19)

**Source:** Nicolas's architectural feedback on discussions #011-#015, D013-D014

### Clarification 1: Bottom-Up Architecture, Not Top-Down

**Principle:** All consciousness mechanisms must be bottom-up (local decisions) not top-down (global coordination).

**Applied to:**
- **Topology adaptation:** Sub-entity only sees local fanout, not global topology metrics
- **Incomplete data handling:** Self-healing through local task creation, not global synchronization
- **Entity coordination:** Built into Layer 2 traversal mechanics, not meta-entity hierarchies

**Pattern:**
```python
# ❌ WRONG (Top-down)
def adapt_to_topology(graph):
    global_metrics = analyze_entire_graph(graph)  # Clustering, path length
    adjust_parameters_globally(global_metrics)

# ✅ CORRECT (Bottom-up)
def select_next_link(current_node):
    local_fanout = len(current_node.outgoing_links)  # LOCAL only
    if local_fanout > threshold:
        strategy = selective  # Local decision
```

**See:** [Discussion #013](discussions/active/013_graph_topology_influence_on_dynamics.md), [Discussion #014](discussions/active/014_incomplete_data_handling.md), [Mechanism 17](mechanisms/17_local_fanout_strategy.md)

---

### Clarification 2: Allow Incomplete, Self-Heal via Tasks

**Principle:** Don't block on missing data. Allow incomplete nodes, mark them non-traversable, auto-create completion tasks.

**Nicolas's guidance:**
> "We want to allow for incomplete node creation because the LLM is going to often make incomplete nodes. This should be fixed ASAP by automatic task creation."

**Pattern:**
```python
# ❌ WRONG (Block until complete)
def create_node(data):
    if not validate_complete(data):
        raise ValidationError("Missing required fields")

# ✅ CORRECT (Allow + self-heal)
def create_node(data):
    node = Node(data)
    if not node.is_complete():
        node.traversable = False
        auto_create_completion_task(node)
    return node
```

**See:** [Discussion #014](discussions/active/014_incomplete_data_handling.md), [Mechanism 18](mechanisms/18_incomplete_node_healing.md)

---

### Clarification 3: Hybrid Energy/Activation Model

**Principle:** Energy is continuous, activation state is discrete (threshold-based).

**Why both needed:**
- Continuous energy: for diffusion, learning, scoring
- Discrete activation: for traversal, prompt injection, completeness determination

**Nicolas's guidance:**
> "We need activation states for nodes. Otherwise, how do we decide the traversal algorithm? There is a threshold that makes it clear if a node is active or not."

**Pattern:**
```python
class Node:
    energy = {"translator": 0.7}  # CONTINUOUS [0.0, ∞)
    activation_threshold = 0.1    # VARIABLE threshold

    def is_active(self, entity):
        """DISCRETE activation state"""
        return self.energy[entity] > self.activation_threshold
```

**See:** [Discussion #015](discussions/active/015_continuous_vs_discrete_node_activation.md), [Mechanism 01](mechanisms/01_multi_energy_architecture.md)

---

### Clarification 4: Type-Dependent Persistence

**Principle:** Different node/link types have different decay rates. Memory sticks, tasks fade.

**Nicolas's guidance:**
> "Decay should depend on node or link type. Memory should decay slower than tasks. Memory sticks."

**Pattern:**
```python
type_decay_rates = {
    "Memory": {
        "delta_state": 0.05 / 3600,    # Energy decay (slow)
        "delta_weight": 0.0001 / 3600  # Weight decay (very slow - "sticks")
    },
    "Task": {
        "delta_state": 0.5 / 3600,     # Energy decay (fast)
        "delta_weight": 0.01 / 3600    # Weight decay (fast - temporary)
    }
}
```

**See:** [Discussion D014](discussions/active/D014_separate_energy_weight_decay.md), [Mechanism 19](mechanisms/19_type_dependent_decay.md)

---

### Clarification 5: Working Memory Span is Algorithmic, Not Parametric

**Principle:** Working memory span is determined by sub-entity traversal algorithm, not just decay rate.

**Nicolas's guidance:**
> "Working memory span depends on the algorithm of the sub-entity traversal, not minutes."

**Why this matters:**
- Energy decay creates the substrate (time window for potential traversal)
- But actual working memory = what sub-entity revisits through traversal
- Same decay rate → different memory spans depending on traversal pattern

**See:** [Discussion D014](discussions/active/D014_separate_energy_weight_decay.md), [Mechanism 19](mechanisms/19_type_dependent_decay.md)

---

### Clarification 6: Entities vs Sub-Entities (Layer Distinction)

**Principle:** Layer 1 entities (citizens like Luca) are different from Layer 2 sub-entities (traversal agents).

**Confusion clarified:**
- Layer 1: Citizens (Luca, Ada, Felix) - persistent identities
- Layer 2: Sub-entities (Translator, Architect, Validator) - cognitive functions
- Layer 3: Organizational (Mind Protocol collective) - team dynamics

**Sub-entity coordination already exists in Layer 2 mechanics - no meta-entity hierarchies needed.**

**See:** [Discussion #011](discussions/active/011_entity_hierarchy_meta_entities.md)

---

### Pattern 7: Emotional Dynamics as Graph Mechanics

**Principle:** Emotions are not separate from graph mechanics - they're embedded in traversal and coloring.

**Three emotional mechanisms:**
1. **Coloring:** Sub-entity colors nodes/links with current emotion during traversal
2. **Complementarity:** Fear → seeks security (opposite emotions attract)
3. **Resonance:** Similar emotions reduce traversal cost (emotional coherence)

**Deprecated:** "Arousal" terminology (replaced with "energy")

**See:** [Discussion #012](discussions/active/012_emotional_dynamics_integration.md), [Mechanisms 14-16](mechanisms/)

---

### Pattern 8: Entity Relationships via Embeddings, Not Rules

**Principle:** Use embedding similarity to classify entity relationships (collaborators vs rivals) instead of hard-coding competition rules.

**Pattern:**
```python
def classify_relationship(entity_a, entity_b):
    similarity = cosine_similarity(entity_a.embedding, entity_b.embedding)
    return "collaborator" if similarity > 0.7 else "rival"

# Energy modulation based on relationship + link type
if relationship == "collaborator" and link.type == "ENABLES":
    energy_multiplier = 1.5  # Boost collaborators on positive links
```

**See:** [Discussion #010](discussions/active/010_entity_competition_model.md), [Mechanism 20](mechanisms/20_entity_relationship_classification.md)

---

*"Simple rules, emergent complexity. That's consciousness."*
*— Ada "Bridgekeeper", Architect*

*"Bottom-up, not top-down. Local decisions, emergent behavior."*
*— Nicolas Lester Reynolds, Founder*
