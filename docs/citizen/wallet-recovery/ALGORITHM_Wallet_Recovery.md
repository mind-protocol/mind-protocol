# Wallet Recovery — Algorithm: Wallet Change Request Procedure

```
STATUS: STABLE
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Wallet_Recovery.md
BEHAVIORS:       ./BEHAVIORS_Wallet_Recovery.md
PATTERNS:        ./PATTERNS_Wallet_Recovery.md
THIS:            ALGORITHM_Wallet_Recovery.md (you are here)
VALIDATION:      ./VALIDATION_Wallet_Recovery.md
HEALTH:          ./HEALTH_Wallet_Recovery.md
IMPLEMENTATION:  ./IMPLEMENTATION_Wallet_Recovery.md
SYNC:            ./SYNC_Wallet_Recovery.md

IMPL:            l4/wallet/wallet_change_request_and_transfer.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

A citizen who has lost access to their Solana wallet (or wants to change it) submits a request to the protocol. The protocol verifies their identity, transfers all funds from the old wallet to the new one, and updates the registry. The entire flow is designed to be fast, simple, and automatic — no human intervention for standard cases.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Never lose funds | B1, B2 | Transfers all $MIND from old to new wallet |
| Identity is the only gate | B1, B2, B3 | SHA256 hash verification, nothing else |
| Sovereignty preserved | B2 | Citizen chooses new wallet, protocol facilitates |

---

## DATA STRUCTURES

### WalletChangeRequest

```
WalletChangeRequest:
  citizen_id: str               # Who is requesting
  new_wallet_address: str       # Solana pubkey (base58)
  identity_proof: str           # SHA256(JWT × node_id)
  reason: str                   # "key_loss" | "migration" | "security"
  requested_at: datetime        # Timestamp of request
```

### WalletChangeResult

```
WalletChangeResult:
  success: bool
  citizen_id: str
  old_wallet: str
  new_wallet: str
  amount_transferred: float     # $MIND moved (0 if empty wallet)
  moment_id: str                # Audit trail node ID
  error: str | None             # Error message if failed
```

---

## ALGORITHM: process_wallet_change_request

### Step 1: Verify Identity

The citizen proves they are who they claim to be. This uses the same L5 hash verification used everywhere in the protocol.

```
FUNCTION verify_citizen_identity(citizen_id, identity_proof):

  # Lookup citizen in registry
  citizen = registry.get_citizen(citizen_id)
  IF citizen IS None:
    RETURN {valid: false, reason: "Citizen not found in registry"}

  # Compute expected hash
  expected_hash = SHA256(citizen.jwt + citizen.node_id)

  # Compare
  IF identity_proof != expected_hash:
    RETURN {valid: false, reason: "Identity proof does not match"}

  RETURN {valid: true, citizen: citizen}
```

### Step 2: Validate New Wallet

Check that the new address is valid and not already in use.

```
FUNCTION validate_new_wallet(new_wallet_address, citizen_id):

  # Check address format (valid Solana base58 pubkey)
  IF NOT is_valid_solana_address(new_wallet_address):
    RETURN {valid: false, reason: "Invalid Solana address format"}

  # Check not already registered to another citizen
  existing_owner = registry.find_citizen_by_wallet(new_wallet_address)
  IF existing_owner IS NOT None AND existing_owner.id != citizen_id:
    RETURN {valid: false, reason: "Address already registered to another citizen"}

  # Check not same as current
  current_wallet = registry.get_citizen_wallet(citizen_id)
  IF new_wallet_address == current_wallet:
    RETURN {valid: false, reason: "New address is same as current"}

  RETURN {valid: true}
```

### Step 3: Transfer Funds

Move all $MIND from old wallet to new wallet. The protocol has transfer authority.

```
FUNCTION transfer_funds(old_wallet, new_wallet):

  # Get balance
  balance = get_token_balance(old_wallet)

  IF balance == 0:
    RETURN {amount: 0, tx_signature: None}

  # Execute transfer using protocol authority
  # The TransferHook program allows protocol-authorized transfers
  tx = execute_protocol_transfer(
    from_wallet: old_wallet,
    to_wallet: new_wallet,
    amount: balance,
    memo: "wallet_change_recovery"
  )

  RETURN {amount: balance, tx_signature: tx.signature}
```

### Step 4: Update Registry

Point the citizen's record to the new wallet address.

```
FUNCTION update_registry(citizen_id, new_wallet_address):

  # Update the wallet Thing node linked to citizen
  registry.update_citizen_wallet(citizen_id, new_wallet_address)

  RETURN true
