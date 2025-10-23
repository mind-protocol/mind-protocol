"""
Event schemas for Mind Protocol consciousness system.

These schemas define the contract between services (Python)
and clients (TypeScript/Next.js frontend).

All websocket events and API responses conform to these schemas.

Author: Ada (Architect)
Created: 2025-10-22
"""

from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass, asdict
from datetime import datetime


# === Event Types ===

EventType = Literal[
    # Frame events
    "frame_start",
    "frame_complete",
    "frame_error",

    # Node/Link events
    "node_activated",
    "node_created",
    "link_traversed",
    "link_created",

    # Subentity events
    "entity_activated",
    "entity_energy_update",
    "entity_threshold_crossed",

    # System events
    "system_status",
    "health_update",
    "error",

    # Visualization events
    "graph_update",
    "cluster_formed",

    # Affective coupling events (PR-A: Instrumentation)
    "affective_threshold",
    "affective_memory",
    "coherence_persistence",
    "multi_pattern_response",
    "identity_multiplicity",
    "consolidation",
    "decay_resistance",
    "stickiness",
    "affective_priming",
    "coherence_metric",
    "criticality_mode",
]


# === Base Event ===

@dataclass
class BaseEvent:
    """Base class for all events."""

    event_type: EventType
    citizen_id: str = ""
    timestamp: str = ""  # ISO 8601 format
    frame_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


# === Frame Events ===

@dataclass
class FrameStartEvent(BaseEvent):
    """Frame processing started."""

    event_type: Literal["frame_start"] = "frame_start"
    stimulus: str = ""
    entities_active: List[str] = None

    def __post_init__(self):
        if self.entities_active is None:
            self.entities_active = []


@dataclass
class FrameCompleteEvent(BaseEvent):
    """Frame processing completed."""

    event_type: Literal["frame_complete"] = "frame_complete"
    duration_ms: float = 0.0
    nodes_activated: int = 0
    links_traversed: int = 0
    response_generated: bool = False


# === Node/Link Events ===

@dataclass
class NodeActivatedEvent(BaseEvent):
    """Node reached activation threshold."""

    event_type: Literal["node_activated"] = "node_activated"
    node_id: str = ""
    node_name: str = ""
    energy: float = 0.0
    source: str = ""  # what activated it


@dataclass
class LinkTraversedEvent(BaseEvent):
    """Link was traversed during spreading activation."""

    event_type: Literal["link_traversed"] = "link_traversed"
    source_node: str = ""
    target_node: str = ""
    link_type: str = ""
    energy_transferred: float = 0.0


# === Subentity Events ===

@dataclass
class EntityActivatedEvent(BaseEvent):
    """Subentity crossed activation threshold."""

    event_type: Literal["entity_activated"] = "entity_activated"
    entity_name: str = ""
    energy: float = 0.0
    threshold: float = 0.0
    neighborhood_size: int = 0


@dataclass
class EntityEnergyUpdateEvent(BaseEvent):
    """Subentity energy level changed."""

    event_type: Literal["entity_energy_update"] = "entity_energy_update"
    entity_name: str = ""
    energy: float = 0.0
    delta: float = 0.0


# === System Events ===

@dataclass
class SystemStatusEvent(BaseEvent):
    """System health status."""

    event_type: Literal["system_status"] = "system_status"
    status: Literal["healthy", "degraded", "error"] = "healthy"
    services: Dict[str, str] = None  # service_name -> status
    metrics: Dict[str, Any] = None  # system metrics

    def __post_init__(self):
        if self.services is None:
            self.services = {}
        if self.metrics is None:
            self.metrics = {}


@dataclass
class ErrorEvent(BaseEvent):
    """Error occurred in system."""

    event_type: Literal["error"] = "error"
    error_message: str = ""
    error_type: str = ""
    service: str = ""
    recoverable: bool = True


# === Visualization Events ===

@dataclass
class GraphUpdateEvent(BaseEvent):
    """Graph structure updated."""

    event_type: Literal["graph_update"] = "graph_update"
    nodes_added: List[str] = None
    links_added: List[str] = None
    nodes_updated: List[str] = None

    def __post_init__(self):
        if self.nodes_added is None:
            self.nodes_added = []
        if self.links_added is None:
            self.links_added = []
        if self.nodes_updated is None:
            self.nodes_updated = []


