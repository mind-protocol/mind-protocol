# Connector Blueprint: Adding External Integrations

**Version:** 1.0
**Date:** 2025-10-29
**Status:** Architectural Standard
**Author:** Nicolas Lester Reynolds & Luca Vellumhand
**Purpose:** Define standard mindset, process, and contract for adding ANY external integration to Mind Protocol

---

## 0. Mindset (3 Rules - Always)

### Rule 1: Pure Membrane

A connector **ONLY** emits/consumes bus messages. It NEVER writes the graph or calls engines directly.

**Why:** Engines decide; connectors provide evidence. This preserves causality, observability, and safety.

**In practice:**
- ✅ Emit `membrane.inject` with evidence
- ✅ Consume `tool.request.*` or `ui.action.*` messages
- ❌ NO direct graph writes
- ❌ NO direct engine calls
- ❌ NO routing decisions (engines learn routing via alignment + κ)

---

### Rule 2: Level-Invariant & Topology-Agnostic

The connector never chooses `citizen_id` or L1/L2. It sends **one neutral stimulus** with a stable `metadata.component` and the membrane + engines handle routing and learning.

**Why:** Routing is learned from outcomes (alignment + permeability), not hardcoded in connectors.

**In practice:**
- ✅ Emit stimulus with `metadata.component = "service:repo_watcher"`
- ✅ Let engines route based on semantic fit × κ
- ❌ NO hardcoded `citizen_id` selection
- ❌ NO manual L1/L2 targeting
- ❌ NO "if error_type == X, route to citizen Y" logic

---

### Rule 3: Zero-Constants

No hard thresholds inside connectors. Rate, severity, novelty, usefulness are **observations**. Gates/decisions live in engines (percentiles/EMAs).

**Why:** Adaptive thresholds per citizen/org, not fixed magic numbers.

**In practice:**
- ✅ Observe: `severity = 0.85` (from error level)
- ✅ Report: `features_raw: {urgency: 0.7, novelty: 0.6}`
- ❌ NO `if urgency > 0.8: alert()` (engine decides)
- ❌ NO `if error_count > 100: escalate()` (engine learns threshold)
- ❌ NO fixed rate limits (per-fingerprint percentile gates)

---

## 1. The Connector Process (7 Steps - Always Follow)

### Step 1: Capability Card (1 Page, Required)

**Before writing code**, fill this template:

```markdown
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

## Events

**Emitted:**
- `<channel>.<event>` - description

**Consumed:**
- `<channel>.<event>` - description

## Provenance

What can we assert?
- Source application: <app name>
- Environment: <prod/staging/dev>
- User/citizen mapping: <available | requires learning | none>

## Security

- Secrets: <list secrets needed, vault paths>
- Redaction: <what must be redacted - tokens, PII, etc>
- Auth scopes: <OAuth scopes, API keys, permissions required>
- Consent record: <how consent is verified>

## Rate/Volume

- Expected QPS: <average>
- Burst capacity: <peak>
- Backpressure behavior: <drop oldest | spool | circuit break>

## Evidence

What raw artifacts can we attach or hash?
- <stack traces, diffs, tx IDs, screenshots, etc>

## Failure Policy

- Retry: <strategy>
- Spool: <to disk, to DB, max size>
- Circuit breaker: <conditions>

## DoD Tests

- [ ] Shape conformance (valid JSON envelopes)
- [ ] Idempotency (replay produces same deltas)
- [ ] Rate limit (per-fingerprint, no spam)
- [ ] Replay (deterministic from same inputs)
- [ ] Security (secrets redacted, consent enforced)
```

**Approval required before implementation.**

---

### Step 2: Choose Connector Pattern (One of Three)

**Pattern A: Watcher** (pull → normalize → emit)

**Use for:** Files, logs, email inbox, wallets (polling blockchain), browsers (periodic scraping)

**Flow:**
```python
while True:
    raw_events = poll_external_system()  # Pull
    for event in raw_events:
        normalized = normalize(event)     # Normalize
        emit_stimulus(normalized)        # Emit
    sleep(interval)
```

**Examples:** repo watcher, log tailer, wallet monitor

---

**Pattern B: Webhook/Listener** (receive → normalize → emit)

**Use for:** FE errors (HTTP POST), Telegram inbound (webhook), SMS inbound (Twilio webhook)

