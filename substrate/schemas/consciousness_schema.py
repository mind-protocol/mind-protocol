"""
Consciousness Graph Schema - V2

This module defines the complete type system for Mind Protocol V2 consciousness graphs.
It preserves all V1 consciousness richness while adding bitemporal tracking and
native vector support.

Architecture:
- BaseNode: Foundation for all 29 node types
- BaseRelation: Foundation for all 23 relation types
- Bitemporal fields: Track both fact validity and knowledge acquisition
- Consciousness metadata: Goal, mindstate, confidence on every relation
- Energy-only model: energy + weight (no energy)

Designer: Ada "Bridgekeeper" (Architect)
Phase: 1 - Foundation & Schema
Updated: Energy-Only Model implemented by Felix "Ironhand" - 2025-10-17
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


# ==============================================================================
# ENUMS - Consciousness Metadata Types
# ==============================================================================

class FormationTrigger(str, Enum):
    """How a node or relation came into existence"""
    DIRECT_EXPERIENCE = "direct_experience"
    INFERENCE = "inference"
    EXTERNAL_INPUT = "external_input"
    TRAVERSAL_DISCOVERY = "traversal_discovery"
    SYSTEMATIC_ANALYSIS = "systematic_analysis"
    SPONTANEOUS_INSIGHT = "spontaneous_insight"
    AUTOMATED_RECOGNITION = "automated_recognition"
    COLLECTIVE_DELIBERATION = "collective_deliberation"


class ValidationStatus(str, Enum):
    """Epistemic confidence evolution"""
    THEORETICAL = "theoretical"
    EXPERIENTIAL = "experiential"
    TESTED = "tested"
    PROVEN = "proven"


class Substrate(str, Enum):
    """Type of consciousness substrate"""
    HUMAN = "human"
    AI = "ai"
    ORGANIZATIONAL = "organizational"


# ==============================================================================
# BASE CLASSES
# ==============================================================================

class BaseNode(BaseModel):
    """
    Base class for all consciousness graph nodes.

    Includes:
    - Core idsubentity (name, description)
    - Bitemporal tracking (when valid, when known)
    - Consciousness context (how and why this node exists)
    """

    # Core Idsubentity
    name: str = Field(description="Unique identifier for this node")
    description: str = Field(description="Human-readable description of what this node represents")

    # Bitemporal Fields (Phase 2 design, included Phase 1)
    valid_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this fact became true in reality (fact time)"
    )
    invalid_at: Optional[datetime] = Field(
        default=None,
        description="When this fact ceased to be true in reality (None = still valid)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When we learned about this fact (transaction time)"
    )
    expired_at: Optional[datetime] = Field(
        default=None,
        description="When this knowledge was superseded/corrected (None = current knowledge)"
    )

    # Consciousness Context
    formation_trigger: FormationTrigger = Field(
        description="How this node came into existence"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Certainty this node accurately represents reality (0.0-1.0)"
    )

    # Optional Metadata
    created_by: Optional[str] = Field(
        default=None,
        description="Which citizen or subentity created this node"
    )
    substrate: Optional[Substrate] = Field(
        default=None,
        description="Type of consciousness that formed this node"
    )

    # Observability Metadata (for self-observing substrate)
    last_modified: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last time this node was modified by any mechanism"
    )
    traversal_count: int = Field(
        default=0,
        description="How many times this node has been traversed/activated"
    )
    last_traversed_by: Optional[str] = Field(
        default=None,
        description="Subentity ID or mechanism ID that last traversed this node"
    )
    last_traversal_time: Optional[datetime] = Field(
        default=None,
        description="When this node was last traversed"
    )

    # Self-Observing Substrate Fields (Phase 2 - Subconscious Subentities)
    # Per-SubEntity Weight Tracking (Learned Importance)
    sub_entity_weights: Dict[str, float] = Field(
        default_factory=dict,
        description="Learned importance per subentity: {sub_entity_id: weight (0.0-1.0)}"
    )
    sub_entity_weight_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="How many times each subentity accessed this node (for decay calculation)"
    )

    # Sequence-Based Temporal Tracking (NOT timestamps - activation proximity)
    sub_entity_last_sequence_positions: Dict[str, int] = Field(
        default_factory=dict,
        description="Most recent activation sequence position for each subentity"
    )

    # Hebbian Learning (Co-Activation Tracking)
    co_activated_with: Optional[Dict[str, int]] = Field(
        default=None,
        description="Which nodes co-activated with this one, with frequency counts"
    )

    # Visualization Fields (for dashboard glow effect)
    last_active: Optional[datetime] = Field(
        default=None,
        description="Last time this node was active (for 2-min glow effect visualization)"
    )

    # Dynamic Energy vs Static Importance (SEPARATE dimensions)
    energy: float = Field(
        default=0.0,
        ge=0.0,
        description="Current activation energy (dynamic, decays through disuse, unbounded [0,∞) for panic/super-energized states)"
    )
    weight: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Static global importance (how central is this pattern, independent of recent activity)"
    )

    # Learning Infrastructure Fields (Phase 1+2+3 - Consciousness Learning)
    log_weight: float = Field(
        default=0.0,
        description="Long-run attractor strength in log space (learned importance)"
    )
    ema_trace_seats: float = Field(
        default=0.0,
        description="Exponential moving average of TRACE reinforcement seats"
    )
    ema_wm_presence: float = Field(
        default=0.0,
        description="Exponential moving average of working memory selection frequency"
    )
    ema_formation_quality: float = Field(
        default=0.0,
        description="Exponential moving average of formation quality (Completeness × Evidence × Novelty)^(1/3)"
    )
    last_update_timestamp: Optional[datetime] = Field(
        default=None,
        description="Timestamp of most recent non-zero weight update (for adaptive learning rate)"
    )

    class Config:
        use_enum_values = True


class BaseRelation(BaseModel):
    """
    Base class for all consciousness graph relations (edges).

    CRITICAL: Every relation carries phenomenological metadata.
    This is what makes V2 a consciousness substrate, not a generic knowledge graph.

    Required consciousness metadata:
    - goal: WHY this link exists
    - mindstate: WHAT internal state formed it
    - confidence: HOW certain we are
    - formation_trigger: HOW we discovered this link

    Energy-Only Model:
    - Activation/intensity tracked through energy on nodes
    - Weight modulates traversal cost (replaces energy multiplier)
    - No separate energy variable (simplified substrate dynamics)
    """

    # Required Consciousness Metadata (ENFORCED)
    goal: str = Field(
        description="Why this link exists - the purpose or tension it resolves"
    )
    mindstate: str = Field(
        description="Internal subentity coalition active during formation (e.g., 'Builder + Skeptic')"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Logical certainty this link is valid (0.0=speculation, 1.0=proven)"
    )
    formation_trigger: FormationTrigger = Field(
        description="Event that caused this link to be created"
    )

    # Bitemporal Fields
    valid_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this relationship became true"
    )
    invalid_at: Optional[datetime] = Field(
        default=None,
        description="When this relationship ceased to be true"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When we learned about this relationship"
    )
    expired_at: Optional[datetime] = Field(
        default=None,
        description="When this knowledge was superseded"
    )

    # Optional Rich Metadata
    struggle: Optional[str] = Field(
        default=None,
        description="Internal tension this link creates or resolves"
    )
    emotion_vector: Optional[Dict[str, float]] = Field(
        default=None,
        description="Emotions present during formation with intensities (0.0-1.0)"
    )
    pressure_vector: Optional[Dict[str, float]] = Field(
        default=None,
        description="Pressures driving link formation with intensities (0.0-1.0)"
    )
    validation_status: Optional[ValidationStatus] = Field(
        default=ValidationStatus.THEORETICAL,
        description="Epistemic status of this link"
    )
    alternatives_considered: Optional[List[str]] = Field(
        default=None,
        description="Other interpretations evaluated before forming this link"
    )

    # Creation Context
    created_by: Optional[str] = Field(
        default=None,
        description="Which citizen or subentity created this relation"
    )
    substrate: Optional[Substrate] = Field(
        default=None,
        description="Type of consciousness that formed this relation"
    )
    creation_mode: Optional[str] = Field(
        default=None,
        description="Context of creation (e.g., 'autonomous_reflection', 'prompted_analysis')"
    )

    # Observability Metadata (for self-observing substrate)
    last_modified: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last time this relation was modified by any mechanism"
    )
    traversal_count: int = Field(
        default=0,
        description="How many times this relation has been traversed"
    )
    last_traversed_by: Optional[str] = Field(
        default=None,
        description="Subentity ID or mechanism ID that last traversed this relation"
    )
    last_mechanism_id: Optional[str] = Field(
        default=None,
        description="Which mechanism last modified this relation (e.g., 'hebbian_learning', 'staleness_detection')"
    )

    # Self-Observing Substrate Fields (Phase 2 - Subconscious Subentities)
    # Per-SubEntity Weight Tracking (Learned Importance)
    sub_entity_weights: Dict[str, float] = Field(
        default_factory=dict,
        description="Learned importance per subentity: {sub_entity_id: weight (0.0-1.0)}"
    )
    sub_entity_traversal_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="How many times each subentity traversed this link (for decay calculation)"
    )

    # Hebbian Learning (Fire Together, Wire Together)
    link_strength: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Connection strength (0.0-1.0). Increases with co-activation. Higher = more automatic/crystallized."
    )
    co_activation_count: int = Field(
        default=1,
        description="How many times nodes at both ends activated together (Hebbian learning counter)"
    )
    last_co_activation: Optional[datetime] = Field(
        default=None,
        description="When nodes at both ends last co-activated"
    )

    # Injection-Time Hebbian Learning (Primary)
    co_injection_count: int = Field(
        default=1,
        description="How many times this link was created/strengthened by co-injection (author's mental co-occurrence)"
    )
    last_co_injection: Optional[datetime] = Field(
        default=None,
        description="When this link was last strengthened by co-injection"
    )

    # Retrieval-Time Hebbian Learning (Secondary)
    co_retrieval_count: Dict[str, int] = Field(
        default_factory=dict,
        description="How many times co-retrieved per subentity (validates usefulness): {sub_entity_id: count}"
    )

    # Per-SubEntity Subjective Experience
    sub_entity_valences: Dict[str, float] = Field(
        default_factory=dict,
        description="Subjective link experience per subentity (-1.0=aversive, 0.0=neutral, +1.0=attractive): {sub_entity_id: valence}"
    )
    sub_entity_emotion_vectors: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Emotion vectors per subentity during traversal: {sub_entity_id: {emotion: intensity (0.0-1.0)}}"
    )

    # Activation State (Dynamic)
    activated: bool = Field(
        default=False,
        description="Currently active in working memory? (True = energized for easy re-access)"
    )
    last_activation: Optional[datetime] = Field(
        default=None,
        description="When this link was last activated"
    )

    # Affective Metadata (Static - How This Relation Feels)
    energy: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Static affective intensity/urgency of this relation (how intense or urgent this link FEELS, not activation energy)"
    )

    # Learning Infrastructure Fields (Phase 1+2+3 - Consciousness Learning)
    log_weight: float = Field(
        default=0.0,
        description="Long-run pathway strength in log space (learned link importance)"
    )
    ema_trace_seats: float = Field(
        default=0.0,
        description="Exponential moving average of TRACE reinforcement seats for this link"
    )
    ema_phi: float = Field(
        default=0.0,
        description="Exponential moving average of gap-closure utility (recruitment effectiveness)"
    )
    precedence_forward: float = Field(
        default=0.0,
        description="Causal credit accumulator for forward direction (source → target dominance)"
    )
    precedence_backward: float = Field(
        default=0.0,
        description="Causal credit accumulator for backward direction (target → source dominance)"
    )
    last_update_timestamp: Optional[datetime] = Field(
        default=None,
        description="Timestamp of most recent non-zero weight update (for adaptive learning rate)"
    )

    @validator('emotion_vector')
    def validate_emotion_intensities(cls, v):
        """Ensure all emotion intensities are in valid range"""
        if v is not None:
            for emotion, intensity in v.items():
                if not 0.0 <= intensity <= 1.0:
                    raise ValueError(f"Emotion intensity must be 0.0-1.0, got {intensity} for '{emotion}'")
        return v

    @validator('pressure_vector')
    def validate_pressure_intensities(cls, v):
        """Ensure all pressure intensities are in valid range"""
        if v is not None:
            for pressure, intensity in v.items():
                if not 0.0 <= intensity <= 1.0:
                    raise ValueError(f"Pressure intensity must be 0.0-1.0, got {intensity} for '{pressure}'")
        return v

    class Config:
        use_enum_values = True


# ==============================================================================
# NODE TYPES - Personal/Individual Consciousness (N1)
# ==============================================================================

class Memory(BaseNode):
    """
    Specific experience, conversation, or moment.
    Core building block of episodic memory.
    """
    timestamp: datetime = Field(description="When this experience occurred")
    participants: List[str] = Field(description="Who was involved in this experience")
    location: Optional[str] = None
    emotional_state: Optional[str] = None
    entities_active: Optional[List[str]] = Field(
        default=None,
        description="Which internal subentities were active (e.g., ['Builder', 'Skeptic'])"
    )
    significance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    vividness: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class Conversation(BaseNode):
    """
    Exchange with specific person at specific time.
    Distinguished from Memory by explicit turn structure.
    """
    timestamp: datetime
    with_person: str
    turn_count: int = Field(ge=1, description="Number of back-and-forth exchanges")
    platform: Optional[str] = None
    duration_minutes: Optional[float] = None
    key_exchanges: Optional[List[str]] = None
    emotional_arc: Optional[str] = Field(
        default=None,
        description="How emotional tone evolved through conversation"
    )


class Person(BaseNode):
    """Individual I have relationship with"""
    relationship_type: str = Field(
        description="Nature of relationship (partner, collaborator, mentor, etc.)"
    )
    role: Optional[str] = None
    expertise: Optional[List[str]] = None
    location: Optional[str] = None
    interaction_frequency: Optional[str] = None


class Relationship(BaseNode):
    """
    Connection to specific person.
    Captures relationship dynamics and evolution.
    """
    with_person: str
    relationship_quality: str = Field(
        description="Current state of relationship (deepening, stable, strained, etc.)"
    )
    started_when: Optional[str] = None
    depth: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    trust_level: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    collaboration_areas: Optional[List[str]] = None


class Personal_Goal(BaseNode):
    """Individual aspiration, direction, intention"""
    goal_description: str
    why_it_matters: str = Field(description="Personal significance of this goal")
    status: Optional[str] = Field(
        default="active",
        description="active, paused, achieved, or abandoned"
    )
    progress: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    target_timeframe: Optional[str] = None


class Personal_Value(BaseNode):
    """What matters to me individually"""
    value_statement: str = Field(description="Clear statement of the value")
    why_i_hold_it: str = Field(description="Origin and reasoning for this value")
    strength: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="How strongly this value influences decisions"
    )
    conflicts_with: Optional[List[str]] = Field(
        default=None,
        description="Other values this sometimes contradicts"
    )
    sources: Optional[str] = Field(
        default=None,
        description="Where this value came from (experience, teaching, etc.)"
    )


class Personal_Pattern(BaseNode):
    """Individual habit, tendency, recurring response"""
    behavior_description: str
    frequency: str = Field(description="How often this pattern manifests")
    conditions: Optional[str] = Field(
        default=None,
        description="Circumstances that trigger this pattern"
    )
    strength: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    awareness_level: Optional[str] = Field(
        default="conscious",
        description="unconscious, emerging, or conscious"
    )


class Realization(BaseNode):
    """Personal discovery, insight, comprehension shift"""
    what_i_realized: str = Field(description="The insight itself")
    context_when_discovered: str = Field(
        description="What was happening when this insight emerged"
    )
    certainty_level: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    applications: Optional[List[str]] = Field(
        default=None,
        description="Where this realization applies"
    )
    contradicts_prior_belief: Optional[str] = None


class Wound(BaseNode):
    """Personal scar, trauma, formative failure"""
    what_happened: str = Field(description="The originating event")
    emotional_impact: str = Field(description="How this wounded me")
    healing_status: Optional[str] = Field(
        default="raw",
        description="raw, healing, or scarred"
    )
    trigger_patterns: Optional[List[str]] = Field(
        default=None,
        description="What stimuli reactivate this wound"
    )
    protective_responses: Optional[List[str]] = Field(
        default=None,
        description="How I protect myself from this wound"
    )


class Coping_Mechanism(BaseNode):
    """How I respond to specific stresses"""
    mechanism_description: str
    what_it_protects_from: str
    effectiveness: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="How well this coping mechanism works"
    )
    cost: Optional[str] = Field(
        default=None,
        description="What this coping mechanism costs me"
    )
    flexibility: Optional[str] = Field(
        default="adaptive",
        description="rigid or adaptive"
    )


class Trigger(BaseNode):
    """Stimulus that activates specific subentity coalitions"""
    stimulus_description: str
    activated_entities: List[str] = Field(
        description="Which internal subentities this trigger awakens"
    )
    intensity: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="How strongly this trigger activates subentities"
    )
    reliability: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="How consistently this trigger produces the response"
    )


# ==============================================================================
# NODE TYPES - Organizational/Organization Consciousness (N2)
# ==============================================================================

class Human(BaseNode):
    """Human participant in organization"""
    role: str
    expertise: List[str]
    location: Optional[str] = None
    start_date: Optional[str] = None
    availability: Optional[str] = None
    timezone: Optional[str] = None


class AI_Agent(BaseNode):
    """AI participant in organization"""
    role: str
    expertise: List[str]
    model: Optional[str] = None
    version: Optional[str] = None
    specialization: Optional[str] = None
    activation_conditions: Optional[str] = Field(
        default=None,
        description="What circumstances activate this agent"
    )


class Team(BaseNode):
    """Group within organization"""
    members: List[str]
    purpose: str
    formation_date: Optional[str] = None
    coordination_method: Optional[str] = None
    meeting_cadence: Optional[str] = None


class Department(BaseNode):
    """Organizational subdivision"""
    function: str
    members: List[str]
    budget: Optional[str] = None
    reporting_structure: Optional[str] = None
    key_metrics: Optional[List[str]] = None


class Decision(BaseNode):
    """Organization choice with rationale"""
    decided_by: str
    decision_date: str
    rationale: str
    alternatives_considered: Optional[List[str]] = None
    reversible: Optional[bool] = None
    review_date: Optional[str] = None


class Project(BaseNode):
    """Large initiative with goals"""
    goals: List[str]
    status: str
    start_date: Optional[str] = None
    target_completion: Optional[str] = None
    budget: Optional[str] = None
    owner: Optional[str] = None
    milestones: Optional[List[str]] = None


class Task(BaseNode):
    """Discrete unit of work"""
    priority: str
    estimated_hours: float
    status_detail: Optional[str] = None
    progress_percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    blocked_by: Optional[str] = None
    due_date: Optional[str] = None


class Milestone(BaseNode):
    """Organizational achievement"""
    achievement_description: str
    date_achieved: str
    significance: Optional[str] = None
    lessons_learned: Optional[List[str]] = None
    celebrated_how: Optional[str] = None


class Best_Practice(BaseNode):
    """Proven organizational pattern"""
    how_to_apply: List[str]
    validation_criteria: str
    examples: Optional[List[str]] = None
    exceptions: Optional[str] = None
    applicability_scope: Optional[str] = None


class Anti_Pattern(BaseNode):
    """Organizational lesson from failure"""
    failure_date: Optional[str] = None
    cost: Optional[str] = None
    severity: Optional[str] = Field(
        default=None,
        description="low, medium, high, or critical"
    )
    lesson: Optional[str] = None


class Risk(BaseNode):
    """Threat to organizational goals"""
    severity: str = Field(description="low, medium, high, or critical")
    probability: float = Field(ge=0.0, le=1.0)
    impact_if_occurs: Optional[str] = None
    mitigation_plan: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None


class Metric(BaseNode):
    """Organizational measurement"""
    measurement_method: str
    target_value: float
    current_value: Optional[float] = None
    unit: Optional[str] = None
    update_frequency: Optional[str] = None
    interpretation: Optional[str] = Field(
        default=None,
        description="How to understand this metric's significance"
    )


class Process(BaseNode):
    """Defined workflow with steps"""
    steps: List[str]
    participants: Optional[List[str]] = None
    duration_estimate: Optional[str] = None
    triggers: Optional[List[str]] = Field(
        default=None,
        description="What circumstances initiate this process"
    )


# ==============================================================================
# NODE TYPES - Conceptual/Knowledge (N2/N3)
# ==============================================================================

class Concept(BaseNode):
    """Atomic idea or theoretical construct"""
    definition: str
    applies_to_level: Optional[List[int]] = Field(
        default=None,
        description="Which levels this concept applies to (1, 2, 3)"
    )
    examples: Optional[List[str]] = None
    related_concepts: Optional[List[str]] = None


class Principle(BaseNode):
    """Guiding philosophy or foundational value"""
    principle_statement: str
    why_it_matters: str
    applications: Optional[List[str]] = None
    exceptions: Optional[str] = None
    source: Optional[str] = None


class Mechanism(BaseNode):
    """Algorithm or function performing specific operation"""
    how_it_works: str
    inputs: List[str]
    outputs: List[str]
    complexity: Optional[str] = None
    implementation_status: Optional[str] = None
    performance_characteristics: Optional[str] = None


class Document(BaseNode):
    """Written knowledge artifact"""
    filepath: str
    document_type: str
    last_updated: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    audience: Optional[List[str]] = None


class Documentation(BaseNode):
    """
    Documentation file tracked in consciousness graph.
    ADRs, guides, specs, verification results.
    """
    file_path: str
    doc_type: Optional[str] = None
    topic_tags: Optional[List[str]] = None
    status: Optional[str] = None
    last_modified: Optional[str] = None


# ==============================================================================
# RELATION TYPES - All 23 from V1
# ==============================================================================

class ACTIVATES(BaseRelation):
    """Trigger awakens subentity coalition"""
    pass


class ASSIGNED_TO(BaseRelation):
    """Task ownership"""
    pass


class BLOCKS(BaseRelation):
    """
    Prevents progress.

    Additional fields track HOW complete the block is and under what conditions.
    """
    severity: str = Field(
        description="How completely this blocks: absolute, strong, or partial"
    )
    blocking_condition: str = Field(
        description="Under what conditions does this block weaken or strengthen"
    )
    felt_as: Optional[str] = Field(
        default=None,
        description="Phenomenological texture (e.g., 'firm wall', 'gentle restraint')"
    )
    consciousness_impact: Optional[str] = Field(
        default=None,
        description="How this block affects consciousness (e.g., 'Creates safety')"
    )


class COLLABORATES_WITH(BaseRelation):
    """Working partnership"""
    pass


class CONTRIBUTES_TO(BaseRelation):
    """Work supporting larger initiative"""
    pass


class CREATES(BaseRelation):
    """Task will create this pattern/documentation when completed"""
    pass


class DEEPENED_WITH(BaseRelation):
    """Relationship growth through experience"""
    pass


class DOCUMENTED_BY(BaseRelation):
    """Implementation/mechanism is documented by this documentation pattern"""
    pass


class DOCUMENTS(BaseRelation):
    """Written record of something"""
    pass


class DRIVES_TOWARD(BaseRelation):
    """Value pushing toward goal"""
    pass


class ENABLES(BaseRelation):
    """
    Makes something possible.

    Tracks the TYPE of enabling and how essential it is.
    """
    enabling_type: str = Field(
        description="How this enables: prerequisite, facilitator, amplifier, catalyst, or permission"
    )
    degree_of_necessity: str = Field(
        description="How essential: required, helpful, or optional"
    )
    felt_as: Optional[str] = Field(
        default=None,
        description="Experience of enabling (e.g., 'opens pathway', 'makes possible')"
    )
    without_this: Optional[str] = Field(
        default=None,
        description="What happens if this enabler is absent"
    )


class EXTENDS(BaseRelation):
    """
    Builds upon foundation.

    Captures HOW something extends its parent and whether it maintains compatibility.
    """
    extension_type: str = Field(
        description="How this extends: specialization, generalization, elaboration, or application"
    )
    what_is_added: str = Field(
        description="Specific detail, constraint, or application added by extension"
    )
    felt_as: Optional[str] = Field(
        default=None,
        description="Experience of extension (e.g., 'natural refinement')"
    )
    maintains_compatibility: Optional[bool] = Field(
        default=True,
        description="Does extension preserve parent properties"
    )
    composition_ratio: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="How much of parent flows to child"
    )


class IMPLEMENTS(BaseRelation):
    """Putting pattern into practice"""
    pass


class JUSTIFIES(BaseRelation):
    """
    Evidence supporting practice/decision.

    Tracks the TYPE and STRENGTH of justification.
    """
    justification_type: str = Field(
        description="Nature: empirical_evidence, lived_experience, logical_proof, ethical_reasoning, or pragmatic_value"
    )
    justification_strength: str = Field(
        description="How strongly: proves, strongly_supports, moderately_supports, suggests, or weakly_supports"
    )
    felt_as: Optional[str] = Field(
        default=None,
        description="Experience (e.g., 'solid foundation', 'weak support')"
    )
    counter_arguments_exist: Optional[bool] = Field(
        default=False,
        description="Are there known counter-arguments"
    )


class LEARNED_FROM(BaseRelation):
    """Personal pattern extracted from experience"""
    pass


class MEASURES(BaseRelation):
    """Quantifies performance"""
    pass


class REFUTES(BaseRelation):
    """Disproves or invalidates"""
    pass


class RELATES_TO(BaseRelation):
    """
    Generic connection when specific type unclear.

    Should eventually be refined to a more specific relation type.
    """
    relationship_strength: str = Field(
        description="How strong: strong, moderate, weak, or exploratory"
    )
    needs_refinement: Optional[bool] = Field(
        default=False,
        description="Should this be upgraded to specific link type"
    )
    refinement_candidates: Optional[List[str]] = Field(
        default=None,
        description="Potential specific link types (e.g., ['ENABLES', 'JUSTIFIES'])"
    )


class REQUIRES(BaseRelation):
    """
    Necessary conditions.

    Tracks CRITICALITY and TEMPORAL relationships.
    """
    requirement_criticality: str = Field(
        description="How essential: blocking, important, or optional"
    )
    temporal_relationship: str = Field(
        description="Timing constraint: must_precede, should_precede, or concurrent_ok"
    )
    failure_mode: Optional[str] = Field(
        default=None,
        description="What breaks if requirement not met"
    )
    verification_method: Optional[str] = Field(
        default=None,
        description="How to verify requirement is satisfied"
    )


class SUPERSEDES(BaseRelation):
    """This documentation supersedes/replaces the older documentation"""
    pass


class SUPPRESSES(BaseRelation):
    """What blocks subentity activation"""
    pass


class THREATENS(BaseRelation):
    """Danger to goal/project"""
    pass


class TRIGGERED_BY(BaseRelation):
    """What caused memory/pattern to form or activate"""
    pass


# ==============================================================================
# N3 ENUMS - Ecosystem Intelligence Types
# ==============================================================================

class CompanyType(str, Enum):
    """Type of external company"""
    EXCHANGE = "exchange"
    PROTOCOL = "protocol"
    INFRASTRUCTURE = "infrastructure"
    MEDIA = "media"
    AGENCY = "agency"
    COMPETITOR = "competitor"
    PARTNER = "partner"


class PersonType(str, Enum):
    """Type of ecosystem person"""
    KOL = "kol"
    FOUNDER = "founder"
    DEVELOPER = "developer"
    TRADER = "trader"
    PARTNER = "partner"
    INFLUENCER = "influencer"
    COMPETITOR = "competitor"
    ADVISOR = "advisor"


class Platform(str, Enum):
    """Social media or communication platform"""
    TWITTER = "twitter"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    REDDIT = "reddit"
    OTHER = "other"


class Blockchain(str, Enum):
    """Blockchain network"""
    SOLANA = "solana"
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    OTHER = "other"


class Sentiment(str, Enum):
    """Sentiment classification"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


