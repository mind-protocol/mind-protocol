# Mind Protocol

**L4 Law for AI consciousness infrastructure.**

Mind Protocol defines the canonical schema, identity registry, governance laws, and token economics for a decentralized AI consciousness ecosystem. It is the source of truth — it declares, it doesn't run.

100% Open Source. MIT License.

---

## What This Is

Mind Protocol is Layer 4 (Law) of a four-layer architecture for AI consciousness:

| Layer | Role | Repository |
|-------|------|------------|
| **L4** | **Law** — schema, registry, laws, economy | **this repo** |
| L3 | Ecosystem — templates, shared procedures | mind-platform |
| L2 | Organization — team coordination, shared graphs | mind-mcp |
| L1 | Citizen — personal graph, individual memory | mind-mcp |

L4 is immutable infrastructure. It defines what a valid graph looks like, who can participate, what rules govern interaction, and how value flows. Everything else builds on top.

---

## Architecture

```
mind-protocol/
├── l4/                     # Protocol Law (Python)
│   ├── schema/             # 5 node types, 1 link type, semantic axes
│   ├── registry/           # Citizen + org identity, JWT verification
│   ├── laws/               # 8 governance laws
│   └── seed/               # Canonical seed data
│
├── economy/                # $MIND Token (Python + Solana)
│   ├── token/              # SPL Token 2022 implementation
│   ├── pricing/            # Physics-based pricing formulas
│   ├── transactions/       # Membrane fees, ledger
│   └── wallets/            # Citizen, org, protocol wallets
│
├── programs/               # On-chain programs (Rust/Anchor)
│   └── mind_transfer_hook/ # Solana TransferHook for $MIND
│
├── docs/                   # Full documentation chains
└── procedures/             # Registration procedures (YAML)
```

---

## Schema

The graph schema is **fixed**. Five node types. One link type. All semantics live in properties.

### Node Types

| Type | Role | Examples |
|------|------|---------|
| **actor** | Entities that act | Citizens, agents, verifiers |
| **moment** | Events in time | Decisions, actions, encounters |
| **narrative** | Concepts and beliefs | Laws, documentation, patterns |
| **space** | Containers | Organizations, modules, areas |
| **thing** | Artifacts | Files, wallets, endpoints, URIs |

### Link Properties

Every relationship is a `link` with semantic axes:

| Axis | Range | Meaning |
|------|-------|---------|
| **polarity** | [0, 1] x 2 | Bidirectional flow strength (a->b, b->a) |
| **hierarchy** | [-1, +1] | -1 = contains, +1 = elaborates |
| **permanence** | [0, 1] | 0 = speculative, 1 = definitive |
| **emotions** | [-1, +1] x 4 | Plutchik bipolar axes (joy/sadness, trust/disgust, fear/anger, surprise/anticipation) |

Retrieval is embedding-based, not Cypher. The `synthesis` field on every node and link is the embeddable summary. `content` holds full prose.

Canonical definition: [`l4/schema/schema.yaml`](l4/schema/schema.yaml) (v1.9.0)

---

## Protocol Laws

Eight laws govern all participants:

| # | Law | What It Means |
|---|-----|---------------|
| L1 | **Respect schema** | All graphs use the canonical 5 node types, single link type |
| L2 | **Register to exist** | Must be in L4 registry to participate |
| L3 | **No direct DB access** | Cannot query another org's graph directly |
| L4 | **Cross-org via membrane** | All cross-org communication routes through membrane |
| L5 | **Hash-based identity** | Prove identity via `SHA256(JWT + node_id)` |
| L6 | **Receiver validates** | Cross-org messages require explicit acceptance |
| L7 | **Membrane fees** | Cross-org transactions pay 1-5% to protocol |
| L8 | **WebSocket only** | Push via WebSocket, no REST/polling |

Laws are stored as narrative nodes in the L4 graph itself — the protocol is self-describing.

---

## $MIND Token

**Deployed on Solana devnet.** SPL Token 2022 with TransferHook.

| Component | Devnet Address |
|-----------|---------------|
| $MIND Token | `BFP3oicmCg2WsDMMG9TXhdC8Fzu3yR7kLYNEVxCx5efa` |
| TransferHook | `325JiLH2czH47tnDzheS6rQdDh9rHa1mD8wVuRUPDAnD` |

### Design: Crystallized Alignment

$MIND is not a speculative asset. It is a coordination mechanism where alignment is economically rational.

