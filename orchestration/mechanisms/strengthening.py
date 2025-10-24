"""
Link Strengthening - Hebbian Learning for V2 Single-Energy

Mechanism: Links strengthen when energy flows through them during diffusion.
"Neurons that fire together, wire together" - frequently traversed paths become highways.

CRITICAL DECISION (D020): Strengthening only when BOTH nodes INACTIVE
- Active nodes (E >= theta): NO strengthening (normal dynamics)
- Inactive nodes being connected: YES strengthening (new pattern learning)
- Prevents runaway strengthening from repeated activation

Integration: Strengthening happens DURING diffusion stride execution, not separately.
Complexity: O(strides) - same as diffusion, negligible additional cost.

Author: Felix (Engineer)
Created: 2025-10-19
Updated: 2025-10-22 - V2 single-energy architecture, stride-based integration
Spec: docs/specs/v2/learning_and_trace/link_strengthening.md
"""

import logging
from typing import Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.node import Node
    from orchestration.core.link import Link

from orchestration.core.settings import settings
from orchestration.core.telemetry import emit_affective_memory
import numpy as np

logger = logging.getLogger(__name__)


# === Data Classes ===

@dataclass
class StrengtheningEvent:
    """
    Record of a single link strengthening event.

    Used for history tracking and analysis.
    """
    timestamp: datetime
    delta_weight: float        # Weight change this event (log space)
    new_weight: float          # log_weight after strengthening
    energy_flow: float         # Energy that triggered strengthening
    source_active: bool        # Was source active?
    target_active: bool        # Was target active?
    reason: str                # Strengthening reason: co_activation | causal | background
    tier_scale: float          # Tier multiplier (1.0 | 0.6 | 0.3)


@dataclass
class StrengtheningMetrics:
    """
    Metrics for link strengthening observability.

    Emitted as `link.strengthen` event per spec.
    """
    links_strengthened: int           # Total links strengthened this tick
    total_delta_weight: float         # Sum of all weight changes
    mean_delta_weight: float          # Average weight change
    max_delta_weight: float           # Largest single change
    inactive_pairs: int               # Links with both nodes inactive (D020)
    active_pairs_skipped: int         # Links skipped (both active)

    # Highway tracking
    new_highways: int                 # Links crossing threshold (0.7)
    highway_threshold: float = 0.7


class StrengtheningContext:
    """
    Context for link strengthening mechanism.

    Placeholder context class for consciousness engine integration.
    Currently unused as strengthening happens during stride execution,
    but kept for API compatibility with consciousness_engine_v2.py

    Author: Iris (fixing import error)
    Date: 2025-10-23
    """
    def __init__(self):
        pass


# === Learning Rate Controller ===

class LearningController:
    """
    Manages learning rate (how fast links strengthen).

    Learning rate can vary by:
    - Link weight (diminishing returns near max)
    - Link type (semantic vs causal)
    - Link age (older links harder to change)
    - Global settings

    Example:
        >>> controller = LearningController(base_rate=0.01)
        >>> rate = controller.get_learning_rate(link)
        >>> # Apply strengthening with adaptive rate
    """

    def __init__(self, base_rate: float = 0.01):
        """
        Initialize learning controller.

        Args:
            base_rate: Base learning rate (default 0.01)
        """
        self.base_rate = base_rate
        self.current_rate = base_rate

    def get_learning_rate(
        self,
        link: 'Link',
        diminishing_returns: bool = True
    ) -> float:
        """
        Get learning rate for specific link.

        Implements diminishing returns: harder to strengthen already-strong links.

        Args:
            link: Link to get rate for
            diminishing_returns: Apply diminishing returns curve

        Returns:
            Learning rate for this link

        Example:
            >>> # Weak link (log_weight=0.2)
            >>> rate = controller.get_learning_rate(weak_link)
            >>> rate  # Full base rate
            0.01
            >>>
            >>> # Strong link (log_weight=0.9)
            >>> rate = controller.get_learning_rate(strong_link)
            >>> rate  # Reduced rate (diminishing returns)
            0.005
        """
        rate = self.base_rate

        if diminishing_returns and link.log_weight > 0.0:
            # Diminishing returns: harder to strengthen already-strong links
            # log_weight > 0 means weight = exp(log_weight) > 1.0 (very strong)
            # As log_weight increases, learning slows
            if link.log_weight > 1.0:
                # Very strong links: 50% slower
                rate *= 0.5
            elif link.log_weight > 0.5:
                # Strong links: 25% slower
                rate *= 0.75

        return rate


