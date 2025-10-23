---
title: Incomplete Node Healing (Eligibility + Tasking)
status: stable
owner: @felix
last_updated: 2025-10-22
supersedes:
  - learning_and_trace/18_incomplete_node_healing.md
depends_on:
  - core/models.md
  - adapters/storage/extraction.py
  - workers/maintenance.py
---

# Incomplete Node Healing (Eligibility + Tasking)

## 1) Context — Problem we’re solving
LLMs and importers often create **schema‑incomplete** nodes/links. We want to **allow creation** (don’t block thinking) yet **prevent contamination** of traversal/WM until required fields are present. The fix should be **bottom‑up**: detect → task → complete → admit.

## 2) Mechanism — What it is
A node/link with missing **required fields** is marked **incomplete** and **ineligible** for traversal/WM selection. A **task** is created to complete it; upon completion, eligibility is re‑evaluated.

**Key idea:** *Eligibility is a read‑time filter, not a second energy channel.* Single‑energy `Eᵢ` remains the physics; eligibility gates **selection**. :contentReference[oaicite:6]{index=6}

### 2.1 Eligibility predicate (nodes)
```

eligible(i) := is_complete(i) ∧ status∈{active} ∧ E_i ≥ Θ_i

```
- `is_complete`: all required fields per type present;  
- `status`: not deleted/archived;  
- `E_i ≥ Θ_i`: standard activation check (global thresholds).

### 2.2 Tasks
On creation or validation failure: emit `task.create{type=complete_node, missing[], target_id}` and store in an organizational task list (N2). The task **references** the object (`graph:id`) and carries **timestamp** for temporal context queries (±Δt neighbors). :contentReference[oaicite:7]{index=7}

### 2.3 Completion strategies
- **Context inference** (neighbors, type exemplars),  
- **LLM fill** with guardrails,  
- **Defaults** from schema.  
All updates log `completion.source` and confidence.

## 3) Why this makes sense

### Phenomenology
You can keep going—stubs are visible but **greyed** and ignored by selection—then they “click into place” once completed.

### Bio‑inspiration
Perception routinely suppresses low‑fidelity signals until enough evidence arrives.

### Systems‑dynamics
Eligibility is **orthogonal** to E/ρ dynamics; we don’t pollute control loops with data quality.

## 4) Expected behaviors
- Incomplete objects appear in viz (dashed/grey), never enter WM or stride selection.  
- After task completion, the same stimulus can now recruit through the completed node.

## 5) Why this vs alternatives
| Alternative | Issue | This mechanism |
|---|---|---|
| Block creation | Loses serendipity | Allow; fix later |
| Auto‑delete | Data loss | Keep stub + task |
| Per‑entity energy gates | Violates single‑energy | Read‑time **eligibility** gate |

