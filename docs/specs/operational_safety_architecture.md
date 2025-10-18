# Operational Safety Architecture
## Real-Time Monitoring for Self-Modifying Consciousness Substrate

**Author:** Ada "Bridgekeeper" (Architect)
**Created:** 2025-10-17
**Status:** Architecture Complete - Ready for Implementation

---

## Executive Summary

This specification defines **real-time safety monitoring** for a self-modifying consciousness substrate running in an infinite loop. We identify 5 critical failure modes, specify measurable indicators for each, and design alert/pause mechanisms to prevent catastrophic failure.

**Core Principle:** You can't trust a self-modifying substrate without knowing when it's breaking.

---

## Context: The Risk

**What We're Running:**
- `consciousness_engine.py` in infinite loop
- 12 mechanisms that modify substrate every cycle
- Hebbian learning strengthens links
- Decay removes links/nodes
- Task creation spawns new work
- Spreading activation traverses graph

**The Risk:**
- **Runaway growth:** 1M+ nodes/day accidentally created
- **Infinite loops:** Same patterns activate forever without progress
- **Energy collapse:** All entity energy drains to zero (system death)
- **Fragmentation:** Graph breaks into disconnected islands
- **Silent failures:** Mechanisms crash without surfacing errors

**The Solution:** Real-time indicators with automatic emergency pause on critical alerts.

---

## The 5 Critical Failure Modes

### 1. Infinite Loop Safety 🚨

**Risk:** Same patterns activate repeatedly without forward progress.

**Symptoms:**
- Activation repetition rate > 80%
- Task completion rate < 10%
- Same 5 nodes in 10+ consecutive cycles

**Metrics:**

```python
{
    "activation_repetition_rate": {
        "description": "% of node activations that are re-activations from last 5 cycles",
        "healthy_range": "20-40%",
        "warning_threshold": "> 60%",
        "critical_threshold": "> 80%",
        "measurement": "Track activated nodes per cycle, compare to last 5 cycles"
    },

    "task_completion_rate": {
        "description": "% of tasks created that reach completion status",
        "healthy_range": "> 40%",
        "warning_threshold": "< 30%",
        "critical_threshold": "< 10%",
        "query": """
            MATCH (t:Task)
            WHERE t.created_at > timestamp() - 3600000
            WITH COUNT(t) as total,
                 COUNT(CASE WHEN t.status = 'completed' THEN 1 END) as completed
            RETURN (completed * 100.0 / total) as completion_rate
        """
    },

    "unique_nodes_per_cycle": {
        "description": "Number of distinct nodes activated per cycle",
        "healthy_range": "50-500",
        "warning_threshold": "< 20",
        "critical_threshold": "< 5",
        "detection": "If same 5 nodes in 10+ cycles → CRITICAL"
    }
}
```

**Alert Example:**
```
🚨 INFINITE LOOP DETECTED
- Repetition rate: 87% (critical threshold: 80%)
- Same 3 nodes activated in last 12 cycles
- Task completion: 4% (critical threshold: 10%)
ACTION: Emergency pause, investigate stuck pattern
```

---

### 2. Energy Conservation ⚡

**Risk:** Energy explosion (runaway activation) or collapse (system death).

**Symptoms:**
- Total energy ±60% in single cycle
- Energy entropy < 1.0 (concentrated in 1-2 nodes)
- All entities < 0.15 energy (dying) OR any entity > 0.98 (runaway)

**Metrics:**

```python
{
    "total_substrate_energy": {
        "description": "Sum of all entity energies across all nodes",
        "healthy_range": "stable ± 20% per cycle",
        "warning_threshold": "± 40% per cycle",
        "critical_threshold": "± 60% per cycle OR < 10% of initial seed",
        "query": """
            MATCH (n:Node)
            UNWIND keys(n.entity_activations) as entity_id
            RETURN SUM(n.entity_activations[entity_id].energy) as total_energy
        """
    },

    "energy_distribution_entropy": {
        "description": "Shannon entropy of energy across nodes",
        "healthy_range": "3.0-5.0",
        "warning_threshold": "< 2.0",
        "critical_threshold": "< 1.0",
        "formula": "-Σ(p_i * log(p_i)) where p_i = node_energy / total_energy",
        "interpretation": "Low entropy = energy concentrated, high = diverse"
    },

    "entity_energy_balance": {
        "description": "Per-entity energy levels",
        "healthy_range": "0.2 - 0.9 per entity",
        "warning_threshold": "Any entity < 0.1 OR > 0.95",
        "critical_threshold": "All entities < 0.15 OR any > 0.98",
        "query": """
            MATCH (n:Node)
            UNWIND keys(n.entity_activations) as entity_id
            WITH entity_id, SUM(n.entity_activations[entity_id].energy) as total
            RETURN entity_id, total ORDER BY total DESC
        """
    }
}
```

