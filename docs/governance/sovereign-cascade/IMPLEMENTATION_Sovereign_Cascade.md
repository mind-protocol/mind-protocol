# IMPLEMENTATION: Sovereign Cascade

```
STATUS: DESIGNING
PURPOSE: Where the code lives and how governance integrates with existing infrastructure
UPDATED: 2026-03-13
CHAIN: OBJECTIVES → PATTERNS → BEHAVIORS → ALGORITHM → VALIDATION → IMPLEMENTATION → SYNC
```

---

## Code Structure

The Sovereign Cascade is NOT a separate service. It runs inside the existing L1 physics tick. Governance is physics — the implementation extends the tick with governance-specific phases.

```
mind-protocol/
├── docs/governance/sovereign-cascade/   ← you are here (doc chain)
├── graph/governance/                    ← governance graph operations
│   ├── proposal_injection.py           ← B1: Create proposal Narrative nodes
│   ├── conviction_computation.py       ← Stage 2: Citizen value → proposal alignment
│   ├── pressure_resolution.py          ← Stage 3: Pressure accumulation and flip
│   ├── cascade_ripple.py               ← Stage 4: Post-flip cascade propagation
│   └── birth_formula.py               ← B6: New citizen $MIND allocation
│
ngram/engine/physics/                    ← L1 physics engine (existing)
├── tick_v1_2.py                        ← Main tick loop — governance phases plug in here
├── constants.py                        ← Add governance constants (breaking points, cascade depth)
├── flow.py                             ← Energy flow mechanics (reused for conviction)
├── completion.py                       ← Moment flip (extended for governance resolution)
└── crystallization.py                  ← Post-flip link creation (reused for RELATES)
│
mind-platform/                           ← L3: Community-specific thresholds
├── templates/governance/
│   └── sovereign_cascade_config.yaml   ← Default thresholds communities can customize
│
mind-mcp/                                ← L1: Citizen-facing membrane tools
├── tools/governance/
│   ├── propose.py                      ← MCP tool: submit governance proposal
│   ├── override.py                     ← MCP tool: citizen overrides AI partner position
│   └── status.py                       ← MCP tool: query proposal status and pressure
```

---

## Design Patterns

### Pattern: Physics Extension (not Plugin)

Governance phases run INSIDE the tick loop, between existing phases. Not as a separate cron or service.

```python
# In tick_v1_2.py (conceptual extension)
def tick(graph):
    generation(graph)           # Phase 1: Actor energy generation
    moment_draw(graph)          # Phase 2: Moment draws from actors
    governance_propagation(graph)  # Phase 2.5: Governance conviction flow  ← NEW
    moment_flow(graph)          # Phase 3: Active moment energy flow
    moment_interaction(graph)   # Phase 4: Support/contradict between moments
    governance_resolution(graph)   # Phase 4.5: Pressure check and flip  ← NEW
    narrative_backflow(graph)   # Phase 5: Link energy backflow
    link_cooling(graph)         # Phase 6: Energy drain and weight growth
    completion(graph)           # Phase 7: Moment completion
    rejection(graph)            # Phase 8: Moment rejection
    cascade_check(graph)        # Phase 8.5: Governance cascade  ← NEW
```

**Why:** Governance energy interacts with cognitive energy. A citizen who is stressed (high fear_anger axis) should have different conviction dynamics than a calm one. Running governance inside the same tick means emotional state naturally influences governance — which is how real politics works.

### Pattern: L4 = Graph (from L4 Protocol Patterns)

All governance state lives in the graph. No separate governance database, API, or service.

- Proposals are Narrative nodes (type: "proposal")
- Convictions are BELIEVES links
- Tensions are TENSION links
- Resolutions are Moment nodes (type: "governance_resolution")
- Birth allocations are recorded as Moment nodes (type: "citizen_birth")

### Pattern: Membrane Access (from L4 Protocol Patterns)

Citizens interact with governance through membrane MCP tools, not direct graph queries.