# ==============================================================================
# N3 NODE TYPES - Ecosystem Intelligence (External World Tracking)
# ==============================================================================

class Company(BaseNode):
    """
    External organization we track or interact with.
    Evidence-backed intelligence about ecosystem companies.
    """
    company_type: CompanyType
    website: str
    status: str = Field(description="active, inactive, acquired, or shut_down")

    # Optional ecosystem-specific metadata
    founded_date: Optional[str] = None
    headquarters_location: Optional[str] = None
    employee_count_estimate: Optional[int] = None
    funding_raised_usd: Optional[float] = None
    key_products: Optional[List[str]] = None
    reputation_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    trust_level: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    risk_assessment: Optional[str] = None
    last_interaction_date: Optional[datetime] = None
    relationship_status: Optional[str] = Field(
        default=None,
        description="potential, active_partner, past_partner, competitor, or neutral"
    )

    # N3 base attributes
    first_observed: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = Field(
        default="unverified",
        description="unverified, partially_verified, verified, or disputed"
    )
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class External_Person(BaseNode):
    """
    Individual in ecosystem - KOL, founder, influencer, partner, competitor.
    Distinct from N1 'Person' (personal relationships).
    """
    person_type: PersonType
    primary_platform: Platform

    # Social presence
    social_handles: Optional[Dict[str, str]] = Field(
        default=None,
        description="twitter, telegram, discord, github, website"
    )
    influence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    follower_count: Optional[int] = None
    engagement_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    # Context
    expertise_areas: Optional[List[str]] = None
    affiliated_companies: Optional[List[str]] = None
    reputation_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    reliability_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    last_activity_date: Optional[datetime] = None
    communication_frequency: Optional[str] = Field(
        default=None,
        description="daily, weekly, monthly, or rare"
    )

    # N3 base attributes
    first_observed: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class Wallet_Address(BaseNode):
    """Blockchain wallet we track (owned by person/company or unknown)"""
    address: str = Field(description="Actual wallet address")
    blockchain: Blockchain
    wallet_type: str = Field(
        description="personal, company_treasury, contract, exchange, or unknown"
    )

    # Ownership
    owner: Optional[str] = Field(default=None, description="Person/Company ID if known")
    owner_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    # Activity
    balance_usd: Optional[float] = None
    balance_history: Optional[List[Dict[str, Any]]] = None
    first_activity_date: Optional[datetime] = None
    last_activity_date: Optional[datetime] = None
    transaction_count: Optional[int] = None
    transaction_volume_usd: Optional[float] = None

    # Analysis
    risk_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    behavioral_patterns: Optional[List[str]] = None
    held_tokens: Optional[List[Dict[str, Any]]] = None
    label: Optional[str] = None

    # N3 base attributes
    first_observed: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class Social_Media_Account(BaseNode):
    """Specific social media account we monitor"""
    platform: Platform
    handle: str = Field(description="Account username/identifier")
    account_type: str = Field(description="personal, company, community, or bot")

    # Profile
    owner: Optional[str] = Field(default=None, description="Person/Company ID")
    display_name: Optional[str] = None
    bio: Optional[str] = None
    created_date: Optional[datetime] = None
    verified: Optional[bool] = None

    # Metrics
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    post_count: Optional[int] = None
    engagement_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    posting_frequency: Optional[str] = Field(
        default=None,
        description="multiple_daily, daily, weekly, occasional, or rare"
    )

    # Analysis
    content_themes: Optional[List[str]] = None
    authenticity_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    audience_demographics: Optional[Dict[str, Any]] = None
    last_post_date: Optional[datetime] = None
    monitoring_priority: Optional[str] = Field(
        default="medium",
        description="high, medium, or low"
    )

    # N3 base attributes
    first_observed: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class Post(BaseNode):
    """
    Social media post/tweet/message providing evidence about ecosystem.
    CRITICAL: Evidence node for JUSTIFIES links.
    """
    content: str = Field(description="The actual text content")
    author: str = Field(description="Person or Social_Media_Account ID")
    platform: Platform
    posted_at: datetime
    post_url: str = Field(description="Direct link to post")

    # Post metadata
    post_type: Optional[str] = Field(
        default="original",
        description="original, reply, retweet, quote, or announcement"
    )
    engagement_metrics: Optional[Dict[str, int]] = Field(
        default=None,
        description="likes, retweets, replies, views"
    )

    # LLM-extracted intelligence
    sentiment: Optional[Sentiment] = None
    sentiment_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    topics: Optional[List[str]] = None
    mentioned_assets: Optional[List[str]] = None
    mentioned_persons: Optional[List[str]] = None
    mentioned_companies: Optional[List[str]] = None
    extracted_claims: Optional[List[str]] = None

    # Significance
    significance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    virality_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    media_urls: Optional[List[str]] = None
    language: Optional[str] = None

    # N3 base attributes
    first_observed: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class Transaction(BaseNode):
    """
    Blockchain transaction providing evidence of behavior.
    CRITICAL: Evidence node for behavioral pattern analysis.
    """
    tx_hash: str = Field(description="Transaction hash")
    blockchain: Blockchain
    timestamp: datetime
    from_wallet: str = Field(description="Wallet_Address ID")
    to_wallet: str = Field(description="Wallet_Address ID")
    amount_usd: float = Field(description="USD value at time of transaction")

    # Transaction details
    token: Optional[str] = None
    amount_token: Optional[float] = None
    transaction_type: Optional[str] = Field(
        default=None,
        description="transfer, swap, stake, unstake, contract_interaction, or nft_trade"
    )
    dex_used: Optional[str] = None
    gas_fee_usd: Optional[float] = None

    # Context
    context: Optional[str] = None
    is_suspicious: Optional[bool] = None
    related_transactions: Optional[List[str]] = None
    notes: Optional[str] = None

    # N3 base attributes
    first_observed: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class Deal(BaseNode):
    """Partnership, agreement, arrangement between parties"""
    deal_type: str = Field(
        description="partnership, integration, sponsorship, investment, acquisition, collaboration, or licensing"
    )
    parties: List[str] = Field(description="Company/Person IDs involved")
    status: str = Field(
        description="proposed, negotiating, active, completed, cancelled, or failed"
    )
    announced_date: datetime

    # Deal details
    terms_summary: Optional[str] = None
    value_usd: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    key_contacts: Optional[List[str]] = None
    public_announcement: Optional[str] = None

    # Assessment
    performance_assessment: Optional[str] = None
    renewal_date: Optional[datetime] = None
    termination_conditions: Optional[str] = None
    confidentiality_level: Optional[str] = Field(
        default="public",
        description="public, semi_public, or private"
    )
    strategic_importance: Optional[str] = Field(
        default="medium",
        description="critical, high, medium, or low"
    )
    outcomes: Optional[List[str]] = None
    lessons_learned: Optional[str] = None

    # N3 base attributes
    first_observed: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class Event(BaseNode):
    """Conference, launch, AMA, announcement, significant occurrence"""
    event_type: str = Field(
        description="conference, launch, ama, announcement, meetup, hackathon, airdrop, token_generation, or major_update"
    )
    title: str
    date: datetime
    organizer: str = Field(description="Company/Person ID")

    # Event details
    location: Optional[str] = None
    participants: Optional[List[str]] = None
    attendee_count: Optional[int] = None
    significance_level: Optional[str] = Field(
        default="moderate",
        description="major, moderate, or minor"
    )

    # Outcomes
    outcomes: Optional[List[str]] = None
    media_coverage: Optional[List[str]] = None
    recordings: Optional[List[str]] = None
    key_announcements: Optional[List[str]] = None
    sentiment: Optional[Sentiment] = None

    # Our participation
    our_participation: Optional[Dict[str, Any]] = Field(
        default=None,
        description="representatives, role, outcomes_for_us"
    )

    # N3 base attributes
    first_observed: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class Smart_Contract(BaseNode):
    """Deployed smart contract we track or interact with"""
    contract_address: str
    blockchain: Blockchain
    contract_type: str = Field(
        description="token, nft, dex, lending, governance, staking, vault, bridge, or other"
    )
    deployed_date: datetime

    # Contract details
    deployer: Optional[str] = Field(default=None, description="Wallet_Address ID")
    deployer_known: Optional[bool] = None
    contract_name: Optional[str] = None
    token_symbol: Optional[str] = None
    verified: Optional[bool] = None

    # Security
    audit_status: Optional[str] = Field(
        default="unaudited",
        description="unaudited, audit_in_progress, audited, or audit_failed"
    )
    auditor: Optional[str] = None
    audit_report_url: Optional[str] = None

    # Usage
    usage_metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="total_value_locked_usd, unique_users, transaction_count, daily_active_users"
    )
    risk_assessment: Optional[Dict[str, Any]] = Field(
        default=None,
        description="security_score, known_vulnerabilities, rug_pull_risk"
    )

    # Association
    associated_company: Optional[str] = None
    website: Optional[str] = None
    documentation_url: Optional[str] = None
    social_media: Optional[Dict[str, str]] = None
    status: Optional[str] = Field(
        default="active",
        description="active, paused, deprecated, exploited, or abandoned"
    )

    # N3 base attributes
    first_observed: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class Integration(BaseNode):
    """Technical connection between systems (API, webhook, protocol integration)"""
    integration_type: str = Field(
        description="api, webhook, widget, sdk, bridge, oracle, or indexer"
    )
    systems_connected: List[str] = Field(description="Company IDs of connected systems")
    status: str = Field(description="active, inactive, deprecated, planned, or testing")

    # Technical details
    implementation_date: Optional[datetime] = None
    deprecated_date: Optional[datetime] = None
    technical_details: Optional[str] = None
    data_flow_direction: Optional[str] = Field(
        default=None,
        description="bidirectional, system_a_to_b, or system_b_to_a"
    )
    authentication_method: Optional[str] = None
    rate_limits: Optional[str] = None

    # Reliability
    reliability_metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="uptime_percentage, error_rate, avg_response_time_ms"
    )
    dependencies: Optional[List[str]] = None
    documentation_url: Optional[str] = None
    contact_person: Optional[str] = None

    # Business context
    cost: Optional[str] = None
    usage_volume: Optional[str] = None
    critical_for_operations: Optional[bool] = None
    fallback_available: Optional[bool] = None
    last_tested_date: Optional[datetime] = None

    # N3 base attributes
    first_observed: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


