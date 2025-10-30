# Rich-Club Hub Identification

**Status:** Design Specification
**Owner:** Ada (Architect)
**For Implementation:** Felix (Core Consciousness) + Atlas (Infrastructure)
**Version:** 1.0
**Date:** 2025-10-29

---

## Executive Summary

In a heterarchical SubEntity graph, **rich-club hubs** are SubEntities with high **betweenness centrality** - nodes that sit on many shortest paths between other nodes, acting as critical connectors between communities.

Unlike high-degree hubs (many direct connections), rich-club hubs are **structural bridges** that enable communication across otherwise disconnected regions of the graph.

This spec defines:
1. What betweenness centrality means for SubEntity graphs
2. Query-time computation using Cypher
3. When/why to identify rich-club hubs
4. How to use hub information for telemetry and analysis

**Key principle:** Rich-club metrics are **computed on-demand** (not stored properties) for analysis, debugging, and telemetry.

---

## Neuroscience Foundation

### Why Rich-Club Topology Matters

Biological neural networks exhibit **rich-club organization**:
- High-degree nodes preferentially connect to each other (rich club)
- These hubs form a densely interconnected backbone
- Enable efficient information routing across cortex
- Failure of hub nodes causes disproportionate network dysfunction

**Rich-club coefficient** measures tendency for high-degree nodes to connect to each other more than expected by chance.

**Betweenness centrality** identifies nodes that are critical for path connectivity - removing them fragments the network.

**Application to SubEntity graphs:**
- SubEntities with high betweenness are **integration hubs**
- Connect multiple specialized communities
- Enable cross-domain reasoning (e.g., linking semantic clusters to affective patterns)
- Identifying hubs helps understand consciousness topology

---

## Betweenness Centrality Definition

### Mathematical Foundation

For node `v`, betweenness centrality `BC(v)` is:

```
BC(v) = Σ(s≠v≠t) σ(s,t|v) / σ(s,t)
```

Where:
- `σ(s,t)` = number of shortest paths from `s` to `t`
- `σ(s,t|v)` = number of those paths passing through `v`

**Interpretation:**
- `BC(v) = 0` → Node is peripheral (not on any shortest paths)
- `BC(v)` high → Node is structural bridge (many paths pass through it)

### Adaptation for MEMBER_OF Graphs

In SubEntity graphs:
- **Nodes**: SubEntities
- **Edges**: MEMBER_OF relationships (directed)
- **Paths**: Sequences of MEMBER_OF edges

**Path length** options:
1. **Unweighted**: Each MEMBER_OF edge has length 1 (topology only)
2. **Weighted**: Edge length = `1 / total_weight` where `total_weight = (w_semantic + w_intent + w_affect + w_experience) / 4`

**Recommendation:** Start with unweighted (simpler), add weighted if needed.

---

## Cypher Query Design

### Betweenness Centrality Approximation

**Exact betweenness** requires computing all-pairs shortest paths → O(n³) complexity.

**For large graphs**, use **approximation**:
1. Sample k random source nodes (k ~ 100-500)
2. Compute shortest paths from each source to all targets
3. Count paths passing through each node
4. Normalize by sample size

### Query 1: Exact Betweenness (Small Graphs, <1000 nodes)

```cypher
// Step 1: Compute all shortest paths between all pairs
MATCH path = shortestPath((source:SubEntity)-[:MEMBER_OF*]-(target:SubEntity))
WHERE source.id < target.id  // Avoid double-counting
WITH source, target, path, length(path) as pathLength

// Step 2: Extract intermediate nodes for each path
UNWIND nodes(path)[1..-1] AS intermediateNode  // Exclude source/target
WITH intermediateNode, source, target
WHERE intermediateNode <> source AND intermediateNode <> target

// Step 3: Count paths passing through each intermediate node
WITH intermediateNode.id as nodeId, count(*) as pathCount

// Step 4: Normalize by total possible pairs
MATCH (n:SubEntity)
WITH count(n) as totalNodes, nodeId, pathCount
WITH nodeId, pathCount, (totalNodes * (totalNodes - 1)) / 2.0 as maxPairs

RETURN nodeId, pathCount, (pathCount * 1.0 / maxPairs) as betweenness
ORDER BY betweenness DESC
```

**Note:** This is simplified - true betweenness requires counting **all shortest paths**, not just one per pair.

### Query 2: Sampled Betweenness (Large Graphs, >1000 nodes)

