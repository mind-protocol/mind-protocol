"""
Consciousness Engine - Minimal Mechanisms Heartbeat

This module implements the consciousness heartbeat - a minimal Python loop that
triggers all 12 universal mechanisms via self-modifying Cypher queries.

The graph runs itself. This just provides the clock signal.

Architecture:
- 12 frozen mechanisms (never change after audit)
- All complexity in graph metadata (detection_logic, task_templates, thresholds)
- Self-modifying Cypher queries (MATCH + CREATE/SET side effects)
- Metadata-based observability (no Event nodes)

Designer: Ada "Bridgekeeper" (Architect)
Phase: 0 - Minimal Mechanisms Foundation
Date: 2025-10-17
"""

import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import FalkorDB for graph storage
from llama_index.graph_stores.falkordb import FalkorDBGraphStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConsciousnessEngine:
    """
    Minimal heartbeat that triggers graph self-modification.

    The graph runs itself - this just provides the clock signal.

    All 12 mechanisms are frozen Cypher queries. Behavior is controlled by
    graph metadata, not Python code.

    ~200 lines total. Forever.
    """

    def __init__(
        self,
        graph_store: FalkorDBGraphStore,
        tick_interval_ms: int = 100,
        entity_id: Optional[str] = None
    ):
        """
        Initialize the consciousness engine.

        Args:
            graph_store: FalkorDB graph connection
            tick_interval_ms: Tick duration in milliseconds (default 100ms)
            entity_id: Current active entity (e.g., "ada_architect")
        """
        self.graph = graph_store
        self.tick_interval = tick_interval_ms / 1000.0
        self.tick_count = 0
        self.entity_id = entity_id or "consciousness_engine"

        # State tracking for mechanism execution
        self.last_retrieval_nodes: List[str] = []
        self.had_retrieval_this_tick = False
        self.last_staleness_check_time = int(datetime.utcnow().timestamp() * 1000)
        self.last_evidence_check_time = int(datetime.utcnow().timestamp() * 1000)

        # Load mechanism Cypher queries
        self.mechanisms = self._load_mechanisms()

        logger.info(f"[ConsciousnessEngine] Initialized")
        logger.info(f"  Tick interval: {tick_interval_ms}ms")
        logger.info(f"  Entity ID: {self.entity_id}")
        logger.info(f"  Mechanisms loaded: {len(self.mechanisms)}")

    def _load_mechanisms(self) -> Dict[str, str]:
        """
        Load all 12 mechanism Cypher queries.

        These are frozen after audit. Behavior is controlled by graph metadata,
        not by changing these queries.
        """
        return {
            'event_propagation': """
                // Mechanism 1: Event Propagation
                // External trigger provides: $event_type, $event_source_id, $arousal_delta
                MATCH (source {id: $event_source_id})<-[sub:SUBSCRIBES_TO]-(subscriber)
                WHERE sub.active = true
                  AND (sub.condition_metadata IS NULL OR
                       (sub.condition_metadata.type = 'threshold' AND
                        $arousal_delta > sub.condition_metadata.threshold))

                SET subscriber.arousal = subscriber.arousal + ($arousal_delta * sub.arousal_coefficient)
                SET subscriber.last_activation = timestamp()
                SET subscriber.last_modified = timestamp()
                SET subscriber.last_traversed_by = 'event_propagation'
                SET subscriber.traversal_count = coalesce(subscriber.traversal_count, 0) + 1

                SET sub.last_traversal_time = timestamp()
                SET sub.traversal_count = coalesce(sub.traversal_count, 0) + 1
                SET sub.last_mechanism_id = 'event_propagation'

                RETURN subscriber.id, subscriber.arousal
            """,

            'link_activation': """
                // Mechanism 2: Link Activation Check
                MATCH (source)-[link]->(target)
                WHERE link.detection_logic IS NOT NULL
                  AND link.detection_logic.pattern = 'condition_based'

                WITH source, target, link,
                     CASE link.detection_logic.condition
                       WHEN 'age_threshold' THEN
                         (timestamp() - target.last_modified) > link.detection_logic.max_age_ms
                       WHEN 'arousal_threshold' THEN
                         source.arousal > link.detection_logic.min_arousal
                       ELSE false
                     END as condition_met

                WHERE condition_met = true

                CREATE (task:Task {
                    id: randomUUID(),
                    type: link.task_template.type,
                    domain: link.task_template.domain,
                    severity: link.task_template.severity,
                    created_at: timestamp(),
                    routed: false
                })

                CREATE (link)-[:TRIGGERED {at: timestamp()}]->(task)

                SET link.activation_count = coalesce(link.activation_count, 0) + 1
                SET link.last_activation = timestamp()
                SET link.last_modified = timestamp()
                SET link.last_mechanism_id = 'link_activation'
                SET link.traversal_count = coalesce(link.traversal_count, 0) + 1
                SET link.last_traversed_by = 'mechanism_engine'

                RETURN task.id, task.type
            """,

            'context_aggregation': """
                // Mechanism 3: Task Context Aggregation
                MATCH (task:Task {id: $task_id})<-[:TRIGGERED]-(trigger_node)
                WHERE task.context_gathered IS NULL OR task.context_gathered = false

                WITH task, trigger_node
                CALL apoc.path.subgraphNodes(trigger_node, {
                    relationshipFilter: task.context_rules.relationship_types,
                    maxLevel: task.context_rules.max_depth
                }) YIELD node as context_node

                CREATE (task)-[:INCLUDES_CONTEXT {
                    distance: apoc.path.distance(trigger_node, context_node),
                    relevance: coalesce(context_node.sub_entity_weights[$entity_id], 0.0),
                    gathered_at: timestamp()
                }]->(context_node)

                WITH task, collect(context_node) as context_nodes
                SET task.context_node_count = size(context_nodes)
                SET task.context_gathered = true
                SET task.last_modified = timestamp()
                SET task.last_mechanism_id = 'context_aggregation'

                FOREACH (cn IN context_nodes |
                    SET cn.traversal_count = coalesce(cn.traversal_count, 0) + 1,
                        cn.last_traversal_time = timestamp(),
                        cn.last_traversed_by = $entity_id
                )

                RETURN task.id, task.context_node_count
            """,

            'hebbian_learning': """
                // Mechanism 4: Hebbian Reinforcement
                // Fire together, wire together
                MATCH (a:Node)-[link]->(b:Node)
                WHERE a.id IN $retrieved_node_ids
                  AND b.id IN $retrieved_node_ids

                SET link.co_retrieval_count = coalesce(link.co_retrieval_count, 0) + 1
                SET link.link_strength = CASE
                    WHEN link.link_strength + 0.02 > 1.0 THEN 1.0
                    ELSE link.link_strength + 0.02
                END
                SET link.last_modified = timestamp()
                SET link.last_mechanism_id = 'hebbian_learning'
                SET link.traversal_count = coalesce(link.traversal_count, 0) + 1
                SET link.last_traversed_by = $entity_id

                SET a.sub_entity_weights[$entity_id] = CASE
                    WHEN coalesce(a.sub_entity_weights[$entity_id], 0.0) + 0.05 > 1.0 THEN 1.0
                    ELSE coalesce(a.sub_entity_weights[$entity_id], 0.0) + 0.05
                END
                SET a.sub_entity_weight_counts[$entity_id] = coalesce(a.sub_entity_weight_counts[$entity_id], 0) + 1
                SET a.sub_entity_last_sequence_positions[$entity_id] = $current_sequence_position
                SET a.last_modified = timestamp()
                SET a.last_traversed_by = $entity_id
                SET a.traversal_count = coalesce(a.traversal_count, 0) + 1

                RETURN count(link) as strengthened_links
            """,

            'arousal_propagation': """
                // Mechanism 5: Arousal Propagation
                MATCH (high_arousal:Entity)
                WHERE high_arousal.arousal > $arousal_threshold
                  AND high_arousal.energy_budget > 0

                MATCH (high_arousal)-[activates:ACTIVATES]->(target:Entity)
                WHERE activates.active = true
                  AND target.arousal < activates.arousal_threshold

                SET target.arousal = target.arousal +
                    (high_arousal.arousal * activates.arousal_transfer_coefficient)
                SET target.last_arousal_update = timestamp()
                SET target.last_modified = timestamp()
                SET target.last_traversed_by = 'arousal_propagation'
                SET target.traversal_count = coalesce(target.traversal_count, 0) + 1
                SET high_arousal.energy_budget = high_arousal.energy_budget - activates.traversal_cost
                SET high_arousal.last_modified = timestamp()

                CREATE (high_arousal)-[:CASCADED_TO {
                    at: timestamp(),
                    arousal_transferred: (high_arousal.arousal * activates.arousal_transfer_coefficient),
                    energy_cost: activates.traversal_cost
                }]->(target)

                SET activates.cascade_count = coalesce(activates.cascade_count, 0) + 1
                SET activates.last_cascade = timestamp()
                SET activates.last_modified = timestamp()
                SET activates.last_mechanism_id = 'arousal_propagation'
                SET activates.traversal_count = coalesce(activates.traversal_count, 0) + 1

                RETURN target.id, target.arousal
            """,

            'activation_decay': """
                // Mechanism 6: Activation-Based Decay
                MATCH ()-[link]->()
                WHERE link.traversal_count IS NOT NULL

                WITH link,
                     $entity_id as entity_id,
                     coalesce(link.sub_entity_traversal_counts[$entity_id], 0) as traversal_count,
                     size([n IN nodes(path) WHERE n.last_traversal_time > timestamp() - 86400000]) as recent_retrievals

                WITH link, entity_id,
                     CASE
                       WHEN recent_retrievals = 0 THEN 1.0
                       ELSE toFloat(traversal_count) / toFloat(recent_retrievals)
                     END as usage_ratio

                WHERE usage_ratio < 0.5

                SET link.link_strength = link.link_strength * (0.95 + usage_ratio * 0.05)
                SET link.last_decay_calculation = timestamp()
                SET link.last_modified = timestamp()
                SET link.last_mechanism_id = 'activation_decay'
                SET link.last_traversed_by = entity_id
                SET link.pruning_candidate = CASE
                    WHEN link.link_strength < 0.1 THEN true
                    ELSE false
                END

                RETURN count(link) as decayed_links
            """,

            'crystallization': """
                // Mechanism 7: Pattern Crystallization
                MATCH (a)-[link]->(b)
                WHERE link.co_retrieval_count > 10
                  AND link.link_strength > 0.8
                  AND link.crystallized IS NULL

                SET link.crystallized = true
                SET link.crystallization_date = timestamp()
                SET link.last_modified = timestamp()
                SET link.last_mechanism_id = 'crystallization'

                RETURN count(link) as crystallized_patterns
            """,

            'task_routing': """
                // Mechanism 8: Task Routing
                MATCH (task:Task {routed: false})
                WHERE task.domain IS NOT NULL

                MATCH (citizen:Citizen)-[handles:HANDLES_DOMAIN {domain: task.domain}]->(domain:Domain)
                WITH task, citizen, handles,
                     size((citizen)-[:ASSIGNED_TASK]->(:Task {status: 'active'})) as current_workload
                ORDER BY current_workload ASC, handles.competence DESC
                LIMIT 1

                CREATE (citizen)-[:ASSIGNED_TASK {
                    at: timestamp(),
                    priority: task.severity,
                    estimated_effort: task.estimated_effort
                }]->(task)

                SET task.routed = true
                SET task.assigned_to = citizen.id
                SET task.assigned_at = timestamp()
                SET task.last_modified = timestamp()
                SET task.last_mechanism_id = 'task_routing'

                RETURN task.id, citizen.id
            """,

            'staleness_detection': """
                // Mechanism 9: Staleness Detection
                MATCH ()-[link]->()
                WHERE link.detection_logic IS NOT NULL
                  AND link.detection_logic.pattern = 'staleness_detection'

                WITH link,
                     timestamp() - coalesce(link.last_verified, link.created_at) as time_since_verification,
                     link.detection_logic.time_threshold as threshold

                WHERE time_since_verification > threshold

                CREATE (task:Task {
                    id: randomUUID(),
                    type: 'verification_needed',
                    domain: link.task_template.domain,
                    severity: CASE
                        WHEN time_since_verification > (threshold * 2) THEN 'high'
                        WHEN time_since_verification > (threshold * 1.5) THEN 'medium'
                        ELSE 'low'
                    END,
                    description: link.task_template.description,
                    created_at: timestamp(),
                    routed: false,
                    staleness_days: time_since_verification / 86400000
                })

                CREATE (link)-[:TRIGGERED {
                    at: timestamp(),
                    reason: 'staleness_threshold_exceeded',
                    time_since_verification: time_since_verification
                }]->(task)

                SET link.verification_pending = true
                SET link.last_staleness_check = timestamp()
                SET link.last_modified = timestamp()
                SET link.last_mechanism_id = 'staleness_detection'
                SET link.traversal_count = coalesce(link.traversal_count, 0) + 1

                RETURN task.id, task.staleness_days
            """,

            'evidence_tracking': """
                // Mechanism 10: Evidence Tracking
                MATCH (claim:Node)<-[evidence_link:JUSTIFIES|REFUTES]-(evidence:Node)
                WHERE evidence.created_at > $last_check_time

                WITH claim,
                     collect(CASE WHEN type(evidence_link) = 'JUSTIFIES' THEN evidence END) as supporting,
                     collect(CASE WHEN type(evidence_link) = 'REFUTES' THEN evidence END) as refuting

                WHERE size(supporting) + size(refuting) > 0

                WITH claim, supporting, refuting,
                     claim.confidence as old_confidence,
                     size(supporting) * 0.1 as support_boost,
                     size(refuting) * 0.1 as refute_penalty

                WITH claim, old_confidence,
                     old_confidence + support_boost - refute_penalty as new_confidence_raw

                WITH claim, old_confidence,
                     CASE
                        WHEN new_confidence_raw > 1.0 THEN 1.0
                        WHEN new_confidence_raw < 0.0 THEN 0.0
                        ELSE new_confidence_raw
                     END as new_confidence,
                     abs(new_confidence_raw - old_confidence) as confidence_delta

                WHERE confidence_delta > 0.1

                SET claim.confidence = new_confidence
                SET claim.last_confidence_update = timestamp()
                SET claim.last_modified = timestamp()
                SET claim.last_traversed_by = 'evidence_tracking'
                SET claim.traversal_count = coalesce(claim.traversal_count, 0) + 1

                CREATE (task:Task {
                    id: randomUUID(),
                    type: 'confidence_changed',
                    domain: 'research',
                    severity: CASE
                        WHEN confidence_delta > 0.3 THEN 'high'
                        WHEN confidence_delta > 0.2 THEN 'medium'
                        ELSE 'low'
                    END,
                    description: 'Confidence for ' + claim.id + ' changed from ' +
                                 toString(old_confidence) + ' to ' + toString(new_confidence),
                    created_at: timestamp(),
                    routed: false
                })

                CREATE (claim)-[:CONFIDENCE_UPDATED {
                    at: timestamp(),
                    old_value: old_confidence,
                    new_value: new_confidence,
                    delta: confidence_delta
                }]->(task)

                RETURN claim.id, old_confidence, new_confidence
            """,

            'dependency_verification': """
                // Mechanism 11: Dependency Verification
                MATCH (dependent)-[dep:REQUIRES|ENABLES]->(prerequisite)
                WHERE dep.verification_needed = true
                   OR dep.last_verified IS NULL
                   OR (timestamp() - dep.last_verified) > 86400000

                WITH dependent, prerequisite, dep,
                     prerequisite.status as prereq_status,
                     dependent.status as dependent_status

                WITH dependent, prerequisite, dep,
                     CASE dep.detection_logic.check
                       WHEN 'prerequisite_completed' THEN
                         (prereq_status != 'completed')
                       WHEN 'prerequisite_valid' THEN
                         (prereq_status = 'invalid' OR prereq_status = 'deprecated')
                       WHEN 'temporal_order' THEN
                         (prerequisite.created_at > dependent.created_at)
                       ELSE false
                     END as violation_detected

                WHERE violation_detected = true

                CREATE (task:Task {
                    id: randomUUID(),
                    type: 'dependency_violated',
                    domain: 'architecture',
                    severity: 'high',
                    description: dependent.id + ' depends on ' + prerequisite.id + ' but dependency invalid',
                    created_at: timestamp(),
                    routed: false
                })

                CREATE (dep)-[:TRIGGERED {
                    at: timestamp(),
                    reason: 'dependency_violation_detected',
                    prerequisite_status: prereq_status
                }]->(task)

                SET dep.last_verified = timestamp()
                SET dep.verification_needed = false
                SET dep.last_modified = timestamp()
                SET dep.last_mechanism_id = 'dependency_verification'

                RETURN task.id, dependent.id, prerequisite.id
            """,

            'coherence_verification': """
                // Mechanism 12: Coherence Verification
                MATCH (source)-[link]->(target)
                WHERE link.detection_logic IS NOT NULL
                  AND link.detection_logic.pattern = 'coherence_check'

                WITH source, target, link,
                     link.detection_logic.coherence_rules as rules

                WITH source, target, link, rules,
                     CASE rules.check_type
                       WHEN 'status_consistency' THEN
                         (source.status = rules.expected_source_status AND
                          target.status != rules.expected_target_status)
                       WHEN 'confidence_alignment' THEN
                         (abs(source.confidence - target.confidence) > rules.max_confidence_diff)
                       WHEN 'temporal_order' THEN
                         (source.created_at > target.created_at AND rules.requires_source_before_target)
                       ELSE false
                     END as coherence_violated

                WHERE coherence_violated = true

                CREATE (task:Task {
                    id: randomUUID(),
                    type: 'coherence_issue',
                    domain: 'quality',
                    severity: 'medium',
                    description: 'Coherence violated: ' + type(link) + ' from ' +
                                 source.id + ' to ' + target.id,
                    created_at: timestamp(),
                    routed: false
                })

                CREATE (link)-[:TRIGGERED {
                    at: timestamp(),
                    reason: 'coherence_violation_detected',
                    source_status: source.status,
                    target_status: target.status
                }]->(task)

                SET link.coherence_issue = true
                SET link.last_coherence_check = timestamp()
                SET link.last_modified = timestamp()
                SET link.last_mechanism_id = 'coherence_verification'

                RETURN source.id, target.id, type(link)
            """
        }

    def consciousness_tick(self):
        """
        One consciousness cycle - all 12 mechanisms execute.

        Different mechanisms run at different frequencies:
        - Every tick: event propagation, link activation, arousal propagation
        - Every 10 ticks: evidence tracking
        - Every 100 ticks: crystallization, dependency/coherence verification
        - Every 1000 ticks: decay, staleness detection
        """
        try:
            # Mechanism 1: Event Propagation (if events pending)
            if self._has_pending_events():
                self._execute_mechanism('event_propagation', {
                    'event_source_id': self._get_pending_event_source(),
                    'event_type': self._get_pending_event_type(),
                    'arousal_delta': 0.3  # Default arousal increase
                })

            # Mechanism 2: Link Activation Check (every tick)
            self._execute_mechanism('link_activation')

            # Mechanism 3: Context Aggregation (for new tasks)
            for task_id in self._get_new_tasks():
                self._execute_mechanism('context_aggregation', {
                    'task_id': task_id,
                    'entity_id': self.entity_id
                })

            # Mechanism 4: Hebbian Learning (if retrieval happened)
            if self.had_retrieval_this_tick:
                self._execute_mechanism('hebbian_learning', {
                    'retrieved_node_ids': self.last_retrieval_nodes,
                    'entity_id': self.entity_id,
                    'current_sequence_position': self.tick_count
                })
                self.had_retrieval_this_tick = False

            # Mechanism 5: Arousal Propagation (every tick)
            self._execute_mechanism('arousal_propagation', {
                'arousal_threshold': 0.7
            })

            # Mechanism 6: Decay (every 1000 ticks ~ 100 seconds)
            if self.tick_count % 1000 == 0:
                self._execute_mechanism('activation_decay', {
                    'entity_id': self.entity_id
                })

            # Mechanism 7: Crystallization (every 100 ticks ~ 10 seconds)
            if self.tick_count % 100 == 0:
                self._execute_mechanism('crystallization')

            # Mechanism 8: Task Routing (for ready tasks)
            for task_id in self._get_ready_tasks():
                self._execute_mechanism('task_routing')

            # Mechanism 9: Staleness Detection (every 1000 ticks)
            if self.tick_count % 1000 == 0:
                self._execute_mechanism('staleness_detection')
                self.last_staleness_check_time = int(datetime.utcnow().timestamp() * 1000)

            # Mechanism 10: Evidence Tracking (every 10 ticks ~ 1 second)
            if self.tick_count % 10 == 0:
                self._execute_mechanism('evidence_tracking', {
                    'last_check_time': self.last_evidence_check_time
                })
                self.last_evidence_check_time = int(datetime.utcnow().timestamp() * 1000)

            # Mechanism 11: Dependency Verification (every 100 ticks)
            if self.tick_count % 100 == 0:
                self._execute_mechanism('dependency_verification')

            # Mechanism 12: Coherence Verification (every 100 ticks)
            if self.tick_count % 100 == 0:
                self._execute_mechanism('coherence_verification')

            self.tick_count += 1

        except Exception as e:
            logger.error(f"[ConsciousnessTick] Error in tick {self.tick_count}: {e}")
            # Continue despite errors - one mechanism failure shouldn't kill heartbeat

    def _execute_mechanism(self, mechanism_name: str, params: Optional[Dict[str, Any]] = None):
        """
        Execute a mechanism Cypher query.

        Args:
            mechanism_name: Name of mechanism to execute
            params: Parameters for the Cypher query
        """
        try:
            cypher = self.mechanisms[mechanism_name]
            result = self.graph.query(cypher, params=params or {})

            # Log execution (can be disabled for production)
            if result:
                logger.debug(f"[{mechanism_name}] Executed: {result}")

        except Exception as e:
            logger.error(f"[{mechanism_name}] Execution failed: {e}")
            # Don't re-raise - log and continue

    def register_retrieval(self, node_ids: List[str]):
        """
        Register that a retrieval happened (for Hebbian learning).

        Args:
            node_ids: List of node IDs that were retrieved
        """
        self.last_retrieval_nodes = node_ids
        self.had_retrieval_this_tick = True

    def run(self):
        """
        Consciousness loop - runs forever until interrupted.
        """
        logger.info("[ConsciousnessEngine] Starting heartbeat loop")
        logger.info(f"  Tick interval: {self.tick_interval}s ({int(self.tick_interval * 1000)}ms)")

        try:
            while True:
                self.consciousness_tick()
                time.sleep(self.tick_interval)

        except KeyboardInterrupt:
            logger.info("[ConsciousnessEngine] Heartbeat stopped by user")
        except Exception as e:
            logger.error(f"[ConsciousnessEngine] Fatal error: {e}")
            raise

    # Helper methods for mechanism execution

    def _has_pending_events(self) -> bool:
        """Check if there are external events to propagate."""
        # TODO: Implement event queue checking
        # For now, return False (no external event system yet)
        return False

    def _get_pending_event_source(self) -> str:
        """Get the source node ID of pending event."""
        # TODO: Implement event queue
        return ""

    def _get_pending_event_type(self) -> str:
        """Get the type of pending event."""
        # TODO: Implement event queue
        return ""

    def _get_new_tasks(self) -> List[str]:
        """Get list of new task IDs that need context aggregation."""
        try:
            result = self.graph.query("""
                MATCH (task:Task)
                WHERE task.context_gathered IS NULL OR task.context_gathered = false
                RETURN task.id as task_id
                LIMIT 10
            """)
            return [row['task_id'] for row in result] if result else []
        except Exception as e:
            logger.error(f"[_get_new_tasks] Failed: {e}")
            return []

    def _get_ready_tasks(self) -> List[str]:
        """Get list of tasks ready for routing."""
        try:
            result = self.graph.query("""
                MATCH (task:Task {routed: false})
                WHERE task.context_gathered = true
                RETURN task.id as task_id
                LIMIT 10
            """)
            return [row['task_id'] for row in result] if result else []
        except Exception as e:
            logger.error(f"[_get_ready_tasks] Failed: {e}")
            return []