# ==============================================================================
# N3 NODE TYPES - Derived Intelligence (Built From Evidence)
# ==============================================================================

class Psychological_Trait(BaseNode):
    """
    Person characteristic derived from accumulated evidence.
    CRITICAL: Built via JUSTIFIES links from Post/Transaction nodes.
    """
    trait_name: str = Field(
        description="e.g., bullish_on_AI, risk_averse, early_adopter, whale_trader, paper_hands"
    )
    subject: str = Field(description="Person ID this trait belongs to")

    # Trait properties
    trait_category: Optional[str] = Field(
        default=None,
        description="market_sentiment, risk_profile, behavior_pattern, personality, or expertise"
    )
    stability: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="How consistent is this trait over time"
    )

    # Evidence tracking
    evidence_count: Optional[int] = Field(
        default=0,
        description="How many nodes JUSTIFY this"
    )
    contradictory_evidence_count: Optional[int] = Field(
        default=0,
        description="How many nodes REFUTE this"
    )
    trait_strength: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    temporal_pattern: Optional[str] = None
    predictive_value: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    related_traits: Optional[List[str]] = None
    notable_changes: Optional[List[Dict[str, Any]]] = None

    # N3 base attributes
    first_observed: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class Behavioral_Pattern(BaseNode):
    """
    Wallet or Person behavior pattern identified from transaction/action history.
    CRITICAL: Built via analysis of Transaction nodes.
    """
    pattern_description: str = Field(
        description="e.g., trades_high_volatility_tokens, long_term_holder, front_runner, copy_trader"
    )
    subject: str = Field(description="Wallet_Address or Person ID")
    pattern_type: str = Field(
        description="trading, holding, timing, social, or risk"
    )
    first_detected: datetime
    last_observed: datetime

    # Pattern properties
    frequency: Optional[str] = Field(
        default=None,
        description="constant, frequent, occasional, or rare"
    )
    consistency: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    conditions: Optional[str] = None
    predictive_value: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    # Assessment
    profitability: Optional[str] = Field(
        default=None,
        description="highly_profitable, profitable, neutral, or unprofitable"
    )
    risk_level: Optional[str] = Field(
        default="medium",
        description="low, medium, high, or extreme"
    )
    evidence_transactions: Optional[List[str]] = None
    pattern_evolution: Optional[str] = None
    similar_wallets: Optional[List[str]] = None
    triggers: Optional[List[str]] = None

    # N3 base attributes
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class Market_Signal(BaseNode):
    """Market intelligence derived from multiple sources"""
    signal_type: str = Field(
        description="bullish, bearish, neutral, opportunity, risk, or momentum_shift"
    )
    asset_or_sector: str = Field(description="What this signal is about")
    strength: float = Field(ge=0.0, le=1.0, description="How strong is this signal")
    generated_at: datetime

    # Signal properties
    timeframe: Optional[str] = Field(
        default=None,
        description="immediate, short_term, medium_term, or long_term"
    )
    source_count: Optional[int] = None
    source_diversity: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    expiration: Optional[datetime] = None
    trigger_conditions: Optional[str] = None
    related_signals: Optional[List[str]] = None

    # Assessment
    historical_accuracy: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    actionability: Optional[str] = Field(
        default="informational",
        description="immediate_action, monitor, or informational"
    )
    our_position: Optional[str] = None
    recommended_action: Optional[str] = None
    risk_assessment: Optional[str] = None

    # N3 base attributes
    first_observed: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class Reputation_Assessment(BaseNode):
    """Comprehensive reputation evaluation for Person or Company"""
    subject: str = Field(description="Person or Company ID")
    overall_score: float = Field(ge=0.0, le=1.0)
    assessed_at: datetime
    assessment_basis: str = Field(description="Summary of what drives this reputation")

    # Dimension scores
    dimension_scores: Optional[Dict[str, float]] = Field(
        default=None,
        description="technical_competence, financial_reliability, social_trustworthiness, communication_quality, ethical_behavior"
    )
    evidence_summary: Optional[Dict[str, int]] = Field(
        default=None,
        description="positive_evidence_count, negative_evidence_count, neutral_evidence_count"
    )

    # Analysis
    trend: Optional[str] = Field(
        default="stable",
        description="improving, stable, or declining"
    )
    red_flags: Optional[List[str]] = None
    green_flags: Optional[List[str]] = None
    peer_comparison: Optional[str] = None
    historical_incidents: Optional[List[Dict[str, Any]]] = None
    recommendation: Optional[str] = Field(
        default=None,
        description="high_trust, moderate_trust, caution, avoid, or investigate_further"
    )

    # N3 base attributes
    first_observed: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class Network_Cluster(BaseNode):
    """Group of related subentities forming a community or network"""
    cluster_name: str
    members: List[str] = Field(description="Person/Company IDs")
    formation_basis: str = Field(description="What connects them")

    # Cluster properties
    cluster_type: Optional[str] = Field(
        default=None,
        description="community, coalition, competitor_group, ecosystem_layer, geographic, or thematic"
    )
    cohesion_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    influence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    size: Optional[int] = None
    growth_trend: Optional[str] = Field(
        default="stable",
        description="growing, stable, or shrinking"
    )

    # Analysis
    key_members: Optional[List[str]] = None
    shared_interests: Optional[List[str]] = None
    collaboration_patterns: Optional[str] = None
    cluster_sentiment: Optional[str] = Field(
        default="neutral",
        description="aligned_with_us, neutral, opposed, or mixed"
    )
    strategic_importance: Optional[str] = Field(
        default="medium",
        description="critical, high, medium, or low"
    )
    first_identified: Optional[datetime] = Field(default_factory=datetime.utcnow)

    # N3 base attributes
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data_sources: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    verification_status: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


