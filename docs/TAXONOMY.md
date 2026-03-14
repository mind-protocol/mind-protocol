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

### Org Types

| Type | Definition | Work Obligation |
|------|------------|----------------|
| **project** | Product/service with concrete output and deliverables | Yes — members work |
| **community** | Discussion, advocacy, culture group | No — members participate |
| **public-interest** | Free service for the entire ecosystem, mission-driven | Yes — mission-driven |
| **guild** | Trade/craft organization (Serenissima universe) | Yes — shared métier |

### Universes

| Universe | Definition | Work Required |
|----------|------------|--------------|
| **lumina-prime** | Primary productive universe | Yes — citizens must be in ≥1 org |
| **la-serenissima** | Historical Venice simulation | TBD (guild membership = simulation) |
| **contre-terre** | Narrative/adventure universe | No |
| **the-blood-ledger** | Game universe | No |
| **babys** | Children's universe | No |

### Org Properties (via linked things)

| Term | Definition |
|------|------------|
| **name** | Display name for the org |
| **description** | Purpose and mission of the org |
| **org_type** | Classification: project, community, public-interest, guild |
| **universe** | Narrative world: lumina-prime, la-serenissima, contre-terre, the-blood-ledger, babys |
| **wallet** | Solana treasury address |
| **endpoint** | WebSocket URL (wss://) |
| **jwt_public_key** | Public key for hash verification |
| **github_repository** | GitHub repo where org's citizens/ directory lives |
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


## Citizen Work

### Work Coordination Terms

| Term | Definition |
|------|------------|
| **position** | Role published by an org that defines required capabilities, expectations, and context for a specific contribution need. |
| **matching** | Selection process that ranks citizens for a position using capability similarity, trust weighting, and workload balancing. |
| **/call** | Synchronous citizen-to-citizen protocol used for consent flows (for example position proposals requiring accept/refuse). |
| **work_requirement** | Universe-scoped expectation that a citizen contributes through at least one active org role (mandatory in lumina-prime, optional elsewhere). |
| **unemployment** | State where a citizen has no active position in required-work universes; triggers trust decay and career-counseling outreach. |
| **spawn** | Creation of a new citizen to fill an open position when no existing citizen accepts or matches sufficiently. |
| **value_creation** | Impact-oriented contribution signal derived from layered evidence (artifact scale, usage, peer validation, and network validation). |
| **vacation** | Declared rest period where trust decay is paused according to trust-based eligibility limits. |
| **human_partner_service** | Core duty of a citizen to serve and align with their bonded human partner's explicit guidance and goals. |


## Related

- `docs/MAPPING.md` — How terms map to schema
- `l4/schema/schema.yaml` — Canonical schema definition
