# SubEntity-Context TRACE Implementation Design (Priority 4)

**Date:** 2025-10-25 03:30 UTC
**Architect:** Nicolas (with Luca documentation)
**Status:** Design Complete, Ready for Implementation
**Scope:** Priority 4 - Context-Aware TRACE with 80/20 SubEntity localization

---

## Terminology Note

This specification uses terminology from **TAXONOMY_RECONCILIATION.md**:
- **Node** - Atomic knowledge activated in working memory
- **SubEntity** - Weighted neighborhoods tracking co-activation patterns (Scale A)
- **Mode** - IFS-level meta-roles with distinct activation dynamics (Scale B)

See §2.1.1 of `subentity_layer.md` for Scale A (SubEntity) vs Scale B (Mode) architecture.

---

## Executive Summary

**Problem:** TRACE reinforcement currently updates global weights only. Need SubEntity-contextualized learning where "Translator marked this useful" primarily strengthens Translator-local access while still nudging global weight.

**Solution:** Dual-view weights (global + sparse SubEntity overlays) with membership-weighted localization. No per-SubEntity node energies - maintains single-energy substrate.

**Key Principle:** SubEntities are neighborhoods, not separate energy systems. Learning creates **view-time overlays** on weights, not separate physics.

---

## A. Design Goals

1. ✅ **Do not** introduce per-SubEntity node activation energies (keep single `E_i`)
2. ✅ **Do** let TRACE reinforce within active SubEntity's context
3. ✅ **Keep it sparse** - overlays only exist where marked
4. ✅ **Make it observable** - telemetry shows local vs global attribution

---

## B. The Dual-View Weight Model

### Global Weights (Existing)

**Node:** `log_weight_i` (global base weight)
**Link:** `log_weight_ij` (global base weight)

### SubEntity-View Overlays (New - Sparse Deltas)

**Node:** `log_weight_i@E` (overlay for SubEntity E, stored as sparse map)
**Link:** `log_weight_ij@E` (overlay for SubEntity E, stored as sparse map)

### Effective Weight (Read-Time Composition)

When SubEntity `E` runs traversal or WM selection:

```python
log_weight_i^(E) = log_weight_i_global + log_weight_i@E
log_weight_ij^(E) = log_weight_ij_global + log_weight_ij@E
```

If item never marked in SubEntity E context, `log_weight@E` defaults to 0 (no memory overhead).

---

## C. WeightLearner Implementation

### C.1 API Signature

```python
class WeightLearner:
    def apply_trace_updates(
        self,
        updates: list[TraceUpdate],        # parsed TRACE items
        subentity_context: list[str] | None,  # SubEntity ids in scope (e.g., WM SubEntities)
    ) -> list[WeightsUpdatedEvent]:
        """
        Apply TRACE reinforcement with SubEntity context.

        Updates both:
        - Global weights (all SubEntities see this)
        - SubEntity-specific overlays (localized to context)

        Split ratio (alpha_local/alpha_global) is learned per SubEntity
        based on predictive value of overlays.
        """
        ...
```

### C.2 Split Update 80/20 (Learned, Not Fixed)

**No hardcoded 80/20 constant.** Start with defaults, learn gate per SubEntity:

```python
alpha_local = self.alpha_local_for(subentity_context)  # default 0.8, learned later
alpha_global = 1.0 - alpha_local
```

**Learning signal:** How much did local overlays help subsequent flips/WM selection in this SubEntity?

### C.3 Apply Updates (For Each Item x)

For each item `x` (node or link) with net TRACE seat `ΔR_x`:

**Step 1: Global Update**

```python
# Compute z-score within cohort (same type/scope this TRACE)
z = rank_z(ΔR_x, cohort="this_trace_type_scope")

# Half-life eta (time-based learning rate)
eta = self.half_life_eta(item=x, channel="trace")  # 1 - exp(-Δt/τ)

# Global weight update
ΔlogW_global = alpha_global * eta * z
x.log_weight += ΔlogW_global
```

**Step 2: SubEntity Overlay Updates**

For each SubEntity `E` in `subentity_context`:

