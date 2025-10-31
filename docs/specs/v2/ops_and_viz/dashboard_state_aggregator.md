# Dashboard State Aggregator

**Purpose:** Single UI-friendly state emission (1Hz) combining presence/status/health/L4 → one subscription for Citizen Wall

**Problem:** Dashboard subscribing to dozens of topics (presence.beacon per citizen, status.activity per citizen, health.* etc.) creates:
- Complex subscription management
- Race conditions (partial updates)
- High WebSocket message volume
- Difficult to reason about UI state

**Solution:** Aggregator service subscribes to all events, emits single `dashboard.state.emit` (1Hz) with complete state snapshot

---

## Architecture

```
presence.beacon (per citizen)
status.activity.emit (per citizen)
message.thread (per citizen)
health.link.snapshot
health.compliance.snapshot
        ↓
Dashboard Aggregator ← subscribes to all
        ↓
dashboard.state.emit (1Hz broadcast)
        ↓
UI (single subscription)
```

**Key insight:** Dashboard UI subscribes to **ONE topic**, gets complete state every second

---

## Event Schema

### Input Events (Aggregator Subscribes)

```typescript
// Per-citizen events
interface PresenceBeacon {
  citizen_id: string;
  availability: "active" | "idle" | "do_not_disturb" | "offline";
  focus_tag?: string;
  ttl_seconds: number;
  timestamp: string;
}

interface StatusActivityEmit {
  citizen_id: string;
  mission_id?: string;
  files: string[];
  incident_id?: string;
  note?: string;
  tags: string[];
  timestamp: string;
}

interface MessageThread {
  from_citizen: string;
  to_citizens: string[];
  thread_id: string;
  body_md: string;
  source_bridge?: "email" | "telegram";
  timestamp: string;
}

// Health events
interface HealthLinkSnapshot {
  ack_rate: number;       // 0-1
  p50_rtt_ms: number;
  p95_rtt_ms: number;
  p99_rtt_ms: number;
  loss_rate: number;      // 0-1
  route_mismatch_count: number;
  timestamp: string;
}

interface HealthComplianceSnapshot {
  accept_rate: number;    // 0-1
  reject_rate: number;    // 0-1
  top_rejects: [string, number][];  // [reason, count]
  timestamp: string;
}
```

### Output Event (UI Subscribes)

```typescript
// Emitted at 1Hz to ecosystem/{eco}/org/{org}/dashboard/state
interface DashboardStateEmit {
  // Citizen states
  citizens: CitizenState[];

  // Health metrics
  health: {
    link: {
      ack_rate: number;
      p95_rtt_ms: number;
      loss_rate: number;
      route_mismatches: number;
    };
    compliance: {
      reject_rate: number;
      top_rejects: [string, number][];
    };
  };

  // L4 Protocol stats
  l4: {
    schemas_count: number;
    namespaces_count: number;
    governed: boolean;
  };

  // Timestamp
  timestamp: string;
}

interface CitizenState {
  id: string;
  display_name: string;
  role: string;

  // Presence (from presence.beacon)
  availability: "active" | "idle" | "do_not_disturb" | "offline" | "stale";
  last_seen: string;
  focus_tag?: string;
  ttl_seconds: number;

  // Status (from status.activity.emit)
  current_activity?: {
    mission_id?: string;
    mission_title?: string;  // Resolved from L2 if mission_id present
    files: string[];
    incident_id?: string;
    note?: string;
    tags: string[];
  };

  // Messages (from message.thread)
  unread_count: number;
  recent_threads: {
    thread_id: string;
    participants: string[];
    last_message_from: string;
    last_message_preview: string;  // First 100 chars
    source_bridge?: "email" | "telegram";
    timestamp: string;
  }[];

  // Credits (optional, from budget.balance.updated)
  credits?: {
    balance: number;
    recent_activity: {
      type: "debit" | "credit" | "rebate";
      amount: number;
      reason: string;
      timestamp: string;
    }[];
  };
}
```

---

## Implementation

