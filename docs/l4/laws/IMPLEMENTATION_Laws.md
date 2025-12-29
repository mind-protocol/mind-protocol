# IMPLEMENTATION: L4 Laws

```
STATUS: DESIGNING
PURPOSE: Code architecture for law enforcement
```

---

## Overview

Laws are not a separate module — they're enforced across the protocol:

| Law | Enforced By | Location |
|-----|-------------|----------|
| L1 | Schema validators | `l4/schema/` |
| L2 | Registry lookup | `l4/registry/` |
| L3 | Network architecture | Infrastructure (no code) |
| L4 | Membrane routing | `mind-ops` |
| L5 | Hash verification | `l4/registry/validation.py` |
| L6 | Receiver handlers | Each org's code |
| L7 | Fee processing | `economy/` (future) |
| L8 | API design | `api/` |

---

## Directory Structure

```
l4/laws/
├── __init__.py          # Exports: check_compliance, audit_org
├── compliance.py        # Compliance checking functions
├── audit.py             # Full compliance audit
└── constants.py         # Law definitions, fee ranges
```

---

## Key Files

### constants.py

```python
# The 8 Laws
LAWS = {
    "L1": "Respect schema",
    "L2": "Register to exist",
    "L3": "No direct DB access",
    "L4": "Cross-org via membrane",
    "L5": "Hash-based identity",
    "L6": "Receiver validates",
    "L7": "Membrane fees",
    "L8": "WebSocket only",
}

# Fee constraints
MIN_FEE_RATE = 0.01  # 1%
MAX_FEE_RATE = 0.05  # 5%

# Schema version
REQUIRED_SCHEMA_VERSION = "1.8.1"
```

### compliance.py

```python
from l4.schema import validate_node, validate_link
from l4.registry import verify_hash, get_citizen

def check_stimulus_compliance(stimulus) -> ComplianceResult:
    """Check if a stimulus complies with all laws."""
    violations = []

    # L1: Schema
    for node in stimulus.nodes:
        if not validate_node(node).is_valid:
            violations.append("L1: Schema violation")

    # L2: Registered
    if not get_citizen(stimulus.sender_id):
        violations.append("L2: Sender not registered")

    # L5: Hash identity
    if "jwt" in str(stimulus.payload).lower():
        violations.append("L5: Raw JWT detected")

    hash_result = verify_hash(stimulus.identity_hash, stimulus.node_id)
    if not hash_result.valid:
        violations.append("L5: Invalid hash")

    # L7: Fee (if cross-org)
    if stimulus.source_org != stimulus.target_org:
        if stimulus.fee < stimulus.value * MIN_FEE_RATE:
            violations.append("L7: Fee below minimum")

    return ComplianceResult(
        compliant=len(violations) == 0,
        violations=violations
    )
```

### audit.py

```python
def audit_org(org_id: str, sample_size: int = 100) -> AuditReport:
    """Full compliance audit for an org."""
    stimuli = get_recent_stimuli(org_id, limit=sample_size)

    results = []
    for stimulus in stimuli:
        result = check_stimulus_compliance(stimulus)
        results.append(result)

    return AuditReport(
        org_id=org_id,
        total_checked=len(stimuli),
        compliant=sum(1 for r in results if r.compliant),
        violations=aggregate_violations(results)
    )
```

---

## Integration Points

| Consumer | What They Use | How |
|----------|---------------|-----|
| Membrane (mind-ops) | check_stimulus_compliance() | Before routing |
| L4 API | compliance endpoints | For audit requests |
| CLI tools | audit_org() | For manual audits |

---

## No Code for L3, L4, L8

These laws are enforced by architecture, not code:

- **L3**: No connection exists between org databases
- **L4**: Network topology routes through membrane
- **L8**: API only exposes WebSocket endpoints

Verification is via infrastructure audit, not runtime code.

---

## Related

- `l4/schema/` — L1 enforcement
- `l4/registry/` — L2, L5 enforcement
- `economy/` — L7 enforcement (future)
- `api/` — L8 enforcement