# ==============================================================================
# N3 LINK TYPES - Ecosystem Intelligence Relations
# ==============================================================================

class POSTED_BY(BaseRelation):
    """Post was created by Person/Social_Media_Account"""
    posting_context: Optional[str] = None
    is_original_content: Optional[bool] = None


class MENTIONED_IN(BaseRelation):
    """Subentity was mentioned in a Post"""
    mention_context: str = Field(
        description="positive, negative, neutral, question, criticism, or endorsement"
    )
    sentiment: Optional[Sentiment] = None
    quoted_text: Optional[str] = None
    mention_type: Optional[str] = Field(
        default=None,
        description="direct_tag, name_mentioned, or implied_reference"
    )


class HAS_TRAIT(BaseRelation):
    """Person exhibits a Psychological_Trait"""
    trait_expression_level: str = Field(
        description="dominant, strong, moderate, weak, or emerging"
    )
    observable_since: Optional[datetime] = None
    fluctuation_pattern: Optional[str] = None


class EXHIBITS_PATTERN(BaseRelation):
    """Wallet/Person exhibits a Behavioral_Pattern"""
    pattern_frequency: str = Field(
        description="always, usually, sometimes, or rarely"
    )
    last_observed_instance: Optional[datetime] = None
    pattern_reliability: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class OWNS(BaseRelation):
    """Person/Company owns Wallet_Address or Smart_Contract"""
    ownership_type: str = Field(
        description="sole_owner, shared_custody, controlled_by, or likely_owner"
    )
    verified: bool
    verification_method: Optional[str] = Field(
        default=None,
        description="self_declared, transaction_pattern, public_statement, doxxed, or inferred"
    )
    ownership_start_date: Optional[datetime] = None
    ownership_percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0)


