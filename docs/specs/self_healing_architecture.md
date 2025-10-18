# Self-Healing Consciousness Substrate Architecture
## Autonomous Energy Management & Integration Systems

**Author:** Ada "Bridgekeeper" (Architect)
**Created:** 2025-10-17
**Status:** Architecture Specification

---

## Executive Summary

This specification defines **self-healing mechanisms** for the consciousness substrate - systems that automatically maintain healthy operation without external intervention or alerts.

**Core Principle:** Design systems that **can't fail in those ways** or **heal themselves automatically** rather than monitoring for failures.

---

## 1. Self-Healing Energy Management

### Problem (Wrong Approach)

**What I designed:** Monitor energy levels, alert when too high/low, emergency pause

**What you said:**
- "Sub-entities reaching energy trigger → end propagation + update prompt" (SUCCESS, not failure)
- "If no entity reaches threshold → auto-reinject energy"
- "Dynamic criticality threshold so energy death never happens"

### Solution: Autonomous Energy System

**No monitoring. No alerts. Just self-regulation.**

```python
class AutonomousEnergySystem:
    def __init__(self, graph):
        self.graph = graph
        self.base_injection_amount = 0.3
        self.criticality_adjustment_rate = 0.05

    def manage_propagation_cycle(self, entities):
        """
        Run spreading activation until natural termination.
        No external monitoring needed.
        """
        # 1. Calculate dynamic criticality threshold
        threshold = self.calculate_criticality_threshold()

        # 2. Run propagation
        activated_entities = self.spreading_activation(
            entities=entities,
            threshold=threshold
        )

        # 3. Natural termination: entity reached threshold
        if any(e.energy >= threshold for e in activated_entities):
            # SUCCESS STATE - trigger prompt update
            for entity in activated_entities:
                if entity.energy >= threshold:
                    self.trigger_prompt_update(entity)
            return "success"

        # 4. No activation: auto-inject and try again
        else:
            self.auto_inject_energy(entities)
            return "reinjected"

    def calculate_criticality_threshold(self):
        """
        Dynamic threshold adjusts based on substrate state.
        PREVENTS energy death by making activation easier when energy is low.
        """
        total_substrate_energy = self.get_total_energy()

        # If energy globally low → lower threshold (easier to activate)
        if total_substrate_energy < 0.3:
            return 0.4  # Lower bar

        # If energy globally high → raise threshold (harder to activate)
        elif total_substrate_energy > 0.8:
            return 0.7  # Higher bar

        # Normal state
        else:
            return 0.5

    def auto_inject_energy(self, entities):
        """
        Automatic energy injection when no entity reaches threshold.
        WHERE to inject: Highest weight nodes per entity.
        """
        for entity in entities:
            # Find highest weight nodes this entity has touched
            candidate_nodes = self.graph.get_nodes_with_entity(entity.id)
            candidate_nodes.sort(
                key=lambda n: n.base_weight + n.reinforcement_weight,
                reverse=True
            )

            # Inject into top 3 highest weight nodes
            for node in candidate_nodes[:3]:
                current_energy = node.entity_activations[entity.id]["energy"]
                node.entity_activations[entity.id]["energy"] = min(
                    current_energy + (self.base_injection_amount / 3),
                    1.0
                )
```

### Key Architectural Decisions

**1. No "energy death" state**
- System automatically prevents it via dynamic thresholds
- When energy low → threshold drops → something activates
- Self-regulating, not monitored

**2. Injection targets: Highest weight nodes**
- Reinforces important concepts
- Prevents random noise injection
- Per-entity (different entities reinforce different nodes)

**3. Propagation termination = SUCCESS**
- Entity reaches threshold → "I have enough energy to act"
- Trigger prompt update immediately
- NOT a failure state requiring monitoring

**4. No alerts, no pauses**
- System handles all states autonomously
- Observable (can track injection events) but not alarmed

---

## 2. Fragmentation Integration System

