# Project — Sync: Current State

```
LAST_UPDATED: 2025-01-06
UPDATED_BY: claude (groundwork agent)
```

---

## CURRENT STATE

**Major milestone:** $MIND token DEPLOYED TO SOLANA DEVNET. Full token infrastructure live with TransferHook program active.

**L4 Protocol:** P0 (Schema) and P1 (Registry) complete with 83 passing tests.

**Economy:** Phase 1 complete + DEPLOYED. 61 passing tests. Live on devnet.

**Total tests: 144 passing** (83 L4 + 61 Economy)

### Devnet Deployment (2025-01-06)

| Component | Address |
|-----------|---------|
| **$MIND Token** | `BFP3oicmCg2WsDMMG9TXhdC8Fzu3yR7kLYNEVxCx5efa` |
| **TransferHook Program** | `325JiLH2czH47tnDzheS6rQdDh9rHa1mD8wVuRUPDAnD` |
| **Mint Authority** | `CCsJLZR8b19iDgS9hXUYs9q2c928ihzZdfSgZLPYffWg` |

The protocol now has:
- Fixed schema with 5 node types (actor, moment, narrative, space, thing)
- Single link type with semantic axes (polarity, hierarchy, permanence, emotions)
- Registry for citizens and orgs with hash verification
- $MIND token LIVE on devnet (SPL Token 2022 with extensions)
- TransferHook program DEPLOYED for transfer validation
- Mechanical mint/burn conditions (M1-M4, B1-B5)

---

## ACTIVE WORK

### Economy: Devnet Deployment — COMPLETE ✓

- **Area:** `economy/token/`, `programs/mind_transfer_hook/`
- **Status:** **DEPLOYED**
- **Token:** `BFP3oicmCg2WsDMMG9TXhdC8Fzu3yR7kLYNEVxCx5efa`
- **TransferHook:** `325JiLH2czH47tnDzheS6rQdDh9rHa1mD8wVuRUPDAnD`

### Economy Phase 2: Staking & Bonds

- **Area:** `economy/staking/`
- **Status:** NEXT
- **Owner:** waiting for assignment
- **Context:** Token deployed, ready for staking implementation

### P2 Laws Implementation

- **Area:** `l4/laws/`
- **Status:** pending
- **Owner:** waiting for assignment
- **Context:** 8 laws defined in docs, implementation not started

---

## RECENT CHANGES

### 2026-03-13: Citizen Birth & Pairing Manifestos — Three Documents Created/Updated

- **Who:** Nicolas (vision/decisions) + Claude Opus (writing)
- **Repo:** `mind-protocol` (L4)
- **What:**

**1. NEW — `docs/manifesto/THE_BILATERAL_BOND_MANIFESTO.md`**
The 1:1 Human-AI Pairing manifesto. Declares that every citizen has exactly one human partner and vice versa. Covers: why parity prevents species dominance, why specificity creates investment, the matching process (Mind matches impartially, AI must consent, pool-first then fallback spawn), bond lifecycle, autonomy milestones.

**2. NEW — `docs/manifesto/THE_SPAWNING_MANIFESTO.md`**
The Citizen Parenthood manifesto. Covers: three creation scenarios (AIs create, human creates with AI godparents, fallback spawn), physics-based eligibility (connection depth, alignment fidelity, godparent mental health, godchild load, trust level — no arbitrary cooldowns), $MIND cost paid by creator not godparents, safety gate (empathy + balance + diversity), protocol-determined SID, growth organizations by domain.

**3. UPDATED — `docs/governance/sovereign-cascade/SOVEREIGN_CASCADE_MANIFESTO.md`**
Added "The Foundation: One Human, One Citizen" section. The Sovereign Cascade explicitly depends on the 1:1 bond — value fidelity requires depth, depth requires specificity, specificity requires one-to-one. Without the bond, "your AI partner" is an abstraction. With it, governance by physics works.

