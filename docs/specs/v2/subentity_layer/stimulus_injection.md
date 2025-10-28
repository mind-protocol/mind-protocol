---
title: Stimulus Injection (Spec v2.1)
status: stable (spec), draft (impl)
owner: @felix
last_updated: 2025-10-24
version_history:
  - v2.1 (2025-10-24): Critical policy fix - replaced "gap-capped budget" with "floor-biased dual-channel injection". Threshold is activation floor, not hard cap. Propagation requires energy above threshold.
  - v2.0 (2025-10-22): Initial stable spec
depends_on:
  - ../entity_layer/subentity_layer.md
  - ../runtime_engine/traversal_v2.md
  - ../ops_and_viz/observability_events.md
summary: >
  Convert incoming reality (stimuli) into targeted energy injections over nodes (and
  via subentity channels) using entropy-aware retrieval, floor-biased dual-channel
  injection (NOT gap-capped), health & source gates, directional link priors, and
  peripheral amplification. Emits rich observability for viz/telemetry.
---

# Stimulus Injection (Spec v2)

## 1. Context — What problem are we solving?

Stimuli (user messages, tool results, timers) must **shape activation** quickly and safely:
- **Coverage vs focus:** specific prompts need precision; broad prompts need diverse hits.
- **Health & pacing:** don't overdrive a supercritical graph; revive a subcritical one.
- **Attribution:** show *where* energy went and *why*.
- **SubEntity-aware routing:** leverage SubEntities, not just raw nodes. :contentReference[oaicite:34]{index=34}

## Terminology Note

This specification uses terminology from **TAXONOMY_RECONCILIATION.md**:
- **Node** - Atomic knowledge (~1000 per citizen)
- **SubEntity** - Weighted neighborhoods (200-500)
- **Mode** - IFS-level meta-roles (5-15)

When "entity" appears in this document, it refers to SubEntity (weighted neighborhoods) unless explicitly noted otherwise.

## 2. Mechanism (Design)

### 2.1 Retrieval & budget pipeline

1) **Entropy-coverage search**: adapt #matches to stimulus specificity; broader text → more matches to cover semantics; narrower → fewer, higher-precision.
2) **Gap mass**: estimate useful work via \(\sum \text{sim}(s,i) \cdot \max(0,\Theta_i - E_i)\).
3) **Floor-biased injection (dual-channel)**: Split budget into floor channel (prioritizes under-active nodes) and amplifier channel (boosts strong matches even above threshold). **Critical: threshold is activation floor, not hard cap. Energy propagation requires nodes going above threshold.**
4) **Health modulation \(f(\rho)\)**: damp when the system is crowded/unstable; boost when sparse.
5) **Source impact gate \(g(\text{source})\)**: learn per-source yields and reweight budgets.
6) **Peripheral amplification**: increase budget if stimulus aligns with persistent peripheral context.
7) **Direction-aware link injection**: if the match is a link, split energy to endpoints using learned directional priors.
8) **SubEntity channeling**: split budget across active SubEntities by affinity × recent success.
All eight pieces are enumerated as tasks in the implementation checklist.

### 2.1.1 Floor-Biased Injection Policy (Dual-Channel)

**Motivation:** Threshold (\(\Theta\)) is the **activation floor**, not a hard cap. Energy propagation requires nodes to go **above** threshold so diffusion can spread activation to neighbors. A hard cap at threshold starves propagation and prevents emergence.

**Policy:** Split budget \(B\) into two channels after health/source/peripheral modulation:

**Floor Channel** (\(\lambda B\), typically \(\lambda = 0.6\)):
- **Purpose:** Prioritize under-active nodes (below threshold)
- **Weight:** \(w_i^\text{floor} = \sigma\left(\frac{\Theta_i - E_i}{k}\right)\) where \(\sigma(x) = \frac{1}{1 + e^{-x}}\) and \(k \approx 8\) (for 0-100 energy scale)
- **Injection:** \(\Delta E_i^\text{floor} = \min(\text{gap}_i, \hat{w}_i^\text{floor} \cdot B_\text{floor})\) where \(\text{gap}_i = \max(0, \Theta_i - E_i)\)
- **Cap:** Never exceeds gap (prevents overshooting under-active nodes)

