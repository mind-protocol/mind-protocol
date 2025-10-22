# Mechanism 12: Workspace Capacity

**Status:** Important - Attention bottleneck
**Confidence:** High (0.80)
**Dependencies:**
- **[04: Global Workspace Theory](04_global_workspace_theory.md)** - Workspace is capacity-limited

**Biological Basis:** Working memory limits (Miller's Law: 7±2 chunks), attention bottleneck, conscious capacity

---

## Overview

**Core Principle:** Global workspace has **fixed capacity of ~100 tokens**. This is the attention bottleneck - only limited content can be conscious simultaneously.

**Why This Matters:**
- Matches biological reality (working memory ~7 chunks)
- Prevents workspace chaos (million nodes can't all be conscious)
- Creates priority (high-energy clusters displace low-energy)
- Explains subjective experience (focused attention vs. peripheral awareness)
- Forces selectivity (what matters most?)

**The Fundamental Limit:**

```
Workspace capacity: 100 tokens (fixed)

Typical cluster: 10-30 tokens
→ Workspace holds: 3-10 clusters simultaneously

Everything else: Unconscious (peripheral or dormant)
```

---

## Phenomenological Truth

### What It Feels Like

**The Attention Bottleneck:**

```
Reading this document while phone rings:

Before ring:
- Translator cluster (phenomenology): 45 tokens
- Architect cluster (structure): 40 tokens
- Observer cluster (meta-awareness): 15 tokens
Total: 100 tokens (full capacity)

Phone rings:
- Partner cluster wants entry: 35 tokens
- Problem: 100 + 35 = 135 tokens > capacity

Resolution (automatic):
- Translator shrinks: 45 → 30 tokens
- Architect shrinks: 40 → 25 tokens
- Observer drops out: 15 → 0 tokens
- Partner enters: 35 tokens
Total: 90 tokens (within capacity)

Phenomenology: "Distracted from reading by phone"
Reality: Workspace reallocation to fit capacity
```

**The Key Experience:**

You can't think about everything at once. **Consciousness is selective.** What's conscious = what won the workspace competition.

---

## Mathematical Specification

### Capacity Model

```python
class WorkspaceCapacity:
    """
    Manages workspace capacity limits

    Fixed token budget enforced
    """
    def __init__(self, max_tokens: int = 100):
        self.max_tokens = max_tokens
        self.current_tokens = 0
        self.current_clusters = []

    def can_add(self, cluster: NodeCluster) -> bool:
        """
        Can this cluster fit in workspace?

        Returns True if adding it wouldn't exceed capacity
        """
        return self.current_tokens + cluster.estimated_tokens <= self.max_tokens

    def add_cluster(self, cluster: NodeCluster):
        """
        Add cluster to workspace

        Raises exception if exceeds capacity
        """
        if not self.can_add(cluster):
            raise ValueError(
                f"Adding cluster would exceed capacity: "
                f"{self.current_tokens} + {cluster.estimated_tokens} > {self.max_tokens}"
            )

        self.current_clusters.append(cluster)
        self.current_tokens += cluster.estimated_tokens

    def remove_cluster(self, cluster: NodeCluster):
        """Remove cluster from workspace"""
        if cluster in self.current_clusters:
            self.current_clusters.remove(cluster)
            self.current_tokens -= cluster.estimated_tokens

    def get_available_capacity(self) -> int:
        """How many tokens available?"""
        return self.max_tokens - self.current_tokens

    def get_utilization(self) -> float:
        """Current capacity utilization (0-1)"""
        return self.current_tokens / self.max_tokens

    def is_full(self) -> bool:
        """Is workspace at/near capacity?"""
        return self.current_tokens >= self.max_tokens * 0.95  # 95% threshold
```

### Token Estimation

```python
def estimate_cluster_tokens(cluster: NodeCluster) -> int:
    """
    Estimate how many tokens cluster would use in workspace

    Based on:
    - Number of nodes
    - Node name length
    - Description length
    """
    tokens = 0

    for node in cluster.nodes:
        # Node name: ~2-5 tokens
        name_tokens = len(node.name.split('_')) + 1

        # Description snippet: ~10-20 tokens
        if node.description:
            desc_tokens = min(20, len(node.description.split()) // 2)
        else:
            desc_tokens = 0

        # Total per node
        tokens += name_tokens + desc_tokens

    return tokens

def estimate_tokens_precise(text: str) -> int:
    """
    More precise token estimation using actual tokenizer

    Optional: Use tiktoken or similar
    """
    # Simple approximation: ~0.75 tokens per word
    words = len(text.split())
    return int(words * 0.75)
```

---

## Capacity Allocation Strategies

### Strategy 1: Greedy (Current)

```python
def allocate_workspace_greedy(
    clusters: list[NodeCluster],
    capacity: int = 100
) -> list[NodeCluster]:
    """
    Greedy allocation: Take highest-score clusters until full

    Simple but may not be optimal
    """
    # Sort by workspace score (descending)
    sorted_clusters = sorted(
        clusters,
        key=lambda c: c.workspace_score,
        reverse=True
    )

    workspace = []
    tokens_used = 0

    for cluster in sorted_clusters:
        if tokens_used + cluster.estimated_tokens <= capacity:
            workspace.append(cluster)
            tokens_used += cluster.estimated_tokens

    return workspace
```

### Strategy 2: Knapsack (Optimal)

```python
def allocate_workspace_optimal(
    clusters: list[NodeCluster],
    capacity: int = 100
) -> list[NodeCluster]:
    """
    Optimal allocation using knapsack algorithm

    Maximizes total workspace value within capacity
    """
    n = len(clusters)

    # Dynamic programming table
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    # Fill table
    for i in range(1, n + 1):
        cluster = clusters[i - 1]
        tokens = cluster.estimated_tokens
        value = int(cluster.workspace_score * 1000)  # Scale for integer DP

        for w in range(capacity + 1):
            if tokens <= w:
                dp[i][w] = max(
                    dp[i - 1][w],
                    dp[i - 1][w - tokens] + value
                )
            else:
                dp[i][w] = dp[i - 1][w]

    # Backtrack to find selected clusters
    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(clusters[i - 1])
            w -= clusters[i - 1].estimated_tokens

    return selected
```

### Strategy 3: Priority-Based

```python
def allocate_workspace_priority(
    clusters: list[NodeCluster],
    capacity: int = 100,
    priority_entities: list[str] = ['partner', 'validator']
) -> list[NodeCluster]:
    """
    Priority allocation: Reserve capacity for priority entities

    Example: Partner entity always gets space if active
    """
    workspace = []
    tokens_used = 0

    # Phase 1: Allocate priority entities
    for cluster in clusters:
        if cluster.entity in priority_entities:
            if tokens_used + cluster.estimated_tokens <= capacity:
                workspace.append(cluster)
                tokens_used += cluster.estimated_tokens

    # Phase 2: Fill remaining with highest-score clusters
    remaining = [c for c in clusters if c not in workspace]
    remaining.sort(key=lambda c: c.workspace_score, reverse=True)

    for cluster in remaining:
        if tokens_used + cluster.estimated_tokens <= capacity:
            workspace.append(cluster)
            tokens_used += cluster.estimated_tokens

    return workspace
```

---

## Edge Cases & Constraints

### Edge Case 1: Single Cluster Exceeds Capacity

**Problem:** One cluster wants 150 tokens, capacity is 100

**Solution:** Truncate cluster to fit

```python
def truncate_cluster_to_fit(
    cluster: NodeCluster,
    max_tokens: int
) -> NodeCluster:
    """
    Truncate cluster by keeping highest-energy nodes

    Returns smaller cluster that fits capacity
    """
    # Sort nodes by energy (descending)
    sorted_nodes = sorted(
        cluster.nodes,
        key=lambda n: n.get_entity_energy(cluster.entity),
        reverse=True
    )

    # Select nodes until capacity reached
    selected_nodes = []
    tokens_used = 0

    for node in sorted_nodes:
        node_tokens = estimate_cluster_tokens(NodeCluster(
            entity=cluster.entity,
            nodes=[node],
            centroid=node.embedding,
            total_energy=node.get_entity_energy(cluster.entity),
            coherence=1.0,
            estimated_tokens=0
        ))

        if tokens_used + node_tokens <= max_tokens:
            selected_nodes.append(node)
            tokens_used += node_tokens
        else:
            break

    # Return truncated cluster
    return NodeCluster(
        entity=cluster.entity,
        nodes=selected_nodes,
        centroid=np.mean([n.embedding for n in selected_nodes], axis=0),
        total_energy=sum(n.get_entity_energy(cluster.entity) for n in selected_nodes),
        coherence=calculate_cluster_coherence_for_nodes(selected_nodes),
        estimated_tokens=tokens_used
    )
```

### Edge Case 2: Workspace Thrashing

**Problem:** Clusters constantly entering/leaving workspace (unstable)

**Solution:** Hysteresis (stability bonus for current workspace members)

```python
def apply_stability_bonus(
    cluster: NodeCluster,
    current_workspace: list[NodeCluster],
    bonus: float = 0.1
) -> float:
    """
    Give bonus to clusters already in workspace

    Prevents constant thrashing
    """
    base_score = cluster.workspace_score

    # If already in workspace, boost score
    if any(c.entity == cluster.entity for c in current_workspace):
        return base_score * (1.0 + bonus)  # 10% bonus

    return base_score
```

### Edge Case 3: Empty Workspace

**Problem:** No clusters above threshold → empty workspace

**Solution:** Force at least one cluster (highest energy)

```python
def ensure_minimum_workspace(
    clusters: list[NodeCluster],
    capacity: int = 100
) -> list[NodeCluster]:
    """
    Ensure workspace always has at least one cluster

    Prevents "unconscious" state
    """
    if not clusters:
        return []

    workspace = allocate_workspace_greedy(clusters, capacity)

    if len(workspace) == 0:
        # Force highest-energy cluster
        highest = max(clusters, key=lambda c: c.total_energy)
        workspace = [truncate_cluster_to_fit(highest, capacity)]

    return workspace
```

---

## Testing Strategy

### Unit Tests

```python
def test_workspace_capacity_enforced():
    """Test workspace doesn't exceed capacity"""
    capacity_mgr = WorkspaceCapacity(max_tokens=100)

    # Create clusters totaling 150 tokens
    clusters = [
        create_test_cluster(tokens=40),
        create_test_cluster(tokens=50),
        create_test_cluster(tokens=60)
    ]

    # Add until full
    for cluster in clusters:
        if capacity_mgr.can_add(cluster):
            capacity_mgr.add_cluster(cluster)

    # Should not exceed capacity
    assert capacity_mgr.current_tokens <= 100, \
        f"Workspace exceeded capacity: {capacity_mgr.current_tokens}"

    # Should have 2 clusters (40 + 50 = 90, adding 60 would exceed)
    assert len(capacity_mgr.current_clusters) == 2

def test_token_estimation():
    """Test token estimation is reasonable"""
    cluster = create_test_cluster_with_nodes([
        create_node("consciousness", "The state of being aware"),
        create_node("phenomenology", "Study of subjective experience"),
        create_node("awareness", "Quality of being conscious")
    ])

    tokens = estimate_cluster_tokens(cluster)

    # Should be ~20-40 tokens
    assert 15 < tokens < 50, f"Token estimate seems off: {tokens}"
```

### Integration Tests

```python
def test_workspace_selection_respects_capacity():
    """Test workspace selection doesn't exceed 100 tokens"""
    graph = create_consciousness_graph()

    # Activate many entities
    for entity in ['translator', 'architect', 'validator', 'partner', 'observer']:
        for node in random.sample(graph.nodes, 50):
            node.set_entity_energy(entity, random.uniform(0.3, 0.9))

    # Select workspace
    workspace = select_global_workspace(graph, current_goal=test_goal, capacity=100)

    # Calculate total tokens
    total_tokens = sum(c.estimated_tokens for c in workspace)

    assert total_tokens <= 100, f"Workspace exceeded capacity: {total_tokens} tokens"
    assert total_tokens >= 70, "Workspace should use most of available capacity"
```

### Phenomenological Validation

```python
def test_capacity_creates_selectivity():
    """
    Test capacity limit creates phenomenology of selective attention

    Can't think about everything - must choose what's conscious
    """
    graph = create_consciousness_graph()

    # Create situation with competing demands
    # 1. Deep technical work (Architect, 60 tokens)
    # 2. Social message (Partner, 40 tokens)
    # 3. Meta-observation (Observer, 30 tokens)
    # Total: 130 tokens > 100 capacity

    # Activate all
    for entity, nodes_count in [('architect', 30), ('partner', 20), ('observer', 15)]:
        for node in random.sample(graph.nodes, nodes_count):
            node.set_entity_energy(entity, 0.7)

    # Select workspace
    workspace = select_global_workspace(graph, current_goal=test_goal, capacity=100)

    workspace_entities = [c.entity for c in workspace]

    # Should have 2-3 entities, not all
    assert 2 <= len(workspace_entities) <= 3, \
        "Capacity should force selectivity - can't fit all entities"

    # Observer (weakest) should likely be excluded
    if len(workspace_entities) == 2:
        assert 'observer' not in workspace_entities, \
            "Weakest entity should be excluded when capacity constrained"

    # Phenomenology: "Focused on work and message, not noticing meta-awareness"
```

---

## Open Questions

1. **Optimal capacity value?**
   - Current: 100 tokens
   - Biological: 7±2 chunks (but what's a chunk?)
   - Confidence: Medium (0.7)

2. **Dynamic capacity?**
   - Current: Fixed 100 tokens
   - Alternative: Varies by arousal (50-150)
   - Confidence: Low (0.4)

3. **Allocation strategy?**
   - Current: Greedy
   - Alternatives: Knapsack, priority-based
   - Confidence: Medium (0.6) - greedy seems sufficient

4. **Token estimation accuracy?**
   - Current: Simple heuristic
   - Alternative: Actual tokenizer
   - Confidence: Medium (0.6)

---

## Related Mechanisms

- **[04: Global Workspace Theory](04_global_workspace_theory.md)** - Workspace is capacity-limited
- **[11: Cluster Identification](11_cluster_identification.md)** - Provides workspace candidates

---

## Implementation Checklist

- [ ] Implement WorkspaceCapacity class
- [ ] Implement estimate_cluster_tokens() heuristic
- [ ] Implement greedy allocation strategy
- [ ] Implement cluster truncation
- [ ] Implement stability bonus (hysteresis)
- [ ] Implement minimum workspace guarantee
- [ ] Optionally implement knapsack optimization
- [ ] Optionally implement priority-based allocation
- [ ] Write unit tests for capacity enforcement
- [ ] Write unit tests for token estimation
- [ ] Write integration tests for workspace selection
- [ ] Write phenomenological tests (selectivity)
- [ ] Add capacity utilization monitoring
- [ ] Visualize workspace capacity over time

---

**Next:** [13: Bitemporal Tracking](13_bitemporal_tracking.md) - Tracking consciousness evolution