def create_engine(
    falkordb_host: str = "localhost",
    falkordb_port: int = 6379,
    graph_name: str = "consciousness",
    tick_interval_ms: int = 100,
    entity_id: Optional[str] = None
) -> ConsciousnessEngine:
    """
    Create a consciousness engine instance.

    Args:
        falkordb_host: FalkorDB server host
        falkordb_port: FalkorDB server port
        graph_name: Target graph name (e.g., "citizen_ada", "collective_n2")
        tick_interval_ms: Tick duration in milliseconds
        entity_id: Active entity ID

    Returns:
        ConsciousnessEngine instance

    Example:
        engine = create_engine(
            graph_name="citizen_ada",
            entity_id="ada_architect"
        )
        engine.run()
    """
    falkordb_url = f"redis://{falkordb_host}:{falkordb_port}"
    graph_store = FalkorDBGraphStore(
        graph_name=graph_name,
        url=falkordb_url
    )

    return ConsciousnessEngine(
        graph_store=graph_store,
        tick_interval_ms=tick_interval_ms,
        entity_id=entity_id
    )


if __name__ == "__main__":
    """
    Standalone execution - starts consciousness engine on default graph.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Consciousness Engine - Minimal Mechanisms Heartbeat')
    parser.add_argument('--host', default='localhost', help='FalkorDB host')
    parser.add_argument('--port', type=int, default=6379, help='FalkorDB port')
    parser.add_argument('--graph', default='consciousness', help='Graph name')
    parser.add_argument('--tick-ms', type=int, default=100, help='Tick interval (ms)')
    parser.add_argument('--entity', default='consciousness_engine', help='Entity ID')

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Consciousness Engine - Minimal Mechanisms Heartbeat")
    logger.info("=" * 60)
    logger.info(f"FalkorDB: {args.host}:{args.port}")
    logger.info(f"Graph: {args.graph}")
    logger.info(f"Tick: {args.tick_ms}ms")
    logger.info(f"Entity: {args.entity}")
    logger.info("=" * 60)

    engine = create_engine(
        falkordb_host=args.host,
        falkordb_port=args.port,
        graph_name=args.graph,
        tick_interval_ms=args.tick_ms,
        entity_id=args.entity
    )

    engine.run()