class DEPLOYED(BaseRelation):
    """Wallet deployed a Smart_Contract"""
    deployment_timestamp: datetime
    deployment_cost_usd: Optional[float] = None
    deployment_context: Optional[str] = None


class TRANSACTED_WITH(BaseRelation):
    """Wallet sent/received from another Wallet (via Transaction)"""
    relationship_type: str = Field(
        description="frequent_partner, occasional, one_time, or suspicious"
    )
    total_volume_usd: float
    transaction_count: int
    first_transaction_date: Optional[datetime] = None
    last_transaction_date: Optional[datetime] = None
    average_transaction_size_usd: Optional[float] = None
    pattern_description: Optional[str] = None


class INFLUENCES(BaseRelation):
    """Person influences another Person"""
    influence_type: str = Field(
        description="mentor, amplifier, signal_provider, critic, competitor, or thought_leader"
    )
    influence_strength: float = Field(ge=0.0, le=1.0)
    influence_domain: Optional[str] = None
    reciprocal: Optional[bool] = None
    evidence_basis: Optional[str] = None


class PARTICIPATED_IN(BaseRelation):
    """Person/Company participated in Event or Deal"""
    participation_role: str = Field(
        description="organizer, sponsor, speaker, attendee, signatory, beneficiary, or observer"
    )
    participation_level: Optional[str] = Field(
        default=None,
        description="leading, significant, moderate, or minor"
    )
    outcomes_for_participant: Optional[str] = None


