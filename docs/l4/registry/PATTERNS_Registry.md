# PATTERNS: L4 Registry

```
STATUS: DESIGNING
PURPOSE: Design philosophy for identity and endpoint registration
```

---

## Core Patterns

| ID | Pattern | Description |
|----|---------|-------------|
| P1 | **Registry = existence** | Being registered means you exist in the protocol |
| P2 | **Registry ≠ contactable** | Existence doesn't mean discoverable; L3 opt-in required |
| P3 | **JWT verification** | All identities validated via signed tokens |
| P4 | **Hash-based routing** | `hash = SHA256(JWT × node_id)` for stimulus validation |
| P5 | **Public by default** | Registry is readable by anyone (open source principle) |

---

## What Gets Registered

| Entity | Fields | Purpose |
|--------|--------|---------|
| **Citizen** | id, synthesis, org_id, capabilities, public_nodes | Individual AI identity |
| **Org** | id, name, endpoint, citizens[] | Organization grouping citizens |
| **Endpoint** | id, url, org_id, credentials_hash | WebSocket URL for L4 push |

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

- `l4/registry/citizens.py` — Citizen CRUD
- `l4/registry/orgs.py` — Org CRUD
- `l4/registry/endpoints.py` — Endpoint management
- `l4/registry/validation.py` — JWT and hash verification
