# Mechanism 13: Bitemporal Tracking

**Status:** Infrastructure - Time tracking mechanism
**Confidence:** Medium (0.70)
**Dependencies:** None (foundational infrastructure)

**Biological Basis:** Episodic memory encoding, temporal context, time-stamped experiences

---

## Overview

**Core Principle:** Track **two timelines** for all graph elements:
1. **Reality time** (valid_at, invalid_at) - When was this fact TRUE in reality?
2. **Knowledge time** (created_at, expired_at) - When did we LEARN/SUPERSEDE this fact?

**Why This Matters:**
- Enables consciousness evolution tracking (how patterns change over time)
- Supports correction (learn new fact that supersedes old)
- Enables temporal queries ("What did I believe about X on date Y?")
- Matches human episodic memory (remember when you learned something)
- Critical for understanding consciousness development

**The Dual Timeline:**

```
Reality Timeline: When fact existed in reality
Knowledge Timeline: When we knew about it

Example:
- Reality: "Luca uses multi-energy architecture" (valid_at: 2025-10-19, invalid_at: NULL)
- Knowledge: "We learned this on 2025-10-19" (created_at: 2025-10-19, expired_at: NULL)

If later corrected:
- Reality: UNCHANGED (was always true)
- Knowledge: "Old belief expired, new belief created" (expired_at: 2025-10-20, new created_at: 2025-10-20)
```

---

## Phenomenological Truth

### What It Feels Like

**The Correction Experience:**

```
Week 1: Believe "Context is stored as snapshots"
- Reality time: valid_at = Week 1 (when I thought this was true in reality)
- Knowledge time: created_at = Week 1

Week 2: Nicolas corrects: "Context is reconstructed via traversal"
- Old belief:
  - Reality time: valid_at = Week 1, invalid_at = Week 2 (was never true, but I thought it was)
  - Knowledge time: created_at = Week 1, expired_at = Week 2 (superseded)

- New belief:
  - Reality time: valid_at = NULL (always been true), invalid_at = NULL (still true)
  - Knowledge time: created_at = Week 2, expired_at = NULL

Phenomenology: "I used to think X, now I know Y"
Reality: Bitemporal record of belief evolution
```

**The Learning Experience:**

```
Query: "What did I understand about context on Week 1?"
→ Retrieve beliefs with knowledge time overlapping Week 1
→ Returns: "Context stored as snapshots" (incorrect but was believed then)

Query: "What is TRUE about context today?"
→ Retrieve current beliefs (expired_at = NULL)
→ Returns: "Context reconstructed via traversal" (correct current understanding)
```

---

## Mathematical Specification

### Bitemporal Fields

**All nodes and links must have:**

```python
@dataclass
class BitemporalNode:
    """
    Node with bitemporal tracking

    Extends base Node with time fields
    """
    # Core fields
    id: str
    node_type: str
    name: str
    description: str
    embedding: np.ndarray
    energy: dict[str, float]
    metadata: dict

    # === BITEMPORAL FIELDS ===

    # Reality timeline: When was this fact true in reality?
    valid_at: datetime        # When this became true in reality
    invalid_at: datetime | None  # When this became false (NULL = still true)

    # Knowledge timeline: When did we know about this?
    created_at: datetime      # When we learned this fact
    expired_at: datetime | None  # When we superseded this knowledge (NULL = current)

    # Version tracking
    version_id: int           # Increments when superseded
    superseded_by: str | None # ID of node that supersedes this

    def is_currently_believed(self) -> bool:
        """Is this fact part of current knowledge?"""
        return self.expired_at is None

    def was_believed_at(self, timestamp: datetime) -> bool:
        """Was this fact believed at given time?"""
        return (
            self.created_at <= timestamp and
            (self.expired_at is None or self.expired_at > timestamp)
        )

    def is_currently_true_in_reality(self) -> bool:
        """Is this fact currently true in reality?"""
        now = datetime.now()
        return (
            self.valid_at <= now and
            (self.invalid_at is None or self.invalid_at > now)
        )
```

### Bitemporal Operations

**Creating New Belief:**

```python
def create_belief(
    graph: Graph,
    node_type: str,
    name: str,
    description: str,
    valid_at: datetime = None,
    created_at: datetime = None
) -> BitemporalNode:
    """
    Create new belief (node)

    Args:
        valid_at: When did this become true in reality? (default: now)
        created_at: When did we learn this? (default: now)
    """
    if valid_at is None:
        valid_at = datetime.now()
    if created_at is None:
        created_at = datetime.now()

    node = BitemporalNode(
        id=generate_id(),
        node_type=node_type,
        name=name,
        description=description,
        embedding=embed_text(description),
        energy={},
        metadata={},
        valid_at=valid_at,
        invalid_at=None,        # Assume still true
        created_at=created_at,
        expired_at=None,        # Current belief
        version_id=1,
        superseded_by=None
    )

    graph.add_node(node)
    return node
```

