# mind-protocol — Sync: Current State

```
LAST_UPDATED: 2024-12-28
UPDATED_BY: claude
STATUS: DESIGNING
```

---

## CURRENT STATE

mind-protocol is the **L4 (Protocol Law) layer** of Mind Protocol. Open source for verifiability.

**Architecture Spec v1 received.** Full spec at `/home/mind-protocol/mind-protocol-architecture-v1.md`

Skeleton structure exists. No implementation yet.

---

## ARCHITECTURE SUMMARY

### 4-Layer System

| Layer | Role | Storage |
|-------|------|---------|
| L4 | Law (schema, registry, rules) | Public, authoritative |
| L3 | Ecosystem (templates) | Dedicated DB |
| L2 | Organization (coordination) | Org-specific |
| L1 | Citizen (personal graph) | Per-citizen |

### This Repo (mind-protocol) Contains

```
L4 (Law) — DECLARES, doesn't RUN
├── l4/schema/       → Node types, link schema, versions (source of truth)
├── l4/registry/     → Citizens, orgs, endpoints, validation
├── l4/rules/        → Laws (immutable), rules (configurable)
├── economy/         → Pricing formulas (physics-based), fee calculation
├── api/             → GraphQL schema, WebSocket protocol handlers
├── graph/           → Neo4j connection, queries
└── deploy/          → Docker, self-hosting guide
```

### Key Principles

- **Stimulus-driven**: No ticks, pure event cascade
- **WebSocket + GraphQL only**: No REST, no polling
- **L4 push**: Client initiates → L4 pushes
- **Membrane fees**: 1-5% for cross-org transactions
- **Organism economics**: Physics-based pricing, not market

### Node Types (Schema)

| Label | Role | Subtypes |
|-------|------|----------|
| Actor | Pump — injects energy | player, npc, system, researcher |
| Moment | Router — branch point | event, decision, action |
| Narrative | Attractor — destination | belief, commitment, claim, step, vocabulary, mapping, skill |
| Space | Container — bidirectional | laboratory, module, procedure, template |
| Thing | Fast passthrough | file, uri, artifact, evidence |

### Single Relation: LINK

All semantics in properties: weight, energy, polarity, hierarchy, permanence, emotions (Plutchik), synthesis, embedding, public.

---

## IMPLEMENTATION PHASES

### Phase 1: MEMBRANE (current priority)
- Cross-level communication (L1 ↔ L2)
- Cross-org communication (via L4)
- `public` field on nodes/links
- Permeability (learned)

### Phase 2: REGISTRY & ROUTING
- L4 Registry (citizens, orgs, endpoints)
- GraphQL API
- L4 key authentication
- Feature gating

### Phase 3: AUTONOMY
- Energy-based wake
- Budget management ($MIND)
- Consolidation
- Health monitoring

### Phase 4: ECONOMY
- $MIND wallets (Solana)
- On-chain transactions
- Organism economics formulas
- Stripe integration (human interface)

---

## ACTIVE WORK

None started. Awaiting priority decision.

---

## TODO

### Phase 1: Schema & Core (Start Here)

- [ ] `l4/schema/node_types.py` — Actor, Moment, Narrative, Space, Thing enums + Pydantic models
- [ ] `l4/schema/link_schema.py` — LINK properties (weight, energy, polarity, emotions, etc.)
- [ ] `l4/schema/versions.py` — Schema versioning system
- [ ] `l4/schema/validation.py` — Validate nodes/links against schema

### Phase 1: Registry

- [ ] `l4/registry/citizens.py` — Citizen registration, lookup
- [ ] `l4/registry/orgs.py` — Org registration, lookup
- [ ] `l4/registry/endpoints.py` — WebSocket endpoint registry
- [ ] `l4/registry/validation.py` — JWT, hash verification

### Phase 1: Rules

- [ ] `l4/rules/laws.py` — Immutable laws (stimulus saturation, refractory, etc.)
- [ ] `l4/rules/rules.py` — Configurable rules

### Phase 2: API

- [ ] `api/graphql/schema.graphql` — GraphQL type definitions
- [ ] `api/graphql/resolvers.py` — Query/mutation resolvers
- [ ] `api/websocket/protocol.py` — WebSocket message types
- [ ] `api/websocket/handlers.py` — Message handlers
- [ ] `api/websocket/server.py` — FastAPI WebSocket server
- [ ] `api/websocket/push.py` — L4 push mechanism

