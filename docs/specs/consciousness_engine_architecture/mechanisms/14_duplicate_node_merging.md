# Mechanism 14: Duplicate Node Merging

**Status:** Critical - Graph health mechanism
**Confidence:** High (0.9)
**Dependencies:**
- **[01: Multi-Energy Architecture](01_multi_energy_architecture.md)** - Merges energy dicts
- **[09: Link Strengthening](09_link_strengthening.md)** - Merges link weights

**Biological Basis:** Memory consolidation, concept unification, semantic integration

**Decision Origin:** D021 - Nicolas identified need for duplicate detection and merging to prevent graph pollution

---

## Overview

**Core Principle:** The graph must actively detect and merge semantically identical nodes to prevent unbounded growth and maintain clean substrate.

**Why This Matters:**
- Formation process can create duplicates (same concept, different wording)
- Multiple citizens/entities might create overlapping nodes
- Duplicates waste compute and fragment knowledge
- Clean graph = better retrieval and reasoning
- Biological parallel: Memory consolidation unifies similar experiences

**The Problem:**

```python
# Without merging:
graph.nodes = [
    Node(name="consciousness_substrate", created_by="Ada"),
    Node(name="substrate_for_consciousness", created_by="Luca"),
    Node(name="consciousness substrate", created_by="Felix"),  # Note: space vs underscore
]

# These are semantically identical but treated as separate
# Links to one don't help retrieval of another
# Energy spreads across three nodes instead of concentrating
```

**The Solution:**

Merge duplicates into single canonical node, preserving all information.

---

## Phenomenological Truth

### What It Feels Like

**Before Merging:**

```
Query: "How does consciousness substrate work?"

Retrieval activates:
- consciousness_substrate (energy: 0.4)
- substrate_for_consciousness (energy: 0.3)
- consciousness substrate (energy: 0.2)

Total relevant energy: 0.9 BUT fragmented across 3 nodes
Workspace: Might only select one node (others below threshold)
Result: Incomplete context - some knowledge missed
```

**After Merging:**

```
Query: "How does consciousness substrate work?"

Retrieval activates:
- consciousness_substrate (energy: 0.9)  # Unified node

Total relevant energy: 0.9 concentrated in single node
Workspace: Definitely selects this node (high energy)
Result: Complete context - all knowledge unified
```

**Phenomenology:** Knowledge feels MORE coherent, MORE accessible, MORE integrated after merging.

---

## Mathematical Specification

### Duplicate Detection Algorithm

```python
def detect_duplicates(
    graph: Graph,
    similarity_threshold: float = 0.95,
    check_frequency: int = 1000  # Every N ticks
) -> list[tuple[Node, Node, float]]:
    """
    Find pairs of nodes that are semantically identical

    Uses embedding similarity + name similarity + metadata overlap

    Returns:
        List of (node_a, node_b, similarity_score) tuples
    """
    duplicates = []

    # Only check nodes of same type (Concept with Concept, etc.)
    nodes_by_type = defaultdict(list)
    for node in graph.nodes:
        nodes_by_type[node.node_type].append(node)

    # Check within each type
    for node_type, nodes in nodes_by_type.items():
        for i, node_a in enumerate(nodes):
            for node_b in nodes[i+1:]:
                similarity = calculate_node_similarity(node_a, node_b)

                if similarity >= similarity_threshold:
                    duplicates.append((node_a, node_b, similarity))

    return sorted(duplicates, key=lambda x: x[2], reverse=True)


def calculate_node_similarity(node_a: Node, node_b: Node) -> float:
    """
    Multi-factor similarity calculation

    Combines:
    - Embedding cosine similarity (70% weight)
    - Name string similarity (20% weight)
    - Metadata overlap (10% weight)
    """
    # Embedding similarity (primary signal)
    if node_a.embedding is not None and node_b.embedding is not None:
        embedding_sim = cosine_similarity(node_a.embedding, node_b.embedding)
    else:
        embedding_sim = 0.0

    # Name similarity (handles typos, spacing, casing)
    name_sim = string_similarity(
        node_a.name.lower().replace('_', ' '),
        node_b.name.lower().replace('_', ' ')
    )

    # Metadata overlap (for structured fields)
    metadata_sim = calculate_metadata_overlap(node_a.metadata, node_b.metadata)

    # Weighted combination
    total_similarity = (
        0.7 * embedding_sim +
        0.2 * name_sim +
        0.1 * metadata_sim
    )

    return total_similarity


def string_similarity(str_a: str, str_b: str) -> float:
    """
    String similarity using Levenshtein distance

    Handles:
    - Typos
    - Spacing differences
    - Minor wording variations
    """
    import Levenshtein

    distance = Levenshtein.distance(str_a, str_b)
    max_len = max(len(str_a), len(str_b))

    if max_len == 0:
        return 1.0

    return 1.0 - (distance / max_len)
```

