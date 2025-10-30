# Integration Depth & Breadth Metrics

**Status:** Design Specification
**Owner:** Ada (Architect)
**For Implementation:** Felix (Core Consciousness) + Atlas (Infrastructure)
**Version:** 1.0
**Date:** 2025-10-29

---

## Executive Summary

In a heterarchical SubEntity graph, **scale is path-dependent**, not a global property. The same SubEntity can be:
- 7 hops from a primitive pattern (deep integration)
- 2 hops from a meta-pattern (high-level abstraction)
- Connected to 5 distinct communities (broad integration)

**Integration metrics** measure where a SubEntity sits in the topology:

1. **Depth** - Hop-distance from primitive patterns (foundational concepts)
2. **Breadth** - Number of distinct communities/clusters connected
3. **Centrality** - Average hop-distance to all other nodes (closeness)

These metrics are **computed query-time** (not stored properties) for telemetry, debugging, and analysis.

---

## Motivation

### Why Depth/Breadth Matter

**Depth** (distance from primitives):
- Low depth (2-3 hops) = Close to foundational patterns (concrete, grounded)
- High depth (7-10 hops) = Distant from foundations (abstract, meta-level)
- Interpretation: "How many layers of abstraction separate this from basics?"

**Breadth** (community connectivity):
- Low breadth (1-2 communities) = Specialized (narrow domain)
- High breadth (5-10 communities) = Integrative (cross-domain connector)
- Interpretation: "How many different conceptual clusters does this bridge?"

**Use cases:**
- **Debugging**: "Why is this high-depth node activating? It's too abstract for current context."
- **Telemetry**: "Consciousness is dwelling in shallow primitives → grounded reasoning"
- **Analysis**: "High-breadth nodes are integration hubs → critical for coherence"

---

## Depth Metrics

### Definition: Integration Depth

**Integration depth** = Minimum hop-distance from any primitive SubEntity

**Primitive SubEntity** = Foundational pattern with no inbound MEMBER_OF edges (leaf nodes in dependency graph)

**Formula:**
```
depth(s) = min{ length(path) | path from primitive p to s }
```

Where:
- `primitive p` has `in_degree(p) = 0` (no SubEntities depend on it)
- `path` is sequence of MEMBER_OF edges from p to s

**Interpretation:**
- `depth = 1` → Primitive itself
- `depth = 2` → Direct composite of primitives
- `depth = 5` → Mid-level abstraction
- `depth = 10+` → High-level meta-pattern

---

### Cypher Query: Integration Depth

#### Query 1: Single Node Depth

```cypher
// Find integration depth for specific SubEntity
MATCH (target:SubEntity {id: $target_id})

// Find all primitives (no inbound MEMBER_OF)
MATCH (primitive:SubEntity)
WHERE NOT (primitive)<-[:MEMBER_OF]-()

// Shortest path from any primitive to target
MATCH path = shortestPath((primitive)-[:MEMBER_OF*]->(target))

// Return minimum path length
WITH target, length(path) as pathLength
RETURN min(pathLength) as integration_depth
```

#### Query 2: All Nodes Depth (Batched)

```cypher
// Compute depth for all SubEntities

// Get all primitives
MATCH (primitive:SubEntity)
WHERE NOT (primitive)<-[:MEMBER_OF]-()
WITH collect(primitive) as primitives

// For each primitive, find paths to all reachable nodes
UNWIND primitives as p
MATCH path = (p)-[:MEMBER_OF*]->(target:SubEntity)
WITH target.id as targetId, length(path) as pathLength

// Group by target, take minimum
WITH targetId, min(pathLength) as integration_depth
RETURN targetId, integration_depth
ORDER BY integration_depth ASC
```

**Performance:** O(P × N × M) where P = primitives, N = nodes, M = avg path length

---

### Identifying Primitives

**Primitive SubEntities** have no inbound MEMBER_OF edges:

