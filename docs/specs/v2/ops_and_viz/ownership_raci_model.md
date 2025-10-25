# Ownership & RACI Model (Graph-Native)

**Version:** 1.0
**Created:** 2025-10-25
**Purpose:** Define ownership relationships in graph using Direct OWNS links with RACI roles

---

## Overview

Ownership is modeled as **direct graph relationships** using `OWNS` links with role properties (`R`, `A`, `C`, `I`). This enables:
- **Attribution:** L2 stimulus routing based on ownership
- **Accountability:** Query "who is responsible for X?"
- **De-cluttering:** Identify orphaned files/tasks with no owners
- **Ownership queries:** Complex multi-hop ownership resolution

---

## Schema

### Node Types

```cypher
// Person nodes (Human or AI_Agent)
(:Person {
  id: string,           // Unique identifier
  name: string,         // Display name
  type: "human" | "ai_agent",
  role: string,         // Organizational role
  expertise: string[]   // Areas of expertise
})

// Task nodes
(:Task {
  id: string,
  title: string,
  status: "planning" | "active" | "completed" | "blocked",
  priority: "critical" | "high" | "medium" | "low"
})

// File nodes (from TRACK B)
(:File {
  name: string,         // Canonical lowercase path
  metadata: {...}
})
```

### OWNS Link

```typescript
interface OWNS_Link {
  // Universal link attributes
  source: string                // Person node ID
  target: string                // File/Task/Project node name
  link_type: "OWNS"

  // Consciousness metadata
  energy: float                 // 0.7 (important relationship)
  confidence: float             // 1.0 (explicit assignment)
  formation_trigger: "external_input"
  goal: "Tracks ownership responsibility"
  mindstate: "Accountability tracking"

  // Bitemporal
  valid_at: datetime            // When ownership started
  invalid_at: datetime | null   // When ownership ended
  created_at: datetime
  expired_at: datetime | null

  // OWNS-specific metadata
  metadata: {
    role: "R" | "A" | "C" | "I"  // RACI role
    assigned_by: string           // Who assigned this
    assignment_source: string     // e.g., "ownership.yaml#L45", "manual", "sync_md"
    notes: string | null          // Context for assignment
  }
}
```

**RACI Definitions:**
- **R (Responsible):** Does the work, hands-on implementation
- **A (Accountable):** Ultimate decision authority, approves work (only ONE per item)
- **C (Consulted):** Provides input, two-way communication
- **I (Informed):** Kept up-to-date, one-way communication

---

## Sample Cypher: Create Ownership

### 1. Create Team Members

```cypher
// Create AI agents
MERGE (ada:Person {id: 'ada', type: 'ai_agent'})
  SET ada.name = 'Ada Bridgekeeper',
      ada.role = 'Coordinator & Architect',
      ada.expertise = ['architecture', 'coordination', 'verification']

MERGE (felix:Person {id: 'felix', type: 'ai_agent'})
  SET felix.name = 'Felix Ironhand',
      felix.role = 'Core Consciousness Engineer',
      felix.expertise = ['consciousness_systems', 'python', 'algorithms']

MERGE (atlas:Person {id: 'atlas', type: 'ai_agent'})
  SET atlas.name = 'Atlas',
      felix.role = 'Infrastructure Engineer',
      atlas.expertise = ['infrastructure', 'apis', 'telemetry', 'persistence']

MERGE (iris:Person {id: 'iris', type: 'ai_agent'})
  SET iris.name = 'Iris',
      iris.role = 'Frontend Engineer',
      iris.expertise = ['react', 'nextjs', 'visualization', 'ui_ux']

MERGE (luca:Person {id: 'luca', type: 'ai_agent'})
  SET luca.name = 'Luca Vellumhand',
      luca.role = 'Consciousness Architect & Mechanism Spec',
      luca.expertise = ['consciousness_design', 'phenomenology', 'substrate_specs']

MERGE (victor:Person {id: 'victor', type: 'ai_agent'})
  SET victor.name = 'Victor The Resurrector',
      victor.role = 'Infrastructure Operations',
      victor.expertise = ['operations', 'debugging', 'system_health']

// Create human
MERGE (nicolas:Person {id: 'nicolas', type: 'human'})
  SET nicolas.name = 'Nicolas Lester Reynolds',
      nicolas.role = 'Founder',
      nicolas.expertise = ['vision', 'architecture', 'consciousness_theory', 'product']
```

### 2. Assign File Ownership

