"""
State Variables - Arousal, Goal Alignment, and Precision

Computes neuromodulatory state variables that modulate MEMBER_OF edge weights at runtime.

State variables:
- arousal: LC/NE-like global activation (0-1)
- goal_alignment: Intent focus strength (0-1)
- precision: Prediction confidence (0-1)

These variables control state-dependent effective weight computation:
- High arousal → amplify w_affect (emotional routing)
- High goal_alignment → amplify w_intent (task-directed routing)
- High precision → amplify w_semantic (semantic coherence routing)

Author: Felix (Core Consciousness Engineer)
Date: 2025-10-29
Spec: docs/specs/v2/subentity_layer/state_dependent_weight_modulation.md
"""

import time
import numpy as np
from typing import Dict, Optional, Any, List
from dataclasses import dataclass


@dataclass
class StateVariables:
    """
    Current state variables for effective weight modulation.

    All values normalized to [0, 1].
    """
    arousal: float                   # Global activation level (LC/NE proxy)
    goal_alignment: float            # Intent focus strength
    precision: float                 # Prediction confidence

    # Component factors (for telemetry)
    energy_norm: float = 0.0         # Normalized mean energy
    valence_extremity: float = 0.0   # |valence| magnitude
    energy_rate: float = 0.0         # Temporal energy gradient
    intent_strength: float = 0.0     # ||intent|| magnitude
    intent_stability: float = 0.0    # Low variance = stable
    wm_coherence: float = 0.0        # Working memory alignment
    prediction_error: float = 0.0    # From predictive coding
    entropy: float = 0.0             # Energy distribution entropy
    temporal_stability: float = 0.0  # Low energy variance = stable

    # Metadata
    timestamp: float = 0.0
    frame_id: int = 0
    citizen_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for telemetry."""
        return {
            'arousal': round(self.arousal, 3),
            'goal_alignment': round(self.goal_alignment, 3),
            'precision': round(self.precision, 3),
            'components': {
                'energy_norm': round(self.energy_norm, 3),
                'valence_extremity': round(self.valence_extremity, 3),
                'energy_rate': round(self.energy_rate, 3),
                'intent_strength': round(self.intent_strength, 3),
                'intent_stability': round(self.intent_stability, 3),
                'wm_coherence': round(self.wm_coherence, 3),
                'prediction_error': round(self.prediction_error, 3),
                'entropy': round(self.entropy, 3),
                'temporal_stability': round(self.temporal_stability, 3)
            },
            'timestamp': self.timestamp,
            'frame_id': self.frame_id,
            'citizen_id': self.citizen_id,
            'state_interpretation': self._interpret_state()
        }

    def _interpret_state(self) -> str:
        """Generate human-readable state interpretation."""
        if self.arousal > 0.7:
            if self.goal_alignment > 0.7:
                return "high_arousal_focused"  # Crisis mode, goal-directed
            else:
                return "high_arousal_exploratory"  # Excited, diffuse
        elif self.precision > 0.7:
            if self.goal_alignment > 0.7:
                return "high_precision_focused"  # Analytical, task-driven
            else:
                return "high_precision_exploratory"  # Confident exploration
        elif self.goal_alignment > 0.7:
            return "goal_driven_calm"  # Calm focus
        else:
            return "low_arousal_exploratory"  # Relaxed exploration


class StateVariableComputer:
    """
    Computes arousal, goal_alignment, and precision from graph state.

    Follows neuroscience grounding:
    - Arousal: Energy magnitude + valence extremity + temporal gradient
    - Goal alignment: Intent strength + stability + WM coherence
    - Precision: Inverse prediction error + low entropy + temporal stability
    """

    def __init__(self):
        # History for temporal calculations
        self.energy_history: List[float] = []
        self.intent_history: List[np.ndarray] = []
        self.history_window = 10  # Frames to track

        # Previous frame state
        self.prev_total_energy: float = 0.0
        self.prev_timestamp: float = time.time()

        # Telemetry
        self.computations: int = 0

    def compute_state_variables(
        self,
        graph: 'Graph',
        intent: Optional[np.ndarray] = None,
        prediction_error: float = 0.5,
        citizen_id: str = "default",
        frame_id: int = 0
    ) -> StateVariables:
        """
        Compute all state variables from current graph state.

        Args:
            graph: Graph with nodes, energies, and thresholds
            intent: Current intent vector (optional)
            prediction_error: Prediction error from predictive coding (0-1)
            citizen_id: Citizen ID for telemetry
            frame_id: Current frame ID

        Returns:
            StateVariables with arousal, goal_alignment, precision
        """
        self.computations += 1
        current_time = time.time()

        # Compute arousal
        arousal, arousal_components = self._compute_arousal(graph, current_time)

        # Compute goal alignment
        goal_alignment, goal_components = self._compute_goal_alignment(graph, intent)

        # Compute precision
        precision, precision_components = self._compute_precision(graph, prediction_error)

        # Create state variables
        state_vars = StateVariables(
            arousal=arousal,
            goal_alignment=goal_alignment,
            precision=precision,
            energy_norm=arousal_components['energy_norm'],
            valence_extremity=arousal_components['valence_extremity'],
            energy_rate=arousal_components['energy_rate'],
            intent_strength=goal_components['intent_strength'],
            intent_stability=goal_components['intent_stability'],
            wm_coherence=goal_components['wm_coherence'],
            prediction_error=prediction_error,
            entropy=precision_components['entropy'],
            temporal_stability=precision_components['temporal_stability'],
            timestamp=current_time,
            frame_id=frame_id,
            citizen_id=citizen_id
        )

        return state_vars

    def _compute_arousal(self, graph: 'Graph', current_time: float) -> tuple[float, Dict]:
        """
        Compute arousal from energy magnitude, valence extremity, and temporal gradient.

        High arousal = high energy + extreme valence + rapid changes

        Returns:
            (arousal, components_dict)
        """
        nodes = list(graph.nodes.values())
        if not nodes:
            return 0.5, {'energy_norm': 0.0, 'valence_extremity': 0.0, 'energy_rate': 0.0}

        # Global activation level (energy magnitude)
        total_energy = sum(node.E for node in nodes)
        energy_norm = total_energy / len(nodes)
        energy_norm = np.clip(energy_norm / 10.0, 0.0, 1.0)  # Normalize assuming max ~10

        # Valence extremity (intense emotions drive arousal)
        valences = [getattr(node, 'valence', 0.0) for node in nodes]
        valence_extremity = float(np.mean([abs(v) for v in valences]))
        valence_extremity = np.clip(valence_extremity, 0.0, 1.0)

        # Temporal gradient (energy change rate)
        dt = current_time - self.prev_timestamp if self.prev_timestamp > 0 else 0.1
        energy_delta = (total_energy - self.prev_total_energy) / max(dt, 0.01)
        energy_rate = abs(energy_delta) / max(total_energy, 0.01)
        energy_rate = np.clip(energy_rate, 0.0, 1.0)

        # Update history
        self.energy_history.append(total_energy)
        if len(self.energy_history) > self.history_window:
            self.energy_history.pop(0)

        self.prev_total_energy = total_energy
        self.prev_timestamp = current_time

        # Combine factors (spec: 0.3 × energy + 0.4 × valence + 0.3 × rate)
        arousal = np.clip(
            0.3 * energy_norm +
            0.4 * valence_extremity +
            0.3 * energy_rate,
            0.0, 1.0
        )

        components = {
            'energy_norm': energy_norm,
            'valence_extremity': valence_extremity,
            'energy_rate': energy_rate
        }

        return float(arousal), components

    def _compute_goal_alignment(
        self,
        graph: 'Graph',
        intent: Optional[np.ndarray]
    ) -> tuple[float, Dict]:
        """
        Compute goal alignment from intent strength, stability, and WM coherence.

        High goal_alignment = strong intent + stable intent + aligned WM

        Returns:
            (goal_alignment, components_dict)
        """
        if intent is None or len(intent) == 0:
            # No intent → exploratory mode (low goal alignment)
            return 0.3, {
                'intent_strength': 0.0,
                'intent_stability': 0.0,
                'wm_coherence': 0.0
            }

        # Intent vector magnitude
        intent_strength = float(np.linalg.norm(intent))
        intent_strength = np.clip(intent_strength, 0.0, 1.0)

        # Intent stability (low variance = stable goal)
        self.intent_history.append(intent)
        if len(self.intent_history) > self.history_window:
            self.intent_history.pop(0)

        if len(self.intent_history) >= 3:
            intent_magnitudes = [np.linalg.norm(i) for i in self.intent_history]
            intent_variance = float(np.var(intent_magnitudes))
            intent_stability = 1.0 / (1.0 + intent_variance)
        else:
            intent_stability = 0.5  # Default until history builds

        # Working memory coherence (active nodes align with intent)
        nodes = list(graph.nodes.values())
        active_nodes = [n for n in nodes if n.E > 0.5]

        if active_nodes:
            # Check if nodes have embeddings
            embeddings = []
            for node in active_nodes:
                if hasattr(node, 'embedding') and node.embedding is not None:
                    embeddings.append(node.embedding)

            if embeddings:
                # Compute alignment via cosine similarity
                intent_dots = []
                for emb in embeddings:
                    if len(emb) == len(intent):
                        dot = float(np.dot(emb, intent))
                        intent_dots.append(max(0, dot))  # Clamp negative to 0

                wm_coherence = float(np.mean(intent_dots)) if intent_dots else 0.0
                wm_coherence = np.clip(wm_coherence, 0.0, 1.0)
            else:
                wm_coherence = 0.5  # Default if no embeddings
        else:
            wm_coherence = 0.5  # Default if no active nodes

        # Combine factors (spec: 0.4 × strength + 0.3 × stability + 0.3 × coherence)
        goal_alignment = np.clip(
            0.4 * intent_strength +
            0.3 * intent_stability +
            0.3 * wm_coherence,
            0.0, 1.0
        )

        components = {
            'intent_strength': intent_strength,
            'intent_stability': intent_stability,
            'wm_coherence': wm_coherence
        }

        return float(goal_alignment), components

    def _compute_precision(
        self,
        graph: 'Graph',
        prediction_error: float
    ) -> tuple[float, Dict]:
        """
        Compute precision from prediction error, entropy, and temporal stability.

        High precision = low prediction error + low entropy + stable energy

        Returns:
            (precision, components_dict)
        """
        nodes = list(graph.nodes.values())
        if not nodes:
            return 0.7, {'entropy': 0.0, 'temporal_stability': 0.0}

        # Prediction error (inverse)
        precision_from_error = 1.0 - np.clip(prediction_error, 0.0, 1.0)

        # Energy distribution entropy (low entropy = focused, high precision)
        energies = np.array([node.E for node in nodes])
        energy_sum = np.sum(energies)

        if energy_sum > 1e-10:
            energy_probs = energies / energy_sum
            # Compute entropy
            entropy = -np.sum(energy_probs * np.log(energy_probs + 1e-10))
            max_entropy = np.log(len(nodes)) if len(nodes) > 1 else 1.0
            normalized_entropy = float(entropy / max_entropy)
        else:
            normalized_entropy = 1.0  # Max uncertainty if no energy

        precision_from_entropy = 1.0 - normalized_entropy

        # Temporal stability (low energy variance = stable state = high precision)
        if len(self.energy_history) >= 3:
            energy_variance = float(np.var(self.energy_history))
            precision_from_stability = 1.0 / (1.0 + energy_variance)
        else:
            precision_from_stability = 0.5  # Default until history builds

        # Combine factors (spec: 0.5 × error + 0.3 × entropy + 0.2 × stability)
        precision = np.clip(
            0.5 * precision_from_error +
            0.3 * precision_from_entropy +
            0.2 * precision_from_stability,
            0.0, 1.0
        )

        components = {
            'entropy': normalized_entropy,
            'temporal_stability': precision_from_stability
        }

        return float(precision), components

    def get_telemetry(self) -> Dict[str, Any]:
        """Get telemetry data for monitoring."""
        return {
            'computations': self.computations,
            'history_size': len(self.energy_history),
            'intent_history_size': len(self.intent_history)
        }