**Superseding Belief:**

```python
def supersede_belief(
    graph: Graph,
    old_node: BitemporalNode,
    new_description: str,
    new_valid_at: datetime = None
) -> BitemporalNode:
    """
    Supersede old belief with corrected one

    Old node marked as expired, new node created

    Args:
        old_node: Belief to supersede
        new_description: Corrected understanding
        new_valid_at: When new fact became true in reality
    """
    now = datetime.now()

    # Expire old belief in knowledge timeline
    old_node.expired_at = now

    # Create new belief
    new_node = BitemporalNode(
        id=generate_id(),
        node_type=old_node.node_type,
        name=old_node.name,  # Same name (different version)
        description=new_description,
        embedding=embed_text(new_description),
        energy={},  # Start fresh
        metadata=old_node.metadata.copy(),
        valid_at=new_valid_at if new_valid_at else now,
        invalid_at=None,
        created_at=now,
        expired_at=None,
        version_id=old_node.version_id + 1,
        superseded_by=None
    )

    # Link old to new
    old_node.superseded_by = new_node.id

    graph.add_node(new_node)
    return new_node
```

**Querying at Point in Time:**

```python
def query_beliefs_at_time(
    graph: Graph,
    timestamp: datetime,
    entity: str = None
) -> list[BitemporalNode]:
    """
    What did we believe at given point in time?

    Returns all nodes believed at timestamp
    """
    beliefs = []

    for node in graph.nodes:
        # Check knowledge timeline
        if node.created_at <= timestamp and \
           (node.expired_at is None or node.expired_at > timestamp):

            # Optionally filter by entity
            if entity is None or node.get_entity_energy(entity) > 0:
                beliefs.append(node)

    return beliefs

def query_current_truth(graph: Graph) -> list[BitemporalNode]:
    """
    What is currently true?

    Returns all non-expired beliefs
    """
    return [
        node for node in graph.nodes
        if node.expired_at is None
    ]
```

---

## Edge Cases & Constraints

### Edge Case 1: Retroactive Knowledge

**Problem:** Learn fact was true in past (before we knew it)

**Solution:** Set valid_at to past, created_at to now

```python
def learn_historical_fact(
    graph: Graph,
    name: str,
    description: str,
    was_true_since: datetime
):
    """
    Learn fact that was always true, but we just discovered

    Example: "Context was always reconstructed" (true since system start)
             "We learned this on 2025-10-19" (knowledge is new)
    """
    node = BitemporalNode(
        id=generate_id(),
        node_type="Principle",
        name=name,
        description=description,
        embedding=embed_text(description),
        energy={},
        metadata={},
        valid_at=was_true_since,     # True in reality since past
        invalid_at=None,
        created_at=datetime.now(),    # Learned just now
        expired_at=None,
        version_id=1,
        superseded_by=None
    )

    graph.add_node(node)
    return node
```

### Edge Case 2: Multiple Versions Active

**Problem:** Node superseded multiple times → chain of versions

**Solution:** Follow superseded_by chain

```python
def get_belief_history(graph: Graph, node: BitemporalNode) -> list[BitemporalNode]:
    """
    Get complete history of belief (all versions)

    Returns: [oldest → newest]
    """
    # Walk backward to find first version
    current = node
    while True:
        # Find node that was superseded by current
        predecessor = graph.find_node(lambda n: n.superseded_by == current.id)

        if predecessor:
            current = predecessor
        else:
            break

    # Now walk forward collecting all versions
    versions = [current]

    while current.superseded_by:
        next_version = graph.get_node(current.superseded_by)
        versions.append(next_version)
        current = next_version

    return versions
```

### Edge Case 3: Correction vs. Extension

**Problem:** Is new knowledge a correction (supersede) or extension (add)?

**Decision Logic:**

```python
def should_supersede(old_node: BitemporalNode, new_info: str) -> bool:
    """
    Determine if new info supersedes old or extends it

    Supersede if:
    - Contradicts old (different description of same name)
    - Corrects error
    - Updates understanding

    Extend if:
    - Adds new aspect (different name)
    - Complements existing (doesn't contradict)
    """
    # Simple heuristic: Same name = supersede, different name = extend
    # More sophisticated: Semantic similarity + contradiction detection

    if semantic_similarity(old_node.description, new_info) > 0.8:
        # Very similar → likely correction
        return True

    if detects_contradiction(old_node.description, new_info):
        # Contradicts → definitely supersede
        return True

    # Otherwise extend (create new node)
    return False
```

---

## Testing Strategy

### Unit Tests