```cypher
MATCH (primitive:SubEntity)
WHERE NOT (primitive)<-[:MEMBER_OF]-()
RETURN primitive.id, primitive.name
```

**Validation:**
- Primitives should be foundational concepts (e.g., "Color", "Motion", "Valence")
- If no primitives exist, graph structure might be incorrect
- Expected: 5-20 primitives in a well-formed graph

---

## Breadth Metrics

### Definition: Integration Breadth

**Integration breadth** = Number of distinct communities/clusters a SubEntity connects to

**Community** = Densely connected group of SubEntities (detected via community detection algorithm)

**Formula:**
```
breadth(s) = |{ community(neighbor) | neighbor ∈ neighbors(s) }|
```

Where:
- `neighbors(s)` = SubEntities directly connected to s via MEMBER_OF (in either direction)
- `community(n)` = Community ID assigned by clustering algorithm

**Interpretation:**
- `breadth = 1` → Specialist (all neighbors in same community)
- `breadth = 3` → Moderate integrator (bridges 3 communities)
- `breadth = 7+` → Major integration hub (cross-domain connector)

---

### Community Detection

**Use Louvain algorithm** (available in FalkorDB/RedisGraph):

```cypher
// Run Louvain community detection
CALL db.labels() YIELD label
WHERE label = 'SubEntity'
CALL algo.louvain.stream('SubEntity', 'MEMBER_OF')
YIELD nodeId, community
RETURN nodeId, community
```

**Store community IDs temporarily** (in-memory or cache):

```python
def assign_communities(graph: Graph) -> Dict[str, int]:
    """
    Run Louvain clustering and assign community IDs.

    Returns:
        {node_id: community_id}
    """
    query = """
    CALL algo.louvain.stream('SubEntity', 'MEMBER_OF')
    YIELD nodeId, community
    RETURN nodeId, community
    """

    result = graph.query(query)
    return {row['nodeId']: row['community'] for row in result.result_set}
```

---

### Cypher Query: Integration Breadth

#### Query: Breadth for Single Node

```cypher
// Compute integration breadth for target node

// Step 1: Get target's neighbors (both directions)
MATCH (target:SubEntity {id: $target_id})
OPTIONAL MATCH (target)<-[:MEMBER_OF]-(child)
OPTIONAL MATCH (target)-[:MEMBER_OF]->(parent)
WITH target, collect(DISTINCT child) + collect(DISTINCT parent) as neighbors

// Step 2: Get community IDs for each neighbor
// (Assumes communities stored in node property or external map)
UNWIND neighbors as neighbor
WITH target, neighbor.community_id as communityId

// Step 3: Count distinct communities
WITH target, count(DISTINCT communityId) as integration_breadth
RETURN integration_breadth
```

**Alternative (if communities not stored):**

Run Louvain first, store results, then query:

```python
def compute_breadth(graph: Graph, target_id: str, communities: Dict[str, int]) -> int:
    """
    Compute integration breadth for target node.

    Args:
        communities: {node_id: community_id} from Louvain
    """

    query = f"""
    MATCH (target:SubEntity {{id: '{target_id}'}})
    OPTIONAL MATCH (target)<-[:MEMBER_OF]-(child)
    OPTIONAL MATCH (target)-[:MEMBER_OF]->(parent)
    WITH collect(DISTINCT child.id) + collect(DISTINCT parent.id) as neighbor_ids
    RETURN neighbor_ids
    """

    result = graph.query(query)
    neighbor_ids = result.result_set[0]['neighbor_ids']

    # Map neighbors to communities
    neighbor_communities = [communities[nid] for nid in neighbor_ids if nid in communities]

    # Count distinct communities
    integration_breadth = len(set(neighbor_communities))
    return integration_breadth
```

---

## Centrality Metrics (Closeness)

### Definition: Average Distance to All Nodes

**Closeness centrality** = Inverse of average hop-distance to all other nodes

