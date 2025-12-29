# HEALTH: L4 Schema

```
STATUS: DESIGNING
PURPOSE: Runtime health checks for schema compliance
```

---

## Health Signals

| Signal | Check | Healthy | Degraded | Failed |
|--------|-------|---------|----------|--------|
| **Schema loaded** | Schema can be parsed | Loads in <100ms | Loads in <1s | Parse error |
| **Version current** | Matches protocol version | Exact match | Minor diff | Major diff |
| **Models valid** | Pydantic models generate | All generate | Some warnings | Generation fails |

---

## Health Check Procedures

### check_schema_loadable

```python
def check_schema_loadable() -> HealthResult:
    """Verify schema.yaml can be loaded and parsed."""
    try:
        start = time.time()
        schema = load_schema()
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

### check_version_current

```python
def check_version_current() -> HealthResult:
    """Verify local schema version matches protocol."""
    local = get_local_schema_version()
    protocol = get_protocol_schema_version()

    compatibility = check_version_compatibility(local, protocol)

    if compatibility == EXACT_MATCH:
        return HealthResult.HEALTHY
    elif compatibility == MINOR_DIFF:
        return HealthResult.DEGRADED
    else:
        return HealthResult.FAILED
```

### check_models_valid

```python
def check_models_valid() -> HealthResult:
    """Verify Pydantic models can be generated from schema."""
    try:
        models = generate_models_from_schema()

        # Try creating instances
        NodeBase(id="test", node_type="actor", weight=1.0, energy=1.0)
        Link(source_id="a", target_id="b", polarity=0.5, hierarchy=0.0, permanence=0.5)

        return HealthResult.HEALTHY
    except ValidationError as e:
        return HealthResult.DEGRADED(str(e))
    except Exception as e:
        return HealthResult.FAILED(str(e))
```

---

## Monitoring

| Metric | Type | Alert Threshold |
|--------|------|-----------------|
| schema_load_time_ms | gauge | > 1000ms |
| schema_version_drift | counter | > 0 (protocol mismatch) |
| validation_errors_total | counter | > 0 per minute |

---

## Recovery Actions

| Failure | Automatic Recovery | Manual Recovery |
|---------|-------------------|-----------------|
| Schema parse error | None | Fix schema.yaml |
| Version mismatch | None | Update to protocol version |
| Model generation fail | None | Check Pydantic compatibility |
| Validation errors | Log and reject | Review and fix data |

---

## Related

- `VALIDATION_Schema.md` — What we're checking
- `IMPLEMENTATION_Schema.md` — Where checks run
- `.mind/state/SYNC_Project_State.md` — Overall health status
