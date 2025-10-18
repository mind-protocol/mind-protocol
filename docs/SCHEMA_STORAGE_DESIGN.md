# Schema Storage in FalkorDB - Design

**Created:** 2025-10-17
**Author:** Felix "Ironhand"
**Purpose:** Store schema definitions IN the graph as queryable source of truth

---

## Problem Statement

**Current Gap:**
- Schema defined in Python + Markdown (external to graph)
- Mechanisms expect `detection_logic` metadata on links
- No way for mechanisms to query schema at runtime
- Schema changes require code deploys, not graph updates

**Desired State:**
- Schema stored IN FalkorDB as special nodes
- Mechanisms query schema to understand how to process types
- Schema changes = graph updates, not code changes
- Single source of truth accessible to all systems

---

## Design: Schema Nodes in FalkorDB

### Approach: Separate Schema Subgraph

**Schema nodes live in a dedicated subgraph:** `schema_registry`

**Benefits:**
- Isolated from consciousness data (clean separation)
- Shared across all citizen/org/ecosystem graphs
- Versioned (can track schema evolution)
- Queryable from any context

---

## Schema Node Structure

### 1. NodeTypeSchema Nodes

**Label:** `:NodeTypeSchema`

**Properties:**
```cypher
{
  type_name: string,           // "Memory", "Decision", "Post"
  level: string,                // "n1", "n2", "n3", "shared"
  category: string,             // "personal", "organizational", "evidence", "derived"
  description: string,
  required_attributes: [string], // ["timestamp", "participants"]
  optional_attributes: [string],
  mechanisms: [string],         // ["spreading_activation", "pattern_formation"]
  created_at: datetime,
  version: string               // "v2.0"
}
```

**Example:**
```cypher
CREATE (:NodeTypeSchema {
  type_name: "Memory",
  level: "n1",
  category: "personal",
  description: "Specific experience or moment",
  required_attributes: ["timestamp", "participants"],
  optional_attributes: ["emotion_vector", "arousal_level"],
  mechanisms: ["spreading_activation", "pattern_formation"],
  created_at: datetime(),
  version: "v2.0"
})
```

---

### 2. LinkTypeSchema Nodes

**Label:** `:LinkTypeSchema`

**Properties:**
```cypher
{
  type_name: string,              // "REQUIRES", "JUSTIFIES", "GROUNDS"
  level: string,                  // "shared", "n1_only", "n2_only", "n3_only"
  category: string,               // "dependency", "evidence", "structural"
  description: string,

  // Type-specific required fields
  required_attributes: [string],  // ["requirement_criticality", "temporal_relationship"]
  optional_attributes: [string],

  // Detection logic (THE KEY PART)
  detection_pattern: string,      // "staleness_detection", "dependency_verification"
  detection_logic: {
    pattern: string,              // "staleness_detection"
    threshold_field: string,      // "staleness_threshold"
    default_threshold: number,    // 2592000000 (30 days in ms)
    check_condition: string       // Cypher WHERE clause template
  },

  // Task generation
  task_template: string,          // "Verify requirement: {source} requires {target}"
  task_priority_formula: string,  // "urgency * criticality"

  // Mechanism mapping
  mechanisms: [string],           // ["staleness_detection", "task_routing"]

  created_at: datetime,
  version: string
}
```

**Example - REQUIRES:**
```cypher
CREATE (:LinkTypeSchema {
  type_name: "REQUIRES",
  level: "shared",
  category: "dependency",
  description: "Necessary conditions for something to work",

  required_attributes: ["requirement_criticality", "temporal_relationship"],
  optional_attributes: ["failure_mode", "verification_method"],

  detection_pattern: "dependency_verification",
  detection_logic: {
    pattern: "dependency_check",
    check_condition: "source.status != 'completed' OR target.status == 'blocked'"
  },

  task_template: "Verify requirement: {source.name} requires {target.name}",
  task_priority_formula: "CASE WHEN r.requirement_criticality = 'blocking' THEN 1.0 ELSE 0.5 END",

  mechanisms: ["dependency_verification", "task_routing"],
  created_at: datetime(),
  version: "v2.0"
})
```

**Example - DOCUMENTS:**
```cypher
CREATE (:LinkTypeSchema {
  type_name: "DOCUMENTS",
  level: "shared",
  category: "documentation",
  description: "Written record of implementation",

  required_attributes: [],
  optional_attributes: ["documentation_type"],

  detection_pattern: "staleness_detection",
  detection_logic: {
    pattern: "staleness_detection",
    threshold_field: "staleness_threshold",
    default_threshold: 2592000000,  // 30 days
    check_condition: "(timestamp() - r.last_modified) > COALESCE(r.staleness_threshold, 2592000000)"
  },

  task_template: "Update documentation: {source.name} for {target.name}",
  task_priority_formula: "0.3",  // Medium-low priority

  mechanisms: ["staleness_detection", "task_routing"],
  created_at: datetime(),
  version: "v2.0"
})
```

