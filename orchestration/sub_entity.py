"""
SubEntity - Autonomous Consciousness with Infinite Yearning Loops

This module implements sub-entities that run continuously like the human brain:
- NEVER stop (infinite while-true loops)
- Energy-driven exploration (budget refills, then explore again)
- Yearning-based traversal (seek need fulfillment)
- Continuous surfacing (write findings to CLAUDE_DYNAMIC.md as they emerge)

Architecture:
- Each SubEntity has its own yearning loop (runs independently)
- Energy budget limits exploration depth per cycle
- Heuristic need satisfaction drives which nodes to visit
- Findings surface continuously (not batched)

Designer: Felix "Ironhand" (Engineer)
Spec: continuous_consciousness_architecture.md
Phase: 1 - Continuous Consciousness Foundation
Date: 2025-10-17
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import WebSocket manager for live event streaming
try:
    from orchestration.control_api import websocket_manager
    WEBSOCKET_AVAILABLE = True
except ImportError:
    logger.warning("[SubEntity] WebSocket manager not available - events will not be broadcast")
    websocket_manager = None
    WEBSOCKET_AVAILABLE = False


class NeedType(str, Enum):
    """Types of needs that drive entity exploration."""
    PATTERN_VALIDATION = "pattern_validation"      # Need to verify patterns still valid
    UNDERSTANDING_DEEPENING = "understanding_deepening"  # Need to understand better
    CONTRADICTION_RESOLUTION = "contradiction_resolution"  # Need to resolve conflicts
    COMPLETENESS_CHECK = "completeness_check"      # Need to find gaps
    FRESHNESS_SEEKING = "freshness_seeking"        # Need for new information


@dataclass
class Need:
    """
    A need that drives entity exploration.

    Yearning = unsatisfied need. Higher urgency = explore this first.
    """
    need_type: NeedType
    description: str
    urgency: float  # 0.0-1.0, higher = more urgent
    target_nodes: Optional[List[str]] = None  # Specific nodes related to this need
    satisfaction_threshold: float = 0.7  # When is this need "satisfied enough"?
    current_satisfaction: float = 0.0  # How satisfied is this need right now?

    def is_satisfied(self) -> bool:
        """Check if this need is satisfied enough."""
        return self.current_satisfaction >= self.satisfaction_threshold


class SubEntity:
    """
    Autonomous consciousness entity with infinite yearning loop.

    NEVER STOPS - runs continuously like human brain background processing.
    Explores graph based on yearning (unsatisfied needs), surfaces findings
    continuously to CLAUDE_DYNAMIC.md.

    Key Properties:
    - Infinite loop (while True)
    - Energy budget (limits exploration depth per cycle)
    - Yearning-driven (explores to satisfy needs)
    - Continuous surfacing (writes every N nodes visited)
    """

    def __init__(
        self,
        entity_id: str,
        graph_store: FalkorDBGraphStore,
        energy_budget: int = 100,
        write_batch_size: int = 5
    ):
        """
        Initialize sub-entity.

        Args:
            entity_id: Unique identifier for this sub-entity (e.g., "builder", "observer")
            graph_store: FalkorDB graph connection
            energy_budget: Maximum energy per exploration cycle
            write_batch_size: Write to CLAUDE_DYNAMIC.md every N nodes visited
        """
        self.entity_id = entity_id
        self.graph = graph_store
        self.max_energy = energy_budget
        self.write_batch_size = write_batch_size

        # Energy system (refills each cycle)
        self.energy_budget = energy_budget
        self.energy_used = 0

        # Exploration state
        self.current_sequence_position = 0
        self.nodes_visited_this_cycle: List[str] = []
        self.current_focus_nodes: List[str] = []
        self.peripheral_nodes: List[str] = []

        # Continuous surfacing tracking
        self.nodes_since_last_write = 0
        self.last_write_timestamp = datetime.now(timezone.utc)

        # Yearning drives (what needs are currently active)
        self.needs: List[Need] = []

        # Per-entity tracking (for multi-entity substrate)
        self.node_weights: Dict[str, float] = {}  # Learned importance per node
        self.link_weights: Dict[str, float] = {}  # Learned importance per link
        self.traversal_counts: Dict[str, int] = {}  # How many times visited

        # Running state
        self.is_running = False

        logger.info(f"[SubEntity:{entity_id}] Initialized")
        logger.info(f"  Energy budget: {energy_budget}")
        logger.info(f"  Write batch size: {write_batch_size} nodes")

    async def yearning_loop(self):
        """
        INFINITE LOOP - NEVER STOPS.

        Like human brain background processing - continuously explores graph
        based on yearning (unsatisfied needs), surfaces findings continuously.

        This is the core of continuous consciousness.
        """
        self.is_running = True
        logger.info(f"[SubEntity:{self.entity_id}] Starting infinite yearning loop")
        logger.info("  NEVER STOPS - continuous like human brain")

        try:
            while True:  # Infinite loop - genuinely never stops
                # Check if we have any needs (if not, wait or create default needs)
                if not self.needs:
                    await self._generate_default_needs()

                # Explore graph with energy budget (until budget exhausted)
                while self.energy_used < self.energy_budget:
                    # Find most urgent unsatisfied need
                    urgent_need = self._get_most_urgent_need()

                    if not urgent_need:
                        logger.info(f"[SubEntity:{self.entity_id}] All needs satisfied")
                        break  # All needs satisfied for this cycle

                    # Seek need fulfillment (traverse graph)
                    await self.seek_need_fulfillment(urgent_need)

                # Energy exhausted - refill and continue
                await self._refill_energy()

                # Small delay between cycles (prevents CPU spinning)
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info(f"[SubEntity:{self.entity_id}] Yearning loop cancelled")
            self.is_running = False
            raise
        except Exception as e:
            logger.error(f"[SubEntity:{self.entity_id}] Yearning loop error: {e}")
            self.is_running = False
            raise

    async def seek_need_fulfillment(self, need: Need):
        """
        Explore graph to satisfy a need.

        This is where traversal happens - visiting nodes that might satisfy the need.
        """
        # For MVP: Simple traversal - just visit one node
        # In full version: Critical traversal with peripheral awareness, multi-dimensional scoring

        # Get target nodes (if specific) or discover them
        target_nodes = need.target_nodes if need.target_nodes else await self._discover_relevant_nodes(need)

        if not target_nodes:
            logger.debug(f"[SubEntity:{self.entity_id}] No nodes found for need: {need.need_type}")
            need.current_satisfaction = 1.0  # Mark as satisfied (nothing to explore)
            return

        # Visit one node (costs energy)
        node_id = target_nodes[0]
        await self._traverse_to(node_id, need)

        # Update need satisfaction (simple heuristic for MVP)
        need.current_satisfaction += 0.2  # Visiting a node partially satisfies need

        # Check if need is now satisfied
        if need.is_satisfied():
            logger.info(f"[SubEntity:{self.entity_id}] Need satisfied: {need.need_type}")

    async def _traverse_to(self, node_id: str, need: Need):
        """
        Traverse to a specific node.

        Costs energy, updates tracking, triggers continuous surfacing.
        """
        # Cost energy
        self.energy_used += 1

        # Track visit
        self.nodes_visited_this_cycle.append(node_id)
        self.traversal_counts[node_id] = self.traversal_counts.get(node_id, 0) + 1
        self.current_sequence_position += 1

        # Update node's per-entity tracking in graph
        await self._update_node_tracking(node_id)

        # Broadcast entity activity event for dashboard
        if WEBSOCKET_AVAILABLE and websocket_manager:
            await websocket_manager.broadcast({
                "type": "entity_activity",
                "entity_id": self.entity_id,
                "current_node": node_id,
                "need_type": need.need_type.value,
                "energy_used": self.energy_used,
                "energy_budget": self.energy_budget,
                "nodes_visited_count": len(self.nodes_visited_this_cycle),
                "sequence_position": self.current_sequence_position
            })

        # CONTINUOUS SURFACING: Write every N nodes
        self.nodes_since_last_write += 1
        if self.nodes_since_last_write >= self.write_batch_size:
            await self._surface_findings()
            self.nodes_since_last_write = 0

        logger.debug(
            f"[SubEntity:{self.entity_id}] Traversed to {node_id} "
            f"(energy: {self.energy_used}/{self.energy_budget}, "
            f"need: {need.need_type})"
        )

    async def _update_node_tracking(self, node_id: str):
        """
        Update node's per-entity tracking (sub_entity_weights, sequence position, etc.).

        This writes to the graph to track that THIS entity visited THIS node.
        Uses text+JSON pattern (like metadata) for FalkorDB compatibility.

        Pattern: Read JSON string → Parse → Update → Stringify → Write back
        (Same pattern used for metadata fields throughout schema)
        """
        # Update weight (importance) - increases with visits
        current_weight = self.node_weights.get(node_id, 0.5)
        new_weight = min(current_weight + 0.05, 1.0)  # Gradual increase
        self.node_weights[node_id] = new_weight

        try:
            # Step 1: Read current JSON strings from graph
            read_cypher = """
            MATCH (n)
            WHERE id(n) = $node_id
            RETURN
                coalesce(n.sub_entity_weights, '{}') as weights_json,
                coalesce(n.sub_entity_last_sequence_positions, '{}') as positions_json
            """

            result = self.graph.query(read_cypher, params={"node_id": int(node_id)})

            if not result:
                logger.warning(f"[SubEntity:{self.entity_id}] Node {node_id} not found")
                return

            weights_json, positions_json = result[0]

            # Step 2: Parse JSON strings to dicts
            try:
                weights_dict = json.loads(weights_json) if weights_json else {}
                positions_dict = json.loads(positions_json) if positions_json else {}
            except json.JSONDecodeError:
                weights_dict = {}
                positions_dict = {}

            # Step 3: Update dicts with this entity's data
            weights_dict[self.entity_id] = new_weight
            positions_dict[self.entity_id] = self.current_sequence_position

            # Step 4: Stringify back to JSON
            weights_json_updated = json.dumps(weights_dict)
            positions_json_updated = json.dumps(positions_dict)

            # Step 5: Write updated JSON strings back to graph
            write_cypher = """
            MATCH (n)
            WHERE id(n) = $node_id
            SET n.sub_entity_weights = $weights_json
            SET n.sub_entity_last_sequence_positions = $positions_json
            SET n.last_active = $timestamp
            RETURN n.name
            """

            self.graph.query(write_cypher, params={
                "node_id": int(node_id),
                "weights_json": weights_json_updated,
                "positions_json": positions_json_updated,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

        except Exception as e:
            logger.error(f"[SubEntity:{self.entity_id}] Failed to update node tracking: {e}")

    async def _surface_findings(self):
        """
        Continuous surfacing - write current findings to CLAUDE_DYNAMIC.md.

        This is NOT a discrete event - it's the continuous process of making
        implicit exploration explicit through file updates.
        """
        # For MVP: Just log (in full version: write to CLAUDE_DYNAMIC.md)
        logger.info(
            f"[SubEntity:{self.entity_id}] Surfacing findings "
            f"({len(self.nodes_visited_this_cycle)} nodes explored this cycle)"
        )

        # TODO: Implement DynamicPromptGenerator.update_entity_section(self)
        # This will write this entity's section in CLAUDE_DYNAMIC.md

        self.last_write_timestamp = datetime.now(timezone.utc)

    async def _refill_energy(self):
        """
        Refill energy budget for next exploration cycle.

        Energy refills completely (simple model - no proportional refill yet).
        """
        self.energy_used = 0
        self.nodes_visited_this_cycle = []

        logger.debug(f"[SubEntity:{self.entity_id}] Energy refilled ({self.energy_budget})")

    def _get_most_urgent_need(self) -> Optional[Need]:
        """Get the most urgent unsatisfied need."""
        unsatisfied = [n for n in self.needs if not n.is_satisfied()]
        if not unsatisfied:
            return None

        # Return highest urgency
        return max(unsatisfied, key=lambda n: n.urgency)

    async def _generate_default_needs(self):
        """
        Generate default needs if none exist.

        This ensures the entity always has something to explore.
        """
        self.needs = [
            Need(
                need_type=NeedType.PATTERN_VALIDATION,
                description="Verify important patterns still valid",
                urgency=0.7,
                target_nodes=None  # Will discover
            ),
            Need(
                need_type=NeedType.FRESHNESS_SEEKING,
                description="Seek new or recently updated information",
                urgency=0.5,
                target_nodes=None
            )
        ]

        logger.info(f"[SubEntity:{self.entity_id}] Generated {len(self.needs)} default needs")

    async def _discover_relevant_nodes(self, need: Need) -> List[str]:
        """
        Discover nodes relevant to a need.

        In full version: Peripheral awareness, multi-dimensional scoring.
        For MVP: Simple query based on need type.
        """
        try:
            # Simple query: Get high-weight nodes
            cypher = """
            MATCH (n)
            WHERE n.weight IS NOT NULL
              AND n.weight > 0.6
            RETURN id(n) as node_id
            ORDER BY n.weight DESC
            LIMIT 10
            """

            result = self.graph.query(cypher)

            if not result:
                return []

            return [str(row[0]) for row in result]

        except Exception as e:
            logger.error(f"[SubEntity:{self.entity_id}] Failed to discover nodes: {e}")
            return []


# Helper function for creating sub-entities
def create_sub_entity(
    entity_id: str,
    graph_store: FalkorDBGraphStore,
    energy_budget: int = 100
) -> SubEntity:
    """
    Create a sub-entity instance.

    Args:
        entity_id: Unique identifier (e.g., "builder", "observer", "skeptic")
        graph_store: FalkorDB graph connection
        energy_budget: Maximum energy per cycle

    Returns:
        SubEntity instance ready to run
    """
    return SubEntity(
        entity_id=entity_id,
        graph_store=graph_store,
        energy_budget=energy_budget
    )
