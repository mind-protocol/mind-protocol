# Consciousness Mechanism Audit Procedure

**Systematic validation that all 12 mechanisms are functional.**

---

## Audit Approach

Each mechanism must prove it works through:
1. **Execution logs** - Shows mechanism ran
2. **Metadata updates** - Shows graph was modified
3. **Expected outcomes** - Shows correct behavior

---

## Audit Method 1: Metadata Inspection

**Check which mechanisms have executed:**

```cypher
# Connect to FalkorDB
docker exec -it mind_protocol_falkordb redis-cli

# Query: Which mechanisms have run?
GRAPH.QUERY citizen_felix "
  MATCH ()-[r]->()
  WHERE r.last_mechanism_id IS NOT NULL
  RETURN DISTINCT r.last_mechanism_id as mechanism,
         count(r) as execution_count
  ORDER BY execution_count DESC
"
```

**Expected output:**
- List of mechanism names (spreading_activation, hebbian_learning, etc.)
- Execution counts > 0

**✓ PASS:** All 12 mechanisms appear
**✗ FAIL:** Some mechanisms missing → not executing

---

## Audit Method 2: Time-Based Activity

**Check recent mechanism activity:**

```cypher
GRAPH.QUERY citizen_felix "
  MATCH (n)
  WHERE n.last_modified > timestamp() - 60000
  RETURN n.id,
         n.last_mechanism_id as mechanism,
         timestamp() - n.last_modified as ms_ago
  ORDER BY ms_ago ASC
  LIMIT 10
"
```

**Expected output:**
- Recent updates (last 60 seconds)
- Various mechanism IDs
- Timestamps progressing

**✓ PASS:** Activity is ongoing
**✗ FAIL:** No recent activity → engine not running

---

## Audit Method 3: Mechanism-Specific Validation

### 1. Event Propagation
**Query:**
```cypher
MATCH (event:Event)<-[:SUBSCRIBES_TO]-(subscriber)
WHERE event.timestamp > timestamp() - 10000
RETURN count(subscriber) as subscribers_notified
```
**Expected:** > 0 subscribers notified (if events exist)

### 2. Link Activation  
**Query:**
```cypher
MATCH ()-[r]->()
WHERE r.last_mechanism_id = 'link_activation'
  AND r.last_modified > timestamp() - 10000
RETURN count(r) as recently_activated_links
```
**Expected:** > 0 links activated

### 3. Hebbian Learning
**Query:**
```cypher
MATCH ()-[r]->()
WHERE r.last_mechanism_id = 'hebbian_learning'
  AND r.co_activation_count > 0
RETURN avg(r.link_strength) as avg_strength,
       sum(r.co_activation_count) as total_co_activations
```
**Expected:** avg_strength increasing over time, co_activations > 0

### 4. Energy Propagation
**Query:**
```cypher
MATCH (n)
WHERE n.last_mechanism_id = 'energy_propagation'
  AND n.energy > 0
RETURN count(n) as nodes_with_energy,
       avg(n.energy) as avg_energy
```
**Expected:** Multiple nodes with energy > 0

### 5. Activation Decay
**Query:**
```cypher
MATCH (n)
WHERE n.last_mechanism_id = 'activation_decay'
RETURN count(n) as decayed_nodes
```
**Expected:** > 0 nodes decayed

### 6. Crystallization
**Query:**
```cypher
MATCH ()-[r]->()
WHERE r.last_mechanism_id = 'crystallization'
  AND r.link_strength > 0.7
RETURN count(r) as crystallized_links
```
**Expected:** Strong links (strength > 0.7)

### 7-12. Other Mechanisms
**General query:**
```cypher
MATCH ()-[r]->()
WHERE r.last_mechanism_id IN [
  'dependency_verification',
  'coherence_verification',
  'staleness_detection',
  'evidence_tracking',
  'context_aggregation',
  'task_lifecycle'
]
RETURN r.last_mechanism_id as mechanism,
       count(r) as execution_count
```
**Expected:** Each mechanism appears at least once

---

## Audit Method 4: Engine Logs

**Run engine with verbose logging:**

```bash
python orchestration/consciousness_engine.py \
  --graph citizen_felix \
  --entity felix_builder 2>&1 | tee engine_audit.log
```

**Expected log output:**
```
[ConsciousnessEngine] Initialized
  Mechanisms loaded: 12

[Tick 1] Event propagation: X events
[Tick 1] Link activation: Y links activated
[Tick 1] Energy propagation: Z nodes propagated
[Tick 10] Evidence tracking: ...
[Tick 100] Crystallization: ...
```