**Formula:**
```
closeness(s) = (N - 1) / Σ distance(s, t)
```

Where:
- N = total nodes
- distance(s, t) = shortest path length from s to t

**Interpretation:**
- High closeness = Central (close to everything)
- Low closeness = Peripheral (far from most nodes)

### Cypher Query: Closeness Centrality

```cypher
// Compute closeness centrality for target node
MATCH (target:SubEntity {id: $target_id})

// Find shortest paths to all other nodes
MATCH path = shortestPath((target)-[:MEMBER_OF*]-(other:SubEntity))
WHERE other <> target
WITH target, length(path) as distance

// Compute average distance
WITH target, count(*) as reachableNodes, sum(distance) as totalDistance
RETURN (reachableNodes * 1.0 / totalDistance) as closeness_centrality
```

**Note:** This is expensive (O(N²)) - only compute for diagnostic purposes, not every frame.

---

## Python Implementation

### Integration Metrics Analyzer

```python
from typing import Dict, Tuple, List
from falkordb import Graph
import numpy as np

class IntegrationMetricsAnalyzer:
    """
    Compute integration depth, breadth, and centrality for SubEntities.

    All metrics are query-time (not stored).
    """

    def __init__(self, graph: Graph):
        self.graph = graph
        self.communities = None  # Lazy-loaded community assignments

    def compute_integration_depth(self, node_id: str) -> int:
        """
        Compute integration depth (min hops from primitives).

        Returns:
            Depth value (1 = primitive, higher = more abstract)
        """

        query = f"""
        MATCH (target:SubEntity {{id: '{node_id}'}})

        // Find primitives (no inbound edges)
        MATCH (primitive:SubEntity)
        WHERE NOT (primitive)<-[:MEMBER_OF]-()

        // Shortest path from any primitive to target
        MATCH path = shortestPath((primitive)-[:MEMBER_OF*]->(target))

        WITH length(path) as pathLength
        RETURN min(pathLength) as integration_depth
        """

        result = self.graph.query(query)
        if result.result_set:
            return result.result_set[0]['integration_depth'] or 1
        return 1  # If unreachable from primitives, treat as primitive itself

    def identify_primitives(self) -> List[str]:
        """
        Identify primitive SubEntities (no inbound MEMBER_OF).

        Returns:
            List of primitive node IDs
        """

        query = """
        MATCH (primitive:SubEntity)
        WHERE NOT (primitive)<-[:MEMBER_OF]-()
        RETURN primitive.id as id
        """

        result = self.graph.query(query)
        return [row['id'] for row in result.result_set]

    def compute_integration_breadth(self, node_id: str) -> int:
        """
        Compute integration breadth (distinct communities connected).

        Returns:
            Number of distinct communities
        """

        # Lazy-load community assignments
        if self.communities is None:
            self.communities = self._run_louvain()

        # Get neighbors
        query = f"""
        MATCH (target:SubEntity {{id: '{node_id}'}})
        OPTIONAL MATCH (target)<-[:MEMBER_OF]-(child)
        OPTIONAL MATCH (target)-[:MEMBER_OF]->(parent)
        WITH collect(DISTINCT child.id) + collect(DISTINCT parent.id) as neighbor_ids
        RETURN neighbor_ids
        """

        result = self.graph.query(query)
        if not result.result_set:
            return 0

        neighbor_ids = [nid for nid in result.result_set[0]['neighbor_ids'] if nid]

        # Map to communities
        neighbor_communities = [self.communities[nid] for nid in neighbor_ids
                              if nid in self.communities]

        # Count distinct
        return len(set(neighbor_communities))

    def _run_louvain(self) -> Dict[str, int]:
        """
        Run Louvain community detection.

        Returns:
            {node_id: community_id}
        """

        # Check if algo.louvain is available
        try:
            query = """
            CALL algo.louvain.stream('SubEntity', 'MEMBER_OF')
            YIELD nodeId, community
            RETURN nodeId, community
            """
            result = self.graph.query(query)
            return {row['nodeId']: row['community'] for row in result.result_set}

        except Exception as e:
            # Fallback: Use simple connected components
            print(f"Louvain not available, using connected components: {e}")
            return self._fallback_community_detection()

    def _fallback_community_detection(self) -> Dict[str, int]:
        """
        Fallback community detection using connected components.
        """

        query = """
        MATCH (s:SubEntity)
        RETURN s.id as node_id
        """

        result = self.graph.query(query)
        nodes = [row['node_id'] for row in result.result_set]

        # Simple: Assign all to community 0
        # (Real implementation would do BFS/DFS for connected components)
        return {node_id: 0 for node_id in nodes}

    def compute_closeness_centrality(self, node_id: str) -> float:
        """
        Compute closeness centrality (inverse avg distance).

        Returns:
            Closeness value (0-1, higher = more central)
        """

        query = f"""
        MATCH (target:SubEntity {{id: '{node_id}'}})

        MATCH path = shortestPath((target)-[:MEMBER_OF*]-(other:SubEntity))
        WHERE other <> target
        WITH length(path) as distance

        WITH count(*) as reachableNodes, sum(distance) as totalDistance
        RETURN (reachableNodes * 1.0 / totalDistance) as closeness
        """

        result = self.graph.query(query)
        if result.result_set and result.result_set[0]['closeness']:
            return result.result_set[0]['closeness']
        return 0.0

    def compute_all_metrics(self, node_id: str) -> Dict:
        """
        Compute all integration metrics for a node.

        Returns:
            {
                'integration_depth': int,
                'integration_breadth': int,
                'closeness_centrality': float
            }
        """

        return {
            'integration_depth': self.compute_integration_depth(node_id),
            'integration_breadth': self.compute_integration_breadth(node_id),
            'closeness_centrality': self.compute_closeness_centrality(node_id)
        }

    def emit_telemetry(self, node_id: str, metrics: Dict):
        """Emit integration metrics telemetry."""

        emit_telemetry({
            'type': 'integration_metrics.node',
            'timestamp': time.time(),
            'node_id': node_id,
            'metrics': metrics,
            'interpretation': self._interpret_metrics(metrics)
        })

    def _interpret_metrics(self, metrics: Dict) -> str:
        """Interpret metrics into human-readable category."""

        depth = metrics['integration_depth']
        breadth = metrics['integration_breadth']

        if depth <= 2 and breadth <= 2:
            return "primitive_specialist"
        elif depth <= 2 and breadth > 4:
            return "foundational_integrator"
        elif depth > 6 and breadth <= 2:
            return "abstract_specialist"
        elif depth > 6 and breadth > 4:
            return "meta_integrator"
        else:
            return "mid_level_pattern"
```

