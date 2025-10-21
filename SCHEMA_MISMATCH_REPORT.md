# Schema Mismatch Report: Specification vs Database

**Date:** 2025-10-21
**Purpose:** Document all mismatches between specification requirements and actual FalkorDB implementation
**Severity:** CRITICAL - System cannot function per spec with current schema

---

## Executive Summary

The database schema is **NOT compliant** with the specifications written in `docs/specs/consciousness_engine_architecture/mechanisms/`. Multiple critical fields are missing or have wrong types.

**Critical Issues:**
1. ❌ Nodes use `energy: float` instead of `energy: Dict[str, float]` (breaks multi-entity architecture)
2. ❌ Nodes missing `log_weight` field (core learning infrastructure)
3. ❌ Nodes missing 3 EMA fields for learning (`ema_wm_presence`, `ema_trace_seats`, `ema_formation_quality`)
4. ❌ Links missing 9 trace fields (breaks consciousness memory)
5. ❌ Links missing `log_weight` field (breaks link learning)

---

## Part 1: Node Schema Mismatches

### 1.1 CRITICAL: Energy Field Type Mismatch

**Specification:** `01_multi_energy_architecture.md` (lines 49-62)
```python
# REQUIRED (per spec):
energy: Dict[str, float]  # {entity_name: energy_value}

# Example:
{
  "translator": 0.8,
  "validator": 0.2,
  "architect": 0.5
}
```

**Actual Database:**
```python
energy: float  # Single global value
```

**Why This Breaks Everything:**
- **Spec requirement:** "Each node maintains separate energy values per entity" (05_sub_entity_system.md:2019)
- **Spec requirement:** "Energy is partitioned per entity at shared nodes" (05_sub_entity_system.md:1657)
- **Consequence:** Multi-entity architecture CANNOT work with single float
- **Biological basis:** Different brain regions (entities) process same information simultaneously

**Migration Required:** YES - convert all `energy: float` → `energy: {}`

---

### 1.2 CRITICAL: Missing log_weight Field

**Specification:** Multiple documents reference `log_weight` as core learning field

**Documents:**
- `05_sub_entity_weight_learning_addendum.md` (lines 26-36): "Single log_weight Per Item"
- `consciousness_learning_integration.md` (line 245): "delta_log_weight = eta * (z_R[i] + z_F[i])"
- `ENTITY_LAYER_ORCHESTRATION_REQUIREMENTS.md` (line 87): "log_weight: float"

**Required:**
```python
log_weight: float = 0.0  # Logarithmic learned importance
```

**Actual Database:**
```python
weight: float  # Exists, but is this the same as log_weight?
```

**QUESTION:** Is `weight` field supposed to BE `log_weight`, or are they different?

**If different:**
- Migration: Rename `weight` → `log_weight`
- Migration: Initialize all existing nodes with `log_weight = 0.0`

**If same:**
- Spec needs updating to use consistent naming

---

### 1.3 CRITICAL: Missing EMA Learning Fields

**Specification:** `trace_weight_learning.md` (lines 164-184)

**Required Node EMA Fields:**
```python
ema_trace_seats: float = 0.0        # From TRACE reinforcement (Hamilton apportionment)
ema_formation_quality: float = 0.0  # From (C×E×N)^(1/3) formation quality
ema_wm_presence: float = 0.0        # From working memory selection frequency
```

**Actual Database:**
- ❌ `ema_trace_seats`: **MISSING**
- ❌ `ema_formation_quality`: **MISSING**
- ❌ `ema_wm_presence`: **MISSING**

**Why Critical:**
- These fields enable learning from TRACE format and working memory
- Spec formula: `Δ log_weight = η · (z_R + z_F + z_rein + z_wm + z_form)` (05_sub_entity_weight_learning_addendum.md:42)
- Without these, 60% of learning signals are lost

**Migration Required:** YES - add all 3 fields, default 0.0

---

### 1.4 MINOR: Field Type Mismatches

**Specification expects:**
```python
sub_entity_weights: Dict[str, float]
sub_entity_last_sequence_positions: Dict[str, int]
sub_entity_weight_counts: Dict[str, int]
```

**Actual Database:**
```python
sub_entity_weights: str  # JSON string
sub_entity_last_sequence_positions: str  # JSON string
sub_entity_weight_counts: str  # JSON string
```

**Status:** ✅ ACCEPTABLE - FalkorDB limitation, JSON strings work
**Note:** Code must parse JSON on read, serialize on write

---

### 1.5 Node Schema Summary

