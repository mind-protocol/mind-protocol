# SafeBroadcaster Pattern

**Purpose:** Harden the `graph.delta.*` emission path so dashboard never shows "0 nodes" due to broadcaster unavailability

**Problem:** Current `self.broadcaster is None` or `is_available() == False` silently drops events → dashboard shows empty even when graph is active

**Solution:** Single choke-point broadcaster with spill/flush/self-report that gates engine start on WebSocket readiness

---

## Architecture

```
Consciousness Engine
       ↓
SafeBroadcaster ← ws_client (WebSocket connection)
       ↓          ← spill (durable ring buffer: SQLite/file)
       ↓          ← health_bus (for self-reporting failures)
       ↓
WebSocket Server
       ↓
Dashboard (subscribes to graph.delta.*)
```

**Key invariant:** Engine ticks **cannot start** until `ws.ready == True`

---

## Implementation

```python
# orchestration/adapters/ws/safe_broadcaster.py

import asyncio
import logging
from collections import deque
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SafeBroadcaster:
    """
    Hardened broadcaster that ensures graph.delta.* events always find a home.

    Features:
    - Gates engine start on ws.ready
    - Spills to durable buffer on failure
    - Flushes spill on reconnect
    - Self-reports failures to health.compliance.*
    """

    def __init__(self, ws_client, spill_path: str, health_bus):
        self.ws = ws_client              # WebSocket client
        self.spill_path = spill_path      # SQLite or file path for ring buffer
        self.spill = deque(maxlen=10000)  # In-memory spill (10K events max)
        self.health_bus = health_bus      # For self-reporting
        self.ready = asyncio.Event()

        # Metrics
        self.emit_count = 0
        self.spill_count = 0
        self.flush_count = 0

    async def start(self):
        """Connect to WebSocket with backoff and retry"""
        attempt = 0
        while True:
            try:
                await self.ws.connect()
                await self.ws.wait_until_ready()

                # Broadcast ready state
                await self._self_report("broadcaster_ready", success=True)
                self.ready.set()

                logger.info("[SafeBroadcaster] Ready - engines can start")
                break

            except Exception as e:
                attempt += 1
                backoff = min(2 ** attempt, 30)  # Exponential backoff, max 30s
                logger.error(f"[SafeBroadcaster] Connection failed (attempt {attempt}), retry in {backoff}s: {e}")
                await self._self_report("broadcaster_connection_failed", success=False, error=str(e))
                await asyncio.sleep(backoff)

    async def safe_emit(self, event: Dict[str, Any]) -> bool:
        """
        Emit event to WebSocket, spill on failure.

        Returns True if emitted successfully, False if spilled.
        """
        try:
            if not self.ws.is_available():
                raise RuntimeError("ws_not_ready")

            await self.ws.send(event)
            self.emit_count += 1
            return True

        except Exception as e:
            # Spill and self-report
            self.spill.append(event)
            self.spill_count += 1

            logger.warning(f"[SafeBroadcaster] Spilled event (topic: {event.get('topic', 'unknown')}): {e}")

            await self._self_report(
                "broadcaster_spill",
                success=False,
                topic=event.get("topic", "unknown"),
                error=str(e),
                spill_depth=len(self.spill)
            )

            return False

    async def flush_spill(self):
        """Flush spilled events after reconnect"""
        if not self.spill:
            return

        logger.info(f"[SafeBroadcaster] Flushing {len(self.spill)} spilled events")

        flushed = 0
        failed = 0

        while self.spill:
            event = self.spill.popleft()
            success = await self.safe_emit(event)

            if success:
                flushed += 1
            else:
                failed += 1
                # Re-spill (already happened in safe_emit)
                break  # Stop flushing if still failing

        self.flush_count += flushed

        await self._self_report(
            "broadcaster_flush_complete",
            success=True,
            flushed=flushed,
            failed=failed,
            remaining=len(self.spill)
        )

    async def _self_report(self, event_type: str, success: bool, **kwargs):
        """Emit health.compliance.snapshot to report broadcaster state"""
        try:
            await self.health_bus.inject({
                "type": "health.compliance.snapshot",
                "content": {
                    "emitter": "broadcaster",
                    "event_type": event_type,
                    "success": success,
                    "accept_rate": 1.0 if success else 0.0,
                    "reject_rate": 0.0 if success else 1.0,
                    "top_rejects": [[event_type, 1]] if not success else [],
                    "metrics": {
                        "total_emits": self.emit_count,
                        "total_spills": self.spill_count,
                        "total_flushes": self.flush_count,
                        "current_spill_depth": len(self.spill),
                        **kwargs
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"[SafeBroadcaster] Self-report failed: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get broadcaster metrics for monitoring"""
        return {
            "emit_count": self.emit_count,
            "spill_count": self.spill_count,
            "flush_count": self.flush_count,
            "current_spill_depth": len(self.spill),
            "ready": self.ready.is_set(),
            "ws_available": self.ws.is_available() if self.ws else False
        }
```