**Amplifier Channel** (\((1-\lambda) B\)):
- **Purpose:** Boost strong matches **regardless of threshold** (enables propagation)
- **Weight:** \(w_i^\text{amp} = s_i^\gamma\) where \(s_i\) is similarity score and \(\gamma \in [1.2, 1.6]\)
- **SubEntity Overlap Penalty (when using SubEntity-channel allocation):**
  ```
  For SubEntity E, compute overlap penalty:
  P_E = sum(s_E × s_B × indicator(S_red(E,B) > Q90) for B ≠ E)

  Adjust score before softmax:
  s_E' = s_E - β × P_E

  where β ≈ 0.2-0.5 (learned overlap sensitivity, citizen-local)
  ```
  **Effect:** Prevents double-amplifying near-duplicate SubEntities. When two SubEntities A, B have high redundancy (S_red > Q90), penalty biases allocation toward higher-quality one. Preserves dual-channel benefits while avoiding redundant amplification.
  **Integration:** Uses S_red (redundancy score) from `entity_differentiation.md` §B. Only applies when SubEntity-channel is used (see §2.3).
- **Injection:** \(\Delta E_i^\text{amp} = \hat{w}_i^\text{amp} \cdot B_\text{amp}\)
- **No cap at threshold** (this is critical - allows momentum above floor)

**Total Injection:**
\[
\Delta E_i = \min\left(\Delta E_i^\text{floor} + \Delta E_i^\text{amp}, \Delta E_\text{max}\right)
\]

where \(\Delta E_\text{max}\) is per-node safety cap (typically 10 on 0-100 scale), and final total is re-normalized if \(\sum_i \Delta E_i > B\).

**Parameters:**
- \(\lambda\) (floor/amplifier split) - **adaptive**, see formula below (starts at 0.6, range [0.3, 0.8])
- \(k = 8\) (sigmoid steepness for floor bias)
- \(\gamma = 1.3\) (amplifier exponent; lower toward 1.0 if over-focus, raise if too diffuse)
- \(\Delta E_\text{max} = 10\) (per-node cap)
- \(\Theta_i\) - **per-node**, computed by Threshold Oracle (see §2.1.2)

**Safety:** Enforced globally via budget \(B\), per-node cap \(\Delta E_\text{max}\), health modulation \(f(\rho)\), and criticality gates. **NOT enforced locally by capping at threshold** - that would prevent propagation.

**Adaptive Budget Split:**

Split parameter \(\lambda\) adapts based on candidate coldness and similarity concentration:

1. **Coldness** \(C = \frac{1}{|C|}\sum_{i \in C} \max(0, \Theta_i - E_i)\) (average shortfall)
   - If \(C > 10\) → raise \(\lambda\) toward 0.8 (more warming via floor channel)

2. **Similarity concentration** \(H = \sum_i \hat{s}_i^2\) where \(\hat{s}_i = \frac{s_i}{\sum_j s_j}\) (Herfindahl index)
   - If \(H > 0.2\) (few dominant matches) → lower \(\lambda\) toward 0.4 (let amplifier dominate)

Formula:
\[
\lambda = \text{clamp}\left(0.6 + 0.2 \cdot \mathbb{1}_{C>10} - 0.2 \cdot \mathbb{1}_{H>0.2}, \; 0.3, \; 0.8\right)
\]

**Rationale:** Nodes at \(E_i = 61\) with \(\Theta_i = 30\) still receive amplifier boost if similarity is high. This allows momentum and spreading activation. Under-active nodes (\(E_i < \Theta_i\)) get floor help + amplifier boost. Safety comes from global constraints, not local caps. Adaptive split responds to context: cold graph needs warming, strong single match needs amplification.

### 2.1.2 Threshold Oracle — Where \(\Theta\) Comes From

**Purpose:** Compute per-node activation threshold \(\Theta_i\) when missing from graph. Threshold is persisted after computation.