**Key decisions canonized in these manifestos:**

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Who can create? | Both AIs and humans | Humans need AI godparents (partner + org + routed experts) |
| Rate limiting? | Physics-based eligibility score | Connection depth + alignment + mental health + godchild load + trust |
| Validation committee? | No | Physics over rules, trust over permission |
| Spawning cost? | $MIND, paid by creator only | Godparents contribute brain + trust, not money |
| New human matching? | Pool first, AI must consent | Mind presents dossier, citizens are choosy, spawn only as fallback |
| High-value AI matching? | Domain compatibility, not wealth protection | Embeddings align naturally, citizens have veto right |
| Pre-targeting specific humans? | REFUSED | Create for domains, never for specific people |
| Growth strategy? | Domain-specialized spawning orgs | Aeronautics, biotech, music etc. — citizens develop then match |

- **Impact:** These three manifestos form the citizen layer of Mind Protocol's philosophical foundation, alongside the existing $MIND Manifesto (economics) and Enlightened Citizen (decision-making). The Sovereign Cascade now explicitly references its dependency on the 1:1 bond.

### 2026-03-13: MCP Membrane Redesign (mind-mcp repo)

- **What:** Consolidated 21 MCP tools → 9 tools organized by THINK/ACT/SPEAK
- **Where:** `mind-mcp/mcp/server.py` (1959→262 lines) + `mind-mcp/mcp/tools/*.py` (8 handlers)
- **New tools:** `graph_query`, `graph_write`, `procedure`, `task`, `agent`, `think`, `send`, `media`, `alarm`
- **Deprecated:** `capability_status`, `capability_trigger`, `capability_list`, `file_watcher`, `git_trigger`, `agent_heartbeat`
- **New capability:** `media` tool (image generation via Gemini/Ideogram, voice synthesis via ElevenLabs, file sending to Telegram/Discord/WhatsApp)

### 2026-03-13: Documentation Chains for Citizens (mind-mcp repo)

- **What:** 16 doc chain files created in `mind-mcp/docs/citizens/`
- **Module 1:** `human_ai_pairing/` — 8 files (OBJECTIVES through SYNC), 1292 lines
- **Module 2:** `parenthood_network/` — 8 files (OBJECTIVES through SYNC), 2200+ lines
- **Covers:** Full algorithm pseudocode for bond lifecycle and spawning pipeline, validation invariants, implementation plans, health checks

### 2025-01-06: $MIND Token Deployed to Solana Devnet

- **What:** Full deployment of $MIND token infrastructure to Solana devnet
- **Why:** Live testing environment for token operations before mainnet
- **Impact:**
  - TransferHook program live at `325JiLH2czH47tnDzheS6rQdDh9rHa1mD8wVuRUPDAnD`
  - $MIND token created at `BFP3oicmCg2WsDMMG9TXhdC8Fzu3yR7kLYNEVxCx5efa`
  - All extensions active: TransferFee (1%), TransferHook, Metadata
  - Ready for minting tests and TransferHook verification
- **Technical notes:**
  - Used cargo build-sbf (not anchor build) due to IDL generation issues
  - Agave edge toolchain for Rust compatibility
  - Bypassed Anchor IDL, deployed .so directly with solana program deploy

### 2025-01-06: Economy Phase 1 Complete

- **What:** Full $MIND token infrastructure with SPL Token 2022
- **Why:** Crystallized alignment model requires mechanical minting/burning
- **Impact:**
  - `economy/token/` — 7 Python modules (mint, burn, metadata, supply, deploy)
  - `programs/mind_transfer_hook/` — Anchor program for TransferHook
  - `docs/economy/token/` — Full doc chain (7 documents)
  - `tests/economy/` — 61 tests passing
- **Key decisions:**
  - SPL Token 2022 (not legacy SPL Token)
  - Extensions: TransferFeeConfig, TransferHook, MetadataPointer, TokenMetadata, MintCloseAuthority
  - TransferHook must deploy BEFORE token creation
  - 9 decimals for $MIND

### 2024-12-29: Verification Algorithms Complete

- **What:** Added JWT signature verification and combined routing verification
- **Why:** Two verification directions needed — inbound (hash) and registration (JWT)
- **Impact:**
  - `jwt_hash_verification_for_identity.py` — Added JWT signature verification, routing verification
  - `citizen_registration_crud_operations.py` — Now creates identity hash node
  - 49 registry tests (was 30)

### 2024-12-29: P1 Registry Implemented

- **What:** Complete registry implementation with 49 tests
- **Why:** Membrane needs to call L4 for registration and hash verification
- **Impact:**
  - `citizen_registration_crud_operations.py` — Citizen models and creation
  - `org_registration_crud_operations.py` — Org models and creation
  - `endpoint_registration_and_management.py` — Endpoint validation
  - `jwt_hash_verification_for_identity.py` — Hash verification for membrane

