# SYNC: L4 Registry

```
LAST_UPDATED: 2024-12-29
STATUS: IMPLEMENTED
PRIORITY: P1
VERSION: 1.0.0
```

---

## Current State

P1 Registry IMPLEMENTED. 49 tests passing.

| Component | Status |
|-----------|--------|
| `citizen_registration_crud_operations.py` | **IMPLEMENTED** — CitizenRegistration, create_citizen_nodes (with identity_hash) |
| `org_registration_crud_operations.py` | **IMPLEMENTED** — OrgRegistration, create_org_nodes |
| `endpoint_registration_and_management.py` | **IMPLEMENTED** — validate_endpoint_url, create_endpoint_node |
| `jwt_hash_verification_for_identity.py` | **IMPLEMENTED** — verify_hash, verify_jwt_signature, verify_and_get_endpoint |
| `tests/l4/test_registry.py` | **49 tests passing** |

---

## Doc Chain

| Doc | Status |
|-----|--------|
| OBJECTIVES | Complete |
| PATTERNS | Complete |
| BEHAVIORS | Complete |
| ALGORITHM | Complete |
| VALIDATION | Complete |
| IMPLEMENTATION | Complete |
| HEALTH | Complete |
| SYNC | This file |
| VOCABULARY | Complete |

---

## Recent Changes

### 2024-12-29: Verification algorithms complete

- Added JWT signature verification for registration flow
  - `verify_jwt_signature()` — Verifies JWT format, claims, and org public key exists
  - `verify_jwt_claims()` — Validates exp, iat, iss claims
  - `decode_jwt_parts()` — Decodes JWT without verification

- Added combined routing verification for inbound stimulus
  - `verify_and_get_endpoint()` — Verifies hash + gets destination endpoint in one call
  - `RoutingVerificationResult` — Result with status, sender info, and endpoint

- Updated citizen registration
  - CitizenRegistration now takes `jwt` (not `jwt_hash`)
  - create_citizen_nodes() now creates identity_hash ThingNode
  - Returns identity_hash for future stimulus verification

- Added 19 new tests (49 total)

### 2024-12-29: P1 Registry implemented

- Implemented `citizen_registration_crud_operations.py`
  - CitizenRegistration dataclass (API input)
  - CitizenRecord dataclass (API output)
  - create_citizen_nodes() — creates ActorNode + linked property nodes
  - Properties as linked nodes (name, status, org_membership, wallet, capabilities, identity_hash)

- Implemented `org_registration_crud_operations.py`
  - OrgRegistration dataclass (API input)
  - OrgRecord dataclass (API output)
  - create_org_nodes() — creates SpaceNode + linked property nodes
  - Properties as linked nodes (name, status, wallet, endpoint, jwt_public_key)

- Implemented `endpoint_registration_and_management.py`
  - validate_endpoint_url() — validates wss:// URLs
  - create_endpoint_node() — creates ThingNode for endpoint

- Implemented `jwt_hash_verification_for_identity.py`
  - compute_hash() — SHA256(JWT + node_id)
  - verify_hash() — verifies against registry lookup via graph query

### 2024-12-29: Vocabulary and mapping

- Created `VOCABULARY_Registry.md` with all registry terms
- Added registry mappings to `docs/MAPPING.md`
- Updated PATTERNS to use linked things model
- Verification status computed from link floats (no separate node)

---

## TODO

- [x] Define Citizen Pydantic model
- [x] Define Org Pydantic model
- [x] Define Endpoint Pydantic model
- [x] Implement JWT validation
- [x] Implement hash verification for cross-org
- [x] Add tests
- [ ] Add GraphQL resolvers for lookup
- [ ] Implement actual graph storage (when graph client available)

---

## Architecture

**L4 Registry = Nodes in Neo4j. No API. All graph queries.**

```
Membrane (mind-ops)                    Neo4j
     │                                   │
     │  create_org_nodes()               │
     │  + mind.graph.ops.create_node()   │
     ├──────────────────────────────────►│
     │                                   │
     │  graph query: verify hash         │
     ├──────────────────────────────────►│
     │◄──────────────────────────────────┤
```

| Operation | Function | How |
|-----------|----------|-----|
| Register org | `create_org_nodes()` | Membrane creates nodes in Neo4j |
| Register citizen | `create_citizen_nodes()` | Membrane creates nodes in Neo4j |
| Verify hash | `compute_hash()` + graph query | Membrane queries Neo4j directly |
| Get endpoint | Graph traversal | org → endpoint thing node |

**No HTTP API. Registry IS nodes in the graph.**

---

## Dependencies

- `l4/schema/` — Uses ActorNode, SpaceNode, ThingNode, NarrativeNode, LinkBase
- `api/graphql/` — Will expose registry via GraphQL (pending)
- `graph/` — Will store registry in Neo4j (pending)

---

## Handoff

**For agents:** Registry models complete. Next: implement graph storage.

**Key decisions:**
- Citizen = ActorNode with type="citizen"
- Org = SpaceNode with type="org"
- Endpoint = ThingNode with type="endpoint"
- Properties as linked nodes (narratives for concepts, things for artifacts)
- Verification via link floats (polarity=1.0 means verified)
- Membrane is the only caller of L4 API

---

## Plan

| Priority | Module | Status |
|----------|--------|--------|
| P0 | Schema | **COMPLETE** — 34 tests passing |
| **P1** | Registry | **COMPLETE** — 49 tests passing |
| P2 | Laws | Next — Enforcement functions |
| P3 | Compliance | Pending — Test suite |

**Total L4 tests: 83 passing**

---

## Markers

*No active escalations.*
