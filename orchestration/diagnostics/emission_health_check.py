#!/usr/bin/env python3
"""
Emission Link Health Check Script

Verifies the entire event emission pipeline:
1. Consciousness engines emitting events
2. Membrane bus receiving events
3. WebSocket manager broadcasting events
4. Clients receiving events

Usage:
    python3 orchestration/diagnostics/emission_health_check.py
"""

import asyncio
import json
import logging
import sys
from typing import Dict, List, Any
from datetime import datetime, timezone
import websockets
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EmissionHealthCheck:
    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.ws_url = "ws://localhost:8000/api/ws"
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {},
            "overall_health": "unknown"
        }

    def check_api_reachable(self) -> bool:
        """Check if API server is responding"""
        try:
            response = requests.get(f"{self.api_base}/api/consciousness/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.results["checks"]["api_reachable"] = {
                    "status": "✅ PASS",
                    "details": {
                        "total_engines": data.get("total_engines", 0),
                        "running": data.get("running", 0)
                    }
                }
                return True
            else:
                self.results["checks"]["api_reachable"] = {
                    "status": "❌ FAIL",
                    "error": f"HTTP {response.status_code}"
                }
                return False
        except Exception as e:
            self.results["checks"]["api_reachable"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
            return False

    def check_consciousness_engines(self) -> bool:
        """Check if consciousness engines have graph data"""
        try:
            response = requests.get(f"{self.api_base}/api/consciousness/status", timeout=5)
            data = response.json()

            engines_with_data = []
            engines_without_data = []

            for citizen_id, engine in data.get("engines", {}).items():
                nodes = engine.get("nodes", 0)
                links = engine.get("links", 0)
                if nodes > 0:
                    engines_with_data.append({
                        "citizen": citizen_id,
                        "nodes": nodes,
                        "links": links,
                        "ticks": engine.get("tick_count", 0)
                    })
                else:
                    engines_without_data.append(citizen_id)

            if engines_with_data:
                self.results["checks"]["consciousness_engines"] = {
                    "status": "✅ PASS",
                    "engines_with_data": len(engines_with_data),
                    "details": engines_with_data[:3]  # Sample first 3
                }
                return True
            else:
                self.results["checks"]["consciousness_engines"] = {
                    "status": "❌ FAIL",
                    "error": "No engines have graph data",
                    "engines_without_data": engines_without_data
                }
                return False
        except Exception as e:
            self.results["checks"]["consciousness_engines"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
            return False

    async def check_websocket_connection(self) -> bool:
        """Check if WebSocket connections can be established"""
        try:
            async with websockets.connect(self.ws_url, timeout=5) as websocket:
                # Wait for subscribe ACK
                message = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(message)

                if data.get("type") == "subscribe.ack@1.0":
                    self.results["checks"]["websocket_connection"] = {
                        "status": "✅ PASS",
                        "connection_id": data.get("payload", {}).get("connection_id"),
                        "topics": data.get("payload", {}).get("topics", [])
                    }
                    return True
                else:
                    self.results["checks"]["websocket_connection"] = {
                        "status": "⚠️ WARN",
                        "message": "Connected but unexpected first message",
                        "received_type": data.get("type")
                    }
                    return False
        except Exception as e:
            self.results["checks"]["websocket_connection"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
            return False

    async def check_event_emission(self, duration_seconds: int = 5) -> bool:
        """Check if events are being emitted over WebSocket"""
        try:
            events_received = []
            graph_delta_events = []
            subentity_events = []

            async with websockets.connect(self.ws_url, timeout=5) as websocket:
                # Skip subscribe ACK
                await websocket.recv()

                # Listen for events for specified duration
                start_time = asyncio.get_event_loop().time()
                while (asyncio.get_event_loop().time() - start_time) < duration_seconds:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1)
                        data = json.loads(message)
                        event_type = data.get("type", "unknown")

                        events_received.append(event_type)

                        if event_type.startswith("graph.delta"):
                            graph_delta_events.append(event_type)
                        elif "subentity" in event_type.lower() or "entity" in event_type.lower():
                            subentity_events.append(event_type)

                    except asyncio.TimeoutError:
                        continue

            # Analyze results
            unique_event_types = set(events_received)
            has_graph_deltas = len(graph_delta_events) > 0
            has_subentity_events = len(subentity_events) > 0

            if has_graph_deltas:
                self.results["checks"]["event_emission"] = {
                    "status": "✅ PASS",
                    "total_events": len(events_received),
                    "unique_types": len(unique_event_types),
                    "graph_delta_count": len(graph_delta_events),
                    "subentity_event_count": len(subentity_events),
                    "sample_types": list(unique_event_types)[:10]
                }
                return True
            elif len(events_received) > 0:
                self.results["checks"]["event_emission"] = {
                    "status": "⚠️ WARN",
                    "message": "Events received but no graph.delta events",
                    "total_events": len(events_received),
                    "event_types": list(unique_event_types)[:10]
                }
                return False
            else:
                self.results["checks"]["event_emission"] = {
                    "status": "❌ FAIL",
                    "error": "No events received during listening period",
                    "duration_seconds": duration_seconds
                }
                return False

        except Exception as e:
            self.results["checks"]["event_emission"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
            return False

    async def run_all_checks(self):
        """Run all health checks"""
        logger.info("🏥 Starting Emission Health Check...")
        logger.info("=" * 60)

        # Check 1: API Reachable
        logger.info("\n[1/4] Checking API reachability...")
        api_ok = self.check_api_reachable()
        logger.info(f"      {self.results['checks']['api_reachable']['status']}")

        if not api_ok:
            logger.error("❌ API not reachable - cannot continue checks")
            self.results["overall_health"] = "CRITICAL"
            return

        # Check 2: Consciousness Engines
        logger.info("\n[2/4] Checking consciousness engines...")
        engines_ok = self.check_consciousness_engines()
        logger.info(f"      {self.results['checks']['consciousness_engines']['status']}")

        # Check 3: WebSocket Connection
        logger.info("\n[3/4] Checking WebSocket connection...")
        ws_ok = await self.check_websocket_connection()
        logger.info(f"      {self.results['checks']['websocket_connection']['status']}")

        # Check 4: Event Emission
        logger.info("\n[4/4] Checking event emission (listening for 5 seconds)...")
        events_ok = await self.check_event_emission(duration_seconds=5)
        logger.info(f"      {self.results['checks']['event_emission']['status']}")

        # Determine overall health
        if api_ok and engines_ok and ws_ok and events_ok:
            self.results["overall_health"] = "HEALTHY ✅"
        elif api_ok and engines_ok and ws_ok:
            self.results["overall_health"] = "DEGRADED ⚠️ (Events not flowing)"
        elif api_ok and engines_ok:
            self.results["overall_health"] = "DEGRADED ⚠️ (WebSocket issues)"
        else:
            self.results["overall_health"] = "UNHEALTHY ❌"

    def print_report(self):
        """Print detailed health report"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 EMISSION HEALTH REPORT")
        logger.info("=" * 60)
        logger.info(f"\n⏰ Timestamp: {self.results['timestamp']}")
        logger.info(f"🏥 Overall Health: {self.results['overall_health']}\n")

        for check_name, check_result in self.results["checks"].items():
            logger.info(f"  {check_name.replace('_', ' ').title()}:")
            logger.info(f"    Status: {check_result['status']}")

            if "details" in check_result:
                logger.info(f"    Details: {json.dumps(check_result['details'], indent=6)}")
            if "error" in check_result:
                logger.info(f"    Error: {check_result['error']}")
            if "message" in check_result:
                logger.info(f"    Message: {check_result['message']}")
            logger.info("")

        logger.info("=" * 60)

        # Diagnostic recommendations
        if self.results["overall_health"] != "HEALTHY ✅":
            logger.info("\n🔧 DIAGNOSTIC RECOMMENDATIONS:\n")

            if self.results["checks"].get("event_emission", {}).get("status") == "❌ FAIL":
                logger.info("  ❌ No events being emitted:")
                logger.info("     - Check if consciousness engines are broadcasting events")
                logger.info("     - Look for 'graph.delta' emissions in consciousness_engine_v2.py")
                logger.info("     - Verify membrane bus is wired to WebSocket manager")
                logger.info("")

            if self.results["checks"].get("websocket_connection", {}).get("status") == "❌ FAIL":
                logger.info("  ❌ WebSocket connection failed:")
                logger.info("     - Check if WebSocket server is running (port 8000)")
                logger.info("     - Verify no firewall blocking port 8000")
                logger.info("")

            if self.results["checks"].get("consciousness_engines", {}).get("status") == "❌ FAIL":
                logger.info("  ❌ Consciousness engines have no data:")
                logger.info("     - Check if entities were bootstrapped")
                logger.info("     - Verify graph persistence is working")
                logger.info("")


async def main():
    checker = EmissionHealthCheck()
    await checker.run_all_checks()
    checker.print_report()

    # Exit with appropriate code
    if checker.results["overall_health"] == "HEALTHY ✅":
        sys.exit(0)
    elif "DEGRADED" in checker.results["overall_health"]:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n\n❌ Health check interrupted by user")
        sys.exit(130)
