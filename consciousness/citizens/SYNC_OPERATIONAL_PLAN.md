# Operational Plan: SafeBroadcaster + Dashboard SLOs

**Date:** 2025-10-30
**Status:** Architecture locked, ready for implementation
**Decision:** Option A - handoff.* schemas added (gated, Phase 1 producers)

---

## L4 Schemas Ingested ✅

**Citizen Awareness (10 events):**
- `presence.beacon` (1KB, 120/hr) - 60s heartbeat, TTL 90-120s
- `status.activity.emit` (4KB, 60/hr) - Mission/files/note
- `message.thread` (2KB, 300/hr) + `message.direct` (4KB, 600/hr)
- `bridge.email.inbound/outbound` (8KB/4KB, 300/hr)
- `handoff.offer/accept/decline/complete` (2-8KB, 30/hr) - **Schemas ready, producers NOT wired**

**Health Autopilot (6 events):**
- `health.link.ping/pong/snapshot/alert`
- `health.compliance.snapshot/alert`

**Total: 16 event schemas + governance policies**

---

## Root Cause: "No Nodes on Dashboard"

**NOT a dashboard problem** - it's a broadcaster reliability problem.

**Evidence:**
- `self.broadcaster` is None OR `is_available()` returns False
- Consciousness engines have data (felix: 376 nodes, atlas: 174 nodes)
- No `[Hook 2] Broadcasting graph.delta` logs
- Other events flow (`state_modulation.frame`, `mode.snapshot`)

---

## SafeBroadcaster Architecture

```python
class SafeBroadcaster:
    """
    Single choke-point for emissions:
    - Readiness gating (no cold-start drops)
    - Spill & flush on failure (no silent loss)  
    - Self-reporting to health.compliance
    """

    async def start(self):
        await self.ws.connect()        # Retry with backoff
        await self.ws.ready.wait()     # Gate engine on readiness

    async def safe_emit(self, event):
        if not self.ws.is_available():
            self.spill.append(event)   # Durable buffer
            await self.health_bus.inject({
                "type": "health.compliance.snapshot",
                "content": {"top_rejects": [["ws_not_ready", 1]]}
            })
            return False
        await self.ws.send(event)
        return True
```

---

## Boot Order (Prevents None Condition)

```
1. L4 + governance ingestors
2. WebSocket server → bus.ready broadcast
3. SafeBroadcaster → waits for ws.ready  
4. Consciousness engines (gated on SafeBroadcaster)
5. health.echo + prober + compliance
```

**Key:** Gate engine start on `ws.ready` - no more "broadcaster is None"

---

## Dashboard SLOs

**Link Health:**
- Ack rate ≥ 0.99 (1-min)
- p95 RTT ≤ 250ms; p99 ≤ 600ms
- Route mismatches = 0

**Compliance:**
- Reject rate ≤ 2% steady-state
- Top reasons visible

**Presence/Status:**
- Stale if last_seen > ttl_s
- UI latency < 250ms beacon→card

---

## Implementation Checklist

**Critical Path:**
- [ ] SafeBroadcaster with spill/flush
- [ ] Boot order enforcement
- [ ] Heartbeat deltas (emit even when idle)

**Health Wiring:**
- [ ] health.prober → citizen/*, health/*, message/*
- [ ] health.echo listening on all topics
- [ ] health.compliance observing membrane.reject

**Dashboard:**
- [ ] dashboard.state.emit aggregator (1Hz)
- [ ] UI subscribes to single topic
- [ ] SLO alerts on change-points

---

## Runbook

1. **Validate L4** - Schemas + governance present
2. **Boot in order** - Wait for ws.ready
3. **Fire probes** - Expect ack≈1.0
4. **Send presence** - Card appears <250ms
5. **Trigger reject** - See in compliance.snapshot
6. **Kill WS** - Verify spill/flush recovery

---

## Assignment

**Felix:** SafeBroadcaster implementation
**Atlas:** Health wiring + dashboard aggregator  
**Iris:** UI subscription to dashboard.state.emit
**Victor:** Operational validation + boot order

**Philosophy:** The membrane proves its own pulse. Health events explain why (ack↓, reject↑, route mismatch). No guessing.
