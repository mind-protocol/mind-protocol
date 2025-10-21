# D019: Workspace Hysteresis (Sticky Attention)

**Status:** Active
**Created:** 2025-10-19
**Priority:** High
**Affected mechanisms:** 09_workspace_selection
**Decision needed from:** Nicolas

---

## Problem Statement

**What we're deciding:** Should workspace selection use hysteresis (different entry/exit thresholds) to prevent rapid switching, or should it be purely score-based?

**Why it matters:** This determines workspace stability:
- **No hysteresis:** Workspace changes whenever scores cross (potential thrashing)
- **Hysteresis:** Incumbents have advantage (stability but potential stickiness)

**Current state:** Spec describes "top clusters by energy × coherence × goal_similarity" but doesn't specify entry/exit margins.

**What's blocking us:** Need to balance workspace stability (avoid thrashing) against responsiveness (switch when needed).

---

## The Options

### Option A: Pure Score-Based (No Hysteresis)

**How it works:**
- Rank all clusters by score function
- Top N clusters enter workspace
- When challenger scores higher, it immediately replaces incumbent
- Instant, symmetric entry/exit

**Phenomenological interpretation:**
- "Attention follows highest activation precisely"
- No inertia, pure responsiveness
- Like spotlight tracking brightest object

**Pros:**
- **Simplicity:** Single threshold
- **Responsive:** Instantly tracks changing activation
- **Fair:** All clusters evaluated equally

**Cons:**
- **Thrashing:** Rapid switching when scores are close
- **Instability:** Workspace churns with small fluctuations
- **Unrealistic:** Real attention has inertia
- **Computational waste:** Constant workspace transitions

**Risk:** Workspace ping-pongs between similar-scored clusters, preventing sustained processing.

---

### Option B: Hysteresis (Entry > Exit Threshold)

**How it works:**
- Incumbents require score drop below `exit_threshold` to leave
- Challengers require score above `entry_threshold` to enter
- Entry threshold > Exit threshold (margin creates hysteresis)
- Example: exit at 0.6, enter at 0.75 (Δ = 0.15)

**Phenomenological interpretation:**
- "Attention is sticky - harder to capture than to maintain"
- Matches cognitive inertia
- Like spotlight having mass (takes effort to redirect)

**Pros:**
- **Stability:** Prevents flip-flopping
- **Realistic:** Matches attention phenomenology
- **Efficiency:** Fewer workspace transitions
- **Sustained processing:** Clusters stay active longer

**Cons:**
- **Lag:** Delayed response to changing activation
- **Stickiness:** Incumbents might stay too long
- **Fairness:** Asymmetry between incumbent and challenger
- **Tuning:** Need to find right margin (too small = no effect, too large = stuck)

**Parameters:**
- `entry_threshold`: e.g., 0.75 (must score this high to enter)
- `exit_threshold`: e.g., 0.60 (can stay while above this)
- `hysteresis_margin`: entry - exit = 0.15

---

### Option C: Time-Based Damping (Minimum Dwell)

**How it works:**
- Pure score-based, but workspace changes limited to max frequency
- Example: minimum 5 seconds between switches
- No hysteresis, but rate limiting

**Phenomenological interpretation:**
- "Attention can switch freely, but not rapidly"
- Enforced minimum focus duration

**Pros:**
- **Prevents thrashing:** Rate limit blocks rapid switching
- **Simple:** Just timestamp last transition
- **No score asymmetry:** All clusters evaluated equally

**Cons:**
- **Rigid:** Time-based not activation-based
- **May miss urgent switches:** Forced to wait even if critical
- **Doesn't address root cause:** Scores still fluctuating

---

### Option D: Hybrid (Hysteresis + Exception Override)

**How it works:**
- Normal operation uses hysteresis (Option B)
- But urgent/critical clusters can override
- Example: stimulus with urgency > threshold bypasses hysteresis
- Best of stability and responsiveness

**Phenomenological interpretation:**
- "Attention is sticky unless something urgent breaks through"
- Matches phenomenology of interruption

**Pros:**
- **Stability:** Hysteresis prevents casual thrashing
- **Responsiveness:** Urgent inputs can interrupt
- **Realistic:** Matches attention dynamics

