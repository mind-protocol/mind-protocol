"""
Emotion Coloring Mechanism

Implements bounded, decaying emotion metadata for nodes and links during traversal.
Emotion is SEPARATE from activation energy and weights - affects cost only, not dynamics.

Algorithm (spec: emotion_coloring.md):
- Coloring: E_emo ← clip(α·E_emo + β·g·A, ||·|| ≤ M)
- Decay: E_emo ← λ^Δt · E_emo
- Gates: Complementarity (opposites) and Resonance (similarity) modulate cost

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/emotion/emotion_coloring.md
"""

import random
import numpy as np
from typing import Any, Dict, List, Optional, Sequence, Tuple
from dataclasses import dataclass

# Import existing affect extraction (Q2 - reuse canonical source)
from orchestration.mechanisms.valence import AffectVector

# Import settings
from orchestration.core.settings import settings

# Import event emitter
from orchestration.adapters.ws.traversal_event_emitter import EmotionDelta, TraversalEventEmitter


# === Affect Extraction (Q2: Canonical source) ===

def extract_entity_affect(description: str) -> np.ndarray:
    """
    Extract affect vector from entity description.

    Reuses valence.AffectVector as canonical source, normalized to [0,1] magnitude.

    Args:
        description: Entity description text

    Returns:
        Affect vector A ∈ ℝ^2, ||A|| ∈ [0,1]
        Format: [valence, arousal]
    """
    # Use existing extractor (keyword-based Phase 1 heuristic)
    raw_affect = AffectVector.extract_affect(description)

    # Normalize to [0, 1] magnitude
    magnitude = float(np.linalg.norm(raw_affect))
    if magnitude < 1e-9:
        return raw_affect  # Neutral, no coloring

    # Normalize direction
    direction = raw_affect / magnitude

    # Clip magnitude to [0, 1]
    intensity = max(0.0, min(magnitude, 1.0))

    return direction * intensity


# === Coloring Core (§5.2) ===

@dataclass
class ColoringContext:
    """
    Context for emotion coloring during traversal.

    Args:
        active_entity_affect: Cached affect vector for active entity (A)
        elapsed_on_elem_ms: Time spent on this element (for dwell gating)
        emitter: Event emitter for observability
        settings: Settings instance with emotion config
    """
    active_entity_affect: np.ndarray
    elapsed_on_elem_ms: float
    emitter: Optional[TraversalEventEmitter]
    tick_count: int = 0

    def zeros_affect(self) -> np.ndarray:
        """Return neutral affect vector."""
        return np.array([0.0, 0.0])

    def rand(self) -> float:
        """Random value for sampling."""
        return random.random()


def cap_for(elem: Any, node_type: Optional[str] = None) -> float:
    """
    Get emotion magnitude cap for element.

    Uses settings EMOTION_CAPS with optional schema override.

    Args:
        elem: Node or link object
        node_type: Optional node type override

    Returns:
        Magnitude cap M ∈ (0, 1]
    """
    # Get type from element or parameter
    if node_type is None:
        if hasattr(elem, 'node_type'):
            node_type = elem.node_type.value if hasattr(elem.node_type, 'value') else str(elem.node_type)
        else:
            node_type = "Link"  # Assume link if no node_type

    # Check for schema override (tighter cap)
    if hasattr(elem, 'meta') and hasattr(elem.meta, 'emotion_cap'):
        schema_cap = elem.meta.emotion_cap
        settings_cap = settings.EMOTION_CAPS.get(node_type, settings.EMOTION_CAPS["default"])
        return min(schema_cap, settings_cap)

    # Use settings cap
    return settings.EMOTION_CAPS.get(node_type, settings.EMOTION_CAPS["default"])


def top_k_axes(vector: np.ndarray, k: int = 2) -> List[Tuple[str, float]]:
    """
    Extract top K emotion axes from vector.

    Args:
        vector: Emotion vector [valence, arousal]
        k: Number of top axes to return

    Returns:
        List of (axis_name, value) tuples sorted by absolute magnitude
    """
    # For 2D affect: valence and arousal
    axes = [
        ("valence", float(vector[0])),
        ("arousal", float(vector[1])) if len(vector) > 1 else ("arousal", 0.0)
    ]

    # Sort by absolute magnitude
    axes.sort(key=lambda x: abs(x[1]), reverse=True)

    return axes[:k]