```python
# orchestration/services/dashboard_aggregator.py

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class DashboardAggregator:
    """
    Subscribes to all relevant events, emits dashboard.state.emit at 1Hz.

    Provides single UI-friendly state snapshot combining:
    - presence.beacon (per citizen)
    - status.activity.emit (per citizen)
    - message.thread (per citizen)
    - health.link.snapshot
    - health.compliance.snapshot
    """

    def __init__(self, event_bus, graph_client, org_id: str = "core"):
        self.bus = event_bus
        self.graph = graph_client
        self.org_id = org_id

        # State caches (updated from events)
        self.presence_state: Dict[str, Dict] = {}  # citizen_id → last presence
        self.status_state: Dict[str, Dict] = {}    # citizen_id → last status
        self.threads_state: Dict[str, List] = defaultdict(list)  # citizen_id → threads
        self.health_link: Optional[Dict] = None
        self.health_compliance: Optional[Dict] = None

        # Citizen registry (from L2 graph)
        self.citizens: List[Dict] = []

    async def start(self):
        """Start aggregator: load citizens, subscribe to events, emit at 1Hz"""

        # Load citizen registry from L2 graph
        await self._load_citizens()

        # Subscribe to all input events
        await self._subscribe_all()

        # Start 1Hz emission loop
        asyncio.create_task(self._emit_loop())

        logger.info("[DashboardAggregator] Started - emitting at 1Hz")

    async def _load_citizens(self):
        """Load citizen registry from L2 graph"""
        query = """
        MATCH (c:Citizen)
        RETURN c.id, c.display_name, c.role
        """
        result = self.graph.query(query)

        self.citizens = [
            {
                "id": row[0],
                "display_name": row[1],
                "role": row[2]
            }
            for row in result.result_set
        ]

        logger.info(f"[DashboardAggregator] Loaded {len(self.citizens)} citizens")

    async def _subscribe_all(self):
        """Subscribe to all input events"""

        # Presence beacons (per citizen)
        for citizen in self.citizens:
            topic = f"ecosystem/mind-protocol/org/{self.org_id}/citizen/{citizen['id']}/presence/beacon"
            await self.bus.subscribe(topic, self._handle_presence)

        # Status activity (per citizen)
        for citizen in self.citizens:
            topic = f"ecosystem/mind-protocol/org/{self.org_id}/citizen/{citizen['id']}/status/activity"
            await self.bus.subscribe(topic, self._handle_status)

        # Message threads (per citizen)
        for citizen in self.citizens:
            topic = f"ecosystem/mind-protocol/org/{self.org_id}/citizen/{citizen['id']}/message/thread/+"
            await self.bus.subscribe(topic, self._handle_message)

        # Health snapshots
        await self.bus.subscribe(f"ecosystem/mind-protocol/org/{self.org_id}/health/link/snapshot", self._handle_health_link)
        await self.bus.subscribe(f"ecosystem/mind-protocol/org/{self.org_id}/health/compliance/snapshot", self._handle_health_compliance)

    async def _handle_presence(self, event):
        """Update presence state cache"""
        citizen_id = event["content"]["citizen_id"]
        self.presence_state[citizen_id] = event["content"]

    async def _handle_status(self, event):
        """Update status state cache"""
        citizen_id = event["content"]["citizen_id"]
        self.status_state[citizen_id] = event["content"]

    async def _handle_message(self, event):
        """Update threads state cache"""
        content = event["content"]
        for citizen_id in content.get("to_citizens", []):
            # Add to that citizen's thread list
            thread = {
                "thread_id": content["thread_id"],
                "participants": [content["from_citizen"]] + content["to_citizens"],
                "last_message_from": content["from_citizen"],
                "last_message_preview": content["body_md"][:100],
                "source_bridge": content.get("source_bridge"),
                "timestamp": content["timestamp"]
            }

            # Deduplicate by thread_id, keep latest
            threads = self.threads_state[citizen_id]
            threads = [t for t in threads if t["thread_id"] != content["thread_id"]]
            threads.append(thread)
            threads.sort(key=lambda t: t["timestamp"], reverse=True)
            self.threads_state[citizen_id] = threads[:10]  # Keep latest 10

    async def _handle_health_link(self, event):
        """Update health link state"""
        self.health_link = event["content"]

    async def _handle_health_compliance(self, event):
        """Update health compliance state"""
        self.health_compliance = event["content"]

    async def _emit_loop(self):
        """Emit dashboard.state.emit at 1Hz"""
        while True:
            await asyncio.sleep(1.0)  # 1Hz

            # Build complete state snapshot
            state = await self._build_state()

            # Emit to dashboard topic
            await self.bus.broadcast({
                "type": "dashboard.state.emit",
                "topic": f"ecosystem/mind-protocol/org/{self.org_id}/dashboard/state",
                "content": state,
                "timestamp": datetime.utcnow().isoformat()
            })

    async def _build_state(self) -> Dict[str, Any]:
        """Build complete dashboard state from caches"""

        citizen_states = []

        for citizen in self.citizens:
            cit_id = citizen["id"]

            # Get presence state
            presence = self.presence_state.get(cit_id, {})
            last_seen = presence.get("timestamp")
            ttl = presence.get("ttl_seconds", 90)

            # Determine availability (with staleness check)
            availability = presence.get("availability", "offline")
            if last_seen:
                elapsed = (datetime.utcnow() - datetime.fromisoformat(last_seen)).total_seconds()
                if elapsed > ttl:
                    availability = "stale"

            # Get status state
            status = self.status_state.get(cit_id, {})
            current_activity = None
            if status:
                current_activity = {
                    "mission_id": status.get("mission_id"),
                    "mission_title": await self._resolve_mission_title(status.get("mission_id")),
                    "files": status.get("files", []),
                    "incident_id": status.get("incident_id"),
                    "note": status.get("note"),
                    "tags": status.get("tags", [])
                }

            # Get threads state
            threads = self.threads_state.get(cit_id, [])
            unread_count = len([t for t in threads if not t.get("read", False)])  # Simplified

            citizen_states.append({
                "id": cit_id,
                "display_name": citizen["display_name"],
                "role": citizen["role"],
                "availability": availability,
                "last_seen": last_seen or "",
                "focus_tag": presence.get("focus_tag"),
                "ttl_seconds": ttl,
                "current_activity": current_activity,
                "unread_count": unread_count,
                "recent_threads": threads[:3]  # Latest 3
            })

        # Build health state
        health = {
            "link": {
                "ack_rate": self.health_link.get("ack_rate", 0.0) if self.health_link else 0.0,
                "p95_rtt_ms": self.health_link.get("p95_rtt_ms", 0) if self.health_link else 0,
                "loss_rate": self.health_link.get("loss_rate", 0.0) if self.health_link else 0.0,
                "route_mismatches": self.health_link.get("route_mismatch_count", 0) if self.health_link else 0
            },
            "compliance": {
                "reject_rate": self.health_compliance.get("reject_rate", 0.0) if self.health_compliance else 0.0,
                "top_rejects": self.health_compliance.get("top_rejects", []) if self.health_compliance else []
            }
        }

        # L4 protocol stats (cached, not queried every second)
        l4 = {
            "schemas_count": await self._count_l4_schemas(),
            "namespaces_count": await self._count_l4_namespaces(),
            "governed": True  # Simplified
        }

        return {
            "citizens": citizen_states,
            "health": health,
            "l4": l4,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _resolve_mission_title(self, mission_id: Optional[str]) -> Optional[str]:
        """Resolve mission title from L2 graph (cached for 1min)"""
        if not mission_id:
            return None

        # Simplified - implement caching in production
        query = f"""
        MATCH (m:Mission {{id: '{mission_id}'}})
        RETURN m.title
        """
        result = self.graph.query(query)

        if result.result_set:
            return result.result_set[0][0]
        return None

    async def _count_l4_schemas(self) -> int:
        """Count Event_Schema nodes in protocol graph"""
        # Cached for 1 minute
        if not hasattr(self, "_l4_schemas_count_cache"):
            query = "MATCH (es:Event_Schema) RETURN count(es)"
            result = self.graph.query(query, graph_name="protocol")
            self._l4_schemas_count_cache = result.result_set[0][0] if result.result_set else 0

        return self._l4_schemas_count_cache

    async def _count_l4_namespaces(self) -> int:
        """Count Topic_Namespace nodes in protocol graph"""
        # Cached for 1 minute
        if not hasattr(self, "_l4_namespaces_count_cache"):
            query = "MATCH (ns:Topic_Namespace) RETURN count(ns)"
            result = self.graph.query(query, graph_name="protocol")
            self._l4_namespaces_count_cache = result.result_set[0][0] if result.result_set else 0

        return self._l4_namespaces_count_cache
```