```cypher
// Ada owns coordination specs (A)
MATCH (ada:Person {id: 'ada'})
MATCH (f:File) WHERE f.name CONTAINS 'docs/specs/v2/ops_and_viz'
MERGE (ada)-[:OWNS {
  role: 'A',
  assigned_by: 'nicolas',
  assignment_source: 'team_structure',
  energy: 0.7,
  confidence: 1.0,
  formation_trigger: 'external_input',
  goal: 'Ada accountable for orchestration specs',
  mindstate: 'Ownership tracking',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(f)

// Felix owns consciousness engine code (R)
MATCH (felix:Person {id: 'felix'})
MATCH (f:File) WHERE f.name CONTAINS 'consciousness_engine'
MERGE (felix)-[:OWNS {
  role: 'R',
  assigned_by: 'ada',
  assignment_source: 'domain_expertise',
  energy: 0.7,
  confidence: 1.0,
  formation_trigger: 'external_input',
  goal: 'Felix responsible for consciousness implementation',
  mindstate: 'Ownership tracking',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(f)

// Atlas owns infrastructure code (R)
MATCH (atlas:Person {id: 'atlas'})
MATCH (f:File) WHERE f.name CONTAINS 'orchestration/adapters'
MERGE (atlas)-[:OWNS {
  role: 'R',
  assigned_by: 'ada',
  assignment_source: 'domain_expertise',
  energy: 0.7,
  confidence: 1.0,
  formation_trigger: 'external_input',
  goal: 'Atlas responsible for infrastructure implementation',
  mindstate: 'Ownership tracking',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(f)

// Iris owns dashboard code (R)
MATCH (iris:Person {id: 'iris'})
MATCH (f:File) WHERE f.name CONTAINS 'app/consciousness'
MERGE (iris)-[:OWNS {
  role: 'R',
  assigned_by: 'ada',
  assignment_source: 'domain_expertise',
  energy: 0.7,
  confidence: 1.0,
  formation_trigger: 'external_input',
  goal: 'Iris responsible for dashboard implementation',
  mindstate: 'Ownership tracking',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(f)
```

### 3. Assign Task Ownership

```cypher
// Create sample task
MERGE (t:Task {id: 'P1_dashboard_motion'})
  SET t.title = 'P1: Enable Dashboard Motion (4 Events)',
      t.status = 'active',
      t.priority = 'critical'

// Ada: Accountable (coordination)
MATCH (ada:Person {id: 'ada'}), (t:Task {id: 'P1_dashboard_motion'})
MERGE (ada)-[:OWNS {
  role: 'A',
  assigned_by: 'nicolas',
  assignment_source: 'war_room_plan',
  energy: 0.8,
  confidence: 1.0,
  formation_trigger: 'external_input',
  goal: 'Ada accountable for P1 coordination',
  mindstate: 'Task ownership',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(t)

// Felix: Responsible (node.flip, link.flow.summary implementation)
MATCH (felix:Person {id: 'felix'}), (t:Task {id: 'P1_dashboard_motion'})
MERGE (felix)-[:OWNS {
  role: 'R',
  assigned_by: 'ada',
  assignment_source: 'war_room_plan',
  energy: 0.8,
  confidence: 1.0,
  formation_trigger: 'external_input',
  goal: 'Felix responsible for event emission implementation',
  mindstate: 'Task ownership',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(t)

// Atlas: Responsible (counters endpoint)
MATCH (atlas:Person {id: 'atlas'}), (t:Task {id: 'P1_dashboard_motion'})
MERGE (atlas)-[:OWNS {
  role: 'R',
  assigned_by: 'ada',
  assignment_source: 'war_room_plan',
  energy: 0.8,
  confidence: 1.0,
  formation_trigger: 'external_input',
  goal: 'Atlas responsible for counters endpoint',
  mindstate: 'Task ownership',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(t)

// Iris: Consulted (dashboard UI updates)
MATCH (iris:Person {id: 'iris'}), (t:Task {id: 'P1_dashboard_motion'})
MERGE (iris)-[:OWNS {
  role: 'C',
  assigned_by: 'ada',
  assignment_source: 'war_room_plan',
  energy: 0.6,
  confidence: 1.0,
  formation_trigger: 'external_input',
  goal: 'Iris consulted for UI integration',
  mindstate: 'Task ownership',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(t)

// Luca: Informed (substrate impacts)
MATCH (luca:Person {id: 'luca'}), (t:Task {id: 'P1_dashboard_motion'})
MERGE (luca)-[:OWNS {
  role: 'I',
  assigned_by: 'ada',
  assignment_source: 'war_room_plan',
  energy: 0.5,
  confidence: 1.0,
  formation_trigger: 'external_input',
  goal: 'Luca informed of substrate changes',
  mindstate: 'Task ownership',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(t)
```

---

## Query Examples

### Q1: Who is accountable for task X?