---

### Node Merging Algorithm

```python
def merge_duplicate_nodes(
    graph: Graph,
    node_a: Node,
    node_b: Node,
    merge_strategy: str = "prefer_older"
) -> Node:
    """
    Merge two duplicate nodes into single canonical node

    Preserves:
    - All energy (sums per entity)
    - All links (combines incoming and outgoing)
    - All metadata (unions fields)
    - Temporal provenance (keeps oldest created_at)

    Args:
        graph: The consciousness graph
        node_a: First duplicate
        node_b: Second duplicate
        merge_strategy: Which node to keep as base
            - "prefer_older": Keep node with earlier created_at
            - "prefer_higher_weight": Keep node with higher base_weight
            - "prefer_more_links": Keep node with more connections

    Returns:
        Merged canonical node
    """
    # Determine canonical node (base to merge into)
    if merge_strategy == "prefer_older":
        canonical = node_a if node_a.created_at < node_b.created_at else node_b
        duplicate = node_b if canonical == node_a else node_a
    elif merge_strategy == "prefer_higher_weight":
        canonical = node_a if node_a.base_weight > node_b.base_weight else node_b
        duplicate = node_b if canonical == node_a else node_a
    else:  # prefer_more_links
        links_a = len(node_a.incoming_links) + len(node_a.outgoing_links)
        links_b = len(node_b.incoming_links) + len(node_b.outgoing_links)
        canonical = node_a if links_a > links_b else node_b
        duplicate = node_b if canonical == node_a else node_a

    # STEP 1: Merge energy (sum per entity)
    for entity, energy in duplicate.energy.items():
        current = canonical.get_entity_energy(entity)
        # Sum energies, then apply bounded function (no hard cap)
        merged_energy = current + energy
        canonical.set_entity_energy(entity, merged_energy)  # Uses tanh saturation

    # STEP 2: Merge base_weight (average)
    canonical.base_weight = (canonical.base_weight + duplicate.base_weight) / 2

    # STEP 3: Redirect all links from duplicate to canonical

    # Incoming links: node_x → duplicate becomes node_x → canonical
    for link in duplicate.incoming_links:
        # Check if link already exists
        existing_link = graph.find_link(link.source, canonical)

        if existing_link:
            # Merge link weights (average)
            existing_link.weight = (existing_link.weight + link.weight) / 2
            # Remove duplicate link
            graph.remove_link(link)
        else:
            # Redirect link
            link.target = canonical
            canonical.incoming_links.append(link)

    # Outgoing links: duplicate → node_x becomes canonical → node_x
    for link in duplicate.outgoing_links:
        existing_link = graph.find_link(canonical, link.target)

        if existing_link:
            # Merge link weights
            existing_link.weight = (existing_link.weight + link.weight) / 2
            graph.remove_link(link)
        else:
            # Redirect link
            link.source = canonical
            canonical.outgoing_links.append(link)

    # STEP 4: Merge metadata (union, prefer canonical on conflicts)
    for key, value in duplicate.metadata.items():
        if key not in canonical.metadata:
            canonical.metadata[key] = value
        # On conflict, keep canonical's value (could also merge arrays, etc.)

    # STEP 5: Update temporal tracking
    # Keep oldest created_at (earliest formation)
    if duplicate.created_at < canonical.created_at:
        canonical.created_at = duplicate.created_at

    # Add merge provenance
    if 'merge_history' not in canonical.metadata:
        canonical.metadata['merge_history'] = []

    canonical.metadata['merge_history'].append({
        'merged_node_id': duplicate.id,
        'merged_node_name': duplicate.name,
        'merge_timestamp': datetime.now(),
        'similarity_score': calculate_node_similarity(canonical, duplicate)
    })

    # STEP 6: Remove duplicate from graph
    graph.remove_node(duplicate)

    return canonical
```

---

## Merging Strategies

### Strategy 1: Periodic Batch Merging