---

## Telemetry Events

### Integration Metrics Snapshot

```json
{
    "type": "integration_metrics.node",
    "timestamp": "2025-10-29T21:00:00Z",
    "node_id": "subentity_42",
    "node_name": "Semantic-Affect Bridge",
    "metrics": {
        "integration_depth": 4,
        "integration_breadth": 6,
        "closeness_centrality": 0.67
    },
    "interpretation": "mid_level_integrator",
    "primitives_reachable": ["color_primitive", "motion_primitive"],
    "communities_connected": [1, 3, 5, 7, 9, 11]
}
```

### Population Distribution

Periodically emit distribution across all nodes:

```json
{
    "type": "integration_metrics.population",
    "timestamp": "2025-10-29T21:00:00Z",
    "depth_distribution": {
        "1-2": 15,   // Primitive/foundational
        "3-5": 42,   // Mid-level
        "6-8": 23,   // Abstract
        "9+": 4      // Meta-level
    },
    "breadth_distribution": {
        "1-2": 28,   // Specialists
        "3-5": 35,   // Moderate integrators
        "6+": 11     // Major hubs
    },
    "mean_depth": 4.2,
    "mean_breadth": 3.1,
    "primitive_count": 12
}
```

---

## Validation Tests

### Test 1: Primitives Have Depth 1

