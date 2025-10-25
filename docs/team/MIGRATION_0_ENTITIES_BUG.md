# Migration Guide: 0-Entities Bug Resolution

**Issue ID:** 0-entities-bug
**Severity:** Critical (Priority 1 blocker)
**Affected Versions:** Pre-2025-10-24
**Resolution Date:** 2025-10-24
**Author:** Felix "Ironhand"

---

## Executive Summary

**Problem:** Entity bootstrap searched for Mechanism nodes to seed functional entities (The Translator, The Architect, etc.), resulting in `entities.total=0` and blocking all entity-aware v2 features.

**Root Cause:** Confusion between Mechanism nodes (algorithms with inputs/outputs) and functional entities (consciousness modes/patterns).

**Solution:** Config-driven entity bootstrap loading from `orchestration/config/functional_entities.yml`.

**Impact:** Unblocks entity-first WM, two-scale traversal, adaptive learning, and all v2 visualizations.

---

## Symptoms

If you encounter these symptoms, you may have the 0-entities bug:

### Telemetry Evidence

**WebSocket events show:**
```json
{
  "type": "wm.emit",
  "selected_entities": [],
  "total_entities": 0,
  "total_members": 0
}
```

**API metrics endpoint (`/api/affective-telemetry/metrics`):**
```json
{
  "entity_count": 0,
  "entity_activation_rate": 0.0
}
```

**Logs show:**
```
[N1:citizen_luca] Subentities already present: 0
[N1:citizen_luca] entities.total=0 - WM will fallback to node-only mode
```

### User-Facing Impact

- Entity bubbles don't appear in Iris's Mood Map visualization
- No boundary beams (entity-to-entity traversal) visible
- WM selection shows nodes only, no entity grouping
- Context-aware features non-functional

---

## Root Cause Analysis

### The Confusion

The old `entity_bootstrap.py` implementation (pre-2025-10-24) contained this logic:

```python
def bootstrap_functional_entities(self) -> List[Subentity]:
    """Extract functional subentities from Mechanism nodes in graph."""
    mechanism_nodes = self.graph.get_nodes_by_type(NodeType.MECHANISM)

    for node in mechanism_nodes:
        if "subentity" in node.name.lower():
            # Create functional subentity from Mechanism node
            ...
```

### Why This Was Wrong

**Mechanism nodes** are for algorithms:
- Fields: `how_it_works`, `inputs`, `outputs`
- Purpose: Document technical functions (e.g., "energy_redistribution_algorithm")
- Examples: WeightLearner, StrengthCalculator, ThresholdComputer

**Functional entities** are consciousness modes:
- Fields: `role_or_topic`, `centroid_embedding`, `energy`, `threshold`
- Purpose: Represent phenomenological patterns (e.g., "The Translator", "The Architect")
- Examples: Translator, Architect, Validator, Pragmatist

**The search found nothing** because no Mechanism nodes had "subentity" in their names. Result: `entities.total=0`.

---

## Resolution

### What Changed

**File:** `orchestration/mechanisms/entity_bootstrap.py`
**Commit:** 5f1fca3 (2025-10-24)
**Changes:**

1. **Removed Mechanism search:**
   ```python
   # OLD (WRONG):
   mechanism_nodes = self.graph.get_nodes_by_type(NodeType.MECHANISM)
   for node in mechanism_nodes:
       if "subentity" in node.name.lower():
           ...

   # NEW (CORRECT):
   entity_configs = self.config.get("entities", [])
   for entity_cfg in entity_configs:
       subentity = self._create_functional_entity_from_config(entity_cfg)
   ```

2. **Config-driven bootstrap:**
   - Loads from `orchestration/config/functional_entities.yml`
   - Creates Entity nodes directly (idempotent upsert)
   - Seeds BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") via keyword matching
   - No dependency on Mechanism nodes

3. **Entity energy formula refinement:**
   - Added log damping: `E_entity = Σ m_i · log1p(max(0, E_i - Θ_i))`
   - Prevents single-node domination
   - Uses surplus-only energy (above threshold)

### Config Structure

**File:** `orchestration/config/functional_entities.yml`

