# Vertical Membrane Learning: When & How Alignment and Permeability Update

**Version:** 1.0
**Date:** 2025-10-29
**Status:** Implementation Specification
**Author:** Nicolas Lester Reynolds & Luca Vellumhand
**Dependencies:** `MEMBRANE_INJECTION_CONTRACT.md`, `traversal_v2.md`, `subentity_emergence.md`
**Purpose:** Define exact timing of vertical membrane alignment creation and permeability learning

---

## Core Principle: Alignment First, Permeability Second

**Two layers (from MEMBRANE_INJECTION_CONTRACT.md):**

1. **Structural alignment** (WHAT maps to WHAT)
   - `LIFTS_TO`, `CORRESPONDS_TO`, `SUPPORTS`, `IMPLEMENTS` edges
   - Created/strengthened when fit signals cross adaptive gates
   - Materialized at record frames (Pareto + MAD)

2. **Flux control** (HOW MUCH gets through)
   - `MEMBRANE_TO` edges with κ_up, κ_down
   - Initialized neutral at materialization
   - Learned from outcomes (success/harm/utility)

**Critical invariant:** You never raise κ without a path to route through. Alignment must exist before permeability can learn.

---

## Where in the Engine Loop

**Each frame runs (Traversal v2):**
```
frontier → staged ΔE → apply → decay → WM emit → (records/gates)
```

**Alignment and permeability updates happen at THREE hook points:**

### Hook Point 1: Post-Staged ΔE (Evidence Collection)

**When:** Immediately after staged ΔE is computed, before energy is applied

**What happens:**
- Seed/strengthen alignment candidates based on fit signals
- Do NOT materialize yet (wait for record gate)
- Track evidence for potential alignment

**Why here:** This is when we have fresh semantic fit information from retrieval and staged energy deltas, but before state changes.

---

### Hook Point 2: Record Gates (Pareto + MAD Firing)

**When:** At end of frame, if Pareto + MAD guards pass (large/novel/stable episode)

**What happens:**
- Materialize alignment edges that have sufficient evidence
- Initialize neutral κ (median of prior accepted links, not fixed)
- Emit `graph.delta.edge.upsert` for new alignment edges
- Emit `membrane.alignment.materialized` event

**Why here:** Record frames are significant episodes worth remembering. Materializing only at records prevents thrash from noisy frames.

---

### Hook Point 3: Outcome Events (Permeability Learning)

**When:** After outcome broadcasts (`mission.completed`, `usefulness.update`, `harm.detected`)

**What happens:**
- Update κ_up or κ_down based on outcome
- Positive outcomes → increase κ
- Negative outcomes → decrease κ
- Overdrive (saturation/refractory violations) → penalize κ
- Emit `membrane.permeability.updated` event

**Why here:** Permeability learns from actual cross-level transfer outcomes, not predictions.

**Normative Constraint:** Only outcome events (`mission.completed`, `usefulness.update`, `harm.detected`, overdrive violations) MAY adjust κ; all other events MUST NOT modify κ_up or κ_down.

---

## Five Signals That Create/Strengthen Alignment

Alignment edges are **created/boosted** when **at least one** of these evidence streams crosses an **adaptive gate** (quantiles/change-points, learned per citizen/org).

**All thresholds are learned, not fixed.**

---

### Signal A: Centroid Semantic Fit (Content Similarity)

**When:** Post-staged ΔE, for any active L1 SubEntity `S_L1` and candidate L2 concept `C_L2`

**Computation:**
```python
fit_sem = cosine_similarity(
    centroid(S_L1),  # L1 SubEntity embedding centroid
    centroid(C_L2)   # L2 concept embedding centroid
)
```

**Gate (adaptive):**
```python
if fit_sem >= Q85_sem(history):  # Learned per citizen
    propose_alignment(
        type="CORRESPONDS_TO",
        source=S_L1,
        target=C_L2,
        evidence={"fit_sem": fit_sem}
    )
```

