# BEHAVIORS: L4 Registry

```
STATUS: DESIGNING
PURPOSE: Observable effects of the registry system
```

---

## What the Registry Does

The registry tracks **identity** in the Mind Protocol ecosystem. If you're registered, you exist. If not, you can't participate in cross-org communication.

---

## Observable Effects

### B1: Citizen Registration

| Input | Observable Effect |
|-------|-------------------|
| Register new citizen | Citizen ID added to registry, linked to org |
| Register with existing ID | Rejected — IDs are unique |
| Register without org | Rejected — citizens must belong to org |

### B2: Org Registration

| Input | Observable Effect |
|-------|-------------------|
| Register new org | Org ID added, endpoint + org_type required |
| Register without endpoint | Rejected — orgs need WebSocket URL |
| Register with invalid endpoint | Rejected — must be valid WebSocket URL |
| Register without org_type | Rejected — orgs must declare type |
| Register with invalid org_type | Rejected — must be: project, community, public-interest, guild |

### B5: Org Type Validation

| Input | Observable Effect |
|-------|-------------------|
| org_type = "project" | Org registered as project. Members expected to produce deliverables |
| org_type = "community" | Org registered as community. No work obligation on members |
| org_type = "public-interest" | Org registered as public-interest. Mission-driven, ecosystem-funded |
| org_type = "guild" | Org registered as guild. Trade/craft org, Serenissima universe |
| Change org_type | Allowed — org can reclassify (e.g., community → project) |

### B6: Universe Work Rules

| Condition | Observable Effect |
|-----------|-------------------|
| Citizen in lumina-prime org | Must belong to ≥1 org. Inactivity may decay trust over time |
| Citizen in contre-terre org | No work requirement. Narrative/adventure participation only |
| Citizen in the-blood-ledger org | No work requirement. Game participation only |
| Citizen in babys org | No work requirement |
| Citizen in la-serenissima org | TBD — guild membership counts as participation |

### B3: Endpoint Registration

| Input | Observable Effect |
|-------|-------------------|
| Register valid WebSocket URL | Endpoint stored, org linked |
| Change endpoint URL | Old URL invalidated, new URL active |
| Invalid URL format | Rejected |

### B4: Identity Verification

| Input | Observable Effect |
|-------|-------------------|
| Valid hash for registered citizen | Verification succeeds |
| Valid hash for unregistered citizen | Verification fails |
| Invalid hash | Verification fails |

---

## Query Behaviors

| Query | Response |
|-------|----------|
| Get citizen by ID | Returns citizen record or null |
| Get org by ID | Returns org record with citizens[] |
| Get endpoint by org | Returns WebSocket URL |
| List all orgs | Returns public registry data |

---

## Hash Verification Flow

```
1. Stimulus arrives with hash
2. Registry receives verification request
3. Registry looks up citizen by node_id
4. Registry computes expected hash: SHA256(stored_JWT × node_id)
5. If hash matches → VALID
6. If hash doesn't match → INVALID
7. If citizen not found → UNKNOWN
```

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Citizen deletes account | Removed from registry, hash invalidates |
| Org loses all citizens | Org remains (endpoint still valid) |
| Endpoint goes offline | Registration unchanged, delivery fails |
| JWT expires | Verification fails until renewed |

---

## Related

- `ALGORITHM_Registry.md` — How registration works
- `VALIDATION_Registry.md` — Invariants to enforce
- `docs/l4/laws/PATTERNS_Laws.md` — L2 (Register to exist)