def color_element(
    elem: Any,
    A: np.ndarray,
    ctx: ColoringContext
) -> None:
    """
    Color element's emotion vector with entity affect (EMA with caps).

    METADATA ONLY - does not alter activation energy or weights.

    Algorithm (§5.2):
        E_emo ← clip(α·E_emo + β·g·A, ||·|| ≤ M)

    Where:
        α = retention (EMOTION_ALPHA ≈ 0.98)
        β = coloring rate (EMOTION_BETA ≈ 0.10)
        g = gating factor from dwell time
        M = per-type magnitude cap
        A = entity affect vector

    Args:
        elem: Node or Link object to color
        A: Entity affect vector (from extract_entity_affect)
        ctx: ColoringContext with gating and emission

    Side effects:
        - Updates elem.emotion_vector in place
        - Emits sampled emotion delta via ctx.emitter
    """
    # Dwell gate: skip if not enough time on element
    if ctx.elapsed_on_elem_ms < settings.EMOTION_DWELL_MIN_MS:
        return

    # Get current emotion (or initialize to neutral)
    if not hasattr(elem, 'emotion_vector') or elem.emotion_vector is None:
        elem.emotion_vector = ctx.zeros_affect()

    E_emo = elem.emotion_vector

    # EMA parameters
    alpha = settings.EMOTION_ALPHA
    beta = settings.EMOTION_BETA

    # Gating factor g (simplified - could add attention, entity energy)
    # For now: g = 1.0 if dwell threshold met (already checked above)
    g = 1.0

    # EMA update
    new = alpha * E_emo + beta * g * A

    # Cap magnitude with hysteresis (§5.2)
    cap = cap_for(elem)
    mag = float(np.linalg.norm(new))

    if mag > cap:
        # Apply cap with small hysteresis (avoid flicker at boundary)
        hysteresis = 0.02
        if mag > cap + hysteresis:
            new *= (cap / (mag + 1e-9))

    # Update element
    elem.emotion_vector = new

    # Sample emission for observability (§7.1)
    if ctx.emitter and ctx.rand() < settings.EMOTION_COLOR_SAMPLE_RATE:
        elem_id = elem.id if hasattr(elem, 'id') else str(elem)
        ctx.emitter.node_emotion_update([EmotionDelta(
            id=elem_id,
            mag=float(np.linalg.norm(new)),
            top_axes=top_k_axes(new, k=2)
        )])


# === Decay Phase (§5.3) ===

@dataclass
class DecayMetrics:
    """
    Metrics from emotion decay tick.

    Args:
        elements_decayed: Count of elements decayed
        mean_magnitude: Mean emotion magnitude after decay
        max_magnitude: Max emotion magnitude after decay
    """
    elements_decayed: int
    mean_magnitude: float
    max_magnitude: float


def emotion_decay(
    graph: Any,
    dt: float,
    decay_rate: Optional[float] = None
) -> DecayMetrics:
    """
    Apply exponential decay to all emotion vectors in graph.

    Algorithm (§5.3):
        E_emo ← λ^Δt · E_emo
        where λ = exp(-η_emo), η_emo ≪ η_act

    Emotion decays SLOWER than activation to provide lasting context.

    Args:
        graph: Graph object with nodes and links
        dt: Time delta (tick interval in seconds)
        decay_rate: Optional override for η_emo (default from settings)

    Returns:
        DecayMetrics with count and magnitude stats
    """
    if decay_rate is None:
        decay_rate = settings.EMOTION_DECAY_RATE

    # Compute decay factor λ^Δt
    lambda_base = np.exp(-decay_rate)
    lambda_dt = lambda_base ** dt

    elements_decayed = 0
    magnitudes = []

    # Decay nodes
    for node in graph.nodes.values():
        if hasattr(node, 'emotion_vector') and node.emotion_vector is not None:
            node.emotion_vector = lambda_dt * node.emotion_vector
            mag = float(np.linalg.norm(node.emotion_vector))
            magnitudes.append(mag)
            elements_decayed += 1

    # Decay links
    for link in graph.links.values():
        if hasattr(link, 'emotion_vector') and link.emotion_vector is not None:
            link.emotion_vector = lambda_dt * link.emotion_vector
            mag = float(np.linalg.norm(link.emotion_vector))
            magnitudes.append(mag)
            elements_decayed += 1

    # Compute metrics
    mean_mag = np.mean(magnitudes) if magnitudes else 0.0
    max_mag = max(magnitudes) if magnitudes else 0.0

    return DecayMetrics(
        elements_decayed=elements_decayed,
        mean_magnitude=float(mean_mag),
        max_magnitude=float(max_mag)
    )