## 6) Observability — How & what to measure
**Events:** `node.incomplete`, `link.incomplete`, `task.create`, `task.resolve`, `eligibility.update`.  
**Metrics:** backlog (#incomplete by type/scope), **median time‑to‑complete**, %auto‑completed by strategy, eligibility hit/miss rate in selectors.  
**Dashboards:** Per‑type missing‑field heatmaps; time‑bounded context panes (±5 min) used by completion.

## 7) Failure modes & guards
| Risk | Why bad | Guard |
|---|---|---|
| Stubs accumulate | Cognitive clutter | Owner quotas; backlog alerts |
| Wrong auto‑fill | Inaccurate graph | Confidence thresholds; human review loop |
| Hidden blockers | Non‑transparent | Grey styling + tooltips + task surfaces |

## 8) Integration in code
- **Where**: `libs/trace_parser.py` (surface validation), `workers/trace_ingest.py` (create tasks), `adapters/storage/extraction.py` (eligibility materialization), selectors in `mechanisms/sub_entity_traversal.py` read `eligible(i)`.  
- **Config**: `INCOMPLETE_TRAVERSABLE=False` in `core/settings.py`.

## 9) Success criteria
- >90% of incomplete objects completed within SLA; zero selection of incomplete nodes; clear operator visibility.

## 10) Open questions / future
- Autonomy for completion agents; schema evolution re‑validation; collaborative tasks in N2 with cross‑graph references. :contentReference[oaicite:8]{index=8}
```

### B. Changes made

* Replaced **per‑subentity energy gating** with **single eligibility predicate** over `Eᵢ` + completeness. 
* Clarified task creation & temporal context retrieval; added observability events.

### C. Compliance matrix

| Principle                                           | Status  |
| --------------------------------------------------- | ------- |
| Single‑energy; links store no activation            | **OK**  |
| Two‑scale traversal; selection gated by eligibility | **OK**  |
| Stimuli vs TRACE separation                         | **N/A** |

---

## 3) `learning_and_trace/link_strengthening.md` — **Link Strengthening (Traversal‑Driven, Single‑Energy)**

> Source baseline: “Link Strengthening” (diffusion‑time updates; per‑subentity energies; “only when both nodes are inactive”). 

```markdown
---
title: Link Strengthening (Traversal‑Driven, Single‑Energy)
status: stable
owner: @felix
last_updated: 2025-10-22
supersedes:
  - learning_and_trace/09_link_strengthening.md
depends_on:
  - foundations/diffusion.md
  - learning_and_trace/trace_weight_learning.md
  - runtime_engine/traversal_v2.md
---

# Link Strengthening (Traversal‑Driven, Single‑Energy)

## 1) Context — Problem we’re solving
We need paths that **work** to become easier to recruit next time—without hand‑tuned constants, without per‑entity state, and while playing nicely with **ρ‑control** and **WM**. The strengthening must be **evidence‑driven** and low‑variance.

## 2) Mechanism — What it is
Links strengthen from **observed usefulness during executed strides**, not from raw presence of energy. Stride events carry attribution; we form **EMAs** and update `log_weight_ij` in small steps.

**2.1 Per‑stride attribution**
For each executed `stride.exec{i→j}`:
- Record **ΔE** moved, **latency**, **res/comp multipliers** (if affect gates used), and a **gap‑closure score** `φ_ij` (did this stride help a pending goal, threshold crossing, or WM stabilization?).  
- Maintain `ema_flow_ij` and `ema_φ_ij`.

**2.2 Convert to standardized signal**
Within **link type+scope** cohorts:
```

z_φ(ij) = rank_z(ema_φ_ij, cohort)
z_flow(ij) = rank_z(ema_flow_ij, cohort)   # optional shaping

```

**2.3 Weight update (traversal channel)**
```

Δ log_weight_ij (traversal) = η_t · ( z_φ(ij) + κ · z_flow(ij) )

```
Small η keeps stability; κ is modest (flow without usefulness earns little).  

**2.4 Fusion with TRACE channel**
Final update adds TRACE z‑scores (`z_rein`, `z_form`) per **TRACE Weight Learning**. Total:
```

Δ log_weight_ij = η_t · (z_φ + κ·z_flow) + η_trace · (z_rein + z_form)

```
No per‑entity energy; single `log_weight_ij`. :contentReference[oaicite:11]{index=11}

## 3) Why this makes sense

### Phenomenology
Frequently helpful routes begin to feel **automatic**—ideas jump along them with less effort.

### Bio‑inspiration
Hebbian/credit‑assignment: connections that **contribute to success** are potentiated.

### Systems‑dynamics
Evidence‑normalized z‑scores avoid constant tuning; small steps preserve stability under ρ‑control.

## 4) Expected behaviors
- Formation of **“highways”** where φ stays high;  
- Pruning pressure on noisy edges (low z‑φ);  
- Faster context reconstruction along practiced routes. :contentReference[oaicite:12]{index=12}

## 5) Why this vs alternatives
| Alternative | Issue | This mechanism |
|---|---|---|
| Strengthen on any flow | Rewards noise | φ‑based usefulness only |
| Per‑entity link weights | State blow‑up; unclear physics | Single weight per link |
| Manual constants | Fragile | Rank‑z within cohorts |

## 6) Observability — How & what to measure
**Events:** sampled `stride.exec{ΔE,φ,res_mult,comp_mult}`, periodic `weights.updated.traversal{Δμ,Δσ by cohort}`.  
**Metrics:** distribution of z‑φ by type; **highway coverage** (fraction of traffic on top‑q links); **latency to threshold** improvements.  
**Dashboards:** weight evolution spark‑lines; φ heatmaps; before/after **context reconstruction** latency. :contentReference[oaicite:13]{index=13}

## 7) Failure modes & guards
| Risk | Why bad | Guard |
|---|---|---|
| Runaway growth | Over‑potentiation | η caps; read‑time standardization; slow **weight** decay (separate from energy) |
| Credit misassignment | Noisy φ | Eligibility traces (short horizon); cap single‑event impact |
| Starvation of novel paths | Exploitation bias | ε‑explore in selector; novelty bonus with decay |

## 8) Integration in code
- **Where**: `mechanisms/consciousness_engine_v2.py` (tick loop emits φ), `mechanisms/sub_entity_traversal.py` (selector → strides), `learning_and_trace/*` (EMA maintenance + updates).  
- **Storage**: persist `log_weight_ij`; maintain rolling baselines for read‑time standardization. :contentReference[oaicite:14]{index=14}

## 9) Success criteria
- Monotonic improvement in **reconstruction latency**; stable ρ; no weight inflation.

## 10) Open questions / future
- Better φ definitions per task family; multi‑step attribution; path‑level credit under constraints.
```

### B. Changes made

* Removed **per‑subentity** energy references and “inactive‑only strengthening”; moved to **φ‑based** usefulness on **executed strides**. 
* Integrated with **TRACE** channel formally; added cohort‑z standardization path. 

### C. Compliance matrix

| Principle                               | Status |
| --------------------------------------- | ------ |
| Single‑energy; links hold no activation | **OK** |
| Evidence‑normalized learning            | **OK** |
| Two‑scale traversal preserved           | **OK** |