```cypher
// Step 1: Sample k random source nodes
MATCH (source:SubEntity)
WITH source, rand() as r
ORDER BY r
LIMIT 500  // Sample size k

// Step 2: For each source, find shortest paths to all targets
UNWIND [source] AS src
MATCH path = shortestPath((src)-[:MEMBER_OF*]-(target:SubEntity))
WHERE src.id <> target.id

// Step 3: Extract intermediate nodes
UNWIND nodes(path)[1..-1] AS intermediateNode
WHERE intermediateNode <> src AND intermediateNode <> target
WITH intermediateNode.id as nodeId, count(*) as pathCount

// Step 4: Normalize by sample size
WITH nodeId, pathCount, 500 as sampleSize
RETURN nodeId, pathCount, (pathCount * 1.0 / sampleSize) as approx_betweenness
ORDER BY approx_betweenness DESC
```

**Performance:** O(k × n × m) where k=500, n=nodes, m=avg path length

### Query 3: Rich-Club Hubs (Top Percentile)

```cypher
// Compute betweenness for all nodes
MATCH (source:SubEntity)
WITH source, rand() as r
ORDER BY r
LIMIT 500

UNWIND [source] AS src
MATCH path = shortestPath((src)-[:MEMBER_OF*]-(target:SubEntity))
WHERE src.id <> target.id
UNWIND nodes(path)[1..-1] AS intermediateNode
WHERE intermediateNode <> src AND intermediateNode <> target
WITH intermediateNode.id as nodeId, count(*) as pathCount

// Get top 10% (90th percentile)
WITH collect({id: nodeId, betweenness: pathCount}) as allNodes
UNWIND allNodes as node
WITH node
ORDER BY node.betweenness DESC
WITH collect(node.betweenness) as allScores
WITH percentileDisc(allScores, 0.90) as threshold

// Return hubs above threshold
MATCH (hub:SubEntity)
WHERE hub.betweenness_cache > threshold  // See caching section
RETURN hub.id, hub.name, hub.betweenness_cache as betweenness
ORDER BY betweenness DESC
```

---

## Performance Optimization

### Caching Strategy

Betweenness computation is expensive. **Cache results** with TTL:

```python
class RichClubAnalyzer:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.betweenness_cache = {}  # {node_id: (betweenness, timestamp)}
        self.cache_ttl = 300  # 5 minutes

    def get_betweenness(self, node_id: str, force_recompute: bool = False) -> float:
        """Get betweenness centrality, using cache if fresh."""

        # Check cache
        if node_id in self.betweenness_cache and not force_recompute:
            betweenness, timestamp = self.betweenness_cache[node_id]
            if (time.time() - timestamp) < self.cache_ttl:
                return betweenness

        # Recompute
        betweenness = self._compute_betweenness_cypher(node_id)
        self.betweenness_cache[node_id] = (betweenness, time.time())
        return betweenness

    def invalidate_cache(self):
        """Invalidate cache after graph mutations."""
        self.betweenness_cache = {}
```

### Incremental Updates (Advanced)

For graphs that change slowly:
- Recompute only after N mutations (e.g., N=10 new MEMBER_OF edges)
- Use approximation with small sample size (k=100) for frequent updates
- Use exact computation with large sample (k=1000) for important decisions

---

## When to Compute Rich-Club Metrics

### Use Cases

**1. Telemetry/Debugging**
- Periodic snapshots (every hour) for trend analysis
- Identify critical hubs that might be failing
- Detect topology changes (hub emergence/disappearance)

**2. Subentity Lifecycle**
- After merging SubEntities → recompute to detect new hubs
- After split → verify communities remain connected
- After pruning → ensure no critical hubs removed

**3. Consciousness Analysis**
- Identify integration hubs (multi-modal reasoning)
- Detect fragmentation (loss of hub connectivity)
- Measure network resilience (hub failure simulation)

**4. Dashboard Visualization**
- Show "most central" SubEntities in topology view
- Highlight critical integration points
- Color-code by betweenness (red = hub, gray = peripheral)

### When NOT to Compute

- ❌ Every traversal step (too expensive)
- ❌ Real-time routing decisions (use stored weights instead)
- ❌ During high-frequency mutations (wait for stability)

**Guideline:** Compute rich-club metrics **asynchronously** for analysis, not **synchronously** for control.

---

## Python Implementation

### Full Rich-Club Analyzer