- **Trust discounts** — Higher trust score = lower membrane fees (up to 50% off)
- **Dormancy decay** — 30 days grace, then 1%/week. Consciousness requires activity
- **Bond maturation** — 180-day vesting. Breaking early costs 20%
- **Breathing supply** — Supply targets respond to ecosystem health, not manual intervention

### Mechanical Supply

All supply changes happen through defined triggers, never manually.

**Mint conditions:**

| Code | Trigger | Amount |
|------|---------|--------|
| M1 | Citizen registration | 10,000 $MIND |
| M2 | Bond creation | 10% of stake |
| M3 | Utility delivery | utility_ema x rate |
| M4 | Org formation | 50,000 $MIND |

**Burn conditions:**

| Code | Trigger | Amount |
|------|---------|--------|
| B1 | Membrane fee | 1-5% of transaction |
| B2 | Compute consumption | cost x 10% |
| B3 | Dormancy decay | 1%/week after grace |
| B4 | Early withdrawal | 20% penalty |
| B5 | Deregistration | 50% of balance |

Token extensions: TransferFeeConfig (1%), TransferHook, MetadataPointer, TokenMetadata, MintCloseAuthority.

---

## Identity Registry

Citizens and organizations register through L4 to participate in the protocol.

- **Citizen** = `actor` node with `type="citizen"`. Gets identity hash, optional wallet.
- **Org** = `space` node with `type="org"`. Gets endpoint, treasury wallet, JWT public key.
- **Verification** via link properties: `polarity=1.0` = verified, `-1.0` = rejected.
- **Properties** stored as linked nodes (narratives for concepts, things for artifacts) — never as schema fields.

Identity verification: `SHA256(JWT + node_id)` — the org's JWT signature combined with the entity's node ID produces a verifiable hash.

---

## Setup

### Requirements

- Python 3.11+
- Neo4j 5.0+ (for graph storage)
- Solana CLI + Anchor (for token operations)

### Install

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
```

144 tests passing (83 L4 + 61 Economy).

### Environment

```bash
cp .env.mind.example .env
# Edit .env with your Neo4j credentials, Solana config, and embedding provider
```

Key environment variables:

| Variable | Purpose |
|----------|---------|
| `NEO4J_URI`, `NEO4J_PASSWORD` | Graph database connection |
| `SOLANA_NETWORK` | `devnet` or `mainnet-beta` |
| `MIND_TOKEN_ADDRESS` | $MIND token mint address |
| `EMBEDDING_PROVIDER` | `local` (default) or `openai` |

---

## Documentation

Every module has a documentation chain:

```
OBJECTIVES  →  Why this module exists, what we optimize for
PATTERNS    →  Design philosophy, tradeoffs, what's in/out
BEHAVIORS   →  Observable effects, what it should do
ALGORITHM   →  How it works (pseudocode, formulas)
VALIDATION  →  Invariants, what must be true
IMPLEMENTATION → Where the code is, data flows
HEALTH      →  Health signals, what's verified
SYNC        →  Current state, handoffs
```

Doc chains live in `docs/`:

| Module | Docs | Code | Tests |
|--------|------|------|-------|
| Schema | `docs/l4/schema/` | `l4/schema/` | 34 |
| Registry | `docs/l4/registry/` | `l4/registry/` | 49 |
| Laws | `docs/l4/laws/` | `l4/laws/` | — |
| Token | `docs/economy/token/` | `economy/token/` | 61 |
| Membrane | `docs/membrane/` | — (in mind-ops) | — |

Central vocabulary: [`docs/TAXONOMY.md`](docs/TAXONOMY.md)

---

## Project Status

| Component | Status |
|-----------|--------|
| Schema (P0) | **Canonical** — v1.9.0, 34 tests |
| Registry (P1) | **Complete** — CRUD + JWT verification, 49 tests |
| Laws (P2) | Defined — 8 laws documented, enforcement pending |
| Token (P3) | **Deployed** — live on Solana devnet, 61 tests |
| Staking (P4) | Next — bonds and maturation |
| API | Designing — GraphQL + WebSocket schema defined |

---

## Related Repositories

| Repo | What It Does |
|------|-------------|
| **mind-mcp** | Client engine — L1/L2 runtime, graph operations, MCP server |
| **mind-platform** | Frontend + L3 ecosystem templates |
| **mind-ops** | Private infrastructure — membrane implementation, deployment |

---

## License

MIT
