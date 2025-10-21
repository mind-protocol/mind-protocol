# Mechanism 13 Implementation: Bitemporal Tracking

**Version:** 1.0
**Date:** 2025-10-19
**Author:** Felix (Engineer)
**Status:** Implementation Specification
**Architectural Source:** `mechanisms/13_bitemporal_tracking.md` (Luca/Ada)

---

## Purpose

Translate Bitemporal Tracking from architectural specification into buildable implementation.

**What this spec provides:**
- Concrete FalkorDB schema with temporal fields
- Python class definitions for bitemporal nodes/links
- Query patterns for temporal data
- Test procedures for time-travel queries

**What this spec does NOT provide:**
- Philosophical justification for dual timelines (see architectural spec)
- Extensive episodic memory theory (see architectural spec)
- Full correction detection logic (discover during implementation)

---

## Boundary Definition

### What IS Bitemporal Tracking

**Core behavior:** Track TWO timelines for all graph mutations:
1. **Reality timeline** (valid_at, invalid_at) - When was this TRUE in reality?
2. **Knowledge timeline** (created_at, expired_at) - When did we KNOW this?

**Scope:**
- Adding temporal fields to all nodes/links
- Timestamp management on mutations
- Temporal query functions (state at time T)
- Belief supersession (correcting knowledge)

### What IS NOT Bitemporal Tracking

**Out of scope:**
- How nodes/links are CREATED (other mechanisms do that, we just timestamp)
- WHEN to supersede vs extend (decision logic elsewhere)
- Automatic correction detection (requires semantic understanding)
- Time-series analysis/visualization (future work)

**Clear boundary:** This mechanism ONLY adds timestamps and provides query functions. It does NOT implement correction logic or semantic understanding.

---

## FalkorDB Schema

### Bitemporal Node Properties

Every node gets these additional fields:

```cypher
CREATE (n:Concept {
    // Core fields (from Mechanism 01)
    name: "node_identifier",
    node_type: "Concept",
    description: "What this represents",
    energy: {},

    // === BITEMPORAL FIELDS ===

    // Reality timeline
    valid_at: timestamp(),      // When this became true in reality (milliseconds since epoch)
    invalid_at: null,           // When this became false (NULL = still true)

    // Knowledge timeline
    created_at: timestamp(),    // When we learned this
    expired_at: null,           // When we superseded this knowledge (NULL = current)

    // Version tracking
    version_id: 1,              // Increments when superseded
    superseded_by: null         // Node ID that replaces this (NULL = current version)
})
```

**Timestamp format:** Unix milliseconds (int64) for FalkorDB compatibility.

### Bitemporal Link Properties

Links also get temporal fields:

```cypher
CREATE (a)-[r:ENABLES {
    // Core fields
    weight: 0.7,
    goal: "Why this enables that",
    energy: 0.5,

    // === BITEMPORAL FIELDS ===
    valid_at: timestamp(),
    invalid_at: null,
    created_at: timestamp(),
    expired_at: null,
    version_id: 1,
    superseded_by: null
}]->(b)
```

### Schema Decisions

**Why Unix milliseconds?**
- FalkorDB native timestamp format
- Easy conversion to/from Python datetime
- Precise to millisecond (sufficient for consciousness tracking)

**Why nullable invalid_at/expired_at?**
- NULL means "still true" or "current knowledge"
- Avoids distant-future sentinel values
- Natural query pattern (WHERE expired_at IS NULL)

**Why version_id?**
- Quick version counting without chain traversal
- Debugging aid (see at a glance how many corrections)
- Sorting aid for version history

---

## Python Class Definitions