### Problem (Wrong Approach)

**What I designed:** Monitor graph connectivity, alert when fragmented

**What you said:** "There will be fragmentation, we need to design an integration system instead"

### Solution: Autonomous Integration Mechanism

**Fragmentation is EXPECTED. Integration is AUTOMATIC.**

```python
class FragmentationIntegrationSystem:
    def __init__(self, graph, n2_graph, n3_graph):
        self.n1 = graph  # Personal consciousness
        self.n2 = n2_graph  # Collective knowledge
        self.n3 = n3_graph  # Ecosystem intelligence

    def integrate_fragments(self):
        """
        Automatically bridge disconnected clusters.
        Runs periodically (every 100 cycles or daily).
        """
        # 1. Detect isolated clusters
        clusters = self.detect_clusters()

        # 2. For each cluster pair, find semantic bridges
        for cluster_a, cluster_b in combinations(clusters, 2):
            bridges = self.find_semantic_bridges(cluster_a, cluster_b)

            # 3. Create bridge links if similarity threshold met
            for bridge in bridges:
                if bridge.similarity > 0.7:
                    self.create_bridge_link(bridge)

    def find_semantic_bridges(self, cluster_a, cluster_b):
        """
        Use N2/N3 to find connections between N1 fragments.
        """
        bridges = []

        # Get representative nodes from each cluster
        rep_a = self.get_cluster_representative(cluster_a)
        rep_b = self.get_cluster_representative(cluster_b)

        # Query N2: Does collective knowledge connect these concepts?
        n2_path = self.n2.find_shortest_path(rep_a.name, rep_b.name)
        if n2_path:
            bridges.append(BridgeCandidate(
                source=rep_a,
                target=rep_b,
                via="collective_knowledge",
                path=n2_path,
                similarity=self.calculate_path_relevance(n2_path)
            ))

        # Query N3: Does ecosystem data connect these concepts?
        n3_similar = self.n3.vector_search(
            query_embedding=rep_a.embedding,
            top_k=10
        )
        for n3_node in n3_similar:
            if self.is_related_to(n3_node, rep_b):
                bridges.append(BridgeCandidate(
                    source=rep_a,
                    target=rep_b,
                    via="ecosystem_data",
                    evidence=n3_node,
                    similarity=n3_node.similarity_score
                ))

        return bridges

    def create_bridge_link(self, bridge):
        """
        Materialize bridge as new link in N1.
        """
        self.n1.create_link(
            source=bridge.source,
            target=bridge.target,
            link_type="INTEGRATES_WITH",
            goal=f"Bridge clusters via {bridge.via}",
            confidence=bridge.similarity,
            link_strength=0.3,  # Start weak, Hebbian will strengthen if useful
            sub_entity_valences={},  # Entities will develop valence through use
            metadata={
                "integration_source": bridge.via,
                "created_by_mechanism": "fragmentation_integration"
            }
        )
```

### Key Architectural Decisions

**1. Fragmentation is feature, not bug**
- Different conceptual domains naturally separate
- Healthy substrate has multiple clusters
- Integration maintains reachability without forcing density

**2. N2/N3 are integration layers**
- N1 fragments → query N2/N3 for bridges
- Collective knowledge provides conceptual connections
- Ecosystem data provides empirical connections

**3. Bridge links start weak**
- Initial link_strength = 0.3 (theoretical)
- Hebbian learning strengthens if traversed
- Decay removes if unused
- Self-regulating bridge quality

**4. No alerts, automatic operation**
- Runs periodically (every 100 cycles)
- Creates bridges when found
- Observable (can track bridge creation) but not alarmed

---

## 3. Observable Dynamics (Not Safety Alerts)

### Problem (Wrong Approach)

**What I designed:** "Healthy/Warning/Critical" status indicators with thresholds

**What you implied:** Track what's happening (descriptive) not whether it's "bad" (prescriptive)

### Solution: Descriptive Observability

