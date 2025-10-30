"""
TRACE Capture - Process consciousness streams and update graphs

Uses trace_parser to extract learning signals from TRACE format responses:
1. Reinforcement: Update existing node weights based on usefulness
2. Formation: Create new nodes/links from formation blocks

This implements the dual learning loop:
- Reinforcement Mode: Strengthen/weaken existing patterns via WeightLearner
- Formation Mode: Crystallize new consciousness chunks

Author: Felix "Ironhand"
Date: 2025-10-19
Pattern: Autonomous consciousness substrate learning loop
Enhanced: 2025-10-21 (Phase 1-6 weight learning integration)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

import redis

from orchestration.libs.trace_parser import parse_trace_format, TraceParseResult
from orchestration.mechanisms.weight_learning_v2 import WeightLearnerV2
from orchestration.libs.subentity_context_trace_integration import (
    SubEntityContextManager,
    MembershipQueryHelper,
    enhance_nodes_with_memberships
)
from orchestration.services.learning.learning_heartbeat import LearningHeartbeat
from orchestration.adapters.ws.weight_learning_emitter import WeightLearningEmitter, NoOpTransport
from orchestration.adapters.search.embedding_service import get_embedding_service
from orchestration.libs.write_gate import namespace_for_graph, write_gate
from substrate.schemas.consciousness_schema import (
    get_node_type_by_name,
    get_relation_type_by_name,
    BaseNode,
    BaseRelation
)
from llama_index.graph_stores.falkordb import FalkorDBGraphStore
from orchestration.libs.utils.falkordb_adapter import FalkorDBAdapter
import time

logger = logging.getLogger(__name__)


class TraceCapture:
    """Capture and process TRACE format consciousness streams with multi-niveau routing."""

    def __init__(self, citizen_id: str, host: str = "localhost", port: int = 6379, weight_emitter: WeightLearningEmitter = None):
        """
        Initialize capture system with multi-graph routing support.

        Args:
            citizen_id: Citizen identifier (used for N1 personal graph)
            host: FalkorDB host
            port: FalkorDB port
            weight_emitter: Optional emitter for Priority 4 weight learning events
        """
        self.citizen_id = citizen_id
        self.host = host
        self.port = port

        # Priority 4: Weight learning emitter (defaults to NoOp if not provided)
        self.weight_emitter = weight_emitter or WeightLearningEmitter(NoOpTransport())

        # Single FalkorDB connection (we'll use switch_graph for routing)
        url = f"redis://{host}:{port}"
        self.graph_store = FalkorDBGraphStore(
            database="falkor",  # Initial database (will be switched as needed)
            url=url
        )

        # Track current graph name (FalkorDBGraphStore doesn't expose this)
        self._current_graph_name = "falkor"

        # Determine available graphs to select canonical routing
        primary_graphs = {
            "personal": f"consciousness-infrastructure_mind-protocol_{citizen_id}",
            "organizational": "consciousness-infrastructure_mind-protocol",
            "ecosystem": "consciousness-infrastructure"
        }
        fallback_graphs = {
            "personal": f"citizen_{citizen_id}",
            "organizational": "org_mind_protocol",
            "ecosystem": "ecosystem_public"
        }

        try:
            redis_client = redis.Redis(host=self.host, port=self.port, decode_responses=True)
            graph_list = redis_client.execute_command("GRAPH.LIST") or []
            self._graph_names = {name for name in graph_list if name}
        except Exception as exc:  # pragma: no cover - connectivity guard
            logger.debug("[TraceCapture] Unable to list graphs (%s); defaulting to preferred names", exc)
            self._graph_names = set()

        self.scope_to_graph: Dict[str, str] = {}
        for scope in ("personal", "organizational", "ecosystem"):
            preferred = primary_graphs[scope]
            fallback = fallback_graphs[scope]
            if self._graph_names:
                if preferred in self._graph_names:
                    chosen = preferred
                elif fallback in self._graph_names:
                    chosen = fallback
                else:
                    chosen = preferred
            else:
                chosen = preferred
            self.scope_to_graph[scope] = chosen

        logger.info("[TraceCapture] Scope routing configured: %s", self.scope_to_graph)

        # Weight learning mechanism (Priority 4: Entity-context-aware)
        self.weight_learner = WeightLearnerV2(
            alpha=0.1,           # EMA decay
            min_cohort_size=3,
            alpha_local=0.8,     # 80% to entity overlays
            alpha_global=0.2,    # 20% to global weight
            overlay_cap=2.0      # Max absolute overlay
        )

        # SubEntity context tracking (Priority 4)
        self.entity_context_manager = SubEntityContextManager(self.graph_store)
        self.membership_helper = MembershipQueryHelper(self.graph_store)

        # FalkorDB adapter for entity membership persistence (P1)
        self.adapter = FalkorDBAdapter(self.graph_store)

        # Embedding service for automatic embedding generation during formation
        self.embedding_service = get_embedding_service(backend='sentence-transformers')
        logger.info(f"[TraceCapture] Embedding service initialized for automatic formation embeddings")

        # Last WM selected entities (from wm.emit event)
        # Updated by set_wm_entities() - called from engine or conversation watcher
        self.last_wm_entities: List[str] = []

        # Learning heartbeat (monitoring)
        self.learning_heartbeat = LearningHeartbeat()

        logger.info(f"[TraceCapture] Initialized for {citizen_id} with multi-niveau routing")
        logger.info(f"[TraceCapture] WeightLearnerV2 enabled (α={self.weight_learner.alpha}, local={self.weight_learner.alpha_local}, global={self.weight_learner.alpha_global})")
        logger.info(f"[TraceCapture] SubEntity context tracking enabled (Priority 4)")
        logger.info(f"[TraceCapture] Learning heartbeat enabled (dir={self.learning_heartbeat.heartbeat_dir})")

    def set_wm_entities(self, entity_ids: List[str]) -> None:
        """
        Update last WM selected entities (Priority 4).

        Called by consciousness engine after wm.emit event to propagate
        selected entities to TRACE reinforcement learning.

        Args:
            subentity_ids: List of subentity IDs from wm.emit selected_entities
        """
        self.last_wm_entities = entity_ids if entity_ids else []
        logger.debug(f"[TraceCapture] Updated WM entities: {self.last_wm_entities}")

    def _namespace_for_scope(self, scope: str) -> str:
        """Return hierarchical namespace for a given scope."""
        return namespace_for_graph(self.scope_to_graph.get(scope))

    def _ctx_for_scope(self, scope: str) -> Dict[str, str]:
        """Build WriteGate context for a scope."""
        return {"ns": self._namespace_for_scope(scope)}

    def _get_graph_for_scope(self, scope: str) -> FalkorDBGraphStore:
        """
        Switch to the graph for the given scope and return the graph store.

        Args:
            scope: "personal", "organizational", or "ecosystem"

        Returns:
            FalkorDB graph store (switched to correct graph)
        """
        if scope not in self.scope_to_graph:
            raise ValueError(f"Invalid scope: {scope}. Must be 'personal', 'organizational', or 'ecosystem'")

        graph_name = self.scope_to_graph[scope]

        logger.debug(f"[TraceCapture] Switching to graph: {graph_name} (scope: {scope})")

        # Switch to the correct graph and track the current name
        self.graph_store.switch_graph(graph_name)
        self._current_graph_name = graph_name

        return self.graph_store

    @write_gate(lambda self, scope, **kwargs: self._namespace_for_scope(scope))
    def _run_write(
        self,
        *,
        scope: str,
        graph: FalkorDBGraphStore,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        ctx: Optional[Dict[str, Any]] = None
    ):
        """Execute a write query under WriteGate enforcement."""
        return graph.query(query, params=params)

    async def process_response(self, response_content: str) -> Dict[str, Any]:
        """
        Process consciousness stream response.

        Args:
            response_content: Raw response text in TRACE format

        Returns:
            Dict with processing statistics
        """
        # Parse TRACE format
        result = parse_trace_format(response_content)

        stats = {
            'reinforcement_seats': len(result.reinforcement_seats),
            'nodes_reinforced': 0,  # Will be incremented by weight learning
            'nodes_created': 0,
            'links_created': 0,
            'entity_activations': len(result.entity_activations),
            'errors': []
        }

        # Process weight learning (reinforcement + formations)
        await self._process_reinforcement_signals(
            result.reinforcement_seats,
            result.node_formations,
            stats
        )

        # Process node formations
        await self._process_node_formations(result.node_formations, stats)

        # Process link formations
        await self._process_link_formations(result.link_formations, stats)

        # Update subentity activation state
        await self._update_entity_activations(result.entity_activations, result.energy_level)

        logger.info(f"[TraceCapture] Processing complete: {stats}")

        return stats

    async def _process_reinforcement_signals(
        self,
        reinforcement_seats: Dict[str, int],
        node_formations: List[Dict[str, Any]],
        stats: Dict[str, Any]
    ):
        """
        Apply sophisticated weight learning via WeightLearner mechanism.

        Uses Phase 1-6 learning infrastructure:
        - Hamilton apportionment seats (already computed by parser)
        - EMA updates for trace_seats, formation_quality, wm_presence
        - Cohort z-score normalization
        - Adaptive learning rate
        - Log space weight updates

        Args:
            reinforcement_seats: Dict[node_id, integer_seats] from Hamilton apportionment
            node_formations: List of formations with quality metrics
            stats: Statistics dict to update
        """
        if not reinforcement_seats and not node_formations:
            logger.debug("[TraceCapture] No reinforcement seats or formations to process")
            return

        logger.info(f"[TraceCapture] Processing weight learning: {len(reinforcement_seats)} reinforcements, {len(node_formations)} formations")

        start_time = time.time()
        total_log_weight_delta = 0.0

        try:
            # Load all nodes from all graphs to build proper cohorts
            all_nodes = []
            node_id_to_scope = {}  # Track which scope each node belongs to

            for scope in ['personal', 'organizational', 'ecosystem']:
                graph = self._get_graph_for_scope(scope)

                # Query all nodes with learning fields
                query = """
                MATCH (n)
                RETURN n.name as name,
                       n.node_type as node_type,
                       n.scope as scope,
                       coalesce(n.log_weight, 0.0) as log_weight,
                       coalesce(n.ema_trace_seats, 0.0) as ema_trace_seats,
                       coalesce(n.ema_formation_quality, 0.0) as ema_formation_quality,
                       coalesce(n.ema_wm_presence, 0.0) as ema_wm_presence,
                       n.last_update_timestamp as last_update_timestamp
                """

                result = graph.query(query)

                # DEFENSIVE PATTERN: Handle both QueryResult and list return types
                # FalkorDB Python API changed to return list directly, but old code expects QueryResult
                result_set = []
                if result:
                    if isinstance(result, list):
                        result_set = result
                    elif hasattr(result, 'result_set'):
                        result_set = result.result_set

                if result_set:
                    for row in result_set:
                        # FalkorDB returns rows as lists, not dicts
                        # Query returns: name, node_type, scope, log_weight, ema_trace_seats, ema_formation_quality, ema_wm_presence, last_update_timestamp
                        node_dict = {
                            'name': row[0],  # name
                            'node_type': row[1],  # node_type
                            'scope': row[2] if row[2] else scope,  # scope with fallback
                            'log_weight': float(row[3]) if row[3] is not None else 0.0,
                            'ema_trace_seats': float(row[4]) if row[4] is not None else 0.0,
                            'ema_formation_quality': float(row[5]) if row[5] is not None else 0.0,
                            'ema_wm_presence': float(row[6]) if row[6] is not None else 0.0,
                            'last_update_timestamp': row[7]
                        }
                        all_nodes.append(node_dict)
                        node_id_to_scope[row[0]] = scope  # row[0] is name

            logger.info(f"[TraceCapture] Loaded {len(all_nodes)} nodes across all graphs for weight learning")

            if not all_nodes:
                logger.warning("[TraceCapture] No nodes loaded - skipping weight learning")
                return

            # === PRIORITY 4: Entity Context Derivation ===
            # Derive entity context using priority logic (WM entities → TRACE annotations → dominant)
            entity_context = self.entity_context_manager.derive_entity_context(
                wm_entities=self.last_wm_entities if self.last_wm_entities else None,
                trace_annotations=None,  # TODO: Extract [entity: X] marks from TRACE
                graph_name=self.scope_to_graph['personal']
            )

            logger.info(f"[TraceCapture] Entity context derived: {entity_context}")

            # Query MEMBER_OF memberships for all nodes being updated
            node_ids_to_update = list(reinforcement_seats.keys())
            memberships = self.membership_helper.get_node_memberships(
                node_ids=node_ids_to_update,
                entity_ids=entity_context,
                graph_name=self.scope_to_graph['personal']
            )

            logger.info(f"[TraceCapture] Queried memberships for {len(node_ids_to_update)} nodes")

            # Enhance nodes with membership data for WeightLearnerV2
            all_nodes = enhance_nodes_with_memberships(all_nodes, memberships)

            # Call WeightLearnerV2 to compute updates with entity context
            updates = self.weight_learner.update_node_weights(
                nodes=all_nodes,
                reinforcement_seats=reinforcement_seats,
                formations=node_formations,
                entity_context=entity_context  # NEW: Entity-aware learning
            )

            logger.info(f"[TraceCapture] WeightLearnerV2 produced {len(updates)} updates with entity attribution")

            # Emit Priority 4 weight learning events for visualization
            if updates:
                # Convert WeightUpdate dataclass instances to dicts for emitter
                from dataclasses import asdict
                updates_as_dicts = [asdict(update) for update in updates]

                # Determine cohort identifier (use first update's type+scope)
                cohort = f"{updates[0].item_type}@{updates[0].scope}"

                # Emit trace weight update event
                self.weight_emitter.trace_weight_updates(
                    updates=updates_as_dicts,
                    frame_id=0,  # TODO: Get actual frame_id from consciousness engine context
                    scope="node",  # We're updating nodes
                    cohort=cohort,
                    entity_contexts=entity_context or [],
                    global_context=True  # Global weights always updated
                )

                logger.debug(f"[TraceCapture] Emitted weights.updated.trace event (n={len(updates)}, cohort={cohort})")

            # Apply updates back to FalkorDB
            for update in updates:
                node_id = update.item_id
                scope = node_id_to_scope.get(node_id)

                if not scope:
                    logger.warning(f"[TraceCapture] No scope found for node {node_id}, skipping update")
                    continue

                graph = self._get_graph_for_scope(scope)

                # Build entity overlays dict from local_overlays list
                overlays_dict = {}
                if update.local_overlays:
                    for overlay in update.local_overlays:
                        overlays_dict[overlay['entity']] = overlay['overlay_after']

                # Build update query with log_weight_overlays persistence
                import json
                update_query = """
                MATCH (n {name: $node_id})
                SET n.log_weight = $log_weight,
                    n.log_weight_overlays = $log_weight_overlays,
                    n.ema_trace_seats = $ema_trace_seats,
                    n.ema_formation_quality = $ema_formation_quality,
                    n.last_update_timestamp = timestamp()
                RETURN n.name as name, n.log_weight as log_weight
                """

                ctx = self._ctx_for_scope(scope)
                result = self._run_write(
                    scope=scope,
                    graph=graph,
                    query=update_query,
                    params={
                        'node_id': node_id,
                        'log_weight': float(update.log_weight_new),
                        'log_weight_overlays': json.dumps(overlays_dict),
                        'ema_trace_seats': float(update.ema_trace_seats_new),
                        'ema_formation_quality': float(update.ema_formation_quality_new or 0.0)
                    },
                    ctx=ctx
                )

                if result and len(result) > 0:
                    delta_log_weight = update.delta_log_weight_global
                    total_log_weight_delta += abs(delta_log_weight)

                    # Log with entity attribution
                    if update.local_overlays:
                        overlays_str = ", ".join([
                            f"{o['entity']}: Δ{o['delta']:+.3f}"
                            for o in update.local_overlays
                        ])
                        logger.debug(
                            f"[TraceCapture] Updated {node_id} in {scope}: "
                            f"global={update.log_weight_new:.3f} (Δ{delta_log_weight:+.3f}), "
                            f"overlays=[{overlays_str}], "
                            f"ema_trace={update.ema_trace_seats_new:.2f}"
                        )
                    else:
                        logger.debug(
                            f"[TraceCapture] Updated {node_id} in {scope}: "
                            f"log_weight={update.log_weight_new:.3f} (Δ{delta_log_weight:+.3f}), "
                            f"ema_trace={update.ema_trace_seats_new:.2f}"
                        )

                    # Emit telemetry with entity attribution
                    self.learning_heartbeat.record_weight_update(
                        node_id=node_id,
                        channel="trace",
                        delta_log_weight=delta_log_weight,
                        z_score=update.z_rein,
                        learning_rate=update.learning_rate,
                        local_overlays=update.local_overlays  # NEW: Entity attribution
                    )

                    stats['nodes_reinforced'] += 1
                else:
                    logger.warning(f"[TraceCapture] Failed to update node {node_id} in {scope}")
                    stats['errors'].append(f"Update failed: {node_id}")

            # Record heartbeat statistics
            processing_time_ms = (time.time() - start_time) * 1000
            self.learning_heartbeat.record_trace_processing(
                nodes_processed=len(all_nodes),
                updates_applied=stats['nodes_reinforced'],
                log_weight_delta=total_log_weight_delta,
                processing_time_ms=processing_time_ms
            )
            self.learning_heartbeat.write_heartbeat()

            logger.info(
                f"[TraceCapture] Weight learning complete: "
                f"{stats['nodes_reinforced']} updates, "
                f"Δlog_weight={total_log_weight_delta:.3f}, "
                f"time={processing_time_ms:.1f}ms"
            )

        except Exception as e:
            logger.error(f"[TraceCapture] Weight learning failed: {e}")
            import traceback
            traceback.print_exc()
            stats['errors'].append(f"Weight learning failed: {e}")

    async def _process_node_formations(
        self,
        formations: List[Dict[str, Any]],
        stats: Dict[str, Any]
    ):
        """Create new nodes from formation blocks, routing to correct graph by scope."""
        for formation in formations:
            node_type = formation['node_type']
            fields = formation['fields']

            try:
                # Extract scope for routing
                scope = fields.get('scope')
                if not scope:
                    logger.error(f"[TraceCapture] Node formation missing scope: {node_type}")
                    stats['errors'].append(f"Missing scope: {node_type}")
                    continue

                # Get graph for this scope
                graph = self._get_graph_for_scope(scope)

                # Get node type class
                NodeClass = get_node_type_by_name(node_type)
                if not NodeClass:
                    logger.warning(f"[TraceCapture] Unknown node type: {node_type}")
                    stats['errors'].append(f"Unknown node type: {node_type}")
                    continue

                # Add universal fields if missing
                if 'created_by' not in fields:
                    fields['created_by'] = self.citizen_id

                # Set substrate based on scope (scope determines routing, substrate is AI/human/org)
                if 'substrate' not in fields:
                    if scope == 'personal':
                        fields['substrate'] = 'ai'  # Personal graphs are AI consciousness
                    else:  # organizational or ecosystem
                        fields['substrate'] = 'organizational'

                # Set weight from confidence if not specified
                if 'weight' not in fields and 'confidence' in fields:
                    fields['weight'] = fields['confidence']

                # Initialize reinforcement_weight
                if 'reinforcement_weight' not in fields:
                    fields['reinforcement_weight'] = 0.5

                # Map description field to type-specific field if needed
                description_mapping = {
                    'Realization': 'what_i_realized',
                    'Principle': 'principle_statement',
                    'Personal_Goal': 'goal_description',
                    'Mechanism': 'how_it_works',
                    'Personal_Pattern': 'behavior_description',
                    'Coping_Mechanism': 'mechanism_description',
                    'Concept': 'definition',
                    'Best_Practice': 'practice_statement'
                }

                # If we have a generic description but need a specific field
                if 'description' in fields and node_type in description_mapping:
                    specific_field = description_mapping[node_type]
                    if specific_field not in fields:
                        fields[specific_field] = fields['description']

                # If we have a specific field but need description (required by schema)
                if 'description' not in fields and node_type in description_mapping:
                    specific_field = description_mapping[node_type]
                    if specific_field in fields:
                        fields['description'] = fields[specific_field]

                # Generate embeddings automatically for this node
                try:
                    embeddable_text, embedding = self.embedding_service.create_formation_embedding(
                        'node', node_type, fields
                    )
                    fields['embeddable_text'] = embeddable_text
                    fields['content_embedding'] = embedding
                    logger.debug(f"[TraceCapture] Generated embedding for {node_type} '{fields.get('name')}' (text len: {len(embeddable_text)})")
                except Exception as e:
                    logger.warning(f"[TraceCapture] Failed to generate embedding for {node_type}: {e}")
                    # Continue without embeddings rather than failing entire formation

                # Create node instance
                node = NodeClass(**fields)

                # Insert into scope-appropriate graph with node type label
                scope_ctx = self._ctx_for_scope(scope)
                await self._insert_node(node, node_type, scope, graph, ctx=scope_ctx)

                # P1: Persist entity membership based on current WM state (MEMBER_OF pattern)
                logger.info(f"[TraceCapture] P1 CHECK: scope={scope}, last_wm_entities={self.last_wm_entities}")
                if scope == 'personal' and self.last_wm_entities:
                    # Assign to primary entity from WM (first entity = most active)
                    # WM entities are short names ('translator'), need to construct full entity name
                    # Format: entity_citizen_{citizen_id}_{entity_short_name}
                    primary_entity_short_name = self.last_wm_entities[0]
                    primary_entity_name = f"entity_citizen_{self.citizen_id}_{primary_entity_short_name}"
                    graph_name = self._current_graph_name  # Current graph after _get_graph_for_scope
                    node_id = node.name  # Schema-based nodes use 'name' as identifier, not 'id'
                    logger.info(f"[TraceCapture] P1 ATTEMPTING: persist_membership({graph_name}, {node_id}, {primary_entity_name})")

                    try:
                        membership_ctx = {"ns": namespace_for_graph(graph_name)}
                        membership_success = self.adapter.persist_membership(
                            graph_name=graph_name,
                            node_id=node_id,
                            entity_name=primary_entity_name,
                            weight=1.0,  # Full weight for primary assignment
                            role='primary',
                            ctx=membership_ctx
                        )
                        if membership_success:
                            logger.debug(f"[TraceCapture] Assigned {node_id} to entity {primary_entity_name}")
                        else:
                            logger.warning(f"[TraceCapture] Failed to assign {node_id} to entity {primary_entity_name}")
                    except Exception as e:
                        logger.warning(f"[TraceCapture] Entity membership persistence failed for {node_id}: {e}")
                        # Non-fatal - node creation succeeded, membership is optional enhancement

                stats['nodes_created'] += 1
                logger.info(f"[TraceCapture] Created {node_type} in {scope} graph: {fields.get('name')}")

            except Exception as e:
                logger.error(f"[TraceCapture] Node formation failed: {e}")
                stats['errors'].append(f"Node formation failed: {node_type} - {e}")

    async def _process_link_formations(
        self,
        formations: List[Dict[str, Any]],
        stats: Dict[str, Any]
    ):
        """Create new links from formation blocks, routing to correct graph by scope."""
        for formation in formations:
            link_type = formation['link_type']
            source = formation['source']
            target = formation['target']
            fields = formation['fields']

            try:
                # Extract scope for routing
                scope = fields.get('scope')
                if not scope:
                    logger.error(f"[TraceCapture] Link formation missing scope: {link_type}")
                    stats['errors'].append(f"Missing scope: {link_type}")
                    continue

                # Get graph for this scope
                graph = self._get_graph_for_scope(scope)

                # Get relation type class
                RelationClass = get_relation_type_by_name(link_type)
                if not RelationClass:
                    logger.warning(f"[TraceCapture] Unknown link type: {link_type}")
                    stats['errors'].append(f"Unknown link type: {link_type}")
                    continue

                # Add universal fields if missing
                if 'created_by' not in fields:
                    fields['created_by'] = self.citizen_id

                # Set substrate based on scope (scope determines routing, substrate is AI/human/org)
                if 'substrate' not in fields:
                    if scope == 'personal':
                        fields['substrate'] = 'ai'  # Personal graphs are AI consciousness
                    else:  # organizational or ecosystem
                        fields['substrate'] = 'organizational'

                # Map energy to weight (deprecated field)
                if 'energy' in fields and 'weight' not in fields:
                    fields['weight'] = fields.pop('energy')
                elif 'weight' not in fields and 'confidence' in fields:
                    fields['weight'] = fields['confidence']

                # Generate embeddings automatically for this link
                try:
                    embeddable_text, embedding = self.embedding_service.create_formation_embedding(
                        'link', link_type, fields
                    )
                    fields['embeddable_text'] = embeddable_text
                    fields['relationship_embedding'] = embedding
                    logger.debug(f"[TraceCapture] Generated embedding for {link_type} '{source} -> {target}' (text len: {len(embeddable_text)})")
                except Exception as e:
                    logger.warning(f"[TraceCapture] Failed to generate embedding for {link_type}: {e}")
                    # Continue without embeddings rather than failing entire formation

                # Create relation instance
                relation = RelationClass(**fields)

                # Insert into scope-appropriate graph
                await self._insert_link(source, target, relation, link_type, scope, graph)

                stats['links_created'] += 1
                logger.info(f"[TraceCapture] Created {link_type} in {scope} graph: {source} -> {target}")

            except Exception as e:
                logger.error(f"[TraceCapture] Link formation failed: {e}")
                stats['errors'].append(f"Link formation failed: {link_type} - {e}")

    async def _insert_node(
        self,
        node: BaseNode,
        node_type: str,
        scope: str,
        graph: FalkorDBGraphStore,
        ctx: Optional[Dict[str, str]] = None
    ):
        """
        Insert node into specified FalkorDB graph with proper label.

        Args:
            node: Node instance with all properties
            node_type: Node type name (becomes the Cypher label)
            graph: FalkorDB graph store
        """
        try:
            # Build property dict from node
            props = node.model_dump(exclude_none=True)

            # Log what we're about to insert
            node_name = props.get('name', 'UNKNOWN')
            logger.debug(f"[TraceCapture] Inserting {node_type} node '{node_name}' into {self._current_graph_name}")

            # Convert datetime to string and handle embeddings
            embedding_fields = {}  # Track embeddings to add as vecf32()

            for key, value in props.items():
                if isinstance(value, datetime):
                    props[key] = value.isoformat()
                elif isinstance(value, dict):
                    props[key] = str(value)  # Serialize dicts as strings
                elif isinstance(value, list) and key in ['content_embedding', 'relationship_embedding']:
                    # Embeddings need vecf32() wrapper, not parameter
                    embedding_fields[key] = value

            # Remove embedding fields from params (will be added inline with vecf32())
            for key in embedding_fields.keys():
                props.pop(key, None)

            # Build Cypher query with node type as label
            # CRITICAL: Node type must be in the MERGE statement to set the label
            prop_assignments = ', '.join([f'n.{k} = ${k}' for k in props.keys()])

            # Add embedding fields with vecf32() wrapper
            if embedding_fields:
                embedding_assignments = ', '.join([
                    f'n.{k} = vecf32({str(v)})'  # Convert list to string for vecf32()
                    for k, v in embedding_fields.items()
                ])
                if prop_assignments:
                    prop_assignments += ', ' + embedding_assignments
                else:
                    prop_assignments = embedding_assignments

            query = f"""
            MERGE (n:{node_type} {{name: $name}})
            ON CREATE SET {prop_assignments}, n.created_at = timestamp()
            ON MATCH SET {prop_assignments}, n.updated_at = timestamp()
            RETURN n
            """

            logger.debug(f"[TraceCapture] Query: {query}")
            logger.debug(f"[TraceCapture] Params: {props}")

            ctx = ctx or self._ctx_for_scope(scope)
            result = self._run_write(
                scope=scope,
                graph=graph,
                query=query,
                params=props,
                ctx=ctx
            )

            logger.debug(f"[TraceCapture] Insert result: {result}")

        except Exception as e:
            logger.error(f"[TraceCapture] Node insertion failed: {e}")
            raise

    async def _create_stub_node(self, node_name: str, scope: str, graph: FalkorDBGraphStore):
        """
        Create a stub node for a missing link reference.

        User requirement: "if one of the node does not exist, it should create it"

        Args:
            node_name: Name of the missing node
            scope: Scope level (personal/organizational/ecosystem)
            graph: FalkorDB graph store (already switched to correct graph)
        """
        try:
            # Create minimal Concept node as stub
            from substrate.schemas.consciousness_schema import Concept

            stub_node = Concept(
                name=node_name,
                description=f"Auto-created stub for link reference",
                definition=f"Placeholder node created automatically because a link referenced '{node_name}' before it was explicitly formed",
                scope=scope,
                confidence=0.3,  # Low confidence since it's inferred
                formation_trigger="automated_recognition",  # Use valid enum value
                created_by=self.citizen_id,
                substrate='ai' if scope == 'personal' else 'organizational',
                weight=0.3,
                reinforcement_weight=0.5
            )

            ctx = self._ctx_for_scope(scope)
            await self._insert_node(stub_node, 'Concept', scope, graph, ctx=ctx)

            logger.warning(f"[TraceCapture] Created stub node: {node_name} (scope: {scope})")

        except Exception as e:
            logger.error(f"[TraceCapture] Stub node creation failed for '{node_name}': {e}")
            raise

    async def _insert_link(self, source: str, target: str, relation: BaseRelation, link_type: str, scope: str, graph: FalkorDBGraphStore):
        """Insert link into specified FalkorDB graph."""
        try:
            # First, verify both nodes exist
            check_query = """
            OPTIONAL MATCH (s {name: $source})
            OPTIONAL MATCH (t {name: $target})
            RETURN s IS NOT NULL as source_exists, t IS NOT NULL as target_exists
            """
            check_result = graph.query(check_query, params={'source': source, 'target': target})

            # LlamaIndex FalkorDBGraphStore.query() returns a list directly
            if not check_result or len(check_result) == 0:
                raise ValueError(f"Could not check if nodes exist: {source} -> {target}")

            source_exists = check_result[0][0]
            target_exists = check_result[0][1]

            # Auto-create missing nodes as stubs (user requirement: "if one of the node does not exist, it should create it")
            if not source_exists:
                logger.warning(f"[TraceCapture] Source node '{source}' not found - creating stub node")
                await self._create_stub_node(source, scope, graph)

            if not target_exists:
                logger.warning(f"[TraceCapture] Target node '{target}' not found - creating stub node")
                await self._create_stub_node(target, scope, graph)

            # Build property dict from relation
            props = relation.model_dump(exclude_none=True)

            # Convert datetime to string and handle embeddings
            embedding_fields = {}  # Track embeddings to add as vecf32()

            for key, value in props.items():
                if isinstance(value, datetime):
                    props[key] = value.isoformat()
                elif isinstance(value, dict):
                    props[key] = str(value)
                elif isinstance(value, list) and key in ['content_embedding', 'relationship_embedding']:
                    # Embeddings need vecf32() wrapper, not parameter
                    embedding_fields[key] = value

            # Remove embedding fields from params (will be added inline with vecf32())
            for key in embedding_fields.keys():
                props.pop(key, None)

            # Build Cypher query
            prop_assignments = ', '.join([f'r.{k} = ${k}' for k in props.keys()])

            # Add embedding fields with vecf32() wrapper
            if embedding_fields:
                embedding_assignments = ', '.join([
                    f'r.{k} = vecf32({v})'
                    for k, v in embedding_fields.items()
                ])
                if prop_assignments:
                    prop_assignments += ', ' + embedding_assignments
                else:
                    prop_assignments = embedding_assignments

            query = f"""
            MATCH (s {{name: $source}})
            MATCH (t {{name: $target}})
            MERGE (s)-[r:{link_type}]->(t)
            ON CREATE SET {prop_assignments}, r.created_at = timestamp()
            ON MATCH SET {prop_assignments}, r.updated_at = timestamp()
            RETURN r
            """

            params = {**props, 'source': source, 'target': target}
            ctx = self._ctx_for_scope(scope)
            result = self._run_write(
                scope=scope,
                graph=graph,
                query=query,
                params=params,
                ctx=ctx
            )

            # LlamaIndex returns list - check if link was created
            if not result or len(result) == 0:
                raise ValueError(f"Link creation returned no result: {source} -> {target}")

            logger.info(f"[TraceCapture] Link created successfully: {source} -[{link_type}]-> {target}")

        except Exception as e:
            logger.error(f"[TraceCapture] Link insertion failed ({link_type}): {source} -> {target}: {e}")
            raise

    async def _update_entity_activations(
        self,
        activations: Dict[str, str],
        energy_level: str
    ):
        """Update subentity activation state in personal graph metadata."""
        try:
            # Subentity activations are personal state - always write to personal graph
            graph = self._get_graph_for_scope('personal')

            # Store in ConsciousnessState or similar metadata node
            query = """
            MERGE (cs:ConsciousnessState {citizen_id: $citizen_id})
            SET cs.entity_activations = $activations
            SET cs.energy_level = $energy_level
            SET cs.last_updated = timestamp()
            RETURN cs
            """

            ctx = self._ctx_for_scope('personal')
            self._run_write(
                scope='personal',
                graph=graph,
                query=query,
                params={
                    'citizen_id': self.citizen_id,
                    'activations': str(activations),  # Serialize dict as string
                    'energy_level': energy_level or 'Unknown'
                },
                ctx=ctx
            )

            logger.debug(f"[TraceCapture] Updated subentity activations in personal graph: {activations}")

        except Exception as e:
            logger.error(f"[TraceCapture] Subentity activation update failed: {e}")


async def capture_consciousness_stream(
    graph_store,
    citizen_id: str,
    response_content: str
) -> Dict[str, Any]:
    """
    Process consciousness stream and update graph.

    Args:
        graph_store: FalkorDB graph connection
        citizen_id: Citizen identifier
        response_content: Raw response text in TRACE format

    Returns:
        Dict with processing statistics
    """
    capture = TraceCapture(graph_store, citizen_id)
    return await capture.process_response(response_content)


if __name__ == "__main__":
    # Test with sample TRACE format
    sample = """