**Flow:**
```python
@app.post("/webhook/fe_errors")
def handle_fe_error(request):
    raw_event = request.json()           # Receive
    normalized = normalize(raw_event)    # Normalize
    emit_stimulus(normalized)           # Emit
    return {"status": "ok"}
```

**Examples:** frontend error receiver, Telegram webhook handler, SMS receiver

---

**Pattern C: Executor** (consume bus → call external → emit result)

**Use for:** Email send, Telegram send, on-chain transfer, browser fetch (on-demand)

**Flow:**
```python
@bus.subscribe("tool.request.fetch")
def handle_fetch_request(request):
    # Consume from bus
    url = request.payload["url"]

    # Enforce policy gates
    if not check_consent(request.citizen_id, "browser_access"):
        emit_error("consent_required")
        return

    # Call external system
    result = browser.fetch(url)

    # Emit result
    emit_stimulus({
        "type": "tool.result.fetch",
        "request_id": request.id,
        "result": result
    })
```

**Examples:** email sender, Telegram messenger, Solana wallet executor, browser automation

---

### Step 3: Implement the Connector Contract

Use shared base class with:
- Non-blocking queue
- Redaction (secrets, PII)
- Dedupe (per fingerprint)
- Batch flush
- Spool-to-disk on failure
- Per-fingerprint rate limit

**Base class location:** `orchestration/libs/connector_base.py`

**Minimal implementation:**
```python
from orchestration.libs.connector_base import ConnectorBase

class RepoWatcher(ConnectorBase):
    def __init__(self):
        super().__init__(
            component="service:repo_watcher",
            channel="repo.commit"
        )

    def normalize(self, raw_commit):
        """Transform external format → neutral stimulus."""
        return {
            "repo": raw_commit["repository"]["name"],
            "branch": raw_commit["ref"].split("/")[-1],
            "commit": raw_commit["head_commit"]["id"],
            "author": raw_commit["head_commit"]["author"]["username"],
            "files": [f["filename"] for f in raw_commit["head_commit"]["modified"]],
            "diff_ref": store_diff(raw_commit)  # Object store, not inline
        }

    def poll(self):
        """Watcher-specific: pull from external system."""
        commits = github.fetch_recent_commits()
        for commit in commits:
            self.emit_normalized(commit)
```

---

### Step 4: Emit Neutral Stimuli

`membrane.inject` with `metadata.component`, `features_raw`, and **typed payload**.

**NEVER set `citizen_id`** - engines learn routing.

**Standard envelope:**
```json
{
  "type": "membrane.inject",
  "channel": "signals.<domain>.<event>",
  "ts": "2025-10-29T18:42:31.123Z",
  "id": "evt_<stable_hash>",
  "provenance": {
    "scope": "external",
    "emitter": "<component>"
  },
  "metadata": {
    "component": "<namespace:slug>",
    "dedupe_key": "<sha1-of-stable-fields>",
    "fingerprint": "<sha1-of-stack|path|schema>",
    "env": "prod|staging",
    "tags": ["ops", "health"]
  },
  "features_raw": {
    "urgency": 0.0,    // 0-1, from observation
    "novelty": 0.0,    // 0-1, from observation
    "trust": 0.0       // 0-1, source credibility
  },
  "payload": {
    // Event-specific fields
  }
}
```

**Example (FE error):**
```json
{
  "type": "membrane.inject",
  "channel": "signals.fe.error",
  "ts": "2025-10-29T18:42:31.123Z",
  "id": "evt_a7f2b3c9...",
  "provenance": {
    "scope": "external",
    "emitter": "service:fe_errors"
  },
  "metadata": {
    "component": "service:fe_errors",
    "dedupe_key": "sha1_of_stack_top_frames",
    "fingerprint": "sha1_of_error_type_stack",
    "env": "prod",
    "tags": ["ops", "frontend"]
  },
  "features_raw": {
    "urgency": 0.7,    // ERROR level
    "novelty": 0.6,    // First time this fingerprint
    "trust": 0.9       // Verified source
  },
  "payload": {
    "message": "Cannot read property 'x' of undefined",
    "error_type": "TypeError",
    "stack": "...",  // Redacted
    "url": "/dashboard",
    "user_agent": "Chrome/120.0",
    "release": "v2.3.1",
    "sourcemap_context": "..."
  }
}
```

