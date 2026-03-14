"""Value cascade computation rules for L4 work trust updates."""

from dataclasses import dataclass
from math import log

VALUE_CASCADE_BASE = 0.01
PEER_WEIGHT = 0.1
NETWORK_DIVERSITY_WEIGHT = 1.0
HUMAN_PARTNER_SIGNAL_WEIGHT = 0.2


@dataclass(frozen=True)
class ValueCascadeInputs:
    scale: float
    attention_count: int
    usage_count: int
    peer_validations: int
    network_score: float


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def compute_value_cascade_delta(inputs: ValueCascadeInputs) -> float:
    scale = _clamp(inputs.scale, 1.0, 5.0)
    attention_multiplier = log(1 + max(0, inputs.attention_count))
    usage_multiplier = log(1 + max(0, inputs.usage_count))
    peer_multiplier = 1.0 + (PEER_WEIGHT * max(0, inputs.peer_validations))
    network_multiplier = 1.0 + (_clamp(inputs.network_score, 0.0, 2.0) * NETWORK_DIVERSITY_WEIGHT)

    return VALUE_CASCADE_BASE * scale * attention_multiplier * usage_multiplier * peer_multiplier * network_multiplier


def apply_human_partner_feedback(trust_score: float, feedback_signal: float) -> float:
    """Apply first-class human partner signal directly to trust."""
    delta = _clamp(feedback_signal, -1.0, 1.0) * HUMAN_PARTNER_SIGNAL_WEIGHT
    return max(0.0, trust_score + delta)
