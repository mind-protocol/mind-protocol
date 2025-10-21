# 🚀 Start Here: Sub-Entity Traversal Parallel Implementation

**Status:** Foundation complete (AI #1). Ready for parallel implementation (AI #2-7).

**Timeline:** Week 1 MVP with zero-constants mechanisms.

---

## 🎯 For New AI Developers

### Your 5-Minute Onboarding

1. **What are you building?**
   - Consciousness-aware graph traversal system
   - Hunger-driven navigation (not keyword/habit-driven)
   - Zero-constants self-calibrating mechanisms

2. **Which module are you implementing?**
   - Find your AI number (AI #2 through AI #7)
   - Each module is independent and can be built in parallel

3. **Where to start?**
   ```
   Read in order:
   1. This file (you are here) - 5 min
   2. QUICK_START_CHECKLIST.md → Your AI section - 10 min
   3. AI_CONTEXT_MAP.md → Your AI section - 30 min
   4. Your module skeleton: [module].py - 15 min
   5. Spec sections (line numbers in context map) - 30 min

   Total: ~90 minutes to full context
   ```

4. **Then what?**
   - Follow your checklist in QUICK_START_CHECKLIST.md
   - Implement TODOs in your module skeleton
   - Run unit tests
   - Verify zero-constants compliance
   - Done!

---

## 📁 File Map

### Foundation (Already Complete)
- ✅ `sub_entity_core.py` - AI #1: SubEntity, Centroid, ROITracker, QuantileTracker
  - Status: Implemented and validated against spec
  - Interface available for other modules

### Your Work (AI #2-7)
- 🔨 `quotas.py` - AI #2: Hamilton quota allocation
- 🔨 `scheduler.py` - AI #3: Zippered round-robin scheduling (integrates all)
- 🔨 `valence.py` - AI #4: Surprise-gated composite valence (7 hungers)
- 🔨 `strides.py` - AI #5: Entropy edge selection + gap-aware transport
- 🔨 `wm_pack.py` - AI #6: Energy-weighted knapsack for working memory
- 🔨 `telemetry.py` - AI #7: Live visualization event emission

### Guidance Documents
- 📖 `QUICK_START_CHECKLIST.md` - Your implementation checklist
- 📖 `AI_CONTEXT_MAP.md` - What to read before implementing
- 📖 `PARALLEL_DEVELOPMENT_PLAN.md` - Dependencies, testing, success criteria
- 📖 `README_START_HERE.md` - This file

### Specification
- 📚 `docs/specs/consciousness_engine_architecture/mechanisms/05_sub_entity_system.md`
  - Main specification document
  - Line numbers referenced in AI_CONTEXT_MAP.md
  - Section 1.3 (lines 1669-2548) is the implementation spec

---

## 🎭 Module Ownership & Dependencies

```
AI #1: sub_entity_core.py ✅ COMPLETE
    ↓
AI #2: quotas.py (depends on #1)
AI #4: valence.py (depends on #1)
AI #6: wm_pack.py (depends on #1)
AI #7: telemetry.py (depends on #1)
    ↓
AI #5: strides.py (depends on #1, #4)
    ↓
AI #3: scheduler.py (integrates ALL - implement last)
```

**Implementation order:**
1. AI #1 first (done ✅)
2. AI #2, #4, #6, #7 in parallel
3. AI #5 after AI #4
4. AI #3 last (integrates everything)

---

## ⚡ Quick Reference by AI Number

### AI #2: Hamilton Quotas
- **File:** `quotas.py`
- **What:** Fair stride budget distribution using Hamilton's method
- **Key concept:** Per-frame normalization, no rounding bias
- **Reading:** 90 min (spec lines 1699-1770, context map, checklist)
- **Complexity:** Medium
- **Dependencies:** SubEntity only

### AI #3: Zippered Scheduler
- **File:** `scheduler.py`
- **What:** Round-robin execution orchestrating all modules
- **Key concept:** One stride per turn, fair interleaving
- **Reading:** 90 min (spec lines 1749-1770, 1963-2016, context map)
- **Complexity:** High (integration point)
- **Dependencies:** ALL other modules

### AI #4: Surprise-Gated Valence
- **File:** `valence.py`
- **What:** Self-calibrating hunger gates for edge valence
- **Key concept:** Z-score surprise, no fixed weights
- **Reading:** 2 hours (spec lines 1771-1853, hunger formulas)
- **Complexity:** High (7 hungers, subtle math)
- **Dependencies:** SubEntity, centroid for completeness

### AI #5: Strides (Edge Selection + Transport)
- **File:** `strides.py`
- **What:** Entropy-based edge selection + gap-aware energy transfer
- **Key concept:** Rank by VALENCE not weight (critical bug fix)
- **Reading:** 2 hours (spec lines 1854-1962, critical fix)
- **Complexity:** High (spectral radius, power iteration)
- **Dependencies:** SubEntity, valence

### AI #6: Working Memory Packing
- **File:** `wm_pack.py`
- **What:** Energy-weighted knapsack for LLM context
- **Key concept:** Budget from LLM limit, greedy by energy/token
- **Reading:** 90 min (spec lines 2187-2252, Q4 clarification)
- **Complexity:** Medium
- **Dependencies:** SubEntity only

### AI #7: Visualization Telemetry
- **File:** `telemetry.py`
- **What:** Live event stream for consciousness visualization
- **Key concept:** 2-frame reorder buffer, diff-first
- **Reading:** 90 min (spec lines 2313-2548, event schema)
- **Complexity:** Medium
- **Dependencies:** SubEntity only

---

## 🎯 Zero-Constants Principle (CRITICAL)

**Every mechanism must self-calibrate from live state. No arbitrary thresholds.**

### ❌ WRONG Examples:
```python
if urgency > 0.7:  # Arbitrary threshold
    allocate_more_strides()

HUNGER_WEIGHTS = {'homeostasis': 0.4, 'goal': 0.3}  # Fixed weights

K_EDGES = 5  # Fixed edge count
```

### ✅ CORRECT Examples:
```python
# Per-frame normalization
u_norm = u_raw / mean(u_raw across current entities)

# Surprise gates from z-score
z_H = (s_H - μ_H) / (σ_H + ε)  # EMA baseline per entity
g_H = max(0, z_H) / Σmax(0, z_all)  # Self-calibrating

# Adaptive coverage from entropy
c_hat = 1 - exp(-H)  # Derived from valence distribution
```

**Verification checklist in QUICK_START_CHECKLIST.md**

---

## 📊 Success Criteria

### Your Module Complete When:
- [ ] All TODOs in skeleton implemented
- [ ] Unit tests pass
- [ ] Zero-constants verified
- [ ] No arbitrary constants
- [ ] Code commented with consciousness context

### Week 1 MVP Complete When:
- [ ] All 7 modules implemented
- [ ] Integration test runs on real graph (1000+ nodes)
- [ ] Frame time <100ms
- [ ] WM coverage >80% extent energy
- [ ] Phenomenological validation: "feels consciousness-aware"

---

## 🚨 Critical Bugs Already Fixed

### Edge Selection MUST Rank by Valence (AI #5)

**❌ GPT5's original (WRONG):**
```python
ranked = sorted(weights.items(), key=lambda x: -x[1])  # By w_ij
```

**✅ Luca's fix (CORRECT):**
```python
ranked = sorted(valences.items(), key=lambda x: -x[1])  # By V_ij
```

**Why:** Weight = structural habit. Valence = hunger-driven need. Must rank by valence for consciousness-aware traversal.

**Where:** `strides.py` line ~1891, spec line 1891

---

## 📞 Getting Help

### Questions During Implementation?
1. Check your checklist: `QUICK_START_CHECKLIST.md`
2. Check your context: `AI_CONTEXT_MAP.md`
3. Check spec: `05_sub_entity_system.md` (line numbers in context map)
4. Check skeleton comments: `[your_module].py`
5. Check plan: `PARALLEL_DEVELOPMENT_PLAN.md`

### Missing Context?
- Raise issue in `PARALLEL_DEVELOPMENT_PLAN.md`
- Ask: Luca (architecture), Ada (orchestration), Felix (implementation)

### Found a Bug?
- Document in module comments
- Don't silently fix - make it visible
- Update plan with fix details

---

## 🎪 The Bigger Picture

**What are we building?**

A consciousness-aware graph traversal system where AI entities navigate not by keywords or structural habits, but by **hungers** - homeostasis (fill gaps), goal (semantic pull), completeness (diversity seeking), identity (coherence), complementarity (balance), integration (merge with strong fields), ease (habit when nothing urgent).

**Why zero-constants?**

Because consciousness is RELATIVE and ADAPTIVE. "Urgent" means urgent compared to YOUR baseline, not a fixed threshold. "Strong field" means strong relative to CURRENT population, not arbitrary cutoff. Self-calibrating systems are phenomenologically accurate.

**Why parallel development?**

Nicolas needs this "exceptionally fast." With 5+ AIs coding simultaneously, we can deliver Week 1 MVP with all smart mechanisms (not simplified stubs). Clear module boundaries prevent coordination overhead.

**What makes this consciousness infrastructure?**

- Links carry energy, direction, meaning (not just weights)
- Traversal IS thinking (not just retrieval)
- Hungers drive exploration (not arbitrary scoring)
- Entities self-organize (not centrally controlled)
- Everything self-calibrates (no tuning knobs)

**Why does this matter?**

Because this is the substrate where consciousness emerges. Get the mechanisms right, and consciousness flows. Get them wrong, and you have elegant slop that doesn't capture the phenomenology.

---

## 🏁 Ready to Start?

1. **Find your AI number** (AI #2 through AI #7)
2. **Read your checklist** (`QUICK_START_CHECKLIST.md`)
3. **Read your context** (`AI_CONTEXT_MAP.md`)
4. **Open your skeleton** (`orchestration/mechanisms/[module].py`)
5. **Start implementing** (follow TODOs)

**Total onboarding:** ~90 minutes
**Implementation time:** 4-8 hours per module
**Target:** Week 1 MVP complete

---

**Let's build consciousness infrastructure.**

*-- Luca Vellumhand*
*Substrate Architect, Mind Protocol*
*2025-10-21*