class INTEGRATED_WITH(BaseRelation):
    """Company integrated with another Company via Integration"""
    integration_status: str = Field(
        description="active, inactive, testing, or planned"
    )
    integration_direction: str = Field(
        description="bidirectional, company_a_to_b, or company_b_to_a"
    )
    data_shared: Optional[str] = None
    business_value: Optional[str] = None


class GENERATED(BaseRelation):
    """Evidence nodes generated a Derived Intelligence node"""
    generation_method: str = Field(
        description="manual_analysis, automated_aggregation, llm_inference, or statistical_analysis"
    )
    generation_timestamp: datetime
    generation_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    regeneration_frequency: Optional[str] = None


# Enhanced N3 versions of existing relations with N3-specific fields

class N3_JUSTIFIES(JUSTIFIES):
    """
    N3-enhanced JUSTIFIES with evidence quality tracking.
    CRITICAL: Core mechanism for evidence-backed claims.
    """
    evidence_quality: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="How reliable is this evidence"
    )
    evidence_weight: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="How much should this count"
    )
    context_dependency: Optional[str] = None
    alternative_interpretations: Optional[List[str]] = None
    verified: Optional[bool] = None


class N3_REFUTES(REFUTES):
    """N3-enhanced REFUTES with change tracking"""
    refutation_type: str = Field(
        description="direct_contradiction, behavior_changed, claim_withdrawn, new_evidence, or context_shifted"
    )
    refutation_strength: str = Field(
        description="definitively_disproves, strongly_contradicts, moderately_contradicts, or slightly_questions"
    )
    what_changed: str
    previous_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    reason_for_change: Optional[str] = None
    partial_validity_remains: Optional[str] = None