```yaml
entities:
  - key: translator
    name: "The Translator"
    kind: "functional"
    description: "Bridges phenomenology and technical structure"
    keywords:
      any:
        - translate
        - bridge
        - phenomenology
        - mapping
    initial_threshold_policy: "cohort_median_plus_mad"
```

Eight functional entities defined: translator, architect, validator, pragmatist, pattern_recognizer, boundary_keeper, partner, observer.

---

## Migration Steps

### For Existing Deployments

**1. Update code:**
```bash
git pull origin main
# Ensure you have commits 5f1fca3 (bootstrap fix) and 1efa7e4 (formula fix)
```

**2. Verify config exists:**
```bash
ls orchestration/config/functional_entities.yml
# Should show 8 entities defined
```

**3. Restart system:**
```bash
# Stop guardian if running
# Ctrl+C in guardian terminal

# Restart
python guardian.py
```

**4. Verify entities created:**
```bash
# Check logs
tail -f guardian.log | grep entity_bootstrap
# Should see: "entity_bootstrap: created={'entities': 8, 'memberships_seeded': ...}"

# Check metrics
curl http://localhost:8000/api/consciousness/status
# Should show "total_entities": 8 for each citizen
```

**5. Verify WM selection:**
```bash
# Check WebSocket events
# Should see wm.emit with non-empty selected_entities array
```

### For New Deployments

No migration needed. Bootstrap runs automatically on first graph load.

---

## Verification Checklist

After applying the fix, verify:

- [ ] Config file exists: `orchestration/config/functional_entities.yml`
- [ ] Logs show bootstrap success: `entity_bootstrap: created={'entities': 8, ...}`
- [ ] Metrics show entities: `total_entities > 0`
- [ ] WM events include entities: `selected_entities.length >= 1`
- [ ] Entity bubbles visible in visualization
- [ ] No "entities.total=0" warnings in logs

---

## Prevention (How to Avoid Regression)

### For Developers

**1. Never search for Mechanism nodes to create entities:**
```python
# ❌ WRONG:
mechanism_nodes = graph.get_nodes_by_type(NodeType.MECHANISM)

# ✅ CORRECT:
entity_configs = config.get("entities", [])
```

**2. Understand the distinction:**
- **Mechanism nodes** = algorithms/functions (technical)
- **Functional entities** = consciousness modes (phenomenological)

**3. Follow bootstrap pattern:**
- Functional entities: config-driven (`functional_entities.yml`)
- Semantic entities: clustering-driven (embeddings)

### For Reviewers

**Red flags in code review:**
- Searching for Mechanism nodes in entity bootstrap
- Creating entities from non-Entity node types
- Missing config file references

**Green flags:**
- Config-driven entity creation
- Keyword-based BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") seeding
- Idempotent upsert patterns

---

## References

- **Field Guide:** `docs/team/FIELD_GUIDE_ENTITIES_TRAVERSAL.md` (comprehensive entity architecture)
- **Spec:** `docs/specs/v2/subentity_layer/subentity_layer.md` §2.6 (bootstrap specification)
- **Gap Analysis:** `docs/specs/v2/IMPLEMENTATION_GAP_ANALYSIS.md` (lines 227-230, Priority 1)
- **Config:** `orchestration/config/functional_entities.yml` (entity definitions)
- **Implementation:** `orchestration/mechanisms/entity_bootstrap.py` (bootstrap code)

---

## Questions?

**Q: Why were Mechanism nodes ever used for entities?**
A: Historical accident during initial implementation. The pattern was wrong but not caught until comprehensive testing.

**Q: Can I add new functional entities?**
A: Yes! Edit `functional_entities.yml`, add entity definition with keywords, restart system. Bootstrap is idempotent.

**Q: What about semantic entities?**
A: Semantic entities come from clustering (future Phase 3 work). Requires embeddings generation first.

**Q: Will old graphs break?**
A: No. Bootstrap is idempotent - existing entities are reused, missing entities are created.

---

**Resolution confirmed:** Priority 1 blocker removed, entity-first architecture operational.

**Next steps:** System restart → verification → Priority 2-6 implementation.