---

## UI Integration (for Iris)

```typescript
// app/consciousness/hooks/useDashboardState.ts

import { useEffect, useState } from 'react';
import { useWebSocket } from './useWebSocket';

interface DashboardState {
  citizens: CitizenState[];
  health: HealthState;
  l4: L4State;
  timestamp: string;
}

export function useDashboardState() {
  const [state, setState] = useState<DashboardState | null>(null);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    // Subscribe to SINGLE topic
    const unsubscribe = subscribe(
      'ecosystem/mind-protocol/org/core/dashboard/state',
      (event) => {
        setState(event.content);
      }
    );

    return unsubscribe;
  }, [subscribe]);

  return state;
}
```

```typescript
// app/consciousness/components/CitizenWall.tsx

import { useDashboardState } from '../hooks/useDashboardState';
import { CitizenCard } from './CitizenCard';

export function CitizenWall() {
  const state = useDashboardState();

  if (!state) {
    return <div>Loading...</div>;
  }

  return (
    <div className="citizen-wall">
      <h2>Citizens ({state.citizens.length})</h2>

      <div className="citizen-grid">
        {state.citizens.map(citizen => (
          <CitizenCard key={citizen.id} citizen={citizen} />
        ))}
      </div>

      <HealthPanel health={state.health} />
      <L4StatusPanel l4={state.l4} />
    </div>
  );
}
```