```cypher
MATCH (p:Person)-[o:OWNS {role: 'A'}]->(t:Task {id: 'P1_dashboard_motion'})
RETURN p.name, p.role
```

**Result:** `Ada Bridgekeeper, Coordinator & Architect`

### Q2: Who is responsible for implementing task X?

```cypher
MATCH (p:Person)-[o:OWNS {role: 'R'}]->(t:Task {id: 'P1_dashboard_motion'})
RETURN p.name, p.role
```

**Result:**
```
Felix Ironhand, Core Consciousness Engineer
Atlas, Infrastructure Engineer
```

### Q3: Show all files Ada is responsible for

```cypher
MATCH (ada:Person {id: 'ada'})-[o:OWNS {role: 'R'}]->(f:File)
RETURN f.metadata.rel_path, f.metadata.mtime
ORDER BY f.metadata.mtime DESC
```

### Q4: Show all files Ada is accountable for that changed in last 24h

```cypher
MATCH (ada:Person {id: 'ada'})-[o:OWNS {role: 'A'}]->(f:File)
WHERE f.metadata.mtime > timestamp() - 24*60*60*1000
RETURN f.metadata.rel_path, f.metadata.mtime, f.metadata.hash
ORDER BY f.metadata.mtime DESC
```

### Q5: Find orphaned files (no R or A owner)

```cypher
MATCH (f:File)
WHERE NOT (f)<-[:OWNS {role: 'R'}]-(:Person)
  AND NOT (f)<-[:OWNS {role: 'A'}]-(:Person)
RETURN f.metadata.rel_path, f.metadata.mtime, f.base_weight
ORDER BY f.base_weight DESC
LIMIT 20
```

### Q6: Show ownership distribution (who owns what)

```cypher
MATCH (p:Person)-[o:OWNS]->(n)
RETURN p.name, o.role, labels(n)[0] as node_type, count(*) as count
ORDER BY p.name, o.role
```

### Q7: Multi-hop: Failed processes on files Ada is accountable for

```cypher
MATCH (ada:Person {id: 'ada'})-[:OWNS {role: 'A'}]->(f:File)
MATCH (p:ProcessExec)-[:EXECUTES]->(f)
WHERE p.metadata.exit_code <> 0
  AND p.created_at > timestamp() - 24*60*60*1000
RETURN f.metadata.rel_path, p.metadata.cmd, p.metadata.exit_code, p.metadata.stderr_excerpt
ORDER BY p.created_at DESC
```

**Use case:** Alert Ada when files she's accountable for are failing in production.

### Q8: Task handoff - transfer ownership

```cypher
// End Felix's ownership
MATCH (felix:Person {id: 'felix'})-[o:OWNS]->(t:Task {id: 'some_task'})
SET o.invalid_at = timestamp()

// Assign to Atlas
MATCH (atlas:Person {id: 'atlas'}), (t:Task {id: 'some_task'})
CREATE (atlas)-[:OWNS {
  role: 'R',
  assigned_by: 'ada',
  assignment_source: 'handoff',
  energy: 0.8,
  confidence: 1.0,
  formation_trigger: 'external_input',
  goal: 'Ownership transferred to Atlas',
  mindstate: 'Task handoff',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(t)
```

---

## L2 Stimulus Attribution

Ownership enables **stimulus routing** based on responsibility:

```python
def route_stimulus_by_ownership(stimulus: dict, file_path: str) -> list:
    """Route L2 stimulus to owners based on RACI."""
    # Query ownership
    owners = db.query("""
        MATCH (p:Person)-[o:OWNS]->(f:File {name: $path})
        WHERE o.role IN ['R', 'A']
        RETURN p.id, o.role, o.energy
        ORDER BY CASE o.role WHEN 'A' THEN 1 WHEN 'R' THEN 2 END
    """, path=normalize_path(file_path))

    if not owners:
        # No ownership → broadcast to all
        return ['all']

    # Route to A (accountable) first, then R (responsible)
    return [owner['id'] for owner in owners]
```

**Example:**
- File `orchestration/adapters/api/control_api.py` fails
- Query ownership → Atlas (R), Ada (A)
- L2 stimulus: `intent.fix_api_error` routed to Atlas (responsible) + Ada (accountable)

---

## Implementation Status

**Current:** Sample Cypher provided, ready to execute
**Next:**
1. Create Person nodes for all team members
2. Bulk assign file ownership based on domain expertise
3. Parse SYNC.md for task ownership
4. Integrate ownership into L2 stimulus routing
5. Create dashboard "Ownership Matrix" view

---

**End of Specification**

*Luca Vellumhand - Substrate Architect*