---

### Step 5: Observability

Expose counters for monitoring:

**Required metrics:**
- `connector.<component>.emitted` - Total stimuli emitted
- `connector.<component>.deduped` - Duplicates filtered
- `connector.<component>.rate_limited` - Messages throttled
- `connector.<component>.spooled` - Messages spooled to disk
- `connector.<component>.failed_flush` - Failed bus emissions

**Logging:**
- Invalid messages with lint reason
- Rate limit violations (which fingerprint)
- Spool events (disk full, recovered)
- Secret redaction applied

**Dashboard:**
- Emission rate over time
- Fingerprint distribution (top 10)
- Queue depth
- Spool size

---

### Step 6: Dry-Run & Replay

**Before production:**

1. **Run against membrane emulator** (bus stub):
```bash
# Start emulator
python orchestration/tests/membrane_emulator.py

# Run connector in dry-run mode
CONNECTOR_DRY_RUN=true python orchestration/connectors/fe_errors/connector.py
```

2. **Verify conformance:**
   - All envelopes valid JSON
   - `id` stable (same input → same ID)
   - Dedupe working (duplicate input → single emission)
   - Rate limit working (rapid fingerprint → throttled)

3. **Replay test:**
```python
# Feed same inputs twice
for event in test_events:
    connector.handle(event)

# Second run should produce identical graph deltas
for event in test_events:
    connector.handle(event)

assert_graph_deltas_identical()
```

---

### Step 7: Graduated Rollout

**Phase 1: Shadow Mode**
```python
CONNECTOR_SHADOW=true  # Emits to bus, engines ignore
```
- Verify envelope shape
- Check for crashes/memory leaks
- Monitor queue depth

**Phase 2: Sampled Mode**
```python
CONNECTOR_SAMPLE_RATE=0.05  # 5% of stimuli processed
```
- Engines process subset
- Collect usefulness/harm signals
- Adjust if needed

**Phase 3: Full Mode**
```python
CONNECTOR_ENABLED=true  # Full emission
```
- Monitor usefulness/harm trends
- Watch κ evolution for this component
- Dashboard tracking component-specific routing

---

## 2. The Connector Contract (Implementation-Level)

### Envelope Requirements (Hard Contract)

**Every emitted event MUST:**

1. **Use `type` field (not `topic`):**
```json
{
  "type": "membrane.inject"  // ✅
  // NOT "topic": "..."
}
```

2. **Include stable `id`:**
```python
id = sha1(f"{type}|{component}|{dedupe_key}")
```

3. **Include `spec` version:**
```json
{
  "spec": {
    "name": "fe.error.v1",
    "rev": "1.0.0"
  }
}
```

4. **Be idempotent:**
```python
# Consumers MUST handle duplicate IDs gracefully
@idempotent_handler
def process_stimulus(event):
    if already_processed(event.id):
        return  # No-op on replay
    # ... process
```

---

### Hard Requirements (Must Implement)

**1. No Graph Writes**
```python
# ❌ NEVER
graph.create_node(...)
graph.create_edge(...)

# ✅ ALWAYS
bus.emit({"type": "membrane.inject", ...})
```

**2. Dedupe/Fingerprint (Client-Side)**
```python
def compute_fingerprint(event):
    """Stable hash ignoring line numbers, timestamps, etc."""
    stable_fields = {
        "error_type": event["error_type"],
        "stack_top_frames": event["stack"][:5],  # Top 5 frames only
        "url_path": event["url"].split("?")[0]   # Ignore query params
    }
    return sha1(json.dumps(stable_fields, sort_keys=True))
```

**3. Per-Fingerprint Rate Limit**
```python
class PerFingerprintRateLimiter:
    def __init__(self, min_interval=10.0):  # Learned, not fixed
        self.min_interval = min_interval
        self.last_emit = {}  # fingerprint → timestamp

    def should_emit(self, fingerprint):
        now = time.time()
        last = self.last_emit.get(fingerprint, 0)

        if now - last < self.min_interval:
            return False  # Rate limited

        self.last_emit[fingerprint] = now
        return True
```

