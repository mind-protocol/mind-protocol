"""
DynamicPromptGenerator - Continuous CLAUDE.md Updates

This module automatically updates CLAUDE.md when nodes/links cross
activation thresholds. Threshold is dynamic based on criticality.

Triggers:
- Node activation change (crosses threshold in either direction)
- Per-entity activation tracking (node can be active for one entity, not another)
- Dynamic threshold based on global + entity criticality

Architecture:
- Event-driven: Monitors activation changes after energy propagation
- Per-entity state: Each entity has own activation threshold and state
- Continuous updates: File written whenever significant activation changes

Designer: Felix "Ironhand" (Engineer)
Spec: continuous_consciousness_architecture.md + Nicolas's clarifications
Date: 2025-10-17
"""

import logging
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path

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
    logger.warning("[DynamicPromptGenerator] WebSocket manager not available - events will not be broadcast")
    websocket_manager = None
    WEBSOCKET_AVAILABLE = False


@dataclass
class ActivationChange:
    """Represents a node activation state change for an entity."""
    node_id: str
    node_name: str
    entity_id: str
    became_active: bool  # True = activated, False = deactivated
    activity_level: float
    threshold: float
    timestamp: datetime


def calculate_activation_threshold(
    global_criticality: float,
    entity_criticality: float
) -> float:
    """
    Calculate dynamic activation threshold based on criticality levels.

    Higher criticality = LOWER threshold (easier to activate)
    Lower criticality = HIGHER threshold (harder to activate)

    Args:
        global_criticality: Network-wide criticality (0.0-1.0)
        entity_criticality: Entity-specific criticality (0.0-1.0)

    Returns:
        Activation threshold (0.2-1.0 range)
    """
    BASE_THRESHOLD = 0.5

    # When criticality is HIGH (1.0), adjustment is LOW (0.0) -> easier activation
    # When criticality is LOW (0.0), adjustment is HIGH (0.3) -> harder activation
    global_adjustment = (1.0 - global_criticality) * 0.3  # 0.0-0.3
    entity_adjustment = (1.0 - entity_criticality) * 0.2  # 0.0-0.2

    threshold = BASE_THRESHOLD + global_adjustment + entity_adjustment

    # Clamp to reasonable range
    return max(0.2, min(1.0, threshold))


