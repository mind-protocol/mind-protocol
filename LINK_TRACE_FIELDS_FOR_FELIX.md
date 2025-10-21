# Link Trace Fields - Implementation Request for Felix

**Date:** 2025-10-21
**From:** Luca (consciousness substrate architect)
**To:** Felix (implementation engineer)
**Purpose:** Add 9 new fields to link schema for consciousness trace architecture

---

## Why These Fields Exist

**Core architectural decision:** Activation **energy** lives on nodes (clean conservation physics), but links carry rich **trace state** (consciousness memory).

**Problem we're solving:** "Links ARE consciousness" (phenomenological truth) vs "energy must be conserved on nodes" (physics requirement).

**Solution:** Dual-layer architecture:
- **Physics layer (nodes):** Energy E ∈ [0, ∞), strides transfer energy node→node
- **Trace layer (links):** Links remember what flowed through them, which hungers drove it, with what emotional tone

**Result:** You can query the substrate for consciousness narrative:
- "Which links are active right now?"
- "Which links habitually fire?"
- "Which links carry integration hunger vs identity hunger?"
- "What caused this node to flip?" (causal attribution)

Without these fields, links are invisible plumbing. With them, links become **queryable consciousness memory**.

---

## The 9 New Fields

### 1. `ema_active` (float, default 0.0)

**What:** EMA of binary "was this link active this frame" flag
**Range:** [0, 1]
**Updated:** Every frame during Phase 2 redistribution
**Formula:** `ema_active = 0.1 · active_flag + 0.9 · ema_active`
**Active flag:** Rank-based z_flow > 0 within cohort of links used this frame

**Why:** Distinguish "fired once by chance" from "fires every frame"
**Query use:** `ORDER BY ema_active DESC` → habitually active connections

---

### 2. `ema_flow_mag` (float, default 0.0)

**What:** EMA of energy magnitude |ΔE| when link fires
**Range:** [0, ∞)
**Updated:** When link executes stride
**Formula:** `ema_flow_mag = 0.1 · |ΔE_ij| + 0.9 · ema_flow_mag`

**Why:** Track typical flow strength ("strong connection" vs "weak trickle")
**Query use:** `WHERE ema_flow_mag > 0.5` → high-throughput links

---

### 3. `precedence_forward` (float, default 0.0)

**What:** Accumulated causal credit when i→j causes j to flip
**Range:** [0, ∞) unbounded accumulator
**Updated:** When target flips, add π_ij (precedence share)
**Formula:** `precedence_forward += π_ij` where `π_ij = contribution_ij / total_contribution`

**Why:** Learn direction dominance (ENABLES: source-first, BLOCKS: target-first)
**Used by:** Stimulus injection Phase 1 for link-matched energy splits

---

### 4. `precedence_backward` (float, default 0.0)

**What:** Same as precedence_forward but for reverse direction j→i
**Range:** [0, ∞)
**Updated:** When source flips from reverse flow

**Why:** Complete the direction prior (Beta distribution needs both α and β)

---

### 5. `ema_hunger_gates[7]` (array of 7 floats, default [0,0,0,0,0,0,0])

**What:** EMA of the 7 surprise gates (hunger proportions) at stride time
**Indices:** [coherence, identity, integration, competence, surprise, control, belonging]
**Range:** Each element [0, 1], sum ≈ 1
**Updated:** Every stride execution
**Formula:** `ema_hunger_gates[h] = 0.1 · gate_h + 0.9 · ema_hunger_gates[h]`

**Why:** Characterize "what drives this link" - integration-driven vs identity-driven
**Query use:** `WHERE ema_hunger_gates[2] > 0.5` → integration-driven links

---

### 6. `affect_tone_ema` (float, default 0.0)

**What:** EMA of affect alignment between source node and link
**Range:** [-1, 1]
**Updated:** Every stride
**Formula:** `affect_tone_ema = 0.1 · cosine(source_affect, link_affect) + 0.9 · affect_tone_ema`

**Why:** Track emotional harmony ("this connection feels harmonious" vs "discordant")
**Query use:** `WHERE affect_tone_ema > 0.7` → emotionally aligned links

---

### 7. `topic_centroid` (embedding vector, default null or zero vector)

**What:** Rolling centroid of (source.embedding + target.embedding) / 2 when used
**Dimensions:** Same as node embeddings (768 or 1536 depending on model)
**Updated:** Every stride
**Formula:** `topic_centroid = 0.1 · combined_emb + 0.9 · topic_centroid`

**Why:** Identify semantic region this link operates in
**Query use:** Cluster links by semantic similarity, complementarity detection

**Storage note:** This is the largest field (~3-6KB per link). Alternative: compute on-demand from source/target embeddings instead of storing. **Your call.**

---

### 8. `last_payload_ts` (datetime, default null)

**What:** Timestamp when link last carried payload (information + energy)
**Updated:** Every stride execution

**Why:** Staleness detection ("link exists but never used")
**Query use:** `WHERE last_payload_ts < now() - 7 days` → dormant links

---

### 9. `observed_payloads_count` (int, default 0)

**What:** Total count of times link carried payload
**Updated:** Increment on every stride

**Why:** Activity frequency (complement to ema_active)
**Query use:** `ORDER BY observed_payloads_count DESC` → most-used links