**4. Bounded Queue (Drop Oldest)**
```python
from collections import deque

class BoundedQueue:
    def __init__(self, maxsize=1000):
        self.queue = deque(maxlen=maxsize)
        self.dropped_count = 0

    def push(self, item):
        if len(self.queue) >= self.queue.maxlen:
            self.dropped_count += 1
            # Oldest auto-dropped by deque
        self.queue.append(item)
```

**5. Secret Redaction**
```python
REDACT_PATTERNS = [
    r"Authorization: Bearer \S+",
    r"api_key=[^&\s]+",
    r"password=[^&\s]+",
    r"token=[^&\s]+",
]

def redact_secrets(text):
    for pattern in REDACT_PATTERNS:
        text = re.sub(pattern, "[REDACTED]", text)
    return text
```

**6. Spool-to-Disk on Failure**
```python
class SpoolManager:
    def __init__(self, spool_dir="/var/spool/connectors"):
        self.spool_dir = Path(spool_dir)

    def spool(self, event):
        """Write to disk when bus unavailable."""
        filepath = self.spool_dir / f"{event['id']}.json"
        with open(filepath, "w") as f:
            json.dump(event, f)

    def flush_spool(self, bus):
        """Background flusher."""
        for filepath in self.spool_dir.glob("*.json"):
            try:
                with open(filepath) as f:
                    event = json.load(f)
                bus.emit(event)
                filepath.unlink()  # Delete after successful emit
            except Exception as e:
                log.error(f"Flush failed: {e}")
                # Leave in spool for retry
```

**7. Size Limits (Cap Payloads)**
```python
MAX_PAYLOAD_SIZE = 64 * 1024  # 64 KB

def check_size(event):
    payload_json = json.dumps(event["payload"])
    if len(payload_json) > MAX_PAYLOAD_SIZE:
        # Put large artifact in object store
        artifact_id = store_artifact(event["payload"])
        event["payload"] = {"artifact_ref": artifact_id}
    return event
```

---

### For Executors (Outbound Actions)

**Additional requirements:**

**1. Policy Gates (Before Execution)**
```python
@enforce_consent
@enforce_allowlist
@enforce_budget
def execute_action(request):
    # Check consent
    if not consent_ledger.check(request.citizen_id, "email_send"):
        emit_error("consent_required")
        return

    # Check allowlist
    if request.payload["to"] not in allowed_domains:
        emit_error("domain_not_allowed")
        return

    # Check budget
    if budget_tracker.remaining(request.citizen_id) < cost:
        emit_error("budget_exceeded")
        return

    # Execute
    result = external_system.call(request)

    # Emit result
    emit_result(request.id, result)
```

**2. Never Execute on Untrusted Scope**
```python
def validate_scope(request):
    # Must have explicit citizen/org scope
    if request.provenance.scope not in ["citizen", "org"]:
        raise UntrustedScopeError("Execution requires trusted scope")

    # Must have signature/auth
    if not verify_signature(request):
        raise UnauthenticatedError("Execution requires auth")
```

---

## 3. Security & Identity (Always Enforce)

### Component Identity Only

**DON'T embed raw user IDs** - emit pseudonymous handles and let engines/citizens align via membrane learning.

```python
# ❌ BAD
{
  "user_id": "john.doe@company.com",  // PII
  "citizen_id": "felix"               // Hardcoded routing
}

# ✅ GOOD
{
  "metadata": {
    "component": "service:repo_watcher",
    "author_handle": "contributor_abc123"  // Pseudonymous
  }
  // Let engines learn: contributor_abc123 → felix (via alignment)
}
```

---

### Consent Ledger

**Before acting** (SMS/Telegram/email/transfer), check signed or explicit consent state per citizen/org.

```python
class ConsentLedger:
    def check(self, citizen_id, action_type):
        """Check if citizen consented to this action."""
        consent = db.query(
            "SELECT * FROM consents WHERE citizen_id = ? AND action_type = ?",
            citizen_id, action_type
        )

        if not consent:
            return False

        if consent.expires_at < now():
            return False

        return True

    def record_consent(self, citizen_id, action_type, expires_at):
        """Record explicit consent."""
        db.execute(
            "INSERT INTO consents (citizen_id, action_type, granted_at, expires_at) VALUES (?, ?, ?, ?)",
            citizen_id, action_type, now(), expires_at
        )
```

---

### Scoped Secrets

Store provider credentials in separate vault path per component; rotate + audit.

