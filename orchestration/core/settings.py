"""
Centralized configuration for Mind Protocol orchestration layer.

All services load configuration from this single source.
Configuration can be provided via environment variables or .env file.

Author: Ada (Architect)
Created: 2025-10-22
"""

import os
from typing import Optional
from pathlib import Path
from pydantic import BaseModel
from orchestration.config.graph_names import resolver

class EngineConfig(BaseModel):
    """
    Configuration for consciousness engine.

    Args:
        tick_interval_ms: Base tick interval in milliseconds. Default 100ms (10 Hz).
        entity_id: Primary subentity identifier. Default "consciousness_engine".
        network_id: Network identifier (N1/N2/N3). Default "N1".
        enable_diffusion: Enable energy diffusion. Default True.
        enable_decay: Enable energy decay. Default True.
        enable_strengthening: Enable link strengthening. Default True.
        enable_websocket: Enable WebSocket broadcasting. Default True.
        compute_budget: Max cost units per tick. Default 100.0.
        max_nodes_per_tick: Max node updates per tick. Default 50000.
    """
    tick_interval_ms: float = 10000.0  # 0.1 Hz (1 tick per 10 seconds) - EMERGENCY THROTTLE to reduce event storm from 65/sec to ~6.5/sec
    entity_id: str = "consciousness_engine"
    network_id: str = "N1"
    enable_diffusion: bool = True
    enable_decay: bool = True
    enable_strengthening: bool = True
    enable_websocket: bool = True
    compute_budget: float = 100.0
    max_nodes_per_tick: int = 50000

