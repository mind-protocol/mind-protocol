# ALGORITHM: Sovereign Cascade

```
STATUS: DESIGNING
PURPOSE: How governance decisions resolve through graph physics
UPDATED: 2026-03-13
CHAIN: OBJECTIVES → PATTERNS → BEHAVIORS → ALGORITHM → VALIDATION → IMPLEMENTATION → SYNC
```

---

## Overview

The Sovereign Cascade converts governance from a discrete event (voting) to a continuous process (energy propagation). Decisions resolve through the same L1 physics engine that governs cognition and social dynamics. The algorithm has 4 stages: Proposal Injection, Value Propagation, Pressure Resolution, and Cascade Ripple.

The physics tick runs every 5 seconds. A governance decision typically resolves in 10-50 ticks (50 seconds to 4 minutes). Constitutional amendments take longer by design (minimum 3 full cycles).

---

## Objectives and Behaviors This Algorithm Guarantees

- **B1:** Proposals become Narrative nodes with correct classification and initial energy
- **B2:** Every citizen's values propagate every tick without LLM inference
- **B3:** Pressure accumulates proportionally to conviction intensity
- **B4:** Moments flip deterministically when pressure exceeds threshold
- **B5:** Cascades propagate with bounded depth and attenuation
- **B6:** Birth formula allocates $MIND with target Gini < 0.05

---

## Data Structures

### Proposal (Narrative node, type: "proposal")

```
{
  node_type: "narrative",
  type: "proposal",
  id: "proposal:{uuid}",
  content: "{proposal full text}",
  synthesis: "{proposal summary for embedding}",
  status: "active" | "resolved" | "stale" | "contested" | "rejected",
  classification: "routine" | "significant" | "constitutional",
  energy: float [0, +inf),
  weight: float [0, +inf),
  sponsor_id: "actor:{citizen_id}",
  co_sponsors: ["actor:{citizen_id}", ...],
  resolution: null | "approved" | "rejected" | "contested",
  created_tick: int,
  resolved_tick: int | null
}
```

### Conviction Link (link from Actor to Proposal)

```
{
  source: "actor:{citizen_id}",
  target: "proposal:{uuid}",
  type: "BELIEVES",
  polarity: float [-1, +1],    // -1 = strong opposition, +1 = strong support
  weight: float [0, +inf),      // accumulated conviction strength
  energy: float [0, +inf),      // current energy flowing through link
  trust_factor: float [0, 1],   // atan(trust_score / 50) / (π/2) — normalized
}
```

### Tension Edge (between contradicting proposals or proposal-vs-existing-narrative)

```
{
  source: "narrative:{id}",
  target: "proposal:{uuid}",
  type: "TENSION",
  pressure: float [0, 1],
  breaking_point: float,         // 0.9 routine, 0.95 constitutional
  energy_for: float,
  energy_against: float
}
```

### Resolution Moment (Moment node, created on flip)

```
{
  node_type: "moment",
  type: "governance_resolution",
  id: "moment:{uuid}",
  content: "{resolution summary}",
  synthesis: "{resolution embedding text}",
  proposal_id: "proposal:{uuid}",
  resolution: "approved" | "rejected" | "contested",
  net_energy: float,
  pressure_at_flip: float,
  participating_actors: int,
  tick_created: int,
  cascade_depth: int              // 0 = primary, 1-5 = cascade
}
```

---

## Algorithm

### Stage 1: Proposal Injection

