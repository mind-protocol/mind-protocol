"""
SubEntity Coalition Assembler - Node Coalition Formation

Takes gap signals and assembles coherent node coalitions for emergence.

Algorithm: Seed → Expand → Prune
1. Seed: Start with retrieved nodes + stimulus context
2. Expand: Add neighbor nodes via graph traversal (density-guided)
3. Prune: Remove weak nodes (low internal connectivity)

Author: Felix (Core Consciousness Engineer)
Date: 2025-10-29
Spec: docs/specs/v2/subentity_layer/subentity_emergence_orchestration.md §3.2
"""

import time
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

from orchestration.mechanisms.subentity_gap_detector import GapSignal, GapType
from orchestration.mechanisms.quantile_gate import QuantileGate, QuantileConfig, ComparisonMode


@dataclass
class NodeCandidate:
    """Candidate node for coalition"""
    node_id: str
    score: float                    # Relevance score for inclusion
    source: str                     # How node was added ("seed", "expand", "neighbor")
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Coalition:
    """Assembled node coalition"""
    nodes: List[NodeCandidate]
    seed_node_ids: List[str]                # Initial seed nodes
    density: float                          # Internal connectivity
    coherence: float                        # Semantic coherence
    gap_signal: GapSignal                   # Original gap that triggered formation
    formation_timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoalitionAssemblyConfig:
    """Configuration for coalition assembly"""
    # Expansion parameters
    max_expansion_hops: int = 2             # How far to traverse from seed
    expansion_branching_factor: int = 5     # Max neighbors per node
    min_edge_weight: float = 0.3            # Minimum relationship strength

    # Density thresholds
    min_coalition_density: float = 0.4      # Minimum internal connectivity
    density_percentile_gate: float = 0.70   # Must exceed Q70 for quality

    # Size constraints
    min_coalition_size: int = 3             # Minimum nodes
    max_coalition_size: int = 50            # Maximum nodes
    target_coalition_size: int = 12         # Ideal size

    # Pruning parameters
    prune_weak_nodes: bool = True
    weak_node_threshold: float = 0.5        # Nodes with score < this are weak

    # Gate configuration
    min_samples_for_gates: int = 30
    history_window: int = 1000