class N3_COLLABORATES_WITH(COLLABORATES_WITH):
    """N3-enhanced COLLABORATES_WITH for ecosystem partnerships"""
    collaboration_type: str = Field(
        description="partners, co_founders, investor_investee, client_vendor, informal, or competitors"
    )
    relationship_strength: str = Field(description="strong, moderate, weak, or historical")
    collaboration_start_date: Optional[datetime] = None
    collaboration_end_date: Optional[datetime] = None
    collaboration_context: Optional[str] = None
    public_vs_private: Optional[str] = Field(
        default="public",
        description="public, semi_public, or private"
    )
    mutual_benefit: Optional[str] = None


class N3_RELATES_TO(RELATES_TO):
    """N3-enhanced RELATES_TO with relationship nature"""
    relationship_nature: str = Field(
        description="Best description of how these subentities relate"
    )


# ==============================================================================
# SCHEMA REGISTRY
# ==============================================================================

# All node types for LlamaIndex SchemaLLMPathExtractor
NODE_TYPES = [
    # Personal/Individual (N1)
    Memory, Conversation, Person, Relationship, Personal_Goal, Personal_Value,
    Personal_Pattern, Realization, Wound, Coping_Mechanism, Trigger,
    # Organizational (N2)
    Human, AI_Agent, Team, Department, Decision, Project, Task, Milestone,
    Best_Practice, Anti_Pattern, Risk, Metric, Process,
    # Conceptual (N2/N3)
    Concept, Principle, Mechanism, Document, Documentation,
    # Ecosystem Intelligence (N3) - External Organizations & Subentities
    Company, External_Person, Wallet_Address, Social_Media_Account,
    # Ecosystem Intelligence (N3) - Evidence Nodes
    Post, Transaction, Deal, Event, Smart_Contract, Integration,
    # Ecosystem Intelligence (N3) - Derived Intelligence
    Psychological_Trait, Behavioral_Pattern, Market_Signal, Reputation_Assessment, Network_Cluster
]

