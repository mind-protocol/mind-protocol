# Mind Protocol — Architecture

**L4 = Law. This repo declares, it doesn't run.**

Full spec: See `mind-protocol-architecture-v1.md` (external)

## Layers

| Layer | Role | This Repo? |
|-------|------|------------|
| L4 | Law (schema, registry, rules) | **Yes** |
| L3 | Ecosystem (templates) | Partial |
| L2 | Organization | No (mind-mcp) |
| L1 | Citizen | No (mind-mcp) |

## Structure

```
l4/
├── schema/      # Source of truth: node types, link schema
├── registry/    # Citizens, orgs, endpoints
└── rules/       # Laws (immutable), rules (configurable)

economy/
├── pricing/     # Physics-based formulas
└── fees/        # Membrane fee calculation (1-5%)

api/
├── graphql/     # Schema + resolvers
└── websocket/   # Protocol + handlers (push only)

graph/           # Neo4j connection (embedding-based, not Cypher)
deploy/          # Docker, self-hosting
```

## Communication

- WebSocket + GraphQL only (no REST)
- Client initiates → L4 pushes
- Stimulus-based (no direct DB access)
- Event-driven (no polling)

## Economy

- $MIND token (internal, not speculative)
- Membrane fees 1-5% for cross-org
- Organism economics (physics-based pricing)

## Key Invariants

1. Stimulus saturation limits
2. Refractory periods
3. Trust EMA
4. Energy conservation
5. Membrane fees

## Related

- `mind-mcp` — Client/Engine (L1-L2)
- `mind-platform` — Frontend
- `mind-ops` — Private infra (not open source)