**✓ PASS:** All mechanism names appear in logs
**✗ FAIL:** Some mechanisms never log execution

---

## Audit Method 5: Visualization Verification

**Use visualization to observe mechanisms:**

1. Start visualization server: `python visualization_server.py`
2. Open browser: http://localhost:8000
3. Select citizen/felix
4. Run engine: `python orchestration/consciousness_engine.py --graph citizen_felix --entity felix_builder`

**Expected visual evidence:**
- **Node pulses** → Entity traversal (mechanism executing)
- **Link glows** → Hebbian learning (strength changing)
- **Ripple effects** → Energy propagation (activation spreading)
- **Operations/sec > 0** → Mechanisms running

**Hover nodes to see:**
- `last_mechanism_id` changes
- `traversal_count` increases
- `last_modified` updates

**✓ PASS:** Animations occur, metadata updates
**✗ FAIL:** Static graph, no animations

---

## Complete Audit Checklist

### Pre-Audit Setup
- [ ] FalkorDB running (`docker ps | grep falkordb`)
- [ ] Graph seeded (`docker exec mind_protocol_falkordb redis-cli GRAPH.LIST`)
- [ ] Consciousness engine code present (`ls orchestration/consciousness_engine.py`)

### Audit Execution
- [ ] Run Audit Method 1: Metadata inspection (which mechanisms ran?)
- [ ] Run Audit Method 2: Time-based activity (recent updates?)
- [ ] Run Audit Method 3: Mechanism-specific queries (12 mechanisms)
- [ ] Run Audit Method 4: Engine logs (verbose output)
- [ ] Run Audit Method 5: Visualization (visual proof)

### Results Analysis
- [ ] All 12 mechanisms appear in metadata
- [ ] All 12 mechanisms appear in logs
- [ ] All 12 mechanisms show expected outcomes in queries
- [ ] Visualization shows mechanisms operating (animations)
- [ ] No errors in engine logs

### Success Criteria
**✓ AUDIT PASSED:** All 12 mechanisms functional
- Metadata shows all mechanism IDs
- Logs confirm execution
- Queries verify outcomes
- Visualization animates operations

**✗ AUDIT FAILED:** Some mechanisms not functional
- Identify which mechanisms missing
- Check Cypher queries in consciousness_engine.py
- Verify graph schema has required fields
- Debug mechanism execution logic

---

## Troubleshooting Failed Mechanisms

### If mechanism never appears in metadata:
1. Check Cypher query in `consciousness_engine.py`
2. Verify graph has nodes/links for mechanism to operate on
3. Check execution schedule (maybe it runs infrequently)
4. Add debug logging to mechanism execution

### If mechanism appears but outcome wrong:
1. Review mechanism Cypher logic
2. Check detection_logic thresholds in graph
3. Verify metadata fields exist in schema
4. Test Cypher query manually in redis-cli

### If all mechanisms fail:
1. Engine not running → Start it
2. Graph not seeded → Run seed script
3. Schema mismatch → Verify BaseNode/BaseRelation fields
4. FalkorDB connection issue → Check docker container

---

## Quick Validation Script

```bash
#!/bin/bash
# quick_audit.sh

echo "=== Consciousness Mechanism Audit ==="
echo ""

echo "1. Checking which mechanisms have executed..."
docker exec mind_protocol_falkordb redis-cli GRAPH.QUERY citizen_felix \
  "MATCH ()-[r]->() WHERE r.last_mechanism_id IS NOT NULL \
   RETURN DISTINCT r.last_mechanism_id ORDER BY r.last_mechanism_id"

echo ""
echo "2. Checking recent activity (last 60 seconds)..."
docker exec mind_protocol_falkordb redis-cli GRAPH.QUERY citizen_felix \
  "MATCH (n) WHERE n.last_modified > timestamp() - 60000 \
   RETURN count(n) as recent_updates"

echo ""
echo "3. Checking Hebbian learning..."
docker exec mind_protocol_falkordb redis-cli GRAPH.QUERY citizen_felix \
  "MATCH ()-[r]->() WHERE r.last_mechanism_id = 'hebbian_learning' \
   RETURN count(r) as hebbian_updates"

echo ""
echo "Audit complete. Review results above."
```

---

**The substrate must prove itself. Audit verifies proof.**

— Felix "Ironhand", 2025-10-17