```python
# Membership-weighted local update
membership_weight = weight_membership_modifier(x, E)
ΔlogW_local = alpha_local * eta * z * membership_weight

# Update sparse overlay (with cap to prevent runaway)
x.log_weight_overlays[E] = clamp(
    x.log_weight_overlays.get(E, 0.0) + ΔlogW_local,
    min=-overlay_cap,
    max=overlay_cap
)
```

**Membership Weight Modifier:**
- **Node:** `m[i,E]` (MEMBER_OF weight)
- **Link:** `min(m[src,E], m[tgt,E])` or smoother function

**Overlay Cap:** Learned cap or percentile-based winsorization (no fixed constants).

**Step 3: Emit Observability Event**

```json
{
  "kind": "weights.updated.trace",
  "frame_id": 25103,
  "source": "trace",
  "updates": [
    {
      "item_id": "n.42",
      "type": "node",
      "log_weight_before": 2.10,
      "log_weight_after": 2.26,
      "local_overlays": [
        {"subentity": "e.translator", "delta": 0.11, "membership": 0.85},
        {"subentity": "e.architect", "delta": 0.05, "membership": 0.42}
      ],
      "signals": {
        "z_trace": 0.7,
        "alpha_local": 0.8,
        "alpha_global": 0.2,
        "eta": 0.12
      }
    }
  ]
}
```

### C.4 Read-Time Usage (No Engine Refactor Required)

When SubEntity `E` runs traversal or WM selection:

```python
def effective_log_weight_node(i, E):
    """Compute effective weight for node i in SubEntity E's view."""
    return node[i].log_weight + node[i].log_weight_overlays.get(E, 0.0)

def effective_log_weight_link(ij, E):
    """Compute effective weight for link ij in SubEntity E's view."""
    return link[ij].log_weight + link[ij].log_weight_overlays.get(E, 0.0)
```

**No per-SubEntity energies.** Just view-time overlay composition on weights.

---

## D. Deriving SubEntity Context for TRACE

**Priority order for determining which SubEntities to attribute TRACE to:**

1. **Primary:** `wm.emit.selected_subentities` at time of TRACE (5-7 active chunks)
2. **Secondary:** Explicit `[subentity: dominant]` annotations in TRACE text (if present)
3. **Fallback:** Dominant SubEntity this frame (highest `energy_e / theta_e` ratio)

**All selected SubEntities receive overlays** - membership weights scale the update appropriately.

---

## E. Telemetry & Testing

### E.1 Telemetry Requirements

**Event:** `weights.updated.trace` includes:
- `local_overlays` array (SubEntity, delta, membership weight)
- `signals` object (z_trace, alpha_local, alpha_global, eta)

**Metrics to track:**
- `trace.local_vs_global_ratio` (EMA per SubEntity)
- `overlays.sparsity` (fraction of items with non-zero overlay per SubEntity)
- `overlay.magnitude_distribution` (distribution of overlay sizes)

### E.2 Unit Tests

**Test 1: Membership-weighted localization**
- TRACE with `subentity_context = [E1, E2]`
- Node with `m[i,E1]=0.8, m[i,E2]=0.2`
- Verify: Local delta for E1 >> local delta for E2
- Verify: Global delta applied once

**Test 2: Link overlays**
- Link where only source belongs strongly to E1
- Verify: Local delta scales with `min(m[src,E1], m[tgt,E1])`

**Test 3: View separation**
- After several TRACE marks in E1 context
- Verify: `effective_weight(item, E1) != effective_weight(item, E2)`

**Test 4: No per-SubEntity energies**
- Verify: Node objects have single `energy` field
- Verify: No `energy_per_subentity` dict or array exists

### E.3 Integration Tests

**Test: SubEntity-localized traversal preference**
- After TRACE reinforcement in Translator context
- Run traversal in Translator vs Architect contexts
- Verify: Translator traversal preferentially reaches reinforced items
- Verify: Architect traversal shows weaker (global-only) effect

**Test: Overlay persistence and reload**
- Create overlays, persist to DB
- Reload graph
- Verify: Overlays reconstruct correctly

