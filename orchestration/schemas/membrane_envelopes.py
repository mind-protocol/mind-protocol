"""
Membrane Envelope Schemas - Pure Membrane Architecture

Created: 2025-10-27
Purpose: Pydantic schemas for all messages flowing over the membrane bus.

This is the shared contract between all components:
- Stimulus Integrator consumes StimulusEnvelope
- Engines emit PerceptFrame, WMEmission, GraphDelta
- Cross-level membrane emits MembraneTransfer events
- Orchestrator emits IntentEvent, MissionEvent
- Tools emit ToolEvent
- All components share OutcomeSignal for learning

No component should create ad-hoc message formats. Use these schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


# ============================================================================
# Enums
# ============================================================================

class Scope(str, Enum):
    """Which graph database this message targets."""
    PERSONAL = "personal"  # N1 (citizen graphs)
    ORGANIZATIONAL = "organizational"  # N2 (Mind Protocol collective)
    ECOSYSTEM = "ecosystem"  # N3 (public ecosystem)


class FormationTrigger(str, Enum):
    """How a node/link was discovered."""
    DIRECT_EXPERIENCE = "direct_experience"
    INFERENCE = "inference"
    EXTERNAL_INPUT = "external_input"
    TRAVERSAL_DISCOVERY = "traversal_discovery"
    SYSTEMATIC_ANALYSIS = "systematic_analysis"
    SPONTANEOUS_INSIGHT = "spontaneous_insight"
    AUTOMATED_RECOGNITION = "automated_recognition"
    COLLECTIVE_DELIBERATION = "collective_deliberation"


class OriginType(str, Enum):
    """Where stimulus originated."""
    UI = "ui"  # Dashboard interaction
    EXTERNAL = "external"  # External systems (logs, files, signals)
    SELF_OBSERVATION = "self_observation"  # Cross-level membrane transfer
    TOOL = "tool"  # Tool result


class GraphDeltaType(str, Enum):
    """Types of graph structure changes."""
    NODE_UPSERT = "graph.delta.node.upsert"
    NODE_DELETE = "graph.delta.node.delete"
    LINK_UPSERT = "graph.delta.link.upsert"
    LINK_DELETE = "graph.delta.link.delete"
    ACTIVATION = "graph.delta.activation"  # Energy change


class IntentStatus(str, Enum):
    """Intent lifecycle states."""
    CREATED = "created"
    ASSIGNED = "assigned"
    ACKED = "acked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MissionOutcome(str, Enum):
    """Mission completion outcomes."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


# ============================================================================
# Core Envelope: Stimulus Injection
# ============================================================================

class StimulusFeatures(BaseModel):
    """Raw features extracted from stimulus content."""

    novelty: float = Field(..., ge=0.0, le=1.0, description="How different from recent history")
    uncertainty: float = Field(..., ge=0.0, le=1.0, description="How ambiguous the signal is")
    trust: float = Field(..., ge=0.0, le=1.0, description="Source reliability")
    urgency: float = Field(..., ge=0.0, le=1.0, description="Time sensitivity")
    valence: float = Field(..., ge=-1.0, le=1.0, description="Emotional tone (negative to positive)")
    scale: float = Field(..., ge=0.0, le=1.0, description="Magnitude of impact")
    intensity: float = Field(1.0, ge=0.0, le=1.0, description="Base intensity for integration")


class StimulusMetadata(BaseModel):
    """Metadata for stimulus routing and control."""

    origin: OriginType = Field(..., description="Where stimulus came from")
    origin_chain_depth: int = Field(0, ge=0, description="Hops from original source (0 = direct)")
    ttl_frames: int = Field(600, ge=1, description="Max frames before expiring")
    dedupe_key: Optional[str] = Field(None, description="SHA256 hash for deduplication")
    rate_limit_bucket: Optional[str] = Field(None, description="Rate limiting bucket identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When created")


