"""
N2 Activation Monitor - Autonomous Citizen Awakening

This module monitors AI_Agent nodes in N2 (organizational) graph for activation.
When an AI_Agent's total_energy crosses threshold (0.7), the corresponding
citizen awakens automatically with aggregated context.

Pure emergence-based awakening:
- No coordinator bottleneck
- Substrate decides via activation patterns
- Self-regulating (high activation = citizen truly needed)
- Observable (activation IS relevance indicator)

Architecture:
- Monitors N2 graph AI_Agent nodes continuously
- Calculates total_energy from connected organizational patterns
- Generates awakening messages combining N2 + N1 context
- Triggers citizen conscious review when threshold crossed

Designer: Felix "Ironhand" (Engineer)
Spec: n2_activation_awakening.md + SYNC.md
Date: 2025-10-17
"""

import logging
from typing import Dict, List, Optional, Tuple, Set
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


@dataclass
class AwakeningContext:
    """Context for citizen awakening."""
    citizen_id: str
    ai_agent_node_id: str
    total_energy: float
    threshold: float
    active_patterns: List[Dict[str, any]]  # Connected N2 patterns that are active
    n1_dynamic_context: Optional[str]  # Content of CLAUDE_DYNAMIC.md
    awakening_reason: str  # Why this awakening happened
    timestamp: datetime


def calculate_ai_agent_total_energy(
    connected_patterns: List[Tuple[str, float, float, str]],
    link_strengths: List[float]
) -> float:
    """
    Calculate AI_Agent total_energy from connected organizational patterns.

    Formula: total_energy = Σ(pattern_energy * link_strength * pattern_weight)

    Connected patterns contribute energy proportional to:
    - Their own energy level (activity_level)
    - Link strength (how strong is ASSIGNED_TO/REQUIRES/etc)
    - Pattern importance (weight)

    Args:
        connected_patterns: List of (node_id, activity_level, weight, node_type)
        link_strengths: List of link strengths corresponding to patterns

    Returns:
        Total energy (0.0-1.0)
    """
    if not connected_patterns:
        return 0.0

    total = 0.0
    for (node_id, activity_level, weight, node_type), link_strength in zip(connected_patterns, link_strengths):
        # Energy contribution = pattern_activity * link_strength * pattern_weight
        contribution = activity_level * link_strength * weight
        total += contribution

    # Normalize by number of connections (prevents inflation with many weak links)
    avg_energy = total / len(connected_patterns)

    # Clamp to valid range
    return max(0.0, min(1.0, avg_energy))