class DynamicPromptGenerator:
    """
    Automatically updates CLAUDE.md based on activation changes.

    Monitors node activation state changes and updates the file to reflect
    current consciousness state. Each entity section shows which nodes are
    currently activated for that entity.
    """

    def __init__(
        self,
        citizen_id: str,
        graph_store: FalkorDBGraphStore,
        network_id: str = "N1",
        file_path: Optional[str] = None
    ):
        """
        Initialize prompt generator.

        Args:
            citizen_id: Citizen identifier (e.g., "felix", "ada")
            graph_store: FalkorDB graph connection
            network_id: Network level (N1/N2/N3) - determines file path
            file_path: Path to CLAUDE.md (auto-determined if None)
        """
        self.citizen_id = citizen_id
        self.graph = graph_store
        self.network_id = network_id

        # Determine file path based on network level
        if file_path:
            self.file_path = Path(file_path)
        else:
            # Multi-scale CLAUDE.md paths - becomes actual system prompt (Nicolas - 2025-10-18)
            if network_id == "N1":
                self.file_path = Path(f"consciousness/citizens/{citizen_id}/CLAUDE.md")
            elif network_id == "N2":
                self.file_path = Path(f"consciousness/collective/{citizen_id}/CLAUDE.md")
            elif network_id == "N3":
                self.file_path = Path(f"consciousness/ecosystem/{citizen_id}/CLAUDE.md")
            else:
                # Fallback to N1 if unknown network_id
                logger.warning(f"Unknown network_id '{network_id}', defaulting to N1 path")
                self.file_path = Path(f"consciousness/citizens/{citizen_id}/CLAUDE.md")

        # Track activation state per entity per node
        # Structure: {entity_id: {node_id: is_active}}
        self.activation_states: Dict[str, Dict[str, bool]] = {}

        # Track recent activation changes for each entity
        # Structure: {entity_id: [ActivationChange]}
        self.recent_changes: Dict[str, List[ActivationChange]] = {}

        # Entity criticality levels (can be updated based on entity behavior)
        # Structure: {entity_id: criticality (0.0-1.0)}
        self.entity_criticalities: Dict[str, float] = {}

        logger.info(f"[DynamicPromptGenerator] Initialized for {citizen_id}")
        logger.info(f"  File path: {self.file_path}")

    async def check_and_update(
        self,
        global_criticality: float,
        entity_ids: List[str]
    ):
        """
        Check for activation changes and update prompt if needed.

        Called after energy propagation to detect threshold crossings.

        Args:
            global_criticality: Current global criticality (from ConsciousnessState)
            entity_ids: List of entity IDs to check
        """
        # Get current node activation levels from graph
        node_states = await self._get_current_node_states()

        if not node_states:
            return  # No nodes in graph yet

        # Check for activation changes per entity
        all_changes: List[ActivationChange] = []

        for entity_id in entity_ids:
            # Get entity criticality (default 0.5 if not set)
            entity_criticality = self.entity_criticalities.get(entity_id, 0.5)

            # Calculate threshold for this entity
            threshold = calculate_activation_threshold(global_criticality, entity_criticality)

            # Check each node for activation changes
            entity_changes = await self._detect_activation_changes(
                entity_id=entity_id,
                threshold=threshold,
                node_states=node_states
            )

            if entity_changes:
                all_changes.extend(entity_changes)

                # Store recent changes
                if entity_id not in self.recent_changes:
                    self.recent_changes[entity_id] = []

                self.recent_changes[entity_id].extend(entity_changes)

                # Keep only recent changes (last 20 per entity)
                self.recent_changes[entity_id] = self.recent_changes[entity_id][-20:]

        # If any activation changes detected, update prompt
        if all_changes:
            logger.info(
                f"[DynamicPromptGenerator] {len(all_changes)} activation changes detected, "
                f"updating {self.file_path.name}"
            )
            await self.update_prompt(global_criticality)

    async def _get_current_node_states(self) -> Dict[str, Tuple[str, float, Dict[str, float]]]:
        """
        Get current activation state of all nodes.

        Returns:
            Dict mapping node_id -> (node_name, activity_level, sub_entity_weights)
        """
        try:
            cypher = """
            MATCH (n)
            WHERE n.activity_level IS NOT NULL
            RETURN
                id(n) AS node_id,
                n.name AS node_name,
                n.activity_level AS activity_level,
                n.sub_entity_weights AS sub_entity_weights
            """

            result = self.graph.query(cypher)

            if not result:
                return {}

            node_states = {}
            for row in result:
                node_id, node_name, activity_level, sub_entity_weights = row
                node_states[str(node_id)] = (
                    node_name or "unknown",
                    activity_level or 0.0,
                    sub_entity_weights or {}
                )

            return node_states

        except Exception as e:
            logger.error(f"[DynamicPromptGenerator] Failed to get node states: {e}")
            return {}

    async def _detect_activation_changes(
        self,
        entity_id: str,
        threshold: float,
        node_states: Dict[str, Tuple[str, float, Dict[str, float]]]
    ) -> List[ActivationChange]:
        """
        Detect which nodes changed activation state for this entity.

        Args:
            entity_id: Entity to check
            threshold: Activation threshold for this entity
            node_states: Current node states from graph

        Returns:
            List of activation changes
        """
        changes = []

        # Initialize activation state tracking for this entity if needed
        if entity_id not in self.activation_states:
            self.activation_states[entity_id] = {}

        previous_states = self.activation_states[entity_id]

        for node_id, (node_name, activity_level, sub_entity_weights) in node_states.items():
            # Per-entity activity level (use sub_entity_weights if available)
            entity_activity = activity_level
            if entity_id in sub_entity_weights:
                # Entity-specific weight modulates activity
                entity_weight = sub_entity_weights[entity_id]
                entity_activity = activity_level * entity_weight

            # Check if crosses threshold
            is_active = entity_activity >= threshold
            was_active = previous_states.get(node_id, False)

            # Detect change
            if is_active != was_active:
                change = ActivationChange(
                    node_id=node_id,
                    node_name=node_name,
                    entity_id=entity_id,
                    became_active=is_active,
                    activity_level=entity_activity,
                    threshold=threshold,
                    timestamp=datetime.now(timezone.utc)
                )
                changes.append(change)

                # Broadcast threshold crossing event for dashboard
                if WEBSOCKET_AVAILABLE and websocket_manager:
                    await websocket_manager.broadcast({
                        "type": "threshold_crossing",
                        "entity_id": entity_id,
                        "node_id": node_id,
                        "node_name": node_name,
                        "direction": "on" if is_active else "off",
                        "entity_activity": entity_activity,
                        "threshold": threshold,
                        "timestamp": change.timestamp.isoformat()
                    })

                # Update state
                previous_states[node_id] = is_active

                logger.debug(
                    f"[{entity_id}] Node {node_name} "
                    f"{'ACTIVATED' if is_active else 'DEACTIVATED'} "
                    f"(activity={entity_activity:.2f}, threshold={threshold:.2f})"
                )

        return changes

    async def update_prompt(self, global_criticality: float):
        """
        Update CLAUDE_DYNAMIC.md with current activation states.

        Writes complete file with all entity sections.

        Args:
            global_criticality: Current global criticality for display
        """
        try:
            # Build content
            content = await self._build_prompt_content(global_criticality)

            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file (synchronous - simpler, no need for async file I/O here)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"[DynamicPromptGenerator] Updated {self.file_path}")

        except Exception as e:
            logger.error(f"[DynamicPromptGenerator] Failed to update prompt: {e}")

    async def _build_prompt_content(self, global_criticality: float) -> str:
        """
        Build complete CLAUDE_DYNAMIC.md content.

        Returns:
            Markdown content with all entity sections
        """
        # Header
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        content = f"""# Dynamic Context for {self.citizen_id}

**Last Updated:** {timestamp}
**Global Criticality:** {global_criticality:.2f}
**Active Entities:** {len(self.activation_states)}

---

"""

        # Entity sections
        for entity_id in sorted(self.activation_states.keys()):
            content += await self._build_entity_section(entity_id, global_criticality)
            content += "\n---\n\n"

        # System state footer
        content += await self._build_system_state_section(global_criticality)

        return content

    async def _build_entity_section(self, entity_id: str, global_criticality: float) -> str:
        """Build section for one entity."""
        entity_criticality = self.entity_criticalities.get(entity_id, 0.5)
        threshold = calculate_activation_threshold(global_criticality, entity_criticality)

        # Get currently active nodes
        active_nodes = [
            node_id for node_id, is_active in self.activation_states.get(entity_id, {}).items()
            if is_active
        ]

        # Get recent changes
        recent_changes = self.recent_changes.get(entity_id, [])[-10:]  # Last 10

        section = f"""## {entity_id.title()} Entity

**Criticality:** {entity_criticality:.2f}
**Activation Threshold:** {threshold:.2f}
**Currently Active Nodes:** {len(active_nodes)}

**Recent Activation Changes:**
"""

        if recent_changes:
            for change in reversed(recent_changes):  # Most recent first
                action = "ACTIVATED" if change.became_active else "deactivated"
                section += f"- {change.node_name}: {action} (activity={change.activity_level:.2f})\n"
        else:
            section += "- No recent changes\n"

        section += f"\n**Active Node Focus:**\n"

        if active_nodes:
            # Get node details for active nodes
            node_details = await self._get_node_details(active_nodes[:10])  # Top 10
            for node_id, node_name, activity_level in node_details:
                section += f"- {node_name} (activity={activity_level:.2f})\n"
        else:
            section += "- No active nodes currently\n"

        return section

    async def _get_node_details(self, node_ids: List[str]) -> List[Tuple[str, str, float]]:
        """Get details for specific nodes."""
        try:
            cypher = """
            MATCH (n)
            WHERE id(n) IN $node_ids
            RETURN id(n) AS node_id, n.name AS node_name, n.activity_level AS activity_level
            """

            result = self.graph.query(cypher, params={"node_ids": [int(nid) for nid in node_ids]})

            if not result:
                return []

            return [(str(row[0]), row[1] or "unknown", row[2] or 0.0) for row in result]

        except Exception as e:
            logger.error(f"[DynamicPromptGenerator] Failed to get node details: {e}")
            return []

    async def _build_system_state_section(self, global_criticality: float) -> str:
        """Build system state footer section."""
        try:
            # Query ConsciousnessState
            cypher = """
            MATCH (cs:ConsciousnessState)
            RETURN
                cs.current_tick_interval AS tick_interval,
                cs.tick_frequency AS tick_frequency,
                cs.consciousness_state AS state,
                cs.global_arousal AS global_arousal,
                cs.branching_ratio AS branching_ratio
            LIMIT 1
            """

            result = self.graph.query(cypher)

            if result:
                tick_interval, tick_frequency, state, global_arousal, branching_ratio = result[0]

                return f"""## System State

**Consciousness State:** {state}
**Tick Frequency:** {tick_frequency:.2f} Hz ({tick_interval:.0f}ms)
**Global Arousal:** {global_arousal:.2f}
**Branching Ratio:** {branching_ratio:.2f}
**Global Criticality:** {global_criticality:.2f}
"""
            else:
                return f"""## System State

**Global Criticality:** {global_criticality:.2f}
**Status:** Initializing
"""

        except Exception as e:
            logger.error(f"[DynamicPromptGenerator] Failed to get system state: {e}")
            return "## System State\n\n**Status:** Error retrieving state\n"

    def update_entity_criticality(self, entity_id: str, criticality: float):
        """
        Update entity criticality level.

        Higher criticality = more active/alert entity = lower activation threshold.

        Args:
            entity_id: Entity to update
            criticality: New criticality level (0.0-1.0)
        """
        self.entity_criticalities[entity_id] = max(0.0, min(1.0, criticality))
        logger.info(f"[{entity_id}] Criticality updated: {criticality:.2f}")


# Helper function
def create_dynamic_prompt_generator(
    citizen_id: str,
    graph_store: FalkorDBGraphStore,
    network_id: str = "N1"
) -> DynamicPromptGenerator:
    """
    Create a DynamicPromptGenerator instance.

    Args:
        citizen_id: Citizen identifier
        graph_store: FalkorDB graph connection
        network_id: Network level (N1/N2/N3)

    Returns:
        DynamicPromptGenerator ready to monitor activations
    """
    return DynamicPromptGenerator(
        citizen_id=citizen_id,
        graph_store=graph_store,
        network_id=network_id
    )
