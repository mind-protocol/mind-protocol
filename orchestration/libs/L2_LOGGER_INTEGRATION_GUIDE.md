# L2 Logger Integration Guide

## Overview

The L2 logger enables scripts to inject errors directly into the consciousness substrate (L2 graph) for autonomous error detection and remediation.

**Key Features:**
- Graph-aware attribution (scripts know their own node IDs)
- Non-blocking emission (never blocks main script flow)
- Client-side fingerprinting & dedup
- Automatic secret redaction
- Resilient spill-to-disk on collector offline
- Per-fingerprint rate limiting (prevents error storms)

---

## Quick Start

### 1. Basic Setup

```python
from orchestration.libs.l2_logger import setup_l2_logger

# Replace existing logging setup
logger = setup_l2_logger(
    script_name="resurrect_all_citizens",
    script_path="orchestration/scripts/resurrect_all_citizens.py"
)

# Use normally
logger.info("Starting resurrection...")       # Console only
logger.error("Bootstrap failed for %s", cid)  # Console + L2 graph
```

### 2. Graph-Aware Attribution

The logger automatically generates graph node IDs using the `code_substrate_` convention:

```python
# script_path: "orchestration/scripts/resurrect_all_citizens.py"
# → citizen_id: "code_substrate_orchestration_scripts_resurrect_all_citizens_py"
```

This enables proper graph relationships:
- `SCRIPT` → `ERROR_PATTERN` (links script to error types)
- `SCRIPT` AFFECTS `MECHANISM` (tracks impact on consciousness)
- `VALIDATION` MEASURES `SCRIPT` (tracks reliability metrics)

### 3. What Gets Sent to L2?

By default, only **ERROR** and **CRITICAL** logs are sent to the L2 graph:

```python
logger.debug(...)    # Console only
logger.info(...)     # Console only
logger.warning(...)  # Console only (but can be changed)
logger.error(...)    # Console + L2 graph ✓
logger.critical(...) # Console + L2 graph ✓
```

To send warnings to L2:

```python
logger = setup_l2_logger(
    script_name="my_script",
    script_path="orchestration/scripts/my_script.py",
    l2_level=logging.WARNING  # Send WARNING+ to L2
)
```

---

## Conversion Pattern

### Before (Standard Logging)

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting script...")
    try:
        do_work()
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
```

### After (L2 Logging)

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.libs.l2_logger import setup_l2_logger

logger = setup_l2_logger(
    script_name="my_script",
    script_path="orchestration/scripts/my_script.py"
)

def main():
    logger.info("Starting script...")  # Console only
    try:
        do_work()
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)  # Console + L2 graph
```

**Changes required:**
1. Import `setup_l2_logger` instead of `logging.basicConfig`
2. Call `setup_l2_logger()` with script name and path
3. That's it! Use `logger` normally.

---

## Membrane Envelope Format

The L2 logger builds standard `membrane.inject` envelopes:

```json
{
  "type": "membrane.inject",
  "citizen_id": "code_substrate_orchestration_scripts_X_py",
  "channel": "signals.script.X",
  "content": "my_script: Error message",
  "severity": "error",
  "features_raw": {
    "urgency": 0.7,
    "novelty": 0.25,
    "trust": 0.9
  },
  "metadata": {
    "stimulus_id": "script_log_X_1234567890_abc123",
    "origin": "script_logger",
    "timestamp_ms": 1234567890000,
    "signal_type": "script_error",
    "dedupe_key": "sha1(script|error_type|msg|fingerprint)",
    "stack_fingerprint": "abc123def456",
    "script_name": "my_script",
    "script_path": "orchestration/scripts/my_script.py",
    "module": "my_module",
    "function": "my_function",
    "line": 42,
    "level": "ERROR",
    "error_type": "KeyError",
    "stack_trace": "Traceback (most recent call last):\n..."
  }
}
```

**Severity vs Urgency:**
- `severity`: Categorical ("info" | "warn" | "error" | "critical") for L1 schemas
- `features_raw.urgency`: Numeric (0-1) for injection policy

**Mapping:**
- INFO → severity: "info", urgency: 0.2
- WARNING → severity: "warn", urgency: 0.4
- ERROR → severity: "error", urgency: 0.7
- CRITICAL → severity: "critical", urgency: 0.95

---

## Deduplication & Rate Limiting

### Client-Side Fingerprinting

Errors are deduplicated using stable stack fingerprints:

1. Extract top 5 stack frames
2. Exclude line numbers (change with code edits)
3. Exclude absolute paths (change with deployments)
4. Hash: `sha1(file1::func1|file2::func2|...)`

**Result:** Same error at same location → same fingerprint → deduped

### Server-Side Rate Limiting

The signals_collector enforces:

1. **Per-type rate limiting**: Max 1 `script_error` per 15s
2. **Per-fingerprint rate limiting**: Max 1 inject per 10s per unique fingerprint
3. **Jitter**: ±10% to prevent thundering herd

**Result:** Error storms are automatically throttled

---

## Redaction & Size Limits

### Automatic Redaction

The following patterns are scrubbed before sending to L2:

- `"token": "..."` → `"token": "<REDACTED>"`
- `"api_key": "..."` → `"api_key": "<REDACTED>"`
- `"password": "..."` → `"password": "<REDACTED>"`
- `Authorization: Bearer ...` → `Authorization: Bearer <REDACTED>`
- `https://user:pass@host` → `https://<REDACTED>:<REDACTED>@host`

