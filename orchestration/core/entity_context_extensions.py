"""
Entity Context Extensions - Schema additions for dual-view weight architecture.

Adds entity-specific weight overlays to Node and Link for context-aware learning.

Architecture (per Nicolas's PR-4 design):
- Global weight: log_weight (single float)
- Entity overlays: log_weight_overlays (sparse dict {entity_id: delta})
- Effective weight for entity E = global + overlay@E
- 80/20 TRACE split: 80% to active entity overlays, 20% to global

Author: Felix (Engineer)
Date: 2025-10-25
Reference: Nicolas's Priority 4 architecture guide (2025-10-25)
"""

from typing import Dict

# Schema extensions to add to Node class:
NODE_SCHEMA_ADDITIONS = """
    # Entity-specific weight overlays (sparse: {entity_id: delta})
    # Effective weight for entity E = log_weight + log_weight_overlays.get(E, 0.0)
    # Updated by TRACE marks with entity_context (80% local, 20% global)
    log_weight_overlays: Dict[str, float] = field(default_factory=dict)
"""

# Schema extensions to add to Link class:
LINK_SCHEMA_ADDITIONS = """
    # Entity-specific weight overlays (sparse: {entity_id: delta})
    # Effective weight for entity E = log_weight + log_weight_overlays.get(E, 0.0)
    # Updated by TRACE marks with entity_context (80% local, 20% global)
    log_weight_overlays: Dict[str, float] = field(default_factory=dict)
"""

# Helper functions for effective weight computation:

def effective_log_weight_node(node, entity_id: str) -> float:
    """
    Compute effective log weight for node in entity context.

    Args:
        node: Node instance
        entity_id: Entity viewing this node

    Returns:
        Global weight + entity-specific overlay
    """
    global_weight = node.log_weight
    overlay = node.log_weight_overlays.get(entity_id, 0.0)
    return global_weight + overlay


def effective_log_weight_link(link, entity_id: str) -> float:
    """
    Compute effective log weight for link in entity context.

    Args:
        link: Link instance
        entity_id: Entity viewing this link

    Returns:
        Global weight + entity-specific overlay
    """
    global_weight = link.log_weight
    overlay = link.log_weight_overlays.get(entity_id, 0.0)
    return global_weight + overlay


def effective_weight_node(node, entity_id: str) -> float:
    """
    Compute effective weight (linear space) for node in entity context.

    Args:
        node: Node instance
        entity_id: Entity viewing this node

    Returns:
        exp(effective_log_weight)
    """
    import math
    log_w = effective_log_weight_node(node, entity_id)
    return math.exp(log_w)


def effective_weight_link(link, entity_id: str) -> float:
    """
    Compute effective weight (linear space) for link in entity context.

    Args:
        link: Link instance
        entity_id: Entity viewing this link

    Returns:
        exp(effective_log_weight)
    """
    import math
    log_w = effective_log_weight_link(link, entity_id)
    return math.exp(log_w)


# Integration notes:
# 1. Add NODE_SCHEMA_ADDITIONS to Node class (after log_weight field)
# 2. Add LINK_SCHEMA_ADDITIONS to Link class (after log_weight field)
# 3. Import these helpers in WeightLearner for dual-view updates
# 4. Import these helpers in traversal/WM code for entity-aware selection
# 5. Update FalkorDB serialization to persist log_weight_overlays (JSON field)
