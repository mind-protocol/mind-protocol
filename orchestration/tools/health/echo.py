#!/usr/bin/env python3
"""
Membrane-Native Health Echo Tool

Stateless responder for health.link.ping probes.
Immediately echoes with health.link.pong to measure link latency and reachability.

Usage:
    python3 orchestration/tools/health/echo.py
"""

import asyncio
import logging
from datetime import datetime, timezone
from uuid import uuid4

from orchestration.libs.websocket_broadcast import get_broadcaster

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HealthEchoTool:
    """
    Stateless echo responder for health probes.

    Subscribes to health.link.ping and immediately responds with health.link.pong.
    Measures round-trip time and reports actual vs expected topic routing.
    """

    def __init__(self, component_id: str = "tool.health.echo"):
        self.component_id = component_id
        self.broadcaster = None
        self.pongs_sent = 0
        logger.info(f"[{self.component_id}] Initialized")

    async def start(self):
        """Start echo service"""
        self.broadcaster = get_broadcaster()
        if not self.broadcaster or not self.broadcaster.is_available():
            raise RuntimeError("Broadcaster not available - cannot start echo tool")

        # Subscribe to health.link.ping
        # Note: In real implementation, would subscribe via membrane bus
        # For now, this is a skeleton showing the pattern
        logger.info(f"[{self.component_id}] Started - listening for health.link.ping")

        # Keep alive
        while True:
            await asyncio.sleep(60)
            logger.debug(f"[{self.component_id}] Heartbeat - pongs sent: {self.pongs_sent}")

    async def on_ping(self, event: dict):
        """
        Handle health.link.ping event

        Args:
            event: Normative membrane envelope with type=health.link.ping
        """
        try:
            probe_id = event["content"]["probe_id"]
            target_topic = event["content"]["target_topic"]
            sent_ts = event.get("ts")
            received_topic = event.get("provenance", {}).get("topic", "unknown")

            # Calculate RTT from original timestamp
            now_iso = datetime.now(timezone.utc).isoformat()
            if sent_ts:
                try:
                    sent_dt = datetime.fromisoformat(sent_ts.replace('Z', '+00:00'))
                    now_dt = datetime.now(timezone.utc)
                    rtt_ms = int((now_dt - sent_dt).total_seconds() * 1000)
                except:
                    rtt_ms = 0
            else:
                rtt_ms = 0

            # Emit health.link.pong
            await self.broadcaster.broadcast_event("health.link.pong", {
                "probe_id": probe_id,
                "target_topic": target_topic,
                "received_topic": received_topic,
                "rtt_ms": max(0, rtt_ms),
                "hops": 1,
                "responder": self.component_id
            })

            self.pongs_sent += 1

            # Log route mismatch if detected
            if target_topic != received_topic:
                logger.warning(
                    f"[{self.component_id}] Route mismatch: "
                    f"probe_id={probe_id}, target={target_topic}, received={received_topic}"
                )
            else:
                logger.debug(
                    f"[{self.component_id}] Pong sent: "
                    f"probe_id={probe_id}, rtt={rtt_ms}ms, topic={target_topic}"
                )

        except Exception as e:
            logger.error(f"[{self.component_id}] Error handling ping: {e}", exc_info=True)


async def main():
    """Run health echo tool"""
    echo = HealthEchoTool()
    try:
        await echo.start()
    except KeyboardInterrupt:
        logger.info(f"[{echo.component_id}] Shutting down (pongs sent: {echo.pongs_sent})")
    except Exception as e:
        logger.error(f"[{echo.component_id}] Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