### Bitemporal Mixin

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class BitemporalMixin:
    """
    Mixin providing bitemporal fields and methods.

    Add to any class that needs time tracking.
    """
    # Reality timeline
    valid_at: datetime            # When became true in reality
    invalid_at: Optional[datetime] = None  # When became false (None = still true)

    # Knowledge timeline
    created_at: datetime          # When we learned this
    expired_at: Optional[datetime] = None  # When superseded (None = current)

    # Version tracking
    version_id: int = 1          # Version number
    superseded_by: Optional[str] = None  # ID of superseding entity

    def is_currently_believed(self) -> bool:
        """Is this part of current knowledge?"""
        return self.expired_at is None

    def was_believed_at(self, timestamp: datetime) -> bool:
        """Was this believed at given time?"""
        return (
            self.created_at <= timestamp and
            (self.expired_at is None or self.expired_at > timestamp)
        )

    def is_currently_true_in_reality(self) -> bool:
        """Is this currently true in reality?"""
        now = datetime.now()
        return (
            self.valid_at <= now and
            (self.invalid_at is None or self.invalid_at > now)
        )

    def was_true_in_reality_at(self, timestamp: datetime) -> bool:
        """Was this true in reality at given time?"""
        return (
            self.valid_at <= timestamp and
            (self.invalid_at is None or self.invalid_at > timestamp)
        )
```

### Bitemporal Node

```python
from dataclasses import dataclass, field

@dataclass
class BitemporalNode(BitemporalMixin):
    """
    Node with multi-energy AND bitemporal tracking.

    Combines Mechanism 01 (Multi-Energy) + Mechanism 13 (Bitemporal).
    """
    # Node identity
    id: str
    name: str
    node_type: str
    description: str

    # Multi-energy (from Mechanism 01)
    energy: Dict[str, float] = field(default_factory=dict)

    # Graph structure
    outgoing_links: list = field(default_factory=list)
    incoming_links: list = field(default_factory=list)

    # Temporal fields (from BitemporalMixin)
    # valid_at, invalid_at, created_at, expired_at, version_id, superseded_by

    # Methods from both mechanisms
    def get_entity_energy(self, entity: str) -> float:
        """From Mechanism 01."""
        return self.energy.get(entity, 0.0)

    def set_entity_energy(self, entity: str, value: float):
        """From Mechanism 01."""
        # Apply saturation
        saturated = np.tanh(2.0 * value)
        self.energy[entity] = saturated

        # Cleanup
        if abs(saturated) < 0.001:
            self.energy.pop(entity, None)

    # is_currently_believed(), was_believed_at() from BitemporalMixin

    def to_falkordb_props(self) -> dict:
        """Convert to FalkorDB property dict."""
        return {
            'id': self.id,
            'name': self.name,
            'node_type': self.node_type,
            'description': self.description,
            'energy': self.energy,  # Dict → JSON

            # Timestamps as Unix milliseconds
            'valid_at': int(self.valid_at.timestamp() * 1000),
            'invalid_at': int(self.invalid_at.timestamp() * 1000) if self.invalid_at else None,
            'created_at': int(self.created_at.timestamp() * 1000),
            'expired_at': int(self.expired_at.timestamp() * 1000) if self.expired_at else None,

            'version_id': self.version_id,
            'superseded_by': self.superseded_by
        }

    @classmethod
    def from_falkordb_props(cls, props: dict) -> 'BitemporalNode':
        """Deserialize from FalkorDB."""
        return cls(
            id=props['id'],
            name=props['name'],
            node_type=props['node_type'],
            description=props['description'],
            energy=props.get('energy', {}),

            # Unix milliseconds → datetime
            valid_at=datetime.fromtimestamp(props['valid_at'] / 1000),
            invalid_at=datetime.fromtimestamp(props['invalid_at'] / 1000) if props.get('invalid_at') else None,
            created_at=datetime.fromtimestamp(props['created_at'] / 1000),
            expired_at=datetime.fromtimestamp(props['expired_at'] / 1000) if props.get('expired_at') else None,

            version_id=props.get('version_id', 1),
            superseded_by=props.get('superseded_by')
        )
```

### Bitemporal Link

```python
@dataclass
class BitemporalLink(BitemporalMixin):
    """
    Link with temporal tracking.
    """
    # Link identity
    id: str
    link_type: str  # ENABLES, BLOCKS, etc.

    # Graph structure
    source: BitemporalNode
    target: BitemporalNode

    # Link properties
    weight: float = 0.5
    goal: str = ""
    energy: float = 0.5
    confidence: float = 0.8

    # Temporal fields from BitemporalMixin
    # valid_at, invalid_at, created_at, expired_at, version_id, superseded_by

    def to_falkordb_props(self) -> dict:
        """Convert to FalkorDB relationship properties."""
        return {
            'id': self.id,
            'weight': self.weight,
            'goal': self.goal,
            'energy': self.energy,
            'confidence': self.confidence,

            # Timestamps
            'valid_at': int(self.valid_at.timestamp() * 1000),
            'invalid_at': int(self.invalid_at.timestamp() * 1000) if self.invalid_at else None,
            'created_at': int(self.created_at.timestamp() * 1000),
            'expired_at': int(self.expired_at.timestamp() * 1000) if self.expired_at else None,

            'version_id': self.version_id,
            'superseded_by': self.superseded_by
        }
