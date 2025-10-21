"""
Stimulus Injection - Dynamic energy injection from external stimuli

Implements constant-free stimulus processing:
1. Entropy-coverage search (adaptive retrieval)
2. Budget calculation: B = gap_mass × f(ρ) × g(source)
3. Direction-aware distribution
4. Health modulation via isotonic regression
5. Source impact learning via flip yield tracking
6. Link-matched injection with direction priors
7. Peripheral amplification

Designer: Felix "Ironhand" - 2025-10-21
Enhanced by: Luca "Vellumhand" - 2025-10-21 (foundation layer features)
Reference: docs/specs/consciousness_engine_architecture/mechanisms/stimulus_injection_specification.md
"""

import numpy as np
from scipy.stats import norm, rankdata
from sklearn.isotonic import IsotonicRegression
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque, defaultdict
import logging
import time

# V1 mechanism modules
from orchestration.mechanisms.health_modulation import HealthModulator
from orchestration.mechanisms.source_impact import SourceImpactGate
from orchestration.mechanisms.peripheral_amplification import PeripheralAmplifier
from orchestration.mechanisms.entity_channels import EntityChannelSelector
from orchestration.mechanisms.direction_priors import DirectionPriorDistributor

logger = logging.getLogger(__name__)


@dataclass
class InjectionMatch:
    """Single match from vector search."""
    item_id: str
    item_type: str  # 'node' or 'link'
    similarity: float  # Cosine similarity [0, 1]
    current_energy: float
    threshold: float
    gap: float  # max(0, threshold - energy)

    # Link-specific fields (only for item_type='link')
    source_id: Optional[str] = None
    target_id: Optional[str] = None
    precedence_forward: Optional[float] = None  # Causal credit for forward direction
    precedence_backward: Optional[float] = None  # Causal credit for backward direction
    source_energy: Optional[float] = None
    target_energy: Optional[float] = None
    source_threshold: Optional[float] = None
    target_threshold: Optional[float] = None


@dataclass
class InjectionResult:
    """Result of stimulus injection."""
    total_budget: float
    items_injected: int
    total_energy_injected: float

    # Breakdown
    gap_mass: float
    health_factor: float  # f(ρ)
    source_factor: float  # g(source)
    peripheral_factor: float  # 1 + max(0, z_align)

    # Entropy coverage
    entropy: float
    coverage_target: float
    matches_selected: int

    # Observability
    nodes_injected: int = 0
    links_injected: int = 0
    flips_caused: int = 0  # Nodes that crossed threshold

    # Per-item injections
    injections: List[Dict[str, Any]] = field(default_factory=list)  # [{item_id, delta_energy}, ...]