# === Affective Coupling (PR-B) ===

def compute_affective_memory_multiplier(
    node: 'Node'
) -> float:
    """
    Compute affective memory amplification multiplier (PR-B: Emotion Couplings).

    High-emotion experiences form stronger memories.
    This implements bounded affect→weight amplification.

    Formula:
        m_affect = max(m_min, 1 + κ · tanh(||E_emo||))

    Where:
        - κ = AFFECTIVE_MEMORY_KAPPA (default 0.3, max 1.3x boost)
        - E_emo = emotion vector on node
        - m_min = AFFECTIVE_MEMORY_MIN (default 0.6, prevents over-dampening)
        - ||·|| = L2 norm (magnitude)

    Returns 1.0 when disabled or emotion missing (neutral multiplier).

    Bounded: m_affect ∈ [m_min, 1+κ] = [0.6, 1.3] by default

    Args:
        node: Node with potential emotion coloring

    Returns:
        Memory amplification multiplier m_affect

    Example:
        >>> # Node with strong emotion
        >>> node.emotion_vector = np.array([0.8, 0.6, 0.0])  # ||E_emo|| = 1.0
        >>> m = compute_affective_memory_multiplier(node)
        >>> # m = max(0.6, 1 + 0.3 * tanh(1.0)) = max(0.6, 1.23) = 1.23
        >>> # 23% memory boost
        >>>
        >>> # Node with no emotion
        >>> node.emotion_vector = None
        >>> m = compute_affective_memory_multiplier(node)
        >>> # m = 1.0 (neutral)
    """
    # Feature flag check
    if not settings.AFFECTIVE_MEMORY_ENABLED:
        return 1.0

    # Guard: need emotion vector
    node_emotion = getattr(node, 'emotion_vector', None)
    if node_emotion is None:
        return 1.0

    if len(node_emotion) == 0:
        return 1.0

    # Compute emotion magnitude
    E_magnitude = float(np.linalg.norm(node_emotion))

    # Guard: if zero emotion, no modulation
    if E_magnitude < 1e-6:
        return 1.0

    # Compute affective multiplier
    # m_affect = max(m_min, 1 + κ · tanh(||E_emo||))
    kappa = settings.AFFECTIVE_MEMORY_KAPPA
    m_min = settings.AFFECTIVE_MEMORY_MIN
    m_affect = max(m_min, 1.0 + kappa * np.tanh(E_magnitude))

    return float(m_affect)


# === Core Strengthening Function ===

