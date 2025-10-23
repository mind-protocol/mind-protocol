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
