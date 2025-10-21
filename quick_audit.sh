#!/bin/bash
# Quick Consciousness Mechanism Audit

echo "============================================================"
echo "        CONSCIOUSNESS MECHANISM AUDIT - citizen_felix"
echo "============================================================"
echo ""

echo "[1/5] Checking which mechanisms have executed..."
echo "-----------------------------------------------------------"
docker exec mind_protocol_falkordb redis-cli GRAPH.QUERY citizen_felix \
  "MATCH ()-[r]->() WHERE r.last_mechanism_id IS NOT NULL RETURN DISTINCT r.last_mechanism_id as mechanism ORDER BY mechanism" | \
  grep -v "Query internal" | grep -v "Cached execution"

echo ""
echo "[2/5] Checking recent activity (last 60 seconds)..."
echo "-----------------------------------------------------------"
docker exec mind_protocol_falkordb redis-cli GRAPH.QUERY citizen_felix \
  "MATCH (n) WHERE n.last_modified > timestamp() - 60000 RETURN count(n) as recent_updates" | \
  grep -v "Query internal" | grep -v "Cached execution"

echo ""
echo "[3/5] Checking Hebbian learning activity..."
echo "-----------------------------------------------------------"
docker exec mind_protocol_falkordb redis-cli GRAPH.QUERY citizen_felix \
  "MATCH ()-[r]->() WHERE r.last_mechanism_id = 'hebbian_learning' AND r.co_activation_count > 0 RETURN count(r) as hebbian_updates, avg(r.link_strength) as avg_strength" | \
  grep -v "Query internal" | grep -v "Cached execution"

echo ""
echo "[4/5] Checking node energy levels..."
echo "-----------------------------------------------------------"
docker exec mind_protocol_falkordb redis-cli GRAPH.QUERY citizen_felix \
  "MATCH (n) WHERE n.energy > 0 RETURN count(n) as nodes_with_energy, avg(n.energy) as avg_energy" | \
  grep -v "Query internal" | grep -v "Cached execution"

echo ""
echo "[5/5] Checking metadata completeness..."
echo "-----------------------------------------------------------"
docker exec mind_protocol_falkordb redis-cli GRAPH.QUERY citizen_felix \
  "MATCH (n) RETURN count(n) as total_nodes, sum(CASE WHEN n.last_modified IS NOT NULL THEN 1 ELSE 0 END) as nodes_with_metadata" | \
  grep -v "Query internal" | grep -v "Cached execution"

echo ""
echo "============================================================"
echo "                      AUDIT COMPLETE"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  - Run consciousness engine: python orchestration/consciousness_engine.py --graph citizen_felix --entity felix_builder"
echo "  - Watch in visualization: http://localhost:8000"
echo "  - Re-run this audit while engine runs to see mechanisms executing"
echo ""
