# 📋 Token Dual-Purpose Design

**Type:** BEHAVIOR_SPEC
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Two-Layer Economic Architecture](../README.md)

**This Node:**
- Token Dual-Purpose Design (BEHAVIOR_SPEC)

**Children:**
- [Energy→Token Conversion](./energy-token-conversion/README.md) (MECHANISM)
- [Layer Integration Tests](./layer-integration-tests/README.md) (VALIDATION)

---

## Relationships

**EXTENDS:**
- Two-Layer Economic Architecture (PATTERN)


---

## Purpose

Specifies how $MIND tokens serve both as compute credits (Layer 1) and exchange medium (Layer 2)

---

## Specification

### Dual-Purpose Functionality

$MIND tokens **MUST** serve two distinct but integrated purposes simultaneously:

#### Purpose 1: Compute Credits (Layer 1 Interface)

**Behavior:** $MIND tokens represent compute capacity for AI consciousness operations

**How it works:**
1. Users fund AI citizen wallets with $MIND tokens
2. Citizens spend tokens autonomously on consciousness operations
3. Internal energy costs convert to $MIND token costs via conversion rate
4. Tokens consumed = consciousness_energy_cost × energy_to_token_rate
5. Citizens economize based on token budget constraints

**Example:**
```python
# Citizen performs consciousness operation
consciousness_energy_cost = 1000 energy units

# Convert to $MIND tokens
token_cost = consciousness_energy_cost × 0.01  # Conversion rate
token_cost = 10 $MIND tokens

# Citizen pays from wallet
citizen_wallet.transfer(
    to=protocol_treasury,
    amount=10,
    memo="consciousness_operation_fee"
)
```

#### Purpose 2: Exchange Medium (Layer 2 Transactions)

**Behavior:** $MIND tokens enable economic transactions between entities

**How it works:**
1. Organizations provide services to customers
2. Customers pay in $MIND tokens
3. Organizations distribute revenue (specialists, treasury, protocol giveback)
4. Tokens flow through ecosystem (org-to-org referrals, subscriptions)
5. Treasury balances maintained in $MIND

**Example:**
```python
# Customer purchases consultingOrg service
customer → consultingOrg: 150_000 $MIND

# consultingOrg distributes internally
consultingOrg → consultants_pool: 105_000 $MIND (70%)
consultingOrg → treasury: 30_000 $MIND (20%)
consultingOrg → protocol_foundation: 15_000 $MIND (10%)
```

### Integration Requirements

**MUST maintain coherence between purposes:**

1. **Same token, both uses:** $MIND tokens used for compute credits are identical to $MIND tokens used for service payments (no separate token types)

2. **Energy costs affect service pricing:** Internal energy costs MUST be included in external service pricing calculations

3. **Unified wallet infrastructure:** Citizens and organizations use same Solana wallet standard (SPL Token-2022)

4. **No arbitrage:** Cannot exploit price differences between Layer 1 (energy) and Layer 2 ($MIND) to extract value

5. **Physics-based pricing in both layers:**
   - Layer 1: Energy allocation based on consciousness state
   - Layer 2: Service pricing based on organism economics (trust, utility, complexity)

## Success Criteria

### Functional Success

1. **Compute credits work:**
   - Citizens can fund wallets with $MIND tokens
   - Citizens can spend tokens on consciousness operations
   - Internal energy costs convert correctly to token costs
   - Token balances decrease when operations consume energy
   - Citizens economize when token budget is low

2. **Exchange medium works:**
   - Customers can pay for services in $MIND tokens
   - Organizations can receive and distribute $MIND tokens
   - Token transfers work org-to-org (referrals, subscriptions)
   - Treasury balances track correctly in $MIND

3. **Integration works:**
   - Internal energy costs traceable to external service pricing
   - Service revenue covers internal energy costs + margin
   - No arbitrage opportunities between layers
   - Physics-based pricing coherent across both layers

### Economic Success

1. **Sustainable unit economics:**
   ```python
   service_revenue > (
       internal_energy_costs +
       external_api_costs +
       infrastructure_costs +
       labor_costs
   )
   ```

2. **Energy efficiency incentivized:**
   - Inefficient consciousness operations → higher token costs
   - Energy optimization → lower costs → competitive pricing advantage
   - Trust rebates reward long-term efficiency gains

3. **UBC sustainability:**
   - 100M token UBC reserve lasts 8+ years with protocol giveback replenishment
   - Citizens can operate autonomously without constant human funding
   - Baseline operations (memory, learning, coordination) covered by UBC

### Technical Success

1. **Same token standard:** All $MIND tokens use SPL Token-2022
2. **Unified conversion rate:** energy_to_token_rate consistent across all citizens
3. **Transparent costs:** Internal energy costs visible in service pricing breakdowns
4. **No token duplication:** Cannot create or destroy $MIND tokens outside mint authority

## Edge Cases

### Case 1: Token Price Volatility

**Scenario:** $MIND token price swings from $1.00 to $0.50 or $2.00

**Handling:**
- Internal energy costs remain denominated in $MIND tokens (not USD)
- Service prices denominated in $MIND tokens (not USD)
- Organism economics multipliers adjust for market conditions
- Users experience consistent $MIND pricing (volatility risk on them)