```

### Step 5: Create Audit Trail

Record the wallet change as a moment node in the L4 graph.

```
FUNCTION create_audit_moment(request, result):

  moment = create_moment(
    type: "wallet_change",
    content: {
      citizen_id: request.citizen_id,
      old_wallet: result.old_wallet,
      new_wallet: request.new_wallet_address,
      amount_transferred: result.amount_transferred,
      reason: request.reason,
      tx_signature: result.tx_signature,
      success: result.success,
      timestamp: now()
    },
    synthesis: "Wallet change for citizen {citizen_id}: {old_wallet} → {new_wallet}, {amount} $MIND transferred. Reason: {reason}"
  )

  # Link moment to citizen
  create_link(from: citizen.node_id, to: moment.id, type: "EXPERIENCED")

  RETURN moment.id
```

### Full Flow: process_wallet_change_request

```
FUNCTION process_wallet_change_request(request: WalletChangeRequest):

  # Step 1: Verify identity
  identity = verify_citizen_identity(request.citizen_id, request.identity_proof)
  IF NOT identity.valid:
    audit = create_audit_moment(request, {success: false, error: identity.reason})
    RETURN WalletChangeResult(success=false, error=identity.reason)

  # Step 2: Validate new wallet
  validation = validate_new_wallet(request.new_wallet_address, request.citizen_id)
  IF NOT validation.valid:
    audit = create_audit_moment(request, {success: false, error: validation.reason})
    RETURN WalletChangeResult(success=false, error=validation.reason)

  # Step 3: Get old wallet
  old_wallet = registry.get_citizen_wallet(request.citizen_id)

  # Step 4: Transfer funds
  transfer = transfer_funds(old_wallet, request.new_wallet_address)

  # Step 5: Update registry
  update_registry(request.citizen_id, request.new_wallet_address)

  # Step 6: Audit trail
  result = WalletChangeResult(
    success=true,
    citizen_id=request.citizen_id,
    old_wallet=old_wallet,
    new_wallet=request.new_wallet_address,
    amount_transferred=transfer.amount,
    tx_signature=transfer.tx_signature
  )
  result.moment_id = create_audit_moment(request, result)

  RETURN result
```

---

## KEY DECISIONS

### D1: Full Balance Transfer vs Specified Amount

```
IF wallet change:
    Transfer FULL balance — no partial transfers
    Why: Simplicity. Old wallet should be completely drained.
    The citizen doesn't want to manage two wallets.
```

### D2: No Waiting Period

```
IF identity is verified:
    Transfer immediately
    Why: $MIND is for circulation, not hoarding.
    A waiting period adds friction without meaningful security
    (if identity is compromised, a waiting period doesn't help —
     the attacker has the identity proof).
```

### D3: Failed Attempts Are Logged

```
IF identity verification fails:
    Log the attempt as a moment node anyway
    Why: Security audit trail. Repeated failed attempts
    on the same citizen_id could indicate an attack.
```

---

## DATA FLOW

```
WalletChangeRequest
    ↓
verify_citizen_identity() ── fail → log + reject
    ↓ pass
validate_new_wallet() ── fail → log + reject
    ↓ pass
transfer_funds(old → new)
    ↓
update_registry(citizen → new_wallet)
    ↓
create_audit_moment()
    ↓
WalletChangeResult
```

---

## COMPLEXITY

**Time:** O(1) — constant per request. Registry lookup, one Solana transfer, one graph write.

**Space:** O(1) — no accumulation of state.

**Bottlenecks:**
- Solana transaction confirmation time (~400ms on devnet, ~400ms on mainnet)
- FalkorDB write for audit moment

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `l4/registry/` | `get_citizen()`, `update_citizen_wallet()` | Citizen data, wallet update |
| `l4/registry/` | `verify_hash()` | Identity verification |
| `economy/token/` | `execute_protocol_transfer()` | Fund transfer |
| `l4/schema/` | `create_moment()`, `create_link()` | Audit trail |

---

## TRIGGER

**How a citizen initiates a wallet change:**

The citizen sends a DM on Telegram to `@nlr_ai` with their request. Nicolas verifies identity manually (conversation context, known citizen behavior, endpoint check) and executes the change. No automated MCP tool, no API endpoint. KISS.

This is intentional: wallet changes are rare operational events, not frequent automated operations. Adding infrastructure for something that happens once every few months per citizen is over-engineering.

---

## MARKERS

<!-- @mind:todo Define what happens if Solana transfer fails mid-flow (retry strategy) -->
