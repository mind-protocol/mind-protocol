# SYNC — Universe Link Schema (L3)

```
STATUS: DESIGNING
UPDATED: 2026-03-13
AUTHOR: @nervo
```

---

## Current State

The L3 Universe Link Schema doc chain is **freshly created**. All four documents (OBJECTIVES, PATTERNS, ALGORITHM, VALIDATION) are in DESIGNING status.

### What exists:
- OBJECTIVES: 5 primary objectives + non-objectives + tradeoffs defined
- PATTERNS: 11 mandatory link dimensions specified with defaults, synthesis grammar, macro-crystallization, trust mechanics, L1/L3 boundary
- ALGORITHM: 6 algorithms with pseudocode (link creation, trust propagation, macro-crystallization, decay/dissolution, trust score computation, name derivation)
- VALIDATION: 6 invariants (V1-V6) with priority classification

### What does NOT exist yet:
- Implementation code (no runtime, no tests)
- BEHAVIORS doc (deferred — behaviors are documented inline in PATTERNS)
- HEALTH doc (deferred — no runtime to health-check yet)
- IMPLEMENTATION doc (deferred — no code yet)
- Concrete values for some constants (MACRO_CRYSTAL_THRESHOLD, MAX_ACTIVE_NODES, GROWTH_TOLERANCE)

---

## Maturity

STATUS: DESIGNING

**What's canonical (design-level):**
- The 11 link dimensions and their ranges
- Trust on links, never on nodes
- Link names derived from dimensions (synthesis grammar)
- Macro-crystallization as the boundedness mechanism
- No limbic dimensions on L3 links

**What's still being designed:**
- Optimal constant values for crystallization thresholds and intervals
- Whether recursive trust (Algorithm 5 Step 3) should be default or opt-in
- Community detection algorithm choice for macro-crystallization
- Performance characteristics at scale (>100K nodes)

**What's proposed (v2):**
- "Confidence" dimension for epistemic relationships
- "Bandwidth" dimension for information flow rate
- Per-universe crystallization cadence
- Incremental crystallization (process only new moments)

---

## Open Questions

1. **Recursive trust**: Should transitive trust propagation (PageRank-style) be the default computation, or should it be opt-in for specific queries? Recursive trust is more accurate for ecosystem reputation, but adds complexity and potential cycles.

2. **Crystallization constants**: The MACRO_CRYSTAL_INTERVAL (500 ticks), MACRO_CRYSTAL_MIN_NODES (10), and density/weight thresholds need empirical calibration against real graph data from La Serenissima.

3. **Energy conservation at L3**: Should total energy in the graph be strictly conserved (injection = creation, decay = destruction, propagation = redistribution)? L1 does this via Law 2's surplus spill-over. L3 currently has energy injection without a global budget.

---

## Handoffs

**For implementers (groundwork agent):**
- Start with Algorithm 1 (Link Creation) and Algorithm 4 (Decay/Dissolution) — these are the simplest and most testable
- Algorithm 2 (Trust Propagation) requires L1 integration — defer until L1 tick loop emits limbic deltas
- Algorithm 3 (Macro-Crystallization) needs performance testing with synthetic graphs

**For @nervo (next session):**
- Calibrate constants against La Serenissima graph data (152 citizens, 7 districts)
- Decide on recursive trust (escalation marker in ALGORITHM doc)

**For doc chain validators (keeper agent):**
- Verify MAPPING.md was updated with L3 link dimension section
- Verify no other doc in the ecosystem contradicts the "trust on links not nodes" invariant

---

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
