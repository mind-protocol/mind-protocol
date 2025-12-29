# HEALTH: L4 Laws

```
STATUS: DESIGNING
PURPOSE: Runtime health checks for law enforcement
```

---

## Health Signals

| Signal | Check | Healthy | Degraded | Failed |
|--------|-------|---------|----------|--------|
| **Compliance rate** | Sample stimulus compliance | >99% | 95-99% | <95% |
| **Hash verification working** | Registry responds to verify | <100ms | <1s | Timeout |
| **Fee collection active** | Fees being deducted | Positive revenue | Zero revenue | Errors |
| **WebSocket only** | No REST routes exist | 0 REST routes | N/A | Any REST route |

---

## Health Check Procedures

### check_compliance_rate

```python
def check_compliance_rate(sample_size: int = 100) -> HealthResult:
    """Sample recent stimuli and check compliance rate."""
    stimuli = get_recent_stimuli(limit=sample_size)
    compliant = sum(1 for s in stimuli if check_stimulus_compliance(s).compliant)
    rate = compliant / len(stimuli)

    if rate >= 0.99:
        return HealthResult.HEALTHY
    elif rate >= 0.95:
        return HealthResult.DEGRADED(f"Compliance rate: {rate:.1%}")
    else:
        return HealthResult.FAILED(f"Compliance rate: {rate:.1%}")
```

### check_hash_verification

```python
def check_hash_verification() -> HealthResult:
    """Verify hash verification is working."""
    try:
        start = time.time()

        # Create test hash
        test_jwt = "test_jwt_" + str(time.time())
        test_node_id = "test_node"
        test_hash = sha256(test_jwt + test_node_id)

        # Register temporary test citizen
        register_test_citizen(test_jwt)

        # Verify
        result = verify_hash(test_hash, test_node_id)
        elapsed = time.time() - start

        # Cleanup
        delete_test_citizen()

        if result.valid and elapsed < 0.1:
            return HealthResult.HEALTHY
        elif result.valid and elapsed < 1.0:
            return HealthResult.DEGRADED(f"Slow: {elapsed:.0f}ms")
        else:
            return HealthResult.FAILED("Verification failed")

    except Exception as e:
        return HealthResult.FAILED(str(e))
```

### check_fee_collection

```python
def check_fee_collection() -> HealthResult:
    """Verify fees are being collected."""
    recent_fees = get_recent_fees(hours=1)

    if len(recent_fees) > 0 and sum(f.amount for f in recent_fees) > 0:
        return HealthResult.HEALTHY
    elif len(recent_fees) == 0:
        return HealthResult.DEGRADED("No recent cross-org traffic")
    else:
        return HealthResult.FAILED("Fees not being collected")
```

### check_websocket_only

```python
def check_websocket_only() -> HealthResult:
    """Verify no REST endpoints exist."""
    routes = get_all_api_routes()
    rest_routes = [r for r in routes if r.protocol != "websocket"]

    if len(rest_routes) == 0:
        return HealthResult.HEALTHY
    else:
        return HealthResult.FAILED(f"Found {len(rest_routes)} REST routes")
```

---

## Monitoring

| Metric | Type | Alert Threshold |
|--------|------|-----------------|
| compliance_rate | gauge | < 0.95 |
| hash_verification_time_ms | histogram | p99 > 1000ms |
| fees_collected_total | counter | 0 for >1 hour |
| law_violations_by_type | counter | Any > 0 |

---

## Law Violation Alerts

| Law | Alert Condition | Severity |
|-----|-----------------|----------|
| L1 | Schema violation detected | Warning |
| L2 | Unregistered sender | Warning |
| L5 | Raw JWT detected | Critical |
| L5 | Hash mismatch spike | High |
| L7 | Fee bypass detected | Critical |
| L8 | REST endpoint found | Critical |

---

## Recovery Actions

| Failure | Automatic Recovery | Manual Recovery |
|---------|-------------------|-----------------|
| Low compliance rate | Alert and log violations | Investigate cause |
| Hash verification slow | Scale registry | Check database |
| Fee collection stopped | Alert | Check economy module |
| REST endpoint found | Block route | Remove from code |

---

## Related

- `VALIDATION_Laws.md` — What we're checking
- `IMPLEMENTATION_Laws.md` — Where checks run
- `docs/compliance/PATTERNS_Compliance.md` — Developer guidance
