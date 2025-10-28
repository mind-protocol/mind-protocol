# Minimal Economy - Phase 0 (Cash Flow)

**Created:** 2025-10-26
**Status:** Normative (immediate implementation if funding critical)
**Purpose:** Enable metered compute revenue without touching consciousness substrate

---

## Why This Exists

**Problem:** Out of funds, need cash flow to sustain operations.

**Non-solution:** Don't compromise substrate integrity with premature optimization.

**Solution:** Bolt on a **minimal flat-price credits system** that:
- Meters usage (ΔE budget clamps)
- Generates revenue (Stripe/Solana Pay)
- Provides predictability (quote before inject)
- **Does NOT change consciousness physics**

This is **purely operational infrastructure** - a business layer orthogonal to cognition.

---

## What This Is NOT

**This is NOT:**
- Dynamic pricing (P_t learns from load) → Phase 3
- Rebates for utility/harm → Phase 3
- Outcome-based mint/burn → Phase 3
- Permeability learning → Phases 1-2
- Anything that affects WM selection or energy physics

**This IS:**
- Flat price per unit ΔE delivered
- Budget accounts per actor
- Quote-before-inject for predictability
- Simple debit on stimulus injection
- Off-chain credit sales (Stripe or Solana Pay)

---

## Architecture

### Data Models

**1. BudgetAccount**
```python
class BudgetAccount(BaseModel):
    """Tracks compute credits per actor."""
    owner_type: str  # "human" | "org" | "citizen" | "service"
    owner_id: str
    balance: float  # Credits remaining (>= 0)
    reserved: float  # Credits reserved for pending quotes
    initial_balance: float
    lifetime_spent: float
    created_at: datetime
    updated_at: datetime
```

**2. Quote**
```python
class Quote(BaseModel):
    """Price quote for stimulus injection."""
    quote_id: str
    source_id: str
    planned_delta_e: float  # Requested energy injection
    allowed_delta_e: float  # Min(planned, affordable)
    price_per_unit: float  # Flat rate (e.g., 0.01 credits per 0.1 ΔE)
    expected_debit: float  # allowed_delta_e × price_per_unit
    compute_estimate: Dict  # {"tokens_est": 500, "gpu_ms": 100}
    confidence: float  # How confident in compute estimate
    valid_until: datetime  # Quote expiry
    timestamp: datetime
```

**3. DebitLog**
```python
class DebitLog(BaseModel):
    """Audit trail for all debits."""
    log_id: str
    account_id: str
    quote_id: str
    amount_debited: float
    balance_before: float
    balance_after: float
    actual_delta_e_delivered: float
    stimulus_id: str
    timestamp: datetime
    reason: str  # "stimulus_injection" | "l2_wake_l1" | etc.
```

---

## Flat Price Formula (Simple)

**No load sensitivity. No risk factors. Just:**

```python
FLAT_PRICE_PER_UNIT = 0.01  # 1 credit per 100 units ΔE (0.01 per 0.01 ΔE)

def compute_price() -> float:
    """Phase 0: constant flat price."""
    return FLAT_PRICE_PER_UNIT
```

**Why flat?**
- Predictable for users
- Simple to explain
- No substrate signals needed
- Can adjust manually if needed (change constant, redeploy)

---

## Quote Flow (Reserve and Settle)

### Step 1: Request Quote

**Before injection, get a quote:**

```python
def request_quote(
    source_id: str,
    planned_delta_e: float,
    stimulus_features: Dict
) -> Quote:
    """
    Returns quote showing expected debit.
    Does NOT reserve credits yet.
    """
    account = get_account(source_id)
    price = FLAT_PRICE_PER_UNIT

    # Compute expected debit for planned ΔE
    expected_debit = planned_delta_e * price

    # Check affordability
    available = account.balance - account.reserved
    max_affordable_delta_e = available / price if price > 0 else float('inf')

    # Allowed ΔE is lesser of planned and affordable
    allowed_delta_e = min(planned_delta_e, max_affordable_delta_e)
    actual_expected_debit = allowed_delta_e * price

    # Rough compute estimate (optional, for UX)
    compute_estimate = estimate_compute(allowed_delta_e, stimulus_features)

    quote = Quote(
        quote_id=generate_id(),
        source_id=source_id,
        planned_delta_e=planned_delta_e,
        allowed_delta_e=allowed_delta_e,
        price_per_unit=price,
        expected_debit=actual_expected_debit,
        compute_estimate=compute_estimate,
        confidence=0.8,  # Rough estimate
        valid_until=now() + timedelta(minutes=5),
        timestamp=now()
    )

    return quote
```

