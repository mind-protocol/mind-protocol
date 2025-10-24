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

    # PR-E.5: Affective Priming fields
    emotion_vector: Optional[np.ndarray] = None  # E_emo for affect alignment


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
    Subentity layer (TODO): Subentity-aware injection channels
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
        self.entity_channels_enabled = False  # V1: Simplified to single subentity

        # Frame counter for diagnostics
        self.frame_count = 0

        # PR-E.5: Affective Priming
        self.affective_priming_enabled = False  # Feature flag
        self.recent_affect = np.zeros(2)  # A_recent: [valence, arousal] EMA
        self.affect_ema_alpha = 0.1  # EMA smoothing factor (window ~20 frames)

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

        # Step 0 (PR-E.5): Apply affective priming
        matches_primed = self._apply_affective_priming(matches)

        # Step 1: Entropy-coverage search (adaptive retrieval)
        entropy, coverage_target, selected = self._entropy_coverage_search(matches_primed)

        logger.info(
            f"[StimulusInjector] Entropy-coverage: H={entropy:.2f}, "
            f"ĉ={coverage_target:.2f}, selected {len(selected)}/{len(matches)} matches"
        )

        # Step 2: Budget calculation (DUAL-CHANNEL: similarity-based, not gap-based)
        # In dual-channel architecture, budget represents total relevance, not deficit
        # Top-Up channel handles deficits internally; Amplifier needs budget regardless of gaps
        similarity_mass = sum(m.similarity for m in selected)

        # Debug: Log individual similarities
        if similarity_mass == 0 and len(selected) > 0:
            logger.warning(
                f"[StimulusInjector] sim_mass=0 with {len(selected)} selected matches. "
                f"First 5 similarities: {[m.similarity for m in selected[:5]]}"
            )

        f_rho = self._health_modulation(rho_proxy)
        g_source = self._source_impact_gate(source_type)

        budget_base = similarity_mass * f_rho * g_source

        # Step 3: Peripheral amplification (optional)
        alpha = 0.0
        if context_embeddings and self.peripheral_amplification_enabled:
            alpha = self._peripheral_alignment(stimulus_embedding, context_embeddings)
            budget = budget_base * (1 + alpha)
            logger.debug(f"[StimulusInjector] Peripheral amplification: α={alpha:.2f}, budget×{(1+alpha):.2f}")
        else:
            budget = budget_base

        # P1 HOTFIX: Budget floor to prevent starvation when vector search broken
        # If we have matches but budget is near-zero (vector search issues), guarantee minimum energy flow
        BUDGET_FLOOR = 0.15  # Minimum budget when non-empty stimulus and matches exist
        if len(matches_primed) > 0 and budget < BUDGET_FLOOR:
            budget_before = budget
            budget = BUDGET_FLOOR
            logger.warning(
                f"[StimulusInjector] HOTFIX: Budget floor applied ({budget_before:.4f} → {budget:.2f}) "
                f"to prevent starvation with {len(matches_primed)} matches"
            )

        logger.info(
            f"[StimulusInjector] Budget: sim_mass={similarity_mass:.2f}, "
            f"f(ρ)={f_rho:.2f}, g({source_type})={g_source:.2f} → B={budget:.2f}"
        )

        # Step 4: Distribute budget across selected matches (DUAL-CHANNEL)
        injections = self._distribute_budget_dual_channel(budget, selected)

        total_injected = sum(inj['delta_energy'] for inj in injections)

        logger.info(f"[StimulusInjector] Injected {total_injected:.2f} energy into {len(injections)} items")

        # Increment frame counter
        self.frame_count += 1

        return InjectionResult(
            total_budget=budget,
            items_injected=len(injections),
            total_energy_injected=total_injected,
            gap_mass=similarity_mass,  # Now represents similarity mass in dual-channel
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

        # Debug: Log similarity distribution
        logger.info(
            f"[StimulusInjector] Entropy-coverage input: {len(matches)} matches, "
            f"similarities: min={similarities.min():.3f}, max={similarities.max():.3f}, "
            f"mean={similarities.mean():.3f}, sum={similarities.sum():.3f}"
        )

        # Normalize to probabilities
        total_sim = similarities.sum()
        if total_sim == 0:
            # All zeros - select none
            logger.warning(f"[StimulusInjector] All {len(matches)} matches have similarity=0, selecting none")
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
        Compute gap mass: Σ s_m · max(0, Θ_m - E_m)

        Weighted sum of gaps by similarity - estimates useful work potential.

        Args:
            matches: Selected matches

        Returns:
            Gap mass (similarity-weighted gap sum)
        """
        gap_mass = sum(m.similarity * m.gap for m in matches)

        logger.debug(f"[StimulusInjector] Gap mass: {gap_mass:.2f} from {len(matches)} matches")

        return gap_mass

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

    def _apply_affective_priming(
        self,
        matches: List[InjectionMatch],
        priming_strength: float = 0.15
    ) -> List[InjectionMatch]:
        """
        Apply affective priming boost to match scores.

        PR-E.5: Affective Priming - Bias stimulus injection toward affect-congruent entry nodes.

        Formula: score_i = s_semantic × (1 + p × r_affect)
        where:
        - s_semantic: baseline semantic match [0,1]
        - p: priming strength (default 0.15 = 15% max boost)
        - r_affect = cos(A_recent, E_emo_i): affect alignment [-1,1]

        Args:
            matches: Injection matches with emotion_vector populated
            priming_strength: Maximum boost fraction (default 0.15)

        Returns:
            Matches with adjusted similarity scores
        """
        if not self.affective_priming_enabled:
            return matches

        # Check if recent affect is significant
        affect_magnitude = np.linalg.norm(self.recent_affect)

        # Read config from settings if available
        from orchestration.core.settings import settings
        min_magnitude = getattr(settings, 'AFFECTIVE_PRIMING_MIN_RECENT', 0.3)
        priming_strength = getattr(settings, 'AFFECTIVE_PRIMING_P', 0.15)

        if affect_magnitude < min_magnitude:
            # Recent affect too weak - skip priming
            logger.debug(f"[AffectivePriming] Skipped - recent affect magnitude {affect_magnitude:.2f} < {min_magnitude}")
            return matches

        primed_matches = []
        priming_applied_count = 0

        for match in matches:
            # Skip if no emotion vector
            if match.emotion_vector is None or len(match.emotion_vector) == 0:
                primed_matches.append(match)
                continue

            # Compute affect alignment: r_affect = cos(A_recent, E_emo_i)
            # Normalize both vectors
            recent_norm = self.recent_affect / (affect_magnitude + 1e-10)
            emotion_norm = match.emotion_vector / (np.linalg.norm(match.emotion_vector) + 1e-10)

            # Cosine similarity
            r_affect = np.dot(recent_norm, emotion_norm)

            # Apply boost: score_i = s_semantic × (1 + p × r_affect)
            # where r_affect ∈ [-1, 1], so boost ∈ [-p, +p]
            boost = priming_strength * r_affect
            boosted_similarity = match.similarity * (1.0 + boost)

            # Clamp to [0, 1] to keep similarity valid
            boosted_similarity = np.clip(boosted_similarity, 0.0, 1.0)

            # Create new match with boosted similarity
            primed_match = InjectionMatch(
                item_id=match.item_id,
                item_type=match.item_type,
                similarity=boosted_similarity,
                current_energy=match.current_energy,
                threshold=match.threshold,
                gap=match.gap,
                source_id=match.source_id,
                target_id=match.target_id,
                precedence_forward=match.precedence_forward,
                precedence_backward=match.precedence_backward,
                source_energy=match.source_energy,
                target_energy=match.target_energy,
                source_threshold=match.source_threshold,
                target_threshold=match.target_threshold,
                emotion_vector=match.emotion_vector
            )

            primed_matches.append(primed_match)

            if abs(boost) > 0.01:  # Log significant boosts
                priming_applied_count += 1
                logger.debug(
                    f"[AffectivePriming] {match.item_id}: "
                    f"r_affect={r_affect:.2f}, boost={boost:+.2f}, "
                    f"sim {match.similarity:.2f} → {boosted_similarity:.2f}"
                )

        if priming_applied_count > 0:
            logger.info(
                f"[AffectivePriming] Applied to {priming_applied_count}/{len(matches)} matches "
                f"(A_recent magnitude={affect_magnitude:.2f})"
            )

        return primed_matches

    def update_recent_affect(self, current_affect: np.ndarray):
        """
        Update recent affect EMA.

        PR-E.5: Track A_recent via exponential moving average.

        Args:
            current_affect: Current active entity affect vector [valence, arousal, ...]
        """
        if not self.affective_priming_enabled:
            return

        # EMA update: A_recent = α × current + (1 - α) × A_recent_old
        self.recent_affect = (
            self.affect_ema_alpha * current_affect[:2]  # Use first 2 dims (valence, arousal)
            + (1 - self.affect_ema_alpha) * self.recent_affect
        )

        logger.debug(
            f"[AffectivePriming] Updated A_recent: [{self.recent_affect[0]:.2f}, {self.recent_affect[1]:.2f}], "
            f"magnitude={np.linalg.norm(self.recent_affect):.2f}"
        )

    def _distribute_budget(
        self,
        budget: float,
        matches: List[InjectionMatch]
    ) -> List[Dict[str, Any]]:
        """
        Distribute budget across matches proportional to similarity × gap, capped at gap.

        Implements gap-capped budgeting: nodes never exceed their threshold.

        Args:
            budget: Total energy budget to distribute
            matches: Selected matches

        Returns:
            List of injections: [{item_id, delta_energy, new_energy}, ...]
        """
        if budget <= 0 or not matches:
            return []

        # Compute weights: similarity × gap
        weights = np.array([m.similarity * m.gap for m in matches])
        total_weight = weights.sum()

        if total_weight == 0:
            # All gaps zero - nothing to inject
            logger.debug("[StimulusInjector] All gaps zero, no injection")
            return []

        injections = []

        for match, weight in zip(matches, weights):
            # Proportional allocation
            delta_energy_uncapped = budget * (weight / total_weight)

            # Cap at gap (don't exceed threshold)
            delta_energy = min(delta_energy_uncapped, match.gap)

            # Skip negligible injections
            if delta_energy < 1e-9:
                continue

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
                f"= {new_energy:.2f} (gap={match.gap:.2f}, sim={match.similarity:.2f})"
            )

        return injections

    def _compute_threshold(
        self,
        node_type: str,
        current_energy: float,
        recency_score: float = 0.0,
        quality_score: float = 0.5,
        affinity_z: float = 0.0
    ) -> Tuple[float, bool]:
        """
        Threshold Oracle: Compute activation floor (Θ) for a node.

        Uses per-type baselines with bounded adjustments for recency, quality, and affinity.

        Args:
            node_type: Type of node (Realization, Memory, etc.)
            current_energy: Node's current energy (for scale guard)
            recency_score: 0-1, fresh=1
            quality_score: 0-1, higher is better
            affinity_z: Entity-affinity z-score, clamped to [-2, 2]

        Returns:
            (threshold, scale_mismatch_detected)
        """
        # Step 1: Type baseline
        TYPE_BASELINES = {
            "Realization": 30.0,
            "Memory": 25.0,
            "Concept": 28.0,
            "Principle": 35.0,
            "Mechanism": 38.0,
            "Document": 22.0,
            "Spec": 22.0,
            "Event": 26.0,
            "Post": 26.0,
            "Signal": 26.0,
            "Best_Practice": 32.0,
            "Anti_Pattern": 30.0,
        }
        theta_base = TYPE_BASELINES.get(node_type, 30.0)

        # Step 2: Adaptive adjustments (bounded)
        delta_recency = -5.0 * recency_score
        delta_quality = 4.0 * (1.0 - quality_score)
        delta_affinity = -2.0 * max(-2.0, min(2.0, affinity_z))

        # Step 3: Combine and clamp
        theta = theta_base + delta_recency + delta_quality + delta_affinity
        theta = max(15.0, min(45.0, theta))

        # Step 4: Scale guard (detect E-Θ unit mismatch)
        scale_mismatch = False
        if current_energy > 1.0 and theta < 1.0:
            logger.warning(
                f"[StimulusInjector] Scale mismatch detected: E={current_energy:.2f}, Θ={theta:.2f}. "
                f"Correcting to Θ=30.0"
            )
            theta = 30.0
            scale_mismatch = True

        return theta, scale_mismatch

    def _distribute_budget_dual_channel(
        self,
        budget: float,
        matches: List[InjectionMatch]
    ) -> List[Dict[str, Any]]:
        """
        Dual-channel injection: Top-Up + Amplifier.

        Top-Up channel (λ*B): Helps nodes below floor reach activation threshold.
        Amplifier channel ((1-λ)*B): Boosts strong matches regardless of current energy.

        Args:
            budget: Total energy budget to distribute
            matches: Selected matches with computed thresholds

        Returns:
            List of injections: [{item_id, delta_energy, new_energy, channel_breakdown}, ...]
        """
        if budget <= 0 or not matches:
            return []

        # Step 1: Compute weights for both channels
        w_top = []
        w_amp = []
        gaps = []

        for m in matches:
            # Top-Up: sigmoid of deficit
            deficit = m.threshold - m.current_energy
            gaps.append(max(0.0, deficit))
            # σ(x) = 1/(1+e^(-x)), k=8
            w_top.append(1.0 / (1.0 + np.exp(-deficit / 8.0)))

            # Amplifier: similarity^γ
            gamma = 1.3
            w_amp.append(pow(m.similarity, gamma))

        # Normalize weights
        sum_top = sum(w_top) or 1e-9
        sum_amp = sum(w_amp) or 1e-9
        w_top_norm = [w / sum_top for w in w_top]
        w_amp_norm = [w / sum_amp for w in w_amp]

        # Step 2: Adaptive λ (budget split)
        # Coldness: average deficit among candidates
        avg_deficit = sum(gaps) / max(len(gaps), 1)

        # Similarity concentration (Herfindahl)
        sum_sim = sum(m.similarity for m in matches) or 1e-9
        s_norm = [m.similarity / sum_sim for m in matches]
        H = sum(s * s for s in s_norm)

        # Adaptive: raise λ if cold (more Top-Up), lower λ if concentrated (more Amplify)
        lambda_base = 0.6
        lambda_val = lambda_base + 0.2 * (1 if avg_deficit > 10 else 0) - 0.2 * (1 if H > 0.2 else 0)
        lambda_val = max(0.3, min(0.8, lambda_val))

        B_top = lambda_val * budget
        B_amp = (1.0 - lambda_val) * budget

        logger.info(
            f"[StimulusInjector] Dual-channel: λ={lambda_val:.2f}, avg_deficit={avg_deficit:.2f}, "
            f"H={H:.3f}, B_top={B_top:.2f}, B_amp={B_amp:.2f}"
        )

        # Step 3: Compute injections per node
        injections = []
        total_proposed = 0.0

        for i, m in enumerate(matches):
            # Top-Up: capped at gap
            delta_top = min(gaps[i], w_top_norm[i] * B_top)

            # Amplifier: no floor cap
            delta_amp = w_amp_norm[i] * B_amp

            # Combined
            delta_proposed = delta_top + delta_amp

            # Per-node cap
            delta_proposed = min(delta_proposed, 10.0)

            total_proposed += delta_proposed

            injections.append({
                'item_id': m.item_id,
                'item_type': m.item_type,
                'delta_energy': delta_proposed,
                'delta_top': delta_top,
                'delta_amp': delta_amp,
                'current_energy': m.current_energy,
                'new_energy': m.current_energy + delta_proposed,
                'threshold': m.threshold,
                'similarity': m.similarity,
                'gap': gaps[i]
            })

        # Step 4: Renormalize if total exceeds budget
        if total_proposed > budget and total_proposed > 0:
            scale = budget / total_proposed
            logger.debug(f"[StimulusInjector] Renormalizing: {total_proposed:.2f} → {budget:.2f} (scale={scale:.3f})")
            for inj in injections:
                inj['delta_energy'] *= scale
                inj['delta_top'] *= scale
                inj['delta_amp'] *= scale
                inj['new_energy'] = inj['current_energy'] + inj['delta_energy']

        # Filter negligible injections
        injections = [inj for inj in injections if inj['delta_energy'] >= 1e-9]

        # Logging
        for inj in injections:
            logger.debug(
                f"[StimulusInjector] {inj['item_id']}: "
                f"E={inj['current_energy']:.2f} + ΔE={inj['delta_energy']:.2f} "
                f"(top={inj['delta_top']:.2f}, amp={inj['delta_amp']:.2f}) "
                f"= {inj['new_energy']:.2f} (Θ={inj['threshold']:.2f}, gap={inj['gap']:.2f}, s={inj['similarity']:.2f})"
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
        """Enable subentity-aware injection."""
        self.entity_channels_enabled = True
        logger.info("[StimulusInjector] Subentity channels ENABLED")

    def enable_peripheral_amplification(self):
        """Enable S5/S6 peripheral amplification."""
        self.peripheral_amplification_enabled = True
        logger.info("[StimulusInjector] Peripheral amplification ENABLED")

    def enable_affective_priming(self):
        """Enable affective priming (PR-E.5)."""
        self.affective_priming_enabled = True
        logger.info("[StimulusInjector] Affective priming ENABLED")


def create_match(
    item_id: str,
    item_type: str,
    similarity: float,
    current_energy: float,
    threshold: float
) -> InjectionMatch:
    """Helper to create InjectionMatch with proper gap computation."""
    # Compute gap: max(0, threshold - current_energy)
    gap = max(0.0, threshold - current_energy)

    return InjectionMatch(
        item_id=item_id,
        item_type=item_type,
        similarity=similarity,
        current_energy=current_energy,
        threshold=threshold,
        gap=gap
    )
