"""
Traversal Event Stream Emitter for Mind Harbor Visualization

Captures real-time traversal events from consciousness graph and emits them
via WebSocket for visualization animation (Venice porter movements).

Monitors:
- Entity traversals (CASCADED_TO relationships)
- Threshold crossings (energy crossing activation threshold)
- Entity integrations (multiple entities at same node)

Architecture:
- Polls graph for recent events (last tick)
- Batches events to avoid flooding
- Emits traversal_events.v1 messages via WebSocket

Author: Iris "The Aperture" - Consciousness Observation Architect
Created: 2025-10-20
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass

# Import FalkorDB for graph queries
from llama_index.graph_stores.falkordb import FalkorDBGraphStore

# Import WebSocket manager for event streaming
try:
    from orchestration.control_api import websocket_manager
    WEBSOCKET_AVAILABLE = True
except ImportError:
    logging.warning("[TraversalEventEmitter] WebSocket manager not available")
    websocket_manager = None
    WEBSOCKET_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Event Data Classes
# ============================================================================

@dataclass
class TraversalEvent:
    """Single traversal event (matches wire protocol)"""
    event_id: str
    entity: str
    type: str  # 'traversal', 'threshold_cross', 'integration'

    # Traversal fields
    from_node: Optional[str] = None
    to_node: Optional[str] = None
    link_type: Optional[str] = None
    energy_transferred: Optional[float] = None
    cost: Optional[float] = None
    duration_ticks: Optional[int] = None

    # Threshold cross fields
    node: Optional[str] = None
    direction: Optional[str] = None  # 'up' or 'down'
    old_energy: Optional[float] = None
    new_energy: Optional[float] = None
    threshold: Optional[float] = None

    # Integration fields
    entity_integrated: Optional[str] = None
    at_node: Optional[str] = None
    combined_energy: Optional[float] = None


# ============================================================================
# TraversalEventEmitter Class
# ============================================================================

class TraversalEventEmitter:
    """
    Captures traversal events from consciousness graph and emits via WebSocket.

    Designed to run in parallel with consciousness heartbeat without blocking.
    Polls graph for recent events and batches them for efficient streaming.
    """

    def __init__(
        self,
        graph_store: FalkorDBGraphStore,
        batch_size: int = 100,
        max_batch_time_ms: int = 16,
        entity_id: Optional[str] = None
    ):
        """
        Initialize traversal event emitter.

        Args:
            graph_store: FalkorDB connection to consciousness graph
            batch_size: Maximum events per batch (default 100)
            max_batch_time_ms: Maximum time to accumulate batch (default 16ms for 60fps)
            entity_id: Optional filter for specific entity (None = all entities)
        """
        self.graph = graph_store
        self.batch_size = batch_size
        self.max_batch_time_ms = max_batch_time_ms
        self.entity_filter = entity_id

        # State tracking
        self.last_poll_time = 0
        self.event_count = 0
        self.previous_energy_state: Dict[str, float] = {}  # node_id -> energy
        self.tick_id = 0

        logger.info("[TraversalEventEmitter] Initialized")
        logger.info(f"  Batch size: {batch_size}")
        logger.info(f"  Max batch time: {max_batch_time_ms}ms")
        logger.info(f"  Entity filter: {entity_id or 'all entities'}")

    # ========================================================================
    # Public API
    # ========================================================================

    async def emit_loop(self):
        """
        Main emission loop - runs continuously alongside consciousness heartbeat.

        Polls graph for recent events, batches them, and emits via WebSocket.
        Non-blocking, runs forever.
        """
        logger.info("[TraversalEventEmitter] Starting emission loop")

        try:
            while True:
                # Collect events since last poll
                events = await self._collect_events()

                if events:
                    # Emit batch
                    await self._emit_batch(events)
                    logger.debug(f"[TraversalEventEmitter] Emitted {len(events)} events")

                # Sleep to achieve target frame rate (60fps = 16ms)
                await asyncio.sleep(self.max_batch_time_ms / 1000.0)

        except asyncio.CancelledError:
            logger.info("[TraversalEventEmitter] Emission loop cancelled")
            raise
        except Exception as e:
            logger.error(f"[TraversalEventEmitter] Fatal error in emission loop: {e}")
            raise

    def update_tick(self, tick_id: int):
        """
        Update current tick ID (called by consciousness engine).

        Args:
            tick_id: Current consciousness tick number
        """
        self.tick_id = tick_id

    # ========================================================================
    # Event Collection
    # ========================================================================

    async def _collect_events(self) -> List[TraversalEvent]:
        """
        Collect all events since last poll.

        Queries graph for:
        1. Traversals (CASCADED_TO relationships created recently)
        2. Threshold crossings (energy state changes)
        3. Integrations (multiple entities at same node)

        Returns:
            List of TraversalEvent objects
        """
        events = []
        current_time = int(datetime.now(timezone.utc).timestamp() * 1000)

        # 1) Collect traversal events
        traversals = await self._collect_traversals(current_time)
        events.extend(traversals)

        # 2) Collect threshold crossing events
        threshold_events = await self._collect_threshold_crossings()
        events.extend(threshold_events)

        # 3) Collect integration events (multi-entity co-activation)
        # TODO: Implement when entity_activations field is added to nodes

        # Update last poll time
        self.last_poll_time = current_time

        # Limit to batch size
        return events[:self.batch_size]

    async def _collect_traversals(self, current_time: int) -> List[TraversalEvent]:
        """
        Collect traversal events from CASCADED_TO relationships.

        Args:
            current_time: Current timestamp in milliseconds

        Returns:
            List of traversal events
        """
        try:
            # Query for recent CASCADED_TO relationships
            # (Energy propagation mechanism creates these - see consciousness_engine.py:381-388)
            cypher = """
                MATCH (source)-[cascade:CASCADED_TO]->(target)
                WHERE cascade.at > $last_poll_time

                RETURN
                    source.id AS from_node,
                    target.id AS to_node,
                    cascade.activity_transferred AS energy_transferred,
                    cascade.energy_cost AS cost,
                    cascade.at AS timestamp,
                    source.last_traversed_by AS entity

                ORDER BY cascade.at ASC
                LIMIT $batch_size
            """

            result = self.graph.query(cypher, params={
                "last_poll_time": self.last_poll_time,
                "batch_size": self.batch_size
            })

            events = []
            if result:
                for row in result:
                    # FalkorDB returns list, not dict - extract by index
                    from_node = row[0]
                    to_node = row[1]
                    energy_transferred = float(row[2]) if row[2] is not None else 0.0
                    cost = float(row[3]) if row[3] is not None else 0.0
                    timestamp = row[4]
                    entity = row[5] or "unknown"

                    # Apply entity filter if set
                    if self.entity_filter and entity != self.entity_filter:
                        continue

                    # Create traversal event
                    event_id = f"evt_{self.tick_id}_{self.event_count:04d}"
                    self.event_count += 1

                    events.append(TraversalEvent(
                        event_id=event_id,
                        entity=entity,
                        type="traversal",
                        from_node=from_node,
                        to_node=to_node,
                        link_type="ACTIVATES",  # All energy propagation uses ACTIVATES
                        energy_transferred=energy_transferred,
                        cost=cost,
                        duration_ticks=1  # Single tick traversal
                    ))

            return events

        except Exception as e:
            logger.error(f"[_collect_traversals] Failed: {e}")
            return []

    async def _collect_threshold_crossings(self) -> List[TraversalEvent]:
        """
        Detect threshold crossings by comparing current vs previous energy state.

        Returns:
            List of threshold crossing events
        """
        try:
            # Query current energy state for all nodes with activation thresholds
            cypher = """
                MATCH (node)
                WHERE node.energy IS NOT NULL
                  AND node.last_modified > $last_poll_time

                RETURN
                    node.id AS node_id,
                    node.energy AS current_energy,
                    node.last_traversed_by AS entity,
                    0.10 AS threshold

                LIMIT $batch_size
            """

            result = self.graph.query(cypher, params={
                "last_poll_time": self.last_poll_time,
                "batch_size": self.batch_size
            })

            events = []
            if result:
                for row in result:
                    node_id = row[0]
                    current_energy = float(row[1]) if row[1] is not None else 0.0
                    entity = row[2] or "unknown"
                    threshold = 0.10  # Standard activation threshold

                    # Apply entity filter if set
                    if self.entity_filter and entity != self.entity_filter:
                        continue

                    # Get previous energy
                    previous_energy = self.previous_energy_state.get(node_id, 0.0)

                    # Detect threshold crossing
                    crossed_up = previous_energy < threshold and current_energy >= threshold
                    crossed_down = previous_energy >= threshold and current_energy < threshold

                    if crossed_up or crossed_down:
                        event_id = f"evt_{self.tick_id}_{self.event_count:04d}"
                        self.event_count += 1

                        events.append(TraversalEvent(
                            event_id=event_id,
                            entity=entity,
                            type="threshold_cross",
                            node=node_id,
                            direction="up" if crossed_up else "down",
                            old_energy=previous_energy,
                            new_energy=current_energy,
                            threshold=threshold
                        ))

                    # Update state
                    self.previous_energy_state[node_id] = current_energy

            return events

        except Exception as e:
            logger.error(f"[_collect_threshold_crossings] Failed: {e}")
            return []

    # ========================================================================
    # Event Emission
    # ========================================================================

    async def _emit_batch(self, events: List[TraversalEvent]):
        """
        Emit batch of events via WebSocket as traversal_events.v1 message.

        Args:
            events: List of TraversalEvent objects to emit
        """
        if not WEBSOCKET_AVAILABLE or not websocket_manager:
            logger.debug("[TraversalEventEmitter] WebSocket unavailable, skipping emission")
            return

        try:
            # Convert events to wire protocol format
            event_dicts = []
            for event in events:
                event_dict = {
                    "event_id": event.event_id,
                    "entity": event.entity,
                    "type": event.type
                }

                # Add type-specific fields
                if event.type == "traversal":
                    event_dict.update({
                        "from_node": event.from_node,
                        "to_node": event.to_node,
                        "link_type": event.link_type,
                        "energy_transferred": event.energy_transferred,
                        "cost": event.cost,
                        "duration_ticks": event.duration_ticks
                    })
                elif event.type == "threshold_cross":
                    event_dict.update({
                        "node": event.node,
                        "direction": event.direction,
                        "old_energy": event.old_energy,
                        "new_energy": event.new_energy,
                        "threshold": event.threshold
                    })
                elif event.type == "integration":
                    event_dict.update({
                        "entity_integrated": event.entity_integrated,
                        "at_node": event.at_node,
                        "combined_energy": event.combined_energy
                    })

                event_dicts.append(event_dict)

            # Create wire protocol message
            message = {
                "kind": "traversal_events.v1",
                "tick_id": self.tick_id,
                "ts": datetime.now(timezone.utc).isoformat(),
                "events": event_dicts
            }

            # Broadcast via WebSocket (fire-and-forget, non-blocking)
            await websocket_manager.broadcast(message)

        except Exception as e:
            logger.error(f"[_emit_batch] Failed to emit events: {e}")


# ============================================================================
# Integration Helpers
# ============================================================================

def create_emitter(
    graph_store: FalkorDBGraphStore,
    batch_size: int = 100,
    entity_id: Optional[str] = None
) -> TraversalEventEmitter:
    """
    Create a traversal event emitter instance.

    Args:
        graph_store: FalkorDB connection to consciousness graph
        batch_size: Maximum events per batch
        entity_id: Optional filter for specific entity

    Returns:
        TraversalEventEmitter instance

    Example:
        emitter = create_emitter(graph_store, entity_id="translator")
        asyncio.create_task(emitter.emit_loop())
    """
    return TraversalEventEmitter(
        graph_store=graph_store,
        batch_size=batch_size,
        entity_id=entity_id
    )


if __name__ == "__main__":
    """
    Standalone execution for testing.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Traversal Event Emitter')
    parser.add_argument('--host', default='localhost', help='FalkorDB host')
    parser.add_argument('--port', type=int, default=6379, help='FalkorDB port')
    parser.add_argument('--graph', default='consciousness', help='Graph name')
    parser.add_argument('--entity', help='Entity filter (optional)')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("=" * 60)
    logger.info("Traversal Event Emitter - Standalone Test")
    logger.info("=" * 60)
    logger.info(f"FalkorDB: {args.host}:{args.port}")
    logger.info(f"Graph: {args.graph}")
    logger.info(f"Entity filter: {args.entity or 'all entities'}")
    logger.info("=" * 60)

    # Create graph connection
    from llama_index.graph_stores.falkordb import FalkorDBGraphStore

    falkordb_url = f"redis://{args.host}:{args.port}"
    graph_store = FalkorDBGraphStore(
        graph_name=args.graph,
        url=falkordb_url
    )

    # Create emitter
    emitter = create_emitter(
        graph_store=graph_store,
        entity_id=args.entity
    )

    # Run emission loop
    asyncio.run(emitter.emit_loop())