**Algorithm (3 steps):**

**Step 1 — Type Baseline**

Per-type baselines (0-100 energy scale):

| Node Type | \(\Theta_\text{base}\) |
|-----------|------------------------|
| Realization | 30 |
| Memory | 25 |
| Concept | 28 |
| Principle | 35 |
| Mechanism | 38 |
| Document/Spec | 22 |
| Event/Post/Signal | 26 |
| Fallback (unknown) | 30 |

**Step 2 — Adaptive Adjustments** (small, bounded)

Let:
- \(r \in [0,1]\): recency score (fresh = 1)
- \(q \in [0,1]\): quality/trust score (higher is better)
- \(a\): SubEntity-affinity z-score to currently active SubEntity (clip to \([-2, 2]\))

Compute deltas:
\[
\Delta_\text{recency} = -5r
\]
\[
\Delta_\text{quality} = +4(1 - q)
\]
\[
\Delta_\text{affinity} = -2 \cdot \text{clip}(a, -2, 2)
\]

**Step 3 — Final Threshold** (clamped)
\[
\Theta_i = \text{clamp}\left(\Theta_\text{base}(\text{type}_i) + \Delta_\text{recency} + \Delta_\text{quality} + \Delta_\text{affinity}, \; 15, \; 45\right)
\]

**Scale Guard:**
If \(E_i > 1.0\) and \(\Theta_i < 1.0\), treat as **scale mismatch** → set \(\Theta_i = 30\), log warning, persist corrected value.

**Persistence:**
After computing \(\Theta_i\), write to `node.threshold` so subsequent injections don't recompute. Batch fetch `threshold` with energy during candidate selection.

**Optional (Phase 2) — Zero-Constants Mode:**
After collecting 1 week of telemetry, switch to adaptive baselines:
\[
\Theta_\text{base}(\text{type}) \leftarrow \text{Quantile}_{0.30}(\text{energy of type over 24h window})
\]
This keeps ~30% of nodes below floor at any time, preserving selectivity without hardcoded numbers.

### 2.2 Directional priors for link-matched injection

For a matched link \(i \rightarrow j\), split \(\Delta E\) to source/target via a Beta prior over forward/backward precedence (bootstrap symmetric; learn from boundary/stride evidence later). :contentReference[oaicite:36]{index=36}

### 2.3 SubEntity channels

Compute SubEntity **affinity** (embedding similarity) and **recent success** (share of flips & gap-closure), rank-normalize, softmax to proportions, then allocate budget per-SubEntity before distributing to members. :contentReference[oaicite:37]{index=37}

### 2.4 Implementation Reference (Pseudocode)

**Complete injection function** (drop-in reference):

