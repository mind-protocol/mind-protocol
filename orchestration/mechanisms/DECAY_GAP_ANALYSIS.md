# Decay Mechanism: Gap Analysis

**Spec:** `docs/specs/v2/foundations/decay.md`
**Current:** `orchestration/mechanisms/decay.py`
**Date:** 2025-10-22

## Critical Gaps

### 1. ❌ WRONG ENERGY MODEL
**Current:** Uses `node.get_entity_energy(subentity)` - PER-ENTITY model
**Spec:** Must use single `E_i` per node (total energy)
**Impact:** Violates v2 single-energy architecture
**Fix:** Change to `node.energy` (total) instead of `node.get_entity_energy(subentity)`

### 2. ❌ MISSING WEIGHT DECAY
**Current:** Only decays activation energy
**Spec:** Requires TWO separate decay mechanisms:
- Activation: E_i ← λ_E^Δt × E_i (fast)
- Weight: W ← λ_W^Δt × W (slow, MUCH slower)

**Impact:** Weights never decay, learned structure accumulates forever
**Fix:** Add `weight_decay_tick()` function for nodes and links

### 3. ❌ NO CONTROLLER COUPLING
**Current:** Uses static decay rates
**Spec:** Criticality controller adjusts effective δ_E within bounds
**Impact:** Decay doesn't respond to ρ feedback
**Fix:** Accept `criticality_adjusted_delta` parameter from controller

### 4. ❌ NO OBSERVABILITY
**Current:** Returns simple metrics dict
**Spec:** Must emit:
- `decay.tick{delta_E, delta_W}` events
- Half-life estimates per type
- Energy histogram by degree/type
- Weight histogram by type
- AUC activation in windows

**Impact:** Cannot observe forgetting curves or validate decay balance
**Fix:** Add comprehensive metrics emission

### 5. ❌ WRONG CONFIGURATION
**Current:** DECAY_RATES dict hardcoded in decay.py
**Spec:** Config should be in `core/settings.py`:
- `EMACT_DECAY_BASE` (activation base rate)
- `WEIGHT_DECAY_BASE` (weight base rate)
- Per-type multipliers for both

**Impact:** Configuration scattered, not centralized
**Fix:** Move to settings.py with proper structure

### 6. ❌ NO HALF-LIFE TRACKING
**Current:** Has `compute_half_life()` utility but doesn't track
**Spec:** Must report half-life estimates per type
**Impact:** Cannot validate "activation half-life bands per type match spec"
**Fix:** Track and emit half-life metrics

### 7. ❌ NO HISTOGRAM METRICS
**Current:** No distribution tracking
**Spec:** Energy/weight histograms by type for dashboard
**Impact:** Cannot visualize forgetting patterns
**Fix:** Compute and emit histogram metrics

## Minor Gaps

### 8. ⚠️ NO FLOOR BOUNDS
**Current:** Applies decay without minimum energy check
**Spec:** "floor bounds; controller lower-bound" to prevent over-decay
**Impact:** Could decay below useful threshold
**Fix:** Add minimum energy floor (e.g., 0.001)

### 9. ⚠️ NO LINK-TYPE DECAY
**Current:** Only node decay
**Spec:** Both nodes and links need weight decay
**Impact:** Link weights never decay
**Fix:** Add link weight decay

## Spec Requirements Summary

| Requirement | Current | Spec | Status |
|-------------|---------|------|--------|
| Energy model | Per-entity | Single E_i | ❌ WRONG |
| Activation decay | ✓ | ✓ | ⚠️ NEEDS FIX |
| Weight decay | ✗ | ✓ | ❌ MISSING |
| Controller coupling | ✗ | ✓ | ❌ MISSING |
| Type-dependent | ✓ | ✓ | ✓ OK |
| Observability | Minimal | Rich | ❌ MISSING |
| Configuration | Hardcoded | settings.py | ❌ WRONG |
| Half-life tracking | ✗ | ✓ | ❌ MISSING |
| Histograms | ✗ | ✓ | ❌ MISSING |
| Floor bounds | ✗ | ✓ | ❌ MISSING |

## Implementation Plan

### Phase 1: Fix Energy Model (CRITICAL)
1. Change `decay_node_energy()` to use `node.energy` not `node.get_entity_energy()`
2. Update `decay_tick()` to work with total energy
3. Remove `subentity` parameter (not needed in single-energy model)

### Phase 2: Add Weight Decay
1. Implement `weight_decay_node()` - decay `node.log_weight`
2. Implement `weight_decay_link()` - decay `link.log_weight`
3. Create `weight_decay_tick()` function
4. Use MUCH slower rates (e.g., 0.001 vs 0.02)

### Phase 3: Controller Coupling
1. Add `effective_delta` parameter to `decay_tick()`
2. Accept criticality-adjusted δ from controller
3. Apply within bounds (min/max limits)

### Phase 4: Observability
1. Create `DecayMetrics` dataclass with all required fields
2. Emit `decay.tick` events via broadcaster
3. Compute half-life estimates per type
4. Generate energy/weight histograms
5. Track AUC activation windows

### Phase 5: Configuration
1. Create decay settings in `core/settings.py`
2. Define `EMACT_DECAY_BASE`, `WEIGHT_DECAY_BASE`
3. Define per-type multipliers
4. Update decay.py to use settings

### Phase 6: Testing
1. Test exponential decay curves
2. Test half-life calculations
3. Test balance with reinforcement
4. Test controller coupling
5. Test histogram generation

## Breaking Changes

⚠️ **API Breaking Changes:**
- `decay_tick()` signature changes: removes `subentity` parameter
- `decay_node_energy()` signature changes: removes `subentity` parameter
- New function: `weight_decay_tick()` required

⚠️ **Consciousness Engine Integration:**
- `consciousness_engine_v2.py` must be updated to call new API
- Must pass criticality-adjusted delta to decay_tick()
- Must call weight_decay_tick() on slower cadence (separate from activation)