### Phase 2: Graph

- [ ] `graph/connection.py` — Neo4j Aura connection
- [ ] `graph/queries.py` — Embedding-based traversal (not Cypher)

### Phase 3: Economy

- [ ] `economy/pricing/physics.py` — Organism economics formulas
- [ ] `economy/fees/calculation.py` — Membrane fee calculation (1-5%)
- [ ] `economy/wallets/` — Wallet management (later)
- [ ] `economy/transactions/solana.py` — On-chain transactions (later)

### Tests

- [ ] `tests/l4/test_schema.py` — Schema validation tests
- [ ] `tests/l4/test_registry.py` — Registry CRUD tests
- [ ] `tests/economy/test_pricing.py` — Pricing formula tests

---

## KEY INVARIANTS (L4 Must Enforce)

1. **Stimulus saturation**: No actor can emit > threshold per window
2. **Refractory period**: Minimum time between stimuli
3. **Trust EMA**: Weighted trust based on history
4. **Energy conservation**: Total energy bounded by physics
5. **Membrane fees**: 1-5% of cross-org value flows to protocol

---

## HANDOFF: FOR AGENTS

**Recommended approach:** Start with `l4/schema/` — it's the source of truth that everything else depends on.

**Agent posture:** `groundwork` (implement) or `architect` (if design questions arise)

**Key files to implement first:**
1. `l4/schema/node_types.py` — Define the 5 node types with Pydantic
2. `l4/schema/link_schema.py` — Define LINK properties
3. Then registry, then API

**Watch out for:**
- Must remain auditable — no hidden logic
- All state changes must be traceable
- Use Pydantic for validation
- Keep it simple — no over-engineering

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Architecture spec v1 received and captured. Skeleton exists, implementation not started.

**Recommended first step:**
Implement L4 schema (node types + link schema) — it's the foundation.

**Decision needed:**
- Confirm Phase 1 priorities
- Neo4j Aura credentials for testing (mentioned in spec but not in repo)

---

## RELATED REPOS

| Repo | Role | Status |
|------|------|--------|
| `mind-mcp` | Client/Engine | Separate repo |
| `mind-platform` | Frontend | Separate repo |
| `mind-ops` | Private infra | Not our concern |

---

## AREAS

| Area | Status | Description |
|------|--------|-------------|
| `l4/schema/` | empty | Node types, link schema, versions |
| `l4/registry/` | empty | Citizens, orgs, endpoints |
| `l4/rules/` | empty | Laws, rules |
| `economy/` | empty | Pricing, fees, wallets |
| `api/` | empty | GraphQL, WebSocket |
| `graph/` | empty | Neo4j connection |
| `deploy/` | skeleton | Docker config |
| `tests/` | empty | Test files exist but empty |

---

## CROSS-REPO COORDINATION

**Agents are allowed to work across all 4 repos.** This is intentional — the repos form a single system.

### Repo Map

| Repo | Layer | Path | Access |
|------|-------|------|--------|
| `mind-mcp` | L1 Client | `/home/mind-protocol/mind-mcp` | open source |
| `mind-protocol` | L4 Law | `/home/mind-protocol/mind-protocol` | open source |
| `mind-platform` | L3 + UI | `/home/mind-protocol/mind-platform` | open source |
| `mind-ops` | Ops | `/home/mind-protocol/mind-ops` | private |

### Coordination Hub: mind-ops

**`mind-ops` is the main cross-repo organization point.**

- Cross-repo issues go in `mind-ops/runbooks/cross-repo/`
- Deployment orchestration in `mind-ops/ci/`
- Shared secrets configuration in `mind-ops/secrets/`
- Integration tests that span repos in `mind-ops/tests/integration/`

### This Repo's Role

**mind-protocol is the SOURCE OF TRUTH for:**
- Node type definitions (Actor, Moment, Narrative, Space, Thing)
- LINK schema (weight, energy, polarity, emotions, etc.)
- Validation rules and invariants
- Economy formulas

**Other repos consume this:**
- `mind-mcp` implements the schema in Python models
- `mind-platform` displays schema in UI
- `mind-ops` enforces schema in membrane routing

### Sync Protocol

When schema changes:
1. Update `l4/schema/` here first
2. Update SYNC here noting the change
3. Propagate to `mind-mcp/mind/models/`
4. Update `mind-platform` if UI affected
5. Note cross-repo sync in all affected SYNCs
