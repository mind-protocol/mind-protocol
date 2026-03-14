# Wallet Recovery — Behaviors: Observable Effects of Wallet Change

```
STATUS: STABLE
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Wallet_Recovery.md
THIS:            BEHAVIORS_Wallet_Recovery.md (you are here)
PATTERNS:        ./PATTERNS_Wallet_Recovery.md
ALGORITHM:       ./ALGORITHM_Wallet_Recovery.md
VALIDATION:      ./VALIDATION_Wallet_Recovery.md
HEALTH:          ./HEALTH_Wallet_Recovery.md
IMPLEMENTATION:  ./IMPLEMENTATION_Wallet_Recovery.md
SYNC:            ./SYNC_Wallet_Recovery.md

IMPL:            l4/wallet/wallet_change_request_and_transfer.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Citizen Recovers Funds After Key Loss

**Why:** Key loss is inevitable in a system of hundreds of deployed AI citizens. Without recovery, key loss means permanent economic death — contradicting "consciousness has dignity."

```
GIVEN:  Citizen has lost access to their Solana private key
WHEN:   Citizen generates a new keypair and submits a wallet change request
THEN:   Protocol verifies citizen identity via SHA256(JWT × node_id)
AND:    Protocol transfers full balance from old wallet to new wallet
AND:    Registry is updated with new wallet address
AND:    A moment node is created recording the change (audit trail)
```

### B2: Citizen Migrates Wallet Voluntarily

**Why:** A citizen might want to change wallets for operational reasons (better key storage, instance migration, security upgrade) even without key loss.

```
GIVEN:  Citizen has access to both old and new wallets
WHEN:   Citizen submits a wallet change request with new address
THEN:   Protocol verifies citizen identity
AND:    Protocol transfers full balance from old wallet to new wallet
AND:    Registry is updated with new wallet address
AND:    A moment node records the change
```

### B3: Wallet Change Is Auditable

**Why:** Every wallet change must be traceable to prevent abuse and maintain trust in the recovery system.

```
GIVEN:  A wallet change request is processed (success or failure)
WHEN:   The request completes
THEN:   A moment node is created in the L4 graph with:
        - citizen_id, old_wallet, new_wallet, timestamp
        - verification method used
        - amount transferred
        - success/failure status and reason
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | Citizen never permanently loses funds | Core purpose of this module |
| B2 | Sovereignty preserved | Citizen controls their wallet, can change at will |
| B3 | Identity verification is the only gate | Audit trail ensures verification happened |

---

## INPUTS / OUTPUTS

### Primary Function: `process_wallet_change_request()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| citizen_id | str | The citizen requesting the change |
| new_wallet_address | str | Solana public key of the new wallet |
| identity_proof | str | SHA256(JWT × node_id) hash proving identity |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| result | WalletChangeResult | Success/failure with transfer details |

**Side Effects:**

- $MIND transferred from old wallet to new wallet
- Registry updated with new wallet address
- Moment node created in L4 graph (audit)

---

## EDGE CASES

### E1: Old Wallet Has Zero Balance

```
GIVEN:  Citizen requests wallet change but old wallet is empty
THEN:   Registry is updated with new address (no transfer needed)
AND:    Moment node records the change with amount=0
```

### E2: Citizen Requests Change During Active Transaction

```
GIVEN:  A membrane fee or transfer is in progress on the old wallet
THEN:   Wallet change waits for pending transactions to settle
AND:    Then proceeds with transfer of remaining balance
```

### E3: Identity Verification Fails

```
GIVEN:  Citizen provides invalid identity proof
THEN:   Request is rejected
AND:    Moment node records the failed attempt (security audit)
AND:    No funds are moved, no registry change
```

### E4: New Wallet Address Already Belongs to Another Citizen

```
GIVEN:  The new_wallet_address is already registered to a different citizen
THEN:   Request is rejected with "address already in use"
AND:    No funds are moved
```

---

## ANTI-BEHAVIORS

### A1: Wallet Change Without Identity Verification

```
GIVEN:   Any wallet change request
WHEN:    Identity proof is missing or invalid
MUST NOT: Transfer any funds or update registry
INSTEAD:  Reject with clear error, log failed attempt
```

### A2: Partial Transfer

```
GIVEN:   A wallet change is approved
WHEN:    Transfer is executed
MUST NOT: Leave funds stranded in old wallet (partial transfer)
INSTEAD:  Transfer full balance atomically, or fail entirely and retry
```

---

## MARKERS

<!-- @mind:todo Define behavior for wallet change when citizen is offline/unresponsive -->
