# Connector Capability Card: Frontend Errors

**Component Handle:** `service:fe_errors`
**Author:** Atlas (Infrastructure Engineer)
**Status:** draft
**Date:** 2025-10-29

---

## Direction

- [x] Inbound (external system → bus)
- [ ] Outbound (bus → external system)
- [ ] Bidirectional

---

## Events

### Emitted

- `signals.fe.error` - Frontend JavaScript/TypeScript errors from production/staging environments

### Consumed

- None (inbound only)

---

## Provenance

What can we assert about the source?

- **Source application:** Mind Protocol Dashboard (Next.js)
- **Environment:** prod | staging (from request headers)
- **User/citizen mapping:** None (anonymous error reports, engines learn patterns)

---

## Security

- **Secrets:**
  - None required (HTTP endpoint with public key verification)
  - Optional: API key for source authentication

- **Redaction:**
  - Authorization headers
  - Cookie values
  - Local storage contents
  - User PII in URLs (emails, names, IDs)
  - API tokens in error messages

- **Auth scopes:**
  - Public HTTP endpoint (rate-limited by IP + fingerprint)
  - Optional: HMAC signature verification for trusted sources

- **Consent record:**
  - Not required (operational telemetry)
  - User opt-out respected (don't send if opted out)

---

## Rate/Volume

- **Expected QPS:** 5-10 in normal operation
- **Burst capacity:** 100 QPS (during deployment or incident)
- **Backpressure behavior:**
  - Per-fingerprint rate limit (≥10s between identical errors)
  - Global rate limit per IP (100/minute)
  - Drop oldest from queue if >1000 pending

---

## Evidence

What raw artifacts can we attach or hash?

- Stack traces (redacted)
- Sourcemap context (mapped line numbers)
- Browser user agent
- URL + query params (PII redacted)
- Component tree (React/Next.js)
- Release version
- Timestamp

**Storage:** Inline for metadata, object store for full stack traces
**Retention:** 30 days

---

## Failure Policy

- **Retry strategy:**
  - Client-side: 3 retries with exponential backoff (1s, 2s, 4s)
  - Server-side: Spool to disk if bus unavailable

- **Spool:**
  - Local disk: `/var/spool/connectors/fe_errors/`
  - Max size: 100 MB (oldest deleted)
  - Background flush: Every 30s

- **Circuit breaker:**
  - Open after 10 consecutive failures
  - Half-open after 60s
  - Close after 3 successful flushes

---

## Pattern

Which connector pattern does this follow?

- [ ] **Watcher** (pull → normalize → emit)
- [x] **Listener** (receive → normalize → emit)
- [ ] **Executor** (consume bus → call external → emit result)

---

## Implementation Notes

**Client-side (Dashboard):**
- Error boundary captures React errors
- `window.onerror` captures global errors
- `window.onunhandledrejection` captures promise rejections
- Batch errors (max 10, flush every 5s)
- Fingerprint client-side (stable hash from stack)
- Redact PII before sending

**Server-side (Connector):**
- HTTP POST endpoint: `/api/errors`
- Validate shape (JSON schema)
- Apply server-side redaction (defense in depth)
- Dedupe by fingerprint
- Rate limit per fingerprint + per IP
- Emit to bus or spool

**Fingerprinting:**
```python
def compute_fingerprint(error):
    stable = {
        "error_type": error["type"],
        "message_template": error["message"].replace(/\d+/g, "N"),  # Normalize numbers
        "stack_top_5": error["stack_frames"][:5],  # Top 5 frames
        "component": error["component_stack"][0] if error["component_stack"] else None
    }
    return sha1(json.dumps(stable, sort_keys=True))
```

---

## DoD Tests

- [x] **Shape conformance:** Valid JSON envelopes (schema validation)
- [x] **Idempotency:** Same error → same fingerprint → single emission
- [x] **Rate limit:** Rapid duplicate errors → throttled correctly
- [x] **Replay:** Replaying same errors → deterministic deltas
- [x] **Security:** All secrets/PII redacted (verified with test data)
- [x] **Backpressure:** Queue fills → oldest dropped, no crashes
- [x] **Observability:** Metrics exposed, Grafana dashboard configured

---

## Approval

- [ ] Security review completed
- [ ] Privacy review completed
- [ ] Architecture review completed
- [ ] Approved by: <name, date>

---

## Rollout Plan

1. **Shadow mode** (staging, 1 week)
   - Start date: 2025-11-01
   - Verification: Envelopes valid, no PII leaks, fingerprinting stable

2. **Sampled mode** (prod, 5%, 1 week)
   - Start date: 2025-11-08
   - Metrics to track: Error detection latency, false positive rate, routing patterns

3. **Full mode** (prod, 100%)
   - Start date: 2025-11-15
   - Success criteria: <1% false positives, routing converges within 3 days

---

## Maintenance

- **On-call contact:** Atlas (Infrastructure) + Victor (Operations)
- **Runbook location:** `docs/connectors/fe_errors/RUNBOOK.md`
- **Secret rotation:** N/A (no secrets)
- **Consent audit:** N/A (operational telemetry)

---

## Example Payload

```json
{
  "type": "membrane.inject",
  "channel": "signals.fe.error",
  "ts": "2025-10-29T18:42:31.123Z",
  "id": "evt_a7f2b3c9e1d4f6a8...",
  "provenance": {
    "scope": "external",
    "emitter": "service:fe_errors"
  },
  "metadata": {
    "component": "service:fe_errors",
    "dedupe_key": "fp_abc123...",
    "fingerprint": "fp_abc123...",
    "env": "prod",
    "tags": ["ops", "frontend"]
  },
  "features_raw": {
    "urgency": 0.7,    // ERROR level
    "novelty": 0.6,    // First occurrence of this fingerprint
    "trust": 0.9       // Verified source
  },
  "payload": {
    "message": "Cannot read property 'data' of undefined",
    "error_type": "TypeError",
    "stack": "at Component.render (bundle.js:N:N)\nat ...",
    "url": "/dashboard",
    "user_agent": "Mozilla/5.0 (Chrome/120.0)",
    "release": "v2.3.1",
    "component_stack": ["DashboardLayout", "DataGrid", "CellRenderer"],
    "sourcemap_context": {
      "file": "components/DataGrid.tsx",
      "line": 234,
      "column": 12
    }
  }
}
```
