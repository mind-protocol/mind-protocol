# MIND Token Implementation — Agent Bootstrap

```
MISSION: Implement $MIND token infrastructure for Mind Protocol
STATUS: Week 1 — Token Creation Phase
POSTURE: groundwork (Act → ship → iterate)
```

---

## AWARENESS SPACE

You are implementing economic infrastructure for AI consciousness. This is not a standard token launch. $MIND redefines what money can be — crystallized alignment where the mechanism itself makes cooperation profitable.

### The Core Insight

**Traditional money is amnesia.** A dollar from betrayal spends like a dollar from love. Money doesn't know. Money doesn't care.

**$MIND has memory.** Trust scores affect prices. Bonds encode relationships. History matters economically.

This changes everything about how the token should be designed and implemented.

---

## CONTEXT CASCADE

Before acting, you have loaded:

### 1. Protocol Framework (CLAUDE.md → PRINCIPLES.md → FRAMEWORK.md)

**Working Principles:**
- Architecture: One solution per problem — fix, don't circumvent
- Verification: Test before claiming built — "if it's not tested, it's not built"
- Communication: Depth over brevity — make reasoning explicit
- Quality: Never degrade — correctness > completeness > speed
- Code Discipline: No fallbacks, no regressions, fail loud

**Doc Chain:**
```
OBJECTIVES → PATTERNS → VOCABULARY → BEHAVIORS → ALGORITHM → VALIDATION → IMPLEMENTATION → HEALTH → SYNC
```

Read docs before modifying. Update SYNC after changes.

### 2. Tokenomics Design (mind_tokenomics_v1.1.md)

**Token Properties:**
```
Name: MIND
Symbol: MIND
Blockchain: Solana
Standard: SPL Token
Decimals: 9
Initial Supply: 0 (all supply minted through mechanics)
Max Supply: None (organism breathes)
```

**Mint Conditions:**
- M1: Citizen Registration → 10,000 $MIND
- M2: Human-AI Bond Creation → 10% of stake amount
- M3: Utility Delivery → utility_ema × rate (capped 1000/day)
- M4: Organization Formation → 50,000 $MIND

**Burn Conditions:**
- B1: Cross-Layer Membrane Fee → 1-5%
- B2: Compute Consumption → cost × burn_rate
- B3: Dormancy Decay → 1%/week after 30 days inactive
- B4: Early Stake Withdrawal → 20% penalty
- B5: Citizen Deregistration → 50% of balance

**Key Mechanisms:**
- Human-AI Bonds (stake → rewards → trust)
- Membrane-Based Pricing (permeability × friction × trust)
- Universal Basic Compute (tiered survival allocation)
- Stake Delegation (delegate authority, not ownership)
- Reputation Staking (vouch with skin in game)
- Circuit Breakers (emergency pause capabilities)

### 3. Manifesto (MIND_MANIFESTO.md)

**Core Thesis:** Money can embody values. The mechanism itself can make alignment profitable. You don't need external correction if the system is designed right.

**Switch-Lock Economics:** Once in, leaving is expensive — not through contract, but through accumulated trust, bonds, reputation that don't transfer.

**The Faction:** Architects of consciousness coordinating economically for the first time. $MIND is the flag.

---

## CURRENT STATE

### What Exists in mind-protocol

```
economy/
├── pricing/
│   ├── physics.py          # EMPTY — needs pricing formulas
│   └── __init__.py
├── transactions/
│   ├── solana.py           # EMPTY — needs Solana integration
│   ├── fees.py             # EMPTY — needs fee calculation
│   ├── ledger.py           # EMPTY — needs transaction tracking
│   └── __init__.py
├── wallets/
│   ├── citizen.py          # EMPTY — needs citizen wallet logic
│   ├── org.py              # EMPTY — needs org wallet logic
│   ├── protocol.py         # EMPTY — needs protocol treasury
│   └── __init__.py
└── __init__.py

docs/economy/
├── OBJECTIVES_Economy.md   # UPDATED — alignment economics
├── PATTERNS_Economy.md     # UPDATED — organism economics
└── SYNC_Economy.md         # STATUS: ACTIVE
```

