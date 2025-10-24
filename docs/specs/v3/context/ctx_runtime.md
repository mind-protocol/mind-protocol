# ctx_runtime.md
**Generated:** 2025-10-24T21:23:35
---

## >>> BEGIN orchestration/mechanisms/consciousness_engine_v2.py
<!-- mtime: 2025-10-24T21:23:33; size_chars: 73142 -->

"""
Consciousness Engine V2 - Phase 1+2 Architecture

Complete implementation using:
- Phase 1: Multi-Energy (M01) + Bitemporal (M13)
- Phase 2: Diffusion (M07) + Decay (M08) + Strengthening (M09) + Threshold (M16)

Architecture: Clean separation of concerns
- Core: Pure data structures (Node, Link, Graph)
- Mechanisms: Pure functions (diffusion, decay, strengthening, threshold)
- Orchestration: System coordination (metrics, websocket_broadcast)
- Engine: Tick loop that composes mechanisms

Tick Algorithm (M16 Part 2 - Four-Phase Cycle):
1. Activation: Compute thresholds, determine active nodes
2. Redistribution: Diffusion + Decay + Stimuli
3. Workspace: Budget enforcement, select active clusters
4. Learning: Strengthen active links + emit metrics

Author: Felix (Engineer)
Created: 2025-10-19
Architecture: Phase 1+2 Clean Break
"""

import time
import asyncio
import logging
import math
import numpy as np
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass

# Core data structures
from orchestration.core import Node, Link, Graph

# Mechanisms (Phase 1+2)
from orchestration.mechanisms import decay, strengthening, threshold, criticality
from orchestration.mechanisms.diffusion_runtime import DiffusionRuntime
from orchestration.mechanisms.strengthening import StrengtheningContext
from orchestration.mechanisms.threshold import ThresholdContext, NoiseTracker
from orchestration.mechanisms.criticality import CriticalityController, ControllerConfig

# Learning Mechanisms (Phase 3+4)
from orchestration.mechanisms.stimulus_injection import StimulusInjector, create_match
from orchestration.mechanisms.weight_learning import WeightLearner

# Observability
from orchestration.libs.metrics import BranchingRatioTracker
from orchestration.libs.websocket_broadcast import ConsciousnessStateBroadcaster

# FalkorDB integration
from orchestration.libs.utils.falkordb_adapter import FalkorDBAdapter

logger = logging.getLogger(__name__)


@dataclass
class EngineConfig:
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
    tick_interval_ms: float = 1000.0  # 1 Hz default (was 100ms = 10Hz, too fast)
    entity_id: str = "consciousness_engine"
    network_id: str = "N1"
    enable_diffusion: bool = True
    enable_decay: bool = True
    enable_strengthening: bool = True
    enable_websocket: bool = True
    compute_budget: float = 100.0
    max_nodes_per_tick: int = 50000


class ConsciousnessEngineV2:
    """
    Phase 1+2 Consciousness Engine.

    Implements complete consciousness tick using Phase 1+2 mechanisms.

    Example:
        >>> adapter = FalkorDBAdapter(host="localhost", port=6379)
        >>> graph = adapter.load_graph("citizen_felix")
        >>> config = EngineConfig(tick_interval_ms=100, entity_id="felix")
        >>> engine = ConsciousnessEngineV2(graph, adapter, config)
        >>> await engine.run()
    """

    def __init__(
        self,
        graph: Graph,
        adapter: FalkorDBAdapter,
        config: Optional[EngineConfig] = None
    ):
        """
        Initialize consciousness engine.

        Args:
            graph: In-memory graph (Node, Link objects)
            adapter: FalkorDB adapter for persistence
            config: Engine configuration (defaults if None)
        """
        self.graph = graph
        self.adapter = adapter
        self.config = config or EngineConfig()

        # Tick state
        self.tick_count = 0
        self.running = False

        # Diffusion runtime (V2 stride-based)
        self.diffusion_rt = DiffusionRuntime()
        # Initialize frontier from graph state
        self.diffusion_rt.compute_frontier(graph)

        # Mechanism contexts (Phase 1+2)
        # NOTE: DecayContext is now created per-tick with criticality-adjusted parameters
        self.strengthening_ctx = StrengtheningContext()
        self.threshold_ctx = ThresholdContext()
        self.noise_tracker = NoiseTracker()

        # Criticality controller (M03)
        self.criticality_controller = CriticalityController(ControllerConfig(
            k_p=0.05,
            enable_pid=False,
            enable_dual_lever=False,
            sample_rho_every_n_frames=5
        ))

        # E.6: Coherence metric (flow vs chaos quality measure)
        from orchestration.mechanisms.coherence_metric import CoherenceState
        self.coherence_state = CoherenceState()

        # Learning mechanisms (Phase 3+4)
        self.stimulus_injector = StimulusInjector()
        self.weight_learner = WeightLearner(alpha=0.1, min_cohort_size=3)

        # Stimulus queue (for Phase 1: Activation)
        self.stimulus_queue: List[Dict[str, any]] = []

        # TRACE queue (for Phase 4: Learning)
        self.trace_queue: List[Dict[str, any]] = []

        # Observability
        self.branching_tracker = BranchingRatioTracker(window_size=10)
        self.broadcaster = ConsciousnessStateBroadcaster() if self.config.enable_websocket else None

        # Subentity Layer (advanced thresholding)
        from orchestration.mechanisms.entity_activation import EntityCohortTracker
        self.entity_cohort_tracker = EntityCohortTracker(window_size=100)

        # Metrics
        self.last_tick_time = datetime.now()
        self.tick_duration_ms = 0.0

        # Transition matrix cache (rebuild only when graph structure changes)
        self._transition_matrix = None
        self._transition_matrix_dirty = True

        logger.info(f"[ConsciousnessEngineV2] Initialized")
        logger.info(f"  Subentity: {self.config.entity_id}")
        logger.info(f"  Network: {self.config.network_id}")
        logger.info(f"  Nodes: {len(self.graph.nodes)}, Links: {len(self.graph.links)}")
        logger.info(f"  Tick interval: {self.config.tick_interval_ms}ms")

    async def run(self, max_ticks: Optional[int] = None):
        """
        Run consciousness engine (main loop).

        Args:
            max_ticks: Optional maximum number of ticks (None = infinite)

        Example:
            >>> await engine.run(max_ticks=1000)  # Run for 1000 ticks
            >>> # Or run indefinitely:
            >>> await engine.run()
        """
        self.running = True
        logger.info("[ConsciousnessEngineV2] Starting main loop...")

        try:
            while self.running:
                # Execute one tick with exception handling
                try:
                    await self.tick()
                except Exception as e:
                    # Log tick errors but continue running
                    logger.error(f"[ConsciousnessEngineV2] Tick {self.tick_count} failed: {e}", exc_info=True)
                    # Don't stop engine - continue to next tick
                    await asyncio.sleep(1.0)  # Brief pause before retry
                    continue

                # Check max ticks
                if max_ticks is not None and self.tick_count >= max_ticks:
                    logger.info(f"[ConsciousnessEngineV2] Reached max ticks ({max_ticks})")
                    break

                # Sleep until next tick
                await asyncio.sleep(self.config.tick_interval_ms / 1000.0)

        except KeyboardInterrupt:
            logger.info("[ConsciousnessEngineV2] Interrupted by user")
        except Exception as e:
            # Fatal error in main loop (not tick-related)
            logger.error(f"[ConsciousnessEngineV2] Fatal error in main loop: {e}", exc_info=True)
        finally:
            self.running = False
            logger.info("[ConsciousnessEngineV2] Stopped")

    def stop(self):
        """Stop the engine."""
        self.running = False

    def pause(self):
        """Pause the engine (same as stop for now)."""
        self.stop()

    def resume(self):
        """Resume the engine."""
        self.running = True
        logger.info(f"[{self.config.entity_id}] Engine resumed")

    # === Frame Pipeline Steps (spec: traversal_v2.md §2) ===

    def _refresh_affect(self):
        """
        Step 1: Compute affect for active entity.

        From spec §3.1: compute A for active entity (Phase 1: valence/arousal).

        TODO: Implement emotion state computation when emotion specs are written.
        For now, this is a stub that returns None (no affect context).
        """
        # TODO: Implement affect computation
        # Should compute valence/arousal state for active entity
        # Used later in emotion gates for cost modulation
        return None

    def _refresh_frontier(self):
        """
        Step 2: Refresh active/shadow frontier sets.

        From spec §3.2:
        - active = {i | E_i >= Θ_i} ∪ {i | received ΔE this frame}
        - shadow = 1-hop(active)

        Uses DiffusionRuntime.compute_frontier() which computes:
        - active: nodes with E >= theta
        - shadow: 1-hop neighbors of active (minus active itself)
        """
        self.diffusion_rt.compute_frontier(self.graph)

        logger.debug(
            f"[Step 2] Frontier: {len(self.diffusion_rt.active)} active, "
            f"{len(self.diffusion_rt.shadow)} shadow"
        )

    def _emit_stride_exec_samples(self):
        """
        Step 5: Emit sampled stride.exec events for observability.

        From spec §3.4: Track φ (gap closure), ema_flow, res/comp for events.
        From spec §5: stride.exec samples with {src,dst,dE,phi,ease,res...,comp...}

        TODO: Implement stride.exec event emission when observability events are designed.
        For now, this is a stub.
        """
        # TODO: Implement stride.exec event sampling
        # Should emit sampled events with:
        # - src, dst node IDs
        # - dE (energy transferred)
        # - phi (gap closure / usefulness)
        # - ease (exp(log_weight))
        # - resonance/complementarity values
        pass

    async def tick(self):
        """
        V2 Frame Pipeline (spec: traversal_v2.md §2)

        10-step orchestration per frame:
        1. refresh_affect() - compute A for active entity
        2. refresh_frontier() - active/shadow sets
        3. choose_boundaries() - entity-scale exits (stub for now)
        4. within_entity_strides(dt) - cost-based stride execution
        5. emit_stride_exec_samples() - observability events (stub)
        6. apply_staged_deltas() - atomic ΔE apply
        7. apply_activation_decay(dt) - type-dependent multipliers
        8. criticality_control() - tune decay/α to keep ρ≈1
        9. wm_select_and_emit() - entity-first WM output
        10. frame_end_event() - end-of-frame observability

        Replaced old 4-phase cycle with spec-aligned 10-step pipeline.
        """
        tick_start = time.time()
        subentity = self.config.entity_id

        # === V2 Event: frame.start ===
        if self.broadcaster and self.broadcaster.is_available():
            # Include entity index for Iris viz (first frame or when entities change)
            entity_index = []
            if hasattr(self.graph, 'subentities') and self.graph.subentities:
                for entity in self.graph.subentities.values():
                    entity_index.append({
                        "id": entity.id,
                        "name": entity.role_or_topic,
                        "color": getattr(entity, 'color', '#888888'),
                        "energy": round(entity.energy_runtime, 4),
                        "threshold": round(entity.threshold_runtime, 4),
                        "active": entity.energy_runtime >= entity.threshold_runtime,
                        "member_count": entity.member_count
                    })

            await self.broadcaster.broadcast_event("frame.start", {
                "v": "2",
                "frame_id": self.tick_count,
                "entity_index": entity_index,  # Entity snapshot for viz
                "t_ms": int(time.time() * 1000)
            })

        # Capture previous state for flip detection
        # NOTE: Single-energy architecture (E >= theta)
        previous_states = {}
        for node in self.graph.nodes.values():
            previous_states[node.id] = {
                'energy': node.E,
                'threshold': node.theta,
                'was_active': node.is_active()
            }

        # === Phase 1: Activation (Stimulus Injection) ===
        # Process incoming stimuli from queue
        while self.stimulus_queue:
            stimulus = self.stimulus_queue.pop(0)

            # Extract stimulus data
            embedding = stimulus.get('embedding')
            text = stimulus.get('text', '')
            source_type = stimulus.get('source_type', 'user_message')

            if embedding is not None:
                # Create matches from vector search (simplified - would use real vector search)
                # For now, match all nodes with simple similarity scoring
                matches = []
                for node in self.graph.nodes.values():
                    # Simplified similarity (would use cosine similarity with actual embeddings)
                    similarity = 0.5  # Placeholder
                    current_energy = node.E  # Single-energy architecture

                    match = create_match(
                        item_id=node.id,
                        item_type='node',
                        similarity=similarity,
                        current_energy=current_energy,
                        threshold=node.theta
                    )
                    matches.append(match)

                # Inject energy using stimulus injector
                if matches:
                    result = self.stimulus_injector.inject(
                        stimulus_embedding=embedding,
                        matches=matches,
                        source_type=source_type
                    )

                    # Apply injections to nodes
                    for injection in result.injections:
                        node = self.graph.get_node(injection['item_id'])
                        if node:
                            node.add_energy(injection['delta_energy'])  # Single-energy: direct add

                    logger.debug(
                        f"[Phase 1] Stimulus injection: {result.total_energy_injected:.2f} energy "
                        f"into {result.items_injected} nodes"
                    )

        # Compute adaptive thresholds and activation masks
        # NOTE: Using TOTAL energy per spec (sub-entity = any active node)
        activation_mask = {
            node.id: node.is_active()
            for node in self.graph.nodes.values()
        }

        activated_nodes = [node_id for node_id, is_active in activation_mask.items() if is_active]

        # === Phase 1.5: Criticality Control (before redistribution) ===
        # Get branching ratio from tracker (cheap proxy for criticality)
        if self.tick_count > 0:
            previous_activated = getattr(self, '_previous_activated', activated_nodes)
            branching_state = self.branching_tracker.measure_cycle(
                activated_this_gen=previous_activated,
                activated_next_gen=activated_nodes
            )
            branching_ratio = branching_state['branching_ratio']
            self._previous_activated = activated_nodes
        else:
            self._previous_activated = activated_nodes
            branching_ratio = 1.0  # Default for first frame
            branching_state = None

        # Update criticality controller (simplified - uses branching ratio proxy)
        # TODO: Build P matrix for proper rho computation when needed
        criticality_metrics = self.criticality_controller.update(
            P=None,  # Skip P-based rho for now (stride-based doesn't need full matrix)
            current_delta=0.03,  # Default decay rate
            current_alpha=0.1,   # Default diffusion rate
            branching_ratio=branching_ratio,
            force_sample=False
        )

        # Compute threshold multiplier from safety state
        threshold_multiplier = criticality.compute_threshold_multiplier(criticality_metrics.safety_state)

        # === V2 Event: criticality.state ===
        if self.broadcaster and self.broadcaster.is_available():
            await self.broadcaster.broadcast_event("criticality.state", {
                "v": "2",
                "frame_id": self.tick_count,
                "rho": {
                    "global": round(criticality_metrics.rho_global, 4),
                    "proxy_branching": round(criticality_metrics.rho_proxy_branching, 4),
                    "var_window": round(criticality_metrics.rho_var_window, 6)
                },
                "safety_state": criticality_metrics.safety_state.value,
                "delta": {
                    "before": round(criticality_metrics.delta_before, 4),
                    "after": round(criticality_metrics.delta_after, 4)
                },
                "alpha": {
                    "before": round(criticality_metrics.alpha_before, 4),
                    "after": round(criticality_metrics.alpha_after, 4)
                },
                "controller_output": round(criticality_metrics.controller_output, 6),
                "oscillation_index": round(criticality_metrics.oscillation_index, 4),
                "threshold_multiplier": round(threshold_multiplier, 3),
                "t_ms": int(time.time() * 1000)
            })

        logger.debug(
            f"[Phase 1.5] Criticality: ρ={criticality_metrics.rho_global:.3f}, "
            f"state={criticality_metrics.safety_state.value}, "
            f"δ={criticality_metrics.delta_after:.4f}, "
            f"α={criticality_metrics.alpha_after:.4f}"
        )

        # === Step 1: Refresh Affect ===
        affect_context = self._refresh_affect()

        # === Step 2: Refresh Frontier ===
        # Compute active/shadow frontier BEFORE diffusion
        self._refresh_frontier()

        # === Step 3: Choose Boundaries (Two-Scale Traversal) ===
        # Phase 1: Between-entity selection using 5-hunger scoring
        from orchestration.core.settings import settings

        strides_executed = 0
        boundary_strides = 0

        if self.config.enable_diffusion:
            alpha_tick = criticality_metrics.alpha_after
            dt = self.config.tick_interval_ms / 1000.0

            if settings.TWO_SCALE_ENABLED and hasattr(self.graph, 'subentities'):
                # Two-scale traversal: entity → atomic
                from orchestration.mechanisms.sub_entity_traversal import (
                    choose_next_entity, select_representative_nodes
                )
                from orchestration.mechanisms.diffusion_runtime import execute_stride_step
                from orchestration.mechanisms.entity_activation import learn_relates_to_from_boundary_stride
                from orchestration.core.types import LinkType

                # Get active entities
                active_entities = [
                    entity for entity in self.graph.subentities.values()
                    if entity.is_active()
                ]

                if active_entities:
                    # Choose next entity using hunger scoring
                    current_entity = None  # TODO: Track current entity in engine state
                    goal_embedding = None  # TODO: Extract from config or context

                    next_entity, entity_scores = choose_next_entity(
                        current_entity,
                        active_entities,
                        goal_embedding,
                        self.graph
                    )

                    if next_entity and current_entity:
                        # Execute between-entity stride (boundary crossing)
                        src_node, tgt_node = select_representative_nodes(current_entity, next_entity)

                        if src_node and tgt_node:
                            # Find link between representative nodes
                            boundary_link = None
                            for link in src_node.outgoing_links:
                                if link.target.id == tgt_node.id:
                                    boundary_link = link
                                    break

                            if boundary_link:
                                # Execute boundary stride with entity-aware weight (Priority 4)
                                from orchestration.core.entity_context_extensions import effective_log_weight_link
                                E_src = src_node.E
                                log_w = effective_log_weight_link(boundary_link, current_entity.id) if current_entity else boundary_link.log_weight
                                ease = math.exp(log_w)
                                delta_E = E_src * ease * alpha_tick * dt

                                if delta_E > 1e-9:
                                    # Stage energy transfer
                                    self.diffusion_rt.add(src_node.id, -delta_E)
                                    self.diffusion_rt.add(tgt_node.id, +delta_E)

                                    # Learn RELATES_TO from boundary stride
                                    learn_relates_to_from_boundary_stride(
                                        current_entity,
                                        next_entity,
                                        delta_E,
                                        self.graph
                                    )

                                    boundary_strides += 1

                    # Within-entity strides (constrained to active entities)
                    # For Phase 1: Execute normal strides (constraint TODO for Phase 2)
                    # Pass entity ID for personalized weight computation (Priority 4)
                    strides_executed = execute_stride_step(
                        self.graph,
                        self.diffusion_rt,
                        alpha_tick=alpha_tick,
                        dt=dt,
                        sample_rate=0.1,
                        broadcaster=self.broadcaster,
                        enable_link_emotion=True,
                        current_entity_id=next_entity.id if next_entity else None
                    )
                else:
                    # No active entities - fall back to atomic
                    from orchestration.mechanisms.diffusion_runtime import execute_stride_step
                    strides_executed = execute_stride_step(
                        self.graph,
                        self.diffusion_rt,
                        alpha_tick=alpha_tick,
                        dt=dt,
                        sample_rate=0.1,
                        broadcaster=self.broadcaster,
                        enable_link_emotion=True
                    )
            else:
                # Two-scale disabled or no subentities - use atomic strides only
                from orchestration.mechanisms.diffusion_runtime import execute_stride_step
                strides_executed = execute_stride_step(
                    self.graph,
                    self.diffusion_rt,
                    alpha_tick=alpha_tick,
                    dt=dt,
                    sample_rate=0.1,
                    broadcaster=self.broadcaster,
                    enable_link_emotion=True
                )

            # === TRIPWIRE: Energy Conservation (CRITICAL) ===
            # Check energy conservation before applying deltas
            # Tripwire triggers Safe Mode on single violation (physics violation)
            conservation_error = self.diffusion_rt.get_conservation_error()

            try:
                from orchestration.services.health.safe_mode import (
                    get_safe_mode_controller, TripwireType
                )
                from orchestration.core.settings import settings

                safe_mode = get_safe_mode_controller()
                epsilon = settings.TRIPWIRE_CONSERVATION_EPSILON  # 0.001

                if abs(conservation_error) > epsilon:
                    # Energy not conserved - CRITICAL violation
                    safe_mode.record_violation(
                        tripwire_type=TripwireType.CONSERVATION,
                        value=abs(conservation_error),
                        threshold=epsilon,
                        message=f"Energy not conserved: ΣΔE={conservation_error:.6f} (ε={epsilon})"
                    )
                    logger.warning(
                        f"[TRIPWIRE] Conservation violation: {conservation_error:.6f} "
                        f"(threshold={epsilon})"
                    )
                else:
                    # Energy conserved - record compliance
                    safe_mode.record_compliance(TripwireType.CONSERVATION)

            except Exception as e:
                # Tripwire check failed - log but don't crash tick
                logger.error(f"[TRIPWIRE] Conservation check failed: {e}")
                # Continue execution - tripwire is diagnostic, not control flow

            # === V2 Event: se.boundary.summary (boundary stride observability) ===
            if self.broadcaster and self.broadcaster.is_available() and boundary_strides > 0:
                await self.broadcaster.broadcast_event("se.boundary.summary", {
                    "v": "2",
                    "frame_id": self.tick_count,
                    "boundary_strides": boundary_strides,
                    "total_strides": strides_executed + boundary_strides,
                    "t_ms": int(time.time() * 1000)
                })

            # === Step 5: Emit Stride Exec Samples ===
            self._emit_stride_exec_samples()

            # === E.6: Compute Coherence Metric ===
            if settings.COHERENCE_METRIC_ENABLED:
                from orchestration.mechanisms.coherence_metric import compute_coherence_metric, emit_coherence_telemetry

                coherence_result = compute_coherence_metric(
                    current_frontier_nodes=self.diffusion_rt.current_frontier_nodes,
                    stride_relatedness_scores=self.diffusion_rt.stride_relatedness_scores,
                    state=self.coherence_state
                )

                # Emit coherence telemetry event
                if self.broadcaster and self.broadcaster.is_available():
                    coherence_event = emit_coherence_telemetry(
                        coherence_result=coherence_result,
                        frame_id=self.tick_count,
                        citizen_id=self.config.entity_id
                    )
                    await self.broadcaster.broadcast_event("coherence.metric", coherence_event)

                logger.debug(
                    f"[E.6] Coherence: C={coherence_result['coherence']:.3f} "
                    f"({coherence_result['interpretation']}), "
                    f"C_frontier={coherence_result['c_frontier']:.3f}, "
                    f"C_stride={coherence_result['c_stride']:.3f}"
                )

            # === Step 6: Apply Staged Deltas ===
            # Apply staged deltas atomically
            for node_id, delta in self.diffusion_rt.delta_E.items():
                node = self.graph.nodes.get(node_id)
                if node:
                    node.add_energy(delta)

            # Clear staged deltas
            self.diffusion_rt.clear_deltas()

            logger.debug(
                f"[Step 3-4] Two-scale traversal: {boundary_strides} boundary strides, "
                f"{strides_executed} within-entity strides, "
                f"α={alpha_tick:.4f}, conservation error={conservation_error:.6f}"
            )

        # === Step 7: Apply Activation Decay ===
        # Apply decay (exponential forgetting with criticality coupling)
        if self.config.enable_decay:
            # Create decay context with criticality-adjusted delta
            decay_ctx = decay.DecayContext(
                dt=self.config.tick_interval_ms / 1000.0,  # Convert to seconds
                effective_delta_E=criticality_metrics.delta_after,  # Use adjusted δ from controller
                apply_weight_decay=(self.tick_count % 60 == 0),  # Weight decay every 60 ticks (~1 minute)
                compute_histograms=(self.tick_count % 100 == 0)  # Histograms every 100 ticks (expensive)
            )
            decay_metrics = decay.decay_tick(self.graph, decay_ctx)

            # === V2 Event: decay.tick ===
            if self.broadcaster and self.broadcaster.is_available():
                await self.broadcaster.broadcast_event("decay.tick", {
                    "v": "2",
                    "frame_id": self.tick_count,
                    "delta_E": round(decay_metrics.delta_E, 6),
                    "delta_W": round(decay_metrics.delta_W, 6),
                    "nodes_decayed": decay_metrics.nodes_decayed,
                    "energy": {
                        "before": round(decay_metrics.total_energy_before, 4),
                        "after": round(decay_metrics.total_energy_after, 4),
                        "lost": round(decay_metrics.energy_lost, 4)
                    },
                    "weight_decay": {
                        "nodes": decay_metrics.nodes_weight_decayed,
                        "links": decay_metrics.links_weight_decayed
                    },
                    "half_lives_activation": {k: round(v, 2) for k, v in decay_metrics.half_lives_activation.items()},
                    "auc_activation": round(decay_metrics.auc_activation_window, 4),
                    "t_ms": int(time.time() * 1000)
                })

            logger.debug(
                f"[Step 7] Decay: {decay_metrics.nodes_decayed} nodes, "
                f"energy lost={decay_metrics.energy_lost:.3f}, "
                f"δ_E={decay_metrics.delta_E:.4f}"
            )

        # Apply emotion decay (separate from activation decay, spec §5.3)
        from orchestration.mechanisms import emotion_coloring
        from orchestration.core.settings import settings as emotion_settings
        if emotion_settings.EMOTION_ENABLED:
            dt = self.config.tick_interval_ms / 1000.0  # Convert to seconds
            emotion_decay_metrics = emotion_coloring.emotion_decay(
                self.graph,
                dt,
                decay_rate=emotion_settings.EMOTION_DECAY_RATE
            )
            logger.debug(
                f"[Step 7] Emotion decay: {emotion_decay_metrics.elements_decayed} elements, "
                f"mean mag: {emotion_decay_metrics.mean_magnitude:.3f}"
            )

        # Note: Step 8 (criticality_control) happens BEFORE diffusion in current implementation
        # This computes α_tick for THIS frame. Spec suggests it should happen after to adjust
        # parameters for NEXT frame, but current approach works as first-order approximation.

        # === Step 8.5: Update Entity Activations ===
        # Compute subentity energy from member nodes (spec: subentity_layer.md §2.2)
        # Formula: E_entity = Σ (m̃_iE × max(0, E_i - Θ_i))
        # With advanced thresholding: cohort-based, health modulation, hysteresis
        # With lifecycle management: promotion/dissolution
        entity_activation_metrics = []
        lifecycle_transitions = []
        if hasattr(self.graph, 'subentities') and len(self.graph.subentities) > 0:
            from orchestration.mechanisms.entity_activation import update_entity_activations

            entity_activation_metrics, lifecycle_transitions = update_entity_activations(
                self.graph,
                global_threshold_mult=threshold_multiplier,
                cohort_tracker=self.entity_cohort_tracker,
                enable_lifecycle=True
            )

            # === V2 Event: subentity.lifecycle (promotion/dissolution) ===
            if self.broadcaster and self.broadcaster.is_available() and lifecycle_transitions:
                for transition in lifecycle_transitions:
                    await self.broadcaster.broadcast_event("subentity.lifecycle", {
                        "v": "2",
                        "frame_id": self.tick_count,
                        "entity_id": transition.entity_id,
                        "old_state": transition.old_state,
                        "new_state": transition.new_state,
                        "quality_score": round(transition.quality_score, 4),
                        "trigger": transition.trigger,
                        "reason": transition.reason,
                        "t_ms": int(time.time() * 1000)
                    })

            # === V2 Event: subentity.flip (detect entity threshold crossings) ===
            if self.broadcaster and self.broadcaster.is_available():
                for metrics in entity_activation_metrics:
                    if metrics.flipped:
                        await self.broadcaster.broadcast_event("subentity.flip", {
                            "v": "2",
                            "frame_id": self.tick_count,
                            "entity_id": metrics.entity_id,
                            "flip_direction": metrics.flip_direction,
                            "energy": round(metrics.energy_after, 4),
                            "threshold": round(metrics.threshold, 4),
                            "activation_level": metrics.activation_level,
                            "member_count": metrics.member_count,
                            "active_members": metrics.active_members,
                            "t_ms": int(time.time() * 1000)
                        })

            logger.debug(
                f"[Step 8.5] Entity activation: {len(entity_activation_metrics)} subentities, "
                f"{sum(1 for m in entity_activation_metrics if m.flipped)} flipped"
            )

        # === Step 8.6: Identity Multiplicity Tracking (PR-D) ===
        # Track outcome metrics and assess multiplicity mode (productive vs conflict)
        if (hasattr(self.graph, 'subentities') and len(self.graph.subentities) > 0 and
            settings.IDENTITY_MULTIPLICITY_ENABLED):

            from orchestration.mechanisms.entity_activation import (
                track_task_progress, track_energy_efficiency, track_identity_flips,
                assess_multiplicity_mode
            )

            # Count active identities (entities above threshold)
            active_entities = [
                entity for entity in self.graph.subentities.values()
                if entity.is_active()
            ]
            num_active_identities = len(active_entities)

            # Determine dominant identity (highest energy)
            dominant_identity = None
            if active_entities:
                dominant_entity = max(active_entities, key=lambda e: e.energy_runtime)
                dominant_identity = dominant_entity.id

            # Track metrics for each entity
            for entity in self.graph.subentities.values():
                # Track task progress (use WM presence + formation quality as proxy)
                # Goals achieved = formations created + WM seats claimed
                goals_achieved = int(entity.ema_formation_quality * 10 + entity.ema_wm_presence * 5)
                track_task_progress(entity, goals_achieved, frames_elapsed=1)

                # Track energy efficiency (work output / energy spent)
                # Work output = active members + formations + WM presence
                work_output = (
                    sum(1 for m in entity.get_members() if m.is_active()) +
                    entity.ema_formation_quality * 10 +
                    entity.ema_wm_presence * 5
                )
                total_energy_spent = entity.energy_runtime + 1e-9  # Avoid division by zero
                track_energy_efficiency(entity, work_output, total_energy_spent)

                # Track identity flips
                track_identity_flips(entity, dominant_identity, self.graph)

            # Assess multiplicity mode and emit events (every 5 frames when multiple identities active)
            if num_active_identities >= 2 and self.tick_count % 5 == 0:
                for entity in active_entities:
                    multiplicity_mode = assess_multiplicity_mode(entity, num_active_identities)

                    # === V2 Event: entity.multiplicity_assessment ===
                    if self.broadcaster and self.broadcaster.is_available():
                        await self.broadcaster.broadcast_event("entity.multiplicity_assessment", {
                            "v": "2",
                            "frame_id": self.tick_count,
                            "entity_id": entity.id,
                            "num_active_identities": num_active_identities,
                            "identities": [e.id for e in active_entities],
                            "task_progress_rate": round(entity.task_progress_rate, 4),
                            "energy_efficiency": round(entity.energy_efficiency, 4),
                            "identity_flip_count": entity.identity_flip_count,
                            "coherence_score": round(entity.coherence_ema, 4),
                            "mode": multiplicity_mode,
                            "intervention": "none",  # Phase 1: no intervention yet
                            "t_ms": int(time.time() * 1000)
                        })

                    # === V2 Event: entity.productive_multiplicity ===
                    # Emit celebration event when multiplicity is productive
                    if multiplicity_mode == "productive" and self.broadcaster and self.broadcaster.is_available():
                        await self.broadcaster.broadcast_event("entity.productive_multiplicity", {
                            "v": "2",
                            "frame_id": self.tick_count,
                            "entity_id": entity.id,
                            "identities": [e.id for e in active_entities],
                            "task_progress_rate": round(entity.task_progress_rate, 4),
                            "energy_efficiency": round(entity.energy_efficiency, 4),
                            "message": f"Productive multiplicity: {num_active_identities} identities achieving good outcomes",
                            "t_ms": int(time.time() * 1000)
                        })

        # === V2 Event: node.flip (detect threshold crossings) ===
        # NOTE: Single-energy architecture (E >= theta for activation)
        if self.broadcaster and self.broadcaster.is_available():
            for node in self.graph.nodes.values():
                prev_state = previous_states[node.id]
                current_energy = node.E  # Single-energy
                is_now_active = node.is_active()  # E >= theta check

                # Emit flip event if activation state changed
                if prev_state['was_active'] != is_now_active:
                    await self.broadcaster.broadcast_event("node.flip", {
                        "v": "2",
                        "frame_id": self.tick_count,
                        "node": node.id,
                        "E_pre": prev_state['energy'],
                        "E_post": current_energy,
                        "Θ": node.theta,
                        "t_ms": int(time.time() * 1000)
                    })

        # === V2 Event: link.flow.summary (aggregate link activity) ===
        if self.broadcaster and self.broadcaster.is_available():
            link_flows = []
            for link in self.graph.links.values():
                # Get energy flow through this link (single-energy)
                source_energy = link.source.E
                target_energy = link.target.E

                # Estimate flow as function of energy difference and link ease
                ease = math.exp(link.log_weight)
                alpha_tick = criticality_metrics.alpha_after
                ΔE_estimate = source_energy * ease * alpha_tick * max(0, source_energy - target_energy)

                # Only include links with non-zero flow
                if ΔE_estimate > 0.001:
                    link_flows.append({
                        "id": f"{link.source.id}->{link.target.id}",
                        "ΔE_sum": round(ΔE_estimate, 4),
                        "φ_max": round(ease, 3),  # Using ease = exp(log_weight)
                        "z_flow": 0.0  # Would compute from cohort normalization
                    })

            if link_flows:
                # Transform to frontend-expected format
                flows_payload = [{
                    "link_id": flow["id"],
                    "count": 1,  # Single traversal per link in this implementation
                    "entity_ids": [subentity]  # Which subentity traversed this link (subentity is string)
                } for flow in link_flows]

                await self.broadcaster.broadcast_event("link.flow.summary", {
                    "v": "2",
                    "frame_id": self.tick_count,
                    "flows": flows_payload,  # Changed from "links" to "flows"
                    "t_ms": int(time.time() * 1000)
                })

        # === Step 9: WM Select and Emit ===
        # Entity-first working memory selection (spec: subentity_layer.md §4)
        workspace_entities, wm_summary = self._select_workspace_entities(subentity)

        # Extract all member nodes from selected entities (for backward compatibility)
        workspace_nodes = []
        for entity in workspace_entities:
            workspace_nodes.extend(entity.get_members())

        # Update WM presence tracking (nodes that are in selected entities)
        wm_node_ids = set(node.id for node in workspace_nodes)
        for node in self.graph.nodes.values():
            wm_indicator = 1 if node.id in wm_node_ids else 0
            node.ema_wm_presence = 0.1 * wm_indicator + 0.9 * node.ema_wm_presence

        # === V2 Event: wm.emit (entity-first working memory selection) ===
        if self.broadcaster and self.broadcaster.is_available():
            # Extract entity IDs and token shares for viz contract
            entity_ids = [e["id"] for e in wm_summary["entities"]]
            entity_token_shares = [
                {"id": e["id"], "tokens": e["tokens"]}
                for e in wm_summary["entities"]
            ]
            # Extract top member nodes from entities
            entity_member_nodes = []
            for e in wm_summary["entities"]:
                entity_member_nodes.extend([m["id"] for m in e["top_members"]])

            await self.broadcaster.broadcast_event("wm.emit", {
                "v": "2",
                "frame_id": self.tick_count,
                "mode": "entity_first",
                "selected_entities": entity_ids,  # Just IDs
                "entity_token_shares": entity_token_shares,  # Token allocation
                "total_entities": wm_summary["total_entities"],
                "total_members": wm_summary["total_members"],
                "token_budget_used": wm_summary["token_budget_used"],
                "selected_nodes": entity_member_nodes,  # Top members from entities
                "t_ms": int(time.time() * 1000)
            })

        # === Phase 4: Learning & Metrics ===
        # Process TRACE signals and update weights
        while self.trace_queue:
            trace_result = self.trace_queue.pop(0)
            self._apply_trace_learning(trace_result)

        # Strengthen links between active nodes
        # NOTE (2025-10-23 Iris): Strengthening now happens during diffusion stride execution
        # The strengthen_tick function no longer exists - strengthening is integrated in DiffusionRuntime
        # See: orchestration/mechanisms/strengthening.py line 12
        # if self.config.enable_strengthening:
        #     strengthening_metrics = strengthening.strengthen_tick(
        #         self.graph,
        #         subentity,
        #         self.strengthening_ctx,
        #         active_nodes=workspace_nodes
        #     )

        # NOTE: branching_state was already computed in Phase 1.5 for criticality control

        # Broadcast state to WebSocket clients
        if self.broadcaster and self.broadcaster.is_available() and branching_state:
            await self.broadcaster.broadcast_consciousness_state(
                network_id=self.config.network_id,
                global_energy=branching_state['global_energy'],
                branching_ratio=branching_state['branching_ratio'],
                raw_sigma=branching_state['raw_sigma'],
                tick_interval_ms=self.config.tick_interval_ms,
                tick_frequency_hz=1000.0 / self.config.tick_interval_ms,
                consciousness_state=self._get_consciousness_state_name(branching_state['global_energy']),
                time_since_last_event=0.0,  # TODO: Track external events
                timestamp=datetime.now()
            )

        # Update metrics
        tick_duration = (time.time() - tick_start) * 1000.0  # ms
        self.tick_duration_ms = tick_duration
        self.last_tick_time = datetime.now()

        # === Step 10: Tick Frame V1 Event (Entity-First Telemetry) + TRIPWIRE: Observability ===
        # tick_frame.v1 is the heartbeat signal - missing events → monitoring blind
        # Replaces legacy frame.end with entity-scale observability
        # Tripwire triggers Safe Mode after 5 consecutive failures
        frame_end_emitted = False

        if self.broadcaster and self.broadcaster.is_available():
            try:
                # Compute entity aggregates for visualization
                from orchestration.core.events import EntityData, TickFrameV1Event
                import time as time_module

                entity_data_list = []
                if hasattr(self.graph, 'subentities') and self.graph.subentities:
                    for entity_id, entity in self.graph.subentities.items():
                        # Get members above threshold
                        active_members = [nid for nid in entity.extent if self.graph.nodes.get(nid) and self.graph.nodes[nid].E >= self.graph.nodes[nid].theta]

                        # Aggregate emotion from active members
                        emotion_valence = None
                        emotion_arousal = None
                        emotion_magnitude = None

                        if active_members:
                            emotions = []
                            for nid in active_members:
                                node = self.graph.nodes.get(nid)
                                if node and hasattr(node, 'emotion_vector') and node.emotion_vector is not None:
                                    emotions.append(node.emotion_vector)

                            if emotions:
                                import numpy as np
                                avg_emotion = np.mean(emotions, axis=0)
                                emotion_valence = float(avg_emotion[0]) if len(avg_emotion) > 0 else 0.0
                                emotion_arousal = float(avg_emotion[1]) if len(avg_emotion) > 1 else 0.0
                                emotion_magnitude = float(np.linalg.norm(avg_emotion))

                        entity_data = EntityData(
                            id=entity_id,
                            name=entity.name if hasattr(entity, 'name') else entity_id,
                            kind=entity.kind.value if hasattr(entity, 'kind') and hasattr(entity.kind, 'value') else "functional",
                            color=entity.color if hasattr(entity, 'color') else "#808080",
                            energy=float(entity.E),
                            theta=float(entity.theta),
                            active=entity.is_active(),
                            members_count=len(entity.extent) if hasattr(entity, 'extent') else 0,
                            coherence=entity.coherence if hasattr(entity, 'coherence') else 0.0,
                            emotion_valence=emotion_valence,
                            emotion_arousal=emotion_arousal,
                            emotion_magnitude=emotion_magnitude
                        )
                        entity_data_list.append(entity_data)

                # Create tick_frame.v1 event
                tick_event = TickFrameV1Event(
                    citizen_id=self.config.citizen_id,
                    frame_id=self.tick_count,
                    t_ms=int(time_module.time() * 1000),
                    tick_duration_ms=round(tick_duration, 2),
                    entities=entity_data_list,
                    nodes_active=len([n for n in self.graph.nodes.values() if n.is_active()]),
                    nodes_total=len(self.graph.nodes),
                    strides_executed=0,  # TODO: Track actual stride count
                    stride_budget=int(self.config.compute_budget),
                    rho=criticality_metrics.rho_global if criticality_metrics else 1.0,
                    coherence=0.0  # TODO: Add coherence metric if available
                )

                # Emit event
                await self.broadcaster.broadcast_event("tick_frame_v1", tick_event.to_dict())
                frame_end_emitted = True

            except Exception as e:
                # tick_frame.v1 emission failed - record observability violation
                logger.error(f"[TRIPWIRE] tick_frame.v1 emission failed: {e}")
                frame_end_emitted = False

        # Record observability tripwire status
        try:
            from orchestration.services.health.safe_mode import (
                get_safe_mode_controller, TripwireType
            )

            safe_mode = get_safe_mode_controller()

            if frame_end_emitted:
                # Event emitted successfully
                safe_mode.record_compliance(TripwireType.OBSERVABILITY)
            else:
                # Event emission failed (either broadcaster unavailable or exception)
                safe_mode.record_violation(
                    tripwire_type=TripwireType.OBSERVABILITY,
                    value=1.0,  # Binary: failed=1
                    threshold=0.0,  # Should always emit
                    message="Failed to emit tick_frame.v1 event (observability lost)"
                )

        except Exception as e:
            # Tripwire check failed - log but don't crash tick
            logger.error(f"[TRIPWIRE] Observability check failed: {e}")
            # Continue execution - tripwire is diagnostic, not control flow

        # Increment tick count AFTER emitting tick_frame.v1 (so frame_id is correct)
        self.tick_count += 1

        # Periodic logging
        if self.tick_count % 100 == 0:
            logger.info(
                f"[ConsciousnessEngineV2] Tick {self.tick_count} | "
                f"Active: {len(activated_nodes)}/{len(self.graph.nodes)} | "
                f"Duration: {tick_duration:.1f}ms"
            )

    def _get_consciousness_state_name(self, global_energy: float) -> str:
        """Map global energy to consciousness state name."""
        if global_energy < 0.2:
            return "dormant"
        elif global_energy < 0.4:
            return "drowsy"
        elif global_energy < 0.6:
            return "calm"
        elif global_energy < 0.8:
            return "engaged"
        else:
            return "alert"

    def _select_workspace(self, activated_node_ids: List[str], subentity: str) -> List[Node]:
        """
        Select working memory nodes using weight-based scoring with entity-aware weights (Priority 4).

        Score = (energy / tokens) * exp(z_W_effective)
        where z_W_effective uses entity-specific overlays when available

        Args:
            activated_node_ids: IDs of nodes above threshold
            subentity: Subentity to select workspace for (used for entity-aware weight computation)

        Returns:
            List of Node objects selected for workspace
        """
        if not activated_node_ids:
            return []

        # Get activated nodes
        candidates = [self.graph.get_node(nid) for nid in activated_node_ids if self.graph.get_node(nid)]

        # Update baselines for weight standardization
        # Convert Node objects to dicts for WeightLearner
        all_nodes_data = []
        for node in self.graph.nodes.values():
            all_nodes_data.append({
                'name': node.id,
                'node_type': node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type),
                'scope': node.scope,
                'log_weight': node.log_weight
            })
        self.weight_learner.update_baselines(all_nodes_data)

        # Score each candidate
        scored = []
        for node in candidates:
            # Energy per token (simplified - would estimate actual tokens)
            token_count = max(1, len(node.description) // 4)  # Rough estimate: 4 chars per token
            energy = node.E  # Single-energy architecture
            energy_per_token = energy / token_count

            # Standardized weight (entity-aware for Priority 4)
            # Use effective weight when subentity context available
            from orchestration.core.entity_context_extensions import effective_log_weight_node
            effective_log_w = effective_log_weight_node(node, subentity) if subentity else node.log_weight

            z_W = self.weight_learner.standardize_weight(
                effective_log_w,
                node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type),
                node.scope
            )

            # Weight boost (normalized attractor mass)
            W_tilde = math.exp(z_W)

            # Combined score
            score = energy_per_token * W_tilde

            scored.append((node, score, token_count))

        # Sort by score (descending)
        scored.sort(key=lambda x: x[1], reverse=True)

        # Greedy selection with token budget (simplified - would use knapsack)
        budget = 2000  # Token budget for workspace
        selected = []
        total_tokens = 0

        for node, score, tokens in scored:
            if total_tokens + tokens <= budget:
                selected.append(node)
                total_tokens += tokens

        logger.debug(
            f"[Phase 3] Workspace: {len(selected)} nodes selected, "
            f"{total_tokens}/{budget} tokens used"
        )

        return selected

    def _select_workspace_entities(self, subentity: str) -> Tuple[List['Subentity'], Dict]:
        """
        Select working memory entities (entity-first WM per spec §4).

        Selects 5-7 coherent entities instead of scattered nodes.
        Score = (E_entity / token_cost) + diversity_bonus

        Args:
            subentity: Current consciousness subentity

        Returns:
            Tuple of (selected_entities, summary_dict)
            summary_dict format:
            {
                "entities": [
                    {
                        "id": str,
                        "energy": float,
                        "activation_level": str,
                        "top_members": [{"id": str, "energy": float}, ...],
                        "member_count": int
                    },
                    ...
                ],
                "total_entities": int,
                "total_members": int
            }

        Example:
            >>> entities, summary = engine._select_workspace_entities("consciousness_architect")
            >>> # Returns 5-7 most relevant entities with their top members
        """
        if not hasattr(self.graph, 'subentities') or not self.graph.subentities:
            return ([], {
                "entities": [],
                "total_entities": 0,
                "total_members": 0,
                "token_budget_used": 0,
                "token_budget_total": 2000
            })

        # Candidate entities: active first, fallback to top-K by energy if none active
        active_entities = [
            e for e in self.graph.subentities.values()
            if e.energy_runtime >= e.threshold_runtime
        ]

        if not active_entities:
            # Fallback: select top 7 by energy (cold start / low activity)
            all_entities = sorted(
                self.graph.subentities.values(),
                key=lambda e: e.energy_runtime,
                reverse=True
            )
            candidate_entities = all_entities[:7]
            logger.debug("[WM] No active entities, using top-7 by energy fallback")
        else:
            candidate_entities = active_entities

        # Score each candidate entity
        scored_entities = []
        selected_embeddings = []  # Track for diversity bonus

        for entity in candidate_entities:
            # Estimate token cost (rough: 50 tokens per entity summary + 10 per top member)
            top_member_count = min(5, entity.member_count)
            token_cost = 50 + (top_member_count * 10)

            if token_cost == 0:
                continue

            # Energy per token
            energy_per_token = entity.energy_runtime / token_cost if token_cost > 0 else 0.0

            # Diversity bonus (semantic distance from already-selected)
            diversity_bonus = 0.0
            if entity.centroid_embedding is not None and selected_embeddings:
                import numpy as np

                # Compute min cosine distance to selected entities
                min_similarity = 1.0
                for selected_emb in selected_embeddings:
                    norm_entity = np.linalg.norm(entity.centroid_embedding)
                    norm_selected = np.linalg.norm(selected_emb)

                    if norm_entity > 1e-9 and norm_selected > 1e-9:
                        cos_sim = np.dot(entity.centroid_embedding, selected_emb) / (norm_entity * norm_selected)
                        min_similarity = min(min_similarity, cos_sim)

                # Higher diversity = lower similarity
                diversity_bonus = (1.0 - min_similarity) * 0.5  # Scale bonus

            # Combined score
            score = energy_per_token + diversity_bonus

            scored_entities.append((entity, score, token_cost))

        # Sort by score (descending)
        scored_entities.sort(key=lambda x: x[1], reverse=True)

        # Select top 5-7 entities (greedy)
        budget = 2000  # Token budget
        selected_entities = []
        total_tokens = 0
        max_entities = 7

        for entity, score, tokens in scored_entities:
            if len(selected_entities) >= max_entities:
                break

            if total_tokens + tokens <= budget:
                selected_entities.append(entity)
                total_tokens += tokens

                # Add embedding for diversity tracking
                if entity.centroid_embedding is not None:
                    selected_embeddings.append(entity.centroid_embedding)

                # Update entity's WM presence EMA
                entity.ema_wm_presence = 0.1 * 1.0 + 0.9 * entity.ema_wm_presence
            else:
                # Budget exhausted
                break

        # Build summary with top members and token costs
        entity_summaries = []
        entity_token_map = {}  # Track tokens per entity
        total_members = 0

        for entity, score, tokens in scored_entities:
            if entity not in selected_entities:
                continue

            entity_token_map[entity.id] = tokens

            # Get members sorted by energy
            from orchestration.core.types import LinkType
            members = [
                (link.source, link.source.E)
                for link in entity.incoming_links
                if link.link_type == LinkType.BELONGS_TO
            ]
            members.sort(key=lambda x: x[1], reverse=True)

            # Top 5 members
            top_members = [
                {"id": node.id, "energy": round(energy, 4)}
                for node, energy in members[:5]
            ]

            entity_summaries.append({
                "id": entity.id,
                "energy": round(entity.energy_runtime, 4),
                "threshold": round(entity.threshold_runtime, 4),
                "activation_level": entity.activation_level_runtime,
                "stability_state": entity.stability_state,
                "quality_score": round(entity.quality_score, 4),
                "top_members": top_members,
                "member_count": len(members),
                "tokens": tokens  # Add token cost to summary
            })

            total_members += len(members)

        summary = {
            "entities": entity_summaries,
            "total_entities": len(selected_entities),
            "total_members": total_members,
            "token_budget_used": total_tokens,
            "token_budget_total": budget
        }

        logger.debug(
            f"[Step 9] Entity-First WM: {len(selected_entities)} entities selected, "
            f"{total_members} total members, {total_tokens}/{budget} tokens"
        )

        return (selected_entities, summary)

    def _apply_trace_learning(self, trace_result: Dict[str, any]):
        """
        Apply TRACE signals to weight updates.

        Args:
            trace_result: Parsed TRACE result with reinforcement seats and formations
        """
        # Extract reinforcement seats
        reinforcement_seats_nodes = trace_result.get('reinforcement_seats', {})
        reinforcement_seats_links = {}  # Would extract from link reinforcements

        # Extract formations
        node_formations = trace_result.get('node_formations', [])
        link_formations = trace_result.get('link_formations', [])

        # Convert graph nodes to dicts for WeightLearner
        nodes_data = []
        for node in self.graph.nodes.values():
            nodes_data.append({
                'name': node.id,
                'node_type': node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type),
                'scope': node.scope,
                'ema_trace_seats': node.ema_trace_seats,
                'ema_formation_quality': node.ema_formation_quality,
                'ema_wm_presence': node.ema_wm_presence,
                'log_weight': node.log_weight,
                'last_update_timestamp': node.last_update_timestamp
            })

        # Update node weights
        node_updates = self.weight_learner.update_node_weights(
            nodes_data,
            reinforcement_seats_nodes,
            node_formations
        )

        # Apply updates back to nodes
        for update in node_updates:
            node = self.graph.get_node(update.item_id)
            if node:
                node.ema_trace_seats = update.ema_trace_seats_new
                node.ema_formation_quality = update.ema_formation_quality_new
                node.log_weight = update.log_weight_new
                node.last_update_timestamp = datetime.now()

        logger.debug(
            f"[Phase 4] TRACE learning: {len(node_updates)} node weights updated, "
            f"avg delta: {sum(u.delta_log_weight for u in node_updates) / max(1, len(node_updates)):.3f}"
        )

        # === V2 Event: weights.updated (after TRACE learning) ===
        if self.broadcaster and self.broadcaster.is_available() and node_updates:
            import asyncio
            asyncio.create_task(self.broadcaster.broadcast_event("weights.updated", {
                "v": "2",
                "frame_id": self.tick_count,
                "source": "trace",
                "updates": [
                    {
                        "item_id": update.item_id,
                        "type": "node",
                        "log_weight_before": round(update.log_weight_new - update.delta_log_weight, 4),
                        "log_weight_after": round(update.log_weight_new, 4),
                        "signals": {
                            "z_rein": round(update.z_rein, 3),
                            "z_form": round(update.z_form, 3) if update.z_form is not None else 0.0
                        },
                        "eta": round(update.learning_rate, 3)
                    }
                    for update in node_updates[:50]  # Limit to first 50 for performance
                ],
                "t_ms": int(time.time() * 1000)
            }))

        # Update link weights (similar process)
        links_data = []
        for link in self.graph.links.values():
            links_data.append({
                'link_id': link.id,
                'name': link.id,
                'link_type': link.link_type.value if hasattr(link.link_type, 'value') else str(link.link_type),
                'scope': link.scope,
                'ema_trace_seats': link.ema_trace_seats,
                'ema_formation_quality': link.ema_formation_quality,
                'log_weight': link.log_weight,
                'last_update_timestamp': link.last_update_timestamp
            })

        if links_data:
            link_updates = self.weight_learner.update_link_weights(
                links_data,
                reinforcement_seats_links,
                link_formations
            )

            for update in link_updates:
                link = self.graph.get_link(update.item_id)
                if link:
                    link.ema_trace_seats = update.ema_trace_seats_new
                    link.ema_formation_quality = update.ema_formation_quality_new
                    link.log_weight = update.log_weight_new
                    link.last_update_timestamp = datetime.now()

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node by ID."""
        return self.graph.get_node(node_id)

    def inject_stimulus(self, text: str, embedding: Optional[np.ndarray] = None, source_type: str = "user_message"):
        """
        Queue external stimulus for next tick.

        Args:
            text: Stimulus text content
            embedding: Optional pre-computed embedding vector
            source_type: Type of stimulus source (user_message, error_trace, etc.)

        Example:
            >>> engine.inject_stimulus("Test stimulus", source_type="user_message")
        """
        self.stimulus_queue.append({
            'text': text,
            'embedding': embedding,
            'source_type': source_type
        })
        logger.info(f"[ConsciousnessEngineV2] Queued stimulus: {text[:50]}... (type={source_type})")

    def apply_trace(self, trace_result: Dict[str, any]):
        """
        Queue TRACE parse result for next tick learning phase.

        Args:
            trace_result: Parsed TRACE result from trace_parser

        Example:
            >>> from orchestration.libs.trace_parser import TraceParser
            >>> parser = TraceParser()
            >>> result = parser.parse(trace_text)
            >>> engine.apply_trace(result.to_dict())
        """
        self.trace_queue.append(trace_result)
        logger.info(f"[ConsciousnessEngineV2] Queued TRACE result for learning")

    async def persist_to_database(self):
        """
        Persist current graph state to FalkorDB.

        Writes energy values and link weights back to database.
        """
        logger.info("[ConsciousnessEngineV2] Persisting to database...")

        # Persist nodes (energy values)
        for node in self.graph.nodes.values():
            self.adapter.update_node_energy(node)

        # Persist links (weights)
        for link in self.graph.links.values():
            self.adapter.update_link_weight(link)

        logger.info("[ConsciousnessEngineV2] Persistence complete")

    def get_metrics(self) -> Dict:
        """
        Get current engine metrics.

        Returns:
            Metrics dict with tick count, duration, active nodes, etc.
        """
        subentity = self.config.entity_id

        # Count active nodes (sub-entities = nodes with total_energy >= threshold)
        active_count = sum(
            1 for node in self.graph.nodes.values()
            if node.is_active()
        )

        # Get branching ratio state
        branching_state = (
            self.branching_tracker.measure_cycle([], [])
            if self.tick_count > 0
            else None
        )

        return {
            "tick_count": self.tick_count,
            "tick_duration_ms": self.tick_duration_ms,
            "nodes_total": len(self.graph.nodes),
            "links_total": len(self.graph.links),
            "nodes_active": active_count,
            "global_energy": branching_state['global_energy'] if branching_state else 0.0,
            "branching_ratio": branching_state['branching_ratio'] if branching_state else 0.0,
            "last_tick": self.last_tick_time.isoformat()
        }

    def get_status(self) -> Dict[str, any]:
        """
        Get engine status in control API format.

        Returns:
            Status dict compatible with /api/citizen/{id}/status endpoint
        """
        subentity = self.config.entity_id

        # Calculate global energy (average energy across all nodes)
        global_energy = sum(
            node.E
            for node in self.graph.nodes.values()
        ) / max(len(self.graph.nodes), 1)

        # Get consciousness state from energy level
        consciousness_state = self._get_consciousness_state_name(global_energy)

        # Calculate tick frequency
        tick_frequency_hz = 1000.0 / self.config.tick_interval_ms if self.config.tick_interval_ms > 0 else 0.0

        # Time since last tick
        time_since_last_tick = (datetime.now() - self.last_tick_time).total_seconds()

        # Get actual subentity count and IDs
        sub_entity_count = len(self.graph.subentities) if self.graph.subentities else 0
        sub_entity_ids = list(self.graph.subentities.keys()) if self.graph.subentities else []

        # Add 1 for self if not already in list
        if subentity not in sub_entity_ids:
            sub_entity_count += 1
            sub_entity_ids.insert(0, subentity)

        return {
            "citizen_id": subentity,
            "running_state": "running" if self.running else "paused",
            "tick_count": self.tick_count,
            "tick_interval_ms": self.config.tick_interval_ms,
            "tick_frequency_hz": round(tick_frequency_hz, 2),
            "tick_multiplier": 1.0,  # V2 doesn't support speed multiplier yet
            "consciousness_state": consciousness_state,
            "time_since_last_event": round(time_since_last_tick, 2),
            "sub_entity_count": sub_entity_count,
            "sub_entities": sub_entity_ids,
            "nodes": len(self.graph.nodes),
            "links": len(self.graph.links)
        }
# Force reload


## <<< END orchestration/mechanisms/consciousness_engine_v2.py
---

## >>> BEGIN orchestration/mechanisms/sub_entity_core.py
<!-- mtime: 2025-10-22T21:44:26; size_chars: 18962 -->

"""
Sub-Entity Core Data Structures

