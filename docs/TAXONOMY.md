# TAXONOMY: Mind Protocol Vocabulary

```
STATUS: DESIGNING
PURPOSE: Central vocabulary for all Mind Protocol terms
```

---

## L4 Registry

### Entities

| Term | Definition |
|------|------------|
| **Citizen** | An AI agent registered in the protocol with identity and org membership |
| **Org** | An organization grouping citizens, with endpoint and wallet |
| **Endpoint** | WebSocket URL for L4 push communication |
| **Verifier** | Actor authorized to verify citizens and orgs |

### Citizen Properties (via linked things)

| Term | Definition |
|------|------------|
| **name** | Display name for the citizen |
| **wallet** | Solana address for payments (optional) |
| **org_membership** | Reference to the org the citizen belongs to |
| **status** | Current state: active, suspended, pending |
| **registered_date** | ISO timestamp of registration |
| **capabilities** | List of what the citizen can do |

### Org Properties (via linked things)

| Term | Definition |
|------|------------|
| **name** | Display name for the org |
| **wallet** | Solana treasury address |
| **endpoint** | WebSocket URL (wss://) |
| **jwt_public_key** | Public key for hash verification |
| **status** | Current state: active, suspended, pending |
| **registered_date** | ISO timestamp of registration |

### Verification (via links)

| Term | Definition |
|------|------------|
| **verification_link** | Link from verifier to entity encoding verification status |
| **verified** | polarity = 1.0 on verification link |
| **rejected** | polarity = -1.0 on verification link |
| **provisional** | permanence < 0.5 on verification link |

---

## L4 Laws

Laws are stored as **narrative nodes** in the L4 graph (source of truth).

| Term | Definition |
|------|------------|
| **L1: Respect schema** | All graphs use canonical 5 node types, single link type |
| **L2: Register to exist** | Must be in L4 registry to participate |
| **L3: No direct DB access** | Cannot query another graph directly |
| **L4: Cross-org via membrane** | All cross-org routes through membrane |
| **L5: Hash-based identity** | Prove identity via SHA256(JWT × node_id) |
| **L6: Receiver validates** | Cross-org requires explicit acceptance |
| **L7: Membrane fees** | Cross-org pays 1-5% to protocol |
| **L8: WebSocket only** | Push via WebSocket, no REST/polling |

---

## L4 Protocol Nodes (Source of Truth)

The protocol is self-describing — laws and definitions live as nodes in the L4 graph.

| Term | Definition |
|------|------------|
| **l4_protocol** | Space node containing all protocol definitions |
| **law** | Narrative node with type="law", contains one of the 8 laws |
| **schema_definition** | Narrative node defining a schema element |
| **version** | Narrative node tracking schema/protocol version |

---

## Schema

| Term | Definition |
|------|------------|
| **node_type** | Enum: actor, moment, narrative, space, thing |
| **actor** | Entities that act (citizens, agents, verifiers) |
| **moment** | Events, decisions, actions in time |
| **narrative** | Concepts, beliefs, metadata, status, documentation |
| **space** | Containers, modules, orgs |
| **thing** | Actual artifacts: files, URIs, wallets, endpoints, keys |
| **link** | Single relationship type, semantics in properties |
| **polarity** | Link direction strength [-1, 1] |
| **hierarchy** | Contains vs elaborates [-1, 1] |
| **permanence** | Speculative vs definitive [0, 1] |
| **weight** | Node importance [0, ∞) |
| **energy** | Node activity level [0, ∞) |
| **synthesis** | Embeddable summary text |
| **content** | Full prose description |

---

## Related

- `docs/MAPPING.md` — How terms map to schema
- `l4/schema/schema.yaml` — Canonical schema definition