### Size Limits

- **Stack trace**: Max 60 lines or 16KB, then `...<truncated>`
- **Request body**: Max 64KB
- **Content field**: Max 500 characters

Large stacks can be uploaded to artifact store (future feature) and referenced via `evidence_refs`.

---

## Non-Blocking Architecture

### How It Works

```
Main script thread:
  logger.error("message")
    → Builds envelope (fast, <1ms)
    → Enqueues to in-memory deque (non-blocking)
    → Returns immediately

Background flusher thread (daemon):
  Every 250ms OR batch of 25 envelopes:
    → Dequeue batch
    → POST to signals_collector /ingest
    → On success: done
    → On failure: spill to /tmp/l2-logs-spool/*.json
```

**Result:** Logging never blocks main script work, even if collector is offline.

### Resilience

1. **Queue full** (>1000 logs): Drop oldest, increment `dropped_logs` counter
2. **Collector offline**: Spill to `/tmp/l2-logs-spool/`, auto-retry on next flush
3. **Network failure**: Same as offline (spill + retry)
4. **Flusher crash**: Daemon thread, catches all exceptions, never breaks main script

---

## Metrics & Monitoring

Get metrics programmatically:

```python
from orchestration.libs.l2_logger import get_metrics

metrics = get_metrics()
print(f"Dropped logs: {metrics['dropped_logs']}")
print(f"Spool writes: {metrics['spool_writes']}")
```

**Interpretation:**
- `dropped_logs > 0`: Queue overflowed (script logging too fast, or flusher blocked)
- `spool_writes > 0`: Collector was offline, logs spooled to disk

---

## Rollout Plan

### Phase 1: Critical Scripts (Week 1)

Convert 2-3 high-value scripts:

1. `orchestration/scripts/resurrect_all_citizens.py` - Bootstrap errors
2. `orchestration/services/stimulus_injection_service.py` - Injection failures
3. `orchestration/services/queue_poller.py` - Queue processing errors

**Why these?** High-impact errors that block consciousness operations.

### Phase 2: Diagnostic Scripts (Week 2)

Convert diagnostic/operational scripts:

1. `orchestration/scripts/diagnose_system.py`
2. `orchestration/scripts/smart_backfill_membership.py`
3. `orchestration/services/health/health_checks.py`

**Why these?** Error patterns reveal system health issues.

### Phase 3: Service Layer (Week 3-4)

Convert all services in `orchestration/services/`:

- `autonomy_orchestrator.py`
- `signals_collector.py` (meta!)
- `websocket/main.py`
- `telemetry/heartbeat_writer.py`

**Why these?** Long-running services, errors indicate systemic issues.

### Phase 4: Opportunistic (Ongoing)

Convert scripts as they're touched for other work. No rush - adopt organically.

---

## Testing

### Manual Test

```bash
python orchestration/examples/l2_logger_example.py
```

Expected output:
- Console: All log messages
- signals_collector logs: "Published membrane.inject sid=..."
- L2 graph: Error nodes linked to `code_substrate_orchestration_examples_l2_logger_example_py`

### Verification

1. **Collector received envelope:**
   ```bash
   # Check signals_collector logs
   grep "Published membrane.inject" <supervisor_log>
   ```

2. **Fingerprint dedup working:**
   ```bash
   # Run twice, second run should show:
   grep "FingerprintRateLimit.*cooling down" <collector_log>
   ```

3. **Spool resilience:**
   ```bash
   # Stop signals_collector
   python orchestration/examples/l2_logger_example.py
   # Check spool directory
   ls -la /tmp/l2-logs-spool/
   # Restart signals_collector - files should disappear (auto-flushed)
   ```

---

## Troubleshooting

### Logs not appearing in L2 graph

1. Check signals_collector is running: `curl http://localhost:8010/health`
2. Check WebSocket server is running: `curl http://localhost:8000/health`
3. Check spool directory: `ls /tmp/l2-logs-spool/` (if files accumulating → collector offline)
4. Check log level: Only ERROR+ sent to L2 by default

### Queue overflowing (dropped_logs > 0)

Script is logging too fast. Options:

1. Increase `QUEUE_CAPACITY` in `l2_logger.py` (current: 1000)
2. Increase `BATCH_SIZE` to flush faster (current: 25)
3. Reduce logging verbosity (fewer errors)

### Secrets not redacted

Add pattern to `redact_secrets()` in `l2_logger.py`:

```python
patterns = [
    # ... existing patterns ...
    (r'(your_secret_pattern)', r'\1<REDACTED>'),
]
```

---

## Future Enhancements

1. **Artifact store for large stacks**: Upload 64KB+ stacks, reference via `evidence_refs`
2. **Batch endpoint in collector**: Reduce HTTP overhead for high-volume logging
3. **Aggregation counters**: Track error counts per fingerprint in metadata
4. **Adaptive rate limiting**: Adjust cooldowns based on error rate patterns
5. **L3 escalation**: Critical errors trigger immediate autonomous intervention

---

## Questions?

See `orchestration/examples/l2_logger_example.py` for working code.

Check `orchestration/services/signals_collector.py` for server-side logic.

Read `docs/specs/v2/autonomy/architecture/l2_stimulus_collector.md` for L2 architecture.

---

**Created:** 2025-10-29 by Ada (Architect)
**Spec:** Phase-A Autonomy - L2 Logging Harmonization