Provides the foundational classes for sub-entity traversal:
- SubEntity: Main subentity class with extent, frontier, energy tracking
- EntityExtentCentroid: O(1) online centroid + semantic dispersion
- ROITracker: Rolling ROI statistics (Q1/Q3/IQR for convergence)
- QuantileTracker: General rolling quantiles for integration/size tracking

Author: AI #1
Created: 2025-10-20
Dependencies: numpy
Zero-Constants: All thresholds derived from rolling statistics
"""

import numpy as np
from typing import Set, Dict, Optional
from collections import deque


class EntityExtentCentroid:
    """
    Online centroid + dispersion tracking for semantic diversity measurement.

    O(1) updates as nodes activate/deactivate (not O(m²) pairwise).
    Dispersion = mean(1 - cos(node_embedding, centroid))

    Low dispersion → narrow semantic extent → completeness hunger activates
    High dispersion → broad semantic extent → completeness satisfied
    """

    def __init__(self, embedding_dim: int = 768):
        """
        Initialize empty centroid.

        Args:
            embedding_dim: Embedding dimension (default 768 for all-mpnet-base-v2)
        """
        self.n = 0
        self.centroid = np.zeros(embedding_dim)
        self.dispersion = 0.0
        self.active_embeddings = []  # For dispersion recomputation

    def add_node(self, embedding: np.ndarray):
        """
        Node became active - update centroid incrementally.

        Args:
            embedding: Node embedding vector (768-dim)
        """
        if self.n == 0:
            self.centroid = embedding.copy()
            self.n = 1
            self.active_embeddings = [embedding]
            self.dispersion = 0.0
        else:
            # Incremental centroid update: C_new = (n*C_old + e) / (n+1)
            self.centroid = ((self.n * self.centroid) + embedding) / (self.n + 1)
            self.n += 1
            self.active_embeddings.append(embedding)

            # Renormalize centroid to unit length for cosine distance
            norm = np.linalg.norm(self.centroid)
            if norm > 1e-9:
                self.centroid = self.centroid / norm

            # Recompute dispersion: mean(1 - cos(e, centroid))
            self._update_dispersion()

    def remove_node(self, embedding: np.ndarray):
        """
        Node deactivated - update centroid.

        Args:
            embedding: Node embedding vector (768-dim)
        """
        if self.n == 0:
            return

        if self.n == 1:
            # Last node removed - reset to empty
            self.centroid = np.zeros_like(self.centroid)
            self.n = 0
            self.active_embeddings = []
            self.dispersion = 0.0
        else:
            # Remove from active list
            self.active_embeddings = [e for e in self.active_embeddings
                                     if not np.allclose(e, embedding)]
            self.n = len(self.active_embeddings)

            # Recompute centroid from scratch (safer than decremental)
            if self.n > 0:
                self.centroid = np.mean(self.active_embeddings, axis=0)
                norm = np.linalg.norm(self.centroid)
                if norm > 1e-9:
                    self.centroid = self.centroid / norm
                self._update_dispersion()
            else:
                self.centroid = np.zeros_like(self.centroid)
                self.dispersion = 0.0

    def distance_to(self, embedding: np.ndarray) -> float:
        """
        Compute semantic distance from target to current extent centroid.

        Used for completeness hunger: favor nodes distant from current extent.

        Args:
            embedding: Target node embedding

        Returns:
            Distance score (1 - cosine similarity)
        """
        if self.n == 0:
            return 1.0  # Maximum distance from empty extent

        # Cosine similarity: cos(θ) = (a·b) / (||a|| ||b||)
        # Embeddings are already normalized, centroid is normalized
        norm_emb = np.linalg.norm(embedding)
        norm_cent = np.linalg.norm(self.centroid)

        if norm_emb < 1e-9 or norm_cent < 1e-9:
            return 1.0  # Degenerate case

        cos_sim = np.dot(embedding, self.centroid) / (norm_emb * norm_cent)
        cos_sim = np.clip(cos_sim, -1.0, 1.0)  # Numerical stability

        # Distance = 1 - cosine similarity (range [0, 2])
        # 0 = identical direction, 1 = orthogonal, 2 = opposite
        return 1.0 - cos_sim

    def _update_dispersion(self):
        """
        Internal: Recompute dispersion from active embeddings.

        Dispersion = mean(1 - cos(e, centroid)) across active nodes
        """
        if self.n == 0:
            self.dispersion = 0.0
            return

        distances = [self.distance_to(e) for e in self.active_embeddings]
        self.dispersion = np.mean(distances) if distances else 0.0


class IdentityEmbedding:
    """
    Tracks subentity's idsubentity center via EMA of active nodes.

    Idsubentity = "Who am I?" = Semantic center of what I've explored
    Different from centroid (current extent) - this is historical idsubentity
    """

    def __init__(self, embedding_dim: int = 768):
        """
        Initialize idsubentity tracker.

        Args:
            embedding_dim: Embedding dimension (default 768)
        """
        self.identity_embedding = np.zeros(embedding_dim)
        self.initialized = False
        self.ema_weight = 0.95  # Slow drift (idsubentity is stable)
        self.embedding_dim = embedding_dim

    def update(self, active_nodes: Set[int], graph):
        """
        Update idsubentity embedding from current active nodes.

        Args:
            active_nodes: Set of currently active node IDs
            graph: Consciousness graph
        """
        if len(active_nodes) == 0:
            return

        # Compute centroid of current active nodes
        embeddings = [graph.nodes[nid]['embedding'] for nid in active_nodes
                     if nid in graph.nodes and 'embedding' in graph.nodes[nid]]

        if len(embeddings) == 0:
            return

        current_centroid = np.mean(embeddings, axis=0)

        # Normalize
        norm = np.linalg.norm(current_centroid)
        if norm > 1e-9:
            current_centroid = current_centroid / norm

        if not self.initialized:
            # First update: Bootstrap idsubentity from current extent
            self.identity_embedding = current_centroid
            self.initialized = True
        else:
            # EMA update: Slow drift toward new experiences
            self.identity_embedding = (
                self.ema_weight * self.identity_embedding +
                (1 - self.ema_weight) * current_centroid
            )

            # Renormalize
            norm = np.linalg.norm(self.identity_embedding)
            if norm > 1e-9:
                self.identity_embedding = self.identity_embedding / norm

    def coherence_with(self, embedding: np.ndarray) -> float:
        """
        Measure coherence between target and idsubentity.

        Args:
            embedding: Target embedding (768-dim)

        Returns:
            coherence: Cosine similarity with idsubentity [0, 1]
        """
        if not self.initialized:
            return 0.5  # Neutral before idsubentity forms

        # Normalize embedding
        norm_emb = np.linalg.norm(embedding)
        if norm_emb < 1e-9:
            return 0.5

        embedding_norm = embedding / norm_emb

        similarity = np.dot(embedding_norm, self.identity_embedding)
        return max(0.0, similarity)


class BetaLearner:
    """
    Learn beta exponent for integration gate from merge outcomes.

    Tracks:
    - Merge events (small -> large merges)
    - ROI impact of merges
    - Adjusts beta to maximize ROI from successful merges
    """

    def __init__(self):
        """Initialize beta learner with neutral beta=1.0"""
        self.beta = 1.0  # Start neutral
        self.merge_history = []  # Recent merge observations
        self.update_frequency = 50  # Update beta every 50 observations

    def observe_potential_merge(
        self,
        small_entity,
        large_entity,
        merged: bool,
        roi_before: float,
        roi_after: float
    ):
        """
        Record merge outcome for learning.

        Args:
            small_entity: Smaller subentity involved
            large_entity: Larger subentity involved
            merged: Whether subentities actually merged (overlap > 50%)
            roi_before: Average ROI before potential merge
            roi_after: Average ROI after merge/no-merge
        """
        # Compute size ratio
        small_size = sum(small_entity.get_energy(n) for n in small_entity.extent)
        large_size = sum(large_entity.get_energy(n) for n in large_entity.extent)
        size_ratio = large_size / (small_size + 1e-9)

        # ROI impact
        roi_impact = roi_after - roi_before

        self.merge_history.append({
            'size_ratio': size_ratio,
            'merged': merged,
            'roi_impact': roi_impact,
            'small_size': small_size,
            'large_size': large_size
        })

        # Update beta periodically
        if len(self.merge_history) >= self.update_frequency:
            self._update_beta()
            self.merge_history = []

    def _update_beta(self):
        """
        Update beta based on merge outcomes.

        Strategy:
        - If merges (with current beta) improve ROI -> increase beta (more merge pressure)
        - If merges hurt ROI -> decrease beta (less merge pressure)
        """
        if len(self.merge_history) < 10:
            return  # Need more data

        # Separate successful vs unsuccessful merges
        successful_merges = [
            m for m in self.merge_history
            if m['merged'] and m['roi_impact'] > 0
        ]

        # Compute success rate
        total_merges = len([m for m in self.merge_history if m['merged']])
        if total_merges == 0:
            return  # No merges to learn from

        success_rate = len(successful_merges) / total_merges

        # Adjust beta based on success rate
        if success_rate > 0.7:
            # Merges are working well, increase beta (more merge pressure)
            self.beta *= 1.1
        elif success_rate < 0.3:
            # Merges are failing, decrease beta (less merge pressure)
            self.beta *= 0.9
        # else: 30-70% success rate -> keep beta stable

        # Clip to reasonable range
        self.beta = np.clip(self.beta, 0.5, 2.0)

    def get_beta(self) -> float:
        """Get current beta value"""
        return self.beta


class ROITracker:
    """
    Rolling ROI statistics for convergence detection.

    Maintains Q1, Q3, IQR over recent stride ROI values.
    Convergence criterion: predicted_roi < Q1 - 1.5*IQR (lower whisker)

    Zero-constants: Threshold adapts to THIS subentity's performance baseline.
    """

    def __init__(self, window_size: int = 256):
        """
        Initialize ROI tracker.

        Args:
            window_size: Number of recent ROI values to track
        """
        self.window = deque(maxlen=window_size)

    def push(self, roi: float):
        """
        Record ROI from stride execution.

        Args:
            roi: gap_reduced / stride_time_us
        """
        self.window.append(roi)

    def lower_whisker(self) -> float:
        """
        Compute convergence threshold: Q1 - 1.5 * IQR

        Returns:
            Lower whisker value (stop when predicted ROI below this)
        """
        if len(self.window) < 4:
            # Insufficient data - no convergence threshold yet
            return float('-inf')

        data = np.array(list(self.window))
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1

        whisker = q1 - 1.5 * iqr
        return whisker


class QuantileTracker:
    """
    General rolling quantiles for integration/size distributions.

    Tracks E_others/E_self ratios and subentity sizes to determine:
    - "Strong field" detection (ratio > Q75)
    - Strategy determination (size < Q25 = merge_seeking, > Q75 = independent)

    Zero-constants: Quantiles recomputed every frame from current population.
    """

    def __init__(self, window_size: int = 100):
        """
        Initialize quantile tracker.

        Args:
            window_size: Number of recent samples
        """
        self.window = deque(maxlen=window_size)

    def update(self, value: float):
        """
        Add sample to rolling distribution.

        Args:
            value: Observed ratio or size
        """
        self.window.append(value)

    def quantile(self, p: float) -> float:
        """
        Compute p-th quantile of current distribution.

        Args:
            p: Quantile level (0.25 for Q25, 0.75 for Q75)

        Returns:
            Quantile value
        """
        if len(self.window) == 0:
            return 0.0  # No data

        data = np.array(list(self.window))
        return np.percentile(data, p * 100)


class SubEntity:
    """
    Main sub-entity class for traversal.

    Represents one active pattern traversing the graph, with:
    - Extent: nodes above threshold for this subentity
    - Frontier: extent ∪ 1-hop neighbors
    - Energy channels: per-node energy tracking
    - Centroid: semantic diversity tracking
    - ROI: convergence detection

    Zero-constants: All behavior from rolling statistics and live state.
    """

    def __init__(self, entity_id: str, embedding_dim: int = 768):
        """
        Initialize sub-entity.

        Args:
            entity_id: Unique subentity identifier
            embedding_dim: Embedding dimension
        """
        self.id = entity_id

        # Extent tracking
        self.extent: Set[int] = set()         # Node IDs above threshold
        self.frontier: Set[int] = set()       # Extent ∪ 1-hop

        # Energy tracking (views into graph state)
        self.energies: Dict[int, float] = {}  # E[entity_id, node_id]
        self.thresholds: Dict[int, float] = {}  # θ[entity_id, node_id]

        # Quota & convergence
        self.quota_assigned = 0
        self.quota_remaining = 0

        # ROI tracking for convergence
        self.roi_tracker = ROITracker(window_size=256)

        # Semantic diversity
        self.centroid = EntityExtentCentroid(embedding_dim)

        # Idsubentity tracking
        self.idsubentity = IdentityEmbedding(embedding_dim)

        # Beta learning for integration gate
        self.beta_learner = BetaLearner()

        # Local health
        self.rho_local_ema = 1.0  # EMA of local spectral radius

        # Hunger baselines (for surprise gates)
        self.hunger_baselines: Dict[str, tuple[float, float]] = {
            # hunger_name -> (μ, σ) EMA
            'homeostasis': (0.0, 1.0),
            'goal': (0.0, 1.0),
            'idsubentity': (0.0, 1.0),
            'completeness': (0.0, 1.0),
            'complementarity': (0.0, 1.0),
            'integration': (0.0, 1.0),
            'ease': (0.0, 1.0),
        }

    def get_energy(self, node_id: int) -> float:
        """Get subentity's energy at node."""
        return self.energies.get(node_id, 0.0)

    def get_threshold(self, node_id: int) -> float:
        """Get subentity's threshold at node."""
        return self.thresholds.get(node_id, 0.1)

    def is_active(self, node_id: int) -> bool:
        """Check if node is above threshold for this subentity."""
        return self.get_energy(node_id) >= self.get_threshold(node_id)

    def update_extent(self, graph):
        """
        Recompute extent and frontier from current energy state.

        Args:
            graph: Graph object with nodes and edges
        """
        old_extent = self.extent.copy()

        # Recompute extent: nodes above threshold
        new_extent = set()
        for node_id in graph.nodes:
            if self.is_active(node_id):
                new_extent.add(node_id)

        # Track centroid changes
        activated = new_extent - old_extent
        deactivated = old_extent - new_extent

        # Update centroid incrementally
        for node_id in deactivated:
            if node_id in graph.nodes and 'embedding' in graph.nodes[node_id]:
                self.centroid.remove_node(graph.nodes[node_id]['embedding'])

        for node_id in activated:
            if node_id in graph.nodes and 'embedding' in graph.nodes[node_id]:
                self.centroid.add_node(graph.nodes[node_id]['embedding'])

        self.extent = new_extent

        # Compute frontier: extent ∪ 1-hop neighbors
        frontier = self.extent.copy()
        for node_id in self.extent:
            if node_id in graph:
                # Add all outgoing neighbors
                for neighbor in graph.neighbors(node_id):
                    frontier.add(neighbor)

        self.frontier = frontier

    def compute_size(self, graph) -> float:
        """
        Compute subentity size (total_energy × mean_link_weight).

        Used for strategy determination (merge_seeking vs independent).

        Args:
            graph: Graph object

        Returns:
            Subentity size metric
        """
        if len(self.extent) == 0:
            return 0.0

        # Total energy in extent
        total_energy = sum(self.get_energy(node_id) for node_id in self.extent)

        # Mean link weight within extent (internal connectivity)
        link_weights = []
        for node_id in self.extent:
            if node_id in graph:
                for neighbor in graph.neighbors(node_id):
                    if neighbor in self.extent:
                        # Internal link
                        edge_data = graph.get_edge_data(node_id, neighbor)
                        if edge_data and 'weight' in edge_data:
                            link_weights.append(edge_data['weight'])

        if len(link_weights) == 0:
            # No internal links - use total energy only
            return total_energy

        mean_weight = np.mean(link_weights)

        # Size = total_energy × mean_internal_link_weight
        # High energy + strong internal links = large robust subentity
        return total_energy * mean_weight


## <<< END orchestration/mechanisms/sub_entity_core.py
---

## >>> BEGIN orchestration/mechanisms/sub_entity_traversal.py
<!-- mtime: 2025-10-23T01:07:45; size_chars: 31349 -->

"""
Two-Scale Traversal - Entity → Atomic Selection

ARCHITECTURAL PRINCIPLE: Traversal operates at two scales to reduce branching.

Phase 1 Implementation (shipped):
- Between-entity: Score entities by 5 hungers, pick next entity, select representative nodes
- Within-entity: Existing atomic stride selection constrained to entity members
- Budget split: Softmax over entity hungers determines entity allocation

This is the DEFAULT architecture (TWO_SCALE_ENABLED=true).

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/subentity_layer/subentity_layer.md §2.4
Status: STABLE (Phase 1 shipped, Phase 2 gated by flags)
"""

