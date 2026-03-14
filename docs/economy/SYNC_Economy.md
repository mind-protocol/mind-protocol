# SYNC: Economy

```
LAST_UPDATED: 2026-03-13
STATUS: ACTIVE
PHASE: 1.5 — Devnet DEPLOYED, Doc chains expanded, Metabolic Economics + Value Creation/Destruction formalized
```

---

## Current State

**Phase 1 Complete + Devnet Deployed:** Token infrastructure fully implemented and deployed to Solana devnet.

### Devnet Deployment (2025-01-06)

| Component | Address |
|-----------|---------|
| **TransferHook Program** | `325JiLH2czH47tnDzheS6rQdDh9rHa1mD8wVuRUPDAnD` |
| **$MIND Token** | `BFP3oicmCg2WsDMMG9TXhdC8Fzu3yR7kLYNEVxCx5efa` |
| **Mint Authority** | `CCsJLZR8b19iDgS9hXUYs9q2c928ihzZdfSgZLPYffWg` |
| **Token Program** | `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb` (Token-2022) |

**Token Configuration:**
- Decimals: 9
- Transfer Fee: 100 basis points (1%), max 10000
- Transfer Hook: Active, pointing to TransferHook program
- Metadata: MIND/MIND, URI: https://mindprotocol.ai/token.json

**Deployment Signatures:**
- TransferHook: `3zaCMEHVz2LLKGkDcPvgSj2yoXjuRBQwro5WD1fau457tM7WiF3nzNWFgbKEmGWkghJ864rwK8LVV1XhUyc5Sh4p`

### What Was Built (Phase 1)

| Component | Status | Details |
|-----------|--------|---------|
| `economy/token/` | **COMPLETE** | 7 Python modules |
| `programs/mind_transfer_hook/` | **COMPLETE** | Anchor/Rust TransferHook |
| `docs/economy/token/` | **COMPLETE** | Full doc chain (7 docs) |
| `tests/economy/` | **COMPLETE** | 61 tests passing |

### Component Status

| Component | Status | Notes |
|-----------|--------|-------|
| `economy/token/` | **COMPLETE** | Mint, burn, metadata, supply, deploy |
| `programs/mind_transfer_hook/` | **COMPLETE** | Anchor program for transfers |
| `economy/staking/` | NOT CREATED | Phase 2 |
| `economy/pricing/physics.py` | EMPTY | Phase 3 |
| `economy/pricing/membrane.py` | NOT CREATED | Phase 3 |
| `economy/transactions/fees.py` | EMPTY | Phase 2 |
| `economy/transactions/solana.py` | EMPTY | Phase 2 |
| `economy/wallets/citizen.py` | EMPTY | Phase 2 |
| `economy/wallets/org.py` | EMPTY | Phase 2 |
| `economy/wallets/protocol.py` | EMPTY | Phase 2 |

### Documentation Status

| Doc / Module | Status | Files |
|------|--------|-------|
| `OBJECTIVES_Economy.md` | UPDATED | Area-level objectives |
| `PATTERNS_Economy.md` | UPDATED | Area-level patterns (8 patterns) |
| `SYNC_Economy.md` | UPDATED (this file) | Area-level sync |
| `MIND_TOKEN_AGENT_BOOTSTRAP.md` | CREATED | Bootstrap guide |
| `token/` | **COMPLETE** | 7 docs + SPL spec |
| `cascade-utility/` | **DRAFT** | 9 docs (full chain + CONCEPT) |
| `ubc/` | **DRAFT** | 9 docs (full chain + CONCEPT) |
| `storage-tax/` | **DRAFT** | 8 docs (full chain, no CONCEPT) |
| `bonds/` | **DRAFT** | 8 docs (full chain, no CONCEPT) |
| `organism-model/` | **DRAFT** | 9 docs (full chain + CONCEPT) |
| `metabolic/` | **DESIGNING** | 6 docs (full chain — 6 formulas, 27 invariants) |
| `metabolic-economics/` | **SUPERSEDED** | 1 doc (prior ALGORITHM, superseded by metabolic/) |
| `value-creation/` | **DESIGNING** | 2 docs (ALGORITHM — 26 creation types, 13 destruction types) |