class SubEntityCoalitionAssembler:
    """
    Assembles coherent node coalitions from gap signals.

    Uses density-guided expansion to grow coalitions from seed nodes,
    then prunes weak connections to maintain coherence.
    """

    def __init__(self, config: Optional[CoalitionAssemblyConfig] = None):
        self.config = config or CoalitionAssemblyConfig()

        # Quantile gate for density quality
        self.density_gate = QuantileGate(QuantileConfig(
            metric_name="coalition_density",
            quantile_level=self.config.density_percentile_gate,
            comparison_mode=ComparisonMode.ABOVE,  # Density must exceed Q70
            min_samples=self.config.min_samples_for_gates,
            window_size=self.config.history_window
        ))

        # Telemetry
        self.coalitions_formed: int = 0
        self.coalitions_rejected: int = 0

    def assemble_coalition(
        self,
        gap_signal: GapSignal,
        graph_accessor,
        stimulus_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Coalition]:
        """
        Assemble a coalition from gap signal.

        Args:
            gap_signal: Gap detection result
            graph_accessor: Object with methods: get_node(id), get_neighbors(id), get_edge(src, dst)
            stimulus_context: Optional stimulus information

        Returns:
            Coalition if successful, None if assembly failed
        """
        # Step 1: Seed - start with retrieved nodes
        seed_nodes = self._initialize_seed(gap_signal, graph_accessor)
        if not seed_nodes:
            self.coalitions_rejected += 1
            return None

        # Step 2: Expand - grow coalition via graph traversal
        expanded_nodes = self._expand_coalition(seed_nodes, graph_accessor)

        # Step 3: Prune - remove weak nodes
        if self.config.prune_weak_nodes:
            pruned_nodes = self._prune_weak_nodes(expanded_nodes, graph_accessor)
        else:
            pruned_nodes = expanded_nodes

        # Validate final coalition
        if len(pruned_nodes) < self.config.min_coalition_size:
            self.coalitions_rejected += 1
            return None

        if len(pruned_nodes) > self.config.max_coalition_size:
            # Trim to max size (keep highest scoring nodes)
            pruned_nodes = sorted(pruned_nodes, key=lambda n: n.score, reverse=True)[:self.config.max_coalition_size]

        # Compute coalition metrics
        density = self._compute_density(pruned_nodes, graph_accessor)
        coherence = self._compute_coherence(pruned_nodes, graph_accessor)

        # Check density gate
        gate_result = self.density_gate.evaluate(density)
        if gate_result.status.value == "fail":
            self.coalitions_rejected += 1
            return None

        # Record successful density for gate learning
        self.density_gate.record(density)

        coalition = Coalition(
            nodes=pruned_nodes,
            seed_node_ids=[n.node_id for n in seed_nodes],
            density=density,
            coherence=coherence,
            gap_signal=gap_signal,
            metadata={
                'seed_count': len(seed_nodes),
                'expanded_count': len(expanded_nodes),
                'final_count': len(pruned_nodes),
                'density_gate_result': gate_result.message,
                'density_percentile': gate_result.percentile
            }
        )

        self.coalitions_formed += 1
        return coalition

    def _initialize_seed(
        self,
        gap_signal: GapSignal,
        graph_accessor
    ) -> List[NodeCandidate]:
        """Initialize seed nodes from gap signal"""
        seed_nodes = []

        for node_id in gap_signal.retrieved_node_ids:
            try:
                node_data = graph_accessor.get_node(node_id)
                if node_data:
                    # Convert Node object to dict for properties
                    node_props = {
                        'type': getattr(node_data, 'node_type', None),
                        'labels': getattr(node_data, 'labels', []),
                        'description': getattr(node_data, 'description', ''),
                        'embedding': getattr(node_data, 'embedding', None),
                        'energy': getattr(node_data, 'E', 0.0)
                    }
                    seed_nodes.append(NodeCandidate(
                        node_id=node_id,
                        score=1.0,  # Seed nodes start with max score
                        source="seed",
                        properties=node_props
                    ))
            except Exception as e:
                continue  # Skip nodes that fail to load

        return seed_nodes

    def _expand_coalition(
        self,
        seed_nodes: List[NodeCandidate],
        graph_accessor
    ) -> List[NodeCandidate]:
        """
        Expand coalition via graph traversal.

        Uses BFS with density-guided selection:
        - Prioritize neighbors with strong connections to existing coalition
        - Stop when target size reached or no more high-quality neighbors
        """
        coalition_nodes = {n.node_id: n for n in seed_nodes}
        frontier = list(seed_nodes)
        visited = set(coalition_nodes.keys())

        for hop in range(self.config.max_expansion_hops):
            if len(coalition_nodes) >= self.config.target_coalition_size:
                break

            next_frontier = []

            for node in frontier:
                # Get neighbors
                try:
                    neighbors = graph_accessor.get_neighbors(node.node_id, limit=self.config.expansion_branching_factor)
                except Exception:
                    continue

                for neighbor_id, edge_weight in neighbors:
                    if neighbor_id in visited:
                        continue

                    if edge_weight < self.config.min_edge_weight:
                        continue

                    # Compute score: how well does this neighbor connect to coalition?
                    neighbor_score = self._compute_neighbor_score(
                        neighbor_id, coalition_nodes, graph_accessor
                    )

                    if neighbor_score > 0:
                        try:
                            neighbor_data = graph_accessor.get_node(neighbor_id)
                            # Convert Node object to dict for properties
                            neighbor_props = {}
                            if neighbor_data:
                                neighbor_props = {
                                    'type': getattr(neighbor_data, 'node_type', None),
                                    'labels': getattr(neighbor_data, 'labels', []),
                                    'description': getattr(neighbor_data, 'description', ''),
                                    'embedding': getattr(neighbor_data, 'embedding', None),
                                    'energy': getattr(neighbor_data, 'E', 0.0)
                                }
                            candidate = NodeCandidate(
                                node_id=neighbor_id,
                                score=neighbor_score,
                                source=f"expand_hop_{hop+1}",
                                properties=neighbor_props
                            )
                            coalition_nodes[neighbor_id] = candidate
                            next_frontier.append(candidate)
                            visited.add(neighbor_id)

                            if len(coalition_nodes) >= self.config.max_coalition_size:
                                break
                        except Exception:
                            continue

                if len(coalition_nodes) >= self.config.max_coalition_size:
                    break

            frontier = next_frontier

            if not frontier:
                break  # No more neighbors to explore

        return list(coalition_nodes.values())

    def _compute_neighbor_score(
        self,
        neighbor_id: str,
        coalition_nodes: Dict[str, NodeCandidate],
        graph_accessor
    ) -> float:
        """
        Compute score for adding neighbor to coalition.

        Score = average edge weight to existing coalition members
        """
        edge_weights = []

        for coalition_node_id in coalition_nodes.keys():
            try:
                edge = graph_accessor.get_edge(neighbor_id, coalition_node_id)
                if edge and 'weight' in edge:
                    edge_weights.append(edge['weight'])
            except Exception:
                continue

        if not edge_weights:
            return 0.0

        return float(np.mean(edge_weights))

    def _prune_weak_nodes(
        self,
        nodes: List[NodeCandidate],
        graph_accessor
    ) -> List[NodeCandidate]:
        """
        Prune nodes with weak connections to coalition.

        Removes nodes with:
        - Score below weak_node_threshold
        - Low connectivity to other members
        """
        if len(nodes) <= self.config.min_coalition_size:
            return nodes  # Don't prune if at minimum size

        # Compute connectivity for each node
        node_connectivity = {}
        node_map = {n.node_id: n for n in nodes}

        for node in nodes:
            # Count edges to other coalition members
            edges_to_coalition = 0
            for other_node in nodes:
                if node.node_id == other_node.node_id:
                    continue
                try:
                    edge = graph_accessor.get_edge(node.node_id, other_node.node_id)
                    if edge:
                        edges_to_coalition += 1
                except Exception:
                    continue

            max_possible_edges = len(nodes) - 1
            connectivity = edges_to_coalition / max_possible_edges if max_possible_edges > 0 else 0.0
            node_connectivity[node.node_id] = connectivity

        # Prune nodes with low score AND low connectivity
        pruned_nodes = []
        for node in nodes:
            connectivity = node_connectivity.get(node.node_id, 0.0)

            # Keep node if:
            # - Score above threshold, OR
            # - Connectivity above average
            avg_connectivity = np.mean(list(node_connectivity.values()))
            if node.score >= self.config.weak_node_threshold or connectivity >= avg_connectivity:
                pruned_nodes.append(node)

        # Ensure minimum size
        if len(pruned_nodes) < self.config.min_coalition_size:
            # Keep highest scoring nodes to meet minimum
            sorted_nodes = sorted(nodes, key=lambda n: n.score, reverse=True)
            pruned_nodes = sorted_nodes[:self.config.min_coalition_size]

        return pruned_nodes

    def _compute_density(
        self,
        nodes: List[NodeCandidate],
        graph_accessor
    ) -> float:
        """
        Compute internal density of coalition.

        Density = actual_edges / max_possible_edges
        """
        if len(nodes) < 2:
            return 0.0

        node_ids = [n.node_id for n in nodes]
        actual_edges = 0

        for i, node_id_1 in enumerate(node_ids):
            for node_id_2 in node_ids[i+1:]:
                try:
                    edge = graph_accessor.get_edge(node_id_1, node_id_2)
                    if edge:
                        actual_edges += 1
                except Exception:
                    continue

        max_edges = (len(nodes) * (len(nodes) - 1)) / 2
        density = actual_edges / max_edges if max_edges > 0 else 0.0

        return float(density)

    def _compute_coherence(
        self,
        nodes: List[NodeCandidate],
        graph_accessor
    ) -> float:
        """
        Compute semantic coherence of coalition.

        For now, use a simple heuristic based on node type diversity.
        Lower diversity = higher coherence.

        Future: Use embedding similarity.
        """
        if not nodes:
            return 0.0

        # Count unique node types
        node_types = set()
        for node in nodes:
            node_type = node.properties.get('type') or node.properties.get('labels', [None])[0]
            if node_type:
                node_types.add(node_type)

        # Coherence inversely related to type diversity
        type_diversity = len(node_types) / len(nodes) if nodes else 1.0
        coherence = 1.0 - type_diversity

        return float(coherence)

    def get_telemetry(self) -> Dict[str, Any]:
        """Get telemetry data for monitoring"""
        return {
            'coalitions_formed': self.coalitions_formed,
            'coalitions_rejected': self.coalitions_rejected,
            'success_rate': self.coalitions_formed / (self.coalitions_formed + self.coalitions_rejected)
                if (self.coalitions_formed + self.coalitions_rejected) > 0 else 0.0,
            'density_gate': self.density_gate.get_stats()
        }