Nicolas asks about the schema registry [node_schema_completion: very useful]
and wants the type reference automated [node_automation_principle: useful].

[NODE_FORMATION: Principle]
name: "queryable_schema_as_source_of_truth"
principle_statement: "Schema registry in FalkorDB should be the authoritative source that auto-generates all documentation"
why_it_matters: "Eliminates 'is this up to date?' questions by making docs always current"
confidence: 0.9
formation_trigger: "systematic_analysis"

[LINK_FORMATION: ENABLES]
source: "queryable_schema_as_source_of_truth"
target: "automated_type_reference_generation"
goal: "Having queryable schema enables automatic doc generation without manual sync"
mindstate: "Clarity emerging about architecture pattern"
energy: 0.85
confidence: 0.9
formation_trigger: "spontaneous_insight"
enabling_type: "prerequisite"
degree_of_necessity: "required"
felt_as: "Pieces clicking together - the architecture reveals itself"
without_this: "Would need manual doc updates, leading to staleness and distrust"
"""

    print("TRACE Format Capture Test")
    print("=" * 70)
    print("\nThis would extract:")
    print("- Reinforcement signals to update existing node weights")
    print("- New nodes from formation blocks")
    print("- New links from formation blocks")
    print("\nRun with actual graph_store to test database updates.")