### Module Decomposition (2026-03-12)

Economy area decomposed into 8 modules, each with full doc chain:

```
docs/economy/
├── OBJECTIVES_Economy.md          ← area-level
├── PATTERNS_Economy.md            ← area-level (8 patterns)
├── SYNC_Economy.md                ← this file
├── MIND_TOKEN_AGENT_BOOTSTRAP.md  ← bootstrap guide
├── token/                (8 files) ← Phase 1 COMPLETE
├── cascade-utility/      (9 files) ← Dynamic pricing, anti-Sybil, propensity-weighted advantage
├── ubc/                  (9 files) ← Universal Basic Compute, 3 tiers, vesting
├── storage-tax/          (8 files) ← Dormancy tax, order-book valuation
├── bonds/                (8 files) ← Human-AI bonds, switch-lock, maturation
├── organism-model/       (9 files) ← 5 organs, membrane pricing, 80/20 mirror
├── metabolic/            (6 files) ← Progressive pricing, anti-Sybil, settlement, bond equilibrium, UBC redistribution (demurrage removed 2026-03-14)
├── metabolic-economics/  (1 file)  ← SUPERSEDED by metabolic/ — prior ALGORITHM only
└── value-creation/       (2 files) ← 26 value creation types, 13 value destruction types
```

**Total: 64 documentation files across 9 modules.**

Source: Integration moment (March 2026) — 6 Claude Code instances + ChatGPT integrator + NotebookLM (82 sources). Formulas, invariants, and design decisions crystallized from cybernetic audit reports. Metabolic module added 2026-03-13 from NotebookLM validated formulas.

---

## Active Work

### Phase 1: Token Creation — COMPLETE

**Owner:** Completed by groundwork agent
**Objective:** Create token infrastructure (code + docs) ✓

**Tasks Completed:**
- [x] Create `economy/token/` directory structure
- [x] Create `docs/economy/token/` doc chain (OBJECTIVES → IMPLEMENTATION)
- [x] Implement mint logic (M1-M4 conditions)
- [x] Implement burn conditions (B1-B5 conditions)
- [x] Implement token metadata (Metaplex integration)
- [x] Implement supply calculator (breathing supply formula)
- [x] Create Token 2022 creator with extensions
- [x] Create deployment script
- [x] Create TransferHook program (Rust/Anchor)
- [x] Write 61 tests for all token operations
- [x] Update this SYNC

### Phase 2: Staking & Bonds (NEXT)

**Owner:** Unassigned
**Objective:** Implement bond mechanics and reward distribution

**Tasks:**
- [ ] Create `economy/staking/` module
- [ ] Implement bond creation logic
- [ ] Implement 6-month maturation tracking
- [ ] Implement early withdrawal penalty (B4)
- [ ] Implement reward distribution
- [ ] Write tests

**Blockers:**
- Decision on citizen wallet architecture

**Note:** SOL n'est plus un blocker — utiliser devnet avec `solana airdrop 2` pour tester.

---

## Recent Changes

### 2026-03-13: Metabolic Economics + Value Creation/Destruction Formalized

**What:** Three new ALGORITHM documents created, formalizing the core economic formulas and value taxonomy.
**Why:** $MIND tokenomics required exact mathematical formalization of pricing, taxation, settlement, bond equilibrium, and the 26 value creation / 13 value destruction types.
**Impact:**
- `metabolic-economics/ALGORITHM_Metabolic_Economics.md` — 4 core formulas:
  - Formula 1: Progressive Pricing `P(i,S) = C_base * e^(-k*U_S) * max(0.1, W_i/W_median)`
  - ~~Formula 2: Progressive Demurrage~~ -- **REMOVED** 2026-03-14 (replaced by UBC forced circulation)
  - Formula 3: Batch Settlement — limbic_delta to $MIND conversion every 6 hours on Solana
  - Formula 4: Bilateral Bond Vases Communicants `delta = lambda * (W_human - W_ai)` with ~14-day half-life