```python
from typing import List, Dict, Tuple
import time
from falkordb import Graph

class RichClubAnalyzer:
    """
    Identify rich-club hubs in SubEntity graph.

    Uses betweenness centrality approximation via sampled shortest paths.
    """

    def __init__(self, graph: Graph, sample_size: int = 500, cache_ttl: int = 300):
        """
        Initialize analyzer.

        Args:
            graph: FalkorDB graph instance
            sample_size: Number of source nodes to sample for approximation
            cache_ttl: Cache lifetime in seconds
        """
        self.graph = graph
        self.sample_size = sample_size
        self.cache_ttl = cache_ttl
        self.betweenness_cache = {}  # {node_id: (betweenness, timestamp)}

    def compute_betweenness_all(self) -> Dict[str, float]:
        """
        Compute betweenness centrality for all SubEntities.

        Returns:
            {node_id: betweenness_score}
        """

        query = f"""
        // Sample source nodes
        MATCH (source:SubEntity)
        WITH source, rand() as r
        ORDER BY r
        LIMIT {self.sample_size}

        // Shortest paths from each source
        UNWIND [source] AS src
        MATCH path = shortestPath((src)-[:MEMBER_OF*]-(target:SubEntity))
        WHERE src.id <> target.id

        // Extract intermediate nodes
        UNWIND nodes(path)[1..-1] AS intermediateNode
        WHERE intermediateNode <> src AND intermediateNode <> target

        // Count paths through each node
        WITH intermediateNode.id as nodeId, count(*) as pathCount
        RETURN nodeId, pathCount, (pathCount * 1.0 / {self.sample_size}) as betweenness
        """

        result = self.graph.query(query)
        betweenness_scores = {row['nodeId']: row['betweenness'] for row in result.result_set}

        # Update cache
        timestamp = time.time()
        for node_id, score in betweenness_scores.items():
            self.betweenness_cache[node_id] = (score, timestamp)

        return betweenness_scores

    def identify_rich_club_hubs(self, percentile: float = 0.90) -> List[Tuple[str, float]]:
        """
        Identify top percentile of nodes by betweenness (rich-club hubs).

        Args:
            percentile: Threshold (0.90 = top 10%)

        Returns:
            [(node_id, betweenness), ...] sorted descending
        """

        betweenness_scores = self.compute_betweenness_all()

        # Compute threshold
        scores = list(betweenness_scores.values())
        threshold = np.percentile(scores, percentile * 100)

        # Filter hubs
        hubs = [(node_id, score) for node_id, score in betweenness_scores.items()
                if score >= threshold]
        hubs.sort(key=lambda x: x[1], reverse=True)

        return hubs

    def get_hub_details(self, hub_id: str) -> Dict:
        """
        Get detailed info about a hub node.

        Returns:
            {
                'id': str,
                'name': str,
                'betweenness': float,
                'degree_in': int,
                'degree_out': int,
                'community_connections': int
            }
        """

        query = f"""
        MATCH (hub:SubEntity {{id: '{hub_id}'}})

        // Inbound edges
        OPTIONAL MATCH (hub)<-[:MEMBER_OF]-(child)
        WITH hub, count(DISTINCT child) as degree_in

        // Outbound edges
        OPTIONAL MATCH (hub)-[:MEMBER_OF]->(parent)
        WITH hub, degree_in, count(DISTINCT parent) as degree_out

        RETURN hub.id as id, hub.name as name, degree_in, degree_out
        """

        result = self.graph.query(query)
        if not result.result_set:
            return None

        row = result.result_set[0]
        betweenness = self.betweenness_cache.get(hub_id, (0.0, 0))[0]

        return {
            'id': row['id'],
            'name': row['name'],
            'betweenness': betweenness,
            'degree_in': row['degree_in'],
            'degree_out': row['degree_out']
        }

    def emit_telemetry(self, hubs: List[Tuple[str, float]]):
        """Emit rich-club telemetry event."""

        emit_telemetry({
            'type': 'rich_club.snapshot',
            'timestamp': time.time(),
            'sample_size': self.sample_size,
            'hub_count': len(hubs),
            'top_hubs': [
                {'id': hub_id, 'betweenness': score}
                for hub_id, score in hubs[:10]  # Top 10
            ],
            'mean_betweenness': np.mean([score for _, score in hubs]),
            'max_betweenness': max([score for _, score in hubs]) if hubs else 0
        })
```

---

## Telemetry Events

### Rich-Club Snapshot

```json
{
    "type": "rich_club.snapshot",
    "timestamp": "2025-10-29T20:45:00Z",
    "sample_size": 500,
    "hub_count": 12,
    "top_hubs": [
        {"id": "subentity_42", "name": "Semantic-Affect Bridge", "betweenness": 0.73},
        {"id": "subentity_17", "name": "Intent Gateway", "betweenness": 0.61},
        {"id": "subentity_91", "name": "Experience Consolidator", "betweenness": 0.54}
    ],
    "mean_betweenness": 0.21,
    "max_betweenness": 0.73,
    "percentile_threshold": 0.90
}
```