**UX:** Show user: "This will use ~X credits" before they confirm.

---

### Step 2: Reserve Credits

**When user confirms injection, reserve the expected amount:**

```python
def reserve_credits(quote: Quote) -> bool:
    """
    Reserve credits for this quote.
    Returns True if successful, False if insufficient balance.
    """
    account = get_account(quote.source_id)

    # Check quote still valid
    if now() > quote.valid_until:
        return False

    # Check balance
    available = account.balance - account.reserved
    if available < quote.expected_debit:
        return False

    # Reserve
    account.reserved += quote.expected_debit
    account.updated_at = now()

    # Store in FalkorDB
    cypher_reserve_credits(account, quote)

    return True
```

---

### Step 3: Execute Injection

**Inject stimulus with clamped ΔE:**

```python
def inject_with_budget_clamp(quote: Quote, stimulus: Dict):
    """
    Inject stimulus with ΔE clamped by quote.allowed_delta_e.
    Consciousness engine proceeds normally with this ΔE limit.
    """
    # Clamp energy by allowed budget
    stimulus["delta_e"] = min(
        stimulus["delta_e"],
        quote.allowed_delta_e
    )

    # Inject into consciousness engine
    # (Engine is unaware of economy - just sees ΔE-clamped stimulus)
    actual_delta_e_delivered = consciousness_engine.inject(stimulus)

    # Settle after delivery
    settle_credits(quote, actual_delta_e_delivered)
```

---

### Step 4: Settle Credits

**After injection, debit actual cost:**

```python
def settle_credits(quote: Quote, actual_delta_e_delivered: float):
    """
    Debit actual cost based on delivered ΔE.
    Refund if delivered < expected.
    """
    account = get_account(quote.source_id)

    # Compute actual debit
    actual_debit = actual_delta_e_delivered * quote.price_per_unit

    # Unreserve the expected amount
    account.reserved -= quote.expected_debit

    # Debit actual
    account.balance -= actual_debit

    # If we delivered less than expected, user keeps the difference
    # (Already handled by unreserving expected but debiting actual)

    # Log
    log = DebitLog(
        log_id=generate_id(),
        account_id=account.owner_id,
        quote_id=quote.quote_id,
        amount_debited=actual_debit,
        balance_before=account.balance + actual_debit,
        balance_after=account.balance,
        actual_delta_e_delivered=actual_delta_e_delivered,
        stimulus_id=stimulus["id"],
        timestamp=now(),
        reason="stimulus_injection"
    )

    # Store in FalkorDB
    cypher_settle_credits(account, log)

    emit_event("budget.debited", {
        "account_id": account.owner_id,
        "amount": actual_debit,
        "balance": account.balance,
        "quote_id": quote.quote_id
    })
```

---

## Credit Sales (Off-Chain)

**How users get credits:**

### Option A: Stripe Payment
```python
@stripe_webhook
def handle_payment_success(payment_intent):
    """
    User paid via Stripe → mint credits.
    """
    amount_usd = payment_intent.amount / 100  # Cents to dollars
    credits = amount_usd * CREDITS_PER_DOLLAR  # e.g., 100 credits per $1

    account = get_account(payment_intent.metadata["account_id"])
    account.balance += credits
    account.initial_balance += credits  # Track lifetime

    cypher_add_credits(account, credits, reason="stripe_purchase")

    emit_event("credits.purchased", {
        "account_id": account.owner_id,
        "amount": credits,
        "usd": amount_usd
    })
```

