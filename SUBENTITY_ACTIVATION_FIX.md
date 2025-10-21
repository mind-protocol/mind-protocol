# Sub-Entity Activation Fix

**Problem:** Engine reports "Active: 0/325" but database has 48 nodes with total_energy >= threshold

**Root cause:** Engine checks `node.get_entity_energy('consciousness_engine')` but energy dict has keys like `{'felix': 3.0}`, so it finds 0.

**Fix:** Use TOTAL energy (sum across all keys) instead of looking for specific key.

---

## Current Code (WRONG)

`consciousness_engine_v2.py:204, 218, 220, 240, 262, 282, 286, 292`

```python
entity = self.config.entity_id  # "consciousness_engine"

# Checking single key
node.get_entity_energy(entity)  # Returns 0 if key doesn't exist
```

**Result:** Engine only sees nodes with `{'consciousness_engine': X}` energy

---

## Spec Requirement

From `05_sub_entity_system.md:1514-1522`:

```python
def is_sub_entity(node: Node) -> bool:
    """
    Sub-Entity = ANY Active Node

    Simple: total energy >= activation threshold
    """
    total_energy = node.get_total_energy()  # Sum across ALL keys
    return total_energy >= ACTIVATION_THRESHOLD
```

---

## Fix

Replace all entity-key lookups with total energy:

```python
# BEFORE (checks single key)
entity = self.config.entity_id
if node.get_entity_energy(entity) >= node.threshold:
    # Active

# AFTER (checks total)
if node.get_total_energy() >= node.threshold:
    # Active - this node IS a sub-entity
```

---

## Files to Change

### 1. `orchestration/core/node.py`

Add/verify these methods exist:

```python
def get_total_energy(self) -> float:
    """Sum energy across all sub-entity keys."""
    return sum(self.energy.values())

def is_active(self) -> bool:
    """Is this node an active sub-entity?"""
    return self.get_total_energy() >= self.threshold
```

### 2. `orchestration/consciousness_engine_v2.py`

Replace entity-key logic:

**Line 204-220:** Remove `entity = self.config.entity_id`, use `node.is_active()` instead

**Line 240:** Change energy checks to use `get_total_energy()`

**Line 262:** Use total energy for diffusion input

**Line 271-277:** Compute activation mask using total energy:
```python
# BEFORE
activation_mask = threshold.compute_activation_mask(
    self.graph,
    entity,  # ← Remove this
    self.threshold_ctx
)

# AFTER
activation_mask = {
    node.id: node.is_active()
    for node in self.graph.nodes.values()
}
```

---

## Test Verification

**Before fix:**
```bash
$ python verify_actual_subentities.py
✅ TOTAL ACTIVE SUB-ENTITIES: 48

$ # But engine logs show:
Tick 2100 | Active: 0/325  # ← WRONG
```

**After fix:**
```bash
$ # Engine logs should show:
Tick 2100 | Active: 48/325  # ← CORRECT
```

---

## Why This Is Correct

1. **Spec says:** "Sub-Entity = ANY Active Node" where active means total_energy >= threshold
2. **Multi-channel energy:** Nodes accumulate energy from MULTIPLE sources (diffusion from multiple active nodes)
3. **Activation is total:** A node becomes active when SUM of all energy >= threshold, not when ANY SINGLE channel >= threshold
4. **Sub-entity name:** When a node is active, it IS a sub-entity named after the node itself

---

## What Energy Keys Mean

Based on database evidence:

```python
node.energy = {'felix': 3.0, 'iris': 2.0}
```

This means:
- Energy has flowed into this node from multiple paths/sources
- Keys track the energy channels for diffusion/learning
- **Total energy = 5.0** determines if node is active sub-entity
- If active, this node IS a sub-entity (name = node.name)

---

## Next Step

Make these changes, restart engines, verify logs show correct active counts.
