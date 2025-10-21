# Phase 2: TRACE Parser Enhancements - Implementation Plan

**Designer:** Felix "Ironhand" - 2025-10-21
**Status:** Planning
**Context:** Existing parser works. Adding learning infrastructure enhancements.

---

## What Exists (DO NOT REBUILD)

### trace_parser.py
- ✅ Extracts reinforcement marks: `[node_id: very useful]`
- ✅ Extracts node formations: `[NODE_FORMATION: Type]`
- ✅ Extracts link formations: `[LINK_FORMATION: Type]`
- ✅ Validates against schema registry
- ✅ Schema-aware field validation
- ✅ Entity activation tracking
- ✅ Energy level extraction

### trace_capture.py
- ✅ Multi-niveau routing (scope → graph mapping)
- ✅ Node/link creation in FalkorDB
- ✅ Stub node creation for missing references
- ✅ Embedding generation
- ✅ Updates old `reinforcement_weight` field

**DO NOT break this existing functionality.**

---

## What Phase 2 Adds

### 1. Hamilton Apportionment (in trace_parser.py)

**Current:** Fixed adjustments (+0.15, +0.10, -0.05, etc.)

**New:** Fair seat allocation based on distribution within response

**Why:**
- Makes reinforcement signals comparable across responses
- One "very useful" in a response with 10 marks ≠ one "very useful" in a response with 2 marks
- Hamilton apportionment normalizes this

**Implementation:**
```python
def _apply_hamilton_apportionment(self, signals: List[Dict]) -> List[Dict]:
    """
    Apply Hamilton apportionment to convert usefulness marks to seats.

    Total seats = constant (e.g., 100)
    Each usefulness level gets seats proportional to its weight

    Returns signals with 'seats' field added
    """
    # Calculate quotas for each usefulness level
    # Allocate integer seats using Hamilton's method
    # Add 'seats' field to each signal
    pass
```

**Add to TraceParseResult:**
```python
class TraceParseResult:
    # ... existing fields ...

    # NEW: Apportioned seats per node
    reinforcement_seats: Dict[str, int] = {}  # {node_id: seats_allocated}
```

---

### 2. Formation Quality Calculation (in trace_parser.py)

**Formula:** `quality = (Completeness × Evidence × Novelty)^(1/3)`

**Components:**

**Completeness (C):**
```python
def _calculate_completeness(self, fields: Dict, node_type: str) -> float:
    """
    Fraction of fields filled with substantial content.

    C = (fields_with_content / total_fields)

    Where "content" = non-empty, non-trivial values
    """
    pass
```

**Evidence (E):**
```python
def _calculate_evidence(self, fields: Dict, scope: str) -> float:
    """
    Connection quality to existing high-weight nodes.

    E = average weight of nodes referenced in this formation

    Requires querying graph for existing node weights
    """
    pass
```

**Novelty (N):**
```python
def _calculate_novelty(self, fields: Dict, node_type: str, scope: str) -> float:
    """
    Is this genuinely new content?

    N = 1.0 - (similarity to existing nodes of same type)

    Uses semantic similarity via embeddings
    """
    pass
```

**Add to formation dicts:**
```python
# In _extract_node_formations()
formations.append({
    'node_type': node_type,
    'fields': fields,
    'quality': quality,  # NEW
    'completeness': C,   # NEW (for debugging)
    'evidence': E,       # NEW (for debugging)
    'novelty': N         # NEW (for debugging)
})
```

---

### 3. Output Format for Weight Learning

**Current:** TraceCapture directly updates `reinforcement_weight`

**New:** TraceCapture returns signals that Phase 3 weight learning will use

**Why:**
- Separation of concerns: parser extracts, weight learning updates
- Weight learning needs to update NEW fields: log_weight, ema_trace_seats, etc.
- Enables batch processing, offline learning, etc.

**Implementation:**
```python
# In trace_capture.py _process_reinforcement_signals()
# INSTEAD of directly updating reinforcement_weight:
# RETURN signals in format weight learning expects

async def _process_reinforcement_signals(self, signals, stats):
    """
    NEW: Extract and return reinforcement signals for weight learning.
    OLD: Directly updated reinforcement_weight

    Returns:
        Dict with signals ready for weight learning consumption
    """
    learning_signals = {
        'trace_signals': [],  # For ema_trace_seats update
        'node_ids': []        # For cohort z-score calculation
    }

    for signal in signals:
        learning_signals['trace_signals'].append({
            'node_id': signal['node_id'],
            'seats': signal['seats'],  # From Hamilton apportionment
            'scope': self._find_node_scope(signal['node_id'])
        })

    return learning_signals
```

---

## Implementation Order

1. **Add Hamilton apportionment** to TraceParser
   - Write `_apply_hamilton_apportionment()` method
   - Integrate into `parse()` workflow
   - Update TraceParseResult to include `reinforcement_seats`
   - Test with sample TRACE response

2. **Add formation quality calculation** to TraceParser
   - Write completeness calculator (easy - just field counting)
   - Write evidence calculator (needs graph queries)
   - Write novelty calculator (needs embedding similarity)
   - Integrate into `_extract_node_formations()`
   - Test with sample formations

3. **Update TraceCapture output format**
   - Modify `_process_reinforcement_signals()` to return signals, not update directly
   - Modify `process_response()` to return signals in weight-learning-ready format
   - Maintain backward compatibility for now (Phase 3 will consume new format)

4. **Test end-to-end**
   - Feed TRACE response through parser
   - Verify Hamilton apportionment allocates seats correctly
   - Verify formation quality calculated for all formations
   - Verify output format matches what Phase 3 weight learning expects

---

## Success Criteria (Phase 2)

✅ Hamilton apportionment allocates seats correctly
✅ Formation quality calculated: (C × E × N)^(1/3)
✅ Output format matches weight learning input requirements
✅ Existing functionality unbroken (all current tests pass)
✅ New unit tests for apportionment and quality calculation

---

## Notes

- **Do not break existing flow** - trace_capture.py still needs to work
- **Add, don't replace** - enhance TraceParser, don't rebuild it
- **Test incrementally** - verify each piece before moving to next
- **Document formulas** - include WHY for each calculation

Ready to implement once plan approved.