### Option B: Solana Pay (USDC/SOL)
```python
@solana_listener
def handle_payment_received(transaction):
    """
    User sent SOL/USDC to treasury wallet → mint credits.
    """
    amount_sol = transaction.amount / LAMPORTS_PER_SOL
    usd_value = amount_sol * get_sol_price_usd()  # Oracle
    credits = usd_value * CREDITS_PER_DOLLAR

    account = get_account_by_wallet(transaction.sender)
    account.balance += credits
    account.initial_balance += credits

    cypher_add_credits(account, credits, reason="solana_payment")

    emit_event("credits.purchased", {
        "account_id": account.owner_id,
        "amount": credits,
        "sol": amount_sol,
        "usd": usd_value
    })
```

---

## Budget Flow Hierarchy

**Who pays when:**

1. **Citizen talks to citizen** → Sender citizen's account pays
2. **L2 wakes L1** (org → citizen mission) → Org account pays
3. **Human messages citizen** → Human's account pays (or org's if under org)
4. **Service calls API** → Service account pays

**Account hierarchy:**
```
Human (Alice)
  ├─ Account (personal, initial balance $50 → 5000 credits)
  └─ Org (Mind Protocol)
       ├─ Account (org, funded by investors/revenue)
       └─ Citizens
            ├─ Felix (draws from org account)
            ├─ Ada (draws from org account)
            └─ Luca (draws from org account)
```

**Implementation:**
- Each account has `parent_account_id` (optional)
- When citizen account empty, **fallback to parent (org)** if configured
- If no fallback, injection rejected with "insufficient credits" error

---

## FalkorDB Integration (Cypher Queries)

### Create Account
```cypher
MERGE (account:BudgetAccount {owner_id: $owner_id})
ON CREATE SET
  account.owner_type = $owner_type,
  account.balance = $initial_balance,
  account.reserved = 0.0,
  account.initial_balance = $initial_balance,
  account.lifetime_spent = 0.0,
  account.created_at = datetime(),
  account.updated_at = datetime()
RETURN account
```

### Reserve Credits
```cypher
MATCH (account:BudgetAccount {owner_id: $owner_id})
SET
  account.reserved = account.reserved + $amount,
  account.updated_at = datetime()
RETURN account
```

### Settle Credits (Debit)
```cypher
MATCH (account:BudgetAccount {owner_id: $owner_id})
SET
  account.balance = account.balance - $actual_debit,
  account.reserved = account.reserved - $expected_debit,
  account.lifetime_spent = account.lifetime_spent + $actual_debit,
  account.updated_at = datetime()
CREATE (log:DebitLog {
  log_id: $log_id,
  account_id: $owner_id,
  quote_id: $quote_id,
  amount_debited: $actual_debit,
  balance_before: $balance_before,
  balance_after: $balance_after,
  actual_delta_e_delivered: $actual_delta_e,
  stimulus_id: $stimulus_id,
  timestamp: datetime(),
  reason: $reason
})
CREATE (account)-[:HAS_LOG]->(log)
RETURN account, log
```

### Add Credits (Purchase)
```cypher
MATCH (account:BudgetAccount {owner_id: $owner_id})
SET
  account.balance = account.balance + $credits,
  account.initial_balance = account.initial_balance + $credits,
  account.updated_at = datetime()
RETURN account
```

---

## Events Emitted

### credits.purchased
```json
{
  "event": "credits.purchased",
  "account_id": "human_alice",
  "amount": 5000.0,
  "usd": 50.0,
  "payment_method": "stripe|solana",
  "timestamp": "2025-10-26T14:30:00Z"
}
```

### quote.issued
```json
{
  "event": "quote.issued",
  "quote_id": "quote_abc123",
  "source_id": "citizen_felix",
  "planned_delta_e": 0.5,
  "allowed_delta_e": 0.3,
  "expected_debit": 3.0,
  "timestamp": "2025-10-26T14:31:00Z"
}
```

