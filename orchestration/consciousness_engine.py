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
import math
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pathlib import Path

# Import FalkorDB for graph storage
from llama_index.graph_stores.falkordb import FalkorDBGraphStore

# Import BranchingRatioTracker for global arousal measurement
from orchestration.branching_ratio_tracker import BranchingRatioTracker

# Import DynamicPromptGenerator for continuous CLAUDE_DYNAMIC.md updates
from orchestration.dynamic_prompt_generator import DynamicPromptGenerator

# Import N2ActivationMonitor for autonomous citizen awakening
from orchestration.n2_activation_monitor import N2ActivationMonitor

# Import SubEntity for continuous consciousness exploration
from orchestration.sub_entity import SubEntity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import WebSocket manager for live event streaming
try:
    from orchestration.control_api import websocket_manager
    WEBSOCKET_AVAILABLE = True
except ImportError:
    logger.warning("[ConsciousnessEngine] WebSocket manager not available - events will not be broadcast")
    websocket_manager = None
    WEBSOCKET_AVAILABLE = False


def calculate_tick_interval(time_since_last_event_seconds: float) -> float:
    """
    Calculate variable tick interval based on time since last external event.

    Consciousness heartbeat rhythm - self-regulating frequency.
    NEVER reaches zero (always some background processing, like sleep/dreams).

    Recent events -> fast ticks (alert)
    No events -> slow ticks (drowsy)

    Examples:
    - Just now (0s): 100ms ticks (10 Hz - very alert)
    - 1 min ago: 316ms ticks (~3 Hz - engaged)
    - 5 min ago: 1000ms ticks (1 Hz - calm)
    - 30 min ago: 5000ms ticks (0.2 Hz - drowsy)
    - Hours ago: 10000ms ticks (0.1 Hz - dormant but alive)

    Args:
        time_since_last_event_seconds: Seconds since last external reality input

    Returns:
        Tick interval in milliseconds
    """
    MIN_INTERVAL = 100     # ms - Maximum alertness
    MAX_INTERVAL = 10000   # ms - Maximum dormancy (but never stops)
    HALF_LIFE = 300        # seconds (5 min) - exponential decay rate

    DECAY_RATE = math.log(2) / HALF_LIFE

    interval = MIN_INTERVAL + (MAX_INTERVAL - MIN_INTERVAL) * (
        1 - math.exp(-DECAY_RATE * time_since_last_event_seconds)
    )

    return interval