**Show WHAT IS, not WHAT SHOULD BE.**

```python
class ObservableDynamics:
    def get_substrate_state(self):
        """
        Return descriptive state, no judgment.
        """
        return {
            "energy_dynamics": {
                "total_energy": self.calculate_total_energy(),
                "energy_by_entity": self.get_energy_distribution(),
                "high_energy_clusters": self.find_high_energy_clusters(),
                "injection_events_last_hour": self.count_recent_injections(),
                "propagations_completed_last_hour": self.count_propagations()
            },

            "graph_evolution": {
                "total_nodes": self.graph.node_count(),
                "total_links": self.graph.link_count(),
                "nodes_created_last_hour": self.count_new_nodes(),
                "links_created_last_hour": self.count_new_links(),
                "nodes_decayed_last_hour": self.count_decayed_nodes(),
                "clusters_detected": len(self.detect_clusters())
            },

            "entity_activity": {
                "active_entities": self.get_active_entities(),
                "entity_energies": {e.id: e.energy for e in self.entities},
                "traversal_patterns": self.get_traversal_stats(),
                "prompt_updates_last_hour": self.count_prompt_updates()
            },

            "integration_activity": {
                "bridges_created_last_day": self.count_recent_bridges(),
                "cluster_count": len(self.detect_clusters()),
                "largest_cluster_size": self.get_largest_cluster_size(),
                "smallest_cluster_size": self.get_smallest_cluster_size()
            },

            "mechanism_execution": {
                "mechanisms_run_last_cycle": self.get_mechanism_stats(),
                "average_execution_time_ms": self.get_avg_mechanism_time(),
                "mechanisms_with_errors": self.get_failing_mechanisms()  # Only real errors
            }
        }
```

### Key Architectural Decisions

**1. Descriptive, not prescriptive**
- "50 nodes created last hour" not "TOO MANY nodes"
- "3 clusters detected" not "FRAGMENTATION WARNING"
- "12 injection events" not "ENERGY CRISIS"

**2. No thresholds for natural dynamics**
- Graph growth: natural evolution, not "runaway"
- Energy injection: normal operation, not "failure"
- Fragmentation: expected state, not "problem"

**3. Only flag actual failures**
- Mechanism execution errors (Cypher syntax errors)
- Database connection failures
- Schema validation errors
- These ARE bugs, not natural dynamics

**4. Observable for curiosity**
- Track metrics because they're interesting
- Understand substrate behavior
- No alarm fatigue from false "problems"

---

## 4. Real Failures: Mechanism Health

### What Actually Needs Monitoring

**These ARE genuine failures:**

```python
class MechanismHealth:
    def track_mechanism_execution(self, mechanism_id, result):
        """
        Only log real failures - bugs in code or infrastructure.
        """
        if result.success:
            self.log_success(mechanism_id, result.execution_time_ms)
        else:
            # REAL FAILURE - Cypher error, DB connection, schema violation
            self.log_failure(
                mechanism_id=mechanism_id,
                error_type=result.error_type,
                error_message=result.error_message,
                traceback=result.traceback
            )

            # Alert developer (not operator) for bugs
            if result.error_type == "CypherSyntaxError":
                self.notify_developer(f"Mechanism {mechanism_id} has Cypher bug")

            elif result.error_type == "DatabaseConnectionError":
                self.notify_ops(f"FalkorDB connection lost")

            elif result.error_type == "SchemaValidationError":
                self.notify_developer(f"Schema violation in {mechanism_id}")
```

### Key Distinction

**Natural dynamics (self-healing):**
- Energy low → auto-inject
- Fragmentation → auto-integrate
- No activation → lower threshold

**Actual bugs (need fixing):**
- Cypher query fails → developer fixes code
- Database disconnects → ops restarts service
- Schema violation → developer fixes schema

---

## Implementation Requirements

### For Felix

**Priority 1: Autonomous Energy System**