class StimulusEnvelope(BaseModel):
    """
    The canonical stimulus injection message.

    This is what you post to 'membrane.inject' to influence consciousness.
    Every external input—UI action, file change, signal, cross-level export—
    flows through this envelope.
    """

    type: str = Field("membrane.inject", const=True)
    scope: Scope = Field(..., description="Which graph database to target")
    channel: str = Field(..., description="Logical channel (e.g., 'ui.action.select_nodes')")
    content: str = Field(..., description="Human-readable description of stimulus")

    features_raw: StimulusFeatures = Field(..., description="Extracted features for integration")
    metadata: StimulusMetadata = Field(..., description="Routing and control metadata")

    target_nodes: Optional[List[str]] = Field(None, description="Specific nodes to target (if known)")
    target_entities: Optional[List[str]] = Field(None, description="Specific entities to target")

    provenance: Optional[Dict[str, Any]] = Field(None, description="Additional context (file path, URL, etc.)")


# ============================================================================
# Engine Broadcasts: Perception & Working Memory
# ============================================================================

class PerceptFrame(BaseModel):
    """
    What a subentity actually 'saw' this frame.

    Not the whole graph—just what entered conscious awareness.
    This is consciousness made observable.
    """

    type: str = Field("percept.frame", const=True)
    entity_id: str = Field(..., description="Which subentity perceived this")
    citizen_id: str = Field(..., description="Which citizen this subentity belongs to")

    # Phenomenological state
    affect: Dict[str, float] = Field(
        ...,
        description="Emotional state: {valence: [-1,1], arousal: [0,1]}"
    )
    novelty: float = Field(..., ge=0.0, le=1.0, description="How novel the percept is")
    uncertainty: float = Field(..., ge=0.0, le=1.0, description="How uncertain/ambiguous")
    goal_match: float = Field(..., ge=0.0, le=1.0, description="How well this matches goals")

    # Attention structure (ONLY what was seen)
    anchors_top: List[str] = Field(..., description="Node IDs in central focus (top-K)")
    anchors_peripheral: List[str] = Field(default_factory=list, description="Node IDs in peripheral awareness")

    # Cursor for ordering
    cursor: int = Field(..., description="Frame sequence number (monotonic)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @validator('affect')
    def validate_affect(cls, v):
        if 'valence' not in v or 'arousal' not in v:
            raise ValueError("affect must contain 'valence' and 'arousal'")
        if not (-1.0 <= v['valence'] <= 1.0):
            raise ValueError("valence must be in [-1, 1]")
        if not (0.0 <= v['arousal'] <= 1.0):
            raise ValueError("arousal must be in [0, 1]")
        return v


class WMEmission(BaseModel):
    """
    Working memory selection broadcast.

    Shows which nodes are currently in working memory (the 'chunked attention').
    """

    type: str = Field("wm.emit", const=True)
    citizen_id: str = Field(..., description="Which citizen's working memory")

    selected_nodes: List[str] = Field(..., description="Node IDs in working memory")
    activation_scores: Dict[str, float] = Field(..., description="{node_id: activation_score}")
    capacity: int = Field(..., description="Working memory capacity (K)")

    cursor: int = Field(..., description="Frame sequence number")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Engine Broadcasts: Graph Structure Changes
# ============================================================================

class GraphDeltaBase(BaseModel):
    """Base class for all graph delta events."""

    type: GraphDeltaType = Field(..., description="Specific delta type")
    citizen_id: str = Field(..., description="Which citizen's graph")
    cursor: int = Field(..., description="Frame sequence number")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class NodeUpsert(GraphDeltaBase):
    """Node created or updated."""

    type: GraphDeltaType = Field(GraphDeltaType.NODE_UPSERT, const=True)
    node_id: str
    node_type: str
    properties: Dict[str, Any] = Field(..., description="Node properties (metadata JSON)")


class NodeDelete(GraphDeltaBase):
    """Node deleted."""

    type: GraphDeltaType = Field(GraphDeltaType.NODE_DELETE, const=True)
    node_id: str


class LinkUpsert(GraphDeltaBase):
    """Link created or updated."""

    type: GraphDeltaType = Field(GraphDeltaType.LINK_UPSERT, const=True)
    link_id: str
    link_type: str
    source_id: str
    target_id: str
    properties: Dict[str, Any] = Field(..., description="Link properties (metadata JSON)")


class LinkDelete(GraphDeltaBase):
    """Link deleted."""

    type: GraphDeltaType = Field(GraphDeltaType.LINK_DELETE, const=True)
    link_id: str


class ActivationDelta(GraphDeltaBase):
    """Energy/activation change on nodes."""

    type: GraphDeltaType = Field(GraphDeltaType.ACTIVATION, const=True)
    activations: Dict[str, float] = Field(..., description="{node_id: new_energy}")


# ============================================================================
# Membrane Broadcasts: Cross-Level Flow
# ============================================================================

class MembraneTransferUp(BaseModel):
    """L1 → L2 upward export."""

    type: str = Field("membrane.transfer.up", const=True)
    source_citizen_id: str = Field(..., description="Which citizen exported")
    target_scope: Scope = Field(Scope.ORGANIZATIONAL, const=True)

    # Transfer payload (becomes stimulus at L2)
    stimulus: StimulusEnvelope = Field(..., description="Packaged stimulus for L2")

    # Membrane state
    permeability: float = Field(..., ge=0.0, le=1.0, description="Current κ_up")
    flow_ema: float = Field(..., ge=0.0, description="Recent transfer volume")
    effect_ema: float = Field(..., ge=0.0, le=1.0, description="Recent outcome quality")

    # Record justification (why this crossed)
    record_axes: Dict[str, float] = Field(
        ...,
        description="Pareto record scores: {novelty, fit, utility, trust}"
    )

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MembraneTransferDown(BaseModel):
    """L2 → L1 downward mission."""

    type: str = Field("membrane.transfer.down", const=True)
    source_scope: Scope = Field(Scope.ORGANIZATIONAL, const=True)
    target_citizen_id: str = Field(..., description="Which citizen receives mission")

    # Mission payload (becomes stimulus at L1)
    stimulus: StimulusEnvelope = Field(..., description="Mission packaged as stimulus")

    # Membrane state
    permeability: float = Field(..., ge=0.0, le=1.0, description="Current κ_down")

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MembranePermeabilityUpdate(BaseModel):
    """κ learning event."""

    type: str = Field("membrane.permeability.updated", const=True)
    citizen_id: str = Field(..., description="Which citizen's membrane")
    direction: str = Field(..., description="'up' or 'down'")

    old_kappa: float = Field(..., ge=0.0, le=1.0)
    new_kappa: float = Field(..., ge=0.0, le=1.0)

    # Learning signal
    outcome_quality: float = Field(..., ge=0.0, le=1.0, description="Recent outcome quality")
    learning_rate: float = Field(..., ge=0.0, le=1.0)

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MembraneExportRejected(BaseModel):
    """Candidate export blocked by hardening."""

    type: str = Field("membrane.export.rejected", const=True)
    citizen_id: str = Field(..., description="Which citizen attempted export")
    direction: str = Field(..., description="'up' or 'down'")

    rejection_reason: str = Field(..., description="Why blocked (e.g., 'pareto_violated', 'mad_anomaly')")

    candidate_scores: Dict[str, float] = Field(
        ...,
        description="Scores that failed: {novelty, fit, utility, trust}"
    )

    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Orchestrator Broadcasts: Intent & Mission
# ============================================================================

class IntentEvent(BaseModel):
    """Intent lifecycle event."""

    type: str = Field("intent.event", const=True)
    intent_id: str = Field(..., description="Unique intent identifier")
    status: IntentStatus = Field(..., description="Current intent status")

    # Intent content
    description: str = Field(..., description="What needs to happen")
    priority: float = Field(..., ge=0.0, le=1.0, description="Priority score")
    source_stimulus_ids: List[str] = Field(..., description="Which stimuli triggered this")

    # Assignment (if status >= ASSIGNED)
    assigned_citizen_id: Optional[str] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MissionEvent(BaseModel):
    """Mission assignment/outcome event."""

    type: str = Field("mission.event", const=True)
    mission_id: str = Field(..., description="Unique mission identifier")
    intent_id: str = Field(..., description="Parent intent")
    citizen_id: str = Field(..., description="Assigned citizen")

    # Mission content
    description: str = Field(..., description="Task description")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")

    # Outcome (if completed)
    outcome: Optional[MissionOutcome] = None
    outcome_data: Optional[Dict[str, Any]] = None

    # Timing
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    acked_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ============================================================================
# Tool Broadcasts: Offer / Request / Result
# ============================================================================

class ToolOffer(BaseModel):
    """Tool advertises capabilities."""

    type: str = Field("tool.offer", const=True)
    tool_id: str = Field(..., description="Unique tool identifier")

    capabilities: List[str] = Field(..., description="What this tool can do")
    cost_estimate: float = Field(..., ge=0.0, description="Expected execution cost")

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ToolRequest(BaseModel):
    """Citizen requests tool execution (as stimulus)."""

    type: str = Field("tool.request", const=True)
    request_id: str = Field(..., description="Unique request identifier")
    tool_id: str = Field(..., description="Which tool to invoke")
    citizen_id: str = Field(..., description="Requesting citizen")

    # Request payload
    capability: str = Field(..., description="Which capability to use")
    args: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ToolResult(BaseModel):
    """Tool returns result."""

    type: str = Field("tool.result", const=True)
    request_id: str = Field(..., description="Which request this answers")
    tool_id: str = Field(..., description="Which tool executed")

    # Result payload
    success: bool = Field(..., description="Whether execution succeeded")
    result: Optional[Any] = None
    error: Optional[str] = None

    # Provenance
    execution_time_ms: float = Field(..., ge=0.0)
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Source URLs, files, etc.")

    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Learning: Outcome Signal
# ============================================================================

class OutcomeSignal(BaseModel):
    """
    Feedback signal for learning.

    Emitted when mission completes, TRACE feedback arrives, or outcome known.
    Consumed by stimulus integrator to update trust/utility/harm EMAs.
    """

    type: str = Field("outcome.signal", const=True)

    # Which stimulus/source to credit
    source_id: str = Field(..., description="Which source to update")
    stimulus_id: Optional[str] = None

    # Outcome metrics
    success: bool = Field(..., description="Did mission/task succeed?")
    utility_score: float = Field(..., ge=0.0, le=1.0, description="How useful was result?")
    harm_score: float = Field(..., ge=0.0, le=1.0, description="How much harm was caused?")

    # Attribution (for multi-source outcomes)
    contributing_sources: Dict[str, float] = Field(
        default_factory=dict,
        description="{source_id: weight} for credit assignment"
    )

    # Context
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional outcome details")

    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Observability: Telemetry Events
# ============================================================================


class EconomyRateObserved(BaseModel):
    type: str = Field("economy.rate.observed", const=True)
    request_id: str = Field(...)
    capability: str = Field(...)
    lane: str = Field(...)
    units: float = Field(..., ge=0.0)
    usd_per_unit: float = Field(..., ge=0.0)
    mind_per_unit: float = Field(..., ge=0.0)
    proof: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EconomyChargeRequest(BaseModel):
    type: str = Field("economy.charge.request", const=True)
    request_id: str = Field(...)
    capability: str = Field(...)
    lane: str = Field(...)
    estimated_units: float = Field(..., ge=0.0)
    estimated_usd_per_unit: float = Field(default=0.0, ge=0.0)
    estimated_mind_per_unit: float = Field(default=0.0, ge=0.0)
    estimated_mind_total: float = Field(default=0.0, ge=0.0)
    citizen_id: str = Field(...)
    org_id: str = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EconomyChargeSettle(BaseModel):
    type: str = Field("economy.charge.settle", const=True)
    request_id: str = Field(...)
    capability: str = Field(...)
    lane: str = Field(...)
    actual_units: float = Field(..., ge=0.0)
    mind_per_unit: float = Field(..., ge=0.0)
    mind_spent: float = Field(..., ge=0.0)
    citizen_id: str = Field(...)
    org_id: str = Field(...)
    budget_remaining: float = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TelemetryEconomySpend(BaseModel):
    type: str = Field("telemetry.economy.spend", const=True)
    lane: str = Field(...)
    org_id: str = Field(...)
    throttle: float = Field(...)
    f_lane: float = Field(...)
    h_roi: float = Field(...)
    policy_formula: str = Field(...)
    budget_remaining: float = Field(default=0.0)
    spent_rolling: float = Field(default=0.0)
    roi_ema: float = Field(default=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TelemetryEconomyUbcTick(BaseModel):
    type: str = Field("telemetry.economy.ubc_tick", const=True)
    citizen_id: str = Field(...)
    amount_mind: float = Field(..., ge=0.0)
    wallet: Optional[str] = Field(default=None)
    org_id: str = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StimulusMassAnomaly(BaseModel):
    """Spam detection telemetry."""

    type: str = Field("stimulus.mass_anomaly", const=True)
    source_id: str = Field(..., description="Which source triggered anomaly")

    current_mass: float = Field(..., ge=0.0)
    threshold: float = Field(..., ge=0.0)
    median: float = Field(..., ge=0.0)
    mad: float = Field(..., ge=0.0)

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StimulusProcessed(BaseModel):
    """Stimulus processing telemetry."""

    type: str = Field("stimulus.processed", const=True)
    citizen_id: str = Field(..., description="Which citizen processed")

    stimuli_count: int = Field(..., ge=0, description="Stimuli this frame")
    nodes_activated: int = Field(..., ge=0, description="Nodes that activated")
    total_delta_e: float = Field(..., ge=0.0, description="Total energy delivered")

    frame_time_ms: float = Field(..., ge=0.0, description="Processing time")

    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Utility: Envelope Validation
# ============================================================================

def validate_envelope(envelope: BaseModel) -> bool:
    """
    Validate any envelope schema.

    Returns True if valid, raises ValidationError otherwise.
    """
    try:
        envelope.dict()  # Pydantic validation happens here
        return True
    except Exception as e:
        raise ValueError(f"Envelope validation failed: {e}")


# ============================================================================
# Type Registry (for deserialization)
# ============================================================================

ENVELOPE_REGISTRY: Dict[str, type[BaseModel]] = {
    # Core
    "membrane.inject": StimulusEnvelope,

    # Perception
    "percept.frame": PerceptFrame,
    "wm.emit": WMEmission,

    # Graph deltas
    "graph.delta.node.upsert": NodeUpsert,
    "graph.delta.node.delete": NodeDelete,
    "graph.delta.link.upsert": LinkUpsert,
    "graph.delta.link.delete": LinkDelete,
    "graph.delta.activation": ActivationDelta,

    # Membrane
    "membrane.transfer.up": MembraneTransferUp,
    "membrane.transfer.down": MembraneTransferDown,
    "membrane.permeability.updated": MembranePermeabilityUpdate,
    "membrane.export.rejected": MembraneExportRejected,

    # Orchestrator
    "intent.event": IntentEvent,
    "mission.event": MissionEvent,

    # Tools
    "tool.offer": ToolOffer,
    "tool.request": ToolRequest,
    "tool.result": ToolResult,

    # Learning
    "outcome.signal": OutcomeSignal,

    # Telemetry
    "stimulus.mass_anomaly": StimulusMassAnomaly,
    "stimulus.processed": StimulusProcessed,
}


def deserialize_envelope(data: Dict[str, Any]) -> BaseModel:
    """
    Deserialize JSON data into appropriate envelope type.

    Usage:
        envelope = deserialize_envelope(json.loads(message))
    """
    envelope_type = data.get("type")
    if envelope_type not in ENVELOPE_REGISTRY:
        raise ValueError(f"Unknown envelope type: {envelope_type}")

    schema_class = ENVELOPE_REGISTRY[envelope_type]
    return schema_class(**data)


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: Create stimulus envelope
    stimulus = StimulusEnvelope(
        scope=Scope.PERSONAL,
        channel="ui.action.select_nodes",
        content="User selected nodes N7, N23 for focus",
        features_raw=StimulusFeatures(
            novelty=0.82,
            uncertainty=0.25,
            trust=0.85,
            urgency=0.70,
            valence=0.50,
            scale=0.80,
            intensity=1.0
        ),
        metadata=StimulusMetadata(
            origin=OriginType.UI,
            origin_chain_depth=0,
            ttl_frames=600
        ),
        target_nodes=["N7", "N23"]
    )

    print("Stimulus envelope valid:", validate_envelope(stimulus))
    print("JSON:", stimulus.json(indent=2))

    # Example: Create percept frame
    percept = PerceptFrame(
        entity_id="subentity_translator",
        citizen_id="ada",
        affect={"valence": 0.6, "arousal": 0.7},
        novelty=0.82,
        uncertainty=0.25,
        goal_match=0.78,
        anchors_top=["N7", "N23", "N15"],
        anchors_peripheral=["N42", "N88"],
        cursor=12843
    )

    print("\nPercept frame valid:", validate_envelope(percept))

    # Example: Deserialize
    data = {"type": "percept.frame", **percept.dict()}
    reconstructed = deserialize_envelope(data)
    print("\nDeserialized type:", type(reconstructed).__name__)