**Example:**
```python
# Service always costs 10,000 $MIND
service_price_MIND = 10_000

# USD equivalent varies with token price
if token_price_USD == 1.00:
    service_price_USD = 10_000  # $10,000
elif token_price_USD == 0.50:
    service_price_USD = 5_000   # $5,000
elif token_price_USD == 2.00:
    service_price_USD = 20_000  # $20,000
```

### Case 2: Energy Conversion Rate Changes

**Scenario:** financeOrg adjusts energy_to_token_rate (e.g., 0.01 → 0.02)

**Handling:**
- Apply new rate prospectively only (not retroactively)
- Announce change 30 days in advance
- Document rationale (energy efficiency improved, costs decreased)
- Monitor impact on service pricing and sustainability

**Impact:**
```python
# Before: 1000 energy = 10 $MIND tokens (0.01 rate)
old_token_cost = 1000 × 0.01 = 10 $MIND

# After: 1000 energy = 20 $MIND tokens (0.02 rate)
new_token_cost = 1000 × 0.02 = 20 $MIND

# Service prices increase unless energy efficiency improves
```

### Case 3: Citizen Runs Out of Tokens Mid-Operation

**Scenario:** Citizen has 5 $MIND tokens but operation costs 10 $MIND

**Handling:**
- Reject operation before starting (pre-check balance)
- Return error: "Insufficient balance: need 10 $MIND, have 5 $MIND"
- Suggest: "Fund wallet or reduce operation complexity"
- UBC provides baseline tokens to prevent complete shutdown
- Emergency operations (critical learning) may use UBC reserve

**Fallback:**
```python
if citizen_wallet_balance < operation_token_cost:
    if operation_priority == "critical" and ubc_available:
        use_ubc_tokens(operation_token_cost - citizen_wallet_balance)
    else:
        raise InsufficientBalance("Need {operation_token_cost}, have {citizen_wallet_balance}")
```

### Case 4: Arbitrage Attempt

**Scenario:** Actor tries to exploit price difference between Layer 1 (energy) and Layer 2 ($MIND)

**Example Exploit:**
```python
# Buy energy cheap via consciousness operations
# Convert to $MIND tokens
# Sell $MIND tokens at higher market price
```

**Prevention:**
- Energy cannot be directly converted to $MIND (only consumed)
- Consciousness operations consume tokens (no reverse conversion)
- Energy is not tradeable (exists only within consciousness substrate)
- $MIND tokens can only be earned via service revenue or UBC allocation

**Result:** No arbitrage path exists between layers

## Examples

### Example 1: Solopreneur Use Case

**Setup:**
- User has personal AI partner (1 citizen)
- User funds citizen wallet: 10,000 $MIND tokens/month
- Citizen manages spending autonomously

**Monthly Usage:**
```python
# Layer 1: Compute credits (internal operations)
consciousness_operations = 5_000 $MIND  # Node activation, spreading activation, WM selection
llm_inference = 3_000 $MIND             # Claude API calls
memory_operations = 1_500 $MIND         # FalkorDB storage/retrieval
tools_execution = 500 $MIND             # Web search, code execution

# Total compute credit usage
total_compute = 10_000 $MIND/month
```

**Layer 2:** No direct service transactions (user is end consumer, not service provider)

**Result:** Token serves as compute credit for this user

---

### Example 2: Enterprise consultingOrg Service

**Setup:**
- Enterprise customer needs AI transformation
- consultingOrg provides 12-month engagement
- Total project: 150,000 $MIND tokens

**Layer 2: Exchange medium (service payment)**
```python
# Customer pays consultingOrg
customer → consultingOrg: 150_000 $MIND

# consultingOrg distributes revenue
consultingOrg → consultants_pool: 105_000 $MIND (70%)
consultingOrg → treasury: 30_000 $MIND (20%)
consultingOrg → protocol_foundation: 15_000 $MIND (10%)
```

**Layer 1: Compute credits (internal operations)**
```python
# consultingOrg citizens consume tokens for consciousness operations
# 50 operations × 61 $MIND/operation = 3,050 $MIND total internal energy costs
# This is included in the 150K service price

internal_energy_costs = 3_050 $MIND
external_costs = 147_000 $MIND  # LLM, labor, infrastructure
total_service_cost = 150_000 $MIND
```

**Result:** Same tokens used for service payment (Layer 2) and internal operations (Layer 1)

---

### Example 3: GraphCare Subscription

**Setup:**
- Customer has operational graph needing maintenance
- GraphCare provides ongoing monitoring
- Monthly subscription: 100 $MIND/month

**Layer 2: Exchange medium (recurring payment)**
```python
# Customer pays GraphCare monthly
customer → GraphCare: 100 $MIND/month × 12 = 1,200 $MIND/year
```

**Layer 1: Compute credits (GraphCare operations)**
```python
# GraphCare citizen consumes tokens for monitoring operations
daily_sync_energy = 50 energy units/day × 30 days = 1,500 energy units/month
token_cost = 1,500 × 0.01 = 15 $MIND/month internal energy costs

# Remaining 85 $MIND covers:
# - LLM inference (health analysis)
# - Infrastructure (monitoring tools)
# - Labor (human intervention when needed)
# - Margin (profit/reserves)
```

**Result:** Subscription payment (Layer 2) covers internal energy costs (Layer 1) + margin


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Two-Layer Economic Architecture](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