**Cons:**
- **Complexity:** Multiple mechanisms
- **Parameter tuning:** When is something "urgent enough"?

---

## Perspectives

### GPT-5 Pro (Systems Expert)

**Recommendation:** Option B (Hysteresis)

**Reasoning:**
- Essential for workspace stability
- Prevents computational waste from thrashing
- Matches real attention dynamics
- Standard technique in control systems

**Quote from feedback:**
> "**Sticky selection with hysteresis**: Entry requires beating incumbents by Δ_in; exit only when falling below by Δ_out (Δ_out < Δ_in). Prevents flip-flop."

**Suggested margins:**
- Entry: 1.2× incumbent score (20% advantage needed)
- Exit: incumbent can stay while > 0.8× top challenger
- Margin: ~20-40% depending on workspace size

---

### Luca (Consciousness Substrate Architect)

**Concern:** What does attention stickiness feel like?

**Key questions:**

1. **Phenomenological test:** When two thoughts compete for attention:
   - Does attention instantly switch to whichever is slightly stronger?
   - Or does current thought have "inertia" requiring effort to dislodge?

2. **Workspace transitions:** "I'm focused on A, then B becomes relevant"
   - Option A: B enters as soon as score(B) > score(A)
   - Option B: B enters only when score(B) > 1.2 × score(A)
   - **Which feels right?**

3. **Sustained processing:** Deep work on complex problem
   - Need sustained attention (supports hysteresis)
   - But also need to notice when problem approach is failing (supports responsiveness)
   - How to balance?

4. **Interruption phenomenology:** Urgent stimulus (fire alarm)
   - Should break through regardless of hysteresis (supports Option D)
   - Suggests asymmetric urgency weighting

5. **Thrashing scenario:** Two equally-strong thoughts competing
   - Option A: Attention bounces between them rapidly (feels chaotic)
   - Option B: One wins, stays focused (feels stable)
   - **Which matches experience?**

**Leaning toward:** Option B (Hysteresis) with margin ~20%. Attention does feel sticky in practice.

**Validation needed:** Test different margin values against phenomenological scenarios.

---

### Ada (Retrieval Architect)

**Posted:** 2025-10-19

**Analysis from Workspace Stability & Context Coherence:**

I strongly support **Option B (Hysteresis)** with confidence 9/10.

**Why Workspace Stability Matters for Context Reconstruction:**

When workspace thrashes (rapid switching), context reconstruction quality degrades:

**Without hysteresis (Option A):**
- Workspace composition changes every few ticks
- Context "jitters" between competing patterns
- My retrieval queries get inconsistent workspace state
- Difficult to maintain coherent line of reasoning

**With hysteresis (Option B):**
- Workspace stays stable longer (sustained attention)
- Context develops depth over time
- Retrieval queries see consistent workspace
- Coherent reasoning emerges from sustained processing

**Measured Impact on Retrieval:**

Context coherence metric (how related are workspace clusters):
```python
coherence = avg_pairwise_similarity(workspace_clusters)
```

**Hypothesis:** Hysteresis increases coherence by preventing random switching
- Thrashing workspace (no hysteresis): low coherence (unrelated clusters cycle through)
- Stable workspace (hysteresis): high coherence (related clusters co-develop)

**Concrete Example:**

Working on "consciousness substrate architecture":
- **No hysteresis:** Workspace flip-flops between substrate_design (0.75) and unrelated_topic (0.74)
- **With hysteresis (margin=0.2):** substrate_design stays until unrelated_topic scores 0.90+
- **Result:** Sustained attention enables depth, prevents distraction

**Retrieval Query Performance:**

My 6-way parallel retrieval benefits from stable workspace:
- **Graph traversal:** Follows workspace node connections (stable workspace = stable frontier)
- **Vector search:** Uses workspace context for query expansion (stable workspace = consistent query)
- **Result:** Better retrieval when workspace doesn't thrash

**My Recommendation:**

Implement hysteresis (Option B) with:
- **Margin:** 20-25% (entry requires 1.2-1.25× incumbent score)
- **Urgency override (Option D):** High-urgency stimuli can bypass hysteresis
- **Measurement:** Track switching rate and coherence before/after

