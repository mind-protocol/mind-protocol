"""
Entity Context Integration for TRACE Capture - Priority 4 Implementation

Provides entity context derivation and membership querying for context-aware
weight learning.

Usage:
    1. Add entity_context_manager to TraceCapture.__init__()
    2. Call derive_entity_context() before weight learning
    3. Pass entity_context to WeightLearnerV2.update_node_weights()

Author: Felix (Engineer)
Date: 2025-10-25
Reference: ENTITY_CONTEXT_TRACE_DESIGN.md Section D
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class EntityContextManager:
    """
    Manages entity context derivation for TRACE reinforcement.

    Implements priority logic from spec:
    1. Primary: WM selected entities
    2. Secondary: Explicit TRACE annotations
    3. Fallback: Dominant entity
    """

    def __init__(self, graph_store):
        """
        Initialize entity context manager.

        Args:
            graph_store: FalkorDBGraphStore for querying entities
        """
        self.graph_store = graph_store
        self.last_wm_entities = []  # Cache from last WM emit
        self.last_update_time = None

    def derive_entity_context(
        self,
        wm_entities: Optional[List[str]] = None,
        trace_annotations: Optional[List[str]] = None,
        graph_name: str = "citizen_felix"
    ) -> List[str]:
        """
        Derive entity context for TRACE reinforcement.

        Priority order (per spec Section D):
        1. wm_entities (from wm.emit.selected_entities)
        2. trace_annotations (explicit [entity: X] marks in TRACE)
        3. Dominant entity (highest energy/threshold ratio)

        Args:
            wm_entities: Entity IDs from working memory selection
            trace_annotations: Entity IDs from explicit TRACE annotations
            graph_name: Graph to query for dominant entity

        Returns:
            List of entity IDs to attribute TRACE to
        """
        # Priority 1: WM selected entities
        if wm_entities and len(wm_entities) > 0:
            logger.debug(f"[EntityContext] Using WM entities: {wm_entities}")
            self.last_wm_entities = wm_entities
            self.last_update_time = datetime.now()
            return wm_entities

        # Priority 2: Explicit TRACE annotations
        if trace_annotations and len(trace_annotations) > 0:
            logger.debug(f"[EntityContext] Using TRACE annotations: {trace_annotations}")
            return trace_annotations

        # Priority 3: Fallback to dominant entity
        dominant = self._get_dominant_entity(graph_name)
        if dominant:
            logger.debug(f"[EntityContext] Using dominant entity: {dominant}")
            return [dominant]

        # No context available - use cached WM entities if recent
        if self.last_wm_entities and self.last_update_time:
            age = (datetime.now() - self.last_update_time).total_seconds()
            if age < 60.0:  # Within last minute
                logger.debug(f"[EntityContext] Using cached WM entities: {self.last_wm_entities}")
                return self.last_wm_entities

        # Absolute fallback: empty context (global learning only)
        logger.warning("[EntityContext] No entity context available - using global learning only")
        return []

    def _get_dominant_entity(self, graph_name: str) -> Optional[str]:
        """
        Find dominant entity (highest energy/threshold ratio).

        Args:
            graph_name: Graph to query

        Returns:
            Entity ID with highest activation ratio, or None
        """
        try:
            # Query entities with energy and threshold
            query = """
            MATCH (e:Subentity)
            WHERE e.energy_runtime IS NOT NULL
              AND e.threshold_runtime IS NOT NULL
              AND e.threshold_runtime > 0
            RETURN e.id as entity_id,
                   e.energy_runtime as energy,
                   e.threshold_runtime as threshold,
                   (e.energy_runtime / e.threshold_runtime) as ratio
            ORDER BY ratio DESC
            LIMIT 1
            """

            # Switch to correct graph
            self.graph_store.switch_graph(graph_name)
            result = self.graph_store.query(query)

            if result and len(result) > 0:
                row = result[0]
                entity_id = row[0]  # entity_id
                ratio = row[3]  # ratio

                if ratio > 1.0:  # Only return if actually active
                    logger.debug(f"[EntityContext] Dominant entity: {entity_id} (ratio={ratio:.2f})")
                    return entity_id

        except Exception as e:
            logger.warning(f"[EntityContext] Failed to query dominant entity: {e}")

        return None

    def update_from_wm_event(self, wm_event: Dict[str, Any]):
        """
        Update entity context from wm.emit event.

        Call this when wm.emit event is received to keep context current.

        Args:
            wm_event: Working memory emit event
        """
        if wm_event.get('kind') == 'wm.emit':
            selected_entities = wm_event.get('selected_entities', [])
            if selected_entities:
                self.last_wm_entities = selected_entities
                self.last_update_time = datetime.now()
                logger.debug(f"[EntityContext] Updated from WM event: {selected_entities}")


class MembershipQueryHelper:
    """
    Helper for querying BELONGS_TO memberships from graph.

    Provides membership weights for entity-localized learning.
    """

    def __init__(self, graph_store):
        """
        Initialize membership query helper.

        Args:
            graph_store: FalkorDBGraphStore for querying
        """
        self.graph_store = graph_store

    def get_node_memberships(
        self,
        node_ids: List[str],
        entity_ids: List[str],
        graph_name: str
    ) -> Dict[str, Dict[str, float]]:
        """
        Query BELONGS_TO memberships for nodes in entity contexts.

        Args:
            node_ids: Node IDs to query memberships for
            entity_ids: Entity IDs to filter by
            graph_name: Graph to query

        Returns:
            Dict[node_id, Dict[entity_id, membership_weight]]
        """
        if not node_ids or not entity_ids:
            return {}

        memberships = {}

        try:
            # Switch to correct graph
            self.graph_store.switch_graph(graph_name)

            # Build query for all node-entity pairs
            # Use parameterized query to avoid Cypher injection
            query = """
            UNWIND $node_ids AS node_id
            UNWIND $entity_ids AS entity_id
            MATCH (n {name: node_id})-[r:BELONGS_TO]->(e:Subentity {id: entity_id})
            RETURN n.name as node_id,
                   e.id as entity_id,
                   r.weight as weight
            """

            params = {
                'node_ids': node_ids,
                'entity_ids': entity_ids
            }

            result = self.graph_store.query(query, params)

            if result and len(result) > 0:
                for row in result:
                    node_id = row[0]
                    entity_id = row[1]
                    weight = float(row[2]) if row[2] is not None else 0.0

                    if node_id not in memberships:
                        memberships[node_id] = {}
                    memberships[node_id][entity_id] = weight

            logger.debug(f"[Membership] Queried {len(memberships)} nodes with memberships")

        except Exception as e:
            logger.error(f"[Membership] Failed to query memberships: {e}")

        return memberships

    def get_link_memberships(
        self,
        link_ids: List[str],
        entity_ids: List[str],
        graph_name: str
    ) -> Dict[str, Dict[str, float]]:
        """
        Compute link memberships from source/target node memberships.

        Link membership = min(source_membership, target_membership)

        Args:
            link_ids: Link IDs to compute memberships for
            entity_ids: Entity IDs to filter by
            graph_name: Graph to query

        Returns:
            Dict[link_id, Dict[entity_id, membership_weight]]
        """
        if not link_ids or not entity_ids:
            return {}

        memberships = {}

        try:
            # Switch to correct graph
            self.graph_store.switch_graph(graph_name)

            # Query links with source/target memberships
            query = """
            UNWIND $link_ids AS link_id
            UNWIND $entity_ids AS entity_id
            MATCH (src:Node)-[link {id: link_id}]->(tgt:Node)
            OPTIONAL MATCH (src)-[src_mem:BELONGS_TO]->(e:Subentity {id: entity_id})
            OPTIONAL MATCH (tgt)-[tgt_mem:BELONGS_TO]->(e)
            RETURN link.id as link_id,
                   entity_id,
                   coalesce(src_mem.weight, 0.0) as src_weight,
                   coalesce(tgt_mem.weight, 0.0) as tgt_weight
            """

            params = {
                'link_ids': link_ids,
                'entity_ids': entity_ids
            }

            result = self.graph_store.query(query, params)

            if result and len(result) > 0:
                for row in result:
                    link_id = row[0]
                    entity_id = row[1]
                    src_weight = float(row[2])
                    tgt_weight = float(row[3])

                    # Link membership = min of source and target
                    link_weight = min(src_weight, tgt_weight)

                    if link_weight > 0.0:
                        if link_id not in memberships:
                            memberships[link_id] = {}
                        memberships[link_id][entity_id] = link_weight

            logger.debug(f"[Membership] Computed {len(memberships)} links with memberships")

        except Exception as e:
            logger.error(f"[Membership] Failed to compute link memberships: {e}")

        return memberships


# Integration helper: Enhance node dicts with membership data
def enhance_nodes_with_memberships(
    nodes: List[Dict[str, Any]],
    memberships: Dict[str, Dict[str, float]]
) -> List[Dict[str, Any]]:
    """
    Add membership data to node dicts for WeightLearnerV2.

    Args:
        nodes: Node dicts from graph query
        memberships: Result from MembershipQueryHelper.get_node_memberships()

    Returns:
        Enhanced node dicts with 'memberships' field
    """
    for node in nodes:
        node_id = node.get('name') or node.get('id')
        if node_id in memberships:
            node['memberships'] = memberships[node_id]
        else:
            node['memberships'] = {}

    return nodes


# Integration example for trace_capture.py:
"""
# In TraceCapture.__init__():
self.entity_context_manager = EntityContextManager(self.graph_store)
self.membership_helper = MembershipQueryHelper(self.graph_store)