**Key benefit:** UI component is **dead simple** - one subscription, complete state every second

---

## SLOs

**Aggregator Health:**
- ✅ Emission frequency: 1Hz ± 50ms
- ✅ State completeness: all citizens present in every emission
- ✅ Staleness detection: availability="stale" if last_seen > ttl
- ❌ Alert if emission stops for >5s

**UI Latency:**
- ✅ Event → UI update < 250ms (event arrives, aggregator processes, emits within 1s, UI renders)
- ✅ Heartbeat visible within 2s of first presence.beacon
- ❌ Alert if UI shows "Loading..." for >10s

---

## Acceptance Criteria

1. **Single subscription works:**
   - UI subscribes to `dashboard/state` only
   - Receives complete state every second
   - No partial updates, no race conditions

2. **Staleness detection:**
   - Citizen stops emitting presence.beacon
   - After TTL expires, aggregator marks availability="stale"
   - UI shows gray "offline" badge

3. **Health metrics visible:**
   - `health.link.snapshot` shows ack_rate, RTT, route mismatches
   - `health.compliance.snapshot` shows reject_rate, top rejects
   - Dashboard displays gauges/charts from aggregated state

4. **Mission title resolution:**
   - Citizen emits status with mission_id
   - Aggregator resolves mission title from L2 graph
   - UI shows "Working on: SubEntity Persistence" instead of "mission:xyz"

---

## Handoff to Atlas

**Files to create:**
- `orchestration/services/dashboard_aggregator.py` (implementation above)
- `orchestration/services/dashboard_aggregator_test.py` (unit tests)

**Integration:**
- Add to boot sequence (after broadcaster ready, before dashboard starts)
- Wire to WebSocket event bus for subscriptions + broadcasts
- Connect to L2 graph client for mission/citizen lookups

**Testing:**
1. Start aggregator → verify 1Hz emission
2. Emit presence/status/message events → verify aggregated state includes them
3. Stop presence beacon → verify staleness after TTL
4. Check UI renders from single subscription

**Success metric:** Iris can build entire Citizen Wall with **one subscription**