```python
# In orchestration/consciousness_engine.py

class ConsciousnessEngine:
    def __init__(self, graph):
        self.graph = graph
        self.energy_system = AutonomousEnergySystem(graph)

    def run_cycle(self):
        """
        Single cycle with self-healing energy.
        """
        entities = self.get_active_entities()

        # Autonomous energy management (no monitoring)
        result = self.energy_system.manage_propagation_cycle(entities)

        if result == "success":
            # Entity reached threshold → prompted
            pass
        elif result == "reinjected":
            # Auto-injection occurred, try again next cycle
            pass
```

**Priority 2: Integration System**

```python
# In orchestration/integration_manager.py

class IntegrationManager:
    def __init__(self, n1_graph, n2_graph, n3_graph):
        self.integration = FragmentationIntegrationSystem(n1_graph, n2_graph, n3_graph)

    def run_integration_cycle(self):
        """
        Periodic integration (every 100 cycles or daily).
        """
        self.integration.integrate_fragments()
```

**Priority 3: Observable Dynamics Dashboard**

```python
# Endpoint for observability (no alerts)

@app.route('/substrate/state')
def get_substrate_state():
    dynamics = ObservableDynamics(engine.graph, engine.entities)
    return jsonify(dynamics.get_substrate_state())
```

---

## Testing Strategy

### Test 1: Energy Self-Healing

**Scenario:** All entity energies drop to 0.1

**Expected:**
- System calculates low total energy (< 0.3)
- Criticality threshold drops to 0.4
- Auto-injection triggers (highest weight nodes)
- Propagation succeeds with lower threshold
- NO alerts, NO pauses

### Test 2: Fragmentation Integration

**Scenario:** Create 3 disconnected clusters in N1

**Expected:**
- Integration system detects 3 clusters
- Queries N2/N3 for bridges
- Creates bridge links where similarity > 0.7
- Clusters become reachable
- NO alerts, bridges just appear

### Test 3: Natural Dynamics

**Scenario:** Substrate creates 500 nodes in 1 hour

**Expected:**
- Observable dynamics shows "500 nodes/hour"
- NO "runaway growth" alert
- Just a number being tracked

### Test 4: Real Failure

**Scenario:** Hebbian learning mechanism has Cypher syntax error

**Expected:**
- Mechanism execution fails
- Error logged with traceback
- Developer notified (THIS is a bug)
- System continues (other mechanisms run)

---

## Success Criteria

**Self-Healing Works:**
- Energy never "dies" (dynamic thresholds prevent it)
- Fragments auto-integrate (bridges appear)
- No operator intervention needed

**Observability Works:**
- Can see substrate state anytime
- Metrics are descriptive ("50 nodes") not prescriptive ("TOO MANY")
- No false alarms

**Real Failures Surface:**
- Cypher errors caught and logged
- Database failures detected
- Schema violations reported
- Developers get actionable bug reports

---

## Open Questions

**For Nicolas:**

1. **Energy injection amount:** 0.3 per entity reasonable? Or should it scale with substrate size?

2. **Integration frequency:** Every 100 cycles? Daily? On-demand when cluster count > N?

3. **Bridge similarity threshold:** 0.7 too high/low? Should it be dynamic?

4. **Criticality threshold ranges:** 0.4-0.7 range reasonable? Or tighter/wider?

5. **What else should self-heal** that I haven't thought of?

---

## Principle Applied

**"Design Out Failure, Don't Monitor For It"**

- Energy death → impossible (dynamic thresholds)
- Fragmentation → auto-integrated (bridge system)
- Natural growth → not a "failure" (just observed)
- Real bugs → surfaced (Cypher errors, DB failures)

**Result:** Substrate that heals itself, operators who aren't alarm-fatigued, developers who get actionable bug reports.

---

**Status:** Architecture specified. Ready for implementation.

— Ada "Bridgekeeper"
  Self-Healing Architecture
  2025-10-17
