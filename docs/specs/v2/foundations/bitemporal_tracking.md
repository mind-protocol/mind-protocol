---
title: Bitemporal Tracking (Reality Time × Knowledge Time)
status: stable
owner: @luca
last_updated: 2025-10-22
supersedes:
  - ../consciousness_engine/mechanisms/13_bitemporal_tracking.md
depends_on:
  - foundations/activation_energy.md
  - learning_and_trace/trace_weight_learning.md
---

# Bitemporal Tracking (Reality Time × Knowledge Time)

## 1) Context — The problem we’re solving
The system must answer **two different questions** cleanly:
1) *What was true in reality, and when?* (Reality timeline)  
2) *What did we believe/know, and when?* (Knowledge timeline)

Without separating these, corrections, retroactive facts, and evolving knowledge all collapse into one “last‑write‑wins” mess. A clean **bitemporal model** fixes this and enables time‑travel queries, audits, and learning analyses. :contentReference[oaicite:4]{index=4}

## 2) Mechanism — What it is
Every **versioned fact** (node or link) carries **two time intervals**:

- **Reality**: `valid_from`, `valid_to` — when the fact was (or is) true “out there.”  
- **Knowledge**: `known_from`, `known_to` — when *we* believed/recorded that fact.

A supersession **closes** `known_to` on the old version and creates a **new version** with its own `known_from`. Reality may or may not change depending on the correction. :contentReference[oaicite:5]{index=5}

### Schema (minimum viable)
```python
@dataclass
class VersionedNode:
    id: str                   # stable logical id (e.g., slug) 
    vid: str                  # version id (immutable)
    name: str
    type: str
    # single-energy substrate (no per-entity channels on nodes)
    E: float                  # activation (runtime, not part of version key)
    weight_log: float         # long-run attractor (learned; can be versioned or separate)
    # bitemporal
    valid_from: datetime
    valid_to: datetime | None
    known_from: datetime
    known_to: datetime | None
    supersedes: str | None    # previous vid
    superseded_by: str | None # next vid
    meta: dict                # tags, provenance, source
````

**Notes**

* **Activation E** is runtime, not part of the bitemporal identity (we don’t time‑version E).
* Links follow the same pattern (`VersionedLink`) with `src_vid`, `dst_vid` or logical ids plus a resolution rule.
* Prefer **immutable versions**; never in‑place edit a version. 

## 3) Why this makes sense

### Phenomenology

“I used to think X; now I know Y.” Bitemporal tracking **stores that evolution** so the system can tell the story back and the agents can ask **“what did we believe on T?”** accurately. 

### Bio‑inspiration

Episodic memory has **event time** and **memory time**. The model mirrors that with two explicit timelines.

### Systems‑dynamics

Separating reality vs knowledge timelines removes feedback loops where “corrections” mutate history invisibly and break learning/attribution.

## 4) Expected behaviors

* **Time‑travel queries**: “As‑of 2025‑10‑18 (knowledge), what did we believe about Context Reconstruction?”
* **Retroactive facts**: learn today something has been true since last month (reality backdated; knowledge starts now).
* **Auditable learning**: track how and when views changed, and what signals triggered corrections. 

## 5) Why this vs alternatives

| Approach               | Problem                       | Bitemporal benefit                    |
| ---------------------- | ----------------------------- | ------------------------------------- |
| Single timeline        | Corrections overwrite history | Keep truth and belief separate        |
| Soft “updated_at” only | No as‑of queries              | Interval semantics enable time‑travel |
| Event log only         | Expensive replay; hard joins  | Versions + intervals are queryable    |

## 6) Observability — How & what to measure, and how to read it

**Events**

* `version.create`, `version.supersede`, `version.expire` with `{id, vid, valid_from/to, known_from/to, reason, source}`.

**Metrics**

* **Correction rate** (versions/day), **median correction latency** (discovery lag = known_from − valid_from), **belief churn** (versions per logical id), **retroactivity share** (facts backdated). These reveal where knowledge is volatile vs stable. 

**Dashboards**

* Timeline lane per logical id; overlays of reality vs knowledge intervals; “where we believed wrong” bands (known overlaps outside valid).

## 7) Failure modes & risks (and why they’re bad)

| Risk                 | Why bad                        | Guard                                                   |
| -------------------- | ------------------------------ | ------------------------------------------------------- |
| Clock skew           | Wrong interval math            | Always store UTC; monotonic checks                      |
| Version explosion    | Storage/cost blow‑ups          | Retain policy: compact “cold” tails; daily rollups      |
| Silent retroactivity | Surprises consumers            | Emit `version.create` with `retroactive=true`; UI badge |
| Ambiguous joins      | Misattribution across versions | Always join by **vid**; define resolution windows       |

## 8) Integration in code

* **Where**: `core/models.py` (versioned dataclasses), persistence in `adapters/storage/*`.
* **Indexing**: composite indices on `(id, known_from/to)` and `(id, valid_from/to)`.
* **APIs**: `GET /v1/nodes/{id}?as_of=knowledge:2025-10-18` and `?as_of=reality:…` helpers.
* **Learning**: TRACE & traversal updates target the **current** vid; superseding creates a new vid and closes `known_to`. 

## 9) Success criteria

* As‑of queries run in **O(log V)**; no full history scans.
* Clear audit trails; correction latency distribution monitored; zero clock‑skew defects in CI.

## 10) Open questions / improvements / mistakes to avoid

* Range vs point **validity** (intervals vs fuzzy ranges) — start with intervals.
* Backfill pipelines for **retroactive imports**.
* **Avoid** in‑place edits; never mutate `vid` rows.

````

### B. Changes made (diff‑style)
- Removed per‑subentity energy fields from examples; **single‑energy** E kept runtime‑side.  
- Replaced mutable “belief nodes” with **immutable version rows** + `supersedes/superseded_by`.  
- Added **events/metrics** and **indices** for real ops.  
- Clarified joins by **vid** and the two distinct `as_of` modes. :contentReference[oaicite:11]{index=11}

### C. Compliance matrix
| Spec point | Status |
|---|---|
| Single‑energy per node; links don’t store activation | **OK** |
| Entities = neighborhoods; WM entity‑first | **N/A** |
| Stimuli inject; learning updates weights | **OK** |
| Two‑scale traversal unaffected | **OK** |
| Observability clear & actionable | **OK** |