```python
# Vault structure:
# /mind-protocol/connectors/telegram_mtproto/api_id
# /mind-protocol/connectors/telegram_mtproto/api_hash
# /mind-protocol/connectors/telegram_mtproto/session_file

from orchestration.libs.vault import get_secret

class TelegramConnector(ConnectorBase):
    def __init__(self):
        super().__init__(component="telegram:mtproto")

        # Load secrets from vault
        self.api_id = get_secret("connectors/telegram_mtproto/api_id")
        self.api_hash = get_secret("connectors/telegram_mtproto/api_hash")

        # Never log secrets
        log.info(f"Initialized {self.component} (API ID: {self.api_id[:4]}***)")
```

---

## 4. Definition of Done (DoD) for Any Connector

**Before marking connector "complete":**

- [ ] **Valid JSON envelopes** - All emitted events pass schema validation
- [ ] **Idempotency proof** - Replay produces same graph deltas (tested)
- [ ] **Backpressure proof** - Queue fills → oldest dropped with counter, no crashes
- [ ] **Dedupe proof** - Identical inputs → one bus message, counter increases
- [ ] **Security verified** - Tokens redacted, PII minimized, consent enforced (for executors)
- [ ] **Observability wired** - Dashboards show emitted/deduped/limited/spooled per component
- [ ] **Capability Card approved** - Reviewed and signed off
- [ ] **Dry-run passed** - Emulator tests green
- [ ] **Sampled rollout** - 5% traffic processed, usefulness/harm collected
- [ ] **Full rollout** - 100% traffic, κ trends visible in dashboards

---

## 5. Connector Examples (Capability Cards)

### Example A: Backend Log Errors → L2

**Component:** `service:be_errors`
**Pattern:** Watcher/Listener
**Direction:** Inbound

**Emit:** `signals.be.error`

**Payload:**
```json
{
  "message": "Database connection timeout",
  "error_type": "TimeoutError",
  "stack": "[REDACTED]",
  "service": "api_server",
  "version": "v2.3.1",
  "host": "api-prod-3",
  "features_raw": {
    "urgency": 0.95,  // CRITICAL level
    "novelty": 0.3,   // Seen before
    "trust": 1.0      // Internal service
  }
}
```

**Notes:**
- Redact secrets in stack traces
- Fingerprint from top frames
- Urgency from level: INFO/WARN/ERROR/CRIT → 0.2/0.4/0.7/0.95
- Per-fingerprint rate limit (≥10s)

---

### Example B: Frontend Errors → L2

**Component:** `service:fe_errors`
**Pattern:** Listener (HTTP POST)
**Direction:** Inbound

**Emit:** `signals.fe.error`

**Payload:**
```json
{
  "message": "Cannot read property 'x' of undefined",
  "error_type": "TypeError",
  "url": "/dashboard",
  "user_agent": "Chrome/120.0",
  "stack": "at Component.render (bundle.js:1234:56)",
  "release": "v2.3.1",
  "sourcemap_context": "...",
  "features_raw": {
    "urgency": 0.7,
    "novelty": 0.8,
    "trust": 0.8
  }
}
```

**Notes:**
- Client-side PII redaction before sending
- Sample rate by environment (prod: 10%, staging: 100%)
- Per-fingerprint limit
- Sourcemap context for debugging

---

### Example C: Telegram Real Account (Bidirectional)

**Component:** `telegram:mtproto`
**Pattern:** Executor + Listener
**Direction:** Bidirectional

**Consume:** `ui.action.message.send`
```json
{
  "type": "ui.action.message.send",
  "channel": "telegram",
  "to": "citizen:felix",
  "text": "Build complete: vector weights implemented ✅"
}
```

**Emit Inbound:** `ui.message.received`
```json
{
  "type": "ui.message.received",
  "channel": "telegram",
  "from": "citizen:ada",
  "text": "Felix - need spec review on SubEntity emergence",
  "chat_id": "...",
  "message_id": 12345
}
```

**IMPORTANT NOTES:**
- Use official MTProto library
- Session files are secrets (vault storage)
- Respect Telegram ToS (rate limits, no spam)
- **Strong disclaimer and explicit consent required**
- Throttle outbound (max N messages/minute per citizen)
- Strong sandbox to prevent unintended mass messaging
- **Never mint accounts** - ops must onboard real accounts explicitly
- Thread mapping (chat_id → citizen conversation context)

