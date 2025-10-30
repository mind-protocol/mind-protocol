"""
Consciousness Engine V2 - Phase 1+2 Architecture

Last modified: 2025-10-25 (Pass B auto-flush integration)
# Hot-reload test: 2025-10-25 21:50 (Atlas Phase 2B validation)

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
import json
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass

import numpy as np

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

# SubEntity Emergence Mechanisms (§4 Emergence Orchestration)
from orchestration.mechanisms.subentity_gap_detector import (
    SubEntityGapDetector, GapDetectionConfig, GapSignal
)
from orchestration.mechanisms.subentity_coalition_assembler import (
    SubEntityCoalitionAssembler, CoalitionAssemblyConfig
)
from orchestration.mechanisms.subentity_emergence_validator import (
    SubEntityEmergenceValidator, EmergenceValidatorConfig, EmergenceDecision
)
from orchestration.mechanisms.subentity_llm_bundle_generator import (
    SubEntityLLMBundleGenerator, LLMBundleGeneratorConfig
)
from orchestration.mechanisms.subentity_membership_weight_learner import (
    SubEntityMembershipWeightLearner, MembershipLearnerConfig
)
from orchestration.mechanisms.vector_weighted_membership import (
    VectorWeightedMembership, VectorWeight, RuntimeContext
)
from orchestration.mechanisms.metastability_tracker import (
    MetastabilityTracker, MetastabilityConfig
)
from orchestration.mechanisms.state_variables import (
    StateVariableComputer, StateVariables
)

# Embedding Service (for Control API fallback)
from orchestration.adapters.search.embedding_service import EmbeddingService

# Observability
from orchestration.libs.metrics import BranchingRatioTracker
from orchestration.libs.websocket_broadcast import ConsciousnessStateBroadcaster
from orchestration.adapters.ws.traversal_event_emitter import TraversalEventEmitter, EmotionDelta

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


class BroadcasterAdapter:
    """Adapter to make ConsciousnessStateBroadcaster compatible with Transport protocol."""
    def __init__(self, broadcaster):
        self.broadcaster = broadcaster

    def emit(self, event_type: str, payload: any) -> None:
        """Emit event via broadcaster if available."""
        if self.broadcaster and self.broadcaster.is_available():
            import asyncio
            try:
                # Try to get the running event loop
                loop = asyncio.get_running_loop()
                # Schedule the coroutine in the running loop
                asyncio.ensure_future(self.broadcaster.broadcast_event(event_type, payload), loop=loop)
            except RuntimeError:
                # No event loop running - create task in default loop
                asyncio.ensure_future(self.broadcaster.broadcast_event(event_type, payload))


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

        # Observability (must initialize before learning mechanisms that need broadcaster)
        self.branching_tracker = BranchingRatioTracker(window_size=10)
        self.broadcaster = (
            ConsciousnessStateBroadcaster(default_citizen_id=self.config.entity_id)
            if self.config.enable_websocket
            else None
        )

        # Telemetry bus for decimated dashboard events (10 Hz batching)
        from orchestration.mechanisms.telemetry_bus import TelemetryBus
        self.telemetry = TelemetryBus(broadcaster=self.broadcaster, fps=10)

        # Dynamic prompt generator - writes CLAUDE_DYNAMIC.md based on entity activation
        from orchestration.libs.dynamic_prompt_generator import DynamicPromptGenerator
        dynamic_path = f"consciousness/citizens/{self.config.entity_id}/CLAUDE_DYNAMIC.md"
        self.dynamic_prompt = DynamicPromptGenerator(
            citizen_id=self.config.entity_id,
            graph_store=self.adapter.graph_store,
            network_id=self.config.network_id,
            file_path=dynamic_path
        )

        # Learning mechanisms (Phase 3+4)
        self.stimulus_injector = StimulusInjector(broadcaster=self.broadcaster)
        self.weight_learner = WeightLearner(alpha=0.1, min_cohort_size=3)

        # P1: Store last WM entity IDs for TraceCapture attribution
        self.last_wm_entity_ids: List[str] = []

        # Stimulus queue (for Phase 1: Activation)
        self.stimulus_queue: List[Dict[str, any]] = []

        # Emergence: Track last stimulus context for gap detection
        self._last_stimulus_id: Optional[str] = None
        self._last_stimulus_text: Optional[str] = None
        self._last_stimulus_channel: Optional[str] = None
        self._last_stimulus_embedding: Optional[np.ndarray] = None
        self._last_retrieved_nodes: List[Dict[str, any]] = []

        # TRACE queue (for Phase 4: Learning)
        self.trace_queue: List[Dict[str, any]] = []

        # Traversal event emitter (for emotion and stride events)
        if self.broadcaster:
            adapter = BroadcasterAdapter(self.broadcaster)
            self.emitter = TraversalEventEmitter(adapter)
        else:
            self.emitter = None

        # Subentity Layer (advanced thresholding)
        from orchestration.mechanisms.subentity_activation import SubEntityCohortTracker
        self.entity_cohort_tracker = SubEntityCohortTracker(window_size=100)

        # SubEntity Context Tracking (Phase 1: Emergent IFS Modes Prerequisites)
        from orchestration.mechanisms.subentity_context_tracking import SubEntityContextTracker
        self.subentity_context_tracker = SubEntityContextTracker(
            alpha_affect=0.1,  # EMA window ~20 frames
            alpha_context=0.05  # EMA window ~40 frames
        )

        # SubEntity Emergence Infrastructure (§4 Emergence Orchestration)
        self.gap_detector = SubEntityGapDetector(GapDetectionConfig())

        # Embedding service - pre-initialize to avoid lazy-init timeout on first stimulus
        # Model loading takes ~2.5s, but subsequent embeds are fast (~0.1s)
        # Pre-init during engine creation prevents first-stimulus timeout
        try:
            from orchestration.adapters.search.embedding_service import EmbeddingService
            self._embedding_service = EmbeddingService(backend='sentence-transformers')
            self._embedding_failures = 0  # Circuit breaker state
            self._embedding_circuit_open_until = 0.0  # Timestamp when circuit closes
            logger.info(f"[{self.config.entity_id}] Embedding service initialized successfully")
        except Exception as e:
            logger.warning(f"[{self.config.entity_id}] Embedding service unavailable: {e}")
            self._embedding_service = None
        self.coalition_assembler = SubEntityCoalitionAssembler(CoalitionAssemblyConfig())
        self.emergence_validator = SubEntityEmergenceValidator(EmergenceValidatorConfig())
        self.bundle_generator = SubEntityLLMBundleGenerator(LLMBundleGeneratorConfig())
        self.membership_learner = SubEntityMembershipWeightLearner(MembershipLearnerConfig())

        # Vector-Weighted Membership (multi-causal membership structure)
        self.vector_membership = VectorWeightedMembership()

        # Metastability Tracking (co-activation pattern monitoring)
        self.metastability_tracker = MetastabilityTracker(MetastabilityConfig())

        # State Variable Computer (arousal, goal_alignment, precision)
        self.state_computer = StateVariableComputer()

        # Metrics
        self.last_tick_time = datetime.now()
        self.tick_duration_ms = 0.0

        # P2.1: Health emitter state tracking (for hysteresis)
        self._last_health_state = None  # "dormant" | "coherent" | "multiplicitous" | "fragmented"
        self._last_frag = 0.0            # Last fragmentation score

        # Transition matrix cache (rebuild only when graph structure changes)
        self._transition_matrix = None
        self._transition_matrix_dirty = True

        # Persistence: Dirty tracking with configurable thresholds
        import os
        import random
        self._persist_enabled = bool(int(os.getenv("MP_PERSIST_ENABLED", "0")))  # Default OFF for Pass A
        self._persist_min_batch = int(os.getenv("MP_PERSIST_MIN_BATCH", "25"))
        self._persist_interval_sec = float(os.getenv("MP_PERSIST_INTERVAL_SEC", "5.0"))
        self._persist_jitter = 0.5  # ±0.5s jitter to avoid herd flushes
        self._dirty_nodes: Set[str] = set()  # Node IDs changed since last persist
        self._last_persisted: Dict[str, tuple[float, float]] = {}  # id -> (E, theta) last written to DB
        self._last_persist_time = time.time()

        # Persistence telemetry (for observability)
        self._persist_batch_sizes: List[int] = []  # Track batch sizes for stats
        self._persist_failures = 0
        self._persist_last_error: Optional[str] = None

        # PR-C: Dashboard event emission state (node.flip, link.flow.summary)
        self._last_E: Dict[str, float] = {}  # node_id -> last E seen (0..100) for dE computation
        self._flip_last_emit = 0.0           # seconds, for 10Hz decimation
        self._flip_fps = 10                  # emit at most 10 Hz
        self._flip_topk = 25                 # number of nodes per emission
        self._flow_last_emit = 0.0           # seconds, for 10Hz decimation

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
        self.loop = asyncio.get_running_loop()  # Capture loop for async injection
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

    def _wm_signature(self, entity_ids: List[str], shares: List[dict]) -> Tuple[frozenset, Tuple[float, ...]]:
        """
        Compute WM signature for on-change detection.

        Creates order-insensitive set signature and order-stable share vector
        to detect when WM composition or token distribution changes significantly.

        Args:
            entity_ids: List of active entity IDs
            shares: List of entity token share dicts (e.g., [{"id": "E1", "tokens": 500}, ...])

        Returns:
            Tuple of (ids_signature, share_vector)
            - ids_signature: frozenset of entity IDs (order-insensitive)
            - share_vector: tuple of token shares in stable order (for drift detection)

        Example:
            >>> sig = self._wm_signature(
            ...     entity_ids=["E.backend", "E.consciousness"],
            ...     shares=[{"id": "E.backend", "tokens": 800}, {"id": "E.consciousness", "tokens": 1200}]
            ... )
            >>> sig
            (frozenset({'E.backend', 'E.consciousness'}), (800.0, 1200.0))

        Author: Atlas (Infrastructure Engineer)
        Implementation: Priority 0 - On-change WM detection
        """
        # Order-insensitive set for set change detection
        ids_sig = frozenset(entity_ids)

        # Stable ordering of shares by entity id to compute drift
        share_map = {s["id"]: float(s.get("tokens", 0.0)) for s in shares}
        vec = tuple(share_map.get(eid, 0.0) for eid in sorted(share_map.keys()))

        return ids_sig, vec

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

        # === Determine tick_reason for autonomy tracking (Phase-A PR-1) ===
        # Check if this tick is stimulus-driven or autonomous
        has_stimulus = len(self.stimulus_queue) > 0
        tick_reason = "stimulus_detected" if has_stimulus else "autonomous_activation"

        # === V2 Event: tick.update (Phase-A PR-1) ===
        # Emit at start of each tick to track autonomy vs stimulus-driven behavior
        if self.broadcaster and self.broadcaster.is_available():
            await self.broadcaster.broadcast_event("tick.update", {
                "v": "2",
                "frame_id": self.tick_count,
                "tick_reason": tick_reason,
                "interval_ms": self.config.tick_interval_ms,
                "has_stimulus": has_stimulus,
                "stimulus_queue_length": len(self.stimulus_queue),
                "t_ms": int(time.time() * 1000),
                "context": {
                    "entity_id": subentity,
                    "tick_count": self.tick_count
                }
            })

        # DEBUG CHECKPOINT D: Track subentities at tick start (every 100th tick to avoid spam)
        if self.tick_count % 100 == 0:
            entity_count = len(self.graph.subentities) if self.graph.subentities else 0
            if entity_count == 0:
                logger.error(f"[tick] CHECKPOINT D: {subentity} tick {self.tick_count}: graph.subentities is EMPTY!")
            else:
                logger.info(f"[tick] CHECKPOINT D: {subentity} tick {self.tick_count}: graph.subentities has {entity_count} items")

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
                "entity_index": entity_index,  # SubEntity snapshot for viz
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
        # Process incoming stimuli from queue (NEVER discard - always attempt injection)
        while self.stimulus_queue:
            stimulus = self.stimulus_queue.pop(0)

            # Extract stimulus data
            embedding = stimulus.get('embedding')
            text = stimulus.get('text', '')
            source_type = stimulus.get('source_type', 'user_message')
            metadata = stimulus.get('metadata', {})
            severity = stimulus.get('severity', 0.3)
            economy_info = metadata.get('economy', {}) if isinstance(metadata, dict) else {}
            economy_multiplier = float(economy_info.get('throttle', 1.0) or 1.0)

            # Track channel for SubEntity context distribution
            self._last_stimulus_channel = source_type

            # Track stimulus for forged identity generation (Phase 3A)
            self._last_stimulus_text = text
            self._last_stimulus_id = metadata.get('stimulus_id', f"stim_{self.tick_count}")

            # Try to ensure embedding if Control API provided none
            injection_path = "vector"  # Default assumption
            if embedding is None:
                embedding = await self._ensure_embedding(text)
                if embedding is None:
                    # Embedder unavailable/timeout - use best-effort fallback
                    injection_path = "best_effort"
                    logger.debug(f"[Stimulus] No embedding available, using best-effort candidate selection")

            # Select candidate nodes for injection
            matches = []
            if injection_path == "vector" and embedding is not None:
                # Vector path: semantic similarity (simplified - full vector search would use semantic_search module)
                for node in self.graph.nodes.values():
                    similarity = 0.5  # Placeholder - would compute cosine similarity with node embeddings
                    match = create_match(
                        item_id=node.id,
                        item_type='node',
                        similarity=similarity,
                        current_energy=node.E,
                        threshold=node.theta
                    )
                    matches.append(match)
            else:
                # Best-effort path: attribution → keyword → small seed
                # Step 1: Try attribution-targeted candidates (if metadata indicates primary entities)
                attribution = metadata.get('attribution', {})
                if attribution and attribution.get('primary_entities'):
                    # TODO: Implement retrieve_entity_members() when entity routing is available
                    pass

                # Step 2: Keyword-based candidates (simple name/description contains)
                if not matches:
                    keywords = text.lower().split()[:5]  # First 5 words as keywords
                    for node in self.graph.nodes.values():
                        node_text = f"{node.name} {node.description}".lower()
                        relevance = sum(1 for kw in keywords if kw in node_text) / max(len(keywords), 1)
                        if relevance > 0:
                            matches.append(create_match(
                                item_id=node.id,
                                item_type='node',
                                similarity=relevance * 0.3,  # Scale to similarity range
                                current_energy=node.E,
                                threshold=node.theta
                            ))

                # Step 3: Small uniform seed if still no candidates (bounded to prevent flooding)
                if not matches:
                    seed_limit = min(50, len(self.graph.nodes))
                    seed_nodes = list(self.graph.nodes.values())[:seed_limit]
                    for node in seed_nodes:
                        matches.append(create_match(
                            item_id=node.id,
                            item_type='node',
                            similarity=0.15,  # Minimal base similarity for seed
                            current_energy=node.E,
                            threshold=node.theta
                        ))

                # Budget floor for best-effort to prevent starvation during embedder outage
                if injection_path == "best_effort" and matches:
                    logger.debug(f"[Stimulus] Best-effort: {len(matches)} candidates selected via keyword/seed")

            # Track stimulus context for gap detection
            self._last_stimulus_embedding = embedding
            # Enrich matches with full node data for gap analysis
            self._last_retrieved_nodes = []
            for match in matches[:20]:  # Keep top 20 for gap analysis
                node = self.graph.get_node(match.item_id)
                if node:
                    node_dict = {
                        'id': node.id,
                        'type': getattr(node, 'type', None),
                        'labels': getattr(node, 'labels', []),
                        'embedding': getattr(node, 'embedding', None),
                        'similarity': match.similarity,
                        'energy': match.current_energy
                    }
                    self._last_retrieved_nodes.append(node_dict)

            # Inject energy using stimulus injector
            if matches:
                result = self.stimulus_injector.inject(
                    stimulus_embedding=embedding if injection_path == "vector" else None,
                    matches=matches,
                    source_type=source_type,
                    economy_multiplier=economy_multiplier
                )

                # Apply injections to nodes (dual-write to E and energy_runtime)
                for injection in result.injections:
                    node = self.graph.get_node(injection['item_id'])
                    if node:
                        delta = injection['delta_energy']
                        # Update latent energy (persisted to DB)
                        node.E = max(0.0, min(100.0, node.E + delta))
                        # Update runtime energy (used by diffusion/decay/flip tracking)
                        node.energy_runtime = max(0.0, min(100.0, node.energy_runtime + delta))
                        # Pass B: Mark node dirty after energy change
                        if self._persist_enabled:
                            self._mark_node_dirty_if_changed(injection['item_id'])

                # Emit telemetry for injection observability
                if self.broadcaster and self.broadcaster.is_available():
                    await self.broadcaster.broadcast_event("stimulus.injection.debug", {
                        "v": "2",
                        "frame_id": self.tick_count,
                        "path": injection_path,
                        "kept_count": result.items_injected,
                        "total_energy": round(result.total_energy_injected, 4),
                        "lam": getattr(result, 'lambda_param', None),
                        "B_top": getattr(result, 'B_top', None),
                        "B_amp": getattr(result, 'B_amp', None),
                        "t_ms": int(time.time() * 1000),
                        "economy_multiplier": economy_multiplier,
                    })

                logger.debug(
                    f"[Phase 1] Stimulus injection ({injection_path}): {result.total_energy_injected:.2f} energy "
                    f"into {result.items_injected} nodes"
                )
            else:
                logger.warning(f"[Stimulus] No candidates found for injection - stimulus dropped")

        # Compute adaptive thresholds and activation masks
        # NOTE: Using TOTAL energy per spec (subentity = any active node)
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
                from orchestration.mechanisms.subentity_activation import learn_relates_to_from_boundary_stride
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
                    logger.debug(f"[{self.config.entity_id}] Executing strides: active_nodes={len(self.diffusion_rt.active)}, broadcaster_available={self.broadcaster.is_available() if self.broadcaster else False}")
                    strides_executed = execute_stride_step(
                        self.graph,
                        self.diffusion_rt,
                        alpha_tick=alpha_tick,
                        dt=dt,
                        sample_rate=0.1,  # 10% emission - prevents websocket overload
                        broadcaster=self.broadcaster,
                        enable_link_emotion=True,
                        current_entity_id=next_entity.id if next_entity else None,
                        emitter=self.emitter
                    )
                    logger.debug(f"[{self.config.entity_id}] Strides executed: {strides_executed}")
                else:
                    # No active entities - fall back to atomic
                    from orchestration.mechanisms.diffusion_runtime import execute_stride_step
                    strides_executed = execute_stride_step(
                        self.graph,
                        self.diffusion_rt,
                        alpha_tick=alpha_tick,
                        dt=dt,
                        sample_rate=0.1,  # 10% emission - prevents websocket overload
                        broadcaster=self.broadcaster,
                        enable_link_emotion=True,
                        emitter=self.emitter
                    )
            else:
                # Two-scale disabled or no subentities - use atomic strides only
                from orchestration.mechanisms.diffusion_runtime import execute_stride_step
                strides_executed = execute_stride_step(
                    self.graph,
                    self.diffusion_rt,
                    alpha_tick=alpha_tick,
                    dt=dt,
                    sample_rate=0.3,  # 30% emission - balance observability vs performance
                    broadcaster=self.broadcaster,
                    enable_link_emotion=True,
                    emitter=self.emitter
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

            # === PR-C: Emit link.flow.summary (top 200 flows at 10Hz) ===
            now = time.time()
            if now - self._flow_last_emit >= 1.0 / self._flip_fps:  # Same 10Hz as flip
                # Get per-link flows from diffusion runtime
                link_flows = getattr(self.diffusion_rt, '_frame_link_flow', {})

                # Emit if we have flows and broadcaster is available
                if link_flows and self.broadcaster and self.broadcaster.is_available():
                    # Sort by absolute flow, cap at 200
                    sorted_flows = sorted(
                        link_flows.items(),
                        key=lambda x: abs(x[1]),
                        reverse=True
                    )[:200]

                    await self.broadcaster.broadcast_event("link.flow.summary", {
                        "v": "2",
                        "frame_id": self.tick_count,
                        "citizen_id": self.config.entity_id,
                        "flows": [
                            {"link_id": link_id, "flow": round(flow, 4)}
                            for (link_id, flow) in sorted_flows
                        ]
                    })

                # Always clear accumulator at decimation boundary (whether we broadcast or not)
                self.diffusion_rt._frame_link_flow.clear()
                self._flow_last_emit = now

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

            # === Hook 1: Gap Detection (Emergence Orchestration) ===
            # Detect gaps after staged ΔE but before apply
            if (self._last_stimulus_id is not None and
                self._last_stimulus_embedding is not None and
                self._last_retrieved_nodes):
                try:
                    gaps = self.gap_detector.detect_gaps(
                        stimulus_id=self._last_stimulus_id,
                        stimulus_embedding=self._last_stimulus_embedding,
                        retrieved_nodes=self._last_retrieved_nodes,
                        graph_context={'citizen_id': self.config.entity_id}
                    )

                    # Emit emergence.gap.detected events (v1 schema)
                    if gaps and self.broadcaster and self.broadcaster.is_available():
                        for gap in gaps:
                            gap_event = {
                                "topic": "emergence.gap.detected",
                                "ts": datetime.utcnow().isoformat() + "Z",
                                "id": f"evt_gap_{self.tick_count}_{gap.gap_type.value}_{hash(gap.stimulus_id) % 10000:04x}",
                                "spec": {"name": "emergence.v1", "rev": "1.0.0"},
                                "provenance": {
                                    "scope": "personal",
                                    "citizen_id": self.config.entity_id,
                                    "frame": self.tick_count,
                                    "emitter": f"engine:{self.config.entity_id}"
                                },
                                "payload": {
                                    "gap_id": f"gap:{self.tick_count}:{hash(gap.stimulus_id) % 10000:04x}",
                                    "gap_type": gap.gap_type.value,
                                    "strength": round(gap.strength, 3),
                                    "locus_nodes": gap.retrieved_node_ids[:10],  # Top 10 for brevity
                                    "features": {
                                        "retrieval_size": len(gap.retrieved_node_ids),
                                        "gap_metrics": gap.gap_metrics  # Fixed: was gap.evidence
                                    }
                                }
                            }
                            await self.broadcaster.broadcast_event("emergence.gap.detected", gap_event)

                    logger.debug(f"[Hook 1] Gap detection: {len(gaps)} gaps detected")

                    # === Hook 2: Coalition Assembly + Validation (Emergence Orchestration) ===
                    # Process each gap: assemble coalition → validate → decide SPAWN/REDIRECT/REJECT
                    for gap in gaps:
                        try:
                            # Step 1: Assemble coalition from gap
                            coalition = self.coalition_assembler.assemble_coalition(
                                gap_signal=gap,
                                graph_accessor=self.graph,
                                stimulus_context={'stimulus_id': gap.stimulus_id}
                            )

                            # Emit emergence.coalition.formed event (if successful)
                            if coalition is not None and self.broadcaster and self.broadcaster.is_available():
                                coalition_event = {
                                    "topic": "emergence.coalition.formed",
                                    "ts": datetime.utcnow().isoformat() + "Z",
                                    "id": f"evt_coalition_{self.tick_count}_{gap.gap_type.value}_{hash(gap.stimulus_id) % 10000:04x}",
                                    "spec": {"name": "emergence.v1", "rev": "1.0.0"},
                                    "provenance": {
                                        "scope": "personal",
                                        "citizen_id": self.config.entity_id,
                                        "frame": self.tick_count,
                                        "emitter": f"engine:{self.config.entity_id}"
                                    },
                                    "payload": {
                                        "gap_id": f"gap:{self.tick_count}:{hash(gap.stimulus_id) % 10000:04x}",
                                        "coalition_size": len(coalition.nodes),
                                        "node_ids": [n.node_id for n in coalition.nodes],
                                        "density": round(coalition.density, 3),
                                        "coherence": round(coalition.coherence, 3)
                                    }
                                }
                                await self.broadcaster.broadcast_event("emergence.coalition.formed", coalition_event)

                            if coalition is None:
                                # Coalition assembly failed (density too low, etc.)
                                logger.debug(f"[Hook 2] Coalition assembly failed for gap {gap.gap_type.value}")

                                # Emit emergence.reject event
                                if self.broadcaster and self.broadcaster.is_available():
                                    reject_event = {
                                        "topic": "emergence.reject",
                                        "ts": datetime.utcnow().isoformat() + "Z",
                                        "id": f"evt_reject_{self.tick_count}_{gap.gap_type.value}_{hash(gap.stimulus_id) % 10000:04x}",
                                        "spec": {"name": "emergence.v1", "rev": "1.0.0"},
                                        "provenance": {
                                            "scope": "personal",
                                            "citizen_id": self.config.entity_id,
                                            "frame": self.tick_count,
                                            "emitter": f"engine:{self.config.entity_id}"
                                        },
                                        "payload": {
                                            "gap_id": f"gap:{self.tick_count}:{hash(gap.stimulus_id) % 10000:04x}",
                                            "reason": "coalition_assembly_failed"
                                        }
                                    }
                                    await self.broadcaster.broadcast_event("emergence.reject", reject_event)
                                continue

                            # Step 2: Validate coalition (engine-side authority)
                            validation_result = self.emergence_validator.validate_emergence(
                                coalition=coalition,
                                graph_accessor=self.graph,
                                existing_subentities=[
                                    {'id': se_id, 'member_ids': list(getattr(se, 'member_ids', set()))}
                                    for se_id, se in self.graph.subentities.items()
                                ]
                            )

                            # Step 3: Handle validation decision
                            if validation_result.decision == EmergenceDecision.REJECT:
                                logger.debug(f"[Hook 2] Emergence rejected: {validation_result.reason}")

                                # Emit emergence.reject event
                                if self.broadcaster and self.broadcaster.is_available():
                                    reject_event = {
                                        "topic": "emergence.reject",
                                        "ts": datetime.utcnow().isoformat() + "Z",
                                        "id": f"evt_reject_{self.tick_count}_{gap.gap_type.value}_{hash(gap.stimulus_id) % 10000:04x}",
                                        "spec": {"name": "emergence.v1", "rev": "1.0.0"},
                                        "provenance": {
                                            "scope": "personal",
                                            "citizen_id": self.config.entity_id,
                                            "frame": self.tick_count,
                                            "emitter": f"engine:{self.config.entity_id}"
                                        },
                                        "payload": {
                                            "gap_id": f"gap:{self.tick_count}:{hash(gap.stimulus_id) % 10000:04x}",
                                            "coalition_size": len(coalition.nodes),
                                            "reason": validation_result.reason
                                        }
                                    }
                                    await self.broadcaster.broadcast_event("emergence.reject", reject_event)

                            elif validation_result.decision == EmergenceDecision.REDIRECT:
                                logger.info(f"[Hook 2] Emergence redirected to {validation_result.redirect_target}")

                                # Emit emergence.redirect event
                                if self.broadcaster and self.broadcaster.is_available():
                                    redirect_event = {
                                        "topic": "emergence.redirect",
                                        "ts": datetime.utcnow().isoformat() + "Z",
                                        "id": f"evt_redirect_{self.tick_count}_{gap.gap_type.value}_{hash(gap.stimulus_id) % 10000:04x}",
                                        "spec": {"name": "emergence.v1", "rev": "1.0.0"},
                                        "provenance": {
                                            "scope": "personal",
                                            "citizen_id": self.config.entity_id,
                                            "frame": self.tick_count,
                                            "emitter": f"engine:{self.config.entity_id}"
                                        },
                                        "payload": {
                                            "gap_id": f"gap:{self.tick_count}:{hash(gap.stimulus_id) % 10000:04x}",
                                            "target_subentity_id": validation_result.redirect_target,
                                            "coalition_size": len(coalition.nodes)
                                        }
                                    }
                                    await self.broadcaster.broadcast_event("emergence.redirect", redirect_event)

                            elif validation_result.decision == EmergenceDecision.SPAWN:
                                logger.info(f"[Hook 2] Emergence SPAWN decision for {len(coalition.nodes)} nodes")

                                # Step 4: Generate identity bundle (LLM explains, doesn't decide)
                                identity_bundle = self.bundle_generator.generate_bundle(
                                    coalition=coalition,
                                    gap_signal=gap,
                                    stimulus_context={'stimulus_id': gap.stimulus_id}
                                )

                                if identity_bundle:
                                    logger.info(f"[Hook 2] Identity bundle generated: {identity_bundle.slug}")

                                # === Step 5: Actually Create SubEntity ===
                                # Generate SubEntity ID BEFORE broadcasting (frontend needs it)
                                from orchestration.core.subentity import Subentity
                                subentity_id = f"subentity_{self.config.entity_id}_{identity_bundle.slug if identity_bundle else 'unnamed'}_{self.tick_count}"

                                # Emit emergence.spawn.completed event with subentity_id
                                # Pass ONLY the data - broadcast_event() will wrap in normative envelope
                                if self.broadcaster and self.broadcaster.is_available():
                                    await self.broadcaster.broadcast_event("emergence.spawn.completed", {
                                        "citizen_id": self.config.entity_id,
                                        "subentity_id": subentity_id,  # Frontend expects this field
                                        "gap_id": f"gap:{self.tick_count}:{hash(gap.stimulus_id) % 10000:04x}",
                                        "coalition_size": len(coalition.nodes),
                                        "node_ids": [n.node_id for n in coalition.nodes],
                                        "density": round(coalition.density, 3),
                                        "coherence": round(coalition.coherence, 3),
                                        "frame": self.tick_count,
                                        "identity": {
                                            "slug": identity_bundle.slug,
                                            "purpose": identity_bundle.purpose,
                                            "intent": identity_bundle.intent,
                                            "emotion": identity_bundle.emotion,
                                            "confidence": round(identity_bundle.confidence, 2)
                                        } if identity_bundle else None
                                    })

                                # Create SubEntity node in graph.subentities with vector-weighted membership
                                try:

                                    # Create SubEntity instance
                                    new_subentity = Subentity(
                                        id=subentity_id,
                                        entity_kind="semantic",  # Emerged from stimulus pattern
                                        role_or_topic=identity_bundle.slug if identity_bundle else "unnamed_pattern",
                                        description=identity_bundle.purpose if identity_bundle else "Emerged pattern",
                                        centroid_embedding=self._last_stimulus_embedding if self._last_stimulus_embedding is not None else None,
                                        energy_runtime=0.0,
                                        threshold_runtime=1.0,
                                        coherence_ema=coalition.coherence,
                                        member_count=len(coalition.nodes),
                                        stability_state="candidate",  # Start as candidate
                                        quality_score=coalition.coherence,
                                        created_from="emergence",
                                        created_by=f"engine:{self.config.entity_id}",
                                        formation_trigger="gap_detected",
                                        confidence=identity_bundle.confidence if identity_bundle else 0.5
                                    )

                                    # Add to graph
                                    if not hasattr(self.graph, 'subentities'):
                                        self.graph.subentities = {}
                                    self.graph.subentities[subentity_id] = new_subentity

                                    # Create vector-weighted MEMBER_OF edges for coalition members
                                    formation_context = f"emergence_{gap.gap_type.value}_{self.tick_count}"
                                    for node_candidate in coalition.nodes:
                                        # Add membership with weak prior (balanced uncertainty)
                                        weak_prior = VectorWeight.weak_prior(formation_context)
                                        self.vector_membership.add_membership(
                                            subentity_id=subentity_id,
                                            node_id=node_candidate.node_id,
                                            weight=weak_prior,
                                            formation_context=formation_context
                                        )

                                    logger.info(f"[Hook 2] SubEntity spawned: {subentity_id} with {len(coalition.nodes)} members")

                                    # Emit graph.delta.node.upsert for new SubEntity
                                    # Pass ONLY the data - broadcast_event() will wrap in normative envelope
                                    if self.broadcaster and self.broadcaster.is_available():
                                        logger.info(f"[Hook 2] Broadcasting graph.delta.node.upsert for {subentity_id}")
                                        await self.broadcaster.broadcast_event("graph.delta.node.upsert", {
                                            "node_id": subentity_id,
                                            "node_type": "SubEntity",
                                            "properties": {
                                                "role_or_topic": new_subentity.role_or_topic,
                                                "description": new_subentity.description,
                                                "entity_kind": new_subentity.entity_kind,
                                                "member_count": new_subentity.member_count,
                                                "coherence": round(new_subentity.coherence_ema, 3)
                                            }
                                        })
                                        logger.info(f"[Hook 2] graph.delta.node.upsert broadcast complete")

                                        # Emit graph.delta.link.upsert for each MEMBER_OF edge
                                        # Pass ONLY the data - broadcast_event() will wrap in normative envelope
                                        logger.info(f"[Hook 2] Broadcasting {len(coalition.nodes)} MEMBER_OF edges")
                                        for node_candidate in coalition.nodes:
                                            weight = self.vector_membership.get_weight(subentity_id, node_candidate.node_id)
                                            await self.broadcaster.broadcast_event("graph.delta.link.upsert", {
                                                "type": "MEMBER_OF",  # Frontend expects "type" not "link_type"
                                                "source": node_candidate.node_id,
                                                "target": subentity_id,
                                                "weight": weight.to_dict() if weight else None
                                            })
                                        logger.info(f"[Hook 2] All MEMBER_OF edges broadcast complete")

                                except Exception as e:
                                    logger.error(f"[Hook 2] SubEntity spawn/broadcast failed: {e}", exc_info=True)

                        except Exception as e:
                            logger.error(f"[Hook 2] Coalition processing failed for gap {gap.gap_type.value}: {e}", exc_info=True)

                except Exception as e:
                    logger.error(f"[Hook 1] Gap detection failed: {e}", exc_info=True)

            # === Step 6: Apply Staged Deltas ===
            # Apply staged deltas atomically
            for node_id, delta in self.diffusion_rt.delta_E.items():
                node = self.graph.nodes.get(node_id)
                if node:
                    node.add_energy(delta)
                    # Pass B: Mark node dirty after diffusion energy change
                    if self._persist_enabled and abs(delta) > 1e-9:
                        self._mark_node_dirty_if_changed(node_id)

            # Clear staged deltas
            self.diffusion_rt.clear_deltas()

            # === PR-C: Emit node.flip (top-K nodes by |dE| at 10Hz) ===
            now = time.time()
            if now - self._flip_last_emit >= 1.0 / self._flip_fps:
                changed = []
                gi = self.graph.nodes  # id -> node (FIXED: node_index -> nodes)
                for nid, node in gi.items():
                    E_now = float(getattr(node, "energy_runtime", 0.0))  # Runtime energy (dynamics)
                    E_prev = self._last_E.get(nid, E_now)
                    dE = E_now - E_prev
                    if dE != 0.0:
                        changed.append((nid, E_prev, E_now, dE))
                    self._last_E[nid] = E_now

                if changed and self.broadcaster and self.broadcaster.is_available():
                    changed.sort(key=lambda x: abs(x[3]), reverse=True)
                    top = changed[:self._flip_topk]
                    await self.broadcaster.broadcast_event("node.flip", {
                        "v": "2",
                        "frame_id": self.tick_count,
                        "citizen_id": self.config.entity_id,
                        "nodes": [
                            {"id": nid, "E": round(E_now, 3), "dE": round(dE, 3)}
                            for (nid, E_prev, E_now, dE) in top
                        ]
                    })
                self._flip_last_emit = now

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

            # Pass B: Mark decayed nodes as dirty
            if self._persist_enabled:
                for node in self.graph.nodes.values():
                    # Decay affects all nodes - mark if energy/threshold changed
                    self._mark_node_dirty_if_changed(node.id)

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

        # === Hook 3: Membership Weight Learning (Emergence Orchestration) ===
        # Observe co-activation patterns post-apply for continuous membership refinement
        if hasattr(self.graph, 'subentities') and len(self.graph.subentities) > 0:
            try:
                # Build frame state for observation
                frame_state = {
                    'subentities': {},
                    'nodes': {}
                }

                # Collect SubEntity state
                for subentity_id, subentity in self.graph.subentities.items():
                    subentity_energy = getattr(subentity, 'energy_runtime', 0.0)
                    # Get member node IDs from vector_membership
                    member_node_ids = self.vector_membership.get_members(subentity_id)
                    frame_state['subentities'][subentity_id] = {
                        'energy': subentity_energy,
                        'member_nodes': member_node_ids
                    }

                # Collect node state
                for node_id, node in self.graph.nodes.items():
                    frame_state['nodes'][node_id] = {
                        'energy': float(getattr(node, 'energy_runtime', 0.0))
                    }

                # Observe frame and get membership adjustment proposals
                adjustments = self.membership_learner.observe_frame(frame_state)

                # Emit membership.updated events for each adjustment
                if adjustments and self.broadcaster and self.broadcaster.is_available():
                    for adjustment in adjustments:
                        membership_event = {
                            "topic": "membership.updated",
                            "ts": datetime.utcnow().isoformat() + "Z",
                            "id": f"evt_membership_{self.tick_count}_{adjustment.subentity_id}_{hash(adjustment.node_id) % 10000:04x}",
                            "spec": {"name": "emergence.v1", "rev": "1.0.0"},
                            "provenance": {
                                "scope": "personal",
                                "citizen_id": self.config.entity_id,
                                "frame": self.tick_count,
                                "emitter": f"engine:{self.config.entity_id}"
                            },
                            "payload": {
                                "subentity_id": adjustment.subentity_id,
                                "node_id": adjustment.node_id,
                                "action": adjustment.action,
                                "reason": adjustment.reason,
                                "current_weight": round(adjustment.current_weight, 3),
                                "proposed_weight": round(adjustment.proposed_weight, 3),
                                "confidence": round(adjustment.confidence, 2)
                            }
                        }
                        await self.broadcaster.broadcast_event("membership.updated", membership_event)

                    logger.debug(f"[Hook 3] Membership learning: {len(adjustments)} adjustments proposed")

                # Apply adjustments to vector_membership weights
                # Updates w_experience dimension based on co-activation observations
                for adjustment in adjustments:
                    if adjustment.action == "admit":
                        # Add new membership with weak prior
                        if not self.vector_membership.has_membership(adjustment.subentity_id, adjustment.node_id):
                            weak_prior = VectorWeight.weak_prior(f"admitted_frame_{self.tick_count}")
                            # Boost w_experience based on co-activation strength
                            weak_prior.w_experience = adjustment.proposed_weight
                            weak_prior.w_total = weak_prior.compute_composite()
                            self.vector_membership.add_membership(
                                subentity_id=adjustment.subentity_id,
                                node_id=adjustment.node_id,
                                weight=weak_prior,
                                formation_context=f"admitted_frame_{self.tick_count}"
                            )
                            logger.debug(f"[Hook 3] Admitted {adjustment.node_id} to {adjustment.subentity_id} (w_experience={adjustment.proposed_weight:.3f})")

                    elif adjustment.action == "prune":
                        # Update w_experience toward proposed weight (decay)
                        current_weight = self.vector_membership.get_weight(adjustment.subentity_id, adjustment.node_id)
                        if current_weight:
                            # Decay w_experience toward proposed weight
                            self.vector_membership.update_dimension_for_member(
                                subentity_id=adjustment.subentity_id,
                                node_id=adjustment.node_id,
                                dimension="experience",
                                new_value=adjustment.proposed_weight
                            )
                            logger.debug(f"[Hook 3] Pruned {adjustment.node_id} from {adjustment.subentity_id} (w_experience={adjustment.proposed_weight:.3f})")

                            # If weight drops below threshold, could remove membership entirely
                            # For now, just decay - removal would need additional logic

                # Emit weight.adjusted event (after all adjustments applied)
                if adjustments and self.broadcaster and self.broadcaster.is_available():
                    weight_event = {
                        "topic": "emergence.weight.adjusted",
                        "ts": datetime.utcnow().isoformat() + "Z",
                        "id": f"evt_weight_{self.tick_count}_{hash(str(adjustments)) % 10000:04x}",
                        "spec": {"name": "emergence.v1", "rev": "1.0.0"},
                        "provenance": {
                            "scope": "personal",
                            "citizen_id": self.config.entity_id,
                            "frame": self.tick_count,
                            "emitter": f"engine:{self.config.entity_id}"
                        },
                        "payload": {
                            "adjustments_count": len(adjustments),
                            "admits": len([a for a in adjustments if a.action == "admit"]),
                            "prunes": len([a for a in adjustments if a.action == "prune"]),
                            "adjustments": [
                                {
                                    "subentity_id": a.subentity_id,
                                    "node_id": a.node_id,
                                    "action": a.action,
                                    "proposed_weight": round(a.proposed_weight, 3)
                                }
                                for a in adjustments[:10]  # Top 10 for brevity
                            ]
                        }
                    }
                    await self.broadcaster.broadcast_event("emergence.weight.adjusted", weight_event)

            except Exception as e:
                logger.error(f"[Hook 3] Membership weight learning failed: {e}", exc_info=True)

        # Note: Step 8 (criticality_control) happens BEFORE diffusion in current implementation
        # This computes α_tick for THIS frame. Spec suggests it should happen after to adjust
        # parameters for NEXT frame, but current approach works as first-order approximation.

        # === Step 8.5: Update SubEntity Activations ===
        # Compute subentity energy from member nodes (spec: subentity_layer.md §2.2)
        # Formula: E_entity = Σ (m̃_iE × max(0, E_i - Θ_i))
        # With advanced thresholding: cohort-based, health modulation, hysteresis
        # With lifecycle management: promotion/dissolution
        entity_activation_metrics = []
        lifecycle_transitions = []
        if hasattr(self.graph, 'subentities') and len(self.graph.subentities) > 0:
            from orchestration.mechanisms.subentity_activation import update_entity_activations

            # === Compute State Variables (arousal, goal_alignment, precision) ===
            # State variables modulate effective weights at runtime
            state_vars = self.state_computer.compute_state_variables(
                graph=self.graph,
                intent=None,  # TODO: Get intent from working memory or goal system
                prediction_error=0.5,  # TODO: Get from predictive coding mechanism
                citizen_id=self.config.entity_id,
                frame_id=self.tick_count
            )

            # Create RuntimeContext from state variables
            runtime_context = RuntimeContext(
                arousal=state_vars.arousal,
                current_goal=None,  # TODO: Intent vector from goal system
                prediction_error_precision=state_vars.precision,
                citizen_id=self.config.entity_id,
                frame_id=self.tick_count
            )

            # Emit state modulation telemetry
            if self.broadcaster and self.broadcaster.is_available():
                await self.broadcaster.broadcast_event("state_modulation.frame", {
                    "v": "2",
                    "frame_id": self.tick_count,
                    "citizen_id": self.config.entity_id,
                    **state_vars.to_dict(),
                    "t_ms": int(time.time() * 1000)
                })

            entity_activation_metrics, lifecycle_transitions = update_entity_activations(
                self.graph,
                global_threshold_mult=threshold_multiplier,
                cohort_tracker=self.entity_cohort_tracker,
                enable_lifecycle=True,
                vector_membership=self.vector_membership,
                runtime_context=runtime_context
            )

            # === V2 Event: subentity.activation (continuous activation state) ===
            if self.broadcaster and self.broadcaster.is_available():
                activations = []
                for entity in self.graph.subentities.values():
                    activations.append({
                        "entity_id": entity.id,
                        "energy": round(entity.energy_runtime, 4),
                        "threshold": round(entity.threshold_runtime, 4),
                        "is_active": entity.is_active(),
                        "member_count": len(entity.get_members()),
                        "active_members": sum(1 for m in entity.get_members() if m.is_active())
                    })

                await self.broadcaster.broadcast_event("subentity.activation", {
                    "v": "2",
                    "frame_id": self.tick_count,
                    "citizen_id": self.config.entity_id,
                    "activations": activations,
                    "t_ms": int(time.time() * 1000)
                })

            # === Metastability Tracking: Co-Activation Pattern Monitoring ===
            # Track persistent co-activation patterns (ephemeral, not stored as entities)
            active_subentities = {
                entity.id for entity in self.graph.subentities.values()
                if entity.is_active()
            }
            activation_scores = {
                entity.id: entity.energy_runtime * getattr(entity, 'recency', 1.0) * getattr(entity, 'emotional_valence', 1.0)
                for entity in self.graph.subentities.values()
            }

            # Observe frame for metastability
            pattern_info = self.metastability_tracker.observe_frame(
                frame_id=self.tick_count,
                active_subentities=active_subentities,
                activation_scores=activation_scores
            )

            # Emit metastable pattern events if detected
            if pattern_info and self.broadcaster and self.broadcaster.is_available():
                await self.broadcaster.broadcast_event("mode.snapshot", {
                    "v": "2",
                    "frame_id": self.tick_count,
                    "citizen_id": self.config.entity_id,
                    **pattern_info,
                    "t_ms": int(time.time() * 1000)
                })

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
                            "entity_id": metrics.subentity_id,
                            "flip_direction": metrics.flip_direction,
                            "energy": round(metrics.energy_after, 4),
                            "threshold": round(metrics.threshold, 4),
                            "activation_level": metrics.activation_level,
                            "member_count": metrics.member_count,
                            "active_members": metrics.active_members,
                            "t_ms": int(time.time() * 1000)
                        })

            logger.debug(
                f"[Step 8.5] SubEntity activation: {len(entity_activation_metrics)} subentities, "
                f"{sum(1 for m in entity_activation_metrics if m.flipped)} flipped"
            )

        # === Step 8.6: Identity Multiplicity Tracking (PR-D) ===
        # Track outcome metrics and assess multiplicity mode (productive vs conflict)
        if (hasattr(self.graph, 'subentities') and len(self.graph.subentities) > 0 and
            settings.IDENTITY_MULTIPLICITY_ENABLED):

            from orchestration.mechanisms.subentity_activation import (
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

        # === Step 8.7: SubEntity Merge Scanning (every 50 ticks) ===
        # Scan for redundant subentities and merge them to maintain differentiation quality
        if (hasattr(self.graph, 'subentities') and len(self.graph.subentities) >= 2 and
            self.tick_count % 50 == 0):

            from orchestration.mechanisms.subentity_merge_split import scan_for_merge_candidates
            from orchestration.libs.subentity_metrics import SubEntityMetrics
            from orchestration.libs.subentity_lifecycle_audit import EntityLifecycleAudit

            try:
                metrics_lib = SubEntityMetrics(self.adapter)
                audit = EntityLifecycleAudit(citizen_id=self.config.entity_id)

                merge_results = scan_for_merge_candidates(
                    graph=self.graph,
                    metrics_lib=metrics_lib,
                    audit=audit,
                    max_per_tick=1,  # Limit to 1 merge per scan for stability
                    q90_threshold=0.7  # S_red > 0.7 required for merge
                )

                if merge_results:
                    successful_merges = [r for r in merge_results if r.success]
                    if successful_merges:
                        logger.info(
                            f"[Step 8.7] SubEntity Merge: {len(successful_merges)} merges executed, "
                            f"{self.graph.subentities and len(self.graph.subentities)} subentities remaining"
                        )
                    else:
                        logger.debug(f"[Step 8.7] SubEntity Merge: {len(merge_results)} attempted, all failed")
            except Exception as e:
                logger.error(f"[Step 8.7] SubEntity Merge scan failed: {e}")

        # === V2 Event: node.flip (detect threshold crossings with top-K decimation) ===
        # NOTE: Single-energy architecture (E >= theta for activation)
        # Decimation: Emit top-K (20) nodes by |ΔE| magnitude for frontend efficiency
        if self.broadcaster and self.broadcaster.is_available():
            flips = []
            for node in self.graph.nodes.values():
                prev_state = previous_states[node.id]
                current_energy = node.E  # Single-energy
                is_now_active = node.is_active()  # E >= theta check

                # Collect flip if activation state changed
                if prev_state['was_active'] != is_now_active:
                    delta_E = abs(current_energy - prev_state['energy'])
                    flips.append({
                        "node_id": node.id,
                        "E_pre": prev_state['energy'],
                        "E_post": current_energy,
                        "theta": node.theta,
                        "delta_E": delta_E
                    })

            # Sort by |ΔE| magnitude descending and emit top-K (20)
            if flips:
                flips_sorted = sorted(flips, key=lambda f: f['delta_E'], reverse=True)
                top_k_flips = flips_sorted[:20]  # Top 20 most significant flips

                logger.debug(f"[node.flip] Detected {len(flips)} flips, emitting top {len(top_k_flips)}")

                for flip in top_k_flips:
                    await self.broadcaster.broadcast_event("node.flip", {
                        "v": "2",
                        "frame_id": self.tick_count,
                        "node": flip["node_id"],
                        "E_pre": flip["E_pre"],
                        "E_post": flip["E_post"],
                        "Θ": flip["theta"],
                        "t_ms": int(time.time() * 1000)
                    })
                    logger.debug(f"[node.flip] {flip['node_id']}: {flip['E_pre']:.3f} → {flip['E_post']:.3f} (Δ={flip['delta_E']:.3f})")
            else:
                # Log when no flips detected (every 100 ticks to avoid spam)
                if self.tick_count % 100 == 0:
                    logger.debug(f"[node.flip] No threshold crossings detected at tick {self.tick_count}")

        # === V2 Event: link.flow.summary (aggregate link activity with decimation) ===
        # Decimation: Random sampling at 10% (~10Hz at 100Hz tick rate) to prevent frontend flood
        if self.broadcaster and self.broadcaster.is_available():
            import random

            # Random decimation: 10% sampling rate = ~10Hz at 100Hz tick rate
            if random.random() < 0.10:
                link_flows = []
                for link in self.graph.links.values():
                    # Skip links that don't connect two Nodes (e.g., links to/from Subentities)
                    # Nodes have .E attribute, Subentities have .energy_runtime
                    if not hasattr(link.source, 'E') or not hasattr(link.target, 'E'):
                        continue

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
        # SubEntity-first working memory selection (spec: subentity_layer.md §4)
        workspace_entities, wm_summary = self._select_workspace_entities(subentity)

        # P2.1.4: Detect phenomenological mismatch (expected vs actual WM)
        mismatch_detected = False
        mismatch_score = 0.0
        expected_entity_ids = []
        actual_entity_ids = [e.id for e in workspace_entities]

        if hasattr(self.graph, 'subentities') and self.graph.subentities:
            # Expected WM: Top entities by raw energy (phenomenological "felt" attention)
            entities_by_energy = sorted(
                self.graph.subentities.values(),
                key=lambda e: e.energy_runtime,
                reverse=True
            )
            expected_entity_ids = [e.id for e in entities_by_energy[:len(workspace_entities)]]

            # Compute mismatch: Jaccard distance (1 - intersection/union)
            expected_set = set(expected_entity_ids)
            actual_set = set(actual_entity_ids)

            if expected_set or actual_set:
                intersection = len(expected_set & actual_set)
                union = len(expected_set | actual_set)
                overlap = intersection / union if union > 0 else 1.0
                mismatch_score = 1.0 - overlap  # 0 = perfect match, 1 = no overlap

                # Gate: Emit if mismatch > 0.3 (30% divergence)
                mismatch_detected = mismatch_score > 0.3

        # P2.1.4: Emit phenomenology.mismatch event when detected
        if mismatch_detected and self.broadcaster and self.broadcaster.is_available():
            try:
                await self.broadcaster.broadcast_event("phenomenology.mismatch", {
                    "v": "2",
                    "frame_id": self.tick_count,
                    "citizen_id": self.config.entity_id,
                    "expected_entities": expected_entity_ids,
                    "actual_entities": actual_entity_ids,
                    "mismatch_score": round(mismatch_score, 3),
                    "diagnosis": f"Algorithm diverged from energy ranking by {mismatch_score:.0%}",
                    "t_ms": int(time.time() * 1000)
                })
                logger.debug(f"[P2.1.4] Mismatch: score={mismatch_score:.3f}, expected={expected_entity_ids}, actual={actual_entity_ids}")
            except Exception as e:
                logger.error(f"[P2.1.4] phenomenology.mismatch emission failed: {e}")

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
            # Defensive: ensure wm_summary and entities list exist
            if wm_summary and "entities" in wm_summary and wm_summary["entities"] is not None:
                entity_ids = [e["id"] for e in wm_summary["entities"] if e is not None]
                entity_token_shares = [
                    {"id": e["id"], "tokens": e.get("tokens", 0)}
                    for e in wm_summary["entities"]
                    if e is not None
                ]
                # Extract top member nodes from entities
                entity_member_nodes = []
                for e in wm_summary["entities"]:
                    if e is not None and "top_members" in e:
                        entity_member_nodes.extend([m["id"] for m in e["top_members"] if m is not None])
            else:
                # Fallback: empty lists if wm_summary is malformed
                entity_ids = []
                entity_token_shares = []
                entity_member_nodes = []

            await self.broadcaster.broadcast_event("wm.emit", {
                "v": "2",
                "frame_id": self.tick_count,
                "mode": "entity_first",
                "selected_entities": entity_ids,  # Just IDs
                "entity_token_shares": entity_token_shares,  # Token allocation
                "total_entities": wm_summary.get("total_entities", 0) if wm_summary else 0,
                "total_members": wm_summary.get("total_members", 0) if wm_summary else 0,
                "token_budget_used": wm_summary.get("token_budget_used", 0) if wm_summary else 0,
                "selected_nodes": entity_member_nodes,  # Top members from entities
                "t_ms": int(time.time() * 1000)
            })

            # === Priority 0: On-Change WM Detection & COACTIVATES_WITH Update ===
            # Emit wm.selected only when WM set or shares drift significantly
            # Updates COACTIVATES_WITH edges for lean U-metric (O(k^2) with k≈5-7)
            now_ms = int(time.time() * 1000)
            ids_sig, vec_sig = self._wm_signature(entity_ids, entity_token_shares)

            emit = False
            if not hasattr(self, "_last_wm_sig"):
                # First WM selection - always emit
                emit = True
            else:
                last_ids, last_vec = self._last_wm_sig

                # Set change detection
                if ids_sig != last_ids:
                    emit = True
                else:
                    # Share drift detection (cosine distance > threshold)
                    if last_vec and vec_sig:
                        a = np.array(last_vec)
                        b = np.array(vec_sig)
                        denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1.0
                        drift = 1.0 - float(np.dot(a, b) / denom)
                        emit = drift > 0.1  # Boot contour; will become learned percentile
                    else:
                        emit = True

            # Store signature for next comparison
            self._last_wm_sig = (ids_sig, vec_sig)

            if emit:
                # 1) WS event (for observability / consumers)
                await self.broadcaster.broadcast_event("wm.selected", {
                    "citizen": self.config.entity_id,
                    "frame_id": self.tick_count,
                    "entities_active": entity_ids,
                    "timestamp_ms": now_ms
                })

                # 2) DB co-activation update (lean U metric)
                try:
                    alpha = 0.1  # Boot contour; will become learned per citizen
                    await self.adapter.update_coactivation_edges_async(
                        citizen_id=self.config.entity_id,
                        entities_active=entity_ids,
                        alpha=alpha,
                        timestamp_ms=now_ms
                    )
                except Exception as e:
                    logger.error(f"[WM Coactivation] Update failed: {e}")

            # P1: Store entity IDs for TraceCapture attribution
            self.last_wm_entity_ids = entity_ids

            # Phase 3A: Forged Identity Generation (observe-only)
            # Generate system prompt + input context from WM state
            # Logs prompts for quality assessment, no LLM execution yet
            logger.debug(f"[ForgedIdentity] Checking stimulus tracking: hasattr={hasattr(self, '_last_stimulus_text')}")
            if hasattr(self, '_last_stimulus_text') and self._last_stimulus_text is not None:
                logger.info(f"[ForgedIdentity] Stimulus tracked: {self._last_stimulus_text[:50]}...")
                try:
                    from orchestration.mechanisms.forged_identity_integration import get_forged_identity_integration

                    integration = get_forged_identity_integration()
                    logger.debug(f"[ForgedIdentity] Integration retrieved: {integration is not None}")

                    if integration:
                        logger.info(f"[ForgedIdentity] Starting prompt generation for {self.config.entity_id}")

                        # Extract WM nodes from entities for prompt generation
                        wm_nodes = []
                        for entity in workspace_entities:
                            entity_data = {
                                "entity_id": entity.id,
                                "energy": entity.energy_runtime,
                                "members": []
                            }
                            # Add member nodes with their energies
                            for member_id in entity.members[:10]:  # Top 10 members per entity
                                node = self.graph.get_node(member_id)
                                if node:
                                    entity_data["members"].append({
                                        "node_id": node.id,
                                        "name": node.name,
                                        "description": node.description,
                                        "energy": node.E
                                    })
                            wm_nodes.append(entity_data)

                        logger.info(f"[ForgedIdentity] Extracted {len(wm_nodes)} WM entities")

                        # Generate prompt (Phase 3A: logs but doesn't execute)
                        await integration.process_stimulus_response(
                            citizen_id=self.config.entity_id,
                            stimulus_text=self._last_stimulus_text,
                            stimulus_id=self._last_stimulus_id,
                            wm_nodes=wm_nodes,
                            conversation_context=None  # TODO: Add conversation history when available
                        )

                        logger.info(f"[ForgedIdentity] Prompt generation completed")

                        # Clear stimulus to prevent re-triggering on subsequent ticks
                        self._last_stimulus_text = None
                        self._last_stimulus_id = None
                        logger.debug(f"[ForgedIdentity] Stimulus tracking cleared - will not re-trigger")
                    else:
                        logger.warning(f"[ForgedIdentity] Integration is None - not initialized properly")
                except Exception as e:
                    import traceback
                    logger.error(f"[ForgedIdentity] Generation failed: {e}")
                    logger.error(f"[ForgedIdentity] Traceback: {traceback.format_exc()}")
                    # Clear stimulus even on failure to prevent infinite retry loops
                    self._last_stimulus_text = None
                    self._last_stimulus_id = None
            else:
                logger.debug(f"[ForgedIdentity] No stimulus tracked this tick")

            # Phase 1: Update SubEntity context tracking (affect EMAs + context distributions)
            # Extract frame-level affect from active entity (if available)
            frame_affect = None
            if wm_summary["entities"]:
                # Use primary entity's affect as frame affect
                primary_entity_id = wm_summary["entities"][0]["id"]
                primary_entity = self.graph.subentities.get(primary_entity_id)
                if primary_entity and hasattr(primary_entity, 'prev_affect_for_coherence'):
                    if primary_entity.prev_affect_for_coherence is not None:
                        # Format: [valence, arousal] -> need [arousal, valence]
                        affect_vec = primary_entity.prev_affect_for_coherence
                        if len(affect_vec) >= 2:
                            # Swap to [arousal, valence] and normalize
                            arousal = float(np.clip(abs(affect_vec[1]), 0.0, 1.0))
                            valence = float(np.clip(affect_vec[0], -1.0, 1.0))
                            frame_affect = np.array([arousal, valence])

            # Extract frame-level channel from last stimulus (if any)
            frame_channel = None
            if hasattr(self, '_last_stimulus_channel'):
                frame_channel = self._last_stimulus_channel

            # Update context tracker for active SubEntities
            self.subentity_context_tracker.update_from_wm_frame(
                graph=self.graph,
                active_subentities=entity_ids,
                frame_affect=frame_affect,
                frame_tool=None,  # TODO: Track from tool usage events
                frame_channel=frame_channel,
                frame_outcome=None  # TODO: Track from TRACE events
            )

            # === V2 Event: subentity.snapshot (active subentity visualization) ===
            # Collect active subentities (energy >= threshold)
            act = []
            if hasattr(self.graph, 'subentities') and self.graph.subentities:
                for e in self.graph.subentities.values():
                    E = float(getattr(e, "energy_runtime", 0.0))
                    th = float(getattr(e, "threshold_runtime", 30.0))
                    if E >= th:
                        # Get display name: try role_or_topic, then id
                        name = getattr(e, "role_or_topic", getattr(e, "id", "unknown"))
                        # If name is still an ID-like string, try to extract last part
                        if name.startswith("entity_"):
                            name = name.split('_')[-1] if '_' in name else name

                        act.append({
                            "id": e.id,
                            "name": name,
                            # Normalize to 0..1 for UI (cap at 100 for reasonable range)
                            "energy": round(min(max(E / 100.0, 0.0), 1.0), 3),
                            "theta": round(min(max(th / 100.0, 0.0), 1.0), 3),
                        })

            # Sort by energy descending, cap at 8
            act.sort(key=lambda x: x["energy"], reverse=True)
            act = act[:8]

            # Build WM list from selected entities
            wm_list = []
            token_budget_total = wm_summary.get("token_budget_total", 2000)
            for entity_id in entity_ids[:8]:  # Cap at 8
                # Find the entity object
                entity = self.graph.subentities.get(entity_id)
                if entity:
                    name = getattr(entity, "role_or_topic", getattr(entity, "id", "unknown"))
                    if name.startswith("entity_"):
                        name = name.split('_')[-1] if '_' in name else name

                    # Get token share from entity_token_shares
                    token_share = 1.0
                    for ets in entity_token_shares:
                        if ets["id"] == entity_id:
                            token_share = float(ets.get("tokens", 1.0)) / token_budget_total if token_budget_total > 0 else 1.0
                            break

                    wm_list.append({
                        "id": entity_id,
                        "name": name,
                        "share": round(token_share, 3)
                    })

            await self.broadcaster.broadcast_event("subentity.snapshot", {
                "v": "1",
                "frame_id": self.tick_count,
                "citizen_id": self.config.entity_id,
                "active": act,
                "wm": wm_list,
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

        # === Dynamic Prompt Update: Check entity activation changes ===
        if hasattr(self, 'dynamic_prompt') and hasattr(self.graph, 'subentities') and self.graph.subentities:
            try:
                entity_ids = list(self.graph.subentities.keys())
                global_crit = criticality_metrics.rho_global if criticality_metrics else 0.5
                await self.dynamic_prompt.check_and_update(
                    global_criticality=global_crit,
                    entity_ids=entity_ids
                )
            except Exception as e:
                logger.warning(f"[DynamicPrompt] Update failed: {e}")

        # === Step 10: Tick Frame V1 Event (SubEntity-First Telemetry) + TRIPWIRE: Observability ===
        # tick_frame.v1 is the heartbeat signal - missing events → monitoring blind
        # Replaces legacy frame.end with subentity-scale observability
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
                                avg_emotion = np.mean(emotions, axis=0)
                                emotion_valence = float(avg_emotion[0]) if len(avg_emotion) > 0 else 0.0
                                emotion_arousal = float(avg_emotion[1]) if len(avg_emotion) > 1 else 0.0
                                emotion_magnitude = float(np.linalg.norm(avg_emotion))

                        entity_data = EntityData(
                            id=entity_id,
                            name=entity.role_or_topic if hasattr(entity, 'role_or_topic') else entity_id,
                            kind=entity.entity_kind if hasattr(entity, 'entity_kind') else "functional",
                            color=entity.properties.get('color', "#808080") if hasattr(entity, 'properties') else "#808080",
                            energy=float(entity.energy_runtime),
                            theta=float(entity.threshold_runtime),
                            active=entity.energy_runtime >= entity.threshold_runtime,
                            members_count=len(entity.extent) if hasattr(entity, 'extent') else 0,
                            coherence=entity.coherence_ema if hasattr(entity, 'coherence_ema') else 0.0,
                            emotion_valence=emotion_valence,
                            emotion_arousal=emotion_arousal,
                            emotion_magnitude=emotion_magnitude
                        )
                        entity_data_list.append(entity_data)

                # Create tick_frame.v1 event
                tick_event = TickFrameV1Event(
                    citizen_id=self.config.entity_id,
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

        # === P2.1 Event: health.phenomenological (hysteresis-based emission) ===
        # Phenomenological health state assessment for operator visibility
        # Translates quantitative metrics into qualitative consciousness states
        # Uses hysteresis: only emit when state changes OR fragmentation shifts >0.1
        if self.tick_count % 5 == 0 and self.broadcaster and self.broadcaster.is_available():
            try:
                from orchestration.mechanisms.phenomenology_health import classify

                # Classify current health state
                result = classify(self.graph.subentities.values() if hasattr(self.graph, 'subentities') else [])

                # Hysteresis check: only emit if state changed OR fragmentation shifted >0.1
                state_changed = (result.state != self._last_health_state)
                frag_shifted = abs(result.fragmentation - self._last_frag) > 0.1
                must_emit = state_changed or frag_shifted or (self._last_health_state is None)

                if must_emit:
                    # Emit event with Nicolas's event shape
                    await self.broadcaster.broadcast_event("health.phenomenological", {
                        "v": "2",
                        "frame_id": self.tick_count,
                        "citizen_id": self.config.entity_id,
                        "state": result.state,
                        "fragmentation": round(result.fragmentation, 3),
                        "components": {
                            "flow": round(result.components.flow, 3),
                            "coherence": round(result.components.coherence, 3),
                            "multiplicity": round(result.components.multiplicity, 3),
                        },
                        "narrative": result.cause,
                        "t_ms": int(time.time() * 1000)
                    })

                    logger.debug(
                        f"[P2.1] Health: {result.state} "
                        f"(frag={result.fragmentation:.3f}, flow={result.components.flow:.2f}, "
                        f"coherence={result.components.coherence:.2f}, mult={result.components.multiplicity:.2f})"
                    )

                    # Update hysteresis state
                    self._last_health_state = result.state
                    self._last_frag = result.fragmentation

            except Exception as e:
                # Health emission failed - log but don't crash tick
                logger.error(f"[P2.1] health.phenomenological emission failed: {e}")

        # === Pass B: Periodic Persistence Flush ===
        # Check if dirty nodes should be persisted (auto-flush enabled with MP_PERSIST_ENABLED=1)
        if self._persist_enabled:
            await self._persist_dirty_if_due()

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
                if link.link_type == LinkType.MEMBER_OF
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
            f"[Step 9] SubEntity-First WM: {len(selected_entities)} entities selected, "
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

    async def _ensure_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Generate embedding for stimulus text with timeout + circuit breaker.

        Embedding service is pre-initialized during engine creation to avoid
        first-stimulus timeout. This method just calls embed() with timeout.

        Args:
            text: Stimulus text to embed

        Returns:
            768-dim embedding array or None if unavailable

        Author: Felix "Ironhand"
        Date: 2025-10-25 (Updated 2025-10-30: pre-init instead of lazy-init)
        Pattern: Circuit breaker for optional enrichments (never block core path)
        """
        # Check if embedding service is available (pre-initialized in __init__)
        if self._embedding_service is None:
            logger.debug("[Stimulus] Embedding service not available, using best-effort fallback")
            return None

        # Circuit breaker: if embedder failed recently, skip (avoid repeated hangs)
        if self._embedding_circuit_open_until > time.time():
            logger.debug("[Stimulus] Embedding circuit breaker OPEN, skipping embed")
            return None

        # Try to embed with hard timeout (2s should be enough for inference only)
        try:
            loop = asyncio.get_running_loop()
            embedding = await asyncio.wait_for(
                loop.run_in_executor(None, self._embedding_service.embed, text),
                timeout=2.0
            )

            # Success - reset failure counter
            self._embedding_failures = 0
            return np.array(embedding)

        except asyncio.TimeoutError:
            logger.warning("[Stimulus] Embedding timeout (>2s), using best-effort fallback")
            self._embedding_failures += 1

            # Open circuit breaker after 3 consecutive failures (30s cooldown)
            if self._embedding_failures >= 3:
                self._embedding_circuit_open_until = time.time() + 30.0
                logger.warning("[Stimulus] Embedding circuit breaker OPEN for 30s after 3 failures")

            return None

        except Exception as e:
            logger.warning(f"[Stimulus] Embedding failed: {e}")
            self._embedding_failures += 1
            return None

    async def inject_stimulus_async(self, text: str, severity: float = 0.3, metadata: dict = None):
        """
        Async-safe stimulus injection (for control API).

        Args:
            text: Stimulus text content
            severity: Stimulus severity/importance (0.0-1.0)
            metadata: Optional metadata dict (stimulus_id, origin, timestamp_ms, etc.)

        Example:
            >>> await engine.inject_stimulus_async("Test", severity=0.5, metadata={"origin": "api"})
        """
        # Extract source_type from metadata or use default
        source_type = (metadata or {}).get("origin", "external")

        # Queue stimulus (list append is atomic in Python)
        self.stimulus_queue.append({
            'text': text,
            'embedding': None,  # Control API doesn't provide embeddings
            'source_type': source_type,
            'severity': severity,
            'metadata': metadata or {}
        })
        logger.info(f"[ConsciousnessEngineV2] Queued stimulus (async): {text[:50]}... (severity={severity}, origin={source_type})")

    def inject_stimulus_threadsafe(self, text: str, severity: float = 0.3, metadata: dict = None):
        """
        Thread-safe stimulus injection (for non-async contexts).

        Args:
            text: Stimulus text content
            severity: Stimulus severity/importance (0.0-1.0)
            metadata: Optional metadata dict

        Returns:
            Future that can be awaited with .result(timeout=...)

        Example:
            >>> future = engine.inject_stimulus_threadsafe("Test", severity=0.5)
            >>> future.result(timeout=5.0)  # Wait for injection to complete

        Raises:
            RuntimeError: If engine loop is not running
        """
        async def _inject():
            await self.inject_stimulus_async(text, severity, metadata)

        if not hasattr(self, 'loop') or not self.loop or not self.loop.is_running():
            raise RuntimeError("Engine loop not running - cannot inject stimulus")

        return asyncio.run_coroutine_threadsafe(_inject(), self.loop)

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

    def _mark_node_dirty_if_changed(self, node_id: str, deadband: float = 0.5):
        """
        Mark node as dirty if energy/threshold changed significantly since last persist.

        Args:
            node_id: Node to check
            deadband: Minimum delta to mark dirty (default 0.5)

        Author: Atlas
        Date: 2025-10-25
        Pass: B (auto-flush integration)
        """
        node = self.graph.get_node(node_id)
        if not node:
            return

        # Get current runtime values
        E_current = float(getattr(node, "energy_runtime", 0.0))
        theta_current = float(getattr(node, "threshold_runtime", 30.0))

        # Get last persisted values (if any)
        if node_id in self._last_persisted:
            E_last, theta_last = self._last_persisted[node_id]

            # Check if changed beyond deadband
            E_delta = abs(E_current - E_last)
            theta_delta = abs(theta_current - theta_last)

            if E_delta > deadband or theta_delta > deadband:
                self._dirty_nodes.add(node_id)
        else:
            # Never persisted before - mark dirty
            self._dirty_nodes.add(node_id)

    async def _persist_dirty_if_due(self):
        """
        Persist dirty nodes if interval elapsed and batch size met.

        Strategy (Pass B - auto-flush enabled):
        - Check if interval elapsed since last persist
        - If yes AND dirty_nodes >= min_batch: flush to database
        - Use thread pool to avoid blocking event loop
        - Track what was persisted to avoid oscillation

        Gating:
        - Requires MP_PERSIST_ENABLED=1 env var
        - Respects interval + jitter (avoid herd flushes)
        - Respects min batch size
        """
        if not self._persist_enabled:
            return  # Feature flag off

        import random
        now = time.time()

        # Time gate with jitter
        jittered_interval = self._persist_interval_sec + random.uniform(-self._persist_jitter, self._persist_jitter)
        elapsed = now - self._last_persist_time

        if elapsed < jittered_interval:
            return  # Not time yet

        if len(self._dirty_nodes) < self._persist_min_batch:
            return  # Not enough dirty nodes to warrant flush

        # Build rows for bulk persist (use runtime fields, not init values)
        rows = []
        for node_id in self._dirty_nodes:
            node = self.graph.get_node(node_id)
            if not node:
                continue

            # V2 SCHEMA FIX: Node uses E and theta attributes directly
            E = float(node.E)  # Single scalar energy (V2 architecture)
            theta = float(node.theta)  # Activation threshold

            # Clamp to valid range (energy is non-negative, theta must be positive)
            E = max(0.0, E)
            theta = max(0.001, theta)  # theta > 0 to avoid division by zero

            # Serialize entity_activations as JSON string for FalkorDB
            entity_activations_json = json.dumps(node.entity_activations) if node.entity_activations else "{}"

            rows.append({
                'node_id': node_id,  # For tracking in _last_persisted
                'id': None,  # Trigger name-based matching (FalkorDB uses prefixed IDs)
                'name': node.name,  # Match by name instead
                'label': node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type),
                'E': E,
                'theta': theta,
                'entity_activations': entity_activations_json  # For frontend viz
            })

        if not rows:
            self._dirty_nodes.clear()
            return

        try:
            # Execute in thread pool to avoid blocking tick loop
            # Pass WriteGate context for L1/L2/L3/L4 namespace enforcement
            namespace = f"L1:{self.config.entity_id}"  # Citizen graphs are L1
            loop = asyncio.get_running_loop()
            updated = await loop.run_in_executor(
                None,
                lambda: self.adapter.persist_node_scalars_bulk(rows, ctx={"ns": namespace})
            )

            logger.info(f"[Persistence] Flushed {updated}/{len(rows)} dirty nodes to FalkorDB")

            # Update _last_persisted tracking for flushed nodes (use node_id, not database id)
            for row in rows:
                self._last_persisted[row['node_id']] = (row['E'], row['theta'])

            # Telemetry
            self._persist_batch_sizes.append(len(rows))

            # Clear dirty set and update timestamp
            self._dirty_nodes.clear()
            self._last_persist_time = now

        except Exception as e:
            logger.error(f"[Persistence] Failed to flush dirty nodes: {e}")
            self._persist_failures += 1
            self._persist_last_error = str(e)
            # Don't clear dirty set - will retry next interval

    async def persist_to_database(self, force: bool = False):
        """
        Force persist all nodes immediately (for shutdown/manual flush).

        Args:
            force: If True, ignores interval/batch thresholds and persists everything

        Usage:
            - Manual API endpoint: POST /api/citizen/{id}/persist
            - Shutdown hook: engine.persist_to_database(force=True)
        """
        logger.info(f"[ConsciousnessEngineV2] Force persisting all nodes (force={force})...")

        # Build rows for all nodes (use runtime fields)
        rows = []
        for node in self.graph.nodes.values():
            # V2 SCHEMA FIX: Node uses E and theta attributes directly
            E = float(node.E)  # Single scalar energy (V2 architecture)
            theta = float(node.theta)  # Activation threshold

            # Clamp to valid range (energy non-negative, theta must be positive)
            E = max(0.0, E)
            theta = max(0.001, theta)  # theta > 0 to avoid division by zero

            # Serialize entity_activations as JSON string for FalkorDB
            entity_activations_json = json.dumps(node.entity_activations) if node.entity_activations else "{}"

            rows.append({
                'node_id': node.id,  # For tracking in _last_persisted
                'id': None,  # Trigger name-based matching (FalkorDB uses prefixed IDs)
                'name': node.name,  # Match by name instead
                'label': node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type),
                'E': E,
                'theta': theta,
                'entity_activations': entity_activations_json  # For frontend viz
            })

        if not rows:
            logger.warning("[ConsciousnessEngineV2] No nodes to persist")
            return

        try:
            # Execute in thread pool
            loop = asyncio.get_running_loop()
            updated = await loop.run_in_executor(
                None,
                lambda: self.adapter.persist_node_scalars_bulk(rows)
            )

            logger.info(f"[ConsciousnessEngineV2] Persisted {updated}/{len(rows)} nodes")

            # Update tracking (use node_id, not database id)
            for row in rows:
                self._last_persisted[row['node_id']] = (row['E'], row['theta'])

            # Clear dirty set
            self._dirty_nodes.clear()
            self._last_persist_time = time.time()

        except Exception as e:
            logger.error(f"[ConsciousnessEngineV2] Force persist failed: {e}")
            self._persist_failures += 1
            self._persist_last_error = str(e)
            raise  # Re-raise on manual flush for visibility

    def get_metrics(self) -> Dict:
        """
        Get current engine metrics.

        Returns:
            Metrics dict with tick count, duration, active nodes, etc.
        """
        subentity = self.config.entity_id

        # Count active nodes (subentities = nodes with total_energy >= threshold)
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

        # Get actual subentity count and IDs (per Nicolas's task specification)
        # DEBUG: Log what we're seeing
        logger.warning(f"[get_status] DEBUG CHECKPOINT C: {subentity}: graph.subentities len={len(self.graph.subentities) if self.graph.subentities else 0}, "
                     f"graph id={id(self.graph)}")
        if self.graph.subentities:
            logger.warning(f"[get_status] DEBUG: {subentity}: subentities keys={list(self.graph.subentities.keys())[:3]}")
        else:
            logger.error(f"[get_status] CRITICAL: {subentity}: graph.subentities is EMPTY/NONE when get_status() called!")
        sub_entity_count = len(self.graph.subentities) if self.graph.subentities else 1
        sub_entity_ids = list(self.graph.subentities.keys()) if self.graph.subentities else [subentity]
        logger.warning(f"[get_status] DEBUG: {subentity}: RETURNING sub_entity_count={sub_entity_count}, ids={sub_entity_ids[:3] if len(sub_entity_ids) > 3 else sub_entity_ids}")

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
            "links": len(self.graph.links),
            # Persistence configuration (Pass B)
            "persistence_enabled": self._persist_enabled,
            "persistence_min_batch": self._persist_min_batch,
            "persistence_interval_sec": self._persist_interval_sec,
            "dirty_nodes_count": len(self._dirty_nodes)
        }
# Force reload
# Force reload
# Trigger hot-reload - Felix fix 2025-10-25
# Trigger restart for Pass B test
# Hot-reload test 1761424683