# === Cost Gates (Complementarity & Resonance) ===

def resonance_multiplier(
    entity_affect: np.ndarray,
    link_emotion: np.ndarray
) -> Tuple[float, float]:
    """
    Compute resonance cost multiplier (coherence via similarity).

    Formula (spec: emotion-weighted traversal §2.1):
        r = cos(A, E_emo) ∈ [-1, 1]
        m_res = exp(-λ_res * r)

    - r > 0 (aligned) → m_res < 1 (attractive, easier)
    - r = 0 (orthogonal) → m_res = 1 (neutral)
    - r < 0 (clash) → m_res > 1 (repulsive, harder)

    Clamped to [RES_MIN_MULT, RES_MAX_MULT] for stability.

    Args:
        entity_affect: Entity affect vector A
        link_emotion: Link emotion vector E_emo

    Returns:
        Tuple of (multiplier, resonance_score)
        - multiplier ∈ [RES_MIN_MULT, RES_MAX_MULT]
        - resonance_score r ∈ [-1, 1]
    """
    # Cosine similarity
    norm_entity = np.linalg.norm(entity_affect)
    norm_link = np.linalg.norm(link_emotion)

    if norm_entity < 1e-9 or norm_link < 1e-9:
        return 1.0, 0.0  # Neutral if either is zero

    cos_sim = np.dot(entity_affect, link_emotion) / (norm_entity * norm_link)
    resonance_score = float(np.clip(cos_sim, -1.0, 1.0))

    # Exponential multiplier (FULL RANGE - not max(0, r))
    mult = np.exp(-settings.RES_LAMBDA * resonance_score)

    # Clamp to bounds
    mult_clamped = float(np.clip(mult, settings.RES_MIN_MULT, settings.RES_MAX_MULT))

    return mult_clamped, resonance_score


def complementarity_multiplier(
    entity_affect: np.ndarray,
    link_emotion: np.ndarray,
    intensity_gate: float = 1.0,
    context_gate: float = 1.0
) -> float:
    """
    Compute complementarity cost multiplier (regulation via opposites).

    Formula (spec: emotion complementarity):
        m_comp = exp(-λ_comp * max(0, -cos(A, E_emo)) * g_int * g_ctx)

    High opposition → lower multiplier → lower cost (regulatory pull).
    Intensity and context gates modulate the effect.

    Args:
        entity_affect: Entity affect vector A
        link_emotion: Link emotion vector E_emo
        intensity_gate: Intensity gate g_int (0-1)
        context_gate: Context gate g_ctx (0-1)

    Returns:
        Cost multiplier ∈ [COMP_MIN_MULT, COMP_MAX_MULT]
    """
    # Cosine similarity
    norm_entity = np.linalg.norm(entity_affect)
    norm_link = np.linalg.norm(link_emotion)

    if norm_entity < 1e-9 or norm_link < 1e-9:
        return 1.0  # Neutral if either is zero

    cos_sim = np.dot(entity_affect, link_emotion) / (norm_entity * norm_link)
    cos_sim = np.clip(cos_sim, -1.0, 1.0)

    # Complementarity: negative similarity (opposites) reduces cost
    comp_score = max(0.0, -cos_sim)

    # Apply gates
    gated_score = comp_score * intensity_gate * context_gate

    # Exponential multiplier
    mult = np.exp(-settings.COMP_LAMBDA * gated_score)

    # Clamp to bounds
    return float(np.clip(mult, settings.COMP_MIN_MULT, settings.COMP_MAX_MULT))