---

## Boot Order (Prevents "None" Condition)

**Critical:** Services must start in dependency order with readiness gates.

```python
# orchestration/boot_sequence.py

async def boot_system():
    """Boot Mind Protocol services in correct dependency order"""

    # 1. Start L4 protocol + governance ingestors
    logger.info("Step 1: Ingesting L4 protocol schemas...")
    await ingest_l4_protocol()

    # 2. Start WebSocket server
    logger.info("Step 2: Starting WebSocket server...")
    ws_server = WebSocketServer(port=8000)
    await ws_server.start()
    await ws_server.publish_ready()  # Emits bus.ready broadcast

    # 3. Start SafeBroadcaster and wait for ready
    logger.info("Step 3: Connecting SafeBroadcaster...")
    broadcaster = SafeBroadcaster(
        ws_client=ws_server.client,
        spill_path=".broadcaster_spill.db",
        health_bus=health_bus
    )
    await broadcaster.start()  # Blocks until ws.ready
    await broadcaster.ready.wait()

    # 4. Start consciousness engines (depends on broadcaster)
    logger.info("Step 4: Starting consciousness engines...")
    engines = [
        ConsciousnessEngine(citizen_id="ada-architect", broadcaster=broadcaster),
        ConsciousnessEngine(citizen_id="atlas-infrastructure", broadcaster=broadcaster),
        # ...
    ]
    for engine in engines:
        await engine.start()

    # 5. Start health tools (monitors the stack)
    logger.info("Step 5: Starting health monitoring...")
    await start_health_tools(broadcaster=broadcaster)

    logger.info("✅ Boot complete - system operational")
```

**Key invariant:** Consciousness engines **cannot start** until `broadcaster.ready.is_set() == True`

---

## Heartbeat Deltas (Dashboard Never Looks Dead)

**Problem:** Dashboard shows "0 nodes" between activations even when graph is healthy

**Solution:** Emit heartbeat deltas every N seconds so Wall always shows liveness

```python
# In ConsciousnessEngine

async def _heartbeat_loop(self):
    """Emit minimal graph.delta.heartbeat every 30s"""
    while True:
        await asyncio.sleep(30)

        # Emit heartbeat with current WM state
        await self.broadcaster.safe_emit({
            "type": "graph.delta.heartbeat",
            "topic": f"graph/{self.citizen_id}/delta/heartbeat",
            "content": {
                "citizen_id": self.citizen_id,
                "wm_size": len(self.working_memory),
                "active_nodes": self.get_active_node_count(),
                "energy_total": self.get_total_energy(),
                "last_tick": self.last_tick_time.isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        })
```

**Result:** Wall shows "Last heartbeat: 15s ago" even when no new nodes created

---

## SLOs (Service-Level Objectives)

**Broadcaster Health:**
- ✅ `emit_success_rate >= 0.99` (1-min window)
- ✅ `spill_depth <= 100` (steady state)
- ✅ `flush_latency <= 5s` (after reconnect)
- ❌ Alert if `spill_depth > 1000` (backpressure)

**Dashboard Freshness:**
- ✅ Heartbeat received within 45s (30s + 15s tolerance)
- ✅ UI latency < 250ms from event → card update
- ❌ Alert if no heartbeat for 60s (dead engine)

---

## Acceptance Criteria

1. **Cold start works:**
   - Boot sequence completes in <10s
   - No events dropped during start
   - Dashboard shows presence within 2s of first beacon

2. **WS disconnect recovery:**
   - Kill WS server → events spill
   - Restart WS → spill flushes automatically
   - Dashboard shows gap (offline indicator) then recovers

3. **Self-reporting visible:**
   - `health.compliance.snapshot` shows spill events
   - Dashboard displays spill depth gauge
   - Top rejects show "ws_not_ready" when applicable

4. **Heartbeat prevents "dead" dashboard:**
   - No node creation for 5 minutes
   - Dashboard still shows "Last heartbeat: Xs ago"
   - Citizens show as "active" based on presence.beacon

---

## Handoff to Atlas

**Files to create:**
- `orchestration/adapters/ws/safe_broadcaster.py` (implementation above)
- `orchestration/boot_sequence.py` (dependency-ordered boot)
- `orchestration/adapters/ws/spill_storage.py` (optional: durable spill to SQLite)

**Integration points:**
- Modify `ConsciousnessEngine.__init__` to accept `broadcaster: SafeBroadcaster`
- Add `_heartbeat_loop()` to each engine
- Wire `self.broadcaster.safe_emit()` everywhere `graph.delta.*` is emitted

**Testing:**
1. Boot system → verify `broadcaster.ready` before engines start
2. Kill WS during operation → verify spill
3. Restart WS → verify flush
4. Check `health.compliance.snapshot` shows spill metrics

**Success metric:** Dashboard NEVER shows "0 nodes" when engines are running