# === Affective Coupling Events (PR-A: Instrumentation) ===

@dataclass
class AffectiveThresholdEvent(BaseEvent):
    """Affect-based threshold modulation (PR-B)."""

    event_type: Literal["affective_threshold"] = "affective_threshold"
    node_id: str = ""
    theta_base: float = 0.0  # Base threshold
    theta_adjusted: float = 0.0  # After affective modulation
    h: float = 0.0  # Threshold reduction amount
    affective_alignment: float = 0.0  # cos(A, E_emo)
    emotion_magnitude: float = 0.0  # ||E_emo||


@dataclass
class AffectiveMemoryEvent(BaseEvent):
    """Affect-based memory amplification (PR-B)."""

    event_type: Literal["affective_memory"] = "affective_memory"
    node_id: str = ""
    m_affect: float = 1.0  # Affective multiplier [m_min, 1+κ]
    emotion_magnitude: float = 0.0  # ||E_emo||
    delta_log_w_base: float = 0.0  # Base weight update
    delta_log_w_amplified: float = 0.0  # After amplification


@dataclass
class CoherencePersistenceEvent(BaseEvent):
    """Coherence state persistence tracking (PR-B)."""

    event_type: Literal["coherence_persistence"] = "coherence_persistence"
    entity_id: str = ""
    coherence_persistence: int = 0  # Consecutive frames
    lambda_res_effective: float = 0.0  # Effective resonance strength
    lock_in_risk: bool = False  # Approaching threshold P


@dataclass
class MultiPatternResponseEvent(BaseEvent):
    """Multi-pattern affective response (PR-C)."""

    event_type: Literal["multi_pattern_response"] = "multi_pattern_response"
    entity_id: str = ""
    pattern_scores: Dict[str, float] = None  # {reg, rum, dist} scores
    pattern_weights: Dict[str, float] = None  # {reg, rum, dist} softmax weights
    selected_pattern: str = ""  # Primary pattern
    m_reg: float = 0.0  # Regulation multiplier
    m_rum: float = 0.0  # Rumination multiplier
    m_dist: float = 0.0  # Distraction multiplier
    m_affect_unified: float = 1.0  # Final weighted multiplier
    rumination_frames_consecutive: int = 0
    rumination_cap_triggered: bool = False

    def __post_init__(self):
        if self.pattern_scores is None:
            self.pattern_scores = {}
        if self.pattern_weights is None:
            self.pattern_weights = {}


@dataclass
class IdentityMultiplicityEvent(BaseEvent):
    """Identity multiplicity assessment (PR-D)."""

    event_type: Literal["identity_multiplicity"] = "identity_multiplicity"
    num_active_identities: int = 0
    identities: List[str] = None
    task_progress_rate: float = 0.0
    energy_efficiency: float = 0.0
    identity_flip_count: int = 0
    coherence_score: float = 0.0
    mode: Literal["productive", "conflict", "monitoring"] = "monitoring"
    intervention: str = "none"  # Currently always "none" (phase 1)

    def __post_init__(self):
        if self.identities is None:
            self.identities = []


@dataclass
class ConsolidationEvent(BaseEvent):
    """Memory consolidation (PR-E)."""

    event_type: Literal["consolidation"] = "consolidation"
    nodes_consolidated: List[str] = None
    consolidation_factors: Dict[str, float] = None  # node_id -> c_total
    trigger_types: Dict[str, str] = None  # node_id -> trigger (retrieval/affect/goal)
    total_nodes: int = 0
    budget_used: int = 0

    def __post_init__(self):
        if self.nodes_consolidated is None:
            self.nodes_consolidated = []
        if self.consolidation_factors is None:
            self.consolidation_factors = {}
        if self.trigger_types is None:
            self.trigger_types = {}


