---
title: TRACE Reinforcement (Zero‑Constant Cohort Allocation)
status: stable
owner: @felix
last_updated: 2025-10-22
supersedes:
  - learning_and_trace/trace_reinforcement_specification.md
depends_on:
  - learning_and_trace/trace_weight_learning.md
---

# TRACE Reinforcement (Zero‑Constant Cohort Allocation)

## 1) Context — Problem we’re solving
We need a principled way to turn reflective judgments in **TRACE** (useful / misleading; formation quality) into **weight updates** without magic constants, while keeping physics clean (TRACE changes **weights**, not activation). :contentReference[oaicite:18]{index=18}

## 2) Mechanism — What it is
**Two signals** from TRACE text:  
1) **Reinforcement marks** → integer “seats” via **Hamilton apportionment** in separate positive/negative pools within the **TRACE cohort**.  
2) **Formation quality** → **C×E×N** (Completeness × Evidence × Novelty) geometric mean per formation cohort.

Parser emits structured signals; the **weight pipeline** converts them to **EMAs** and **cohort z‑scores** and applies to `log_weight`. See `trace_weight_learning.md`. :contentReference[oaicite:19]{index=19}

### 2.1) Context-Aware Scope (Where Reinforcement Applies)

**Problem:** Global reinforcement (apply useful/useless to ALL memberships of a node) loses context. A node may be useful in one entity context but useless in another.

**Solution:** Apply TRACE marks **primarily to entity memberships active at marking time**, with a **small global bump**.

**Formula:**

When marking node `i` as "useful" (or "useless"):

```python
# Primary reinforcement: Active entity contexts
for entity_id in active_entities_at_mark_time:
    apply_trace_update(
        node=i,
        entity=entity_id,
        seats=allocated_seats,
        weight=0.8  # 80% of signal to active contexts
    )

# Secondary reinforcement: Global bump
apply_trace_update(
    node=i,
    entity=None,  # All memberships
    seats=allocated_seats,
    weight=0.2  # 20% of signal globally
)
```

**Split rationale:**
- **Local (80%)**: Learn WHERE a node is useful (which entity, which task)
- **Global (20%)**: Some nodes are universally useful/useless

**Example:**

```
Marking "schema validation" as "very useful" during architecture work:
- Active entities: ["luca", "ada"]
- Active tasks: ["substrate_design"]

Result:
- Luca membership: +0.8 × seats (strong boost)
- Ada membership: +0.8 × seats (strong boost)
- Other memberships: +0.2 × seats (small global bump)

Effect:
"schema validation" becomes more retrievable for Luca/Ada in substrate contexts,
slightly more retrievable globally, but NOT boosted for unrelated entities.
```

**Observability:**

```json
{
    "event": "weights.updated.trace",
    "node_id": "schema_validation",
    "mark": "very useful",
    "seats": 3,
    "attribution": {
        "active_entities": ["luca", "ada"],
        "active_tasks": ["substrate_design"],
        "local_weight": 0.8,
        "global_weight": 0.2
    },
    "updates": [
        {"entity": "luca", "delta_log_w": 0.0024},
        {"entity": "ada", "delta_log_w": 0.0024},
        {"entity": "global", "delta_log_w": 0.0006}
    ]
}
```

**Guards:**
- **Require active entities**: If no entities active at mark time, apply 100% globally (fallback)
- **Cap per-entity updates**: Prevent single mark from dominating entity-specific weights
- **Track context overlap**: Measure how often marks occur in same contexts (validates context learning)

## 3) Why this makes sense
- **Zero constants**: seat budgets equal what the author marked; category strengths are **learned** from outcomes.  
- **Anti‑gaming**: overused labels self‑normalize.  
- **Balanced formation scoring**: geometric mean requires all three axes.

## 4) Expected behaviors
- Dense analytic TRACEs yield proportionally more signal; throwaway TRACEs yield little—**correct** phenomenology.  
- High‑quality formations get a **head‑start**; weak ones don’t.

## 5) Why this vs alternatives
| Alt | Issue | This |
|---|---|---|
| Fixed label weights | Tunables drift | Hamilton seats per TRACE |
| Additive quality | Gaming one axis | C×E×N geometric mean |
| Global normalization | Domain shift | Cohort‑local ranks |

## 6) Observability — How & what
**Events:** `trace.parsed{pool sizes, seats}`, `weights.updated.trace{cohorts, Δμ}`.  
**Diagnostics:** per‑TRACE seat tables, formation component breakdowns.

## 7) Failure modes & guards
| Risk | Guard |
|---|---|
| Small cohorts (N<3) | Fallback ranks; widen cohort |
| Label drift | Weekly strength re‑estimation |
| Seat outliers | Winsorize remainders; cap per‑TRACE impact |

## 8) Integration in code
- **Parser**: extracts marks/blocks → emits signals.  
- **Learner**: updates `ema_trace_seats` & `ema_formation_quality`, computes cohort z‑scores, calls `apply_trace_weight_updates()`. :contentReference[oaicite:20]{index=20}

## 9) Success criteria
- Seat distributions track TRACE density; stable weight baselines; explainable updates (audit panes).

## 10) Open questions
- Per‑author dampening; confidence weighting; temporal decay of old TRACEs.