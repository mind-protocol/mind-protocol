# PATTERNS: L4 Laws

```
STATUS: DESIGNING
PURPOSE: Ecosystem obligations for Mind Protocol participants
```

---

## What Laws Are

Laws are **obligations** for participating in the Mind Protocol ecosystem. They define how graphs communicate with each other, not how they run internally.

| Not Laws | Laws |
|----------|------|
| Graph structure (schema) | Ecosystem participation |
| Physics formulas | Communication rules |
| Range constraints | Identity & routing |

---

## Laws

| ID | Law | Obligation |
|----|-----|------------|
| L1 | **Respect schema** | All graphs must use canonical schema (5 node types, single link type) |
| L2 | **Register to exist** | Must register in L4 registry to participate in ecosystem |
| L3 | **No direct DB access** | Cannot query/modify another graph — stimulus only |
| L4 | **Cross-org via membrane** | All cross-org communication routes through membrane |
| L5 | **Hash-based identity** | Prove identity via `hash = SHA256(JWT × node_id)`, never send token |
| L6 | **Receiver validates** | Cross-org stimulus requires explicit receiver acceptance |
| L7 | **Membrane fees** | Cross-org transactions pay 1-5% to protocol |
| L8 | **WebSocket only** | Communication via WebSocket push, no polling |

---

## Law Details

### L1: Respect schema
All graphs in the ecosystem use the same schema. No custom node types, no custom link types. This enables interoperability.

### L2: Register to exist
To participate in cross-org communication, you must be registered in L4. Registry = existence in the protocol.

### L3: No direct DB access
You never touch another graph's database. All communication is via stimulus through membrane. Privacy by design.

### L4: Cross-org via membrane
Cross-org communication routes through membrane network. No direct connections between orgs.

### L5: Hash-based identity
Never send your JWT. Prove you have it via hash: `SHA256(JWT × node_id)`. Receiver validates against L4 registry.

### L6: Receiver validates
Cross-org stimulus requires explicit acceptance. Receiver decides whether to process based on trust, mode (public/sanitized/trust).

### L7: Membrane fees
Cross-org transactions pay 1-5% to the protocol. Same-org is free.

### L8: WebSocket only
No REST. No polling. Client initiates WebSocket, L4 pushes. Event-driven.

---

## What Devs Can vs Cannot Change

| Cannot Change (Laws) | Can Change (Your Choice) |
|---------------------|--------------------------|
| Node types (must be 5) | Subtypes (`type` field) |
| Link type (must be `link`) | Link properties (polarity, hierarchy, etc.) |
| Communication via membrane | Internal graph structure |
| Hash-based identity | Your JWT secret |
| Receiver validation required | Trust thresholds |
| Membrane fees exist (1-5%) | Which orgs you interact with |
| WebSocket protocol | Your endpoint URL |
| Registration required | Your org name, synthesis |

**Rule of thumb:** Laws define the protocol. Everything else is your choice within the protocol.

---

## Non-Laws

These are NOT laws (they live elsewhere):

| What | Where |
|------|-------|
| Schema (node types, ranges) | `l4/schema/` |
| Physics formulas | `l4/schema/` or mind-mcp |
| Configurable rules | mind-mcp |
| Design principles | `.mind/PRINCIPLES.md` |

---

## Related

- `l4/schema/schema.yaml` — Graph structure definition
- `l4/registry/` — Registration for ecosystem participation