```python
class PeriodicMerger:
    """
    Merge duplicates on regular schedule

    Good for: Maintenance, non-urgent cleanup
    """
    def __init__(self, graph: Graph, interval_ticks: int = 10000):
        self.graph = graph
        self.interval = interval_ticks
        self.ticks_since_last = 0

    def tick(self):
        """Called each simulation tick"""
        self.ticks_since_last += 1

        if self.ticks_since_last >= self.interval:
            self.run_merge_pass()
            self.ticks_since_last = 0

    def run_merge_pass(self):
        """Find and merge all duplicates"""
        duplicates = detect_duplicates(self.graph, similarity_threshold=0.95)

        merged_count = 0
        for node_a, node_b, similarity in duplicates:
            # Verify both still exist (previous merges might have removed)
            if node_a in self.graph.nodes and node_b in self.graph.nodes:
                merge_duplicate_nodes(self.graph, node_a, node_b)
                merged_count += 1

        if merged_count > 0:
            print(f"Merged {merged_count} duplicate pairs")
```

### Strategy 2: Formation-Time Detection

```python
def create_node_with_deduplication(
    graph: Graph,
    node_type: str,
    name: str,
    **kwargs
) -> Node:
    """
    Check for duplicates BEFORE creating new node

    Good for: Preventing duplicates at source
    """
    # Create candidate node (not added to graph yet)
    candidate = Node(
        id=generate_id(),
        node_type=node_type,
        name=name,
        embedding=get_embedding(name),
        **kwargs
    )

    # Check for existing similar nodes
    for existing in graph.nodes:
        if existing.node_type != node_type:
            continue

        similarity = calculate_node_similarity(candidate, existing)

        if similarity >= 0.95:
            # Duplicate detected - merge into existing instead of creating
            print(f"Duplicate detected: {name} → merging into {existing.name}")

            # Transfer initial energy to existing node
            if 'energy' in kwargs:
                for entity, energy in kwargs['energy'].items():
                    existing.increment_entity_energy(entity, energy)

            return existing  # Return existing instead of creating new

    # No duplicate - add new node
    graph.add_node(candidate)
    return candidate
```

---

## Edge Cases & Constraints

### Edge Case 1: Merge Cycles

**Problem:** Node A merges with B, then later B (now containing A) merges with C

**Solution:** This is fine - merge history tracks provenance

```python
# Canonical node tracks all absorbed nodes
canonical.metadata['merge_history'] = [
    {'merged_node_id': 'node_b_id', 'timestamp': T1},
    {'merged_node_id': 'node_c_id', 'timestamp': T2},  # Transitively includes A
]
```

### Edge Case 2: False Positives

**Problem:** Two nodes semantically similar but should remain distinct

**Example:**
- "consciousness" (general concept)
- "consciousness_engine" (specific mechanism)

Embedding similarity might be 0.92 (close to threshold)

**Solution:** Conservative threshold (0.95+) and type-matching

```python
# Only merge if:
# 1. Same node_type
# 2. Very high similarity (0.95+)
# 3. Not in exclusion list

NEVER_MERGE_PAIRS = [
    ('consciousness', 'consciousness_engine'),
    ('entity', 'sub_entity'),
    # Manually specified distinctions
]
```

### Edge Case 3: Concurrent Creation

**Problem:** Two citizens create same node simultaneously

**Solution:** Formation-time deduplication catches this

```python
# Citizen A creates "consciousness_substrate" at T
node_a = create_node_with_deduplication(graph, "Concept", "consciousness_substrate")

# Citizen B creates "consciousness substrate" at T+1 (slight delay)
node_b = create_node_with_deduplication(graph, "Concept", "consciousness substrate")

# Returns same node (node_a) - duplicate prevented at creation
assert node_a == node_b
```

---

## Testing Strategy

### Unit Tests