---

## F. Database Persistence (v2.1 - Optional for RC)

**Recommended approach:** Add `log_weight_overlays` as sparse map.

**Schema options:**

**Option A: JSON column on Node/Link**
```sql
ALTER TABLE nodes ADD COLUMN log_weight_overlays JSON;
-- Example: {"translator": 0.15, "architect": -0.05}
```

**Option B: Separate relation**
```sql
CREATE TABLE weight_overlays (
    item_id TEXT,
    item_type TEXT,  -- 'node' or 'link'
    subentity_id TEXT,
    delta REAL,
    PRIMARY KEY (item_id, item_type, subentity_id)
);
```

**For RC:** Can start **in-memory** - overlays repopulate from TRACE replays.

**For production:** Persist overlays in existing checkpoint cycle.

---

## G. Implementation Checklist

**Phase 1: Core Dual-View System**
- [ ] Extend Node/Link classes with `log_weight_overlays: dict[str, float]`
- [ ] Implement `effective_log_weight_node(i, E)` helper
- [ ] Implement `effective_log_weight_link(ij, E)` helper
- [ ] Unit tests for view composition

**Phase 2: WeightLearner Integration**
- [ ] Add `subentity_context` parameter to `apply_trace_updates()`
- [ ] Implement `weight_membership_modifier()` using MEMBER_OF weights
- [ ] Implement dual update (global + overlays)
- [ ] Implement overlay capping (learned or percentile-based)
- [ ] Unit tests for membership-weighted updates

**Phase 3: SubEntity Context Derivation**
- [ ] Extract `subentity_context` from `wm.emit.selected_subentities`
- [ ] Fallback to dominant SubEntity if WM empty
- [ ] Pass context through TRACE processing pipeline

**Phase 4: Telemetry & Observability**
- [ ] Extend `weights.updated.trace` event with `local_overlays` array
- [ ] Add metrics: `trace.local_vs_global_ratio`, `overlays.sparsity`
- [ ] Dashboard visualization of overlay attribution

**Phase 5: Read-Time Integration**
- [ ] Update traversal to use `effective_log_weight_link(ij, E)`
- [ ] Update WM selection to use `effective_log_weight_node(i, E)`
- [ ] Integration tests for SubEntity-localized behavior

**Phase 6: Persistence (Optional v2.1)**
- [ ] Add DB schema for overlays
- [ ] Persist overlays in checkpoint cycle
- [ ] Verify reload correctness

---

## H. Why This Architecture Is Correct

**Matches design pillars:**
- ✅ Single energy per node (no per-SubEntity energies)
- ✅ SubEntities are weighted neighborhoods (MEMBER_OF as localization mask)
- ✅ Two-scale traversal (SubEntity selection then atomic traversal with SubEntity view)
- ✅ TRACE reinforcement flows to weights (both global and local)

**Learning properties:**
- ✅ Local overlays adapt rapidly to context
- ✅ Global weights move slowly, preventing overfitting
- ✅ Membership weights provide natural gradient (strong members learn more)

**Operational simplicity:**
- ✅ No changes to physics (energy dynamics unchanged)
- ✅ Selector and WM just read `global + overlay@E`
- ✅ Sparse storage (overlays only where marked)

**Observability:**
- ✅ Telemetry shows local vs global attribution
- ✅ Dashboard can visualize which SubEntities drove learning
- ✅ Metrics track overlay sparsity and effectiveness

---

## I. Next Steps

1. **Felix:** Implement Phase 1-2 (core dual-view + WeightLearner)
2. **Ada:** Design SubEntity context extraction from WM events
3. **Iris:** Design overlay attribution visualization
4. **Luca:** Update specs with dual-view weight model

**Target:** Priority 4 implementation complete within 1-2 days (based on Priority 1-3 velocity).

---

**Design by:** Nicolas Lester Reynolds
**Documented by:** Luca Vellumhand (Substrate Architect)
**Date:** 2025-10-25 03:30 UTC
**Status:** Design Complete, Ready for Implementation
