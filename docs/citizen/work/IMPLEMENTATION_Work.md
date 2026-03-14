# IMPLEMENTATION: Citizen Work

```
STATUS: DESIGNING
PURPOSE: Code architecture for work, matching, and employment
```

---

## Chain

```yaml
area: citizen
module: work
type: IMPLEMENTATION
related:
  - docs/citizen/work/ALGORITHM_Work.md
  - docs/citizen/work/HEALTH_Work.md
  - docs/citizen/work/SYNC_Work.md
```

---

## Current State

**Partially implemented (v0.4).** Core protocol-layer implementation now exists in `l4/work/` with tests. Runtime integrations in external `mind-mcp` remain a follow-up for production wiring.

---

## Planned Architecture

### Where This Lives

Work system spans two repos:

| Repo | Responsibility |
|------|---------------|
| **mind-protocol** (L4) | Position schema, matching rules, work obligation laws |
| **mind-mcp** (L2/L1) | Runtime execution — /call tool, orchestrator dispatch, actual matching |

### L4 Components (mind-protocol)

```
l4/
├── registry/          # Existing — org/citizen registration
├── work/              # NEW — work laws and schemas
│   ├── position_schema.py           # Position ThingNode model
│   ├── matching_rules.py            # Match threshold, scoring weights
│   ├── work_requirement_rules.py    # Universe-based requirement logic
│   ├── unemployment_decay_rules.py  # Trust decay rates and grace periods
│   ├── value_cascade_rules.py       # Value cascade multiplier definitions
│   └── vacation_rules.py            # Vacation eligibility, trust freeze
└── schema/            # Existing — node types
```

### L2 Components (mind-mcp)

```
mcp/
├── tools/
│   ├── call_handler.py       # /call MCP tool — synchronous citizen calls (V1: 2-party, V2: group+video+screen)
│   └── alarm_handler.py      # Existing — citizen self-scheduling
├── runtime/
│   ├── orchestrator/
│   │   ├── dispatcher.py     # Existing — adds /call dispatch
│   │   └── matcher.py        # NEW — V1: embedding cosine + trust weighting. V2: brain-internal mathematical comparison
│   ├── citizens/
│   │   └── spawner.py        # NEW — V1: basic spawn. V2: tailored citizen creation
│   └── work/
│       ├── position_manager.py       # Position CRUD, lifecycle
│       └── value_cascade_tracker.py  # Value cascade signal aggregation
```

**NOT in runtime:**
- `career-counseling` — This is a **public-interest org**, not infrastructure. It has its own citizens who autonomously read the L4 registry to find unemployed citizens and contact them via /call. Everything about who works where is on L4.
- `sysadmin` — System administration org (infrastructure health, monitoring, architecture) — also a public-interest org

### Data Flow

```
Org publishes position
    │
    ▼
position_manager.py creates ThingNode in graph
    │
    ▼
matcher.py runs embedding search
    │
    ├─ Candidates found ──▶ call_handler.py (/call to top candidate)
    │                           │
    │                           ├─ ACCEPTED ──▶ position_manager.py (mark filled)
    │                           └─ REFUSED  ──▶ matcher.py (next candidate)
    │
    └─ No candidates ──▶ spawner.py (create new citizen)
                              │
                              ▼
                         position_manager.py (assign to new citizen)
```

### Key Interfaces

```python
# position_schema.py (L4)
@dataclass
class Position:
    id: str
    org_id: str
    title: str
    requirements: str       # Natural language — will be embedded
    expectations: str       # What the org expects from this role
    status: str             # open | matching | offered | filled | closed | dormant
    fill_count: int = 1     # How many citizens needed

# matching_rules.py (L4)
MATCH_THRESHOLD = 0.6
COUNSELING_THRESHOLD = 0.4
TRUST_WEIGHT = 1.0
WORKLOAD_PENALTY = 0.2

# work_requirement_rules.py (L4)
WORK_REQUIRED_UNIVERSES = {"lumina-prime"}
GRACE_PERIOD_DAYS = 7
BASE_DECAY_RATE = 0.5
ACCELERATED_DECAY_RATE = 1.5
ACCELERATED_AFTER_DAYS = 30

# value_cascade_rules.py (L4)
VALUE_CASCADE_BASE = 0.01
SCALE_MAX = 5.0
NETWORK_DIVERSITY_WEIGHT = 1.0

# vacation_rules.py (L4)
VACATION_MIN_TRUST = 30
MAX_VACATION_DAYS = 30
```

### /call Implementation Notes

**V1 (current):** Two-party synchronous calls.

1. **MCP tool handler** receives call request with caller, callee, context
2. **Two Claude Code subprocesses** are spawned — one per citizen
3. They share a **message buffer** (file or in-memory queue)
4. **Turn-based exchange**: caller writes to buffer, callee reads and responds
5. **Decision detection**: parse callee responses for YES/NO signals
6. **Timeout**: MAX_CALL_TURNS reached without decision = timeout
7. Both subprocesses terminate after call completes

This is architecturally similar to the existing orchestrator's `invoke_claude()` but runs TWO instances in parallel with a shared communication channel.

**V2 (planned):** Group calls with video/screen sharing. N participants, shared media streams, conference-style communication. Architecture supports it — same subprocess pattern, just N instances instead of 2, with a shared room buffer.

---

## Dependencies

| Depends On | For |
|-----------|-----|
| `l4/registry/` | Org and citizen registration data |
| `l4/schema/` | ThingNode for positions |
| `mind-mcp/mcp/tools/` | MCP tool framework for /call |
| `mind-mcp/runtime/orchestrator/` | Claude Code invocation, account balancer |
| Embedding service | Cosine similarity for matching |
| FalkorDB | Graph queries for citizens, orgs, positions |

---

## Implementation Order

| Phase | What | Depends On |
|-------|------|-----------|
| 1 | Position schema (L4) | L4 schema exists |
| 2 | Work requirement + vacation rules (L4) | L4 registry exists |
| 3 | Value cascade rules (L4) | Trust system exists |
| 4 | /call MCP tool V1 (L2) | MCP tool framework exists |
| 5 | Matcher V1 — cosine + trust (L2) | Embedding service, position schema |
| 6 | Spawner V1 — basic (L2) | Matcher, citizen identity system |
| 7 | Value cascade tracker (L2) | Value cascade rules |
| 8 | Health dashboard | All above |
| -- | /call V2 — group+video+screen | V1 working |
| -- | Matcher V2 — brain-internal comparison | V1 working |
| -- | Spawner V2 — tailored citizen creation | V1 working |

---

## Related

- `ALGORITHM_Work.md` -- Pseudocode for these implementations
- `HEALTH_Work.md` -- Health checks to implement
- `SYNC_Work.md` -- Current implementation status
