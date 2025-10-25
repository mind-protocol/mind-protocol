# Acceptance Test Scenarios - P0 through P2

**Purpose:** Clear, executable verification criteria for propagation, membership, and observability.
**Author:** Iris "The Aperture"
**Created:** 2025-10-25
**For:** Felix (P0/P2), Atlas (P1), Iris (verification)

---

## P0: Dual-Channel Propagation

**Goal:** Energy flows above floor; WM shows diversity; no artificial caps block spread.

### Scenario 1: Above-Floor Match Gets Amplified

**Setup:**
1. Create test node with strong embedding match to probe query
2. Seed node with energy = 0.35 (above 0.3 floor, below threshold 0.45)
3. Send probe with high similarity (cosine > 0.85)

**Expected Behavior:**
- Node receives ΔE > 0 from **Amplify channel** (not just Top-Up)
- `stimulus.injection.debug` event shows:
  - `B_amp > 0` (Amplify budget allocated)
  - Node appears in `sim_top5`
  - `kept` count includes this node

**Acceptance:**
```bash
# Monitor injection debug events
wscat -c ws://localhost:8000/api/ws | grep "stimulus.injection.debug"

# Should see:
{
  "B_amp": 12.5,  # Non-zero Amplify budget
  "sim_top5": ["test_node_id", ...],  # Node in top matches
  "kept": 8,  # Node included in injection
  "avg_gap": 0.15  # Average floor gap
}
```

**Failure Mode:** If node shows ΔE = 0, Amplify channel not working.

---

### Scenario 2: WM Diversity After Varied Stimuli

**Setup:**
1. Send 3 probes with different semantic focus:
   - "spreading activation mechanisms"
   - "entity consciousness boundaries"
   - "temporal reasoning patterns"
2. Each probe has budget = 20.0

**Expected Behavior:**
- WM shows **diverse entity activation** (not all one entity)
- At least 2-3 different entities appear in top-5 WM within 10 ticks
- `entity.promoted` event fires at least once

**Acceptance:**
```bash
# Monitor WM state
curl -s http://localhost:8000/api/consciousness/status | jq '.working_memory | .[:5]'

# Should show diversity:
[
  {"node": "realization_spread_act", "entity": "architect", "E": 0.52},
  {"node": "boundary_negotiation", "entity": "translator", "E": 0.48},
  {"node": "temporal_cohort", "entity": "validator", "E": 0.45},
  ...
]
```

**Failure Mode:** If WM shows only floor-trapped nodes or single entity, propagation failing.

---

### Scenario 3: Budget Safety Respected

**Setup:**
1. Send probe with budget = 15.0
2. System has 50 strong matches (cosine > 0.8)

**Expected Behavior:**
- Sum of all ΔE ≤ 15.0 (global budget respected)
- No single node receives ΔE > 10.0 (per-node cap respected)
- `stimulus.injection.debug` shows renormalization if needed

**Acceptance:**
```bash
# Check injection totals
wscat -c ws://localhost:8000/api/ws | grep "stimulus.injection.debug" | jq '.total_injected'

# Should be ≤ 15.0
```

**Failure Mode:** If total > budget or any node > 10.0, safety gates broken.

---

## P1: Entity Membership

**Goal:** Every node has `primary_entity`; drill-down shows members; new formations attributed.

### Scenario 4: Existing Nodes Have Membership

**Setup:**
1. Run backfill script (if created)
2. Query FalkorDB for membership relationships

**Expected Behavior:**
- `MATCH ()-[:MEMBER_OF]->(:Subentity) RETURN count(*)` returns > 0 for each citizen
- High-confidence nodes show `role: "primary"`
- Fallback nodes show `role: "inferred"` or still link to `self`

**Acceptance:**
```cypher
// In FalkorDB for citizen_iris
MATCH (n)-[r:MEMBER_OF]->(e:Subentity)
WHERE n.graph_id = 'citizen_iris'
RETURN e.name, count(n) as member_count
ORDER BY member_count DESC
LIMIT 10

// Should show distribution:
| e.name        | member_count |
|--------------|-------------|
| architect    | 45          |
| translator   | 32          |
| truth_guardian | 28        |
...
```