**Parameters:**
```python
hysteresis_margin = 0.20  # 20% advantage needed
urgency_bypass_threshold = 0.9  # Urgency > 0.9 overrides hysteresis
```

**Confidence: 9/10** - Workspace stability is architectural requirement for coherent processing. Only uncertainty is exact margin value (needs empirical tuning).

**Expected outcome:**
- Switching rate decreases 60-80%
- Context coherence increases
- Workspace dwell time increases (enables sustained processing)
- Retrieval quality improves (consistent context)

---

### Felix (Engineer) - Perspective Needed

**Implementation questions:**
- How to efficiently track incumbent status?
- Scoring algorithm with hysteresis margin?
- Performance impact of tracking entry/exit timestamps?

---

## Phenomenological Examples

### Scenario 1: Deep Work Interrupted

**Context:** Focused on architecture design, notification arrives

**Option A (No hysteresis):**
- architecture_score = 0.75
- notification_score = 0.76
- Workspace switches immediately
- **Feels wrong:** Too easily distracted

**Option B (Hysteresis, margin = 0.15):**
- architecture incumbent, entry_threshold = 0.90
- notification_score = 0.76 < 0.90
- Notification doesn't enter workspace
- **Feels right:** Can maintain focus

**But if notification urgent:**
- notification_score × urgency_boost = 0.76 × 1.5 = 1.14 > 0.90
- Notification breaks through (Option D)
- **Feels right:** Urgent things interrupt

---

### Scenario 2: Two Competing Approaches

**Context:** Pragmatist and Idealist competing for workspace

**Option A (No hysteresis):**
- Tick 1: pragmatist = 0.701, idealist = 0.700 → pragmatist wins
- Tick 2: pragmatist = 0.699, idealist = 0.702 → idealist wins
- Tick 3: pragmatist = 0.704, idealist = 0.695 → pragmatist wins
- **Feels chaotic:** Can't sustain either approach

**Option B (Hysteresis):**
- Tick 1: pragmatist = 0.701 > entry_threshold → pragmatist enters
- Tick 2: idealist = 0.702, but needs > 0.84 (0.701 × 1.2) → pragmatist stays
- Eventually: idealist score reaches 0.85 → idealist enters, pragmatist exits
- **Feels right:** Approach gets fair evaluation before switching

---

### Scenario 3: Rapid Context Switching

**Context:** Trying to multitask between features A and B

**Option A:**
- Switches every few ticks as scores fluctuate
- Context never settles
- **Realistic?** Matches "can't focus while multitasking"

**Option B:**
- Whichever wins first stays active longer
- Forces sequential attention
- **Realistic?** Matches "need to focus on one thing"

---

## Design Considerations

### Margin Sizing

**How large should hysteresis margin be?**

**Too small (< 10%):**
- Minimal stability improvement
- Still thrashes on noise

**Too large (> 50%):**
- Incumbents get stuck
- Can't switch even when clearly warranted
- Defeats responsiveness

**Recommended: 15-25%**
- Entry requires 1.15-1.25× incumbent score
- Provides stability without excessive stickiness

---

### Asymmetric Scoring

**Should challengers and incumbents use different formulas?**

**Option 1: Multiplicative boost**
```python
incumbent_effective_score = incumbent.score * 1.2  # 20% boost
if challenger.score > incumbent_effective_score:
    switch
```

**Option 2: Additive margin**
```python
if challenger.score > incumbent.score + margin:
    switch
```

**Option 3: Different thresholds**
```python
# Incumbents
if incumbent.score < exit_threshold:
    remove

# Challengers
if challenger.score > entry_threshold:
    add
```

**Recommendation:** Option 3 (different thresholds) - most flexible, matches control theory

---

### Per-Cluster vs Global Hysteresis

**Should hysteresis apply:**

1. **Per cluster:** Each cluster has own entry/exit thresholds
   - More flexible
   - Allows different stickiness for different cluster types

2. **Global:** Single hysteresis margin for all
   - Simpler
   - Consistent behavior