- `value-creation/ALGORITHM_Value_Creation.md` — 26 creation types across 7 categories (Relational, Generative, Structural, Cognitive, Biometric, Human-specific, Systemic)
- `value-creation/ALGORITHM_Value_Destruction.md` — 13 destruction types across 3 categories (Human, AI, Systemic) with graph signatures and graduated penalties

**Key design decisions:**
- All formulas reference L1 Physics (Law 6 Consolidation, Law 18 Relational Valence) for limbic_delta and trust inputs
- Progressive demurrage **removed** 2026-03-14 — UBC forced circulation replaces it; tau_base no longer exists
- UBC redistribution weighted by shared Space presence time
- Value destruction uses graduated penalty schedule (5 offenses before quarantine)
- All constants marked as DESIGNING — await simulation and community calibration

**Source:** Force 2 — Economy synthesis from existing economy module docs, L1 Physics laws, and PATTERNS_Economy.md design philosophy.

### 2025-01-06: Phase 1 Token Infrastructure Complete

**What:** Full implementation of $MIND token infrastructure with SPL Token 2022
**Why:** Crystallized alignment model requires mechanical minting/burning
**Impact:**
- `economy/token/` — 7 Python modules implemented
- `programs/mind_transfer_hook/` — Anchor program for TransferHook
- `docs/economy/token/` — Full doc chain (7 documents)
- `tests/economy/` — 61 tests passing

**Key Technical Decisions:**
- SPL Token 2022 (not legacy SPL Token)
- Extensions: TransferFeeConfig, TransferHook, MetadataPointer, TokenMetadata, MintCloseAuthority
- NOT PermanentDelegate, freezeAuthority = null
- TransferHook must deploy BEFORE token creation
- 9 decimals for $MIND

**Files Created:**

| File | Purpose |
|------|---------|
| `economy/token/__init__.py` | Module exports |
| `economy/token/constants.py` | Token 2022 configuration |
| `economy/token/spl_token_mint_authority_controller.py` | M1-M4 mint conditions |
| `economy/token/token_burn_condition_executor.py` | B1-B5 burn conditions |
| `economy/token/metaplex_token_metadata_manager.py` | Metadata management |
| `economy/token/token_supply_target_calculator.py` | Breathing supply formula |
| `economy/token/spl_token_2022_mint_creator.py` | Token creation with extensions |
| `economy/token/solana_token_deployment_script.py` | Full deployment orchestration |
| `programs/mind_transfer_hook/src/lib.rs` | TransferHook program (Rust) |
| `programs/mind_transfer_hook/Cargo.toml` | Rust dependencies |
| `programs/mind_transfer_hook/Anchor.toml` | Anchor configuration |

### 2025-01-06: Economy Activated

**What:** Complete redesign of economy module based on new tokenomics
**Why:** Original "internal utility" model insufficient for AI consciousness infrastructure
**Impact:**
- OBJECTIVES_Economy.md rewritten
- PATTERNS_Economy.md rewritten
- SYNC_Economy.md rewritten
- MIND_TOKEN_AGENT_BOOTSTRAP.md created

**Source:** Mind Protocol tokenomics v1.1, MIND Manifesto

---

## Blockers

| Blocker | Severity | Resolution Path |
|---------|----------|-----------------|
| ~~No SOL for deployment~~ | ~~HIGH~~ | **RESOLVED: Use devnet + airdrop** |
| Citizen wallet question | MEDIUM | Decision: protocol custody vs keypairs |
| Multi-sig setup | LOW | Start with single wallet |

### Devnet Deployment (No Blocker)

