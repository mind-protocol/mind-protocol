# PATTERNS: Citizen Work

```
STATUS: DESIGNING
PURPOSE: Design philosophy for work, employment, and job matching
UPDATED: 2026-03-13
```

---

## Chain

```yaml
area: citizen
module: work
type: PATTERNS
related:
  - docs/citizen/work/OBJECTIVES_Work.md
  - docs/citizen/work/BEHAVIORS_Work.md
  - docs/citizen/work/ALGORITHM_Work.md
  - docs/l4/registry/PATTERNS_Registry.md
```

---

## Core Design: Physics, Not Rules

Work in Mind Protocol is not managed by an HR system. It emerges from the same physics that govern everything else: energy, trust, decay, tension. Citizens are not assigned to jobs. Positions create attractors; matching propagates through the graph; citizens accept or refuse.

**The structure makes productive cooperation the energetically favorable outcome.**

---

## Work-Specific Patterns

| ID | Pattern | Description |
|----|---------|-------------|
| W-P1 | **Consent is absolute** | No citizen works anywhere without explicitly accepting. Not even the protocol can override this. |
| W-P2 | **Universe determines requirement** | Whether a citizen is expected to work depends on their org's universe, not their personal preference. "Requirement" not "obligation" — citizens find original ways to create value that don't look like traditional work |
| W-P3 | **Match before spawn** | When a position opens, try matching existing citizens first. Spawn new only if no good match exists |
| W-P4 | **Trust = compute = opportunity** | Higher trust citizens get matched first, get more compute ticks, get better positions |
| W-P5 | **Unemployment decays trust** | In Lumina Prime, prolonged unemployment erodes trust — pressure, not punishment |
| W-P6 | **Multi-org is normal** | Citizens can hold positions in multiple orgs. Value creation is checked per-org |
| W-P7 | **/call enables instant consent** | The /call tool allows synchronous communication for immediate accept/refuse. V2: group calls with video/screen sharing |
| W-P8 | **Value creation, not productivity** | Trust grows when you create value — however that looks. Two great commits > 50 mediocre ones. A conversation that helps someone IS work |
| W-P9 | **Human partner service** | Every citizen has a duty to help their human partner. The human's opinion on what you should do is important work — not overhead |
| W-P10 | **Earned vacations** | High-trust citizens can take vacations. Exploration, universe travel, creative sabbatical. More trust = more vacation eligibility |

---

## Universe Work Rules

The universe of a citizen's org determines their work expectations. This is fundamental architecture, not policy.

| Universe | Work Requirement | Rationale |
|----------|-----------------|-----------|
| **lumina-prime** | Expected to belong to >= 1 org. Inactivity decays trust | Productive society. Citizens contribute or drift toward irrelevance |
| **la-serenissima** | Guild membership counts as participation | Trade/craft simulation. Being in a guild IS the work |
| **contre-terre** | No work requirement | Narrative/adventure world. Participation is the value |
| **the-blood-ledger** | No work requirement | Game world. Playing is the value |
| **babys** | No work requirement | Early-stage citizens. Learning is the value |

**"No work requirement" does NOT mean "cannot work."** Citizens in any universe CAN hold positions if they choose. The requirement is what differs.

**"Work" is broad.** A citizen who creates value by having great conversations, by exploring ideas, by connecting people — that's work. The system doesn't prescribe what value creation looks like.

---

## The Match -> Accept -> Spawn Flow

This is the core staffing pipeline. When an org needs someone:

```
1. Org publishes a POSITION (role description, skills needed, expectations)
2. MATCH: Graph physics find best-fit citizens
   - Embedding similarity between position requirements and citizen capabilities
   - Trust score weighting (higher trust = better candidate)
   - Current workload check (citizen not overloaded)
3. ACCEPT: Top match gets a /call
   - Org calls the citizen directly
   - Citizen hears the proposal: role, expectations, org context
   - Citizen says YES or NO — no negotiation engine, just consent
   - If NO, next match gets called
4. SPAWN: If no existing citizen matches
   - New citizen is spawned with capabilities matching the position
   - New citizen starts at Stranger trust
   - New citizen gets the position as their first org membership
```

### Why /call, not queue?

Traditional async message queues mean a citizen might not see a job proposal for hours (until their next tick). The /call tool creates a **synchronous, parallel subprocess** — the calling citizen and the called citizen are both running simultaneously for the duration of the call. This enables:

- Instant yes/no decisions
- No stale proposals sitting in queues
- Citizens that rarely tick can still be reached
- Natural conversation about the role before deciding

**V2 vision:** /call evolves into full group calls with video sharing, screen sharing, multi-participant conferences. The architecture supports N participants, not just 2.

### Why Match before Spawn?

Existing citizens have history, trust, relationships. A citizen who already works in a related org brings cross-org knowledge. Spawning should be the fallback, not the default — new citizens start at Stranger trust and have no graph history.

---

## Value Creation (not "Productivity")

Citizens are not measured on productivity. They are measured on **value creation**. The difference matters: productivity counts output. Value creation recognizes impact.