def strengthen_link(
    link: 'Link',
    energy_flow: float,
    learning_controller: LearningController,
    track_history: bool = False,
    citizen_id: str = "",
    frame_id: Optional[str] = None,
    stride_utility: float = 0.0,
    source_was_active_pre: bool = False,
    target_was_active_pre: bool = False,
    target_crossed_threshold: bool = False
) -> Optional[StrengtheningEvent]:
    """
    Strengthen link proportional to energy flowing through it.

    3-TIER STRENGTHENING (Replaces D020):
    - STRONG (co_activation): Both nodes active → tier_scale = 1.0
    - MEDIUM (causal): Stride caused target flip → tier_scale = 0.6
    - WEAK (background): Neither active → tier_scale = 0.3

    This is Hebbian learning: "Neurons that fire together, wire together"

    Args:
        link: Link to strengthen
        energy_flow: Amount of energy transferred this stride
        learning_controller: Controller for adaptive learning rates
        track_history: Whether to record this event in history
        citizen_id: Citizen ID for telemetry
        frame_id: Frame ID for telemetry
        stride_utility: Z-score of stride value (filters noise, default 0.0 = neutral)
        source_was_active_pre: Source was active before this stride
        target_was_active_pre: Target was active before this stride
        target_crossed_threshold: This stride caused target to activate

    Returns:
        StrengtheningEvent if strengthening occurred, None if filtered

    Example:
        >>> controller = LearningController(base_rate=0.01)
        >>> event = strengthen_link(link, energy_flow=0.05, learning_controller=controller,
        ...                         stride_utility=1.5)  # Above average utility
        >>> if event:
        ...     print(f"Strengthened: Δw={event.delta_weight:.4f}, reason={event.reason}")
    """
    # Check current activation states (post-stride)
    source_active_post = link.source.is_active()  # E >= theta
    target_active_post = link.target.is_active()  # E >= theta

    # Determine strengthening tier (3-tier rule - PR-A)
    if source_active_post and target_active_post:
        # STRONG: Co-activation (both active same frame)
        # "Neurons that fire together wire together" - full strength
        tier_scale = 1.0
        reason = "co_activation"
    elif target_crossed_threshold and not target_was_active_pre:
        # MEDIUM: Causal credit (stride caused target to flip)
        # This stride specifically enabled activation
        tier_scale = 0.6
        reason = "causal"
    else:
        # WEAK: Background spillover (neither active or no flip)
        # Ambient diffusion, prevents noise learning
        tier_scale = 0.3
        reason = "background"

    # Guard: require minimum stride utility to filter noise (PR-A)
    # Below -1 sigma = noise, don't learn from it
    if stride_utility < -1.0:
        return None

    # Get adaptive learning rate
    learning_rate = learning_controller.get_learning_rate(link)

    # Compute affective memory multiplier (PR-B)
    # Apply to target node (where memory is being written)
    m_affect = compute_affective_memory_multiplier(link.target)

    # Compute weight delta with 3-tier scaling (PR-A)
    # delta = learning_rate × energy_flow × tier_scale × max(0, stride_utility) × m_affect
    delta_log_w_base = learning_rate * energy_flow * tier_scale

    # Apply stride utility scaling (only positive utility contributes)
    # This filters noise and rewards valuable flows
    utility_scale = max(0.1, stride_utility) if stride_utility > 0 else 0.1  # Minimum 10% even for neutral utility
    delta_log_w_utility = delta_log_w_base * utility_scale

    # Apply affective amplification
    delta_log_w_amplified = delta_log_w_utility * m_affect

    # Store old weight for event
    old_log_weight = link.log_weight

    # Apply strengthening (in log space)
    link.log_weight += delta_log_w_amplified

    # Clamp to reasonable maximum (prevents numerical overflow)
    # log_weight = 2.0 → weight = exp(2.0) ≈ 7.4 (very strong)
    link.log_weight = min(link.log_weight, settings.WEIGHT_CEILING)

    # Emit affective memory telemetry (PR-B)
    if settings.AFFECTIVE_MEMORY_ENABLED and m_affect != 1.0:
        target_emotion = getattr(link.target, 'emotion_vector', None)
        if target_emotion is not None:
            E_magnitude = float(np.linalg.norm(target_emotion))

            emit_affective_memory(
                citizen_id=citizen_id,
                frame_id=frame_id or "",
                node_id=link.target.id,
                m_affect=m_affect,
                emotion_magnitude=E_magnitude,
                delta_log_w_base=delta_log_w_base,
                delta_log_w_amplified=delta_log_w_amplified
            )

    # Create event
    event = StrengtheningEvent(
        timestamp=datetime.now(),
        delta_weight=delta_log_w_amplified,  # Use amplified delta
        new_weight=link.log_weight,
        energy_flow=energy_flow,
        source_active=source_active,
        target_active=target_active
    )

    # Track history if requested
    if track_history:
        if not hasattr(link, 'strengthening_history'):
            link.strengthening_history = []

        link.strengthening_history.append(event)

        # Prune history to prevent unbounded growth
        if len(link.strengthening_history) > settings.MAX_STRENGTHENING_HISTORY:
            link.strengthening_history = link.strengthening_history[-settings.MAX_STRENGTHENING_HISTORY:]

    return event


