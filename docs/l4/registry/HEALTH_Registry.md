# HEALTH: L4 Registry

```
STATUS: DESIGNING
PURPOSE: Runtime health checks for registry integrity
```

---

## Health Signals

| Signal | Check | Healthy | Degraded | Failed |
|--------|-------|---------|----------|--------|
| **Registry accessible** | Can query registry | <100ms response | <1s response | Timeout/error |
| **Integrity valid** | All invariants hold | 0 violations | Soft constraint issues | Critical violations |
| **Endpoints reachable** | Sample endpoint checks | All respond | Some slow | None respond |

---

## Health Check Procedures

### check_registry_accessible

```python
def check_registry_accessible() -> HealthResult:
    """Verify registry can be queried."""
    try:
        start = time.time()
        orgs = list_orgs()
        elapsed = time.time() - start

        if elapsed < 0.1:
            return HealthResult.HEALTHY
        elif elapsed < 1.0:
            return HealthResult.DEGRADED
        else:
            return HealthResult.FAILED
    except Exception as e:
        return HealthResult.FAILED(str(e))
```

### check_integrity

```python
def check_integrity() -> HealthResult:
    """Verify all registry invariants."""
    violations = verify_registry_integrity()

    critical = [v for v in violations if v.startswith("V")]
    soft = [v for v in violations if v.startswith("S")]

    if not critical and not soft:
        return HealthResult.HEALTHY
    elif not critical:
        return HealthResult.DEGRADED(f"{len(soft)} soft issues")
    else:
        return HealthResult.FAILED(f"{len(critical)} critical violations")
```

### check_endpoints_reachable

```python
def check_endpoints_reachable(sample_size: int = 5) -> HealthResult:
    """Sample endpoint connectivity."""
    endpoints = sample_endpoints(sample_size)
    results = [ping_endpoint(e) for e in endpoints]

    reachable = sum(1 for r in results if r.success)
    ratio = reachable / len(endpoints)

    if ratio == 1.0:
        return HealthResult.HEALTHY
    elif ratio >= 0.5:
        return HealthResult.DEGRADED(f"{reachable}/{len(endpoints)} reachable")
    else:
        return HealthResult.FAILED(f"Only {reachable}/{len(endpoints)} reachable")
```

---

## Monitoring

| Metric | Type | Alert Threshold |
|--------|------|-----------------|
| registry_query_time_ms | gauge | > 1000ms |
| registry_citizens_total | gauge | N/A (info) |
| registry_orgs_total | gauge | N/A (info) |
| registry_violations_total | counter | > 0 |
| endpoint_unreachable_count | counter | > 10% of total |

---

## Recovery Actions

| Failure | Automatic Recovery | Manual Recovery |
|---------|-------------------|-----------------|
| Registry unreachable | Retry with backoff | Check L4 graph connection |
| Integrity violation | Log and alert | Fix data, run migration |
| Endpoints unreachable | None (external) | Contact org operators |

---

## Audit Log

All registry mutations are logged:

```python
{
    "timestamp": "2024-12-28T10:00:00Z",
    "action": "register_citizen",
    "actor": "system",
    "citizen_id": "abc123",
    "org_id": "org456",
    "result": "success"
}
```

---

## Related

- `VALIDATION_Registry.md` — What we're checking
- `IMPLEMENTATION_Registry.md` — Where checks run
- `.mind/state/SYNC_Project_State.md` — Overall health status
