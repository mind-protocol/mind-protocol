# PATTERNS: Compliance

```
STATUS: DESIGNING
PURPOSE: How to check compliance and develop around the protocol
```

---

## What Compliance Means

Compliance = following the 8 laws. If you follow them, you're part of the ecosystem. If you don't, you're not.

---

## Compliance Checklist

### L1: Respect Schema

| Check | How to Verify |
|-------|---------------|
| Using 5 node types only | `node.node_type in ["actor", "moment", "narrative", "space", "thing"]` |
| Using single link type | All edges are `link`, no custom types |
| Schema version matches | `config.schema_version == "1.8.1"` |

**Dev tip:** Use the Pydantic models from `l4/schema/`. They enforce types automatically.

### L2: Register to Exist

| Check | How to Verify |
|-------|---------------|
| Org registered in L4 | `GET /graphql { org(id: "your-id") { id } }` returns result |
| Citizens registered | Each citizen has entry in registry |
| Endpoint registered | WebSocket URL on file |

**Dev tip:** Registration is one-time. Do it before going live.

### L3: No Direct DB Access

| Check | How to Verify |
|-------|---------------|
| No cross-org DB queries | Code review: no external Neo4j connections |
| All cross-org via stimulus | Audit logs show stimulus messages only |

**Dev tip:** If you're tempted to query another graph, you're doing it wrong. Send a stimulus instead.

### L4: Cross-org via Membrane

| Check | How to Verify |
|-------|---------------|
| Cross-org routes through membrane | Network trace shows membrane endpoint |
| No direct org-to-org connections | Firewall: only membrane can reach your endpoint |

**Dev tip:** Your code should only know about membrane, never about other orgs directly.

### L5: Hash-based Identity

| Check | How to Verify |
|-------|---------------|
| JWT never sent in clear | Code review: no raw JWT in payloads |
| Hash computed correctly | `hash = SHA256(JWT × node_id)` |
| Hash validated by receiver | Receiver checks hash against registry |

**Dev tip:** Store JWT securely. Only expose the hash.

### L6: Receiver Validates

| Check | How to Verify |
|-------|---------------|
| Cross-org requires acceptance | Code has explicit accept/reject logic |
| Trust mode applied | Response filtered by public/sanitized/trust |

**Dev tip:** Default to reject. Explicitly accept known sources.

### L7: Membrane Fees

| Check | How to Verify |
|-------|---------------|
| Fees paid on cross-org | Transaction log shows fee deduction |
| Fee in range 1-5% | Fee percentage within bounds |

**Dev tip:** Same-org is free. Only cross-org costs.

### L8: WebSocket Only

| Check | How to Verify |
|-------|---------------|
| No REST endpoints for protocol | API audit shows WebSocket only |
| Push, not poll | No periodic GET requests to L4 |

**Dev tip:** Open WebSocket once, receive pushes. Don't poll.

---

## Compliance Levels

| Level | Description | Requirements |
|-------|-------------|--------------|
| **Local** | Running locally, no ecosystem | Follow schema (L1 only) |
| **Registered** | In registry, can receive | L1 + L2 |
| **Connected** | Cross-org enabled | L1-L8 (all laws) |

---

## Common Violations

| Violation | Why It Happens | Fix |
|-----------|----------------|-----|
| Custom node types | "I need a special type" | Use subtypes instead |
| Direct DB access | "It's faster" | Send stimulus, accept latency |
| Sending raw JWT | "Easier to debug" | Hash it, log the hash |
| Polling L4 | "Need real-time" | WebSocket IS real-time |
| Skipping fees | "Same company" | If different org ID, pay fee |

---

## Testing Compliance

```python
# Example compliance test
def test_schema_compliance(node):
    assert node.node_type in ["actor", "moment", "narrative", "space", "thing"]
    assert 0 <= node.weight
    assert 0 <= node.energy

def test_no_jwt_leak(stimulus):
    assert "jwt" not in stimulus.payload.lower()
    assert stimulus.hash == sha256(jwt + node_id)

def test_membrane_routing(cross_org_request):
    assert cross_org_request.endpoint.startswith("membrane://")
```

---

## Related

- `docs/l4/laws/` — The 8 laws in detail
- `docs/manifesto/` — Why these laws exist
- `l4/schema/schema.yaml` — Schema to comply with