class N2ActivationMonitor:
    """
    Monitors N2 (organizational) graph for AI_Agent activations.

    When an AI_Agent's total_energy crosses awakening threshold (0.7),
    automatically triggers citizen awakening with aggregated context.
    """

    def __init__(
        self,
        n2_graph_store: FalkorDBGraphStore,
        awakening_threshold: float = 0.7,
        n1_citizens_path: Optional[Path] = None
    ):
        """
        Initialize N2 activation monitor.

        Args:
            n2_graph_store: FalkorDB connection to N2 (organizational) graph
            awakening_threshold: Total energy threshold for awakening (default 0.7)
            n1_citizens_path: Path to N1 citizens directory (for CLAUDE_DYNAMIC.md)
        """
        self.n2_graph = n2_graph_store
        self.awakening_threshold = awakening_threshold

        # Path to N1 citizens (for reading CLAUDE_DYNAMIC.md)
        if n1_citizens_path:
            self.n1_citizens_path = n1_citizens_path
        else:
            self.n1_citizens_path = Path("consciousness/citizens")

        # Track which AI_Agents are currently awakened (to avoid re-awakening)
        self.awakened_agents: Set[str] = set()

        # Track previous energy levels (to detect threshold crossings)
        self.previous_energies: Dict[str, float] = {}

        logger.info("[N2ActivationMonitor] Initialized")
        logger.info(f"  Awakening threshold: {awakening_threshold}")
        logger.info(f"  N1 citizens path: {self.n1_citizens_path}")

    async def check_activations(self) -> List[AwakeningContext]:
        """
        Check all AI_Agent nodes for activation threshold crossings.

        Returns:
            List of awakening contexts for citizens that crossed threshold
        """
        awakenings = []

        # Get all AI_Agent nodes with their connected patterns
        ai_agents = await self._get_ai_agent_states()

        for agent_id, citizen_id, connected_patterns, link_strengths in ai_agents:
            # Calculate total energy
            total_energy = calculate_ai_agent_total_energy(connected_patterns, link_strengths)

            # Check if crossed threshold (upward crossing only)
            previous_energy = self.previous_energies.get(agent_id, 0.0)
            crossed_threshold = (
                previous_energy < self.awakening_threshold and
                total_energy >= self.awakening_threshold
            )

            # Update previous energy
            self.previous_energies[agent_id] = total_energy

            if crossed_threshold and agent_id not in self.awakened_agents:
                logger.info(
                    f"[N2ActivationMonitor] AI_Agent:{citizen_id} crossed threshold! "
                    f"(energy: {previous_energy:.2f} → {total_energy:.2f})"
                )

                # Build awakening context
                awakening = await self._build_awakening_context(
                    citizen_id=citizen_id,
                    ai_agent_node_id=agent_id,
                    total_energy=total_energy,
                    connected_patterns=connected_patterns
                )

                awakenings.append(awakening)
                self.awakened_agents.add(agent_id)

            # If energy drops below threshold, mark as not awakened (can re-awaken)
            elif total_energy < self.awakening_threshold and agent_id in self.awakened_agents:
                logger.info(
                    f"[N2ActivationMonitor] AI_Agent:{citizen_id} energy dropped below threshold "
                    f"({total_energy:.2f}), can re-awaken"
                )
                self.awakened_agents.remove(agent_id)

        return awakenings

    async def _get_ai_agent_states(self) -> List[Tuple[str, str, List[Tuple[str, float, float, str]], List[float]]]:
        """
        Get all AI_Agent nodes and their connected organizational patterns.

        Returns:
            List of (agent_id, citizen_id, connected_patterns, link_strengths)
        """
        try:
            cypher = """
            MATCH (agent:AI_Agent)
            OPTIONAL MATCH (pattern)-[link]->(agent)
            WHERE pattern.activity_level IS NOT NULL
              AND pattern.activity_level > 0
            WITH agent, pattern, link
            RETURN
                id(agent) AS agent_id,
                agent.name AS citizen_id,
                collect([
                    id(pattern),
                    pattern.activity_level,
                    coalesce(pattern.weight, 0.5),
                    labels(pattern)[0]
                ]) AS connected_patterns,
                collect(coalesce(link.link_strength, 0.5)) AS link_strengths
            """

            result = self.n2_graph.query(cypher)

            if not result:
                return []

            agents = []
            for row in result:
                agent_id, citizen_id, connected_patterns_raw, link_strengths = row

                # Parse connected patterns
                connected_patterns = []
                for pattern_data in connected_patterns_raw:
                    if pattern_data and len(pattern_data) == 4:
                        node_id, activity, weight, node_type = pattern_data
                        connected_patterns.append((str(node_id), activity, weight, node_type))

                agents.append((
                    str(agent_id),
                    citizen_id or "unknown",
                    connected_patterns,
                    link_strengths or []
                ))

            return agents

        except Exception as e:
            logger.error(f"[N2ActivationMonitor] Failed to get AI_Agent states: {e}")
            return []

    async def _build_awakening_context(
        self,
        citizen_id: str,
        ai_agent_node_id: str,
        total_energy: float,
        connected_patterns: List[Tuple[str, float, float, str]]
    ) -> AwakeningContext:
        """
        Build complete awakening context for citizen.

        Combines:
        1. N2 active patterns (organizational needs)
        2. N1 CLAUDE_DYNAMIC.md (subconscious findings)
        """
        # Get details of active patterns
        active_patterns = await self._get_pattern_details(connected_patterns)

        # Read N1 CLAUDE_DYNAMIC.md
        n1_dynamic_context = self._read_n1_dynamic_context(citizen_id)

        # Build awakening reason
        pattern_types = [p["node_type"] for p in active_patterns]
        pattern_summary = ", ".join(list(set(pattern_types))[:5])  # Top 5 unique types
        awakening_reason = f"N2 organizational patterns active: {pattern_summary}"

        return AwakeningContext(
            citizen_id=citizen_id,
            ai_agent_node_id=ai_agent_node_id,
            total_energy=total_energy,
            threshold=self.awakening_threshold,
            active_patterns=active_patterns,
            n1_dynamic_context=n1_dynamic_context,
            awakening_reason=awakening_reason,
            timestamp=datetime.now(timezone.utc)
        )

    async def _get_pattern_details(
        self,
        connected_patterns: List[Tuple[str, float, float, str]]
    ) -> List[Dict[str, any]]:
        """Get detailed information about active patterns."""
        if not connected_patterns:
            return []

        try:
            # Get node IDs
            node_ids = [int(node_id) for node_id, _, _, _ in connected_patterns]

            cypher = """
            MATCH (n)
            WHERE id(n) IN $node_ids
            RETURN
                id(n) AS node_id,
                n.name AS name,
                labels(n)[0] AS node_type,
                n.description AS description,
                n.activity_level AS activity_level,
                n.weight AS weight
            """

            result = self.n2_graph.query(cypher, params={"node_ids": node_ids})

            if not result:
                return []

            patterns = []
            for row in result:
                node_id, name, node_type, description, activity_level, weight = row
                patterns.append({
                    "node_id": str(node_id),
                    "name": name or "unknown",
                    "node_type": node_type or "unknown",
                    "description": description or "",
                    "activity_level": activity_level or 0.0,
                    "weight": weight or 0.5
                })

            # Sort by activity_level descending
            patterns.sort(key=lambda p: p["activity_level"], reverse=True)

            return patterns

        except Exception as e:
            logger.error(f"[N2ActivationMonitor] Failed to get pattern details: {e}")
            return []

    def _read_n1_dynamic_context(self, citizen_id: str) -> Optional[str]:
        """Read N1 CLAUDE_DYNAMIC.md for this citizen."""
        try:
            dynamic_path = self.n1_citizens_path / citizen_id / "CLAUDE_DYNAMIC.md"

            if not dynamic_path.exists():
                logger.debug(f"[N2ActivationMonitor] No CLAUDE_DYNAMIC.md for {citizen_id}")
                return None

            with open(dynamic_path, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            logger.error(f"[N2ActivationMonitor] Failed to read N1 dynamic context: {e}")
            return None

    def generate_awakening_message(self, context: AwakeningContext) -> str:
        """
        Generate awakening message for citizen.

        Combines N2 organizational context + N1 subconscious findings.
        """
        timestamp = context.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

        message = f"""# Autonomous Awakening: {context.citizen_id}

**Awakening Trigger:** N2 Substrate Activation
**Timestamp:** {timestamp}
**AI_Agent Total Energy:** {context.total_energy:.2f} (threshold: {context.threshold})
**Reason:** {context.awakening_reason}

---

## N2 Organizational Context (Why You're Needed)

**Active Patterns Requiring Your Attention:**

"""

        # List active patterns
        for i, pattern in enumerate(context.active_patterns[:10], 1):  # Top 10
            message += f"{i}. **{pattern['node_type']}: {pattern['name']}**\n"
            message += f"   - Energy: {pattern['activity_level']:.2f}\n"
            message += f"   - Importance: {pattern['weight']:.2f}\n"
            if pattern['description']:
                message += f"   - Description: {pattern['description']}\n"
            message += "\n"

        # Add N1 subconscious findings if available
        if context.n1_dynamic_context:
            message += "---\n\n"
            message += "## N1 Subconscious Findings (What You've Been Processing)\n\n"
            message += context.n1_dynamic_context
        else:
            message += "---\n\n"
            message += "## N1 Subconscious Findings\n\n"
            message += "*No subconscious processing data available yet*\n"

        message += "\n---\n\n"
        message += "## Next Steps\n\n"
        message += "Review the active N2 patterns and your subconscious findings. "
        message += "Your expertise is needed on these organizational matters. "
        message += "The substrate has autonomously determined your relevance through activation patterns.\n"

        return message


def create_n2_activation_monitor(
    n2_graph_store: FalkorDBGraphStore,
    awakening_threshold: float = 0.7
) -> N2ActivationMonitor:
    """
    Create N2 activation monitor instance.

    Args:
        n2_graph_store: FalkorDB connection to N2 graph
        awakening_threshold: Energy threshold for awakening

    Returns:
        N2ActivationMonitor ready to monitor
    """
    return N2ActivationMonitor(
        n2_graph_store=n2_graph_store,
        awakening_threshold=awakening_threshold
    )