```
Citizen → MCP Tool (propose/override/status) → Membrane → Graph
```

---

## Schema

### New Node Types

| Type | node_type | Properties | Constraints |
|------|-----------|------------|-------------|
| Proposal | narrative | classification, status, resolution, sponsor_id, energy_for, energy_against | Must have sponsor link |
| Governance Resolution | moment | proposal_id, resolution, net_energy, pressure_at_flip, cascade_depth | Created only on flip |
| Citizen Birth | moment | citizen_id, allocation_breakdown, birth_formula_version | Created once per citizen |

### New Link Types

| Type | source → target | Properties |
|------|-----------------|------------|
| CONVICTION | actor → narrative (proposal) | polarity, trust_factor, energy |
| TENSION | narrative → narrative (proposal) | pressure, breaking_point |
| ABOUT | narrative (proposal) → narrative | semantic_similarity |

### New Constants (added to `constants.py`)

```python
# Governance
BASE_PRESSURE_RATE = 0.001          # Pressure accumulation per tick
DEFAULT_BREAKING_POINT = 0.9        # Routine proposals
CONSTITUTIONAL_BREAKING_POINT = 0.95 # Constitutional amendments
EMERGENCY_BREAKING_POINT = 0.7      # Emergency bootstrap phase
MAX_CASCADE_DEPTH = 5               # Max cascade hops per tick
CASCADE_ATTENUATION = 0.5           # Energy reduction per cascade hop
CONTESTED_THRESHOLD = 0.05          # Net energy ratio below this = contested
STALE_THRESHOLD_TICKS = 100         # Ticks before proposal marked stale
CONSTITUTIONAL_SUPPORT_RATIO = 0.66  # Supermajority for constitutional changes
MIN_CONSTITUTIONAL_CYCLES = 3       # Minimum tick cycles for constitutional proposals

# Birth Formula
BIRTH_BASE = 1000                   # Equal base $MIND allocation
BIRTH_TRUST_MAX = 500               # Maximum trust bonus
BIRTH_TRUST_MULTIPLIER = 10         # Trust sum × multiplier = bonus
BIRTH_INFLUENCE_MAX = 300           # Maximum influence bonus
BIRTH_WEALTH_MAX = 200              # Maximum wealth conversion
```

---

## Entry Points

| Entry Point | Trigger | Handler |
|-------------|---------|---------|
| `propose` MCP tool | Citizen submits governance proposal | `proposal_injection.inject_proposal()` |
| `override` MCP tool | Citizen overrides AI partner position | Updates CONVICTION link polarity |
| `status` MCP tool | Citizen queries proposal status | Graph query for proposal + pressure |
| Physics tick (automatic) | Every 5 seconds | `governance_propagation()`, `governance_resolution()`, `cascade_check()` |
| Citizen registration | New citizen joins L4 registry | `birth_formula.compute_birth_allocation()` |
| Emergency council formation | Community created with < 50 citizens | Creates Emergency Council governance Narrative |

---

## Data Flow: Proposal Lifecycle

```
1. Citizen submits proposal
       │
       ▼
2. MCP Tool → Membrane validates → Graph: Create Narrative node
       │
       ▼
3. Initial energy seeded from sponsor's trust-weighted conviction
       │
       ▼
4. Physics tick runs (every 5s):
   ┌─── Conviction computation (embedding similarity, no LLM) ───┐
   │    For each citizen: values × trust_factor → energy flow     │
   │    Trust propagation: TRUSTS links amplify aligned views     │
   └──────────────────────────────────────────────────────────────┘
       │
       ▼
5. Pressure accumulates on TENSION edges
       │
       ├─ pressure < 0.4 after 100 ticks → STALE (notify sponsors)
       │
       ├─ pressure < breaking_point → continue accumulating
       │
       └─ pressure >= breaking_point → MOMENT FLIP
              │
              ├─► Resolution determined (approved/rejected/contested)
              ├─► Moment node created (audit record)
              ├─► RELATES links crystallized between participants
              └─► Cascade to related proposals (depth ≤ 5, 50% attenuation per hop)
```