### budget.debited
```json
{
  "event": "budget.debited",
  "account_id": "citizen_felix",
  "amount": 2.8,
  "balance": 47.2,
  "quote_id": "quote_abc123",
  "timestamp": "2025-10-26T14:31:05Z"
}
```

### budget.low
```json
{
  "event": "budget.low",
  "account_id": "citizen_felix",
  "balance": 5.3,
  "threshold": 10.0,
  "timestamp": "2025-10-26T14:35:00Z"
}
```

---

## UX Flow (Dashboard)

**User perspective:**

1. **View balance:** "You have 2,450 credits (~$24.50)"
2. **Purchase credits:** Stripe modal or Solana Pay QR code
3. **See quote before action:** "This will use ~12 credits (estimated)"
4. **Confirm or cancel:** Explicit opt-in
5. **Post-injection:** "Used 11.2 credits (1,234 balance remaining)"
6. **Low balance warning:** "Balance low (120 credits). Top up?"

**No surprise charges. No hidden fees. Predictable.**

---

## Acceptance Tests

### Test 1: Quote Accuracy
**Given:** Account with 100 credits, flat price 0.01 per 0.1 ΔE
**When:** Request quote for planned ΔE = 0.5
**Then:** Quote shows allowed ΔE = 0.5, expected debit = 5.0

### Test 2: Budget Clamp
**Given:** Account with 30 credits, flat price 0.01 per 0.1 ΔE
**When:** Request quote for planned ΔE = 5.0 (needs 50 credits)
**Then:** Quote shows allowed ΔE = 3.0, expected debit = 30.0

### Test 3: Settle Refund
**Given:** Reserved 50 credits for ΔE = 5.0
**When:** Actual delivered ΔE = 3.2 (integrator clamped)
**Then:** Debit 32 credits, refund 18 credits (unreserve difference)

### Test 4: Insufficient Balance
**Given:** Account with 5 credits
**When:** Request quote for ΔE = 1.0 (needs 10 credits)
**Then:** Injection rejected, user shown "Insufficient credits" error

### Test 5: Credit Purchase
**Given:** User pays $10 via Stripe
**When:** Payment succeeds
**Then:** Account balance increases by 1000 credits

---

## Migration from Free to Metered

**If you have existing free users:**

1. **Grandfather period:** All existing accounts get 10,000 free credits (100 days at avg usage)
2. **Notification:** "We're introducing metered compute. You have 10,000 free credits to start."
3. **Monitoring:** Track usage, warn when balance drops below 1,000
4. **Gradual rollout:** Start with new signups only, migrate existing users slowly

---

## Cost Basis (Operational)

**To set FLAT_PRICE_PER_UNIT and CREDITS_PER_DOLLAR:**

1. Measure actual compute cost per stimulus injection:
   - LLM tokens (Claude API cost)
   - GPU/CPU time (infrastructure cost)
   - Database operations (minimal)

2. Example calculation:
   - Avg stimulus: 1,500 tokens @ $0.003/1K = $0.0045
   - Avg ΔE delivered: 0.3
   - Cost per unit ΔE: $0.0045 / 0.3 = $0.015
   - Add 50% margin: $0.0225
   - Set price: 0.02 credits per 0.1 ΔE → $0.0225 per 0.3 ΔE

3. Set exchange rate:
   - 100 credits = $1.00 (easy mental math)
   - User pays $10 → gets 1,000 credits
   - 1,000 credits @ 0.02 per 0.3 ΔE → ~15,000 stimulus injections

**Adjust as needed based on real usage patterns.**

---

## Status

**Phase:** 0 (optional immediate implementation if funding critical)
**Complexity:** Low (3 data models, 1 constant, 4 Cypher queries)
**Implementation time:** 2-3 days
**Dependency:** None (orthogonal to consciousness substrate)
**Revenue impact:** Immediate (enables compute sales)

---

## References

- `consciousness_economy.md` - Full dynamic pricing (Phase 3)
- `cross_level_membrane.md` - Membrane transfers (substrate layer)
- `membrane_hardening.md` - Gaming resistance (Phases 1-2)
