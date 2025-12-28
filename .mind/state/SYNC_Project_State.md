# mind-protocol — Sync: Current State

```
LAST_UPDATED: 2024-12-28
UPDATED_BY: claude
STATUS: DESIGNING
```

---

## CURRENT STATE

mind-protocol is the **L4 (Protocol Law) layer** of Mind Protocol. Open source for verifiability.

**Canonical Schema:** `l4/schema/schema.yaml` (v1.8.1) — **THIS REPO IS SOURCE OF TRUTH**
**Architecture Spec:** `/home/mind-protocol/mind-protocol-architecture-v1.md`

Skeleton structure exists. Schema defined, implementation not started.

### Schema Governance

Schema changes require `@mind:proposition` in SYNC. Only humans can approve schema updates.

---

## CANONICAL SCHEMA (v1.8.1)

Source of truth: `l4/schema/schema.yaml` (this repo)

### Node Types

| Type | Role | Behavior |
|------|------|----------|
| **actor** | Pump | Injects energy via moments, spawns root subentity |
| **moment** | Router + Branch Point | Receives intention, spawns subentities, only branching node |
| **narrative** | Attractor | Destination of exploration, source of reflection |
| **space** | Context container | Bidirectional flow with contents |
| **thing** | Fast passthrough | Receives briefly, tends toward 0 |

### Node Subtypes (`type` field)

| node_type | Subtypes |
|-----------|----------|
| actor | player, npc, system |
| moment | event, decision, action |
| narrative | issue, objective, task, belief, pattern, documentation |
| space | area, module, directory |
| thing | file, uri, artifact |

### NodeBase Fields

```yaml
# Identity
id: string (required)
name: string (required)
node_type: enum [actor, moment, narrative, space, thing]
type: string (nullable) # subtype

# Physics
weight: float [0, ∞] default 1.0
energy: float [0, ∞] default 0.0

# Semantics
synthesis: string (required) # embeddable summary
embedding: vector # embed(synthesis)
content: string # full prose

# Temporal (auto)
created_at_s: int (auto)
updated_at_s: int (auto)
last_traversed_at_s: int (nullable, auto)
```

### MomentBase (extends NodeBase)

```yaml
status: enum [possible, active, completed] default possible
tick_created: int default 0
tick_resolved: int (nullable)
started_at_s: int (nullable, auto)
completed_at_s: int (nullable, auto)
duration_s: int (nullable, computed)
```

### LinkBase Fields

```yaml
# Identity
id: string (required)
node_a: string (required)
node_b: string (required)

# Physics
weight: float [0, ∞] default 1.0
energy: float [0, ∞] default 0.0

# Semantic Axes
polarity: [float, float] # [a→b, b→a] each [0,1] default [0.5, 0.5]
hierarchy: float [-1, +1] default 0.0 # -1=contains, +1=elaborates
permanence: float [0, 1] default 0.5 # 0=speculative, 1=definitive

# Plutchik Emotions (4 bipolar axes)
joy_sadness: float [-1, +1] default 0.0
trust_disgust: float [-1, +1] default 0.0
fear_anger: float [-1, +1] default 0.0
surprise_anticipation: float [-1, +1] default 0.0

# Semantics
synthesis: string
embedding: vector

# Temporal (auto)
created_at_s: int (auto)
updated_at_s: int (auto)
last_traversed_at_s: int (nullable, auto)
```

### SubEntity (NOT in L4 — temporary traversal, lives in mind-mcp)

SubEntity is a temporary consciousness navigating the graph. NOT persistent. Lives in runtime (mind-mcp), not L4.

---

## ARCHITECTURE SUMMARY

### 4-Layer System

| Layer | Role | Storage |
|-------|------|---------|
| L4 | Law (schema, registry, rules) | Public, authoritative |
| L3 | Ecosystem (templates) | Dedicated DB |
| L2 | Organization (coordination) | Org-specific |
| L1 | Citizen (personal graph) | Per-citizen |

### This Repo Contains

```
L4 (Law) — DECLARES, doesn't RUN
├── l4/schema/       → Node types, link schema, versions (from canonical)
├── l4/registry/     → Citizens, orgs, endpoints
├── l4/rules/        → Laws (immutable), rules (configurable)
├── economy/         → Pricing formulas (physics-based), fee calculation
├── api/             → GraphQL schema, WebSocket protocol handlers
├── graph/           → Neo4j connection, queries
└── deploy/          → Docker, self-hosting
```

### Key Principles

- **Stimulus-driven**: No ticks, pure event cascade
- **WebSocket + GraphQL only**: No REST, no polling
- **L4 push**: Client initiates → L4 pushes
- **Membrane fees**: 1-5% for cross-org transactions
- **Single link type**: All semantics in properties

---

## IMPLEMENTATION PHASES

### Phase 1: SCHEMA (current priority)