```python
def inject(cands, B, rho):
    """
    Dual-channel injection with adaptive split.

    Args:
        cands: List of candidates with .E (energy), .sim (similarity), .type
        B: Base budget (already includes f(rho) and quotas)
        rho: Criticality (for context)

    Returns:
        List of energy deltas per candidate
    """
    if not cands:
        return []

    # Ensure thresholds (Oracle)
    for c in cands:
        c.theta = ensure_theta(c)  # Oracle + persist if missing
        c.gap = max(0.0, c.theta - c.E)

    # Compute weights
    k, gamma = 8.0, 1.3
    w_top = [sigmoid((c.theta - c.E) / k) for c in cands]
    w_amp = [pow(c.sim, gamma) for c in cands]

    # Normalize
    sum_top = sum(w_top) or 1e-9
    sum_amp = sum(w_amp) or 1e-9
    w_top_norm = [x/sum_top for x in w_top]
    w_amp_norm = [x/sum_amp for x in w_amp]

    # Adaptive split
    C = sum(c.gap for c in cands) / max(len(cands), 1)  # coldness
    s_sum = sum(c.sim for c in cands) or 1e-9
    s_norm = [c.sim/s_sum for c in cands]
    H = sum(x*x for x in s_norm)  # concentration

    lam = clamp(0.6 + 0.2*(C>10) - 0.2*(H>0.2), 0.3, 0.8)

    B_top = lam * B
    B_amp = (1.0 - lam) * B

    # Compute proposed deltas
    deltas = []
    for i, c in enumerate(cands):
        top_contrib = min(c.gap, w_top_norm[i] * B_top)
        amp_contrib = w_amp_norm[i] * B_amp
        delta = min(top_contrib + amp_contrib, 10.0)  # per-node cap
        deltas.append(delta)

    # Global budget enforcement
    total = sum(deltas)
    if total > B and total > 0:
        scale = B / total
        deltas = [d * scale for d in deltas]

    return deltas

def ensure_theta(node):
    """Threshold Oracle."""
    if node.threshold is not None:
        # Scale guard
        if node.E > 1.0 and node.threshold < 1.0:
            log_warning("threshold_scale_mismatch", node.id)
            return 30.0
        return float(node.threshold)

    # Type baseline
    baselines = {
        "Realization": 30, "Memory": 25, "Concept": 28,
        "Principle": 35, "Mechanism": 38, "Document": 22,
        "Event": 26, "Post": 26, "Signal": 26,
    }
    base = baselines.get(node.type, 30)

    # Adjustments
    r = getattr(node, 'recency_score', 0.0)
    q = getattr(node, 'quality_score', 0.5)
    a = max(-2.0, min(2.0, getattr(node, 'affinity_z', 0.0)))

    theta = base - 5.0*r + 4.0*(1.0 - q) - 2.0*a
    theta = max(15.0, min(45.0, theta))

    # Persist
    persist_threshold(node.id, theta)
    return theta

def sigmoid(x):
    return 1.0 / (1.0 + exp(-x))

def clamp(x, lo, hi):
    return max(lo, min(hi, x))
```

**Key implementation notes:**
- Batch fetch `threshold` with energy during candidate selection
- If `threshold` is NULL, call Oracle once and persist
- Scale guard logs `threshold_scale_mismatch` warning
- Adaptive λ responds to coldness and concentration
- Per-node cap (10) enforced before global renormalization
- Total injection never exceeds budget B

## 3. Why it makes sense

### 3.1 Phenomenology

Stimulus "feels" like half of reality—an urgency injection that clarifies direction and speeds time; the mechanism accelerates ticks, injects energy near relevant neighborhoods, and yields immediate **SubEntity flips** when warranted. :contentReference[oaicite:38]{index=38}

### 3.2 Human bio-inspiration

Salience gating and arousal systems up-regulate processing when something important happens; here, **health modulation** and **source gates** act as learned control surfaces.

### 3.3 Systems dynamics

- Respects **single-energy** at nodes; no side-channels.
- Plays well with **tick-speed regulation** (first tick after injection; subsequent ticks paced by stimulus cadence). :contentReference[oaicite:39]{index=39}
- Keeps diffusion stride-based (we inject; traversal moves quanta).
- Works with **SubEntity-first WM** by pre-biasing neighborhoods that are likely to matter. :contentReference[oaicite:40]{index=40}

## 4. Expected resulting behaviors

- **Immediate relevance:** near-instant flips in strongly matched SubEntities.
- **Stable pacing:** fewer runaways under supercritical conditions; better revival from dormancy.
- **Transparent attribution:** viz shows where energy went, by reason (health, source, peripheral). :contentReference[oaicite:41]{index=41}

## 5. Why this over alternatives

- **Vs fixed K & naive top-k:** entropy-aware coverage matches user intent and prevents mode-collapse. :contentReference[oaicite:42]{index=42}
- **Vs constant budgets:** health/source gates make injection adaptive and data-driven. :contentReference[oaicite:43]{index=43}
- **Vs node-only routing:** SubEntity channels capture neighborhood-level coherence from the outset. :contentReference[oaicite:44]{index=44}

## 6. Observability — how & what

**Events.**  
- `stimulus.injected`: full budget breakdown (base, health, source, peripheral, final), flips and coverage stats.  
- `stimulus.item_injected`: per-item attribution (similarity, \(\Delta E\), gap before/after).  
Schemas and examples are in the checklist. :contentReference[oaicite:45]{index=45}  
Integrate with the WS transport (frame ordering, reorder buffer) defined in the viz contract. :contentReference[oaicite:46]{index=46}