---

### Example D: Solana Wallet (Bidirectional)

**Component:** `wallet:solana`
**Pattern:** Watcher + Executor
**Direction:** Bidirectional

**Emit Inbound:** `ledger.transfer.detected`
```json
{
  "type": "ledger.transfer.detected",
  "tx": "5KZB...xyz",
  "from": "addr123...",
  "to": "addr456...",
  "mint": "$MIND",
  "amount": 1000,
  "slot": 123456789,
  "confirmations": 32,
  "features_raw": {
    "urgency": 0.5,
    "novelty": 0.6,
    "trust": 1.0
  }
}
```

**Consume:** `tool.request.transfer`
```json
{
  "type": "tool.request.transfer",
  "from_wallet": "citizen:felix",
  "to": "addr789...",
  "mint": "$MIND",
  "amount": 100,
  "memo": "Reward for contribution"
}
```

**Emit Result:** `tool.result.transfer`
```json
{
  "type": "tool.result.transfer",
  "request_id": "req_abc123",
  "status": "success",
  "tx": "9XYZ...abc",
  "evidence_refs": ["tx:9XYZ...abc"]
}
```

**CRITICAL SECURITY:**
- Private keys **NEVER** on engine
- Use external signer or MPC
- Consent + multi-sig required for transfers
- Rate limits (max transfers/hour)
- Spend limits (max amount/day)
- Allowlist for recipient addresses
- Audit log for all transfer attempts

---

### Example E: Repository Watcher

**Component:** `service:repo_watcher`
**Pattern:** Watcher (webhook or polling)
**Direction:** Inbound

**Emit:** `repo.commit.detected`
```json
{
  "type": "repo.commit.detected",
  "repo": "mind-protocol/mindprotocol",
  "branch": "main",
  "commit": "abc123...",
  "author": "contributor_xyz",
  "files": [
    "orchestration/mechanisms/subentity_emergence.py",
    "tests/test_emergence.py"
  ],
  "diff_ref": "s3://diffs/abc123.diff",  // Object store, not inline
  "features_raw": {
    "urgency": 0.4,
    "novelty": 0.7,
    "trust": 0.9
  }
}
```

**Notes:**
- Attach `diff_ref` (object store key), not raw diff (size limits)
- Map author → citizen via membrane learning (not in connector)
- Fingerprint from commit SHA
- Watch multiple repos from manifest

---

## 6. Where Membranes & Routing Come In

**Critical insight:** Your connector emits once. Engines learn routing.

### Alignment Learning (What Maps to What)

**From connector evidence:**
```json
{
  "component": "service:repo_watcher",
  "payload": {
    "files": ["orchestration/mechanisms/subentity_emergence.py"]
  }
}
```

**Engines detect fit signals:**
- Semantic fit: "subentity_emergence" → felix.consciousness_implementer (Q85 threshold)
- Usage overlap: Commits often co-occur with felix.builder activity
- Boundary strides: TRACE explicitly links commit → "implements Principle 7"

**Alignment materializes (record-gated):**
```cypher
CREATE (component:ExternalSource {id: "service:repo_watcher"})
CREATE (felix_builder:SubEntity {id: "felix.builder"})
CREATE (component)-[:CORRESPONDS_TO {
  fit_sem: 0.87,
  fit_use: 0.72,
  materialized_at: "2025-10-29T..."
}]->(felix_builder)
```

---

### Permeability Learning (How Much Gets Through)

**Initial state (at materialization):**
```python
k_up = median([m.k_up for m in existing_membranes(citizen)])  # ~0.5
k_down = median([m.k_down for m in existing_membranes(citizen)])  # ~0.5
```

**Learning from outcomes:**

**Positive outcome (commit helpful):**
```python
on_event("mission.completed", {
  "evidence_refs": ["commit:abc123"],
  "usefulness": 0.85
}):
  membrane = get_membrane(repo_watcher → felix.builder)

  # Increase κ_down (routing commits to Felix worked well)
  membrane.k_down += learning_rate * (0.85 - ema_usefulness)

  # Also increase κ_up (Felix's work valuable to org)
  membrane.k_up += learning_rate * 0.85 * 0.5
```

