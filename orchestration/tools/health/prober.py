#!/usr/bin/env python3
"""
Membrane-Native Health Link Prober

Active synthetic monitoring via health.link.ping/pong.
Emits probes, tracks responses, detects change-points, reports health.link.snapshot.

Usage:
    python3 orchestration/tools/health/prober.py --targets graph.delta.* emergence.* --window 60
"""

import asyncio
import argparse
import logging
from datetime import datetime, timezone
from uuid import uuid4
from collections import defaultdict
import statistics

from orchestration.libs.websocket_broadcast import get_broadcaster

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LinkProber:
    """
    Active link health prober using health.link.ping/pong.

    Emits synthetic probes, tracks responses, computes metrics,
    detects change-points, and reports health.link.snapshot + alerts.
    """

    def __init__(
        self,
        component_id: str = "tool.health.prober",
        targets: list[str] = None,
        probe_interval_s: int = 10,
        window_s: int = 60
    ):
        self.component_id = component_id
        self.targets = targets or ["graph.delta.*", "emergence.*"]
        self.probe_interval_s = probe_interval_s
        self.window_s = window_s

        self.broadcaster = None
        self.outstanding = {}  # probe_id -> (sent_ts, target_topic)
        self.window = []  # Recent probe outcomes
        self.history = defaultdict(list)  # Per-topic history for change detection

        self.probes_sent = 0
        self.pongs_received = 0

        logger.info(
            f"[{self.component_id}] Initialized - "
            f"targets={targets}, interval={probe_interval_s}s, window={window_s}s"
        )

    async def start(self):
        """Start prober service"""
        self.broadcaster = get_broadcaster()
        if not self.broadcaster or not self.broadcaster.is_available():
            raise RuntimeError("Broadcaster not available - cannot start prober")

        logger.info(f"[{self.component_id}] Started")

        # Start probe emission loop
        probe_task = asyncio.create_task(self._probe_loop())

        # Start snapshot flush loop
        flush_task = asyncio.create_task(self._flush_loop())

        # Wait for both
        await asyncio.gather(probe_task, flush_task)

    async def _probe_loop(self):
        """Emit health.link.ping probes periodically"""
        while True:
            try:
                for target_topic in self.targets:
                    await self._send_probe(target_topic)
                    await asyncio.sleep(0.1)  # Small gap between probes

                await asyncio.sleep(self.probe_interval_s)

            except Exception as e:
                logger.error(f"[{self.component_id}] Error in probe loop: {e}", exc_info=True)
                await asyncio.sleep(5)

    async def _send_probe(self, target_topic: str):
        """Send single health.link.ping probe"""
        probe_id = str(uuid4())
        sent_ts = datetime.now(timezone.utc)

        self.outstanding[probe_id] = (sent_ts, target_topic)

        await self.broadcaster.broadcast_event("health.link.ping", {
            "probe_id": probe_id,
            "target_topic": target_topic,
            "ttl_ms": 30000
        })

        self.probes_sent += 1
        logger.debug(f"[{self.component_id}] Probe sent: {probe_id} -> {target_topic}")

        # Schedule timeout check
        asyncio.create_task(self._check_timeout(probe_id, sent_ts))

    async def _check_timeout(self, probe_id: str, sent_ts: datetime):
        """Mark probe as timed out if no pong received"""
        await asyncio.sleep(30)  # TTL

        if probe_id in self.outstanding:
            sent_ts, target_topic = self.outstanding.pop(probe_id)
            self.window.append({
                "topic": target_topic,
                "ok": False,
                "rtt": None,
                "ts": datetime.now(timezone.utc),
                "reason": "timeout"
            })
            logger.warning(
                f"[{self.component_id}] Probe timeout: {probe_id} -> {target_topic}"
            )

    async def on_pong(self, event: dict):
        """
        Handle health.link.pong response

        Args:
            event: Normative membrane envelope with type=health.link.pong
        """
        try:
            probe_id = event["content"]["probe_id"]
            if probe_id not in self.outstanding:
                logger.debug(f"[{self.component_id}] Pong for unknown probe: {probe_id}")
                return

            sent_ts, target_topic = self.outstanding.pop(probe_id)
            rtt = event["content"]["rtt_ms"]
            received_topic = event["content"]["received_topic"]

            self.window.append({
                "topic": target_topic,
                "ok": True,
                "rtt": rtt,
                "ts": datetime.now(timezone.utc),
                "route_mismatch": target_topic != received_topic
            })

            self.pongs_received += 1

            if target_topic != received_topic:
                logger.warning(
                    f"[{self.component_id}] Route mismatch: "
                    f"probe={probe_id}, target={target_topic}, received={received_topic}"
                )
            else:
                logger.debug(
                    f"[{self.component_id}] Pong received: "
                    f"probe={probe_id}, rtt={rtt}ms, topic={target_topic}"
                )

        except Exception as e:
            logger.error(f"[{self.component_id}] Error handling pong: {e}", exc_info=True)

    async def _flush_loop(self):
        """Emit health.link.snapshot periodically"""
        while True:
            await asyncio.sleep(self.window_s)

            try:
                await self._flush_snapshot()
            except Exception as e:
                logger.error(f"[{self.component_id}] Error flushing snapshot: {e}", exc_info=True)

    async def _flush_snapshot(self):
        """Compute metrics and emit health.link.snapshot"""
        if not self.window:
            logger.debug(f"[{self.component_id}] No data in window, skipping snapshot")
            return

        # Group by topic
        by_topic = defaultdict(list)
        for outcome in self.window:
            by_topic[outcome["topic"]].append(outcome)

        # Emit snapshot per topic
        for topic, outcomes in by_topic.items():
            metrics = self._compute_metrics(outcomes)

            await self.broadcaster.broadcast_event("health.link.snapshot", {
                "window_s": self.window_s,
                "emitter": self.component_id,
                "topic": topic,
                **metrics
            })

            logger.info(
                f"[{self.component_id}] Snapshot: topic={topic}, "
                f"ack_rate={metrics['ack_rate']:.2f}, "
                f"rtt_p50={metrics['rtt_p50']:.1f}ms, "
                f"loss_rate={metrics['loss_rate']:.2f}"
            )

            # Check for change-points (simple version)
            await self._check_alerts(topic, metrics)

        # Clear window
        self.window.clear()

    def _compute_metrics(self, outcomes: list) -> dict:
        """Compute health metrics from probe outcomes"""
        total = len(outcomes)
        successes = [o for o in outcomes if o["ok"]]
        rtts = [o["rtt"] for o in successes if o["rtt"] is not None]
        route_mismatches = sum(1 for o in successes if o.get("route_mismatch", False))

        ack_rate = len(successes) / total if total > 0 else 0.0
        loss_rate = 1.0 - ack_rate

        rtt_p50 = statistics.median(rtts) if rtts else 0.0
        rtt_p95 = statistics.quantiles(rtts, n=20)[18] if len(rtts) > 2 else rtt_p50
        jitter = statistics.stdev(rtts) if len(rtts) > 1 else 0.0

        last_ok = max((o["ts"] for o in successes), default=None)

        return {
            "ack_rate": round(ack_rate, 3),
            "rtt_p50": round(rtt_p50, 1),
            "rtt_p95": round(rtt_p95, 1),
            "jitter_ms": round(jitter, 1),
            "loss_rate": round(loss_rate, 3),
            "ordering_errors": 0,  # Would need sequence tracking
            "route_mismatch": route_mismatches,
            "last_ok_ts": last_ok.isoformat() if last_ok else None
        }

    async def _check_alerts(self, topic: str, metrics: dict):
        """
        Detect change-points using simple record/MAD method.

        In production, use proper change-point detection (Page-Hinkley, CUSUM, etc.)
        """
        history = self.history[topic]
        history.append(metrics)

        # Keep last N windows
        if len(history) > 20:
            history.pop(0)

        # Need at least 5 data points
        if len(history) < 5:
            return

        # Simple threshold-based alerting (replace with learned change-points)
        if metrics["ack_rate"] < 0.8 and len(history) > 1:
            prev_ack_rate = history[-2]["ack_rate"]
            if prev_ack_rate >= 0.8:  # Drop detected
                await self.broadcaster.broadcast_event("health.link.alert", {
                    "emitter": self.component_id,
                    "topic": topic,
                    "signal": "ack_rate_drop",
                    "evidence": {
                        "current_ack_rate": metrics["ack_rate"],
                        "previous_ack_rate": prev_ack_rate,
                        "drop": prev_ack_rate - metrics["ack_rate"]
                    },
                    "severity": "high" if metrics["ack_rate"] < 0.5 else "medium"
                })

                logger.warning(
                    f"[{self.component_id}] ⚠️ Alert: ack_rate_drop on {topic} "
                    f"({prev_ack_rate:.2f} → {metrics['ack_rate']:.2f})"
                )


async def main():
    """Run health link prober"""
    parser = argparse.ArgumentParser(description="Membrane-native health link prober")
    parser.add_argument("--targets", nargs="+", default=["graph.delta.*", "emergence.*"],
                        help="Topic patterns to probe")
    parser.add_argument("--interval", type=int, default=10,
                        help="Probe interval in seconds")
    parser.add_argument("--window", type=int, default=60,
                        help="Snapshot window in seconds")

    args = parser.parse_args()

    prober = LinkProber(
        targets=args.targets,
        probe_interval_s=args.interval,
        window_s=args.window
    )

    try:
        await prober.start()
    except KeyboardInterrupt:
        logger.info(
            f"[{prober.component_id}] Shutting down "
            f"(probes sent: {prober.probes_sent}, pongs received: {prober.pongs_received})"
        )
    except Exception as e:
        logger.error(f"[{prober.component_id}] Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