class StimulusInjector:
    """
    Implements dynamic stimulus injection with entropy-coverage search.

    Core: Entropy-based adaptive retrieval + gap-weighted budget distribution
    Foundation: Health modulation, source learning, link injection, peripheral amplification
    Entity layer (TODO): Entity-aware injection channels
    """

    def __init__(self):
        """
        Initialize stimulus injector with V1 mechanisms.
        """

        # V1 Mechanisms
        self.health_modulator = HealthModulator(
            history_size=1000,
            min_samples=200
        )

        self.source_impact_gate = SourceImpactGate(
            window_seconds=604800.0,  # 1 week
            min_samples=50
        )

        self.peripheral_amplifier = PeripheralAmplifier(
            cohort_size=100,
            min_cohort=20
        )

        self.entity_selector = EntityChannelSelector(
            window_size=100,
            min_samples=20
        )

        self.direction_distributor = DirectionPriorDistributor()

        # Feature flags
        self.health_modulation_enabled = True
        self.source_impact_enabled = True
        self.peripheral_amplification_enabled = True
        self.link_injection_enabled = True
        self.entity_channels_enabled = False  # V1: Simplified to single entity

        # Frame counter for diagnostics
        self.frame_count = 0

        logger.info(
            f"[StimulusInjector] Initialized V1 with mechanisms: "
            f"health_modulation, source_impact, peripheral_amplification, direction_priors"
        )

    def inject(
        self,
        stimulus_embedding: np.ndarray,
        matches: List[InjectionMatch],
        source_type: str = "user_message",
        rho_proxy: Optional[float] = None,
        context_embeddings: Optional[List[np.ndarray]] = None
    ) -> InjectionResult:
        """
        Inject energy from stimulus into matched nodes.

        Args:
            stimulus_embedding: Embedding vector of stimulus chunk
            matches: Vector search results with similarity scores
            source_type: Type of stimulus source
            rho_proxy: Optional spectral radius proxy for health modulation
            context_embeddings: Optional S5/S6 context chunk embeddings

        Returns:
            InjectionResult with budget breakdown and per-item injections
        """

        # Step 1: Entropy-coverage search (adaptive retrieval)
        entropy, coverage_target, selected = self._entropy_coverage_search(matches)

        logger.info(
            f"[StimulusInjector] Entropy-coverage: H={entropy:.2f}, "
            f"ĉ={coverage_target:.2f}, selected {len(selected)}/{len(matches)} matches"
        )

        # Step 2: Budget calculation
        gap_mass = self._compute_gap_mass(selected)
        f_rho = self._health_modulation(rho_proxy)
        g_source = self._source_impact_gate(source_type)

        budget_base = gap_mass * f_rho * g_source

        # Step 3: Peripheral amplification (optional)
        alpha = 0.0
        if context_embeddings and self.peripheral_amplification_enabled:
            alpha = self._peripheral_alignment(stimulus_embedding, context_embeddings)
            budget = budget_base * (1 + alpha)
            logger.debug(f"[StimulusInjector] Peripheral amplification: α={alpha:.2f}, budget×{(1+alpha):.2f}")
        else:
            budget = budget_base

        logger.info(
            f"[StimulusInjector] Budget: sim_mass={gap_mass:.2f}, "
            f"f(ρ)={f_rho:.2f}, g({source_type})={g_source:.2f} → B={budget:.2f}"
        )

        # Step 4: Distribute budget across selected matches
        injections = self._distribute_budget(budget, selected)

        total_injected = sum(inj['delta_energy'] for inj in injections)

        logger.info(f"[StimulusInjector] Injected {total_injected:.2f} energy into {len(injections)} items")

        # Increment frame counter
        self.frame_count += 1

        return InjectionResult(
            total_budget=budget,
            items_injected=len(injections),
            total_energy_injected=total_injected,
            gap_mass=gap_mass,
            health_factor=f_rho,
            source_factor=g_source,
            peripheral_factor=(1 + alpha),
            entropy=entropy,
            coverage_target=coverage_target,
            matches_selected=len(selected),
            injections=injections
        )

    def _entropy_coverage_search(
        self,
        matches: List[InjectionMatch]
    ) -> Tuple[float, float, List[InjectionMatch]]:
        """
        Adaptive retrieval via entropy-coverage.

        Replaces fixed top-K with data-derived selection:
        - Specific queries (low entropy) → few matches
        - Broad queries (high entropy) → many matches

        Args:
            matches: All vector search results

        Returns:
            (entropy, coverage_target, selected_matches)
        """
        if not matches:
            return 0.0, 0.0, []

        # Extract similarities
        similarities = np.array([m.similarity for m in matches])

        # Normalize to probabilities
        total_sim = similarities.sum()
        if total_sim == 0:
            # All zeros - select none
            return 0.0, 0.0, []

        probabilities = similarities / total_sim

        # Compute Shannon entropy
        # H = -Σ p_i · log(p_i)
        entropy = -np.sum(probabilities * np.log(probabilities + 1e-10))

        # Coverage target: ĉ = 1 - exp(-H)
        coverage_target = 1.0 - np.exp(-entropy)

        # Sort matches by similarity (descending)
        sorted_matches = sorted(matches, key=lambda m: m.similarity, reverse=True)

        # Select prefix until coverage target reached
        selected = []
        cumulative_mass = 0.0

        for match in sorted_matches:
            selected.append(match)
            cumulative_mass += match.similarity / total_sim

            if cumulative_mass >= coverage_target:
                break

        logger.debug(
            f"[StimulusInjector] Entropy={entropy:.2f} → coverage={coverage_target:.2f} "
            f"→ selected {len(selected)} matches (cumulative mass={cumulative_mass:.2f})"
        )

        return entropy, coverage_target, selected

    def _compute_gap_mass(self, matches: List[InjectionMatch]) -> float:
        """
        Compute similarity mass: Σ s_m

        Total relevance across all matches (no gap constraint).
        Renamed from gap_mass but kept method name for backward compatibility.

        Args:
            matches: Selected matches

        Returns:
            Similarity mass (total relevance)
        """
        similarity_mass = sum(m.similarity for m in matches)

        logger.debug(f"[StimulusInjector] Similarity mass: {similarity_mass:.2f} from {len(matches)} matches")

        return similarity_mass

    def _health_modulation(
        self,
        rho_proxy: Optional[float] = None
    ) -> float:
        """
        Health modulation factor f(ρ).

        Damps injection when supercritical, boosts when subcritical.

        Uses HealthModulator with isotonic regression learning.

        Args:
            rho_proxy: Spectral radius proxy (optional, defaults to 0 if not provided)

        Returns:
            Modulation factor f(ρ) ∈ [0.5, 1.5]
        """
        if not self.health_modulation_enabled:
            return 1.0

        # Use provided rho_proxy or default to neutral
        if rho_proxy is None:
            # No graph stats available - neutral modulation
            return 1.0

        # Apply health modulation
        f_rho = self.health_modulator.modulate(rho_proxy)

        return f_rho

    def _source_impact_gate(self, source_type: str) -> float:
        """
        Source impact gate g(source).

        Learns which stimulus sources are most effective via flip yield tracking.

        Uses SourceImpactGate with rank normalization to [0.5, 1.5].

        Args:
            source_type: Type of stimulus source

        Returns:
            Modulation factor g(source) ∈ [0.5, 1.5]
        """
        if not self.source_impact_enabled:
            return 1.0

        # Apply source impact modulation
        g_source = self.source_impact_gate.modulate(source_type)

        return g_source

    def _peripheral_alignment(
        self,
        stimulus_embedding: np.ndarray,
        context_embeddings: Optional[List[np.ndarray]] = None
    ) -> float:
        """
        Peripheral alignment z-score.

        Computes alignment with S5/S6 context and z-score normalizes within cohort.

        Uses PeripheralAmplifier with context similarity + z-score normalization.

        Args:
            stimulus_embedding: Embedding of stimulus
            context_embeddings: Optional S5/S6 context chunk embeddings

        Returns:
            Amplification factor α = max(0, z_alignment) ≥ 0
        """
        if not self.peripheral_amplification_enabled:
            return 0.0

        # Apply peripheral amplification
        alpha = self.peripheral_amplifier.amplify(
            stimulus_embedding,
            context_embeddings,
            timestamp=time.time()
        )

        return alpha

    def _distribute_budget(
        self,
        budget: float,
        matches: List[InjectionMatch]
    ) -> List[Dict[str, Any]]:
        """
        Distribute budget across matches proportional to similarity only.

        No gap constraint - nodes can accumulate energy indefinitely.

        Args:
            budget: Total energy budget to distribute
            matches: Selected matches

        Returns:
            List of injections: [{item_id, delta_energy, new_energy}, ...]
        """
        if budget <= 0 or not matches:
            return []

        # Compute weights: similarity only (no gap constraint)
        weights = np.array([m.similarity for m in matches])
        total_weight = weights.sum()

        if total_weight == 0:
            # All similarities zero - nothing to inject
            logger.debug("[StimulusInjector] All similarities zero, no injection")
            return []

        injections = []

        for match, weight in zip(matches, weights):
            # Proportional allocation
            delta_energy = budget * (weight / total_weight)

            # No cap - energy accumulates indefinitely
            new_energy = match.current_energy + delta_energy

            injections.append({
                'item_id': match.item_id,
                'item_type': match.item_type,
                'delta_energy': delta_energy,
                'current_energy': match.current_energy,
                'new_energy': new_energy,
                'threshold': match.threshold,
                'similarity': match.similarity,
                'weight': weight
            })

            logger.debug(
                f"[StimulusInjector] {match.item_id}: "
                f"E={match.current_energy:.2f} + ΔE={delta_energy:.2f} "
                f"= {new_energy:.2f} (sim={match.similarity:.2f})"
            )

        return injections

    # =========================================================================
    # Learning Observations
    # =========================================================================

    def record_frame_result(
        self,
        result: InjectionResult,
        source_type: str,
        rho_proxy: Optional[float] = None,
        max_degree: Optional[int] = None,
        avg_weight: Optional[float] = None,
        active_node_count: Optional[int] = None,
        activation_entropy: Optional[float] = None,
        overflow_occurred: bool = False,
        num_flips: Optional[int] = None
    ):
        """
        Record frame result for learning mechanisms.

        Call this after injection completes and graph is updated with new energies.

        Args:
            result: InjectionResult from inject()
            source_type: Type of stimulus source
            rho_proxy: Spectral radius proxy (or compute from max_degree/avg_weight/active_node_count)
            max_degree: Max node outgoing degree
            avg_weight: Average link weight
            active_node_count: Number of active nodes
            activation_entropy: Shannon entropy of active node distribution
            overflow_occurred: Whether hard limits were hit
            num_flips: Number of threshold crossings (or compute from result.injections)
        """
        timestamp = time.time()

        # Compute rho_proxy if not provided
        if rho_proxy is None and all(x is not None for x in [max_degree, avg_weight, active_node_count]):
            rho_proxy = self.health_modulator.compute_rho_proxy(
                max_degree, avg_weight, active_node_count
            )

        # Compute num_flips if not provided (count nodes that crossed threshold)
        if num_flips is None:
            num_flips = sum(
                1 for inj in result.injections
                if inj['new_energy'] >= inj['threshold'] and inj['current_energy'] < inj['threshold']
            )

        # Record for HealthModulator
        if rho_proxy is not None and activation_entropy is not None:
            self.health_modulator.add_observation(
                rho_proxy=rho_proxy,
                num_flips=num_flips,
                budget_spent=result.total_budget,
                activation_entropy=activation_entropy,
                overflow_occurred=overflow_occurred,
                timestamp=timestamp
            )

        # Record for SourceImpactGate
        self.source_impact_gate.add_observation(
            source_type=source_type,
            num_flips=num_flips,
            budget_spent=result.total_budget,
            timestamp=timestamp
        )

        logger.debug(
            f"[StimulusInjector] Recorded frame result: "
            f"flips={num_flips}, budget={result.total_budget:.2f}, source={source_type}"
        )

    def get_stats(self) -> dict:
        """Get statistics from all learning mechanisms."""
        return {
            "frame_count": self.frame_count,
            "health_modulator": self.health_modulator.get_stats(),
            "source_impact": self.source_impact_gate.get_stats(),
            "peripheral_amplifier": self.peripheral_amplifier.get_stats(),
            "entity_selector": self.entity_selector.get_stats(),
            "direction_distributor": self.direction_distributor.get_stats()
        }

    # =========================================================================
    # Feature Toggles (for compatibility)
    # =========================================================================

    def enable_health_modulation(self):
        """Enable health modulation f(ρ) learning."""
        self.health_modulation_enabled = True
        logger.info("[StimulusInjector] Health modulation ENABLED")

    def enable_source_impact_learning(self):
        """Enable source impact g(source) learning."""
        self.source_impact_enabled = True
        logger.info("[StimulusInjector] Source impact learning ENABLED")

    def enable_entity_channels(self):
        """Enable entity-aware injection."""
        self.entity_channels_enabled = True
        logger.info("[StimulusInjector] Entity channels ENABLED")

    def enable_peripheral_amplification(self):
        """Enable S5/S6 peripheral amplification."""
        self.peripheral_amplification_enabled = True
        logger.info("[StimulusInjector] Peripheral amplification ENABLED")


def create_match(
    item_id: str,
    item_type: str,
    similarity: float,
    current_energy: float,
    threshold: float
) -> InjectionMatch:
    """Helper to create InjectionMatch (gap field kept for backward compatibility but unused)."""
    # Gap no longer used - nodes can accumulate energy indefinitely
    gap = 0.0  # Placeholder only

    return InjectionMatch(
        item_id=item_id,
        item_type=item_type,
        similarity=similarity,
        current_energy=current_energy,
        threshold=threshold,
        gap=gap
    )