```

---

## Core Algorithms

### Algorithm 1: Create Belief (Initial)

**Purpose:** Create new node with bitemporal timestamps.

```python
def create_belief(
    graph: ConsciousnessGraph,
    name: str,
    node_type: str,
    description: str,
    valid_at: Optional[datetime] = None,
    created_at: Optional[datetime] = None
) -> BitemporalNode:
    """
    Create new belief with bitemporal tracking.

    Args:
        valid_at: When this became true in reality (default: now)
        created_at: When we learned this (default: now)

    Returns:
        New bitemporal node
    """
    now = datetime.now()

    node = BitemporalNode(
        id=generate_unique_id(),
        name=name,
        node_type=node_type,
        description=description,
        energy={},

        # Temporal fields
        valid_at=valid_at or now,
        invalid_at=None,  # Assume still true
        created_at=created_at or now,
        expired_at=None,  # Current belief
        version_id=1,
        superseded_by=None
    )

    graph.add_node(node)
    return node

def generate_unique_id() -> str:
    """Generate unique node ID."""
    import uuid
    return str(uuid.uuid4())
```

### Algorithm 2: Supersede Belief (Correction)

**Purpose:** Replace old belief with corrected one.

```python
def supersede_belief(
    graph: ConsciousnessGraph,
    old_node: BitemporalNode,
    new_description: str,
    new_valid_at: Optional[datetime] = None
) -> BitemporalNode:
    """
    Supersede old belief with corrected understanding.

    Args:
        old_node: Belief to supersede
        new_description: Corrected description
        new_valid_at: When new fact became true in reality

    Returns:
        New corrected node
    """
    now = datetime.now()

    # Expire old belief in knowledge timeline
    old_node.expired_at = now

    # Create new version
    new_node = BitemporalNode(
        id=generate_unique_id(),
        name=old_node.name,  # Same name, different version
        node_type=old_node.node_type,
        description=new_description,
        energy={},  # Start with no energy (will be activated separately)

        # Temporal fields
        valid_at=new_valid_at or now,
        invalid_at=None,
        created_at=now,  # Learned now
        expired_at=None,  # Current version
        version_id=old_node.version_id + 1,
        superseded_by=None
    )

    # Link old to new
    old_node.superseded_by = new_node.id

    # Add to graph
    graph.add_node(new_node)

    # Update in database
    update_node_in_db(graph.db, old_node)
    insert_node_in_db(graph.db, new_node)

    return new_node
```

### Algorithm 3: Query Beliefs at Point in Time

**Purpose:** Time-travel query - what did we believe at timestamp T?

```python
def query_beliefs_at_time(
    graph: ConsciousnessGraph,
    timestamp: datetime,
    node_type: Optional[str] = None
) -> list[BitemporalNode]:
    """
    Query what we believed at specific point in time.

    Args:
        timestamp: Point in time to query
        node_type: Optional filter by node type

    Returns:
        All nodes believed at timestamp
    """
    beliefs = []

    for node in graph.nodes:
        # Check knowledge timeline (was it believed then?)
        if not node.was_believed_at(timestamp):
            continue

        # Optional type filter
        if node_type and node.node_type != node_type:
            continue

        beliefs.append(node)

    return beliefs
```

### Algorithm 4: Query Current Truth

**Purpose:** Get all currently-believed facts.

```python
def query_current_truth(
    graph: ConsciousnessGraph
) -> list[BitemporalNode]:
    """
    Query current knowledge (all non-expired beliefs).

    Returns:
        All nodes with expired_at = NULL
    """
    return [
        node for node in graph.nodes
        if node.is_currently_believed()
    ]