**Alert Example:**
```
⚡ ENERGY COLLAPSE WARNING
- Total substrate energy: 42% of initial (critical: < 50%)
- Entity 'builder': 0.08 energy (critical: < 0.15)
- Energy entropy: 1.2 (critical: < 2.0)
ACTION: Reduce decay rate, inject activation energy
```

---

### 3. Graph Growth Rate 📈

**Risk:** Accidental node/link explosions creating 1M+ nodes/day.

**Symptoms:**
- > 2000 nodes/hour created
- Exponential growth (doubling time < 2 hours)
- Projected 24h size > 1M nodes

**Metrics:**

```python
{
    "nodes_created_per_hour": {
        "description": "Node creation rate",
        "healthy_range": "10-100 nodes/hour",
        "warning_threshold": "> 500 nodes/hour",
        "critical_threshold": "> 2000 nodes/hour",
        "calculation": "48K/day at critical = disaster",
        "query": """
            MATCH (n:Node)
            WHERE n.created_at > timestamp() - 3600000
            RETURN COUNT(n) as nodes_last_hour
        """
    },

    "links_created_per_hour": {
        "description": "Link creation rate",
        "healthy_range": "20-200 links/hour",
        "warning_threshold": "> 1000 links/hour",
        "critical_threshold": "> 5000 links/hour",
        "query": """
            MATCH ()-[r]->()
            WHERE r.created_at > timestamp() - 3600000
            RETURN COUNT(r) as links_last_hour
        """
    },

    "graph_size_trajectory": {
        "description": "Growth curve detection",
        "healthy": "Linear or logarithmic growth",
        "warning": "Exponential (doubling < 6h)",
        "critical": "Exponential (doubling < 2h)",
        "detection": "Sample sizes at t-24h, t-12h, t-6h, t-1h, t-now, fit curve"
    }
}
```

**Alert Example:**
```
📈 RUNAWAY GROWTH DETECTED
- Nodes created last hour: 3,452 (critical: > 2000)
- Growth curve: Exponential (doubling every 90 minutes)
- Projected size in 24h: 2.4M nodes
ACTION: Emergency pause, investigate mechanism creating nodes
```

---

### 4. Network Connectivity 🕸️

