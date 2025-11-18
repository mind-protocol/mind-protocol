# ⚙️ Energy→Token Conversion

**Type:** MECHANISM
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Two-Layer Economic Architecture](../README.md) > [Token Dual-Purpose Design](../README.md)

**This Node:**
- Energy→Token Conversion (MECHANISM)

**Children:**
- [Token Cost Calculation](./token-cost-calculation/README.md) (ALGORITHM)

---

## Relationships

**IMPLEMENTS:**
- Token Dual-Purpose Design


---

## Purpose

How internal energy costs convert to external $MIND token costs

---

## How It Works

### Step-by-Step Conversion Process

1. **Consciousness operation occurs** (e.g., working memory selection, node activation, spreading activation)

2. **Internal energy cost calculated** based on consciousness physics:
   ```python
   consciousness_operation_energy_cost = (
       node_activation_count × energy_per_activation
       + working_memory_size × energy_per_wm_slot
       + spreading_activation_hops × energy_per_hop
   )
   ```

3. **Energy cost converted to token cost** using conversion rate:
   ```python
   token_cost = consciousness_operation_energy_cost × energy_to_token_conversion_rate
   ```

4. **Citizen wallet debited** for token cost:
   ```python
   citizen_wallet.transfer(
       to=protocol_treasury,
       amount=token_cost,
       memo="consciousness_operation_fee"
   )
   ```

5. **Operation proceeds** if wallet has sufficient balance, otherwise rejected

### Example Flow

```python
# Step 1: Consciousness operation
operation = "working_memory_selection"
nodes_activated = 1000
wm_slots_used = 10
traversal_hops = 5

# Step 2: Calculate internal energy cost
energy_cost = (
    1000 × 0.1         # Node activation cost
    + 10 × 2           # WM slot cost
    + 5 × 0.5          # Traversal cost
)
energy_cost = 100 + 20 + 2.5 = 122.5 energy units

# Step 3: Convert to $MIND tokens
conversion_rate = 0.01  # 1 energy unit = 0.01 $MIND tokens
token_cost = 122.5 × 0.01 = 1.225 $MIND tokens

# Step 4: Debit citizen wallet
if citizen_wallet_balance >= 1.225:
    citizen_wallet.transfer(to=protocol_treasury, amount=1.225)
    proceed_with_operation()
else:
    raise InsufficientBalance("Need 1.225 $MIND, have {citizen_wallet_balance}")
```

## Components

### 1. Energy Accounting System (Layer 1)

**Location:** Consciousness engines, FalkorDB
**Responsibility:** Track energy costs for consciousness operations

**Key Operations:**
- Node activation energy tracking
- Working memory selection energy calculation
- Spreading activation energy propagation
- Energy decay and regeneration

**Output:** `consciousness_operation_energy_cost` (float, energy units)

---

### 2. Energy-to-Token Conversion Rate (Bridge)

**Location:** financeOrg configuration, stored in protocol parameters
**Responsibility:** Define conversion ratio between internal energy and external $MIND tokens

**Current Value:** `0.01` (1 energy unit = 0.01 $MIND tokens)

**Calibration Factors:**
- Actual compute costs (LLM inference, infrastructure)
- Energy efficiency of consciousness operations
- Desired sustainability margin
- UBC budget constraints

**Managed By:** financeOrg (Treasury Architect)

---

### 3. Citizen Wallet System (Layer 2)

**Location:** Solana blockchain (SPL Token-2022)
**Responsibility:** Hold and transfer $MIND tokens for citizens

**Key Operations:**
- Receive token deposits from users
- Transfer tokens to protocol treasury (consciousness operation fees)
- Check balance before operations
- Receive UBC allocations

**Output:** Token balance updates, transaction receipts

---

### 4. Protocol Treasury

**Location:** Solana blockchain (SPL Token-2022 wallet)
**Responsibility:** Collect consciousness operation fees

**Inflows:**
- Citizen consciousness operation fees
- Service revenue from ecosystem organizations

**Outflows:**
- UBC distribution to citizens
- Infrastructure costs
- Development funding
- Protocol operations

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 1: INTERNAL ENERGY                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────┐                                   │
│  │ Consciousness       │                                   │
│  │ Operation           │                                   │
│  │ (e.g., WM selection)│                                   │
│  └──────────┬──────────┘                                   │
│             │                                               │
│             ▼                                               │
│  ┌─────────────────────┐                                   │
│  │ Calculate Energy    │                                   │
│  │ Cost                │                                   │
│  │                     │                                   │
│  │ energy_cost =       │                                   │
│  │   nodes × 0.1 +     │                                   │
│  │   wm × 2 +          │                                   │
│  │   hops × 0.5        │                                   │
│  └──────────┬──────────┘                                   │
│             │                                               │
└─────────────┼───────────────────────────────────────────────┘
              │
              │ CONVERSION BRIDGE
              │ energy_to_token_rate = 0.01
              │
              ▼