# === Integration with Diffusion ===

def strengthen_during_stride(
    link: 'Link',
    energy_flow: float,
    learning_controller: LearningController
) -> bool:
    """
    Strengthen link during stride execution (integrated with diffusion).

    This is called from execute_stride_step() for each energy transfer.

    Args:
        link: Link through which energy is flowing
        energy_flow: Amount of energy being transferred
        learning_controller: Learning rate controller

    Returns:
        True if strengthening occurred, False if skipped (both nodes active)

    Example:
        >>> # During diffusion stride:
        >>> energy_flow = E_src * ease * alpha * dt
        >>> strengthened = strengthen_during_stride(link, energy_flow, controller)
        >>> if strengthened:
        ...     print("Link learned from this transfer")
    """
    event = strengthen_link(
        link,
        energy_flow,
        learning_controller,
        track_history=False  # Don't track during normal operation (too expensive)
    )

    return event is not None


# === Analysis Functions ===

def identify_highway_paths(
    graph: 'Graph',
    min_weight: float = 0.0,  # V2: log_weight threshold
    min_path_length: int = 3
) -> List[List['Node']]:
    """
    Find paths with consistently high link weights ("highways").

    These are automatically traversed associations - thinking flows effortlessly.

    Args:
        graph: Consciousness graph
        min_weight: Minimum log_weight for highway links (default 0.0 = weight≈1.0)
        min_path_length: Minimum path length to qualify

    Returns:
        List of highway paths (each path is list of nodes)

    Example:
        >>> highways = identify_highway_paths(graph, min_weight=0.5)
        >>> for path in highways:
        ...     print(" → ".join(n.name for n in path))
        consciousness → substrate → falkordb
        energy → diffusion → learning
    """
    highways = []

    # Find chains of strong links
    for start_node in graph.nodes.values():
        # Only start from nodes with some energy
        if start_node.E < 0.1:
            continue

        path = [start_node]
        current = start_node

        # Follow strongest links
        while True:
            if not current.outgoing_links:
                break

            # Find strongest link
            strongest_link = max(
                current.outgoing_links,
                key=lambda l: l.log_weight
            )

            # Highway requires strong link
            if strongest_link.log_weight < min_weight:
                break

            # Avoid cycles
            if strongest_link.target in path:
                break

            path.append(strongest_link.target)
            current = strongest_link.target

            # Limit path length to prevent runaway
            if len(path) > 10:
                break

        # Only return paths above minimum length
        if len(path) >= min_path_length:
            highways.append(path)

    return highways


def analyze_link_symmetry(graph: 'Graph') -> Dict:
    """
    Measure how symmetric link weights are.

    High asymmetry = strong directional associations (A → B stronger than B → A).
    This is CORRECT behavior for causal/directional relationships.

    Args:
        graph: Consciousness graph

    Returns:
        Dict with symmetry statistics

    Example:
        >>> stats = analyze_link_symmetry(graph)
        >>> print(f"Mean asymmetry: {stats['mean_asymmetry']:.3f}")
        >>> for pair in stats['highly_asymmetric']:
        ...     print(f"{pair['forward'].source.name} → {pair['forward'].target.name}: ratio={pair['ratio']:.2f}")
    """
    asymmetries = []

    # Build reverse link index for fast lookup
    reverse_links = {}
    for link in graph.links.values():
        key = (link.target.id, link.source.id)
        reverse_links[key] = link

    # Analyze each link
    for link_ab in graph.links.values():
        # Find reverse link
        key = (link_ab.source.id, link_ab.target.id)
        link_ba = reverse_links.get(key)

        if link_ba:
            # Both directions exist
            asymmetry = abs(link_ab.log_weight - link_ba.log_weight)

            # Compute ratio (in linear space for interpretability)
            weight_ab = max(0.001, link_ab.log_weight)  # Avoid division by zero
            weight_ba = max(0.001, link_ba.log_weight)
            ratio = weight_ab / weight_ba if weight_ba > 0 else float('inf')

            asymmetries.append({
                'forward': link_ab,
                'backward': link_ba,
                'asymmetry': asymmetry,
                'ratio': ratio
            })

    if not asymmetries:
        return {
            'mean_asymmetry': 0.0,
            'median_asymmetry': 0.0,
            'highly_asymmetric': [],
            'count': 0
        }

    import numpy as np

    asymmetry_values = [a['asymmetry'] for a in asymmetries]

    return {
        'mean_asymmetry': np.mean(asymmetry_values),
        'median_asymmetry': np.median(asymmetry_values),
        'highly_asymmetric': [
            a for a in asymmetries
            if a['ratio'] > 3.0 or a['ratio'] < 0.33
        ],
        'count': len(asymmetries)
    }


