# VALIDATION: L4 Registry

```
STATUS: DESIGNING
PURPOSE: Invariants that must always hold for registry integrity
```

---

## Critical Invariants

These MUST be true at all times. Violation = protocol breach.

| ID | Invariant | Verification |
|----|-----------|--------------|
| V1 | **Unique citizen IDs** | No two citizens share same ID |
| V2 | **Unique org IDs** | No two orgs share same ID |
| V3 | **Citizens have org** | Every citizen.org_id references valid org |
| V4 | **Orgs have endpoint** | Every org has exactly one endpoint |
| V5 | **Valid WebSocket URL** | All endpoints are valid wss:// URLs |
| V6 | **JWT never stored raw** | Only hashes stored, never plaintext JWT |

---

## Referential Integrity

| ID | Invariant | Check |
|----|-----------|-------|
| R1 | Citizen → Org | `citizen.org_id` exists in orgs |
| R2 | Endpoint → Org | `endpoint.org_id` exists in orgs |
| R3 | Org.citizens[] | All IDs in list exist in citizens |

---

## Verification Procedures

```python
def verify_registry_integrity() -> List[Violation]:
    """Check all registry invariants."""
    violations = []

    # V1: Unique citizen IDs
    citizen_ids = [c.id for c in get_all_citizens()]
    if len(citizen_ids) != len(set(citizen_ids)):
        violations.append("V1: Duplicate citizen IDs found")

    # V2: Unique org IDs
    org_ids = [o.id for o in get_all_orgs()]
    if len(org_ids) != len(set(org_ids)):
        violations.append("V2: Duplicate org IDs found")

    # V3: Citizens have valid org
    for citizen in get_all_citizens():
        if not get_org(citizen.org_id):
            violations.append(f"V3: Citizen {citizen.id} has invalid org_id")

    # V4: Orgs have endpoint
    for org in get_all_orgs():
        if not get_endpoint_for_org(org.id):
            violations.append(f"V4: Org {org.id} has no endpoint")

    # V5: Valid WebSocket URLs
    for endpoint in get_all_endpoints():
        if not is_valid_websocket_url(endpoint.url):
            violations.append(f"V5: Invalid endpoint URL: {endpoint.url}")

    return violations
```

---

## Soft Constraints

These SHOULD be true but won't break the protocol if violated.

| ID | Constraint | Reason |
|----|------------|--------|
| S1 | Synthesis present | Human-readable identity |
| S2 | Endpoint reachable | Delivery will work |
| S3 | JWT not expired | Verification will succeed |

---

## When Validation Runs

| Trigger | What's Checked |
|---------|----------------|
| Citizen registration | V1, V3 |
| Org registration | V2, V4, V5 |
| Hash verification | V6 (implicitly) |
| Periodic audit | All invariants |

---

## Related

- `ALGORITHM_Registry.md` — How registration works
- `HEALTH_Registry.md` — Runtime checks
- `docs/l4/laws/PATTERNS_Laws.md` — L2 (Register to exist)