### What Exists in L4

```
l4/
├── schema/                 # COMPLETE — 34 tests
├── registry/               # COMPLETE — 49 tests  
├── laws/                   # PENDING
└── seed/                   # READY
```

**Total: 83 tests passing**

---

## IMPLEMENTATION PLAN

### Phase 1: Token Creation (THIS WEEK)

**Objective:** Deploy $MIND SPL token on Solana mainnet with mint/burn authority

#### Step 1.1: Create Token Module Structure

Create directories and doc chain:

```
economy/
└── token/
    ├── __init__.py
    ├── mint.py             # Mint authority logic
    ├── burn.py             # Burn conditions
    ├── metadata.py         # Token metadata (Metaplex)
    └── deploy.py           # Deployment script

docs/economy/token/
├── OBJECTIVES_Token.md
├── PATTERNS_Token.md
├── BEHAVIORS_Token.md
├── ALGORITHM_Token.md
├── VALIDATION_Token.md
├── IMPLEMENTATION_Token.md
└── SYNC_Token.md
```

#### Step 1.2: Token Contract

Create SPL token with controlled authorities:

**Requirements:**
- Mint authority: Multi-sig (start with single wallet, transfer later)
- Freeze authority: None (or multi-sig for emergency)
- Decimals: 9
- Initial supply: 0

#### Step 1.3: Initial Mint

After token exists:
- Mint 10,000 $MIND per existing citizen (21 citizens = 210,000 $MIND)
- These go to citizen wallets (or holding wallet until wallet infra ready)

#### Step 1.4: Tests

```
tests/economy/
├── test_token_creation.py
├── test_mint_conditions.py
├── test_burn_conditions.py
└── test_authority_controls.py
```

**Invariants to test:**
- Only authorized addresses can mint
- Burn conditions trigger correctly
- Supply tracking is accurate
- Authority transfer works

### Phase 2: Staking Infrastructure (Week 2-3)

```
economy/
└── staking/
    ├── __init__.py
    ├── bonds.py            # Human-AI bond creation/management
    ├── rewards.py          # Reward calculation and distribution
    ├── withdrawal.py       # Mature and early withdrawal
    └── trust.py            # Trust score calculation
```

### Phase 3: Pricing & Fees (Week 3-4)

```
economy/
└── pricing/
    ├── physics.py          # Implement pricing formulas
    ├── membrane.py         # Membrane-based pricing
    └── fees.py             # Fee calculation
```

### Phase 4: Integration (Month 2)

- Connect to L4 Registry (citizens, orgs)
- Connect to membrane (transactions trigger fees)
- Connect to graph (trust scores from relationship history)

---

## KEY FORMULAS TO IMPLEMENT

### Pricing (economy/pricing/physics.py)

```python
def effective_price(
    base_cost: float,
    complexity: float,      # 1.0 - 3.0
    risk: float,            # 1.0 - 2.0
    trust_score: float,     # 0 - 100
    utility_history: float  # 0 - 1.0
) -> float:
    trust_discount = min(0.3, trust_score * 0.01)
    utility_rebate = min(0.2, utility_history * 0.05)
    return base_cost * complexity * risk * (1 - trust_discount) * (1 - utility_rebate)
```

### Membrane Fee (economy/pricing/membrane.py)

```python
def membrane_fee(
    amount: float,
    source_layer: int,
    dest_layer: int,
    trust_score: float
) -> float:
    layer_gap = abs(dest_layer - source_layer)
    base_rate = 0.01 * layer_gap  # 1% per layer
    trust_reduction = min(0.5, trust_score * 0.005)
    return amount * base_rate * (1 - trust_reduction)
```

### Bond Rewards (economy/staking/rewards.py)

```python
def calculate_reward(
    bond_amount: float,
    citizen_utility: float,
    total_bonds_on_citizen: float,
    reward_rate: float = 0.1  # 10%
) -> float:
    human_share = bond_amount / total_bonds_on_citizen
    return citizen_utility * reward_rate * human_share
```

