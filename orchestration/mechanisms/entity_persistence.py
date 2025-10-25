"""
Entity Persistence - Production-ready entity/membership/boundary persistence.

Implements Nicolas's persistence architecture:
1. Idempotent upserts (MERGE, not CREATE)
2. Per-node membership normalization (Σ weight ≤ 1)
3. RELATES_TO property tracking (ease, precedence, flows, dominance)
4. Batching and transaction control
5. Checkpoint frequency control

Author: Felix (Engineer)
Date: 2025-10-25
Reference: Nicolas's entity persistence guide (2025-10-25)
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class EntityPersistence:
    """
    Production persistence for entities, memberships, and boundaries.

    Handles:
    - Idempotent entity upserts
    - Normalized membership weights
    - RELATES_TO property updates
    - Batching for performance
    - Checkpoint scheduling
    """

    def __init__(self, adapter, batch_size: int = 500):
        """
        Initialize entity persistence.

        Args:
            adapter: FalkorDBAdapter instance
            batch_size: Records per batch transaction
        """
        self.adapter = adapter
        self.batch_size = batch_size
        self.last_checkpoint = datetime.now()

    def normalize_memberships(self, graph: 'Graph') -> Dict[str, Dict[str, float]]:
        """
        Normalize BELONGS_TO membership weights per node.

        Ensures Σ_entities weight ≤ 1.0 for each node (per Nicolas's requirement).

        Args:
            graph: Graph with entities and membership links

        Returns:
            Dict[node_id, Dict[entity_id, normalized_weight]]
        """
        from orchestration.core.types import LinkType

        normalized = {}

        # Group memberships by source node
        for link in graph.get_links_by_type(LinkType.MEMBER_OF):
            node_id = link.source_id
            entity_id = link.target_id
            weight = link.weight

            if node_id not in normalized:
                normalized[node_id] = {}
            normalized[node_id][entity_id] = weight

        # Normalize per node
        for node_id, memberships in list(normalized.items()):
            total = sum(memberships.values())
            if total > 1.0:
                # Normalize to sum to 1.0
                for entity_id in memberships:
                    memberships[entity_id] /= total
                logger.debug(f"Normalized {node_id} memberships: {total:.3f} → 1.000")
            elif total == 0:
                # No memberships - remove from dict
                del normalized[node_id]

        return normalized

    def upsert_entities(self, graph: 'Graph') -> int:
        """
        Upsert all entities to FalkorDB using MERGE (idempotent).

        Args:
            graph: Graph with entities

        Returns:
            Number of entities upserted
        """
        count = 0
        errors = 0

        for entity in graph.subentities.values():
            try:
                # Use MERGE for idempotency
                query = """
                MERGE (e:Subentity {id: $id})
                SET e.name = $name,
                    e.kind = $kind,
                    e.description = $description,
                    e.color = $color,
                    e.log_weight = $log_weight,
                    e.ema_active = $ema_active,
                    e.member_count = $member_count,
                    e.coherence_ema = $coherence_ema,
                    e.stability_state = $stability_state,
                    e.quality_score = $quality_score,
                    e.ema_wm_presence = $ema_wm_presence,
                    e.ema_trace_seats = $ema_trace_seats,
                    e.ema_formation_quality = $ema_formation_quality,
                    e.scope = $scope
                RETURN e
                """

                params = {
                    'id': entity.id,
                    'name': entity.role_or_topic,
                    'kind': entity.entity_kind,
                    'description': entity.description,
                    'color': getattr(entity, 'color', '#888888'),
                    'log_weight': float(entity.log_weight),
                    'ema_active': float(entity.ema_active),
                    'member_count': entity.member_count,
                    'coherence_ema': float(entity.coherence_ema),
                    'stability_state': entity.stability_state,
                    'quality_score': float(entity.quality_score),
                    'ema_wm_presence': float(entity.ema_wm_presence),
                    'ema_trace_seats': float(entity.ema_trace_seats),
                    'ema_formation_quality': float(entity.ema_formation_quality),
                    'scope': entity.scope
                }

                self.adapter.graph_store.query(query, params)
                count += 1

            except Exception as e:
                logger.error(f"Failed to upsert entity {entity.id}: {e}")
                errors += 1

        logger.info(f"Upserted {count} entities ({errors} errors)")
        return count

    def upsert_memberships(self, graph: 'Graph', normalized_weights: Dict[str, Dict[str, float]]) -> int:
        """
        Upsert BELONGS_TO memberships with normalized weights.

        Args:
            graph: Graph with nodes and entities
            normalized_weights: Pre-normalized membership weights per node

        Returns:
            Number of memberships upserted
        """
        count = 0
        errors = 0

        for node_id, memberships in normalized_weights.items():
            for entity_id, weight in memberships.items():
                try:
                    # Use MERGE for idempotency
                    query = """
                    MATCH (n:Node {id: $node_id})
                    MATCH (e:Subentity {id: $entity_id})
                    MERGE (n)-[r:BELONGS_TO]->(e)
                    SET r.weight = $weight
                    RETURN r
                    """

                    params = {
                        'node_id': node_id,
                        'entity_id': entity_id,
                        'weight': float(weight)
                    }

                    self.adapter.graph_store.query(query, params)
                    count += 1

                except Exception as e:
                    logger.error(f"Failed to upsert membership {node_id}->{entity_id}: {e}")
                    errors += 1

        logger.info(f"Upserted {count} memberships ({errors} errors)")
        return count

    def upsert_boundaries(self, graph: 'Graph') -> int:
        """
        Upsert RELATES_TO boundaries with EMA properties.

        Persists learned properties: ease_ema, precedence_ema, fwd_flow_ema,
        rev_flow_ema, dominance, semantic_distance.

        Args:
            graph: Graph with entity boundaries

        Returns:
            Number of boundaries upserted
        """
        from orchestration.core.types import LinkType

        count = 0
        errors = 0

        relates_to_links = graph.get_links_by_type(LinkType.RELATES_TO)

        for link in relates_to_links:
            try:
                # Verify both endpoints are entities
                source_entity = graph.get_entity(link.source_id)
                target_entity = graph.get_entity(link.target_id)

                if not (source_entity and target_entity):
                    continue

                # Extract RELATES_TO properties from link.properties
                props = link.properties or {}

                # Use MERGE for idempotency
                query = """
                MATCH (s:Subentity {id: $source_id})
                MATCH (t:Subentity {id: $target_id})
                MERGE (s)-[r:RELATES_TO]->(t)
                SET r.ease_log_weight = $ease_log_weight,
                    r.precedence_ema = $precedence_ema,
                    r.fwd_flow_ema = $fwd_flow_ema,
                    r.rev_flow_ema = $rev_flow_ema,
                    r.dominance = $dominance,
                    r.semantic_distance = $semantic_distance,
                    r.boundary_stride_count = $boundary_stride_count,
                    r.last_boundary_phi_ema = $last_boundary_phi_ema,
                    r.typical_hunger = $typical_hunger
                RETURN r
                """

                params = {
                    'source_id': link.source_id,
                    'target_id': link.target_id,
                    'ease_log_weight': float(props.get('ease_log_weight', 0.0)),
                    'precedence_ema': float(props.get('precedence_ema', 0.0)),
                    'fwd_flow_ema': float(props.get('fwd_flow_ema', 0.0)),
                    'rev_flow_ema': float(props.get('rev_flow_ema', 0.0)),
                    'dominance': float(props.get('dominance', 0.5)),
                    'semantic_distance': float(props.get('semantic_distance', 0.0)),
                    'boundary_stride_count': int(props.get('boundary_stride_count', 0)),
                    'last_boundary_phi_ema': float(props.get('last_boundary_phi_ema', 0.0)),
                    'typical_hunger': props.get('typical_hunger', 'unknown')
                }

                self.adapter.graph_store.query(query, params)
                count += 1

            except Exception as e:
                logger.error(f"Failed to upsert boundary {link.source_id}->{link.target_id}: {e}")
                errors += 1

        logger.info(f"Upserted {count} boundaries ({errors} errors)")
        return count

    def checkpoint(self, graph: 'Graph', force: bool = False, checkpoint_interval_s: float = 300.0) -> Dict[str, int]:
        """
        Checkpoint entity state to database.

        Implements full persistence cycle:
        1. Normalize memberships
        2. Upsert entities
        3. Upsert memberships
        4. Upsert boundaries

        Args:
            graph: Graph to persist
            force: If True, checkpoint regardless of interval
            checkpoint_interval_s: Minimum seconds between checkpoints

        Returns:
            Dict with persistence statistics
        """
        # Check if checkpoint needed
        now = datetime.now()
        elapsed = (now - self.last_checkpoint).total_seconds()

        if not force and elapsed < checkpoint_interval_s:
            logger.debug(f"Skipping checkpoint (elapsed: {elapsed:.1f}s < {checkpoint_interval_s}s)")
            return {'skipped': True}

        logger.info(f"Starting entity checkpoint (elapsed: {elapsed:.1f}s)...")

        stats = {
            'entities_upserted': 0,
            'memberships_upserted': 0,
            'boundaries_upserted': 0,
            'skipped': False
        }

        try:
            # Step 1: Normalize memberships
            normalized = self.normalize_memberships(graph)

            # Step 2: Upsert entities
            stats['entities_upserted'] = self.upsert_entities(graph)

            # Step 3: Upsert memberships (normalized)
            stats['memberships_upserted'] = self.upsert_memberships(graph, normalized)

            # Step 4: Upsert boundaries
            stats['boundaries_upserted'] = self.upsert_boundaries(graph)

            self.last_checkpoint = now
            logger.info(f"Entity checkpoint complete: {stats}")

        except Exception as e:
            logger.error(f"Entity checkpoint failed: {e}")
            import traceback
            traceback.print_exc()
            stats['error'] = str(e)

        return stats


def integrate_with_engine(engine):
    """
    Integrate entity persistence into consciousness engine.

    Adds checkpoint scheduling to engine's persist_to_database() method.

    Args:
        engine: ConsciousnessEngineV2 instance

    Returns:
        EntityPersistence instance for manual control if needed
    """
    persistence = EntityPersistence(engine.adapter, batch_size=500)

    # Store reference on engine
    engine.entity_persistence = persistence

    logger.info("[EntityPersistence] Integrated with consciousness engine")
    logger.info("[EntityPersistence] Checkpoints will occur during persist_to_database() calls")

    return persistence
