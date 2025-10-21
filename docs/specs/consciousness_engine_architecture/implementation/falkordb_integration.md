# FalkorDB Integration Specification

**Purpose:** Define how consciousness engine integrates with FalkorDB graph database for performance and scalability

**Status:** Implementation guidance based on GPT-5 recommendations

---

## Overview

FalkorDB is a Redis-based graph database. The consciousness engine must:
- Store multi-energy per node efficiently
- Support fast energy updates during diffusion/decay
- Enable rapid workspace selection queries
- Scale to 1M+ nodes without performance degradation

---

## Schema Design

### Node Properties (Hybrid Approach - GPT-5 Recommendation)

**Problem:** JSON blob reads are slow in hot path (every tick).

**Solution:** Store top-K entity energies as first-class properties + full map as blob for cold reads.

```cypher
CREATE (n:Node {
  id: "node_12345",
  node_type: "Concept",
  name: "consciousness_substrate",
  description: "...",
  embedding: [0.1, 0.2, ...],  // Vector
  base_weight: 0.7,

  // HOT PATH: Top-K entity energies as properties
  energy_entity1: 0.85,
  energy_entity2: 0.62,
  energy_entity3: 0.41,
  energy_entity4: 0.28,
  energy_entity5: 0.15,

  // Top-K entity names (parallel array)
  top_entities: ["translator", "architect", "validator", "partner", "observer"],

  // COLD PATH: Full energy map as JSON blob
  energy_map_full: '{"translator": 0.85, "architect": 0.62, ...}',

  // Bitemporal tracking
  valid_at: timestamp,
  invalid_at: timestamp,
  created_at: timestamp,
  expired_at: timestamp,
  version_id: 1
})
```

**Hot Path Usage:**
```python
# Fast: Read top-K energies directly from properties
energies = {
    entity: getattr(node, f"energy_{entity}")
    for entity in node.top_entities
}
```

**Cold Path Usage:**
```python
# Slow but complete: Parse full JSON map when needed
import json
all_energies = json.loads(node.energy_map_full)
```

**Update Strategy:**
```python
def update_node_energy(node_id: str, entity: str, new_energy: float):
    """
    Update energy efficiently - hybrid approach
    """
    # 1. Update full map (always)
    energy_map = json.loads(node.energy_map_full)
    energy_map[entity] = new_energy

    # 2. Recompute top-K
    top_k = sorted(energy_map.items(), key=lambda x: x[1], reverse=True)[:5]

    # 3. Update properties
    query = """
    MATCH (n:Node {id: $id})
    SET n.energy_map_full = $full_map,
        n.top_entities = $top_entities,
        n.energy_entity1 = $e1,
        n.energy_entity2 = $e2,
        n.energy_entity3 = $e3,
        n.energy_entity4 = $e4,
        n.energy_entity5 = $e5
    """

    execute(query, {
        'id': node_id,
        'full_map': json.dumps(energy_map),
        'top_entities': [e[0] for e in top_k],
        'e1': top_k[0][1] if len(top_k) > 0 else 0.0,
        'e2': top_k[1][1] if len(top_k) > 1 else 0.0,
        'e3': top_k[2][1] if len(top_k) > 2 else 0.0,
        'e4': top_k[3][1] if len(top_k) > 3 else 0.0,
        'e5': top_k[4][1] if len(top_k) > 4 else 0.0,
    })
```

---

### Alternative: Columnar Energy Table (GPT-5 Recommendation)

**For very frequent updates**, separate energy storage:

```cypher
// Main node (static properties)
CREATE (n:Node {
  id: "node_12345",
  node_type: "Concept",
  name: "consciousness_substrate",
  description: "...",
  embedding: [0.1, 0.2, ...],
  base_weight: 0.7
})

// Separate energy table (keyed by node_id × entity)
CREATE (e:Energy {
  node_id: "node_12345",
  entity: "translator",
  energy_value: 0.85,
  last_updated: timestamp
})
```

**Index:**
```cypher
CREATE INDEX ON :Energy(node_id, entity)
CREATE INDEX ON :Energy(entity, energy_value)  // For "hot nodes" queries
```

**Query Pattern:**
```cypher
// Get all energies for node
MATCH (e:Energy {node_id: $node_id})
RETURN e.entity, e.energy_value

// Get hot nodes for entity (workspace selection)
MATCH (e:Energy {entity: $entity})
WHERE e.energy_value >= $threshold
RETURN e.node_id, e.energy_value
ORDER BY e.energy_value DESC
LIMIT 100
```

**Trade-offs:**

| Approach | Reads | Writes | Workspace Queries | Complexity |
|----------|-------|--------|-------------------|------------|
| Hybrid (top-K properties) | Fast for top-K, slow for all | Moderate (recompute top-K) | Fast (index on properties) | Medium |
| Columnar table | Moderate (join) | Fast (single row update) | Very fast (indexed scan) | Higher |