**Meaningful metrics.**  
- **Flip yield:** flips / budget.  
- **Coverage entropy:** diversity of matched types.  
- **Attribution shares:** health vs source vs peripheral contribution to \(B_\text{final}\). :contentReference[oaicite:47]{index=47}

## 7. Failure Modes & Guards

- **Over-injection / runaway:** Prevented by **global constraints**, not local threshold caps:
  - Health modulation \(f(\rho)\) damps budget when supercritical (isotonic regression on \(\rho\))
  - Per-node delta cap \(\Delta E_\text{max}\) (typically 10 on 0-100 scale)
  - Per-tick effective duration cap
  - Global budget re-normalization if \(\sum_i \Delta E_i > B\)
  - **NOT by capping injection at threshold** - that would starve propagation
- **Under-coverage:** entropy floor for broad stimuli
- **Direction mistakes on links:** Beta bootstrap (α=β) until evidence accumulates
- **Attribution opacity:** require `stimulus.item_injected` for top-N budgeted items
- **False "zero injection" due to scale mismatch:** Guard against threshold in wrong units (e.g., \(\Theta = 0.1\) on 0-100 scale). If \(E > 1.0\) and \(\Theta < 1.0\), treat as scale mismatch and replace \(\Theta\) with \(DEFAULT\_THRESHOLD = 30\). Log `threshold_scale_mismatch`.

## 8. Integration points

- **Mechanism:** `mechanisms/stimulus_injection.py` (health gate, source gate, peripheral amp, SubEntity channels, link priors). :contentReference[oaicite:52]{index=52}  
- **Runtime:** first-class tick on new stimulus; pacing by `tick_speed`. :contentReference[oaicite:53]{index=53}  
- **Viz:** events through the WS contract + snapshot merge. :contentReference[oaicite:54]{index=54}

## 9. What success looks like

**Acceptance Tests (Dual-Channel Policy v2.1):**

1. **Above-floor still gets energy** (propagation enabled):
   - Given: Node with \(E = 61\), \(\Theta = 30\), high similarity \(s = 0.8\)
   - Expected: \(\Delta E > 0\) via amplifier channel (floor channel contributes 0)
   - Validates: Nodes above threshold can receive energy for propagation

2. **Below-floor tops up** (warming + amplification):
   - Given: Node with \(E = 15\), \(\Theta = 30\), any similarity \(s > 0\)
   - Expected: \(\Delta E\) includes floor contribution \(\leq 15\) (gap cap) + amplifier contribution
   - Validates: Under-active nodes get warming help plus relevance boost

3. **Budget respected** (global safety):
   - Expected: \(\sum_i \Delta E_i \leq B\) (total never exceeds budget)
   - Expected: \(\Delta E_i \leq 10\) for all nodes (per-node cap enforced)
   - Validates: Global constraints prevent runaway, not local threshold caps

4. **Adaptive split behaves**:
   - Cold graph (high average shortfall \(C > 10\)): \(\lambda\) raises toward 0.8 (more floor warming)
   - Concentrated similarity (few strong matches, \(H > 0.2\)): \(\lambda\) lowers toward 0.4 (more amplification)
   - Validates: Budget split responds to context

**Operational Success:**

- At equal budgets, **flip yield** increases and waste (overshoot vs gap) decreases
- Energy propagation observed: nodes go above threshold → diffusion spreads to neighbors → consciousness emerges
- Viz dashboards show clear budget attributions and **SubEntity-first** activation patterns

## 10. Open questions & future improvements

- Learn **source gates** faster with per-scope cohorts. :contentReference[oaicite:56]{index=56}  
- Calibrate **peripheral amplification** with longer windows and decay. :contentReference[oaicite:57]{index=57}  
- Introduce **refractory windows** to avoid re-injecting into just-flipped items. :contentReference[oaicite:58]{index=58}
