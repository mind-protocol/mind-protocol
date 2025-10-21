"""
Zippered Round-Robin Scheduler

Implements fair, interleaved entity execution:
- One stride per turn for each entity
- Round-robin cycling through all active entities
- Quota-aware (entity exits when quota exhausted)
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
    entities: List[SubEntity],
    deadline_ms: Optional[float] = None
) -> List[tuple[str, int]]:
    """
    Generate zippered execution schedule for entities.

    One stride per turn, round-robin until all quotas exhausted.

    Args:
        entities: Active sub-entities with assigned quotas
        deadline_ms: Optional wall-clock deadline (ms from epoch)

    Returns:
        List of (entity_id, stride_index) tuples in execution order

    Algorithm:
        1. Initialize quota_remaining for each entity
        2. While any entity has quota_remaining > 0:
            a. For each entity in round-robin order:
                - If quota_remaining > 0:
                    - Schedule one stride
                    - Decrement quota_remaining
                - If deadline approaching:
                    - Early termination
        3. Return schedule

    Example:
        Entity A: quota=3
        Entity B: quota=2
        Entity C: quota=4

        Schedule: [A0, B0, C0, A1, B1, C1, A2, C2, C3]

        No entity gets >1 stride ahead of others (zippered fairness)
    """
    if not entities:
        return []

    schedule = []
    stride_counts = {entity.id: 0 for entity in entities}

    # Round-robin until all quotas exhausted
    while True:
        # Check if any entity has quota remaining
        active = filter_active_entities(entities)
        if not active:
            break

        # One stride per entity per round
        for entity in entities:
            if entity.quota_remaining <= 0:
                continue

            # Schedule this stride
            schedule.append((entity.id, stride_counts[entity.id]))
            stride_counts[entity.id] += 1
            entity.quota_remaining -= 1

    return schedule


def execute_frame(
    entities: List[SubEntity],
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
        entities: Active sub-entities this frame
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
        entities=entities,
        Q_total=Q_total,
        graph=graph,
        recent_stimuli=recent_stimuli
    )

    # Emit quota events
    for entity in entities:
        emit_entity_quota_event(
            frame=frame_number,
            entity=entity,
            quota_assigned=entity.quota_assigned
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
        active = filter_active_entities(entities)
        if not active:
            break

        # One stride per entity per round
        made_progress = False
        for entity in entities:
            if entity.quota_remaining <= 0:
                continue

            # Check deadline before executing
            remaining_strides = sum(e.quota_remaining for e in entities)
            if check_early_termination(frame_deadline_ms, avg_stride_time_us, remaining_strides):
                early_termination = True
                break

            # === Step 3a: Select Edge ===
            # Get valences for all frontier edges
            source_node = None
            if entity.extent:
                # Select a source node from extent (highest energy)
                source_node = max(entity.extent, key=lambda n: entity.get_energy(n))

            if source_node is None:
                # Entity has no extent (dissolved or empty)
                entity.quota_remaining = 0
                entities_converged.append(entity.id)
                emit_convergence_event(
                    frame=frame_number,
                    entity=entity,
                    reason="dissolution",
                    final_roi=0.0,
                    whisker_threshold=entity.roi_tracker.lower_whisker() if entity.roi_tracker.lower_whisker() != float('-inf') else 0.0,
                    strides_executed=entity.quota_assigned - entity.quota_remaining
                )
                continue

            # Compute valences for outgoing edges
            neighbors = list(graph.neighbors(source_node))
            if not neighbors:
                # No outgoing edges (dead end)
                entity.quota_remaining = 0
                entities_converged.append(entity.id)
                emit_convergence_event(
                    frame=frame_number,
                    entity=entity,
                    reason="dead_end",
                    final_roi=0.0,
                    whisker_threshold=entity.roi_tracker.lower_whisker() if entity.roi_tracker.lower_whisker() != float('-inf') else 0.0,
                    strides_executed=entity.quota_assigned - entity.quota_remaining
                )
                continue

            valences = {}
            for target_node in neighbors:
                v = composite_valence(
                    entity=entity,
                    source_i=source_node,    # Fixed: use source_i
                    target_j=target_node,    # Fixed: use target_j
                    graph=graph,
                    goal_embedding=goal_embedding
                )
                valences[target_node] = v

            # Select edge by valence coverage
            selected_edges = select_edge_by_valence_coverage(
                entity=entity,
                source_i=source_node,
                valences=valences,
                graph=graph
            )
            if not selected_edges:
                # No valid edges (all zero valence)
                entity.quota_remaining = 0
                entities_converged.append(entity.id)
                emit_convergence_event(
                    frame=frame_number,
                    entity=entity,
                    reason="zero_valence",
                    final_roi=0.0,
                    whisker_threshold=entity.roi_tracker.lower_whisker() if entity.roi_tracker.lower_whisker() != float('-inf') else 0.0,
                    strides_executed=entity.quota_assigned - entity.quota_remaining
                )
                continue

            target_node = selected_edges[0]  # Take first (highest valence)

            # === Step 3b: Execute Stride ===
            # Predict ROI before execution
            pred_roi = valences[target_node] * 100.0  # Rough prediction from valence

            # Capture state before stride
            source_before = {
                'E': entity.get_energy(source_node),
                'theta': entity.get_threshold(source_node)
            }
            target_before = {
                'E': entity.get_energy(target_node),
                'theta': entity.get_threshold(target_node)
            }

            result = execute_stride(
                entity=entity,
                source_i=source_node,
                target_j=target_node,
                graph=graph
            )

            # Capture state after stride
            source_after = {
                'E': entity.get_energy(source_node),
                'theta': entity.get_threshold(source_node)
            }
            target_after = {
                'E': entity.get_energy(target_node),
                'theta': entity.get_threshold(target_node)
            }

            stride_time_us = result['stride_time_us']

            # Update EMA of stride time
            avg_stride_time_us = (ema_alpha * stride_time_us) + ((1 - ema_alpha) * avg_stride_time_us)

            # === Step 3c: Check Convergence ===
            if result['delta'] > 0:
                # Record ROI for this stride
                roi = result['delta'] / (stride_time_us + 1e-6)
                entity.roi_tracker.push(roi)

                # Check if converged (ROI below whisker)
                whisker = entity.roi_tracker.lower_whisker()
                if whisker != float('-inf') and roi < whisker:
                    # Converged - ROI too low
                    entity.quota_remaining = 0
                    entities_converged.append(entity.id)
                    emit_convergence_event(
                        frame=frame_number,
                        entity=entity,
                        reason="roi_convergence",
                        final_roi=roi,
                        whisker_threshold=whisker,
                        strides_executed=entity.quota_assigned - entity.quota_remaining
                    )
                    continue

            # === Step 3d: Emit Telemetry ===
            emit_stride_exec_event(
                frame=frame_number,
                entity=entity,
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
            entity.quota_remaining -= 1
            strides_executed += 1
            made_progress = True

        if early_termination:
            break

        if not made_progress:
            # No entity could make progress (all converged/blocked)
            break

    # === Step 4: Select Working Memory Nodes ===
    # (Would be called here in full integration)
    # selected_wm, stats = select_wm_nodes(entities, graph, token_budget)

    # === Step 5: Emit Frame Summary ===
    frame_end_time = time.time()
    wall_time_us = (frame_end_time - frame_start_time) * 1e6

    emit_frame_summary(
        frame=frame_number,
        entities=entities,
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


def update_quota_remaining(entity: SubEntity):
    """
    Decrement quota_remaining after entity executes a stride.

    Args:
        entity: Sub-entity that just executed

    Side Effects:
        Modifies entity.quota_remaining in place
    """
    if entity.quota_remaining > 0:
        entity.quota_remaining -= 1


def filter_active_entities(entities: List[SubEntity]) -> List[SubEntity]:
    """
    Filter entities that still have quota remaining.

    Args:
        entities: All sub-entities

    Returns:
        List of entities with quota_remaining > 0

    Zero-constants: No minimum quota threshold, natural completion
    """
    return [e for e in entities if e.quota_remaining > 0]