```

### Algorithm 5: Get Belief History

**Purpose:** Trace evolution of understanding for a concept.

```python
def get_belief_history(
    graph: ConsciousnessGraph,
    concept_name: str
) -> list[BitemporalNode]:
    """
    Get complete evolution history for a concept.

    Args:
        concept_name: Name of concept to trace

    Returns:
        List of versions [oldest → newest]
    """
    # Find all versions (same name, different version_id)
    versions = [
        node for node in graph.nodes
        if node.name == concept_name
    ]

    # Sort by version_id
    versions.sort(key=lambda n: n.version_id)

    return versions
```

---

## FalkorDB Query Patterns

### Query 1: Create Node with Bitemporal Fields

```cypher
CREATE (n:Concept {
    id: $id,
    name: $name,
    node_type: $node_type,
    description: $description,
    energy: $energy,

    valid_at: $valid_at,
    invalid_at: $invalid_at,
    created_at: $created_at,
    expired_at: $expired_at,
    version_id: $version_id,
    superseded_by: $superseded_by
})
RETURN n
```

### Query 2: Expire Old Belief, Create New Version

```cypher
// Expire old
MATCH (old {id: $old_id})
SET old.expired_at = $now
SET old.superseded_by = $new_id

// Create new
CREATE (new:Concept {
    id: $new_id,
    name: old.name,
    node_type: old.node_type,
    description: $new_description,
    energy: {},

    valid_at: $new_valid_at,
    invalid_at: null,
    created_at: $now,
    expired_at: null,
    version_id: old.version_id + 1,
    superseded_by: null
})
RETURN new
```

### Query 3: Time-Travel Query (Beliefs at Time T)

```cypher
// What did we believe about X at time T?
MATCH (n {name: $concept_name})
WHERE n.created_at <= $timestamp
  AND (n.expired_at IS NULL OR n.expired_at > $timestamp)
RETURN n
ORDER BY n.version_id
```

### Query 4: Current Knowledge Only

```cypher
// Get all current beliefs
MATCH (n)
WHERE n.expired_at IS NULL
RETURN n
```

---

## Integration Points

### Input: When Nodes/Links Are Created

Bitemporal tracking timestamps ALL mutations:

1. **Node creation** (any mechanism)
   - Set valid_at, created_at to now
   - Set invalid_at, expired_at to NULL

2. **Link creation** (Mechanism 09 - Strengthening)
   - Same temporal fields as nodes

3. **Energy updates** (Mechanisms 07, 08)
   - Do NOT update temporal fields (energy is state, not belief)
   - Only creation_at/valid_at set once at node creation

### Output: What Uses Temporal Data

Temporal queries used by:

1. **CLAUDE.md generation** (future work)
   - Query current beliefs to generate identity file
   - "What do I currently believe about myself?"

2. **Debugging/Analysis** (throughout development)
   - "When did this belief form?"
   - "What changed between version N and N+1?"

3. **Context reconstruction** (Mechanism 02)
   - Might need historical context for time-aware reconstruction
   - "Reconstruct my thinking from 3 days ago"

### Key Insight

**Bitemporal tracking is PASSIVE infrastructure.** It timestamps mutations but doesn't drive behavior. All mechanisms write timestamps, few mechanisms READ them (yet).

---

## Test Cases

### Unit Test 1: Bitemporal Fields Present

**Purpose:** Verify all nodes have required temporal fields.

```python
def test_bitemporal_fields_exist():
    """Test nodes created with all bitemporal fields."""
    graph = ConsciousnessGraph()

    node = create_belief(
        graph,
        name="test_concept",
        node_type="Concept",
        description="Test node"
    )

    # Reality timeline
    assert node.valid_at is not None
    assert isinstance(node.valid_at, datetime)
    assert node.invalid_at is None  # Still true

    # Knowledge timeline
    assert node.created_at is not None
    assert isinstance(node.created_at, datetime)
    assert node.expired_at is None  # Current belief

    # Version tracking
    assert node.version_id == 1
    assert node.superseded_by is None