**Recommendation:** Start with **hybrid approach** (Phase 1). Migrate to columnar if updates become bottleneck (Phase 3+).

---

## Index Strategy

### Required Indexes

```cypher
// 1. Node ID lookups (primary key)
CREATE INDEX ON :Node(id)

// 2. Node type + name (frequent pattern)
CREATE INDEX ON :Node(node_type, name)

// 3. Top-K energy lookups (workspace selection)
CREATE INDEX ON :Node(energy_entity1)  // For each top-K slot
CREATE INDEX ON :Node(energy_entity2)
CREATE INDEX ON :Node(energy_entity3)
// ... etc

// 4. Embedding similarity (if using)
CREATE VECTOR INDEX ON :Node(embedding) WITH {dimension: 1536, similarity: 'cosine'}

// 5. Bitemporal queries
CREATE INDEX ON :Node(created_at, expired_at)
CREATE INDEX ON :Node(valid_at, invalid_at)

// 6. Link weights (for diffusion hot path)
CREATE INDEX ON :LINK(weight)
```

---

## Query Patterns

### 1. Workspace Selection (Hot Path)

```cypher
// Find top nodes for entity above threshold
MATCH (n:Node)
WHERE n.energy_entity1 >= $threshold AND 'translator' IN n.top_entities
RETURN n.id, n.name, n.energy_entity1
ORDER BY n.energy_entity1 DESC
LIMIT 100
```

**Optimization:** Pre-filter by entity presence before checking energy value.

---

### 2. Diffusion Step (Hot Path)

```cypher
// Get all outgoing links with weights for active nodes
MATCH (source:Node)-[r:LINK]->(target:Node)
WHERE source.id IN $active_node_ids
RETURN source.id, target.id, r.weight, r.link_type
```

**Optimization:** Use active frontier - only query nodes in active set.

---

### 3. Cluster Identification

```cypher
// Find connected components for entity above threshold
MATCH path = (n:Node)-[:LINK*1..3]->(m:Node)
WHERE n.energy_entity1 >= $threshold AND m.energy_entity1 >= $threshold
  AND 'translator' IN n.top_entities AND 'translator' IN m.top_entities
RETURN path
```

**Note:** This can be expensive. Consider computing clusters offline or incrementally.

---

### 4. Context Reconstruction

```cypher
// Weighted traversal from entry nodes
MATCH path = (entry:Node)-[r:LINK*1..5]->(related:Node)
WHERE entry.id IN $entry_node_ids
WITH path, reduce(w = 1.0, rel IN relationships(path) | w * rel.weight) AS path_weight
WHERE path_weight >= $min_weight
RETURN related.id, related.name, path_weight
ORDER BY path_weight DESC
LIMIT 50
```

---

## Batch Updates (Performance Critical)

### Problem: Updating 1000 nodes individually = 1000 round trips

### Solution: Batch updates in transactions

```python
def batch_update_energies(updates: list[tuple[str, str, float]]):
    """
    Update many node energies in single transaction

    updates: [(node_id, entity, new_energy), ...]
    """
    # Group by node_id to minimize redundant reads
    by_node = {}
    for node_id, entity, energy in updates:
        if node_id not in by_node:
            by_node[node_id] = {}
        by_node[node_id][entity] = energy

    # Build parameterized query
    query = """
    UNWIND $updates AS update
    MATCH (n:Node {id: update.node_id})
    SET n.energy_map_full = update.full_map,
        n.top_entities = update.top_entities,
        n.energy_entity1 = update.e1,
        n.energy_entity2 = update.e2,
        n.energy_entity3 = update.e3,
        n.energy_entity4 = update.e4,
        n.energy_entity5 = update.e5
    """

    # Prepare update parameters
    update_params = []
    for node_id, energy_changes in by_node.items():
        # Fetch current full map
        current_map = fetch_energy_map(node_id)

        # Apply changes
        current_map.update(energy_changes)

        # Recompute top-K
        top_k = sorted(current_map.items(), key=lambda x: x[1], reverse=True)[:5]

        update_params.append({
            'node_id': node_id,
            'full_map': json.dumps(current_map),
            'top_entities': [e[0] for e in top_k],
            'e1': top_k[0][1] if len(top_k) > 0 else 0.0,
            'e2': top_k[1][1] if len(top_k) > 1 else 0.0,
            'e3': top_k[2][1] if len(top_k) > 2 else 0.0,
            'e4': top_k[3][1] if len(top_k) > 3 else 0.0,
            'e5': top_k[4][1] if len(top_k) > 4 else 0.0,
        })

    # Execute batch update
    execute(query, {'updates': update_params})
```