class Settings:
    """Central configuration for all Mind Protocol services."""

    DEFAULT_TIMEOUT_SEC: float = 10.0

    # === Service Ports ===
    WS_HOST: str = os.getenv("WS_HOST", "localhost")
    WS_PORT: int = int(os.getenv("WS_PORT", "8000"))

    API_HOST: str = os.getenv("MP_API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("MP_API_PORT", "8788"))

    # === Database ===
    FALKORDB_HOST: str = os.getenv("FALKORDB_HOST", "localhost")
    FALKORDB_PORT: int = int(os.getenv("FALKORDB_PORT", "6379"))

    # Graph names - Use resolver from orchestration.config.graph_names
    N2_GRAPH_NAME: str = resolver.org_base()  # N2 organizational graph
    N3_GRAPH_NAME: str = "ecosystem"  # N3 ecosystem graph (L3)

    # === Embeddings & Search ===
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # === Logging ===
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # json or text

    # === Paths ===
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    CONSCIOUSNESS_DIR: Path = PROJECT_ROOT / "consciousness"

    # === Feature Flags ===
    ENTITY_LAYER_ENABLED: bool = os.getenv("ENTITY_LAYER_ENABLED", "true").lower() == "true"
    TRACE_LEARNING_ENABLED: bool = os.getenv("TRACE_LEARNING_ENABLED", "true").lower() == "true"
    WEIGHT_LEARNING_ENABLED: bool = os.getenv("WEIGHT_LEARNING_ENABLED", "true").lower() == "true"

    # Two-Scale Traversal (Phase 1: default enabled)
    TWO_SCALE_ENABLED: bool = os.getenv("TWO_SCALE_ENABLED", "true").lower() == "true"
    TWO_SCALE_HUNGERS: list = ["goal_fit", "integration", "completeness", "ease", "novelty"]  # Phase 1: 5 hungers
    TWO_SCALE_TOPK_ENTITIES: int = int(os.getenv("TWO_SCALE_TOPK_ENTITIES", "1"))  # Phase 2: multi-entity expansion

    # === Performance ===
    MAX_CONTEXT_TOKENS: int = int(os.getenv("MAX_CONTEXT_TOKENS", "180000"))
    FRAME_RATE_TARGET: float = float(os.getenv("FRAME_RATE_TARGET", "1.0"))  # frames per second

    # === Proof Runner ===
    PROOF_CAPTURE_SECONDS: int = int(os.getenv("PROOF_CAPTURE_SECONDS", "60"))
    PROOF_RHO_BAND_LOW: float = float(os.getenv("PROOF_RHO_BAND_LOW", "0.8"))
    PROOF_RHO_BAND_HIGH: float = float(os.getenv("PROOF_RHO_BAND_HIGH", "1.2"))

    # === Health Monitoring ===
    HEARTBEAT_INTERVAL: int = int(os.getenv("HEARTBEAT_INTERVAL", "5"))  # seconds
    HEALTH_CHECK_PORT: int = int(os.getenv("HEALTH_CHECK_PORT", "8789"))

    # === Emotion Coloring (spec: emotion_coloring.md) ===
    EMOTION_ENABLED: bool = os.getenv("EMOTION_ENABLED", "true").lower() == "true"

    # Coloring parameters
    EMOTION_ALPHA: float = float(os.getenv("EMOTION_ALPHA", "0.98"))  # retention per tick
    EMOTION_BETA: float = float(os.getenv("EMOTION_BETA", "0.10"))   # write rate (telemetry-tuned)
    EMOTION_DWELL_MIN_MS: float = float(os.getenv("EMOTION_DWELL_MIN_MS", "25"))  # min dwell time to color
    EMOTION_COLOR_SAMPLE_RATE: float = float(os.getenv("EMOTION_COLOR_SAMPLE_RATE", "0.1"))  # emission sampling

    # Per-type magnitude caps (can be overridden by node schema)
    EMOTION_CAPS: dict = {
        "default": 0.8,
        "Memory": 1.0,
        "Episode": 0.9,
        "Realization": 0.85,
        "Link": 0.7,
    }

    # Decay parameters
    EMOTION_DECAY_RATE: float = float(os.getenv("EMOTION_DECAY_RATE", "0.001"))  # η_emo (slower than activation)

    # Resonance gate (coherence via similarity)
    RES_LAMBDA: float = float(os.getenv("RES_LAMBDA", "0.6"))  # sensitivity
    RES_MIN_MULT: float = float(os.getenv("RES_MIN_MULT", "0.6"))  # clamp floor
    RES_MAX_MULT: float = float(os.getenv("RES_MAX_MULT", "1.6"))  # clamp ceiling

    # Complementarity gate (regulation via opposites)
    COMP_LAMBDA: float = float(os.getenv("COMP_LAMBDA", "0.8"))  # sensitivity
    COMP_MIN_MULT: float = float(os.getenv("COMP_MIN_MULT", "0.7"))  # clamp floor
    COMP_MAX_MULT: float = float(os.getenv("COMP_MAX_MULT", "1.5"))  # clamp ceiling

    # Emotion gates integration (traversal cost modulation)
    EMOTION_GATES_ENABLED: bool = os.getenv("EMOTION_GATES_ENABLED", "true").lower() == "true"  # Feature flag for gate integration (ENABLED 2025-10-23)

    # === Decay (spec: type_dependent_decay.md) ===

    # Activation decay (fast, per-tick)
    # Base rate: 0.00002/s gives Memory (~19h), Task (~2h) half-lives
    EMACT_DECAY_BASE: float = float(os.getenv("EMACT_DECAY_BASE", "0.00002"))  # Base activation decay per second

    # Per-type multipliers for activation decay (multiply by base)
    EMACT_DECAY_MULTIPLIERS: dict = {
        "Memory": 0.5,              # Slow: 0.00001/s → half-life ~19h
        "Episodic_Memory": 0.25,    # Very slow: 0.000005/s → half-life ~38h
        "Concept": 1.0,             # Medium: 0.00002/s → half-life ~9.6h
        "Task": 5.0,                # Fast: 0.0001/s → half-life ~1.9h
        "Goal": 0.5,                # Slow: 0.00001/s → half-life ~19h
        "Event": 2.5,               # Medium-fast: 0.00005/s → half-life ~3.8h
        "Person": 0.5,              # Slow: 0.00001/s → half-life ~19h
        "Document": 0.75,           # Slow-medium: 0.000015/s → half-life ~12.8h
        "Mechanism": 1.0,           # Medium: 0.00002/s → half-life ~9.6h
        "Principle": 0.5,           # Slow: 0.00001/s → half-life ~19h
        "Realization": 1.5,         # Medium: 0.00003/s → half-life ~6.4h
        "Default": 1.0              # Fallback
    }

    # Weight decay (slow, periodic)
    # Base rate: 0.000001/s gives Memory (~16 days), Task (~2.7 days) half-lives
    WEIGHT_DECAY_BASE: float = float(os.getenv("WEIGHT_DECAY_BASE", "0.000001"))  # Base weight decay per second (MUCH slower)

    # Per-type multipliers for weight decay
    WEIGHT_DECAY_MULTIPLIERS: dict = {
        "Memory": 0.5,              # Very slow: 0.0000005/s → half-life ~16 days
        "Episodic_Memory": 0.25,    # Extremely slow: 0.00000025/s → half-life ~32 days
        "Concept": 1.0,             # Slow: 0.000001/s → half-life ~8 days
        "Task": 3.0,                # Faster: 0.000003/s → half-life ~2.7 days
        "Goal": 0.5,                # Very slow: 0.0000005/s → half-life ~16 days
        "Event": 2.0,               # Faster: 0.000002/s → half-life ~4 days
        "Person": 0.3,              # Extremely slow: 0.0000003/s → half-life ~27 days (relationships persist)
        "Document": 0.7,            # Slow: 0.0000007/s → half-life ~11 days
        "Mechanism": 0.8,           # Slow: 0.0000008/s → half-life ~10 days
        "Principle": 0.3,           # Extremely slow: 0.0000003/s → half-life ~27 days (core knowledge)
        "Realization": 1.5,         # Medium: 0.0000015/s → half-life ~5.3 days
        "Default": 1.0              # Fallback
    }

    # Decay bounds (safety limits for criticality controller)
    EMACT_DECAY_MIN: float = float(os.getenv("EMACT_DECAY_MIN", "0.000001"))   # Minimum activation decay (~100h half-life)
    EMACT_DECAY_MAX: float = float(os.getenv("EMACT_DECAY_MAX", "0.001"))      # Maximum activation decay (~11min half-life)
    WEIGHT_DECAY_MIN: float = float(os.getenv("WEIGHT_DECAY_MIN", "0.0000001"))  # Minimum weight decay (~80 days)
    WEIGHT_DECAY_MAX: float = float(os.getenv("WEIGHT_DECAY_MAX", "0.00001"))    # Maximum weight decay (~19h)

    # Energy floor (prevent over-decay)
    ENERGY_FLOOR: float = float(os.getenv("ENERGY_FLOOR", "0.001"))

    # Weight floor (prevent complete erasure)
    WEIGHT_FLOOR: float = float(os.getenv("WEIGHT_FLOOR", "-5.0"))  # log_weight floor

    # Weight ceiling (prevent numerical overflow)
    WEIGHT_CEILING: float = float(os.getenv("WEIGHT_CEILING", "2.0"))  # log_weight ceiling (exp(2) ≈ 7.4)

    # === Link Strengthening (spec: link_strengthening.md) ===

    # Learning rate
    LEARNING_RATE_BASE: float = float(os.getenv("LEARNING_RATE_BASE", "0.01"))  # Base Hebbian learning rate

    # History tracking
    MAX_STRENGTHENING_HISTORY: int = int(os.getenv("MAX_STRENGTHENING_HISTORY", "100"))  # Max events per link

    # === Affective Coupling Telemetry (PR-A: Instrumentation) ===

    # Global telemetry toggle
    AFFECTIVE_TELEMETRY_ENABLED: bool = os.getenv("AFFECTIVE_TELEMETRY_ENABLED", "true").lower() == "true"

    # Sampling and buffering
    TELEMETRY_SAMPLE_RATE: float = float(os.getenv("TELEMETRY_SAMPLE_RATE", "1.0"))  # 1.0 = emit all events
    TELEMETRY_BUFFER_SIZE: int = int(os.getenv("TELEMETRY_BUFFER_SIZE", "1000"))  # Buffer size before flush
    TELEMETRY_FLUSH_INTERVAL_S: float = float(os.getenv("TELEMETRY_FLUSH_INTERVAL_S", "5.0"))  # Auto-flush interval

    # === PR-B: Emotion Couplings (Threshold + Memory) ===

    # Threshold Modulation
    AFFECTIVE_THRESHOLD_ENABLED: bool = os.getenv("AFFECTIVE_THRESHOLD_ENABLED", "true").lower() == "true"
    AFFECTIVE_THRESHOLD_LAMBDA_FACTOR: float = float(os.getenv("AFFECTIVE_THRESHOLD_LAMBDA_FACTOR", "0.08"))  # ~8% threshold reduction

    # Memory Amplification
    AFFECTIVE_MEMORY_ENABLED: bool = os.getenv("AFFECTIVE_MEMORY_ENABLED", "true").lower() == "true"
    AFFECTIVE_MEMORY_KAPPA: float = float(os.getenv("AFFECTIVE_MEMORY_KAPPA", "0.3"))  # Max 1.3x boost at saturation
    AFFECTIVE_MEMORY_MIN: float = float(os.getenv("AFFECTIVE_MEMORY_MIN", "0.6"))  # Floor to prevent over-dampening

    # Coherence Persistence
    RES_DIMINISH_ENABLED: bool = os.getenv("RES_DIMINISH_ENABLED", "true").lower() == "true"
    COHERENCE_SIMILARITY_THRESHOLD: float = float(os.getenv("COHERENCE_SIMILARITY_THRESHOLD", "0.85"))  # Cosine threshold for "same state"
    COHERENCE_PERSISTENCE_THRESHOLD: int = int(os.getenv("COHERENCE_PERSISTENCE_THRESHOLD", "20"))  # Frames before diminishing returns (P)
    COHERENCE_DECAY_RATE: float = float(os.getenv("COHERENCE_DECAY_RATE", "0.05"))  # Resonance weakening rate (γ)

    # === PR-C: Affective Response V2 (Multi-Pattern) ===

    # Global toggle
    AFFECTIVE_RESPONSE_V2: bool = os.getenv("AFFECTIVE_RESPONSE_V2", "false").lower() == "true"

    # Pattern strengths (base multipliers)
    LAMBDA_REG: float = float(os.getenv("LAMBDA_REG", "0.5"))  # Regulation strength
    LAMBDA_RUM: float = float(os.getenv("LAMBDA_RUM", "0.3"))  # Rumination strength
    LAMBDA_DIST: float = float(os.getenv("LAMBDA_DIST", "0.2"))  # Distraction strength

    # Initial pattern weights (softmax distribution)
    PATTERN_WEIGHTS_INITIAL: list = [0.5, 0.3, 0.2]  # [reg, rum, dist]

    # Rumination cap (safety limit)
    RUMINATION_CAP: int = int(os.getenv("RUMINATION_CAP", "10"))  # Max consecutive rumination frames

    # Multiplier bounds
    M_AFFECT_MIN: float = float(os.getenv("M_AFFECT_MIN", "0.6"))  # Floor for multi-pattern multiplier
    M_AFFECT_MAX: float = float(os.getenv("M_AFFECT_MAX", "1.0"))  # Ceiling (neutral or dampening only)

    # Pattern effectiveness learning
    PATTERN_EFFECTIVENESS_EMA_ALPHA: float = float(os.getenv("PATTERN_EFFECTIVENESS_EMA_ALPHA", "0.1"))  # EMA alpha for learning

    # === Identity Multiplicity (PR-D: Outcome-Based Detection) ===

    # Global toggle
    IDENTITY_MULTIPLICITY_ENABLED: bool = os.getenv("IDENTITY_MULTIPLICITY_ENABLED", "false").lower() == "true"

    # Outcome thresholds (detect productive vs conflict states)
    PROGRESS_THRESHOLD: float = float(os.getenv("PROGRESS_THRESHOLD", "0.3"))  # Min progress rate for productive state
    EFFICIENCY_THRESHOLD: float = float(os.getenv("EFFICIENCY_THRESHOLD", "0.5"))  # Min energy efficiency for productive state
    FLIP_THRESHOLD: int = int(os.getenv("FLIP_THRESHOLD", "5"))  # Max identity flips before conflict
    MULTIPLICITY_WINDOW_FRAMES: int = int(os.getenv("MULTIPLICITY_WINDOW_FRAMES", "20"))  # Rolling window for metrics

    # === PR-E: Foundations Enrichments ===

    # E.2 Consolidation (prevents premature decay of important patterns)
    CONSOLIDATION_ENABLED: bool = os.getenv("CONSOLIDATION_ENABLED", "false").lower() == "true"
    CONSOLIDATION_RETRIEVAL_BOOST: float = float(os.getenv("CONSOLIDATION_RETRIEVAL_BOOST", "0.3"))  # c_retrieval
    CONSOLIDATION_AFFECT_BOOST: float = float(os.getenv("CONSOLIDATION_AFFECT_BOOST", "0.4"))  # c_affect
    CONSOLIDATION_GOAL_BOOST: float = float(os.getenv("CONSOLIDATION_GOAL_BOOST", "0.5"))  # c_goal
    CONSOLIDATION_MAX_FACTOR: float = float(os.getenv("CONSOLIDATION_MAX_FACTOR", "0.8"))  # Max total c
    CONSOLIDATION_FLOOR: float = float(os.getenv("CONSOLIDATION_FLOOR", "0.01"))  # Prevent complete decay

    # E.3 Decay Resistance (central/bridge nodes persist longer)
    DECAY_RESISTANCE_ENABLED: bool = os.getenv("DECAY_RESISTANCE_ENABLED", "false").lower() == "true"
    DECAY_RESISTANCE_MAX_FACTOR: float = float(os.getenv("DECAY_RESISTANCE_MAX_FACTOR", "1.5"))  # Max resistance multiplier

    # E.4 Diffusion Stickiness (energy retention during diffusion)
    DIFFUSION_STICKINESS_ENABLED: bool = os.getenv("DIFFUSION_STICKINESS_ENABLED", "false").lower() == "true"
    STICKINESS_TYPE_MEMORY: float = float(os.getenv("STICKINESS_TYPE_MEMORY", "0.9"))  # Memory nodes sticky
    STICKINESS_TYPE_TASK: float = float(os.getenv("STICKINESS_TYPE_TASK", "0.3"))  # Task nodes flow
    STICKINESS_TYPE_DEFAULT: float = float(os.getenv("STICKINESS_TYPE_DEFAULT", "0.6"))  # Default stickiness
    STICKINESS_CONSOLIDATION_BOOST: float = float(os.getenv("STICKINESS_CONSOLIDATION_BOOST", "0.2"))  # Extra stickiness if consolidated

    # E.5 Affective Priming (mood-congruent stimulus injection)
    AFFECTIVE_PRIMING_ENABLED: bool = os.getenv("AFFECTIVE_PRIMING_ENABLED", "false").lower() == "true"
    AFFECTIVE_PRIMING_P: float = float(os.getenv("AFFECTIVE_PRIMING_P", "0.15"))  # Max 15% boost
    AFFECTIVE_PRIMING_MIN_RECENT: float = float(os.getenv("AFFECTIVE_PRIMING_MIN_RECENT", "0.3"))  # Min ||A_recent||
    AFFECTIVE_PRIMING_WINDOW_FRAMES: int = int(os.getenv("AFFECTIVE_PRIMING_WINDOW_FRAMES", "20"))  # EMA window

    # E.6 Coherence Metric (measures flow vs chaos)
    COHERENCE_METRIC_ENABLED: bool = os.getenv("COHERENCE_METRIC_ENABLED", "false").lower() == "true"
    COHERENCE_ALPHA_FRONTIER: float = float(os.getenv("COHERENCE_ALPHA_FRONTIER", "0.6"))  # Weight for frontier similarity
    COHERENCE_ALPHA_STRIDE: float = float(os.getenv("COHERENCE_ALPHA_STRIDE", "0.4"))  # Weight for stride relatedness
    COHERENCE_SMOOTHING_WINDOW: int = int(os.getenv("COHERENCE_SMOOTHING_WINDOW", "5"))  # Rolling average frames

    # E.7 Criticality Modes (classifies system state)
    CRITICALITY_MODES_ENABLED: bool = os.getenv("CRITICALITY_MODES_ENABLED", "false").lower() == "true"
    # Mode thresholds (see classify_criticality_mode logic)
    # subcritical: ρ < 0.9
    # flow: 0.9 <= ρ <= 1.1 and C >= 0.7
    # generative_overflow: ρ > 1.1 and C >= 0.7
    # chaotic_racing: ρ > 1.1 and C < 0.4

    # E.8 Task-Adaptive Targets (adjusts ρ based on task context)
    TASK_ADAPTIVE_TARGETS_ENABLED: bool = os.getenv("TASK_ADAPTIVE_TARGETS_ENABLED", "false").lower() == "true"
    TASK_CONTEXT_HYSTERESIS_FRAMES: int = int(os.getenv("TASK_CONTEXT_HYSTERESIS_FRAMES", "5"))  # Frames before switching context

    # Task context target tables (ρ targets by inferred context)
    TASK_CONTEXT_TARGETS: dict = {
        "explore": 1.05,       # Slightly supercritical for exploration
        "implement": 0.95,     # Subcritical for focused execution
        "consolidate": 0.85,   # Lower for memory consolidation
        "rest": 0.70,          # Very low for idle/rest
        "unknown": 1.0         # Default critical state
    }

    TASK_CONTEXT_TOLERANCES: dict = {
        "explore": 0.10,
        "implement": 0.05,
        "consolidate": 0.08,
        "rest": 0.15,
        "unknown": 0.10
    }

    # === Safe Mode (Operational Resilience) ===
    # Automatic degradation when tripwires fire
    # Per SCRIPT_MAP.md operational resilience requirements

    SAFE_MODE_ENABLED: bool = os.getenv("SAFE_MODE_ENABLED", "false").lower() == "true"  # Disabled - Safe Mode broken (kills engines instead of degrading)

    # Tripwire thresholds (how many violations before entering Safe Mode)
    SAFE_MODE_VIOLATION_THRESHOLD: int = int(os.getenv("SAFE_MODE_VIOLATION_THRESHOLD", "3"))  # Violations within window
    SAFE_MODE_VIOLATION_WINDOW_S: int = int(os.getenv("SAFE_MODE_VIOLATION_WINDOW_S", "60"))  # Rolling window

    # Safe Mode overrides (env-driven instant apply)
    # These values replace normal settings when Safe Mode activates
    SAFE_MODE_HARD_EXIT: bool = os.getenv("SAFE_MODE_HARD_EXIT", "false").lower() == "true"

    SAFE_MODE_OVERRIDES: dict = {
        # Reduce activation rate
        "ALPHA_TICK_MULTIPLIER": float(os.getenv("SAFE_MODE_ALPHA_TICK_MULT", "0.3")),  # 70% reduction

        # Cap time delta
        "DT_CAP": float(os.getenv("SAFE_MODE_DT_CAP", "1.0")),  # 1s max

        # Disable risky features
        "TOPK_SPLIT": False,  # No splitting
        "TWO_SCALE_TOPK_ENTITIES": 1,  # Single entity only
        "FANOUT_STRATEGY": "selective",  # Top-1 only

        # Disable all affective couplings
        "AFFECTIVE_THRESHOLD_ENABLED": False,
        "AFFECTIVE_MEMORY_ENABLED": False,
        "AFFECTIVE_RESPONSE_V2": False,
        "IDENTITY_MULTIPLICITY_ENABLED": False,
        "CONSOLIDATION_ENABLED": False,
        "DECAY_RESISTANCE_ENABLED": False,
        "DIFFUSION_STICKINESS_ENABLED": False,
        "AFFECTIVE_PRIMING_ENABLED": False,
        "COHERENCE_METRIC_ENABLED": False,
        "CRITICALITY_MODES_ENABLED": False,
        "TASK_ADAPTIVE_TARGETS_ENABLED": False,

        # Increase sampling for diagnosis
        "TELEMETRY_SAMPLE_RATE": 1.0,  # Emit all events
    }

    # Tripwire types (what can trigger Safe Mode)
    TRIPWIRE_CONSERVATION_EPSILON: float = float(os.getenv("TRIPWIRE_CONSERVATION_EPS", "0.001"))  # Energy conservation tolerance
    TRIPWIRE_CRITICALITY_UPPER: float = float(os.getenv("TRIPWIRE_CRITICALITY_UPPER", "1.3"))  # rho > this = chaotic
    TRIPWIRE_CRITICALITY_LOWER: float = float(os.getenv("TRIPWIRE_CRITICALITY_LOWER", "0.7"))  # rho < this = dying
    TRIPWIRE_CRITICALITY_FRAMES: int = int(os.getenv("TRIPWIRE_CRITICALITY_FRAMES", "10"))  # Consecutive frames out of band
    TRIPWIRE_FRONTIER_PCT: float = float(os.getenv("TRIPWIRE_FRONTIER_PCT", "0.3"))  # Frontier > 30% of graph
    TRIPWIRE_FRONTIER_FRAMES: int = int(os.getenv("TRIPWIRE_FRONTIER_FRAMES", "20"))  # Consecutive frames over threshold
    TRIPWIRE_MISSING_EVENTS_FRAMES: int = int(os.getenv("TRIPWIRE_MISSING_EVENTS", "5"))  # Missing frame.end events

    # Health monitoring
    HEALTH_CHECK_INTERVAL_S: int = int(os.getenv("HEALTH_CHECK_INTERVAL_S", "30"))  # Service health check frequency
    HEALTH_CHECK_TIMEOUT_S: float = float(os.getenv("HEALTH_CHECK_TIMEOUT_S", "5.0"))  # Health endpoint timeout
    HEALTH_CHECK_FAILURES_THRESHOLD: int = int(os.getenv("HEALTH_CHECK_FAILURES_THRESHOLD", "3"))  # Failures before action

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set for embedding service")

    @classmethod
    def get_citizen_graph_name(cls, citizen_name: str) -> str:
        """
        Get N1 graph name for a citizen.

        CORRECT FORMAT: ecosystem_mind-protocol_{citizen_name}
        WRONG FORMAT: citizen_{citizen_name}
        """
        return f"ecosystem_mind-protocol_{citizen_name.lower()}"


# Singleton instance
settings = Settings()