@dataclass
class DecayResistanceEvent(BaseEvent):
    """Structural decay resistance (PR-E)."""

    event_type: Literal["decay_resistance"] = "decay_resistance"
    node_id: str = ""
    r_deg: float = 1.0  # Centrality resistance
    r_bridge: float = 1.0  # Cross-entity bridge resistance
    r_type: float = 1.0  # Type-based resistance
    r_total: float = 1.0  # Combined resistance factor


@dataclass
class StickinessEvent(BaseEvent):
    """Target-side energy retention (PR-E)."""

    event_type: Literal["stickiness"] = "stickiness"
    node_id: str = ""
    s_type: float = 0.6  # Type-based stickiness
    s_consolidation: float = 1.0  # Consolidation bonus
    s_centrality: float = 1.0  # Centrality bonus
    s_total: float = 0.6  # Combined stickiness factor
    retained_energy: float = 0.0  # How much energy retained


@dataclass
class AffectivePrimingEvent(BaseEvent):
    """Affect-congruent stimulus injection (PR-E)."""

    event_type: Literal["affective_priming"] = "affective_priming"
    primed_nodes: List[str] = None
    boost_factors: Dict[str, float] = None  # node_id -> boost (1.0 + p·r_affect)
    a_recent_magnitude: float = 0.0  # ||A_recent||
    total_boost: float = 0.0  # Total budget boost from priming

    def __post_init__(self):
        if self.primed_nodes is None:
            self.primed_nodes = []
        if self.boost_factors is None:
            self.boost_factors = {}


@dataclass
class CoherenceMetricEvent(BaseEvent):
    """System coherence quality metric (PR-E)."""

    event_type: Literal["coherence_metric"] = "coherence_metric"
    C: float = 0.0  # Overall coherence [0, 1]
    C_frontier: float = 0.0  # Frontier similarity
    C_stride: float = 0.0  # Stride relatedness
    smoothed_C: float = 0.0  # Rolling window smoothed value


@dataclass
class CriticalityModeEvent(BaseEvent):
    """Criticality mode classification (PR-E)."""

    event_type: Literal["criticality_mode"] = "criticality_mode"
    rho: float = 1.0  # Current spectral radius
    C: float = 0.0  # Current coherence
    mode: Literal["subcritical", "flow", "generative_overflow", "chaotic_racing", "mixed"] = "mixed"
    mode_duration_frames: int = 0  # How long in this mode
    controller_adjustment: float = 0.0  # What adjustment was made


# === Helper Functions ===

def create_event(
    event_type: EventType,
    citizen_id: str,
    frame_id: Optional[str] = None,
    **kwargs
) -> BaseEvent:
    """
    Factory function to create events.

    Args:
        event_type: Type of event to create
        citizen_id: Citizen generating the event
        frame_id: Current frame ID (if applicable)
        **kwargs: Event-specific fields

    Returns:
        Event instance
    """
    timestamp = datetime.utcnow().isoformat() + "Z"

    event_classes = {
        "frame_start": FrameStartEvent,
        "frame_complete": FrameCompleteEvent,
        "node_activated": NodeActivatedEvent,
        "link_traversed": LinkTraversedEvent,
        "entity_activated": EntityActivatedEvent,
        "entity_energy_update": EntityEnergyUpdateEvent,
        "system_status": SystemStatusEvent,
        "error": ErrorEvent,
        "graph_update": GraphUpdateEvent,
        # Affective coupling events
        "affective_threshold": AffectiveThresholdEvent,
        "affective_memory": AffectiveMemoryEvent,
        "coherence_persistence": CoherencePersistenceEvent,
        "multi_pattern_response": MultiPatternResponseEvent,
        "identity_multiplicity": IdentityMultiplicityEvent,
        "consolidation": ConsolidationEvent,
        "decay_resistance": DecayResistanceEvent,
        "stickiness": StickinessEvent,
        "affective_priming": AffectivePrimingEvent,
        "coherence_metric": CoherenceMetricEvent,
        "criticality_mode": CriticalityModeEvent,
    }

    event_class = event_classes.get(event_type, BaseEvent)

    return event_class(
        event_type=event_type,
        timestamp=timestamp,
        citizen_id=citizen_id,
        frame_id=frame_id,
        **kwargs
    )