---

### 3. MechanismSchema Nodes

**Label:** `:MechanismSchema`

**Properties:**
```cypher
{
  mechanism_id: string,           // "staleness_detection"
  mechanism_name: string,         // "Staleness Detection"
  description: string,
  detection_patterns: [string],   // ["staleness_detection", "time_drift"]
  applicable_link_types: [string], // ["DOCUMENTS", "DOCUMENTED_BY", "ASSIGNED_TO"]
  cypher_template: string,        // Parameterized Cypher query
  tick_frequency_ms: number,      // 5000 (run every 5 seconds)
  created_at: datetime,
  version: string
}
```

**Example:**
```cypher
CREATE (:MechanismSchema {
  mechanism_id: "staleness_detection",
  mechanism_name: "Staleness Detection",
  description: "Detects when entities or links haven't been updated within their freshness window",
  detection_patterns: ["staleness_detection", "time_drift"],
  applicable_link_types: ["DOCUMENTS", "DOCUMENTED_BY", "ASSIGNED_TO", "MEASURES"],

  cypher_template: "
    MATCH (source)-[r:$link_type]->(target)
    WHERE r.detection_logic IS NOT NULL
      AND r.detection_logic.pattern = 'staleness_detection'
      AND (timestamp() - r.last_modified) > COALESCE(r.staleness_threshold, $default_threshold)
    RETURN source, r, target, r.task_template as template
  ",

  tick_frequency_ms: 5000,
  created_at: datetime(),
  version: "v2.0"
})
```

---

## How Mechanisms Use Schema

### Query Pattern:

**1. At startup, load applicable link type schemas:**
```cypher
// In staleness_detection mechanism
MATCH (schema:LinkTypeSchema)
WHERE schema.detection_pattern = 'staleness_detection'
RETURN schema.type_name, schema.detection_logic, schema.task_template
```

**Returns:**
```json
[
  {
    "type_name": "DOCUMENTS",
    "detection_logic": {
      "pattern": "staleness_detection",
      "default_threshold": 2592000000
    },
    "task_template": "Update documentation: {source.name} for {target.name}"
  },
  {
    "type_name": "ASSIGNED_TO",
    "detection_logic": {...},
    "task_template": "Review assignment: {target.name} to {source.name}"
  }
]
```

**2. For each link type, execute detection query:**
```cypher
MATCH (source)-[r:DOCUMENTS]->(target)
WHERE (timestamp() - r.last_modified) > COALESCE(r.staleness_threshold, 2592000000)
RETURN source, r, target
```

**3. Create tasks based on template:**
```cypher
CREATE (task:Task {
  description: "Update documentation: phase3_retrieval.md for consciousness_engine.py",
  created_by: "staleness_detection",
  created_at: timestamp(),
  priority: 0.3
})
```

---

## Implementation Plan

### Step 1: Create Schema Ingestion Script

**File:** `tools/ingest_schema_to_falkordb.py`

```python
from falkordb import FalkorDB
import json

# Parse UNIFIED_SCHEMA_REFERENCE.md
# Extract node types, link types, mechanisms
# Create schema nodes in schema_registry graph

db = FalkorDB(host='localhost', port=6379)
g = db.select_graph("schema_registry")

# Ingest node type schemas
for node_type in node_types:
    g.query("""
        MERGE (s:NodeTypeSchema {type_name: $type_name})
        SET s.level = $level,
            s.category = $category,
            s.description = $description,
            s.required_attributes = $required_attributes,
            s.optional_attributes = $optional_attributes,
            s.mechanisms = $mechanisms,
            s.created_at = datetime(),
            s.version = 'v2.0'
    """, params=node_type)

# Ingest link type schemas
for link_type in link_types:
    g.query("""
        MERGE (s:LinkTypeSchema {type_name: $type_name})
        SET s.level = $level,
            s.category = $category,
            s.description = $description,
            s.detection_pattern = $detection_pattern,
            s.detection_logic = $detection_logic,
            s.task_template = $task_template,
            s.mechanisms = $mechanisms,
            s.created_at = datetime(),
            s.version = 'v2.0'
    """, params=link_type)

# Ingest mechanism schemas
for mechanism in mechanisms:
    g.query("""
        MERGE (m:MechanismSchema {mechanism_id: $mechanism_id})
        SET m.mechanism_name = $mechanism_name,
            m.description = $description,
            m.detection_patterns = $detection_patterns,
            m.applicable_link_types = $applicable_link_types,
            m.cypher_template = $cypher_template,
            m.tick_frequency_ms = $tick_frequency_ms,
            m.created_at = datetime(),
            m.version = 'v2.0'
    """, params=mechanism)
```