import math
import numpy as np
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.subentity import Subentity
    from orchestration.core.node import Node


# === Phase 1: Slim Hunger Set ===

@dataclass
class EntityHungerScores:
    """
    Hunger scores for entity selection (Phase 1: 5 hungers).

    Each hunger ∈ [0, 1] represents motivation to activate this entity.
    Higher score = more attractive.
    """
    entity_id: str
    goal_fit: float  # Alignment with current goal embedding
    integration: float  # Semantic distance (novelty/complementarity)
    completeness: float  # How much of entity is already active
    ease: float  # Boundary precedence from RELATES_TO
    novelty: float  # Unexplored entity (low ema_active)
    total_score: float  # Softmax-weighted combination


def compute_goal_fit(
    entity: 'Subentity',
    goal_embedding: Optional[np.ndarray]
) -> float:
    """
    Compute goal alignment hunger (higher = more aligned).

    Uses cosine similarity between entity centroid and goal embedding.

    Args:
        entity: Candidate entity
        goal_embedding: Current goal vector

    Returns:
        Goal fit score ∈ [0, 1]
    """
    if goal_embedding is None or entity.centroid_embedding is None:
        return 0.5  # Neutral

    norm_goal = np.linalg.norm(goal_embedding)
    norm_entity = np.linalg.norm(entity.centroid_embedding)

    if norm_goal < 1e-9 or norm_entity < 1e-9:
        return 0.5

    cos_sim = np.dot(goal_embedding, entity.centroid_embedding) / (norm_goal * norm_entity)

    # Map [-1, 1] → [0, 1]
    return (cos_sim + 1.0) / 2.0


def compute_integration_hunger(
    current_entity: 'Subentity',
    candidate_entity: 'Subentity'
) -> float:
    """
    Compute integration hunger (semantic distance).

    Higher distance = more integration potential (novelty/complementarity).

    Args:
        current_entity: Entity we're currently in
        candidate_entity: Entity we're considering

    Returns:
        Integration score ∈ [0, 1] (higher = more distant/novel)
    """
    if (current_entity.centroid_embedding is None or
        candidate_entity.centroid_embedding is None):
        return 0.5  # Neutral

    norm_curr = np.linalg.norm(current_entity.centroid_embedding)
    norm_cand = np.linalg.norm(candidate_entity.centroid_embedding)

    if norm_curr < 1e-9 or norm_cand < 1e-9:
        return 0.5

    cos_sim = np.dot(current_entity.centroid_embedding, candidate_entity.centroid_embedding) / (norm_curr * norm_cand)

    # Distance = 1 - similarity (higher distance = more integration)
    return 1.0 - ((cos_sim + 1.0) / 2.0)


def compute_completeness_hunger(entity: 'Subentity') -> float:
    """
    Compute completeness hunger (how much already active).

    Lower completeness = more room to explore.

    Args:
        entity: Candidate entity

    Returns:
        Completeness score ∈ [0, 1] (higher = more incomplete)
    """
    if entity.member_count == 0:
        return 0.0

    # Get active members (E >= theta)
    from orchestration.core.types import LinkType
    active_count = sum(
        1 for link in entity.incoming_links
        if link.link_type == LinkType.BELONGS_TO and link.source.is_active()
    )

    completeness_ratio = active_count / entity.member_count

    # Invert: high incompleteness = high hunger
    return 1.0 - completeness_ratio


def compute_ease_hunger(
    current_entity: 'Subentity',
    candidate_entity: 'Subentity',
    graph: 'Graph'
) -> float:
    """
    Compute ease hunger (boundary precedence from RELATES_TO).

    Strong RELATES_TO link = easy to traverse = high hunger.

    Args:
        current_entity: Entity we're currently in
        candidate_entity: Entity we're considering
        graph: Graph containing RELATES_TO links

    Returns:
        Ease score ∈ [0, 1]
    """
    from orchestration.core.types import LinkType

    # Find RELATES_TO link
    for link in current_entity.outgoing_links:
        if (link.link_type == LinkType.RELATES_TO and
            link.target.id == candidate_entity.id):
            # Found link - convert log_weight to ease
            ease = math.exp(link.log_weight)
            # Normalize to [0, 1] (assuming log_weight ∈ [-5, 2])
            normalized = (ease - 0.007) / (7.4 - 0.007)  # exp(-5) to exp(2)
            return np.clip(normalized, 0.0, 1.0)

    # No link = neutral ease
    return 0.5


def compute_novelty_hunger(entity: 'Subentity') -> float:
    """
    Compute novelty hunger (unexplored entity).

    Low ema_active = high novelty = high hunger.

    Args:
        entity: Candidate entity

    Returns:
        Novelty score ∈ [0, 1]
    """
    # Invert ema_active: low activation history = high novelty
    return 1.0 - entity.ema_active


def score_entity_hungers(
    current_entity: Optional['Subentity'],
    candidate_entity: 'Subentity',
    goal_embedding: Optional[np.ndarray],
    graph: 'Graph',
    hunger_weights: Optional[Dict[str, float]] = None
) -> EntityHungerScores:
    """
    Score candidate entity across all hungers (Phase 1: 5 hungers).

    Args:
        current_entity: Entity we're currently in (None if first selection)
        candidate_entity: Entity to score
        goal_embedding: Current goal vector
        graph: Graph containing entities and links
        hunger_weights: Optional weights for each hunger (default: uniform)

    Returns:
        EntityHungerScores with individual and total scores
    """
    if hunger_weights is None:
        hunger_weights = {
            "goal_fit": 0.25,
            "integration": 0.20,
            "completeness": 0.20,
            "ease": 0.20,
            "novelty": 0.15
        }

    # Compute individual hungers
    goal_fit = compute_goal_fit(candidate_entity, goal_embedding)

    integration = 0.5  # Default if no current entity
    if current_entity:
        integration = compute_integration_hunger(current_entity, candidate_entity)

    completeness = compute_completeness_hunger(candidate_entity)

    ease = 0.5  # Default if no current entity
    if current_entity:
        ease = compute_ease_hunger(current_entity, candidate_entity, graph)

    novelty = compute_novelty_hunger(candidate_entity)

    # Weighted total
    total_score = (
        hunger_weights["goal_fit"] * goal_fit +
        hunger_weights["integration"] * integration +
        hunger_weights["completeness"] * completeness +
        hunger_weights["ease"] * ease +
        hunger_weights["novelty"] * novelty
    )

    return EntityHungerScores(
        entity_id=candidate_entity.id,
        goal_fit=goal_fit,
        integration=integration,
        completeness=completeness,
        ease=ease,
        novelty=novelty,
        total_score=total_score
    )


def choose_next_entity(
    current_entity: Optional['Subentity'],
    active_entities: List['Subentity'],
    goal_embedding: Optional[np.ndarray],
    graph: 'Graph',
    hunger_weights: Optional[Dict[str, float]] = None
) -> Tuple[Optional['Subentity'], Optional[EntityHungerScores]]:
    """
    Choose next entity to expand using hunger-based scoring (Phase 1).

    Algorithm:
    1. Score all active entities (or all entities if no current)
    2. Apply softmax to get distribution
    3. Sample from distribution (deterministic: argmax for now)

    Args:
        current_entity: Current entity (None if first selection)
        active_entities: Entities above threshold
        goal_embedding: Current goal vector
        graph: Graph containing entities
        hunger_weights: Optional hunger weights

    Returns:
        Tuple of (selected_entity, scores) or (None, None) if no candidates
    """
    if not active_entities:
        return (None, None)

    # Score all candidates
    scored = [
        (entity, score_entity_hungers(current_entity, entity, goal_embedding, graph, hunger_weights))
        for entity in active_entities
        if entity != current_entity  # Don't select current entity
    ]

    if not scored:
        return (None, None)

    # Sort by total score (deterministic argmax for Phase 1)
    scored.sort(key=lambda x: x[1].total_score, reverse=True)

    # TODO Phase 2: Sample from softmax distribution instead of argmax
    best_entity, best_scores = scored[0]

    return (best_entity, best_scores)


def select_representative_nodes(
    source_entity: 'Subentity',
    target_entity: 'Subentity'
) -> Tuple[Optional['Node'], Optional['Node']]:
    """
    Select representative nodes for boundary stride (Phase 1 strategy).

    Strategy:
    - Source: Highest-E active member (E >= theta)
    - Target: Member with largest (gap-to-theta) × ease

    Args:
        source_entity: Entity energy flows from
        target_entity: Entity energy flows to

    Returns:
        Tuple of (source_node, target_node) or (None, None) if no valid pair
    """
    from orchestration.core.types import LinkType

    # Get source members (active only)
    source_members = [
        link.source for link in source_entity.incoming_links
        if link.link_type == LinkType.BELONGS_TO and link.source.is_active()
    ]

    if not source_members:
        return (None, None)

    # Source: max E_i
    source_node = max(source_members, key=lambda n: n.E)

    # Get target members
    target_members = [
        link.source for link in target_entity.incoming_links
        if link.link_type == LinkType.BELONGS_TO
    ]

    if not target_members:
        return (None, None)

    # Target: max (gap × ease)
    # Gap = theta - E (how much room to fill)
    # Ease = average incoming link weight
    def score_target(node):
        gap = max(0.0, node.theta - node.E)

        # Ease: average exp(log_weight) of incoming links
        if not node.incoming_links:
            ease = 1.0
        else:
            ease = sum(math.exp(link.log_weight) for link in node.incoming_links) / len(node.incoming_links)

        return gap * ease

    target_node = max(target_members, key=score_target)

    return (source_node, target_node)


def split_stride_budget_by_entity(
    entity_scores: List[EntityHungerScores],
    total_budget: int
) -> Dict[str, int]:
    """
    Split stride budget across entities using softmax over hunger scores.

    Args:
        entity_scores: List of scored entities
        total_budget: Total strides available this frame

    Returns:
        Dict of entity_id → stride_budget
    """
    if not entity_scores:
        return {}

    # Softmax over total scores
    scores = np.array([s.total_score for s in entity_scores])
    exp_scores = np.exp(scores - np.max(scores))  # Numerical stability
    softmax = exp_scores / exp_scores.sum()

    # Allocate budget proportionally
    budget_allocation = {}
    remaining_budget = total_budget

    for i, entity_score in enumerate(entity_scores):
        allocated = int(softmax[i] * total_budget)
        budget_allocation[entity_score.entity_id] = allocated
        remaining_budget -= allocated

    # Distribute remainder to highest-scored entity
    if remaining_budget > 0 and entity_scores:
        top_entity = max(entity_scores, key=lambda s: s.total_score)
        budget_allocation[top_entity.entity_id] += remaining_budget

    return budget_allocation


# === PR-B: Coherence Persistence Tracking ===

def update_coherence_persistence(
    entity: 'Subentity',
    current_affect: Optional[np.ndarray]
) -> None:
    """
    Update coherence persistence counter (PR-B: Emotion Couplings).

    Tracks consecutive frames where affect remains similar (coherence lock-in risk).
    Increments counter when cos(A_curr, A_prev) > threshold.
    Resets counter when affect changes significantly.

    Args:
        entity: Subentity to update
        current_affect: Current affective state vector

    Side effects:
        - Updates entity.coherence_persistence (increments or resets)
        - Updates entity.prev_affect_for_coherence (stores current)
    """
    from orchestration.core.settings import settings

    # Feature flag check
    if not settings.RES_DIMINISH_ENABLED:
        return

    # Guard: need current affect
    if current_affect is None or len(current_affect) == 0:
        entity.coherence_persistence = 0
        entity.prev_affect_for_coherence = None
        return

    # First frame: store affect, no persistence yet
    if entity.prev_affect_for_coherence is None:
        entity.prev_affect_for_coherence = current_affect.copy()
        entity.coherence_persistence = 0
        return

    # Compute cosine similarity with previous affect
    curr_norm = np.linalg.norm(current_affect)
    prev_norm = np.linalg.norm(entity.prev_affect_for_coherence)

    if curr_norm < 1e-6 or prev_norm < 1e-6:
        # Affect too weak, reset
        entity.coherence_persistence = 0
        entity.prev_affect_for_coherence = current_affect.copy()
        return

    dot_product = np.dot(current_affect, entity.prev_affect_for_coherence)
    cos_similarity = dot_product / (curr_norm * prev_norm)

    # Check if still coherent (same affective state)
    if cos_similarity > settings.COHERENCE_SIMILARITY_THRESHOLD:
        # Same state: increment persistence counter
        entity.coherence_persistence += 1
    else:
        # State changed: reset counter
        entity.coherence_persistence = 0

    # Store current affect for next frame
    entity.prev_affect_for_coherence = current_affect.copy()


def compute_effective_lambda_res(
    entity: 'Subentity',
    base_lambda_res: float = 0.5
) -> float:
    """
    Compute effective resonance strength with coherence diminishing returns (PR-B).

    After P frames of coherence persistence, resonance strength decays exponentially
    to prevent lock-in (rumination, obsession, spiral).

    Formula:
        λ_res_effective = λ_res * exp(-γ * max(0, persistence - P))

    Where:
        - λ_res = base resonance strength (default 0.5)
        - γ = COHERENCE_DECAY_RATE (default 0.05)
        - P = COHERENCE_PERSISTENCE_THRESHOLD (default 20 frames)
        - persistence = consecutive frames in same affective state

    Returns λ_res when disabled or below threshold (no decay).

    Args:
        entity: Subentity with coherence persistence tracking
        base_lambda_res: Base resonance strength (default 0.5)

    Returns:
        Effective resonance strength (decayed if persistence > P)

    Example:
        >>> entity.coherence_persistence = 25  # 5 frames over threshold
        >>> lambda_res_eff = compute_effective_lambda_res(entity, 0.5)
        >>> # lambda_res_eff = 0.5 * exp(-0.05 * 5) = 0.5 * 0.78 = 0.39
        >>> # 22% reduction (diminishing returns kicking in)
    """
    from orchestration.core.settings import settings
    from orchestration.core.telemetry import get_emitter

    # Feature flag check
    if not settings.RES_DIMINISH_ENABLED:
        return base_lambda_res

    # Compute excess persistence (frames beyond threshold)
    P = settings.COHERENCE_PERSISTENCE_THRESHOLD
    excess = max(0, entity.coherence_persistence - P)

    if excess == 0:
        # Below threshold: no decay
        lambda_res_effective = base_lambda_res
        lock_in_risk = False
    else:
        # Above threshold: exponential decay
        gamma = settings.COHERENCE_DECAY_RATE
        decay_factor = np.exp(-gamma * excess)
        lambda_res_effective = base_lambda_res * decay_factor
        lock_in_risk = (entity.coherence_persistence > P + 10)  # Warning at P+10

    # Emit telemetry event
    if settings.AFFECTIVE_TELEMETRY_ENABLED:
        emitter = get_emitter()
        emitter.emit_affective_event(
            "coherence_persistence",
            citizen_id="unknown",  # Will be set by caller
            frame_id=None,  # Will be set by caller
            entity_id=entity.id,
            coherence_persistence=entity.coherence_persistence,
            lambda_res_effective=float(lambda_res_effective),
            lock_in_risk=lock_in_risk
        )

    return float(lambda_res_effective)


# === PR-C: Multi-Pattern Affective Response ===

def compute_regulation_pattern(
    active_affect: np.ndarray,
    emotion_magnitude: float,
    control_capacity: float
) -> float:
    """
    Compute regulation pattern score (PR-C: Multi-Pattern Response).

    Regulation pattern: Intentional dampening of emotional response.
    Works when control capacity is high.

    Formula:
        score_reg = control_capacity * (1 - tanh(||A||))

    High control + low affect → high regulation score
    (System has capacity to regulate)

    Args:
        active_affect: Current affective state vector
        emotion_magnitude: Magnitude of emotion vector
        control_capacity: Available control capacity [0, 1]

    Returns:
        Regulation pattern score [0, 1]

    Example:
        >>> A = np.array([0.2, 0.0, 0.0])  # Weak affect
        >>> score = compute_regulation_pattern(A, 0.5, 0.8)
        >>> # High control, low affect → good regulation opportunity
    """
    A_magnitude = float(np.linalg.norm(active_affect))

    # Regulation score: high control × low affect
    # tanh(||A||) → [0, 1], so (1 - tanh(||A||)) → [1, 0]
    # More affect → harder to regulate
    regulation_potential = 1.0 - np.tanh(A_magnitude)
    score = control_capacity * regulation_potential

    return float(np.clip(score, 0.0, 1.0))


def compute_rumination_pattern(
    active_affect: np.ndarray,
    emotion_magnitude: float,
    valence: float
) -> float:
    """
    Compute rumination pattern score (PR-C: Multi-Pattern Response).

    Rumination pattern: Intensification of negative affect.
    Occurs when valence negative and affect strong.

    Formula:
        score_rum = max(0, -valence) * tanh(||A||)

    Negative valence + strong affect → high rumination score
    (System spiraling into negative state)

    Args:
        active_affect: Current affective state vector
        emotion_magnitude: Magnitude of emotion vector
        valence: Emotional valence [-1, 1] (negative = bad)

    Returns:
        Rumination pattern score [0, 1]

    Example:
        >>> A = np.array([1.0, 0.0, 0.0])  # Strong affect
        >>> score = compute_rumination_pattern(A, 0.8, -0.7)
        >>> # Negative valence + strong affect → rumination risk
    """
    A_magnitude = float(np.linalg.norm(active_affect))

    # Rumination score: negative valence × strong affect
    # Only ruminate when valence < 0 (negative state)
    negative_intensity = max(0.0, -valence)
    affect_strength = np.tanh(A_magnitude)
    score = negative_intensity * affect_strength

    return float(np.clip(score, 0.0, 1.0))


def compute_distraction_pattern(
    active_affect: np.ndarray,
    emotion_magnitude: float,
    control_capacity: float,
    valence: float
) -> float:
    """
    Compute distraction pattern score (PR-C: Multi-Pattern Response).

    Distraction pattern: Shift attention away from current affect.
    Works when regulation insufficient but some control remains.

    Formula:
        score_dist = (1 - control_capacity) * tanh(||A||) * max(0, -valence)

    Low control + strong negative affect → high distraction score
    (Can't regulate, need to redirect attention)

    Args:
        active_affect: Current affective state vector
        emotion_magnitude: Magnitude of emotion vector
        control_capacity: Available control capacity [0, 1]
        valence: Emotional valence [-1, 1]

    Returns:
        Distraction pattern score [0, 1]

    Example:
        >>> A = np.array([0.8, 0.0, 0.0])  # Strong affect
        >>> score = compute_distraction_pattern(A, 0.7, 0.3, -0.6)
        >>> # Low control + strong negative → distraction needed
    """
    A_magnitude = float(np.linalg.norm(active_affect))

    # Distraction score: low control × strong negative affect
    depletion = 1.0 - control_capacity  # Inverted control
    affect_strength = np.tanh(A_magnitude)
    negative_intensity = max(0.0, -valence)

    score = depletion * affect_strength * negative_intensity

    return float(np.clip(score, 0.0, 1.0))


def compute_pattern_scores(
    active_affect: np.ndarray,
    emotion_magnitude: float,
    control_capacity: float,
    valence: float
) -> tuple[float, float, float]:
    """
    Compute all three pattern scores.

    Args:
        active_affect: Current affective state vector
        emotion_magnitude: Magnitude of emotion vector
        control_capacity: Available control capacity [0, 1]
        valence: Emotional valence [-1, 1]

    Returns:
        Tuple of (score_reg, score_rum, score_dist)
    """
    score_reg = compute_regulation_pattern(active_affect, emotion_magnitude, control_capacity)
    score_rum = compute_rumination_pattern(active_affect, emotion_magnitude, valence)
    score_dist = compute_distraction_pattern(active_affect, emotion_magnitude, control_capacity, valence)

    return (score_reg, score_rum, score_dist)


def compute_pattern_weights(
    scores: tuple[float, float, float],
    pattern_effectiveness: Dict[str, float]
) -> np.ndarray:
    """
    Compute pattern weights using softmax over scores × effectiveness.

    Weights sum to 1.0 and represent probability of selecting each pattern.

    Args:
        scores: Tuple of (score_reg, score_rum, score_dist)
        pattern_effectiveness: EMA effectiveness for each pattern

    Returns:
        Numpy array of weights [w_reg, w_rum, w_dist]

    Example:
        >>> scores = (0.8, 0.3, 0.2)
        >>> eff = {"regulation": 0.7, "rumination": 0.5, "distraction": 0.6}
        >>> weights = compute_pattern_weights(scores, eff)
        >>> # weights sum to 1.0, regulation dominant
    """
    score_reg, score_rum, score_dist = scores

    # Modulate scores by effectiveness
    eff_reg = pattern_effectiveness.get("regulation", 0.5)
    eff_rum = pattern_effectiveness.get("rumination", 0.5)
    eff_dist = pattern_effectiveness.get("distraction", 0.5)

    adjusted_scores = np.array([
        score_reg * eff_reg,
        score_rum * eff_rum,
        score_dist * eff_dist
    ])

    # Softmax (with numerical stability)
    exp_scores = np.exp(adjusted_scores - np.max(adjusted_scores))
    weights = exp_scores / exp_scores.sum()

    return weights


def compute_unified_multiplier(
    active_affect: np.ndarray,
    emotion_magnitude: float,
    control_capacity: float,
    valence: float,
    pattern_weights: np.ndarray
) -> float:
    """
    Compute unified affective multiplier using weighted pattern combination (PR-C).

    This REPLACES the simple m_affect from PR-B when PR-C is enabled.

    Formula:
        m_reg = 1 - λ_reg * tanh(||A||)  # Dampening
        m_rum = 1 + λ_rum * tanh(||A||) * max(0, -valence)  # Intensification
        m_dist = 1 - λ_dist * tanh(||A||) * (1 - control_capacity)  # Dampening via attention shift

        m_affect_unified = w_reg * m_reg + w_rum * m_rum + w_dist * m_dist

    Bounded by [M_AFFECT_MIN, M_AFFECT_MAX].

    Args:
        active_affect: Current affective state vector
        emotion_magnitude: Magnitude of emotion vector
        control_capacity: Available control capacity [0, 1]
        valence: Emotional valence [-1, 1]
        pattern_weights: Softmax weights [w_reg, w_rum, w_dist]

    Returns:
        Unified affective multiplier (clamped to bounds)
    """
    from orchestration.core.settings import settings

    A_magnitude = float(np.linalg.norm(active_affect))
    A_tanh = np.tanh(A_magnitude)

    # Compute individual pattern multipliers
    lambda_reg = settings.LAMBDA_REG
    lambda_rum = settings.LAMBDA_RUM
    lambda_dist = settings.LAMBDA_DIST

    # Regulation: dampens response (m < 1)
    m_reg = 1.0 - lambda_reg * A_tanh

    # Rumination: intensifies negative response (m > 1 when valence < 0)
    negative_intensity = max(0.0, -valence)
    m_rum = 1.0 + lambda_rum * A_tanh * negative_intensity

    # Distraction: dampens via attention shift (m < 1 when control low)
    depletion = 1.0 - control_capacity
    m_dist = 1.0 - lambda_dist * A_tanh * depletion

    # Weighted combination
    w_reg, w_rum, w_dist = pattern_weights
    m_affect_unified = w_reg * m_reg + w_rum * m_rum + w_dist * m_dist

    # Clamp to bounds
    m_min = settings.M_AFFECT_MIN
    m_max = settings.M_AFFECT_MAX
    m_affect_unified = np.clip(m_affect_unified, m_min, m_max)

    return float(m_affect_unified)


def apply_rumination_cap(
    entity: 'Subentity',
    selected_pattern: str,
    pattern_weights: np.ndarray
) -> np.ndarray:
    """
    Apply rumination cap: force weight to 0 after consecutive threshold.

    Safety mechanism to prevent indefinite rumination spirals.

    Args:
        entity: Subentity with rumination counter
        selected_pattern: Currently dominant pattern
        pattern_weights: Current weights [w_reg, w_rum, w_dist]

    Returns:
        Adjusted weights (rumination zeroed if cap exceeded)

    Side effects:
        - Updates entity.rumination_frames_consecutive
    """
    from orchestration.core.settings import settings

    if selected_pattern == "rumination":
        entity.rumination_frames_consecutive += 1
    else:
        entity.rumination_frames_consecutive = 0

    # Check if cap exceeded
    if entity.rumination_frames_consecutive >= settings.RUMINATION_CAP:
        # Force rumination weight to 0, renormalize
        adjusted_weights = pattern_weights.copy()
        adjusted_weights[1] = 0.0  # Zero out rumination (index 1)

        # Renormalize remaining weights
        total = adjusted_weights.sum()
        if total > 0:
            adjusted_weights = adjusted_weights / total
        else:
            # Fallback: equal weights for reg/dist
            adjusted_weights = np.array([0.5, 0.0, 0.5])

        return adjusted_weights

    return pattern_weights


def get_selected_pattern(pattern_weights: np.ndarray) -> str:
    """
    Get selected pattern name based on weights.

    Args:
        pattern_weights: Weights [w_reg, w_rum, w_dist]

    Returns:
        Pattern name ("regulation", "rumination", or "distraction")
    """
    max_idx = int(np.argmax(pattern_weights))
    pattern_names = ["regulation", "rumination", "distraction"]
    return pattern_names[max_idx]


def update_pattern_effectiveness(
    entity: 'Subentity',
    pattern_name: str,
    outcome_score: float
) -> None:
    """
    Update pattern effectiveness using EMA (PR-C: Pattern Learning).

    Effectiveness tracks how well each pattern achieves its goals:
    - Regulation: Did affect intensity decrease?
    - Rumination: Did it lead to spiraling (bad) or insight (good)?
    - Distraction: Did it enable recovery?

    Args:
        entity: Subentity with pattern_effectiveness dict
        pattern_name: Pattern to update ("regulation", "rumination", "distraction")
        outcome_score: Success score [0, 1] (1 = pattern worked well)

    Side effects:
        - Updates entity.pattern_effectiveness[pattern_name] via EMA
    """
    from orchestration.core.settings import settings

    alpha = settings.PATTERN_EFFECTIVENESS_EMA_ALPHA

    # Get current effectiveness
    current_eff = entity.pattern_effectiveness.get(pattern_name, 0.5)

    # Update via EMA
    # new_eff = alpha * outcome + (1 - alpha) * old_eff
    new_eff = alpha * outcome_score + (1.0 - alpha) * current_eff

    # Clamp to [0, 1]
    new_eff = np.clip(new_eff, 0.0, 1.0)

    # Store
    entity.pattern_effectiveness[pattern_name] = float(new_eff)


def compute_regulation_outcome(
    affect_before: np.ndarray,
    affect_after: np.ndarray
) -> float:
    """
    Compute regulation outcome score (did affect decrease?).

    Args:
        affect_before: Affect magnitude before regulation
        affect_after: Affect magnitude after regulation

    Returns:
        Outcome score [0, 1] (1 = successful dampening)
    """
    mag_before = float(np.linalg.norm(affect_before))
    mag_after = float(np.linalg.norm(affect_after))

    if mag_before < 1e-6:
        return 0.5  # Neutral if no affect to begin with

    # Compute reduction ratio
    reduction = (mag_before - mag_after) / mag_before

    # Map to [0, 1] range
    # reduction > 0 → dampened (good), < 0 → intensified (bad)
    outcome = 0.5 + 0.5 * np.tanh(reduction)

    return float(np.clip(outcome, 0.0, 1.0))


def compute_rumination_outcome(
    affect_magnitude: float,
    spiral_detected: bool,
    insight_gained: bool
) -> float:
    """
    Compute rumination outcome score.

    Rumination can be:
    - Bad: Spiraling without insight (low score)
    - Good: Deep processing leading to insight (high score)

    Args:
        affect_magnitude: Current affect strength
        spiral_detected: True if affect spiraling upward
        insight_gained: True if pattern led to insight/resolution

    Returns:
        Outcome score [0, 1]
    """
    if insight_gained:
        return 0.8  # Productive rumination

    if spiral_detected:
        return 0.2  # Unproductive spiral

    # Neutral: rumination without clear outcome
    return 0.5


def compute_distraction_outcome(
    recovery_enabled: bool,
    attention_shifted: bool
) -> float:
    """
    Compute distraction outcome score (did it enable recovery?).

    Args:
        recovery_enabled: True if affect decreased after distraction
        attention_shifted: True if attention successfully redirected

    Returns:
        Outcome score [0, 1]
    """
    if recovery_enabled and attention_shifted:
        return 0.9  # Successful distraction

    if recovery_enabled or attention_shifted:
        return 0.6  # Partial success

    return 0.3  # Distraction didn't help


## <<< END orchestration/mechanisms/sub_entity_traversal.py
---

## >>> BEGIN orchestration/mechanisms/weight_learning_v2.py
<!-- mtime: 2025-10-24T19:47:21; size_chars: 12403 -->

"""
Weight Learning V2 - Entity-context-aware TRACE reinforcement.

Implements dual-view weight architecture (Priority 4):
- Global weights: Updated by 20% of TRACE signal
- Entity overlays: Updated by 80% of TRACE signal (membership-weighted)
- Effective weight = global + overlay@E (computed at read-time)

Designer: Felix "Ironhand" - 2025-10-25
Reference: Nicolas's Priority 4 architecture guide
"""

import numpy as np
from scipy.stats import rankdata, norm
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WeightUpdate:
    """Result of weight learning update with entity attribution."""
    item_id: str
    item_type: str  # node type or link type
    scope: str

    # EMA updates
    ema_trace_seats_new: float
    ema_formation_quality_new: Optional[float]

    # Z-scores
    z_rein: float
    z_form: Optional[float]

    # Weight changes
    delta_log_weight_global: float
    log_weight_new: float

    # Entity-specific overlays
    local_overlays: List[Dict[str, Any]]  # [{"entity": "e1", "delta": 0.11}, ...]

    # Metadata
    cohort_size: int
    learning_rate: float