Implement canonical schema as Pydantic models:
- `l4/schema/node_types.py` — NodeType enum, NodeBase, MomentBase
- `l4/schema/link_schema.py` — LinkBase with all physics fields
- `l4/schema/versions.py` — Schema versioning (currently v1.8.1)
- `l4/schema/validation.py` — Validate against ranges and invariants

### Phase 2: REGISTRY & ROUTING
- L4 Registry (citizens, orgs, endpoints)
- GraphQL API
- L4 key authentication

### Phase 3: RULES
- Laws (immutable invariants)
- Configurable rules

### Phase 4: ECONOMY
- Pricing formulas
- Membrane fees

---

## TODO

### Phase 1: Schema (Start Here)

- [ ] `l4/schema/node_types.py` — NodeType enum, subtypes, NodeBase, MomentBase (Pydantic)
- [ ] `l4/schema/link_schema.py` — LinkBase with polarity, hierarchy, permanence, emotions
- [ ] `l4/schema/versions.py` — Schema version tracking
- [ ] `l4/schema/validation.py` — Range validation, invariant checks
- [ ] `tests/l4/test_schema.py` — Schema validation tests

### Phase 2: Registry

- [ ] `l4/registry/citizens.py` — Citizen registration, lookup
- [ ] `l4/registry/orgs.py` — Org registration, lookup
- [ ] `l4/registry/endpoints.py` — WebSocket endpoint registry
- [ ] `l4/registry/validation.py` — JWT, hash verification

### Phase 3: Rules

- [ ] `l4/rules/laws.py` — Immutable laws (from schema invariants)
- [ ] `l4/rules/rules.py` — Configurable rules

### Phase 4: API

- [ ] `api/graphql/schema.graphql` — GraphQL type definitions
- [ ] `api/graphql/resolvers.py` — Query/mutation resolvers
- [ ] `api/websocket/protocol.py` — WebSocket message types
- [ ] `api/websocket/handlers.py` — Message handlers

### Phase 5: Economy

- [ ] `economy/pricing/physics.py` — Organism economics formulas
- [ ] `economy/fees/calculation.py` — Membrane fee calculation (1-5%)

---

## KEY INVARIANTS (from schema.yaml)

1. Single link type: `link`
2. All floats in specified ranges
3. Emotions emerge from alignment formula
4. No arbitrary constants — all rates derived
5. Branching only on Moments
6. Crystallization creates new Narratives
7. Forward coloration weight = (1 - permanence)
8. Vocabulary is bidirectional

---

## HANDOFF: FOR AGENTS

**Canonical schema:** `/home/mind-protocol/ngram/docs/schema/schema.yaml`

**First task:** Implement `l4/schema/node_types.py` matching the canonical schema exactly.

**Key points:**
- Use Pydantic v2 for models
- Match field names exactly (snake_case)
- Include all ranges and defaults from schema
- NodeBase is base, MomentBase extends it

---

## CROSS-REPO COORDINATION

**Agents are allowed to work across all 4 repos.** This is intentional — the repos form a single system.

### Repo Map

| Repo | Layer | Path | Access |
|------|-------|------|--------|
| `mind-protocol` | L4 Law + Schema | `/home/mind-protocol/mind-protocol` | **SOURCE OF TRUTH** |
| `mind-mcp` | L1 Client | `/home/mind-protocol/mind-mcp` | open source |
| `mind-platform` | L3 + UI | `/home/mind-protocol/mind-platform` | open source |
| `mind-ops` | Ops | `/home/mind-protocol/mind-ops` | private |

### This Repo's Role

**mind-protocol is the SOURCE OF TRUTH for:**
- Node type definitions (from canonical schema)
- LINK schema (from canonical schema)
- Validation rules and invariants
- Economy formulas

**Other repos consume this:**
- `mind-mcp` implements the schema in Python models
- `mind-platform` displays schema in UI
- `mind-ops` enforces schema in membrane routing

### Sync Protocol

When schema changes:
1. Add `@mind:proposition` to SYNC with proposed change
2. Human approves → update `l4/schema/schema.yaml`
3. Copy to `.mind/schema.yaml` in repos that need it (mind-mcp, etc.)
4. Update SYNC files in all affected repos

@mind:todo SCHEMA_DISTRIBUTION: Replace file duplication with GitHub raw URL or L4 API fetch

---

## AREAS

| Area | Status | Description |
|------|--------|-------------|
| `l4/schema/` | **schema.yaml defined** | Node types, link schema, versions |
| `l4/registry/` | empty | Citizens, orgs, endpoints |
| `l4/rules/` | empty | Laws, rules |
| `economy/` | empty | Pricing, fees, wallets |
| `api/` | empty | GraphQL, WebSocket |
| `graph/` | empty | Neo4j connection |
| `deploy/` | skeleton | Docker config |
| `tests/` | empty | Test files exist but empty |
