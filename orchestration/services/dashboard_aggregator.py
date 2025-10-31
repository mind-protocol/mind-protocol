"""
Dashboard State Aggregator - 1Hz Complete State Emission

Subscribes to: presence.*, status.*, message.*, health.*
Emits: dashboard.state.emit at 1Hz

Architecture:
- Membrane-pure (no REST, no polling)
- Single subscription for UI (no race conditions)
- Self-diagnosing (health metrics included)

Author: Felix (Core Consciousness Engineer) + Ada (Architecture)
Date: 2025-10-30
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List

from orchestration.schemas.dashboard_state_schema import (
    DashboardState, CitizenState, CitizenStatus,
    LinkHealth, ComplianceHealth, BroadcasterHealth, L4State,
    build_dashboard_state
)

logger = logging.getLogger(__name__)


class DashboardAggregator:
    """
    Aggregates membrane events into 1Hz dashboard state.

    SLOs:
    - Emission frequency: 1Hz ± 50ms
    - State completeness: all citizens present
    - Alert if emission stops for >5s
    """

    def __init__(self, broadcaster, ecosystem_id: str = "mindnet", org_id: str = "mind-protocol"):
        self.broadcaster = broadcaster
        self.ecosystem_id = ecosystem_id
        self.org_id = org_id

        # State accumulation (updated from events)
        self.citizens: Dict[str, CitizenState] = {}  # citizen_id -> state
        self.link_health = LinkHealth(ack_rate=1.0, p50_rtt_ms=0, p95_rtt_ms=0, p99_rtt_ms=0, loss=0.0, jitter_ms=0)
        self.compliance_health = ComplianceHealth(reject_rate=0.0, accept_count=0, reject_count=0)
        self.broadcaster_health = BroadcasterHealth(emit_success_rate=1.0, spill_depth=0, last_heartbeat=datetime.now(timezone.utc).isoformat())
        self.l4_stats = L4State(schemas_count=16, namespaces_count=3, governance_policies=5, governed=True)

        self.running = False

    async def handle_presence_beacon(self, event: dict):
        """Update citizen last_seen from presence.beacon."""
        citizen_id = event.get("provenance", {}).get("citizen_id")
        if not citizen_id:
            return

        if citizen_id not in self.citizens:
            self.citizens[citizen_id] = CitizenState(
                id=citizen_id,
                name=citizen_id.split("_")[-1].title(),
                awake="awake",
                last_seen=event.get("ts", datetime.now(timezone.utc).isoformat())
            )
        else:
            self.citizens[citizen_id].last_seen = event.get("ts")
            self.citizens[citizen_id].awake = "awake"

    async def handle_status_activity(self, event: dict):
        """Update citizen status from status.activity.emit."""
        citizen_id = event.get("provenance", {}).get("citizen_id")
        payload = event.get("payload", {})

        if citizen_id in self.citizens:
            self.citizens[citizen_id].status = CitizenStatus(
                mission_id=payload.get("mission_id"),
                incident_id=payload.get("incident_id"),
                files=payload.get("files", []),
                note=payload.get("note"),
                workspace=payload.get("workspace"),
                content_hash=payload.get("content_hash", "")
            )

    async def handle_health_link_snapshot(self, event: dict):
        """Update link health from health.link.snapshot."""
        payload = event.get("payload", {})
        self.link_health = LinkHealth(
            ack_rate=payload.get("ack_rate", 1.0),
            p50_rtt_ms=payload.get("p50_rtt_ms", 0),
            p95_rtt_ms=payload.get("p95_rtt_ms", 0),
            p99_rtt_ms=payload.get("p99_rtt_ms", 0),
            loss=payload.get("loss", 0.0),
            jitter_ms=payload.get("jitter_ms", 0),
            route_mismatches=payload.get("route_mismatches", 0)
        )

    async def handle_health_compliance_snapshot(self, event: dict):
        """Update compliance health from health.compliance.snapshot."""
        payload = event.get("payload", {})
        self.compliance_health = ComplianceHealth(
            reject_rate=payload.get("reject_rate", 0.0),
            top_rejects=payload.get("top_rejects", []),
            accept_count=payload.get("accept_count", 0),
            reject_count=payload.get("reject_count", 0)
        )

    async def emit_dashboard_state(self):
        """Emit aggregated state at 1Hz."""
        # Update staleness
        now = datetime.now(timezone.utc)
        for citizen in self.citizens.values():
            last_seen = datetime.fromisoformat(citizen.last_seen.replace("Z", "+00:00"))
            if (now - last_seen).total_seconds() > citizen.ttl_s:
                citizen.awake = "stale"

        # Build complete state
        state = build_dashboard_state(
            citizens=list(self.citizens.values()),
            link_health=self.link_health,
            compliance_health=self.compliance_health,
            broadcaster_health=self.broadcaster_health,
            l4_stats=self.l4_stats
        )

        # Emit via broadcaster
        topic = f"ecosystem/{self.ecosystem_id}/org/{self.org_id}/dashboard/state"
        await self.broadcaster.broadcast({
            "type": "dashboard.state.emit",
            "topic": topic,
            "content": state.model_dump(),
            "ts": state.ts
        })

        logger.debug(f"[DashboardAggregator] Emitted state: {len(state.citizens)} citizens, ack={state.health.link.ack_rate:.3f}")

    async def run(self):
        """Main aggregator loop - emit at 1Hz."""
        self.running = True
        logger.info("[DashboardAggregator] Starting 1Hz emission loop")

        while self.running:
            try:
                await self.emit_dashboard_state()
                await asyncio.sleep(1.0)  # 1Hz
            except Exception as e:
                logger.error(f"[DashboardAggregator] Emission error: {e}", exc_info=True)
                await asyncio.sleep(1.0)  # Continue despite errors

    def stop(self):
        """Stop aggregator loop."""
        self.running = False
        logger.info("[DashboardAggregator] Stopped")


# === Integration Example ===

async def main():
    """Example: Wire aggregator to membrane bus."""
    from orchestration.adapters.ws.websocket_server import get_broadcaster  # Your actual broadcaster

    broadcaster = get_broadcaster()
    aggregator = DashboardAggregator(broadcaster)

    # Subscribe to input events
    # (In production, wire these via your event bus subscription mechanism)
    # Example:
    # bus.subscribe("presence.*", aggregator.handle_presence_beacon)
    # bus.subscribe("status.activity.*", aggregator.handle_status_activity)
    # bus.subscribe("health.link.*", aggregator.handle_health_link_snapshot)
    # bus.subscribe("health.compliance.*", aggregator.handle_health_compliance_snapshot)

    # Start 1Hz emission loop
    await aggregator.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