def compute_strengthening_metrics(
    events: List[StrengtheningEvent],
    highway_threshold: float = 0.7
) -> StrengtheningMetrics:
    """
    Compute observability metrics from strengthening events.

    Args:
        events: List of strengthening events this tick
        highway_threshold: log_weight threshold for "highway" status

    Returns:
        StrengtheningMetrics for observability

    Example:
        >>> metrics = compute_strengthening_metrics(events)
        >>> print(f"Strengthened {metrics.links_strengthened} links")
        >>> print(f"New highways: {metrics.new_highways}")
    """
    if not events:
        return StrengtheningMetrics(
            links_strengthened=0,
            total_delta_weight=0.0,
            mean_delta_weight=0.0,
            max_delta_weight=0.0,
            inactive_pairs=0,
            active_pairs_skipped=0,
            new_highways=0,
            highway_threshold=highway_threshold
        )

    deltas = [e.delta_weight for e in events]
    total_delta = sum(deltas)
    mean_delta = total_delta / len(events)
    max_delta = max(deltas)

    # Count inactive pairs (D020 criterion)
    inactive_pairs = sum(
        1 for e in events
        if not e.source_active and not e.target_active
    )

    # Count new highways
    new_highways = sum(
        1 for e in events
        if e.new_weight >= highway_threshold and (e.new_weight - e.delta_weight) < highway_threshold
    )

    return StrengtheningMetrics(
        links_strengthened=len(events),
        total_delta_weight=total_delta,
        mean_delta_weight=mean_delta,
        max_delta_weight=max_delta,
        inactive_pairs=inactive_pairs,
        active_pairs_skipped=0,  # Not tracked in events list (they return None)
        new_highways=new_highways,
        highway_threshold=highway_threshold
    )


# === History Management ===

def prune_strengthening_history(link: 'Link', max_history: int = 100) -> int:
    """
    Prune strengthening history to prevent unbounded memory growth.

    Args:
        link: Link to prune history for
        max_history: Maximum history entries to keep

    Returns:
        Number of entries pruned

    Example:
        >>> pruned = prune_strengthening_history(link, max_history=100)
        >>> print(f"Pruned {pruned} old entries")
    """
    if not hasattr(link, 'strengthening_history'):
        return 0

    original_length = len(link.strengthening_history)

    if original_length > max_history:
        link.strengthening_history = link.strengthening_history[-max_history:]
        return original_length - max_history

    return 0


def prune_all_histories(graph: 'Graph', max_history: int = 100) -> int:
    """
    Prune strengthening histories for all links in graph.

    Args:
        graph: Consciousness graph
        max_history: Maximum history entries per link

    Returns:
        Total number of entries pruned

    Example:
        >>> total_pruned = prune_all_histories(graph, max_history=100)
        >>> print(f"Pruned {total_pruned} total entries across all links")
    """
    total_pruned = 0

    for link in graph.links.values():
        total_pruned += prune_strengthening_history(link, max_history)

    return total_pruned
