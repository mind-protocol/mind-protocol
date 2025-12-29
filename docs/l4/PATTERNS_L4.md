# PATTERNS: L4 Protocol

```
STATUS: IMPLEMENTED
PURPOSE: Core architectural rules for all L4 modules
UPDATED: 2024-12-29
```

---

## Core Rules

These rules apply to ALL L4 modules (Registry, Laws, Compliance).

| Rule | Pattern | Description |
|------|---------|-------------|
| **L4-1** | **L4 = Graph** | No API. L4 IS nodes in the graph. All access via graph traversal. |
| **L4-2** | **Membrane only** | Citizens/orgs never call L4 directly — only membrane. |
| **L4-3** | **Graph MCP calls** | Membrane uses `mind.graph.ops` — NO Cypher, graph physics does the work. |
| **L4-4** | **Skill + Procedure** | Every operation is a skill that executes a procedure via MCP — no exceptions. |

---

## L4-1: L4 = Graph

**L4 is not a service. L4 is data in the graph.**

```
Wrong:                           Right:
┌─────────┐                      ┌─────────┐
│ L4 API  │  ← separate service  │  Graph  │  ← L4 lives here
└─────────┘                      └─────────┘
     │                                │
     ▼                                │
┌─────────┐                      No separate L4 service
│  Graph  │
└─────────┘
```

**Why:**
- No service to maintain
- No API versioning
- No sync issues
- Single source of truth
- Graph IS the registry, laws, compliance

---

## L4-2: Membrane Only

**Citizens and orgs never talk to L4 directly.**

```
Citizen ──► Membrane ──► Graph
Org ──────► Membrane ──► Graph
              │
              └── All rules applied here
```

**Why:**
- Single security gate
- All validation in one place
- No bypass possible
- Audit trail at membrane
- Laws enforced before graph write

**Invariant:** If it didn't go through membrane, it doesn't exist.

---

## L4-3: Graph Query Interface

**Single interface. Declarative. Graph infers the action.**

```python
graph_query(
    queries=["...", "..."],  # Array of questions (WHAT)
    intent="..."             # String libre (WHY) → system infers type
)
```

**Why:**
- Single interface for everything (read, write, update, delete)
- Declarative — you say WHAT, graph figures out HOW
- Intent-driven — WHY helps system optimize
- No query injection (no Cypher, no SQL)
- Graph physics does the work

**Examples:**

```yaml
# READ
queries:
  - "What is the endpoint for org_123?"
  - "Is this org active?"
intent: "Get routing info for stimulus delivery"

# WRITE
queries:
  - "Create a new org named Acme"
  - "The org has endpoint wss://acme.com/ws"
intent: "Register new organization"

# UPDATE
queries:
  - "Change status of citizen_456 to suspended"
intent: "Suspend citizen for violation"

# DELETE
queries:
  - "Delete org_789 and all linked properties"
intent: "Remove org from registry"
```

**The graph infers operation type from intent + queries.**

---

## L4-4: Skill + Procedure

**Every L4 operation = Skill + Procedure + MCP. No exceptions.**

```
Request arrives
      │
      ▼
 Load Skill           ← skills/SKILL_*.md
      │
      ▼
 Execute Procedure    ← procedures/procedure_*.yaml
      │
      ▼
 Call Graph MCP       ← mind.graph.ops
      │
      ▼
 Return result
```

**Why:**
- Every operation is documented (skill)
- Every operation is reproducible (procedure)
- Every operation is traceable (MCP calls)
- No ad-hoc code paths
- Easy to audit, test, extend

**Structure:**

```
skills/
├── SKILL_register_citizen.md
├── SKILL_register_org.md
├── SKILL_verify_identity.md
└── ...

procedures/
├── procedure_register_citizen.yaml
├── procedure_register_org.yaml
├── procedure_verify_identity.yaml
└── ...
```

---

## Why This Architecture Is Solid

### Security by Design

```
Attack vector          Defense
─────────────────────────────────────
Direct L4 access       → Impossible (L4-2)
SQL/Cypher injection   → No queries (L4-3)
Bypass validation      → Single gate (L4-2)
Untraceable changes    → All via skills (L4-4)
```

### Simplicity

```
No API to maintain     (L4-1)
No Cypher to debug     (L4-3)
No cache to invalidate (L4-1)
No sync between systems (L4-1)
```

### Auditability

```
Every op is a skill    (L4-4)
Every op goes through membrane (L4-2)
Every op uses MCP      (L4-3)
→ Complete trace of everything
```

### Evolvability

```
Add new operation?
→ Create skill + procedure (L4-4)
→ Use same MCP ops (L4-3)
→ No new infrastructure
```

---

## Module-Specific Patterns

Each L4 module has additional patterns specific to its domain:

| Module | Patterns | Location |
|--------|----------|----------|
| Registry | P1-P5 (existence, JWT, hash) | `docs/l4/registry/PATTERNS_Registry.md` |
| Laws | Enforcement patterns | `docs/l4/laws/PATTERNS_Laws.md` |
| Compliance | Audit patterns | `docs/l4/compliance/PATTERNS_Compliance.md` |

---

## Graph Query Interface Reference

**Single function. Intent-driven. Graph physics does the work.**

```python
graph_query(
    queries: List[str],   # WHAT — questions or statements
    intent: str           # WHY — purpose, helps system optimize
) -> Result
```

| Action | Example Queries | Example Intent |
|--------|-----------------|----------------|
| Read | "What is the endpoint for org X?" | "Route stimulus" |
| Write | "Create org named Y with endpoint Z" | "Register new org" |
| Update | "Set status of citizen X to suspended" | "Enforce law violation" |
| Delete | "Remove org X and all linked nodes" | "Unregister org" |
| Validate | "Is X a valid wss:// URL?" | "Validate before create" |
| Check | "Does org X exist?" | "Prevent duplicate" |

**No Cypher. No SQL. No imperative operations.**

The graph infers:
- Operation type (read/write/update/delete) from queries + intent
- Node types from context
- Links to create/traverse from relationships mentioned
- Validation rules from intent

---

## Related

- `PATTERNS_Registry.md` — Registry-specific patterns
- `PATTERNS_Laws.md` — Laws enforcement patterns
- `.mind/PRINCIPLES.md` — Project-wide principles
- `.mind/FRAMEWORK.md` — Documentation framework