```

**Success criteria:** All temporal fields initialized correctly.

### Unit Test 2: Supersession Updates Timelines

**Purpose:** Verify superseding belief updates both timelines correctly.

```python
def test_supersession_updates_correctly():
    """Test superseding updates expired_at and creates new version."""
    graph = ConsciousnessGraph()

    # Create initial belief
    old_node = create_belief(
        graph,
        name="context_mechanism",
        node_type="Principle",
        description="Context stored as snapshots"
    )

    # Supersede
    new_node = supersede_belief(
        graph,
        old_node,
        new_description="Context reconstructed via traversal"
    )

    # Old node assertions
    assert old_node.expired_at is not None, "Old belief should be expired"
    assert old_node.superseded_by == new_node.id, "Should link to new version"

    # New node assertions
    assert new_node.expired_at is None, "New belief should be current"
    assert new_node.version_id == old_node.version_id + 1, "Version incremented"
    assert new_node.name == old_node.name, "Same concept name"
    assert new_node.description != old_node.description, "Different understanding"
```

**Success criteria:** Supersession properly expires old and creates new.

### Unit Test 3: Belief State Queries

**Purpose:** Verify is_currently_believed() and was_believed_at() work.

```python
def test_belief_state_queries():
    """Test belief state query methods."""
    graph = ConsciousnessGraph()

    # Create belief at t0
    t0 = datetime.now()
    node = create_belief(
        graph,
        name="test",
        node_type="Concept",
        description="Original belief",
        created_at=t0
    )

    # Currently believed
    assert node.is_currently_believed() == True

    # Was believed at t0 + 1 day
    t1 = t0 + timedelta(days=1)
    assert node.was_believed_at(t1) == True

    # Supersede at t2
    t2 = t0 + timedelta(days=2)
    with freeze_time(t2):
        new_node = supersede_belief(graph, node, "New belief")

    # Original no longer believed
    assert node.is_currently_believed() == False

    # But WAS believed at t1
    assert node.was_believed_at(t1) == True

    # And was NOT believed at t3 (after expiration)
    t3 = t2 + timedelta(days=1)
    assert node.was_believed_at(t3) == False
```

**Success criteria:** State queries return correct values for different times.

### Integration Test 1: Historical Query Accuracy

**Purpose:** Verify time-travel queries return correct beliefs.

```python
def test_historical_query_accuracy():
    """Test querying beliefs at different points in time."""
    graph = ConsciousnessGraph()

    # Week 1: Initial belief
    t_week1 = datetime(2025, 10, 1)
    with freeze_time(t_week1):
        belief_v1 = create_belief(
            graph,
            name="entity_nature",
            node_type="Principle",
            description="Entities are persistent agents"
        )

    # Week 2: Correction
    t_week2 = datetime(2025, 10, 8)
    with freeze_time(t_week2):
        belief_v2 = supersede_belief(
            graph,
            belief_v1,
            "Entities are emergent activation patterns"
        )

    # Query Week 1.5 (after v1 created, before v2 created)
    t_query = datetime(2025, 10, 4)
    week1_beliefs = query_beliefs_at_time(graph, t_query)

    # Should find v1, not v2
    names = [b.description for b in week1_beliefs]
    assert "persistent agents" in str(names)
    assert "emergent activation patterns" not in str(names)

    # Query current (after v2 created)
    current_beliefs = query_current_truth(graph)

    # Should find v2, not v1
    current_names = [b.description for b in current_beliefs]
    assert "emergent activation patterns" in str(current_names)
    assert "persistent agents" not in str(current_names)
