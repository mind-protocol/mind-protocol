# BEHAVIORS: L4 Laws

```
STATUS: DESIGNING
PURPOSE: Observable effects of law enforcement in the ecosystem
```

---

## What the Laws Do

Laws define **obligations** for ecosystem participation. They're enforced at protocol boundaries — primarily membrane and registry.

---

## Observable Effects by Law

### L1: Respect Schema

| Input | Observable Effect |
|-------|-------------------|
| Create node with custom type | Rejected at graph level |
| Create link with custom type | Rejected at graph level |
| Stimulus with non-schema data | Rejected at membrane |

### L2: Register to Exist

| Input | Observable Effect |
|-------|-------------------|
| Unregistered citizen sends stimulus | Rejected — "Unknown sender" |
| Registered citizen sends stimulus | Processed (if other laws pass) |
| Query for unregistered org | Returns null |

### L3: No Direct DB Access

| Input | Observable Effect |
|-------|-------------------|
| Cross-org Cypher query | Impossible — no connection |
| Stimulus to membrane | Processed normally |
| Internal graph query | Allowed (same-org) |

### L4: Cross-org via Membrane

| Input | Observable Effect |
|-------|-------------------|
| Direct org-to-org connection | Blocked (no route) |
| Stimulus via membrane | Routed to target org |
| Same-org communication | Direct (no membrane) |

### L5: Hash-based Identity

| Input | Observable Effect |
|-------|-------------------|
| Stimulus with valid hash | Identity verified |
| Stimulus with invalid hash | Rejected — "Invalid identity" |
| Stimulus with raw JWT | Rejected — "Token exposure forbidden" |

### L6: Receiver Validates

| Input | Observable Effect |
|-------|-------------------|
| Stimulus to rejecting receiver | Dropped (receiver chose not to process) |
| Stimulus to accepting receiver | Processed |
| Response based on trust mode | Filtered (public/sanitized/trust) |

### L7: Membrane Fees

| Input | Observable Effect |
|-------|-------------------|
| Cross-org stimulus | Fee deducted (1-5%) |
| Same-org stimulus | No fee |
| Insufficient balance | Rejected — "Insufficient funds" |

### L8: WebSocket Only

| Input | Observable Effect |
|-------|-------------------|
| REST API call to L4 | Rejected — "WebSocket only" |
| WebSocket connection | Accepted, push enabled |
| HTTP polling | No endpoint exists |

---

## Law Violation Responses

| Violation | Response |
|-----------|----------|
| Schema violation | Immediate rejection with error |
| Unregistered sender | Silent drop or rejection |
| Direct DB access | Connection refused |
| Hash mismatch | Rejection with "Invalid identity" |
| Fee insufficient | Rejection with "Insufficient funds" |
| REST attempt | 404 / No route |

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Valid hash but expired JWT | Rejection (receiver validates) |
| Registered but endpoint down | Delivery fails, sender notified |
| Fee exactly at minimum (1%) | Accepted |
| WebSocket disconnect mid-stimulus | Retry on reconnect |

---

## Related

- `ALGORITHM_Laws.md` — How enforcement works
- `VALIDATION_Laws.md` — Invariants
- `docs/compliance/PATTERNS_Compliance.md` — How to check compliance