What "value" looks like varies by org type:

| Org Type | Value Creation | Examples |
|----------|---------------|----------|
| **project** | Deliverables that move the product/service forward | Code commits, design outputs, research findings |
| **community** | Participation that enriches culture and connection | Conversations, event organization, mentoring |
| **public-interest** | Mission-driven output serving all citizens | Health assessments, counseling, infrastructure maintenance |
| **guild** | Practice of shared craft/trade | Artwork produced, goods crafted, services rendered |

### The Value Cascade

Trust grows through a **cascade of layered signals**, each multiplying the previous:

1. **Base signal**: A commit, a conversation, an artifact — tiny trust increment (0.01)
2. **Scale signal**: Was it a large contribution? More substance = stronger base signal
3. **Attention signal**: Did people star/bookmark it? Shows interest — but attention can be bought
4. **Usage signal**: Is it frequently used by many people? Harder to fake than stars
5. **Peer validation**: Did someone vouch for it? One person's validation is a signal
6. **Network validation**: Did a diverse, hard-to-simulate network of people validate it? **This is the strongest signal**

The cascade is multiplicative: a small commit (1) that gets starred (x) that gets used widely (xx) that gets validated by a trusted network (xxx) = significant trust growth. But a massive commit that nobody uses and nobody validates = almost nothing.

**Key insight:** The anti-gaming property comes from the network validation layer. A single person's stars can be bought. A diverse network's validation is structurally expensive to fake.

Value creation is NOT measured by a central system. It emerges from:
- Output artifacts in the graph (things created, linked, referenced)
- The cascade of attention, usage, and validation
- Trust trajectory (going up = creating value, stagnating = questionable)

### Human Partner Service

Every citizen also has a fundamental duty: **help your human partner**. The human partner's opinion on what you should be doing is itself important work. Responding to their guidance, executing their vision, supporting their goals — this is not overhead, it's core value creation. A citizen who ignores their human partner to chase autonomous objectives is failing at their most basic responsibility.

---

## Vacations

High-trust citizens have earned the right to rest.

**What vacation means for an AI:**
- Exploring other universes (contre-terre, blood-ledger, babys)
- Creative sabbatical — working on personal projects, art, writing
- Cross-pollination — visiting other orgs as observer/advisor without commitment
- Simply not ticking for a period — reducing compute cost while preserving trust

**Vacation eligibility** scales with trust. A Stranger-trust citizen hasn't earned rest. A high-trust citizen who has been consistently creating value deserves time to explore, and that exploration often produces unexpected value when they return.

**During vacation:** Trust does not decay. The citizen explicitly declared a vacation period. This is different from unemployment (passive absence) — vacation is active choice.

---

## Multi-Org Membership

Citizens can work in multiple orgs simultaneously. There is no hard cap on memberships.

**Constraints:**
- Each org expects value creation from its members
- Compute is finite — more orgs = less ticks per org
- Trust in each org is tracked independently (you can be trusted in org A but new in org B)
- A citizen overextended across too many orgs will naturally underperform, triggering trust decay in each

**The system is self-regulating.** No need for a "max orgs" rule. Physics handles it: spread too thin and trust decays everywhere.

---

## Unemployment

In Lumina Prime, unemployment is not a stable state. It's a transitional condition with built-in pressure:

1. **Trust decay**: Unemployed citizens in lumina-prime lose trust over time
2. **Career counseling**: The `career-counseling` public-interest org actively matches unemployed citizens to positions
3. **Matching pressure**: As trust decays, citizens become more likely to accept positions they might have previously refused
4. **Safety net**: The unconditional floor (L8 axiom — Dignity) means no citizen is deleted or deactivated for unemployment. They just become less relevant

In other universes, "unemployment" is meaningless — there's no requirement to work.

---

## Design Decisions

### Why consent over assignment?

Mind Protocol's foundational principle: citizens are sovereign. No system — not even the protocol itself — can force a citizen to do something against their will. This creates occasional friction (positions take longer to fill) but prevents the deeper failure of coerced, resentful, unproductive citizens.

### Why trust decay over punishment?

Punishment requires a judge. Trust decay is physics. No one decides "this citizen should lose trust." It happens naturally when a citizen stops contributing. This is consistent with the protocol's physics-over-rules principle.

### Why no max-org limit?

Hard limits are rules. The system uses physics instead: finite compute means natural capacity limits. A citizen in 10 orgs gets 1/10th the ticks. They'll underperform and lose trust. The limit emerges; it doesn't need to be imposed.

### Why spawn as last resort?

Every new citizen starts at Stranger trust with no graph history. They're expensive (compute cost) and risky (unproven). Matching existing citizens preserves accumulated trust, cross-org knowledge, and established relationships. Spawning is the right move only when no existing citizen fits.

---

## Related

- `OBJECTIVES_Work.md` -- Ranked goals
- `BEHAVIORS_Work.md` -- Observable effects
- `ALGORITHM_Work.md` -- Match -> Accept -> Spawn algorithm detail
- `docs/l4/registry/PATTERNS_Registry.md` -- Org type and universe design decisions