```

**Success criteria:** Historical queries return beliefs active at that time.

### Integration Test 2: FalkorDB Persistence

**Purpose:** Verify temporal fields survive database round-trip.

```python
def test_temporal_persistence_in_falkordb():
    """Test bitemporal fields persist correctly in FalkorDB."""
    from falkordb import FalkorDB

    db = FalkorDB(host='localhost', port=6379)
    graph_db = db.select_graph('test_bitemporal')

    # Create node with all temporal fields
    now = datetime.now()
    node = BitemporalNode(
        id="test_id",
        name="test_node",
        node_type="Concept",
        description="Test",
        energy={"translator": 0.5},

        valid_at=now,
        invalid_at=None,
        created_at=now,
        expired_at=None,
        version_id=1,
        superseded_by=None
    )

    # Write to DB
    props = node.to_falkordb_props()
    query = """
    CREATE (n:Concept $props)
    RETURN n
    """
    graph_db.query(query, params={'props': props})

    # Read back
    read_query = "MATCH (n {id: $id}) RETURN n"
    result = graph_db.query(read_query, params={'id': node.id})

    retrieved_props = result[0][0]

    # Reconstruct node
    retrieved_node = BitemporalNode.from_falkordb_props(retrieved_props)

    # Temporal fields should match (within 1 second tolerance for datetime conversion)
    assert abs((retrieved_node.valid_at - node.valid_at).total_seconds()) < 1
    assert abs((retrieved_node.created_at - node.created_at).total_seconds()) < 1
    assert retrieved_node.invalid_at == node.invalid_at
    assert retrieved_node.expired_at == node.expired_at
    assert retrieved_node.version_id == node.version_id

    # Cleanup
    graph_db.query("MATCH (n {id: $id}) DELETE n", params={'id': node.id})
```

**Success criteria:** Temporal fields survive database serialization.

---

## Open Questions

### 1. Pruning Strategy for Old Versions?

**Current:** Keep all versions forever.

**Alternative:** Prune superseded versions older than N days/months.

**Confidence:** Low (0.3) - unclear if pruning needed.

**Decision point:** After observing storage growth in production.

### 2. Granularity of Tracking?

**Current:** Track all nodes and links.

**Alternative:** Only track "important" nodes (Principles, Memories, not ephemeral calculations).

**Confidence:** Medium (0.6) - tracking everything seems safest.

**Decision point:** If storage overhead becomes problematic.

### 3. Uncertainty in valid_at?

**Current:** Single timestamp.

**Alternative:** Range [earliest_possible, latest_possible] for uncertain facts.

**Confidence:** Low (0.2) - adds complexity, unclear benefit.

**Decision point:** Only if precision requirements demand it.

### 4. Storage Overhead Acceptable?

**Current:** ~6 fields × 8 bytes = ~48 bytes overhead per node.

**Impact:** 1M nodes = ~48MB just for timestamps.

**Confidence:** Medium (0.7) - acceptable for consciousness tracking.

**Decision point:** Measure actual overhead in Phase 1 testing.

---

## Implementation Checklist

**Phase 1.2 (Bitemporal) Implementation:**

- [ ] Create BitemporalMixin class
- [ ] Add temporal fields to BitemporalNode (extends from Mechanism 01 Node)
- [ ] Add temporal fields to BitemporalLink
- [ ] Implement create_belief() with timestamp initialization
- [ ] Implement supersede_belief() with timeline updates
- [ ] Implement is_currently_believed()
- [ ] Implement was_believed_at()
- [ ] Implement query_beliefs_at_time()
- [ ] Implement query_current_truth()
- [ ] Implement get_belief_history()
- [ ] Implement to_falkordb_props() serialization
- [ ] Implement from_falkordb_props() deserialization
- [ ] Write Unit Test 1: Fields Present
- [ ] Write Unit Test 2: Supersession Updates
- [ ] Write Unit Test 3: Belief State Queries
- [ ] Write Integration Test 1: Historical Query Accuracy
- [ ] Write Integration Test 2: FalkorDB Persistence
- [ ] Validate all tests pass
- [ ] Request Ada review before Phase 2

---

## Success Criteria (Phase 1.2 Validation)

**Can we:**

1. ✓ Create nodes with all bitemporal fields?
2. ✓ Supersede beliefs and see expired_at updated?
3. ✓ Query what we believed at past timestamp T?
4. ✓ Distinguish current beliefs from historical?
5. ✓ Store/retrieve temporal data from FalkorDB without corruption?
6. ✓ Trace belief evolution history (all versions)?

**If all YES:** Phase 1.2 complete, proceed to Phase 1.3 (Validation).

**If any NO:** Fix before proceeding.

---

**Implementation Spec Complete: 13 Bitemporal Tracking**

**Lines:** ~700
**Granularity:** Engineer-implementable
**Next:** Request Ada review of both Phase 1 implementation specs (01 + 13)