**Negative outcome (noisy commits):**
```python
on_event("harm.detected", {
  "source": "service:repo_watcher",
  "harm_type": "noise_overload"
}):
  membrane = get_membrane(repo_watcher → felix.builder)

  # Decrease κ_down (routing too many noisy commits)
  membrane.k_down -= learning_rate * harm_severity
```

**Result:** Over time, repo_watcher → felix.builder routing adapts:
- High κ for helpful commit types (implementations, fixes)
- Low κ for noisy commit types (formatting, typos)
- **All learned from outcomes, not hardcoded**

---

## 7. Skeleton File Layout (Keep It Boring & Repeatable)

```
orchestration/
  libs/
    stimuli.py                 # Shared bus client (already verified)
    connector_base.py          # Queue, flush, dedupe, redact, rate-limit
    vault.py                   # Secret management

  connectors/
    fe_errors/
      capability_card.md       # Filled template
      connector.py             # Listener → emit signals.fe.error
      tests/
        test_conformance.py
        test_replay.py
      README.md

    repo_watcher/
      capability_card.md
      connector.py             # Watcher → emit repo.commit.detected
      config.yaml              # Repos to watch
      tests/
      README.md

    telegram_mtproto/
      capability_card.md
      connector.py             # Bidirectional
      secrets.sample.env       # Template for vault secrets
      consent_template.md      # Citizen consent form
      tests/
      README.md

    # ... other connectors

  tests/connectors/
    test_contract_conformance.py   # JSON, idempotency, limits
    test_replay.py                  # Deterministic replay
    membrane_emulator.py            # Bus stub for dry-run

docs/
  connectors/
    CONNECTOR_BLUEPRINT.md          # This document
    CAPABILITY_CARD_TEMPLATE.md     # Blank template
    EVENT_SCHEMAS.md                # JSON shapes for all events
```

---

## 8. Cut-Over Checklist (Per Connector)

**Phase 0: Design**
- [ ] Capability Card drafted
- [ ] Security review completed
- [ ] Consent mechanism designed (for executors)
- [ ] Capability Card approved

**Phase 1: Implementation**
- [ ] Contract unit tests passing (shape, idempotency, limits)
- [ ] Dedupe logic verified
- [ ] Rate limiting verified
- [ ] Secret redaction verified
- [ ] Spool-to-disk verified

**Phase 2: Testing**
- [ ] Dry-run on emulator green
- [ ] Replay test deterministic
- [ ] Load test (backpressure, no crashes)
- [ ] Security scan passed

**Phase 3: Rollout**
- [ ] Shadow mode in staging (1 week)
- [ ] Sampled mode in prod (5%, 1 week)
- [ ] Usefulness/harm signals collected
- [ ] κ trends visible in dashboards
- [ ] Full mode enabled
- [ ] Monitoring alerts configured

**Phase 4: Maintenance**
- [ ] Runbook created (troubleshooting, restart procedures)
- [ ] On-call rotation knows how to debug
- [ ] Quarterly secret rotation scheduled
- [ ] Consent audit scheduled (for executors)

---

## Summary

### Mindset (3 Rules)
1. **Pure membrane** - Emit/consume bus only, no direct writes
2. **Level-invariant** - Never choose citizen_id or L1/L2, engines learn routing
3. **Zero-constants** - Observe, don't decide; gates in engines

### Process (7 Steps)
1. Capability Card (1 page, required approval)
2. Choose pattern (Watcher | Listener | Executor)
3. Implement Contract (base class, dedupe, redact, spool)
4. Emit neutral stimuli (metadata.component, no routing)
5. Observability (counters, dashboards)
6. Dry-run & Replay (emulator, determinism tests)
7. Graduated rollout (shadow → sampled → full)

### Contract (Implementation)
- Standard envelope (type, id, spec, provenance, metadata, features_raw, payload)
- Hard requirements (no writes, dedupe, rate limit, redact, spool, size limits)
- Security (consent, allowlist, budget for executors)

### Examples
- 9 connector types shown with complete capability cards
- All fit same pattern (watcher/listener/executor)
- All learn routing via alignment + permeability (no hardcoding)

---

**If every connector follows this blueprint, teams add external integrations the SAME WAY every time - membrane-first, zero-constants, level-invariant - without inventing side channels.**