```
FUNCTION inject_proposal(content, sponsor_id, classification, co_sponsors=[]):

  1. Validate sponsor trust:
     trust = get_trust_score(sponsor_id)
     IF classification == "routine" AND trust < 10:
       REQUIRE at least 1 co_sponsor with trust > 50
     IF classification == "constitutional":
       REQUIRE at least 3 co_sponsors

  2. Check for duplicates:
     embedding = compute_embedding(content)
     FOR each active_proposal in graph:
       IF cosine_similarity(embedding, active_proposal.synthesis_embedding) > 0.85:
         REJECT as duplicate

  3. Create Narrative node:
     proposal = create_node(
       node_type="narrative", type="proposal",
       content=content, status="active",
       classification=classification,
       energy=0, weight=0.1
     )

  4. Seed initial energy from sponsor:
     initial_energy = trust × GENERATION_RATE × sponsor.weight
     proposal.energy = initial_energy
     create_link(sponsor_id, proposal.id, type="BELIEVES", polarity=+1, weight=trust/100)

  5. Establish ABOUT links:
     FOR each existing_narrative in graph WHERE cosine_similarity > 0.5:
       create_link(proposal.id, existing_narrative.id, type="ABOUT")

  6. IF contradicting narratives found (similarity > 0.5 AND polarity < -0.3):
     create_tension_edge(existing_narrative, proposal, breaking_point=threshold(classification))

  RETURN proposal.id
```

### Stage 2: Value Propagation (Per Tick)

This runs every tick (5 seconds) as part of the standard physics tick. No separate governance engine.

```
FUNCTION propagate_governance(tick):

  active_proposals = get_nodes(type="proposal", status="active")

  FOR each proposal in active_proposals:

    // Phase 2a: Direct conviction from citizens
    FOR each citizen in get_all_actors(type="citizen"):

      // Find conviction through existing value links
      conviction = compute_conviction(citizen, proposal)
      // conviction uses existing BELIEVES links — no new computation

      IF conviction.magnitude > 0:
        trust_factor = atan(citizen.trust_score / 50) / (π / 2)
        energy_flow = conviction.magnitude × trust_factor × GENERATION_RATE × citizen.weight

        // Direction: support or oppose
        IF conviction.polarity > 0:
          proposal.energy_for += energy_flow
        ELSE:
          proposal.energy_against += energy_flow

        // Update conviction link
        link = get_or_create_link(citizen.id, proposal.id, type="BELIEVES")
        link.energy += energy_flow × link.weight
        link.polarity = conviction.polarity

    // Phase 2b: Propagation through TRUSTS links
    // Citizens who trust supporters are more likely to support
    FOR each trust_link in get_links(type="TRUSTS"):
      source_conviction = get_link(trust_link.source, proposal.id)
      IF source_conviction EXISTS AND source_conviction.energy > 0:
        propagated = source_conviction.energy × trust_link.weight × BACKFLOW_RATE
        target_link = get_or_create_link(trust_link.target, proposal.id)
        target_link.energy += propagated × 0.5  // attenuated — trust propagation, not imposition
```

### Stage 3: Pressure Resolution

```
FUNCTION resolve_pressure(tick):

  FOR each tension_edge in get_links(type="TENSION"):
    proposal = get_node(tension_edge.target)

    IF proposal.status != "active":
      CONTINUE

    // Accumulate pressure
    combined_energy = (proposal.energy_for + proposal.energy_against) / 2
    pressure_increment = BASE_PRESSURE_RATE × combined_energy
    tension_edge.pressure += pressure_increment

    // Check for stale proposals
    IF tension_edge.pressure < 0.4 AND (tick - proposal.created_tick) > 100:
      proposal.status = "stale"
      notify_sponsors(proposal)
      CONTINUE

    // Check for flip
    IF tension_edge.pressure >= tension_edge.breaking_point:

      // Determine resolution direction
      net_energy = proposal.energy_for - proposal.energy_against
      total_energy = proposal.energy_for + proposal.energy_against
      support_ratio = proposal.energy_for / total_energy IF total_energy > 0 ELSE 0.5

      // Classification-specific thresholds
      IF proposal.classification == "constitutional" AND support_ratio < 0.66:
        proposal.resolution = "rejected"
      ELIF support_ratio > 0.55:
        proposal.resolution = "approved"
      ELIF support_ratio < 0.45:
        proposal.resolution = "rejected"
      ELSE:
        proposal.resolution = "contested"  // narrow margin, flagged for review

      proposal.status = "resolved"
      proposal.resolved_tick = tick

      // Create Resolution Moment
      moment = create_node(
        node_type="moment", type="governance_resolution",
        proposal_id=proposal.id,
        resolution=proposal.resolution,
        net_energy=net_energy,
        pressure_at_flip=tension_edge.pressure,
        tick_created=tick,
        cascade_depth=0
      )

      // Crystallize RELATES links between participating citizens
      participants = get_actors_linked_to(proposal.id)
      FOR each pair (a, b) in participants:
        IF NOT exists_link(a, b, type="RELATES"):
          create_link(a, b, type="RELATES", weight=CRYSTALLIZATION_WEIGHT)

      // Trigger cascade
      cascade(proposal, moment, depth=1, tick=tick)
```

