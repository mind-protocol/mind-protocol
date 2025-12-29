# VALIDATION: L4 Laws

```
STATUS: DESIGNING
PURPOSE: Invariants that ensure law compliance
```

---

## Critical Invariants

These MUST be true at all times. Violation = law breach.

| ID | Law | Invariant | Verification |
|----|-----|-----------|--------------|
| V1 | L1 | Schema compliance | All nodes/links pass schema validation |
| V2 | L2 | Registered senders | `stimulus.sender_id` exists in registry |
| V3 | L3 | No direct DB access | Network audit: only membrane connections cross org |
| V4 | L4 | Membrane routing | All cross-org traffic through membrane endpoints |
| V5 | L5 | Hash-based identity | No raw JWT in stimulus payload |
| V6 | L5 | Valid hash | `hash == SHA256(jwt × node_id)` |
| V7 | L6 | Receiver consent | Cross-org stimulus has acceptance flag |
| V8 | L7 | Fees paid | `transaction.fee >= 0.01 * transaction.value` |
| V9 | L8 | WebSocket only | L4 API has no REST endpoints |

---

## Verification Procedures

### V1: Schema Compliance

```python
def verify_schema_compliance(stimulus):
    """All data in stimulus must pass schema validation."""
    for node in stimulus.nodes:
        assert validate_node(node).is_valid
    for link in stimulus.links:
        assert validate_link(link).is_valid
```

### V2-V4: Registration and Routing

```python
def verify_cross_org_path(stimulus, network_trace):
    """Cross-org traffic must go through membrane."""
    sender = registry.get_citizen(stimulus.sender_id)
    assert sender is not None, "V2: Sender not registered"

    for hop in network_trace:
        if hop.source_org != hop.target_org:
            assert hop.via_membrane, "V4: Direct org-to-org connection"
```

### V5-V6: Hash Identity

```python
def verify_hash_identity(stimulus):
    """Identity must be proven via hash, never raw token."""
    # V5: No raw JWT
    assert "jwt" not in str(stimulus.payload).lower(), "V5: Raw JWT detected"

    # V6: Valid hash
    citizen = registry.get_citizen(stimulus.sender_id)
    expected = sha256(citizen.jwt + stimulus.node_id)
    assert stimulus.identity_hash == expected, "V6: Hash mismatch"
```

### V7: Receiver Consent

```python
def verify_receiver_consent(stimulus, receiver_log):
    """Receiver explicitly accepted or rejected."""
    assert receiver_log.decision in ["accept", "reject"], "V7: No explicit decision"
```

### V8: Fees

```python
def verify_fee_payment(transaction):
    """Cross-org transactions pay minimum fee."""
    if transaction.source_org != transaction.target_org:
        min_fee = transaction.value * 0.01
        assert transaction.fee >= min_fee, f"V8: Fee {transaction.fee} < minimum {min_fee}"
```

### V9: WebSocket Only

```python
def verify_no_rest_endpoints():
    """L4 API exposes only WebSocket."""
    routes = get_all_api_routes()
    for route in routes:
        assert route.protocol == "websocket", f"V9: REST route found: {route}"
```

---

## Compliance Audit

```python
def full_compliance_audit(org_id):
    """Audit an org's compliance with all laws."""
    results = {}

    # Sample recent stimuli
    stimuli = get_recent_stimuli(org_id, limit=100)

    for stimulus in stimuli:
        results[stimulus.id] = {
            "schema": verify_schema_compliance(stimulus),
            "identity": verify_hash_identity(stimulus),
            "routing": verify_cross_org_path(stimulus),
            "fees": verify_fee_payment(stimulus),
        }

    return results
```

---

## Soft Constraints

These SHOULD be true but are enforced by receivers, not protocol.

| ID | Constraint | Reason |
|----|------------|--------|
| S1 | Response filtered by trust mode | Receiver's choice |
| S2 | Fee rate in reasonable range | Market dynamics |
| S3 | Timely response | No protocol timeout |

---

## Related

- `ALGORITHM_Laws.md` — How enforcement works
- `HEALTH_Laws.md` — Runtime checks
- `docs/compliance/PATTERNS_Compliance.md` — Developer checklist
