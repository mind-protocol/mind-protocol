# Connector Capability Card: <name>

**Component Handle:** `<namespace>:<slug>` (e.g., `service:fe_errors`, `telegram:mtproto`)
**Author:** <team/person>
**Status:** draft | approved | active
**Date:** <YYYY-MM-DD>

---

## Direction

- [ ] Inbound (external system → bus)
- [ ] Outbound (bus → external system)
- [ ] Bidirectional

---

## Events

### Emitted

- `<channel>.<event>` - <description>

### Consumed

- `<channel>.<event>` - <description>

---

## Provenance

What can we assert about the source?

- **Source application:** <app name>
- **Environment:** <prod/staging/dev>
- **User/citizen mapping:** <available | requires learning | none>

---

## Security

- **Secrets:** <list secrets needed>
  - Vault path: `connectors/<component>/<secret_name>`
- **Redaction:** <what must be redacted - tokens, PII, credentials, etc>
- **Auth scopes:** <OAuth scopes, API keys, permissions required>
- **Consent record:** <how consent is verified - required for executors>

---

## Rate/Volume

- **Expected QPS:** <average queries per second>
- **Burst capacity:** <peak QPS>
- **Backpressure behavior:** <drop oldest | spool to disk | circuit break>

---

## Evidence

What raw artifacts can we attach or hash?

- <examples: stack traces, diffs, tx IDs, screenshots, logs, etc>
- **Storage:** <inline | object store reference>
- **Retention:** <how long kept>

---

## Failure Policy

- **Retry strategy:** <exponential backoff, max retries, etc>
- **Spool:** <to disk, to database, max size>
- **Circuit breaker:** <failure threshold, recovery conditions>

---

## Pattern

Which connector pattern does this follow?

- [ ] **Watcher** (pull → normalize → emit)
- [ ] **Listener** (receive → normalize → emit)
- [ ] **Executor** (consume bus → call external → emit result)

---

## Implementation Notes

<Any special considerations, edge cases, dependencies>

---

## DoD Tests

- [ ] **Shape conformance:** Valid JSON envelopes
- [ ] **Idempotency:** Replay produces same graph deltas
- [ ] **Rate limit:** Per-fingerprint throttling works
- [ ] **Replay:** Deterministic from same inputs
- [ ] **Security:** Secrets redacted, consent enforced (executors)
- [ ] **Backpressure:** Queue fills gracefully, no crashes
- [ ] **Observability:** Metrics exposed, dashboards configured

---

## Approval

- [ ] Security review completed
- [ ] Privacy review completed (if PII involved)
- [ ] Architecture review completed
- [ ] Approved by: <name, date>

---

## Rollout Plan

1. **Shadow mode** (staging, 1 week)
   - Start date: <YYYY-MM-DD>
   - Verification: <what to check>

2. **Sampled mode** (prod, 5%, 1 week)
   - Start date: <YYYY-MM-DD>
   - Metrics to track: <usefulness, harm, κ trends>

3. **Full mode** (prod, 100%)
   - Start date: <YYYY-MM-DD>
   - Success criteria: <what defines success>

---

## Maintenance

- **On-call contact:** <team/person>
- **Runbook location:** `docs/connectors/<component>/RUNBOOK.md`
- **Secret rotation:** <quarterly | on-demand>
- **Consent audit:** <quarterly | annually> (for executors)