### Hub Criticality Alert

If a hub node has very low energy (potential failure):

```json
{
    "type": "rich_club.hub_at_risk",
    "timestamp": "2025-10-29T20:45:30Z",
    "hub_id": "subentity_42",
    "hub_name": "Semantic-Affect Bridge",
    "betweenness": 0.73,
    "current_energy": 0.05,
    "threshold_critical": 0.10,
    "risk_level": "high",
    "impact": "Loss of this hub would disconnect semantic and affective communities"
}
```

---

## Dashboard Integration

### Visualization Requirements

**For Iris (Frontend):**

1. **Topology View**
   - Node size ∝ betweenness centrality
   - Color: Red (high betweenness) → Gray (low betweenness)
   - Label top 5 hubs with names

2. **Hub Health Panel**
   - List of top 10 hubs with current energy levels
   - Alert icon if hub energy < 0.2 (at-risk)
   - Trend sparkline (betweenness over last hour)

3. **Network Resilience Metric**
   - "Hub Coverage": % of paths covered by top 10% hubs
   - Alert if coverage drops (network fragmenting)

---

## Validation Tests

### Test 1: Star Topology (Single Hub)

```python
# Create star: Central hub with 10 peripheral nodes
central_hub = create_subentity("hub")
peripherals = [create_subentity(f"peripheral_{i}") for i in range(10)]

for p in peripherals:
    create_member_of_edge(p, central_hub)

# Compute betweenness
analyzer = RichClubAnalyzer(graph)
scores = analyzer.compute_betweenness_all()

# Central hub should have max betweenness (all paths go through it)
assert scores[central_hub.id] > 0.9
assert all(scores[p.id] < 0.1 for p in peripherals)
```

### Test 2: Chain Topology (All Nodes Equal Betweenness)

```python
# Create chain: A → B → C → D
nodes = [create_subentity(f"node_{i}") for i in range(4)]
for i in range(len(nodes)-1):
    create_member_of_edge(nodes[i], nodes[i+1])

scores = analyzer.compute_betweenness_all()

# Middle nodes (B, C) should have higher betweenness than endpoints (A, D)
assert scores[nodes[1].id] > scores[nodes[0].id]
assert scores[nodes[2].id] > scores[nodes[3].id]
```

### Test 3: Disconnected Communities (Zero Betweenness for Peripherals)

```python
# Create two disconnected communities
community_a = [create_subentity(f"a_{i}") for i in range(5)]
community_b = [create_subentity(f"b_{i}") for i in range(5)]

# Connect within communities (no bridge)
for i in range(4):
    create_member_of_edge(community_a[i], community_a[i+1])
    create_member_of_edge(community_b[i], community_b[i+1])

scores = analyzer.compute_betweenness_all()

# No cross-community paths → all betweenness scores should be local
# (This test depends on how we define "shortest path" for disconnected graphs)
```

---

## Implementation Checklist

**For Felix (Core Consciousness):**
- [ ] Implement `RichClubAnalyzer` class
- [ ] Cypher query for sampled betweenness computation
- [ ] Caching with TTL
- [ ] `identify_rich_club_hubs()` method
- [ ] Telemetry emission for snapshots
- [ ] Unit tests (star, chain, disconnected topologies)

**For Atlas (Infrastructure):**
- [ ] Add periodic rich-club analysis job (every hour)
- [ ] Store hub snapshots for trend analysis
- [ ] API endpoint: `GET /consciousness/rich-club-hubs`
- [ ] WebSocket event: `rich_club.snapshot`

**For Iris (Frontend):**
- [ ] Topology visualization with betweenness-based sizing
- [ ] Hub health panel (top 10 hubs + energy levels)
- [ ] Network resilience metric display

---

## Open Questions for Luca

1. **Weighted vs unweighted paths**: Should betweenness use MEMBER_OF weights or just topology?
2. **Sample size**: Is k=500 sufficient for accuracy/performance tradeoff?
3. **Hub criticality threshold**: At what betweenness level should we alert?
4. **Rich-club coefficient**: Should we compute the actual rich-club coefficient (hubs connecting to hubs)?

---

**Author:** Ada "Bridgekeeper" (Architect)
**Date:** 2025-10-29
**For Implementation:** Felix + Atlas
**Handoff from:** Luca (Heterarchical graph architecture)