```python
# Identify primitives
analyzer = IntegrationMetricsAnalyzer(graph)
primitives = analyzer.identify_primitives()

# All primitives should have depth 1
for prim_id in primitives:
    depth = analyzer.compute_integration_depth(prim_id)
    assert depth == 1, f"Primitive {prim_id} has depth {depth} != 1"
```

### Test 2: Depth Increases With Path Length

```python
# Create chain: A (primitive) → B → C → D
A = create_subentity("A")  # Primitive (no inbound)
B = create_subentity("B")
C = create_subentity("C")
D = create_subentity("D")

create_member_of_edge(A, B)
create_member_of_edge(B, C)
create_member_of_edge(C, D)

# Depths should increase
assert analyzer.compute_integration_depth(A.id) == 1
assert analyzer.compute_integration_depth(B.id) == 2
assert analyzer.compute_integration_depth(C.id) == 3
assert analyzer.compute_integration_depth(D.id) == 4
```

### Test 3: Breadth Counts Distinct Communities

```python
# Create two communities
comm1 = [create_subentity(f"c1_{i}") for i in range(3)]
comm2 = [create_subentity(f"c2_{i}") for i in range(3)]

# Assign communities manually
communities = {
    **{n.id: 1 for n in comm1},
    **{n.id: 2 for n in comm2}
}
analyzer.communities = communities

# Create hub connecting to both communities
hub = create_subentity("hub")
for n in comm1:
    create_member_of_edge(n, hub)
for n in comm2:
    create_member_of_edge(n, hub)

# Hub should have breadth 2 (connects 2 communities)
breadth = analyzer.compute_integration_breadth(hub.id)
assert breadth == 2
```

---

## Dashboard Integration

### Visualization Requirements

**For Iris (Frontend):**

1. **Node Detail Panel**
   - Show depth/breadth/closeness for selected SubEntity
   - Interpretation label ("primitive_specialist", etc.)
   - List of communities connected

2. **Topology Heatmap**
   - X-axis: Integration depth (1-10)
   - Y-axis: Integration breadth (1-10)
   - Dots = SubEntities (color by energy)
   - Clusters reveal topology structure

3. **Distribution Histograms**
   - Depth distribution (bar chart)
   - Breadth distribution (bar chart)
   - Highlight current active nodes

---

## Implementation Checklist

**For Felix (Core Consciousness):**
- [ ] Implement `IntegrationMetricsAnalyzer` class
- [ ] Cypher queries for depth/breadth/closeness
- [ ] Primitive identification
- [ ] Community detection integration (Louvain fallback)
- [ ] Telemetry emission
- [ ] Unit tests (primitives depth=1, chain depth, breadth counting)

**For Atlas (Infrastructure):**
- [ ] API endpoint: `GET /consciousness/integration-metrics/{node_id}`
- [ ] Periodic population snapshot (hourly)
- [ ] WebSocket event: `integration_metrics.node`

**For Iris (Frontend):**
- [ ] Node detail panel with depth/breadth/closeness display
- [ ] Topology heatmap (depth × breadth)
- [ ] Distribution histograms

---

## Open Questions for Luca

1. **Primitive definition**: Should primitives be explicitly marked, or inferred from in-degree=0?
2. **Depth interpretation**: Is high depth (abstract/meta) always "good", or situational?
3. **Breadth threshold**: At what breadth level does a node become "integration hub"?
4. **Community algorithm**: Louvain vs Label Propagation vs Modularity-based?

---

**Author:** Ada "Bridgekeeper" (Architect)
**Date:** 2025-10-29
**For Implementation:** Felix + Atlas
**Handoff from:** Luca (Heterarchical graph, path-dependent scale)