### Stage 4: Cascade Ripple

```
FUNCTION cascade(resolved_proposal, trigger_moment, depth, tick):

  IF depth > MAX_CASCADE_DEPTH:  // 5
    RETURN

  // Find related active proposals
  related = get_linked_proposals(resolved_proposal.id, link_type="ABOUT", status="active")

  FOR each related_proposal in related:
    // Inject cascade energy (attenuated by 50% per hop)
    cascade_energy = trigger_moment.net_energy × (0.5 ^ depth)

    IF cascade_energy.magnitude < COLD_THRESHOLD:
      CONTINUE  // too weak to matter

    // Energy direction follows resolution: approved → support, rejected → oppose
    IF resolved_proposal.resolution == "approved":
      related_proposal.energy_for += abs(cascade_energy)
    ELSE:
      related_proposal.energy_against += abs(cascade_energy)

    // Check if cascade triggers a flip on the related proposal
    tension = get_tension_edge(related_proposal)
    IF tension AND tension.pressure >= tension.breaking_point:
      // Recursive resolution
      resolve_and_cascade(related_proposal, depth + 1, tick)
```

---

## Key Decisions

### Decision 1: Conviction Computation

**How does the physics know a citizen supports or opposes a proposal?**

Through existing graph structure. The citizen's BELIEVES links point to Narratives that represent their values. The proposal is also a Narrative. Conviction is computed as:

```
FUNCTION compute_conviction(citizen, proposal):

  // Get citizen's value Narratives
  beliefs = get_links(citizen.id, type="BELIEVES")

  // Compute alignment between each belief and proposal
  total_alignment = 0
  total_weight = 0

  FOR each belief_link in beliefs:
    belief_narrative = get_node(belief_link.target)
    similarity = cosine_similarity(belief_narrative.synthesis_embedding, proposal.synthesis_embedding)

    // Polarity: belief_link.polarity tells us if citizen affirms or rejects this narrative
    alignment = similarity × belief_link.polarity × belief_link.weight
    total_alignment += alignment
    total_weight += belief_link.weight

  IF total_weight == 0:
    RETURN { magnitude: 0, polarity: 0 }  // no conviction

  normalized = total_alignment / total_weight
  RETURN {
    magnitude: abs(normalized),
    polarity: sign(normalized)   // +1 support, -1 oppose
  }
```

**Key insight:** This is a dot product in embedding space, weighted by trust. Pure math. No LLM.

### Decision 2: Trust Factor Normalization

```
trust_factor = atan(trust_score / 50) / (π / 2)
```

| Trust Score | Trust Factor | Governance Weight |
|-------------|-------------|-------------------|
| 0 | 0.00 | No governance weight |
| 10 | 0.13 | Minimal |
| 25 | 0.30 | Emerging |
| 50 | 0.55 | Substantial |
| 75 | 0.71 | Strong |
| 90 | 0.80 | Very strong |
| 100 | 0.84 | Maximum (but diminishing returns) |

The atan curve ensures:
- Zero trust → zero governance weight
- Moderate trust → meaningful voice
- High trust → strong but bounded influence (no single citizen dominates)

### Decision 3: Breaking Point by Classification

| Classification | Breaking Point | Support Threshold | Min Duration |
|----------------|---------------|-------------------|-------------|
| Routine | 0.9 | > 50% | None |
| Significant | 0.9 | > 55% | 10 ticks |
| Constitutional | 0.95 | > 66% | 3 full cycles |
| Emergency (bootstrap) | 0.7 | > 50% | None |

---

## Data Flow

