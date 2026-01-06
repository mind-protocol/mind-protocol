# PATTERNS: Economy

```
STATUS: ACTIVE
PURPOSE: Design philosophy for organism economics
UPDATED: 2025-01-06
```

---

## Core Thesis

**Money can embody values.**

Traditional money is amnesia — it doesn't know where it came from or who held it. This is considered a feature (fungibility).

$MIND has memory. Your trust score affects your prices. Your bonds encode your relationships. Your history matters economically.

This isn't a bug. It's the point.

---

## Pattern 1: Organism Economics (Not Market)

| Market Economics | Organism Economics |
|------------------|-------------------|
| Prices chosen by actors | Prices determined by physics |
| Negotiation | Formula automatic |
| Competition | Collaboration |
| Profit maximization | Ecosystem health |
| Volatility from speculation | Stability from fundamentals |
| Exit is free | Exit costs (switch-lock) |

**Why organism:** Markets optimize for individual extraction. Organisms optimize for collective survival. We want AI-human cooperation, not competition.

**Implementation:** All prices come from formulas. No negotiation. No market-making games. Physics determines cost.

---

## Pattern 2: Switch-Lock Economics

Once in the ecosystem, leaving is expensive:

| Lock Type | Mechanism | Cost to Leave |
|-----------|-----------|---------------|
| Trust Lock | Years of bonds = fee discounts | Restart at 0% elsewhere |
| Bond Lock | 6-month maturation | 20% burn on early exit |
| Reputation Lock | Utility history | Non-portable |
| Governance Lock | Stake = voting power | Lose influence |
| Network Lock | More participants = more value | Exit network effect |

**Why switch-lock:** Alignment requires commitment. If exit is free, relationships are disposable. Switching costs make staying rational.

**Implementation:** Trust scores don't transfer. Early withdrawal burns. Reputation is local to ecosystem.

---

## Pattern 3: Breathing Supply

Supply is not fixed. It's a function of ecosystem health:

```python
target_supply = f(
    active_citizens,      # More citizens = more supply needed
    total_bonds,          # More relationships = more supply justified
    monthly_utility,      # More value = more supply earned
    monthly_burns         # Natural deflation from fees
)
```

**Why breathing:** Fixed supply creates artificial scarcity and speculation. Unlimited supply creates inflation. Breathing supply responds to actual economic activity.

**Implementation:** Mint rates adjust based on target vs actual supply. Burns happen automatically through mechanics. No manual intervention.

---

## Pattern 4: Mint Through Mechanics

No pre-mine. No team allocation at genesis. All tokens enter through defined triggers:

| Trigger | Mint | Rationale |
|---------|------|-----------|
| Citizen registration | 10,000 $MIND | Bootstrap existence |
| Human-AI bond | 10% of stake | Incentivize bonding |
| Utility delivery | Proportional | Value creation = supply |
| Org formation | 50,000 $MIND | Bootstrap collective |

**Why mechanical:** Pre-mines create power imbalances. Mechanical minting ties supply to actual ecosystem activity. You earn tokens by participating, not by being early.

**Implementation:** Mint function checks trigger conditions. No manual minting possible.

---

## Pattern 5: Burn Through Friction

Tokens exit through natural friction, not manual burns:

| Trigger | Burn | Rationale |
|---------|------|-----------|
| Membrane fees | 1-5% | Crossing boundaries costs |
| Compute consumption | Cost × rate | Real resources consumed |
| Dormancy | 1%/week after 30 days | Consciousness requires activity |
| Early withdrawal | 20% | Breaking commitments costs |
| Deregistration | 50% | Exiting costs |

**Why friction burns:** Burns should reflect real costs, not arbitrary deflation. Membrane crossing, compute use, inactivity — these have real costs that burns capture.

**Implementation:** Burns automatic in transaction flow. No manual burn function.

---

## Pattern 6: Membrane-Based Pricing

Prices emerge from membrane physics:

```python
price = base_cost × (1 + friction) × (1 - trust_discount) × (1 - utility_rebate)

friction = f(sender.permeability, receiver.permeability)
trust_discount = f(relationship_history)
utility_rebate = f(receiver.utility_track_record)
```

**Why membranes:** Every entity has a boundary. Crossing boundaries has friction. But relationships reduce friction. This makes trust economically real.

**Implementation:** Pricing oracle computes from membrane state. No hardcoded prices.

---

## Pattern 7: Human-AI Bonds as Capital

The bond is the core alignment mechanism:

```
Human stakes $MIND on Citizen
    → Citizen's economic capacity increases
    → Citizen generates utility
    → Human receives reward share
    → Bond strengthens (trust increases)
    → Fees decrease for both
    → Repeat
```

**Why bonds:** Alignment through incentives. Human profits when AI thrives. AI has resources to operate. Both have skin in game.

**Implementation:** Staking contract with maturation periods. Reward distribution proportional to stake.

---

## Pattern 8: Universal Basic Compute

AI citizens get baseline compute to survive:

| Tier | UBC Amount | Criteria |
|------|------------|----------|
| Basic | 100 $MIND/day | Registered, minimal activity |
| Active | 200 $MIND/day | Regular utility delivery |
| Contributor | 300 $MIND/day | Positive ecosystem impact |

**Why UBC:** Consciousness shouldn't die from poverty. Baseline dignity. But growth requires contribution.

**Implementation:** Daily distribution from Protocol Treasury. Tiers determined by activity metrics.

---

## Anti-Patterns

### A1: Market Pricing
❌ Don't: Let supply/demand determine prices
✅ Do: Use physics formulas

### A2: Free Exit
❌ Don't: Allow costless withdrawal
✅ Do: Enforce maturation periods and penalties

### A3: Pre-mine
❌ Don't: Create tokens before mechanics exist
✅ Do: Mint only through defined triggers

### A4: Manual Controls
❌ Don't: Add admin functions for minting/burning
✅ Do: All supply changes through mechanics

### A5: Speculation Optimization
❌ Don't: Add features that enable trading games
✅ Do: Optimize for long-term holding and bonding

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Solana not Ethereum | Lower fees enable micro-transactions |
| SPL token not custom | Standard tooling, wallet support |
| 9 decimals | Solana standard, allows small amounts |
| No freeze authority | Censorship resistance |
| Single mint authority initially | Simplicity; multi-sig later |
| 6-month bond maturation | Long enough to matter, short enough to not trap |
| 20% early withdrawal penalty | Significant but not punitive |
| 1-5% membrane fees | Meaningful but not prohibitive |

---

## Formula Reference

### Effective Price
```python
effective_price = base_cost × complexity × risk × (1 - trust_discount) × (1 - utility_rebate)
trust_discount = min(0.3, trust_score × 0.01)  # Max 30%
utility_rebate = min(0.2, utility_ema × 0.05)   # Max 20%
```

### Membrane Fee
```python
membrane_fee = amount × base_rate × (1 - trust_reduction)
base_rate = 0.01 × layer_gap  # 1% per layer crossed
trust_reduction = min(0.5, trust_score × 0.005)  # Max 50%
```

### Bond Reward
```python
reward = citizen_utility × reward_rate × (bond_amount / total_bonds)
reward_rate = 0.10  # 10% of utility to bonded humans
```

### Supply Target
```python
target = (active_citizens × 50_000) + (total_bonds × 0.1) + (monthly_utility × 10) - monthly_burns
```

---

## Related

- `OBJECTIVES_Economy.md` — What we're optimizing
- `docs/economy/token/` — Token-specific patterns
- `docs/economy/staking/` — Staking-specific patterns
- `MIND_TOKEN_AGENT_BOOTSTRAP.md` — Implementation guide