# In _process_reinforcement_signals(), before calling weight_learner:

# 1. Derive entity context
entity_context = self.entity_context_manager.derive_entity_context(
    wm_entities=None,  # TODO: Get from last WM emit
    graph_name=self.scope_to_graph['personal']
)

# 2. Query memberships for all nodes being updated
node_ids = list(reinforcement_seats.keys())
memberships = self.membership_helper.get_node_memberships(
    node_ids=node_ids,
    entity_ids=entity_context,
    graph_name=self.scope_to_graph['personal']
)

# 3. Enhance nodes with membership data
all_nodes = enhance_nodes_with_memberships(all_nodes, memberships)

# 4. Call WeightLearnerV2 with entity context
from orchestration.mechanisms.weight_learning_v2 import WeightLearnerV2
learner_v2 = WeightLearnerV2(alpha=0.1, alpha_local=0.8, alpha_global=0.2)

updates = learner_v2.update_node_weights(
    nodes=all_nodes,
    reinforcement_seats=reinforcement_seats,
    formations=node_formations,
    entity_context=entity_context  # NEW: Entity context parameter
)

# 5. Apply overlays back to database (in addition to global weights)
for update in updates:
    if update.local_overlays:
        for overlay in update.local_overlays:
            # Persist overlay to database
            # TODO: Add log_weight_overlays field updates
            pass
"""