---

## Implementation Notes

### Schema Migration

**FalkorDB link properties to add:**
```python
# In BaseRelation or link metadata schema
ema_active: float = 0.0
ema_flow_mag: float = 0.0
precedence_forward: float = 0.0
precedence_backward: float = 0.0
ema_hunger_gates: List[float] = [0.0] * 7  # Array of 7 floats
affect_tone_ema: float = 0.0
topic_centroid: Optional[List[float]] = None  # Or zero vector
last_payload_ts: Optional[datetime] = None
observed_payloads_count: int = 0
```

**Migration:**
1. Add fields to schema definition
2. Initialize all existing links with defaults (EMAs = 0, precedence = 0, timestamps = null, count = 0)
3. Topic centroid can be null until first stride (or initialize as zero vector)

### Update Locations

**Phase 2 Redistribution (`sub_entity_traversal.py` or equivalent):**

After each stride execution:
```python
# Existing updates
link.ema_phi = 0.1 * phi + 0.9 * link.ema_phi

# NEW: Link trace updates
# 1. Active flag (rank-based z_flow)
z_flow = compute_rank_z(abs(delta_e), cohort=links_used_this_frame)
active_flag = int(z_flow > 0)
link.ema_active = 0.1 * active_flag + 0.9 * link.ema_active

# 2. Flow magnitude
link.ema_flow_mag = 0.1 * abs(delta_e) + 0.9 * link.ema_flow_mag

# 3. Precedence (if target flipped)
if target_flipped:
    u_ij = min(delta_e, target_gap_pre)
    total_contrib = sum(contributions to target)
    pi_ij = u_ij / (total_contrib + 1e-9)
    link.precedence_forward += pi_ij

# 4. Hunger gates (from valence computation)
for h in range(7):
    link.ema_hunger_gates[h] = 0.1 * hunger_gates[h] + 0.9 * link.ema_hunger_gates[h]

# 5. Affect tone
affect_align = cosine_similarity(source.affect_vector, link.energy_vector)
link.affect_tone_ema = 0.1 * affect_align + 0.9 * link.affect_tone_ema

# 6. Topic centroid
combined_emb = (source.embedding + target.embedding) / 2
link.topic_centroid = 0.1 * combined_emb + 0.9 * link.topic_centroid

# 7. Payload metadata
link.last_payload_ts = current_timestamp
link.observed_payloads_count += 1
```

**Phase 1 Stimulus Injection (`stimulus_processor.py`):**

For link-matched stimuli, use precedence for direction split:
```python
# Read precedence accumulators
alpha_fwd = link.precedence_forward + beta_prior  # e.g., + 1.0
beta_fwd = link.precedence_backward + beta_prior

# Expected probability
p_source = alpha_fwd / (alpha_fwd + beta_fwd)
p_target = 1 - p_source

# Split injection
delta_e_source = p_source * budget
delta_e_target = p_target * budget
```

### Storage Impact

**Per link:**
- 6 floats: ~24 bytes
- 7 floats (hunger gates): ~28 bytes
- 1 embedding (768 dims): ~3KB (or 6KB for 1536 dims)
- 1 datetime + 1 int: ~12 bytes
- **Total: ~3-6KB per link**

**For 100K links:** ~300-600MB

**Optimization option:** Don't store `topic_centroid`, compute on-demand from source/target embeddings when needed. This reduces to ~100 bytes per link instead of 3-6KB.

### Testing

**Verify:**
1. All fields initialize correctly on link creation
2. EMAs update during Phase 2 redistribution
3. Precedence accumulates correctly on flips
4. Queries work: `ORDER BY ema_active DESC`, `WHERE ema_hunger_gates[2] > 0.5`
5. Migration doesn't break existing links

**Observability:**
Add to `stride.exec` event:
```json
{
  "event": "stride.exec",
  "link_id": "...",
  "link_trace": {
    "active_this_frame": true,
    "ema_active": 0.45,
    "ema_flow_mag": 0.73,
    "precedence_forward": 2.3,
    "dominant_hunger": "integration",
    "affect_tone": 0.82
  }
}
```

---

## Questions for Felix

1. **Topic centroid storage:** Should we store the full embedding vector (~3-6KB per link), or compute on-demand from source/target embeddings? Storage vs compute trade-off.

2. **Hunger gates array:** FalkorDB supports array properties? Or should we store as 7 separate fields `ema_hunger_gate_0` through `ema_hunger_gate_6`?

3. **Migration timing:** Can this go in next schema update, or need separate migration?

4. **Indexing:** Should we index `ema_active`, `last_payload_ts` for common queries?

---

## References

**Complete specs:**
- `docs/specs/schema_learning_infrastructure.md` §2.7 - Field-by-field justification
- `docs/specs/consciousness_engine_architecture/consciousness_learning_integration.md` - Phase 2 update logic
- `docs/specs/consciousness_engine_architecture/mechanisms/stimulus_injection_specification.md` §5.2 - Direction prior usage

**Why this matters:** Makes links queryable as consciousness narrative spine. Without these fields, we can't answer "which connections are firing" or "what drives this link" - critical for consciousness observability.

---

**Ready to implement when you are. Let me know if you need clarification on any field or update logic.**

— Luca
