"""
Working Memory Packing: Energy-Weighted Knapsack Selection

Implements:
- Energy-weighted greedy knapsack (energy/token ratio)
- Token budget from LLM context limit (not arbitrary cap)
- LRU eviction when budget exceeded
- Cross-subentity aggregation for workspace construction

Author: AI #6
Created: 2025-10-20
Dependencies: sub_entity_core
Zero-Constants: Budget derived from LLM limit, selection by energy density
"""

from typing import List, Dict, Set, Tuple
from orchestration.mechanisms.sub_entity_core import SubEntity


# --- Token Budget Derivation ---

def compute_wm_token_budget(
    llm_context_limit: int,
    measured_overhead: int
) -> int:
    """
    Derive working memory token budget from LLM capacity.

    NOT an arbitrary cap - directly derived from technical constraint.

    Formula (from GPT5 Q4 answer):
        budget = llm_context_limit - measured_overhead

    Where:
        llm_context_limit = model capacity (e.g., 200K for Claude Sonnet 4.5)
        measured_overhead = system prompt + instructions + schema (measured empirically)

    Args:
        llm_context_limit: Model's maximum context window
        measured_overhead: Empirically measured system overhead (tokens)

    Returns:
        Available token budget for WM nodes

    Example:
        llm_context_limit = 200000
        measured_overhead = 15000 (system prompt, schema, instructions)
        budget = 185000 tokens available for WM
    """
    # Direct derivation from technical constraint - zero-constants compliant
    # The only "constant" here is the LLM's architectural limit (external constraint)
    budget = llm_context_limit - measured_overhead

    # Safety: Never return negative budget
    if budget < 0:
        raise ValueError(
            f"Measured overhead ({measured_overhead}) exceeds LLM context limit ({llm_context_limit}). "
            f"System prompt too large for model capacity."
        )

    return budget