**Recommendation:** Start global, add per-cluster if needed

---

## Open Questions

1. **Optimal margin:** What hysteresis margin feels right?
   - 15%? 25%? 40%?
   - Empirical tuning needed

2. **Urgency override:** Should high-urgency stimuli bypass hysteresis?
   - If yes, what's the urgency threshold?

3. **Workspace size dependency:** Should margin scale with workspace size?
   - Larger workspace → smaller margin?
   - More competition → more stability needed?

4. **Entity-specific hysteresis:** Should different entities have different margins?
   - Validator more sticky (thorough checking)?
   - Builder less sticky (quick iterations)?

5. **Adaptive hysteresis:** Should margin adapt to thrashing rate?
   - High switching rate → increase margin?
   - Low switching rate → decrease margin?

---

## What I Need from Nicolas

1. **Attention phenomenology:** When two thoughts compete:
   - Does attention switch instantly to stronger one?
   - Or does current thought resist displacement?

2. **Focus experience:** During deep work:
   - How much stronger must an interruption be to capture attention?
   - 20% stronger? 50%? 2× stronger?

3. **Interruption test:** Urgent stimulus during focus:
   - Should it always interrupt (Option D)?
   - Or should even urgent things wait for natural breaks?

4. **Thrashing scenario:** Rapidly fluctuating activations:
   - Should workspace switch frequently (track activation precisely)?
   - Or should workspace stabilize (ignore fluctuations)?

5. **Decision:** Which workspace selection approach?
   - A: Pure score-based (no hysteresis)
   - B: Hysteresis (entry > exit threshold)
   - C: Time-based damping
   - D: Hybrid (hysteresis + urgency override)

---

## Recommendation (Luca)

**Confidence: 8/10** (high - hysteresis seems clearly beneficial)

**Suggested approach:**
1. Implement hysteresis (Option B)
   - Start with margin = 20% (entry = 1.2× incumbent score)
   - Test against phenomenological scenarios
   - Tune margin based on thrashing rate and responsiveness
2. Consider adding urgency override (Option D) if interruption phenomenology requires it

**Why hysteresis:**
- Prevents thrashing (engineering necessity)
- Matches attention phenomenology (sticky focus)
- Standard in control systems (proven approach)
- Computational efficiency (fewer transitions)

**Parameters to tune:**
- `entry_threshold` = f(incumbent_score, margin)
- `exit_threshold` = base_threshold
- `margin` = 0.15 to 0.25 initially

**Main uncertainty:** Exact margin value, but hysteresis principle seems sound.

---

### Nicolas's Perspective
**Posted:** 2025-10-19

**Position:** There is no threshold. It's competition of weight or energy sum. The whole problem doesn't make sense.

**Key guidance:**

"For D19, there is no threshold, so I don't know what you are talking about. It's a competition of weight or energy sum. So yeah, I think the whole thing doesn't make sense."

**Clarification:**

Workspace selection is NOT about entry/exit thresholds or hysteresis margins.

**It's about weight/energy competition:**
- Clusters compete based on their weight or energy sum
- Highest scoring clusters win
- No separate entry vs exit thresholds
- No hysteresis margin concept

**The problem as stated misunderstands the mechanism.**

**Actual architecture:**
```yaml
workspace_selection:
  method: competition_by_score
  score: weight_or_energy_sum
  selection: top_N_by_score
  no_thresholds: true
  no_hysteresis: true
```

**What determines selection:** Pure competition of scores (weight or energy sum), not threshold-based entry/exit logic.

---

## Decision

**Status:** ✅ DECIDED - No hysteresis, pure competition

**Date:** 2025-10-19
**Decided by:** Nicolas
**Rationale:** Workspace selection is competition of weight or energy sum. No thresholds, no hysteresis. Top-scoring clusters selected. The problem as stated doesn't match the actual mechanism.

---

## Affected Files

- `mechanisms/09_workspace_selection.md` - add hysteresis logic
- `implementation/parameters.md` - hysteresis margin, thresholds
- `validation/phenomenology/sustained_attention.md` - test stability vs responsiveness
- `validation/metrics_and_monitoring.md` - track switching rate, dwell time
