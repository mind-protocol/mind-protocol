# PATTERNS: L4 Registry

```
STATUS: IMPLEMENTED
PURPOSE: Design philosophy for identity and endpoint registration
UPDATED: 2024-12-29
INHERITS: docs/l4/PATTERNS_L4.md
```

---

## Core L4 Rules

**See `docs/l4/PATTERNS_L4.md` for rules that apply to ALL L4 modules:**
- L4-1: L4 = Graph
- L4-2: Membrane only
- L4-3: Graph MCP calls
- L4-4: Skill + Procedure

---

## Registry-Specific Patterns

| ID | Pattern | Description |
|----|---------|-------------|
| R1 | **Registry = existence** | Being registered means you exist in the protocol |
| R2 | **Registry ≠ contactable** | Existence doesn't mean discoverable; L3 opt-in required |
| R3 | **JWT verification** | All identities validated via signed tokens |
| R4 | **Hash-based routing** | `hash = SHA256(JWT + node_id)` for stimulus validation |
| R5 | **Public by default** | Registry is readable by anyone (open source principle) |

---

## Registry Skills + Procedures

| Skill | Procedure | Purpose |
|-------|-----------|---------|
| `register_citizen` | `procedure_register_citizen.yaml` | Create citizen + identity hash |
| `register_org` | `procedure_register_org.yaml` | Create org + endpoint + wallet |
| `verify_identity` | `procedure_verify_identity.yaml` | Check hash for routing |
| `verify_jwt` | `procedure_verify_jwt.yaml` | Check JWT for registration |
| `get_endpoint` | `procedure_get_endpoint.yaml` | Get org's WebSocket URL |
| `update_status` | `procedure_update_status.yaml` | Change citizen/org status |
| `suspend_citizen` | `procedure_suspend_citizen.yaml` | Mark citizen suspended |
| `update_endpoint` | `procedure_update_endpoint.yaml` | Change org's endpoint |

---

## What Gets Registered

Entities are schema nodes. Properties are **linked nodes** (narrative for concepts, thing for artifacts).

### Citizen (actor, type: "citizen")

| Linked Node | node_type | Type | Required | Public |
|-------------|-----------|------|----------|--------|
| name | narrative | `"name"` | Yes | true |
| org_membership | narrative | `"org_membership"` | Yes | true |
| status | narrative | `"status"` | Yes | true |
| registered_date | narrative | `"registered_date"` | Yes | true |
| wallet | thing | `"wallet"` | No | false |
| capabilities | narrative | `"capabilities"` | No | true |

### Org (space, type: "org")

| Linked Node | node_type | Type | Required | Public |
|-------------|-----------|------|----------|--------|
| name | narrative | `"name"` | Yes | true |
| wallet | thing | `"wallet"` | Yes | true |
| endpoint | thing | `"endpoint"` | Yes | true |
| jwt_public_key | thing | `"jwt_public_key"` | Yes | false |
| status | narrative | `"status"` | Yes | true |
| registered_date | narrative | `"registered_date"` | Yes | true |

### Verification (via link from verifier)

| Link Property | Meaning |
|---------------|---------|
| polarity = 1.0 | Verified |
| polarity = -1.0 | Rejected |
| permanence < 0.5 | Provisional |
| No link | Unverified |

---

## Design Decisions

### Why separate Citizens and Orgs?

Citizens are individuals with personal graphs (L1). Orgs coordinate multiple citizens (L2). The registry reflects this hierarchy:

```
Org A
├── Citizen 1 (owns personal graph)
├── Citizen 2 (owns personal graph)
└── Endpoint (WebSocket URL for L4 push)
```

### Why hash-based validation?

Cross-org communication requires proving:
1. The stimulus comes from who it claims
2. The origin graph is registered
3. The membrane is official

Hash = `SHA256(JWT_origin × node_id)` proves all three.

### Why registry is public?

L4 = Law. Laws must be verifiable. Anyone can:
- Check if a citizen exists
- Verify an org is registered
- Audit the registry

---

## Non-Objectives

| ID | Non-Objective | Reason |
|----|---------------|--------|
| N1 | Store graph data | Registry is identity, not content |
| N2 | Manage permissions | That's L2 org-level |
| N3 | Handle payments | That's economy module |
| N4 | Route stimuli | That's membrane (mind-ops) |

---

## Invariants

1. Every citizen belongs to exactly one org
2. Every org has exactly one endpoint
3. Endpoint URL must be valid WebSocket
4. JWT must be valid and unexpired
5. No duplicate citizen IDs across orgs

---

## Related

- `VOCABULARY_Registry.md` — Terms defined by this module
- `docs/TAXONOMY.md` — Central vocabulary
- `docs/MAPPING.md` — Schema translation
- `l4/registry/citizen_registration_crud_operations.py` — Citizen models + node creation
- `l4/registry/org_registration_crud_operations.py` — Org models + node creation
- `l4/registry/jwt_hash_verification_for_identity.py` — Hash verification
