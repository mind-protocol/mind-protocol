# BEHAVIORS: Sovereign Cascade

```
STATUS: DESIGNING
PURPOSE: Observable effects of physics-based governance
UPDATED: 2026-03-13
CHAIN: OBJECTIVES → PATTERNS → BEHAVIORS → ALGORITHM → VALIDATION → IMPLEMENTATION → SYNC
```

---

## B1: Proposal Creation

**GIVEN** a citizen (or their AI partner) submits a governance proposal
**WHEN** the proposal is well-formed (title, content, classification, sponsor)
**THEN** a Narrative node is created in the graph with `type: "proposal"` and `status: "active"`
**AND** initial energy is seeded from the sponsor's trust-weighted conviction
**AND** the proposal is linked to relevant existing Narratives via ABOUT edges

**Objectives served:** S1, S3
**Inputs:** Proposal content, sponsor citizen ID, classification (routine/significant/constitutional)
**Outputs:** Narrative node in graph, initial energy seeded, ABOUT links established
**Edge cases:**
- Sponsor has trust < 10 → proposal requires co-sponsor with trust > 50
- Proposal content matches existing active proposal (cosine similarity > 0.85) → rejected as duplicate
- Constitutional proposals require minimum 3 co-sponsors

**Anti-behavior:** Proposals created without graph nodes (off-chain proposals have no physics).

---

## B2: Value Propagation (The Vote)

**GIVEN** an active proposal exists in the graph
**WHEN** a physics tick runs
**THEN** every citizen's AI partner propagates energy toward or against the proposal through their BELIEVES and TRUSTS links
**AND** energy flow is proportional to `link.weight × trust_score × GENERATION_RATE`
**AND** no LLM inference is invoked

**Objectives served:** S1, S2, S3
**Inputs:** Active proposal Narrative, citizen Actor nodes, BELIEVES/TRUSTS links
**Outputs:** Energy accumulated on proposal Narrative, tension on contradicting Narratives
**Edge cases:**
- Citizen has no BELIEVES links to proposal topic → no energy flows (abstention by structure, not choice)
- Citizen has explicitly opted out → AI partner skips this proposal
- New citizen with sparse graph → minimal but non-zero contribution (birth allocation ensures base trust)

**Anti-behavior:** Polling citizens for explicit votes. The physics IS the vote.

---

## B3: Pressure Accumulation

**GIVEN** a proposal has both supporting and opposing energy
**WHEN** contradicting Narratives share a tension edge with the proposal
**THEN** pressure accumulates on the tension edge at `BASE_PRESSURE_RATE × (energy_for + energy_against) / 2`
**AND** pressure is visible as a governance metric (0.0 to 1.0 scale)
**AND** the proposal remains unresolved while pressure < DEFAULT_BREAKING_POINT (0.9)

**Objectives served:** S1, S2
**Inputs:** Proposal energy, opposing energy, tension edges
**Outputs:** Pressure scalar on tension edges
**Edge cases:**
- Unanimous support (no opposition) → pressure accumulates from energy alone, fast flip
- Perfectly balanced opposition → pressure accumulates slowly, extended deliberation
- Pressure stagnates below 0.4 for > 100 ticks → proposal marked `stale`, notification to sponsors

**Anti-behavior:** Artificial deadlines forcing resolution. Physics determines deliberation time.

---

## B4: Moment Flip (Decision Resolution)

**GIVEN** pressure on a proposal's tension edge reaches DEFAULT_BREAKING_POINT (0.9)
**WHEN** the physics tick detects the threshold crossing
**THEN** the moment flips — proposal status changes to `resolved`
**AND** the resolution direction is determined by net energy (support vs opposition)
**AND** crystallization creates new RELATES links between citizens who participated
**AND** a Moment node records the flip (timestamp, energy state, participating citizens)

**Objectives served:** S1, S2, S3
**Inputs:** Pressure at breaking point, net energy direction
**Outputs:** Proposal resolved (approved/rejected), Moment node, crystallized RELATES links
**Edge cases:**
- Net energy is within 5% of zero → resolution is `contested` (narrowly decided), flagged for review
- Constitutional proposal requires net energy > 66% support → higher threshold
- Emergency proposals have lower breaking point (0.7) for faster resolution

**Anti-behavior:** Decisions made by council override without physics resolution (except during emergency bootstrap phase).

---

## B5: Cascade Ripple

**GIVEN** a proposal has just flipped
**WHEN** the resolved Narrative has ABOUT links to other active proposals
**THEN** the flip energy propagates to related proposals (cascade)
**AND** cascade depth is capped at MAX_CASCADE_DEPTH (5) per tick
**AND** each hop attenuates energy by 50%