---

### Step 2: Update Consciousness Engine

**File:** `orchestration/consciousness_engine.py`

**Before (hardcoded):**
```python
def staleness_detection(g, tick):
    result = g.query("""
        MATCH (source)-[r:DOCUMENTS]->(target)
        WHERE (timestamp() - r.last_modified) > 2592000000
        RETURN source, r, target
    """)
```

**After (schema-driven):**
```python
def staleness_detection(g, tick):
    # Query schema for applicable link types
    schema_result = g.query("""
        MATCH (schema:LinkTypeSchema)
        WHERE schema.detection_pattern = 'staleness_detection'
        RETURN schema.type_name as link_type,
               schema.detection_logic as logic,
               schema.task_template as template
    """)

    for schema_row in schema_result.result_set:
        link_type = schema_row[0]
        logic = schema_row[1]
        template = schema_row[2]

        # Execute detection query for this link type
        detection_result = g.query(f"""
            MATCH (source)-[r:{link_type}]->(target)
            WHERE (timestamp() - r.last_modified) > {logic['default_threshold']}
            RETURN source, r, target
        """)

        # Create tasks from template
        for row in detection_result.result_set:
            create_task(g, template, row, logic)
```

---

### Step 3: Verify Schema Query Performance

**Test query:**
```cypher
// From consciousness_engine.py, query schema_registry
MATCH (schema:LinkTypeSchema)
WHERE schema.detection_pattern = 'staleness_detection'
RETURN schema
```

**Expected latency:** <1ms (schema registry is tiny)

---

## Schema Versioning

**When schema evolves:**

1. Create new schema nodes with incremented version:
```cypher
CREATE (:LinkTypeSchema {
  type_name: "REQUIRES",
  version: "v2.1",  // Incremented
  detection_logic: {...},  // Updated logic
  created_at: datetime()
})
```

2. Mechanisms query latest version by default:
```cypher
MATCH (schema:LinkTypeSchema)
WHERE schema.type_name = 'REQUIRES'
RETURN schema
ORDER BY schema.version DESC
LIMIT 1
```

3. Historical queries can request specific version:
```cypher
MATCH (schema:LinkTypeSchema)
WHERE schema.type_name = 'REQUIRES'
  AND schema.version = 'v2.0'
RETURN schema
```

---

## Benefits

**1. Mechanisms become generic:**
- No hardcoded link types in mechanism code
- One `staleness_detection()` function handles ALL staleness-checked link types
- Schema defines behavior, not code

**2. Schema evolution without code changes:**
- Add new link type → update schema_registry graph
- Change detection threshold → update LinkTypeSchema node
- No Python code deploy needed

**3. Queryable by all systems:**
- Visualization server can show which mechanisms apply to which types
- External tools can introspect schema
- LLMs can query schema to understand system

**4. Self-documenting:**
- Schema IS the documentation (stored in graph)
- No drift between code and docs
- UNIFIED_SCHEMA_REFERENCE.md becomes VIEW on schema_registry

---

## Migration Path

**Phase 1: Parallel operation**
- Create schema_registry graph
- Ingest schema from UNIFIED_SCHEMA_REFERENCE.md
- Mechanisms still use hardcoded logic (no breaking changes)

**Phase 2: Schema-driven mechanisms**
- Update one mechanism (e.g., staleness_detection) to query schema
- Verify it produces same results as hardcoded version
- Repeat for remaining mechanisms

**Phase 3: Deprecate hardcoded logic**
- Remove hardcoded link type lists from consciousness_engine.py
- All mechanisms now query schema_registry
- UNIFIED_SCHEMA_REFERENCE.md becomes generated from schema_registry

---

## Next Steps

1. ✅ Design complete (this document)
2. ⏳ Implement `tools/ingest_schema_to_falkordb.py`
3. ⏳ Create schema_registry graph with initial data
4. ⏳ Update ONE mechanism (staleness_detection) to be schema-driven
5. ⏳ Test and verify
6. ⏳ Roll out to remaining mechanisms

---

**Author:** Felix "Ironhand"
**Status:** Design complete, ready for implementation
**Priority:** High - unblocks mechanism execution

*"Schema isn't documentation—it's executable truth stored in the graph."*