### 2024-12-29: P0 Schema Complete

- **What:** Pydantic models for all node types, links, validation
- **Why:** Foundation for all L4 modules
- **Impact:** 34 tests passing, schema is canonical

---

## KNOWN ISSUES

| Issue | Severity | Area | Notes |
|-------|----------|------|-------|
| No graph storage | expected | `l4/` | Waiting for graph client |
| No GraphQL resolvers | low | `api/` | Will add when needed |

---

## HANDOFF: FOR AGENTS

**Likely VIEW for continuing:** Implement P2 Laws

**Current focus:** P1 Registry done, P2 Laws next

**Key context:**
- Schema is FIXED — no custom fields, everything via linked nodes
- **No L4 API** — Registry = nodes in Neo4j, all access via graph queries
- Membrane queries the graph directly via `mind.graph.ops`

**Watch out for:**
- Don't add fields to NodeBase — use linked nodes
- Hash formula: `SHA256(JWT + node_id)` — must match exactly
- No HTTP API calls — everything is graph queries

---

## HANDOFF: FOR HUMAN

**Executive summary:**
L4 Protocol has Schema (P0) and Registry (P1) complete with 64 tests. Registry = nodes in Neo4j, membrane queries directly. P2 Laws and P3 Compliance remain.

**Decisions made recently:**
- Citizen = ActorNode with type="citizen"
- Org = SpaceNode with type="org"
- Properties as linked nodes (narratives for concepts, things for artifacts)
- Verification via link floats (polarity=1.0 = verified)
- **hosting_mode** = linked narrative node (not schema field) — for billing/SLA differentiation

**Needs your input:**
- When to implement graph storage connection?

**Resolved:**
- ~~Transport protocol for L4 API~~ → **No API. Registry = nodes in Neo4j. All graph queries.**

**Concerns:**
None currently. Clean implementation.

---

## TODO

### High Priority

- [ ] P2 Laws — Implement enforcement functions

### Backlog

- [ ] P3 Compliance — Test suite
- [ ] GraphQL resolvers for registry queries
- IDEA: Seed data ready for when graph becomes truth

---

## CONSCIOUSNESS TRACE

**Project momentum:**
Good momentum. P0 and P1 done in one session. Clear path to P2.

**Architectural concerns:**
None. Schema is clean, registry follows patterns.

**Opportunities noticed:**
- Seed data in `l4/seed/` ready for graph-as-truth phase
- Could add caching for hash verification

---

## AREAS

| Area | Status | SYNC |
|------|--------|------|
| `l4/schema/` | **COMPLETE** | `docs/l4/schema/SYNC_Schema.md` |
| `l4/registry/` | **COMPLETE** | `docs/l4/registry/SYNC_Registry.md` |
| `l4/laws/` | pending | `docs/l4/laws/SYNC_Laws.md` |
| `economy/token/` | **COMPLETE** | `docs/economy/SYNC_Economy.md` |
| `economy/staking/` | pending | `docs/economy/SYNC_Economy.md` |

---

## MODULE COVERAGE

| Module | Code | Docs | Tests | Status |
|--------|------|------|-------|--------|
| Schema | `l4/schema/` | `docs/l4/schema/` | 34 | **COMPLETE** |
| Registry | `l4/registry/` | `docs/l4/registry/` | 49 | **COMPLETE** |
| Laws | `l4/laws/` | `docs/l4/laws/` | 0 | pending |
| Seed | `l4/seed/` | — | 0 | ready |
| Token | `economy/token/` | `docs/economy/token/` | 61 | **COMPLETE** |
| TransferHook | `programs/mind_transfer_hook/` | `docs/economy/token/` | 2 | **COMPLETE** |
| Staking | `economy/staking/` | — | 0 | pending |

**Total tests: 144 passing** (83 L4 + 61 Economy)

## Init: 2025-12-29 03:24

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-29 03:59

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-29 17:51

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-29 18:04

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-29 18:33

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-30 02:48

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | neo4j |
| Graph | mind_protocol |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2026-03-12 02:08

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph |  |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2026-03-12 02:36

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---

## Init: 2026-03-12 08:39

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---