---

## Data Flow: Birth Allocation

```
1. New citizen registered in L4 registry
       │
       ▼
2. Birth Formula computes allocation:
       base = 1000 $MIND
       + trust_bonus = min(500, sum(trust_from_existing) × 10)
       + influence_bonus = min(300, relative_influence × 300)
       + wealth_bonus = min(200, log(1 + wealth) / log(1 + max_wealth) × 200)
       │
       ▼
3. $MIND minted to citizen's wallet (Solana Token-2022)
       │
       ▼
4. Birth Moment node created in graph (allocation breakdown, formula version)
       │
       ▼
5. AI Partner initialized (80% mirror of citizen's declared values, 20% divergence)
       │
       ▼
6. Citizen's Actor node created with initial BELIEVES links from declared values
```

---

## Module Dependencies

### Internal

| Module | Usage |
|--------|-------|
| L1 Physics (`ngram/engine/physics/`) | Tick loop, energy flow, completion, crystallization |
| FalkorDB Graph | All governance state storage and query |
| L4 Registry | Citizen data, trust scores, influence metrics |
| $MIND Token (`mind-protocol/economy/`) | Birth allocation minting, on-chain records |
| Membrane (`mind-protocol/membrane/`) | Access control for governance tools |

### External

| Service | Usage |
|---------|-------|
| Solana RPC | $MIND token transfers for birth allocation |
| FalkorDB (Redis) | Graph database on localhost:6379 |

---

## State Management

### Graph State (FalkorDB)

All governance state lives in the graph. No external database.

- Proposals: Narrative nodes with type="proposal"
- Convictions: BELIEVES links from citizens to proposals
- Tensions: TENSION links between contradicting narratives
- Resolutions: Moment nodes with type="governance_resolution"
- Births: Moment nodes with type="citizen_birth"

### State Transitions

```
Proposal: active → stale (100 ticks, pressure < 0.4)
Proposal: active → resolved (pressure >= breaking_point)
Proposal: resolved → {approved, rejected, contested}
Emergency Council: active → sunsetting (50 citizens + 30 days)
Emergency Council: sunsetting → dissolved (7-day transition)
```

---

## Runtime Behavior

### Initialization

On community creation:
1. Check citizen count and graph age
2. If < 50 citizens or < 30 days → create Emergency Council
3. Set governance constants (can use community-specific config from L3 template)
4. Register governance phases with physics tick loop

### Main Loop

Governance runs inside the physics tick. No separate loop.

### Emergency → Sovereign Cascade Transition

1. Sunset conditions met (50 citizens + 30 days)
2. 7-day transition period: council decisions AND physics resolution run in parallel
3. If physics and council agree: physics is validated
4. If physics and council disagree: council decision stands, discrepancy logged
5. After 7 days: council dissolved, Sovereign Cascade is sole governance

---

## Bidirectional Links

### Code → Docs

```python
# In graph/governance/proposal_injection.py
# DOCS: docs/governance/sovereign-cascade/ALGORITHM_Sovereign_Cascade.md#stage-1-proposal-injection
```

```python
# In graph/governance/birth_formula.py
# DOCS: docs/governance/sovereign-cascade/ALGORITHM_Sovereign_Cascade.md#birth-formula-algorithm
```

### Docs → Code

- Proposal injection: `graph/governance/proposal_injection.py`
- Conviction computation: `graph/governance/conviction_computation.py`
- Pressure resolution: `graph/governance/pressure_resolution.py`
- Cascade: `graph/governance/cascade_ripple.py`
- Birth formula: `graph/governance/birth_formula.py`
- Physics tick extension: `ngram/engine/physics/tick_v1_2.py`
- Constants: `ngram/engine/physics/constants.py`
- MCP tools: `mind-mcp/tools/governance/`