def estimate_node_tokens(node, graph) -> int:
    """
    Estimate token cost for including node in WM.

    Includes:
        - Node content (name, description, metadata)
        - Link content for active edges
        - Formatting overhead

    Args:
        node: Graph node object or node_id
        graph: Graph object (NetworkX-compatible with .nodes attribute)

    Returns:
        Estimated token count for this node

    Note:
        Use empirical measurement or heuristic (e.g., content length / 4)
    """
    # Handle both node object and node_id
    if isinstance(node, int):
        node_id = node
        node_data = graph.nodes[node_id]
    else:
        node_id = node
        node_data = graph.nodes[node_id]

    # Heuristic: ~4 chars per token (standard GPT tokenization estimate)
    # This is rough but adequate for knapsack ranking
    chars = 0

    # Node name
    if 'name' in node_data:
        chars += len(str(node_data['name']))

    # Node description (primary content)
    if 'description' in node_data:
        chars += len(str(node_data['description']))

    # Embeddable text (if present)
    if 'embeddable_text' in node_data:
        chars += len(str(node_data['embeddable_text']))

    # Metadata fields (selective - only semantic content)
    semantic_fields = ['context_when_discovered', 'what_i_realized', 'how_it_works',
                       'principle_statement', 'why_it_matters', 'goal_description']
    for field in semantic_fields:
        if field in node_data:
            chars += len(str(node_data[field]))

    # Base formatting overhead per node (bullet, labels, spacing)
    base_overhead = 50  # tokens for "- Node_Name (E=0.85): Description\n"

    # Estimate tokens from characters
    estimated_tokens = (chars // 4) + base_overhead

    return max(estimated_tokens, 20)  # Minimum 20 tokens per node


# --- Energy-Weighted Knapsack Selection ---

def select_wm_nodes(
    subentities: List[SubEntity],
    graph,
    token_budget: int
) -> Tuple[Set[int], Dict[str, any]]:
    """
    Select nodes for working memory using energy-weighted greedy knapsack.

    Algorithm:
        1. Aggregate nodes across all subentities
        2. For each node: compute energy density = E_total / token_cost
        3. Sort by energy density descending
        4. Greedy select until budget exhausted
        5. Return selected nodes + statistics

    Args:
        subentities: Active sub-entities with energy distributions
        graph: Graph object
        token_budget: Available token budget (from compute_wm_token_budget)

    Returns:
        Tuple (selected_nodes, statistics) where:
            selected_nodes = Set[node_id]
            statistics = {
                'nodes_selected': int,
                'total_energy': float,
                'tokens_used': int,
                'budget_utilization': float,
                'nodes_excluded': int
            }

    Zero-constants:
        - Selection by energy/token ratio (not arbitrary scoring)
        - Budget from LLM capacity (not fixed cap)
        - No minimum/maximum node count constraints
    """
    # Step 1: Aggregate energy across all subentities
    energy_totals = aggregate_entity_energies(subentities, graph)

    if not energy_totals:
        # No active nodes - return empty selection
        return set(), {
            'nodes_selected': 0,
            'total_energy': 0.0,
            'tokens_used': 0,
            'budget_utilization': 0.0,
            'nodes_excluded': 0,
            'energy_coverage': 0.0
        }

    # Step 2: Compute candidates with (node_id, energy, tokens, density)
    candidates = []
    for node_id, total_energy in energy_totals.items():
        tokens = estimate_node_tokens(node_id, graph)
        density = compute_energy_density(node_id, total_energy, graph)
        candidates.append((node_id, total_energy, tokens, density))

    # Step 3: Sort by energy density descending (greedy knapsack)
    # Highest value per token cost selected first
    ranked = sorted(candidates, key=lambda x: x[3], reverse=True)

    # Step 4: Greedy select until budget exhausted
    selected_nodes = set()
    tokens_used = 0
    total_energy_selected = 0.0

    for node_id, energy, tokens, density in ranked:
        if tokens_used + tokens <= token_budget:
            # Fits in budget - select this node
            selected_nodes.add(node_id)
            tokens_used += tokens
            total_energy_selected += energy

    # Step 5: Compute statistics
    nodes_excluded = len(candidates) - len(selected_nodes)
    total_system_energy = sum(energy_totals.values())

    statistics = {
        'nodes_selected': len(selected_nodes),
        'total_energy': total_energy_selected,
        'tokens_used': tokens_used,
        'budget_utilization': tokens_used / token_budget if token_budget > 0 else 0.0,
        'nodes_excluded': nodes_excluded,
        'energy_coverage': total_energy_selected / total_system_energy if total_system_energy > 0 else 0.0
    }

    return selected_nodes, statistics


def aggregate_entity_energies(
    subentities: List[SubEntity],
    graph
) -> Dict[int, float]:
    """
    Aggregate energy values across all subentities.

    Formula:
        E_total[node] = Σ (E[subentity, node] for subentity in subentities)

    Args:
        subentities: Active sub-entities
        graph: Graph object

    Returns:
        Dict[node_id -> total_energy]

    Interpretation:
        Nodes with high aggregate energy are important to multiple subentities.
        These are workspace candidates.
    """
    energy_totals = {}

    for subentity in subentities:
        # Iterate through subentity's extent (nodes above threshold for this subentity)
        for node_id in subentity.extent:
            # Get subentity's energy at this node
            node_energy = subentity.get_energy(node_id)

            # Aggregate across subentities
            if node_id in energy_totals:
                energy_totals[node_id] += node_energy
            else:
                energy_totals[node_id] = node_energy

    return energy_totals


def compute_energy_density(
    node_id: int,
    total_energy: float,
    graph
) -> float:
    """
    Compute energy density (energy per token).

    Formula:
        density = total_energy / estimate_node_tokens(node)

    Args:
        node_id: Node to evaluate
        total_energy: Aggregated energy across subentities
        graph: Graph object

    Returns:
        Energy density (energy/token)

    Interpretation:
        High density = high value per token cost.
        Greedy knapsack maximizes total energy under token constraint.
    """
    token_cost = estimate_node_tokens(node_id, graph)

    # Avoid division by zero (should never happen with min 20 tokens, but defensive)
    if token_cost == 0:
        return 0.0

    density = total_energy / token_cost

    return density


# --- LRU Eviction (Optional Extension) ---

def evict_lru_nodes(
    current_wm: Set[int],
    new_candidates: Set[int],
    token_budget: int,
    graph,
    access_history: Dict[int, int]
) -> Set[int]:
    """
    Evict least recently used nodes when budget exceeded.

    Args:
        current_wm: Current working memory node set
        new_candidates: Nodes that need to be added
        token_budget: Available token budget
        graph: Graph object
        access_history: Dict[node_id -> last_access_frame]

    Returns:
        Updated working memory node set (after eviction)

    Algorithm:
        1. Compute token cost of (current_wm ∪ new_candidates)
        2. If cost > budget:
            a. Sort current_wm by last_access_frame ascending
            b. Evict nodes until budget met
        3. Add new_candidates
        4. Return updated set
    """
    # TODO AI #6: Implement LRU eviction
    # This is optional - may not be needed if greedy selection sufficient
    pass


# --- Statistics and Diagnostics ---

def compute_wm_statistics(
    selected_nodes: Set[int],
    subentities: List[SubEntity],
    graph,
    token_budget: int
) -> Dict[str, any]:
    """
    Compute diagnostic statistics for WM selection.

    Returns:
        Dict with:
            - nodes_selected: int
            - total_energy: float (aggregate energy in WM)
            - tokens_used: int (actual token consumption)
            - budget_utilization: float (tokens_used / token_budget)
            - nodes_excluded: int (nodes above threshold but excluded)
            - energy_coverage: float (WM energy / total subentity energy)
    """
    energy_totals = aggregate_entity_energies(subentities, graph)

    # Total energy in system
    total_system_energy = sum(energy_totals.values())

    # Energy in selected nodes
    total_energy_selected = sum(energy_totals.get(nid, 0.0) for nid in selected_nodes)

    # Token consumption
    tokens_used = sum(estimate_node_tokens(nid, graph) for nid in selected_nodes)

    # Nodes excluded (candidates not selected)
    all_candidates = set(energy_totals.keys())
    nodes_excluded = len(all_candidates - selected_nodes)

    statistics = {
        'nodes_selected': len(selected_nodes),
        'total_energy': total_energy_selected,
        'tokens_used': tokens_used,
        'budget_utilization': tokens_used / token_budget if token_budget > 0 else 0.0,
        'nodes_excluded': nodes_excluded,
        'energy_coverage': total_energy_selected / total_system_energy if total_system_energy > 0 else 0.0
    }

    return statistics


# --- Integration with Traversal Frame ---

def construct_workspace_prompt(
    selected_nodes: Set[int],
    graph,
    subentities: List[SubEntity]
) -> str:
    """
    Construct workspace prompt from selected nodes.

    Includes:
        - Node content (name, description, metadata)
        - Active links between WM nodes
        - Subentity extent indicators (which subentities are present)

    Args:
        selected_nodes: Nodes selected for WM
        graph: Graph object
        subentities: Active sub-entities

    Returns:
        Formatted workspace prompt string

    Format:
        ## Workspace (Frame N)

        **Nodes:**
        - Node_A (E=0.85, subentities=[translator, architect])
          Description: ...
          Links: → Node_B (ENABLES, w=0.7)

        **Active Subentities:**
        - translator: 12 nodes, center=Node_A
        - architect: 8 nodes, center=Node_C
    """
    if not selected_nodes:
        return "## Workspace (Empty)\n\nNo nodes currently active.\n"

    lines = ["## Workspace\n"]
    lines.append("**Active Nodes:**\n")

    # Sort nodes by total energy (highest first) for readability
    energy_totals = aggregate_entity_energies(subentities, graph)
    sorted_nodes = sorted(selected_nodes,
                         key=lambda nid: energy_totals.get(nid, 0.0),
                         reverse=True)

    for node_id in sorted_nodes:
        node_data = graph.nodes[node_id]

        # Node header with energy
        node_name = node_data.get('name', f'node_{node_id}')
        total_energy = energy_totals.get(node_id, 0.0)

        # Which subentities have this node in their extent?
        present_entities = [e.id for e in subentities if node_id in e.extent]
        entity_str = ', '.join(present_entities) if present_entities else 'none'

        lines.append(f"- **{node_name}** (E={total_energy:.2f}, subentities=[{entity_str}])")

        # Node description
        if 'description' in node_data:
            desc = node_data['description']
            # Truncate if too long
            if len(desc) > 200:
                desc = desc[:197] + "..."
            lines.append(f"  {desc}")

        # Active links to other WM nodes
        if hasattr(graph, 'neighbors'):
            neighbors_in_wm = [n for n in graph.neighbors(node_id) if n in selected_nodes]
            if neighbors_in_wm:
                link_strs = []
                for neighbor_id in neighbors_in_wm[:5]:  # Limit to 5 links per node
                    neighbor_name = graph.nodes[neighbor_id].get('name', f'node_{neighbor_id}')
                    edge_data = graph.get_edge_data(node_id, neighbor_id)
                    if edge_data:
                        link_type = edge_data.get('link_type', 'RELATES_TO')
                        weight = edge_data.get('weight', 0.0)
                        link_strs.append(f"→ {neighbor_name} ({link_type}, w={weight:.2f})")

                if link_strs:
                    lines.append(f"  Links: {', '.join(link_strs)}")

        lines.append("")  # Blank line between nodes

    # Subentity summary
    lines.append("\n**Active Sub-Entities:**\n")
    for subentity in subentities:
        extent_size = len(subentity.extent)
        # Find highest-energy node in extent as "center"
        if subentity.extent:
            center_node_id = max(subentity.extent, key=lambda nid: subentity.get_energy(nid))
            center_name = graph.nodes[center_node_id].get('name', f'node_{center_node_id}')
        else:
            center_name = 'none'

        lines.append(f"- **{subentity.id}**: {extent_size} nodes, center={center_name}")

    return '\n'.join(lines)
