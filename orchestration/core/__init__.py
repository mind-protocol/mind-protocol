"""
Core data structures for consciousness engine.

This package provides the fundamental data types:
- Node: Graph nodes with multi-energy + bitemporal tracking
- Link: Directed relationships with bitemporal tracking
- Entity: Multi-scale consciousness neighborhoods (Phase 7)
- Graph: Container for nodes, entities, and links

These are PURE DATA STRUCTURES - no mechanism logic.
All behavior is implemented in mechanisms/ and services/ packages.

Author: Felix (Engineer)
Created: 2025-10-19
Architecture: Phase 1 Clean Break + Phase 7 Multi-Scale
"""

from .node import Node
from .link import Link
from .entity import Entity
from .graph import Graph
from .types import NodeType, LinkType

__all__ = ['Node', 'Link', 'Entity', 'Graph', 'NodeType', 'LinkType']