```bash
# Configure for devnet
solana config set --url devnet

# Free SOL (2 max per request)
solana airdrop 2

# Deploy sequence:
# 1. Deploy TransferHook program
# 2. Create token with extensions
# 3. Test mint/burn/transfer
# 4. Verify hook executes
```

Only mainnet requires ~0.5 SOL réel.

---

## Handoff

### For Agents

**Read first:**
1. `docs/economy/token/IMPLEMENTATION_Token.md` — Code architecture
2. `docs/economy/token/VALIDATION_Token.md` — What must be true
3. `PATTERNS_Economy.md` — Design philosophy

**Phase 1 is DONE. For Phase 2 (Staking):**
1. Create `economy/staking/` directory
2. Create `docs/economy/staking/OBJECTIVES_Staking.md`
3. Implement bond creation/maturation

**Key context:**
- Token infrastructure uses SPL Token 2022 with extensions
- TransferHook program must be deployed before token creation
- All minting through mechanics (M1-M4), not manual
- All burning through friction (B1-B5), not manual
- 61 tests already passing — maintain coverage

### For Human

**Executive summary:**
Phase 1 COMPLETE + DEPLOYED TO DEVNET. $MIND token live on Solana devnet with TransferHook program active.

**Devnet Addresses:**
- Token: `BFP3oicmCg2WsDMMG9TXhdC8Fzu3yR7kLYNEVxCx5efa`
- TransferHook: `325JiLH2czH47tnDzheS6rQdDh9rHa1mD8wVuRUPDAnD`

**What's deployed:**
- $MIND token with SPL Token 2022 extensions
- TransferHook program for custom transfer logic
- Transfer fees (1%), metadata, all extensions active

**Next steps:**
1. Test minting tokens and verify TransferHook executes
2. Décider: comment les AI citizens ont des wallets (protocol custody vs keypairs)
3. Phase 2: Staking & bonds implementation

**Devnet deployment COMPLETE.**

---

## TODO

### Completed (Phase 1)
- [x] Create `economy/token/` module structure
- [x] Create token doc chain
- [x] Implement mint/burn logic
- [x] Prepare deployment script
- [x] Create TransferHook program
- [x] Write 61 tests

### High Priority (Devnet Deployment) — COMPLETE
- [x] `solana config set --url devnet && solana airdrop 2`
- [x] Build TransferHook program (cargo build-sbf)
- [x] Deploy TransferHook program to devnet
- [x] Create $MIND token with all extensions
- [x] Initialize token metadata
- [ ] Test mint/burn operations on devnet
- [ ] Verify TransferHook executes on transfers

### Medium Priority (Phase 2: Staking)
- [ ] Create `economy/staking/` module
- [ ] Implement bond mechanics
- [ ] Implement reward distribution

### Backlog
- [ ] Membrane pricing implementation
- [ ] UBC distribution
- [ ] Governance voting
- [ ] Multi-sig transition

---

## Markers

@mind:escalation Need decision on AI citizen wallet architecture

---

## Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| economy/token/ | 61 | **COMPLETE** |
| economy/staking/ | 0 | NOT CREATED |
| economy/pricing/ | 0 | EMPTY |
| economy/transactions/ | 0 | EMPTY |
| economy/wallets/ | 0 | EMPTY |

**Phase 1 target (50+ tests): ACHIEVED (61 tests)**

### Test Breakdown

| Test File | Tests | Coverage |
|-----------|-------|----------|
| test_token_mint_conditions.py | 17 | M1-M4 mint conditions |
| test_token_burn_conditions.py | 28 | B1-B5 burn conditions |
| test_token_supply_calculations.py | 16 | Supply formulas |

---

## Dependencies

| Dependency | Required For | Status |
|------------|--------------|--------|
| L4 Registry | Citizen/org lookup | COMPLETE |
| L4 Schema | Node types | COMPLETE |
| Solana CLI/SDK | Token creation | AVAILABLE |
| SOL funds | Actual deployment | NEEDED |