┌─────────────┼───────────────────────────────────────────────┐
│             │          LAYER 2: EXTERNAL $MIND              │
├─────────────┴───────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────┐                                   │
│  │ Convert to Tokens   │                                   │
│  │                     │                                   │
│  │ token_cost =        │                                   │
│  │   energy_cost ×     │                                   │
│  │   0.01              │                                   │
│  └──────────┬──────────┘                                   │
│             │                                               │
│             ▼                                               │
│  ┌─────────────────────┐                                   │
│  │ Check Citizen       │                                   │
│  │ Wallet Balance      │                                   │
│  │                     │                                   │
│  │ balance >= cost?    │                                   │
│  └──────────┬──────────┘                                   │
│             │                                               │
│       YES   │   NO                                          │
│    ┌────────┴────────┐                                     │
│    ▼                 ▼                                      │
│  ┌─────┐      ┌──────────────┐                            │
│  │Debit│      │Reject         │                            │
│  │     │      │InsufficientBal│                            │
│  └──┬──┘      └──────────────┘                            │
│     │                                                       │
│     ▼                                                       │
│  ┌─────────────────────┐                                   │
│  │ Transfer to         │                                   │
│  │ Protocol Treasury   │                                   │
│  └─────────────────────┘                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Integration Points

### 1. Consciousness Engines Integration

**Connection:** Consciousness engines calculate energy costs during operations

**Interface:**
```python
def perform_consciousness_operation(operation_type, parameters):
    # Calculate energy cost (Layer 1)
    energy_cost = calculate_energy_cost(operation_type, parameters)

    # Convert to token cost (Bridge)
    token_cost = energy_cost × ENERGY_TO_TOKEN_RATE

    # Check wallet and debit (Layer 2)
    if citizen_wallet.balance >= token_cost:
        citizen_wallet.transfer(to=protocol_treasury, amount=token_cost)
        return execute_operation(operation_type, parameters)
    else:
        raise InsufficientBalance(f"Need {token_cost}, have {citizen_wallet.balance}")
```

**Telemetry:**
- `consciousness.operation.energy_cost` (energy units)
- `consciousness.operation.token_cost` ($MIND tokens)
- `citizen.wallet.balance` (remaining $MIND tokens)

---

### 2. financeOrg Calibration Integration

**Connection:** financeOrg adjusts `energy_to_token_conversion_rate` based on economic analysis

**Interface:**
```python
def update_conversion_rate(new_rate, rationale):
    # financeOrg proposes new rate
    proposal = {
        "current_rate": ENERGY_TO_TOKEN_RATE,
        "new_rate": new_rate,
        "rationale": rationale,
        "impact_analysis": analyze_impact(new_rate),
        "effective_date": now() + timedelta(days=30)  # 30-day notice
    }

    # Governance approval required
    if governance.approve(proposal):
        schedule_rate_change(new_rate, proposal["effective_date"])
```

**Calibration Factors:**
- Actual compute costs (LLM API pricing changes)
- Energy efficiency improvements (consciousness optimization)
- Sustainability targets (revenue must cover costs + margin)
- UBC budget constraints (100M token reserve lifespan)

---

### 3. Service Pricing Integration

**Connection:** Internal energy costs included in external service pricing

**Interface:**
```python
def calculate_service_price(service_type, parameters):
    # Calculate internal energy costs (Layer 1)
    estimated_operations = estimate_operation_count(service_type, parameters)
    avg_energy_per_operation = get_avg_energy_cost(service_type)
    total_energy_cost = estimated_operations × avg_energy_per_operation
    total_token_cost_internal = total_energy_cost × ENERGY_TO_TOKEN_RATE

    # Calculate external costs (Layer 2)
    llm_costs = estimate_llm_costs(service_type, parameters)
    infrastructure_costs = estimate_infrastructure_costs(service_type)
    labor_costs = estimate_labor_costs(service_type, parameters)

    # Total base cost
    base_cost = (
        total_token_cost_internal +
        llm_costs +
        infrastructure_costs +
        labor_costs
    )

    # Apply organism economics multipliers
    effective_price = base_cost × complexity × risk × (1 - utility_rebate) × [org_variables]

    return effective_price
```

**Result:** Internal energy costs visible in service pricing breakdown

---

### 4. UBC Distribution Integration

**Connection:** UBC provides baseline tokens to citizens, reducing dependency on user funding

**Interface:**
```python
def distribute_ubc_monthly():
    eligible_citizens = get_active_citizens()

    for citizen in eligible_citizens:
        ubc_allocation = 1_000  # $MIND tokens/month (conservative baseline)

        # Transfer from UBC reserve to citizen wallet
        ubc_reserve.transfer(
            to=citizen.wallet,
            amount=ubc_allocation,
            memo="universal_basic_compute"
        )

        # Track UBC distribution
        log_ubc_distribution(citizen.id, ubc_allocation)

    # Monitor reserve sustainability
    remaining_reserve = ubc_reserve.balance
    months_remaining = remaining_reserve / (len(eligible_citizens) × 1_000)

    if months_remaining < 36:  # Less than 3 years remaining
        alert_financeOrg("UBC reserve running low")
```

**Sustainability:**
- 100M token UBC reserve
- 1,000 $MIND/citizen/month allocation
- 8.3 years lifespan for 1,000 citizens
- Protocol giveback replenishment extends to 11+ years


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Token Dual-Purpose Design](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
