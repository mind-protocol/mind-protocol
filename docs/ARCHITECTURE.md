# mind-protocol Architecture

## Layer Position: L4 (Protocol Law)

mind-protocol is the **L4 protocol layer** - the immutable law that all Mind clients must follow. This repo is open source for verifiability.

```
┌─────────────────────────────────────────────────────────────┐
│ L4: Protocol (mind-protocol) ◄── YOU ARE HERE              │
│     Registry, Economy, Validation, Broadcast                │
│                         │                                   │
│                         │ WebSocket push                    │
│                         ▼                                   │
├─────────────────────────────────────────────────────────────┤
│ L3: Ecosystem (mind-platform)                               │
│     Templates, Organizations, Public Graph                  │
├─────────────────────────────────────────────────────────────┤
│ L2: Organization                                            │
│     Multi-user coordination                                 │
├─────────────────────────────────────────────────────────────┤
│ L1: Citizen (mind-mcp)                                      │
│     Local graph, Physics engine, MCP server                 │
└─────────────────────────────────────────────────────────────┘
```

## Core Responsibilities

### 1. Registry
- Actor registration and identity
- Space definitions
- Rule sets and constraints

### 2. Economy
- $MIND token mechanics
- Membrane fees (1-5%)
- Staking and rewards

### 3. Validation
- Stimulus validation rules
- Physics constraints enforcement
- Saturation limits, refractory periods

### 4. Broadcast
- WebSocket push to L1 clients
- No polling - L4 pushes updates
- Real-time synchronization

## Key Invariants

These must be enforced at L4:

| Invariant | Description |
|-----------|-------------|
| Stimulus Saturation | No actor can emit > threshold per window |
| Refractory Period | Minimum time between stimuli |
| Trust EMA | Weighted trust based on history |
| Energy Conservation | Total energy in system is conserved |
| Membrane Fees | 1-5% of value flows to protocol |

## Key Design Decisions

### Open Source for Verifiability
All L4 code is public. Anyone can verify the protocol behaves as documented. No hidden logic.

### Push Only - No Polling
L4 pushes to clients. Clients don't poll. This ensures consistency and reduces load.

### Immutable Core
Once deployed, core invariants don't change. Upgrades require migration, not mutation.

## Module Structure

```
l4/
├── registry/          # Actor, space, rule registration
├── validation/        # Stimulus validation
├── broadcast/         # WebSocket server
└── invariants/        # Core protocol rules

economy/
├── token/             # $MIND mechanics
├── fees/              # Membrane fee calculation
└── staking/           # Stake and reward logic

api/
├── graphql/           # GraphQL schema
└── websocket/         # Push protocol

graph/
└── schema/            # L4 graph schema
```

## Communication Protocol

### WebSocket Push Format

```json
{
  "type": "stimulus",
  "from": "actor_xxx",
  "to": "space_yyy",
  "energy": 0.8,
  "payload": { ... },
  "timestamp": 1703788800,
  "signature": "..."
}
```

### Validation Response

```json
{
  "type": "validation_result",
  "stimulus_id": "stim_xxx",
  "valid": true,
  "reason": null,
  "fee_charged": 0.02
}
```

## Related Repos

| Repo | Layer | Purpose |
|------|-------|---------|
| mind-mcp | L1 | Client engine |
| mind-protocol | L4 | This repo - protocol law |
| mind-platform | L3 | Frontend, templates, ecosystem |
| mind-ops | - | Private infrastructure, billing |
