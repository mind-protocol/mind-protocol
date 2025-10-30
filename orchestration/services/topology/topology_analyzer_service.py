"""
Topology Analyzer Service - Event-Driven Topology Analysis

Listens to graph mutation and activation events from the membrane bus,
performs reactive topology analysis, and emits telemetry events.

Event-driven architecture (NO cron jobs):
- SubEntity spawned → compute integration metrics
- 10 spawns accumulated → recompute betweenness centrality
- SubEntity activation + low energy → check hub risk
- MEMBER_OF edge created → invalidate community cache

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-29
Spec: orchestration/adapters/TOPOLOGY_ANALYZER_EVENT_WIRING.md
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional
from collections import defaultdict

from falkordb import FalkorDB

from orchestration.mechanisms.rich_club_analyzer import RichClubAnalyzer, RichClubConfig
from orchestration.mechanisms.integration_metrics_analyzer import IntegrationMetricsAnalyzer, IntegrationMetricsConfig
from orchestration.libs.websocket_broadcast import ConsciousnessStateBroadcaster

logger = logging.getLogger(__name__)


class TopologyAnalyzerService:
    """
    Event-driven topology analyzer listening on membrane bus.

    Subscribes to 4 event types:
    1. graph.delta.node.upsert (SubEntity spawn) → integration metrics + batched betweenness
    2. subentity.activation → hub risk detection
    3. graph.delta.link.upsert (MEMBER_OF edge) → invalidate cache
    4. topology.analyze.request → on-demand full analysis

    Throttling:
    - Batching: Recompute betweenness every 10 spawns
    - Debouncing: Min 60s between betweenness recomputes
    - Priority: Hub alerts (immediate) > node metrics > full recompute
    """

    def __init__(
        self,
        citizen_id: str = "default_citizen",
        broadcaster: Optional[ConsciousnessStateBroadcaster] = None,
        rich_club_config: Optional[RichClubConfig] = None,
        integration_config: Optional[IntegrationMetricsConfig] = None,
        falkordb_host: str = "localhost",
        falkordb_port: int = 6379
    ):
        """
        Initialize topology analyzer service (synchronous setup only).

        Graph loading happens in async_init() to avoid blocking event loop.

        Args:
            citizen_id: Citizen to analyze topology for
            broadcaster: WebSocket broadcaster (if None, creates new instance)
            rich_club_config: RichClubAnalyzer configuration
            integration_config: IntegrationMetricsAnalyzer configuration
            falkordb_host: FalkorDB host
            falkordb_port: FalkorDB port
        """
        self.citizen_id = citizen_id
        self.broadcaster = broadcaster or ConsciousnessStateBroadcaster()
        self.falkordb_host = falkordb_host
        self.falkordb_port = falkordb_port

        # Store configs for async_init
        self.rich_club_config = rich_club_config or RichClubConfig()
        self.integration_config = integration_config or IntegrationMetricsConfig()

        # Graph and analyzers initialized in async_init()
        self.graph = None
        self.rich_club_analyzer = None
        self.integration_analyzer = None

        # Batching state
        self.spawn_count = 0
        self.betweenness_recompute_threshold = 10  # Every 10 spawns
        self.edge_count = 0
        self.edge_recompute_threshold = 20  # Every 20 edges (optional)

        # Debouncing state
        self.last_betweenness_compute = 0.0
        self.min_recompute_interval = 60.0  # 60 seconds minimum between recomputes

        # Telemetry
        self.events_processed = defaultdict(int)
        self.started_at = time.time()

        # Initialization state
        self._initialized = False

        logger.info(f"[TopologyAnalyzer] Created for citizen {citizen_id} (awaiting async_init)")

    async def async_init(self):
        """
        Async initialization - loads graph without blocking event loop.

        Must be called after __init__() and awaited before using the service.
        """
        if self._initialized:
            logger.warning(f"[TopologyAnalyzer] Already initialized for {self.citizen_id}")
            return

        try:
            # Load graph in executor to avoid blocking event loop
            loop = asyncio.get_event_loop()

            # Create FalkorDB connection in thread pool
            db = await loop.run_in_executor(
                None,
                FalkorDB,
                self.falkordb_host,
                self.falkordb_port
            )

            # Load graph in thread pool
            graph_name = f"citizen_{self.citizen_id}"
            self.graph = await loop.run_in_executor(
                None,
                db.select_graph,
                graph_name
            )

            logger.debug(f"[TopologyAnalyzer] Connected to graph: {graph_name}")

            # Initialize analyzers (quick, no blocking I/O)
            self.rich_club_analyzer = RichClubAnalyzer(
                graph=self.graph,
                config=self.rich_club_config
            )

            self.integration_analyzer = IntegrationMetricsAnalyzer(
                graph=self.graph,
                config=self.integration_config
            )

            self._initialized = True
            logger.info(f"[TopologyAnalyzer] Initialized for citizen {self.citizen_id}")

        except Exception as e:
            logger.error(f"[TopologyAnalyzer] Failed to connect to graph for {self.citizen_id}: {e}")
            raise

    def start(self):
        """
        Start the topology analyzer service.

        Registers event listeners on the membrane bus.
        """
        # Register listeners on ConsciousnessStateBroadcaster
        ConsciousnessStateBroadcaster.register_listener(self._event_router)

        logger.info("[TopologyAnalyzer] Event listeners registered")
        logger.info(f"[TopologyAnalyzer] Batching threshold: {self.betweenness_recompute_threshold} spawns")
        logger.info(f"[TopologyAnalyzer] Debounce interval: {self.min_recompute_interval}s")

    def stop(self):
        """
        Stop the topology analyzer service.

        Unregisters event listeners.
        """
        ConsciousnessStateBroadcaster.unregister_listener(self._event_router)
        logger.info("[TopologyAnalyzer] Event listeners unregistered")

    async def _event_router(self, citizen_id: str, event_type: str, payload: Dict[str, Any]):
        """
        Route events to appropriate handlers.

        This is the main event listener registered on ConsciousnessStateBroadcaster.

        Args:
            citizen_id: Citizen ID from event
            event_type: Event type string
            payload: Event payload
        """
        # Only process events for our citizen
        if citizen_id != self.citizen_id:
            return

        # Skip events if not initialized yet (graph still loading)
        if not self._initialized:
            logger.debug(f"[TopologyAnalyzer] Skipping {event_type} - service not initialized yet")
            return

        try:
            # Route to handler based on event type
            if event_type == "graph.delta.node.upsert":
                await self._on_node_upsert(payload)
            elif event_type == "subentity.activation":
                await self._on_activation(payload)
            elif event_type == "graph.delta.link.upsert":
                await self._on_link_upsert(payload)
            elif event_type == "topology.analyze.request":
                await self._on_analyze_request(payload)

            # Track events processed
            self.events_processed[event_type] += 1

        except Exception as e:
            logger.error(f"[TopologyAnalyzer] Event handler failed for {event_type}: {e}", exc_info=True)

    async def _on_node_upsert(self, payload: Dict[str, Any]):
        """
        Handle graph.delta.node.upsert event.

        Triggers:
        1. Immediate integration metrics computation for new SubEntity
        2. Batched betweenness recomputation (every 10 spawns)

        Event format:
        {
            "node_id": "subentity_citizen_ops_42",
            "node_type": "SubEntity",
            "properties": {...}
        }
        """
        # Only process SubEntity nodes
        if payload.get("node_type") != "SubEntity":
            return

        node_id = payload.get("node_id")
        if not node_id:
            return

        logger.debug(f"[TopologyAnalyzer] SubEntity spawned: {node_id}")

        # 1. Compute integration metrics for new SubEntity
        try:
            metrics = self.integration_analyzer.compute_all_metrics(node_id)

            # Emit integration_metrics.node event
            telemetry = self.integration_analyzer.emit_telemetry(node_id, metrics)
            await self.broadcaster.broadcast_event("integration_metrics.node", {
                "v": "2",
                "citizen_id": self.citizen_id,
                **telemetry
            })

            logger.debug(f"[TopologyAnalyzer] Integration metrics computed for {node_id}: {metrics}")

        except Exception as e:
            logger.error(f"[TopologyAnalyzer] Failed to compute metrics for {node_id}: {e}")

        # 2. Batched betweenness recomputation
        self.spawn_count += 1

        if self.spawn_count >= self.betweenness_recompute_threshold:
            await self._recompute_betweenness()
            self.spawn_count = 0  # Reset counter

    async def _on_activation(self, payload: Dict[str, Any]):
        """
        Handle subentity.activation event.

        Checks if any activated SubEntity is a critical hub at risk (low energy).

        Event format:
        {
            "activations": [
                {
                    "id": "subentity_citizen_ops_42",
                    "energy": 0.15,
                    "threshold": 1.2,
                    "level": "weak"
                }
            ]
        }
        """
        activations = payload.get("activations", [])

        for activation in activations:
            node_id = activation.get("id")
            energy = activation.get("energy", 1.0)

            if not node_id:
                continue

            # Check if this is a critical hub at risk
            if energy < 0.2:  # Low energy threshold
                try:
                    risk_alert = self.rich_club_analyzer.detect_hub_at_risk(
                        hub_id=node_id,
                        energy_threshold=0.2
                    )

                    if risk_alert:
                        # Critical hub is at risk - emit alert
                        await self.broadcaster.broadcast_event("rich_club.hub_at_risk", {
                            "v": "2",
                            "citizen_id": self.citizen_id,
                            **risk_alert
                        })

                        logger.warning(
                            f"[TopologyAnalyzer] Hub at risk: {node_id} "
                            f"(betweenness={risk_alert.get('betweenness')}, energy={energy})"
                        )

                except Exception as e:
                    logger.error(f"[TopologyAnalyzer] Hub risk detection failed for {node_id}: {e}")

    async def _on_link_upsert(self, payload: Dict[str, Any]):
        """
        Handle graph.delta.link.upsert event.

        Invalidates community cache when MEMBER_OF edges are created.

        Event format:
        {
            "link_type": "MEMBER_OF",
            "source_id": "node_123",
            "target_id": "subentity_citizen_ops_42"
        }
        """
        link_type = payload.get("link_type")

        # Only process MEMBER_OF edges (affect community structure)
        if link_type != "MEMBER_OF":
            return

        # Invalidate community cache (forces recomputation on next breadth calculation)
        self.integration_analyzer.communities = None

        logger.debug("[TopologyAnalyzer] Community cache invalidated after MEMBER_OF edge creation")

        # Optional: Batched recomputation after N edges
        # self.edge_count += 1
        # if self.edge_count >= self.edge_recompute_threshold:
        #     await self._recompute_integration_metrics()
        #     self.edge_count = 0

    async def _on_analyze_request(self, payload: Dict[str, Any]):
        """
        Handle topology.analyze.request event (on-demand analysis).

        Event format:
        {
            "analysis_type": "rich_club" | "integration_metrics" | "full",
            "node_id": "subentity_citizen_ops_42"  # Optional, for single-node analysis
        }
        """
        analysis_type = payload.get("analysis_type", "full")
        node_id = payload.get("node_id")

        logger.info(f"[TopologyAnalyzer] Explicit analysis requested: {analysis_type}")

        try:
            # Rich-club analysis
            if analysis_type in ["rich_club", "full"]:
                await self._recompute_betweenness()

            # Integration metrics analysis
            if analysis_type in ["integration_metrics", "full"]:
                if node_id:
                    # Single node analysis
                    metrics = self.integration_analyzer.compute_all_metrics(node_id)
                    telemetry = self.integration_analyzer.emit_telemetry(node_id, metrics)
                    await self.broadcaster.broadcast_event("integration_metrics.node", {
                        "v": "2",
                        "citizen_id": self.citizen_id,
                        **telemetry
                    })
                else:
                    # Population distribution
                    distribution = self.integration_analyzer.compute_population_distribution()
                    await self.broadcaster.broadcast_event("integration_metrics.population", {
                        "v": "2",
                        "citizen_id": self.citizen_id,
                        "timestamp": time.time(),
                        **distribution
                    })

        except Exception as e:
            logger.error(f"[TopologyAnalyzer] Explicit analysis failed: {e}", exc_info=True)

    async def _recompute_betweenness(self):
        """
        Recompute betweenness centrality and emit rich-club snapshot.

        Uses debouncing to prevent over-computation.
        """
        # Debounce: Don't recompute more than once per min_recompute_interval
        now = time.time()
        if (now - self.last_betweenness_compute) < self.min_recompute_interval:
            logger.debug(
                f"[TopologyAnalyzer] Betweenness recompute skipped (debounce: "
                f"{now - self.last_betweenness_compute:.1f}s < {self.min_recompute_interval}s)"
            )
            return  # Skip, too soon

        self.last_betweenness_compute = now

        try:
            logger.info("[TopologyAnalyzer] Recomputing betweenness centrality...")

            # Compute betweenness for all nodes
            hubs = self.rich_club_analyzer.identify_rich_club_hubs(percentile=0.90)

            # Emit rich_club.snapshot event
            snapshot = self.rich_club_analyzer.emit_telemetry(hubs, event_type="rich_club.snapshot")
            await self.broadcaster.broadcast_event("rich_club.snapshot", {
                "v": "2",
                "citizen_id": self.citizen_id,
                **snapshot
            })

            logger.info(
                f"[TopologyAnalyzer] Betweenness computed: {len(hubs)} hubs identified "
                f"(sample_size={self.rich_club_analyzer.config.sample_size})"
            )

        except Exception as e:
            logger.error(f"[TopologyAnalyzer] Betweenness recomputation failed: {e}", exc_info=True)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get service statistics.

        Returns:
            {
                "uptime_seconds": float,
                "spawn_count": int,
                "edge_count": int,
                "last_betweenness_compute": float,
                "events_processed": {event_type: count},
                "rich_club_stats": {...},
                "integration_stats": {...}
            }
        """
        return {
            "uptime_seconds": time.time() - self.started_at,
            "spawn_count": self.spawn_count,
            "edge_count": self.edge_count,
            "last_betweenness_compute": self.last_betweenness_compute,
            "events_processed": dict(self.events_processed),
            "rich_club_stats": self.rich_club_analyzer.get_telemetry_stats(),
            "integration_stats": self.integration_analyzer.get_telemetry_stats()
        }
