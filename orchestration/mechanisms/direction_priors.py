"""
Direction-Aware Energy Distribution - Beta Priors for Link Matching

Implements direction-aware energy splitting using Beta distributions:
- Outgoing links: Beta(α_out, β_out) → energy flows forward
- Incoming links: Beta(β_in, α_in) → energy flows backward
- Link-matched distributions encode stronger priors

Designer: Felix "Ironhand"
Date: 2025-10-21
Reference: stimulus_injection_specification.md §3.7
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class LinkDistribution:
    """Beta distribution parameters for a link type."""
    link_type: str
    alpha: float  # Shape parameter α
    beta: float   # Shape parameter β
    direction: str  # 'outgoing' or 'incoming'


class DirectionPriorDistributor:
    """
    Distributes energy using direction-aware Beta priors.

    For matched nodes with links:
    - Outgoing links: Beta(α_out, β_out) - energy flows to target
    - Incoming links: Beta(β_in, α_in) - energy flows to source

    Returns:
    - Per-item energy deltas based on link-aware sampling
    """

    def __init__(self):
        """Initialize direction prior distributor."""

        # Default Beta parameters for common link types
        # Higher α → more energy flows in that direction
        # Higher β → less energy flows in that direction

        self.link_priors: Dict[str, Dict[str, Tuple[float, float]]] = {
            # Structural links
            'ENABLES': {
                'outgoing': (3.0, 1.0),  # Strong forward flow
                'incoming': (1.0, 3.0)   # Weak backward flow
            },
            'REQUIRES': {
                'outgoing': (2.0, 1.0),
                'incoming': (2.0, 1.0)   # Bidirectional
            },
            'BLOCKS': {
                'outgoing': (1.0, 2.0),  # Weak forward
                'incoming': (2.0, 1.0)   # Stronger backward
            },
            'EXTENDS': {
                'outgoing': (2.5, 1.0),
                'incoming': (1.5, 1.0)
            },

            # Learning links
            'LEARNED_FROM': {
                'outgoing': (2.0, 1.0),
                'incoming': (3.0, 1.0)   # Strong backward (to experience)
            },
            'DEEPENED_WITH': {
                'outgoing': (2.0, 2.0),  # Balanced bidirectional
                'incoming': (2.0, 2.0)
            },

            # Evidence links
            'JUSTIFIES': {
                'outgoing': (3.0, 1.0),
                'incoming': (1.5, 1.0)
            },
            'REFUTES': {
                'outgoing': (2.0, 1.0),
                'incoming': (1.0, 2.0)
            },

            # Activation links
            'ACTIVATES': {
                'outgoing': (3.0, 1.0),  # Strong forward
                'incoming': (1.0, 3.0)
            },
            'TRIGGERED_BY': {
                'outgoing': (1.0, 2.0),
                'incoming': (3.0, 1.0)
            },

            # Generic fallback
            'RELATES_TO': {
                'outgoing': (1.5, 1.5),  # Weak balanced
                'incoming': (1.5, 1.5)
            }
        }

        logger.info(
            f"[DirectionPriorDistributor] Initialized with "
            f"{len(self.link_priors)} link type priors"
        )

    def get_link_prior(
        self,
        link_type: str,
        direction: str
    ) -> Tuple[float, float]:
        """
        Get Beta prior parameters for link type and direction.

        Args:
            link_type: Type of link
            direction: 'outgoing' or 'incoming'

        Returns:
            (alpha, beta) parameters for Beta distribution
        """
        # Get link-specific prior or fallback to RELATES_TO
        link_params = self.link_priors.get(
            link_type,
            self.link_priors['RELATES_TO']
        )

        alpha, beta = link_params[direction]

        return (alpha, beta)

    def sample_split(
        self,
        link_type: str,
        direction: str,
        energy_to_split: float
    ) -> float:
        """
        Sample energy split from Beta distribution.

        Args:
            link_type: Type of link
            direction: 'outgoing' or 'incoming'
            energy_to_split: Total energy to distribute

        Returns:
            Energy delta for this direction
        """
        # Get Beta parameters
        alpha, beta = self.get_link_prior(link_type, direction)

        # Sample from Beta(α, β)
        split_proportion = np.random.beta(alpha, beta)

        # Apply to energy
        energy_delta = energy_to_split * split_proportion

        logger.debug(
            f"[DirectionPriorDistributor] {link_type} {direction}: "
            f"Beta({alpha}, {beta}) → {split_proportion:.3f} → Δ={energy_delta:.3f}"
        )

        return float(energy_delta)

    def distribute_via_links(
        self,
        matched_node_id: str,
        node_energy_allocation: float,
        outgoing_links: List[Dict],
        incoming_links: List[Dict]
    ) -> Dict[str, float]:
        """
        Distribute energy through links using direction priors.

        Args:
            matched_node_id: Central matched node
            node_energy_allocation: Energy allocated to this node
            outgoing_links: List of outgoing links: [{target, link_type}, ...]
            incoming_links: List of incoming links: [{source, link_type}, ...]

        Returns:
            Dict mapping node_id -> energy_delta
        """
        energy_deltas = {}

        # Split energy between node itself and links
        # Reserve 50% for node, 50% for distribution through links
        node_energy = node_energy_allocation * 0.5
        link_energy = node_energy_allocation * 0.5

        energy_deltas[matched_node_id] = node_energy

        # Count total links
        total_links = len(outgoing_links) + len(incoming_links)

        if total_links == 0:
            # No links - all energy to node
            energy_deltas[matched_node_id] = node_energy_allocation
            return energy_deltas

        # Energy per link (equal budget per link)
        energy_per_link = link_energy / total_links

        # Distribute through outgoing links
        for link in outgoing_links:
            target_id = link['target']
            link_type = link['link_type']

            # Sample split for outgoing direction
            delta = self.sample_split(link_type, 'outgoing', energy_per_link)

            if target_id not in energy_deltas:
                energy_deltas[target_id] = 0.0

            energy_deltas[target_id] += delta

        # Distribute through incoming links
        for link in incoming_links:
            source_id = link['source']
            link_type = link['link_type']

            # Sample split for incoming direction (reversed Beta)
            delta = self.sample_split(link_type, 'incoming', energy_per_link)

            if source_id not in energy_deltas:
                energy_deltas[source_id] = 0.0

            energy_deltas[source_id] += delta

        logger.debug(
            f"[DirectionPriorDistributor] Distributed {node_energy_allocation:.2f} "
            f"across {matched_node_id} + {total_links} links"
        )

        return energy_deltas

    def get_stats(self) -> dict:
        """Get current distributor statistics."""
        return {
            "link_types_configured": len(self.link_priors),
            "link_types": list(self.link_priors.keys())
        }