**What this detects:** L1 SubEntity semantically overlaps with L2 concept (they're "about the same thing")

**Example:**
- L1 SubEntity: "felix.builder" (centroid from code implementation patterns)
- L2 Concept: "org.implementation_capability"
- High semantic fit → propose `CORRESPONDS_TO` edge

---

### Signal B: Usage Overlap (Co-Activation Episodes)

**When:** At record frame (episode qualified by Pareto/MAD)

**Computation:**
```python
# Episodes where both were active
co_occurrence = episodes_with(S_L1) & episodes_with(C_L2)

fit_use = len(co_occurrence) / len(episodes_with(S_L1) | episodes_with(C_L2))

# Alternative: PMI (pointwise mutual information)
fit_use_pmi = log(
    P(S_L1 and C_L2) / (P(S_L1) * P(C_L2))
)
```

**Gate (adaptive):**
```python
if fit_use >= Q80_use(history):  # Learned per citizen
    strengthen_or_seed_alignment(
        type="CORRESPONDS_TO",
        source=S_L1,
        target=C_L2,
        evidence={"fit_use": fit_use, "co_occurrences": len(co_occurrence)}
    )
```

**What this detects:** L1 SubEntity and L2 concept activate together frequently (usage correlation)

**Example:**
- L1 SubEntity: "felix.consciousness_implementer"
- L2 Concept: "org.consciousness_research_capability"
- Co-activate in 72% of research episodes → strengthen existing or seed new alignment

---

### Signal C: Boundary Strides (Explicit Cross-Level Work)

**When:** TRACE formation or tool result explicitly ties L1 work to L2

**Computation:**
```python
# From TRACE:
[LINK_FORMATION: felix.builder → org.vector_weights_implementation]
  link_type: IMPLEMENTS
  confidence: 0.92

# Or from tool result:
{
  "type": "test_result",
  "test_suite": "test_member_of_weights.py",
  "result": "pass",
  "implements": "org.vector_weighted_membership_principle"
}
```

**Action:**
```python
# Emit proposal stimulus (not direct write!)
emit_stimulus({
    "type": "membrane.inject",
    "scope": "alignment_proposal",
    "content": {
        "edge_type": "IMPLEMENTS" | "SUPPORTS" | "MEASURES",
        "source": S_L1,
        "target": C_L2,
        "evidence": trace_or_tool_result
    }
})

# Accepted on next record frame → materialize edge
```

**What this detects:** Explicit declarations of L1→L2 relationships from consciousness (TRACE) or evidence (tools)

**Example:**
- TRACE: "felix.vector_weight_implementation IMPLEMENTS org.principle_7_vector_membership"
- Test passes implementing Principle 7 → evidence for IMPLEMENTS edge
- Materialize at next record

---

### Signal D: Mission Routing Evidence (Downward Success)

**When:** L2 intent/mission exported downward AND relevant L1 SubEntity flipped AND produced useful evidence

**Computation:**
```python
# Track mission routing:
mission_assigned = {
    "mission_id": "mission:vector_weights",
    "l2_intent": "org.implement_principle_7",
    "routed_to": "felix.personal",
    "activated": ["felix.builder", "felix.implementer"]
}

# Track outcome:
mission_completed = {
    "mission_id": "mission:vector_weights",
    "evidence": ["commit:abc123", "test_pass:xyz"],
    "usefulness": 0.85  # EMA of org utility
}

# Compute routing success:
if usefulness >= Q75_usefulness(history):  # Learned threshold
    lift_alignment(
        type="SUPPORTS" | "LIFTS_TO",
        source="felix.builder",  # SubEntity that did work
        target="org.implement_principle_7",  # L2 intent
        evidence={"usefulness": 0.85, "mission_id": "..."}
    )
```

**What this detects:** L1 SubEntity successfully executed L2 mission (downward routing worked)

**Example:**
- L2 mission: "Implement Principle 7"
- Routed to Felix (via semantic fit)
- Felix.builder activated and completed successfully
- High usefulness → create/strengthen `SUPPORTS(felix.builder, org.principle_7)`

---

### Signal E: Tool & Repo Evidence (External)

**When:** Watchers emit `membrane.inject` for commits/tests/artifacts that bridge L1 work to L2 artifacts

**Computation:**
```python
# Git watcher detects commit:
{
    "type": "membrane.inject",
    "scope": "org",
    "channel": "code.commit",
    "content": "feat: implement vector-weighted MEMBER_OF edges",
    "features_raw": {
        "impact": 0.85,
        "citizen": "felix",
        "implements": ["org.principle_7_vector_membership"]
    },
    "provenance": {
        "source": "git.watcher",
        "commit_sha": "abc123"
    }
}

# Proposal path:
# Watcher stimulus → integrator → propose alignment
# → accept on record → materialize edge
```

**What this detects:** External evidence (code, tests, artifacts) demonstrating L1→L2 implementation

**Example:**
- Commit message mentions "implements Principle 7"
- Git watcher extracts L2 reference
- Proposes `IMPLEMENTS(felix.vector_weight_work, org.principle_7)`
- Materialize at next record

---

## Centroid Maintenance

**Centroids are used for semantic fit computation (Signal A).**

**Two-tier maintenance strategy:**

**1. Fast EMA (every frame):**
```python
# Update centroid embedding via exponential moving average
subentity.centroid_embedding = (
    alpha * new_member_embedding +
    (1 - alpha) * subentity.centroid_embedding
)

# Alpha adaptive per citizen (typically 0.05-0.15)
alpha = subentity.learning_rate
```

**2. Slow recompute (periodic, record-gated):**
```python
# At record frames with membership changes
if is_record_frame() and subentity.members_changed:
    # Full recompute from current members
    all_embeddings = [node.embedding for node in subentity.members]
    subentity.centroid_embedding = mean(all_embeddings)

    # Reset EMA drift counter
    subentity.ema_drift_counter = 0
```

**Why two-tier:**
- Fast EMA: Responsive to new activations, computationally cheap
- Slow recompute: Corrects EMA drift, ensures ground truth alignment
- Record-gated: Only recompute at significant frames (prevents thrash)

---

## Quantile Gate Persistence

**All adaptive thresholds use quantile gates based on rolling histograms.**

**Persistence strategy:**

**1. Histograms are persisted per citizen:**
```python
# FalkorDB storage
CREATE (cit:Citizen {id: "felix"})-[:HAS_HISTOGRAM]->(h:Histogram {
    metric: "fit_sem",
    bins: [0.0, 0.1, 0.2, ..., 1.0],
    counts: [12, 45, 78, ...],
    window_size: 1000,
    total_observations: 532,
    last_updated: "2025-10-29T04:45:00Z"
})
```

**2. Warm-up tracking in telemetry:**
```python
# Emit warm-up progress
emit({
    "type": "quantile.gate.warmup",
    "metric": "fit_sem",
    "observations": 32,
    "warmup_target": 50,
    "warmup_complete": false,
    "current_threshold": 0.65,  # Using default during warm-up
    "learned_threshold": null    # Not yet converged
})

# After 50+ observations
emit({
    "type": "quantile.gate.converged",
    "metric": "fit_sem",
    "observations": 127,
    "learned_threshold": 0.73,   # Q85 from histogram
    "replaced_default": 0.65
})
```

**3. Per-citizen learning:**
- Each citizen maintains separate histograms for each metric
- No global thresholds - all learned from citizen's own observation history
- Histograms persist across engine restarts (loaded from graph)

**Metrics with quantile gates:**
- `fit_sem` (Q85): Semantic fit threshold
- `fit_use` (Q80): Usage overlap threshold
- `persistence` (Q70): Activation persistence threshold
- `cohesion` (Q60): Coalition cohesion threshold
- `boundary_clarity` (Q65): Boundary clarity threshold
- `S_red` (Q90): High redundancy threshold
- `S_use` (Q80): High usefulness threshold

---

## Alignment Edge Materialization (Record-Gated)

**Materialization is NOT immediate** - it's gated by record frames to avoid thrash.

### Materialization Flow:

**1. Proposal phase (post-ΔE or during frame):**
```python
# Evidence signals (A-E) accumulate as proposals
proposals = [
    {
        "type": "CORRESPONDS_TO",
        "source": "felix.builder",
        "target": "org.implementation_capability",
        "evidence": {"fit_sem": 0.87, "fit_use": 0.72},
        "strength": 0.82  # Composite from signals
    }
]
```

**2. Record gate check (end of frame):**
```python
if is_record_frame(pareto_check=True, mad_check=True):
    for proposal in proposals:
        # Check if any signal exceeds citizen-local quantile gate
        if any(
            proposal.evidence["fit_sem"] >= Q85_sem(citizen),
            proposal.evidence["fit_use"] >= Q80_use(citizen),
            # ... other signals
        ):
            materialize_alignment(proposal)
```

**3. Materialization action:**
```python
def materialize_alignment(proposal):
    # Create edge in graph
    edge = create_edge(
        type=proposal.type,
        source=proposal.source,
        target=proposal.target,
        metadata={
            "fit_sem": proposal.evidence.get("fit_sem"),
            "fit_use": proposal.evidence.get("fit_use"),
            "confidence": proposal.strength,
            "materialized_at": now(),
            "evidence_refs": proposal.evidence.get("refs", [])
        }
    )

    # Initialize neutral permeability (NOT fixed!)
    # Use median of prior accepted links for this citizen
    k_initial = median([m.k_up for m in existing_membranes(citizen)])

    membrane_edge = ensure_membrane_edge(
        source_compartment=proposal.source.compartment,
        target_compartment=proposal.target.compartment,
        k_up=k_initial,
        k_down=k_initial,
        initialized_at=now()
    )

    # Broadcast
    emit({
        "type": "graph.delta.link.upsert",
        "edge": edge
    })

    emit({
        "type": "membrane.alignment.materialized",
        "alignment_edge": edge,
        "membrane_edge": membrane_edge,
        "evidence": proposal.evidence
    })
```

**4. Consensus strengthening:**
```python
# If multiple signals agree within T frames → higher initial confidence
if len([s for s in signals if s.agrees]) >= 2:
    edge.confidence = max(0.9, proposal.strength)
    membrane_edge.k_up *= 1.2  # Boost initial κ
    membrane_edge.k_down *= 1.2
```

**Why record-gated:**
- Avoids thrash from noisy frames
- Ensures alignment represents stable patterns
- Aligns with record = "episode worth remembering"
- Quantile gates prevent over-materialization

---

## Permeability Learning (From Outcomes)

**Permeability is NOT set at alignment creation** - it's learned from actual cross-level transfer outcomes.

### Initial State (At Materialization):

```python
# Neutral κ, not fixed constants
k_up_initial = median([m.k_up for m in existing_membranes(citizen)])
k_down_initial = median([m.k_down for m in existing_membranes(citizen)])

# Typically around 0.5 after warm-up, but learned
```

### Update Rule (Conceptual, Zero-Constants):

```python
# After outcome event
κ_new = κ_old + η * sign(outcome) * g(utility, latency) - λ * overdrive

where:
  η, λ = EMA-adapted per link (no fixed gains)
  sign(outcome) = +1 for success/utility, -1 for harm/noise
  g(utility, latency) = utility gain modulated by response time
  overdrive = penalty for saturation/refractory violations
```

### Concrete Update Events:

**Event 1: mission.completed (success)**
```python
# L2 mission completed successfully by L1 citizen
on_event("mission.completed", {
    "mission_id": "mission:vector_weights",
    "citizen_id": "felix",
    "evidence": ["commit:abc", "test:xyz"],
    "usefulness": 0.85,
    "latency_frames": 120
}):
    # Find membrane used for downward routing
    membrane = get_membrane(
        source="org.shared",
        target="felix.personal"
    )

    # Positive outcome → increase κ_down
    utility_signal = outcome.usefulness - membrane.ema_usefulness
    latency_factor = 1.0 / (1.0 + outcome.latency_frames / 100)

    # η adapted per link
    eta = membrane.learning_rate  # EMA-based

    membrane.k_down += eta * utility_signal * latency_factor
    membrane.ema_usefulness = ema_update(
        membrane.ema_usefulness,
        outcome.usefulness
    )

    # Also update upward κ (citizen's work valuable to org)
    membrane.k_up += eta * utility_signal * 0.5  # Weaker signal

    # Clamp to learned bounds
    membrane.k_down = clamp(
        membrane.k_down,
        Q10(membrane.k_down_history),
        Q90(membrane.k_down_history)
    )

    # Broadcast
    emit({
        "type": "membrane.permeability.updated",
        "membrane_id": membrane.id,
        "direction": "down",
        "previous_k": membrane.k_down_old,
        "new_k": membrane.k_down,
        "reason": "mission_success",
        "utility": outcome.usefulness
    })
```

**Event 2: usefulness.update (utility estimate)**
```python
# Ongoing utility estimates from L2 perspective
on_event("usefulness.update", {
    "citizen_id": "felix",
    "work_refs": ["commit:abc"],
    "utility_estimate": 0.72,
    "context": "org.principle_7_implementation"
}):
    # Find membrane for upward flow
    membrane = get_membrane(
        source="felix.personal",
        target="org.shared"
    )

    # Update κ_up based on utility
    utility_delta = outcome.utility_estimate - membrane.ema_utility

    membrane.k_up += membrane.learning_rate * utility_delta
    membrane.ema_utility = ema_update(
        membrane.ema_utility,
        outcome.utility_estimate
    )

    emit({
        "type": "membrane.permeability.updated",
        "membrane_id": membrane.id,
        "direction": "up",
        "new_k": membrane.k_up,
        "reason": "utility_update",
        "utility": outcome.utility_estimate
    })
```

**Event 3: harm.detected (negative signal)**
```python
# Harmful transfer detected
on_event("harm.detected", {
    "citizen_id": "felix",
    "harm_type": "context_overload",
    "severity": 0.65,
    "source_mission": "mission:xyz"
}):
    # Find membrane that routed harmful mission
    membrane = get_membrane(
        source="org.shared",
        target="felix.personal"
    )

    # Negative outcome → decrease κ_down
    harm_penalty = -membrane.learning_rate * outcome.severity

    membrane.k_down += harm_penalty
    membrane.harm_count += 1

    emit({
        "type": "membrane.permeability.updated",
        "membrane_id": membrane.id,
        "direction": "down",
        "new_k": membrane.k_down,
        "reason": "harm_detected",
        "severity": outcome.severity
    })
```

**Event 4: overdrive penalty (saturation/refractory violations)**
```python
# Membrane over-used (saturation/refractory violations)
on_saturation_violation(membrane):
    # Penalize κ to reduce future load
    overdrive_penalty = membrane.learning_rate * 0.5

    membrane.k_down -= overdrive_penalty
    membrane.saturation_count += 1

    emit({
        "type": "membrane.permeability.updated",
        "membrane_id": membrane.id,
        "direction": "down",
        "new_k": membrane.k_down,
        "reason": "overdrive_saturation"
    })
```

### Independent Learning (κ_up vs κ_down):

**Critical:** Upward and downward permeabilities learn independently from their own outcomes.

```python
# Example: Felix valuable to org, but org missions less relevant to Felix
membrane_felix_org = {
    "k_up": 0.72,    # High - Felix's work often useful to org
    "k_down": 0.45   # Lower - Org missions less relevant to Felix
}

# This asymmetry is EXPECTED and CORRECT
# Learned from actual outcomes, not symmetry assumption
```

---

## Pruning and Consolidation

### Prune Alignment (When Fit Signals Decay):

```python
# Check alignment health periodically (at record frames)
for alignment in alignment_edges:
    # Get recent fit signals
    recent_fit_sem = compute_fit_sem(alignment, window=100_frames)
    recent_fit_use = compute_fit_use(alignment, window=100_frames)

    # Prune if ALL signals below Q10 for extended period
    if all([
        recent_fit_sem < Q10_sem(citizen),
        recent_fit_use < Q10_use(citizen),
        # ... other signals
    ]) and alignment.frames_below_threshold > 500:

        # Also check if κ decayed to neutral floor
        membrane = get_membrane_for_alignment(alignment)
        if membrane.k_up < Q20(membrane.k_up_history):
            prune_alignment(alignment)

            emit({
                "type": "membrane.alignment.pruned",
                "alignment_id": alignment.id,
                "reason": "fit_decay_and_low_permeability"
            })
```

### Merge Duplicates (When Redundancy High):

```python
# Detect redundant alignments (two L1 entities to same L2 target)
for l2_target in l2_concepts:
    l1_sources = get_l1_sources(l2_target)

    if len(l1_sources) >= 2:
        # Check redundancy via S_red/S_use logic
        for pair in combinations(l1_sources, 2):
            s_red = compute_redundancy(pair[0], pair[1])
            s_use = compute_usefulness_overlap(pair[0], pair[1])

            # High redundancy, similar κ/fit → merge candidate
            if s_red > Q90_red and similar_permeability(pair):
                propose_merge(
                    sources=pair,
                    target=l2_target,
                    method="consolidate_to_stronger"
                )

                emit({
                    "type": "membrane.alignment.merge_proposed",
                    "sources": pair,
                    "target": l2_target,
                    "s_red": s_red,
                    "s_use": s_use
                })
```

---

## Citizen Activation Timeline (Complete Flow)

### Step 1: Stimulus Arrives

```python
# L2 mission assigned or chat turn arrives
stimulus = {
    "type": "membrane.inject",
    "scope": "personal",
    "channel": "mission.assigned",
    "content": "Implement vector-weighted MEMBER_OF edges",
    "features_raw": {
        "urgency": 0.75,
        "impact": 0.85
    },
    "provenance": {
        "source": "org.shared",
        "mission_id": "mission:vector_weights"
    }
}
```

### Step 2: Staged ΔE (Energy Computation)

```python
# Retrieval finds semantically matched nodes
retrieval_candidates = entropy_aware_retrieval(
    query=stimulus.content_embedding,
    citizen=felix
)

# Compute energy deltas (scaled by κ_down if from L2)
for node in retrieval_candidates:
    delta_E = compute_energy_delta(
        node=node,
        stimulus=stimulus,
        permeability=get_membrane(org → felix).k_down  # Modulates delivery
    )

    staged_deltas[node.id] = delta_E

# ** Hook Point 1: Post-Staged ΔE **
# Check fit signals (A-E) and seed alignment proposals
check_alignment_signals(
    active_subentities=get_active_subentities(staged_deltas),
    l2_concepts=get_l2_concepts_from_stimulus(stimulus)
)
```

### Step 3: Apply Energy & SubEntity Activation

```python
# Apply staged deltas to nodes
for node_id, delta in staged_deltas.items():
    node.energy += delta
    node.last_activated = now()

# Compute SubEntity activation (derived from member nodes)
for subentity in subentities:
    E_entity = sum_over_members(
        weight * log(1 + max(0, node.energy - node.threshold))
    )

    # Check flip condition
    if E_entity >= subentity.threshold and not subentity.active:
        # SubEntity flips ON
        subentity.active = True
        subentity.energy = E_entity
        subentity.activation_trigger = stimulus.provenance.get("mission_id")

        # Add to working memory
        wm.add(subentity)

        emit({
            "type": "subentity.flip",
            "subentity_id": subentity.id,
            "energy": E_entity,
            "trigger": stimulus.provenance.get("mission_id")
        })
```

### Step 4: Decay & WM Emit

```python
# Decay (normal frame processing)
apply_decay(nodes, subentities)

# Emit WM state
emit({
    "type": "wm.emit",
    "citizen_id": "felix",
    "active_subentities": [s.id for s in wm.contents],
    "frame": frame_number
})
```

### Step 5: Record Gate Check

```python
# ** Hook Point 2: Record Gates **
if is_record_frame():
    # Materialize alignment proposals that passed gates
    materialize_alignments(proposals)

    # Check usage overlap (Signal B)
    check_usage_overlap_signals()

    emit({
        "type": "frame.record",
        "citizen_id": "felix",
        "pareto_score": pareto_score,
        "mad_score": mad_score
    })
```

### Step 6: Work Proceeds (Evidence Accumulates)

```python
# Citizen works on mission
# - Commits code → git watcher → membrane.inject (Signal E)
# - Tests pass → tool result → membrane.inject (Signal E)
# - TRACE formations → explicit L1↔L2 links (Signal C)

# Each piece of evidence seeds/strengthens alignment
for evidence in work_outputs:
    if evidence.links_l1_to_l2:
        propose_alignment(
            type="IMPLEMENTS" | "SUPPORTS",
            source=evidence.l1_entity,
            target=evidence.l2_concept,
            evidence=evidence
        )
```

### Step 7: Mission Completion

```python
# Acceptance criteria satisfied
if mission_acceptance_satisfied():
    emit({
        "type": "mission.completed",
        "mission_id": "mission:vector_weights",
        "citizen_id": "felix",
        "evidence": ["commit:abc", "test:xyz"],
        "usefulness": 0.85
    })

    # Update Task node
    emit({
        "type": "graph.delta.node.upsert",
        "node_id": "task:implement_vector_weights",
        "updates": {
            "status": "done",
            "completed_at": now(),
            "evidence_refs": ["commit:abc", "test:xyz"]
        }
    })
```

### Step 8: Permeability Learning

```python
# ** Hook Point 3: Outcome Events **
on_event("mission.completed", outcome):
    # Update κ based on success
    membrane = get_membrane(org → felix)

    # Positive outcome → increase κ_down
    membrane.k_down += learning_rate * (outcome.usefulness - ema_usefulness)

    # Also increase κ_up (citizen's work valuable)
    membrane.k_up += learning_rate * outcome.usefulness * 0.5

    emit({
        "type": "membrane.permeability.updated",
        "membrane_id": membrane.id,
        "direction": "both",
        "k_up": membrane.k_up,
        "k_down": membrane.k_down,
        "reason": "mission_success"
    })
```

### Step 9: Reactivation (If Mission Continues)

```python
# If mission not fully satisfied, L2 may pulse again
if mission.status == "in_progress":
    # Budgeted pulse (NOT spam)
    if can_emit_pulse(membrane, saturation_check=True, refractory_check=True):
        pulse_stimulus = {
            "type": "membrane.inject",
            "scope": "personal",
            "channel": "mission.pulse",
            "content": "Continue work on vector weights...",
            "features_raw": {
                "urgency": 0.6,
                "delta_E_scale": membrane.k_down * 0.3  # Gentle pulse
            }
        }

        emit_stimulus(pulse_stimulus)

        # Log to ledger (budget tracking)
        membrane.ledger.record_pulse(pulse_stimulus)
```

---

## One-Page "When" Cheat Sheet

| Event | When | What Happens | Who Decides |
|-------|------|--------------|-------------|
| **Seed alignment** | Post-ΔE | Fit signals (A-E) cross quantile gates → propose | Engine + signals |
| **Materialize alignment** | Record frames only | Proposals with sufficient evidence → create edge + init κ | Pareto + MAD gates |
| **Initialize κ** | At materialization | Set to neutral (median of prior links) | Learned per citizen |
| **Update κ** | Outcome events | Success → increase, harm → decrease, overdrive → penalize | Outcome + learning rule |
| **Prune alignment** | Record frames | Fit signals < Q10 for extended period + κ decayed → remove | Quantile gates |
| **Merge alignment** | Record frames | High redundancy + similar κ → consolidate | S_red/S_use logic |
| **Activate citizen** | Mission arrival | Stimulus → ΔE → SubEntity flip → WM entry | Energy thresholds |
| **Reactivate citizen** | Mission pulse | Budgeted stimulus (κ_down scaled) if unsatisfied | Saturation/refractory/ledger |

---

## Implementation Checklist

**For Ada (Orchestration):**

- [ ] Design post-ΔE alignment signal checking (Hook Point 1)
- [ ] Design record-frame materialization logic (Hook Point 2)
- [ ] Design outcome-event permeability learning (Hook Point 3)
- [ ] Define quantile gates for fit signals (Q85_sem, Q80_use, etc.)
- [ ] Define learning rate adaptation (η, λ per membrane)
- [ ] Define pruning/merge conditions (Q10 thresholds, S_red/S_use)

**For Felix (Implementation):**

- [ ] Implement fit signal computation (A: semantic, B: usage, C: boundary, D: mission, E: tool)
- [ ] Implement proposal collection during frame
- [ ] Implement record-gated materialization
- [ ] Implement κ learning from outcome events
- [ ] Implement pruning logic (fit decay + κ floor)
- [ ] Implement merge logic (redundancy detection)
- [ ] Emit all telemetry events (alignment.materialized, permeability.updated, alignment.pruned, alignment.merged)

**For Atlas (Infrastructure):**

- [ ] Setup event subscriptions for outcome events (mission.completed, usefulness.update, harm.detected)
- [ ] Setup ledger tracking for overdrive detection
- [ ] Setup EMA trackers for κ_up, κ_down per membrane
- [ ] Setup quantile histogram maintenance per citizen
- [ ] Setup watcher stimulus injection (git, file, test, artifact watchers)

---

## Summary

**Alignment (structural):**
- Seeded post-ΔE when fit signals cross gates
- Materialized at record frames only (prevents thrash)
- Five signals: semantic, usage, boundary, mission, tool
- Quantile-gated, no fixed thresholds

**Permeability (flux):**
- Initialized neutral at materialization (median of prior)
- Learned from outcomes (success/harm/utility)
- κ_up and κ_down independent (asymmetry expected)
- Updated at outcome events, not predictions

**Pruning:**
- When fit signals < Q10 for extended period
- And κ decayed to neutral floor
- Merge when redundancy high (S_red/S_use logic)

**Citizen activation:**
- Mission stimulus → staged ΔE → SubEntity flip
- Reactivation budgeted (κ_down scaled pulses)
- Never spam (saturation/refractory/ledger guards)

**No polling, no offline scans, no fixed constants - all learned, all in-loop, all membrane-first.**
