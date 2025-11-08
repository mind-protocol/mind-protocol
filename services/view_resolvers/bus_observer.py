"""
L2 Bus Observer - Subscribe to docs.view.request Events

Connects to membrane bus and routes requests to ViewResolver.
This runs as a separate process (org-internal L2 compute boundary).

Usage:
    python -m services.view_resolvers.bus_observer

Author: Mel "Bridgekeeper"
Date: 2025-11-04
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import websockets

from services.view_resolvers.runner import ViewResolver, ViewCache, EconomyStub
from orchestration.libs.utils.falkordb_adapter import FalkorDBAdapter
from llama_index.graph_stores.falkordb import FalkorDBGraphStore

logger = logging.getLogger(__name__)


class SimpleBus:
    """Minimal bus adapter for L2 resolver to broadcast results."""

    def __init__(self, inject_uri="ws://localhost:8765/inject"):
        self.inject_uri = inject_uri
        self._ws = None

    async def connect(self):
        """Connect to membrane bus /inject endpoint."""
        self._ws = await websockets.connect(self.inject_uri)
        logger.info(f"[L2 Bus] Connected to {self.inject_uri}")

    async def broadcast(self, channel: str, content: dict):
        """Broadcast event to membrane bus."""
        from datetime import datetime, timezone

        envelope = {
            "type": "membrane.inject",
            "channel": channel,
            "payload": content,
            "origin": "l2.resolver",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if self._ws and not self._ws.closed:
            await self._ws.send(json.dumps(envelope))
            logger.debug(f"[L2 Bus] Broadcasted to '{channel}'")
        else:
            logger.error(f"[L2 Bus] Cannot broadcast - connection closed")


class SimpleGraph:
    """Minimal graph adapter for L2 resolver."""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    def query(self, cypher: str, params: dict = None, graph_name: str = None) -> list:
        """Execute Cypher query against FalkorDB.

        Args:
            cypher: Cypher query string
            params: Query parameters
            graph_name: Target graph (extracted from request scope/URL slug)
        """
        import requests

        if not graph_name:
            raise ValueError("graph_name required (should be extracted from request scope)")

        payload = {
            "graph_name": graph_name,
            "query": cypher,
            "params": params or {}
        }

        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            result = response.json()

            # FalkorDB returns {"data": {"result": [...]}}
            if "data" in result and "result" in result["data"]:
                return result["data"]["result"]

            return []

        except Exception as e:
            logger.error(f"[L2 Graph] Query failed for graph '{graph_name}': {e}")
            raise


async def observe_and_resolve(
    resolver: ViewResolver,
    observe_uri="ws://localhost:8765/observe"
):
    """
    Subscribe to docs.view.request and route to resolver.

    This is the main loop for L2 compute.
    """
    async with websockets.connect(observe_uri) as ws:
        # Subscribe to docs.view.request channel
        await ws.send(json.dumps({
            "type": "subscribe",
            "channels": ["docs.view.request"]
        }))

        # Wait for ack
        ack = json.loads(await ws.recv())
        logger.info(f"[L2 Observer] Subscribed to: {ack.get('channels')}")

        # Process events forever
        while True:
            raw = await ws.recv()
            env = json.loads(raw)

            channel = env.get("channel")
            payload = env.get("payload", {})

            if channel == "docs.view.request":
                logger.info(f"[L2 Observer] Received docs.view.request: {payload.get('request_id')}")

                # Route to resolver (synchronous call wrapped in async)
                try:
                    resolver.on_docs_view_request({"content": payload})
                except Exception as e:
                    logger.error(f"[L2 Observer] Resolver error: {e}", exc_info=True)


async def main():
    """Start L2 bus observer."""

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

    # Configuration from environment
    import os

    api_url = os.getenv("FALKORDB_API_URL")
    if not api_url:
        raise ValueError("FALKORDB_API_URL environment variable required")

    api_key = os.getenv("FALKORDB_API_KEY")
    if not api_key:
        raise ValueError("FALKORDB_API_KEY environment variable required")

    observe_uri = os.getenv("MEMBRANE_OBSERVE_URI", "ws://localhost:8765/observe")

    logger.info(f"[L2 Observer] Starting L2 resolver")
    logger.info(f"[L2 Observer] FalkorDB: {api_url}")
    logger.info(f"[L2 Observer] Bus: {observe_uri}")

    # Create bus adapter
    bus = SimpleBus()
    await bus.connect()

    # Create graph adapter (no graph_name - extracted per-request)
    graph = SimpleGraph(api_url, api_key)

    # Create resolver (graph_name extracted from request scope)
    economy = EconomyStub()
    cache = ViewCache(ttl_seconds=300)
    resolver = ViewResolver(bus=bus, graph=graph, economy=economy, cache=cache)

    # Start observing
    logger.info("[L2 Observer] Ready - waiting for docs.view.request events")

    try:
        await observe_and_resolve(resolver, observe_uri)
    except Exception as e:
        logger.error(f"[L2 Observer] Crashed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