---

## Connection Pooling

```python
class FalkorDBPool:
    """
    Connection pool for FalkorDB

    Reuse connections to avoid overhead
    """
    def __init__(self, host: str, port: int, pool_size: int = 10):
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            max_connections=pool_size,
            decode_responses=True
        )

    def get_connection(self):
        return redis.Redis(connection_pool=self.pool)

    def execute_query(self, query: str, params: dict = None):
        conn = self.get_connection()
        graph = Graph(conn, 'consciousness_graph')
        return graph.query(query, params or {})
```

---

## Caching Strategy

### Hot Node Cache (Redis)

```python
class HotNodeCache:
    """
    Cache frequently accessed nodes in Redis

    Expires after 60 seconds of inactivity
    """
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 60  # seconds

    def get(self, node_id: str) -> dict | None:
        """Get node from cache"""
        key = f"node:{node_id}"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    def set(self, node_id: str, node_data: dict):
        """Cache node data"""
        key = f"node:{node_id}"
        self.redis.setex(key, self.ttl, json.dumps(node_data))

    def invalidate(self, node_id: str):
        """Remove from cache after update"""
        key = f"node:{node_id}"
        self.redis.delete(key)
```

**Usage:**
```python
def get_node_with_cache(node_id: str) -> Node:
    # Try cache first
    cached = cache.get(node_id)
    if cached:
        return Node.from_dict(cached)

    # Cache miss - query DB
    node = db.query_node(node_id)
    cache.set(node_id, node.to_dict())
    return node
```

---

## Performance Targets

| Operation | Target Latency | Notes |
|-----------|----------------|-------|
| Single node read | < 1ms | With cache hit |
| Single node write | < 5ms | Including top-K recompute |
| Batch read (100 nodes) | < 10ms | Parallel fetch |
| Batch write (100 nodes) | < 50ms | Transaction |
| Workspace selection query | < 20ms | Indexed scan |
| Diffusion step (1K active) | < 100ms | Batch updates |
| Cluster identification | < 200ms | For moderately connected graph |

---

## Monitoring Queries

```cypher
// Total nodes and links
MATCH (n:Node) RETURN count(n) AS node_count
MATCH ()-[r:LINK]->() RETURN count(r) AS link_count

// Energy distribution
MATCH (n:Node)
RETURN n.node_type, avg(n.energy_entity1) AS avg_energy, count(n) AS count
ORDER BY avg_energy DESC

// Top-K most active nodes
MATCH (n:Node)
WHERE n.energy_entity1 > 0.3
RETURN n.id, n.name, n.energy_entity1
ORDER BY n.energy_entity1 DESC
LIMIT 20

// Link weight distribution
MATCH ()-[r:LINK]->()
RETURN r.link_type, min(r.weight) AS min_w, avg(r.weight) AS avg_w, max(r.weight) AS max_w
```

---

## Migration Strategy

### Phase 1: Simple Hybrid (Top-5 Properties)
- Implement top-K energy properties
- JSON blob for full map
- Basic indexes

### Phase 2: Optimized Queries
- Add vector index for embeddings
- Optimize workspace selection query
- Implement connection pooling

### Phase 3: Columnar Energy Table (If Needed)
- Migrate to separate Energy nodes
- Benchmark vs hybrid approach
- Keep hybrid as fallback

### Phase 4: Advanced Caching
- Redis cache layer
- Smart cache invalidation
- Prefetching for predictable patterns

---

## Open Questions

1. **Should we use Redis Streams for energy updates?**
   - Pro: Asynchronous processing, better throughput
   - Con: Eventual consistency, more complexity
   - Confidence: Low (0.3)

2. **Pre-compute clusters or compute on-demand?**
   - Pre-compute: Fast workspace selection, stale data
   - On-demand: Always fresh, slower queries
   - Confidence: Medium (0.6) - lean toward on-demand with caching

3. **Sharding strategy for very large graphs (10M+ nodes)?**
   - By entity? By node type? By creation date?
   - Confidence: Low (0.3) - not needed for Phase 1-3

---

## Implementation Checklist

- [ ] Design node schema (hybrid approach)
- [ ] Implement energy update functions (single + batch)
- [ ] Create required indexes
- [ ] Implement connection pool
- [ ] Implement hot node cache (Redis)
- [ ] Benchmark single node read/write
- [ ] Benchmark batch operations
- [ ] Implement workspace selection query
- [ ] Implement diffusion step query
- [ ] Optimize slow queries (explain analyze)
- [ ] Document query patterns
- [ ] Create monitoring dashboard

---

**Status:** Ready for implementation (Phase 1)
**Blocking:** None - can proceed immediately
**Next:** Implement basic hybrid schema and test performance