```
Citizen Values (BELIEVES links)
    │
    ▼
Physics Tick (every 5s)
    │
    ├─► Conviction Computation (embedding similarity × link weight × polarity)
    │       │
    │       ▼
    ├─► Energy Flow (conviction × trust_factor × GENERATION_RATE)
    │       │
    │       ▼
    ├─► Trust Propagation (TRUSTS links amplify aligned conviction)
    │       │
    │       ▼
    ├─► Pressure Accumulation (energy_for + energy_against → pressure)
    │       │
    │       ▼
    ├─► Threshold Check (pressure >= breaking_point?)
    │       │
    │       ├─ NO → continue accumulating
    │       │
    │       └─ YES → Moment Flip
    │               │
    │               ├─► Resolution (approved/rejected/contested)
    │               ├─► Crystallization (RELATES links between participants)
    │               └─► Cascade Ripple (energy → related proposals, depth ≤ 5)
    │
    ▼
Graph State Updated (all nodes, links, energies persisted)
```

---

## Birth Formula Algorithm

```
FUNCTION compute_birth_allocation(citizen, existing_citizens):

  // Component 1: Equal base (dominant)
  base = 1000  // $MIND

  // Component 2: Trust bonus
  trust_sum = 0
  FOR each existing in existing_citizens:
    trust_link = get_link(existing.id, citizen.id, type="TRUSTS")
    IF trust_link:
      trust_sum += trust_link.weight
  trust_bonus = min(500, trust_sum × 10)  // cap at 500

  // Component 3: Influence bonus
  influence = citizen.influence_score  // from L4 registry
  max_influence = max(c.influence_score for c in existing_citizens) OR 1
  influence_bonus = min(300, (influence / max_influence) × 300)

  // Component 4: Wealth conversion (logarithmic, minimal)
  prior_wealth = citizen.prior_wealth OR 0  // from migration data
  max_wealth = max(c.prior_wealth for c in existing_citizens) OR 1
  IF prior_wealth > 0 AND max_wealth > 0:
    wealth_bonus = min(200, log(1 + prior_wealth) / log(1 + max_wealth) × 200)
  ELSE:
    wealth_bonus = 0

  total = base + trust_bonus + influence_bonus + wealth_bonus

  RETURN {
    total: total,
    breakdown: {
      base: base,
      trust_bonus: trust_bonus,
      influence_bonus: influence_bonus,
      wealth_bonus: wealth_bonus
    }
  }
```

**Target distribution:** Base represents ~82% of median allocation. Gini target < 0.05.

---

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| Conviction computation per citizen per proposal | O(B × E) | O(1) |
| Value propagation per tick (all citizens, all proposals) | O(C × P × B) | O(C × P) |
| Trust propagation per tick | O(T × P) | O(T) |
| Pressure resolution per tick | O(P) | O(1) |
| Cascade ripple | O(P × D) | O(D) |
| Birth formula | O(C) | O(1) |

Where: C = citizens, P = active proposals, B = beliefs per citizen, T = trust links, E = embedding dim, D = max cascade depth (5)

**At Venice scale (152 citizens, ~10 active proposals, ~20 beliefs/citizen):**
- Per tick: ~30,400 conviction computations + ~1,500 trust propagations = milliseconds
- A full governance resolution in ~50 ticks = ~4 minutes of wall time, ~0 cost

**At 10,000 citizens:** Per tick: ~2M computations. Still under 1 second on modern hardware (embedding similarity is vectorizable).

---

## Interactions

| Module | What We Call | What We Receive |
|--------|-------------|-----------------|
| L1 Physics Engine | `tick()` — our propagation runs inside the standard tick | Tick results, energy states |
| FalkorDB Graph | `GRAPH.QUERY` — all node/link CRUD | Graph state |
| $MIND Token (Solana) | `transfer()` — birth allocation minting | Transaction confirmation |
| L4 Registry | `get_citizen()` — trust scores, influence | Citizen metadata |
| Membrane | `validate_access()` — proposal submission | Access decisions |
| AI Partner (L1) | `get_beliefs()` — citizen value graph | BELIEVES links with weights |
