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
import numpy as np
from typing import Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass

# Core data structures
from orchestration.core import Node, Link, Graph

# Mechanisms (Phase 1+2)
from orchestration.mechanisms import diffusion, decay, strengthening, threshold
from orchestration.mechanisms.diffusion import DiffusionContext
from orchestration.mechanisms.decay import DecayContext
from orchestration.mechanisms.strengthening import StrengtheningContext
from orchestration.mechanisms.threshold import ThresholdContext, NoiseTracker

# Learning Mechanisms (Phase 3+4)
from orchestration.mechanisms.stimulus_injection import StimulusInjector, create_match
from orchestration.mechanisms.weight_learning import WeightLearner

# Observability
from orchestration.orchestration.metrics import BranchingRatioTracker
from orchestration.orchestration.websocket_broadcast import ConsciousnessStateBroadcaster

# FalkorDB integration
from orchestration.utils.falkordb_adapter import FalkorDBAdapter

logger = logging.getLogger(__name__)


@dataclass
class EngineConfig:
    """
    Configuration for consciousness engine.

    Args:
        tick_interval_ms: Base tick interval in milliseconds. Default 100ms (10 Hz).
        entity_id: Primary entity identifier. Default "consciousness_engine".
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

        # Mechanism contexts (Phase 1+2)
        self.diffusion_ctx = DiffusionContext()
        self.decay_ctx = DecayContext()
        self.strengthening_ctx = StrengtheningContext()
        self.threshold_ctx = ThresholdContext()
        self.noise_tracker = NoiseTracker()

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

        # Metrics
        self.last_tick_time = datetime.now()
        self.tick_duration_ms = 0.0

        # Transition matrix cache (rebuild only when graph structure changes)
        self._transition_matrix = None
        self._transition_matrix_dirty = True

        logger.info(f"[ConsciousnessEngineV2] Initialized")
        logger.info(f"  Entity: {self.config.entity_id}")
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
                # Execute one tick
                await self.tick()

                # Check max ticks
                if max_ticks is not None and self.tick_count >= max_ticks:
                    logger.info(f"[ConsciousnessEngineV2] Reached max ticks ({max_ticks})")
                    break

                # Sleep until next tick
                await asyncio.sleep(self.config.tick_interval_ms / 1000.0)

        except KeyboardInterrupt:
            logger.info("[ConsciousnessEngineV2] Interrupted by user")
        finally:
            self.running = False
            logger.info("[ConsciousnessEngineV2] Stopped")

    def stop(self):
        """Stop the engine."""
        self.running = False

    async def tick(self):
        """
        Execute one consciousness tick.

        Four-Phase Cycle with Learning Integration:
        1. Activation: Process stimuli, inject energy
        2. Redistribution: Diffusion + Decay
        3. Workspace: Weight-based WM selection
        4. Learning: TRACE signals + weight updates
        """
        tick_start = time.time()
        entity = self.config.entity_id

        # === V2 Event: frame.start ===
        if self.broadcaster and self.broadcaster.is_available():
            await self.broadcaster.broadcast_event("frame.start", {
                "v": "2",
                "frame_id": self.tick_count,
                "t_ms": int(time.time() * 1000)
            })

        # Capture previous state for flip detection
        # NOTE: Using TOTAL energy per spec (sub-entity = any active node)
        previous_states = {}
        for node in self.graph.nodes.values():
            previous_states[node.id] = {
                'energy': node.get_total_energy(),
                'threshold': node.threshold,
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
                    current_energy = node.get_total_energy()  # Use total energy for activation

                    match = create_match(
                        item_id=node.id,
                        item_type='node',
                        similarity=similarity,
                        current_energy=current_energy,
                        threshold=node.threshold
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
                            node.increment_entity_energy(entity, injection['delta_energy'])

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

        # === Phase 2: Redistribution ===
        # Apply diffusion (conservative energy redistribution)
        if self.config.enable_diffusion:
            diffusion.diffusion_tick(self.graph, entity, self.diffusion_ctx)

        # Apply decay (exponential forgetting)
        if self.config.enable_decay:
            decay_metrics = decay.decay_tick(self.graph, entity, self.decay_ctx)

        # === V2 Event: node.flip (detect threshold crossings) ===
        # NOTE: Using TOTAL energy per spec (sub-entity activation is total_energy >= threshold)
        if self.broadcaster and self.broadcaster.is_available():
            for node in self.graph.nodes.values():
                prev_state = previous_states[node.id]
                current_energy = node.get_total_energy()  # Use total energy for sub-entity activation
                is_now_active = node.is_active()  # Sub-entity activation check

                # Emit flip event if activation state changed
                if prev_state['was_active'] != is_now_active:
                    await self.broadcaster.broadcast_event("node.flip", {
                        "v": "2",
                        "frame_id": self.tick_count,
                        "node": node.id,
                        "E_pre": prev_state['energy'],
                        "E_post": current_energy,
                        "Θ": node.threshold,
                        "t_ms": int(time.time() * 1000)
                    })

        # === V2 Event: link.flow.summary (aggregate link activity) ===
        if self.broadcaster and self.broadcaster.is_available():
            link_flows = []
            for link in self.graph.links.values():
                # Get energy flow through this link (simplified - would track actual flow during diffusion)
                source_energy = link.source.get_entity_energy(entity)
                target_energy = link.target.get_entity_energy(entity)

                # Estimate flow as function of energy difference and link weight
                ΔE_estimate = link.weight * max(0, source_energy - target_energy) * self.diffusion_ctx.alpha

                # Only include links with non-zero flow
                if ΔE_estimate > 0.001:
                    link_flows.append({
                        "id": f"{link.source.id}->{link.target.id}",
                        "ΔE_sum": round(ΔE_estimate, 4),
                        "φ_max": round(link.weight, 3),  # Using link weight as proxy for φ
                        "z_flow": 0.0  # Would compute from cohort normalization
                    })

            if link_flows:
                # Transform to frontend-expected format
                flows_payload = [{
                    "link_id": flow["id"],
                    "count": 1,  # Single traversal per link in this implementation
                    "entity_ids": [entity]  # Which entity traversed this link (entity is string)
                } for flow in link_flows]

                await self.broadcaster.broadcast_event("link.flow.summary", {
                    "v": "2",
                    "frame_id": self.tick_count,
                    "flows": flows_payload,  # Changed from "links" to "flows"
                    "t_ms": int(time.time() * 1000)
                })

        # === Phase 3: Workspace Selection (Weight-Based) ===
        # Select working memory nodes using weight-based scoring
        workspace_nodes = self._select_workspace(activated_nodes, entity)

        # Update WM presence tracking
        for node in self.graph.nodes.values():
            wm_indicator = 1 if node in workspace_nodes else 0
            node.ema_wm_presence = 0.1 * wm_indicator + 0.9 * node.ema_wm_presence

        # === V2 Event: wm.emit (working memory selection) ===
        if self.broadcaster and self.broadcaster.is_available():
            await self.broadcaster.broadcast_event("wm.emit", {
                "v": "2",
                "frame_id": self.tick_count,
                "selected_nodes": [node.id for node in workspace_nodes],
                "t_ms": int(time.time() * 1000)
            })

        # === Phase 4: Learning & Metrics ===
        # Process TRACE signals and update weights
        while self.trace_queue:
            trace_result = self.trace_queue.pop(0)
            self._apply_trace_learning(trace_result)

        # Strengthen links between active nodes
        if self.config.enable_strengthening:
            strengthening_metrics = strengthening.strengthen_tick(
                self.graph,
                entity,
                self.strengthening_ctx,
                active_nodes=workspace_nodes
            )

        # Measure branching ratio
        # (Compare activated this gen vs next gen - simplified: use current activated count)
        if self.tick_count > 0:
            previous_activated = getattr(self, '_previous_activated', activated_nodes)
            branching_state = self.branching_tracker.measure_cycle(
                activated_this_gen=previous_activated,
                activated_next_gen=activated_nodes
            )
            self._previous_activated = activated_nodes
        else:
            self._previous_activated = activated_nodes
            branching_state = None

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

        # === V2 Event: frame.end ===
        if self.broadcaster and self.broadcaster.is_available():
            await self.broadcaster.broadcast_event("frame.end", {
                "v": "2",
                "frame_id": self.tick_count,
                "t_ms": int(time.time() * 1000),
                "stride_budget_used": 0,  # TODO: Track actual stride count
                "stride_budget_left": int(self.config.compute_budget),
                "emit_counts": {
                    "nodes": len([n for n in self.graph.nodes.values() if n.is_active()]),  # Count active sub-entities
                    "links": len(workspace_nodes),  # Simplified
                    "tick_duration_ms": round(tick_duration, 2)
                }
            })

        # Increment tick count AFTER emitting frame.end (so frame_id is correct)
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

    def _select_workspace(self, activated_node_ids: List[str], entity: str) -> List[Node]:
        """
        Select working memory nodes using weight-based scoring.

        Score = (energy / tokens) * exp(z_W)

        Args:
            activated_node_ids: IDs of nodes above threshold
            entity: Entity to select workspace for

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
            energy = node.get_total_energy()  # Use total energy for workspace selection
            energy_per_token = energy / token_count

            # Standardized weight
            z_W = self.weight_learner.standardize_weight(
                node.log_weight,
                node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type),
                node.scope
            )

            # Weight boost (normalized attractor mass)
            import math
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
            >>> from orchestration.trace_parser import TraceParser
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
        entity = self.config.entity_id

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
        entity = self.config.entity_id

        # Calculate global energy (average total energy across all nodes)
        global_energy = sum(
            node.get_total_energy()
            for node in self.graph.nodes.values()
        ) / max(len(self.graph.nodes), 1)

        # Get consciousness state from energy level
        consciousness_state = self._get_consciousness_state_name(global_energy)

        # Calculate tick frequency
        tick_frequency_hz = 1000.0 / self.config.tick_interval_ms if self.config.tick_interval_ms > 0 else 0.0

        # Time since last tick
        time_since_last_tick = (datetime.now() - self.last_tick_time).total_seconds()

        return {
            "citizen_id": entity,
            "running_state": "running" if self.running else "paused",
            "tick_count": self.tick_count,
            "tick_interval_ms": self.config.tick_interval_ms,
            "tick_frequency_hz": round(tick_frequency_hz, 2),
            "tick_multiplier": 1.0,  # V2 doesn't support speed multiplier yet
            "consciousness_state": consciousness_state,
            "time_since_last_event": round(time_since_last_tick, 2),
            "sub_entity_count": 1,  # V2 doesn't support multiple sub-entities yet
            "sub_entities": [entity],
            "nodes": len(self.graph.nodes),
            "links": len(self.graph.links)
        }
# Force reload
