"""
SubEntity Gap Detector - Emergence Opportunity Detection

Detects three types of gaps during stimulus injection:
1. Semantic Gap: Retrieved nodes don't cover stimulus embedding
2. Quality Gap: Retrieved nodes too general/abstract for concrete stimulus
3. Structural Gap: Retrieved nodes disconnected/sparse

Hooks into stimulus injection pipeline (after retrieval, before energy apply).
Emits emergence proposals when gaps detected.

Author: Felix (Core Consciousness Engineer)
Date: 2025-10-29
Spec: docs/specs/v2/subentity_layer/subentity_emergence_orchestration.md §3.1
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from orchestration.mechanisms.quantile_gate import QuantileGate, QuantileConfig, ComparisonMode, GateStatus


class GapType(str, Enum):
    """Type of gap detected"""
    SEMANTIC = "semantic"      # Embedding coverage gap
    QUALITY = "quality"        # Abstraction mismatch
    STRUCTURAL = "structural"  # Graph connectivity gap


@dataclass
class GapSignal:
    """Signal indicating a gap was detected"""
    gap_type: GapType
    strength: float                    # 0-1, how strong the gap signal is
    stimulus_id: str
    retrieved_node_ids: List[str]
    gap_metrics: Dict[str, float]      # Metrics that triggered gap
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GapDetectionConfig:
    """Configuration for gap detection"""
    # Semantic gap thresholds
    min_embedding_coverage: float = 0.6      # Minimum cosine similarity to stimulus
    coverage_percentile_gate: float = 0.30   # Must be below Q30 to trigger semantic gap

    # Quality gap thresholds
    max_abstraction_mismatch: float = 2.0    # Max difference in abstraction levels
    abstraction_percentile_gate: float = 0.70  # Must exceed Q70 to trigger quality gap

    # Structural gap thresholds
    min_connectivity: float = 0.3            # Minimum inter-node connectivity
    connectivity_percentile_gate: float = 0.30  # Must be below Q30 to trigger structural gap

    # Gate configuration
    min_samples_for_gates: int = 30
    history_window: int = 1000


class SubEntityGapDetector:
    """
    Detects gaps in retrieval that signal emergence opportunities.

    Maintains quantile gates for each gap type and evaluates retrieval
    quality against learned thresholds.

    Integration Point: stimulus_injection.py after retrieval, before energy apply
    """

    def __init__(self, config: Optional[GapDetectionConfig] = None):
        self.config = config or GapDetectionConfig()

        # Quantile gates for adaptive thresholds
        self.coverage_gate = QuantileGate(QuantileConfig(
            metric_name="embedding_coverage",
            quantile_level=self.config.coverage_percentile_gate,
            comparison_mode=ComparisonMode.BELOW,  # Coverage below Q30 = gap
            min_samples=self.config.min_samples_for_gates,
            window_size=self.config.history_window
        ))

        self.abstraction_gate = QuantileGate(QuantileConfig(
            metric_name="abstraction_mismatch",
            quantile_level=self.config.abstraction_percentile_gate,
            comparison_mode=ComparisonMode.ABOVE,  # Mismatch above Q70 = gap
            min_samples=self.config.min_samples_for_gates,
            window_size=self.config.history_window
        ))

        self.connectivity_gate = QuantileGate(QuantileConfig(
            metric_name="node_connectivity",
            quantile_level=self.config.connectivity_percentile_gate,
            comparison_mode=ComparisonMode.BELOW,  # Connectivity below Q30 = gap
            min_samples=self.config.min_samples_for_gates,
            window_size=self.config.history_window
        ))

        # Telemetry
        self.gaps_detected_count: Dict[GapType, int] = {
            GapType.SEMANTIC: 0,
            GapType.QUALITY: 0,
            GapType.STRUCTURAL: 0
        }

    def detect_gaps(
        self,
        stimulus_id: str,
        stimulus_embedding: np.ndarray,
        retrieved_nodes: List[Dict[str, Any]],
        graph_context: Optional[Dict[str, Any]] = None
    ) -> List[GapSignal]:
        """
        Detect gaps in retrieval results.

        Args:
            stimulus_id: Unique identifier for stimulus
            stimulus_embedding: Embedding vector of stimulus
            retrieved_nodes: List of nodes retrieved for stimulus
                Each node dict should have: id, embedding, properties
            graph_context: Optional graph structure information

        Returns:
            List of GapSignals detected (may be empty, or contain multiple gaps)
        """
        if not retrieved_nodes:
            # No nodes retrieved = extreme semantic gap
            return [GapSignal(
                gap_type=GapType.SEMANTIC,
                strength=1.0,
                stimulus_id=stimulus_id,
                retrieved_node_ids=[],
                gap_metrics={'embedding_coverage': 0.0},
                context={'reason': 'no_nodes_retrieved'}
            )]

        gaps: List[GapSignal] = []

        # 1. Check semantic gap
        semantic_gap = self._detect_semantic_gap(
            stimulus_id, stimulus_embedding, retrieved_nodes
        )
        if semantic_gap:
            gaps.append(semantic_gap)
            self.gaps_detected_count[GapType.SEMANTIC] += 1

        # 2. Check quality gap
        quality_gap = self._detect_quality_gap(
            stimulus_id, retrieved_nodes
        )
        if quality_gap:
            gaps.append(quality_gap)
            self.gaps_detected_count[GapType.QUALITY] += 1

        # 3. Check structural gap
        if graph_context:
            structural_gap = self._detect_structural_gap(
                stimulus_id, retrieved_nodes, graph_context
            )
            if structural_gap:
                gaps.append(structural_gap)
                self.gaps_detected_count[GapType.STRUCTURAL] += 1

        # Record metrics for gate learning (even if no gap)
        # This builds history for quantile computation
        if semantic_gap:
            self.coverage_gate.record(semantic_gap.gap_metrics['embedding_coverage'])
        if quality_gap:
            self.abstraction_gate.record(quality_gap.gap_metrics['abstraction_mismatch'])
        if structural_gap:
            self.connectivity_gate.record(structural_gap.gap_metrics['node_connectivity'])

        return gaps

    def _detect_semantic_gap(
        self,
        stimulus_id: str,
        stimulus_embedding: np.ndarray,
        retrieved_nodes: List[Dict[str, Any]]
    ) -> Optional[GapSignal]:
        """
        Detect semantic gap: retrieved embeddings don't cover stimulus embedding.

        Measures: Max cosine similarity between stimulus and retrieved nodes
        Gap triggered: When max similarity is low (below Q30 of historical coverage)
        """
        # Extract embeddings from nodes
        node_embeddings = []
        for node in retrieved_nodes:
            if 'embedding' in node and node['embedding'] is not None:
                emb = node['embedding']
                if isinstance(emb, list):
                    emb = np.array(emb)
                node_embeddings.append(emb)

        if not node_embeddings:
            # No embeddings available = semantic gap
            return GapSignal(
                gap_type=GapType.SEMANTIC,
                strength=1.0,
                stimulus_id=stimulus_id,
                retrieved_node_ids=[node['id'] for node in retrieved_nodes],
                gap_metrics={'embedding_coverage': 0.0},
                context={'reason': 'no_embeddings'}
            )

        # Compute max cosine similarity (best coverage)
        similarities = []
        for node_emb in node_embeddings:
            # Cosine similarity
            cos_sim = np.dot(stimulus_embedding, node_emb) / (
                np.linalg.norm(stimulus_embedding) * np.linalg.norm(node_emb)
            )
            similarities.append(cos_sim)

        max_coverage = float(np.max(similarities))
        mean_coverage = float(np.mean(similarities))

        # Evaluate against gate
        gate_result = self.coverage_gate.evaluate(max_coverage)

        # Gap detected if:
        # 1. Coverage below absolute minimum, OR
        # 2. Coverage fails quantile gate (below Q30)
        if max_coverage < self.config.min_embedding_coverage:
            strength = 1.0 - (max_coverage / self.config.min_embedding_coverage)
        elif gate_result.status == GateStatus.FAIL:
            # Use percentile to compute strength (lower percentile = stronger gap)
            strength = 1.0 - (gate_result.percentile / 100) if gate_result.percentile else 0.5
        else:
            return None  # No gap

        return GapSignal(
            gap_type=GapType.SEMANTIC,
            strength=min(strength, 1.0),
            stimulus_id=stimulus_id,
            retrieved_node_ids=[node['id'] for node in retrieved_nodes],
            gap_metrics={
                'embedding_coverage': max_coverage,
                'mean_coverage': mean_coverage,
                'gate_status': gate_result.status.value,
                'gate_percentile': gate_result.percentile
            },
            context={
                'gate_message': gate_result.message,
                'similarities': [float(s) for s in similarities[:5]]  # Top 5 for debugging
            }
        )

    def _detect_quality_gap(
        self,
        stimulus_id: str,
        retrieved_nodes: List[Dict[str, Any]]
    ) -> Optional[GapSignal]:
        """
        Detect quality gap: retrieved nodes too abstract for concrete stimulus.

        Measures: Abstraction level mismatch
        Gap triggered: When mismatch exceeds Q70 (historically high mismatch)

        Abstraction levels (heuristic):
        - Principle, Best_Practice: Level 1 (most abstract)
        - Mechanism, Pattern: Level 2
        - Behavior, Decision: Level 3
        - Memory, Realization: Level 4 (most concrete)
        """
        # Abstraction level mapping
        abstraction_levels = {
            'Principle': 1,
            'Best_Practice': 1,
            'Mechanism': 2,
            'Pattern': 2,
            'Behavior': 3,
            'Decision': 3,
            'Memory': 4,
            'Realization': 4,
            'AI_Agent': 3,  # Operational nodes
            'Process': 3,
            'Task': 4
        }

        # Infer stimulus abstraction level from retrieved nodes
        # If stimulus retrieved mostly concrete nodes, stimulus is likely concrete
        node_levels = []
        for node in retrieved_nodes:
            node_type = node.get('type')
            if not node_type:
                labels = node.get('labels', [])
                node_type = labels[0] if labels else None
            level = abstraction_levels.get(node_type, 3)  # Default to mid-level
            node_levels.append(level)

        if not node_levels:
            return None  # Can't determine abstraction

        mean_node_level = np.mean(node_levels)
        std_node_level = np.std(node_levels)

        # High std = mixed abstraction levels = potential quality gap
        # Mean skewed toward abstract (low level) for concrete stimulus = quality gap
        abstraction_mismatch = std_node_level

        # Evaluate against gate
        gate_result = self.abstraction_gate.evaluate(abstraction_mismatch)

        # Gap detected if:
        # 1. Mismatch exceeds absolute maximum, OR
        # 2. Mismatch fails quantile gate (above Q70)
        if abstraction_mismatch > self.config.max_abstraction_mismatch:
            strength = min(abstraction_mismatch / self.config.max_abstraction_mismatch, 1.0)
        elif gate_result.status == GateStatus.FAIL:
            # Use percentile to compute strength (higher percentile = stronger gap)
            strength = (gate_result.percentile / 100) if gate_result.percentile else 0.5
        else:
            return None  # No gap

        return GapSignal(
            gap_type=GapType.QUALITY,
            strength=min(strength, 1.0),
            stimulus_id=stimulus_id,
            retrieved_node_ids=[node['id'] for node in retrieved_nodes],
            gap_metrics={
                'abstraction_mismatch': abstraction_mismatch,
                'mean_node_level': mean_node_level,
                'std_node_level': std_node_level,
                'gate_status': gate_result.status.value,
                'gate_percentile': gate_result.percentile
            },
            context={
                'gate_message': gate_result.message,
                'node_levels': node_levels[:5]  # Sample for debugging
            }
        )

    def _detect_structural_gap(
        self,
        stimulus_id: str,
        retrieved_nodes: List[Dict[str, Any]],
        graph_context: Dict[str, Any]
    ) -> Optional[GapSignal]:
        """
        Detect structural gap: retrieved nodes disconnected/sparse.

        Measures: Inter-node connectivity (density of subgraph)
        Gap triggered: When connectivity below Q30 (historically weak connectivity)
        """
        if len(retrieved_nodes) < 2:
            return None  # Need at least 2 nodes to measure connectivity

        node_ids = [node['id'] for node in retrieved_nodes]

        # Get edges between retrieved nodes from graph_context
        edges_between = graph_context.get('edges_between_retrieved', [])
        actual_edges = len(edges_between)

        # Theoretical max edges for full connectivity
        n = len(node_ids)
        max_edges = (n * (n - 1)) / 2  # Undirected graph

        # Connectivity ratio
        connectivity = actual_edges / max_edges if max_edges > 0 else 0.0

        # Evaluate against gate
        gate_result = self.connectivity_gate.evaluate(connectivity)

        # Gap detected if:
        # 1. Connectivity below absolute minimum, OR
        # 2. Connectivity fails quantile gate (below Q30)
        if connectivity < self.config.min_connectivity:
            strength = 1.0 - (connectivity / self.config.min_connectivity)
        elif gate_result.status == GateStatus.FAIL:
            # Use percentile to compute strength (lower percentile = stronger gap)
            strength = 1.0 - (gate_result.percentile / 100) if gate_result.percentile else 0.5
        else:
            return None  # No gap

        return GapSignal(
            gap_type=GapType.STRUCTURAL,
            strength=min(strength, 1.0),
            stimulus_id=stimulus_id,
            retrieved_node_ids=node_ids,
            gap_metrics={
                'node_connectivity': connectivity,
                'actual_edges': actual_edges,
                'max_edges': max_edges,
                'node_count': n,
                'gate_status': gate_result.status.value,
                'gate_percentile': gate_result.percentile
            },
            context={
                'gate_message': gate_result.message
            }
        )

    def get_telemetry(self) -> Dict[str, Any]:
        """Get telemetry data for monitoring"""
        return {
            'gaps_detected': dict(self.gaps_detected_count),
            'total_gaps': sum(self.gaps_detected_count.values()),
            'gates': {
                'coverage': self.coverage_gate.get_stats(),
                'abstraction': self.abstraction_gate.get_stats(),
                'connectivity': self.connectivity_gate.get_stats()
            }
        }
