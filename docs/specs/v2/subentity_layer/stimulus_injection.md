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
- **Health & pacing:** don’t overdrive a supercritical graph; revive a subcritical one.
- **Attribution:** show *where* energy went and *why*.
- **Entity-aware routing:** leverage subentities, not just raw nodes. :contentReference[oaicite:34]{index=34}

## 2. Mechanism (Design)

### 2.1 Retrieval & budget pipeline

1) **Entropy-coverage search**: adapt #matches to stimulus specificity; broader text → more matches to cover semantics; narrower → fewer, higher-precision.
2) **Gap mass**: estimate useful work via \(\sum \text{sim}(s,i) \cdot \max(0,\Theta_i - E_i)\).
3) **Floor-biased injection (dual-channel)**: Split budget into floor channel (prioritizes under-active nodes) and amplifier channel (boosts strong matches even above threshold). **Critical: threshold is activation floor, not hard cap. Energy propagation requires nodes going above threshold.**
4) **Health modulation \(f(\rho)\)**: damp when the system is crowded/unstable; boost when sparse.
5) **Source impact gate \(g(\text{source})\)**: learn per-source yields and reweight budgets.
6) **Peripheral amplification**: increase budget if stimulus aligns with persistent peripheral context.
7) **Direction-aware link injection**: if the match is a link, split energy to endpoints using learned directional priors.
8) **Subentity channeling**: split budget across active entities by affinity × recent success.
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
- **Injection:** \(\Delta E_i^\text{amp} = \hat{w}_i^\text{amp} \cdot B_\text{amp}\)
- **No cap at threshold** (this is critical - allows momentum above floor)

**Total Injection:**
\[
\Delta E_i = \min\left(\Delta E_i^\text{floor} + \Delta E_i^\text{amp}, \Delta E_\text{max}\right)
\]

where \(\Delta E_\text{max}\) is per-node safety cap (typically 10 on 0-100 scale), and final total is re-normalized if \(\sum_i \Delta E_i > B\).

**Parameters:**
- \(\lambda = 0.6\) (floor/amplifier split)
- \(k = 8\) (sigmoid steepness for floor bias)
- \(\gamma = 1.3\) (amplifier exponent)
- \(\Delta E_\text{max} = 10\) (per-node cap)
- \(\Theta_i = 30\) (default threshold for 0-100 scale; type-specific later)

**Safety:** Enforced globally via budget \(B\), per-node cap \(\Delta E_\text{max}\), health modulation \(f(\rho)\), and criticality gates. **NOT enforced locally by capping at threshold** - that would prevent propagation.

**Rationale:** Nodes at \(E_i = 61\) with \(\Theta_i = 30\) still receive amplifier boost if similarity is high. This allows momentum and spreading activation. Under-active nodes (\(E_i < \Theta_i\)) get floor help + amplifier boost. Safety comes from global constraints, not local caps.

### 2.2 Directional priors for link-matched injection

For a matched link \(i \rightarrow j\), split \(\Delta E\) to source/target via a Beta prior over forward/backward precedence (bootstrap symmetric; learn from boundary/stride evidence later). :contentReference[oaicite:36]{index=36}

### 2.3 Subentity channels

Compute entity **affinity** (embedding similarity) and **recent success** (share of flips & gap-closure), rank-normalize, softmax to proportions, then allocate budget per-entity before distributing to members. :contentReference[oaicite:37]{index=37}

## 3. Why it makes sense

### 3.1 Phenomenology

Stimulus “feels” like half of reality—an urgency injection that clarifies direction and speeds time; the mechanism accelerates ticks, injects energy near relevant neighborhoods, and yields immediate **entity flips** when warranted. :contentReference[oaicite:38]{index=38}

### 3.2 Human bio-inspiration

Salience gating and arousal systems up-regulate processing when something important happens; here, **health modulation** and **source gates** act as learned control surfaces.

### 3.3 Systems dynamics

- Respects **single-energy** at nodes; no side-channels.  
- Plays well with **tick-speed regulation** (first tick after injection; subsequent ticks paced by stimulus cadence). :contentReference[oaicite:39]{index=39}  
- Keeps diffusion stride-based (we inject; traversal moves quanta).  
- Works with **entity-first WM** by pre-biasing neighborhoods that are likely to matter. :contentReference[oaicite:40]{index=40}

## 4. Expected resulting behaviors

- **Immediate relevance:** near-instant flips in strongly matched entities.  
- **Stable pacing:** fewer runaways under supercritical conditions; better revival from dormancy.  
- **Transparent attribution:** viz shows where energy went, by reason (health, source, peripheral). :contentReference[oaicite:41]{index=41}

## 5. Why this over alternatives

- **Vs fixed K & naive top-k:** entropy-aware coverage matches user intent and prevents mode-collapse. :contentReference[oaicite:42]{index=42}  
- **Vs constant budgets:** health/source gates make injection adaptive and data-driven. :contentReference[oaicite:43]{index=43}  
- **Vs node-only routing:** entity channels capture neighborhood-level coherence from the outset. :contentReference[oaicite:44]{index=44}

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

- **Mechanism:** `mechanisms/stimulus_injection.py` (health gate, source gate, peripheral amp, entity channels, link priors). :contentReference[oaicite:52]{index=52}  
- **Runtime:** first-class tick on new stimulus; pacing by `tick_speed`. :contentReference[oaicite:53]{index=53}  
- **Viz:** events through the WS contract + snapshot merge. :contentReference[oaicite:54]{index=54}

## 9. What success looks like

- At equal budgets, **flip yield** increases and waste (overshoot vs gap) decreases.  
- Viz dashboards show clear budget attributions and **entity-first** activation patterns. :contentReference[oaicite:55]{index=55}

## 10. Open questions & future improvements

- Learn **source gates** faster with per-scope cohorts. :contentReference[oaicite:56]{index=56}  
- Calibrate **peripheral amplification** with longer windows and decay. :contentReference[oaicite:57]{index=57}  
- Introduce **refractory windows** to avoid re-injecting into just-flipped items. :contentReference[oaicite:58]{index=58}