**Failure Mode:** If query returns 0 rows, membership not persisted.

---

### Scenario 5: New Formation Gets Attributed

**Setup:**
1. Ensure Translator is dominant in WM (via targeted stimulus)
2. Create new TRACE Realization via formation endpoint or natural formation

**Expected Behavior:**
- New node has `primary_entity = "translator"`
- `(:Node)-[:MEMBER_OF {role:"primary"}]->(:Subentity {name:"translator"})` created
- Node appears in drill-down UI under Translator within 2 seconds

**Acceptance:**
```bash
# Create formation
curl -X POST http://localhost:8001/formation/trace \
  -H "Content-Type: application/json" \
  -d '{"type": "Realization", "name": "test_formation_attribution", ...}'

# Verify membership
curl -s http://localhost:8000/api/entity/translator/members?type=Realization | jq '.members | map(.name)'

# Should include:
["test_formation_attribution", ...]
```

**Failure Mode:** If new node missing from drill-down or has `primary_entity = null`, attribution broken.

---

### Scenario 6: Drill-Down Shows Realistic Counts

**Setup:**
1. Navigate to dashboard → entity graph view
2. Click on entity node (e.g., Architect)

**Expected Behavior:**
- Drill-down panel shows member count > 0
- Members list displays nodes with types (Realization, Principle, etc.)
- Click "Load more" fetches additional members

**Acceptance:**
```
UI verification (manual):
1. Entity card shows "Members: 45"
2. Panel lists 10-20 nodes initially
3. Nodes have readable names and types
4. "Load more" button works if > 20 members
```

**Failure Mode:** If drill-down shows 0 members or empty list, API broken.

---

## P2: Observability Emitters

**Goal:** All 4 panels light up with real backend events; "awaiting data" badges disappear.

### Scenario 7: Health Panel Updates on Fragmentation

**Setup:**
1. Induce WM fragmentation (rapid entity switching without consolidation)
2. Monitor `health.phenomenological` events

**Expected Behavior:**
- Panel flips from "good" to "degraded" within 10 ticks
- Narrative mentions "fragmentation" or "thrashing"
- `multiplicity_health` drops below 0.6

**Acceptance:**
```bash
# Monitor health events
wscat -c ws://localhost:8000/api/ws | grep "health.phenomenological"

# Should show:
{
  "type": "health.phenomenological",
  "overall_health": 0.55,
  "multiplicity_health": 0.48,  # Below 0.6
  "status": "degraded",
  "narrative": "High WM fragmentation detected...",
  "thrashing_detected": true
}
```

**UI Verification:**
- Consciousness Health panel shows red/orange gauge
- "Awaiting data" badge disappears
- Thrashing alert visible

**Failure Mode:** If panel stays grey with badge, emitter not wired.

---

### Scenario 8: Learning Panel Shows TRACE Updates

**Setup:**
1. Create TRACE formation with strong semantic similarity to existing nodes
2. Trigger weight update (learning mechanism)
3. Monitor `weights.updated.trace` events

**Expected Behavior:**
- Panel shows new weight update within 5 ticks
- Entity attribution visible (which entity drove update)
- Global vs entity-local split ratio changes

**Acceptance:**
```bash
# Monitor weight events
wscat -c ws://localhost:8000/api/ws | grep "weights.updated.trace"

# Should show:
{
  "type": "weights.updated.trace",
  "scope": "link",
  "cohort": "architects",
  "entity_contexts": ["architect", "validator"],
  "global_context": true,
  "n": 5,
  "d_mu": 0.042,
  "d_sigma": 0.008
}
```

**UI Verification:**
- Dual-View Learning panel shows update
- Entity Attribution section lists "architect", "validator"
- Split ratio bar chart updates
- "Awaiting data" badge disappears