class WeightLearnerV2:
    """
    Entity-context-aware TRACE weight learning.

    Implements dual-view architecture:
    - 20% of signal → global weight (cross-entity learning)
    - 80% of signal → entity overlays (context-specific learning)

    Membership weights modulate local reinforcement strength.
    """

    def __init__(
        self,
        alpha: float = 0.1,
        min_cohort_size: int = 3,
        alpha_local: float = 0.8,
        alpha_global: float = 0.2,
        overlay_cap: float = 2.0
    ):
        """
        Initialize weight learner with entity context support.

        Args:
            alpha: EMA decay rate (default 0.1 = recent 10 TRACEs)
            min_cohort_size: Minimum cohort size for z-score computation
            alpha_local: Fraction of signal to entity overlays (default 0.8)
            alpha_global: Fraction of signal to global weight (default 0.2)
            overlay_cap: Maximum absolute overlay value (prevents runaway)
        """
        self.alpha = alpha
        self.min_cohort_size = min_cohort_size
        self.alpha_local = alpha_local
        self.alpha_global = alpha_global
        self.overlay_cap = overlay_cap

        # Cohort baselines for read-time standardization
        self.baselines = {}  # {(type, scope): (μ, σ)}

        logger.info(
            f"[WeightLearnerV2] Initialized with α={alpha}, "
            f"local={alpha_local:.1f}, global={alpha_global:.1f}"
        )

    def update_node_weights(
        self,
        nodes: List[Dict[str, Any]],
        reinforcement_seats: Dict[str, int],
        formations: List[Dict[str, Any]],
        entity_context: Optional[List[str]] = None
    ) -> List[WeightUpdate]:
        """
        Update node weights from TRACE signals with entity context.

        Args:
            nodes: Current node states from graph
            reinforcement_seats: {node_id: seats} from Hamilton apportionment
            formations: Node formations with quality metrics
            entity_context: Active entity IDs during this TRACE (from WM or explicit)

        Returns:
            List of WeightUpdate results with entity attribution
        """
        updates = []

        # Build cohorts by (type, scope)
        cohorts = self._build_cohorts(nodes)

        # Get membership weights for context entities
        membership_weights = self._get_membership_weights(nodes, entity_context or [])

        # Process reinforcement signals
        for node in nodes:
            node_id = node.get('name')
            if not node_id:
                continue

            # Get reinforcement seats (0 if not mentioned)
            delta_seats = reinforcement_seats.get(node_id, 0)

            # Get formation quality (None if not formed this TRACE)
            formation = next((f for f in formations if f['fields'].get('name') == node_id), None)
            formation_quality = formation['quality'] if formation else None

            # Update EMAs
            ema_trace_seats_old = float(node.get('ema_trace_seats') or 0.0)
            ema_formation_quality_old = float(node.get('ema_formation_quality') or 0.0)

            ema_trace_seats_new = self.alpha * delta_seats + (1 - self.alpha) * ema_trace_seats_old

            if formation_quality is not None:
                ema_formation_quality_new = self.alpha * formation_quality + (1 - self.alpha) * ema_formation_quality_old
            else:
                ema_formation_quality_new = ema_formation_quality_old

            # Compute cohort z-scores
            node_type = node.get('node_type', 'unknown')
            scope = node.get('scope', 'personal')
            cohort_key = (node_type, scope)

            z_rein, z_form, cohort_size = self._compute_z_scores(
                node_id,
                ema_trace_seats_new,
                ema_formation_quality_new if formation_quality is not None else None,
                cohorts.get(cohort_key, [])
            )

            # Compute adaptive learning rate
            last_update = node.get('last_update_timestamp')
            eta = self._compute_learning_rate(last_update)

            # Total signal strength
            z_total = z_rein + (z_form if z_form is not None else 0)

            # === DUAL-VIEW UPDATE (Priority 4) ===

            # 1. Global weight update (20% of signal)
            delta_log_weight_global = self.alpha_global * eta * z_total
            log_weight_old = float(node.get('log_weight') or 0.0)
            log_weight_new = log_weight_old + delta_log_weight_global

            # 2. Entity overlay updates (80% of signal, membership-weighted)
            local_overlays = []
            if entity_context and delta_seats != 0:
                for entity_id in entity_context:
                    # Get membership weight for this node-entity pair
                    membership_weight = membership_weights.get(node_id, {}).get(entity_id, 0.0)

                    if membership_weight > 0.0:
                        # Local delta scaled by membership
                        delta_overlay = self.alpha_local * eta * z_total * membership_weight

                        # Clamp overlay to prevent runaway
                        overlay_old = node.get('log_weight_overlays', {}).get(entity_id, 0.0)
                        overlay_new = np.clip(
                            overlay_old + delta_overlay,
                            -self.overlay_cap,
                            self.overlay_cap
                        )

                        local_overlays.append({
                            "entity": entity_id,
                            "delta": float(delta_overlay),
                            "overlay_before": float(overlay_old),
                            "overlay_after": float(overlay_new),
                            "membership_weight": float(membership_weight)
                        })

            # Create update result
            update = WeightUpdate(
                item_id=node_id,
                item_type=node_type,
                scope=scope,
                ema_trace_seats_new=ema_trace_seats_new,
                ema_formation_quality_new=ema_formation_quality_new,
                z_rein=z_rein,
                z_form=z_form,
                delta_log_weight_global=delta_log_weight_global,
                log_weight_new=log_weight_new,
                local_overlays=local_overlays,
                cohort_size=cohort_size,
                learning_rate=eta
            )

            updates.append(update)

            # Logging
            if local_overlays:
                overlays_str = ", ".join([f"{o['entity']}: {o['delta']:+.3f}" for o in local_overlays])
                logger.debug(
                    f"[WeightLearnerV2] Node {node_id}: "
                    f"global={delta_log_weight_global:+.3f}, "
                    f"overlays=[{overlays_str}]"
                )

        logger.info(f"[WeightLearnerV2] Updated {len(updates)} node weights with entity context")
        return updates

    def _get_membership_weights(
        self,
        nodes: List[Dict[str, Any]],
        entity_context: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """
        Extract membership weights for nodes in entity context.

        Args:
            nodes: Node states
            entity_context: Active entity IDs

        Returns:
            Dict[node_id, Dict[entity_id, membership_weight]]
        """
        membership_weights = {}

        for node in nodes:
            node_id = node.get('name')
            if not node_id:
                continue

            # Get BELONGS_TO memberships from node
            # (Assumes memberships stored in node.properties or similar)
            # TODO: Get from graph.get_links_by_type(BELONGS_TO) filtered by node_id
            memberships = node.get('memberships', {})  # {entity_id: weight}

            # Filter to active entity context
            context_memberships = {
                entity_id: weight
                for entity_id, weight in memberships.items()
                if entity_id in entity_context and weight > 0.0
            }

            if context_memberships:
                membership_weights[node_id] = context_memberships

        return membership_weights

    def _build_cohorts(self, items: List[Dict[str, Any]]) -> Dict[Tuple[str, str], List[Dict]]:
        """Group items by (type, scope) for rank-z normalization."""
        cohorts = {}
        for item in items:
            item_type = item.get('node_type') or item.get('link_type', 'unknown')
            scope = item.get('scope', 'personal')
            key = (item_type, scope)

            if key not in cohorts:
                cohorts[key] = []
            cohorts[key].append(item)

        return cohorts

    def _compute_z_scores(
        self,
        item_id: str,
        ema_trace: float,
        ema_quality: Optional[float],
        cohort: List[Dict]
    ) -> Tuple[float, Optional[float], int]:
        """Compute rank-based z-scores within cohort."""
        if len(cohort) < self.min_cohort_size:
            # Fallback: use raw EMAs as z-scores
            z_rein = ema_trace / 10.0  # Normalize roughly
            z_form = (ema_quality / 1.0) if ema_quality is not None else None
            return z_rein, z_form, len(cohort)

        # Extract EMAs for cohort
        trace_values = [float(item.get('ema_trace_seats', 0.0)) for item in cohort]
        quality_values = [float(item.get('ema_formation_quality', 0.0)) for item in cohort] if ema_quality is not None else None

        # Rank-based z-scores (van der Waerden)
        ranks_trace = rankdata(trace_values, method='average')
        z_rein = norm.ppf(ranks_trace / (len(trace_values) + 1))

        # Find this item's position
        item_idx = next((i for i, item in enumerate(cohort) if item.get('name') == item_id), 0)
        z_rein_item = z_rein[item_idx]

        z_form_item = None
        if ema_quality is not None and quality_values:
            ranks_quality = rankdata(quality_values, method='average')
            z_form = norm.ppf(ranks_quality / (len(quality_values) + 1))
            z_form_item = z_form[item_idx]

        return float(z_rein_item), float(z_form_item) if z_form_item is not None else None, len(cohort)

    def _compute_learning_rate(self, last_update: Optional[datetime]) -> float:
        """Adaptive learning rate: η = 1 - exp(-Δt / τ)"""
        if last_update is None:
            return 1.0  # First update

        delta_t = (datetime.now() - last_update).total_seconds()
        tau = 86400.0  # 1 day half-life
        eta = 1.0 - np.exp(-delta_t / tau)
        return float(np.clip(eta, 0.01, 1.0))

    # Similar update_link_weights() method would follow same pattern
    # (Omitted for brevity - same dual-view logic applies)


## <<< END orchestration/mechanisms/weight_learning_v2.py
---

## >>> BEGIN orchestration/mechanisms/entity_activation.py
<!-- mtime: 2025-10-23T01:03:19; size_chars: 31137 -->

"""
Entity Activation - Deriving subentity energy from single-node substrate.

ARCHITECTURAL PRINCIPLE: Single-energy per node, entity energy is DERIVED.

Formula (spec: subentity_layer.md §2.2):
    E_entity = Σ (m̃_iE × max(0, E_i - Θ_i))

Where:
    - E_i = node activation energy (node.E)
    - Θ_i = node threshold (node.theta)
    - m̃_iE = normalized membership weight from BELONGS_TO link
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
    Normalize BELONGS_TO membership weights to sum to 1.0.

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
    # Get members via BELONGS_TO links
    from orchestration.core.types import LinkType

    members_with_weights = []
    for link in entity.incoming_links:
        if link.link_type != LinkType.BELONGS_TO:
            continue

        node = link.source
        membership_weight = link.weight  # BELONGS_TO.weight ∈ [0,1]
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
            if link.link_type == LinkType.BELONGS_TO:
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
    if entity.low_quality_streak >= dissolution_streak_required:
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

    This removes the entity from the graph and deletes all BELONGS_TO links
    to its members. Members return to the atomic node pool.

    Args:
        graph: Graph containing the entity
        entity: Entity to dissolve

    Side effects:
        - Removes entity from graph.subentities
        - Deletes all BELONGS_TO links to this entity
        - Members become free-floating nodes

    Example:
        >>> dissolve_entity(graph, low_quality_entity)
        >>> # Entity removed, members available for other entities
    """
    from orchestration.core.types import LinkType

    # Remove all BELONGS_TO links (release members)
    belongs_to_links = [
        link for link in entity.incoming_links
        if link.link_type == LinkType.BELONGS_TO
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
            quality_score = compute_entity_quality_score(entity)
            transition = update_entity_lifecycle(entity, quality_score)

            if transition:
                lifecycle_transitions.append(transition)

                # Mark for dissolution if state is "dissolved"
                if transition.new_state == "dissolved":
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
                   if link.link_type == LinkType.BELONGS_TO]

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


## <<< END orchestration/mechanisms/entity_activation.py
---

## >>> BEGIN orchestration/mechanisms/multi_energy.py
<!-- mtime: 2025-10-22T21:44:26; size_chars: 11358 -->

"""
Mechanism 01: Multi-Energy Architecture - Pure Functions

CRITICAL ARCHITECTURAL PRINCIPLES (CORRECTED 2025-10-20):
1. Energy is strictly non-negative [0.0, ∞) - UNBOUNDED
2. Inhibition is LINK-BASED (SUPPRESS links), NOT value-based (negative energy)
3. Each subentity has independent energy on each node
4. Bounded GROWTH (not bounded values) prevents numerical overflow
5. Near-zero cleanup maintains graph efficiency

Energy Storage:
    Node.energy: Dict[entity_id, float]
    - Key: subentity identifier (str)
    - Value: raw energy >= 0.0 (unbounded)

Energy Bounds:
    Range: [0.0, ∞) - no maximum cap
    Growth: Logarithmic dampening at high values prevents overflow
    Negative values: Clamped to 0.0

Growth Control:
    Energy can grow arbitrarily large (panic, excitement states)
    But growth RATE slows at high values via log dampening
    This prevents numerical overflow while allowing unbounded values

Why Unbounded Energy:
    - Panic mode: Energy needs to boost repeatedly
    - Excitement: Sustained high-energy states
    - No arbitrary ceiling on consciousness intensity

Cleanup:
    If energy < THRESHOLD, remove from dict
    - THRESHOLD = 0.001 (configurable)
    - Prevents accumulation of near-zero values
    - Reduces memory and query cost

Author: Felix (Engineer)
Created: 2025-10-19
Updated: 2025-10-20 - Removed tanh saturation, implemented unbounded energy
Spec: Based on Nicolas's architectural corrections 2025-10-20
"""

import numpy as np
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from orchestration.core.node import Node
    from orchestration.core.types import EntityID

# --- Configuration ---

ENERGY_MIN: float = 0.0  # Minimum energy (non-negative only)
CLEANUP_THRESHOLD: float = 0.001  # Remove energy below this threshold
GROWTH_DAMPENING: float = 0.1  # Logarithmic dampening factor for high-energy growth


# --- Core Energy Operations ---

def get_entity_energy(node: 'Node', subentity: 'EntityID') -> float:
    """
    Get energy for subentity on node.

    Args:
        node: Node to query
        subentity: Subentity identifier

    Returns:
        Energy value (>= 0.0), or 0.0 if subentity not present

    Example:
        >>> node = Node(id="n1", ...)
        >>> set_entity_energy(node, "validator", 0.5)
        >>> get_entity_energy(node, "validator")
        0.462  # tanh(2.0 * 0.5)
        >>> get_entity_energy(node, "other")
        0.0
    """
    return node.energy.get(subentity, 0.0)


def get_total_energy(node: 'Node') -> float:
    """
    Get TOTAL energy across all subentities on this node.

    This is the canonical energy used for sub-entity activation detection.
    Per spec (05_sub_entity_system.md:1514-1522):
        Sub-Entity = ANY Active Node
        is_sub_entity(node) = total_energy >= threshold

    Args:
        node: Node to query

    Returns:
        Sum of energy across all subentity keys

    Example:
        >>> node.energy = {'felix': 3.0, 'iris': 2.0}
        >>> get_total_energy(node)
        5.0
    """
    return float(sum(node.energy.values()))


def set_entity_energy(node: 'Node', subentity: 'EntityID', value: float) -> None:
    """
    Set energy for subentity on node with cleanup.

    CRITICAL: Energy is strictly non-negative [0.0, ∞) - UNBOUNDED.
    Negative values are clamped to 0.0.

    Process:
    1. Clamp to non-negative: max(0.0, value)
    2. Store in node.energy dict (raw value, no saturation)
    3. Cleanup if < THRESHOLD

    Args:
        node: Node to modify
        subentity: Subentity identifier
        value: Energy value (will be clamped to >= 0.0, stored as-is)

    Example:
        >>> node = Node(id="n1", ...)
        >>> set_entity_energy(node, "validator", 1.0)
        >>> node.energy["validator"]
        1.0  # Raw value stored
        >>> set_entity_energy(node, "validator", 100.0)
        >>> node.energy["validator"]
        100.0  # High energy allowed (panic/excitement)
        >>> set_entity_energy(node, "validator", -0.5)  # Negative clamped
        >>> node.energy["validator"]
        0.0
    """
    # 1. Clamp to non-negative
    clamped = max(0.0, value)

    # 2. Store raw value (no saturation)
    node.energy[subentity] = clamped

    # 3. Cleanup near-zero
    if clamped < CLEANUP_THRESHOLD:
        node.energy.pop(subentity, None)


def add_entity_energy(node: 'Node', subentity: 'EntityID', delta: float) -> None:
    """
    Add energy delta to subentity (can be positive or negative).

    With logarithmic dampening for large positive additions to prevent overflow.

    Process:
    1. Get current energy
    2. Apply dampening to large positive deltas: delta_eff = sign(delta) * log(1 + abs(delta))
    3. Add dampened delta: new = current + delta_eff
    4. Set new energy (clamped to non-negative)

    Args:
        node: Node to modify
        subentity: Subentity identifier
        delta: Energy change (positive = add, negative = subtract)

    Example:
        >>> node = Node(id="n1", ...)
        >>> set_entity_energy(node, "validator", 0.5)
        >>> add_entity_energy(node, "validator", 0.2)
        >>> get_entity_energy(node, "validator")
        0.682  # 0.5 + log(1 + 0.2) * GROWTH_DAMPENING
        >>> add_entity_energy(node, "validator", 100.0)  # Large addition
        >>> get_entity_energy(node, "validator")
        # Still grows but dampened: 0.682 + log(1 + 100) * GROWTH_DAMPENING ~= 1.14
    """
    current = get_entity_energy(node, subentity)

    # Apply logarithmic dampening to prevent overflow on large additions
    if delta > 0:
        # Dampen positive delta: effective delta = log(1 + delta) / dampening_factor
        delta_effective = np.log(1.0 + delta) / (1.0 / GROWTH_DAMPENING)
    else:
        # Negative delta (energy removal) - no dampening needed
        delta_effective = delta

    new_value = current + delta_effective
    set_entity_energy(node, subentity, new_value)


def multiply_entity_energy(node: 'Node', subentity: 'EntityID', factor: float) -> None:
    """
    Multiply subentity energy by factor (for decay, diffusion).

    Process:
    1. Get current energy
    2. Multiply by factor
    3. Set new energy (clamped to non-negative)

    Args:
        node: Node to modify
        subentity: Subentity identifier
        factor: Multiplication factor (e.g., 0.9 for decay)

    Example:
        >>> node = Node(id="n1", ...)
        >>> set_entity_energy(node, "validator", 0.8)
        >>> multiply_entity_energy(node, "validator", 0.5)  # 50% decay
        >>> get_entity_energy(node, "validator")
        0.4  # 0.8 * 0.5
        >>> set_entity_energy(node, "validator", 100.0)
        >>> multiply_entity_energy(node, "validator", 0.9)  # Decay
        >>> get_entity_energy(node, "validator")
        90.0  # High energy decays proportionally
    """
    current = get_entity_energy(node, subentity)
    if current > 0:
        new_value = current * factor
        set_entity_energy(node, subentity, new_value)


def get_all_active_entities(node: 'Node') -> List['EntityID']:
    """
    Get all subentities with non-zero energy on node.

    Returns:
        List of subentity IDs with energy > 0

    Example:
        >>> node = Node(id="n1", ...)
        >>> set_entity_energy(node, "validator", 0.5)
        >>> set_entity_energy(node, "translator", 0.3)
        >>> get_all_active_entities(node)
        ['validator', 'translator']
    """
    return list(node.energy.keys())


def clear_entity_energy(node: 'Node', subentity: 'EntityID') -> None:
    """
    Remove subentity energy from node entirely.

    Args:
        node: Node to modify
        subentity: Subentity identifier

    Example:
        >>> node = Node(id="n1", ...)
        >>> set_entity_energy(node, "validator", 0.5)
        >>> clear_entity_energy(node, "validator")
        >>> get_entity_energy(node, "validator")
        0.0
    """
    node.energy.pop(subentity, None)


def clear_all_energy(node: 'Node') -> None:
    """
    Remove all energy from node (all subentities).

    Args:
        node: Node to modify

    Example:
        >>> node = Node(id="n1", ...)
        >>> set_entity_energy(node, "validator", 0.5)
        >>> set_entity_energy(node, "translator", 0.3)
        >>> clear_all_energy(node)
        >>> len(node.energy)
        0
    """
    node.energy.clear()


# --- Energy Statistics ---

def get_total_energy(node: 'Node') -> float:
    """
    Get sum of all subentity energies on node.

    Returns:
        Sum of all energy values

    Example:
        >>> node = Node(id="n1", ...)
        >>> set_entity_energy(node, "validator", 0.5)
        >>> set_entity_energy(node, "translator", 0.3)
        >>> get_total_energy(node)
        0.754  # tanh(2*0.5) + tanh(2*0.3)
    """
    return sum(node.energy.values())


def get_max_entity_energy(node: 'Node') -> tuple['EntityID', float]:
    """
    Get subentity with maximum energy on node.

    Returns:
        Tuple of (entity_id, energy_value), or (None, 0.0) if no energy

    Example:
        >>> node = Node(id="n1", ...)
        >>> set_entity_energy(node, "validator", 0.5)
        >>> set_entity_energy(node, "translator", 0.8)
        >>> get_max_entity_energy(node)
        ('translator', 0.664)
    """
    if not node.energy:
        return (None, 0.0)

    max_entity = max(node.energy.items(), key=lambda x: x[1])
    return max_entity


def get_energy_distribution(node: 'Node') -> Dict['EntityID', float]:
    """
    Get normalized energy distribution (percentages).

    Returns:
        Dict mapping subentity to percentage of total energy

    Example:
        >>> node = Node(id="n1", ...)
        >>> set_entity_energy(node, "validator", 0.5)
        >>> set_entity_energy(node, "translator", 0.5)
        >>> get_energy_distribution(node)
        {'validator': 0.5, 'translator': 0.5}
    """
    total = get_total_energy(node)
    if total == 0:
        return {}

    return {subentity: energy / total for subentity, energy in node.energy.items()}


# --- Energy Isolation Verification ---

def verify_energy_isolation(node: 'Node') -> bool:
    """
    Verify that all energy values are non-negative.

    Energy is unbounded [0, ∞), so no upper limit check.

    This is a diagnostic function for testing and validation.

    Returns:
        True if all energy values are valid, False otherwise

    Example:
        >>> node = Node(id="n1", ...)
        >>> set_entity_energy(node, "validator", 0.5)
        >>> verify_energy_isolation(node)
        True
        >>> set_entity_energy(node, "panic", 100.0)  # High energy OK
        >>> verify_energy_isolation(node)
        True
        >>> node.energy["bad"] = -0.5  # Manual corruption
        >>> verify_energy_isolation(node)
        False
    """
    for subentity, energy in node.energy.items():
        if energy < 0.0:
            return False  # Negative energy detected
        # No upper bound check - energy can be arbitrarily large
    return True


## <<< END orchestration/mechanisms/multi_energy.py
---

## >>> BEGIN orchestration/mechanisms/quotas.py
<!-- mtime: 2025-10-22T21:44:26; size_chars: 9140 -->

"""
Hamilton Quota Allocation with Per-Frame Normalization

Implements fair stride budget distribution across subentities using:
- Inverse-size weighting (small subentities get more strides per node)
- Modulation factors (urgency, reachability, health)
- Hamilton's largest remainder method (unbiased integer allocation)
- Per-frame normalization (zero-constants compliance)

Author: AI #2
Created: 2025-10-20
Dependencies: sub_entity_core
Zero-Constants: All factors normalized to mean=1.0 per-frame
"""

from typing import List, Dict
from orchestration.mechanisms.sub_entity_core import SubEntity


def compute_modulation_factors(
    subentities: List[SubEntity],
    graph,
    recent_stimuli
) -> Dict[str, Dict[str, float]]:
    """
    Compute urgency, reachability, health factors for each subentity.

    All factors normalized to mean=1.0 across current active subentities.

    Args:
        subentities: Active sub-entities this frame
        graph: Graph object
        recent_stimuli: Recent stimulus history (list of dicts with 'embedding' key)

    Returns:
        Dict[entity_id -> {urgency, reachability, health}]
    """
    import numpy as np

    if not subentities:
        return {}

    N = len(subentities)
    factors = {}

    # === URGENCY: Cosine similarity to recent stimuli ===
    urgency_raw = {}
    for subentity in subentities:
        if not recent_stimuli or subentity.centroid.n == 0:
            # No stimuli or empty extent → neutral urgency
            urgency_raw[subentity.id] = 1.0
        else:
            # Max cosine similarity to recent stimuli
            max_sim = 0.0
            for stimulus in recent_stimuli:
                if 'embedding' in stimulus:
                    stim_emb = stimulus['embedding']
                    # Cosine similarity = 1 - distance
                    distance = subentity.centroid.distance_to(stim_emb)
                    similarity = max(0.0, 1.0 - distance)  # Clamp to [0,1]
                    max_sim = max(max_sim, similarity)
            urgency_raw[subentity.id] = max_sim

    # === REACHABILITY: Inverse distance to high-energy workspace nodes ===
    # Heuristic: Distance from extent centroid to workspace centroid
    # (Simplified version - full version would track actual workspace)
    reachability_raw = {}
    for subentity in subentities:
        if subentity.centroid.n == 0:
            reachability_raw[subentity.id] = 1.0
        else:
            # For Phase 1: assume all subentities equally reachable
            # Phase 2+: Implement actual workspace distance
            reachability_raw[subentity.id] = 1.0

    # === HEALTH: Inverse of local spectral radius ===
    health_raw = {}
    for subentity in subentities:
        # Lower rho = healthier = higher health factor
        # rho near 1.0 = edge of criticality (neutral health)
        # rho > 1.0 = unstable (low health)
        # rho < 1.0 = stable (high health)
        rho = subentity.rho_local_ema
        if rho > 0.0:
            health_raw[subentity.id] = 1.0 / rho
        else:
            health_raw[subentity.id] = 1.0  # Degenerate case

    # === NORMALIZATION: Mean = 1.0 per factor ===
    def normalize_to_mean_one(raw_values: Dict[str, float]) -> Dict[str, float]:
        """Normalize so mean across subentities = 1.0"""
        values = list(raw_values.values())
        if not values:
            return raw_values

        mean_val = np.mean(values)
        if mean_val <= 1e-9:
            # All values near zero - return uniform
            return {eid: 1.0 for eid in raw_values.keys()}

        return {eid: v / mean_val for eid, v in raw_values.items()}

    urgency_norm = normalize_to_mean_one(urgency_raw)
    reachability_norm = normalize_to_mean_one(reachability_raw)
    health_norm = normalize_to_mean_one(health_raw)

    # === OPTIONAL SHRINKAGE (commented out for Phase 1) ===
    # N_0 = N  # Shrinkage prior
    # urgency_shrunk = {eid: (N * u + N_0) / (N + N_0)
    #                   for eid, u in urgency_norm.items()}

    # === COMBINE FACTORS ===
    for subentity in subentities:
        factors[subentity.id] = {
            'urgency': urgency_norm[subentity.id],
            'reachability': reachability_norm[subentity.id],
            'health': health_norm[subentity.id]
        }

    return factors


def hamilton_quota_allocation(
    subentities: List[SubEntity],
    Q_total: int,
    weights: Dict[str, float]
) -> Dict[str, int]:
    """
    Allocate integer quotas using Hamilton's largest remainder method.

    Prevents rounding bias that could systematically favor certain subentities.

    Args:
        subentities: Active sub-entities
        Q_total: Total stride budget for this frame
        weights: Per-subentity allocation weights (already computed)

    Returns:
        Dict[entity_id -> quota_assigned]

    Algorithm:
        1. Compute fractional quotas: q_e_frac = Q_total × (w_e / Σw)
        2. Take integer parts: q_e_int = ⌊q_e_frac⌋
        3. Compute remainder: R = Q_total - Σq_e_int
        4. Sort subentities by fractional remainder descending
        5. Give +1 to top R subentities
    """
    import math

    # Edge case: no subentities or no budget
    if not subentities or Q_total <= 0:
        return {subentity.id: 0 for subentity in subentities}

    # Step 1: Compute total weight
    total_weight = sum(weights.values())

    # Edge case: zero total weight (all subentities empty)
    if total_weight <= 1e-9:
        # Distribute evenly
        base_quota = Q_total // len(subentities)
        remainder = Q_total % len(subentities)
        quotas = {subentity.id: base_quota for subentity in subentities}
        # Give remainder to first R subentities (arbitrary but fair)
        for i, subentity in enumerate(subentities):
            if i < remainder:
                quotas[subentity.id] += 1
        return quotas

    # Step 2: Compute fractional quotas
    fractional_quotas = {}
    for subentity in subentities:
        w_e = weights.get(subentity.id, 0.0)
        fractional_quotas[subentity.id] = Q_total * (w_e / total_weight)

    # Step 3: Take integer parts
    integer_quotas = {eid: math.floor(fq) for eid, fq in fractional_quotas.items()}

    # Step 4: Compute remainder to distribute
    allocated = sum(integer_quotas.values())
    R = Q_total - allocated

    # Step 5: Sort subentities by fractional remainder (descending)
    remainders = {}
    for eid, fq in fractional_quotas.items():
        remainders[eid] = fq - integer_quotas[eid]

    sorted_entities = sorted(
        subentities,
        key=lambda e: remainders[e.id],
        reverse=True
    )

    # Step 6: Give +1 to top R subentities
    final_quotas = integer_quotas.copy()
    for i in range(R):
        if i < len(sorted_entities):
            final_quotas[sorted_entities[i].id] += 1

    return final_quotas


def allocate_quotas(
    subentities: List[SubEntity],
    Q_total: int,
    graph,
    recent_stimuli
) -> Dict[str, int]:
    """
    Main quota allocation function.

    Combines inverse-size weighting, modulation factors, and Hamilton allocation.

    Args:
        subentities: Active sub-entities this frame
        Q_total: Total stride budget for this frame
        graph: Graph object
        recent_stimuli: Recent stimulus history

    Returns:
        Dict[entity_id -> quota_assigned]

    Formula:
        w_e = (1 / |extent_e|) × u_e × r_e × h_e
        where u, r, h are normalized to mean=1.0 per-frame
    """
    if not subentities:
        return {}

    # Step 1: Compute inverse-size weights
    # Small subentities get more strides per node (inverse proportion)
    inverse_size_weights = {}
    for subentity in subentities:
        extent_size = len(subentity.extent)
        if extent_size > 0:
            inverse_size_weights[subentity.id] = 1.0 / extent_size
        else:
            # Empty extent - assign minimal weight
            inverse_size_weights[subentity.id] = 0.0

    # Step 2: Compute modulation factors
    factors = compute_modulation_factors(subentities, graph, recent_stimuli)

    # Step 3: Combine into final weights
    # w_e = (1/|extent|) × u_e × r_e × h_e
    combined_weights = {}
    for subentity in subentities:
        inv_size = inverse_size_weights[subentity.id]
        u_e = factors[subentity.id]['urgency']
        r_e = factors[subentity.id]['reachability']
        h_e = factors[subentity.id]['health']

        combined_weights[subentity.id] = inv_size * u_e * r_e * h_e

    # Step 4: Allocate quotas using Hamilton's method
    quotas = hamilton_quota_allocation(subentities, Q_total, combined_weights)

    # Step 5: Assign quotas to subentities
    for subentity in subentities:
        quota = quotas.get(subentity.id, 0)
        subentity.quota_assigned = quota
        subentity.quota_remaining = quota

    return quotas


## <<< END orchestration/mechanisms/quotas.py
---

## >>> BEGIN orchestration/mechanisms/scheduler.py
<!-- mtime: 2025-10-22T21:44:26; size_chars: 15056 -->

"""
Zippered Round-Robin Scheduler

Implements fair, interleaved subentity execution:
- One stride per turn for each subentity
- Round-robin cycling through all active subentities
- Quota-aware (subentity exits when quota exhausted)
- Deadline-aware (early termination on time pressure)

Author: AI #3
Created: 2025-10-20
Dependencies: sub_entity_core, quotas, valence, strides, wm_pack, telemetry
Zero-Constants: No fixed priorities, no starvation
"""

from typing import List, Dict, Optional, Any
from orchestration.mechanisms.sub_entity_core import SubEntity
from orchestration.mechanisms.quotas import allocate_quotas
from orchestration.mechanisms.valence import composite_valence
from orchestration.mechanisms.strides import (
    select_edge_by_valence_coverage,
    execute_stride
)
from orchestration.mechanisms.wm_pack import select_wm_nodes
from orchestration.mechanisms.telemetry import (
    emit_entity_quota_event,
    emit_stride_exec_event,
    emit_convergence_event,
    emit_frame_summary
)
import time


def zippered_schedule(
    subentities: List[SubEntity],
    deadline_ms: Optional[float] = None
) -> List[tuple[str, int]]:
    """
    Generate zippered execution schedule for subentities.

    One stride per turn, round-robin until all quotas exhausted.

    Args:
        subentities: Active sub-entities with assigned quotas
        deadline_ms: Optional wall-clock deadline (ms from epoch)

    Returns:
        List of (entity_id, stride_index) tuples in execution order

    Algorithm:
        1. Initialize quota_remaining for each subentity
        2. While any subentity has quota_remaining > 0:
            a. For each subentity in round-robin order:
                - If quota_remaining > 0:
                    - Schedule one stride
                    - Decrement quota_remaining
                - If deadline approaching:
                    - Early termination
        3. Return schedule

    Example:
        Subentity A: quota=3
        Subentity B: quota=2
        Subentity C: quota=4

        Schedule: [A0, B0, C0, A1, B1, C1, A2, C2, C3]

        No subentity gets >1 stride ahead of others (zippered fairness)
    """
    if not subentities:
        return []

    schedule = []
    stride_counts = {subentity.id: 0 for subentity in subentities}

    # Round-robin until all quotas exhausted
    while True:
        # Check if any subentity has quota remaining
        active = filter_active_entities(subentities)
        if not active:
            break

        # One stride per subentity per round
        for subentity in subentities:
            if subentity.quota_remaining <= 0:
                continue

            # Schedule this stride
            schedule.append((subentity.id, stride_counts[subentity.id]))
            stride_counts[subentity.id] += 1
            subentity.quota_remaining -= 1

    return schedule


def execute_frame(
    subentities: List[SubEntity],
    graph,
    goal_embedding,
    Q_total: int,
    frame_deadline_ms: float,
    recent_stimuli: List[Dict] = None,
    frame_number: int = 0
) -> Dict[str, Any]:
    """
    Execute one traversal frame with zippered scheduling.

    Args:
        subentities: Active sub-entities this frame
        graph: Graph object
        goal_embedding: Current goal vector
        Q_total: Total stride budget for this frame
        frame_deadline_ms: Wall-clock deadline for frame completion
        recent_stimuli: Recent stimulus history for urgency computation
        frame_number: Current frame index

    Returns:
        Dict with frame statistics:
            - strides_executed: int
            - entities_converged: List[str]
            - wall_time_us: float
            - early_termination: bool

    Algorithm:
        1. Allocate quotas (via quotas.allocate_quotas)
        2. Generate zippered schedule
        3. For each scheduled stride:
            a. Select edge (via strides.select_edge)
            b. Execute stride (via strides.execute_stride)
            c. Check convergence (via SubEntity.roi_tracker)
            d. Emit telemetry (via telemetry.emit_event)
            e. Check deadline
        4. Return statistics
    """
    frame_start_time = time.time()

    if recent_stimuli is None:
        recent_stimuli = []

    # === Step 1: Allocate Quotas ===
    allocate_quotas(
        subentities=subentities,
        Q_total=Q_total,
        graph=graph,
        recent_stimuli=recent_stimuli
    )

    # Emit quota events
    for subentity in subentities:
        emit_entity_quota_event(
            frame=frame_number,
            subentity=subentity,
            quota_assigned=subentity.quota_assigned
        )

    # === Step 2: Execute Strides in Zippered Fashion ===
    strides_executed = 0
    entities_converged = []
    early_termination = False

    # EMA tracking for deadline checking
    avg_stride_time_us = 100.0  # Initial estimate (100 microseconds)
    ema_alpha = 0.1  # EMA smoothing factor

    # Round-robin execution
    while True:
        active = filter_active_entities(subentities)
        if not active:
            break

        # One stride per subentity per round
        made_progress = False
        for subentity in subentities:
            if subentity.quota_remaining <= 0:
                continue

            # Check deadline before executing
            remaining_strides = sum(e.quota_remaining for e in subentities)
            if check_early_termination(frame_deadline_ms, avg_stride_time_us, remaining_strides):
                early_termination = True
                break

            # === Step 3a: Select Edge ===
            # Get valences for all frontier edges
            source_node = None
            if subentity.extent:
                # Select a source node from extent (highest energy)
                source_node = max(subentity.extent, key=lambda n: subentity.get_energy(n))

            if source_node is None:
                # Subentity has no extent (dissolved or empty)
                subentity.quota_remaining = 0
                entities_converged.append(subentity.id)
                emit_convergence_event(
                    frame=frame_number,
                    subentity=subentity,
                    reason="dissolution",
                    final_roi=0.0,
                    whisker_threshold=subentity.roi_tracker.lower_whisker() if subentity.roi_tracker.lower_whisker() != float('-inf') else 0.0,
                    strides_executed=subentity.quota_assigned - subentity.quota_remaining
                )
                continue

            # Compute valences for outgoing edges
            neighbors = list(graph.neighbors(source_node))
            if not neighbors:
                # No outgoing edges (dead end)
                subentity.quota_remaining = 0
                entities_converged.append(subentity.id)
                emit_convergence_event(
                    frame=frame_number,
                    subentity=subentity,
                    reason="dead_end",
                    final_roi=0.0,
                    whisker_threshold=subentity.roi_tracker.lower_whisker() if subentity.roi_tracker.lower_whisker() != float('-inf') else 0.0,
                    strides_executed=subentity.quota_assigned - subentity.quota_remaining
                )
                continue

            valences = {}
            for target_node in neighbors:
                v = composite_valence(
                    subentity=subentity,
                    source_i=source_node,    # Fixed: use source_i
                    target_j=target_node,    # Fixed: use target_j
                    graph=graph,
                    goal_embedding=goal_embedding
                )
                valences[target_node] = v

            # Select edge by valence coverage
            selected_edges = select_edge_by_valence_coverage(
                subentity=subentity,
                source_i=source_node,
                valences=valences,
                graph=graph
            )
            if not selected_edges:
                # No valid edges (all zero valence)
                subentity.quota_remaining = 0
                entities_converged.append(subentity.id)
                emit_convergence_event(
                    frame=frame_number,
                    subentity=subentity,
                    reason="zero_valence",
                    final_roi=0.0,
                    whisker_threshold=subentity.roi_tracker.lower_whisker() if subentity.roi_tracker.lower_whisker() != float('-inf') else 0.0,
                    strides_executed=subentity.quota_assigned - subentity.quota_remaining
                )
                continue

            target_node = selected_edges[0]  # Take first (highest valence)

            # === Step 3b: Execute Stride ===
            # Predict ROI before execution
            pred_roi = valences[target_node] * 100.0  # Rough prediction from valence

            # Capture state before stride
            source_before = {
                'E': subentity.get_energy(source_node),
                'theta': subentity.get_threshold(source_node)
            }
            target_before = {
                'E': subentity.get_energy(target_node),
                'theta': subentity.get_threshold(target_node)
            }

            result = execute_stride(
                subentity=subentity,
                source_i=source_node,
                target_j=target_node,
                graph=graph
            )

            # Capture state after stride
            source_after = {
                'E': subentity.get_energy(source_node),
                'theta': subentity.get_threshold(source_node)
            }
            target_after = {
                'E': subentity.get_energy(target_node),
                'theta': subentity.get_threshold(target_node)
            }

            stride_time_us = result['stride_time_us']

            # Update EMA of stride time
            avg_stride_time_us = (ema_alpha * stride_time_us) + ((1 - ema_alpha) * avg_stride_time_us)

            # === Step 3c: Check Convergence ===
            if result['delta'] > 0:
                # Record ROI for this stride
                roi = result['delta'] / (stride_time_us + 1e-6)
                subentity.roi_tracker.push(roi)

                # Check if converged (ROI below whisker)
                whisker = subentity.roi_tracker.lower_whisker()
                if whisker != float('-inf') and roi < whisker:
                    # Converged - ROI too low
                    subentity.quota_remaining = 0
                    entities_converged.append(subentity.id)
                    emit_convergence_event(
                        frame=frame_number,
                        subentity=subentity,
                        reason="roi_convergence",
                        final_roi=roi,
                        whisker_threshold=whisker,
                        strides_executed=subentity.quota_assigned - subentity.quota_remaining
                    )
                    continue

            # === Step 3d: Emit Telemetry ===
            emit_stride_exec_event(
                frame=frame_number,
                subentity=subentity,
                source_i=source_node,
                target_j=target_node,
                delta=result['delta'],
                alpha=result['alpha'],
                pred_roi=pred_roi,
                actual_time_us=stride_time_us,
                rho_local=result['rho_local'],
                source_after=source_after,
                target_after=target_after
            )

            # Update quota
            subentity.quota_remaining -= 1
            strides_executed += 1
            made_progress = True

        if early_termination:
            break

        if not made_progress:
            # No subentity could make progress (all converged/blocked)
            break

    # === Step 4: Select Working Memory Nodes ===
    # (Would be called here in full integration)
    # selected_wm, stats = select_wm_nodes(subentities, graph, token_budget)

    # === Step 5: Emit Frame Summary ===
    frame_end_time = time.time()
    wall_time_us = (frame_end_time - frame_start_time) * 1e6

    emit_frame_summary(
        frame=frame_number,
        subentities=subentities,
        strides_executed=strides_executed,
        wall_time_us=wall_time_us
    )

    return {
        'strides_executed': strides_executed,
        'entities_converged': entities_converged,
        'wall_time_us': wall_time_us,
        'early_termination': early_termination
    }


def check_early_termination(
    deadline_ms: float,
    avg_stride_time_us: float,
    remaining_strides: int
) -> bool:
    """
    Determine if frame should terminate early to meet deadline.

    Conservative estimate: stop if predicted overshoot > 10%.

    Args:
        deadline_ms: Wall-clock deadline (ms from epoch)
        avg_stride_time_us: EMA of stride execution time (microseconds)
        remaining_strides: Number of strides left in schedule

    Returns:
        True if should terminate early, False otherwise

    Formula:
        time_remaining = deadline_ms - current_time_ms
        predicted_time = (remaining_strides * avg_stride_time_us) / 1000.0

        terminate_early = (predicted_time > time_remaining * 1.1)
    """
    # Get current time in milliseconds
    current_time_ms = time.time() * 1000.0

    # Calculate time remaining until deadline
    time_remaining_ms = deadline_ms - current_time_ms

    if time_remaining_ms <= 0:
        # Already past deadline
        return True

    # Predict time needed for remaining strides (convert μs to ms)
    predicted_time_ms = (remaining_strides * avg_stride_time_us) / 1000.0

    # Conservative check: terminate if predicted to exceed deadline by >10%
    return predicted_time_ms > (time_remaining_ms * 1.1)


def update_quota_remaining(subentity: SubEntity):
    """
    Decrement quota_remaining after subentity executes a stride.

    Args:
        subentity: Sub-entity that just executed

    Side Effects:
        Modifies subentity.quota_remaining in place
    """
    if subentity.quota_remaining > 0:
        subentity.quota_remaining -= 1


def filter_active_entities(subentities: List[SubEntity]) -> List[SubEntity]:
    """
    Filter subentities that still have quota remaining.

    Args:
        subentities: All sub-entities

    Returns:
        List of subentities with quota_remaining > 0

    Zero-constants: No minimum quota threshold, natural completion
    """
    return [e for e in subentities if e.quota_remaining > 0]


## <<< END orchestration/mechanisms/scheduler.py
---

## >>> BEGIN orchestration/mechanisms/threshold.py
<!-- mtime: 2025-10-23T00:58:39; size_chars: 17068 -->

"""
Mechanism 16 Part 1: Adaptive Activation Threshold

ARCHITECTURAL PRINCIPLE: Nodes Become Subentities via Threshold Crossing

"Every time a node reaches the threshold of activation from a sensory input,
it becomes a sub-entity." - Nicolas

Core Truth (CORRECTED 2025-10-20):
- NOT pre-defined subentities (Translator, Architect) - those are CLUSTERS of micro-subentities
- ANY node crossing activation threshold becomes its own sub-entity
- Subentity name = node name (simple one-to-one mapping)
- Thousands of simultaneous micro-subentities (normal and expected)
- Threshold is DYNAMIC - depends on system criticality (active nodes/links)
- NO MIN THRESHOLD, NO MAX THRESHOLD - unbounded adaptation

Threshold Architecture:
- PRIMARY: Criticality-driven (more active nodes/links = higher threshold)
- SECONDARY: Base noise floor (prevents false activations from noise)

Formula:
    theta_{i,k} = BASE_THRESHOLD * (1 + CRITICALITY_FACTOR * num_active / num_total)

    where:
    - BASE_THRESHOLD: Starting threshold (much higher than 0.1)
    - CRITICALITY_FACTOR: How much criticality raises threshold
    - num_active: Number of currently active nodes
    - num_total: Total nodes in graph

This creates adaptive behavior:
- Low activity (few nodes active): Lower threshold, easy to activate new nodes
- High activity (many nodes active): Higher threshold, harder to activate more
- Prevents runaway activation while allowing exploration when quiet

Activation test:
    node_is_active = (e_{i,k} >= theta_{i,k})

Soft activation (recommended):
    a_{i,k} = sigmoid(beta * (e_{i,k} - theta_{i,k}))

Author: Felix (Engineer)
Created: 2025-10-19
Updated: 2025-10-20 - Made threshold criticality-driven, removed bounds
Spec: Based on Nicolas's architectural corrections 2025-10-20
"""

import numpy as np
from typing import Dict, Optional, TYPE_CHECKING
from dataclasses import dataclass
from collections import deque

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.node import Node
    from orchestration.core.types import EntityID

from orchestration.core.settings import settings
from orchestration.core.telemetry import emit_affective_threshold

# --- Configuration ---

BASE_THRESHOLD_DEFAULT: float = 1.0  # Base activation threshold (way higher than 0.1)
CRITICALITY_FACTOR_DEFAULT: float = 2.0  # How much criticality multiplies threshold
KAPPA_DEFAULT: float = 10.0  # Soft activation sharpness


@dataclass
class NoiseStatistics:
    """
    Noise floor statistics for threshold calculation.

    Tracked via Exponential Moving Average (EMA) when node is quiet.

    Args:
        mu: Noise floor (mean energy when quiet)
        sigma: Noise variability (std dev when quiet)
        sample_count: Number of samples collected
    """
    mu: float = 0.02
    sigma: float = 0.01
    sample_count: int = 0


@dataclass
class ThresholdContext:
    """
    Configuration for adaptive threshold calculation.

    Args:
        base_threshold: Starting threshold value. Default 1.0.
        criticality_factor: How much criticality multiplies threshold. Default 2.0.
        kappa: Soft activation sharpness. Default 10.0.
        num_active: Number of currently active nodes (computed dynamically)
        num_total: Total number of nodes in graph
    """
    base_threshold: float = BASE_THRESHOLD_DEFAULT
    criticality_factor: float = CRITICALITY_FACTOR_DEFAULT
    kappa: float = KAPPA_DEFAULT
    num_active: int = 0
    num_total: int = 1


# --- Threshold Calculation ---

def compute_base_threshold(
    mu: float,
    sigma: float,
    z_alpha: float
) -> float:
    """
    Compute base statistical threshold.

    Formula: theta_base = mu + z_alpha * sigma

    This is the MINIMUM threshold - sets false-positive rate.

    Args:
        mu: Noise floor (mean energy when quiet)
        sigma: Noise variability (std dev when quiet)
        z_alpha: Z-score (e.g., 1.28 for alpha=10%)

    Returns:
        Base threshold

    Example:
        >>> mu, sigma = 0.02, 0.01
        >>> theta_base = compute_base_threshold(mu, sigma, 1.28)
        >>> print(f"Base threshold: {theta_base:.3f}")
        Base threshold: 0.033  # mu + 1.28*sigma
    """
    return mu + z_alpha * sigma


def compute_adaptive_threshold(
    node: 'Node',
    subentity: 'EntityID',
    ctx: ThresholdContext,
    active_affect: Optional[np.ndarray] = None,
    citizen_id: str = "",
    frame_id: Optional[str] = None
) -> float:
    """
    Compute adaptive threshold for node-subentity pair.

    Threshold driven by system criticality (number of active nodes).
    Optionally modulated by affective coupling (PR-B).

    Formula:
        theta_base = BASE_THRESHOLD * (1 + CRITICALITY_FACTOR * (num_active / num_total))
        theta_adjusted = theta_base - h  (if affective coupling enabled)

    Where h is the affective threshold reduction (bounded [0, λ_aff]).

    More active nodes = higher threshold = harder to activate more nodes.
    This prevents runaway activation.

    Args:
        node: Node to compute threshold for
        subentity: Subentity identifier
        ctx: Threshold configuration with criticality state
        active_affect: Current affective state vector (optional, for PR-B)
        citizen_id: Citizen ID for telemetry
        frame_id: Frame ID for telemetry

    Returns:
        Adaptive threshold value (unbounded - no min/max)

    Example:
        >>> ctx = ThresholdContext(
        ...     base_threshold=1.0,
        ...     criticality_factor=2.0,
        ...     num_active=10,
        ...     num_total=100
        ... )
        >>> theta = compute_adaptive_threshold(node, "translator", ctx)
        >>> # theta = 1.0 * (1 + 2.0 * (10/100)) = 1.0 * 1.2 = 1.2
    """
    # Compute criticality ratio
    if ctx.num_total > 0:
        criticality_ratio = ctx.num_active / ctx.num_total
    else:
        criticality_ratio = 0.0

    # Apply criticality-driven threshold
    theta_base = ctx.base_threshold * (1.0 + ctx.criticality_factor * criticality_ratio)

    # Apply affective modulation if enabled (PR-B)
    h = 0.0
    theta_adjusted = theta_base

    if settings.AFFECTIVE_THRESHOLD_ENABLED and node is not None:
        # Get node emotion vector (if it has one)
        node_emotion = getattr(node, 'emotion_vector', None)

        if node_emotion is not None and active_affect is not None:
            h = compute_affective_threshold_reduction(
                active_affect=active_affect,
                node_emotion=node_emotion,
                node_id=node.id if node else "",
                citizen_id=citizen_id,
                frame_id=frame_id
            )
            theta_adjusted = theta_base - h

            # Emit telemetry event
            if settings.AFFECTIVE_TELEMETRY_ENABLED and h > 0.0:
                A_magnitude = float(np.linalg.norm(active_affect))
                E_magnitude = float(np.linalg.norm(node_emotion))
                dot_product = float(np.dot(active_affect, node_emotion))
                affective_alignment = dot_product / (A_magnitude * E_magnitude) if A_magnitude > 0 and E_magnitude > 0 else 0.0

                emit_affective_threshold(
                    citizen_id=citizen_id,
                    frame_id=frame_id or "",
                    node_id=node.id if node else "",
                    theta_base=theta_base,
                    theta_adjusted=theta_adjusted,
                    h=h,
                    affective_alignment=affective_alignment,
                    emotion_magnitude=E_magnitude
                )

    return theta_adjusted


def soft_activation(
    energy: float,
    threshold: float,
    kappa: float = KAPPA_DEFAULT
) -> float:
    """
    Compute soft activation using sigmoid.

    Formula: a = 1 / (1 + exp(-kappa * (e - theta)))

    Smooth transition around threshold:
    - e << theta: a ~= 0
    - e = theta: a = 0.5
    - e >> theta: a ~= 1

    Args:
        energy: Node energy
        threshold: Activation threshold
        kappa: Sharpness parameter (higher = steeper sigmoid)

    Returns:
        Soft activation value [0, 1]

    Example:
        >>> energy, threshold = 0.05, 0.03
        >>> a = soft_activation(energy, threshold, kappa=10.0)
        >>> print(f"Activation: {a:.3f}")
        Activation: 0.881  # Smoothly above threshold
    """
    return 1.0 / (1.0 + np.exp(-kappa * (energy - threshold)))


def hard_activation(
    energy: float,
    threshold: float
) -> bool:
    """
    Compute hard activation (binary).

    Args:
        energy: Node energy
        threshold: Activation threshold

    Returns:
        True if energy >= threshold, False otherwise

    Example:
        >>> hard_activation(0.05, 0.03)
        True
        >>> hard_activation(0.02, 0.03)
        False
    """
    return energy >= threshold


# --- Affective Coupling (PR-B) ---

def compute_affective_threshold_reduction(
    active_affect: Optional[np.ndarray],
    node_emotion: Optional[np.ndarray],
    node_id: str = "",
    citizen_id: str = "",
    frame_id: Optional[str] = None
) -> float:
    """
    Compute affective threshold reduction (PR-B: Emotion Couplings).

    Affect-congruent nodes get lower thresholds (easier to activate).
    This implements the bounded affect→threshold modulation.

    Formula:
        h = λ_aff · tanh(||A|| · cos(A, E_emo)) · clip(||E_emo||, 0, 1)

    Where:
        - λ_aff = AFFECTIVE_THRESHOLD_LAMBDA_FACTOR (default 0.08, ~8% reduction)
        - A = current affective state vector
        - E_emo = emotion vector on node
        - cos(A, E_emo) = cosine similarity (alignment)
        - ||·|| = L2 norm (magnitude)

    Returns positive h for aligned affect (reduces threshold).
    Returns 0 when disabled or when affect/emotion missing.

    Bounded: h ∈ [0, λ_aff] (max 8% threshold reduction by default)

    Args:
        active_affect: Current affective state vector (A)
        node_emotion: Emotion vector on node (E_emo)
        node_id: Node ID for telemetry
        citizen_id: Citizen ID for telemetry
        frame_id: Frame ID for telemetry

    Returns:
        Threshold reduction h (positive value)

    Example:
        >>> A = np.array([0.5, 0.5, 0.0])  # Moderate positive affect
        >>> E_emo = np.array([0.8, 0.6, 0.0])  # Node has positive emotion
        >>> h = compute_affective_threshold_reduction(A, E_emo, "node1", "felix", "frame_001")
        >>> # h ≈ 0.08 * tanh(0.707 * 0.98) * 1.0 ≈ 0.05 (5% reduction)
    """
    # Feature flag check
    if not settings.AFFECTIVE_THRESHOLD_ENABLED:
        return 0.0

    # Guard: need both affect and emotion vectors
    if active_affect is None or node_emotion is None:
        return 0.0

    if len(active_affect) == 0 or len(node_emotion) == 0:
        return 0.0

    # Compute magnitudes
    A_magnitude = float(np.linalg.norm(active_affect))
    E_magnitude = float(np.linalg.norm(node_emotion))

    # Guard: if either is zero, no modulation
    if A_magnitude < 1e-6 or E_magnitude < 1e-6:
        return 0.0

    # Compute cosine similarity (alignment)
    # cos(A, E_emo) = (A · E_emo) / (||A|| · ||E_emo||)
    dot_product = float(np.dot(active_affect, node_emotion))
    affective_alignment = dot_product / (A_magnitude * E_magnitude)

    # Clamp emotion magnitude to [0, 1]
    E_magnitude_clamped = min(max(E_magnitude, 0.0), 1.0)

    # Compute threshold reduction
    # h = λ_aff · tanh(||A|| · cos(A, E_emo)) · clip(||E_emo||, 0, 1)
    lambda_aff = settings.AFFECTIVE_THRESHOLD_LAMBDA_FACTOR
    inner_term = A_magnitude * affective_alignment
    h = lambda_aff * np.tanh(inner_term) * E_magnitude_clamped

    # h should be positive (we subtract it from threshold)
    # If alignment is negative (opposite affect), h becomes negative, which would RAISE threshold
    # Clamp h to [0, lambda_aff] to only allow reduction, not increase
    h = max(0.0, min(h, lambda_aff))

    # Emit telemetry event
    if settings.AFFECTIVE_TELEMETRY_ENABLED:
        # We don't know theta_base here, so we'll emit from the caller
        # Store values for caller to emit
        pass

    return float(h)


# --- Noise Statistics Tracking ---

class NoiseTracker:
    """
    Tracks noise statistics for node-subentity pairs using EMA.

    Maintains rolling statistics (mu, sigma) for threshold calculation.
    """

    def __init__(self, ema_alpha: float = 0.1):
        """
        Initialize noise tracker.

        Args:
            ema_alpha: EMA smoothing factor (0 < alpha < 1). Default 0.1.
        """
        self.ema_alpha = ema_alpha
        self.stats: Dict[str, NoiseStatistics] = {}  # Key: f"{node_id}_{subentity}"

    def _get_key(self, node_id: str, subentity: str) -> str:
        """Generate key for node-subentity pair."""
        return f"{node_id}_{subentity}"

    def get_stats(self, node_id: str, subentity: str) -> NoiseStatistics:
        """
        Get noise statistics for node-subentity pair.

        Returns:
            NoiseStatistics (creates default if not exists)
        """
        key = self._get_key(node_id, subentity)
        if key not in self.stats:
            self.stats[key] = NoiseStatistics()
        return self.stats[key]

    def update(self, node_id: str, subentity: str, energy: float, is_quiet: bool):
        """
        Update noise statistics with new energy sample.

        Only updates when node is "quiet" (no external stimuli).

        Args:
            node_id: Node identifier
            subentity: Subentity identifier
            energy: Current energy value
            is_quiet: True if node is quiet (suitable for noise sampling)
        """
        if not is_quiet:
            return

        stats = self.get_stats(node_id, subentity)

        # Update EMA for mu (mean)
        if stats.sample_count == 0:
            stats.mu = energy
        else:
            stats.mu = self.ema_alpha * energy + (1 - self.ema_alpha) * stats.mu

        # Update EMA for sigma (std dev) - using squared deviation
        if stats.sample_count == 0:
            stats.sigma = 0.01  # Initial guess
        else:
            deviation = abs(energy - stats.mu)
            stats.sigma = self.ema_alpha * deviation + (1 - self.ema_alpha) * stats.sigma

        stats.sample_count += 1


# --- Activation Computation ---

def compute_activation_mask(
    graph: 'Graph',
    subentity: 'EntityID',
    ctx: ThresholdContext
) -> Dict[str, bool]:
    """
    Compute hard activation mask for all nodes.

    Threshold is same for all nodes (criticality-driven), so this is simple.

    Args:
        graph: Graph with nodes
        subentity: Subentity to compute activations for
        ctx: Threshold configuration (with num_active, num_total set)

    Returns:
        Dict mapping node_id to activation bool

    Example:
        >>> ctx = ThresholdContext(
        ...     base_threshold=1.0,
        ...     num_active=5,
        ...     num_total=50
        ... )
        >>> mask = compute_activation_mask(graph, "translator", ctx)
        >>> active_count = sum(mask.values())
        >>> print(f"Active nodes: {active_count}/{len(graph.nodes)}")
    """
    mask = {}

    # Compute threshold once (same for all nodes)
    threshold = compute_adaptive_threshold(None, subentity, ctx)

    for node in graph.nodes.values():
        energy = node.get_entity_energy(subentity)
        mask[node.id] = hard_activation(energy, threshold)

    return mask


def compute_activation_values(
    graph: 'Graph',
    subentity: 'EntityID',
    ctx: ThresholdContext
) -> Dict[str, float]:
    """
    Compute soft activation values for all nodes.

    Args:
        graph: Graph with nodes
        subentity: Subentity to compute activations for
        ctx: Threshold configuration (with num_active, num_total set)

    Returns:
        Dict mapping node_id to soft activation [0, 1]

    Example:
        >>> ctx = ThresholdContext(
        ...     base_threshold=1.0,
        ...     num_active=5,
        ...     num_total=50
        ... )
        >>> activations = compute_activation_values(graph, "translator", ctx)
        >>> print(f"Average activation: {np.mean(list(activations.values())):.3f}")
    """
    activations = {}

    # Compute threshold once (same for all nodes)
    threshold = compute_adaptive_threshold(None, subentity, ctx)

    for node in graph.nodes.values():
        energy = node.get_entity_energy(subentity)
        activations[node.id] = soft_activation(energy, threshold, ctx.kappa)

    return activations


## <<< END orchestration/mechanisms/threshold.py
---

## >>> BEGIN orchestration/mechanisms/tick_speed.py
<!-- mtime: 2025-10-24T19:17:42; size_chars: 18567 -->

"""
Tick Speed Regulation - Three-Factor Adaptive Scheduling (PR-B)

Implements three-factor adaptive tick scheduling:
- Factor 1 (Stimulus): Fast ticks during active stimulation
- Factor 2 (Activation): Fast ticks during high internal energy (autonomous momentum)
- Factor 3 (Arousal): Arousal floor prevents slow ticks during anxious/excited states
- Physics dt capping to prevent blow-ups
- Optional EMA smoothing to reduce oscillation

Three-Factor Minimum:
  interval_next = min(interval_stimulus, interval_activation, interval_arousal)
  Fastest factor wins - enables rumination, arousal modulation

Architecture:
- Stimulus tracking: Record arrival times
- Activation tracking: Sum total active energy across graph
- Arousal tracking: Mean arousal from active entities
- Interval calculation: Three-factor minimum with bounds
- dt capping: Prevent over-integration after long sleep
- EMA smoothing: Dampen rapid changes
- Reason tracking: Which factor determined interval (observability)

Author: Felix (Engineer)
Created: 2025-10-22
Updated: 2025-10-24 - PR-B: Three-factor tick speed (activation + arousal)
Spec: docs/specs/v2/runtime_engine/tick_speed.md
"""

import time
from dataclasses import dataclass
from typing import Optional, List, TYPE_CHECKING
import logging
import numpy as np

if TYPE_CHECKING:
    from orchestration.core.graph import Graph

logger = logging.getLogger(__name__)


# === Three-Factor Computation Functions (PR-B) ===

def compute_interval_activation(
    graph: 'Graph',
    active_entities: List[str],
    min_interval_ms: float = 100.0,
    max_interval_s: float = 60.0,
    activation_threshold: float = 0.3
) -> float:
    """
    Compute tick interval from internal activation level (PR-B Factor 2).

    High internal activation → fast ticks (enables autonomous momentum).
    Allows rumination, generative overflow without external stimuli.

    Algorithm:
    1. Sum total active energy across all nodes and active entities
    2. Map activation to interval (inverse relationship)
       - High activation (>10.0) → min_interval (fast)
       - Low activation (<1.0) → max_interval (slow)
       - Middle range → log-space interpolation

    Args:
        graph: Consciousness graph
        active_entities: List of entity IDs to check
        min_interval_ms: Minimum interval (fastest rate)
        max_interval_s: Maximum interval (slowest rate)
        activation_threshold: Energy threshold for "active" nodes

    Returns:
        Interval in seconds based on activation level

    Example:
        >>> # High internal energy (ruminating)
        >>> interval = compute_interval_activation(graph, ["felix"], 100, 60, 0.3)
        >>> # interval ≈ 0.1s (fast ticks continue after stimulus)
        >>>
        >>> # Low internal energy (dormant)
        >>> interval = compute_interval_activation(graph, ["felix"], 100, 60, 0.3)
        >>> # interval ≈ 60s (slow ticks)
    """
    # Sum total active energy across graph and entities
    total_active_energy = 0.0

    for node in graph.nodes.values():
        node_energy = node.E  # Total energy across all entities
        if node_energy > activation_threshold:
            total_active_energy += node_energy

    # Map activation to interval (inverse relationship)
    # High activation → short interval (fast ticks)
    # Low activation → long interval (slow ticks)

    min_interval_s = min_interval_ms / 1000.0

    if total_active_energy > 10.0:
        # High activation → minimum interval (fast)
        return min_interval_s
    elif total_active_energy < 1.0:
        # Low activation → maximum interval (slow)
        return max_interval_s
    else:
        # Linear interpolation in log space
        log_energy = np.log10(total_active_energy)
        log_min = np.log10(1.0)
        log_max = np.log10(10.0)

        t = (log_energy - log_min) / (log_max - log_min)  # [0, 1]

        # Invert: high energy → short interval
        interval = max_interval_s * (1 - t) + min_interval_s * t

        return interval


def compute_interval_arousal(
    active_entities: List[str],
    entity_affect_getter,  # Callable that gets affect for entity_id
    min_interval_ms: float = 100.0,
    max_interval_s: float = 60.0,
    arousal_floor_enabled: bool = True
) -> float:
    """
    Compute interval floor from affect arousal (PR-B Factor 3).

    High arousal → prevents very slow ticks (anxiety/excitement keeps mind active).
    Provides arousal floor that prevents dormancy during emotional states.

    Algorithm:
    1. Get arousal magnitude for each active entity
    2. Compute mean arousal
    3. Map arousal to interval floor
       - High arousal (>0.7) → 2x min_interval (prevents slow ticks)
       - Low arousal (<0.3) → max_interval (no constraint)
       - Middle range → linear interpolation

    Args:
        active_entities: List of entity IDs to check
        entity_affect_getter: Function that returns affect vector for entity_id
        min_interval_ms: Minimum interval (fastest rate)
        max_interval_s: Maximum interval (slowest rate)
        arousal_floor_enabled: Whether to apply arousal floor

    Returns:
        Interval floor in seconds based on arousal level

    Example:
        >>> # High arousal (anxious/excited)
        >>> interval = compute_interval_arousal(["felix"], get_affect, 100, 60, True)
        >>> # interval ≈ 0.2s (2x minimum - prevents very slow ticks)
        >>>
        >>> # Low arousal (calm)
        >>> interval = compute_interval_arousal(["felix"], get_affect, 100, 60, True)
        >>> # interval ≈ 60s (no constraint)
    """
    if not arousal_floor_enabled:
        return max_interval_s  # No floor constraint

    # Compute mean arousal across active entities
    arousals = []

    for entity_id in active_entities:
        try:
            affect = entity_affect_getter(entity_id)  # Should return numpy array or None
            if affect is not None and len(affect) > 0:
                arousal = float(np.linalg.norm(affect))  # Magnitude as arousal proxy
                arousals.append(arousal)
        except Exception:
            # If affect getter fails, skip this entity
            continue

    if not arousals:
        # No arousal data → no constraint
        return max_interval_s

    mean_arousal = np.mean(arousals)

    # Map arousal to interval floor
    # High arousal → short floor (prevents slow ticks)
    # Low arousal → no floor constraint

    min_interval_s = min_interval_ms / 1000.0
    arousal_floor = min_interval_s * 2  # 2x minimum

    if mean_arousal > 0.7:
        # High arousal → arousal floor (still fast)
        return arousal_floor
    elif mean_arousal < 0.3:
        # Low arousal → no constraint
        return max_interval_s
    else:
        # Linear interpolation
        t = (mean_arousal - 0.3) / (0.7 - 0.3)
        floor = max_interval_s * (1 - t) + arousal_floor * t
        return floor


@dataclass
class TickSpeedConfig:
    """
    Configuration for adaptive tick speed regulation.

    Attributes:
        min_interval_ms: Minimum tick interval (fastest rate). Default 100ms (10 Hz).
        max_interval_s: Maximum tick interval (slowest rate). Default 60s (1/min).
        dt_cap_s: Maximum physics integration step. Default 5.0s.
        ema_beta: EMA smoothing factor (0=no smoothing, 1=no memory). Default 0.3.
        enable_ema: Whether to apply EMA smoothing. Default True.
    """
    min_interval_ms: float = 100.0  # 10 Hz max
    max_interval_s: float = 60.0    # 1/min min
    dt_cap_s: float = 5.0           # Cap physics dt
    ema_beta: float = 0.3           # Smoothing factor
    enable_ema: bool = True         # EMA toggle


class AdaptiveTickScheduler:
    """
    Three-factor adaptive tick scheduler with dt capping (PR-B).

    Implements the three-factor tick speed regulation mechanism:
    1. Track time since last stimulus (Factor 1)
    2. Compute activation-driven interval (Factor 2 - autonomous momentum)
    3. Compute arousal-driven floor (Factor 3 - emotion modulation)
    4. interval_next = min(all three factors) - fastest wins
    5. Optional EMA smoothing
    6. Cap physics dt to prevent blow-ups
    7. Track reason (which factor determined interval)

    Example:
        >>> config = TickSpeedConfig(min_interval_ms=100, max_interval_s=60)
        >>> scheduler = AdaptiveTickScheduler(config, graph, ["felix"])
        >>>
        >>> # On stimulus arrival
        >>> scheduler.on_stimulus()
        >>>
        >>> # Before each tick
        >>> interval_next, reason, details = scheduler.compute_next_interval()
        >>> dt_used, was_capped = scheduler.compute_dt(interval_next)
        >>>
        >>> # Execute tick with dt_used
        >>> await tick(dt=dt_used)
        >>>
        >>> # Sleep until next tick
        >>> await asyncio.sleep(interval_next)
    """

    def __init__(
        self,
        config: TickSpeedConfig,
        graph: Optional['Graph'] = None,
        active_entities: Optional[List[str]] = None,
        entity_affect_getter = None
    ):
        """
        Initialize three-factor adaptive tick scheduler.

        Args:
            config: Tick speed configuration
            graph: Consciousness graph (for activation tracking)
            active_entities: List of active entity IDs (for activation/arousal)
            entity_affect_getter: Function that returns affect vector for entity_id
        """
        self.config = config
        self.graph = graph
        self.active_entities = active_entities or []
        self.entity_affect_getter = entity_affect_getter

        # Stimulus tracking
        self.last_stimulus_time: Optional[float] = None

        # Tick timing
        self.last_tick_time: float = time.time()

        # EMA state
        self.interval_prev: float = config.min_interval_ms / 1000.0

        # Three-factor state (for diagnostics)
        self.last_interval_stimulus: Optional[float] = None
        self.last_interval_activation: Optional[float] = None
        self.last_interval_arousal: Optional[float] = None
        self.last_reason: Optional[str] = None

        logger.info(f"[TickSpeed] Initialized three-factor scheduler: "
                   f"min={config.min_interval_ms}ms, max={config.max_interval_s}s, "
                   f"dt_cap={config.dt_cap_s}s, entities={len(self.active_entities)}")

    def on_stimulus(self) -> None:
        """
        Record stimulus arrival time.

        Call this when a stimulus arrives (user message, external event, etc.).
        Updates last_stimulus_time to current time.

        Side effects:
            Updates self.last_stimulus_time

        Example:
            >>> scheduler.on_stimulus()  # Stimulus just arrived
            >>> interval = scheduler.compute_next_interval()
            >>> # interval will be near min_interval
        """
        self.last_stimulus_time = time.time()
        logger.debug(f"[TickSpeed] Stimulus recorded at {self.last_stimulus_time:.3f}")

    def compute_next_interval(self) -> tuple[float, str, dict]:
        """
        Compute next tick interval using three-factor minimum (PR-B).

        Algorithm:
        1. Compute interval_stimulus (Factor 1): time_since_last_stimulus
        2. Compute interval_activation (Factor 2): from total active energy
        3. Compute interval_arousal (Factor 3): from mean arousal
        4. interval_next = min(all three) - fastest factor wins
        5. Determine reason (which factor won)
        6. Optional EMA smoothing to reduce oscillation

        Returns:
            Tuple of (interval, reason, details):
            - interval: Next tick interval in seconds
            - reason: "stimulus" | "activation" | "arousal_floor"
            - details: Dict with all three intervals + diagnostics

        Example:
            >>> scheduler.on_stimulus()
            >>> interval, reason, details = scheduler.compute_next_interval()
            >>> # reason="stimulus" (just received input)
            >>> # interval ≈ 0.1s
            >>>
            >>> # High internal energy, no recent stimulus
            >>> interval, reason, details = scheduler.compute_next_interval()
            >>> # reason="activation" (autonomous momentum)
            >>> # interval ≈ 0.15s (ruminating)
        """
        now = time.time()

        # Factor 1: Stimulus-driven interval
        if self.last_stimulus_time is None:
            # No stimulus yet - dormant mode
            interval_stimulus_raw = self.config.max_interval_s
        else:
            # Time since last stimulus
            time_since_stimulus = now - self.last_stimulus_time
            interval_stimulus_raw = time_since_stimulus

        # Clamp stimulus interval to bounds
        interval_stimulus = max(
            self.config.min_interval_ms / 1000.0,  # min (convert ms to s)
            min(interval_stimulus_raw, self.config.max_interval_s)  # max
        )

        # Factor 2: Activation-driven interval (autonomous momentum)
        if self.graph and self.active_entities:
            interval_activation = compute_interval_activation(
                self.graph,
                self.active_entities,
                self.config.min_interval_ms,
                self.config.max_interval_s
            )
        else:
            # No graph/entities → no activation factor
            interval_activation = self.config.max_interval_s

        # Factor 3: Arousal-driven floor (emotion modulation)
        if self.active_entities and self.entity_affect_getter:
            interval_arousal = compute_interval_arousal(
                self.active_entities,
                self.entity_affect_getter,
                self.config.min_interval_ms,
                self.config.max_interval_s
            )
        else:
            # No affect data → no arousal factor
            interval_arousal = self.config.max_interval_s

        # Three-factor minimum: Fastest factor wins
        interval_candidates = {
            'stimulus': interval_stimulus,
            'activation': interval_activation,
            'arousal_floor': interval_arousal
        }

        interval_min = min(interval_candidates.values())
        reason = min(interval_candidates, key=interval_candidates.get)

        # Store for diagnostics
        self.last_interval_stimulus = interval_stimulus
        self.last_interval_activation = interval_activation
        self.last_interval_arousal = interval_arousal
        self.last_reason = reason

        # Optional EMA smoothing
        if self.config.enable_ema:
            # ema_t = β·v_t + (1-β)·ema_{t-1}
            interval_smoothed = (
                self.config.ema_beta * interval_min +
                (1 - self.config.ema_beta) * self.interval_prev
            )
            self.interval_prev = interval_smoothed
            final_interval = interval_smoothed
        else:
            final_interval = interval_min

        # Build details dict for observability
        details = {
            'interval_stimulus': interval_stimulus,
            'interval_activation': interval_activation,
            'interval_arousal': interval_arousal,
            'interval_min': interval_min,
            'interval_smoothed': final_interval if self.config.enable_ema else None,
            'reason': reason
        }

        logger.debug(f"[TickSpeed] Three-factor: stimulus={interval_stimulus:.3f}s, "
                    f"activation={interval_activation:.3f}s, arousal={interval_arousal:.3f}s "
                    f"→ {reason}={final_interval:.3f}s")

        return final_interval, reason, details

    def compute_dt(self, interval: float) -> tuple[float, bool]:
        """
        Compute physics dt with capping.

        Algorithm (spec §2.2):
        dt_used = min(interval, dt_cap)

        This prevents "first tick after long sleep" from over-integrating
        diffusion/decay by limiting physics integration step.

        Args:
            interval: Wall-clock interval (from compute_next_interval)

        Returns:
            Tuple of (dt_used, was_capped)
            - dt_used: Physics integration time step (seconds)
            - was_capped: True if dt < interval (dt was capped)

        Example:
            >>> # After short interval
            >>> dt, capped = scheduler.compute_dt(0.5)
            >>> # dt=0.5, capped=False (under cap)
            >>>
            >>> # After long dormancy
            >>> dt, capped = scheduler.compute_dt(120.0)
            >>> # dt=5.0, capped=True (hit dt_cap)
        """
        dt_used = min(interval, self.config.dt_cap_s)
        was_capped = dt_used < interval

        if was_capped:
            logger.debug(f"[TickSpeed] dt capped: interval={interval:.3f}s → dt={dt_used:.3f}s")
        else:
            logger.debug(f"[TickSpeed] dt uncapped: {dt_used:.3f}s")

        return dt_used, was_capped

    def get_diagnostics(self) -> dict:
        """
        Get scheduler diagnostics for observability (three-factor).

        Returns:
            Dictionary with diagnostic fields:
            - last_stimulus_time: When last stimulus arrived (None if never)
            - time_since_stimulus: Seconds since last stimulus (None if never)
            - interval_prev: Previous EMA-smoothed interval
            - three_factor_state: Last computed three-factor intervals
            - last_reason: Which factor determined last interval
            - config: Current configuration

        Example:
            >>> diag = scheduler.get_diagnostics()
            >>> print(f"Reason: {diag['last_reason']}")
            >>> print(f"Activation interval: {diag['three_factor_state']['activation']:.2f}s")
        """
        now = time.time()

        return {
            'last_stimulus_time': self.last_stimulus_time,
            'time_since_stimulus': now - self.last_stimulus_time if self.last_stimulus_time else None,
            'interval_prev': self.interval_prev,
            'three_factor_state': {
                'stimulus': self.last_interval_stimulus,
                'activation': self.last_interval_activation,
                'arousal_floor': self.last_interval_arousal
            },
            'last_reason': self.last_reason,
            'config': {
                'min_interval_ms': self.config.min_interval_ms,
                'max_interval_s': self.config.max_interval_s,
                'dt_cap_s': self.config.dt_cap_s,
                'ema_beta': self.config.ema_beta,
                'enable_ema': self.config.enable_ema
            }
        }


## <<< END orchestration/mechanisms/tick_speed.py
---

## >>> BEGIN orchestration/mechanisms/decay.py
<!-- mtime: 2025-10-23T01:09:50; size_chars: 18927 -->

"""
Mechanism: Energy & Weight Decay (Dual-Clock Forgetting)

ARCHITECTURAL PRINCIPLE: Two-Timescale Forgetting with Criticality Coupling

Implements BOTH:
1. Activation decay: E_i ← λ_E^Δt × E_i (fast, per-tick)
2. Weight decay: W ← λ_W^Δt × W (slow, periodic)

WHY TWO CLOCKS:
- Fast activation decay: vivid → vague → gone (hours)
- Slow weight decay: core ideas persist for weeks
- Prevents: structure erasure (same decay) or stickiness (no decay)

CONTROLLER COUPLING:
- Criticality controller adjusts effective δ_E within bounds
- Weight decay operates INDEPENDENTLY on slower horizons
- Never tie weight decay to ρ (different timescales)

SINGLE-ENERGY MODEL:
- Operates on node.E (total activation scalar), NOT per-entity buffers
- Type-dependent multipliers from settings.py
- Floor bounds prevent over-decay

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/foundations/decay.md
"""

import math
import numpy as np
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass
from collections import defaultdict

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.node import Node
    from orchestration.core.link import Link
    from orchestration.core.types import NodeType

from orchestration.core.settings import settings


# === Data Classes ===

@dataclass
class DecayMetrics:
    """
    Complete decay metrics for observability.

    Emitted as `decay.tick` event per spec §6.
    """
    # Activation decay
    delta_E: float                          # Effective activation decay rate used
    nodes_decayed: int                      # Nodes with activation decay
    total_energy_before: float              # Energy before decay
    total_energy_after: float               # Energy after decay
    energy_lost: float                      # Energy removed by decay

    # Weight decay
    delta_W: float                          # Effective weight decay rate used
    nodes_weight_decayed: int               # Nodes with weight decay
    links_weight_decayed: int               # Links with weight decay

    # Half-life estimates per type
    half_lives_activation: Dict[str, float] # Type → half-life (seconds)
    half_lives_weight: Dict[str, float]     # Type → half-life (seconds)

    # Histograms
    energy_histogram: Dict[str, List[float]]  # Type → energy distribution
    weight_histogram: Dict[str, List[float]]  # Type → weight distribution

    # AUC tracking
    auc_activation_window: float            # Area under curve (activation)


@dataclass
class DecayContext:
    """
    Configuration for decay tick.

    Args:
        dt: Time duration for this tick (seconds). Default 1.0.
        effective_delta_E: Criticality-adjusted activation decay. If None, uses base from settings.
        apply_weight_decay: Whether to apply weight decay this tick. Default False (periodic).
        compute_histograms: Whether to compute expensive histograms. Default False (sampled).
    """
    dt: float = 1.0
    effective_delta_E: Optional[float] = None
    apply_weight_decay: bool = False
    compute_histograms: bool = False


# === Helper Functions ===

def compute_half_life(decay_rate: float) -> float:
    """
    Compute half-life from decay rate.

    Formula: t_half = ln(2) / decay_rate

    Args:
        decay_rate: Decay rate per second

    Returns:
        Half-life (seconds)
    """
    if decay_rate <= 0:
        return float('inf')
    return math.log(2) / decay_rate


def get_activation_decay_rate(node_type: str) -> float:
    """
    Get activation decay rate for node type.

    Formula: rate = EMACT_DECAY_BASE × multiplier[type]

    Args:
        node_type: Node type string

    Returns:
        Decay rate (per second)
    """
    multiplier = settings.EMACT_DECAY_MULTIPLIERS.get(node_type, 1.0)
    return settings.EMACT_DECAY_BASE * multiplier


def get_weight_decay_rate(node_type: str) -> float:
    """
    Get weight decay rate for node type.

    Formula: rate = WEIGHT_DECAY_BASE × multiplier[type]

    Args:
        node_type: Node type string

    Returns:
        Decay rate (per second)
    """
    multiplier = settings.WEIGHT_DECAY_MULTIPLIERS.get(node_type, 1.0)
    return settings.WEIGHT_DECAY_BASE * multiplier


# === Activation Decay ===

def decay_node_activation(
    node: 'Node',
    dt: float,
    effective_delta: Optional[float] = None,
    graph: Optional['Graph'] = None
) -> Tuple[float, float]:
    """
    Apply exponential decay to node activation energy (single E_i).

    Formula: E_i ← λ^Δt × E_i, where λ = exp(-rate)

    With controller coupling:
    - If effective_delta provided: use it (criticality-adjusted)
    - Otherwise: use type-dependent base rate

    With PR-E enrichments (optional, behind feature flags):
    - Consolidation: (λ^Δt)^c_total slows decay for important patterns
    - Resistance: λ^(Δt/r_i) extends half-life for central/bridge nodes

    Args:
        node: Node to decay
        dt: Time duration (seconds)
        effective_delta: Optional criticality-adjusted decay rate
        graph: Optional graph (for consolidation/resistance computation)

    Returns:
        Tuple of (energy_before, energy_after)
    """
    energy_before = node.E  # Single-energy architecture

    if energy_before < settings.ENERGY_FLOOR:
        # Already at floor, skip
        return (energy_before, energy_before)

    # Determine decay rate
    if effective_delta is not None:
        # Use criticality-adjusted rate (bounded)
        decay_rate = np.clip(
            effective_delta,
            settings.EMACT_DECAY_MIN,
            settings.EMACT_DECAY_MAX
        )
    else:
        # Use type-dependent base rate
        node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
        decay_rate = get_activation_decay_rate(node_type)

    # === PR-E: Apply Decay Resistance (E.3) ===
    # Resistance divides the decay rate (extends half-life)
    if graph is not None:
        r_i = compute_decay_resistance(node, graph)
        effective_rate = decay_rate / r_i
    else:
        effective_rate = decay_rate

    # Compute base decay factor
    decay_factor = math.exp(-effective_rate * dt)

    # === PR-E: Apply Consolidation (E.2) ===
    # Consolidation powers the decay factor (brings it closer to 1, slowing decay)
    if graph is not None:
        c_total = compute_consolidation_factor(node, graph)
        if c_total > 0.0:
            # Raise to power: (λ^Δt)^c_total
            # When c_total < 1, this brings decay_factor closer to 1 (slower decay)
            decay_factor = decay_factor ** c_total

    energy_after = energy_before * decay_factor

    # Apply floor
    energy_after = max(energy_after, settings.ENERGY_FLOOR)

    # Write back
    node.E = energy_after  # Single-energy architecture

    return (energy_before, energy_after)


def activation_decay_tick(
    graph: 'Graph',
    dt: float,
    effective_delta: Optional[float] = None
) -> Tuple[int, float, float]:
    """
    Apply activation decay to all nodes in graph.

    Args:
        graph: Graph with nodes
        dt: Time duration (seconds)
        effective_delta: Optional criticality-adjusted decay rate

    Returns:
        Tuple of (nodes_decayed, total_energy_before, total_energy_after)
    """
    nodes_decayed = 0
    total_before = 0.0
    total_after = 0.0

    for node in graph.nodes.values():
        # Pass graph for consolidation/resistance computation (PR-E)
        before, after = decay_node_activation(node, dt, effective_delta, graph)

        if before > settings.ENERGY_FLOOR:
            total_before += before
            total_after += after
            nodes_decayed += 1

    return (nodes_decayed, total_before, total_after)


# === Weight Decay ===

def decay_node_weight(node: 'Node', dt: float) -> Tuple[float, float]:
    """
    Apply exponential decay to node weight (log scale).

    Formula: log_W ← log_W - (rate × dt)
    Equivalent to: W ← W × exp(-rate × dt)

    Args:
        node: Node to decay weight
        dt: Time duration (seconds)

    Returns:
        Tuple of (log_weight_before, log_weight_after)
    """
    log_weight_before = node.log_weight

    # Get type-dependent weight decay rate
    node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
    decay_rate = get_weight_decay_rate(node_type)

    # Apply decay (log space: subtract)
    log_weight_after = log_weight_before - (decay_rate * dt)

    # Apply floor
    log_weight_after = max(log_weight_after, settings.WEIGHT_FLOOR)

    # Write back
    node.log_weight = log_weight_after

    return (log_weight_before, log_weight_after)


def decay_link_weight(link: 'Link', dt: float) -> Tuple[float, float]:
    """
    Apply exponential decay to link weight (log scale).

    Args:
        link: Link to decay weight
        dt: Time duration (seconds)

    Returns:
        Tuple of (log_weight_before, log_weight_after)
    """
    log_weight_before = link.log_weight

    # Get type-dependent weight decay rate (use link type)
    link_type = link.link_type.value if hasattr(link.link_type, 'value') else str(link.link_type)
    decay_rate = get_weight_decay_rate(link_type)

    # Apply decay
    log_weight_after = log_weight_before - (decay_rate * dt)

    # Apply floor
    log_weight_after = max(log_weight_after, settings.WEIGHT_FLOOR)

    # Write back
    link.log_weight = log_weight_after

    return (log_weight_before, log_weight_after)


def weight_decay_tick(graph: 'Graph', dt: float) -> Tuple[int, int]:
    """
    Apply weight decay to all nodes and links in graph.

    NOTE: This runs on SLOW cadence (not every tick).
    Typical: once per minute vs activation decay every tick.

    Args:
        graph: Graph with nodes and links
        dt: Time duration (seconds)

    Returns:
        Tuple of (nodes_decayed, links_decayed)
    """
    nodes_decayed = 0
    links_decayed = 0

    # Decay node weights
    for node in graph.nodes.values():
        decay_node_weight(node, dt)
        nodes_decayed += 1

    # Decay link weights
    for link in graph.links.values():
        decay_link_weight(link, dt)
        links_decayed += 1

    return (nodes_decayed, links_decayed)


# === Metrics & Observability ===

def compute_half_life_estimates(graph: 'Graph', weight_mode: bool = False) -> Dict[str, float]:
    """
    Compute half-life estimates per node type.

    Args:
        graph: Graph with nodes
        weight_mode: If True, compute weight decay half-lives; else activation

    Returns:
        Dict of type → half-life (seconds)
    """
    half_lives = {}

    # Get unique types
    types_seen = set()
    for node in graph.nodes.values():
        node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
        types_seen.add(node_type)

    # Compute half-life for each type
    for node_type in types_seen:
        if weight_mode:
            decay_rate = get_weight_decay_rate(node_type)
        else:
            decay_rate = get_activation_decay_rate(node_type)

        half_lives[node_type] = compute_half_life(decay_rate)

    return half_lives


def compute_energy_histogram(graph: 'Graph') -> Dict[str, List[float]]:
    """
    Compute energy distribution per node type.

    Returns:
        Dict of type → list of energy values
    """
    histogram = defaultdict(list)

    for node in graph.nodes.values():
        node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
        histogram[node_type].append(node.E)  # Single-energy architecture

    return dict(histogram)


def compute_weight_histogram(graph: 'Graph') -> Dict[str, List[float]]:
    """
    Compute weight distribution per node type.

    Returns:
        Dict of type → list of log_weight values
    """
    histogram = defaultdict(list)

    for node in graph.nodes.values():
        node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
        histogram[node_type].append(node.log_weight)

    return dict(histogram)


# === Main Decay Tick ===

def decay_tick(graph: 'Graph', ctx: Optional[DecayContext] = None) -> DecayMetrics:
    """
    Execute one tick of decay (activation and optionally weight).

    Implements dual-clock forgetting per spec §2:
    - Activation decay: fast, per-tick, criticality-coupled
    - Weight decay: slow, periodic, independent

    Args:
        graph: Graph with nodes and links
        ctx: Decay configuration (defaults if None)

    Returns:
        DecayMetrics with comprehensive observability
    """
    if ctx is None:
        ctx = DecayContext()

    # === Activation Decay (always) ===
    nodes_decayed, total_before, total_after = activation_decay_tick(
        graph, ctx.dt, ctx.effective_delta_E
    )

    energy_lost = total_before - total_after

    # Determine effective delta used
    if ctx.effective_delta_E is not None:
        delta_E = ctx.effective_delta_E
    else:
        delta_E = settings.EMACT_DECAY_BASE  # Base rate

    # === Weight Decay (conditional) ===
    if ctx.apply_weight_decay:
        nodes_weight_decayed, links_weight_decayed = weight_decay_tick(graph, ctx.dt)
        delta_W = settings.WEIGHT_DECAY_BASE
    else:
        nodes_weight_decayed = 0
        links_weight_decayed = 0
        delta_W = 0.0

    # === Half-Life Estimates ===
    half_lives_activation = compute_half_life_estimates(graph, weight_mode=False)
    half_lives_weight = compute_half_life_estimates(graph, weight_mode=True)

    # === Histograms (expensive, sampled) ===
    if ctx.compute_histograms:
        energy_histogram = compute_energy_histogram(graph)
        weight_histogram = compute_weight_histogram(graph)
    else:
        energy_histogram = {}
        weight_histogram = {}

    # === AUC Activation (simplified: total energy) ===
    auc_activation_window = total_after

    return DecayMetrics(
        delta_E=delta_E,
        nodes_decayed=nodes_decayed,
        total_energy_before=total_before,
        total_energy_after=total_after,
        energy_lost=energy_lost,
        delta_W=delta_W,
        nodes_weight_decayed=nodes_weight_decayed,
        links_weight_decayed=links_weight_decayed,
        half_lives_activation=half_lives_activation,
        half_lives_weight=half_lives_weight,
        energy_histogram=energy_histogram,
        weight_histogram=weight_histogram,
        auc_activation_window=auc_activation_window
    )


# === PR-E: Foundations Enrichments ===

# E.2 Consolidation (prevents premature decay of important patterns)

def compute_consolidation_factor(node: 'Node', graph: 'Graph') -> float:
    """
    Compute consolidation factor c_total for this node.

    Consolidation slows decay for important patterns via:
    - c_retrieval: Node used in goal-serving (high WM presence)
    - c_affect: High emotional magnitude (||E_emo|| > 0.7)
    - c_goal: Unresolved goal link to active goal

    Formula: c_total = min(c_max, c_retrieval + c_affect + c_goal)

    Applied as: E_i ← (λ^Δt)^c_total × E_i

    Args:
        node: Node to compute consolidation for
        graph: Graph (for checking goal links)

    Returns:
        Consolidation factor ∈ [0, c_max]
    """
    from orchestration.core.settings import settings

    if not settings.CONSOLIDATION_ENABLED:
        return 0.0

    c_total = 0.0

    # c_retrieval: High WM presence indicates retrieval usage
    # Use ema_wm_presence as proxy for retrieval
    if hasattr(node, 'ema_wm_presence'):
        c_retrieval = settings.CONSOLIDATION_RETRIEVAL_BOOST * node.ema_wm_presence
        c_total += c_retrieval

    # c_affect: High emotional magnitude
    if hasattr(node, 'emotion_vector') and node.emotion_vector is not None:
        emotion_magnitude = float(np.linalg.norm(node.emotion_vector))
        if emotion_magnitude > 0.7:  # High-affect threshold
            c_affect = settings.CONSOLIDATION_AFFECT_BOOST * (emotion_magnitude - 0.7) / 0.3
            c_total += np.clip(c_affect, 0.0, settings.CONSOLIDATION_AFFECT_BOOST)

    # c_goal: Unresolved goal link to active goal
    from orchestration.core.types import LinkType
    if hasattr(graph, 'nodes'):
        for link in node.outgoing_links:
            if link.link_type == LinkType.RELATES_TO and hasattr(link.target, 'node_type'):
                target_type = link.target.node_type.value if hasattr(link.target.node_type, 'value') else str(link.target.node_type)
                if target_type in ['Goal', 'Personal_Goal']:
                    # Check if goal is active
                    if link.target.is_active():
                        c_total += settings.CONSOLIDATION_GOAL_BOOST
                        break  # Only count once

    # Cap at max
    c_total = min(c_total, settings.CONSOLIDATION_MAX_FACTOR)

    return c_total


# E.3 Decay Resistance (central/bridge nodes persist longer)

def compute_decay_resistance(node: 'Node', graph: 'Graph') -> float:
    """
    Compute decay resistance factor r_i for this node.

    Resistance extends half-life for important structural nodes via:
    - r_deg: High centrality (degree-based)
    - r_bridge: Cross-entity bridges (multi-entity membership)
    - r_type: Type-based importance (Memory, Principle persist longer)

    Formula: r_i = min(r_max, r_deg · r_bridge · r_type)

    Applied as: E_i ← (λ^Δt / r_i) × E_i

    Args:
        node: Node to compute resistance for
        graph: Graph (for checking entity membership)

    Returns:
        Resistance factor ∈ [1.0, r_max]
    """
    from orchestration.core.settings import settings

    if not settings.DECAY_RESISTANCE_ENABLED:
        return 1.0  # No resistance

    # r_deg: Centrality-based resistance
    degree = len(node.outgoing_links) + len(node.incoming_links)
    r_deg = 1.0 + 0.1 * math.tanh(degree / 20.0)

    # r_bridge: Cross-entity bridge resistance
    # Count how many entities this node belongs to
    from orchestration.core.types import LinkType
    entity_count = 0
    if hasattr(graph, 'subentities'):
        for link in node.outgoing_links:
            if link.link_type == LinkType.BELONGS_TO:
                entity_count += 1

    if entity_count > 1:
        r_bridge = 1.0 + 0.15 * min(1.0, (entity_count - 1) / 5.0)
    else:
        r_bridge = 1.0

    # r_type: Type-based resistance
    node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
    type_resistance_map = {
        "Memory": 1.2,
        "Episodic_Memory": 1.25,
        "Principle": 1.15,
        "Personal_Value": 1.15,
        "Task": 1.0,
        "Event": 1.0,
    }
    r_type = type_resistance_map.get(node_type, 1.0)

    # Combine
    r_i = r_deg * r_bridge * r_type

    # Cap at max
    r_i = min(r_i, settings.DECAY_RESISTANCE_MAX_FACTOR)

    return r_i


## <<< END orchestration/mechanisms/decay.py
---

## >>> BEGIN orchestration/mechanisms/diffusion_runtime.py
<!-- mtime: 2025-10-24T20:39:05; size_chars: 27306 -->

"""
Diffusion Runtime Accumulator & Stride Executor

Manages staged energy deltas for stride-based diffusion.

Architecture:
- delta_E: Accumulates energy transfers during tick
- active: Nodes with E >= theta or receiving energy this tick
- shadow: 1-hop neighbors of active nodes (frontier expansion)
- Stride executor: Selects best edges and stages energy transfers

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/foundations/diffusion.md
"""

import math
import random
import time
import numpy as np
from typing import Dict, Set, Optional, Any, TYPE_CHECKING
from dataclasses import dataclass
from orchestration.core.entity_context_extensions import effective_log_weight_link

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.link import Link
    from orchestration.mechanisms.strengthening import LearningController


@dataclass
class CostBreakdown:
    """
    Forensic trail for link cost computation.

    Enables attribution tracking - understanding exactly why a link was chosen.
    All intermediate values preserved for observability.

    Fields:
        total_cost: Final cost after all modulations (lower = better)
        ease: exp(log_weight) - structural ease of traversal
        ease_cost: 1/ease - cost from link strength
        goal_affinity: cos(target.emb, goal.emb) - alignment with goal
        res_mult: Resonance multiplier from emotion gates (1.0 = neutral)
        res_score: Resonance alignment score (cosine similarity)
        comp_mult: Complementarity multiplier from emotion gates (1.0 = neutral)
        emotion_mult: Combined emotion multiplier (res_mult * comp_mult)
        base_cost: Cost before emotion modulation (ease_cost - goal_affinity)
        reason: Human-readable explanation of why this link was chosen
    """
    total_cost: float
    ease: float
    ease_cost: float
    goal_affinity: float
    res_mult: float
    res_score: float
    comp_mult: float
    emotion_mult: float
    base_cost: float
    reason: str


class DiffusionRuntime:
    """
    Runtime accumulator for stride-based energy diffusion.

    Collects energy deltas during traversal, applies atomically at end of tick.
    Maintains active/shadow frontier for O(frontier) performance.

    Attributes:
        delta_E: Accumulated energy deltas per node (staged)
        active: Nodes with E >= theta or touched this tick
        shadow: 1-hop neighbors of active (candidate frontier)
    """
    __slots__ = ("delta_E", "active", "shadow", "stride_relatedness_scores", "current_frontier_nodes")

    def __init__(self):
        """Initialize empty runtime accumulator."""
        self.delta_E: Dict[str, float] = {}
        self.active: Set[str] = set()
        self.shadow: Set[str] = set()

        # Coherence tracking (E.6) - collected during stride execution
        self.stride_relatedness_scores: List[float] = []
        self.current_frontier_nodes: List[Any] = []

    def add(self, node_id: str, delta: float) -> None:
        """
        Stage energy delta for node.

        Accumulates delta into staging buffer. Applied atomically at end of tick.

        Args:
            node_id: Node identifier
            delta: Energy change (positive = gain, negative = loss)

        Example:
            >>> rt = DiffusionRuntime()
            >>> rt.add("n1", -0.05)  # Source loses energy
            >>> rt.add("n2", +0.05)  # Target gains energy
        """
        self.delta_E[node_id] = self.delta_E.get(node_id, 0.0) + delta

    def clear_deltas(self) -> None:
        """Clear staged deltas after applying."""
        self.delta_E.clear()

    def compute_frontier(self, graph: 'Graph') -> None:
        """
        Recompute active and shadow sets from current energy state.

        Active: nodes with E >= theta
        Shadow: 1-hop neighbors of active nodes

        Args:
            graph: Consciousness graph

        Side effects:
            Updates self.active and self.shadow
        """
        # Active = nodes above threshold
        self.active = {
            node.id for node in graph.nodes.values()
            if node.is_active()
        }

        # Shadow = 1-hop neighbors of active
        self.shadow = set()
        for node_id in self.active:
            node = graph.nodes.get(node_id)
            if node:
                # Add all outgoing neighbors to shadow
                for link in node.outgoing_links:
                    self.shadow.add(link.target.id)

        # Shadow excludes already-active nodes
        self.shadow -= self.active

    def get_conservation_error(self) -> float:
        """
        Compute total staged energy delta (should be ~0 for conservation).

        Returns:
            Sum of all deltas (conservation error if != 0)

        Example:
            >>> error = rt.get_conservation_error()
            >>> assert abs(error) < 1e-6, "Energy not conserved!"
        """
        return sum(self.delta_E.values())


def _compute_link_emotion(link: 'Link', energy_flow: float) -> Optional[np.ndarray]:
    """
    Compute link emotion by interpolating source and target node emotions.

    Phase 1 implementation: Simple linear interpolation weighted by energy flow.
    Higher energy flow → stronger emotion transfer.

    Args:
        link: Link being traversed
        energy_flow: Energy flowing through link this stride

    Returns:
        Link emotion vector [valence, arousal] or None if no node emotions exist

    Example:
        >>> link_emotion = _compute_link_emotion(link, energy_flow=0.05)
        >>> # Returns blend of source and target emotions weighted by flow
    """
    # Check if nodes have emotions
    source_emotion = getattr(link.source, 'emotion_vector', None)
    target_emotion = getattr(link.target, 'emotion_vector', None)

    if source_emotion is None and target_emotion is None:
        return None  # No emotion to propagate

    # Initialize neutral if missing
    if source_emotion is None:
        source_emotion = np.array([0.0, 0.0])
    if target_emotion is None:
        target_emotion = np.array([0.0, 0.0])

    # Interpolate: blend source and target emotions
    # Weight by energy flow intensity (higher flow → more blending)
    flow_weight = min(energy_flow * 10.0, 1.0)  # Scale factor for visibility

    # Simple average weighted by flow
    link_emotion = (1.0 - flow_weight * 0.5) * source_emotion + flow_weight * 0.5 * target_emotion

    return link_emotion


def _emit_link_emotion_event(
    link: 'Link',
    emotion_vector: np.ndarray,
    broadcaster: Any,
    sample_rate: float
) -> None:
    """
    Emit link.emotion.update event via WebSocket.

    Event format (matches frontend expectation):
    {
        type: 'link.emotion.update',
        link_id: string,
        emotion_magnitude: number,
        top_axes: [
            {axis: 'valence', value: number},
            {axis: 'arousal', value: number}
        ],
        timestamp: string
    }

    Args:
        link: Link being updated
        emotion_vector: Computed emotion vector [valence, arousal]
        broadcaster: WebSocket broadcaster
        sample_rate: Emission sampling rate (0-1)
    """
    # Sample emission to reduce WebSocket traffic
    if random.random() > sample_rate:
        return

    if not broadcaster or not hasattr(broadcaster, 'is_available'):
        return

    if not broadcaster.is_available():
        return

    # Compute magnitude
    magnitude = float(np.linalg.norm(emotion_vector))

    # Extract top axes (valence and arousal for 2D affect)
    top_axes = [
        {"axis": "valence", "value": float(emotion_vector[0])},
        {"axis": "arousal", "value": float(emotion_vector[1]) if len(emotion_vector) > 1 else 0.0}
    ]

    # Emit event
    import asyncio
    asyncio.create_task(broadcaster.broadcast_event("link.emotion.update", {
        "link_id": link.id,
        "emotion_magnitude": magnitude,
        "top_axes": top_axes,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    }))


def execute_stride_step(
    graph: 'Graph',
    rt: DiffusionRuntime,
    alpha_tick: float = 0.1,
    dt: float = 1.0,
    sample_rate: float = 0.1,
    learning_controller: Optional['LearningController'] = None,
    enable_strengthening: bool = True,
    goal_embedding: Optional[np.ndarray] = None,
    broadcaster: Optional[Any] = None,
    enable_link_emotion: bool = True,
    current_entity_id: Optional[str] = None
) -> int:
    """
    Execute one stride step: select best edges from active nodes and stage energy transfers.

    Algorithm (spec: traversal_v2.md §3.4):
        For each active node:
            1. Select best outgoing edge (argmin cost: ease + goal + emotion)
            2. Compute ΔE = E_src · f(w) · α_tick · Δt
            3. Stage transfer: rt.add(src, -ΔE), rt.add(dst, +ΔE)
            4. Strengthen link (Hebbian learning - integrated)
            5. Emit stride.exec event (sampled)

    Where f(w) = exp(log_weight) per spec.

    Cost computation (traversal_v2.md §3.4):
        cost = base_cost * emotion_mult
        - base_cost = (1/ease) - goal_affinity
        - ease = exp(log_weight)
        - goal_affinity = cos(target.embedding, goal_embedding)
        - emotion_mult = resonance_mult * complementarity_mult (when EMOTION_GATES_ENABLED)

    Strengthening: Links strengthen when energy flows through them (spec: link_strengthening.md).
    Only when BOTH nodes inactive (D020 rule) - prevents runaway strengthening.

    Args:
        graph: Consciousness graph
        rt: DiffusionRuntime accumulator
        alpha_tick: Redistribution share (fraction of energy redistributed)
        dt: Time delta (tick interval in seconds)
        sample_rate: Emission sampling rate for observability
        learning_controller: Optional learning rate controller (created if None)
        enable_strengthening: Whether to apply link strengthening (default True)
        goal_embedding: Optional goal vector for goal-affinity cost computation
        broadcaster: Optional WebSocket broadcaster for emotion events
        enable_link_emotion: Whether to compute and emit link emotions (default True)
        current_entity_id: Optional entity ID for personalized weight computation (Priority 4)

    Returns:
        Number of strides executed

    Example:
        >>> rt = DiffusionRuntime()
        >>> rt.active = {"n1", "n2", "n3"}
        >>> strides = execute_stride_step(graph, rt, alpha_tick=0.1, dt=1.0, goal_embedding=goal_vec)
        >>> print(f"Executed {strides} strides")
    """
    # Create learning controller if not provided
    if learning_controller is None and enable_strengthening:
        from orchestration.mechanisms.strengthening import LearningController
        from orchestration.core.settings import settings
        learning_controller = LearningController(base_rate=settings.LEARNING_RATE_BASE)

    strides_executed = 0

    # === E.6: Collect current frontier nodes for coherence metric ===
    if settings.COHERENCE_METRIC_ENABLED:
        rt.current_frontier_nodes = [graph.nodes[nid] for nid in rt.active if nid in graph.nodes]
        rt.stride_relatedness_scores = []  # Reset for this tick

    # Iterate over active nodes
    for src_id in list(rt.active):
        node = graph.nodes.get(src_id)
        if not node:
            continue

        E_src = node.E
        if E_src <= 0.0:
            continue

        # Construct emotion context for gate computation
        emotion_context = None
        if hasattr(node, 'emotion_vector') and node.emotion_vector is not None:
            emotion_magnitude = np.linalg.norm(node.emotion_vector)
            emotion_context = {
                'entity_affect': node.emotion_vector,  # Use node's emotion as current affect
                'intensity': emotion_magnitude,
                'context_gate': 1.0  # Neutral context (TODO: infer from task mode)
            }

        # Select best outgoing edge using cost computation (K=1 for now)
        # Link selection is entity-aware when current_entity_id provided (Priority 4)
        result = _select_best_outgoing_link(node, goal_embedding=goal_embedding, emotion_context=emotion_context, current_entity_id=current_entity_id)
        if not result:
            continue

        best_link, cost_breakdown = result

        # === E.6: Collect stride relatedness for coherence metric ===
        if settings.COHERENCE_METRIC_ENABLED:
            from orchestration.mechanisms.coherence_metric import assess_stride_relatedness
            relatedness = assess_stride_relatedness(node, best_link.target, best_link)
            rt.stride_relatedness_scores.append(relatedness)

        # Compute ease from effective weight: f(w) = exp(effective_log_weight)
        # Uses entity-specific overlay when current_entity_id provided (Priority 4)
        # Falls back to global log_weight when entity_id is None
        if current_entity_id:
            log_w = effective_log_weight_link(best_link, current_entity_id)
        else:
            log_w = best_link.log_weight
        ease = math.exp(log_w)

        # Compute energy transfer: ΔE = E_src · f(w) · α · Δt
        delta_E = E_src * ease * alpha_tick * dt

        if delta_E <= 1e-9:  # Skip negligible transfers
            continue

        # === PR-E: Apply Stickiness (E.4) ===
        # Stickiness determines how much energy target retains
        # Memory nodes: high stickiness (energy sticks), Task nodes: low stickiness (energy flows)
        stickiness = compute_stickiness(best_link.target, graph)
        retained_delta_E = stickiness * delta_E

        # Stage transfer (non-conservative if stickiness < 1.0: energy dissipates)
        rt.add(src_id, -delta_E)  # Source loses full amount
        rt.add(best_link.target.id, +retained_delta_E)  # Target gains retained amount
        # Energy leak: (delta_E - retained_delta_E) dissipates to environment

        # Compute and emit link emotion (Phase 1: interpolation)
        if enable_link_emotion and broadcaster is not None:
            link_emotion = _compute_link_emotion(best_link, delta_E)
            if link_emotion is not None:
                # Update link's emotion vector
                best_link.emotion_vector = link_emotion
                # Emit event to frontend
                _emit_link_emotion_event(best_link, link_emotion, broadcaster, sample_rate)

        # Strengthen link (Hebbian learning - integrated with diffusion)
        if enable_strengthening and learning_controller is not None:
            from orchestration.mechanisms.strengthening import strengthen_during_stride
            strengthen_during_stride(best_link, delta_E, learning_controller)

        # Learn RELATES_TO from boundary strides (spec: subentity_layer.md §2.5)
        # Detect if this stride crosses an entity boundary
        if hasattr(graph, 'subentities') and graph.subentities:
            from orchestration.core.types import LinkType

            # Find which entities the source and target nodes belong to
            source_entities = []
            target_entities = []

            # Check source node's BELONGS_TO links
            for link in node.outgoing_links:
                if link.link_type == LinkType.BELONGS_TO:
                    source_entities.append(link.target)

            # Check target node's BELONGS_TO links
            for link in best_link.target.outgoing_links:
                if link.link_type == LinkType.BELONGS_TO:
                    target_entities.append(link.target)

            # If nodes belong to different entities, this is a boundary stride
            for src_entity in source_entities:
                for tgt_entity in target_entities:
                    if src_entity.id != tgt_entity.id:
                        # Boundary stride detected!
                        from orchestration.mechanisms.entity_activation import learn_relates_to_from_boundary_stride
                        learn_relates_to_from_boundary_stride(
                            src_entity,
                            tgt_entity,
                            delta_E,
                            graph,
                            learning_rate=0.05
                        )

        strides_executed += 1

        # Emit stride.exec event with forensic trail (sampled for performance)
        if broadcaster is not None and random.random() < sample_rate:
            # Get threshold value (phi) for forensic trail
            phi = getattr(node, 'theta', 0.0)

            stride_data = {
                'src_node': src_id,
                'dst_node': best_link.target.id,
                'link_id': best_link.id,
                # Forensic trail fields
                'phi': round(phi, 4),  # Threshold
                'ease': round(cost_breakdown.ease, 4),
                'ease_cost': round(cost_breakdown.ease_cost, 4),
                'goal_affinity': round(cost_breakdown.goal_affinity, 4),
                'res_mult': round(cost_breakdown.res_mult, 4),
                'res_score': round(cost_breakdown.res_score, 4),
                'comp_mult': round(cost_breakdown.comp_mult, 4),
                'emotion_mult': round(cost_breakdown.emotion_mult, 4),
                'base_cost': round(cost_breakdown.base_cost, 4),
                'total_cost': round(cost_breakdown.total_cost, 4),
                'reason': cost_breakdown.reason,
                # Energy transfer
                'delta_E': round(delta_E, 6),
                'stickiness': round(stickiness, 4),
                'retained_delta_E': round(retained_delta_E, 6),
                # Metadata
                'chosen': True  # This link was selected (lowest cost)
            }

            # Emit via broadcaster
            broadcaster.stride_exec(stride_data)

    return strides_executed


def _compute_link_cost(
    link: 'Link',
    goal_embedding: Optional[np.ndarray] = None,
    emotion_context: Optional[Dict] = None,
    current_entity_id: Optional[str] = None
) -> CostBreakdown:
    """
    Compute traversal cost for link with full forensic trail (lower cost = better).

    Cost components (spec: traversal_v2.md §3.4):
    - Ease cost: 1/exp(effective_log_weight) - harder to traverse weak links (entity-aware, Priority 4)
    - Goal affinity: -cos(link.target.embedding, goal) - prefer goal-aligned targets
    - Emotion gates: resonance/complementarity multipliers (modulate base cost)

    Args:
        link: Link to evaluate
        goal_embedding: Optional goal vector for affinity computation
        emotion_context: Optional emotion state dict with:
            - entity_affect: np.ndarray - current entity affect vector
            - context_gate: float - context modulation (0-2, focus vs recovery)
            - intensity: float - affect magnitude
        current_entity_id: Optional entity ID for personalized weight computation (Priority 4)

    Returns:
        CostBreakdown with total_cost and all intermediate values for observability

    Example:
        >>> breakdown = _compute_link_cost(link, goal_embedding=goal_vec, current_entity_id="entity_translator")
        >>> # Strong link (log_weight=0.7) aligned with goal → low cost
        >>> # breakdown.ease = 2.0, breakdown.goal_affinity = 0.8, breakdown.total_cost = 0.2
    """
    import numpy as np
    from orchestration.core.settings import settings

    # 1. Ease cost: 1/exp(effective_log_weight) - entity-aware (Priority 4)
    #    Strong links (log_weight >> 0) have low ease cost
    #    Weak links (log_weight << 0) have high ease cost
    #    Uses entity-specific overlays when current_entity_id provided
    if current_entity_id:
        log_w = effective_log_weight_link(link, current_entity_id)
    else:
        log_w = link.log_weight
    ease = math.exp(log_w)
    ease_cost = 1.0 / max(ease, 1e-6)  # Avoid division by zero

    # 2. Goal affinity bonus (negative = reduce cost)
    #    High similarity to goal reduces cost (prefer goal-aligned paths)
    goal_affinity = 0.0
    if goal_embedding is not None and hasattr(link.target, 'embedding') and link.target.embedding is not None:
        # Cosine similarity
        target_emb = link.target.embedding
        norm_goal = np.linalg.norm(goal_embedding)
        norm_target = np.linalg.norm(target_emb)

        if norm_goal > 1e-9 and norm_target > 1e-9:
            cos_sim = np.dot(goal_embedding, target_emb) / (norm_goal * norm_target)
            goal_affinity = np.clip(cos_sim, -1.0, 1.0)

    # 3. Emotion gates (resonance + complementarity)
    #    Modulate base cost multiplicatively per specs:
    #    - emotion_complementarity.md - regulation via opposites
    #    - emotion_weighted_traversal.md - coherence via similarity
    emotion_mult = 1.0  # Neutral default
    res_mult = 1.0  # Neutral (no resonance modulation)
    res_score = 0.0  # No alignment
    comp_mult = 1.0  # Neutral (no complementarity modulation)

    if settings.EMOTION_GATES_ENABLED and emotion_context:
        entity_affect = emotion_context.get('entity_affect')
        link_emotion = getattr(link, 'emotion_vector', None)

        if entity_affect is not None and link_emotion is not None:
            from orchestration.mechanisms.emotion_coloring import (
                resonance_multiplier,
                complementarity_multiplier
            )

            # Resonance gate (coherence - prefer emotionally aligned paths)
            # r > 0 (aligned) → m_res < 1 (attractive, easier)
            # r < 0 (clash) → m_res > 1 (repulsive, harder)
            res_mult, res_score = resonance_multiplier(entity_affect, link_emotion)

            # Complementarity gate (regulation - prefer opposite affect for balance)
            # High opposition → lower multiplier → lower cost (regulatory pull)
            intensity_gate = emotion_context.get('intensity', np.linalg.norm(entity_affect))
            context_gate = emotion_context.get('context_gate', 1.0)  # 0-2 scale
            comp_mult = complementarity_multiplier(
                entity_affect,
                link_emotion,
                intensity_gate=np.clip(intensity_gate, 0.0, 1.0),
                context_gate=context_gate
            )

            # Combine gates multiplicatively (per spec: order doesn't matter)
            emotion_mult = res_mult * comp_mult

    # Total cost: base cost modulated by emotion gates
    base_cost = ease_cost - goal_affinity
    total_cost = base_cost * emotion_mult

    # Generate human-readable reason for why this link was chosen
    reason_parts = []
    if ease > 1.5:
        reason_parts.append(f"strong_link(ease={ease:.2f})")
    elif ease < 0.5:
        reason_parts.append(f"weak_link(ease={ease:.2f})")

    if goal_affinity > 0.5:
        reason_parts.append(f"goal_aligned(aff={goal_affinity:.2f})")
    elif goal_affinity < -0.5:
        reason_parts.append(f"goal_opposed(aff={goal_affinity:.2f})")

    if res_mult < 0.9:
        reason_parts.append(f"resonance_attract(r={res_score:.2f})")
    elif res_mult > 1.1:
        reason_parts.append(f"resonance_repel(r={res_score:.2f})")

    if comp_mult < 0.9:
        reason_parts.append(f"regulation_pull")

    reason = " + ".join(reason_parts) if reason_parts else "neutral"

    # Return full breakdown for forensic trail
    return CostBreakdown(
        total_cost=total_cost,
        ease=ease,
        ease_cost=ease_cost,
        goal_affinity=goal_affinity,
        res_mult=res_mult,
        res_score=res_score,
        comp_mult=comp_mult,
        emotion_mult=emotion_mult,
        base_cost=base_cost,
        reason=reason
    )


def _select_best_outgoing_link(
    node,
    goal_embedding: Optional[np.ndarray] = None,
    emotion_context: Optional[Dict] = None,
    current_entity_id: Optional[str] = None
) -> Optional[tuple['Link', CostBreakdown]]:
    """
    Select best outgoing link from node (argmin cost) with full forensic trail.

    Uses cost computation with ease, goal affinity, and emotion gates.
    This is the V2 spec implementation (traversal_v2.md §3.4).
    Link selection is entity-aware when current_entity_id provided (Priority 4).

    Args:
        node: Source node
        goal_embedding: Optional goal vector for affinity-based selection
        emotion_context: Optional emotion state for gate computation
        current_entity_id: Optional entity ID for personalized weight computation (Priority 4)

    Returns:
        Tuple of (best_link, cost_breakdown), or None if no outgoing links

    Example:
        >>> result = _select_best_outgoing_link(node, goal_embedding=goal_vec, current_entity_id="entity_translator")
        >>> if result:
        >>>     best_link, breakdown = result
        >>>     print(f"Chosen link: {best_link.id}, reason: {breakdown.reason}")
    """
    if not node.outgoing_links:
        return None

    # Compute cost for each outgoing link (entity-aware when current_entity_id provided)
    link_costs = [
        (_compute_link_cost(link, goal_embedding, emotion_context, current_entity_id), link)
        for link in node.outgoing_links
    ]

    # Select link with minimum cost
    best_breakdown, best_link = min(link_costs, key=lambda x: x[0].total_cost)

    return (best_link, best_breakdown)


# === PR-E: E.4 Stickiness (energy retention during diffusion) ===

def compute_stickiness(node, graph: 'Graph') -> float:
    """
    Compute stickiness factor for this node.

    Stickiness determines how much energy a node retains during diffusion:
    - Memory nodes: high stickiness (0.9) - energy sticks
    - Task nodes: low stickiness (0.3) - energy flows freely
    - Default: medium stickiness (0.6)

    Additional factors:
    - Consolidation: +0.2 if consolidated (important patterns retain more)
    - Centrality: +0.1 * tanh(degree/20) for high-degree nodes

    Formula: s_j = clip(s_type + s_consolidation + s_centrality, 0.1, 1.0)

    Args:
        node: Target node receiving energy
        graph: Graph (for checking consolidation status)

    Returns:
        Stickiness factor ∈ [0.1, 1.0]
    """
    from orchestration.core.settings import settings

    if not settings.DIFFUSION_STICKINESS_ENABLED:
        return 1.0  # No stickiness effect, perfect transfer

    # s_type: Base stickiness by node type
    node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
    type_stickiness_map = {
        "Memory": settings.STICKINESS_TYPE_MEMORY,
        "Episodic_Memory": settings.STICKINESS_TYPE_MEMORY,
        "Principle": 0.85,
        "Personal_Value": 0.85,
        "Task": settings.STICKINESS_TYPE_TASK,
        "Event": 0.4,
    }
    s_type = type_stickiness_map.get(node_type, settings.STICKINESS_TYPE_DEFAULT)

    # s_consolidation: Boost if consolidated
    s_consolidation = 0.0
    if hasattr(node, 'consolidated') and node.consolidated:
        s_consolidation = settings.STICKINESS_CONSOLIDATION_BOOST

    # s_centrality: Boost for high-degree nodes (structural importance)
    degree = len(node.outgoing_links) + len(node.incoming_links)
    s_centrality = 0.1 * math.tanh(degree / 20.0)

    # Combine (additive)
    s_j = s_type + s_consolidation + s_centrality

    # Clamp to valid range
    s_j = np.clip(s_j, 0.1, 1.0)

    return s_j


## <<< END orchestration/mechanisms/diffusion_runtime.py
---

## >>> BEGIN orchestration/mechanisms/fanout_strategy.py
<!-- mtime: 2025-10-23T00:28:23; size_chars: 8987 -->

"""
Fanout Strategy - Local bottom-up topology adaptation

Implements adaptive candidate pruning based on outdegree:
- High fanout (d > 10): Selective (top-k=5)
- Medium fanout (3 <= d <= 10): Balanced (top-k=d/2)
- Low fanout (d < 3): Exhaustive (all edges)

With optional WM pressure modulation and top-K energy splitting.

Architecture:
- Strategy selection: Based on local outdegree only (no global topology)
- Candidate pruning: Pre-filter by quick heuristic (weight) before cost computation
- WM adaptation: Reduce top-k under working memory pressure
- Top-K split: Optional softmax energy distribution across K best links

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/runtime_engine/fanout_strategy.md
"""

import math
from enum import Enum
from typing import List, Tuple, Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from orchestration.core.link import Link


@dataclass
class FanoutConfig:
    """
    Configuration for fanout strategy selection.

    Attributes:
        fanout_low: Low fanout threshold. Default 3.
        fanout_high: High fanout threshold. Default 10.
        selective_topk: K for selective strategy (high fanout). Default 5.
        topk_split_enabled: Enable top-K energy distribution. Default False.
        topk_split_k: K for energy splitting. Default 3.
        topk_split_temperature: Softmax temperature. Default 1.0.
        wm_pressure_enabled: Enable WM pressure modulation. Default True.
        wm_pressure_threshold: WM headroom threshold (0-1). Default 0.2 (20%).
        wm_pressure_reduction: Reduction factor under pressure. Default 0.6 (40% cut).
        min_topk: Floor on top_k to prevent over-pruning. Default 2.
    """
    fanout_low: int = 3
    fanout_high: int = 10
    selective_topk: int = 5
    topk_split_enabled: bool = False
    topk_split_k: int = 3
    topk_split_temperature: float = 1.0
    wm_pressure_enabled: bool = True
    wm_pressure_threshold: float = 0.2
    wm_pressure_reduction: float = 0.6
    min_topk: int = 2


class FanoutStrategy(Enum):
    """
    Fanout strategy types.

    SELECTIVE: High fanout nodes (hubs) - prune to small top-k
    BALANCED: Medium fanout - prune to ~50% of edges
    EXHAUSTIVE: Low fanout - evaluate all edges
    """
    SELECTIVE = "selective"
    BALANCED = "balanced"
    EXHAUSTIVE = "exhaustive"


def select_strategy(
    outdegree: int,
    wm_headroom: Optional[float] = None,
    config: Optional[FanoutConfig] = None
) -> Tuple[FanoutStrategy, int]:
    """
    Select fanout strategy based on outdegree and WM pressure.

    Algorithm (spec §2.1):
    - High fanout (d > τ_high): Selective(top_k = k_high)
    - Medium (τ_low ≤ d ≤ τ_high): Balanced(top_k = round(d/2))
    - Low (d < τ_low): Exhaustive()
    - WM pressure: if headroom < threshold, reduce top_k by reduction factor

    Args:
        outdegree: Number of outgoing edges from node
        wm_headroom: Optional WM headroom (0-1, where 1=completely free)
        config: Fanout configuration (defaults if None)

    Returns:
        Tuple of (strategy, top_k)

    Example:
        >>> # High fanout node
        >>> strategy, k = select_strategy(outdegree=50)
        >>> # Returns (SELECTIVE, 5)
        >>>
        >>> # Medium fanout
        >>> strategy, k = select_strategy(outdegree=6)
        >>> # Returns (BALANCED, 3)
        >>>
        >>> # Low fanout
        >>> strategy, k = select_strategy(outdegree=2)
        >>> # Returns (EXHAUSTIVE, 2)
        >>>
        >>> # With WM pressure
        >>> strategy, k = select_strategy(outdegree=50, wm_headroom=0.1)
        >>> # Returns (SELECTIVE, 3) - reduced from 5 due to pressure
    """
    if config is None:
        config = FanoutConfig()

    # Base strategy from outdegree
    if outdegree > config.fanout_high:
        strategy = FanoutStrategy.SELECTIVE
        top_k = config.selective_topk
    elif outdegree >= config.fanout_low:
        strategy = FanoutStrategy.BALANCED
        top_k = max(1, outdegree // 2)
    else:
        strategy = FanoutStrategy.EXHAUSTIVE
        top_k = outdegree

    # WM pressure modulation (spec §2.1)
    if config.wm_pressure_enabled and wm_headroom is not None:
        if wm_headroom < config.wm_pressure_threshold:
            # Reduce top_k under pressure
            top_k = int(top_k * config.wm_pressure_reduction)
            top_k = max(config.min_topk, top_k)  # Floor to prevent over-pruning

    return strategy, top_k


def reduce_candidates(
    edges: List['Link'],
    strategy: FanoutStrategy,
    top_k: int
) -> List['Link']:
    """
    Prune edges based on fanout strategy.

    Uses quick heuristic (link log_weight) for pre-filtering.
    Full cost computation happens on reduced set.

    Algorithm (spec §2.1):
    - EXHAUSTIVE: Return all edges
    - SELECTIVE/BALANCED: Sort by log_weight, take top_k

    Args:
        edges: All outgoing edges from node
        strategy: Selected fanout strategy
        top_k: Number of candidates to keep

    Returns:
        Pruned edge list

    Example:
        >>> # Hub with 100 edges, selective strategy
        >>> pruned = reduce_candidates(edges, FanoutStrategy.SELECTIVE, top_k=5)
        >>> len(pruned)  # 5 (top by weight)
        >>>
        >>> # Low fanout, exhaustive
        >>> pruned = reduce_candidates(edges, FanoutStrategy.EXHAUSTIVE, top_k=2)
        >>> len(pruned)  # 2 (all edges)
    """
    if strategy == FanoutStrategy.EXHAUSTIVE:
        return edges

    if len(edges) <= top_k:
        # Already small enough
        return edges

    # Sort by log_weight (quick heuristic, not full cost)
    # Higher weight = stronger attractor = lower cost
    sorted_edges = sorted(edges, key=lambda e: e.log_weight, reverse=True)

    # Take top_k
    return sorted_edges[:top_k]


def compute_top_k_split(
    edges_with_costs: List[Tuple['Link', float]],
    k: int,
    temperature: float = 1.0
) -> List[Tuple['Link', float]]:
    """
    Compute top-K energy split using softmax over costs.

    Optional feature (spec §2.3) for distributing energy across K best edges
    instead of sending all to single best edge.

    Algorithm:
    π_k = softmax(-c_k / T)
    Returns (link, π_k) pairs where sum(π_k) = 1.0

    Args:
        edges_with_costs: List of (link, cost) tuples
        k: Number of edges to split across
        temperature: Softmax temperature (higher = more uniform)

    Returns:
        List of (link, energy_fraction) tuples

    Example:
        >>> edges_costs = [(link1, 0.5), (link2, 1.0), (link3, 1.5)]
        >>> split = compute_top_k_split(edges_costs, k=2, temperature=1.0)
        >>> # Returns [(link1, 0.73), (link2, 0.27)] - fractions sum to 1.0
    """
    if k <= 0:
        return []

    # Sort by cost (ascending)
    sorted_items = sorted(edges_with_costs, key=lambda x: x[1])

    # Take top-k (lowest cost)
    top_k_items = sorted_items[:k]

    if len(top_k_items) == 0:
        return []

    # Softmax over -cost/T
    # (negative because lower cost = better, higher probability)
    logits = [-cost / temperature for _, cost in top_k_items]

    # Compute softmax
    max_logit = max(logits)
    exp_logits = [math.exp(l - max_logit) for l in logits]  # Numerical stability
    sum_exp = sum(exp_logits)

    if sum_exp == 0:
        # Fallback: uniform distribution
        uniform_prob = 1.0 / len(top_k_items)
        return [(link, uniform_prob) for link, _ in top_k_items]

    probs = [e / sum_exp for e in exp_logits]

    return [(link, prob) for (link, _), prob in zip(top_k_items, probs)]


def get_prune_rate(
    original_count: int,
    pruned_count: int
) -> float:
    """
    Compute prune rate for observability.

    Args:
        original_count: Number of edges before pruning
        pruned_count: Number of edges after pruning

    Returns:
        Prune rate (0-1, where 1 = 100% pruned)

    Example:
        >>> rate = get_prune_rate(100, 5)
        >>> # 0.95 (95% pruned)
    """
    if original_count == 0:
        return 0.0

    return (original_count - pruned_count) / original_count


def get_diagnostics(
    outdegree: int,
    strategy: FanoutStrategy,
    top_k: int,
    wm_headroom: Optional[float] = None,
    prune_rate: Optional[float] = None
) -> dict:
    """
    Get fanout diagnostics for observability.

    Returns:
        Dictionary with diagnostic fields

    Example:
        >>> diag = get_diagnostics(
        ...     outdegree=50,
        ...     strategy=FanoutStrategy.SELECTIVE,
        ...     top_k=5,
        ...     prune_rate=0.9
        ... )
        >>> print(diag)
        {
            'outdegree': 50,
            'strategy': 'selective',
            'top_k': 5,
            'wm_headroom': None,
            'prune_rate': 0.9
        }
    """
    return {
        'outdegree': outdegree,
        'strategy': strategy.value,
        'top_k': top_k,
        'wm_headroom': wm_headroom,
        'prune_rate': prune_rate
    }


## <<< END orchestration/mechanisms/fanout_strategy.py
---

## >>> BEGIN orchestration/mechanisms/valence.py
<!-- mtime: 2025-10-22T21:44:26; size_chars: 21913 -->

"""
Surprise-Gated Composite Valence (v1.5)

Implements self-calibrating hunger gates using z-score surprise:
- Seven hungers: Homeostasis, Goal, Idsubentity, Completeness, Complementarity, Integration, Ease
- EMA baselines (μ, σ) per hunger per subentity
- Positive surprise gates (δ_H = max(0, z_H))
- Normalized composite valence: V_ij = Σ_H (g_H × ν_H(i→j))

Author: AI #4
Created: 2025-10-20
Dependencies: sub_entity_core, numpy
Zero-Constants: All gates self-calibrate from experience
"""

import numpy as np
from typing import Dict, List, Set
from orchestration.mechanisms.sub_entity_core import (
    SubEntity,
    EntityExtentCentroid,
    IdentityEmbedding,
    BetaLearner
)


# --- Data Structures for Advanced Hungers ---
# Note: EntityExtentCentroid, IdentityEmbedding, BetaLearner are in sub_entity_core.py

class AffectVector:
    """
    Emotional coloring of nodes

    Simplified Phase 1: Use 2D valence-arousal model
    """

    @staticmethod
    def extract_affect(node_description: str) -> np.ndarray:
        """
        Extract affect vector from node description

        Phase 1 heuristic: Keyword-based valence detection

        Args:
            node_description: Node text content

        Returns:
            affect: 2D vector [valence, arousal] in [-1, 1]
        """
        # Valence keywords (positive/negative)
        positive_words = {'good', 'happy', 'joy', 'success', 'love', 'peace', 'hope', 'win'}
        negative_words = {'bad', 'sad', 'fear', 'fail', 'hate', 'anger', 'worry', 'lose'}

        # Arousal keywords (high/low)
        high_arousal = {'urgent', 'panic', 'excited', 'intense', 'critical', 'vital'}
        low_arousal = {'calm', 'peace', 'steady', 'slow', 'gentle', 'quiet'}

        text = node_description.lower()
        words = text.split()

        # Count keywords
        positive_count = sum(1 for w in words if w in positive_words)
        negative_count = sum(1 for w in words if w in negative_words)
        high_arousal_count = sum(1 for w in words if w in high_arousal)
        low_arousal_count = sum(1 for w in words if w in low_arousal)

        # Compute valence
        if positive_count + negative_count > 0:
            valence = (positive_count - negative_count) / (positive_count + negative_count)
        else:
            valence = 0.0

        # Compute arousal
        if high_arousal_count + low_arousal_count > 0:
            arousal = (high_arousal_count - low_arousal_count) / (high_arousal_count + low_arousal_count)
        else:
            arousal = 0.0

        return np.array([valence, arousal])


# --- Hunger Score Functions ---

def hunger_homeostasis(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph
) -> float:
    """
    Homeostasis hunger: fill gaps to survive.

    Formula: ν_homeostasis = G_j / (S_i + G_j + ε)

    Where:
        S_i = slack at source = max(0, E[subentity, i] - θ[subentity, i])
        G_j = gap at target = max(0, θ[subentity, j] - E[subentity, j])

    Interpretation:
        High when target has large gap and source has modest slack.
        Drives gap-filling behavior.

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object

    Returns:
        Homeostasis hunger score [0, 1]
    """
    epsilon = 1e-9

    # Compute slack at source: excess energy above threshold
    E_i = subentity.get_energy(source_i)
    theta_i = subentity.get_threshold(source_i)
    S_i = max(0.0, E_i - theta_i)

    # Compute gap at target: deficit below threshold
    E_j = subentity.get_energy(target_j)
    theta_j = subentity.get_threshold(target_j)
    G_j = max(0.0, theta_j - E_j)

    # Homeostasis score: gap-filling potential
    # High when target has large gap, regardless of source slack
    # Normalized by total energy context (S_i + G_j)
    score = G_j / (S_i + G_j + epsilon)

    return score


def hunger_goal(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph,
    goal_embedding: np.ndarray
) -> float:
    """
    Goal hunger: semantic similarity to goal.

    Formula: ν_goal = max(0, cos(E_j, E_goal))

    Where:
        E_j = embedding of target node
        E_goal = current goal embedding

    Interpretation:
        High when target is semantically close to goal.
        Drives goal-directed traversal.

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object
        goal_embedding: Current goal vector (768-dim)

    Returns:
        Goal hunger score [0, 1]
    """
    # Get target node embedding
    if target_j not in graph.nodes:
        return 0.0

    node_data = graph.nodes[target_j]
    if 'embedding' not in node_data:
        return 0.0

    E_j = node_data['embedding']

    # Compute cosine similarity: cos(θ) = (a·b) / (||a|| ||b||)
    norm_goal = np.linalg.norm(goal_embedding)
    norm_node = np.linalg.norm(E_j)

    if norm_goal < 1e-9 or norm_node < 1e-9:
        return 0.0  # Degenerate case

    cos_sim = np.dot(E_j, goal_embedding) / (norm_node * norm_goal)
    cos_sim = np.clip(cos_sim, -1.0, 1.0)  # Numerical stability

    # Positive similarity only (negative = opposite direction)
    score = max(0.0, cos_sim)

    return score


def hunger_completeness(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph
) -> float:
    """
    Completeness hunger: semantic diversity seeking.

    Formula: ν_completeness = (1 - cos(E_j, centroid))

    Where:
        centroid = subentity.centroid.centroid (current extent centroid)
        E_j = embedding of target node

    Interpretation:
        High when target is semantically distant from current extent.
        Drives exploration beyond current semantic cluster.

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object

    Returns:
        Completeness hunger score [0, 1]
    """
    # Get target node embedding
    if target_j not in graph.nodes:
        return 0.0

    node_data = graph.nodes[target_j]
    if 'embedding' not in node_data:
        return 0.0

    target_embedding = node_data['embedding']

    # Check if subentity has centroid tracker
    if not hasattr(subentity, 'centroid'):
        return 0.5  # Neutral if no centroid tracker

    # Distance from target to current extent centroid
    distance = subentity.centroid.distance_to(target_embedding)

    # Normalize to [0, 1] range
    # distance_to returns [0, 2] where 0=identical, 1=orthogonal, 2=opposite
    # We want completeness to be high for distant nodes, so we scale to [0, 1]
    normalized_distance = min(distance, 1.0)  # Cap at 1.0 for opposite vectors

    return normalized_distance


def hunger_ease(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph
) -> float:
    """
    Ease hunger: structural weight preference.

    Formula: ν_ease = w_ij / max(w_ik for k in neighbors)

    Where:
        w_ij = link weight from i to j
        neighbors = out_edges(i)

    Interpretation:
        High when edge is well-traveled (high weight).
        Drives habitual traversal (complementary to novelty-seeking).

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object

    Returns:
        Ease hunger score [0, 1]
    """
    epsilon = 1e-9

    # Get weight of edge i → j
    edge_data = graph.get_edge_data(source_i, target_j)
    if edge_data is None or 'weight' not in edge_data:
        return 0.0

    w_ij = edge_data['weight']

    # Get all outgoing edge weights from source_i
    if source_i not in graph:
        return 0.0

    neighbor_weights = []
    for neighbor in graph.neighbors(source_i):
        neighbor_edge = graph.get_edge_data(source_i, neighbor)
        if neighbor_edge and 'weight' in neighbor_edge:
            neighbor_weights.append(neighbor_edge['weight'])

    if not neighbor_weights:
        return 0.0

    max_weight = max(neighbor_weights)

    # Normalize by local maximum weight
    # High when this edge is the strongest outgoing edge (habitual path)
    score = w_ij / (max_weight + epsilon)

    return score


def hunger_idsubentity(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph
) -> float:
    """
    Idsubentity hunger: coherence around center.

    Formula: ν_idsubentity = max(0, cos(E_j, E_idsubentity))

    Where:
        E_idsubentity = subentity's idsubentity embedding (EMA of explored nodes)
        E_j = embedding of target node

    Interpretation:
        High when target is semantically close to subentity's idsubentity.
        Drives coherent pattern formation.

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object

    Returns:
        Idsubentity hunger score [0, 1]
    """
    # Get target node embedding
    if target_j not in graph.nodes:
        return 0.0

    node_data = graph.nodes[target_j]
    if 'embedding' not in node_data:
        return 0.0

    target_embedding = node_data['embedding']

    # Check if subentity has idsubentity tracker
    if not hasattr(subentity, 'idsubentity'):
        return 0.5  # Neutral if no idsubentity tracker

    # Coherence with idsubentity
    coherence = subentity.idsubentity.coherence_with(target_embedding)

    return coherence


def hunger_complementarity(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph
) -> float:
    """
    Complementarity hunger: emotional balance seeking.

    Formula: ν_complementarity = dot(target_affect, -extent_affect_centroid)

    Where:
        extent_affect_centroid = mean(affect_vector) across extent nodes
        target_affect = affect vector of target node

    Interpretation:
        High when target has opposite affect from extent centroid.
        Drives emotional regulation (anxious extent seeks calm).

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object

    Returns:
        Complementarity hunger score [0, 1]
    """
    # Check if subentity has extent
    if len(subentity.extent) == 0:
        return 0.0

    # Compute affect centroid of current extent
    extent_affects = []
    for node_id in subentity.extent:
        node_data = graph.nodes[node_id]
        description = node_data.get('description', '')
        affect = AffectVector.extract_affect(description)
        extent_affects.append(affect)

    if len(extent_affects) == 0:
        return 0.0

    affect_centroid = np.mean(extent_affects, axis=0)

    # Target node's affect
    target_data = graph.nodes[target_j]
    target_description = target_data.get('description', '')
    target_affect = AffectVector.extract_affect(target_description)

    # Complementarity = dot product with OPPOSITE of centroid
    # Normalize to [0, 1]
    complementarity = np.dot(target_affect, -affect_centroid)

    # Map from [-2, 2] to [0, 1]
    complementarity_normalized = (complementarity + 2.0) / 4.0

    return np.clip(complementarity_normalized, 0.0, 1.0)


def hunger_integration(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph,
    all_active_entities: List[SubEntity] = None
) -> float:
    """
    Integration hunger: merge-seeking when weak.

    Formula: ν_integration = size_ratio × max(0, semantic_sim)

    Where:
        size_ratio = E_others / E_self at target node
        semantic_sim = cos(entity_centroid, target_embedding)

    Interpretation:
        High when target has strong energy from other subentities
        AND target is semantically related to this subentity.
        Drives coalition formation.

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object
        all_active_entities: List of all active subentities (for computing E_others)

    Returns:
        Integration hunger score [0, 1]
    """
    epsilon = 1e-9

    # If no other subentities provided, integration hunger is zero
    if all_active_entities is None or len(all_active_entities) <= 1:
        return 0.0

    # 1. Energy at target from THIS subentity
    E_self = subentity.get_energy(target_j)

    # 2. Energy at target from OTHER subentities
    E_others = 0.0
    for other_entity in all_active_entities:
        if other_entity.id != subentity.id:
            E_others += other_entity.get_energy(target_j)

    # 3. Size ratio (field strength)
    size_ratio = E_others / (E_self + epsilon)

    # Clip to reasonable range (0-10x)
    size_ratio = min(size_ratio, 10.0)

    # 4. Semantic similarity between subentity centroid and target node
    if not hasattr(subentity, 'centroid'):
        semantic_sim = 0.5  # Neutral if no centroid
    else:
        if target_j not in graph.nodes:
            return 0.0

        node_data = graph.nodes[target_j]
        if 'embedding' not in node_data:
            return 0.0

        target_embedding = node_data['embedding']
        entity_centroid = subentity.centroid.centroid

        # Cosine similarity
        norm_centroid = np.linalg.norm(entity_centroid)
        if norm_centroid < epsilon:
            semantic_sim = 0.5  # Neutral if no centroid formed yet
        else:
            semantic_sim = np.dot(entity_centroid, target_embedding)

    # 5. Integration hunger ONLY when semantically related
    # Gated by similarity: negative similarity -> zero integration pull
    ν_integration = size_ratio * max(0.0, semantic_sim)

    # Normalize to roughly [0, 1] range (size_ratio is 0-10, semantic_sim is 0-1)
    # So product is 0-10, we scale down by dividing by 10
    ν_integration = ν_integration / 10.0

    return min(ν_integration, 1.0)


# --- Surprise Gate Construction ---

def compute_hunger_scores(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph,
    goal_embedding: np.ndarray,
    global_quantiles: Dict[str, float],
    all_active_entities: List[SubEntity] = None
) -> Dict[str, float]:
    """
    Compute raw hunger scores for edge i→j.

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object
        goal_embedding: Current goal vector
        global_quantiles: Size distribution quantiles
        all_active_entities: All active subentities (for integration hunger)

    Returns:
        Dict[hunger_name -> raw_score]
    """
    # Full 7-hunger system (Phase 1 complete specification)
    scores = {
        'homeostasis': hunger_homeostasis(subentity, source_i, target_j, graph),
        'goal': hunger_goal(subentity, source_i, target_j, graph, goal_embedding),
        'ease': hunger_ease(subentity, source_i, target_j, graph),
        'completeness': hunger_completeness(subentity, source_i, target_j, graph),
        'idsubentity': hunger_idsubentity(subentity, source_i, target_j, graph),
        'complementarity': hunger_complementarity(subentity, source_i, target_j, graph),
        'integration': hunger_integration(subentity, source_i, target_j, graph, all_active_entities),
    }

    return scores


def compute_surprise_gates(
    subentity: SubEntity,
    hunger_scores: Dict[str, float]
) -> Dict[str, float]:
    """
    Compute surprise-based gates from hunger scores.

    Algorithm:
        1. For each hunger H:
            a. z_H = (s_H - μ_H) / (σ_H + ε)  # Standardize
            b. δ_H = max(0, z_H)               # Positive surprise only
        2. Normalize gates: g_H = δ_H / (Σ δ_H' + ε)

    Args:
        subentity: Sub-entity with hunger_baselines (μ, σ)
        hunger_scores: Raw hunger scores for current edge

    Returns:
        Dict[hunger_name -> gate_weight]
        where Σ gate_weights = 1.0

    Zero-constants: Baselines (μ, σ) are EMA updated per subentity per hunger
    """
    epsilon = 1e-9
    gates = {}
    positive_surprises = {}

    # Step 1: Compute z-scores and positive surprises for each hunger
    for hunger_name, observed_score in hunger_scores.items():
        # Get baseline for this hunger
        mu, sigma = subentity.hunger_baselines[hunger_name]

        # Compute standardized surprise (z-score)
        z_score = (observed_score - mu) / (sigma + epsilon)

        # Positive surprise only (abnormal need)
        delta = max(0.0, z_score)

        positive_surprises[hunger_name] = delta

        # Update baselines with EMA (learn from this observation)
        update_hunger_baselines(subentity, hunger_name, observed_score)

    # Step 2: Normalize to gate weights
    total_surprise = sum(positive_surprises.values()) + epsilon

    for hunger_name, delta in positive_surprises.items():
        gates[hunger_name] = delta / total_surprise

    return gates


def composite_valence(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph,
    goal_embedding: np.ndarray,
    global_quantiles: Dict[str, float] = None,
    all_active_entities: List[SubEntity] = None
) -> float:
    """
    Compute surprise-gated composite valence for edge i→j.

    Formula: V_ij = Σ_H (g_H × ν_H(i→j))

    Where:
        g_H = surprise gate for hunger H (with size-ratio modulation for integration)
        ν_H(i→j) = hunger score for edge i→j

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object
        goal_embedding: Current goal vector
        global_quantiles: Size distribution quantiles (optional)
        all_active_entities: All active subentities (for integration hunger)

    Returns:
        Composite valence score V_ij (unbounded, typically [0, 1])

    Zero-constants:
        - Hunger scores adapt to graph structure
        - Gates self-calibrate from experience
        - No fixed hunger weights
        - Size-ratio modulation learned from merge outcomes (β)
    """
    # Default empty quantiles
    if global_quantiles is None:
        global_quantiles = {}

    # Step 1: Compute raw hunger scores for this edge
    hunger_scores = compute_hunger_scores(
        subentity, source_i, target_j, graph, goal_embedding, global_quantiles, all_active_entities
    )

    # Step 2: Compute surprise gates (also updates baselines via EMA)
    gates = compute_surprise_gates(subentity, hunger_scores)

    # Step 3: Size-ratio modulation for integration gate
    # Apply r^β multiplier to integration gate before weighted sum
    if 'integration' in gates and hasattr(subentity, 'beta_learner'):
        # Compute size ratio at this node
        epsilon = 1e-9
        E_self = subentity.get_energy(target_j)

        if all_active_entities is not None:
            E_others = sum(
                other.get_energy(target_j)
                for other in all_active_entities
                if other.id != subentity.id
            )
            size_ratio = E_others / (E_self + epsilon)
            size_ratio = min(size_ratio, 10.0)  # Clip to reasonable range

            # Get learned beta exponent
            beta = subentity.beta_learner.get_beta()

            # Apply gate multiplier: r^β
            gate_multiplier = size_ratio ** beta
            gate_multiplier = np.clip(gate_multiplier, 0.1, 10.0)

            # Modulate integration gate
            gates['integration'] *= gate_multiplier

            # Renormalize all gates (sum should still be 1.0)
            total_gate = sum(gates.values()) + epsilon
            for hunger_name in gates:
                gates[hunger_name] = gates[hunger_name] / total_gate

    # Step 4: Weighted sum - composite valence
    valence = 0.0
    for hunger_name, raw_score in hunger_scores.items():
        gate_weight = gates[hunger_name]
        valence += gate_weight * raw_score

    return valence


# --- Baseline Tracking ---

def update_hunger_baselines(
    subentity: SubEntity,
    hunger_name: str,
    observed_score: float,
    ema_alpha: float = 0.1
):
    """
    Update EMA baselines (μ, σ) for hunger.

    Args:
        subentity: Sub-entity with hunger_baselines
        hunger_name: Which hunger to update
        observed_score: Current hunger score
        ema_alpha: Smoothing factor (0.1 = 10% new, 90% old)

    Side Effects:
        Modifies subentity.hunger_baselines[hunger_name] in place

    Algorithm:
        μ_new = α × observed + (1-α) × μ_old
        deviation = |observed - μ_new|
        σ_new = α × deviation + (1-α) × σ_old
    """
    # Get current baselines
    mu_old, sigma_old = subentity.hunger_baselines[hunger_name]

    # Update mean with EMA
    mu_new = ema_alpha * observed_score + (1.0 - ema_alpha) * mu_old

    # Compute deviation from new mean
    deviation = abs(observed_score - mu_new)

    # Update std deviation with EMA
    sigma_new = ema_alpha * deviation + (1.0 - ema_alpha) * sigma_old

    # Store updated baselines
    subentity.hunger_baselines[hunger_name] = (mu_new, sigma_new)


## <<< END orchestration/mechanisms/valence.py
---

## >>> BEGIN orchestration/core/graph.py
<!-- mtime: 2025-10-23T02:06:25; size_chars: 9950 -->

"""
Graph container - manages nodes, subentities, and links.

ARCHITECTURAL PRINCIPLE: Container, not controller.

Graph provides:
- Storage (nodes, subentities, links)
- Basic operations (add, get, remove)
- Graph structure maintenance (link references)

Graph does NOT provide:
- Energy dynamics (see mechanisms/diffusion.py)
- Workspace selection (see services/workspace.py)
- Subentity detection (see services/subentity.py)

Author: Felix (Engineer)
Created: 2025-10-19
Architecture: Phase 1 Clean Break + Phase 7 Multi-Scale
"""

from typing import Dict, List, Optional, Set, Union
from datetime import datetime

from .node import Node
from .subentity import Subentity
from .link import Link
from .types import NodeID, EntityID, NodeType, LinkType


class Graph:
    """
    Container for nodes, subentities, and links with basic graph operations.

    This is a CONTAINER, not a CONTROLLER. Complex operations delegate to:
    - orchestration.mechanisms.* (energy dynamics)
    - orchestration.services.* (workspace, clustering, subentity detection)

    Storage:
        nodes: Dict[NodeID, Node] - All nodes by ID
        subentities: Dict[str, Subentity] - All subentities by ID
        links: Dict[LinkID, Link] - All links by ID

    Graph Structure:
        Maintains bidirectional references:
        - Node.outgoing_links / Node.incoming_links
        - Subentity.outgoing_links / Subentity.incoming_links
        - Link.source / Link.target (can be Node or Subentity)
    """

    def __init__(self, graph_id: str, name: str):
        """
        Initialize empty graph.

        Args:
            graph_id: Unique graph identifier (e.g., "citizen_luca")
            name: Human-readable name
        """
        self.id = graph_id
        self.name = name

        # Storage
        self.nodes: Dict[NodeID, Node] = {}
        self.subentities: Dict[str, Subentity] = {}
        self.links: Dict[str, Link] = {}

        # Metadata
        self.created_at = datetime.now()

    # --- Node Operations ---

    def add_node(self, node: Node) -> None:
        """
        Add node to graph.

        Args:
            node: Node to add

        Raises:
            ValueError: If node.id already exists
        """
        if node.id in self.nodes:
            raise ValueError(f"Node {node.id} already exists in graph {self.id}")

        self.nodes[node.id] = node

    def get_node(self, node_id: NodeID) -> Optional[Node]:
        """
        Get node by ID.

        Args:
            node_id: Node identifier

        Returns:
            Node if found, None otherwise
        """
        return self.nodes.get(node_id)

    def remove_node(self, node_id: NodeID) -> None:
        """
        Remove node and all connected links.

        Args:
            node_id: Node identifier
        """
        node = self.nodes.get(node_id)
        if not node:
            return

        # Remove all connected links
        for link in list(node.outgoing_links):
            self.remove_link(link.id)
        for link in list(node.incoming_links):
            self.remove_link(link.id)

        # Remove node
        del self.nodes[node_id]

    def get_nodes_by_type(self, node_type: NodeType) -> List[Node]:
        """
        Get all nodes of given type.

        Args:
            node_type: Type to filter by

        Returns:
            List of nodes with matching type
        """
        return [n for n in self.nodes.values() if n.node_type == node_type]

    # --- Subentity Operations ---

    def add_entity(self, subentity: Subentity) -> None:
        """
        Add subentity to graph.

        Args:
            subentity: Subentity to add

        Raises:
            ValueError: If subentity.id already exists
        """
        if subentity.id in self.subentities:
            raise ValueError(f"Subentity {subentity.id} already exists in graph {self.id}")

        self.subentities[subentity.id] = subentity

    def get_entity(self, entity_id: str) -> Optional[Subentity]:
        """
        Get subentity by ID.

        Args:
            entity_id: Subentity identifier

        Returns:
            Subentity if found, None otherwise
        """
        return self.subentities.get(entity_id)

    def remove_entity(self, entity_id: str) -> None:
        """
        Remove subentity and all connected links.

        Args:
            entity_id: Subentity identifier
        """
        subentity = self.subentities.get(entity_id)
        if not subentity:
            return

        # Remove all connected links
        for link in list(subentity.outgoing_links):
            self.remove_link(link.id)
        for link in list(subentity.incoming_links):
            self.remove_link(link.id)

        # Remove subentity
        del self.subentities[entity_id]

    def get_entities_by_kind(self, entity_kind: str) -> List[Subentity]:
        """
        Get all subentities of given kind.

        Args:
            entity_kind: Kind to filter by ("functional" or "semantic")

        Returns:
            List of subentities with matching kind
        """
        return [e for e in self.subentities.values() if e.entity_kind == entity_kind]

    def get_active_entities(self) -> List[Subentity]:
        """
        Get all subentities currently active (energy >= threshold).

        Returns:
            List of active subentities
        """
        return [e for e in self.subentities.values() if e.is_active()]

    # --- Link Operations ---

    def add_link(self, link: Link) -> None:
        """
        Add link to graph and update node/subentity references.

        Supports:
        - Node -> Node links (ENABLES, BLOCKS, etc.)
        - Node -> Subentity links (BELONGS_TO)
        - Subentity -> Subentity links (RELATES_TO)

        Args:
            link: Link to add

        Raises:
            ValueError: If link.id already exists or source/target not found
        """
        if link.id in self.links:
            raise ValueError(f"Link {link.id} already exists in graph {self.id}")

        # Try to find source in nodes, then subentities
        source: Union[Node, Subentity, None] = self.get_node(link.source_id)
        if not source:
            source = self.get_entity(link.source_id)

        # Try to find target in nodes, then subentities
        target: Union[Node, Subentity, None] = self.get_node(link.target_id)
        if not target:
            target = self.get_entity(link.target_id)

        if not source:
            raise ValueError(f"Source {link.source_id} not found in graph {self.id}")
        if not target:
            raise ValueError(f"Target {link.target_id} not found in graph {self.id}")

        # Update link references
        link.source = source
        link.target = target

        # Update source/target references
        source.outgoing_links.append(link)
        target.incoming_links.append(link)

        # Store link
        self.links[link.id] = link

    def get_link(self, link_id: str) -> Optional[Link]:
        """
        Get link by ID.

        Args:
            link_id: Link identifier

        Returns:
            Link if found, None otherwise
        """
        return self.links.get(link_id)

    def remove_link(self, link_id: str) -> None:
        """
        Remove link and update node references.

        Args:
            link_id: Link identifier
        """
        link = self.links.get(link_id)
        if not link:
            return

        # Remove from node references
        if link.source:
            link.source.outgoing_links.remove(link)
        if link.target:
            link.target.incoming_links.remove(link)

        # Remove link
        del self.links[link_id]

    def get_links_by_type(self, link_type: LinkType) -> List[Link]:
        """
        Get all links of given type.

        Args:
            link_type: Type to filter by

        Returns:
            List of links with matching type
        """
        return [l for l in self.links.values() if l.link_type == link_type]

    # --- Subentity Queries (delegate to mechanisms) ---

    def get_all_active_entities(self) -> Set[EntityID]:
        """
        Get all subentities with non-zero energy anywhere in graph.

        Scans all nodes for active energy.

        Returns:
            Set of subentity IDs with energy > 0

        NOTE: In V2 architecture, nodes use single-energy E (not per-entity buffers).
        Entity differentiation is handled by mechanism layer via membership/selection.
        This method returns empty set as there are no entity-specific energy buffers.
        """
        # V2: No per-entity buffers, entity differentiation via mechanism layer
        return set()

    def get_nodes_with_entity_energy(self, subentity: EntityID, min_energy: float = 0.0) -> List[Node]:
        """
        Get all nodes where subentity has energy above threshold.

        Args:
            subentity: Subentity identifier
            min_energy: Minimum energy threshold (default 0.0)

        Returns:
            List of nodes with subentity energy > min_energy
        """
        return [
            node for node in self.nodes.values()
            if node.get_entity_energy(subentity) > min_energy
        ]

    # --- Statistics ---

    def __len__(self) -> int:
        """Number of nodes in graph."""
        return len(self.nodes)

    def __repr__(self) -> str:
        """Human-readable representation."""
        return (f"Graph(id={self.id!r}, nodes={len(self.nodes)}, "
                f"subentities={len(self.subentities)}, links={len(self.links)})")


## <<< END orchestration/core/graph.py
---

## >>> BEGIN orchestration/core/node.py
<!-- mtime: 2025-10-24T20:02:48; size_chars: 6827 -->

"""
Node data structure - single-energy + bitemporal tracking.

ARCHITECTURAL PRINCIPLE: Core is pure data, delegates to mechanisms.

This Node class is a data container with delegation methods.
All logic lives in orchestration.mechanisms.*

Energy Architecture (V2 - Single Energy):
- Strictly non-negative [0.0, ∞)
- Single scalar E per node (not per-entity)
- Entity differentiation via membership and selection, not energy buffers
- Inhibition via SUPPRESS link type, NOT negative energy

Bitemporal Architecture (V2 - Immutable Versions):
- Reality timeline: valid_at, invalidated_at
- Knowledge timeline: created_at, expired_at
- Version tracking: vid (immutable), supersedes/superseded_by (version chain)

Author: Felix (Engineer)
Created: 2025-10-19
Updated: 2025-10-22 - Added version tracking (vid, supersedes, superseded_by)
Architecture: V2 Stride-Based Diffusion - foundations/diffusion.md
Spec: foundations/bitemporal_tracking.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, TYPE_CHECKING
import uuid

from .types import NodeType, EnergyDict, EntityID

if TYPE_CHECKING:
    from .link import Link


@dataclass
class Node:
    """
    Core node structure with single-energy + bitemporal tracking.

    This is a PURE DATA STRUCTURE. All behavior is delegated to:
    - orchestration.mechanisms.diffusion (stride-based energy transfer)
    - orchestration.mechanisms.decay (exponential forgetting)
    - orchestration.mechanisms.bitemporal (M13)

    Energy Storage (V2 Single-Energy):
        E: float - Activation energy (non-negative scalar)
        theta: float - Activation threshold (adaptive)
        Entity differentiation via membership, not per-entity buffers

    Bitemporal Tracking (M13):
        valid_at: When this node became true in reality
        invalidated_at: When this node became false in reality
        created_at: When we learned about this node
        expired_at: When we learned it's no longer valid

    Graph Structure:
        outgoing_links: Links where this node is source
        incoming_links: Links where this node is target
    """

    # Identity
    id: str  # Logical entity id (stable across versions)
    name: str
    node_type: NodeType
    description: str

    # Version tracking (V2 Bitemporal - Immutable Versions)
    vid: str = field(default_factory=lambda: f"v_{uuid.uuid4().hex[:12]}")  # Version id (immutable)
    supersedes: Optional[str] = None  # Previous version vid
    superseded_by: Optional[str] = None  # Next version vid (set when superseded)

    # Single-energy storage (V2)
    # CRITICAL: Energy is strictly non-negative [0.0, ∞)
    # Inhibition is implemented via SUPPRESS link type, not negative values
    E: float = 0.0  # Activation energy (single scalar, not per-entity)

    # Bitemporal tracking (M13) - Reality timeline
    valid_at: datetime = field(default_factory=datetime.now)
    invalidated_at: Optional[datetime] = None

    # Bitemporal tracking (M13) - Knowledge timeline
    created_at: datetime = field(default_factory=datetime.now)
    expired_at: Optional[datetime] = None

    # Graph structure (populated by Graph container)
    outgoing_links: List['Link'] = field(default_factory=list)
    incoming_links: List['Link'] = field(default_factory=list)

    # Metadata
    properties: Dict[str, any] = field(default_factory=dict)

    # Emotion metadata (separate from activation - affects cost only)
    emotion_vector: Optional[any] = None  # 2D affect vector [valence, arousal]

    # Learning Infrastructure (Phase 1-4: Consciousness Learning)
    # Long-run attractor strength in log space
    log_weight: float = 0.0
    # Entity-specific weight overlays (Priority 4: Entity Context Tracking)
    # Sparse dict: {entity_id: delta}
    # Effective weight for entity E = log_weight + log_weight_overlays.get(E, 0.0)
    # Updated by TRACE marks with entity_context (80% local, 20% global)
    log_weight_overlays: Dict[str, float] = field(default_factory=dict)
    # Exponential moving average of TRACE reinforcement seats
    ema_trace_seats: float = 0.0
    # Exponential moving average of working memory selection frequency
    ema_wm_presence: float = 0.0
    # Exponential moving average of formation quality
    ema_formation_quality: float = 0.0
    # Timestamp of most recent non-zero weight update (for adaptive learning rate)
    last_update_timestamp: Optional[datetime] = None
    # Node scope for cohort grouping (personal/organizational/ecosystem)
    scope: str = "personal"
    # Threshold for activation (adaptive, computed from μ + z·σ)
    theta: float = 0.1

    # --- Energy Methods (V2 Single-Energy) ---

    def is_active(self) -> bool:
        """
        Is this node currently active?

        Per V2 spec (foundations/diffusion.md):
            Active = E >= theta (activation threshold)

        Returns:
            True if E >= theta
        """
        return self.E >= self.theta

    def add_energy(self, delta: float) -> None:
        """
        Add energy delta to this node (used by diffusion staging).

        Args:
            delta: Energy change (can be positive or negative)

        Side effects:
            Updates self.E, clamped to [0.0, ∞)
        """
        self.E = max(0.0, self.E + delta)

    def is_currently_valid(self, at_time: Optional[datetime] = None) -> bool:
        """
        Check if node is valid at given time (reality timeline).

        Delegates to: orchestration.mechanisms.bitemporal.is_currently_valid()

        Args:
            at_time: Time to check (defaults to now)

        Returns:
            True if node valid at given time
        """
        from orchestration.mechanisms.bitemporal import is_currently_valid
        return is_currently_valid(self, at_time)

    def is_currently_known(self, at_time: Optional[datetime] = None) -> bool:
        """
        Check if node is known at given time (knowledge timeline).

        Delegates to: orchestration.mechanisms.bitemporal.is_currently_known()

        Args:
            at_time: Time to check (defaults to now)

        Returns:
            True if node known at given time
        """
        from orchestration.mechanisms.bitemporal import is_currently_known
        return is_currently_known(self, at_time)

    def __repr__(self) -> str:
        """Human-readable representation."""
        return f"Node(id={self.id!r}, name={self.name!r}, type={self.node_type.value}, E={self.E:.3f}, theta={self.theta:.3f})"

    def __hash__(self) -> int:
        """Hash by ID for set/dict usage."""
        return hash(self.id)


## <<< END orchestration/core/node.py
---

## >>> BEGIN orchestration/core/link.py
<!-- mtime: 2025-10-24T20:03:03; size_chars: 5886 -->

"""
Link data structure - bitemporal directed relationships.

ARCHITECTURAL PRINCIPLE: Links ARE consciousness.

Links represent relationships with rich metadata:
- Who created the link (subentity)
- Why it exists (goal, mindstate)
- How strong it is (weight, energy)
- When it was true (bitemporal tracking)
- Version history (immutable versions)

Special Link Types:
- SUPPRESS: Implements inhibition (link-based, not value-based)
- DIFFUSES_TO: Energy flow relationships
- ENABLES/BLOCKS: Causal relationships

Author: Felix (Engineer)
Created: 2025-10-19
Updated: 2025-10-22 - Added version tracking (vid, supersedes, superseded_by)
Architecture: Phase 1 Clean Break - Mechanism 13
Spec: foundations/bitemporal_tracking.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, TYPE_CHECKING
import uuid

from .types import LinkType, EntityID

if TYPE_CHECKING:
    from .node import Node


@dataclass
class Link:
    """
    Directed link between nodes with bitemporal tracking.

    Links carry consciousness metadata:
    - source/target: Which nodes are connected
    - link_type: What kind of relationship
    - subentity: Which subentity created this link
    - weight: Relationship strength
    - energy: Current activation energy

    Bitemporal Tracking (M13):
        valid_at: When this relationship became true in reality
        invalidated_at: When this relationship became false in reality
        created_at: When we learned about this relationship
        expired_at: When we learned it's no longer valid
    """

    # Identity (required fields first)
    id: str  # Logical relationship id (stable across versions)
    source_id: str  # Source node ID
    target_id: str  # Target node ID
    link_type: LinkType
    subentity: EntityID  # Which subentity created/owns this link

    # Version tracking (V2 Bitemporal - Immutable Versions)
    vid: str = field(default_factory=lambda: f"v_{uuid.uuid4().hex[:12]}")  # Version id (immutable)
    supersedes: Optional[str] = None  # Previous version vid
    superseded_by: Optional[str] = None  # Next version vid (set when superseded)

    # Link metadata
    weight: float = 1.0  # Relationship strength (affects diffusion)
    energy: float = 0.0  # Current activation energy on link

    # Bitemporal tracking (M13) - Reality timeline
    valid_at: datetime = field(default_factory=datetime.now)
    invalidated_at: Optional[datetime] = None

    # Bitemporal tracking (M13) - Knowledge timeline
    created_at: datetime = field(default_factory=datetime.now)
    expired_at: Optional[datetime] = None

    # Consciousness metadata (from TRACE format)
    goal: Optional[str] = None  # Why this link exists
    mindstate: Optional[str] = None  # Internal state when forming
    formation_trigger: Optional[str] = None  # How discovered
    confidence: float = 1.0  # Certainty in this relationship

    # Type-specific properties
    properties: Dict[str, any] = field(default_factory=dict)

    # Learning Infrastructure (Phase 1-4: Consciousness Learning)
    # Long-run pathway strength in log space
    log_weight: float = 0.0
    # Entity-specific weight overlays (Priority 4: Entity Context Tracking)
    # Sparse dict: {entity_id: delta}
    # Effective weight for entity E = log_weight + log_weight_overlays.get(E, 0.0)
    # Updated by TRACE marks with entity_context (80% local, 20% global)
    log_weight_overlays: Dict[str, float] = field(default_factory=dict)
    # Exponential moving average of TRACE reinforcement seats for links
    ema_trace_seats: float = 0.0
    # Exponential moving average of gap-closure utility (recruitment effectiveness)
    ema_phi: float = 0.0
    # Causal credit accumulator for forward direction
    precedence_forward: float = 0.0
    # Causal credit accumulator for backward direction
    precedence_backward: float = 0.0
    # Timestamp of last update
    last_update_timestamp: Optional[datetime] = None
    # Link scope for cohort grouping
    scope: str = "organizational"
    # Exponential moving average of formation quality
    ema_formation_quality: float = 0.0

    # Reference to actual nodes (populated by Graph)
    source: Optional['Node'] = field(default=None, repr=False)
    target: Optional['Node'] = field(default=None, repr=False)

    # --- Delegation Methods ---

    def is_currently_valid(self, at_time: Optional[datetime] = None) -> bool:
        """
        Check if link is valid at given time (reality timeline).

        Delegates to: orchestration.mechanisms.bitemporal.is_currently_valid()

        Args:
            at_time: Time to check (defaults to now)

        Returns:
            True if link valid at given time
        """
        from orchestration.mechanisms.bitemporal import is_currently_valid
        return is_currently_valid(self, at_time)

    def is_currently_known(self, at_time: Optional[datetime] = None) -> bool:
        """
        Check if link is known at given time (knowledge timeline).

        Delegates to: orchestration.mechanisms.bitemporal.is_currently_known()

        Args:
            at_time: Time to check (defaults to now)

        Returns:
            True if link known at given time
        """
        from orchestration.mechanisms.bitemporal import is_currently_known
        return is_currently_known(self, at_time)

    def __repr__(self) -> str:
        """Human-readable representation."""
        return (f"Link(id={self.id!r}, {self.source_id} --[{self.link_type.value}]--> "
                f"{self.target_id}, subentity={self.subentity}, weight={self.weight:.2f})")

    def __hash__(self) -> int:
        """Hash by ID for set/dict usage."""
        return hash(self.id)


## <<< END orchestration/core/link.py
---

## >>> BEGIN orchestration/core/events.py
<!-- mtime: 2025-10-24T20:53:41; size_chars: 14843 -->

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
    "tick_frame_v1",  # Entity-first frame telemetry (replaces frame.end)

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


@dataclass
class EntityData:
    """Entity data structure for tick_frame.v1 events (matches frontend Entity interface)."""

    id: str
    name: str
    kind: str = "functional"  # "functional", "identity", etc.
    color: str = "#808080"    # Default gray
    energy: float = 0.0       # Derived aggregate energy
    theta: float = 0.0        # Activation threshold
    active: bool = False      # Above threshold
    members_count: int = 0    # Number of member nodes
    coherence: float = 0.0    # Pattern coherence [0-1]
    # Optional emotion aggregate
    emotion_valence: Optional[float] = None
    emotion_arousal: Optional[float] = None
    emotion_magnitude: Optional[float] = None


@dataclass
class TickFrameV1Event(BaseEvent):
    """
    Entity-first frame telemetry (replaces legacy frame.end).

    Per visualization_patterns.md §2, provides entity-scale observability:
    - Entity aggregates (energy, coherence, emotion)
    - Active members per entity
    - Boundary crossings between entities

    Consumed by EntityMoodMap.tsx for entity bubble visualization.
    """

    event_type: Literal["tick_frame_v1"] = "tick_frame_v1"
    v: str = "1"                          # Schema version
    frame_id: int = 0                     # Tick count
    t_ms: int = 0                         # Unix timestamp (ms)
    tick_duration_ms: float = 0.0         # Frame processing time

    # Entity aggregates (entity-scale view)
    entities: List[EntityData] = None     # All entities with metadata

    # Node counts (atomic-scale summary)
    nodes_active: int = 0                 # Nodes above threshold
    nodes_total: int = 0                  # Total graph nodes

    # Stride budget
    strides_executed: int = 0             # Actual strides this frame
    stride_budget: int = 0                # Max strides per frame

    # Criticality metrics
    rho: float = 1.0                      # Spectral radius estimate
    coherence: float = 0.0                # System coherence [0-1]

    def __post_init__(self):
        if self.entities is None:
            self.entities = []


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
        "tick_frame_v1": TickFrameV1Event,
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


## <<< END orchestration/core/events.py
---

## >>> BEGIN orchestration/core/settings.py
<!-- mtime: 2025-10-23T05:03:33; size_chars: 20093 -->

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


class Settings:
    """Central configuration for all Mind Protocol services."""

    # === Service Ports ===
    WS_HOST: str = os.getenv("WS_HOST", "localhost")
    WS_PORT: int = int(os.getenv("WS_PORT", "8000"))

    API_HOST: str = os.getenv("MP_API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("MP_API_PORT", "8788"))

    # === Database ===
    FALKORDB_HOST: str = os.getenv("FALKORDB_HOST", "localhost")
    FALKORDB_PORT: int = int(os.getenv("FALKORDB_PORT", "6379"))

    # Graph names
    N1_GRAPH_PREFIX: str = "citizen_"  # citizen_luca, citizen_felix, etc
    N2_GRAPH_NAME: str = "mind_protocol_collective_graph"
    N3_GRAPH_NAME: str = "ecosystem_public_graph"

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
        """Get N1 graph name for a citizen."""
        return f"{cls.N1_GRAPH_PREFIX}{citizen_name.lower()}"


# Singleton instance
settings = Settings()


## <<< END orchestration/core/settings.py
---

## >>> BEGIN orchestration/core/telemetry.py
<!-- mtime: 2025-10-23T01:24:24; size_chars: 11177 -->

"""
Telemetry infrastructure for Mind Protocol affective coupling.

Provides event emission with:
- Sampling (configurable rate to reduce overhead)
- Buffering (batch events before emission)
- Validation (ensure events match schemas)
- Feature flag control (enable/disable cleanly)

Author: Felix - 2025-10-23
PR-A: Instrumentation (Telemetry Foundation)
"""

import time
import random
from typing import Dict, List, Any, Optional
from collections import deque
from dataclasses import asdict
import logging

from .settings import settings
from .events import (
    BaseEvent,
    EventType,
    create_event,
    # Affective coupling events
    AffectiveThresholdEvent,
    AffectiveMemoryEvent,
    CoherencePersistenceEvent,
    MultiPatternResponseEvent,
    IdentityMultiplicityEvent,
    ConsolidationEvent,
    DecayResistanceEvent,
    StickinessEvent,
    AffectivePrimingEvent,
    CoherenceMetricEvent,
    CriticalityModeEvent,
)

logger = logging.getLogger(__name__)


class TelemetryBuffer:
    """
    Buffer for high-frequency events with automatic flushing.

    Provides:
    - Size-based flushing (when buffer reaches max size)
    - Time-based flushing (when interval elapsed)
    - Manual flushing (on demand)
    """

    def __init__(
        self,
        max_size: int = 1000,
        flush_interval_s: float = 5.0,
        flush_callback=None
    ):
        """
        Initialize telemetry buffer.

        Args:
            max_size: Maximum events before auto-flush
            flush_interval_s: Seconds between auto-flushes
            flush_callback: Function to call on flush (receives list of events)
        """
        self.max_size = max_size
        self.flush_interval_s = flush_interval_s
        self.flush_callback = flush_callback

        self.buffer: deque = deque(maxlen=max_size)
        self.last_flush_time = time.time()

        # Statistics
        self.total_events_received = 0
        self.total_events_flushed = 0
        self.flush_count = 0

    def add(self, event: BaseEvent):
        """
        Add event to buffer.

        May trigger auto-flush if conditions met.

        Args:
            event: Event to buffer
        """
        self.buffer.append(event)
        self.total_events_received += 1

        # Check flush conditions
        if len(self.buffer) >= self.max_size:
            self.flush(reason="size_limit")
        elif time.time() - self.last_flush_time >= self.flush_interval_s:
            self.flush(reason="time_limit")

    def flush(self, reason: str = "manual"):
        """
        Flush buffered events.

        Args:
            reason: Why flush triggered (size_limit/time_limit/manual)
        """
        if not self.buffer:
            return

        events_to_flush = list(self.buffer)
        self.buffer.clear()

        # Emit events
        if self.flush_callback:
            try:
                self.flush_callback(events_to_flush)
            except Exception as e:
                logger.error(f"[Telemetry] Flush callback error: {e}")

        # Update stats
        self.total_events_flushed += len(events_to_flush)
        self.flush_count += 1
        self.last_flush_time = time.time()

        logger.debug(
            f"[Telemetry] Flushed {len(events_to_flush)} events (reason={reason})"
        )

    def get_stats(self) -> dict:
        """Get buffer statistics."""
        return {
            "total_events_received": self.total_events_received,
            "total_events_flushed": self.total_events_flushed,
            "flush_count": self.flush_count,
            "current_buffer_size": len(self.buffer),
            "max_buffer_size": self.max_size,
        }


class TelemetryEmitter:
    """
    Main telemetry emission system.

    Features:
    - Feature flag control (respects AFFECTIVE_TELEMETRY_ENABLED)
    - Sampling (reduces overhead for high-frequency events)
    - Buffering (batches events before emission)
    - Validation (ensures events match schemas)
    """

    def __init__(self):
        """Initialize telemetry emitter."""
        self.enabled = settings.AFFECTIVE_TELEMETRY_ENABLED
        self.sample_rate = settings.TELEMETRY_SAMPLE_RATE

        # Buffer with callback (currently just logs, will connect to websocket later)
        self.buffer = TelemetryBuffer(
            max_size=settings.TELEMETRY_BUFFER_SIZE,
            flush_interval_s=settings.TELEMETRY_FLUSH_INTERVAL_S,
            flush_callback=self._emit_batch
        )

        # Statistics
        self.event_counts: Dict[EventType, int] = {}
        self.sampled_out_count = 0

        logger.info(
            f"[Telemetry] Initialized "
            f"(enabled={self.enabled}, sample_rate={self.sample_rate})"
        )

    def emit_affective_event(
        self,
        event_type: EventType,
        citizen_id: str = "unknown",
        frame_id: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Emit an affective coupling event.

        Args:
            event_type: Type of event
            citizen_id: Citizen generating event
            frame_id: Current frame ID
            **kwargs: Event-specific fields

        Returns:
            True if event was emitted (or buffered), False if skipped
        """
        # Feature flag check
        if not self.enabled:
            return False

        # Sampling check
        if self.sample_rate < 1.0:
            if random.random() > self.sample_rate:
                self.sampled_out_count += 1
                return False

        # Create event
        try:
            event = create_event(
                event_type=event_type,
                citizen_id=citizen_id,
                frame_id=frame_id,
                **kwargs
            )
        except Exception as e:
            logger.error(f"[Telemetry] Event creation error ({event_type}): {e}")
            return False

        # Validate event
        if not self._validate_event(event):
            logger.warning(f"[Telemetry] Event validation failed: {event_type}")
            return False

        # Buffer event
        self.buffer.add(event)

        # Update counts
        self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1

        return True

    def _validate_event(self, event: BaseEvent) -> bool:
        """
        Validate event matches expected schema.

        Args:
            event: Event to validate

        Returns:
            True if valid
        """
        try:
            # Check required fields exist
            if not event.event_type:
                return False
            if not event.timestamp:
                return False

            # Convert to dict (will raise if invalid)
            event_dict = event.to_dict()

            # Check dict is not empty
            if not event_dict:
                return False

            return True
        except Exception as e:
            logger.error(f"[Telemetry] Validation error: {e}")
            return False

    def _emit_batch(self, events: List[BaseEvent]):
        """
        Emit a batch of events.

        Routes events to affective telemetry buffer for API consumption.

        Args:
            events: Events to emit
        """
        # Import here to avoid circular dependency
        from orchestration.mechanisms.affective_telemetry_buffer import get_affective_buffer

        buffer = get_affective_buffer()

        # Route each event to buffer
        for event in events:
            try:
                event_dict = event.to_dict()
                event_type = event_dict.get("event_type", "unknown")

                # Convert event_type format from "affective_threshold" to "affective.threshold"
                event_type_dotted = event_type.replace("_", ".", 1)

                # Add to buffer (will add timestamp automatically if not present)
                buffer.add_event(event_type_dotted, event_dict)

            except Exception as e:
                logger.error(f"[Telemetry] Failed to route event to buffer: {e}")

        logger.debug(
            f"[Telemetry] Routed {len(events)} events to affective buffer "
            f"(types: {[e.event_type for e in events[:5]]}...)"
        )

    def flush(self):
        """Manually flush buffered events."""
        self.buffer.flush(reason="manual")

    def get_stats(self) -> dict:
        """Get emitter statistics."""
        buffer_stats = self.buffer.get_stats()

        return {
            "enabled": self.enabled,
            "sample_rate": self.sample_rate,
            "event_counts_by_type": self.event_counts,
            "sampled_out_count": self.sampled_out_count,
            "buffer": buffer_stats,
        }


# Singleton instance
_emitter: Optional[TelemetryEmitter] = None


def get_emitter() -> TelemetryEmitter:
    """Get or create singleton telemetry emitter."""
    global _emitter
    if _emitter is None:
        _emitter = TelemetryEmitter()
    return _emitter


# === Convenience Functions ===

def emit_affective_threshold(
    citizen_id: str,
    frame_id: str,
    node_id: str,
    theta_base: float,
    theta_adjusted: float,
    h: float,
    affective_alignment: float,
    emotion_magnitude: float
):
    """Emit affective threshold event (PR-B)."""
    emitter = get_emitter()
    return emitter.emit_affective_event(
        "affective_threshold",
        citizen_id=citizen_id,
        frame_id=frame_id,
        node_id=node_id,
        theta_base=theta_base,
        theta_adjusted=theta_adjusted,
        h=h,
        affective_alignment=affective_alignment,
        emotion_magnitude=emotion_magnitude
    )


def emit_affective_memory(
    citizen_id: str,
    frame_id: str,
    node_id: str,
    m_affect: float,
    emotion_magnitude: float,
    delta_log_w_base: float,
    delta_log_w_amplified: float
):
    """Emit affective memory event (PR-B)."""
    emitter = get_emitter()
    return emitter.emit_affective_event(
        "affective_memory",
        citizen_id=citizen_id,
        frame_id=frame_id,
        node_id=node_id,
        m_affect=m_affect,
        emotion_magnitude=emotion_magnitude,
        delta_log_w_base=delta_log_w_base,
        delta_log_w_amplified=delta_log_w_amplified
    )


def emit_coherence_persistence(
    citizen_id: str,
    frame_id: str,
    entity_id: str,
    coherence_persistence: int,
    lambda_res_effective: float,
    lock_in_risk: bool
):
    """Emit coherence persistence event (PR-B)."""
    emitter = get_emitter()
    return emitter.emit_affective_event(
        "coherence_persistence",
        citizen_id=citizen_id,
        frame_id=frame_id,
        entity_id=entity_id,
        coherence_persistence=coherence_persistence,
        lambda_res_effective=lambda_res_effective,
        lock_in_risk=lock_in_risk
    )


# Additional convenience functions for other event types would go here
# (PR-C, PR-D, PR-E events)


def flush_telemetry():
    """Manually flush all buffered telemetry events."""
    emitter = get_emitter()
    emitter.flush()


def get_telemetry_stats() -> dict:
    """Get telemetry system statistics."""
    emitter = get_emitter()
    return emitter.get_stats()


## <<< END orchestration/core/telemetry.py
---

## >>> BEGIN orchestration/mechanisms/test_tick_speed.py
<!-- mtime: 2025-10-23T00:18:57; size_chars: 11438 -->

"""
Test: Adaptive Tick Speed Regulation

Verifies that:
1. Interval bounded to [min, max]
2. Physics dt capped correctly
3. EMA smoothing reduces oscillation
4. Stimulus triggers fast intervals
5. Dormancy leads to slow intervals
6. Diagnostics provide accurate state

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/runtime_engine/tick_speed.md
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import time
import pytest
from orchestration.mechanisms.tick_speed import AdaptiveTickScheduler, TickSpeedConfig


def test_interval_bounds():
    """Test that interval is clamped to [min, max] bounds (spec §2.1)."""
    print("\n=== Test 1: Interval Bounds ===")

    config = TickSpeedConfig(
        min_interval_ms=100.0,  # 0.1s
        max_interval_s=10.0,    # 10s
        enable_ema=False        # Disable smoothing for clearer bounds
    )
    scheduler = AdaptiveTickScheduler(config)

    # No stimulus yet - should use max_interval
    interval = scheduler.compute_next_interval()
    print(f"  No stimulus: interval={interval:.3f}s (expected {config.max_interval_s}s)")
    assert interval == config.max_interval_s, f"Expected max interval {config.max_interval_s}, got {interval}"

    # Fresh stimulus - should use min_interval
    scheduler.on_stimulus()
    interval = scheduler.compute_next_interval()
    print(f"  Fresh stimulus: interval={interval:.3f}s (expected {config.min_interval_ms/1000}s)")
    assert abs(interval - config.min_interval_ms/1000) < 0.001, \
        f"Expected min interval {config.min_interval_ms/1000}, got {interval}"

    # Wait 5 seconds (mid-range)
    scheduler.last_stimulus_time = time.time() - 5.0
    interval = scheduler.compute_next_interval()
    print(f"  5s after stimulus: interval={interval:.3f}s (expected 5s)")
    assert abs(interval - 5.0) < 0.1, f"Expected ~5s interval, got {interval}"

    # Wait 20 seconds (should clamp to max)
    scheduler.last_stimulus_time = time.time() - 20.0
    interval = scheduler.compute_next_interval()
    print(f"  20s after stimulus: interval={interval:.3f}s (clamped to {config.max_interval_s}s)")
    assert interval == config.max_interval_s, f"Expected clamped to max {config.max_interval_s}, got {interval}"

    print("  ✓ Intervals correctly bounded to [min, max]")


def test_dt_capping():
    """Test that physics dt is capped (spec §2.2)."""
    print("\n=== Test 2: Physics dt Capping ===")

    config = TickSpeedConfig(
        dt_cap_s=5.0,  # Max 5 second physics step
        enable_ema=False
    )
    scheduler = AdaptiveTickScheduler(config)

    # Short interval (under cap)
    dt_used, was_capped = scheduler.compute_dt(interval=2.0)
    print(f"  Short interval (2.0s): dt={dt_used:.3f}s, capped={was_capped}")
    assert dt_used == 2.0, f"Expected dt=2.0, got {dt_used}"
    assert not was_capped, "Short interval should not be capped"

    # Interval at cap
    dt_used, was_capped = scheduler.compute_dt(interval=5.0)
    print(f"  At cap (5.0s): dt={dt_used:.3f}s, capped={was_capped}")
    assert dt_used == 5.0, f"Expected dt=5.0, got {dt_used}"
    assert not was_capped, "Interval at cap should not be marked as capped"

    # Long interval (over cap)
    dt_used, was_capped = scheduler.compute_dt(interval=120.0)
    print(f"  Long interval (120s): dt={dt_used:.3f}s, capped={was_capped}")
    assert dt_used == config.dt_cap_s, f"Expected dt capped to {config.dt_cap_s}, got {dt_used}"
    assert was_capped, "Long interval should be capped"

    print("  ✓ Physics dt correctly capped")


def test_ema_smoothing():
    """Test that EMA smoothing reduces oscillation (spec §2.1, §7)."""
    print("\n=== Test 3: EMA Smoothing ===")

    config = TickSpeedConfig(
        min_interval_ms=100.0,
        max_interval_s=10.0,
        ema_beta=0.3,       # 30% new, 70% old
        enable_ema=True
    )
    scheduler = AdaptiveTickScheduler(config)

    # First stimulus - starts at min
    scheduler.on_stimulus()
    interval_1 = scheduler.compute_next_interval()
    print(f"  Initial (fresh stimulus): {interval_1:.3f}s")

    # Simulate sudden jump to 5 seconds
    scheduler.last_stimulus_time = time.time() - 5.0
    interval_2 = scheduler.compute_next_interval()
    print(f"  After 5s gap (with EMA): {interval_2:.3f}s")

    # EMA should smooth: 0.3 * 5.0 + 0.7 * interval_1
    # interval_1 ≈ 0.1 (min_interval)
    expected_ema = 0.3 * 5.0 + 0.7 * interval_1
    print(f"  Expected EMA: {expected_ema:.3f}s")
    assert abs(interval_2 - expected_ema) < 0.1, \
        f"EMA should be ~{expected_ema:.3f}, got {interval_2:.3f}"

    # Without EMA, should jump directly to 5.0
    scheduler_no_ema = AdaptiveTickScheduler(TickSpeedConfig(
        min_interval_ms=100.0,
        max_interval_s=10.0,
        enable_ema=False
    ))
    scheduler_no_ema.on_stimulus()
    _ = scheduler_no_ema.compute_next_interval()
    scheduler_no_ema.last_stimulus_time = time.time() - 5.0
    interval_no_ema = scheduler_no_ema.compute_next_interval()
    print(f"  Without EMA (direct jump): {interval_no_ema:.3f}s")
    assert abs(interval_no_ema - 5.0) < 0.1, "Without EMA should jump directly to 5.0"

    print("  ✓ EMA smoothing reduces oscillation")


def test_stimulus_tracking():
    """Test that stimulus tracking triggers fast intervals."""
    print("\n=== Test 4: Stimulus Tracking ===")

    config = TickSpeedConfig(
        min_interval_ms=100.0,
        max_interval_s=60.0,
        enable_ema=False
    )
    scheduler = AdaptiveTickScheduler(config)

    # No stimulus - dormant
    interval_dormant = scheduler.compute_next_interval()
    print(f"  Dormant (no stimulus): {interval_dormant:.3f}s")
    assert interval_dormant == config.max_interval_s, "Dormant should use max interval"

    # Stimulus arrives
    scheduler.on_stimulus()
    interval_active = scheduler.compute_next_interval()
    print(f"  Active (fresh stimulus): {interval_active:.3f}s")
    assert abs(interval_active - config.min_interval_ms/1000) < 0.001, \
        "Fresh stimulus should trigger min interval"

    # Multiple rapid stimuli
    for i in range(5):
        scheduler.on_stimulus()
        interval = scheduler.compute_next_interval()
        print(f"  Stimulus #{i+1}: {interval:.3f}s")
        assert abs(interval - config.min_interval_ms/1000) < 0.001, \
            "Rapid stimuli should keep interval at min"

    print("  ✓ Stimulus tracking triggers fast intervals")


def test_dormancy_behavior():
    """Test that long inactivity leads to slow intervals."""
    print("\n=== Test 5: Dormancy Behavior ===")

    config = TickSpeedConfig(
        min_interval_ms=100.0,
        max_interval_s=10.0,
        enable_ema=False
    )
    scheduler = AdaptiveTickScheduler(config)

    # Active phase
    scheduler.on_stimulus()
    interval_active = scheduler.compute_next_interval()
    print(f"  Active phase: {interval_active:.3f}s")

    # Gradual transition to dormancy
    time_points = [0.5, 1.0, 2.0, 5.0, 8.0, 15.0]
    for t in time_points:
        scheduler.last_stimulus_time = time.time() - t
        interval = scheduler.compute_next_interval()
        expected = min(t, config.max_interval_s)
        print(f"  {t:.1f}s after stimulus: {interval:.3f}s (expected {expected:.3f}s)")
        assert abs(interval - expected) < 0.1, \
            f"At {t}s should have interval ~{expected:.3f}, got {interval:.3f}"

    print("  ✓ Dormancy behavior correct")


def test_dt_integration_flow():
    """Test complete flow: interval → dt → physics integration."""
    print("\n=== Test 6: dt Integration Flow ===")

    # Test 6a: Conversation mode (with EMA)
    config_active = TickSpeedConfig(
        min_interval_ms=100.0,
        max_interval_s=60.0,
        dt_cap_s=5.0,
        enable_ema=True,
        ema_beta=0.3
    )
    scheduler_active = AdaptiveTickScheduler(config_active)

    print("  Simulating conversation mode (rapid stimuli, with EMA):")
    for i in range(3):
        scheduler_active.on_stimulus()
        interval = scheduler_active.compute_next_interval()
        dt, capped = scheduler_active.compute_dt(interval)
        print(f"    Tick {i+1}: interval={interval:.3f}s, dt={dt:.3f}s, capped={capped}")
        assert dt <= config_active.dt_cap_s, f"dt should never exceed cap"
        assert dt <= interval, f"dt should never exceed interval"

    # Test 6b: Dormancy mode (no EMA for clearer capping behavior)
    config_dormant = TickSpeedConfig(
        min_interval_ms=100.0,
        max_interval_s=60.0,
        dt_cap_s=5.0,
        enable_ema=False  # Disable for clearer cap testing
    )
    scheduler_dormant = AdaptiveTickScheduler(config_dormant)

    print("  Simulating dormancy mode (no stimuli, no EMA):")
    for i in range(3):
        scheduler_dormant.last_stimulus_time = time.time() - (10.0 * (i+1))  # 10s, 20s, 30s ago
        interval = scheduler_dormant.compute_next_interval()
        dt, capped = scheduler_dormant.compute_dt(interval)
        print(f"    Tick {i+1}: interval={interval:.3f}s, dt={dt:.3f}s, capped={capped}")
        assert dt == config_dormant.dt_cap_s, f"Long intervals should hit dt cap"
        assert capped, f"Long intervals should be marked as capped"

    print("  ✓ dt integration flow correct")


def test_diagnostics():
    """Test diagnostic output for observability."""
    print("\n=== Test 7: Diagnostics ===")

    config = TickSpeedConfig()
    scheduler = AdaptiveTickScheduler(config)

    # Get diagnostics before stimulus
    diag = scheduler.get_diagnostics()
    print(f"  Before stimulus:")
    print(f"    last_stimulus_time: {diag['last_stimulus_time']}")
    print(f"    time_since_stimulus: {diag['time_since_stimulus']}")
    assert diag['last_stimulus_time'] is None, "Should be None before stimulus"
    assert diag['time_since_stimulus'] is None, "Should be None before stimulus"

    # After stimulus
    scheduler.on_stimulus()
    time.sleep(0.1)  # Brief pause
    diag = scheduler.get_diagnostics()
    print(f"  After stimulus:")
    print(f"    last_stimulus_time: {diag['last_stimulus_time']:.3f}")
    print(f"    time_since_stimulus: {diag['time_since_stimulus']:.3f}s")
    assert diag['last_stimulus_time'] is not None, "Should record stimulus time"
    assert diag['time_since_stimulus'] >= 0.1, "Should show time elapsed"
    assert diag['config']['min_interval_ms'] == config.min_interval_ms, "Config should match"

    print("  ✓ Diagnostics provide accurate state")


def run_all_tests():
    """Run all tick speed tests."""
    print("\n" + "=" * 70)
    print("Adaptive Tick Speed Regulation Tests")
    print("=" * 70)

    test_interval_bounds()
    test_dt_capping()
    test_ema_smoothing()
    test_stimulus_tracking()
    test_dormancy_behavior()
    test_dt_integration_flow()
    test_diagnostics()

    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)

    print("\nSummary:")
    print("  - Interval bounds enforced [min, max]")
    print("  - Physics dt capped to prevent blow-ups")
    print("  - EMA smoothing reduces oscillation")
    print("  - Stimulus triggers fast intervals")
    print("  - Dormancy leads to slow intervals")
    print("  - dt integration flow correct")
    print("  - Diagnostics accurate")
    print("  - Ready for production deployment")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()


## <<< END orchestration/mechanisms/test_tick_speed.py
---