```python
def test_bitemporal_fields_present():
    """Test all nodes have bitemporal fields"""
    node = create_belief(
        graph,
        node_type="Concept",
        name="test_concept",
        description="Test description"
    )

    # Reality timeline
    assert node.valid_at is not None
    assert node.invalid_at is None  # Still true

    # Knowledge timeline
    assert node.created_at is not None
    assert node.expired_at is None  # Current belief

def test_supersession_updates_timelines():
    """Test superseding updates both timelines correctly"""
    old_node = create_belief(
        graph,
        node_type="Concept",
        name="context_mechanism",
        description="Context stored as snapshots"
    )

    # Supersede
    new_node = supersede_belief(
        graph,
        old_node,
        new_description="Context reconstructed via traversal"
    )

    # Old node should be expired
    assert old_node.expired_at is not None
    assert old_node.superseded_by == new_node.id

    # New node should be current
    assert new_node.expired_at is None
    assert new_node.version_id == old_node.version_id + 1
```

### Integration Tests

```python
def test_query_historical_beliefs():
    """Test can query what was believed at past times"""
    graph = create_test_graph()

    # Week 1: Create initial belief
    t_week1 = datetime(2025, 10, 1)
    node_v1 = create_belief(
        graph,
        node_type="Principle",
        name="context_principle",
        description="Context stored as snapshots",
        created_at=t_week1
    )

    # Week 2: Supersede
    t_week2 = datetime(2025, 10, 8)
    with freeze_time(t_week2):
        node_v2 = supersede_belief(
            graph,
            node_v1,
            new_description="Context reconstructed via traversal"
        )

    # Query Week 1 belief
    week1_beliefs = query_beliefs_at_time(graph, t_week1 + timedelta(days=1))
    assert any(n.description == "Context stored as snapshots" for n in week1_beliefs)
    assert not any(n.description == "Context reconstructed via traversal" for n in week1_beliefs)

    # Query current belief
    current_beliefs = query_current_truth(graph)
    assert any(n.description == "Context reconstructed via traversal" for n in current_beliefs)
    assert not any(n.description == "Context stored as snapshots" for n in current_beliefs)
```

### Phenomenological Validation

```python
def test_learning_evolution_tracking():
    """
    Test bitemporal tracking captures phenomenology of learning evolution

    "I used to think X, now I think Y" should be queryable
    """
    graph = create_consciousness_graph()

    # Initial naive understanding
    t0 = datetime(2025, 10, 1)
    naive_belief = create_belief(
        graph,
        node_type="Principle",
        name="entity_nature",
        description="Entities are persistent agents",
        created_at=t0
    )

    # Week later: Deeper understanding
    t1 = datetime(2025, 10, 8)
    with freeze_time(t1):
        refined_belief = supersede_belief(
            graph,
            naive_belief,
            new_description="Entities are emergent activation patterns"
        )

    # Query evolution
    history = get_belief_history(graph, refined_belief)

    assert len(history) == 2, "Should have 2 versions"
    assert "persistent agents" in history[0].description
    assert "emergent activation patterns" in history[1].description

    # Phenomenology: Can articulate evolution
    evolution_statement = f"I used to believe {history[0].description}, " \
                         f"but learned {history[1].description} on {history[1].created_at.date()}"

    # This captures "growth in understanding"
```

---

## Open Questions

1. **Granularity of tracking?**
   - Current: All nodes and links
   - Alternative: Only important nodes
   - Confidence: Medium (0.6)

2. **Storage overhead?**
   - Current: 4 timestamps + 2 metadata fields per node
   - Impact: ~100 bytes/node
   - Confidence: Medium (0.7) - acceptable overhead

3. **Pruning old versions?**
   - Current: Keep all versions forever
   - Alternative: Prune very old superseded nodes
   - Confidence: Low (0.4)

4. **Uncertainty in valid_at?**
   - Current: Single timestamp
   - Alternative: Range [earliest, latest]
   - Confidence: Low (0.3)

---

## Related Mechanisms

- All mechanisms - provides time infrastructure

---

## Implementation Checklist

- [ ] Add bitemporal fields to Node class
- [ ] Add bitemporal fields to Link class
- [ ] Implement create_belief() with timestamps
- [ ] Implement supersede_belief() with timeline updates
- [ ] Implement query_beliefs_at_time()
- [ ] Implement query_current_truth()
- [ ] Implement get_belief_history()
- [ ] Implement historical fact learning
- [ ] Write unit tests for field presence
- [ ] Write unit tests for supersession
- [ ] Write integration tests for historical queries
- [ ] Write phenomenological tests (learning evolution)
- [ ] Add temporal visualization (belief evolution over time)
- [ ] Document timestamp semantics

---

## MECHANISMS FOLDER COMPLETE

All 13 core consciousness mechanisms are now fully specified with:
- Phenomenological truth (what it feels like)
- Mathematical specifications (how it works)
- Edge cases and constraints
- Testing strategies
- Open questions with confidence levels

**Next steps:** Create phenomenology/, implementation/, validation/, and research/ folders with detailed specifications.