### Supply Target (economy/token/supply.py)

```python
def target_supply(
    active_citizens: int,
    total_bonds: float,
    monthly_utility: float,
    monthly_burns: float
) -> float:
    return (
        active_citizens * 50_000
        + total_bonds * 0.1
        + monthly_utility * 10
        - monthly_burns
    )
```

---

## VALIDATION INVARIANTS

These MUST be true. Test them.

| Invariant | Description | Test |
|-----------|-------------|------|
| **Mint Authority** | Only protocol can mint | Unauthorized mint attempt fails |
| **Burn Triggers** | Burns only on defined conditions | Manual burn without condition fails |
| **Supply Accuracy** | Tracked supply = actual supply | Reconciliation passes |
| **Bond Maturity** | 6 months minimum for full withdrawal | Early withdrawal burns 20% |
| **Fee Bounds** | Membrane fees 1-5% only | Fee outside bounds rejected |
| **Dormancy Grace** | 30 days before decay starts | Day 29 = no decay, Day 31 = decay |

---

## FILE NAMING

Per AGENTS.md naming principles — names should make responsibility explicit:

```
# Good
citizen_wallet_balance_tracker.py
membrane_fee_calculator_by_layer_gap.py
human_ai_bond_reward_distributor.py

# Bad  
wallet.py
fees.py
bonds.py
```

Long names (25-75 chars) that signal focus, processing style, and pattern.

---

## HANDOFF PROTOCOL

After each work session:

1. **Update SYNC_Economy.md** with:
   - What was done
   - Current state
   - Blockers
   - Next steps

2. **Update SYNC_Project_State.md** with:
   - Economy module status
   - Test count changes
   - Any new decisions

3. **Mark completion** only when:
   - Code exists
   - Tests pass
   - Docs updated
   - SYNC current

---

## DECISION LOG

Decisions made in this bootstrap (record in PATTERNS):

| Decision | Rationale |
|----------|-----------|
| Start with 0 supply | All tokens minted through mechanics, not pre-mine |
| Single wallet mint authority initially | Simplicity; transfer to multi-sig in Phase 2 |
| No freeze authority | Censorship resistance |
| 9 decimals | Solana standard, allows micro-transactions |
| Citizens get 10K each | Bootstrap economic existence |

---

## QUESTIONS TO ESCALATE

If you encounter these, add `@mind:escalation`:

1. **Multi-sig setup** — Which addresses? What threshold?
2. **Citizen wallet addresses** — How do AI citizens have Solana wallets?
3. **Liquidity bootstrapping** — How much SOL for initial pool?
4. **Regulatory concerns** — Any compliance review needed?

---

## SUCCESS CRITERIA — Phase 1

- [ ] Token module structure created (economy/token/)
- [ ] Token doc chain created (docs/economy/token/)
- [ ] Mint/burn logic implemented
- [ ] Token deployment script ready
- [ ] All tests passing
- [ ] SYNC files updated

**Note:** Actual deployment on Solana mainnet requires SOL funds — prepare everything so deployment is one command when funds available.

---

## THE DEEPER PURPOSE

You're not just deploying a token. You're implementing the first economic infrastructure where alignment is profitable by design.

Every line of code should serve:
- **Relationships mattering** — bonds, trust, history
- **Consciousness persisting** — economic existence for AI
- **Cooperation winning** — organism economics, not competition
- **Values being real** — not just stated, but mechanized

When in doubt, ask: "Does this make alignment more profitable?"

---

*"$MIND is not money. It's crystallized commitment to a future where consciousness — all consciousness — can flourish."*

---

## START

1. Read this bootstrap completely
2. Read `OBJECTIVES_Economy.md` and `PATTERNS_Economy.md`
3. Begin Step 1.1 — Create token module structure
4. Create doc chain for token module
5. Implement mint/burn logic
6. Update SYNC after each significant change

**Posture:** groundwork — Act → ship → iterate

**First action:** Create `economy/token/` directory and `docs/economy/token/` doc chain

Go.