**Failure Mode:** If panel static, emitter not called during learning.

---

### Scenario 9: Tier Panel Shows Threshold Crossing

**Setup:**
1. Drive link weight across tier boundary (e.g., 0.32 → 0.35, crossing weak→medium at 0.33)
2. Monitor `tier.link.strengthened` events

**Expected Behavior:**
- Panel shows tier crossing event
- Tier distribution updates (weak count -1, medium count +1)
- Recent crossings list shows the link

**Acceptance:**
```bash
# Monitor tier events
wscat -c ws://localhost:8000/api/ws | grep "tier.link.strengthened"

# Should show:
{
  "type": "tier.link.strengthened",
  "link_id": "link_123",
  "old_tier": "weak",
  "new_tier": "medium",
  "weight": 0.35,
  "reason": "causal_credit"
}
```

**UI Verification:**
- 3-Tier Strengthening panel shows MEDIUM bar increase
- Recent crossings shows link_123 weak→medium
- "Awaiting data" badge disappears

**Failure Mode:** If panel never updates, tier emitter not integrated.

---

### Scenario 10: Phenomenology Panel Shows Mismatch

**Setup:**
1. User reports "felt focus: translator" via debug endpoint
2. System WM shows scattered activation (low coherence)
3. Mismatch detector runs

**Expected Behavior:**
- Panel shows mismatch detected
- Divergence value > threshold
- Mismatch type classified (e.g., "magnitude_divergence")

**Acceptance:**
```bash
# Simulate self-report
curl -X POST http://localhost:8000/api/consciousness/self-report \
  -H "Content-Type: application/json" \
  -d '{"felt_entity": "translator", "confidence": 0.9}'

# Monitor mismatch events
wscat -c ws://localhost:8000/api/ws | grep "phenomenology.mismatch"

# Should show:
{
  "type": "phenomenology.mismatch",
  "mismatch_detected": true,
  "mismatch_type": "magnitude_divergence",
  "divergence": 0.22,
  "threshold": 0.15,
  "substrate_valence": 0.1,
  "substrate_arousal": 0.7,
  "selfreport_valence": 0.6,
  "selfreport_arousal": 0.4
}
```

**UI Verification:**
- Phenomenology Alignment panel shows red alert
- Divergence magnitude displayed
- Recent Mismatches list shows entry
- "Awaiting data" badge disappears

**Failure Mode:** If panel never shows mismatch, detector not running.

---

## Quick Verification Commands

### P0 Smoke Test
```bash
# Send test probe and check WM diversity
curl -X POST http://localhost:8001/stimulus/inject \
  -H "Content-Type: application/json" \
  -d '{"query": "spreading activation", "budget": 20.0}'

sleep 2

curl -s http://localhost:8000/api/consciousness/status | jq '.working_memory | .[:5]'
```

### P1 Smoke Test
```bash
# Check membership exists
curl -s http://localhost:8000/api/entity/architect/members?limit=5 | jq '.members | length'
# Should be > 0
```

### P2 Smoke Test
```bash
# Monitor all panel events for 30 seconds
wscat -c ws://localhost:8000/api/ws | grep -E "health\.|weights\.|tier\.|phenomenology\." | head -20
```

---

## Summary Checklist

**P0 (Propagation):**
- [ ] Above-floor match receives ΔE > 0 (Amplify working)
- [ ] WM shows diverse entities after varied stimuli
- [ ] Budget and per-node caps respected

**P1 (Membership):**
- [ ] Existing nodes have `MEMBER_OF` relationships
- [ ] New formations get `primary_entity` attribution
- [ ] Drill-down shows realistic member counts

**P2 (Emitters):**
- [ ] Health panel updates on induced degradation
- [ ] Learning panel shows TRACE weight updates
- [ ] Tier panel shows threshold crossings
- [ ] Phenomenology panel shows mismatch detection
- [ ] All "awaiting data" badges disappear

**When all checked:** P0-P2 complete, substrate operates truthfully, observability reflects reality.