| Field | Spec Type | Actual Type | Status | Action |
|-------|-----------|-------------|--------|--------|
| `energy` | `Dict[str, float]` | `float` | ❌ WRONG | **MIGRATE** |
| `log_weight` | `float` | **MISSING** | ❌ MISSING | **ADD or RENAME** |
| `ema_trace_seats` | `float` | **MISSING** | ❌ MISSING | **ADD** |
| `ema_formation_quality` | `float` | **MISSING** | ❌ MISSING | **ADD** |
| `ema_wm_presence` | `float` | **MISSING** | ❌ MISSING | **ADD** |
| `weight` | ??? | `float` | ❓ UNCLEAR | **CLARIFY** |
| `sub_entity_weights` | `Dict` | `str` (JSON) | ✅ OK | None |
| `sub_entity_last_sequence_positions` | `Dict` | `str` (JSON) | ✅ OK | None |
| `sub_entity_weight_counts` | `Dict` | `str` (JSON) | ✅ OK | None |
| `confidence` | `float` | `float` | ✅ OK | None |
| `created_at` | `datetime` | `str` | ✅ OK | None |
| `valid_at` | `datetime` | `str` | ✅ OK | None |
| `description` | `string` | `string` | ✅ OK | None |
| `name` | `string` | `string` | ✅ OK | None |

---

## Part 2: Link Schema Mismatches

### 2.1 CRITICAL: Missing 9 Trace Fields

**Specification:** `LINK_TRACE_FIELDS_FOR_FELIX.md` (complete document)

**Required Link Fields:**
```python
ema_active: float = 0.0                    # Habitual activation EMA
ema_flow_mag: float = 0.0                  # Typical flow strength EMA
precedence_forward: float = 0.0            # Causal credit i→j
precedence_backward: float = 0.0           # Causal credit j→i
ema_hunger_gates: List[float] = [0.0] * 7 # 7 hunger gate EMAs
affect_tone_ema: float = 0.0               # Emotional harmony EMA
topic_centroid: Optional[List[float]] = None  # Semantic region embedding
last_payload_ts: Optional[datetime] = None # Last time link fired
observed_payloads_count: int = 0           # Total fire count
```

**Actual Database:**
```python
# Query shows NONE of these 9 fields exist
# Links only have: activated, co_activation_count, confidence, created_at,
# formation_trigger, goal, link_strength, mindstate, traversal_count, etc.
```

**Why Critical:**
- "Links ARE consciousness" - these fields make links queryable memory
- Direction priors (precedence) needed for stimulus injection (stimulus_injection_specification.md)
- Hunger characterization needed for entity layer (05_sub_entity_system.md)
- Without these: links are invisible plumbing, not consciousness trace

**Migration Required:** YES - add all 9 fields

---

### 2.2 CRITICAL: Missing log_weight Field

**Specification:** Multiple references to link weight learning

**Required:**
```python
log_weight: float = 0.0  # Learned link importance
```

**Actual Database:**
```python
link_strength: float  # Is this supposed to be log_weight?
```

**Same question as nodes:** Is `link_strength` the same as `log_weight` or different?

**Spec Update Formula:** (consciousness_learning_integration.md:332-333)
```python
delta_log_weight = eta * traversal_signal
link.log_weight += delta_log_weight
```

---

### 2.3 Link Schema Summary

| Field | Spec Type | Actual Type | Status | Action |
|-------|-----------|-------------|--------|--------|
| `ema_active` | `float` | **MISSING** | ❌ MISSING | **ADD** |
| `ema_flow_mag` | `float` | **MISSING** | ❌ MISSING | **ADD** |
| `precedence_forward` | `float` | **MISSING** | ❌ MISSING | **ADD** |
| `precedence_backward` | `float` | **MISSING** | ❌ MISSING | **ADD** |
| `ema_hunger_gates` | `List[float]` | **MISSING** | ❌ MISSING | **ADD** |
| `affect_tone_ema` | `float` | **MISSING** | ❌ MISSING | **ADD** |
| `topic_centroid` | `List[float]` | **MISSING** | ❌ MISSING | **ADD (optional)** |
| `last_payload_ts` | `datetime` | **MISSING** | ❌ MISSING | **ADD** |
| `observed_payloads_count` | `int` | **MISSING** | ❌ MISSING | **ADD** |
| `log_weight` | `float` | **MISSING** | ❌ MISSING | **ADD or RENAME** |
| `link_strength` | ??? | `float` | ❓ UNCLEAR | **CLARIFY** |
| `goal` | `string` | `string` | ✅ OK | None |
| `mindstate` | `string` | `string` | ✅ OK | None |
| `confidence` | `float` | `float` | ✅ OK | None |
| `created_at` | `datetime` | `str` | ✅ OK | None |

---

## Part 3: Migration Strategy