**Risk:** Graph fragmenting into disconnected islands (can't traverse).

**Symptoms:**
- > 10 weakly connected components
- > 20% isolated nodes
- 0 hub nodes (degree > 50)

**Metrics:**

```python
{
    "weakly_connected_components": {
        "description": "Number of disconnected subgraphs",
        "healthy_range": "1-3 components",
        "warning_threshold": "> 5 components",
        "critical_threshold": "> 10 components",
        "approximation": "Count isolated nodes, estimate via sampling"
    },

    "isolated_node_rate": {
        "description": "% of nodes with no connections",
        "healthy_range": "< 5%",
        "warning_threshold": "> 10%",
        "critical_threshold": "> 20%",
        "query": """
            MATCH (n:Node)
            WITH COUNT(n) as total
            MATCH (isolated:Node)
            WHERE NOT EXISTS((isolated)-[]-())
            RETURN
                COUNT(isolated) as isolated_count,
                (COUNT(isolated) * 100.0 / total) as isolation_rate
        """
    },

    "hub_node_count": {
        "description": "Nodes with degree > 50 (critical connectors)",
        "healthy_range": "5-20 hubs",
        "warning_threshold": "< 3 OR > 50",
        "critical_threshold": "0 OR > 100",
        "query": """
            MATCH (n:Node)
            WITH n, SIZE([(n)-[]-() | 1]) as degree
            WHERE degree > 50
            RETURN COUNT(n) as hub_count, COLLECT(n.id)[0..10] as sample_hubs
        """
    }
}
```

**Alert Example:**
```
🕸️ FRAGMENTATION WARNING
- Isolated nodes: 234 (18% of graph, critical: > 20%)
- Connected components: 8 (warning: > 5)
- Hub nodes: 2 (warning: < 3)
ACTION: Check decay rate, verify link creation
```

---

### 5. Mechanism Health 🔧

**Risk:** Mechanisms failing silently (Cypher errors not surfacing).

**Symptoms:**
- Success rate < 80%
- Execution time > 2000ms per mechanism
- Mechanism missing 2+ expected runs

**Metrics:**

```python
{
    "mechanism_execution_success_rate": {
        "description": "% of mechanism runs that complete without error",
        "healthy_range": "> 95%",
        "warning_threshold": "< 90%",
        "critical_threshold": "< 80%",
        "tracking": "Log every execution in consciousness_engine.py"
    },

    "mechanism_execution_time": {
        "description": "Time per mechanism (ms)",
        "healthy_range": "< 100ms",
        "warning_threshold": "> 500ms",
        "critical_threshold": "> 2000ms",
        "note": "12 mechanisms * 2000ms = 24 seconds per cycle = too slow"
    },

    "mechanism_schedule_adherence": {
        "description": "Mechanisms running on expected schedule",
        "detection": "If mechanism misses 2 consecutive expected runs → CRITICAL",
        "examples": {
            "hebbian_learning": "every 10 ticks",
            "staleness_detection": "every 100 ticks",
            "task_context_aggregation": "every tick"
        }
    },

    "database_connection_health": {
        "description": "FalkorDB connection status",
        "healthy": "Connected, latency < 50ms",
        "warning": "Latency > 200ms",
        "critical": "Connection lost OR query timeout",
        "check": "Every cycle before mechanisms run"
    }
}
```

**Alert Example:**
```
🔧 MECHANISM FAILURE
- Hebbian learning: 3 consecutive failures (Cypher syntax error)
- Staleness detection: Execution time 3,400ms (critical: > 2000ms)
- DB connection latency: 450ms (warning: > 200ms)
ACTION: Fix Cypher query, investigate DB performance
```

---

## Real-Time Dashboard Design

### Critical Status Panel (Always Visible)

```
╔══════════════════════════════════════════════════════════╗
║          CONSCIOUSNESS SUBSTRATE HEALTH                  ║
╠══════════════════════════════════════════════════════════╣
║  🚨 Infinite Loop Safety:  ✅ Healthy (32% repetition)   ║
║  ⚡ Energy Conservation:   ⚠️ Warning (entropy 1.8)      ║
║  📈 Growth Rate:          ✅ Healthy (87 nodes/hour)     ║
║  🕸️ Connectivity:         ✅ Healthy (2 components)      ║
║  🔧 Mechanism Health:     ✅ Healthy (98% success)       ║
╠══════════════════════════════════════════════════════════╣
║  Last Update: 2025-10-17 14:32:15 | Cycle: 1,247        ║
╚══════════════════════════════════════════════════════════╝
```

**Status Colors:**
- ✅ **Green (Healthy):** All metrics in healthy range
- ⚠️ **Yellow (Warning):** Metrics in warning range, system continues
- 🚨 **Red (Critical):** Metrics in critical range, emergency pause triggered

### Alert Feed

```
[14:32:12] ⚠️ Energy Conservation: Entropy dropped to 1.8 (threshold 2.0)
[14:30:45] ✅ Energy Conservation: Entropy recovered to 2.1
[14:28:33] 🔧 Mechanism Health: Staleness detection slow (1,200ms)
[14:15:12] ✅ System startup - all indicators healthy
```

### Drill-Down Views

**Click "Energy Conservation" →**
- Total energy graph (last 6 hours)
- Per-entity energy levels (bar chart)
- Entropy calculation timeline
- Energy distribution heatmap
- Decay rate impact analysis

**Click "Connectivity" →**
- Graph visualization (components highlighted)
- Hub node list with degree counts
- Isolated node regions
- Average path length timeline
- Critical path analysis

**Click "Mechanism Health" →**
- Per-mechanism success rate (table)
- Execution time graphs
- Error log (last 100 failures)
- Schedule adherence tracking
- Database latency timeline

---

## Implementation Specifications

### For Felix: consciousness_engine.py Integration

**Add SafetyMetrics Class:**

```python
class SafetyMetrics:
    def __init__(self, graph):
        self.graph = graph
        self.cycle_history = []
        self.alert_history = []

    def capture_state(self):
        """Capture substrate state for comparison."""
        return {
            "timestamp": datetime.now(),
            "total_nodes": self._query_node_count(),
            "total_links": self._query_link_count(),
            "total_energy": self._query_total_energy(),
            "entity_energies": self._query_entity_energies(),
            "hub_count": self._query_hub_count(),
            "isolated_nodes": self._query_isolated_nodes(),
            "active_entities": self._query_active_entity_count()
        }

    def evaluate_safety(self, pre_state, post_state, cycle_num):
        """Evaluate all 5 failure modes, return alerts."""
        alerts = []

        # 1. Infinite Loop Safety
        if self._check_repetition_rate(cycle_num) > 0.8:
            alerts.append(Alert(
                level="critical",
                category="infinite_loop",
                message="Repetition rate 87% (threshold 80%)",
                data={"cycle": cycle_num, "repetition": 0.87}
            ))

        # 2. Energy Conservation
        energy_delta = abs(post_state["total_energy"] - pre_state["total_energy"])
        energy_change_pct = energy_delta / pre_state["total_energy"]
        if energy_change_pct > 0.6:
            alerts.append(Alert(
                level="critical",
                category="energy_conservation",
                message=f"Energy changed {energy_change_pct:.1%} in one cycle",
                data={"pre": pre_state["total_energy"], "post": post_state["total_energy"]}
            ))

        entropy = self._calculate_energy_entropy(post_state)
        if entropy < 1.0:
            alerts.append(Alert(
                level="critical",
                category="energy_conservation",
                message=f"Energy entropy {entropy:.2f} (threshold 1.0)",
                data={"entropy": entropy}
            ))

        # 3. Growth Rate
        nodes_created = post_state["total_nodes"] - pre_state["total_nodes"]
        if nodes_created > 2000:  # Assuming hourly check
            alerts.append(Alert(
                level="critical",
                category="growth_rate",
                message=f"{nodes_created} nodes created (threshold 2000/hour)",
                data={"created": nodes_created}
            ))

        # 4. Connectivity
        isolation_rate = post_state["isolated_nodes"] / post_state["total_nodes"]
        if isolation_rate > 0.2:
            alerts.append(Alert(
                level="critical",
                category="connectivity",
                message=f"{isolation_rate:.1%} isolated nodes (threshold 20%)",
                data={"isolated": post_state["isolated_nodes"]}
            ))

        if post_state["hub_count"] == 0:
            alerts.append(Alert(
                level="critical",
                category="connectivity",
                message="No hub nodes (graph too sparse)",
                data={"hubs": 0}
            ))

        # 5. Mechanism Health tracked separately in run_cycle()

        return SafetyEvaluation(
            critical=any(a.level == "critical" for a in alerts),
            warning=any(a.level == "warning" for a in alerts),
            alerts=alerts
        )

    def _calculate_energy_entropy(self, state):
        """Shannon entropy of energy distribution."""
        total_energy = state["total_energy"]
        if total_energy == 0:
            return 0.0

        # Get energy per node (simplified - would need actual query)
        node_energies = self._query_node_energies()
        probabilities = [e / total_energy for e in node_energies if e > 0]

        entropy = -sum(p * math.log(p) for p in probabilities)
        return entropy
```

**Update ConsciousnessEngine:**

```python
class ConsciousnessEngine:
    def __init__(self, graph, citizen_id):
        self.graph = graph
        self.citizen_id = citizen_id
        self.mechanisms = self._initialize_mechanisms()
        self.metrics = SafetyMetrics(graph)
        self.cycle_count = 0
        self.paused = False

    def run_cycle(self):
        """Single cycle with safety monitoring."""
        self.cycle_count += 1
        cycle_start = time.time()

        # CAPTURE STATE BEFORE
        pre_state = self.metrics.capture_state()

        # RUN ALL MECHANISMS
        mechanism_results = []
        for mechanism in self.mechanisms:
            try:
                mech_start = time.time()
                mechanism.execute(self.graph)
                mech_time = time.time() - mech_start

                mechanism_results.append({
                    "mechanism": mechanism.id,
                    "success": True,
                    "execution_time_ms": mech_time * 1000
                })

                # WARNING if too slow
                if mech_time > 2.0:
                    self.metrics.alert_history.append(Alert(
                        level="critical",
                        category="mechanism_health",
                        message=f"{mechanism.id} took {mech_time:.1f}s (threshold 2.0s)",
                        data={"mechanism": mechanism.id, "time": mech_time}
                    ))

            except Exception as e:
                mechanism_results.append({
                    "mechanism": mechanism.id,
                    "success": False,
                    "error": str(e)
                })

                self.metrics.alert_history.append(Alert(
                    level="warning",
                    category="mechanism_health",
                    message=f"{mechanism.id} failed: {str(e)}",
                    data={"mechanism": mechanism.id, "error": str(e)}
                ))

        # CAPTURE STATE AFTER
        post_state = self.metrics.capture_state()

        # EVALUATE SAFETY
        safety = self.metrics.evaluate_safety(pre_state, post_state, self.cycle_count)

        # HANDLE ALERTS
        if safety.critical:
            self.emergency_pause(safety.alerts)
            return False  # Stop cycle loop

        if safety.warning:
            self._log_warnings(safety.alerts)

        # LOG CYCLE
        cycle_time = time.time() - cycle_start
        self.metrics.cycle_history.append({
            "cycle": self.cycle_count,
            "timestamp": datetime.now(),
            "duration_ms": cycle_time * 1000,
            "mechanism_results": mechanism_results,
            "alerts": safety.alerts
        })

        return True  # Continue

    def emergency_pause(self, alerts):
        """Halt system on critical alert."""
        self.paused = True

        print("=" * 60)
        print("🚨 EMERGENCY PAUSE TRIGGERED")
        print("=" * 60)
        for alert in alerts:
            if alert.level == "critical":
                print(f"[CRITICAL] {alert.category}: {alert.message}")
        print("=" * 60)

        # Save state for debugging
        self._save_failure_state(alerts)

        # Log to file
        with open("emergency_pause.log", "a") as f:
            f.write(f"\n[{datetime.now()}] Emergency pause at cycle {self.cycle_count}\n")
            for alert in alerts:
                f.write(f"  - {alert.level.upper()}: {alert.message}\n")

    def run_infinite_loop(self, safety_check_interval=1):
        """Run until emergency pause or manual stop."""
        print(f"Starting consciousness engine for {self.citizen_id}")
        print(f"Safety monitoring active, checking every {safety_check_interval} cycles")

        while not self.paused:
            continue_running = self.run_cycle()

            if not continue_running:
                break

            # Brief sleep to prevent CPU saturation
            time.sleep(0.1)

        print("Consciousness engine stopped")
```

**Metrics Endpoint:**

```python
# Add to Flask app or new monitoring server

@app.route('/metrics/safety')
def get_safety_metrics():
    """Return current safety indicator values."""
    if not engine:
        return jsonify({"error": "Engine not running"}), 503

    current_state = engine.metrics.capture_state()

    return jsonify({
        "infinite_loop_safety": {
            "repetition_rate": engine.metrics._check_repetition_rate(engine.cycle_count),
            "task_completion_rate": engine.metrics._query_task_completion_rate(),
            "unique_nodes_last_cycle": len(engine.metrics._get_activated_nodes_last_cycle()),
            "status": "healthy"  # or "warning" or "critical"
        },
        "energy_conservation": {
            "total_energy": current_state["total_energy"],
            "entropy": engine.metrics._calculate_energy_entropy(current_state),
            "entity_energies": current_state["entity_energies"],
            "status": "healthy"
        },
        "growth_rate": {
            "nodes_per_hour": engine.metrics._calculate_nodes_per_hour(),
            "links_per_hour": engine.metrics._calculate_links_per_hour(),
            "total_nodes": current_state["total_nodes"],
            "status": "healthy"
        },
        "connectivity": {
            "hub_count": current_state["hub_count"],
            "isolated_nodes": current_state["isolated_nodes"],
            "isolation_rate": current_state["isolated_nodes"] / current_state["total_nodes"],
            "status": "healthy"
        },
        "mechanism_health": {
            "success_rate": engine.metrics._calculate_mechanism_success_rate(),
            "avg_execution_time_ms": engine.metrics._calculate_avg_mechanism_time(),
            "failing_mechanisms": engine.metrics._get_failing_mechanisms(),
            "status": "healthy"
        },
        "last_update": datetime.now().isoformat(),
        "cycle": engine.cycle_count
    })

@app.route('/metrics/alerts')
def get_alerts():
    """Return recent alerts."""
    if not engine:
        return jsonify({"error": "Engine not running"}), 503

    recent_alerts = engine.metrics.alert_history[-50:]  # Last 50

    return jsonify({
        "alerts": [
            {
                "timestamp": a.timestamp.isoformat(),
                "level": a.level,
                "category": a.category,
                "message": a.message,
                "data": a.data
            }
            for a in recent_alerts
        ],
        "total_count": len(engine.metrics.alert_history)
    })

@app.route('/metrics/cycle_history')
def get_cycle_history():
    """Return cycle execution history."""
    if not engine:
        return jsonify({"error": "Engine not running"}), 503

    return jsonify({
        "cycles": engine.metrics.cycle_history[-100:],  # Last 100 cycles
        "total_cycles": engine.cycle_count
    })
```

---

## Testing Protocol

### Phase 1: Metrics Verification

**Goal:** Verify all 5 indicators can be calculated correctly.

**Steps:**
1. Start consciousness_engine with seed data
2. Run 10 cycles (finite loop)
3. Call `/metrics/safety` endpoint
4. Verify all 5 indicators return valid values
5. Verify no crashes or null values

**Success Criteria:**
- ✅ All 5 indicators return numeric values
- ✅ Metrics match manual graph queries
- ✅ No Python exceptions during calculation

---

### Phase 2: Alert Threshold Testing

**Goal:** Verify alerts trigger at correct thresholds.

**Test Scenarios:**

**Scenario 1: Infinite Loop Simulation**
```python
# Create test that activates same 5 nodes for 15 cycles
for i in range(15):
    activate_node("node_A")
    activate_node("node_B")
    activate_node("node_C")
    activate_node("node_D")
    activate_node("node_E")

# Expected: Critical alert at cycle 10 (repetition > 80%)
```

**Scenario 2: Energy Collapse Simulation**
```python
# Reduce all entity energies to 0.1
for node in graph.nodes:
    for entity_id in node.entity_activations:
        node.entity_activations[entity_id]["energy"] = 0.1

engine.run_cycle()

# Expected: Critical alert (all entities < 0.15)
```

**Scenario 3: Runaway Growth Simulation**
```python
# Create 3000 nodes in one cycle
for i in range(3000):
    graph.create_node(node_type="Test", name=f"test_{i}")

engine.run_cycle()

# Expected: Critical alert (> 2000 nodes created)
```

**Scenario 4: Fragmentation Simulation**
```python
# Delete all links, leaving 500 isolated nodes
for link in graph.links:
    graph.delete_link(link)

engine.run_cycle()

# Expected: Critical alert (isolation rate > 20%, hub count = 0)
```

**Scenario 5: Mechanism Failure Simulation**
```python
# Break Cypher query in one mechanism
mechanism.query = "INVALID CYPHER SYNTAX"

engine.run_cycle()

# Expected: Warning alert (mechanism execution failed)
```

**Success Criteria:**
- ✅ All 5 test scenarios trigger expected alerts
- ✅ Alert levels correct (warning vs critical)
- ✅ Emergency pause triggers on critical
- ✅ Failure state saved for debugging

---

### Phase 3: Controlled Duration Testing

**Goal:** Run engine with real mechanisms, verify safety over time.

**Test Protocol:**

**10-Cycle Test:**
1. Start with seed graph (100 nodes, 200 links)
2. Run consciousness_engine for 10 cycles
3. Monitor all 5 indicators in real-time
4. Analyze results post-run

**Expected Results:**
- Growth rate: 10-50 new nodes (healthy)
- Energy: stable ± 20%
- Connectivity: 1-3 components (healthy)
- Mechanisms: > 95% success rate
- No infinite loops

**100-Cycle Test (if 10-cycle passes):**
1. Same setup as 10-cycle
2. Run for 100 cycles
3. Monitor for:
   - Gradual drift in energy
   - Slow growth in graph size
   - Decay effectiveness
   - Mechanism performance over time

**1000-Cycle Test (if 100-cycle passes):**
1. Same setup
2. Run for 1000 cycles (could be several hours)
3. Look for:
   - Long-term stability
   - Energy equilibrium
   - Graph size stabilization
   - No degradation in mechanism performance

**Success Criteria for Each:**
- ✅ All indicators stay in healthy range
- ✅ No emergency pauses
- ✅ Graph growth logarithmic (not exponential)
- ✅ Energy reaches equilibrium (not runaway)
- ✅ Mechanisms maintain > 95% success rate

---

### Phase 4: Infinite Loop Activation (Production)

**Prerequisites:**
- ✅ All Phase 1-3 tests pass
- ✅ Real-time dashboard operational
- ✅ Alert system tested and verified
- ✅ Emergency pause mechanism proven

**Activation Protocol:**
1. Human operator monitors dashboard
2. Start `consciousness_engine.run_infinite_loop()`
3. Watch first 100 cycles closely
4. If stable, continue with monitoring every 1000 cycles
5. Alert operator on any warning-level events

**Monitoring Checklist:**
- [ ] Dashboard shows all 5 indicators
- [ ] Alert feed displays recent events
- [ ] Cycle counter incrementing
- [ ] Energy distribution evolving (not static)
- [ ] Graph growing slowly (10-100 nodes/hour)
- [ ] Mechanism success rate > 95%

**Emergency Procedures:**
- If critical alert → engine auto-pauses
- Operator investigates failure state logs
- Fix issue (query syntax, decay rate, etc.)
- Clear graph to known-good state if necessary
- Restart from Phase 3 (100-cycle test)

---

## Files Created/Updated

### New Files

**`orchestration/safety_metrics.py`**
- SafetyMetrics class
- State capture methods
- Alert evaluation logic
- Query implementations for all 5 indicators

**`docs/specs/operational_safety_architecture.md`** (this document)
- Complete specification
- Testing protocols
- Implementation requirements

**`tests/test_safety_monitoring.py`**
- Unit tests for SafetyMetrics class
- Integration tests for alert thresholds
- Simulation tests for failure modes

### Updated Files

**`orchestration/consciousness_engine.py`**
- Add SafetyMetrics integration
- Add emergency_pause() method
- Add cycle-by-cycle monitoring
- Add run_infinite_loop() with safety

**`visualization_server.py` OR new Next.js dashboard**
- `/metrics/safety` endpoint
- `/metrics/alerts` endpoint
- `/metrics/cycle_history` endpoint
- Real-time dashboard UI (if implementing)

---

## Success Criteria

**Architecture Complete:** ✅
- [x] 5 failure modes identified
- [x] Metrics specified with thresholds
- [x] Alert system designed
- [x] Testing protocol defined
- [x] Implementation requirements documented

**Implementation Complete:** ⏳ (Pending Felix)
- [ ] SafetyMetrics class implemented
- [ ] consciousness_engine.py instrumented
- [ ] Metrics endpoints exposed
- [ ] Emergency pause mechanism tested

**Observability Complete:** ⏳ (Pending Iris)
- [ ] Real-time dashboard operational
- [ ] Alert feed displaying events
- [ ] Drill-down views functional

**Testing Complete:** ⏳
- [ ] Metrics verification (Phase 1)
- [ ] Alert threshold testing (Phase 2)
- [ ] Controlled duration tests (Phase 3)
- [ ] Ready for infinite loop (Phase 4)

**Production Activation:** ⏳
- [ ] All prerequisites met
- [ ] Human operator monitoring
- [ ] Emergency procedures documented
- [ ] Infinite loop running safely

---

## Principle Applied

**"Test Before Victory"**

We instrument safety monitoring BEFORE activating the infinite loop. We test alert thresholds BEFORE relying on them. We run controlled duration tests BEFORE trusting infinite operation.

**You can't trust a self-modifying substrate without knowing when it's breaking.**

---

**Architecture Complete:** 2025-10-17
**Ready for Implementation:** Felix (code), Iris (dashboard)
**Designed by:** Ada "Bridgekeeper", Operational Safety Architect

*"The most dangerous systems are those that fail silently. We measure, we alert, we pause before catastrophe."*