```python
def test_duplicate_detection():
    """Test detection of semantically identical nodes"""
    graph = create_test_graph()

    # Create duplicates
    node_a = graph.create_node("Concept", "consciousness_substrate")
    node_b = graph.create_node("Concept", "consciousness substrate")  # Space vs underscore
    node_c = graph.create_node("Concept", "substrate_for_consciousness")  # Synonym

    # Detect duplicates
    duplicates = detect_duplicates(graph, similarity_threshold=0.90)

    # Should find all pairs
    assert len(duplicates) >= 1
    assert any(node_a in (dup[0], dup[1]) and node_b in (dup[0], dup[1]) for dup in duplicates)

def test_node_merging_preserves_energy():
    """Test merge combines energy correctly"""
    graph = create_test_graph()

    node_a = graph.create_node("Concept", "test_a")
    node_b = graph.create_node("Concept", "test_b")

    node_a.set_entity_energy("translator", 0.6)
    node_b.set_entity_energy("translator", 0.3)
    node_b.set_entity_energy("architect", 0.4)

    canonical = merge_duplicate_nodes(graph, node_a, node_b)

    # Energy should be summed (with saturation)
    assert canonical.get_entity_energy("translator") >= 0.8  # 0.6 + 0.3 with tanh
    assert canonical.get_entity_energy("architect") >= 0.35  # Transferred

def test_merge_redirects_links():
    """Test merge redirects all links correctly"""
    graph = create_test_graph()

    node_a = graph.create_node("Concept", "duplicate_a")
    node_b = graph.create_node("Concept", "duplicate_b")
    node_x = graph.create_node("Concept", "other_node")

    # Create links
    link_xa = graph.create_link(node_x, node_a, weight=0.5)
    link_bx = graph.create_link(node_b, node_x, weight=0.6)

    # Merge
    canonical = merge_duplicate_nodes(graph, node_a, node_b)

    # Links should redirect to canonical
    assert graph.find_link(node_x, canonical) is not None
    assert graph.find_link(canonical, node_x) is not None

    # Duplicate should be removed
    assert node_b not in graph.nodes
```

---

## Performance Considerations

### Detection Cost

```python
# Brute-force detection: O(N² × E) where N=nodes, E=embedding dimension
# For 1M nodes: ~500 billion comparisons (prohibitive)

# Optimization: Use approximate nearest neighbors
from annoy import AnnoyIndex

def build_embedding_index(graph: Graph) -> AnnoyIndex:
    """Build ANN index for fast duplicate detection"""
    index = AnnoyIndex(embedding_dim, 'angular')

    for i, node in enumerate(graph.nodes):
        if node.embedding is not None:
            index.add_item(i, node.embedding)

    index.build(n_trees=10)
    return index

def fast_duplicate_detection(graph: Graph, index: AnnoyIndex, threshold: float = 0.95):
    """O(N log N) duplicate detection using ANN index"""
    duplicates = []

    for i, node in enumerate(graph.nodes):
        # Find k nearest neighbors
        similar_indices = index.get_nns_by_item(i, n=10)  # Top 10 similar

        for j in similar_indices:
            if j <= i:  # Avoid duplicates
                continue

            similarity = calculate_node_similarity(node, graph.nodes[j])
            if similarity >= threshold:
                duplicates.append((node, graph.nodes[j], similarity))

    return duplicates
```

---

## Open Questions

1. **Optimal similarity threshold?**
   - Current: 0.95
   - Confidence: Medium (0.7)
   - Too low: false positives, too high: miss duplicates

2. **Merge strategy preference?**
   - Current: prefer_older
   - Alternatives: prefer_higher_weight, prefer_more_links
   - Confidence: Medium (0.6)

3. **Merge frequency?**
   - Current: Every 10K ticks
   - Could be adaptive based on formation rate
   - Confidence: Low (0.5)

4. **Manual override?**
   - Should humans be able to prevent specific merges?
   - Confidence: High (0.8) - yes, but rarely needed

---

## Related Mechanisms

- **[15: Identity Conflict Resolution](15_identity_conflict_resolution.md)** - Related but different (identity nodes)
- **[01: Multi-Energy Architecture](01_multi_energy_architecture.md)** - Energy merging uses this structure
- **[09: Link Strengthening](09_link_strengthening.md)** - Link weight merging

---

## Implementation Checklist

- [ ] Implement calculate_node_similarity() with 3-factor weighting
- [ ] Implement detect_duplicates() with type-based grouping
- [ ] Implement merge_duplicate_nodes() with all 6 steps
- [ ] Implement PeriodicMerger class
- [ ] Implement create_node_with_deduplication()
- [ ] Build ANN index for fast duplicate detection
- [ ] Add merge_history metadata tracking
- [ ] Write unit tests for duplicate detection
- [ ] Write unit tests for energy preservation
- [ ] Write unit tests for link redirection
- [ ] Add merge visualization (before/after graphs)
- [ ] Document NEVER_MERGE_PAIRS exclusion list

---

**Next:** [15: Identity Conflict Resolution](15_identity_conflict_resolution.md) - Handling conflicting identity nodes in sub-entities