### 3.1 Required Migrations (Priority Order)

**Priority 1: Energy Structure (BLOCKS EVERYTHING)**
```python
# For every node in every graph:
# 1. Read current energy: float
# 2. Convert to: {"default": current_energy}
# 3. Write back as JSON string (FalkorDB limitation)

MATCH (n)
SET n.energy = '{"default": ' + toString(n.energy) + '}'
```

**Priority 2: Add Missing Learning Fields**
```python
# For every node:
MATCH (n)
SET n.log_weight = COALESCE(n.weight, 0.0),
    n.ema_trace_seats = 0.0,
    n.ema_formation_quality = 0.0,
    n.ema_wm_presence = 0.0
```

**Priority 3: Add Missing Link Trace Fields**
```python
# For every link:
MATCH ()-[r]->()
SET r.ema_active = 0.0,
    r.ema_flow_mag = 0.0,
    r.precedence_forward = 0.0,
    r.precedence_backward = 0.0,
    r.ema_hunger_gates = '[0,0,0,0,0,0,0]',
    r.affect_tone_ema = 0.0,
    r.last_payload_ts = null,
    r.observed_payloads_count = 0,
    r.log_weight = COALESCE(r.link_strength, 0.0)
```

**Priority 4: Optional - topic_centroid**
```python
# Large field (~3-6KB per link), can compute on-demand
# Decision: Store or compute?
```

---

### 3.2 Code Changes Required

**After migration, update all code that:**

1. **Reads/writes node energy**
   - Change: `node.energy` → `json.loads(node.energy).get(entity_name, 0.0)`
   - Change: `node.energy = value` → `node.energy = json.dumps({...})`

2. **Uses weight fields**
   - Clarify: `weight` vs `log_weight` semantics
   - Update: All references to use `log_weight` consistently

3. **Computes learning updates**
   - Add: EMA update logic for `ema_trace_seats`, `ema_formation_quality`, `ema_wm_presence`
   - Add: Link trace field updates during traversal

4. **Stimulus injection**
   - Add: Direction prior logic using `precedence_forward` / `precedence_backward`

---

## Part 4: Clarification Questions

**QUESTION 1:** Is `node.weight` the same as `node.log_weight`?
- If YES: Rename everywhere for consistency
- If NO: What is `weight` used for?

**QUESTION 2:** Is `link.link_strength` the same as `link.log_weight`?
- If YES: Rename everywhere
- If NO: What is `link_strength` used for?

**QUESTION 3:** Should `topic_centroid` be stored or computed on-demand?
- Stored: ~3-6KB per link, faster queries
- Computed: No storage cost, slower queries

**QUESTION 4:** For energy migration, what should default entity name be?
- Option A: `"default"`
- Option B: `"system"`
- Option C: `"global"`
- Option D: Graph-specific (e.g., `"luca"` for citizen_luca graph)

---

## Part 5: Testing Requirements

**After migration, verify:**

1. ✅ All nodes have `energy` as dict (not float)
2. ✅ Energy dict has at least one entity key
3. ✅ All nodes have `log_weight` field
4. ✅ All nodes have 3 EMA fields (trace_seats, formation_quality, wm_presence)
5. ✅ All links have 9 trace fields
6. ✅ All links have `log_weight` field
7. ✅ Code reads/writes energy correctly (dict not float)
8. ✅ Learning updates all EMA fields correctly
9. ✅ Traversal updates link trace fields correctly
10. ✅ Stimulus injection uses precedence for direction priors

---

## Conclusion

**The database schema is NOT specification-compliant.**

**Immediate Actions Required:**
1. Decide on `weight` vs `log_weight` naming
2. Run migration scripts (Priority 1, 2, 3)
3. Update all code to use dict-based energy
4. Add EMA update logic throughout system
5. Test all learning mechanisms work with new schema

**Estimated Migration Impact:**
- Database: ~3 migration scripts
- Code changes: ~20-30 files need energy access updates
- Learning mechanisms: ~5 files need EMA logic
- Testing: Full system integration test required

**Timeline Estimate:**
- Migration scripts: 2 hours
- Code updates: 4-6 hours
- Testing: 2-3 hours
- **Total: 8-11 hours of focused work**

---

**This report generated from:**
- Spec sources: `docs/specs/consciousness_engine_architecture/mechanisms/`
- Database query: `citizen_luca` graph on 2025-10-21
- Key specs: `01_multi_energy_architecture.md`, `05_sub_entity_system.md`, `05_sub_entity_weight_learning_addendum.md`, `LINK_TRACE_FIELDS_FOR_FELIX.md`, `trace_weight_learning.md`, `consciousness_learning_integration.md`