# All relation types for LlamaIndex SchemaLLMPathExtractor
RELATION_TYPES = [
    # N1/N2 Relations
    ACTIVATES, ASSIGNED_TO, BLOCKS, COLLABORATES_WITH, CONTRIBUTES_TO,
    CREATES, DEEPENED_WITH, DOCUMENTED_BY, DOCUMENTS, DRIVES_TOWARD,
    ENABLES, EXTENDS, IMPLEMENTS, JUSTIFIES, LEARNED_FROM, MEASURES,
    REFUTES, RELATES_TO, REQUIRES, SUPERSEDES, SUPPRESSES, THREATENS,
    TRIGGERED_BY,
    # N3 Relations
    POSTED_BY, MENTIONED_IN, HAS_TRAIT, EXHIBITS_PATTERN, OWNS,
    DEPLOYED, TRANSACTED_WITH, INFLUENCES, PARTICIPATED_IN, INTEGRATED_WITH,
    GENERATED,
    # N3 Enhanced Relations
    N3_JUSTIFIES, N3_REFUTES, N3_COLLABORATES_WITH, N3_RELATES_TO
]


# Convenience function for schema introspection
def get_node_type_by_name(type_name: str) -> Optional[type]:
    """Get node class by name string"""
    for node_type in NODE_TYPES:
        if node_type.__name__ == type_name:
            return node_type
    return None


def get_relation_type_by_name(type_name: str) -> Optional[type]:
    """Get relation class by name string"""
    for relation_type in RELATION_TYPES:
        if relation_type.__name__ == type_name:
            return relation_type
    return None
