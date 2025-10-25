"""
Entity Activation - Deriving subentity energy from single-node substrate.

ARCHITECTURAL PRINCIPLE: Single-energy per node, entity energy is DERIVED.

Formula (spec: subentity_layer.md §2.2):
    E_entity = Σ (m̃_iE × max(0, E_i - Θ_i))

Where:
    - E_i = node activation energy (node.E)
    - Θ_i = node threshold (node.theta)
    - m̃_iE = normalized membership weight from BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") link
    - Only above-threshold energy contributes (max(0, E_i - Θ_i))

This respects the V2 single-energy invariant: nodes hold ONE energy value,
subentities READ from that substrate rather than maintaining per-entity channels.

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/subentity_layer/subentity_layer.md
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass
from collections import deque
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.subentity import Subentity
    from orchestration.core.node import Node
    from orchestration.core.link import Link


# === Cohort-Based Threshold Tracking ===

class EntityCohortTracker:
    """
    Tracks cohort statistics for dynamic entity thresholds.

    Uses rolling window of "touched entities" (entities with energy > 0)
    to compute adaptive thresholds similar to node cohort logic.
    """

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.energy_history: deque = deque(maxlen=window_size)
        self.mean_energy: float = 1.0
        self.std_energy: float = 0.5

    def update(self, touched_entities: List[float]):
        """
        Update cohort statistics from entities touched this frame.

        Args:
            touched_entities: List of energy values for entities with E > 0
        """
        if not touched_entities:
            return

        # Add to rolling window
        for energy in touched_entities:
            self.energy_history.append(energy)

        # Recompute statistics
        if len(self.energy_history) > 10:  # Need minimum samples
            self.mean_energy = float(np.mean(self.energy_history))
            self.std_energy = float(np.std(self.energy_history))
            # Floor std to prevent collapse
            self.std_energy = max(self.std_energy, 0.1)

    def compute_threshold(self, z_score: float = 0.0) -> float:
        """
        Compute threshold from cohort statistics.

        Args:
            z_score: Standard deviations above mean (0 = mean)

        Returns:
            Threshold value
        """
        return self.mean_energy + z_score * self.std_energy


@dataclass
class EntityActivationMetrics:
    """
    Metrics from entity activation computation.

    Emitted as `subentity.activation` event per spec.
    """
    entity_id: str
    energy_before: float
    energy_after: float
    threshold: float
    member_count: int
    active_members: int  # Members with E_i >= Θ_i
    activation_level: str  # "dominant"|"strong"|"moderate"|"weak"|"absent"
    flipped: bool  # Crossed threshold this frame
    flip_direction: Optional[str] = None  # "activate"|"deactivate"|None


@dataclass
class LifecycleTransition:
    """
    Record of entity lifecycle state transition.

    Used for observability and debugging.
    """
    entity_id: str
    old_state: str  # "candidate"|"provisional"|"mature"
    new_state: str  # "candidate"|"provisional"|"mature"|"dissolved"
    quality_score: float
    trigger: str  # "promotion"|"demotion"|"dissolution"
    reason: str  # Human-readable explanation


def normalize_membership_weights(
    members: List[Tuple['Node', float]]
) -> Dict[str, float]:
    """
    Normalize BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") membership weights to sum to 1.0.

    Args:
        members: List of (node, raw_weight) tuples

    Returns:
        Dict of node_id -> normalized_weight

    Example:
        >>> members = [(node1, 0.8), (node2, 0.6), (node3, 0.4)]
        >>> weights = normalize_membership_weights(members)
        >>> # Returns {node1.id: 0.44, node2.id: 0.33, node3.id: 0.22}
    """
    if not members:
        return {}

    # Extract raw weights
    total_weight = sum(weight for _, weight in members)

    if total_weight < 1e-9:
        # All weights are zero - uniform distribution
        uniform_weight = 1.0 / len(members)
        return {node.id: uniform_weight for node, _ in members}

    # Normalize to sum to 1.0
    return {
        node.id: weight / total_weight
        for node, weight in members
    }


def compute_entity_activation(
    entity: 'Subentity',
    graph: 'Graph'
) -> float:
    """
    Compute subentity activation energy from member nodes (spec §2.2).

    Formula:
        E_entity = Σ (m̃_iE × max(0, E_i - Θ_i))

    Only above-threshold node energy contributes. This implements the
    "effective energy" principle: activation spreads only when nodes
    are themselves active.

    Args:
        entity: Subentity to compute activation for
        graph: Graph containing nodes and links

    Returns:
        Entity activation energy

    Example:
        >>> energy = compute_entity_activation(entity, graph)
        >>> # Returns weighted sum of member above-threshold energies
    """
    # Get members via BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") links
    from orchestration.core.types import LinkType

    members_with_weights = []
    for link in entity.incoming_links:
        if link.link_type != LinkType.MEMBER_OF:
            continue

        node = link.source
        membership_weight = link.weight  # BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF").weight ∈ [0,1]
        members_with_weights.append((node, membership_weight))

    if not members_with_weights:
        return 0.0  # No members = no energy

    # Normalize membership weights
    normalized_weights = normalize_membership_weights(members_with_weights)

    # Compute weighted sum of above-threshold energies
    entity_energy = 0.0
    for node, _ in members_with_weights:
        # Get node energy and threshold
        E_i = node.E  # Single-energy architecture
        Theta_i = node.theta

        # Above-threshold energy only
        effective_energy = max(0.0, E_i - Theta_i)

        # Weighted contribution
        m_tilde = normalized_weights[node.id]
        entity_energy += m_tilde * effective_energy

    return entity_energy


def compute_entity_threshold(
    entity: 'Subentity',
    graph: 'Graph',
    cohort_tracker: Optional[EntityCohortTracker] = None,
    global_threshold_mult: float = 1.0,
    use_hysteresis: bool = True
) -> float:
    """
    Compute dynamic threshold for subentity activation with cohort logic.

    Implements spec §2.3:
    - Cohort-based threshold from rolling statistics
    - Health modulation
    - Hysteresis for flip stability

    Algorithm:
        1. Compute base threshold from cohort statistics (mean + z*std)
        2. Modulate by entity health/quality
        3. Apply hysteresis if near previous threshold

    Args:
        entity: Subentity to compute threshold for
        graph: Graph containing nodes
        cohort_tracker: Optional cohort tracker for dynamic thresholds
        global_threshold_mult: Global threshold multiplier (from criticality)
        use_hysteresis: Whether to apply hysteresis near threshold

    Returns:
        Entity activation threshold
    """
    from orchestration.core.types import LinkType

    # Base threshold from cohort statistics
    if cohort_tracker and len(cohort_tracker.energy_history) > 10:
        # Use cohort-based threshold (z-score = 0 for mean)
        base_threshold = cohort_tracker.compute_threshold(z_score=0.0)
    else:
        # Fallback: weighted mean of member thresholds
        members_with_weights = []
        for link in entity.incoming_links:
            if link.link_type == LinkType.MEMBER_OF:
                members_with_weights.append((link.source, link.weight))

        if not members_with_weights:
            return 1.0  # Default threshold

        normalized_weights = normalize_membership_weights(members_with_weights)

        base_threshold = 0.0
        for node, _ in members_with_weights:
            m_tilde = normalized_weights[node.id]
            base_threshold += m_tilde * node.theta

    # Health modulation (spec §2.3)
    # Higher quality/coherence → lower threshold (easier to activate)
    health_factor = 1.0
    if hasattr(entity, 'quality_score') and entity.quality_score > 0:
        # Quality ∈ [0, 1], invert to get threshold reduction
        # quality=1.0 → 0.8× threshold, quality=0.5 → 0.9× threshold
        health_factor = 1.0 - (0.2 * entity.quality_score)

    threshold = base_threshold * health_factor

    # Hysteresis for flip stability (spec §2.3)
    # Prevents thrashing when energy oscillates near threshold
    if use_hysteresis and hasattr(entity, 'threshold_runtime'):
        prev_threshold = entity.threshold_runtime
        energy = entity.energy_runtime

        # Hysteresis band: ±5% of threshold
        hysteresis_band = 0.05 * prev_threshold

        # If energy is within band of previous threshold, use previous
        if abs(energy - prev_threshold) < hysteresis_band:
            threshold = prev_threshold

    # Apply global multiplier
    threshold *= global_threshold_mult

    return threshold


def get_activation_level(energy: float, threshold: float) -> str:
    """
    Compute activation level label from energy/threshold ratio.

    Levels (from spec):
        dominant: E > 3×Θ
        strong: E > 2×Θ
        moderate: E > 1×Θ
        weak: E > 0.5×Θ
        absent: E ≤ 0.5×Θ

    Args:
        energy: Entity energy
        threshold: Entity threshold

    Returns:
        Activation level string
    """
    if threshold < 1e-9:
        return "absent"

    ratio = energy / threshold

    if ratio > 3.0:
        return "dominant"
    elif ratio > 2.0:
        return "strong"
    elif ratio > 1.0:
        return "moderate"
    elif ratio > 0.5:
        return "weak"
    else:
        return "absent"


# === Lifecycle Management (Promotion/Dissolution) ===

def compute_entity_quality_score(entity: 'Subentity') -> float:
    """
    Compute entity quality score from 5 EMA signals (geometric mean).

    Quality signals (all in [0, 1]):
    1. ema_active - How often entity is active
    2. coherence_ema - How tight the cluster is
    3. ema_wm_presence - How often in working memory
    4. ema_trace_seats - How often reinforced by TRACE
    5. ema_formation_quality - How well-formed the entity is

    Returns:
        Quality score ∈ [0, 1] (geometric mean prevents compensatory averaging)

    Example:
        >>> entity.ema_active = 0.8
        >>> entity.coherence_ema = 0.7
        >>> entity.ema_wm_presence = 0.6
        >>> entity.ema_trace_seats = 0.5
        >>> entity.ema_formation_quality = 0.9
        >>> quality = compute_entity_quality_score(entity)
        >>> quality  # ~0.70 (geometric mean)
    """
    # Extract quality signals (with floor to prevent zero multiplication)
    signals = [
        max(0.01, entity.ema_active),
        max(0.01, entity.coherence_ema),
        max(0.01, entity.ema_wm_presence),
        max(0.01, entity.ema_trace_seats),
        max(0.01, entity.ema_formation_quality)
    ]

    # Geometric mean (prevents compensatory averaging - one bad signal drags down quality)
    quality = np.prod(signals) ** (1.0 / len(signals))

    return float(np.clip(quality, 0.0, 1.0))


def update_entity_lifecycle(
    entity: 'Subentity',
    quality_score: float,
    promotion_threshold: float = 0.6,
    dissolution_threshold: float = 0.2,
    promotion_streak_required: int = 10,
    dissolution_streak_required: int = 20
) -> Optional[LifecycleTransition]:
    """
    Update entity lifecycle state based on quality score.

    Lifecycle progression:
    - candidate → provisional: Sustained quality above promotion_threshold
    - provisional → mature: High quality for longer period
    - any → dissolved: Sustained quality below dissolution_threshold

    Args:
        entity: Subentity to update
        quality_score: Current quality score (0-1)
        promotion_threshold: Minimum quality for promotion (default 0.6)
        dissolution_threshold: Maximum quality for dissolution (default 0.2)
        promotion_streak_required: Frames needed for promotion (default 10)
        dissolution_streak_required: Frames needed for dissolution (default 20)

    Returns:
        LifecycleTransition if state changed, None otherwise

    Example:
        >>> transition = update_entity_lifecycle(entity, quality_score=0.75)
        >>> if transition:
        ...     print(f"{transition.entity_id}: {transition.old_state} → {transition.new_state}")
    """
    old_state = entity.stability_state

    # Update quality tracking
    entity.quality_score = quality_score
    entity.frames_since_creation += 1

    if quality_score >= promotion_threshold:
        entity.high_quality_streak += 1
        entity.low_quality_streak = 0
    elif quality_score <= dissolution_threshold:
        entity.low_quality_streak += 1
        entity.high_quality_streak = 0
    else:
        # Middle quality - reset both streaks
        entity.high_quality_streak = 0
        entity.low_quality_streak = 0

    # Check for dissolution (any state can dissolve)
    # LAYER 3 GUARD: Require substantial age before dissolution to prevent freshly loaded entities
    # from dissolving before their EMAs stabilize (all EMAs start at 0.0 → quality_score ~0.01)
    # 1000 frames = ~100 seconds at 100ms/tick - gives EMAs proper warm-up time
    minimum_age_for_dissolution = 1000  # frames (~100 seconds at 100ms/tick)

    if (entity.low_quality_streak >= dissolution_streak_required and
        entity.frames_since_creation >= minimum_age_for_dissolution):
        return LifecycleTransition(
            entity_id=entity.id,
            old_state=old_state,
            new_state="dissolved",
            quality_score=quality_score,
            trigger="dissolution",
            reason=f"Quality below {dissolution_threshold} for {entity.low_quality_streak} frames"
        )

    # Check for promotion
    new_state = old_state

    if entity.stability_state == "candidate":
        # candidate → provisional: Sustained high quality
        if entity.high_quality_streak >= promotion_streak_required:
            new_state = "provisional"

    elif entity.stability_state == "provisional":
        # provisional → mature: High quality + age requirement
        mature_age_required = 100  # frames
        if (entity.high_quality_streak >= promotion_streak_required * 2 and
            entity.frames_since_creation >= mature_age_required):
            new_state = "mature"

    # Apply state change if promotion occurred
    if new_state != old_state:
        entity.stability_state = new_state
        return LifecycleTransition(
            entity_id=entity.id,
            old_state=old_state,
            new_state=new_state,
            quality_score=quality_score,
            trigger="promotion",
            reason=f"Quality {quality_score:.2f} sustained for {entity.high_quality_streak} frames"
        )

    return None


def dissolve_entity(
    graph: 'Graph',
    entity: 'Subentity'
) -> None:
    """
    Dissolve entity and release its members.

    This removes the entity from the graph and deletes all BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") links
    to its members. Members return to the atomic node pool.

    Args:
        graph: Graph containing the entity
        entity: Entity to dissolve

    Side effects:
        - Removes entity from graph.subentities
        - Deletes all BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") links to this entity
        - Members become free-floating nodes

    Example:
        >>> dissolve_entity(graph, low_quality_entity)
        >>> # Entity removed, members available for other entities
    """
    from orchestration.core.types import LinkType

    # Remove all BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") links (release members)
    belongs_to_links = [
        link for link in entity.incoming_links
        if link.link_type == LinkType.MEMBER_OF
    ]

    for link in belongs_to_links:
        # Remove from source node's outgoing links
        if link in link.source.outgoing_links:
            link.source.outgoing_links.remove(link)

        # Remove from entity's incoming links
        if link in entity.incoming_links:
            entity.incoming_links.remove(link)

        # Remove from graph's links dict
        if link.id in graph.links:
            del graph.links[link.id]

    # Remove entity from graph
    if entity.id in graph.subentities:
        del graph.subentities[entity.id]


def update_entity_activations(
    graph: 'Graph',
    global_threshold_mult: float = 1.0,
    cohort_tracker: Optional[EntityCohortTracker] = None,
    enable_lifecycle: bool = True
) -> Tuple[List[EntityActivationMetrics], List[LifecycleTransition]]:
    """
    Update activation state for all subentities in graph.

    This is the main entry point called each frame to:
    1. Compute E_entity from member nodes
    2. Compute Θ_entity dynamically (with cohort-based thresholding)
    3. Update entity.energy_runtime and entity.threshold_runtime
    4. Detect flips (threshold crossings)
    5. Update activation_level_runtime
    6. Update cohort statistics for next frame
    7. Update lifecycle state (promotion/dissolution)

    Args:
        graph: Graph with subentities, nodes, and links
        global_threshold_mult: Global threshold multiplier (from criticality)
        cohort_tracker: Optional cohort tracker for dynamic thresholds
        enable_lifecycle: Whether to run lifecycle management (default True)

    Returns:
        Tuple of (activation_metrics, lifecycle_transitions)

    Example:
        >>> tracker = EntityCohortTracker()
        >>> metrics, transitions = update_entity_activations(
        ...     graph, global_threshold_mult=1.0, cohort_tracker=tracker
        ... )
        >>> for m in metrics:
        ...     if m.flipped:
        ...         print(f"{m.entity_id} flipped {m.flip_direction}")
        >>> for t in transitions:
        ...     print(f"{t.entity_id}: {t.old_state} → {t.new_state}")
    """
    if not hasattr(graph, 'subentities'):
        return ([], [])  # No subentities in graph

    metrics_list = []
    lifecycle_transitions = []
    touched_entities = []  # Track energies for cohort update
    entities_to_dissolve = []  # Track entities marked for dissolution

    for entity in graph.subentities.values():
        # Save previous energy for flip detection
        energy_before = entity.energy_runtime
        threshold_before = entity.threshold_runtime

        # Compute new energy and threshold (with advanced thresholding)
        energy_after = compute_entity_activation(entity, graph)
        threshold_after = compute_entity_threshold(
            entity,
            graph,
            cohort_tracker=cohort_tracker,
            global_threshold_mult=global_threshold_mult,
            use_hysteresis=True
        )

        # Track touched entities (energy > 0) for cohort update
        if energy_after > 0:
            touched_entities.append(energy_after)

        # Update runtime state
        entity.energy_runtime = energy_after
        entity.threshold_runtime = threshold_after

        # Update activation level
        entity.activation_level_runtime = get_activation_level(energy_after, threshold_after)

        # Update lifecycle state (promotion/dissolution)
        if enable_lifecycle:
            # LAYER 1 GUARD: Functional entities are permanent infrastructure, never dissolve
            # They provide scaffolding for attention/WM, not emergent hypotheses
            if entity.entity_kind == "functional":
                # Update quality score for telemetry, but skip lifecycle transitions
                quality_score = compute_entity_quality_score(entity)
                entity.quality_score = quality_score
            else:
                # Semantic/emergent entities follow normal lifecycle
                quality_score = compute_entity_quality_score(entity)
                transition = update_entity_lifecycle(entity, quality_score)

                if transition:
                    lifecycle_transitions.append(transition)

                    # Mark for dissolution if state is "dissolved"
                    if transition.new_state == "dissolved":
                        logger.warning(f"[Lifecycle] Marking entity for dissolution: {entity.id} "
                                      f"(quality={quality_score:.3f}, low_streak={entity.low_quality_streak}, "
                                      f"frames={entity.frames_since_creation})")
                        entities_to_dissolve.append(entity)

        # Detect flip
        was_active = energy_before >= threshold_before
        is_active = energy_after >= threshold_after
        flipped = was_active != is_active

        flip_direction = None
        if flipped:
            flip_direction = "activate" if is_active else "deactivate"

        # Count members
        from orchestration.core.types import LinkType
        members = [link.source for link in entity.incoming_links
                   if link.link_type == LinkType.MEMBER_OF]

        member_count = len(members)
        active_members = sum(1 for node in members if node.E >= node.theta)

        # Create metrics
        metrics = EntityActivationMetrics(
            entity_id=entity.id,
            energy_before=energy_before,
            energy_after=energy_after,
            threshold=threshold_after,
            member_count=member_count,
            active_members=active_members,
            activation_level=entity.activation_level_runtime,
            flipped=flipped,
            flip_direction=flip_direction
        )

        metrics_list.append(metrics)

    # Update cohort tracker with touched entities this frame
    if cohort_tracker and touched_entities:
        cohort_tracker.update(touched_entities)

    # Dissolve entities marked for removal
    for entity in entities_to_dissolve:
        logger.warning(f"[Lifecycle] DISSOLVING entity: {entity.id} (role={entity.role_or_topic}, "
                      f"quality={entity.quality_score:.3f}, frames_since_creation={entity.frames_since_creation}, "
                      f"low_quality_streak={entity.low_quality_streak}, state={entity.stability_state})")
        dissolve_entity(graph, entity)

    return (metrics_list, lifecycle_transitions)


# === RELATES_TO Learning from Boundary Strides ===

def learn_relates_to_from_boundary_stride(
    source_entity: 'Subentity',
    target_entity: 'Subentity',
    energy_flow: float,
    graph: 'Graph',
    learning_rate: float = 0.05
) -> None:
    """
    Learn or update RELATES_TO link from boundary stride (spec §2.5).

    When energy flows from a node in source_entity to a node in target_entity,
    this creates/strengthens a RELATES_TO link capturing:
    - Boundary ease (log_weight): How easily energy flows between entities
    - Dominance prior: Which entity tends to activate which
    - Semantic distance: Embedding distance between centroids
    - Count: How many boundary strides occurred

    Args:
        source_entity: Entity energy is flowing from
        target_entity: Entity energy is flowing to
        energy_flow: Amount of energy transferred
        graph: Graph containing entities and links
        learning_rate: Hebbian learning rate (default 0.05)

    Side effects:
        Creates or updates RELATES_TO link in graph

    Example:
        >>> # During stride: node in entity_A → node in entity_B
        >>> learn_relates_to_from_boundary_stride(entity_A, entity_B, energy_flow=0.05, graph)
        >>> # Creates/strengthens RELATES_TO(entity_A → entity_B)
    """
    from orchestration.core.types import LinkType
    from orchestration.core.link import Link
    import numpy as np

    # Find existing RELATES_TO link
    existing_link = None
    for link in source_entity.outgoing_links:
        if (link.link_type == LinkType.RELATES_TO and
            link.target.id == target_entity.id):
            existing_link = link
            break

    if existing_link:
        # Update existing link
        # Strengthen based on energy flow (Hebbian learning)
        delta_weight = learning_rate * energy_flow

        existing_link.log_weight += delta_weight

        # Clamp to reasonable range
        from orchestration.core.settings import settings
        existing_link.log_weight = min(existing_link.log_weight, settings.WEIGHT_CEILING)

        # Update count
        if not hasattr(existing_link, 'boundary_stride_count'):
            existing_link.boundary_stride_count = 0
        existing_link.boundary_stride_count += 1

        # Update semantic distance (if embeddings exist)
        if (source_entity.centroid_embedding is not None and
            target_entity.centroid_embedding is not None):
            norm_source = np.linalg.norm(source_entity.centroid_embedding)
            norm_target = np.linalg.norm(target_entity.centroid_embedding)

            if norm_source > 1e-9 and norm_target > 1e-9:
                cos_sim = np.dot(source_entity.centroid_embedding, target_entity.centroid_embedding) / (norm_source * norm_target)
                semantic_distance = 1.0 - cos_sim  # Distance = 1 - similarity

                # EMA update
                if not hasattr(existing_link, 'semantic_distance'):
                    existing_link.semantic_distance = semantic_distance
                else:
                    existing_link.semantic_distance = 0.1 * semantic_distance + 0.9 * existing_link.semantic_distance

    else:
        # Create new RELATES_TO link
        link_id = f"relates_{source_entity.id}_to_{target_entity.id}"

        # Compute initial semantic distance
        semantic_distance = 0.5  # Default
        if (source_entity.centroid_embedding is not None and
            target_entity.centroid_embedding is not None):
            norm_source = np.linalg.norm(source_entity.centroid_embedding)
            norm_target = np.linalg.norm(target_entity.centroid_embedding)

            if norm_source > 1e-9 and norm_target > 1e-9:
                cos_sim = np.dot(source_entity.centroid_embedding, target_entity.centroid_embedding) / (norm_source * norm_target)
                semantic_distance = 1.0 - cos_sim

        from datetime import datetime

        new_link = Link(
            id=link_id,
            link_type=LinkType.RELATES_TO,
            source=source_entity,
            target=target_entity,
            goal="Entity boundary relationship learned from energy flow",
            mindstate="Boundary stride detection",
            energy=energy_flow,
            confidence=0.5,  # Initial confidence
            formation_trigger="traversal_discovery",
            created_by="consciousness_engine_v2",
            substrate="organizational"
        )

        # Set initial log_weight from energy flow
        new_link.log_weight = learning_rate * energy_flow

        # Add custom attributes
        new_link.boundary_stride_count = 1
        new_link.semantic_distance = semantic_distance

        # Add link to graph
        graph.links[link_id] = new_link
        source_entity.outgoing_links.append(new_link)
        target_entity.incoming_links.append(new_link)


# === Identity Multiplicity Tracking (PR-D) ===

def track_task_progress(
    entity: 'Subentity',
    goals_achieved: int,
    frames_elapsed: int
) -> None:
    """
    Track task progress rate for identity multiplicity detection.

    Computes progress rate as goals_achieved / frames_elapsed, then updates
    entity.task_progress_rate using EMA (α = 0.1 for smoothing).

    Args:
        entity: Subentity to track
        goals_achieved: Number of goals/tasks completed in window
        frames_elapsed: Number of frames in measurement window

    Side effects:
        Updates entity.task_progress_rate
    """
    from orchestration.core.settings import settings

    if not settings.IDENTITY_MULTIPLICITY_ENABLED:
        return

    if frames_elapsed == 0:
        return

    # Compute instantaneous progress rate
    progress_rate = goals_achieved / frames_elapsed

    # Update with EMA (α = 0.1 for smoothing)
    alpha = 0.1
    entity.task_progress_rate = (
        alpha * progress_rate +
        (1.0 - alpha) * entity.task_progress_rate
    )


def track_energy_efficiency(
    entity: 'Subentity',
    work_output: float,
    total_energy_spent: float
) -> None:
    """
    Track energy efficiency for identity multiplicity detection.

    Computes efficiency as work_output / total_energy_spent, then updates
    entity.energy_efficiency using EMA (α = 0.1 for smoothing).

    Work output could be:
    - Number of nodes activated
    - Number of formations created
    - WM seats claimed
    - Any measurable productive outcome

    Args:
        entity: Subentity to track
        work_output: Productive output measure (higher = more work done)
        total_energy_spent: Total energy consumed by entity members

    Side effects:
        Updates entity.energy_efficiency
    """
    from orchestration.core.settings import settings

    if not settings.IDENTITY_MULTIPLICITY_ENABLED:
        return

    if total_energy_spent <= 1e-9:
        return  # Avoid division by zero

    # Compute instantaneous efficiency
    efficiency = work_output / total_energy_spent

    # Clamp to [0, 1] for numerical stability
    efficiency = np.clip(efficiency, 0.0, 1.0)

    # Update with EMA (α = 0.1 for smoothing)
    alpha = 0.1
    entity.energy_efficiency = (
        alpha * efficiency +
        (1.0 - alpha) * entity.energy_efficiency
    )


def track_identity_flips(
    entity: 'Subentity',
    current_dominant_identity: Optional[str],
    graph: 'Graph'
) -> None:
    """
    Track identity flip count for multiplicity detection.

    Detects when the dominant identity changes and increments flip counter.
    Uses rolling window decay to forget old flips.

    Args:
        entity: Subentity to track
        current_dominant_identity: ID of currently dominant identity (most active entity)
        graph: Graph (for accessing previous state if stored)

    Side effects:
        Updates entity.identity_flip_count
        Stores previous_dominant_identity in entity.properties
    """
    from orchestration.core.settings import settings

    if not settings.IDENTITY_MULTIPLICITY_ENABLED:
        return

    if current_dominant_identity is None:
        return

    # Retrieve previous dominant identity from properties
    previous_dominant = entity.properties.get('previous_dominant_identity')

    # Detect flip
    flipped_this_frame = False
    if previous_dominant is not None and previous_dominant != current_dominant_identity:
        # Flip detected - increment counter
        entity.identity_flip_count += 1
        flipped_this_frame = True

    # Store current as previous for next frame
    entity.properties['previous_dominant_identity'] = current_dominant_identity

    # Apply rolling window decay (forget old flips gradually)
    # Only decay on frames where NO flip occurred (to avoid immediate decay of current flip)
    if not flipped_this_frame and entity.identity_flip_count > 0:
        decay_rate = 1.0 - (1.0 / settings.MULTIPLICITY_WINDOW_FRAMES)
        entity.identity_flip_count = int(entity.identity_flip_count * decay_rate)


def assess_multiplicity_mode(entity: 'Subentity', num_active_identities: int) -> str:
    """
    Assess identity multiplicity mode (productive vs conflict vs monitoring).

    Logic:
    - If single identity active: "monitoring" (no multiplicity)
    - If multiple identities active:
        - If outcomes poor (low progress, low efficiency, high flips): "conflict"
        - Otherwise: "productive"

    Args:
        entity: Subentity to assess
        num_active_identities: Number of currently active identities

    Returns:
        Mode: "productive" | "conflict" | "monitoring"
    """
    from orchestration.core.settings import settings

    if not settings.IDENTITY_MULTIPLICITY_ENABLED:
        return "monitoring"

    # Single identity = no multiplicity, just monitoring
    if num_active_identities < 2:
        return "monitoring"

    # Multiple identities active - assess outcomes
    if (entity.task_progress_rate < settings.PROGRESS_THRESHOLD and
        entity.energy_efficiency < settings.EFFICIENCY_THRESHOLD and
        entity.identity_flip_count > settings.FLIP_THRESHOLD):
        # Poor outcomes - conflict state
        return "conflict"
    else:
        # Good outcomes despite multiplicity - productive state
        return "productive"