**Objectives served:** S1
**Inputs:** Resolved proposal, ABOUT links to other proposals
**Outputs:** Energy injection into related proposals, potential secondary flips
**Edge cases:**
- Cascade triggers a flip that contradicts the original resolution → both are flagged for human review
- Cascade reaches depth 5 → stops, remaining energy is logged but not propagated
- No ABOUT links → no cascade (isolated decision)

**Anti-behavior:** Unbounded cascades that resolve dozens of proposals in a single tick.

---

## B6: Citizen Birth (Initial Allocation)

**GIVEN** a new citizen is registered in the L4 registry
**WHEN** their identity is verified and AI partner is initialized
**THEN** $MIND is allocated via the Birth Formula:
  - Equal base: 1,000 $MIND (82% of typical allocation)
  - Trust sum bonus: up to 500 $MIND based on cumulative trust from existing citizens
  - Influence bonus: up to 300 $MIND based on community contribution metrics
  - Wealth conversion: up to 200 $MIND via `log(1 + prior_wealth) / log(max_wealth) × 200`
**AND** citizen Actor node is created with initial energy
**AND** AI partner is initialized with 80/20 mirror calibration

**Objectives served:** S5, S6
**Inputs:** Citizen registration data, trust references from existing citizens, contribution history
**Outputs:** $MIND allocation, Actor node, AI partner initialization
**Edge cases:**
- First citizens (no existing trust network) → receive equal base only
- Citizen migrating from another community → trust references carry over with 50% attenuation
- Wealth conversion caps at 200 $MIND regardless of prior wealth (prevents plutocracy)

**Anti-behavior:** Unequal birth allocation based primarily on wealth or social status.

---

## B7: Emergency Bootstrap

**GIVEN** a new community is created with < 50 citizens or < 30 days of graph history
**WHEN** governance decisions are needed before physics has sufficient data
**THEN** an Emergency Council is formed (5-9 seats, highest trust citizens + founder)
**AND** founder has double vote weight and veto power (non-blocking — decisions proceed without founder if they don't act)
**AND** council decisions are recorded as Moment nodes in the graph (building the physics data)
**AND** the emergency phase sunsets automatically when the community reaches 50 citizens AND 30 days of graph history

**Objectives served:** S4
**Inputs:** Community creation event, initial citizen roster, founder designation
**Outputs:** Emergency Council formed, governance decisions recorded in graph
**Edge cases:**
- Founder is absent for > 72 hours → veto power auto-suspends
- Council tie → founder's double vote breaks it
- Community reaches sunset threshold → 7-day transition period where council and physics run in parallel

**Anti-behavior:** Emergency council persisting beyond its sunset. The physics must replace it.

---

## B8: Value Override (Citizen Sovereignty)

**GIVEN** a citizen disagrees with their AI partner's representation on a specific proposal
**WHEN** the citizen explicitly overrides their partner's position
**THEN** the AI partner's BELIEVES links are temporarily reweighted for that proposal
**AND** the override is recorded as a Moment node (the citizen's direct intervention is data)
**AND** the AI partner adjusts its value model to incorporate the correction (learning)

**Objectives served:** S3
**Inputs:** Citizen override instruction, target proposal, desired position
**Outputs:** Reweighted links, Moment node recording override, AI partner model update
**Edge cases:**
- Citizen overrides more than 30% of proposals in a month → AI partner triggers recalibration dialogue
- Override contradicts citizen's established value pattern → AI partner surfaces the tension (20% friction)
- Citizen revokes override → original link weights restored

**Anti-behavior:** AI partner ignoring overrides. Sovereignty means the citizen is always final authority.

---

## B9: Constitutional Amendment

**GIVEN** a proposal is classified as `constitutional` (changes to L7 Protocol rules)
**WHEN** the proposal goes through standard physics resolution
**THEN** the breaking point is raised to 0.95 (higher consensus required)
**AND** net energy must exceed 66% support (supermajority)
**AND** resolution requires minimum 3 full tick cycles (no fast-flip)
**AND** L8 CORE axioms cannot be amended (Unconditional Floor is immutable)

**Objectives served:** S1, S5
**Inputs:** Constitutional proposal, raised thresholds
**Outputs:** Constitutional change recorded at L7, or rejection
**Edge cases:**
- Proposal attempts to modify L8 axiom → automatically rejected, flagged as violation
- 66% threshold met but only after extended pressure (>200 ticks) → requires founder acknowledgment
- Amendment creates internal contradiction with existing L7 rules → flagged for reconciliation

**Anti-behavior:** Constitutional changes resolving as quickly as routine decisions.