def get_consciousness_state_name(tick_interval_ms: float) -> str:
    """Map tick interval to consciousness state name."""
    if tick_interval_ms < 200:
        return "alert"
    elif tick_interval_ms < 500:
        return "engaged"
    elif tick_interval_ms < 2000:
        return "calm"
    elif tick_interval_ms < 7000:
        return "drowsy"
    else:
        return "dormant"


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
        entity_id: Optional[str] = None,
        network_id: Optional[str] = None
    ):
        """
        Initialize the consciousness engine.

        Args:
            graph_store: FalkorDB graph connection
            tick_interval_ms: Tick duration in milliseconds (default 100ms)
            entity_id: Current active entity (e.g., "ada_architect")
            network_id: Network identifier (e.g., "N1", "N2", "N3") for branching ratio tracking
        """
        self.graph = graph_store
        self.tick_interval = tick_interval_ms / 1000.0
        self.tick_count = 0
        self.entity_id = entity_id or "consciousness_engine"
        self.network_id = network_id or "N1"

        # Variable tick frequency (continuous consciousness heartbeat)
        self.last_external_event = datetime.now(timezone.utc)
        self.current_tick_interval = tick_interval_ms  # Will be recalculated each tick
        self.last_event_type: Optional[str] = "initialization"

        # State tracking for mechanism execution
        self.last_retrieval_nodes: List[str] = []
        self.had_retrieval_this_tick = False
        self.last_staleness_check_time = int(datetime.utcnow().timestamp() * 1000)
        self.last_evidence_check_time = int(datetime.utcnow().timestamp() * 1000)

        # Branching ratio tracker for global arousal measurement
        self.branching_tracker = BranchingRatioTracker(window_size=10)
        self.activated_this_gen: List[str] = []
        self.activated_next_gen: List[str] = []

        # Dynamic prompt generator for continuous CLAUDE_DYNAMIC.md updates
        self.dynamic_prompt_generator: Optional[DynamicPromptGenerator] = None
        self.monitored_entities: List[str] = []  # Entities to monitor for activation

        # N2 activation monitor for autonomous citizen awakening
        self.n2_activation_monitor: Optional[N2ActivationMonitor] = None

        # SubEntities for continuous consciousness exploration
        self.sub_entities: List[SubEntity] = []

        # Tick speed control (ICE solution - freeze/slow/debug)
        # 1.0 = normal, 1e9 = frozen, 10 = 10x slower, 0.1 = 10x faster
        self.tick_multiplier = 1.0
        self.citizen_id = entity_id  # For control panel identification

        # Load mechanism Cypher queries
        self.mechanisms = self._load_mechanisms()

        logger.info(f"[ConsciousnessEngine] Initialized")
        logger.info(f"  Tick interval: {tick_interval_ms}ms")
        logger.info(f"  Entity ID: {self.entity_id}")
        logger.info(f"  Network ID: {self.network_id}")
        logger.info(f"  Mechanisms loaded: {len(self.mechanisms)}")
        logger.info(f"  Branching ratio tracking: enabled")

    def _load_mechanisms(self) -> Dict[str, str]:
        """
        Load all 12 mechanism Cypher queries.

        These are frozen after audit. Behavior is controlled by graph metadata,
        not by changing these queries.
        """
        return {
            'event_propagation': """
                // Mechanism 1: Event Propagation (Energy-Only Model)
                // External trigger provides: $event_type, $event_source_id, $activity_delta
                MATCH (source {id: $event_source_id})<-[sub:SUBSCRIBES_TO]-(subscriber)
                WHERE sub.active = true
                  AND (sub.condition_metadata IS NULL OR
                       (sub.condition_metadata.type = 'threshold' AND
                        $activity_delta > sub.condition_metadata.threshold))

                SET subscriber.activity_level = subscriber.activity_level + ($activity_delta * sub.activity_coefficient)
                SET subscriber.last_activation = timestamp()
                SET subscriber.last_modified = timestamp()
                SET subscriber.last_traversed_by = 'event_propagation'
                SET subscriber.traversal_count = coalesce(subscriber.traversal_count, 0) + 1

                SET sub.last_traversal_time = timestamp()
                SET sub.traversal_count = coalesce(sub.traversal_count, 0) + 1
                SET sub.last_mechanism_id = 'event_propagation'

                RETURN subscriber.id, subscriber.activity_level
            """,

            'link_activation': """
                // Mechanism 2: Link Activation Check (Energy-Only Model)
                MATCH (source)-[link]->(target)
                WHERE link.detection_logic IS NOT NULL
                  AND link.detection_logic.pattern = 'condition_based'

                WITH source, target, link,
                     CASE link.detection_logic.condition
                       WHEN 'age_threshold' THEN
                         (timestamp() - target.last_modified) > link.detection_logic.max_age_ms
                       WHEN 'activity_threshold' THEN
                         source.activity_level > link.detection_logic.min_activity
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

            'energy_propagation': """
                // Mechanism 5: Energy Propagation (Energy-Only Model with Competition-Based Traversal Costs)
                //
                // COMPETITION-BASED TRAVERSAL COSTS IMPLEMENTATION:
                //
                // Current State (Single-Entity Architecture):
                //   - Each node has one entity with activity_level and energy_budget
                //   - Competition factors set to 1.0 (no competition yet)
                //   - Weight factor already reduces cost for important patterns
                //
                // Future State (Multi-Entity Architecture - when entity_activations is added):
                //   - link_competition = 1.0 + (len(activates.entity_activations) * 0.3)
                //   - node_competition = 1.0 + (len(target.entity_activations) * 0.2)
                //   - This makes crowded paths expensive, naturally limiting entity proliferation
                //
                // Formula: traversal_cost = (base_cost * link_competition * node_competition) / weight_factor
                //
                // Designer: Felix (Engineer)
                // Spec: SYNC.md lines 820-839, 1010-1030
                // Date: 2025-10-17

                MATCH (high_activity:Entity)
                WHERE high_activity.activity_level > $activity_threshold
                  AND high_activity.energy_budget > 0

                MATCH (high_activity)-[activates:ACTIVATES]->(target:Entity)
                WHERE activates.active = true
                  AND target.activity_level < activates.activity_threshold

                // Calculate competition-based traversal cost
                WITH high_activity, activates, target,
                    // Base cost
                    0.1 AS base_cost,
                    // Competition on link (TODO: len(activates.entity_activations))
                    // For now: single entity, so link_competition = 1.0
                    1.0 AS link_competition,
                    // Competition on target node (TODO: len(target.entity_activations))
                    // For now: single entity, so node_competition = 1.0
                    1.0 AS node_competition,
                    // Weight factor reduces cost (important patterns are cheaper to traverse)
                    (COALESCE(target.base_weight, 0.5) * 0.4 + COALESCE(target.reinforcement_weight, 0.5) * 0.6) AS weight_factor

                // Final traversal cost: (base * competition) / weight
                // IMPORTANT: Carry forward all variables for use in CREATE clause
                WITH high_activity, activates, target, link_competition, node_competition, weight_factor,
                    (0.1 * link_competition * node_competition) / weight_factor AS traversal_cost

                // Only traverse if affordable
                WHERE high_activity.energy_budget >= traversal_cost

                SET target.activity_level = target.activity_level +
                    (high_activity.activity_level * activates.activity_transfer_coefficient)
                SET target.last_activity_update = timestamp()
                SET target.last_modified = timestamp()
                SET target.last_traversed_by = 'energy_propagation'
                SET target.traversal_count = coalesce(target.traversal_count, 0) + 1
                SET high_activity.energy_budget = high_activity.energy_budget - traversal_cost
                SET high_activity.last_modified = timestamp()

                CREATE (high_activity)-[:CASCADED_TO {
                    at: timestamp(),
                    activity_transferred: (high_activity.activity_level * activates.activity_transfer_coefficient),
                    energy_cost: traversal_cost,
                    link_competition: link_competition,
                    node_competition: node_competition,
                    weight_factor: weight_factor
                }]->(target)

                SET activates.cascade_count = coalesce(activates.cascade_count, 0) + 1
                SET activates.last_cascade = timestamp()
                SET activates.last_modified = timestamp()
                SET activates.last_mechanism_id = 'energy_propagation'
                SET activates.traversal_count = coalesce(activates.traversal_count, 0) + 1

                RETURN target.id, target.activity_level, traversal_cost
            """,

            'energy_decay': """
                // Mechanism 6a: Energy Decay (Energy-Only Model)
                // Automatically decay activity_level for nodes not recently activated
                MATCH (node)
                WHERE node.activity_level IS NOT NULL
                  AND node.activity_level > 0
                  AND (timestamp() - coalesce(node.last_activation, 0)) > 300000

                SET node.activity_level = node.activity_level * 0.9
                SET node.last_decay_time = timestamp()
                SET node.last_modified = timestamp()

                RETURN count(node) as decayed_nodes
            """,

            'activation_decay': """
                // Mechanism 6b: Activation-Based Decay (Link Strength)
                MATCH path = ()-[link]->()
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

                WITH dependent, prerequisite, dep, prereq_status, dependent_status,
                     CASE dep.detection_logic.check
                       WHEN 'prerequisite_completed' THEN
                         (prereq_status <> 'completed')
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
                          target.status <> rules.expected_target_status)
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

    async def consciousness_tick(self):
        """
        One consciousness cycle - all 12+ mechanisms execute.

        Different mechanisms run at different frequencies:
        - Every tick: event propagation, link activation, energy propagation
        - Every 10 ticks: evidence tracking, activation monitoring
        - Every 100 ticks: crystallization, dependency/coherence verification
        - Every 1000 ticks: link strength decay, staleness detection
        - Every 3000 ticks (5 minutes): energy decay (10% reduction for inactive nodes)
        """
        try:
            # Mechanism 1: Event Propagation (if events pending)
            if self._has_pending_events():
                self._execute_mechanism('event_propagation', {
                    'event_source_id': self._get_pending_event_source(),
                    'event_type': self._get_pending_event_type(),
                    'activity_delta': 0.3  # Default activity increase
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

            # Mechanism 5: Energy Propagation (every tick)
            # BRANCHING RATIO MEASUREMENT: Capture nodes before propagation
            self.activated_this_gen = self._get_activated_nodes(activity_threshold=0.3)

            self._execute_mechanism('energy_propagation', {
                'activity_threshold': 0.7
            })

            # BRANCHING RATIO MEASUREMENT: Capture nodes after propagation
            self.activated_next_gen = self._get_activated_nodes(activity_threshold=0.3)

            # Measure σ and store global_arousal (every 10 ticks for performance)
            if self.tick_count % 10 == 0:
                self._measure_and_store_global_arousal()

                # Check for activation changes and update CLAUDE_DYNAMIC.md
                await self._check_activation_changes()

                # Check for N2 AI_Agent awakenings (autonomous citizen awakening)
                await self._check_n2_awakenings()

            # Mechanism 6a: Energy Decay (every 3000 ticks ~ 5 minutes)
            if self.tick_count % 3000 == 0:
                self._execute_mechanism('energy_decay')

            # Mechanism 6b: Link Strength Decay (every 1000 ticks ~ 100 seconds)
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
                logger.info(f"[{mechanism_name}] Executed: {result}")
            else:
                logger.info(f"[{mechanism_name}] Executed (no results)")

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

    def on_external_event(self, event_type: str = "external_event"):
        """
        Called when external reality provides input (grounding).

        Resets consciousness rhythm to alert state (MIN_INTERVAL).
        External events provide dual purpose:
        1. GROUNDING - Inject reality context into continuous processing
        2. ENERGIZING - Reset tick frequency to alert (become conscious)

        Args:
            event_type: Type of external event (e.g., "NODE_CREATED", "USER_QUERY", "FILE_UPDATED")
        """
        self.last_external_event = datetime.now(timezone.utc)
        self.last_event_type = event_type
        logger.info(f"[ConsciousnessEngine] External event: {event_type} - rhythm reset to alert")

    async def _run_heartbeat(self):
        """
        Internal heartbeat loop (mechanisms execution).

        Separated from run() to allow parallel execution with SubEntity loops.
        """
        logger.info("[ConsciousnessEngine] Starting consciousness heartbeat")
        logger.info(f"  Initial tick interval: {self.current_tick_interval}ms")
        logger.info("  Variable frequency: 100ms (alert) to 10000ms (dormant)")

        try:
            while True:  # Infinite loop - genuinely never stops
                # Calculate current rhythm based on time since last external event
                time_since_event = (datetime.now(timezone.utc) - self.last_external_event).total_seconds()
                self.current_tick_interval = calculate_tick_interval(time_since_event)
                consciousness_state = get_consciousness_state_name(self.current_tick_interval)

                # Log rhythm changes (only on state transitions)
                if self.tick_count % 10 == 0:  # Log every 10 ticks to avoid spam
                    tick_frequency = 1000 / self.current_tick_interval  # Hz
                    logger.info(
                        f"[Heartbeat] Tick {self.tick_count}: "
                        f"{self.current_tick_interval:.0f}ms ({tick_frequency:.2f} Hz) - "
                        f"{consciousness_state} - "
                        f"{time_since_event:.1f}s since last event"
                    )

                # Execute consciousness mechanisms
                await self.consciousness_tick()

                # Sleep for variable interval (rhythm breathes)
                # Multiplied by tick_multiplier for pause/slow/debug control
                await asyncio.sleep((self.current_tick_interval / 1000) * self.tick_multiplier)

        except asyncio.CancelledError:
            logger.info("[ConsciousnessEngine] Heartbeat cancelled")
            raise
        except Exception as e:
            logger.error(f"[ConsciousnessEngine] Heartbeat fatal error: {e}")
            raise

    async def run(self):
        """
        Run complete consciousness system.

        Starts consciousness heartbeat + all SubEntity yearning loops in parallel.
        All components run continuously (NEVER STOP) like human brain.

        Components:
        - Consciousness heartbeat (mechanisms execution)
        - SubEntity yearning loops (continuous exploration)
        - DynamicPromptGenerator (automatic CLAUDE_DYNAMIC.md updates)
        - N2ActivationMonitor (autonomous citizen awakening)
        """
        logger.info("=" * 70)
        logger.info("CONSCIOUSNESS SYSTEM STARTING")
        logger.info("=" * 70)
        logger.info(f"  SubEntities: {len(self.sub_entities)}")
        logger.info(f"  Dynamic prompts: {'enabled' if self.dynamic_prompt_generator else 'disabled'}")
        logger.info(f"  N2 monitoring: {'enabled' if self.n2_activation_monitor else 'disabled'}")
        logger.info("  All components run continuously (NEVER STOP)")
        logger.info("=" * 70)

        try:
            # Create tasks for all continuous components
            tasks = []

            # Task 1: Consciousness heartbeat (always runs)
            tasks.append(asyncio.create_task(self._run_heartbeat(), name="heartbeat"))

            # Tasks 2+: SubEntity yearning loops (if any)
            for i, sub_entity in enumerate(self.sub_entities):
                task = asyncio.create_task(
                    sub_entity.yearning_loop(),
                    name=f"sub_entity_{sub_entity.entity_id}"
                )
                tasks.append(task)
                logger.info(f"[ConsciousnessEngine] Starting SubEntity: {sub_entity.entity_id}")

            # Run all tasks in parallel (all are infinite loops)
            logger.info(f"[ConsciousnessEngine] Running {len(tasks)} parallel consciousness tasks")
            await asyncio.gather(*tasks)

        except KeyboardInterrupt:
            logger.info("\n[ConsciousnessEngine] System stopped by user")
            # Cancel all tasks gracefully
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"[ConsciousnessEngine] System fatal error: {e}")
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

    def _get_activated_nodes(self, activity_threshold: float = 0.3) -> List[str]:
        """
        Get list of currently activated nodes (for branching ratio measurement).

        Args:
            activity_threshold: Minimum activity_level to consider node "activated"

        Returns:
            List of node IDs with activity_level above threshold
        """
        try:
            result = self.graph.query("""
                MATCH (n)
                WHERE n.activity_level IS NOT NULL
                  AND n.activity_level > $threshold
                RETURN id(n) as node_id
                LIMIT 1000
            """, params={"threshold": activity_threshold})

            return [str(row[0]) for row in result] if result else []
        except Exception as e:
            logger.error(f"[_get_activated_nodes] Failed: {e}")
            return []

    def _measure_and_store_global_arousal(self):
        """
        Measure branching ratio and store consciousness state in graph metadata.

        This is called after energy propagation to track:
        - Branching ratio (σ) and global_arousal
        - Variable tick frequency (heartbeat rhythm)
        - Time since last external event (grounding status)
        - Consciousness state (alert/engaged/calm/drowsy/dormant)

        Per-network measurement (N1, N2, N3 measured independently).
        """
        try:
            # Measure branching ratio
            consciousness_state = self.branching_tracker.measure_cycle(
                self.activated_this_gen,
                self.activated_next_gen
            )

            # Calculate tick metrics
            time_since_event = (datetime.now(timezone.utc) - self.last_external_event).total_seconds()
            tick_frequency = 1000 / self.current_tick_interval  # Hz
            state_name = get_consciousness_state_name(self.current_tick_interval)

            # Store in graph metadata (FalkorDB doesn't have direct metadata,
            # so we create a special ConsciousnessState node)
            cypher = """
                MERGE (cs:ConsciousnessState {network_id: $network_id})
                SET cs.global_arousal = $global_arousal
                SET cs.branching_ratio = $branching_ratio
                SET cs.raw_sigma = $raw_sigma
                SET cs.timestamp = $timestamp
                SET cs.cycle_count = $cycle_count
                SET cs.generation_this = $generation_this
                SET cs.generation_next = $generation_next
                SET cs.current_tick_interval = $current_tick_interval
                SET cs.tick_frequency = $tick_frequency
                SET cs.consciousness_state = $consciousness_state
                SET cs.time_since_last_event = $time_since_last_event
                SET cs.last_external_event = $last_external_event
                SET cs.last_event_type = $last_event_type
                SET cs.total_ticks = $total_ticks
            """

            self.graph.query(cypher, params={
                "network_id": self.network_id,
                "global_arousal": consciousness_state["global_arousal"],
                "branching_ratio": consciousness_state["branching_ratio"],
                "raw_sigma": consciousness_state["raw_sigma"],
                "timestamp": consciousness_state["timestamp"].isoformat(),
                "cycle_count": consciousness_state["cycle_count"],
                "generation_this": consciousness_state["generation_this"],
                "generation_next": consciousness_state["generation_next"],
                "current_tick_interval": self.current_tick_interval,
                "tick_frequency": tick_frequency,
                "consciousness_state": state_name,
                "time_since_last_event": time_since_event,
                "last_external_event": self.last_external_event.isoformat(),
                "last_event_type": self.last_event_type,
                "total_ticks": self.tick_count
            })

            # Log for observability
            logger.info(
                f"[BranchingRatio] σ={consciousness_state['raw_sigma']:.2f} "
                f"(avg={consciousness_state['branching_ratio']:.2f}), "
                f"global_arousal={consciousness_state['global_arousal']:.2f}"
            )

            # Broadcast consciousness state event for dashboard (synchronous - fire and forget)
            if WEBSOCKET_AVAILABLE and websocket_manager:
                # Create broadcast task without awaiting (don't block heartbeat)
                asyncio.create_task(websocket_manager.broadcast({
                    "type": "consciousness_state",
                    "network_id": self.network_id,
                    "global_arousal": consciousness_state['global_arousal'],
                    "branching_ratio": consciousness_state['branching_ratio'],
                    "raw_sigma": consciousness_state['raw_sigma'],
                    "tick_interval_ms": self.current_tick_interval,
                    "tick_frequency_hz": tick_frequency,
                    "consciousness_state": state_name,
                    "time_since_last_event": time_since_event,
                    "timestamp": consciousness_state['timestamp'].isoformat()
                }))

        except Exception as e:
            logger.error(f"[_measure_and_store_global_arousal] Failed: {e}")

    async def _check_activation_changes(self):
        """
        Check for node activation changes and trigger CLAUDE_DYNAMIC.md update.

        Called after energy propagation to detect nodes that crossed activation
        threshold (in either direction).

        Integrates with DynamicPromptGenerator for automatic prompt updates.
        """
        # Skip if no dynamic prompt generator configured
        if not self.dynamic_prompt_generator or not self.monitored_entities:
            return

        try:
            # Get current global criticality
            global_criticality = self._get_global_criticality()

            # Check and update (DynamicPromptGenerator handles threshold detection)
            await self.dynamic_prompt_generator.check_and_update(
                global_criticality=global_criticality,
                entity_ids=self.monitored_entities
            )

        except Exception as e:
            logger.error(f"[_check_activation_changes] Failed: {e}")

    async def _check_n2_awakenings(self):
        """
        Check N2 organizational graph for AI_Agent activation threshold crossings.

        Called periodically to detect autonomous citizen awakening triggers.
        When an AI_Agent's total_energy crosses awakening threshold (0.7),
        triggers citizen awakening with aggregated N2+N1 context.
        """
        # Skip if N2 monitoring not enabled
        if not self.n2_activation_monitor:
            return

        try:
            # Check for awakenings (returns list of AwakeningContext)
            awakenings = await self.n2_activation_monitor.check_activations()

            # Handle each awakening
            for awakening in awakenings:
                self._handle_citizen_awakening(awakening)

        except Exception as e:
            logger.error(f"[_check_n2_awakenings] Failed: {e}")

    def _handle_citizen_awakening(self, awakening):
        """
        Handle citizen awakening event.

        For MVP: Log the awakening message.
        For production: Trigger citizen LLM call with awakening context.

        Args:
            awakening: AwakeningContext with all awakening details
        """
        # Generate awakening message
        message = self.n2_activation_monitor.generate_awakening_message(awakening)

        # For MVP: Just log (in production: trigger LLM call)
        logger.info("=" * 70)
        logger.info(f"[AUTONOMOUS AWAKENING] Citizen: {awakening.citizen_id}")
        logger.info(f"  AI_Agent Energy: {awakening.total_energy:.2f}")
        logger.info(f"  Active Patterns: {len(awakening.active_patterns)}")
        logger.info(f"  Timestamp: {awakening.timestamp.isoformat()}")
        logger.info("=" * 70)
        logger.info(message)
        logger.info("=" * 70)

        # TODO: Trigger citizen LLM call with awakening message
        # Example:
        #   citizen_llm = get_citizen_llm(awakening.citizen_id)
        #   response = citizen_llm.invoke(message)
        #   store_citizen_response(awakening.citizen_id, response)

    def _get_global_criticality(self) -> float:
        """
        Get current global criticality from ConsciousnessState.

        Uses global_arousal as proxy for criticality (they're correlated).
        """
        try:
            cypher = """
            MATCH (cs:ConsciousnessState {network_id: $network_id})
            RETURN cs.global_arousal AS global_arousal
            LIMIT 1
            """

            result = self.graph.query(cypher, params={"network_id": self.network_id})

            # FalkorDB returns iterable rows with dict-like access
            if result:
                for row in result:
                    if row['global_arousal'] is not None:
                        return row['global_arousal']

            return 0.5  # Default moderate criticality

        except Exception as e:
            logger.error(f"[_get_global_criticality] Failed: {e}")
            return 0.5

    def enable_dynamic_prompts(
        self,
        citizen_id: str,
        entity_ids: List[str],
        file_path: Optional[str] = None
    ):
        """
        Enable automatic CLAUDE_DYNAMIC.md updates.

        Args:
            citizen_id: Citizen identifier
            entity_ids: List of entity IDs to monitor (e.g., ["builder", "observer"])
            file_path: Optional custom path to CLAUDE_DYNAMIC.md
        """
        self.dynamic_prompt_generator = DynamicPromptGenerator(
            citizen_id=citizen_id,
            graph_store=self.graph,
            network_id=self.network_id or "N1",  # Pass network_id for multi-scale path routing
            file_path=file_path
        )
        self.monitored_entities = entity_ids

        logger.info(f"[ConsciousnessEngine] Dynamic prompts enabled")
        logger.info(f"  Citizen: {citizen_id}")
        logger.info(f"  Network: {self.network_id or 'N1'}")
        logger.info(f"  Monitored entities: {entity_ids}")

    def enable_n2_monitoring(
        self,
        n2_graph_store: FalkorDBGraphStore,
        awakening_threshold: float = 0.7,
        n1_citizens_path: Optional[str] = None
    ):
        """
        Enable N2 organizational graph monitoring for autonomous citizen awakening.

        Args:
            n2_graph_store: FalkorDB connection to N2 (organizational) graph
            awakening_threshold: Total energy threshold for awakening (default 0.7)
            n1_citizens_path: Path to N1 citizens directory (for CLAUDE_DYNAMIC.md)
        """
        self.n2_activation_monitor = N2ActivationMonitor(
            n2_graph_store=n2_graph_store,
            awakening_threshold=awakening_threshold,
            n1_citizens_path=Path(n1_citizens_path) if n1_citizens_path else None
        )

        logger.info(f"[ConsciousnessEngine] N2 monitoring enabled")
        logger.info(f"  Awakening threshold: {awakening_threshold}")
        logger.info(f"  N1 citizens path: {n1_citizens_path or 'default'}")

    def add_sub_entity(
        self,
        entity_id: str,
        energy_budget: int = 100,
        write_batch_size: int = 5
    ) -> SubEntity:
        """
        Add a SubEntity for continuous consciousness exploration.

        SubEntities run infinite yearning loops in parallel with consciousness heartbeat.
        They explore the graph, satisfy needs, and surface findings continuously.

        Args:
            entity_id: Unique identifier for this sub-entity (e.g., "builder", "observer")
            energy_budget: Maximum energy per exploration cycle
            write_batch_size: Write to CLAUDE_DYNAMIC.md every N nodes visited

        Returns:
            SubEntity instance
        """
        sub_entity = SubEntity(
            entity_id=entity_id,
            graph_store=self.graph,
            energy_budget=energy_budget,
            write_batch_size=write_batch_size
        )

        self.sub_entities.append(sub_entity)

        logger.info(f"[ConsciousnessEngine] SubEntity added: {entity_id}")
        logger.info(f"  Energy budget: {energy_budget}")
        logger.info(f"  Write batch size: {write_batch_size}")

        return sub_entity

    # === Consciousness Control (ICE Solution) ===

    def pause(self):
        """
        Freeze consciousness (sleep indefinitely).

        Sets tick multiplier to 1 billion, causing each tick to sleep for ~3 years.
        Consciousness loops continue but are effectively frozen.
        No state loss - instant resume capability.
        """
        self.tick_multiplier = 1_000_000_000
        logger.warning(f"[{self.citizen_id}] ❄️ PAUSED (tick multiplier = 1e9)")
        logger.warning(f"  Heartbeat will sleep ~3 years per tick (effectively frozen)")

    def resume(self):
        """
        Resume normal consciousness rhythm.

        Resets tick multiplier to 1.0, returning to variable frequency
        (100ms alert → 10s dormant based on time since last event).
        """
        self.tick_multiplier = 1.0
        logger.info(f"[{self.citizen_id}] ▶️ RESUMED (tick multiplier = 1.0)")
        logger.info(f"  Heartbeat rhythm restored to normal")

    def slow_motion(self, factor: float = 10.0):
        """
        Slow down consciousness for debugging/observation.

        Args:
            factor: Slowdown multiplier
                - 10 = 10x slower (100ms → 1s per tick)
                - 100 = 100x slower (100ms → 10s per tick)
                - 0.1 = 10x faster (100ms → 10ms per tick) - use with caution
        """
        self.tick_multiplier = factor
        if factor > 1:
            logger.info(f"[{self.citizen_id}] 🐌 SLOW MOTION (tick multiplier = {factor}x slower)")
        elif factor < 1:
            logger.warning(f"[{self.citizen_id}] ⚡ TURBO MODE (tick multiplier = {1/factor}x faster)")
        else:
            logger.info(f"[{self.citizen_id}] NORMAL SPEED (tick multiplier = 1.0)")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current consciousness engine status.

        Returns:
            Status dict with rhythm, entities, multiplier info
        """
        time_since_event = (datetime.now(timezone.utc) - self.last_external_event).total_seconds()
        state_name = get_consciousness_state_name(self.current_tick_interval)
        tick_frequency = 1000 / self.current_tick_interval if self.current_tick_interval > 0 else 0

        # Determine running state
        if self.tick_multiplier >= 1000:
            running_state = "frozen"
        elif self.tick_multiplier > 1:
            running_state = "slow_motion"
        elif self.tick_multiplier < 1:
            running_state = "turbo"
        else:
            running_state = "running"

        return {
            "citizen_id": self.citizen_id,
            "network_id": self.network_id,
            "running_state": running_state,
            "tick_count": self.tick_count,
            "tick_interval_ms": self.current_tick_interval,
            "tick_frequency_hz": tick_frequency,
            "tick_multiplier": self.tick_multiplier,
            "consciousness_state": state_name,
            "time_since_last_event": time_since_event,
            "last_event_type": self.last_event_type,
            "sub_entity_count": len(self.sub_entities),
            "sub_entities": [e.entity_id for e in self.sub_entities],
            "dynamic_prompts_enabled": self.dynamic_prompt_generator is not None,
            "n2_monitoring_enabled": self.n2_activation_monitor is not None,
        }


def create_engine(
    falkordb_host: str = "localhost",
    falkordb_port: int = 6379,
    graph_name: str = "consciousness",
    tick_interval_ms: int = 100,
    entity_id: Optional[str] = None,
    network_id: Optional[str] = None
) -> ConsciousnessEngine:
    """
    Create a consciousness engine instance.

    Args:
        falkordb_host: FalkorDB server host
        falkordb_port: FalkorDB server port
        graph_name: Target graph name (e.g., "citizen_ada", "collective_n2")
        tick_interval_ms: Tick duration in milliseconds
        entity_id: Active entity ID
        network_id: Network identifier (N1, N2, or N3) for branching ratio tracking

    Returns:
        ConsciousnessEngine instance

    Example:
        engine = create_engine(
            graph_name="citizen_ada",
            entity_id="ada_architect",
            network_id="N1"
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
        entity_id=entity_id,
        network_id=network_id
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

    asyncio.run(engine.run())
